# etcpak

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> SIMD multithreaded ETC1/ETC2/EAC/BC encoder: 500-1400x faster than Etc2Comp/ETCPACK multithreaded, 9-21x single-thread scalar, at lower quality.

| | |
|---|---|
| **Beats** | Etc2Comp (effort=0, error metric rgba) and ETCPACK 4.0.1 (reference ETC2 encoder in Arm Mali Texture Compression Tool 4.3.0), as measured in the QuickETC2 paper (ACM TOG 2020); the current README only cites the NVIDIA in-driver ETC2 decoder (42.5 Mpx/s) for decompression, and the 2016-2018 README (etcpak 0.5) timed PVRTexToolCLI 3.5, Mali etcpack 4.2, etc2comp and crunch (rg-etc1) 1.04. |
| **Claimed result** | QuickETC2 paper Table 1 (Ryzen 7 3700X, fastest settings, 55 RGB textures): etcpak 0.7 ETC1 3250 Mpx/s and ETC2 planar-only 1931 Mpx/s (16 threads, SIMD) vs Etc2Comp ETC2 3.8 Mpx/s (16 threads) and ETCPACK ETC2 1.4 Mpx/s (single-threaded); with one thread and SIMD disabled, etcpak ETC1 44.6 and ETC2(p) 28.9 Mpx/s vs Etc2Comp 3.1 and ETCPACK 1.4 Mpx/s. Ratios (derived from page data): ETC2(p) about 508x vs Etc2Comp and 1379x vs ETCPACK at highest-performance settings, 9.3x and 20.6x single-thread scalar. Quality is lower: etcpak ETC2(p) 36.82 dB PSNR vs 37.89 dB (Etc2Comp) and 38.09 dB (ETCPACK); etcpak ETC1 35.87 dB. The paper's SIGGRAPH 2020 talk table gives etcpak 0.6.1 1782 Mpix/s vs Etc2Comp 4.0 and ETCPACK 1.3 Mpix/s. First-party README (Ryzen 9 7950X, 16K x 16K atlas): ETC1 797 Mpx/s ST / 9613 MT, ETC2 356/6378, BC1 5730/10174, BC3 2437/8568, BC7 12.1/225; ETC2 decode 599 Mpx/s ST vs 'Nvidia in-driver ETC2 decoder can do only 42.5 Mpx/s' (about 14x, derived from page data; no machine given for the NVIDIA figure). Historical README table (etcpak 0.5, 2016, Xeon E3-1230 v3, 8192x8192 RGB): etcpak 0.5 AVX2 ETC1 872.6 Mpx/s vs crunch (rg-etc1) 1.04 11.53, etc2comp effort=0 1.96, PVRTexToolCLI 3.5 1.3 (total time including image decode) and Mali etcpack 4.2 0.777 Mpx/s. |
| **Workload** | Paper: compression of 64 test textures (256x256 to 8192x8192; 55 RGB, 9 RGBA) with each encoder at its fastest setting, highest-performance (16 threads, SIMD) and baseline-control (1 thread, no SIMD) settings, PSNR and SSIM reported. README: ETC1, ETC2, BC1, BC3 and BC7 compression and decompression of a non-public real-life RGBA 16K x 16K atlas, single-threaded and multithreaded. |
| **Metric** | throughput |
| **Hardware** | QuickETC2 paper: AMD Ryzen 7 3700X @3.6 GHz, 8 cores with SMT, 32 GB RAM, Ubuntu 20.04. README: AMD Ryzen 9 7950X, Intel i7 1185G7, Apple M3 Max (historical README: Intel Xeon E3-1230 v3). |
| **Adoption** | 331 stars, 50 forks; README says it is used in production builds by millions of users; the QuickETC2 paper says Unity integrated etcpak (alongside ETCPACK and Etc2Comp) since Unity 2017.3 |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/wolfpld/etcpak) · [benchmark](https://raw.githubusercontent.com/nahjaeho/nahjaeho.github.io/master/papers/SA20/QUICKETC2_SA20.pdf) |

## Verdict

The independent QuickETC2 paper (ACM TOG 39(6), 2020; Ryzen 7 3700X, Ubuntu 20.04, compiler and flags not stated) timed etcpak 0.7 on 55 RGB textures. ETC2 planar-only ran at 1931 Mpx/s with 16 threads and SIMD (28.9 Mpx/s single-threaded scalar) against Etc2Comp effort 0 at 3.8 (3.1) and single-threaded ETCPACK 4.0.1 at 1.4 Mpx/s, at 36.82 dB vs 37.89/38.09 dB PSNR. Today's etcpak (1.0 and later) ships the paper's QuickETC2 T/H-mode and early mode-decision code, whose row in the same table is 2577 Mpx/s (40.6 single-threaded scalar) at 37.17 dB. The README's own Ryzen 9 7950X numbers (for example ETC2 356 Mpx/s single-threaded) time no competitor.

## Use it when

- Development or iteration builds that have to re-encode many or very large textures (8K-16K atlases) to ETC1/ETC2 in seconds rather than hours
- Runtime or on-device texture encoding where a few ms per 4K texture matters more than about 1 dB of PSNR (Godot uses it for its in-engine ETC/BC compression)
- Producing ETC2 for OpenGL ES 3 / Android targets when Etc2Comp at effort 0 or ETCPACK is the current bottleneck
- Fast BC1/BC3/BC4/BC5 encoding on x86-64 or AArch64 when quality is checked by eye rather than by a PSNR target

## Skip it when

- Final shipping assets where quality matters: in the QuickETC2 paper the etcpak-derived ETC2 is 0.72-1.47 dB PSNR below Etc2Comp and ETCPACK, and the paper names etcpak's ETC1 logic as the cause. Open issues report artefacts on subtle blue/white shades (#48) and over-brightened output (#40)
- Colour gradients whose channels move in opposite directions (for example red to green) in BC1: endpoints are the bounding-box min/max corners, with no PCA or cluster fit, so the encoder cannot represent that axis (from reading ProcessDxtc.cpp)
- Needs it does not cover: ETC2 RGB with punch-through alpha (open issue #21), ASTC, KTX/KTX2 output, or input formats other than PNG
- Portable binaries: SIMD is chosen at compile time and CMake defaults to -march=native with no runtime dispatch, so a binary built on a new CPU can crash with an illegal instruction on an older one (issue #39, SSSE3 shuffle on an Athlon II)
- High-quality BC7: the BC7 encoder is bc7enc limited to modes 1/6 (RGB) and 5/6/7 (RGBA), and the README's BC7 speed (12.1 Mpx/s single-threaded on a 7950X) has no competitor timing

## How it is fast

The ETC1 path does no endpoint search. It averages the block's colour for both 2x4/4x2 sub-block splits, keeps the split with the lowest error, then picks the best intensity-modifier table and selectors with SSE4.1/AVX2/NEON error arithmetic. Solid blocks exit early. ETC2 adds the QuickETC2 scheme (Nah, ACM TOG 2020; shipped in etcpak 1.0 as 'heuristics'): a luma-range test sends very-low-contrast blocks straight to planar mode (thresholds 0.03/0.09/0.38 in ProcessRGB.cpp). Only high-contrast blocks go to a luma-ordered T/H-mode search. BC1 takes per-channel bounding-box min/max endpoints with an inset and assigns selectors by projecting the summed channel offsets, all in SSE/AVX/NEON registers. BC7 is a SIMD-rewritten copy of Rich Geldreich's bc7enc (AVX2/AVX-512 paths). Images are cut into 32-block-row slices on a thread pool.

## Compared with alternatives

Pick etcpak over Goofy (ETC1/DXT1 only) when you need full ETC2 (planar, T and H modes, EAC alpha), BC3-BC5 or mipmapped PVR/DDS output from one tool. Pick bc7enc or bc7e directly for BC7 quality control, and ICBC for higher-quality BC1. Basis Universal's etc1f only claims, with no numbers, to be faster than etcpak.

## Integration

| | |
|---|---|
| **Form** | source-drop (the repo builds only a CLI executable; copy ProcessRGB/ProcessDxtc, Tables, Dither, Math, Vector, ForceInline and ProcessCommon, plus bc7enc.cpp for BC7) |
| **Dependencies** | Encoder files: none beyond the C++ standard library. CLI: libpng via pkg-config, and Tracy fetched from its master branch by CPM at configure time (network needed). BC7 decode uses the bundled bcdec.h (MIT) |
| **Minimum toolchain** | CMake 3.29 and C++20 (CMAKE_CXX_STANDARD 20; bc7enc.cpp includes &lt;bit&gt;); GCC/Clang/MSVC paths are present, but SIMD on MSVC depends on __SSE4_1__/__AVX2__ being defined (since July 2026 __AVX__ implies SSE4.1) |
| **Platforms** | x86-64 (SSE4.1, AVX2, AVX-512 paths), AArch64 NEON (ARMv7 NEON fixed per issue #25), scalar fallback; SIMD level fixed at compile time |
| **Thread safety** | Compress\* functions work on caller buffers and only read shared tables, so different slices can be encoded in parallel. bc7enc_compress_block_init() must run once before BC7 use, and the bundled TaskDispatch pool is a process-wide singleton. |
| **Drop-in for the baseline** | no |

## Gotchas

- --disable-heuristics does more than turn off the mode shortcut: in ProcessRGB_ETC2 the T/H-mode search runs only inside the heuristics branch. Without it, ETC2 output is limited to ETC1, planar and solid blocks.
- Width and height must be multiples of 4. This is checked only by assert() in BlockData and Bitmap, so release builds do not reject other sizes. The CLI's PNG loader also ignores setjmp's return value, so a libpng error does not abort cleanly.
- Licence hygiene: LICENSE.txt is BSD-3 but keeps template placeholders ('&lt;organization&gt;', '&lt;COPYRIGHT HOLDER&gt;'; open issue #24). ProcessRGB.cpp holds T/H helper functions marked '(C) Ericsson AB 2005-2013. All Rights Reserved' from ETCPACK v2.74, which point to an Ericsson statement the file does not include.
- Channel order is easy to get wrong: ETC paths expect BGRA-ordered input while BC paths expect RGBA (Application.cpp sets bgr only for ETC codecs; issues #32 and #34 complain about the naming).

## Known shortcomings

- Upgraded C to B on the peer-reviewed QuickETC2 paper (ACM TOG 39(6) 2020, Ryzen 7 3700X; PDF reached via raw.githubusercontent.com/nahjaeho/nahjaeho.github.io): ETC2 planar 1931 Mpx/s vs Etc2Comp 3.8 and ETCPACK 1.4, single-thread scalar 28.9 vs 3.1/1.4 (9.3x/20.6x derived). Planar-only ETC2 at about 1.1-1.3 dB lower PSNR; no compiler or flags. Baselines are texture-compression tools, not the category's image codecs.
- The current ETC2 encoder is the merged QuickETC2 (release 1.0; thresholds 0.03/0.09/0.38 match the paper), so the paper's 2577 Mpx/s at 37.17 dB row fits today's code better than the 0.7 planar-only row. CLI only with no library target; -march=native with no runtime dispatch (issue #39 SIGILL); --disable-heuristics turns off the T and H modes; BC1 uses bounding-box endpoints without PCA; BC7 is the vendored bc7enc; multiple-of-4 dimensions are checked only by assert; ETCPACK code carries Ericsson all-rights-reserved snippets and the LICENSE has placeholders (#24); open quality issues #48 and #40.

## Caveats and trade-offs

Speed comes at lower quality: in the QuickETC2 paper etcpak's ETC2 mode is planar-only (no T- and H-modes at version 0.7), so it searches a smaller mode space than Etc2Comp and ETCPACK and scores about 1.1-1.3 dB lower PSNR; compare at matched quality before treating the ratios as like-for-like. In the paper's highest-performance setting ETCPACK ran single-threaded while etcpak used 16 threads; the single-thread scalar ratios (9.3x, 20.6x) are the fair algorithmic comparison. Compiler and flags are not stated anywhere; etcpak's CMakeLists.txt enables -march=native by default. The README's own benchmark (Application.cpp -b mode) uses a non-public atlas and times no competitor; the competitor table was removed from the README in 2018 and the NVIDIA decoder figure has no stated machine. The paper's numbers are for etcpak 0.7 / 0.6.1, not the current 2.1. BC1/BC3/BC7 speed claims have no competitor numbers.

Quality is explicitly not the goal ('best suited for rapid assets preparation during development, when graphics quality is not a concern'). Handles ETC1, ETC2, BC1-BC7 and decoding; Benchmarked on x86 (Ryzen, Intel) and Apple M3 Max.

## Maintenance

Actively maintained by Tracy's author (release 2.1 in February 2026, last commit 2026-09-13), BSD-3 and vendored by Godot; its 11 open issues are mostly quality and API complaints with no maintainer replies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the peer-reviewed QuickETC2 paper (ACM Trans. Graph. 39(6) Article 270, Dec 2020, by a third party) times etcpak 0.7 against Etc2Comp (effort=0) and ETCPACK 4.0.1 (the reference ETC2 encoder in Arm's Mali Texture Compression Tool) on 64 textures on a Ryzen 7 3700X under Ubuntu 20.04 with PSNR/SSIM reported. Not A: compiler and flags are not stated and the harness is only an ACM supplement (patch plus executables), not a public repo; the README's own numbers have no competitor timing.
- **Verifier notes:** The search agent missed the independent evidence: the QuickETC2 paper PDF is reachable on raw.githubusercontent.com (nahjaeho.github.io repo) and gives etcpak vs Etc2Comp/ETCPACK speed and PSNR on a named CPU, so the entry moves C to B. Etc2Comp and ETCPACK/Mali tool are recognisable ETC incumbents; the win is real but at lower quality (planar-only ETC2, \~1 dB PSNR less). Aras Pranckevicius's 'Texture Compression in 2020' blog also covers etcpak but is blocked here (search snippet only, not used for the tier).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/wolfpld/etcpak>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/README.md>
  - <https://github.com/wolfpld/etcpak/commits/master>
  - <https://github.com/wolfpld/etcpak/commits/master/README.md>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/0ebbc71/README.md>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/fb8145b/README.md>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/449cd4d/README.md>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/6305db7/README.md>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/a77d5a3/README.md>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/Application.cpp>
  - <https://raw.githubusercontent.com/nahjaeho/nahjaeho.github.io/master/papers/SA20/QUICKETC2_SA20.pdf>
  - <https://raw.githubusercontent.com/nahjaeho/nahjaeho.github.io/master/papers/SIG2020.pdf>
- **Sources the enricher read:**
  - <https://github.com/wolfpld/etcpak>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/README.md>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/Application.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/ProcessRGB.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/ProcessRGB.hpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/ProcessDxtc.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/ProcessDxtc.hpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/bc7enc.h>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/bc7enc.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/bcdec.h>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/Decode.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/BlockData.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/BlockData.hpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/TaskDispatch.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/DataProvider.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/Bitmap.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/Tables.cpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/ForceInline.hpp>
  - <https://raw.githubusercontent.com/wolfpld/etcpak/HEAD/simd.py>
  - <https://github.com/wolfpld/etcpak/issues?q=is%3Aissue>
  - <https://github.com/wolfpld/etcpak/issues/6>
  - <https://github.com/wolfpld/etcpak/issues/39>
  - <https://github.com/wolfpld/etcpak/issues/40>
  - <https://github.com/wolfpld/etcpak/issues/48>
  - <https://github.com/wolfpld/etcpak/commits/master>
  - <https://github.com/wolfpld/etcpak/releases>
  - <https://raw.githubusercontent.com/nahjaeho/nahjaeho.github.io/master/papers/SA20/QUICKETC2_SA20.pdf>
  - <https://raw.githubusercontent.com/godotengine/godot/master/thirdparty/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/wolfpld/etcpak`) · [data/wave10/enrich/raw/github_com_wolfpld_etcpak.json](../../../data/wave10/enrich/raw/github_com_wolfpld_etcpak.json) (enrichment confidence 0.75)

</details>
