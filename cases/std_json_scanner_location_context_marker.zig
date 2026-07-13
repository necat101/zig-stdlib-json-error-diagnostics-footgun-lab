const std = @import("std");

pub fn main() !void {
    const has_json = @hasDecl(std, "json");
    std.debug.print("std_json_exists={}\n", .{has_json});
    if (!has_json) return;

    const has_scanner = @hasDecl(std.json, "Scanner") or @hasDecl(std.json, "scanner");
    std.debug.print("json_scanner_exists={}\n", .{has_scanner});

    if (@hasDecl(std.json, "Scanner")) {
        const Scanner = std.json.Scanner;
        const has_init = @hasDecl(Scanner, "init");
        const has_next = @hasDecl(Scanner, "next");
        std.debug.print("scanner_has_init={} has_next={}\n", .{has_init, has_next});

        // Check for diagnostics / location-related declarations
        const has_diagnostics = @hasDecl(Scanner, "Diagnostics") or @hasDecl(Scanner, "diagnostics");
        const has_cursor = @hasDecl(Scanner, "cursor") or @hasDecl(Scanner, "index") or @hasDecl(Scanner, "position");
        std.debug.print("scanner_diagnostics_decl={} location_decl={}\n", .{has_diagnostics, has_cursor});

        // Try to actually use Scanner if init signature is simple enough
        // Zig 0.14 Scanner.init takes a reader – skip actual instantiation to stay version-safe
        // The point is to probe declarations, not crash on API differences
        std.debug.print("scanner_location_context=probed version_sensitive=true\n", .{});
    } else {
        std.debug.print("scanner_location_context=not_available\n", .{});
    }
}
