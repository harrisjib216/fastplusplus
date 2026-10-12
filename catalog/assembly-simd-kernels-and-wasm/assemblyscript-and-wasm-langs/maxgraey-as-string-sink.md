# as-string-sink

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript (TypeScript)` · `MIT` · 🟡 stale

> Growable UTF-16 string builder for AssemblyScript; replaces quadratic String += and beats V8 rope concat about 4x.

| | |
|---|---|
| **Beats** | JavaScript string concatenation (String += in V8, which uses ropes) and naive String += in AssemblyScript |
| **Claimed result** | 200,000 strings: JS String += 11.93 ms, AS String += 7622.72 ms, StringSink AS 2.88 ms (about 4.1x over JS, derived from page data; README prints \~2600x over AS +=); 50,000 strings: JS 3.34 ms, AS 509.54 ms, StringSink 0.73 ms (about 4.6x over JS, derived from page data); 100 strings: JS 0.013 ms, AS 0.014 ms, StringSink 0.0042 ms (README prints 3x). The README headline 'up to 6 times faster than JS concat' and 'up to 4000 times faster than naive concatenation' exceed every row of its own table. |
| **Workload** | Append n alternating 4-character literals ('foo\|', '\|boo') for n = 100, 50,000 and 200,000 and return the final length; one timed call per size with performance.now after 150 warm-up calls at n = 100 (benchmark/run.js, benchmark/index.ts) |
| **Metric** | latency |
| **Compiler and flags** | AssemblyScript asc (devDependency ^0.27.0) -O3 --noAssert (package.json build:bench); Node.js version not stated |
| **Adoption** | 29 stars |
| **Last commit** | 2023-02-17 |
| **Links** | [repository](https://github.com/MaxGraey/as-string-sink) · [benchmark](https://github.com/MaxGraey/as-string-sink#benchmark-results) |

## Verdict

First-party README table: appending alternating 4-character literals 200,000 times took 2.88 ms with StringSink in AssemblyScript (asc -O3 --noAssert) vs 11.93 ms for JavaScript String += in Node/V8 and 7,622.72 ms for AssemblyScript's naive String +=, about 4.1x and 2,650x (derived from page data); 50,000 strings gave 0.73 vs 3.34 vs 509.54 ms. Node.js version, CPU and OS are not stated and each figure is a single timed call.

## Use it when

- AssemblyScript code that builds a long string from many small pieces in a loop (serialisers, code or SVG generators, CSV/JSON writers) where += would go quadratic.
- Mixing text, numbers and code points into one output without allocating a temporary string per piece (writeNumber, writeCodePoint).
- Appending substrings by index range (write(src, start, end)) without materialising substring() copies.
- Output sizes from a few KB up to hundreds of MB, with a reusable sink (clear/reserve) across iterations to avoid regrowth.

## Skip it when

- Plain JavaScript or TypeScript projects: the npm package ships only AssemblyScript source, and the maintainer advises against driving it from JS (issue #14).
- When you already have all pieces in a string[]: the AssemblyScript stdlib's Array&lt;string&gt;.join (joinStringArray) sums the lengths and copies once, which is also linear and was not benchmarked against StringSink.
- UTF-8 output: the buffer is UTF-16 only; a UTF-8 writer is an open feature request (issue #6, open since 2021).
- Outputs above 2^29 bytes (256 Mi UTF-16 code units): power-of-two growth then requests a 2^30-byte block, which exceeds the runtime's OBJECT_MAXSIZE and aborts with an allocation-too-large error, even though a string of that size could otherwise fit.
- Memory-tight builds: capacity rounds up to a power of two and toString() copies, so peak memory can reach about 3x the final string until the sink is dropped or shrink() is called.

## How it is fast

Amortised geometric growth: each write memory.copy's the UTF-16 bytes at the current offset and, when capacity runs out, __renew grows the buffer to the next power of two, so n appends cost O(n) total bytes copied. AssemblyScript's own String += allocates a fresh string and copies both operands on every append, which is O(n^2) in total, so the gap against it grows with n rather than being a constant factor. writeNumber formats digits directly into the buffer instead of allocating a temporary string per number.

## Compared with alternatives

Pick it over as-str when the hot spot is accumulating output rather than individual String methods (as-str speeds up indexOf/split-style stdlib operations); json-as and as-proto are full serialisers, so use StringSink when you are writing your own text format in AssemblyScript.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond the AssemblyScript stdlib and runtime (util/number, __new/__renew) |
| **Minimum toolchain** | AssemblyScript asc 0.27 (package devDependency ^0.27.0; npm 0.5.3 published 2023-02-08); other asc versions not documented |
| **Platforms** | any WebAssembly host that runs AssemblyScript output (wasm32); tested in CI on ubuntu-latest with Node lts and latest |
| **Thread safety** | not documented (single-threaded Wasm instance; no atomics used) |
| **Drop-in for the baseline** | partial: replaces the += accumulation pattern inside AssemblyScript with write()/toString() calls; not usable from JavaScript, so not a replacement for V8's String += |

## Gotchas

- Benchmark harness (benchmark/run.js): each size is timed by a single performance.now() call after 150 warm-ups at n = 100 only, Wasm tier-up state is not controlled, and the three arms run in a fixed order with both Wasm arms sharing one instance, so StringSink always runs right after the AS += arm has grown linear memory and left garbage for the incremental GC; noise and order effects are unquantified. The JS arm returns res.length of an unflattened V8 rope while StringSink's toString() builds a flat copy.
- README headlines ('up to 4000x', 'up to 6x faster than JS concat') are larger than every row of its own table (best about 2,650x over AS += and about 4.6x over JS at 50,000 strings, derived from page data); the ratio against AS += is an O(n^2) vs O(n) gap, so it can be made any size by picking n.
- writeCodePoint only rejects code points above 0x10FFFF with assert(); in builds with --noAssert (the benchmark's own flag) invalid values silently produce garbage surrogate pairs.
- Building the package itself with asc 0.27.27 emits warning AS235 because a class cannot be a Wasm export (issue #15); import StringSink from other AssemblyScript files instead.

## Known shortcomings

- One timed call per size, no hardware stated; README headlines (6x over JS, 4000x) exceed its own table (4.6x, about 2600x derived); StringSink is about 3x faster at 100 strings too.
- Harness flaws: one performance.now() call per size with warm-up at n = 100 only and Wasm tier state uncontrolled; the arms run in a fixed order in one shared instance, so StringSink always follows AS += with memory already grown and GC garbage left behind; the JS rope is never flattened; there is no AS Array&lt;string&gt;.join baseline although the stdlib join is also linear. Power-of-two growth aborts with E_ALLOCATION_TOO_LARGE once content passes 2^29 bytes; writeCodePoint produces garbage for invalid code points under --noAssert. No library bug found.

## Caveats and trade-offs

Tiny first-party microbenchmark: no hardware, CPU model or Node.js version stated, and each figure is a single timed call (warm-up only at n = 100), so noise is unquantified. At 100 strings StringSink is about 3x faster than both plain concatenations (0.0042 vs 0.013 and 0.014 ms), but at that size all three are microseconds. The JS baseline returns res.length without flattening V8's rope while StringSink's toString() builds a flat string, which if anything favours JS. The headline 4000x is against AssemblyScript's own naive String +=, which copies the whole string on every append (quadratic), not against JS; the table's best is about 2,650x, and the 'up to 6x over JS' headline is not shown (best row about 4.6x, derived from page data).

Buffer-based string builder with its own write/toString API; only helps accumulation patterns.

## Maintenance

Stale since 2023-02-17 (npm 0.5.3, 29 stars, one open feature request), but it is one MIT-licensed 166-line file with an as-pect test suite, small enough to vendor (last known-good toolchain AssemblyScript 0.27); its benchmark is a single-call, fixed-order run with no Array.join baseline, so read the ratios as directional.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table produced by public code (benchmark/index.ts, benchmark/run.js; build flags -O3 --noAssert in package.json), but no hardware, CPU model or Node.js version is stated and each figure is a single timed call, so C.
- **Verifier notes:** Numbers in the record match the README; the benchmark source was opened this time and is a plain append loop with a single timed call per size. Shortcomings: no hardware or runtime stated, single-sample timing, README headlines (6x over JS, 4000x) larger than its own table (4.6x, \~2600x); repo stale since 2023-02-17.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-19 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/MaxGraey/as-string-sink>
  - <https://github.com/MaxGraey/as-string-sink/commits>
  - <https://github.com/MaxGraey/as-string-sink/tree/main/benchmark>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/README.md>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/benchmark/index.ts>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/benchmark/run.js>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/package.json>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/asconfig.json>
- **Sources the enricher read:**
  - <https://github.com/MaxGraey/as-string-sink>
  - <https://github.com/MaxGraey/as-string-sink/commits/main>
  - <https://github.com/MaxGraey/as-string-sink/issues?q=is%3Aissue>
  - <https://github.com/MaxGraey/as-string-sink/issues/3>
  - <https://github.com/MaxGraey/as-string-sink/issues/14>
  - <https://github.com/MaxGraey/as-string-sink/issues/15>
  - <https://github.com/MaxGraey/as-string-sink/tree/main/assembly/__tests__>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/README.md>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/package.json>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/asconfig.json>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/assembly/index.ts>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/assembly/__tests__/general.spec.ts>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/benchmark/index.ts>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/benchmark/run.js>
  - <https://raw.githubusercontent.com/MaxGraey/as-string-sink/HEAD/.github/workflows/test.yml>
  - <https://registry.npmjs.org/as-string-sink>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/main/std/assembly/rt/common.ts>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/main/std/assembly/rt/itcms.ts>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/main/std/assembly/util/number.ts>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/main/std/assembly/util/string.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/maxgraey/as-string-sink`) · [data/wave13/enrich/raw/github_com_maxgraey_as_string_sink.json](../../../data/wave13/enrich/raw/github_com_maxgraey_as_string_sink.json) (enrichment confidence 0.75)

</details>
