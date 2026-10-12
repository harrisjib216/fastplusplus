# simdjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 OR MIT` · 🟢 active

> SIMD-accelerated JSON parser with full UTF-8 validation; \~4x faster than RapidJSON, \~25x than nlohmann.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | README text: "parse JSON 4x faster than RapidJSON and 25x faster than JSON for Modern C++" and "uses three-quarters less instructions than state-of-the-art parser RapidJSON". NDJSON: "3.5 GB/s" (feature bullet) and "we can exceed 3 GB/s" with multithreaded parse_many. Paper Table 10 (Skylake i7-6700), twitter.json: simdjson 2.2 GB/s vs RapidJSON 0.45 GB/s (\~4.9x, derived from page data), vs RapidJSON insitu 0.72 GB/s (\~3.1x, derived from page data), vs JSON for Modern C++ 0.10 GB/s (\~22x, derived from page data). |
| **Workload** | README chart (doc/rome.png): single-core throughput in GB/s on load-and-process tasks (partial tweets, kostya, distinct user id, top tweet) against yyjson, RapidJSON and JSON for Modern C++ (code in benchmark/). VLDB Journal 2019 paper, Table 10: full-validating parse of 14 real-world files (twitter.json, canada, citm_catalog, gsoc-2018, ...) against RapidJSON, sajson, nlohmann and others. The README's synthetic file-size scaling chart (doc/growing.png, up to \~3.5 MB) plots simdjson alone, with no baseline. |
| **Metric** | throughput |
| **Hardware** | README: 'Intel Skylake processor (3.4 GHz)', model not named. VLDB 2019 paper: Intel i7-6700 (Skylake, 3.4 GHz base / 3.7 GHz turbo, DDR4-2133) and Intel i3-8121U (Cannon Lake, 2.2 GHz). |
| **Compiler and flags** | README chart: GNU GCC 10 with -O3; file-size chart: GNU GCC 9 with -O3. VLDB 2019 paper: GNU GCC 9.1 with -O3 -march=native. |
| **Adoption** | 24.3k stars; used in Node.js, ClickHouse, Meta Velox, Apache Doris, Milvus, StarRocks, WatermelonDB, Ladybird Browser |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/simdjson/simdjson) · [benchmark](https://github.com/simdjson/simdjson#performance-results) |

## Verdict

On GCC 10 -O3 on an unnamed 3.4 GHz Skylake chip, the README's rome.png chart (code in benchmark/) shows simdjson at roughly 2.2-3.2 GB/s against RapidJSON at roughly 0.4-0.5 GB/s. The peer-reviewed VLDB Journal 2019 paper pins the same comparison down with named hardware: on an Intel i7-6700 (Skylake) with GCC 9.1 -O3 -march=native, Table 10 shows simdjson parsing twitter.json at 2.2 GB/s vs RapidJSON at 0.45 GB/s (\~4.9x) and RapidJSON insitu at 0.72 GB/s (\~3.1x).

## Use it when

- Large or numerous real-world JSON payloads (twitter.json-scale and up) where RapidJSON/nlohmann parsing throughput is the bottleneck
- Single-pass extraction of a known set of fields, read in roughly document order (log/event pipelines, API response parsing)
- x86-64 (SSE4.2+) or aarch64 targets where a runtime-CPU-dispatching binary is acceptable
- NDJSON or streamed multi-document workloads via parse_many/iterate_many, optionally multithreaded
- Need strict RFC 8259 + full UTF-8 validation with no correctness shortcuts

## Skip it when

- Random, out-of-order, or repeated access to the same keys with On-Demand — raises OUT_OF_ORDER_ITERATION or falls back to a much slower path (Glaze's independent ABC test measured On-Demand at 89 MB/s vs 1163 MB/s in-order)
- You need a true drop-in replacement for RapidJSON's API — the iterator/On-Demand or DOM interface differs and calling code must change
- Non-standard or very old embedded targets without a &gt;=4KB page size or a supported compiler (GCC 7.4+/Clang 6+/VS2017+)
- Float-heavy documents (e.g. GeoJSON) — decimal-to-binary float conversion caps throughput at a few hundred MB/s regardless of SIMD
- Chips below SSE4.2/NEON/VSX — falls back to the generic kernel and loses most of the speedup

## How it is fast

Uses SIMD vector instructions to find structural characters, string boundaries, and numbers in bulk rather than byte-by-byte, splitting parsing into index-building and interpretation stages. The On-Demand front-end skips materializing a full DOM/tape, lazily interpreting bytes only as the caller touches them so unused fields/subtrees cost nothing. A runtime CPU-dispatch layer selects among icelake (AVX-512), haswell (AVX2), westmere (SSE4.2), arm64 (NEON), ppc64 (VSX/AltiVec), lsx/lasx (LoongArch), or a generic 64-bit fallback kernel, so one compiled binary runs optimally across chips.

## Compared with alternatives

Pick simdjson over yyjson when you need the widest CPU/platform dispatch matrix (AVX-512 down through ARM/PPC/LoongArch) or the lazy On-Demand API for single-pass field extraction; yyjson's simpler in-situ DOM is easier to reason about and still beats RapidJSON by roughly 2x with less API surface. Pick simdjson over glaze when you can't build a static C++ struct/reflection schema for glaze to compile against, or don't want On-Demand's key-order sensitivity — glaze generates a schema-specific path and isn't subject to the same out-of-order penalty.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the core library at runtime (bundles Dragonbox for float serialization and a Boost-licensed string_view shim for pre-C++17 compilers); the benchmark suite alone depends on RapidJSON/nlohmann/sajson/yyjson/etc. |
| **Minimum toolchain** | C++11 minimum (GNU GCC 7.4+, LLVM Clang 6+, Xcode 11+, Visual Studio 2017+); C++17 unlocks padded_input convenience; C++20 unlocks u8string_view/ranges; C++26 unlocks reflection-based (de)serialization |
| **Platforms** | x86-64 (SSE4.2 'westmere' floor, AVX2 'haswell', AVX-512-VBMI2 'icelake' auto-selected at runtime), aarch64 (NEON), ppc64 (VSX/AltiVec, tested little-endian), LoongArch (LSX/LASX), plus a generic 64-bit fallback; also tested on big-endian s390x |
| **Thread safety** | Single-threaded except parse_many/iterate_many, which may use secondary threads when built with thread support. One parser instance per thread is recommended; the On-Demand `document` is an iterator and is not thread-safe. Runtime CPU-detection dispatch itself is thread-safe, but relies on globals set up at process start, so using the library from background threads during main-thread teardown can be unsafe. |
| **Drop-in for the baseline** | partial — explain: same problem domain (parse JSON to accessible values) but a different API shape (lazy On-Demand iterator, or a separate DOM tree type) than RapidJSON's SAX/DOM interface, so call sites need rewriting |

## Gotchas

- On-Demand documents must generally be walked forward, once, in roughly key order; re-reading a field or skipping around triggers OUT_OF_ORDER_ITERATION or a slow path
- Input must be a padded buffer (SIMDJSON_PADDING extra bytes); raw pointers/spans without padding aren't accepted directly (padded_string::load, the _padded literal, or padded_string_view handle this)
- Exceptions are thrown by default on parse errors; the no-exception API/build path must be opted into explicitly
- Debug builds can need hundreds of KB of stack; the README recommends turning on optimization or increasing stack size in threaded/limited-stack environments

## Caveats and trade-offs

The legend of the README chart (doc/rome.png) names RapidJSON and 'JSON for M. C++' (nlohmann) along with yyjson, so both headline baselines are in the plotted comparison. Exact bar values are not printed; read visually, they put simdjson at about 2.2-3.2 GB/s against RapidJSON at about 0.4-0.5 GB/s. The README's CPU is given only as 'Skylake 3.4 GHz'; the exact model (i7-6700) comes from the VLDB 2019 paper, whose runs used GCC 9.1 rather than the README chart's GCC 10. The file-size scaling chart has no baseline. The reproducible-experiments repo simdjson/simdjson_experiments_vldb2019 is public but archived. GitHub reports Apache-2.0, but the README says the code is also available under MIT (LICENSE-MIT) at the user's choice.

The On-Demand API can drop to a fraction of its peak throughput when JSON keys arrive out of the schema's expected order or objects have variable shape (documented independently by Glaze's ABC test, which measured simdjson On-Demand at 89 MB/s vs 1163 MB/s in-order); requires padded input buffers; DOM API trades some flexibility for predictable random access.

## Maintenance

Actively maintained (last commit 2026-09-23, 24.3k stars, used in Node.js, ClickHouse, Meta Velox, Apache Doris, Milvus, StarRocks and others); dual Apache-2.0/MIT licensed and small enough to vendor as a two-file source drop.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The README gives the 4x RapidJSON / 25x nlohmann claims, and its GCC 10 -O3 chart (doc/rome.png) plots simdjson against yyjson, RapidJSON and JSON for Modern C++, with the code in simdjson/benchmark/ (e.g. partial_tweets/rapidjson.h). The linked peer-reviewed VLDB Journal 2019 paper (arXiv 1902.08318) names the CPU as an Intel i7-6700 and the build as GCC 9.1 -O3 -march=native, and its public artifact repo (simdjson/simdjson_experiments_vldb2019, experiments/comparison) supplies the code, so code, compiler, flags and CPU model are all stated.
- **Verifier notes:** The headline and README numbers check out. The paper's Table 10 backs up the \~4x RapidJSON claim (twitter.json 2.2 vs 0.45 GB/s). Metadata checks out: 24,272 stars, last commit 2026-09-23, not a fork, not archived. The license is dual Apache-2.0 OR MIT, and benchmark_url was kept as the README.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `license`, `caveats`
- **Shortcomings recorded by:** Parsing 20k records (2.88 MB, nested 3 deep, escaped strings) and extracting 9 fields each, simdjson On Demand with a reused parser took 113.546 ns/record (1268 MB/s) vs 191.56 ns for yyjson (1.69x). On a 13.86 MB selection corpus it ran at 1445 MB/s vs Glaze 787, yyjson 643 and RapidJSON 248 (5.8x RapidJSON). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party); Building simdjson.cpp with -march=native on an AVX-512 host compiled only the icelake kernel (vs icelake, haswell, westmere and fallback with no arch flag), which gives a binary that dies with SIGILL on AVX2-only CPUs. The active kernel was icelake in all three builds, so the portable build cost nothing measurable, and the vendored source is 10.5 MB vs yyjson's 733 KB. (developer source, private repo; gcc 13.3.0, AVX-512 Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/simdjson/simdjson>
  - <https://github.com/simdjson/simdjson#performance-results>
  - <https://github.com/simdjson/simdjson/blob/master/doc/rome.png>
  - <https://github.com/simdjson/simdjson/blob/master/doc/growing.png>
  - <https://github.com/simdjson/simdjson/tree/master/benchmark>
  - <https://github.com/simdjson/simdjson/tree/master/benchmark/partial_tweets>
  - <https://github.com/simdjson/simdjson_experiments_vldb2019>
  - <https://arxiv.org/pdf/1902.08318>
- **Sources the enricher read:**
  - <https://github.com/simdjson/simdjson>
  - <https://github.com/simdjson/simdjson#performance-results>
  - <https://github.com/simdjson/simdjson/blob/master/doc/basics.md>
  - <https://github.com/simdjson/simdjson/blob/master/doc/implementation-selection.md>
  - <https://github.com/simdjson/simdjson/blob/master/doc/performance.md>
  - <https://github.com/simdjson/simdjson/tree/master>
  - <https://github.com/simdjson/simdjson/issues?q=out+of+order>
  - <https://github.com/simdjson/simdjson/issues?q=CVE>
  - <https://github.com/simdjson/simdjson/issues?q=not+recommended>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/simdjson/simdjson`) · [data/wave0-seed/enrich/raw/github_com_simdjson_simdjson.json](../../../data/wave0-seed/enrich/raw/github_com_simdjson_simdjson.json) (enrichment confidence 0.85)

</details>
