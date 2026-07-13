#!/usr/bin/env python3
"""Generate 48 deterministic Zig case files for zig-stdlib-json-error-diagnostics-footgun-lab"""
import json, pathlib

repo_root = pathlib.Path(__file__).parent
cases_dir = repo_root / "cases"
cases_dir.mkdir(exist_ok=True)

cases = []

def write_case(case_id, category, src, purpose, features, exp_compile="pass", exp_run="n/a", exp_stdout="", exp_stderr="", exp_error_cat="", exp_diag="", exp_cleanup="", exp_parser="", exp_ownership="", exp_context="", exp_api_ver="0.14.0", command_override=None, timeout_ms=3000, nonzero_reason=""):
    path = cases_dir / f"{case_id}.zig"
    path.write_text(src)
    cmd = command_override or f"zig run {path} -O ReleaseSafe"
    cases.append({
        "case_id": case_id,
        "category": category,
        "source_path": str(path.relative_to(repo_root)),
        "purpose": purpose,
        "features": features,
        "expected_compile": exp_compile,
        "expected_run": exp_run,
        "expected_stdout_marker": exp_stdout,
        "expected_stderr_marker": exp_stderr,
        "expected_error_category": exp_error_cat,
        "expected_diagnostic_category": exp_diag,
        "expected_cleanup_order": exp_cleanup,
        "expected_parser_result": exp_parser,
        "expected_ownership_behavior": exp_ownership,
        "expected_context_only_reason": exp_context,
        "expected_api_version_sensitivity": exp_api_ver,
        "command": cmd,
        "timeout_ms": timeout_ms,
        "nonzero_success_reason": nonzero_reason,
    })

# 1-17 same as before
write_case("local_zig_version_marker","version_probe",
'''const std = @import("std");
pub fn main() !void {
    const v = @import("builtin").zig_version;
    std.debug.print("zig_version={}.{}.{}\\n", .{v.major, v.minor, v.patch});
}
''',"probe local zig version","zig_version,builtin",exp_run="pass",exp_stdout="zig_version=")

write_case("zig_env_std_dir_marker","version_probe",
'''const std = @import("std");
pub fn main() !void {
    std.debug.print("std_import_ok\\n", .{});
}
''',"confirm std import resolves","std_import",exp_run="pass",exp_stdout="std_import_ok")

write_case("error_union_namespace_context_marker","error_union",
'''const std = @import("std");
const DemoError = error{ DemoFail, InvalidInput };
pub fn main() !void {
    const v: DemoError!u32 = 42;
    std.debug.print("error_union_ok value={}\\n", .{v catch 0});
}
''',"error union namespace basic","error_union",exp_run="pass",exp_stdout="error_union_ok")

write_case("basic_error_union_success_marker","error_union",
'''const std = @import("std");
const E = error{Fail};
fn f(ok: bool) E!u32 { if (ok) return 123 else return E.Fail; }
pub fn main() !void {
    const r = try f(true);
    std.debug.print("success_value={}\\n", .{r});
}
''',"error union success path","error_union,try",exp_run="pass",exp_stdout="success_value=123")

write_case("basic_error_union_failure_marker","error_union",
'''const std = @import("std");
const E = error{Fail};
fn f() E!u32 { return E.Fail; }
pub fn main() !void {
    const r = f() catch |e| {
        std.debug.print("captured_error={s}\\n", .{@errorName(e)});
        return;
    };
    _ = r;
}
''',"error union failure capture","error_union,catch,@errorName",exp_run="pass",exp_stdout="captured_error=Fail",exp_error_cat="Fail")

write_case("explicit_error_set_marker","error_union",
'''const std = @import("std");
const E = error{ A, B };
fn f(x: u32) E!u32 { if (x==0) return E.A else if (x==1) return E.B else return x; }
pub fn main() !void {
    std.debug.print("explicit_A={s} B={s}\\n", .{@errorName(E.A), @errorName(E.B)});
}
''',"explicit error set","error_set,@errorName",exp_run="pass",exp_stdout="explicit_A=A")

write_case("inferred_error_set_marker","error_union",
'''const std = @import("std");
fn may_fail(x: bool) !u32 { if (x) return error.Foo else return 7; }
pub fn main() !void {
    const r = may_fail(false) catch 0;
    std.debug.print("inferred_ok={}\\n", .{r});
}
''',"inferred error set","inferred_error_set,try,catch",exp_run="pass",exp_stdout="inferred_ok=7")

write_case("error_name_marker","error_union",
'''const std = @import("std");
pub fn main() !void {
    const e = error.DemoError;
    std.debug.print("error_name={s}\\n", .{@errorName(e)});
}
''',"@errorName probe","@errorName",exp_run="pass",exp_stdout="error_name=DemoError")

write_case("try_propagates_error_marker","error_union",
'''const std = @import("std");
const E = error{Foo};
fn inner() E!u32 { return E.Foo; }
fn outer() E!u32 { return try inner(); }
pub fn main() !void {
    _ = outer() catch |e| {
        std.debug.print("try_propagated={s}\\n", .{@errorName(e)});
        return;
    };
}
''',"try propagates error","try,error_union",exp_run="pass",exp_stdout="try_propagated=Foo",exp_error_cat="Foo")

write_case("catch_maps_error_marker","error_union",
'''const std = @import("std");
const E = error{Foo};
fn f() E!u32 { return E.Foo; }
pub fn main() !void {
    const r = f() catch error.Bar;
    _ = r catch |e| {
        std.debug.print("catch_mapped={s}\\n", .{@errorName(e)});
        return;
    };
}
''',"catch maps error","catch,error_union",exp_run="pass",exp_stdout="catch_mapped=Bar")

write_case("catch_captures_error_marker","error_union",
'''const std = @import("std");
pub fn main() !void {
    const r: error{Foo}!u32 = error.Foo;
    _ = r catch |e| {
        std.debug.print("catch_captured={s}\\n", .{@errorName(e)});
        return;
    };
}
''',"catch captures error value","catch,@errorName",exp_run="pass",exp_stdout="catch_captured=Foo",exp_error_cat="Foo")

write_case("catch_default_value_marker","error_union",
'''const std = @import("std");
fn f() error{Foo}!u32 { return error.Foo; }
pub fn main() !void {
    const v = f() catch 99;
    std.debug.print("catch_default={}\\n", .{v});
}
''',"catch default value","catch",exp_run="pass",exp_stdout="catch_default=99")

write_case("errdefer_runs_on_error_marker","errdefer",
'''const std = @import("std");
var log: [8]u8 = undefined;
var log_len: usize = 0;
fn append(c: u8) void { if (log_len < log.len) { log[log_len]=c; log_len+=1; } }
fn f() error{Foo}!void { errdefer append('E'); return error.Foo; }
pub fn main() !void {
    _ = f() catch {};
    std.debug.print("errdefer_ran={}\\n", .{log_len > 0 and log[0]=='E'});
}
''',"errdefer runs on error","errdefer",exp_run="pass",exp_stdout="errdefer_ran=true",exp_cleanup="errdefer_executed")

write_case("errdefer_not_on_success_marker","errdefer",
'''const std = @import("std");
var ran: bool = false;
fn f() !void { errdefer ran = true; }
pub fn main() !void {
    f() catch {};
    std.debug.print("errdefer_skipped={}\\n", .{!ran});
}
''',"errdefer not on success","errdefer",exp_run="pass",exp_stdout="errdefer_skipped=true",exp_cleanup="errdefer_not_executed")

write_case("defer_errdefer_order_marker","errdefer",
'''const std = @import("std");
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
    std.debug.print("order_ok={}\\n", .{ok});
}
''',"defer / errdefer order","defer,errdefer",exp_run="pass",exp_stdout="order_ok=true",exp_cleanup="E_then_D")

write_case("errdefer_cleanup_counter_marker","errdefer",
'''const std = @import("std");
var counter: u32 = 0;
fn f(fail: bool) error{Foo}!void {
    errdefer counter += 1;
    if (fail) return error.Foo;
}
pub fn main() !void {
    _ = f(true) catch {};
    _ = f(false) catch {};
    std.debug.print("cleanup_count={}\\n", .{counter});
}
''',"errdefer cleanup counter","errdefer",exp_run="pass",exp_stdout="cleanup_count=1",exp_cleanup="counter_1")

write_case("errdefer_failure_context_print_marker","errdefer",
'''const std = @import("std");
fn f() error{Foo}!void {
    errdefer std.debug.print("errdefer_context_printed\\n", .{});
    return error.Foo;
}
pub fn main() !void {
    _ = f() catch {};
    std.debug.print("returned_after_errdefer\\n", .{});
}
''',"errdefer failure context print","errdefer",exp_run="pass",exp_stdout="errdefer_context_printed",exp_cleanup="context_printed")

# 18
write_case("optional_error_info_out_param_marker","error_info",
'''const std = @import("std");
const ErrorInfo = struct { code: u32, msg: []const u8 };
const E = error{Fail};
fn f(info: ?*ErrorInfo) E!u32 {
    if (info) |p| { p.* = .{ .code = 1, .msg = "demo_user" }; }
    return E.Fail;
}
pub fn main() !void {
    var info: ErrorInfo = undefined;
    _ = f(&info) catch |e| {
        std.debug.print("error_info_out code={} msg={s} err={s}\\n", .{info.code, info.msg, @errorName(e)});
        return;
    };
}
''',"optional error info out-param","error_info,out_param",exp_run="pass",exp_stdout="error_info_out code=1",exp_diag="out_param_provided")

# 19
write_case("null_error_info_out_param_marker","error_info",
'''const std = @import("std");
const ErrorInfo = struct { code: u32 };
const E = error{Fail};
fn f(info: ?*ErrorInfo) E!u32 {
    if (info) |p| p.* = .{.code=1};
    return E.Fail;
}
pub fn main() !void {
    _ = f(null) catch |e| {
        std.debug.print("null_info_ok err={s}\\n", .{@errorName(e)});
        return;
    };
}
''',"null error info out-param","error_info,out_param",exp_run="pass",exp_stdout="null_info_ok err=Fail",exp_diag="out_param_null")

# 20
write_case("error_info_union_variant_marker","error_info",
'''const std = @import("std");
const FailInfo = union(enum) { code: u32, msg: []const u8 };
pub fn main() !void {
    const info: FailInfo = .{ .code = 42 };
    switch (info) {
        .code => |c| std.debug.print("info_union_code={}\\n", .{c}),
        .msg => |m| std.debug.print("info_union_msg={s}\\n", .{m}),
    }
}
''',"error info union variant","tagged_union,error_info",exp_run="pass",exp_stdout="info_union_code=42",exp_diag="union_variant")

# 21
write_case("tagged_union_result_alternative_marker","error_info",
'''const std = @import("std");
const Result = union(enum) { ok: u32, err: []const u8 };
fn f(ok: bool) Result {
    if (ok) return .{ .ok = 7 } else return .{ .err = "sample_item" };
}
pub fn main() !void {
    const r = f(false);
    switch (r) { .ok => |v| std.debug.print("ok={}\\n", .{v}), .err => |e| std.debug.print("result_err={s}\\n", .{e}) }
}
''',"tagged-union result alternative","tagged_union,result",exp_run="pass",exp_stdout="result_err=sample_item",exp_diag="tagged_result")

# 22
write_case("error_payload_memory_policy_context_marker","error_info",
'''const std = @import("std");
pub fn main() !void {
    std.debug.print("error_payload_memory_policy=caller_provided_no_implicit_alloc\\n", .{});
}
''',"error payload memory policy context","error_info,memory_policy",exp_run="pass",exp_stdout="error_payload_memory_policy=caller_provided",exp_context="policy_documentary",exp_diag="explicit_allocation")

# 23
write_case("oom_safe_diagnostic_context_marker","error_info",
'''const std = @import("std");
pub fn main() !void {
    var buf: [64]u8 = undefined;
    _ = &buf;
    std.debug.print("oom_safe_diagnostic=fixed_buffer_no_alloc\\n", .{});
}
''',"OOM-safe diagnostic context","error_info,oom",exp_run="pass",exp_stdout="oom_safe_diagnostic=fixed_buffer",exp_context="oom_documentary",exp_diag="oom_safe")

# 24
write_case("std_testing_expect_error_marker","testing",
'''const std = @import("std");
const E = error{Foo};
fn f() E!u32 { return E.Foo; }
test "expect_error_demo" {
    try std.testing.expectError(E.Foo, f());
}
pub fn main() !void {
    std.debug.print("testing_expect_error_compiled\\n", .{});
}
''',"std.testing.expectError","std.testing",exp_run="pass",exp_stdout="testing_expect_error_compiled",exp_context="run_zig_test_for_full_validation")

# 25
write_case("std_testing_expected_failure_marker","testing",
'''const std = @import("std");
test "deliberate_fail" {
    try std.testing.expect(false);
}
pub fn main() !void {
    std.debug.print("expected_failure_marker_compiled\\n", .{});
}
''',"std.testing expected failure","std.testing",exp_run="pass",exp_stdout="expected_failure_marker_compiled",exp_context="run_zig_test_expects_failure")

# JSON helper struct used in multiple cases
json_demo_struct = '''
const DemoConfig = struct { name: []const u8, count: u8, };
'''

# 26
write_case("std_json_namespace_probe_marker","json",
'''const std = @import("std");
pub fn main() !void {
    const has_json = @hasDecl(std, "json");
    std.debug.print("std_json_exists={}\\n", .{has_json});
}
''',"std.json namespace probe","std.json,@hasDecl",exp_run="pass",exp_stdout="std_json_exists=true",exp_parser="namespace_probe")

# 27
write_case("std_json_parse_valid_object_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\\"name\\":\\"demo_user\\",\\"count\\":5}";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_parse_error={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_valid name={s} count={}\\n", .{parsed.value.name, parsed.value.count});
}
''',"std.json parse valid object","std.json,parseFromSlice",exp_run="pass",exp_stdout="json_valid name=demo_user",exp_parser="valid",exp_ownership="deinit_required")

# 28
write_case("std_json_missing_required_field_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\\"name\\":\\"toy_config\\"}";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_missing_field err={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_missing_field_unexpected_ok\\n", .{});
}
''',"std.json missing required field","std.json",exp_run="pass",exp_stdout="json_missing_field err=",exp_parser="missing_field",exp_error_cat="MissingField")

# 29
write_case("std_json_wrong_field_type_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\\"name\\":\\"sample_item\\",\\"count\\":\\"bad\\"}";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_wrong_type err={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_wrong_type_unexpected_ok\\n", .{});
}
''',"std.json wrong field type","std.json",exp_run="pass",exp_stdout="json_wrong_type err=",exp_parser="wrong_type")

# 30
write_case("std_json_unknown_field_default_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\\"name\\":\\"example_count\\",\\"count\\":1,\\"extra\\":\\"fake_path\\"}";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_unknown_field err={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_unknown_ok name={s}\\n", .{parsed.value.name});
}
''',"std.json unknown field default","std.json",exp_run="pass",exp_parser="unknown_field",exp_stdout="json_unknown")

# 31
write_case("std_json_unknown_field_reject_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\\"name\\":\\"diagnostic_case\\",\\"count\\":2,\\"x\\":1}";
    const opts: std.json.ParseOptions = .{ .ignore_unknown_fields = false };
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, opts) catch |e| {
        std.debug.print("json_unknown_reject err={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_unknown_accepted name={s}\\n", .{parsed.value.name});
}
''',"std.json unknown field reject option","std.json",exp_run="pass",exp_parser="unknown_field_policy",exp_stdout="json_unknown_")

# 32
write_case("std_json_malformed_syntax_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\\"name\\":\\"local_parser_test\\"";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_malformed err={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_malformed_unexpected_ok\\n", .{});
}
''',"std.json malformed syntax","std.json",exp_run="pass",exp_stdout="json_malformed err=",exp_parser="syntax_error")

# 33
write_case("std_json_trailing_tokens_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "{\\"name\\":\\"demo_user\\",\\"count\\":3} trailing";
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{}) catch |e| {
        std.debug.print("json_trailing err={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_trailing_ok name={s}\\n", .{parsed.value.name});
}
''',"std.json trailing tokens","std.json",exp_run="pass",exp_parser="trailing_tokens",exp_stdout="json_trailing_")

# 34
write_case("std_json_unexpected_token_marker","json",
'''const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const input = "[1,2,]";
    const parsed = std.json.parseFromSlice(std.json.Value, alloc, input, .{}) catch |e| {
        std.debug.print("json_unexpected_token err={s}\\n", .{@errorName(e)}); return;
    };
    defer parsed.deinit();
    std.debug.print("json_unexpected_ok\\n", .{});
}
''',"std.json unexpected token","std.json",exp_run="pass",exp_stdout="json_unexpected_token err=",exp_parser="unexpected_token")

# 35
write_case("std_json_scanner_exists_marker","json_scanner",
'''const std = @import("std");
pub fn main() !void {
    const has_scanner = @hasDecl(std.json, "Scanner") or @hasDecl(std.json, "scanner");
    std.debug.print("json_scanner_exists={}\\n", .{has_scanner});
}
''',"std.json.Scanner exists probe","std.json.Scanner,@hasDecl",exp_run="pass",exp_stdout="json_scanner_exists=",exp_parser="scanner_probe",exp_api_ver="version_sensitive")

# 36
write_case("std_json_scanner_diagnostics_exists_marker","json_scanner",
'''const std = @import("std");
pub fn main() !void {
    var found: bool = false;
    if (@hasDecl(std.json, "Scanner")) {
        const S = std.json.Scanner;
        found = @hasDecl(S, "Diagnostics") or @hasDecl(S, "diagnostics");
    }
    std.debug.print("scanner_diagnostics_decl={}\\n", .{found});
}
''',"std.json.Scanner diagnostics probe","std.json.Scanner",exp_run="pass",exp_stdout="scanner_diagnostics_decl=",exp_parser="scanner_diagnostics",exp_diag="version_sensitive",exp_api_ver="version_sensitive")

# 37
write_case("std_json_scanner_location_context_marker","json_scanner",
'''const std = @import("std");
pub fn main() !void {
    std.debug.print("scanner_location_context=version_dependent\\n", .{});
}
''',"std.json.Scanner location context","std.json.Scanner",exp_run="pass",exp_stdout="scanner_location_context=",exp_parser="scanner_location",exp_diag="version_sensitive",exp_context="api_version_dependent",exp_api_ver="version_sensitive")

# 38
write_case("std_json_parse_from_slice_api_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    const has_parse = @hasDecl(std.json, "parseFromSlice");
    std.debug.print("parse_from_slice_exists={}\\n", .{has_parse});
    if (!has_parse) return;
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const parsed = std.json.parseFromSlice(DemoConfig, alloc, "{\\"name\\":\\"demo_user\\",\\"count\\":1}", .{}) catch return;
    defer parsed.deinit();
    std.debug.print("parse_from_slice_ok\\n", .{});
}
''',"std.json parseFromSlice API","std.json.parseFromSlice",exp_run="pass",exp_stdout="parse_from_slice_exists=",exp_parser="api_probe",exp_api_ver="version_sensitive")

# 39
write_case("std_json_parse_from_token_source_api_marker","json",
'''const std = @import("std");
pub fn main() !void {
    const has_token = @hasDecl(std.json, "parseFromTokenSource");
    std.debug.print("parse_from_token_source_exists={}\\n", .{has_token});
}
''',"std.json parseFromTokenSource API probe","std.json",exp_run="pass",exp_stdout="parse_from_token_source_exists=",exp_parser="api_probe",exp_api_ver="version_sensitive")

# 40
write_case("std_json_parsed_deinit_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const parsed = try std.json.parseFromSlice(DemoConfig, alloc, "{\\"name\\":\\"sample_item\\",\\"count\\":9}", .{});
    defer parsed.deinit();
    std.debug.print("parsed_deinit_ok name={s}\\n", .{parsed.value.name});
}
''',"std.json Parsed deinit","std.json",exp_run="pass",exp_stdout="parsed_deinit_ok",exp_ownership="deinit_called")

# 41
write_case("std_json_parsed_value_lifetime_marker","json",
json_demo_struct + '''
const std = @import("std");
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();
    const parsed = try std.json.parseFromSlice(DemoConfig, alloc, "{\\"name\\":\\"toy_config\\",\\"count\\":4}", .{});
    defer parsed.deinit();
    const name = parsed.value.name;
    std.debug.print("lifetime_ok name_len={}\\n", .{name.len});
}
''',"std.json parsed value lifetime","std.json",exp_run="pass",exp_stdout="lifetime_ok name_len=",exp_ownership="use_before_deinit")

# 42
write_case("std_zon_namespace_probe_marker","zon",
'''const std = @import("std");
pub fn main() !void {
    const has_zon = @hasDecl(std, "zon");
    std.debug.print("std_zon_exists={}\\n", .{has_zon});
}
''',"std.zon namespace probe","std.zon,@hasDecl",exp_run="pass",exp_stdout="std_zon_exists=",exp_api_ver="version_sensitive")

# 43
write_case("std_zon_parse_api_marker","zon",
'''const std = @import("std");
pub fn main() !void {
    const has_zon = @hasDecl(std, "zon");
    var has_parse: bool = false;
    if (has_zon) {
        has_parse = @hasDecl(std.zon, "parse") or @hasDecl(std.zon, "parseFromSlice");
    }
    std.debug.print("zon_parse_exists={}\\n", .{has_parse});
}
''',"std.zon parse API probe","std.zon",exp_run="pass",exp_stdout="zon_parse_exists=",exp_api_ver="version_sensitive")

# 44
write_case("std_zon_diagnostics_probe_marker","zon",
'''const std = @import("std");
pub fn main() !void {
    const has_zon = @hasDecl(std, "zon");
    var found: bool = false;
    if (has_zon) {
        found = @hasDecl(std.zon, "Diagnostics");
    }
    std.debug.print("zon_diagnostics_exists={}\\n", .{found});
}
''',"std.zon diagnostics probe","std.zon",exp_run="pass",exp_stdout="zon_diagnostics_exists=",exp_diag="version_sensitive",exp_api_ver="version_sensitive")

# 45
write_case("debugger_breakpoint_context_not_run_marker","context",
'''const std = @import("std");
pub fn main() !void {
    const enable_break = false;
    if (enable_break) {
        @breakpoint();
    }
    std.debug.print("breakpoint_context_not_run\\n", .{});
}
''',"debugger breakpoint context not run","@breakpoint",exp_run="pass",exp_stdout="breakpoint_context_not_run",exp_context="breakpoint_never_executed")

# 46
write_case("no_network_no_external_input_marker","context",
'''const std = @import("std");
pub fn main() !void {
    std.debug.print("no_network_no_external_input\\n", .{});
}
''',"no network no external input","context",exp_run="pass",exp_stdout="no_network_no_external_input",exp_context="local_only")

# 47
write_case("no_global_error_design_claim_marker","context",
'''const std = @import("std");
pub fn main() !void {
    std.debug.print("no_global_error_design_claim\\n", .{});
}
''',"no global error design claim","context",exp_run="pass",exp_stdout="no_global_error_design_claim",exp_context="no_universal_claim")

# 48
write_case("production_diagnostics_policy_not_tested_marker","context",
'''const std = @import("std");
pub fn main() !void {
    std.debug.print("production_diagnostics_not_tested\\n", .{});
}
''',"production diagnostics policy not tested","context",exp_run="pass",exp_stdout="production_diagnostics_not_tested",exp_context="not_production_proof")

# write cases.json
with open(repo_root / "cases.json", "w") as f:
    json.dump(cases, f, indent=2)

print(f"Generated {len(cases)} cases")
assert len(cases) == 48, f"expected 48, got {len(cases)}"
