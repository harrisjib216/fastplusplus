# fkYAML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++11 YAML 1.2 DOM parser/emitter that parses 7.3-7.7x faster than yaml-cpp in the project's benchmark.

| | |
|---|---|
| **Beats** | yaml-cpp |
| **Claimed result** | 76.13 MiB/s vs yaml-cpp's 10.12 MiB/s (\~7.5x) on ubuntu.yml; 121.04 vs 16.67 MiB/s (\~7.3x) on citm_catalog.json; 56.08 vs 7.31 MiB/s (\~7.7x) on citm_catalog.yml (ratios derived from page data); README states 'more than 7x faster than yaml-cpp'. rapidyaml is \~2x faster than fkYAML only on ubuntu.yml (151.1/132.4 vs 76.1 MiB/s); fkYAML is slightly ahead of rapidyaml on citm_catalog.json (121.0 vs 109.5/113.1) and citm_catalog.yml (56.1 vs 53.7/53.4) |
| **Workload** | Deserialize an in-memory copy of ubuntu.yml, citm_catalog.json, and citm_catalog.yml with Google Benchmark v1.9.5 (tools/benchmark/main.cpp), reporting processed bytes/sec in a Release build. Compares fkYAML with yaml-cpp 0.9.0, libfyaml v1.0.0-beta1, and rapidyaml v0.16.0 (in-place and arena). The results were committed 2026-09-07 in tools/benchmark/results, as a single run per file with no repetitions. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800H @3.20GHz, Ubuntu 22.04 (WSL2) |
| **Compiler and flags** | g++ 11.4.0, CMake Release; tools/benchmark/CMakeLists.txt adds -O2 to the benchmarker target (which compiles header-only fkYAML); yaml-cpp/rapidyaml/libfyaml are built via FetchContent under their own Release flags |
| **Adoption** | 153 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/fktn-k/fkYAML) · [benchmark](https://github.com/fktn-k/fkYAML#benchmarking) |

## Verdict

The project's Google Benchmark v1.9.5 harness deserializes an in-memory std::string of ubuntu.yml (8,819 B), citm_catalog.yml (717,429 B) and citm_catalog.json (1,727,204 B) into a DOM and destroys it each iteration. Single Release runs built with g++ 11.4.0 (fkYAML at -O2; yaml-cpp 0.9.0 under its own Release flags) on a Ryzen 7 5800H under WSL2 gave fkYAML 76.1/56.1/121.0 MiB/s against yaml-cpp's 10.1/7.3/16.7 MiB/s (7.5x/7.7x/7.3x); no third party has reproduced this, and yaml-cpp ran only 6 iterations on each citm file.

## Use it when

- Replacing yaml-cpp where YAML load time matters. The benchmark inputs were an 8.8 KB block-YAML file (ubuntu.yml), a 0.7 MB YAML file and a 1.7 MB JSON file, and fkYAML was about 7.5x faster than yaml-cpp on all three.
- You want header-only, zero-dependency integration (a single-header node.hpp is provided, plus a CMake package and pkg-config) that builds as C++11 on old toolchains. CI covers GCC 5.3 to 16, Clang 3.4 to 21, AppleClang and VS 2022/2026.
- Code reads many typed values after parsing: ints, floats, bools and nulls are converted once during deserialize, so get_value&lt;int&gt;() or as_bool() does not re-parse text.
- Inputs arrive in mixed encodings (UTF-16/UTF-32 LE/BE with or without BOM), or JSON has to go through the same parser. In the benchmark, fkYAML's best absolute speed was on citm_catalog.json (121 MiB/s).
- Parse, modify and re-serialize workflows where an editable DOM with value semantics is more convenient than an event API.

## Skip it when

- You need the fastest C++ YAML parser for typical block-style files. In the same harness, rapidyaml was \~2x faster on ubuntu.yml (151/132 vs 76 MiB/s); fkYAML led it by only 4-11% on the two citm files.
- Large documents or memory-constrained targets. The library is DOM-only with no event/streaming API. FILE\* and istream inputs are read fully into a std::string first. Every string, sequence and mapping is a separate std::allocator heap object, and each node also carries a shared_ptr and a unique_ptr. There is no allocator or arena hook, and memory use is not benchmarked.
- Documents that depend on duplicate keys, source key order or YAML 1.1 semantics. Mappings default to std::map, so duplicate keys are rejected and output keys come out sorted. %YAML directives are ignored and the 1.2 rules apply. The source has no merge-key (&lt;&lt;) handling.
- Untrusted input in security-sensitive services without your own fuzzing. In Aug 2026, fuzzing found out-of-bounds reads, release-mode SEGVs, a leak, and a stack overflow from self-referential aliases (#536, #546, #548). All were fixed for v0.4.4/v0.5.0, but that is recent hardening.
- Code that needs API stability: the library is pre-1.0, and v0.5.0 (2026-09-17) removed APIs deprecated since v0.3.12 and v0.4.3 (node_t, type(), get_value_ref&lt;T&gt;(), and others).

## How it is fast

One up-front pass validates UTF-8 (transcoding UTF-16/32 or stripping CRs only when needed). For contiguous LF-only UTF-8 input, the lexer then runs directly on the caller's buffer and emits tokens as non-owning str_view slices, which avoids copying; the maintainer's PR #448 credits 'reducing redundant object creations and data copies'. Scalars are typed during parsing by a length-switched scanner and converted immediately, with hand-written bounds-checked integer parsing and std::from_chars for floats under C++17. As a result, nodes hold bool/int64_t/double natively, and only multi-line or escaped scalars use a scratch buffer (PR #409 split scalar parsing out of the lexer). The deserializer is an iterative state machine over an explicit std::deque context stack, not recursive descent. There is no SIMD; delimiter searches are per-byte char_traits::find loops.

## Compared with alternatives

Pick fkYAML over rapidyaml when you want a header-only C++11 value-type DOM with scalars already typed and your inputs look like the large, JSON-like citm files, where it matched or slightly beat ryml; for small block YAML, ryml was \~2x faster. fkYAML beat libfyaml 2.1-2.6x in the same harness, but PipeYAML's yaml-cpp ratios come from a different harness, so the published data cannot rank the two.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++11. CI tests GCC 5.3.1+, Clang 3.4.2+, AppleClang 15+, Visual Studio 17 2022+ and IntelLLVM 2026.1. The std::from_chars float path needs C++17 with __cpp_lib_to_chars. |
| **Platforms** | Linux, macOS and Windows are CI-tested. The code is portable C++ with no SIMD or other architecture-specific code. |
| **Thread safety** | Not documented. The headers have no mutable global or static state. All nodes of one document, including copies, share one std::shared_ptr to the document metainfo and anchor table. |
| **Drop-in for the baseline** | no |

## Gotchas

- A string-key lookup (node["k"] or at("k")) first builds a temporary basic_node, which heap-allocates a std::string, then does an O(log n) std::map search. Non-const operator[] inserts a node on a miss. The insertion-order option, fkyaml::ordered_map, is a std::vector with linear-search find().
- Every access through an anchor or alias node calls resolve_reference(). Since the fix for #548, that call walks the whole anchored subtree to detect self-references, so repeated access to large anchored subtrees costs O(subtree) each time.
- CRLF input forces a full copy of the buffer (the docs say this); only contiguous LF-only UTF-8 is parsed in place. Serialization always writes LF.
- Without C++17 &lt;charconv&gt; float support, each float scalar goes through std::stod on a temporary std::string, so the benchmark numbers may not hold for C++11/14 builds.

## Caveats and trade-offs

Numbers come from the project's own tool, but the tool's code, library versions, compiler and CPU are all public or stated. No third party has reproduced them yet. The runs are single Google Benchmark runs under WSL2. The ubuntu.yml result header reports 12 CPUs, while the other two runs report 16 CPUs from the same session. In the harness, the libfyaml loop never calls fy_document_destroy, so libfyaml's teardown is not timed; yaml-cpp and fkYAML nodes are destroyed inside the loop. This affects only the libfyaml comparison, not the yaml-cpp one.

Header-only; deserializes scalars into native bool/int/double types during parsing (rather than lazily on access like yaml-cpp), which changes API ergonomics and can speed up repeated queries

## Maintenance

Actively maintained (v0.5.0 on 2026-09-17, commits through 2026-09-21, one open issue) and MIT-licensed, header-only and easy to vendor, but still pre-1.0 with recent API removals and a fresh round of fuzz-driven fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The fkYAML README 'Benchmarking' section has Google Benchmark tables with fkYAML at 76.1277/121.04/56.0765 Mi/s and yaml-cpp at 10.122/16.6685/7.30883 Mi/s. They match the committed raw outputs in tools/benchmark/results/result_release_\*.txt (2026-09-07). The code is public (tools/benchmark/main.cpp and CMakeLists.txt pin yaml-cpp 0.9.0, rapidyaml v0.16.0, libfyaml v1.0.0-beta1, Release with -O2), and the page states the compiler (g++ 11.4.0) and CPU (Ryzen 7 5800H).
- **Verifier notes:** The benchmark_url given (tools/benchmark/README.md) has only usage instructions and no numbers. The numbers are in the main README Benchmarking section, and the raw outputs are in tools/benchmark/results. The record's claim that fkYAML is 'about 2x slower than rapidyaml on the same files' was wrong: that holds only for ubuntu.yml. last_commit was the pushed_at date; the newest commit on the default branch (develop) is 2026-09-21.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/README.md>
  - <https://github.com/fktn-k/fkYAML>
  - <https://github.com/fktn-k/fkYAML/blob/develop/README.md>
  - <https://github.com/fktn-k/fkYAML/tree/develop/tools/benchmark>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/CMakeLists.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/main.cpp>
  - <https://github.com/fktn-k/fkYAML/tree/develop/tools/benchmark/results>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_ubuntu_yml.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_citm_catalog_json.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_citm_catalog_yml.txt>
  - <https://github.com/fktn-k/fkYAML/commits/develop>
- **Sources the enricher read:**
  - <https://github.com/fktn-k/fkYAML>
  - <https://github.com/fktn-k/fkYAML/blob/develop/README.md>
  - <https://github.com/fktn-k/fkYAML/tree/develop/tools/benchmark>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/README.md>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/main.cpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/CMakeLists.txt>
  - <https://github.com/fktn-k/fkYAML/tree/develop/tools/benchmark/cases>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_ubuntu_yml.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_citm_catalog_json.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_citm_catalog_yml.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/node.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/fkyaml_fwd.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/ordered_map.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/input/lexical_analyzer.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/input/input_adapter.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/input/deserializer.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/input/scalar_scanner.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/input/scalar_parser.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/input/position_tracker.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/conversions/scalar_conv.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/str_view.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/macros/cpp_config_macros.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/document_metainfo.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/node_property.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/include/fkYAML/detail/exception_safe_allocation.hpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/CMakeLists.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/CHANGELOG.md>
  - <https://github.com/fktn-k/fkYAML/blob/develop/docs/docs/api/macros.md>
  - <https://github.com/fktn-k/fkYAML/blob/develop/docs/docs/migration.md>
  - <https://github.com/fktn-k/fkYAML/blob/develop/docs/docs/api/basic_node/deserialize.md>
  - <https://github.com/fktn-k/fkYAML/blob/develop/.github/workflows/ubuntu.yml>
  - <https://github.com/fktn-k/fkYAML/releases>
  - <https://github.com/fktn-k/fkYAML/commits/develop>
  - <https://github.com/fktn-k/fkYAML/issues>
  - <https://github.com/fktn-k/fkYAML/issues/536>
  - <https://github.com/fktn-k/fkYAML/issues/546>
  - <https://github.com/fktn-k/fkYAML/issues/548>
  - <https://github.com/fktn-k/fkYAML/pull/448>
  - <https://github.com/fktn-k/fkYAML/pull/409>
  - <https://github.com/fktn-k/fkYAML/pull/356>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/fktn-k/fkyaml`) · [data/wave4/enrich/raw/github_com_fktn_k_fkyaml.json](../../../data/wave4/enrich/raw/github_com_fktn_k_fkyaml.json) (enrichment confidence 0.85)

</details>
