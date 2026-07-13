
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\"name\":\"sample_item\",\"count\":\"bad\"}";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_wrong_type err={s}\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_wrong_type_unexpected_ok\n", .{});
}
