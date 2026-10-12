# OpenEXR

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Reference C/C++ EXR library; faster than TinyEXR's dependency-free build on ZIPS, PXR24 and HTJ2K, not its libdeflate build.

| | |
|---|---|
| **Beats** | TinyEXR v3 (pure-C11 EXR codec by the TinyEXR author). OpenEXR's leads are against TinyEXR's dependency-free in-tree build (DEFLATE=intree, the freestanding/WASM path) and against TinyEXR's HTJ2K codec; TinyEXR's hosted default (DEFLATE=auto, vendored libdeflate 1.25, the same backend OpenEXR uses) matches or beats OpenEXR on ZIP/ZIPS/PXR24. |
| **Claimed result** | Mixed, rival-authored results; current pinned Ryzen 9 3950X single-thread run (README headline charts doc/perf-libdeflate-htj2k-decode.svg and -encode.svg, values also in doc/gen_perf_charts.py), MP/s TinyEXR in-tree vs OpenEXR: decode zip 32.2 vs 30.7 (TinyEXR ahead), zips 17.0 vs 24.4 (OpenEXR 1.44x), pxr24 29.9 vs 43.8 (OpenEXR 1.46x), htj2k256 23.2 vs 29.8 (OpenEXR 1.28x), htj2k32 23.5 vs 27.9 (OpenEXR 1.19x); encode zip 9.6 vs 14 (OpenEXR 1.46x), zips 10.3 vs 14.8 (1.44x), pxr24 9.2 vs 15.8 (1.72x), htj2k256 11 vs 33.2 (3.0x), htj2k32 11.6 vs 31.6 (2.7x) (all ratios derived from page data). Against TinyEXR's default libdeflate build OpenEXR is slower or tied on the deflate family (decode zip 42.4 vs 30.7, zips 31.8 vs 24.4, pxr24 43.7 vs 43.8; encode zip 15.3 vs 14, zips 16.2 vs 14.8, pxr24 16.4 vs 15.8) and keeps only HTJ2K decode (24.1 vs 29.8 and 23.5 vs 27.9, about 1.2x) and PIZ decode (33.8 vs 35.6, about 1.05x). The doc's TL;DR and the README quote older ratios from doc/perf-decode.svg (in-tree decode zip 51.2 vs 62.1 = 1.21x, zips 23.1 vs 48.7 = 2.11x, pxr24 49 vs 88.9 = 1.81x, piz 24.8 vs 67.5 = 2.72x before TinyEXR's PIZ rewrite, htj2k256 24.6 vs 59.7 = 2.43x, htj2k32 27.7 vs 55 = 1.99x; derived from page data); the README's 'HTJ2K \~2.5-3x' decode and '\~4x' encode lines exceed those charts. At 16 threads (in-tree, doc/perf-mt-compare.svg) OpenEXR leads PIZ decode 207.7 vs 110.5 (1.88x) and PXR24 269.5 vs 242.1 (1.11x) while TinyEXR leads RLE/ZIP/ZIPS/B44; with libdeflate at 16 threads TinyEXR leads zip 339.6 vs 226.6 and zips 358.5 vs 151.1. TinyEXR wins uncompressed (1380 vs 389) and RLE (114 vs 45.5) decode outright. |
| **Workload** | Single-threaded, fully in-memory encode and decode of one 660x440 four-channel HALF image (asakusa.exr) per compression codec (none, RLE, ZIP, ZIPS, PIZ, PXR24, B44, HTJ2K), megapixels per second, OpenEXR 4.0-dev versus TinyEXR v3 built dependency-free. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X (16C/32T, Zen2), avx2+f16c, machine idle; secondary Apple M1 (4P+4E, macOS 26) runs |
| **Compiler and flags** | gcc -O3 (doc setup line 'OpenEXR 4.0-dev, gcc -O3'; Makefile builds benchmark/bench_compare.cpp with \$(CXX) -std=c++14 -O3 and bench_tx.c with -O3, TinyEXR library with V3_OPT=-O3 for the headline run although the Makefile default is -O2); compiler version not stated; OpenEXR is linked from an out-of-tree build at \$(HOME)/work/openexr/_build whose commit, CMake build type and OpenJPH version (x86) are not stated. Apple M1 rows: Apple clang 21, OpenJPH 0.27. |
| **Adoption** | 1.9k stars, 703 forks; reference implementation of the EXR format used across film VFX tools |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/AcademySoftwareFoundation/openexr) · [benchmark](https://github.com/syoyo/tinyexr/blob/release/doc/performance-vs-openexr.md) |

## Verdict

TinyEXR's author benchmarked TinyEXR v3 against OpenEXR 4.0-dev in benchmark/bench_compare.cpp: one thread, gcc -O3, Ryzen 9 3950X, the 660x440 four-channel HALF asakusa.exr in memory. Against TinyEXR's in-tree codec, OpenEXR decoded ZIPS at 24.4 vs 17.0 MP/s, PXR24 at 43.8 vs 29.9 and htj2k256 at 29.8 vs 23.2, and encoded htj2k256 about 3x faster (33.2 vs 11). It tied or lost against TinyEXR's default libdeflate build on ZIP/ZIPS/PXR24 and lost uncompressed and RLE decode outright, partly because the harness adds stream copies on the OpenEXR side.

## Use it when

- Production rendering, compositing and texture pipelines that need the full EXR feature set (multi-part, deep, tiled, DWA, HTJ2K, ZSTD) and reference-grade interoperability.
- HTJ2K-compressed EXR, especially writing: in TinyEXR's harness OpenEXR encoded htj2k256 at 33.2 vs 11 MP/s (about 3x) and decoded it at 29.8 vs 23.2 MP/s against TinyEXR's in-tree codec (Ryzen 9 3950X, one thread).
- When the alternative is TinyEXR's dependency-free in-tree build (freestanding or WASM path): OpenEXR decodes ZIPS and PXR24 about 1.45x faster and encodes ZIP/ZIPS/PXR24 1.4-1.7x faster.
- Multithreaded PIZ decode: at 16 threads OpenEXR decoded PIZ at 207.7 vs 110.5 MP/s against in-tree TinyEXR.
- Python users: PyPI OpenEXR 3.5.2 ships wheels for manylinux and musllinux (x86-64, aarch64), macOS (x86-64, arm64, universal2) and Windows (amd64, arm64).

## Skip it when

- Single-thread uncompressed or RLE decode: TinyEXR measured 1380 vs 389 MP/s and 114 vs 45.5 MP/s (part of that gap is harness overhead on the OpenEXR side; see gotchas).
- When TinyEXR's default hosted build (DEFLATE=auto, vendored libdeflate) is an option: it ties or beats OpenEXR on ZIP/ZIPS/PXR24 single-thread (ZIP decode 42.4 vs 30.7 MP/s) and leads the deflate family at 16 threads (ZIPS 358.5 vs 151.1, ZIP 339.6 vs 226.6 MP/s).
- Small-footprint, WASM or freestanding builds: OpenEXR needs CMake 3.14+, a C++17 compiler, Imath, libdeflate, OpenJPH 0.32.0+ and zstd 1.5.0+ (vendored or auto-fetched fallbacks) plus a thread library.
- DWAA/DWAB write-heavy workloads on 3.3 or later: open issues #1915 and #2201 report DWA encode regressions against 3.2.1 (writePixels about 20 ms in 3.4.0 vs about 10 ms in 3.2.1; up to 58% slower HD half writes in a real application).
- Parsing untrusted files on an old release: SECURITY.md lists 38 distinct CVE-2026 IDs and 10 CVE-2025 IDs, mostly decoder memory-safety bugs, patched only in recent 3.2.x-3.5.x releases.

## How it is fast

ZIP, ZIPS and PXR24 go through libdeflate (adopted in 3.2 in place of zlib; vendored 1.26 in 3.5). HTJ2K uses OpenJPH's High-Throughput (ITU-T T.814) block coder, which selects its AVX2 codeblock decoder on x86. PIZ is a wavelet plus Huffman codec. Scanline blocks and tiles are processed in parallel on the IlmThread worker pool (or TBB) sized by setGlobalThreadCount(). DWA has AVX and NEON SIMD paths, per the release notes.

## Compared with alternatives

Pick OpenEXR over OpenJPH when you need EXR containers (it uses OpenJPH internally for HTJ2K and adds every other EXR codec and feature), and over meshoptimizer's vertex codec, which beat OpenEXR ZIP in its own float-image harness, whenever files must stay readable by standard EXR tools.

## Integration

| | |
|---|---|
| **Form** | shared lib (BUILD_SHARED_LIBS defaults ON) or static lib; Python module via PyPI wheels |
| **Dependencies** | Imath 3.1+ (auto-fetched if absent), libdeflate (vendored 1.26 fallback), OpenJPH &gt;= 0.32.0 (vendored fallback), zstd &gt;= 1.5.0 (vendored 1.5.7 fallback), Threads (optional oneTBB) |
| **Minimum toolchain** | C++17 compiler, CMake 3.14+ |
| **Platforms** | Linux, macOS, Windows (including ARM64/ARM64EC fixes); FreeBSD in CI; x86-64 and arm64 |
| **Thread safety** | Documented thread-safe: threads may use distinct file objects concurrently, and accesses to one shared file object are serialized by a mutex. setGlobalThreadCount(n) adds an internal worker pool that parallelizes chunks within a file (0 means work runs in the calling thread). In OpenEXRCore, calls after exr_start_read() are thread-safe. |
| **Drop-in for the baseline** | partial — the file format is interoperable with TinyEXR, but the API is different (C++ FrameBuffer/Slice or OpenEXRCore contexts versus TinyEXR's exr_load/exr_save functions) |

## Gotchas

- Harness flaw in the evidence, biased against OpenEXR: on every timed decode, TinyEXR's benchmark/bench_compare.cpp copies the whole compressed file into a std::istringstream (iss.str(buf)), builds a new InputFile, and zero-fills a new 2.3 MB framebuffer (make_fb assigns 0). Each timed encode also copies its output out through oss.str(). The TinyEXR side decodes from a raw pointer. OpenEXR's own docs say these copies matter for uncompressed reads and offer a memory-mapped IStream instead. TinyEXR's 3.5x NONE and 2.5x RLE decode wins are therefore partly harness overhead, and OpenEXR's leads on compressed codecs are, if anything, understated. TinyEXR's loop also counts failed decodes as timed iterations and only warns on stderr.
- The source doc's numbers drift about 2x between runs, although it claims 'a few % run-to-run'. OpenEXR ZIP decode is 30.7 MP/s in the 2026-08-08 table and headline chart, 58.8 in the LIBDEFLATE=1 line and 62.1 in the older perf-decode chart. HTJ2K encode flips between the table (TinyEXR 18.7 vs 16.4) and the encode chart (OpenEXR 33.2 vs 11). OpenEXR's HTJ2K values are carried over from an older run. OpenEXR was built out of tree at \$(HOME)/work/openexr/_build with no commit stated (OpenEXR's CMake defaults to a Release build when no type is given).
- Chunk granularity drives multithreaded speed: htj2k256 uses 256-scanline chunks, so small images get almost no parallelism; the 3.4.0 notes say htj2k32 is 4-6x faster in some multithreaded cases at slightly larger size. By default each open file tries to use the whole global worker pool.
- Recent release hazards: 3.5.1 fixed a heap buffer overflow in ZSTD deep scanline decoding. Lossy LJ2K files written by 3.5.0 and 3.5.1 lack the transfer-function LUT and should be regenerated (3.5.2 adds a read fallback). Before 3.5.2 the auto-fetched Imath tracked the main branch rather than a pinned tag.

## Known shortcomings

- Downgraded A to B: the rival-authored TinyEXR benchmark doc is mixed and internally inconsistent (absolute MP/s about 2x apart between table and charts, HTJ2K encode flips, M1 table vs chart disagree), OpenEXR HTJ2K values are carried from an older run, and the OpenEXR out-of-tree build commit is unstated. OpenEXR leads only against TinyEXR's in-tree build (about 1.45x ZIPS/PXR24 decode, 1.2-1.3x HTJ2K decode, 1.4-1.7x deflate encode, 2.7-3x HTJ2K encode); against TinyEXR's default libdeflate build it is slower or tied.
- Enricher: TinyEXR's bench_compare.cpp is biased against OpenEXR (every timed decode copies the whole file into a std::istringstream, builds a new InputFile and zero-fills a new 2.3 MB framebuffer, and encode copies output via oss.str(), while TinyEXR decodes from a raw pointer; the TinyEXR loop also counts failed decodes as iterations), so TinyEXR's none 3.5x and RLE 2.5x wins are partly harness and OpenEXR's compressed-codec leads are understated; the doc's OpenEXR ZIP decode drifts 30.7/58.8/62.1 MP/s across runs. Open DWA encode regressions vs 3.2.1 (#1915, #2201: writePixels about 20 ms vs 10 ms); SECURITY.md lists 38 CVE-2026 and 10 CVE-2025 IDs; 3.5.1 ZSTD deep heap overflow; LJ2K files from 3.5.0/3.5.1 need regenerating.

## Caveats and trade-offs

Evidence is a rival project's benchmark (TinyEXR author), not an OpenEXR claim, and it is mixed: OpenEXR is itself the incumbent EXR library and TinyEXR is not a default, so this entry is the reference implementation beating a lightweight alternative, and the doc's net conclusion is that TinyEXR's default hosted build (vendored libdeflate) matches or beats OpenEXR on ZIP/ZIPS/PXR24 single-thread and leads the whole deflate family at 16 threads (zip 339.6 vs 226.6, zips 358.5 vs 151.1 MP/s). OpenEXR's clear wins are HTJ2K (OpenJPH backend) and deflate-family encode/decode versus TinyEXR's dependency-free in-tree codec. The doc is internally inconsistent: the 2026-08-08 'full single-thread numbers' table reports roughly half the absolute MP/s of the charts and README text for both libraries (OpenEXR rle decode 45.5 vs 88.2, b44 86.8 vs 180.2; README uncompressed 2699 vs 789 against the doc's 1384 vs 392), the table shows TinyEXR faster on HTJ2K encode (18.7 vs 16.4) while the headline encode chart shows OpenEXR about 3x faster (33.2 vs 11), and the Apple M1 table (OpenEXR decode zips 60.6 vs 22.2, piz 66.1 vs 28.2) disagrees with the M1 chart data in doc/gen_perf_charts.py (zips 60 vs 56, piz 64 vs 68). The doc's TL;DR and the README quote stale ratios (PIZ 2.7x predates TinyEXR's PIZ rewrite, now 33.8 vs 35.6; README HTJ2K 2.5-3x decode exceeds the chart's 2.43x/1.99x). OpenEXR/OpenJPH HTJ2K values are 'the latest available same-machine baseline', not re-measured in the same run as TinyEXR's 2026-06-13 HTJ2K numbers. OpenEXR is linked from an out-of-tree build (\$(HOME)/work/openexr/_build) with unstated commit and CMake options. One small 660x440 four-channel HALF image (asakusa.exr), which limits thread scaling and makes per-call overhead count. OpenEXR's own release notes (CHANGES.md 3.3, 3.5, per the search record) give only unquantified or self-relative speed claims, no outside baseline; openexr.com not opened.

Heavier than TinyEXR: depends on Imath, a vendored libdeflate, vendored zstd (3.5) and OpenJPH for HTJ2K, with its own internal thread pool. The C core (OpenEXRCore) sits under the C++ API since 3.3.

## Maintenance

Actively maintained ASWF project (3.5.2 released 2026-10-02, commits through 2026-10-10), BSD-3-Clause and packaged by Linux distros, Homebrew, MacPorts and PyPI; frequent security patch releases across the 3.2-3.5 branches mean you should track the latest patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now B.
- **Tier reason:** Independent (rival-authored) measurement: TinyEXR's doc/performance-vs-openexr.md with a public harness (benchmark/bench_compare.cpp, Makefile target bench-compare), AMD Ryzen 9 3950X and gcc -O3 stated, so the method is literally A-grade. Lowered to B because the doc's data are internally inconsistent (absolute MP/s differ about 2x between the 2026-08-08 table and the charts, HTJ2K encode flips from OpenEXR about 3x in the charts to TinyEXR 18.7 vs 16.4 in the table, the M1 table and M1 chart disagree), OpenEXR's HTJ2K values are carried over from an older run rather than measured in the same run, and OpenEXR is linked from an out-of-tree build (\$(HOME)/work/openexr/_build) with unstated 4.0-dev commit, CMake configuration and x86 OpenJPH version, so no OpenEXR-favouring ratio ties to one reproducible run.
- **Verifier notes:** Benchmark page and README opened; harness (benchmark/bench_compare.cpp, Makefile bench-compare) and chart data (doc/\*.svg, doc/gen_perf_charts.py) read directly, which recovered the in-tree numbers the search agent could not read. The record's TL;DR ratios are real but stale; the current pinned run shows smaller OpenEXR leads (about 1.45x ZIPS/PXR24 decode, 1.2-1.3x HTJ2K decode, 1.4-1.7x deflate-family encode, 2.7-3x HTJ2K encode vs in-tree TinyEXR) and OpenEXR losing or tying against TinyEXR's default libdeflate build. Shortcomings to record: rival-authored mixed evidence, incumbent measured against a non-default alternative, internally inconsistent doc data, HTJ2K baseline not same-run, out-of-tree OpenEXR build with unstated commit; metadata confirmed (BSD-3-Clause, 1.9k stars, 703 forks, last commit Oct 10 2026, active).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-118 (wave 10); enricher w10 pair-024
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/performance-vs-openexr.md>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/README.md>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/Makefile>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/benchmark/bench_compare.cpp>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/gen_perf_charts.py>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-decode.svg>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-encode.svg>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-libdeflate-decode.svg>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-mt-compare.svg>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-libdeflate-htj2k-decode.svg>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-libdeflate-htj2k-encode.svg>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-arm-decode.svg>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/perf-arm-encode.svg>
  - <https://github.com/AcademySoftwareFoundation/openexr>
  - <https://github.com/AcademySoftwareFoundation/openexr/commits>
- **Sources the enricher read:**
  - <https://github.com/AcademySoftwareFoundation/openexr/commits/main>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/README.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/cmake/OpenEXRSetup.cmake>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/src/lib/OpenEXRCore/openexr.h>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/src/lib/OpenEXRCore/openexr_context.h>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/src/lib/OpenEXRCore/openexr_decode.h>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/website/ReadingAndWritingImageFiles.rst>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/website/OpenEXRCoreAPI.rst>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/website/install.rst>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/openexr/HEAD/website/concepts.rst>
  - <https://github.com/AcademySoftwareFoundation/openexr/issues?q=is%3Aissue+performance>
  - <https://github.com/AcademySoftwareFoundation/openexr/issues/2201>
  - <https://github.com/AcademySoftwareFoundation/openexr/issues/1915>
  - <https://pypi.org/pypi/OpenEXR/json>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/performance-vs-openexr.md>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/benchmark/bench_compare.cpp>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/benchmark/bench_tx.c>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/benchmark/bench_tx.h>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/benchmark/README.md>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/Makefile>
  - <https://raw.githubusercontent.com/syoyo/tinyexr/release/doc/gen_perf_charts.py>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/academysoftwarefoundation/openexr`) · [data/wave10/enrich/raw/github_com_academysoftwarefoundation_openexr.json](../../../data/wave10/enrich/raw/github_com_academysoftwarefoundation_openexr.json) (enrichment confidence 0.75)

</details>
