# Bourbon (learned index for LSM-trees, OSDI'20 artifact)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> LevelDB/WiscKey-based LSM key-value store that swaps SSTable index search for per-file linear models; 1.23-1.78x faster lookups than WiscKey.

| | |
|---|---|
| **Beats** | WiscKey (the authors' LevelDB-derived LSM with key-value separation; no direct stock-LevelDB or RocksDB comparison) |
| **Claimed result** | Abstract: "BOURBON improves lookup performance by 1.23x-1.78x as compared to state-of-the-art production LSMs". In Fig. 9 the baseline is WiscKey, with 1.23x-1.78x lower average lookup latency across six datasets. vs WiscKey elsewhere: YCSB-C about 1.6x, YCSB-B/D 1.24x-1.44x, YCSB-A/F 1.06x-1.18x, YCSB-E 1.16x-1.19x; SOSD 1.48x-1.74x; Optane SSD 1.25x-1.28x; SATA SSD with limited memory 1.04x (uniform) and 1.25x (zipfian). |
| **Workload** | Read-only lookups (10M operations, 16B integer keys, 64B values, in-memory) on six datasets (linear, seg-1%, seg-10%, normal with 64M keys; Amazon Reviews 33.5M; NY OpenStreetMaps 21.9M), comparing Bourbon's per-file greedy piecewise-linear-regression models (error bound 8) with the WiscKey baseline; plus YCSB, SOSD, Optane SSD and limited-memory runs. |
| **Metric** | latency |
| **Hardware** | 20-core Intel Xeon CPU E5-2660, 160 GB memory, 480 GB SATA SSD (CloudLab c220g2 per ARTIFACT_README); the fast-storage runs used an Intel Optane SSD. |
| **Compiler and flags** | Compiler not stated; built with cmake -DCMAKE_BUILD_TYPE=RELEASE -DNDEBUG_SWITCH=ON (ARTIFACT_README/CS736_README) |
| **Adoption** | 47 stars |
| **Last commit** | 2023-09-06 |
| **Links** | [repository](https://bitbucket.org/daiyifandanny/learned-leveldb) · [benchmark](https://www.usenix.org/conference/osdi20/presentation/dai) |

## Verdict

The OSDI'20 paper ran 10M in-memory read-only lookups with 16 B integer keys and 64 B values on six datasets (four synthetic 64M-key sets, Amazon Reviews 33.5M, NY OSM 21.9M). Bourbon's file models (delta = 8) averaged about 2.65-3.64 us per lookup, 1.23-1.78x lower latency than WiscKey, the authors' LevelDB-derived key-value-separated LSM built from the same codebase. The machine was a 20-core Xeon E5-2660 with 160 GB RAM and a SATA SSD (an Optane SSD for the fast-storage runs); the compiler is not stated, and there is no RocksDB or stock-LevelDB head-to-head.

## Use it when

- Read-dominated LSM workloads where the working set is in the page cache or on Optane-class storage, so indexing dominates lookup time: about 1.6x on YCSB-C and 1.23-1.78x on in-memory read-only lookups vs WiscKey.
- Fixed-width integer keys (zero-padded decimal strings such as the paper's 16 B keys) with smooth distributions. Fewer PLR segments means bigger gains: the linear dataset, at one segment per file, got 1.78x.
- Point lookups and very short scans: 1.90x at range length 1 on the Amazon Reviews data, falling to 1.15x at 100 items.
- Skewed (zipfian) reads on a memory-limited SATA-SSD machine where the hot set stays cached: 1.25x lower latency.
- Reproducing or extending learned-index-in-LSM research. The repo ships the WiscKey baseline mode (-m 8), the read_cold driver and the scripts/run_\*.sh experiment scripts.

## Skip it when

- Production storage. It is an abandoned research artifact configured through global variables. Value-log garbage collection was never ported (Vlog.h: 'Bourbon doesn't test on deletion'), so overwrites and deletes never reclaim space.
- String or variable-length keys, or key compression. The paper says these are unsupported, and the code turns keys into integers by parsing ASCII decimal digits (SliceToInteger).
- Write-heavy workloads. Writes are not sped up, and YCSB-A/F gain only 1.06-1.18x. Always re-learning at 50% writes did more total work than plain WiscKey, and level learning ran slower than baseline (0.87x).
- Uniform random reads over data much larger than RAM on a SATA SSD. I/O dominates and the gain is only 1.04x.
- If you need proof it beats RocksDB or stock LevelDB. The paper and repo compare only against their own WiscKey port, whatever the abstract's 'production LSMs' wording says.

## How it is fast

Each SSTable gets a greedy piecewise linear regression model (GreedyPLR, adapted from RyanMarcus/plr) with error bound delta = 8. A lookup binary-searches the model's segments, predicts the key's position plus or minus delta, and reads only that byte range of the data block. Because entries are fixed-size, this replaces the index-block and data-block binary searches and also cuts the bytes loaded. A cost-benefit analyzer waits T_wait = 50 ms after a file is created, then learns the file only if the estimated lookup-time savings (per-level stats for positive and negative lookups) outweigh the training cost, so short-lived files under writes are skipped. The paper prefers file models to whole-level models because levels change constantly under writes; level learning only pays off when read-only.

## Compared with alternatives

The catalogued learned indexes (PGM-index, RMI, RadixSpline, ALEX, LIPP) are in-memory structures over sorted arrays. Pick Bourbon only when you want learned indexing inside a persistent LSM store with write-aware re-learning, mainly as a research base. To embed an index, use PGM-index or ALEX. For a production LSM that measurably beats RocksDB, TerarkDB is the catalogued choice.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target 'leveldb', a modified LevelDB 1.22; shared build via BUILD_SHARED_LIBS) plus the read_cold benchmark driver |
| **Dependencies** | Threads (required). snappy, crc32c and tcmalloc are auto-detected and optional. cxxopts is bundled (mod/cxxopts.hpp) for read_cold. |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11), CMake &gt;= 3.7. Compiler and version not documented. |
| **Platforms** | x86-64 Linux in practice. mod/util.h includes &lt;x86intrin.h&gt; and uses __rdtscp, and the experiment scripts drop caches with sudo via /proc/sys/vm/drop_caches. Windows and non-x86 builds not documented. |
| **Thread safety** | Not documented. From reading the code: DBImpl's constructor sets the global pointer adgMod::db and the mode and key size are globals, so it is effectively one DB per process. DBImpl::Put appends to the VLog buffer before taking the DB mutex, and VLog has no lock. Get reads that buffer outside the mutex, so concurrent writers, or reads racing writes, look unsafe. |
| **Drop-in for the baseline** | partial — it keeps the leveldb::DB Open/Put/Get API, but the mode is set through globals, the on-disk format stores value-log pointers (not LevelDB-compatible), and in the code reviewed DB iterators never dereference the value log, so scans return raw 12-byte pointers rather than values. |

## Gotchas

- Wrong-result bug in the OSDI snapshot. If the same user key is written twice before a flush, both versions land in one SSTable, the PLR computes a NaN slope, and Get can fail. PR #7 (merged 2023-09-06) reported more than 3% bad Gets on a real-world trace. Only this fork's main branch has the fix (commit 0cd4715). The 'original bourbon' commit ad6abcb and the Bitbucket artifact (last updated 2020-10-05) predate it.
- Fixed-size keys are assumed. generate_key zero-pads decimal keys to key_size, and block entry count and entry size are recorded once in globals, so the byte-range read assumes every entry has the same size.
- Experiment config is fiddly. Mixed read-write runs need a rebuild with -DLEVEL_SWITCH=ON -DINTERNAL_TIMER_SWITCH=ON (CS736_README). The reported numbers use file models (--change_level_load, called 'Sazerac-File' in the README). The CPU frequency used to turn rdtscp cycles into time for the learning timers is hardcoded (reference_frequency = 2.6).
- Hard to reproduce. Issue #6 reports segfaults in scripts/run_load_order.sh with no fix. The datasets are not published (issues #5, #8). The artifact's ready-made CloudLab machine was only for OSDI reviewers and UW-Madison students (issues #2, #3).

## Known shortcomings

- The only baseline is WiscKey (LevelDB-derived), never RocksDB or stock LevelDB; no compiler stated. github.com/edydfang/bourbon is a third-party course-project copy; the authors' original code is bitbucket.org/daiyifandanny/learned-leveldb.
- Wrong-result bug in the OSDI snapshot: a duplicate user key within one SSTable gives a NaN PLR slope and over 3% bad Gets on a real trace (PR #7; fixed only in a fork in 2023). Value-log GC was never ported, so overwrites and deletes never free space.
- Keys must be fixed-width ASCII-decimal integers; x86 only (rdtscp); mode is set by process globals (one DB per process). From code reading, iterators return raw value-log pointers and Put/Get touch the value-log buffer outside the DB mutex, so concurrent use looks unsafe. Hard to reproduce: segfault issue #6 open and datasets never published.

## Caveats and trade-offs

The only baseline is WiscKey (a research LSM built on LevelDB), despite the abstract's 'production LSMs' wording; there is no RocksDB or stock-LevelDB head-to-head. Gains are for lookups only, with integer keys; string keys and key compression are unsupported, and writes are not improved. This GitHub repo is not the authors' own: a third party (Edward Fang) imported it as a snapshot ('original bourbon', 2020-10-11) of the authors' Bitbucket learned-leveldb artifact. It then added CS736 course-project changes (offline/synchronous level learning, 'mode 9') and a 2023 PLR NaN-slope fix. The README says the owner is not the paper's author. Compiler is unstated.

Learned index is trained per SSTable file at compaction time using a cost-benefit rule to decide when learning is worthwhile; benefits are workload/data-distribution dependent (helps most when keys within a file are well-approximated by a piecewise-linear model).

## Maintenance

Abandoned: the fork's last commit is 2023-09-06 (a bug-fix PR) and the authors' Bitbucket original was last updated 2020-10-05; the code is BSD-3-Clause and about 5K LOC on top of a WiscKey port, fine for research but not production-ready (no value-log GC, global config).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** OSDI'20 peer-reviewed paper; every result compares Bourbon only against WiscKey, the authors' LevelDB-derived key-value-separated LSM, not against stock LevelDB or RocksDB. The CPU (Xeon E5-2660) and code (read_cold, scripts/run_\*.sh; CMake RELEASE build) are available, but the compiler and its version are never stated, so it is not A.
- **Verifier notes:** The 1.23x-1.78x quote is verbatim from the USENIX abstract and paper. The record's baseline ('LevelDB / production LSM (RocksDB-class)') and workload ('unmodified production LSM implementations') overstate it, because the paper measures only against WiscKey. Kept at B, not rejected, since WiscKey is a recognizable LevelDB derivative. The authors' original code is public at bitbucket.org/daiyifandanny/learned-leveldb (Bitbucket API: public, last updated 2020-10-05); consider re-pointing the entry there. gh metadata matches: BSD-3-Clause, 47 stars, last commit 2023-09-06 (abandoned, just over 3 years old).
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `workload`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/conference/osdi20/presentation/dai>
  - <https://www.usenix.org/system/files/osdi20-dai_0.pdf>
  - <https://github.com/edydfang/Bourbon>
  - <https://github.com/edydfang/Bourbon/blob/main/ARTIFACT_README>
  - <https://github.com/edydfang/Bourbon/blob/main/CS736_README>
  - <https://bitbucket.org/daiyifandanny/learned-leveldb>
  - <https://api.bitbucket.org/2.0/repositories/daiyifandanny/learned-leveldb>
- **Sources the enricher read:**
  - <https://github.com/edydfang/Bourbon>
  - <https://github.com/edydfang/Bourbon/blob/main/README.md>
  - <https://github.com/edydfang/Bourbon/blob/main/ARTIFACT_README>
  - <https://github.com/edydfang/Bourbon/blob/main/CS736_README>
  - <https://github.com/edydfang/Bourbon/blob/main/CMakeLists.txt>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/learned_index.h>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/learned_index.cpp>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/plr.h>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/plr.cpp>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/util.h>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/util.cpp>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/CBMode_Learn.h>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/CBMode_Learn.cpp>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/Vlog.h>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/Vlog.cpp>
  - <https://github.com/edydfang/Bourbon/blob/main/mod/read_cold.cc>
  - <https://github.com/edydfang/Bourbon/blob/main/db/db_impl.cc>
  - <https://github.com/edydfang/Bourbon/blob/main/db/db_iter.cc>
  - <https://github.com/edydfang/Bourbon/blob/main/db/version_set.cc>
  - <https://github.com/edydfang/Bourbon/blob/main/table/table.cc>
  - <https://github.com/edydfang/Bourbon/commits/main>
  - <https://github.com/edydfang/Bourbon/issues?q=is%3Aissue>
  - <https://github.com/edydfang/Bourbon/issues/2>
  - <https://github.com/edydfang/Bourbon/issues/3>
  - <https://github.com/edydfang/Bourbon/issues/4>
  - <https://github.com/edydfang/Bourbon/issues/5>
  - <https://github.com/edydfang/Bourbon/issues/6>
  - <https://github.com/edydfang/Bourbon/issues/8>
  - <https://github.com/edydfang/Bourbon/issues/9>
  - <https://github.com/edydfang/Bourbon/pull/1>
  - <https://github.com/edydfang/Bourbon/pull/7>
  - <https://www.usenix.org/conference/osdi20/presentation/dai>
  - <https://www.usenix.org/system/files/osdi20-dai_0.pdf>
  - <https://api.bitbucket.org/2.0/repositories/daiyifandanny/learned-leveldb>
  - <https://api.bitbucket.org/2.0/repositories/daiyifandanny/learned-leveldb/commits>
  - <https://hn.algolia.com/api/v1/search?query=bourbon%20learned%20index&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/edydfang/bourbon`) · [data/wave6/enrich/raw/github_com_edydfang_bourbon.json](../../../data/wave6/enrich/raw/github_com_edydfang_bourbon.json) (enrichment confidence 0.8)

</details>
