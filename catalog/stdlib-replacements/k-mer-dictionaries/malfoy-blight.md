# BLight

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [k-mer dictionaries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `AGPL-3.0` · 🟡 stale

> Minimizer-partitioned, MPHF-based exact k-mer dictionary; indexes human k=31 at 22.3 bits/k-mer versus Pufferfish's 55.6.

| | |
|---|---|
| **Beats** | Pufferfish |
| **Claimed result** | Human genome, k=31. Table 1 (construction): BLight 10 min, 7.4 GB peak, 22.3 bits/k-mer vs Pufferfish dense 69 min, 27.4 GB, 55.59 bits/k-mer. BLight ran with 12 threads; its single-thread human build took 60 min. Table 2 (querying all reference k-mers): BLight 1,748 s single-thread vs Pufferfish '1.799' (presumably 1,799 s), and 155 s multi-threaded vs 655 s. The column is labelled 16T, but the text says 12 threads. On real reads (SRR5833294), single-thread BLight takes 1,577 s vs Pufferfish 1,260 s, so BLight is slower there. All figures are verbatim from the paper. |
| **Workload** | Exact associative index over k-mers of the human genome (k=31): build the index and answer membership/identifier queries over the full reference, using an MPHF (BBHash-style) plus minimizer indexing. |
| **Metric** | memory |
| **Hardware** | Intel Xeon E5-2420 @ 1.90 GHz, 192 GB RAM, Ubuntu 16.04 |
| **Compiler and flags** | Not stated in the paper; repo makefile builds with g++ (version unstated) -DNDEBUG -Ofast -flto -march=native -mtune=native -msse4 |
| **Adoption** | 36 stars |
| **Last commit** | 2024-07-06 |
| **Links** | [repository](https://github.com/Malfoy/BLight) · [benchmark](https://academic.oup.com/bioinformatics/article/37/18/2858/6209734) |

## Verdict

The BLight paper (Bioinformatics 37(18):2858) measured human k=31 on a Xeon E5-2420 at 1.9 GHz with 192 GB RAM under Ubuntu 16.04, with compiler and flags unstated. On 12 threads BLight built in 10 min with 7.4 GB peak and 22.3 bits/k-mer vs Pufferfish dense's 69 min, 27.4 GB and 55.59 bits/k-mer; querying all 2.5 billion reference k-mers took 1,748 s vs 1,799 s single-threaded and 155 s vs 655 s multi-threaded, and no std:: container, BBHash or other standalone MPHF was benchmarked.

## Use it when

- Static, duplicate-free k-mer set (k &lt;= 32, canonical) from BCALM2 unitigs where RAM is the limit: the paper reports 22.3 bits/k-mer and 7.4 GB peak for the 2.5 billion human k-mers. It also built pine and axolotl (18.3 billion k-mers in 62.4 GB), where Pufferfish could not be built for lack of memory on a 192 GB machine.
- You need a dense k-mer-to-integer ID in [0, N) to index your own side arrays (counts, colors, flags) and you need exact negatives, not the arbitrary value a bare MPHF returns for absent keys.
- Batch-querying whole genomes or read files on a multi-core machine: all human reference k-mers took 155 s vs Pufferfish's 655 s with 12 threads (Table 2 labels the column 16T). The paper's Table 2 footnote says Pufferfish queries cannot benefit from multiple threads.
- Index build time matters and you have about 12 cores: 10 min for human vs 69 min for Pufferfish dense. BLight's single-thread build took 60 min, so the build win needs the threads.

## Skip it when

- Single-threaded querying: 1,748 s vs Pufferfish's 1,799 s on reference k-mers (parity), and 1,577 s vs 1,260 s on real reads (SRR5833294), so BLight is about 25% slower there.
- You want the smallest index or the fastest single-core lookups: in the SSHash paper's benchmark (i9-9940X, gcc 11.2, one core) BLight b=0 used 20.17 bits/k-mer vs 8.28-9.39 for SSHash, and streamed high-hit reads at 440 vs 253 ns/k-mer.
- Query streams that are mostly misses: the same benchmark measured 1,088 ns/k-mer for BLight on a low-hit stream vs 183 for canonical SSHash, and that paper notes BLight's query time degrades when most queries are negative.
- Sets that change, k &gt; 32, or non-DNA keys: the index is static (rebuild to add k-mers), and the kmer type is uint64_t, with a commented-out __uint128_t typedef for k &lt;= 64 that needs a recompile.
- Counting k-mer abundance from raw reads: in the paper's Table 4, BLight took 19:49 (hh:mm) vs 05:12 for SRC and 15:11 for Squeakr, and won only on peak memory (20.8 GB vs 44.2 and 185.4 GB).

## How it is fast

K-mers are partitioned into 4^m buckets by minimizer (m=10 by default), and each run of consecutive k-mers that share a minimizer is stored once as a 2-bit-packed super-k-mer. Each partition gets a BBHash minimal perfect hash function. Per k-mer the index keeps only log2(super-k-mers in its bucket) bits that point to its super-k-mer, finds that super-k-mer's start with a BitMagic rank/select bitvector, and decodes it to check the hit, so answers are exact. The paper's breakdown is about 8-11 bits/k-mer for sequence, 4 for the MPHF, 5-13 for positions and under 1 for rank/select. Streaming queries cache the decoded super-k-mer and test the next query k-mers against it before touching the MPHF, and construction splits the input into 4^s temporary files that OpenMP threads process independently, which is why build and batch queries scale with cores.

## Compared with alternatives

Pick BLight over SSHash or RSHash when build RAM is the tightest limit (the SSHash paper measured 7.5 GB peak to build human with BLight vs 15.4 GB for SSHash) or when you want OpenMP-parallel construction and batch-query helpers in a C++11 codebase that can accept AGPL. Otherwise SSHash (8.28-9.39 vs 20.17 bits/k-mer, 253 vs 440 ns/k-mer streaming in that benchmark) and RSHash, which its entry reports as faster than SSHash, are smaller, faster per core, MIT-licensed and still maintained.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | zlib and OpenMP; BBHash, BitMagic, LZ4, zstr and robin_hood are vendored in include/ and lz4/ |
| **Minimum toolchain** | C++11 (the makefile uses g++ -std=c++11 -fopenmp); minimum GCC version not documented |
| **Platforms** | x86-64 only in practice (SSSE3 _mm_shuffle_epi8 via &lt;tmmintrin.h&gt;; the makefile sets -msse4 -march=native); POSIX/Linux (setrlimit, pthread); macOS and Windows not documented |
| **Thread safety** | Construction and the file_query_\* helpers parallelize internally with OpenMP (core_Number parameter, default 1). The file_query_\* helpers call get_presence_query/get_hashes_query concurrently on one index, but the methods are non-const and no guarantee for user threads is documented. Building two indexes in one process segfaults (issue #10). |
| **Drop-in for the baseline** | no |

## Gotchas

- Input must be 2-line FASTA (one sequence line per record; no multi-line FASTA or FASTQ, per snippet.cpp) with no duplicate k-mers. Construction encodes every character other than uppercase A/C/G as T, while queries map bases with (c/2)%4 (N becomes G), so soft-masked or N-containing input gives wrong answers without any error.
- construct_index needs a working directory that already exists and opens 4^s temporary files (256 by default), so raise ulimit -n. Failures such as a file that cannot be opened call exit() instead of throwing, and the library prints progress and index recaps to stdout.
- Building a second index in the same process segfaults (issue #10, open since 2022-02-17 with no reply).
- get_hashes_query returns MPHF values, not positions, and there is no ID-to-k-mer access call (only a full iterator). An index loaded from disk hard-codes 20 threads for the file_query_\* helpers, and the destructor deletes any files named _out0.._out&lt;4^s-1&gt; in the current directory.

## Known shortcomings

- Benchmarked only against Pufferfish (and Squeakr/SRC, where it builds slower). The construction win needs 12 threads; single-thread queries are at parity on reference k-mers and slower on real reads (1,577 s vs 1,260 s).

## Caveats and trade-offs

BLight is compared only against Pufferfish, a k-mer index, not against std::unordered_map, BBHash or CMPH directly. The construction win compares BLight on 12 threads against Pufferfish. Single-thread queries are at parity on reference k-mers, and BLight is slower than Pufferfish on real reads (1,577 vs 1,260 s). BLight wins only multi-threaded, because Pufferfish queries do not scale with threads. In the abundance-index use case, BLight builds slower than SRC and Squeakr (19:49 vs 05:12 and 15:11) and wins only on memory. The paper states no compiler or flags. The repo was last pushed 2024-07-06 (stale).

AGPL-3.0 is copyleft and network-use-triggering, a stronger restriction than most catalog entries; specialized to k-mer/genomics keys; static index (no updates) as opposed to Bifrost's dynamic index.

## Maintenance

Stale since 2024-07-06 (last commit was a BCALM2 parsing tweak), with 4 open issues including an unanswered segfault report and a libBlight packaging PR open since 2021. The core is about 1,400 lines of blight.cpp plus vendored headers, small enough to vendor, but AGPL-3.0 carries copyleft to programs that link it, including network services.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): reject; tier before verification B, tier now B.
- **Tier reason:** This tier covers only the off-category comparison against Pufferfish. The peer-reviewed paper (Bioinformatics 37(18):2858, Tables 1-2) and the matching bioRxiv v4 preprint name the CPU (Xeon E5-2420) but state no compiler or flags. The repo's bench_blight.cpp times BLight alone, and its makefile uses unversioned g++, so the evidence cannot reach Tier A.
- **Verifier notes:** The claimed numbers match the published Tables 1-2. The OUP page came through WebFetch (curl gets 403) and matches bioRxiv 10.1101/546309v4. The rejection is on category scope only. Repo metadata checked: AGPL-3.0, not a fork, not archived, 36 stars, last commit 2024-07-06 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://academic.oup.com/bioinformatics/article/37/18/2858/6209734>
  - <https://www.biorxiv.org/content/10.1101/546309v4.full.pdf>
  - <https://github.com/Malfoy/BLight>
  - <https://github.com/Malfoy/BLight/blob/master/bench_blight.cpp>
  - <https://github.com/Malfoy/BLight/blob/master/makefile>
  - <https://www.biorxiv.org/content/10.1101/2024.11.26.625346v1.full.pdf>
- **Sources the enricher read:**
  - <https://github.com/Malfoy/BLight>
  - <https://github.com/Malfoy/BLight/blob/master/README.md>
  - <https://github.com/Malfoy/BLight/blob/master/blight.h>
  - <https://github.com/Malfoy/BLight/blob/master/blight.cpp>
  - <https://github.com/Malfoy/BLight/blob/master/utils.h>
  - <https://github.com/Malfoy/BLight/blob/master/utils.cpp>
  - <https://github.com/Malfoy/BLight/blob/master/bench_blight.cpp>
  - <https://github.com/Malfoy/BLight/blob/master/snippet.cpp>
  - <https://github.com/Malfoy/BLight/blob/master/makefile>
  - <https://github.com/Malfoy/BLight/blob/master/include/conf.h>
  - <https://github.com/Malfoy/BLight/blob/master/lz4/lz4_stream.h>
  - <https://github.com/Malfoy/BLight/issues/10>
  - <https://github.com/Malfoy/BLight/issues/8>
  - <https://github.com/Malfoy/BLight/issues/7>
  - <https://github.com/Malfoy/BLight/issues/6>
  - <https://github.com/Malfoy/BLight/pull/9>
  - <https://github.com/Malfoy/BLight/commits/master>
  - <https://academic.oup.com/bioinformatics/article/37/18/2858/6209734>
  - <https://doi.org/10.1093/bioinformatics/btac245>
  - <https://academic.oup.com/bioinformatics/article/38/Supplement_1/i185/6617506>
  - <https://github.com/jermp/sshash>
  - <https://github.com/jonsmcode/rshash>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/malfoy/blight`) · [data/wave1-phf/enrich/raw/github_com_malfoy_blight.json](../../../data/wave1-phf/enrich/raw/github_com_malfoy_blight.json) (enrichment confidence 0.8)

</details>
