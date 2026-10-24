# OpenMP parallel all-pairs nearest-neighbor distance (The C++ Programmer's Mindset, ch. 4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Book sample: one OpenMP 'parallel for' min-reduction pragma on an O(n^2) closest-pair loop, about 4x over one thread.

| | |
|---|---|
| **Beats** | sequential nested-loop version of the same all-pairs minimum-distance computation (nearest_neighbor_distance_seq, one thread) |
| **Claimed result** | About 4x faster with 8 threads: 4,797 ms sequential versus 1,161 ms with OpenMP (ratio 4.1x derived from those two figures; book figures as paraphrased in the seed lead, not on the repo page). |
| **Workload** | All-pairs minimum Euclidean distance (std::hypot on float Point2D) over 65,536 random points in [-1,1]^2, an O(n^2) triangular double loop, timed per call with Google Benchmark in milliseconds; the OpenMP version adds '#pragma omp parallel for reduction(min:...)' on the outer loop. |
| **Metric** | latency |
| **Hardware** | Not stated (book: 8 threads; CPU model not given in the lead). |
| **Compiler and flags** | Not stated. Chapter-04/CMakeLists.txt requires C++20 (CMake 3.30), links OpenMP::OpenMP_CXX and Google Benchmark, and sets no CMAKE_BUILD_TYPE or optimisation flags; the repository has no CMakePresets.json, so with an empty build type CMake adds no -O flag and the optimisation level depends on how the reader configures it. |
| **Adoption** | 20 stars (Packt companion repository for the 2025 book) |
| **Last commit** | 2026-01-22 |
| **Links** | [repository](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset) · [benchmark](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_nearest_neighbor.cpp) |

## Verdict

The repository holds code only; the book's run, relayed by the seed lead, gives 4,797 ms for the sequential all-pairs loop and 1,161 ms with OpenMP on 8 threads over 65,536 random float points (about 4.1x), timed with Google Benchmark against the same author's single-threaded loop. Compiler, flags, OpenMP runtime and CPU model are not stated, and the repository's CMake sets no optimisation level.

## Use it when

- As a minimal template for parallelising an embarrassingly parallel outer loop that ends in a scalar min, max or sum reduction, in code that already builds with OpenMP.
- Brute-force all-pairs kernels on a few thousand to tens of thousands of points where writing a spatial index is not worth it; the min reduction is exact and order-independent, so the result is identical to the sequential loop.
- Teaching or measuring OpenMP scaling and load imbalance on a multi-core desktop, where the gap between 4.1x and 8x is itself the lesson.

## Skip it when

- Closest-pair search on large point sets: a divide-and-conquer or sweep-line closest-pair algorithm, or a uniform grid or k-d tree, is O(n log n), about a million steps at n = 65,536 against 2.1 billion pair checks here, which no thread count makes up for (derived).
- When you need the pair itself (the two indices); the functions return only the minimum distance.
- Toolchains without an OpenMP runtime: find_package(OpenMP REQUIRED) fails where none is installed (AppleClang does not ship one by default), and MSVC needs the experimental runtime that the CMake file selects for reduction(min).
- Code that already runs inside its own thread pool or several application threads: each call opens its own OpenMP team, so concurrent callers oversubscribe the cores.
- Small inputs: only 65,536 points are benchmarked, so the size below which thread start-up and the final barrier outweigh the gain is not documented.

## How it is fast

Plain fork-join thread parallelism: OpenMP splits the outer loop's rows across a team of threads (one per logical CPU by default), each thread keeps a private minimum, and the min reduction combines them at the end. The per-pair work is unchanged (one std::hypot call per pair) and the algorithm stays O(n^2). The rows are triangular (row i does n-i-1 pairs) and there is no schedule clause, so under the usual static schedule the first of 8 threads gets about 23% of all pairs, which caps the speedup near 4.3x (derived from the code); the reported 4.1x sits right at that cap.

## Compared with alternatives

None of the SIMD siblings (xsimd, Vc, NumKong) add threads; use this pattern when the kernel is already acceptable per element and idle cores are the cheapest win, and reach for NumKong or xsimd to speed up the per-pair arithmetic instead (the two combine; NumKong's distance kernels target long vectors rather than 2-D points).

## Integration

| | |
|---|---|
| **Form** | source-drop (two functions in Chapter-04/nearest_neighbor.cpp plus a short header; the speedup is a single pragma) |
| **Dependencies** | an OpenMP runtime (libgomp, LLVM libomp or MSVC's); the benchmark needs Google Benchmark, and the shared Chapter-04 CMake project also requires GTest and Threads at configure time (BLAS optional) |
| **Minimum toolchain** | C++20 (std::span; the benchmark's emplace_back on the aggregate Point2D needs parenthesised aggregate initialisation, GCC 10+ or Clang 16+), OpenMP 3.1+ for reduction(min), CMake 3.30+ as the CMakeLists requires |
| **Platforms** | any OS and CPU with an OpenMP-capable C++20 compiler; no ISA-specific code |
| **Thread safety** | Reentrant (reads a const span and returns a value), but every call starts an OpenMP parallel region; concurrent calls from several threads oversubscribe the cores, and calls nested inside another parallel region usually run with one thread. |
| **Drop-in for the baseline** | partial: same signature and the same result as nearest_neighbor_distance_seq, but the translation unit must be compiled with the OpenMP flag (-fopenmp, /openmp) and linked against the runtime; without it the pragma is ignored and the code runs sequentially. |

## Gotchas

- No schedule clause on a triangular loop: with the default static schedule thread 0 gets rows 0-8191, about 503 million of the 2.15 billion pairs, so 8 threads cannot exceed about 4.3x; schedule(dynamic, chunk), schedule(guided) or pairing row i with row n-1-i should balance the work (derived from the code, not measured).
- Each pair calls std::hypot, which guards against overflow and is slower than sqrt(dx\*dx + dy\*dy); comparing squared distances and taking one sqrt at the end lightens the inner loop for both versions and makes it a candidate for auto-vectorisation, so SIMD and threads could compound (derived, not measured).
- The benchmark does not call UseRealTime(); Google Benchmark's default CPU timer measures only the main thread, so read the wall-clock Time column for the OpenMP row. At 1-5 s per call the default 0.5 s minimum time is met after one iteration, so each figure is probably a single call unless --benchmark_repetitions was passed (derived from the Google Benchmark user guide).
- Chapter-04/CMakeLists.txt sets no CMAKE_BUILD_TYPE, so a plain configure builds without optimisation; configure Release to compare. Open PR #14 (December 2025, unmerged) fixes build errors in the same chapter's gemm files (a missing matrix.h include, asserts naming undeclared a, b, c), so build the bench_nearest_neighbor target on its own if the full project fails.

## Known shortcomings

- Repo has code only; the 4,797 vs 1,161 ms figures are the book's. No build type or -O level. The triangular loop has no schedule clause, so under the static default thread 0 gets 23.4% of the 2,147,450,880 pairs and the speedup caps near 4.27x: the reported 4.1x mostly reflects load imbalance (derived from page data). An OpenMP technique filed under a SIMD-style category, a loose fit.
- Enricher: static schedule on a triangular loop caps 8 threads near 4.27x; no UseRealTime() and each figure likely a single iteration; no build type in CMake; an O(n log n) closest-pair algorithm beats both versions.

## Caveats and trade-offs

The numbers are the book's own figures as paraphrased in the seed lead; they are not printed anywhere in the repository (the Chapter-04 listing shows 23 source and build files and no results), and the book itself was deliberately not consulted. Baseline is the book's own single-threaded loop, so this shows OpenMP scaling on a toy O(n^2) kernel, not an improvement on a library or std facility (nearest_neighbor.cpp includes &lt;execution&gt; but does not use parallel algorithms). The triangular loop uses '#pragma omp parallel for' with no schedule clause; under a static default schedule (libgomp's default) the first of 8 threads gets rows 0-8191, about 503 million of the 2,147,450,880 pairs (23.4%), which caps the speedup near 4.27x, so the reported 4.1x mostly reflects load imbalance and schedule(dynamic) or guided would likely scale further (derived from the code). Each pair calls std::hypot (about 2.2 ns per pair at 4,797 ms, derived); comparing squared distances would remove it from both versions. The sequential and OpenMP benchmarks generate separate random point sets from std::random_device on every run (work is data-independent, so the effect is small). Compiler, flags and CPU are not stated, so no tier A. Tier C: first-party book measurement. [retier] Enricher: a static schedule on the triangular pair loop gives thread 0 23.4% of the pairs, so 8 threads cap near 4.27x and the book's 4.1x sits at that cap (schedule(dynamic) or a balanced split would do better). The benchmark has no UseRealTime() and Google Benchmark's default CPU timer counts only the main thread; calls take 1-5 s, so with the default 0.5 s minimum time each figure is likely a single iteration. An O(n log n) closest-pair algorithm would beat both versions (about 1M steps against 2.1B pair checks, derived). CMake sets no build type (a plain build is unoptimised); open PR #14 fixes Chapter-04 gemm build errors, so building the whole chapter may fail.

Needs an OpenMP runtime and compiler support. The outer loop is triangular (iteration i does n-i-1 inner steps), so the default static schedule leaves the threads with unequal work (code reading); 4.1x on 8 threads is about 52% parallel efficiency. The O(n^2) algorithm is unchanged; a spatial index (k-d tree or grid) would change the complexity, which this record does not claim.

## Maintenance

Packt book companion repository, MIT-licensed, 20 stars and 8 forks; the last commit (2026-01-22) changed only the README and the code last changed in November 2025, with one open issue (#15, about the chapter-4 clamp loop) and one unmerged build-fix PR (#14); the technique is a single pragma, so there is nothing to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter-04/bench_nearest_neighbor.cpp times nearest_neighbor_distance_seq against nearest_neighbor_distance_omp (Google Benchmark, Arg(65536), milliseconds) on the same kernel, but the repo holds code only: the 4,797 ms and 1,161 ms figures appear nowhere in the repository and come from the book via the seed lead. Compiler, flags and CPU are not stated and CMakeLists.txt sets no build type, so first-party tier C.
- **Verifier notes:** Code verified: same kernel with and without 'omp parallel for reduction(min:...)', std::hypot on float Point2D, 65,536 points, Google Benchmark in ms; numbers not in the repo (book-only). MIT (Copyright 2025 Packt), 20 stars, 8 forks, last commit 2026-01-22 (active), not a fork, not archived. Category math-simd-linear-algebra is a loose fit; this is OpenMP thread parallelism.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-04>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_nearest_neighbor.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_nearest_neighbor.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/nearest_neighbor.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/nearest_neighbor.h>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-04>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues/15>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/pulls>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/pull/14/files>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_nearest_neighbor.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/nearest_neighbor.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/nearest_neighbor.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/open_mp_demo.cpp>
  - <https://raw.githubusercontent.com/google/benchmark/main/docs/user_guide.md>
  - <https://raw.githubusercontent.com/google/benchmark/main/src/benchmark.cc>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-cpp-programmers-mindset-openmp-nearest-neighbor`) · [data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_openmp_nearest_neighbor.json](../../../data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_openmp_nearest_neighbor.json) (enrichment confidence 0.7)

</details>
