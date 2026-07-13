const std = @import("std");
pub fn main() !void {
    const has_json = @hasDecl(std, "json");
    std.debug.print("std_json_exists={}\n", .{has_json});
}
