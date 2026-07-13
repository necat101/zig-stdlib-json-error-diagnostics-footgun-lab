const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "[1,2,]";
    const parsed = std.json.parseFromSlice(std.json.Value, alloc, input, .{}) catch |e| {
        std.debug.print("json_unexpected_token err={s}\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_unexpected_ok\n", .{});
}
