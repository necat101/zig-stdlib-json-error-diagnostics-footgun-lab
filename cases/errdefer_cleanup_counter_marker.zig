const std = @import("std");
var counter: u32 = 0;
fn f(fail: bool) error{Foo}!void {
    errdefer counter += 1;
    if (fail) return error.Foo;
}
pub fn main() !void {
    _ = f(true) catch {};
    _ = f(false) catch {};
    std.debug.print("cleanup_count={}\n", .{counter});
}
