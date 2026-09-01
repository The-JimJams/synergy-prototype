/**
 * SYNERGY AMR Fleet Control Platform — Main Dashboard Controller
 * Connects UI controls, manages polling loop, updates tables, event feed, and inspector panel.
 */

document.addEventListener('DOMContentLoaded', () => {
    const pollIntervalMs = window.POLL_INTERVAL || 500;

    // ── Components ───────────────────────────────────────────────────────────
    const mapRenderer = new WarehouseMapRenderer('warehouse-canvas');
    const metricsEvaluator = new MetricsEvaluator();

    // ── Global State ─────────────────────────────────────────────────────────
    let currentRobots = {};
    let currentIntents = [];
    let currentReservations = [];
    let currentTasks = [];
    let currentEvents = [];
    let selectedRobotId = null;

    // ── DOM References ───────────────────────────────────────────────────────
    const backendDot = document.getElementById('backend-dot');
    const backendStatusText = document.getElementById('backend-status-text');
    const systemMode = document.getElementById('system-mode');
    const lastUpdateTime = document.getElementById('last-update-time');
    const scenarioSelector = document.getElementById('scenario-selector');
    const eventFeedList = document.getElementById('event-feed-list');
    const eventTypeFilter = document.getElementById('event-type-filter');
    const eventRobotFilter = document.getElementById('event-robot-filter');

    // ── Map Toolbar Controls ─────────────────────────────────────────────────
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => mapRenderer.zoomIn());
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => mapRenderer.zoomOut());
    document.getElementById('btn-fit-map')?.addEventListener('click', () => mapRenderer.fitWarehouse());
    document.getElementById('btn-reset-view')?.addEventListener('click', () => mapRenderer.resetView());
    document.getElementById('btn-center-robot')?.addEventListener('click', () => {
        if (selectedRobotId) mapRenderer.centerOnRobot(selectedRobotId);
    });

    // ── Layer Toggles ────────────────────────────────────────────────────────
    document.getElementById('toggle-paths')?.addEventListener('change', (e) => {
        mapRenderer.showPaths = e.target.checked;
    });
    document.getElementById('toggle-lanes')?.addEventListener('change', (e) => {
        mapRenderer.showLanes = e.target.checked;
    });
    document.getElementById('toggle-grid')?.addEventListener('change', (e) => {
        mapRenderer.showGrid = e.target.checked;
    });
    document.getElementById('toggle-labels')?.addEventListener('change', (e) => {
        mapRenderer.showLabels = e.target.checked;
    });
    document.getElementById('toggle-obstacles')?.addEventListener('change', (e) => {
        mapRenderer.showObstacles = e.target.checked;
    });

    // ── Map Selection Callback ───────────────────────────────────────────────
    mapRenderer.onSelectRobot = (robotId) => {
        selectedRobotId = robotId;
        updateInspector();
        highlightRobotCards();
    };

    // ── AMR Card Click Handlers (Right Column) ───────────────────────────────
    document.querySelectorAll('.amr-card').forEach(card => {
        card.addEventListener('click', () => {
            const rid = card.getAttribute('data-robot');
            if (rid) {
                selectedRobotId = rid;
                mapRenderer.selectRobot(rid);
                mapRenderer.centerOnRobot(rid);
                updateInspector();
                highlightRobotCards();
            }
        });
    });

    // ── Inspector Action Buttons ─────────────────────────────────────────────
    document.getElementById('btn-focus-selected')?.addEventListener('click', () => {
        if (selectedRobotId) {
            mapRenderer.centerOnRobot(selectedRobotId);
        }
    });

    document.getElementById('btn-deselect')?.addEventListener('click', () => {
        selectedRobotId = null;
        mapRenderer.selectRobot(null);
        updateInspector();
        highlightRobotCards();
    });

    // ── Scenario Switching ───────────────────────────────────────────────────
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
                console.log(`Switched to scenario: ${selected}`);
                fetchTelemetry();
            }
        } catch (err) {
            console.error('Failed to switch scenario:', err);
        }
    });

    // ── Event Filters ────────────────────────────────────────────────────────
    eventTypeFilter?.addEventListener('change', () => fetchTelemetry());
    eventRobotFilter?.addEventListener('change', () => fetchTelemetry());

    // ── Main Telemetry Polling Loop ──────────────────────────────────────────
    async function fetchTelemetry() {
        try {
            // Build events filter query
            const eventParams = new URLSearchParams();
            if (eventTypeFilter && eventTypeFilter.value) eventParams.append('event_type', eventTypeFilter.value);
            if (eventRobotFilter && eventRobotFilter.value) eventParams.append('robot_id', eventRobotFilter.value);

            const eventsUrl = '/api/events' + (eventParams.toString() ? '?' + eventParams.toString() : '');

            // Parallel fetches for responsive updates
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

            // Cache data
            currentRobots = stateData.robots || {};
            currentIntents = intentsData.intents || [];
            currentReservations = resData.reservations || [];
            currentTasks = tasksData.tasks || [];
            currentEvents = eventsData.events || [];

            // Update Connection Status
            backendDot.className = 'connection-dot online';
            backendStatusText.textContent = 'ONLINE';
            systemMode.textContent = (healthData.mode || 'MOCK').toUpperCase();

            // Update Telemetry Timestamp
            const now = new Date();
            lastUpdateTime.textContent = now.toLocaleTimeString();

            // Handover telemetry to 60fps Map Canvas
            mapRenderer.updateTelemetry(currentRobots, currentReservations, currentIntents, currentEvents, currentTasks);

            // Update UI Panels
            updateRobotCards();
            updateInspector();
            updateTasksTable();
            updateReservationsTable();
            updateNetworkDiagnostics(netData);
            updateEventFeed();
            updateFleetSummaryKPIs();
            metricsEvaluator.updateUI(metricsData);

        } catch (err) {
            backendDot.className = 'connection-dot offline';
            backendStatusText.textContent = 'RECONNECTING';
            console.warn('Telemetry polling error:', err);
        }
    }

    // ── UI Update Helpers ────────────────────────────────────────────────────

    function updateRobotCards() {
        ['A', 'B', 'C'].forEach(rid => {
            const r = currentRobots[rid];
            if (!r) return;

            // Status Tag
            const statusTag = document.getElementById(`robot-${rid}-status`);
            if (statusTag) {
                statusTag.textContent = r.status || 'IDLE';
                statusTag.className = `status-badge tag-${(r.status || 'idle').toLowerCase()}`;
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
                batBar.className = `battery-bar-fill ${bat < 15 ? 'crit' : (bat < 30 ? 'low' : '')}`;
            }
        });
    }

    function highlightRobotCards() {
        ['A', 'B', 'C'].forEach(rid => {
            const card = document.getElementById(`robot-card-${rid}`);
            if (card) {
                if (selectedRobotId === rid) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            }
        });
    }

    function updateInspector() {
        const titleElem = document.getElementById('inspect-robot-id');
        const poseElem = document.getElementById('inspect-pose');
        const speedElem = document.getElementById('inspect-speed');
        const taskElem = document.getElementById('inspect-task');
        const intentElem = document.getElementById('inspect-intent');

        if (!selectedRobotId || !currentRobots[selectedRobotId]) {
            if (titleElem) titleElem.textContent = 'None Selected (Click an AMR)';
            if (poseElem) poseElem.textContent = '—';
            if (speedElem) speedElem.textContent = '—';
            if (taskElem) taskElem.textContent = '—';
            if (intentElem) intentElem.textContent = '—';
            return;
        }

        const r = currentRobots[selectedRobotId];
        const yawDeg = Math.round(((r.yaw || 0.0) * 180 / Math.PI));

        if (titleElem) titleElem.textContent = `AMR ${r.robot_id} [${r.status || 'IDLE'}]`;
        if (poseElem) poseElem.textContent = `X: ${r.x.toFixed(2)}m, Y: ${r.y.toFixed(2)}m, θ: ${yawDeg}°`;
        if (speedElem) speedElem.textContent = `${(r.velocity || 0.0).toFixed(2)} m/s (Bat: ${Math.round(r.battery)}%)`;

        // Assigned Task
        const task = currentTasks.find(t => t.assigned_robot === selectedRobotId && t.status !== 'COMPLETED');
        if (taskElem) {
            taskElem.textContent = task ? `${task.task_id} (${task.pickup} → ${task.dropoff}) [${task.status}]` : (r.task_id ? `${r.task_id}` : 'None (Available)');
        }

        // Declared Intent
        const intent = currentIntents.find(i => i.robot_id === selectedRobotId);
        if (intentElem) {
            intentElem.textContent = intent ? `${intent.resource_id} (ETA: ${intent.eta ? intent.eta + 's' : 'immediate'})` : 'None (No contention)';
        }
    }

    function updateFleetSummaryKPIs() {
        const robotsArr = Object.values(currentRobots);
        const activeCount = robotsArr.filter(r => r.status === 'MOVING').length;
        const failedCount = robotsArr.filter(r => r.status === 'FAILED').length;
        const completedTasks = currentTasks.filter(t => t.status === 'COMPLETED').length;

        const totalElem = document.getElementById('summary-total-amrs');
        const activeElem = document.getElementById('summary-active-amrs');
        const tasksElem = document.getElementById('summary-completed-tasks');
        const fleetBadge = document.getElementById('fleet-health-badge');
        const kpiActive = document.getElementById('kpi-active-robots');

        if (totalElem) totalElem.textContent = robotsArr.length || 3;
        if (activeElem) activeElem.textContent = activeCount;
        if (tasksElem) tasksElem.textContent = completedTasks;
        if (kpiActive) kpiActive.textContent = `${robotsArr.length || 3} AMRs`;

        if (fleetBadge) {
            if (failedCount > 0) {
                fleetBadge.textContent = `${failedCount} AMR FAILED`;
                fleetBadge.className = 'status-badge tag-failed';
            } else {
                fleetBadge.textContent = `${robotsArr.length}/3 HEALTHY`;
                fleetBadge.className = 'status-badge tag-completed';
            }
        }
    }

    function updateTasksTable() {
        const tbody = document.getElementById('tasks-tbody');
        if (!tbody) return;

        if (currentTasks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-row">No active warehouse tasks</td></tr>';
            return;
        }

        tbody.innerHTML = currentTasks.map(t => {
            let statusClass = 'tag-idle';
            if (t.status === 'COMPLETED') statusClass = 'tag-completed';
            if (t.status === 'IN_PROGRESS' || t.status === 'ASSIGNED') statusClass = 'tag-moving';
            if (t.status === 'FAILED') statusClass = 'tag-failed';
            if (t.status === 'WAITING' || t.status === 'REASSIGNED') statusClass = 'tag-waiting';

            return `
                <tr>
                    <td><strong>${t.task_id}</strong></td>
                    <td class="mono">${t.pickup} &rarr; ${t.dropoff}</td>
                    <td>${t.assigned_robot ? `AMR ${t.assigned_robot}` : '—'}</td>
                    <td><span class="status-badge ${statusClass}">${t.status}</span></td>
                </tr>
            `;
        }).join('');
    }

    function updateReservationsTable() {
        const tbody = document.getElementById('reservations-tbody');
        if (!tbody) return;

        if (currentReservations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-row">No active intersection claims</td></tr>';
            return;
        }

        tbody.innerHTML = currentReservations.map(r => `
            <tr>
                <td><strong>${r.resource_id}</strong></td>
                <td>${r.robot_id ? `AMR ${r.robot_id}` : '—'}</td>
                <td><span class="status-badge ${r.status === 'ACTIVE' ? 'tag-moving' : 'tag-idle'}">${r.status}</span></td>
                <td class="mono">${r.eta ? r.eta + 's' : '—'}</td>
            </tr>
        `).join('');
    }

    function updateNetworkDiagnostics(net = {}) {
        const statusTag = document.getElementById('network-status-tag');
        if (statusTag) {
            const status = net.status || 'NORMAL';
            statusTag.textContent = status;
            statusTag.className = `status-badge ${status === 'NORMAL' ? 'tag-completed' : 'tag-waiting'}`;
        }

        const latElem = document.getElementById('net-latency');
        if (latElem) latElem.textContent = `${net.latency_ms !== null && net.latency_ms !== undefined ? net.latency_ms : 12} ms`;

        const lossElem = document.getElementById('net-loss');
        if (lossElem) lossElem.textContent = `${net.packet_loss_percent !== null && net.packet_loss_percent !== undefined ? net.packet_loss_percent : 0.0}%`;

        const peersElem = document.getElementById('net-peers');
        if (peersElem) peersElem.textContent = `${net.active_peers !== null && net.active_peers !== undefined ? net.active_peers : 3} / 3`;
    }

    function updateEventFeed() {
        if (!eventFeedList) return;

        if (currentEvents.length === 0) {
            eventFeedList.innerHTML = '<div class="empty-row">Awaiting telemetry events...</div>';
            return;
        }

        eventFeedList.innerHTML = currentEvents.slice(0, 50).map(e => {
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

    // ── Initial Start ────────────────────────────────────────────────────────
    fetchTelemetry();
    setInterval(fetchTelemetry, pollIntervalMs);
});
