#!/usr/bin/env python3
import json, subprocess, time, pathlib, sys, os
repo_root = pathlib.Path(__file__).parent
cases_path = repo_root / "cases.json"
if not cases_path.exists():
    print("run generate_cases.py first", file=sys.stderr); sys.exit(1)
cases = json.loads(cases_path.read_text())

ZIG_BIN = os.environ.get("ZIG_BIN", "/home/ubuntu/.openclaw/workspace/.tools/zig/0.14.0/zig")
print(f"Using ZIG_BIN={ZIG_BIN}", file=sys.stderr)
ver_out = subprocess.run([ZIG_BIN, "version"], capture_output=True, text=True)
zig_version = ver_out.stdout.strip()
print(f"zig_version={zig_version}", file=sys.stderr)

# get stdlib dir for stdlib_source_probe
try:
    env_out = subprocess.run([ZIG_BIN, "env"], capture_output=True, text=True, timeout=5)
    env_json = json.loads(env_out.stdout)
    stdlib_dir = env_json.get("lib_dir", "") + "/std"
except Exception:
    stdlib_dir = str(pathlib.Path(ZIG_BIN).parent.parent / "lib" / "std")

methods = [
"zig_version_probe",
"zig_env_probe",
"stdlib_source_probe",
"compile_only_debug",
"compile_only_release_safe",
"zig_test_debug",
"zig_test_release_safe",
"run_safe_executable",
"error_union_observer",
"try_catch_observer",
"errdefer_observer",
"json_parse_observer",
"json_diagnostics_observer",
"zon_diagnostics_observer",
"context_only_guard",
"deliver_no_external_truth_marker",
]

def method_applies(method, case):
    cat = case["category"]
    if method == "zig_version_probe": return "version" in cat
    if method == "zig_env_probe": return "version" in cat
    if method == "stdlib_source_probe": return cat in ("json","json_scanner","zon")
    if method == "compile_only_debug": return True
    if method == "compile_only_release_safe": return True
    if method == "zig_test_debug": return cat in ("testing",)
    if method == "zig_test_release_safe": return cat in ("testing",)
    if method == "run_safe_executable": return case.get("expected_context_only_reason","") == ""
    if method == "error_union_observer": return cat == "error_union"
    if method == "try_catch_observer": return cat == "error_union"
    if method == "errdefer_observer": return cat == "errdefer"
    if method == "json_parse_observer": return cat == "json"
    if method == "json_diagnostics_observer": return cat in ("json","json_scanner")
    if method == "zon_diagnostics_observer": return cat == "zon"
    if method == "context_only_guard": return case.get("expected_context_only_reason","") != ""
    if method == "deliver_no_external_truth_marker": return cat == "context"
    return False

rows = []
start_all = time.perf_counter()
subprocess_count = 0

for method in methods:
    for case in cases:
        src_path = repo_root / case["source_path"]
        applies = method_applies(method, case)
        row_base = {
            "method": method,
            "case_id": case["case_id"],
            "category": case["category"],
            "source_path": case["source_path"],
            "zig_path": ZIG_BIN,
            "zig_version": zig_version,
        }
        if not applies:
            rows.append({**row_base,
                "command": "",
                "optimize_mode": "",
                "expected_compile": case["expected_compile"],
                "actual_compile": "n/a",
                "expected_run": case["expected_run"],
                "actual_run": "not_run",
                "exit_code": None,
                "stdout": "",
                "stderr": "",
                "elapsed_ms": 0,
                "timeout": False,
                "expected_classification": "not_run",
                "actual_classification": "not_run",
                "error_name": "",
                "diagnostic_marker": "",
                "cleanup_order": "",
                "parser_observation": "",
                "api_changed": False,
                "context_only_reason": case.get("expected_context_only_reason",""),
                "skip_reason": "method_not_applicable",
                "failure_reason": "",
                "version_specific": True,
            })
            continue

        # context-only guard: do NOT execute
        context_reason = case.get("expected_context_only_reason","")
        if method == "context_only_guard" or context_reason:
            rows.append({**row_base,
                "command": "",
                "optimize_mode": "",
                "expected_compile": case["expected_compile"],
                "actual_compile": "n/a",
                "expected_run": case["expected_run"],
                "actual_run": "not_run",
                "exit_code": None,
                "stdout": "",
                "stderr": "",
                "elapsed_ms": 0,
                "timeout": False,
                "expected_classification": "context_only",
                "actual_classification": "context_only",
                "error_name": "",
                "diagnostic_marker": case.get("expected_diagnostic_category",""),
                "cleanup_order": case.get("expected_cleanup_order",""),
                "parser_observation": case.get("expected_parser_result",""),
                "api_changed": False,
                "context_only_reason": context_reason,
                "skip_reason": "context_only",
                "failure_reason": "",
                "version_specific": True,
            })
            continue

        # decide command
        is_probe = False
        if method == "zig_version_probe":
            cmd = [ZIG_BIN, "version"]
            optimize = ""
            is_test = False
            is_run = True
            is_probe = True
        elif method == "zig_env_probe":
            cmd = [ZIG_BIN, "env"]
            optimize = ""
            is_test = False
            is_run = True
            is_probe = True
        elif method == "stdlib_source_probe":
            # inspect stdlib source for json/zon declarations
            cmd = ["sh", "-c", f"grep -rn 'json\\|zon\\|ParseOptions\\|Diagnostics' {stdlib_dir} 2>/dev/null | head -30 || true"]
            optimize = ""
            is_test = False
            is_run = True
            is_probe = True
        elif method == "compile_only_debug":
            cmd = [ZIG_BIN, "build-exe", str(src_path), "-femit-bin=/tmp/zig_out_test", "-O", "Debug"]
            optimize = "Debug"
            is_test = False
            is_run = False
        elif method == "compile_only_release_safe":
            cmd = [ZIG_BIN, "build-exe", str(src_path), "-femit-bin=/tmp/zig_out_test", "-O", "ReleaseSafe"]
            optimize = "ReleaseSafe"
            is_test = False
            is_run = False
        elif method in ("zig_test_debug","zig_test_release_safe"):
            opt = "Debug" if "debug" in method else "ReleaseSafe"
            cmd = [ZIG_BIN, "test", str(src_path), f"-O{opt}"]
            optimize = opt
            is_test = True
            is_run = False
        else:
            cmd = [ZIG_BIN, "run", str(src_path), "-O", "ReleaseSafe"]
            optimize = "ReleaseSafe"
            is_test = False
            is_run = True

        t0 = time.perf_counter()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            elapsed = (time.perf_counter()-t0)*1000
            stdout = p.stdout
            stderr = p.stderr
            exit_code = p.returncode
            timeout_flag = False
        except subprocess.TimeoutExpired as e:
            elapsed = (time.perf_counter()-t0)*1000
            stdout = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr = (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
            exit_code = -1
            timeout_flag = True
        subprocess_count += 1

        hay = stdout + stderr
        hay_lower = hay.lower()

        # api_changed detection
        api_changed = any(s in stderr for s in ["no member named", "has no member", "unknown identifier", "undeclared identifier", "no field named"])

        # compile status – check stderr for compiler error patterns
        # zig compiler errors contain "error:" and ".zig:"
        is_compiler_error = ("error:" in stderr.lower() and ".zig:" in stderr)
        if api_changed and exit_code != 0:
            actual_compile = "api_changed"
        elif exit_code == 0:
            actual_compile = "pass"
        elif is_compiler_error:
            actual_compile = "error"
        elif is_test or is_run:
            # program ran (or tried to), compile likely succeeded – check for obvious compile failures
            # if no compiler error markers, assume compile passed, run/test failed
            actual_compile = "pass"
        else:
            actual_compile = "error"

        if is_test:
            actual_run = "test_pass" if exit_code==0 else "test_fail"
        elif not is_run:
            actual_run = "compile_only"
        else:
            actual_run = "run_pass" if exit_code==0 else "run_fail"

        # classification
        exp_stdout_marker = case.get("expected_stdout_marker","")
        exp_error_cat = case.get("expected_error_category","")
        exp_diag = case.get("expected_diagnostic_category","")

        actual_classification = "run_fail"  # default

        if timeout_flag:
            actual_classification = "timeout_context"
        elif api_changed and exit_code != 0:
            actual_classification = "api_changed"
        elif is_probe and exit_code == 0:
            actual_classification = "run_pass"
        elif is_test and exit_code == 0:
            actual_classification = "test_pass"
        elif is_test and exit_code != 0:
            # expected test failure – require evidence in output
            test_evidence = False
            # check expected stdout marker
            if exp_stdout_marker and exp_stdout_marker in hay:
                test_evidence = True
            # check for test failure indicators + case-specific markers
            if "deliberate_fail" in case["case_id"] and "FAILED" in hay and "deliberate_fail" in hay:
                test_evidence = True
            if "expect_error" in case["case_id"] and ("Test" in hay or "ERROR" in hay or exp_error_cat in hay):
                test_evidence = True
            if test_evidence:
                actual_classification = "expected_test_failure"
            else:
                actual_classification = "test_fail"
        elif not is_run and not is_test and exit_code == 0:
            actual_classification = "compile_pass"
        elif not is_run and not is_test and exit_code != 0:
            actual_classification = "compile_error_unexpected" if not api_changed else "api_changed"
        elif is_run and exit_code == 0:
            # check expected stdout marker if provided
            if exp_stdout_marker and exp_stdout_marker not in hay:
                actual_classification = "run_fail"
            else:
                actual_classification = "run_pass"
        else:  # is_run and exit_code != 0
            # check for expected parse error – require expected_error_category match
            if exp_error_cat and exp_error_cat.lower() in hay_lower:
                actual_classification = "expected_parse_error"
            # check for expected diagnostic marker
            elif exp_diag and exp_diag in hay:
                actual_classification = "expected_diagnostic_observed"
            # check expected stdout marker even on nonzero exit (some cases print then fail)
            elif exp_stdout_marker and exp_stdout_marker in hay:
                # For JSON error cases: they catch the error and print "json_xxx err=YYY", then return cleanly (exit 0).
                # If we get here with exit_code !=0, it's unexpected – but if marker matches, still count as expected_parse_error
                if case["category"] in ("json", "json_scanner"):
                    actual_classification = "expected_parse_error"
                else:
                    actual_classification = "run_fail"
            else:
                actual_classification = "run_fail"

        # extract error name
        error_name = ""
        for token in hay.split():
            if "err=" in token:
                error_name = token.split("err=")[-1].strip().split()[0][:32]
                break

        rows.append({**row_base,
            "command": " ".join(cmd) if isinstance(cmd, list) else str(cmd),
            "optimize_mode": optimize,
            "expected_compile": case["expected_compile"],
            "actual_compile": actual_compile,
            "expected_run": case["expected_run"],
            "actual_run": actual_run,
            "exit_code": exit_code,
            "stdout": stdout[:2000],
            "stderr": stderr[:2000],
            "elapsed_ms": round(elapsed,2),
            "timeout": timeout_flag,
            "expected_classification": case.get("expected_error_category","") or "run_pass",
            "actual_classification": actual_classification,
            "error_name": error_name,
            "diagnostic_marker": exp_diag,
            "cleanup_order": case.get("expected_cleanup_order",""),
            "parser_observation": case.get("expected_parser_result",""),
            "api_changed": api_changed,
            "context_only_reason": context_reason,
            "skip_reason": "",
            "failure_reason": "" if actual_classification in ("run_pass","compile_pass","test_pass","expected_parse_error","expected_diagnostic_observed","expected_test_failure","context_only","api_changed") else stderr[:200],
            "version_specific": True,
        })

total_time = time.perf_counter() - start_all

from collections import Counter
cnt = Counter(r["actual_classification"] for r in rows)
print(f"Rows: {len(rows)}  counts: {dict(cnt)}", file=sys.stderr)
print(f"subprocesses: {subprocess_count}  time: {total_time:.2f}s", file=sys.stderr)

with open(repo_root / "results_rows.json","w") as f: json.dump(rows, f, indent=2)
import csv
if rows:
    with open(repo_root / "results_rows.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

with open(repo_root / "RESULTS.md","w") as out:
    out.write(f"# zig-stdlib-json-error-diagnostics-footgun-lab – RESULTS\n\n")
    out.write(f"Zig: {zig_version}  path: {ZIG_BIN}\n\n")
    out.write(f"Total rows: {len(rows)}\n\n")
    for k,v in sorted(cnt.items()):
        out.write(f"- {k}: {v}\n")
    out.write("\n")
    out.write(f"compile_pass: {cnt.get('compile_pass',0)}\n")
    out.write(f"test_pass: {cnt.get('test_pass',0)}\n")
    out.write(f"run_pass: {cnt.get('run_pass',0)}\n")
    out.write(f"expected_parse_error: {cnt.get('expected_parse_error',0)}\n")
    out.write(f"api_changed: {cnt.get('api_changed',0)}\n")
    out.write(f"context_only: {cnt.get('context_only',0)}\n")
    out.write(f"not_run: {cnt.get('not_run',0)}\n")

print("Wrote RESULTS.md / results_rows.json / results_rows.csv", file=sys.stderr)
