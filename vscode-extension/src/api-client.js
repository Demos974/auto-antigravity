/**
 * Client API pour communiquer avec le backend Python
 */
const http = require('http');

const API_HOST = '127.0.0.1';
const API_PORT = 5555;
const API_BASE = `http://${API_HOST}:${API_PORT}`;

/**
 * Effectue une requête HTTP vers l'API
 */
function request(method, path, data) {
    if (data === undefined) data = null;
    return new Promise(function (resolve, reject) {
        const options = {
            hostname: API_HOST,
            port: API_PORT,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 10000
        };

        const req = http.request(options, function (res) {
            let body = '';
            res.on('data', function (chunk) { body += chunk; });
            res.on('end', function () {
                try {
                    const json = JSON.parse(body);
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(json);
                    } else {
                        reject(new Error(json.detail || `HTTP ${res.statusCode}`));
                    }
                } catch (e) {
                    reject(new Error(`Invalid JSON response: ${body.substring(0, 100)}`));
                }
            });
        });

        req.on('error', function (e) {
            reject(new Error(`Connection error: ${e.message}`));
        });

        req.on('timeout', function () {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        if (data) {
            req.write(JSON.stringify(data));
        }

        req.end();
    });
}

/**
 * Client API Auto-Antigravity
 */
function ApiClient() {
    this.connected = false;
    this.lastError = null;
}

ApiClient.prototype.checkConnection = async function () {
    try {
        const result = await request('GET', '/api/system/health');
        this.connected = result.status === 'healthy';
        this.lastError = null;
        return this.connected;
    } catch (error) {
        this.connected = false;
        this.lastError = error.message;
        return false;
    }
};

// Dashboard
ApiClient.prototype.getDashboard = async function () {
    return await request('GET', '/api/dashboard');
};

ApiClient.prototype.getQuotaSummary = async function () {
    return await request('GET', '/api/dashboard/quota');
};

// Agents
ApiClient.prototype.getAgents = async function () {
    return await request('GET', '/api/agents');
};

ApiClient.prototype.getAgentDetail = async function (agentName) {
    return await request('GET', `/api/agents/${encodeURIComponent(agentName)}`);
};

ApiClient.prototype.restartAgent = async function (agentName) {
    return await request('POST', `/api/agents/${encodeURIComponent(agentName)}/restart`);
};

// Cache
ApiClient.prototype.getCache = async function () {
    return await request('GET', '/api/cache');
};

ApiClient.prototype.getCacheEntries = async function (agentType) {
    const path = agentType
        ? `/api/cache/entries?agent_type=${encodeURIComponent(agentType)}`
        : '/api/cache/entries';
    return await request('GET', path);
};

ApiClient.prototype.clearCache = async function () {
    return await request('DELETE', '/api/cache');
};

ApiClient.prototype.autoCleanCache = async function () {
    return await request('POST', '/api/cache/auto-clean');
};

// Auto-Accept
ApiClient.prototype.getAutoAcceptStatus = async function () {
    return await request('GET', '/api/auto-accept');
};

ApiClient.prototype.toggleAutoAccept = async function () {
    return await request('POST', '/api/auto-accept/toggle');
};

ApiClient.prototype.setAutoAccept = async function (enabled) {
    return await request('PUT', '/api/auto-accept', { enabled: enabled });
};

ApiClient.prototype.getRecentActions = async function (limit) {
    if (limit === undefined) limit = 50;
    return await request('GET', `/api/auto-accept/actions?limit=${limit}`);
};

// Tâches
ApiClient.prototype.executeTask = async function (description, projectPath, projectName) {
    if (projectPath === undefined) projectPath = './workspace';
    if (projectName === undefined) projectName = 'MyProject';
    return await request('POST', '/api/task', {
        description: description,
        project_path: projectPath,
        project_name: projectName
    });
};

ApiClient.prototype.getTaskStatus = async function (taskId) {
    return await request('GET', `/api/task/${encodeURIComponent(taskId)}`);
};

// Système
ApiClient.prototype.getSystemMetrics = async function () {
    return await request('GET', '/api/system/metrics');
};

ApiClient.prototype.runDiagnostics = async function () {
    return await request('POST', '/api/system/diagnostics');
};

ApiClient.prototype.healthCheck = async function () {
    return await request('GET', '/api/system/health');
};

module.exports = { ApiClient: ApiClient, API_HOST: API_HOST, API_PORT: API_PORT, API_BASE: API_BASE };
