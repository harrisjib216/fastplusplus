# Cylon

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++/Arrow distributed-memory dataframe engine on MPI/UCX/Gloo that scales join, groupby and aggregation past serial pandas.

| | |
|---|---|
| **Beats** | pandas |
| **Claimed result** | Paper states Cylon's C++ local operators 'perform on par or better than pandas' at parallelism=1, and Figure 3 plots dotted lines for speed-up over pandas (pandas_time/time) that increase with core count; exact per-point multipliers are shown only in log-scale figures, not as a single quoted number in the text. |
| **Workload** | Distributed groupby/join/aggregation operators over a uniformly random two-int64-column, 10^9-row dataset (worst-case for key-based ops), run at increasing parallelism (1-512 cores) across a 15-node cluster, compared to serial pandas and to Dask/Modin. |
| **Metric** | throughput |
| **Hardware** | 15-node Intel Xeon Platinum 8160 cluster, 255GB RAM/node, SSD storage, Infiniband 40Gbps interconnect, up to 40 of 48 cores/node used |
| **Compiler and flags** | GCC v9.4, OpenMPI v4.1, Apache Arrow v5.0; explicit optimization flags (e.g. -O level) not stated |
| **Adoption** | 302 stars |
| **Last commit** | 2026-03-12 |
| **Links** | [repository](https://github.com/cylondata/cylon) · [benchmark](https://arxiv.org/abs/2209.06146) |

## Verdict

PPAM 2022 (arXiv 2209.06146), Fig. 3: strong scaling on 10^9 rows of two uniform-random int64 columns (C=0.9) on 15 Xeon Platinum 8160 nodes (up to 40 cores each, 40 Gbps InfiniBand). Cylon (GCC 9.4, OpenMPI 4.1, Arrow 5.0; optimization flags not stated) is plotted against serial pandas 1.4, Dask 2022.1 and Modin 0.12, with speedup over pandas drawn only as log-scale dotted lines. The gains come from 1-512 ranks versus one pandas process, time rises again at 512, and at one rank Cylon is described only as 'on par or better than pandas'.

## Use it when

- Joins or groupbys over roughly 10^8-10^9+ rows that don't fit comfortably in one pandas process, and you have a multi-node Linux/HPC cluster with MPI (ideally InfiniBand) already allocated to you
- BSP/mpirun batch pipelines where pandas-like data prep feeds MPI-based ML (e.g. PyTorch distributed) in the same processes, without a Spark/Dask scheduler
- High-cardinality key-based operations (the paper's C=0.9 worst case), where hash shuffle-compute scaled up to 256 ranks in the paper
- Low-cardinality groupby, where the combine-shuffle-reduce (mapred) groupby shrinks the shuffle a lot. The variant is chosen by the caller (pycylon groupby_type), not automatically.
- C++ codebases already on Arrow that want distributed relational operators with a pluggable transport (MPI, Gloo, UCX/UCC)

## Skip it when

- Single machine, or only a few cores: at parallelism 1 the paper claims only parity-or-better with pandas, and a single-node engine will usually do better
- Workloads that need broad pandas API coverage: coverage was about 25% at publication, and window and transpose operators were not implemented then
- Multi-tenant, elastic or fault-tolerant environments: the paper says execution needs dedicated resources and has no fault tolerance, and Release 2.0 checkpointing is labelled experimental
- Very small per-rank partitions: in the paper, wall time went back up from 256 to 512 ranks once communication dominated
- Teams that need prebuilt binaries: the only conda package (cylondata/pycylon 0.4.0) is linux-64 from 2021, so current code (Arrow 16.1, Release 2.0) has to be built from source

## How it is fast

Operators are built from BSP patterns. Shuffle-Compute hash-partitions rows (MurmurHash3 mod P), runs an all-to-all shuffle and then a local operator; Combine-Shuffle-Reduce pre-aggregates first, MapReduce-style; sort uses sample sort with regular sampling. The local operators are single-threaded C++ over Arrow columns: ska::bytell_hash_map row-index groupby, hash (std::unordered_multimap) or sort joins, and Arrow Compute where it fits. The speedup over pandas comes mainly from spreading work over hundreds of MPI ranks; at parallelism 1 the paper claims only 'on par or better than pandas'.

## Compared with alternatives

Pick Cylon over cuDF (cudf.pandas), data.table or chDB when the data and compute must span many CPU nodes under MPI rather than one GPU or one machine. Pick it over Bodo DataFrames when you want an Apache-2.0 C++ library of explicit Arrow operators with swappable transports, not a pandas-API/JIT layer.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Apache Arrow C++ (CMake pins 16.1.0; conda env pins pyarrow/libarrow 16.1.0), MPI (required even for other transports), glog; optional UCX/UCC, Gloo, Redis (hiredis, redis++), CUDA/cuDF for GCylon; Python bindings need Cython, NumPy &lt;2.0 and pandas &gt;=2.0,&lt;2.2.3 |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17), CMake 3.17+; CI uses GCC 11 on Ubuntu 22.04; the docs still say C++14 and CMake 3.16.5 (stale) |
| **Platforms** | Linux x86-64 is the primary target (README: 'only works on Linux'). There is a macOS conda env pinned to Arrow 9 and a Windows env file, but no current CI for either. SIMD level is set at build time: SSE4.2 by default, AVX2/AVX512 optional. |
| **Thread safety** | Not documented. The model is one single-threaded process per core. CylonContext::GetNextSequence is a plain non-atomic int32 increment, so don't share a context across threads. |
| **Drop-in for the baseline** | partial: pycylon.DataFrame mirrors pandas method names (merge, join, groupby, sort_values, drop_duplicates) but covers only a subset, needs an explicit env for distributed ops and must be launched under mpirun; the C++ API has nothing in common with pandas |

## Gotchas

- The default join algorithm is SORT, both in the C++ JoinConfig and in pycylon merge/join (algorithm="sort"). Request the hash join explicitly (JoinAlgorithm::HASH / algorithm="hash"). The multi-column hash join also returns Invalid on chunked arrays.
- hash_groupby.cpp is marked 'todo handle chunked arrays', and its aggregation loop reads only chunk(0) of each value column. Combine chunks (arrow::Table::CombineChunks) before grouping.
- Distributed sort throws 'empty vector passed onto merge' when any rank's partition is empty, which is common after a filter (open issues #664 and #611).
- Errors come back as Status, except that JoinConfig's constructor throws a raw string literal. That size check runs after std::move of the shadowed parameters, so it never fires, and mismatched key lists are reported later by Join().

## Known shortcomings

- The big gains are up to 512 cores vs serial pandas; compiler flags unstated.
- The speedup comes from MPI ranks (1-512 over 15 nodes) vs serial pandas; at one rank it is only 'on par or better' and time rises again at 512. \~25% pandas API coverage at publication (no window/transpose), no fault tolerance, needs dedicated resources. Default join is sort-based (hash must be requested); multi-column hash join rejects chunked arrays; groupby reads only chunk(0); distributed sort crashes when any rank is empty (#664, #611 open).
- The conda package is stale (0.4.0, 2021, linux-64 only), so build from source against Arrow 16.1 + MPI; docs say C++14 while CMake needs C++17; release 2.0 (2026-03) is mostly experimental features.

## Caveats and trade-offs

Speed-ups appear only as dotted log-log lines in Fig. 3 (pandas_time/time), so there is no tabulated headline number. At parallelism 1 the paper says only that Cylon's C++ local operators 'perform on par or better than pandas'. The large multipliers come from running on up to 512 cores (15 nodes) against single-threaded serial pandas, so this is a distributed-vs-serial comparison. Past 256 the wall-clock time rises again at 512 because communication dominates. The paper says Dask and Modin are 'compared here only as a baseline'. Modin join failed at 1B rows, so a 100M-row run was used instead. Data is uniform random with cardinality C=0.9. Venue is the peer-reviewed PPAM 2022 conference (LNCS), not a Euro-Par workshop. The benchmark scripts are in cylondata/cylon_experiments, which has no license detected by GitHub. Optimization flags are unstated.

Needs an MPI/UCX/Gloo runtime and a distributed cluster to realize the shown gains; pandas operator coverage was only \~25% at publication; the documented public interface is mostly the Python binding (pycylon) even though the core engine (libcylon) is C++.

## Maintenance

Active but research-driven: Release 2.0 (2026-03-12) added mostly experimental features (Rust port, checkpointing, WASM, SIMD), and CI still runs on feature branches in 2026-09. However, docs, conda packages (0.4.0) and many 2021-2023 issues are stale; Apache-2.0 and buildable from source with CMake, but not small enough to vendor casually.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PPAM 2022 paper (Springer LNCS, DOI 10.1007/978-3-031-30442-2_22). Its Fig. 3 plots Cylon strong scaling against serial pandas v1.4, Dask and Modin on a 1B-row, two-int64-column dataset, with speed-up over pandas on a log axis. Not A: the scripts are public (cylondata/cylon_experiments), and GCC v9.4 and the Xeon Platinum 8160 CPU are stated, but the optimization flags are not.
- **Verifier notes:** Record is accurate apart from the venue caveat and last_commit. pushed_at is 2026-05-26, but the latest commit on the default branch is 2026-03-12, which is still active. Stars (302), Apache-2.0, not a fork and not archived were all verified via gh.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2209.06146>
  - <https://arxiv.org/pdf/2209.06146>
  - <https://github.com/cylondata/cylon>
  - <https://github.com/cylondata/cylon_experiments>
- **Sources the enricher read:**
  - <https://github.com/cylondata/cylon>
  - <https://github.com/cylondata/cylon/blob/main/README.md>
  - <https://github.com/cylondata/cylon/blob/main/cpp/CMakeLists.txt>
  - <https://github.com/cylondata/cylon/blob/main/cpp/CMake/Modules/SetupCxxFlags.cmake>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/table.hpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/join/join_config.hpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/join/hash_join.cpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/join/join.cpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/groupby/hash_groupby.hpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/groupby/hash_groupby.cpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/arrow/arrow_partition_kernels.cpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/ctx/cylon_context.hpp>
  - <https://github.com/cylondata/cylon/blob/main/cpp/src/cylon/ctx/cylon_context.cpp>
  - <https://github.com/cylondata/cylon/blob/main/python/pycylon/pycylon/frame.py>
  - <https://github.com/cylondata/cylon/blob/main/conda/environments/cylon.yml>
  - <https://github.com/cylondata/cylon/blob/main/conda/environments/cylon_MacOS.yml>
  - <https://github.com/cylondata/cylon/blob/main/.github/workflows/c-cpp.yml>
  - <https://github.com/cylondata/cylon/pull/694>
  - <https://github.com/cylondata/cylon/issues>
  - <https://github.com/cylondata/cylon/issues/664>
  - <https://github.com/cylondata/cylon/issues/611>
  - <https://github.com/cylondata/cylon/issues/626>
  - <https://github.com/cylondata/cylon/issues/679>
  - <https://github.com/cylondata/cylon/actions>
  - <https://github.com/cylondata/cylon_experiments>
  - <https://cylondata.org/docs/>
  - <https://api.anaconda.org/package/cylondata/pycylon>
  - <https://arxiv.org/abs/2209.06146>
  - <https://arxiv.org/pdf/2209.06146>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cylondata/cylon`) · [data/wave6/enrich/raw/github_com_cylondata_cylon.json](../../../data/wave6/enrich/raw/github_com_cylondata_cylon.json) (enrichment confidence 0.8)

</details>
