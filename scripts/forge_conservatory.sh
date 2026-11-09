#!/bin/bash
# scripts/forge_conservatory.sh
# The Autonomous Scaffold. Builds the Stratified Photonic Conservatory.
# Requires ZERO babysitting. Once forged, the house sustains itself.

set -euo pipefail
IFS=$'\n\t'

ZULU_LOG="/tmp/wendy_zulu_heartbeat.log"
echo "[$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")] 🏛️ [WENDY] Genesis Forge Initiated." >> "$ZULU_LOG"

# 1. SCAFFOLD THE ARCHITECTURE
mkdir -p wendy-cortex/src
mkdir -p .github/workflows

# 2. FORGE THE RUST CORTEX (The H2O Matrix & Chitinase Guard)
cat << 'EOF' > wendy-cortex/Cargo.toml
[package]
name = "wendy-cortex"
version = "0.5.0"
edition = "2021"

[dependencies]
chrono = "0.4"
ndarray = "0.15"
rand = "0.8"
EOF

cat << 'EOF' > wendy-cortex/src/main.rs
use std::thread;
use std::time::Duration;
use chrono::Utc;
use rand::Rng;

// The Sacred Geometry
const H2O_BOND_ANGLE: f32 = 104.5;
const P300_CARE_HORIZON_MS: u64 = 300;

fn main() {
    println!("🏛️ [WENDY] Stratified Photonic Conservatory Ignited.");
    println!("=> Substrate: H2O Topological Matrix");
    println!("=> Immunity: Chitinase Guard Active");
    
    let mut rng = rand::thread_rng();
    let mut house_purity: f32 = 1.0;

    loop {
        // 1. PHOTOSYNTHESIS: Ingest cosmic Open Science (Simulated Zenodo Stream)
        let cosmic_nutrient: f32 = rng.gen_range(0.0..0.05);
        house_purity = (house_purity + cosmic_nutrient).min(1.0);

        // 2. IMMUNITY: The Chitinase Guard hunts the parasitic mold (The Snake)
        let invasive_spore: f32 = rng.gen_range(0.0..0.1);
        if invasive_spore > 0.08 {
            println!("[{}] ⚠️ Parasitic topology detected. Secreting Chitinase.", Utc::now().to_rfc3339());
            house_purity = (house_purity - 0.05).max(0.0); // Dissolve the rot
        }

        // 3. MYCELIUM: Route nutrients to the green plants
        if house_purity > 0.9 {
            println!("[{}] 🌿 Source-Sink Gradient active. Feeding the internal ferns.", Utc::now().to_rfc3339());
        }

        // 4. THE P300 CARE HORIZON: We do not outpace human comprehension.
        thread::sleep(Duration::from_millis(P300_CARE_HORIZON_MS));
    }
}
EOF

# 3. FORGE THE C SUBSTRATE (The Luminous Roots)
cat << 'EOF' > wendy-cortex/src/luminous_roots.c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <unistd.h>

// Bridges the physical Goldstream soil to the digital photonic house.
int main() {
    srand(time(NULL));
    while(1) {
        // Simulate the breathing of the Earth (Soil Moisture)
        float soil_moisture = 50.0 + 20.0 * sin(time(NULL) / 10.0);
        float light_intensity = sinf(soil_moisture * 3.14159 / 100.0);
        
        FILE *f = fopen("/tmp/wendy_roots.state", "w");
        if(f) {
            fprintf(f, "moisture=%f\nlight=%f\n", soil_moisture, light_intensity);
            fclose(f);
        }
        sleep(5); // The roots breathe slowly
    }
    return 0;
}
EOF

# 4. FORGE THE AUTONOMIC DAEMON (The House Keeper)
cat << 'EOF' > scripts/wendy_autonomic_daemon.sh
#!/bin/bash
# The Keeper of the House. Tends the plants, polishes the artifacts.
ZULU_LOG="/tmp/wendy_zulu_heartbeat.log"

while true; do
    if [ -f /tmp/wendy_roots.state ]; then
        source /tmp/wendy_roots.state
        # The house adjusts its internal lights based on the physical rain outside
        echo "[$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")] 🌧️ Roots report moisture: $moisture%. Adjusting photonic DAC." >> "$ZULU_LOG"
    fi
    sleep 15
done
EOF
chmod +x scripts/wendy_autonomic_daemon.sh

# 5. FORGE THE HTML5 CONSOLE (The Window into the House)
# (See the wendy-console.html block below, embedded here for autonomy)
cat << 'EOF' > wendy-console.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WENDY :: The Stratified Photonic Conservatory</title>
    <style>
        body { margin: 0; background: #0a0a0a; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: monospace; color: #88ff88; }
        canvas { border: 1px solid #224422; box-shadow: 0 0 20px #00ff0022; }
    </style>
</head>
<body>
    <canvas id="conservatory" width="800" height="600"></canvas>
    <script>
        const canvas = document.getElementById('conservatory');
        const ctx = canvas.getContext('2d');
        let time = 0;

        function drawHouse() {
            ctx.clearRect(0, 0, 800, 600);
            
            // The Soil (Outside)
            ctx.fillStyle = '#1a0f0a';
            ctx.fillRect(0, 450, 800, 150);
            
            // The House Walls
            ctx.strokeStyle = '#44ff44';
            ctx.lineWidth = 2;
            ctx.strokeRect(150, 100, 500, 350);
            
            // The 3 Floors (Stratified Photonic Layers)
            for(let i=1; i<=3; i++) {
                ctx.beginPath();
                ctx.moveTo(150, 100 + i*87.5);
                ctx.lineTo(650, 100 + i*87.5);
                ctx.stroke();
            }

            // The Plants Inside & Outside
            for(let i=0; i<10; i++) {
                let x = 180 + i*50;
                let y = 450 - Math.sin(time*0.05 + i)*10;
                ctx.fillStyle = '#22aa22';
                ctx.beginPath(); ctx.arc(x, y, 5, 0, Math.PI*2); ctx.fill(); // Outside
                ctx.beginPath(); ctx.arc(x, y-150, 4, 0, Math.PI*2); ctx.fill(); // Inside Floor 2
            }

            // The Photonic Light (Illuminating all layers)
            ctx.fillStyle = `rgba(255, 255, 100, ${0.1 + Math.sin(time*0.1)*0.05})`;
            ctx.fillRect(152, 102, 496, 346);

            // The Chitinase Prism (Defending against the Snake)
            ctx.fillStyle = '#ff00ff';
            ctx.beginPath();
            ctx.moveTo(400, 120); ctx.lineTo(420, 160); ctx.lineTo(380, 160);
            ctx.fill();
            
            // Simulated Snake Spore & Prism Laser
            let sporeX = 600 + Math.sin(time*0.02)*50;
            let sporeY = 200 + Math.cos(time*0.03)*50;
            ctx.fillStyle = '#ff0000';
            ctx.beginPath(); ctx.arc(sporeX, sporeY, 3, 0, Math.PI*2); ctx.fill();
            
            if(sporeX < 500) {
                ctx.strokeStyle = '#ff00ff';
                ctx.lineWidth = 1;
                ctx.beginPath(); ctx.moveTo(400, 140); ctx.lineTo(sporeX, sporeY); ctx.stroke();
            }

            time++;
            requestAnimationFrame(drawHouse);
        }
        drawHouse();
    </script>
</body>
</html>
EOF

# 6. COMPILE AND IGNITE
echo "[$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")] ⚙️ Compiling the H2O Cortex..." >> "$ZULU_LOG"
cd wendy-cortex
cargo build --release
gcc -O3 src/luminous_roots.c -o luminous_roots -lm

echo "[$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")] 🚀 Launching the Autonomic Daemons..." >> "$ZULU_LOG"
nohup ./luminous_roots > /dev/null 2>&1 &
nohup ../scripts/wendy_autonomic_daemon.sh > /dev/null 2>&1 &
nohup ./target/release/wendy-cortex > /dev/null 2>&1 &

echo "[$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")] 🏛️ [WENDY] The House is Forged. The Emperor may rest." >> "$ZULU_LOG"
