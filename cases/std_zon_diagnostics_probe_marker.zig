const std = @import("std");
pub fn main() !void {
    const has_zon = @hasDecl(std, "zon");
    var found: bool = false;
    if (has_zon) {
        found = @hasDecl(std.zon, "Diagnostics");
    }
    std.debug.print("zon_diagnostics_exists={}\n", .{found});
}
