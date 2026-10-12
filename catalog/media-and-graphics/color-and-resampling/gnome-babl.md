# babl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-3.0-or-later` · 🟢 active

> GIMP/GEGL's C pixel-format and matrix+TRC colour-space converter. GIMP claims up to 10x over LCMS2; no published benchmark backs it, and an lcms2 test found babl slower.

| | |
|---|---|
| **Beats** | Little CMS 2 (lcms2) |
| **Claimed result** | GIMP 2.10 release notes (snippet only, page blocked): babl is 'up to 10 times faster than LCMS2 for the cases tested'; no timings, cases or hardware are given. Disputed: the Little CMS blog post 'Babl throughput comparative' (2019-10-02, from the lcms2 project, snippet only) measured lcms2 at 3.59 s vs babl at 6.36 s on 8-bit transforms on a low-end machine, so lcms2 was about 1.8x faster (derived from snippet), and lcms2 with its fast-float plugin took 1.7 s. |
| **Workload** | Pixel format and colour space conversion (GIMP 2.10 and GEGL pipeline). |
| **Metric** | throughput |
| **Adoption** | 25 stars (read-only GitHub mirror of gitlab.gnome.org/GNOME/babl); used by GIMP and GEGL |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/GNOME/babl) · [benchmark](https://www.gimp.org/release-notes/gimp-2.10.html) |

## Verdict

The only claim is first-party and comes without methodology: the GIMP 2.10 release notes (gimp.org, blocked here; WebSearch snippet) say babl is 'up to 10 times faster than LCMS2 for the cases tested', and a search-result summary adds that GIMP uses babl for ICC matrix-based conversions because it is 'an order of magnitude faster' than lcms2. No cases, timings, hardware or code are published. The babl tree holds no lcms2 comparison (tools/babl-benchmark.c times babl fishes alone in MPx/s on 1 Mi-pixel buffers), and the one reachable rebuttal (Little CMS blog, 2019-10-02, snippet only) measured babl at 6.36 s against lcms2 at 3.59 s, roughly 1.8x slower (derived from snippet). Any advantage is plausible only on matrix+TRC RGB paths: CMYK in babl runs through lcms2 itself.

## Use it when

- GEGL or GIMP plug-ins, or any C program that converts pixel buffers between u8/u16/half/float encodings, alpha modes and RGB spaces in one call.
- Matrix+TRC RGB-to-RGB conversion (sRGB, Adobe RGB, ProPhoto, Rec2020, display profiles without CLUTs), where babl folds the profile pair into one 3x3 plus TRC tables.
- Long-running processes that convert many 8-bit images with the same format pair, where the automatic 256^3 lookup table pays off after its 32,768-pixel threshold.
- Interactive previews where you can trade accuracy for speed with babl_fast_fish("fast"/"glitch") or a BABL_TOLERANCE of 0.01-0.1 (docs).

## Skip it when

- CMYK or other CLUT-based ICC work: babl hands every CMYK profile to lcms2 itself (cmsCreateTransform with TYPE_CMYKA_DBL to and from a linear scRGB profile, double precision, BPC on), so it adds a step on top of lcms2 rather than beating it.
- RGB profiles whose A2B0/B2A0 CLUTs matter: babl_space_from_icc refuses them for relative colorimetric ('use lcms, accuracy desired and cluts are present') unless BABL_ICC_INTENT_PERFORMANCE is set, refuses explicit perceptual on CLUT profiles, and does not implement absolute colorimetric or saturation intents.
- Choosing it on speed alone against lcms2: the only timed head-to-head found, from the Little CMS project (2019), had lcms2 at 3.59 s against babl at 6.36 s, and lcms2 with the fast_float plugin at 1.7 s (snippet only).
- Memory-constrained hosts with BABL_LUT enabled: a single 8-bit RGBA fish can allocate 64 MiB (u8 out) or 256 MiB (float out) for its table, freed only after 5 minutes unused by default.

## How it is fast

babl does not walk a general ICC pipeline. For RGB-to-RGB between spaces it multiplies the source RGB-to-XYZ and destination XYZ-to-RGB matrices once into a single float 3x3 (babl-rgb-converter.c), and linearises u8 input through 256-entry TRC tables. Conversions are 'fishes' built from chains of registered fast-path converters. At runtime babl times candidate chains (searching up to BABL_PATH_LENGTH steps, 3 by default) and keeps the fastest one whose error against its 64-bit floating-point reference stays under BABL_TOLERANCE (0.0000047 in code). The choices are cached on disk in \~/.cache/babl/babl-fishes. Hot converters are compiled several times, for x86-64-v2/v3/v4 (SSE4.1, AVX2/F16C/FMA, AVX-512) and for NEON, and dispatched at runtime. Once a fish with 8-bit-per-channel input has processed 32,768 pixels, babl replaces it with a full 256^3 (or 256^2) lookup table, enabled by default on little-endian hosts (BABL_LUT).

## Compared with alternatives

Pick babl when you need GEGL-compatible pixel-format conversion (data type, alpha mode and matrix+TRC RGB space in one call) inside a C codebase. For ICC transforms with CMYK or CLUT profiles, use Little CMS 2 with its fast_float plugin (C) or moxcms (Rust); jsColorEngine covers the same ICC ground for JavaScript hosts.

## Integration

| | |
|---|---|
| **Form** | shared lib (meson build; extensions are loaded from BABL_PATH as shared objects at runtime) |
| **Dependencies** | none required for RGB/gray; lcms2 &gt;= 2.8 (optional, meson with-lcms) for CMYK ICC profiles; threads; optional gobject-introspection and vapigen for bindings |
| **Minimum toolchain** | meson &gt;= 0.60; C compiler with C11 atomics (MSVC built with /std:c11 since 0.1.126); gcc/clang on Linux, BSD and macOS |
| **Platforms** | x86-64 (runtime-dispatched v2/v3/v4 builds of SIMD extensions), aarch64 and 32-bit ARM NEON, i686, other little- and big-endian targets (LUTs disabled on big-endian); win32, Linux, BSDs, macOS; initial WASM support since 0.1.128 |
| **Thread safety** | Partly documented. Space creation from ICC is mutex-guarded (babl_space_mutex; 0.1.86 'improved thread safety for babl_space_from_icc', 0.1.78 fixed mutex and atomicity bugs). babl.h says babl_gc() must be called from the main thread with no concurrent babl processing in other threads, which implies processing may otherwise run in parallel. |
| **Drop-in for the baseline** | no |

## Gotchas

- The first use of a new format pair runs a timed path search, and the result is persisted to \~/.cache/babl/babl-fishes keyed on version, BABL_PATH_LENGTH and BABL_TOLERANCE, so first-run and cache-miss latency differ from steady state.
- The 256^3 LUT allocation in babl-fish-path.c (babl_fish_lut_process_maybe) is written to straight after malloc with no NULL check. Set BABL_LUT=0 where a 64-256 MiB allocation can fail.
- The docs give the default BABL_TOLERANCE as 0.000001, but the code uses 0.0000047. babl_fast_fish results are not singletons and leak unless the caller caches them (babl.h).
- LUT handling has had regressions: 0.1.102 disabled LUT code paths by default ('brown paper bag release'), 0.1.104 re-enabled them, 0.1.106 fixed 1bpp-to-4bpp LUTs, and 0.1.114 fixed a broken TRC cache for formula-based ICC TRCs and removed 'some broken conversions'.

## Known shortcomings

- The 'up to 10 times faster than LCMS2 for the cases tested' claim exists only in the GIMP 2.10 release notes (blocked, snippet) with no timings or cases, and the babl tree has no lcms2 harness (tools/babl-benchmark.c is babl-only). The Little CMS project's rebuttal (snippet only) measured lcms2 3.59 s vs babl 6.36 s on 8-bit data, so the claim is disputed. LGPL-3.0-or-later.
- The speed claim stays snippet-only (GIMP 2.10 'up to 10x'; the lcms blog measured lcms2 3.59 s against babl 6.36 s, so babl lost there). CMYK runs through lcms2 itself (double-precision CMYKA_DBL to scRGB with BPC); CLUT RGB profiles are refused unless BABL_ICC_INTENT_PERFORMANCE and the absolute and saturation intents are unimplemented, so any gain is matrix plus TRC only. The default 256^3 u8 LUT (64-256 MiB) is built after 32768 pixels and its malloc result is unchecked in babl-fish-path.c; the documented tolerance 0.000001 differs from the code's 0.0000047. GIMP issue #3764 (30 s sRGB to matrix ICC conversion) unread (gitlab.gnome.org blocked).

## Caveats and trade-offs

Snippet only: the GIMP 2.10 release notes (gimp.org) and littlecms.com are blocked here, and gitlab.gnome.org is blocked as well. Neither the 10x claim nor the rebuttal could be opened, and the release notes do not say which conversions were tested. The babl repository (GitHub mirror) has no benchmark against lcms2; tools/babl-benchmark.c measures babl's own conversion paths only. The only timed comparison found comes from the baseline's own project (Little CMS) and shows babl slower on 8-bit data. babl's ICC support covers matrix+TRC RGB profiles natively, and CMYK goes through lcms2 itself. Keep as a flagged, low-confidence entry.

Converts between pixel formats with runtime-optimised fast paths and caching; needs lcms2 for CMYK profiles (per search snippet); the GitHub page is a read-only mirror.

## Maintenance

Actively maintained in GNOME GitLab (0.1.128 released 2026-08-07; commits since then through 2026-10-03 are build and CI changes, mirrored read-only to GitHub with 25 stars). It is LGPL-3.0-or-later and a core GIMP/GEGL dependency, so it is safe to link dynamically, but the speed claim against lcms2 is unsubstantiated.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The claim lives only in the GIMP 2.10 release notes (gimp.org, blocked here; WebSearch snippet: babl is 'up to 10 times faster than LCMS2 for the cases tested'). That is a first-party ratio with no timings, workloads, machine or code. The babl repository has no lcms2 comparison benchmark: tools/babl-benchmark.c times babl's own conversions only, and NEWS, OldNews and the docs carry no lcms2 speed claim. Snippet-only evidence without methodology caps it at C.
- **Verifier notes:** I found where the claim lives (GIMP 2.10 release notes) via WebSearch, but its measurements are not published anywhere reachable, and babl's own tree has no lcms2 timing harness. A disputed, unpublished claim stays C as a caveat, not a reject. Metadata is confirmed on the GitHub mirror: 25 stars, last commit 2026-10-03. Source headers say LGPL version 3 or any later version.
- **Fields the verifier corrected:** `benchmark_url`, `license`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/GNOME/babl>
  - <https://github.com/GNOME/babl/commits/master>
  - <https://github.com/GNOME/babl/tree/master/tools>
  - <https://github.com/GNOME/babl/tree/master/docs>
  - <https://raw.githubusercontent.com/GNOME/babl/master/NEWS>
  - <https://raw.githubusercontent.com/GNOME/babl/master/tools/babl-benchmark.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/tests/meson.build>
  - <https://raw.githubusercontent.com/GNOME/babl/master/meson_options.txt>
  - <https://raw.githubusercontent.com/GNOME/babl/master/docs/ColorManagement-static.html>
  - <https://raw.githubusercontent.com/GNOME/babl/master/docs/OldNews-static.html>
  - <https://raw.githubusercontent.com/GNOME/babl/master/docs/index-static.html.in>
  - <https://raw.githubusercontent.com/GNOME/babl/master/docs/CMYK-static.html>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl.c>
- **Sources the enricher read:**
  - <https://github.com/GNOME/babl>
  - <https://github.com/GNOME/babl/commits/master>
  - <https://raw.githubusercontent.com/GNOME/babl/master/NEWS>
  - <https://raw.githubusercontent.com/GNOME/babl/master/meson.build>
  - <https://raw.githubusercontent.com/GNOME/babl/master/meson_options.txt>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl.h>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-fish-path.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-fish.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-fish-reference.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-icc.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-space.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-cache.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-cpuaccel.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/babl-internal.h>
  - <https://raw.githubusercontent.com/GNOME/babl/master/babl/base/babl-rgb-converter.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/tools/babl-benchmark.c>
  - <https://raw.githubusercontent.com/GNOME/babl/master/docs/index-static.html.in>
  - <https://raw.githubusercontent.com/GNOME/babl/master/docs/ColorManagement-static.html>
  - WebSearch: babl "faster than LCMS2" GIMP release notes (snippets of https://www.gimp.org/release-notes/gimp-2.10.html and https://gegl.org/babl/)
  - WebSearch: littlecms babl throughput comparative (snippet of https://littlecms.com/blog/2019/10/02/througput-babl/)
  - https://gitlab.gnome.org/GNOME/gimp/-/issues/3764 (blocked: CONNECT 403)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/gnome/babl`) · [data/wave10/enrich/raw/github_com_gnome_babl.json](../../../data/wave10/enrich/raw/github_com_gnome_babl.json) (enrichment confidence 0.75)

</details>
