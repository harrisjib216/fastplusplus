# stryke (strykelang): Perl 5 compatible interpreter with bytecode VM and Cranelift JIT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust Perl 5 interpreter with bytecode VM and Cranelift JIT; beats perl 5 on tiny scripts, LuaJIT only on three gamed rows.

| | |
|---|---|
| **Beats** | LuaJIT 2.1.1774896198 (also perl 5.42.2, Python 3.14.4, Ruby 4.0.2, Julia 1.12.6, Raku) |
| **Claimed result** | README table (stryke v0.7.7, rustc unstated, millisecond workloads including startup): faster than perl 5.42.2 on 7 of 8 rows (startup slower, 3.3 vs 2.3 ms); LuaJIT faster on 5 of 8. The regex row (0.07x vs LuaJIT, 7.1x vs perl) measures a memoised match (the engine runs once for 100,000 identical matches) and is not a regex-speed result; the map_grep, array and fib rows run MapIntMul/GrepIntModEq superinstructions, a native sort_by on presorted input and a fib_like evaluator respectively. |
| **Workload** | Eight small scripts (startup, fib, loop, string, hash, array, regex, map_grep) timed end to end with hyperfine, mean of at least 10 runs with 3 warmups, process startup included. |
| **Metric** | throughput |
| **Hardware** | Apple M5, 18 cores |
| **Compiler and flags** | Cargo release profile opt-level 3, fat LTO, codegen-units 1, panic abort (from Cargo.toml); rustc version not stated; measured binary reports stryke v0.7.7; LuaJIT build flags not stated |
| **Adoption** | 5 stars; crate strykelang on crates.io (4454 downloads, 956 recent; created 2026-04-19) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/MenkeTechnologies/strykelang) · [benchmark](https://github.com/MenkeTechnologies/strykelang) |

## Verdict

README table from bench/run_bench_all.sh (hyperfine, mean of 10 runs after 3 warmups, process start-up included) on an Apple M5 with 18 cores: stryke v0.7.7 beats LuaJIT 2.1.1774896198 on loop (3.2 vs 4.3 ms), array (9.8 vs 59.0 ms) and regex (12.6 vs 178.2 ms), and loses the other five rows. Against perl 5.42.2 it wins 7 of 8 rows, losing start-up. The regex win comes from a match-result memo, the array win from a native sort of presorted input, and fib from a fib-shape evaluator.

## Use it when

- Existing Perl 5 one-liners and short scripts where perl's interpreter overhead dominates, and you can test them against stryke's parity gaps first.
- Data-parallel scripting over all cores with pmap/pgrep/pfor (rayon work stealing) when you want Perl syntax instead of Python or Go.
- Integer-heavy loops and numeric sorts in Perl syntax, where the block JIT and the native sort path apply.
- Interactive or shell-pipeline use (-n/-p/-e) on Linux or macOS where a 3 ms start-up is acceptable.

## Skip it when

- As a LuaJIT substitute: it runs Perl, not Lua, and LuaJIT is faster on 5 of the 8 README rows (startup, fib, string, hash 3.4x, map_grep 4.2x).
- Perl code that relies on CPAN XS modules or exact perl semantics: XS is unsupported apart from a native subset, and docs/BUGS.md documents about 158 open parity gaps and bugs.
- Long-running steady-state compute you want to judge from the README: every row includes process start-up and lasts 2-14 ms, and no steady-state comparison with LuaJIT is published.
- Windows or minimal-footprint deployments: CI builds only x86-64 Linux and x86-64/aarch64 macOS, the README cites a 44 MB static binary, and the crate pulls a large dependency tree (Cranelift, PCRE2, ureq, svg2pdf, pdf-extract, zshrs, fusevm).
- Projects needing a mature, widely used runtime: 5 stars, one author, 219 crate versions since 2026-04-19.

## How it is fast

Source is lowered to bytecode for a match-dispatch VM with NaN-boxed u64 values and frame-local slot ops; hot loops and linear subs go through a Cranelift block JIT, and string-bearing segments through the author's fusevm Cranelift JIT. Several benchmark rows are carried by idiom recognisers rather than the JIT: `map { $_ * K }` and `grep { $_ % M == R }` compile to the native superinstructions MapIntMul and GrepIntModEq (map_grep_fast.rs), `sort { $a <=> $b }` becomes a native Rust sort_by (sort_fast.rs), fib-shaped recursive subs run in fib_like_tail.rs, and non-/g regex matches are memoised on (pattern, flags, haystack).

## Compared with alternatives

Pick stryke only when the code is Perl and you want a faster perl; for a fast embeddable scripting JIT, LuaJIT itself, WrenJIT or libriscv have like-for-like LuaJIT comparisons, and XS (xs-lang) has the same start-up-dominated timing caveat.

## Integration

| | |
|---|---|
| **Form** | crate (library `stryke`, also built as a staticlib) plus CLI binaries stryke / st / s; Homebrew tap |
| **Dependencies** | rayon, regex, fancy-regex, pcre2 (C PCRE2), cranelift 0.130 (jit, codegen, frontend, native, module), fusevm 0.26.7, zshrs 0.13.1, crossbeam, dashmap, ureq, svg2pdf, pdf-extract and many more (about 200 dependency lines in Cargo.toml) |
| **Minimum toolchain** | Rust stable, edition 2021 (no rust-version field; CI uses dtolnay/rust-toolchain@stable) |
| **Platforms** | x86-64 Linux, x86-64 and aarch64 macOS (CI release matrix); Windows not built in CI; signal-hook is a unix-only dependency |
| **Thread safety** | Each parallel block runs an isolated VM with a captured scope on rayon workers; shared state goes through varsync (Arc&lt;Mutex&gt;); thread safety of the embedding API is not documented |
| **Drop-in for the baseline** | partial — not a drop-in for LuaJIT (different language); for perl 5 it runs many scripts via `stryke script.pl` (with --compat for strict Perl semantics) but not XS modules, and documented parity gaps remain |

## Gotchas

- Harness flaw in the regex row: bench_regex.pl matches one constant string against one constant pattern 100,000 times, and regex_match_execute (interpreter.rs in 0.7.7, vm_helper.rs now) returns the memoised result whenever pattern, flags, multiline and haystack equal the previous non-/g match, so the regex engine runs once and the other 99,999 iterations are a string compare. The 0.07x vs LuaJIT (which runs Lua patterns every iteration) and 7.1x vs perl measure the memo, not regex speed. In v0.7.7, the build behind the table, the memo was keyed on the uninterpolated pattern text, so a loop over an interpolated pattern (/^\$p/) on an unchanged string replayed a stale answer; the current source carries a comment describing that fix.
- Other rows also hit shape-specific paths that the perturbed-source check in run_bench.sh cannot catch, because it only renames \$i/\$sum/\$count: map_grep uses MapIntMul and GrepIntModEq superinstructions, array uses a native Rust sort_by for { \$a &lt;=&gt; \$b } on already-sorted input (a single run, against LuaJIT's C quicksort calling the comparator), and fib uses the fib_like evaluator. All four paths are present in the published 0.7.7 crate, whose bench scripts match the current ones apart from the fib sub's name.
- All rows include process start-up: stryke's startup row (3.3 ms) is above its loop row (3.2 ms), and it is slower than perl (2.3 ms) and LuaJIT (1.5 ms) on start-up, although the README text says stryke beats perl on all 8.
- The README numbers come from v0.7.7 (crates.io, published 2026-04-19); the current crate is 0.17.59, and no newer table has been published.

## Known shortcomings

- Workloads take milliseconds and include startup (the loop row total sits below stryke's own startup row); the regex row compares Lua patterns with a regex engine, the array row sorts already-sorted input, and the fib row runs a fib-shaped fast path in vm.rs (fib_like_tail with an explicit stack). The README says faster than perl 5.42.2 on all 8 rows but its own table shows startup slower (3.3 vs 2.3 ms), so 7 of 8; LuaJIT is faster on 5 of 8 rows. Measured build v0.7.7 (current crate 0.17.59), rustc version unstated. bench_fusion.rs folded the exact bench scripts to constants in 0.1.13-0.1.22 (commit a0e04a9) and was unwired by 0.1.26; the v0.7.7 numbers postdate that, so the evidence stands. Rust.
- Enricher: the regex row measures memoisation, not regex speed (the bench matches a constant string against a constant pattern 100,000 times and regex_match_execute returns the cached result when pattern, flags and haystack equal the previous non-/g match, so the engine runs once); in the v0.7.7 crate behind the table the memo was keyed on uninterpolated pattern text (a stale-answer bug for /^\$p/ loops, later fixed). The same crate runs MapIntMul and GrepIntModEq superinstructions for map_grep, a native Rust sort_by on presorted input for array, and a fib_like evaluator for fib; run_bench.sh's perturbation check only renames variables and catches none of these.

## Caveats and trade-offs

First-party numbers from the README benchmark section, produced by bench/run_bench_all.sh. They were measured on stryke v0.7.7, not the current 0.17.59, and the rustc version and LuaJIT build are not stated. Each script finishes in 2-14 ms with process startup included, so the rows mostly measure startup and tiny loops, not steady-state JIT speed. In the loop row stryke's total (3.2 ms) is below its own startup row (3.3 ms), so the loop cost is lost in startup noise. The rows are not like-for-like: in regex, LuaJIT runs Lua patterns, which backtrack from each start position, while stryke uses a regex engine. The array row sorts already-sorted input, which probably favours stryke's native adaptive sort over Lua's quicksort table.sort (reviewer inference, not measured). The fib row hits a fib-shape fast path in vm.rs (sub tagged fib_like, evaluated by fib_like_tail::eval_fib_like_recursive_add with an explicit stack; source comment: 'bench_fib collapses from \~2.7M recursive VM calls to a single while loop'). That path still does the full recursion work, but it measures a specialised evaluator, not general calls or the Cranelift JIT. History: strykelang/bench_fusion.rs held AST-shape matchers for the exact bench_string/hash/array/regex/map_grep/loop scripts that folded them to constants. It was wired into the compiler in 0.1.13-0.1.22 (commit a0e04a9 'fusion', 2026-04-09) and unwired by 0.1.26. The file remains in the tree as dead code, and the v0.7.7 numbers postdate the removal. bench/run_bench.sh (perl only) has a perturbed-source column to catch such matchers, but run_bench_all.sh, which produces the LuaJIT table, does not. The README text claims wins over perl on all 8 rows, but its own table shows stryke slower on startup. LuaJIT wins 5 of 8 rows, and the LuaJIT comparison is one column in a Perl-centred suite. [retier] Workloads take milliseconds and include startup (the loop row total sits below stryke's own startup row); the regex row compares Lua patterns with a regex engine and, in stryke, hits a memo cache after the first match (in v0.7.7 keyed on uninterpolated pattern text, a stale-answer bug later fixed); the array row sorts already-sorted input with native Rust sort_by; the fib row runs a fib-shaped fast path in vm.rs; map_grep runs superinstructions; run_bench.sh's perturbation check only renames variables. bench_fusion.rs folded the exact bench scripts to constants in 0.1.13-0.1.22 (commit a0e04a9), unwired by 0.1.26; the v0.7.7 numbers postdate that. Current crate 0.17.59. Rust.

Runs Perl 5 source (a superset with parallel primitives), so it is a Perl runtime rather than a Lua or general JIT; Rust crate, no C API seen; JIT can be switched off with STRYKE_NO_JIT=1.

## Maintenance

Very active single-author MIT project (1,983 commits, last commit 2026-10-05, 0.17.59 on crates.io, 5 stars) and installable via cargo or Homebrew. Its benchmark evidence is a stale v0.7.7 table whose regex, array, map_grep and fib rows are carried by memoisation and idiom fast paths, so treat the LuaJIT claim as unproven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table produced by the public harness bench/run_bench_all.sh (bench/bench_\*.pl vs bench_\*.lua) on a stated CPU (Apple M5, 18 cores) with release-profile flags in Cargo.toml, but the rustc version and LuaJIT build flags are not stated and the numbers come from stryke v0.7.7, an untagged build roughly ten minor versions behind the current crate (0.17.59), so not A; no independent measurement, so not B.
- **Verifier notes:** Numbers match the README table exactly, but the record's 'faster than perl on all 8' repeats a README claim that its own table contradicts (startup 1.43x slower). The evidence is valid but narrow: stryke beats LuaJIT only on loop (inside startup noise), array (presorted sort) and regex (Lua patterns vs a regex engine), and fib runs a fib-shape fast path. The bench-shape constant-folding (bench_fusion.rs) was active only in April 0.1.13-0.1.22 builds and is dead code now, so this is not a reject. Record as shortcomings: stale build (v0.7.7), startup-dominated millisecond workloads, unlike-for-like regex and array rows, and the fib-shaped fast path.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `stars_or_usage`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/README.md>
  - <https://github.com/MenkeTechnologies/strykelang>
  - <https://github.com/MenkeTechnologies/strykelang/tree/main/bench>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/run_bench_all.sh>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/run_bench.sh>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_regex.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_array.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_loop.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/Cargo.toml>
  - <https://github.com/MenkeTechnologies/strykelang/tree/main/strykelang>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/bench_fusion.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/fib_like_tail.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/vm.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/lib.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/a0e04a9/src/lib.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/a0e04a9/src/compiler.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/018c566/src/lib.rs>
  - <https://github.com/MenkeTechnologies/strykelang/commits/main>
  - <https://github.com/MenkeTechnologies/strykelang/commits/ceda9dc/src/bench_fusion.rs>
  - <https://github.com/MenkeTechnologies/strykelang/commit/75d6597>
  - <https://crates.io/api/v1/crates/strykelang>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/README.md>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/run_bench_all.sh>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/run_bench.sh>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_startup.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_startup.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_fib.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_fib.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_loop.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_loop.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_string.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_string.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_hash.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_hash.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_array.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_array.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_regex.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_regex.lua>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_map_grep.pl>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/bench/bench_map_grep.lua>
  - <https://github.com/MenkeTechnologies/strykelang/tree/main/strykelang>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/map_grep_fast.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/fib_like_tail.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/jit.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/compiler.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/vm.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/vm_helper.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/lib.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/bench_fusion.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/strykelang/main.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/MenkeTechnologies/strykelang/HEAD/docs/BUGS.md>
  - <https://crates.io/api/v1/crates/strykelang/versions>
  - <https://static.crates.io/crates/strykelang/strykelang-0.7.7.crate>
  - <https://github.com/MenkeTechnologies/strykelang>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/menketechnologies/strykelang`) · [data/wave12/enrich/raw/github_com_menketechnologies_strykelang.json](../../../data/wave12/enrich/raw/github_com_menketechnologies_strykelang.json) (enrichment confidence 0.75)

</details>
