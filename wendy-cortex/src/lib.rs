//! WENDY Crystalline Cortex: Real Science Artifacts
//! SPDX-License-Identifier: EUPL-1.2
//! Hard real-time, numerically stable telemetry processing.

/// Calculates the sample variance of a massive telemetry stream (e.g., SAR backscatter)
/// using Welford's Online Algorithm to prevent catastrophic floating-point cancellation.
/// 
/// # Safety
/// The caller must ensure `data` points to a valid array of `len` f64 elements.
#[no_mangle]
pub extern "C" fn wendy_welford_variance(data: *const f64, len: usize) -> f64 {
    if data.is_null() || len == 0 {
        return 0.0;
    }

    let slice = unsafe { std::slice::from_raw_parts(data, len) };
    
    let mut count: f64 = 0.0;
    let mut mean: f64 = 0.0;
    let mut m2: f64 = 0.0;

    // LLVM will auto-vectorize this loop in --release mode (SIMD optimization)
    for &x in slice {
        count += 1.0;
        let delta = x - mean;
        mean += delta / count;
        let delta2 = x - mean;
        m2 += delta * delta2;
    }

    if count < 2.0 {
        return 0.0;
    }
    
    // Return sample variance (Bessel's correction)
    m2 / (count - 1.0)
}

/// Base heartbeat to verify the C-FFI boundary is intact.
#[no_mangle]
pub extern "C" fn wendy_cortex_heartbeat() -> i32 {
    1
}
