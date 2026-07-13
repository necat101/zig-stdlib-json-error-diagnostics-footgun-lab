const std = @import("std");
pub fn main() !void {
    const has_zon = @hasDecl(std, "zon");
    var has_parse: bool = false;
    if (has_zon) {
        has_parse = @hasDecl(std.zon, "parse") or @hasDecl(std.zon, "parseFromSlice");
    }
    std.debug.print("zon_parse_exists={}\n", .{has_parse});
}
