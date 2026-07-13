const std = @import("std");
var buf: [8]u8 = undefined;
var n: usize = 0;
fn push(c: u8) void { if (n < buf.len) { buf[n]=c; n+=1; } }
fn f() error{Foo}!void {
    defer push('D');
    errdefer push('E');
    return error.Foo;
}
pub fn main() !void {
    _ = f() catch {};
    const ok = n >= 2 and buf[0]=='E' and buf[1]=='D';
    std.debug.print("order_ok={}\n", .{ok});
}
