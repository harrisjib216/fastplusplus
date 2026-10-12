# TurboRes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MPL-2.0` · 🟢 active

> Zig-to-WebAssembly Apple ProRes decoder for JavaScript runtimes; about 2.3-2.8x native FFmpeg 7.1.1 throughput on an Apple M4.

| | |
|---|---|
| **Beats** | FFmpeg 7.1.1 native CLI (single- and multithreaded, plus VideoToolbox hardware decode) and ffmpeg.wasm |
| **Claimed result** | Single-threaded: 42 FPS vs 15 FPS native FFmpeg at ProRes 422 HQ 4K (\~2.8x, derived from page data), 128 vs 55 (4444 1080p), 158 vs 57 (422 HQ 1080p), 450 vs 161 (Proxy 1080p). Multithreaded: 250 FPS vs 107 FPS native FFmpeg and 84 FPS ffmpeg.wasm at 4K; 2310 vs 948 FPS at Proxy 1080p. Native hardware-accelerated FFmpeg: 160 FPS at 4K. |
| **Workload** | Apple ProRes decode (422 HQ 4K, 4444 1080p, 422 HQ 1080p, 422 Proxy 1080p), frames per second averaged over 10 runs of decoding a file. |
| **Metric** | throughput |
| **Hardware** | Apple M4 (4P+6E) MacBook Air; TurboRes 1.2.0, FFmpeg 7.1.1 |
| **Compiler and flags** | TurboRes: Zig 0.16, zig build-exe -target wasm32-freestanding -O ReleaseSmall -mcpu=generic+atomics+bulk_memory+multivalue+nontrapping_fptoint+reference_types+sign_ext+simd128 -fno-single-threaded --shared-memory --import-memory (scripts/build-zig.sh --release, called by scripts/build.sh). Browser/wasm engine and version used for the table not stated. Native FFmpeg 7.1.1 build provenance and flags not stated; ffmpeg.wasm row uses @ffmpeg/ffmpeg 0.11.6 with @ffmpeg/core 0.11.0 from unpkg. |
| **Adoption** | 208 stars |
| **Last commit** | 2026-07-14 |
| **Links** | [repository](https://github.com/Vanilagy/turbores) · [benchmark](https://github.com/Vanilagy/turbores) |

## Verdict

Author-run table (TurboRes 1.2.0 versus FFmpeg 7.1.1 CLI, ffmpeg.wasm 0.11 and VideoToolbox on an Apple M4 10-core MacBook Air, averaged over 10 file decodes). Single-threaded: 42 vs 15 FPS at 422 HQ 4K and 450 vs 161 at 422 Proxy 1080p (2.3-2.8x, derived from page data). Multithreaded: 250 vs 107 FPS at 4K and 2310 vs 948 at Proxy (2.2-2.5x across the four files, derived from page data), plus 250 vs 160 against hardware-accelerated FFmpeg. The native baseline runs FFmpeg's scalar C ProRes IDCT on aarch64, and the browser running the wasm is not named.

## Use it when

- Decoding ProRes in a web app (editor, preview or transcoder front end) where WebCodecs has no ProRes support and ffmpeg.wasm is too slow: the README table gives 2.6-3.4x ffmpeg.wasm throughput on the same machine (derived from page data).
- High-resolution ProRes 422 HQ or 4444 at faster than real time on CPU only: 250 FPS at 4K with shared-memory threads on an M4 MacBook Air.
- Pipelines that already demux with Mediabunny or similar and need planar 8/10/12-bit output (I420/I422/I444, with or without alpha) without a separate conversion pass.
- Node, Deno or Bun servers that want a ProRes decoder without native FFmpeg binaries or N-API builds.

## Skip it when

- You need encoding or any codec other than ProRes: it is decode-only and ProRes-only.
- You need output bit-identical to FFmpeg or Apple's decoder: PR #3 measured Y/U/V only 84-87% bit-identical to FFmpeg 6.0 (max difference 2) and 97.2-97.7% to VideoToolbox, despite the README's 'bit-exact' claim.
- Native x86-64 apps that can link FFmpeg: FFmpeg's ProRes IDCT has x86 SIMD but none on aarch64, so the 2-3x lead measured on an M4 versus scalar C may shrink on x86. There are no x86 numbers.
- Pages that cannot be cross-origin isolated (COOP/COEP): you lose shared-memory threading and fall back to the slower worker-pool mode or single-threaded decoding.
- Risk-averse production use: the first release was 2026-06-29, the project has one main author, and a 4x 4444 output-scale bug shipped until 1.2.2.

## How it is fast

The decoder is written from scratch in Zig and compiled to wasm32 with SIMD128, threads and bulk memory (ReleaseSmall). Entropy decoding is nearly branchless, uses a LUT, reads bits through a 64-bit accumulator, and decodes slice pairs interleaved for instruction-level parallelism. The 8x8 IDCT is a float AAN (Arai-Agui-Nakajima) transform with dequantization, AAN scale factors and bit-depth scaling folded into one multiply. The transpose, the float-to-u16 conversion and the 128-bit stores are vectorized, and pixel-format conversion is fused into the store. Shared-memory threading splits every frame across workers dynamically, with no allocation after the first packet.

## Compared with alternatives

Pick TurboRes when the media is ProRes; the catalogued wasm video siblings target other codecs (Pare encodes H.264 and beats ffmpeg.wasm's assembly-less x264, WXInlinePlayer plays H.264/H.265). For a general-purpose multi-codec decoder in the browser, ffmpeg.wasm is still the fallback.

## Integration

| | |
|---|---|
| **Form** | npm module (ESM and UMD builds with an inlined wasm binary and inlined worker) |
| **Dependencies** | none at runtime (zero npm dependencies; the wasm is built with Zig 0.16 for development) |
| **Minimum toolchain** | Runtime with WebAssembly SIMD128, threads and Atomics.waitAsync for shared-memory mode; building needs Zig 0.16 and Node/npm |
| **Platforms** | Any JavaScript runtime with wasm SIMD128 (Chromium, Firefox and Safari per the README; Node, Deno, Bun); shared-memory threading needs cross-origin isolation in browsers |
| **Thread safety** | Each Decoder serializes its own packets with an internal mutex and resolves results in queue order. Within a packet, work is split across shared-memory workers. A Frame is locked while in flight (FrameLockedError). |
| **Drop-in for the baseline** | no |

## Gotchas

- The decoder trusts the caller-supplied FourCC for bit depth. The benchmark hard-codes 'apch', so its '4444 @ 1080p' row decodes the 4444 file to 10-bit, while FFmpeg outputs yuva444p12le. In ap4h/ap4x mode, every 4444 output was 4x too small until PR #3 (fixed in 1.2.2, 2026-07-09), and the bug went unnoticed because the test's reference file had been generated by TurboRes itself.
- Test oracle: tests/tests.test.ts compares frames against gzipped framedata files produced by TurboRes, not by FFmpeg or Apple, so the suite catches regressions but not conformance. The IDCT ends with a truncating float-to-u32 conversion clamped to [0, 2^depth-1], while FFmpeg clamps to [4, 2^depth-5]; together these account for the 1-2 LSB differences.
- Harness asymmetries behind the table: TurboRes pre-demuxes every packet into memory and runs 3 warm-up passes. The native FFmpeg script times CLI demux plus decode as (11-loop minus 1-loop rtime)/10. benchmark-ffmpeg-wasm.html runs stream_loop 0 and 9 (1 and 10 passes, not 1 and 11) with 10 threads hard-coded and leaves the arithmetic to the reader. No single-threaded configuration of TurboRes or ffmpeg.wasm is committed, and neither the browser nor the native thread count is named.
- To reproduce, build the wasm with ./scripts/build-zig.sh --release first. benchmark-turbores.html imports ../src/index, which inlines build/lib.wasm, and the default build (also run by npm test) is Debug. Release builds use ReleaseSmall, not ReleaseFast.

## Known shortcomings

- Browser and wasm engine unnamed, native FFmpeg build unstated; FFmpeg 7.1.1's ProRes IDCT has SIMD only on x86 (proresdsp.c), so the M4 baseline ran scalar C; input is pre-demuxed against a CLI demux; single-threaded configs are not scripted; the "bit-exact" claim is contradicted by PR #3 (max diff 2 vs FFmpeg); the 4444 scale bug fixed 2026-07-09 is not on the benchmarked apch path.
- Numbers stand, no invalidating flaw. The test references are TurboRes's own output (PR #3 confirms a silently wrong 4444 reference), so 'bit-exact' is untested and false against FFmpeg (max diff 2). The ffmpeg.wasm script runs stream_loop 0 and 9 (1 and 10 passes; the native script 1 and 11) with the arithmetic left manual; the benchmark page inlines build/lib.wasm and the default build is Debug (build release first). Recheck lead: draft PR #5 'TurboRes native' adds x86-64 and aarch64 native builds plus x86-64 benchmarks that would test the lead against FFmpeg's x86 SIMD IDCT.

## Caveats and trade-offs

First-party numbers on one Apple M4 laptop; the browser (and so the wasm JIT) is not named. Baseline weakness: FFmpeg 7.1.1's ProRes IDCT has SIMD only on x86 (libavcodec/proresdsp.c calls ff_proresdsp_init_x86 under ARCH_X86 and nothing for aarch64), so on the M4 native FFmpeg ran its scalar C IDCT while TurboRes uses wasm SIMD128; the 2-3x lead over native FFmpeg may shrink on x86. Harness asymmetry: TurboRes pre-demuxes all packets into memory (Mediabunny) and runs 3 warm-up passes, while the FFmpeg CLI script ((11-loop rtime minus 1-loop rtime)/10 with -f null) includes mov demuxing and file reads; the VideoToolbox row (-hwaccel videotoolbox without a hardware output format) includes copying frames back to system memory. benchmark-turbores.html is the multithreaded variant only and benchmark-ffmpeg-wasm.html hard-codes 10 threads, so the single-threaded rows are not reproducible from committed code; the benchmark hard-codes proresFourCc 'apch' for every file, so the 4444 file is decoded under the 422 HQ profile (10-bit output scale vs FFmpeg's yuva444p12le). Correctness: the README says decoding is bit-exact, but PR #3 (merged 2026-07-09, after the 1.2.0 benchmark update of 2026-07-02) fixed 4444 (ap4h/ap4x) output values that were 4x too small and reported Y/U/V only 84-87% bit-identical to FFmpeg 6.0 (max difference 2) and 97.2-97.7% to VideoToolbox (float AAN IDCT), so outputs are close but not bit-exact; the 'apch' path used by the benchmark was not affected by that bug. Release build uses ReleaseSmall. Test videos are hosted on an external R2 bucket. A second merged record of the same repo exists (paper:turbores-aslang-registry, category assemblyscript-and-wasm-langs).

Decoder only (no ProRes encoder). Needs WebAssembly SIMD; the multithreaded path uses wasm shared memory and a worker pool option. MPL-2.0 is file-level copyleft. Hand-written for ProRes, so no other codecs.

## Maintenance

Active but very young (npm 1.0.0 on 2026-06-29, 1.2.2 on 2026-07-09, last commit 2026-07-14). MPL-2.0 (file-level copyleft), zero runtime dependencies, about 50 kB gzipped, so it is easy to adopt. Draft PR #5 ('TurboRes native') adds native x86-64 and aarch64 builds with M4 and x86-64 benchmarks and is worth rechecking for an x86 comparison against FFmpeg's SIMD IDCT. No harness flaw invalidates the numbers, but the 'bit-exact' claim is false against FFmpeg (max difference 2) and the tests are self-referential.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party README Performance table (TurboRes 1.2.0 vs FFmpeg 7.1.1 CLI and ffmpeg.wasm on an Apple M4 MacBook Air) matches every quoted number, and the harness is public (benchmark/benchmark-turbores.html, benchmark/benchmark-ffmpeg-native.sh, benchmark/benchmark-ffmpeg-wasm.html) with Zig flags in scripts/build-zig.sh. It is not A because the browser/wasm engine and version that JIT-compile the TurboRes side are never named (same rule that kept galois at C and let pare reach A only with a pinned Chromium build), the native FFmpeg build is unstated, and the single-threaded TurboRes and ffmpeg.wasm configurations are not in the committed scripts.
- **Verifier notes:** All README numbers confirmed (single-threaded 42/128/158/450 FPS vs native FFmpeg 15/55/57/161; multithreaded 250/763/920/2310 vs 107/342/375/948, VideoToolbox 160/256/464/466, ffmpeg.wasm 84/288/295/706); metadata confirmed (MPL-2.0, 208 stars, 88 commits, last commit 2026-07-14, not a fork). Shortcomings to record: browser unstated, native FFmpeg on aarch64 lacks SIMD ProRes IDCT, pre-demuxed input vs CLI demux, single-threaded configs not scripted, 'bit-exact' claim contradicted by PR #3 (max diff 2 vs FFmpeg), 4444 scale bug fixed after the benchmark (not on the benchmarked apch path). paper:turbores-aslang-registry is a second record of this repo and probably wants decision duplicate.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-81 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Vanilagy/turbores>
  - <https://github.com/Vanilagy/turbores/commits>
  - <https://github.com/Vanilagy/turbores/pull/3>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/README.md>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/benchmark-ffmpeg-native.sh>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/benchmark-turbores.html>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/benchmark-ffmpeg-wasm.html>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/scripts/build-zig.sh>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/package.json>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.1.1/libavcodec/proresdsp.c>
- **Sources the enricher read:**
  - <https://github.com/Vanilagy/turbores>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/README.md>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/package.json>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/benchmark-ffmpeg-native.sh>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/benchmark-turbores.html>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/benchmark/benchmark-ffmpeg-wasm.html>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/scripts/build-zig.sh>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/scripts/build.sh>
  - <https://github.com/Vanilagy/turbores/tree/main/src>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/decoder.zig>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/decoder.ts>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/runtime.ts>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/wasm.ts>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/index.zig>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/frame.zig>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/worker.zig>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/misc.zig>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/src/BrkAllocator.zig>
  - <https://github.com/Vanilagy/turbores/tree/main/tests>
  - <https://raw.githubusercontent.com/Vanilagy/turbores/HEAD/tests/tests.test.ts>
  - <https://github.com/Vanilagy/turbores/pulls?q=is%3Apr>
  - <https://github.com/Vanilagy/turbores/pull/3>
  - <https://github.com/Vanilagy/turbores/pull/5>
  - <https://github.com/Vanilagy/turbores/issues?q=is%3Aissue>
  - <https://github.com/Vanilagy/turbores/commits/main>
  - <https://registry.npmjs.org/turbores>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/vanilagy/turbores`) · [data/wave13/enrich/raw/github_com_vanilagy_turbores.json](../../../data/wave13/enrich/raw/github_com_vanilagy_turbores.json) (enrichment confidence 0.8)

</details>
