# VVenC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `BSD-3-Clause-Clear` · 🟢 active

> Fraunhofer's open H.266/VVC encoder; with 8 threads it runs 19x to 2400x faster than the single-threaded VTM reference encoder.

| | |
|---|---|
| **Beats** | VTM-19.2 (JVET VVC reference encoder) and HM-17.0 (HEVC reference encoder); x265 v3.5 is also plotted but only in figures |
| **Claimed result** | VVenC v1.14.0 Table III, 8 threads vs single-threaded reference encoders, random access, JVET CTC: HD4K speedup over VTM-19.2 faster 2400x, fast 1100x, medium 330x, slow 87x, slower 19x (HD column 2400x/1100x/280x/74x/15x; UHD column 2500x/1200x/380x/98x/22x); over HM-17.0 the HD4K speedups are 380x/180x/53x/14x/3x with PSNR-YUV BD-rate versus HM of -13.3%/-25.8%/-35.1%/-39.1%/-42.1%. Only the slower preset matches VTM's compression (Figure 1 puts VTM-19.2 at roughly -41% BD-rate versus HM, read approximately from the figure), so the quality-matched speedup over VTM is 15x HD / 22x UHD / 19x HD4K, and it includes 8 threads versus 1. The page prose says 'more than 20x for HD4K' for slower and quotes 2300x/370x/-13.7% (faster) and 280x/45x/-35.8% (medium) for HD4K, which disagree with the v1.14.0 table and look stale. Versus x265 3.5 (8 threads) there are no numbers, only Figure 2: x265's plotted presets sit at about +29% to +42% PSNR BD-rate versus HM at about 0.4% to 6% of HM's runtime, while VVenC's presets sit at -13% to -42% at about 0.26% to 33% of HM's runtime (read approximately from Figure 2, derived from page data), i.e. a compression win at similar runtime rather than a speed win over x265. |
| **Workload** | Random-access encoding of JVET common-test-condition sequences (class B HD, classes A1/A2 UHD) at constant QP 22/27/32/37; VVenC v1.14.0 with 8 threads versus single-threaded VTM-19.2 and HM-17.0 (both with MCTF enabled), reported as encoder runtime speedup together with PSNR-YUV BD-rate versus HM-17.0. The x265 3.5 runs in Figure 2 use 8 threads, --tune psnr and CRF 17/22/27/32 instead of constant QP. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7502P 32-Core @2.5GHz (Dell servers); VVenC and x265 run with 8 threads, HM and VTM single-threaded |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/fraunhoferhhi/vvenc) · [benchmark](https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Encoder-Performance.md) |

## Verdict

First-party Fraunhofer wiki Table III (VVenC v1.14.0, 8 threads, AMD EPYC 7502P, JVET CTC random access at QP 22-37; compiler and flags not stated; VTM-19.2 and HM-17.0 single-threaded with MCTF) gives HD4K speedups over VTM of 2400x (faster, -13.3% BD-rate versus HM), 330x (medium, -35.1%) and 19x (slower, -42.1%, about VTM's efficiency). Only the slower row is quality-matched to VTM, and even if 8 threads scaled perfectly it still implies at least about 2.4x per thread (derived from page data); no x265 or x264 speed numbers are tabulated.

## Use it when

- You must produce H.266/VVC bitstreams (VOD archives, DASH, VVC test content) with an open encoder; the wiki puts the medium preset at -35.1% PSNR-YUV BD-rate versus HM-17.0 on HD/UHD test sequences.
- Research or conformance work that would otherwise run VTM: the slower preset reaches roughly VTM-19.2's compression (-42.1% versus HM) in 1/19 of VTM's HD4K encode time on 8 threads.
- Offline encoding where bitrate matters more than encoder time and a multi-core server is available (default 8 threads at 720p and above).
- Arm servers: the library carries Neon and SVE/SVE2 kernels, and 1.13 and 1.14 added many Arm SIMD paths.

## Skip it when

- Speed-critical or live encoding where H.264/HEVC/AV1 output is acceptable: Fraunhofer's own Figure 2 puts x265 3.5 presets at about 0.4% to 6% of HM's runtime versus 0.26% to 33% for VVenC (read from the figure), and unopened third-party snippets describe vvenc medium as roughly 15x slower than x265 medium; the speedups are only versus the VVC and HEVC reference encoders.
- Players or hardware without VVC decode support; output is a raw .266 elementary stream that needs a VVC decoder such as VVdeC.
- Projects that need an OSI-approved license or a patent grant: the Clear BSD license explicitly grants no patent rights, and VVC itself is covered by patent pools.
- Lossless coding (issue #59, labelled wontfix) or multiple slices per picture (issue #635, open); vvencapp documents only 4:2:0 8- and 10-bit input.
- Content where fine static detail matters with default settings: open issue #369 (bug label) reports QPA removing detail in static regions, and #489 reports visible blocking on slow-moving objects.

## How it is fast

It started from the VTM reference code and was restructured around SIMD kernels (x86 SSE4.1/SSE4.2/AVX/AVX2 with runtime selection, Arm NEON/SVE/SVE2, LoongArch LSX, SIMDe for other targets) and Pareto-tuned presets that prune the VVC search space: 64x64 CTUs and no multi-type-tree splits in inter slices for faster/fast, fast diamond motion search, early CU termination, fewer intra modes in full RD and tool subsets per preset. Encoding runs as CTU tasks in a no-malloc thread pool with wavefront dependencies (top and top-right CTU), plus inter-frame parallelization (IFP), tiles and parallel GOPs; dependent quantization uses trellis pruning and vectorization per the authors' EUSIPCO 2024 paper listed on the wiki.

## Compared with alternatives

Pick VVenC when you need VVC/H.266 output or the highest PSNR-per-bit of the catalogued encoders and can spend encode time; pick SVT-AV1 for royalty-free AV1 with much faster production presets, Kvazaar or x265 for fast HEVC, and uavs3e only for AVS3. OpenVVC and VVdeC are VVC decoders that pair with it rather than compete.

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib (BUILD_SHARED_LIBS=1), plus vvencapp and vvencFFapp executables |
| **Dependencies** | none external; SIMDe and nlohmann_json (rate-control statistics, optional) are bundled |
| **Minimum toolchain** | C++14, CMake 3.13+, GCC 5+, Xcode clang, Visual Studio 2017+; the build refuses MSVC 19.38-19.39 as known-miscompiling unless VVENC_OVERRIDE_COMPILER_CHECK=ON |
| **Platforms** | x86 and x86-64 (SSE4.1 required since 1.13.1; SSE4.2/AVX/AVX2 kernels picked at runtime), AArch64 (Neon, optional SVE/SVE2), 32-bit Arm Neon, LoongArch64 LSX, other targets including Emscripten through SIMDe; Linux, macOS and Windows |
| **Thread safety** | Each vvencEncoder owns its worker pool; separate encoder instances are independent. The global vvenc_set_logging_callback is deprecated as not thread-safe in favour of a per-config callback. |
| **Drop-in for the baseline** | partial: emits standard VVC bitstreams like VTM, and vvencFFapp keeps VTM-style option names, but presets, defaults and the produced bitstreams differ from VTM, and the API is VVenC's own |

## Gotchas

- Floating-point contraction is on by default, so bitstreams can differ across platforms and compiler versions; build with VVENC_FFP_CONTRACT_OFF=On for bit-exact output (README).
- The two apps have different defaults: vvencapp turns perceptual QPA on (--qpa 1) while vvencFFapp's PerceptQPA defaults to 0, so the same preset gives different PSNR and bitrate results.
- VVENC_ENABLE_WERROR defaults to On, so a newer compiler that emits a new warning breaks the build until the option is turned off; VVENC_ENABLE_UNSTABLE_API breaks ABI compatibility with other 1.x releases.
- The benchmark is for the v1.14.0 tag while master reports 1.15.0-dev, and the wiki prose (e.g. 'more than 2300x', 'around 370x', 280x for medium) disagrees with its own v1.14.0 Table III, so quote the table, not the prose.

## Known shortcomings

- Not faster than the listed baselines: VVenC is compared only against the single-threaded VTM-19.2 and HM-17.0 reference encoders (v1.14.0 wiki Table III, 8 threads, AMD EPYC 7502P), with no timing harness, compiler or flags published; quality-matched speedup over VTM is 15x HD, 22x UHD, 19x HD4K, and every preset except slower gives up compression. Against x265 3.5 (figure only, CRF vs constant QP) VVenC sits at similar runtime with better compression, and third-party snippets put vvenc medium far slower than x265 medium. Page prose (over 20x, 2300x, 280x/45x) disagrees with its own table. Licence BSD-3-Clause-Clear (no patent grant; SPDX marks it not OSI approved), so usability set to reference.
- The speed win is only against VTM and HM; the one quality-matched row (slower preset, HD/4K, 8 threads) is 19x, at least 2.4x per thread (derived from page data), and the project's own Figure 2 plus search snippets show VVenC slower than x265. Wiki prose is stale against Table III. Open issues #369 (QPA detail loss) and #489 (blocking artefacts); no lossless mode (#59, wontfix) and no multi-slice (#635); the default floating-point contraction breaks bit-exactness across platforms. Clear BSD licence with no patent grant (reference).

## Caveats and trade-offs

First-party wiki numbers; compiler, flags and thread pinning are not stated and no timing harness is published, so not reproducible-tier. The measured code does different work from the baselines: VVenC runs 8 threads while VTM and HM are single-threaded, and every preset except slower gives up compression relative to VTM (faster loses roughly 28 BD-rate points against VTM), so the 2400x headline compares a fast, lower-quality multi-threaded VVC encode with the single-threaded JVET reference encoder. VTM and HM are research reference encoders, not production encoders; the category baselines x264/x265 are a different codec generation and VVenC is not shown to be faster than them in wall-clock time: the x265 3.5 comparison exists only as figures (CRF rate control versus constant QP for VVenC; the reference [14] links the x265 Release_3.4 tree while the text says v3.5), and third-party search snippets (forasoft.com, dev.to; not opened, blocked) describe vvenc medium as far slower than x265 medium on wall clock. The page prose disagrees with its own Table III (e.g. slower 'more than 20x' versus 19x HD4K in the table). Peer-reviewed first-party papers (ICMEW 2021: snippet only, single-threaded VVenC at 46% of VTM runtime and fastest configuration over 140x faster than VTM for an early version) were not opened. License is the Clear BSD License (BSD-3-Clause-Clear), which is FSF-libre but not OSI-approved per the SPDX license list 3.29.0, and it explicitly grants no patent rights; H.266/VVC itself is covered by patent pools. Page last edited 2026-03-30.

Encodes H.266/VVC, whose decoder support and patent licensing differ from H.264/HEVC; the speedups are relative to the slow JVET reference software, not to a production encoder. Perceptual tuning (XPSNR-based QPA) is available.

## Maintenance

Actively developed by Fraunhofer HHI (last commit 2026-10-02, latest tag 1.14.0, master at 1.15.0-dev) with unit tests for SIMD kernels; filed as reference because the Clear BSD license is not OSI-approved and grants no patent rights, and VVC patent licensing is separate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Fraunhofer HHI wiki (Encoder-Performance.md, last edited 2026-03-30) gives Table III speedups of VVenC v1.14.0 (8 threads) over VTM-19.2 and HM-17.0 (single-threaded) on AMD EPYC 7502P, but no timing harness is published (repo cfg/ holds only preset configs) and compiler and flags are not stated, so it cannot be A. The peer-reviewed VVenC papers (ICMEW 2021 and later) are on blocked IEEE/ACM/arXiv/ResearchGate pages, so their numbers are snippet only and cannot lift the tier to B.
- **Verifier notes:** All Table III numbers in the record match the v1.14.0 wiki table; metadata (1.2k stars, not a fork, not archived, last commit 2026-10-02) confirmed. Usability changed to reference only because SPDX marks BSD-3-Clause-Clear as not OSI-approved (it is BSD-3-Clause plus an explicit no-patent-grant clause); the orchestrator may prefer to treat it as copyable by policy. The record is a fair VTM/HM comparison but not evidence of beating x264/x265 on speed; consider a shortcoming saying the speed win is versus the VVC reference encoder only.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Encoder-Performance.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/data/vvenc-1.14.0.png>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/data/vvenc-0.1-1.14.png>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Home.md>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/README.md>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json>
  - <https://github.com/fraunhoferhhi/vvenc>
  - <https://github.com/fraunhoferhhi/vvenc/commits/master>
  - <https://github.com/fraunhoferhhi/vvenc/wiki/Encoder-Performance/_history>
  - <https://github.com/fraunhoferhhi/vvenc/tree/master/cfg>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/README.md>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/changelog.txt>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/include/vvenc/vvenc.h.in>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/include/vvenc/vvencCfg.h>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/source/Lib/vvenc/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fraunhoferhhi/vvenc/HEAD/source/Lib/EncoderLib/EncSlice.cpp>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Encoder-Performance.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Home.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Usage.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Build.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Presets.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/Publications.md>
  - <https://raw.githubusercontent.com/wiki/fraunhoferhhi/vvenc/License.md>
  - <https://github.com/fraunhoferhhi/vvenc/tree/master/source/Lib/CommonLib>
  - <https://github.com/fraunhoferhhi/vvenc/tree/master/source/Lib/EncoderLib>
  - <https://github.com/fraunhoferhhi/vvenc/issues>
  - <https://github.com/fraunhoferhhi/vvenc/issues/724>
  - <https://github.com/fraunhoferhhi/vvenc/issues?q=is%3Aissue+mismatch>
  - <https://github.com/fraunhoferhhi/vvenc/issues?q=is%3Aissue+x265+speed>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/fraunhoferhhi/vvenc`) · [data/wave10/enrich/raw/github_com_fraunhoferhhi_vvenc.json](../../../data/wave10/enrich/raw/github_com_fraunhoferhhi_vvenc.json) (enrichment confidence 0.8)

</details>
