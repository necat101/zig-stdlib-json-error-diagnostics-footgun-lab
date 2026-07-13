const std = @import("std");
const ErrorInfo = struct { code: u32, msg: []const u8 };
const E = error{Fail};
fn f(info: ?*ErrorInfo) E!u32 {
    if (info) |p| { p.* = .{ .code = 1, .msg = "demo_user" }; }
    return E.Fail;
}
pub fn main() !void {
    var info: ErrorInfo = undefined;
    _ = f(&info) catch |e| {
        std.debug.print("error_info_out code={} msg={s} err={s}\n", .{info.code, info.msg, @errorName(e)});
        return;
    };
}
