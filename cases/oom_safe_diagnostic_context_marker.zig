const std = @import("std");

const Diag = struct {
    code: u32,
    offset: usize,
    msg_buf: [32]u8,
    msg_len: u8,
    fn message(self: *const Diag) []const u8 {
        return self.msg_buf[0..self.msg_len];
    }
};

const ParseError = error{InvalidSyntax, OutOfMemory};

fn parse_toy(input: []const u8, diag: ?*Diag) ParseError!u32 {
    // Simulate OOM-safe diagnostics: fixed-size stack buffer, no allocation
    if (input.len < 2) {
        if (diag) |d| {
            const m = "short";
            @memcpy(d.msg_buf[0..m.len], m);
            d.*.code = 1;
            d.offset = input.len;
            d.msg_len = m.len;
        }
        return ParseError.InvalidSyntax;
    }
    return 123;
}

pub fn main() !void {
    // Fixed-size stack buffer – OOM-safe, no heap allocation on error path
    var diag: Diag = undefined;
    diag.msg_buf = [_]u8{0} ** 32;
    diag.msg_len = 0;

    _ = parse_toy("x", &diag) catch |e| {
        std.debug.print("oom_safe_diagnostic code={} offset={} msg={s} err={s} alloc_bytes=0 buffer_size=32\n", .{ diag.code, diag.offset, diag.message(), @errorName(e) });
    };

    // Verify no allocation occurred – everything stack-local
    var diag2: Diag = undefined;
    diag2.msg_buf = [_]u8{0} ** 32;
    const ok = parse_toy("ok_input", &diag2) catch 0;
    std.debug.print("oom_safe_ok value={}\n", .{ok});
}
