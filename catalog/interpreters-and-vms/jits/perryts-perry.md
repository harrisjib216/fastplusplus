# Perry

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Ahead-of-time TypeScript-to-native compiler (SWC + LLVM); beats Node/V8 on some numeric and JSON micro-benchmarks, loses others.

| | |
|---|---|
| **Beats** | Node.js v25.8.0 (V8); Bun 1.3.12 and Java OpenJDK 21.0.7 (HotSpot) appear in the same table |
| **Claimed result** | README (pinned to Perry v0.5.908, Apple M1 Max polyglot RESULTS.md): convolution 354 vs Node 1,207 ms, fib 309 vs 987 ms. The project's authoritative later artifact (benchmarks/results/public-node-bun-v1.json, Perry 0.5.1639, Apple M1, 2026-09-23, correctness-checked) reverses it: convolution 2,266 vs Node 1,220 ms (1.86x slower), accumulate 94 vs 95 ms, regex_replace 754 vs 98 ms, JSON 500k 2,123 vs 864 ms; the HEAD x86_64 table (2026-09-01) also has Perry slower on convolution (1,204.4 vs 975.0 ms). |
| **Workload** | Polyglot sweep of nine identical f64 benchmarks (fibonacci, loop_overhead, loop_data_dependent, array_write, array_read, math_intensive, object_create, nested_loops, accumulate), median of 11 runs; Perry compiles the same TypeScript source that Node and Bun run. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max (10 cores, 64 GB RAM), macOS 26.4 for polyglot RESULTS.md and for honest_bench at pinned revision 7beb3a50ca; honest_bench REPORT.md at HEAD and polyglot RESULTS_AUTO.md (both 2026-09-01, v0.5.1519) ran on an x86_64 16-core Ubuntu 24.04 / Linux 6.17 host whose CPU model is not stated |
| **Compiler and flags** | Perry v0.5.908 (LLVM backend), default mode without fast-math; METHODOLOGY.md lists rustc -O, clang++ -O3, javac and java (HotSpot JIT), Node v25.8.0 run on precompiled JS, Bun 1.3.12; no non-default optimization flags |
| **Adoption** | 4.9k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/PerryTS/perry) · [benchmark](https://github.com/PerryTS/perry/blob/HEAD/benchmarks/polyglot/RESULTS.md) |

## Verdict

Project-run, same-source comparisons against Node (V8): on Apple M1 Max with Perry v0.5.908 and Node v25.8.0, recursive fib(40) took 309 vs 987 ms and the modulo loop 97 vs 597 ms, with three ties and a loss. The newer 2026-09-23 correctness-checked artifact (Perry 0.5.1639, Node v22.23.1, Bun 1.3.14, Apple M1) keeps the fib win (338 vs 912 ms) and the JSON round-trip win (144 vs 379-392 ms). In that artifact the modulo-loop gap closes to a tie (94 vs 95 ms), and Perry is slower than Node on image convolution (2,266 vs 1,220 ms), 500k-record JSON, method calls, binary trees, regex and promises.

## Use it when

- CLI tools and services written in TypeScript where startup time, a single small binary (from about 330 KB) and low RSS matter more than peak JIT throughput.
- Integer- or f64-heavy recursive or loop code with stable types, e.g. recursive fib: 338 ms vs Node v22.23.1 912 ms in the project's 2026-09-23 correctness-checked artifact on Apple M1.
- JSON parse/stringify round-trips and small JSON pipelines: json_roundtrip 144 ms vs Node 379-392 ms, 100-record pipeline 55.7 vs 100.0 ms in the same artifact.
- Shipping TypeScript to targets Node cannot run on (iOS, Android, watchOS, tvOS) with native widgets.

## Skip it when

- Compute kernels over Buffer/Uint8Array: the project's own 2026-09-23 artifact (Perry 0.5.1639, Apple M1) has the 4K 5x5 image convolution at 2,266 ms vs Node 1,220 ms and Bun 888 ms, i.e. Perry 1.86x slower than Node (derived from page data), the opposite of the README headline.
- Class-method-heavy or allocation-heavy object code: method_calls 35 vs 11 ms, binary_trees 13 vs 6 ms, object_create 8 vs 5 ms against Node in the same artifact; large JSON (500k records) 2,123 vs 864 ms.
- Regex- or promise-heavy code: regex_replace 754 ms vs Node 98 ms and promise_all_chains 86 vs 59 ms in the artifact's app_patterns component.
- Code that relies on runtime eval, runtime-computed dynamic import(), runtime-installed npm plugins or runtime type validation: these compile to deferred throws or are unsupported.
- Teams that cannot absorb compiler bugs: the issue tracker shows recent silent miscompilations (#9278: stores to a module-global Buffer dropped, closed 2026-09-01; #9717 private-field array losing contents).

## How it is fast

SWC parses the TypeScript and Perry lowers it to LLVM IR (LLVM 22, in-process), so hot loops get ahead-of-time LLVM optimisation with no warm-up. Type inference narrows `number` to i64/i32 where a function only does integer work (fib uses integer add/compare, `i % 1000` becomes `srem` instead of an fmod call), proves `for (i < arr.length)` loops in-bounds and vectorises them, and a scalar-replacement pass removes short-lived object allocations. A generational GC and NaN-boxed values handle the dynamic remainder; fast-math (reassoc/contract) is opt-in via `--fast-math` since v0.5.585.

## Compared with alternatives

Pick Perry over katsu or Graal.js when you want an existing TypeScript/Node codebase compiled AOT to one native binary, possibly for mobile or watch targets, and your hot paths are typed numeric loops or JSON. Stay on V8 (or pick Graal.js for peak JIT throughput) when the workload is method dispatch, regex, promises or byte-buffer kernels, where Perry's own data shows it losing.

## Integration

| | |
|---|---|
| **Form** | Rust-built compiler CLI producing standalone executables (installed via npm @perryts/perry, Homebrew, winget, APT or Scoop) |
| **Dependencies** | Prebuilt binary: none at runtime. Building from source: pinned Rust nightly-2026-10-04, LLVM 22 development files, libclang (bindgen for libsqlite3-sys), system C compiler. |
| **Minimum toolchain** | Rust nightly-2026-10-04 and LLVM 22 to build Perry itself; input is TypeScript (a supported subset) |
| **Platforms** | macOS, Linux, Windows, iOS, Android, watchOS, tvOS, visionOS natively; JavaScript or WebAssembly output for the web |
| **Thread safety** | Real OS threads via parallelMap/spawn from perry/thread; closures are deep-copied across threads and the compiler rejects shared mutable state, except explicit shared memory used with Atomics. |
| **Drop-in for the baseline** | partial: replaces `node app.js` with a compiled binary and re-implements most node:\* modules, but no runtime-built eval/new Function, no runtime-computed dynamic import of uncompiled code, and type annotations are not enforced at runtime |

## Gotchas

- Harness finding: the README's lead row (image convolution 354 ms vs Node 1,207 ms, 3.4x) is pinned to v0.5.908 (2026-05-14). The workload source is byte-identical at HEAD, yet the project's own correctness-gated artifact benchmarks/results/public-node-bun-v1.json (Perry 0.5.1639, Node v22.23.1, Apple M1, 2026-09-23) measures Perry at 2,266 ms vs Node 1,220 ms, and HEAD REPORT.md (v0.5.1519, x86_64) has 1,204 vs 975 ms. That is a roughly 6x Perry regression on unchanged code, and the README still advertises the old figure, although benchmarks/README.md itself says the v0.5.908 tables are historical and the versioned artifact is authoritative where they differ. The cause is not documented; the x86 sweep is dated 2026-09-01, the day #9278 closed, and #9278 (a silent miscompilation that dropped stores to a module-global Buffer and gave this exact convolution workload a wrong checksum on 0.5.1220) hit the same code pattern.
- The 6.2x 'accumulate' win (Perry 97 vs Node 597 ms on Node v25.8.0) does not hold on Node v22.23.1: the 2026-09-23 artifact has Perry 94 vs Node 95 ms. The gap depends on whether that V8 version inlines fmod for `i % 1000`, so it is not a Perry property. The Perry/Node 'accumulate' row is produced by suite/13_factorial.ts, whose header says it computes no factorial.
- The polyglot table compares workloads that are not identical across languages. bench.cpp's nested_loops sums a 9M-element flat array while the TS version sums arr[i]+arr[j] over a 3,000-element array; fib is int in bench.cpp and i64 in bench.rs; math_intensive and object_create use different start values. RESULTS.md says all use f64 and identical algorithms. Only the Perry/Node/Bun columns run the same source, and only the public-JSON mode checks that their outputs agree (RESULTS_AUTO.md does not). Timing is in-process Date.now() at 1 ms resolution, so the 1-9 ms cells (array_write, object_create, array_read) sit at clock resolution.
- RESULTS.md's loop_overhead prose describes an old `sum += 1.0` kernel that HEAD replaced with an Math.imul FNV recurrence because the old one folded to near zero. Its 12 ms --fast-math and 97 ms default figures therefore come from a different benchmark than the one in the suite now, and the current kernel ties Node (125 vs 126 ms on M1).

## Known shortcomings

- Mixed against Node (loses loop_overhead, method_calls and binary_trees on the M1 Max polyglot RESULTS.md; the HEAD x86_64 table of 2026-09-01 has Perry slower on convolution, 1,204.4 vs 975.0 ms, CPU unnamed); honest_bench/scripts/report.py hard-codes stale v0.5.81 prose ('268 ms, 4.5x faster than Node') and the README's 500k JSON row (1,649 ms) comes from that prose rather than the pinned run (1,098.4 ms). Ahead-of-time TypeScript compiler, not a JIT.
- Enricher: the README's top claim (convolution 354 vs Node 1,207 ms) is pinned to v0.5.908, while the project's own newest correctness-checked artifact (benchmarks/results/public-node-bun-v1.json, Perry 0.5.1639, Apple M1, 2026-09-23, which benchmarks/README.md calls authoritative) has Perry at 2,266 vs Node 1,220 ms (1.86x slower), the accumulate 6.2x win gone (94 vs 95 ms on Node v22.23.1), regex_replace 754 vs 98 ms and JSON 500k 2,123 vs 864 ms; issue #9278 was a silent miscompilation giving this same convolution workload a wrong checksum on 0.5.1220. The polyglot C++, Rust and TypeScript kernels are not identical (nested_loops, fib int vs i64) and the RESULTS.md loop_overhead numbers come from a kernel later replaced.

## Caveats and trade-offs

AOT compiler measured against V8's JIT, included because the claim is against Node/V8. Results are mixed and the repo says so: HotSpot Java beats Perry on fibonacci, Node wins loop_overhead, and the README's public Node/Bun suite shows Perry losing method_calls (3x), binary_trees and prime_sieve. Several polyglot wins are 2-9 ms cells where noise matters, and accumulate's 6x comes from V8 not inlining fmod. METHODOLOGY.md lists Perry v0.5.585 while RESULTS.md reports v0.5.908, and RESULTS.md's prose cites stale numbers (array_read 3 ms, Node 322 ms on loop_data_dependent) that disagree with its own table (11 ms, 226 ms). honest_bench REPORT.md is internally inconsistent at HEAD: scripts/report.py hard-codes v0.5.81-era bottom-line prose (Perry 268 ms on convolution, 4.5x faster than Node; JSON 500k 1,649 ms) above freshly generated tables in which Perry is slower than Node on convolution (1,204.4 vs 975.0 ms, sigma 282) and on JSON 500k (1,831.2 vs 1,183.5 ms). The README pins its convolution and JSON-100 figures to revision 7beb3a50ca (M1 Max, v0.5.908: 354.0 vs 1,206.6 ms), but its 500k-record JSON row (1,649 / 1,010 / 647 / 604 ms) matches the stale hard-coded prose, not that revision's table (1,098.4 / 966.3 / 649.9 / 608.3 ms); its note that HEAD reads 0.0 ms is also out of date (regenerated with real numbers in #9405, 2026-09-01). The newest x86_64 sweeps do not name the CPU model. Written by the project itself with a 'we publish everything' framing; the README highlight table selects favourable rows. [retier] Ahead-of-time TypeScript compiler, not a JIT. Headline numbers are from v0.5.908; issue #9278 (silent miscompilation, wrong checksum on this convolution workload at 0.5.1220) and the later correctness-checked artifact that shows Perry behind Node mean the claim does not hold on current code. honest_bench/scripts/report.py hard-codes stale v0.5.81 prose ('268 ms, 4.5x faster than Node'); the README 500k JSON row (1,649 ms) comes from that prose rather than the pinned run (1,098.4 ms); the polyglot C++, Rust and TypeScript kernels are not identical (nested_loops, fib int vs i64); the RESULTS.md loop_overhead kernel was later replaced.

Ahead-of-time compiler, not a JIT: compiles a typed TypeScript subset to native executables through SWC and LLVM, with Node-compatible shims (about 97% of Node's own test suite passes on 53 node:\* modules per the README). No dynamic eval. Binaries are 330 KB and up, with lower RSS than Node.

## Maintenance

Very active (last commit 2026-10-06, version 0.5.1657 in Cargo.toml, 4.9k stars), MIT. The project publishes raw samples and correctness-checked results, but its README headline numbers are older than, and in two rows contradicted by, its own newest artifact, and recent issues include silent miscompilations, so verify output and speed on your own workload before adopting.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now C.
- **Tier reason:** benchmarks/polyglot/RESULTS.md runs the same TypeScript sources (benchmarks/suite/\*.ts, with bench.cpp/.rs/.java peers and run_all.sh public) under Perry v0.5.908 default mode and Node v25.8.0 / Bun 1.3.12, with compiler versions and release-mode-only flags in METHODOLOGY.md and the CPU named (Apple M1 Max), median of 11 runs; first-party but fully reproducible, so A stands.
- **Retiered** A to C: A to C: the headline numbers are pinned to v0.5.908, a silent miscompilation (#9278) later gave the same convolution workload a wrong checksum, and the project's own newest correctness-checked artifact (0.5.1639, 2026-09-23) has Perry 1.86x slower than Node on that workload; numbers measured on code later fixed for correctness bugs and reversed by the project's own later data go to C.
- **Verifier notes:** Polyglot RESULTS.md numbers match the record and the page meets tier A. The search agent's inconsistency flag is correct and has a cause: honest_bench/scripts/report.py hard-codes stale v0.5.81 bottom-line prose (268 ms, 4.5x vs Node) above regenerated tables in which Perry is now slower than Node on convolution (1,204.4 vs 975.0 ms on x86_64, v0.5.1519); the README's 500k JSON row also comes from that stale prose rather than its pinned 7beb3a50ca revision. Record shortcomings: mixed results versus Node, stale or contradictory prose in the project's reports, unnamed CPU on the newest x86_64 runs.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PerryTS/perry>
  - <https://github.com/PerryTS/perry/commits/main>
  - <https://github.com/PerryTS/perry/tree/main/benchmarks/polyglot>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/README.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/RESULTS.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/METHODOLOGY.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/RESULTS_AUTO.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/02_loop_overhead.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/honest_bench/REPORT.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/7beb3a50ca/benchmarks/honest_bench/REPORT.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/honest_bench/scripts/report.py>
  - <https://github.com/PerryTS/perry/blob/main/benchmarks/honest_bench/REPORT.md>
  - <https://github.com/PerryTS/perry/commits/main/benchmarks/honest_bench/REPORT.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/README.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/RESULTS.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/METHODOLOGY.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/RESULTS_AUTO.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/run_all.sh>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/bench.cpp>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/polyglot/bench.rs>
  - <https://github.com/PerryTS/perry/tree/main/benchmarks/suite>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/02_loop_overhead.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/03_array_write.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/04_array_read.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/05_fibonacci.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/06_math_intensive.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/07_object_create.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/09_method_calls.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/10_nested_loops.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/12_binary_trees.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/13_factorial.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/suite/17_loop_data_dependent.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/results/public-node-bun-v1.json>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/honest_bench/REPORT.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/7beb3a50ca/benchmarks/honest_bench/REPORT.md>
  - <https://github.com/PerryTS/perry/tree/main/benchmarks/honest_bench/workloads/3_image_convolution>
  - <https://github.com/PerryTS/perry/tree/main/benchmarks/honest_bench/workloads/3_image_convolution/perry>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/benchmarks/honest_bench/workloads/3_image_convolution/perry/image_conv.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/7beb3a50ca/benchmarks/honest_bench/workloads/3_image_convolution/perry/image_conv.ts>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/docs/src/language/limitations.md>
  - <https://raw.githubusercontent.com/PerryTS/perry/HEAD/docs/src/contributing/building.md>
  - <https://github.com/PerryTS/perry/issues?q=convolution>
  - <https://github.com/PerryTS/perry/issues?q=is%3Aissue+miscompilation>
  - <https://github.com/PerryTS/perry/issues/139>
  - <https://github.com/PerryTS/perry/issues/9278>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/perryts/perry`) · [data/wave12/enrich/raw/github_com_perryts_perry.json](../../../data/wave12/enrich/raw/github_com_perryts_perry.json) (enrichment confidence 0.75)

</details>
