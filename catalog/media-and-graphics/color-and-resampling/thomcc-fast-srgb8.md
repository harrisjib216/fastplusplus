# fast-srgb8

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0, MIT, CC0-1.0` · 🔴 abandoned

> Tiny no_std Rust crate: table-based linear-f32 to sRGB-u8 and back, several times faster than per-call powf.

| | |
|---|---|
| **Beats** | naive powf-based sRGB transfer function (reference implementation inside the crate's own benchmark) |
| **Claimed result** | README bench output, one iteration = 51 conversions (204 for the x4 pair, 256 for sRGB8 to f32): f32 to sRGB8 scalar 144 ns/iter vs 971 ns for the naive powf reference (about 6.7x, derived from page data); f32x4 SSE2 440 ns vs 3,625 ns for four naive calls (about 8.2x, derived from page data), but only about 1.1x over four scalar fast calls (482 ns, derived from page data); sRGB8 to f32 lookup table 81 ns vs 4,026 ns (about 50x, derived from page data). The README prose says '\~5x' and '\~20x'. |
| **Workload** | Convert linear f32 to 8-bit sRGB (scalar and four-wide SSE2) and 8-bit sRGB to f32, measured with Rust bench harness in ns per iteration. |
| **Metric** | throughput |
| **Compiler and flags** | Rust nightly libtest #[bench] (needs --cfg unstable_bench); rustc version, optimization flags and target CPU not stated |
| **Adoption** | 23 stars; crates.io 18.3M downloads (10.5M recent) as of 2026-10-04 |
| **Last commit** | 2021-05-09 |
| **Links** | [repository](https://github.com/thomcc/fast-srgb8) · [benchmark](https://github.com/thomcc/fast-srgb8) |

## Verdict

The README shows the crate's own nightly libtest #[bench] output: 51 linear-to-sRGB conversions in 144 ns versus 971 ns for a naive powf reference written in the same file (about 6.7x), 51 four-wide conversions in 440 ns versus 3,625 ns for four naive calls (about 8.2x) and 482 ns for four scalar fast calls, and 256 sRGB-to-linear lookups in 81 ns versus 4,026 ns (about 50x), all derived from page data. No CPU, rustc version or flags are given, and the baseline is a straw-man reference, not an incumbent library; the README prose itself claims only about 5x and 20x.

## Use it when

- Rust code (including no_std, embedded or WASM) that converts individual colour components or small batches between linear float and 8-bit sRGB, e.g. writing a linear-light framebuffer to RGBA8.
- Replacing per-pixel powf calls in a hand-written loop: the crate's own benchmark shows about 6.7x for f32 to u8 and about 50x for u8 to f32 against a powf reference (derived from page data).
- Graphics output where the D3D11 FLOAT-to-SRGB rule (error under 0.6 on the integer side, monotonic, round-trips with the inverse) is the accuracy you need.
- Building colour constants at compile time: srgb8_to_f32 is a const fn.

## Skip it when

- C or C++ projects: there is no C API, and stb_image_resize2.h already contains the identical 104-entry table (fp32_to_srgb8_tab4, stbir__linear_to_srgb_uchar) plus a 256-entry inverse table, with SIMD paths in stb itself.
- When output must match a correctly rounded powf result bit for bit: f32_to_srgb8 is approximate (max error 0.544 against the exact value), so some inputs round to a neighbouring u8 compared with the reference; the source comment itself flags this for scientific or medical imaging.
- Bulk image conversion on aarch64 or other non-x86 targets: f32x4_to_srgb8 falls back to four scalar calls (no NEON), and even on x86 the SSE2 path is only about 1.1x faster than four scalar calls (440 vs 482 ns/iter, derived from page data).
- Anything beyond 8-bit sRGB: no 16-bit, no other transfer functions (gamma 2.2, PQ, HLG), no colour-space conversion; a request for general gamma routines (issue #1, 2022) and a portable-SIMD port (issue #3, 2024) are open without response.
- Projects that need an active maintainer: last commit 2021-05-09, version 1.0.0, and the Debian i386 test failure (issue #2, 2023) has no reply.

## How it is fast

Linear to sRGB uses Fabien Giesen's (ryg) public-domain trick: clamp the float to [2^-13, 1-eps], use its exponent and top mantissa bits as an index into a 104-entry u32 table of packed (bias, scale) pairs, and linearly interpolate with the next 8 mantissa bits in integer arithmetic, so no powf, no division and no libm. The SSE2 version does the clamp, shifts and the multiply-add (_mm_madd_epi16) four-wide, but the four table loads stay scalar because SSE2 has no gather. sRGB to linear is a plain 256-entry f32 lookup table.

## Compared with alternatives

None of the catalogued siblings (fast_image_resize, stb-image-resize-opt, tir, colortwist, yuv2rgb, ImageSharp) exposes a standalone sRGB transfer function; pick fast-srgb8 in Rust when you only need the per-component conversion without a resize library. In C or C++, take the same routine from stb_image_resize2.h (or the stb-image-resize-opt fork) instead.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (no libm either) |
| **Minimum toolchain** | Rust 1.46 (MSRV badge; CI matrix includes 1.46.0); benchmarks need nightly with --cfg unstable_bench |
| **Platforms** | any Rust target (no_std); SSE2 four-wide path on x86/x86_64 selected at compile time when target_feature sse2 is enabled, scalar elsewhere and under Miri |
| **Thread safety** | Pure functions over constant tables; no shared mutable state (not documented explicitly) |
| **Drop-in for the baseline** | partial — same signature shape as a hand-written powf transfer function, but f32_to_srgb8 is not bitwise identical to the rounded powf reference, NaN maps to 0 and out-of-range input is clamped |

## Gotchas

- The crate's srgb8_to_f32 table equals the x86-64 powf reference for all 256 inputs, but on Debian i386 (i686, Rust 1.66) test_from_srgb8 fails because the runtime powf reference there differs in the last digit for several entries (issue #2); the shipped table is constant, so outputs do not change, but the 'exact' claim is relative to one platform's powf.
- The README benchmark loops use compile-time loop counters as inputs and include an int-to-float conversion and a division in both arms, on an unstated CPU and rustc; treat the ratios as hot-L1 best cases for 51 or 256 values per iteration, not image-pipeline throughput.
- The SIMD dispatch is compile-time only: an x86 build without target_feature sse2 (for example i586 targets) silently uses the scalar path; there is no runtime CPU detection and no AVX2 or gather path.
- The table index relies on get_unchecked (unsafe) after clamping; the bounds argument is documented in the source and the exhaustive all-2^32-input tests (run in CI on stable in release mode) check error bound, monotonicity and SIMD-equals-scalar.

## Known shortcomings

- The baseline is the crate's own naive powf transfer function, not an incumbent; the 104-entry table is byte-identical to stb_image_resize2.h's fp32_to_srgb8_tab4, so the incumbent stb already ships the same trick. f32_to_srgb8 is not bitwise exact to the rounded reference (max error 0.544, within the D3D 0.6 bound); srgb8_to_f32 is exact for all 256 inputs.
- The 104-entry table is confirmed identical to stb_image_resize2.h's fp32_to_srgb8_tab4 (104 of 104) and stb also ships a SIMD path, so the incumbent already carries the trick; the bench inputs are loop constants with a division in both arms (hot-L1 best case, no CPU or rustc stated); the SSE2 x4 path is only 1.1x over scalar and there is no NEON. Issue #2 (test_from_srgb8 fails on Debian i386 with Rust 1.66; table and runtime powf differ in the last digit) has no maintainer reply; downloads came mostly through palette 0.7.6, and palette 0.7.7 dropped the dependency.

## Caveats and trade-offs

The baseline is a naive per-call powf reference written inside the crate's own bench module, not an incumbent library. f32_to_srgb8 is ryg's public-domain table-plus-lerp routine, and its 104-entry table is byte-identical to fp32_to_srgb8_tab4 in stb_image_resize2.h (stbir__linear_to_srgb_uchar), so the category incumbent already uses this exact technique and the crate gives no speedup over stb's own sRGB path. The output is not bitwise equal to the rounded powf reference for every input: the max error is 0.544 against the exact value (the D3D bound is 0.6), and the exhaustive test checks that error bound, monotonicity, SIMD equal to scalar, and round-tripping, not equality with the rounded reference. srgb8_to_f32 matches the powf reference exactly for all 256 inputs. The README prose ratios (\~5x, \~20x) are smaller than the ratios the bench numbers imply. No CPU, compiler or flags are stated. Last commit 2021-05-09. Not compared against ImageMagick, lcms or stb. If the CC0-1.0 option is chosen there is no patent grant; Apache-2.0 and MIT are also offered.

Table-driven conversion, no_std, no libm needed; 8-bit sRGB endpoints only (not a general color-management library). The repo lists three licenses (Apache-2.0, MIT, CC0-1.0); the CC0 option carries no patent grant.

## Maintenance

Unmaintained since 2021-05-09 (v1.0.0) but tiny, dependency-free and available under CC0-1.0, MIT or Apache-2.0, so it is easy to vendor; its 18.3M crates.io downloads came largely through palette 0.7.6, which depended on it, while palette 0.7.7 replaced it with its own palette_math crate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows the ns/iter output of the crate's own libtest #[bench] functions (src/lib.rs, tests::bench). Those benchmarks compare the crate only against a naive powf reference written in the same file, and no rustc version, flags or CPU is given. That makes the evidence first-party with partial methodology, so tier C.
- **Verifier notes:** Kept at C. The baseline sits inside the same repo and is not an incumbent. The lookup is approximate (within 0.6 ULP), not exact to the rounded reference. stb_image_resize2.h contains the same ryg table (checked byte for byte), so this is a separate Rust port of a routine the stb incumbent already ships, not a port of stb itself. The orchestrator may prefer a duplicate or reference note against nothings/stb.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/README.md>
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/Cargo.toml>
  - <https://github.com/thomcc/fast-srgb8>
  - <https://github.com/thomcc/fast-srgb8/commits>
  - <https://crates.io/api/v1/crates/fast-srgb8>
  - <https://raw.githubusercontent.com/nothings/stb/HEAD/stb_image_resize2.h>
- **Sources the enricher read:**
  - <https://github.com/thomcc/fast-srgb8>
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/README.md>
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/src/sse2.rs>
  - <https://raw.githubusercontent.com/thomcc/fast-srgb8/HEAD/.github/workflows/ci.yml>
  - <https://github.com/thomcc/fast-srgb8/issues?q=is%3Aissue>
  - <https://github.com/thomcc/fast-srgb8/issues/2>
  - <https://github.com/thomcc/fast-srgb8/pulls?q=is%3Apr>
  - <https://crates.io/api/v1/crates/fast-srgb8>
  - <https://crates.io/api/v1/crates/fast-srgb8/reverse_dependencies?per_page=30>
  - <https://crates.io/api/v1/crates/palette>
  - <https://crates.io/api/v1/crates/palette/0.7.6/dependencies>
  - <https://crates.io/api/v1/crates/palette/0.7.7/dependencies>
  - <https://crates.io/api/v1/crates/palette_math/0.7.7/dependencies>
  - <https://raw.githubusercontent.com/Ogeon/palette/master/palette/Cargo.toml>
  - <https://raw.githubusercontent.com/Ogeon/palette/master/palette_math/Cargo.toml>
  - <https://raw.githubusercontent.com/Ogeon/palette/master/palette_math/src/lib.rs>
  - <https://raw.githubusercontent.com/Ogeon/palette/master/palette_math/src/lut.rs>
  - <https://raw.githubusercontent.com/Ogeon/palette/master/palette_math/src/gamma.rs>
  - <https://raw.githubusercontent.com/nothings/stb/HEAD/stb_image_resize2.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/thomcc/fast-srgb8`) · [data/wave10/enrich/raw/github_com_thomcc_fast_srgb8.json](../../../data/wave10/enrich/raw/github_com_thomcc_fast_srgb8.json) (enrichment confidence 0.85)

</details>
