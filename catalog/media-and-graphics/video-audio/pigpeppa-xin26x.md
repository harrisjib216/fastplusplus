# Xin26x

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `AGPL-3.0` · 🟢 active

> Low-delay HEVC/VVC encoder framework in C; README shows 2.4-4.7x x265 fast fps single-threaded, HEVC core binary-only.

| | |
|---|---|
| **Beats** | x265 (--preset fast, single thread, build dated 2020-12-25) |
| **Claimed result** | FPS xin26x vs x265: BasketballDrive 20.68 vs 7.96 (PSNR 36.929 vs 36.913); pedestrian_area 39.203 vs 8.35 (39.719 vs 39.707); KristenAndSara 103.68 vs 23.56 (43.218 vs 43.183); sc_desktop 39.48 vs 16.83 (40.082 vs 29.817). README text: 'The performance of xin26x(HEVC) is x4 compared to x265 under single unit core.' Ratios 2.6x, 4.7x, 4.4x, 2.3x (derived from page data). |
| **Workload** | Single-thread low-delay IPPP encode of four clips (1080p BasketballDrive, 1080p pedestrian_area, 720p KristenAndSara, 1080p sc_desktop screen content) at matched bitrate, frames per second and PSNR; separate offline table gives BD-rate against x265 veryslow. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for either benchmarked binary. The HEVC encoder and shared core are prebuilt Windows static libraries (h26x_core.lib, h265_core.lib, h265_enc.lib) of unknown compiler and flags; CMakeLists.txt adds -W4 /arch:AVX and -Oi -GL (MSVC release) only for the parts built from source. Commands: xin26x_test.exe -a 0 -I 0 --wpp 0 --thread 1 --preset 0 (preset 3 for BasketballDrive) --bframes 0 (-s 1 for sc_desktop); x265.exe --preset fast -I -1 --pools 1 --bframes 0 --frame-threads 0 --no-wpp --tune psnr. The x265 2020/12/25 version is stated only for the offline BD-rate table. |
| **Adoption** | 108 stars |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/pigpeppa/xin26x) · [benchmark](https://github.com/pigpeppa/xin26x) |

## Verdict

README low-delay tables (added 28 Dec 2020), first-party, single thread, IPPP with ABR: xin26x 20.68 vs x265 7.96 fps on 1080p BasketballDrive (xin26x preset 3, 500 frames), 39.203 vs 8.35 on 1080p pedestrian_area, 103.68 vs 23.56 on 720p KristenAndSara (preset 0) and 39.48 vs 16.83 on 1080p sc_desktop (preset 0 plus screen-content mode, PSNR 40.08 vs 29.82 dB), i.e. 2.60x, 4.69x, 4.40x and 2.35x (derived from page data), against x265 --preset fast --tune psnr --pools 1 --no-wpp --frame-threads 0 --bframes 0. No CPU, compiler, flags, achieved bitrate or x265 version is given for these runs (the 2020/12/25 x265 build is named only for the offline table), FPS comes from different clients (xin26x_test divides frames by wall-clock time, including file I/O), and in current x265 source --pools 1 still creates a one-worker pool next to the frame-encoder thread, so neither run is strictly one core; CPU utilisation is not reported.

## Use it when

- Evaluating single-core, low-delay (IPPP, no B-frames) HEVC encoding on Windows x86-64 with AVX2, where the README shows 20.7-103.7 fps against 8.0-23.6 fps for x265 --preset fast at PSNR within 0.04 dB on natural 720p/1080p clips.
- Screen-sharing style content in HEVC: the -s 1 mode turns on transform skip and 4x4 intra/inter partitions, and on sc_desktop it reached 40.08 dB against x265's 29.82 dB at the same 2 Mbit/s target (x265 ran without any screen-content tools).
- Studying or extending an open VVC encoder: since June-July 2026 h266_core and h266_encoder build from source, and the offline table claims xin266 preset 6 at -41.5% BD-rate against x265 veryslow (no speed given).
- Real-time pipelines that need run-time control of bitrate, frame rate, IDR insertion and temporal layers (up to 3) through Xin26xControlOption.

## Skip it when

- When the encoder must be auditable, rebuilt or run off Windows: h26x_core.lib, h265_core.lib and h265_enc.lib are prebuilt MSVC libraries, CMake's Linux and macOS branches look for .a files that do not exist (issue #12, 'cannot find -lxin26x', open since 2022), issue #15 (a Visual Studio build that 'does nothing') has been open since 2023, and the pre-built win64 encoder the README mentions is gone from testbin, which now holds only VvcDecoderApp.exe.
- Non-x86 or pre-AVX2 CPUs: the README lists only Intel x86 with AVX2, ARM support (issue #11) has been open since 2021, and CMake's USE_INTRINSICS branch tests PROC_ARCH_ARM, which nothing sets, so even an ARM_PLATFORM build defines _X86_OPT_.
- Closed-source or SaaS products: the LICENSE file is AGPL-3.0, 2026 source headers say GPL-3.0-or-later and the app files still say '(c) 2020, shennung ... All rights reserved', so the terms need clarifying before shipping.
- Offline/VOD or multi-threaded encoding decisions: there are no multi-thread speed numbers, the offline table gives no speeds, and its fastest listed HEVC preset (xin265 p1) is 22.8% worse in BD-rate than x265 veryslow.
- 10-bit or non-4:2:0 sources, resolutions above the README's 3860x2160 limit, or more than 3 temporal layers; the sample client reads 8-bit 4:2:0 raw YUV only.

## How it is fast

Not documented, and the HEVC encoder source is not in the repository, so the technique cannot be confirmed. The open option parser shows what the measured presets switch off: preset 0 (labelled 'superfast' in the CLI help) uses one reference frame, motion search mode 1, no RDOQ, no MCTF and no SMP, while preset 3 ('medium', used for BasketballDrive) raises references to 3 and turns MCTF on; a 48-frame lookahead and unit-tree (the cu-tree analogue) stay on by default. The README requires AVX2 and 2026 commits mention an 'intel optimized subroutine', so hand-vectorised kernels are likely part of it, but which kernels and how much they contribute is not visible.

## Compared with alternatives

Pick Xin26x over Kvazaar only when single-core low-delay HEVC speed on Windows/AVX2 matters more than having source and portability, since Kvazaar is the open, cross-platform HEVC encoder in this category that also claims to beat x265. For VVC, VVenC has a published speed table against VTM; Xin26x's VVC encoder has quality claims only.

## Integration

| | |
|---|---|
| **Form** | static lib: HEVC encoder and shared core as prebuilt Windows .lib files; VVC, AV1-intra and API layers built from source with CMake |
| **Dependencies** | none external documented; the Windows client compiles the bundled third_party/getopt |
| **Minimum toolchain** | CMake 3.5+ and Visual Studio 2022 (README); Windows release flags -W4 /arch:AVX -Oi -GL for the parts built from source |
| **Platforms** | Windows x86-64 with AVX2 in practice; Linux, macOS and ARM paths exist in CMakeLists.txt but the closed HEVC libraries exist only as .lib |
| **Thread safety** | not documented; the API layer installs a process-wide logger (_XIN_LOGGER) from the first encoder created, so later encoders' pfXinLogEntry callbacks are ignored; otherwise each encoder has its own handle and internal thread pool (--thread) |
| **Drop-in for the baseline** | no |

## Gotchas

- Xin26xEncoderReconfig is exported, but the API layer never assigns pfXinEncoderReconfig, so calling it jumps through a NULL function pointer. When Xin26xEncoderCreate fails (for example, a codec disabled at build time) it still returns a handle whose function pointers are NULL, so Xin26xEncoderDelete on it crashes and skipping it leaks.
- The published low-delay commands omit the PSNR switches on both sides (xin26x's -P/--psnr leaves calcPsnr off by default; x265 needs --psnr, which --tune psnr does not set), and the achieved bitrates are not reported, so 'equal PSNR at equal ABR target' cannot be re-derived from the README commands.
- Presets are not matched by name: xin26x preset 0 is its 'superfast' (preset 3 'medium' for BasketballDrive) against x265 --preset fast. The low-delay rows date from 28 Dec 2020 (README blame) and the HEVC .lib files have been replaced since ('update libs to fix bugs', Jul 2026), so the current binaries are not the ones measured.
- -f means frame rate in xin26x_test but frame count in x265 (the BasketballDrive commands use -n 500 and -f 500 respectively); -r is rate-control mode, and the offline commands use -r 5, a value the CLI help (0-3) does not document.

## Known shortcomings

- CPU, compiler and flags unstated; xin26x presets 0 and 3 are compared with x265 fast with PSNR within 0.04 dB on 3 natural clips, but the sc_desktop clip is not like-for-like. The HEVC encoder and h26x_core ship only as prebuilt Windows .lib files with no source, so usability is mixed.
- Enricher (e118, 2026-10-05): measurement flaws, no proven correctness bug. The low-delay rows date from 2020-12-28 (README blame) while the HEVC .lib has since been replaced ('update libs to fix bugs', July 2026) and testbin has no encoder executable; the published commands omit PSNR switches on both sides (calcPsnr off by default, x265 --tune psnr does not enable --psnr) and the achieved bitrate is not reported; preset 0 ('superfast') is compared with x265 fast. API: Xin26xEncoderReconfig calls a never-assigned NULL function pointer; a failed Create returns a handle that crashes Delete. License conflict: LICENSE is AGPL-3.0, SPDX headers say GPL-3.0-or-later, app files say 'All rights reserved'. Linux build impossible (no .a, issue #12).

## Caveats and trade-offs

The measured HEVC encoder is closed: h26x_core/h26x_core.lib, h265_core/h265_core.lib and h265_encoder/h265_enc.lib are prebuilt Windows static libraries that CMakeLists.txt imports as STATIC IMPORTED, with no HEVC source in the repo (only the VVC h266_\*, AV1-intra h265p_\*, API and app code have source under AGPL-3.0), so the fast code cannot be read, audited or rebuilt for other platforms; open issue #15 (2023) reports a Visual Studio build that produces an executable that does nothing and doubts all code is included, and Linux build issues #10/#12 exist. First-party table only: CPU model, compiler and flags are not stated, and the test sequences are not in the repo (only a Google Drive link to xin26x bitstreams). xin26x presets differ per sequence (preset 3 for BasketballDrive, preset 0 elsewhere) against x265 --preset fast, which is not x265's fastest preset (ultrafast to faster are quicker), so the gap is not at matched effort; PSNR is matched within 0.04 dB at equal ABR bitrate for the three natural sequences (PSNR only, no BD-rate for the low-delay runs). The sc_desktop row is not like for like (xin26x's screen-content tool -s 1, PSNR 40.082 versus 29.817). x265 --frame-threads 0 is its auto setting, which with --pools 1 should resolve to one frame thread; CPU utilisation is not reported. The README says lookahead and cu-tree are enabled in both. x86 AVX2 only. The repo dates to 2020 (issue #1, 2020-08-19; 215 commits); the first commits page only reaches back to 2026-04-28.

Requires x86 with AVX2 (README lists no other CPU support). Build scripts target Windows (CMake plus Visual Studio). HEVC and VVC encoders only; AV1 is intra-only pure C without SIMD or threads. Max resolution stated as 3860x2160, max 3 temporal layers, evaluation mode supports ABR only. AGPL-3.0 copyleft. Plain C API.

## Maintenance

Single-author project, active (last commit 2026-08-26) and opening more source during 2026 (API in April, AV1-intra in May, VVC in June-July), but the HEVC encoder behind the speed table is still binary-only Windows libraries with conflicting licence headers, so treat it as an evaluation binary rather than a library to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README low-delay tables give xin26x and x265 FPS and PSNR with full command lines, matching the record (2.60x, 4.69x, 4.40x, 2.35x derived from page data), but no CPU, compiler, flags or x265 build for these runs, the sequences are not in the repo, and the measured HEVC encoder ships only as prebuilt binaries, so it is first-party C.
- **Verifier notes:** Confirmed at C with usability corrected to mixed: the benchmarked HEVC encoder and shared core are binary-only .lib files, which matters more for this catalog than the speed claim. License AGPL-3.0 (LICENSE file), 108 stars, 10 forks, last commit 2026-08-26 confirmed via github.com pages.
- **Fields the verifier corrected:** `usability`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party README table
- **Pages the verifier opened:**
  - <https://github.com/pigpeppa/xin26x>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/README.md>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/LICENSE>
  - <https://github.com/pigpeppa/xin26x/commits>
  - <https://github.com/pigpeppa/xin26x/tree/master/lib>
  - <https://github.com/pigpeppa/xin26x/tree/master/h26x_core>
  - <https://github.com/pigpeppa/xin26x/tree/master/h265_core>
  - <https://github.com/pigpeppa/xin26x/tree/master/h265_encoder>
  - <https://github.com/pigpeppa/xin26x/tree/master/h266_encoder>
  - <https://github.com/pigpeppa/xin26x/tree/master/h266_encoder/source>
  - <https://github.com/pigpeppa/xin26x/tree/master/h266_core>
  - <https://github.com/pigpeppa/xin26x/tree/master/h26x_api>
  - <https://github.com/pigpeppa/xin26x/issues?q=is%3Aissue>
  - <https://github.com/pigpeppa/xin26x/issues/15>
- **Sources the enricher read:**
  - <https://github.com/pigpeppa/xin26x>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/README.md>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/app/encoder/source/xin_app_enc.c>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/app/encoder/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/app/common/source/xin_encoder_option.c>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/app/common/include/xin_encoder_option.h>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/h26x_api/source/h26x_encoder_api.c>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/h26x_api/include/h265_encoder_api.h>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/h26x_api/include/h26x_encoder_struct.h>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/h26x_api/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/video_api/video_encoder/include/xin26x_params.h>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/video_api/video_encoder/include/xin26x_encoder_api.h>
  - <https://raw.githubusercontent.com/pigpeppa/xin26x/HEAD/docs/vvc-deployment-challenges.md>
  - <https://github.com/pigpeppa/xin26x/tree/master/testbin>
  - <https://github.com/pigpeppa/xin26x/tree/master/h26x_core>
  - <https://github.com/pigpeppa/xin26x/tree/master/app>
  - <https://github.com/pigpeppa/xin26x/tree/master/app/encoder>
  - <https://github.com/pigpeppa/xin26x/tree/master/app/encoder/source>
  - <https://github.com/pigpeppa/xin26x/tree/master/h26x_api>
  - <https://github.com/pigpeppa/xin26x/tree/master/h26x_api/source>
  - <https://github.com/pigpeppa/xin26x/tree/master/h26x_api/include>
  - <https://github.com/pigpeppa/xin26x/tree/master/lib>
  - <https://github.com/pigpeppa/xin26x/commits>
  - <https://github.com/pigpeppa/xin26x/commits/master/README.md>
  - <https://github.com/pigpeppa/xin26x/commit/dc4f3ea>
  - <https://github.com/pigpeppa/xin26x/commit/bbdf726>
  - <https://github.com/pigpeppa/xin26x/blame/master/README.md>
  - <https://github.com/pigpeppa/xin26x/issues?q=is%3Aissue>
  - <https://github.com/pigpeppa/xin26x/issues/1>
  - <https://github.com/pigpeppa/xin26x/issues/12>
  - <https://github.com/pigpeppa/xin26x/issues/13>
  - <https://github.com/pigpeppa/xin26x/issues/14>
  - <https://github.com/pigpeppa/xin26x/issues/15>
  - <https://raw.githubusercontent.com/videolan/x265/master/source/common/param.cpp>
  - <https://raw.githubusercontent.com/videolan/x265/master/source/common/threadpool.cpp>
  - <https://raw.githubusercontent.com/videolan/x265/master/source/x265cli.cpp>
  - <https://raw.githubusercontent.com/videolan/x265/master/source/x265.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/pigpeppa/xin26x`) · [data/wave10/enrich/raw/github_com_pigpeppa_xin26x.json](../../../data/wave10/enrich/raw/github_com_pigpeppa_xin26x.json) (enrichment confidence 0.65)

</details>
