# J2CL WasmGC backend (Google Sheets calculation worker port)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Google's Java transpiler with a WasmGC backend (J2Wasm); Sheets reports its calc worker about 2x faster than J2CL's JavaScript output.

| | |
|---|---|
| **Beats** | The same Java code transpiled by J2CL to Closure-compiled JavaScript, running in V8 (Chrome) |
| **Claimed result** | Final WasmGC build of the Sheets calculation worker about 2x faster calculation than the JavaScript build, described as a 4x improvement over the first WasmGC build (snippet only); the JavaScript build had been more than 3x slower than the Java build on the server (snippet only). The record's 'speculative inlining plus devirtualization cut Chrome calculation time by about 40%' figure was not visible in the snippets seen by the verifier and is unconfirmed here. |
| **Workload** | Google Sheets spreadsheet calculation worker, written in Java, built once as JavaScript through J2CL and once as WasmGC, calculation time measured in Chrome by the Sheets team. |
| **Metric** | throughput |
| **Compiler and flags** | J2CL Java-to-Wasm output optimized with Binaryen wasm-opt (Binaryen's README lists J2CL/J2Wasm as a wasm-opt user); exact flags not seen |
| **Adoption** | 1.4k stars; the Wasm output runs in production in Google Sheets |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/google/j2cl) · [benchmark](https://web.dev/case-studies/google-sheets-wasmgc) |

## Verdict

Google's web.dev case study (not reachable here; snippets only) says the Sheets calculation worker, Java compiled by J2CL, ran more than 3x slower as JavaScript than on the JVM, the first WasmGC build was about 2x slower than the JS build, and the tuned WasmGC build ended about 2x faster than JS in desktop Chrome and Edge; no hardware, Chrome version or method is given, and Wasm would still be about 1.5x the JVM's time (derived from the snippet figures). The V8 blog (opened via its GitHub source) adds first-party measurements: wasm-opt speeds J2Wasm builds of four Octane-style benchmarks by 1.9x on average, and speculative inlining is worth about 30% on the Sheets calc engine.

## Use it when

- A large, CPU-bound Java codebase (spreadsheet formula engines, parsers, layout or business logic) already shared between server and web through J2CL, where the JavaScript build is measurably slower than the JVM.
- Compute that runs in a web worker with coarse-grained calls across the JS boundary, so interop cost stays small relative to the work.
- Code heavy in Java long arithmetic or tight object-oriented loops: the JS backend boxes long into goog.math.Long objects, while Wasm has native 64-bit integers (inference from docs/semantics.md, not separately measured).
- Targets limited to current Chromium-based browsers (WasmGC from Chrome 119) where you can afford a Bazel plus Binaryen build.

## Skip it when

- Code that is chatty with the DOM or JS APIs, or relies on JS-native regex and string machinery: the Sheets team had to swap the Wasm-compiled re2j for the browser's RegExp to fix regex speed (snippet only).
- You need Java reflection, Enum.valueOf, java.net or a complete JRE: J2CL emulates only a subset (docs/limitations.md).
- Non-Bazel or Windows-native toolchains: the workflow is Bazel-only and not supported on Windows (use WSL).
- You need stable, cross-browser production support guarantees: the README calls Wasm support 'work-in-progress' and the project 'alpha release for developer preview'; the 2x figure is reported only for desktop Chrome and Edge.
- Small or startup-dominated workloads, where module compile and tier-up time count more than steady-state throughput (not measured in any public source seen).

## How it is fast

Java objects become WasmGC structs and arrays with static types, so the engine skips JavaScript's dynamic property and shape checks, and Java long maps to native 64-bit integers instead of the goog.math.Long objects the JS backend uses (docs/semantics.md). The optimized rule runs Binaryen wasm-opt in three stages of repeated -O3 with --closed-world, --traps-never-happen, --gufa (whole-program flow analysis), --unsubtyping, --type-merging, itable merging and J2CL-specific passes; the V8 team measured wasm-opt making J2Wasm builds of Box2D, DeltaBlue, RayTrace and Richards 1.9x faster on average. At run time V8's speculative inlining of indirect calls (about 30% on the Sheets calc engine) and Wasm deoptimization (up to 7%, Chrome M137) supply the virtual-call devirtualization a JVM would do.

## Compared with alternatives

Pick J2CL's Wasm backend when the code is Java; the closest siblings do the same JS-to-WasmGC switch for other languages: Kotlin/Wasm for Kotlin, the Scala.js WebAssembly backend for Scala, and wasm_of_ocaml for OCaml. None of them gives a reproducible JS-versus-Wasm harness either, so choose by source language, not by the headline numbers.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Bazel (Bazelisk), Binaryen wasm-opt (third_party:binaryen), J2CL's JRE emulation |
| **Minimum toolchain** | Bazel with the j2cl rules; browser with WasmGC (Chrome 119+ per docs) and Wasm exception handling (enabled in every wasm-opt stage) |
| **Platforms** | Browsers and JS engines with WasmGC; build on Linux/macOS (Windows via WSL only) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same Java source as the J2CL JavaScript build, but a different artifact (wasm module plus JsInterop glue) and a stricter browser floor |

## Gotchas

- The optimized j2wasm_application sets jre.checks.checkLevel=MINIMAL and jre.checkedMode=DISABLED and always passes Binaryen --closed-world --traps-never-happen, so code that would trap or depends on Java runtime checks (bounds, casts, nulls) can behave differently between the _dev and optimized builds.
- The JS baseline differs semantically too: it maps long to goog.math.Long objects, float to 64-bit doubles and skips array bounds checks (docs/semantics.md, docs/limitations.md), so part of the gap is representation cost rather than compiler quality.
- Wasm-specific JRE bugs have occurred, e.g. HashMap.computeIfAbsent with a null key threw under Wasm (issue #199, fixed 2023-08-15).
- The speedup is shared credit: the speculative-inlining figures in V8's posts are V8 engine work (about 30%, not the record's unconfirmed 40%), and the 1.9x is Binaryen's, measured against unoptimized J2Wasm output rather than against JavaScript.

## Known shortcomings

- Only source is Google's own Sheets case study seen in snippets (web.dev blocked): about 2x vs the JavaScript build and 4x vs the first WasmGC build; the 40% inlining figure is unconfirmed; the gain also comes from V8 and Binaryen work; the Sheets code is not public.
- Enricher: the 2x remains snippet-only (web.dev and the SED transcript blocked); the v8.dev source says speculative inlining gained about 30% on Sheets (not 40%), wasm-opt is 1.9x over unoptimised J2Wasm rather than over JS, and deopts cost up to 7% (Chrome M137); the optimised build uses jre.checks MINIMAL plus Binaryen --traps-never-happen --closed-world; the JS baseline uses goog.math.Long with no bounds checks; no published results in benchmarking/.

## Caveats and trade-offs

Snippet only: web.dev (and its web.developers.google.cn mirror) do not resolve here, so the case study was not opened; the 2x and 4x figures were read from WebSearch snippets of the page, and press coverage (heise, 9to5Google, mezha.ua) only repeats Google's claim. First-party Google claim on the proprietary Sheets calculation engine, not reproducible from the repo; no hardware, Chrome version or flags stated; the gain is reported for desktop Chrome and Edge. The 2x is not attributable to J2CL alone: it combines J2CL's WasmGC backend, Binaryen wasm-opt, V8 engine work (speculative inlining and devirtualization are V8 optimizations) and Sheets code changes; the same case study reports that moving regex from a WasmGC-compiled re2j to Chrome's native RegExp made regex operations nearly 100x faster (record's figure, not re-seen). Since the JavaScript build was more than 3x slower than Java, the 2x gain recovers only part of that gap. The repo README calls Wasm support 'fully working but ... work-in-progress'. The repo has a benchmarking/ folder (benchmarking/README.md: `j2 bench <name>` runs Closure, Wasm and JVM targets, e.g. octane Box2dBenchmark) but no published results were seen.

Output needs a browser with WasmGC (Chrome 119 or later and other current engines) and a Binaryen optimization step. Java source is required, so this only helps code already written in Java. JS interop and browser-native APIs still cross the Wasm boundary.

## Maintenance

Actively developed (8,654 commits, last commit 2026-10-11), Apache-2.0 and in production in Google Sheets, but the Wasm backend is labelled experimental and the repo publishes no benchmark results, so the evidence stays first-party.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google case study on the proprietary Sheets calculation engine (WasmGC build vs the J2CL JavaScript build in Chrome), seen only through WebSearch snippets; no hardware, flags or public harness, so not reproducible and capped at C. The J2CL repo's benchmarking/ harness (j2 bench on Closure, Wasm and JVM) publishes no results.
- **Verifier notes:** Real and notable (1.4k stars, production use in Google Sheets), Apache-2.0, last commit 2026-10-11 confirmed. Shortcomings: snippet-only evidence from an unopened first-party page, proprietary workload, no methodology, speed-up shared with V8 and Binaryen work; the 40% sub-claim could not be re-confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-95 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/google/j2cl>
  - <https://github.com/google/j2cl/commits/master>
  - <https://raw.githubusercontent.com/google/j2cl/HEAD/benchmarking/README.md>
- **Sources the enricher read:**
  - <https://github.com/google/j2cl>
  - <https://raw.githubusercontent.com/google/j2cl/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/j2cl/HEAD/benchmarking/README.md>
  - <https://raw.githubusercontent.com/google/j2cl/HEAD/docs/getting-started-j2wasm.md>
  - <https://raw.githubusercontent.com/google/j2cl/HEAD/docs/limitations.md>
  - <https://raw.githubusercontent.com/google/j2cl/HEAD/docs/semantics.md>
  - <https://raw.githubusercontent.com/google/j2cl/HEAD/build_defs/internal_do_not_use/j2wasm_application.bzl>
  - <https://github.com/google/j2cl/tree/master/benchmarking/java/com/google/j2cl/benchmarks>
  - <https://github.com/google/j2cl/issues?q=is%3Aissue%20wasm>
  - <https://github.com/google/j2cl/issues/199>
  - <https://raw.githubusercontent.com/v8/v8.dev/main/src/blog/wasm-gc-porting.md>
  - <https://raw.githubusercontent.com/v8/v8.dev/main/src/blog/wasm-speculative-optimizations.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/google/j2cl`) · [data/wave13/enrich/raw/github_com_google_j2cl.json](../../../data/wave13/enrich/raw/github_com_google_j2cl.json) (enrichment confidence 0.6)

</details>
