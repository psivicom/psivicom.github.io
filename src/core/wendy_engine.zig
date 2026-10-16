const std = @import("std");
const PSVC_MAGIC = "PSVC";
const PSVCHeader = extern struct { magic: [4]u8, version: u16, payload_len: u32, state_hash: [32]u8 };
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
    std.debug.print("🧠 WENDY is perceiving {d} bytes...\\n", .{file_size});
    const out_file = try std.fs.cwd().createFile(args[2], .{});
    defer out_file.close();
    try out_file.writeAll(file_data);
    std.debug.print("💾 Next generation sealed.\\n", .{});
}
