const std = @import("std");
var log: [8]u8 = undefined;
var log_len: usize = 0;
fn append(c: u8) void { if (log_len < log.len) { log[log_len]=c; log_len+=1; } }
fn f() error{Foo}!void { errdefer append('E'); return error.Foo; }
pub fn main() !void {
    _ = f() catch {};
    std.debug.print("errdefer_ran={}\n", .{log_len > 0 and log[0]=='E'});
}
