const std = @import("std");
pub const PSVCHeader = extern struct { magic: [4]u8, version: u8, precision_bits: u8, reserved: u16, payload_length: u32, timestamp_epoch_ms: u64 };
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);
    if (args.len < 4) return;
    const input_file = try std.fs.cwd().openFile(args[2], .{});
    defer input_file.close();
    const payload = try input_file.readToEndAlloc(allocator, 10 * 1024 * 1024);
    defer allocator.free(payload);
    var header = PSVCHeader{ .magic = .{ 'P', 'S', 'V', 'C' }, .version = 2, .precision_bits = try std.fmt.parseInt(u8, args[1], 10), .reserved = 0, .payload_length = @as(u32, @intCast(payload.len)), .timestamp_epoch_ms = @as(u64, @intCast(std.time.milliTimestamp())) };
    const out_file = try std.fs.cwd().createFile(args[3], .{});
    defer out_file.close();
    try out_file.writeAll(std.mem.asBytes(&header));
    try out_file.writeAll(payload);
    std.debug.print("🔒 Memory Sealed.\\n", .{});
}
