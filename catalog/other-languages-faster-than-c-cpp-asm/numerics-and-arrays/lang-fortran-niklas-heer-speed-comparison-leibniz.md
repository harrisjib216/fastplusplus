# Fortran (gfortran) in niklas-heer/speed-comparison: Leibniz pi series

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Fortran` · `MIT` · 🟢 active

> gfortran -Ofast Leibniz pi loop in speed-comparison: 1.11x faster than gcc-built C, level with clang-built C and C++.

| | |
|---|---|
| **Beats** | C (gcc 15.2.0, -O3 -flto -march=native with -fno-signed-zeros -fno-trapping-math -fassociative-math) and the clang / C++ builds of the same Leibniz loop in the same suite |
| **Claimed result** | Published snapshot 2026-09-05T193245, combined_results.csv medians in ms: Fortran 90 (gfortran 14.3.0) 141.67 vs C (gcc 15.2.0) 157.9, about 1.11x (derived from page data); vs C++ (g++) 158.78, about 1.12x (derived); vs C (clang 21.1.2) 146.07, about 1.03x (derived); vs C++ (clang++) 143.32, about 1.01x (derived). Min-max ranges: Fortran 141.04-144.35 ms, C++ clang++ 142.74-144.96 ms, C (clang) 143.63-150.61 ms, C (gcc) 155.46-160.78 ms, so the lead over the clang builds is inside the sample range. |
| **Workload** | Single-threaded Leibniz series for pi, 1,000,000,000 terms per run (rounds.txt), timed with hyperfine; this historical run used two warm-up executions, three measured samples (TimesPerRun in the raw JSON) and a separate output execution; median wall time reported. Sources at revision c71e4cd81464b238172605982806c5bf827a70a1 (src/leibniz.f90, src/leibniz.c, src/leibniz.cpp). |
| **Metric** | throughput |
| **Hardware** | AMD EPYC-Genoa Processor, 4 threads, shared x86-64 VM (runner homelab-argo), kernel 6.18.38-talos |
| **Compiler and flags** | Fortran: gfortran 14.3.0 `gfortran leibniz.f90 -o leibniz -Ofast -flto -ffast-math -march=native -mtune=native`. C: gcc 15.2.0 `gcc -O3 -s -flto -march=native -mtune=native -fomit-frame-pointer -fno-signed-zeros -fno-trapping-math -fassociative-math -o leibniz leibniz.c -lm`. C++ clang++ 21.1.2 and C clang 21.1.2 use the same flag set (from docs/history/2026-09-05T193245/raw/\*.json). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 750 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/niklas-heer/speed-comparison) · [benchmark](https://github.com/niklas-heer/speed-comparison/blob/master/docs/history/2026-09-05T193245/combined_results.csv) |

## Verdict

In the published 2026-09-05 snapshot (AMD EPYC-Genoa VM, 1e9 terms, hyperfine median of three runs), gfortran 14.3.0 -Ofast -ffast-math -march=native took 141.67 ms. That is 1.11x faster than gcc 15.2.0 -O3 C with three relaxed-math flags (157.9 ms) and 1.01x faster than clang++ 21.1.2 (143.32 ms, inside the sample range). The December 2025 snapshot repeats the lead only over gcc-built C (238.94 vs 253.23 ms, 1.06x); clang++ and g++ C++ were faster than Fortran there.

## Use it when

- You keep numerical code in Fortran and want evidence that gfortran -Ofast vectorises a simple division-heavy reduction as well as clang does for C and C++.
- A gcc-built C or C++ reduction loop trails clang by about 10%: this pair shows the gap can come from gcc 15's code generation for that loop shape, so try clang or rewrite the loop with fixed-sign unrolled terms before blaming the language (inference).
- You need a reproducible single-threaded floating-point reference: sources pinned at revision c71e4cd, exact compile commands, per-sample timings and the CPU model are all in docs/history/2026-09-05T193245/raw/\*.json.
- Comparing math-flag regimes (-Ofast -ffast-math against selective relaxed-math flags) on x86-64 with AVX-512 (EPYC Genoa, -march=native).

## Skip it when

- Choosing a language for speed: the lead over the best C/C++ build (clang++ 143.32 ms) is 1.2% and inside the three-sample ranges, and the project README says three samples cannot establish a reliable winner for small differences.
- Code that needs strict IEEE results: -Ofast -ffast-math also enables finite-math-only and reciprocal math. The Fortran result is 1.4e-10 away from the exact 1e9-term partial sum, against under 5e-12 for the gcc and clang C builds (derived from the raw JSON).
- Inside a C++ project: the clang++ build of the plain one-term C++ loop already runs at the same speed (143.32 ms), so a compiler or flag change gets the result without a language switch.
- Term counts above about 1.07e9, or not a multiple of 4 (see gotchas).

## How it is fast

The suite states no mechanism, and the numbers point to a shared floor rather than a Fortran advantage. In the 2026-09-05 snapshot the fastest group sits within 3.4%: Rust SIMD 141.31, Fortran 141.67, Nim 142.43, Objective-C 142.95, C++ clang++ 143.32 and C clang 146.07 ms. Only the two gcc 15.2.0 builds of the one-term C/C++ loop, at 157.9 and 158.78 ms, sit about 11% above it (derived from page data). Every run performs 1e9 double divisions, which fits all well-vectorised builds hitting the same divide-throughput limit (inference; not profiled). gfortran reaches that floor with -Ofast -ffast-math, whose reassociation lets it vectorise the reduction, plus the four-term unroll that drops the C loop's per-term parity-sign arithmetic. clang reaches it from the unchanged one-term C source with only -fassociative-math -fno-signed-zeros -fno-trapping-math.

## Compared with alternatives

It is the cleanest of the Fortran-vs-C rows, the plb2 matmul (6% over clang C on an M1) and fortran-lang poisson2d, for showing that the gap is backend code generation (gfortran and clang against gcc 15) rather than the language, and its lead over gcc-built C repeated across two snapshots (1.06x in December 2025, 1.11x in September 2026). The JuliaLang/Microbenchmarks mandelbrot Fortran row, by contrast, reversed in its suite's later run.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the gfortran runtime |
| **Minimum toolchain** | Fortran 2008 (open with newunit=, iso_fortran_env real64); measured with gfortran 14.3.0 (2026-09-05 snapshot) and 14.2.0 (2025-12-14 snapshot) |
| **Platforms** | Measured only on x86-64 (AMD EPYC-Genoa VM with AVX-512, -march=native); the source is portable standard Fortran |
| **Thread safety** | Not applicable: single-threaded program with no shared state; the suite keeps its Fortran OpenMP variant outside the ranked comparison |
| **Drop-in for the baseline** | no |

## Gotchas

- The loop is not the C loop. Fortran sums four terms per iteration with fixed signs and a default 32-bit signed counter, while C uses one term per iteration with a parity-derived sign in unsigned arithmetic. The term counts match only because 1e9 is a multiple of 4; for other counts the Fortran loop adds up to three extra terms (derived from source).
- Latent overflow and unchecked input. 2\*i+7 is computed in default 32-bit integer and overflows once i passes 1,073,741,820, so any rounds.txt value above about 1.07e9 gives a wrong sum; C's unsigned arithmetic holds to about 2.1e9 (derived from source). The read's iostat is never checked, so a missing rounds.txt leaves rounds undefined.
- Accuracy is lower. Four times the exact 1e9-term partial sum is about pi + 1e-9 = 3.1415926545898. Against that, gcc C prints 3.1415926545850823 (-4.7e-12), clang C 3.1415926545907205 (+9.3e-13) and Fortran 3.141592654730 (+1.4e-10). The -Ofast summation is therefore 30-150x less accurate (derived), which the suite's accuracy column shows as 9.44 against 9.50. In the same snapshot Nim prints 2.0e-9 below gcc C (4/(2e9+1)), so it sums one term fewer; that is harmless for timing but means its row is not quite the same workload.
- Historical protocol. The snapshot ran on a shared 4-thread Argo VM (runner homelab-argo) with two warm-ups, three measured executions and a separate output execution. Process start-up and the rounds.txt read fall inside the timer, which is negligible at about 140 ms. The README says this run predates the current one-warm-up, three-measurement runner, and no newer full run is published.

## Known shortcomings

- No mechanism: the Fortran loop is hand-unrolled by 4 with constant signs while C computes the sign from index parity; built -Ofast against C at -O3 with partial relaxed math; the 1-3% lead over the clang builds is inside noise and only the lead over gcc C repeats.
- No Fortran advantage: Fortran, Rust SIMD, Nim, Objective-C and the clang C/C++ builds all sit at 141-146 ms, likely a shared divide limit (inference); only gcc 15 C/C++ is about 11% slower, so the gap is gcc codegen, not language. Source flaws: the int32 2\*i+7 overflows above about 1.07e9 rounds; the Fortran result is 1.4e-10 off the exact sum against under 5e-12 for C; Nim sums one term fewer.

## Caveats and trade-offs

Evidence would qualify as A (code, compiler versions, flags and CPU model are all public for both sides) but no mechanism is established, so the tier is capped at C. The margin over the best C/C++ build (clang++ 143.32 ms) is about 1% and inside the three-sample ranges; the suite's README warns that three samples cannot establish a winner for small differences. Flags are not matched: gfortran is built with -Ofast -ffast-math (adds -freciprocal-math, -ffinite-math-only, -fno-math-errno) while C sets only -fno-signed-zeros -fno-trapping-math -fassociative-math, and the backends differ (gfortran 14.3.0 vs gcc 15.2.0). The sources are not line-for-line equivalent: the Fortran loop is hand-unrolled by four with compile-time signs (do i=1,rounds,4: pi = pi + x/(2i+1) - x/(2i+3) + x/(2i+5) - x/(2i+7), signed 32-bit counter), while the C and C++ loops compute each term's sign from the index parity (x = -1.0 + 2.0\*(i & 1)) in unsigned arithmetic; both sum the same 1e9 terms with one division each. The CalculatedPi values differ by about 1.5e-10 (Fortran 3.141592654730, C 3.1415926545850823), so the lower accuracy column (9.440 vs 9.499 digits) reflects both the 12-digit printout and a different summation order. Nim (142.43 ms), Rust SIMD (141.31 ms) and Objective-C (142.95 ms) are also faster than gcc C in the same snapshot; Nim compiles through gcc, so that gap comes from source form, not language. Explicit-SIMD C++ (AVX2) is slower (290.67 ms). In the earlier snapshot docs/history/2025-12-14T070941 (gfortran 14.2.0) Fortran took 238.94 ms: about 1.06x faster than C (gcc) 253.23 ms (derived from page data) but slower than C++ (clang++) 223.89 ms and C++ (g++) 226.37 ms and level with C (clang) 237.46 ms, so only the lead over gcc-built C is repeatable, and in that snapshot g++-built C++ beat gcc-built C by 1.12x on the same loop, which shows how much of the gap is run-to-run and build variation. The HEAD pipeline pins different compiler versions than the snapshot (not re-checked); the snapshot's per-target JSON was used here. [retier] Fortran, Rust SIMD, Nim, Objective-C and the clang C/C++ builds all sit at 141-146 ms, likely a shared divide limit; only gcc 15 C/C++ is about 11% slower, so the gap is gcc codegen, not language. The int32 2\*i+7 overflows above about 1.07e9 rounds; the Fortran result is 1.4e-10 off the exact sum against under 5e-12 for C; Nim sums one term fewer.

The suite compares single implementations of one arithmetic loop, not Fortran as a whole. The Fortran loop is written differently from the C loop: it is unrolled by hand to four terms per iteration (src/leibniz.f90), while C/C++ use a one-term loop with an `i & 1` sign trick written to allow vectorisation (src/leibniz.c).

## Maintenance

The suite is active (last commit 2026-09-20; Nix/Devbox pipeline publishing raw samples per snapshot) and MIT-licensed. The Fortran program is an 18-line source-drop contributed and tuned in PRs #36, #58, #63 and #67 (October 2022). The takeaway is compiler choice and math flags, not something to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Methodology is A-grade (src/leibniz.f90 and src/leibniz.c at source revision c71e4cd, compile commands, compiler versions and the AMD EPYC-Genoa CPU are all in docs/history/2026-09-05T193245/raw/\*.json), but no mechanism is stated or readable from the sources: the gap over gcc-built C coincides with source-form and flag differences (hand-unrolled Fortran loop, -Ofast vs -O3 plus three relaxed-math flags, gfortran 14.3.0 vs gcc 15.2.0) and the lead over the clang builds is inside the three-sample range, so the wave-14 no-mechanism cap holds it at C.
- **Verifier notes:** Numbers match combined_results.csv and the per-target raw JSON exactly (Fortran 141.67 ms, C gcc 157.9, C++ g++ 158.78, C clang 146.07, C++ clang++ 143.32); earlier-snapshot figures also match. Shortcomings to record: no mechanism; flags not matched (-Ofast vs -O3 plus partial relaxed math); Fortran source hand-unrolled by four with constant signs vs per-term parity sign in C; lead over clang builds within three-sample noise; only the lead over gcc C repeats across snapshots; different summation result (CalculatedPi differs by 1.5e-10). Metadata checks out (MIT, 750 stars, not a fork, last commit 2026-09-20).
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-47 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/combined_results.csv>
  - <https://github.com/niklas-heer/speed-comparison/blob/master/docs/history/2026-09-05T193245/combined_results.csv>
  - <https://github.com/niklas-heer/speed-comparison/tree/master/docs/history/2026-09-05T193245/raw>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/fortran.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/c.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/c-clang.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/cpp.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/cpp-clang.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/nim.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/README.md>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/source-revision.txt>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/c71e4cd81464b238172605982806c5bf827a70a1/src/leibniz.f90>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/c71e4cd81464b238172605982806c5bf827a70a1/src/leibniz.c>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/c71e4cd81464b238172605982806c5bf827a70a1/src/leibniz.cpp>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2025-12-14T070941/combined_results.csv>
  - <https://github.com/niklas-heer/speed-comparison>
  - <https://github.com/niklas-heer/speed-comparison/commits/master>
  - <https://github.com/niklas-heer/speed-comparison/tree/master/docs/history>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/c71e4cd81464b238172605982806c5bf827a70a1/src/leibniz.f90>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/c71e4cd81464b238172605982806c5bf827a70a1/src/leibniz.c>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/c71e4cd81464b238172605982806c5bf827a70a1/src/leibniz.cpp>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/c71e4cd81464b238172605982806c5bf827a70a1/src/rounds.txt>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/combined_results.csv>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/fortran.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/c.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/c-clang.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/cpp.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/cpp-clang.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/nim.json>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/README.md>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2026-09-05T193245/raw/source-revision.txt>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/docs/history/2025-12-14T070941/combined_results.csv>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/README.md>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/src/leibniz.f90>
  - <https://raw.githubusercontent.com/niklas-heer/speed-comparison/master/src/leibniz.c>
  - <https://github.com/niklas-heer/speed-comparison/issues?q=is%3Aissue+fortran>
  - <https://github.com/niklas-heer/speed-comparison/pulls?q=is%3Apr+fortran>
  - <https://github.com/niklas-heer/speed-comparison/pull/63>
  - <https://github.com/niklas-heer/speed-comparison/pull/67>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:fortran/niklas-heer/speed-comparison#leibniz`) · [data/wave14/enrich/raw/lang_fortran_niklas_heer_speed_comparison_leibniz.json](../../../data/wave14/enrich/raw/lang_fortran_niklas_heer_speed_comparison_leibniz.json) (enrichment confidence 0.65)

</details>
