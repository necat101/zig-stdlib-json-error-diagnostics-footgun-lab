const std = @import("std");
const E = error{Fail};
fn f(ok: bool) E!u32 { if (ok) return 123 else return E.Fail; }
pub fn main() !void {
    const r = try f(true);
    std.debug.print("success_value={}\n", .{r});
}
