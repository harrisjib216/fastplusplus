# strager/perfect-hash-tables

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `CC-BY-NC-ND-4.0` · 🔴 abandoned

> Research generator of CRC32-hashed perfect hash tables for 80 JS/TS keywords; beats gperf \~1.2-1.4x except on keyword-only input.

| | |
|---|---|
| **Beats** | gperf |
| **Claimed result** | notes.txt (author's dev log, approximate '\~' figures): on the nonkeywords corpus, pht with the icrc32 hasher and --string-compare=check1memcmp (\~69 us) beats gperf default (\~95 us) [\~1.38x, derived from page data]. On the mixed corpus, the same pht config (\~152 us) beats gperf default (\~188 us) [\~1.24x, derived from page data], and beats gperf's best mixed config, --inline-strings (\~184 us) [\~1.21x, derived from page data]. With --string-compare=memcmp, gperf beats every one of the author's hash variants on all three corpora. The keywords-only corpus has no numbers: gperf beats all memcmp variants, and icrc32 with check1memcmp is only 'competitive' with gperf, so pht does NOT win that workload. frozen::unordered_map with lehmer128 is \~85 us (nonkeywords) and \~209 us (mixed), slower than the icrc32/check1memcmp pht in both [derived from page data]. |
| **Workload** | Google Benchmark loop (benchmark.cpp) looks up every identifier token in three corpora. map-to-tokens.cpp builds the corpora from jquery-3.5.1.js: keywords-only, non-keywords-only, and mixed, whitespace-padded to \~287 KB each. Lookups run against the JavaScript keyword set (token.gperf). Each implementation is compiled as a shared library and loaded with dlopen: dozens of generated pht variants, gperf 3.1 option combos, mygperf, bsearch and linear scans, frozen::unordered_map, std::unordered_map, and Rust phf and std::collections::HashMap. |
| **Metric** | throughput |
| **Hardware** | notes.txt says 'my 5950X' (AMD Ryzen 9 5950X) only for the perf-stat branch-miss section. The microsecond figures carry no CPU statement. The icrc32 pht configs are only built on Linux x86 (Intel CRC32 intrinsic, Linux-only block in the Makefile). This is consistent with the 5950X, but the file does not say so. |
| **Compiler and flags** | Makefile: on Linux, CXX=g++-12, and every implementation is also built with \~/Toolchains/clang-stage2/bin/clang++ (-clang.so variants). Flags are -std=c++20 -g -O3 -fvisibility=hidden -fPIC, plus -fcf-protection=full -msse4 -maes on Linux only; the benchmark binary adds -fno-lto. On macOS (aarch64), the Makefile does not set CXX (make default) and uses Homebrew google-benchmark 1.7.1. The baseline is gperf 3.1 (per the generated/gperf_.cpp header). notes.txt does not say which compiler build produced the quoted figures. |
| **Adoption** | 226 stars |
| **Last commit** | 2023-03-12 |
| **Links** | [repository](https://github.com/strager/perfect-hash-tables) · [benchmark](https://github.com/strager/perfect-hash-tables/blob/master/notes.txt) |

## Verdict

The author's dev log (notes.txt: rounded '\~' figures, no raw output) gives time per benchmark iteration, where one iteration looks up every identifier in a \~287 KB corpus built from jquery-3.5.1.js. pht icrc32 + check1memcmp took \~69 us vs \~95 us for stock gperf 3.1 on non-keywords (\~1.38x) and \~152 us vs \~188 us on mixed (\~1.24x; \~1.21x vs gperf with inline strings), and only tied gperf on keywords-only. Builds are -O3 -std=c++20 with g++-12 or a local clang on Linux x86-64; notes.txt names no CPU or compiler for these figures, and the Ryzen 9 5950X appears only in its perf-stat section.

## Use it when

- You write a lexer and want to know how to beat gperf on a small fixed keyword set (here 80 keys of 2-11 bytes); read generate-pht.cpp and the committed generated/ outputs as a worked design study.
- Your lookups are mostly misses (identifiers that are not keywords). The length bounds check plus the first-character check rejected them fastest: \~69 us vs \~95 us for stock gperf on the non-keyword corpus.
- You target x86-64 with SSE4.2. The winning hasher is the CRC32 instruction, and the Makefile builds the icrc32 variants only on Linux x86-64.
- You want a ready harness that compares gperf options, frozen::unordered_map, std::unordered_map, binary/linear search and Rust phf on one key set, using Google Benchmark and perf stat.

## Skip it when

- Anything you ship or modify. LICENSE is CC-BY-NC-ND-4.0 and README says 'EDUCATIONAL USE ONLY', so commercial use and derivatives are not allowed.
- Keyword-heavy input. On the keywords-only corpus gperf was only 'competitive' with the best pht variant, so expect no win there.
- A plain memcmp compare. Every pht hasher with --string-compare=memcmp lost to gperf on all three corpora; the gain comes from the check1memcmp compare.
- Key sets that change at runtime or come from a file. Keys are compiled in from token.h, there is no insertion, and the generator exits with 'character selection is not unique' if the chosen characters do not tell the keys apart.
- Non-x86-64 or big-endian targets for the winning config. icrc32 needs the SSE4.2 CRC32 intrinsic, and pht.h has a FIXME noting that its 2-byte memcpy character load is endian-dependent.

## How it is fast

Stock gperf hashes with len + asso_values[s[0]] + asso_values[s[1]] + asso_values[s[len-1]]. The winning pht variant instead packs four selected bytes (first two and last two) into one 32-bit word and hashes it with a single SSE4.2 CRC32 instruction (_mm_crc32_u32). The generator brute-forces the seed and table size until all 80 keys land in distinct slots (a perfect hash: one probe, no collision chain); the --table-size=small search settled on 262 slots. A lookup rejects lengths outside 2..11, compares the first character, memcmps the rest, and checks the length by reading the NUL at entry_keyword[size], with keywords stored inline in 13-byte entries instead of gperf's default const char\* pointers. Other variants try SIMD compares (SSE2 movemask, PTEST, PCMPESTRM, NEON), cmov-based branchless result selection, and AES, Lehmer-128, xxHash3, FNV-1a and Pearson hashers.

## Compared with alternatives

Pick this repo to learn why a gperf-class keyword table is fast or slow: it ablates hasher, character selection, table size and compare strategy against gperf 3.1 options and frozen::unordered_map on one workload. For code you can ship, use triehash (also benchmarked against gperf) or frozen (a constexpr C++ container API), after you check their licenses, because this repo forbids derivatives.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Generated lookups: pht.h, fnv.h, token.h, and the xxHash header (pht.h includes &lt;xxhash.h&gt; unconditionally). Full harness: Google Benchmark, gperf 3.1, frozen, Python 3, and Rust/cargo (phf crate). The Makefile hard-codes local paths such as \~/tmp/Projects/xxhash, \~/tmp/Projects/frozen/include and \~/Toolchains/clang-stage2. |
| **Minimum toolchain** | C++20 plus GNU extensions (__uint128_t, [[gnu::always_inline]], GNU inline asm for the --cmov variants). The author built with g++-12 and a local clang build on Linux and with make's default compiler on macOS; MSVC is not addressed. |
| **Platforms** | Linux x86-64 with SSE4.2 and AES-NI (-msse4 -maes) for the icrc32, aes and SIMD-compare variants; macOS aarch64 for the lehmer128, fnv1a32, pearson8 and NEON variants. Little-endian assumed. The generator needs getopt_long_only and the harness needs dlopen. |
| **Thread safety** | not documented; each generated look_up_identifier reads only constexpr tables and keeps no mutable state |
| **Drop-in for the baseline** | no |

## Gotchas

- The SIMD compare variants (sse2, ptest, cmpestri, neon-mask-test) load 16 bytes, and chunk84 loads 12 bytes, from the input pointer whatever the key length. The harness pads every buffer by 32 bytes (padding_bytes in token.h). The check1memcmp winner reads only `size` input bytes.
- --no-early-bounds-check read past the end of the table through entry_keyword[size] (issue #1). It is safe only together with --keyword-size-in-entry, which is how the Makefile pairs them.
- The 'gperf --inline-strings' baseline is not a stock gperf 3.1 option. The Makefile strips the flag and defines GPERF_INLINE, which changes token.gperf's struct to inline char arrays. mygperf is a Python post-processor of gperf's tables with the author's compare code.
- Source files carry GPL-3.0-or-later 'part of quick-lint-js' headers, while README and LICENSE say CC-BY-NC-ND-4.0, and issue #3 about licensing is still open. Treat the code as read-only reference.

## Caveats and trade-offs

Tier C, not A. notes.txt is a free-text dev log with rounded '\~' microsecond figures; the repo has no committed results file or raw Google Benchmark output. The CPU (5950X) is stated only for the perf-stat section, and the notes never say whether the g++-12 or the clang (-clang.so) build produced the quoted figures. The win depends on the workload. pht icrc32+check1memcmp beats gperf 3.1 default on the nonkeywords (\~1.38x) and mixed (\~1.24x) corpora. On keywords-only it only ties gperf ('competitive'). Every pht variant with --string-compare=memcmp loses to gperf on all three corpora. --string-compare is an option of the author's generators (generate-pht.cpp, generate-mygperf.py), not of gperf. The harness also builds std::unordered_map, frozen::unordered_map, Rust phf and Rust std HashMap variants, but notes.txt publishes no std::unordered_map or Rust numbers. The corpora are synthetic: map-to-tokens.cpp filters identifiers from jquery-3.5.1.js. LICENSE is CC-BY-NC-ND-4.0: GitHub reports NOASSERTION, and the LICENSE text confirms it. README says 'EDUCATIONAL USE ONLY', so usability is 'reference': no copying and no patent grant. There are no commits since 2023-03-12 (more than 3 years); the repo is not archived. The companion talk (https://www.youtube.com/watch?v=DMQ_HcNSOAI, 'Faster than Rust and C++: the PERFECT hash table', title confirmed via YouTube oEmbed) could not be read, so any speedup figures stated in the talk are not reflected here. The record also says the technique was reimplemented in private:developer-source (fastcpp::phf). The verifier did not check that repo, and it is not evidence for this repo's numbers.

Perfect-hash tables require the full keyword/key set to be known at build time (code-generation step via generate-pht.cpp / generate-mygperf.py / gperf itself), so they are not usable as a general-purpose associative container; no insertion/deletion at runtime; many generated variants trade code size and branch-predictability for speed (e.g. AES-hasher variants generate much larger .cpp files than FNV/lehmer128 ones); results are highly sensitive to table-size, hasher choice (icrc32/fnv1a32/lehmer128/pearson8/aes/xx364), string-compare strategy (memcmp/check1memcmp/chunk84/cmpestri/sse2/ptest), and CPU features (msse4/maes/cmov), meaning the 'winning' configuration is workload- and hardware-specific rather than a single drop-in replacement.

## Maintenance

Abandoned since 2023-03-12 (not archived, 2 open issues) and licensed CC-BY-NC-ND-4.0 'EDUCATIONAL USE ONLY', so read it rather than vendor it; the author's maintained GPL-3.0 descendant of the technique is quick-lint-js's tools/generate-lex-keyword.cpp, which hashes the first two and last two characters with a multiply-shift into a power-of-two table.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** notes.txt has only approximate '\~NN us' dev-log figures and no raw benchmark output. The benchmark code (benchmark.cpp) and the Makefile compilers and flags are public, but the 5950X is named only for the earlier perf-stat section, and the notes never say which CPU or which build (g++-12 or clang-stage2 .so) produced the microsecond figures, so this is first-party evidence short of A.
- **Verifier notes:** The notes.txt numbers match the record, but the original claimed_speedup misread the keywords line: '--string-compare=check1memcmp' is an option of the pht/mygperf generators, not of gperf. claimed_speedup is corrected. The metadata checks out: 226 stars, last commit 2023-03-12, CC-BY-NC-ND-4.0, not a fork, not archived. compared_against_cpp_std_directly stays true because the harness includes std-unordered-map.cpp, but no std::unordered_map numbers are published.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/strager/perfect-hash-tables>
  - <https://github.com/strager/perfect-hash-tables/blob/master/notes.txt>
  - <https://github.com/strager/perfect-hash-tables/blob/master/README.md>
  - <https://github.com/strager/perfect-hash-tables/blob/master/LICENSE>
  - <https://github.com/strager/perfect-hash-tables/blob/master/benchmark.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/benchmark-lite.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/Makefile>
  - <https://github.com/strager/perfect-hash-tables/blob/master/implementations.h>
  - <https://github.com/strager/perfect-hash-tables/blob/master/map-to-tokens.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generate-pht.cpp>
  - <https://github.com/strager/perfect-hash-tables/tree/master/generated>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generated/gperf_.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generated/implementations.inc>
  - <https://www.youtube.com/watch?v=DMQ_HcNSOAI>
  - <https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=DMQ_HcNSOAI&format=json>
- **Sources the enricher read:**
  - <https://github.com/strager/perfect-hash-tables>
  - <https://github.com/strager/perfect-hash-tables/blob/master/README.md>
  - <https://github.com/strager/perfect-hash-tables/blob/master/notes.txt>
  - <https://github.com/strager/perfect-hash-tables/blob/master/LICENSE>
  - <https://github.com/strager/perfect-hash-tables/blob/master/Makefile>
  - <https://github.com/strager/perfect-hash-tables/blob/master/pht.h>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generate-pht.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generate-mygperf.py>
  - <https://github.com/strager/perfect-hash-tables/blob/master/token.h>
  - <https://github.com/strager/perfect-hash-tables/blob/master/token.gperf>
  - <https://github.com/strager/perfect-hash-tables/blob/master/benchmark.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/implementations.h>
  - <https://github.com/strager/perfect-hash-tables/blob/master/file.h>
  - <https://github.com/strager/perfect-hash-tables/blob/master/lex.h>
  - <https://github.com/strager/perfect-hash-tables/blob/master/map-to-tokens.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/test.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/frozen-unordered-map.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/frozen-unordered-map-lehmer128-firsttwolasttwo.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/std-unordered-map.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/std-unordered-map-lehmer128-firsttwolasttwo.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/rs-phf/src/lib.rs>
  - <https://github.com/strager/perfect-hash-tables/tree/master/generated>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generated/pht--table-size-small_--characters-15_--hasher-icrc32_--string-compare-check1memcmp.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generated/gperf_.cpp>
  - <https://github.com/strager/perfect-hash-tables/blob/master/generated/mygperf--string-compare-check1memcmp.cpp>
  - <https://github.com/strager/perfect-hash-tables/issues/1>
  - <https://github.com/strager/perfect-hash-tables/issues/2>
  - <https://github.com/strager/perfect-hash-tables/issues/3>
  - <https://github.com/strager/perfect-hash-tables/commits/master>
  - <https://www.youtube.com/watch?v=DMQ_HcNSOAI>
  - <https://github.com/quick-lint/quick-lint-js>
  - <https://github.com/quick-lint/quick-lint-js/blob/master/tools/generate-lex-keyword.cpp>
  - <https://github.com/quick-lint/quick-lint-js/blob/master/src/quick-lint-js/fe/keyword-lexer.h>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/strager/perfect-hash-tables`) · [data/wave1-phf/enrich/raw/github_com_strager_perfect_hash_tables.json](../../../data/wave1-phf/enrich/raw/github_com_strager_perfect_hash_tables.json) (enrichment confidence 0.8)

</details>
