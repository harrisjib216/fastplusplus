# Go: LangArena Etc::Words

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go's strings.Fields plus built-in map word count, 1.41x faster than every C and C++ build in LangArena Etc::Words.

| | |
|---|---|
| **Beats** | C++ splitting with std::istringstream and counting in std::unordered_map&lt;std::string,int&gt; (g++ 16, clang++ 22); best C/C++ row is C++/G++/PGO at 1.587 s, the C rows use uthash with a strdup per word at about 1.99 s |
| **Claimed result** | Go 1.129 s vs C++/G++ 1.638 s and C++/Clang++ 1.707 s (prod, -O2), C++/G++/Fast 1.651 s (-O3 -march=native), best of the 16 Clang/GCC C and C++ configurations C++/G++/PGO 1.587 s, C/Clang 1.988 s: about 1.41x faster than the best C/C++ row and 1.45x faster than C++/G++ prod (derived from page data). Go/Opt (static, stripped) 1.11 s. Peak RSS 11.3 MB vs 7.5-7.9 MB for the C++ rows. |
| **Workload** | Split a generated text of 50,000 space-separated words (3 to 8 lowercase letters, about 325 KB) into words, count frequencies in a hash map, then report the most frequent word and the vocabulary size; 360 timed iterations after 72 untimed warm-up iterations (run.js). A verifier simulation of the suite's LCG gives 18,623 distinct words and a unique top word ('tea', 9 times), reproducing run.js's checksum 1998586832 over 432 runs, so all languages do the same work. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++ (cpp/Makefile, c/Makefile; versions and build commands from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu snapshot package), libstdc++ (no -stdlib flag). Headline 'prod' rows (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections; C++ adds -std=c++20. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use -fprofile-correction (GCC). The Makefiles pass -flto=thin (Fast) and -flto=full (Unsafe) only on the link line while the objects are compiled without -flto, so no link-time optimisation actually takes place (inference from the Makefiles). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared (instrumented PGO/Gen rows excluded). Go 1.27.1 'go build -buildvcs=false' (default gc compiler, no PGO). Go harness runs 20 percent untimed warm-up iterations and runtime.GC() before the timed loop; the C++ harness also runs the same warm-up count. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Go uses strings.Fields (substrings share the text's backing array, no copies) and a built-in map[string]int; C++ copies each word out of an istringstream into std::string keys (this agent's reading of the sources). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X (Linux), Go 1.27.1's default build took 1.129 s for 360 iterations, against 1.587 s for the best of 16 C/C++ configurations (C++/G++/PGO, GCC 16.0.1 snapshot, libstdc++ istringstream plus unordered_map&lt;std::string,int&gt;), 1.638 s for C++/G++ at -O2, 1.707 s for C++/Clang++ (Clang 22.1.8) and 1.988 s for C/Clang with strtok_r and uthash. That is about 1.41x faster than the best C/C++ row (derived from page data).

## Use it when

- Batch word or token counting in Go over ASCII, whitespace-separated text that fits in memory as one string.
- Modest vocabularies (here 18,623 distinct 3-8 letter words, about 37% of tokens seen for the first time in each pass) where zero-copy substring keys avoid one allocation per new word.
- As a data point when reviewing C++ text tooling: a tokenizer built on std::istringstream plus std::unordered_map&lt;std::string,int&gt; leaves about 1.4x against a garbage-collected language's defaults on this shape of input.
- Teams already writing Go who want idiomatic code without hand tuning.

## Skip it when

- Inside a C++ codebase: fix the C++ instead (string_view tokenizing and an open-addressing map); the suite never measured such a version, so the size of that gain is an inference.
- When you want the fastest row: Crystal 0.88 s, Zig 0.91 s and Rust 1.021 s (prod builds) beat Go's 1.129 s on the same task, and Zig/Unchecked reaches 0.57 s.
- Memory-tight jobs: Go peaked at 11.3 MB RSS against 7.5-7.9 MB for the C++ rows, 5.1-5.5 MB for C and 4.2 MB for Zig; strings.Fields allocates a 50,000-entry []string (about 800 KB) on every call, and the map's keys keep the whole text alive.
- Non-ASCII input: strings.Fields switches to FieldsFunc(s, unicode.IsSpace) as soon as any byte is 0x80 or above (strings.go), a slower path this benchmark never exercises.
- Input larger than memory or arriving as a stream: this code needs the full text as one string, and a streaming tokenizer would likely have to copy words (not measured).

## How it is fast

The win comes from library idioms, not code generation. Go 1.27.1's strings.Fields takes an ASCII fast path that counts fields in one pass, allocates an exactly sized []string, and in a second pass slices substrings that share the text's bytes, so no word is copied; the map keys are those 16-byte string headers stored inline in Swiss-table groups, so a new key costs a slot write rather than an allocation. The C++ baseline copies the whole 325 KB text into a std::istringstream every iteration, extracts each word with operator&gt;&gt; into a std::string, and calls try_emplace on a node-based std::unordered_map&lt;std::string,int&gt; (libstdc++ caches the _Hash_bytes string hash and picks the bucket by modulo over a prime), which allocates a node holding its own string copy for each of the 18,623 distinct words per iteration and frees them all at scope exit. All 16 C and C++ configurations land within 1.59-2.08 s whatever the compiler or flags, while D/LDC (1.294 s), V/Clang (1.299 s), Nim/Clang (1.38 s) and C3 (1.463 s) prod rows also beat every C++ row, which points at istringstream and unordered_map rather than at the C++ compilers (inference from the results file).

## Compared with alternatives

Among the catalogued Etc::Words rows, Crystal (0.88 s), Zig (0.91 s, 4.2 MB) and Rust (1.021 s, 5.4 MB) are all faster and lighter, so pick the Go row only when the code is already Go; it is the shortest standard-library-only version among them. Go/Opt (static, stripped) at 1.11 s is the same code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Go standard library strings package and the built-in map) |
| **Minimum toolchain** | go.mod declares go 1.24.0; measured with go1.27.1, default 'go build' (GOAMD64=v1, no PGO) |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X); nothing platform-specific in the code |
| **Thread safety** | Go maps are not safe for concurrent writes; the runtime aborts with 'concurrent map writes' (internal/runtime/maps). The benchmark is single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- Small-vocabulary test: the fasta LCG has a period of 139,968 draws, so the text is an 18,656-word block repeated about 2.7 times. My Python replay gives a 325,090-byte text with 18,623 distinct words and a unique top word ('tea' 9 times, runners-up 6), and reproduces run.js's checksum 1998586832 as 432 runs (72 warm-up plus 360 timed), so every language does the same work. The map stays cache-sized.
- The checksum relies on luck in two places: the max-word loop ranges over a Go map, whose iteration order is randomized (C++ unordered_map order is unspecified), so a tied top count would make the result order-dependent. The C++ generator computes the word length as Helper::next_int(word_len) + Helper::next_int(3) + 3, whose operand evaluation order C++ leaves unspecified (Go guarantees left to right). The results file does not record checksum status. Neither affects the measured rows as far as the replay shows.
- Harness check, no flaw found: both sides run 72 untimed warm-up iterations, reset the LCG and time 360 iterations with a monotonic clock, and neither pre-sizes its map. Go also calls runtime.GC() before the timer, and garbage left at the end is never collected inside the timed window. Its background GC and sweeper can use the 3800X's 15 other hardware threads while C++ frees every node on the timed thread. Timing is wall-clock with one measurement per configuration.
- The lead is stable: golang/words.go (2026-04-23) and cpp/src/words.cpp (2026-04-24) did not change across the five monthly runs, and Go beat the best C/C++ row by 1.34x (Go 1.26.5, 2026-07-14), 1.39x, 1.45x (Go 1.27.1), 1.44x and 1.41x (2026-10-05), all derived from the results files.

## Known shortcomings

- Win is a stdlib/idiom difference (istringstream plus node-based unordered_map in the C++ row vs strings.Fields plus Go's Swiss-table map), not codegen; Crystal, Zig, Rust and Java also beat the C++ row. Single run of a subjective AI-assisted suite; production C/C++ rows built at -O2 (the -O3 rows also lose) and the Makefile's link-only -flto is inert.
- No harness flaw: a replay matches checksum 1998586832 (18,623 distinct words, unique top word 'tea' x9). The lead is library idioms: strings.Fields zero-copy substrings plus a Swiss map against an istringstream text copy plus a node per word; the D/LDC, V/Clang, Nim and C3 rows also beat every C++ row. Minor: the max-word result relies on a unique top count (random Go map order); the C++ generator relies on unspecified operand evaluation order; the results file records no checksum status. The lead is stable at 1.34-1.45x over 5 runs.

## Caveats and trade-offs

Mostly a standard-library and idiom comparison (tokenizing and hashing containers), so the result is about istringstream and node-based unordered_map, not code generation; a C++ version with string_view keys and a flat hash map would likely close the gap (inference, not measured). Other languages also beat every C/C++ row: Crystal 0.88 s, Zig 0.91 s, Rust 1.021 s, Java/OpenJDK 1.272 s (the Java row is a separate verified record of the same test). The C version (strdup of the whole text every iteration, strtok_r, uthash with a strdup per new key) is slower still at 1.963-2.084 s. LangArena calls itself 'a subjective benchmark' and says AI tools helped translate the tests between languages. The suite publishes one measurement per test and configuration (no variance). The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3 Fast, Unsafe and PGO variants were also compared and Go still wins; the Makefiles' -flto flags are link-only, so the 'LTO' builds probably get no LTO. The per-benchmark ratios are derived from the results file, not stated by the suite. Rows were picked by the search agent as text tests where a Rust, Zig or Go production row beats every C and C++ row; most other text tests in the suite go the other way (for example Base64::Encode and Base64::Decode, where C is about 3x faster than Rust, and Distance::Jaro, which is a tie). [retier] A replay matches checksum 1998586832 (18,623 distinct words, unique top word 'tea' x9). The lead is library idioms: strings.Fields zero-copy substrings plus a Swiss map against an istringstream text copy plus a node per word; the D/LDC, V/Clang, Nim and C3 rows also beat every C++ row. The max-word result relies on a unique top count (random Go map order); the C++ generator relies on unspecified operand evaluation order. Stable at 1.34-1.45x over 5 runs.

Zero-copy word keys; the Go and Rust versions keep a reference to the whole text while the map is alive.

## Maintenance

The MIT-licensed suite is active (41 stars, 622 commits, monthly reruns, last commit 2026-10-08 per the verifier); the author calls it subjective, treats C++ and Crystal as the reference implementations and asks for the same containers in every language (issue #1), so this row compares default Go idioms with default C++ idioms, not a component to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for both sides (golang/words.go, cpp/src/words.cpp, c/src/words.c, harnesses golang/benchmark.go and cpp/src/benchmark.cpp; workload and checksum in run.js), C/C++ flags in cpp/Makefile and c/Makefile, and exact compiler versions, build commands and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; every quoted runtime matches the Etc::Words-runtime rows. Same tier as the already verified Java row of this test.
- **Verifier notes:** Confirm at A: runtimes match the results file row for row (Go 1.129 s, C++/G++ 1.638 s, C++/G++/PGO 1.587 s best, C/Clang 1.988 s, RSS 11.3 MB), metadata checks out (MIT, 41 stars, not a fork, last commit 2026-10-08), and a simulation reproduces the run.js checksum, so the work is identical. Shortcomings to record: standard-library/idiom win (istringstream plus node-per-key unordered_map vs strings.Fields plus Swiss-table map), not codegen; Crystal, Zig, Rust and Java also beat C++; single measurement per configuration; subjective AI-assisted suite; prod C/C++ rows at -O2 (the -O3 rows also lose); LTO flags inert; 1.45x more memory than C++.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-34 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://github.com/kostya/LangArena/tree/master/cpp>
  - <https://github.com/kostya/LangArena/tree/master/cpp/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://github.com/kostya/LangArena/tree/master/golang>
  - <https://github.com/kostya/LangArena/tree/master/c/src>
  - <https://github.com/kostya/LangArena/tree/master/rust/src>
  - <https://github.com/kostya/LangArena/tree/master/rust/src/benchmarks>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/words.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/helper.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/benchmark.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/words.rs>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/issues/1>
  - <https://github.com/kostya/LangArena/commits/master/golang/words.go>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/words.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/benchmark.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/helper.go>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/golang/go.mod>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/strings/strings.go>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/internal/runtime/maps/group.go>
  - <https://raw.githubusercontent.com/golang/go/go1.27.1/src/internal/runtime/maps/runtime_fast32.go>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/basic_string.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/hashtable.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/hashtable_policy.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/functional_hash.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:go/kostya/langarena#etc-words`) · [data/wave14/enrich/raw/lang_go_kostya_langarena_etc_words.json](../../../data/wave14/enrich/raw/lang_go_kostya_langarena_etc_words.json) (enrichment confidence 0.75)

</details>
