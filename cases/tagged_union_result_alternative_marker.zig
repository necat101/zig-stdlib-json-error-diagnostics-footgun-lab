const std = @import("std");
const Result = union(enum) { ok: u32, err: []const u8 };
fn f(ok: bool) Result {
    if (ok) return .{ .ok = 7 } else return .{ .err = "sample_item" };
}
pub fn main() !void {
    const r = f(false);
    switch (r) { .ok => |v| std.debug.print("ok={}\n", .{v}), .err => |e| std.debug.print("result_err={s}\n", .{e}) }
}
