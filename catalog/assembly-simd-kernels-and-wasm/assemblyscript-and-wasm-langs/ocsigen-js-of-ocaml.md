# wasm_of_ocaml (OCaml to WebAssembly GC compiler in ocsigen/js_of_ocaml)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `OCaml` · `LGPL-2.1-or-later WITH OCaml-LGPL-linking-exception` · 🟢 active

> OCaml-bytecode-to-WebAssembly-GC compiler in the js_of_ocaml repo; preliminary 2023 runs: 10-20% faster than js_of_ocaml's JavaScript.

| | |
|---|---|
| **Beats** | js_of_ocaml (OCaml bytecode to JavaScript) output running in Node.js / V8 |
| **Claimed result** | Early benchmarks suggested compiled programs typically run around 10-20% faster than the js_of_ocaml equivalent (preliminary figure from a late-2023 OCaml forum update, snippet only). |
| **Workload** | OCaml programs compiled once by wasm_of_ocaml and once by js_of_ocaml and timed in Node.js. The repo's benchmarks/ directory is the harness: `make bench` runs microbenchmarks plus benchmark-fiat-crypto, benchmark-ocamlc, benchmark-partial-render-table, benchmark-camlboy and benchmark-others for current-bench; report-wasm-cb.config charts wasm_of_ocaml times on node and report-jsoo-cb.config charts js_of_ocaml times on node as a separate series (no shared reference line); run.config runs node with --no-liftoff. Which workloads the quoted 10-20% figure covers is not stated. |
| **Metric** | throughput |
| **Compiler and flags** | wasm_of_ocaml with Binaryen 119 or later; flags not seen |
| **Adoption** | 1.1k stars (repo shared with js_of_ocaml) |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/ocsigen/js_of_ocaml) · [benchmark](https://discuss.ocaml.org/t/an-update-from-the-ocaml-wasm-organization/13114) |

## Verdict

The only speed figure is the ocaml-wasm developers' late-2023 forum update, seen here as search snippets: compiled programs 'typically run around 10-20% faster' than the js_of_ocaml output, with no programs, engine version, CPU or flags given. The repo's benchmarks/ harness runs both outputs under node --no-liftoff and records child-process user CPU time (tms_cutime, all threads, startup included; 1 s warm-up, at least 10 runs to a 3% interval). It builds js_of_ocaml with --opt=2 --effects=disabled but passes no effects flag to wasm_of_ocaml, so on OCaml 5 the Wasm side uses its jspi default. No results from that harness are published in the repo.

## Use it when

- OCaml programs already shipped with js_of_ocaml whose hot paths are CPU-bound pure OCaml (data structures, parsers, emulators, numeric code) and whose users run Chrome 119+, Firefox 122+, Safari 18.2+ or Node.js 22+.
- Code heavy in Int64, Int32 or boxed arithmetic, which js_of_ocaml emulates with JavaScript objects and wasm_of_ocaml maps to native i64/i32 fields with unboxing.
- Running OCaml under a WASI 0.1 engine (Node.js, Wasmtime with all proposals, Wizard) where no JavaScript interop is needed.
- Large Bonsai/Incremental-style web apps that already build with dune and want the Wasm backend without changing source, after re-implementing any `.js` stubs in Wasm.

## Skip it when

- When you must support older engines: the output needs Wasm GC (with i31 and typed function references), tail calls and exception handling, and JSPI effects need Chrome 137 or Node.js 25.
- Code dominated by JavaScript interop (DOM calls, string and float conversions): each OCaml float crossing the boundary needs Js.to_float/Js.float, and no published measurement shows a gain there.
- Effect-heavy OCaml 5 code on the default --effects=jspi: the README says performing effects is slower than CPS, and the fastest mode (--effects=native) needs an experimental WasmFX flag.
- Projects with many hand-written `.js` primitives, which all need Wasm or WAT reimplementations; the Thread library and SharedArrayBuffer/Atomics are unsupported (feature request #1930 is open).
- When you need hard numbers before switching: the only speed figure is a preliminary 2023 'typically 10-20% faster', so benchmark your own program.

## How it is fast

It compiles js_of_ocaml's optimized intermediate code (flow analysis, inlining, dead-code removal) to the Wasm GC proposal rather than to JavaScript. OCaml values become typed structs and arrays, ints become i31ref, Int64 is a struct holding a native i64 (js_of_ocaml uses an MlInt64 object built from three JS numbers), and tail calls and exceptions use the Wasm tail-call and exception-handling instructions. Later releases added float and integer unboxing, specialized number comparisons, and direct calls to statically known functions. Binaryen's wasm-merge, wasm-metadce and wasm-opt (-O2/-O3, --traps-never-happen) finish the output.

## Compared with alternatives

It is the WasmGC backend for OCaml, playing the role J2CL's WasmGC backend, Kotlin/Wasm and the Scala.js WebAssembly backend play for their languages. Pick it when your code is already OCaml on js_of_ocaml; expect a modest gain (10-20% preliminary) rather than J2CL's reported 2x on the Sheets worker, and note that its figure, unlike Kotlin's chart, is a snippet with no published programs.

## Integration

| | |
|---|---|
| **Form** | module (OCaml compiler executable distributed through opam as wasm_of_ocaml-compiler; output is a JS loader plus .wasm assets) |
| **Dependencies** | OCaml &gt;= 4.14, js_of_ocaml (same version), a system Binaryen &gt;= 119 (conf-binaryen, which provides wasm-opt, wasm-merge and wasm-metadce), cmdliner &gt;= 2.0, sedlex, menhir, yojson, ppxlib; dune &gt;= 3.17 for built-in dune rules |
| **Minimum toolchain** | OCaml 4.14 (5.x for effect handlers), Binaryen 119+; engines Chrome 119, Firefox 122, Safari 18.2, Node.js 22 |
| **Platforms** | Any Wasm GC engine (browsers, Node.js); WASI 0.1 via Node.js, Wasmtime (-W=all-proposals=y) or Wizard; the compiler runs on Linux, macOS and Windows |
| **Thread safety** | Single-threaded output: the Thread library is not supported and SharedArrayBuffer/Atomics is an open feature request (#1930) |
| **Drop-in for the baseline** | partial: it takes the same bytecode and the js_of_ocaml libraries, but floats need explicit Js.to_float/Js.float conversions, the Typed_array typings changed, `.js` stub primitives must be rewritten in Wasm, the default effects mode is jspi, and the output layout is file.js plus file.assets/ |

## Gotchas

- Integers are i31ref values (gc_target.ml), so overflow happens at 31 bits, unlike js_of_ocaml's full 32-bit ints and native 63-bit ints. Code that is correct under one backend can wrap differently under the other.
- Codegen bugs fixed only after the latest release (6.4.1, 2026-06-30, dev section of CHANGES.md): `x land y` was assumed to fit in 31 bits when one operand did, which is wrong for negative operands (#2490); specialized Genarray get/set read one field too far, returning wrong values or going out of bounds (#2427); and the Wasm linker mis-decoded instructions (#2504).
- Effects cannot be performed across JavaScript frames in any mode. With the default --effects=jspi, handlers also cannot be installed inside JavaScript callbacks, since JSPI only suspends Wasm running on its own stack, and the program then runs on a JSPI stack.
- WASI builds: weak references and ephemerons are never reclaimed, JavaScript bindings are unavailable, and the manual says Marshal is quadratic (a dev-branch change, #2470, removes that).

## Known shortcomings

- The 10-20% figure is a preliminary 2023 forum claim seen in snippets only (discuss.ocaml.org, lwn.net, ocsigen.org blocked); the report-wasm-cb.config charts show wasm_of_ocaml times only, not against js_of_ocaml.
- The 10-20% claim is still snippet-only (ocsigen.org ENOTFOUND; no published results in the repo). Harness: timings are tms_cutime user CPU including node startup with node --no-liftoff; the microbench builds jsoo with --effects=disabled and wasm with no flag (jspi default on OCaml 5), so the effect modes differ; the fiat-crypto bench times the compilers, not their output. Integers are i31ref (31-bit vs jsoo's 32-bit). Codegen fixes landed after 6.4.1: x land y (#2490), Genarray off-by-one (#2427), linker (#2504).

## Caveats and trade-offs

Snippet only: the forum post (discuss.ocaml.org), its LWN repeat and the ocsigen.org performance page do not resolve here, so the 10-20% figure was read from WebSearch snippets; it is a 2023 preliminary result with no published programs or methodology, and later versions (6.x, many 'Runtime/Wasm: faster ...' CHANGES entries) are not quantified. A newer ocaml.org post (April 2026) also could not be opened. The repo harness records timings but states no CPU model, Node.js version or flags (run.config is tuned per machine). Output requires Wasm GC, tail-call and exception-handling support (Chrome 119, Node.js 22, Firefox 122, Safari 18.2 or newer); effect handlers default to JSPI, which the README says is slower for performing effects than --effects=cps. Licence: dune-project declares GPL-2.0-or-later and LGPL-2.1-or-later WITH OCaml-LGPL-linking-exception; the LICENSE file puts the compiler, lib, runtime, toplevel and tools under LGPL 2.1 with a static-linking exception.

Generated code needs the Wasm GC, tail-call and exception-handling extensions (Chrome 119, Node.js 22, Firefox 122, Safari 18.2 or newer) and a system Binaryen. OCaml 5 effects are slower with --effects=jspi and need CPS or stack switching on other engines.

## Maintenance

Actively developed inside ocsigen/js_of_ocaml (last commit 2026-10-09, release 6.4.1 on 2026-06-30) and usable by any OCaml project under LGPL-2.1 with the OCaml static-linking exception. The speed claim is preliminary and first-party, and the fiat-crypto entry in its current-bench suite times the compilers themselves (js_of_ocaml with --effects cps against wasm_of_ocaml defaults), not the generated code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only figure is a preliminary first-party '10-20% faster than js_of_ocaml' from the late-2023 ocaml-wasm forum update, seen via WebSearch snippets (discuss.ocaml.org, lwn.net and ocsigen.org do not resolve here); the repo's benchmarks/ harness exists but no published results with CPU, Node.js version or flags were seen, so C.
- **Verifier notes:** Real project (1.1k stars shared with js_of_ocaml, last commit 2026-10-09, binaryen 119+ requirement confirmed in README.md). The record's claim that report-wasm-cb.config uses js_of_ocaml as its reference was wrong and is corrected in workload. Shortcomings: snippet-only, preliminary 2023 figure, no methodology, modest gain.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-95 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ocsigen/js_of_ocaml>
  - <https://github.com/ocsigen/js_of_ocaml/commits/master>
  - <https://github.com/ocsigen/js_of_ocaml/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/README_wasm_of_ocaml.md>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/README.md>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/report-wasm-cb.config>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/report-jsoo-cb.config>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/run.config>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/dune-project>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/CHANGES.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/README.md>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/README_wasm_of_ocaml.md>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/dune-project>
  - <https://github.com/ocsigen/js_of_ocaml/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/run.config>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/run.ml>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/common.ml>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/report-wasm-cb.config>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/report-jsoo-cb.config>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/utils/aggregate.sh>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/benchmark-camlboy/Makefile>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/benchmark-partial-render-table/Makefile>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/benchmark-fiat-crypto/Makefile>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/benchmark-ocamlc/Makefile>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/benchmarks/benchmark-others/Makefile>
  - <https://github.com/ocsigen/js_of_ocaml/tree/master/manual>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/manual/performances.mld>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/manual/files/performances/time.png>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/manual/wasm_overview.mld>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/manual/wasm_runtime.mld>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/manual/browser-compat.mld>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/manual/runtime-representation.mld>
  - <https://github.com/ocsigen/js_of_ocaml/tree/master/compiler/lib-wasm>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/compiler/lib-wasm/binaryen.ml>
  - <https://raw.githubusercontent.com/ocsigen/js_of_ocaml/HEAD/compiler/lib-wasm/gc_target.ml>
  - <https://github.com/ocsigen/js_of_ocaml/issues?q=is%3Aissue+wasm+slow>
  - <https://github.com/ocsigen/js_of_ocaml/issues?q=is%3Aissue+label%3Awasm>
  - <https://raw.githubusercontent.com/ocaml-wasm/CAMLBOY/node/README.md>
  - <https://raw.githubusercontent.com/linoscope/CAMLBOY/HEAD/README.md>
  - <https://raw.githubusercontent.com/linoscope/CAMLBOY/HEAD/benchmark.md>
  - <https://github.com/linoscope/CAMLBOY/pull/15>
  - WebSearch snippets: discuss.ocaml.org/t/an-update-from-the-ocaml-wasm-organization/13114, discuss.ocaml.org/t/ann-js-of-ocaml-6-1-0-wasm-of-ocaml/16912, lwn.net/Articles/946287 (pages not opened; ocsigen.org did not resolve)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ocsigen/js_of_ocaml`) · [data/wave13/enrich/raw/github_com_ocsigen_js_of_ocaml.json](../../../data/wave13/enrich/raw/github_com_ocsigen_js_of_ocaml.json) (enrichment confidence 0.75)

</details>
