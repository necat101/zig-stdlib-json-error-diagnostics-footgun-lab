const std = @import("std");
const E = error{ A, B };
fn f(x: u32) E!u32 { if (x==0) return E.A else if (x==1) return E.B else return x; }
pub fn main() !void {
    std.debug.print("explicit_A={s} B={s}\n", .{@errorName(E.A), @errorName(E.B)});
}
