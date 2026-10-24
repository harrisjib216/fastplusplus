# Cache-blocked double-precision matrix multiply with tile accumulator (The C++ Programmer's Mindset, ch. 4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Teaching example: 32x32 cache-blocked scalar dgemm with a tile accumulator, about 1.9x faster than a naive triple loop.

| | |
|---|---|
| **Beats** | naive i-j-k triple-loop dgemm (dgemm_basic in the same repo, no blocking); OpenBLAS cblas_dgemm is measured as a reference and is far faster than the blocked code |
| **Claimed result** | Basic 547 ms, blocked (block size 32) 289 ms, OpenBLAS 24.1 ms per multiplication; blocked is about 1.9x faster than basic (derived), OpenBLAS about 12x faster than blocked and 23x faster than basic (derived); book figures as paraphrased in the seed lead, not on the repo page. Averages over 39 (basic), 73 (blocked) and 874 (OpenBLAS) iterations. |
| **Workload** | Dense square row-major double matrix multiply (alpha=1, beta=0), time per multiplication with Google Benchmark in ms; the repo's bench_gemm.cpp uses 1000x1000 matrices (the book shows the size only in an image); blocked variant uses block size 32 with a local tile accumulator. |
| **Metric** | latency |
| **Hardware** | Not stated. |
| **Compiler and flags** | Not stated. Chapter-04/CMakeLists.txt sets C++20 and no build type or optimisation level; it adds '-g -pg -fno-omit-frame-pointer' to the bench_gemm target only (bench_gemm.cpp, the driver), while dgemm_basic and dgemm_blocked are compiled in the separate static library target 'gemm' (gemm.cpp) without those options. gemm.cpp only compiles with NDEBUG defined (see caveats), which in CMake means a Release, RelWithDebInfo or MinSizeRel build. BLAS comes from CMake FindBLAS (static, 8-byte integers requested, cblas.h from /usr/include/openblas). |
| **Adoption** | 20 stars (Packt companion repository for the 2025 book) |
| **Last commit** | 2026-01-22 |
| **Links** | [repository](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset) · [benchmark](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_gemm.cpp) |

## Verdict

The book's own run, relayed by the seed lead and not recorded in the repo, reports 547 ms for the naive i-j-k loop, 289 ms for the 32x32 blocked kernel and 24.1 ms for OpenBLAS cblas_dgemm per 1000x1000 double multiply: about 1.9x for blocking and about 12x more for OpenBLAS (derived), or 0.55 ns and 0.29 ns per multiply-add for the two scalar kernels (derived). Compiler, build type, flags, OpenBLAS thread count and CPU are not stated.

## Use it when

- Learning or teaching cache blocking on a short, readable kernel before moving to BLIS/OpenBLAS-style packed micro-kernels.
- A dependency-free fallback dgemm in a small project that cannot link any BLAS, for square row-major double matrices from a few hundred to a few thousand elements per side.
- A simple reference or starting point for your own tiled kernel, applying the same tile-and-accumulate pattern to other loop nests whose working set exceeds L1.

## Skip it when

- Any production matrix multiply: the relayed OpenBLAS figure (24.1 ms against 289 ms) is about 12x faster again; use OpenBLAS, MKL, BLIS or Eigen.
- Non-square inputs: both kernels bound the k loop by B.cols() instead of A.cols(), and dgemm_basic also bounds j by A.cols(), so results are only correct when A.cols() == B.cols(); check_dimensions validates shapes but the loops do not follow them.
- Column-major or transposed operands: only row-major is handled, and the asserts that would catch other orders are compiled out in any NDEBUG build.
- Multicore or SIMD throughput needs: the code is single-threaded scalar C++ with no packing, so power-of-two sizes such as 1024, where the 32 B rows in a tile sit 8 KB apart and share a few L1 sets, may lose much of the blocking gain (not measured).

## How it is fast

Loop tiling (cache blocking): C is computed in 32x32 tiles, and for each k block the 32x32 slices of A and B (8 KB each) plus an 8 KB tile accumulator fit in L1 together, so each loaded line of B is reused across the whole tile instead of B being streamed column-wise from L2 or memory for every element of C. Inside a tile the source still walks i-j-k with B read down columns, but it accumulates into the tile array rather than a scalar, which makes the inner loops a perfect nest that a compiler may interchange and vectorise (GCC enables -floop-interchange at -O3, and its documented example is this matmul nest). The relayed 289 ms is about 0.29 ns per multiply-add (derived), below one floating-point add latency at desktop clock speeds, so the book's blocked build very likely did not run the source's serial k-loop as written; part of the 1.9x is probably compiler restructuring rather than tiling alone (inference, not checked by compiling).

## Compared with alternatives

No catalogued sibling is a CPU GEMM: the category holds SIMD and math-function libraries (xsimd, Vc, SLEEF) and sibling examples from the same book (SAXPY multiversioning, OpenMP nearest neighbour). Read this one to learn CPU cache tiling; the GPU Programming with C++ and CUDA shared-memory tiled matrix multiply is the GPU analogue, and for real workloads a BLAS beats both.

## Integration

| | |
|---|---|
| **Form** | source-drop (gemm.cpp with matrix_view.h and matrix.h; the chapter's CMake builds them as static library 'gemm') |
| **Dependencies** | none for the kernels (C++ standard library); bench_gemm needs Google Benchmark and optionally a CBLAS found by CMake FindBLAS; the chapter CMakeLists.txt also requires GTest, OpenMP and Threads at configure time |
| **Minimum toolchain** | C++20 (matrix_view.h includes &lt;ranges&gt; and &lt;span&gt;; matrix.h uses aligned operator new), CMake 3.30+ |
| **Platforms** | any for the portable scalar kernels; the platform used for the book's numbers is not documented |
| **Thread safety** | not documented; the kernels keep no shared state (the tile buffer is a local Matrix), so concurrent calls writing distinct output matrices look safe by inspection |
| **Drop-in for the baseline** | partial — same ct::MatrixView signature as dgemm_basic plus a block_size argument; not a drop-in for cblas_dgemm (no transpose flags, leading dimensions or column-major order) |

## Gotchas

- As committed (HEAD, and unchanged since commit 0be92ac of May 2025), bench_gemm.cpp and test_gemm.cpp use ct::Matrix but include only gemm.h, which pulls in matrix_view.h and not matrix.h, so neither compiles without adding #include "matrix.h"; gemm.cpp's dgemm_blocked also asserts on lowercase a, b, c that do not exist, so it compiles only with NDEBUG. The book's run therefore used code or a build that the repo does not record.
- The benchmark never writes matrix a (ct::Matrix only default-initialises its doubles), so every product is zero; on Linux, untouched fresh allocations read as the kernel's shared zero page, so A may occupy almost no physical cache footprint, and whether a is fresh or recycled heap memory can differ between benchmark runs. Fill every input before timing.
- The only correctness test compares blocked against basic on square 250x250 all-ones matrices with block 64, which cannot expose the k-bound bug for non-square shapes and makes summation order irrelevant.
- The ratio is likely compiler-dependent: GCC turns on -floop-interchange at -O3, while Clang left loop interchange off by default until an August 2026 LLVM change (per search snippets), and the repo pins neither compiler nor build type.

## Known shortcomings

- Book numbers only. -g -pg -fno-omit-frame-pointer are set on bench_gemm.cpp only (kernels in an uninstrumented static library); OpenBLAS threads not limited, so the 24.1 ms (about 83 GFLOP/s, derived from page data) baseline may be multithreaded; non-default min_time (about 21 s per benchmark, derived).
- Enricher: the committed bench and test do not compile (missing matrix.h include), so the book ran code the repo lacks; kernels are correct only when A.cols() == B.cols(); input matrix a never written (all products zero, possible zero-page reads); 0.29 ns per multiply-add implies compiler loop interchange or vectorisation, so the ratio is compiler-dependent.

## Caveats and trade-offs

The numbers are the book's own figures as paraphrased in the seed lead; they are not printed anywhere on the repository pages opened (the repo holds the benchmark code and no results, and the Chapter-04 folder has no results files), and the book itself was deliberately not consulted. The only baseline beaten is the book's own naive loop; against the real incumbent (OpenBLAS) the technique is about 12x slower. The -pg/-fno-omit-frame-pointer options apply only to bench_gemm.cpp, not to the gemm library that holds both kernels, so the kernels are not gprof-instrumented. Matrix 'a' is never filled: ct::Matrix uses std::uninitialized_default_construct_n, so its doubles are indeterminate (zero if the allocation came fresh from the OS; leftover data otherwise). dgemm_blocked contains assert(a.is_row_major()) with lowercase names that do not exist, so gemm.cpp only compiles with assertions disabled (NDEBUG), i.e. a Release-type build. Within each 32x32 tile the loop order is still i-j-k with B read down columns; the gain comes from tile reuse in L1, not from a reordered inner loop. The harness does not limit OpenBLAS threads: 24.1 ms for 2e9 flops is about 83 GFLOP/s (derived from the lead's figures), at or above the FP64 peak of one desktop core, so the OpenBLAS row may be multithreaded against single-threaded kernels. The quoted iteration counts times the per-iteration times give about 21 s per benchmark (derived), so the book's run used a non-default --benchmark_min_time or similar that the repo does not record. Compiler and CPU not stated. Tier C: first-party book measurement. [retier] Enricher: bench_gemm.cpp and test_gemm.cpp use ct::Matrix but never include matrix.h, so neither compiles as committed (HEAD and 0be92ac, May 2025). Both kernels bound k by B.cols() and the basic kernel bounds j by A.cols(), so results are correct only when A.cols() == B.cols(); the only test (square 250x250 all-ones) cannot catch this. Matrix a is never written, so every product is zero, and untouched fresh memory on Linux may read as the shared zero page, which can differ between runs. 289 ms is 0.29 ns per multiply-add (derived), below one floating-point add latency, so the blocked build likely got loop interchange or vectorisation (GCC -floop-interchange at -O3), which contradicts the earlier note that the gain is tile reuse alone; the ratio is likely compiler-dependent (inference, not compiled).

Teaching-level blocking only: scalar inner loops, no packing, no SIMD, no threading. It is not a replacement for OpenBLAS, MKL, BLIS or Eigen, which are an order of magnitude faster in the book's own numbers.

## Maintenance

Active Packt companion repo for the 2025 book (last commit 2026-01-22, 20 stars, Chapter-04 last touched by a 2025-11-08 reformat), MIT-licensed; the kernels are about 100 lines and easy to copy, but fix the missing matrix.h include, the lowercase asserts and the k-loop bound before reuse.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter-04/bench_gemm.cpp times dgemm_basic, dgemm_blocked (block 32) and cblas_dgemm on 1000x1000 doubles with Google Benchmark, but the repo holds code only; the 547/289/24.1 ms figures are the book's own run relayed by the lead, with compiler, flags and CPU unstated, so first-party C.
- **Verifier notes:** Source matches the record (1000x1000, block 32, alpha 1, beta 0, uninitialised 'a', broken lowercase asserts). Corrected the -pg caveat: it is set on bench_gemm.cpp only, and the kernels live in the separate 'gemm' static library. Added OpenBLAS threading and min_time observations. Metadata confirmed: MIT, 20 stars, last commit 2026-01-22 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_gemm.cpp>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-04>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_gemm.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/gemm.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/gemm.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/matrix.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_gemm.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/gemm.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/gemm.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/matrix.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/matrix_view.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/test_gemm.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/0be92ac/Chapter-04/bench_gemm.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/0be92ac/Chapter-04/gemm.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/0be92ac/Chapter-04/gemm.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/0be92ac/Chapter-04/test_gemm.cpp>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main/Chapter-04>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues?q=is%3Aissue>
  - https://gcc.gnu.org/ml/gcc-patches/2017-12/msg00360.html (search snippet only)
  - https://lists.llvm.org/pipermail/flang-commits/2026-August/084328.html (search snippet only)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-cpp-programmers-mindset-cache-blocked-gemm`) · [data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_cache_blocked_gemm.json](../../../data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_cache_blocked_gemm.json) (enrichment confidence 0.6)

</details>
