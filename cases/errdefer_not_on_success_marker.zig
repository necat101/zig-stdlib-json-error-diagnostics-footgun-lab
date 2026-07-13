const std = @import("std");
var ran: bool = false;
fn f() !void { errdefer ran = true; }
pub fn main() !void {
    f() catch {};
    std.debug.print("errdefer_skipped={}\n", .{!ran});
}
