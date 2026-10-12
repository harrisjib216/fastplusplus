# BoltFFI

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust multi-language bindings generator; returns arrays of structs to JS or Swift far faster than wasm-bindgen class handles or UniFFI.

| | |
|---|---|
| **Beats** | wasm-bindgen (Rust-to-JavaScript glue); on native targets UniFFI |
| **Claimed result** | README static snapshot (v0.24.0, Apple M3, Benchmark.js mean): 1k particles 29,886 vs 13,532,530 ns (453x); 100 particles 3,117 vs 748,287 ns (240x); 1k locations 21,931 vs 4,037,879 ns (184x); 1k trades 42,015 vs 5,781,767 ns (138x); 100 locations 2,199 vs 283,753 ns (129x); same snapshot shows ties at 2 ns on scalar calls, ties on primitive vectors, 1.6-3.6x on strings. Dashboard (stated source of truth, boltffi/benchmarks-dashboard public/data/archive, five wasm runs 2026-04-16 to 2026-06-25) shows much smaller wins: generate_\*_1k/10k means 18-115x, medians 5.9-35x (e.g. generate_particles_1k on Apple M3 Max 2026-06-05: median 29,245 vs 276,455 ns, 9.5x, derived from page data; mean 76x); host-to-Rust record passing 1.1-1.9x; echo_string_1k 1.2-2.7x; and BoltFFI slower on scalar calls in every run (noop 112-247 ns vs 2-8 ns, about 20-50x slower), on primitive vectors (0.27-1.0x), classes (counter_increment_single_threaded 0.51-0.59x in May-June runs), find_even_100 (0.09x) and sum_user_scores (0.71x). README headline also claims up to 1,000x vs UniFFI on Swift (noop &lt;1 ns vs 1,416 ns). |
| **Workload** | Benchmark.js microbenchmarks in benchmarks/harnesses/wasm-bench/bench.mjs over the same examples/demo Rust crate exported by BoltFFI and by wasm-bindgen (Node.js): scalar calls, strings, primitive vectors, generating 100/1k/10k records (locations, trades, particles; wasm-bindgen returns arrays of opaque #[wasm_bindgen] class handles that the loop never frees, BoltFFI returns plain JS objects decoded from a wire buffer), passing records from JS to Rust, classes, enums, callbacks and async. |
| **Metric** | latency |
| **Hardware** | README snapshot: Apple M3 (WASM and Swift), Apple M4 Max (JVM); dashboard runs: Apple M3 Max (14 cores, macOS 15.7.3, local) and Apple M1 (Virtual) GitHub Actions macOS runners (3 cores) |
| **Compiler and flags** | benchmarks/harnesses/wasm-bench/run-bench.sh: BoltFFI side 'boltffi pack wasm --release' with the benchmark overlay; wasm-bindgen side 'cargo build --release --target wasm32-unknown-unknown --features wasm-bench' then 'wasm-bindgen --target nodejs' (CLI version from cargo metadata); Benchmark.js 2.1.4 means. README snapshot states no versions; dashboard runs record rustc 1.95.0 (2026-04-14) or 1.94.0-nightly, Node v20.2.0 to v24.17.0, wasm-bindgen 0.2.108 (2026-04-16 run), no wasm-opt. |
| **Adoption** | 895 stars, 54 forks, 2,244 commits; no GitHub releases listed on the repo page |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/boltffi/boltffi) · [benchmark](https://github.com/boltffi/boltffi) |

## Verdict

BoltFFI's own Benchmark.js suite wraps the same examples/demo crate with BoltFFI and with wasm-bindgen 0.2.108 (Node.js). The README v0.24.0 snapshot (Apple M3) shows 129-453x on generate_\* means, but the dashboard CI runs (rustc 1.94-1.95, Node 20-24, Apple M3 Max and Apple M1 Virtual) show generate_\* medians of 5.9-35x across five runs (7.5-35x in the 2026-06-25 run), 1.1-1.9x on passing records into Rust, and 20-35x losses on scalar calls. The Swift dashboard run shows 600x-plus wins only on record generation against UniFFI, and ties on noop.

## Use it when

- Rust functions that return many small records to JavaScript: in the 2026-06-25 dashboard run, generate_locations_1k took 19.8 us vs 695 us median (35x) against wasm-bindgen's class-handle return, and generate_particles_1k 59 us vs 617 us (10x).
- Swift or Kotlin apps where UniFFI's record serialization dominates: in the same day's Swift run, generate_locations_1k took 3.0 us vs 1.89 ms and process_locations_1k 1.7 us vs 48.7 us.
- One Rust core shipped to Swift, Kotlin, Java, C#, Python and TypeScript from a single set of annotations, with packaging handled by one CLI.
- Callback-heavy APIs (Rust calling host-implemented traits): 1.5-1.7x faster than wasm-bindgen and about 2.1x faster than UniFFI in the dashboard runs.

## Skip it when

- Hot loops of scalar calls from JavaScript: in the 2026-06-25 dashboard run BoltFFI's noop took 236 ns vs 7 ns median for wasm-bindgen, echo_i32 160 ns vs 6 ns, enum calls 285-580 ns vs 7-10 ns, and find_even_100 ran at 0.09x.
- Primitive vectors, byte buffers and stateful classes on WASM: ties or losses (sum_i32_vec 0.77-0.88x, echo_vec_i32_10k 0.72x, counter_increment 0.59-0.71x, accumulator 0.70-0.82x).
- Passing records into Rust when wasm-bindgen already uses serde-wasm-bindgen: the harness's own serde-wasm-bindgen rows (user profiles) show BoltFFI 1.9x faster on generate but 0.71-0.74x (slower) on sum_user_scores and count_active_users.
- C++ consumers: C++ is only 'Planned', the C target is experimental and synchronous only, and Kotlin Multiplatform supports only synchronous infallible free functions over primitives; cxx or Diplomat fit C++ better.
- Projects needing a stable API: pre-1.0 (29 crates.io releases since 2026-02-17), with open lifecycle bugs such as #664 (use-after-close race in C#, Java and Kotlin wrappers) and #670 (C# class wrappers passed by value are not invalidated).

## How it is fast

Primitives cross as raw values. On native targets, `#[data]` structs with only primitive fields are passed as pointers to memory both sides can read, which avoids UniFFI's serialize-every-value RustBuffer step. On WASM, records and collections are written into one wire buffer in linear memory, and the TypeScript runtime decodes it eagerly into plain JS objects with a DataView reader (`WireReader.readArray`). wasm-bindgen instead boxes each exported struct separately in Rust and hands JS one wrapper object per element, each registered with a FinalizationRegistry. Strings and collections are still encoded and copied.

## Compared with alternatives

None of the catalogued siblings is a bindings generator: json-as, as-proto, MoonBit and Kotlin/Wasm are WASM languages or kernels that make the code inside WASM faster. BoltFFI only reduces the cost of crossing the Rust-to-host boundary, so pick it when that boundary moves struct-shaped data, not when the work inside WASM is the bottleneck.

## Integration

| | |
|---|---|
| **Form** | crate plus CLI code generator (boltffi crate, boltffi_cli via cargo install or prebuilt archives; WASM output also needs the @boltffi/runtime npm package) |
| **Dependencies** | boltffi crates; per-target toolchains (Xcode for Apple, Android NDK, JDK, .NET SDK, Python, Node); wasm-opt from binaryen for release WASM packs unless optimisation is turned off or on_missing is relaxed |
| **Minimum toolchain** | Rust edition 2024 (so Rust 1.85 or later); no rust-version declared on crates.io |
| **Platforms** | iOS and macOS (Swift), Android and JVM (Kotlin, Java via JNI), .NET (C#), CPython, wasm32-unknown-unknown (Node.js and browsers); C experimental; Dart in progress |
| **Thread safety** | Exported objects inherit the Rust type's own synchronization (the harness compares Mutex-backed and single-threaded counters); open issue #664 says concurrent use-after-close is still possible in the C#, Java and Kotlin wrappers |
| **Drop-in for the baseline** | no |

## Gotchas

- Asymmetric WASM toolchain in the benchmark: the benchmark overlay (examples/demo/boltffi.benchmark.toml) sets [targets.wasm.optimize] enabled = true, and the release CI installs binaryen, so BoltFFI's .wasm is post-processed with `wasm-opt -Os` (the default level). run-bench.sh runs no wasm-opt on the wasm-bindgen output, and the dashboard metadata records optimizer null for both sides.
- A release `boltffi pack wasm` runs wasm-opt by default and aborts with 'wasm-opt not found in PATH' when binaryen is missing (on_missing defaults to Error); set level or on_missing under [targets.wasm.optimize] to change this.
- The README tables are a static v0.24.0 snapshot, and the dashboard (newest runs 2026-06-25, before releases 0.29-0.31) contradicts several of them. WASM scalar calls went from a 2 ns tie to 20-35x losses. In Swift, noop and echo_i32 tie UniFFI at about 29 ns mean (41 ns median, one Apple timer tick) instead of '&lt;1 ns vs 1,416 ns', and counter_increment is 9.3 us vs 22.6 us (2.4x), not 1,282x. The '1,000x faster than UniFFI' headline is not reproduced.
- Returned records are eager JS copies; classes need an explicit dispose() (the harness calls it). wasm-bindgen's generate rows in the harness never free their class handles, so their means include GC and FinalizationRegistry pauses (generate_locations_10k max 167.6 ms vs median 6.0 ms).

## Known shortcomings

- The README 453x is a stale static snapshot; the boltffi/benchmarks-dashboard runs give record generation 18-115x by mean but only 5.9-35x by median, the means inflated by GC outliers from wasm-bindgen handles never freed; BoltFFI is 20-50x slower on scalar calls (noop 112-247 ns vs 2-8 ns) and slower on vectors and classes.
- Enricher: asymmetric toolchain: the benchmark overlay enables wasm optimisation and CI installs binaryen, so the BoltFFI .wasm gets wasm-opt -Os while the wasm-bindgen side gets none (dashboard records optimizer null); the Swift dashboard (2026-06-25) has noop and echo_i32 tying UniFFI at about 29 ns and counter_increment at 2.4x, so the README '1,000x' is not reproduced; the serde-wasm-bindgen user-profile rows give BoltFFI 1.9x on generate but 0.71-0.74x on consume; the wasm-bindgen sum_\* rows build 1,000 handles inside the timed region; dashboard data stale since 2026-06-25.

## Caveats and trade-offs

First-party microbenchmarks of trivial constructors and sums that isolate FFI overhead, so the ratios are boundary cost, not application speed. The 453x headline is a mean from a static README snapshot; the dashboard named as source of truth never reproduces it: wasm-bindgen generate_\* samples are few (7-29) with maxima up to 327 ms against medians of 0.23-6.0 ms, consistent with GC/FinalizationRegistry pauses from never-freed class handles, so mean ratios overstate the median gap (5.9-35x). BoltFFI is about 20-50x slower than wasm-bindgen on scalar calls in every dashboard run (noop 112-247 ns vs 2-8 ns), contradicting the README snapshot's 2 ns tie, and slower on primitive vectors, stateful classes and find_even. JVM snapshot shows uniffi-bindgen-java (FFM) faster than BoltFFI on inc_u64, echo_string_small and find_even. Baseline is wasm-bindgen's default class-handle representation, not serde-wasm-bindgen or tsify.

Own code generator and annotations (#[data], #[export]); WASM uses a wire buffer format that avoids per-field allocation; also targets Swift, Kotlin, Java, C#, Python and C. wasm-bindgen is more general (documented by BoltFFI itself as materialising every struct as a JS object).

## Maintenance

Active (0.31.0 on crates.io 2026-09-28, last commit 2026-10-09, MIT, copyable), but pre-1.0 with 44 bug-labelled issues and no dashboard run since 2026-06-25. Harness findings: BoltFFI's WASM build gets `wasm-opt -Os` while the wasm-bindgen build gets none; the headline means are inflated by GC outliers from never-freed wasm-bindgen class handles; the wasm-bindgen host-to-Rust rows construct 1,000 class handles through constructor FFI calls inside the timed region; and the Swift dashboard ties UniFFI on noop, contradicting the README's '1,000x' headline.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party Benchmark.js harness (benchmarks/harnesses/wasm-bench/bench.mjs, run-bench.sh) against wasm-bindgen; the README snapshot names only an Apple M3 with no Rust, Node or wasm-bindgen versions. The dashboard run JSONs do record rustc 1.95.0 --release, Node v20.2.0-v24.17.0 and CPU (Apple M3 Max, Apple M1 Virtual), but tier stays C because the headline ratios are means over 7-29 wasm-bindgen samples dominated by multi-millisecond GC outliers and are not reproduced by any dashboard run.
- **Verifier notes:** README numbers are quoted correctly but are a stale static snapshot; the dashboard runs (public JSON with full toolchain and CPU metadata) show 6-35x median wins only on Rust-to-JS record generation and 20-50x losses on scalar calls. Claim overstated; record the GC-outlier mean skew, scalar-call regression and never-freed wasm-bindgen handles as shortcomings.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-65 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/boltffi/boltffi>
  - <https://github.com/boltffi/boltffi/commits>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/README.md>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/harnesses/wasm-bench/bench.mjs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/harnesses/wasm-bench/run-bench.sh>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/harnesses/wasm-bench/package.json>
  - <https://github.com/boltffi/boltffi/tree/main/examples/demo/bench_macros/src>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/examples/demo/bench_macros/src/lib.rs>
  - <https://github.com/boltffi/benchmarks-dashboard>
  - <https://github.com/boltffi/benchmarks-dashboard/tree/main/public/data>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/index.json>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/archive/2026/06/25/2026-06-25t20-20-28z-wasm-node-benchmarkjs-2dc0e963810c--ef8d99f69769.json>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/archive/2026/06/22/2026-06-22t20-46-41z-wasm-node-benchmarkjs-d708c113cdd9--1269493002dc.json>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/archive/2026/06/05/2026-06-05t15-28-37z-wasm-node-benchmarkjs-0c5c2f3187f9--74ddd1660f6e.json>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/archive/2026/05/31/2026-05-31t19-44-35z-wasm-node-benchmarkjs-7f4ec798c558--84c6783f863b.json>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/archive/2026/04/16/2026-04-16t12-18-02z-wasm-node-benchmarkjs-f9c5f59f960d--1e2bba64578f.json>
- **Sources the enricher read:**
  - <https://github.com/boltffi/boltffi>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/README.md>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/harnesses/wasm-bench/bench.mjs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/harnesses/wasm-bench/run-bench.sh>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/benchmarks/harnesses/wasm-bench/package.json>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/examples/demo/bench_macros/src/lib.rs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/examples/demo/Cargo.toml>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/examples/demo/boltffi.benchmark.toml>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/examples/demo/boltffi.toml>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/examples/demo/src/wasm_bench.rs>
  - <https://github.com/boltffi/boltffi/tree/main/examples/demo/src>
  - <https://github.com/boltffi/boltffi/tree/main/boltffi_cli/src>
  - <https://github.com/boltffi/boltffi/tree/main/boltffi_cli/src/pack>
  - <https://github.com/boltffi/boltffi/tree/main/boltffi_cli/src/pack/wasm>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/boltffi_cli/src/pack/wasm/mod.rs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/boltffi_cli/src/pack/wasm/module.rs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/boltffi_cli/src/pack/wasm/package.rs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/boltffi_cli/src/pack/wasm/bindgen.rs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/boltffi_cli/src/config/mod.rs>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/.github/workflows/benchmark-release.yml>
  - <https://github.com/boltffi/boltffi/tree/main/runtime/typescript/src>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/runtime/typescript/package.json>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/runtime/typescript/src/wire.ts>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/runtime/typescript/src/handle.ts>
  - <https://raw.githubusercontent.com/boltffi/boltffi/HEAD/runtime/typescript/src/module.ts>
  - <https://github.com/boltffi/boltffi/issues?q=is%3Aissue+wasm+performance>
  - <https://github.com/boltffi/boltffi/issues?q=is%3Aissue+label%3Abug>
  - <https://crates.io/api/v1/crates/boltffi>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/index.json>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/archive/2026/06/25/2026-06-25t20-20-28z-wasm-node-benchmarkjs-2dc0e963810c--ef8d99f69769.json>
  - <https://raw.githubusercontent.com/boltffi/benchmarks-dashboard/HEAD/public/data/archive/2026/06/25/2026-06-25t18-30-44z-swift-macos-benchmark-2dc0e963810c--08b9bc9ba416.json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/boltffi/boltffi`) · [data/wave13/enrich/raw/github_com_boltffi_boltffi.json](../../../data/wave13/enrich/raw/github_com_boltffi_boltffi.json) (enrichment confidence 0.72)

</details>
