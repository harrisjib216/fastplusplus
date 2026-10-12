# Parshred

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `AGPL-3.0-or-later` · 🟢 active

> C++20 SIMD XML parser with a flat 32-byte-node DOM; 1.6-3.3x pugixml's read-only parse throughput on synthetic XML.

| | |
|---|---|
| **Beats** | pugixml |
| **Claimed result** | vs pugixml: 2572 vs 1465 MB/s (\~1.76x) at 64KB; 2722 vs 821 MB/s (\~3.3x) at 1MB; 2519 vs 1585 MB/s (\~1.59x) at 16MB; 1678 vs 641 MB/s (\~2.6x) at 64MB; 1317 vs 712 MB/s (\~1.85x) at 128MB (derived from page data); vs RapidXml: within \~5% at 64KB-16MB, 1.5x-1.83x faster at 64MB+ (up to 2.4x observed on other machines per the README) |
| **Workload** | Single-threaded in-memory DOM parse of synthetic generated XML (repeated &lt;item id name status&gt;text&lt;/item&gt; records under &lt;root&gt;) at 64 KB to 128 MB (bench/bench_dom.cpp, median of 50 down to 2 runs per size). Parshred runs fast_dom_parse&lt;FDOM_FASTEST&gt;, which skips text nodes and comments. It is compared with RapidXML 1.13 parse_fastest (also skips data nodes) and pugixml 1.14 load_buffer with parse_minimal (copies the input and still builds PCDATA nodes). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 7640U, 12 threads |
| **Compiler and flags** | GCC 16.1, -O3 (README); bench/bench_dom.cpp header compile line: g++ -std=c++20 -O3 -mavx2; library built with the CMake 'release' preset (-O3 -DNDEBUG plus per-TU SIMD flags); single thread |
| **Adoption** | 0 stars; new project (created July 2026); also ships a PyPI package (pip install parshred) |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/gregghy/parshred) · [benchmark](https://github.com/gregghy/parshred#c-dom-throughput-x86-64-avx2) |

## Verdict

Setup: generated &lt;item id name status&gt;text&lt;/item&gt; records at 64 KB-128 MB, single thread, Ryzen 5 7640U, GCC 16.1 -O3 -mavx2. fast_dom_parse&lt;FDOM_FASTEST&gt;, which builds no text nodes, ran at 1317-2722 MB/s against pugixml 1.14 load_buffer(parse_minimal) at 641-1585 MB/s, a 1.6x-3.3x gap. It matched RapidXML 1.13 parse_fastest within \~5% up to 16 MB and was 1.5-1.8x faster at 64-128 MB. These are first-party numbers, and pugixml copies the buffer and still builds PCDATA nodes, so the pugixml ratio overstates a same-work comparison.

## Use it when

- Read-only extraction of element structure and attributes (not text) from trusted, well-formed UTF-8 XML, which is exactly the FDOM_FASTEST shape that was benchmarked
- Large documents (64-128 MB) on x86-64 with AVX2, where the README shows 1.5-1.8x over RapidXML and 1.85-2.6x over pugixml
- Replacing a pugixml load_buffer + walk used only for reading, when you can adopt an index-based API with string_view results and keep the input buffer alive
- Python batch jobs over trusted XML that need more than lxml's roughly 90-106 MB/s (README reports 527-575 MB/s), provided raw, entity-undecoded text is acceptable
- Open-source projects already under AGPL-3.0-or-later, or teams willing to buy the commercial license

## Skip it when

- Untrusted or possibly malformed input: neither fast_dom_parse nor dom_parse checks that end tags match or reports parse errors. The project's own W3C run shows 928 of 1383 not-wf cases wrongly accepted (SAX path)
- Closed-source products or SaaS without a paid license: AGPL-3.0 §13 network-use copyleft, whereas pugixml (MIT) and RapidXML are permissive
- Files of 64 KB-16 MB where you already use RapidXML: Parshred's own table shows parity within \~5% there, and RapidXML is header-only
- Needs beyond read-only DOM: editing the tree in place, pugixml's full XPath 1.0 (ancestor/preceding axes and variables are missing), namespace-aware DOM/XPath, or UTF-16/Latin-1 input (UTF-8 only)
- Workloads that need production maturity: single author, 0 stars, and all code landed 2026-07-11 to 07-29 with no commits since. The weekly fuzz job has failed twice in fuzz_xpath (out-of-memory in xpath::eval_step and UBSan float-to-integer overflow in xpath.hpp)

## How it is fast

It makes a single pass over the input. AVX2 32-byte compare+movemask+ctz scans (_mm256_cmpeq_epi8/_mm256_movemask_epi8) jump to the next '&lt;', closing quote or comment/CDATA end, and names are read with a scalar lookup table. Nodes are 32-byte structs written in order into one malloc'd array, which starts at len/35 nodes and doubles with realloc. They are linked by uint32 indices, not pointers, and names and attribute values stay as pointers or offsets into the input (zero-copy). The benchmarked FDOM_FASTEST mode also skips building text nodes. The parser never matches end-tag names or reports errors, so it does less work than pugixml. The author puts the 64 MB+ gap over RapidXML down to RapidXML's per-node allocation versus this one flat array.

## Compared with alternatives

Pick it over RapidXml when documents are 64 MB or larger (1.5-1.8x in its own table) or when you want XPath and Python bindings, and AGPL or a commercial license is acceptable; below 16 MB, RapidXml is at parity, header-only and permissively licensed. Against libsimdxml (about 1.2-1.25x over pugixml on an old i7) it claims a bigger pugixml margin, but on different hardware and a synthetic workload. Use SpeedyXml instead for measured real-world streaming.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime (vcpkg.json lists none); GoogleTest and Google Benchmark are fetched only for tests/benchmarks; pybind11 only for the Python module |
| **Minimum toolchain** | C++20; README: GCC 12+, Clang 15+, MSVC 2022+; CMake 3.20+ (CI builds GCC 13, Clang 17, AppleClang on macos-14, MSVC 2022) |
| **Platforms** | x86-64 (README says SSE4.2 minimum, but FastDOM's SIMD needs your own TU compiled with -mavx2) and aarch64 (NEON helpers exist but are not called by the FastDOM/SAX paths checked, so scalar there); Linux, macOS, Windows |
| **Thread safety** | not documented. fast_dom_parse keeps its state on the stack and in the returned FastDom, so separate parses on separate threads look independent; MmapReader is documented as not thread-safe |
| **Drop-in for the baseline** | no |

## Gotchas

- The parsers lose data silently. fast_dom_parse drops CDATA sections entirely and leaves entities undecoded unless you pass FDOM_NORMALIZE. value_len is a uint16, so values over 65535 bytes are truncated. Nesting beyond 255 levels (64 for dom_parse) quietly corrupts the tree, even though conformance.md claims dom_parse throws at depth 512. The Python binding uses fast_dom_parse&lt;0&gt;, so Python users hit the CDATA and entity behaviour too.
- fast_dom_parse chooses SIMD at compile time: simd_utils.hpp is gated on #ifdef __AVX2__, so a TU built without -mavx2/-march gets scalar byte loops. The CPUID runtime dispatch covers only the simd_scan backends, and the PyPI binding module is built with plain -O3.
- FastDom stores raw pointers and 32-bit offsets into the caller's buffer, so the buffer must outlive the DOM. Offsets and indices are uint32, which implies a 4 GiB input limit (not documented). Parent lookup (XPath '..') scans the whole node array, O(n).
- parallel_fast_dom_parse splits only where nesting depth returns to 0, so a normal single-root document falls back to serial. The README's FetchContent snippet pins v0.1.0, but the latest tag is v0.1.6. Some docs are stale: performance.md has older numbers, and the migration guide describes an 80-byte XmlNode with a parent pointer, but the code has a 64-byte node with no parent.

## Known shortcomings

- Its fast DOM parsers do not validate: end-tag mismatches are not reported (the project's own W3C run accepts 928 of 1,383 not-well-formed cases), fast_dom_parse drops CDATA and leaves entities undecoded unless FDOM_NORMALIZE is passed, values over 65,535 bytes are truncated, and deep nesting silently produces a wrong tree. The SIMD path needs the caller built with -mavx2.

## Caveats and trade-offs

This is a first-party benchmark, but the code, compiler, flags and CPU are all public or stated. No third party has reproduced it yet. The workload is one synthetic, homogeneous XML shape, not real-world files. The pugixml comparison is not like for like. Parshred's FDOM_FASTEST mode skips text nodes, while pugixml builds PCDATA nodes and load_buffer copies the input (load_buffer_inplace would not). The pugixml ratios (1.6x to 3.3x) therefore overstate a same-work comparison somewhat. bench_dom.cpp is not part of the CMake build; it is compiled by hand. docs/performance.md still shows older approximate numbers on unnamed hardware (1.3-1.5x vs RapidXML, 2-2.5x vs pugixml) that contradict the README. The license is AGPL-3.0-or-later (strong network copyleft), with a paid commercial license on offer. The project is very new (created 2026-07-11) and has 0 stars.

AGPL-3.0 is a strong copyleft license (network-use/source-disclosure clause), a much bigger adoption barrier than pugixml's or RapidXml's permissive licenses; 32-byte compact DOM node format trades some API flexibility for \~3x lower memory than traditional per-node allocation; author explicitly states the large-file speedup ratio is machine-dependent (observed 1.5x-2.4x range)

## Maintenance

Young single-author project (created 2026-07-11, last commit 2026-07-29 at v0.1.6, also on PyPI, 0 stars, no issues filed). It is usable under AGPL-3.0-or-later or a paid commercial license, not permissively.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README 'C++ DOM throughput (x86-64, AVX2)' table gives Parshred FastDOM at 2572/2722/2519/1678/1317 MB/s and pugixml at 1465/821/1585/641/712 MB/s, measured on a stated Ryzen 5 7640U with GCC 16.1 -O3 (single thread). The benchmark code is public (bench/bench_dom.cpp, whose header gives the compile line g++ -std=c++20 -O3 -mavx2 against RapidXML 1.13 and pugixml 1.14). The library is built with the CMake release preset (-O3 -DNDEBUG).
- **Verifier notes:** All README numbers and the derived pugixml ratios check out, as does the RapidXML statement (within \~5% up to 16 MB, 1.52-1.83x at 64 MB and above, and 'up to 2.4x' on other machines). The DOM_FASTEST in-situ run earlier in bench_dom does not mutate the shared buffer (make_insitu_sv writes nothing), so the later RapidXML and pugixml runs are not affected. The license was tightened to AGPL-3.0-or-later per the README and pyproject; it is OSI-approved, so usability stays copyable.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gregghy/parshred#c-dom-throughput-x86-64-avx2>
  - <https://github.com/gregghy/parshred>
  - <https://github.com/gregghy/parshred/blob/main/bench/bench_dom.cpp>
  - <https://github.com/gregghy/parshred/blob/main/bench/CMakeLists.txt>
  - <https://github.com/gregghy/parshred/blob/main/docs/performance.md>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/dom_fast.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/dom_parser.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/dom_parser_impl.hpp>
  - <https://github.com/gregghy/parshred/blob/main/CMakePresets.json>
  - <https://github.com/gregghy/parshred/blob/main/CMakeLists.txt>
  - <https://github.com/gregghy/parshred/blob/main/src/CMakeLists.txt>
  - <https://github.com/gregghy/parshred/blob/main/LICENSE>
  - <https://github.com/gregghy/parshred/blob/main/pyproject.toml>
  - <https://github.com/gregghy/parshred/commit/151888c3>
  - <https://github.com/gregghy/parshred/commits/main>
- **Sources the enricher read:**
  - <https://github.com/gregghy/parshred>
  - <https://github.com/gregghy/parshred#c-dom-throughput-x86-64-avx2>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/dom_fast.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/dom_parser.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/dom_parser_impl.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/dom.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/parshred.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/simd_utils.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/simd_neon.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/platform.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/fast_sax_impl.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/tokenizer.hpp>
  - <https://github.com/gregghy/parshred/blob/main/include/parshred/pull_parser.hpp>
  - <https://github.com/gregghy/parshred/blob/main/src/simd_scanner.cpp>
  - <https://github.com/gregghy/parshred/blob/main/src/fast_sax.cpp>
  - <https://github.com/gregghy/parshred/blob/main/src/tokenizer.cpp>
  - <https://github.com/gregghy/parshred/blob/main/src/simd/scanner_scalar.cpp>
  - <https://github.com/gregghy/parshred/blob/main/src/CMakeLists.txt>
  - <https://github.com/gregghy/parshred/blob/main/CMakeLists.txt>
  - <https://github.com/gregghy/parshred/blob/main/CMakePresets.json>
  - <https://github.com/gregghy/parshred/blob/main/vcpkg.json>
  - <https://github.com/gregghy/parshred/blob/main/CHANGELOG.md>
  - <https://github.com/gregghy/parshred/blob/main/COMMERCIAL_LICENSE.md>
  - <https://github.com/gregghy/parshred/blob/main/docs/performance.md>
  - <https://github.com/gregghy/parshred/blob/main/docs/conformance.md>
  - <https://github.com/gregghy/parshred/blob/main/docs/api_reference.md>
  - <https://github.com/gregghy/parshred/blob/main/docs/migration.md>
  - <https://github.com/gregghy/parshred/blob/main/bench/bench_dom.cpp>
  - <https://github.com/gregghy/parshred/blob/main/tests/test_security.cpp>
  - <https://github.com/gregghy/parshred/blob/main/python/parshred_py.cpp>
  - <https://github.com/gregghy/parshred/blob/main/python/bindings.cpp>
  - <https://github.com/gregghy/parshred/blob/main/python/CMakeLists.txt>
  - <https://github.com/gregghy/parshred/blob/main/.github/workflows/ci.yml>
  - <https://github.com/gregghy/parshred/actions>
  - <https://github.com/gregghy/parshred/actions/runs/35497528574>
  - <https://github.com/gregghy/parshred/actions/runs/32614690279>
  - <https://github.com/gregghy/parshred/commits/main>
  - <https://github.com/gregghy/parshred/commit/b964336a>
  - <https://github.com/gregghy/parshred/compare/v0.1.0...v0.1.6>
  - <https://github.com/gregghy/parshred/tags>
  - <https://github.com/gregghy/parshred/releases>
  - <https://github.com/gregghy/parshred/issues>
  - <https://pypi.org/pypi/parshred/json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/gregghy/parshred`) · [data/wave4/enrich/raw/github_com_gregghy_parshred.json](../../../data/wave4/enrich/raw/github_com_gregghy_parshred.json) (enrichment confidence 0.78)

</details>
