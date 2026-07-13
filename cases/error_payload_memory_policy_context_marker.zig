const std = @import("std");

const ErrorInfo = struct {
    code: u32,
    message: [64]u8,
    msg_len: usize,
};

const DemoError = error{ ParseFailed, InvalidInput };

fn parse_demo(input: []const u8, err_info: ?*ErrorInfo) DemoError!u32 {
    if (input.len == 0) {
        if (err_info) |info| {
            const msg = "empty_input";
            @memcpy(info.message[0..msg.len], msg);
            info.*.code = 1;
            info.msg_len = msg.len;
        }
        return DemoError.InvalidInput;
    }
    if (input[0] == 'X') {
        if (err_info) |info| {
            const msg = "demo_user_parse_error";
            @memcpy(info.message[0..msg.len], msg);
            info.*.code = 2;
            info.msg_len = msg.len;
        }
        return DemoError.ParseFailed;
    }
    return 42;
}

pub fn main() !void {
    // Caller-provided diagnostics storage – stack allocated, no heap, OOM-safe
    var info: ErrorInfo = undefined;
    info.message = [_]u8{0} ** 64;
    info.msg_len = 0;

    // Error path with diagnostics
    const r1 = parse_demo("Xsample", &info) catch |e| blk: {
        std.debug.print("error_payload_memory_policy code={} msg={s} err={s} alloc=none caller_provided=true oom_safe=true\n", .{ info.code, info.message[0..info.msg_len], @errorName(e) });
        break :blk @as(u32, 0);
    };
    _ = r1;

    // Same call without diagnostics pointer – still works, caller opts out
    const r2 = parse_demo("", null) catch 99;
    std.debug.print("null_info_ok value={}\n", .{r2});
}
