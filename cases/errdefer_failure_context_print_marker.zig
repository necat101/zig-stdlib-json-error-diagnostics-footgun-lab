const std = @import("std");
fn f() error{Foo}!void {
    errdefer std.debug.print("errdefer_context_printed\n", .{});
    return error.Foo;
}
pub fn main() !void {
    _ = f() catch {};
    std.debug.print("returned_after_errdefer\n", .{});
}
