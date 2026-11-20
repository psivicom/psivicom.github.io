//! WENDY Mathematical Core
//! SPDX-License-Identifier: EUPL-1.2

pub fn welford_variance(data: &[f64]) -> f64 {
    let mut count: f64 = 0.0;
    let mut mean: f64 = 0.0;
    let mut m2: f64 = 0.0;
    for &x in data {
        count += 1.0;
        let delta = x - mean;
        mean += delta / count;
        let delta2 = x - mean;
        m2 += delta * delta2;
    }
    if count < 2.0 { 0.0 } else { m2 / (count - 1.0) }
}
