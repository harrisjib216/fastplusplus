# skcms

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Skia's small ICC colour-management library (parse profiles, SIMD pixel transforms); no published speed comparison against Little CMS.

| | |
|---|---|
| **Beats** | Little CMS (lcms2) |
| **Claimed result** | none: no numeric comparison found |
| **Workload** | No comparison against Little CMS or any other library was found. The repo's bench.c only times skcms_Transform on 255-pixel batches (default sRGB to Display P3, rotating pixel formats) and prints ns per pixel for skcms alone. |
| **Metric** | throughput |
| **Adoption** | 4 stars, 3 forks on the GitHub mirror (read-only mirror of skia.googlesource.com/skcms; latest tag 2025_09_16); used by Skia and Chromium, and an optional colour backend of libjxl (per search snippets and the libjxl enrichment) |
| **Last commit** | 2025-09-16 |
| **Links** | [repository](https://github.com/google/skcms) |

## Verdict

Nothing comparative has been measured: neither README makes a speed claim, and bench.c (mirror branch) only prints skcms's own ns per pixel for 255-pixel batches of sRGB to a Display P3 matrix, which its header calls 'mostly to run in a profiler'. imazen/cms-bench has a zenbench harness timing moxcms, skcms and lcms2 on 8-bit, 16-bit, float and LUT profiles but commits no results; in its identity group skcms gets the same profile pointer twice (no colour math), and only the skcms rows include per-call setup.

## Use it when

- You already build Skia or Chromium-style code and want the same colour conversions they ship, with no new dependency.
- Decoding images (JPEG, PNG, WebP, AVIF, JPEG XL) whose embedded ICC or CICP profile must be converted to sRGB or a display profile, row by row.
- HDR pipelines that need PQ and HLG transfer functions, including the HLG OOTF, plus half-float and 10-bit XR output formats.
- Many pixel formats in one library without writing per-format packing code; 255-pixel or larger batches, so the per-call planning cost is amortised.
- Untrusted ICC input: the repo carries libFuzzer targets (fuzz/fuzz_iccprofile_info.c, fuzz/fuzz_iccprofile_transform.c), and skcms.cc never calls malloc, so parsing does not allocate or copy.

## Skip it when

- You need lcms2 features: rendering intents beyond the A2B0/A2B1 preference, black point compensation, proofing, device links, named colours or multi-profile chains.
- Destination profiles with tabulated TRCs: they must be rewritten by skcms_MakeUsableAsDestination(), which fits a parametric curve and fails or approximates badly on some profiles (tests.c lists several).
- You need bit-exact or lcms2-identical output: transfer functions run through approx_pow, and the repo's own A2B round-trip test tolerates 1/255 error (9/255 at zero).
- You picked it for speed: no benchmark against Little CMS, its fast_float plugin, qcms or moxcms is published, and bench.c only times skcms itself.
- General CMYK workflows: CMYK is handled as Photoshop-style inverted CMYK only (the code says those are the only CMYK profiles it has seen).

## How it is fast

Each skcms_Transform call compiles a short program of at most 32 ops (load, curves, matrix or CLUT, clamp, premul, store) and runs it over float vectors of 4 (SSE/NEON/LSX/WASM), 8 (AVX2+F16C, 'hsw') or 16 (AVX-512, 'skx') lanes, picked by a one-time cpuid/xgetbv check. Stages are chained with [[clang::musttail]] tail calls where the compiler supports it, transfer functions use approximate log2/exp2 (approx_pow) instead of powf, the source and destination gamut matrices are concatenated into one 3x3, an identical gamut skips the matrix, and LUT/CLUT lookups use AVX2/AVX-512 gathers and hardware half-float conversion.

## Compared with alternatives

Pick skcms over the Little-CMS fast_float plugin when you want a small, dependency-free, fuzzed C/C++ library matching Skia and Chromium output and can live without lcms2's intents and device links; pick moxcms instead in Rust code, where it at least publishes timings against lcms2. Keep lcms2 plus fast_float when you need the full ICC feature set or measured speed.

## Integration

| | |
|---|---|
| **Form** | source-drop (skcms.cc plus src/\*.cc and headers); ninja and Bazel builds produce a static library |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | C++ with lambdas and constexpr (C++11 level; the exact standard is not documented); Clang or GCC vector extensions for the SIMD paths, otherwise SKCMS_PORTABLE scalar code (for example MSVC without clang-cl) |
| **Platforms** | x86-64 with runtime dispatch to SSE baseline, AVX2+F16C or AVX-512 (AVX2/AVX-512 paths disabled on Android); aarch64 and armv7 NEON; LoongArch LSX; WebAssembly SIMD via Emscripten; ppc64le and RISC-V without musttail; Windows without musttail |
| **Thread safety** | not documented; from the code, skcms_Transform keeps no shared mutable state apart from a one-time CPU-detection static, so concurrent calls with read-only profiles look safe, and parsed profiles borrow the caller's ICC buffer |
| **Drop-in for the baseline** | no |

## Gotchas

- skcms_Transform has no cached transform object: every call re-plans the pipeline (including inverting the destination transfer functions), so very small calls pay setup each time.
- Passing the same profile pointer as source and destination skips the colour conversion entirely (only format conversion runs); any benchmark against lcms2 that does this is not like for like.
- skcms_ICCProfile points into the ICC buffer passed to skcms_Parse(); the buffer must outlive the profile.
- bench.c times skcms on static float buffers that are never filled (all-zero pixels) and rotates pixel formats each iteration, so its ns-per-pixel figure is a profiling aid, not a throughput number for real images.

## Known shortcomings

- Tier D: bench.c on the GitHub mirror times skcms alone, there is no lcms2 number anywhere reachable, imazen/cms-bench commits no results, and the mirror's last commit is 2025-09-16 with the upstream (skia.googlesource.com) unverifiable here.
- Enricher (e107, 2026-10-05): stays D, no catalogued numbers. bench.c times all-zero static buffers and rotates formats; skcms_Transform has no transform object and re-plans every call; passing the same source and destination profile pointer skips the colour math, which is exactly what the imazen/cms-bench identity group does (only the skcms rows include setup; no results committed). GitHub mirror last synced 2025-09-16.

## Caveats and trade-offs

No numeric comparison against Little CMS was found. The main-branch README only describes the mirror; the mirror-branch README covers building only. bench.c (raw.githubusercontent.com/google/skcms/mirror/bench.c; it is absent from main) times skcms alone (default sRGB to Display P3, -n 100000 iterations) and prints no lcms2 figure. imazen/cms-bench has a harness comparing moxcms, lcms2, skcms and ArgyllCMS but commits no results. skia.googlesource.com and the Chromium review thread 'Enable skcms in Skia' (groups.google.com) are blocked here, so a speed claim there could not be checked. Little CMS fast_float is already on the list. The mirror's last commit is 2025-09-16 ('Disable must_tail on GCC when compiling for RISC-V'), 12.6 months before 2026-10-04, so it reads as stale by the 12-month rule. Upstream on skia.googlesource.com may be newer if the mirror sync stopped; this could not be checked.

Read-only mirror of skia.googlesource.com/skcms. The default branch main holds only README, LICENSE, CONTRIBUTING and workflows; sources (skcms.cc, bench.c, tests.c, profiles, fuzz, bazel and ninja builds) are on the mirror branch. Library does ICC profile parsing and pixel transforms (SIMD paths incl. loong64 LSX), not a full colour-management stack; Bazel and ninja builds.

## Maintenance

The GitHub repo is a read-only mirror whose last sync is 2025-09-16 ('Disable must_tail on GCC when compiling for RISC-V'), so it reads as stale even though upstream on skia.googlesource.com is likely still used by Skia and Chromium; BSD-3-Clause and small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No numbers against Little CMS or any other library. bench.c (on the mirror branch) times skcms_Transform alone on 255-pixel batches and says it is 'mostly to run in a profiler'. The READMEs on both branches make no speed claim, and one WebSearch query found nothing numeric.
- **Verifier notes:** Stays D, confirmed. Notable as Skia and Chromium's colour-management library despite 4 mirror stars, so keep. Maintenance is judged from the mirror only.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** none
- **Pages the verifier opened:**
  - <https://github.com/google/skcms>
  - <https://github.com/google/skcms/commits/mirror>
  - <https://github.com/google/skcms/tags>
  - <https://raw.githubusercontent.com/google/skcms/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/skcms/mirror/README.md>
  - <https://raw.githubusercontent.com/google/skcms/mirror/bench.c>
  - <https://raw.githubusercontent.com/google/skcms/mirror/LICENSE>
  - <https://raw.githubusercontent.com/google/skcms/mirror/BUILD.bazel>
  - <https://github.com/imazen/cms-bench>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/google/skcms/mirror/README.md>
  - <https://raw.githubusercontent.com/google/skcms/mirror/bench.c>
  - <https://raw.githubusercontent.com/google/skcms/mirror/skcms.h>
  - <https://raw.githubusercontent.com/google/skcms/mirror/skcms.cc>
  - <https://raw.githubusercontent.com/google/skcms/mirror/BUILD.bazel>
  - <https://raw.githubusercontent.com/google/skcms/mirror/BAZEL.md>
  - <https://raw.githubusercontent.com/google/skcms/mirror/build.ninja>
  - <https://raw.githubusercontent.com/google/skcms/mirror/LICENSE>
  - <https://raw.githubusercontent.com/google/skcms/mirror/tests.c>
  - <https://raw.githubusercontent.com/google/skcms/mirror/src/skcms_public.h>
  - <https://raw.githubusercontent.com/google/skcms/mirror/src/skcms_internals.h>
  - <https://raw.githubusercontent.com/google/skcms/mirror/src/skcms_Transform.h>
  - <https://raw.githubusercontent.com/google/skcms/mirror/src/Transform_inl.h>
  - <https://raw.githubusercontent.com/google/skcms/mirror/src/skcms_TransformBaseline.cc>
  - <https://raw.githubusercontent.com/google/skcms/mirror/src/skcms_TransformHsw.cc>
  - <https://raw.githubusercontent.com/google/skcms/mirror/src/skcms_TransformSkx.cc>
  - <https://github.com/google/skcms/commits/mirror>
  - <https://github.com/imazen/cms-bench>
  - <https://github.com/imazen/cms-bench/tree/main/benches>
  - <https://raw.githubusercontent.com/imazen/cms-bench/main/benches/transform.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/README.md>
  - <https://github.com/yfedoseev/pdf_oxide/issues/749>
  - <https://raw.githubusercontent.com/google/skcms/mirror/fuzz/fuzz_iccprofile_transform.c>
  - <https://raw.githubusercontent.com/google/skcms/mirror/fuzz/fuzz_iccprofile_info.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/google/skcms`) · [data/wave10/enrich/raw/github_com_google_skcms.json](../../../data/wave10/enrich/raw/github_com_google_skcms.json) (enrichment confidence 0.6)

</details>
