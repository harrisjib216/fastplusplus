# Rust: LangArena Etc::Words

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust split_whitespace with borrowed &str keys in std HashMap, 1.55x faster than the best C/C++ build in LangArena Etc::Words.

| | |
|---|---|
| **Beats** | C++ splitting with std::istringstream operator&gt;&gt; and counting in std::unordered_map&lt;std::string,int&gt; (cpp/src/words.cpp; g++ 16 and clang++ 22, libstdc++); best C/C++ row is C++/G++/PGO at 1.587 s. The C rows (c/src/words.c) strdup the whole text per iteration, tokenize with strtok_r and count in uthash with a malloc plus strdup per distinct word, at about 1.96-2.0 s. |
| **Claimed result** | Rust 1.021 s vs C++/G++/PGO 1.587 s (best of the 16 C/C++ configurations), C++/G++/Unsafe 1.631 s, C++/G++ 1.638 s (prod, -O2), C++/G++/Fast 1.651 s (-O3 -march=native) and C/Clang 1.988 s: about 1.55x faster than the best C/C++ row and 1.60x faster than C++/G++ prod (derived from page data). Peak RSS 5.4 MB (C++ 7.8 MB). Other rows also beat every C/C++ row: Crystal 0.88 s, Zig 0.91 s, Go 1.129 s, Rust/PGO 0.898 s. Earlier monthly runs show a smaller Rust lead over the best C/C++ row: 1.18x on 2026-08-14 (1.37 vs 1.623 s), 1.21x on 2026-09-03 (1.329 vs 1.613 s), 1.53x on 2026-09-18 (1.054 vs 1.612 s); the jump followed the 2026-09-06 commit 'rust: count Words with borrowed &str keys' (derived from the results files). |
| **Workload** | Split a generated 50,000-word text (words of 3 to 8 random lowercase letters separated by single spaces) into words, count frequencies in a hash map, then fold the top word, its count and the vocabulary size into a checksum; 360 timed iterations, text generation untimed. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78 GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37; the run's change note says the host moved from Ubuntu to Arch Linux) |
| **Compiler and flags** | C/C++ (c/Makefile, cpp/Makefile; versions from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu package build), libstdc++ (no -stdlib flag), -std=c++20 for C++. Headline 'prod' rows (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3, no -march). 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -ffast-math -fno-stack-protector -fomit-frame-pointer -fvisibility=hidden -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use (GCC). -flto=thin (Fast) and -flto=full (Unsafe) appear only in LDFLAGS while objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO rows were compared (instrumented PGO/Gen rows excluded). Rust: rustc 1.99.0, 'cargo build --release' with the default release profile (opt-level 3, no LTO, no target-cpu flag; rust/Cargo.toml). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Rust iterates split_whitespace() and keys a HashMap with &str slices into the original text (no per-word allocation) against C++ istringstream plus std::string keys in std::unordered_map (this agent's reading of the sources). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In the 2026-10-05 LangArena run on an AMD Ryzen 7 3800X, the Rust test (rustc 1.99.0, default release profile, std HashMap&lt;&str, i32&gt;) took 1.021 s for 360 timed iterations. The best of 16 C/C++ builds, C++/G++ 16.0.1 PGO with std::istringstream and libstdc++ std::unordered_map&lt;std::string,int&gt;, took 1.587 s, and the -O2 prod builds took 1.638 s (G++) and 1.707 s (Clang++ 22.1.8), so Rust is 1.55x and 1.60x faster (derived from the results file). Peak RSS was 5.4 MB against 7.8 MB.

## Use it when

- Word or token frequency counts over an in-memory buffer that outlives the map, where borrowed keys remove all per-word allocation.
- Whitespace-separated ASCII or UTF-8 text (split_whitespace also handles Unicode whitespace) with vocabularies in the tens of thousands; this test has 18,623 distinct words of 3-8 bytes.
- Choosing between standard-library-only implementations of a text-counting tool, where Rust's defaults (slice tokenizer, flat map) beat the C++ defaults (istringstream, std::unordered_map).
- Quick tools where you would otherwise write the C++ istringstream loop: the Rust idiom is just as short and about 1.6x faster here.

## Skip it when

- If you are staying in C++: split manually into std::string_view and count in a flat map with heterogeneous lookup (absl::flat_hash_map, boost::unordered_flat_map or ankerl::unordered_dense, all in this catalogue's hash-maps-sets category). That probably closes the gap (inference; the suite allows only standard containers).
- Streaming input or buffers freed before the counts are used: borrowed keys need the whole text alive. With owned String keys the Rust lead was only 1.18-1.28x in the June to early-September 2026 runs.
- Very large vocabularies, long keys or untrusted input: the default SipHash-1-3 is the slow but HashDoS-resistant choice. A faster hasher is only safe on trusted input, and nothing beyond about 19k keys was measured.
- As a language codegen claim: Crystal 0.88 s, Zig 0.91 s and Go 1.129 s also beat every C/C++ row. The C rows (1.96-2.04 s) strdup the whole text every run and malloc plus strdup each new word into uthash.
- Close calls: one measurement per configuration, and C++/G++ prod drifted between 1.611 and 1.678 s across six monthly runs with unchanged cpp/src/words.cpp.

## How it is fast

Zero-copy tokenizing: split_whitespace yields slices of the original text, and the map stores those slices as keys, so counting never copies or allocates a word; the only allocations are the growth steps of hashbrown's flat SwissTable array. The C++ side extracts every token through std::istringstream operator&gt;&gt; into a std::string, then inserts into node-based std::unordered_map&lt;std::string,int&gt;, which allocates a node for each of the 18,623 distinct words per run (words of at most 8 characters fit libstdc++'s 15-character small-string buffer, so keys add no extra allocation). Rust still pays SipHash-1-3 on every word. Before 2026-09-06 the Rust test allocated an owned String for every one of the 50,000 tokens, more allocations than C++, and still led by 1.18-1.28x. That points at the istringstream tokenizer and the node map as the main C++ costs (inference; no profile published).

## Compared with alternatives

Crystal (0.88 s) and Zig (0.91 s, 4.2 MB) rows of the same test are faster, and Go (1.129 s, 11.3 MB) is close. Pick the Rust idiom when you want borrow-checked zero-copy keys with low memory (5.4 MB peak RSS) in a memory-safe default build. For a C++ codebase, the flat maps in hash-maps-sets plus string_view tokenizing are the direct fix.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Rust std: str::split_whitespace and std::collections::HashMap); the benchmark crate's serde_json and regex serve other tests and the harness |
| **Minimum toolchain** | Rust edition 2021 (rust/Cargo.toml); measured with rustc 1.99.0 and the default release profile (opt-level 3, 16 codegen units, no LTO, no target-cpu) |
| **Platforms** | Measured only on x86-64 Linux (AMD Ryzen 7 3800X); the code is portable safe Rust with nothing platform-specific |
| **Thread safety** | Not shared: the map is local to each run and borrows the text immutably, so the borrow checker prevents mutating the text while the map lives. The benchmark is single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- The current margin partly reflects less work on the Rust side. Commit 0d31537 (2026-09-06, 'rust: count Words with borrowed &str keys', AI co-authored) switched to borrowed keys; its message says 'C++ keys its unordered_map by owned std::string and Crystal's split allocates a String per word', so the change removes a cost the reference implementations still pay. The Rust lead over the best C/C++ row went from 1.18-1.28x (2026-06-16 to 2026-09-03) to 1.53-1.55x (2026-09-18, 2026-10-05), while cpp/src/words.cpp stayed unchanged since 2026-04-24. The C++ version was never given the equivalent string_view rewrite.
- Harness check, no flaw found. My Python replay of the workload reproduces the expected checksum 1998586832 as 432 runs (72 untimed warm-up plus 360 timed) of 193,525,383. The fasta LCG's period of 139,968 makes the text repeat, so it holds 18,623 distinct words, and the top word ('tea', 9 times, next best 6) is unique: Rust's max_by_key over a randomly ordered map and C++'s first-maximum loop agree. benchmarks.rb records a runtime only on '&lt;test&gt;: OK in Xs' output and runs each test in its own process; neither side pre-sizes its map.
- The C++ generator computes a word length as Helper::next_int(word_len) + Helper::next_int(3) + 3, whose operand evaluation order C++ leaves unspecified (Rust evaluates left to right). The matching checksums show that both G++ and Clang++ evaluated it left to right here, but another compiler could silently generate a different text.
- Build settings barely matter for Rust here: Rust/WMO with codegen-units 1 is 0.998 s and Rust/PGO 0.898 s against 1.021 s for the headline row, so the time sits in tokenizing, hashing and memory rather than in missed inlining (inference). The C/C++ toolchain is GCC 16.0.1 '(experimental)' trunk and Clang 22.1.8; the Makefiles' -flto flags are link-only, so no LTO actually happens.

## Known shortcomings

- 1.55x over the best C++ row (1.021 vs 1.587 s) comes from idiom and container choices (istringstream, std::string keys and a node-based unordered_map against borrowed &str SwissTable keys); the lead was only 1.2x before the 2026-09-06 Rust commit; single run of a subjective AI-assisted suite, LTO flags link-only.
- Asymmetric work behind about half the margin: commit 0d31537 (2026-09-06) switched the Rust version to borrowed &str keys, and its own message says the C++ reference still pays owned std::string keys (cpp/src/words.cpp unchanged since 2026-04-24); the lead went from 1.18-1.28x to 1.53-1.55x. A replay reproduces checksum 1998586832 (432 runs) with 18,623 distinct words and a unique top word 'tea'. Latent issue: the C++ generator's `next_int(word_len) + next_int(3) + 3` has unspecified evaluation order, harmless here.

## Caveats and trade-offs

Standard-library and idiom comparison (istringstream tokenizer plus node-based unordered_map against a borrowed-slice tokenizer and an open-addressing map), not code generation; a C++ version with std::string_view keys and a flat hash map would likely close the gap. Half the current margin comes from the 2026-09-06 Rust change to borrowed &str keys (1.2x before, 1.55x after). The C version does extra work (strdup of the whole text each iteration, malloc plus strdup per distinct word). The same test appears under Java in the wave jitaot file. LangArena calls itself 'a subjective benchmark' and says AI tools helped translate the tests between languages. One measurement per test and configuration (no variance reported), although the harness checks each run's checksum against run.js. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3 -march=native Fast and Unsafe rows and the PGO rows also lose. Ratios are derived from the results file, not stated by the suite. Rows were picked as text tests where a non-C row beats every C and C++ row; most other text tests go the other way (Base64::Encode and Base64::Decode, where C is about 3x faster than Rust; Distance::Jaro is a tie). [retier] Enricher: about half of the current margin reflects less work on the Rust side; commit 0d31537 (2026-09-06) switched the Rust version to borrowed &str keys, and its own message says the C++ reference still pays owned std::string keys (cpp/src/words.cpp unchanged since 2026-04-24); the lead went from 1.18-1.28x (2026-06-16 to 2026-09-03) to 1.53-1.55x (2026-09-18, 2026-10-05). A replay reproduces checksum 1998586832 (432 runs) with 18,623 distinct words. Latent issue: the C++ generator's `next_int(word_len) + next_int(3) + 3` has unspecified evaluation order, harmless here.

Zero-copy word keys; the Go and Rust versions keep a reference to the whole text while the map is alive.

## Maintenance

LangArena is MIT-licensed and actively maintained, re-run about monthly (last commit 2026-10-08, 41 stars). This is a benchmark row rather than a library: copy the idiom (borrowed &str keys over a live buffer), and note that about half of today's margin dates from a September 2026 Rust-only change.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for both sides (rust/src/benchmarks/words.rs, cpp/src/words.cpp, c/src/words.c; workload and checksum in run.js), C/C++ flags in cpp/Makefile and c/Makefile, Rust profile in rust/Cargo.toml, and compiler versions, build commands and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; an independent multi-language suite. Every quoted number matches the Etc::Words-runtime entries.
- **Verifier notes:** Confirm at A: numbers match the 2026-10-05 results file exactly and metadata checks out (MIT, 41 stars, last commit 2026-10-08, not a fork, not archived). Shortcomings to record: idiom and container comparison rather than a language win; margin rose from 1.2x to 1.55x after the Rust test switched to borrowed keys on 2026-09-06; C++ code uses istringstream and std::string keys where string_view keys would remove copies; single run; subjective, AI-assisted suite.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-35 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/words.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/helper.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
  - <https://github.com/kostya/LangArena/commits/master/rust/src/benchmarks/words.rs>
  - <https://github.com/kostya/LangArena/tree/master/results>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/helper.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/words.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/words.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/words.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/benchmarks.rb>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-07-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-06-16-kostya-ms7c37.js>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://github.com/kostya/LangArena/commits/master/rust/src/benchmarks/words.rs>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/words.cpp>
  - <https://github.com/kostya/LangArena/commit/0d31537>
  - <https://github.com/kostya/LangArena/commit/0d31537.patch>
  - <https://github.com/kostya/LangArena/pull/11>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/collections/hash/map.rs>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc%2B%2B-v3/include/bits/basic_string.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/kostya/langarena#etc-words`) · [data/wave14/enrich/raw/lang_rust_kostya_langarena_etc_words.json](../../../data/wave14/enrich/raw/lang_rust_kostya_langarena_etc_words.json) (enrichment confidence 0.72)

</details>
