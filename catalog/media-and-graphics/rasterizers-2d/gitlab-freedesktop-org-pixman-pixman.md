# pixman (SIMD bilinear fast paths: SSE2, NEON, RVV)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Pixman's hand-written SIMD bilinear fetchers (SSE2, NEON, RISC-V RVV) beat its own scalar C paths by 1.5x to 11x.

| | |
|---|---|
| **Beats** | pixman's own scalar C bilinear affine fetcher (bits_image_fetch_bilinear_affine_normal_a8r8g8b8 in pixman-fast-path.c) for the RVV row; pixman's generic C compositing path for the 2011 SSE2 and NEON rows |
| **Claimed result** | RVV a8r8g8b8 bilinear affine fetch (commit e1f49d9, 2026-09-01) against the generic C fetch of the previous tree, SpacemiT K3, GCC 15.2.0, Meson release build, medians of five interleaved runs: affine-bench rotate 30 degrees 29.15 to 44.74 MPix/s (+53.48%), shear 0.25 36.46 to 60.75 MPix/s (+66.62%). Pure-scale lowlevel-blt-bench -b -c src_8888_8888 stays within run-to-run variation (-0.29% to +1.19%), because pure scaling was already served by the two-row-cache bilinear cover fetch. Follow-up commit caa79f2 (2026-09-24, K3 X100 core pinned to CPU 2 at 2.2 GHz) reports none-repeat affine a8r8g8b8 scale 0.5 75.24 to 119.36, rotate 30 28.41 to 42.53 and shear 0.25 34.56 to 55.87 MPix/s against the previous tree, with a forced-C build faster than RVV below widths of about 52-54 pixels. Historical first-party rows: SSE2 bilinear scaled src_8888_8888 (commit 3500293, 2011-02-21) is 'approximately 2x faster than pixman general compositing path'; its microbenchmark (2000x2000 image, scale factor close to 1x, Intel Core i7) goes from 70.48 to 165.38 MPix/s (2.35x, derived from page data), and cairo-perf-trace image firefox-planet-gnome from 12.566 to 10.961 (1.15x, derived from page data; the page gives no unit, though cairo-perf-trace prints its min and median columns in seconds). ARM NEON on a Cortex-A8: src_8888_8888 6.70 to 44.27 MPix/s (17feaa9), src_8888_0565 6.56 to 61.65 MPix/s (2ee27e7, r2p2 at 1 GHz with 32-bit LPDDR at 200 MHz), src_0565_x888 3.39 to 36.82 MPix/s (29003c3). |
| **Workload** | Primary row: test/affine-bench, SRC compositing of a8r8g8b8 to a8r8g8b8 at 1920x1080 with bilinear filtering under a 30-degree rotation and a 0.25 shear (the default op and formats of affine-bench.c), pinned to one core. Historical rows: bilinear SRC compositing of a 2000x2000 image at a scale factor close to 1x (SSE2 a8r8g8b8 to a8r8g8b8 on x86-64; NEON 8888, 0565 and x888 variants on a Cortex-A8), plus a cairo-perf-trace replay of firefox-planet-gnome on the image backend. |
| **Metric** | throughput |
| **Hardware** | Primary row: SpacemiT K3 (RISC-V 64-bit with RVV 1.0; the follow-up commit caa79f2 names an X100 core pinned to CPU 2 at 2.2 GHz). Historical rows: an Intel Core i7 of unstated model (SSE2) and an ARM Cortex-A8 (NEON; r2p2 at 1 GHz with 32-bit LPDDR at 200 MHz in two commits). |
| **Compiler and flags** | Primary row: GCC 15.2.0, Meson release build (buildtype=release, i.e. -O3 without debug info; pixman-rvv.c gets -march=rv64gcv1p0 from meson.build). The 2011 SSE2 and NEON rows give no compiler or flags. |
| **Adoption** | Compositing backend library behind Cairo's image backend and the X.org server (usage from general knowledge, not verified this session). Only GitHub mirrors were reachable: aseprite/pixman 12 stars, X11Libre/mirror.fdo.pixman 0 stars. |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://gitlab.freedesktop.org/pixman/pixman) · [benchmark](https://github.com/X11Libre/mirror.fdo.pixman/commit/e1f49d9e6665ce354b90a189bf7bb5bbde9a1f20) |

## Verdict

On a SpacemiT K3 (RVV 1.0) pinned to one core, built with GCC 15.2.0 in Meson release mode, test/affine-bench at 1920x1080 SRC a8r8g8b8 bilinear rose from 29.15 to 44.74 MPix/s for a 30-degree rotation (1.53x) and from 36.46 to 60.75 for a 0.25 shear (1.67x). The baseline was the previous tree's scalar C affine fetcher, the figures are medians of five interleaved runs (e1f49d9), and pure scaling did not change. caa79f2 extended the fetch to none-repeat and x8r8g8b8 sources (+46% to +62%). The 2011 Siamashka commits report SSE2 bilinear scaling at 70.48 to 165.38 MPix/s on an unnamed Core i7 and NEON gains of 6.6x to 10.9x on a Cortex-A8, with no compiler or flags given.

## Use it when

- Your stack already composites through pixman or Cairo image surfaces on RISC-V with RVV 1.0 and draws rotated or sheared bilinear a8r8g8b8/x8r8g8b8 images. Current master measured 1.5x to 1.7x on a SpacemiT K3.
- Scaled (not rotated) bilinear SRC or OVER blits of 8888 or 0565 images on x86-64 (SSE2/SSSE3) or ARM NEON, where hand-written scale paths exist (2.35x SSE2 on a Core i7 and 6.6x to 10.9x NEON on a Cortex-A8 against the 2011 C path).
- You need identical output whichever path runs: the RVV paths reuse the C integer weight formula, and the RVV commits report the full pixman test suite passing (35 tests).
- You want to A/B test SIMD against C in one binary: PIXMAN_DISABLE='rvv', 'sse2 ssse3 mmx' or 'fast' switches implementations off at startup.

## Skip it when

- Rotated or sheared bilinear sources on x86-64 or ARM: SSE2, SSSE3 and NEON register scale-only bilinear paths, so these transforms run the scalar C affine fetcher in pixman-fast-path.c. Blend2D is the faster choice there.
- Distro or tagged pixman builds that need the RVV affine speedup: the fetchers landed in master in September 2026. The mirror's newest tag is pixman-0.46.4 (2025-07-20), and meson.build at HEAD reads 0.46.5.
- Short rows on RVV: a forced-C build beats the RVV gather fetch below about 52-54 pixels (none-repeat 0.75x scale sweep), so the library keeps C through 53 pixels for positive horizontal scales.
- Format, operator or repeat combinations with no registered fast path or iterator drop to the general path and gain nothing.
- Full vector-graphics rendering (paths, gradients, text): pixman is a compositing back end, and sibling renderers such as Blend2D cover the whole pipeline.

## How it is fast

Pixman stacks implementations at run time (general C, then format-specialised C, then each CPU's SIMD layer). Each layer registers fast paths and iterators keyed on format, operator and image flags, such as SCALE versus AFFINE transform and FAST_PATH_SAMPLES_COVER_CLIP_BILINEAR. For pure scaling, SSE2 and NEON use bilinear scanline functions, and SSSE3 and RVV use a two-row cache that interpolates each source row horizontally once and reuses it for the vertical blend. The 2026 RVV affine fetch handles rotation and shear. It computes each lane's 16.16 fixed-point coordinate as x + i\*ux and loads the four taps with indexed gathers (vluxei32, falling back to 64-bit offsets above 4 GiB). It then blends two channels at a time in 16-bit lanes with widening multiply-accumulates on 7-bit weights, which reproduces the C fetcher's integer formula. Because the cover flag guarantees in-bounds taps, it also skips the C fetcher's per-tap repeat() wrap.

## Compared with alternatives

Pick pixman when you are already on Cairo's image backend or the X server and only need faster image compositing, or when you target RISC-V RVV, where it now has vector bilinear affine fetches. For a standalone 2D renderer, Blend2D (JIT pipelines; the clear winner in the ETH thesis) or Vello CPU is faster across whole scenes.

## Integration

| | |
|---|---|
| **Form** | shared lib (Meson library 'pixman-1'; static with default_library=static) |
| **Dependencies** | libm and threads (pthreads); libpng, GTK 3/GLib and OpenMP are optional and only for tests and demos |
| **Minimum toolchain** | C99 (c_std gnu99,c99), Meson &gt;= 1.3.0; the RVV layer needs RISC-V vector intrinsics from GCC 14 or Clang 18 and is built with -march=rv64gcv1p0 |
| **Platforms** | Any C99 target. SIMD layers exist for x86 MMX/SSE2/SSSE3, ARMv6 SIMD, ARM NEON, AArch64 NEON, MIPS DSPr2, POWER VMX/POWER8/POWER9, Loongson MMI and RISC-V RVV 1.0. RVV builds only for riscv64, is detected at run time on Linux (hwprobe or getauxval) and FreeBSD (elf_aux_info), and is disabled elsewhere. |
| **Thread safety** | not documented in the files read (the build has a 'tls' option for compiler thread-local storage) |
| **Drop-in for the baseline** | yes |

## Gotchas

- Baseline correction for the tier-A RVV rows: 'previous tree' means pixman-fast-path.c's scalar C fetcher bits_image_fetch_bilinear_affine_normal_a8r8g8b8, which is format- and repeat-specialised by MAKE_BILINEAR_FETCHER. It is not the general compositing path. That fetcher wraps every tap through repeat() and tests the mask per pixel even when samples cover the clip, so the 1.5x to 1.7x gain mixes vectorisation with a cover-only fetcher that drops that work.
- Do not compare absolute MPix/s across the RVV commits. The pure-scale src_8888_8888 'M' row reads 75.39 MPix/s in e1f49d9 but 116.91 in the caa79f2 baseline measured by 95853c3. That later run pinned the userspace governor at 2.2 GHz; e1f49d9 states no frequency or governor. Each commit's ratios come from interleaved medians and remain usable.
- Path selection depends on flags and table order. COVER needs every tap, zero-weight ones included, inside the image (caa79f2 forced the none-repeat path by shortening the source one row). rvv_iters[] comments warn that reordering entries silently routes scale sources onto the gather path.
- The RVV width thresholds (53 pixels for the affine gather, 11 pixels for the vectorised vertical pass) and the gather design were tuned on one core, the SpacemiT K3 X100. A vectorised horizontal gather was 6.9-8.3% slower there and was dropped.

## Known shortcomings

- Tier A rests on the RVV commit e1f49d9 (2026-09-01: in-tree test/affine-bench.c, GCC 15.2.0, Meson release buildtype, SpacemiT K3, medians of 5 interleaved runs against the generic C fetch; rotate 29.15 to 44.74 MPix/s, shear 36.46 to 60.75), a gain of only about 1.5-1.7x; the forced-C build beats RVV below about 52-54 px widths (caa79f2). The 2011 SSE2 and NEON rows are first-party commit messages with no compiler or flags and CPU given only as Intel Core i7. 'Release build' means the Meson buildtype, not a stated flag list. No independent benchmark; gitlab.freedesktop.org unreachable, evidence read from the X11Libre GitHub mirror.
- Enricher: the tier-A RVV row's baseline (e1f49d9) is not the general compositing path but pixman-fast-path.c's scalar bits_image_fetch_bilinear_affine_normal_a8r8g8b8, which runs a repeat() wrap and mask test per tap that the RVV cover fetcher skips, so the 1.53x and 1.67x mix SIMD with a cover-only shortcut. Absolute MPix/s are not comparable across RVV commits (pure-scale row 75.39 in e1f49d9 vs 116.91 in the caa79f2 baseline with the governor pinned at 2.2 GHz; e1f49d9 states no frequency). The RVV affine fetchers are on master only (September 2026); the newest tag is pixman-0.46.4 (2025-07-20). The x86 and ARM SSE2, SSSE3 and NEON bilinear paths are scale-only, so rotate and shear run scalar C there. RVV math is bit-exact with the C formula.

## Caveats and trade-offs

Tier A rests on the RVV commit e1f49d9: the benchmark is in-tree (test/affine-bench.c), the command lines, compiler, build type and CPU are stated, and the runs are interleaved medians. 'Release build' is a Meson build type, not a literal flag list; it maps to -O3 under Meson's documented buildtype, and pixman's meson.build supplies -march=rv64gcv1p0 for the RVV file. The baseline is the previous tree, where rotated and sheared bilinear sources fall back to the generic C fetch (the existing bilinear cover iterators cover pure scaling only). The generic C file is built for the toolchain's default ISA, the usual runtime-dispatch setup, so the gain mixes hand-written RVV with any loss of autovectorization in the default build. The gain is about 1.5-1.7x on RISC-V; at row widths under about 52-54 pixels a forced-C build beats RVV (caa79f2). caa79f2's affine table uses a test-only affine-bench variant that is not in the tree. The SSE2 and NEON rows are first-party Nokia commit messages from 2011 (Siarhei Siamashka). The x86 CPU is given only as 'Intel Core i7', there is no compiler or flags, and the microbenchmark tool is unnamed; the 'op=1, src=..., dst=..., speed=' output does not match the in-tree lowlevel-blt-bench format. The 2011 baseline was the general compositing path of that time; later changes such as the SSSE3 bilinear iterator may have narrowed or moved the gap, so those ratios are historical. The NEON messages do not say that 'before' is the general C path; this is inferred from the diffs, which only add fast-path table entries and scanline functions. No SSSE3 fast-path-against-generic numbers were found. The aarch64 NEON commit (eadb828) points to freedesktop bug 94758, which was not opened. No independent third-party benchmark was found. gitlab.freedesktop.org failed from this environment (getaddrinfo ENOTFOUND), so every page opened is the X11Libre/mirror.fdo.pixman GitHub mirror (described as a 'Read-only mirror for CI'; upstream gitlab.freedesktop.org/pixman/pixman.git). COPYING describes MIT as the license 'agreed upon by most contributors'; some files carry older permissive X11/HPND-style notices (for example test/affine-bench.c). [retier] Enricher: the RVV cover fetcher skips the repeat() wrap and mask test the scalar baseline runs per tap, so the 1.53x and 1.67x mix SIMD with a cover-only shortcut; absolute MPix/s differ across RVV commits (frequency unstated in e1f49d9); the RVV fetchers are unreleased (master only, newest tag 0.46.4); x86 and ARM bilinear SIMD paths are scale-only.

Fast paths are per-architecture and chosen at run time: x86 MMX/SSE2/SSSE3, ARM NEON and A64 NEON, ARMv6 SIMD, MIPS DSPr2, POWER VMX, RISC-V RVV (added in the 0.46 series). Only format and operator combinations that have a registered fast path are accelerated; everything else drops to the general path. The environment variable PIXMAN_DISABLE (for example 'sse2 ssse3 mmx') turns implementations off, so the same binary can be timed with and without SIMD. The SSE2 bilinear path in this commit is deliberately naive (one pixel at a time, SRC only, three repeat modes), and part of its gain comes from restructuring the scanline loop (single pass without a temporary buffer), not only from SIMD.

## Maintenance

Actively maintained: the GitHub mirror's last commit is 2026-10-02, and RVV work by ISCAS contributors landed through September 2026 (committed by mattst88). MIT-licensed, but the RVV affine fetchers are not in any tag yet (newest 0.46.4, 2025-07-20). The upstream gitlab.freedesktop.org was unreachable, so everything was read from the X11Libre read-only mirror. The record's baseline wording ('general compositing path') is wrong for the tier-A RVV rows: their baseline is the format-specialised C fetcher in pixman-fast-path.c.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. RVV commit e1f49d9 (author date 2026-09-01) reports the in-tree benchmark test/affine-bench.c with exact command lines (taskset -c 2 ./test/affine-bench -b 0.8660254 -0.5 0.5 0.8660254 and -b 1 0.25 0.25 1), GCC 15.2.0, a Meson release build (buildtype=release, i.e. -O3, plus -march=rv64gcv1p0 for pixman-rvv.c from the public meson.build) and a SpacemiT K3 CPU, against the previous tree's generic C bilinear affine fetch, as medians of five interleaved runs. The SSE2 and NEON rows the record led with are first-party 2011 commit messages without compiler, flags or exact CPU, so on their own they are tier C.
- **Verifier notes:** All numbers check out verbatim against the mirror's commit messages (3500293, 17feaa9, 2ee27e7, 29003c3, e1f49d9); the derived ratios 2.35x and 1.15x are correct. I upgraded the entry to A on the 2026 RVV commit (in-tree affine-bench, GCC 15.2.0, Meson release, SpacemiT K3, interleaved medians against the generic C fetch), so the record's name no longer matches its primary row. Consider a name override such as 'pixman (SIMD bilinear fast paths: SSE2, NEON, RVV)'. The license (MIT, COPYING), last commit 2026-10-02 and active status are confirmed on the mirror. If the orchestrator does not accept a Meson build type as stated flags, the entry falls back to C.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`, `baseline`
- **Shortcomings recorded by:** verifier batch-120 (wave 10 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/350029396d911941591149cc82b5e68a78ad6747>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/350029396d911941591149cc82b5e68a78ad6747.patch>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/17feaa9c50bb8521b0366345efe181bd99754957>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/2ee27e7d79637da9173ee1bf3423e5a81534ccb4>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/29003c3befe2159396d181ef9ac1caaadcabf382>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/e1f49d9e6665ce354b90a189bf7bb5bbde9a1f20>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/e1f49d9e6665ce354b90a189bf7bb5bbde9a1f20.patch>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/caa79f2>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/95853c3>
  - <https://github.com/X11Libre/mirror.fdo.pixman>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commits>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commits/master/pixman/pixman-rvv.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/COPYING>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/meson.build>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/test/affine-bench.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/test/scaling-bench.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/test/lowlevel-blt-bench.c>
- **Sources the enricher read:**
  - <https://github.com/X11Libre/mirror.fdo.pixman>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/e1f49d9e6665ce354b90a189bf7bb5bbde9a1f20>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/e1f49d9e6665ce354b90a189bf7bb5bbde9a1f20.patch>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/caa79f2>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/95853c31d507ddc6c20bf933324d478ab09714d9>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/350029396d911941591149cc82b5e68a78ad6747>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commit/fda93e625df86d4b82faa4d7307b5ec943908f36>
  - <https://github.com/X11Libre/mirror.fdo.pixman/commits/master>
  - <https://github.com/X11Libre/mirror.fdo.pixman/tags>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/README.md>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/meson.build>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/meson.options>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/NEWS>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/meson.build>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-rvv.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-riscv.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-fast-path.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-inlines.h>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-private.h>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-implementation.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-bits-image.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-ssse3.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-sse2.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/pixman/pixman-arm-neon.c>
  - <https://raw.githubusercontent.com/X11Libre/mirror.fdo.pixman/HEAD/test/affine-bench.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://gitlab.freedesktop.org/pixman/pixman`) · [data/wave10/enrich/raw/gitlab_freedesktop_org_pixman_pixman.json](../../../data/wave10/enrich/raw/gitlab_freedesktop_org_pixman_pixman.json) (enrichment confidence 0.78)

</details>
