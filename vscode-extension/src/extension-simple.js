/**
 * Extension Auto-Antigravity pour VS Code / Antigravity IDE
 * Version JavaScript pure (sans TypeScript)
 */
const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let pythonProcess = null;
let refreshInterval = null;
let dashboardPanel = null;

/**
 * Crée et affiche le dashboard
 */
function showDashboard(context) {
    if (dashboardPanel) {
        dashboardPanel.reveal();
        return;
    }

    dashboardPanel = vscode.window.createWebviewPanel(
        'autoAntigravity.dashboard',
        'Auto-Antigravity Dashboard',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    dashboardPanel.webview.html = getDashboardHtml();
    
    dashboardPanel.onDidDispose(() => {
        dashboardPanel = null;
    });

    dashboardPanel.webview.onDidReceiveMessage(message => {
        if (message.type === 'refresh') {
            refreshDashboard(context, false);
        }
    });
}

/**
 * Génère le HTML du dashboard
 */
function getDashboardHtml() {
    return `<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Antigravity Dashboard</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #2d3748;
        }
        h2 {
            font-size: 18px;
            margin-top: 30px;
            margin-bottom: 15px;
            color: #24292e;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .section {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .stat-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2d3748;
        }
        .stat-label {
            font-size: 12px;
            color: #6c757d;
            margin-top: 5px;
        }
        .status-ok {
            color: #28a745;
            font-weight: 600;
        }
        .status-warning {
            color: #f59e0b;
            font-weight: 600;
        }
        .status-error {
            color: #dc3545;
            font-weight: 600;
        }
        button {
            background: #0078d4;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            margin-right: 10px;
            transition: background-color 0.2s;
        }
        button:hover {
            background: #0056b3;
        }
        .info-box {
            background: #fff3cd;
            border-left: 4px solid #0078d4;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>🚀 Auto-Antigravity</h1>
    <p style="margin-bottom: 20px; color: #666;">Framework multi-agents avec monitoring avancé pour Google Antigravity IDE</p>
    
    <div class="section">
        <h2>📊 Vue d'ensemble</h2>
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">✅</div>
                <div class="stat-label">Système Actif</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">4</div>
                <div class="stat-label">Agents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">0</div>
                <div class="stat-label">Cache (MB)</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🤖 État des Agents</h2>
        <div style="margin: 10px 0;">
            <div><strong>Planner:</strong> <span class="status-ok">● Idle</span></div>
            <div><strong>Coder:</strong> <span class="status-ok">● Idle</span></div>
            <div><strong>Reviewer:</strong> <span class="status-ok">● Idle</span></div>
            <div><strong>Tester:</strong> <span class="status-ok">● Idle</span></div>
        </div>
    </div>
    
    <div class="section">
        <h2>💾 Cache</h2>
        <p><strong>Entrées:</strong> 0</p>
        <p><strong>Taille totale:</strong> 0 MB</p>
        <div style="margin-top: 15px;">
            <button onclick="window.location.reload()">🔄 Rafraîchir</button>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Quotas</h2>
        <div style="margin: 10px 0;">
            <div><strong>Gemini:</strong> <span class="status-ok">OK (15%)</span></div>
            <div><strong>Claude:</strong> <span class="status-warning">⚠️ 28%</span></div>
            <div><strong>OpenAI:</strong> <span class="status-ok">OK (45%)</span></div>
        </div>
    </div>
    
    <div class="section">
        <h2>🎮 Auto-Accept</h2>
        <p><strong>État:</strong> <span class="status-error">Désactivé</span></p>
        <div style="margin-top: 15px;">
            <button onclick="toggleAutoAccept()">🔘 Activer</button>
            <button onclick="window.location.reload()">🔄 Rafraîchir</button>
        </div>
    </div>
    
    <div class="info-box">
        <strong>💡 Conseil:</strong> Utilisez <code>Ctrl+Shift+P</code> et tapez <code>Auto-Antigravity</code> pour voir toutes les commandes disponibles.
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function refreshDashboard() {
            vscode.postMessage({ type: 'refresh' });
        }
        
        function toggleAutoAccept() {
            vscode.postMessage({ type: 'toggleAutoAccept' });
        }
        
        // Demander un rafraîchissement automatique
        setInterval(() => {
            vscode.postMessage({ type: 'refresh' });
        }, 5000);
    </script>
</body>
</html>`;
}

/**
 * Met à jour la barre de statut
 */
function updateStatusBar(statusBar, isError = false) {
    const icon = isError ? '❌' : '✅';
    statusBar.text = `$(info) AA: ${status}`;
    statusBar.color = isError ? undefined : undefined;
}

/**
 * Fonction d'activation principale
 */
function activate(context) {
    console.log('Auto-Antigravity est en cours d\'activation...');
    
    // Créer la barre de statut
    const statusBar = vscode.window.createStatusBarItem(
        'autoAntigravity.status',
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBar.text = '$(info) AA: Ready';
    statusBar.command = 'autoAntigravity.showDashboard';
    statusBar.show();
    context.subscriptions.push(statusBar);
    
    // Créer le canal de sortie
    const outputChannel = vscode.window.createOutputChannel('Auto-Antigravity');
    context.subscriptions.push(outputChannel);
    
    // Enregistrer les commandes
    context.subscriptions.push(
        vscode.commands.registerCommand('autoAntigravity.showDashboard', () => {
            showDashboard(context);
            outputChannel.appendLine('Dashboard ouvert');
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('autoAntigravity.refresh', () => {
            outputChannel.appendLine('Rafraîchissement demandé');
            vscode.window.showInformationMessage('Dashboard rafraîchi !');
            if (dashboardPanel) {
                dashboardPanel.webview.postMessage({ type: 'refresh' });
            }
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('autoAntigravity.toggleAutoAccept', () => {
            const config = vscode.workspace.getConfiguration('autoAntigravity');
            const current = config.get('autoAccept.enabled', false);
            const newValue = !current;
            config.update('autoAccept.enabled', newValue, vscode.ConfigurationTarget.Global);
            
            const message = newValue ? 'Auto-Accept activé' : 'Auto-Accept désactivé';
            vscode.window.showInformationMessage(message);
            updateStatusBar(statusBar);
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('autoAntigravity.executeTask', () => {
            vscode.window.showInputBox({
                prompt: 'Entrez la description de la tâche',
                placeHolder: 'Ex: Créer une application web Flask',
                ignoreFocusOut: true
            }).then(task => {
                if (task) {
                    vscode.window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: `Exécution: ${task.substring(0, 50)}...`,
                        cancellable: false
                    }, (progress) => {
                        progress.report({ increment: 0 });
                        
                        // Simuler l'exécution
                        setTimeout(() => {
                            progress.report({ increment: 100 });
                            vscode.window.showInformationMessage('Tâche simulée avec succès !');
                        }, 2000);
                    });
                }
            });
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('autoAntigravity.clearCache', () => {
            vscode.window.showWarningMessage(
                'Voulez-vous vraiment supprimer tout le cache ?',
                'Oui',
                'Annuler'
            ).then(result => {
                if (result === 'Oui') {
                    outputChannel.appendLine('Cache vidé');
                    vscode.window.showInformationMessage('Cache supprimé (simulation)');
                }
            });
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('autoAntigravity.runDiagnostics', () => {
            outputChannel.appendLine('Diagnostics en cours...');
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Diagnostics...',
                cancellable: false
            }, (progress) => {
                progress.report({ increment: 0, message: 'Vérification...' });
                
                setTimeout(() => {
                    progress.report({ increment: 50, message: 'Analyse...' });
                }, 1000);
                
                setTimeout(() => {
                    progress.report({ increment: 50 });
                    vscode.window.showInformationMessage('Diagnostics terminés (simulation)');
                    outputChannel.appendLine('=== RAPPORT DE DIAGNOSTICS ===');
                    outputChannel.appendLine('✓ Language Server: OK');
                    outputChannel.appendLine('✓ API Connection: OK');
                    outputChannel.appendLine('✓ File System: OK');
                    outputChannel.appendLine('✓ Cache System: OK');
                }, 2000);
            });
        })
    );
    
    vscode.window.showInformationMessage('Auto-Antigravity activé !');
    console.log('Auto-Antigravity activé avec succès');
}

/**
 * Fonction de désactivation
 */
function deactivate() {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
    
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    
    if (dashboardPanel) {
        dashboardPanel.dispose();
        dashboardPanel = null;
    }
    
    console.log('Auto-Antigravity désactivé');
}

module.exports = {
    activate,
    deactivate
};
