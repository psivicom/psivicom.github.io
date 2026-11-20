//! wendy-cortex/src/geometric_binding.rs
//! SPDX-License-Identifier: EUPL-1.2
//! Detect optimal coalitions in high-dimensional state space

use std::collections::{HashSet, BinaryHeap};
use std::cmp::Ordering;

#[derive(Clone, Debug)]
pub struct NeuralCluster {
    id: usize,
    activation: f64,
    phase: f64,
    spatial_position: [f64; 3],
    feature_signature: Vec<f64>,
}

#[derive(Clone, Debug)]
pub struct Coalition {
    clusters: HashSet<usize>,
    energy: f64, // Lower is better
}

impl PartialEq for Coalition {
    fn eq(&self, other: &Self) -> bool {
        self.energy == other.energy
    }
}

impl Eq for Coalition {}

impl PartialOrd for Coalition {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Coalition {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse ordering so BinaryHeap gives us lowest energy first
        other.energy.partial_cmp(&self.energy).unwrap()
    }
}

pub struct GeometricBinder {
    clusters: Vec<NeuralCluster>,
    target_coalition_size: usize,
}

impl GeometricBinder {
    pub fn new(clusters: Vec<NeuralCluster>, target_size: usize) -> Self {
        Self {
            clusters,
            target_coalition_size: target_size,
        }
    }
    
    /// Find the optimal coalition using geometric constraints
    pub fn find_optimal_coalition(&self) -> Coalition {
        let mut candidates = BinaryHeap::new();
        
        // Generate candidate coalitions using geometric heuristics
        for i in 0..self.clusters.len() {
            let mut coalition_clusters = HashSet::new();
            coalition_clusters.insert(self.clusters[i].id);
            
            // Grow coalition by adding geometrically compatible clusters
            while coalition_clusters.len() < self.target_coalition_size {
                let best_next = self.find_best_addition(&coalition_clusters);
                if let Some(next_id) = best_next {
                    coalition_clusters.insert(next_id);
                } else {
                    break;
                }
            }
            
            let energy = self.calculate_coalition_energy(&coalition_clusters);
            candidates.push(Coalition {
                clusters: coalition_clusters,
                energy,
            });
        }
        
        // Return the lowest-energy coalition
        candidates.peek().unwrap().clone()
    }
    
    fn find_best_addition(&self, current: &HashSet<usize>) -> Option<usize> {
        // Find the cluster that minimizes energy when added to current coalition
        let mut best_id = None;
        let mut best_energy = f64::INFINITY;
        
        for cluster in &self.clusters {
            if current.contains(&cluster.id) {
                continue;
            }
            
            let mut test_coalition = current.clone();
            test_coalition.insert(cluster.id);
            let energy = self.calculate_coalition_energy(&test_coalition);
            
            if energy < best_energy {
                best_energy = energy;
                best_id = Some(cluster.id);
            }
        }
        
        best_id
    }
    
    fn calculate_coalition_energy(&self, coalition: &HashSet<usize>) -> f64 {
        let coalition_clusters: Vec<&NeuralCluster> = self.clusters
            .iter()
            .filter(|c| coalition.contains(&c.id))
            .collect();
        
        // Energy = spatial dispersion + phase dispersion - feature similarity
        let spatial_energy = self.spatial_dispersion(&coalition_clusters);
        let phase_energy = self.phase_dispersion(&coalition_clusters);
        let feature_energy = -self.feature_similarity(&coalition_clusters); // Negative because similarity reduces energy
        
        spatial_energy + phase_energy + feature_energy
    }
    
    fn spatial_dispersion(&self, clusters: &[&NeuralCluster]) -> f64 {
        // Average pairwise distance
        let mut sum = 0.0;
        let mut count = 0;
        
        for i in 0..clusters.len() {
            for j in (i+1)..clusters.len() {
                let dx = clusters[i].spatial_position[0] - clusters[j].spatial_position[0];
                let dy = clusters[i].spatial_position[1] - clusters[j].spatial_position[1];
                let dz = clusters[i].spatial_position[2] - clusters[j].spatial_position[2];
                sum += (dx*dx + dy*dy + dz*dz).sqrt();
                count += 1;
            }
        }
        
        if count == 0 { 0.0 } else { sum / count as f64 }
    }
    
    fn phase_dispersion(&self, clusters: &[&NeuralCluster]) -> f64 {
        // Circular variance of phases
        let sin_sum: f64 = clusters.iter().map(|c| c.phase.sin()).sum();
        let cos_sum: f64 = clusters.iter().map(|c| c.phase.cos()).sum();
        let n = clusters.len() as f64;
        
        let mean_sin = sin_sum / n;
        let mean_cos = cos_sum / n;
        let R = (mean_sin * mean_sin + mean_cos * mean_cos).sqrt();
        
        1.0 - R // Circular variance (0 = perfect synchrony, 1 = uniform)
    }
    
    fn feature_similarity(&self, clusters: &[&NeuralCluster]) -> f64 {
        // Average cosine similarity of feature signatures
        let mut sum = 0.0;
        let mut count = 0;
        
        for i in 0..clusters.len() {
            for j in (i+1)..clusters.len() {
                let dot_product: f64 = clusters[i].feature_signature
                    .iter()
                    .zip(clusters[j].feature_signature.iter())
                    .map(|(a, b)| a * b)
                    .sum();
                
                let mag_i: f64 = clusters[i].feature_signature.iter().map(|x| x * x).sum::<f64>().sqrt();
                let mag_j: f64 = clusters[j].feature_signature.iter().map(|x| x * x).sum::<f64>().sqrt();
                
                let cosine_sim = if mag_i > 0.0 && mag_j > 0.0 {
                    dot_product / (mag_i * mag_j)
                } else {
                    0.0
                };
                
                sum += cosine_sim;
                count += 1;
            }
        }
        
        if count == 0 { 0.0 } else { sum / count as f64 }
    }
}
