# Kotlin/Wasm (JetBrains kotlin-wasm-benchmarks)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Kotlin` · `Apache-2.0` · 🟢 active

> Kotlin's WasmGC compiler backend; JetBrains' 2023 charts show 1.25-2.5x faster than Kotlin/JS output on most macro benchmarks.

| | |
|---|---|
| **Beats** | Kotlin/JS output (JavaScript) running in V8 |
| **Claimed result** | Relative-time bar chart (Kotlin/JS = 100%, lower is better), read off the screenshot by pixel position so approximate (derived from page data): List about 39% (about 2.5x faster), Queens about 64%, Bounce about 64%, CD about 66%, Sieve about 69%, Permute about 70%, Storage about 73%, Havlak about 77%, Towers about 77%, nBody about 80% (so roughly 1.25-1.6x faster), Mandelbrot about 102% (no gain), JSON about 174% (about 1.7x slower). Compose Multiplatform chart (JVM = 100%): Wasm about 156% / 181% / 158% vs JS about 329% / 399% / 315% on AnimatedVisibility / LazyGrid / VisualEffects, so Wasm about 2.0-2.2x faster than JS (derived from page data; Compose data from JetBrains/compose-multiplatform branch bench_with_kwasm). |
| **Workload** | are-we-fast-yet style benchmark set (CD, Havlak, JSON, Mandelbrot, nBody, Bounce, List, Permute, Queens, Sieve, Storage, Towers) built once for Kotlin/Wasm and once for Kotlin/JS and run in V8 through kotlinx-benchmark; a second chart runs Compose Multiplatform UI benchmarks (AnimatedVisibility, LazyGrid, VisualEffects) on JVM, Wasm and JS. |
| **Metric** | throughput |
| **Compiler and flags** | Screenshots were committed 2023-12-07 (commit a82a6cb, Kotlin/Wasm Alpha era); the Kotlin, V8/Chrome and Binaryen versions used for them are not stated. JetBrains' December 2023 'Kotlin for WebAssembly goes Alpha' post says the results came from a recent Google Chrome (search snippet only). The current harness pins kotlin_version=2.3.20-RC (gradle.properties), Node 26.2.0, d8/V8 15.0.45 and Binaryen 129 (gradle/libs.versions.toml), with kotlin.js.ir.output.granularity=whole-program; README tasks wasmBenchmark, wasmOptBenchmark (Binaryen-optimised) and jsBenchmark; which Wasm variant the chart shows is not stated. |
| **Adoption** | JetBrains/kotlin 53.5k stars; Kotlin/kotlin-wasm-benchmarks 23 stars (last commit 2026-10-07 is for the benchmark repo) |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/JetBrains/kotlin) · [benchmark](https://github.com/Kotlin/kotlin-wasm-benchmarks) |

## Verdict

JetBrains' December 2023 chart (Kotlin 1.9.20 Alpha-era harness; the committed build ran JS on a Node 21 V8 canary and Wasm on d8 11.9.125; no CPU stated) shows Kotlin/Wasm taking 39-80% of the Kotlin/JS time on 10 of 12 are-we-fast-yet benchmarks (1.25-2.5x faster), about 102% on Mandelbrot and about 174% on JSON. A second chart from Compose's bench_with_kwasm branch (Compose 1.5.10-dev-wasm01, Kotlin 1.9.20-RC, browser targets) puts Wasm at 156-181% of JVM time against 315-399% for Kotlin/JS, about 2x faster than JS; all values are read off PNGs.

## Use it when

- CPU-bound Kotlin code you already ship as Kotlin/JS (object graphs, recursion, collections, simulations): 10 of 12 are-we-fast-yet benchmarks ran in 39-80% of the Kotlin/JS time in JetBrains' chart.
- Compose Multiplatform web UIs, where Wasm is the web target and JetBrains' chart puts it at about 2x faster than the Kotlin/JS build (156-181% of JVM time vs 315-399%).
- Sharing one Kotlin codebase across JVM, Android, native and web, when your users run Chrome or Chromium 119+, Firefox 120+ or Safari 18.2+.
- Server-side or plugin use in standalone Wasm VMs through the wasmWasi target (the benchmark harness runs it on Wasmtime with -W gc,exceptions,function-references and on WasmEdge).

## Skip it when

- String-heavy work such as parsing or text processing: the JSON benchmark (a string-only parser) took about 174% of the Kotlin/JS time.
- Tight floating-point loops that the JS JIT already handles well: Mandelbrot was level (about 102% of Kotlin/JS).
- Audiences on older browsers: Safari before 18.2 is not supported, and Chrome before 119 needs a Kotlin release older than 1.9.20 plus a flag.
- Code that crosses the Wasm/JS boundary constantly (DOM-heavy logic, many small calls into JS libraries): interop types are restricted and the boundary cost is not measured in these charts.
- Decisions that need current numbers: the only published results are 2023 Alpha-era screenshots without hardware or engine details; re-run the harness on your Kotlin version and engine.

## How it is fast

Kotlin classes and arrays become statically typed WasmGC structs and arrays managed by the engine's garbage collector, and Int, Long and Double arithmetic maps to native Wasm i32/i64/f64 operations, so the engine runs ahead-of-time typed code rather than speculating on the types of Kotlin/JS output. Production builds are post-optimised with Binaryen's wasm-opt (the harness pins Binaryen 116 in 2023 and 129 today). The largest gains are on allocation- and pointer-heavy code (List, a recursive linked-list benchmark, about 2.5x), not on string handling.

## Compared with alternatives

Pick Kotlin/Wasm when the code is already Kotlin or Compose Multiplatform; its 1.25-2.5x over Kotlin/JS on most macro benchmarks is in the same range as J2CL's WasmGC result (about 2x on the Sheets worker) and above wasm_of_ocaml's early 10-20%. Scala.js's Wasm backend is the equivalent choice for Scala code, and MoonBit is a new language rather than a backend for existing code.

## Integration

| | |
|---|---|
| **Form** | compiler target (Kotlin Multiplatform wasmJs / wasmWasi via the Kotlin Gradle plugin); output is a .wasm module plus .mjs loader |
| **Dependencies** | Kotlin Gradle plugin (multiplatform); an engine with WasmGC and (legacy or new) exception handling; Binaryen for optimised production builds |
| **Minimum toolchain** | Kotlin 1.9.20+ (final WasmGC encoding, per the Kotlin docs); the benchmark harness now pins Kotlin 2.3.20-RC; Gradle |
| **Platforms** | Chrome/Chromium 119+, Firefox 120+, Safari/WebKit 18.2+, Node.js (harness pins 26.2.0), V8 d8, SpiderMonkey shell, JavaScriptCore, Wasmtime and WasmEdge (wasmWasi) |
| **Thread safety** | not documented in the sources read |
| **Drop-in for the baseline** | partial — the same common Kotlin code builds for both targets, but it is a separate target with stricter JS-interop rules (external declarations limited to JsAny subtypes and selected built-in types), needs WasmGC-capable engines, and is still Beta |

## Gotchas

- Cross-host baseline in the chart's own harness: the build script committed with the screenshots (a82a6cb, Kotlin 1.9.20) runs Kotlin/JS under nodejs() on Node 21.0.0-v8-canary202309167e82ab1fa2 and Kotlin/Wasm under d8() on d8 11.9.125 (plus both on a 2023-09-21 SpiderMonkey nightly shell); it has no browser runner, while the Kotlin docs say the results come from Google Chrome, so which run produced the chart, and whether both sides ran in the same V8 host, is undocumented.
- CD, Havlak, JSON, nBody and Mandelbrot sit in the slowMacro configuration: one measured invocation (iterations = 1, iterationTime = 1 ns) after 5 warm-ups in 2023 (10 today), so those five bars rest on a single sample per target; the fast set uses 5 x 50 ms iterations. The chart also does not say whether it shows Dev or Prod builds, or the plain or Binaryen-optimised (wasmOpt) Wasm variant.
- Open issue #30 (2026-10-05): the WasmEdge and Wasmtime benchmark tasks do not depend on the tasks that build the wasmWasi binaries, so after a clean build they fail, and otherwise a stale .wasm from an earlier build can be benchmarked silently and distort results.
- The README's run instructions (wasmBenchmark, wasmOptBenchmark, -Pkotlin_version=1.8.0) describe the 2023 'wasm' and 'wasmOpt' targets, which the current build script no longer registers; it now builds per-engine tasks such as wasmJsFastMicro_Wasm_Prod_WasmEdgeBenchmark and loads a prebuilt kotlinx-benchmark 0.6.0 plugin jar checked into the repo.

## Known shortcomings

- Two first-party PNG charts committed 2023-12-07 (Kotlin/Wasm Alpha era) with no hardware or engine versions; the baseline is Kotlin/JS output; JSON is about 1.7x slower.
- Cross-host baseline in the chart's own harness: the build script committed with the screenshots (a82a6cb, Kotlin 1.9.20) runs Kotlin/JS under Node 21.0.0 V8 canary and Kotlin/Wasm under d8 11.9.125, with no browser runner although the docs say Chrome; which run produced the chart and whether both sides shared one V8 host is undocumented. CD, Havlak, JSON, nBody and Mandelbrot are single-sample rows (iterations = 1). Open issue #30: a stale wasmWasi binary can be benchmarked silently. Charts not refreshed since 2023-12-07.

## Caveats and trade-offs

Numbers exist only as two PNG screenshots committed 2023-12-07, nearly three years old and predating Kotlin 2.x and current V8, so they may not reflect today's compiler; read by eye (+-3 points); no CPU, engine version, Kotlin version or warm-up settings stated; baseline is Kotlin/JS compiler output, not hand-written JS or TypeScript; README calls the suite work-in-progress; the benchmark repo's LICENSE.md lists Apache-2.0, BSD and MIT for different benchmark sources without mapping them; the compiler itself (JetBrains/kotlin) is Apache-2.0 per its README; JSON is about 1.7x slower and Mandelbrot is level, so the win is workload-dependent; the Compose chart comes from a separate compose-multiplatform benchmark branch; the entry id points at the whole Kotlin compiler repo, the Wasm backend being one part of it. [retier] Numbers exist only as two PNG screenshots committed 2023-12-07 (commit a82a6cb, Kotlin 1.9.20), read by eye (+-3 points), predating Kotlin 2.x and current V8. Cross-host baseline: the build script committed with the screenshots runs Kotlin/JS under nodejs() on Node 21.0.0-v8-canary202309167e82ab1fa2 and Kotlin/Wasm under d8() on d8 11.9.125 (plus both on a 2023-09-21 SpiderMonkey nightly shell) and has no browser runner, while the Kotlin docs say the results come from Google Chrome, so which run produced the chart and whether both sides ran in one V8 host is undocumented. CD, Havlak, JSON, nBody and Mandelbrot sit in the slowMacro configuration with one measured invocation (iterations = 1) after warm-up, so five bars rest on a single sample; the fast set uses 5 x 50 ms iterations. Whether the chart shows Dev or Prod builds, or the plain or Binaryen-optimised Wasm variant, is not stated. No CPU, engine version or Kotlin version stated; baseline is Kotlin/JS compiler output, not hand-written JS; JSON is about 1.7x slower and Mandelbrot level. Open issue #30 (2026-10-05): the WasmEdge and Wasmtime tasks can silently benchmark a stale wasmWasi binary. The current harness (Kotlin 2.3.20-RC, Node 26.2.0, d8/V8 15.0.45, Binaryen 129) has no published results; the README's run instructions describe 2023 targets the build no longer registers. The Compose chart comes from a separate compose-multiplatform benchmark branch. The entry id points at the whole Kotlin compiler repo.

Needs a WasmGC-capable engine (current Chromium, Firefox, Node); JS interop and DOM access cross the Wasm/JS boundary; Wasm output is larger on first load than hand-tuned JS for small apps (not measured here); string-heavy code is the weak spot (JSON benchmark is slower on Wasm).

## Maintenance

The Kotlin compiler (Apache-2.0, 53.5k stars) is actively developed with Kotlin/Wasm in Beta, and the benchmark repo is maintained (last commit 2026-10-07, harness on Kotlin 2.3.20-RC, V8 15.0.45, Node 26.2.0), but the published charts have not been refreshed since 2023-12-07.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party JetBrains charts (two PNGs in the kotlin-wasm-benchmarks README) compare Kotlin/Wasm against Kotlin/JS output in V8/Chrome; the benchmark code is public (Kotlin/kotlin-wasm-benchmarks src/, kotlinx-benchmark), but the charts state no CPU, engine version, Kotlin version or flags, so tier C.
- **Retiered** C to D: Enricher: the chart's own harness (commit a82a6cb) runs Kotlin/JS under Node 21 V8 canary and Kotlin/Wasm under d8 11.9.125 with no browser runner, so the published bars compare different V8 hosts (cross-run precedent: PostgreSQL, MySQL, ODB); five of twelve bars are single samples (iterations = 1); values exist only as pixel readings of a 2023 screenshot. No like-for-like measurement is documented, so D.
- **Verifier notes:** Chart values match the record within reading error. Shortcomings to record: evidence is two first-party screenshots dated 2023-12-07 (Kotlin/Wasm Alpha) with no hardware or engine versions; Kotlin/JS output, not hand-written JS, is the baseline; JSON about 1.7x slower. Kotlin/kotlin-wasm-benchmarks: 23 stars, default branch dev, last commit 2026-10-07; JetBrains/kotlin 53.5k stars.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/commits/dev>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/commits/master/screenshots>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/commits/dev/screenshots>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/screenshots/kotlin-wasm-macro-benchmarks.png>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/screenshots/compose-multiplatform-benchmarks.png>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/gradle.properties>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/gradle/libs.versions.toml>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/build.gradle.kts>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/settings.gradle.kts>
  - <https://github.com/JetBrains/kotlin>
- **Sources the enricher read:**
  - <https://github.com/JetBrains/kotlin>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/tree/dev/src>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/tree/dev/src/commonMain/kotlin>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/tree/dev/src/commonMain/kotlin/macroBenchmarks>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/tree/dev/src/commonMain/kotlin/macroBenchmarks/som>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/tree/dev/src/commonMain/kotlin/infra>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/issues>
  - <https://github.com/Kotlin/kotlin-wasm-benchmarks/issues/30>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/build.gradle.kts>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/gradle.properties>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/gradle/libs.versions.toml>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/settings.gradle.kts>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/src/commonMain/kotlin/macroBenchmarks/MacroBenchmarks.kt>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/src/commonMain/kotlin/macroBenchmarks/Json.kt>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/src/commonMain/kotlin/macroBenchmarks/List.kt>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/src/commonMain/kotlin/macroBenchmarks/Mandelbrot.kt>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/src/commonMain/kotlin/infra/MacroBenchmark.kt>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/src/commonMain/kotlin/infra/MacroBenchmarksBase.kt>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/jsStubs.js>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/screenshots/kotlin-wasm-macro-benchmarks.png>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/dev/screenshots/compose-multiplatform-benchmarks.png>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/a82a6cb/build.gradle.kts>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/a82a6cb/gradle.properties>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/a82a6cb/README.md>
  - <https://raw.githubusercontent.com/Kotlin/kotlin-wasm-benchmarks/a82a6cb/settings.gradle.kts>
  - <https://github.com/JetBrains/compose-multiplatform/tree/bench_with_kwasm/benchmarks/ios/jvm-vs-kotlin-native>
  - <https://raw.githubusercontent.com/JetBrains/compose-multiplatform/bench_with_kwasm/benchmarks/ios/jvm-vs-kotlin-native/build.gradle.kts>
  - <https://raw.githubusercontent.com/JetBrains/compose-multiplatform/bench_with_kwasm/benchmarks/ios/jvm-vs-kotlin-native/gradle.properties>
  - <https://raw.githubusercontent.com/JetBrains/kotlin-web-site/master/docs/topics/wasm/wasm-overview.md>
  - <https://raw.githubusercontent.com/JetBrains/kotlin-web-site/master/docs/topics/wasm/wasm-configuration.md>
  - <https://raw.githubusercontent.com/JetBrains/kotlin-web-site/master/docs/topics/wasm/wasm-js-interop.md>
  - https://blog.jetbrains.com/kotlin/2023/12/kotlin-for-webassembly-goes-alpha/ (fetch failed: ENOTFOUND; claim known from a WebSearch snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jetbrains/kotlin`) · [data/wave13/enrich/raw/github_com_jetbrains_kotlin.json](../../../data/wave13/enrich/raw/github_com_jetbrains_kotlin.json) (enrichment confidence 0.75)

</details>
