const std = @import("std");
const DemoError = error{ DemoFail, InvalidInput };
pub fn main() !void {
    const v: DemoError!u32 = 42;
    std.debug.print("error_union_ok value={}\n", .{v catch 0});
}
