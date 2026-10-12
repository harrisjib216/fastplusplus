# Hob3l

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🟡 stale

> C command-line tool that turns SCAD/CSG models into layered STL for 3D printing, 50-350x faster than OpenSCAD's CGAL render.

| | |
|---|---|
| **Beats** | OpenSCAD with CGAL rendering (CGAL Nef polyhedron 3D CSG) converting SCAD/CSG to STL |
| **Claimed result** | README: x-carriage.csg to STL 45.208 s (openscad) vs 0.824 s (hob3l), about 50x faster; extruder-body.scad 2m42s vs 1.24 s, 130x; uselessbox+body 53.433 s vs 0.610 s, 85x. test31b.scad (\$fn=99 ellipsoids) 4m30.198s vs 0.748s, 350x. Repo title says '100x Faster Slicing of SCAD Files'. |
| **Workload** | Converting Prusa i3 MK3 part and personal SCAD models to STL by slicing into 0.2 mm layers (Hob3l) versus full 3D CSG rendering in OpenSCAD with CGAL. |
| **Metric** | latency |
| **Adoption** | 265 stars |
| **Last commit** | 2024-06-23 |
| **Links** | [repository](https://github.com/moehriegitt/hob3l) · [benchmark](https://github.com/moehriegitt/hob3l) |

## Verdict

First-party `time` wall-clock runs from the README: OpenSCAD's CGAL 3D CSG render vs Hob3l at 0.2 mm layers on two Prusa i3 MK3 parts and two of the author's own models (45.2 s vs 0.82 s, 2m42s vs 1.24 s, 53.4 s vs 0.61 s including a 23 MB STL write, and 4m30s vs 0.75 s). No CPU, compiler, flags or OpenSCAD version is stated, the outputs differ in kind (layered vs solid), and per GitHub's blame view the timings date from October 2018, before the April 2023 'replace core by robust integer arithmetics' rewrite.

## Use it when

- OpenSCAD's F6/CGAL render of a model for FDM printing takes tens of seconds to minutes and you only need a printable STL; the README shows 45.2 s to 0.82 s (x-carriage) and 4m30s to 0.75 s (test31b with \$fn=99 ellipsoids)
- Models built mainly from unions, differences and intersections of high-facet primitives, where CGAL time grows quickly and Hob3l's per-layer 2D work stays under a second
- Edit-and-reload prototyping: write SCAD in an editor, run Hob3l to WebGL/JS (about 0.65 s for the README's curry.scad) and reload a browser viewer
- Inputs where CGAL reports 'object may not be a valid 2-manifold' on coincident faces: Hob3l's integer arithmetic and snap rounding are built to produce valid 2-manifold output there

## Skip it when

- You need a single exact 3D solid (for CAD export, FEM, machining or further mesh booleans): output is separate stacked layers with visible stair-stepping, and Slic3r's split makes it many objects
- Models that rely on 3D hull(), minkowski(), offset(), resize() or render(): hull() is 2D only, projection() supports cut=true only, and SCAD variables, functions and modules must first be flattened by OpenSCAD's .csg export
- Long-running or embedded use: the author says memory leaks are not fixed because the tool starts, allocates and exits
- macOS: issue #11 (open, 'help wanted') reports a segfault slicing a .scad file there; development and testing are on Linux, with MinGW cross builds
- Comparing against current OpenSCAD: the timings are against its CGAL render path from the 2018 era, not OpenSCAD's newer Manifold backend

## How it is fast

It reverses OpenSCAD's 'compute the 3D CSG, then slice' order: each primitive polyhedron is cut into polygons at every layer height first, and the booleans are then done per layer in 2D, which avoids CGAL's Nef-polyhedron 3D booleans entirely. The 2D clipping is a Bentley-Ottmann plane sweep extended with Martinez-Rueda-Feito rules for overlapping edges, evaluating many polygons at once through a boolean function stored as a bit array. Coordinates are 32-bit integers (default unit 1/8192 mm), intersection points use a fixed 160-bit exact fraction instead of a generic bignum library, and de Berg's snap rounding brings results back to input precision before Hertel-Mehlhorn triangulation.

## Compared with alternatives

Pick Hob3l over Manifold, MeshLib or kigumi only when the goal is a printable layered STL from SCAD and you never need the exact 3D boolean result; those siblings compute real mesh booleans (Manifold is also what newer OpenSCAD builds can use instead of CGAL) and are the choice when the solid itself matters.

## Integration

| | |
|---|---|
| **Form** | CLI executable (hob3l) plus static libraries (hob3lbase, hob3lop, hob3lmat, hob3l) with installable headers; no documented library API |
| **Dependencies** | none beyond a C compiler, libc/POSIX, GNU make and Perl (Perl scripts generate C code at build time); OpenSCAD is optional as a .scad-to-.csg preprocessor |
| **Minimum toolchain** | C11 (-std=c11) with GCC extensions (statement expressions, __typeof__); GCC or Clang, MinGW for Windows cross builds |
| **Platforms** | Linux (development platform); Windows via MinGW cross-compile (win32/win64 targets); 32- and 64-bit x86 gcc targets; macOS has an open segfault report (#11) |
| **Thread safety** | not documented (single-threaded command-line tool) |
| **Drop-in for the baseline** | partial: replaces the `openscad model.csg -o model.stl` CGAL render step for printing, but reads only a SCAD subset and produces layered rather than solid 3D output |

## Gotchas

- \$fa and \$fs are accepted but ignored (only \$fn is used), so circle and sphere faceting can differ from OpenSCAD's output
- Stricter parser than OpenSCAD: arguments the OpenSCAD docs call mandatory are rejected when missing, where OpenSCAD silently defaults them
- The default build (MODE=normal) is -O2 with runtime checks on (NDEBUG off); MODE=release gives -O3 and -DNDEBUG. The README's '-march=native' default actually applies only in MODE=devel
- Input polyhedra with holes (missing faces) are not supported (README). Separately, users hit the assertion 'Odd number of edges meet in one point' (issues #5 and #9, both closed)

## Known shortcomings

- No hardware or versions; layered output, not like-for-like with full 3D CSG; author admits memory leaks; stale.
- Speed timings date from Oct 2018, before the April 2023 core rewrite to robust integer arithmetic, so they are not reproducible on current code. Open macOS segfault #11; author acknowledges memory leaks. Baseline is OpenSCAD's CGAL path, not CGAL itself, and output is layered (not like-for-like). Default build is -O2 with asserts; -march=native applies only to devel mode.

## Caveats and trade-offs

Wall-clock `time` figures on unspecified hardware and flags, against an unstated OpenSCAD version. The speedups above 50x come from a different algorithm (slice first, then 2D booleans) with layered output, so they are not like-for-like with CGAL mesh booleans; the README shows the layered STL and says the final slicer result is the same. The baseline is OpenSCAD's CGAL rendering path, not CGAL used directly, and OpenSCAD's newer Manifold backend is not compared. The 85x uselessbox figure includes writing a 23 MB STL (loading and converting alone take 0.23 s). Only a subset of SCAD is read, so full SCAD needs OpenSCAD as a preprocessor. The author admits memory leaks ('Memory management has leaks. I admit I don't care enough'). The core 2D library was fuzzed with afl. Last commit June 2024.

Different pipeline, not a general CGAL replacement: it slices the model into 2D layers and does 2D boolean operations with integer arithmetic and snap rounding, so output is a layered STL (visible layering artifacts) rather than an exact 3D mesh. Reads flat .csg from OpenSCAD plus STL/SVG import. GPL-3.0.

## Maintenance

Stale single-author hobby project (last commit 2024-06-23, 341 commits, no releases shown, 4 open issues) under GPL-3.0, so linking it into proprietary code is not an option, though the standalone CLI is easy to build with no third-party libraries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'Speed comparison' section gives first-party `time` wall-clock figures for hob3l against OpenSCAD's CGAL 3D CSG rendering on four models. It states no hardware, compiler, flags or OpenSCAD version, and has no benchmark script. With unstated flags and gains above 50x, the cap is C.
- **Verifier notes:** All four timings in the record match the README verbatim (45.208 s vs 0.824 s, 2m42s vs 1.24 s, 53.433 s vs 0.610 s, 4m30.198s vs 0.748 s). Metadata from github.com: GPL-3.0 (LICENSE file), 265 stars, 17 forks, 341 commits, last commit 2024-06-23, so stale is right. Shortcoming worth recording: the author admits memory leaks.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/moehriegitt/hob3l>
  - <https://github.com/moehriegitt/hob3l/commits>
  - <https://raw.githubusercontent.com/moehriegitt/hob3l/HEAD/README.md>
  - <https://raw.githubusercontent.com/moehriegitt/hob3l/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/moehriegitt/hob3l>
  - <https://github.com/moehriegitt/hob3l/commits>
  - <https://github.com/moehriegitt/hob3l/tree/master/include>
  - <https://github.com/moehriegitt/hob3l/issues?q=is%3Aissue>
  - <https://github.com/moehriegitt/hob3l/issues/11>
  - <https://github.com/moehriegitt/hob3l/issues/4>
  - <https://github.com/moehriegitt/hob3l/blame/master/README.md>
  - <https://raw.githubusercontent.com/moehriegitt/hob3l/HEAD/README.md>
  - <https://raw.githubusercontent.com/moehriegitt/hob3l/HEAD/Makefile>
  - <https://raw.githubusercontent.com/moehriegitt/hob3l/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/moehriegitt/hob3l/HEAD/doc/scadformat.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/moehriegitt/hob3l`) · [data/wave8/enrich/raw/github_com_moehriegitt_hob3l.json](../../../data/wave8/enrich/raw/github_com_moehriegitt_hob3l.json) (enrichment confidence 0.75)

</details>
