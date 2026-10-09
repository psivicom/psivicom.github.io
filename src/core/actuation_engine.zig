// src/core/actuation_engine.zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");

// Simple rule evaluator for 16-dim float32 vector
// Index mapping: 0=phase, 1=intensity, 2=defense_weight, 3=explore_weight, 4=stress_accumulator, 5=conscious_mass
fn evaluateRule(rule_condition: []const u8, vector: [16]f32) bool {
    // Note: In a full production build, this would use a proper AST parser or 
    // pre-compiled function pointers. For this MVP, we use simple string matching 
    // for demonstration of the bare-metal evaluation concept.
    
    const intensity = vector[1];
    const stress = vector[4];
    const defense = vector[2];

    if (std.mem.indexOf(u8, rule_condition, "stress_accumulator >= 0.75") != null) {
        return stress >= 0.75;
    }
    if (std.mem.indexOf(u8, rule_condition, "intensity >= 0.85") != null and std.mem.indexOf(u8, rule_condition, "stress_accumulator < 0.75") != null) {
        return intensity >= 0.85 and stress < 0.75;
    }
    if (std.mem.indexOf(u8, rule_condition, "defense_weight >= 0.80") != null) {
        return defense >= 0.80;
    }
    
    return false;
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 3) {
        std.debug.print("Usage: actuation_engine <vector_csv> <rules_json_path>\n", .{});
        std.process.exit(1);
    }

    // 1. Parse the 16-dim float32 vector from CSV string
    var vector: [16]f32 = undefined;
    var it = std.mem.tokenizeScalar(u8, args[1], ',');
    var i: usize = 0;
    while (it.next()) |token| : (i += 1) {
        if (i < 16) {
            vector[i] = try std.fmt.parseFloat(f32, token);
        }
    }

    // 2. Read the rules JSON file
    const rules_file = try std.fs.cwd().openFile(args[2], .{});
    defer rules_file.close();
    const rules_json = try rules_file.readToEndAlloc(allocator, 1024 * 1024);
    defer allocator.free(rules_json);

    // 3. Parse JSON and evaluate (Simplified for MVP)
    // In production, use std.json.parse for robust AST traversal
    var matched_commands = std.ArrayList([]const u8).init(allocator);
    defer matched_commands.deinit();

    // Hardcoded MVP evaluation to prove bare-metal speed concept
    // A full implementation would dynamically parse the JSON array of rules
    if (vector[4] >= 0.75) {
        try matched_commands.append("{\"action\":\"ACTIVATE_COOLING\",\"target\":\"apiary_hive_01\",\"priority\":\"CRITICAL\"}");
    }
    if (vector[1] >= 0.85 and vector[4] < 0.75) {
        try matched_commands.append("{\"action\":\"OPEN_ENTRANCE\",\"target\":\"apiary_hive_01\",\"priority\":\"HIGH\"}");
    }
    if (vector[2] >= 0.80) {
        try matched_commands.append("{\"action\":\"ENABLE_LIDAR_SCAN\",\"target\":\"apiary_perimeter\",\"priority\":\"HIGH\"}");
    }

    // 4. Output matched commands as JSON array
    std.debug.print("[", .{});
    for (matched_commands.items, 0..) |cmd, index| {
        std.debug.print("{s}", .{cmd});
        if (index < matched_commands.items.len - 1) {
            std.debug.print(",", .{});
        }
    }
    std.debug.print("]\n", .{});
}
