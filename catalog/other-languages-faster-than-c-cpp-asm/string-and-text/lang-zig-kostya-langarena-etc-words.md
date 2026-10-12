# Zig: LangArena Etc::Words

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig word-frequency count with zero-copy slice keys in a StringHashMap; 1.74x faster than every C/C++ build in LangArena Etc::Words.

| | |
|---|---|
| **Beats** | C++ splitting with std::istringstream and counting in std::unordered_map&lt;std::string,int&gt; (g++ 16, clang++ 22); best C/C++ row is C++/G++/PGO at 1.587 s, the C rows use uthash with a strdup per word at about 1.99 s |
| **Claimed result** | Zig (ReleaseSafe) 0.91 s vs C++/G++ 1.638 s (prod, -O2), C++/G++/Fast 1.651 s and C++/G++/Unsafe 1.631 s (-O3 -march=native), and the best of all 16 C/C++ rows C++/G++/PGO 1.587 s: about 1.74x faster than the best C/C++ row (derived from page data). The C rows (uthash, strdup per key) are slower still: C/Gcc/Fast 1.963 s, C/Clang 1.988 s. Zig/Unchecked (ReleaseFast) runs 0.57 s, about 2.8x faster than the best C/C++ row (derived). Rust (1.021 s) and Go (1.129 s) also beat every C/C++ row. Peak RSS 4.2 MB for Zig vs 7.8 MB for C++/G++. The lead is stable across the five monthly runs checked: 1.71x on 2026-07-14 (Zig 0.941 s vs C++/G++ 1.611 s), 1.72x on 2026-08-14 and 2026-09-03, 1.71x on 2026-09-18 and 1.74x on 2026-10-05 (all derived from page data; Zig 0.16.0 before 2026-10-05). |
| **Workload** | Split a large generated text into words and count word frequencies, then report the most frequent word and the vocabulary size. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37; the run notes say the host moved from Ubuntu to Arch Linux for this run) |
| **Compiler and flags** | C/C++: Clang 22.1.8 (official LLVM release tarball; docker/base_clang points cc, c++, gcc and g++ at clang via update-alternatives and sets no -stdlib flag, so the clang rows link the system libstdc++) and GCC 16.0.1 20260322 (trunk, Ubuntu build), -std=c++20, glibc malloc. Headline 'prod' build (cpp/Makefile CXXFLAGS_PROD, c/Makefile CFLAGS_PROD): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3). The same suite also builds 'Fast' (-O3 -march=native -mtune=native -pipe ..., -flto=thin at link), 'Unsafe' (-O3 -march=native -ffast-math ..., -flto=full at link) and 'PGO' (-O2 plus -fprofile-instr-use or -fprofile-use) variants; the LTO flags appear only in LDFLAGS, so those builds probably get no real LTO (inference from the Makefiles). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared (instrumented PGO/Gen rows and the author's mycc/cproc compilers excluded; they are slower anyway). Zig 0.17.0 'zig build build-zig': zig/build.zig builds this 'Zig' row with optimize = .ReleaseSafe (LLVM release optimisation with runtime safety checks kept) and b.standardTargetOptions(.{}), which defaults to the native host CPU, so it is closer to -O3 -march=native with bounds checks than to the generic -O2 prod C/C++ build; 'Zig/Unchecked' is the same source at .ReleaseFast. Go 1.27.1 (go.mod says go 1.24.0) 'go build -buildvcs=false' with default settings (no opt levels in Go); 'Go/Opt' adds -trimpath and a static link. Rust: rustc 1.99.0 'cargo build --release'. Versions and build/run commands from the results file's version, build-cmd and run-cmd fields. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Zig splits with std.mem.splitScalar and keys a std.StringHashMap with slices into the original text inside an arena allocator, so no per-word allocation or copy happens; the C++ test reads with istringstream &gt;&gt; std::string and copies each key into std::unordered_map (this agent's reading of the sources). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

On an AMD Ryzen 7 3800X (results 2026-10-05), the Zig 0.17.0 ReleaseSafe build ran 360 timed iterations in 0.91 s against 1.587 s for the best of the 16 GCC 16.0.1 and Clang 22.1.8 C and C++ builds (C++/G++/PGO; libstdc++ istringstream plus unordered_map), 1.638 s for the -O2 prod C++/G++ row and 1.96-2.0 s for the C uthash rows: about 1.74x, derived from page data. The four earlier monthly runs (Zig 0.16.0) give 1.71-1.73x.

## Use it when

- Batch word or token counting in Zig over in-memory ASCII text that outlives the map, so the keys can stay slices into the text.
- Build-read-drop maps: one count per batch, read once, then freed in a single arena.deinit (here 50,000 tokens, 18,623 distinct, about 37% first occurrences per pass).
- Memory-tight jobs: Zig peaked at 4.2 MB RSS on this test against 7.5-7.9 MB for the C++ rows, 5.1-5.5 MB for C, 5.4 MB for Rust and 11.3 MB for Go.
- As evidence when reviewing C++ text tooling: a tokenizer built on std::istringstream and std::unordered_map&lt;std::string,int&gt; loses 1.7x even to bounds-checked Zig on this input shape.

## Skip it when

- Inside a C++ codebase: rewrite the C++ with std::string_view tokens and an open-addressing map instead; the suite never measured such a version, so how much of the 1.74x it would recover is unmeasured.
- When the source text is freed or modified while the map is alive: the keys are slices into it and would dangle; duplicating keys (allocator.dupe) gives up the zero-copy advantage.
- Long-lived or incrementally grown maps: the code never reserves capacity, and an arena does not free the tables discarded on each grow, so memory comes back only at arena.deinit.
- Text with tabs, newlines or runs of spaces: splitScalar splits on ' ' only, skips the empty tokens and keeps '\t' or '\n' inside tokens, unlike operator&gt;&gt;, which skips all whitespace.
- When you need the fastest production row: Crystal (0.88 s) edges Zig (0.91 s) on the same test; only the unchecked ReleaseFast build (0.57 s) leads clearly, and the suite files that build under 'hack'.

## How it is fast

Allocation and container choice, not code generation. splitScalar yields slices into the original text and getOrPut stores those slices as the keys, so no word is copied or individually allocated; std.StringHashMap is an open-addressing table (Wyhash with seed 0, mem.eql compare, power-of-two capacity, 80% max load, one metadata byte per slot) whose storage comes from the arena and is released by one arena.deinit. The C++ baseline copies the 325 KB text into a std::istringstream every iteration, extracts each token with operator&gt;&gt; into a std::string and try_emplaces it into a node-based std::unordered_map&lt;std::string,int&gt;, which allocates a node holding its own key copy for each of the 18,623 distinct words per iteration; the C version strdup()s the whole text, tokenizes with strtok_r and mallocs an entry plus a strdup'd key per distinct word in uthash. The ReleaseFast build of the same source (Zig/Unchecked) runs 0.57 s, so safety checks and other ReleaseSafe differences take about 37% of the 0.91 s production time.

## Compared with alternatives

Among the catalogued Etc::Words rows, Zig has the lowest peak RSS (4.2 MB against Crystal 8.8, Rust 5.4 and Go 11.3) and the fastest unchecked build (0.57 s), while Crystal's production row is marginally faster (0.88 vs 0.91 s) and Rust (1.021 s) and Go (1.129 s) trail; pick the Zig pattern when you want explicit control of key lifetime and allocation. For production text tools, the catalogued CLI siblings (huniq, cuniq, runiq) are real programs; this row is only a code pattern.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for this task (Zig std: ArenaAllocator, StringHashMap, mem.splitScalar); the suite's build.zig links libc and pcre2-8 and pulls the csv-zero package for other tests |
| **Minimum toolchain** | Zig 0.16 std APIs (the harness uses std.process.Init and std.Io); measured with Zig 0.16.0 (July to September 2026 runs) and 0.17.0 (2026-10-05) |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X) built for the host CPU (b.standardTargetOptions default); nothing platform-specific in words.zig |
| **Thread safety** | Not documented; the std.HashMap source read has no locking (only a safe-mode pointer-stability assertion), and the benchmark is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw against the suite's own rules: the author's first rule (issue #1) is 'Try to use the same semantics, same constructs and containers - this is most important', and the Crystal reference (crystal/main.cr) builds a fresh String per word with String#split, yet the Zig port keys its map with zero-copy slices inside an arena while C++ copies every new key into a heap node. Much of the 1.74x is that implementation choice, not Zig.
- Checksums reproduce: a Python replay of the suite's LCG gives a 325,090-byte text with 18,623 distinct words and a unique top word ('tea', 9 times), and reaches run.js's 1998586832 only as 432 runs (72 untimed warm-up plus 360 timed). Zig keeps the first maximum in hash-iteration order, so a tied top count would make the checksum order-dependent; this input has no tie.
- The C++ generator computes Helper::next_int(word_len) + Helper::next_int(3) + 3, whose operand evaluation order C++ leaves unspecified (Zig and C sequence the two calls left to right); a compiler that evaluated right to left would build a different text and fail the checksum rather than skew timing. The results file does not record checksum status.
- One timing per configuration per monthly run, no variance; the README itself says its ranking reflects 50 tasks, 'not my pick for a single test'. Code and lead were stable: zig/src/words.zig is unchanged since 2026-02-28 and cpp/src/words.cpp since 2026-04-24, and Zig led the best C/C++ row by 1.712x, 1.725x, 1.716x, 1.708x and 1.744x from 2026-07-14 to 2026-10-05 (derived from the results files).

## Known shortcomings

- Idiom/container win (zero-copy slice keys, flat StringHashMap and an arena vs istringstream plus node-based unordered_map), not codegen; the Zig production row is ReleaseSafe for the native CPU while production C/C++ rows are -O2 (the -O3 -march=native rows also lose). 1.71-1.74x holds across 5 monthly runs of a subjective AI-assisted suite.
- The Zig port breaks the suite's own first rule (issue #1: 'same semantics, same constructs and containers'): it keys its map with zero-copy slices into the text inside an arena, while the Crystal reference builds a String per word and C++ copies every new key into a heap node, so most of the 1.74x is that idiom, not codegen. Timing harness is the same as C and C++ and checksum 1998586832 replays (432 runs). Latent only: the C++ generator's next_int + next_int evaluation order is unspecified. Which allocator init.gpa uses in ReleaseSafe was not established (codeberg and ziggit blocked).

## Caveats and trade-offs

Standard-library and idiom comparison, not code generation: Zig keys a flat hash map with zero-copy slices into the text inside an arena, while the C++ test uses istringstream plus a node-based unordered_map with copied keys and the C test strdup()s the text and every key; a C++ version with std::string_view keys and a flat hash map would likely close most of the gap (inference, not measured). Both sides do the same split, count and max-scan over the same text and the suite checks the checksum. Zig's production row is ReleaseSafe built for the native CPU (b.standardTargetOptions default), while the prod C/C++ rows are generic x86-64 -O2 with hardening flags; the -O3 -march=native Fast and Unsafe rows and the PGO rows were also compared and still lose, and the Makefiles pass the LTO flags only at link time, so no C/C++ row had real LTO. The same test is catalogued for Java (lang:java/kostya/langarena#etc-words), where the same C++ weakness drives the result. LangArena's README calls it not an objective, peer-reviewed or industry-standard suite (rules and library choices are the author's judgment) and says AI tools helped translate the tests from Crystal, with the author reviewing them. Each configuration is timed once per monthly run (no repeats or variance within a run); every language, C and C++ included, runs 20% of the iterations as untimed warm-up and checksums are verified. The per-benchmark ratios are derived from the results files, not stated by the suite. Rows were picked by the search agent as text tests where a Rust, Zig or Go production row beats every C and C++ row; most other text tests in the suite go the other way (for example Base64::Encode and Base64::Decode, where C is about 3x faster than Rust, and Distance::Jaro, a tie). [retier] Enricher: the Zig port breaks the suite's first rule (issue #1: 'same semantics, same constructs and containers'); it keys its map with zero-copy slices into the text inside an arena while the Crystal reference builds a String per word and C++ copies every new key into a heap node, so most of the 1.74x is that idiom. Checksum 1998586832 replays (432 runs). Which allocator init.gpa uses in ReleaseSafe was not established.

Zero-copy word keys and arena allocation; the map and its keys die with the arena.

## Maintenance

Active MIT-licensed suite (41 stars, last commit 2026-10-08, monthly reruns) and words.zig is a copyable 130-line pattern, but no timing bug was found: the C, C++ and Zig harnesses time run_all the same way after a 20% untimed warm-up and verify the checksum; the flaw is that the Zig port uses zero-copy keys and an arena that the Crystal reference and the suite's 'same containers' rule do not, so read the row as 'the C++ idiom is slow', not 'Zig codegen beats C++'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for every side (zig/src/words.zig, cpp/src/words.cpp, c/src/words.c; workload in run.js: 50,000 words, word_len 4, 360 iterations), build modes in zig/build.zig (ReleaseSafe), flags in cpp/Makefile and c/Makefile, compiler versions, build commands and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; the -O3 -march=native C/C++ rows lose too, and the margin is stable across five monthly runs, so A stands (same tier the Java Etc::Words entry got).
- **Verifier notes:** Confirm at A: every number matches the Etc::Words-runtime rows of the 2026-10-05 results file, and four earlier monthly runs give the same 1.71-1.72x lead. Shortcomings to record: a container and idiom win (zero-copy slice keys, flat StringHashMap and arena against istringstream plus node-based unordered_map with copied keys), Zig production row is ReleaseSafe for the native CPU against generic -O2 prod C/C++ (the -O3 -march=native rows also lose), one timing per configuration per run, subjective AI-assisted suite. Metadata checks out (MIT, 41 stars, 16 forks, not a fork, last commit 2026-10-08).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-36 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/clang_cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base_clang>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.h>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://github.com/kostya/LangArena/tree/master/zig>
  - <https://github.com/kostya/LangArena/tree/master/zig/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/words.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/benchmark.zig>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/main.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/benchmark.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/helper.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/words.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.h>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/helper.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/crystal/main.cr>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena/commits/master/zig/src/words.zig>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/words.cpp>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/issues/1>
  - <https://github.com/kostya/LangArena/tree/master/crystal>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/hash_map.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/build.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/start.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/process.zig>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/kostya/langarena#etc-words`) · [data/wave14/enrich/raw/lang_zig_kostya_langarena_etc_words.json](../../../data/wave14/enrich/raw/lang_zig_kostya_langarena_etc_words.json) (enrichment confidence 0.75)

</details>
