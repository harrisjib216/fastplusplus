# NanoSVG2 (RudjiGames fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🟢 active

> Copy of the two-header NanoSVG parser and rasterizer with SSE2 blending and span-delta coverage, 2.5-3.7x faster than its own previous rasterizer.

| | |
|---|---|
| **Beats** | The fork's own pre-PR master, not a category incumbent: a 2024-08-15 copy of memononen/nanosvg whose rasterizer matches upstream nanosvgrast.h apart from later upstream fixes (paint order, NaN clamping, dash stroke preparation). Skia, Cairo and Blend2D are not measured, and upstream nanosvg HEAD is not measured either. |
| **Claimed result** | PR #2 vs pre-PR master (mean of 40 runs, -O2, x86-64): rasterization 2.5x-3.7x faster per the PR text (23.svg 1x 15.5 ms to 5.6 ms; 23.svg 3x 83.4 ms to 24.3 ms; drawing.svg 1x 8.7 ms to 3.4 ms; drawing.svg 3x 85.8 ms to 31.4 ms; nano.svg 1x 1.29 ms to 0.35 ms; nano.svg 3x 10.8 ms to 2.9 ms; per-row ratios 2.56x-3.72x, derived from page data), parsing up to about 2x (23.svg 3x 1.17 ms to 0.65 ms). PR #3 on top of that (best of 11 runs, callgrind instruction counts): 1.34x-1.98x (23.svg 1x 3.90 ms to 2.91 ms; 23.svg 3x 19.1 ms to 11.1 ms; drawing.svg 1x 2.49 ms to 1.49 ms; drawing.svg 3x 25.9 ms to 17.6 ms; nano.svg 3x 2.79 ms to 1.85 ms; gradients 3x 4.64 ms to 2.34 ms), output byte-identical to the post-PR #2 master; with NSVG_NO_SIMD the gain mostly disappears (e.g. 23.svg 3x 17.2 ms). The two PRs were timed under different conditions (PR #3's master time for 23.svg 3x, 19.1 ms, is below PR #2's optimized 24.3 ms), so the speedups should not be multiplied. |
| **Workload** | Parsing and rasterizing example/23.svg, drawing.svg, nano.svg and a gradient test SVG at 1x and 3x scale with the single-header NanoSVG rasterizer, before and after each PR. |
| **Metric** | latency |
| **Hardware** | not stated (x86-64 only) |
| **Compiler and flags** | -O2 on x86-64; compiler and version not stated (PR #3 says the SSE2 path enables on GCC, Clang and MSVC) |
| **Adoption** | 0 stars, 0 forks, 12 commits |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/RudjiGames/nanosvg2) · [benchmark](https://github.com/RudjiGames/nanosvg2/pull/2) |

## Verdict

The fork's own PRs time its rasterizer against its pre-PR master (essentially upstream NanoSVG's 2024 rasterizer) on example/23.svg, drawing.svg, nano.svg and a gradient test at 1x and 3x scale, -O2 on x86-64 with no CPU or compiler version: PR #2 reports 2.5-3.7x (mean of 40 runs) and PR #3 adds 1.34-1.98x with SSE2 (best of 11, callgrind counts); no harness is committed, and the two PRs' absolute times are not comparable, so the gains should not be multiplied. Reading the diffs found no correctness bug behind these numbers: the SSE2 blend, coverage prefix sum and reciprocal unpremultiply match the scalar arithmetic (the reciprocal identity holds for all 8-bit inputs when rechecked).

## Use it when

- Baking SVG icons or UI glyphs into textures at load time in a game or tool, where a two-header, dependency-free C library is worth more than full SVG conformance.
- You already ship upstream NanoSVG and want a faster drop-in rasterizer on x86-64 without changing call sites.
- Small to medium images (tens to a few hundred pixels per side) with simple fills and gradients, rendered on one thread per rasterizer object.
- Builds that cannot pull in C++ or a large dependency tree (Cairo, Skia, Blend2D).

## Skip it when

- You need correct rendering of real-world SVG: no clip paths, masks, filters, patterns, text, &lt;use&gt; handling beyond the parser's support, or embedded images; the inherited README still calls the rasterizer 'not particular fast or accurate'.
- Quality matters: anti-aliasing uses only 5 vertical subsamples per pixel, so near-horizontal edges show visible banding compared with analytic-coverage renderers.
- Non-x86 targets expect the full gain: the SSE2 path is x86 only, and PR #3's own NSVG_NO_SIMD column runs about 1.0-1.1x the post-PR #2 code, so ARM gets roughly the PR #2 algorithmic speedup only.
- You need upstream NanoSVG's newer features: this copy lacks upstream's paint-order support (shape-&gt;paintOrder) and uses its own 2024 CSS style handling rather than upstream's class-based one.
- You want a maintained, reviewed library: 0 stars, 12 commits, all speed work landed on 2026-09-24 from an AI-agent branch, and no tests or fuzzing harness are in the repo.

## How it is fast

The rasterizer is NanoSVG's 5-subsample scanline converter with exact horizontal fixed-point coverage; the fork stores fully covered spans as start/end deltas in an int array and prefix-sums them once per pixel row instead of adding 51 to every byte five times per row. The blend loop fuses that prefix sum with SSE2 4-pixel source-over blending (div255 as _mm_mulhi_epu16(x+1, 257)), skips zero-coverage pixels, writes fully opaque runs directly, evaluates gradient colors only for covered pixels, starts at the first edge's row and stops when edges run out, and limits the unpremultiply/defringe pass to the drawn bounding box using 24-bit reciprocals instead of divisions. It also stops zero-length cubics from recursing 2047 times in the flattener, and the parser replaces strtoll/pow/sscanf/strchr with hand-written digit loops and power-of-ten tables.

## Compared with alternatives

Pick it over LunaSVG or ThorVG when you want two C headers with no build step and only need flat fills, gradients and strokes for icon baking; pick LunaSVG for a C++ renderer with much broader SVG support, and Blend2D or ThorVG when rendering quality, clipping or throughput on large scenes matter.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond libc and libm (stdio.h, string.h, stdlib.h, math.h); emmintrin.h for the SSE2 path |
| **Minimum toolchain** | C99 for nanosvg.h (the CDATA skip in nsvg__parseXML declares a variable after a statement); nanosvgrast.h is stated to build with -std=c89 -pedantic; CMake 3.10 for the optional package |
| **Platforms** | any; SSE2 fast path on x86-64 (GCC, Clang, MSVC) and 32-bit MSVC with /arch:SSE2, scalar elsewhere or with NSVG_NO_SIMD |
| **Thread safety** | not documented; no mutable globals in either header, but an NSVGrasterizer holds scratch buffers, so use one rasterizer per thread |
| **Drop-in for the baseline** | yes |

## Gotchas

- Output is not byte-identical to the pre-PR code or to upstream: PR #2 fixes the defringe check (x-1 &gt; 0 became x &gt; 0), which changes the color of fully transparent pixels in column 1 and row 1, and the hex color parser now rejects malformed colors (spaces, signs, 0x prefixes) that the sscanf version accepted.
- nsvgRasterize still clears the whole destination buffer each call, so it cannot composite onto existing pixels; the unpremultiply pass then runs only over the drawn bounding box plus a one-pixel border.
- Coverage still wraps modulo 256 like the original unsigned char sums, so heavily overlapping sub-paths under the nonzero rule keep NanoSVG's existing artifacts.
- The repository is a standalone copy of a 2024 NanoSVG snapshot with local parser changes (title capture, CDATA skipping, rgba alpha), not a GitHub fork, so upstream fixes do not flow in automatically.

## Known shortcomings

- Fork of memononen/nanosvg whose 2.5x-3.7x (PR #2) and 1.34x-1.98x (PR #3) rasterizer gains are measured against the fork's own pre-PR master (an upstream NanoSVG 2024 snapshot), not a category incumbent; Skia, Cairo and Blend2D were never run. No harness in the repo, no CPU, -O2 x86-64 only; the commits are by an account named claude.
- No harness, no CPU and the compiler is unknown; the NSVG_NO_SIMD column is only about 1.0-1.1x, so non-x86 targets get only the PR #2 gain. The fork lacks upstream's paint-order support, nanosvg.h now needs C99 (mixed declarations in CDATA), and output differs from upstream only through the defringe fix and the hex-colour parser rejecting malformed colours. 0 stars, AI-authored pull requests, and the README still says 'not actively maintained'.

## Caveats and trade-offs

Baseline is the fork's own earlier code, not a recognisable category incumbent: no Skia, Cairo or Blend2D numbers, and no run against upstream memononen/nanosvg HEAD (the pre-PR rasterizer is a 2024 snapshot of upstream minus some later upstream fixes, so the gain over upstream is inferred). No harness or benchmark script is in the repo and no CPU or compiler version is given. All optimization commits were authored by an account named 'claude' on branch claude/friendly-ride-r2z9m7 and merged by the owner (milostosic) on 2026-09-24 (PR #2 opened by claude; PR #3 shown as opened by milostosic). PR #2 also fixes a defringe bug, so its output is not byte-identical to the old master in the first row and column. The README, inherited from upstream, still says the rasterizer is 'not particular fast or accurate' and that the project 'is not actively maintained'. Not a GitHub fork: a standalone copy (initial commit 2024-08-15) carrying Mikko Mononen's zlib license; 0 stars.

Single-header C SVG parser plus simple rasterizer; SSE2 path is x86-only (a no-SIMD column is reported). Keeps NanoSVG's limited quality and feature set.

## Maintenance

Active only in the sense that the owner merged three AI-authored PRs on 2026-09-24 (0 stars, README still says 'not actively maintained'); zlib-licensed and two headers, so it is easy to vendor, but treat it as a lightly tested patch set over NanoSVG.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #2 and PR #3 give first-party before/after timings against the repo's own pre-PR master (-O2, x86-64, mean of 40 runs and best of 11 runs), but no benchmark harness is in the repo (example/ holds only example1.c, example2.c and SVGs), and neither compiler version nor CPU model is stated; C.
- **Verifier notes:** No harness and no machine: the PRs state only -O2, x86-64 and run counts. The baseline is not a recognisable incumbent but the fork's own past, which a diff shows is essentially upstream NanoSVG's 2024 rasterizer; I kept it at C as a keep-and-document entry rather than rejecting, since NanoSVG itself is a known library, but if the orchestrator treats own-past baselines as no comparison the reject reason would be no-baseline-comparison. Speedup range corrected to the PR's own 2.5x-3.7x.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `is_fork_of`, `stars_or_usage`, `caveats`, `workload`
- **Pages the verifier opened:**
  - <https://github.com/RudjiGames/nanosvg2/pull/2>
  - <https://github.com/RudjiGames/nanosvg2/pull/3>
  - <https://github.com/RudjiGames/nanosvg2>
  - <https://github.com/RudjiGames/nanosvg2/commits>
  - <https://github.com/RudjiGames/nanosvg2/commits/master>
  - <https://github.com/RudjiGames/nanosvg2/tree/master/example>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/README.md>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/src/nanosvgrast.h>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/14f7ea0/src/nanosvgrast.h>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/3f177c6/src/nanosvgrast.h>
  - <https://raw.githubusercontent.com/memononen/nanosvg/HEAD/src/nanosvgrast.h>
  - <https://raw.githubusercontent.com/memononen/nanosvg/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/RudjiGames/nanosvg2>
  - <https://github.com/RudjiGames/nanosvg2/commits/master>
  - <https://github.com/RudjiGames/nanosvg2/pull/1>
  - <https://github.com/RudjiGames/nanosvg2/pull/2>
  - <https://github.com/RudjiGames/nanosvg2/pull/3>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/README.md>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/src/nanosvgrast.h>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/src/nanosvg.h>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/example/example1.c>
  - <https://raw.githubusercontent.com/RudjiGames/nanosvg2/HEAD/example/example2.c>
  - <https://raw.githubusercontent.com/memononen/nanosvg/HEAD/src/nanosvgrast.h>
  - <https://raw.githubusercontent.com/memononen/nanosvg/HEAD/src/nanosvg.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/rudjigames/nanosvg2`) · [data/wave10/enrich/raw/github_com_rudjigames_nanosvg2.json](../../../data/wave10/enrich/raw/github_com_rudjigames_nanosvg2.json) (enrichment confidence 0.6)

</details>
