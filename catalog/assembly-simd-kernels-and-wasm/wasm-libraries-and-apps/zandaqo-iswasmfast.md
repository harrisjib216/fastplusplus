# iswasmfast

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ compiled to WebAssembly and to an N-API addon, JavaScript harness` · `MIT` · 🔴 abandoned

> Node.js demo that times five toy kernels as plain JS, a C++ N-API addon and C++ compiled to WebAssembly; WASM wins 2 of 5.

| | |
|---|---|
| **Beats** | Pure JavaScript implementation (labelled 'Native' in the README) and the same C++ code built as a Node.js N-API addon |
| **Claimed result** | Fibonacci: WebAssembly 11,508,910 ops/s vs N-API addon 5,204,691 and JS 4,044,156 (2.8x JS, derived from page data). SHA256: addon 67,807, WebAssembly 34,445, JS 13,453 (WebAssembly 2.6x JS, derived). The Fermat row (WebAssembly 2,402,964 vs addon 1,833,692 and JS 1,678,845) is struck: the C++ kernel overflows and returns wrong answers for n &gt; 46,341. WebAssembly loses on Levenshtein (210,776 vs addon 308,924 and JS 295,433) and on simple linear regression (37,117 and 42,521 vs JS 291,985). |
| **Workload** | Levenshtein distance, Fibonacci, Fermat primality test, simple linear regression and SHA256 in Node.js, benchmark.js ops/sec. |
| **Metric** | throughput |
| **Compiler and flags** | WASM: emcc --bind -std=c++14 src/wasm.cpp -s WASM=1 -s SINGLE_FILE=1 -O3 (package.json build:wasm; Emscripten version not stated). Addon: node-gyp rebuild --release with default node-gyp Release flags (binding.gyp sets no extra flags). Node version not stated. |
| **Adoption** | 196 stars |
| **Last commit** | 2022-04-09 |
| **Links** | [repository](https://github.com/zandaqo/iswasmfast) · [benchmark](https://github.com/zandaqo/iswasmfast) |

## Verdict

First-party benchmark.js output in the README, with unknown CPU, Node and Emscripten versions and +-8-15% error bars. Against the pure-JS versions, WASM ran Fibonacci 2.85x, Fermat 1.43x (inflated by the C++ overflow bug above) and SHA-256 2.56x faster, the last against an unoptimised reference JS implementation. It ran Levenshtein at 0.71x and linear regression at 0.13-0.15x. The N-API addon beat WASM on SHA-256 (67,807 vs 34,445 ops/s) and Levenshtein. All ratios are derived from page data.

## Use it when

- As a teaching example of the three ways to call C++ from Node.js (pure JS, N-API addon through node-addon-api, Emscripten/Embind WASM), with matching build scripts in package.json.
- To show that per-call overhead decides small-kernel results: WASM ran 11.5 M vs 4.0 M ops/s on Fibonacci (2.85x over JS, 2.21x over the addon; derived from page data).
- As a starting harness to re-measure on your own Node and Emscripten versions before deciding whether to move a hot scalar function to WASM.

## Skip it when

- Production hashing. The SHA-256 rows compare a C++ port against Chris Veness's JavaScript reference implementation, which its own header calls 'without any optimisations' and not meant for production. It recommends Node's built-in crypto module, which is not measured here. Use node:crypto, or the sibling hash-wasm (426 MB/s SHA-256).
- Array-heavy work across the JS/WASM boundary. Regression on 1,000-point arrays ran 37,117-42,521 ops/s in WASM against 291,985 for plain JS, roughly 7x slower.
- Any decision that needs current numbers. The results come with no CPU, Node.js or Emscripten version, carry +-8-15% error bars, and were produced years ago: release 0.0.13 dates from 2019-05-06, and the last commit (2022-04-09) only bumped a dependency.
- Reuse of the C++ kernels. The Fermat code overflows a signed 32-bit int (see gotchas), regression() takes its vectors by value, and isPrime uses the global rand().

## How it is fast

Nothing is specially optimised; the results show where each route pays. WASM wins on scalar kernels with tiny arguments and no data marshalling. Fibonacci is a tail-recursive C++ function that the compiler turns into a loop, while V8 recurses up to 45 levels without tail calls. Fermat is a short modular-exponentiation loop. WASM loses wherever data crosses the boundary. Embind copies each JS string, and vecFromArray copies each 1,000-element array into linear memory through a Float64Array view; the N-API addon converts plain Arrays element by element.

## Compared with alternatives

Pick it only to learn how JS, N-API and WASM compare on toy kernels. BenchmarkingWebAssembly is a systematic study of WASM against JavaScript compiled from the same C programs, hash-wasm is a production-grade WASM SHA-256 that beats pure-JS libraries, and zaw shows how to cut the marshalling cost that sinks the regression row here.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | node-addon-api ^4.0.0 and node-gyp for the addon. The Emscripten SDK is needed only to rebuild src/wasm.js. benchmark and jest are dev dependencies. |
| **Minimum toolchain** | Node.js 8.6+ (package.json engines); C++14 (emcc -std=c++14); the Emscripten version is not stated |
| **Platforms** | The WASM build runs on any Node.js. The N-API addon needs a native C++ compiler for each host platform. |
| **Thread safety** | Not documented. The C++ Fermat kernel calls the global rand(). |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness bug behind the Fermat row. lib/fermat.cpp computes (res \* a) % p and (a \* a) % p in 32-bit int, but benchmark.js draws n up to 1,000,000, so products of residues reach about 10^12 and overflow for any n above 46,341 (about 95% of inputs). lib/fermat.js computes in exact doubles. A wrap-around simulation of the C++ power() reported 2,923 of 2,934 sampled primes above 46,341 as composite on the first witness. The addon and WASM therefore return wrong answers for nearly every large prime and skip the other two witnesses that JS runs. That is roughly 15% fewer power() calls overall, which inflates the 1.43x WASM-over-JS Fermat ratio. The jest tests check only 2, 7, 100, 561 and 1e6, so the bug goes unnoticed.
- Harness: randomInRange(max, min) computes floor(random \* (max + 1)) and ignores min, so Fibonacci n is drawn from 0-45 instead of 30-45. Every timed call also includes Math.random and array indexing. Both apply equally to all three implementations, but they shrink and add noise to the ratios.
- The C++ Levenshtein kernel calls std::array&lt;unsigned,50&gt;::swap after every row, so it swaps 50 elements on rows that compute at most 40 (often about 20) DP cells. The JS version only swaps two references. This extra work, plus Embind's string copies, probably explains part of WASM's loss on Levenshtein (210,776 vs 295,433 ops/s for JS). This is a reading of the code, not a measurement.
- README's 'Native' means the pure-JavaScript version, not native code. Several rows (Levenshtein JS 295,433 vs addon 308,924) lie within the +-9% error bars.

## Known shortcomings

- Numbers match but there is no CPU, Node or Emscripten version and 8-15% noise; WASM is fastest on 2 of 5 kernels and beats JS on 3 of 5; the Fibonacci row measures tail-call elimination; randomInRange ignores min; demo repo abandoned 2022-04-09.
- Correctness bug behind the Fermat row: lib/fermat.cpp computes (res\*a)%p in 32-bit int, which overflows for n &gt; 46,341 (about 95% of the benchmark's inputs); a wrap simulation misreported 2,923 of 2,934 large primes as composite, so the C++ addon and WASM return wrong answers with about 15% fewer power() calls, inflating the 1.43x row. Jest tests miss it. The SHA256 JS baseline is an unoptimised reference implementation (its own header says so; node:crypto not measured) and the C++ Levenshtein swaps a 50-element std::array every row.

## Caveats and trade-offs

Toy kernels with +-8-15% reported variance; no CPU, Node version or Emscripten version stated, and the README labels the pure-JS version 'Native'. WebAssembly is fastest on only 2 of 5 tasks (Fibonacci, Fermat); it beats pure JS on 3 of 5 (also SHA256, 34,445 vs 13,453 ops/s, about 2.6x derived from page data) but loses to JS on Levenshtein and linear regression and to the N-API addon on Levenshtein, regression and SHA256. The Fibonacci kernel is tail-recursive, which the C++ compiler turns into a loop while JS has no tail calls, so that row mostly measures tail-call elimination. benchmark.js draws random inputs on every call and its randomInRange helper ignores its min argument (Fibonacci n ranges 0-45, not 30-45); inputs are identically distributed for all three implementations. A benchmark/demo repository rather than a reusable library; last release 0.0.13 (2019-05-06), last commit 2022-04-09. The linked Medium post was not opened (blocked). [retier] Toy kernels with 8-15% reported variance; no CPU, Node version or Emscripten version stated, and the README labels the pure-JS version 'Native'. Correctness bug: lib/fermat.cpp computes (res\*a)%p and (a\*a)%p in 32-bit int while benchmark.js draws n up to 1,000,000, so products overflow for any n above 46,341 (about 95% of inputs); a wrap simulation misreported 2,923 of 2,934 sampled large primes as composite, and the wrong path does about 15% fewer power() calls, so the C++ addon and WASM Fermat rows timed incorrect, cheaper work (Jest tests miss it). The SHA256 JS baseline is an unoptimised reference implementation by its own header (node:crypto not measured); the C++ Levenshtein swaps a 50-element std::array every row. WebAssembly beats pure JS on Fibonacci and SHA256 only; it loses to JS on Levenshtein and linear regression and to the N-API addon on three of five tasks.

Mixed result by design: WASM beats the same C++ built as an addon when per-call overhead dominates (Fibonacci, Fermat) but loses where data is copied across the boundary (regression, Levenshtein).

## Maintenance

Abandoned: release 0.0.13 dates from 2019-05-06, and the last commit (2022-04-09) is a dependabot minimist bump. It is MIT-licensed (196 stars, 12 forks) and small, but it is a demo whose C++ Fermat kernel is incorrect for n &gt; 46,341, so treat it as an illustration rather than code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark.js (benchmark.js library) output pasted in the README; the harness and the emcc flags are public (package.json build:wasm: emcc --bind -std=c++14 -O3), but no CPU, Node version or Emscripten version is given, and the runs show +-8-15% variance.
- **Verifier notes:** README numbers match the record exactly. Shortcomings to record: no CPU, Node or Emscripten version; noisy toy kernels; WASM loses to plain JS on 2 of 5 and to the native addon on 3 of 5; Fibonacci row measures tail-call elimination; randomInRange min bug; benchmark repo, not a library; abandoned (last commit 2022-04-09). Metadata confirmed: MIT (LICENSE.md), 196 stars, 12 forks, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-22 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/zandaqo/iswasmfast>
  - <https://github.com/zandaqo/iswasmfast/commits/master>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/README.md>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/package.json>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/binding.gyp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/index.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/src/wasm.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/src/native.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/fibonacci.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/fibonacci.js>
- **Sources the enricher read:**
  - <https://github.com/zandaqo/iswasmfast>
  - <https://github.com/zandaqo/iswasmfast/commits/master>
  - <https://github.com/zandaqo/iswasmfast/tree/master/test>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/README.md>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/package.json>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/binding.gyp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/index.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/src/wasm.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/src/node.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/src/native.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/fibonacci.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/fibonacci.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/fermat.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/fermat.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/levenstein.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/levenstein.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/regression.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/regression.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/sha256.cpp>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/lib/sha256.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/test/fermat.js>
  - <https://raw.githubusercontent.com/zandaqo/iswasmfast/HEAD/test/index.spec.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/zandaqo/iswasmfast`) · [data/wave13/enrich/raw/github_com_zandaqo_iswasmfast.json](../../../data/wave13/enrich/raw/github_com_zandaqo_iswasmfast.json) (enrichment confidence 0.6)

</details>
