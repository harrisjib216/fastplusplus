# Julia Base sort! in LilithHafner/InterLanguageSortingComparisons

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Julia` · `no license` · 🔴 abandoned

> Julia 1.9 Base sort! (LSD radix sort on Float64 bit patterns) timed against std::sort and qsort built at -O0; not a valid C++ comparison.

| | |
|---|---|
| **Beats** | C++ std::sort on std::vector&lt;double&gt; (src/script.cpp, Apple clang 13 under the g++ name) and C qsort with a comparator callback (src/script.c), same suite |
| **Claimed result** | data.txt at 3^14 = 4,782,969 elements, ns per element of sorting: Julia 1.9.0-beta3 35.1, Julia 1.8.5 92.5, C++ 207.6, C gcc 307.2, so Julia 1.9 is 5.9x and Julia 1.8 2.2x faster than C++ (derived from page data). README: 'Julia and Rust outperform other languages'. |
| **Workload** | Sorting-dominated workload: fill a vector of 3^i uniform random Float64 values, sort it, compute a dot product; the sorting time is inferred by subtracting a no-sort control run; ns per element for 3 to 3^15 elements. |
| **Metric** | throughput |
| **Hardware** | 2019 MacBook Air, 1.6 GHz dual-core Intel Core i5, 8 GB |
| **Compiler and flags** | Commands recorded in data.txt: C 'gcc script.c' and C++ 'g++ -std=c++11 script.cpp', both Apple LLVM 13.0.0 (clang-1300.0.27.3) with no -O flag (-O0); Julia 1.9.0-beta3 and 1.8.5 with default settings; Rust 1.67.0 'cargo run --release'. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Why it wins** | Not stated for C++; the README only says the benchmark isolates sorting speed. Julia's Base sort uses a different (radix-based) algorithm for Float64 at these sizes, inferred from the AcceleratedKernels README calling it a radix sort. |
| **Adoption** | 11 stars |
| **Last commit** | 2023-02-17 |
| **Links** | [repository](https://github.com/LilithHafner/InterLanguageSortingComparisons) · [benchmark](https://github.com/LilithHafner/InterLanguageSortingComparisons) |

## Verdict

On a 2019 MacBook Air (1.6 GHz dual-core i5), one trial per size, sorting 3^14 = 4,782,969 uniform Float64 values took 35.1 ns per element with Julia 1.9.0-beta3 (radix sort) and 92.5 with Julia 1.8.5 (QuickSort), against 207.6 for C++ std::sort and 307.2 for C qsort, both built by Apple clang 13 at -O0; Rust 1.67 sort_unstable_by at --release took 68.5 and glidesort 79.4. Only the Rust row is an optimized native comparison, and Julia 1.9 beats it by about 1.95x (derived from page data).

## Use it when

- You are already in Julia and sort large plain vectors of Float64, Float32 or machine integers (thousands to tens of millions of elements): default sort! picks radix sort with no code change; 35.1 ns per element at 4.78M doubles on a 1.6 GHz i5 in this run.
- As a hint for C++ work: a sort-bound step on large float or integer keys gains more from an LSD radix sort over the uint-mapped bit pattern than from tuning a comparison sort; on the same laptop Julia 1.9's radix sort was about 1.95x faster than Rust's release-built sort_unstable_by (35.1 vs 68.5 ns per element, derived from page data).
- When NaNs may appear: Julia's default sort! is defined for every Float64 (NaNs go to the end), while std::sort with operator&lt; on data containing NaN violates strict weak ordering (undefined behaviour, the repo's issue #9).
- As a starting harness for a fair re-run: the generate, sort, dot-product, subtract-control design is easy to port; fix the C and C++ build lines first.

## Skip it when

- As evidence that Julia beats optimized C++ std::sort: the C and C++ rows were built with 'gcc script.c' and 'g++ -std=c++11 script.cpp' (Apple clang 13, no -O flag, so -O0; plot.jl confirms the commands), while Rust used --release, so the 5.9x (Julia 1.9) and 2.2x (Julia 1.8) leads over C++ are mostly a build artifact.
- As a comparison-sort result: the gap is algorithmic (radix sort against introsort and qsort); the open issue #11 objects to exactly this reading, and the author replies that the repo only gives 'a rough idea of performance across languages'.
- For sorts with a custom lt, a by key, structs or strings: those inputs are not UIntMappable and fall back to ScratchQuickSort, so nothing here applies.
- When memory is tight: the radix path allocates an n-element scratch buffer (plus a 2^chunk_size count array) where std::sort is in place.
- Below a few hundred elements: radix sort is not chosen and the per-element numbers at 3^1 to 3^5 are dominated by noise and JIT effects (Julia 1.9 row 1 is 145.2 ns, including compilation).

## How it is fast

From Julia 1.9 the default sort for Float64 is no longer a comparison sort: IEEEFloatOptimization moves NaNs to the end, splits by sign and reinterprets the values as UInt64, then ConsiderRadixSort picks a stable least-significant-digit RadixSort when bits+70 &lt; 22\*log(n), after subtracting the minimum so fewer bits are radixed (base/sort.jl, v1.9.0-beta3 and still on master). For uniform [0,1) data that switch happens from about 3^6 = 729 elements; at 3^14 the range spans 57 bits, sorted in 6 counting passes of 10 bits with an n-element scratch buffer. Julia 1.8.5 still used an unstable QuickSort with integer comparisons, which is why its 92.5 ns per element at 3^14 trails Rust's optimized pdqsort-based sort_unstable_by (68.5 ns) in the same table.

## Compared with alternatives

Pick this only to learn which algorithm Julia's default Float64 sort uses and roughly how fast it is; for a Julia-versus-C++ sort measurement with optimized C++ builds the LangArena Sort::Self sibling (Julia 1.13 against std::sort at -O2 and -O3) is the better-evidenced entry, and the radix-versus-comparison confound applies there too.

## Integration

| | |
|---|---|
| **Form** | module (Julia Base; the benchmark repo itself is a set of standalone scripts) |
| **Dependencies** | none (Julia standard library Random for the benchmark's rand!) |
| **Minimum toolchain** | Julia 1.9 for the radix-sort default (measured on 1.9.0-beta3); Julia 1.8.5 uses QuickSort |
| **Platforms** | any platform Julia supports; measured only on an x86-64 macOS laptop |
| **Thread safety** | single-threaded; sort! mutates its argument in place, so concurrent calls need distinct vectors (not documented beyond that) |
| **Drop-in for the baseline** | partial — same role as std::sort for Julia code, but nothing callable from C++ without embedding Julia or porting base/sort.jl's RadixSort |

## Gotchas

- Crippled baseline: C and C++ were compiled at -O0 (no -O flag on Apple clang 13), while Rust ran cargo --release; the C++ figure is also not a sort time: script.cpp prints total runtime (allocation, generation, sort, dot product) times a fixed 0.85 because the author saw negative differences ('strange bug', issue #1), and it stops at 3^14 while other languages run to 3^15.
- script.cpp allocates a fresh std::vector&lt;double&gt;(n) and constructs a default-seeded std::default_random_engine for every repetition, so every repetition of one size sorts identical data and pays allocation and zero-fill inside the timed region; the C row times qsort through a function-pointer comparator compiled at -O0.
- Each data point is a single trial (README), on a dual-core laptop; the owner later said a reporter on a Xeon Gold 6254 measured Julia about 4x slower relative to clock than on her machine and guessed at slower memory bandwidth (issue #1), so radix-sort gains depend on cache and memory behaviour.
- No LICENSE file in the benchmark repo, so its scripts are reference only; Julia Base itself is MIT.

## Known shortcomings

- C and C++ rows built at -O0 (data.txt commands) and the C++ row is total time times 0.85 rather than sort time; no license; last commit 2023-02-17.
- The crippled -O0 C and C++ baselines are confirmed from the plot.jl build commands (Apple clang 13, no -O flag), and the C++ row is not even a sort time: script.cpp prints total runtime times a fixed 0.85 as the author's workaround for a 'strange bug' (issue #1), allocates a fresh vector and a default-seeded engine per repetition, and stops at 3^14. The only optimised native comparison on the page is Rust --release (pdqsort) 68.5 ns per element vs Julia 1.9 35.1 ns, about 1.95x (derived from page data); Julia 1.8.5's QuickSort (92.5 ns) is slower than Rust. Julia 1.9's Float64 sort is an LSD radix sort on uint-mapped bits from about 729 elements (six passes of 10 bits at 3^14), still the default in base/sort.jl on master. Open issues #9 (NaN undefined behaviour in std::sort) and #11 (radix-versus-comparison fairness).

## Caveats and trade-offs

Crippled baseline: the C and C++ programs were compiled without any optimization flag (-O0) while Rust used --release, so std::sort's templated comparisons run unoptimized and the 5.9x (Julia 1.9 vs C++) and 8.8x (Julia 1.9 vs C) figures are mostly a build artifact. The C++ figure is not a sort time: script.cpp prints total runtime (vector allocation, generation, sort and dot product) times a fixed 0.85 (comment says 0.8, label says 80%) instead of subtracting the no-sort control, and it stops at 3^14 (N = 14) while the other languages run to 3^15. script.cpp also constructs a fresh default-seeded std::default_random_engine for every vector, so all repetitions of one size sort identical data. The C row is qsort with a function-pointer comparator, a different algorithm from std::sort and from Julia's sort!. Each data point is a single trial (README says so). No LICENSE file (raw LICENSE and LICENSE.md requests returned 404; the repo page shows no license), so reference only. The repo owner works on Julia's Base sorting (general knowledge, not verified in this run), so the Julia side is close to first-party. A sorting-heavy workload rather than numerics proper. [retier] Enricher: the -O0 baselines are confirmed from the plot.jl build commands (Apple clang 13, no -O flag). The C++ row is not a sort time: script.cpp prints total runtime (allocation, generation, sort, dot product) times a fixed 0.85 as the author's workaround for a 'strange bug' (issue #1), allocates a fresh vector and a default-seeded engine per repetition, and stops at 3^14. The only optimised native comparison on the page is Rust --release (pdqsort) 68.5 ns per element vs Julia 1.9.0-beta3 35.1 ns, about 1.95x, while Julia 1.8.5's QuickSort (92.5 ns) is slower than Rust (derived from page data). Julia 1.9's Float64 sort is an LSD radix sort on uint-mapped bits from about 729 elements (six passes of 10 bits at 3^14), still the default in base/sort.jl on master. Open issues #9 (NaN undefined behaviour in std::sort) and #11 (radix-versus-comparison fairness).

Algorithm difference: the AcceleratedKernels.jl README calls Julia's Base CPU sort a radix sort, unlike std::sort's introsort and the C qsort comparator version; Julia JIT warm-up is not in the per-element numbers.

## Maintenance

Abandoned benchmark (last commit 2023-02-17, open issues on NaN undefined behaviour in the C++ script and on comparison-sort fairness, no license) kept as reference at tier D; the radix-sort default it showcases ships in every Julia release since 1.9 and is still the dispatch in base/sort.jl on master.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** data.txt records the C and C++ builds as 'gcc script.c' and 'g++ -std=c++11 script.cpp' with no -O flag (Apple clang 13, so -O0), so the C/C++ baselines are crippled; under the crippled-baseline precedent the Julia-vs-C++ ratios carry no valid language-level measurement, hence D.
- **Verifier notes:** Numbers verified in data.txt (row 14: Julia 1.9 35.1, Julia 1.8 92.5, C++ 207.6, C 307.2 ns per element). Downgrade C to D under the crippled-baseline precedent (C/C++ at -O0); keep with the shortcoming documented. Last commit 2023-02-17 is over 3 years old, so maintenance corrected to abandoned; 11 stars, no license confirmed.
- **Fields the verifier corrected:** `maintenance_status`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-39 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/commits/main>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/README.md>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/data.txt>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script.cpp>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script.c>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script.jl>
- **Sources the enricher read:**
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/tree/main/src>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/commits/main>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/README.md>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/data.txt>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/plot.jl>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script.cpp>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script.c>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script.jl>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script.py>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script_rs/src/main.rs>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/script_rs/Cargo.toml>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/src/glide_rs/Cargo.toml>
  - <https://raw.githubusercontent.com/LilithHafner/InterLanguageSortingComparisons/HEAD/LICENSE>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/issues?q=is%3Aissue>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/issues/1>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/issues/5>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/issues/9>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/issues/11>
  - <https://github.com/LilithHafner/InterLanguageSortingComparisons/pull/8>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.9.0-beta3/base/sort.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.8.5/base/sort.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/base/sort.jl>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/lilithhafner/interlanguagesortingcomparisons#sort-float64`) · [data/wave14/enrich/raw/lang_julia_lilithhafner_interlanguagesortingcomparisons_sort_float64.json](../../../data/wave14/enrich/raw/lang_julia_lilithhafner_interlanguagesortingcomparisons_sort_float64.json) (enrichment confidence 0.85)

</details>
