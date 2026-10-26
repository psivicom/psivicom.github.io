const std = @import("std");

pub const VectorState = struct {
    data: [16]f32,
    
    pub fn fromCsv(csv: []const u8) !VectorState {
        var state: VectorState = undefined;
        var it = std.mem.tokenizeScalar(u8, csv, ',');
        var i: usize = 0;
        while (it.next()) |token| : (i += 1) {
            if (i < 16) {
                state.data[i] = try std.fmt.parseFloat(f32, token);
            }
        }
        return state;
    }

    pub fn normalize(self: *VectorState) void {
        var magnitude: f32 = 0.0;
        for (self.data) |v| {
            magnitude += v * v;
        }
        magnitude = @sqrt(magnitude);
        if (magnitude > 0.0) {
            for (&self.data) |*v| {
                v.* /= magnitude;
            }
        }
    }
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 2) {
        std.debug.print("Usage: vector_engine <csv_data>\n", .{});
        return;
    }

    var state = try VectorState.fromCsv(args[1]);
    state.normalize();
    
    std.debug.print("👁️ Sensory Input Normalized\n", .{});
}
