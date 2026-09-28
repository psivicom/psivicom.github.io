// mesh/workflows/aggregate-mesh-v2.js
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const SpatialClusterer = require('../spatial-clustering');
const DynamicGeoCalculator = require('../dynamic-geo');

const CONFIG = {
    meshStatusPath: path.join(__dirname, '../../mesh-status.json'),
    metabolismPath: path.join(__dirname, '../../wendy_metabolism.json'),
    heartbeatStorePath: path.join(__dirname, '../.heartbeat-store.json'),
    staleThresholdMs: 120000
};

class HeartbeatStore {
    constructor(storePath) {
        this.storePath = storePath;
        this.data = new Map();
    }

    async load() {
        try {
            const raw = await fs.readFile(this.storePath, 'utf-8');
            this.data = new Map(Object.entries(JSON.parse(raw)));
        } catch (e) {
            this.data = new Map();
        }
    }

    async save() {
        await fs.writeFile(this.storePath, JSON.stringify(Object.fromEntries(this.data), null, 2));
    }

    upsert(heartbeat) {
        const existing = this.data.get(heartbeat.nodeId);
        if (!existing || heartbeat.timestamp > existing.timestamp) {
            this.data.set(heartbeat.nodeId, heartbeat);
            return true;
        }
        return false;
    }

    pruneStale(thresholdMs) {
        const cutoff = Date.now() - thresholdMs;
        let pruned = 0;
        for (const [id, hb] of this.data.entries()) {
            if (new Date(hb.timestamp).getTime() < cutoff) {
                this.data.delete(id);
                pruned++;
            }
        }
        return pruned;
    }

    getAll() {
        return Array.from(this.data.values());
    }
}

class MetabolismManager {
    constructor(metabolismPath) {
        this.path = metabolismPath;
        this.data = null;
    }

    async load() {
        try {
            this.data = JSON.parse(await fs.readFile(this.path, 'utf-8'));
        } catch (e) {
            this.data = this._createDefault();
        }
    }

    _createDefault() {
        return {
            schema_version: '1.0.0',
            last_updated: new Date().toISOString(),
            current_state: { mode: 'sequential', complexity: 'low', network_health: 'poor', active_cluster_count: 0, active_node_count: 0, avg_mesh_latency_ms: null, dynamic_radius_km: 200.0 },
            thresholds: { optimal: { max_avg_latency_ms: 10.0, min_clusters: 1, mode: 'parallel', complexity: 'high' }, degraded: { max_avg_latency_ms: 50.0, min_clusters: 0, mode: 'hybrid', complexity: 'medium' }, poor: { max_avg_latency_ms: null, min_clusters: 0, mode: 'sequential', complexity: 'low' } },
            history: [],
            history_config: { max_entries: 500, retention_days: 30 }
        };
    }

    update(meshSummary) {
        const now = new Date().toISOString();
        const prevMode = this.data.current_state.mode;
        const prevHealth = this.data.current_state.network_health;

        let newState;
        if (meshSummary.avgLatencyMs <= 10.0 && meshSummary.clusterCount >= 1) {
            newState = { mode: 'parallel', complexity: 'high', network_health: 'optimal' };
        } else if (meshSummary.avgLatencyMs <= 50.0) {
            newState = { mode: 'hybrid', complexity: 'medium', network_health: 'degraded' };
        } else {
            newState = { mode: 'sequential', complexity: 'low', network_health: 'poor' };
        }

        this.data.current_state = { ...this.data.current_state, ...newState, active_cluster_count: meshSummary.clusterCount, active_node_count: meshSummary.nodeCount, avg_mesh_latency_ms: meshSummary.avgLatencyMs, dynamic_radius_km: meshSummary.dynamicRadius };
        this.data.last_updated = now;

        if (prevMode !== newState.mode || prevHealth !== newState.network_health || this.data.history.length === 0) {
            this.data.history.push({ timestamp: now, mode: newState.mode, complexity: newState.complexity, network_health: newState.network_health, trigger: 'mesh_update', active_nodes: meshSummary.nodeCount, avg_latency_ms: meshSummary.avgLatencyMs });
            if (this.data.history.length > this.data.history_config.max_entries) {
                this.data.history = this.data.history.slice(-this.data.history_config.max_entries);
            }
        }
    }

    async save() {
        await fs.writeFile(this.path, JSON.stringify(this.data, null, 2));
    }
}

async function main() {
    const startTime = process.hrtime.bigint();
    const now = new Date().toISOString();
    const store = new HeartbeatStore(CONFIG.heartbeatStorePath);
    const metabolism = new MetabolismManager(CONFIG.metabolismPath);
    const geoCalc = new DynamicGeoCalculator();

    await store.load();
    await metabolism.load();

    if (process.env.PAYLOAD) {
        try {
            const payload = JSON.parse(process.env.PAYLOAD);
            store.upsert({ ...payload, status: 'active' });
        } catch (e) { console.warn('[Ingest] Invalid PAYLOAD:', e.message); }
    }

    store.pruneStale(CONFIG.staleThresholdMs);
    const nodes = store.getAll();

    for (const node of nodes) {
        if (typeof node.latency_to_wendy_core === 'number') geoCalc.recordLatency(node.latency_to_wendy_core);
    }
    const dynamicRadius = geoCalc.getDynamicRadius();

    const clusterer = new SpatialClusterer(dynamicRadius);
    const clusters = clusterer.cluster(nodes);

    const clusteredIds = new Set(clusters.flatMap(c => c.members));
    const isolatedCount = nodes.filter(n => n.status === 'active' && !clusteredIds.has(n.nodeId || n.id)).length;
    const latencies = nodes.map(n => n.latency_to_wendy_core).filter(l => typeof l === 'number' && !isNaN(l));
    const avgLatency = latencies.length > 0 ? latencies.reduce((a, b) => a + b, 0) / latencies.length : 999;

    const meshState = {
        timestamp: now,
        mesh_version: '2.0.0',
        dynamic_radius_km: dynamicRadius,
        nodes: nodes.map(n => ({ nodeId: n.nodeId, location: n.location, status: n.status, current_load: n.current_load, latency_to_wendy_core: n.latency_to_wendy_core, timestamp: n.timestamp })),
        optimal_clusters: clusters,
        summary: { total_nodes: nodes.length, total_clusters: clusters.length, isolated_nodes: isolatedCount, aggregation_duration_ms: Number(process.hrtime.bigint() - startTime) / 1e6 }
    };

    metabolism.update({ nodeCount: nodes.length, clusterCount: clusters.length, avgLatencyMs: avgLatency, dynamicRadius });

    await fs.writeFile(CONFIG.meshStatusPath, JSON.stringify(meshState, null, 2));
    await store.save();
    await metabolism.save();

    console.log(`[Aggregator] Wrote mesh-status.json (${nodes.length} nodes, ${clusters.length} clusters) in ${(Number(process.hrtime.bigint() - startTime) / 1e6).toFixed(2)}ms`);
}

main().catch(err => { console.error('[FATAL]', err); process.exit(1); });
