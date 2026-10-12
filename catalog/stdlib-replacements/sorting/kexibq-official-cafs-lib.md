# CAFS (cache-aware frequency sort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only AVX2 hash-count sort for integer vectors with few distinct values; beats pdqsort, IPS4o and vqsort while K stays far below N.

| | |
|---|---|
| **Beats** | vqsort (Google Highway), std::sort, pdqsort, IPS4o, ska_sort |
| **Claimed result** | Bin-mean speedup 1.7-3.1x vs pdqsort, 1.97-3.52x vs IPS4o, 1.27-2.34x vs vqsort, 4-17x vs ska_sort and 8-17x vs std::sort across the K &lt;&lt; N band (README table, K = 4 to 8 distinct values: std::sort 17.10x, ska_sort 16.96x, IPS4o 3.50x, pdqsort 3.10x, vqsort 1.32x). It loses where K approaches N: bin-mean 0.60 vs vqsort and 0.66 vs ska_sort for K of 8.4e6 to 1.7e7, and the README says vqsort wins by 1.5 to 2 times beyond K = 6.7e5. |
| **Workload** | Sorting integer arrays with N elements and K distinct values over a 1600-point (N, K) grid, 592,770 measurements, AVX2 hot loop (one cmpeq per element on 64-byte buckets). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-12400F, 32 GB DDR4-3200 |
| **Compiler and flags** | g++ 13.2 -O3 -mavx2 -mbmi -DNDEBUG (Windows 11); benchmark/main_bigdata.cpp in the repo |
| **Adoption** | 32 stars |
| **Last commit** | 2026-08-07 |
| **Links** | [repository](https://github.com/kexibq-official/cafs-lib) · [benchmark](https://github.com/kexibq-official/cafs-lib) |

## Verdict

Author-run grid on an Intel Core i5-12400F under Windows 11 (g++ 13.2 -O3 -mavx2 -mbmi, libstdc++ std::sort, vqsort on its AVX2 path): uint64 keys drawn uniformly from K-value palettes, N from 1,000 to 3e7, best of 2 runs per point, with CAFS using a pdqsort fallback. Bin-mean speedups are 17.1x std::sort, 3.1x pdqsort and 1.32x vqsort at K = 4-8, still 1.59x vqsort at K of about 1e4, and fall to 0.60x vqsort and 0.66x ska_sort near K = N; every output is checked against std::sort, so the timings are of real sorts.

## Use it when

- Large (N of 1e5 and up) uint64, int64 or int32 columns with K far below N: dictionary-encoded or categorical fields, foreign keys into small dimension tables, bucketed numeric features; the README bins show 1.27-2.34x vqsort and 2.1-3.1x pdqsort for K up to about 16,384
- Arrays with 8 or fewer distinct values, where the single counting pass measured 17.1x libstdc++ std::sort and 3.1x pdqsort
- x86-64 machines with AVX2 but no AVX-512 (the measured i5-12400F class), where vqsort is also limited to its AVX2 path
- Cases where only the sorted integers are needed (no satellite data) and you can pass pdqsort as the fallback so high-cardinality inputs degrade to pdqsort speed rather than std::sort

## Skip it when

- K that may approach N: for N above 1e6 vqsort wins by 1.5-2x past K of about 6.7e5, ska_sort wins past 8.1e5, and the worst case seen in the grid was about 5x pdqsort time
- Sorting records, key-value pairs, floats, custom orders or anything other than a std::vector of integers: output is regenerated from counts, so it cannot carry payloads or act as a general std::sort replacement
- Non-x86 or pre-AVX2 targets: there is no runtime dispatch (binaries built with -mavx2 fault on older CPUs), and &lt;immintrin.h&gt; is included unconditionally, so the header does not build on ARM even for types that use the scalar bucket path
- Memory-tight code: the table holds about two 64-byte buckets per estimated distinct key, capped at bit_ceil(N/4) buckets (up to about twice the size of a u64 input), plus the spill vector, the (key, count) array and a radix buffer
- Production code that needs a track record: one author, 7 commits between 2026-05-09 and 2026-08-07, no releases, no filed issues, all numbers from one Windows desktop, and the preprint is not peer reviewed

## How it is fast

A dispatcher first returns early on already-sorted input (and reverses non-increasing input), then estimates K with the Chao1 estimator over 1024 strided samples. For K of 8 or fewer it makes one branchless pass counting matches against eight candidate keys; otherwise each run of equal values is hashed (Fibonacci multiplicative hash) into a table of 64-byte, cache-line-aligned buckets (4 u64/i64 or 8 i32 keys plus 32-bit counts) probed with one AVX2 cmpeq plus movemask, sized to about 8 slots per estimated key. Keys that find their bucket full go to a spill vector sorted with std::sort; the distinct (key, count) pairs are LSD-radix-sorted and expanded with fill_n, so the work is O(N + K) instead of O(N log N). If the sample looks all-unique, K_est \* 2 &gt; N, or the spill exceeds N/2, the input goes to the fallback.

## Compared with alternatives

Pick CAFS over vqsort, pdqsort, IPS4o or ska_sort only for integer-only sorts on AVX2 hardware where K is known to stay well below about 1e5 (the pdqsort crossover) to 6.7e5 (the vqsort crossover). Pick vqsort (Highway) when K may approach N or you need AVX-512, NEON or SVE dispatch, and pdqsort for portable general-purpose sorting; no comparison with x86-simd-sort exists.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library (include/cafs.hpp and include/cafs2.hpp); the benchmark needs pdqsort.h and optionally ska_sort, IPS4o (with TBB headers or stubs) and Google Highway |
| **Minimum toolchain** | C++20 (std::bit_ceil, std::bit_width, std::countr_zero); g++ 13+ or clang 16+ per the README; MSVC not documented |
| **Platforms** | x86-64 with AVX2 and BMI1 only (compile with -mavx2 -mbmi); Windows (_aligned_malloc) and POSIX (std::aligned_alloc) allocation paths |
| **Thread safety** | not documented; each call allocates its own table and touches only the vector passed in, so concurrent calls on different vectors look safe from the code; the sort itself is single-threaded |
| **Drop-in for the baseline** | partial — replaces std::sort(v.begin(), v.end()) on a std::vector of integers in ascending order only; no iterator, comparator or payload interface |

## Gotchas

- The default fallback is std::sort, but the benchmark passes pdqsort (main_bigdata.cpp), and the C, Python, Rust and Go bindings call the default. Past the dispatcher's cutoff the measured CAFS is pdqsort (bin-mean 1.00), whereas default and binding users get std::sort, which the same table puts 3.47x slower in the K = 8.4e6-1.7e7 bin (derived from page data). Pass pdqsort or vqsort as the fallback explicitly.
- Harness gaps found this session: competitors.hpp implements dense_map_sort (count with ankerl::unordered_dense, sort the distinct keys, expand), which is the plain hash-count-sort that CAFS's technique should be compared against, and Boost spreadsort, but main_bigdata.cpp never registers either, so the published table only pits an O(N + K log K) histogram method against comparison and radix sorts. The 592,770 rows are exactly the driver's default grid truncated at N = 3e7 (98,795 (N, K) cases x 6 algorithms over 58 sizes, best of 2 each; the preprint abstract, seen as a search snippet, also says 58 sizes), not a 1600-point grid, so the 3.5e7-1e8 sizes were not part of the published run. The heatmap script silently drops rows whose output check failed and the CSV is unpublished, so FAIL rows cannot be ruled out.
- The K estimate reads every (N/1024)-th element, so periodic inputs alias: with N = 1,048,576 and data[i] = key[i % 1024] the sample sees one value, the table is sized at its 8-bucket minimum (32 slots), about 97% of the elements are pushed into a spill vector reserved for 8, and the fallback then sorts everything anyway (read from the code, not run). Skewed (Zipf-like) inputs were not benchmarked; every grid point draws keys uniformly from the palette.
- Hashing is a bare Fibonacci multiply into 4-slot buckets with no rehash, and spilled keys are sorted with std::sort rather than the fallback. My Python simulation of the table fill with the benchmark's own arithmetic-progression palette at K = 100,000 spilled 4,635 keys against 18 for random 64-bit keys, so structured key sets can spill far more than the measured ones. Counts are 32-bit (wraps only past 2^32 copies of one value), and the older cafs::cafs_sort entry point in cafs.hpp, still reachable through cafs2.hpp, returns with the data unsorted if its table allocation fails.

## Known shortcomings

- One Windows i5-12400F box, best of 2 runs, raw CSV not in the repo; the README contradicts itself on the std::sort crossover (parity at K=1.7e7 vs 3.47x in the table); slower than vqsort (0.60x) and ska_sort (0.66x) near K=N; the bench checks sort output. Filed under sorting.
- Harness gaps: the benchmark passes a pdqsort fallback while the default and all bindings fall back to std::sort, about 3.47x slower near K = N (derived); competitors.hpp implements dense_map_sort (hash-count sort, the natural comparator) and Boost spreadsort, but main_bigdata.cpp never registers them. The 592,770 rows are exactly the default grid cut at N = 3e7 (98,795 cases x 6 algorithms over 58 sizes), not a '1600-point grid'; the heatmap script drops FAIL rows. The strided 1024-sample K estimate aliases on periodic input; with the benchmark's own arithmetic-progression palette the 4-slot buckets spilled 4,635 keys at K = 1e5 against 18 for random keys (enricher simulation).

## Caveats and trade-offs

Very new single-author repo (7 commits, 2026-05-09 to 2026-08-07, 32 stars); all numbers from one Windows 11 desktop (i5-12400F, AVX2 path only, no AVX-512 run of vqsort). std::sort is libstdc++ (inferred from the g++ 13.2 toolchain; the README does not name the library). Timings are best of 2 runs per (N, K) point with high_resolution_clock, on uint64 keys drawn from a K-value palette spread over the 64-bit range; only the u64 path is benchmarked although int32/int64 specializations exist. The raw CSV is not in the repo (README says it ships with the preprint artifact); arXiv 2605.25040 exists (seen via a search snippet only, arXiv blocked) and is not peer reviewed. The README is internally inconsistent about std::sort: its crossover line says std::sort reaches parity at K = 1.7e7, while the table shows 3.47x for that bin and the operational table says CAFS still wins at K = N. CAFS loses to vqsort (0.60x) and ska_sort (0.66x) near K = N, and the dispatcher's worst case is about 5x pdqsort time. A 'signed-radix fix' landed on 2026-05-09 but does not touch the u64 path measured. This is a sorting library; it fits the existing 'sorting' category better than simd-intrinsics-libraries. [retier] Very new single-author repo (7 commits, 2026-05-09 to 2026-08-07, 32 stars); all numbers from one Windows 11 desktop (i5-12400F, AVX2 path only, no AVX-512 run of vqsort); std::sort is libstdc++ (inferred from g++ 13.2). Timings are best of 2 runs per (N, K) point with high_resolution_clock on uint64 keys drawn uniformly from a K-value palette spread over the 64-bit range; the 592,770 rows are the driver's default grid cut at N = 3e7 (98,795 (N, K) cases x 6 algorithms over 58 sizes), the heatmap script drops FAIL rows, and the raw CSV is not in the repo. Harness gaps: main_bigdata.cpp passes pdqsort as the CAFS fallback while the default and the C, Python, Rust and Go bindings fall back to std::sort, which the same table puts about 3.47x slower in the K = 8.4e6-1.7e7 bin (derived from page data), so default users past the dispatcher's cutoff get a slower sort than the one measured; competitors.hpp implements dense_map_sort (hash-count sort with ankerl::unordered_dense, the plain technique CAFS should be compared against) and Boost spreadsort, but neither is registered, so the table only pits an O(N + K log K) histogram method against comparison and radix sorts. The K estimate reads every (N/1024)-th element, so periodic inputs alias (N = 1,048,576 with data[i] = key[i % 1024] sizes the table at its minimum and spills about 97% of elements); skewed inputs were not benchmarked; the 4-slot Fibonacci-hash buckets have no rehash, and an enricher simulation with the benchmark's own arithmetic-progression palette at K = 100,000 spilled 4,635 keys against 18 for random keys. arXiv 2605.25040 is not peer reviewed; the README is internally inconsistent about std::sort parity at K = 1.7e7. Only the u64 path is benchmarked.

Header-only C++20, x86-64 with AVX2 and BMI only; targets integer columns with few distinct values; an adaptive dispatcher falls back to pdqsort for high-entropy input (worst case observed about 5x pdqsort time). Primarily a sorting algorithm that uses SIMD, so it may belong with the sorting lists.

## Maintenance

Active but young (single author, 7 commits from 2026-05-09 to 2026-08-07, 32 stars, no releases or issues); MIT and two small headers, so easy to vendor, best used behind your own K check with an explicit pdqsort or vqsort fallback.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README 'Benchmark results' table gives bin-mean speedups vs std::sort, pdqsort, ska_sort, IPS4o and vqsort produced by the public driver benchmark/main_bigdata.cpp (with competitors.hpp, datagen.hpp, bench_engine.hpp and benchmark/CMakeLists.txt), and states g++ 13.2, -O3 -mavx2 -mbmi -DNDEBUG and Intel Core i5-12400F. The driver checks every run's output against a std::sort reference and logs an ok/FAIL column, so the timings are of real sorts.
- **Verifier notes:** Numbers match the README table exactly; benchmark code is public, verifies correctness and uses fair std::function wrappers for every algorithm. Shortcomings: one desktop CPU, best of 2 runs, raw CSV not published, README contradicts itself on the std::sort crossover, slower than vqsort and ska_sort when K approaches N. Suggest a category override to 'sorting'.
- **Fields the verifier corrected:** `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** verifier batch-24 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/kexibq-official/cafs-lib>
  - <https://github.com/kexibq-official/cafs-lib/commits>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/README.md>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/main_bigdata.cpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/competitors.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/bench_engine.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/datagen.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/third_party/README.md>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/include/cafs2.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/tests/sanity.cpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/kexibq-official/cafs-lib>
  - <https://github.com/kexibq-official/cafs-lib/commits>
  - <https://github.com/kexibq-official/cafs-lib/commit/e863f42>
  - <https://github.com/kexibq-official/cafs-lib/issues?q=is%3Aissue>
  - <https://github.com/kexibq-official/cafs-lib/tree/main/bindings>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/README.md>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/include/cafs2.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/include/cafs.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/main_bigdata.cpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/competitors.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/bench_engine.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/datagen.hpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/benchmark/third_party/README.md>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/tests/sanity.cpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/bindings/README.md>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/bindings/c/cafs_c.cpp>
  - <https://raw.githubusercontent.com/kexibq-official/cafs-lib/HEAD/analysis/heatmap_v2.py>
  - https://arxiv.org/pdf/2605.25040 (WebSearch snippet only; arXiv blocked)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/kexibq-official/cafs-lib`) · [data/wave13/enrich/raw/github_com_kexibq_official_cafs_lib.json](../../../data/wave13/enrich/raw/github_com_kexibq_official_cafs_lib.json) (enrichment confidence 0.8)

</details>
