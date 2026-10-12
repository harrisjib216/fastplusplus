# SerialXML

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++26 reflection-based struct-to-XML writer; author measures \~9.6x lower latency than Boost.Serialization/cereal XML archives.

| | |
|---|---|
| **Beats** | Boost.Serialization, cereal |
| **Claimed result** | 822.085 ns/iter for SerialXML vs 7899.305 ns/iter for Boost.Serialization (\~9.6x, derived from page data) and 7945.590 ns/iter for Cereal (\~9.7x, derived from page data); README prose separately claims '8.3x faster than boost_xml' and '1.9x faster than pugixml', which does not match the table's own numbers for the Boost.Serialization row |
| **Workload** | Struct-to-XML serialization of an Order object (nested Address, vector&lt;LineItem&gt;, vector&lt;int&gt; tags) via to_xml(), 100,000 iterations single-threaded, compared against Boost.Serialization's xml_oarchive, cereal's XMLOutputArchive, and pugixml |
| **Metric** | latency |
| **Hardware** | Single Intel Core 7 240H laptop CPU, 5600 MT/s DDR5 (per README; no further CPU/RAM/OS detail given) |
| **Compiler and flags** | Not stated for the benchmark run. README lists GCC 16.1 as the minimum compiler (the devcontainer image is gcc:16.2.0); CMakePresets 'release-gcc' preset sets CMAKE_BUILD_TYPE=Release (README's install instructions name a nonexistent 'release-gcc-16' preset); CMakeLists adds -freflection with C++26; no explicit -O level in README or CMake files |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/EJainDev/SerialXML) · [benchmark](https://github.com/EJainDev/SerialXML/blob/main/README.md) |

## Verdict

In one first-party run on the author's Intel Core 7 240H laptop (DDR5-5600), with a GCC 16 toolchain and unstated flags, a small Order (id, customer, 3-field address, 3 line items, 4 int tags) was serialized 100,000 times. SerialXML took 822 ns per call, vs 7,899 ns for Boost.Serialization xml_oarchive and 7,946 ns for cereal XMLOutputArchive (\~9.6x), and 1,585 ns for a hand-built pugixml tree (\~1.9x). The outputs are not equivalent (cereal indents by default, and Boost and cereal add archive metadata and go through ostringstream), the harness never checks them, and from reading the source, SerialXML's output for this payload is truncated at the double unit_price element, so its number is not a like-for-like measurement.

## Use it when

- Write-only export of plain structs to XML text (reports, config dumps, service payloads), where annotations on the struct define the schema and nothing needs to read the XML back.
- Latency-sensitive output of small records with integer and short-string fields: the author's Order payload (about 20 fields) took \~0.8 us per call, vs \~7.9 us with Boost or cereal XML archives and \~1.6 us with a hand-built pugixml tree.
- Codebases already on GCC 16.1+ with -freflection, C++26 and CMake 4.3 `import std` that want to drop hand-written serialize() boilerplate.
- Cases where a bad mapping should fail the build: conflicting annotations (attribute+unpack, attribute+cdata, cdata+raw, cdata+iteration and so on) are static_assert errors.

## Skip it when

- You need to parse or round-trip XML. There is no deserializer, so it cannot replace the load side of Boost.Serialization or cereal.
- You use any toolchain other than GCC 16 with reflection (Clang, MSVC, older GCC, pre-C++26 code), or your build cannot consume C++ named modules and experimental `import std`.
- Your data has floating-point child elements, strings of 64+ characters, or special characters near the end of strings at least one SIMD vector long. From reading the current source, these paths truncate, corrupt or leave text unescaped, and the tests do not cover them.
- You need versioning or schema evolution, pointer tracking, polymorphism, or binary or JSON formats. None of these are documented.
- You need something production-grade: one author, 0 stars, no tags or releases (CMake version 0.1.0.0), and a StructuralTuple dependency fetched from the main branch of another 0-star repo.

## How it is fast

C++26 static reflection (P2996 `std::meta::members_of`/`annotations_of` plus `define_static_string`/`define_static_array`) works out every member's tag text, attribute prefix and handling mode at compile time. At runtime this leaves an unrolled `template for` sequence that memcpy's the precomputed tag literals and uses std::to_chars for numbers, all appended into one pre-reserved (4 KB) std::string through resize_and_overwrite. Escaping compares std::simd vectors against the five XML special characters to build a bitmask, sizes the output with popcount, jumps between hits with countr_zero and copies the clean runs with memcpy. There is no DOM, archive object or ostream. In the benchmark, by contrast, each Boost and cereal call builds an std::ostringstream and an archive, and the pugixml call builds a document tree before printing it.

## Compared with alternatives

All catalogued siblings (bitsery, YAS, ser20, Cista++, struct_pack, FBE) are binary serializers benchmarked on binary output. Pick SerialXML only when the output must be XML text, you only ever write it, and you are on GCC 16 reflection; for round-trip, portability across compilers or production maturity, bitsery, YAS, ser20 or cereal itself are safer.

## Integration

| | |
|---|---|
| **Form** | module (C++ named module `serial_xml` compiled into a CMake STATIC library; consumed via FetchContent or cmake --install + find_package(SerialXML)) |
| **Dependencies** | StructuralTuple (EJainDev, MIT; found with find_package or fetched from its main branch with FetchContent); the standard library module (`import std`). Benchmarks, built by default, also need Boost.Serialization, cereal and pugixml v1.16 (fetched); tests need GoogleTest. |
| **Minimum toolchain** | C++26 with -freflection; GCC 16.1+ (CI uses gcc:16.2.0); CMake 4.3+ with experimental import std (CMAKE_CXX_MODULE_STD); the presets use Ninja |
| **Platforms** | Not documented. CI only exercises Linux x86-64 with GCC 16.2. Escape scanning uses std::simd at the target's native width, and the code uses std::aligned_alloc. |
| **Thread safety** | Not documented. to_xml works only on local strings plus a thread_local scratch vector, so from reading the code, concurrent calls on different threads look safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Floating-point child elements (from reading the code, not run): in add_child, the floating-point branch returns `combined_size + (ptr - buf)` to resize_and_overwrite without adding original_size. Any float or double emitted as a child element (including inside std::optional or a vector) therefore cuts the whole output down to its first few dozen bytes. Attributes and integers take correct paths. The bug is present both at the benchmark commit (2d679989) and at HEAD, and the benchmark's LineItem::unit_price is exactly such a member.
- Escaping (from reading the code, not run): get_escape_bitmask never checks the last vector-width block of strings that are at least one vector long, because its tail loop runs `simd_size & 7` = 0 times, and for a string exactly one vector long it loads from before the buffer. Separately, copy_with_escapes offsets each 64-bit mask word by `i * 8` instead of `i * 64` and copies at most 63 characters per word. Strings of 64+ characters therefore come out with dropped or duplicated characters and are written past the resized length. The tests only use strings shorter than 40 characters.
- Since 2026-09-05, reflection walks members_of rather than only data members. Any accessible const member function that returns a value and needs no arguments (getters, size(), empty()) is emitted as a child element; use [[=serial_xml::skip]] to suppress it.
- CMake: BUILD_BENCHMARKS and BUILD_EXAMPLES default to ON, so FetchContent consumers must have Boost.Serialization and cereal installed unless they set BUILD_BENCHMARKS=OFF. The README's `release-gcc-16` preset does not exist (the real one is `release-gcc`). -freflection is added through directory-scoped CMAKE_CXX_FLAGS instead of a PUBLIC target option, so consuming targets probably need to add it themselves.

## Known shortcomings

- Benchmark likely invalid (found by reading the source, not run): add_child's floating-point branch drops original_size when resizing, truncating the whole output whenever a float/double child is written, and the benchmark payload has one (LineItem::unit_price) while the harness never checks output. Escaping bugs: the last SIMD block of long strings is never checked, and strings of 64+ characters lose or duplicate characters. Writer only (no parser), unlike the Boost.Serialization and cereal baselines. Needs GCC 16 with -freflection; BUILD_BENCHMARKS defaults ON.

## Caveats and trade-offs

First-party, single-machine, single-run benchmark (100,000 iterations after 1,000 warmup, one steady_clock measurement, no repetitions/variance); compiler version and optimization flags for the run are not stated (only a GCC 16.1 minimum requirement), so it cannot be tier A. README prose claims '8.3x faster than boost_xml', which does not match its own table (7899.305/822.085 = \~9.6x); the 1.9x vs pugixml prose does match. Output formats are not identical: cereal's XMLOutputArchive runs with its default options (indented output) and Boost/cereal/pugixml all build or stream through their own archive/DOM layers, while SerialXML emits a flat string from a compile-time layout. Numbers were published 2026-09-04 and the library code changed afterwards (last commit 2026-09-07). Repo created 2026-07-12, 0 stars, and it depends on GCC 16 C++26 reflection, so adoption and robustness are unproven.

Requires C++26 with an experimental reflection-capable compiler (GCC 16.1+); XML-only serializer (no binary/JSON formats); annotation-driven API (C++26 struct/member annotations) rather than archive-based like Boost.Serialization/cereal; no versioning/schema-evolution support shown; benchmark payload is small/fixed and not representative of all workloads

## Maintenance

Actively developed by one author (repo created 2026-07-12, last commit 2026-09-07, GCC 16.2 CI passing) under MIT, but it has 0 stars, no tags or releases, and correctness gaps in the float and long-string paths, so treat it as experimental and pin a commit if you use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks table gives SerialXML 822.085 ns/iter vs Boost.Serialization 7899.305, Cereal 7945.590, pugixml 1585.212 (code public at benchmarks/xml_serialization_benchmarks.cpp, CPU Intel Core 7 240H stated), but no compiler version or flags are stated for the run (only a GCC 16.1 minimum requirement), so it is first-party with partial methodology: C.
- **Verifier notes:** Numbers and ratios in the record check out (9.61x vs Boost, 9.67x vs cereal, derived from page data). I fixed the compiler/flags description (the preset name in the README does not exist in CMakePresets.json) and the caveat that said the repo was created 'days before' the search; it was created 2026-07-12. Metadata matches: MIT, 0 stars, not a fork, last commit 2026-09-07.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/EJainDev/SerialXML>
  - <https://github.com/EJainDev/SerialXML/blob/main/README.md>
  - <https://github.com/EJainDev/SerialXML/blob/main/benchmarks/xml_serialization_benchmarks.cpp>
  - <https://github.com/EJainDev/SerialXML/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/EJainDev/SerialXML/blob/main/CMakePresets.json>
  - <https://github.com/EJainDev/SerialXML/blob/main/CMakeLists.txt>
  - <https://github.com/EJainDev/SerialXML/blob/main/.devcontainer/Dockerfile>
  - <https://github.com/EJainDev/SerialXML/blob/main/.github/workflows/build-and-test.yml>
  - <https://github.com/EJainDev/SerialXML/commits/main>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/archives/xml.hpp>
- **Sources the enricher read:**
  - <https://github.com/EJainDev/SerialXML>
  - <https://github.com/EJainDev/SerialXML/blob/main/README.md>
  - <https://github.com/EJainDev/SerialXML/blob/main/include/serial_xml.cxx>
  - <https://github.com/EJainDev/SerialXML/blob/2d679989/include/serial_xml.cxx>
  - <https://github.com/EJainDev/SerialXML/blob/main/benchmarks/xml_serialization_benchmarks.cpp>
  - <https://github.com/EJainDev/SerialXML/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/EJainDev/SerialXML/blob/main/tests/test_serial_xml.cpp>
  - <https://github.com/EJainDev/SerialXML/blob/main/tests/CMakeLists.txt>
  - <https://github.com/EJainDev/SerialXML/blob/main/CMakeLists.txt>
  - <https://github.com/EJainDev/SerialXML/blob/main/CMakePresets.json>
  - <https://github.com/EJainDev/SerialXML/blob/main/cmake/SerialXMLConfig.cmake.in>
  - <https://github.com/EJainDev/SerialXML/blob/main/.devcontainer/Dockerfile>
  - <https://github.com/EJainDev/SerialXML/blob/main/.github/workflows/build-and-test.yml>
  - <https://github.com/EJainDev/SerialXML/blob/main/CONTRIBUTING.md>
  - <https://github.com/EJainDev/SerialXML/blob/main/examples/CMakeLists.txt>
  - <https://github.com/EJainDev/SerialXML/blob/main/examples/advanced_mixed.cpp>
  - <https://github.com/EJainDev/SerialXML/blob/main/examples/format_specifiers.cpp>
  - <https://github.com/EJainDev/SerialXML/blob/main/examples/escaping.cpp>
  - <https://github.com/EJainDev/SerialXML/blob/main/examples/stl_containers.cpp>
  - <https://github.com/EJainDev/SerialXML/blob/main/examples/hello_world.cpp>
  - <https://github.com/EJainDev/SerialXML/commits/main>
  - <https://github.com/EJainDev/SerialXML/issues?q=is%3Aissue>
  - <https://github.com/EJainDev/SerialXML/actions>
  - <https://github.com/EJainDev/SerialXML/tags>
  - <https://github.com/EJainDev/StructuralTuple>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/archives/xml.hpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ejaindev/serialxml`) · [data/wave4/enrich/raw/github_com_ejaindev_serialxml.json](../../../data/wave4/enrich/raw/github_com_ejaindev_serialxml.json) (enrichment confidence 0.75)

</details>
