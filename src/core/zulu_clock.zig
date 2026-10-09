// src/core/zulu_clock.zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");

pub fn getZuluTimestampMs() [24]u8 {
    const now_ms = std.time.milliTimestamp();
    const total_secs: u64 = @intCast(@divFloor(now_ms, 1000));
    const ms: u32 = @intCast(@mod(now_ms, 1000));

    const epoch_secs = std.time.epoch.EpochSeconds{ .secs = total_secs };
    const day_secs = epoch_secs.getDaySeconds();
    const year_day = epoch_secs.getEpochDay().calculateYearDay();
    const month_day = year_day.calculateMonthDay();

    const year = year_day.year;
    const month = @intFromEnum(month_day.month);
    const day = month_day.day_index + 1;

    const hour = day_secs.getHoursIntoDay();
    const min = day_secs.getMinutesIntoHour();
    const sec = day_secs.getSecondsIntoMinute();

    var buf: [24]u8 = undefined;
    _ = std.fmt.bufPrint(&buf, "{d:0>4}-{d:0>2}-{d:0>2}T{d:0>2}:{d:0>2}:{d:0>2}.{d:0>3}Z", .{
        year, month, day, hour, min, sec, ms,
    }) catch unreachable;

    return buf;
}

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    const timestamp = getZuluTimestampMs();
    try stdout.print("{s}\n", .{timestamp});
}
