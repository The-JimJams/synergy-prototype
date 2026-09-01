/**
 * SYNERGY Dashboard - Warehouse Canvas Renderer (Phase 6 & 7)
 * HTML Canvas map renderer with world-to-screen coordinate transformation.
 */

class WarehouseMapRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        // Configurable warehouse dimensions (metres)
        this.worldWidth = 12.0;
        this.worldHeight = 8.0;

        // Named stations & intersections (matching config.py layout)
        this.stations = {
            'S1': { x: 2.0, y: 1.5, label: 'Station 1 (Pickup)' },
            'S2': { x: 2.0, y: 6.5, label: 'Station 2 (Dropoff)' },
            'S3': { x: 10.0, y: 1.5, label: 'Station 3 (Pickup)' },
            'S4': { x: 10.0, y: 6.5, label: 'Station 4 (Dropoff)' }
        };

        this.intersections = {
            'I1': { x: 5.0, y: 4.0, label: 'Intersection 1' },
            'I2': { x: 8.0, y: 4.0, label: 'Intersection 2' }
        };

        // Robot color palette
        this.colors = {
            'A': '#ef4444',
            'B': '#3b82f6',
            'C': '#10b981'
        };

        // Settings toggles
        this.showGrid = true;
        this.showPaths = true;
        this.showLabels = true;

        // Position history for rendering trajectory lines
        this.history = { 'A': [], 'B': [], 'C': [] };
        this.maxHistoryLength = 20;

        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = Math.max(380, rect.height);
    }

    // World (metres) to Screen (pixels) transformation
    worldToScreen(x, y) {
        const padding = 30;
        const width = this.canvas.width - padding * 2;
        const height = this.canvas.height - padding * 2;

        const scaleX = width / this.worldWidth;
        const scaleY = height / this.worldHeight;

        const screenX = padding + x * scaleX;
        // Invert Y axis for standard screen coordinates (0,0 at bottom-left in world)
        const screenY = this.canvas.height - (padding + y * scaleY);

        return { x: screenX, y: screenY, scale: (scaleX + scaleY) / 2 };
    }

    render(robots = {}, reservations = [], intents = []) {
        if (!this.ctx) return;

        // Clear canvas
        this.ctx.fillStyle = '#070a12';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        if (this.showGrid) this.drawGrid();

        // Draw warehouse racks and aisles layout
        this.drawWarehouseLayout();

        // Draw intersections & active reservations
        this.drawIntersections(reservations);

        // Draw stations
        this.drawStations();

        // Update position history for paths
        Object.values(robots).forEach(r => {
            if (!this.history[r.robot_id]) this.history[r.robot_id] = [];
            this.history[r.robot_id].push({ x: r.x, y: r.y });
            if (this.history[r.robot_id].length > this.maxHistoryLength) {
                this.history[r.robot_id].shift();
            }
        });

        // Draw robot paths/trails
        if (this.showPaths) this.drawPaths();

        // Draw robot intents
        this.drawIntents(intents, robots);

        // Draw robot markers
        Object.values(robots).forEach(r => this.drawRobot(r));
    }

    drawGrid() {
        this.ctx.strokeStyle = '#141c2e';
        this.ctx.lineWidth = 1;

        for (let x = 0; x <= this.worldWidth; x += 1.0) {
            const p1 = this.worldToScreen(x, 0);
            const p2 = this.worldToScreen(x, this.worldHeight);
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.stroke();
        }

        for (let y = 0; y <= this.worldHeight; y += 1.0) {
            const p1 = this.worldToScreen(0, y);
            const p2 = this.worldToScreen(this.worldWidth, y);
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.stroke();
        }
    }

    drawWarehouseLayout() {
        // Draw outer warehouse boundary wall
        const p1 = this.worldToScreen(0, 0);
        const p2 = this.worldToScreen(this.worldWidth, this.worldHeight);

        this.ctx.strokeStyle = '#233152';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(p1.x, p2.y, p2.x - p1.x, p1.y - p2.y);

        // Draw storage rack blocks (schematic representation)
        const racks = [
            { x: 3.5, y: 1.0, w: 1.0, h: 2.0 },
            { x: 3.5, y: 5.0, w: 1.0, h: 2.0 },
            { x: 7.5, y: 1.0, w: 1.0, h: 2.0 },
            { x: 7.5, y: 5.0, w: 1.0, h: 2.0 }
        ];

        this.ctx.fillStyle = '#162238';
        this.ctx.strokeStyle = '#233152';
        this.ctx.lineWidth = 1;

        racks.forEach(r => {
            const topL = this.worldToScreen(r.x, r.y + r.h);
            const botR = this.worldToScreen(r.x + r.w, r.y);
            this.ctx.fillRect(topL.x, topL.y, botR.x - topL.x, botR.y - topL.y);
            this.ctx.strokeRect(topL.x, topL.y, botR.x - topL.x, botR.y - topL.y);

            if (this.showLabels) {
                this.ctx.fillStyle = '#475569';
                this.ctx.font = '10px sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.fillText('RACK', (topL.x + botR.x) / 2, (topL.y + botR.y) / 2);
                this.ctx.fillStyle = '#162238';
            }
        });
    }

    drawStations() {
        Object.entries(this.stations).forEach(([id, st]) => {
            const pos = this.worldToScreen(st.x, st.y);

            this.ctx.fillStyle = '#1e293b';
            this.ctx.strokeStyle = '#38bdf8';
            this.ctx.lineWidth = 2;

            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, 14, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.stroke();

            this.ctx.fillStyle = '#38bdf8';
            this.ctx.font = 'bold 11px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(id, pos.x, pos.y);

            if (this.showLabels) {
                this.ctx.fillStyle = '#94a3b8';
                this.ctx.font = '10px sans-serif';
                this.ctx.fillText(st.label, pos.x, pos.y + 22);
            }
        });
    }

    drawIntersections(reservations = []) {
        Object.entries(this.intersections).forEach(([id, inter]) => {
            const pos = this.worldToScreen(inter.x, inter.y);
            const res = reservations.find(r => r.resource_id === id);
            const isReserved = res && res.status === 'ACTIVE';

            this.ctx.fillStyle = isReserved ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.1)';
            this.ctx.strokeStyle = isReserved ? '#ef4444' : '#f59e0b';
            this.ctx.lineWidth = 2;

            // Draw intersection zone box
            const size = 30;
            this.ctx.fillRect(pos.x - size/2, pos.y - size/2, size, size);
            this.ctx.strokeRect(pos.x - size/2, pos.y - size/2, size, size);

            this.ctx.fillStyle = isReserved ? '#ef4444' : '#f59e0b';
            this.ctx.font = 'bold 11px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(id, pos.x, pos.y);

            if (isReserved && this.showLabels) {
                this.ctx.fillStyle = '#f87171';
                this.ctx.font = 'bold 10px sans-serif';
                this.ctx.fillText(`HELD: ${res.robot_id}`, pos.x, pos.y - 20);
            }
        });
    }

    drawPaths() {
        Object.entries(this.history).forEach(([rid, pts]) => {
            if (pts.length < 2) return;
            const color = this.colors[rid] || '#ffffff';

            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.globalAlpha = 0.35;

            this.ctx.beginPath();
            const start = this.worldToScreen(pts[0].x, pts[0].y);
            this.ctx.moveTo(start.x, start.y);

            for (let i = 1; i < pts.length; i++) {
                const p = this.worldToScreen(pts[i].x, pts[i].y);
                this.ctx.lineTo(p.x, p.y);
            }
            this.ctx.stroke();
            this.ctx.globalAlpha = 1.0;
        });
    }

    drawIntents(intents = [], robots = {}) {
        intents.forEach(intent => {
            const robot = robots[intent.robot_id];
            const inter = this.intersections[intent.resource_id];
            if (!robot || !inter) return;

            const rPos = this.worldToScreen(robot.x, robot.y);
            const iPos = this.worldToScreen(inter.x, inter.y);

            this.ctx.strokeStyle = this.colors[intent.robot_id] || '#60a5fa';
            this.ctx.lineWidth = 1.5;
            this.ctx.setLineDash([4, 4]);

            this.ctx.beginPath();
            this.ctx.moveTo(rPos.x, rPos.y);
            this.ctx.lineTo(iPos.x, iPos.y);
            this.ctx.stroke();

            this.ctx.setLineDash([]); // Reset
        });
    }

    drawRobot(r) {
        const pos = this.worldToScreen(r.x, r.y);
        const color = this.colors[r.robot_id] || '#ffffff';
        const radius = 16;

        // Draw glow if moving/active
        if (r.status === 'MOVING') {
            this.ctx.fillStyle = color;
            this.ctx.globalAlpha = 0.15;
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, radius * 1.6, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.globalAlpha = 1.0;
        }

        // Main robot circle body
        this.ctx.fillStyle = '#1e293b';
        this.ctx.strokeStyle = r.status === 'FAILED' ? '#ef4444' : color;
        this.ctx.lineWidth = 3;

        this.ctx.beginPath();
        this.ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.stroke();

        // Draw orientation heading arrow
        const yaw = r.yaw || 0.0;
        const arrowLen = radius * 0.8;
        const arrowX = pos.x + Math.cos(yaw) * arrowLen;
        const arrowY = pos.y - Math.sin(yaw) * arrowLen;

        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(pos.x, pos.y);
        this.ctx.lineTo(arrowX, arrowY);
        this.ctx.stroke();

        // Robot ID text label
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = 'bold 12px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(r.robot_id, pos.x, pos.y);

        // Status text underneath
        if (this.showLabels) {
            this.ctx.fillStyle = r.status === 'FAILED' ? '#f87171' : '#94a3b8';
            this.ctx.font = '10px sans-serif';
            this.ctx.fillText(r.status, pos.x, pos.y + radius + 12);
        }
    }
}
