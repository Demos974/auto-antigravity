/**
 * TreeDataProviders pour les vues Agents et Cache
 */
const vscode = require('vscode');

/**
 * Provider pour la vue des Agents
 */
function AgentsTreeProvider(apiClient) {
    this.apiClient = apiClient;
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    this.agents = [];
}

AgentsTreeProvider.prototype.refresh = function () {
    this._onDidChangeTreeData.fire();
};

AgentsTreeProvider.prototype.updateData = async function () {
    try {
        const data = await this.apiClient.getAgents();
        this.agents = data.agents || [];
        this.refresh();
    } catch (error) {
        console.error('Failed to fetch agents:', error);
        this.agents = [];
        this.refresh();
    }
};

AgentsTreeProvider.prototype.getTreeItem = function (element) {
    return element;
};

AgentsTreeProvider.prototype.getChildren = async function (element) {
    if (element) {
        // Enfants d'un agent (détails)
        return [
            new AgentDetailItem('Tâches complétées', element.tasksCompleted.toString(), 'number'),
            new AgentDetailItem('Tâches échouées', element.tasksFailed.toString(), 'error'),
            new AgentDetailItem('Taux de succès', `${element.successRate}%`, 'percentage'),
        ];
    }

    // Liste des agents
    const self = this;
    return this.agents.map(function (agent) {
        return new AgentTreeItem(agent);
    });
};

/**
 * Item représentant un agent dans l'arbre
 */
function AgentTreeItem(agent) {
    // Appel du constructeur parent (simulation)
    vscode.TreeItem.call(this, agent.name, vscode.TreeItemCollapsibleState.Collapsed);

    this.agentData = agent;
    this.tasksCompleted = agent.tasks_completed || 0;
    this.tasksFailed = agent.tasks_failed || 0;
    this.successRate = agent.success_rate || 0;

    // Icône selon le statut
    const statusIcon = this.getStatusIcon(agent.status);
    this.iconPath = new vscode.ThemeIcon(statusIcon.icon, statusIcon.color);

    // Description
    this.description = agent.status;

    // Tooltip
    this.tooltip = new vscode.MarkdownString(
        `**${agent.name}** (${agent.type})\n\n` +
        `- Statut: ${agent.status}\n` +
        `- Tâches: ${this.tasksCompleted} complétées, ${this.tasksFailed} échouées\n` +
        `- Taux de succès: ${this.successRate}%`
    );

    // Context value pour les menus
    this.contextValue = 'agent';
}

// Héritage
AgentTreeItem.prototype = Object.create(vscode.TreeItem.prototype);
AgentTreeItem.prototype.constructor = AgentTreeItem;

AgentTreeItem.prototype.getStatusIcon = function (status) {
    switch (status.toLowerCase()) {
        case 'working':
            return { icon: 'sync~spin', color: new vscode.ThemeColor('charts.blue') };
        case 'error':
            return { icon: 'error', color: new vscode.ThemeColor('charts.red') };
        case 'idle':
        default:
            return { icon: 'check', color: new vscode.ThemeColor('charts.green') };
    }
};

/**
 * Item de détail d'un agent
 */
function AgentDetailItem(label, value, type) {
    vscode.TreeItem.call(this, `${label}: ${value}`, vscode.TreeItemCollapsibleState.None);

    switch (type) {
        case 'error':
            this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('charts.orange'));
            break;
        case 'percentage':
            this.iconPath = new vscode.ThemeIcon('graph');
            break;
        default:
            this.iconPath = new vscode.ThemeIcon('primitive-dot');
    }
}
AgentDetailItem.prototype = Object.create(vscode.TreeItem.prototype);
AgentDetailItem.prototype.constructor = AgentDetailItem;

/**
 * Provider pour la vue du Cache
 */
function CacheTreeProvider(apiClient) {
    this.apiClient = apiClient;
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    this.cacheData = { entries: [], total_size_mb: 0, total_entries: 0 };
}

CacheTreeProvider.prototype.refresh = function () {
    this._onDidChangeTreeData.fire();
};

CacheTreeProvider.prototype.updateData = async function () {
    try {
        const data = await this.apiClient.getCache();
        this.cacheData = data;
        this.refresh();
    } catch (error) {
        console.error('Failed to fetch cache:', error);
        this.cacheData = { entries: [], total_size_mb: 0, total_entries: 0 };
        this.refresh();
    }
};

CacheTreeProvider.prototype.getTreeItem = function (element) {
    return element;
};

CacheTreeProvider.prototype.getChildren = async function (element) {
    if (element) {
        return [];
    }

    const items = [];

    // Info résumé
    items.push(new CacheSummaryItem(
        `Total: ${this.cacheData.total_entries || 0} entrées`,
        `${(this.cacheData.total_size_mb || 0).toFixed(2)} MB`
    ));

    // Entrées de cache groupées par agent
    const entries = this.cacheData.entries || [];
    const groupedByAgent = {};

    for (const entry of entries) {
        const agentType = entry.agent_type || 'unknown';
        if (!groupedByAgent[agentType]) {
            groupedByAgent[agentType] = [];
        }
        groupedByAgent[agentType].push(entry);
    }

    for (const [agentType, agentEntries] of Object.entries(groupedByAgent)) {
        items.push(new CacheAgentGroupItem(agentType, agentEntries));
    }

    return items;
};

/**
 * Item résumé du cache
 */
function CacheSummaryItem(label, description) {
    vscode.TreeItem.call(this, label, vscode.TreeItemCollapsibleState.None);
    this.description = description;
    this.iconPath = new vscode.ThemeIcon('database');
    this.contextValue = 'cacheSummary';
}
CacheSummaryItem.prototype = Object.create(vscode.TreeItem.prototype);
CacheSummaryItem.prototype.constructor = CacheSummaryItem;

/**
 * Groupe d'entrées de cache par agent
 */
function CacheAgentGroupItem(agentType, entries) {
    vscode.TreeItem.call(this, agentType, vscode.TreeItemCollapsibleState.Collapsed);
    this.entries = entries;
    this.description = `${entries.length} entrées`;
    this.iconPath = new vscode.ThemeIcon('folder');
    this.contextValue = 'cacheGroup';
}
CacheAgentGroupItem.prototype = Object.create(vscode.TreeItem.prototype);
CacheAgentGroupItem.prototype.constructor = CacheAgentGroupItem;

/**
 * Provider pour les actions récentes (Auto-Accept)
 */
function ActionsTreeProvider(apiClient) {
    this.apiClient = apiClient;
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    this.actions = [];
    this.stats = {};
}

ActionsTreeProvider.prototype.refresh = function () {
    this._onDidChangeTreeData.fire();
};

ActionsTreeProvider.prototype.updateData = async function () {
    try {
        const status = await this.apiClient.getAutoAcceptStatus();
        this.stats = status.statistics || {};

        const actionsData = await this.apiClient.getRecentActions(20);
        this.actions = actionsData || [];
        this.refresh();
    } catch (error) {
        console.error('Failed to fetch actions:', error);
        this.actions = [];
        this.stats = {};
        this.refresh();
    }
};

ActionsTreeProvider.prototype.getTreeItem = function (element) {
    return element;
};

ActionsTreeProvider.prototype.getChildren = async function (element) {
    if (element) {
        return [];
    }

    const items = [];

    // Statistiques
    items.push(new ActionStatsItem('Traités', this.stats.total_processed || 0, 'pulse'));
    items.push(new ActionStatsItem('Acceptés', this.stats.auto_accepted || 0, 'check'));
    items.push(new ActionStatsItem('Rejetés', this.stats.rejected || 0, 'x'));

    // Actions récentes
    const recentActions = this.actions.slice(0, 10);
    for (let i = 0; i < recentActions.length; i++) {
        items.push(new ActionItem(recentActions[i]));
    }

    return items;
};

/**
 * Item de statistique d'action
 */
function ActionStatsItem(label, value, icon) {
    vscode.TreeItem.call(this, `${label}: ${value}`, vscode.TreeItemCollapsibleState.None);
    this.iconPath = new vscode.ThemeIcon(icon);
}
ActionStatsItem.prototype = Object.create(vscode.TreeItem.prototype);
ActionStatsItem.prototype.constructor = ActionStatsItem;

/**
 * Item d'action
 */
function ActionItem(action) {
    const label = action.action_type || 'unknown';
    vscode.TreeItem.call(this, label, vscode.TreeItemCollapsibleState.None);

    this.description = action.accepted ? 'Accepté' : 'Rejeté';
    this.iconPath = new vscode.ThemeIcon(
        action.accepted ? 'check' : 'x',
        action.accepted
            ? new vscode.ThemeColor('charts.green')
            : new vscode.ThemeColor('charts.red')
    );

    if (action.timestamp) {
        this.tooltip = `${label}\nDate: ${new Date(action.timestamp).toLocaleString()}`;
    }
}
ActionItem.prototype = Object.create(vscode.TreeItem.prototype);
ActionItem.prototype.constructor = ActionItem;

module.exports = {
    AgentsTreeProvider: AgentsTreeProvider,
    CacheTreeProvider: CacheTreeProvider,
    ActionsTreeProvider: ActionsTreeProvider
};
