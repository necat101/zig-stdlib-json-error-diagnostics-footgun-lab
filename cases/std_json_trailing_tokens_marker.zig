
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\"name\":\"demo_user\",\"count\":3} trailing";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_trailing err={s}\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_trailing_ok name={s}\n", .{parsed.value.name});
}
