# Goofy (realtime DXT1/ETC1 encoder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (header-only, SSE2)` · `MIT` · 🟡 stale

> Header-only SSE2 BC1/ETC1 encoder, about 1.4 GP/s per core, trading about 4 dB PSNR for 24-400x speed.

| | |
|---|---|
| **Beats** | stb_dxt (ryg DXT1, STB_DXT_NORMAL); also rgbcx 1.08, icbc 1.0 and rg_etc1 1.04 |
| **Claimed result** | Goofy DXT1 1429 MP/s at 37.02 dB vs rgbcx v1.08 level 0 60 MP/s (40.85 dB), ryg stb_dxt 43 MP/s (40.82 dB), icbc v1.0 24 MP/s (41.00 dB); Goofy ETC1 1221 MP/s (36.30 dB) vs rg_etc1 v1.04 3 MP/s (40.87 dB). Ratios derived from page data: about 24x vs rgbcx, 33x vs stb_dxt, 60x vs icbc, 407x vs rg_etc1. |
| **Workload** | Single-thread compression of the repo's 42 test images (24 Kodak images, lena, baboon, monarch, peppers, sail, tulips, parrot_red, patterns, five PBR textures including a normal map, six Roblox images; list in Src/main.cpp), best of 128 runs per image, averaged speed (MP/s) and RGB-PSNR, each encoder at its fastest or lowest-quality setting. |
| **Metric** | throughput |
| **Hardware** | i7-7820HQ 2.9 GHz, single thread, fastest of 128 runs |
| **Adoption** | 91 stars |
| **Last commit** | 2024-01-29 |
| **Links** | [repository](https://github.com/SergeyMakeev/Goofy) · [benchmark](https://github.com/SergeyMakeev/Goofy) |

## Verdict

The author's 2020 README table (Src/main.cpp harness, i7-7820HQ single thread, best of 128 runs, 42 images; compiler and flags not stated, likely the repo's VS2017 Win64 build) gives Goofy DXT1 1429 MP/s at 37.02 dB against stb_dxt 43 MP/s at 40.82 dB (about 33x), rgbcx 1.08 level 0 60 MP/s (about 24x), icbc 1.0 fast 24 MP/s (about 60x), and Goofy ETC1 1221 MP/s against rg_etc1 1.04 low quality 3 MP/s (about 407x), all ratios derived from page data. Reading the harness narrows the init-in-loop concern: rgbcx's init returns at once after its first call and rg_etc1's is under 1% of its time, so only the icbc ratio is inflated (see measurement_notes), and the README's 'RGB-PSNR' sits about 4.8 dB above conventional RGB PSNR for every encoder alike.

## Use it when

- On-the-fly BC1 compression of runtime-generated or downloaded RGBA8 textures on x86-64, when encode time matters more than about 4 dB of PSNR (README: 1429 MP/s per thread on an i7-7820HQ).
- Fast 'preview' content builds with thousands of textures, re-encoding later with rgbcx, ICBC or bc7e for shipping.
- Live-sync editor tools: show a Goofy encode immediately, then replace it with a slow high-quality encode in the background.
- ETC1 targets where ETC1S-level quality is already acceptable: the README puts Goofy ETC1 (36.30 dB) level with Basis Universal ETC1S output (36.27 dB) on its image set, with no supercompression.

## Skip it when

- Shipping assets: on the README image set it scores 3.8-4.6 dB lower RGB-PSNR than stb_dxt, rgbcx level 0, icbc fast and rg_etc1 low quality, the fastest settings of those encoders.
- Normal maps (the README warns quality is much worse), alpha or punch-through textures, and any format other than BC1 and ETC1 (no BC3/BC4/BC5/BC7, ETC2 or ASTC; the README's DXT5/ETC2 alpha plan never landed and issue #5 asking about ETC2 is unanswered).
- ARM devices, where ETC1 is mostly used: GOOFY_SSE2 is hard-coded to 1, there is no NEON path, and the scalar emulation path needs a header edit and has no published speed numbers.
- Arbitrary image sizes or unaligned buffers without padding or copying first (width must be a multiple of 16, height of 4, and rows 16-byte aligned).
- Projects that need an active upstream: last commit 2024-01-29 (README and contributor WASM/CI work), and issues #4 and #5 from 2025 have no reply.

## How it is fast

Each call encodes four 4x4 blocks (a 16x4 pixel strip, one 64-byte cache line per row) entirely in 8-bit SSE2 lanes. Per-channel min/max via _mm_min_epu8/_mm_max_epu8 plus 4x4 transposes give bounding-box endpoints (quantised to RGB555 with shifts done as repeated _mm_avg_epu8). Luma is computed as YCoCg Y = avg(avg(R,B),G), and each pixel is classified against the block's luma midpoint and a 0.375\*range threshold. The two resulting byte masks are packed into 2-bit selectors with movemask. There is no endpoint search, least-squares refinement, floating point or error evaluation; for ETC1 the base colour is the block average and the intensity-table control byte comes from a 256-entry lookup on the luma range.

## Compared with alternatives

Pick Goofy over bc7enc/rgbcx or ICBC only when raw single-thread encode speed dominates and about 4 dB lower PSNR is acceptable; those encoders are the ones to use for shipping BC1. For ETC1, etcpak is the quality-and-speed incumbent (QuickETC2 paper: 3250 Mpx/s with 16 threads on a Ryzen 7 3700X, about 200 per thread, derived); Goofy's 1221 MP/s on one i7-7820HQ thread is a different machine and harness and a simpler ETC1S-only search, so prefer Goofy only for x86 previews where ETC1S quality is enough.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (SSE2 intrinsics from &lt;emmintrin.h&gt;) |
| **Minimum toolchain** | not documented; the header uses C++11 features and the repo's CMake builds it as C++17, with CI Release builds on MSVC, GCC and Clang |
| **Platforms** | x86/x86-64 with SSE2; WebAssembly via Emscripten SSE2 emulation (-msimd128 -msse2, used by the in-repo test page); no NEON |
| **Thread safety** | not documented; by inspection the encoder keeps no mutable global state (only static const tables) and spawns no threads, so concurrent calls on separate buffers look safe |
| **Drop-in for the baseline** | partial: produces standard BC1/ETC1 blocks, but the API is whole-image with size and alignment preconditions rather than stb_dxt's per-block call, and it has no quality or alpha options |

## Gotchas

- Loads use _mm_load_si128, so the input pointer and every row (stride) must be 16-byte aligned (the code asserts 64-byte). With NDEBUG the assert is compiled out and misaligned input crashes instead of failing cleanly. The Jan 2024 Linux port of the test harness hit exactly this ('compilation on linux (crashes though)', then 'fix alignment').
- The header #defines GOOFYTC_IMPLEMENTATION itself and has no include guard, so the non-inline compressDXT1/compressETC1 are compiled into every translation unit that includes it. Include it from exactly one .cpp and declare the two functions elsewhere, or you get duplicate-symbol link errors.
- Endpoints are the per-channel bounding-box min and max, with no choice of box diagonal, and selectors come from luma alone. Blocks whose channels move in opposite directions (red-to-green or blue-to-yellow edges) or change only in chroma at equal luma are badly encoded, beyond the normal-map warning in the README.
- DXT1 output is always 4-colour opaque (colour0's green LSB is forced to 1 so colour0 &gt; colour1), and endpoints are effectively RGB555, so smooth green gradients lose a bit of precision against encoders that use full 565.

## Known shortcomings

- Real-time DXT1/ETC1 encoder: Src/main.cpp public, i7-7820HQ, compiler and flags unstated; competitors reach 3.8-4.6 dB higher PSNR and Goofy's ETC1 is ETC1S only. The harness calls icbc, rgbcx and rg_etc1 initialisation inside the timed loop, inflating those ratios; the stb_dxt 33x row is the cleanest. test-results/ is empty. Baselines are texture encoders, not the category's image codecs.
- Only icbc::init_dxt1 is unguarded in the harness (a 1,310,720-iteration table rebuild inside each timed call), so the 60x against ICBC is probably 10-25% high (code estimate); rgbcx and rg_etc1 inits are guarded, so the 24x stands. The README's 'RGB-PSNR' is 10\*log10(768^2 / summed MSE), 4.805 dB above standard RGB PSNR for every encoder, so gaps are valid but absolute dB values are not comparable. Aligned _mm_load_si128 on unaligned input (crashes with NDEBUG), width must be a multiple of 16, the header forces GOOFYTC_IMPLEMENTATION (multi-translation-unit link errors), SSE2 hard-coded with no NEON, bounding-box endpoints fail on anti-correlated chroma; issues #4 and #5 (2025) unanswered.

## Caveats and trade-offs

Speed-quality trade, not equal quality: the compared encoders score about 3.8-4.6 dB higher RGB-PSNR (Goofy DXT1 37.02 dB vs 40.82-41.00 dB; Goofy ETC1 36.30 dB vs rg_etc1 40.87 dB), and Goofy's ETC1 output is restricted to the ETC1S subset, so it does less search work than rg_etc1. The harness (Src/main.cpp) calls icbc::init_dxt1(), rgbcx::encode_bc1_init() and rg_etc1::pack_etc1_block_init() inside every timed call, so those competitors' times include one-time table setup; the stb_dxt wrapper has no such call, so the 33x ratio vs stb_dxt is the cleanest. Compiler and flags are not stated (the repo ships a VS2017 Win64 CMake generator script and CI builds Release with MSVC, GCC and Clang, but the README does not say which build produced the table). test-results/ holds only keep_me.txt, so no raw result files are published. Not suited to normal maps per the README.

Speed over quality by design: about 37.0 dB RGB-PSNR for DXT1 versus roughly 40.8-41.0 dB for the compared encoders (only 3.6 dB above the downsample-to-RGB565 baseline at 33.39 dB). One heuristic, DXT1 and ETC1s only, poor on normal maps; DXT5 and ETC2 alpha are future work. Header-only, needs SSE2 (NEON not implemented).

## Maintenance

Stale: code essentially unchanged since 2020, last commit 2024-01-29 (README edits and a contributor's WASM/CI port), and two 2025 issues are unanswered. It is MIT and a single 1,500-line header, easy to vendor on x86 if you accept the size, alignment and quality limits.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table on a named CPU (i7-7820HQ, single thread, best of 128) with public benchmark code (Src/main.cpp times Goofy, stb_dxt, rgbcx, icbc and rg_etc1 on 42 test images and averages PSNR and time), but compiler and flags are not stated, so not A; no independent measurement found.
- **Verifier notes:** All numbers and ratios match the README. stb_dxt, rgbcx (bc7enc), icbc and rg_etc1 are recognisable texture-encoder incumbents; baseline_in_list false is right since the category lists image codecs. Flag for enrichment: competitor init calls sit inside the timed loop in Src/main.cpp, which inflates the rgbcx, icbc and rg_etc1 ratios by an unknown amount.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/SergeyMakeev/Goofy>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/README.md>
  - <https://github.com/SergeyMakeev/Goofy/commits/master>
  - <https://github.com/SergeyMakeev/Goofy/tree/master/Src>
  - <https://github.com/SergeyMakeev/Goofy/tree/master/test-results>
  - <https://github.com/SergeyMakeev/Goofy/tree/master/VisualStudio>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/Src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/Src/main.cpp>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/VisualStudio/generate17.cmd>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/.github/workflows/cmake-multi-platform.yml>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/SergeyMakeev/Goofy>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/README.md>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/GoofyTC/goofy_tc.h>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/Src/main.cpp>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/Src/decoder.cpp>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/Src/decoder.h>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/Src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/.github/workflows/cmake-multi-platform.yml>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/ThirdParty/icbc/icbc.h>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/ThirdParty/bc7enc/rgbcx.h>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/ThirdParty/rgetc/rg_etc1.cpp>
  - <https://raw.githubusercontent.com/SergeyMakeev/Goofy/HEAD/ThirdParty/ryg/stb_dxt.h>
  - <https://github.com/SergeyMakeev/Goofy/issues>
  - <https://github.com/SergeyMakeev/Goofy/issues/4>
  - <https://github.com/SergeyMakeev/Goofy/issues/5>
  - <https://github.com/SergeyMakeev/Goofy/commits/master>
  - <https://github.com/SergeyMakeev/Goofy/commits/master/Src/main.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/sergeymakeev/goofy`) · [data/wave10/enrich/raw/github_com_sergeymakeev_goofy.json](../../../data/wave10/enrich/raw/github_com_sergeymakeev_goofy.json) (enrichment confidence 0.85)

</details>
