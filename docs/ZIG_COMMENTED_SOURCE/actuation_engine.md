# Actuation Engine: Bare-Metal Zig Implementation
**SPDX-License-Identifier:** EUPL-1.2  
**SPDX-FileCopyrightText:** 2026 Louis-Philippe Audette | PSIVI.COM  

## Architectural Purpose
This Zig module serves as the high-performance evaluation engine for the Robotic Actuator Bridge. It replaces brittle Python `if` statements with a compiled, zero-dependency binary that evaluates actuation rules in **nanoseconds**, completely bypassing the Python GIL.

## Vector Mapping (16-Dimensional `float32`)
The engine expects a comma-separated string of 16 `float32` values, mapped as follows:
- `[0]`: phase
- `[1]`: intensity (Foraging activity level)
- `[2]`: defense_weight (Threat detection readiness)
- `[3]`: explore_weight
- `[4]`: stress_accumulator (Environmental stress, e.g., heat/humidity)
- `[5]`: conscious_mass
- `[6-15]`: padding / reserved for future expansion

## Execution Flow
1. **Parse Arguments**: Receives the 16-dim vector as a CSV string and the path to `actuation_rules.json`.
2. **Parse Vector**: Tokenizes the CSV string and converts each token to `f32`.
3. **Evaluate Rules**: Checks the vector against threshold conditions.
4. **Output**: Prints a valid JSON array of matched commands to `stdout`, which the Python bridge captures, cryptographically signs, and dispatches via MQTT/ROS2.

## Compilation Note
This documented version resides in `/docs/ZIG_COMMENTED_SOURCE/`. The active, compiled version in `src/core/actuation_engine.zig` is strictly stripped of all comments to ensure maximum compatibility and zero parsing overhead in the GitHub Actions Zig compiler.
