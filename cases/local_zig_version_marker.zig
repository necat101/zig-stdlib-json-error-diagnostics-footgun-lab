const std = @import("std");
pub fn main() !void {
    const v = @import("builtin").zig_version;
    std.debug.print("zig_version={}.{}.{}\n", .{v.major, v.minor, v.patch});
}
