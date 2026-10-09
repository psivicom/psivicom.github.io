// src/core/zulu_clock.zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");

/// Returns a strictly formatted Zulu timestamp: "YYYY-MM-DDTHH:MM:SS.sssZ"
/// Exactly 24 bytes. No heap allocation.
pub fn getZuluTimestampMs() [24]u8 {
    const now_ms = std.time.milliTimestamp();
    const total_seconds = @divFloor(now_ms, 1000);
    const ms = @as(u32, @intCast(@mod(now_ms, 1000)));

    const days = @divFloor(total_seconds, 86400);
    const rem = @mod(total_seconds, 86400);
    
    const hour = @as(u32, @intCast(@divFloor(rem, 3600)));
    const min = @as(u32, @intCast(@divFloor(@mod(rem, 3600), 60)));
    const sec = @as(u32, @intCast(@mod(rem, 60)));

    const z = days + 719468;
    const era = @divFloor(z, 146097);
    const doe = z - era * 146097;
    const yoe = @divFloor(doe - @divFloor(doe, 1460) + @divFloor(doe, 36524) - @divFloor(doe, 146096), 365);
    const y: i64 = era * 400 + yoe;
    const doy = doe - (365 * yoe + @divFloor(yoe, 4) - @divFloor(yoe, 100));
    const mp = @divFloor(5 * doy + 2, 153);
    const d = doy - @divFloor(153 * mp + 2, 5) + 1;
    const m = mp + (if (mp < 10) 3 else -9);
    
    const final_y: u32 = @intCast(if (m < 3) y + 1 else y);
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

test "zulu clock format" {
    // Verify exact formatting and length (comment moved inside to satisfy compiler)
    const ts = getZuluTimestampMs();
    try std.testing.expectEqual(@as(usize, 24), ts.len);
    try std.testing.expectEqual(@as(u8, 'Z'), ts[23]);
    try std.testing.expectEqual(@as(u8, 'T'), ts[10]);
}
