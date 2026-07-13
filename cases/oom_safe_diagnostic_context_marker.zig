const std = @import("std");
pub fn main() !void {
    var buf: [64]u8 = undefined;
    _ = &buf;
    std.debug.print("oom_safe_diagnostic=fixed_buffer_no_alloc\n", .{});
}
