# C2 (cache-conscious succinct tries)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Research re-implementations of FST, CoCo-trie and MARISA succinct tries; C2-FST and C2-MARISA beat the originals on lookup and size.

| | |
|---|---|
| **Beats** | MARISA (marisa-trie), FST (SuRF), CoCo-trie |
| **Claimed result** | Authors' README (arXiv 2606.16104): C2-FST up to 1.92x faster and up to 41% smaller; C2-CoCo up to 1.22x faster and up to 46% smaller (against CoCo'); C2-MARISA up to 1.51x faster and up to 46% smaller. Independent rerun at 1M keys on 12 corpora (string-index-benchmarks artifact, derived from page data, rho=0 vs rho=0 lookup latency): C2-MARISA 1.21x to 1.48x faster than MARISA on all 12; C2-FST 1.05x to 1.82x faster than FST on 11 and 0.87x (slower) on opaque; C2-CoCo against the original CoCo-trie is slower on 7 of 8 corpora where both ran (0.78x to 0.92x) and faster only on urls (1.49x). Size: C2-MARISA up to 43% smaller than MARISA (dna) but 13% larger on words; C2-FST up to 36% smaller than FST, 2.5% larger on domains. |
| **Workload** | Lookup latency and size of succinct tries (FST, CoCo-trie, MARISA families) over 6 key-set datasets; case IDs and scripts in run_benchmarks.sh. |
| **Metric** | latency |
| **Hardware** | Authors: single Intel Xeon Gold core with 25 MB LLC (exact model not stated). Independent rerun: AMD Ryzen 7 5800HS (8 cores / 16 threads, 16 MiB L3), Fedora 44, 2026-09-26 |
| **Compiler and flags** | C++20, CMake Release: -O3 -march=native -Wall -pedantic (CMakeLists.txt); independent rerun with GCC 16.2.1 |
| **Adoption** | 0 stars, 1 commit on this repo |
| **Last commit** | 2026-06-20 |
| **Links** | [repository](https://github.com/gt-alg-kit/C2) · [benchmark](https://github.com/ilgrad/string-index-benchmarks) |

## Verdict

Authors (README and arXiv 2606.16104, a single Intel Xeon Gold core with 25 MB LLC, model not stated) report up to 1.92x faster and 41% smaller for C2-FST against SuRF's FST, and up to 1.51x and 46% for C2-MARISA. The independent ilgrad/string-index-benchmarks rerun (GCC 16.2.1, -O3 -march=native, AMD Ryzen 7 5800HS, 1M keys, rho=0, timed with C2's own benchmark.cpp driver over positive lookups) has C2-MARISA 1.21-1.48x faster than MARISA on all 12 corpora and C2-FST 1.05-1.82x faster than FST on 11 of 12; that harness's author also maintains the competing lexindex.

## Use it when

- Static, build-once in-memory dictionaries of up to a few million strings (URLs, words, titles, domains) where both size and exact-lookup latency matter and MARISA or SuRF's FST is the incumbent.
- C2-MARISA when you want a smaller-than-MARISA trie that is also faster: the independent 1M-key rerun has it 1.21-1.48x faster than MARISA on all 12 corpora.
- C2-FST when you need ordered operations (successor, prefix test, range scan) on a compact trie and can test them on your own data first.
- x86-64 Linux builds with GCC 10+ or Clang 12+, C++20 and Boost, where pulling in sdsl-lite, ds2i, sux and FSST as submodules is acceptable.

## Skip it when

- As a CoCo-trie replacement: in the independent rerun C2-CoCo was slower than upstream CoCo-trie on 7 of 8 corpora (0.78-0.92x) and larger on dna (10.25 vs 6.14 B/key); the README's 1.22x is against CoCo', the authors' own build with the original CoCo bitvector.
- Persistent or memory-mapped dictionaries: the trie classes have no save/load or mmap path, so the structure must be rebuilt from the keys at every start.
- Numeric-string corpora or very large key sets: the C2 variants produced no result on the numeric corpus in the rerun, and ids, ranks and positions are 32-bit (uint32_t) throughout.
- Production code that needs maintenance: one public commit (2026-06-20), 0 stars, forked from HardyZ1906/C2, no issues, tests or releases.
- Keys containing the 0x00 byte (it is the trie terminator label, c2::terminator_ = 0) or keys longer than 65535 bytes in C2-FST.

## How it is fast

The LOUDS-style topology and label bitvectors use a cache-conscious block layout: each 256-bit block keeps its absolute 32-bit rank, four 8-bit sub-ranks and the 256 bits together (c2::BitVector::Block, louds_cc.hpp), so rank, select and child navigation usually touch one block instead of separate rank/select directories. Adaptive unary-path compression keeps short terminal suffixes inline (at most 4 labels for FST, 3 for MARISA) and moves longer ones to a string pool that is either a recursive nested trie (depth rho 0-2) or an FSST or Re-pair tail container, chosen by size (strpool_t::build_optimal). rho=0 is the latency-optimal setting.

## Compared with alternatives

Choose C2-MARISA or C2-FST over MARISA, and over xcdat or Darts-clone, when you want a succinct trie with ordered or prefix queries that is both smaller and faster than MARISA or SuRF and you can rebuild it in memory at start-up; xcdat (2.2-2.9x faster than marisa on its Wiki set) and Darts-clone are the older, more widely used options, and lexindex was the smallest structure on all 13 corpora in the same campaign.

## Integration

| | |
|---|---|
| **Form** | header-only templates, but they include and link compiled third-party code (sdsl-lite, ds2i succinct, FSST static library); in practice a source-drop of include/ plus lib/ |
| **Dependencies** | Boost (&gt;= 1.71), sdsl-lite (vgteam fork), ds2i (aboffa fork), sux, FSST, and MARISA's grimoire vector header; all but Boost are git submodules included by relative paths like ../lib/ds2i/ |
| **Minimum toolchain** | C++20, CMake 3.13+, GCC 10+ or Clang 12+ (README) |
| **Platforms** | x86-64 Linux tested; built with -march=native; GCC builtins (popcount, ctz, clz) are portable but other platforms are not documented |
| **Thread safety** | not documented; lookups are const member functions on an immutable built structure, so concurrent reads look safe, but build is single-threaded and not reentrant |
| **Drop-in for the baseline** | no |

## Gotchas

- C2-FST lookup stores the key length in a uint16_t (fst_cc.hpp: uint16_t len = key.size()), so keys of 65536 bytes or more are silently truncated and can match the wrong entry; MarisaCC uses uint32_t.
- FstCC::successor returns the leaf id as soon as the query reaches a linked (pool-compressed) leaf, with the comment 'link: treat as exact match', without comparing the stored suffix; a query that diverges inside a compressed suffix can get a wrong successor. Seen in code, not tested here; the paper's headline numbers are exact lookups only.
- FstCC, MarisaCC and CoCoCC own the suffix pool through a raw next_ pointer deleted in the destructor but keep implicit copy constructors, so copying a trie double-frees; calling build twice leaks the old pool, and BitVector grows with an unchecked realloc. Release builds compile asserts out, so an empty key set (assert(!key_set.empty())) is undefined behaviour.
- benchmark.cpp prints [PASSED] unconditionally: lookup results are checked only when __CORRECTNESS_TEST__ is defined, which the CMake build does not set, and timed queries are shuffled existing keys only (no negative lookups). CMakeLists adds -w globally, so the advertised -Wall -pedantic warnings never show.

## Known shortcomings

- Raised C to A from the independent string-index-benchmarks artifact (pin 92c1b86, GCC 16.2.1, Ryzen 7 5800HS): C2-MARISA 1.21-1.48x vs MARISA and C2-FST 0.87-1.82x vs FST, but C2-CoCo is slower than upstream CoCo on 7 of 8 corpora (derived from page data); the harness author also wrote the competitor lexindex.
- Read in code: FstCC::lookup keeps the key length in uint16_t (keys of 64 KiB or more truncated); FstCC::successor returns the linked leaf without comparing the suffix (possible wrong successor, not tested). Raw owning next_ with an implicit copy constructor (double free on copy); building twice leaks; unchecked realloc; empty key set UB in Release. Terminator byte 0x00 conflicts with NUL in keys. No save/load or mmap; 32-bit ids and ranks. benchmark.cpp prints [PASSED] unconditionally (checks only under __CORRECTNESS_TEST__) and times positive lookups only. CMake adds -w globally. C2-CoCo is slower than upstream CoCo-trie in an independent rerun. Single commit; vendored baselines keep upstream licences.

## Caveats and trade-offs

Authors' numbers come from the arXiv preprint 2606.16104 (blocked here) and README; they are 'up to' maxima and the CoCo comparison is against CoCo' (a C2-CoCo build with the original CoCo bitvector), not the upstream CoCo-trie. In the independent rerun C2-CoCo is slower than upstream CoCo-trie on most corpora and larger on dna (10.25 vs 6.14 B/key); C2 variants produced no result on the numeric corpus. The independent harness is written by the author of lexindex (a competing dictionary), uses C2's own benchmark.cpp driver for the C2 and FST/CoCo/MARISA baseline rows, and lists C2-CoCo rho=1 as the smallest structure on dna at 10M keys. The listed repo is a one-commit public release copy forked from HardyZ1906/C2; alexztc/C2 redirects here. Vendored baselines keep their upstream licenses.

Header-only research re-implementations that need Boost and vendored baselines (sdsl-lite, ds2i, sux, FSST) as submodules; build is involved. Adds adaptive unary-path compression and tail containers (FSST, Re-pair).

## Maintenance

Single-commit MIT-licensed paper artifact from 2026-06-20 with vendored baselines under their own licenses; worth vendoring include/ for an experiment, but expect to add serialization, copy semantics and tests before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the independent ilgrad/string-index-benchmarks harness pins this repo at commit 92c1b86 (the only commit here), builds it with its own CMake Release flags (-O3 -march=native per CMakeLists.txt; harness/build.sh) and publishes per-cell results in results/frontier-1m-2026-09-26-arz-be75a38.json naming GCC 16.2.1 and an AMD Ryzen 7 5800HS; there C2-FST and C2-MARISA beat the FST and MARISA baselines on most corpora. The repo's own README headline (up to 1.92x / 1.51x) is first-party and its CPU model is not stated.
- **Verifier notes:** Repo page confirms MIT, 0 stars, forked from HardyZ1906/C2, single commit 92c1b86 on 2026-06-20 (matches the harness pin). Tier raised to A on the independent string-index-benchmarks artifact; the C2-CoCo speed claim does not hold against upstream CoCo-trie there.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** independent: ilgrad/string-index-benchmarks artifact; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/gt-alg-kit/C2>
  - <https://github.com/gt-alg-kit/C2/commits>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/README.md>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/CMakeLists.txt>
  - <https://github.com/ilgrad/string-index-benchmarks>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/harness/build.sh>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/results/frontier-1m-2026-09-26-arz-be75a38.json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/README.md>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/LICENSE>
  - <https://github.com/gt-alg-kit/C2/tree/main/include>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/fst_cc.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/marisa_cc.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/coco_cc.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/bit_vector.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/louds_cc.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/louds_sparse_cc.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/key_set.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/utils.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/alphabet.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/strpool.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/compressed_string_pool.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/include/coco_optimizer.hpp>
  - <https://raw.githubusercontent.com/gt-alg-kit/C2/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/harness/build.sh>
  - <https://raw.githubusercontent.com/ilgrad/string-index-benchmarks/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/gt-alg-kit/c2`) · [data/wave9/enrich/raw/github_com_gt_alg_kit_c2.json](../../../data/wave9/enrich/raw/github_com_gt_alg_kit_c2.json) (enrichment confidence 0.75)

</details>
