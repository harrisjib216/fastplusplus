# watr

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT` · 🟢 active

> Zero-dependency pure-JavaScript WAT-to-Wasm compiler; about 3.6x wabt.js and 6.6x binaryen.js on one small module, in-process.

| | |
|---|---|
| **Beats** | wabt (wat2wasm) and Binaryen (parseText plus emitBinary) |
| **Claimed result** | README metrics: watr 3,123 op/s versus wabt 859 op/s (about 3.6x, derived from page data), Binaryen 473 op/s (about 6.6x), the WebAssembly spec wast.js 1,509 op/s and wat-compiler 355 op/s. Optimizer table (wasm-opt 128, 21 modules in test/example): watr/optimize about 110 ms in-process for the batch versus wasm-opt -Oz 990 ms as a CLI run (about 9x, but includes process spawn), with total output 19,734 B against 19,852 B for -Oz and 22,302 B for -O3. |
| **Workload** | Compiling test/example/brownian.wat to a Wasm binary 500 times in a loop, in-process (JavaScript builds of each compiler); a second table compares watr's optimizer to wasm-opt over the 21 modules in test/example. |
| **Metric** | throughput |
| **Adoption** | 74 stars; used by jz |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/dy/watr) · [benchmark](https://github.com/dy/watr/blob/main/readme.md) |

## Verdict

In a browser-run loop of 500 compiles of one 6.5 KB WAT file, watr reached 3,123 op/s versus 859 op/s for wabt.js (with its binary-writer log enabled), 473 op/s for binaryen.js parseText plus emitBinary, 1,509 op/s for the spec interpreter's wast.js and 355 op/s for wat-compiler; first-party, no CPU, browser or engine version, no warmup and no output-equality check.

## Use it when

- Generating WAT at runtime in a browser or Node (DSLs, JIT-style codegen, teaching tools, playgrounds) and compiling it in-process many times per second.
- Small to medium modules (the benchmark input is a 200-line, 6.5 KB file) where per-call overhead of loading wabt.js or binaryen.js dominates.
- Bundle-size-sensitive front ends: 44 KB minified (14 KB gzipped) versus 282 KB for wabt.js and 1,100 KB for binaryen.js per the README.
- Size-oriented optimization of hand-written or generated WAT inside a JS build step without spawning wasm-opt (README: 19,734 B total versus 19,852 B for wasm-opt -Oz on its 21 example modules).
- Targeting older engines: watr/polyfill lowers newer proposals to MVP before compiling.

## Skip it when

- When you need a validator: watr does not type-check bodies, so invalid WAT can compile to an invalid binary that only fails at WebAssembly.Module time.
- Large modules or heavy optimization: the README says Binaryen's native core is faster on a 5.5 MB module (0.44 s versus about 2.6 s optimize plus 0.19 s compile).
- Native toolchains and build systems that already call wabt's wat2wasm or wasm-opt as native binaries; the comparison is against their JavaScript/Wasm builds, not the native CLIs.
- When you need the rest of a toolkit (wasm2wat, objdump, interpreter, wasm2c): watr only goes text to binary.
- Production use of watr/optimize without your own tests: the optimizer received several correctness fixes in late September and early October 2026.

## How it is fast

A single-pass charCodeAt tokenizer turns the text into nested arrays of source slices, and a direct encoder walks that tree to bytes, all in plain JavaScript (about 44 KB minified); a compile call has no Wasm module instantiation, no copying of source text into a Wasm heap and no IR construction, unlike the Emscripten builds of wabt and Binaryen it is compared with. The code section is written into a growable Uint8Array byte buffer rather than a JS array of numbers, and the cleanup pass copies an AST node only where it changes. It does not type-check function bodies, which also skips work a validating toolchain does.

## Compared with alternatives

No sibling is a WAT text compiler; wasm2c (WABT) belongs to the same toolkit as the wabt baseline, so pick WABT when you want a native, validating toolchain and pick watr when you must compile WAT inside a JavaScript process with a small bundle. jz (same author) uses watr as its backend, so jz users get it implicitly.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | not documented (ES-module JavaScript, no engines field in package.json; tests run on Node with --experimental-wasm-exnref and in a browser) |
| **Platforms** | any JavaScript engine with ES modules (Node, browsers); a jz-compiled dist/watr.wasm build is also shipped |
| **Thread safety** | not documented; single-threaded JS, and compile.js keeps module-level error-location state, so use one instance per worker (each worker loads its own copy) |
| **Drop-in for the baseline** | partial: replaces wabt's wat2wasm (text to binary) and Binaryen parseText plus emitBinary for that job, with a different API and without validation or the other wabt/Binaryen tools |

## Gotchas

- Harness flaw: test/bench.js times one tiny input (test/example/brownian.wat, 200 lines, 6.5 KB) 500 times with no warmup, in a fixed order, with no check that the five outputs are equal; it fetches a relative path, so it runs only in the browser test page, and test/index.js has the bench import commented out, so the README op/s figures come from a manual run with no CPU, browser or engine version stated.
- Harness flaw: the wabt arm (test/util.js wat2wasm) calls toBinary with log: true, so wabt also builds a text log of the binary writer on every iteration, and enables 18 feature flags; this likely handicaps the baseline by an unmeasured amount. On a 6.5 KB input the fixed per-call cost of the Wasm builds (copying text into the Wasm heap, Module dispose) probably weighs heavily too.
- No validation: the spec testsuite's assert_invalid cases pass because the harness hands watr's output to V8's WebAssembly.Module; test/util.js also skips whole classes of assert_invalid (constant-expression rules, offset range, 64-bit alignment, tag result types, custom annotation placement).
- The optimizer comparison (about 110 ms in-process versus 990 ms for wasm-opt as a CLI) has no committed script and includes process spawn on the wasm-opt side; the size numbers predate several optimizer correctness fixes committed 2026-09-29 to 2026-10-01.

## Known shortcomings

- The wabt baseline runs with toBinary({log: true}) in test/util.js, likely inflating wabt's time; no CPU or browser named, one input, no warm-up, and the optimizer comparison is in-process against a spawned CLI. JavaScript wat compiler, not a runtime.
- Enricher: test/bench.js times one 6.5 KB file 500 times in a browser with no warm-up and no output-equality check, and the bench import is commented out of test/index.js so the README ops/s come from a manual run; watr does no type validation of its own (spec assert_invalid passes only because V8's WebAssembly.Module rejects the binary, and util.js skips several assert_invalid classes); the optimizer-versus-wasm-opt table has no committed script and the optimizer received correctness fixes between 2026-09-29 and 10-01.

## Caveats and trade-offs

Benchmark code is public (test/bench.js, browser-run, single brownian.wat input, N=500, no warmup, no check that outputs match) but the README gives no CPU, browser or Node version. wabt and Binaryen are measured as their JavaScript/Wasm builds, not as native CLIs. The wabt path (test/util.js wat2wasm) calls toBinary with log: true, which makes wabt build a binary-writer log on every iteration; that probably inflates wabt's time, though by how much was not measured. For a 5.5 MB module the README itself says Binaryen's native core is faster (0.44 s versus about 2.6 s optimize plus 0.19 s compile). The 110 ms versus 990 ms optimizer comparison pits an in-process call against a spawned CLI. The LICENSE is MIT and is also offered under the Krishnized License.

Pure-JavaScript, zero-dependency WAT compiler (about 44 KB minified) that also polyfills, minifies and optimizes; no native core, so large modules are slower than Binaryen.

## Maintenance

Very actively maintained (v5.11.9, commits through 2026-10-01, one open issue) and MIT-licensed (also offered under the Krishnized License), zero-dependency and easy to vendor, but the speed numbers are a single first-party browser run on one small input with a handicapped wabt arm.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Metrics section gives first-party op/s numbers against wabt and Binaryen, produced by public code (test/bench.js), but names no CPU, browser or Node version, so it is C.
- **Verifier notes:** README numbers and bench code match the record. New shortcoming: the wabt baseline runs with toBinary({log: true}) in test/util.js, a likely handicap to the baseline. Other flaws: no hardware or runtime stated, one input file, no warmup. Metadata is correct: 74 stars, MIT, last commit 2026-10-01.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dy/watr>
  - <https://github.com/dy/watr/commits/main>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/readme.md>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/bench.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/util.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/package.json>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/dy/watr>
  - <https://github.com/dy/watr/commits/main>
  - <https://github.com/dy/watr/issues?q=is%3Aissue>
  - <https://github.com/dy/watr/tree/main/test>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/readme.md>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/docs.md>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/package.json>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/watr.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/src/compile.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/src/parse.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/src/optimize.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/bench.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/util.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/testsuite.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/optimize.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/index.js>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/index.html>
  - <https://raw.githubusercontent.com/dy/watr/HEAD/test/example/brownian.wat>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dy/watr`) · [data/wave12/enrich/raw/github_com_dy_watr.json](../../../data/wave12/enrich/raw/github_com_dy_watr.json) (enrichment confidence 0.6)

</details>
