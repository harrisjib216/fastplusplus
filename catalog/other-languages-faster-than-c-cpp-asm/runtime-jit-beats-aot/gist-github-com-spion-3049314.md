# LuaJIT vs C and C++ hash-table word count (spion gist)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Lua` · `no license` · 🔴 abandoned

> 2012 gist where LuaJIT's plain table counts words from a 19-word sentence faster than naive C and std::unordered_map versions.

| | |
|---|---|
| **Beats** | C (hand-written chained hash table, gcc -O3) and C++ (std::unordered_map&lt;string,int&gt; with a custom hash, g++ -O3 -std=gnu++0x) |
| **Claimed result** | Original 2012 'benchmark' transcript (one `time` run each, real time): C 0.234 s, C++ 0.321 s, Node 0.317 s, LuaJIT 0.161 s, so LuaJIT 1.45x faster than C and 1.99x faster than C++ (derived from page data). Author's 2020-05-26 rerun comment (no versions or hardware): C 0.173 s, C++ 0.36 s, Node 0.5 s, LuaJIT 0.08 s (2.2x vs C, 4.5x vs C++, derived from page data); at 10x iterations LuaJIT 0.76 s, C 1.44 s, C++ 3.35 s (1.9x vs C, 4.4x vs C++, derived from page data). |
| **Workload** | Count occurrences of the 19 words of a hard-coded, pre-split sentence over 1,000,000 passes in a string-keyed hash table, one lookup per word per pass. C: hand-written table of 256 buckets indexed by the key's first character, strcmp along each chain, malloc per new counter. C++: std::unordered_map&lt;string,int&gt; over a vector&lt;string&gt; with a custom hash returning s[0], cnt[\*it] += 1. Lua: a plain table, `if map[text[i]] then map[text[i]] = map[text[i]] + 1`. |
| **Metric** | throughput |
| **Compiler and flags** | gcc -O3 test.c; g++ -O3 -std=gnu++0x test.cpp; luajit test.lua with default options; no gcc, g++ or LuaJIT versions are given for the 2012 transcript or the 2020 rerun. The gcc 8.3.0, Node v15.12.0 and LuaJIT 2.0.5 named in mbossX's 2021 comment belong to that commenter's own separate 100M-iteration array-based programs (C 0.001 s, LuaJIT 1.774 s), not to the author's numbers. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 72 gist stars, 6 forks (2026-10-11); widely cited in LuaJIT vs C discussions |
| **Last commit** | 2015-08-18 |
| **Links** | [repository](https://gist.github.com/spion/3049314) · [benchmark](https://gist.github.com/spion/3049314) |

## Verdict

One `time` run each in 2012 on an unnamed Linux machine, with unstated gcc, g++ and LuaJIT versions: 19M increments into a 17-key string table took 0.161 s in LuaJIT, 0.234 s in C (gcc -O3, first-letter chained table) and 0.321 s in C++ (g++ -O3 -std=gnu++0x, libstdc++ std::unordered_map with an s[0] hash). That is 1.45x and 1.99x (derived from page data). The author's 2020 rerun (no versions or hardware) gave 0.08 s vs 0.173 s and 0.36 s, and at 10x the iterations 0.76 s vs 1.44 s and 3.35 s, so process startup does not explain the gap.

## Use it when

- As a teaching example of why string interning and cached hashes matter for small, fixed string-keyed tables.
- As evidence that std::unordered_map&lt;std::string,int&gt; with a weak first-character hash is a poor fit for a tiny hot dictionary; jh3141's fork shows pointer keys plus a small linear table beat LuaJIT (90 ms vs 95 ms).
- In Lua code that counts tokens from a small vocabulary of strings that already exist, where a plain LuaJIT table needs no tuning.
- As a starting point for a discussion of micro-benchmark pitfalls, which is how the author now frames it.

## Skip it when

- As evidence that LuaJIT beats C or C++ at hash tables in general. The author says real text, larger dictionaries and un-split words (each new word must be allocated and interned) would change the result.
- As a template for a C or C++ word counter. Both baselines are weak: a first-letter hash with strcmp in C, and std::string keys in a node-based std::unordered_map in C++.
- For large dictionaries in LuaJIT. joeatbayes (2015) reports long pauses above 1 GB and the 2 GB heap limit on a Wikipedia-scale word count, which forced FFI or C hash tables.
- As copyable code: the gist has no licence.

## How it is fast

LuaJIT interns every string, so equal words are the same object with a hash computed once at creation. A table lookup is a masked hash on that cached value plus a pointer compare, and the trace compiler inlines it into the loop. The C baseline instead calls strcmp on heap copies for every chain probe, and the C++ baseline compares std::string contents after libstdc++'s modulo-by-prime bucket step and node walk. That LuaJIT also folds the three map[text[i]] accesses per iteration into one lookup is an inference from its alias analysis; nobody published a -jdump. So the gap measures interned versus content-compared string keys more than JIT versus AOT compilation.

## Compared with alternatives

Use this gist only as the historic, minimal three-file illustration of interned string keys. For a string-keyed hash-table comparison with named toolchains, the LuaJIT 2.1 k-nucleotide entry in kostya/jit-benchmarks (g++ 12.2.0 -O3, std::unordered_map&lt;std::string,int&gt;) and the LangArena Etc::Words entries (g++ 16 and clang++ 22 in 16 configurations) are better evidence.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | LuaJIT (test.lua calls table.getn, a Lua 5.1 function); gcc and g++ with libstdc++ for the baselines; node for test.js |
| **Minimum toolchain** | g++ with -std=gnu++0x (C++11 initializer lists); test.c needs a compiler that accepts C89 implicit int (see gotchas). gcc, g++ and LuaJIT versions not documented. |
| **Platforms** | Any platform with gcc and LuaJIT; the original runs were on Linux, hardware not documented |
| **Thread safety** | Not applicable: single-threaded benchmark programs |
| **Drop-in for the baseline** | no |

## Gotchas

- Unverified optimisation claim. test.lua's 2013 comment says 'luajit probably optimizes away all dictionary lookups', and the author's 2020 comment says 'only luajit is doing super-clever (unrealistic) optimizations'. Neither was checked with -jdump. The about 4 ns (2020) to 8.5 ns (2012) per word that LuaJIT takes is consistent with one real interned-key lookup per word (inference), not with the work being removed.
- The baselines collide by design. Four first-letter pairs share a C bucket (at/a, lazy/lake, over/of, near/new) and pay a full strcmp per probe on strdup'd copies. The C++ hash s[0] puts the same pairs in one libstdc++ bucket chain. The C malloc per counter runs only 17 times, not per increment, so Zack24's complaint about allocation in the loop does not explain the gap.
- Several comment-thread numbers do not measure the same work. ayosec's Rust 0.104 s loop runs range(0u32, 100000), 100,000 passes, against C's 1,000,000-pass 0.179 s, so it did a tenth of the work. Zack24's (0.003 s) and mbossX's (C 0.001 s, LuaJIT 1.774 s) C programs index an array and do no hashing. marcomagdy's pointer-keyed std::unordered_map was still 0.495 s against LuaJIT 0.186 s on craigbarnes' machine, so most of the C++ cost is the container, not string comparison.
- test.c declares fht_put without a return type (C89 implicit int) and never returns a value. GCC 14+ and Clang 16+ reject implicit int by default in C99 and later modes, so rebuilding needs -std=gnu89 or -fpermissive. The bucket index is a plain char, which would go negative and index out of bounds for non-ASCII first bytes where char is signed.

## Known shortcomings

- The author calls the benchmark misleading: the C/C++ versions hash by the first letter only while Lua interns strings with a cached hash, and the author's own note says LuaJIT probably optimises away the dictionary lookups; one time run each with no CPU or versions; the jh3141 fork reaching 90 ms replaced the hash table with a vector. No licence (reference). Last revision 2015-08-18, 72 stars.
- The gap comes from LuaJIT's interned, pre-hashed string keys against C strcmp chains and libstdc++ std::unordered_map overhead, not from JIT versus AOT; the 10x rerun (0.76 vs 1.44 s) rules out start-up cost, and nobody checked the 'optimizes away lookups' claim with -jdump (about 4-8.5 ns per word fits real lookups). In the comment thread ayosec's Rust 0.104 s ran 100,000 passes against C's 1,000,000 (10x less work), and marcomagdy's pointer-keyed unordered_map still took 0.495 s against LuaJIT's 0.186 s. test.c uses implicit int, so it fails to build on GCC 14+ and Clang 16+ by default. No licence.

## Caveats and trade-offs

The author's a-warning.md (added 2015-08-18) says the benchmark 'has been misleading for a while': hard-coded text, small dictionary, pre-split words, no allocation cost. The author's own 2013 comment in test.lua says 'luajit probably optimizes away all dictionary lookups', which he did not verify. The C and C++ baselines use a first-character hash, so words sharing an initial letter collide and pay full string compares, while Lua strings are interned with a cached hash and compared by pointer; the author notes the default std::hash made C++ 2x slower. Timings are single `time` runs including process startup, with no CPU model and no compiler or LuaJIT versions. Comments show the C++ side can be beaten back: jh3141's fork (2014-12-06, g++ and clang++ -O3) reached 90 ms vs LuaJIT 95 ms and 71 ms with clang++, but it replaced the hash table with a vector of pairs plus a cached next-item pointer and interned pointers, a benchmark-specific structure that does not settle the hash-table comparison either; later array-based C versions (Zack24 2017, mbossX 2021) do no hashing. Source files last changed 2012-07-14 (test.c) and 2013-10-16 (test.lua comment only). No license. [retier] The author's a-warning.md (2015-08-18) calls the benchmark misleading: hard-coded text, small dictionary, pre-split words, no allocation cost. The gap comes from LuaJIT's interned, pre-hashed string keys against the C version's first-character hash with strcmp chains and libstdc++ std::unordered_map overhead, not from JIT versus AOT; the 10x rerun (0.76 vs 1.44 s) rules out start-up cost, and the 'optimizes away all dictionary lookups' remark was never checked with -jdump (about 4-8.5 ns per word fits one real interned-key lookup). In the thread, ayosec's Rust 0.104 s ran 100,000 passes against C's 1,000,000 (10x less work) and marcomagdy's pointer-keyed unordered_map still took 0.495 s against LuaJIT's 0.186 s. test.c uses implicit int, so it fails to build on GCC 14+ and Clang 16+ by default. No licence; single `time` runs.

Toy workload with a tiny hard-coded dictionary and pre-split words.

## Maintenance

Abandoned gist (code from 2012, a comment edit in 2013, a warning file added 2015-08-18) with no licence, so it is a reference only; the author himself labels it misleading.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The gist publishes test.c, test.cpp and test.lua plus the compile commands (gcc -O3, g++ -O3 -std=gnu++0x) and a 'benchmark' transcript with C 0.234 s, C++ 0.321 s, LuaJIT 0.161 s, but no CPU model, no compiler or LuaJIT versions, and one `time` run per program; the 2020 rerun is a comment with no versions or hardware. First-party numbers with partial methodology, so C, not A.
- **Verifier notes:** Numbers on the gist match the record (original transcript and the author's 2020 comment); tier C stands as first-party with public code and flags but no CPU or versions. Fixed a misattribution: the gcc 8.3.0 / LuaJIT 2.0.5 versions come from a commenter's separate array-based test, not the author's runs. Shortcomings to record: author-declared misleading benchmark, weak first-letter hash on the C/C++ side versus Lua's interned pre-hashed strings, single-run whole-process timings with no hardware, author's own unverified note that LuaJIT may optimise away the lookups; baseline_stdlib libstdc++ inferred from the g++ toolchain of 2012. Not a reject: the measured work is real on all three sides as far as the source shows.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `baseline_stdlib`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-27 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://gist.github.com/spion/3049314>
  - <https://gist.github.com/spion/3049314/revisions>
  - <https://gist.github.com/spion/3049314/forks>
  - <https://gist.github.com/jh3141/768a9672dba9a8fc2524>
- **Sources the enricher read:**
  - <https://gist.github.com/spion/3049314>
  - <https://gist.github.com/spion/3049314/revisions>
  - <https://gist.github.com/jh3141/768a9672dba9a8fc2524>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://gist.github.com/spion/3049314`) · [data/wave14/enrich/raw/gist_github_com_spion_3049314.json](../../../data/wave14/enrich/raw/gist_github_com_spion_3049314.json) (enrichment confidence 0.75)

</details>
