# Julia 1.13: LangArena Sort::Self (built-in sort vs std::sort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia's default sort! on Int32 radix-sorts a 400k-element array 8.5x faster than C++ std::sort in LangArena Sort::Self.

| | |
|---|---|
| **Beats** | std::sort on std::vector&lt;int32_t&gt; (g++ 16, clang++ 22); best C/C++ configuration is C++/G++ prod at 0.982 s |
| **Claimed result** | Julia/Default 0.116 s vs C++/G++ 0.982 s (prod -O2, also the best of the 16 gcc/clang C and C++ configurations), C++/G++/Fast at -O3 0.998 s and C++/Clang++ 1.022 s: about 8.5x (derived from page data). Java/OpenJDK at 0.187 s is about 5.3x faster than std::sort (derived). C# Array.Sort at 1.057 s is slightly slower. The C rows use qsort with a comparison callback (best C/mycc/LLVM/Default 1.957 s, C/Gcc/Fast 1.964 s). The timed loop is 50 sorts of a copied 400,000-element array after 10 untimed warm-up sorts. The suite's same-algorithm sorts show no managed-runtime win: Sort::Quick Julia/Default 1.307 s vs C/Gcc 1.15 s, and Sort::Merge Julia/Default 1.602 s vs C/Clang 1.09 s. |
| **Workload** | Copy a large array of random 32-bit integers and sort it with each language's built-in sort (std::sort, Arrays.sort, Julia sort!). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++ (cpp/Makefile, c/Makefile; versions from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk, Ubuntu package build), libstdc++ (no -stdlib flag). 'prod' (headline rows): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, -std=c++20 for C++. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use (GCC). -flto=thin (Fast) and -flto=full (Unsafe) are passed only on the link line (LDFLAGS) while objects are compiled without -flto, so no link-time optimisation actually takes place. Managed side: dotnet 11.0.100-rc.1.26425.128, 'dotnet build -c Release' (Optimize=true) run as 'dotnet Benchmark.dll' with default tiered JIT; the C#/AOT rows are NativeAOT with IlcInstructionSet=native and IlcOptimizationPreference=Speed; Julia 1.13.1 run as 'julia --project=. --threads=16 benchmark.jl' (Julia/Max adds -O3 --check-bounds=no --math-mode=fast); Temurin OpenJDK 27+35 run as 'java -Xmx2g -jar'. Every language, C and C++ included, runs untimed warm-up iterations (20 percent of the timed count) before the timed loop. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | The suite's own docs/ai_analysis.js says Julia specializes sort! on Int32 at run time and picks a radix or counting sort (O(n)), and docs/ai_critic.js says this is the standard library choosing a better algorithm for the data type, not the language being faster ('You're comparing algorithms, not languages'). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

On an AMD Ryzen 7 3800X (LangArena results 2026-10-05, one run per configuration), 50 sorts of a copied 400,000-element Int32 array take 0.116 s with Julia 1.13.1's default sort! against 0.982 s with g++ 16.0.1 -O2 std::sort, the best of the 16 C/C++ configurations: about 8.5x (derived from page data). C's qsort-with-callback rows take 1.96-2.03 s (instrumented PGO builds excluded).

## Use it when

- In Julia, sorting large Vector{Int32}, Vector{Int64}, Float or other UInt-mappable element types with the default ordering: plain sort! already picks counting or radix sort, so no package is needed.
- As a reminder to C++ developers that the speedup is available in C++ too: for integer keys, swap std::sort for a radix or SIMD sort such as Boost.Sort spreadsort, ska_sort, Highway vqsort or x86-simd-sort (all catalogued).
- When arrays are in the hundreds of thousands of elements and the key range is narrow relative to n, where Julia's heuristic chooses counting or radix sort.

## Skip it when

- As evidence that a JIT beats AOT C++: in the same suite's same-algorithm tests Julia loses (Sort::Quick Julia/Default 1.307 s vs C/Gcc 1.15 s; Sort::Merge 1.602 s vs C/Clang 1.09 s).
- With a custom lt/by ordering or a non-UInt-mappable element type: the IsUIntMappable branch falls back to ScratchQuickSort, so the radix path and this speedup do not apply.
- For small arrays (insertion sort below 40 elements) or wide key ranges with few elements, where bits + 70 &gt;= 22 ln(n) sends Julia to a comparison sort.
- Under memory pressure: radix sort allocates an n-element scratch buffer per call, and the Julia process peaks at about 405 MB against 8.6 MB for C++ in this test.
- When you need the fastest comparison sort: even Rust's built-in t.sort() takes 0.410 s here, 2.4x faster than std::sort, so std::sort is a weak reference point (derived from page data).

## How it is fast

Julia's default sort for vectors runs a decision tree (_DEFAULT_ALGORITHMS_FOR_VECTORS: InitialOptimizations, IsUIntMappable, Small{40}, CheckSorted, ComputeExtrema, ConsiderCountingSort, ConsiderRadixSort). Here the range 999,992 is not below div(399,999, 2), so counting sort is skipped. 20 bits + 70 &lt; 22 ln(399,999), which is about 284, so it commits to an LSD radix sort over the 20-bit offset from the minimum (base/sort.jl v1.13.1). That is linear-time radix sorting against libstdc++'s comparison-based introsort. The win is algorithm choice in the standard library, not JIT code quality; the suite's own docs/ai_critic.js says 'You're comparing algorithms, not languages.'

## Compared with alternatives

Pick this only to show that a managed language's standard library can choose a better algorithm by default. Among the LangArena siblings, the OpenJDK Binarytrees::Obj and Calculator::Ast rows compare like-for-like algorithms and say more about the runtime itself. The Julia (no BLAS) matmul entry is a similar algorithm and loop-structure mismatch.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Julia Base.Sort); the LangArena harness itself uses JSON3 and Printf |
| **Minimum toolchain** | Julia with the ComputeExtrema/ConsiderRadixSort default pipeline (present in base/sort.jl v1.13.1; a code comment there dates the radix path to the v1.9 development cycle); measured on Julia 1.13.1 |
| **Platforms** | any Julia platform; measured on x86-64 (AMD Ryzen 7 3800X, Linux) |
| **Thread safety** | sort! mutates its argument in place, single-threaded; concurrent sorts of distinct vectors are independent (no shared state documented) |
| **Drop-in for the baseline** | partial — sort! is Julia's default, so Julia code gets it automatically; it is not callable as a std::sort replacement from C++ |

## Gotchas

- Harness quirk: the 'random' input comes from the Benchmarks Game LCG (IM = 139968, IA = 3877, IC = 29573 in cpp/src/helper.hpp), whose full period is 139,968. The 400,000-element array is therefore the same 139,968-value sequence repeated about 2.86 times, with every value occurring 2 or 3 times (checked by re-running the generator). This affects both sides equally and does not invalidate the comparison, but the input is not 400k independent random keys.
- Not the same algorithm: the 8.5x is radix sort against introsort. The verifier capped the entry at C for this reason, and a C++ radix sort would be the fair comparison.
- One measurement per test and configuration, no variance; the headline C++ row is the -O2 'prod' build, but -O3 -march=native ('Fast', 0.998 s) and PGO (0.999 s) do not help std::sort. The Julia harness forces GC.gc() before the timed loop, and both sides run untimed warm-up iterations (20% of the timed count) before timing.
- The results file notes say the host switched from Ubuntu to Arch Linux, yet the reported gcc is an Ubuntu-packaged trunk snapshot (16.0.1 20260322, experimental), so the exact toolchain provenance is unclear.

## Known shortcomings

- Julia sort! picks LSD radix sort (base/sort.jl) while std::sort is introsort, so an algorithm win rather than a language win; the Java row is probably the JDK x86-simd-sort intrinsic; -flto inert; single run.
- Confirmed radix sort against introsort (sort.jl v1.13.1: the range 999,992 is too wide for counting sort; 20+70 &lt; 284 so RadixSort). Harness quirk: the Benchmarks Game LCG in cpp/src/helper.hpp has period 139,968, so the 400k 'random' array is one sequence repeated 2.86x with each value present 2-3 times (checked by re-running the generator); it affects both sides equally and is not invalidating. Rust's built-in t.sort() at 0.410 s is 2.4x faster than std::sort, so std::sort is a weak reference. One run per configuration; gcc is an Ubuntu trunk snapshot while the results notes say the host moved to Arch.

## Caveats and trade-offs

Not the same algorithm. std::sort is a comparison introsort. Julia's default sort! for Int32 runs ComputeExtrema and skips counting sort because the range (about 1,000,000) exceeds half the length. It then picks its stable LSD RadixSort, because 20 bits + 70 &lt; 22 ln(399,999), which is about 284 (base/sort.jl ConsiderRadixSort). The suite's own docs/ai_critic.js says 'You're comparing algorithms, not languages'. A radix sort in C++ would be expected to match or beat it. The Java row is probably not a JIT win either. OpenJDK ships an AVX2 sort intrinsic (libsimdsort, avx2-32bit-qsort.hpp, C++ based on Intel x86-simd-sort) that Arrays.sort(int[]) can use on AVX2 CPUs such as this Ryzen; whether it ran here was not checked. Every language, C and C++ included, runs untimed warm-up iterations (20 percent of the timed count, cpp/src/benchmark.cpp and csharp/BenchmarkBase.cs) before the timed loop, so steady state is compared on both sides; the record's statement that only JIT languages get a warm-up was wrong. -flto appears only on the link line in cpp/Makefile, so the 'Fast' and 'Unsafe' rows get no actual LTO (the hot code sits in one translation unit, so this is probably immaterial). One measurement per test and configuration (no variance). LangArena's README calls it 'a subjective benchmark' and says AI tools helped translate the tests between languages. Rows were selected as tests where a managed-runtime row beats every C/C++ row; most tests go the other way (for example Sort::Quick, Sort::Merge and Binarytrees::Arena). Ratios are derived from the results file, not stated by the suite. [retier] sort.jl v1.13.1 picks the stable LSD RadixSort for this input (range too wide for counting sort). The Benchmarks Game LCG in cpp/src/helper.hpp has period 139,968, so the 400k 'random' array is one sequence repeated 2.86x with each value present 2-3 times (affects both sides equally). Rust's built-in t.sort() at 0.410 s is 2.4x faster than std::sort, so std::sort is a weak reference. One run per configuration.

Julia peak RSS about 405 MB; JIT latency excluded by the warm-up phase.

## Maintenance

LangArena is active (monthly result files, MIT, 41 stars) and calls itself a subjective benchmark. The Julia behaviour is the standard-library default and needs no integration, but the comparison is an algorithm win capped at tier C.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness meets A methodology (cpp/src/sort.cpp std::sort vs julia/src/benchmarks/Sort.jl sort!, flags in cpp/Makefile, versions and CPU in the results file) and the rows match. However, the two sides run different algorithms. For this Vector{Int32} (400,000 values in 0..999,999), Julia's default sort! dispatches to its LSD RadixSort per base/sort.jl, while std::sort runs introsort, so the language-level claim is capped at C (same_algorithm false precedent: OrdinaryDiffEq.jl, Julia matmul-no-blas).
- **Verifier notes:** Downgrade A to C: the numbers match the results file, but the win is Julia's standard-library radix sort against comparison-based std::sort (same_algorithm false). It is an algorithm win, not a language win, and the same-algorithm Sort::Quick and Sort::Merge tests show C ahead. Shortcomings to record: different algorithm; the Java row is likely the JDK's x86-simd-sort intrinsic; a single run; a subjective suite. Consider a category override out of runtime-jit-beats-aot (for example numerics-and-arrays).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-24 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/cpp/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/helper.cpp>
  - <https://github.com/kostya/LangArena/tree/master/julia>
  - <https://github.com/kostya/LangArena/tree/master/julia/src>
  - <https://github.com/kostya/LangArena/tree/master/julia/src/benchmarks>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/sort.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/sort.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/julia/src/benchmarks/Sort.jl>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/julia/benchmark.jl>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/SortSelf.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/SortBenchmark.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/sort.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docs/ai_analysis.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docs/ai_critic.js>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.13.1/base/sort.jl>
  - <https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/linux/native/libsimdsort/avx2-32bit-qsort.hpp>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/sort.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/sort.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/helper.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/sort.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/julia/benchmark.jl>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/julia/src/BenchmarkFramework.jl>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/julia/src/benchmarks/Sort.jl>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/src/benchmarks/sort_self.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/docs/ai_critic.js>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.13.1/base/sort.jl>
  - <https://github.com/kostya/LangArena/tree/master/rust/src>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue+sort>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/kostya/langarena#sort-self`) · [data/wave14/enrich/raw/lang_julia_kostya_langarena_sort_self.json](../../../data/wave14/enrich/raw/lang_julia_kostya_langarena_sort_self.json) (enrichment confidence 0.8)

</details>
