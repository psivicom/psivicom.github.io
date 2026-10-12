const std = @import("std");

pub const PsvcHeader = packed struct {
    magic: [4]u8 = .{ 'P', 'S', 'V', 'C' },
    version: u8 = 1,
    precision_bits: u8,
    reserved: u16 = 0,
    payload_length: u32,
    timestamp_epoch_ms: u64,
};

pub fn sealPayload(
    payload: []const u8,
    precision_bits: u8,
    timestamp_ms: u64,
    output_path: []const u8,
) !void {
    var header = PsvcHeader{
        .precision_bits = precision_bits,
        .payload_length = @as(u32, @intCast(payload.len)),
        .timestamp_epoch_ms = timestamp_ms,
    };

    var file = try std.fs.cwd().createFile(output_path, .{});
    defer file.close();

    try file.writeAll(std.mem.asBytes(&header));
    try file.writeAll(payload);

    std.debug.print("Sealed: {s} ({d} bytes, {d}-bit)\n", .{
        output_path,
        @sizeOf(PsvcHeader) + payload.len,
        precision_bits,
    });
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 5) {
        std.debug.print("Usage: psvc_sealer <precision_bits> <timestamp_ms> <input_file> <output_file>\n", .{});
        std.debug.print("Example: psvc_sealer 32 1697000000000 data.bin output.psvc\n", .{});
        return;
    }

    const precision_bits = try std.fmt.parseInt(u8, args[1], 10);
    const timestamp_ms = try std.fmt.parseInt(u64, args[2], 10);
    const input_path = args[3];
    const output_path = args[4];

    const input_file = try std.fs.cwd().openFile(input_path, .{});
    defer input_file.close();

    const payload = try input_file.readToEndAlloc(allocator, 100 * 1024 * 1024);
    defer allocator.free(payload);

    try sealPayload(payload, precision_bits, timestamp_ms, output_path);
}
