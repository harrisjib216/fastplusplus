# simdjson_nodejs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript (Node.js native addon binding to C++ simdjson)` · `Apache-2.0` · 🔴 abandoned

> Node.js N-API binding to C++ simdjson 0.9; lazyParse beats JSON.parse up to 2.3x by never building JS objects.

| | |
|---|---|
| **Beats** | V8 JSON.parse (Node.js built-in) |
| **Claimed result** | Page 'X faster' column (simdjson.lazyParse vs JSON.parse) ranges from 0.77x to 2.30x and is faster on 11 of 15 files. Examples: sf_citylots.json 1492.166 ms vs 709.692 ms = 2.10x (stated on page); numbers.json 2.30x. Slower on citm_catalog.json (0.93x), random.json (0.78x) and twitter.json (0.77x). About even on update_center (1.03x) and instruments (1.09x). |
| **Workload** | Parsing 15 standard JSON benchmark corpus files (apache_builds.json through update_center.json, including a 190MB sf_citylots.json) via a Node.js benchmark comparing JSON.parse against simdjson.lazyParse |
| **Metric** | throughput |
| **Hardware** | 2018 MacBook Pro, 2.3GHz Intel Core i9 |
| **Compiler and flags** | Not stated on the benchmark page; binding.gyp builds the addon in Release config with -O3 -std=c++17 (node-addon-api). Compiler and Node.js versions unstated. |
| **Adoption** | 620 stars; npm package "simdjson" (latest 0.9.2, \~45.9k downloads in the month ending 2026-09-21) |
| **Last commit** | 2023-02-23 |
| **Links** | [repository](https://github.com/luizperes/simdjson_nodejs) · [benchmark](https://github.com/luizperes/simdjson_nodejs#benchmarks) |

## Verdict

The first-party README table (Benchmark.js on a 2018 MacBook Pro, 2.3 GHz Core i9; Node/V8 and compiler versions not stated; addon built at -O3) times simdjson.lazyParse(str), which validates and builds a C++ tape with no JS objects, against JSON.parse(str), which builds the full object graph: 0.77x (twitter.json) to 2.30x (numbers.json), faster on 11 of 15 files, with 2.10x on the 190 MB sf_citylots.json. The results are noisy and fall short of the typings' claim: the same page's ops/sec block shows up to ±192.65% error on JSON.parse, an April 2020 run of the then-master by simdjson maintainer John Keiser (PR #36) had lazyParse slower on 6 of 15 files (mesh.json 0.56x), and the table's 0.20-0.87 GB/s for lazyParse is well below the '&gt; 2.5GB/s' in index.d.ts.

## Use it when

- Large JSON strings (MBs to hundreds of MB) where you read only a few fields with valueForKeyPath. The README shows 2.10x on the 190 MB sf_citylots.json (710 vs 1492 ms).
- Number-heavy or geometry documents such as canada.json, marine_ik.json, mesh.json and numbers.json, which the README shows at 1.9-2.3x JSON.parse.
- Validation-only gates, where isValid(str) is enough and no JS object is needed. In the maintainer's 2020 run in issue #28 (200k iterations of a 25 KB document), isValid took 5.7 s against JSON.parse's 33.5 s.
- An environment you can pin and that builds the addon: Linux x86-64 with a C++17 compiler and an older Node (CI only exercises Node 12.x).

## Skip it when

- You need the whole JS object. parse() and valueForKeyPath('') build it node by node through N-API: 1.7-4x slower than JSON.parse in issue #5's tables, and about 5x slower on a 25 KB document in issue #28.
- Many small documents, such as HTTP request bodies of a few KB. Every call copies the JS string to UTF-8, may copy it again into a padded buffer, and allocates a fresh dom::parser, since reusing the parser was never done (open issue #35). Issues #28 and #42 report lazyParse slower than JSON.parse in this pattern.
- String-heavy documents: on the README's own table lazyParse loses on twitter.json (0.77x), random.json (0.78x) and citm_catalog.json (0.93x).
- Windows, Apple Silicon or current Node. Open issues report MSVC build failures (#44, #52), 'illegal hardware instruction' with an x86_64 Node on an Apple M2 Pro (#70), and node-gyp 6.1.0 failing on Node 20 (#71). There are no prebuilt binaries, and the npm tarball unpacks to 39 MB because the benchmark corpus ships with it (#54).
- Production services that need a maintained dependency. Code has not changed since June 2021. A lazyParse memory-leak report (#40, confirmed by a second user in 2022) is still open. Bad key paths can abort the process (see gotchas).

## How it is fast

The vendored simdjson 0.9.x parses in two stages: a SIMD pass (AVX2, SSE4.2 or NEON, chosen at runtime) finds structural characters and validates UTF-8, then a second pass writes a compact 64-bit-word 'tape' of the document. lazyParse moves that parsed dom::document into a heap-allocated Napi::External and returns it with no per-value V8 allocation, while JSON.parse builds every object, array and string on the V8 heap. Most of the measured gain is that skipped object construction (issue #5): whenever this binding does build JS objects (parse(), or valueForKeyPath on a large subtree), it adds one property at a time through N-API and loses to JSON.parse.

## Compared with alternatives

No other Node.js JSON parser is catalogued, and the siblings are libraries for other languages. If you can write your own N-API addon, calling current simdjson (the C++ sibling, v4.x) directly avoids this binding's per-call parser allocation, its DOM-only interface (no On-Demand) and its 2021-era code; orjson and ssrJSON are the Python counterparts and, unlike this binding, return full native objects faster than their stdlib.

## Integration

| | |
|---|---|
| **Form** | module (npm package `simdjson`, an N-API native addon compiled from source by an install script running `node-gyp rebuild`; no prebuilt binaries) |
| **Dependencies** | node-addon-api ^2.0.0. Building needs node-gyp, Python and a C++17 compiler. simdjson is vendored as the amalgamated simdjson.h/simdjson.cpp (0.9.x; the header declares SIMDJSON_VERSION 0.9.1). |
| **Minimum toolchain** | A C++17 compiler (binding.gyp: -O3 -std=c++17, /std:c++17 on MSVC, C++ exceptions on) and a Node.js with N-API. There is no engines field. CI tests only Node 12.x on ubuntu-latest. |
| **Platforms** | The vendored simdjson picks a kernel at runtime: x86-64 Haswell (AVX2) or Westmere (SSE4.2), ARM64 (NEON), PPC64, or a portable fallback. The README claims macOS, Linux and Windows, but the Windows (#44, #52) and Apple Silicon (#70) build/run failures are open. The /EHsc workaround for MSVC was suggested in #52 but never merged. |
| **Thread safety** | Not documented. Calls are synchronous, and each one builds its own dom::parser on the stack, so the binding keeps no shared parser state. Use from worker_threads is not documented or tested. |
| **Drop-in for the baseline** | partial — parse(str) matches JSON.parse(str) without a reviver but is slower than it. The fast lazyParse returns an opaque handle that you read through valueForKeyPath key-path strings, so code has to change. |

## Gotchas

- Calling valueForKeyPath with a non-numeric segment where the document has an array (e.g. 'items.name' when items is an array) does not throw a catchable JS error. The binding queues a JS exception, keeps running, and calls std::stoi, whose std::invalid_argument is never caught, so the whole Node process aborts ('terminate called ... what(): stoi', issue #46, reproduced again in 2023).
- Key paths are split on '.', '[' and ']' with strtok, and there is no escaping. Keys that contain those characters, such as '@avito-core/toggles:6.1.18' in issue #68, cannot be reached. Every valueForKeyPath call also rebuilds the selected subtree as fresh JS objects, so reading a large subtree costs as much as parse().
- If build/Release/simdjson.node is missing (e.g. installed with --ignore-scripts), require('simdjson') silently returns the global JSON object with an isValid function added to it. The global JSON gets modified, and lazyParse is undefined.
- It is stricter than JSON.parse and handles input differently. Integers outside the int64/uint64 range fail with a number error (JSON.parse returns an imprecise double), and nesting is capped at 1024 levels. Only JS strings are accepted, so a Buffer must be decoded and is then re-encoded to UTF-8 on every call. Object keys are passed as C strings, so a key containing \u0000 is truncated (a source TODO says 'not 8-bit clean'), and the C++ document's memory is never reported to V8 (no AdjustExternalMemory), so the GC does not see it.

## Known shortcomings

- The benchmark compares lazyParse, which never builds JS objects, against JSON.parse; the full simdjson.parse is much slower (#5). Slower than JSON.parse on 3 of 15 files. Abandoned since 2023-02.
- An April 2020 run by a simdjson maintainer had lazyParse slower than JSON.parse on 6 of 15 files, and the README's JSON.parse figures carry up to +/-192% error. A bad key path aborts the Node process via an uncaught std::stoi exception (#46, open). Open lazyParse memory-leak report (#40); native memory is not reported to V8. If the native build is missing it silently patches the global JSON object. Vendors simdjson 0.9.x (upstream v4.6); open build failures on Windows, Apple Silicon with x86_64 Node, and Node 20.

## Caveats and trade-offs

The comparison is not like-for-like: lazyParse returns an external C++ parsed-document handle without building JS objects, while JSON.parse builds the full JS object graph. The README and issue #5 note that the eager simdjson.parse, which converts to JS objects, is much slower. Hardware is a 2018 laptop, with no compiler or Node version given. Not uniformly faster: slower on 3 of 15 corpus files. Unmaintained since Feb 2023 (&gt;3 years). Vendors an old simdjson.

Overhead of converting the parsed C++ object into JS objects can make eager parse() slower than native JSON.parse; only the lazy-parse API is competitive; results are mixed across workloads (3 of 15 files were net slower in the published table); Node.js/V8 version and native-addon compiler flags are not stated.

## Maintenance

Abandoned: code last changed on 2021-06-14 (npm 0.9.2, vendoring simdjson 0.9.x while upstream is at v4.6.11), later commits up to 2023-02-23 are dependabot merges only, and the fix PRs sit unmerged (#58 simdjson 2.2.2 was closed, #72 node-gyp is open), but it still gets about 46.8k npm downloads a month and is Apache-2.0 with about 150 lines of binding C++, so a fork onto current simdjson is practical.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table produced by public benchmark code (benchmark/benchmark.js, Benchmark.js suite of simdjson.lazyParse vs JSON.parse). The page gives no compiler or Node.js version, and the CPU is only '2018 MacBook Pro, 2.3GHz Intel Core i9' without a model, so not A. It is not third-party, so not B.
- **Verifier notes:** The numbers match the README table exactly, including the lower bound. The record left out that random.json (0.78x) was also slower. Metadata checked via gh: Apache-2.0, 620 stars, not archived or forked, last commit 2023-02-23, so 'abandoned' is correct. The main speed comes from wrapping C++ simdjson (a seed/known project), but this is a distinct binding project with its own benchmark.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/luizperes/simdjson_nodejs>
  - <https://github.com/luizperes/simdjson_nodejs#benchmarks>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/benchmark/benchmark.js>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/binding.gyp>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/package.json>
  - <https://github.com/luizperes/simdjson_nodejs/issues/5>
  - <https://registry.npmjs.org/simdjson>
  - <https://api.npmjs.org/downloads/point/last-month/simdjson>
- **Sources the enricher read:**
  - <https://github.com/luizperes/simdjson_nodejs>
  - <https://github.com/luizperes/simdjson_nodejs#benchmarks>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/README.md>
  - <https://github.com/luizperes/simdjson_nodejs/tree/master>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/binding.gyp>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/package.json>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/index.js>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/index.d.ts>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/lib/simdjsontarget.js>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/lib/moduleexists.js>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/simdjson/bindings.cpp>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/simdjson/bindings.h>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/simdjson/main.cpp>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/simdjson/src/simdjson.h>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/benchmark/benchmark.js>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/benchmark/is_valid.js>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/tests/simdjson.js>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/.github/workflows/tests.yml>
  - <https://github.com/luizperes/simdjson_nodejs/blob/master/.npmrc>
  - <https://github.com/luizperes/simdjson_nodejs/commits/master>
  - <https://github.com/luizperes/simdjson_nodejs/issues?q=is%3Aissue>
  - <https://github.com/luizperes/simdjson_nodejs/issues/5>
  - <https://github.com/luizperes/simdjson_nodejs/issues/13>
  - <https://github.com/luizperes/simdjson_nodejs/issues/28>
  - <https://github.com/luizperes/simdjson_nodejs/issues/34>
  - <https://github.com/luizperes/simdjson_nodejs/issues/35>
  - <https://github.com/luizperes/simdjson_nodejs/pull/36>
  - <https://github.com/luizperes/simdjson_nodejs/issues/40>
  - <https://github.com/luizperes/simdjson_nodejs/issues/42>
  - <https://github.com/luizperes/simdjson_nodejs/issues/44>
  - <https://github.com/luizperes/simdjson_nodejs/issues/46>
  - <https://github.com/luizperes/simdjson_nodejs/pull/47>
  - <https://github.com/luizperes/simdjson_nodejs/issues/49>
  - <https://github.com/luizperes/simdjson_nodejs/issues/52>
  - <https://github.com/luizperes/simdjson_nodejs/issues/54>
  - <https://github.com/luizperes/simdjson_nodejs/pull/55>
  - <https://github.com/luizperes/simdjson_nodejs/pull/58>
  - <https://github.com/luizperes/simdjson_nodejs/issues/59>
  - <https://github.com/luizperes/simdjson_nodejs/pull/60>
  - <https://github.com/luizperes/simdjson_nodejs/pull/61>
  - <https://github.com/luizperes/simdjson_nodejs/issues/67>
  - <https://github.com/luizperes/simdjson_nodejs/issues/68>
  - <https://github.com/luizperes/simdjson_nodejs/issues/69>
  - <https://github.com/luizperes/simdjson_nodejs/issues/70>
  - <https://github.com/luizperes/simdjson_nodejs/issues/71>
  - <https://github.com/luizperes/simdjson_nodejs/pull/72>
  - <https://github.com/luizperes/simdjson_nodejs/issues/73>
  - <https://registry.npmjs.org/simdjson>
  - <https://api.npmjs.org/downloads/point/last-month/simdjson>
  - <https://github.com/simdjson/simdjson/releases/latest>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/luizperes/simdjson_nodejs`) · [data/wave4/enrich/raw/github_com_luizperes_simdjson_nodejs.json](../../../data/wave4/enrich/raw/github_com_luizperes_simdjson_nodejs.json) (enrichment confidence 0.8)

</details>
