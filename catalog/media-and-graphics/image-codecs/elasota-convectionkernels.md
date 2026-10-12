# ConvectionKernels (CVTT BC6H decoder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> MIT texture-compression kernels (BC1-7, ETC1/2) whose scalar BC6H decoder narrowly beat bcdec in aras-p's 2022 single-thread test.

| | |
|---|---|
| **Beats** | bcdec (also AMD Compressonator cmp_core, DirectXTex, SwiftShader, Mesa in the same chart; BC6H unsigned decode only) |
| **Claimed result** | BC6H unsigned decode, Mpix/s, single thread, printed bar labels in aras-p's three chart PNGs (ratios derived from page data): Ryzen 5950X VS2022: convection 101 vs bcdec 85 (1.19x), swiftshader 70, mesa 57, DirectXTex 25 (4.0x), amd_cmp 9 (11x). Ryzen 5950X clang14: convection 105 vs bcdec 104 (1.01x, a tie), swiftshader 97, mesa 79, DirectXTex 34 (3.1x), amd_cmp 33 (3.2x). Apple M1 Max clang13: convection 149 vs swiftshader 143 (1.04x), mesa 84, bcdec 79 (1.89x), DirectXTex 37 (4.0x), amd_cmp 30 (5.0x). The post's own words: 'Fastest BC6H decoder (by a small margin)'. On BC7 decode it is slower than bcdec and far slower than bc7enc_rdo's bc7decomp (VS2022: convection 124 vs bcdec 142 vs bc7dec_rdo 621; clang14: 121 vs 169 vs 656; M1 Max: 157 vs 220 vs 517). |
| **Workload** | Single-thread BC6H (unsigned) texture decode in Mpix/s, from aras-p's June 2022 bcn_decoder_tester harness decoding a set of DDS test images (ambientCG textures, Kodak, Poly Haven HDRI, WebP gallery) with ConvectionKernels ('convection') versus eight other BCn decoders. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5950X (Windows, VS2022 and clang14 charts); Apple M1 Max (macOS clang13 chart); 1 thread |
| **Compiler and flags** | Windows: Visual Studio 2022 (cl, preset x64-release) and clang 14 (clang-cl, preset x64-release-clang), both CMAKE_BUILD_TYPE RelWithDebInfo plus /Ob2 from CMakeLists.txt, C++17; macOS: Apple clang 13, no preset or build type given. Versions per the post: convection 350416d (2022-06-23), bcdec e3ca0 (2022-06-23), DirectXTex 679538e, compressonator b2b4ee3, swiftshader 2b79b2f, mesa ad3d6d9. |
| **Adoption** | 53 stars; embedded in aras-p/bcn_decoder_tester |
| **Last commit** | 2022-06-23 |
| **Links** | [repository](https://github.com/elasota/ConvectionKernels) · [benchmark](https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2022/bcn-decode-win-vs2022.png) |

## Verdict

aras-p's public bcn_decoder_tester (20 runs per DDS file, one thread, every BC6H decoder producing float32 RGB, Windows builds RelWithDebInfo plus /Ob2) measured ConvectionKernels 350416d's BC6H unsigned decoder at 101 Mpix/s against bcdec e3ca0's 85 (1.19x) with VS2022 and 105 against 104 (a tie) with clang 14 on a Ryzen 5950X, and at 149 against SwiftShader's 143 and bcdec's 79 on an Apple M1 Max with Apple clang 13; DirectXTex was 3-4x slower, and on BC7 it trailed both bcdec and bc7enc_rdo.

## Use it when

- Bulk CPU decoding of BC6H (HDR) textures on x86-64 or Apple Silicon, single-threaded, where 1.0-1.2x over bcdec is worth an extra dependency (aras-p measured 101-149 Mpix/s).
- You already vendor CVTT for BC6H, BC7 or ETC encoding (Godot ships it as thirdparty/cvtt) and want the matching decoder for round-trip error measurement.
- You want BC6H output as half floats: UnpackOne writes FP16 bit patterns directly, so no float32 round trip is needed if the consumer takes FP16.
- One MIT library covering both encode and decode of BC6H and BC7.

## Skip it when

- BC1-BC5 decoding: there are no decoders for them; use bcdec (every BCn format in one header) or etcpak (fastest BC1/BC3 in the same test).
- BC7 decoding: slower than bcdec (124 vs 142 Mpix/s with VS2022, 121 vs 169 with clang 14) and 4-5x slower than bc7enc_rdo's bc7decomp (621 and 656 Mpix/s).
- Where the margin must hold up: with clang 14 it ties bcdec (105 vs 104 Mpix/s), and bcdec has moved on since the measured e3ca0 while this repo has not changed since 2022-06-23.
- Small builds: aras-p counts 9 source files and 487 KB of source to get two decoders, mostly encoder code; bcdec is one 69 KB header.
- Projects that need maintained code: the README still labels BC6H 'Experimental' and the project has had no commits since 2022.

## How it is fast

The BC6H decoder loads the 128-bit block into four 32-bit words, shifts the 65- or 82-bit header out in one step, and runs a per-mode generated straight-line function (BC6H_IO g_readFuncs, one for each of the 14 modes) that gathers the scattered endpoint bits with constant masks and shifts, instead of walking a per-bit mode-descriptor table as the DirectXTex-derived layout does. Endpoints are then sign-extended, delta-decoded and unquantised in integer math, and the 16 pixels are interpolated with the BC6H weight tables; the decoder is plain scalar C++, so the gain comes from cheap bit extraction, not SIMD. The encoders (not part of the measured claim) use an SPMD design that processes 8 blocks per call with SSE2 16-bit math through ParallelMath, with a scalar fallback elsewhere.

## Compared with alternatives

Pick ConvectionKernels only for BC6H decode throughput, or when you already ship its BC6H/BC7/ETC encoders; otherwise bcdec covers every BCn format in one header and tied or nearly tied it on BC6H, and bc7enc_rdo's bc7decomp (bc7enc family) is 4-5x faster on BC7. For BC7 encoding, bc7e and bc7enc have independent quality and speed measurements; CVTT's encoders have none in this catalogue.

## Integration

| | |
|---|---|
| **Form** | source-drop / static lib (10 .cpp and 23 .h files; ConvectionKernels_SingleFile.cpp with CVTT_SINGLE_FILE builds everything as one translation unit; a Visual Studio project is included, no CMake) |
| **Dependencies** | none beyond the C/C++ standard headers (emmintrin.h when SSE2 is enabled) |
| **Minimum toolchain** | C++ without a documented standard; aras-p built it as C++17 with Visual Studio 2022, clang 14 (clang-cl) and Apple clang 13 |
| **Platforms** | any; SSE2 SIMD on x86/x64 (CVTT_USE_SSE2 is defined automatically when SSE2 is available), scalar ParallelMath elsewhere including ARM64 (no NEON path); the decoders are scalar on every platform |
| **Thread safety** | not documented for the decoders; from the code they keep all state on the stack and read const tables, so concurrent calls on different blocks look safe; the README says ETC encoder scratch data may move between threads but must not be used by two encode calls at once |
| **Drop-in for the baseline** | false - not a bcdec or DirectXTex replacement: it decodes only BC6H and BC7, in fixed batches of 8 blocks into PixelBlockF16/PixelBlockU8 structs that the caller must scatter into the image |

## Gotchas

- Public DecodeBC6HU/DecodeBC6HS/DecodeBC7 always read 8 blocks (128 bytes) and write 8 output blocks; decoding a single block or an image whose block count is not a multiple of 8 needs padded buffers, or the cvtt::Internal::...::UnpackOne functions from ConvectionKernels_BC67.h that the benchmark used (not in the public header).
- The BC6H decoder was broken until the day of the measurement: aras-p's issue #6 (2022-06-22) reported that UnpackOne produced 'something entirely else', and commit 350416d 'Fix bit framing error in BC6H decoder' (2022-06-23) fixed it; that commit is the one benchmarked and the last in the repo. Any copy taken from an older commit decodes BC6H incorrectly.
- Godot's thirdparty/cvtt (pinned at 350416d) still applies 0001-revert-bc6h-reorg.patch from PR #73715 (February 2023, a BC6H quality-regression fix), which swaps the generated per-mode BC6H read/write code, including inside UnpackOne, back to the older per-bit mode-descriptor tables. Copies taken from Godot therefore do not contain the decoder that was measured.
- Reserved or invalid BC6H mode bits decode silently to black with alpha 1.0, with no error return; the harness's output-hash check only prints a warning on mismatch, so bit-exactness of the timed output rests on the post's statement that only Compressonator differed on BC6H.

## Known shortcomings

- BC6H decode margin is tiny in the aras-p 2022 charts (1.19x over bcdec with VS2022, ties bcdec at 105 vs 104 Mpix/s on clang 14) and it is slower than bcdec and bc7enc_rdo on BC7; BC6H is marked Experimental; the harness times the internal UnpackOne, its hash check only warns, macOS flags are unstated (Windows presets RelWithDebInfo plus /Ob2, Ryzen 5950X). Abandoned since 2022-06-23.
- Enricher: mostly an encoder library that decodes only BC6H and BC7 with a scalar decoder; the BC6H decoder was broken until the measured commit 350416d (aras-p issue #6, fixed 2022-06-23), and Godot pins the same commit but applies 0001-revert-bc6h-reorg.patch (PR #73715), which swaps UnpackOne's generated BC6H read code back to the old descriptor tables, so Godot copies lack the measured decoder; public Decode functions take fixed 8-block batches; the harness hash check only warns; tie with bcdec on clang 14.

## Caveats and trade-offs

Decoder only: the README makes only an unquantified claim ('very high quality at good speed') and labels its BC6H support 'Experimental'; no encode comparison against ispc_texcomp, bc7enc or Compressonator was found. The BC6H margin is small (1.19x over bcdec with VS2022, a 1% tie with clang 14, 1.04x over SwiftShader on M1 Max) and the post itself says 'by a small margin'. The bcdec measured was e3ca0 (2022-06-23, right after aras-p's speedup PR #1); the harness later moved its bcdec submodule to 026acf9 (2022-09-15) without new charts, so current bcdec may close the gap and a re-run is needed. The harness calls the internal per-block API cvtt::Internal::BC6HComputer::UnpackOne rather than the public cvtt::Kernels::DecodeBC6HU, and converts each half to float with its own half_to_float_fast5 inside the timed loop, so all BC6H decoders are timed to the same float32 RGB output (bcdec through bcdec_bc6h_float). Output hashes are checked against _hashes.txt but a mismatch only prints a warning. Windows flags come from the public CMake presets; macOS flags are not stated. The post text was read from raw.githubusercontent.com/aras-p/aras-p.hugo (content/blog/2022/06-bcn-decode-libraries.md) because aras-p.info is blocked here; the figures are the printed bar labels of static/img/blog/2022/bcn-decode-win-vs2022.png, bcn-decode-win-clang14.png and bcn-decode-mac.png. The measured commit (2022-06-23, 350416d per the harness README) is dated the same day as the repo's last commit, 'Fix bit framing error in BC6H decoder'; nothing has been committed since, so the project is abandoned.

Stand-alone SPMD-style SIMD kernels extracted from Convection Texture Tools (CVTT); SIMD ops and 16-bit math; the API works on cvtt::NumParallelBlocks blocks at a time, so callers must pad partial batches. README lists BC6H as 'Experimental' and 11-bit EAC as 'Experimental'; BC7, BC1-5 and ETC1/ETC2 as complete; no ASTC or PVRTC. The faster-decode result is for BC6H only.

## Maintenance

Abandoned since 2022-06-23 (the BC6H bit-framing fix that was benchmarked); MIT-licensed with a DirectXTex-derived notice, 53 stars, and vendored by Godot at that commit but with the BC6H reorganisation reverted. Copyable, but treat BC6H as the README does: experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent public harness aras-p/bcn_decoder_tester (src/main.cpp: 20 runs per DDS file, convection submodule pinned at 350416d, output-hash check that only warns) with Windows flags in CMakePresets.json (x64-release and x64-release-clang = RelWithDebInfo) plus /Ob2 in CMakeLists.txt, compilers VS2022 and clang 14 named in the chart titles, CPU Ryzen 5950X; all three chart PNGs show convection as the top BC6Hu bar. The measured convection commit is dated the same day as the repo's last commit (a BC6H bit-framing fix), so there is no later-fixed-code cap; the macOS chart lacks flags but the Windows charts alone meet A.
- **Verifier notes:** Numbers verified verbatim against all three chart PNGs and the post source; tier A stands on the Windows charts (public harness, pinned submodules, RelWithDebInfo plus /Ob2, Ryzen 5950X), consistent with retier-32's reading of the same post for bcdec. baseline_in_list set to false because bcdec and DirectXTex are not among the image-codecs baselines (libjpeg-turbo, libpng, libwebp, libavif). Shortcomings to record: tiny BC6H margin (tie with bcdec on clang 14), slower than bcdec and bc7enc_rdo on BC7, BC6H marked Experimental, internal API timed, harness hash check warns only, macOS flags unstated, abandoned since 2022-06-23.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** current re-run of bcn_decoder_tester
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2022/bcn-decode-win-vs2022.png>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2022/bcn-decode-win-clang14.png>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2022/bcn-decode-mac.png>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/content/blog/2022/06-bcn-decode-libraries.md>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/readme.md>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/src/main.cpp>
  - <https://github.com/elasota/ConvectionKernels>
  - <https://github.com/elasota/ConvectionKernels/commits>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/README.md>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels.h>
- **Sources the enricher read:**
  - <https://github.com/elasota/ConvectionKernels>
  - <https://github.com/elasota/ConvectionKernels/commits/master>
  - <https://github.com/elasota/ConvectionKernels/issues?q=is%3Aissue>
  - <https://github.com/elasota/ConvectionKernels/issues/6>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/README.md>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels.h>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels_Config.h>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels_API.cpp>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels_BC67.cpp>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels_BC67.h>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels_BC6H_IO.cpp>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels_ParallelMath.h>
  - <https://raw.githubusercontent.com/elasota/ConvectionKernels/HEAD/ConvectionKernels_SingleFile.cpp>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/readme.md>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/aras-p/bcn_decoder_tester/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/content/blog/2022/06-bcn-decode-libraries.md>
  - <https://github.com/aras-p/aras-p.hugo/tree/master/content/blog/2020>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/content/blog/2020/12-texcompr.md>
  - <https://raw.githubusercontent.com/godotengine/godot/master/thirdparty/README.md>
  - <https://raw.githubusercontent.com/godotengine/godot/master/thirdparty/cvtt/patches/0001-revert-bc6h-reorg.patch>
  - <https://github.com/godotengine/godot/pull/73715>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/elasota/convectionkernels`) · [data/wave10/enrich/raw/github_com_elasota_convectionkernels.json](../../../data/wave10/enrich/raw/github_com_elasota_convectionkernels.json) (enrichment confidence 0.75)

</details>
