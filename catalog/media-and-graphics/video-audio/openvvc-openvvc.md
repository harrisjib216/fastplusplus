# OpenVVC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1` · 🔴 abandoned

> INSA Rennes' lightweight C decoder for H.266/VVC; matches Fraunhofer VVdeC's speed in an independent study while using about half the memory.

| | |
|---|---|
| **Beats** | VTM reference decoder and Fraunhofer VVdeC |
| **Claimed result** | Snippet only (all papers blocked): the arXiv 2205.12217 abstract says OpenVVC reaches real-time UHD decoding by combining SIMD with frame-level parallelism, decodes faster than VVdeC, and uses less memory than VVdeC by a factor greater than 2.11x. An independent study (Journal of Real-Time Image Processing 2023, 'Performance analysis of optimized versatile video coding software decoders on embedded platforms') found OpenVVC and VVdeC both reach real-time FHD on an 8-core and HD on a 4-core embedded platform with comparable energy (about 26 J and 15 J), with VVdeC needing 2x OpenVVC's memory; that is a memory win, not a speed win. The ACM MMSys 2023 end-to-end pipeline (uvg266 encoder + uvgRTP + OpenVVC) is almost 34,000x as fast as a VTM-based pipeline and 3.3x the fastest VVenC/VVdeC configuration; those are whole-pipeline figures that include the encoder, not decoder-only speedups. The 290 fps FHD / 90 fps UHD figures in the original record did not appear in any snippet this verifier saw. |
| **Workload** | Software decoding of VVC (H.266) bit-streams on multi-core x86 and embedded ARM platforms; also a live 4K intra end-to-end pipeline paper. |
| **Metric** | throughput |
| **Adoption** | 133 stars, 27 forks |
| **Last commit** | 2022-03-22 |
| **Links** | [repository](https://github.com/OpenVVC/OpenVVC) · [benchmark](https://arxiv.org/abs/2205.12217) |

## Verdict

Snippet only: search summaries of the authors' arXiv 2205.12217 paper (blocked) give about 37 fps FHD and 12 fps UHD single-threaded, 249 fps FHD and 75 fps UHD on average multi-threaded, and above 290 fps FHD and 90 fps UHD at best on an unnamed multi-core x86 platform (compiler and flags not visible), with VVdeC slightly faster single-threaded and OpenVVC scaling better. The independent JRTIP 2023 embedded study (also snippet only) found speed and energy on par with VVdeC (real-time FHD on 8 cores, HD on 4) and VVdeC using about 2x the memory, so the confirmed advantage is memory, not decode speed; the 34,000x MMSys 2023 figure is an end-to-end pipeline result driven by the encoder.

## Use it when

- You need a small, LGPL-2.1 C library to play or analyse 10-bit 4:2:0 VVC main-profile streams (JVET CTC-style random-access or all-intra) and want lower memory than VVdeC: the independent JRTIP 2023 study measured VVdeC needing about 2x OpenVVC's memory.
- Embedded or mobile Arm decoding (Linux, Android, macOS, iOS build support) where memory footprint matters and real-time HD on 4 cores or FHD on 8 cores is enough, per the same study.
- Research on VVC decoder parallelism or energy, where a compact C codebase with separate 8-bit and 10-bit DSP templates is easier to modify than VVdeC's C++.
- Feeding VVC into an FFmpeg-based pipeline through the OpenVVC FFmpeg fork, as in the authors' uvg266 + uvgRTP + OpenVVC live 4K intra toolkit.

## Skip it when

- General-purpose or untrusted VVC playback: 72 of the 238 JVET conformance streams in CI/conf.vmd5 are commented out as failing, including WPP_A/B, SLICES_A, SUBPIC_A to E, TILE_B to G, WP_A/B (weighted prediction), LMCS_A/B, DMVR_A, SCALING_A to C, GDR, FIELD, PALETTE, ACT, BDPCM and all 4:4:4 streams; the project site lists WPP, subpictures, 4:0:0/4:2:2/4:4:4 and 12-bit as unsupported and slices and multi-tile as partial.
- 8-bit content when speed matters: every SIMD init in rcn.c is guarded by bitdepth == 10, so 8-bit streams run the scalar C templates only.
- Anything that needs maintenance or security fixes: the last commit on master is 2022-03-22, issue #17 (June 2026) asking whether it is still maintained has no reply, and issue #7 on decoding corrupted files was never answered; no fuzzing or error-resilience work is documented.
- When FFmpeg's native VVC decoder (FFVVC, the subject of a FOSDEM 2024 talk seen in search results) or VVdeC is an option: both avoid the out-of-tree FFmpeg fork OpenVVC needs; their speed and conformance were not checked in this pass.
- Builds on a fresh macOS toolchain or Linux/ARM64 without some effort: issues #16 (configure failure on a MacBook, April 2025) and #15 (ARM64 build and test request) are open with no maintainer response.

## How it is fast

Written from scratch in C rather than derived from the C++ VTM reference, with SIMD kernels for the reconstruction stages: SSE4.1 for transforms, intra (angular, DC/planar, MIP, CCLM), motion compensation, DMVR, BDOF/PROF, ALF/CC-ALF, SAO, deblocking and dequantization, plus AVX2 versions of MC, ALF, SAO, MIP, DMVR, BDOF/PROF and intra angular (5,374 lines in x86/rcn_mc_avx2.c alone), selected at run time with __builtin_cpu_supports. On Arm the same SSE code is translated through a vendored SIMDe, plus hand-written AArch64 assembly for MC and DC/planar. Parallelism combines frame-level threads (several pictures in flight) with entry (tile) threads; both default to the core count.

## Compared with alternatives

No other VVC decoder is catalogued; VVenC (the Fraunhofer encoder) and uvgRTP are pipeline partners rather than competitors. Pick OpenVVC over the uncatalogued VVdeC or FFmpeg's native VVC decoder only when memory footprint on 10-bit 4:2:0 content outweighs conformance coverage and maintenance.

## Integration

| | |
|---|---|
| **Form** | shared lib (libovvc.so via libtool) and static lib, with pkg-config file libopenvvc.pc and the dectest example binary |
| **Dependencies** | POSIX threads (required); optional SLHDR library (slhdr_cwrap via pkg-config, enabled automatically if found, --disable-slhdr to skip); SIMDe headers are vendored under libovvc/arm/simde |
| **Minimum toolchain** | C compiler (configure probes gcc, then clang), autoconf, automake and libtool; Windows only through Cygwin or MSYS2; no C standard level documented |
| **Platforms** | x86 and x86-64 (SSE4.1 and AVX2 kernels for 10-bit), AArch64 and 32-bit Arm (SIMDe-translated SSE code plus AArch64 assembly), Linux, macOS, Windows (Cygwin/MSYS2), Android, iOS (build support added March 2022) |
| **Thread safety** | Decoder state lives in each OVDec instance with its own frame and entry worker threads; the log level and log callback (ovdec_set_log_callback) are process-wide globals, so set them once before creating decoders. Concurrent use of one OVDec from several threads is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- configure appends -msse4.1 and -mavx2 to the global CFLAGS whenever the compiler accepts them, so every source file, not only the kernels behind the __builtin_cpu_supports checks, may be compiled with AVX2 code; a binary built this way is not safe to ship to CPUs without AVX2 unless you override CFLAGS or pass --disable-simd.
- The README changelog stops at v1.0.0 and says only 8-bit bitstreams were added, yet VERSION reads 1.1.0 and the library builds both 8-bit and 10-bit DSP templates, with all SIMD on the 10-bit path; trust the code and CI/conf.vmd5, not the README, for what is supported.
- OVDEC_NB_ENTRY_THREADS parallelises tiles only (per ovdec.h), so single-tile streams get no intra-picture speedup and scale only through frame threads; the frame-thread count is capped at the entry-thread count.
- The CI conformance script and README test command download bitstreams from openvvc.insa-rennes.fr and nasext-vaader.insa-rennes.fr, which may not stay online now that the project is idle.

## Known shortcomings

- Numbers exist only in snippets of blocked papers (arXiv 2205.12217, MMSys 2023); the 290/90 fps figures were not found in any snippet, and the 34,000x is a whole-pipeline figure including the encoder. An independent JRTIP 2023 study rates its speed comparable to VVdeC, with VVdeC needing twice the memory. Last commit 2022-03-22, abandoned.
- CI/conf.vmd5 marks 72 of 238 JVET conformance streams as failing (WPP, SLICES_A, SUBPIC, TILE_B-G, WP, LMCS_A/B, 4:4:4). rcn.c enables SIMD only when bitdepth == 10, so 8-bit runs scalar C; configure puts -msse4.1 -mavx2 into the global CFLAGS, so binaries may not run on CPUs without AVX2. Dead since 2022-03-22 with issues #17, #16 and #7 unanswered. The paper's figures (290/90 fps peak, 249/75 average, 37/12 single-thread FHD/UHD; VVdeC slightly faster single-threaded) remain snippet-only with CPU and flags not visible.

## Caveats and trade-offs

Snippet only: every number comes from search snippets of blocked papers (arXiv 2205.12217; ACM MMSys 2023 'Open-Source Toolkit for Live End-to-End 4K VVC Intra Coding'; Springer JRTIP 2023 independent study at https://link.springer.com/article/10.1007/s11554-023-01376-7); none was opened, and the repo README has no numbers or benchmark harness. The baselines are the VTM reference decoder and Fraunhofer VVdeC, not FFmpeg; no comparison against FFmpeg's native VVC decoder was found. The independent study shows parity in speed with VVdeC and a 2x memory advantage, so the speed claim rests on the authors' own paper. The 34,000x figure is an end-to-end pipeline result dominated by the encoder choice. Last commit on master is 2022-03-22 (2,197 commits), so the code may lag the papers' decoder; README still says 'still under development' and supports only 8-bit bitstreams. LGPL-2.1.

Supports 8-bit bit-streams, frame and tile parallelism, RPR; README says it is still under development. Lightweight, lower memory than VVdeC.

## Maintenance

Abandoned since 2022-03-22 (2,197 commits, 133 stars, open issues unanswered) but LGPL-2.1 and plain C, so it can be vendored for 10-bit 4:2:0 decoding if you accept the conformance gaps listed in its own CI file.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo README has no numbers and no benchmark code; the only figures come from search snippets of blocked peer-reviewed papers (arXiv 2205.12217, ACM MMSys 2023, and an independent J. Real-Time Image Processing 2023 study), and snippet-only numbers cap the entry at C.
- **Verifier notes:** Tier and verdict unchanged; claimed_speedup rewritten to what the snippets support, with the memory-vs-speed distinction and the pipeline nature of the 34,000x figure made explicit. pmc.ncbi.nlm.nih.gov (PiSDF paper) and archive.fosdem.org (FFVVC slides) were tried and are EGRESS_BLOCKED; a paper-access retier could check the arXiv PDF for the 290/90 fps figures and hardware.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/README.md>
  - <https://github.com/OpenVVC/OpenVVC>
  - <https://github.com/OpenVVC/OpenVVC/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/README.md>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/VERSION>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/.gitlab-ci.yml>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/CI/conf.vmd5>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/CI/checkMD5.sh>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/Makefile.am>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/x86/Makefile.am>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/arm/Makefile.am>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/ovdec.h>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/ovdec.c>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/ovthreads.c>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/ovthreads.h>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/dec_init.c>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/rcn.c>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/ovlog.c>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/x86/rcn_mc_avx2.c>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/arm/rcn_mc_sse.c>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/libovvc/arm/simde/x86/sse4.2.h>
  - <https://raw.githubusercontent.com/OpenVVC/OpenVVC/HEAD/examples/dectest.c>
  - <https://raw.githubusercontent.com/OpenVVC/openvvc.github.io/HEAD/index.md>
  - <https://raw.githubusercontent.com/OpenVVC/openvvc.github.io/HEAD/_config.yml>
  - <https://raw.githubusercontent.com/OpenVVC/openvvc.github.io/HEAD/_data/supported_tools.csv>
  - <https://github.com/OpenVVC/OpenVVC>
  - <https://github.com/OpenVVC/OpenVVC/commits/master>
  - <https://github.com/OpenVVC/OpenVVC/issues?q=is%3Aissue>
  - <https://github.com/OpenVVC/OpenVVC/issues/17>
  - <https://github.com/OpenVVC/OpenVVC/issues/16>
  - <https://github.com/OpenVVC/OpenVVC/issues/7>
  - WebSearch: OpenVVC decoder fps UHD VVdeC comparison (result snippets for arXiv 2205.12217 and Springer JRTIP 2023; pages not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/openvvc/openvvc`) · [data/wave10/enrich/raw/github_com_openvvc_openvvc.json](../../../data/wave10/enrich/raw/github_com_openvvc_openvvc.json) (enrichment confidence 0.6)

</details>
