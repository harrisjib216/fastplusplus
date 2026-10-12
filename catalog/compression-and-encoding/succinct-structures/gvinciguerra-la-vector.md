# LA-vector

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Header-only C++17 compressed sorted-integer container and rank/select dictionary built from piecewise linear approximations; competes with SDSL sd_vector-style dictionaries.

| | |
|---|---|
| **Beats** | SDSL compressed bitvectors (sdsl::s18_vector, sdsl::rle_vector and other rank/select dictionaries compared in the paper repo) |
| **Claimed result** | TALG 2022 abstract (quoted in the artifact repo README): 'our select is the fastest, and our rank is on the space-time Pareto frontier' versus many well-established compressed rank/select dictionary implementations. No numbers seen here; a search snippet of the paper says LA-vector select is roughly 50 ns slower than sdsl::sd_vector in some configuration, so the win is dataset-dependent (snippet only). |
| **Workload** | Random access and rank over compressed bitvectors/containers using learned piecewise linear approximations; experiments in the paper repo. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5-2407 v2 2.40GHz, 41 GB RAM, Ubuntu 16.04.6 |
| **Compiler and flags** | gcc 9.2.1; CMake Release (-O3 -DNDEBUG) plus -march=native -pthread -fopenmp (Learned-Compressed-Rank-Select-TALG22 CMakeLists.txt) |
| **Adoption** | 47 stars |
| **Last commit** | 2024-09-04 |
| **Links** | [repository](https://github.com/gvinciguerra/la_vector) · [benchmark](https://github.com/aboffa/Learned-Compressed-Rank-Select-TALG22) |

## Verdict

The ACM TALG 2022 paper (abstract quoted in the GPL-3.0 artifact repo aboffa/Learned-Compressed-Rank-Select-TALG22) reports that la_vector's select is the fastest and its rank is on the space-time Pareto frontier against established compressed rank/select dictionaries including SDSL structures, s18_vector and rle_vector, measured with gcc 9.2.1 Release builds on an Intel Xeon E5-2407 v2. No numbers could be read in this session because the paper is behind blocked hosts and the artifact repo commits no result CSVs; the verifier's notes cite a search snippet saying select can be about 50 ns slower than sdsl::sd_vector on some data, so treat the win as data-dependent.

## Use it when

- Static sorted integer sets or sparse bitvectors (posting lists, DNA/k-mer positions, URL or document ID lists) whose values follow near-linear trends, so few segments and small corrections suffice.
- Select-heavy or random-access-heavy workloads (position to value) where you want a compressed representation that still decodes an element in a few instructions.
- When you want both a container view (operator[], iterators, lower_bound) and a rank/select view over the same compressed data.
- Space-time trade-off experiments against SDSL dictionaries, since the TALG22 artifact repo wires la_vector next to sd_vector, s18_vector, rle_vector and others.

## Skip it when

- Rank-dominated workloads where you need guaranteed speed: rank is a bounded search inside a segment window, and the authors only claim it is on the space-time Pareto frontier, not the fastest.
- Dynamic data: there is no insert, delete or bit flip; any change means rebuilding.
- Plain dense bitvectors with uniform random bits, where an uncompressed rank/select index (rank9, pasta-flat, SPIDER, QuadRank) is smaller in overhead and faster; LA-vector pays off only when the integer sequence is compressible by lines.
- MSVC builds or non-GCC/Clang toolchains: the code relies on __int128 and __builtin_clzll.
- Projects that cannot take an sdsl-lite dependency (the header includes sdsl/bits.hpp and sdsl/int_vector.hpp).

## How it is fast

Points (i, A[i]) are covered by an optimal piecewise linear approximation (the PGM-index segmentation algorithm) with error bound epsilon = 2^(bpc-1)-1, and each element is stored only as a small bpc-bit correction against its segment's prediction. select(i) is just operator[](i-1): a two-level bucketed lookup plus a branchless binary search finds the segment, then one multiply-add and one bit-field read decode the value, which is why the authors report select as the fastest among the dictionaries they compared. rank and lower_bound predict a position from the segment, then binary-search (or linearly scan) a window of at most 2\*epsilon+1 corrections, using sampled corrections in the fixed-bpc variant.

## Compared with alternatives

Pick LA-vector over h0_bv or succinct-bitvec-cpp when the data is a sparse, regular sorted integer set (Elias-Fano/sd_vector territory) and select or random access dominates; pick SPIDER, QuadRank or rankselect for dense plain bitvectors where raw rank speed with a few percent overhead matters more than compression.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | sdsl-lite headers (xxsds/sdsl-lite, git submodule); OpenMP optional (used for parallel segmentation at build time, a #warning recommends -fopenmp) |
| **Minimum toolchain** | C++17; GCC or Clang (uses __int128 and __builtin_clzll); CI builds with g++-11 on ubuntu-latest; CMake 3.12 for the bundled build |
| **Platforms** | 64-bit targets with __int128 (x86-64 tested in CI); the bundled CMakeLists adds -march=native |
| **Thread safety** | not documented; queries are const member functions over immutable data, construction may use OpenMP threads internally |
| **Drop-in for the baseline** | partial: same role as sdsl::sd_vector plus rank/select support, and it reuses SDSL serialization, but it is built from a sorted integer array rather than an sdsl::bit_vector and exposes rank(value)/select(i) member functions instead of SDSL rank_support/select_support objects |

## Gotchas

- Input must be sorted and non-decreasing unsigned integers; the segmentation throws std::logic_error on non-increasing x and std::overflow_error when a segment's bit fields or corrections do not fit, and the auto-bpc builder can throw std::runtime_error('Cannot reach target vertex').
- Correctness fixes landed after the papers: commit 'Fixes and space optimisation for 64-bit data #2' (2022-08-28) for a crash report on 127 values around 1.5e13, and 'Fixed signed overflow on input integers &gt;= 2^31 or 2^63' (2024-09-04). Use the current master, not the 2021-2022 snapshots the experiments were run on.
- rank(x) is implemented as distance(begin, lower_bound(x)), which counts elements strictly less than x, while its doc comment (and example.cpp) says 'less than or equal'; check the convention you need (observed in source, not tested).
- The range constructor reads \*begin and the last element before checking n == 0, so constructing from an empty range is undefined behaviour (observed in source).

## Known shortcomings

- Tier B on the TALG paper (ACM and boffa.top blocked, numbers unseen): select is the fastest and rank sits on the Pareto frontier per the abstract; a snippet says select is about 50 ns slower than sd_vector on some data. The artifact repo gives gcc 9.2.1 -march=native on a Xeon E5-2407 v2.
- rank(x) is implemented as distance(begin, lower_bound(x)), counting elements &lt; x, while its doc comment and example.cpp say &lt;= (seen in source, not tested); the constructor reads \*begin before checking n==0, so an empty range is undefined behaviour. Crash and overflow fixes came after the papers (issue #2 fixed 2022-08-28; signed overflow on inputs &gt;= 2^31/2^63 fixed 2024-09-04), so use current master rather than the measured code. Needs GCC/Clang (__int128) and sdsl-lite.

## Caveats and trade-offs

Peer-reviewed (ALENEX 2021, ACM TALG 2022), but neither paper could be opened here (ACM and boffa.top blocked), and the artifact repo commits no result CSVs, so the claimed advantage over SDSL is qualitative (abstract) only. A search snippet indicates select can be \~50 ns slower than sdsl::sd_vector on some data, so the advantage is a space-time trade-off, not a uniform speedup. Artifact repo is GPL-3.0 while the library itself is Apache-2.0. Depends on sdsl-lite.

Header-only C++17 that depends on SDSL headers. Compressed (space-saving) rather than a pure speed structure; supports operator[], lower_bound, rank, select, iterators, serialization. The experiment repo is GPL-3.0 and needs at least 32 GB RAM and a Google Drive dataset.

## Maintenance

Stale research code (last commits 2024-09-04, 31 commits, 47 stars, both issues closed) under Apache-2.0, small (two headers) and easy to vendor alongside sdsl-lite.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed (ACM TALG 2022, ALENEX 2021); the TALG abstract quoted in the artifact repo README states the la_vector select is the fastest and its rank is on the space-time Pareto frontier against many established compressed rank/select dictionaries (SDSL structures incl. s18_vector, rle_vector). The artifact repo (my_benchmark.cpp, run_all.sh) states gcc 9.2.1, Release plus -march=native and the Xeon E5-2407 v2, which would meet A, but no result numbers are in the repo and the paper PDFs (ACM, boffa.top) are blocked here, so the numbers stay unseen.
- **Verifier notes:** Library and benchmark repos exist and match the record (Apache-2.0, 47 stars, last commit 2024-09-04, stale). An environment that reaches dl.acm.org or boffa.top/files/ALENEX.pdf could check the numbers and possibly raise it to A, since the artifact repo states code, compiler, flags and CPU.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/gvinciguerra/la_vector>
  - <https://github.com/gvinciguerra/la_vector/commits/master>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/README.md>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/LICENSE>
  - <https://github.com/aboffa/Learned-Compressed-Rank-Select-TALG22>
  - <https://raw.githubusercontent.com/aboffa/Learned-Compressed-Rank-Select-TALG22/HEAD/README.md>
  - <https://raw.githubusercontent.com/aboffa/Learned-Compressed-Rank-Select-TALG22/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aboffa/Learned-Rank-Select-ALENEX21/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/gvinciguerra/la_vector>
  - <https://github.com/gvinciguerra/la_vector/commits/master>
  - <https://github.com/gvinciguerra/la_vector/issues?q=is%3Aissue>
  - <https://github.com/gvinciguerra/la_vector/issues/2>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/README.md>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/example.cpp>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/include/la_vector.hpp>
  - <https://raw.githubusercontent.com/gvinciguerra/la_vector/HEAD/include/piecewise_linear_model.hpp>
  - <https://raw.githubusercontent.com/aboffa/Learned-Compressed-Rank-Select-TALG22/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/gvinciguerra/la_vector`) · [data/wave9/enrich/raw/github_com_gvinciguerra_la_vector.json](../../../data/wave9/enrich/raw/github_com_gvinciguerra_la_vector.json) (enrichment confidence 0.7)

</details>
