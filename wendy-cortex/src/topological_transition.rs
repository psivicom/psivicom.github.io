//! wendy-cortex/src/topological_transition.rs
//! SPDX-License-Identifier: EUPL-1.2
//! Detect when the system crosses a bifurcation point (the "wow" moment)

pub struct TopologicalMonitor {
    state_history: Vec<f64>, // Energy over time
    window_size: usize,
}

impl TopologicalMonitor {
    pub fn new(window_size: usize) -> Self {
        Self {
            state_history: Vec::new(),
            window_size,
        }
    }
    
    pub fn update(&mut self, current_energy: f64) -> bool {
        self.state_history.push(current_energy);
        
        if self.state_history.len() > self.window_size {
            self.state_history.remove(0);
        }
        
        self.detect_bifurcation()
    }
    
    fn detect_bifurcation(&self) -> bool {
        if self.state_history.len() < self.window_size {
            return false;
        }
        
        // Calculate the derivative (rate of change)
        let mut derivatives = Vec::new();
        for i in 1..self.state_history.len() {
            derivatives.push(self.state_history[i] - self.state_history[i-1]);
        }
        
        // Detect sudden acceleration (bifurcation)
        let recent_derivative = derivatives[derivatives.len() - 1];
        let avg_derivative = derivatives[..derivatives.len()-1]
            .iter()
            .sum::<f64>() / (derivatives.len() - 1) as f64;
        
        // If recent change is 3x the average, we've hit a bifurcation
        (recent_derivative - avg_derivative).abs() > 3.0 * avg_derivative.abs()
    }
}
