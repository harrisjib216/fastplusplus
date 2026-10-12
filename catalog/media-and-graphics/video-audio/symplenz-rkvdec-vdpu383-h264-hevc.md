# rkvdec-vdpu383 HEVC/H.264 read-cache fix

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🟢 active

> Linux kernel patch that turns on the RK3576 VDPU383 decoder's read caches, cutting mainline HEVC/H.264 hardware decode time several-fold.

| | |
|---|---|
| **Beats** | Mainline Linux rkvdec-vdpu383 HEVC and H.264 backends (upstream driver without read-cache configuration); vendor MPP stack as reference |
| **Claimed result** | Pure hardware decode time, 1080p, RK3576, kernel 7.0.1-edge-rockchip64, upstream driver with read cache off versus this patch with it on: HEVC \~12 ms to 1.70 ms (\~7x), H.264 8.7 ms to 3.6 ms (\~2.4x). The README table labels the HEVC result '= vendor MPP', but the same README later says a 'consistent \~1.9x residual vs the vendor stack across all codecs (HEVC and VP9 alike)' remains after the cache fix, so the parity-with-MPP claim is contradicted by the page itself. Whether the times are per frame or per clip is not stated (the values are consistent with per-frame times). |
| **Workload** | MMIO-kick-to-completion hardware decode time of one unnamed 1080p clip (HEVC and H.264) on the RK3576 VDPU383 decoder under kernel 7.0.1-edge-rockchip64, with the patch's hevc_cache module parameter set to 0 (upstream behaviour) versus 1. |
| **Metric** | latency |
| **Hardware** | Rockchip RK3576 (VDPU383 decoder) |
| **Adoption** | 1 star |
| **Last commit** | 2026-06-28 |
| **Links** | [repository](https://github.com/SympleNZ/rkvdec-vdpu383-h264-hevc) · [benchmark](https://github.com/SympleNZ/rkvdec-vdpu383-h264-hevc) |

## Verdict

These are first-party numbers on an RK3576 running Armbian 7.0.1-edge-rockchip64, decoding one unnamed 1080p clip. Measured time per frame runs from the decode kick to the hardirq: HEVC \~12 ms cache-off vs 1.70 ms cache-on (\~7x), H.264 8.7 ms vs 3.6 ms (\~2.4x). The timer is published as the sibling driver's vp9_time module parameter (ktime_get at the kick, hardirq timestamp, mean printed every 100 frames), so the values are per-frame means, not per-clip totals. The kick timestamp is taken before the cache writes, so the cache-on time also includes seven MMIO writes. The clip, frame count and run count are not published. The author's own code comments give different figures for the same comparison (HEVC 4.6 ms cache-off vs MPP 1.15 ms, '\~4x'/'\~5x'), so read the ratio as roughly 2-7x, not as a precise number.

## Use it when

- You decode HEVC or H.264 on an RK3576 board (Radxa ROCK 4D, Armbian edge kernels) through mainline V4L2 stateless decoding and hardware decode time limits frame rate or power.
- You maintain a downstream kernel built on Collabora's merged VDPU383 support and want the cheapest throughput gain before tackling AFBC or link-mode pipelining.
- You are comparing mainline against the vendor BSP/MPP stack on the same silicon and need to remove a known non-silicon gap first.
- You want a tiny, auditable change: seven register writes plus one optional ioremap, gated by a runtime module parameter.

## Skip it when

- Any SoC other than RK3576: the patch touches only the VDPU383 backends. RK3588 (VDPU381) also has a 'cache' window in the upstream DT and its upstream backend does not configure it either, but nobody has tested or measured a port.
- You need a fix that git am can apply: the patch file uses elided paths ('drivers/.../rkvdec.c') and tells you in prose to add a struct field, so you must port it by hand or take the much larger experimental sibling driver.
- You need vendor-stack throughput: the README itself reports a \~1.9x residual against MPP after the fix, attributed to missing AFBC reference compression and link-mode pipelining.
- You need upstream-supported code: the patch has not been accepted into mainline. A search found no linux-media submission of the cache fix, only the merged VDPU381/383 series and a May 2026 H.264 deblocking bug thread.
- You need CPU or software decoding, or another codec: VP9/AV1 on this chip live in the sibling out-of-tree driver.

## How it is fast

The VDPU383 has three reference read caches (CACHE0/1/2) in a dedicated register window at 0x27b00600 on RK3576. Mainline Linux (torvalds master, checked 2026-10-05) maps only the 'link' and 'function' windows, so these caches are never configured and every reference read goes to DRAM. The patch writes CACHEABLE|READ_ALLOC|LINE_64 (0x13) to each cache's config register, clears all three, and sets MAX_READS to 0x1c before setting DEC_E. These are the values the author captured from a register-write trace of the vendor MPP driver. It only changes how the hardware fetches memory: the README reports HEVC output byte-identical with the cache off and on.

## Compared with alternatives

Every catalogued sibling decoder (edge264, rivet-h26x, rusty_h265, dav1d) is a CPU decoder racing libavcodec. Pick this patch only when you already use the RK3576 hardware decoder through mainline V4L2 and want it to run at closer to its real speed. On any other platform, or for portable software decoding, use edge264 (H.264) or rivet-h26x/rusty_h265 (HEVC).

## Integration

| | |
|---|---|
| **Form** | source-drop (kernel patch sketch); buildable as the out-of-tree rockchip-vdec.ko module from the sibling rkvdec-vdpu383-av1 repo |
| **Dependencies** | Linux kernel with Collabora's rkvdec VDPU383 HEVC/H.264 backends (merged early 2026); DT node exposing reg-name 'cache' (upstream rk3576.dtsi already does) |
| **Minimum toolchain** | Kernel build tree; developed against Armbian 7.0.1-edge-rockchip64 (kernel headers, KBUILD_MODPOST_WARN=1 for the out-of-tree build) |
| **Platforms** | Rockchip RK3576 (VDPU383) only, aarch64 |
| **Thread safety** | Kernel driver; the cache writes sit in the per-job device_run path serialized by v4l2-m2m; hevc_cache is a plain int module parameter (0644) read without locking |
| **Drop-in for the baseline** | partial: the V4L2 API is unchanged, but the patch must be hand-ported into the mainline rkvdec sources or the whole experimental sibling module must be substituted |

## Gotchas

- Mapping is optional: if the DT lacks reg-name 'cache', the driver silently keeps the old cache-off behaviour. The sibling module logs 'rkvdec: cache window mapped/ABSENT' at probe, so check dmesg. Upstream rk3576.dtsi already lists 'link', 'function', 'cache' (0x27b00600, size 0x100), so the verifier's DT caveat matters only for older or downstream DTs.
- The author's own numbers disagree. README and patch: HEVC \~12 ms to 1.70 ms (\~7x, '= vendor MPP'), H.264 8.7 to 3.6 ms. The sibling driver's 2026-06-27 code comment: HEVC 4.6 ms cache-off vs MPP 1.15 ms (\~4x). Module help text: '\~5x throughput fix'. The H.264 comment: '\~5x pure-HW-decode-time gap vs MPP'.
- The sibling driver that carries the fix is a heavily instrumented development module, about 167 KB of rkvdec.c against 51 KB upstream, with dozens of A/B module parameters. Its AV1 backend has a documented non-deterministic decode bug (docs/NONDETERMINISM_BUG.md: about half of runs wrong). Lift only the cache hunk into production kernels.
- Stale comment in the sibling rkvdec.c: it says 'Default off for the A/B', but the code sets hevc_cache = 1.

## Known shortcomings

- Off-category: a Linux kernel driver change measuring hardware-decoder throughput on one SoC (RK3576, kernel 7.0.1-edge-rockchip64, 1080p, MMIO-to-completion timing: HEVC about 12 ms to 1.70 ms, H.264 8.7 ms to 3.6 ms) with no clip, harness or run count. The README contradicts itself (the table says equal to the vendor MPP stack while the residual section says about a 1.9x gap remains for HEVC), and the patch is a hunk sketch with elided paths, so git am fails.
- Enricher (e123, 2026-10-05): the timer lives in the sibling rkvdec-vdpu383-av1 source (vp9_time parameter, ktime from kick to hardirq, mean over 100 frames), so the numbers are per frame. The author's own figures disagree: README about 12 ms to 1.70 ms (about 7x, '= MPP'), a driver comment of 2026-06-27 gives HEVC cache-off 4.6 ms vs MPP 1.15 ms (about 4x), and the module help says 'about 5x', so the ratio is uncertain; C at best. The upstream rk3576.dtsi already carries the 'cache' register window (0x27b00600), so the verifier's device-tree caveat is mostly moot, but the upstream driver never maps it (confirmed in torvalds master). The sibling driver is heavily experimental and its AV1 backend has a documented nondeterminism bug; no upstream submission found. Possible but unmeasured: the same cache gap on RK3588 VDPU381.

## Caveats and trade-offs

This is a Linux kernel driver patch that writes three read-cache configuration registers before the decode kick in the mainline rkvdec-vdpu383 HEVC and H.264 backends; the speedup is hardware decoder throughput on one SoC (RK3576), not a software codec, and the baseline is the upstream kernel driver rather than FFmpeg, x264/x265 or Opus, so it is off the category baselines. First-party numbers on an unnamed clip with no published timing harness, frame count or repetition count. The README contradicts itself: the table says HEVC with the cache on equals vendor MPP, while the 'Honest residual' section says a \~1.9x gap to the vendor stack remains for HEVC and VP9 after the fix. The HEVC output is stated byte-identical (md5 18f9bbc46cf0528a, cache off and on); no checksum is quoted for H.264 with the cache on (the separate '64/64 bit-exact' statement refers to the H.264 deblock warmup fix, which is not in this repo). The patch file is a hunk sketch with elided paths ('drivers/.../rkvdec.c') and a prose instruction to add a struct field, so it does not apply with git am; the buildable driver lives in the sibling rkvdec-vdpu383-av1 and rkvdec-vdpu383-vp9 repos. Requires a device-tree 'cache' reg window that the RK3576 node may lack. Not yet accepted upstream. All three commits (2026-06-28) are co-authored with an AI assistant. Very new repo, 1 star.

Kernel patch for Rockchip RK3576 only; module parameter hevc_cache is on by default. README reports a remaining \~1.9x gap to the vendor stack (FBC and one more factor) on all codecs.

## Maintenance

A one-off GPL-2.0 drop (three commits, all 2026-06-28, 1 star, no issues or PRs) that has not been submitted or accepted upstream. The change is small enough to port by hand into any kernel carrying the merged VDPU383 backends.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README and the commit message in patches/0001-vdpu383-hevc-h264-read-cache.patch give first-party cache-off versus cache-on hardware decode times (HEVC \~12 ms to 1.70 ms, H.264 8.7 ms to 3.6 ms) with SoC (RK3576), kernel (7.0.1-edge-rockchip64), resolution (1080p) and timing point (MMIO kick to completion), but no clip name, frame count, repetition count or timing harness is published. That is a number with a partial setup, so C rather than D; nothing independent exists.
- **Verifier notes:** Repo page, commit list and patch confirmed: GPL-2.0, not a fork, 3 commits all dated 2026-06-28, 1 star; the numbers match the record. Verdict is downgrade only because the 'equal to vendor MPP' part of the claim is contradicted by the README's own residual section; tier stays C as a first-party number with partial setup. WebSearch found the upstream VDPU383 HEVC/H.264 series (Collabora) and a May 2026 linux-media H.264 bug thread title, but no independent measurement of this cache fix; the sibling rkvdec-vdpu383-mpp-mainline repo carries checksums only, no timings.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party in-driver timer
- **Pages the verifier opened:**
  - <https://github.com/SympleNZ/rkvdec-vdpu383-h264-hevc>
  - <https://github.com/SympleNZ/rkvdec-vdpu383-h264-hevc/commits>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-h264-hevc/HEAD/README.md>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-h264-hevc/HEAD/patches/0001-vdpu383-hevc-h264-read-cache.patch>
  - <https://github.com/SympleNZ/rkvdec-vdpu383-mpp-mainline>
- **Sources the enricher read:**
  - <https://github.com/SympleNZ/rkvdec-vdpu383-h264-hevc>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-h264-hevc/HEAD/README.md>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-h264-hevc/HEAD/patches/0001-vdpu383-hevc-h264-read-cache.patch>
  - <https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/platform/rockchip/rkvdec/rkvdec.c>
  - <https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/platform/rockchip/rkvdec/rkvdec.h>
  - <https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-hevc.c>
  - <https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-h264.c>
  - <https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-regs.h>
  - <https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/platform/rockchip/rkvdec/Makefile>
  - <https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/rockchip/rk3576.dtsi>
  - <https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/rockchip/rk3588-base.dtsi>
  - <https://raw.githubusercontent.com/torvalds/linux/master/Documentation/devicetree/bindings/media/rockchip,vdec.yaml>
  - <https://github.com/SympleNZ/rkvdec-vdpu383-av1>
  - <https://github.com/SympleNZ/rkvdec-vdpu383-av1/tree/main/src>
  - <https://github.com/SympleNZ/rkvdec-vdpu383-av1/tree/main/docs>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/src/rkvdec.c>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/src/rkvdec.h>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/src/rkvdec-vdpu383-hevc.c>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/src/rkvdec-vdpu383-h264.c>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/src/rkvdec-vdpu383-av1.c>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/src/rkvdec-vdpu383-vp9.c>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/src/rkvdec-link.c>
  - <https://raw.githubusercontent.com/SympleNZ/rkvdec-vdpu383-av1/HEAD/docs/BUILD_AND_TEST.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/symplenz/rkvdec-vdpu383-h264-hevc`) · [data/wave10/enrich/raw/github_com_symplenz_rkvdec_vdpu383_h264_hevc.json](../../../data/wave10/enrich/raw/github_com_symplenz_rkvdec_vdpu383_h264_hevc.json) (enrichment confidence 0.6)

</details>
