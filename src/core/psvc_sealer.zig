const std = @import("std");
const Ed25519 = std.crypto.sign.Ed25519;

pub const PsvcHeader = packed struct {
    magic: [4]u8 = .{ 'P', 'S', 'V', 'C' },
    version: u8 = 2,
    precision_bits: u8,
    reserved: u16 = 0,
    payload_length: u32,
    timestamp_epoch_ms: u64,
};

pub fn sealPayload(
    allocator: std.mem.Allocator,
    payload: []const u8,
    precision_bits: u8,
    timestamp_ms: u64,
    signing_key: ?*const Ed25519.SecretKey,
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

    if (signing_key) |key| {
        const header_bytes = std.mem.asBytes(&header);
        var message = try allocator.alloc(u8, header_bytes.len + payload.len);
        defer allocator.free(message);
        @memcpy(message[0..header_bytes.len], header_bytes);
        @memcpy(message[header_bytes.len..], payload);
        
        const signature = Ed25519.sign(message, key, null);
        try file.writeAll(&signature.toBytes());
    }

    const total_size = @sizeOf(PsvcHeader) + payload.len + (if (signing_key != null) @as(usize, 64) else 0);
    std.debug.print("Sealed PSVC: {s} ({d} bytes, {d}-bit, signed={})\n", .{
        output_path, total_size, precision_bits, signing_key != null
    });
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 5) {
        std.debug.print("Usage: psvc_sealer <precision_bits> <input_file> <output_psvc>\n", .{});
        std.debug.print("Environment: WENDY_PRIVATE_KEY_SEED (hex, optional for signing)\n", .{});
        return;
    }

    const precision_bits = try std.fmt.parseInt(u8, args[1], 10);
    const input_path = args[2];
    const output_path = args[3];

    const input_file = try std.fs.cwd().openFile(input_path, .{});
    defer input_file.close();

    const payload = try input_file.readToEndAlloc(allocator, 100 * 1024 * 1024);
    defer allocator.free(payload);

    var signing_key: ?Ed25519.SecretKey = null;
    if (std.process.getEnvVarOwned(allocator, "WENDY_PRIVATE_KEY_SEED")) |seed_hex| {
        defer allocator.free(seed_hex);
        var seed: [32]u8 = undefined;
        _ = std.fmt.hexToBytes(&seed, seed_hex) catch return error.InvalidKeySeed;
        signing_key = Ed25519.SecretKey.fromSeed(seed);
    } else |_| {}

    const timestamp_ms = @as(u64, @intCast(std.time.milliTimestamp()));

    try sealPayload(
        allocator,
        payload,
        precision_bits,
        timestamp_ms,
        if (signing_key != null) &signing_key.? else null,
        output_path
    );
}