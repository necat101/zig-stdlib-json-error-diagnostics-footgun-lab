const std = @import("std");
pub fn main() !void {
    const has_token = @hasDecl(std.json, "parseFromTokenSource");
    std.debug.print("parse_from_token_source_exists={}\n", .{has_token});
}
