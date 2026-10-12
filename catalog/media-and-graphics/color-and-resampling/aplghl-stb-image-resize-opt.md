# stb-image-resize-opt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT OR Unlicense` · 🟢 active

> Unchanged stb_image_resize2 v2.18 shipped as a static library with runtime AVX2 dispatch; about 1.36x faster than stock -O2 builds.

| | |
|---|---|
| **Beats** | stb_image_resize2.h v2.18 (nothings/stb commit 904aa67, 2026-03-13; the vendored upstream/ copy's sha256 173e654634f6ccaad98f603e686ea212eec1fe8ea6d2a5e5e8056efa10ae3880 matches nothings/stb master), compiled -O2 -ffp-contract=off for the default x86-64 (SSE2) target |
| **Claimed result** | results/summary.csv (upstream at -O2/SSE2 vs the fork's runtime-dispatched library at -O3 with held-out PGO, 23 rows, min ns over repeats): geomean 1.3623x (upsample 1.3495x, downsample 1.3842x); per row 1.09-1.66x: uint8 1.29-1.60x, uint16 1.52-1.66x, float 1.12-1.42x, uint8 RGBA 1.32-1.35x, RGBA_PM 1.44-1.57x, sRGB 1.12-1.22x, half 1.09-1.11x. results/kernels.csv (the same library forced to its base vs AVX2 path): geomean 1.3491x over the non-half rows, half 1.00x. results/consumer.csv (load, resize, sRGB RGBA program vs stock -O2): geomean 1.230x (1.11-1.57x). The README's +32.8% without PGO has no committed CSV. The fork's own docs/MEASUREMENT.md says upstream compiled with -O3 -march=x86-64-v3 is byte-exact and +26-34% faster by itself, so these gains are upstream's AVX2 code path enabled at runtime, not a faster resampler. |
| **Workload** | bench/bench.c matrix of 23 rows (256x256 and 1024x1024 inputs; up, down and same-size; uint8/uint16/float/half/sRGB; 1ch/RGB/4ch/RGBA/RGBA_PM; default and point-sample filters; clamp edge), min ns per stbir_resize_extended call over repeats; plus an isolated base-vs-AVX2 kernel run (harness/kernbench.sh) and a downstream load-resize-sRGB consumer (harness/consumer/run.sh). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-14700F (Raptor Lake, hybrid P/E cores), WSL2 Ubuntu 24.04 |
| **Compiler and flags** | clang 23.1.2 (hermetic LLVM toolchain via scripts/env.sh). Baseline: upstream header with bench/bench.c at -O2 -ffp-contract=off and no -march (harness/bench_vs_upstream.sh). Fork: scripts/build_opt.sh exact compiles the unchanged header twice, lib/resize_base.c at -O3 -march=x86-64-v2 -ffp-contract=off and lib/resize_avx2.c at -O3 -march=x86-64-v3 -ffp-contract=off, adds a CPUID/XGETBV dispatch layer and uses held-out PGO (PGO=1; tools/train.c trains on rows distinct from the bench rows); the bench driver is built at -O3 -march=x86-64-v2; runs are pinned with taskset -c 3. |
| **Adoption** | 0 stars, 0 forks; created 2026-09-29 with 5 commits, no GitHub release (CHANGELOG lists v1.0.0) |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/aplghl/stb-image-resize-opt) · [benchmark](https://github.com/aplghl/stb-image-resize-opt) |

## Verdict

The test pits stock stb_image_resize2 v2.18 (sha256-identical to nothings/stb master), compiled at -O2 for SSE2, against the fork's library: -O3 with an x86-64-v2 base variant, an x86-64-v3 AVX2 variant and held-out PGO, built with clang 23.1.2 and run on an i7-14700F under WSL2. Both sides run the same bench/bench.c driver over 23 rows with the same calls, filter, edge mode, datatype and layout, timing the min ns per stbir_resize_extended call. The fork comes out 1.36x geomean faster (1.09-1.66x per row), and an isolated base-versus-AVX2 run on the same library gives 1.35x. The benchmark itself does not compare outputs. Byte-identity comes from the separate harness/diff_lib.sh matrix, which passes in CI but uses outputs of at most 200x150 and about 3.7x downsampling, so the benchmark's 16x (1024 to 64) and 2048x2048 cases are not covered.

## Use it when

- You ship one portable x86-64 binary (distribution package, game, tool) that resizes with stb_image_resize2, and you cannot compile with -march=x86-64-v3, but want upstream's AVX2 speed on Haswell-or-newer CPUs.
- uint8, uint16 and premultiplied RGBA resizes, where the committed results show 1.29-1.66x over stock -O2; the 1024x1024 to 64x64 thumbnail row reached 1.60x.
- You need output byte-identical to upstream SSE2 (golden-image tests, reproducible pipelines), since the exact build is differential-tested against the pristine header on base, AVX2 and auto dispatch.
- You already use stb_image_resize2 and want a link-time swap with no source changes.

## Skip it when

- Your build can already target x86-64-v3 (or -march=native): the fork's own docs/MEASUREMENT.md says stock upstream at -O3 -march=x86-64-v3 is byte-exact and 26-34% faster by itself, so the fork adds only runtime dispatch.
- Header-only use: the README's option 2 gives only the baseline variant, which measured within about 5% of stock -O2 on most rows. Half-float output and sRGB rows gain little (1.09-1.11x and 1.12-1.22x).
- Non-x86 targets: aarch64 and others get a single baseline build (upstream NEON or scalar) with no speedup.
- MSVC cl.exe builds of the library: lib/resize_dispatch.c uses &lt;cpuid.h&gt;, __get_cpuid_count and GNU inline asm for XGETBV, so as written it needs GCC, Clang or zig cc. Windows binaries come from zig's x86_64-windows-gnu target.
- You need outside scrutiny or long-term maintenance: it is an unofficial derivative that the stb author does not endorse, created 2026-09-29 with 5 commits and 0 stars. Upstream fixes after v2.18 need a manual re-sync.

## How it is fast

None of the resampling code changes. The gain comes from running upstream's own STBIR_SIMD8/AVX2 code paths on CPUs that support them, without having to compile the whole program with -march=x86-64-v3. lib/resize_dispatch.c checks CPUID and XGETBV for the full x86-64-v3 feature set once and caches the answer. Calls whose output type is half-float stay on the SSE2 variant. Optional held-out PGO (trained by tools/train.c on sizes and filters different from the benchmark rows) improves code layout in the split-TU library. Comparing the two committed CSVs (derived from page data), the -O3/x86-64-v2 baseline variant is within 5% of stock -O2 on 18 of 23 rows, so nearly all of the speedup is the AVX2 path.

## Compared with alternatives

Pick it when you must keep stb_image_resize2's API and exact output and only want its AVX2 speed in a portable binary. tir (tinyexr) is faster than stb2 on the float32 AVX2 path but changes output, and fast_image_resize (Rust) or Pillow-SIMD are faster resizers with different APIs and outputs.

## Integration

| | |
|---|---|
| **Form** | static lib (scripts/build_opt.sh or zig build; prebuilt v1.0.0 archives on GitHub releases), or source-drop of the unchanged header |
| **Dependencies** | none at runtime; building needs clang or gcc (llvm-profdata for clang PGO) or zig 0.16.0 |
| **Minimum toolchain** | C, as upstream; the dispatch layer needs GCC/Clang-style &lt;cpuid.h&gt; and inline asm |
| **Platforms** | x86-64 (SSE2 baseline, AVX2 variant used on full x86-64-v3 CPUs); aarch64 and other targets baseline only; prebuilt archives for x86_64-linux-gnu, x86_64-linux-musl, aarch64-linux-musl, x86_64-windows-gnu, aarch64-macos |
| **Thread safety** | Same as upstream: separate STBIR_RESIZE objects are independent, and the split API (stbir_build_samplers_with_splits plus stbir_resize_extended_split) spreads one resize over threads. The dispatch layer adds a non-atomic static cache of the CPU check, written on first use (a benign race). |
| **Drop-in for the baseline** | partial: same header, same 22 exported symbols and byte-identical output, but you link the archive instead of defining STB_IMAGE_RESIZE_IMPLEMENTATION; header-only use gets no AVX2 dispatch |

## Gotchas

- Byte-identity depends on -ffp-contract=off. scripts/build_opt.sh and build.zig pass it, but if you compile lib/\*.c in your own build system, GCC's default contraction plus x86-64-v3 FMA can produce FMAs and different output bytes.
- The STBIR_CPU environment variable (base, sse2 or scalar) is read on the first call in production builds and silently forces the baseline path. STBIR_CPU=avx2 cannot force AVX2 on a CPU without x86-64-v3.
- The v1.0.0 release archives are not the benchmarked artifact: release.yml builds them with zig 0.16 ReleaseFast, no PGO, a generic x86-64 baseline and a Haswell AVX2 variant. CI runs the differential test only on the clang build_opt.sh library, not on these archives. Expect the no-PGO figure (README +32.8%) at best.
- Read from the dispatch code, not tested: each call picks a variant from the current output datatype. If you build samplers, then switch the output type to or from half with stbir_set_datatypes, the resize runs on samplers built by the other variant. The matrix's mixed-type cases set types before building, so this path is not covered.

## Known shortcomings

- Claim overstated: the fork leaves the stb_image_resize2 resampler source unchanged (upstream v2.18 pinned by sha256, byte-identical output checked in CI); the whole gain is build configuration (-O3, upstream's own AVX2 path, PGO) against an upstream built at -O2 SSE2. The fork's MEASUREMENT.md says upstream at -march=x86-64-v3 alone gains 26-34%. Geomean 1.36x, float rows 1.12x. Brand-new 0-star fork of nothings/stb; treat as a build-flags recipe rather than a faster implementation.
- bench.c never compares outputs; byte-identity with upstream is checked only by diff_lib.sh at outputs up to 200x150 and about 3.7x downsample, not at the benchmarked 1024 to 64 or 2048x2048 sizes. Rows r6 and r19 disagree by about 1.6x between summary.csv and kernels.csv for the same code paths although the README claims under 3% noise (kernels geomean 1.349, 1.315 without r19); type_name() lacks UINT8_SRGB so the sRGB rows r21/r22 are labelled uint8. The base variant is within 5% of stock -O2 on 18 of 23 rows, so the gain is the AVX2 path. Release archives are built by zig ReleaseFast (no PGO, generic baseline plus haswell AVX2) and CI never differential-tests them; dispatch needs cpuid.h and GNU asm, so MSVC cl.exe cannot build it; STBIR_CPU is honoured in production builds.

## Caveats and trade-offs

A brand-new unofficial derivative of nothings/stb (not a GitHub fork object; 5 commits, all on 2026-09-29), not endorsed by the stb author, with no outside scrutiny. src/stb_image_resize2.h is byte-identical to upstream v2.18 (sha256 checked against nothings/stb master), and the fork adds only build glue: the same header compiled for SSE2 and for x86-64-v3 AVX2, a CPUID dispatch layer and PGO. All of the measured speedup therefore comes from build configuration, since the baseline is upstream at -O2 for the default SSE2 target. The fork's own docs/MEASUREMENT.md says upstream built with -O3 -march=x86-64-v3 is byte-exact and +26-34% faster on its own, and docs/REJECTED.md says PGO is neutral (0.9985x) on a monolithic build and only recovers the split library's layout (+32.8% to +38.0%). No head-to-head against an upstream x86-64-v3 build is published. The practical value is a portable x86-64 binary that uses upstream's AVX2 path at runtime; a project that can target x86-64-v3 gets the same speed from stock stb. Output is claimed byte-identical by harness/diff_lib.sh (8,284 checks on each of 3 dispatch paths), which is configured in CI (pass status not checked here); half-float output stays on the SSE2 path because of a signed-zero divergence. Timings come from a single WSL2 run on a hybrid P/E-core CPU, pinned to vCPU 3 with no PMU, min over repeats; the README calls per-row differences under about 3% noise. The fork documents upstream quirks it does not fix (an uninitialized read in the uint16 WRAP BOX upsample and some half filter paths; a UBSan false positive in the sRGB encoder).

Byte-identical output to upstream (README states a differential test of 8,284 cases on 3 dispatch paths). The resampler source is unchanged; the speedup comes from shipping a prebuilt static library with baseline and AVX2 variants chosen by CPUID at runtime, plus PGO. Header-only use gets only the baseline build. x86-64 gains only; aarch64 is a single scalar/NEON build. half output falls back to baseline.

## Maintenance

Brand-new (created 2026-09-29, 5 commits, v1.0.0 release with prebuilt archives, CI green on all 5 runs). It is MIT OR Unlicense and small enough to vendor, but unofficial and pinned to upstream v2.18.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now A.
- **Tier reason:** The comparison is reproducible: bench/bench.c with harness/bench_vs_upstream.sh, kernbench.sh and consumer/run.sh build upstream stb_image_resize2 v2.18 (vendored, sha256 173e6546... identical to nothings/stb master, commit 904aa67 of 2026-03-13) at -O2 against the fork's library at stated flags with clang 23.1.2 on an i7-14700F, and the CSVs are committed, so the tier stays A. The record overstated the claim: the resampler code is unchanged and the whole gain comes from build flags (upstream's own AVX2 path, -O3 and PGO against an SSE2 -O2 build), and the float rows reach only 1.12x.
- **Verifier notes:** is_fork_of is set (it was already correct). Upstream pinning, flags and the byte-identity harness all check out, so it keeps A on reproducibility; the verdict is downgrade because the record's claim overstated what the fork contributes. The measured code does the same work as the baseline (identical source and identical output), but the baseline is built with weaker flags; the honest headline is 'stock stb's AVX2 speed in a portable binary', not a faster resizer.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/aplghl/stb-image-resize-opt>
  - <https://github.com/aplghl/stb-image-resize-opt/commits/main>
  - <https://github.com/aplghl/stb-image-resize-opt/blob/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/summary.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/kernels.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/consumer.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/bench_vs_upstream.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/bench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/kernbench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/consumer/run.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/scripts/build_opt.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/scripts/env.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/lib/resize_avx2.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/lib/resize_base.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/docs/MEASUREMENT.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/docs/REJECTED.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/upstream/stb_image_resize2.h>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/src/stb_image_resize2.h>
  - <https://raw.githubusercontent.com/nothings/stb/master/stb_image_resize2.h>
  - <https://github.com/nothings/stb/commits/master/stb_image_resize2.h>
- **Sources the enricher read:**
  - <https://github.com/aplghl/stb-image-resize-opt>
  - <https://github.com/aplghl/stb-image-resize-opt/actions>
  - <https://github.com/aplghl/stb-image-resize-opt/releases>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/build.zig>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/bench_vs_upstream.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/bench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/kernbench.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/diff_lib.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/matrix.inc.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/consumer/run.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/harness/consumer/consumer.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/scripts/build_opt.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/scripts/env.sh>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/lib/resize_base.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/lib/resize_avx2.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/lib/resize_dispatch.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/tools/train.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/tools/resize_dump.c>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/tools/gen.h>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/docs/MEASUREMENT.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/docs/REJECTED.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/docs/PORT_STATUS.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/README.md>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/summary.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/kernels.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/results/consumer.csv>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/upstream/stb_image_resize2.h>
  - <https://raw.githubusercontent.com/aplghl/stb-image-resize-opt/HEAD/src/stb_image_resize2.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aplghl/stb-image-resize-opt`) · [data/wave10/enrich/raw/github_com_aplghl_stb_image_resize_opt.json](../../../data/wave10/enrich/raw/github_com_aplghl_stb_image_resize_opt.json) (enrichment confidence 0.85)

</details>
