# wrs (lorenzhs/wrs, parallel weighted random sampling and alias tables, ESA 2019)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Research C++17 library of sequential and parallel alias tables and weighted samplers; reported 3-4x faster queries than GSL's gsl_ran_discrete.

| | |
|---|---|
| **Beats** | GNU Scientific Library (GSL) alias table implementation |
| **Claimed result** | Not on an opened page; search-result summaries of the paper (arXiv 1903.00227 / LIPIcs ESA 2019, both blocked here) report alias-table queries roughly 3-4x faster than GSL 2.5's gsl_ran_discrete (one summary says about 4x at n=10^8, an earlier one more than 3x), attributed to an array-of-structs layout, branchless choice within buckets and a faster random number generator, and Vose-method construction 30% faster than GSL on the Intel machine and 44% faster on the AMD machine. Parallel construction and queries scale near-linearly up to 158 threads. |
| **Workload** | Weighted random sampling: alias table construction and queries, sequential and parallel, versus GSL; benchmark scripts for an Intel 80-core and an AMD 32-core machine. |
| **Metric** | throughput |
| **Hardware** | Intel machine with 80 cores and 160 threads, and AMD machine with 32 cores and 64 threads (models not named in README) |
| **Compiler and flags** | C++17, CMake 3.9.2+. CMakeLists.txt adds -march=native, -flto (WRS_USE_LTO on by default), -g, -pthread and warnings; the default build type is Debug unless CMAKE_BUILD_TYPE=Release is passed. Compiler, version and build type used for the paper's runs are not stated in the repo. |
| **Adoption** | 21 stars |
| **Last commit** | 2020-12-09 |
| **Links** | [repository](https://github.com/lorenzhs/wrs) · [benchmark](https://github.com/lorenzhs/wrs) |

## Verdict

Search-result summaries of the ESA 2019 paper (not opened; arXiv and Dagstuhl are blocked here) report sequential alias-table queries about 4x faster than GSL 2.5 gsl_ran_discrete at n = 10^8 (an earlier summary says more than 3x) and construction 30% faster on an Intel 80-core/160-thread machine and 44% faster on an AMD 32-core/64-thread machine; the GSL comparison is run single-threaded (benchmark/run_seq.sh passes -t 1) against an allocation-free copy of GSL's preprocessing in wrs/gsl.cpp. Compiler version, CPU models and build type for those runs are not stated in the repo.

## Use it when

- Millions to hundreds of millions of static weights sampled many times (Monte Carlo, graph generators, particle resampling) on Linux x86-64.
- You can build the table once and run queries from many threads: sample(u) is const and takes the random number as an argument.
- Table construction itself is the bottleneck and you have a many-core NUMA box: PSA and multi_alias build in parallel and the paper reports near-linear scaling.
- You need a batch of k samples with replacement and only want counts per item: outsens returns multiplicities instead of k individual draws.
- You are studying or reimplementing alias-table algorithms and want a reference with GSL wired in for comparison.

## Skip it when

- Closed-source or permissively licensed products: the code is GPL-3.0.
- Weights that change between draws: alias tables must be rebuilt in O(n); no dynamic or update API exists.
- Non-Linux or non-x86-64 targets: it calls madvise, links a prebuilt x86-64 ELF static library (extlib/stocc/libaelf64.a) and compiles with -march=native.
- Production use expecting maintenance: 8 commits, last one 2020-12-09, no releases, no issues filed, research-oriented logging and benchmark scaffolding throughout.
- Small tables or few queries: for a handful of weights std::discrete_distribution or a linear or binary search over a prefix sum is simpler and the setup cost (thread pool, submodules) dominates.

## How it is fast

The table is stored as an array of structs {double p; uint32 alias} so a query touches one cache line, where GSL keeps F[] and A[] in separate arrays; the query picks between bucket and alias with a branchless index (candidates[rand &gt;= p]) and reuses the fractional part of one uniform draw. Construction classifies small and large items into a single work array and pairs them in one sweep (Vose-style), and the parallel PSA variants split the item range with prefix sums so threads build disjoint table segments. Tables above 1 MB are allocated 2 MB-aligned with madvise(MADV_HUGEPAGE), and uniforms come from Intel MKL or dSFMT in blocks rather than one gsl_rng call per sample.

## Compared with alternatives

No other alias-table or weighted-sampling library is catalogued in this category; the siblings (SFMT, Randen, xoshiro and Philox SIMD generators, Ziggurat samplers) produce uniform or normal variates and can feed wrs's sample(u), so pick wrs for discrete weighted draws and pair it with whichever uniform generator wins for your platform. For GPU work, ByteHamster/alias-table-gpu (same group, CUDA, GPL-3.0) ports PSA to the GPU.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | tlx (author's fork, threadpool_init branch, git submodule), pthread, libatomic, Agner Fog's stocc with prebuilt asmlib libaelf64.a (vendored); optional Intel MKL (fast uniform generation), libnuma with hwloc and the Silo and Topo submodules (NUMA-aware pools), GSL (comparison only); googletest for tests |
| **Minimum toolchain** | C++17, CMake 3.9.2+ (GCC or Clang; MSVC branch exists in CMake but untested here) |
| **Platforms** | Linux x86-64 (madvise, prebuilt x86-64 asmlib, -march=native); NUMA optional |
| **Thread safety** | Queries on a constructed table are const and safe from many threads with per-thread RNGs; parallel construction uses a process-global tlx thread pool that must be created with wrs::init_threads(n) and torn down with wrs::release_threads(). The gsl_alias wrapper shares one gsl_rng and is not thread-safe. |
| **Drop-in for the baseline** | partial — same alias-method semantics as gsl_ran_discrete_preproc / gsl_ran_discrete, but a different C++ API (init/construct/sample(u)) and the caller supplies uniforms |

## Gotchas

- Default index type is uint32_t; a table with more than 2^32-1 items needs wrs::alias&lt;size_t&gt;, and construct() on a too-large or wrong-sized input only logs an error and returns, leaving the table unusable without throwing.
- CMake defaults to a Debug build; pass -DCMAKE_BUILD_TYPE=Release, and run git submodule update --init first.
- Benchmark fairness: benchmark/alias.cpp says the wrs tables must be switched to size_t indices for a fair GSL comparison, and the GSL query path draws from gsl_rng_mt19937 while wrs uses MKL or dSFMT block generation plus huge-page tables, so part of the reported query gain is the RNG and allocator, not the table layout.
- Move construction and move assignment are deleted on wrs::alias; copies deep-copy the table.

## Known shortcomings

- Tier B (ESA 2019 paper; benchmark/alias.cpp runs the GSL alias table beside wrs), but the GSL numbers (queries about 3-4x faster than GSL 2.5; Vose construction 30% faster on Intel, 44% on AMD) are known only from search summaries because drops.dagstuhl.de and publikationen.bibliothek.kit.edu were blocked. Build flags -march=native -flto with a default Debug build type. Paper-based retier to A still open.
- The GSL query comparison is not like for like: the GSL path draws gsl_rng_mt19937 per call while wrs uses MKL/dSFMT block uniforms plus 2 MB huge-page tables (madvise); benchmark/alias.cpp itself says to use size_t rather than the default uint32 index for a fair GSL comparison, and gsl_alias shares one gsl_rng so GSL ran single-threaded (run_seq.sh -t 1). Linux x86-64 only (prebuilt asmlib libaelf64.a, madvise, -march=native); CMake defaults to Debug. The 3-4x GSL numbers remain snippet-only.

## Caveats and trade-offs

Snippet only: the paper (arXiv 1903.00227; Dagstuhl LIPIcs ESA 2019; a journal version at dl.acm.org doi 10.1145/3549934 seen only as a search result) is EGRESS_BLOCKED here, so the GSL speedup figures are unverified search-result summaries and differ slightly between results (more than 3x vs about 4x for queries). Part of the query gain comes from a faster random-number generator (optional Intel MKL), not only the table layout. benchmark/alias.cpp notes that, for a fair GSL comparison, the other algorithms must be reconfigured to use size_t indices. The repo README itself states no numbers; CPU models are not named (Intel 80-core/160-thread and AMD 32-core/64-thread machines). Baseline is GSL rather than a C++ standard facility such as std::discrete_distribution. GPL-3.0. Last commit is the dissertation version, 2020-12-09; the ESA version is the esa tag.

GPLv3 copyleft. Implements sequential and parallel algorithms for sampling single items, k items with or without replacement and alias tables; needs C++17 and git submodules; optional MKL and NUMA dependencies.

## Maintenance

Abandoned research code (last commit 2020-12-09, dissertation version; ESA version under the esa tag), GPL-3.0, usable as a reference or vendored into GPL projects on Linux x86-64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ESA 2019 paper (LIPIcs vol. 144, 59:1-59:24, doi 10.4230/LIPIcs.ESA.2019.59, cited in the README) whose public benchmark code (benchmark/alias.cpp runs wrs::gsl_alias for construction and queries next to the wrs algorithms; benchmark/bench_intel.sh, bench_all_64.sh, run_seq.sh) compares against the GSL alias table; the GSL figures are known only from search-result summaries because the paper hosts are egress-blocked. Compiler version and CPU models are not in the repo, so not A.
- **Verifier notes:** Repo, GPL-3.0 license, 21 stars, 2 forks, 8 commits and last commit 2020-12-09 confirmed on github.com; abandoned is correct (&gt;3 years). drops.dagstuhl.de and publikationen.bibliothek.kit.edu were tried once each and are EGRESS_BLOCKED; a paper-based retier to A may be possible if the paper states compiler, flags and CPU models.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/lorenzhs/wrs>
  - <https://github.com/lorenzhs/wrs/commits>
  - <https://github.com/lorenzhs/wrs/tree/master/benchmark>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/README.md>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/benchmark/alias.cpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/benchmark/run_seq.sh>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/lorenzhs/wrs>
  - <https://github.com/lorenzhs/wrs/tree/master/wrs>
  - <https://github.com/lorenzhs/wrs/tree/master/wrs/generators>
  - <https://github.com/lorenzhs/wrs/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/README.md>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/benchmark/alias.cpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/benchmark/bench_intel.sh>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/benchmark/run_seq.sh>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/alias.hpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/gsl.hpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/gsl.cpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/multi_alias.hpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/par_scan_alias2.hpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/parallel_do.hpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/parallel_do.cpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/outsens.hpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/memory.hpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/memory.cpp>
  - <https://raw.githubusercontent.com/lorenzhs/wrs/HEAD/wrs/generators/select.hpp>
  - <https://github.com/ByteHamster/alias-table-gpu>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lorenzhs/wrs`) · [data/wave8/enrich/raw/github_com_lorenzhs_wrs.json](../../../data/wave8/enrich/raw/github_com_lorenzhs_wrs.json) (enrichment confidence 0.6)

</details>
