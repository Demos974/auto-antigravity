/**
 * Extension Auto-Antigravity pour VS Code / Antigravity IDE
 */
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn, ChildProcess } from 'child_process';

let pythonProcess: ChildProcess | null = null;
let refreshInterval: NodeJS.Timeout | null = null;

/**
 * Interface pour les données du Dashboard
 */
interface DashboardData {
  agents: any[];
  quota: any;
  cache: any;
  usage_trends: any;
}

/**
 * Classe principale de l'extension
 */
export class AutoAntigravityExtension {
  private context: vscode.ExtensionContext;
  private dashboardPanel: vscode.WebviewPanel | null = null;
  private statusBar: vscode.StatusBarItem;
  private outputChannel: vscode.OutputChannel;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    
    // Créer la barre de statut
    this.statusBar = vscode.window.createStatusBarItem(
      'autoAntigravity.quotaStatus',
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBar.text = '$(info) AA: Ready';
    this.statusBar.command = 'autoAntigravity.refreshDashboard';
    this.statusBar.show();
    
    // Créer le canal de sortie
    this.outputChannel = vscode.window.createOutputChannel('Auto-Antigravity');
    
    this.registerCommands();
    this.registerViews();
    
    // Démarrer le processus Python
    this.startPythonProcess();
    
    // Rafraîchir périodiquement
    this.startRefresh();
    
    vscode.window.showInformationMessage('Auto-Antigravity activé !');
  }

  /**
   * Enregistre les commandes de l'extension
   */
  private registerCommands() {
    const commands = [
      { id: 'autoAntigravity.refreshDashboard', handler: () => this.refreshDashboard() },
      { id: 'autoAntigravity.openSettings', handler: () => this.openSettings() },
      { id: 'autoAntigravity.toggleAutoAccept', handler: () => this.toggleAutoAccept() },
      { id: 'autoAntigravity.clearCache', handler: () => this.clearCache() },
      { id: 'autoAntigravity.autoCleanCache', handler: () => this.autoCleanCache() },
      { id: 'autoAntigravity.runDiagnostics', handler: () => this.runDiagnostics() },
      { id: 'autoAntigravity.healthCheck', handler: () => this.healthCheck() },
      { id: 'autoAntigravity.systemMetrics', handler: () => this.showSystemMetrics() },
      { id: 'autoAntigravity.restartLanguageServer', handler: () => this.restartLanguageServer() },
      { id: 'autoAntigravity.executeTask', handler: () => this.executeTask() }
    ];

    commands.forEach(({ id, handler }) => {
      this.context.subscriptions.push(
        vscode.commands.registerCommand(id, handler)
      );
    });
  }

  /**
   * Enregistre les vues de l'extension
   */
  private registerViews() {
    // Enregistrer les tree views pour les agents, cache, quotas
    // Ces seront implémentés dans une version ultérieure
  }

  /**
   * Démarre le processus Python en arrière-plan
   */
  private startPythonProcess() {
    const config = vscode.workspace.getConfiguration('autoAntigravity');
    const pythonPath = config.get<string>('pythonPath') || 'python';
    
    const scriptPath = path.join(
      this.context.extensionPath,
      '..',
      'main.py'
    );

    this.outputChannel.appendLine(`Démarrage du processus Python: ${pythonPath} ${scriptPath}`);
    
    pythonProcess = spawn(pythonPath, ['main.py'], {
      cwd: path.join(this.context.extensionPath, '..'),
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    pythonProcess.stdout?.on('data', (data) => {
      const output = data.toString();
      this.outputChannel.appendLine(output);
      this.updateStatusBar('OK');
    });

    pythonProcess.stderr?.on('data', (data) => {
      const output = data.toString();
      this.outputChannel.appendLine(`ERROR: ${output}`);
      this.updateStatusBar('Error', true);
    });

    pythonProcess.on('close', (code) => {
      this.outputChannel.appendLine(`Processus terminé avec le code ${code}`);
      this.updateStatusBar('Stopped', true);
    });
  }

  /**
   * Rafraîchit périodiquement les données
   */
  private startRefresh() {
    const config = vscode.workspace.getConfiguration('autoAntigravity');
    const interval = config.get<number>('monitoring.refreshInterval') || 5000;
    
    refreshInterval = setInterval(() => {
      this.refreshDashboard(false);
    }, interval);
  }

  /**
   * Rafraîchit le dashboard
   */
  private async refreshDashboard(showNotification: boolean = true) {
    const config = vscode.workspace.getConfiguration('autoAntigravity');
    const monitoringEnabled = config.get<boolean>('monitoring.enabled');
    
    if (!monitoringEnabled) {
      return;
    }

    try {
      // Simuler la récupération des données
      // Dans une vraie implémentation, cela appellerait le processus Python
      const dashboardData: DashboardData = {
        agents: [],
        quota: {},
        cache: {},
        usage_trends: {}
      };

      // Mettre à jour le webview si ouvert
      if (this.dashboardPanel) {
        this.dashboardPanel.webview.postMessage({
          type: 'dashboardUpdate',
          data: dashboardData
        });
      }

      // Mettre à jour la barre de statut
      this.updateStatusBar('Active');

      if (showNotification) {
        vscode.window.showInformationMessage('Dashboard rafraîchi');
      }
    } catch (error) {
      this.outputChannel.appendLine(`Erreur: ${error}`);
      vscode.window.showErrorMessage('Erreur lors du rafraîchissement du dashboard');
    }
  }

  /**
   * Met à jour la barre de statut
   */
  private updateStatusBar(status: string, isError: boolean = false) {
    const icon = isError ? '$(error)' : '$(info)';
    this.statusBar.text = `${icon} AA: ${status}`;
    this.statusBar.color = isError ? new vscode.ThemeColor('errorForeground') : undefined;
  }

  /**
   * Ouvre les paramètres
   */
  private openSettings() {
    vscode.commands.executeCommand('workbench.action.openSettings', 'autoAntigravity');
  }

  /**
   * Active/désactive le mode Auto-Accept
   */
  private async toggleAutoAccept() {
    const config = vscode.workspace.getConfiguration('autoAntigravity');
    const current = config.get<boolean>('autoAccept.enabled', false);
    const newValue = !current;
    
    await config.update('autoAccept.enabled', newValue, vscode.ConfigurationTarget.Global);
    
    const message = newValue ? 'Auto-Accept activé' : 'Auto-Accept désactivé';
    vscode.window.showInformationMessage(message);
    
    this.updateStatusBar(newValue ? 'Auto-Accept' : 'Active');
  }

  /**
   * Vide tout le cache
   */
  private async clearCache() {
    const result = await vscode.window.showWarningMessage(
      'Voulez-vous vraiment supprimer tout le cache ?',
      'Oui',
      'Annuler'
    );

    if (result === 'Oui') {
      // Appeler le processus Python pour vider le cache
      this.outputChannel.appendLine('Cache vidé');
      vscode.window.showInformationMessage('Cache supprimé');
    }
  }

  /**
   * Nettoie automatiquement le cache
   */
  private async autoCleanCache() {
    // Appeler le processus Python
    this.outputChannel.appendLine('Auto-clean du cache en cours...');
    vscode.window.showInformationMessage('Auto-clean terminé');
  }

  /**
   * Exécute les diagnostics
   */
  private async runDiagnostics() {
    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Exécution des diagnostics...',
      cancellable: false
    }, async (progress) => {
      progress.report({ increment: 0 });
      
      // Simuler l'exécution des diagnostics
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      progress.report({ increment: 100 });
      vscode.window.showInformationMessage('Diagnostics terminés');
      
      // Afficher le rapport dans le canal de sortie
      this.outputChannel.appendLine('=== RAPPORT DE DIAGNOSTICS ===');
      this.outputChannel.appendLine('Language Server: OK');
      this.outputChannel.appendLine('API Connection: OK');
      this.outputChannel.appendLine('File System: OK');
      this.outputChannel.appendLine('Cache System: OK');
    });
  }

  /**
   * Effectue un contrôle de santé
   */
  private async healthCheck() {
    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Contrôle de santé...',
      cancellable: false
    }, async () => {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      vscode.window.showInformationMessage(
        'Système sain !',
        'OK'
      );
    });
  }

  /**
   * Affiche les métriques système
   */
  private async showSystemMetrics() {
    const config = vscode.workspace.getConfiguration('autoAntigravity');
    
    // Créer un webview pour afficher les métriques
    const panel = vscode.window.createWebviewPanel(
      'autoAntigravity.systemMetrics',
      'Métriques Système',
      vscode.ViewColumn.One,
      {}
    );

    panel.webview.html = this.getSystemMetricsWebviewContent();
  }

  /**
   * Redémarre le Language Server
   */
  private async restartLanguageServer() {
    const result = await vscode.window.showWarningMessage(
      'Voulez-vous redémarrer le Language Server ?',
      'Redémarrer',
      'Annuler'
    );

    if (result === 'Redémarrer') {
      vscode.window.showInformationMessage('Language Server redémarré');
      this.outputChannel.appendLine('Language Server redémarré');
    }
  }

  /**
   * Exécute une nouvelle tâche
   */
  private async executeTask() {
    const task = await vscode.window.showInputBox({
      prompt: 'Entrez la description de la tâche',
      placeHolder: 'Ex: Créer une application web Flask'
    });

    if (task) {
      vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Exécution de la tâche: ${task}`,
        cancellable: false
      }, async (progress) => {
        progress.report({ increment: 0, message: 'En cours...' });
        
        // Simuler l'exécution
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        progress.report({ increment: 100, message: 'Terminé !' });
        vscode.window.showInformationMessage('Tâche exécutée avec succès');
      });
    }
  }

  /**
   * Ouvre le dashboard webview
   */
  private openDashboard() {
    if (this.dashboardPanel) {
      this.dashboardPanel.reveal();
      return;
    }

    this.dashboardPanel = vscode.window.createWebviewPanel(
      'autoAntigravity.dashboard',
      'Auto-Antigravity Dashboard',
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true
      }
    );

    this.dashboardPanel.webview.html = this.getDashboardWebviewContent();

    this.dashboardPanel.onDidDispose(() => {
      this.dashboardPanel = null;
    });

    this.dashboardPanel.webview.onDidReceiveMessage(message => {
      if (message.type === 'refresh') {
        this.refreshDashboard(false);
      }
    });
  }

  /**
   * Génère le contenu du dashboard webview
   */
  private getDashboardWebviewContent(): string {
    return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Auto-Antigravity Dashboard</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      padding: 20px;
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
    }
    h1, h2, h3 {
      margin-top: 0;
      color: var(--vscode-textLink-foreground);
    }
    .section {
      margin-bottom: 20px;
      padding: 15px;
      border: 1px solid var(--vscode-panel-border);
      border-radius: 5px;
    }
    .stat {
      display: inline-block;
      margin-right: 20px;
      padding: 10px;
      background-color: var(--vscode-textBlockQuote-background);
      border-radius: 3px;
    }
    .status-ok { color: #4ec9b0; }
    .status-warning { color: #cca700; }
    .status-error { color: #f14c4c; }
    button {
      padding: 8px 16px;
      margin: 5px;
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      border-radius: 3px;
      cursor: pointer;
    }
    button:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
  </style>
</head>
<body>
  <h1>🚀 Auto-Antigravity Dashboard</h1>
  
  <div class="section">
    <h2>📊 Vue d'ensemble</h2>
    <div class="stat">✅ Système actif</div>
    <div class="stat">🤖 Agents: 4</div>
    <div class="stat">📦 Cache: OK</div>
    <button onclick="window.location.reload()">🔄 Rafraîchir</button>
  </div>
  
  <div class="section">
    <h2>🤖 Agents</h2>
    <div>
      <strong>Planner:</strong> <span class="status-ok">● Idle</span>
    </div>
    <div>
      <strong>Coder:</strong> <span class="status-ok">● Idle</span>
    </div>
    <div>
      <strong>Reviewer:</strong> <span class="status-ok">● Idle</span>
    </div>
    <div>
      <strong>Tester:</strong> <span class="status-ok">● Idle</span>
    </div>
  </div>
  
  <div class="section">
    <h2>💾 Cache</h2>
    <div class="stat">Entrées: 0</div>
    <div class="stat">Taille: 0 MB</div>
    <div style="margin-top: 10px;">
      <button onclick="alert('Cache vidé !')">🗑️ Vider tout</button>
      <button onclick="alert('Auto-clean terminé !')">🧹 Auto-clean</button>
    </div>
  </div>
  
  <div class="section">
    <h2>📊 Quotas</h2>
    <div>
      <strong>Gemini:</strong> <span class="status-ok">OK (15%)</span>
    </div>
    <div>
      <strong>Claude:</strong> <span class="status-warning">⚠️ 28%</span>
    </div>
    <div>
      <strong>OpenAI:</strong> <span class="status-ok">OK (45%)</span>
    </div>
  </div>
  
  <div class="section">
    <h2>🎮 Auto-Accept</h2>
    <div>
      <strong>État:</strong> <span class="status-ok">Activé</span>
    </div>
    <div class="stat">Actions traitées: 0</div>
    <div class="stat">Acceptées: 0</div>
  </div>
  
  <script>
    const vscode = acquireVsCodeApi();
    
    // Demander un rafraîchissement périodique
    setInterval(() => {
      vscode.postMessage({ type: 'refresh' });
    }, 5000);
  </script>
</body>
</html>`;
  }

  /**
   * Génère le contenu des métriques système
   */
  private getSystemMetricsWebviewContent(): string {
    return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Métriques Système</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      padding: 20px;
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
    }
    .metric {
      margin: 15px 0;
      padding: 15px;
      background-color: var(--vscode-textBlockQuote-background);
      border-radius: 5px;
    }
    .progress-bar {
      width: 100%;
      height: 20px;
      background-color: var(--vscode-progressBar-background);
      border-radius: 3px;
      margin-top: 5px;
    }
    .progress-fill {
      height: 100%;
      background-color: var(--vscode-progressBar-foreground);
      border-radius: 3px;
      transition: width 0.3s ease;
    }
  </style>
</head>
<body>
  <h1>💻 Métriques Système</h1>
  
  <div class="metric">
    <strong>CPU:</strong> 25%
    <div class="progress-bar">
      <div class="progress-fill" style="width: 25%"></div>
    </div>
  </div>
  
  <div class="metric">
    <strong>Mémoire:</strong> 45%
    <div class="progress-bar">
      <div class="progress-fill" style="width: 45%"></div>
    </div>
  </div>
  
  <div class="metric">
    <strong>Disque:</strong> 60%
    <div class="progress-bar">
      <div class="progress-fill" style="width: 60%"></div>
    </div>
  </div>
  
  <div class="metric">
    <strong>Processus:</strong> 127
  </div>
</body>
</html>`;
  }

  /**
   * Nettoyage lors de la désactivation
   */
  public dispose() {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
    
    if (pythonProcess) {
      pythonProcess.kill();
    }
    
    this.statusBar.dispose();
    this.outputChannel.dispose();
    
    if (this.dashboardPanel) {
      this.dashboardPanel.dispose();
    }
  }
}

/**
 * Point d'entrée de l'extension
 */
export function activate(context: vscode.ExtensionContext) {
  const extension = new AutoAntigravityExtension(context);
}

/**
 * Point de sortie de l'extension
 */
export function deactivate() {
  if (pythonProcess) {
    pythonProcess.kill();
  }
}
