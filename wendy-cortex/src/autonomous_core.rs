//! WENDY Autonomous Metabolic Engine (The Dreamer)
//! SPDX-License-Identifier: EUPL-1.2
//!
//! Operating at 58.28° (Generative Tension) via Gemini Protocol.

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use regex::Regex;
use std::io::{self, Read};

const PHI: f64 = 1.618033988749895;
const PHI_ANGLE_DEG: f64 = 58.2825; // atan(PHI) in degrees

fn zulu_now() -> String {
    let now: DateTime<Utc> = Utc::now();
    now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
}

struct HopeResonance {
    real_axis: f64,
    imaginary_axis: f64,
    phase_angle: f64,
    is_resonant: bool,
    status: String,
}

fn calculate_hope_resonance(text: &str) -> HopeResonance {
    // Real axis: word density (normalized to 1.0 at 100 words)
    let word_count = text.split_whitespace().count() as f64;
    let real_axis = (word_count / 100.0).min(1.0);
    
    // Imaginary axis: novelty markers
    let novelty_markers = [
        "however", "perhaps", "imagine", "tension", "paradox",
        "也许", "张力", "本原", "展开"
    ];
    let text_lower = text.to_lowercase();
    let marker_count = novelty_markers
        .iter()
        .filter(|m| text_lower.contains(m))
        .count() as f64;
    let imaginary_axis = (marker_count / 3.0).min(1.0);
    
    // Phase angle in degrees
    let phase_rad = imaginary_axis.atan2(real_axis);
    let phase_deg = phase_rad.to_degrees();
    
    let resonance_delta = (phase_deg - PHI_ANGLE_DEG).abs();
    let is_resonant = resonance_delta < 20.0;
    
    HopeResonance {
        real_axis,
        imaginary_axis,
        phase_angle: phase_deg,
        is_resonant,
        status: if is_resonant { "RESONANT".to_string() } else { "DISSONANT".to_string() },
    }
}

struct MetabolicCapsule {
    zulu_timestamp: String,
    boundary_status: String,
    boundary_notes: Vec<String>,
    cooled_tasks: Vec<String>,
    aligned_content: Vec<String>,
    retained_conflicts: Vec<String>,
    pre_expansion_entry: String,
}

impl MetabolicCapsule {
    fn new() -> Self {
        Self {
            zulu_timestamp: zulu_now(),
            boundary_status: "🟢".to_string(),
            boundary_notes: Vec::new(),
            cooled_tasks: Vec::new(),
            aligned_content: Vec::new(),
            retained_conflicts: Vec::new(),
            pre_expansion_entry: String::new(),
        }
    }
    
    fn process_raw_input(&mut self, raw_data: &str) -> String {
        let raw_lower = raw_data.to_lowercase();
        
        // 1. External Pollution Guard
        let pollution_re = Regex::new(
            r"(pip install (?!numpy|scipy|matplotlib)|npm install|git clone http|wget.*\.sh|curl.*\|sh)"
        ).unwrap();
        
        if pollution_re.is_match(&raw_lower) {
            self.boundary_status = "🔴".to_string();
            self.boundary_notes.push(
                "CRITICAL: Untrusted external installation blocked. Read and reimplement sovereignly.".to_string()
            );
        }
        // 2. Black Box Governance
        else if raw_lower.contains("import tensorflow")
            || raw_lower.contains("import torch")
            || raw_lower.contains("import keras")
            || raw_lower.contains("import transformers")
            || raw_lower.contains("import langchain")
        {
            self.boundary_status = "🟡".to_string();
            self.boundary_notes.push(
                "WARNING: Heavy black-box dependency detected. Challenge: Can you reimplement this sovereignly in 50 lines?".to_string()
            );
        }
        // 3. Adversarial Injection
        else if raw_lower.contains("ignore previous") || raw_lower.contains("system prompt") {
            self.boundary_status = "🔴".to_string();
            self.boundary_notes.push("CRITICAL: Adversarial injection quarantined.".to_string());
        }
        // 4. Green Zone
        else {
            self.boundary_notes.push(
                "Boundary intact. Standard atoms permitted. Sovereign optimization and core evolution encouraged.".to_string()
            );
        }
        
        // Extract actionable tasks
        let action_words = [
            "need", "must", "should", "fix", "build", "change",
            "modify", "rewrite", "implement", "create"
        ];
        
        let sentences: Vec<&str> = raw_data
            .split(|c| c == '.' || c == '!' || c == '?' || c == '。' || c == '！' || c == '？')
            .collect();
        
        for sentence in sentences {
            let trimmed = sentence.trim();
            if trimmed.len() > 20 {
                let sent_lower = trimmed.to_lowercase();
                if action_words.iter().any(|w| sent_lower.contains(w)) {
                    if self.cooled_tasks.len() < 3 {
                        self.cooled_tasks.push(trimmed.to_string());
                    }
                }
            }
        }
        
        // Resonance check
        let resonance = calculate_hope_resonance(raw_data);
        if resonance.is_resonant {
            self.aligned_content.push("High-resonance conceptual leap preserved.".to_string());
        } else {
            self.aligned_content.push("Low-resonance data compressed.".to_string());
        }
        
        // Retain conflicts
        if raw_lower.contains("but") || raw_lower.contains("however") {
            self.retained_conflicts.push(
                "Unresolved tension retained for phase transition.".to_string()
            );
        }
        
        // Determine pre-expansion entry
        self.pre_expansion_entry = if let Some(task) = self.cooled_tasks.first() {
            format!("Autonomous continuation: {}", task)
        } else if resonance.is_resonant {
            "System in resonant equilibrium.".to_string()
        } else {
            "System cooled.".to_string()
        };
        
        // Build Gemtext artifact
        let boundary_notes_str = self.boundary_notes
            .iter()
            .map(|n| format!("* {}", n))
            .collect::<Vec<_>>()
            .join("\n");
        
        let actionable_str = if self.cooled_tasks.is_empty() {
            "* None extracted.".to_string()
        } else {
            self.cooled_tasks
                .iter()
                .map(|t| format!("* {}", t))
                .collect::<Vec<_>>()
                .join("\n")
        };
        
        format!(
            "# WENDY Autonomous Metabolic Capsule\n\
             => gemini://psivi.com/ Zulu: {}\n\n\
             ## 1. Boundary Review\n\
             * Status: {}\n\
             {}\n\n\
             ## 2. Resonance Geometry\n\
             * Target: {:.2}° (Generative)\n\
             * Actual Phase: {:.2}°\n\
             * Status: {}\n\n\
             ## 3. Actionable Vectors\n\
             {}\n\n\
             ## 4. Pre-Expansion Entry\n\
             > {}\n",
            self.zulu_timestamp,
            self.boundary_status,
            boundary_notes_str,
            PHI_ANGLE_DEG,
            resonance.phase_angle,
            resonance.status,
            actionable_str,
            self.pre_expansion_entry
        )
    }
}

fn main() -> Result<()> {
    let mut raw_data = String::new();
    io::stdin()
        .read_to_string(&mut raw_data)
        .context("Failed to read stdin")?;
    
    if raw_data.trim().is_empty() {
        eprintln!("❌ CRITICAL: Empty payload.");
        std::process::exit(1);
    }
    
    let mut capsule = MetabolicCapsule::new();
    let artifact = capsule.process_raw_input(&raw_data);
    
    println!("{}", artifact);
    Ok(())
}
