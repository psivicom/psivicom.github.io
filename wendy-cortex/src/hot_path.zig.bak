// wendy-cortex/src/hot_path.zig
// SPDX-License-Identifier: EUPL-1.2
// Hot path for mathematical operations (optimized by WENDY)

const std = @import("std");

/// Compute mean of float array (baseline implementation)
pub fn mean(values: []const f64) f64 {
    if (values.len == 0) return 0.0;
    
    var sum: f64 = 0.0;
    for (values) |val| {
        sum += val;
    }
    return sum / @as(f64, @floatFromInt(values.len));
}

/// Compute variance using Welford's algorithm (numerically stable)
pub fn variance(values: []const f64) f64 {
    if (values.len < 2) return 0.0;
    
    var count: usize = 0;
    var mean_val: f64 = 0.0;
    var m2: f64 = 0.0;
    
    for (values) |val| {
        count += 1;
        const delta = val - mean_val;
        mean_val += delta / @as(f64, @floatFromInt(count));
        const delta2 = val - mean_val;
        m2 += delta * delta2;
    }
    
    return m2 / @as(f64, @floatFromInt(count - 1));
}

/// Dot product of two vectors
pub fn dot_product(a: []const f64, b: []const f64) f64 {
    if (a.len != b.len) return 0.0;
    
    var sum: f64 = 0.0;
    for (a, 0..) |val, idx| {
        sum += val * b[idx];
    }
    return sum;
}

// Export for C FFI
comptime {
    @export(mean, .{ .name = "wendy_mean", .linkage = .strong });
    @export(variance, .{ .name = "wendy_variance", .linkage = .strong });
    @export(dot_product, .{ .name = "wendy_dot_product", .linkage = .strong });
}
