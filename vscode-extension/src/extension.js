/**
 * Extension Auto-Antigravity v1.0 pour Antigravity IDE
 * Framework multi-agents avec monitoring avancé
 */
const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');

const { ApiClient } = require('./api-client');
const { AgentsTreeProvider, CacheTreeProvider, ActionsTreeProvider } = require('./tree-providers');
const dashboardUI = require('./dashboard-ui');

// Instances globales
let apiClient = null;
let serverProcess = null;
let refreshInterval = null;
let statusBarItem = null;
let outputChannel = null;

// Providers
let agentsProvider = null;
let cacheProvider = null;
let actionsProvider = null;

/**
 * Provider pour la vue Dashboard dans la barre d'activité
 */
function DashboardViewProvider(context, apiClient) {
    this._context = context;
    this._apiClient = apiClient;
    this._view = null;
}

DashboardViewProvider.prototype.resolveWebviewView = function (webviewView, context, token) {
    this._view = webviewView;

    webviewView.webview.options = {
        enableScripts: true,
        localResourceRoots: [this._context.extensionUri]
    };

    webviewView.webview.html = dashboardUI.getDashboardHtml();

    // Gérer les messages du webview
    webviewView.webview.onDidReceiveMessage(async (message) => {
        switch (message.type) {
            case 'refresh':
                await this.updateDashboard();
                break;
            case 'toggleAutoAccept':
                await this.toggleAutoAccept();
                break;
            case 'executeTask':
                vscode.commands.executeCommand('autoAntigravity.executeTask');
                break;
            case 'clearCache':
                await this.clearCache();
                break;
            case 'autoCleanCache':
                await this.autoCleanCache();
                break;
            case 'runDiagnostics':
                vscode.commands.executeCommand('autoAntigravity.runDiagnostics');
                break;
        }
    });

    // Mise à jour initiale
    this.updateDashboard();
};

DashboardViewProvider.prototype.updateDashboard = async function () {
    if (!this._view) return;

    try {
        const connected = await this._apiClient.checkConnection();

        let data = { connected };

        if (connected) {
            const results = await Promise.all([
                this._apiClient.getDashboard().catch(() => null),
                this._apiClient.getSystemMetrics().catch(() => null),
                this._apiClient.getAutoAcceptStatus().catch(() => null)
            ]);
            const dashboard = results[0];
            const metrics = results[1];
            const autoAccept = results[2];

            if (dashboard) {
                data.agents = dashboard.agents;
                data.quota = dashboard.quota;
                data.cache = dashboard.cache;
            }
            if (metrics) {
                data.metrics = metrics;
            }
            if (autoAccept) {
                data.auto_accept = autoAccept;
            }
        }

        this._view.webview.postMessage({ type: 'update', data });
    } catch (error) {
        if (outputChannel) outputChannel.appendLine(`Dashboard update error: ${error.message}`);
        this._view.webview.postMessage({
            type: 'update',
            data: { connected: false }
        });
    }
};

DashboardViewProvider.prototype.toggleAutoAccept = async function () {
    try {
        const result = await this._apiClient.toggleAutoAccept();
        vscode.window.showInformationMessage(result.message);
        await this.updateDashboard();
    } catch (error) {
        vscode.window.showErrorMessage(`Erreur: ${error.message}`);
    }
};

DashboardViewProvider.prototype.clearCache = async function () {
    const confirm = await vscode.window.showWarningMessage(
        'Voulez-vous vraiment vider tout le cache ?',
        'Oui', 'Annuler'
    );

    if (confirm === 'Oui') {
        try {
            const result = await this._apiClient.clearCache();
            vscode.window.showInformationMessage(result.message);
            await this.updateDashboard();
            if (cacheProvider) cacheProvider.updateData();
        } catch (error) {
            vscode.window.showErrorMessage(`Erreur: ${error.message}`);
        }
    }
};

DashboardViewProvider.prototype.autoCleanCache = async function () {
    try {
        const result = await this._apiClient.autoCleanCache();
        vscode.window.showInformationMessage(result.message);
        await this.updateDashboard();
        if (cacheProvider) cacheProvider.updateData();
    } catch (error) {
        vscode.window.showErrorMessage(`Erreur: ${error.message}`);
    }
};

/**
 * Démarre le serveur Python en arrière-plan
 */
function startServer(context) {
    const fs = require('fs');

    // Chercher le serveur dans plusieurs emplacements possibles
    const possiblePaths = [
        // 1. Chemin absolu vers le projet ThatIDE
        'c:\\ThatIDE\\server',
        // 2. Workspace actuel
        ...(vscode.workspace.workspaceFolders || []).map(f => path.join(f.uri.fsPath, 'server')),
        // 3. Parent de l'extension (pour dev)
        path.join(context.extensionPath, '..', 'server'),
    ];

    let serverDir = null;
    for (const dir of possiblePaths) {
        const scriptPath = path.join(dir, 'run.py');
        if (fs.existsSync(scriptPath)) {
            serverDir = dir;
            break;
        }
    }

    if (!serverDir) {
        outputChannel.appendLine('⚠️ Serveur non trouvé dans les chemins suivants:');
        possiblePaths.forEach(p => outputChannel.appendLine(`   - ${p}`));
        outputChannel.appendLine('⚠️ Mode démo activé (pas de backend)');
        return null;
    }

    outputChannel.appendLine(`✅ Serveur trouvé dans: ${serverDir}`);

    // Récupérer la configuration
    const config = vscode.workspace.getConfiguration('autoAntigravity');
    const apiKey = config.get('apiKey');

    // Exécuter depuis le dossier server/ pour que les imports fonctionnent
    serverProcess = spawn('python', ['run.py'], {
        cwd: serverDir,
        env: {
            ...process.env,
            PYTHONUNBUFFERED: '1',
            PYTHONIOENCODING: 'utf-8',
            ANTIGRAVITY_API_KEY: apiKey || process.env.ANTIGRAVITY_API_KEY
        }
    });

    if (serverProcess.stdout) {
        serverProcess.stdout.on('data', (data) => {
            outputChannel.appendLine(`[Server] ${data.toString().trim()}`);
        });
    }

    if (serverProcess.stderr) {
        serverProcess.stderr.on('data', (data) => {
            outputChannel.appendLine(`[Server ERROR] ${data.toString().trim()}`);
        });
    }

    serverProcess.on('close', (code) => {
        outputChannel.appendLine(`[Server] Processus terminé avec code ${code}`);
        serverProcess = null;
    });

    serverProcess.on('error', (error) => {
        outputChannel.appendLine(`[Server ERROR] ${error.message}`);
        serverProcess = null;
    });

    return serverProcess;
}

/**
 * Met à jour la barre de statut
 */
async function updateStatusBar() {
    if (!statusBarItem) return;

    const connected = await apiClient.checkConnection();

    if (connected) {
        try {
            // Récupérer Status et Quota en parallèle
            const results = await Promise.all([
                apiClient.getAutoAcceptStatus(),
                apiClient.getQuotaSummary()
            ]);
            const autoAccept = results[0];
            const quotaData = results[1];

            const aaIcon = autoAccept.enabled ? '$(check-all)' : '$(circle-slash)';
            const aaText = autoAccept.enabled ? 'Auto' : 'Manual';

            // Calculer l'affichage du quota (Local ou Externe)
            let usage = 0;
            if (quotaData.summary && typeof quotaData.summary.max_percentage === 'number') {
                usage = quotaData.summary.max_percentage;
            }

            const quotaText = `${usage.toFixed(0)}%`;

            // Format: [Graph] Quota: 15% | [Icon] AA: Auto
            statusBarItem.text = `$(graph) Quota: ${quotaText} | ${aaIcon} AA: ${aaText}`;

            // Couleurs d'alerte pour le quota
            statusBarItem.backgroundColor = undefined;
            if (usage > 80) statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            if (usage > 95) statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');

        } catch (e) {
            console.error('Erreur MAJ status bar:', e);
            // Fallback en cas d'erreur API partielle
            statusBarItem.text = '$(info) AA: Ready';
        }
    } else {
        statusBarItem.text = '$(warning) AA: Offline';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }
}

/**
 * Rafraîchit toutes les données
 */
async function refreshAll() {
    await updateStatusBar();
    if (agentsProvider) agentsProvider.updateData();
    if (cacheProvider) cacheProvider.updateData();
    if (actionsProvider) actionsProvider.updateData();
}

/**
 * Fonction d'activation principale
 */
function activate(context) {
    try {
        const extensionData = vscode.extensions.getExtension('auto-antigravity.auto-antigravity');
        const version = extensionData ? extensionData.packageJSON.version : 'Unknown';

        console.log(`Auto-Antigravity v${version} en cours d'activation...`);
        console.log("Using Dashboard UI from:", './dashboard-ui.js');

        // Créer le canal de sortie
        outputChannel = vscode.window.createOutputChannel('Auto-Antigravity');
        context.subscriptions.push(outputChannel);
        outputChannel.show(true); // Force visibility without stealing focus
        outputChannel.appendLine(`🚀 Auto-Antigravity v${version} démarrage...`);

        // Créer le client API
        apiClient = new ApiClient();

        // Créer la barre de statut
        statusBarItem = vscode.window.createStatusBarItem(
            'autoAntigravity.status',
            vscode.StatusBarAlignment.Right,
            100
        );
        statusBarItem.text = '$(loading~spin) AA: Starting...';
        statusBarItem.command = 'autoAntigravity.showDashboard';
        statusBarItem.tooltip = 'Auto-Antigravity - Cliquez pour ouvrir le dashboard';
        statusBarItem.show();
        context.subscriptions.push(statusBarItem);

        // Démarrer le serveur Python
        startServer(context);

        // Attendre que le serveur démarre
        setTimeout(async () => {
            await updateStatusBar();
        }, 3000);

        // Créer les providers
        agentsProvider = new AgentsTreeProvider(apiClient);
        cacheProvider = new CacheTreeProvider(apiClient);
        actionsProvider = new ActionsTreeProvider(apiClient);

        // Enregistrer les TreeViews
        context.subscriptions.push(
            vscode.window.registerTreeDataProvider('autoAntigravity.agentsView', agentsProvider),
            vscode.window.registerTreeDataProvider('autoAntigravity.cacheView', cacheProvider),
            vscode.window.registerTreeDataProvider('autoAntigravity.actionsView', actionsProvider)
        );

        // Enregistrer le WebviewViewProvider pour le dashboard
        const dashboardProvider = new DashboardViewProvider(context, apiClient);
        context.subscriptions.push(
            vscode.window.registerWebviewViewProvider(
                'autoAntigravity.dashboard',
                dashboardProvider
            )
        );

        // Enregistrer les commandes
        const commands = [
            {
                id: 'autoAntigravity.showDashboard',
                handler: () => {
                    vscode.commands.executeCommand('autoAntigravity.dashboard.focus');
                }
            },
            {
                id: 'autoAntigravity.refresh',
                handler: async () => {
                    await refreshAll();
                    vscode.window.showInformationMessage('Dashboard rafraîchi !');
                }
            },
            {
                id: 'autoAntigravity.toggleAutoAccept',
                handler: async () => {
                    try {
                        const result = await apiClient.toggleAutoAccept();
                        vscode.window.showInformationMessage(result.message);
                        await updateStatusBar();
                        if (actionsProvider) actionsProvider.updateData();
                    } catch (error) {
                        vscode.window.showErrorMessage(`Erreur: ${error.message}`);
                    }
                }
            },
            {
                id: 'autoAntigravity.executeTask',
                handler: async () => {
                    const task = await vscode.window.showInputBox({
                        prompt: 'Entrez la description de la tâche',
                        placeHolder: 'Ex: Créer une application web Flask',
                        ignoreFocusOut: true
                    });

                    if (task) {
                        try {
                            const result = await apiClient.executeTask(task);
                            vscode.window.showInformationMessage(`Tâche démarrée: ${result.task_id}`);
                            if (agentsProvider) agentsProvider.updateData();
                        } catch (error) {
                            vscode.window.showErrorMessage(`Erreur: ${error.message}`);
                        }
                    }
                }
            },
            {
                id: 'autoAntigravity.clearCache',
                handler: async () => {
                    const confirm = await vscode.window.showWarningMessage(
                        'Voulez-vous vraiment vider tout le cache ?',
                        'Oui', 'Annuler'
                    );

                    if (confirm === 'Oui') {
                        try {
                            const result = await apiClient.clearCache();
                            vscode.window.showInformationMessage(result.message);
                            if (cacheProvider) cacheProvider.updateData();
                        } catch (error) {
                            vscode.window.showErrorMessage(`Erreur: ${error.message}`);
                        }
                    }
                }
            },
            {
                id: 'autoAntigravity.runDiagnostics',
                handler: async () => {
                    await vscode.window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: 'Diagnostics en cours...',
                        cancellable: false
                    }, async (progress) => {
                        progress.report({ increment: 0 });

                        try {
                            const result = await apiClient.runDiagnostics();
                            progress.report({ increment: 100 });

                            outputChannel.appendLine('=== RAPPORT DE DIAGNOSTICS ===');
                            outputChannel.appendLine(JSON.stringify(result, null, 2));
                            outputChannel.show();

                            vscode.window.showInformationMessage('Diagnostics terminés - voir Output');
                        } catch (error) {
                            vscode.window.showErrorMessage(`Erreur: ${error.message}`);
                        }
                    });
                }
            },
            {
                id: 'autoAntigravity.startServer',
                handler: () => {
                    if (serverProcess) {
                        vscode.window.showWarningMessage('Le serveur est déjà en cours d\'exécution');
                        return;
                    }
                    startServer(context);
                    vscode.window.showInformationMessage('Serveur démarré');
                }
            },
            {
                id: 'autoAntigravity.stopServer',
                handler: () => {
                    if (serverProcess) {
                        serverProcess.kill();
                        serverProcess = null;
                        vscode.window.showInformationMessage('Serveur arrêté');
                        updateStatusBar();
                    } else {
                        vscode.window.showWarningMessage('Le serveur n\'est pas en cours d\'exécution');
                    }
                }
            },
            {
                id: 'autoAntigravity.showOutput',
                handler: () => {
                    outputChannel.show();
                }
            },
            {
                id: 'autoAntigravity.restartAgent',
                handler: async (item) => {
                    if (item && item.agentData) {
                        try {
                            const result = await apiClient.restartAgent(item.agentData.name);
                            vscode.window.showInformationMessage(result.message);
                            if (agentsProvider) agentsProvider.updateData();
                        } catch (error) {
                            vscode.window.showErrorMessage(`Erreur: ${error.message}`);
                        }
                    }
                }
            }
        ];

        commands.forEach(({ id, handler }) => {
            context.subscriptions.push(
                vscode.commands.registerCommand(id, handler)
            );
        });

        // Rafraîchissement périodique
        refreshInterval = setInterval(() => {
            refreshAll();
        }, 10000);

        // Initial refresh after a delay
        setTimeout(() => {
            refreshAll();
        }, 5000);

        outputChannel.appendLine(`✅ Auto-Antigravity v${version} activé avec succès`);
        vscode.window.showInformationMessage(`Auto-Antigravity v${version} activé !`);
    } catch (e) {
        console.error('CRITICAL ERROR in activate:', e);
        vscode.window.showErrorMessage(`Auto-Antigravity Activation Error: ${e.message}`);
    }
}

/**
 * Fonction de désactivation
 */
function deactivate() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }

    if (serverProcess) {
        serverProcess.kill();
        serverProcess = null;
    }

    console.log('Auto-Antigravity désactivé');
}

module.exports = {
    activate,
    deactivate
};
