const std = @import("std");
fn f() error{Foo}!u32 { return error.Foo; }
pub fn main() !void {
    const v = f() catch 99;
    std.debug.print("catch_default={}\n", .{v});
}
