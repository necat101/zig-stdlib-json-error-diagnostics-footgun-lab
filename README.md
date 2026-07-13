# zig-stdlib-json-error-diagnostics-footgun-lab

A small, reproducible, compiler-validated correctness lab for Zig stdlib error handling and JSON/ZON diagnostics footguns. Inspired by a Hacker News thread on "Zig Error Patterns".

**Compiler:** Zig 0.14.0, workspace-local at `.tools/zig/0.14.0/zig`  
**Platform:** x86_64-linux-gnu  
**Cases:** 48 deterministic Zig source files  
**Methods:** 16 observer modes  
**Rows:** 768 structured result rows

---

## Hacker News thread access

The Hacker News thread at https://news.ycombinator.com/item?id=44812985 ("Zig Error Patterns", https://glfmn.io/posts/zig-error-patterns/) was read using the bundled real Hacker News Firebase API CLI (`hackernews get-item --id 44812985` with recursive comment fetching) **before** the sentiment summary below was prepared.

Raw thread evidence is committed in this repository:
- `hn_thread_evidence.md` – human-readable summary with item IDs
- `hn_comments_sanitized.json` – structured HN data (item ID, author, parent, timestamp, text), 54 nodes

No direct quotes are used below unless the HN API returned the exact text and the quote is short. Otherwise content is paraphrased in my own words.

---

## What Hacker News users were actually debating

The linked article (https://glfmn.io/posts/zig-error-patterns/) focuses on practical test-debugging patterns in Zig: using `errdefer` to print context only when a test fails, using `@breakpoint()` on an error path, and using build options to make debugger behaviour conditional.

The HN discussion broadened significantly beyond the article, into Zig's error-handling design itself. Here are the actual themes from the thread, including disagreement between commenters:

### Payload-less errors: clean control flow or ergonomic limitation?

`davidkunz` opened the error-payload discussion, asking how people deal with Zig errors not carrying arbitrary payloads, specifically calling out `std.json`'s `UnexpectedToken` error as not very helpful.

Multiple commenters framed Zig errors as **control-flow values**, not data carriers. `jmull` wrote that "errors are for control flow. If you have other information to return from a function, you can just return it — whether directly as the return value or through an 'out' parameter." `meepmorp` noted this essentially restates what Zig's BDFL said when closing issue #2647 on error payloads.

`delifue` countered: "In my opinion Zig is elegant except for one thing: cannot attach data to error." `mark38848` was blunter, calling it "complete dogshit not to be able to have data there" and saying "Odin is much better here."

`nektro` explained the design rationale: "attaching a payload requires asking the question of who and how the memory of such a payload is managed, and Zig the language never prescribes you into a particular answer to that question."

### Optional diagnostics out-parameters fit Zig's explicit-allocation philosophy

`quantummagic` described the idiomatic pattern: return a simple unadorned error, but return detailed error data through a pointer argument. The caller arranges memory usage for error data, so "the compiler does not trigger any implicit memory allocation to accommodate error returns. This is a fundamental element of Zig's design, that there are no hidden or implicit memory allocations."

`dnautics` linked to an article/video about "sneaky error payloads" – a compile-time pattern that fully compiles out if you don't use it, as an alternative to the nullable-pointer strategy. They also noted "libraries are not typically designed with a standardized convention for payload return."

### Callers reserving diagnostic storage – convenience vs. correctness

`nextaccountic` objected: "the caller must allocate space for the error payload, even if the error is very unlikely."

`quantummagic` replied that the out-parameter is optional – "the caller may omit it if desired. The reason for this particular tradeoff, is in favour of correctness rather than convenience."

`davidkunz`, after reading the explanations: "I like the approach with an optional pointer, it fits to zig's philosophy quite well. Although there's a bit of a disconnect between the unadorned error and the corresponding data struct. I could imagine it requires care when the data struct is a union, as one needs to know which error corresponds to which variant."

`randyrand` suggested from a C perspective that error objects should include a pointer to preallocated memory (e.g. 1024 bytes for error strings), with code checking for available space – "all the code is ambivalent about whether this extra space exists."

### OOM-safe error reporting

`quantummagic` specifically raised OOM safety as the reason for the explicit-allocation tradeoff: "if the failure is in an OOM condition, it can still be reported." Because the caller provides diagnostic storage up front, error reporting doesn't need to allocate.

### Comparisons with C

`metaltyphoon`: "So… pretty much how C does it."

`quantummagic` replied: "The main difference is that C doesn't have error (result types) baked into the language. So the expectation would be in the Zig example […] the calling function would never even bother to inspect the error details, unless the error path was triggered by the called function."

`dwattttt`: "Culture and coding standards count for a lot. C _can_ do this, but it's not normal to. If Zig can foster a culture of handling errors this way, it'll be the way the community writ large handle errors."

`pjmlp` was more critical overall: "Zig is basically the safety of Modula-2, with a revamped C like syntax, which is why it feels too little for a 2025 language." They'd "rather keep C around with a standard -fhardening […] and leave everything else to safer managed languages." They also disliked Zig's `@`, `!`, `.{ }` syntax and "struct based imports that look like Javascript `require()` instead of a proper module system."

`quantummagic` countered optimistically: Zig is "meant as a foundational language, to take over the role C still has today, of being the only true glue language that can underlie all the others."

### Tagged unions / result types when callers need structured failure details

`hansvm` gave a detailed analysis contrasting with Rust. For `catch`-like functionality with payloads: "That's just a `union` type. If you actually expect callers to inspect and care about the details of each possible return branch, you should provide a return type allowing them to do stuff with that information."

They also described a workaround for the `errdefer` interaction: "have a private inner function and a public outer function. The inner function has some sort of `out` parameter where it sticks that unioned metadata. The outer function executes the code which might have to be cleaned up on errors, calls the inner function, and figures out what to do from there."

`hansvm` also noted letting "the caller specify my return type, and I'll avoid work if they don't request a certain payload (e.g., not adding parse failure line numbers if not requested)."

### `try`, `catch`, and `errdefer` have different relationships with payload data

`hansvm` specifically called out that `errdefer` is "the odd duck out": "it's reasonably common for libraries to want to do some sort of cleanup on 'error' conditions, where that cleanup often doesn't depend on which error you hit, and you lose that functionality if you just return a union type."

For `try`: error propagation with payloads in Rust "need[s] a compatible error type (a notable source of minor refactors bubbling into whole-project changes), or else you can accept a little more boilerplate and box everything with a library like `anyhow`." Whether that extra metadata helps solve real problems – "opinions vary."

### Error-type compatibility and propagation – comparisons with Rust

`hansvm` argued that in Rust, wanting `try`-like functionality with arbitrary payloads means "both functions need a compatible error type (a notable source of minor refactors bubbling into whole-project changes)."

`Ar-Curunir` disagreed: "you simply need to add a single new variant to the callers error type, and either a From impl or a manual conversion at the call site."

`hansvm` replied this is "prone to causing propagating changes if you're not comfortable slapping duck tape on every conversion."

`dwattttt`: "It depends on whether people depend on the structure of the errors. If they just stringify them, that shouldn't result in changes."

### `std.json` high-level schema failures were criticized

`maleldil` noted that "Stdlib's JSON module has a separate diagnostics object" and called this "the weakest part of Zig's error handling story, although the reasons for this are understandable."

**Andy Kelley (Zig's BDFL, `AndyKelley` on HN)** replied directly: "I'd like to note that std.json, as it currently stands, is not a good example of proper error handling. Unless you use that awkward lower level Scanner API, if you get a schema mismatch it reports some failure code and does not populate a diagnostics struct, which is painful and useless."

### Lower-level Scanner diagnostics – awkward but sometimes necessary

Andy Kelley described the `std.json.Scanner` API as "awkward" but noted it's currently the only way to get useful diagnostics from `std.json` parse failures.

The lab probes `std.json.Scanner` existence, diagnostics declarations, and location-reporting APIs in a version-sensitive way, and records that scanner diagnostics availability depends on the Zig version.

### `std.zon` diagnostics – a better direction

Andy Kelley: "On the other hand the std.zon author did not make this mistake, i.e. `std.zon.parse.fromSlice` takes an optional Diagnostics struct which gives you all the information you need (including a handy format method for printing human readable messages)."

The lab probes `std.zon` parse and diagnostics APIs where available, with version-sensitive compile-time checks.

### `errdefer` for failure-only cleanup and debugging

Multiple commenters praised `errdefer`. `skrebbel`: "Wow, errdefer sounds like the kind of thing every language ought to have."

`etyp`: "the `errdefer` patterns in tests are super nice!"

`skrebbel` explained the appeal: "it lets you put code that goes in 'catch' all over your function body, right next to where it's most relevant … when reading a function [you can] forget about [errors]" without jumping to a catch block.

There was pushback too. `jayd16`: "Is it significantly different than a try-catch block?" and "the exceptional behaviors are listed first … Would you say we should move to catch-try syntax?" `masklinn`: "usually you've got half the method in a giant try block and have fun untangling which errors are caught intentionally and which are side-effects."

### Why one tiny parser example cannot settle Zig's overall error-handling design

The HN thread repeatedly circled back to the fundamental tradeoff: Zig prioritizes explicit memory control and zero hidden allocations over convenience. Whether that tradeoff is worth it depends on the domain – foundational/systems code vs. application code, OOM-critical paths vs. happy-path ergonomics.

`nextaccountic` summarized: "there's space for a post-Rust, post-Zig language to combine the approaches of both and make it _possible_ to do away with automatic heap allocation (when needed – not every piece of code wants to bother with this), but also don't make code overly verbose when doing so."

The lab does not claim Zig's error model is good or bad, does not design a replacement error system, and does not claim any language has the universally correct approach. It turns the HN discussion into a tiny reproducible compiler-validated probe showing that error propagation, cleanup ordering, optional diagnostics, parser API levels, and stdlib API versions need to be checked against the actual Zig compiler being used.

---

## Lab contents

48 deterministic Zig case files (`cases/*.zig`):

**Error unions (12 cases):**
`local_zig_version_marker`, `zig_env_std_dir_marker`, `error_union_namespace_context_marker`, `basic_error_union_success_marker`, `basic_error_union_failure_marker`, `explicit_error_set_marker`, `inferred_error_set_marker`, `error_name_marker`, `try_propagates_error_marker`, `catch_maps_error_marker`, `catch_captures_error_marker`, `catch_default_value_marker`

**errdefer (5 cases):**
`errdefer_runs_on_error_marker`, `errdefer_not_on_success_marker`, `defer_errdefer_order_marker`, `errdefer_cleanup_counter_marker`, `errdefer_failure_context_print_marker`

**Error info / diagnostics (6 cases):**
`optional_error_info_out_param_marker`, `null_error_info_out_param_marker`, `error_info_union_variant_marker`, `tagged_union_result_alternative_marker`, `error_payload_memory_policy_context_marker`, `oom_safe_diagnostic_context_marker`

**Testing (2 cases):**
`std_testing_expect_error_marker`, `std_testing_expected_failure_marker`

**std.json (16 cases):**
`std_json_namespace_probe_marker`, `std_json_parse_valid_object_marker`, `std_json_missing_required_field_marker`, `std_json_wrong_field_type_marker`, `std_json_unknown_field_default_marker`, `std_json_unknown_field_reject_marker`, `std_json_malformed_syntax_marker`, `std_json_trailing_tokens_marker`, `std_json_unexpected_token_marker`, `std_json_scanner_exists_marker`, `std_json_scanner_diagnostics_exists_marker`, `std_json_scanner_location_context_marker`, `std_json_parse_from_slice_api_marker`, `std_json_parse_from_token_source_api_marker`, `std_json_parsed_deinit_marker`, `std_json_parsed_value_lifetime_marker`

**std.zon (3 cases):**
`std_zon_namespace_probe_marker`, `std_zon_parse_api_marker`, `std_zon_diagnostics_probe_marker`

**Context / guard cases (4 cases):**
`debugger_breakpoint_context_not_run_marker`, `no_network_no_external_input_marker`, `no_global_error_design_claim_marker`, `production_diagnostics_policy_not_tested_marker`

…plus version/environment probes.

All JSON/ZON inputs are short synthetic strings with fake values: `demo_user`, `sample_item`, `toy_config`, `example_count`, `fake_path`, `diagnostic_case`, `local_parser_test`. No real user data, credentials, or network responses.

---

## Methods

16 observer methods, 48 cases = 768 structured rows:

| Method | Purpose |
|---|---|
| `zig_version_probe` | compiler version detection |
| `zig_env_probe` | stdlib import / environment |
| `stdlib_source_probe` | json/zon namespace probing |
| `compile_only_debug` | compile check, Debug |
| `compile_only_release_safe` | compile check, ReleaseSafe |
| `zig_test_debug` | `zig test`, Debug |
| `zig_test_release_safe` | `zig test`, ReleaseSafe |
| `run_safe_executable` | `zig run`, ReleaseSafe |
| `error_union_observer` | error union control flow |
| `try_catch_observer` | try/catch propagation |
| `errdefer_observer` | errdefer cleanup ordering |
| `json_parse_observer` | `std.json.parseFromSlice` |
| `json_diagnostics_observer` | scanner / diagnostics probing |
| `zon_diagnostics_observer` | `std.zon` diagnostics probing |
| `context_only_guard` | non-executing context cases |
| `deliver_no_external_truth_marker` | no universal design claims |

Rows not applicable to a method are classified `not_run` / `context_only`, never silently omitted.

---

## Results

See [RESULTS.md](RESULTS.md) for the full compiler-validated run.

---

## Verifying

```sh
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
ZIG_BIN=/path/to/workspace-local/zig python3 run_lab.py
```

See [VERIFY.md](VERIFY.md) for a clean-clone verification transcript.

---

## Scope and limitations

- The point is **not** to prove Zig's error model good/bad, design a replacement, or claim any language is universally correct
- **Not** fuzzing, not huge inputs, not memory exhaustion, not malformed UTF-8 stress
- **No** filesystem input, sockets, TLS, debugger, profiler, package downloads, or production parser
- **No** actual `@breakpoint()` execution – breakpoint case is `context_only`, compile-time guarded false
- Parsed-value lifetime case verifies owner stays alive while slices are used – no post-`deinit` access
- JSON error names are recorded as observed locally – not assumed stable across Zig versions
- Scanner / ZON diagnostics APIs are probed with `@hasDecl` – missing declarations recorded as `api_changed`, not faked
- Only narrow, local, version-specific conclusions are drawn
- One tiny parser example **cannot** settle Zig's overall error-handling design – this is the point of the lab

---

## License

Public domain / CC0 / Unlicense – do what you want.
