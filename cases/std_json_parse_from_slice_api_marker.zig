
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    const has_parse = @hasDecl(std.json, "parseFromSlice");
    std.debug.print("parse_from_slice_exists={}\n", .{has_parse});
    if (!has_parse) return;
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, "{\"name\":\"demo_user\",\"count\":1}", .{}) catch return;
    defer parsed.deinit();
    std.debug.print("parse_from_slice_ok\n", .{});
}
