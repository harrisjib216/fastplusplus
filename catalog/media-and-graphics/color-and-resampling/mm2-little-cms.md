# Little-CMS fast_float plugin

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0-or-later for the fast_float plugin (plugins/fast_float source headers say 'version 3 of the License, or (at your option) any later version'; COPYING.GPL3 in that directory; the plugin PDF says a paid alternative licence is available from the author). The lcms2 core in the same repo is MIT.` · 🟢 active

> GPL-3.0 add-on for Little CMS 2 that swaps stock transforms for precomputed-table, SSE2 and 15-bit kernels; about 7x on one Lab-to-RGB float case.

| | |
|---|---|
| **Beats** | Little CMS 2 (lcms2) stock transforms |
| **Claimed result** | RawTherapee issue #6016: on a 45.6 MP file exported full size to JPEG with the RTv4_sRGB output profile, 'lab2rgbOut took 5312 ms' without the fast-float plugin vs 754 ms with it (about 7x, derived from page data). The plugin PDF ('LittleCMS floating point extensions 1.7') states increased throughput for 8-bit gray/RGB/CMYK transforms and for 32-bit float transforms, without numbers. |
| **Workload** | RawTherapee exporting a 45.6 MP image to full-size JPEG with the RTv4_sRGB output profile, timing the Lab-to-RGB output colour transform (lab2rgbOut) with and without the fast_float plugin. |
| **Metric** | latency |
| **Adoption** | 751 stars (Little-CMS repo); shipped in lcms2 since 2.10 (ChangeLog). Not used by RawTherapee: issue #6016 remains open and its sources never call cmsFastFloatExtensions. |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/mm2/Little-CMS) · [benchmark](https://github.com/Beep6581/RawTherapee/issues/6016) |

## Verdict

One RawTherapee developer (issue #6016, Dec 2020) reported that the Lab-to-RGB output transform for a 45.6 MP export took 5312 ms with stock lcms2 and 754 ms with the plugin (about 7x). No CPU, thread count, compiler, flags or lcms2 commit are given. lcms2 since 2.11 skips plugins under cmsFLAGS_NOOPTIMIZE, which RawTherapee's lab2rgbOut still passes, so that run must have used locally modified RawTherapee code that was not published on the issue page as read here. The fast path for that case is the 51^3 tetrahedral Lab grid, an approximation of stock output whose error the testbed reports but does not bound.

## Use it when

- You already use lcms2 and run float-to-float transforms (Gray, RGB, CMYK or Lab input) on large images, e.g. a raw developer's working-space-to-output step.
- 8-bit RGB or CMYK transforms on whole images, where the precomputed curve, matrix and tetrahedral tables pay off over millions of pixels.
- Pipelines that hold Photoshop 1.15 fixed-point data (TYPE_\*_15) or need dithered 8-bit output to reduce banding.
- Your application is GPL-3.0-compatible, or you will buy the commercial licence the plugin PDF offers.
- You want speed and keep full ICC v4 profile support: profile parsing and pipeline construction are still done by lcms2.

## Skip it when

- Closed-source or MIT-only products that cannot accept GPL-3.0-or-later and will not buy the alternate licence. The lcms2 core is MIT; this plugin is not.
- Workflows that need bit-identical output to stock lcms2. The testbed accepts float differences up to 0.005 (EPSILON_FLOAT_TESTS) and 0.007 in another check. For the Lab float path, CheckLab2RGB only prints the maximum RGB distance and asserts no limit.
- Soft-proofing or gamut-check transforms (the dispatcher refuses cmsFLAGS_SOFTPROOFING), reversed-polarity (FLAVOR) formats, or transforms that later need cmsChangeBuffersFormat().
- Small per-call batches, e.g. one pixel per call or per-scanline calls. The PDF says creating the transform and starting a call are costly, and it recommends one cmsDoTransformLineStride() call over many lines.
- Unbounded or out-of-range float Lab input. The Lab kernel clamps L\* to 0..100 and a\*/b\* to -128..128 before indexing the grid.

## How it is fast

At transform creation the dispatcher tries, in order, 15-bit matrix-shaper, joined 8-bit curves, an SSE2 8-bit matrix-shaper (float matrix on 1.14 fixed-point shaper tables, chosen after a runtime cpuid check), a plain 8-bit matrix-shaper, joined float curves, a float matrix-shaper, 8-bit and 16-bit prelinearization plus tetrahedral CLUT, and float CLUTs for RGB, CMYK and Lab input. The float Lab-input path (fast_float_lab.c) resamples the whole Lab-to-device pipeline into a 51^3 float grid (33 with cmsFLAGS_LOWRESPRECALC, 66 with HIGHRESPRECALC), puts a sigmoid on the a\*/b\* axes, and evaluates each pixel with tetrahedral interpolation. Stock lcms2 instead runs every float pipeline stage per pixel (its own optimizers skip float formats). So the speedup comes from replacing exact evaluation with table lookups, not only from SIMD.

## Compared with alternatives

Pick it over moxcms (Rust) or jsColorEngine (JS/WASM) when you are in C or C++, already depend on lcms2's full ICC v4.4 implementation, and want the speedup without changing your colour-management code. Pick babl only inside GEGL/GIMP. moxcms publishes reproducible numbers against lcms2, while this plugin has only one anecdotal number.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (liblcms2_fast_float), built from the plugins/fast_float directory of the lcms2 source tree; off by default in autotools, meson and CMake |
| **Dependencies** | lcms2 2.12 or newer (REQUIRED_LCMS_VERSION 2120), libm |
| **Minimum toolchain** | C99 compiler (also compiles as C++ since 2.12); autotools, meson or CMake 3.16+; Visual Studio project in plugins/fast_float/VC2022 |
| **Platforms** | Any platform lcms2 supports. The SSE2 8-bit matrix-shaper kernel is x86 only, with runtime detection, and CMS_DONT_USE_SSE2 disables it. Every other kernel is portable scalar C, and there are no NEON or AVX kernels. |
| **Thread safety** | Transforms evaluate read-only tables built at creation time. Register the plugin once at startup, globally with cmsPlugin or per context with cmsPluginTHR. Beyond that, the plugin's threading is not documented. |
| **Drop-in for the baseline** | partial: one registration call and no other API change, but transforms created with cmsFLAGS_NOOPTIMIZE never reach the plugin (lcms2 2.11+ skips transform plugins under that flag), outputs differ slightly from stock, and only matching format and colour-space combinations are accelerated |

## Gotchas

- cmsFLAGS_NOOPTIMIZE silently disables the plugin. In lcms2 2.11, 2.12 and current master, AllocEmptyTransform calls transform plugins only when that flag is clear, and the plugin PDF does not mention this. RawTherapee's current lab2rgbOut creates its Lab_FLT-to-RGB_FLT transform with cmsFLAGS_NOOPTIMIZE | cmsFLAGS_NOCACHE.
- The autotools build compiles the plugin with -Ofast (plugins/fast_float/src/Makefile.am). That flag implies -ffast-math, under which the isnan() guards in fclamp, flerp and fclamp128 may be optimised away. The meson build does not add -Ofast.
- Past wrong-output and crash bugs in the plugin's issue history, all closed now: #272 (8-bit RGB to Lab with Optimize8BitRGBTransform), #325 (float sRGB to Lab off by about 100x in 2.13.1), #247 (Krita, broken or transparent tiles with cLUT display profiles), #236 and #260 (segfaults). Test your own profiles against stock lcms2 before switching.
- On aarch64 nothing is vectorised. PR #549 (March 2026) fixed an ARM64 compile failure in the SSE2 file, so older releases may not build there.

## Known shortcomings

- Plugin licence is GPL-3.0-or-later (headers and COPYING.GPL3) while the Little-CMS core is MIT. The only numbers are issue #6016 (5312 vs 754 ms) with no methodology. The plugin trades accuracy for speed: its testbed allows a float difference of 0.005.
- The only number needs an unpublished patched build (retier-18): RawTherapee's lab2rgbOut passes cmsFLAGS_NOOPTIMIZE and lcms2 2.11+ skips transform plugins under that flag; RawTherapee does not use the plugin (issue #6016 open, no cmsFastFloatExtensions call in its sources). The 7x path is a 51^3 tetrahedral Lab CLUT approximation (L clamped to 0..100, a/b to plus or minus 128). Autotools builds the plugin with -Ofast (isnan guards may vanish); SSE2 only, no NEON; past wrong-output bugs #272, #325 (about 100x off in 2.13.1) and #247 (Krita), and segfaults #236 and #260, all closed.

## Caveats and trade-offs

Numbers come from one RawTherapee developer's comment in an issue (independent of lcms2 but anecdotal): no CPU, thread count, compiler or flags. The plugin is GPL-3.0-or-later (a commercial licence is sold by the author) while the lcms2 core is MIT, so linking it imposes GPL terms on the application. The plugin trades accuracy for speed: its testbed accepts float results that differ from stock lcms2 by up to 0.005 (EPSILON_FLOAT_TESTS) and 0.007 in another check, so the faster path does not reproduce stock lcms2 output exactly. The testbed would let someone reproduce plugin vs no-plugin MPixel/sec, but I found no published results. The baseline is lcms2 itself, not a different library. [retier] The only number (RawTherapee issue #6016, 5312 ms stock versus 754 ms with the plugin) needs an unpublished patched build, because RawTherapee passes cmsFLAGS_NOOPTIMIZE and lcms2 2.11+ skips transform plugins under that flag; no CPU, thread count, compiler or flags. The 7x path is a 51^3 tetrahedral Lab CLUT approximation (L clamped to 0..100, a/b to plus or minus 128); the testbed accepts float results differing from stock lcms2 by up to 0.005 (0.007 in another check). The plugin is GPL-3.0-or-later (commercial licence sold) while the lcms2 core is MIT. Autotools builds the plugin with -Ofast (isnan guards may vanish); SSE2 only, no NEON. Past wrong-output bugs, all closed: #272, #325 (about 100x off in 2.13.1), #247 (Krita); segfaults #236 and #260.

The plugin lives in plugins/fast_float of the lcms2 repo and registers optimized float-to-float and 8-bit transform kernels (SIMD where available). Only Gray, RGB, CMYK and Lab are optimizable, transforms must have fixed formats (no cmsChangeBuffersFormat), and big blocks are needed to amortise startup.

## Maintenance

Actively maintained in the lcms2 repo (last commit 2026-10-02; the ChangeLog says the formerly commercial plugin was open-sourced under GPL3 in 2.10). It is copyable under GPL-3.0-or-later or a paid licence, while the lcms2 core stays MIT. Correction to the record: RawTherapee does not ship it. Issue #6016 is still open, and RawTherapee's dev CMakeLists.txt, rtengine/iccstore.cc, rtengine/init.cc and rtgui/main.cc never call cmsFastFloatExtensions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** RawTherapee issue #6016 (opened 5 Dec 2020 by RawTherapee developer heckflosse) reports 'lab2rgbOut took 5312 ms' without the plugin and 754 ms with it on a 45.6 MP export, but gives no CPU, threads, compiler or flags; the plugin's own PDF has no numbers and its testbed (plugins/fast_float/testbed/fast_float_testbed.c) prints MPixel/sec against stock lcms2 but no results are published. Numbers without methodology are C.
- **Verifier notes:** Numbers confirmed verbatim on the issue page. Usability changed from mixed to copyable because GPL-3.0-or-later is OSI-approved and no part is unlicensed (precedent: KFR, GPL-2.0-or-later with commercial dual licence, filed copyable); the record's id is the whole lcms2 repo, so check it does not collide with an lcms2-core entry. Metadata on github.com: 751 stars, last commit 2026-10-02 (active); I could not check the 'shipped since lcms2 2.10' claim and left it unchanged.
- **Fields the verifier corrected:** `license`, `usability`, `claimed_speedup`, `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/Beep6581/RawTherapee/issues/6016>
  - <https://github.com/mm2/Little-CMS/tree/master/plugins/fast_float>
  - <https://github.com/mm2/Little-CMS/tree/master/plugins/fast_float/doc>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/doc/LittleCMS%20floating%20point%20extensions%201.7.pdf>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/testbed/fast_float_testbed.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/include/lcms2_fast_float.h>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_float_internal.h>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/LICENSE>
  - <https://github.com/mm2/Little-CMS/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/README.md>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/ChangeLog>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/configure.ac>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/meson.build>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/meson_options.txt>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/meson.build>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/meson.build>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/meson.build>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/Makefile.am>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/include/lcms2_fast_float.h>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_float_internal.h>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_float_sup.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_float_lab.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_float_tethra.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_float_matsh.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_8_matsh_sse.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/src/fast_8_tethra.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/testbed/fast_float_testbed.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/plugins/fast_float/doc/LittleCMS%20floating%20point%20extensions%201.7.pdf>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/src/cmsxform.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/2.11/src/cmsxform.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/lcms2.12/src/cmsxform.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/lcms2.16/src/cmsxform.c>
  - <https://github.com/mm2/Little-CMS/issues?q=fast_float>
  - <https://github.com/mm2/Little-CMS/issues/247>
  - <https://github.com/mm2/Little-CMS/issues/272>
  - <https://github.com/mm2/Little-CMS/issues/325>
  - <https://github.com/Beep6581/RawTherapee/issues/6016>
  - <https://raw.githubusercontent.com/Beep6581/RawTherapee/dev/rtengine/iplab2rgb.cc>
  - <https://raw.githubusercontent.com/Beep6581/RawTherapee/dev/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Beep6581/RawTherapee/dev/rtengine/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Beep6581/RawTherapee/dev/rtengine/iccstore.cc>
  - <https://raw.githubusercontent.com/Beep6581/RawTherapee/dev/rtengine/init.cc>
  - <https://raw.githubusercontent.com/Beep6581/RawTherapee/dev/rtgui/main.cc>
  - <https://raw.githubusercontent.com/Beep6581/RawTherapee/dev/rtgui/main-cli.cc>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/mm2/little-cms`) · [data/wave10/enrich/raw/github_com_mm2_little_cms.json](../../../data/wave10/enrich/raw/github_com_mm2_little_cms.json) (enrichment confidence 0.7)

</details>
