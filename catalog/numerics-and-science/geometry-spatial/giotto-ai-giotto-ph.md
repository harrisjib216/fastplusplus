# giotto-ph (giotto-ai)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0` · 🟡 stale

> Multithreaded lock-free Vietoris-Rips persistent homology (Python API, C++ backend) that outruns single-threaded Ripser v1.2 when given several cores.

| | |
|---|---|
| **Beats** | Ripser v1.2 (Ripser/ripser by Ulrich Bauer); also compared with GPU Ripser++ according to the release notes |
| **Claimed result** | README figure (multithreading_speedup.svg) is self-relative thread scaling, normalized to 1.0 at one thread for every dataset (derived from page data by reading the SVG path coordinates): at 48 threads fractal about 23.7x, o3_4096 about 14.2x, random16 about 12.9x, o3_1024 about 10.2x, torus4 about 10.1x, sphere3 about 1.7x, dragon about 1.06x (dragon peaks about 1.5x between 5 and 11 threads). Against Ripser v1.2 the paper (arXiv 2107.05412, search snippet only) says giotto-ph performs very similarly on one thread and is faster whenever more than one thread is used; v0.1.0 release notes say it surpasses 'GPU-accelerated implementations such as Ripser++ when using as few as 5-10 CPU cores'. No head-to-head times against Ripser or Ripser++ were reachable. |
| **Workload** | Wall-clock computation of Vietoris-Rips persistence barcodes on the Ripser benchmark datasets (sphere3, dragon, o3_1024, random16, fractal, o3_4096, torus4) as a function of thread count, from the README speedup figure. |
| **Metric** | latency |
| **Adoption** | 59 stars; designed for integration with giotto-tda and pyflagser (README) |
| **Last commit** | 2024-05-30 |
| **Links** | [repository](https://github.com/giotto-ai/giotto-ph) · [benchmark](https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/docs/images/multithreading_speedup.svg) |

## Verdict

The only numbers in the repository are the README figure, which is giotto-ph's own thread scaling (every curve is exactly 1.00 at one thread; the paper describes its scaling figure as giotto-ph with more worker threads), reaching 23.7x on fractal, 14.2x on o3_4096 and 10x to 13x on o3_1024, random16 and torus4 at 48 threads but only 1.7x on sphere3 and 1.06x on dragon (derived from the SVG path data), with no CPU, compiler or flags given. The comparison with Ripser v1.2 (parity on one thread, faster with more) and the claim of beating GPU Ripser++ with 5 to 10 CPU cores come from the arXiv 2107.05412 paper and the v0.1.0 notes, seen here only through search snippets.

## Use it when

- Large Vietoris-Rips problems with homology dimension 2 or higher on a many-core CPU, where the README figure shows 10x to 24x self-relative scaling at 48 threads (fractal 23.7x, o3_4096 14.2x, random16 12.9x, o3_1024 10.2x, torus4 10.1x).
- Python topological data analysis pipelines, especially with giotto-tda or pyflagser, that today call ripser.py single-threaded.
- You need flag persistence generators (vertices and edges creating or killing bars), weighted or DTM-reweighted Rips filtrations, or coefficients other than Z/2.
- Pushing to higher homology dimensions on dense point clouds where edge collapse removes enough edges to make the computation fit.

## Skip it when

- Small or shallow computations: the README figure shows sphere3 at 1.7x and dragon (dimension 1 only) at 1.06x even with 48 threads; dragon drops from 1.51x at 11 threads to 1.07x at 13 and never recovers (derived from the SVG), so more threads can hurt.
- Closed-source or network-served products that cannot accept AGPL-3.0; a different licence is only available on request from L2F.
- Any filtration other than Vietoris-Rips (cubical, alpha, witness complexes), or when you need a C++ API: the backend is a pybind11 extension and the header pulls in the preshing Junction and Turf submodules.
- Python 3.13 or newer, Linux aarch64 or other platforms without wheels: PyPI 0.2.4 ships only CPython 3.8 to 3.12 wheels for manylinux2014 x86_64, macOS universal2 and win_amd64, and source-build issues #72 and #75 (Clang needs explicit atomic linking) are open.
- Many points at high maxdim: simplex indices are capped at 2^55 - 1, so issue #74 (2,000 points, maxdim=5) fails with OverflowError, and point clouds without a threshold go through a dense O(n^2) pairwise distance matrix.

## How it is fast

It reimplements Morozov and Nigmetov's lock-free Ripser: worker threads from a thread pool reduce coboundary-matrix columns concurrently, columns live in a vector of std::atomic pointers with epoch-based memory reclamation, and the pivot table is a Junction leapfrog concurrent hash map updated by insert or compare-and-update instead of locks. Ripser v1.2's apparent (zero-persistence) pair shortcut is searched in parallel chunks, column lists are sorted with a parallel sort, and an optional edge collapse (reimplemented from GUDHI) shrinks the 1-skeleton before the flag complex is built. Dimension 0 (union-find) stays sequential.

## Compared with alternatives

The geometry-spatial siblings are spatial indexes, meshing and geometry kernels, none of which compute persistent homology; the closest catalogued project is Ripserer.jl (filed elsewhere), a Julia reimplementation that runs at or below single-threaded Ripser speed, so pick giotto-ph when you have many cores, a Python pipeline and a large or deep Vietoris-Rips computation, and stay with single-threaded Ripser for small or shallow problems or when AGPL terms are unacceptable.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python &gt;= 3.7 with NumPy &gt;= 1.19.1, SciPy &gt;= 1.5.0, scikit-learn &gt;= 0.23.1; source builds need CMake &gt;= 3.9, a C++14 compiler, pybind11, preshing Junction and Turf (git submodules) |
| **Minimum toolchain** | C++14 (CMakeLists.txt); prebuilt wheels for CPython 3.8 to 3.12 |
| **Platforms** | x86-64 Linux (manylinux2014), macOS universal2 (x86-64 and Apple Silicon), Windows x86-64; other platforms only via source build |
| **Thread safety** | Internally multithreaded via its own thread pool; concurrent calls of ripser_parallel from several Python threads are not documented |
| **Drop-in for the baseline** | partial — replaces ripser.py-style calls with ripser_parallel and similar arguments, but it is not a C++ drop-in for Ripser, returns float32 barcodes, defaults to one thread, and cannot combine collapse_edges with return_generators |

## Gotchas

- ripser_parallel defaults to n_threads=1, which per the paper performs about like Ripser v1.2; pass n_threads=-1 (all hardware threads) or an explicit count to get any speedup.
- Issue #68 (open since 2022-08-17, help wanted) reports intermittent failures in the tests that compare multithreaded with single-threaded results, including assertion errors and not only deadline timeouts; the lock-free reduction code itself notes that its consistency check is weaker than the original lock-free paper's and carries a TODO to think through memory orders. Cross-check important barcodes with n_threads=1.
- Filtration values are float32 inside the backend and in the returned diagrams (release 0.2.1), and the GCC/Clang release build compiles the edge collapser with -Ofast, which assumes finite, non-NaN values; precomputed matrices with inf entries fed through collapse_edges are outside what that flag guarantees.
- No benchmark code, datasets, CPU model, compiler or flags are in the repository (reproducibility issue #20 is open), so the published scaling cannot be rerun from the repo alone.

## Known shortcomings

- The README speedup SVG is self-relative thread scaling (every curve 1.0 at 1 thread, read from path coordinates), not a head-to-head with Ripser; the Ripser and Ripser++ wins are first-party only (paper snippet, v0.1.0 notes). No CPU, compiler, flags or benchmark code. AGPL-3.0.
- Enricher: the README figure is confirmed self-relative (all curves 1.00 at 1 thread) and the dragon dataset drops from 1.51x to 1.07x past 12 threads; no bench code or hardware in the repo. Issue #68 (flaky multithread-vs-single tests with assertion errors) is open and the code has a TODO on memory orders; default n_threads is 1; float32 only; index cap 2^55-1 (#74); wheels only for CPython 3.8-3.12; last commit 2024-05-30.

## Caveats and trade-offs

The README figure is giotto-ph's own thread scaling (every curve is 1.0 at one thread), not a head-to-head with Ripser; the speedup over Ripser v1.2 can only be inferred by combining it with the paper's statement (search snippet only, arXiv blocked) that single-thread giotto-ph performs about like Ripser v1.2. The paper's Figure 2 (giotto-ph vs Ripser v1.2) and its Ripser++ comparison could not be opened. No CPU model, core count (axis reaches 48 threads), compiler or flags appear in the README, release notes or repo, and the repo has no benchmark folder or benchmark code. Gains are small on easy datasets (sphere3 about 1.7x, dragon about 1.06x at 48 threads). Licensed AGPL-3.0 (copyleft), and the last commit (2024-05-30) is over two years old. Ripserer.jl issue #168 (the lead) has no speed data.

AGPLv3 network copyleft (the README offers a separate licence on request via the L2F team); Python API with a C++ backend, installed as wheels. Only Vietoris-Rips filtrations. The optional edge collapse (reimplementation of GUDHI's algorithm) does not help every dataset, and speedup depends on dataset size and homology dimension: shallow computations such as dragon up to dimension 1 barely scale.

## Maintenance

Stale: the last commit and the last PyPI releases (0.2.3 and 0.2.4) date from 2024-05-30, with no wheels beyond CPython 3.12 and 10 open issues including build failures and flaky multithreaded tests; AGPL-3.0, so it is copyable only on AGPL terms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark_url SVG is a thread-scaling plot whose every curve starts at exactly 1.0 at one thread, so it is giotto-ph against its own single-thread run, not against Ripser; the Ripser v1.2 comparison and the Ripser++ claim are first-party (arXiv 2107.05412 via search snippet, v0.1.0 release notes) with no reachable numbers, CPU, compiler, flags or benchmark code. First-party claim without methodology stays C.
- **Verifier notes:** Shortcoming: benchmark figure is self-relative thread scaling, not a Ripser head-to-head; Ripser and Ripser++ wins are first-party paper/release-note claims seen only via snippet, no hardware, compiler, flags or benchmark code. Metadata checked: 59 stars, AGPL-3.0 per README and LICENSE file, last commit 2024-05-30 (stale), not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-180 (wave 8 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/docs/images/multithreading_speedup.svg>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/README.rst>
  - <https://github.com/giotto-ai/giotto-ph>
  - <https://github.com/giotto-ai/giotto-ph/commits>
  - <https://github.com/giotto-ai/giotto-ph/releases>
- **Sources the enricher read:**
  - <https://github.com/giotto-ai/giotto-ph>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/README.rst>
  - <https://github.com/giotto-ai/giotto-ph/tree/main/gph/src>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/gph/src/ripser.h>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/gph/python/ripser_interface.py>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/.gitmodules>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/setup.py>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/RELEASE.rst>
  - <https://raw.githubusercontent.com/giotto-ai/giotto-ph/main/docs/images/multithreading_speedup.svg>
  - <https://github.com/giotto-ai/giotto-ph/issues?q=is%3Aissue>
  - <https://github.com/giotto-ai/giotto-ph/issues/68>
  - <https://github.com/giotto-ai/giotto-ph/issues/74>
  - <https://pypi.org/pypi/giotto-ph/json>
  - https://arxiv.org/pdf/2107.05412 (blocked: ENOTFOUND; content seen only through WebSearch snippets)
  - https://github.com/mtsch/ripserer.jl (catalogue record in data/wave14/verified.json, not the repo)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/giotto-ai/giotto-ph`) · [data/wave8/enrich/raw/github_com_giotto_ai_giotto_ph.json](../../../data/wave8/enrich/raw/github_com_giotto_ai_giotto_ph.json) (enrichment confidence 0.68)

</details>
