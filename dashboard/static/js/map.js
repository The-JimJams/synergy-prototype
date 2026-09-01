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

        // ── Stations & Infrastructure (from Gazebo visual layout) ────────────
        this.stations = {
            'P1': { x: -7.2, y: 0.0, label: 'Pickup Station (P)', type: 'pickup', code: 'P', color: '#16A34A' },
            'D1': { x: 6.8, y: 0.0, label: 'Dropoff Station (D)', type: 'dropoff', code: 'D', color: '#0284C7' },
            'CHG': { x: 6.0, y: 6.0, label: 'Charging Bay (CHG)', type: 'charging', code: '⚡', color: '#EAB308' }
        };

        // Shared Intersections with Red Cross markers & Bollards
        this.intersections = {
            'I1': { x: -4.3, y: 0.0, label: 'Intersection 1', bollards: [-0.85, 0.85] },
            'I2': { x: 0.8, y: 0.0, label: 'Intersection 2', bollards: [-0.85, 0.85] }
        };

        // 8 Vertical Shelving Racks (S1 to S8) matching Gazebo layout
        // Top row: S2, S4, S6, S8 (y = 5.5) | Bottom row: S1, S3, S5, S7 (y = -5.5)
        this.racks = [
            { id: 'S2', x: -6.5, y: 5.5, w: 1.5, h: 4.4, label: 'S2' },
            { id: 'S4', x: -2.1, y: 5.5, w: 1.5, h: 4.4, label: 'S4' },
            { id: 'S6', x: -0.7, y: 5.5, w: 1.5, h: 4.4, label: 'S6' },
            { id: 'S8', x: 3.2, y: 5.5, w: 1.5, h: 4.4, label: 'S8' },

            { id: 'S1', x: -6.5, y: -5.5, w: 1.5, h: 4.4, label: 'S1' },
            { id: 'S3', x: -2.1, y: -5.5, w: 1.5, h: 4.4, label: 'S3' },
            { id: 'S5', x: -0.7, y: -5.5, w: 1.5, h: 4.4, label: 'S5' },
            { id: 'S7', x: 3.2, y: -5.5, w: 1.5, h: 4.4, label: 'S7' }
        ];

        // Static Obstacles & Environmental Props
        this.staticObstacles = [
            // Orange container in central corridor
            { id: 'OBS_AISLE', x: -1.5, y: 0.0, w: 1.2, h: 1.0, label: 'Obstacle Box', color: '#F97316' },
            // Green Dumpster (East side)
            { id: 'DUMPSTER', x: 6.2, y: -2.5, w: 1.4, h: 1.1, label: 'Waste Container', color: '#15803D' },
            // Cardboard Pallet Stacks
            { id: 'PALLET_SE', x: 6.2, y: -5.5, w: 1.3, h: 1.3, label: 'Pallet Stack', color: '#B45309', isZone: true },
            { id: 'PALLET_NW', x: -8.2, y: 5.5, w: 1.1, h: 1.1, label: 'Pallet', color: '#B45309' },
            { id: 'PALLET_SW', x: -3.7, y: -7.8, w: 1.2, h: 1.2, label: 'Pallet', color: '#B45309' }
        ];

        // ── Robot Palette (Industrial identifiable colors) ───────────────────
        this.robotColors = {
            'A': { primary: '#0284C7', light: '#E0F2FE', dark: '#0369A1' }, // Blue
            'B': { primary: '#16A34A', light: '#DCFCE7', dark: '#15803D' }, // Green
            'C': { primary: '#EA580C', light: '#FFEDD5', dark: '#C2410C' }  // Orange
        };

        // ── Viewport & Transform State ───────────────────────────────────────
        this.scale = 24.0; // pixels per metre default
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;
        this.panStartX = 0;
        this.panStartY = 0;

        // ── Visual Layer Toggles ─────────────────────────────────────────────
        this.showPaths = true;
        this.showLabels = true;
        this.showGrid = true;
        this.showLanes = true;
        this.showObstacles = true;

        // ── Live Telemetry & Interpolation State ──────────────────────────────
        this.liveRobots = {};
        this.visualRobots = {};
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
        let hasFitOnce = false;
        const ro = new ResizeObserver(() => {
            this.resize();
            if (!hasFitOnce && this.screenWidth > 10 && this.screenHeight > 10) {
                this.fitWarehouse();
                hasFitOnce = true;
            } else if (hasFitOnce) {
                this.fitWarehouse();
            }
        });

        if (this.canvas.parentElement) {
            ro.observe(this.canvas.parentElement);
        }

        window.addEventListener('resize', () => {
            this.resize();
            this.fitWarehouse();
        });
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.ctx.resetTransform?.();
        this.ctx.scale(dpr, dpr);
        this.screenWidth = rect.width;
        this.screenHeight = rect.height;
    }

    // ── Coordinate Conversions (World Metres <-> Screen Pixels) ──────────────

    worldToScreen(wx, wy) {
        const centerX = this.screenWidth / 2 + this.panX;
        const centerY = this.screenHeight / 2 + this.panY;
        const sx = centerX + wx * this.scale;
        const sy = centerY - wy * this.scale;
        return { x: sx, y: sy };
    }

    screenToWorld(sx, sy) {
        const centerX = this.screenWidth / 2 + this.panX;
        const centerY = this.screenHeight / 2 + this.panY;
        const wx = (sx - centerX) / this.scale;
        const wy = (centerY - sy) / this.scale;
        return { x: wx, y: wy };
    }

    // ── Viewport Control Functions ───────────────────────────────────────────

    zoomIn() {
        this.zoom(1.2);
    }

    zoomOut() {
        this.zoom(0.833);
    }

    zoom(factor, pivotX = this.screenWidth / 2, pivotY = this.screenHeight / 2) {
        const worldBefore = this.screenToWorld(pivotX, pivotY);
        this.scale = Math.min(70.0, Math.max(12.0, this.scale * factor));
        const worldAfter = this.screenToWorld(pivotX, pivotY);
        this.panX += (worldAfter.x - worldBefore.x) * this.scale;
        this.panY -= (worldAfter.y - worldBefore.y) * this.scale;
    }

    resetView() {
        this.panX = 0;
        this.panY = 0;
        this.fitWarehouse();
    }

    fitWarehouse() {
        if (!this.screenWidth || !this.screenHeight) return;
        const padding = 28;
        const availWidth = this.screenWidth - padding * 2;
        const availHeight = this.screenHeight - padding * 2;

        const scaleX = availWidth / (this.world.width + 1.6);
        const scaleY = availHeight / (this.world.height + 1.6);

        this.scale = Math.min(scaleX, scaleY);
        this.panX = 0;
        this.panY = 0;
    }

    centerOnRobot(robotId) {
        const r = this.visualRobots[robotId] || this.liveRobots[robotId];
        if (!r) return;
        this.panX = -r.x * this.scale;
        this.panY = r.y * this.scale;
    }

    // ── Mouse & Touch Event Handlers ─────────────────────────────────────────

    initEvents() {
        if (!this.canvas) return;

        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) {
                this.isPanning = true;
                this.panStartX = e.clientX - this.panX;
                this.panStartY = e.clientY - this.panY;
                this.canvas.style.cursor = 'grabbing';
            }
        });

        window.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            if (this.isPanning) {
                this.panX = e.clientX - this.panStartX;
                this.panY = e.clientY - this.panStartY;
            }

            if (mouseX >= 0 && mouseX <= rect.width && mouseY >= 0 && mouseY <= rect.height) {
                this.cursorWorldCoords = this.screenToWorld(mouseX, mouseY);
                const coordsBadge = document.getElementById('map-coords');
                if (coordsBadge) {
                    coordsBadge.textContent = `X: ${this.cursorWorldCoords.x.toFixed(2)}m  Y: ${this.cursorWorldCoords.y.toFixed(2)}m`;
                }
                this.checkHover(mouseX, mouseY);
            }
        });

        window.addEventListener('mouseup', () => {
            if (this.isPanning) {
                this.isPanning = false;
                this.canvas.style.cursor = 'crosshair';
            }
        });

        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            this.handleClick(mouseX, mouseY);
        });

        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
            this.zoom(zoomFactor, mouseX, mouseY);
        }, { passive: false });
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
                    lastTargetTime: now
                };
            } else {
                const vr = this.visualRobots[rid];
                vr.targetX = r.x;
                vr.targetY = r.y;
                vr.targetYaw = r.yaw !== undefined ? r.yaw : vr.targetYaw;
                vr.velocity = r.velocity || 0.0;
                vr.battery = r.battery !== undefined ? r.battery : 100.0;
                vr.status = r.status || 'IDLE';
                vr.task_id = r.task_id || null;
                vr.lastTargetTime = now;
            }

            if (!this.history[rid]) this.history[rid] = [];
            const hist = this.history[rid];
            const lastPt = hist[hist.length - 1];
            if (!lastPt || Math.hypot(lastPt.x - r.x, lastPt.y - r.y) > 0.15) {
                hist.push({ x: r.x, y: r.y });
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

    interpolateRobots(dt) {
        const easeFactor = Math.min(1.0, dt * 10.0);

        Object.values(this.visualRobots).forEach(r => {
            r.x += (r.targetX - r.x) * easeFactor;
            r.y += (r.targetY - r.y) * easeFactor;

            let deltaYaw = r.targetYaw - r.yaw;
            while (deltaYaw < -Math.PI) deltaYaw += Math.PI * 2;
            while (deltaYaw > Math.PI) deltaYaw -= Math.PI * 2;
            r.yaw += deltaYaw * easeFactor;
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

        // 7. Trajectory breadcrumb paths
        if (this.showPaths) {
            this.renderTrajectoryPaths(ctx);
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

        // Horizontal navigation lanes
        const hLanes = [
            8.5,    // Top bypass lane
            1.6,    // Central highway upper line
            -1.6,   // Central highway lower line
            -8.5    // Bottom bypass lane
        ];

        hLanes.forEach(y => {
            const sp1 = this.worldToScreen(-9.2, y);
            const sp2 = this.worldToScreen(9.2, y);
            ctx.beginPath();
            ctx.moveTo(sp1.x, sp1.y);
            ctx.lineTo(sp2.x, sp2.y);
            ctx.stroke();
        });

        // Vertical aisle navigation lanes
        const vLanes = [
            -7.5,   // West perimeter lane (near Pickup P)
            -4.3,   // Aisle between S1/S2 and S3/S4 (I1 corridor)
            -1.4,   // Between S3/S4 and S5/S6
            1.2,    // Between S5/S6 and S7/S8 (I2 corridor)
            4.8,    // Aisle next to S7/S8
            8.2     // East perimeter lane
        ];

        vLanes.forEach(x => {
            const sp1 = this.worldToScreen(x, 8.5);
            const sp2 = this.worldToScreen(x, -8.5);
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
            const size = 1.8 * this.scale;

            ctx.save();
            ctx.translate(sp.x, sp.y);

            // White concrete bay pad
            ctx.fillStyle = '#FFFFFF';
            ctx.fillRect(-size / 2, -size / 2, size, size);

            // Yellow/Black dashed hazard boundary
            ctx.strokeStyle = '#EAB308';
            ctx.lineWidth = 2.5;
            ctx.setLineDash([5, 4]);
            ctx.strokeRect(-size / 2, -size / 2, size, size);
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
                ctx.fillText('P', 0, 0);
            } else if (st.type === 'dropoff') {
                // Cyan/Blue Bold 'D'
                ctx.fillStyle = '#0284C7';
                ctx.font = `bold ${Math.round(size * 0.55)}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('D', 0, 0);
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

            // Top end caps (Dark metallic strip)
            ctx.fillStyle = '#1E293B';
            ctx.fillRect(-w / 2, -h / 2, w, 4);
            ctx.fillRect(-w / 2, h / 2 - 4, w, 4);

            // Shelf divider crossbars
            ctx.strokeStyle = '#EAB308';
            ctx.lineWidth = 1;
            const divCount = 4;
            for (let i = 1; i < divCount; i++) {
                const dy = -h / 2 + (h / divCount) * i;
                ctx.beginPath();
                ctx.moveTo(-w / 2, dy);
                ctx.lineTo(w / 2, dy);
                ctx.stroke();
            }

            // Bold Rack ID Banner (e.g. S1, S2, S4...)
            ctx.fillStyle = '#000000';
            ctx.font = `bold ${Math.max(12, Math.round(w * 0.4))}px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(rk.label, 0, 0);

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
                if (i === 0) ctx.moveTo(sp.x, sp.y);
                else ctx.lineTo(sp.x, sp.y);
            });
            ctx.stroke();
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
