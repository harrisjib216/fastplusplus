# cpp-yyjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 JSON DOM library: header-only API over a bundled SIMD-patched yyjson fork; reads 1.4-4.6x, writes 2.6-8.1x faster than RapidJSON.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | vs RapidJSON: 1.4-4.6x faster reads, 2.6-8.1x faster writes across the ten documents (per-document ranges from the root README table); time-weighted totals: 2.31x faster reads, 3.91x faster writes (docs/benchmark page). vs simdjson: 1.1-1.6x faster reads against On Demand on read-only input including copy+pad (root README range); the weighted 2.14x is against simdjson DOM, and against On Demand on a caller-prepared padded buffer the weighted margin is 1.34x fresh / 1.19x with parser and allocator reused (simdjson has no serializer). vs nlohmann-json: 2.8-27x faster writes, weighted 6.67x (not in read comparison). vs upstream yyjson: 1.0-1.8x faster reads / 1.0-2.1x faster writes, weighted 1.69x / 1.46x. |
| **Workload** | Read (parse a document and visit every element) and write (serialize a parsed document back to text) across ten JSON documents (0.1-66.4 MB, number-heavy to string-heavy) from the yyjson_benchmark dataset, measured with Google Benchmark (median of 11-101 repetitions, one process per run). |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-12900K, 8 logical CPUs (E-cores and Turbo Boost disabled), Ubuntu 26.04.1 LTS, Linux 7.0.0 |
| **Compiler and flags** | GCC 15.2.0; all four benchmark executables built with -O3, -march=x86-64-v3 and link-time optimization (rapidjson and nlohmann-json are header-only and compiled with identical flags; simdjson and yyjson are prebuilt vcpkg libraries built without -march=x86-64-v3 or LTO). |
| **Adoption** | 95 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/yosh-matsuda/cpp-yyjson) · [benchmark](https://github.com/yosh-matsuda/cpp-yyjson/blob/main/docs/benchmark/README.md) |

## Verdict

Setup: Intel i9-12900K (P-cores only, Turbo off), Ubuntu 26.04, GCC 15.2.0 with -O3 -march=x86-64-v3 and LTO for both cpp-yyjson (AVX2 backend) and header-only RapidJSON 2025-02-26 (default Parse flags, RAPIDJSON_SSE42 not defined). Parsing and visiting every element of ten yyjson_benchmark documents was 1.4x (canada) to 4.6x (github_events) faster than RapidJSON, 2.31x time-weighted; re-serializing was 2.6-8.1x faster, 3.91x weighted. The verifier recomputed every ratio from the committed Google Benchmark logs, and the two largest documents (48.8 MB fgo, 66.4 MB otfcc) dominate the weighted totals.

## Use it when

- C++20 code that parses whole documents into a DOM and walks them, or builds documents and serializes them, where RapidJSON or nlohmann-json is the bottleneck. String-heavy documents (gsoc-2018, github_events) and indented ones gain the most.
- x86-64 builds where you can set CPPYYJSON_ENABLE_AVX2=ON and call cpp_yyjson_enable_lto(). This is the configuration that was benchmarked.
- Linux/glibc services that read or write documents of tens of MB. The huge-page advice gives 1.4-1.8x over upstream yyjson there; on other systems, reuse a pool_allocator instead.
- Read-only input such as network buffers or const strings that you cannot pad or overwrite. On such input it read all ten test documents 1.06-1.65x faster than simdjson On Demand, whose time includes the copy and padding it needs.
- Teams that want yyjson-level speed with idiomatic C++: ranges, std::optional accessors, RAII document lifetime and struct reflection for (de)serialization.

## Skip it when

- You need a SAX, streaming or incremental reader, or bounded memory on very large inputs. The documented API builds a full DOM only.
- Access patterns with many lookups in large objects. Object find/contains/operator[] are O(N), and mutable array operator[] is O(N).
- Toolchains older than C++20 with &lt;ranges&gt; and &lt;format&gt;. The minimum is GCC 13, LLVM 17 or AppleClang 16.
- Non-x86 targets where you expect the headline numbers. The SIMD string and indentation paths are x86-64 only, huge pages work only on Linux/glibc, and no ARM results are published.
- Strict dependency policies. The speed comes from a single-maintainer downstream fork: 14 commits on top of yyjson 0.13.0, written 2026-09-12 to 2026-09-23, that upstream declined to merge (ibireme/yyjson PR #294). Upstream security fixes must be carried over by hand, and the project has 95 stars.

## How it is fast

Parsing and serialization are done by yyjson's DOM reader and writer, which run in a bundled fork of yyjson 0.13.0. The author added x86-64 changes to that fork after upstream declined them because upstream yyjson stays free of SIMD on purpose. The changes: SSE2/AVX2 scanning of strings 16 or 32 bytes at a time for quote, backslash, control or non-ASCII bytes (byte-shuffle table plus movemask); SIMD block copies of long strings on write; one vector compare to skip the predicted indentation of pretty-printed input; SWAR parsing of four decimal digits per step; and madvise(MADV_HUGEPAGE) on glibc blocks of 32 MiB or more, which cuts page faults. The benchmark compiles the backend together with the calling code under LTO; the author measures no overhead from the C++ layer itself.

## Compared with alternatives

Pick it over yyjson when you want a C++ API (ranges, std::optional, RAII, struct reflection) plus the fork's x86-64 SIMD and huge-page gains: 1.0-1.8x reads and 1.0-2.1x writes vs upstream yyjson 0.12.0. Pick it over simdjson when you also build, mutate or serialize JSON (simdjson has no serializer) or cannot supply a padded buffer. For fixed schemas mapped straight into structs, glaze skips the DOM step and is not in this benchmark, so measure both.

## Integration

| | |
|---|---|
| **Form** | header-only C++ API plus a static lib (bundled yyjson backend compiled from src/yyjson.c); fully header-only over an external yyjson with -DCPPYYJSON_USE_BUNDLED_YYJSON=OFF |
| **Dependencies** | none with the bundled backend (yyjson.h and field_reflection.hpp ship in include/); external mode needs yyjson &gt;= 0.6.0 (e.g. from vcpkg) |
| **Minimum toolchain** | C++20 with &lt;ranges&gt; and &lt;format&gt;; CI tests GCC 13-16, LLVM 17-22, AppleClang 16/17/21, MSVC cl and clang-cl (windows-2022/2025); CMake adds /Zc:preprocessor for MSVC |
| **Platforms** | CI covers x86-64 Linux and Windows and arm64 macOS. SIMD paths are x86-64 only: SSE2 by default, AVX2 opt-in with CPPYYJSON_ENABLE_AVX2=ON, after which the binary requires an AVX2 CPU. Huge-page advice works only on Linux with glibc. |
| **Thread safety** | Not documented by cpp-yyjson. The bundled yyjson.h says reads are thread-safe when the input is not modified and the allocator is thread-safe or NULL, and that its pool and dynamic allocators are not thread-safe. Documents are reference-counted with std::shared_ptr. The reference shows building separate arrays on worker threads and merging them on one thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default build is not the benchmarked build. AVX2 is OFF unless you set CPPYYJSON_ENABLE_AVX2=ON; it defaults to ON only for the repo's own benchmark build. LTO applies only after cpp_yyjson_enable_lto(target). With Clang 17 or older, or MSVC, every target that links cpp-yyjson then needs that call, or the link fails with 'file format not recognized'.
- Errors are exceptions: read_error for invalid JSON, bad_cast for a failed conversion, std::out_of_range from const operator[] on a missing key, and std::runtime_error when a pool_allocator is too small. Non-const operator[] on a mutable object inserts a default value for a missing key, and emplace does not check for duplicate keys.
- The \*_ref classes and string_view results borrow from the document that owns them. Referenced (not copied) strings in built documents must outlive the document. Copying costs 2.5x on array_string, so referencing is faster when lifetimes allow it. stack_pool_allocator must outlive every value created with it.
- Each yyjson::value/array/object owns a separate mutable document, so creating many small ones is expensive. The reference recommends tuple/pair construction and emplace(key, empty_object) over building nested objects separately and inserting them.

## Known shortcomings

- The benchmark enabled AVX2, x86-64-v3 and LTO, which a default user build does not; RapidJSON ran without its opt-in SSE whitespace skipping. The backend is a young single-maintainer fork of yyjson 0.13.0 with SIMD that upstream declined (yyjson PR #294), so upstream fixes must be carried by hand. x86-64 only for SIMD paths; the top ratios (4.6x read, 8.1x write) come from 9-19 us timings on a 0.1 MB document.

## Caveats and trade-offs

The project's own README flags an asymmetry as the main caveat of its comparison: simdjson and yyjson are linked as prebuilt vcpkg libraries without -march=x86-64-v3 or LTO, while header-only rapidjson and nlohmann-json get the same flags as cpp-yyjson; this could inflate the margin against simdjson/yyjson specifically (simdjson picks SIMD kernels at runtime, which partly offsets this). The page also says much of the weighted total comes from the bundled backend's madvise(MADV_HUGEPAGE) on &gt;32 MiB blocks (Linux/glibc only), which only the two large documents (fgo, otfcc) get; with the allocator reused the fgo/otfcc read margin over yyjson shrinks to 91%/96% of its time. The per-document ranges come from the root README table; the weighted totals come from docs/benchmark/README.md. I recomputed both from the committed raw logs and they match. Compiler, flags and CPU are stated, and the code and raw logs are public, so Tier A holds.

Requires a C++20 compiler with range support; bundled backend compiles yyjson.c from source (an external-yyjson mode is also available); the huge-page allocator optimization only applies on Linux/glibc for blocks &gt;=32MB, so most of the weighted-average gain against yyjson/simdjson on the two largest documents (fgo, otfcc) comes from that platform-specific effect rather than parsing algorithm differences; simdjson has no serializer so is excluded from write comparisons and nlohmann-json is excluded from read comparisons.

## Maintenance

Active (v1.0.0 released 2026-09-24, CI on GCC/LLVM/AppleClang/MSVC) and MIT-licensed, bundled yyjson fork included, so it is easy to vendor. It is a single-maintainer project with 95 stars, and its SIMD backend is about two weeks old.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code (test/bench_read.cpp, test/bench_write.cpp, test/CMakeLists.txt, docs/benchmark/run_benchmarks.sh) plus raw Google Benchmark logs, run directly against RapidJSON. The page states GCC 15.2.0, -O3 -march=x86-64-v3 with LTO (confirmed in test/CMakeLists.txt), and an Intel Core i9-12900K.
- **Verifier notes:** I recomputed every ratio from the committed logs (test/\*_bench_\*.log): RapidJSON read 1.40-4.58x (weighted 2.31), write 2.56-8.11x (3.91); nlohmann 2.77-26.7x (6.67); yyjson read 1.05-1.79x (1.69), write 0.99-2.11x (1.46); simdjson On Demand copy+pad 1.06-1.65x, DOM weighted 2.14x. The only fix is in claimed_speedup: the record had attached the weighted 2.14x to the On Demand range, but 2.14x is against DOM. Metadata checks out (MIT, 95 stars, last commit 2026-09-24, v1.0.0 release, not a fork, not archived).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/docs/benchmark/README.md>
  - <https://github.com/yosh-matsuda/cpp-yyjson>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/README.md>
  - <https://github.com/yosh-matsuda/cpp-yyjson/tree/main/docs/benchmark>
  - <https://github.com/yosh-matsuda/cpp-yyjson/tree/main/test>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/CMakeLists.txt>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/docs/benchmark/run_benchmarks.sh>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/cpp_yyjson_bench_read.log>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/cpp_yyjson_bench_write.log>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/yyjson_bench_read.log>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/yyjson_bench_write.log>
- **Sources the enricher read:**
  - <https://github.com/yosh-matsuda/cpp-yyjson>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/README.md>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/docs/benchmark/README.md>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/docs/reference.md>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/include/cpp_yyjson.hpp>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/include/yyjson.h>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/src/yyjson.c>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/CMakeLists.txt>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/CMakeLists.txt>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/bench_read.cpp>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/cpp_yyjson_bench_read.log>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/test/cpp_yyjson_bench_write.log>
  - <https://github.com/yosh-matsuda/cpp-yyjson/blob/main/.github/workflows/tests.yml>
  - <https://github.com/yosh-matsuda/cpp-yyjson/issues?q=is%3Aissue>
  - <https://github.com/yosh-matsuda/cpp-yyjson/issues/5>
  - <https://github.com/yosh-matsuda/cpp-yyjson/issues/23>
  - <https://github.com/yosh-matsuda/cpp-yyjson/pulls?q=is%3Apr>
  - <https://github.com/yosh-matsuda/cpp-yyjson/releases>
  - <https://github.com/yosh-matsuda/yyjson/commits/simd>
  - <https://github.com/ibireme/yyjson/compare/0.13.0...yosh-matsuda:yyjson:simd>
  - <https://github.com/ibireme/yyjson/blob/master/CHANGELOG.md>
  - <https://github.com/ibireme/yyjson/pull/294>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/yosh-matsuda/cpp-yyjson`) · [data/wave4/enrich/raw/github_com_yosh_matsuda_cpp_yyjson.json](../../../data/wave4/enrich/raw/github_com_yosh_matsuda_cpp_yyjson.json) (enrichment confidence 0.85)

</details>
