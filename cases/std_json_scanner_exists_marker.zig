const std = @import("std");
pub fn main() !void {
    const has_scanner = @hasDecl(std.json, "Scanner") or @hasDecl(std.json, "scanner");
    std.debug.print("json_scanner_exists={}\n", .{has_scanner});
}
