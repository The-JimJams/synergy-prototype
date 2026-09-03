/**
 * SYNERGY AMR Fleet Control Platform — Warehouse Map Canvas Renderer
 * Accurate architectural floor plan matching Gazebo simulation (warehouse.sdf):
 * - 20x20m facility coordinate space (-10m to +10m)
 * - True vertical shelving racks (S1 to S8)
 * - Dedicated Charging Bay (CHG) with charging dock & lightning indicator
 * - Pickup (P) & Dropoff (D) bays with industrial hazard markings
 * - Shared Intersections (I1, I2) with red cross markers & bollards
 * - Obstacles: Central orange container, green dumpster, pallet stacks
 * - 60 FPS smooth lerp & shortest-arc orientation interpolation
 * - Top-down industrial AMR geometric model with real-time telemetry
 */

// Gap in CSS pixels between the wrapper edge and the square drawing surface.
const MAP_EDGE_INSET = 6;

// Largest distance a robot can plausibly cover between two telemetry samples.
// Top speed is 0.6 m/s (max_vel_x) and poses arrive at roughly 10 Hz, so ~0.06 m
// is normal; anything past this is a gap in the stream, not movement.
const TELEMETRY_JUMP_METRES = 0.75;

class WarehouseMapRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');

        // ── Gazebo World Dimensions (20m x 20m centered at 0,0) ──────────────
        this.world = {
            minX: -10.0,
            maxX: 10.0,
            minY: -10.0,
            maxY: 10.0,
            width: 20.0,
            height: 20.0,
        };

        // ═══════════════════════════════════════════════════════════════════
        // WAREHOUSE LAYOUT — GROUND TRUTH
        //
        // Every coordinate and footprint below is read from
        // gazebo/simulation/worlds/warehouse.sdf and agrees cell-for-cell with
        // the Nav2 occupancy grid (src/synergy_nav2/maps/warehouse_map.pgm).
        //
        // This panel is a view of the live world, so drawing furniture the world
        // does not contain makes correct robots look broken: with the previous
        // (invented) layout an AMR driving down the real central corridor was
        // painted straight through racks that only existed on this canvas.
        //
        // Mirrors STATIONS / INTERSECTIONS / RACKS / OBSTACLES in
        // dashboard/config.py and WAYPOINTS in task_allocator_node.py.
        // ═══════════════════════════════════════════════════════════════════

        // Station pads. P1/P2 are pickup, D1 dropoff, CHG the charging bay.
        this.stations = {
            'P1': { x: 0.0, y: 8.0, w: 2.4, h: 1.8, label: 'Pickup Station 1 (P1)', type: 'pickup', code: 'P1', color: '#16A34A' },
            'P2': { x: -5.5, y: -7.0, w: 2.4, h: 1.8, label: 'Pickup Station 2 (P2)', type: 'pickup', code: 'P2', color: '#16A34A' },
            'D1': { x: 0.0, y: -8.1, w: 2.8, h: 2.0, label: 'Dropoff Station (D1)', type: 'dropoff', code: 'D1', color: '#0284C7' },
            'CHG': { x: 5.5, y: -7.5, w: 2.4, h: 2.2, label: 'Charging Bay (CHG)', type: 'charging', code: '⚡', color: '#EAB308' }
        };

        // Shared intersections. Each is a 2.7 x 2.7 m marked square in the
        // central corridor, flanked by a bollard at x = +/- 0.75.
        this.intersections = {
            'I1': { x: 0.0, y: 5.2, label: 'Intersection 1', bollards: [-0.75, 0.75] },
            'I2': { x: 0.0, y: -0.7, label: 'Intersection 2', bollards: [-0.75, 0.75] }
        };

        // 8 high-bay racks in two columns at x = -4.8 / +4.8.
        // Each is 5.0 m across (X) by 1.0 m deep (Y) — they run ALONG the
        // aisles, they are not vertical blocks.
        this.racks = [
            { id: 'S1', x: -4.8, y: 7.5, w: 5.0, h: 1.0, label: 'S1' },
            { id: 'S2', x: 4.8, y: 7.5, w: 5.0, h: 1.0, label: 'S2' },
            { id: 'S3', x: -4.8, y: 3.0, w: 5.0, h: 1.0, label: 'S3' },
            { id: 'S4', x: 4.8, y: 3.0, w: 5.0, h: 1.0, label: 'S4' },
            { id: 'S5', x: -4.8, y: 1.5, w: 5.0, h: 1.0, label: 'S5' },
            { id: 'S6', x: 4.8, y: 1.5, w: 5.0, h: 1.0, label: 'S6' },
            { id: 'S7', x: -4.8, y: -3.0, w: 5.0, h: 1.0, label: 'S7' },
            { id: 'S8', x: 4.8, y: -3.0, w: 5.0, h: 1.0, label: 'S8' }
        ];

        // Static obstacles & environmental props.
        this.staticObstacles = [
            // Movable container parked in the central corridor — the blocked-aisle prop
            { id: 'OBS_AISLE', x: -0.2, y: 0.75, w: 0.8, h: 1.2, label: 'Blocked Aisle Container', color: '#F97316' },
            // Green waste container, south-west
            { id: 'DUMPSTER', x: -2.8, y: -7.3, w: 1.2, h: 0.8, label: 'Waste Container', color: '#15803D' },
            // Cardboard pallet towers
            { id: 'PALLET_SW', x: -5.2, y: -7.3, w: 1.5, h: 1.5, label: 'Pallet Stack', color: '#B45309' },
            { id: 'PALLET_NE', x: 5.2, y: 8.75, w: 1.5, h: 1.5, label: 'Pallet Stack', color: '#B45309' },
            { id: 'PALLET_NW', x: -8.0, y: 5.25, w: 1.5, h: 1.5, label: 'Pallet Stack', color: '#B45309' }
        ];

        // ── Robot Palette (Industrial identifiable colors) ───────────────────
        this.robotColors = {
            'A': { primary: '#0284C7', light: '#E0F2FE', dark: '#0369A1' }, // Blue
            'B': { primary: '#16A34A', light: '#DCFCE7', dark: '#15803D' }, // Green
            'C': { primary: '#EA580C', light: '#FFEDD5', dark: '#C2410C' }  // Orange
        };

        // ── Viewport & Transform State (Auto-Framing) ────────────────────
        this.scale = 24.0; // dynamic
        this.offsetX = 0;
        this.offsetY = 0;

        // ── Visual Layer Toggles ─────────────────────────────────────────────
        this.showPaths = true;
        this.showLabels = true;
        this.showGrid = true;
        this.showLanes = true;
        this.showObstacles = true;

        // ── Live Telemetry & Interpolation State ──────────────────────────────
        this.liveRobots = {};
        this.visualRobots = {};
        // robot_id -> planned route [[x, y], ...] still ahead of the robot
        this.plannedPaths = {};
        this.reservations = [];
        this.intents = [];
        this.events = [];
        this.tasks = [];

        // Trajectory History for path breadcrumbs
        this.history = { 'A': [], 'B': [], 'C': [] };
        this.maxHistoryLength = 40;

        // Selection & Hover
        this.selectedRobotId = null;
        this.hoveredEntity = null;
        this.cursorWorldCoords = { x: 0.0, y: 0.0 };

        // Selection callback
        this.onSelectRobot = null;

        // Animation timing
        this.lastFrameTime = performance.now();

        // Initialize setup
        this.initCanvas();
        this.initEvents();
        this.startRenderLoop();
    }

    initCanvas() {
        // Observe the wrapper only. The canvas size is derived from the wrapper, so
        // observing the canvas too would re-enter resize() on every size we set.
        const ro = new ResizeObserver(() => this.resize());
        if (this.canvas.parentElement) {
            ro.observe(this.canvas.parentElement);
        }

        window.addEventListener('resize', () => this.resize());

        // The first ResizeObserver callback can arrive while the flex layout is
        // still resolving, at which point the wrapper measures 0 and resize() bails.
        // Retry until we get a real size, so the viewport is never left on its
        // placeholder transform. A hidden tab gets no animation frames, so fall
        // back to a timer there rather than waiting for the tab to be focused.
        let tries = 0;
        const fit = () => {
            this.resize();
            if (this.screenWidth && this.screenWidth >= 10) return;
            if (tries++ >= 120) return;
            if (document.hidden) {
                setTimeout(fit, 100);
            } else {
                requestAnimationFrame(fit);
            }
        };
        fit();

        // Re-fit when the tab becomes visible again; a tab that was hidden the
        // whole time it was loading has never had a real layout to measure.
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) this.resize();
        });
    }

    /**
     * Size the canvas as the largest square that fits its wrapper.
     *
     * The wrapper is whatever shape the dashboard grid gives it (usually wide).
     * Taking min(width, height) makes the drawing surface square, which combined
     * with the single `scale` in updateViewportTransform() is what guarantees the
     * 20 m x 20 m world is drawn as a square with equal X and Y scale.
     *
     * Width and height are written as explicit pixels rather than left to CSS: a
     * canvas takes its intrinsic size from its width/height attributes, so an auto
     * CSS width lets the backing store feed back into layout and the element grows
     * on each pass.
     */
    resize() {
        if (!this.canvas) return;
        const host = this.canvas.parentElement;
        if (!host) return;

        const hostRect = host.getBoundingClientRect();
        const side = Math.floor(Math.min(hostRect.width, hostRect.height)) - MAP_EDGE_INSET * 2;
        if (side < 10) return;   // layout not resolved yet; the caller retries

        this.canvas.style.width = side + 'px';
        this.canvas.style.height = side + 'px';

        const dpr = window.devicePixelRatio || 1;
        const backing = Math.round(side * dpr);
        if (this.canvas.width !== backing || this.canvas.height !== backing) {
            this.canvas.width = backing;
            this.canvas.height = backing;
        }
        this.ctx.resetTransform?.();
        this.ctx.scale(dpr, dpr);

        // Must be assigned before updateViewportTransform(), which reads them.
        this.screenWidth = side;
        this.screenHeight = side;
        this.updateViewportTransform();
    }

    // ── Coordinate Conversions (Auto-Framing) ──────────────

    updateViewportTransform() {
        if (!this.canvas || !this.screenWidth || !this.screenHeight) return;
        const padding = 18; // pixels of breathing room around the world square

        const availableW = Math.max(1, this.screenWidth - padding * 2);
        const availableH = Math.max(1, this.screenHeight - padding * 2);

        // ONE scale for both axes. Never derive an independent scaleX/scaleY:
        // a metre of X and a metre of Y must occupy the same number of pixels,
        // so the 20 x 20 world always renders as a true square.
        this.scale = Math.min(availableW / this.world.width,
                              availableH / this.world.height);

        // Centre the world square (which is centred on the origin) in the view.
        this.offsetX = this.screenWidth / 2;
        this.offsetY = this.screenHeight / 2;
    }

    worldToScreen(gx, gy) {
        return {
            x: this.offsetX + gx * this.scale,
            y: this.offsetY - gy * this.scale // Invert Y for Canvas
        };
    }

    screenToWorld(sx, sy) {
        return {
            x: (sx - this.offsetX) / this.scale,
            y: (this.offsetY - sy) / this.scale
        };
    }

    // ── Mouse & Touch Event Handlers ─────────────────────────────────────────

    initEvents() {
        if (!this.canvas) return;

        window.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            if (mouseX >= 0 && mouseX <= rect.width && mouseY >= 0 && mouseY <= rect.height) {
                this.cursorWorldCoords = this.screenToWorld(mouseX, mouseY);
                const coordsBadge = document.getElementById('map-coords');
                if (coordsBadge) {
                    coordsBadge.textContent = `X: ${this.cursorWorldCoords.x.toFixed(2)}m  Y: ${this.cursorWorldCoords.y.toFixed(2)}m`;
                }
                this.checkHover(mouseX, mouseY);
            }
        });

        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            this.handleClick(mouseX, mouseY);
        });
    }

    checkHover(screenX, screenY) {
        const hitRadius = 24;
        let hovered = null;

        Object.values(this.visualRobots).forEach(r => {
            const sp = this.worldToScreen(r.x, r.y);
            const dist = Math.hypot(sp.x - screenX, sp.y - screenY);
            if (dist < hitRadius) {
                hovered = { type: 'robot', id: r.robot_id, data: r };
            }
        });

        if (!hovered) {
            Object.entries(this.stations).forEach(([id, st]) => {
                const sp = this.worldToScreen(st.x, st.y);
                const dist = Math.hypot(sp.x - screenX, sp.y - screenY);
                if (dist < hitRadius) {
                    hovered = { type: 'station', id, data: st };
                }
            });
        }

        this.hoveredEntity = hovered;
    }

    handleClick(screenX, screenY) {
        const hitRadius = 26;
        let clickedRobot = null;

        Object.values(this.visualRobots).forEach(r => {
            const sp = this.worldToScreen(r.x, r.y);
            const dist = Math.hypot(sp.x - screenX, sp.y - screenY);
            if (dist < hitRadius) {
                clickedRobot = r.robot_id;
            }
        });

        if (clickedRobot) {
            this.selectRobot(clickedRobot);
        } else {
            this.selectRobot(null);
        }
    }

    selectRobot(robotId) {
        this.selectedRobotId = robotId;
        if (typeof this.onSelectRobot === 'function') {
            this.onSelectRobot(robotId);
        }
    }

    // ── Telemetry Ingestion ──────────────────────────────────────────────────

    setPlannedPaths(paths = {}) {
        this.plannedPaths = paths || {};
    }

    updateTelemetry(robots = {}, reservations = [], intents = [], events = [], tasks = []) {
        this.liveRobots = robots;
        this.reservations = reservations;
        this.intents = intents;
        this.events = events;
        this.tasks = tasks;

        const now = performance.now();

        Object.entries(robots).forEach(([rid, r]) => {
            if (!this.visualRobots[rid]) {
                this.visualRobots[rid] = {
                    robot_id: rid,
                    x: r.x,
                    y: r.y,
                    yaw: r.yaw || 0.0,
                    velocity: r.velocity || 0.0,
                    battery: r.battery !== undefined ? r.battery : 100.0,
                    status: r.status || 'IDLE',
                    task_id: r.task_id || null,
                    targetX: r.x,
                    targetY: r.y,
                    targetYaw: r.yaw || 0.0,
                    fromX: r.x,
                    fromY: r.y,
                    fromYaw: r.yaw || 0.0,
                    legDuration: 500,
                    legElapsed: 500,
                    lastTargetTime: now
                };
            } else {
                const vr = this.visualRobots[rid];
                const moved = Math.hypot(r.x - vr.targetX, r.y - vr.targetY) > 1e-6
                           || Math.abs((r.yaw || 0) - vr.targetYaw) > 1e-6;

                if (moved) {
                    // A target metres away from where we are drawing is a
                    // telemetry gap (adapter reconnect, backgrounded tab, node
                    // restart, AMCL correction), not travel. Smoothstepping to
                    // it slides the icon in a straight line over racks and
                    // stations, which reads as the AMR driving through them.
                    // Snap instead: the robot is simply somewhere else now.
                    if (Math.hypot(r.x - vr.x, r.y - vr.y) > TELEMETRY_JUMP_METRES) {
                        vr.x = r.x; vr.y = r.y;
                        vr.yaw = r.yaw !== undefined ? r.yaw : vr.yaw;
                    }
                    // Start this leg from where the robot is being drawn right now,
                    // so playback is continuous even if the last leg had not finished.
                    vr.fromX = vr.x;
                    vr.fromY = vr.y;
                    vr.fromYaw = vr.yaw;
                    vr.targetX = r.x;
                    vr.targetY = r.y;
                    vr.targetYaw = r.yaw !== undefined ? r.yaw : vr.targetYaw;

                    // Measured telemetry interval, clamped so one late packet
                    // cannot stall or fast-forward the animation.
                    const measured = now - vr.lastTargetTime;
                    vr.legDuration = Math.min(1500, Math.max(60, measured));
                    vr.legElapsed = 0;
                    vr.lastTargetTime = now;
                }

                vr.velocity = r.velocity || 0.0;
                vr.battery = r.battery !== undefined ? r.battery : 100.0;
                vr.status = r.status || 'IDLE';
                vr.task_id = r.task_id || null;
            }

            if (!this.history[rid]) this.history[rid] = [];
            const hist = this.history[rid];
            const lastPt = hist[hist.length - 1];
            const step = lastPt ? Math.hypot(lastPt.x - r.x, lastPt.y - r.y) : 0;
            if (!lastPt || step > 0.15) {
                // Same reasoning as the leg snap above: joining the two sides of
                // a telemetry gap draws a dashed line straight through the
                // racking. Flag the break so the trail shows a gap instead.
                hist.push({ x: r.x, y: r.y, discontinuity: !!lastPt && step > TELEMETRY_JUMP_METRES });
                if (hist.length > this.maxHistoryLength) hist.shift();
            }
        });
    }

    // ── 60 FPS Render Loop with Smooth Interpolation ─────────────────────────

    startRenderLoop() {
        const loop = (time) => {
            const dt = Math.min(0.1, (time - this.lastFrameTime) / 1000);
            this.lastFrameTime = time;

            this.interpolateRobots(dt);
            this.render();

            requestAnimationFrame(loop);
        };
        requestAnimationFrame(loop);
    }

    /**
     * Advance the DISPLAYED pose of each robot.
     *
     * Purely a rendering concern. `visualRobots` is never read back as robot
     * state and is never sent anywhere -- `liveRobots` holds the authoritative
     * telemetry exactly as it arrived, and every panel, table and export reads
     * that. This only decides which pixel to draw between two real samples.
     *
     * Telemetry lands in discrete packets (~10 Hz live, 500 ms fallback). The
     * previous exponential ease had a ~100 ms time constant, so the robot
     * snapped most of the way to the new sample and then sat still until the
     * next one -- the "hop and wait" stutter. Playing each leg out at constant
     * speed over the measured interval turns the same samples into continuous
     * motion.
     */
    interpolateRobots(dt) {
        Object.values(this.visualRobots).forEach(r => {
            r.legElapsed = (r.legElapsed || 0) + dt * 1000.0;
            const duration = r.legDuration || 500;
            const t = Math.min(1.0, r.legElapsed / duration);

            // smoothstep: no velocity discontinuity at the seam between legs
            const e = t * t * (3.0 - 2.0 * t);

            const fromX = (r.fromX !== undefined) ? r.fromX : r.targetX;
            const fromY = (r.fromY !== undefined) ? r.fromY : r.targetY;
            const fromYaw = (r.fromYaw !== undefined) ? r.fromYaw : r.targetYaw;

            r.x = fromX + (r.targetX - fromX) * e;
            r.y = fromY + (r.targetY - fromY) * e;

            // shortest-arc yaw
            let deltaYaw = r.targetYaw - fromYaw;
            while (deltaYaw < -Math.PI) deltaYaw += Math.PI * 2;
            while (deltaYaw > Math.PI) deltaYaw -= Math.PI * 2;
            r.yaw = fromYaw + deltaYaw * e;
        });
    }

    // ═════════════════════════════════════════════════════════════════════════
    // RENDER PIPELINE
    // ═════════════════════════════════════════════════════════════════════════

    render() {
        if (!this.ctx || !this.screenWidth || !this.screenHeight) return;
        const ctx = this.ctx;

        // Clear canvas
        ctx.clearRect(0, 0, this.screenWidth, this.screenHeight);

        // 1. Concrete floor slab
        this.renderFloor(ctx);

        // 2. Safety navigation lanes
        if (this.showLanes) {
            this.renderSafetyLanes(ctx);
        }

        // 3. Station zones & Intersections
        this.renderStationZones(ctx);
        this.renderIntersections(ctx);

        // 4. Shelving racks S1-S8
        this.renderShelvingRacks(ctx);

        // 5. Environmental obstacles & pallets
        if (this.showObstacles) {
            this.renderObstacles(ctx);
        }

        // 6. Perimeter walls & structural pillars
        this.renderPerimeterWalls(ctx);

        // 7. Breadcrumb history, then the route still to be driven
        if (this.showPaths) {
            this.renderTrajectoryPaths(ctx);
            this.renderPlannedPaths(ctx);
        }

        // 8. AMRs with top-down industrial geometry & charging state
        this.renderRobots(ctx);

        // 9. Floating overlays (Hover readout, legend)
        this.renderOverlays(ctx);
    }

    // ── 1. Floor slab & Grid ─────────────────────────────────────────────────

    renderFloor(ctx) {
        const p1 = this.worldToScreen(this.world.minX, this.world.maxY);
        const p2 = this.worldToScreen(this.world.maxX, this.world.minY);
        const fw = p2.x - p1.x;
        const fh = p2.y - p1.y;

        // Concrete slab base color (matching Gazebo concrete)
        ctx.fillStyle = '#E8ECEF';
        ctx.fillRect(p1.x, p1.y, fw, fh);

        // 5m major concrete tile grid
        if (this.showGrid) {
            ctx.save();
            ctx.strokeStyle = '#D8DFE5';
            ctx.lineWidth = 1;

            // 1m fine grid lines
            for (let x = -9; x <= 9; x += 1) {
                if (x === 0 || x % 5 === 0) continue;
                const sp1 = this.worldToScreen(x, this.world.maxY);
                const sp2 = this.worldToScreen(x, this.world.minY);
                ctx.beginPath();
                ctx.moveTo(sp1.x, sp1.y);
                ctx.lineTo(sp2.x, sp2.y);
                ctx.stroke();
            }

            for (let y = -9; y <= 9; y += 1) {
                if (y === 0 || y % 5 === 0) continue;
                const sp1 = this.worldToScreen(this.world.minX, y);
                const sp2 = this.worldToScreen(this.world.maxX, y);
                ctx.beginPath();
                ctx.moveTo(sp1.x, sp1.y);
                ctx.lineTo(sp2.x, sp2.y);
                ctx.stroke();
            }

            // 5m major tiles
            ctx.strokeStyle = '#CBD5E1';
            ctx.lineWidth = 1.5;
            for (let x = -5; x <= 5; x += 5) {
                const sp1 = this.worldToScreen(x, this.world.maxY);
                const sp2 = this.worldToScreen(x, this.world.minY);
                ctx.beginPath();
                ctx.moveTo(sp1.x, sp1.y);
                ctx.lineTo(sp2.x, sp2.y);
                ctx.stroke();
            }
            for (let y = -5; y <= 5; y += 5) {
                const sp1 = this.worldToScreen(this.world.minX, y);
                const sp2 = this.worldToScreen(this.world.maxX, y);
                ctx.beginPath();
                ctx.moveTo(sp1.x, sp1.y);
                ctx.lineTo(sp2.x, sp2.y);
                ctx.stroke();
            }
            ctx.restore();
        }
    }

    // ── 2. Green Safety Navigation Lanes ────────────────────────────────────

    renderSafetyLanes(ctx) {
        ctx.save();
        ctx.strokeStyle = '#10B981'; // Industrial Green Safety Line
        ctx.lineWidth = Math.max(2, this.scale * 0.08);
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        // Lane markings painted on the warehouse floor, taken from the
        // `lane_*` floor visuals in warehouse.sdf so the canvas shows the same
        // markings Gazebo renders. Horizontal lanes are 18.4 m long (x +/- 9.2),
        // vertical lanes 18.2 m (y +/- 9.1).
        const hLanes = [
            9.1,    // lane_a1_t — north bypass, top edge
            5.9,    // lane_a1_b — north bypass, bottom edge
            4.5,    // lane_a2_t — main north aisle, top edge
            0.0,    // lane_a2_b — main north aisle, bottom edge
            -1.4    // lane_a3_t — central cross-aisle
        ];

        hLanes.forEach(y => {
            const sp1 = this.worldToScreen(-9.2, y);
            const sp2 = this.worldToScreen(9.2, y);
            ctx.beginPath();
            ctx.moveTo(sp1.x, sp1.y);
            ctx.lineTo(sp2.x, sp2.y);
            ctx.stroke();
        });

        const vLanes = [
            -8.2,   // lane_bp_w — west perimeter bypass
            -1.4,   // lane_cv_l — central corridor, west edge
            1.4,    // lane_cv_r — central corridor, east edge
            8.2     // lane_bp_e — east perimeter bypass
        ];

        vLanes.forEach(x => {
            const sp1 = this.worldToScreen(x, 9.1);
            const sp2 = this.worldToScreen(x, -9.1);
            ctx.beginPath();
            ctx.moveTo(sp1.x, sp1.y);
            ctx.lineTo(sp2.x, sp2.y);
            ctx.stroke();
        });

        ctx.restore();
    }

    // ── 3. Stations & Intersections ──────────────────────────────────────────

    renderStationZones(ctx) {
        Object.entries(this.stations).forEach(([id, st]) => {
            const sp = this.worldToScreen(st.x, st.y);
            // Pad footprint in metres, from the world file; `size` stays the
            // icon/'font' scale so the glyphs keep their previous proportions.
            const padW = (st.w || 1.8) * this.scale;
            const padH = (st.h || 1.8) * this.scale;
            const size = Math.min(padW, padH);

            ctx.save();
            ctx.translate(sp.x, sp.y);

            // White concrete bay pad
            ctx.fillStyle = '#FFFFFF';
            ctx.fillRect(-padW / 2, -padH / 2, padW, padH);

            // Yellow/Black dashed hazard boundary
            ctx.strokeStyle = '#EAB308';
            ctx.lineWidth = 2.5;
            ctx.setLineDash([5, 4]);
            ctx.strokeRect(-padW / 2, -padH / 2, padW, padH);
            ctx.setLineDash([]);

            // Station Identity Icon/Letter
            if (st.type === 'charging') {
                // Charging Station Dock Console at top
                ctx.fillStyle = '#1E293B';
                ctx.fillRect(-size * 0.35, -size / 2 - 4, size * 0.7, 6);

                // Bright Yellow Lightning Bolt Symbol ⚡
                ctx.fillStyle = '#EAB308';
                ctx.font = `bold ${Math.round(size * 0.55)}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('⚡', 0, 0);

                if (this.showLabels) {
                    ctx.font = `bold 9px sans-serif`;
                    ctx.fillStyle = '#854D0E';
                    ctx.fillText('CHG', 0, size * 0.35);
                }
            } else if (st.type === 'pickup') {
                // Green Bold 'P'
                ctx.fillStyle = '#16A34A';
                ctx.font = `bold ${Math.round(size * 0.55)}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(st.code || 'P', 0, 0);
            } else if (st.type === 'dropoff') {
                // Cyan/Blue Bold 'D'
                ctx.fillStyle = '#0284C7';
                ctx.font = `bold ${Math.round(size * 0.55)}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(st.code || 'D', 0, 0);
            }

            ctx.restore();
        });
    }

    renderIntersections(ctx) {
        Object.entries(this.intersections).forEach(([id, inter]) => {
            const sp = this.worldToScreen(inter.x, inter.y);
            const size = 1.8 * this.scale;

            // Check reservation state
            const res = this.reservations.find(r => r.resource_id === id);
            const isReserved = res && res.status === 'ACTIVE';

            ctx.save();
            ctx.translate(sp.x, sp.y);

            // White intersection zone tile
            ctx.fillStyle = isReserved ? '#FEF2F2' : '#FFFFFF';
            ctx.fillRect(-size / 2, -size / 2, size, size);

            // Yellow dashed boundary
            ctx.strokeStyle = isReserved ? '#EF4444' : '#EAB308';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 4]);
            ctx.strokeRect(-size / 2, -size / 2, size, size);
            ctx.setLineDash([]);

            // Red Cross Marker (+)
            ctx.strokeStyle = '#DC2626';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(-size * 0.25, 0);
            ctx.lineTo(size * 0.25, 0);
            ctx.moveTo(0, -size * 0.25);
            ctx.lineTo(0, size * 0.25);
            ctx.stroke();

            // Safety Bollards (small cylindrical posts)
            if (inter.bollards) {
                inter.bollards.forEach(bx => {
                    const bpX = bx * this.scale;
                    ctx.fillStyle = '#F59E0B'; // Safety yellow
                    ctx.beginPath();
                    ctx.arc(bpX, 0, 3, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = '#000000';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                });
            }

            // Label
            if (this.showLabels) {
                ctx.font = 'bold 9px sans-serif';
                ctx.fillStyle = isReserved ? '#991B1B' : '#64748B';
                ctx.textAlign = 'center';
                ctx.fillText(id, 0, size * 0.38);
            }

            ctx.restore();
        });
    }

    // ── 4. Shelving Racks S1-S8 ──────────────────────────────────────────────

    renderShelvingRacks(ctx) {
        this.racks.forEach(rk => {
            const sp = this.worldToScreen(rk.x, rk.y);
            const w = rk.w * this.scale;
            const h = rk.h * this.scale;

            ctx.save();
            ctx.translate(sp.x, sp.y);

            // Drop shadow
            ctx.fillStyle = 'rgba(0, 0, 0, 0.12)';
            ctx.fillRect(-w / 2 + 3, -h / 2 + 3, w, h);

            // Industrial Bright Yellow Shelf Body (matching Gazebo racks)
            ctx.fillStyle = '#FACC15';
            ctx.fillRect(-w / 2, -h / 2, w, h);

            // Metallic border
            ctx.strokeStyle = '#CA8A04';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(-w / 2, -h / 2, w, h);

            // Dark metallic end frames on the rack's short ends. A rack is
            // 5.0 m long by 1.0 m deep, so the end frames are the left/right
            // edges -- the aisle faces are the long sides.
            const cap = Math.max(2, Math.min(4, w * 0.02));
            ctx.fillStyle = '#1E293B';
            ctx.fillRect(-w / 2, -h / 2, cap, h);
            ctx.fillRect(w / 2 - cap, -h / 2, cap, h);

            // Bay uprights along the rack's length
            ctx.strokeStyle = '#CA8A04';
            ctx.lineWidth = 1;
            const bays = 4;
            for (let i = 1; i < bays; i++) {
                const dx = -w / 2 + (w / bays) * i;
                ctx.beginPath();
                ctx.moveTo(dx, -h / 2);
                ctx.lineTo(dx, h / 2);
                ctx.stroke();
            }

            // Rack ID. Sized off the SHORT side so the label stays inside the
            // 1.0 m depth instead of spilling across the aisle.
            if (this.showLabels) {
                ctx.fillStyle = '#000000';
                ctx.font = `bold ${Math.max(8, Math.round(Math.min(h * 0.62, w * 0.14)))}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(rk.label, 0, 0);
            }

            ctx.restore();
        });
    }

    // ── 5. Environmental Obstacles & Pallets ─────────────────────────────────

    renderObstacles(ctx) {
        this.staticObstacles.forEach(obs => {
            const sp = this.worldToScreen(obs.x, obs.y);
            const w = (obs.w || 1.2) * this.scale;
            const h = (obs.h || 1.2) * this.scale;

            ctx.save();
            ctx.translate(sp.x, sp.y);

            if (obs.isZone) {
                // Dashed hazard box around pallet stack
                ctx.strokeStyle = '#EAB308';
                ctx.lineWidth = 2;
                ctx.setLineDash([4, 3]);
                ctx.strokeRect(-w * 0.7, -h * 0.7, w * 1.4, h * 1.4);
                ctx.setLineDash([]);
            }

            // Object drop shadow
            ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
            ctx.fillRect(-w / 2 + 2, -h / 2 + 2, w, h);

            // Base Body
            ctx.fillStyle = obs.color || '#F97316';
            ctx.fillRect(-w / 2, -h / 2, w, h);

            ctx.strokeStyle = 'rgba(0, 0, 0, 0.25)';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(-w / 2, -h / 2, w, h);

            // Container / Pallet internal details
            if (obs.id === 'OBS_AISLE') {
                // Orange hazard diagonal stripes
                ctx.strokeStyle = '#EA580C';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(-w / 2, -h / 2); ctx.lineTo(w / 2, h / 2);
                ctx.moveTo(w / 2, -h / 2); ctx.lineTo(-w / 2, h / 2);
                ctx.stroke();
            } else if (obs.id === 'DUMPSTER') {
                // Dark green dumpster lid lines
                ctx.fillStyle = '#14532D';
                ctx.fillRect(-w / 2, -h / 2, w, 4);
            } else if (obs.id.startsWith('PALLET')) {
                // Wood slat lines
                ctx.strokeStyle = '#78350F';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(-w / 2, 0); ctx.lineTo(w / 2, 0);
                ctx.stroke();
            }

            ctx.restore();
        });
    }

    // ── 6. Perimeter Walls & Pillars ─────────────────────────────────────────

    renderPerimeterWalls(ctx) {
        const p1 = this.worldToScreen(this.world.minX, this.world.maxY);
        const p2 = this.worldToScreen(this.world.maxX, this.world.minY);
        const fw = p2.x - p1.x;
        const fh = p2.y - p1.y;
        const wallThick = Math.max(8, this.scale * 0.35);

        ctx.save();

        // Dark grey solid perimeter walls (matching Gazebo enclosure)
        ctx.fillStyle = '#475569';

        // North wall
        ctx.fillRect(p1.x - wallThick, p1.y - wallThick, fw + wallThick * 2, wallThick);
        // South wall
        ctx.fillRect(p1.x - wallThick, p2.y, fw + wallThick * 2, wallThick);
        // West wall
        ctx.fillRect(p1.x - wallThick, p1.y, wallThick, fh);
        // East wall
        ctx.fillRect(p2.x, p1.y, wallThick, fh);

        // Outer Structural Buttress Pillars (matching screenshot)
        ctx.fillStyle = '#1E293B';
        const pillarDist = 5.0; // every 5m
        for (let x = -10; x <= 10; x += pillarDist) {
            const topP = this.worldToScreen(x, 10.0);
            const botP = this.worldToScreen(x, -10.0);
            ctx.fillRect(topP.x - 3, topP.y - wallThick - 4, 6, wallThick + 4);
            ctx.fillRect(botP.x - 3, botP.y, 6, wallThick + 4);
        }
        for (let y = -10; y <= 10; y += pillarDist) {
            const leftP = this.worldToScreen(-10.0, y);
            const rightP = this.worldToScreen(10.0, y);
            ctx.fillRect(leftP.x - wallThick - 4, leftP.y - 3, wallThick + 4, 6);
            ctx.fillRect(rightP.x, rightP.y - 3, wallThick + 4, 6);
        }

        ctx.restore();
    }

    // ── 7. Trajectory Breadcrumbs ────────────────────────────────────────────

    renderTrajectoryPaths(ctx) {
        ctx.save();
        Object.entries(this.history).forEach(([rid, pts]) => {
            if (pts.length < 2) return;
            const col = this.robotColors[rid]?.primary || '#64748B';

            ctx.strokeStyle = col;
            ctx.lineWidth = 2;
            ctx.setLineDash([4, 4]);
            ctx.globalAlpha = 0.45;

            ctx.beginPath();
            pts.forEach((pt, i) => {
                const sp = this.worldToScreen(pt.x, pt.y);
                if (i === 0 || pt.discontinuity) ctx.moveTo(sp.x, sp.y);
                else ctx.lineTo(sp.x, sp.y);
            });
            ctx.stroke();
        });
        ctx.restore();
    }

    /**
     * The route each robot still has to drive.
     *
     * Drawn from the same waypoints the robot is actually following, so the
     * line bends through the aisles instead of cutting across racking. The
     * breadcrumb trail behind it shows where the robot has been; this shows
     * where it is going.
     */
    renderPlannedPaths(ctx) {
        ctx.save();
        Object.entries(this.plannedPaths).forEach(([rid, pts]) => {
            if (!pts || pts.length < 2) return;
            const col = this.robotColors[rid]?.primary || '#64748B';

            // Soft halo so the route reads over the floor grid.
            ctx.strokeStyle = 'rgba(255,255,255,0.85)';
            ctx.lineWidth = 5;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';
            ctx.setLineDash([]);
            ctx.beginPath();
            pts.forEach((pt, i) => {
                const sp = this.worldToScreen(pt[0], pt[1]);
                if (i === 0) ctx.moveTo(sp.x, sp.y); else ctx.lineTo(sp.x, sp.y);
            });
            ctx.stroke();

            ctx.strokeStyle = col;
            ctx.globalAlpha = 0.9;
            ctx.lineWidth = 2.5;
            ctx.setLineDash([7, 5]);
            ctx.lineDashOffset = -(performance.now() / 45) % 12;   // gentle flow toward the goal
            ctx.beginPath();
            pts.forEach((pt, i) => {
                const sp = this.worldToScreen(pt[0], pt[1]);
                if (i === 0) ctx.moveTo(sp.x, sp.y); else ctx.lineTo(sp.x, sp.y);
            });
            ctx.stroke();
            ctx.setLineDash([]);

            // Goal marker at the end of the route.
            const goal = this.worldToScreen(pts[pts.length - 1][0], pts[pts.length - 1][1]);
            ctx.globalAlpha = 1.0;
            ctx.fillStyle = col;
            ctx.beginPath(); ctx.arc(goal.x, goal.y, 4.5, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = '#FFFFFF'; ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.arc(goal.x, goal.y, 4.5, 0, Math.PI * 2); ctx.stroke();
        });
        ctx.restore();
    }

    // ── 8. Top-Down Industrial AMRs with Charging State ─────────────────────

    renderRobots(ctx) {
        Object.values(this.visualRobots).forEach(r => {
            const sp = this.worldToScreen(r.x, r.y);
            const col = this.robotColors[r.robot_id] || { primary: '#0284C7', light: '#E0F2FE', dark: '#0369A1' };
            const isSelected = this.selectedRobotId === r.robot_id;
            const isCharging = r.status === 'CHARGING';

            // Robot Physical Footprint: 0.65m x 0.50m (TurtleBot / Industrial AMR)
            const length = 0.65 * this.scale;
            const width = 0.50 * this.scale;

            ctx.save();
            ctx.translate(sp.x, sp.y);

            // Selection halo ring
            if (isSelected) {
                ctx.strokeStyle = col.primary;
                ctx.lineWidth = 2.5;
                ctx.setLineDash([4, 3]);
                ctx.beginPath();
                ctx.arc(0, 0, Math.max(length, width) * 1.1, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            // Charging Glow Effect when docked
            if (isCharging) {
                ctx.fillStyle = 'rgba(234, 179, 8, 0.25)';
                ctx.beginPath();
                ctx.arc(0, 0, Math.max(length, width) * 1.25, 0, Math.PI * 2);
                ctx.fill();
            }

            // Invert yaw for screen coordinates (+Y is North)
            ctx.rotate(-r.yaw);

            // AMR Drop Shadow
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.fillRect(-length / 2 + 2, -width / 2 + 2, length, width);

            // AMR Main Chassis (Dark industrial body)
            ctx.fillStyle = '#1E293B';
            ctx.fillRect(-length / 2, -width / 2, length, width);

            // Directional Front Bumper (Color coded)
            ctx.fillStyle = col.primary;
            ctx.fillRect(length / 2 - 4, -width / 2, 4, width);

            // Status LED Ring in Center
            let ledColor = '#10B981'; // Green = OK
            if (isCharging) ledColor = '#EAB308'; // Yellow = Charging
            if (r.status === 'WAITING' || r.status === 'REROUTING') ledColor = '#F59E0B';
            if (r.status === 'FAILED') ledColor = '#EF4444';

            ctx.fillStyle = ledColor;
            ctx.beginPath();
            ctx.arc(0, 0, 4, 0, Math.PI * 2);
            ctx.fill();

            // Rotating LIDAR puck (top center)
            ctx.fillStyle = '#0F172A';
            ctx.beginPath();
            ctx.arc(-length * 0.1, 0, 3, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();

            // ── Robot ID & Status Callout Label ──
            ctx.save();
            ctx.translate(sp.x, sp.y);

            const badgeY = -width * 0.9 - 6;

            // ID Badge pill
            ctx.fillStyle = isCharging ? '#FEF3C7' : '#FFFFFF';
            ctx.strokeStyle = isCharging ? '#EAB308' : col.primary;
            ctx.lineWidth = 1.5;
            const badgeText = isCharging ? `⚡ AMR ${r.robot_id} [${Math.round(r.battery)}%]` : `AMR ${r.robot_id}`;

            ctx.font = 'bold 10px sans-serif';
            const tw = ctx.measureText(badgeText).width;

            ctx.fillRect(-tw / 2 - 5, badgeY - 7, tw + 10, 14);
            ctx.strokeRect(-tw / 2 - 5, badgeY - 7, tw + 10, 14);

            ctx.fillStyle = isCharging ? '#854D0E' : '#0F172A';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(badgeText, 0, badgeY);

            ctx.restore();
        });
    }

    // ── 9. Overlays (Hover Readout) ──────────────────────────────────────────

    renderOverlays(ctx) {
        if (this.hoveredEntity && this.hoveredEntity.type === 'robot') {
            const r = this.hoveredEntity.data;
            const sp = this.worldToScreen(r.x, r.y);

            ctx.save();
            ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 1;

            const text = `AMR ${r.robot_id}: (${r.x.toFixed(2)}, ${r.y.toFixed(2)}) | ${r.status} | Bat: ${Math.round(r.battery)}%`;
            ctx.font = '11px monospace';
            const tw = ctx.measureText(text).width;

            const boxX = Math.min(this.screenWidth - tw - 20, Math.max(10, sp.x - tw / 2));
            const boxY = sp.y + 24;

            ctx.fillRect(boxX, boxY, tw + 16, 22);
            ctx.strokeRect(boxX, boxY, tw + 16, 22);

            ctx.fillStyle = '#F8FAFC';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(text, boxX + 8, boxY + 11);

            ctx.restore();
        }
    }
}
