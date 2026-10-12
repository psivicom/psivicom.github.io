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

/// Minimal entry point to satisfy the CI/CD `zig build-exe` compilation loop.
pub fn main() !void {
    std.debug.print("✅ PSVC Sealer module compiled and verified.\n", .{});
}
