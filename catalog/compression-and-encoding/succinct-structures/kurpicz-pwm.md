# pwm (parallel wavelet tree and matrix construction)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Sequential, parallel and external-memory wavelet tree/matrix construction (prefix counting/sorting); ALENEX 2018 reports up to 2x faster than Shun's construction.

| | |
|---|---|
| **Beats** | Shun's wavelet tree construction (DCC 2015) and Labeit et al.; SDSL-based competitors can be built with PWM_BUILD_SDSL_WT |
| **Claimed result** | Search-result snippet of the ALENEX 2018 abstract (page not opened, snippet only): sequential algorithm up to twice as fast as the currently fastest sequential construction (Shun, DCC 2015) while saving a factor 2 in space; parallel algorithm scales to 32 cores with performance comparable to Labeit et al. using about 75% of the space. |
| **Workload** | Construction of wavelet trees and wavelet matrices from text, sequential and parallel (up to 32 cores); also an external-memory variant. |
| **Metric** | build-time |
| **Adoption** | 26 stars |
| **Last commit** | 2020-07-12 |
| **Links** | [repository](https://github.com/kurpicz/pwm) · [benchmark](https://arxiv.org/abs/1702.07578) |

## Verdict

The ALENEX 2018 paper (seen through search snippets only; arXiv, SIAM and Semantic Scholar are blocked) reports a sequential prefix-counting construction up to 2x faster than Shun's DCC 2015 algorithm using half the space. In parallel, ddpcWT is on average 13% faster than Shun's recWT on 32 cores and comparable to Labeit et al. using about 75% of the space. Hardware, compiler and tables were not seen; the repo's CMake builds with -O3 -funroll-loops -march=native and includes the competitors' code, so the comparison is reproducible in principle.

## Use it when

- Building wavelet trees or matrices over large texts (GBs; byte, 16-bit or 32-bit symbols after alphabet reduction) where construction time or peak memory is the bottleneck.
- Multicore Linux servers: the paper says the domain-decomposition variant (ddpcWT) is on average 13% faster than Shun's recWT on 32 cores, and faster on large or small-alphabet texts (PROT, 1000G, CC).
- Texts that do not fit in RAM: the semi-external and fully external variants (STXXL-based) build the structure from disk.
- Benchmarking WT/WM construction: the repo vendors Shun's and Labeit et al.'s competitors (serialWT, levelWT, recWT, ddWT, sortWTOpt and others) and a driver that reports median time and peak memory and can check its output against the naive builder.

## Skip it when

- You need fast rank/select/access queries: pwm only builds the bit vectors; query speed comes from whatever rank/select layer you put on top (SDSL, QWT and so on).
- Small texts, where SDSL's built-in constructors are good enough and avoid the pwm, tlx and STXXL dependency chain.
- Very large alphabets that have not been reduced: prefix counting keeps a 2^levels histogram per level (per thread for ppc), so memory grows with sigma.
- Wanting all cores busy in the plain ppc variant: after the first level, its parallelism is over levels (levels - 1 tasks, e.g. 7 for a byte alphabet). Use the dd_\* variants for wide machines.
- Non-Linux or non-GCC/Clang builds: CMake rejects other compilers and links rt, dl and stdc++fs; abandoned since July 2020 with a dead travis-ci.org badge.

## How it is fast

Prefix counting builds the levels bottom-up. One scan writes level 0 and a histogram of the reduced alphabet; parent histograms come from summing child buckets, prefix sums of the histogram (with the bit-reversal permutation for the matrix) give each bit prefix's write offset, and each level is then a single linear pass writing one bit per symbol. Prefix sorting instead stable-sorts the text by bit prefix level by level. The parallel versions shard histograms per thread and run the levels in parallel with OpenMP. The domain-decomposition variants (dd_pc, dd_ps) split the text into p slices, build per-slice structures and merge the bit vectors, which the paper says lets them scale to 32 cores while using less memory than Labeit et al.

## Compared with alternatives

No sibling builds wavelet trees faster; QWT and quad-wavelet-tree speed up queries, and wavelet_forest and faster-minuter change the tree shape. Use pwm to build the levels quickly and in parallel, then hand them to a query-side structure; pick a sibling when query latency is the goal.

## Integration

| | |
|---|---|
| **Form** | header-only algorithms (include/), built with CMake as a benchmark executable |
| **Dependencies** | OpenMP; tlx (submodule, command-line parser); STXXL (fetched by find_or_download_package, needed by the benchmark and external-memory variants); googletest for tests; competitor builds need Cilk Plus (gcc &lt; 8) and optionally an installed SDSL |
| **Minimum toolchain** | C++17; GCC 7.3+ or Clang 3.4+ (CMake checks); Release builds use -O3 -funroll-loops -march=native -fopenmp |
| **Platforms** | Linux x86-64 in practice (links rt, dl, stdc++fs; -march=native); other compilers are rejected by CMake |
| **Thread safety** | not documented; parallel variants use OpenMP internally and size thread-local histograms from omp_get_max_threads() |
| **Drop-in for the baseline** | partial: it replaces the construction step only; output is pwm's own wavelet_structure (level bit vectors plus zeros), which you must convert for SDSL or other query libraries |

## Gotchas

- PWM_ENABLE_CILK_ALGORITHM defaults to ON, but those competitors need Cilk Plus, which GCC removed in version 8. On a modern GCC, configure with -DPWM_ENABLE_CILK_ALGORITHM=OFF (or -DPWM_BUILD_COMPETITORS=OFF).
- The README calls the SDSL option PWM_BUILD_SDSL_WT, but CMakeLists.txt defines PWM_BUILD_SDSL_WX, so the documented flag silently does nothing.
- Past correctness bugs, all now closed: issue #1 (Apr 2017) was a heap overflow in every construction algorithm (memset of (size+63)&gt;&gt;3 bytes into a buffer of ((size+63)&gt;&gt;6) uint64 words). Issue #5 (Oct 2018) suspected ppc_ss OpenMP pragmas made threads redo the same work. Issues #16/#17 (Dec 2018, fixed by PR #18) were a thread limit not applied to the ppx variants and ppc_ss performance problems. Issue #1 was closed after the February 2017 arXiv v1 but before ALENEX 2018; the _ss and ppc fixes came after the paper.
- The benchmark's --check validation works only for 1-byte alphabets (benchmark.cpp prints that it can only check texts over 1-byte alphabets).

## Known shortcomings

- Downgraded B to C: 'up to 2x vs Shun DCC 2015' is seen only in abstract snippets (arXiv 1702.07578 blocked); construction time, not vs SDSL queries. Retier candidate.
- Construction only; output is its own wavelet_structure, not SDSL's. Past bugs, all closed: #1 memset heap overflow in all construction algorithms (Apr 2017, after arXiv v1 and before ALENEX), #5 ppc_ss OpenMP pragmas suspect, #16/#17 thread limit and ppc_ss performance (PR #18, after the paper). PWM_ENABLE_CILK_ALGORITHM defaults ON and needs gcc &lt; 8; README flag PWM_BUILD_SDSL_WT differs from CMake's PWM_BUILD_SDSL_WX. Linux-only links (rt, dl, stdc++fs); --check works only for 1-byte alphabets.

## Caveats and trade-offs

The number is from the ALENEX 2018 abstract via search snippets only (arXiv, SIAM, doi.org and Semantic Scholar are blocked here); tables, hardware and flags were not seen. The baseline is other construction algorithms (Shun DCC 2015, Labeit et al.), not SDSL's constructor, which is only an optional competitor build (PWM_BUILD_SDSL_WT, off by default). The repo includes a benchmark driver and the competitors' code, so the paper's tables could support A or B after a paper-access retier. Last commit July 2020.

Construction only: it builds the tree faster and in less space, it does not change query speed. Output format differs from sdsl wt classes.

## Maintenance

Abandoned since July 2020 (all 4 issues closed); BSD-2-Clause, and the core algorithms are a handful of headers that can be vendored without the benchmark's STXXL and Cilk baggage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The 'up to twice as fast as Shun (DCC 2015) while saving a factor 2 in space' figure appears in several search snippets of the ALENEX 2018 abstract (arXiv 1702.07578, linked from the README), but the paper body, its tables, compiler, flags and CPU could not be opened. A headline number from the authors' own abstract, with no methodology seen, is C. The repo ships the benchmark driver (src/benchmark) and competitor builds (external/wavelet_construction), but the README has no results.
- **Verifier notes:** benchmark_url set to the arXiv preprint the README links (blocked here, not opened). Metadata confirmed: BSD-2-Clause, 26 stars, 2 forks, not a fork, not archived, last commit 2020-07-12 (abandoned). Retier candidate once arXiv is reachable.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; peer-reviewed paper (ALENEX)
- **Pages the verifier opened:**
  - <https://github.com/kurpicz/pwm>
  - <https://github.com/kurpicz/pwm/commits>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/README.md>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/kurpicz/pwm>
  - <https://github.com/kurpicz/pwm/tree/master/include>
  - <https://github.com/kurpicz/pwm/tree/master/include/construction>
  - <https://github.com/kurpicz/pwm/tree/master/include/arrays>
  - <https://github.com/kurpicz/pwm/tree/master/include/queries>
  - <https://github.com/kurpicz/pwm/tree/master/src>
  - <https://github.com/kurpicz/pwm/tree/master/external/wavelet_construction>
  - <https://github.com/kurpicz/pwm/issues?q=is%3Aissue>
  - <https://github.com/kurpicz/pwm/issues/1>
  - <https://github.com/kurpicz/pwm/issues/5>
  - <https://github.com/kurpicz/pwm/issues/16>
  - <https://github.com/kurpicz/pwm/issues/17>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/README.md>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/wx_pc.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/wx_ppc.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/wx_ppc_ss.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/wx_base.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/construction/pc.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/construction/ppc.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/construction/ppc_ss.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/construction/building_blocks.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/arrays/bit_vectors.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/include/arrays/flat_two_dim_array.hpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/external/wavelet_construction/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kurpicz/pwm/HEAD/test/CMakeLists.txt>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/kurpicz/pwm`) · [data/wave9/enrich/raw/github_com_kurpicz_pwm.json](../../../data/wave9/enrich/raw/github_com_kurpicz_pwm.json) (enrichment confidence 0.7)

</details>
