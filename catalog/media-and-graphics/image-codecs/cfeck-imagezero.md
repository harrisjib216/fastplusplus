# ImageZero

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Tiny one-pass lossless codec for 24-bit RGB photos; README claims 20x faster compression than PNG, with no benchmark to back it.

| | |
|---|---|
| **Beats** | PNG (format only; the README never names the PNG implementation, tool or compression level, so libpng/zlib is inferred) |
| **Claimed result** | README: 'Compared to PNG, it compresses 24 bit PPM files about 20 times faster, and decompresses to PPM about 2 times faster, while the compression rate is nearly as good as PNG for natural photos.' |
| **Workload** | Lossless compression and decompression of 24-bit PPM files, natural photos. |
| **Metric** | throughput |
| **Adoption** | 53 stars, 22 forks; repackaged for ROS as the imagezero package and swri-robotics/imagezero_transport (37 stars) |
| **Last commit** | 2013-11-06 |
| **Links** | [repository](https://github.com/cfeck/imagezero) · [benchmark](https://raw.githubusercontent.com/cfeck/imagezero/HEAD/README) |

## Verdict

Nothing has been measured reproducibly. The README states, with no method, that compared with PNG (implementation and level unnamed) it compresses 24-bit PPM files about 20x faster and decompresses about 2x faster at a nearly equal ratio on natural photos; the repository has no timing code. The one third-party observation is a 2018 ROS gist on an i7-6700HQ (640x320 at 30 fps), where the imagezero transport used 82-84% CPU against 108% for PNG levels 3 and 9, a CPU-load reading, not a codec throughput benchmark; the swri ROS plugin also routes every frame through an OpenCV PPM encode and decode.

## Use it when

- Real-time lossless capture or streaming of 8-bit RGB camera frames where encode CPU per frame matters more than file size, especially in ROS, where swri-robotics/imagezero_transport already wraps it as an image_transport plugin (ROS Indigo to Lunar).
- Noisy natural photographs or camera video, which is the content the README says compresses nearly as well as PNG. The per-pixel prefix code cannot exploit long flat runs anyway.
- Embedded or legacy builds that need a dependency-free codec of about 930 lines of library code under BSD-2-Clause, and can accept a private, unversioned file format.
- Studying a minimal context-coded predictive image coder; the design is small enough to read in one sitting.

## Skip it when

- When you need measured performance: the 20x/2x figures are one README sentence with no benchmark program, test images, PNG implementation, compiler or CPU. nigeltao/qoir left it out because it cannot represent alpha, and the WangXuan95 shootout does not include it. The only third-party data point is an informal 2018 ROS gist (i7-6700HQ, 640x320 at 30 fps) showing 82-84% CPU for the imagezero transport against 108% for PNG levels 3 and 9 (with frame lag at level 9) and 36-40% for JPEG.
- Images with alpha, grayscale, palettes or 16-bit samples: the Pixel class is hard-coded to three 8-bit channels, and the CLI rejects anything other than 24-bit PPM.
- Flat computer-generated graphics, screenshots and UI captures (the README excludes them): with no run-length or LZ stage, every pixel costs at least one bit, so it cannot approach PNG or QOI ratios on such content.
- Untrusted or archival data: there is no magic number, version, checksum or input-length parameter, the bitstream is written in host byte order (byte swapping is commented out), and the author calls both the format and the API 'early work in progress'.
- Anything that needs upkeep: last commit 2013-11-06, archived 2022-09-14; issues #3 (2018) and #5 (2022) are still open, and the only PR (#2, 0.2.4) was closed unmerged.

## How it is fast

Every pixel costs the same, fixed amount of work in a single pass. ImageZero predicts each channel with a blend of planar and average prediction, (3\*left + 3\*up - 2\*upleft + 2) &gt;&gt; 2; the first row and first column use the left or upper neighbour instead. Green's residual is then subtracted from the red and blue residuals, and each residual is zigzag-mapped to an unsigned value. The coder finds how many bits the largest of the three residuals needs (0-8). It writes that length with a static prefix code chosen by the previous pixel's length (9 contexts, codes up to 6 bits long), then writes all three residuals as fixed-length fields of that size. There is no LZ matching, no filter search, no Huffman table construction and no arithmetic coding. The bit I/O uses a 64-bit cache flushed in 32-bit words, and decoding is one 64-entry table lookup per pixel plus shifts. Branch-free bit tricks (intmacros.h) do the clamping and sign handling.

## Compared with alternatives

Rarely. For 24-bit photos, QOI, QOIR and Zpng have independent, reproducible numbers against libpng on the QOI suite (for example Zpng encodes 126 MPixels/s at CmpRatio 0.2182 vs libpng's 5.49 at 0.2423) and also handle alpha. Choose ImageZero only when you already run its ROS image_transport plugin or need a dependency-free RGB-only coder you can read in an afternoon.

## Integration

| | |
|---|---|
| **Form** | source-drop (libiz.cpp + table.cpp + headers); autotools builds libiz as a library, while the CMake and qmake files build only the iz CLI |
| **Dependencies** | none for the library; the CLI's file.cpp uses POSIX mmap when HAVE_MMAP is defined and falls back to stdio otherwise |
| **Minimum toolchain** | GCC or Clang (uses __attribute__((always_inline)) and __builtin_clz, C++98-era code); must be built with optimization (shipped flags -O2 -mmmx -mtune=atom -fno-rtti -fno-exceptions); MSVC support not documented |
| **Platforms** | 64-bit LP64/LLP64 targets use a 64-bit integer bit cache, and 32-bit x86 uses MMX; macOS needs MAP_POPULATE removed from file.cpp (patch in issue #1, never merged); the swri-robotics fork drops the Intel-only flags off x86 (CHANGELOG 0.2.2); .iz files are tied to the host's byte order |
| **Thread safety** | Not documented. initEncodeTable()/initDecodeTable() fill global tables and must finish before any encode or decode. After that the encoder and decoder are per-call objects that only read the global tables, so concurrent calls on separate images look safe from the code. |
| **Drop-in for the baseline** | no |

## Gotchas

- Relies on undefined behaviour being optimized away: on the first row and first column the predictor call still evaluates p[-bpp], p[-bpr] and p[-bpp-bpr], memory before the image start, as arguments that the chosen predictor ignores. Only inlining removes those loads, which is why the WARNING file says non-inlined predictors 'cause an access violation'. The autotools --enable-debug build (-O0) and sanitizer builds hit this.
- Forgetting initEncodeTable() fails silently: the encoder copies the zero-filled global staticdBits table and writes a corrupt stream with no error. Decoding likewise needs initDecodeTable().
- Buffer contracts are on the caller. The encoder needs up to width\*height\*4 + 33 bytes (the CLI's sizing). Rows must be tightly packed (samplesPerLine == 3\*width): with padded rows the encoder's end-of-image test never matches and it reads past the buffer. From reading the code, the decoder has no input-length argument and can fetch one 32-bit word past the end of even a valid stream, so pad input buffers by at least 4 bytes.
- Dimensions are limited by the 4-bit field width to 32768 per side (the CLI rejects anything above 16384x16384), and the decoder always assumes 3\*width bytes per row.

## Known shortcomings

- README-only claim (about 20x compress, 2x decompress vs 'PNG' with the implementation unnamed); main.cpp is a converter, no benchmark code. Archived 2022-09-14. The only independent data is an informal 2018 gist (CPU time 82-84% vs PNG 108%); LWN and ROS discourse pages blocked here.
- No benchmark code in the repo and no third-party run in QOIR or WangXuan95; the only outside data is a 2018 ROS gist (CPU 82-84% versus PNG 108%). The code relies on undefined behaviour (out-of-bounds predictor loads that only inlining removes; -O0 and debug builds crash); the decoder can over-read 4 bytes past a valid stream; skipping the init tables gives silently corrupt output; padded rows overrun; no magic, version or checksum; host-endian; RGB only.

## Caveats and trade-offs

Only a README paragraph backs the claim: no benchmark code, test images, CPU, compiler or PNG implementation, so the baseline is inferred (low confidence). The repository was archived on 2022-09-14 and its last commit is 2013-11-06, so the comparison predates modern libpng, zlib-ng and libdeflate. The author calls the code 'early work in progress' with no fixed format or API, and the WARNING file says it must be built with full optimization or the non-inlined predictors cause an access violation (CMake sets -O2 -mmmx -mtune=atom). It handles only 24-bit RGB, no alpha or grayscale, which is why nigeltao/qoir left it out of its benchmark. The only independent number found is an informal 2018 gist (awesomebytes, i7-6700HQ, ROS Kinetic, 640x320 at 30 fps) where the subscribing node used 82-84% CPU with imagezero versus 108% with PNG at levels 3 and 9, a CPU-usage observation rather than a throughput benchmark.

Own format and API (README calls it 'early work in progress'; neither format nor API fully outlined). Works on 24-bit RGB only; README says it is not suited for flat computer-generated graphics or grayscale images.

## Maintenance

Abandoned (last commit 2013-11-06, archived 2022-09-14). It is BSD-2-Clause and small enough to vendor, but treat it as experimental: unversioned host-endian format, optimization-dependent memory safety, no tests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party ratios against PNG (about 20x faster compression, about 2x faster decompression of 24-bit PPM) with no benchmark program, test images, PNG implementation, compiler or CPU; main.cpp is only a PPM-to-IZ converter with no timing code. Ratios without methodology are tier C.
- **Verifier notes:** Claim text matches the README exactly; no repository file measures anything. The ROS announcement (discourse.openrobotics.org) and the 2012 LWN article were EGRESS_BLOCKED, so any numbers there were not checked; the swri-robotics/imagezero_transport README only repeats the 20x/2x sentence.
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/README>
  - <https://github.com/cfeck/imagezero>
  - <https://github.com/cfeck/imagezero/commits>
  - <https://github.com/cfeck/imagezero/blob/master/main.cpp>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/WARNING>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/AUTHORS>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/libiz.h>
  - <https://gist.github.com/awesomebytes/359b198e83e8a2e6294d2d86c3a3a1c8>
  - <https://github.com/swri-robotics/imagezero_transport>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/cfeck/imagezero>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/README>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/WARNING>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/AUTHORS>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/configure.in>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/build.mk>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/buildconf.sh>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/iz.pro>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/bitcoder.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/decoder.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/encoder.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/file.cpp>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/file.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/image.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/intmacros.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/iz_p.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/libiz.cpp>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/libiz.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/pixel.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/portableimage.cpp>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/portableimage.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/predict.h>
  - <https://raw.githubusercontent.com/cfeck/imagezero/HEAD/table.cpp>
  - <https://github.com/cfeck/imagezero/issues?q=is%3Aissue>
  - <https://github.com/cfeck/imagezero/issues/1>
  - <https://github.com/cfeck/imagezero/issues/3>
  - <https://github.com/cfeck/imagezero/pulls?q=is%3Apr>
  - <https://github.com/cfeck/imagezero/pull/2>
  - <https://github.com/swri-robotics/imagezero_transport>
  - <https://github.com/swri-robotics/imagezero_transport/tree/master/imagezero>
  - <https://raw.githubusercontent.com/swri-robotics/imagezero_transport/HEAD/imagezero/CMakeLists.txt>
  - <https://raw.githubusercontent.com/swri-robotics/imagezero_transport/HEAD/imagezero/CHANGELOG.rst>
  - <https://github.com/swri-robotics/imagezero_transport/tree/master/imagezero_ros/src>
  - <https://raw.githubusercontent.com/swri-robotics/imagezero_transport/HEAD/imagezero_ros/src/ros_support.cpp>
  - <https://gist.github.com/awesomebytes/359b198e83e8a2e6294d2d86c3a3a1c8>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/cfeck/imagezero`) · [data/wave10/enrich/raw/github_com_cfeck_imagezero.json](../../../data/wave10/enrich/raw/github_com_cfeck_imagezero.json) (enrichment confidence 0.75)

</details>
