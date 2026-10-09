```zig
// src/core/zulu_clock.zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");

/// Returns a strictly formatted Zulu timestamp: "YYYY-MM-DDTHH:MM:SS.sssZ"
/// Exactly 24 bytes. No heap allocation.
pub fn getZuluTimestampMs() [24]u8 {
    const now_ms: i64 = std.time.milliTimestamp();
    const total_seconds: i64 = @divFloor(now_ms, 1000);
    const ms: u32 = @intCast(@mod(now_ms, 1000));

    const days: i64 = @divFloor(total_seconds, 86400);
    const rem: i64 = @mod(total_seconds, 86400);
    
    const hour: u32 = @intCast(@divFloor(rem, 3600));
    const min: u32 = @intCast(@divFloor(@mod(rem, 3600), 60));
    const sec: u32 = @intCast(@mod(rem, 60));

    // Pure mathematical UTC date calculation (Howard Hinnant's algorithm)
    const z: i64 = days + 719468;
    const era: i64 = @divFloor(z, 146097);
    const doe: i64 = z - era * 146097;
    const yoe: i64 = @divFloor(doe - @divFloor(doe, 1460) + @divFloor(doe, 36524) - @divFloor(doe, 146096), 365);
    const y: i64 = era * 400 + yoe;
    const doy: i64 = doe - (365 * yoe + @divFloor(yoe, 4) - @divFloor(yoe, 100));
    const mp: i64 = @divFloor(5 * doy + 2, 153);
    const d: i64 = doy - @divFloor(153 * mp + 2, 5) + 1;
    
    // NOTE: We must do the math inside the branches (mp + 3) rather than 
    // adding comptime literals (3) to a runtime condition, to satisfy Zig's 
    // strict comptime/runtime separation rules.
    const m: i64 = if (mp < 10) mp + 3 else mp - 9;
    
    const final_y: u32 = @intCast(if (m < 3) y + 1 else y);
    const final_m: u32 = @intCast(m);
    const final_d: u32 = @intCast(d);

    var buf: [24]u8 = undefined;
    std.fmt.bufPrint(&buf, "{d:0>4}-{d:0>2}-{d:0>2}T{d:0>2}:{d:0>2}:{d:0>2}.{d:0>3}Z", .{
        final_y, final_m, final_d, hour, min, sec, ms,
    }) catch unreachable;
    
    return buf;
}

/// CLI entry point for testing or subprocess invocation from Python/Bash
pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    const timestamp = getZuluTimestampMs();
    try stdout.print("{s}\n", .{timestamp});
}
```
