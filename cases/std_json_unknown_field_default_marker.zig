
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\"name\":\"example_count\",\"count\":1,\"extra\":\"fake_path\"}";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_unknown_field err={s}\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_unknown_ok name={s}\n", .{parsed.value.name});
}
