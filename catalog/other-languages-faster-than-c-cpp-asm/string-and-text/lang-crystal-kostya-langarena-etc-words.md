# Crystal: LangArena Etc::Words

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Crystal` · `MIT` · 🟢 active

> Crystal's idiomatic String#split plus built-in Hash word count, about 1.8x faster than every C and C++ build in LangArena Etc::Words.

| | |
|---|---|
| **Beats** | C++ splitting with std::istringstream and counting in std::unordered_map&lt;std::string,int&gt;, and C using strtok_r with uthash (strdup per new word); both built by g++/gcc 16.0.1 and clang 22.1.8; best C/C++ configuration is C++/G++/PGO at 1.587 s |
| **Claimed result** | Crystal 0.88 s (peak RSS 8.8 MB) vs C++/G++/PGO 1.587 s (best of the 16 Clang/GCC C and C++ configurations), C++/G++ 1.638 s and C++/Clang++ 1.707 s (prod, -O2), C++/G++/Fast 1.651 s (-O3 -march=native) and C/Clang 1.988 s: about 1.80x faster than the best C/C++ row, 1.86x faster than C++/G++ prod and 2.26x faster than C/Clang (derived from page data). Zig 0.91 s, Rust 1.021 s and Go 1.129 s also beat every C/C++ row. The lead is stable across five monthly runs: 1.79x on 2026-07-14 (Crystal 1.20.3, 0.901 s vs C++/G++ 1.611 s), 1.81x on 2026-08-14, 1.80x on 2026-09-03, 1.82x on 2026-09-18 and 1.80x on 2026-10-05 (derived from the results files). The suite's 'Crystal/O3' row (crystal build -O3 without --release) is much slower at 3.105 s, slower than every C row. |
| **Workload** | Split a generated text of 50,000 space-separated words (3 to 8 lowercase letters) into words, count frequencies in a hash map, then report the most frequent word, the vocabulary size and a checksum; 360 timed iterations after 72 untimed warm-up iterations (run.js). Each harness checks the final checksum against run.js (1998586832), so Crystal does the same work as C and C++. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++ (cpp/Makefile, c/Makefile; versions and build commands from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu snapshot package), libstdc++ (no -stdlib flag), -std=c++20 for C++. Headline 'prod' rows (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use -fprofile-correction (GCC). -flto=thin (Fast) and -flto=full (Unsafe) appear only in the link flags while objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared (instrumented PGO/Gen rows and the author's mycc/cproc compilers excluded). Crystal 1.21.1 [73ea5c2b1] (2026-09-26): headline row 'crystal build main.cr --release' (Crystal 1.21.1's src/compiler/crystal/command.cr defines --release as '-O3 --single-module'; LLVM backend, Boehm GC); the 'Crystal/O3' hack row is 'crystal build main.cr -O3', i.e. without --single-module, which plausibly explains its 3.5x slower time (inference, not stated by the suite). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Code reading (crystal/main.cr, cpp/src/words.cpp, c/src/words.c): the C++ baseline tokenizes with istringstream operator&gt;&gt; and copies each word into a std::string key of a node-based unordered_map; the C baseline strdup's every distinct word into uthash; Crystal splits on ' ' with a block and updates its built-in Hash. Agent inference: a tokenizer and container difference, not code generation. |
| **Adoption** | 41 stars (suite repo) |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In the 2026-10-05 LangArena run on an AMD Ryzen 7 3800X (Linux), Crystal 1.21.1 built with --release took 0.88 s for 360 iterations, against 1.587 s for the best of 16 C/C++ configurations (C++/G++/PGO, GCC 16.0.1 trunk, libstdc++, -O2 plus profile use), 1.638 s for C++/G++ at -O2 and 1.988 s for C/Clang 22.1.8. That is about 1.8x faster than the best C/C++ row (derived from page data), with the same 1.79-1.82x lead in five monthly runs since 2026-07-14.

## Use it when

- You are choosing a language for log, text or word-count tooling and want GC-managed, Ruby-like code that still beats a naive istringstream plus unordered_map C++ version.
- Workloads that tokenize on a single ASCII byte and count small string keys (about 18.6k distinct 3-8 letter words here) in a hash that fits in cache.
- Command-line or batch jobs on Linux x86-64 or AArch64 where you can build with crystal build --release.
- As a reference point to check whether your own C++ tokenizer or hash map has the same istream or node-allocation overhead.

## Skip it when

- Inside an existing C++ codebase: Crystal binds to C APIs only (its README: 'call C code by writing bindings'), so a C++ program would need a C shim, and Crystal brings its own Boehm GC runtime.
- If you can change the C++ code: string_view tokenizing plus a flat or open-addressing map is the obvious fix, and the suite never measured such a version, so the 1.8x gap says little against tuned C++ (inference).
- Memory-tight jobs: Crystal peaked at 8.8 MB RSS against 5.3 MB for C and 7.8 MB for C++ on this task, and it allocates a fresh String for every word, including repeated ones.
- Builds without --release: the suite's Crystal/O3 row (crystal build -O3, no --single-module) took 3.105 s, slower than every C and C++ row.
- Latency-sensitive services where stop-the-world Boehm GC pauses matter; this benchmark only reports total runtime.

## How it is fast

The win comes from the libraries, not from code generation. Crystal's String#split(Char) walks the bytes once with Char::Reader and copies each word into a new GC-allocated String. Its Hash is an insertion-ordered, open-addressing table with linear probing over a power-of-two index array, and strings are hashed with the funny_hash-based Crystal::Hasher. The C++ baseline instead runs the locale-aware std::istringstream operator&gt;&gt; (which also copies the whole text into its stringbuf each iteration) and a node-based std::unordered_map&lt;std::string,int&gt;. Every C row timed almost the same (1.96-2.08 s) whether built by Clang, GCC, the author's mycc or cproc/QBE, and every C++ row stayed within 1.59-1.73 s whatever the flags, which suggests most of the time is spent inside libc and libstdc++ calls rather than in compiled user code (inference from the results file).

## Compared with alternatives

Against the other catalogued LangArena Etc::Words rows, Crystal (0.88 s) is the fastest default-flag build, ahead of Zig ReleaseSafe 0.91 s, Rust 1.021 s and Go 1.129 s; pick Crystal for the shortest garbage-collected code, Zig (4.2 MB) or Rust (5.4 MB) when memory matters or you need code that can live next to C. For production text splitting in a C/C++ stack, a real tool such as csv-zero or a Rust crate from the sibling list is more useful than this benchmark row.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Crystal compiler (1.21.1 in the measured run, LLVM backend) and its runtime, linked against Boehm GC (libgc / bdw-gc); the benchmark file also requires the cryyjson shard, which this task does not use |
| **Minimum toolchain** | Crystal 1.21.1 measured; older versions not tested here |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X); Crystal's README shows Linux, macOS, AArch64 and Windows CI |
| **Thread safety** | Not documented for this task; the benchmark is single-threaded and Crystal's Hash is not synchronized |
| **Drop-in for the baseline** | no |

## Gotchas

- The workload is less random than it looks. Helper.next_int is the Benchmarks Game fasta LCG (IM 139968, IA 3877, IC 29573), whose period is at most 139,968, and the text needs about 375k draws, so the 50,000-word text is an 18,656-word block repeated about 2.7 times. That leaves 18,623 distinct words, most seen 2 or 3 times, and one clear winner ('tea', 9 times). My Python replay reproduces run.js's checksum 1998586832 as 432 iterations (72 warm-up plus 360 timed) of 9 + djb2('tea') + 18,623. The checksum is therefore valid across languages because the top word has no tie, but the test is a small-vocabulary hash workload, not a 50k-key one.
- The 1.8x is a library and idiom comparison: C++ pays for std::istringstream operator&gt;&gt; and a whole-text copy into the stringbuf each iteration; C does strdup of the whole text, strtok_r, strlen and a malloc plus strdup per distinct word into uthash. Neither is how a performance-minded C++ programmer would write it.
- Crystal's Hash#update with a default probes twice on a miss (find_entry_with_index, then upsert), so the Crystal side is not even optimal; about 37% of words per iteration are first sightings.
- Crystal runs GC.collect before the timer starts and after it stops, so the final collection of each run is untimed; collections during the 360 iterations are still counted. One measurement per configuration, no variance reported.

## Known shortcomings

- Container/idiom win (istringstream plus node-based unordered_map vs open-addressing Hash plus the Boehm GC), not codegen; Crystal allocates a String per word; the Crystal/O3 row without --single-module (3.105 s) loses to every C row; the final GC pass is untimed. 1.79-1.82x over five monthly runs of a subjective AI-assisted suite.
- Workload flaw found by replaying the run.js generator: the fasta LCG (IM 139968) has a period shorter than about 375k draws, so the 50,000-word text is an 18,656-word block repeated about 2.7x; the vocabulary is only 18,623 words, top word 'tea' x9, no tie. A Python replay reproduces checksum 1998586832 as 432 iterations (72 warm-up plus 360 timed); the checksum is valid across languages, but the test is small-vocabulary, not 50k keys. Library or idiom win (istringstream plus whole-text stringbuf copy and a node map against Crystal's open-addressing Hash); all C rows sit at 1.96-2.08 s even with mycc and cproc/QBE, so the time is in libc/libstdc++; Crystal's Hash#update probes twice on a miss. The author wrote Crystal first and calls the C++ and Crystal versions the reference implementations (issue #1).

## Caveats and trade-offs

Mostly a standard-library and idiom comparison (tokenizer, hash container and allocator), so it says little about Crystal's code generation; a C++ version with string_view tokenizing and a flat hash map would likely close the gap (inference, not measured). Crystal allocates a new String per word as well, so the gap is not zero-copy splitting. The Crystal harness runs GC.collect after the timer stops, so the last collection is untimed, while C++ frees its map nodes inside every timed iteration. Only the --release build wins; the suite's Crystal/O3 build (no --single-module) runs 3.105 s, slower than every C and C++ row. LangArena calls itself 'a subjective benchmark' and says AI tools helped translate the tasks between languages; it publishes one measurement per test and configuration (no variance), though the lead is stable across five monthly runs. The headline C/C++ rows are -O2 with hardening flags, but the -O3 -march=native Fast, Unsafe and PGO rows also lose; the Makefiles' LTO flags are link-only. The row was selected because a non-C/C++ language beats every C and C++ configuration; most other tasks in the suite go the other way. Ratios are derived from the results files, not stated by the suite. [retier] The fasta LCG (IM 139968) has a period shorter than about 375k draws, so the 50,000-word text is an 18,656-word block repeated about 2.7x (vocabulary 18,623, top word 'tea' x9); a Python replay reproduces checksum 1998586832 as 432 iterations. Library or idiom win (istringstream plus whole-text stringbuf copy and a node map against Crystal's open-addressing Hash); all C rows sit at 1.96-2.08 s even with mycc and cproc/QBE. The author wrote Crystal first (issue #1).

Crystal peak RSS 8.8 MB vs 5.3 MB for C and 7.8 MB for C++ in the same run.

## Maintenance

Active MIT-licensed suite (41 stars, last commit 2026-10-08, monthly reruns); the author calls it subjective, began it in Crystal and calls C++ and Crystal the reference implementations (issue #1), with other languages AI-assisted translations, so use the row as a language-level data point, not as a component to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for every side (crystal/main.cr class Words, cpp/src/words.cpp, c/src/words.c; workload and checksum in run.js), C/C++ flags in cpp/Makefile and c/Makefile, and exact compiler versions, build commands (crystal build main.cr --release) and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; every quoted runtime matches the Etc::Words-runtime rows. Same tier as the already verified Java, Go, Rust and Zig rows of this test.
- **Verifier notes:** Confirm at A: runtimes match the 2026-10-05 results file (Crystal 0.88 s, C++/G++/PGO 1.587 s best, C++/G++ 1.638 s, C/Clang 1.988 s, RSS 8.8 MB) and four earlier monthly runs give the same 1.79-1.82x lead; metadata checks out (MIT, 41 stars, 16 forks, not a fork, last commit 2026-10-08). Shortcomings to record: container and idiom win (istringstream plus node-based unordered_map vs Crystal's open-addressing Hash and Boehm GC), not codegen; Crystal also allocates a String per word; only the --release build wins (Crystal/O3 row 3.105 s loses to every C row); final GC untimed; single measurement per configuration; subjective AI-assisted suite; prod C/C++ at -O2 (the -O3 rows also lose).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/crystal/main.cr>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/crystal/shard.yml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/src/string.cr>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/src/hash.cr>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/src/compiler/crystal/command.cr>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/issues/1>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/crystal/main.cr>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/crystal/shard.yml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/README.md>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/src/string.cr>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/src/hash.cr>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/src/crystal/hasher.cr>
  - <https://raw.githubusercontent.com/crystal-lang/crystal/1.21.1/src/gc/boehm.cr>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:crystal/kostya/langarena#etc-words`) · [data/wave14/enrich/raw/lang_crystal_kostya_langarena_etc_words.json](../../../data/wave14/enrich/raw/lang_crystal_kostya_langarena_etc_words.json) (enrichment confidence 0.75)

</details>
