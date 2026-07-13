
const DemoConfig = struct { name: []const u8, count: u8, };

const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const parsed = try std.json.parseFromSlice(DemoConfig, alloc, "{\"name\":\"sample_item\",\"count\":9}", .{});
    defer parsed.deinit();
    std.debug.print("parsed_deinit_ok name={s}\n", .{parsed.value.name});
}
