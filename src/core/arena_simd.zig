const std = @import("std");

pub const ArenaConfig = struct {
    block_size: usize = 65536,
    alignment: usize = 64,
};

pub const SimdVector = @Vector(16, f32);

pub const ArenaSimd = struct {
    allocator: std.mem.Allocator,
    block_size: usize,
    alignment: usize,
    current_block: ?*Block,
    blocks_allocated: usize,
    bytes_allocated: usize,

    const Block = struct {
        next: ?*Block,
        capacity: usize,
        used: usize,
        data: [*]u8,

        fn init(allocator: std.mem.Allocator, capacity: usize, alignment: usize) !*Block {
            const total_size = @sizeOf(Block) + capacity + alignment;
            const raw = try allocator.alignedAlloc(u8, std.mem.Alignment.fromByteUnits(alignment), total_size);
            const block = @as(*Block, @ptrCast(@alignCast(raw.ptr)));
            block.next = null;
            block.capacity = capacity;
            block.used = 0;
            block.data = raw.ptr + @sizeOf(Block);
            return block;
        }

        fn deinit(self: *Block, allocator: std.mem.Allocator) void {
            const raw_ptr = @as([*]u8, @ptrCast(self));
            const total_size = @sizeOf(Block) + self.capacity + 64;
            allocator.free(raw_ptr[0..total_size]);
        }
    };

    pub fn init(allocator: std.mem.Allocator, config: ArenaConfig) ArenaSimd {
        return ArenaSimd{
            .allocator = allocator,
            .block_size = config.block_size,
            .alignment = config.alignment,
            .current_block = null,
            .blocks_allocated = 0,
            .bytes_allocated = 0,
        };
    }

    pub fn deinit(self: *ArenaSimd) void {
        var curr = self.current_block;
        while (curr) |block| {
            const next = block.next;
            block.deinit(self.allocator);
            curr = next;
        }
        self.current_block = null;
        self.blocks_allocated = 0;
        self.bytes_allocated = 0;
    }

    pub fn alloc(self: *ArenaSimd, comptime T: type, count: usize) ![]T {
        const size = @sizeOf(T) * count;
        const align_val = @max(self.alignment, @alignOf(T));
        const ptr = try self.rawAlloc(size, align_val);
        return @as([*]T, @ptrCast(@alignCast(ptr)))[0..count];
    }

    pub fn rawAlloc(self: *ArenaSimd, size: usize, alignment: usize) ![*]u8 {
        const aligned_size = (size + (alignment - 1)) & ~(alignment - 1);

        if (self.current_block) |block| {
            const current_ptr = @intFromPtr(block.data) + block.used;
            const misaligned = current_ptr % alignment;
            const adjustment = if (misaligned == 0) 0 else (alignment - misaligned);
            const total_needed = aligned_size + adjustment;

            if (block.used + total_needed <= block.capacity) {
                block.used += adjustment;
                const allocated_ptr = block.data + block.used;
                block.used += aligned_size;
                self.bytes_allocated += total_needed;
                return allocated_ptr;
            }
        }

        const new_capacity = @max(self.block_size, aligned_size + alignment);
        const new_block = try Block.init(self.allocator, new_capacity, self.alignment);
        new_block.next = self.current_block;
        self.current_block = new_block;
        self.blocks_allocated += 1;

        const current_ptr = @intFromPtr(new_block.data);
        const misaligned = current_ptr % alignment;
        const adjustment = if (misaligned == 0) 0 else (alignment - misaligned);
        new_block.used += adjustment + aligned_size;
        self.bytes_allocated += new_block.used;

        return new_block.data + adjustment;
    }

    pub fn processSimdPipeline(self: *ArenaSimd, data: []f32, factor: f32) ![]f32 {
        const result = try self.alloc(f32, data.len);
        const factor_vec: SimdVector = @splat(factor);
        
        var i: usize = 0;
        const chunks = data.len / 16;

        while (i < chunks * 16) : (i += 16) {
            const chunk_ptr = data[i..][0..16].ptr;
            const vec: SimdVector = @as(*SimdVector, @ptrCast(@alignCast(chunk_ptr))).*;
            const res_vec = vec * factor_vec;
            @as(*SimdVector, @ptrCast(@alignCast(result[i..].ptr))).* = res_vec;
        }

        while (i < data.len) : (i += 1) {
            result[i] = data[i] * factor;
        }

        return result;
    }
};

export fn create_arena(block_size: usize, alignment: usize) *ArenaSimd {
    const allocator = std.heap.c_allocator;
    const arena = allocator.create(ArenaSimd) catch @panic("OOM");
    arena.* = ArenaSimd.init(allocator, ArenaConfig{
        .block_size = block_size,
        .alignment = alignment,
    });
    return arena;
}

export fn destroy_arena(arena: *ArenaSimd) void {
    const allocator = arena.allocator;
    arena.deinit();
    allocator.destroy(arena);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    var arena = ArenaSimd.init(allocator, ArenaConfig{
        .block_size = 65536,
        .alignment = 64,
    });
    defer arena.deinit();

    const data = [_]f32{1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0};
    const result = try arena.processSimdPipeline(&data, 2.0);

    std.debug.print("⚡ SIMD Pipeline: Processed {} elements\n", .{result.len});
}
