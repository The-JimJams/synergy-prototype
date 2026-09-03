/**
 * Square-view regression check for the warehouse map.
 *
 * Paste into the browser console with the dashboard open, or run it through a
 * headless driver. It re-shapes the map panel into a range of aspect ratios and
 * asserts, for each one, that:
 *
 *   - the drawing surface is square
 *   - (-10,-10) (10,-10) (-10,10) (10,10) form a square on screen
 *   - one metre of X occupies exactly as many pixels as one metre of Y
 *   - all four corners of the world stay inside the viewport
 *   - repeated resize passes converge (no canvas-size feedback loop)
 *
 * Returns {pass, results}. Requires window.mapRenderer (set in dashboard.js).
 */
(async function checkSquareView() {
    const m = window.mapRenderer;
    if (!m) throw new Error('window.mapRenderer not found - is the dashboard loaded?');

    const panel = document.querySelector('.map-panel');
    const host = m.canvas.parentElement;
    const SHAPES = [[1600, 900], [1200, 700], [900, 900], [700, 1100], [500, 520], [1900, 600]];
    const EPS = 1e-6;
    const results = [];

    const settle = async () => {
        await new Promise(r => setTimeout(r, 120));
        m.resize();
        await new Promise(r => setTimeout(r, 60));
        m.resize();
    };

    for (const [w, h] of SHAPES) {
        panel.style.width = w + 'px';
        panel.style.height = h + 'px';
        await settle();

        // Stability: the canvas must not grow when resize() runs repeatedly.
        const sizes = [];
        for (let i = 0; i < 4; i++) { m.resize(); sizes.push(m.canvas.width); }
        const stable = new Set(sizes).size === 1;

        const cr = m.canvas.getBoundingClientRect();
        const P = (x, y) => m.worldToScreen(x, y);
        const BL = P(-10, -10), BR = P(10, -10), TL = P(-10, 10), TR = P(10, 10);
        const dist = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);
        const sides = [dist(TL, TR), dist(BL, BR), dist(BL, TL), dist(BR, TR)];
        const diags = [dist(BL, TR), dist(BR, TL)];

        const o = P(0, 0), ux = P(1, 0), uy = P(0, 1);
        const pxPerX = Math.hypot(ux.x - o.x, ux.y - o.y);
        const pxPerY = Math.hypot(uy.x - o.x, uy.y - o.y);

        const checks = {
            canvasSquare: Math.abs(cr.width - cr.height) < 0.5,
            sidesEqual: Math.max(...sides) - Math.min(...sides) < EPS,
            diagonalsEqual: Math.abs(diags[0] - diags[1]) < EPS,
            uniformScale: Math.abs(pxPerX - pxPerY) < 1e-9,
            cornersVisible: [BL, BR, TL, TR].every(
                p => p.x >= -0.5 && p.x <= cr.width + 0.5 && p.y >= -0.5 && p.y <= cr.height + 0.5
            ),
            noResizeFeedback: stable,
        };

        results.push({
            wrapper: [Math.round(host.getBoundingClientRect().width),
                      Math.round(host.getBoundingClientRect().height)],
            canvas: [Math.round(cr.width), Math.round(cr.height)],
            side: +sides[0].toFixed(3),
            pxPerMetre: +pxPerX.toFixed(4),
            checks,
            pass: Object.values(checks).every(Boolean),
        });
    }

    panel.style.width = '';
    panel.style.height = '';
    m.resize();

    const pass = results.every(r => r.pass);
    console.table(results.map(r => ({ wrapper: r.wrapper.join('x'), canvas: r.canvas.join('x'),
                                     side: r.side, pxPerMetre: r.pxPerMetre, pass: r.pass })));
    console.log(pass ? 'PASS: 20x20 world renders square at every tested aspect ratio.'
                     : 'FAIL: see the results array for which shape broke.');
    return { pass, results };
})();
