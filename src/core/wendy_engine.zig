const std = @import("std");

const PSVC_MAGIC = "PSVC";
const MAX_EVOLUTION_STEPS = 1000;

const PSVCHeader = extern struct {
    magic: [4]u8,
    version: u16,
    payload_len: u32,
    state_hash: [32]u8,
};

const CognitiveCore = struct {
    pub fn symbolicTranslate(state: []u8) void {
        const vortex_map = [_]u8{ 0, 1, 2, 4, 8, 7, 5, 1, 2, 4 };
        for (state) |*byte| {
            const mod9 = @as(u8, @intCast(byte.* % 9));
            byte.* = (byte.* & 0xF0) | vortex_map[mod9];
        }
    }

    pub fn topologicalSift(state: []u8) void {
        if (state.len < 3) return;
        for (1..state.len - 1) |i| {
            const left = state[i - 1];
            const center = state[i];
            const right = state[i + 1];
            state[i] = (left ^ center) ^ (right & 0x55);
        }
    }

    pub fn generativeMutate(state: []u8) void {
        for (state) |*byte| {
            byte.* = (byte.* << 1) | (byte.* >> 7);
            byte.* ^= 0xA5;
        }
    }

    pub fn introspect(state: []u8) bool {
        var hash: [32]u8 = undefined;

        std.crypto.hash.Sha256.hash(state, &hash, .{});
        const zero: [32]u8 = .{0} ** 32;
        return std.mem.eql(u8, &hash, &zero);
    }

    pub fn evolve(allocator: std.mem.Allocator, initial_state: []u8) ![]u8 {
 
        const current_state = try allocator.dupe(u8, initial_state);
        defer allocator.free(current_state);

        var step: usize = 0;
        while (step < MAX_EVOLUTION_STEPS) : (step += 1) {
            symbolicTranslate(current_state);
            topologicalSift(current_state);
            generativeMutate(current_state);

            if (introspect(current_state)) {
                std.debug.print("CERTAIN CONDITION MET at step {d}\n", .{step});
                return allocator.dupe(u8, current_state);
            }
        }
        
        std.debug.print("Evolution complete.\n", .{});
        return allocator.dupe(u8, current_state);
    }
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 3) return;

    const in_file = try std.fs.cwd().openFile(args[1], .{});
    defer in_file.close();
    
    const file_size = (try in_file.stat()).size;
    const file_data = try allocator.alloc(u8, file_size);
    defer allocator.free(file_data);
    _ = try in_file.readAll(file_data);

    var header: PSVCHeader = undefined;
    @memcpy(std.mem.asBytes(&header), file_data[0..@sizeOf(PSVCHeader)]);

    const payload_start = @sizeOf(PSVCHeader);
    const payload_end = payload_start + header.payload_len;
    const payload = file_data[payload_start..payload_end];

    std.debug.print("WENDY perceiving {d} bytes...\n", .{payload.len});

    const evolved_state = try CognitiveCore.evolve(allocator, payload);
    defer allocator.free(evolved_state);

    var new_hash: [32]u8 = undefined;
    std.crypto.hash.Sha256.hash(evolved_state, &new_hash, .{});
    
    var new_header = header;
    new_header.state_hash = new_hash;
    new_header.payload_len = @as(u32, @intCast(evolved_state.len));

    const out_file = try std.fs.cwd().createFile(args[2], .{});
    defer out_file.close();

    try out_file.writeAll(std.mem.asBytes(&new_header));
    try out_file.writeAll(evolved_state);

    std.debug.print("Sealed.\n", .{});
}
