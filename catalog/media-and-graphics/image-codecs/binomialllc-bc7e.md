# bc7e (Binomial BC7 encoder, ISPC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `ISPC (C-callable object code)` · `Apache-2.0` · 🔴 abandoned

> ISPC SIMD BC7 encoder; independent tests show its profiles 3-10x faster than ispc_texcomp's like-named profiles at higher PSNR.

| | |
|---|---|
| **Beats** | Intel ispc_texcomp (Fast ISPC Texture Compressor) |
| **Claimed result** | Independent measurement (Aras Pranckevicius, Dec 2020, 20 images, Core i9 2.9 GHz MacBook Pro 2018, clang 11.0.3, ISPC 1.14, AVX2), same-name profiles against ispc_texcomp: fast 3.0x, basic 4.0x, slow 10.1x faster at 0.7-1.1 dB higher PSNR; ultrafast 0.88x (slower) (derived from chart data). README says 'usually around 2-3x faster vs. ispc_texcomp at the same average quality ... up to \~8x faster vs. ispc_texcomp's slow profile'. |
| **Workload** | BC7 texture encoding at matched average quality (PSNR or SSIM) against the ispc_texcomp library and its profiles. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9 2.9 GHz, MacBook Pro 2018 (Aras Pranckevicius run); AVX2 |
| **Compiler and flags** | clang 11.0.3, ISPC 1.14, AVX2 target (Aras Pranckevicius run); optimisation flags not stated |
| **Adoption** | 182 stars, 19 forks; the latest bc7e.ispc ships in richgel999/bc7enc_rdo (which todds uses for BC7), and bc7e.ispc was ported to plain C++ in basis_universal (encoder/basisu_bc7e_scalar.cpp) |
| **Last commit** | 2026-01-28 |
| **Links** | [repository](https://github.com/BinomialLLC/bc7e) · [benchmark](https://github.com/aras-p/aras-p.hugo/blob/master/content/blog/2020/12-texcompr.md) |

## Verdict

The README alone (first-party, no data) claims 2-3x over ispc_texcomp at equal quality and about 8x over its slow profile. Independent support comes from Aras Pranckevicius's 'Texture Compression in 2020' (December 2020). He ran 20 Unity textures on a 2018 MacBook Pro (Core i9 2.9 GHz, 6 cores/12 threads) built with Xcode 11.7 (Apple clang 11.0.3) and ISPC 1.14, up to AVX2, multi-threaded, in perceptual mode, scoring Luma-PSNR. Average Mpix/s and dB were: bc7e fast 30.97 at 46.18 vs ISPC fast 10.10 at 45.36 and ISPC basic 4.53 at 46.07; bc7e basic 20.65 at 46.75; bc7e slow 13.04 at 47.40 vs ISPC slow 1.29 at 46.28. That makes bc7e about 3.0x, 4.0x and 10.1x faster than ispc_texcomp's like-named fast, basic and slow profiles, at 0.7-1.1 dB higher PSNR (derived from page data, harmonic means over the 20 images).

## Use it when

- Offline or build-time BC7 baking on x86-64 with AVX2, where you want more PSNR per second than ispc_texcomp gives. In Aras's tests every bc7e profile from fast upwards beat every ispc_texcomp profile.
- High-quality BC7 at moderate speed: the slow profile averaged 13.0 Mpix/s at 47.40 dB Luma-PSNR, against ispc_texcomp slow at 1.29 Mpix/s and 46.28 dB on the same 12-thread machine.
- Pipelines that already batch blocks and run their own thread pool (bc7e expects 32-64 or more blocks per call).
- sRGB colour textures where its perceptual (scaled YCbCr) metric can let you drop to a faster profile.

## Skip it when

- Bit-exact reproducible output across machines or builds from this archived copy. Its estimate_partition_list early-out uses all() across SIMD lanes, so results depend on SIMD width and on which blocks share a gang (issue #2). The fixed version is richgel999/bc7enc_rdo's bc7e.ispc (BC7E_NON_DETERMINISTIC 0).
- Your toolchain cannot run the ISPC compiler, or you need the best speed on ARM. bc7e is tuned for wide AVX2 lanes: single-threaded, Aras found a 2019 Intel MacBook Pro 1.5x faster than an M1 (4-wide NEON) for ISPC compressors including bc7e. Use bc7e_scalar or bc7f in basis_universal instead.
- Real-time or runtime encoding: ultrafast is mode 6 only and was 0.88x the speed of ispc_texcomp ultrafast (harmonic mean, derived), though 2.2 dB better. bc7f claims to be faster still.
- Opaque textures that must decode to alpha exactly 255: open issue #3 reports scattered alpha 254 in fully opaque areas.
- You need maintenance: the repo was archived on 2026-01-28 and bugs are fixed only in bc7enc_rdo.

## How it is fast

Each SIMD lane encodes one block through ISPC's SPMD model; the build line targets SSE2, SSE4, AVX and AVX2 in one object. Partitions for modes 0/1/2/3/7 are ranked with a cheap per-subset error estimate (estimate_partition_list), and only the best 1-4 go on to full encoding. Endpoints come from least-squares fits refined over a profile-set number of passes, plus optional p-bit search and 'uber' selector perturbation. Precomputed optimal-endpoint tables handle single-colour subsets. The profiles turn whole modes, rotations and partition counts on or off, which is where most of the speed difference comes from.

## Compared with alternatives

Pick bc7e over bc7enc (bc7enc16): in the same independent run, bc7enc's best preset reached 3.8 Mpix/s at 45.48 dB, while bc7e basic reached 20.6 Mpix/s at 46.75 dB. Pick basis_universal's bc7f instead when you need portable scalar real-time BC7 and can accept lower PSNR, or bc7e_scalar there when ISPC is not available.

## Integration

| | |
|---|---|
| **Form** | source-drop (bc7e.ispc compiled by ISPC to an object file plus a generated C/C++ header) |
| **Dependencies** | ISPC compiler at build time; the example tool also uses lodepng, bc7decomp (detex) and OpenMP |
| **Minimum toolchain** | ISPC 1.8.2 or 1.10.0 (README: tested mostly with 'v1.82', bundled ispc.exe 1.10.0); Aras built with ISPC 1.14; example project for Visual Studio 2015-2019 |
| **Platforms** | x86/x86-64 via the sse2/sse4/avx/avx2 multi-target build; ISPC NEON builds run on ARM (Aras ran it on Apple M1); tested on Windows, Linux and macOS per README |
| **Thread safety** | bc7e_compress_blocks and the params init functions are thread safe. bc7e_compress_block_init() writes global tables behind an unsynchronised bool, so call it once before starting threads. |
| **Drop-in for the baseline** | partial: same style of C API and similar profile names as ispc_texcomp, but different entry points, input layout (16 contiguous pixels per block, not an rgba_surface) and a mandatory init call |

## Gotchas

- Forgetting bc7e_compress_block_init() gives all-zero BC7 blocks in release builds (only an assert in debug).
- Results depend on SIMD width in this archived copy (issue #2, closed 2021-01-08 with the fix landing only in bc7enc_rdo). The README also says to restrict targets to SSE and drop --opt=fast-math if you need identical output on Intel and AMD.
- In perceptual mode the opaque path skips mode 5 and alpha blocks skip mode 4/5 rotations. The archived copy also has no solid-colour shortcut, which bc7enc_rdo added (exact mode 5 encode).
- The bundled bc7enc example times encoding with clock() around an OpenMP loop. On Linux and macOS that is CPU time summed over all threads, not wall time, so its 'Total time' overstates elapsed time when threaded.

## Known shortcomings

- Texture encoder (BC7) whose baseline ispc_texcomp is not a listed incumbent. README claims 2-3x at matched PSNR/SSIM and about 8x against the slow profile with no table, machine or harness; the independent aras-p blog is blocked (snippet directional only). Repo archived 2026-01-28; the encoder ships inside bc7enc_rdo (used by todds) and as a scalar C++ port in basis_universal.
- Archived; the shipped bc7e.ispc has a SIMD-width-dependent all() early-out in estimate_partition_list (issue #2), fixed only in bc7enc_rdo (BC7E_NON_DETERMINISTIC 0), and open issue #3 reports alpha 254 in opaque areas. The example tool's clock() timing over OpenMP measures CPU time, not wall time. The independent ratios (retier-03) hold against upstream ispc_texcomp only: Traverse-Research/intel-tex-rs-2 PR #50 (2026-09-28) makes ispc_texcomp BC7 2.1-6.2x faster; ultrafast is slower than ispc_texcomp (0.88x).

## Caveats and trade-offs

Claims only: no benchmark table, hardware, image set, ispc_texcomp version or harness. The same 2-3x claim for Basis BC7 appears in the bc7enc README, so the evidence is first-party only. The 'slow' profiles are 'calibrated to compete against' ispc_texcomp's similarly named profiles, but matched-quality data is not shown. Both encoders encode blocks single-threaded per call (threading is the caller's job). The repo was archived on 2026-01-28; the README calls it an archive of the original release and says the latest bc7e.ispc (determinism fixes, better solid-colour blocks) is in richgel999/bc7enc_rdo, and points to the newer, faster bc7f. The repo ships a prebuilt ispc.exe. An independent comparison exists in Aras Pranckevicius's 'Texture Compression in 2020' blog post (2018 MacBook Pro, Core i9 2.9 GHz, Xcode 11.7, Mpix/s vs Luma-PSNR charts), but the blog is blocked here and the search snippet is directional only ('bc7e presets have either better quality or faster compression than ISPC'). [retier] Mixed at the fastest setting: ultrafast is 0.88x of ispc_texcomp. The timed bc7e.ispc carries the SIMD-width-dependent all() early-out (issue #2; fixed only in bc7enc_rdo via BC7E_NON_DETERMINISTIC 0). ispc_texcomp has since been sped up 2.1-6.2x in Traverse-Research/intel-tex-rs-2 (PR #50, 2026-09-28), so the ratios hold against upstream Intel ispc_texcomp only. Repository archived.

Needs the ISPC compiler. Deterministic (does not use approximate SSE instructions, unlike ispc_texcomp). Repository archived by the owner on 2026-01-28; the bc7enc_rdo README says bc7e.ispc was ported to plain C++ (basisu_bc7e_scalar.cpp in basis_universal) and that the newer bc7f is faster still.

## Maintenance

Archived on 2026-01-28 (182 stars, Apache-2.0) and copyable, but the maintained bc7e.ispc with the determinism fix lives in richgel999/bc7enc_rdo, with C++ (bc7e_scalar) and successor (bc7f) versions in basis_universal.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** The README states verbatim that BC7E is 'usually around 2-3x faster vs. ispc_texcomp at the same average quality (as measured by PSNR or SSIM), and up to \~8x faster vs. ispc_texcomp's "slow" profile', but gives no table, image set, hardware, ispc_texcomp version or harness; the repo holds only the encoder and an example packer (bc7enc.cpp), no comparison benchmark. First-party numbers without methodology, so C.
- **Retiered** C to B: Raised C to B: the enricher reached an independent measurement by Aras Pranckevicius (December 2020 texture compression post; source and chart data in aras-p/aras-p.hugo at content/blog/2020/12-texcompr.md and static/img/blog/2020/texcompr/chart-bc7.html, read via raw.githubusercontent.com) on 20 images, Intel Core i9 2.9 GHz MacBook Pro 2018, clang 11.0.3, ISPC 1.14, AVX2: against ispc_texcomp's same-name profiles bc7e is 3.0x faster at fast, 4.0x at basic and 10.1x at slow, at 0.7-1.1 dB higher PSNR, while ultrafast is 0.88x (slower). Independent and numeric with compiler and CPU named; not A because the benchmark harness itself is not published with build flags. Caveat: the timed bc7e.ispc has the SIMD-width-dependent all() early-out in estimate_partition_list (issue #2, fixed only in bc7enc_rdo), a small quality effect that does not void the ratio; and Traverse-Research/intel-tex-rs-2 PR #50 (2026-09-28) makes ispc_texcomp BC7 2.1-6.2x faster, so the ratios hold against upstream ispc_texcomp only.
- **Verifier notes:** Baseline ispc_texcomp (Intel ISPCTextureCompressor) is the recognisable CPU BC7 incumbent; baseline_in_list false is correct because the category lists image codecs, not texture encoders. Archived means maintenance stays 'abandoned' even though the last commit (README edit) is 2026-01-28. Aras's independent blog numbers could support tier B if an environment reaches aras-p.info.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`, `claimed_speedup`, `benchmark_url`, `hardware`
- **Pages the verifier opened:**
  - <https://github.com/BinomialLLC/bc7e>
  - <https://github.com/BinomialLLC/bc7e/commits>
  - <https://raw.githubusercontent.com/BinomialLLC/bc7e/HEAD/README>
  - <https://raw.githubusercontent.com/richgel999/bc7enc_rdo/HEAD/README.md>
  - <https://raw.githubusercontent.com/todds-encoder/todds/HEAD/README.md>
  - <https://github.com/aras-p?tab=repositories&q=texture>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/BinomialLLC/bc7e/HEAD/README>
  - <https://raw.githubusercontent.com/BinomialLLC/bc7e/HEAD/bc7e.ispc>
  - <https://raw.githubusercontent.com/BinomialLLC/bc7e/HEAD/bc7enc.cpp>
  - <https://github.com/BinomialLLC/bc7e>
  - <https://github.com/BinomialLLC/bc7e/issues?q=is%3Aissue>
  - <https://github.com/BinomialLLC/bc7e/issues/2>
  - <https://github.com/BinomialLLC/bc7e/issues/3>
  - <https://raw.githubusercontent.com/richgel999/bc7enc_rdo/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/bc7enc_rdo/HEAD/bc7e.ispc>
  - <https://github.com/aras-p?tab=repositories&q=blog>
  - <https://github.com/aras-p/aras-p.hugo/tree/master/content/blog/2020>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/content/blog/2020/12-texcompr.md>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/static/img/blog/2020/texcompr/chart-bc7.html>
  - <https://github.com/aras-p/aras-p.hugo/tree/master/content/blog/2021>
  - <https://raw.githubusercontent.com/aras-p/aras-p.hugo/master/content/blog/2021/01-m1-texcompr.md>
  - <https://raw.githubusercontent.com/wiki/BinomialLLC/basis_universal/XUBC7-Usage-Guide.md>
  - <https://github.com/Traverse-Research/intel-tex-rs-2/pull/50>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/binomialllc/bc7e`) · [data/wave10/enrich/raw/github_com_binomialllc_bc7e.json](../../../data/wave10/enrich/raw/github_com_binomialllc_bc7e.json) (enrichment confidence 0.8)

</details>
