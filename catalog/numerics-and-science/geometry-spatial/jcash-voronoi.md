# jc_voronoi

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Single-header C99 Fortune-sweep 2D Voronoi/Delaunay generator, 1.4-3.7x faster than Boost.Polygon voronoi on random points.

| | |
|---|---|
| **Beats** | Boost.Polygon voronoi_diagram (Boost 1.92.0); also jc_voronoi 0.9.0, and in older README prose Fastjet/Fortune C, O'Sullivan C++, voronoi++ |
| **Claimed result** | test/release-0.10.0-performance.md, median Voronoi generation time, jc_voronoi 0.10 vs Boost.Polygon 1.92.0: 1k random sites 178.00 us vs 649.83 us (about 3.65x, derived from page data); 10k 4.87 ms vs 6.82 ms (about 1.40x); 100k 53.95 ms vs 80.21 ms ('32.7% faster than Boost', about 1.49x); 100k pathological (issue48) 18.63 ms vs 39.25 ms ('52.5% faster', about 2.1x). Peak memory is close to Boost (104.0%, 95.2%, 98.4%, 78.4% of Boost's peak), retained memory 27.4% lower at 100k, and allocations per generation far fewer (1,187 vs 557,371 at 100k). The older README prose says Boost is '\~2x as slow as the fastest algorithms' and voronoi++ 10x-15x slower; its charts and test/report.md are gone (404). |
| **Workload** | 2D Voronoi diagram generation (Fortune sweep) from deterministic random point sets (1k, 10k, 100k sites, seed 4) and a 100k pathological symmetric diagonal-pair set (issue48); median time with diagram destruction included, plus peak/retained heap and allocation count; also code size and build time. |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max MacBook Pro, 128 GB RAM, arm64 macOS (0.10.0 release numbers); the older README numbers were on an Intel Core i7-7567U 3.50 GHz MacBook Pro, 16 GB LPDDR3 |
| **Compiler and flags** | Apple clang 21.0.0, -O3 -DNDEBUG, C++11 benchmark harness (per test/release-0.10.0-performance.md); note test/compile_perftest.sh at HEAD builds with clang++ -O2 -g |
| **Adoption** | 733 stars |
| **Last commit** | 2026-07-25 |
| **Links** | [repository](https://github.com/JCash/voronoi) · [benchmark](https://raw.githubusercontent.com/JCash/voronoi/dev/test/release-0.10.0-performance.md) |

## Verdict

The author's test/release-0.10.0-performance.md (Apple M5 Max, Apple clang 21.0.0, -O3 -DNDEBUG, medians with diagram destruction included) times jc_voronoi 0.10 against Boost.Polygon from Boost 1.92.0 at 178.00 us vs 649.83 us (1k random sites), 4.87 vs 6.82 ms (10k), 53.95 vs 80.21 ms (100k) and 18.63 vs 39.25 ms (100k pathological), with similar peak memory. The committed harness differs slightly from the published method: test/perftest.cpp seeds with srand(0) on a 4096-unit integer grid (the doc says seed 4), and compile_perftest.sh builds with -O2 -g, so reproducing the published numbers needs those settings changed.

## Use it when

- Games, procedural maps, stippling or Lloyd relaxation that need clipped Voronoi cells with ordered edge loops from thousands to a few hundred thousand points, in C or C++.
- Replacing Boost.Polygon voronoi_diagram when the sites are points and you want edges already clipped to a box or convex polygon, without Boost headers (0.17 s vs 0.97 s clean build and a 33.7 KB vs 150.6 KB minimal executable in the author's table).
- Allocation-sensitive or embedded code: jcv_diagram_generate_useralloc takes custom alloc/free callbacks, and generation does about a thousand allocations rather than hundreds of thousands.
- Inputs with heavy symmetry or collinear structure, where 0.10's RAVL beachline keeps O(n log n) behaviour (100k pathological case 18.63 ms vs Boost 39.25 ms).
- Browser or Node use via the npm jc-voronoi WebAssembly package when you need per-cell edge access.

## Skip it when

- Segment sites, medial axes or exact predicates: Boost.Polygon handles segment input with robust integer predicates; jc_voronoi is float-based Fortune on points and prunes duplicates and out-of-bounds points.
- Raw Delaunay or Voronoi speed in JavaScript: the repo's own BENCHMARKS.md has d3-delaunay generating 100k random diagrams in 31.54 ms against JCV-wasm's 98.21 ms, with lower memory.
- Upgrading from 0.9 just for speed on ordinary random input: at 100k random sites 0.9.0 (51.22 ms) is slightly faster than 0.10.0 (53.95 ms); 0.10 fixes worst-case scaling and memory instead.
- Clipping to non-convex boundaries: only box and convex-polygon clippers ship (open issue #50 asks for non-convex).
- Code that relied on the 0.9 API: 0.10 broke the edge API (jcv_graphedge, jcv_site.edges and jcv_diagram_get_next_edge removed) and changed struct layouts; see MIGRATION_GUIDE.md.

## How it is fast

It is Fortune's sweep-line algorithm with: an introsort specialized for jcv_site (y-then-x order; already-sorted input returns at once, reversed input is reversed in place); a binary-heap event queue specialized for half-edges; and, since 0.10, a rank-balanced relaxed AVL (RAVL) tree that indexes the beachline, replacing a linked scan that went quadratic on adversarial input (the 100k issue48 case fell from 9.15 s to 18.63 ms). Memory comes from a few large blocks (one up-front block for sites and events, then 16 KiB arenas), so a 100k diagram makes 1,187 allocations against Boost's 557,371. Per-site edge topology is built after the sweep from shared edges rather than per-site copies, and edges are sorted around each site by an overflow-safe pseudo-angle (0.10 changelog).

## Compared with alternatives

Choose it over Delaunay32 or detria when you need Voronoi cells with clipped, ordered edge loops in plain C, not a triangulation; Delaunay32 (multithreaded, beats delaunator-cpp and Triangle) and detria (constrained Delaunay) are faster or stronger when the Delaunay triangulation itself is the output. Against CGAL-based Voronoi, it trades exact predicates for a dependency-free single header.

## Integration

| | |
|---|---|
| **Form** | header-only (stb-style: define JC_VORONOI_IMPLEMENTATION in one translation unit); optional jc_voronoi_clip.h; CMake target jc_voronoi::jc_voronoi, Homebrew tap, npm WebAssembly package |
| **Dependencies** | none (libc math and stdlib only) |
| **Minimum toolchain** | C99 (C11, C17 and C23 supported); includable from C++; the benchmark harness is C++11 |
| **Platforms** | any; CI builds on macOS, Linux and Windows (MSVC build script provided); WebAssembly via Emscripten |
| **Thread safety** | not documented; the header has no mutable global state (only static const values), and each call allocates its own context, so separate diagrams on separate threads look independent (inferred from source, not stated) |
| **Drop-in for the baseline** | partial — covers point-site Voronoi (and Delaunay adjacency) with clipping included, but the API, coordinate type and output graph differ from Boost.Polygon's construct_voronoi/voronoi_diagram, and segment sites are not supported |

## Gotchas

- Sites come back sorted for the sweep, not in input order; use site-&gt;index to map back. The header comment on jcv_diagram_get_sites still says 'each index is the same as the original input point array', which contradicts the README and the 0.10 changelog.
- Duplicate points, points outside the rect, and points rejected by the clipper are silently dropped, so diagram.numsites can be lower than num_points; with a NULL rect the bounds are computed automatically with 10 units of padding.
- Default precision is float (JCV_REAL_TYPE); for large coordinate ranges or near-collinear input, switch to double by overriding JCV_REAL_TYPE, JCV_ATAN2, JCV_SQRT, JCV_FLT_MAX, JCV_REAL_TYPE_EPSILON and JCV_PI identically in every translation unit.
- Allocation failures are not checked (the context block is memset straight after allocfn returns), and the fixed-size event-queue bound is guarded only by assert; several crash, infinite-loop and memory-blowup issues (#83, #85, #91) were closed during the July 2026 0.10 work.

## Known shortcomings

- README's '2.5x Boost memory' claim is not borne out (peak memory within \~5%); compile_perftest.sh uses -O2 -g, not the -O3 the performance doc states.
- Committed harness differs from the published method: perftest.cpp uses srand(0) on a 4096 integer grid while the doc says seed 4; compile_perftest.sh uses -O2 -g while the doc says -O3 (seed 4 chosen to avoid a 0.9.0 bug). Own BENCHMARKS.md shows d3-delaunay \~3x faster than the JCV wasm build at JS generation (31.54 vs 98.21 ms, 100k). Header comment on site order contradicts README; 0.10 broke the API.

## Caveats and trade-offs

Single Apple M5 Max machine, author-run. On regular random inputs at 100k the older jc_voronoi 0.9.0 (51.22 ms) is slightly faster than 0.10.0 (53.95 ms); 0.10.0 mainly fixes pathological scaling (9.15 s to 18.63 ms). The release doc states -O3 -DNDEBUG while the committed compile_perftest.sh uses -O2 -g, so reproducing needs the stated flags. The README's older claim that Boost uses \~2.5x the memory is not borne out by the 0.10.0 data (peak memory within about 5% at random inputs). The README charts and test/report.md return 404. Boost.Polygon is not Boost.Geometry; Boost leaves edge clipping to the client.

Single C99 header, usable from C++; clips cell edges for you, exposes cell edge lists, supports Delaunay generation and custom allocators. Boost.Polygon's Voronoi handles segment sites; this library is point sites only.

## Maintenance

Active (0.10.0 released 2026-07-22, last commit 2026-07-25, 733 stars, 129 commits on dev) and MIT-licensed, so copyable; the 0.10 rewrite is recent and broke the API, so pin a version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: test/release-0.10.0-performance.md in the repo gives median timings of jc_voronoi 0.9/0.10 vs Boost.Polygon (Boost 1.92.0) with method stated (Apple M5 Max, Apple clang 21.0.0, -O3 -DNDEBUG, C++11 harness, seed 4, iteration counts), and the benchmark code is public (test/perftest.cpp built by test/compile_perftest.sh with -DUSE_JC_VORONOI / -DUSE_BOOST).
- **Verifier notes:** Found a much stronger numbers page than the record used: test/release-0.10.0-performance.md (0.10.0 released 2026-07-22 per CHANGELOG). Default branch is dev; last commit 2026-07-25; 733 stars; MIT confirmed from LICENSE.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `baseline`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/JCash/voronoi/HEAD/README.md>
  - <https://github.com/JCash/voronoi>
  - <https://github.com/JCash/voronoi/tree/dev/test>
  - <https://github.com/JCash/voronoi/commits/dev>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/test/release-0.10.0-performance.md>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/test/perftest.cpp>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/test/compile_perftest.sh>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/CHANGELOG.md>
  - <https://raw.githubusercontent.com/JCash/voronoi/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/JCash/voronoi>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/README.md>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/CHANGELOG.md>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/LICENSE>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/test/release-0.10.0-performance.md>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/test/perftest.cpp>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/test/compile_perftest.sh>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/src/jc_voronoi.h>
  - <https://raw.githubusercontent.com/JCash/voronoi/dev/src/jc_voronoi_clip.h>
  - <https://github.com/JCash/voronoi/issues>
  - <https://github.com/JCash/voronoi/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/JCash/voronoi/issues/91>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jcash/voronoi`) · [data/wave8/enrich/raw/github_com_jcash_voronoi.json](../../../data/wave8/enrich/raw/github_com_jcash_voronoi.json) (enrichment confidence 0.8)

</details>
