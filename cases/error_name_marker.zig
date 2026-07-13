const std = @import("std");
pub fn main() !void {
    const e = error.DemoError;
    std.debug.print("error_name={s}\n", .{@errorName(e)});
}
