# zig-js

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Zig` · `MIT` · 🟢 active

> JavaScript engine in Zig with a JavaScriptCore-shaped C API; ten small kernels run 2.3x faster than system JSC, which probably had its JIT off.

| | |
|---|---|
| **Beats** | JavaScriptCore (system framework on macOS, public C embedding API) |
| **Claimed result** | README geomean 2.32x over JavaScriptCore on 10 micro rows (recomputed), but the JSC runner is signed without the com.apple.security.cs.allow-jit entitlement (build.zig), so under macOS arm64 JIT restrictions JSC ran interpreter-only (15.5 ns per arithmetic iteration, 26.7 ns per fib call match LLInt); 9 of 10 rows hit legacy_narrow exact-bytecode kernels (docs/advanced/vm-quickening.md) written for those loop shapes. zig-js's own diagnostics: JSC 4.05x faster on JSON, up to 10.47x on deep stringify, about 10x on Wasm SIMD. docs/benchmarks.md cites a different July 29 report (2.29x/2.51x/2.61x). |
| **Workload** | Ten small project-owned JavaScript kernels from bench/comparison.js (arithmetic, properties, polymorphic_properties, object_churn, arrays, direct_calls, method_calls, closure_calls, arguments_calls, fibonacci), identical bytes run in both engines with equal-work checksums, seven samples, 50 ms timing floor, alternating runner order. |
| **Metric** | throughput |
| **Hardware** | Apple M3 Pro, 11 cores, 18 GiB, macOS 27.0, AC power, no CPU pinning |
| **Compiler and flags** | Zig 0.17.0-dev.1441+d5181a9c9, zig-js built ReleaseFast, precise GC enabled; JSC is the macOS system framework 22625.1.24.11.2 with unstated JIT configuration |
| **Adoption** | 31 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/zig-utils/zig-js) · [benchmark](https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/.data/benchmark-comparison-2026-07-29-precise-nursery.md) |

## Verdict

Setup: Apple M3 Pro, macOS 27.0, Zig 0.17.0-dev.1441 ReleaseFast with precise GC; the JSC side was the system JavaScriptCore 22625.1.24.11.2 called through its public C API. In one warmed context zig-js ran ten small project-written kernels 1.21x (object_churn) to 5.34x (fibonacci) faster, geomean 2.32x, and 2.53x and 2.52x at 8 independent warmed and cold contexts. The JSC runner carries no allow-jit entitlement, so JSC most likely ran interpreter-only, and most rows hit zig-js's exact-pattern VM kernels.

## Use it when

- A Zig program that needs an embedded JavaScript engine and can build with Zig 0.17-dev, so it does not have to link V8 or JSC.
- A macOS arm64 host written against the JavaScriptCore C API, where you want to try another engine behind the same calls for the subset zig-js implements.
- Scripts that need real parallelism inside one JavaScript heap: shared-realm `Thread`s with no GIL, which JSC's public API does not offer (the report shows 4.84x scaling at 8 lanes).
- Tight numeric loops and small call-heavy kernels on Apple Silicon, where the baseline JIT and the quickening kernels apply.
- Embedders who want test262 conformance (53,175 of 53,175 configured tests) from an MIT engine with no C++ dependency.

## Skip it when

- Peak throughput against JSC with its JIT on, V8 or SpiderMonkey: no such comparison exists, and the published JSC baseline very likely ran interpreter-only.
- JSON-heavy, Wasm SIMD or Promise-heavy work: on the project's own diagnostics system JSC is 4.05x faster on JSON parse and stringify (up to 10.47x on deep stringify) and about 10x faster on Wasm SIMD.
- Linux x86-64, Windows, iOS, tvOS or visionOS: there is no native tier on x86-64 (correctness CI only, no performance claim), and Windows and restricted Darwin targets are unsupported.
- Production systems that need a stable ABI or API: everything is pre-stabilization, macOS arm64 has no release-gated correctness CI, and one author commits daily.
- Code that does not match the documented fast subsets: most code stays on the tree-walker or general bytecode dispatch, and loops shaped differently from the benchmark kernels miss the exact-pattern kernels.

## How it is fast

Execution is tiered: a tree-walking interpreter, then a bytecode VM with inline caches, then an AArch64 baseline JIT (MAP_JIT memory with W^X switching), then a speculative optimizing tier over a documented numeric subset with deoptimization back to the interpreter. The VM also contains guarded quickening kernels. Nine of them are labelled `legacy_narrow` in the project's own inventory, meaning each matches one exact bytecode loop shape, and most of the benchmark rows run through them. A July 16 profile shows the arithmetic row spending 93.3% of samples in JIT-generated code and fibonacci spending 96.6% in `runQuickObservableRecurrence`. Arrays still spend 65% of samples in the general `runChunk` dispatch loop.

## Compared with alternatives

Pick it over QuickJS when the host is Zig or already uses the JavaScriptCore C API on macOS arm64 and needs shared-heap parallel threads. QuickJS stays the choice for small, portable C embedding on any OS. For raw speed V8 (or Hermes on mobile) remains the safer pick, because zig-js has not been compared against any JIT-enabled engine.

## Integration

| | |
|---|---|
| **Form** | static lib (libzig-js.a with JavaScriptCore-shaped C headers) or Zig module |
| **Dependencies** | zig-regex and zig-gc (zig-utils), resolved by local path as sibling checkouts (../zig-regex, ../zig-gc); macOS Objective-C bridge glue; the system JavaScriptCore framework only for differential and benchmark targets |
| **Minimum toolchain** | Zig 0.17.0-dev (at least 0.17.0-dev.956; Zig 0.16 will not build it) |
| **Platforms** | macOS AArch64 for both native tiers (the only published performance); Linux x86-64 is correctness-gated in CI and runs interpreter or VM only; Windows, iOS, tvOS and visionOS are unsupported |
| **Thread safety** | Contexts and C API handles are affine to the thread that created them. Use one context per OS thread or workers that exchange structured-clone messages. Contexts created with enable_threads get shared-realm Threads that run in parallel without a GIL by default (gil = true serializes them). |
| **Drop-in for the baseline** | partial: exports an inventoried subset of the JavaScriptCore C API plus an Objective-C bridge pinned to one macOS SDK. Signatures match, but coverage is incomplete, it adds zig-js extensions (ZJSGlobalContextCreateThreaded and others), and it is pre-stabilization. |

## Gotchas

- Harness flaw: the JSC baseline very likely ran without its JIT. WebKit's isJITEnabled() under HAVE(MAC_JIT_RESTRICTIONS) (macOS arm64) with Apple's internal SDK requires the com.apple.security.cs.allow-jit entitlement. build.zig links bench/comparison_jsc.zig against the framework with no codesign or entitlement step, and comparison_jsc.zig sets no options. JSC's derived per-operation costs, about 15.5 ns per modulo-add iteration and 26.7 ns per recursive call, look like its LLInt interpreter. The headline therefore compares the zig-js JIT with interpreter-only JSC.
- The kernels are benchmark-shaped. docs/advanced/vm-quickening.md lists `legacy_narrow` exact-bytecode kernels that match the benchmark rows one by one: four-property-loop (properties), polymorphic-property-loop, fixed-shape three-property allocation loop (object_churn), packed-array push with an 'add-three-and-bitmask' specialization that matches `(i + job + lane) & 65535` (arrays), packed-array sum, numeric-call-loop for direct, method, closure and arguments calls, and observable-numeric-recurrence (fibonacci). Only arithmetic runs in the general baseline JIT. The project says these kernels are not evidence of broad coverage.
- Default `Context` uses an arena that frees nothing until `destroy()` (enable_gc defaults to false). The benchmark turned on the precise GC, so long-running hosts must opt into it.
- Report statistics: the 5.67x zig-js cold-lifecycle scaling geomean includes closure_calls at 11.08x, which comes from a bimodal one-lane median (203.962 ms against a 107.068 ms minimum); without that row the geomean is 5.27x (derived from page data). Rows with up to 46.63% RSD were accepted. The current runners time `__benchmarkInvoke`, not the report's `__benchmarkSelected`.

## Known shortcomings

- Downgraded A to C: the JavaScriptCore runner sets no options and records no tier data; per-operation JSC costs derived from the page (15.5 ns per arithmetic iteration, 26.7 ns per fib call) look like interpreter tiers, so JSC's optimizing JIT probably did not run; docs/benchmarks.md cites a different July 29 report (2.29x/2.51x/2.61x). Zig.
- Enricher: the JavaScriptCore baseline very likely ran with its JIT off (WebKit's isJITEnabled() under macOS arm64 JIT restrictions requires the com.apple.security.cs.allow-jit entitlement and build.zig signs the JSC runner with none; the 15.5 ns per iteration and 26.7 ns per call look like LLInt), so the 2.32x is a zig-js JIT against an interpreter-only JSC. docs/advanced/vm-quickening.md lists legacy_narrow exact-bytecode kernels matching 9 of 10 benchmark rows (four-property loop, polymorphic loop, three-property allocation loop, packed push with an add-three-and-bitmask specialization matching '(i + job + lane) & 65535', call loops, the observable fib recurrence at 96.6% of fib samples); only arithmetic runs in the general baseline JIT. zig-js's own diagnostics have JSC 4.05x faster on JSON, up to 10.47x on deep stringify and about 10x on Wasm SIMD; the cold-scaling geomean 5.67x drops to 5.27x without the bimodal closure_calls row.

## Caveats and trade-offs

The report says the ten kernels 'deliberately exercise guarded native/VM tiers that zig-js currently implements' and is 'not a claim about applications or unsupported workloads'. The JSC runner (bench/comparison_jsc.zig) calls JSGlobalContextCreate/JSEvaluateScript with no JSC options, and the docs say the public C API exposes no tier counters. Derived from page data, JSC spends about 15.5 ns per iteration of a modulo-add loop (24M iterations in 371 ms) and about 26.7 ns per recursive call (18.76M calls in 500 ms), where zig-js spends 3.6 ns and 5.0 ns. Those JSC costs look like its LLInt/baseline tiers, so its optimizing JIT may not have run in this embedding (unverified; a WebSearch snippet only says JSC disables its JIT for third-party in-process embedders on Apple platforms). The README's own JSON/JIT diagnostic shows system JSC 4.05x faster, and the Wasm SIMD report shows JSC about 10x faster. docs/benchmarks.md 'Latest JavaScriptCore comparison' cites a different July 29 report (commit 0f8b33c: 2.29x/2.51x/2.61x, 9 of 10 wins at 8 lanes) than the README's precise-nursery report (commit 14d94ec). README diagnostics name an Apple M2 Pro while the headline report names an M3 Pro. No CPU pinning. No QuickJS, Duktape or Lua comparison. Very new project (31 stars, about 4,800 commits) with daily changes. [retier] No comparison against a JIT-enabled JavaScriptCore; the JSC runner sets no options and records no tier data. Benchmark-shaped kernels: four-property loop, polymorphic loop, three-property allocation loop, packed push with an add-three-and-bitmask specialization matching '(i + job + lane) & 65535', call loops and the observable fib recurrence are handled by exact-bytecode kernels, while only arithmetic runs in the general baseline JIT. Cold-scaling geomean 5.67x is inflated by the bimodal closure_calls row (5.27x without it). Zig.

Exports JavaScriptCore-shaped C headers, so it targets JSC API compatibility; APIs are pre-stabilization; the macOS comparison needs the system JSC framework. Passes 53,175/53,175 configured test262 tests per its README.

## Maintenance

Very active (one author, daily commits, about 4,815 commits, last on 2026-10-06; 31 stars) and MIT-licensed, but pre-stabilization, needs Zig 0.17-dev with sibling checkouts, and has published performance only on macOS arm64. The 2.32x headline is not a fair engine comparison: the JSC baseline was very likely interpreter-only, and most rows go through benchmark-shaped VM kernels. On the project's own JSON diagnostics JSC is 4x faster.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification A, tier now D.
- **Tier reason:** The harness is public (bench/comparison.js, bench/comparison_jsc.zig, bench/comparison_zig_js.zig) with Zig 0.17.0-dev.1441, ReleaseFast and Apple M3 Pro stated, but the baseline's execution configuration is not: comparison_jsc.zig sets no JSC options and records no tier data. JSC's per-operation costs derived from the report (about 15.5 ns per arithmetic iteration, 26.7 ns per fib call) look like its interpreter/baseline tiers rather than DFG/FTL. A first-party claim against a possibly unoptimized baseline is capped at C.
- **Retiered** C to D: C to D: the enricher found the JavaScriptCore baseline almost certainly ran interpreter-only (no allow-jit entitlement on the signed runner, per-op costs matching LLInt) and that 9 of 10 benchmark rows hit exact-bytecode kernels written for those loop shapes, so no comparison against a JIT-enabled baseline survives; results are disclosed, not fabricated, so kept.
- **Verifier notes:** Headline numbers are on the README and match the report's medians (geomean 2.32x recomputed). Downgraded A to C because the baseline may be JSC without its optimizing JIT: the runner sets no JSC options, and JSC's derived per-op costs are interpreter-like. If a JIT-on JSC run (or JSC_useJIT logging) confirms the numbers, this can return to A. Metadata checked: MIT, 31 stars, not a fork, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/.data/benchmark-comparison-2026-07-29-precise-nursery.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/README.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/bench/comparison.js>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/bench/comparison_jsc.zig>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/benchmarks.md>
  - <https://github.com/zig-utils/zig-js/tree/main/bench>
  - <https://github.com/zig-utils/zig-js>
  - <https://github.com/zig-utils/zig-js/commits>
- **Sources the enricher read:**
  - <https://github.com/zig-utils/zig-js>
  - <https://github.com/zig-utils/zig-js/commits/main>
  - <https://github.com/zig-utils/zig-js/issues>
  - <https://github.com/zig-utils/zig-js/issues?q=JavaScriptCore+JIT>
  - <https://github.com/zig-utils/zig-js/tree/main/docs/.data>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/README.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/build.zig>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/.data/benchmark-comparison-2026-07-29-precise-nursery.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/.data/json-jit-pipeline-jsc-2026-10-01.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/.data/baseline-jit-profile-2026-07-16.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/bench/comparison.js>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/bench/comparison_jsc.zig>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/bench/comparison_zig_js.zig>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/architecture.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/platforms.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/baseline-jit.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/optimizing-jit.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/advanced/index.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/advanced/execution-tiers.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/advanced/vm-quickening.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/advanced/embedding.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/api.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/conformance.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/threads/index.md>
  - <https://raw.githubusercontent.com/zig-utils/zig-js/HEAD/docs/dependencies.md>
  - <https://github.com/WebKit/WebKit/blob/main/Source/JavaScriptCore/jit/ExecutableAllocator.cpp>
  - <https://github.com/WebKit/WebKit/blob/main/Source/WTF/wtf/PlatformHave.h>
  - <https://developer.apple.com/forums/thread/821584>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/zig-utils/zig-js`) · [data/wave12/enrich/raw/github_com_zig_utils_zig_js.json](../../../data/wave12/enrich/raw/github_com_zig_utils_zig_js.json) (enrichment confidence 0.65)

</details>
