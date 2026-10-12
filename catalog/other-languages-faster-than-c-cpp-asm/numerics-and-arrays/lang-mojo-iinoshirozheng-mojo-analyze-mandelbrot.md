# Mojo (explicit SIMD) in mojo-analyze: Mandelbrot

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Mojo` · `MIT` · 🟢 active

> Hand-vectorised Mojo Mandelbrot kernel (4 x Float64 lanes, escape mask) that runs 1.6x faster than scalar clang -O3 C.

| | |
|---|---|
| **Beats** | Scalar C Mandelbrot in the same repo (c/mandelbrot.c, clang -O3 -ffp-contract=off, standard library only) |
| **Claimed result** | ANALYSIS.md Mandelbrot table: Mojo (SIMD) 0.0554 s, C (-O3, scalar) 0.0904 s (1.6x slower), Rust (scalar, release) 0.1114 s (2.0x slower). README: 'Mojo wins the SIMD-heavy Mandelbrot case ... 1.6x faster than C'. The same repo reports C ahead of Mojo on the other four categories (sieve 1.05x, word-frequency 1.6x, CSV aggregation 2.3x, JSON parsing 2.3x). |
| **Workload** | Escape-time Mandelbrot over 800x600 pixels, max 500 iterations, Float64, checksum of per-pixel iteration counts verified equal across all variants; timing of the core computation only, 2 warmups and 7 measured trials, mean reported. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Pro, 14 cores, 24 GB RAM, macOS 26.5.2, arm64 (Linux x86_64 and arm64 CI runners are a secondary reference, no C row there yet) |
| **Compiler and flags** | Mojo 1.0.0 (pixi.toml allows mojo &gt;=1.0.0,&lt;2; ANALYSIS.md states 1.0.0): mojo build --fp-mode contract=off benchmarks/mandelbrot/mandelbrot.mojo, at the default optimisation level 3 (mojolang.org mojo build docs, WebSearch snippet only). C: Apple clang 21, clang -O3 -ffp-contract=off -o dist/mandelbrot-c c/mandelbrot.c (pixi.toml build-c). No -march/-mcpu, LTO or PGO on either side. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Why it wins** | Explicit 4-lane Float64 SIMD with per-lane escape masks in Mojo versus plain scalar loops in C and Rust that depend on autovectorisation (the source's own explanation). |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/iinoshirozheng/mojo-analyze) · [benchmark](https://github.com/iinoshirozheng/mojo-analyze/blob/main/ANALYSIS.md) |

## Verdict

On an Apple M4 Pro under macOS 26.5.2, the Mojo 1.0.0 4-lane SIMD kernel averaged 0.0554 s over 7 runs (after 2 warm-ups) against 0.0904 s for one-pixel-at-a-time C built with Apple clang 21 -O3 -ffp-contract=off (1.63x) and 0.1114 s for scalar Rust, at 800x600 and 500 iterations with identical checksums (42411634). Pooled Linux CI runs on shared GitHub runners give 2.7x on x86_64 and 1.18x on arm64 (derived from page data).

## Use it when

- As a worked, MIT-licensed pattern for writing a masked escape-time loop with Mojo's built-in SIMD type instead of intrinsics: the compute function is about 60 lines.
- When judging whether Mojo's SIMD ergonomics pay off for per-element-independent Float64 loops with a data-dependent exit, compared with C you have not vectorised by hand.
- As a checksum-gated harness template: every variant prints TIME_SECONDS and CHECKSUM, and bench.py refuses to report timings unless all checksums agree, which makes it easy to add a C vector-extension variant and measure the fair comparison.
- When you need Float64 on Apple Silicon: the repo's Metal GPU port is 7.9x faster at 800x600 but runs in Float32 and misses the checksum by 1,180.

## Skip it when

- As evidence that Mojo generates faster code than C: the C baseline is scalar, and a C version using clang ext_vector_type or NEON/AVX intrinsics with the same 4-lane masking is the fair comparison; the repo has none.
- Multi-core or GPU rendering: the kernel is single-threaded on a 14-core machine, and the repo's own GPU port is 7.9x (800x600) to 15.4x (4000x3000) faster in Float32.
- Anything not shaped like independent SIMD-friendly arithmetic: in the same repo C beats Mojo on sieve (1.05x), word frequency (1.6x), CSV aggregation (2.3x) and JSON parsing (2.3x).
- Production image generation: there is no image output and no callable API, and the repo has 0 stars, one author and no issue tracker activity.
- Deeply zoomed or highly chaotic regions: each 4-pixel batch keeps iterating until its slowest lane escapes, so throughput drops when neighbouring pixels have very different escape counts (not measured in the repo).

## How it is fast

Explicit SIMD with per-lane masking: four adjacent pixels go into SIMD[DType.float64, 4] vectors, z is advanced with active.select(new, old) so escaped lanes freeze, and the batch stops when a horizontal reduce of the mask reaches zero or max_iter is hit; a scalar loop handles width % 4. The win comes from running four independent iteration chains at once, where the C loop iterates one pixel at a time through a data-dependent while exit that clang does not vectorise, so it executes one serial dependency chain. On arm64 the 4-wide Float64 vector lowers to two 128-bit NEON registers; Mojo targets the host CPU by default (mojo build docs, search snippet), so on x86-64 it can use one 256-bit register, which fits the larger Linux x86_64 CI gap (2.7x) than arm64 (1.6x on M4 Pro, 1.18x on the CI arm64 runner).

## Compared with alternatives

Pick this over the Julia and Fortran userfunc_mandelbrot rows in JuliaLang/Microbenchmarks when you want an explicit-SIMD code pattern with an exact checksum gate; pick those rows for a scalar-against-scalar language comparison. The LangArena Mojo Nbody entry is the catalogue's same-algorithm Mojo-vs-C row, but it is a single-run 1.07x that appeared only with a toolchain change.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Mojo standard library only (SIMD, std.sys.argv, std.time.perf_counter_ns); the repo builds through pixi with the MAX conda channel |
| **Minimum toolchain** | Mojo 1.0.0 (pixi.lock pins mojo-1.0.0-release and max 26.5.0; pixi.toml allows mojo &gt;=1.0.0,&lt;2) |
| **Platforms** | osx-arm64, linux-64, linux-aarch64 (pixi.toml); Windows only through WSL2 |
| **Thread safety** | single-threaded program with no shared state; not documented otherwise |
| **Drop-in for the baseline** | no |

## Gotchas

- Build with --fp-mode contract=off (and clang -ffp-contract=off for C): the default contraction fuses zr\*zr - zi\*zi + re into FMA and drifts the checksum (Mojo by 10, clang -O3 from 42411634 to 42411589), because escape counts near the set boundary are sensitive to rounding. Both published timings use contraction off, so neither side benefits from FMA.
- The record's caveat that the Linux CI has no C row is out of date: experiments/2026-09-04-linux-five-category-crosscheck.md pools 3 CI runs (9 trials each) and shows Mojo 0.0493 s vs C 0.1348 s on x86_64 (2.7x) and 0.0923 s vs 0.1093 s on arm64 (1.18x, ratios derived from page data). The gap tracks vector width and core type, consistent with hand vectorisation rather than code generation.
- Mojo builds for the host CPU and its features by default (docs snippet), while clang without -march targets a generic baseline; a Mojo binary built on a newer machine may not run on an older one, and the two sides are not built for the same ISA level.
- The kernel is untuned even as SIMD code: it reduces the active mask every iteration and squares the new z for the escape test, then squares it again on the next iteration. A tuned C or Mojo SIMD version could be faster, so 1.6x is neither an upper nor a lower bound on what explicit SIMD gives here.

## Known shortcomings

- Crippled baseline: plain scalar C against hand-written 4-lane SIMD Mojo; the repository itself says the techniques differ.
- Hand SIMD (4 x Float64 lanes) against scalar C remains the main flaw and the repo has no vectorised C row. The record's caveat that the Linux CI has no C row is out of date: experiments/2026-09-04-linux-five-category-crosscheck.md shows Mojo 0.0493 s vs C 0.1348 s on x86_64 (2.7x) and 0.0923 vs 0.1093 s on arm64 (1.18x), ratios that track vector width and are consistent with hand vectorisation. Mojo builds for the host CPU by default while clang builds a generic baseline; both published timings use contraction off, so neither side gets FMA. Kernel and checksum are correct.

## Caveats and trade-offs

Not a same-technique comparison, and the repo says so. The Mojo version restructures the pixel loop into SIMD[DType.float64, 4] batches with a per-lane active mask (two 128-bit NEON registers per vector on arm64). It keeps iterating each batch until its slowest lane escapes, then runs a scalar remainder loop. The C and Rust versions iterate one pixel at a time in a while loop with a data-dependent exit, which clang does not autovectorise, so C runs fully scalar. The 1.6x therefore measures hand vectorisation against scalar code, not Mojo code generation. A C version using clang vector extensions or NEON intrinsics would be the fair baseline, and none is provided. Both sides are optimised builds with FMA contraction turned off, and the checksums match (42411634). Single machine (Apple M4 Pro, macOS 26.5.2), 2 warm-ups and 7 timed runs, means reported (C stdev 0.0019 s). The Linux CI runs have no C row yet. Single-author repo with 0 stars and 0 forks. C is ahead of Mojo on the other four categories in the same repo (sieve 1.05x, word frequency 1.6x, CSV aggregation 2.3x, JSON 2.3x). [retier] Enricher correction: the Linux CI does have a C row now; experiments/2026-09-04-linux-five-category-crosscheck.md pools 3 CI runs (9 trials each) and shows Mojo 0.0493 s vs C 0.1348 s on x86_64 (2.7x) and 0.0923 vs 0.1093 s on arm64 (1.18x, derived from page data), a gap that tracks vector width and is consistent with hand vectorisation. Mojo builds for the host CPU by default while clang builds a generic baseline; both published timings use contraction off, so neither side gets FMA; kernel and checksum are correct.

The Mojo kernel is hand-vectorised (SIMD[DType.float64, 4] with a per-lane active mask and a scalar remainder loop), so it costs more code than the C loop. Mojo needs --fp-mode contract=off here: the default fused-multiply-add contraction changed the checksum by 10 out of about 42.4 million; clang -O3 on this platform shows the same drift unless -ffp-contract=off.

## Maintenance

Active, MIT-licensed single-author research notebook (124 commits, last 2026-09-25, 0 stars, commits co-authored with Claude); the kernel is small enough to copy, but its 1.6x measures hand SIMD against scalar C, which is why it sits at tier D.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now D.
- **Tier reason:** ANALYSIS.md shows Mojo (SIMD) 0.0554 s against C (-O3, scalar) 0.0904 s, and the code (c/mandelbrot.c, benchmarks/mandelbrot/mandelbrot.mojo), flags (pixi.toml build and build-c) and CPU (Apple M4 Pro) are public, which would meet A. But the C baseline is plain one-pixel-at-a-time scalar code, while the Mojo version is hand-vectorised into 4-pixel masked SIMD batches, and the repo says so itself ('Not an apples-to-apples same-technique comparison, by design'). That is naive code against a tuned other-language version, so the crippled-baseline precedent puts it at D.
- **Verifier notes:** Downgraded A to D under the wave-14 crippled-baseline rule (naive scalar C against a hand-SIMD Mojo version). The numbers and flags all check out, but the repo itself calls the comparison not same-technique. same_algorithm corrected to false and same_opt_level to true (both optimised builds with FP contraction off; the Mojo default level 3 comes from a docs snippet). MIT, 0 stars, last commit 2026-09-25, active.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-60 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/README.md>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/ANALYSIS.md>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/pixi.toml>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/c/mandelbrot.c>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/benchmarks/mandelbrot/mandelbrot.mojo>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/LICENSE>
  - <https://github.com/iinoshirozheng/mojo-analyze>
  - <https://github.com/iinoshirozheng/mojo-analyze/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/README.md>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/ANALYSIS.md>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/pixi.toml>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/pixi.lock>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/c/mandelbrot.c>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/benchmarks/mandelbrot/mandelbrot.mojo>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/rust/src/bin/mandelbrot.rs>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/scripts/bench.py>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/results/results.json>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/LICENSE>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/experiments/2026-09-04-linux-five-category-crosscheck.md>
  - <https://raw.githubusercontent.com/iinoshirozheng/mojo-analyze/main/experiments/2026-09-08-shared-runner-estimator-sensitivity.md>
  - <https://github.com/iinoshirozheng/mojo-analyze>
  - <https://github.com/iinoshirozheng/mojo-analyze/tree/main/experiments>
  - <https://github.com/iinoshirozheng/mojo-analyze/issues?q=is%3Aissue>
  - <https://github.com/iinoshirozheng/mojo-analyze/commits/main>
  - <https://github.com/iinoshirozheng/mojo-analyze/commits/main/benchmarks/mandelbrot/mandelbrot.mojo>
  - <https://github.com/iinoshirozheng/mojo-analyze/commits/main/results/results.json>
  - https://docs.modular.com/mojo/cli/build (WebSearch snippet only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:mojo/iinoshirozheng/mojo-analyze#mandelbrot`) · [data/wave14/enrich/raw/lang_mojo_iinoshirozheng_mojo_analyze_mandelbrot.json](../../../data/wave14/enrich/raw/lang_mojo_iinoshirozheng_mojo_analyze_mandelbrot.json) (enrichment confidence 0.75)

</details>
