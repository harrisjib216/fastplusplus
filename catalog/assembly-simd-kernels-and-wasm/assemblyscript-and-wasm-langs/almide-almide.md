# Almide

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Almide (statically typed language compiling to Rust and WebAssembly)` · `MIT OR Apache-2.0` · 🟢 active

> LLM-oriented statically typed language that compiles to Rust and WebAssembly; its native output beats Box-per-node Rust on two tree-allocation benchmarks.

| | |
|---|---|
| **Beats** | Ordinary hand-written Rust (Box-linked recursive enum, no arena, rustc 1.96.1 opt-level=3, LTO, 1 codegen unit) |
| **Claimed result** | Native output vs ordinary hand-written Rust on Apple M4 Pro (almide 0.62.0, 2026-09-08, median of 9 interleaved runs): binarytrees d17 134 ms vs 382 ms (0.35x time), d19 581 vs 1826 ms (0.32x); treealloc d20 112 vs 375 ms (0.30x), d21 221 vs 748 ms (0.30x). With the region window turned off (ALMIDE_REGION_OFF=1) the same Almide source is 1.10-1.26x slower than the Rust reference. ubuntu-latest CI runner (2026-10-03, almide 0.66.0 dev): binarytrees 0.581 (d17), treealloc 0.365 (d20). Arithmetic kernels (2026-07-30, rustc 1.96.1): n-body and spectral-norm 1.00x, fasta 1.16x and FFT 1.18x slower than Rust. Wasm leg: README ledger (2026-09-29, embedded wasm host vs native binary, min of 2x5 interleaved) gives wasm/native ratios of 0.67x (mapbuild) to 1.96x (listbuild_append), e.g. treealloc 1.04x, binarytrees 1.07x, nbody 1.10x, fft 1.53x; these ratios are on the README, not on BENCHMARKS.md, whose older dated wasm paragraph still describes FFT (\~3,500x) and mandelbrot (\~130x) cliffs. |
| **Workload** | Benchmarks-Game-style programs (binarytrees, treealloc, n-body, spectral-norm, fasta, FFT) on native output; wasm output measured as a ratio to native |
| **Metric** | throughput |
| **Hardware** | Apple M4 Pro (arm64), almide 0.62.0, 2026-09-08; also an ubuntu-latest CI runner |
| **Compiler and flags** | almide --release (emits Rust, cargo release profile opt-level=3 + LTO) vs handwritten Rust built by bench.py with rustc -C opt-level=3 -C lto=yes -C codegen-units=1; median of 9 interleaved runs after warmup; byte-identical stdout verified before timing. rustc 1.96.1 is stated for the 2026-07-30 scoreboard; the 2026-09-08 victory JSON records almide 0.62.0 but no rustc version (README says CI builds with 1.96.0). |
| **Adoption** | 35 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/almide/almide) · [benchmark](https://github.com/almide/almide/blob/develop/docs/project/BENCHMARKS.md) |

## Verdict

bench.py builds Almide `--release` output and hand-written Rust references (Box-linked recursive enum, one thread, no arena) with rustc -C opt-level=3 -C lto=yes -C codegen-units=1, checks byte-identical stdout, then times 9 interleaved runs after a warmup: on an Apple M4 Pro with almide 0.62.0 (2026-09-08) binarytrees took 134 vs 382 ms (d17) and 581 vs 1826 ms (d19), treealloc 112 vs 375 ms (d20) and 221 vs 748 ms (d21), while the same Almide source with the region window disabled was 1.10-1.26x slower than the Rust reference. The win is an arena against malloc/free per node, not better general codegen; arithmetic kernels are at parity and fasta/FFT are 1.16-1.18x slower.

## Use it when

- You want an LLM to write and repeatedly edit small programs and need compiler diagnostics that name the fix, with one source building both a native binary and a small self-contained wasm module (Hello world 325 B on develop).
- Allocation-heavy recursive-variant code whose tree lives for exactly one produce-then-consume expression (binarytrees/treealloc shape): the region window gives about 0.30-0.35x the time of Box-per-node Rust on an M4 Pro and 0.37-0.58x on an ubuntu-latest runner.
- Numeric kernels where parity with hand-written Rust is enough (n-body and spectral-norm 1.00x on M4 Pro, 1.03-1.07x on the CI runner).
- Programs that must produce byte-identical output natively and under wasmtime, e.g. reproducible CLI tools that also ship to the browser.

## Skip it when

- As evidence that a compiler beats Rust in general: a Rust program using an arena (bumpalo or typed-arena, as Benchmarks Game entries do) erases the win; issue #3586 records a hand-written Rust arena at 31.3 ms against Almide native 51 ms on binarytrees d19x12 (M4 Pro), and the project's own table shows Zig's arena at 88 ms vs 72 ms.
- Float-heavy code that calls sin/cos (deterministic software libm for cross-target byte identity costs about 1.6x on listbuild), fasta (1.16x slower) and FFT (1.18x slower) on M4 Pro.
- Trees that are held (`let t = make(d)` read twice), contain String payloads, touch globals or mut params, or cross a lambda: the window does not fire and the emitted Box code runs 1.10-1.26x slower than the Rust reference.
- Production use needing stability guarantees: pre-1.0, support limited to the latest release line, 35 stars, and the region-window PR (#2032) merged with no reviews listed.
- Comparisons against JavaScript/V8 or Emscripten (this category's baseline): the repo never measures them; its wasm numbers are only ratios to its own native binary.

## How it is fast

The below-1.0 rows come from one optimisation, the region window (#1991, PR #2032): when the effect system proves a `check(make(d))` pair region-pure (no effects, no globals, scalar result), the compiler clones both functions as `__rgn_` twins over Copy enums whose recursive fields are handles into a thread-local bump arena, and rewinds the arena once per tree instead of freeing each node. Everything else is ordinary rustc/LLVM codegen with Perceus-style ownership inference deciding clones and drops, which is why arithmetic kernels sit at parity with hand-written Rust and the IR optimiser's own passes measure 1.00x in the project's ablation.

## Compared with alternatives

Pick Almide over MoonBit, Kotlin/Wasm or wasm_of_ocaml only when you want one LLM-friendly source that builds both a Rust-backed native binary at Rust parity and a tiny wasm module with byte-identical output; for beating JavaScript in V8 those siblings (MoonBit 7.7x over plain JS iterator chains, Kotlin/Wasm vs Kotlin/JS) carry the relevant evidence and Almide carries none.

## Integration

| | |
|---|---|
| **Form** | compiler binary (Rust crate, single executable; native output is a cargo-built Rust binary, wasm output is a self-contained WASI module) |
| **Dependencies** | Building the compiler needs Rust 1.96+ (the binary embeds a wasmtime host); native builds of user programs need a Rust toolchain and cargo; the emitted native binary has 0 crate dependencies |
| **Minimum toolchain** | Rust 1.96 (rust-version of the almide package; CI builds with 1.96.0) |
| **Platforms** | macOS (arm64 measured), Linux (ubuntu-latest CI, x86-64 and Neoverse-V2 in issue #3586), Windows installer; wasm32 WASI output runs on stock runtimes |
| **Thread safety** | Region arena is thread-local and its handles are !Send/!Sync, so a window never spans threads; `fan` runs arms on threads natively only for pure callbacks over scalars |
| **Drop-in for the baseline** | no |

## Gotchas

- The region arena never returns memory: chunks start at 64 KiB, double up to 64 MiB each, and are kept for the life of the thread at the high-water mark; rewind does not drop anything (region types are Copy by construction).
- Soundness of the window rests on the compiler's region-pure verdict: the prelude's own comment says a wrong verdict is a silent use-after-rewind that reads stale bytes; only a build-time ALMIDE_REGION_TRAP_STALE=1 build adds generation checks that panic instead.
- Provenance gaps: results/2026-09-08-m4pro-victory-1330.json is a hand-assembled summary (medians and ratios only, no per-run arrays, no rustc version) rather than bench.py's normal output format; the README's fannkuchredux victory row (0.21 at n10, 0.12 at n11, stated as M4 Pro 2026-09-08 median of 9) has no matching raw file: the same victory JSON shows fannkuchredux at 0.964 (n9) and 1.058 (n11), and the parallel run in results/2026-09-09-fan-repair.json reads 54 ms vs 172 ms at n10 (about 0.31x, derived from page data, median of 7), threaded Almide against one-thread Rust.
- The ratio is allocator- and CPU-dependent: binarytrees reads 0.32-0.35 on macOS, 0.581 on the ubuntu-latest runner (BENCHMARKS.md prose still says 0.61), and issue #3586 measured Almide native 94.55 ms vs Rust Box 216.97 ms on a Xeon 8581C, where the native leg was 1.47x slower than its own wasm leg until PR #3597 (2026-10-12); the M4 Pro columns were not re-measured on 0.66.

## Known shortcomings

- Beats only Rust that does malloc/free per Box node (the win is a region-window bump arena); no JS/V8 or Emscripten comparison (off-category baseline); the ratio depends on the allocator (CI runner 0.581/0.365); the README fannkuch row is threaded Almide vs one-thread Rust; wasm ratios 0.67x-1.96x appear in the README, not BENCHMARKS.md.
- Enricher: the win is a bump arena against Rust that pays malloc/free per node; issue #3586 has a hand-written Rust arena at 31.3 ms vs Almide 51 ms (binarytrees d19x12, M4 Pro); the victory JSON (results/2026-09-08-m4pro-victory-1330.json) is a hand-assembled summary with medians only, no per-run data and no rustc version; the README fannkuchredux 0.21/0.12 row has no matching raw file (the same JSON shows 0.964/1.058 and 2026-09-09-fan-repair.json about 0.31x, threaded vs one thread); the region arena keeps chunks for the thread's life and a wrong region-pure verdict is a silent use-after-rewind (prelude_region.rs). Retiered to C.

## Caveats and trade-offs

Off the category baseline: the comparison is native Rust output, not TypeScript/JS in V8 or C++ via Emscripten, and the wasm output is only compared with Almide's own native binary, never with JS/V8 or an Emscripten build. The whole win is one optimization (the region window, a thread-local bump arena rewound once per check(make(d)) tree) against a Rust reference that deliberately pays malloc/free per Box node; a Rust program using an arena (bumpalo/typed-arena, as Benchmarks Game Rust entries do) would close most of the gap (the same document shows a Zig arena at 88 ms vs Almide 72 ms at d16). Two workloads, one mechanism. The ratio is allocator-dependent (0.581 and 0.365 on the ubuntu-latest runner vs 0.35 and 0.30 on macOS). The M4 Pro columns were measured on 0.62.0 and not re-measured. The README's third victory row (fannkuchredux 0.21/0.12 via parallel fan) compares a threaded Almide run with a one-thread Rust reference and should not be cited. Self-reported by the project. [retier] Baseline Rust pays malloc/free per node; a hand-written Rust arena beats Almide (issue #3586); victory JSON hand-assembled without per-run data or rustc version; fannkuchredux README row unsupported by raw files; region arena never returns memory and a wrong region-pure verdict is a silent use-after-rewind

Young language optimised for LLM code generation; wins on allocation-heavy rows come from a compiler-proven region (bump-arena) window the ordinary Rust program does not have. Loses on fasta and FFT.

## Maintenance

Very active (11,586 commits on develop, last commit 2026-10-11, PR #3597 merged 2026-10-12) and dual MIT/Apache-2.0, but a pre-1.0 research language with 35 stars whose speed claims are first-party and self-gated by its own CI ratchet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** Public harness research/benchmark/perf/bench.py with the Rust references in research/benchmark/perf/rust-ref/ (binarytrees.rs, treealloc.rs) and raw per-run JSON (results/2026-09-08-m4pro-victory-1330.json, whose numbers match the page: 133.9 vs 381.8 ms at d17, 580.8 vs 1825.9 ms at d19); rustc flags opt-level=3, lto, codegen-units=1 and the Apple M4 Pro CPU are stated, so the native comparison against ordinary Rust is reproducible.
- **Retiered** A to C: Enricher (2026-10-12): first-party provenance gaps behind the A-grade table. results/2026-09-08-m4pro-victory-1330.json is a hand-assembled summary (medians and ratios only, no per-run arrays, no rustc version) rather than bench.py's output format, the README fannkuchredux 0.21/0.12 row has no matching raw file (the same JSON shows 0.964/1.058), and the binarytrees win is a bump arena against a Rust baseline that pays malloc/free per node (issue #3586: a hand-written Rust arena runs 31.3 ms vs Almide 51 ms at d19x12).
- **Verifier notes:** Numbers on docs/project/BENCHMARKS.md match the raw JSON in the repo and the harness and Rust references are public, so A stands for the native-vs-Rust claim. Shortcomings to record: off-category baseline (no JS/V8 or Emscripten comparison), win comes only from an arena vs a malloc-per-node Rust reference, allocator-dependent ratio, unequal threaded fannkuchredux row on the README.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-18 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/almide/almide/develop/docs/project/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/almide/almide/develop/README.md>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/results/2026-09-08-m4pro-victory-1330.json>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/rust-ref/binarytrees.rs>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/bench.py>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/README.md>
  - <https://raw.githubusercontent.com/almide/almide/develop/docs/benchmarks/native-victory.txt>
  - <https://github.com/almide/almide>
  - <https://github.com/almide/almide/commits/develop>
- **Sources the enricher read:**
  - <https://github.com/almide/almide>
  - <https://raw.githubusercontent.com/almide/almide/develop/README.md>
  - <https://raw.githubusercontent.com/almide/almide/develop/docs/project/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/bench.py>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/README.md>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/rust-ref/binarytrees.rs>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/rust-ref/treealloc.rs>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/rust-ref/fannkuchredux.rs>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/binarytrees/binarytrees.almd>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/treealloc/treealloc.almd>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/fannkuchredux/fannkuchredux.almd>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/results/2026-09-08-m4pro-victory-1330.json>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/results/2026-09-08-m4pro.json>
  - <https://raw.githubusercontent.com/almide/almide/develop/research/benchmark/perf/results/2026-09-09-fan-repair.json>
  - <https://github.com/almide/almide/tree/develop/research/benchmark/perf/results>
  - <https://raw.githubusercontent.com/almide/almide/develop/docs/benchmarks/native-victory.txt>
  - <https://raw.githubusercontent.com/almide/almide/develop/scripts/check-perf-ratio.sh>
  - <https://raw.githubusercontent.com/almide/almide/develop/spec/lang/region_window_test.almd>
  - <https://raw.githubusercontent.com/almide/almide/develop/crates/almide-codegen/src/lib.rs>
  - <https://raw.githubusercontent.com/almide/almide/develop/crates/almide-codegen/src/prelude_region.rs>
  - <https://raw.githubusercontent.com/almide/almide/develop/src/cli/build.rs>
  - <https://raw.githubusercontent.com/almide/almide/develop/Cargo.toml>
  - <https://github.com/almide/almide/issues/1991>
  - <https://github.com/almide/almide/pull/2032>
  - <https://github.com/almide/almide/issues/3586>
  - <https://github.com/almide/almide/issues?q=is%3Aissue+region+window>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/almide/almide`) · [data/wave13/enrich/raw/github_com_almide_almide.json](../../../data/wave13/enrich/raw/github_com_almide_almide.json) (enrichment confidence 0.8)

</details>
