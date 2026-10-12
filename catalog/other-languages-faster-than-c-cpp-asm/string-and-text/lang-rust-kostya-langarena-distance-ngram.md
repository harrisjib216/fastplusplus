# Rust: LangArena Distance::NGram

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust std HashMap counting 4-grams, 1.54x faster than the best C/C++ build (std::unordered_map) in LangArena Distance::NGram.

| | |
|---|---|
| **Beats** | C++ using std::unordered_map&lt;uint32_t,int&gt; for 4-gram counts (g++ 16, clang++ 22); best C/C++ row is C++/Clang++/PGO at 0.822 s, C/Clang is 1.811 s |
| **Claimed result** | Rust 0.533 s vs C++/G++ 0.863 s and C++/Clang++ 0.877 s (prod, -O2), C++/G++/Fast 0.85 s (-O3 -march=native), best of the 16 Clang/GCC C and C++ configurations C++/Clang++/PGO 0.822 s, C/Clang 1.811 s: about 1.54x faster than the best C/C++ row and 1.62x faster than C++/G++ prod (derived from page data). Rust/WMO (codegen-units 1) 0.388 s. Peak RSS 4.3 MB vs 6.6-7.1 MB for the C++ rows. |
| **Workload** | For 10 generated string pairs (lengths 4 to 20,003 over a 10-letter alphabet, so at most 10,000 distinct 4-grams), count 4-gram frequencies of each string in two hash maps (reserved to the string length) and compute the n-gram overlap score; 100 timed iterations after 20 untimed warm-up iterations (run.js). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37) |
| **Compiler and flags** | C/C++ (cpp/Makefile, c/Makefile; versions and build commands from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu snapshot package), libstdc++ (no -stdlib flag). Headline 'prod' rows (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections; C++ adds -std=c++20. 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -DNDEBUG -pipe -fno-stack-protector -fomit-frame-pointer -ffast-math -fvisibility=hidden -fno-common -fstrict-overflow -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use -fprofile-correction (GCC). The Makefiles pass -flto=thin (Fast) and -flto=full (Unsafe) only on the link line while the objects are compiled without -flto, so no link-time optimisation actually takes place (inference from the Makefiles). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO configurations were compared (instrumented PGO/Gen rows excluded). Rust: rustc 1.99.0 'cargo build --release' (default release profile from rust/Cargo.toml: opt-level 3, 16 codegen units, no LTO, no target-cpu). Both harnesses run 20 percent untimed warm-up iterations. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. Rust's std HashMap (hashbrown SwissTable) is flat open addressing, while C++ std::unordered_map&lt;uint32_t,int&gt; allocates a node per distinct 4-gram, and the test builds two maps per string pair (this agent's inference from the containers used). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In the 2026-10-05 LangArena run on an AMD Ryzen 7 3800X, the Rust test (rustc 1.99.0, default release profile, std HashMap with SipHash) took 0.533 s for 100 timed iterations. The best of 16 C/C++ builds, C++/Clang++ 22.1.8 PGO with libstdc++ std::unordered_map&lt;uint32_t,int&gt;, took 0.822 s, and the -O2 prod builds took 0.863 s (G++ 16.0.1) and 0.877 s (Clang++), so Rust is 1.54x and 1.62x faster (derived from the results file). Peak RSS was 4.3 MB against 6.6-7.1 MB.

## Use it when

- Counting small integer keys (packed n-grams, k-mers, IDs) in a map that is built, probed and dropped per call, where a node-based map spends its time in malloc and free.
- Picking a language for text-similarity or k-mer counting code that must stick to standard containers: Rust's default HashMap is already a flat SwissTable, while C++'s std::unordered_map is not.
- Maps of up to about 10^4 keys pre-sized with with_capacity, as measured (at most 8,647 keys per map, 10,000 possible 4-grams).
- Evidence that std::unordered_map, not the compiler, is the bottleneck in a C++ counting loop before you swap containers.

## Skip it when

- If you are staying in C++: replacing std::unordered_map with absl::flat_hash_map, boost::unordered_flat_map or ankerl::unordered_dense (all in this catalogue's hash-maps-sets category) probably closes the gap without a rewrite. This is inference; the suite only allows standard containers (the maintainer closed PR #11, an HPPC primitive-map patch for the Java NGram test, on that ground).
- Hash-bound workloads on trusted input: the default SipHash-1-3 is slow for u32 keys. A faster hasher via with_capacity_and_hasher (FxHash, foldhash) would probably go further than the measured row, but that is not measured.
- Key sets far larger than cache: the test never holds more than 8,647 keys per map, so there is no evidence for millions of keys.
- As a Rust-beats-C++ codegen claim: Zig 0.52 s, C# 0.516 s, Julia 0.58 s, Go 0.603 s and even Rust compiled to WebAssembly under Node (0.473 s) beat every C/C++ row, and the C rows (uthash, a malloc per distinct gram, 1.79-1.84 s) are slower still.
- Decisions that hinge on a few percent: one measurement per configuration, and the C++/G++ prod row drifted between 0.839 and 0.908 s across six monthly runs with unchanged code.

## How it is fast

Rust's std HashMap is hashbrown, a port of Google's SwissTable (open addressing with quadratic probing and SIMD lookup of control bytes), so keys and counts sit inline in the reserved table and an insert does not allocate. libstdc++ std::unordered_map is node-based: each of the 122,691 distinct-key inserts per run (from my replay of the workload) allocates a node that is freed again when the map dies inside the timed loop, about 12.3 million malloc/free pairs over 100 timed runs, and every probe walks bucket-to-node pointers. Rust wins although it hashes with SipHash-1-3, which its own docs say other hashers beat for integer keys, while libstdc++ hashes integers with the identity function. The win comes from the container layout, not from code generation.

## Compared with alternatives

Against the Zig (0.52 s, 3.4 MB) and Go (0.603 s, 12.0 MB) rows of the same test, Rust prod is in the same band (0.533 s, 4.3 MB) but has the best tuned builds (0.388 s with codegen-units 1, 0.387 s with PGO), so pick it when you want a memory-safe default map with low RSS and headroom from build settings. If you must stay in C++, the hash-maps-sets entries (abseil, Boost.Unordered, unordered_dense) are the direct fix.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Rust std::collections::HashMap); the benchmark crate's serde_json, regex and similar dependencies serve other tests and the harness |
| **Minimum toolchain** | Rust edition 2021 (rust/Cargo.toml); measured with rustc 1.99.0 and the default release profile (opt-level 3, 16 codegen units, no LTO, no target-cpu) |
| **Platforms** | Measured only on x86-64 Linux (AMD Ryzen 7 3800X); the code is portable safe Rust with nothing platform-specific |
| **Thread safety** | Not shared: each call builds two local maps; HashMap has no internal locking and mutation needs an exclusive &mut borrow. The benchmark is single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness check, no flaw found. My Python replay of the run.js workload (fasta LCG, period 139,968) gives 10 pairs with 213,051 characters, at most 8,647 keys per map, 122,691 distinct-key inserts and 320,106 hash operations per run, and reproduces the expected checksum 397440 as 120 runs (20 untimed warm-up plus 100 timed) of 3,312. benchmarks.rb records a runtime only when the binary prints '&lt;test&gt;: OK in Xs', runs each test in its own process and takes peak RSS from /usr/bin/time; both harnesses time only run_all with a monotonic clock, and both include map destruction.
- The Rust test was tuned on 2026-09-06 (commit 9ebdaec, 'reuse the NGram map entry', AI co-authored like much of the suite). Before it, Rust looked the s2 gram up a second time and led the best C/C++ row by 1.32-1.40x (2026-06-16 to 2026-09-03 results); afterwards the lead is 1.51-1.54x. The change matches the C++ try_emplace logic, so the current figure is the like-for-like one. cpp/src/distance.cpp is unchanged since 2026-04-24.
- The headline Rust row is not Rust's best: the default release profile uses 16 codegen units, and Rust/WMO (codegen-units 1, 0.388 s) and Rust/PGO (0.387 s) are about 2.1x faster than the best C/C++ row. Rust also builds without -march=native, while the C++ Fast, Unsafe and PGO rows lose despite -O3 -march=native or profile data.
- The C/C++ toolchain is GCC 16.0.1 '(experimental)' trunk r16-8246 and Clang 22.1.8. The -flto flags in cpp/Makefile appear only on the link line (objects compile without -flto), so the 'LTO' variants get no LTO; that matters little here because the hot code is in one file.

## Known shortcomings

- Container win: Rust's SwissTable HashMap (even with SipHash) vs node-based std::unordered_map, same algorithm line for line; Zig, C#, Go and Julia also beat the C++ row. Single run, subjective AI-assisted suite, C/C++ at -O2 with inert link-only -flto.
- No harness flaw: a Python replay reproduces checksum 397440 (120 runs x 3,312), with at most 8,647 keys per map and 122,691 node inserts per run. The win is the container, not codegen: SwissTable against node-based std::unordered_map, and Rust wins despite SipHash against libstdc++'s identity hash. Commit 9ebdaec (2026-09-06) removed an extra Rust lookup to match C++ try_emplace; the lead was 1.32-1.40x before and 1.51-1.54x after, now like-for-like. Rust/WMO 0.388 s and Rust/WASM/Node 0.473 s also beat every C and C++ row.

## Caveats and trade-offs

Container comparison: a C++ open-addressing map (absl::flat_hash_map, boost::unordered_flat_map) would likely close the gap (inference, not measured), and the suite only uses std::unordered_map. Other languages also beat every C/C++ row: Zig 0.52 s, C#/JIT 0.516 s (a separate verified record of the same test), Go 0.603 s, Julia 0.58 s. The C version (uthash, one malloc per distinct gram) is slower still at 1.789-1.844 s for the non-instrumented Clang/GCC rows. LangArena calls itself 'a subjective benchmark' and says AI tools helped translate the tests between languages. The suite publishes one measurement per test and configuration (no variance). The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3 Fast, Unsafe and PGO variants were also compared and Rust still wins; the Makefiles' -flto flags are link-only, so the 'LTO' builds probably get no LTO. The per-benchmark ratios are derived from the results file, not stated by the suite. Rows were picked by the search agent as text tests where a Rust, Zig or Go production row beats every C and C++ row; most other text tests in the suite go the other way (for example Base64::Encode and Base64::Decode, where C is about 3x faster than Rust, and Distance::Jaro, which is a tie). [retier] Enricher: no harness flaw; a Python replay reproduces checksum 397440 (120 runs x 3,312), with at most 8,647 keys per map and 122,691 node inserts per run. The win is the container (SwissTable against node-based std::unordered_map), and Rust wins despite SipHash against libstdc++'s identity hash. Commit 9ebdaec (2026-09-06) removed an extra Rust lookup to match C++ try_emplace; the lead was 1.32-1.40x before and 1.51-1.54x after. Rust/WMO 0.388 s and Rust/WASM/Node 0.473 s also beat every C and C++ row.

Flat hash tables use less memory per entry than node-based std::unordered_map.

## Maintenance

LangArena is MIT-licensed and actively maintained, re-run about monthly (last commit 2026-10-08, 41 stars); this is a benchmark row rather than a library, so copy the pattern (u32-packed n-grams in a pre-sized flat map), and in C++ get the same effect by switching to a flat hash map.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public code for both sides (rust/src/benchmarks/distance.rs NGram::ngram vs cpp/src/distance.cpp NGram::ngram, c/src/distance.c; workload in run.js), C/C++ flags in the Makefiles, Rust profile in rust/Cargo.toml, exact compiler versions and the CPU (AMD Ryzen 7 3800X) in results/2026-10-05-kostya-ms7c37.js; both sides pack the same 4-grams into their standard hash maps with the same reserve, matching the already verified C# row of this test.
- **Verifier notes:** Confirm at A: runtimes match the results file (Rust 0.533 s, C++/G++ 0.863 s, C++/Clang++/PGO 0.822 s best, C/Clang 1.811 s, RSS 4.3 MB), the Rust and C++ ngram functions are line-for-line the same algorithm, and metadata checks out (MIT, 41 stars, last commit 2026-10-08). Shortcomings to record: container comparison (SwissTable vs node-based std::unordered_map), not codegen; Zig, C#, Go and Julia also win; single measurement per configuration; subjective AI-assisted suite; prod C/C++ rows at -O2 (the -O3 rows also lose); LTO flags inert.
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
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://github.com/kostya/LangArena/tree/master/rust/src/benchmarks>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/distance.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/distance.c>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/helper.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/distance.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/distance.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/distance.c>
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
  - <https://github.com/kostya/LangArena/commits/master/rust/src/benchmarks/distance.rs>
  - <https://github.com/kostya/LangArena/commits/master/cpp/src/distance.cpp>
  - <https://github.com/kostya/LangArena/commit/9ebdaec>
  - <https://github.com/kostya/LangArena/pull/11>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/issues/3>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/collections/hash/map.rs>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc%2B%2B-v3/include/bits/functional_hash.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/kostya/langarena#distance-ngram`) · [data/wave14/enrich/raw/lang_rust_kostya_langarena_distance_ngram.json](../../../data/wave14/enrich/raw/lang_rust_kostya_langarena_distance_ngram.json) (enrichment confidence 0.75)

</details>
