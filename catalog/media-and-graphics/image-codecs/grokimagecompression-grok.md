# Grok JPEG 2000 codec

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0-only` · 🟢 active

> AGPL C++23 JPEG 2000 (Part 1 and HTJ2K) codec. Its GDAL driver beats OpenJPEG on tiled, region and S3 reads.

| | |
|---|---|
| **Beats** | OpenJPEG (JPEG 2000); also Kakadu (proprietary, via GDAL JP2KAK) |
| **Claimed result** | README table (16 threads, GDAL release build, Fedora 42; seconds), Grok (JP2Grok) vs Kakadu (JP2KAK) vs OpenJPEG: Spot 6 (Network Storage) 35.17 vs 344 vs 85; Spot 6 (Local Storage) 26.92 vs 30.57 vs 52.09; Pleiades (Region) 0.74 vs 1.41 vs 4.28. Versus OpenJPEG that is 2.4x, 1.9x and 5.8x faster (derived from page data). |
| **Workload** | GDAL workflows reading JPEG 2000 imagery: Spot 6 on network storage, Spot 6 on local storage, and a Pleiades region read, using 16 threads and a GDAL release build. |
| **Metric** | latency |
| **Hardware** | Fedora 42, 16 threads (CPU model not stated) |
| **Compiler and flags** | GDAL release build (compiler and flags not stated) |
| **Adoption** | 295 stars; integrated into GDAL |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/GrokImageCompression/grok) · [benchmark](https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/README.md) |

## Verdict

A first-party README table times gdal_translate decodes with the JP2Grok, JP2KAK (Kakadu 8.4.1) and JP2OpenJPEG (2.5.4) drivers on an unnamed '8 core / 16 thread' CPU under Fedora 42, with Grok 20.0.0 built by GCC 15.2. Those details were in the October 2025 README and were removed later. Results: Spot 6 26624x26624 12-bit lossless with TLM, local 26.92 s vs OpenJPEG 52.09 s; the same file on MinIO 35.17 s vs 85 s; an 8000x8000 region of a Pleiades 16-bit lossy file 0.74 s vs 4.28 s. The local-storage OpenJPEG cell was 34.91 s (1.30x) until commit ac33404 (2026-02-26, 'README: update benchmark number') changed only that cell to 52.09 s (1.94x), with no re-run of the Grok or Kakadu cells and no explanation.

## Use it when

- GDAL pipelines that read large tiled JPEG 2000 satellite or aerial products (Spot, Pleiades) from local disk or S3/MinIO, especially windowed reads of files with TLM markers.
- Remote (S3/HTTP) reads where request count and latency dominate: the first-party network-storage run is 35 s vs OpenJPEG's 85 s, a gap that comes from fetch strategy rather than entropy-decoding speed.
- You need an open-source codec that both reads Part 1 (EBCOT/MQ) files and reads and writes HTJ2K, with multi-threaded decode, and AGPL terms are acceptable.
- Server-side region or overview extraction where the caller can pass the read window up front (AdviseRead in GDAL, or a decode window in the C API).

## Skip it when

- Proprietary or permissively licensed products, or network services you cannot open-source: the library is AGPL-3.0-only (no 'or later'). OpenJPEG (BSD-2) or OpenJPH (BSD-2, HTJ2K only) avoid that.
- If you need a codec-only speed claim: the published numbers are end-to-end gdal_translate timings dominated by I/O, caching and region selection, and no single-image decode throughput against OpenJPEG is published.
- Older toolchains: the build sets CMAKE_CXX_STANDARD 23, and INSTALL.md asks for GCC 12+, Clang 16+ or MSVC 2022 and CMake 3.20+ (CMakeLists requires 3.21).
- Code that needs a stable decoder: releases arrive every few days (v20.4.5 to v20.4.14 in September 2026 alone), the default decode path changed to the Rust Mercury engine in August 2026, and that change shifts lossy 9/7 output by plus or minus 1 LSB (issue #425).
- Whole-image decode of huge single-tile files on memory-limited hosts: the pre-2025 README showed Grok 9.7.8 using 16.6 GB against Kakadu's 0.05 GB on a HiRISE image (13.74 s vs 9.02 s). Mercury targets this case, but only for eligible streams.

## How it is fast

Code-block (T1) decoding and the per-tile pipeline run on a Taskflow work-stealing pool, and the inverse 5/3 and 9/7 lifting wavelets use Google Highway SIMD kernels with an int16 fast path for low-precision data. HTJ2K blocks go through a vendored copy of OpenJPH's BSD-2 HT block coder, with SSSE3/AVX2/AVX-512 variants. For the GDAL workflows that were measured, most of the gain comes from I/O: TLM/PLT markers let it fetch and decode only the tiles and packets inside the window, AdviseRead-driven async decode overlaps packet parsing with T1, and cached tile-part offsets and compressed chunks avoid re-walking the codestream or re-fetching from S3. Newer builds also route eligible full-resolution decodes through 'Mercury', a Rust streaming engine (bounded SPSC rings, O(window) buffering). Its README reports \~10.9 s and \~63 MB RSS versus \~14.4 s and multiple GB for the classic pipeline on one HiRISE image.

## Compared with alternatives

Pick Grok over OpenJPH when you must read ordinary Part 1 JPEG 2000 or want multi-threaded and region decode of large tiled files; Grok embeds OpenJPH's HT block coder anyway. OpenJPH stays the permissive (BSD-2), dependency-free choice for HTJ2K-only work. CharLS and HALIC are different formats (JPEG-LS, custom) and do not read JPEG 2000 archives.

## Integration

| | |
|---|---|
| **Form** | shared lib by default (BUILD_SHARED_LIBS ON), static optional; CMake package and pkg-config; Debian, AUR and Homebrew packages; SWIG Python/C#/Java and Rust bindgen bindings |
| **Dependencies** | git submodules Highway, Taskflow (maintainer's fork), spdlog, CLI11; lcms2 (built by default); libcurl for S3/HTTP reads; libtiff, libpng and libjpeg for the command-line tools (built by default); optional Rust toolchain (cargo, rust-version 1.87) for the Mercury fast path; a private, off-by-default CUDA/Metal GPU plugin submodule |
| **Minimum toolchain** | C++23; GCC 12+, Clang 16+, MSVC 2022 per INSTALL.md (CMakeLists only rejects GCC &lt; 10); CMake 3.21 |
| **Platforms** | Linux x86-64 and AArch64, Windows, macOS, WebAssembly (Emscripten); runtime SIMD dispatch through Highway; s390x big-endian test failures fixed in issue #418 |
| **Thread safety** | Process-wide Taskflow pool set by grk_initialize(num_threads; 0 = all CPUs). Per grok.h, num_threads = 1 decodes on an inline executor so that concurrent single-threaded decompresses are independent. Sharing one codec object across threads is not documented. |
| **Drop-in for the baseline** | partial: in GDAL, swapping the JP2OpenJPEG driver for JP2Grok (GDAL 3.13+, Grok &gt;= 20.3.5 for 3.13.2) needs no code change; at the library level the C API is Grok's own, not OpenJPEG's |

## Gotchas

- Builds differ silently: the Mercury fast path is compiled in only when a working cargo is found at configure time, and otherwise mercury_fastpath.cpp compiles to a no-op. GRK_MERCURY=0 forces the classic pipeline. Mercury rejects HT, BYPASS and RESTART code-block modes, tile-part POC, region and reduced-resolution decodes, and falls back to the classic path for them.
- In GDAL the JP2Grok driver decodes asynchronously only when the caller calls AdviseRead first. Without it the driver falls back to synchronous per-swath decode, which the driver docs call 'much slower, especially when decompressing over the network'.
- The early JP2Grok driver had correctness fixes after release: GDAL 3.13.1 scaled overview coordinates (#14516) and fixed the overview tile-cache strategy, and GDAL 3.13.2 fixed 'CopyTileData was using tile origin as region offset'. Use GDAL 3.13.2 or later.
- Recent correctness issues, all now closed: #420, nondeterministic decoded samples with 4+ threads on macOS arm64 (v20.3.10); #442, rate control silently writes an empty image when an ICC profile exceeds the first layer's byte budget; #427, LTO with AVX-512 constant initialisers.

## Known shortcomings

- AGPL-3.0-only. First-party GDAL driver table (Grok 20.0 vs OpenJPEG 2.5.4 and Kakadu 8.4; OpenJPEG is not a listed baseline) with no CPU model or flags; benchmark/results.txt holds only 'xx' placeholders. No independent numbers found (encode.su and fastcompression.com blocked here).
- Commit ac33404 (2026-02-26, 'README: update benchmark number') changed only the OpenJPEG local cell from 34.91 s to 52.09 s without re-running the Grok or Kakadu cells or giving a reason, moving the local ratio from 1.30x to 1.94x. The October 2025 README gave an 8-core/16-thread CPU and GCC 15.2 with MinIO at 20 ms while results.txt says 50 ms and one 'MinIO' command reads a local file. The default decoder is now the Rust 'Mercury' path (lossy output shifts by 1 LSB, #425); GDAL 3.13.2 fixed a JP2Grok CopyTileData region-offset bug; vendors the OpenJPH HT coder; OpenJPEG BSD-2 lineage.

## Caveats and trade-offs

JPEG 2000 is outside the listed baselines (libjpeg-turbo, libpng, libwebp, libavif); OpenJPEG is the recognizable open-source incumbent. First-party end-to-end GDAL timings that include I/O, caching and region reads, not codec-only throughput. benchmark/results.txt describes the method (gdal_translate on a 26kx26k 12-bit Spot 6 image with 2kx2k tiles, with and without TLM markers; network case is MinIO with 50 ms latency and VSI_CACHE=YES; drivers Grok 20.0, OpenJPEG 2.5.4, Kakadu 8.4) but its result slots are 'xx' placeholders, so the README numbers cannot be tied to a recorded run; CPU model, compiler flags and the input images are not published. Kakadu's 344 s network-storage time versus 30.57 s locally suggests an I/O-pattern effect rather than codec speed (inference). AGPL-3.0-only (LICENSE says version 3, no 'or later'), a strong copyleft licence for anyone embedding it.

Strong copyleft: AGPL v3 (network use triggers source obligations), a poor fit for permissive-license projects. Adds HTJ2K, random-access sub-image decoding with TLM and PLT markers, a multi-level tile cache and S3 access, which are features of the whole GDAL workflow measured. Reported to have started as an OpenJPEG fork (per third-party descriptions seen in search snippets); GitHub does not mark it as a fork.

## Maintenance

Very active (last commit 2026-10-03, v20.4.14 on 29 Sep, \~1,000 commits, OSS-Fuzz and 2,000+ tests, upstream GDAL driver since 3.13). Copyable only under AGPL-3.0-only, and the LICENSE file shows the code incorporates OpenJPEG's BSD-2 work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (repeated on the wiki home page) of GDAL end-to-end timings against OpenJPEG and Kakadu; benchmark/results.txt gives the gdal_translate commands and driver versions but only 'xx' placeholders, and no CPU model, compiler flags or public input images are given.
- **Verifier notes:** Numbers match the README exactly; no independent Grok vs OpenJPEG measurement was reachable (encode.su and fastcompression.com are egress-blocked). Licence AGPL-3.0-only confirmed from the LICENSE header; 295 stars, last commit 2026-10-03, not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/README.md>
  - <https://github.com/GrokImageCompression/grok>
  - <https://github.com/GrokImageCompression/grok/commits/master>
  - <https://github.com/GrokImageCompression/grok/tree/master/benchmark>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/benchmark/results.txt>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/LICENSE>
  - <https://github.com/GrokImageCompression/grok/wiki>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/README.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/benchmark/results.txt>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/src/lib/core/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/src/lib/core/grok.h>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/src/lib/core/t1/part1/block_coder/BlockCoderDec.cpp>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/src/lib/core/t1/part15/coding/ojph_block_decoder32.cpp>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/DESIGN_TODO.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/TESTING.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/doc/TileCache.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/mercury/README.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/HEAD/mercury/Cargo.toml>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/ac33404f787fc9a2c71ebfa60c7ca6ffac005eff/README.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/06b56b68e4b976a14da5803917553475ae50e1a2/README.md>
  - <https://raw.githubusercontent.com/GrokImageCompression/grok/06b56b68e4b976a14da5803917553475ae50e1a2~1/README.md>
  - <https://github.com/GrokImageCompression/grok>
  - <https://github.com/GrokImageCompression/grok/tree/master/src/lib/core>
  - <https://github.com/GrokImageCompression/grok/tree/master/integrations>
  - <https://github.com/GrokImageCompression/grok/releases>
  - <https://github.com/GrokImageCompression/grok/commits/master/README.md>
  - <https://github.com/GrokImageCompression/grok/commit/ac33404f787fc9a2c71ebfa60c7ca6ffac005eff>
  - <https://github.com/GrokImageCompression/grok/issues?q=is%3Aissue>
  - <https://github.com/GrokImageCompression/grok/issues/420>
  - <https://github.com/GrokImageCompression/grok/issues/425>
  - <https://github.com/GrokImageCompression/grok/wiki>
  - <https://raw.githubusercontent.com/OSGeo/gdal/master/NEWS.md>
  - <https://raw.githubusercontent.com/OSGeo/gdal/master/frmts/CMakeLists.txt>
  - <https://raw.githubusercontent.com/OSGeo/gdal/master/doc/source/drivers/raster/jp2grok.rst>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/grokimagecompression/grok`) · [data/wave10/enrich/raw/github_com_grokimagecompression_grok.json](../../../data/wave10/enrich/raw/github_com_grokimagecompression_grok.json) (enrichment confidence 0.75)

</details>
