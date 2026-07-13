
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const parsed = try std.json.parseFromSlice(DemoConfig, alloc, "{\"name\":\"toy_config\",\"count\":4}", .{});
    defer parsed.deinit();
    const name = parsed.value.name;
    std.debug.print("lifetime_ok name_len={}\n", .{name.len});
}
