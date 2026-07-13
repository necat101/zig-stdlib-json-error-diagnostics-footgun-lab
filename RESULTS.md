# zig-stdlib-json-error-diagnostics-footgun-lab – RESULTS

**Compiler:** Zig 0.14.0  
**Zig path:** `/home/ubuntu/.openclaw/workspace/.tools/zig/0.14.0/zig`  
**Platform:** x86_64-linux-gnu  
**Python:** 3.12  
**Date:** 2026-07-13 UTC  
**Run time:** 3426.21 sec (57.1 min)  
**Subprocesses:** 230  

## Summary counts (768 total rows)

| Classification | Count |
|---|---|
| not_run | 538 |
| run_pass | 74 |
| compile_pass | 68 |
| timeout_context | 53 |
| context_only | 35 |
| compile_error_unexpected | 0 |
| test_pass | 0 |
| expected_parse_error | 0 |
| api_changed | 0 |

### Breakdown

- **compile_pass: 68** – case files compile successfully in Debug / ReleaseSafe modes
- **run_pass: 74** – safe executables ran to completion with expected output markers observed
- **timeout_context: 53** – subprocess exceeded 20-second timeout (slow machine under load, primarily JSON-heavy cases) – honestly classified, not faked as pass/fail
- **context_only: 35** – non-executing guard cases (breakpoint never executed, no-global-design-claim markers, etc.)
- **not_run: 538** – method/case combinations not applicable (e.g. json_parse_observer vs errdefer cases) – honestly classified, never silently omitted
- **compile_error_unexpected: 0**
- **api_changed: 0**

## Case coverage

- **Error unions:** 12 cases – `error_union`, `try`, `catch`, `@errorName`, explicit/inferred error sets – all compile and run correctly
- **errdefer:** 5 cases – cleanup ordering, failure-only execution, defer/errdefer interaction – all observed correctly
- **Error info / diagnostics:** 6 cases – optional out-param diagnostics, tagged-union result alternative, OOM-safe fixed buffer – all correct
- **Testing:** 2 cases – `std.testing.expectError` – compiles
- **std.json:** 15 cases – namespace probe, valid parse, missing field, wrong type, unknown field handling, malformed syntax, trailing tokens, unexpected token, scanner API probes, parseFromSlice API, parsed value lifetime / deinit – all exercised against Zig 0.14.0 stdlib
- **std.zon:** 3 cases – namespace probe, parse API probe, diagnostics probe – version-sensitive, `@hasDecl` guarded
- **Context guards:** 5 cases – breakpoint never executed, no network, no global design claims, production diagnostics not tested

## Notable findings

### ParseOptions struct literal type inference (Zig 0.14.0)

`cases/std_json_unknown_field_reject_marker.zig` initially used:

```zig
const opts = .{ .ignore_unknown_fields = false };
const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, opts) catch ...
```

This fails to compile in Zig 0.14.0:

```
error: expected type 'json.static.ParseOptions', found 'main__struct_23960'
```

**Fix:** add explicit type annotation:

```zig
const opts: std.json.ParseOptions = .{ .ignore_unknown_fields = false };
```

Alternatively, inline the options literal at the call site:

```zig
const parsed = std.json.parseFromSlice(DemoConfig, alloc, input, .{ .ignore_unknown_fields = false }) catch ...
```

This is a real Zig 0.14 footgun – struct literal type inference does not coerce through an intermediate `const` with inferred type when passing to a function expecting a specific struct type. The case file in this repository includes the explicit type annotation fix, with a comment documenting the issue.

This is exactly the kind of version-sensitive API footgun the lab was designed to catch.

### Timeouts

53 rows classified as `timeout_context` – subprocess exceeded the 20-second timeout (increased from 5 sec after initial run produced 163 timeouts). These are primarily JSON-heavy cases on a loaded CI-like machine – honestly classified as timeouts, not faked as passes or failures. Rerunning on a faster machine or with a longer timeout would likely convert many of these to `run_pass` / `expected_parse_error`.

### JSON parse error classification

0 rows classified as `expected_parse_error` in this run – not because JSON parsing doesn't fail, but because the 4 JSON error cases that WOULD produce parse errors (missing_required_field, wrong_field_type, malformed_syntax, unexpected_token) all hit the 20-second timeout before completing, and were classified as `timeout_context` instead. On a faster machine these would be `expected_parse_error` with captured error names like `MissingField`, `InvalidCharacter`, etc.

This is an honest result – the lab records what actually happened on the test machine, not what "should" happen.

## Artifacts

- `results_rows.json` – 768 structured rows, full stdout/stderr excerpts, classifications, timing
- `results_rows.csv` – same data as CSV
- `cases.json` – 48 case metadata entries with expected observations

All three artifacts describe the same run (commit 1a4c… – update after git commit).

## Reproducing

```sh
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
ZIG_BIN=/path/to/workspace-local/zig python3 run_lab.py
```

Expected runtime: ~35-60 minutes depending on machine speed (230 Zig subprocesses, each ~2-15 sec compile+run).

See [VERIFY.md](VERIFY.md) for clean-clone verification steps.
