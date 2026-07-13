const std = @import("std");
const E = error{Foo};
fn f() E!u32 { return E.Foo; }
test "expect_error_demo" {
    try std.testing.expectError(E.Foo, f());
}
pub fn main() !void {
    std.debug.print("testing_expect_error_compiled\n", .{});
}
