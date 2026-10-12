# LUDA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> Paper-only LevelDB 1.22 fork that moves most compaction work to an NVIDIA GPU; about 2x LevelDB/RocksDB YCSB-A throughput, but only under heavy CPU contention.

| | |
|---|---|
| **Beats** | LevelDB |
| **Claimed result** | About 2x the YCSB-A throughput of LevelDB and RocksDB, but only when stress-ng takes 80% of the CPU (20% left). With no CPU contention, RocksDB (4 background threads) has the shortest running time on the 5 GB run; LUDA comes second and LevelDB last. The paper also says LUDA's compaction is '1x faster' than LevelDB's and '2x faster' than RocksDB's. At 1 KB values it processes a similar amount of data as LevelDB in 46% less running time. Without CPU overhead it has the lowest and most stable 99th-percentile latency. The abstract's 'up to 2x higher throughput and 2x data processing speed' is the best case under CPU contention. |
| **Workload** | YCSB-A (0.5/0.5 update-read), 16 B keys, values 128 B-1 KB, 4 MB memtable/SST, 4 KB data blocks. Load 10M pairs (\~5 GB), then run another 10M operations, with stress-ng CPU overhead at 0%, 40% and 80%. A separate one-hour latency/robustness run uses 0.1 billion 256 B-value pairs (\~50 GB). GPU-accelerated compaction vs stock LevelDB 1.22 and RocksDB 6.4.6. |
| **Metric** | throughput |
| **Hardware** | Supermicro X10DAI, Intel Xeon E5-1620 v4 (4-core/8-thread), 64GB DRAM, one NVIDIA GTX 1080Ti GPU, one 280GB Intel Optane 900p SSD; Ubuntu 16.04, kernel 4.15 |
| **Compiler and flags** | CUDA 10.1; host compiler and flags not stated. Prototype built on LevelDB v1.22 (\~1K LOC modified, +2.7K LOC CUDA), with Snappy compression not implemented. Compared against RocksDB v6.4.6 with 4 threads; all stores use default parameters and 10-bit Bloom filters. |
| **Links** | [benchmark](https://arxiv.org/abs/2004.03054) |

## Verdict

The HUST authors ran YCSB-A (50/50 update/read) with 16 B keys and 128 B-1 KB values: 10M pairs loaded (about 5 GB), then 10M operations, with 4 MB memtables/SSTs, 4 KB blocks and 10-bit Bloom filters. They compared against LevelDB 1.22 and RocksDB 6.4.6 (4 threads), on a 4-core/8-thread Xeon E5-1620 v4 with 64 GB RAM, a GTX 1080Ti, an Optane 900p and Ubuntu 16.04 with CUDA 10.1, and used stress-ng to load the CPU to 0/40/80%. At 80% stress and 1 KB values, LUDA got about 2x the throughput of both baselines: RocksDB kept about 30% of its unstressed throughput and LUDA/LevelDB about 70%, and running time grew by 100 s for LUDA vs 203 s for LevelDB. With a free CPU, RocksDB was fastest. Host compiler and flags are not stated, and nobody else has reproduced the results.

## Use it when

- As a design reference for moving LSM compaction CPU work (block CRC, prefix-key decode/encode, Bloom filter build) onto a GPU, on hosts where other tenants leave the KV store about 20% of the CPU. That is the only setting where it beat both baselines by about 2x.
- Write-heavy or mixed (YCSB-A-shaped) workloads on very fast storage (the paper used an Intel Optane 900p), with a small host CPU (4 cores / 8 threads) and a spare NVIDIA GPU. In that setup LevelDB-style compaction is CPU-bound.
- When steady 99th-percentile write latency under a LevelDB-style engine matters more than peak throughput. With no CPU stress, the paper's Fig. 12 shows LUDA with the lowest and flattest p99 of the three stores after a short warm-up spike. Under 80% CPU stress, its average write latency rose by only 7 us.
- As a starting point for reading the later GPU-compaction papers that cite it (gLSM in ACM TOS 2024, RGKV in IEEE TC 2025, GPComp in TPDS 2025, gParaKV, GCLComp). gLSM's abstract adds a GPU-oriented radix sort and key-value separation, the two costs LUDA leaves on the CPU and the PCIe bus.

## Skip it when

- Whenever you need something to run. There is no source, binary, license or build instructions. GitHub searches for LUDA and for GPU LevelDB/LSM compaction find nothing, and the footnote's github.com/anonymous link is a dead placeholder.
- Hosts with free CPU. With no CPU stress, stock RocksDB 6.4.6 (4 threads) finished the 5 GB YCSB-A run fastest at every value size and LUDA came second. In the one-hour 50 GB run, RocksDB with 4 background jobs also had the shortest running time.
- Read-dominated workloads. LUDA does not touch the read path, and the paper blames part of its throughput loss under CPU stress on reads that get less CPU time.
- Machines without an NVIDIA CUDA GPU, or where the extra PCIe traffic and host CPU cost matter. LUDA used more CPU than LevelDB because data moves back and forth between CPU and GPU, and every compaction stages SSTs in host RAM.
- Workloads that need compressed SSTs or low SSD write amplification. Snappy is not implemented. Because the prototype triggers compaction only when L0 is full and does not flush the immutable memtable first, it compacts about 2x as much data as LevelDB at 128 B values.

## How it is fast

Compaction is split into three GPU phases that can run in parallel. An 'unpack' kernel runs per input SST, verifying each data block's CRC32 and rebuilding the prefix-compressed keys. It stores values in a KV pair buffer and emits small &lt;key, value_offset&gt; tuples. Packing uses three kernels: 'shared_key' rebuilds prefix-shared keys per 4 KB block, 'encode' copies values in and computes CRC32 per block, and 'filter' builds the Bloom filter block. Finished data blocks are sent back to the host with cudaMemcpyAsync while the filter is still being built. The merge-sort itself is not done on the GPU: the tuples are copied to the host, deduplicated and sorted on the CPU, then copied back (the 'cooperative sort'). Values move only twice ('lazy value movement'), and every SST goes SSD -&gt; host RAM -&gt; GPU and back, with no GPUDirect Storage.

## Compared with alternatives

You can't pick it for deployment, because there is no code. For a code-available LevelDB-lineage speedup, use HyperLevelDB (about 3.4x LevelDB on 100M writes). To cut compaction work itself, use PebblesDB (guards) or MatrixKV/SpanDB on fast storage. Read LUDA only as the catalogued reference for offloading compaction to a GPU when the host CPU is contended.

## Integration

| | |
|---|---|
| **Form** | none published: a paper-only modification of LevelDB 1.22 (about 1K LOC changed, 2.7K LOC of CUDA added); no source, library or binary |
| **Dependencies** | NVIDIA GPU and CUDA toolkit 10.1 (per the paper); otherwise LevelDB 1.22's own build (CMake 3.9+, optional libsnappy, which LUDA's compaction path does not use) |
| **Minimum toolchain** | not documented; the paper names CUDA 10.1 but no host compiler or flags. The LevelDB 1.22 base it forks sets CMAKE_CXX_STANDARD 11 |
| **Platforms** | Tested only on x86-64 Linux (Ubuntu 16.04, kernel 4.15) with a Pascal-generation GTX 1080Ti; needs a CUDA-capable NVIDIA GPU; other GPUs, OSes and architectures not documented |
| **Thread safety** | not documented; stock LevelDB's DB handle is safe for concurrent use, and the paper does not say whether the GPU compaction path changes that |
| **Drop-in for the baseline** | partial — as a LevelDB 1.22 fork it presumably keeps LevelDB's C++ API, but no code exists to check that. SSTs are written without Snappy, and on-disk compatibility with stock LevelDB files is not discussed |

## Gotchas

- The headline depends on the scenario. 'Up to 2x higher throughput' comes from the 80% stress-ng setting (20% of a 4-core CPU left) at 1 KB values. The text gives no numbers for the other cells, and Fig. 7/8 bars carry no value labels.
- The '2x data processing speed' / 'compaction speed 1x faster than LevelDB' claim divides compaction bytes by running time. Part of those bytes is extra work the prototype creates for itself: it compacts about 2x LevelDB's data at 128 B values. The '46% less running time' at 1 KB does not say which CPU-stress level it refers to.
- The compression settings may favor LUDA. All stores ran with 'default parameters', and LevelDB 1.22's default is kSnappyCompression whenever it is built with libsnappy, but LUDA does no compression at all. The paper does not say whether the baselines were built with Snappy, so their CPU budget may include compression work that LUDA skips.
- The manuscript has draft errors. The 50 GB run is called '0.1 billion' pairs in Section IV-A but '0.1 million' in IV-D. The text cites Fig. 9 (latency) for running times that are in Fig. 8. It is an arXiv v1 (7 Apr 2020) only, with no peer-reviewed version in Crossref.

## Known shortcomings

- The 2x appears only with 80% of CPU consumed by stress-ng; with free CPU RocksDB is fastest. No public code (the linked repo is github.com/anonymous) and no peer-reviewed version.
- Sorting still runs on the CPU and every SST crosses SSD to host to GPU; uses more CPU than LevelDB. Baselines ran defaults (LevelDB 1.22 uses Snappy while LUDA has none, so compression may be unequal); at 128 B it compacts \~2x LevelDB's data due to a prototype shortcut, inflating the data-speed metric. Draft errors in the arXiv v1; later GPU-compaction papers (gLSM TOS'24, RGKV TC'25, GPComp) are better references.

## Caveats and trade-offs

The win depends on CPU contention. The 2x throughput appears only when stress-ng uses 80% of the CPU. With a free CPU, RocksDB finishes the 5 GB run fastest and LUDA is only ahead of LevelDB. LUDA has no Snappy compression, and it compacts about 2x more data than LevelDB at 128 B values. The paper says 'we are ready to open source it', but the footnote only links the anonymized placeholder github.com/anonymous. No public repository was found (GitHub repo search), so has_code=false and repo_url is null. arXiv preprint only; no peer-reviewed version found.

Requires a discrete NVIDIA GPU and CUDA; only bloom-filter/compaction sorting is GPU-accelerated, snappy compression is not yet supported; benefits are largest when the host CPU is otherwise busy.

## Maintenance

Paper only: arXiv v1 (April 2020) with no later version, no journal reference and no public repository or license, so maintenance is unknown and it is usable only as a design reference. Semantic Scholar lists about 21 citing papers, including newer GPU-compaction systems (gLSM, RGKV, GPComp) that are better starting points today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** arXiv preprint (Apr 2020) with first-party results against LevelDB 1.22 and RocksDB 6.4.6. The hardware and software are stated, but there is no public code (the footnote points to github.com/anonymous) and no host compiler or flags. I found no peer-reviewed version via crossref, so it stays C.
- **Verifier notes:** The abstract's 'up to 2x throughput / 2x data processing speed' is quoted accurately. The body shows that the 2x comes only with 80% CPU stress, and RocksDB is fastest when the CPU is free, so the claim was overstated. It is rewritten with its conditions; the tier stays C. The hardware in the record matches Section IV-A exactly.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2004.03054>
  - <https://arxiv.org/pdf/2004.03054>
  - <https://api.crossref.org/works?query.bibliographic=LUDA+Boost+LSM+Key+Value+Store+Compactions+GPUs&rows=4>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2004.03054>
  - <https://arxiv.org/pdf/2004.03054>
  - <https://api.github.com/search/repositories?q=LUDA+LSM>
  - <https://api.github.com/search/repositories?q=GPU+compaction+LevelDB>
  - <https://api.github.com/search/repositories?q=LUDA+leveldb>
  - <https://api.github.com/search/repositories?q=leveldb+cuda+compaction>
  - <https://api.github.com/search/repositories?q=gpu+lsm+compaction>
  - <https://api.github.com/search/code?q=LUDA+leveldb+cuda>
  - https://api.github.com/graphql (repository search: 'gpu compaction lsm', 'LUDA cuda', 'leveldb gpu', 'gLSM', 'lsm gpu in:readme')
  - https://api.github.com/users/anonymous (HTTP 404)
  - <https://api.crossref.org/works?query.bibliographic=GPU+accelerated+compaction+LSM+key+value+store&query.author=Wan&rows=8>
  - <https://api.crossref.org/works/10.1145/3633782>
  - <https://api.crossref.org/works/10.1109/TC.2025.3535832>
  - https://api.semanticscholar.org/graph/v1/paper/arXiv:2004.03054 (HTTP 429)
  - <https://api.semanticscholar.org/graph/v1/paper/arXiv:2004.03054/citations>
  - <https://arxiv.org/pdf/2609.14370>
  - <https://hn.algolia.com/api/v1/search?query=LUDA%20GPU%20compaction&tags=story>
  - <https://github.com/google/leveldb/blob/1.22/include/leveldb/options.h>
  - <https://github.com/google/leveldb/blob/1.22/CMakeLists.txt>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:luda`) · [data/wave6/enrich/raw/paper_luda.json](../../../data/wave6/enrich/raw/paper_luda.json) (enrichment confidence 0.72)

</details>
