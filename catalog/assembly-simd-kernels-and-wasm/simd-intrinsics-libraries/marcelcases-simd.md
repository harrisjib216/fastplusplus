# marcelcases/simd (std::experimental::simd kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Seven teaching kernels written with libstdc++ std::experimental::simd, timed against de-vectorized scalar loops on x86-64, AArch64 and RVV.

| | |
|---|---|
| **Beats** | scalar C++ version of each kernel built with compiler auto-vectorization disabled (-fno-tree-vectorize) |
| **Claimed result** | x86-64 Intel Xeon Platinum 8480+, one pinned core, GCC 14.1: sum reduction 5.37x, 1D convolution 5.89x, upper-bound clamp 6.81x, count above threshold 4.85x, horizontal blur 2.12x, dot product 1.78x, element-wise add 1.62x, softmax 1.57x, memory-bound FMA 1.04x. icpx 2025.2 on the same CPU: clamp 10.29x, dot product 4.45x, sum reduction 5.32x. Apple M1 Pro, GCC 15.2.0: count above threshold 24.51x, clamp 20.00x, sum reduction 4.00x, 1D convolution 4.02x, element-wise add 2.60x. Banana Pi F3 (RVV 1.0, VL=8): sum reduction 4.51x, 1D convolution 2.15x. |
| **Workload** | Seven exercises (nine kernel rows: element-wise add, memory-bound FMA, sum reduction, dot product, upper-bound clamp, count above threshold, stable softmax, horizontal blur, 1D convolution) written with libstdc++ std::experimental::simd versus scalar versions; 16,777,216 floats for the first four, 4,194,304 for softmax, a 1920x1080 grayscale image for blur, 1,048,576 floats for convolution; median of 9 samples. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8480+ (MareNostrum 5 GPP, one pinned core, exclusive node); Banana Pi F3 (RISC-V RVV 1.0, 256-bit VLEN); Apple M1 Pro (4-lane NEON, not pinned) |
| **Compiler and flags** | GCC 14.1 (MareNostrum 5), icpx 2025.2, Homebrew GCC 15.2.0 (M1), conda-forge GCC 16.2 cross-compiler (RISC-V). Makefile: Linux -std=c++2b -O3 -march=native -mavx512f -mavx512vl -mavx512dq -mavx512bw -fno-math-errno -fno-trapping-math; macOS arm64 -std=c++2b -O3 -mcpu=apple-m1 -fno-math-errno -fno-trapping-math; RISC-V (README) -std=c++23 -O3 -march=rv64gcv_zvl256b -mrvv-vector-bits=zvl -static -fno-math-errno -fno-trapping-math. Scalar builds add -fno-tree-vectorize -fno-tree-loop-distribute-patterns (GCC) or -fno-vectorize -fno-slp-vectorize (icpx/clang). RISC-V VL=4 and VL=8 variants used separate builds with temporary SIMD aliases not in the repo. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/marcelcases/simd) · [benchmark](https://github.com/marcelcases/simd) |

## Verdict

On one pinned core of an Intel Xeon Platinum 8480+ with GCC 14.1, std::experimental::simd versions ran faster than scalar builds compiled with -fno-tree-vectorize -fno-tree-loop-distribute-patterns by 5.37x (sum), 5.89x (1D convolution), 6.81x (clamp), 4.85x (count), 1.78x (dot product) and 1.04x (memory-bound FMA), median of 9 samples of 10 calls; icpx 2025.2, an unpinned Apple M1 Pro with GCC 15.2.0 (up to 24.51x on count) and a Banana Pi F3 (RVV, VL=8, 4.51x sum) were also measured. Only the sum and dot-product rows plausibly survive against a plain -O3 build, since GCC does not reassociate float reductions without -ffast-math.

## Use it when

- Learning or teaching std::experimental::simd idioms (where, popcount on masks, reduce, hmax, shifted loads) from short, documented examples.
- Copying a small reduction kernel (float sum or dot product) where you cannot use -ffast-math; these are the rows GCC would not auto-vectorize at -O3 anyway (5.37x sum on the Xeon with GCC).
- Checking how one std::experimental::simd source behaves across AVX-512, NEON and RVV toolchains, including the README's notes on what each compiler actually emitted.
- Starting point for a portable stencil or FIR kernel when you are already on GCC/libstdc++ and want to avoid intrinsics.

## Skip it when

- As evidence that std::simd beats normally optimized code: every scalar row is built with -fno-tree-vectorize (GCC) or -fno-vectorize -fno-slp-vectorize (icpx), and no plain -O3 scalar row exists, so add, FMA, clamp, blur and convolution gains are likely much smaller against an ordinary build.
- When you need a maintained library: 0 stars, history from 2026-09-03, no releases, no packaging, no API stability; for production use EVE, Vector Class Library or ISPC.
- Toolchains without libstdc++ &lt;experimental/simd&gt; (Apple Clang/libc++, MSVC) or code meant for C++26 &lt;simd&gt;, which the repo does not use.
- Transcendental-heavy work: softmax's exp loop stays scalar std::exp, so softmax gains are only 1.2x to 2.35x.
- Memory-bound streaming (add, FMA): gains are 1.01x to 2.60x because the kernels are traffic-limited.

## How it is fast

Plain explicit vectorization with native_simd&lt;float&gt; (16 lanes under AVX-512, 4 on M1 NEON, fixed 4 or 8 on the RISC-V toolchain): copy_from/copy_to unaligned loads and stores, one lane-wise accumulator plus stdx::reduce or stdx::hmax for reductions, stdx::fma for dot product, where() masks for clamp and popcount(mask) for counting, three shifted loads for the blur and broadcast weights for the convolution, with scalar tails. There are no multi-accumulator tricks, prefetching, non-temporal stores or vector exp; most of the clamp and count gains come from replacing branchy scalar decisions with masks.

## Compared with alternatives

Pick it over EVE or the Vector Class Library only when you want short worked examples of the standard std::experimental::simd API rather than a supported SIMD library; like UltraSIMD and libalgebra, its speedups are measured against deliberately non-vectorized scalar code, so do not use its ratios to choose between libraries.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libstdc++ &lt;experimental/simd&gt; |
| **Minimum toolchain** | C++23 (-std=c++2b) with libstdc++ &lt;experimental/simd&gt;; tested with GCC 14.1, Homebrew GCC 15.2.0, conda-forge GCC 16.2 (RISC-V cross) and icpx 2025.2 |
| **Platforms** | x86-64 (Makefile defaults assume AVX-512 on MareNostrum 5), AArch64 (Apple M1 with Homebrew GCC), RISC-V RVV 1.0 (cross-compiled; native_simd&lt;float&gt; reports one lane, so fixed widths 4 and 8 were used in separate, unpublished builds) |
| **Thread safety** | not documented; the kernels are stateless free functions over caller-owned buffers |
| **Drop-in for the baseline** | partial — each SIMD kernel keeps the same signature as its scalar twin and can be copied, but there is no library target, header-only package or versioned API |

## Gotchas

- Harness asymmetry beyond the documented de-vectorized baseline: the SIMD binaries are compiled with auto-vectorization on, so the SIMD column also includes whatever the compiler vectorizes in the source's plain loops (the README notes icpx turns softmax's scalar exp loop into SVML calls, which only the SIMD build can do).
- Clamp's scalar side is a branchy conditional store on uniform [-1, 1] data with bound 0.5 (about 25% taken, random), and count tests &gt; 0 on the same distribution (about 50%); the 6.81x/10.29x x86 and 20.00x/24.51x M1 clamp/count rows largely measure removed branch mispredictions against a baseline the compiler was told not to vectorize.
- Weak softmax validation: the driver accepts a max absolute difference of 1e-2 while each output for 4,194,304 standard-normal logits is at most about 3e-5 (my estimate), so only the sum-to-one checksum (within 1e-3) guards correctness; the kernel itself looks correct on reading.
- Kernels do not check preconditions: convolve_1d computes input_size - kernel_size + 1 in size_t and blur_horizontal assumes width &gt;= 2; only the drivers validate. Clamp and softmax drivers keep 10 full copies of the input (640 MiB for clamp at the default 16,777,216 floats); no result CSVs are committed (results/ is gitignored), and x86 rows for exercises 1-5 predate the per-sample warm-up change.

## Known shortcomings

- Downgraded A to C: the scalar baseline is built with auto-vectorization off (-fno-tree-vectorize / -fno-vectorize) while the SIMD side is libstdc++ std::experimental::simd itself; RISC-V VL=4/8 builds are not in the repo, no result CSVs, 0-star teaching study; only the sum and dot rows (5.37x, 1.78x) hold against plain -O3; M1 flags are -mcpu=apple-m1.
- Harness asymmetry: the scalar baseline is built with auto-vectorization off while the SIMD build has it on, with no plain -O3 row; icpx's SVML vectorizes the softmax exp loop in the SIMD build only. Clamp and count scalar loops are branchy on random data (about 25% and 50% taken), so the 6.81x/10.29x/20.00x/24.51x rows mostly measure removed mispredictions. The softmax check accepts an absolute difference of 1e-2 while outputs are at most about 3e-5, so only the sum-to-one check guards it; the code itself looks correct. No result CSVs (results/ gitignored); x86 rows 1-5 are stale.

## Caveats and trade-offs

Teaching study, not a reusable library; the SIMD side is libstdc++'s std::experimental::simd itself (std::simd is one of the category's listed baselines), so the entry measures std::simd code against scalar loops, not a library beating an incumbent. The baseline is deliberately de-vectorized scalar code, so the speedups say little about beating a normally compiled -O3 build; the exception is sum reduction and dot product, which GCC cannot auto-vectorize at -O3 without -ffast-math anyway, so those rows (5.37x and 1.78x on the Xeon with GCC) are the ones that would hold against a plain -O3 build. Element-wise add and memory-bound FMA are memory-traffic-limited (1.01x to 1.65x on x86 and RISC-V). The README itself notes that count_above on RISC-V contained no RVV instructions (gain is scalar unrolling), that icpx vectorizes softmax's exp loop through SVML, and that the large M1 clamp/count gains come from replacing branches with masks. x86 exercises 1-5 used three initial warm-ups instead of per-sample warm-ups and have not been refreshed. The RISC-V VL=4/VL=8 variants cannot be rebuilt from the repo (temporary aliases), and no result CSVs are committed (results/ is absent). M1 run had no core pinning. Repository history starts 2026-09-03, 0 stars, so results are unreviewed.

Needs a C++23 compiler with libstdc++ &lt;experimental/simd&gt; (GCC); does not use C++26 &lt;simd&gt;. Makefile defaults target MareNostrum 5 AVX-512 and Apple M1, not generic hosts. Portable across x86-64, AArch64 and RISC-V RVV, but the RISC-V toolchain reports one lane for native_simd&lt;float&gt;, so fixed widths 4 and 8 were used.

## Maintenance

Active (last commit 2026-10-06, 89 commits, all since 2026-09-03), MIT-licensed teaching code with 0 stars, no issues and no releases; small enough to copy single kernels, but treat it as documentation of std::experimental::simd rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness (Makefile, drivers/, scripts/benchmark.sh) is public and the README states compilers, flags and CPUs, which would be A, but the baseline is deliberately de-optimized: scalar builds add -fno-tree-vectorize -fno-tree-loop-distribute-patterns (GCC) or -fno-vectorize -fno-slp-vectorize (icpx), so by analogy with the -O0 cap the win over a normal -O3 build is not shown; the RISC-V VL=4/VL=8 rows came from builds with temporary aliases that are not in the repo and no raw result CSVs are committed. Capped at C.
- **Verifier notes:** All quoted speedups match the README tables. Downgraded A to C for a crippled baseline (auto-vectorization disabled in the scalar build), unreproducible RISC-V variants and missing raw results; the M1 build uses -mcpu=apple-m1, not -march=native. libstdc++ in baseline_stdlib is the SIMD implementation (std::experimental::simd), not the baseline; shortcomings to record: de-vectorized baseline, teaching study with 0 stars, stale x86 rows 1-5.
- **Fields the verifier corrected:** `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** verifier batch-40 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/marcelcases/simd>
  - <https://github.com/marcelcases/simd/commits>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/Makefile>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/02_reduction_dot/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/03_clamp/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/07_conv1d/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/02_reduction_dot.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/02_reduction_dot.cpp>
- **Sources the enricher read:**
  - <https://github.com/marcelcases/simd>
  - <https://github.com/marcelcases/simd/commits>
  - <https://github.com/marcelcases/simd/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/Makefile>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/benchmark_common.hpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/benchmark_implementation.hpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/benchmark_reference.hpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd_common.h>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/01_add_fma.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/02_reduction_dot.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/03_clamp.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/04_count.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/05_softmax.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/06_filter.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/drivers/07_conv1d.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/01_add_fma.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/02_reduction_dot.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/03_clamp.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/04_count.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/05_softmax.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/06_filter.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/scalar/07_conv1d.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/01_add_fma.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/02_reduction_dot.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/03_clamp.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/04_count.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/05_softmax.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/06_filter.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/src/simd/07_conv1d.cpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/include/exercises/01_add_fma.hpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/include/exercises/02_reduction_dot.hpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/include/exercises/03_clamp.hpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/include/exercises/04_count.hpp>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/01_add_fma/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/02_reduction_dot/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/03_clamp/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/04_count/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/05_softmax/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/06_filter/README.md>
  - <https://raw.githubusercontent.com/marcelcases/simd/HEAD/docs/07_conv1d/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/marcelcases/simd`) · [data/wave13/enrich/raw/github_com_marcelcases_simd.json](../../../data/wave13/enrich/raw/github_com_marcelcases_simd.json) (enrichment confidence 0.8)

</details>
