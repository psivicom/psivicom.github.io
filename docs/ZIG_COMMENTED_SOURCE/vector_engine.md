# WENDY Bare-Metal Vector Engine

**File Path:** `src/core/vector_engine.zig`

## 🧠 Architectural Overview

This module represents the foundational cognitive state of WENDY. Unlike high-level languages that abstract memory management and enforce garbage collection pauses, this Zig implementation provides **comptime-generic, bare-metal vector operations** optimized for direct VRAM mapping.

The core innovation is **Dynamic Precision Scaling**. WENDY does not default to 32-bit floats. She dynamically selects the exact bit-width (4, 8, 16, 32, 64, or 128) required for the task at compile time. This maximizes SIMD (Single Instruction, Multiple Data) throughput and minimizes memory bandwidth bottlenecks, allowing her to process exponentially more data in the same physical memory footprint.

---

## 📜 Fully Commented Source Code

```zig
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

const std = @import("std");
// CRITICAL FIX for Zig 0.11.0: Sha256 is now inside the sha2 namespace.
// This ensures cryptographic hashing of the cognitive state for sovereign sealing.
const Sha256 = std.crypto.hash.sha2.Sha256;

/// Supported cognitive precisions for VRAM optimization.
/// 4-bit and 8-bit are used for quantized inference (maximum density, fastest SIMD).
/// 16, 32, 64, 128 are used for floating-point state and high-fidelity scientific math.
pub const Precision = enum {
    bits_4,
    bits_8,
    bits_16,
    bits_32,
    bits_64,
    bits_128,
};

/// Maps a Precision enum to the actual Zig type at compile time.
/// Because this returns 'type' (a compile-time-only construct), 
/// the parameter 'p' MUST be marked as 'comptime'. This ensures zero runtime 
/// overhead for type resolution; the compiler generates dedicated machine code 
/// for each precision branch.
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

/// Represents WENDY's bare-metal cognitive state in memory.
/// Generic over precision (comptime P) to allow maximum VRAM efficiency.
pub fn VectorState(comptime P: Precision) type {
    const T = PrecisionType(P);
    
    return struct {
        dimension: usize,
        data: []T, // Slice backed by allocator (simulating direct VRAM access)
        allocator: std.mem.Allocator,

        /// Initializes a zeroed vector state to prevent data leakage from previous cognitive cycles.
        pub fn init(allocator: std.mem.Allocator, dimension: usize) !@This() {
            const data = try allocator.alloc(T, dimension);
            @memset(data, 0); 
            return @This(){
                .dimension = dimension,
                .data = data,
                .allocator = allocator,
            };
        }

        /// Explicitly frees the allocated memory. No garbage collector needed.
        pub fn deinit(self: *@This()) void {
            self.allocator.free(self.data);
        }

        /// Applies a deterministic linear transformation (The "Cognitive Operation").
        /// The Zig compiler will automatically unroll and vectorize this loop 
        /// into architecture-specific SIMD instructions (e.g., AVX-512 for f32/f64, 
        /// or packed integer ops for u4/u8) based on the comptime type T.
        pub fn applyTransformation(self: *@This(), matrix: []const T) !void {
            std.debug.assert(matrix.len == self.dimension * self.dimension);
            
            // Allocate temporary buffer for the transformation result
            const temp = try self.allocator.alloc(T, self.dimension);
            defer self.allocator.free(temp); // Guaranteed cleanup

            var i: usize = 0;
            while (i < self.dimension) : (i += 1) {
                var sum: T = 0;
                var j: usize = 0;
                while (j < self.dimension) : (j += 1) {
                    sum += matrix[i * self.dimension + j] * self.data[j];
                }
                temp[i] = sum;
            }

            // Zero-copy update back to the primary state buffer ("VRAM")
            @memcpy(self.data, temp);
        }

        /// Computes SHA-256 hash of the raw byte state for PSVC cryptographic sealing.
        /// This guarantees that the mathematical truth can be verified before and after transit.
        pub fn hashState(self: @This()) [Sha256.digest_length]u8 {
            const bytes = std.mem.sliceAsBytes(self.data);
            var hash: [Sha256.digest_length]u8 = undefined;
            Sha256.hash(bytes, &hash, .{});
            return hash;
        }

        /// Returns the raw byte payload for sovereign encapsulation.
        /// Uses sliceAsBytes to provide a direct pointer to the memory without 
        /// any serialization overhead, ready for immediate PSVC sealing.
        pub fn getRawBytes(self: @This()) []const u8 {
            return std.mem.sliceAsBytes(self.data);
        }
    };
}

/// Minimal entry point to satisfy the CI/CD `zig build-exe` compilation loop.
/// Proves the module compiles successfully as a standalone executable.
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    // DEMONSTRATION 1: Ultra-fast 4-bit quantized state (Maximum VRAM density)
    const dim_4: usize = 6000; // 4x the dimension of 32-bit in the same memory!
    var state_4 = try VectorState(.bits_4).init(allocator, dim_4);
    defer state_4.deinit();
    
    var i: usize = 0;
    while (i < dim_4) : (i += 1) {
        state_4.data[i] = @as(u4, @intCast(i % 15));
    }
    
    std.debug.print("4-bit State: {d} dims, {d} bytes.\n", .{ dim_4, state_4.getRawBytes().len });

    // DEMONSTRATION 2: High-fidelity 64-bit scientific state
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
