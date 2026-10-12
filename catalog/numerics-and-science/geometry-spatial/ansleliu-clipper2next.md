# clipper2next

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> C++23 rewrite of Clipper2 integer polygon clipping/offsetting with identical results, about 1.6x faster than Clipper2 (author's geomean).

| | |
|---|---|
| **Beats** | Clipper2 (AngusJohnson/Clipper2, called 'legacy Clipper2' in the README) |
| **Claimed result** | Release-gate results for version 5.0.1 against legacy Clipper2 (README). Linux (GCC 13.1, -O3): 14-pair geometric mean 1.615x; intersection 1.584x, union 1.669x, difference 1.694x, XOR 1.715x, offset 1.770x, triangulation 2.340x, Minkowski 1.454x, unprepared RectClip 1.247x (lowest). Windows (MSVC 19.44 /O2): geometric mean 1.758x, labelled directional because other benchmarks exceeded the 5% CV ceiling (intersection 1.487x, offset 1.563x, triangulation 2.878x, open-line RectClip 4.287x). The README says versions 6.1.x make no new performance claim. |
| **Workload** | Integer polygon boolean ops (intersection, union, difference, XOR), offsetting, triangulation, Minkowski, rect clip and PolyTree on an external benchmark corpus of 11 normalized profiles (2,426 cases); results first compared exactly against legacy Clipper2 with no coordinate tolerance. |
| **Metric** | throughput |
| **Compiler and flags** | Linux: GCC 13.1 -O3 -DNDEBUG; Windows: MSVC 19.44 /O2 /Ob2 /DNDEBUG; Google Benchmark 1.9.5, 7 repetitions of at least 0.5 s, pairwise process isolation, randomized pair order, 1 s warmup, 5% CV ceiling |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/ansleliu/clipper2next) · [benchmark](https://github.com/ansleliu/clipper2next) |

## Verdict

The author's 5.0.1 release gate ran Google Benchmark (7 repetitions, at least 0.5 s each, process isolation, randomized pair order, 5% CV ceiling) against a build of legacy Clipper2 on 11 external corpus profiles, after checking outputs matched exactly. Linux GCC 13.1 -O3 gave a 1.615x geometric mean over 14 operation families (1.25x unprepared RectClip to 2.34x triangulation); Windows MSVC 19.44 /O2 gave 1.758x but the author labels it noisy. The CPU is not named, and the 6.x releases carry no new speed claim.

## Use it when

- You already use Clipper2 on integer coordinates and want the same output bits faster: the author's Linux gate shows 1.4-1.8x on booleans, offset, PolyTree and Minkowski, and 2.3x on triangulation.
- Hot loops that clip many small polygons against rectangles or test overlapping boxes, where the rectangle/containment/disjoint-bounds fast paths skip the Vatti sweep.
- Services that want error codes rather than silent empty geometry: the checked APIs separate valid empty output from coordinate-range, scale, resource-limit and allocation failures.
- Pipelines that already own their geometry storage: borrowed input ranges and caller-provided output spans avoid converting to and from Paths64.
- Very large offsets (at least 512 paths and 524,288 points) when you can lend a 16-worker executor (README: 1.315x end-to-end on the Linux runner).

## Skip it when

- Toolchains without C++23 std::expected (older GCC/Clang/MSVC, many embedded SDKs): the library will not build.
- Floating-point or exact-rational geometry, curves/arcs, or OGC validity semantics: it is integer-only like Clipper2; GEOS, Boost.Geometry, CGAL or CavalierContours (arcs) cover those.
- When you need a battle-tested dependency: the repo is weeks old (8 commits, 1 star, no issue history), and it has broken ABI twice (SONAME 6 in 6.0.0, with no compatibility shim).
- When you need a third-party speed number: every figure is the author's own, with no CPU model and no raw JSON published, and the 6.x releases make no new speed claim.
- Code that relies on Clipper2's own API (Clipper64/ClipperD classes, InflatePaths and similar): there is no drop-in header.

## How it is fast

The core is still Clipper2's Vatti scanbeam sweep. It is reorganized around contiguous arrays: the intersection list for a scanbeam is built by a bottom-up merge sort over a std::vector of active-edge pointers, with an early exit when a pass is already ordered. Requests are pre-classified (metadata) so that rectangle-vs-rectangle union/intersection/difference/XOR, a containing-rectangle intersection and disjoint-bounds intersection skip the sweep entirely for EvenOdd/NonZero. Per-thread scratch buffers are retained between calls, results can be written into caller-owned storage, and the direct topology writer drops an intermediate ring-scratch copy (2,048 fewer point writes on the README's 256-group case). Large offset groups can fan out over a caller-supplied executor.

## Compared with alternatives

Pick it over CavalierContours when you need integer polygon booleans and Clipper2-identical offsets rather than arc-aware polyline offsetting. Pick it over TG or GeoRepair when your inputs are integer-scaled paths in a Clipper2 pipeline rather than OGC/GEOS-style geometries.

## Integration

| | |
|---|---|
| **Form** | shared lib (CMake add_library SHARED, SONAME 6) plus a header-only geotypes interface target; Conan recipe and vcpkg manifest provided |
| **Dependencies** | none at runtime; GoogleTest, Google Benchmark and legacy Clipper2 only for tests/benchmarks/oracle; Qt only for the optional demo |
| **Minimum toolchain** | C++23 with std::expected, CMake 3.24+, Ninja; tested with GCC 13 on Linux and MSVC (19.44 in the benchmarks) on Windows |
| **Platforms** | Linux and Windows tested; other platforms not documented. No -march flag in the build; the README mentions 'vectorized containment paths on supported CPUs' without saying how they are selected. |
| **Thread safety** | Not stated as a guarantee. The library keeps per-thread scratch caches (release_thread_caches() frees the calling thread's), which suggests independent calls on separate threads are intended, and a ThreadSanitizer preset exists. Parallelism inside a call happens only through a caller-supplied sync_bulk_executor_ref. |
| **Drop-in for the baseline** | partial: results are bit-identical to Clipper2 by contract, but the API (request structs, std::expected, clipper2next namespace) differs, so call sites must be rewritten |

## Gotchas

- Borrowed inputs (borrow_paths64) must stay alive and unchanged until execution returns; the library does not copy them.
- Thread-local scratch grows with the largest job a worker has seen; long-lived pool threads should call release_thread_caches() after bursts.
- The rectangle/containment fast paths apply only to EvenOdd/NonZero fill with preserve_collinear on and reverse_solution off; Positive/Negative fills always take the full sweep.
- Unchecked entry points assume the caller already validated coordinates; use the \*_checked variants to get coordinate_range errors instead of empty results.

## Known shortcomings

- No CPU model; derived from Clipper2 (is_fork_of set); numbers are from the 5.0.1 release gate and 6.x makes no speed claim.
- Always builds as a shared library with two ABI breaks (SONAME 6 in 6.0.0); no CPU stated; 1 star.

## Caveats and trade-offs

No CPU model is stated, so this falls short of tier A, and the raw benchmark JSON is not in Git. All numbers are the author's own, from the 5.0.1 release gate, against the author's build of 'legacy' Clipper2. The speedups are for the default/unprepared APIs, and the 6.x releases make no new speed claim. The author flags the Windows result as noisy. The code is derived from Clipper2 (per NOTICE.md), so this is a modernized fork that is faster than its parent. It requires C++23 (std::expected), which limits where it can be used. The repo is about four weeks old (first commit 2026-09-03, 8 commits) with one star. There is no comparison against Boost.Geometry, GEOS or CGAL.

Requires C++23 (std::expected), CMake 3.24 and Ninja; integer (Point64) geometry only, like Clipper2. Keeps Clipper2's result contract (strict equivalence) while adding prepared requests, borrowed input ranges, flat path sets and streaming topology output. The README says 6.x makes no new speedup claim.

## Maintenance

Very active (6.1.1, last commit 2026-09-30) but only about four weeks old with a single maintainer and one star; the BSL-1.0 license, inherited from Clipper2, allows vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Performance evidence' table gives per-family speedups over legacy Clipper2, with compiler and flags (GCC 13.1 -O3 -DNDEBUG; MSVC 19.44 /O2 /Ob2 /DNDEBUG) and Google Benchmark settings. The benchmark code is public in benchmarks/ (oracle/, product/, tools/; presets linux-gcc-oracle-benchmarks and msvc-oracle-benchmarks). No CPU model is stated anywhere I opened, only 'the Linux release runner', and the raw JSON is kept out of Git. That makes it first-party with partial methodology, so C.
- **Verifier notes:** All Linux and Windows ratios in the record match the README table. I added the provenance from NOTICE.md (derived from Clipper2; Clipper2 itself is not in the catalog, so this is not a duplicate) and the 5.0.1/6.x context. BSL-1.0, 1 star, last commit 2026-09-30 and not a GitHub fork all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `is_fork_of`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/README.md>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/NOTICE.md>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/LICENSE_1_0.txt>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/CMakePresets.json>
  - <https://github.com/ansleliu/clipper2next>
  - <https://github.com/ansleliu/clipper2next/commits>
  - <https://github.com/ansleliu/clipper2next/tree/main/benchmarks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/README.md>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/NOTICE.md>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/vcpkg.json>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/conanfile.py>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/src/clip/closed_clip_fast_path.cpp>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/src/clip/clip_execution_strategy.cpp>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/src/clip/engine/engine_intersections_contiguous.cpp>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/src/api/release_thread_caches.cpp>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/include/clipper2next/api/execution.h>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/include/clipper2next/api/memory.h>
  - <https://raw.githubusercontent.com/ansleliu/clipper2next/HEAD/include/clipper2next/api/error.h>
  - <https://github.com/ansleliu/clipper2next>
  - <https://github.com/ansleliu/clipper2next/issues>
  - <https://github.com/ansleliu/clipper2next/tree/main/benchmarks>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ansleliu/clipper2next`) · [data/wave8/enrich/raw/github_com_ansleliu_clipper2next.json](../../../data/wave8/enrich/raw/github_com_ansleliu_clipper2next.json) (enrichment confidence 0.7)

</details>
