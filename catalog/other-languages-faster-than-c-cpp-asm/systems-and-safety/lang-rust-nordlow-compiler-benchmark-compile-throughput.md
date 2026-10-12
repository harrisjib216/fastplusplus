# rustc compile throughput vs gcc and g++ in nordlow/compiler-benchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> rustc at opt-level 0 builds a 40,000-function generated program 1.6-2.6x faster than GCC builds the C/C++ twin; clang beats it.

| | |
|---|---|
| **Beats** | C (gcc 15.3.0 and 16.2.1, clang 23.1.1) and C++ (g++ 15.3.0 and 16.2.1, clang++ 23.1.1) compiling the same generated arithmetic translation unit |
| **Claimed result** | README table (AMD Ryzen AI 7 350 run, tables updated 2026-10-09), Total=Build+Run us/f (untemplated / templated): rustc 187 / 238 vs C gcc-15 392, C gcc-16 454, C++ g++-15 303 / 600, C++ g++-16 486 / 566, C++ clang++ 236 / 107, C clang 118. Derived from page data: 2.1x faster than gcc-15 and 2.4x faster than gcc-16 on C, 1.6x faster than g++-15 and 2.6x faster than g++-16 on untemplated C++, 2.5x faster than g++-15 and 2.4x faster than g++-16 templated, 1.26x faster than clang++ untemplated; 1.6x slower than clang C (118) and 2.2x slower than clang++ templated (107). The README highlight says 'rustc (187 µs/f) significantly outpaces GCC-based C/C++ (\~450–486 µs/f)'; its Conclusions section, from an earlier run, says rustc (183 µs/f) 'handily outperforms both GCC-based C/C++ front-ends (\~418–455 µs/f)'. |
| **Workload** | nordlow/compiler-benchmark: compile (and run) one massive synthetic translation unit of arithmetic call chains, reported as microseconds per generated function ('Total=Build+Run [us/f]'), untemplated and templated variants. |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8 cores) at 5.09 GHz, Arch Linux, sample run as of 2026-09 |
| **Compiler and flags** | Flags are in the public harness cbench (README's ./benchmark is a symlink to it; the same flag code is in benchmark at d16d0a5, the 2026-10-09 commit that updated the README tables): gcc/clang C build = -Wall -Wextra -o &lt;exe&gt; with no -O flag (GCC/Clang default -O0), C++ uses -Wno-c++11-extensions instead of the warning flags; rustc gets no flags (RUSTC_FLAGS = [], so opt-level 0 through LLVM with debug assertions and overflow checks on by default; the cranelift RUSTC_NIGHTLY_FLAGS list is defined but unused); zig build-exe -fno-llvm -fno-lld -fno-clang (Debug mode, Zig's self-hosted x86_64 backend and linker). Versions from the README table: rustc 1.100.0-nightly, zig 0.18.0-dev.35+5e754304d, gcc 15.3.0 and 16.2.1, clang 23.1.1. Defaults: 200 chains x depth 200 = 40,000 functions per file, minimum of up to 10 builds (capped to 2-3 when a build exceeds 1-3 s), constants re-randomised per run to defeat caches. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: the README says rustc 'handily outperforms' the GCC front ends and notes that GCC and clang skip some C++ semantic checks that Rustc performs in full; no further mechanism is given. |
| **Adoption** | 119.7k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/rust-lang/rust) · [benchmark](https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md) |

## Verdict

One run of nordlow/compiler-benchmark on an AMD Ryzen AI 7 350 under Arch Linux (tables committed 2026-10-09) built and ran 40,000 generated arithmetic functions per language. rustc 1.100.0-nightly with no flags (opt-level 0, overflow checks on) took 187 us/f plain and 238 generic, against gcc 15.3.0 at 392, gcc 16.2.1 at 454, g++ 15.3.0 at 303/600 and g++ 16.2.1 at 486/566, all at default -O0 with warning flags only; clang 23.1.1 (118) and templated clang++ (107) were faster than rustc.

## Use it when

- Choosing a language for a project where unoptimised (debug) build latency of large, flat code matters and the C/C++ alternative would be built with GCC: rustc's full build ran 1.6x faster than g++ 15.3.0 and 2.4-2.6x faster than gcc/g++ 16.2.1 on 40,000 plain functions.
- Machine-generated Rust with many small non-generic functions in one crate, the shape measured (200 chains x 200 depth in one file).
- Generic code compared with GCC templates: templated rustc (238 us/f) beat g++ 15.3.0 (600) and g++ 16.2.1 (566) by about 2.4-2.5x, although the Rust generic source does less work (see gotchas).
- x86-64 Linux with the official rustup toolchain, where rust-lld is the default linker and keeps link time small.

## Skip it when

- If clang is the C/C++ compiler you would use: clang built the C version in 118 us/f (1.6x faster than rustc's 187) and clang++ built the templated C++ in 107 (2.2x faster than rustc's 238).
- Fast type-check feedback: rustc's check costs 86.3 us/f (141.5 generic), 6-7x gcc's and clang's syntax-only checks, so editor or `cargo check` loops on large files stay slower than for C.
- If compile speed is the main reason to pick a language: dmd (13 us/f), Zig (110), Odin (147) and C3 (153) all built the same program faster in the same table.
- Optimised builds or real projects: every compiler ran unoptimised, and the generated file has no crates, macros, traits beyond Add, or module graph; the README says real builds are dominated by headers, module resolution and stdlib footprint, none of which is exercised.
- Heavy generics: the generic variant costs 27% more per function than the plain one (238 vs 187 us/f), and its check 64% more (141.5 vs 86.3).

## How it is fast

Not in the front end: rustc's check (--emit=metadata: parse, type and borrow check) costs 86.3 us/f, against 11.9 for gcc -fsyntax-only and 13.5 for clang, so rustc's front end is about 7x slower than GCC's on this file. The lead comes after it. Build minus check is about 101 us/f for rustc (lowering, LLVM opt-level-0 code generation and linking) against about 380-442 us/f for gcc 15/16, whose -O0 code generation alone (Compile 193.8 and 400.1) is slower than clang's LLVM path (77.9); rustc uses the same LLVM backend family as clang (derived from page data). Since Rust 1.90 the official x86_64-unknown-linux-gnu toolchain also links with the bundled rust-lld by default, while the harness leaves gcc and clang on the system default linker. rustc's default 16 codegen units can run LLVM in parallel threads, but the harness pins each compiler to one core, so that parallelism did not count.

## Compared with alternatives

Among the nordlow/compiler-benchmark siblings rustc is the slowest untemplated (187 us/f vs Zig 110, Odin 147, C3 153, dmd 13) and beats only C3 on generics (238 vs 255); pick it when you want Rust's checked semantics and are comparing against a GCC-built C/C++ debug workflow, not for the fastest compiler in the table.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (rustc, normally installed with rustup; prebuilt binaries per release channel) |
| **Dependencies** | a system C compiler driver (cc) for linking; on x86_64-unknown-linux-gnu the official builds bundle rust-lld and use it by default since 1.90 |
| **Minimum toolchain** | rustc 1.100.0-nightly as measured; rust-lld default linking needs Rust 1.90 or later on x86_64-unknown-linux-gnu |
| **Platforms** | measured on x86-64 Linux only (x86_64-unknown-linux-gnu is a Tier 1 target: kernel 3.2+, glibc 2.17+); rustc targets many other platforms, none measured here |
| **Thread safety** | not applicable (command-line compiler) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw specific to Rust: bm_Rust loops over rustup channels ['stable', 'nightly'] and calls `rustup default <channel>` before each pass, with no lock, while the four Rust tasks (check and build, plain and generic) run in parallel pool workers through the rustup proxy `rustc`. An overlapping task can switch the global toolchain under another task's timed runs, and the result key (language, templated, executable) ignores the version, so the nightly pass silently overwrites the stable pass and the '1.100.0-nightly' label is whatever `rustc --version` printed at probe time. Running the suite also leaves the machine's rustup default changed.
- No link-free number for Rust: the harness registers only check and build for Rust (Compile is N/A), so Rust's only timing is Total, which includes linking with rust-lld while the gcc and clang rows link with the system default linker. The untemplated C/C++ rows' Total-minus-Compile gaps (link plus noise) range from 33 to 198 us/f, as large as rustc's whole 116 us/f margin over g++-15, and the templated g++-15 and clang++ Totals are below their own Compile. The conservative comparison, rustc's full build against GCC's link-free compile, gives about 1.0x against gcc-15 C (187 vs 193.8), 1.4x against g++-15 (269.6), 2.1x against gcc 16.2.1 (400.1) and 2.0x against g++ 16.2.1 (372.3) (derived from page data).
- Unequal work in both directions: rustc at opt-level 0 turns on debug assertions and overflow checks, so every `+` gets a checked add and panic path (against rustc; output 360 B/f vs gcc's 121 also includes statically linked std). But the generic Rust source drops the per-function constants that the generic C++ source keeps (leaf `x`, chain `x + prev(x)`), so the 2.4-2.5x templated ratio compares less code, and that source is byte-identical on every repetition despite the suite's per-run constant randomisation.
- One run, one laptop: tasks run concurrently, one worker pinned per selected CPU on a Zen 5/Zen 5c part, builds over 3 s (rustc and every GCC row) keep the minimum of only 2 runs, nothing checks the program's output, and the README's own earlier run differs (rustc 183, GCC 418-455, clang 87). Its headline range '\~450-486 us/f' for GCC quotes only the GCC 16 rows, which the README itself flags as a regression.

## Known shortcomings

- Compile time of unoptimised builds (gcc/clang -Wall -Wextra at default -O0, rustc with no flags), not run time at -O3; slower than clang C (118 vs 187 us per function, 1.6x), so the win is over the GCC backend, not the language; the templated Rust source omits constants; single noisy run.
- Harness flaw specific to Rust: bm_Rust runs `rustup default stable` then `nightly` with no lock while the four Rust tasks run in parallel, so the global toolchain can switch under another task's timed runs; the result key ignores the version, so the nightly pass silently overwrites the stable pass and the '1.100.0-nightly' label is unreliable. Rust has no link-free Compile column: its Total includes rust-lld (default since 1.90) while gcc and clang use the system linker. A conservative ratio (rustc full build against GCC's link-free compile) is 1.0x gcc-15, 1.4x g++-15 and 2.0-2.1x GCC 16; the rustc front end alone is 7x slower than gcc (check 86.3 vs 11.9 us per function). Retiered to C.

## Caveats and trade-offs

Compile-time comparison of unoptimised builds on one synthetic translation unit of 40,000 arithmetic functions with no headers, standard library or module resolution (the README says it does not reflect real builds); not the wave's run-time -O3 comparison. The README does not state flags, but the harness does: gcc/clang get only -Wall -Wextra (default -O0) and rustc gets none (opt-level 0, debug assertions and overflow checks on), so optimisation levels are matched at 'unoptimised'. Not a language win: clang compiles the same C 1.6x faster than rustc (118 vs 187 us/f) and clang++ templated is 2.2x faster (107 vs 238); the margin over GCC comes from GCC's slower -O0 pipeline (gcc-16 compile-only 400 us/f against clang's 78) and a GCC 15 to 16 regression the README itself flags. The templated Rust source omits the per-function constants that the C++ templated source carries (cbench Rust leaf 'x', chain 'x + prev(x)'), so the 2.5x templated ratio compares slightly less code. One sample run with a large run-to-run spread: the README's Conclusions section (an earlier run) gives clang 87, rustc 183 and GCC 418-455 us/f, and in the table the gcc-15 C build (392) is twice its compile-only time (193.8) while the other GCC rows differ by 12-31%. Tasks run concurrently in a multiprocessing pool pinned to cores chosen by cpu_topology.py heuristics on a Zen 5/Zen 5c part, so rows may have run on different core types. GCC and clang skip some C++ semantic checks that rustc performs in full (README note). The sibling record for D (dmd) is from the same table. Independent suite, but a small one (167 stars), one machine. [retier] Enricher: bm_Rust runs `rustup default stable` then `nightly` with no lock while the four Rust tasks run in parallel pool workers through the rustup proxy, so the global toolchain can switch under another task's timed runs; the result key ignores the version, so the nightly pass silently overwrites the stable pass and the '1.100.0-nightly' label is unreliable. Rust has no link-free Compile column: its Total includes rust-lld (default since 1.90) while gcc and clang use the system linker. A conservative ratio (rustc full build against GCC's link-free compile) is 1.0x gcc-15, 1.4x g++-15 and 2.0-2.1x GCC 16; the rustc front end alone is 7x slower than gcc (check 86.3 vs 11.9 us per function).

Compile speed only; rustc adds +30% build time for templated (generic) code in this suite.

## Maintenance

rustc is actively developed (rust-lang/rust: 343,164 commits, 119.7k stars, Apache-2.0 OR MIT); the evidence is a single-machine run by an independent developer whose public harness (nordlow/compiler-benchmark, commits through 2026-10-12) has a rustup channel race that makes the Rust row's toolchain label unreliable, so re-run with one pinned toolchain before quoting ratios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** Upgraded B to A: independent public harness (nordlow/compiler-benchmark cbench: bm_Rust, gcc_clang_op_flags, bm_C_and_Cxx_using_gcc/clang) fixes every flag (gcc/clang -Wall -Wextra at default -O0, rustc with no flags at opt-level 0), the README table names every compiler version, and the CPU is stated (AMD Ryzen AI 7 350, Arch Linux). All README numbers in the claim match the Rust, C and C++ rows.
- **Retiered** A to C: Downgraded from A to C: the harness cannot say which toolchain it timed (bm_Rust switches the global rustup default between stable and nightly with no lock while four Rust tasks run in parallel, and the nightly pass overwrites the stable result under a key that ignores the version), and the Rust Total includes a rust-lld link while gcc and clang get a link-free Compile column; the conservative ratio against gcc-15's link-free compile is 1.0x (Odin sibling kept A because its win survives the same asymmetry).
- **Verifier notes:** Numbers and ratios check out against the README table; tier raised to A because the public harness pins every flag (no -O for gcc/clang/rustc) and the CPU and versions are stated. Shortcomings to record: compile-time of unoptimised builds on one synthetic file (off the wave's run-time -O3 baseline), rustc is slower than clang C (1.6x) and clang++ templated (2.2x) so the win is over GCC's backend, not a language effect; templated Rust source omits constants; single noisy run (README's own earlier run differs by up to 36% for clang).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-87 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/d16d0a5/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cpu_topology.py>
  - <https://github.com/nordlow/compiler-benchmark>
  - <https://github.com/nordlow/compiler-benchmark/commits>
  - <https://github.com/nordlow/compiler-benchmark/commits/master/README.md>
  - <https://github.com/rust-lang/rust>
  - <https://github.com/rust-lang/rust/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cpu_topology.py>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/process_timer.py>
  - <https://github.com/nordlow/compiler-benchmark/commits>
  - <https://github.com/rust-lang/rust>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/src/doc/rustc/src/codegen-options/index.md>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/compiler/rustc_target/src/spec/targets/x86_64_unknown_linux_gnu.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/compiler/rustc_target/src/spec/base/linux_gnu.rs>
  - WebSearch snippet only: https://blog.rust-lang.org/2025/09/01/rust-lld-on-1.90.0-stable (rust-lld default linker on x86_64-unknown-linux-gnu from Rust 1.90.0)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/nordlow/compiler-benchmark#compile-throughput`) · [data/wave14/enrich/raw/lang_rust_nordlow_compiler_benchmark_compile_throughput.json](../../../data/wave14/enrich/raw/lang_rust_nordlow_compiler_benchmark_compile_throughput.json) (enrichment confidence 0.6)

</details>
