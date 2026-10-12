# ser20

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> C++20 fork of cereal with a buffered binary archive: 1.3-2.1x faster than cereal, 1.1-2.8x than Boost, on small-field data.

| | |
|---|---|
| **Beats** | cereal, boost::serialization |
| **Claimed result** | README: "Ser20 is sometimes two times as fast as cereal and boost::serialization in binary serialization". Raw values in scripts/benchmark_plot.py (lower is faster), shown as ser20 vs cereal vs boost. PoDStruct: save 37.79 vs 75.25 vs 102.78, load 32.00 vs 58.57 vs 82.66. Map(PoDStruct): save 2.14 vs 4.48 vs 5.93, load 3.51 vs 4.58 vs 9.46. String: save 1.36 vs 2.51 vs 2.10, load 3.09 vs 4.07 vs 3.42. Derived from page data: about 1.3-2.1x faster than cereal and 1.1-2.8x faster than boost in these three categories. vector&lt;double&gt; and vector&lt;uint8_t&gt; are at parity. PoDChild load is slightly slower than cereal (26.27 vs 24.64). |
| **Workload** | Binary archive save to std::ostringstream and load from std::istringstream, 100-run averages, in sandbox/performance.cpp. That file is built by sandbox/CMakeLists.txt when Boost is found, not by doc/CMakeLists.txt. Data sets: vector&lt;double&gt; (1 to 1M), vector&lt;uint8_t&gt; (64M), vector&lt;PoDStruct&gt; (1 to 2M), vector&lt;PoDChild&gt; with a virtual base (1024, 32K), strings (200K to 20M chars), vector&lt;string&gt; (512 to 128K) and map&lt;string,PoDStruct&gt; (1024, 64K). The chart shows 6 categories, and the sizes behind each bar are not documented. |
| **Metric** | throughput |
| **Adoption** | 34 stars |
| **Last commit** | 2025-06-25 |
| **Links** | [repository](https://github.com/royjacobson/ser20) · [benchmark](https://github.com/royjacobson/ser20#performance) |

## Verdict

The repo's own sandbox/performance.cpp saves and loads the same data with Boost, cereal and ser20 binary archives to std::ostringstream/istringstream, averaged over 100 interleaved runs. The committed numbers show ser20 about 2.0x faster on save and 1.8x on load than cereal for vector&lt;PoDStruct&gt;, 2.1x/1.3x for map&lt;string,PoDStruct&gt;, and 1.85x/1.3x for the 'String' bar. That bar is most likely the vector&lt;string&gt; test, because a duplicate dict key overwrote the single-string entry, which was at parity. Against Boost the range is 1.1-2.8x, and bulk arithmetic vectors are at parity. Compiler, flags, CPU, library versions and the data size behind each bar are not stated, and no one has reproduced the results independently.

## Use it when

- An existing cereal codebase on BinaryArchive where profiles show time in many small field writes: vectors of structs, map&lt;string, struct&gt;, many short strings. The repo's numbers show 1.8-2.1x faster saves and 1.3-1.8x faster loads than cereal on these.
- Moving off boost::serialization to a cereal-style API. ser20 keeps cereal's Boost transition layer (operator&, is_loading/is_saving) and beat Boost 1.1-2.8x in the chart's struct, map and string categories.
- The project is already on C++20 (GCC 10+, Clang 13+, AppleClang 15+, MSVC VS 2019/2022) and builds with CMake 3.20+ or Bazel bzlmod.
- Saving to or loading from std::ostringstream/istringstream or file streams, where per-call streambuf overhead dominates.
- You care about debug builds. The README claims smaller debug symbols and a better debugging experience because of nodebug/always_inline wrappers, and 25% faster compiles, but gives no data.

## Skip it when

- Bulk arithmetic payloads (vector&lt;double&gt;, vector&lt;uint8_t&gt;, one large std::string): the repo's own numbers show parity with cereal and Boost.
- Types with virtual bases or heavy polymorphism: PoDChild (virtual base) loads were about 7% slower than cereal (26.27 vs 24.64).
- Portable-binary, JSON or XML archives: only BinaryArchive has the buffer. PortableBinaryArchive still calls sputn/sgetn for every value, and no benchmarks exist for the other archives.
- You need top throughput: the author says it is 'by far not the fastest serialization library out there'. It keeps cereal's per-field stream model and only batches it.
- Maturity or untrusted input matter: single maintainer, 34 stars, v0.9.1, no commits since 2025-06-25, no issue tracker activity. Container loads resize() to the size stored in the archive with no bound, so a hostile archive can force huge allocations.

## How it is fast

cereal's BinaryArchive makes one streambuf sputn/sgetn call per primitive, so a vector of structs or a container of short strings pays that per-call stream overhead for every field. ser20's BinaryOutputArchive memcpys writes under 1 KiB into a 4 KiB buffer and flushes it at the end of each top-level archive call; this is write coalescing. BinaryInputArchive reads the stream in 4 KiB chunks and serves small loads from that buffer (read-ahead buffering). Dispatch functions are also marked always_inline + nodebug (SER20_HIDE_FUNCTION). Contiguous arithmetic vectors and single large strings already go out as one bulk write in both libraries, so they gain nothing.

## Compared with alternatives

Pick ser20 when you have cereal-style code, or need cereal features (polymorphic pointers, shared_ptr tracking, versioning, JSON/XML archives), and want a cheap speedup from a rename. For raw speed, bitsery and YAS report 3.5-10x wins over cereal and Boost in third-party suites, and Cista++ and struct_pack are different, much faster designs, but all of them are separate libraries with their own APIs.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | None at runtime. It bundles rapidjson, rapidxml and base64 headers for the JSON/XML archives. Boost.Serialization is needed only for the optional comparison benchmark (SKIP_PERFORMANCE_COMPARISON=OFF). |
| **Minimum toolchain** | C++20 with concepts (C++17 is rejected with #error). CI covers GCC 10/12/14, Clang 13/15/16/18, AppleClang via Xcode 15.4/16.2, and MSVC on windows-2019/2025. Needs CMake 3.20+ or Bazel (bzlmod). |
| **Platforms** | Any platform with a C++20 compiler. CI runs on Ubuntu, macOS and Windows. BinaryArchive uses native endianness; PortableBinaryArchive handles endianness conversion. |
| **Thread safety** | One archive must be used by one thread at a time. Running several archives in parallel is safe only with SER20_THREAD_SAFE=1, which puts mutexes around the global static registries. The CMake THREAD_SAFE option defaults to OFF and is only offered on UNIX. |
| **Drop-in for the baseline** | partial — cereal code is source-compatible after renaming the cereal:: namespace and the CEREAL_\* macros to SER20_\*. JSON/XML class-version fields are written as 'ser20_class_version' instead of 'cereal_class_version'. Binary compatibility with cereal archives is not documented. Boost users get cereal's transition layer but must still port serialize(ar, version) signatures and registration macros. |

## Gotchas

- BinaryInputArchive reads ahead in 4 KiB sgetn chunks and never gives unused bytes back (the destructor is defaulted). After a load, the istream position can be past the end of the archive. Unlike cereal, which reads exactly the bytes it needs, you cannot interleave raw reads or run back-to-back archives on the same stream. On a pipe or socket streambuf, a small load may block until 4 KiB or EOF arrives.
- BinaryOutputArchive holds data in a 4 KiB buffer until the end of each top-level ar(...) call or until destruction. Writes of 1 KiB or more bypass the buffer. Stream write or read failures throw ser20::Exception.
- Version numbers disagree: the CMake project says 1.4.0 (used for the find_package SameMajorVersion check), version.hpp says 0.9.1 and MODULE.bazel says 0.9.0. version.hpp warns that compatibility is not guaranteed across versions.
- The C++20 module file (module/ser20.cppm) is marked experimental and is not wired into the CMake build. The README's '15% smaller' and 'compile up to 25% faster' claims have no published data.

## Known shortcomings

- The speedup over cereal only applies to the plain BinaryArchive (4 KiB write and read-ahead buffers); PortableBinaryArchive is unchanged and JSON/XML were not benchmarked. The read-ahead never returns unused bytes, so raw reads or back-to-back archives on one stream break, and pipe/socket reads can block. The plotted 'String' bar is likely vector&lt;string&gt;; a single large string is at parity. Not a pure rename: JSON/XML write 'ser20_class_version' and macros become SER20_\*. First-party benchmark with no compiler, flags or CPU stated.

## Caveats and trade-offs

The chart plots time normalized to cereal; lower is faster. Its raw values are in scripts/benchmark_plot.py. That dict has two "String" keys, so the second entry (probably the Vector(String) test) overwrites the first (a parity entry). No compiler, flags, CPU, or Boost/cereal versions are stated. The gain is attributed to buffering small ostream reads and writes. The README claims about '15% smaller' and 'compile up to 25% faster' have no data. GitHub does not mark the repo as a fork (fork:false), but the README calls it a C++20 fork of cereal. It is a small single-maintainer project (34 stars, 5 forks).

Requires C++20 concepts (GCC 10-14, Clang 13-18, MSVC v16/17, AppleClang 15-16); not header-only, needs a separate compile step; API is cereal-compatible except for a namespace change, so migrating existing cereal/boost::serialization code is low-effort; author states it is 'by far not the fastest serialization library out there'.

## Maintenance

Stale single-maintainer project (v0.9.1, last commit 2025-06-25, 34 stars, no issues filed). It is BSD-3-Clause and small (two .cpp files plus cereal-derived headers), so it is easy to vendor. Upstream cereal (4.7k stars) is still being pushed to as of 2026-03.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Evidence is first-party only. The README chart (doc/benchmarks.png) and its raw timings in scripts/benchmark_plot.py come from the public benchmark sandbox/performance.cpp, which compares ser20, cereal and boost::serialization binary archives. No compiler, flags or CPU is stated, and there is no independent suite.
- **Verifier notes:** The claim and the chart are accurate. The workload path was wrong: the benchmark is sandbox/performance.cpp, not something built by doc/CMakeLists.txt. The chart is labeled 'Relative performance: load/save' and its raw numbers are in the repo, so the record's 'unlabeled chart' caveat is fixed. Metadata checks OK: BSD-3-Clause, 34 stars, not archived, last commit 2025-06-25, stale.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/royjacobson/ser20>
  - <https://github.com/royjacobson/ser20#performance>
  - <https://github.com/royjacobson/ser20/blob/main/doc/benchmarks.png>
  - <https://github.com/royjacobson/ser20/blob/main/sandbox/performance.cpp>
  - <https://github.com/royjacobson/ser20/blob/main/sandbox/CMakeLists.txt>
  - <https://github.com/royjacobson/ser20/blob/main/scripts/benchmark_plot.py>
  - <https://github.com/royjacobson/ser20/blob/main/doc/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/royjacobson/ser20>
  - <https://github.com/royjacobson/ser20#performance>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/archives/binary.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/archives/portable_binary.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/ser20.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/macros.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/version.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/types/vector.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/types/polymorphic.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/include/ser20/details/static_object.hpp>
  - <https://github.com/royjacobson/ser20/blob/main/src/ser20.cpp>
  - <https://github.com/royjacobson/ser20/blob/main/src/polymorphic_impl.cpp>
  - <https://github.com/royjacobson/ser20/blob/main/CMakeLists.txt>
  - <https://github.com/royjacobson/ser20/blob/main/BUILD>
  - <https://github.com/royjacobson/ser20/blob/main/MODULE.bazel>
  - <https://github.com/royjacobson/ser20/blob/main/module/ser20.cppm>
  - <https://github.com/royjacobson/ser20/blob/main/sandbox/performance.cpp>
  - <https://github.com/royjacobson/ser20/blob/main/sandbox/CMakeLists.txt>
  - <https://github.com/royjacobson/ser20/blob/main/scripts/benchmark_plot.py>
  - <https://github.com/royjacobson/ser20/blob/main/doc/benchmarks.png>
  - <https://github.com/royjacobson/ser20/blob/main/unittests/benchmarks/benchmark.cpp>
  - <https://github.com/royjacobson/ser20/blob/main/unittests/binary_archive.cpp>
  - <https://github.com/royjacobson/ser20/blob/main/unittests/CMakeLists.txt>
  - <https://github.com/royjacobson/ser20/blob/main/.github/workflows/ci-lin.yml>
  - <https://github.com/royjacobson/ser20/blob/main/.github/workflows/ci-macos.yml>
  - <https://github.com/royjacobson/ser20/blob/main/.github/workflows/ci-win.yml>
  - <https://github.com/royjacobson/ser20/issues>
  - <https://github.com/royjacobson/ser20/pulls>
  - <https://github.com/royjacobson/ser20/commits/main>
  - <https://github.com/royjacobson/ser20/releases>
  - <https://github.com/USCiLab/cereal>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/archives/binary.hpp>
  - <https://github.com/USCiLab/cereal/blob/master/include/cereal/cereal.hpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/royjacobson/ser20`) · [data/wave4/enrich/raw/github_com_royjacobson_ser20.json](../../../data/wave4/enrich/raw/github_com_royjacobson_ser20.json) (enrichment confidence 0.6)

</details>
