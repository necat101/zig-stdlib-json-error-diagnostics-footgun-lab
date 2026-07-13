const std = @import("std");
const E = error{Fail};
fn f() E!u32 { return E.Fail; }
pub fn main() !void {
    const r = f() catch |e| {
        std.debug.print("captured_error={s}\n", .{@errorName(e)});
        return;
    };
    _ = r;
}
