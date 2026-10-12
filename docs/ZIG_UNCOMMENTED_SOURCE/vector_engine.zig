const std = @import("std");
// CRITICAL FIX for Zig 0.11.0: Sha256 is now inside the sha2 namespace
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

        pub fn getRawBytes(self: @This()) []const u8 {
            return std.mem.sliceAsBytes(self.data);
        }
    };
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const dim_4: usize = 6000;
    var state_4 = try VectorState(.bits_4).init(allocator, dim_4);
    defer state_4.deinit();
    
    var i: usize = 0;
    while (i < dim_4) : (i += 1) {
        state_4.data[i] = @as(u4, @intCast(i % 15));
    }
    
    std.debug.print("4-bit State: {d} dims, {d} bytes.\n", .{ dim_4, state_4.getRawBytes().len });

    const dim_64: usize = 1500;
    var state_64 = try VectorState(.bits_64).init(allocator, dim_64);
    defer state_64.deinit();

    var j: usize = 0;
    while (j < dim_64) : (j += 1) {
        state_64.data[j] = @as(f64, @floatFromInt(j)) * 0.001;
    }

    const hash_64 = state_64.hashState();
    std.debug.print("64-bit State: {d} dims, {d} bytes. Hash: {s}\n", .{
        dim_64, state_64.getRawBytes().len, std.fmt.fmtSliceHexLower(&hash_64)
    });
}
