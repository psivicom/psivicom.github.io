<!--
  Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM
  SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Zulu Clock: Commented Source Reference

This document contains the fully annotated source code for the PSIVI AETHER Mesh Zulu Clock utility. 

**Purpose:** Generates strict RFC 3339 UTC timestamps with millisecond precision (`YYYY-MM-DDTHH:MM:SS.sssZ`).  
**Design:** Pure Zig implementation using the standard library for mathematically correct, branchless UTC date decomposition. Zero `libc` dependencies, ensuring ultra-fast, deterministic execution on pico-compute edge nodes.

```zig
// src/core/zulu_clock.zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");

/// Returns a strictly formatted Zulu timestamp: "YYYY-MM-DDTHH:MM:SS.sssZ"
/// Exactly 24 bytes. No heap allocation. Uses Zig's std.time.epoch for
/// mathematically correct, branchless UTC date decomposition.
pub fn getZuluTimestampMs() [24]u8 {
    // Get current UTC time in milliseconds since Unix epoch
    const now_ms: i64 = std.time.milliTimestamp();
    
    // Split into whole seconds and remaining milliseconds
    const secs: u64 = @intCast(@divFloor(now_ms, @as(i64, 1000)));
    const ms: u32 = @intCast(@mod(now_ms, @as(i64, 1000)));

    // Use Zig's standard library for all calendar math.
    // This avoids manual algorithm implementation and eliminates 
    // all comptime/runtime mixing issues.
    const epoch_secs = std.time.epoch.EpochSeconds{ .secs = secs };
    const day_secs = epoch_secs.getDaySeconds();
    const year_day = epoch_secs.getEpochDay().calculateYearDay();
    const month_day = year_day.calculateMonthDay();

    // Extract individual components with safe type casts
    const year: u32 = @intCast(year_day.year);
    const month: u32 = month_day.month.numeric();
    const day: u32 = @as(u32, month_day.day_index) + 1;
    const hour: u32 = day_secs.getHoursIntoDay();
    const min: u32 = day_secs.getMinutesIntoHour();
    const sec: u32 = day_secs.getSecondsIntoMinute();

    // Format into fixed-size buffer: "YYYY-MM-DDTHH:MM:SS.sssZ"
    var buf: [24]u8 = undefined;
    _ = std.fmt.bufPrint(&buf, "{d:0>4}-{d:0>2}-{d:0>2}T{d:0>2}:{d:0>2}:{d:0>2}.{d:0>3}Z", .{
        year, month, day, hour, min, sec, ms,
    }) catch unreachable;

    return buf;
}

/// CLI entry point for testing or subprocess invocation from Python/Bash
pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    const ts = getZuluTimestampMs();
    try stdout.print("{s}\n", .{ts});
}
