# simdjson experimental_json_builder (C++26 reflection-based JSON serializer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Obsolete 2024 prototype of a C++26 reflection JSON serializer; about 20x nlohmann/json throughput. Now part of simdjson's builder.

| | |
|---|---|
| **Beats** | nlohmann/json |
| **Claimed result** | Serialization throughput vs nlohmann/json, in MB/s. M3 Max: Twitter 1900 vs 100 (19x) and artificial 1800 vs 50 (36x). Intel Ice Lake: Twitter 1800 vs 110 (16x) and artificial 1400 vs 50 (28x). The page's summary is 'roughly 20x faster than nlohmann/json'. Two claims are qualitative only, with no numbers on the page: hand-written code 'can be slightly faster... (10% to 20%)', and 'We can be twice as fast as reflect-cpp'. |
| **Workload** | Serializing native C++ structs to JSON using C++26 static reflection (P2996), measured on the twitter.json corpus and on an artificial/synthetic JSON dataset, reported in MB/s |
| **Metric** | throughput |
| **Hardware** | Apple M3 Max MacBook Pro; an Intel Ice Lake machine (exact SKU not given) |
| **Compiler and flags** | clang++ from the Bloomberg experimental clang-p2996 fork (implements P2996 reflection; the page gives no version or commit). CMakeLists.txt hardcodes clang++ and defaults to CMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG), with -freflection -stdlib=libc++ -std=c++26. This is the same at blog-date commit d3d2521 and at HEAD. Baseline: nlohmann/json 3.10.5 via CPM, and reflect-cpp v0.13.0 (patched). |
| **Adoption** | 60 stars |
| **Last commit** | 2025-10-28 |
| **Links** | [repository](https://github.com/simdjson/experimental_json_builder) · [benchmark](https://lemire.me/blog/2024/08/13/reflection-based-json-in-c-at-gigabytes-per-second/) |

## Verdict

Lemire's 2024-08-13 post serialized a Twitter-derived struct (a field subset of twitter.json) and a synthetic JSON-Generator dataset. On an Apple M3 Max: 1900 vs 100 MB/s (19x) and 1800 vs 50 MB/s (36x). On an unnamed Intel Ice Lake: 1800 vs 110 (16x) and 1400 vs 50 MB/s (28x). The baseline was nlohmann/json 3.10.5 (build a json tree, then dump()). Both sides were built with the Bloomberg clang-p2996 fork, Release (-O3), with libc++. MB/s is output bytes over mean time per call. The claims of 10-20% slower than hand-written code and 2x faster than reflect-cpp come with no published numbers.

## Use it when

- In production, use the successor, not this repo. simdjson v4.0.0+ has simdjson::to_json(obj) and string_builder `sb << obj`. On the latest release (v4.6.11), define SIMDJSON_STATIC_REFLECTION=1 or pass CMake -DSIMDJSON_STATIC_REFLECTION=ON, with a P2996 compiler (simdjson's p2996/ docker uses clang-p2996).
- On simdjson master (unreleased as of 2026-09-26), reflection is auto-detected. Compiling with GCC 16 and `-std=c++26 -freflection` is enough. CMake gets SIMDJSON_STATIC_REFLECTION_MODE=AUTO|ON|OFF.
- Throughput-bound output of plain aggregates (ints, floats, bools, std::string, std::vector, nested structs) to compact JSON, such as API responses or logs, where nlohmann's build-a-json-tree-then-dump() path is the bottleneck.
- Reproducing or studying Lemire's August 2024 numbers, or learning how a minimal P2996 serializer works. json_builder.h is about 150 lines.

## Skip it when

- Any production build. The author declared the repo obsolete on 2025-10-28. It needs the 2024-era Bloomberg clang-p2996 fork with libc++, and the last code change was in September 2024.
- Types beyond arithmetic, strings, indexable containers (size() plus operator[]) and aggregates. json_builder.h has no overloads for std::map, std::optional, enums or smart pointers, and it has no field renaming, skipping or pretty-printing. simdjson's successor has all of these (annotations like rename/skip, enums as strings, optional, fractured-JSON pretty printing).
- Data whose strings contain control characters. The escape table emits "\x0000"-style sequences, which are not valid JSON; simdjson's version uses \u0000. NaN and infinity go through std::to_chars and come out as nan/inf, which are also not valid JSON.
- Large string fields. string_builder::capacity_check doubles the capacity only once, whatever the size of the pending write. A single string bigger than the space left after one doubling (for example, a \~3 KB string into a fresh 1 KB builder) writes past the heap buffer. simdjson's version grows to max(2\*capacity, position+needed).
- When you need parsing or a DOM. This is a one-way struct-to-JSON writer, not a replacement for nlohmann::json values.

## How it is fast

C++26 static reflection (P2996: nonstatic_data_members_of plus member splicing t.[:dm:]) unrolls each struct at compile time into a straight-line series of buffer appends, with no intermediate DOM. The intermediate DOM is where the nlohmann path spends its time. Each key is quoted and escaped at compile time (a consteval to_quoted_escaped), so at run time it is one memcpy of a constant. Everything goes into one reusable, doubling char buffer (string_builder): numbers through std::to_chars, and strings after a 16-byte SSE2/NEON scan that takes a plain memcpy fast path when nothing needs escaping.

## Compared with alternatives

Every C++ sibling here (Cista++, struct_pack, YAS, bitsery, FBE, ser20) targets binary formats, and SerialXML emits XML. Pick this family (in practice simdjson's builder) when the output must be JSON text from unannotated structs. ffjson is the Go analogue: it generates code ahead of time instead of using compile-time reflection.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | The serializer headers need only the standard library plus &lt;experimental/meta&gt; from the clang-p2996 fork. The repo's CMake also fetches simdjson (builder_development_branch), nlohmann/json 3.10.5, reflect-cpp v0.13.0 (patched) and optionally corrosion/Rust for the benchmarks via CPM. |
| **Minimum toolchain** | Bloomberg clang-p2996 fork (2024 snapshot, no version pinned) with -std=c++26 -freflection -stdlib=libc++. The code uses the pre-final single-caret ^T syntax and std::meta::reflect_value, so expect it not to build on compilers with final P2996 syntax (^^, &lt;meta&gt;). Open issue #45 notes the ^^ change. No released compiler is documented as working. |
| **Platforms** | x86-64 (SSE2 escape path), aarch64 (NEON path), scalar fallback elsewhere. Benchmarked on Apple M3 Max and Intel Ice Lake. The README supports Linux/macOS via docker and recommends WSL on Windows. |
| **Thread safety** | Not documented. The free functions keep no global state, and to_json_string makes a local string_builder per call. A string_builder instance is not synchronized. |
| **Drop-in for the baseline** | no |

## Gotchas

- The top-level CMakeLists.txt hardcodes CMAKE_C_COMPILER=clang and CMAKE_CXX_COMPILER=clang++, which overrides CC/CXX. It adds -freflection -stdlib=libc++ -std=c++26 through the INTERFACE target, so every consumer inherits libc++.
- Before P1306 expansion statements existed, member iteration used a substitute()/replicator workaround. universal_formatter.h includes a non-existent string_builder.hpp and uses the removed name_of, so it is dead code.
- Benchmark asymmetry: the nlohmann baseline builds a nlohmann::json object per record, then calls dump() into a fresh std::string. bench_fast_simpler reuses a warmed string_builder instead. The blog does not say which of the three reflection variants (reused builder, fresh std::string, assign) produced the headline MB/s.
- string_builder throws std::runtime_error on capacity overflow and uses new[] (so std::bad_alloc is possible). There is no allocator customization.

## Known shortcomings

- The repo says it is obsolete: the same reflection-based builder now ships in simdjson itself (generic/builder, benchmark/static_reflect). Requires the clang-p2996 reflection fork. The 'twice as fast as reflect-cpp' line has no published numbers.
- Emits invalid JSON for control characters (\x0000-style escapes) and for NaN/inf. string_builder::capacity_check doubles once regardless of write size, so a large string can write past the buffer (heap overflow; fixed in simdjson's version). Uses pre-standard reflection syntax (^T, &lt;experimental/meta&gt;) and probably does not build on current compilers. Use simdjson::to_json / string_builder in simdjson v4.0.0+ instead (enable SIMDJSON_STATIC_REFLECTION with a P2996 compiler).

## Caveats and trade-offs

The repo README now opens with 'THIS REPOSITORY IS OBSOLETE. The functionality is part of the simdjson library'. The move has already happened: simdjson/simdjson, which is already catalogued, ships include/simdjson/generic/builder and benchmark/static_reflect. This standalone prototype is therefore the historical source of the numbers, not the place to get the code today. Since Dec 2024 the only commits are README edits, the last being the 2025-10-28 obsolete notice. The benchmark needs the experimental Bloomberg clang-p2996 fork (through Docker or a from-source Clang build), because the CMake setup hardcodes clang++ with -freflection and libc++. The baseline is the older nlohmann/json 3.10.5 (Jan 2022). The Ice Lake CPU is named only by microarchitecture, with no SKU. The comparisons with hand-written code and reflect-cpp have no published numbers.

Requires an experimental, non-shipping C++26 compiler (Bloomberg's clang-p2996 fork with -freflection) rather than any release toolchain, so the technique is not usable in production yet. Same post reports it as \~2x faster than reflect-cpp (getml/reflect-cpp, an existing reflection-based serialization library) though exact reflect-cpp throughput numbers are not tabulated on the page. Hand-written (non-reflective) serialization code remains 10-20% faster than the generated code.

## Maintenance

Declared obsolete by its authors: only README edits since September 2024, and the 2025-10-28 notice says the functionality now lives in simdjson. It is Apache-2.0 and small enough to read or vendor for study, but for real use take simdjson &gt;= 4.0.0's builder, which is actively maintained (v4.6.11 released 2026-09-05; builder commits through 2026-09-23).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Lemire's 2024-08-13 post has two MB/s tables comparing nlohmann/json with the C++26 serializer, and it names an Apple M3 Max and the Bloomberg clang-p2996 compiler. The benchmark code is public in the linked repo (benchmarks/src/benchmark_serialization_twitter.cpp and benchmark_serialization.cpp, with nlohmann/json 3.10.5 pinned in benchmarks/CMakeLists.txt). CMakeLists.txt at the blog-date commit d3d2521 forces a Release build (CMake default -O3 -DNDEBUG) with -freflection -stdlib=libc++ -std=c++26, so A holds for the M3 Max numbers. The Ice Lake numbers have no exact SKU.
- **Verifier notes:** All four nlohmann ratios and the MB/s figures match the page exactly. The only fix is the reflect-cpp wording: the page says 'can be twice as fast', with no numbers. I did not reject this as the known simdjson project, because the benchmark measured this separate prototype codebase. The orchestrator may still want to fold the serialization claim into the existing simdjson/simdjson entry, since the README says the functionality now lives there. maintenance_status stays 'active' under the last-commit rule (2025-10-28 is about 11 months ago), but the author has declared the repo obsolete.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://lemire.me/blog/2024/08/13/reflection-based-json-in-c-at-gigabytes-per-second/>
  - <https://github.com/simdjson/experimental_json_builder>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/README.md>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/CMakeLists.txt>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/src/CMakeLists.txt>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/src/benchmark_serialization_twitter.cpp>
  - <https://github.com/simdjson/experimental_json_builder/blob/d3d2521d9d3ac2f634012427552a1fcb690c4057/CMakeLists.txt>
  - <https://github.com/simdjson/experimental_json_builder/blob/d3d2521d9d3ac2f634012427552a1fcb690c4057/benchmarks/CMakeLists.txt>
  - <https://github.com/simdjson/experimental_json_builder/commits/main>
  - <https://github.com/simdjson/simdjson>
  - <https://github.com/simdjson/simdjson/releases>
- **Sources the enricher read:**
  - <https://github.com/simdjson/experimental_json_builder>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/README.md>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/include/simdjson/json_builder/json_builder.h>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/include/simdjson/json_builder/json_escaping.h>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/include/simdjson/json_builder/string_builder.h>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/include/simdjson/json_builder/universal_formatter.h>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/CMakeLists.txt>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/src/benchmark_serialization_twitter.cpp>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/src/benchmark_serialization.cpp>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/src/benchmark_helper.hpp>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/src/event_counter.h>
  - <https://github.com/simdjson/experimental_json_builder/blob/main/benchmarks/src/nlohmann_twitter_data.hpp>
  - <https://github.com/simdjson/experimental_json_builder/issues?q=is%3Aissue>
  - <https://github.com/simdjson/experimental_json_builder/issues/45>
  - <https://github.com/simdjson/experimental_json_builder/issues/11>
  - <https://github.com/simdjson/experimental_json_builder/pulls?q=is%3Apr>
  - <https://github.com/simdjson/experimental_json_builder/commits/main>
  - <https://lemire.me/blog/2024/08/13/reflection-based-json-in-c-at-gigabytes-per-second/>
  - <https://github.com/simdjson/simdjson>
  - <https://github.com/simdjson/simdjson/blob/master/README.md>
  - <https://github.com/simdjson/simdjson/blob/master/doc/builder.md>
  - <https://github.com/simdjson/simdjson/blob/master/doc/basics.md>
  - <https://github.com/simdjson/simdjson/blob/v4.6.11/doc/basics.md>
  - <https://github.com/simdjson/simdjson/blob/master/include/simdjson/compiler_check.h>
  - <https://github.com/simdjson/simdjson/blob/v4.6.11/include/simdjson/compiler_check.h>
  - <https://github.com/simdjson/simdjson/blob/master/CMakeLists.txt>
  - <https://github.com/simdjson/simdjson/blob/master/p2996/README.md>
  - <https://github.com/simdjson/simdjson/blob/master/benchmark/static_reflect/CMakeLists.txt>
  - <https://github.com/simdjson/simdjson/blob/master/include/simdjson/generic/builder/json_string_builder-inl.h>
  - <https://github.com/simdjson/simdjson/blob/master/include/simdjson/generic/builder/json_builder.h>
  - <https://github.com/simdjson/simdjson/commits/master/include/simdjson/generic/builder/json_builder.h>
  - <https://github.com/simdjson/simdjson/releases/tag/v4.0.0>
  - <https://github.com/simdjson/simdjson/releases/tag/v4.1.0>
  - <https://github.com/simdjson/simdjson/releases/tag/v4.2.2>
  - <https://github.com/simdjson/simdjson/releases/tag/v4.3.0>
  - <https://github.com/simdjson/simdjson/releases/tag/v4.6.0>
  - <https://github.com/simdjson/simdjson/releases>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/simdjson/experimental_json_builder`) · [data/wave4/enrich/raw/github_com_simdjson_experimental_json_builder.json](../../../data/wave4/enrich/raw/github_com_simdjson_experimental_json_builder.json) (enrichment confidence 0.82)

</details>
