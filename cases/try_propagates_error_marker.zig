const std = @import("std");
const E = error{Foo};
fn inner() E!u32 { return E.Foo; }
fn outer() E!u32 { return try inner(); }
pub fn main() !void {
    _ = outer() catch |e| {
        std.debug.print("try_propagated={s}\n", .{@errorName(e)});
        return;
    };
}
