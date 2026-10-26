const std = @import("std");

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

    const mem = arena.allocator().alloc(u8, 1024) catch unreachable;
    testing.expect(mem.len == 1024) catch unreachable;
    arena.resetCycle();
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    
    var arena = CognitiveArena.init(gpa.allocator());
    defer arena.deinit();

    const mem = try arena.allocator().alloc(u8, 1024);
    _ = mem;
    
    arena.resetCycle();
    
    std.debug.print("🧠 Cognitive Arena: Cycle complete\n", .{});
}
