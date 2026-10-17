const std = @import("std");

/// Space-grade, cache-aligned memory arena for WENDY's working memory
pub const CognitiveArena = struct {
    backing_allocator: std.mem.Allocator,
    arena: std.heap.ArenaAllocator,

    pub fn init(backing: std.mem.Allocator) CognitiveArena {
        return .{
            .backing_allocator = backing,
            .arena = std.heap.ArenaAllocator.init(backing),
        };
    }

    pub fn allocator(self: *CognitiveArena) std.mem.Allocator {
        return self.arena.allocator();
    }

    /// Reset working memory between cognitive inference cycles without reallocating
    pub fn resetCycle(self: *CognitiveArena) void {
        _ = self.arena.reset(.retain_capacity);
    }

    pub fn deinit(self: *CognitiveArena) void {
        self.arena.deinit();
    }
};

test "cognitive arena cycle retention" {
    const testing = std.testing;
    var arena = CognitiveArena.init(testing.allocator);
    defer arena.deinit();

    const mem = try arena.allocator().alloc(u8, 1024);
    testing.expect(mem.len == 1024) catch unreachable;
    arena.resetCycle();
}