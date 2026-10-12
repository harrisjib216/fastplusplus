# fast_matrix_market (parallel Matrix Market sparse matrix I/O)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Parallel, full-format Matrix Market (.mtx) reader/writer; about 10x single-thread and 30x on 8 threads over IOStreams loaders.

| | |
|---|---|
| **Beats** | C++ IOStreams (std::istream/ostream) and scanf-based Matrix Market loaders; for the Python bindings, scipy.io.mmread/mmwrite before SciPy 1.12 |
| **Claimed result** | README: 'Reach &gt;1GB/s read and write speeds on a laptop (about 25x improvement over IOStreams).' Committed example output (benchmark_plots/benchmark_output_example/cpp-8-Core Apple M1 Pro Laptop.json, 2023-05-27): coordinate read 1578 MB/s at 8 threads (peak 1598 MB/s at 6) vs sequential IOStream 48.5 MB/s, about 32.5x; 1 thread 500 MB/s, about 10.3x. Coordinate write 691 MB/s at 8 threads vs IOStream 60.9 MB/s, about 11.3x; 1 thread 217 MB/s, about 3.6x. Array read 1477 MB/s and array write 1020 MB/s at 8 threads (ratios derived from page data). Python bindings read coordinate files at 1652 MB/s vs the old SciPy mmread at 51.0 MB/s. |
| **Workload** | Reading and writing Matrix Market sparse matrix files, thread-scaling plots on a laptop. |
| **Metric** | throughput |
| **Hardware** | 8-core Apple M1 Pro laptop (README plot titles and committed benchmark JSON) |
| **Compiler and flags** | run_benchmarks.sh: CMake -D CMAKE_BUILD_TYPE=Release; compiler not stated |
| **Adoption** | 91 stars; included as scipy.io.mmread and mmwrite from SciPy 1.12 per the README |
| **Last commit** | 2024-06-03 |
| **Links** | [repository](https://github.com/alugowski/fast_matrix_market) · [benchmark](https://github.com/alugowski/fast_matrix_market) |

## Verdict

First-party Google Benchmark (benchmark/fmm_bench via run_benchmarks.sh, CMake Release, compiler not stated) on an 8-core Apple M1 Pro: coordinate reads 1578 MB/s on 8 threads vs 48.5 MB/s for a sequential IOStreams loader (about 32x; about 10x on one thread); coordinate writes 691 MB/s vs 60.9 MB/s (about 11x; 3.6x on one thread). The README's '&gt;1 GB/s, about 25x' headline holds for reads and for array writes, not for coordinate writes.

## Use it when

- Loading multi-GB SuiteSparse or graph .mtx files into C++ where the existing loader (Eigen's loadMarket, hand-written scanf/IOStreams code) is the bottleneck
- Coordinate files with real/integer/complex/pattern fields read into std::vector-like triplets or CSC/CSR; the example output shows about 500 MB/s on one thread and about 1.6 GB/s on 8 threads on an M1 Pro
- Writing large sparse or dense results to .mtx, including CSC/CSR directly without a COO intermediate
- Python on SciPy older than 1.12, or when you need vector files, longdouble or direct CSR/CSC writes, which scipy.io.mmread lacks (pip or conda fast_matrix_market)
- Files SuiteSparse ships that partial loaders reject: array format, vector objects, skew-symmetric/hermitian, 64-bit indices

## Skip it when

- Small files where load time is already negligible; the gain only matters at hundreds of MB and up
- Binary formats would be faster still: if you control both ends, a binary sparse format avoids text parsing altogether
- Some paths fall back to sequential: bool value types, symmetric array files, and coordinate files read into dense handlers do not parallelize
- Toolchains without float std::from_chars and with fast_float disabled fall back to strtod, which the author's parse-bench shows serializing on the locale lock
- If you need an actively maintained dependency: last commit June 2024, PyPI wheels stop at CPython 3.12 (1.7.6, December 2023)

## How it is fast

Field conversion uses fast_float or C++17 std::from_chars for numbers and Dragonbox/Ryu or std::to_chars for writing, avoiding scanf/strtod/IOStreams, which also lock on the locale and get slower with threads. The main thread reads the stream in 2 MiB line-aligned chunks; a thread pool counts lines per chunk so each chunk's output offset (coordinate) or row/column start (array) is known, then parses chunks in parallel straight into presized output vectors. Bounded in-flight chunks give backpressure, and chunk buffers are reused to keep RSS down.

## Compared with alternatives

No sibling does the same job: the other sparse-and-solvers entries (merge-spmv, CSR5, AMGCL, Ginkgo) are kernels and solvers that need their input loaded first. Use this as their I/O front end when .mtx parsing dominates benchmark or pipeline start-up time.

## Integration

| | |
|---|---|
| **Form** | header-only (CMake INTERFACE target; header-only only when the optional fast_float, Dragonbox and Ryu dependencies are disabled) |
| **Dependencies** | C++11 threads; optional and on by default: fast_float, Dragonbox, Ryu (vendored under dependencies/); bundled task_thread_pool header. Eigen/GraphBLAS/CXSparse/Blaze/Armadillo only for their bindings |
| **Minimum toolchain** | C++17, CMake 3.14+; CI tests GCC 8 and 13, LLVM/Clang 8, MSVC and MinGW 13 (CMake probes for std::from_chars/std::to_chars support) |
| **Platforms** | any platform with C++17 and std::thread (CI: Linux, macOS, Windows; PyPI wheels for x86-64 and aarch64) |
| **Thread safety** | Each call uses its own thread pool, default std::thread::hardware_concurrency() threads (read_options.num_threads, parallel_ok); concurrent calls on separate streams are not documented |
| **Drop-in for the baseline** | partial: a replacement for scipy.io.mmread/mmwrite (the same functions in SciPy 1.12+) and for library loaders, but C++ callers switch to its free-function API with a std::istream |

## Gotchas

- Open output streams in binary mode; text mode on Windows writes CRLF line endings that other loaders may reject
- Symmetric files are expanded to general by default (generalize_symmetry=true); a diagonal entry gets an extra explicit zero (ExtraZeroElement) unless the app binding generalizes, so nnz can differ from what other loaders produce
- Output vectors are resized from the header's nnz before parsing, so a corrupt or hostile header can force a very large allocation before any error is raised
- Uses all hardware threads by default; set num_threads (C++) or parallelism (Python) inside already-parallel programs

## Known shortcomings

- Coordinate read \~32.5x over sequential IOStream at 8 threads but write only \~11.3x (691 MB/s); the '&gt;1GB/s write' claim holds for array files only; compiler unstated; edge of the sparse category (I/O, not compute).
- Presizes output from the header's nnz, so a bad or crafted header can force a huge allocation. Some paths run single-threaded (bool values, symmetric array files, coordinate files read into dense handlers). PyPI wheels stop at CPython 3.12.

## Caveats and trade-offs

This is sparse matrix file I/O, not a solver or kernel, so it is at the edge of the category. The IOStreams baseline is sequential by the author's choice (IOStreams slow down with threads because of locale locking), so most of the headline ratio is parallelism; single-thread gains are about 10x for reads and 3.6x for writes (derived from page data). '&gt;1GB/s write' holds for array files only; coordinate writes peak at 691 MB/s. Compiler and C++ standard library are not stated; the README's detailed comparison sits in the separate parse-bench repo, which was not opened.

Needs C++17 (uses std::from_chars, falls back to fast_float and Dragonbox); ready-made bindings for GraphBLAS, Eigen, CXSparse, Blaze and Armadillo; supports all Matrix Market fields and the array format.

## Maintenance

Stale since June 2024 (C++ header version 1.7.7, PyPI 1.7.6) but feature-complete, BSD-2-Clause and shipped inside SciPy 1.12+, so it is safe to vendor; open issues are build and packaging requests, not bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark run (benchmark/fmm_bench via run_benchmarks.sh, Release build) on an 8-core Apple M1 Pro laptop, with raw output committed in benchmark_plots/benchmark_output_example/; the compiler is not stated, so it falls short of A and stays C.
- **Verifier notes:** README claim quoted correctly; numbers behind the README plots are in the committed example JSON, so claimed_speedup now carries them. Metadata: BSD-2-Clause (LICENSE.txt), 91 stars, 290 commits, not archived or a fork, last commit 2024-06-03 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/alugowski/fast_matrix_market>
  - <https://github.com/alugowski/fast_matrix_market/commits>
  - <https://github.com/alugowski/fast_matrix_market/tree/main/benchmark_plots/benchmark_output_example>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/README.md>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/benchmark_plots/parallel-scaling-cpp-read.svg>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/benchmark_plots/parallel-scaling-cpp-write.svg>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/benchmark_plots/plot.ipynb>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/benchmark_plots/benchmark_output_example/cpp-8-Core%20Apple%20M1%20Pro%20Laptop.json>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/benchmark_plots/benchmark_output_example/python-8-Core%20Apple%20M1%20Pro%20Laptop.json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/README.md>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/README.Eigen.md>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/python/README.md>
  - <https://github.com/alugowski/fast_matrix_market/tree/main/include/fast_matrix_market>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/fast_matrix_market.hpp>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/types.hpp>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/chunking.hpp>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/read_body.hpp>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/read_body_threads.hpp>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/write_body_threads.hpp>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/field_conv.hpp>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/include/fast_matrix_market/app/triplet.hpp>
  - <https://github.com/alugowski/fast_matrix_market/issues>
  - <https://github.com/alugowski/fast_matrix_market/commits>
  - <https://pypi.org/pypi/fast-matrix-market/json>
  - <https://raw.githubusercontent.com/alugowski/parse-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/alugowski/fast_matrix_market/HEAD/.github/workflows/tests.yml>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/alugowski/fast_matrix_market`) · [data/wave8/enrich/raw/github_com_alugowski_fast_matrix_market.json](../../../data/wave8/enrich/raw/github_com_alugowski_fast_matrix_market.json) (enrichment confidence 0.8)

</details>
