const std = @import("std");
const FailInfo = union(enum) { code: u32, msg: []const u8 };
pub fn main() !void {
    const info: FailInfo = .{ .code = 42 };
    switch (info) {
        .code => |c| std.debug.print("info_union_code={}\n", .{c}),
        .msg => |m| std.debug.print("info_union_msg={s}\n", .{m}),
    }
}
