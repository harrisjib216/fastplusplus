# Boost.JSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Mutable C++11 JSON DOM with an SSE2-assisted streaming parser; median \~2.6x faster parsing than nlohmann/json, roughly ties RapidJSON.

| | |
|---|---|
| **Beats** | nlohmann/json, RapidJSON |
| **Claimed result** | Page charts, in MB/s, listed as clang / gcc / msvc. Parse citm_catalog: boost 476/503/477 vs nlohmann 140/143/148 (\~3.3-3.5x, derived from page data), and boost(pool) 1120/1096/999 vs rapidjson(pool) 1200/1279/978, so it is slower on clang and gcc and roughly tied on msvc. Parse canada: boost 385/395/369 vs nlohmann 55/26/52 (\~7-15x, derived from page data), and boost(pool) 642/675/637 vs rapidjson(pool) 506/641/490. Serialize citm_catalog: boost 2882/3263/2128 vs nlohmann 1151/1204/1142 (\~1.9-2.7x, derived from page data) and vs rapidjson 2210/2469/2135. Across all 14 files x 3 compilers (derived from page data / bench/results.txt): boost beats nlohmann in 42/42 parse cases (2.1x-38.7x, median \~2.6x) and 42/42 serialize cases (1.7x-9.3x, median \~3.5x). Against RapidJSON, boost (default) wins only 20/42 parse cases (median \~0.94x); boost(pool) beats rapidjson(pool) in 33/42 parse cases (median \~1.26x); boost beats rapidjson in 33/42 serialize cases (median \~1.17x). |
| **Workload** | Boost.JSON's own bench program (bench/bench.cpp) measures in-memory parse and serialize throughput in MB/s over 14 standard JSON files between 64KB and 3.25MB: apache_builds, canada, citm_catalog, github_events, gsoc-2018, instruments, marine_ik, mesh, mesh.pretty, numbers, random, twitter, twitterescaped and update-center. It compares boost (default allocator) and boost (pool/monotonic_resource) against rapidjson (CrtAllocator), rapidjson (MemoryPoolAllocator) and nlohmann/json. Each configuration runs for at least 5 s per sample, and the median samples are averaged. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700K CPU @ 4.20GHz, Windows 10, 32GB RAM |
| **Compiler and flags** | gcc 8.1 (-O3), clang 12.0 (-O3), msvc 19.26 (/O2); x64/sse2 builds |
| **Adoption** | 479 stars on the standalone mirror (Boost.JSON ships as part of the wider Boost distribution, so GitHub stars understate real usage) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/boostorg/json) · [benchmark](https://www.boost.org/doc/libs/latest/libs/json/doc/html/benchmarks.html) |

## Verdict

Boost's own bench/bench.cpp, last regenerated in October 2020 on an Intel i7-7700K under Windows 10 (gcc 8.1 -O3, clang 12 -O3, MSVC 19.26 /O2, SSE2), measured in-memory parse and serialize MB/s on 14 simdjson-corpus files against unpinned HEAD clones of RapidJSON and nlohmann/json. Boost.JSON beat nlohmann in all 42 parse cases (median \~2.6x) and all 42 serialize cases (median \~3.5x). Against RapidJSON the result is mixed: the default allocator won 20/42 parse cases, while the monotonic pool won 33/42 (median \~1.26x).

## Use it when

- You need a mutable DOM (edit it, build documents from scratch, pass `json::value` through library APIs) and nlohmann/json shows up in profiles. The vendor run was 2.1-38.7x faster at parsing and 1.7-9.3x faster at serializing across 14 files and 3 compilers.
- Parse-then-discard workloads (request bodies, message payloads, config snapshots) where you can pass a `monotonic_resource` to `parse()`. That configuration beat RapidJSON's MemoryPoolAllocator in 33/42 parse cases (median \~1.26x), for example canada.json at 637-675 vs 490-641 MB/s.
- Network code that receives JSON in chunks. `stream_parser::write_some` resumes across buffer boundaries; Boost's comparison page lists no incremental parsing for RapidJSON or nlohmann.
- Codebases already on Boost (Asio/Beast) or with constraints such as `-fno-exceptions`, `error_code`/`system::result` APIs, arena or stack-buffer allocation (`static_resource`, `BOOST_JSON_STACK_BUFFER_SIZE`), or big-endian targets.
- Mapping JSON straight to structs without building a DOM: `parse_into<T>` with Boost.Describe avoids the parse-then-`value_to` cost.

## Skip it when

- Maximum-speed read-only extraction from large documents: simdjson and yyjson are faster. In an independent MSVC 2022 run (Boost 1_90), Boost.JSON read a 540.82MB integer file in 2.269 s vs yyjson 1.007 s.
- String-heavy input with the default allocator, compared with RapidJSON's CRT allocator: it loses on twitter.json (308-329 vs 406-423 MB/s) and random.json (171-180 vs 222-308 MB/s). Only the `monotonic_resource` configuration is reliably competitive with RapidJSON.
- Hot paths that (de)serialize structs, where Glaze fits. In the maintainer's 2025 gcc run (issue #1102), Glaze direct parsing reached 1880 vs Boost.JSON direct 640 MB/s on citm_catalog, and direct serialization 8275 vs 2275 MB/s.
- Projects that cannot take Boost dependencies. Standalone mode was removed in Boost 1.79, and the build pulls in Container, System, Charconv, Endian, Describe, Mp11 and others.
- Numbers outside int64/uint64/double (no big-number or number-as-string mode; issue #872 is still open), binary formats such as CBOR (none in the tree), or heavy mutation of a document parsed into `monotonic_resource`, which never reclaims memory before it is destroyed.

## How it is fast

The parser is a hand-written resumable state machine, templated on the handler, on each parse option and on a StackEmpty flag so the non-resuming path skips suspend-state checks, and it uses SSE2 16-byte scans (`_mm_cmpeq_epi8` plus `_mm_movemask_epi8`) to find quote, backslash and control characters, skip whitespace and count digits. `value_stack` buffers parsed elements and then builds each array, object and string with one exact-size allocation; with `monotonic_resource` (a bump-pointer arena whose deallocate is a no-op) and parser reuse, allocation cost almost disappears. The default 'imprecise' number mode scales the mantissa with a 618-entry power-of-10 table (precise mode uses a fast_float-derived `from_chars`). Serialization uses a 2-digit lookup table for integers and Boost.Charconv `to_chars` for doubles, and objects above a small size carry a hash index for O(1) average key lookup.

## Compared with alternatives

Choose Boost.JSON over simdjson or yyjson when you need a mutable, allocator-aware C++ DOM with chunked incremental parsing; simdjson's DOM is read-only and yyjson is a C API. Choose it over Glaze or reflect-cpp when you need a real DOM: in the maintainer's 2025 run, Boost.JSON pool parsing was 2-4x faster than `glz::json_t` (citm_catalog 1177 vs 328 MB/s). For direct struct mapping, Glaze is faster.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib; header-only by including &lt;boost/json/src.hpp&gt; in exactly one TU (MSVC also needs BOOST_JSON_NO_LIB) |
| **Dependencies** | Boost: Assert, Charconv, Config, Container, ContainerHash, Core, Describe, Endian, Mp11, System, ThrowException (from build.jam); Boost.Container may need linking |
| **Minimum toolchain** | C++11; README lists clang 3.8 and 4-23, gcc 5-16, MSVC 14.0-14.5 as tested (GCC &lt;5 support ended in Boost 1.88) |
| **Platforms** | any; SSE2 fast paths switch on automatically on x86/x64 (`__SSE2__`/`_M_X64`) with scalar fallbacks elsewhere; little- and big-endian via Boost.Endian |
| **Thread safety** | Standard container guarantee: distinct instances may be used concurrently, but no member of a shared `value`, `object` or `stream_parser` may run while a non-const member runs on it; `monotonic_resource` members must not be called concurrently. |
| **Drop-in for the baseline** | false — the value type and accessor API differ from both nlohmann/json and RapidJSON, so migration means rewriting call sites |

## Gotchas

- `parse_options::max_depth` defaults to 32, so more deeply nested documents fail to parse until you raise it.
- The default `number_precision::imprecise` can lose precision on long mantissas; use `precise` for correctly rounded doubles at some speed cost. The published benchmark used imprecise mode, with RapidJSON also run without its full-precision flag.
- Duplicate keys: the parser keeps the last occurrence, but constructing an `object` from an initializer list or range keeps the first. Doubles are always serialized in scientific notation (`chars_format::scientific`).
- The allocator is `boost::container::pmr::memory_resource`, not `std::pmr` (a `std::pmr` resource needs an adapter; issue #583). `storage_ptr` is reference-counted, and `monotonic_resource` frees only on destruction.

## Caveats and trade-offs

These are first-party results, last regenerated on 2020-10-21 (commit 8f42799) and not re-run since; bench/bench.cpp has changed since then (2025 commits). The RapidJSON and nlohmann versions are unpinned (bench/clone.sh does a depth-1 clone of HEAD) and are not stated on the page. The clear win is over nlohmann/json; against RapidJSON the result is mixed, and Boost.JSON loses several parse workloads (e.g. random.json, citm_catalog and twitter on gcc). Independent corroboration comes from danielaparker/json_benchmarks (VS 2022 17.14.16 /O2 /Ot, Boost 1_90, laptop with no CPU model, run by the jsoncons author, single run, timing includes file stream I/O). There Boost.JSON reads the 540.82MB integer file in 2.269s vs nlohmann 8.177s and RapidJSON 2.254s, and the 794.72MB float file in 3.579s vs 15.997s and 3.443s.

Requires (or vendors) the wider Boost dependency footprint even though Boost.JSON itself is usable header-only/standalone; API is more verbose than nlohmann's for simple use cases; memory footprint (502MB/621MB in this test) sits between RapidJSON and yyjson.

## Maintenance

Actively maintained: Boost 1.92.0 is tagged and the develop branch had commits on 2026-09-23. BSL-1.0 and ships in every Boost release, so its 479 GitHub stars understate real usage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A on stronger evidence. Boost.JSON's own Benchmarks page compares against RapidJSON (pool and CRT allocators) and nlohmann/json. It states the CPU (Intel Core i7-7700K @ 4.20GHz, Windows 10, 32GB), the compilers and flags (gcc 8.1 -O3, clang 12.0 -O3, msvc 19.26 /O2), and the method. The benchmark code is public at boostorg/json bench/bench.cpp, with raw data in bench/results.txt and bench/samples.txt. The originally cited danielaparker/json_benchmarks pages would only be C: that suite has 6 stars, is run by the jsoncons author, and states no CPU model.
- **Verifier notes:** I switched benchmark_url to the project's own A-grade page. The numbers from the original json_benchmarks pages were all accurate for the Boost.JSON row and are kept in caveats as corroboration. The default branch is develop; its latest commit is dated 2026-09-23 (committer date), while pushed_at of 2026-09-24 reflects another branch. 479 stars and BSL-1.0 are confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/boostorg/json>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.floating_point.md>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.integer.md>
  - <https://github.com/danielaparker/json_benchmarks>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/tests/boost_json_benchmark.cpp>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/tests/nlohmann_benchmark.cpp>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/benchmarks.adoc>
  - <https://github.com/boostorg/json/blob/develop/bench/README.md>
  - <https://github.com/boostorg/json/blob/develop/bench/results.txt>
  - <https://github.com/boostorg/json/blob/develop/bench/samples.txt>
  - <https://github.com/boostorg/json/blob/develop/bench/bench.cpp>
  - <https://github.com/boostorg/json/blob/develop/bench/clone.sh>
  - <https://github.com/boostorg/json/blob/develop/doc/images/parse_citm_catalog.png>
  - <https://github.com/boostorg/json/blob/develop/doc/images/serialize_citm_catalog.png>
  - <https://github.com/boostorg/json/blob/develop/doc/images/parse_canada.png>
  - <https://github.com/boostorg/json/blob/develop/doc/images/parse_twitter.png>
  - <https://github.com/boostorg/json/commit/8f427990200fac48b8180458512bd6e7e4dd79c6>
  - <https://www.boost.org/doc/libs/latest/libs/json/doc/html/index.html>
  - <https://www.boost.org/doc/libs/latest/libs/json/doc/html/benchmarks.html>
- **Sources the enricher read:**
  - <https://github.com/boostorg/json>
  - <https://github.com/boostorg/json/blob/develop/README.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/benchmarks.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/comparison.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/faq.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/dom/numbers.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/io/parsing.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/conversion/direct.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/allocators/overview.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/allocators/uses_allocator.adoc>
  - <https://github.com/boostorg/json/blob/develop/doc/pages/allocators/storage_ptr.adoc>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/basic_parser_impl.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/basic_parser.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/detail/sse2.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/detail/config.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/detail/object.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/detail/impl/format.ipp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/parse_options.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/parse.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/object.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/impl/object.ipp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/monotonic_resource.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/stream_parser.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/value.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/value_stack.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/storage_ptr.hpp>
  - <https://github.com/boostorg/json/blob/develop/include/boost/json/impl/serializer.ipp>
  - <https://github.com/boostorg/json/blob/develop/CHANGELOG.adoc>
  - <https://github.com/boostorg/json/blob/develop/build.jam>
  - <https://github.com/boostorg/json/blob/develop/bench/README.md>
  - <https://github.com/boostorg/json/blob/develop/bench/bench.cpp>
  - <https://github.com/boostorg/json/blob/develop/bench/results.txt>
  - <https://github.com/boostorg/json/issues/1102>
  - <https://github.com/boostorg/json/issues/697>
  - <https://github.com/boostorg/json/issues/583>
  - <https://github.com/boostorg/json/issues?q=label%3APerformance>
  - <https://github.com/boostorg/json/issues?q=label%3ABug+is%3Aopen>
  - <https://www.boost.org/doc/libs/latest/libs/json/doc/html/benchmarks.html>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.integer.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/boostorg/json`) · [data/wave4/enrich/raw/github_com_boostorg_json.json](../../../data/wave4/enrich/raw/github_com_boostorg_json.json) (enrichment confidence 0.8)

</details>
