#!/bin/bash
# WENDY Zig Hot Path Bootstrap
# SPDX-License-Identifier: EUPL-1.2

mkdir -p ../src

cat > ../src/hot_path.zig << 'ZIG_EOF'
// WENDY Hot Path (Bootstrapped Baseline)
// SPDX-License-Identifier: EUPL-1.2
const std = @import("std");

pub fn process_telemetry(data: []const f64) f64 {
    var sum: f64 = 0.0;
    for (data) |val| { sum += val; }
    return sum / @as(f64, @floatFromInt(data.len));
}

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("⚡ WENDY Hot Path (Zig) initializing...\n", .{});
    var buffer: [10000]f64 = undefined;
    var i: usize = 0;
    while (i < 10000) : (i += 1) { buffer[i] = @as(f64, @floatFromInt(i)); }
    const start = std.time.nanoTimestamp();
    const mean = process_telemetry(&buffer);
    const end = std.time.nanoTimestamp();
    const elapsed_ns = end - start;
    try stdout.print("✅ Zig Hot Path: Processed 10,000 points in {} ns (Mean: {d:.4})\n", .{elapsed_ns, mean});
}
ZIG_EOF

echo "✅ Zig hot path created at ../src/hot_path.zig"
