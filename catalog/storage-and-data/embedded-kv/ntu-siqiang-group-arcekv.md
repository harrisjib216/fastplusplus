# ArceKV (ElasticLSM + Arce)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0 (GitHub-detected; repo is a modified RocksDB tree that ships both LICENSE.Apache and LICENSE.leveldb, matching RocksDB's dual Apache-2.0/GPL-2.0 licensing)` · 🟢 active

> RocksDB fork whose workload-driven compaction and write-stall policy (Arce) beats RocksDB leveling when read/write mixes shift.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Paper: average 2.00x and 1.41x over 1-Leveling (RocksDB's default compaction style, the strongest baseline) across the two dynamic workloads; 2.17x-2.92x over Tiering and LazyLeveling; around 3x faster than state-of-the-art compaction strategies in dynamic scenarios; over 10x vs Cassandra and WiredTiger and 3x vs Pebble. Repo README (prod branch, in-memory tmpfs variant vs RocksDB leveling): total latency 282.09s vs 808.85s at read_ratio 0.1 (2.87x) shrinking to 438.04s vs 479.20s at 0.9 (1.09x) (derived from page data). |
| **Workload** | Dynamic and static read/write-ratio workloads on a RocksDB-based KV store, cgroup-capped memory (75GiB), comparing against RocksDB's own Leveling/1-Leveling/Tiering compaction styles and academic baselines (LazyLeveling, Moose, Ruskey, CAMAL) |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-13900K (5.40GHz), 128GB RAM, 1TB NVMe SSD, Ubuntu 22.04, ext4, memory capped at 75GiB via cgroup |
| **Compiler and flags** | Not stated in paper; repo README lists gcc/g++ (version unstated) with a CMake Release build |
| **Adoption** | 1 star |
| **Last commit** | 2026-04-29 |
| **Links** | [repository](https://github.com/NTU-Siqiang-Group/ArceKV) · [benchmark](<https://arxiv.org/abs/2508.03565 (PVLDB 19(5): 958-972, 2026; https://www.vldb.org/pvldb/vol19/p958-liu.pdf)>) |

## Verdict

In PVLDB 19(5):958-972 (2026), on an i9-13900K with 128 GB RAM capped to 75 GiB, NVMe/ext4, one flush and one compaction thread, and two 245.76M-operation compound workloads, ArceKV's average throughput was 2.00x and 1.41x that of 1-Leveling (RocksDB's default style, reimplemented on the RocksDB-based Moose framework) and 2.17x-2.92x that of Tiering and LazyLeveling; no compiler or flags are stated, and the abstract's '\~3x' is measured against the slowest baseline. The prod README's own test (tmpfs, one thread, point reads plus inserts, uniform keys, 64 MB memtable, no compression, compared against RocksDB 9.5 leveled compaction with dynamic level bytes off) shows 2.87x lower total time at 10% reads, shrinking to 1.09x at 90%.

## Use it when

- Reproducing or extending workload-aware LSM compaction research (against Moose, Ruskey, CAMAL, LazyLeveling) on a RocksDB code base with \~1 KB values, as in the paper (24 B keys, 1000 B values).
- Read/write mixes that shift over time (for example, write-heavy ingest followed by read-heavy serving), where you know or can measure the mix and pass it to the controller.
- Write-heavy to balanced phases where leveled RocksDB is stall-bound. The prod README's tmpfs table shows the largest gains at 10-40% reads (2.87x to 1.39x lower total time), mostly on the write side: 183.7 s vs 702.7 s of write latency at 10% reads.
- In-memory or tmpfs single-column-family stores with one compaction stream, which is the setup the prod branch was adapted to (a TikTok recommendation service) and the setup both repo harnesses test.
- Linux x86-64 with GCC and OpenMP available; the paper and README results are from an i9-13900K on Ubuntu 22.04.

## Skip it when

- Production systems that need a supported RocksDB: 1 star, no releases, and the default branch says it is not a faithful implementation of the paper.
- Steady read-dominated workloads. At 90% reads the prod gain is about 9% (438 s vs 479 s), and the paper shows ArceKV trailing 1-Leveling and Leveling right after an abrupt write-to-read shift (workload B to D).
- On-disk stores sensitive to insert latency or SSD wear. The dev README's on-disk run has higher insert latency (2.45 us vs 2.15 us) and 54% more compaction writes (426 GB vs 276 GB) than leveled compaction.
- Setups that rely on parallel compactions. Both branches assume one compaction decision stream: dev logs a warning when max_background_jobs or max_background_compactions is above 1 ('may lead to unstable run indexing'), and the paper's evaluation used one compaction thread.
- Workloads that need range filters or an up-to-date upstream: prod removed the range-filter policy and is pinned to RocksDB 9.5.

## How it is fast

Each candidate compaction gets an 'effectiveness score': M times its long-term benefit (runs removed x (range + FPR x point) lookup cost) minus a short-term penalty for the reads slowed and writes stalled while it runs. Only non-dominated candidates can win, meaning none removes more runs in less time. Write stalls are decoupled from level shape: in the prod code, writes slow once the count reaches a threshold c and stop at 4c. A background simulation over a windowed cost model (one window = memtable size / entry size updates) grid-searches (M, c) on 16 OpenMP threads and reruns when the average run count drifts more than 10%. In read-heavy phases this yields multi-level merges that cut runs faster than Leveling; in write-heavy phases it defers compaction more than Tiering.

## Compared with alternatives

Pick ArceKV over Titan or DobLIX when the problem is compaction and write-stall policy under a read/write mix that changes over time with \~1 KB values: Titan targets large values through key-value separation, and DobLIX speeds up SST index lookups but gains only 1.04x on write-heavy loads. If you can leave RocksDB's format entirely and want bigger raw write gains from a maintained engine, pick SplinterDB, KVell or F2 instead.

## Integration

| | |
|---|---|
| **Form** | static lib (a full RocksDB source fork built with CMake; it replaces librocksdb instead of linking beside it) |
| **Dependencies** | prod: gflags, OpenMP (REQUIRED in CMakeLists; &lt;omp.h&gt; is included from a public header), and the grafite git submodule (SSH URL git@github.com:marcocosta97/grafite.git, pulling sux and sdsl-lite headers) included by table/block_based/filter_policy_internal.h. The tools/arce_bench harness also links TBB. dev: gflags, with OpenMP optional (WITH_OPENMP=ON by default, falls back to serial) and no submodules. RocksDB's usual optional compression libraries apply to both. |
| **Minimum toolchain** | prod: C++17 (RocksDB 9.5 base), CMake 3.10+. dev: C++20 (CMAKE_CXX_STANDARD 20, RocksDB 11.2 base). Compiler versions are not documented beyond 'gcc/g++'. |
| **Platforms** | Tested only on Linux x86-64 (Ubuntu 22.04, i9-13900K). Other RocksDB platforms are not documented, and prod will not build on a toolchain without OpenMP. |
| **Thread safety** | Normal RocksDB DB-handle thread safety. Controller state is guarded by a std::mutex, but the compaction policy assumes one active compaction decision at a time (prod's picker bails out if a chosen file is already being compacted, and dev warns when background jobs are above 1). |
| **Drop-in for the baseline** | partial — same RocksDB API, but you build this fork instead of upstream, set a non-upstream compaction_style and controller object, and supply workload ratios yourself; compatibility of the resulting DB directories with upstream RocksDB is not documented |

## Gotchas

- prod: the AdaptiveCompactionController is a raw pointer in Options that the README example allocates with new and never frees. Its constructor spawns a detached thread that captures this and loops with 5 s sleeps, so deleting the controller while that thread is alive is a use-after-free. DB::Open also blocks in find_first_mc_when_ready(), polling once a second until the first tree state appears, and prints timings to stdout.
- prod: ColumnFamilyData::RecalculateWriteStallConditions (db/column_family.cc) reads comp_controller-&gt;compactioner without a null check, so column families that do not use the dynamic style depend on the optimizer removing that dead load. The stall check also compares the L0 file count against c and 4c, while the simulation models total runs. The README's cmake line '-CMAKE_BUILD_TYPE=Release' is a typo; use -DCMAKE_BUILD_TYPE=Release, because RocksDB's CMakeLists makes a git checkout a Debug build by default.
- dev: if arce_compaction_controller is null, PickCompaction builds a fresh default controller on every call, so the (M, c) grid search reruns on every pick with a default update-only workload. Even with a controller, the search runs inside PickCompaction (which RocksDB calls with the DB mutex held), and both branches call omp_set_num_threads(16), which changes the OpenMP thread count for the whole process.
- The library does not measure the workload mix. You pass range/update/point proportions (prod: once, at construction; dev: via SetWorkloadProportions, which the dev harness calls at each phase change). The paper's online workload-statistics module and Eigen/SIMD score vectorization are not present in either branch.

## Known shortcomings

- The default branch (prod) is an in-memory TikTok variant that does not match the paper; the on-disk code on the dev branch shows only 1.41x runtime. Paper gives no compiler or flags; venue is PVLDB 19(5) 2026.
- Prod branch: the compaction controller is a raw pointer with a detached thread capturing 'this' (use-after-free if deleted); DB::Open blocks polling for the first state; compactioner is read without a null check; a README cmake typo gives a Debug build. Dev branch: a null controller creates a new default one per pick, running a grid search under the DB mutex; omp_set_num_threads(16) is process-wide.
- The workload mix is supplied by the caller, not measured; the paper's Eigen SIMD and online statistics modules are absent from both branches; single compaction stream only. The abstract's \~3x is vs the slowest baseline; on disk (dev) insert latency is worse and compaction writes rise 54%.

## Caveats and trade-offs

The paper states no compiler or flags. The 1-Leveling/Leveling/Tiering/LazyLeveling baselines were implemented on the RocksDB-based Moose framework, not stock RocksDB builds. Stock RocksDB appears only in the industrial-system comparison. The default 'prod' branch is explicitly NOT a faithful implementation of the paper: it is an in-memory adaptation for a TikTok recommendation service. An on-disk version was published on the 'dev' branch (2026-04-29), and its README reports a modest gain over leveled compaction: 1.41x total runtime (929.0s vs 1310.5s) and about 10% lower all-op latency, with worse insert latency (2.45us vs 2.15us) and higher compaction I/O. The prod README's cmake line has a typo (-CMAKE_BUILD_TYPE). License: GitHub detects GPL-2.0; the tree carries RocksDB's COPYING (GPLv2), LICENSE.Apache and LICENSE.leveldb.

Replaces RocksDB's fixed compaction hierarchy with a workload-adaptive engine (Arce) that expands the compaction/write-stall action space; adds a decision-engine overhead and requires online profiling to adapt to workload shifts, versus RocksDB's simpler static leveling/tiering.

## Maintenance

An active research artifact (last push 2026-04-29, 1 star, 0 issues, no releases), dual-licensed GPLv2/Apache-2.0 like RocksDB; using it means building the whole fork, with prod as the in-memory TikTok adaptation and dev as the on-disk port on RocksDB 11.2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 19(5):958-972 (2026) paper with public artifact repo (NTU-Siqiang-Group/ArceKV; prod branch tools/arce_bench, dev branch examples/arce_dynamic_compaction_integration.cc) and stated hardware (i9-13900K), but neither the paper nor the READMEs state a compiler version or flags (README only says gcc/g++ with a CMake Release build), so it cannot be A.
- **Verifier notes:** The paper is real and peer-reviewed (PVLDB vol 19 issue 5, 2026, not VLDB 2025 as recorded), and the headline numbers match its text. The tier drops from A to B because no compiler or flags are stated anywhere. The public default branch differs from the evaluated system, so treat the repo as a research artifact.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2508.03565>
  - <https://arxiv.org/abs/2508.03565>
  - <https://www.vldb.org/pvldb/volumes/19/>
  - <https://github.com/NTU-Siqiang-Group/ArceKV>
- **Sources the enricher read:**
  - <https://github.com/NTU-Siqiang-Group/ArceKV>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/tree/dev>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/tree/tier>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/include/rocksdb/dyncompactionv4.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/include/rocksdb/dynamic_lookforward.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/dyncompactioner.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/compaction/compaction_picker_dynamic.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/compaction/compaction_picker_dynamic.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/include/rocksdb/advanced_options.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/include/rocksdb/options.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/options/cf_options.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/column_family.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/db_impl/db_impl_open.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/db_impl/db_impl.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/db_impl/db_impl_write.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/db_impl/db_impl_compaction_flush.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/db/version_set.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/tools/arce_bench.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/tools/CMakeLists.txt>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/examples/run_arce_bench.sh>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/CMakeLists.txt>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/.gitmodules>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/table/block_based/filter_policy_internal.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/table/block_based/range_filter.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/prod/include/rocksdb/version.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/dev/include/rocksdb/version.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/dev/include/rocksdb/arce_dynamic_compaction.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/dev/db/compaction/compaction_picker_arce.h>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/dev/db/compaction/compaction_picker_arce.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/dev/examples/arce_dynamic_compaction_integration.cc>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/blob/dev/CMakeLists.txt>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/issues>
  - <https://github.com/NTU-Siqiang-Group/ArceKV/forks>
  - <https://github.com/facebook/rocksdb/tree/v9.5.2>
  - <https://arxiv.org/pdf/2508.03565>
  - <https://www.vldb.org/pvldb/vol19/p958-liu.pdf>
  - <https://hn.algolia.com/api/v1/search?query=ArceKV>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ntu-siqiang-group/arcekv`) · [data/wave6/enrich/raw/github_com_ntu_siqiang_group_arcekv.json](../../../data/wave6/enrich/raw/github_com_ntu_siqiang_group_arcekv.json) (enrichment confidence 0.8)

</details>
