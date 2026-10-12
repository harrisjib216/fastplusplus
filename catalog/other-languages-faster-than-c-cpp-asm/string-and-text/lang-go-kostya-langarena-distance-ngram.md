# Go: LangArena Distance::NGram

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go's built-in Swiss-table map counting 4-grams, 1.36x faster than the best C/C++ build in LangArena Distance::NGram.

| | |
|---|---|
| **Beats** | C++ using std::unordered_map&lt;uint32_t,int&gt; for 4-gram counts (g++ 16.0.1, clang++ 22.1.8); best C/C++ configuration is C++/Clang++/PGO at 0.822 s; the C version of the same task is slower still (C/Clang 1.811 s) |
| **Claimed result** | Go 0.603 s (peak RSS 12.0 MB) vs C++/Clang++/PGO 0.822 s (best of the 16 Clang/GCC C and C++ configurations), C++/G++/Fast 0.85 s (-O3 -march=native), C++/G++ 0.863 s and C++/Clang++ 0.877 s (prod, -O2), C/Clang 1.811 s: about 1.36x faster than the best C/C++ row, 1.43x faster than C++/G++ prod and 3.0x faster than C/Clang (derived from page data). Go/Opt (static, stripped) 0.598 s. Rust 0.533 s and Zig 0.52 s are faster still. The lead grew over five monthly runs: 1.16x on 2026-07-14 (Go 1.26.5, 0.699 s vs C++/Clang++/PGO 0.81 s), 1.21x on 2026-08-14, 1.29x on 2026-09-03 (Go 1.27.1), 1.27x on 2026-09-18 and 1.36x on 2026-10-05 (derived from the results files). |
| **Workload** | For 10 generated string pairs (lengths 4 to 20,003 over a 10-letter alphabet), pack each 4-gram into a 32-bit key, count the first string's grams in one hash map and the second string's in another while counting the intersection, and sum the overlap scores; 100 timed iterations after 20 untimed warm-up iterations, with the result checked against run.js's checksum (397440). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++ (cpp/Makefile, c/Makefile; versions and build commands from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu snapshot package), libstdc++ (no -stdlib flag), -std=c++20 for C++. Headline 'prod' rows (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use -fprofile-correction (GCC). -flto=thin (Fast) and -flto=full (Unsafe) appear only in the link flags while objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared (instrumented PGO/Gen rows and the author's mycc/cproc compilers excluded). Go: go1.27.1 linux/amd64, 'go build -buildvcs=false' (the gc compiler has no optimisation levels and always optimises; default GOAMD64=v1 generic target, no PGO); Go/Opt adds -a -trimpath -ldflags='-s -w' with a static netgo build, which does not change code generation. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Not stated by the suite. Code reading (golang/distance.go vs cpp/src/distance.cpp): identical algorithm (two hash maps of 4-byte grams); Go uses its built-in map[uint32]int, C++ uses libstdc++'s node-based unordered_map. Agent inference: container implementation, not code generation (Go 1.24 and later use swiss-table maps). |
| **Adoption** | 41 stars (suite repo) |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X (Linux), Go 1.27.1's default build took 0.603 s for 100 iterations, against 0.822 s for the best of 16 C/C++ configurations (C++/Clang++/PGO, Clang 22.1.8 with libstdc++ std::unordered_map), 0.863 s for C++/G++ at -O2 (GCC 16.0.1 snapshot) and 1.811 s for C/Clang with uthash. That is about 1.36x faster than the best C/C++ row (derived from page data), and Go led in all five monthly runs since 2026-07-14 (1.16x to 1.36x) on unchanged source.

## Use it when

- You are choosing a language for histogram or counting code keyed by small integers (here at most 8,647 distinct uint32 keys per map, rebuilt on every call) and want GC-managed code that beats default-STL C++.
- Many short-lived integer-keyed maps where per-key node allocation in std::unordered_map would dominate.
- As a data point when arguing to replace std::unordered_map&lt;uint32_t,...&gt; in a C++ hot loop with an open-addressing table: this row shows the size of the gap the container alone can cause.
- Code that is already Go on Linux x86-64: the built-in map needs no dependency and no tuning to get this result.

## Skip it when

- Inside a C++ codebase: you cannot link this; swap the container instead (an open-addressing map such as absl::flat_hash_map or boost::unordered_flat_map was never measured by the suite, so the expected gain is an inference).
- When you want the fastest safe-default row: Zig 0.52 s, C#/JIT 0.516 s and Rust 0.533 s beat Go's 0.603 s on the same task, and Zig/Unchecked reaches 0.325 s.
- Memory-tight jobs: Go peaked at 12.0 MB RSS against 6.6-7.1 MB for the C++ rows, about 4 MB for C and 3.4 MB for Zig, and its len(s) size hints allocate about 0.5 MB of map groups for each of the larger strings.
- Latency-sensitive code paths: the suite reports total runtime only, and Go's garbage collector runs during the timed loop.
- Go releases before 1.24 (the go.mod minimum) were not measured; the lead was smaller with Go 1.26.5 (1.16-1.21x) than with 1.27.1 (1.27-1.36x).

## How it is fast

The gap is the hash table, not code generation. Go 1.27's built-in map is a Swiss table (internal/runtime/maps): 8-slot groups with a control word of 7-bit hash tags that AMD64 matches with SIMD intrinsics, slots stored inline so a new key costs no allocation, and tables capped at 1,024 slots that split as the map grows. libstdc++'s std::unordered_map&lt;uint32_t,int&gt; is a chained, node-based table: the identity std::hash, a bucket index taken as hash % prime bucket count (a 64-bit division), no cached hash for integer keys so the modulo is recomputed while walking a chain, and one heap node per distinct key, which is 122,691 node allocations and frees per iteration here (about 12.3 million in the timed loop, from a replay of the generator). Go wins while doing more work (a []byte copy of each string and three map operations per second-string gram against two in C++), and Rust, Zig, C#, Julia and Nim/NLVM rows also beat every C++ row, which points at the container rather than the compiler.

## Compared with alternatives

Among the catalogued Distance::NGram rows, Zig (0.52 s, 3.4 MB) and Rust (0.533 s, 4.3 MB) are faster and lighter, so pick the Go row only when your code is already Go or you want a garbage-collected language whose default map still beats default C++. For string-keyed counting, see the Go Etc::Words sibling.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Go built-in map and strings.Builder for input generation) |
| **Minimum toolchain** | go.mod declares go 1.24.0; measured with go1.27.1, default 'go build' (GOAMD64=v1, no PGO) |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X); the Go map uses SIMD group matching on AMD64 and a portable SWAR version elsewhere (group.go) |
| **Thread safety** | Go maps are not safe for concurrent writes; the runtime aborts with 'concurrent map writes' (internal/runtime/maps/runtime_fast32.go). The benchmark is single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- Small, cache-resident key space: a 4-gram over 10 letters has only 10,000 values, so no map ever holds more than 8,647 keys. The fasta LCG behind the input has a period of 139,968 draws while the strings need 213,051 characters, so the last third of the data repeats earlier characters. My Python replay reproduces run.js's checksum 397440 as 120 runs (20 warm-up plus 100 timed) of a per-run score of 3,312, so all languages do the same work. It is not a large-key hash-map test.
- The Go code is not tuned and is even handicapped: the len(s) hint (up to 19,121) on a key space of 10,000 makes Go build 32 tables of 1,024 slots for the largest strings, about 6.1 MB of zeroed map memory per iteration and roughly 600 MB over the timed loop (my estimate from the NewMap and newTable sizing code). Each call also copies both strings with []byte(s). Better sizing would probably widen the lead (inference).
- Harness check, no flaw found: both harnesses run 20 untimed warm-up iterations that feed the same checksum, reset the LCG and time 100 iterations with a monotonic clock. Go also calls runtime.GC() before starting the timer, and garbage left at the end is never collected inside the timed window, while the C++ rows free every node inside it. Go's background GC and sweeper can use the 3800X's 15 other hardware threads. Timing is wall-clock with one measurement per configuration.
- Run-to-run drift is about 5-7%: golang/distance.go (2026-04-23) and cpp/src/distance.cpp (2026-04-24) did not change across the five monthly runs, yet Go went from 0.651 s to 0.603 s on the same go1.27.1 between 2026-09-03 and 2026-10-05. The 2026-10-05 notes say the host moved from Ubuntu to Arch Linux, although the GCC version string still names the Ubuntu snapshot package. The C++ code's loop bound s1.size() - 4 would underflow for strings shorter than 4, which this generator never produces; the Go version checks the length first.

## Known shortcomings

- Swiss-table map vs node-based std::unordered_map, not codegen; the concurrent GC may use idle cores under wall-clock timing; the lead grew from 1.16x to 1.36x between July and October, mostly with Go 1.27.
- No correctness bug or harness flaw: the harnesses are symmetric (20 warm-ups, LCG reset, monotonic clock) and a replay matches checksum 397440. The win comes from the container: libstdc++ unordered_map makes 122,691 node mallocs per iteration and takes a prime modulo, uncached for integer keys, against Go's Swiss table; Go is handicapped rather than favoured (3 map operations against 2, plus a len(s) hint allocating about 6.1 MB of zeroed map memory per iteration). The key space is only 10,000 grams and the LCG data repeats; drift is about 5-7% between runs (host moved to Arch 2026-10-05) with the source unchanged since April. The D/LDC, V/Clang, Nim and C3 rows also beat every C++ row, so the cause is the container, not the compiler.

## Caveats and trade-offs

Container comparison: a C++ open-addressing map (absl::flat_hash_map, boost::unordered_flat_map) would likely close the gap, and the suite only uses std::unordered_map (the C rows use uthash with a malloc per gram and are about 3x slower). Timing is wall-clock, and Go's concurrent GC may do part of its reclamation on otherwise idle cores of the 8-core Ryzen while the C++ rows free every node on the timed thread. Rust, Zig, C# and Julia also beat every C/C++ row here, so the result is about std::unordered_map, not Go. The lead grew from 1.16x in July 2026 to 1.36x in October, mostly with Go 1.27 (the C++ rows stayed at 0.81-0.85 s). LangArena calls itself 'a subjective benchmark' and says AI tools helped translate the tasks between languages; it publishes one measurement per test and configuration (no variance). The headline C/C++ rows are -O2 with hardening flags, but the -O3 -march=native Fast, Unsafe and PGO rows also lose, and Go builds for generic x86-64; the Makefiles' LTO flags are link-only. The row was selected because a non-C/C++ language beats every C and C++ configuration; most other tasks in the suite go the other way. Ratios are derived from the results files, not stated by the suite. [retier] The harnesses are symmetric (20 warm-ups, LCG reset, monotonic clock) and a replay matches checksum 397440. libstdc++ unordered_map makes 122,691 node mallocs per iteration with a prime modulo against Go's Swiss table; Go does 3 map operations against 2 plus a len(s) hint allocating about 6.1 MB of zeroed map memory per iteration. The key space is only 10,000 grams; drift is about 5-7% between runs. The D/LDC, V/Clang, Nim and C3 rows also beat every C++ row, so the cause is the container, not the compiler.

Go peak RSS 12.0 MB vs about 7 MB for C++ and 4 MB for C in the same run; garbage collected.

## Maintenance

The MIT-licensed suite is active (41 stars, 622 commits, monthly reruns, last commit 2026-10-08 per the verifier); the author treats C++ and Crystal as the reference implementations and asks other languages to use the same containers (issue #1), so this row measures Go's default map against default std::unordered_map, not a component to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for every side (golang/distance.go NGram.ngram, cpp/src/distance.cpp NGram::ngram, c/src/distance.c NGram_calc; workload in run.js), C/C++ flags in the Makefiles, and Go 1.27.1, the build commands, compiler versions and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; both sides pack the same 4-grams into two pre-sized standard hash maps, so A stands (same precedent as the C#, Rust and Zig rows of this test).
- **Verifier notes:** Confirm at A: runtimes match the 2026-10-05 results file (Go 0.603 s, C++/Clang++/PGO 0.822 s best, C++/G++ 0.863 s, C/Clang 1.811 s, RSS 12.0 MB), Go and C++ run the same algorithm with pre-sized maps, and Go leads in all five monthly runs (1.16-1.36x); same_opt_level set true because Go has no optimisation levels and the -O3 -march=native C++ rows also lose. Shortcomings to record: Swiss-table map vs node-based std::unordered_map, not codegen; concurrent GC may use spare cores (wall-clock timing); Rust, Zig, C# and Julia also win; single measurement per configuration; subjective AI-assisted suite; prod C/C++ at -O2; 1.7x the memory of C++. Metadata checks out (MIT, 41 stars, last commit 2026-10-08).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/distance.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/benchmark.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/go.mod>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/distance.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/issues/1>
  - <https://github.com/kostya/LangArena/commits/master/golang/distance.go>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/distance.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/benchmark.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/helper.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/go.mod>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/main.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/distance.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/internal/runtime/maps/group.go>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/internal/runtime/maps/map.go>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/internal/runtime/maps/table.go>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/internal/runtime/maps/runtime_fast32.go>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/runtime/alg.go>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/hashtable_policy.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/hashtable.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/functional_hash.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:go/kostya/langarena#distance-ngram`) · [data/wave14/enrich/raw/lang_go_kostya_langarena_distance_ngram.json](../../../data/wave14/enrich/raw/lang_go_kostya_langarena_distance_ngram.json) (enrichment confidence 0.75)

</details>
