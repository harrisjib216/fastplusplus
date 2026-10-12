# libyuv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Google's SIMD YUV/RGB conversion, scaling and rotation library; snippet-only reports put it 4-10x ahead of libswscale.

| | |
|---|---|
| **Beats** | FFmpeg libswscale |
| **Claimed result** | libheif issue #1215 (a user report, no hardware stated): YUV420 HEVC multi-tile decode to interleaved RGB took 42 ms with the ffmpeg decoder plugin plus libheif's own yuv2rgb conversion vs 30 ms with the same decoder plugin plus libyuv for the conversion, about 1.4x for the whole step (derived from page data); since the decoder is the same, the 12 ms difference comes from the conversion (derived from page data). Against libswscale, search snippets only (ffmpeg-devel threads, blocked here): about 4.19 s for libswscale vs 0.93 s for libyuv (about 4-5x) scaling a 1088x1920 BGR24 frame to 480x854 YUV420P 500 times on a MacBook Pro (2016), and about 10x on an Apple M1 for unscaled RGBA to YUV420P, still about 5x after FFmpeg's aarch64 NEON optimizations. |
| **Workload** | YUV/RGB format conversion and scaling (ARGB, I420, NV12 and others) in video and imaging pipelines. |
| **Metric** | throughput |
| **Adoption** | 930 stars and 302 forks on this unofficial GitHub mirror (its description says to submit issues and PRs upstream); upstream is chromium.googlesource.com/libyuv/libyuv, and README.chromium marks it shipped and security-critical in Chromium. |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/lemenkov/libyuv) · [benchmark](https://github.com/strukturag/libheif/issues/1215) |

## Verdict

No reproducible libyuv-versus-libswscale benchmark exists in reach: the 4-5x (1088x1920 BGR24 to 480x854 YUV420P, 500 runs, about 4.19 s vs 0.93 s, MacBook Pro 2016) and about 10x (RGBA to YUV420P on Apple M1) figures come from search snippets of blocked ffmpeg-devel threads, where FFmpeg developers answered that swscale's defaults run a higher-quality scaler. The one page with numbers, libheif issue #1215 (no hardware, compiler or code), times a whole HEVC multi-tile decode-to-RGB step at 42 ms with libheif's own converter and 30 ms with a 'hacky' libyuv hookup, which is about 1.4x and does not involve libswscale.

## Use it when

- Real-time camera, WebRTC or video pipelines converting between I420/NV12/NV21/YUY2 and ARGB/RGB24/RAW at 8 bits, where per-frame latency matters more than resampling quality.
- Decoders and image libraries (the libheif report) that need a fast final YUV 4:2:0 to interleaved RGB step on x86 or Arm.
- Downscaling video frames by 2x, 4x, 3/4 or 3/8 with box or bilinear filtering, or rotating mobile camera frames by 90/180/270 degrees.
- Projects that want a permissive (BSD-3-Clause plus Google patent grant), widely shipped library with a C fallback on every platform and bit-exact SIMD versus C output in its unit tests.

## Skip it when

- High-quality resampling or colour-space work (Lanczos, correct chroma siting, dithering): libyuv offers only point, linear, bilinear and box, its bilinear upsampler is described in docs/filtering.md as 'not technically correct' (the image is slightly magnified), and zimg or libswscale with quality flags fit better.
- Chroma upsampling quality: the plain I420ToARGB/I420ToRGB24 paths replicate each chroma sample over a 2x2 block (nearest neighbour); you must call the \*MatrixFilter variants with kFilterBilinear for interpolated chroma.
- Workloads that want the absolute fastest 8-bit kernels on a given path: catalogued siblings yuvutils-rs (NV12 to RGBA 377.59 vs 621.11 us), xxYUV and sparkyuv (8-bit 4:2:0 decode on Apple M3) beat it on some paths, though sparkyuv loses to libyuv on encode.
- Plain MSVC (cl.exe) builds: x86 kernels then come from row_win.cc, a smaller set, and the CMake Arm/SVE/SME/RVV objects are only built when not MSVC; Chromium compiles Windows x64 libyuv with clang to get the inline assembly.
- Multi-core scaling of one large frame: the library spawns no threads, so callers must split the image across threads themselves.

## How it is fast

Every operation is a loop over rows that calls one row function chosen once per call by runtime CPU detection (TestCpuFlag): hand-written GCC/Clang inline assembly for SSE2/SSSE3/AVX2/AVX-512 (row_gcc.cc), Neon, SVE2 and SME on Arm, RVV, LSX/LASX and MSA, with C fallbacks and '_Any_' wrappers for widths that are not a multiple of the vector size. YUV to RGB uses 6-bit fixed-point coefficients: pmaddubsw on bias-shifted UV, pmulhuw for the Y gain, saturating adds, then shift and pack, all in 16-bit lanes. The scaler has dedicated 2x, 4x, 3/4 and 3/8 down paths, a box filter, 16.16 fixed-point bilinear, and ScaleFilterReduce drops to a cheaper filter when the scale factor allows it.

## Compared with alternatives

Pick libyuv over yuvutils-rs, xxYUV, sparkyuv or the old descampsa/yuv2rgb when you need one maintained, permissively licensed C/C++ library covering nearly every 8/10/12-bit YUV and RGB layout plus scaling and rotation on every major ISA; pick zimg or FFmpeg's libswscale with quality flags when resampling and colour accuracy matter more than speed, and yuvutils-rs if you are in Rust and want its faster NV12/RGBA paths.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake builds both; GN for Chromium; also Makefile and Bazel files) |
| **Dependencies** | none required; optional libjpeg for MJPG decode (HAVE_JPEG, on by default when found); gtest and pthread only for the unit tests |
| **Minimum toolchain** | CMake 3.16; a C++ compiler (no C++ standard pinned in CMakeLists.txt); GCC or Clang for the x86 inline-assembly kernels; Arm SVE2/SME kernels need a compiler accepting -march=armv8.5-a+i8mm+sve2/+sme |
| **Platforms** | x86/x86-64 (SSE2 to AVX-512, runtime dispatch), 32- and 64-bit Arm Neon, SVE2, SME, RISC-V RVV, LoongArch LSX/LASX, MIPS MSA, portable C elsewhere |
| **Thread safety** | Conversion and scaling functions are stateless and work on caller buffers, so concurrent calls on different buffers are safe (from reading the source; not stated in docs). CPU flags are cached in a global cpu_info_ (relaxed atomic store); MaskCpuFlags is commented 'not thread safe', and sandboxed processes may need SetCpuFlags because detection can read /proc/cpuinfo. |
| **Drop-in for the baseline** | no |

## Gotchas

- Format names follow register order, not memory order: ARGB is B,G,R,A in memory, RGB24 is B,G,R and RAW is R,G,B, so 'interleaved RGB' output means I420ToRAW, not I420ToRGB24.
- The plain I420ToARGB/I420ToRGB24 entry points assume BT.601 limited range (kYuvI601Constants); full-range or BT.709 content needs the J/H/F-prefixed functions or a \*Matrix call, or colours shift silently.
- 10/12-bit inputs converted to ARGB are reduced to 8 bits per channel; use the AR30/AB30 or 16-bit paths to keep precision.
- The GitHub repo is an unofficial mirror: issues and patches go to chromium.googlesource.com/libyuv/libyuv, there is no ABI promise (CMake sets no SOVERSION) and the version is a single integer (1974 here) that consumers pin.

## Known shortcomings

- Upgraded D to C on libheif issue #1215 (42 ms vs 30 ms whole conversion step against libheif's own yuv2rgb, hardware unstated). The libswscale comparison exists only in search snippets (4.19 s vs 0.93 s on a 2016 MacBook Pro, about 10x on Apple M1; ffmpeg.org archives blocked here), and FFmpeg developers replied that swscale defaults to a higher-quality scaler, so it is not like-for-like. No public libyuv-vs-swscale benchmark code; libyuv's unit tests time only its SIMD paths against its own C. Record points at the unofficial GitHub mirror (lemenkov/libyuv); upstream is chromium.googlesource.com/libyuv/libyuv (blocked here). BSD-3-Clause plus Google PATENTS grant.
- The libheif #1215 comparison (42 versus 30 ms) is likely unequal work: libheif defaults to bilinear chroma upsampling plus a 4:4:4 intermediate pass (heif_color.cc) while plain I420ToRGB24/RAW does nearest chroma in one pass, and the reporter names no function or matrix. libyuv's own unittest prints one cold C call against the mean of N SIMD calls, overstating SIMD-versus-C ratios (outputs are asserted bit-exact).

## Caveats and trade-offs

The libswscale comparison rests on search snippets of ffmpeg-devel threads ('Why not integrate libyuv as a scale filter' and the June 2024 'swscale modernization proposal'), which this sandbox cannot open (ffmpeg.org pipermail, narkive, mail-archive and patchwork are blocked), so the numbers, hardware and swscale settings are unverified. In the same threads FFmpeg developers replied that libswscale defaults to a higher-quality scaler, that comparable speed is reachable by tuning its flags, and that libyuv does no dithering or advanced filtering, so the gap partly reflects quality settings; the snippet numbers may also predate later swscale work. The libheif numbers compare against libheif's own converter, not libswscale, are whole-step times, and state no hardware, compiler or code. No public benchmark code comparing libyuv with libswscale was found; libyuv's unittests benchmark only its SIMD paths against its own C code. The incumbent role is better documented by sparkyuv, yuvutils-rs and xxYUV, which benchmark against libyuv and beat it only on some paths. This GitHub repo is an unofficial mirror; upstream is Chromium's libyuv on googlesource. BSD-3-Clause with a separate Google PATENTS grant.

Optimized for SSSE3/AVX2 on x86, Neon/SVE2/SME on Arm, MSA on MIPS and RVV on RISC-V; conversion, scaling, rotation. Official upstream is chromium.googlesource.com/libyuv/libyuv; the GitHub repo is an unofficial mirror (issues and PRs go upstream).

## Maintenance

Active (mirror last commit 2026-10-02, version 1974, shipped and marked security-critical in Chromium); BSD-3-Clause with a separate patent grant, so copyable, but track upstream on googlesource rather than the mirror.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D to C: the benchmark page does carry numbers (a libheif user's 42 ms vs 30 ms whole-step times, libheif's own yuv2rgb vs libyuv, with no hardware, compiler, flags or code), and the libswscale numbers exist only in search snippets of blocked ffmpeg-devel threads, which caps them at C. No public benchmark code comparing libyuv with libswscale was found; libyuv's own unittests (docs/getting_started.md, LIBYUV_REPEAT) time its SIMD paths only against its own C fallback.
- **Verifier notes:** Upgraded D to C (verdict confirm): the libheif page has numbers, but they compare against libheif's own converter, and the swscale numbers are snippet only. The orchestrator may want repo_url to point at upstream chromium.googlesource.com/libyuv/libyuv (blocked here, not checkable); license BSD-3-Clause, 930 stars, last commit 2026-10-02 (active) and copyable all confirmed on the mirror.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/strukturag/libheif/issues/1215>
  - <https://github.com/lemenkov/libyuv>
  - <https://github.com/lemenkov/libyuv/commits>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/README.chromium>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/PATENTS>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/getting_started.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/deprecated_builds.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/environment_variables.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/filtering.md>
  - <https://raw.githubusercontent.com/metarutaiga/xxYUV/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/sparkyuv/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/lemenkov/libyuv>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/README.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/README.chromium>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/BUILD.gn>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/getting_started.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/formats.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/filtering.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/environment_variables.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/docs/rotation.md>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/version.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/cpu_id.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/convert.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/convert_argb.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/scale.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/row.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/source/row_gcc.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/source/row_common.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/source/convert_argb.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/source/scale.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/source/cpu_id.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/unit_test/unit_test.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/unit_test/unit_test.h>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/unit_test/convert_argb_test.cc>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/unit_test/scale_test.cc>
  - <https://github.com/strukturag/libheif/issues/1215>
  - <https://raw.githubusercontent.com/strukturag/libheif/HEAD/libheif/api/libheif/heif_color.h>
  - <https://raw.githubusercontent.com/strukturag/libheif/HEAD/libheif/api/libheif/heif_color.cc>
  - <https://raw.githubusercontent.com/strukturag/libheif/HEAD/libheif/api/libheif/heif.h>
  - <https://raw.githubusercontent.com/strukturag/libheif/HEAD/libheif/color-conversion/colorconversion.cc>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/lemenkov/libyuv`) · [data/wave10/enrich/raw/github_com_lemenkov_libyuv.json](../../../data/wave10/enrich/raw/github_com_lemenkov_libyuv.json) (enrichment confidence 0.7)

</details>
