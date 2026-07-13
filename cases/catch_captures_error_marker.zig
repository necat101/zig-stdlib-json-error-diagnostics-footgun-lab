const std = @import("std");
pub fn main() !void {
    const r: error{Foo}!u32 = error.Foo;
    _ = r catch |e| {
        std.debug.print("catch_captured={s}\n", .{@errorName(e)});
        return;
    };
}
