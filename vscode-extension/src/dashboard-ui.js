/**
 * Contenu HTML/CSS/JS pour le dashboard webview
 */

function getDashboardHtml(data) {
    if (!data) data = {};
    console.log("Rendering Dashboard UI v1.7.7");
    const connected = data.connected || false;
    return `<!DOCTYPE html>
    <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
            <title>Auto-Antigravity Dashboard</title>
            <style>
                :root {
                    --bg-primary: var(--vscode-editor-background);
                    --bg-secondary: var(--vscode-sideBar-background);
                    --bg-card: var(--vscode-editorWidget-background);
                    --text-primary: var(--vscode-foreground);
                    --text-secondary: var(--vscode-descriptionForeground);
                    --border-color: var(--vscode-panel-border);
                    --accent-color: var(--vscode-button-background);
                    --success-color: #4ec9b0;
                    --warning-color: #cca700;
                    --error-color: #f14c4c;
                    --info-color: #3794ff;
                }
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { font-family: var(--vscode-font-family, sans-serif); font-size: 13px; color: var(--text-primary); background: var(--bg-primary); padding: 16px; line-height: 1.5; }
                .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
                .header h1 { font-size: 18px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
                .status-badge { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
                .status-connected { background: var(--success-color); color: #000; }
                .status-disconnected { background: var(--error-color); color: #fff; }
                .status-connecting { background: var(--warning-color); color: #000; }
                .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
                .card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; min-height: 150px; }
                .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
                .card-title { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; }
                .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
                .stat-item { text-align: center; padding: 12px 8px; background: var(--bg-secondary); border-radius: 6px; }
                .stat-value { font-size: 24px; font-weight: 700; color: var(--accent-color); }
                .stat-label { font-size: 11px; color: var(--text-secondary); margin-top: 4px; }
                .agent-list, .quota-list { display: flex; flex-direction: column; gap: 8px; }
                .agent-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: var(--bg-secondary); border-radius: 6px; }
                .agent-info { display: flex; align-items: center; gap: 10px; }
                .agent-dot { width: 10px; height: 10px; border-radius: 50%; }
                .agent-dot.idle { background: var(--success-color); }
                .agent-dot.working { background: var(--info-color); animation: pulse 1s infinite; }
                .agent-dot.error { background: var(--error-color); }
                @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
                .agent-name { font-weight: 500; }
                .agent-status { font-size: 11px; color: var(--text-secondary); }
                .quota-item { display: flex; flex-direction: column; gap: 6px; }
                .quota-header { display: flex; justify-content: space-between; font-size: 12px; }
                .quota-name { font-weight: 500; }
                .quota-value { color: var(--text-secondary); }
                .progress-bar { height: 6px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
                .progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s ease; }
                .progress-ok { background: var(--success-color); }
                .progress-warning { background: var(--warning-color); }
                .progress-critical { background: var(--error-color); }
                .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
                .metric-item { display: flex; flex-direction: column; align-items: center; padding: 16px; background: var(--bg-secondary); border-radius: 6px; }
                .metric-circle { width: 60px; height: 60px; border-radius: 50%; border: 4px solid var(--border-color); display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
                .metric-label { font-size: 11px; color: var(--text-secondary); }
                .actions-bar { display: flex; gap: 8px; margin-top: 20px; }
                button { padding: 8px 16px; background: var(--accent-color); color: var(--vscode-button-foreground); border: none; border-radius: 4px; font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: opacity 0.2s; }
                button:hover { opacity: 0.9; }
                button.secondary { background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); }
                .toggle-container { display: flex; align-items: center; gap: 8px; }
                .toggle { width: 40px; height: 22px; background: var(--border-color); border-radius: 11px; position: relative; cursor: pointer; transition: background 0.2s; }
                .toggle.active { background: var(--success-color); }
                .toggle-knob { width: 18px; height: 18px; background: white; border-radius: 50%; position: absolute; top: 2px; left: 2px; transition: left 0.2s; }
                .toggle.active .toggle-knob { left: 20px; }
                .footer { margin-top: 20px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 11px; color: var(--text-secondary); display: flex; justify-content: space-between; }
                .pies-container { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; padding: 8px 0; }
                .pie-item { display: flex; flex-direction: column; align-items: center; width: 100px; text-align: center; } /* Wider */
                .pie-chart { width: 60px; height: 60px; position: relative; margin-bottom: 8px; }
                .pie-chart svg { width: 100%; height: 100%; transform: rotate(-90deg); }
                .pie-circle-bg { fill: none; stroke: var(--bg-secondary); stroke-width: 8; }
                .pie-circle-fill { fill: none; stroke: var(--accent-color); stroke-width: 8; stroke-linecap: round; transition: stroke-dasharray 0.6s ease; }
                .pie-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 12px; font-weight: 700; }
                .pie-label { font-size: 11px; font-weight: 500; line-height: 1.2; color: var(--text-primary); width: 100%; margin-bottom: 2px; } /* Removed truncation */
                .pie-sublabel { font-size: 9px; color: var(--text-secondary); opacity: 0.8; word-break: break-all; }
                
                /* Dynamic Colors will be set via inline style or classes helper */
                .color-good { stroke: var(--success-color); }
                .color-warn { stroke: var(--warning-color); }
                .color-crit { stroke: var(--error-color); }
                
                /* User Card Styles (Refined) */
                .user-card { display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 6px; margin-bottom: 20px; background: var(--bg-secondary); border-left: 3px solid var(--accent-color); }
                .user-icon { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: var(--text-primary); opacity: 0.8; background: rgba(255,255,255,0.05); border-radius: 50%; }
                .user-details { display: flex; flex-direction: column; gap: 3px; }
                .user-plan { font-weight: 600; font-size: 13px; color: var(--text-primary); display: flex; align-items: center; gap: 6px; }
                .user-email { font-size: 11px; color: var(--text-secondary); opacity: 0.7; }
                .tag-pro { background: var(--accent-color); color: white; padding: 1px 6px; border-radius: 3px; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; }
                
                /* Task List Styles */
                .task-list { display: flex; flex-direction: column; gap: 8px; max-height: 200px; overflow-y: auto; }
                .task-item { display: flex; align-items: center; justify-content: space-between; padding: 10px; background: var(--bg-secondary); border-radius: 6px; border-left: 3px solid transparent; }
                .task-item.status-in_progress { border-left-color: var(--info-color); background: rgba(55, 148, 255, 0.1); }
                .task-item.status-completed { border-left-color: var(--success-color); opacity: 0.7; }
                .task-item.status-failed { border-left-color: var(--error-color); }
                .task-info { display: flex; flex-direction: column; gap: 4px; overflow: hidden; }
                .task-desc { font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
                .task-meta { display: flex; align-items: center; gap: 8px; font-size: 10px; color: var(--text-secondary); }
                .task-agent { background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-size: 9px; }
                .task-icon { font-size: 14px; min-width: 20px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Auto-Antigravity</h1>
                <span id="status-badge" class="status-badge status-connecting">Connexion...</span>
            </div>

            <div class="dashboard-grid">
                <!-- Vue d'ensemble -->
                <div class="card">
                    <div class="card-header"><span class="card-title">📊 Vue d'ensemble</span></div>
                    <div class="stats-grid">
                        <div class="stat-item"><div class="stat-value" id="agents-count">0</div><div class="stat-label">Agents</div></div>
                        <div class="stat-item"><div class="stat-value" id="cache-entries">0</div><div class="stat-label">Cache</div></div>
                        <div class="stat-item"><div class="stat-value" id="tasks-count">0</div><div class="stat-label">Tâches</div></div>
                    </div>
                </div>

                <!-- Agents -->
                <div class="card">
                    <div class="card-header"><span class="card-title">🤖 Agents</span></div>
                    <div class="agent-list" id="agents-list">
                        <div class="agent-item"><div class="agent-info"><span class="agent-dot idle"></span><span class="agent-name">Chargement...</span></div></div>
                    </div>
                </div>

                <!-- Tâches en cours (New) -->
                <div class="card" id="card-tasks" style="display:none;">
                    <div class="card-header"><span class="card-title">📋 Tâches en cours <span id="project-name" style="font-weight:400; opacity:0.7; margin-left:8px;"></span></span></div>
                    <div class="task-list" id="task-list">
                        <!-- Items dynamiques -->
                    </div>
                </div>

                <!-- Quotas -->
                <div class="card">
                    <div class="card-header"><span class="card-title">📈 Quotas & Limites</span></div>
                    <div class="pies-container" id="pies-container">
                        <div style="padding:10px; text-align:center; color:var(--text-secondary);">Chargement...</div>
                    </div>
                    <div class="quota-list" id="quota-list" style="margin-top:16px; border-top:1px solid var(--border-color); padding-top:12px;"></div>
                </div>

                <!-- Métriques Système -->
                <div class="card">
                    <div class="card-header"><span class="card-title">💻 Système</span></div>
                    <div class="metrics-grid">
                        <div class="metric-item"><div class="metric-circle" id="cpu-circle">--%</div><div class="metric-label">CPU</div></div>
                        <div class="metric-item"><div class="metric-circle" id="memory-circle">--%</div><div class="metric-label">RAM</div></div>
                        <div class="metric-item"><div class="metric-circle" id="gpu-circle">--%</div><div class="metric-label">GPU Core</div></div>
                        <div class="metric-item"><div class="metric-circle" id="disk-circle">--%</div><div class="metric-label">VRAM</div></div>
                    </div>
                </div>

                <!-- Auto-Accept -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">🎮 Auto-Accept</span>
                        <div class="toggle-container">
                            <div class="toggle" id="auto-accept-toggle" onclick="toggleAutoAccept()"><div class="toggle-knob"></div></div>
                        </div>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item"><div class="stat-value" id="aa-processed">0</div><div class="stat-label">Traités</div></div>
                        <div class="stat-item"><div class="stat-value" id="aa-accepted">0</div><div class="stat-label">Acceptés</div></div>
                        <div class="stat-item"><div class="stat-value" id="aa-rejected">0</div><div class="stat-label">Rejetés</div></div>
                    </div>
                </div>

                <!-- Cache -->
                <div class="card">
                    <div class="card-header"><span class="card-title">💾 Cache</span></div>
                    <div class="stats-grid">
                        <div class="stat-item"><div class="stat-value" id="cache-count">0</div><div class="stat-label">Entrées</div></div>
                        <div class="stat-item"><div class="stat-value" id="cache-size">0</div><div class="stat-label">MB</div></div>
                    </div>
                    <div class="actions-bar" style="margin-top: 12px;">
                        <button class="secondary" onclick="clearCache()">🗑️ Vider</button>
                        <button class="secondary" onclick="autoCleanCache()">🧹 Auto-clean</button>
                    </div>
                </div>
            </div>

            <div class="actions-bar">
                <button onclick="executeTask()">▶️ Nouvelle Tâche</button>
                <button onclick="refresh()">🔄 Rafraîchir</button>
                <button class="secondary" onclick="runDiagnostics()">🔍 Diagnostics</button>
            </div>

            <div class="footer">
                <span>Auto-Antigravity v1.8.9</span>
                <span id="last-update">Dernière mise à jour: --</span>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                function refresh() { vscode.postMessage({ type: 'refresh' }); }
                function toggleAutoAccept() { vscode.postMessage({ type: 'toggleAutoAccept' }); }
                function executeTask() { vscode.postMessage({ type: 'executeTask' }); }
                function clearCache() { vscode.postMessage({ type: 'clearCache' }); }
                function autoCleanCache() { vscode.postMessage({ type: 'autoCleanCache' }); }
                function runDiagnostics() { vscode.postMessage({ type: 'runDiagnostics' }); }

                window.addEventListener('message', function(event) {
                    const message = event.data;
                    if (message.type === 'update') {
                        updateDashboard(message.data);
                    }
                });

                function createPieHtml(percentage, label, sublabel, colorClass) {
                    const radius = 22;
                    const circumference = 2 * Math.PI * radius;
                    const offset = circumference - (percentage / 100) * circumference;
                    const safePercent = isNaN(percentage) ? 0 : Math.round(percentage);

                    return \`
                    <div class="pie-item">
                        <div class="pie-chart">
                            <svg viewBox="0 0 60 60">
                                <circle class="pie-circle-bg" cx="30" cy="30" r="\${radius}"></circle>
                                <circle class="pie-circle-fill \${colorClass}" cx="30" cy="30" r="\${radius}"
                                    style="stroke-dasharray: \${circumference} \${circumference}; stroke-dashoffset: \${offset}"></circle>
                            </svg>
                            <div class="pie-text">\${safePercent}%</div>
                        </div>
                        <div class="pie-label">\${label}</div>
                        <div class="pie-sublabel">\${sublabel}</div>
                    </div>\`;
                }

                function updateDashboard(data) {
                    // Status
                    const statusBadge = document.getElementById('status-badge');
                    if (data.connected) {
                        statusBadge.textContent = 'Connecté';
                        statusBadge.className = 'status-badge status-connected';
                    } else {
                        statusBadge.textContent = 'Déconnecté';
                        statusBadge.className = 'status-badge status-disconnected';
                    }

                    // Overview
                    document.getElementById('agents-count').textContent = (data.agents && data.agents.total_agents) || 0;
                    if (data.cache) {
                        document.getElementById('cache-entries').textContent = data.cache.total_entries || 0;
                        document.getElementById('cache-count').textContent = data.cache.total_entries || 0;
                        document.getElementById('cache-size').textContent = (data.cache.total_size_mb || 0).toFixed(1);
                    }
                    if (data.agents) {
                        document.getElementById('tasks-count').textContent = data.tasks_count || 0;
                    }

                    // Agents
                    if (data.agents && data.agents.agents) {
                        const agentsList = document.getElementById('agents-list');
                        agentsList.innerHTML = data.agents.agents.map(function(agent) {
                            return '<div class="agent-item"><div class="agent-info"><span class="agent-dot ' + 
                                (agent.status || 'idle').toLowerCase() + '"></span>' +
                                '<span class="agent-name">' + agent.name + '</span></div>' +
                                '<span class="agent-status">' + agent.status + '</span></div>';
                        }).join('');
                    }

                    // Quotas
                    const piesContainer = document.getElementById('pies-container');
                    const quotaList = document.getElementById('quota-list');
                    const ext = data.quota && data.quota.external;
                    let htmlPies = '';
                    let htmlList = '';

                    if (ext && ext.source === 'LanguageServer') {
                        // Helper for Fuel Gauge logic (Remaining %)
                        // Helper for Fuel Gauge logic (Remaining %)
                        const renderGauge = (label, used, total, usagePct, forceSubLabel) => {
                             const remainingPct = Math.max(0, 100 - usagePct);
                             let color = 'color-good';
                             if (remainingPct < 20) color = 'color-crit';
                             else if (remainingPct < 50) color = 'color-warn';
                             
                             let subLabel = '';
                             if (forceSubLabel) {
                                 subLabel = forceSubLabel;
                             } else if (total > 0) {
                                 const left = total - used;
                                 subLabel = left >= 1000 ? (left/1000).toFixed(1) + 'k restants' : left + ' restants';
                             } else {
                                 subLabel = remainingPct.toFixed(0) + '% Restant';
                             }
                             
                             htmlPies += createPieHtml(remainingPct, label, subLabel, color);
                        };

                        if (ext.prompt_credits) {
                            renderGauge('Prompts', ext.prompt_credits.available, ext.prompt_credits.total, ext.prompt_credits.percentage || 0);
                        }
                        if (ext.flow_credits) {
                            renderGauge('Flow', ext.flow_credits.available, ext.flow_credits.total, ext.flow_credits.percentage || 0);
                        }
                        if (ext.models && ext.models.length > 0) {
                            ext.models.forEach(function(m) {
                                const usage = m.usage_percentage || 0;
                                const remaining = Math.max(0, 100 - usage);
                                
                                let subLabel = remaining.toFixed(0) + '% Restant';
                                
                                // Show Reset Time if available
                                if (m.reset_time) {
                                    try {
                                        const resetDate = new Date(m.reset_time);
                                        const now = new Date();
                                        // If reset is today, show time, else show date
                                        if (resetDate.toDateString() === now.toDateString()) {
                                            subLabel += ' (Reset ' + resetDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) + ')';
                                        } else {
                                            subLabel += ' (Reset ' + resetDate.toLocaleDateString() + ')';
                                        }
                                    } catch(e) { /* ignore parse error */ }
                                }
                                
                                renderGauge(m.name, 0, 0, usage, subLabel);
                            });
                        }
                        if (ext.user && ext.user.tier) {
                            const email = ext.user.email || 'Unknown';
                            // Logic to avoid "ProPRO"
                            const tierLower = ext.user.tier.toLowerCase();
                            const hasProInName = tierLower.includes('pro'); // If name has "Pro", we consider it tagged
                            // Only add tag if it's a paid tier BUT "Pro" isn't already in the name to avoid redundancy
                            // Actually, if it's "Google AI Pro", the "PRO" tag is redundant.
                            // If it's "Basic", showing no tag is fine.
                            // If it's "Something Else", and isPro is true (via 'paid'), maybe show tag.
                            const isPaid = tierLower.includes('paid') || hasProInName;
                            const showTag = isPaid && !hasProInName; // Avoid duplication
                            
                            htmlList += '<div class="user-card">' +
                                '<div class="user-icon">' +
                                    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>' +
                                '</div>' +
                                '<div class="user-details">' +
                                    '<div class="user-plan">' + ext.user.tier + (showTag ? '<span class="tag-pro">PRO</span>' : '') + '</div>' +
                                    '<div class="user-email">' + email + '</div>' +
                                '</div>' +
                            '</div>';
                        }
                    } else if (data.quota && data.quota.external && Object.keys(data.quota.external).length > 0) {
                         const ext = data.quota.external;
                         if (ext.Status || ext.Info) {
                             const statusColor = ext.Status && ext.Status.includes('En Ligne') ? 'var(--success-color)' : 'var(--warning-color)';
                             htmlPies = '<div style="width:100%; text-align:center; padding:20px;">' +
                                '<div style="font-size:24px; margin-bottom:8px;">' + (ext.Status || '⚠️') + '</div>' +
                                '<div style="color:var(--text-secondary); font-size:12px;">' + (ext.Info || '') + '</div>' +
                                (ext.Detail ? '<div style="color:var(--error-color); font-size:10px; margin-top:4px;">' + ext.Detail + '</div>' : '') +
                            '</div>';
                         } else {
                             for (const key in ext) {
                                 let v = ext[key];
                                 if (typeof v === 'object') v = JSON.stringify(v);
                                 if (String(v).length > 40) v = String(v).substring(0, 40) + '...';
                                 htmlList += '<div class="quota-item"><div class="quota-header"><span class="quota-name">' + key + '</span><span class="quota-value">' + v + '</span></div></div>';
                             }
                         }
                    } else {
                        htmlPies = '<div style="width:100%; text-align:center; opacity:0.5; font-size:11px; padding:10px;">Aucun quota disponible</div>';
                    }
                    piesContainer.innerHTML = htmlPies;
                    quotaList.innerHTML = htmlList;

                    // Metrics
                    if (data.metrics) {
                        document.getElementById('cpu-circle').textContent = (data.metrics.cpu_percent || 0).toFixed(0) + '%';
                        document.getElementById('memory-circle').textContent = (data.metrics.memory_percent || 0).toFixed(0) + '%';
                        document.getElementById('gpu-circle').textContent = data.metrics.gpu_percent != null ? data.metrics.gpu_percent.toFixed(0) + '%' : 'N/A';
                        // Remplacement Disque -> VRAM
                        document.getElementById('disk-circle').textContent = data.metrics.gpu_memory_percent != null ? data.metrics.gpu_memory_percent.toFixed(0) + '%' : 'N/A';
                    }

                    // Tasks Rendering
                    const taskList = document.getElementById('task-list');
                    const taskCard = document.getElementById('card-tasks');
                    const projectNameObj = document.getElementById('project-name');
                    
                    if (data.tasks && data.tasks.length > 0) {
                        taskCard.style.display = 'block';
                        if (data.project_name) projectNameObj.textContent = '(' + data.project_name + ')';
                        
                        taskList.innerHTML = data.tasks.map(function(t) {
                            let icon = '⏳';
                            let statusClass = 'status-' + t.status.toLowerCase();
                            
                            if (t.status === 'in_progress') icon = '🏃';
                            else if (t.status === 'completed') icon = '✅';
                            else if (t.status === 'failed') icon = '❌';
                            
                            return '<div class="task-item ' + statusClass + '">' +
                                '<div class="task-info">' +
                                    '<div class="task-desc" title="' + t.description + '">' + t.description + '</div>' +
                                    '<div class="task-meta">' +
                                        (t.agent ? '<span class="task-agent">' + t.agent + '</span>' : '') +
                                        '<span>' + t.status + '</span>' +
                                    '</div>' +
                                '</div>' +
                                '<div class="task-icon">' + icon + '</div>' +
                            '</div>';
                        }).join('');
                    } else {
                        taskCard.style.display = 'none'; // Hide if no active tasks
                    }

                    if (data.auto_accept) {
                        const toggle = document.getElementById('auto-accept-toggle');
                        if (data.auto_accept.enabled) toggle.classList.add('active');
                        else toggle.classList.remove('active');
                        const stats = data.auto_accept.statistics || {};
                        document.getElementById('aa-processed').textContent = stats.total_processed || 0;
                        document.getElementById('aa-accepted').textContent = stats.auto_accepted || 0;
                        document.getElementById('aa-rejected').textContent = stats.rejected || 0;
                    }
                    document.getElementById('last-update').textContent = 'Mise à jour: ' + new Date().toLocaleTimeString();
                }

                refresh();
                setInterval(refresh, 5000);
            </script>
        </body>
    </html>`;
}

module.exports = { getDashboardHtml: getDashboardHtml };
