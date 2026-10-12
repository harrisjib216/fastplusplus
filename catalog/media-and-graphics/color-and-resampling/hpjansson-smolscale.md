# Smolscale

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `LGPL-3.0-only OR BSD-4-Clause` · 🔴 abandoned

> Embeddable C bilinear/box RGBA scaler (SWAR, AVX2, row-batch threading); no published speed ratio against Pixman, libswscale or stb.

| | |
|---|---|
| **Beats** | libswscale (FFmpeg), Pixman, stb_image_resize, GDK-Pixbuf, SDL_gfx and Skia (as wired into the project's own benchmark harness) |
| **Claimed result** | No ratio against any baseline is reachable. Search snippets of the author's blocked 2019 post 'Battle of the Bilerps' give absolute throughput only (about 5.3 Gpx/s, roughly 21 GB/s of input, on 8 threads of an i7-4770K for a 16383x16383 downscale) and directional statements (Pixman the fastest single-threaded competitor at 0.5-1.0x of Smolscale's speed, Skia below 0.5x); libswscale and stb_image_resize are not in the published comparison. The figures predate the 2023 rewrite. |
| **Workload** | Proportional scaling sweep (test.c run_benchmark_proportional) of a random 32-bit RGBA canvas from 0.01x up to 2x of the input size, so both downscaling and upscaling. The bench.sh defaults use 200 steps and 5 repetitions on 1920x1080 and 3840x2160 inputs (0.01-2x) and 7680x4320 (0.01-1x). TESTS_AVAILABLE adds sets such as 16383x16383 at 0.0001-0.1x. Each library runs its own filter: libswscale uses SWS_FAST_BILINEAR (scale &lt;= 2) or SWS_AREA; Pixman uses separable box convolution (beyond 2x reduction) or bilinear; GDK-Pixbuf uses GDK_INTERP_BILINEAR; stb_image_resize uses a box filter in linear colorspace with premultiplied alpha. |
| **Metric** | throughput |
| **Hardware** | i7-4770K (Haswell) at 3.5 GHz according to a search snippet of the blocked blog post; not stated in the repo |
| **Compiler and flags** | Makefile: gcc. Smolscale is built with -Wall -Wextra -g -O2 -DSMOL_WITH_AVX2, and smolscale-avx2.c additionally with -mavx2 (runtime dispatch). test.c is built at -O2, and Skia at -O3 when enabled. The baseline libraries (libswscale, Pixman, GDK-Pixbuf, SDL_gfx) are system packages found through pkg-config, so their build flags are the distro's. |
| **Adoption** | 39 stars; vendored into hpjansson/chafa (5.3k stars) as chafa/internal/smolscale |
| **Last commit** | 2023-04-12 |
| **Links** | [repository](https://github.com/hpjansson/smolscale) · [benchmark](https://github.com/hpjansson/smolscale/blob/master/bench.sh) |

## Verdict

No comparative number is reachable. The repo's harness (test.c run_benchmark_proportional via bench.sh) times one-shot calls including setup: smol_scale_simple; sws_getContext + sws_scale + sws_freeContext per call (SWS_FAST_BILINEAR up to 2x reduction, SWS_AREA beyond); Pixman separable box convolution or bilinear into a calloc'd buffer; GDK-Pixbuf bilinear; and the bundled stb_image_resize v0.97 (the old v1) box filter. It reports the mean of (input + output pixels) per second with 5th and 95th percentiles, and no results are committed. Search-result text of the blocked 2019 post says it ran on an i7-4770K at 3.5 GHz with a 2000x2000 RGBA input, taking the fastest of 50 runs at each of 500 sizes, and compared GDK-Pixbuf, Pixman 0.36.0, SDL, Skia and Smolscale; libswscale and stb are not named there. Its qualitative findings put Pixman fastest single-threaded at 0.5-1.0x and Skia among the fastest below 0.5x. Its one number, 8-thread Smolscale at about 5.3 Gpx/s on a 16383x16383 input, measured 2019 code that was largely rewritten in 2023 (premultiplication overhaul, AVX2 lerp).

## Use it when

- Large-factor downscaling or thumbnailing of big RGBA buffers in-process on x86-64, with output rows split across threads. Per a search snippet of the author's post, 8 threads scaled a 16383x16383 image down in about 50 ms, roughly 5.3 Gpx/s of input.
- Pipelines that need scaling fused with pixel-order and alpha-mode conversion, for example unassociated RGBA in and premultiplied BGRA out for a compositor, without a separate conversion pass.
- C or C++ projects that want a dependency-free source drop (libc only) where 'no jaggies' bilinear or box quality is enough, as in Chafa's terminal image renderer.
- Streaming or tiled output: the batch API produces any range of output rows on demand, and the post-row callback can process each row.

## Skip it when

- High-quality resampling (Lanczos, Mitchell, bicubic): it offers only automatically chosen bilinear and box filters with 8-bit interpolation fractions.
- Single-threaded scaling at 0.5x-1.0x: according to search-result text of the author's own 2019 post (snippet only), Pixman's SIMD code was the fastest single-threaded implementation in that range and Skia was among the fastest below 0.5x.
- YUV or planar input, 16-bit or float channels, or images wider or taller than 65535 px.
- Long-term use of the standalone repo. It has been frozen since 2023-04-12 with 19 open issues, and later fixes (allocation checks, a premul16 AVX2 alpha-extraction fix, argument validation) went only into Chafa's copy, which has an incompatible API.
- MSVC builds: the code relies on GNU C extensions (statement expressions in smol_alloc_aligned, __attribute__((always_inline)), __builtin_assume_aligned, __builtin_cpu_supports).

## How it is fast

SWAR: each 32-bit pixel is unpacked into a uint64 with four 16-bit lanes (mask 0x00ff00ff00ff00ff), so one 64-bit multiply, shift and add interpolates all four channels with an 8-bit fraction. A 128bpp layout (two words, 24-bit lanes) is used for linear sRGB or reductions beyond 255x. The filter is picked per axis: copy at 1:1; plain bilinear for upscaling and reductions down to 1/2; bilinear with one or two built-in 'halvings' (2 or 4 bilinear taps accumulated per output, then shifted) for 1/2 to 1/8; and box (area) averaging, with precomputed spans and a fixed-point reciprocal multiplier, beyond 1/8. Scaling is separable: offsets are precomputed once per context, and each horizontally scaled input row is kept in a 4-row ring for the vertical pass. The AVX2 file is chosen at run time with __builtin_cpu_supports, and threading is done by splitting output rows into batches.

## Compared with alternatives

Pick Smolscale for a dependency-free C drop-in that fuses channel reordering and premultiplication with scaling and lets you thread by output-row batches. For measured speed with quality filters, fast_image_resize (Rust, AVX2, beats libvips single-threaded) or stb-image-resize-opt and zimg (C/C++, published ratios) are better-evidenced choices.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc (the test.c benchmark needs glib, libpng, pixman, gdk-pixbuf, SDL_gfx and libswscale) |
| **Minimum toolchain** | GCC or Clang with GNU C extensions; a shim covers GCC &lt; 8 missing _mm256_set_m128i; no C standard is stated |
| **Platforms** | any 64-bit-capable C target through the generic SWAR path; an optional x86-64 AVX2 path (compile smolscale-avx2.c with -mavx2 and everything with -DSMOL_WITH_AVX2) is picked at run time; no NEON or SSE-only path |
| **Thread safety** | smol_scale_batch and smol_scale_batch_full may run concurrently on one context for non-overlapping output rows, and each call mallocs its own four row buffers; smol_scale_simple is documented as single-thread only; destroy the context only after all workers finish. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README is stale. It says to copy three files, but smolscale.c calls _smol_get_generic_implementation() from smolscale-generic.c, so four files are needed (five with AVX2). It also says the AVX2 file is 'mostly just a straight copy of the generic code', yet the current smolscale-avx2.c has about 278 _mm256 intrinsic uses in pack/unpack and the 64bpp horizontal lerp, added in the March-April 2023 rework.
- There is no argument validation and no allocation-failure handling: smol_scale_new's calloc and do_rows' mallocs are unchecked and every entry point returns void. An output dimension of 0 divides by zero in precalc_boxes_array (test.c clamps sizes to at least 1), and the uint16 precalc offsets cap dimensions at 65535 with no check. Chafa's copy rejects dimensions outside [1, 65535] and returns 0 on failure.
- The defaults differ between copies: here with_srgb is an explicit argument and switches to the 128bpp path, and issue #2 ('Check if linearization works above 1:8191') is still open; Chafa's copy linearizes by default unless SMOL_DISABLE_SRGB_LINEARIZATION is passed.
- The last standalone commit (2023-04-12) fixed a potential over-read in box precalc, so older vendored copies carry that bug. The code itself comments that box filtering is only precise enough when the input dimension exceeds five times the output.

## Known shortcomings

- Repo carries no results; the numbers (16383x16383 in about 50 ms on 8 threads, i7-4770K) are snippet-only from the blocked hpjansson.org post and give no ratio against a baseline. Smolscale's multi-threaded path gets all cores while libswscale, Pixman and stb ran single-threaded, each with its own filter. Code is maintained inside chafa/internal/smolscale (Chafa, 5.3k stars, commit 2026-09-25).
- Retiered C to D (retier-13): no ratio against any baseline is reachable; the blog snippets give absolute throughput and directional claims only (Pixman 0.5-1.0x, Skia under 0.5x), for the 2019 code before the 2023 rewrite, and libswscale and stb_image_resize are not in the published comparison. README stale (build needs smolscale-generic.c); no allocation or argument checks (dimension 0 divides by zero); the harness times sws_getContext per call and bundles stb_image_resize v0.97; the Chafa copy is maintained but API-incompatible.

## Caveats and trade-offs

The evidence is snippet-only. The comparison numbers are in a blog post that could not be opened (egress blocked), so the speedup against each baseline is unconfirmed and the tier is capped at C. The public harness ships no results. Threading is asymmetric: 'Smolscale MT' (test.c scale_do_smol_threaded) runs a GThreadPool with g_get_num_processors() threads, while libswscale, Pixman, stb and GDK-Pixbuf are called single-threaded. The libraries also do different work, since each uses its own filter (fast bilinear or area, box convolution, bilinear, box in linear light), so quality differs. The README said at the time that the AVX2 file was 'mostly just a straight copy of the generic code'. The benchmark compares 2019-era library versions. The standalone repo's last commit is 2023-04-12, but the code is still developed inside Chafa (chafa/internal/smolscale, commits up to 2026-09-25), which is the maintained copy. The license is LGPLv3 or BSD 4-clause at the user's choice (COPYING). BSD-4-Clause is not OSI-approved, but the LGPLv3 option is. [retier] Snippet-only, directional, and for the 2019 code before the 2023 rewrite. The README is stale (the build needs smolscale-generic.c; the AVX2 file has about 278 _mm256 uses). No allocation or argument checks (a zero dimension divides by zero). The harness times sws_getContext inside each call and bundles stb_image_resize v0.97. The Chafa copy is maintained but has an incompatible API.

Three files (smolscale.c, .h, -private.h) plus an optional AVX2 file; copyable into a project. Handles 4-channel 32 bpp packed data (RGBA, ARGB, BGRA) and 3-channel data, premultiplied or unassociated alpha, host-byte-order agnostic, maximum 65535x65535. Quality goal is 'reasonable' (no aliasing), not Lanczos-class. Row-batch and one-shot APIs, easily parallelised. Dual licence: BSD 4-clause (advertising clause) or LGPLv3; closed-source use needs credit or an LGPL library split.

## Maintenance

The standalone repo has been abandoned since 2023-04-12 (278 commits, 19 open issues, almost all the author's own TODOs). The maintained copy is chafa/internal/smolscale in Chafa (commits through 2026-09-25: AVX2 linearization, compositing, nearest mode, argument and allocation checks), but its API is incompatible, so vendor from Chafa under the same LGPLv3-or-BSD-4-Clause choice.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** bench.sh and test.c wire Smolscale against libswscale, Pixman, stb_resize and GDK-Pixbuf, and the Makefile gives gcc with -O2, but the repo ships no results. The only numbers are absolute throughput figures from search snippets of the author's blocked blog post, so the tier is capped at C and no ratio against any baseline was seen.
- **Retiered** C to D: Lowered C to D: after the enricher's pass there is still no ratio against any baseline anywhere reachable. The repo ships the harness (bench.sh, test.c, Makefile with gcc -O2) but no results; the only figures are search snippets of the author's blocked 2019 blog post, which give absolute throughput (about 5.3 Gpx/s on 8 threads for a 16383x16383 downscale) and directional statements (Pixman the fastest single-threaded competitor at 0.5-1.0x, Skia among the fastest at under 0.5x; libswscale and stb_image_resize not in the published comparison). Those figures are also for the 2019 code, before the 2023 rewrite. Directional evidence without a reproducible number is D.
- **Verifier notes:** There is no comparative number anywhere reachable, only absolute throughput from snippets. C is kept per the snippet rule, but this is close to D. An enricher with blog access could add per-library ratios. Consider pointing users at Chafa's actively maintained copy.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hpjansson/smolscale>
  - <https://github.com/hpjansson/smolscale/commits/master>
  - <https://github.com/hpjansson/smolscale/tree/master/gnuplot>
  - <https://github.com/hpjansson/smolscale/tree/master/tools>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/README>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/plot.sh>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/test.c>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/COPYING>
  - <https://github.com/hpjansson/chafa/tree/master/chafa/internal/smolscale>
  - <https://github.com/hpjansson/chafa/commits/master/chafa/internal/smolscale>
- **Sources the enricher read:**
  - <https://github.com/hpjansson/smolscale>
  - <https://github.com/hpjansson/smolscale/commits/master>
  - <https://github.com/hpjansson/smolscale/issues>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/README>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/COPYING>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/plot.sh>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/test.c>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/smolscale.h>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/smolscale-private.h>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/smolscale.c>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/smolscale-generic.c>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/smolscale-avx2.c>
  - <https://raw.githubusercontent.com/hpjansson/smolscale/HEAD/stb_image_resize.h>
  - <https://github.com/hpjansson/chafa/tree/master/chafa/internal/smolscale>
  - <https://github.com/hpjansson/chafa/commits/master/chafa/internal/smolscale>
  - <https://raw.githubusercontent.com/hpjansson/chafa/HEAD/chafa/internal/smolscale/smolscale.h>
  - <https://raw.githubusercontent.com/hpjansson/chafa/HEAD/chafa/internal/smolscale/README>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/hpjansson/smolscale`) · [data/wave10/enrich/raw/github_com_hpjansson_smolscale.json](../../../data/wave10/enrich/raw/github_com_hpjansson_smolscale.json) (enrichment confidence 0.6)

</details>
