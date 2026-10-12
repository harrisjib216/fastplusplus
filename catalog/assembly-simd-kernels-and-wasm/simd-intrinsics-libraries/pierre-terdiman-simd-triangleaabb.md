# SIMD_TriangleAABB (SIMD triangle-box overlap test)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> SSE version of Akenine-Moeller's triangle-vs-AABB SAT overlap test; about 2x on full tests, 20x with an added early exit.

| | |
|---|---|
| **Beats** | Moeller's scalar triangle-box overlap code ('old code', and the 'new, faster code' variant) from Tomas Akenine-Moeller's page |
| **Claimed result** | README, vs Version1 (old code): best case 20.617886x, worst case 1.987882x, no hit 2.896657x, mixed 3.295337x; vs Version2: 26.198313x, 2.587267x, 4.126582x, 3.375974x. Times: default 5072/3773/953/5088 vs optimized 246/1898/329/1544. |
| **Workload** | Triangle-vs-AABB overlap tests in four scenarios (best case, worst case, no hit, mixed), time in the program's own units, SSE implementation with an extra early exit. |
| **Metric** | throughput |
| **Hardware** | 'my test PC' (Windows-based machine, CPU not stated) |
| **Compiler and flags** | SIMD_TriangleAABB.vcproj (Visual Studio 2008 format, Version 9.00) Release config: /O2 /Ob2 /Oi /Ot /Oy /GT /GL /arch:SSE2 /fp:fast, Win32 (the timer is MSVC inline __asm cpuid+rdtsc, so 32-bit x86 only); the README does not say which configuration or compiler version produced the numbers |
| **Adoption** | 14 stars |
| **Last commit** | 2021-09-08 |
| **Links** | [repository](https://github.com/Pierre-Terdiman/SIMD_TriangleAABB) · [benchmark](https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/README.md) |

## Verdict

One rdtsc run per scenario by the author on an unnamed Windows PC (Visual Studio 2008 Win32 Release project with /O2 /arch:SSE2 /fp:fast; compiler version and CPU not stated), 16384 triangles per scenario, compared with his lightly edited copy of Akenine-Moeller's 'old' scalar tribox code. Results: 1.99x when every test runs (worst case), 2.90x on no-hit, 3.30x on the mixed set, and 20.6x in the best case, which comes from the added v0-inside-box exit rather than SIMD width. Against the 'new, faster' variant the ratios are 2.6-26.2x, because that variant ran slower on his machine.

## Use it when

- Mesh-vs-box queries in collision detection, BVH or octree builds and voxelization on x86 with SSE2, one triangle per call.
- Workloads where many triangles have their first vertex inside the box (small triangles against larger boxes or cells), where the added exit costs about 15 rdtsc ticks per test against about 317 for the scalar code on the author's machine (derived from page data).
- Vertex buffers you control and can pad so that 16 bytes are readable at every vertex, box centre and extents address.
- As a known-good reference when writing or checking your own SIMD triangle-box test; its author notes that most other SIMD ports he benchmarked were slower than the scalar code.

## Skip it when

- You need a licence: the repo has none (only a tip-jar link). The same routine ships, maintained and licensed, as Gu::intersectTriangleBox_Unsafe in NVIDIA PhysX (BSD-3 header in NVIDIAGameWorks/PhysX 4.x, SPDX Apache-2.0 in the current NVIDIA-Omniverse/PhysX source).
- Tightly packed 12-byte vertices whose last element ends at the buffer end, or vertices followed by non-float data: every load reads 4 bytes past the Point.
- Non-x86 targets: raw SSE intrinsics with no NEON or scalar fallback (PhysX's version goes through its portable aos vector layer).
- Large batches where a structure-of-arrays kernel testing 4-16 triangles per instruction (ISPC, AVX2 or AVX-512) would use the lanes better: here the w lane is idle and only 3 axes are tested per vector op.
- Exact boundary semantics: the early exit uses a strict inside test, and the benchmark was built with /fp:fast and flush-to-zero.

## How it is fast

Each group of SAT axes is evaluated in one 128-bit SSE register: the triangle's AABB against the box on x, y, z at once (minps/maxps plus one movemask), the plane test with sign-masked extents, and the 9 'class III' edge axes as three calls that each test 3 axes for all three vertices. Data-dependent min/max swap branches of the scalar code become minps/maxps, while early exits are kept (cheap AABB and plane rejections first, edge axes last). An extra first exit returns 'overlap' when vertex v0 lies strictly inside the box (abs, subtract, sign-bit movemask), which accounts for the 20x best case.

## Compared with alternatives

No sibling solves triangle-box overlap: the catalogued neighbours are general SIMD toolkits (EVE, Vector Class Library, ISPC) that you would use to write a batched, many-triangles-per-call version. Pick this for a ready single-call SSE SAT test, and take the PhysX copy (portable, 3-lane dot, licensed) for shipping code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond &lt;xmmintrin.h&gt;/&lt;emmintrin.h&gt; and the repo's 12-byte Point struct (stdafx.h) |
| **Minimum toolchain** | Kernel: any compiler with SSE intrinsics, but it uses MSVC-specific __forceinline and __declspec(align(16)), so GCC or Clang needs small macro shims. Harness: Visual Studio 2008 project (Version 9.00), Win32 only (inline __asm cpuid/rdtsc, __control87_2). |
| **Platforms** | x86 or x86-64 with SSE (SSE2 enabled in the project); benchmark harness 32-bit Windows only |
| **Thread safety** | Reentrant from code reading: a pure function using only constant static tables; not documented. |
| **Drop-in for the baseline** | partial: same arguments and result as the scalar Akenine-Moeller test (hit counts matched in all four scenarios), but needs 4 readable bytes after each Point argument, and the w lane must hold a finite float |

## Gotchas

- Out-of-bounds read: LoadU is _mm_loadu_ps(&v.x) on a 12-byte Point, so every vertex, centre and extents load reads 4 extra bytes. The harness itself does this on the last vertex of gTris = new Point[16384\*3], reading past the heap allocation. PhysX names its copy intersectTriangleBox_Unsafe and notes 'all params must be safe to V4LoadU'.
- Latent correctness bug: DotV sums all four lanes, so the plane test includes the garbage w lanes. If those 4 bytes after a vertex or the centre hold NaN or Inf, or their products overflow, the dot products become NaN and the plane test silently never rejects, giving false 'overlap' results. PhysX's version uses a 3-lane V4Dot3 instead. Hit counts matched in the author's run, so the published numbers are not affected.
- The added early exit fires when v0 alone is strictly inside the box, not 'when the box fully contains the triangle' as the README says. That is still a correct overlap answer, but only vertex slot 0 is checked; the 'worst case' generator places v0 outside on purpose. PhysX's version uses an inclusive (&gt;=) comparison.
- Harness: each scenario is one cpuid+rdtsc sample (Time/1024 over 16384 tests) with no warm-up or repetition, and all scalar runs come before the SIMD ones. The scalar best case costs 5072 units against 3773 for the worst case, although both follow the same no-early-exit path, which suggests vertex-order-dependent branch mispredictions in the baseline. The 1.99x worst-case row (about 236 vs 119 ticks per test, derived from page data) is the clean SIMD-only figure.

## Known shortcomings

- VS2008 flags (/O2 /arch:SSE2 /fp:fast /GL, Win32) with no CPU and single-shot rdtsc timing; the 20x best case comes from an extra early exit absent from the Moeller baseline; no licence (reference).
- Latent correctness bug: LoadU is _mm_loadu_ps on a 12-byte Point, so every vertex load reads 4 bytes past the struct (the harness itself reads past the end of gTris), and the 4-lane DotV feeds that garbage w lane into the plane test, so a NaN or Inf there silently disables rejection and gives false overlaps; hit counts matched in the author's run, so the published numbers stand. Harness: one rdtsc sample per scenario with no warm-up, all scalar runs before the SIMD ones; the scalar best case costs 5072 vs 3773 for the worst case on the same code path, so the 1.99x worst-case row is the clean SIMD figure; the early exit checks v0 only, not 'triangle fully inside' as the README says. A licensed, maintained copy exists as NVIDIA PhysX Gu::intersectTriangleBox_Unsafe (GuIntersectionTriangleBox.cpp, V4Dot3; BSD-3 in NVIDIAGameWorks/PhysX, Apache-2.0 SPDX in NVIDIA-Omniverse/PhysX).

## Caveats and trade-offs

Numbers are a copy of the author's blog post (codercorner.com/blog/?p=1118, not reachable here, post date unchecked) with no CPU stated. The harness takes one rdtsc reading (cycles/1024) per scenario over 16384 triangles, with no repetition or warm-up, and runs all four default-code scenarios before the optimized ones. The 20x best case comes from an extra early exit (vertex v0 inside the box, a point-in-AABB test) that the scalar baseline lacks and that scalar code could equally add; it is not SIMD throughput. Typical gains are 2x to 3x (author says so); hit counts match between versions (16384/16384, 16384/16384, 0/0, 12420/12420). Baseline is the author's 'more or less verbatim, not quite' copy of Akenine-Moeller's old and new tribox code, and the 'new, faster' version was slower on his machine. The harness needs MSVC (inline asm, _control87_2); the SSE kernel in TriBox_Optimized.cpp uses portable SSE intrinsics. No licence file (author asks for a tip jar), so code is reference only.

SSE (128-bit) code; keeps branches and early exits instead of branchless SIMD; theoretical maximum from 4-wide SIMD is 4x, the 20x best case comes from an added early exit.

## Maintenance

Abandoned upload (6 commits, all on 2021-09-08, of code first released on the author's codercorner blog), with no licence, so reference only. A maintained and licensed descendant with the w-lane dot fixed lives in NVIDIA PhysX as Gu::intersectTriangleBox_Unsafe.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README reproduces the author's own run of SIMD_TriangleAABB/SIMD_TriangleAABB/SIMD_TriangleAABB.cpp against Akenine-Moeller's scalar tribox code (both versions); the VS2008 project gives Release flags but the README names no CPU or compiler version, so first-party C.
- **Verifier notes:** All README times and speedups match the record. Shortcomings: no CPU or compiler version, single-shot rdtsc timing, best-case 20x is an algorithmic early exit absent from the baseline rather than SIMD, no licence (reference only), 32-bit MSVC-only harness. Metadata checked: 14 stars, 6 commits all on 2021-09-08 (abandoned), no licence shown, not a fork. Could also sit in wave 8 geometry-spatial.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-112 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/README.md>
  - <https://github.com/Pierre-Terdiman/SIMD_TriangleAABB>
  - <https://github.com/Pierre-Terdiman/SIMD_TriangleAABB/commits>
  - <https://github.com/Pierre-Terdiman/SIMD_TriangleAABB/tree/main/SIMD_TriangleAABB>
  - <https://github.com/Pierre-Terdiman/SIMD_TriangleAABB/tree/main/SIMD_TriangleAABB/SIMD_TriangleAABB>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/SIMD_TriangleAABB.cpp>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/SIMD_TriangleAABB.vcproj>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/ReadMe.txt>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/TriBox_Optimized.cpp>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/Random.h>
- **Sources the enricher read:**
  - <https://github.com/Pierre-Terdiman/SIMD_TriangleAABB>
  - <https://github.com/Pierre-Terdiman/SIMD_TriangleAABB/tree/main/SIMD_TriangleAABB/SIMD_TriangleAABB>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/README.md>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/SIMD_TriangleAABB.cpp>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/TriBox_Optimized.cpp>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/TriBox_Default.cpp>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/TriBox.h>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/stdafx.h>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/stdafx.cpp>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/targetver.h>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/Random.h>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/Random.cpp>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/ReadMe.txt>
  - <https://raw.githubusercontent.com/Pierre-Terdiman/SIMD_TriangleAABB/HEAD/SIMD_TriangleAABB/SIMD_TriangleAABB/SIMD_TriangleAABB.vcproj>
  - <https://raw.githubusercontent.com/NVIDIA-Omniverse/PhysX/HEAD/physx/source/geomutils/src/intersection/GuIntersectionTriangleBox.cpp>
  - <https://raw.githubusercontent.com/NVIDIAGameWorks/PhysX/HEAD/physx/source/geomutils/src/intersection/GuIntersectionTriangleBox.cpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/pierre-terdiman/simd_triangleaabb`) · [data/wave13/enrich/raw/github_com_pierre_terdiman_simd_triangleaabb.json](../../../data/wave13/enrich/raw/github_com_pierre_terdiman_simd_triangleaabb.json) (enrichment confidence 0.75)

</details>
