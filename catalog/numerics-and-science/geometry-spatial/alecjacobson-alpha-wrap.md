# alpha-wrap (CGAL-free Alpha Wrapping)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> MIT clean-room C++17 alpha wrapping (TOG 2022) without CGAL; about 2x faster than a GMP-free CGAL::alpha_wrap_3 build.

| | |
|---|---|
| **Beats** | CGAL 6.x CGAL::alpha_wrap_3 (Alpha_wrap_3), GMP-free build |
| **Claimed result** | README: 'Speed: competitive to faster (ours \~2x faster on most inputs in this GMP-free CGAL environment)'. Same page: face count 0.6-1.0x CGAL's, symmetric Hausdorff distance to the CGAL wrap 0.1%-3.4% of the bbox diagonal. No per-model timing table. |
| **Workload** | Alpha wrapping with offset of triangle soups (bundled meshes, a 100k-triangle sphere and a 236k-triangle Actaeon statue, alpha = diag/30), compared with the CGAL reference build for speed, topology and Hausdorff distance. |
| **Metric** | latency |
| **Compiler and flags** | CMake -DCMAKE_BUILD_TYPE=Release for the comparison build (RelWithDebInfo for the default build); optimization flags and compiler not stated |
| **Adoption** | 10 stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/alecjacobson/alpha-wrap) · [benchmark](https://github.com/alecjacobson/alpha-wrap) |

## Verdict

The only speed claim is one README sentence: 'competitive to faster (ours \~2x faster on most inputs in this GMP-free CGAL environment)', measured by the author against CGAL 6.0.1 CGAL::alpha_wrap_3 with the EPICK kernel built header-only with CGAL_DISABLE_GMP, over the bundled meshes, a 100k-triangle sphere and a 236k-triangle statue at alpha = diag/30. No per-model times, hardware or compiler are given; output is 0.6-1.0x CGAL's face count and within 0.1-3.4% of the bbox diagonal (Hausdorff) of CGAL's wrap, so the two do not produce identical work.

## Use it when

- Making watertight, manifold shells from defective meshes (scans, CAD exports, game assets, Thingi10K-style 3D-print models) for meshing, simulation, collision proxies or 3D printing, when you cannot ship GPL/LGPL CGAL code
- Python pipelines that want a pip-installable wrapper over NumPy arrays (wheels are built for Linux, macOS arm64/x86_64 and Windows x86-64) without pulling Boost or CGAL
- Coarse to medium wraps (alpha around diag/20 to diag/300) of meshes up to a few hundred thousand triangles: the README tested a 100k-triangle sphere and a 236k-triangle statue, and a 1000-model Thingi10K run gave median 1.1 s and p90 6.2 s per model
- Batch jobs where a slightly coarser output (0.6-1.0x CGAL's face count) is acceptable or even preferred

## Skip it when

- When you need CGAL's exact output or its extra features (point-set and segment-soup oracles, seeds for interior wrapping, visitors, custom oracles, the faster unsorted LIFO queue): this implements only the triangle-soup path
- When you already link CGAL with GMP: the only speed claim is against a CGAL 6.0.1 build with CGAL_DISABLE_GMP (Boost.Multiprecision fallback), with no timing table, hardware or compiler, so a normal GMP-backed CGAL may close the gap
- Very fine wraps or huge inputs that need multithreading: the wrap is single-threaded (no threading in src/), and the Thingi10K worst case took 59 s on one model
- Production code that needs a track record: the repo is two months old (first commit 2026-07-29, 8 commits, 10 stars, no issues filed), and the authors note a known residual degenerate case (zero-volume Delaunay cells) that is only detected, not fixed, by verify_topology()
- Binary I/O or formats beyond OBJ and ASCII PLY through the CLI

## How it is fast

It runs the paper's algorithm on its own data structures instead of CGAL's generic machinery: a roughly 1.2k-line incremental Bowyer-Watson 3D Delaunay on flat cell arrays with a free list, an enclosing super-tetrahedron instead of an infinite vertex, and Shewchuk's adaptive exact orient3d/insphere predicates (public domain). The input soup goes into a hand-written AABB tree that answers distance, closest point, tet-soup intersection and the offset-surface crossing; the crossing is found by sphere tracing the 1-Lipschitz distance field. Gates are flood-filled from a max-circumradius priority queue as in CGAL's sorted reference variant. The README attributes the measured gap partly to the comparison environment ('in this GMP-free CGAL environment'); no profiling breakdown is published.

## Compared with alternatives

No catalogued sibling does alpha wrapping. Pick it over Manifold or MeshLib when the input is a broken soup that their booleans reject or that you must first close: alpha-wrap is the repair/wrapping step that yields the closed manifold mesh those tools require, and it does so under MIT without CGAL. For booleans on already-clean meshes use Manifold, kigumi or trueform instead.

## Integration

| | |
|---|---|
| **Form** | static lib (awcore, 4 .cpp files) plus CLI and Python wheel (nanobind, scikit-build-core) |
| **Dependencies** | Shewchuk's robust predicates (danshapero/predicates), fetched by CMake FetchContent from GIT_TAG master on first configure (network needed); NumPy for the Python package. Optional CGAL 6.0.1 + Boost 1.85 headers only for the reference tool or wrap_cgal (GPL-encumbered build). |
| **Minimum toolchain** | C++17, CMake 3.16+; Python 3.8+ for bindings (wheels built for CPython 3.9-3.13); CI builds with Release on ubuntu-latest, macos-latest and windows-latest |
| **Platforms** | Linux, macOS (arm64 tested, x86_64 cross-built), Windows x86-64; no SIMD or architecture-specific code; musllinux, PyPy and 32-bit wheels are skipped |
| **Thread safety** | not documented; each aw::AlphaWrap object holds its own Delaunay, oracle and labels, so separate instances on separate threads look independent, but no guarantee is stated |
| **Drop-in for the baseline** | partial — same algorithm, guarantees and alpha/offset parameters as CGAL::alpha_wrap_3 for triangle soups, but a different API and mesh type, a slightly different (coarser) output, and no point-set/segment inputs or seeds |

## Gotchas

- Builds must keep -ffp-contract=off (set in CMake for GCC/Clang) and must not use fast-math, or the exact predicates break silently; vendoring the sources into another build needs the same flags
- The flood fill stops at a hard cap of 5,000,000 Steiner points (max_steiner in alpha_wrap.cpp) and just breaks out of the loop; check WrapStats.steiner_points or the CLI's invariant report if you push alpha very small
- The predicates dependency is fetched from an unpinned master branch, so builds are not reproducible and pick up upstream changes; pin GIT_TAG for production
- Default CMake build type is RelWithDebInfo; the CGAL comparison used -DCMAKE_BUILD_TYPE=Release, so benchmark both in Release

## Known shortcomings

- Only '\~2x faster vs GMP-free CGAL' with no timing table or hardware; output is coarser (0.6-1.0x CGAL's face count); all commits co-authored by Claude.
- CGAL reference build is CGAL 6.0.1 with GMP disabled (CGAL_DISABLE_GMP), so the \~2x claim is not against a normal CGAL install. Flood fill stops silently at 5M Steiner points. Predicates dependency fetched from unpinned master. Single-threaded.

## Caveats and trade-offs

One summary sentence ('competitive to faster, \~2x faster on most inputs') with no timing table; the CGAL reference is built GMP-free (CGAL 6.x fetched by CMake with -DAW_CGAL_REFERENCE=ON), which can make CGAL slower than a typical GMP-backed install; hardware and compiler unstated. The benchmarks/thingi10k README reports robustness (1000/1000 valid wraps) and absolute times (median 1.1 s, p90 6.2 s, max 59 s per model, 32-way parallel) but no CGAL timings. Output is coarser (0.6-1.0x CGAL's face count), so equal work is not shown. Very new repo (first commit 2026-07-29, 8 commits, 10 stars) and every commit lists Claude as co-author. Not an independent measurement.

Clean-room implementation of the TOG 2022 algorithm; only dependency is Shewchuk's public-domain predicates (no CGAL, no GPL); Python bindings via nanobind; coarser output (0.6-1.0x faces) and small geometric deviations from CGAL's wrap.

## Maintenance

Active but very new (8 commits from 2026-07-29 to 2026-08-31, every commit co-authored by Claude per the verifier), MIT-licensed and small enough to vendor; treat as a promising research-grade tool rather than a proven replacement for CGAL.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Comparison against CGAL' section compares against CGAL's Alpha_wrap_3 and gives one summary figure ('ours \~2x faster on most inputs in this GMP-free CGAL environment') with no per-model timings, hardware or compiler. The comparison tool (tools/cgal_wrap, aw_metrics) is public, but methodology is partial and the measurement is first-party, so C.
- **Verifier notes:** README numbers match the record. Metadata checked on the repo page: MIT, 10 stars, not a fork, last commit 2026-08-31. CGAL is a named incumbent of geometry-spatial, so baseline_in_list true is right.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/alecjacobson/alpha-wrap>
  - <https://github.com/alecjacobson/alpha-wrap/commits>
  - <https://github.com/alecjacobson/alpha-wrap/tree/main/benchmarks/thingi10k>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/alecjacobson/alpha-wrap>
  - <https://github.com/alecjacobson/alpha-wrap/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/README.md>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/DESIGN.md>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/docs/algorithm-spec.md>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/cmake/cgal.cmake>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/cmake/dependencies.cmake>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/tools/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/tools/cgal_wrap.cpp>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/src/alpha_wrap.hpp>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/src/alpha_wrap.cpp>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/src/delaunay.hpp>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/src/aabb_tree.hpp>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/python/alpha_wrap/__init__.py>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/benchmarks/thingi10k/README.md>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/alecjacobson/alpha-wrap/HEAD/.github/workflows/wheels.yml>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/alecjacobson/alpha-wrap`) · [data/wave8/enrich/raw/github_com_alecjacobson_alpha_wrap.json](../../../data/wave8/enrich/raw/github_com_alecjacobson_alpha_wrap.json) (enrichment confidence 0.7)

</details>
