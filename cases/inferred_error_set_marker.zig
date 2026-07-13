const std = @import("std");
fn may_fail(x: bool) !u32 { if (x) return error.Foo else return 7; }
pub fn main() !void {
    const r = may_fail(false) catch 0;
    std.debug.print("inferred_ok={}\n", .{r});
}
