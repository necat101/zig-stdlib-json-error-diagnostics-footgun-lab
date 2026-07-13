const std = @import("std");
const E = error{Foo};
fn f() E!u32 { return E.Foo; }
pub fn main() !void {
    const r = f() catch error.Bar;
    _ = r catch |e| {
        std.debug.print("catch_mapped={s}\n", .{@errorName(e)});
        return;
    };
}
