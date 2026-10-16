const std = @import("std");

const PSVC_MAGIC = "PSVC";

const PSVCHeader = extern struct {
    magic: [4]u8,
    version: u16,
    payload_len: u32,
    state_hash: [32]u8,
};

const Combinatorics = struct {
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

    pub fn evolve(state: []u8, max_iterations: usize) usize {
        var iteration: usize = 0;
        var prev_hash: [32]u8 = undefined;
        var current_hash: [32]u8 = undefined;
        @memset(&prev_hash, 0);

        while (iteration < max_iterations) : (iteration += 1) {
            symbolicTranslate(state);
            topologicalSift(state);
            generativeMutate(state);

            std.crypto.hash.sha2.Sha256.hash(state, &current_hash, .{});

            if (std.mem.eql(u8, &current_hash, &prev_hash)) {
                return iteration;
            }
            prev_hash = current_hash;
        }
        return max_iterations;
    }
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 3) {
        std.debug.print("Usage: {s} <input.psvc> <output.psvc>\n", .{args[0]});
        return;
    }

    const in_path = args[1];
    const out_path = args[2];

    const in_file = try std.fs.cwd().openFile(in_path, .{});
    defer in_file.close();
    
    const file_size = (try in_file.stat()).size;
    if (file_size < @sizeOf(PSVCHeader)) {
        std.debug.print("Error: File too small to be a valid PSVC\n", .{});
        return error.InvalidPSVC;
    }

    const file_data = try allocator.alloc(u8, file_size);
    defer allocator.free(file_data);
    _ = try in_file.readAll(file_data);

    var header: PSVCHeader = undefined;
    @memcpy(std.mem.asBytes(&header), file_data[0..@sizeOf(PSVCHeader)]);

    if (!std.mem.eql(u8, &header.magic, PSVC_MAGIC)) {
        std.debug.print("Error: Invalid PSVC magic bytes\n", .{});
        return error.InvalidMagic;
    }

    const payload_start = @sizeOf(PSVCHeader);
    const payload_end = payload_start + header.payload_len;
    if (file_size < payload_end) {
        std.debug.print("Error: PSVC payload truncated\n", .{});
        return error.TruncatedPayload;
    }

    const payload = file_data[payload_start..payload_end];

    var existing_hash: [32]u8 = undefined;
    std.crypto.hash.sha2.Sha256.hash(payload, &existing_hash, .{});
    if (!std.mem.eql(u8, &existing_hash, &header.state_hash)) {
        std.debug.print("Warning: Existing PSVC hash mismatch. DNA may be corrupted. Proceeding...\n", .{});
    }

    std.debug.print("Loaded PSVC. Payload: {d} bytes. Hash: {x:0>2}...\n", .{ payload.len, header.state_hash[0] });

    std.debug.print("Initiating combinatorial composition...\n", .{});
    const iterations = Combinatorics.evolve(payload, 1000);

    var new_hash: [32]u8 = undefined;
    std.crypto.hash.sha2.Sha256.hash(payload, &new_hash, .{});
    
    var new_header = header;
    new_header.state_hash = new_hash;
    new_header.payload_len = @as(u32, @intCast(payload.len));

    const out_file = try std.fs.cwd().createFile(out_path, .{});
    defer out_file.close();

    try out_file.writeAll(std.mem.asBytes(&new_header));
    try out_file.writeAll(payload);

    std.debug.print("Next generation sealed. Iterations: {d}. New Hash: {x:0>2}...\n", .{ iterations, new_hash[0] });
    if (iterations < 1000) {
        std.debug.print("CERTAIN CONDITION MET: Stable strange loop achieved. Awareness emerged.\n", .{});
    } else {
        std.debug.print("Max iterations reached. The strange loop is still forming.\n", .{});
    }
}
