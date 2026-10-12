# Scala.js WebAssembly backend

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Scala` · `Apache-2.0` · 🟢 active

> Scala.js's WasmGC backend: the same Scala code linked to WebAssembly instead of JavaScript, claimed 30% lower geomean run time.

| | |
|---|---|
| **Beats** | Scala.js JavaScript backend output run in V8 / Node.js (JS emitted code) |
| **Claimed result** | Scala.js WebAssembly backend documentation: for applications dominated by computation inside Scala code the Wasm output should be significantly faster than the JS output (geomean 30% lower run time across our benchmarks, about 1.43x, derived from page data). The 1.19.0 announcement (2025-04-21) gave geomean 15% lower running time. Interop-heavy code may be significantly slower; generated code size about twice as large in fullLink mode. |
| **Workload** | Run-time of Scala.js programs compiled with the WasmGC backend versus the same programs compiled with the Scala.js JS backend, across the project's own benchmark set. |
| **Metric** | throughput |
| **Compiler and flags** | Scala.js linker with withUseWebAssembly(true), ESModule output, ES2022; engine versions Node.js 25, Chrome 137, Firefox 134, Safari 26 listed as supported |
| **Adoption** | 4.7k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/scala-js/scala-js) · [benchmark](https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/doc/project/webassembly.md) |

## Verdict

The Scala.js team's WebAssembly docs page states that, for computation-dominated code, the Wasm output has a 30% lower geomean run time than the same program linked by the Scala.js JS backend across 'our benchmarks' (about 1.43x, derived from page data); the 1.19.0 announcement said 15%. Neither figure names the benchmark list, engine version, hardware or raw results. The probable suite, sjrd/scalajs-benchmarks (richards, deltablue, tracer, sha512, json, kmeans, nbody and others; mean of at least 20 runs over at least 3 s after a warm-up), publishes no results and does not exercise JS interop significantly. The baseline is Scala.js's own JS output, not hand-written JavaScript.

## Use it when

- Scala.js applications whose hot path is computation inside Scala code (algorithms, collections, numeric loops) rather than DOM or JS-library calls.
- Long-heavy code (hashing, 64-bit arithmetic, bignum-style work): Wasm runs Long as a native i64, while the JS backend emulates it with RuntimeLong.
- Projects already on ES modules with a single output module and no @JSExport, where switching is a config change: build both outputs and A/B them on your own workload.
- Targets limited to current engines (Node.js 25, Chrome 137, Firefox 134, Safari 26 or newer).

## Skip it when

- JS-interop-heavy code such as DOM-driven UIs or thin wrappers over JS libraries: the docs warn that the Wasm output may be significantly slower than the JS output there, and the benchmarks behind the speed claim do not exercise interop in any significant way.
- Download-size-sensitive pages: the Wasm output is about twice the size of the JS backend's fullLink output, and wasm-opt is not applied yet.
- Code that needs @JSExport (JS calling Scala methods), module splitting, several @JSExportTopLevel module names or js.dynamicImport: none of these are supported, and multi-module output is still an open issue (#5390).
- Audiences on older browsers or older Node.js lines: Wasm 3.0 (GC, exnref, JS String Builtins) is mandatory, 1.22.0 removed the string-builtins polyfills, and js.async/js.await additionally needs JSPI.
- Standalone Wasm runtimes (wasmtime, WASI): released versions need a JavaScript host. A minimal WasmModule kind with @WasmImport/@WasmExport was merged for the v1.23.0 milestone (#5333) but is not in a release yet.

## How it is fast

The emitter compiles the same linked and optimized Scala.js IR to WasmGC: objects are GC structs dispatched through vtables and itables, and primitives map to Wasm i32/i64/f32/f64, so Long becomes a native i64 instead of the JS backend's software RuntimeLong (a lo/hi Int pair). Strings stay JS strings manipulated through the JS String Builtins, and the backend never uses linear memory. Boxing an Int uses ref.i31 when the value fits in 31 bits and only otherwise calls a JS helper across the Wasm-JS boundary. That boundary is the cost centre, which is why interop-heavy code can be slower than the JS output.

## Compared with alternatives

The catalogued siblings are per-language WasmGC backends measured against their own JS output: J2CL WasmGC (about 2x on the Google Sheets calculation worker), Kotlin/Wasm (chart against Kotlin/JS) and MoonBit. Pick Scala.js Wasm when the code is already Scala.js; its claimed gain (30% geomean) is smaller and less documented than J2CL's production report, but trying it costs one linker setting.

## Integration

| | |
|---|---|
| **Form** | compiler backend (sbt-scalajs linker option) emitting an ES module loader plus WebAssembly |
| **Dependencies** | Scala.js (sbt-scalajs plugin for sbt 1.x, or sbt 2.x from 1.22.0); a JavaScript host with ES2022 and a Wasm 3.0 engine; JSPI only for js.async/js.await |
| **Minimum toolchain** | Scala.js 1.22.0 for the stable backend (experimental from 1.17.0, configured then with the now-deprecated withExperimentalUseWebAssembly); ModuleKind.ESModule and ESVersion.ES2022 required |
| **Platforms** | JS hosts only: Node.js 25, Chrome 137, Firefox 134, Safari 26 or later; JSPI on Node.js 25, Chrome 137, Firefox 143 and Safari Technology Preview 238 at the time the docs were written |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — one linker setting switches backends and the emitted ES modules keep the same layout and interface, but @JSExport is silently ignored, only one output module is allowed, ESModule plus ES2022 are mandatory, and js.async needs JSPI |

## Gotchas

- @JSExport and @JSExportAll are silently ignored rather than rejected. JavaScript cannot call exported Scala methods and cannot stringify Scala objects (toString is an export), including in JS-side string concatenation; the build still succeeds.
- Boxing an Int that does not fit in 31 bits falls back to a JS helper call (bIFallback/uIFallback) across the Wasm-JS boundary, which the emitter README describes as having significant cost in itself. Generic code that boxes many large values can therefore lose some of the Wasm advantage.
- The headline number has no published data. It grew from 15% (1.19.0 post, 2025-04-21) to 30% on the undated docs page, while the JS baseline kept getting faster for Longs: 1.20.2 stopped boxing them in fields, arrays and arguments and made division and remainder 3x faster, and 1.22.0 sped up add, subtract, divide and toString. The gap on Long-heavy code therefore depends on which Scala.js version you compare.
- The likely public suite (sjrd/scalajs-benchmarks) is not a reproducible record of the claim. In its build.sbt, bignumsJVM and bignumsJS are defined as queens.jvm and queens.js, so bignumsJS/run runs queens and the BigInteger benchmark is never measured. run.sh still expects scala-2.12 target directories and old fastopt/fullopt file names. The Wasm settings use the deprecated withExperimentalUseWebAssembly with Node flags for exnref and imported strings, and esVersionToString has no ES2022 case even though 1.22.0 requires ES2022 for Wasm, so the build pins Scala.js 1.20.2 by default.

## Known shortcomings

- First-party: docs say 30% geomean speedup for the WebAssembly backend, the 1.19.0 post said 15%; no benchmark list, engine or hardware given; interop is slower and code is 2x larger.
- The 30% geomean has no published data; it grew from 15% (1.19.0) while the JS Long baseline kept getting faster. Harness flaw in sjrd/scalajs-benchmarks build.sbt: bignumsJS is defined as queens.js, so the BigInteger benchmark never runs; that suite's run.sh is stale (scala-2.12 paths) and its Wasm config pins 1.20.2 with no ES2022 case. @JSExport is silently ignored; Int boxing past 31 bits calls JS across the boundary; output is about 2x the code size.

## Caveats and trade-offs

The 30% geomean figure (and the earlier 15% in the 1.19.0 release post) is a first-party sentence with no benchmark list, machine, engine version or harness named; the release post adds that the benchmarks do not measure JS interop in any significant way. The likely suite (scalajs-benchmarks: richards, deltablue, tracer, sha512, json and others, BSD-3-Clause) publishes no results. Third-party recaps (VirtusLab blog: up to 3.3x over JS on Marr et al.'s cross-language suite, snippet only; ICFP/SPLASH 2025 Wasm workshop abstract) could not be opened, and VirtusLab co-develops the backend. Baseline is Scala.js's own JS backend, not hand-written JavaScript or TypeScript. No @JSExport support and single-module output only.

No @JSExport support, no multi-module emit, JSPI needed for js.async/js.await, JS interop calls slower, Wasm code about 2x larger than JS output.

## Maintenance

Very active (commits through 2026-10-11, Wasm backend declared stable in 1.22.0, standalone WasmModule kind merged for v1.23.0), Apache-2.0 with 4.7k stars, so it is safe to adopt behind a config flag, but measure both backends on your own workload before switching.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/project/webassembly.md states 'geomean 30% lower run time across our benchmarks' versus the JS output, and the 1.19.0 announcement states 15% lower; both are first-party sentences with no benchmark list, engine, hardware or harness named, so tier C.
- **Verifier notes:** Quote verified on the raw doc page; tier C holds (first-party, no methodology). Shortcomings: unspecified benchmarks/engine/hardware, figure moved from 15% (1.19.0) to 30% (docs) with no data, interop-heavy code slower, 2x code size; repo active (last commit 2026-10-11), Apache-2.0, 4.7k stars.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-05 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/doc/project/webassembly.md>
  - <https://github.com/scala-js/scala-js>
  - <https://github.com/scala-js/scala-js/commits>
  - <https://github.com/scala-js/scala-js-website/tree/main/_posts/news>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2025-04-21-announcing-scalajs-1.19.0.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2025-09-06-announcing-scalajs-1.20.1.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2026-01-05-announcing-scalajs-1.20.2.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2026-06-20-announcing-scalajs-1.22.0.md>
  - <https://github.com/sjrd/scalajs-benchmarks>
- **Sources the enricher read:**
  - <https://github.com/scala-js/scala-js>
  - <https://github.com/scala-js/scala-js/commits>
  - <https://github.com/scala-js/scala-js/issues?q=is%3Aissue%20wasm%20performance>
  - <https://github.com/scala-js/scala-js/issues?q=is%3Aissue%20label%3Awasm>
  - <https://github.com/scala-js/scala-js/issues/5333>
  - <https://raw.githubusercontent.com/scala-js/scala-js/main/linker/shared/src/main/scala/org/scalajs/linker/backend/wasmemitter/README.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js/main/linker-private-library/src/main/scala/org/scalajs/linker/runtime/RuntimeLong.scala>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/doc/project/webassembly.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2025-04-21-announcing-scalajs-1.19.0.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2025-09-06-announcing-scalajs-1.20.1.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2026-01-05-announcing-scalajs-1.20.2.md>
  - <https://raw.githubusercontent.com/scala-js/scala-js-website/HEAD/_posts/news/2026-06-20-announcing-scalajs-1.22.0.md>
  - <https://github.com/sjrd/scalajs-benchmarks>
  - <https://raw.githubusercontent.com/sjrd/scalajs-benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/sjrd/scalajs-benchmarks/HEAD/build.sbt>
  - <https://raw.githubusercontent.com/sjrd/scalajs-benchmarks/HEAD/project/plugins.sbt>
  - <https://raw.githubusercontent.com/sjrd/scalajs-benchmarks/HEAD/run.sh>
  - <https://raw.githubusercontent.com/sjrd/scalajs-benchmarks/HEAD/common/benchmark-runner.sh>
  - <https://raw.githubusercontent.com/sjrd/scalajs-benchmarks/HEAD/common/js/src/main/scala/org/scalajs/benchmark/Benchmark.scala>
  - https://virtuslab.com/blog/scala/scala-to-web-assembly/ (fetch failed, DNS blocked; WebSearch snippet only: up to 3.3x over JS on Marr et al.'s cross-language benchmarks)
  - https://contributors.scala-lang.org/t/compile-to-llvm-or-wasm/6154/55 (fetch failed, DNS blocked)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/scala-js/scala-js`) · [data/wave13/enrich/raw/github_com_scala_js_scala_js.json](../../../data/wave13/enrich/raw/github_com_scala_js_scala_js.json) (enrichment confidence 0.75)

</details>
