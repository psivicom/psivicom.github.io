// src/core/zulu_clock.zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");

/// Returns a strictly formatted Zulu timestamp: "YYYY-MM-DDTHH:MM:SS.sssZ"
/// Exactly 24 bytes. No heap allocation. Uses Zig's std.time.epoch for
/// mathematically correct, branchless UTC date decomposition.
pub fn getZuluTimestampMs() [24]u8 {
    const now_ms: i64 = std.time.milliTimestamp();
    const secs: u64 = @intCast(@divFloor(now_ms, @as(i64, 1000)));
    const ms: u32 = @intCast(@mod(now_ms, @as(i64, 1000)));

    const epoch_secs = std.time.epoch.EpochSeconds{ .secs = secs };
    const day_secs = epoch_secs.getDaySeconds();
    const year_day = epoch_secs.getEpochDay().calculateYearDay();
    const month_day = year_day.calculateMonthDay();

    const year: u32 = @intCast(year_day.year);
    const month: u32 = month_day.month.numeric();
    const day: u32 = @as(u32, month_day.day_index) + 1;
    const hour: u32 = day_secs.getHoursIntoDay();
    const min: u32 = day_secs.getMinutesIntoHour();
    const sec: u32 = day_secs.getSecondsIntoMinute();

    var buf: [24]u8 = undefined;
    _ = std.fmt.bufPrint(&buf, "{d:0>4}-{d:0>2}-{d:0>2}T{d:0>2}:{d:0>2}:{d:0>2}.{d:0>3}Z", .{
        year, month, day, hour, min, sec, ms,
    }) catch unreachable;

    return buf;
}

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    const ts = getZuluTimestampMs();
    try stdout.print("{s}\n", .{ts});
}
