# WENDY Bare-Metal Vector Engine (`src/core/vector_engine.zig`)

## Architectural Overview
This module represents the foundational cognitive state of WENDY. Unlike high-level languages that abstract memory management, this Zig implementation provides **comptime-generic, bare-metal vector operations** optimized for direct VRAM mapping. 

The core innovation is **Dynamic Precision Scaling**. WENDY does not default to 32-bit floats. She dynamically selects the exact bit-width (4, 8, 16, 32, 64, or 128) required for the task, maximizing SIMD throughput and minimizing memory bandwidth bottlenecks.

## Full Commented Source

```zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");
const Sha256 = std.crypto.hash.Sha256;

/// Supported cognitive precisions for VRAM optimization.
/// 4-bit and 8-bit are used for quantized inference (maximum density).
/// 16, 32, 64, 128 are used for floating-point state and high-fidelity math.
pub const Precision = enum {
    bits_4,
    bits_8,
    bits_16,
    bits_32,
    bits_64,
    bits_128,
};

/// Maps a Precision enum to the actual Zig type at compile time.
/// This ensures zero runtime overhead for type resolution.
pub fn PrecisionType(p: Precision) type {
    return switch (p) {
        .bits_4 => u4,
        .bits_8 => u8,
        .bits_16 => f16,
        .bits_32 => f32,
        .bits_64 => f64,
        .bits_128 => f128,
    };
}

/// Represents WENDY's bare-metal cognitive state in memory.
/// Generic over precision to allow maximum VRAM efficiency.
pub fn VectorState(comptime P: Precision) type {
    const T = PrecisionType(P);
    
    return struct {
        dimension: usize,
        data: []T, // Slice backed by allocator (simulating direct VRAM access)
        allocator: std.mem.Allocator,

        pub fn init(allocator: std.mem.Allocator, dimension: usize) !@This() {
            const data = try allocator.alloc(T, dimension);
            @memset(data, 0); // Zero-initialize to prevent data leakage from previous states
            return @This(){
                .dimension = dimension,
                .data = data,
                .allocator = allocator,
            };
        }

        pub fn deinit(self: *@This()) void {
            self.allocator.free(self.data);
        }

        /// Applies a deterministic linear transformation (The "Cognitive Operation").
        /// The Zig compiler will automatically unroll and vectorize this loop 
        /// into architecture-specific SIMD instructions (e.g., AVX-512 for f32/f64, 
        /// or packed integer ops for u4/u8).
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

            // Zero-copy update back to the primary state buffer
            @memcpy(self.data, temp);
        }

        /// Computes SHA-256 hash of the raw byte state for PSVC cryptographic sealing.
        pub fn hashState(self: @This()) [Sha256.digest_length]u8 {
            const bytes = std.mem.sliceAsBytes(self.data);
            var hash: [Sha256.digest_length]u8 = undefined;
            Sha256.hash(bytes, &hash, .{});
            return hash;
        }

        /// Returns the raw byte payload for sovereign encapsulation.
        pub fn getRawBytes(self: @This()) []const u8 {
            return std.mem.sliceAsBytes(self.data);
        }
    };
}
