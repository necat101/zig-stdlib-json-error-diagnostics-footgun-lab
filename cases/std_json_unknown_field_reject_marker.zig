
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\"name\":\"diagnostic_case\",\"count\":2,\"x\":1}";
    const opts = .{ .ignore_unknown_fields = false };
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, opts) catch |e| {
        std.debug.print("json_unknown_reject err={s}\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_unknown_accepted name={s}\n", .{parsed.value.name});
}
