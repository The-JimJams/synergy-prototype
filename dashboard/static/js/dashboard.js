/**
 * SYNERGY Dashboard - Main Controller (Phase 5 - 11)
 * Manages periodic polling, DOM updates, event log filtering, and scenario selection.
 */

document.addEventListener('DOMContentLoaded', () => {
    const pollIntervalMs = window.POLL_INTERVAL || 500;
    
    // Components
    const mapRenderer = new WarehouseMapRenderer('warehouse-canvas');
    const metricsEvaluator = new MetricsEvaluator();

    // DOM Elements
    const backendDot = document.getElementById('backend-dot');
    const backendStatusText = document.getElementById('backend-status-text');
    const systemMode = document.getElementById('system-mode');
    const lastUpdateTime = document.getElementById('last-update-time');
    const scenarioSelector = document.getElementById('scenario-selector');
    const eventFeedList = document.getElementById('event-feed-list');
    const eventTypeFilter = document.getElementById('event-type-filter');
    const eventRobotFilter = document.getElementById('event-robot-filter');

    // Controls
    document.getElementById('toggle-paths')?.addEventListener('change', (e) => {
        mapRenderer.showPaths = e.target.checked;
    });
    document.getElementById('toggle-labels')?.addEventListener('change', (e) => {
        mapRenderer.showLabels = e.target.checked;
    });
    document.getElementById('toggle-grid')?.addEventListener('change', (e) => {
        mapRenderer.showGrid = e.target.checked;
    });

    // Scenario Switching
    scenarioSelector?.addEventListener('change', async (e) => {
        const selected = e.target.value;
        try {
            const res = await fetch('/api/simulator/scenario', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario: selected })
            });
            const data = await res.json();
            if (data.status === 'success') {
                console.log(`Switched to scenario ${selected}`);
            }
        } catch (err) {
            console.error('Failed to switch scenario:', err);
        }
    });

    // Event Filter Listeners
    eventTypeFilter?.addEventListener('change', () => fetchTelemetry());
    eventRobotFilter?.addEventListener('change', () => fetchTelemetry());

    // Main Polling Loop
    async function fetchTelemetry() {
        try {
            // Build events filter query
            const eventParams = new URLSearchParams();
            if (eventTypeFilter && eventTypeFilter.value) eventParams.append('event_type', eventTypeFilter.value);
            if (eventRobotFilter && eventRobotFilter.value) eventParams.append('robot_id', eventRobotFilter.value);

            const eventsUrl = '/api/events' + (eventParams.toString() ? '?' + eventParams.toString() : '');

            // Parallel API fetches for responsiveness
            const [stateRes, intentsRes, resRes, tasksRes, eventsRes, netRes, metricsRes, healthRes] = await Promise.all([
                fetch('/api/state'),
                fetch('/api/intents'),
                fetch('/api/reservations'),
                fetch('/api/tasks'),
                fetch(eventsUrl),
                fetch('/api/network'),
                fetch('/api/metrics'),
                fetch('/api/health')
            ]);

            if (!stateRes.ok) throw new Error('API fetch error');

            const stateData = await stateRes.json();
            const intentsData = await intentsRes.json();
            const resData = await resRes.json();
            const tasksData = await tasksRes.json();
            const eventsData = await eventsRes.json();
            const netData = await netRes.json();
            const metricsData = await metricsRes.json();
            const healthData = await healthRes.json();

            // Update Connection Status
            backendDot.className = 'indicator-dot online';
            backendStatusText.textContent = 'Connected';
            systemMode.textContent = (healthData.mode || 'MOCK').toUpperCase();

            // Update Last Time
            const now = new Date();
            lastUpdateTime.textContent = now.toLocaleTimeString();

            // Update Robots Cards & Map
            updateRobotCards(stateData.robots || {}, intentsData.intents || []);
            mapRenderer.render(stateData.robots || {}, resData.reservations || [], intentsData.intents || [], eventsData.events || []);

            // Update Lower Panels
            updateReservationsTable(resData.reservations || []);
            updateTasksTable(tasksData.tasks || []);
            updateNetworkPanel(netData);
            updateEventFeed(eventsData.events || []);
            metricsEvaluator.updateUI(metricsData);

        } catch (err) {
            backendDot.className = 'indicator-dot offline';
            backendStatusText.textContent = 'Disconnected';
            console.warn('Polling error:', err);
        }
    }

    function updateRobotCards(robots = {}, intents = []) {
        ['A', 'B', 'C'].forEach(rid => {
            const r = robots[rid];
            if (!r) return;

            // Status tag class mapping
            const statusTag = document.getElementById(`robot-${rid}-status`);
            if (statusTag) {
                statusTag.textContent = r.status || 'UNKNOWN';
                statusTag.className = `status-tag tag-${(r.status || 'idle').toLowerCase()}`;
            }

            // Position & Speed
            const posElem = document.getElementById(`robot-${rid}-pos`);
            if (posElem) posElem.textContent = `(${r.x.toFixed(1)}, ${r.y.toFixed(1)})`;

            const speedElem = document.getElementById(`robot-${rid}-speed`);
            if (speedElem) speedElem.textContent = `${(r.velocity || 0.0).toFixed(1)} m/s`;

            // Battery
            const batVal = document.getElementById(`robot-${rid}-bat-val`);
            const batBar = document.getElementById(`robot-${rid}-bat-bar`);
            if (batVal && batBar) {
                const bat = r.battery !== undefined ? r.battery : 100;
                batVal.textContent = `${Math.round(bat)}%`;
                batBar.style.width = `${bat}%`;
                batBar.style.backgroundColor = bat < 20 ? '#ef4444' : (bat < 50 ? '#f59e0b' : '#10b981');
            }

            // Task
            const taskElem = document.getElementById(`robot-${rid}-task`);
            if (taskElem) taskElem.textContent = r.task_id || 'None';

            // Intent
            const intent = intents.find(i => i.robot_id === rid);
            const intentElem = document.getElementById(`robot-${rid}-intent`);
            if (intentElem) {
                intentElem.textContent = intent ? `${intent.resource_id} (${intent.eta ? intent.eta + 's' : 'active'})` : 'None';
            }
        });
    }

    function updateReservationsTable(reservations = []) {
        const tbody = document.getElementById('reservations-tbody');
        if (!tbody) return;

        if (reservations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-row">No active reservations</td></tr>';
            return;
        }

        tbody.innerHTML = reservations.map(r => `
            <tr>
                <td><strong>${r.resource_id}</strong></td>
                <td>${r.robot_id ? `<span class="robot-avatar robot-${r.robot_id}">${r.robot_id}</span> Robot ${r.robot_id}` : '—'}</td>
                <td><span class="status-tag ${r.status === 'ACTIVE' ? 'tag-failed' : 'tag-idle'}">${r.status}</span></td>
                <td>${r.eta ? r.eta + 's' : '—'}</td>
            </tr>
        `).join('');
    }

    function updateTasksTable(tasks = []) {
        const tbody = document.getElementById('tasks-tbody');
        if (!tbody) return;

        if (tasks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-row">No active tasks</td></tr>';
            return;
        }

        tbody.innerHTML = tasks.map(t => `
            <tr>
                <td><strong>${t.task_id}</strong></td>
                <td>${t.pickup} → ${t.dropoff}</td>
                <td>${t.assigned_robot ? `Robot ${t.assigned_robot}` : 'Unassigned'}</td>
                <td><span class="status-tag ${t.status === 'COMPLETED' ? 'tag-normal' : (t.status === 'FAILED' ? 'tag-failed' : (t.status === 'WAITING' ? 'tag-waiting' : 'tag-moving'))}">${t.status}</span></td>
            </tr>
        `).join('');
    }

    function updateNetworkPanel(net = {}) {
        const statusTag = document.getElementById('network-status-tag');
        if (statusTag) {
            const status = net.status || 'NORMAL';
            statusTag.textContent = status;
            statusTag.className = `status-tag ${status === 'NORMAL' ? 'tag-normal' : 'tag-failed'}`;
        }

        const latElem = document.getElementById('net-latency');
        if (latElem) latElem.textContent = `${net.latency_ms !== null && net.latency_ms !== undefined ? net.latency_ms : 12} ms`;

        const lossElem = document.getElementById('net-loss');
        if (lossElem) lossElem.textContent = `${net.packet_loss_percent !== null && net.packet_loss_percent !== undefined ? net.packet_loss_percent : 0.0}%`;

        const peersElem = document.getElementById('net-peers');
        if (peersElem) peersElem.textContent = `${net.active_peers !== null && net.active_peers !== undefined ? net.active_peers : 3} / 3`;
    }

    function updateEventFeed(events = []) {
        if (!eventFeedList) return;

        if (events.length === 0) {
            eventFeedList.innerHTML = '<div class="empty-feed">No matching events recorded</div>';
            return;
        }

        eventFeedList.innerHTML = events.slice(0, 50).map(e => {
            const date = new Date(e.timestamp);
            const timeStr = isNaN(date.getTime()) ? '--:--:--' : date.toLocaleTimeString();

            return `
                <div class="event-item type-${e.event_type}">
                    <span class="event-time">${timeStr}</span>
                    <span class="event-msg">${e.message || (e.event_type + ' event')}</span>
                </div>
            `;
        }).join('');
    }

    // Start Polling
    fetchTelemetry();
    setInterval(fetchTelemetry, pollIntervalMs);
});
