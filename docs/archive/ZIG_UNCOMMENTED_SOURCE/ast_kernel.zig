const std = @import("std");

pub const NodeKind = enum(u8) {
    Root,
    Function,
    Variable,
    BinaryOp,
    Literal,
};

pub const AstNode = struct {
    kind: NodeKind,
    value: []const u8,
    children: std.ArrayList(AstNode),

    pub fn init(allocator: std.mem.Allocator, kind: NodeKind, value: []const u8) AstNode {
        return AstNode{
            .kind = kind,
            .value = value,
            .children = std.ArrayList(AstNode).init(allocator),
        };
    }

    pub fn deinit(self: *AstNode) void {
        for (self.children.items) |*child|
            child.deinit();
        self.children.deinit();
    }
};

pub const AstKernel = struct {
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) AstKernel {
        return AstKernel{ .allocator = allocator };
    }

    pub fn parseIntrospection(self: *AstKernel, source: []const u8) !AstNode {
        var root = AstNode.init(self.allocator, .Root, "root");
        var it = std.mem.tokenizeAny(u8, source, " \n\t{}");
        while (it.next()) |token|
        {
            if (std.mem.eql(u8, token, "fn")) {
                if (it.next()) |fname| {
                    var fn_node = AstNode.init(self.allocator, .Function, fname);
                    try root.children.append(fn_node);
                }
            } else if (std.mem.eql(u8, token, "var")) {
                if (std.mem.eql(u8, token, "var")) {
                    if (it.next()) |vname| {
                        var var_node = AstNode.init(self.allocator, .Variable, vname);
                        try root.children.append(var_node);
                    }
                }
            }
        }
        return root;
    }
};

export fn wendy_ast_kernel_verify() bool {
    var arena = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = arena.deinit();
    var kernel = AstKernel.init(arena.allocator());
    var node = kernel.parseIntrospection("fn optimize() { var x = 1; }") catch return false;
    defer node.deinit();
    return node.children.items.len == 2;
}
