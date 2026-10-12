# Versor (geometric algebra library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Template-metaprogrammed C++ geometric algebra library; within \~15% of GATL and 18-2,600x faster than Garamon, TbGAL, GluCat.

| | |
|---|---|
| **Beats** | other C++ geometric algebra solutions: GluCat (framed and matrix), TbGAL, Garamon, Gaalet, Gaalop, GATL |
| **Claimed result** | ga-benchmark 2020-02-05 run, wall-clock real_time (derived from the run JSONs): Versor geomean 0.88x GATL speed (GATL faster in 1,239 of 1,816 cases; inverse kinematics 242 vs 857 ns), 0.96-0.98x Gaalop and Gaalet; Versor 18x faster than Garamon, 37x TbGAL, 162x GluCat (framed), 2,588x GluCat (matrix). Wall-clock golds: GATL 111, Gaalet 76, Gaalop 55, Versor 23. The published medal table (GATL 247 golds, Versor 246) ranks by CPU time read from a 15.625 ms WSL1 tick, so its golds are zero-time ties. |
| **Workload** | ga-benchmark: 10 unary and 12 binary geometric algebra operations (geometric product, outer product, inner products, dualization, inversion and others) on conformal, Euclidean (2-5 D) and Minkowski models plus a conformal inverse kinematics algorithm, ranked by mean CPU time with Google Benchmark. |
| **Metric** | throughput |
| **Hardware** | 8 x 1992 MHz CPUs, CPU model not stated, Linux 4.4.0-18362-Microsoft (Windows Subsystem for Linux), CPU scaling off, metric CPU time |
| **Compiler and flags** | GNU Compiler Collection 7.4.0 in 'release' mode (CMake Release; exact flags not stated in the result pages) |
| **Adoption** | 327 stars, 54 forks; one of seven solutions in ga-benchmark |
| **Last commit** | 2025-11-03 |
| **Links** | [repository](https://github.com/wolftype/Versor) · [benchmark](https://raw.githubusercontent.com/ga-developers/ga-benchmark-runs/HEAD/2020.02.05/ranking_1.html) |

## Verdict

ga-benchmark's 2020-02-05 run (GCC 7.4.0, CMake Release, double precision, Google Benchmark with 10,000 calls x 30 repetitions on random blades, 8 x 1992 MHz CPUs under WSL1, CPU model not stated) gives Versor 246/76/1 medals by mean CPU time, level with GATL, but almost all those golds are zero-CPU-time ties caused by the 15.625 ms WSL1 clock. The run's own wall-clock data put Versor at about 0.88x GATL's speed and 0.96-0.98x Gaalop's and Gaalet's on geometric mean, and 18x to 2,588x faster than Garamon, TbGAL and GluCat over the cases both implement (derived from page data); nothing is compared with Boost.Geometry, CGAL, GEOS or a std facility.

## Use it when

- Conformal GA (3D CGA) or 2-5D Euclidean/Minkowski algebra in C++ where dimensions and blade layouts are known at compile time and you want typed sparse multivectors with no runtime overhead
- Replacing a runtime-dispatched GA library: in the 2020 ga-benchmark run Versor's per-call wall-clock time was 18x (Garamon), 37x (TbGAL), 162x (GluCat framed) and 2,588x (GluCat matrix) lower on geometric mean over shared cases (derived from page data)
- Normalization-heavy code: runit() measured about 3.4x faster than GATL's normalization on geometric mean (derived from page data)
- Robotics, kinematics or parametric-design prototypes that benefit from the built-in OpenGL/GLES drawing and example apps
- Projects that need a permissive licence (BSD-2-Clause) for GA code

## Skip it when

- You want the fastest compile-time GA library: in the same run GATL was faster in 1,239 of 1,816 shared cases (about 1.14x geometric mean) and 3.5x faster on the conformal inverse-kinematics algorithm (242 ns vs 857 ns per call, derived from page data)
- Commutator-product-heavy code: operator% computes (ab - ba)/2 with two full geometric products and measured about 2.5x slower than GATL
- You need operations ga-benchmark found missing: right contraction, regressive product, dot and Hestenes inner products were marked not implemented (a scalar_product method exists in current devel)
- Higher or runtime-chosen dimensions: blade lists are compile-time types, the build needs -ftemplate-depth-1200, compile times grow with dimension, and issue #22 reports the Rotor typedef is incomplete above 3D (no pseudoscalar)
- You need a Boost.Geometry/CGAL/GEOS replacement: no robust predicates, polygons, meshes or spatial indexes, and no benchmark against those incumbents

## How it is fast

Each multivector type carries its list of basis blades as a template parameter, and products are expanded at compile time: vsr_products.h enumerates blade pairs with bitmask tests (xor for the result blade, sign-flip, inner/outer legality), builds an instruction list for only the non-zero coefficient pairs, and deduces the sparse result type, so a \* b compiles to a fixed sequence of multiply-adds over a plain value_t val[N] array with no runtime dispatch or heap. Conformal null-basis metrics are handled by a compile-time split to a diagonal Minkowski basis (vsr_split_met.h). This is the same compile-time code-generation family as GATL, Gaalet (expression templates) and Gaalop (precompiler), which is why those four cluster within about 15% of each other while runtime-dispatched Garamon, TbGAL and GluCat are one to three orders of magnitude slower.

## Compared with alternatives

None of the catalogued geometry-spatial siblings is a geometric algebra library: they are predicates, triangulation, spatial indexes, mesh booleans and physics engines (CGAL, Boost.Geometry, nanoflann, Manifold, Jolt). Pick Versor only to express rigid-body and conformal transformations of points, lines, circles and spheres algebraically, and pair it with one of those siblings for spatial queries.

## Integration

| | |
|---|---|
| **Form** | static lib (product core is header templates in include/vsr; libvsr/vsr_shared are built with CMake from src/space/\*.cpp for CGA helper functions, and ga-benchmark links libvsr) |
| **Dependencies** | none for the math core; GLEW plus the ext/gfx submodule (GL/GLES, GLV/imgui) for graphics; ext/gtest submodule for tests |
| **Minimum toolchain** | C++11 (README: gcc 4.7+ or clang 3.2+), CMake 3.10, -ftemplate-depth-1200; clang 20.1.8 compile errors fixed in PR #33 (Nov 2025) |
| **Platforms** | README says tested on Linux and macOS; CMake also has Windows and Raspberry Pi (GLES) branches and a 2024 commit mentions an Android build; portable scalar C++ with no SIMD intrinsics in the core headers read |
| **Thread safety** | not documented; multivectors are plain value types over fixed arrays and no shared mutable state was seen in the core headers (only static basis constants) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the recorded medal table: ga-benchmark ranks by mean CPU time (USED_METRIC = 'cpu_time' in gabm.py), but on the WSL1 host the CPU clock advances in 15.625 ms ticks while each 10,000-call repetition takes only about 20-200 microseconds, so 89% of Versor's measured cases (92% of GATL's, 92-93% of Gaalop's and Gaalet's) record exactly 0.0 CPU time; golds are ties at zero (1,042 golds over 324 cases in my reproduction from the run's JSON files) and a silver means one tick happened to land in one of 30 repetitions (5.2e-05 ms = 15.625 ms / 10,000 / 30). Re-ranked by the high-resolution real_time stored in the same files, golds are GATL 111, Gaalet 76, Gaalop 55, Versor 23 (derived from page data).
- operator! computes \~A / (A \~A)[0], which is a correct inverse only for blades and versors, and silently returns the reverse when that scalar is 0; runit() returns a zero multivector for null input and norm() clamps negative weights to 0.
- Assigning between multivector types compiles and silently drops components: issue #20 (open) shows vector e1e2 = e1\*e2 yielding zero; use auto or the exact product type.
- operator&lt;= is the left contraction (zero when the left grade exceeds the right), not a symmetric dot product.

## Known shortcomings

- ga-benchmark compares only geometric algebra libraries (no Boost.Geometry, CGAL or GEOS) and its medal table gives no speed ratios; golds go to exact time ties (1,043 golds over 323 cases), so 246 vs GATL 247 is a tie; no CPU model, 2020 run on WSL1. The gafro IEEE RAM 2024 paper backs B (snippet only). Filed under numerics-and-science/geometry-spatial.
- Harness flaw in the ga-benchmark 2020-02-05 medal table: it ranks by mean CPU time, but the WSL1 CPU clock ticks every 15.625 ms while each 10,000-call repetition runs about 20-200 us, so 89% of Versor cases (92% GATL, 92-93% Gaalop/Gaalet) read exactly 0.0 and the golds are zero-time ties (1,042 over 324 cases, reproduced from 1,982 run JSONs; silver is one stray tick). Wall-clock real_time in the same files (derived): golds GATL 111, Gaalet 76, Gaalop 55, Versor 23; Versor geomean 0.88x GATL speed (GATL faster in 1,239 of 1,816 cases; IK 242 vs 857 ns), 0.96-0.98x Gaalop/Gaalet; Versor 18x faster than Garamon, 37x TbGAL, 162x GluCat framed, 2,588x GluCat matrix. The 'ties GATL for the lead' claim is unsupported; 'near the fastest GA template libraries' holds. Other: commutator is two geometric products (2.5x slower than GATL); operator! valid only for blades and versors; silent zeroing on implicit type conversion (issue #20); Rotor typedef wrong above 3D (#22); 5 of 12 binary ops missing from the harness.

## Caveats and trade-offs

Tier B: independent community suite (ga-developers/ga-benchmark, GPL-3.0, code public, run published in ga-benchmark-runs) but the context line gives no CPU model (8 x 1992 MHz, WSL1 kernel 4.4.0-18362-Microsoft) and no flags beyond CMake Release with GCC 7.4.0, and the run is from February 2020, so the Versor revision tested may differ from current devel. The result is a medal ranking against other geometric algebra libraries, not a speedup against the geometry-spatial category incumbents (Boost.Geometry, CGAL, GEOS) or any standard-library facility, and gives no time ratios. Medals are positions by exact equality of mean CPU time (gabm.py make_ranking), and 1,043 golds were awarded over 323 cases (derived from page data), so GATL, Versor, Gaalop and Gaalet share first place in most cases: a Versor gold means tied-fastest, not uniquely fastest, and its 246 golds vs GATL's 247 is a tie. Gaalop and Gaalet counts are depressed by 59 compilation-error faults each. The inverse-kinematics algorithm is excluded from the medal table (IGNORED_GROUPS). The gafro paper (Loew and Calinon, IEEE Robotics and Automation Magazine 2024, arXiv 2310.19090) forked ga-benchmark and states that GATL and Versor were previously reported to be the fastest GA libraries (read from search snippets only; arXiv and idiap.ch are blocked). The suite's install script clones github.com/wolftype/versor; the Versor README itself has no numbers (prose 'fast' and 'on steroids' only). [retier] Medal table ranks by CPU time on WSL1 (15.625 ms tick) while each repetition runs 20-200 us, so 89-93% of cases read 0.0 and golds are ties; wall-clock data shows Versor fourth behind GATL, Gaalet and Gaalop. Commutator is two geometric products; operator! only for blades/versors; silent zeroing on implicit conversion (#20); Rotor typedef wrong above 3D (#22); 5 of 12 binary ops missing from the harness.

Template-metaprogramming library for Euclidean, Conformal, Projective and Minkowski geometric algebras with arbitrary metrics; needs C++11 (gcc 4.7+, clang 3.2+); heavy compile times were reported as improved in the README; includes OpenGL drawing helpers; the lead developer's PhD project.

## Maintenance

Active on the default devel branch (last commit 2025-11-03 merging an outside contributor's clang 20 fixes; most 2024-2025 commits are graphics demos), BSD-2-Clause and usable as a math-only library, but its only independent speed evidence is a 2020 run whose CPU-time medal table is a timer-resolution artifact; the same run's wall-clock data support 'close to the fastest GA template libraries', not 'fastest'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** ranking_1.html in ga-developers/ga-benchmark-runs (2020.02.05) shows exactly the recorded medal counts from the independent community suite ga-developers/ga-benchmark (Google Benchmark, random arguments, DoNotOptimize, 30 repetitions); GCC 7.4.0 Release is stated but no CPU model and no explicit flags beyond CMake Release, so not A; a peer-reviewed gafro paper (IEEE RAM 2024, snippet only) also reports GATL and Versor as the fastest GA libraries, supporting B.
- **Verifier notes:** Medal table numbers match the page exactly; tier B confirmed. Main shortcomings: off-category baseline (other GA libraries, not Boost.Geometry/CGAL/GEOS), ranking without speed ratios where golds are mostly shared ties with GATL/Gaalop/Gaalet, no CPU model, 2020-era run on WSL1. Metadata checked: BSD-2-Clause, 327 stars, 54 forks, last commit 2025-11-03 on devel.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** ga-benchmark medal table (verifier); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark-runs/HEAD/2020.02.05/ranking_1.html>
  - <https://github.com/ga-developers/ga-benchmark-runs>
  - <https://github.com/ga-developers/ga-benchmark>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/HEAD/gabm.py>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/HEAD/Macros.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/HEAD/BinaryOperations.cpp>
  - <https://github.com/wolftype/Versor>
  - <https://github.com/wolftype/Versor/commits/devel>
- **Sources the enricher read:**
  - <https://github.com/wolftype/Versor>
  - <https://github.com/wolftype/Versor/commits/devel>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/README.md>
  - <https://raw.githubusercontent.com/wolftype/versor/master/README.md>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/copyrights/COPYRIGHT>
  - <https://github.com/wolftype/versor/tree/devel/include/vsr/detail>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/include/vsr/detail/vsr_multivector.h>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/include/vsr/detail/vsr_products.h>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/include/vsr/detail/vsr_instructions.h>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/include/vsr/detail/vsr_basis.h>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/include/vsr/detail/vsr_split_met.h>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/include/vsr/detail/vsr_algebra.h>
  - <https://raw.githubusercontent.com/wolftype/versor/devel/include/vsr/space/vsr_cga3D_op.h>
  - <https://github.com/wolftype/versor/issues?q=is%3Aissue>
  - <https://github.com/wolftype/versor/pulls?q=is%3Apr>
  - <https://github.com/wolftype/versor/issues/20>
  - <https://github.com/wolftype/versor/issues/22>
  - <https://github.com/wolftype/versor/issues/27>
  - <https://github.com/wolftype/versor/issues/29>
  - <https://github.com/wolftype/versor/pull/33>
  - <https://github.com/ga-developers/ga-benchmark>
  - <https://github.com/ga-developers/ga-benchmark/tree/master/source/Versor>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/source/Versor/SpecializedAlgebra.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/source/Versor/SpecializedBinaryOperations.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/source/Versor/SpecializedUnaryOperations.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/source/Versor/SpecializedUtils.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/source/Versor/SpecializedAlgorithmInverseKinematics.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/source/Versor/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/Macros.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/Types.hpp>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/gabm.py>
  - <https://raw.githubusercontent.com/ga-developers/ga-benchmark/master/README.md>
  - <https://github.com/ga-developers/ga-benchmark-runs>
  - <https://github.com/ga-developers/ga-benchmark-runs/tree/master/2020.02.05>
  - <https://github.com/ga-developers/ga-benchmark-runs/tree/master/2020.02.05/data>
  - https://raw.githubusercontent.com/ga-developers/ga-benchmark-runs/master/2020.02.05/data/ (1,982 readable result JSON files for all 8 solutions; one Gaalet file is truncated)
  - <https://gitlab.com/gafro>
  - WebSearch: gafro benchmark Versor GATL geometric algebra github results
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/wolftype/versor`) · [data/wave1/enrich/raw/github_com_wolftype_versor.json](../../../data/wave1/enrich/raw/github_com_wolftype_versor.json) (enrichment confidence 0.75)

</details>
