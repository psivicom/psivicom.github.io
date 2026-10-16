const std = @import("std");
const Sha256 = std.crypto.hash.sha2.Sha256;
const Ed25519 = std.crypto.sign.Ed25519;

pub const Precision = enum {
    bits_4,
    bits_8,
    bits_16,
    bits_32,
    bits_64,
    bits_128,
};

pub fn PrecisionType(comptime p: Precision) type {
    return switch (p) {
        .bits_4 => u4,
        .bits_8 => u8,
        .bits_16 => f16,
        .bits_32 => f32,
        .bits_64 => f64,
        .bits_128 => f128,
    };
}

pub const PsvcHeader = packed struct {
    magic: [4]u8 = .{ 'P', 'S', 'V', 'C' },
    version: u8 = 2,
    precision_bits: u8,
    reserved: u16 = 0,
    payload_length: u32,
    timestamp_epoch_ms: u64,
};

pub fn VectorState(comptime P: Precision) type {
    const T = PrecisionType(P);
    
    return struct {
        dimension: usize,
        data: []T,
        allocator: std.mem.Allocator,

        pub fn init(allocator: std.mem.Allocator, dimension: usize) !@This() {
            const data = try allocator.alloc(T, dimension);
            @memset(data, 0);
            return @This(){
                .dimension = dimension,
                .data = data,
                .allocator = allocator,
            };
        }

        pub fn deinit(self: *@This()) void {
            self.allocator.free(self.data);
        }

        pub fn loadFromFile(self: *@This(), file_path: []const u8) !void {
            const file = try std.fs.cwd().openFile(file_path, .{});
            defer file.close();
            
            const bytes = try file.readToEndAlloc(self.allocator, 100 * 1024 * 1024);
            defer self.allocator.free(bytes);
            
            const expected_size = self.dimension * @sizeOf(T);
            if (bytes.len != expected_size) {
                return error.SizeMismatch;
            }
            
            @memcpy(self.data, std.mem.bytesAsSlice(T, bytes));
        }

        pub fn applyTransformation(self: *@This(), matrix: []const T) !void {
            std.debug.assert(matrix.len == self.dimension * self.dimension);
            
            const temp = try self.allocator.alloc(T, self.dimension);
            defer self.allocator.free(temp);

            var i: usize = 0;
            while (i < self.dimension) : (i += 1) {
                var sum: T = 0;
                var j: usize = 0;
                while (j < self.dimension) : (j += 1) {
                    sum += matrix[i * self.dimension + j] * self.data[j];
                }
                temp[i] = sum;
            }

            @memcpy(self.data, temp);
        }

        pub fn getRawBytes(self: @This()) []const u8 {
            return std.mem.sliceAsBytes(self.data);
        }
    };
}

pub fn sealAsPSVC(
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

    if (args.len < 6) {
        std.debug.print("Usage: vector_engine <precision> <dimension> <input_vector> <matrix_file> <output_psvc>\n", .{});
        std.debug.print("Environment: WENDY_PRIVATE_KEY_SEED (hex, optional for signing)\n", .{});
        return;
    }

    const precision_str = args[1];
    const dimension = try std.fmt.parseInt(usize, args[2], 10);
    const input_path = args[3];
    const matrix_path = args[4];
    const output_path = args[5];

    const precision = if (std.mem.eql(u8, precision_str, "4")) Precision.bits_4
        else if (std.mem.eql(u8, precision_str, "8")) Precision.bits_8
        else if (std.mem.eql(u8, precision_str, "16")) Precision.bits_16
        else if (std.mem.eql(u8, precision_str, "32")) Precision.bits_32
        else if (std.mem.eql(u8, precision_str, "64")) Precision.bits_64
        else if (std.mem.eql(u8, precision_str, "128")) Precision.bits_128
        else return error.InvalidPrecision;

    const precision_bits: u8 = switch (precision) {
        .bits_4 => 4, .bits_8 => 8, .bits_16 => 16,
        .bits_32 => 32, .bits_64 => 64, .bits_128 => 128,
    };

    var signing_key: ?Ed25519.SecretKey = null;
    if (std.process.getEnvVarOwned(allocator, "WENDY_PRIVATE_KEY_SEED")) |seed_hex| {
        defer allocator.free(seed_hex);
        var seed: [32]u8 = undefined;
        _ = std.fmt.hexToBytes(&seed, seed_hex) catch return error.InvalidKeySeed;
        signing_key = Ed25519.SecretKey.fromSeed(seed);
    } else |_| {}

    const timestamp_ms = @as(u64, @intCast(std.time.milliTimestamp()));

    switch (precision) {
        .bits_32 => {
            var state = try VectorState(.bits_32).init(allocator, dimension);
            defer state.deinit();
            
            try state.loadFromFile(input_path);
            
            const matrix_file = try std.fs.cwd().openFile(matrix_path, .{});
            defer matrix_file.close();
            const matrix_bytes = try matrix_file.readToEndAlloc(allocator, 100 * 1024 * 1024);
            defer allocator.free(matrix_bytes);
            const matrix = std.mem.bytesAsSlice(f32, matrix_bytes);
            
            try state.applyTransformation(matrix);
            
            try sealAsPSVC(
                allocator,
                state.getRawBytes(),
                precision_bits,
                timestamp_ms,
                if (signing_key != null) &signing_key.? else null,
                output_path
            );
        },
        .bits_64 => {
            var state = try VectorState(.bits_64).init(allocator, dimension);
            defer state.deinit();
            
            try state.loadFromFile(input_path);
            
            const matrix_file = try std.fs.cwd().openFile(matrix_path, .{});
            defer matrix_file.close();
            const matrix_bytes = try matrix_file.readToEndAlloc(allocator, 100 * 1024 * 1024);
            defer allocator.free(matrix_bytes);
            const matrix = std.mem.bytesAsSlice(f64, matrix_bytes);
            
            try state.applyTransformation(matrix);
            
            try sealAsPSVC(
                allocator,
                state.getRawBytes(),
                precision_bits,
                timestamp_ms,
                if (signing_key != null) &signing_key.? else null,
                output_path
            );
        },
        else => {
            std.debug.print("Precision {s} not yet implemented for CLI\n", .{precision_str});
        }
    }
} 
