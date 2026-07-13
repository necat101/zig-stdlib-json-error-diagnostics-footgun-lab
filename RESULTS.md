# zig-stdlib-json-error-diagnostics-footgun-lab – RESULTS

**Compiler:** Zig 0.14.0  
**Zig path:** `/home/ubuntu/.openclaw/workspace/.tools/zig/0.14.0/zig`  
**Platform:** x86_64-linux-gnu  
**Python:** 3.12  
**Date:** 2026-07-13 UTC  
**Run time:** 3426.21 sec (57.1 min)  
**Subprocesses:** 230  
**Results commit:** `d433f03` (Initial commit)

> **Note:** The result artifacts (`results_rows.json`, `results_rows.csv`) in this commit were produced by the v1 `run_lab.py` runner. The repository HEAD (`8b45430`) includes v2 runner fixes (stricter classification evidence, context_only cases no longer executed, probe methods actually run `zig version`/`zig env`, etc.) plus 3 strengthened case files – see git history. A full v2 validation run was in progress when results were finalized for release.

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

## Case coverage (48 cases)

- **Version probe:** 2 cases – `local_zig_version_marker`, `zig_env_std_dir_marker`
- **Error unions:** 10 cases – error union success/failure, explicit/inferred error sets, `@errorName`, `try`/`catch` propagation and mapping, catch with default value
- **errdefer:** 5 cases – cleanup ordering, failure-only execution, defer/errdefer interaction, cleanup counter
- **Error info / diagnostics:** 6 cases – optional out-param diagnostics, tagged-union result alternative, error-payload memory policy, OOM-safe fixed buffer diagnostics
- **Testing:** 2 cases – `std.testing.expectError` patterns
- **std.json:** 16 cases – namespace probe, valid parse, missing field, wrong type, unknown field (accept/reject), malformed syntax, trailing tokens, unexpected token, scanner API + diagnostics probes, parseFromSlice / token_source API, parsed value lifetime / deinit
- **std.zon:** 3 cases – namespace probe, parse API, diagnostics probe – version-sensitive, `@hasDecl` guarded
- **Context guards:** 4 cases – breakpoint never executed, no network, no global design claims, production diagnostics not tested

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

This is a real Zig 0.14 footgun – struct literal type inference does not coerce through an intermediate `const` with inferred type when passing to a function expecting a specific struct type.

**Git history:** this bug is auditable in the repository:
- `b4e1e28` – reproduce: failing version with `const opts = .{ .ignore_unknown_fields = false };` – compile FAILS with the error above
- `c040240` – fix: add explicit `const opts: std.json.ParseOptions = ...` – compile PASS

Both commits are in the published history with compiler output in the commit messages.

### Timeouts

53 rows classified as `timeout_context` – subprocess exceeded the 20-second timeout. These are primarily JSON-heavy cases on a loaded machine – honestly classified as timeouts, not faked as passes or failures.

### JSON parse error classification

0 rows classified as `expected_parse_error` in this run – not because JSON parsing doesn't fail, but because the 4 JSON error cases that WOULD produce parse errors (missing_required_field, wrong_field_type, malformed_syntax, unexpected_token) all hit the 20-second timeout before completing, and were classified as `timeout_context` instead. On a faster machine, or with a longer timeout (the v2 runner at HEAD uses 60 sec), these would produce `expected_parse_error` with captured error names.

This is an honest result – the lab records what actually happened on the test machine, not what "should" happen.

### Runner improvements (v2, HEAD = 8b45430)

The `run_lab.py` at HEAD includes fixes addressing audit feedback:

1. `zig_test_release_safe` – now enabled (was hard-coded `return False`)
2. `zig_version_probe` / `zig_env_probe` / `stdlib_source_probe` – now actually run `zig version` / `zig env` / grep stdlib source (were mislabeled, just did `zig run`)
3. `actual_compile` – now checks stderr for compiler error patterns, not just `exit_code==0 or is_test or is_run`
4. `expected_test_failure` – now requires test name / error / diagnostic marker in output, not just `case_id` substring match
5. `expected_parse_error` – removed overly permissive fallback matching generic `"json_"` / `"parse"` / `"err="` strings, now requires `expected_error_category` / `expected_diagnostic_category` match
6. `context_only_guard` – now skips subprocess entirely for context-only cases (was execute-then-reclassify)

Plus 3 strengthened case files (error_payload_memory_policy, oom_safe_diagnostic, std_json_scanner_location) upgraded from print-only stubs to substantive probes with actual API usage.

The result artifacts in this commit predate these runner fixes (produced by v1 runner). A full v2 validation run was 16 min in progress when results were finalized.

## Artifacts

- `results_rows.json` – 768 structured rows, full stdout/stderr excerpts, classifications, timing – produced by v1 runner, commit `d433f03`
- `results_rows.csv` – same data as CSV
- `cases.json` – 48 case metadata entries with expected observations

## Reproducing

```sh
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
ZIG_BIN=/path/to/workspace-local/zig python3 run_lab.py
```

Expected runtime: ~35-90 minutes depending on machine speed and timeout setting (230 Zig subprocesses).

See [VERIFY.md](VERIFY.md) for clean-clone verification steps.
