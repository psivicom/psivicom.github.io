// mesh/agents/volunteer-agent.js
const os = require('os');
const https = require('https');
const crypto = require('crypto');

const CONFIG = {
    nodeId: process.env.PSVC_NODE_ID || `node-${os.hostname()}`,
    githubToken: process.env.PSVC_GITHUB_TOKEN,
    repoOwner: 'psivicom',
    repoName: 'psivicom.github.io',
    apiKey: process.env.PSVC_API_KEY,
    reportIntervalMs: parseInt(process.env.PSVC_REPORT_INTERVAL || '15000'),
    location: {
        lat: parseFloat(process.env.PSVC_LAT || '48.45'),
        lon: parseFloat(process.env.PSVC_LON || '-123.5')
    }
};

async function measureLoad() {
    const load = os.loadavg()[0];
    const cpus = os.cpus().length;
    return Math.min(1.0, load / cpus);
}

async function measureLatencyToCore() {
    return new Promise((resolve) => {
        const start = process.hrtime.bigint();
        const req = https.get('https://psivi.com/assets/ping-test.txt', (res) => {
            res.resume();
            res.on('end', () => {
                const end = process.hrtime.bigint();
                resolve(Math.round((Number(end - start) / 1e6) * 100) / 100);
            });
        });
        req.on('error', () => resolve(null));
        req.setTimeout(3000, () => { req.destroy(); resolve(null); });
    });
}

async function sendHeartbeat() {
    const now = new Date().toISOString();
    try {
        const payload = {
            nodeId: CONFIG.nodeId,
            timestamp: now,
            location: CONFIG.location,
            status: 'active',
            current_load: await measureLoad(),
            latency_to_wendy_core: await measureLatencyToCore(),
            system: { platform: os.platform(), arch: os.arch(), cpus: os.cpus().length, totalMemMb: Math.round(os.totalmem() / 1024 / 1024) }
        };

        const signature = crypto.createHmac('sha256', CONFIG.apiKey).update(JSON.stringify(payload)).digest('hex');
        const data = JSON.stringify({ event_type: 'mesh-heartbeat', client_payload: payload });
        
        const req = https.request({
            hostname: 'api.github.com',
            path: `/repos/${CONFIG.repoOwner}/${CONFIG.repoName}/dispatches`,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${CONFIG.githubToken}`,
                'Accept': 'application/vnd.github+json',
                'User-Agent': 'psvc-volunteer-agent/2.0',
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(data),
                'X-PSVC-Signature': signature
            }
        }, (res) => {
            if (res.statusCode === 204) {
                console.log(`[${now}] [${CONFIG.nodeId}] Heartbeat sent (load: ${(payload.current_load * 100).toFixed(1)}%, latency: ${payload.latency_to_wendy_core}ms)`);
            } else {
                console.error(`[${now}] [${CONFIG.nodeId}] Heartbeat failed: ${res.statusCode}`);
            }
        });

        req.on('error', (e) => console.error(`[${now}] [${CONFIG.nodeId}] Network error:`, e.message));
        req.write(data);
        req.end();

    } catch (error) {
        console.error(`[${now}] [${CONFIG.nodeId}] Heartbeat generation error:`, error);
    }
}

console.log(`[${new Date().toISOString()}] [${CONFIG.nodeId}] PSVC Volunteer Agent starting...`);
sendHeartbeat();
setInterval(sendHeartbeat, CONFIG.reportIntervalMs);
