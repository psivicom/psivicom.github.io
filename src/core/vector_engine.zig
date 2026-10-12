const std = @import("std");
const Sha256 = std.crypto.hash.sha2.Sha256;

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

        pub fn saveToFile(self: @This(), file_path: []const u8) !void {
            const file = try std.fs.cwd().createFile(file_path, .{});
            defer file.close();
            
            const bytes = std.mem.sliceAsBytes(self.data);
            try file.writeAll(bytes);
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

        pub fn hashState(self: @This()) [Sha256.digest_length]u8 {
            const bytes = std.mem.sliceAsBytes(self.data);
            var hash: [Sha256.digest_length]u8 = undefined;
            Sha256.hash(bytes, &hash, .{});
            return hash;
        }
    };
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 6) {
        std.debug.print("Usage: vector_engine <precision> <dimension> <input_vector> <matrix_file> <output_vector>\n", .{});
        std.debug.print("Example: vector_engine 32 1500 state.bin matrix.bin result.bin\n", .{});
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
            try state.saveToFile(output_path);
            
            const hash = state.hashState();
            std.debug.print("Transformed: {s} -> {s} (SHA256: {s})\n", .{
                input_path, output_path, std.fmt.fmtSliceHexLower(&hash)
            });
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
            try state.saveToFile(output_path);
            
            const hash = state.hashState();
            std.debug.print("Transformed: {s} -> {s} (SHA256: {s})\n", .{
                input_path, output_path, std.fmt.fmtSliceHexLower(&hash)
            });
        },
        else => {
            std.debug.print("Precision {s} not yet implemented for CLI\n", .{precision_str});
        }
    }
}
