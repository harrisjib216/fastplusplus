# Crystal (GPU query-processing library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only CUDA library of block-wide device functions for hand-writing fused SQL query kernels; about 16x faster than OmniSci on SSB.

| | |
|---|---|
| **Beats** | OmniSci (commercial GPU OLAP DBMS, formerly MapD, now HEAVY.AI) on the same GPU. Also the authors' own equivalent CPU implementation, which is itself compared against Hyper and MonetDB. |
| **Claimed result** | Per the SIGMOD 2020 paper (Section 5.2): the Crystal-based Standalone GPU implementation is on average about 16x faster than OmniSci (a commercial GPU OLAP DBMS) on the same V100, and on average 25x faster than the authors' own equivalent CPU implementation across the 13 SSB queries. The 1.17x (vs Hyper) and 2.5x (vs MonetDB) averages belong to the authors' Standalone CPU implementation, not to Crystal on the GPU. The paper does not state direct GPU-vs-Hyper or GPU-vs-MonetDB ratios. |
| **Workload** | 13 Star Schema Benchmark queries at scale factor 20 (120M-row lineorder fact table, about 13 GB). String columns are dictionary-encoded to 4-byte integers and the queries are manually rewritten. Data is preloaded into device memory, and each result is the average of 3 runs. Crystal on the GPU (thread block 256, 8 items per thread per tile) is compared with OmniSci on the GPU and with an equivalent CPU implementation; Hyper and MonetDB are compared only with that CPU implementation. |
| **Metric** | throughput |
| **Hardware** | CPU: single-socket Intel i7-6900 (the paper calls it Skylake-class; 8 cores/16 SMT, AVX2, 64 GB). GPU: Nvidia V100 (32 GB, 880 GB/s; measured bidirectional PCIe 12.8 GB/s). Ubuntu 16.04, CUDA 10.0. |
| **Compiler and flags** | GPU: nvcc (CUDA 10.0). The repo Makefile compiles with -O3 --std=c++11 -Xptxas="-dlcm=cg" and defaults to gencode sm_52 (the sm_70 lines are commented out). CPU-implementation compiler and flags are not stated. |
| **Adoption** | 91 stars |
| **Last commit** | 2020-08-29 |
| **Links** | [repository](https://github.com/anilshanbhag/crystal) · [benchmark](http://anilshanbhag.in/static/papers/crystal_sigmod20.pdf) |

## Verdict

The SIGMOD 2020 paper (Section 5.2, Figure 14) ran the 13 SSB queries at SF20: a 120M-row lineorder table of about 13 GB, dictionary-encoded to 4-byte ints, with queries hand-rewritten and data preloaded into device memory, averaged over 3 runs. The Crystal-based GPU kernels averaged about 16x faster than OmniSci on the same V100 (32 GB, 880 GB/s, CUDA 10.0). They also averaged about 25x faster than the authors' own CPU implementation on an 8-core i7-6900 with 53 GB/s memory bandwidth (compiler and flags not stated); in the q2.1 case study this was 3.86 ms vs 125 ms. The 1.17x (vs Hyper) and 2.5x (vs MonetDB) figures belong to that CPU implementation, not to Crystal. On AWS pricing (p3.2xlarge at \$3.06/h vs r5.2xlarge at \$0.504/h), the paper concludes the GPU is about 4x more cost-effective, provided the dataset fits in GPU memory.

## Use it when

- You have an Nvidia GPU and a fixed set of star-schema analytic queries (SSB-like: filter the fact table, join 1-4 small dimensions, aggregate) that you are willing to hand-code as one CUDA kernel each.
- All columns are, or can be dictionary-encoded to, 4-byte integers, and the working set fits in device memory. The paper's SF20 run was about 13 GB on a 32 GB V100.
- Dimension join keys are dense surrogate integers (for example 1..N part/supplier keys or yyyymmdd date keys), so a direct-mapped array can act as the hash table.
- You are doing GPU database research or teaching and want a small, readable reference: the SSB kernels are the baseline many GPU-DB papers cite.
- Data is loaded once and many queries run over it. The paper measures PCIe at 12.8 GB/s, versus 880 GB/s of HBM bandwidth, so repeated transfers would erase the gain.

## Skip it when

- You need ad-hoc SQL, strings, NULLs, 64-bit or decimal columns, or general GROUP BY. The library only offers integer comparison predicates, perfect-hash joins and a sum reduction. Each SSB kernel hard-codes its group-by as a fixed arithmetic index into a result array.
- The data does not fit in GPU memory or lives on the host. There is no out-of-core, multi-GPU or transfer pipelining, and the paper's own analysis shows GPU-as-coprocessor loses to a good CPU engine once PCIe is involved.
- Join keys are sparse, skewed or duplicated. Build ignores the atomicCAS result and does no collision handling, so colliding keys are silently dropped and 0 is reserved as the empty-slot marker.
- You want the full API described in the paper. BlockLoadSel, BlockScan, BlockShuffle, BlockLookup and BlockAggregate (paper Table 1) are not in the repo (open issue #8), so selection with compacted output (the paper's Q0) cannot be built from the published headers.
- You need a maintained dependency. The last commit was Aug 2020. The build pins CUB 1.6.4, targets sm_52 by default, and uses 32-bit int row counts. Two 2024 PRs that fix include paths for CCCL-era CUDA are still unmerged.

## How it is fast

It uses the paper's 'tile-based execution model'. The unit of work is the thread block, not the thread. Each block loads a tile of BLOCK_THREADS x ITEMS_PER_THREAD values with coalesced, striped loads into registers and tracks selections as per-item flags. A whole query (filters, then a probe of every dimension hash table, then aggregation) is fused into one kernel, so intermediate results never go to global memory. Aggregates are reduced in two steps, first with warp shuffles (__shfl_down_sync) and then through shared memory, which leaves one global atomicAdd per block; in the paper's selection microbenchmark this cut runtime from 19 ms to 2.1 ms. Joins use 'perfect hash' tables: direct-mapped arrays indexed by (key - min) % len over dense integer keys, so a probe is a single random read and the small dimension tables stay in GPU L2. The paper credits the larger-than-bandwidth-ratio gain over CPU to GPU warp switching hiding latency on irregular join probes. The Makefile also builds with -Xptxas -dlcm=cg, which caches global loads in L2 only.

## Compared with alternatives

Sirius (benchmarked against DuckDB at SF100-SF1000) and cuDF (cudf.pandas, a pandas accelerator) are engines you point at data. Crystal is a kit for hand-writing fused GPU kernels, so pick it only when you control the exact queries and want minimal, inspectable primitives, for example for research or a fixed dashboard query set. Compared with Velox, StarRocks or Umbra, it makes sense only when the data fits in GPU memory and integer-only columns are acceptable.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | The crystal/\*.cuh headers need only the CUDA toolkit (nvcc). The bundled SSB and ops programs also need CUB 1.6.4, fetched by `make setup` for CachingDeviceAllocator and test_util.h, plus cuRAND. SSB data generation needs the bundled dbgen/loader (C) and Python. |
| **Minimum toolchain** | Not stated. __shfl_down_sync implies CUDA 9+, and the code uses --std=c++11. The paper used CUDA 10.0, and issue #1 reports a working build on CUDA 10.2 with GCC 7.5 after a template fix. On newer CUDA with bundled CCCL, the cub/test include paths need editing (PRs #10, #11). |
| **Platforms** | Nvidia GPUs only (CUDA). The Makefile defaults to sm_52, with the sm_70/V100 lines commented out. Linux: the paper used Ubuntu 16.04, and the scripts assume a POSIX shell. |
| **Thread safety** | Not documented. Every thread of a block must call the functions uniformly: BlockSum uses __syncthreads, a caller-supplied 32-slot shared buffer and warp shuffles over full warps. The PHT_2 build sets the key with atomicCAS but writes the payload non-atomically. |
| **Drop-in for the baseline** | false. OmniSci/HEAVY.AI is a full SQL DBMS, while Crystal requires writing and compiling a CUDA kernel for each query, with manual dictionary encoding and query rewriting. |

## Gotchas

- The repo's SSB kernels launch with 128 threads x 4 items per thread, but paper Section 5.2 says the SSB runs used 256 threads x 8 items. The Makefile also targets sm_52, not the V100's sm_70. To reproduce Figure 14, both need editing.
- src/ssb/ssb_utils.h hard-codes SF 1 and BASE_PATH /home/ubuntu/dbops/..., and loadColumn returns NULL silently when a file is missing. A wrong path therefore shows up as 'CUDA error 11 invalid argument' at cudaMemcpy (issue #3).
- The bundled SSB dbgen segfaults on some systems (issue #4). The reported workaround is raising MAXAGG_LEN or using eyalroz/ssb-dbgen instead.
- The published BlockLoad is a plain striped load loop that keeps the tile in registers. The paper's vectorized full-tile loads and shared-memory staging are not in the headers, so performance on other GPUs depends on the tile-size template parameters you choose.

## Known shortcomings

- The 2.5x/1.17x vs MonetDB/Hyper is the authors' CPU code, not the GPU library; the GPU result is about 16x vs OmniSci on the same V100 and 25x vs their own CPU code. Abandoned (last commit 2020-08).
- The repo's SSB kernels run 128 threads x 4 items while the paper used 256 x 8, and the Makefile targets sm_52 (V100 is sm_70), so paper numbers are not reproducible as shipped. Hash-join tables have no collision handling (colliding keys silently dropped, key 0 reserved): dense unique integer keys only.
- The paper's BlockScan/BlockShuffle/BlockLoadSel/BlockLookup and the CPU implementation are missing from the repo (issues #8, #12). Pinned to CUB 1.6.4 with a hard-coded BASE_PATH; newer-CUDA include fixes unmerged (PRs #10, #11); no live fork.

## Caveats and trade-offs

The headline GPU speedups are largely cross-hardware: a V100 against an 8-core desktop CPU, a memory-bandwidth ratio of about 16x. The paper is a GPU-vs-CPU study; the like-for-like incumbent comparison is Crystal vs OmniSci on the same GPU (about 16x). Hyper and MonetDB were compared only against the authors' CPU implementation. The CPU implementation and the baseline-system runs are not in the repo. The \~13 GB SF20 dataset fits in GPU memory. Published at SIGMOD 2020, so it predates DuckDB/ClickHouse-era baselines. The last commit on master (the only branch) is 2020-08-29; the 2024-06-03 date is GitHub's pushed_at, not a commit. It is an academic reference library.

Requires an Nvidia GPU and CUDA toolchain; provides block-wide device-function building blocks and SSB query implementations rather than a full SQL engine; the paper's own cost analysis weighs the \~\$3/hr V100 rental cost against the speedup rather than declaring an unconditional win.

## Maintenance

Abandoned: the last commit on master was 2020-08-29 (13 commits in total), with 8 open issues, unmerged 2024 CUB/CCCL build-fix PRs and no active fork (every fork found has 0 stars). It is MIT-licensed, though, and the core is about five small .cuh headers that are easy to vendor; the last toolchain reported to work is CUDA 10.x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SIGMOD 2020 paper (Section 5.2, Figure 14) shows the Crystal GPU implementation beating OmniSci, a commercial GPU OLAP DBMS, by about 16x on average on SSB on the same V100. It stays below A because the repo (src/ssb/\*.cu plus Makefile) holds only the GPU queries: the CPU implementation and the OmniSci/Hyper/MonetDB runs are not scripted, and the CPU build flags are unstated.
- **Verifier notes:** The record's claimed_speedup misreads the paper: 2.5x and 1.17x are the authors' CPU code vs MonetDB/Hyper, and '&gt;5x' refers to Peloton being slower. The real Crystal numbers are larger (about 16x vs OmniSci, 25x vs CPU). The tier stays B. last_commit/maintenance are fixed from 2024 'stale' to 2020 'abandoned'.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `hardware`, `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <http://anilshanbhag.in/static/papers/crystal_sigmod20.pdf>
  - <https://github.com/anilshanbhag/crystal>
  - <https://github.com/anilshanbhag/crystal/blob/master/Makefile>
  - <https://github.com/anilshanbhag/crystal/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/anilshanbhag/crystal>
  - <https://github.com/anilshanbhag/crystal/blob/master/README.md>
  - <https://github.com/anilshanbhag/crystal/blob/master/Makefile>
  - <https://github.com/anilshanbhag/crystal/blob/master/crystal/crystal.cuh>
  - <https://github.com/anilshanbhag/crystal/blob/master/crystal/join.cuh>
  - <https://github.com/anilshanbhag/crystal/blob/master/crystal/load.cuh>
  - <https://github.com/anilshanbhag/crystal/blob/master/crystal/pred.cuh>
  - <https://github.com/anilshanbhag/crystal/blob/master/crystal/reduce.cuh>
  - <https://github.com/anilshanbhag/crystal/blob/master/crystal/store.cuh>
  - <https://github.com/anilshanbhag/crystal/blob/master/src/ssb/q11.cu>
  - <https://github.com/anilshanbhag/crystal/blob/master/src/ssb/q12.cu>
  - <https://github.com/anilshanbhag/crystal/blob/master/src/ssb/q21.cu>
  - <https://github.com/anilshanbhag/crystal/tree/master/src/ssb>
  - <https://github.com/anilshanbhag/crystal/blob/master/src/ssb/ssb_utils.h>
  - <https://github.com/anilshanbhag/crystal/blob/master/src/ssb/gpu_utils.h>
  - <https://github.com/anilshanbhag/crystal/blob/master/src/ops/join.cu>
  - <https://github.com/anilshanbhag/crystal/blob/master/src/ops/project.cu>
  - <https://github.com/anilshanbhag/crystal/blob/master/test/util.py>
  - <https://github.com/anilshanbhag/crystal/blob/master/test/ssb/SSB.md>
  - <https://github.com/anilshanbhag/crystal/blob/master/test/ssb/loader/convert.py>
  - <https://github.com/anilshanbhag/crystal/commits/master>
  - <https://github.com/anilshanbhag/crystal/issues/1>
  - <https://github.com/anilshanbhag/crystal/issues/3>
  - <https://github.com/anilshanbhag/crystal/issues/4>
  - <https://github.com/anilshanbhag/crystal/issues/7>
  - <https://github.com/anilshanbhag/crystal/issues/8>
  - <https://github.com/anilshanbhag/crystal/issues/12>
  - <https://github.com/anilshanbhag/crystal/pull/2>
  - <https://github.com/anilshanbhag/crystal/pull/10>
  - <https://github.com/anilshanbhag/crystal/pull/11>
  - <https://github.com/anilshanbhag/crystal/pull/13>
  - <https://github.com/anilshanbhag/crystal/forks>
  - <http://anilshanbhag.in/static/papers/crystal_sigmod20.pdf>
  - <https://github.com/NVlabs/cub/archive/1.6.4.zip>
  - <https://hn.algolia.com/api/v1/search?query=crystal%20gpu%20shanbhag&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=%22Fundamental%20Performance%20Characteristics%20of%20GPUs%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/anilshanbhag/crystal`) · [data/wave6/enrich/raw/github_com_anilshanbhag_crystal.json](../../../data/wave6/enrich/raw/github_com_anilshanbhag_crystal.json) (enrichment confidence 0.8)

</details>
