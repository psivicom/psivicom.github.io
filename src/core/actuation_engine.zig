const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 3) {
        std.debug.print("Usage: actuation_engine <vector_csv> <rules_json_path>\n", .{});
        std.process.exit(1);
    }

    var vector: [16]f32 = undefined;
    var it = std.mem.tokenizeScalar(u8, args[1], ',');
    var i: usize = 0;
    while (it.next()) |token| : (i += 1)
