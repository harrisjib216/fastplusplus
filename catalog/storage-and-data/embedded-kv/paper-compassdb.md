# CompassDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> Paper-only RocksDB-derived KV engine that replaces SST indexes with in-memory two-tier perfect hashing; reports 2.5-4x RocksDB YCSB point-op throughput.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | YCSB (16 threads, 200M keys, 100M ops): 2.5x-4x throughput vs RocksDB and 5x-17x vs PebblesDB on point-lookup/insert workloads A, B, C, D, F. Workload A \~3x, C 2.52x, D 5.5x vs RocksDB. 50%-85% lower average/p99 latency vs RocksDB. Slower than both RocksDB and PebblesDB on scan-heavy YCSB-E. Intro: RocksDB's write amplification about 2x CompassDB's (15x in a 100M-key one-level test), read amplification 3x in pure reads, space amplification 1.2x. |
| **Workload** | YCSB A-F with 16 threads after loading 200M keys (20-byte keys, 1KB values) then 100M operations; O_DIRECT, compression disabled, RocksDB/PebblesDB with 32MB LRU block cache, up to 4x128MB memtables; plus Workload C value-size sweep (50B-50KB) and fill/read/mixed microbenchmarks |
| **Metric** | throughput |
| **Hardware** | Dell PowerEdge T440, Intel Xeon Silver 2.40 GHz (exact model not stated), Samsung PM9A3 3.84TB NVMe SSD, 128GB RAM, Ubuntu 20.04 LTS, ext4 (ordered mode) |
| **Links** | [benchmark](<https://arxiv.org/abs/2406.18099 (arXiv v1 preprint, 26 Jun 2024; no journal reference listed)>) |

## Verdict

The DiPeak authors ran YCSB with 16 threads on a Dell T440 (Xeon Silver 2.40 GHz, exact model not given; 128GB RAM; Samsung PM9A3 NVMe; Ubuntu 20.04 ext4). They loaded 200M 20B/1KB records and ran 100M operations with O_DIRECT, compression off, and 4x128MB memtables, against RocksDB 7.9.2 and PebblesDB commit 703bd0 (2019). Bar labels give CompassDB vs RocksDB of 122.7 vs 33.8 KOPS on A (3.6x), 186.3 vs 42.1 on B (4.4x), 137.0 vs 54.2 on C (2.5x), 262.7 vs 74.4 on D (3.5x), 98.4 vs 24.1 on F (4.1x) and 2.08 vs 11.04 on E (5x slower). Compiler and flags are not stated, and nobody else has reproduced the results.

## Use it when

- As a design reference if you maintain a RocksDB fork whose traffic is mostly point Get/Put/update (YCSB A, B, C, D, F shapes) on NVMe, with a dataset much larger than RAM.
- Read-heavy point lookups where RocksDB index and filter blocks miss cache and cost extra I/Os. The design aims for one device read per Get. The paper reports about 3x lower read amplification (about 10 vs about 32 for RocksDB with 20B keys and 128B values) and 8.5x db_bench readrandom throughput at 200M keys.
- Point-read workloads with 1KB-50KB values. The perfect-hash index size depends on key count, not data size, and read-only YCSB-C reports 3.6x RocksDB at 1KB and 7.2x at 50KB (my reading of the Fig. 10b bar labels).
- SSD write-endurance-sensitive loads with random inserts. Delta piece files avoid rewriting unchanged keys, and the paper reports write amplification of 4.34 vs about 10.6-11 for RocksDB and PebblesDB at 500M keys. For read-mostly data, 'one level' mode reports 15x lower write amplification than RocksDB (100M keys, 1KB values).
- If you are evaluating CHD or PTHash as a replacement for an SST index, CPHash's dense/sparse bucketing, parameter reuse, AVX2 fastmod and per-segment parallel build are documented well enough to copy.

## Skip it when

- Whenever you need something to run. There is no public repository, binary, license, API reference or build instructions, and GitHub has only unrelated 'compassdb' projects.
- Range scans and iterators. On YCSB-E, CompassDB gets 2.08 KOPS vs RocksDB's 11.04 (about 5x slower), with average read latency of 8.0ms vs 1.5ms. Data is stored in hash order, so scans go through a sorted key-location array (8 bytes per key, sampled every 64 keys) and one random read per key.
- Memory-constrained hosts or very large key counts with small values. The one-I/O guarantee requires every global and local index to stay in RAM, and memory grows with key count. The paper measured 1.7GB at 50M keys and 2.9GB at 100M keys (about 29-34 bytes per key in total, including memtables), well above its 6.5 bytes-per-key estimate.
- Workloads heavy in deletes or overwrites under a tight space budget. A deleted key keeps a placeholder in the global index until its old piece file is garbage-collected. Each TPH holds up to 16 piece files by default (configurable up to 1024), so stale versions accumulate, and every compaction reads all piece files of the TPH. The paper's local-index sizing assumes 1.7x space amplification.
- Non-x86 targets, or any production decision based on these numbers. Perfect-hash construction uses AVX2 and no other ISA is mentioned. The results are first-party vendor numbers that nobody has reproduced.

## How it is fast

Each TPH (the SSTable replacement) carries a global perfect-hash table that maps a key's 64-bit hash to a 1-byte signature (a Bloom-filter substitute with about 1/255 false positives) plus the ID of the piece file holding the key. Each piece has a local perfect-hash table that maps the key to a block offset, and because both tables stay in RAM (estimated at about 6.5 bytes per key), a Get costs two in-memory lookups and one disk read. Compaction writes only new or changed keys into a new delta piece file and leaves unchanged keys where they are, and 'hash range' mode partitions each level by a 32-bit key hash so every compaction touches a fixed number of TPHs (similar to PebblesDB's guards). The perfect hash is CPHash, a mix of CHD and PTHash (dense and sparse buckets, parameter reuse, load factor 0.9), and its construction uses AVX2 with Lemire's fastmod and is split into 64 parallel segments.

## Compared with alternatives

You can't pick it for deployment, because there is no code. For deployable point-lookup speedups over RocksDB, use SplinterDB (2-2.6x point queries, about 2x lower write amplification, open source), KVell, or F2/FASTER. DobLIX is the closest code-available idea: it also swaps RocksDB's SST index, for a learned one. Read CompassDB only as the catalogued reference for putting perfect hashing plus delta piece files in place of SSTs, when scans do not matter.

## Integration

| | |
|---|---|
| **Form** | none published: a vendor-internal (DiPeak) C++ embedded engine derived from RocksDB and described only in the paper; no source, library or binary |
| **Dependencies** | not documented; the paper says it is built on RocksDB and uses DJB hash and CityHash |
| **Minimum toolchain** | not documented (C++; compiler and flags not stated) |
| **Platforms** | Tested only on x86-64 Linux (Xeon Silver 2.40 GHz, Ubuntu 20.04, ext4, Samsung PM9A3 NVMe); perfect-hash construction uses AVX2; other ISAs and OSes not documented |
| **Thread safety** | not documented; it claims RocksDB API compatibility, and YCSB was driven with 16 client threads |
| **Drop-in for the baseline** | partial — the paper claims compatibility with all RocksDB APIs, but no code exists to verify that; on-disk files are a new .ph piece format, and migrating existing SST data is not discussed |

## Gotchas

- The baseline setup is lopsided. RocksDB 7.9.2 and PebblesDB got a 32MB LRU block cache under O_DIRECT, while CompassDB runs with no block cache but keeps its whole perfect-hash index in RAM (about 1.3GB even at the estimated 6.5 bytes per key for 200M keys). The paper says other RocksDB options stayed at defaults and argues against a '10-bit Bloom filter default'. But RocksDB 7.9.2's BlockBasedTableOptions::filter_policy defaults to nullptr, so whether the YCSB baseline had Bloom filters at all is not stated.
- The numbers disagree with each other. The text claims 5.5x over RocksDB on YCSB-D, but the bar labels read 262.67 vs 74.37 KOPS, which is about 3.5x. The 1KB point in the Workload-C value-size sweep (122.7/33.79/11.86) exactly repeats the Workload-A bars rather than the Workload-C bars (137.01/54.24/24.84). The advantage over RocksDB also does not grow steadily with value size, as the text says: it is 4.2x at 300B, 2.5x at 10KB and 7.2x at 50KB.
- The manuscript reads like a draft. It still carries the ACM template's placeholder running header 'Trovato et al.', it cites a 'Table 5.5-1' that does not exist, and two background paragraphs appear twice. It is arXiv v1 only, and the claimed SIGMOD/PACMMOD publication does not appear in Crossref.
- The benchmark used 'hash range' mode, where TPHs are partitioned by a hash of the key rather than by key order. I infer, though the paper does not say so, that a range scan must visit every TPH on every level. That fits the YCSB-E loss, which the paper leaves as future work.

## Known shortcomings

- The 5-17x is against PebblesDB, not SplinterDB. The claimed SIGMOD/PACMMOD venue could not be found in Crossref, so this is an arXiv-only vendor preprint; no code.
- Loses YCSB-E about 5x (2.08 vs 11.04 KOPS; scans become random reads in hash order). Lopsided baseline: RocksDB 7.9.2 with a 32 MB cache under O_DIRECT and no stated Bloom filter, while CompassDB keeps its whole index in RAM (measured \~29-34 B/key including memtables, vs a 6.5 B/key estimate). Internal mismatches (text 5.5x vs bars \~3.5x on D; duplicated figure bars); deletes leave tombstones until GC; AVX2/x86 only.

## Caveats and trade-offs

No public repository: GitHub search finds only unrelated 'compassdb' projects. The arXiv preprint (v1, June 2024) has no venue or journal reference. The claimed SIGMOD / Proc. ACM Manag. Data 3(6) Article 294 publication could not be verified: there is no CompassDB entry in Crossref's PACMMOD (ISSN 2836-6573) index, even though vol 3 issue 6 is indexed. The authors are all from DiPeak, the vendor, so these are first-party numbers. The secondary baseline is PebblesDB, not SplinterDB; SplinterDB appears only as related work. Setup is not like-for-like: RocksDB/PebblesDB got a 32MB block cache under O_DIRECT, and CompassDB loses on scan-heavy YCSB-E.

Perfect-hash in-memory index (\~6 bytes/KV) instead of RocksDB's default block-based index+bloom filter; claims RocksDB API compatibility for drop-in migration, but no public implementation to verify; perfect-hash structures typically complicate/limit fully dynamic online rebuilds under skewed insert patterns.

## Maintenance

Paper only: arXiv v1 (26 Jun 2024), with no later version and no journal reference. It is absent from Crossref's PACMMOD records (551 since June 2025), so the claimed SIGMOD publication is unverified. OpenAlex lists only the arXiv version, with zero citations. There is no repository or license, DiPeak's homepage (an enterprise LLM data-intelligence vendor) shows no CompassDB material in its static HTML, and maintenance is unknown, so it is usable only as a design reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** Only an arXiv v1 preprint (June 2024, no journal reference) by the vendor's (DiPeak) own engineers, with no public code, no compiler/flags, and an incomplete CPU model ('Intel Xeon Silver 2.40 GHz'). The claimed SIGMOD/PACMMOD 3(6) publication could not be found in Crossref's PACMMOD index, so this is first-party numbers with partial methodology.
- **Verifier notes:** The '5x-17x vs SplinterDB' claim is wrong; the paper says PebblesDB. The peer-review claim is unverified (Crossref PACMMOD has no match; the ACM DL returned 403, DBLP showed a bot wall and Semantic Scholar returned 429), so the tier drops to C. Re-raise to B only if a published SIGMOD/PACMMOD version is located.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2406.18099>
  - <https://arxiv.org/abs/2406.18099>
  - <https://api.crossref.org/works?query.bibliographic=CompassDB&filter=from-pub-date:2025-01-01,issn:2836-6573&rows=5&select=DOI,title,volume,issue,article-number,published>
  - <https://dl.acm.org/toc/pacmmod/2025/3/6>
- **Sources the enricher read:**
  - <https://arxiv.org/pdf/2406.18099>
  - <https://export.arxiv.org/api/query?id_list=2406.18099>
  - <https://api.crossref.org/works?query.bibliographic=CompassDB+perfect+hash+key-value+store>
  - <https://api.crossref.org/works?query.bibliographic=perfect+hash+key-value+store+LSM&filter=issn:2836-6573>
  - <https://api.crossref.org/works?query.bibliographic=two-tier+perfect+hash+table+key-value&filter=from-pub-date:2024-06-01>
  - <https://api.crossref.org/journals/2836-6573/works?filter=from-pub-date:2025-06-01,until-pub-date:2026-09-30&rows=1000>
  - <https://api.openalex.org/works?search=CompassDB>
  - https://api.semanticscholar.org/graph/v1/paper/arXiv:2406.18099 (HTTP 429)
  - <https://hn.algolia.com/api/v1/search?query=CompassDB>
  - <https://github.com/search?q=compassdb&type=repositories>
  - <https://github.com/search?q=CompassDB&type=code>
  - <https://api.github.com/search/users?q=dipeak>
  - <https://api.github.com/users/dipeak-web/repos>
  - <https://www.dipeak.com>
  - <https://github.com/facebook/rocksdb/blob/v7.9.2/include/rocksdb/table.h>
  - <https://github.com/facebook/rocksdb/releases/tag/v7.9.2>
  - <https://github.com/utsaslab/pebblesdb/commit/703bd01bba47c586fc3fd07273452528826cd38e>
  - <https://github.com/brianfrankcooper/YCSB/blob/master/rocksdb/src/main/java/site/ycsb/db/rocksdb/RocksDBClient.java>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:compassdb`) · [data/wave6/enrich/raw/paper_compassdb.json](../../../data/wave6/enrich/raw/paper_compassdb.json) (enrichment confidence 0.7)

</details>
