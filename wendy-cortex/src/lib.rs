//! WENDY Crystalline Cortex
//! SPDX-License-Identifier: EUPL-1.2
//! This module serves as the dynamic boundary for WENDY's hot-swappable native artifacts.

pub mod crystals;

/// Base heartbeat to ensure the cdylib compiles and loads correctly on initialization.
#[no_mangle]
pub extern "C" fn wendy_cortex_heartbeat() -> i32 {
    1 // Nominal
}
