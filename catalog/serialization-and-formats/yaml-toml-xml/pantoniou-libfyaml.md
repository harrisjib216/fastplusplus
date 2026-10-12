# libfyaml

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Full-spec YAML 1.2/JSON parser and emitter in C, with 3.0-3.6x yaml-cpp's parse throughput in fkYAML's benchmark.

| | |
|---|---|
| **Beats** | yaml-cpp |
| **Claimed result** | 35.98 MiB/s vs yaml-cpp's 10.12 MiB/s (\~3.6x) on ubuntu.yml; 50.71 vs 16.67 MiB/s (\~3.0x) on citm_catalog.json; 21.94 vs 7.31 MiB/s (\~3.0x) on citm_catalog.yml (derived from page data; slower than both rapidyaml and fkYAML in the same test) |
| **Workload** | fkYAML's third-party Google Benchmark harness (tools/benchmark/main.cpp) calls fy_document_build_from_string with default config on in-memory ubuntu.yml, citm_catalog.json and citm_catalog.yml, reporting bytes/sec. It compares libfyaml v1.0.0-beta1 against yaml-cpp 0.9.0 (plus fkYAML and rapidyaml v0.16.0) on the same machine and build. Results were committed 2026-09-07, one run per file. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800H @3.20GHz, Ubuntu 22.04 (WSL2) |
| **Compiler and flags** | g++ 11.4.0 (the only compiler the fkYAML README names; libfyaml's C sources use the configured C compiler), CMake Release; libfyaml is built as a static library via FetchContent, and its CMakeLists adds -O2 for non-Debug builds |
| **Adoption** | 346 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/pantoniou/libfyaml) · [benchmark](https://github.com/fktn-k/fkYAML#benchmarking) |

## Verdict

fkYAML's author, a third party, benchmarked this with Google Benchmark on a Ryzen 7 5800H under WSL2, using g++ 11.4.0 in a Release build with libfyaml built static at -O2. The timed call was libfyaml v1.0.0-beta1's fy_document_build_from_string with the default config against yaml-cpp 0.9.0, parsing in-memory ubuntu.yml (about 8.6 KiB, derived from time x throughput), citm_catalog.json and citm_catalog.yml. Results were 35.98 vs 10.12 MiB/s (3.6x), 50.71 vs 16.67 (3.0x) and 21.94 vs 7.31 (3.0x). It was a single run, and libfyaml's documents are never destroyed inside the timed loop while yaml-cpp's teardown is timed, which slightly favors libfyaml.

## Use it when

- C or C++ code that needs full YAML 1.2 conformance (anchors, tags, complex keys, multi-document streams, JSON input) and wants about 3x yaml-cpp's DOM-parse throughput on small-to-medium documents.
- Round-trip tools such as config editors, formatters and linters that must keep comments (FYPCF_KEEP_COMMENTS), original styles (FYPCF_KEEP_STYLE) and source markers, then re-emit with controlled indentation and quoting.
- Large or streaming inputs where you do not want a tree at all: the event API walks the document without building one.
- Processes that re-read the same large, rarely changing YAML/JSON files at every startup: the opt-in cache (FYPCF_ENABLE_CACHE) skips re-parsing unchanged content. The docs say it helps little for tiny or volatile inputs.
- C codebases that want YAML decoded straight into native C structs (reflection API) or into a Python-like immutable value model (fy_generic).

## Skip it when

- When raw parse speed is the point. In the same fkYAML benchmark, fkYAML was 2.1-2.6x faster than libfyaml and rapidyaml 2.2-4.2x faster (for example 132-151 vs 36 MiB/s on ubuntu.yml). The project's own docs say it puts correctness ahead of raw speed.
- Untrusted input on the v1.0.0-beta1 tag. Fuzzing since August 2026 produced dozens of now-closed reports: use-after-free, heap overflows, exponential-time alias/merge-key resolution (#347, #400) and quadratic mapping builds (#394). The fixes are on master, and no release has been tagged since beta1 (2026-08-13).
- When you want idiomatic C++. There is no C++ wrapper, RAII or exceptions, and libfyaml-cpp.h is a C-preprocessor macro kit, not a C++ API. The generic layer's macros rely on C11 _Generic and GNU statement expressions, so treat generics and reflection as C-only.
- MSVC (cl) builds that need generics, reflection or the parse cache. These need statement expressions, which only GCC, Clang and clang-cl provide, and the generic layer is also little-endian only.
- Sharing one document across threads. The docs say the document subsystem is not designed for multithreaded processing; only the immutable fy_generic values can be read-shared without locking.

## How it is fast

The scanner is zero-copy. Tokens are 'atoms' holding start/end marks into the input: files are mmap'd, in-memory strings are referenced without copying, and escape/fold processing happens only when someone asks for the text. Freed tokens, events and parser-state objects go onto per-parser recycling lists instead of back to malloc. Each mapping node can also carry an xxHash32-keyed hash table (an 'accelerator'), which makes key lookups and duplicate-key checks O(1) instead of a list scan. The core scanner has no SIMD: the SSE/AVX/NEON code in the tree belongs to the bundled BLAKE3 hasher, which keys the opt-in transparent parse cache. On a cache hit, that cache loads a serialized generic arena instead of re-parsing.

## Compared with alternatives

Pick libfyaml over fkYAML, rapidyaml or PipeYAML when you are writing C, or when you need its documented extras: comment- and style-preserving round-trips, a libyaml-style event API, YPATH queries, YAML&lt;-&gt;C-struct reflection, or the on-disk parse cache. For plain fast parsing into a tree from C++, the same benchmark shows fkYAML at 2.1-2.6x and rapidyaml at 2.2-4.2x libfyaml's throughput.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake or Autotools; BUILD_SHARED_LIBS defaults ON; find_package(libfyaml) and pkg-config supported) |
| **Dependencies** | pthreads on non-Windows (required); bundled xxHash and BLAKE3; optional libclang/LLVM to author reflection metadata from C headers (not needed at runtime with packed blobs); optional libyaml for a compatibility mode |
| **Minimum toolchain** | C11 compiler (CMake prefers gnu2x/c2x and falls back to gnu11); CMake 3.14+. MSVC needs /std:c17 plus /experimental:c11atomics. Generics, reflection and the parse cache need GNU statement expressions (GCC/Clang/clang-cl). libclang-based reflection needs CMake newer than 3.27. |
| **Platforms** | Linux, macOS, Windows (MSVC, clang-cl, MinGW; CI covers ubuntu, macos, windows incl. windows-11-arm); x86-64, x86, arm64, arm. The core parser needs no SIMD. The generic layer is little-endian only; the mremap allocator is Linux-specific (with mmap/malloc fallbacks). |
| **Thread safety** | The document API is not designed for multithreaded processing (doc/intro.rst). fy_generic values are immutable and read-shareable without locks. The library ships a thread pool for parallel generic transforms. The rules for confining a parser or document to one thread are not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- In v1.0.0-beta1, the tag that was benchmarked, the default (iterative) document builder never set up the mapping accelerators, so duplicate-key checks are quadratic. Issue #394 measured 26.4 s for a 20,000-key flat mapping with the default config vs 0.05 s with FYPCF_PREFER_RECURSIVE. It is fixed on master (commit 4a9346d, 2026-09-23) but not yet in a tagged release.
- Input strings are referenced, not copied. Memory inputs keep the caller's pointer, and fy_parser_set_string's doc says the string must not go out of scope while the parser is active. To hand ownership to the document, use fy_document_build_from_malloc_string. fy_node_get_scalar returns a pointer and length that is not NUL-terminated; fy_node_get_scalar0 allocates a terminated copy.
- Aliases and merge keys are not resolved unless you set FYPCF_RESOLVE_DOCUMENT or call fy_document_resolve. Before the September 2026 fixes, resolving crafted merge-key aliases could take exponential time.
- From C++ with Clang/libc++, &lt;libfyaml.h&gt; pulls in &lt;stdatomic.h&gt;, which defines atomic_load and similar names as macros. The project's own C++ test says to include &lt;libfyaml.h&gt; before any STL header that reaches &lt;atomic&gt;, or to keep such headers out of that translation unit.

## Known shortcomings

- The benchmarked tag (v1.0.0-beta1) has a quadratic slowdown on large mappings with the default config (issue #394: 26.4 s for 20,000 keys); it is fixed on master but no newer release is tagged.

## Caveats and trade-offs

The benchmark was run by a third party (fkYAML's author, a competing library), not by libfyaml. libfyaml has no speed comparison of its own. The harness never calls fy_document_destroy inside the timed loop, so libfyaml's teardown is excluded while yaml-cpp's is timed. That slightly favors libfyaml, and the leaked documents also accumulate across iterations. libfyaml's opt-in transparent parse cache is not enabled with the default config used here. The runs are single Google Benchmark runs under WSL2, and no one has reproduced them independently. libfyaml is slower than both rapidyaml and fkYAML in this test.

C library with a C API (not C++-idiomatic); implements the full YAML spec and passes the official YAML testsuite; usable directly from C++ as a C library per the assignment's language filter

## Maintenance

Actively maintained by its original author (commits through 2026-09-23, with a burst of fuzzing fixes in September 2026) and MIT-licensed, but 1.0 is still in beta, so build from a recent master commit rather than the v1.0.0-beta1 tag if you parse untrusted or large-mapping input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The fkYAML README Benchmarking tables have libfyaml rows at 35.9803/50.7076/21.9363 Mi/s against yaml-cpp at 10.122/16.6685/7.30883 Mi/s. The raw outputs are in fkYAML tools/benchmark/results. The benchmark code is public (fkYAML tools/benchmark/main.cpp and CMakeLists.txt pin libfyaml v1.0.0-beta1 and yaml-cpp 0.9.0 in a Release build; libfyaml's own CMakeLists adds -O2 for non-Debug builds). The compiler (g++ 11.4.0) and CPU (Ryzen 7 5800H) are stated, and third-party runs qualify for A.
- **Verifier notes:** The comparison against yaml-cpp and all three derived ratios (\~3.6x, \~3.0x, \~3.0x) check out. The benchmark_url was changed to the fkYAML README section that actually contains the numbers. last_commit was the pushed_at date; the newest commit on master is 2026-09-23.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/README.md>
  - <https://github.com/fktn-k/fkYAML/blob/develop/README.md>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/main.cpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/CMakeLists.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_ubuntu_yml.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_citm_catalog_json.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_citm_catalog_yml.txt>
  - <https://github.com/pantoniou/libfyaml>
  - <https://github.com/pantoniou/libfyaml/blob/master/README.md>
  - <https://github.com/pantoniou/libfyaml/commits/master>
  - <https://github.com/pantoniou/libfyaml/blob/v1.0.0-beta1/CMakeLists.txt>
  - <https://github.com/pantoniou/libfyaml/blob/v1.0.0-beta1/doc/transparent-cache.rst>
- **Sources the enricher read:**
  - <https://github.com/pantoniou/libfyaml>
  - <https://github.com/pantoniou/libfyaml/blob/master/README.md>
  - <https://github.com/pantoniou/libfyaml/blob/master/include/libfyaml/libfyaml-core.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/include/libfyaml/libfyaml-cpp.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/include/libfyaml/libfyaml-allocator.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/include/libfyaml/libfyaml-generic.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/include/libfyaml.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-accel.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-accel.c>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-atom.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-atom.c>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-input.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-input.c>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-parse.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-parse.c>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-doc.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-doc.c>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/lib/fy-cache.c>
  - <https://github.com/pantoniou/libfyaml/blob/v1.0.0-beta1/src/lib/fy-doc.c>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/util/fy-utf8.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/src/util/fy-ctype.h>
  - <https://github.com/pantoniou/libfyaml/blob/master/doc/intro.rst>
  - <https://github.com/pantoniou/libfyaml/blob/master/doc/transparent-cache.rst>
  - <https://github.com/pantoniou/libfyaml/blob/master/doc/windows-support.txt>
  - <https://github.com/pantoniou/libfyaml/blob/master/doc/libfyaml-core.rst>
  - <https://github.com/pantoniou/libfyaml/blob/master/CMakeLists.txt>
  - <https://github.com/pantoniou/libfyaml/blob/master/CHANGELOG.md>
  - <https://github.com/pantoniou/libfyaml/blob/master/test/libfyaml-test-cpp-include-tu.cpp>
  - <https://github.com/pantoniou/libfyaml/blob/master/.github/workflows/ci.yaml>
  - <https://github.com/pantoniou/libfyaml/blob/master/.github/workflows/cmake.yaml>
  - <https://github.com/pantoniou/libfyaml/issues?q=is%3Aissue>
  - <https://github.com/pantoniou/libfyaml/issues/394>
  - <https://github.com/pantoniou/libfyaml/issues/347>
  - <https://github.com/pantoniou/libfyaml/commit/4a9346dbaa>
  - <https://github.com/pantoniou/libfyaml/commits/master>
  - <https://github.com/pantoniou/libfyaml/releases>
  - <https://github.com/pantoniou/libfyaml/tags>
  - <https://github.com/pantoniou/libfyaml/compare/v1.0.0-beta1...bbbdf7d2df4f623b1fe7e6091b0bca598488a098>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=libfyaml>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-88359>
  - <https://github.com/fktn-k/fkYAML#benchmarking>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/main.cpp>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/CMakeLists.txt>
  - <https://github.com/fktn-k/fkYAML/blob/develop/tools/benchmark/results/result_release_ubuntu_yml.txt>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/pantoniou/libfyaml`) · [data/wave4/enrich/raw/github_com_pantoniou_libfyaml.json](../../../data/wave4/enrich/raw/github_com_pantoniou_libfyaml.json) (enrichment confidence 0.82)

</details>
