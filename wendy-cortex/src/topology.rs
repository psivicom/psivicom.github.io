use std::collections::HashMap;
use tracing::info;

pub struct HebbianTopology {
    weights: HashMap<String, f32>,
}

impl HebbianTopology {
    pub fn new() -> Self {
        Self {
            weights: HashMap::new(),
        }
    }

    pub async fn update_weight(&mut self, uri: &str, delta: f32) {
        let current = self.weights.entry(uri.to_string()).or_insert(0.0);
        *current += delta;
        info!(target: "hebbian_topology", "edge_weight updated | uri={} | new_weight={:.3}", uri, current);
    }
}
