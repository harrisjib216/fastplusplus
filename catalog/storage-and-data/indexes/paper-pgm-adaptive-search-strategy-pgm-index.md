# PGM++ (adaptive search-strategy PGM-index)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Research patch to PGM-index static lookups: hybrid branchless/linear segment search plus cost-model epsilon tuning, up to 2.31x faster.

| | |
|---|---|
| **Beats** | PGM-index |
| **Claimed result** | Up to 2.31x faster lookups than the original PGM-Index and up to 1.56x faster than state-of-the-art learned indexes (CDFShop-optimized RMI) at comparable space cost (abstract). In the paper body, PGM++ beats PGM by 1.2x-2.2x at the same index size on Uniform query workloads, and RMI still beats PGM++ on the synthetic normal dataset. |
| **Workload** | Lookup queries on 4 SOSD real datasets (fb and wiki at 200M uint64 keys; books and osm at 800M) plus 3 synthetic ones (uniform, normal, lognormal). PGM++ (a mixture of internal search strategies with epsilon tuned by a cost model) is compared with the original PGM-Index and CDFShop-optimized RMI at comparable index size on three platforms. B+-tree and other non-learned baselines are deliberately excluded. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-13700K (Ubuntu 20.04, 32/64 GB DDR4); 2x AMD EPYC 7413 (CentOS 9.4, 1 TB DDR4); Apple M3 MacBook Air (macOS 14.4.1, 16 GB) |
| **Compiler and flags** | g++ 11.4 on the two x86 platforms and clang++ 15 on ARM (per paper); optimization flags are not stated in the paper. The artifact's documented builds pass no -O flag: README 'g++ main.cpp -std=c++17 -I. -o main -fopenmp' and exp_rmi/Makefile_all. |
| **Adoption** | Artifact repo qyliu-hkust/bench_search: 6 stars; paper in PVLDB 18(9):2886-2898 (2025), doi:10.14778/3746405.3746415 |
| **Last commit** | 2025-02-01 |
| **Links** | [repository](https://github.com/qyliu-hkust/bench_search) · [benchmark](https://www.vldb.org/pvldb/vol18/p2886-liu.pdf) |

## Verdict

The PVLDB 2025 paper reports up to 2.31x faster lookups than the original PGM-Index and up to 1.56x faster than CDFShop-tuned RMI at comparable index size. It tested 4 SOSD datasets (fb and wiki at 200M uint64 keys, books and osm at 800M) plus 3 synthetic sets, on an i7-13700K and 2x EPYC 7413 with g++ 11.4 and on an Apple M3 with clang++ 15; the body gives 1.2x-2.2x over PGM at equal eps_l. There is no stdlib or B+-tree baseline in the static comparison, and optimization flags are unstated. The public harness times 5,000 lookups per round, each wrapped in its own high_resolution_clock pair, and its documented build has no -O flag, while the paper's text says 100M lookups.

## Use it when

- You already use the static pgm::PGMIndex on sorted 64-bit integer keys and profiling shows the internal segment search dominates. Porting the \~20-line branchless bound from exp_pgm/search_algo.h is the cheap change behind the paper's 1.2x-2.2x at equal eps_l.
- Read-only lookups over large in-memory sorted arrays (200M-800M uint64 keys in the paper) where you want a learned index with a guaranteed maximum error instead of RMI's data-dependent error (the paper measured RMI max error up to 1.77M positions on osm).
- Tight index-memory budgets: the paper reports a 0.1 MB PGM++ beating a 100+ MB CDFShop-tuned RMI on the wiki dataset.
- Reproducing or extending the study. exp_pgm/main.cpp sweeps the full eps_l x eps_i grid over {4..1024}, and exp_rmi/ holds the pre-generated CDFShop RMI models for all 7 datasets.
- Hosts with relatively low memory latency. On osm the average gain over PGM was 1.78x on the i7-13700K and Apple M3 but only 1.32x on the EPYC 7413 server.

## Skip it when

- As a production dependency. This is a benchmark harness with no LICENSE for the PGM++-specific files, no tests, no build system beyond a one-line g++ command, and no code changes since 2024-10-02.
- Updatable workloads. The repo contains only the static PGMIndex; the paper's DPGM++ is not published there, and even in the paper ALEX has the highest throughput on every mix except write-heavy (80%) and write-only.
- Keys that follow smooth normal or lognormal distributions: in the paper, CDFShop-tuned RMI (with cubic-spline models) beats both PGM and PGM++ there.
- Code that probes keys larger than the maximum indexed key, or that relies on getting end(): the branchless helpers never return the end iterator (see gotchas).
- If you need upstream's other structures (DynamicPGMIndex, compressed/bucketing/Elias-Fano variants, multidimensional). Only pgm_index.h and piecewise_linear_model.h are vendored.

## How it is fast

The paper finds PGM lookups are memory-bound and dominated by the internal error-bounded searches, which take 69-81% of lookup time in its Table 7. Upstream does these with std::upper_bound once eps_i is above a small threshold. PGM++ replaces them with a CMOV-style branchless binary search (base = base[half-1] &lt; k ? base + half : base), falls back to a linear scan for tiny ranges, and uses the branchless search for the last-mile step too; per the Table 9 ablation, removing this makes lookups 39-60% slower. The paper adds two more pieces: 'layer bypassing', which starts the descent at the first level whose child level is dense (12-22% in the same ablation), and a calibrated cost model that estimates leaf-segment count from gap mean/variance via kernel change-point detection on a 0.05% sample and then picks the eps_i with the lowest modeled lookup cost.

## Compared with alternatives

Pick it over the PGM-index sibling only when you want PGM's guaranteed error bound with faster static lookups and are willing to vendor unlicensed research code, or just port its branchless search. CHT (which reports 1.7-2.5x over PGM), RadixSpline and RMI are different static designs, RMI still wins on normal/lognormal keys, and ALEX or LIPP are the choice when you need inserts.

## Integration

| | |
|---|---|
| **Form** | source-drop (loose headers in exp_pgm/: pgm_index.h, piecewise_linear_model.h, search_algo.h; no packaging) |
| **Dependencies** | none beyond the C++ standard library; OpenMP is optional (with -fopenmp construction runs in parallel on up to 20 threads; without it a #pragma message is emitted and construction is single-threaded) |
| **Minimum toolchain** | C++17 (README builds with g++ -std=c++17; the paper used g++ 11.4 and clang++ 15) |
| **Platforms** | x86-64 and aarch64 as tested in the paper (i7-13700K, EPYC 7413, Apple M3); no intrinsics are required (the __builtin_prefetch path is compiled out by default); Windows not documented |
| **Thread safety** | not documented; lookups do not mutate the index, but search_data() is declared non-const, so it cannot be called on a const PGMIndex |
| **Drop-in for the baseline** | partial: same search()/ApproxPos semantics as upstream PGMIndex, but the template parameter list changes and only the static index is included |

## Gotchas

- search::lower_bound_branchless and upper_bound_branchless never return end. When every element in the range is below (or not above) the key, they return the last element instead. I checked a Python port of the exact loops against bisect on 20k random cases, and every mismatch was this end case. The benchmark only queries existing keys, so this path is never exercised.
- Build flags: the README command and exp_rmi/Makefile_all pass no -O flag, so the documented builds compile both PGM and PGM++ at -O0, and the paper does not state flags. Re-measure at -O2/-O3 before trusting the ratios.
- The artifact's 'original PGM' baseline is PGMIndex&lt;..., false, 0, float&gt;. linear_search_threshold=0 forces std::upper_bound on every internal level, whereas upstream master linear-scans when EpsilonRecursive &lt;= 8\*64/sizeof(Segment) = 32. For eps_i of 4-32 the in-repo baseline is therefore not upstream's code path.
- The code covers only part of what the paper's ablation credits. Layer bypassing is commented out in segment_for_key (start_level is computed but unused), the last-mile search has no linear-scan branch, and the KCPD/cost-model tuner is absent.

## Known shortcomings

- Code exists at qyliu-hkust/bench_search but has no LICENSE (usability mixed) and is stale since 2025-02; the documented builds pass no -O flag, so published numbers may be -O0; paper in PVLDB 18(9) 2025.
- The in-repo 'PGM' baseline sets linear_search_threshold=0 (always std::upper_bound) whereas upstream PGM linear-scans at eps &lt;= 32, so the baseline is not upstream's code path. The code implements only part of the paper (layer bypassing commented out; no cost-model tuner, DPGM++ or last-mile linear scan). Branchless lower/upper_bound never return end (keys above the max get the last element; untested because queries use existing keys). The harness times 5k lookups per round individually while the paper says 100M; RMI still wins on normal/lognormal; code stale since 2024-10.

## Caveats and trade-offs

Research artifact, not a library: the code is at github.com/qyliu-hkust/bench_search (exp_pgm/), which is linked from the paper's PVLDB Artifact Availability box, so the record's 'no code released' is wrong. The repo has no LICENSE. Its vendored PGM-index headers keep their Apache-2.0 notices, but the PGM++-specific files (search_algo.h, main.cpp, utils.h) are unlicensed. Optimization flags are unstated, and the documented build commands use the -O0 default for both PGM and PGM++. There is no B+-tree or std baseline, only learned indexes. The paper is by Qiyu Liu et al. (Southwest University / HKUST), not the PGM-index authors. gvinciguerra/Learned-indexes-effectiveness belongs to a different, earlier paper (Ferragina, Lillis, Vinciguerra, ICML 2020).

Requires a calibrated cost model to pick a search-strategy mixture per dataset, adding tuning complexity over PGM's plain binary/linear search.

## Maintenance

Stale, low-adoption research artifact: 6 stars, code last touched 2024-10-02 (README 2025-02-01), no LICENSE for the PGM++ files (the vendored PGM headers keep Apache-2.0), and upstream PGM-index issue #58, which proposed upstreaming it, has had no reply since 2024-10-20.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** This is a peer-reviewed paper (PVLDB 18(9):2886-2898, 2025) whose public artifact is github.com/qyliu-hkust/bench_search (exp_pgm/main.cpp). It shows up to 2.31x over the original PGM-Index, and the CPUs and compilers are stated (i7-13700K and EPYC 7413 with g++ 11.4; Apple M3 with clang++ 15), so it would ordinarily be B. It is capped at C because the paper states no optimization flags, and the artifact's only documented builds pass no -O flag: the README's 'g++ main.cpp -std=c++17 -I. -o main -fopenmp' and exp_rmi/Makefile_all. That means both the PGM baseline and PGM++ are built at the -O0 default.
- **Verifier notes:** Please update fields outside the allowed correction set by hand: repo_url should be https://github.com/qyliu-hkust/bench_search, and language should be 'C++'. The abstract numbers are verbatim. The tier stays C only because of the -O0 build concern. If the authors confirm optimized builds, this becomes B (peer-reviewed PVLDB).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `usability`, `last_commit`, `maintenance_status`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2410.00846>
  - <https://arxiv.org/pdf/2410.00846>
  - <https://www.vldb.org/pvldb/vol18/p2886-liu.pdf>
  - <https://api.crossref.org/works/10.14778/3746405.3746415>
  - <https://github.com/qyliu-hkust/bench_search>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/README.md>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/main.cpp>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/pgm_index.h>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/search_algo.h>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_rmi/Makefile_all>
- **Sources the enricher read:**
  - <https://github.com/qyliu-hkust/bench_search>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/README.md>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/main.cpp>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/pgm_index.h>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/piecewise_linear_model.h>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/search_algo.h>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_pgm/utils.h>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/exp_rmi/Makefile_all>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/data/gen_data.sh>
  - <https://github.com/qyliu-hkust/bench_search/blob/main/data/gen_normal.py>
  - <https://github.com/qyliu-hkust/bench_search/commits/main>
  - <https://www.vldb.org/pvldb/vol18/p2886-liu.pdf>
  - <https://arxiv.org/abs/2410.00846>
  - <https://github.com/gvinciguerra/PGM-index>
  - <https://github.com/gvinciguerra/PGM-index/tree/master/include/pgm>
  - <https://raw.githubusercontent.com/gvinciguerra/PGM-index/master/include/pgm/pgm_index.hpp>
  - <https://raw.githubusercontent.com/gvinciguerra/PGM-index/master/include/pgm/piecewise_linear_model.hpp>
  - <https://github.com/gvinciguerra/PGM-index/issues/58>
  - <https://hn.algolia.com/api/v1/search?query=PGM%2B%2B&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=%22Why%20Are%20Learned%20Indexes%20So%20Effective%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:pgm-adaptive-search-strategy-pgm-index`) · [data/wave6/enrich/raw/paper_pgm_adaptive_search_strategy_pgm_index.json](../../../data/wave6/enrich/raw/paper_pgm_adaptive_search_strategy_pgm_index.json) (enrichment confidence 0.8)

</details>
