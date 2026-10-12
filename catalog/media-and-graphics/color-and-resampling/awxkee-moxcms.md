# moxcms

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause OR Apache-2.0` · 🟢 active

> Pure-Rust ICC colour-management crate; the author's README showed 8-bit transforms 3.7-7.4x faster than stock Little CMS 2.

| | |
|---|---|
| **Beats** | Little CMS 2 (lcms2); also qcms |
| **Claimed result** | moxcms 0.7.4 README (NEON / AVX2): RGB to RGB 2.68 / 4.52 ms vs lcms2 13.1 / 27.73 ms vs qcms 6.47 / 4.59 ms; LUT RGB to RGB 6.03 / 12.43 ms vs lcms2 27.60 / 58.26 ms vs qcms 26.72 / 60.80 ms; RGBA to RGBA 2.96 / 4.83 ms vs lcms2 21.97 / 35.70 ms vs qcms 6.83 / 4.99 ms; CMYK to RGBA 9.74 / 21.65 ms vs lcms2 39.71 / 79.40 ms vs qcms 25.97 / 61.54 ms. Against lcms2 that is 3.7x to 7.4x (derived from page data). The last README table before removal (commit 178e732, Sep 2025) shows slower moxcms LUT 7.18 / 17.50 ms and CMYK 11.86 / 27.98 ms, i.e. 2.8x to 3.8x on those rows (derived from page data). On AVX2 the matrix-shaper rows are at parity with qcms. |
| **Workload** | ICC profile colour transform of a 1997x1331 image with 8-bit samples: RGB to RGB, LUT-based RGB to RGB, RGBA to RGBA and CMYK to RGBA. |
| **Metric** | throughput |
| **Hardware** | Not stated beyond 'NEON' and 'AVX2' columns. |
| **Compiler and flags** | Not stated. |
| **Adoption** | 52 stars; 89.5M crates.io downloads (max version 0.9.1); 46 reverse dependencies including the image crate, jxl-oxide and typst-library |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/awxkee/moxcms) · [benchmark](https://crates.io/api/v1/crates/moxcms/0.7.4/readme) |

## Verdict

The moxcms 0.7.4 README (Aug 2025) times 8-bit transforms of a 1997x1331 JPEG with Criterion against the lcms2 6.1 crate and qcms 0.3, in unnamed NEON and AVX2 columns with no CPU, rustc version or flags. For example, RGB to RGB took 2.68/4.52 ms against lcms2's 13.1/27.73 ms, about 3.7-7.4x across rows (derived from page data). The lcms2 side is stock: lcms2-sys either links the system library or builds only the core src/\*.c files, and the bench registers no fast_float plugin. Precision is roughly comparable on matrix-shaper rows (moxcms Q2.13 fixed point vs lcms2's 1.14 fixed-point MatShaper8 path), and both use Perceptual intent. The rows still do not do the same work: moxcms converts to its built-in sRGB while lcms2/qcms convert to assets/bt_2020.icc, the lcms2 CMYK row is fed the RGBA buffer, the qcms 'CMYK' row is built with DataType::RGBA8 (which in qcms 0.3 builds a 33^3 RGB CLUT, not the 4D CMYK path), and the LUT variant behind each moxcms LUT/CMYK row is not stated. The table is not reproducible from the repo: the lcms2/qcms rows were never re-measured after Mar 2025, and the app/Cargo.toml checked in with the last table (commit 178e732) enables no moxcms features, so SIMD is off and the options-gated LUT bench cannot compile.

## Use it when

- Rust image pipelines that convert embedded ICC profiles to sRGB. The image crate, jxl-oxide and typst already depend on it (about 89.7M crates.io downloads).
- Bulk 8-bit RGB/RGBA conversion on x86-64 with AVX2 or aarch64 with NEON, where stock lcms2 is the current cost.
- CMYK JPEG/TIFF to RGB(A) in Rust without linking C.
- Parsing untrusted ICC data in a memory-safe language: unsafe code is confined to SIMD paths, the crate forbids unsafe when all SIMD features are off, and a fuzz target ships in the repo.

## Skip it when

- C or C++ projects without a Rust toolchain: there is no C API, so stock lcms2 with its fast_float plugin is the in-language option.
- Pipelines that need bit-identical output across platforms. Issue #192 (Sep 2026) reports x86-64 vs aarch64 differences on about 1.7 % of pixels (up to 3/255) on the fixed-point path and about 91 % (1/255) on the float path, traced to per-architecture SIMD and FMA.
- Work that needs a user-facing black-point-compensation flag (commented out in TransformOptions) or other lcms2 features such as proofing or device links, which the README does not document.
- Precision-critical 8-bit conversions under default options (trilinear, low barycentric weights, fixed point). Issue #162 reported up to 12/255 divergence from the float/tetrahedral/high-weight path before PR #181 (May 2026), and the tetrahedral/pyramid/prism and High-weight choices need the non-default options feature.
- Deciding against an already-tuned lcms2: the published comparison used stock lcms2 without the fast_float plugin, so the gap to a tuned lcms2 is unmeasured.

## How it is fast

When both profiles are matrix/TRC (matrix-shaper) profiles, the transform becomes 256-entry linearisation tables, a 3x3 matrix in Q2.13 fixed point and a 4096-entry output gamma table, run with SSE4.1, AVX2, NEON or opt-in AVX-512 intrinsics. Stock lcms2's equivalent 8-bit path (MatShaperEval16 in cmsopt.c, 1.14 fixed point) is scalar C. LUT-based and CMYK profiles are pre-sampled into a 3D/4D grid and evaluated with trilinear (the default), tetrahedral, pyramid or prism interpolation, in Q0.15 fixed point or float, with SIMD variants. So most of the gain is SIMD over a precomputed pipeline at similar fixed-point precision, not a different colour model.

## Compared with alternatives

Pick moxcms over the Little-CMS fast_float plugin when the code base is Rust and memory-safe profile parsing matters. Stay with lcms2 plus fast_float in C/C++, or when you need lcms2's wider feature set. jsColorEngine fills the same role only for JavaScript/WASM, and babl is GIMP's pixel-format engine rather than a general ICC transform library.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits, pxfm |
| **Minimum toolchain** | Rust 1.89 for 0.9.x (1.85 for 0.8.x); the opt-in sve feature on aarch64 needs nightly (feature(stdarch_aarch64_sve)) |
| **Platforms** | any Rust target; SIMD paths for x86-64 (SSE4.1 and AVX2 by default, AVX-512 opt-in) and aarch64 (NEON by default, SVE opt-in), scalar elsewhere |
| **Thread safety** | Transform executors are returned as Arc&lt;dyn TransformExecutor + Send + Sync&gt;, so one transform can be shared across threads |
| **Drop-in for the baseline** | no |

## Gotchas

- SIMD and the faster matrix-shaper variants are separate cargo features. The default set omits avx512, the \*_shaper_optimized_paths features, options and in_place, all of which the benchmark app enables, so a default build (for example through the image crate) may not run the code paths that were timed.
- allow_use_cicp_transfer defaults to true. Issue #155 reported wrong PQ/HLG output with that default and #154 reported setters not clearing CICP (both closed Feb 2026), so check HDR profiles against a reference.
- CMYK output had a real colour error: issue #144 (Dec 2025) found green 2-8/255 low on the pure-yellow axis of US Web Coated SWOP against lcms2 and skcms, fixed in PR #147 ('Remove invalid gamut clipping', 2025-12-29). That is after the 0.7.4 README numbers.
- Issue #122 (Dec 2025) flagged unsound safe wrappers around get_unchecked in the SIMD interpolation code; keep up with releases if you feed untrusted LUT profiles.

## Known shortcomings

- Rust (language-filter mismatch). 0.7.4 table matches public bench code (app/benches/icc, lut) with no CPU, rustc version or flags; same Perceptual intent and 8-bit on both sides, moxcms in Q2.13 fixed point. Destinations differ (moxcms to built-in sRGB, lcms2 and qcms to bt_2020.icc) and the lcms2 CMYK row was fed the RGBA buffer instead of CMYK data. lcms2 rows were never re-measured after March 2025; the last table before their removal (April 2026) showed moxcms slower, 2.8-3.8x, on LUT and CMYK. Lead: imazen/cms-bench harness, no published results.
- The Little-CMS side is stock lcms2 (lcms2-sys builds the core sources or links the system library; no fast_float plugin, no cmsPlugin call), both sides Perceptual; matrix-shaper precision is comparable (moxcms Q2.13 versus lcms2 MatShaper8 1.14 fixed point) but destinations differ (built-in sRGB versus bt_2020.icc). The qcms 'CMYK' row is built with DataType::RGBA8, so qcms times a 33^3 RGB CLUT, not CMYK. app/Cargo.toml at 178e732 (the last table) enables no moxcms features, so SIMD is off and the options-gated LUT bench cannot compile: the table is not reproducible. Colour bugs after the 0.7.4 numbers: CMYK yellow axis up to 8/255 (#144, fixed PR #147, 2025-12-29), default path up to 12/255 off versus float tetrahedral (#162, fixed PR #181), x86-64 and aarch64 outputs differ (#192 open).

## Caveats and trade-offs

First-party numbers: benchmark code is public (app/benches/icc/main.rs and app/benches/lut/main.rs, Criterion, lcms2 crate 6.1 and qcms 0.3 in app/Cargo.toml) but no CPU model, rustc version or flags are stated. The README table ran from Mar 2025 until commit d9c883a (Apr 2026) removed it; the lcms2 and qcms rows never changed from the Mar 30 2025 run (6ed1459) while moxcms rows were re-measured, and the 0.7.4 figures are faster than the last published ones (Sep 2025: LUT 7.18 / 17.50 ms, CMYK 11.86 / 27.98 ms). Transforms are not identical in the current bench code: moxcms RGB and LUT rows convert to its built-in sRGB profile while lcms2 and qcms convert to assets/bt_2020.icc; the lcms2 CMYK row is fed the RGBA image buffer instead of the CMYK buffer moxcms gets. Intent matches (Perceptual for lcms2; moxcms default RenderingIntent is Perceptual), both are 8-bit in and out, but moxcms matrix-shaper rows use its default fixed-point path (Q2.13 per src/transform.rs; LUT rows Q0.15 or float depending on the variant), and the bench installs no lcms2 fast-float plugin. Which bench variant (tetrahedral/pyramid/prism/linear, fixed or float) each README LUT row reports is not stated. An imazen/cms-bench harness (moxcms 0.8.1 vs lcms2 vs skcms vs ArgyllCMS, zenbench, LTO) exists but publishes no results.

Rust crate (no C or C++ API seen in the README); pure Rust, no unsafe C dependency; supports CMYK, LAB, GRAY and display-class profiles.

## Maintenance

Very active (0.9.1 on 2026-09-15, last commit 2026-09-29, one open issue) and dual BSD-3-Clause/Apache-2.0. Most of its 89.7M downloads come through the image crate. The README benchmark table was removed in Apr 2026, so the project currently publishes no speed numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The 0.7.4 crates.io README table matches the record exactly, and public Criterion benchmark code exists (app/benches/icc/main.rs, app/benches/lut/main.rs), but no CPU model, rustc version or flags are given beyond 'NEON'/'AVX2' columns, and the numbers are first-party: C.
- **Verifier notes:** Real and widely depended-on (via the image crate); license, last commit 2026-09-29 and active status confirmed. Language is correct as 'Rust' (pure Rust, no C ABI). imazen/cms-bench (Apr 2026) is a lead for an independent rerun if anyone publishes its output.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://crates.io/api/v1/crates/moxcms/0.7.4/readme>
  - <https://static.crates.io/readmes/moxcms/moxcms-0.7.4.html>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/README.md>
  - <https://github.com/awxkee/moxcms>
  - <https://github.com/awxkee/moxcms/commits>
  - <https://github.com/awxkee/moxcms/tree/master/app>
  - <https://github.com/awxkee/moxcms/tree/master/app/benches>
  - <https://raw.githubusercontent.com/awxkee/moxcms/master/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/master/app/benches/icc/main.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/master/app/benches/lut/main.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/master/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/master/src/transform.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/master/src/lib.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/master/src/profile.rs>
  - <https://github.com/awxkee/moxcms/commits/master/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/6ed1459/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/c893439/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/a5ef0d6/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/97c7fd1/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/178e732/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/d9c883a/README.md>
  - <https://crates.io/api/v1/crates/moxcms>
  - <https://crates.io/api/v1/crates/moxcms/versions?per_page=100>
  - <https://crates.io/api/v1/crates/moxcms/reverse_dependencies?per_page=10>
  - <https://github.com/imazen/cms-bench>
  - <https://github.com/imazen/cms-bench/tree/main>
  - <https://github.com/imazen/cms-bench/commits/main>
  - <https://raw.githubusercontent.com/imazen/cms-bench/main/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/cms-bench/main/Dockerfile>
  - <https://raw.githubusercontent.com/imazen/cms-bench/main/benches/transform.rs>
- **Sources the enricher read:**
  - <https://github.com/awxkee/moxcms>
  - <https://github.com/awxkee/moxcms/tree/master/src>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/app/benches/icc/main.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/app/benches/lut/main.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/src/transform.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/HEAD/src/profile.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/178e732/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/178e732/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/178e732/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/178e732/app/benches/icc/main.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/178e732/app/benches/lut/main.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/178e732/src/transform.rs>
  - <https://raw.githubusercontent.com/awxkee/moxcms/6ed1459/README.md>
  - <https://raw.githubusercontent.com/awxkee/moxcms/6ed1459/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/6ed1459/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/moxcms/6ed1459/app/benches/icc/main.rs>
  - <https://crates.io/api/v1/crates/moxcms/0.7.4/readme>
  - <https://static.crates.io/readmes/moxcms/moxcms-0.7.4.html>
  - <https://crates.io/api/v1/crates/moxcms>
  - <https://crates.io/api/v1/crates/moxcms/versions?per_page=100>
  - <https://crates.io/api/v1/crates/lcms2>
  - <https://crates.io/api/v1/crates/lcms2-sys>
  - <https://raw.githubusercontent.com/kornelski/rust-lcms2-sys/HEAD/src/build.rs>
  - <https://raw.githubusercontent.com/kornelski/rust-lcms2-sys/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/kornelski/rust-lcms2/HEAD/src/transform.rs>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/src/cmsopt.c>
  - <https://raw.githubusercontent.com/mm2/Little-CMS/master/src/cmspcs.c>
  - <https://raw.githubusercontent.com/FirefoxGraphics/qcms/HEAD/src/transform.rs>
  - <https://raw.githubusercontent.com/FirefoxGraphics/qcms/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/FirefoxGraphics/qcms/HEAD/Cargo.toml>
  - <https://github.com/awxkee/moxcms/issues?q=is%3Aissue>
  - <https://github.com/awxkee/moxcms/issues/122>
  - <https://github.com/awxkee/moxcms/issues/144>
  - <https://github.com/awxkee/moxcms/issues/162>
  - <https://github.com/awxkee/moxcms/issues/192>
  - <https://github.com/awxkee/moxcms/pull/147>
  - <https://github.com/awxkee/moxcms/pull/181>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/awxkee/moxcms`) · [data/wave10/enrich/raw/github_com_awxkee_moxcms.json](../../../data/wave10/enrich/raw/github_com_awxkee_moxcms.json) (enrichment confidence 0.7)

</details>
