# ChainedFilter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🔴 abandoned

> SIGMOD'24 research code chaining approximate and exact filters for zero false positives on known negatives; beats RocksDB's Bloom P99.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | SIGMOD 2024 paper: up to 36% lower P99 tail point-query latency than RocksDB's built-in Bloom filter at the same filter space (\|U\|=16M existing-item queries: about 31us for Bloom vs under 20us for ChainedFilter); up to 31% fewer external memory accesses than raw Cuckoo Hashing; 26% extra space over the theoretical lower bound for an implicit static dictionary; 0.22 extra bits/item over the lower bound for lossless compression; up to 99.1% less filter space than the original Learned Bloom Filter |
| **Workload** | RocksDB (all SSTables in L0, default 64MB write buffer, 36-byte random keys and 64-byte values, 4M-16M items) P70/P99 point-query latency with ChainedFilter replacing the built-in Bloom filter, versus Bloom-only filters at 0x/1x/2x space; also external-memory accesses for Cuckoo Hashing, static-dictionary space and Learned Bloom Filter space |
| **Metric** | latency |
| **Hardware** | Intel Core i9-10980XE @ 3.00GHz (the paper says '36 Intel Core i9-10980XE CPU'), 24.8MiB L3, 128GB DRAM |
| **Compiler and flags** | g++ 7.5.0 (Ubuntu 7.5.0-6ubuntu2), -O3; the README says C++17, but the Self-Adaptive Hashing Makefile uses --std=c++11 -O3 -g |
| **Adoption** | 6 stars |
| **Last commit** | 2023-04-27 |
| **Links** | [repository](https://github.com/ChainedFilter/ChainedFilter) · [benchmark](https://arxiv.org/abs/2308.13632) |

## Verdict

The 36% figure comes from the SIGMOD 2024 paper, not from runnable repo code. RocksDB was set up with all SSTables in L0 and a 64MB write buffer, with 36-byte keys, 64-byte values and 16M items (1.6GB, 30 SSTables). P99 latency for existing-key point lookups was about 31us with RocksDB's own Bloom filter at the same filter space and under 20us with ChainedFilter (RocksDB's Bloom filter plus an Othello whitelist), on an Intel i9-10980XE with 128GB DRAM and g++ 7.5.0 -O3. The repo's runnable experiments cover only the static dictionary, Huffman and Cuckoo-hash results, and none of them runs a Bloom baseline.

## Use it when

- Static exact membership or 1-bit retrieval over a closed universe, where every key that will ever be queried is known at build time and false positives are not acceptable (the paper's implicit static dictionary uses about 26% more space than the lower bound).
- LSM-trees with many overlapping sorted runs in one level (tiered compaction, or a large L0) where the P99 latency of existing-key point lookups matters. Treat the paper's design (Bloom stage 1, Othello stage 2 whitelisting keys from later SSTables) as a blueprint to implement yourself; this repo has no code for it.
- Cuckoo hash tables in slow or external memory: Algorithm 2, trained online, predicts which of the two tables holds each key. The paper reports 31% fewer external memory accesses at load 0.4 and zero mispredictions after 7 training rounds.
- Random-access decoding of Huffman-coded data, where the paper reports 0.22 extra bits per item over the lower bound.
- Studying the chain-rule construction before writing your own version on top of a maintained xor, binary-fuse or ribbon filter library.

## Skip it when

- As a general Bloom filter replacement when negatives are unknown. False positives on never-seen keys are only as good as stage 1, and in the paper's RocksDB test, latency for non-existing keys at 16M items still rises depending on which SSTable reports the false positive.
- Workloads with frequent inserts or deletes. Algorithm 1 is static and must be rebuilt, the paper says the chain rule does not hold for general dynamic membership, and the dynamic whitelist it suggests (Othello or Coloring Embedder) costs about 2.2-2.33 bits per item.
- Anything that ships. There is no LICENSE file (all rights reserved), the repo has 3 commits from April 2023, and there are no tests and no build system beyond per-folder Makefiles. The code also has leaks and undefined behavior (see gotchas).
- Keys that are not 32-bit ints, or large sets built on a tight memory budget. The code hashes only int keys, and a build keeps the full positive and negative arrays plus peeling scratch arrays in RAM; the paper notes peeling needs Ω(n log n) extra construction space.
- Range queries: ChainedFilter handles point lookups only.

## How it is fast

The paper's 'chain rule' shows that the space for exact membership factorizes as f(0,λ) = f(ε,λ) + f(0,ελ), so splitting the job into stages costs no extra space. Stage 1 is an approximate Bloomier (xor) filter with ⌊log2 λ⌋-bit fingerprints, built by hypergraph peeling with its 3 hash positions inside a window about 1/120 of the table (as in binary fuse filters), and stage 2 is a 1-bit exact Bloomier (retrieval) table that holds only the positives and stage 1's false positives and is probed only when stage 1 says yes. At λ=16 this gives 64% less space and 103% higher query throughput than a single exact Bloomier filter. The RocksDB gain is not a faster probe: each SSTable's filter (RocksDB's Bloom filter plus an Othello whitelist) is made exact with respect to keys in the later SSTables of the same level, so a lookup of an existing key reads at most one extra SSTable per level instead of up to N.

## Compared with alternatives

Choose ChainedFilter's design over Xor Filter or BuRR only when you know the negative keys at build time and need zero false positives on them, as in an exact static dictionary or the paper's trick of excluding keys that live in later SSTables. For ordinary approximate membership, Xor Filter and BuRR are licensed, usable libraries built on the same peeling/retrieval ideas, and SuRF is the RocksDB choice when you need range queries.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library, plus a bundled public-domain MurmurHash.h) |
| **Minimum toolchain** | C++11 in practice: the Makefiles use g++ --std=c++11 -O3 -g, and the authors report g++ 7.5.0. The README says C++17, but Bloomier.h uses the 'register' keyword, which C++17 removed. |
| **Platforms** | Not documented. The code is plain scalar C++ with no SIMD or intrinsics, and it has only been run on x86-64 Ubuntu (Intel i9-10980XE). |
| **Thread safety** | Not documented. Nothing is locked, and Algorithm 2's insert() and change() allocate new layers lazily, so treat it as single-threaded. |
| **Drop-in for the baseline** | partial — it plays a Bloom filter's role, but build() needs the negative set up front, keys must be int, and the RocksDB drop-in from the paper is not published |

## Gotchas

- build() signals failure with negative return codes (-1 to -6), not exceptions, and retries peeling with only a fixed list of 10 seeds. The 'memory' it returns is a computed bit count (slots × fingerprint length), while the tables are stored as int[] (32 bits per slot), and Algorithm 2 stores bool[] (1 byte per bit), so real RAM use is far above the reported filter space.
- Undefined behavior: Algorithm 2's Layer never initializes its 'upper' pointer (or sum1) before 'upper==NULL' checks. In the Cuckoo experiment, CuckooHash::query_with_pre can fall off the end without returning, and query() reads an uninitialized variable.
- Leaks: \~ChainedFilter calls \~Bloomier() directly instead of delete, each seed retry allocates a new Encoder without freeing the old one, error paths leak their scratch arrays, and the experiment mains call \~ChainedFilter() by hand. The experiment mains also declare multi-GB static arrays (for example, three int[2^27] arrays in the Static Dictionary experiment).
- The headers define non-inline functions (MurmurHash32 is actually MurmurHash2, plus getp) and put 'using namespace std' at global scope, and both Algorithm1.h and Algorithm2.h declare 'class ChainedFilter'. You cannot include both in one translation unit, and including either from two .cpp files breaks the link. The faster interleaved variant, ChainedFilter_fast.h, ships but no main.cpp uses it, and the paper's experiments used 64-bit keys while the repo code hashes 32-bit ints.

## Known shortcomings

- The RocksDB benchmark code isn't in the repo; no licence (reference only); abandoned since 2023-04.
- No LICENSE; three commits in April 2023; reference code only. The RocksDB P99 code (Bloom + Othello) is not in the repo, so the 36% is paper-only. Zero false positives hold only for negatives known at build time; unknown keys still see the Bloom FPR, and Algorithm 1 is static (rebuild on change).
- int32 keys only (the paper used 64-bit); reported bits ignore int[]/bool[] storage, so real RAM is far larger. UB (uninitialised 'upper' in Algorithm 2, a cuckoo function missing a return), leaks, non-inline header functions, duplicate ChainedFilter class; 'register' contradicts the README's C++17 claim and the Makefiles use c++11.

## Caveats and trade-offs

No LICENSE file, so all rights are reserved by default and the code is reference/study-only. The repo says the code is there to help readers understand the paper's algorithms; it is not a packaged library. The headline RocksDB P99 experiment (paper Section 5.4) has no code in the repo, which only covers Algorithms 1-2, the static dictionary, random-access Huffman and self-adaptive Cuckoo hashing. The 36% gain is for existing-key queries at |U|=16M; for non-existing keys at 16M, ChainedFilter latency rises depending on which SSTable reports the false positive. Last commit was 2023-04-27, more than 3 years ago.

A general 'chain rule' framework composing several elementary filters rather than a drop-in single filter; the RocksDB integration is a case study, not a merged patch to upstream RocksDB

## Maintenance

Abandoned after three commits in April 2023, with no license file. Treat it as a reference for reading the paper, not code you can vendor, and note that the RocksDB integration was never published.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C-&gt;B: the numbers come from the peer-reviewed SIGMOD 2024 paper (arXiv:2308.13632), whose Section 5.4.3 swaps RocksDB's built-in Bloom filter for ChainedFilter at equal filter space and reports P99 point-query latency falling from about 31us to under 20us (36% lower). It is not A because the RocksDB integration and benchmark code is not in the repo. The repo has only src/Algorithm1-2, Static Dictionary, Random Access Huffman Coding and Self-Adaptive Hashing, and none of them runs a Bloom baseline, although the CPU (i9-10980XE) and compiler (g++ 7.5.0 -O3) are stated.
- **Verifier notes:** The numbers match the README and the arXiv abstract; the paper was accepted at SIGMOD 2024 (arXiv comment and PDF header). The tier goes up to B because of the peer-reviewed paper, so the verdict is confirm. maintenance_status changes from stale to abandoned, since the last commit was 3.4 years ago.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ChainedFilter/ChainedFilter>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Self-Adaptive%20Hashing/main.cpp>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Self-Adaptive%20Hashing/Makefile>
  - <http://export.arxiv.org/api/query?search_query=all:ChainedFilter&max_results=5>
  - <https://arxiv.org/abs/2308.13632>
  - <https://arxiv.org/pdf/2308.13632>
- **Sources the enricher read:**
  - <https://github.com/ChainedFilter/ChainedFilter>
  - <https://api.github.com/repos/ChainedFilter/ChainedFilter/readme>
  - <https://api.github.com/repos/ChainedFilter/ChainedFilter/git/trees/HEAD?recursive=1>
  - <https://api.github.com/repos/ChainedFilter/ChainedFilter/issues?state=all>
  - <https://api.github.com/repos/ChainedFilter/ChainedFilter/commits>
  - <https://api.github.com/repos/ChainedFilter/ChainedFilter/forks>
  - <https://api.github.com/users/ChainedFilter/repos>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/src/Algorithm1.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/src/Algorithm2.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/src/Bloomier.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/src/MurmurHash.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Static%20Dictionary/main.cpp>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Static%20Dictionary/Makefile>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Static%20Dictionary/include/ChainedFilter.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Random%20Access%20Huffman%20Coding/main.cpp>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Random%20Access%20Huffman%20Coding/Makefile>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Random%20Access%20Huffman%20Coding/include/ChainedFilter.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Random%20Access%20Huffman%20Coding/include/ChainedFilter_fast.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Self-Adaptive%20Hashing/main.cpp>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Self-Adaptive%20Hashing/include/CuckooHash.h>
  - <https://raw.githubusercontent.com/ChainedFilter/ChainedFilter/main/%20Self-Adaptive%20Hashing/include/ChainedFilter.h>
  - <https://arxiv.org/pdf/2308.13632>
  - <http://export.arxiv.org/api/query?id_list=2308.13632>
  - <https://hn.algolia.com/api/v1/search?query=ChainedFilter>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/chainedfilter/chainedfilter`) · [data/wave6/enrich/raw/github_com_chainedfilter_chainedfilter.json](../../../data/wave6/enrich/raw/github_com_chainedfilter_chainedfilter.json) (enrichment confidence 0.72)

</details>
