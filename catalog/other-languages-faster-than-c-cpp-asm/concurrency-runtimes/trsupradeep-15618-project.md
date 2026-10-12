# Rayon vs OpenMP (CMU 15-618 project)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🔴 abandoned

> 2019 CMU course study timing Rust+Rayon against C++/OpenMP on four kernels; Rayon wins only large parallel stable sorts.

| | |
|---|---|
| **Beats** | C++ with OpenMP (and GNU parallel-mode sort) for Mandelbrot, matrix multiplication, sorting and reduction; C++ compiled with GCC per the report |
| **Claimed result** | Mixed; absolute times from data/Data.xlsx (best of three). Matmul 2048x2048, Rayon par_chunks row-dot vs OpenMP: Rust faster at 1, 2, 4, 6, 12 and 16 threads (12 threads 2168.8 vs 2864.5 ms, about 1.32x; 16 threads 2149.1 vs 2264.2 ms, about 1.05x, derived from page data) but slower at 8 threads (2501.7 vs 2277.6 ms) and serially (16277.1 vs 15509.5 ms); the report's 'Rayon performs better for all cases of threads for size 2048' is contradicted by its own 8-thread row, and its 'C++ is faster for all cases of threads for size 1024' by the 12-thread (272.4 vs 362.1 ms) and 16-thread (265.2 vs 285.7 ms) rows. These matmul comparisons are invalid (see caveats). Stable parallel sort, 100M elements: Rayon par_sort 1380 ms vs GNU parallel stable sort 1534.1 ms at 12 threads and 1226 vs 1476.2 ms at 16 threads (about 1.11x and 1.20x, derived from page data); C++ faster at 1 to 8 threads (8 threads 1690.0 vs 1834 ms) and serially (8467.6 vs 10908 ms). Unstable sort: Rust pdqsort/par_sort_unstable is faster in absolute time at every thread count (100M serial 3611 vs 7851.1 ms; 16 threads 684 vs 975.4 ms) although the report says C++ scales better; this is pdqsort vs introsort/multiway mergesort, an algorithm difference. Mandelbrot: C++ faster serially and Rust within about 1% multithreaded; quoted serial view 1 (4096x4096): Rust 19319.043 ms vs C++ 18813.754 ms, Rust 18758.684 ms after removing the num::Complex32 overhead. Reduction: Rust marginally faster serially (500M sum 456.5 vs 460.5 ms), OpenMP faster at every thread count. |
| **Workload** | Four shared-memory benchmarks written in Rust+Rayon and C++/OpenMP: Mandelbrot (2048 to 8192 square images, 7 views), integer matrix multiplication (1024 and 2048 square, all-ones inputs), stable and unstable sort of 1M, 10M and 100M random elements (Rust: uniform random u64 via par_sort/par_sort_unstable; C++: std::vector&lt;int&gt; via GNU parallel mode, source not committed), and sum/sum-of-squares reduction over 500M, 1B and 2B f64; best of three runs, threads 1 to 16. |
| **Metric** | throughput |
| **Compiler and flags** | From the committed binaries: Rust built with rustc 1.33.0 for x86_64-unknown-linux-musl (static musl); C++ sort built with GCC 4.8.5 on glibc. The C++ serial script uses an undefined \${serial_cc}. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Report: Rayon work stealing balances load and its merge sort was tuned (three merge variants benchmarked); for 2048x2048 matmul the unvectorized Rust inner loop keeps scaling longer and par_chunks avoids fork-join overhead. |
| **Adoption** | 56 stars |
| **Last commit** | 2019-11-01 |
| **Links** | [repository](https://github.com/trsupradeep/15618-project) · [benchmark](https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/project_docs/15618-Project-Final.pdf) |

## Verdict

Data.xlsx (best of three runs, unnamed x86-64 Linux machine, threads 1-16) shows Rayon 1.0.3 par_sort on 100M random u64 at 1380 ms with 12 threads and 1226 ms with 16, against 1534.1 and 1476.2 ms for GNU parallel-mode stable sort of 100M int built with g++ 4.8.5 -O3 (about 1.11x and 1.20x, derived from page data); C++ was faster at 1-8 threads and serially (8467.6 vs 10908 ms). The matmul 'wins' are invalid because the C++ kernel computes a different product, and OpenMP won every reduction.

## Use it when

- As a dated, qualitative reference on Rayon versus OpenMP ergonomics: parallel iterators that refuse to compile racy sharing versus pragmas (the report notes OpenMP segfaults during development).
- As a hint, to be re-measured on current versions, that a work-stealing parallel merge sort can out-scale libstdc++ parallel mode on 100M-element sorts at 12-16 threads.
- As teaching material on how decomposition (pixel versus row) and Rayon's adaptive splitting change speedup curves.
- Never as a dependency: adopt Rayon or OpenMP themselves.

## Skip it when

- As evidence that Rust/Rayon beats C++/OpenMP at matrix multiplication: the C++ kernels compute a different product (B indexed by row i), so those rows are not same-work.
- For reductions or embarrassingly parallel loops: OpenMP was faster at every thread count on the reductions, and Mandelbrot was C++-faster serially and within about 1% multithreaded.
- As a current comparison: Rayon 1.0.3, rustc 1.33.0 (2019-02-28) and GCC 4.8.5 (2015); Rust's std sorts and Rayon have since been rewritten, and open issue #1 (2024-08-12) asks for an update.
- As copyable code: the repository has no licence.
- When you need the hardware: the CPU model is never stated (thread sweep to 16, 'compute bound at 8 threads').

## How it is fast

Where Rayon comes out ahead it is the library algorithm, not the language: Rayon's par_sort is a parallel merge sort (rayon::slice::mergesort with par_merge) that reached 8.9x self-speedup at 16 threads on 100M u64, against 6.1x for GNU parallel mode's multiway mergesort (parallel_sort_mwms) on 100M int (derived from Data.xlsx). The serial unstable-sort lead is pdqsort (Rust sort_unstable) against introsort. Rayon's work-stealing join gives dynamic load balancing, but on uniform reductions OpenMP's static schedule won at every thread count. The authors attribute the matmul result to GCC vectorizing the inner loop while LLVM did not, but that comparison rests on a wrong C++ kernel (see gotchas).

## Compared with alternatives

NPB-Rust (GMAP) is the better-controlled Rayon-versus-OpenMP comparison (full NAS kernels against the group's own C++ port); use this repository only for its small-kernel observations and the single surviving data point, parallel stable sort at 12-16 threads.

## Integration

| | |
|---|---|
| **Form** | source-drop (benchmark programs, not a library) |
| **Dependencies** | Rust: rayon 1.0.3, clap 2.33, num 0.2, num_cpus 1.10, crossbeam 0.7, rand 0.6; C++: OpenMP (libgomp), libstdc++ parallel mode, CycleTimer.h |
| **Minimum toolchain** | rustc 1.33.0, edition 2018 (from the committed binaries); g++ -m64 -O3 -Wall -fopenmp (GCC 4.8.5 in the committed sort binary) |
| **Platforms** | x86-64 Linux (committed binaries); CPU not stated |
| **Thread safety** | not applicable (benchmark programs); the Rayon versions are data-race-free by construction |
| **Drop-in for the baseline** | no |

## Gotchas

- Matmul harness is broken on the C++ side: matmul_serial2 and matmul_par_row compute c += A[iOff + k] \* B[RM(k, i, size)], indexing B by the row i instead of the column j, so every j of a row re-reads one cache-resident column of B and the result is a different matrix; all-ones inputs and no result check hide it, while the Rust kernel walks B[index][col] correctly. The C++ 'par_outer' block calls matmul_par_row again without resetting minThread, and the C++ serial script passes an undefined \${serial_cc}, so those runs also execute both 16-thread parallel variants after the serial timing.
- New binary-level finding: the committed Rust binaries (rust/bin/quicksort-rust and mandelbrot-rust) are release builds by rustc 1.33.0 (2aa4c46cf 2019-02-28) for x86_64-unknown-linux-musl, statically linked against musl (musl malloc and memcpy) with Ubuntu 16.04 GCC 5.4.0 startup objects, while the C++ sort binary was built by GCC 4.8.5 (Red Hat 4.8.5-36) against glibc, so the two sides differ in libc and allocator. quicksort-rust contains rayon::slice::mergesort::par_mergesort but no rayon quicksort symbol, so its '[sort-unstable par]' loop runs the stable par_sort exactly as the committed source does; the Data.xlsx unstable-parallel numbers (for example 684 ms at 16 threads for 100M) cannot have come from the committed binary or source.
- Sort comparisons are uneven: Rust sorts Vec&lt;u64&gt; (8-byte keys) while the C++ binary sorts std::vector&lt;int&gt; (4-byte keys), which handicaps Rust; the C++ 'unstable' parallel path is also multiway mergesort (parallel_sort_mwms&lt;false&gt;), not quicksort; and the Rust serial times in Data.xlsx are one value (10908 ms stable, 3611 ms unstable for 100M) copied into every thread row.
- The report's prose overstates its data: 'Rayon performs better for all cases of threads for size 2048' fails at 8 threads (2501.7 vs 2277.6 ms), and its Mandelbrot time comparison (Figure 3) sets Rust pixel-parallel against C++ row-parallel, where the C++ pixel version uses schedule(static) and the row version schedule(dynamic).

## Known shortcomings

- Same harness flaws: Tokio 30.7 s vs the untuned libuv docs example 43.6 s in single runs from different dates with the cargo profile unstated, and it loses to Asio (29.5 s); tier D.
- From the committed binaries: Rust was built with rustc 1.33.0 for x86_64-unknown-linux-musl (static musl) while the C++ sort was built with GCC 4.8.5 on glibc; quicksort-rust has par_mergesort but no rayon quicksort symbol, so the Data.xlsx unstable-parallel numbers cannot come from the committed binary or source. The verifier's wrong C++ matmul kernel (B indexed by i) is confirmed, and the C++ serial script uses an undefined \${serial_cc}. Only the parallel stable sort at 12-16 threads stands.

## Caveats and trade-offs

Student course project (CMU 15-618, 2019): results are graphs inside a PDF plus raw timings in data/Data.xlsx; no hardware stated (threads swept to 16); no license file. Harness defects found in the committed code: (1) the C++ matmul kernels matmul_serial2 and matmul_par_row compute c += A[iOff + k] \* B[RM(k, i, size)], indexing B by the row i instead of the column j, so C++ computes a different (wrong) product whose B working set is a single cache-resident column per row, while the Rust kernel correctly walks B[index][col]; the bug is masked because A and B are all ones and the C++ result is never verified, so the matmul comparison is not same-work; (2) the C++ 'par_outer' timing block calls matmul_par_row again and never resets minThread, so the par_outer rows duplicate par_row; (3) the C++ sort source (C++/quicksort/main.cpp) is not committed, only a prebuilt ELF binary whose symbols show std::vector&lt;int&gt; (32-bit keys) sorted with __gnu_parallel multiway mergesort, while the Rust benchmark sorts Vec&lt;u64&gt; (64-bit keys), so element widths differ (against Rust); (4) the committed Rust sort code times stable_sort_par in its 'unstable parallel' loop (unstable_sort_par, typed &mut [u32], is never called) and prints fractional milliseconds, whereas Data.xlsx holds integer-millisecond Rust sort times that differ between stable and unstable, so the Rust sort numbers came from an earlier, uncommitted code version; correctness asserts are commented out; (5) Data.xlsx has copy errors (Rust Mandelbrot view 1 row-parallel row duplicates view 0). The Rayon matmul advantage the report explains (Rust not vectorizing the inner loop and hitting the compute limit later, par_chunks avoiding fork-join overhead) rests on the invalid kernel comparison. Sort compares different library algorithms (Rust stable merge sort and pdqsort vs GNU parallel multiway mergesort and introsort). Old toolchains: GCC 4.8.5 (2015) vs Rayon 1.0.3-era rustc (2019). [retier] quicksort-rust has par_mergesort but no rayon quicksort symbol, so the Data.xlsx unstable-parallel numbers cannot come from the committed binary or source; the wrong C++ matmul kernel (B indexed by i) is confirmed. Only the parallel stable sort at 12-16 threads stands.

Rayon work stealing adapts to uneven work but pays split and steal overhead; the report finds OpenMP static scheduling faster on reductions and Mandelbrot. Rust refuses to compile unsafe sharing between threads.

## Maintenance

Abandoned since 2019-11-01 (open issue #1 asks to update OpenMP and Rayon), no licence and 56 stars: a dated reference for reading, not code to copy, with harness defects (wrong C++ matmul kernel, Rust sort numbers not reproducible from the committed source or binary, musl-versus-glibc builds) that leave only the parallel stable-sort result standing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party student report (graphs; the only quoted timings, Mandelbrot view 1 Rust 19319.043 ms vs C++ 18813.754 ms and 18758.684 ms after the Complex32 fix, match) with raw timings in data/Data.xlsx and C++ Makefiles at g++ -m64 -O3 -fopenmp, but no CPU model, no Rust build flags or rustc version, the C++ sort source is not committed, and the matmul baseline kernel computes a different product; C at best.
- **Verifier notes:** Keep at tier C but the claim was overstated: the matmul win is invalid because the C++ kernel indexes B by row i (wrong, cache-friendlier product, masked by all-ones inputs), the report's 2048 'every thread count' claim fails at 8 threads, the C++ sort source is missing (binary only, 32-bit ints vs Rust u64), and the committed Rust sort code is not the version that produced the numbers. The only surviving Rayon-over-OpenMP result is stable parallel sort at 12-16 threads (about 1.11-1.20x at 100M, derived). Usability reference (no license), abandoned (last commit 2019-11-01).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-31 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/project_docs/15618-Project-Final.pdf>
  - <https://github.com/trsupradeep/15618-project>
  - <https://github.com/trsupradeep/15618-project/commits/master>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/README.md>
  - <https://github.com/trsupradeep/15618-project/tree/master/C++>
  - <https://github.com/trsupradeep/15618-project/tree/master/C++/quicksort>
  - <https://github.com/trsupradeep/15618-project/tree/master/rust>
  - <https://github.com/trsupradeep/15618-project/tree/master/scripts>
  - <https://github.com/trsupradeep/15618-project/tree/master/scripts/matmul>
  - <https://github.com/trsupradeep/15618-project/tree/master/data>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/data/Data.xlsx>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/mandelbrot/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/matrixmultiply/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/quicksort/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/reduction/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/quicksort/quicksort>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/matrixmultiply/main.cpp>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/matrixmultiply/src/main.rs>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/quick_sort/src/main.rs>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/matrixmultiply/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/quick_sort/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/reduction/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/mandelbrot/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/scripts/matmul/profile_matmul_rust_threads.sh>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/scripts/matmul/profile_matmul_c%2B%2B_threads.sh>
- **Sources the enricher read:**
  - <https://github.com/trsupradeep/15618-project>
  - <https://github.com/trsupradeep/15618-project/issues>
  - <https://github.com/trsupradeep/15618-project/tree/master/rust>
  - <https://github.com/trsupradeep/15618-project/tree/master/rust/bin>
  - <https://github.com/trsupradeep/15618-project/tree/master/scripts>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/README.md>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/project_docs/15618-Project-Final.pdf>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/data/Data.xlsx>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/matrixmultiply/main.cpp>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/matrixmultiply/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/reduction/main.cpp>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/reduction/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/mandelbrot/main.cpp>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/mandelbrot/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/quicksort/Makefile>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/C%2B%2B/quicksort/quicksort>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/bin/quicksort-rust>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/bin/mandelbrot-rust>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/matrixmultiply/src/main.rs>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/matrixmultiply/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/quick_sort/src/main.rs>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/quick_sort/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/reduction/src/main.rs>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/reduction/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/mandelbrot/src/main.rs>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/rust/mandelbrot/Cargo.toml>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/scripts/matmul/profile_matmul_rust_threads.sh>
  - <https://raw.githubusercontent.com/trsupradeep/15618-project/HEAD/scripts/matmul/profile_matmul_c%2B%2B_threads.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/trsupradeep/15618-project`) · [data/wave14/enrich/raw/github_com_trsupradeep_15618_project.json](../../../data/wave14/enrich/raw/github_com_trsupradeep_15618_project.json) (enrichment confidence 0.75)

</details>
