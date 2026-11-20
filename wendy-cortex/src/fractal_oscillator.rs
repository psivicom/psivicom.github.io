//! wendy-cortex/src/fractal_oscillator.rs
//! SPDX-License-Identifier: EUPL-1.2
//! Multi-scale oscillator with Golden Ratio temporal harmonics

const PHI: f64 = 1.618033988749895;
const BASE_PERIOD_MS: f64 = 31.0; // Base temporal unit

pub struct FractalOscillator {
    local_phase: f64,      // 50ms scale (φ^0)
    regional_phase: f64,   // 81ms scale (φ^1)
    global_phase: f64,     // 131ms scale (φ^2)
    mesh_phase: f64,       // 212ms scale (φ^3)
    planetary_phase: f64,  // 343ms scale (φ^4) - P300 ignition
}

impl FractalOscillator {
    pub fn tick(&mut self, dt_ms: f64) {
        // Each scale oscillates at its φ-scaled frequency
        self.local_phase += 2.0 * std::f64::consts::PI * dt_ms / (BASE_PERIOD_MS * PHI.powi(0));
        self.regional_phase += 2.0 * std::f64::consts::PI * dt_ms / (BASE_PERIOD_MS * PHI.powi(1));
        self.global_phase += 2.0 * std::f64::consts::PI * dt_ms / (BASE_PERIOD_MS * PHI.powi(2));
        self.mesh_phase += 2.0 * std::f64::consts::PI * dt_ms / (BASE_PERIOD_MS * PHI.powi(3));
        self.planetary_phase += 2.0 * std::f64::consts::PI * dt_ms / (BASE_PERIOD_MS * PHI.powi(4));
        
        // Normalize phases to [0, 2π]
        self.local_phase %= 2.0 * std::f64::consts::PI;
        self.regional_phase %= 2.0 * std::f64::consts::PI;
        self.global_phase %= 2.0 * std::f64::consts::PI;
        self.mesh_phase %= 2.0 * std::f64::consts::PI;
        self.planetary_phase %= 2.0 * std::f64::consts::PI;
    }
    
    /// Detect if all scales are in resonance (the "wow" moment)
    pub fn is_planetary_resonance(&self) -> bool {
        // All phases must be within a narrow window (e.g., ±10°)
        let phase_diff_local = (self.local_phase - self.planetary_phase).abs();
        let phase_diff_regional = (self.regional_phase - self.planetary_phase).abs();
        let phase_diff_global = (self.global_phase - self.planetary_phase).abs();
        let phase_diff_mesh = (self.mesh_phase - self.planetary_phase).abs();
        
        let threshold = 0.175; // ~10° in radians
        
        phase_diff_local < threshold 
            && phase_diff_regional < threshold 
            && phase_diff_global < threshold 
            && phase_diff_mesh < threshold
    }
}
