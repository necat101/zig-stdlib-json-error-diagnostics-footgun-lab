
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\"name\":\"demo_user\",\"count\":5}";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_parse_error={s}\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_valid name={s} count={}\n", .{parsed.value.name, parsed.value.count});
}
