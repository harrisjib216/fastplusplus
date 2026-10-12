# bc7enc (rgbcx BC1 and bc7enc16 BC7 encoders)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (BC7 encoder in C)` · `MIT OR Unlicense` · 🔴 abandoned

> Scalar single-file BC1-5 (rgbcx.h) and modes-1/6 BC7 encoders; first-party tables beat ispc_texcomp, independent tests mostly do not.

| | |
|---|---|
| **Beats** | libsquish (BC1 cluster fit); Intel ispc_texcomp (BC7); also AMD Compressonator and DirectXTex CPU BC7 |
| **Claimed result** | README (first-party, bc7enc16 era, 31 images, multithreaded, luma PSNR): ispc_texcomp slow 355.4 s at 48.6 dB vs bc7enc16 uber0/max_partitions 64 38.3 s at 49.6 dB (9.3x, derived from page data). Independent (Aras Pranckevicius, Dec 2020, i9-8950HK, clang 11.0.3, 20 Unity textures, luma PSNR, derived from chart data): bc7enc level 64.4 at 0.34x the speed of ispc_texcomp fast (faster on 2 of 20), level 16.0 at 0.99x of ispc_texcomp vfast at -0.35 dB; wins only against ispc_texcomp slow at lower quality (2.62x at -0.79 dB, 10.6x at -1.45 dB). BC1: README claims rgbcx is 3-4x faster than libsquish cluster fit with no timings; Aras measured rgbcx level 0 at 1.07x stb_dxt (-0.17 dB) and ispc_texcomp BC1 2.1x faster than rgbcx 0. |
| **Workload** | Encoding 31 images (Kodak corpus plus others) to BC1 and BC7, comparing total encode time and average PSNR at matched quality settings (multithreaded with OpenMP). |
| **Metric** | throughput |
| **Hardware** | dual Xeon workstation (CPU model not stated) |
| **Compiler and flags** | Not stated; multithreaded with OpenMP; ispc_texcomp called with 64 blocks at a time using AVX instructions |
| **Adoption** | 243 stars, 24 forks; archived 2026-01-28; superseded by richgel999/bc7enc_rdo, which carries rgbcx and the bc7enc BC7 encoder |
| **Last commit** | 2022-07-04 |
| **Links** | [repository](https://github.com/richgel999/bc7enc) · [benchmark](https://github.com/richgel999/bc7enc) |

## Verdict

The README's BC7 table is first-party: 31 images (Kodak plus others), encode time only, OpenMP on an unnamed dual Xeon, compiler unstated, ispc_texcomp at AVX. Its largest wins are against ispc_texcomp slow (9.3x at +1.0 dB Luma-PSNR in perceptual mode) and a locally patched DirectXTex (263x). At matched RGB PSNR it shows parity with ispc_texcomp fast. Independent per-image data from Aras Pranckevicius (December 2020; i9-8950HK, 12 threads, Apple clang 11.0.3 up to AVX2; 20 Unity textures; bc7enc and rgbcx built from April 2020 code) reproduce the speed lead only against ISPC slow (bc7enc 64.4: 2.62x geomean, faster on 20/20, at 0.79 dB lower mean Luma-PSNR). Against ISPC fast, basic and vfast at similar quality, bc7enc is slower or tied. The BC1 claims against libsquish and Compressonator have no numbers anywhere.

## Use it when

- You need a dependency-free, portable scalar BC1/BC3/BC4/BC5 encoder with a single quality knob, e.g. in an asset pipeline that cannot run the ISPC compiler or on ARM/WASM, where SIMD-only encoders lose their edge.
- Highest-quality BC1 when encode time does not matter. In Aras Pranckevicius's 2020 test (20 Unity textures, i9-8950HK, 12 threads) rgbcx level 18 had the best DXTC Luma-PSNR of any library (38.47 dB) at 4.7 Mpix/s.
- Fast BC1 near stb_dxt quality: level 0 was 1.07x stb_dxt's speed at 0.17 dB lower PSNR (per-image geomean, derived from Aras's chart data). Goofy's README measured rgbcx 1.08 level 0 at 60 MP/s and 40.85 dB, against stb_dxt at 43 MP/s and 40.82 dB, on one thread.
- Opaque, photographic BC7 content scored on luma, where bc7enc's perceptual YCbCr metric pays off: on kodim23crop it was 6.9x faster than ISPC slow at +1.40 dB Luma-PSNR in Aras's data.
- Learning or prototyping BC7: about 2,200 lines of readable C covering endpoint fitting, p-bits, partition estimation and block packing.

## Skip it when

- Production BC7. In the same independent run, bc7e fast was about 9x faster than bc7enc's best preset (per-image geomean) at 0.70 dB higher mean Luma-PSNR. The author's own README points to bc7e.ispc in bc7enc_rdo, and basis_universal carries bc7e_scalar and bc7f.
- Whenever ispc_texcomp's fast or veryfast presets are available. At matched Luma-PSNR on Aras's 20 textures, ISPC fast (10.10 Mpix/s, 45.36 dB) was 2.6x faster than bc7enc 64.4 (3.82 Mpix/s, 45.48 dB), and bc7enc 16.0 tied ISPC vfast on speed at 0.35 dB lower.
- BC7 normal maps, alpha gradients or mixed content. bc7enc lost up to 4-5 dB to ISPC on normal maps, sprites and frymire in Aras's data, and open issue #2 reports blocky, sawtooth alpha on translucent gradients, with no maintainer reply.
- Throughput-critical BC1 on x86 with SIMD. ISPC BC1 was 2.1x faster than rgbcx level 0 at equal mean PSNR, and icbc level 8 (AVX2) was 3.2x faster than rgbcx level 10 at 0.11 dB lower (per-image geomeans, derived).
- You need upstream maintenance: archived on 2026-01-28 with the last code change in February 2021; issues #2, #3 and #5 and PR #6 (missing abs/memcpy/memset includes) were never answered.

## How it is fast

rgbcx's 'prioritized cluster fit' replaces cluster fit's walk over all orderings with precomputed tables. There are 969 unique 4-colour selector histograms (g_unique_total_orders4) with precomputed least-squares factors, plus, for each ordering, a ranked list of up to 128 other orderings likely to help (g_best_total_orderings4). Higher levels simply try more of them (level 10 tries 20, level 17 tries 128); low levels use bounding-box, 2D least-squares or PCA endpoint fits like stb_dxt. bc7enc's speed comes from searching only two BC7 modes. Mode-1 partitions are scanned in usage-frequency order with a cheap per-subset error estimate, and an optional 'filterbank' skips lesser-used partitions unless the best of the first 14 predicts them (about 11% faster for about 0.08 dB). Single-colour subsets use precomputed optimal-endpoint tables, and 'uber' levels 1-4 add selector perturbation passes.

## Compared with alternatives

Pick rgbcx over ICBC when you need BC3/BC4/BC5 as well as BC1, or a scalar build (scalar ICBC is slower than RGBCX at most levels in its own chart). Pick Goofy only for real-time BC1, where it is far faster at about 4 dB lower PSNR. For BC7, prefer bc7e (or bc7e_scalar/bc7f in Basis Universal); bc7enc is only worth picking for its tiny plain-C footprint.

## Integration

| | |
|---|---|
| **Form** | source-drop (rgbcx.h single header with RGBCX_IMPLEMENTATION; bc7enc.c/.h and bc7decomp.cpp/.h as separate files) |
| **Dependencies** | none for the encoders (libc/libm and &lt;algorithm&gt;); the test app adds lodepng and dds_defs.h |
| **Minimum toolchain** | C++11 for rgbcx.h (enum class, static_assert); C99 for bc7enc.c (inline functions in the header); CMake 2.8 file builds the test app with -fno-strict-aliasing |
| **Platforms** | any: portable scalar C/C++, no SIMD or intrinsics; tested by the author with MSVC, and clang warnings fixed in 2020 |
| **Thread safety** | rgbcx::init() and bc7enc_compress_block_init() write global tables and are not thread safe; call them once before starting threads. After that, all rgbcx encode and decode functions are documented as thread safe, and bc7enc_compress_block reads only static tables and stack state. |
| **Drop-in for the baseline** | partial: per-block C/C++ calls with your own block loop and threading, unlike libsquish's image API or ispc_texcomp's rgba_surface batches; BC1 output for a chosen GPU vendor needs the matching bc1_approx_mode |

## Gotchas

- Skipping the init call does not fail in release builds. bc7enc only asserts, and its header warns you will 'get artifacts'; rgbcx needs init() before any encode or decode.
- bc7enc_compress_block_params_init() selects the perceptual YCbCr metric by default. Call bc7enc_compress_block_params_init_linear_weights() if you judge output by RGB PSNR, which is the metric under which the README shows ispc_texcomp ahead.
- BC1 at level 5 and above with use_transparent_texels_for_black codes dark texels with the 3-colour transparent index, so your shader must ignore sampled alpha. An unknown level silently falls back to level 5, and level 19 is a hidden, extremely slow training mode.
- The default rgbcx build carries a 969x128 uint16_t ordering table (about 248 KB). Define RGBCX_USE_SMALLER_TABLES 1 for the 969x32 table, which caps BC1 levels at 32 orderings.

## Known shortcomings

- Texture encoder (BC7) whose baseline ispc_texcomp is not a listed incumbent. README claims 2-3x at matched PSNR/SSIM and about 8x against the slow profile with no table, machine or harness; the independent aras-p blog is blocked (snippet directional only). Repo archived 2026-01-28; the encoder ships inside bc7enc_rdo (used by todds) and as a scalar C++ port in basis_universal.
- Texture encoder (BC1 and BC7) whose baselines ispc_texcomp and DirectXTex are not listed incumbents; ispc_texcomp is faster in the ultrafast rows, and the matched-RGB-PSNR update shows parity (41.42 s vs 41.45 s); perceptual rows are scored on luma PSNR, which favours bc7enc16. Only BC7 modes 1 and 6, so different work from ispc_texcomp; the 263x over DirectXTex is against a slow baseline. Dual Xeon unnamed, no flags. Licence MIT OR Unlicense.
- Independent data contradicts the BC7 headline (retier-21 narrows the claim): in Aras Pranckevicius's 2020 run (i9-8950HK, clang 11.0.3, 20 Unity textures) bc7enc level 64.4 runs at 0.34x the speed of ispc_texcomp fast and level 16.0 at 0.99x of vfast at -0.35 dB, winning only against ispc_texcomp slow at lower quality (2.62x at -0.79 dB, 10.6x at -1.45 dB); it leads on opaque photo crops and loses up to 4-5 dB on normal maps and alpha. The repo's test.cpp is single-threaded without OpenMP, so the README's harness is absent; the BC1 claim against libsquish and Compressonator is measured nowhere (Aras: rgbcx 0 is 1.07x stb_dxt at -0.17 dB; ispc_texcomp 2.1x faster than rgbcx 0); issue #3's solid-block bug is not confirmed in rgbcx v1.12.

## Caveats and trade-offs

Most timings are for the original bc7enc16 release (the README says the latest bc7enc16.c is 8-27% faster with mode 1 enabled); this repo's bc7enc.c adds alpha modes and is not exactly the code timed. The encoders do different work: bc7enc16 uses only BC7 modes 1 and 6 for opaque blocks while ispc_texcomp searches all modes, and the perceptual rows are scored on luma PSNR, the metric bc7enc16's perceptual mode optimizes and ispc_texcomp does not, which favours bc7enc16. At matched RGB PSNR the later update shows parity with ispc_texcomp fast, and in the ultrafast rows ispc_texcomp is faster (1.9 s vs 3.8 s at 42.7 dB non-perceptual; 1.9 s vs 8.9 s perceptual, where bc7enc16 scores 48.4 vs 46.2 dB). The test machine is an unnamed dual Xeon; compiler and flags are unstated; ispc_texcomp was called 64 blocks at a time with AVX; the comparison harness is not in the repo. The DirectXTex run used a locally patched pbit bugfix, and the page's own times (9485.1 s vs 355.4 s for ispc_texcomp slow) show DirectXTex's CPU BC7 path is a very slow baseline, so the 263x figure overstates the practical gain. The BC1 claims have no numbers on the page. The repo was archived on 2026-01-28, and its README calls the BC7 encoder unvectorized work in progress and points to bc7enc_rdo and bc7e.ispc. Dual-licensed MIT or Unlicense (public-domain option, no patent grant).

The BC7 encoder here supports only modes 1 and 6 for RGB (plus modes 5 and 7 for alpha) and is scalar, not vectorized, so it will not match full-mode encoders on every texture; the author points to bc7e and bc7enc_rdo for best BC7 quality. Single-source C/C++ with no dependencies; archived 2026-01-28.

## Maintenance

Archived on 2026-01-28, with the last code commit on 2021-02-03; MIT or Unlicense and trivially vendorable, but the maintained rgbcx and BC7 code (with RDO) lives in richgel999/bc7enc_rdo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README carries a first-party BC7 table (31 images, encode time and average PSNR) against ispc_texcomp and DirectXTex on an unnamed dual Xeon with OpenMP, no compiler or flags, and the comparison harness is not in the repo; the BC1 claims against libsquish and Compressonator have no numbers at all. First-party with partial methodology, and the 263x DirectXTex figure exceeds 50x with flags unstated, so C.
- **Verifier notes:** All quoted numbers match the README rows; the corrected claim adds the matched-RGB-PSNR parity row and the DirectXTex mode-6 row so the headline wins are not read in isolation. Baselines ispc_texcomp, DirectXTex, libsquish and Compressonator are all recognisable texture-encoder incumbents; baseline_in_list false is correct. bc7enc_rdo (not in the list) is the maintained successor of both this repo and bc7e; the orchestrator may want to treat the three together.
- **Fields the verifier corrected:** `license`, `stars_or_usage`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/richgel999/bc7enc>
  - <https://github.com/richgel999/bc7enc/commits>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/richgel999/bc7enc_rdo/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/richgel999/bc7enc>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/rgbcx.h>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/bc7enc.c>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/bc7enc.h>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/richgel999/bc7enc/HEAD/bc7decomp.h>
  - <https://github.com/richgel999/bc7enc/commits/master>
  - <https://github.com/richgel999/bc7enc/issues?q=is%3Aissue>
  - <https://github.com/richgel999/bc7enc/issues/2>
  - <https://github.com/richgel999/bc7enc/issues/3>
  - <https://github.com/richgel999/bc7enc/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/richgel999/bc7enc_rdo/HEAD/README.md>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/content/blog/2020/12-texcompr.md>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2020/texcompr/chart-bc7.html>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2020/texcompr/chart-dxtc.html>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/richgel999/bc7enc`) · [data/wave10/enrich/raw/github_com_richgel999_bc7enc.json](../../../data/wave10/enrich/raw/github_com_richgel999_bc7enc.json) (enrichment confidence 0.8)

</details>
