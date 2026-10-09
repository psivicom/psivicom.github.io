// src/core/zulu_clock.zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");

pub fn getZuluTimestampMs() [24]u8 {
    const now_ms: i64 = std.time.milliTimestamp();
    const total_seconds: i64 = @divFloor(now_ms, @as(i64, 1000));
    const ms: u32 = @intCast(@mod(now_ms, @as(i64, 1000)));

    const days: i64 = @divFloor(total_seconds, @as(i64, 86400));
    const rem: i64 = @mod(total_seconds, @as(i64, 86400));
    
    const hour: u32 = @intCast(@divFloor(rem, @as(i64, 3600)));
    const min: u32 = @intCast(@divFloor(@mod(rem, @as(i64, 3600)), @as(i64, 60)));
    const sec: u32 = @intCast(@mod(rem, @as(i64, 60)));

    const z: i64 = days + @as(i64, 719468);
    const era: i64 = @divFloor(z, @as(i64, 146097));
    const doe: i64 = z - era * @as(i64, 146097);
    const yoe: i64 = @divFloor(
        doe - @divFloor(doe, @as(i64, 1460)) + @divFloor(doe, @as(i64, 36524)) - @divFloor(doe, @as(i64, 146096)), 
        @as(i64, 365)
    );
    const y: i64 = era * @as(i64, 400) + yoe;
    const doy: i64 = doe - (@as(i64, 365) * yoe + @divFloor(yoe, @as(i64, 4)) - @divFloor(yoe, @as(i64, 100)));
    const mp: i64 = @divFloor(@as(i64, 5) * doy + @as(i64, 2), @as(i64, 153));
    const d: i64 = doy - @divFloor(@as(i64, 153) * mp + @as(i64, 2), @as(i64, 5)) + @as(i64, 1);
    
    // BRANCHLESS MATH: All literals are explicitly cast to i64 to satisfy Zig's strict type system.
    const m: i64 = mp + @as(i64, 3) - @as(i64, 12) * @as(i64, @intFromBool(mp >= @as(i64, 10)));
    
    const final_y: u32 = @intCast(y + @as(i64, @intFromBool(m < @as(i64, 3))));
    const final_m: u32 = @intCast(m);
    const final_d: u32 = @intCast(d);

    var buf: [24]u8 = undefined;
    std.fmt.bufPrint(&buf, "{d:0>4}-{d:0>2}-{d:0>2}T{d:0>2}:{d:0>2}:{d:0>2}.{d:0>3}Z", .{
        final_y, final_m, final_d, hour, min, sec, ms,
    }) catch unreachable;
    
    return buf;
}

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    const timestamp = getZuluTimestampMs();
    try stdout.print("{s}\n", .{timestamp});
}
