const std = @import("std");
test "deliberate_fail" {
    try std.testing.expect(false);
}
pub fn main() !void {
    std.debug.print("expected_failure_marker_compiled\n", .{});
}
