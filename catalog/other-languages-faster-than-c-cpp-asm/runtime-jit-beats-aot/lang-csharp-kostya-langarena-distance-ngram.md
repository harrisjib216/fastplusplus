# dotnet JIT (C# on .NET 11): LangArena Distance::NGram

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> Idiomatic C# Dictionary&lt;uint,int&gt; 4-gram counting on .NET 11, about 1.6x faster than the suite's C++ std::unordered_map version.

| | |
|---|---|
| **Beats** | C++ using std::unordered_map&lt;uint32_t,int&gt; for 4-gram counts (g++ 16, clang++ 22); best C/C++ configuration is C++/Clang++/PGO at 0.822 s |
| **Claimed result** | C#/JIT 0.516 s vs C++/G++ 0.863 s and C++/Clang++ 0.877 s (prod, -O2). The best of the 16 gcc/clang C and C++ configurations is C++/Clang++/PGO at 0.822 s (C++/G++/Fast at -O3 0.85 s), so C# is about 1.67x faster than C++/G++ prod and 1.59x faster than the best row (derived from page data). Other .NET rows also win, including NativeAOT builds with no JIT: C#/SC-JIT 0.475 s, C#/R2R 0.526 s, C#/AOT 0.609 s. F#/JIT 0.534 s and Julia/Default 0.58 s also win. Java/OpenJDK at 2.072 s is slower, and the C version (uthash, one malloc per distinct gram) is slower still: best C/Clang/Fast 1.789 s, C/Clang prod 1.811 s. The timed loop is 100 iterations over 10 string pairs (lengths 4 to 20,003 over a 10-letter alphabet), after 20 untimed warm-up iterations. |
| **Workload** | Count 4-gram frequencies of many generated string pairs in two hash maps and compute the n-gram overlap score. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++ (cpp/Makefile, c/Makefile; versions from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk, Ubuntu package build), libstdc++ (no -stdlib flag). 'prod' (headline rows): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, -std=c++20 for C++. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use (GCC). -flto=thin (Fast) and -flto=full (Unsafe) are passed only on the link line (LDFLAGS) while objects are compiled without -flto, so no link-time optimisation actually takes place. Managed side: dotnet 11.0.100-rc.1.26425.128, 'dotnet build -c Release' (Optimize=true) run as 'dotnet Benchmark.dll' with default tiered JIT; the C#/AOT rows are NativeAOT with IlcInstructionSet=native and IlcOptimizationPreference=Speed; Julia 1.13.1 run as 'julia --project=. --threads=16 benchmark.jl' (Julia/Max adds -O3 --check-bounds=no --math-mode=fast); Temurin OpenJDK 27+35 run as 'java -Xmx2g -jar'. Every language, C and C++ included, runs untimed warm-up iterations (20 percent of the timed count) before the timed loop. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Inferred from the sources, not stated by the suite: .NET Dictionary&lt;uint,int&gt; keeps entries in flat arrays, while libstdc++ std::unordered_map allocates a node per distinct key, and each string pair builds two maps. This is a container-implementation effect rather than JIT code quality. |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

LangArena results of 2026-10-05 (AMD Ryzen 7 3800X, Linux) time 100 iterations over 10 generated string pairs of 4 to 20,003 letters after 20 warm-up iterations: C#/JIT (.NET 11.0.100-rc.1, dotnet build -c Release, default tiered JIT) 0.516 s against C++ prod builds at -O2 with libstdc++ std::unordered_map of 0.863 s (g++ 16.0.1 trunk) and 0.877 s (clang++ 22.1.8), and 0.822 s for the best C/C++ configuration (Clang++ PGO), about 1.67x and 1.59x (derived from page data). Rust (0.533 s), Zig (0.52 s), Go (0.603 s) and C# NativeAOT (0.609 s) also beat C++ on the same test.

## Use it when

- Counting small packed integer keys (n-grams, k-mers, IDs) in .NET: idiomatic Dictionary&lt;uint,int&gt; code already runs about 1.6-1.7x faster than C++ code that reaches for std::unordered_map (0.516 s vs 0.863 s).
- Choosing a language for text-similarity or frequency-count services where the C++ alternative would be written with standard containers rather than a tuned flat hash map.
- Deployments that cannot use a JIT: NativeAOT builds also win (C#/AOT 0.609 s at 14.6 MB, against C++/G++ 0.863 s at 7.1 MB).
- Long-running processes where tiered JIT warm-up is amortized; the measured loop follows 20 untimed warm-up iterations.

## Skip it when

- As a reason to leave C++: the loss is the container's, and a C++ open-addressing map would likely close the gap; the suite never ran one, but Rust's std HashMap (0.533 s, 4.3 MB) and Zig (0.52 s, 3.4 MB) show what array-based maps reach with a fraction of the memory.
- Memory-tight processes: C#/JIT peaks at 40.6 MB against 6.6-7.1 MB for the C++ rows and 4.0 MB for C.
- As evidence that managed JITs beat C++ in general: the JVM rows lose badly on the same test (Java/OpenJDK 2.072 s, Kotlin about 2.0 s, Scala about 2.4 s), and C#/JIT beats both C++ prod rows in only 7 of the 50 tests in this results file (derived from page data).
- Short-lived or cold-start workloads: the reported time excludes data generation and 20 warm-up iterations for every language, so first-call JIT cost is not reflected.
- Strict release-only toolchains: the run used .NET 11.0.100-rc.1 and a GCC 16.0.1 trunk snapshot.

## How it is fast

The gap is in the containers, not in JIT code generation: libstdc++ std::unordered_map allocates a node for every distinct key and walks bucket chains through pointers, while .NET's Dictionary keeps buckets and entries in flat arrays, so building and dropping thousands of grams per call costs no per-key heap allocation (inferred from the sources; the suite gives no explanation). Every language whose standard map is array-based also beats C++ here: Rust std HashMap with its default SipHash hasher 0.533 s, Zig 0.52 s, Go 0.603 s, and C# compiled ahead of time with NativeAOT 0.609 s. The C# code even does more work per gram (two lookups per update and a fourth lookup for the count check, plus an ASCII copy of both strings) than the C++ try_emplace plus find.

## Compared with alternatives

Among the catalogued LangArena managed-runtime wins, this is the clearest container-driven case: pick it when the workload is integer-keyed counting, where .NET's flat Dictionary wins and the JVM rows lose (Java 2.072 s), whereas the Java Etc::Words and CacheSimulation siblings are string-keyed maps and the C# Graph::AStar sibling rests on a priority queue and a buggy C heap.

## Integration

| | |
|---|---|
| **Form** | runtime plus source snippet (csharp/Distance.cs in a .NET console project, Benchmark.csproj) |
| **Dependencies** | none for this test beyond the .NET base class library (the project references CsvHelper 33.1.0 for other tests) |
| **Minimum toolchain** | .NET 11 SDK as measured (TargetFramework net11.0, 11.0.100-rc.1.26425.128); the code itself uses only long-standing BCL APIs |
| **Platforms** | any .NET target; measured on x86-64 Linux (AMD Ryzen 7 3800X) |
| **Thread safety** | not documented; each call builds and discards its own two dictionaries on one thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Container comparison rather than a JIT win: C# NativeAOT (0.609 s), Rust std HashMap (0.533 s), Zig (0.52 s) and Go (0.603 s) all beat every C++ row, while the C version with uthash (one malloc per distinct gram) is twice as slow as C++ at 1.79-1.84 s; the catalogue category runtime-jit-beats-aot fits poorly.
- The C++ ngram loop runs 'for (size_t i = 0; i &lt;= s.size() - 4; ++i)', which underflows and reads out of bounds for strings shorter than four characters; the generator always produces at least four, so the numbers are unaffected, and the C# version returns 0.0 early for short input.
- Both sides reserve capacity equal to the string length (up to 20,003) although at most 10,000 distinct 4-grams exist over the 10-letter alphabet, so each call zeroes or allocates more bucket space than it uses; C# also calls GC.Collect between warm-up and the timed loop.
- One measurement per configuration with no variance figure; the results file is from a single host on 2026-10-05, and LangArena's README calls the suite subjective and AI-assisted in translation.

## Known shortcomings

- A container effect (node-based std::unordered_map against the flat .NET Dictionary), not the JIT: C#/AOT (0.609 s) also beats the best C++ row (0.822 s); -flto only on the link line (inert); single run of a subjective AI-assisted suite.
- Container effect confirmed: Rust std HashMap (SipHash) 0.533 s, Zig 0.52, Go 0.603 and C#/AOT 0.609 all beat C++'s 0.863, and C# does more lookups per gram and still wins; JVM rows lose (Java 2.072 s). C#/JIT beats both C++ prod rows in only 7 of 50 tests. Latent C++ bug: i &lt;= s.size() - 4 underflows size_t on strings under 4 characters (the generator never makes them, so the numbers are valid). The category runtime-jit-beats-aot fits poorly.

## Caveats and trade-offs

This is a container comparison more than a JIT one. .NET NativeAOT builds with no JIT (C#/AOT 0.609 s, C#/SC-AOT 0.61 s) also beat every C/C++ row, so the runtime-jit-beats-aot category fits poorly. The C++ side uses node-based std::unordered_map&lt;uint32_t,int&gt;, reserved to the string length, with the default identity hash and prime-modulo buckets. An open-addressing map would likely close the gap. The C version (uthash with one malloc per distinct gram) is about 2x slower than the C++ one. The C# side does slightly more work: Encoding.ASCII.GetBytes copies both strings on every call. Every language, C and C++ included, runs untimed warm-up iterations (20 percent of the timed count, cpp/src/benchmark.cpp and csharp/BenchmarkBase.cs) before the timed loop, so steady state is compared on both sides; the record's statement that only JIT languages get a warm-up was wrong. -flto appears only on the link line in cpp/Makefile, so the 'Fast' and 'Unsafe' rows get no actual LTO (the hot code sits in one translation unit, so this is probably immaterial). Java does not share the win, so this is not a general JIT property. One measurement per test and configuration (no variance). LangArena's README calls it 'a subjective benchmark' and says AI tools helped translate the tests between languages. Rows were selected as tests where a managed-runtime row beats every C/C++ row; most tests go the other way (for example Sort::Quick, Sort::Merge and Binarytrees::Arena). Ratios are derived from the results file, not stated by the suite. [retier] Container effect: Rust std HashMap (SipHash) 0.533 s, Zig 0.52, Go 0.603 and C#/AOT 0.609 all beat C++'s 0.863; C# does more lookups per gram and still wins; JVM rows lose (Java 2.072 s). C#/JIT beats both C++ prod rows in only 7 of 50 tests. Latent C++ bug: i &lt;= s.size() - 4 underflows on strings under 4 characters (the generator never makes them).

C# peak RSS about 41 MB. .NET 11 is a release candidate (11.0.100-rc.1) in this run.

## Maintenance

LangArena is active (MIT, 41 stars, last commit 2026-10-08, monthly result files), and the C# NGram code has been unchanged since 2026-03-04 while the C++ file was last touched on 2026-04-24; the 60-line C# routine is copyable, but the result says more about std::unordered_map than about .NET.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The benchmark code is public (cpp/src/distance.cpp NGram::ngram vs csharp/Distance.cs CalcNGram, workload in run.js), the compilers and flags are in cpp/Makefile and the results file's version and build-cmd fields, and the CPU (AMD Ryzen 7 3800X) is stated. Both sides pack the same 4-grams into each language's standard hash map at release settings, and -O3 -march=native C++ builds were compared too, so A stands (knucleotide precedent: idiomatic std::unordered_map against an idiomatic runtime hash table).
- **Verifier notes:** Confirm at A: the numbers match the results file row for row, and the metadata checks out (MIT, 41 stars, last commit 2026-10-08, not a fork). Shortcomings to record: a container comparison (node-based std::unordered_map against a flat .NET Dictionary); not a JIT win, since C# NativeAOT also beats every C++ row (consider a category override such as string-and-text); a single run; a subjective, AI-assisted suite; headline C++ rows at -O2, though the -O3 rows also lose; LTO flags inert.
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
  - <https://github.com/kostya/LangArena/tree/master/csharp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/distance.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/Distance.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/BenchmarkBase.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/csharp/Benchmark.csproj>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/distance.c>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/distance.cpp>
  - <https://github.com/kostya/LangArena/commits/master/csharp/Distance.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/csharp/Distance.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/csharp/BenchmarkBase.cs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/csharp/Benchmark.csproj>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/distance.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/distance.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:csharp/kostya/langarena#distance-ngram`) · [data/wave14/enrich/raw/lang_csharp_kostya_langarena_distance_ngram.json](../../../data/wave14/enrich/raw/lang_csharp_kostya_langarena_distance_ngram.json) (enrichment confidence 0.72)

</details>
