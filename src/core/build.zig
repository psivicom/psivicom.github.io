const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const core_dir_path = ".";

    var dir = std.fs.cwd().openDir(core_dir_path, .{ .iterate = true }) catch |err| {
        std.debug.print("Warning: Could not open {s}: {}\n", .{ core_dir_path, err });
        return;
    };
    defer dir.close();

    var iter = dir.iterate();
    var exe_count: usize = 0;

    while (iter.next() catch null) |entry| {
        if (entry.kind != .file) continue;

        if (!std.mem.endsWith(u8, entry.name, ".zig")) continue;

        if (std.mem.eql(u8, entry.name, "build.zig")) continue;

        const exe_name = std.mem.sliceTo(entry.name, '.');
        const src_path = b.fmt("{s}/{s}", .{ core_dir_path, entry.name });

        const exe = b.addExecutable(.{
            .name = exe_name,
            .root_source_file = b.path(src_path),
            .target = target,
            .optimize = optimize,
        });

        b.installArtifact(exe);
        exe_count += 1;
    }

    std.debug.print("WENDY Cortex Build: configured {d} core modules for compilation.\n", .{exe_count});
}
