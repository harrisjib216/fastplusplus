# lua-rs (luars, pure Rust Lua 5.5)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust Lua 5.5 interpreter and embedding crate; roughly at parity with C Lua 5.5, faster on macOS, slower on x86 Linux.

| | |
|---|---|
| **Beats** | Native Lua 5.5 (C reference interpreter) |
| **Claimed result** | Windows snapshot (docs/benchmarks/windows.md, Ryzen 7 5800X), luars throughput as % of native Lua 5.5: arithmetic 111, control flow 87, locals 132, functions 92, closures 80, multiple returns 78, tables 92, table library 118, iterators 93, math 98, metatables 78, OOP 92, coroutines 152, errors 103 (9 of 14 scripts below parity). macOS snapshot (docs/benchmarks/macos.md, Apple M4, contributed by @sniper00): arithmetic 136, control flow 143, locals 143, functions 119, closures 99, multiple returns 105, tables 141, table library 301, iterators 123, math 140, metatables 121, OOP 109, coroutines 113, errors 120 (13 of 14 above parity); string scripts about 99 and 120. README: Linux runs are often 20% to 40% slower than native Lua on broad coverage while winning a subset (no Linux numbers in the repo). |
| **Workload** | Script-level Lua microbenchmarks in benchmarks/ (bench_arithmetic.lua through bench_errors.lua) run by run_benchmarks.ps1 (Windows) or run_benchmarks.sh (macOS); each value is luars throughput divided by native Lua 5.5 throughput times 100. The runners execute 18 scripts but the snapshot charts show 14 (bench_tailcall, bench_gc, bench_strings and bench_string_lib are left out of the Windows chart). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800X (Windows snapshot); Apple M4 (macOS snapshot) |
| **Compiler and flags** | luars: cargo build --release with the default release profile (no custom [profile.release] in the workspace Cargo.toml); rustc version not stated. Native Lua build used for the snapshots not stated (the CI workflow builds lua-5.5.0 with make linux / make macosx and CMake Release on Windows, but CI numbers are not in the repo). |
| **Adoption** | 58 stars |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/CppCXY/lua-rs) · [benchmark](https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/docs/benchmarks/windows.md) |

## Verdict

With in-script os.clock timing and one run per interpreter, the Windows snapshot (Ryzen 7 5800X, run_benchmarks.ps1) puts luars at 78% to 152% of native Lua 5.5 throughput, below parity on 9 of 14 script groups, and a contributor's Apple M4 run (run_benchmarks.sh) at 99% to 301%, above parity on 13 of 14. The luars binary is cargo --release with the default profile plus mimalloc, rustc and native-Lua build flags are not stated, and the README reports Linux as often 20-40% slower with no Linux numbers in the repo.

## Use it when

- Rust host applications that want Lua 5.5 scripting with no C toolchain, cross-compilation of liblua or FFI layer (pure cargo build).
- Embedding Lua in a WASM build (crates/luars_wasm) where linking C Lua is awkward.
- Workloads heavy on table.sort/insert/remove/move, coroutines or local-variable arithmetic, where the repo's own runs show luars ahead of C Lua (Windows coroutines 152%, table library 118% to 301%).
- Apple Silicon hosts: the contributed M4 run is above parity on 13 of 14 script groups.

## Skip it when

- C or C++ hosts: there is no lua_State C API, so it cannot replace liblua; use C Lua, Luau or LuaJIT there.
- x86-64 Linux servers where throughput matters: the README says broad Linux runs are often 20-40% slower than native Lua, and on Windows 9 of 14 script groups are below parity (closures 80%, multiple returns 78%, metatables 78%).
- Programs that load C modules (package.loadlib always fails), share precompiled bytecode with C Lua (string.dump format is luars-only) or depend on full debug-library behavior (debug.setuservalue/getuservalue missing, hooks partly implemented).
- Hosts that need multi-threaded access to one VM: the VM is single-threaded internally (Rc, raw pointers); the `unsafe-send` feature only marks types Send+Sync and leaves exclusion to the caller.
- Safety-critical embedding: the code is AI-assisted (README), unsafe sits in GC/value layout and VM hot paths, Miri tests run with stacked borrows disabled, and issue #28 reported a SIGSEGV from running collect_garbage() during a host-side table iteration.

## How it is fast

It is a register-based Lua VM in Rust with tagged-pointer values, compact GC object layouts and unsafe stack/upvalue pointer fast paths on the hot interpreter loop; recent commits trim per-call CallInfo work and string interning. Some of the wins come from library-level algorithm choices rather than the interpreter loop: table.sort with the default comparator on all-integer, all-float or all-string arrays copies the array into a Vec and calls Rust's sort_unstable_by (pdqsort, linear on presorted input) instead of Lua's quicksort with per-compare VM calls. The `lua` binary also installs mimalloc as its global allocator.

## Compared with alternatives

Pick luars over Luau or LuaJIT Remake only when the host is Rust (or WASM) and you want stock Lua 5.5 semantics without linking C; from C++ Luau (geomean about 1.5x over PUC Lua) is both faster and has a C API. Against Prolua, the other from-scratch reimplementation in the catalogue (0.60x to 1.19x of Lua 5.4.8's time), luars has the richer embedding toolkit and the newer language version, and like Lua-CSharp it is chosen for host-language purity rather than raw speed.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | chrono, itoa, luars-derive; optional serde and serde_json (feature serde); js-sys on wasm32; the luars_interpreter binary adds mimalloc and luars_debugger |
| **Minimum toolchain** | Rust edition 2024 (so Rust 1.85 or newer); no rust-version field on crates.io and no rust-toolchain.toml in the repo |
| **Platforms** | Windows and macOS (Apple M4) measured; Linux, Windows and macOS built in the GitHub Actions benchmark workflow; wasm32 via crates/luars_wasm |
| **Thread safety** | Single VM is single-threaded (Rc and raw pointers internally); opt-in `unsafe-send` feature adds unsafe impl Send/Sync for framework bounds, with no internal locking |
| **Drop-in for the baseline** | partial — Lua 5.5 language and stdlib compatible at script level (upstream all.lua passes with testC skips), but no C API, no C modules, incompatible bytecode, and a Rust-only embedding API |

## Gotchas

- os.clock returns wall-clock seconds since VM start (std::time::Instant via platform_time.rs), not process CPU time as C Lua's clock() gives on Linux and macOS; scripts that time themselves get different semantics, and in the repo's benchmarks native Lua is timed in CPU time and luars in wall time on POSIX (this skews slightly against luars, not for it). The difference is not listed in docs/Different.md.
- Harness: the per-script percentages in docs/benchmarks/\*.md are hand-summarized from per-subtest ops/sec printed by one run of each interpreter; there is no aggregation script, no repetition or variance, and run_benchmarks.sh falls back to whatever `lua` is on PATH when `lua5.5` is absent without checking its version (the macOS contributor's native Lua version and build are unrecorded). The snapshots were last touched 2026-03-30 (macOS) and 2026-04-22, five months before the current 0.26.3 code.
- bench_table_lib's 'sorted' and 'reversed' subtests measure an algorithm change: luars's default table.sort on homogeneous arrays is Rust pdqsort (linear on presorted input), C Lua's is median-of-3 quicksort calling lua_lessthan per compare. The same fast path treats NaN as equal to everything (partial_cmp unwrap_or Equal) and compares mixed integer/float arrays through f64, so orderings differ from C Lua for NaN or integers above 2^53, and Rust documents that sort_unstable_by may panic when the comparator is not a total order.
- docs/Different.md lists further gaps: multi-value concatenation across a coroutine yield does not resume correctly, the stack-overflow limit differs from C Lua, os.date never sets isdst, no locale-dependent number parsing, and GC does not shrink stacks.

## Known shortcomings

- Mixed result vs native Lua 5.5: on Windows 9 of 14 scripts are slower and the README says Linux is 20-40% slower; docs/benchmarks/macos.md (Apple M4, run by @sniper00) has 13 of 14 faster with the table library at 301%. The luars binary uses mimalloc as global allocator while native Lua uses system malloc; native Lua build and rustc version not stated; README says the code is AI-assisted.
- Enricher: snapshot percentages are hand-summarised from one run with no aggregation script or variance; run_benchmarks.sh falls back to any lua on PATH without a version check, so the macOS native build is unknown; snapshots date from 2026-03/04 while the code is now 0.26.3. luars os.clock is wall time (Instant) while native POSIX clock() is CPU time. table.sort's default path is Rust pdqsort (linear on presorted input), so the tablelib 118%/301% rows are partly an algorithm change; that path treats NaN as Equal and compares int/float via f64. No C API. Issue #28 SIGSEGV (GC during host table iteration).

## Caveats and trade-offs

Mixed result: on Windows 9 of 14 scripts are slower than native Lua 5.5, and the README says Linux runs are often 20-40% slower (no maintained Linux snapshot, only a CI workflow whose output is not in the repo); the faster macOS snapshot (13 of 14 above parity, table library 301%) was contributed by a third party on an Apple M4 with no build details. The author attributes the Windows coroutine win (152%) partly to native Lua's longjmp cost on Windows. The luars interpreter binary installs mimalloc as its global allocator while native Lua uses the system malloc, which may account for part of the table/GC-heavy wins. rustc version and native Lua build flags for the snapshots are not stated; tailcall, GC and string scripts are omitted from the Windows chart (strings because of timer resolution). The README states the project was written through AI-assisted programming.

Pure Rust Lua 5.5 runtime with embedding toolkit, derive macros, debugger integration and a WASM target; usable from C++ only through a C boundary the project may expose, not as a drop-in C library. Aims at Lua 5.5 compatibility rather than a different language.

## Maintenance

Actively developed (0.26.3 on crates.io, about 61k downloads, last commit 2026-09-11 with a run of perf commits) and MIT-licensed, but young, AI-assisted and still changing its unsafe internals, so pin a version and run your own workload against C Lua before adopting it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from the repo's own runner (run_benchmarks.ps1 / run_benchmarks.sh over benchmarks/bench_\*.lua) against native Lua 5.5 on a named CPU (Ryzen 7 5800X; macOS snapshot on Apple M4), but the rustc version and the native Lua build/compiler/flags used for the snapshots are not stated, so it falls short of A.
- **Verifier notes:** Numbers on windows.md match the record exactly; the record missed docs/benchmarks/macos.md, which does carry numbers (Apple M4, mostly faster). Shortcomings to record: mixed/not faster on Windows and Linux, unequal allocators (mimalloc vs system malloc), native Lua build unstated, AI-assisted code (now confirmed in the README, not snippet only).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** same-allocator comparison with stated builds; repeated runs with a pinned native Lua build
- **Pages the verifier opened:**
  - <https://github.com/CppCXY/lua-rs>
  - <https://github.com/CppCXY/lua-rs/commits>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/docs/benchmarks/windows.md>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/docs/benchmarks/macos.md>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/run_benchmarks.ps1>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars_interpreter/Cargo.toml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars_interpreter/src/bin/main.rs>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars/Cargo.toml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/docs/benchmarks/windows.md>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/docs/benchmarks/macos.md>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/run_benchmarks.ps1>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars/Cargo.toml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars_interpreter/Cargo.toml>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars_interpreter/src/bin/main.rs>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/rust-toolchain.toml>
  - <https://github.com/CppCXY/lua-rs/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/benchmarks/bench_table_lib.lua>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/benchmarks/bench_locals.lua>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/benchmarks/bench_arithmetic.lua>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/benchmarks/run_all.lua>
  - <https://github.com/CppCXY/lua-rs/tree/main/crates/luars/src>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars/src/platform_time.rs>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars/src/stdlib/os.rs>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars/src/stdlib/mod.rs>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars/src/stdlib/table.rs>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/crates/luars/src/stdlib/sort_table/mod.rs>
  - <https://raw.githubusercontent.com/CppCXY/lua-rs/HEAD/docs/Different.md>
  - <https://crates.io/api/v1/crates/luars>
  - <https://github.com/CppCXY/lua-rs/issues?q=is%3Aissue>
  - <https://github.com/CppCXY/lua-rs/issues/28>
  - <https://github.com/CppCXY/lua-rs/issues/34>
  - <https://github.com/CppCXY/lua-rs/commits/main>
  - <https://github.com/CppCXY/lua-rs/commits/main/docs/benchmarks>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/cppcxy/lua-rs`) · [data/wave12/enrich/raw/github_com_cppcxy_lua_rs.json](../../../data/wave12/enrich/raw/github_com_cppcxy_lua_rs.json) (enrichment confidence 0.75)

</details>
