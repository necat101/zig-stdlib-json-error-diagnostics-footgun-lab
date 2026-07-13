const std = @import("std");
pub fn main() !void {
    const has_zon = @hasDecl(std, "zon");
    std.debug.print("std_zon_exists={}\n", .{has_zon});
}
