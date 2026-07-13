const std = @import("std");
pub fn main() !void {
    std.debug.print("error_payload_memory_policy=caller_provided_no_implicit_alloc\n", .{});
}
