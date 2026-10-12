# LPHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Minimal perfect hash functions](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Locality-preserving MPHF for DNA k-mer sets: 0.53-0.87 bits/k-mer at k=63, versus 3.06-3.71 for BBHash and 2.04-2.76 for PTHash.

| | |
|---|---|
| **Beats** | BBHash (also PTHash) |
| **Claimed result** | Paper Table 3: partitioned LPHash at k=63 uses 0.53, 0.64, 0.83, 0.58 and 0.87 bits/k-mer on Yeast, Elegans, Cod, Kestrel and Human. BBHash-v1 uses 3.71 bits/k-mer, BBHash-v2 3.06, PTHash-v1 2.58-2.76 and PTHash-v2 2.04-2.20. The paper states LPHash is 5.1x, 4.1x, 3.2x, 4.4x and 3x smaller than PTHash-v1 and 2.3-3.7x smaller than PTHash-v2. Against BBHash-v2 it is about 3.5-5.8x smaller (derived from page data). At k=31, LPHash uses 1.18-1.74 bits/k-mer. For streaming queries the paper says: 'Compared to BBHash, LPHash is 2x faster on Yeast and up to 4-5x faster on the larger datasets.' The README's claim of '&lt; 0.9 bits/k-mer vs 1.44 lower bound and 2-3 bits/k-mer for practical constructions' matches these tables. |
| **Workload** | An MPHF over the distinct k-mers of 5 whole-genome datasets, from Yeast (11.6M k-mers) to Human (2.77G k-mers), given as spectrum-preserving string sets (BCALM2 + UST stitched unitigs), for k=31..63. Space is measured in bits/k-mer. Queries are about 100M k-mers from human chr13, measured in streaming and random order on a single core. |
| **Metric** | memory |
| **Hardware** | Intel i9-9900K @ 3.60 GHz, 64 GB RAM, Linux 5.13.0. Queries ran on 1 core. Builds used 4 threads. |
| **Compiler and flags** | gcc 11.2.0, -O3 -march=native (paper). The repo CMakeLists.txt also adds -std=c++17 -mbmi2 -msse4.2. |
| **Adoption** | 44 stars |
| **Last commit** | 2023-07-19 |
| **Links** | [repository](https://github.com/jermp/lphash) · [benchmark](https://academic.oup.com/bioinformatics/article/39/Supplement_1/i534/7210438) |

## Verdict

In the Bioinformatics 2023 paper, five whole-genome SPSS k-mer sets were tested (Yeast 11.6M to Human 2.77G k-mers). At k=63, partitioned LPHash took 0.53-0.87 bits/k-mer, against 3.06-3.71 for BBHash (gamma 1 and 2) and 2.04-2.76 for PTHash, and streaming queries over about 100M Human chr13 k-mers on one core took 22-53 ns/k-mer, against 42-190 ns for BBHash. All code was compiled with gcc 11.2.0 -O3 -march=native and run on an Intel i9-9900K with 64 GB RAM. No C++ standard library container was part of the comparison.

## Use it when

- You need an MPHF, or a k-mer-to-slot index for counts, colors or unitig IDs, over the distinct k-mers of a genome or de Bruijn graph, and memory is the limit. At k=47-63 the paper measured 0.53-1.14 bits/k-mer, below the 1.44 bits/key lower bound for general MPHFs.
- Lookups arrive as consecutive k-mers from reads or sequences (streaming). At k=63 the paper measured 22-53 ns/k-mer on one core, against 24-72 ns for PTHash-v1 and 42-190 ns for BBHash.
- You want satellite values to compress well. Consecutive k-mers get consecutive codes, so a value array indexed by the code forms runs of similar values.
- Sets of millions to a few billion k-mers (11.6M-2.77G tested) on Linux or macOS. The build can spill to disk through --max-memory and -d.
- Your pipeline already produces SPSS input (BCALM2 + UST or a similar tool), so the preprocessing costs you nothing extra.

## Skip it when

- The keys are not k-mers from a spectrum-preserving string set. LPHash cannot hash arbitrary keys, and the paper itself calls BBHash and PTHash the general-purpose options.
- Most lookups are in random order. LPHash random lookups measured 110-188 ns/k-mer, against 24-72 ns for PTHash-v1.
- k is around 31 and lookups are streaming. At k=31, LPHash streaming was slower than PTHash-v1 on 4 of 5 datasets (for example 107 vs 72 ns on Human), and space was 1.18-1.74 bits/k-mer. The maintainer says k &lt; 31 was never tested.
- You need canonical k-mers, where a k-mer and its reverse complement get the same code. LPHash treats them as different keys (issue #22), and BCALM2/UST output contains only one orientation of each k-mer, so reads from the other strand get arbitrary codes.
- You need a maintained library with a stable API, or Windows/MSVC support. There has been no main-branch commit since July 2023, there is no library target, and the code depends on __uint128_t and GCC/Clang flags.

## How it is fast

Each k-mer is keyed by its random minimizer. A run of consecutive k-mers that share a minimizer (a super-k-mer) is stored once, and a k-mer's code is the super-k-mer's prefix-sum offset plus a local rank computed from where the minimizer sits inside the k-mer. As a result, the stored parts are only a PTHash MPHF over the distinct minimizers (about 2/(w+1) of the k-mers, with w = k-m+1) and the offsets and positions, coded with Elias-Fano. The partitioned variant labels each super-k-mer as left-right-max, left-max, right-max or non-max in a 2-bit wavelet tree with Rank9, and skips the offsets or positions that each label already implies. Ambiguous minimizers (1-4% in the paper's datasets) go to a fallback PTHash over their k-mers. In streaming queries the minimizer usually stays the same from one k-mer to the next, so the next code is the previous code plus or minus 1, with no hash-table lookup.

## Compared with alternatives

Pick LPHash over PTHash, SicHash, ShockHash or ConsensusRecSplit only when the keys are DNA k-mers from a spectrum-preserving string set and k is about 47 or more. In that case it goes below the \~1.44 bits/key floor that general MPHFs approach (for example ShockHash at about 1.56 bits/key), and it beats PTHash on streaming lookups. For arbitrary keys, random-order lookups, or k near 31 (1.18-1.74 bits/k-mer), PTHash (which LPHash uses internally) or the RecSplit family is the better choice.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | PTHash (git submodule, which brings its essentials and cmd_line_parser headers) and zlib; kseq.h is vendored. BBHash (external/BooPHF.hpp) is vendored only for the benchmark tools. |
| **Minimum toolchain** | C++17 and CMake 3.5+, with GCC or Clang (__uint128_t required). The paper used GCC 11.2.0. With Clang, CMake adds -stdlib=libc++. |
| **Platforms** | The README says it is tested on Linux with GCC and on macOS with Clang, on Intel and ARM (Apple M1). On x86-64, CMake forces -march=native -mbmi2 -msse4.2, so binaries need BMI2 and POPCNT and may not run on other CPUs (issue #21: 'Illegal instruction' on a Xeon E5-2470). Windows is not documented. |
| **Thread safety** | Not documented. The build uses PTHash's multithreaded search (-t); one user with -t 64 got 'parallel search should use at most 36 threads', and the maintainer says contention can make more threads slower. The query methods are const and allocate their buffers per call, but the CLI queries on one thread only (issue #19 asks for more). |
| **Drop-in for the baseline** | no |

## Gotchas

- The k-mer width is a compile-time typedef in include/compile_constants.tpd (default __uint128_t, k &lt;= 63). In issue #21, a k=25 build with the default type aborted with PTHash's 'seed did not work', and switching to uint64_t fixed it. The fallback hasher gives different results for the two typedefs, so query with a binary built with the same typedef as the one that built the .lph file.
- The query tool crashes on any sequence shorter than k (reported in issue #21 and acknowledged). The random-lookup loop is still unguarded on both main and dev. Non-ACGT bases are not supported: streaming mode skips k-mers that contain them, but random mode does not, so the two modes can return different counts.
- Construction uses external memory: --max-memory defaults to 8 GB, and temp files go to -d (default: current directory). A 955M-k-mer fallback build in issue #21 logged a peak of 28 GB of disk. With 4 threads, the build is slower than BBHash-v1 (Cod 05:30 vs 00:48, Human 07:25 vs 04:13) but faster than PTHash on the three largest sets.
- Like any MPHF, it returns a valid-looking code for a k-mer that was never indexed (maintainer, issue #22). Add a membership check (for example SSHash) if query reads can contain unseen k-mers.

## Caveats and trade-offs

The space win applies only to overlapping k-mers from spectrum-preserving string sets. The paper stresses that BBHash and PTHash are general-purpose MPHFs for arbitrary keys. Random-order (non-streaming) queries are slower than PTHash. Construction is slower than BBHash-v1: Table 5 gives 05:30 vs 00:48 on Cod and 07:25 vs 04:13 on Human. Datasets are on Zenodo (record 7239205). The last commit on the default branch (main) is 2023-07-19. The dev branch has a later commit, dated 2023-11-18.

Specialized for consecutive/overlapping k-mer key sets in bioinformatics, not a general-purpose MPHF; requires k-mer-specific preprocessing (stitched unitig files); partitioned vs. unpartitioned construction is a further trade-off between memory and speed.

## Maintenance

Abandoned by the catalog rule: the last commit on main is 2023-07-19, a restructured dev branch stops at 2023-11-18, and the short-input crash reported in 2023 is still unfixed. It is MIT-licensed, has about 20 source files plus the PTHash submodule, and builds with a C++17 GCC or Clang toolchain, so you can vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The peer-reviewed paper (Bioinformatics 39 Suppl. 1, i534) compares LPHash against BBHash and PTHash. It states the Intel i9-9900K CPU, gcc 11.2.0 and the flags -O3 -march=native. The benchmark code is public in the repo: src/ptbb/ptbb_build.cpp and src/ptbb/ptbb_query.cpp build and query BBHash (external/BooPHF.hpp) and PTHash, and scripts/experiments.sh runs them.
- **Verifier notes:** The paper names BBHash and PTHash as the competitors, so the 'unnamed baseline' caveat and the 0.4 confidence cap no longer apply. maintenance_status follows the prescribed commits?per_page=1 method (main, 2023-07-19, more than 3 years ago = abandoned). If the dev-branch commit (2023-11-18) is used instead, the status is 'stale'. The orchestrator may prefer that date.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://academic.oup.com/bioinformatics/article/39/Supplement_1/i534/7210438>
  - <https://arxiv.org/pdf/2210.13097v2>
  - <http://export.arxiv.org/api/query?search_query=ti:%22Locality-preserving%20minimal%20perfect%20hashing%22&max_results=5>
  - <https://github.com/jermp/lphash>
  - <https://github.com/jermp/lphash/blob/main/README.md>
  - <https://github.com/jermp/lphash/blob/main/CMakeLists.txt>
  - <https://github.com/jermp/lphash/blob/main/scripts/experiments.sh>
  - <https://github.com/jermp/lphash/blob/main/src/ptbb/ptbb_build.cpp>
- **Sources the enricher read:**
  - <https://github.com/jermp/lphash>
  - <https://github.com/jermp/lphash/blob/main/README.md>
  - <https://github.com/jermp/lphash/blob/main/CMakeLists.txt>
  - <https://github.com/jermp/lphash/blob/main/.gitmodules>
  - <https://github.com/jermp/lphash/blob/main/include/compile_constants.tpd>
  - <https://github.com/jermp/lphash/blob/main/include/constants.hpp>
  - <https://github.com/jermp/lphash/blob/main/include/partitioned_mphf.hpp>
  - <https://github.com/jermp/lphash/blob/main/include/mphf_utils.hpp>
  - <https://github.com/jermp/lphash/blob/main/include/util.hpp>
  - <https://github.com/jermp/lphash/blob/main/src/partitioned_mphf.cpp>
  - <https://github.com/jermp/lphash/blob/main/src/query.cpp>
  - <https://github.com/jermp/lphash/blob/main/src/build.cpp>
  - <https://github.com/jermp/lphash/commits/main>
  - <https://github.com/jermp/lphash/commits/dev>
  - <https://github.com/jermp/lphash/compare/main...dev>
  - <https://github.com/jermp/lphash/blob/dev/CMakeLists.txt>
  - <https://github.com/jermp/lphash/blob/dev/lib/include/mphf.hpp>
  - <https://github.com/jermp/lphash/blob/dev/lib/include/partitioned_mphf.hpp>
  - <https://github.com/jermp/lphash/issues?q=is%3Aissue>
  - <https://github.com/jermp/lphash/issues/18>
  - <https://github.com/jermp/lphash/issues/19>
  - <https://github.com/jermp/lphash/issues/20>
  - <https://github.com/jermp/lphash/issues/21>
  - <https://github.com/jermp/lphash/issues/22>
  - <https://arxiv.org/pdf/2210.13097v2>
  - <https://academic.oup.com/bioinformatics/article/39/Supplement_1/i534/7210438>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/jermp/lphash`) · [data/wave1-phf/enrich/raw/github_com_jermp_lphash.json](../../../data/wave1-phf/enrich/raw/github_com_jermp_lphash.json) (enrichment confidence 0.85)

</details>
