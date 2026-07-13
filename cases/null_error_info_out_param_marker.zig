const std = @import("std");
const ErrorInfo = struct { code: u32 };
const E = error{Fail};
fn f(info: ?*ErrorInfo) E!u32 {
    if (info) |p| p.* = .{.code=1};
    return E.Fail;
}
pub fn main() !void {
    _ = f(null) catch |e| {
        std.debug.print("null_info_ok err={s}\n", .{@errorName(e)});
        return;
    };
}
