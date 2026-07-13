const std = @import("std");
pub fn main() !void {
    var found: bool = false;
    if (@hasDecl(std.json, "Scanner")) {
        const S = std.json.Scanner;
        found = @hasDecl(S, "Diagnostics") or @hasDecl(S, "diagnostics");
    }
    std.debug.print("scanner_diagnostics_decl={}\n", .{found});
}
