# OpenJPH (HTJ2K encoder and decoder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> BSD-2 C++ HTJ2K (JPEG 2000 Part 15) codec; its lossless decode ran 6-16x faster than OpenJPEG's Part 1 decode.

| | |
|---|---|
| **Beats** | OpenJPEG (JPEG 2000 Part 1) |
| **Claimed result** | dicom-codecs README (MacBook Pro M1 Pro), lossless decode time per image: OpenJPH 4.09 ms versus OpenJPEG 24.73 ms (8-bit color US 640x480), 1.43 versus 15.65 ms (12-bit gray MR 512x512), 1.53 versus 22.27 ms (16-bit gray CT 512x512), 89.20 versus 1447.63 ms (12-bit gray MG 3064x4664): about 6.0x, 10.9x, 14.6x and 16.2x (derived from page data). OpenJPH also beats CharLS JPEG-LS lossless (7.46, 3.14, 3.46, 212.92 ms; about 1.8x to 2.4x, derived) but Kakadu is faster still (1.13, 0.51, 0.64, 29.36 ms). Encode times are measured by the harness but not published in the README. |
| **Workload** | dicom-codecs tests/main.cpp: each codec encodes the raw test image from dicom-codecs/test-data (US1-640-480-3-8-0, MR4-512-512-1-12-0, CT1-512-512-1-16-1, MG1-3064-4664-1-12-0) with its own encoder, then the timed loop decodes its own codestream once after one warm-up decode (iterations = 1). OpenJPH writes an HTJ2K (Part 15) codestream, reversible, RPCL, 64x64 code blocks, decomposition count chosen so the lowest level is at most 64 px (3 for US/MR/CT, 6 for MG), no colour transform; OpenJPEG writes a JPEG 2000 Part 1 J2K codestream, reversible, RPCL, 64x64 blocks, 5 decompositions, RCT on the colour image. Both are single-threaded and lossless; round trips are checked before timing. |
| **Metric** | latency |
| **Hardware** | Apple MacBook Pro M1 Pro |
| **Compiler and flags** | build.sh: cmake -DCMAKE_BUILD_TYPE=Release, on arm64 also -DOJPH_DISABLE_INTEL_SIMD=ON; OpenJPEG compiled from source with -ffast-math in Release and threading stubbed out (MUTEX_stub); compiler not stated. Submodules pinned at OpenJPH 5aab43f and OpenJPEG 41c25e3 (updated 2023-12-14) |
| **Adoption** | 296 stars; packaged in several distributions per the README's repology badge |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/aous72/OpenJPH) · [benchmark](https://github.com/dicom-codecs/dicom-codecs) |

## Verdict

dicom-codecs (a third-party, WIP DICOM wrapper; tests/main.cpp and tests/benchmark.cpp) was run on an Apple M1 Pro with an unnamed compiler: each codec encoded four raw images losslessly with its own encoder, then one warm-up and one timed decode. OpenJPH took 4.09/1.43/1.53/89.20 ms against OpenJPEG's 24.73/15.65/22.27/1447.63 ms (about 6x-16x, derived). OpenJPEG was decoding a Part 1 EBCOT stream while OpenJPH decoded its own HTJ2K stream, so the ratio measures format plus library together. OpenJPH ran its generic non-SIMD path on arm64, OpenJPEG was built single-threaded with -ffast-math, and OpenJPEG's own HTJ2K decoder was not timed.

## Use it when

- Lossless storage of medical images under the DICOM HTJ2K transfer syntaxes (1.2.840.10008.1.2.4.201/202/203), where you control the encoder and decode latency matters (1.4-1.5 ms per 512x512 12/16-bit slice on an M1 Pro in the measured run).
- You need an open-source (BSD-2-Clause) HTJ2K encoder as well as a decoder, and Kakadu's licence is not an option.
- Streaming or low-memory pipelines that can feed or consume one image row at a time through exchange()/pull().
- Decoding in browsers or Node.js through the provided WebAssembly SIMD build.
- OpenEXR HTJ2K compression, which builds on OpenJPH (it appears as HTJ2K_32/HTJ2K_256 in the catalogued meshoptimizer harness, and issue #273 comes from an OpenEXR 3.4.11 user).

## Skip it when

- Existing JPEG 2000 Part 1 archives or third-party .jp2/.j2k files: OpenJPH implements only the HT block coder. Use OpenJPEG or Grok, or transcode first.
- Raw speed above all: in the same dicom-codecs run, Kakadu's HTJ2K decode was 2.4x to 3.6x faster (derived) than OpenJPH (for example 29.36 vs 89.20 ms on the 3064x4664 mammogram).
- Multi-core decoding of one large image: OpenJPH has no internal threading (no thread options in the API or in ojph_compress/ojph_expand), while OpenJPEG, Grok and Kakadu can parallelise across code blocks. The benchmark ran every codec single-threaded and compiled OpenJPEG's threading out.
- ARM targets that need SIMD: the CMake ARM section is empty and src/core/coding has no NEON kernels, so aarch64 (including Apple Silicon) runs the generic C++ path. Open issue #273 also reports a SIGSEGV in the scalar encoder's mem_elastic_allocator on arm64.
- Rate-controlled lossy encoding to a byte or bitrate target: docs/status.md says only quantisation-step lossy is implemented, with no rate control.

## How it is fast

The HT block coder replaces JPEG 2000's bit-plane-by-bit-plane MQ arithmetic coding (EBCOT) with a single cleanup pass. That pass codes 2x2 quads through three byte streams: an adaptive run-length MEL coder, table-driven VLC codewords (table0.h/table1.h) and raw MagSgn bits, plus optional SigProp/MagRef refinement passes. Decoding is mostly table lookups and bit extraction instead of one context-modelled binary decision per bit. The wavelet and colour transforms work line by line, which keeps memory small, and on x86-64 the block coder and transforms dispatch at runtime to SSE/SSSE3/AVX2/AVX-512 kernels. There are also VSX (POWER8/9) and WebAssembly SIMD paths.

## Compared with alternatives

Pick it over CharLS when you want a wavelet codec with resolution scalability and faster lossless decode: CharLS decoded 1.8-2.4x slower in the same run, although CharLS reads standard JPEG-LS data that OpenJPH cannot. Pick Grok or OpenJPEG instead when you must read Part 1 JPEG 2000 files or want multi-threaded decoding of large images.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (CMake; BUILD_SHARED_LIBS defaults to ON) |
| **Dependencies** | none for the library; libtiff for TIFF I/O in the command-line tools (OJPH_ENABLE_TIFF_SUPPORT defaults to ON, can be turned off); emscripten for the wasm build |
| **Minimum toolchain** | CMake 3.12; C++14 by default (the CMake comment says C++11 suffices for the library, C++14 is for gtest); C11 for aligned_alloc |
| **Platforms** | x86-64 (runtime dispatch over SSE through AVX-512), ppc64le (VSX kernels, POWER8+), WebAssembly SIMD, aarch64 and other targets generic C++ only; little- and big-endian handled |
| **Thread safety** | not documented; the library does no internal threading, so the usual pattern is one ojph::codestream object per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Decoded line_buf samples are not clamped to the component bit depth; callers must clamp them, as the dicom-codecs wrapper does (OpenJPH issue #35). For colour without a colour transform, set_planar(true) takes a faster path (issue #34).
- Release 0.31.0 broke API and ABI compatibility, so pin a version. Issues #303 and #304 report a broken openjph-config-version.cmake in 0.30.0 and unusual shared-library names.
- Strict-aliasing type punning in the block decoders made GCC 15/16 (MinGW, -O2/-O3) produce silently wrong multipass irreversible decodes (issue #279, fixed in 0.30.0). Avoid older releases with recent GCC. The open crash issues are #273 (arm64 scalar encoder) and #374 (segfault with very small qstep values).
- '.raw' files are read as little-endian, unlike Kakadu and OpenJPEG ('.rawl'), and docs/usage_examples.md says this convention is planned to change.

## Known shortcomings

- Tier B on the dicom-codecs shootout (README plus tests/main.cpp, MacBook Pro M1 Pro, compiler unstated, 1 iteration) against OpenJPEG (JPEG 2000 Part 1): decode 6.0x/10.9x/14.6x/16.2x faster (derived), both reversible lossless; Kakadu is faster and CharLS slower, lossy not benchmarked. HTJ2K and Part 1 are different codestreams, so the gap is mostly the format; decomposition levels and colour transform differ slightly and compressed sizes are not reported.

## Caveats and trade-offs

The two libraries decode different codestreams: OpenJPH decodes HTJ2K (Part 15 block coder) while OpenJPEG decodes JPEG 2000 Part 1 (EBCOT/MQ coder), so most of the gap is the HT format rather than the library; OpenJPEG at the pinned commit also contains an HTJ2K decoder (ht_dec.c) but it was not timed on OpenJPH's stream. Settings differ slightly (decomposition levels 3 versus 5 on three images, RCT only for OpenJPEG on the colour image). Compressed sizes are not reported (the ratio printout is commented out), so the speed versus size trade-off is unknown. One iteration per case, compiler unstated, OpenJPH built with Intel SIMD disabled on arm64, OpenJPEG built single-threaded with -ffast-math. The dicom-codecs repository calls itself WIP (10 stars, last commit 2023-12-14). The libjpeg-turbo8 row (4.06 ms on the US image) is lossy baseline JPEG and not comparable. The OpenJPH README publishes no numbers of its own.

Implements High-Throughput JPEG 2000 (Part 15, ITU-T T.814) only, with Part 1 wavelet and coding features reused; it cannot read ordinary Part 1 JPEG 2000 files, so adoption needs HTJ2K-encoded data. The HT block coder trades some compression ratio for speed.

## Maintenance

Actively maintained (last commit 2026-10-01, release 0.32.0, 296 stars, 91 forks, 31 open issues, packaged in several distributions per repology) under BSD-2-Clause. It is copyable, but the measured numbers come from a December 2023 snapshot (pinned commit 5aab43f) in a third-party harness that is itself marked WIP and has been dormant since 2023-12-14.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement with public code (dicom-codecs tests/main.cpp and tests/benchmark.cpp, wrappers lib/openjph/encoder.cpp and src/openjpeg/encoder.cpp) and a stated machine (MacBook Pro M1 Pro), but no compiler is named and each case is one timed iteration after one warm-up, so it falls short of A.
- **Verifier notes:** Baseline is OpenJPEG (JPEG 2000 Part 1, lossless); Kakadu (proprietary) and CharLS (JPEG-LS) are also in the same run. Lossless settings match (both reversible), lossy settings were not benchmarked. Kept at B as an independent measurement with public code; the format-versus-library caveat is spelled out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dicom-codecs/dicom-codecs>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/README.md>
  - <https://github.com/dicom-codecs/dicom-codecs/tree/main/tests>
  - <https://github.com/dicom-codecs/dicom-codecs/commits/main>
  - <https://github.com/dicom-codecs/dicom-codecs/tree/main/src>
  - <https://github.com/dicom-codecs/dicom-codecs/tree/main/extern>
  - <https://github.com/dicom-codecs/dicom-codecs/tree/main/lib/openjph>
  - <https://github.com/dicom-codecs/dicom-codecs/tree/main/lib/openjpeg>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/main.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/benchmark.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/timer.hpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/build.sh>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/lib/openjph/encoder.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/lib/openjph/decoder.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/lib/openjpeg/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/src/openjpeg/encoder.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/src/openjpeg/decoder.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/src/lib.cpp>
  - <https://github.com/aous72/OpenJPH>
  - <https://github.com/aous72/OpenJPH/commits/master>
  - <https://github.com/aous72/OpenJPH/commit/5aab43f>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/README.md>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/docs/status.md>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/docs/compiling.md>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/docs/usage_examples.md>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/docs/fuzzing.md>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/src/core/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/src/core/openjph/ojph_version.h>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/src/core/openjph/ojph_codestream.h>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/src/core/openjph/ojph_arch.h>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/src/core/coding/ojph_block_decoder32.cpp>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/src/apps/ojph_expand/ojph_expand.cpp>
  - <https://raw.githubusercontent.com/aous72/OpenJPH/HEAD/src/apps/ojph_compress/ojph_compress.cpp>
  - <https://github.com/aous72/OpenJPH>
  - <https://github.com/aous72/OpenJPH/tree/master/src/core/coding>
  - <https://github.com/aous72/OpenJPH/releases>
  - <https://github.com/aous72/OpenJPH/issues?q=is%3Aissue>
  - <https://github.com/aous72/OpenJPH/issues/273>
  - <https://github.com/aous72/OpenJPH/issues/279>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/README.md>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/build.sh>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/CMakeLists.txt>
  - <https://github.com/dicom-codecs/dicom-codecs/tree/main/tests>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/main.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/benchmark.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/timer.hpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/tests/roundTrip.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/lib/openjph/encoder.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/lib/openjph/decoder.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/lib/openjpeg/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/src/openjpeg/encoder.cpp>
  - <https://raw.githubusercontent.com/dicom-codecs/dicom-codecs/HEAD/src/openjpeg/decoder.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aous72/openjph`) · [data/wave10/enrich/raw/github_com_aous72_openjph.json](../../../data/wave10/enrich/raw/github_com_aous72_openjph.json) (enrichment confidence 0.8)

</details>
