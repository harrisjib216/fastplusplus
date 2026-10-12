# Nim in edin/raytracer (500x500 render) vs C and C++ with GCC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim port of a toy 500x500 ray tracer, timed at 130 ms vs 160 ms for the repo's GCC-built C and C++ ports.

| | |
|---|---|
| **Beats** | C (GCC) and C++ (GCC) ray tracers in the same repository, 160 ms each |
| **Claimed result** | README table: Nim 130 ms vs C (GCC) 160 ms, C++ (GCC) 160 ms and Fortran 160 ms, about 1.23x faster (derived from page data). With MSVC the C and C++ builds take 250 ms, so Crystal 190 ms, D (LDC) 210 ms and Rust 220 ms also beat the MSVC builds but not the GCC builds. |
| **Workload** | Ray tracer rendering a 500x500 scene, ported to many language and compiler combinations; the README table lists the time in ms. |
| **Metric** | latency |
| **Hardware** | AMD FX-8120 |
| **Compiler and flags** | At the time of the README table (per-language scripts at commit 80bb306, before the June 2026 move to projects.xml): Nim 'nim c -d:danger -d:lto -d:intpow -d:quake --passC:"-march=native"'; C 'g++ RayTracer.c -x c -O3' (no -march=native, no LTO); C++ 'g++ RayTracer.cpp -O2 -std=c++17 -s'. The current projects.xml keeps the same C and C++ commands (gcc RayTracer.c -O3 on Linux) and builds Nim with '-d:danger -d:lto -d:intpow --passC:"-march=native"' (no -d:quake). Compiler versions are not stated. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Source (README note): the Nim version uses the Quake inverse-square-root algorithm; no language mechanism is given. |
| **Adoption** | 61 stars |
| **Last commit** | 2026-06-18 |
| **Links** | [repository](https://github.com/edin/raytracer) · [benchmark](https://github.com/edin/raytracer) |

## Verdict

The README table (single runs on an AMD FX-8120, apparently Windows with MinGW g++ given the run.bat scripts and MSVC rows) shows the 500x500 render at 130 ms for Nim built with -d:danger -d:lto -d:intpow -d:quake -march=native against 160 ms for C (g++ -x c -O3) and C++ (g++ -O2 -std=c++17), about 1.23x (derived from page data), with the C and C++ rows dating from May 2020 and the Nim row from March 2021. Third-party points in the repo agree on direction but not size: the PR #4 author measured 55 ms (no math switches) and 37 ms (with them) against 74 ms for C++ on unstated hardware, and jzakiya (issue #11) measured C/C++ at 75-78 ms against fast Nim at 42-45 ms on an i7-6700HQ.

## Use it when

- As a template for fast scalar Nim code: compile-time-sized arrays, case objects instead of class hierarchies, and templates/macros for field-wise vector math compile to tight C with -d:danger.
- As evidence that a naive C++ design (virtual calls per object, std::optional copies, -O2) leaves performance on the table: the PR #4 author measured the Nim rewrite without the math switches at 55 ms against 74 ms for the C++ port (hardware not stated).
- Preview-quality rendering or geometry kernels where an inverse square root with about 0.2% error and integer-exponent pow are acceptable, if you copy the -d:quake and -d:intpow ideas consciously.
- Small single-threaded CPU-bound programs where you already use Nim and want a reference point that its C backend is not a handicap.

## Skip it when

- As proof that Nim beats C or C++ as a language: the programs differ in algorithm (approximate norm, integer pow), work per hit and build flags, and the rows were measured about a year apart.
- When output must match a reference image: with -d:quake the spheres come out slightly smaller than in the original Nim, C++ and D outputs (reported in issue #11).
- As a renderer: three objects, four lights, no acceleration structure, no threads or SIMD, no API; it is a benchmark sample.
- When you need a like-for-like comparison: no C build with -march=native and LTO, and no C++ build at -O3 with a switch-based design, has been timed in this repo.
- For current-hardware numbers: the table is from an AMD FX-8120 and has not been re-measured since the June 2026 move to projects.xml.

## How it is fast

Two of the three sources of the gap are not language features. First, approximate math behind compile switches: -d:quake replaces sqrt plus divide in norm() (every primary ray, sphere normal and light vector) with a bit-trick inverse square root (magic 0x5fe6eb50c7b537a9) and one Newton step, and -d:intpow replaces libm pow(specular, 250.0 or 150.0) with exponentiation by squaring; the PR's own commit is titled 'add unfair optimizations'. Second, build flags: Nim's generated C got -march=native and LTO, while C was built with g++ -x c -O3 and C++ with -O2. Third, a leaner program: the scene lives in fixed-size arrays of a generic Scene[T, L: static int] with a variant (case) object per shape, so there is no virtual dispatch (the C++ port calls virtual GetIntersection/GetNormal/GetSurface and copies std::optional&lt;Intersection&gt;), the shadow test returns only a distance (C copies a full Intersection with its Ray per hit), and surface properties and the normalized reflection direction are computed once per hit (C computes surface properties twice per hit and re-normalizes the reflection direction for every unshadowed light).

## Compared with alternatives

Among systems-and-safety siblings, the benchLANG Nim binary-trees entry measures Nim against C and C++ with matched -O3 -march=native -flto flags and the same algorithm on a dated 2026 run, so it is the stronger Nim data point; mosdepth and the c-blake tools (cligen/dents, procs, dups) are usable Nim programs that beat C tools, whereas this entry only shows that a carefully restructured Nim toy with approximate math beats an unoptimized C++ class-hierarchy port.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Nim standard library only (math, times, macros, os, strutils); Nim's C backend compiler (GCC in the measured setup) |
| **Minimum toolchain** | Not documented; the code dates from March 2021 (Nim 1.4 era) and was updated in June 2026; -d:lto needs a backend C compiler with LTO |
| **Platforms** | Any Nim target in principle; -march=native ties the binary to the build CPU and the quake trick assumes IEEE-754 binary64 layout |
| **Thread safety** | Not applicable: single-threaded program |
| **Drop-in for the baseline** | no |

## Gotchas

- Cross-run comparison: the C (GCC) and C++ (GCC) 160 ms rows first appear in the README of 1 May 2020 (commit 1ca4ffb, when Nim was listed at 1500 ms); the Nim row was set on 22 March 2021 after PR #4 (150 ms in 67da4de, then 130 ms in 8ea9877 the same day). The rows were never re-run together, compiler versions are not given, each is a single run rounded to 10 ms, and the three programs use different timers (Nim cpuTime, C clock(), C++ high_resolution_clock), all including scene setup.
- The 130 ms build used -d:quake and -d:intpow (approximate inverse square root, integer pow) plus -march=native and LTO; the PR author labelled these 'unfair optimizations', and the current projects.xml drops -d:quake but keeps -d:intpow, -march=native and LTO for Nim while C stays at plain -O3 and C++ at -O2.
- Latent bug in the Nim intersections template: in the plane branch, the closeness test (dist &lt; closest) runs before dist is assigned, so it compares the default 0.0 and accepts any plane hit; this is harmless only because the plane is the first object in the scene, and reordering the scene would make the plane occlude nearer spheres.
- The baselines have their own defects: the C Legalize() casts to uint8 before clamping, so channels above 1.0 overflow (undefined conversion) instead of saturating, and the README remark that the C++ port does bounds checking is not borne out by its source (no .at() calls).

## Known shortcomings

- Crippled baseline: the old nim/run.bat (commit 80bb306) built with -d:quake (approximate inverse sqrt), -d:intpow (integer pow instead of libm pow), -march=native and LTO while C was plain -O3 and C++ -O2; no compiler versions.
- Cross-run comparison: the C (GCC) and C++ (GCC) 160 ms rows first appear in README commit 1ca4ffb (2020-05-01, when Nim was listed at 1500 ms) and the Nim row was set to 150 ms (67da4de) then 130 ms (8ea9877) on 2021-03-22 after PR #4; the rows were never re-run together and each uses a different timer (cpuTime, clock(), high_resolution_clock). PR #4 carries a commit titled 'add unfair optimizations' (-d:quake, -d:intpow, -march=native), issue #11 reports the quake build draws slightly smaller spheres, and the PR author measured Nim 55 ms without those flags against 74 ms for C++ on unstated hardware (jzakiya on an i7-6700HQ: Nim 42-45 ms vs C/C++ 75-78 ms). Latent bug: the Nim intersections template tests the plane before dist is assigned, harmless only because the plane is first in the scene; C's Legalize() casts to uint8 before clamping, so bright channels overflow. Enricher confidence 0.2.

## Caveats and trade-offs

Not the same algorithm and not the same flags, so the 130 ms vs 160 ms gap is not a language win. The Nim build used -d:quake, which replaces 1/len in norm() with the Quake fast inverse square root (magic constant 0x5fe6eb50c7b537a9 plus one Newton step, an approximation that changes the output), and -d:intpow, which replaces the specular pow(specular, 250.0 or 150.0) with integer exponentiation by squaring, while the C and C++ versions call libm pow(double, double). On top of that, Nim was built with -march=native and -d:lto, while C got plain -O3 (compiled as C by g++ -x c on Windows) and C++ only -O2. Compiler versions are not stated, and the table is old (an FX-8120 CPU, Node 15 and PHP 8.0 rows, MSVC rows), so it is not tied to a dated run. The README comment that C++ does bounds checking is not borne out by the C++ source (no .at() calls). Only Nim beats the GCC C and C++ builds; D (LDC) 210 ms, Crystal 190 ms and Rust 220 ms lose to them and beat only the MSVC builds (250 ms). There is no repeat count or variance. [retier] Enricher: cross-run comparison; the C (GCC) and C++ (GCC) 160 ms rows first appear in README commit 1ca4ffb (2020-05-01, when Nim was listed at 1500 ms) and the Nim row was set to 150 ms (67da4de) then 130 ms (8ea9877) on 2021-03-22 after PR #4, never re-run together, each a single run rounded to 10 ms with a different timer (Nim cpuTime, C clock(), C++ high_resolution_clock). PR #4 carries a commit titled 'add unfair optimizations' (-d:quake, -d:intpow, -march=native); issue #11 reports the quake build draws slightly smaller spheres; the PR author measured Nim 55 ms without those flags against 74 ms for C++ on unstated hardware (jzakiya on an i7-6700HQ: Nim 42-45 ms vs C/C++ 75-78 ms). Latent bug: the Nim intersections template tests the plane before dist is assigned (harmless only because the plane is first in the scene); C's Legalize() casts to uint8 before clamping, so bright channels overflow.

Single small program per language; community-style ports.

## Maintenance

MIT-licensed, 61 stars, last commit 2026-06-18 (a new projects.xml-driven 'ray' wrapper), but the results table has not been refreshed since 2021 and the Nim file is a benchmark sample, not a maintained component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The readme.md table does show Nim 130 ms against C (GCC) 160 ms and C++ (GCC) 160 ms on an AMD FX-8120, but the build scripts show a tuned Nim build (-d:quake fast inverse sqrt, -d:intpow integer pow, -march=native, LTO) against plain C at -O3 and C++ at -O2 with libm pow. Under the crippled-baseline precedent (naive baseline against a tuned other-language version, unequal flags), the result is tier D. Compiler versions are not stated either.
- **Verifier notes:** Downgraded C to D under the crippled-baseline precedent: the README note 'Uses Quake square root algorithm' understates the asymmetry, because the pre-June-2026 nim/run.bat also enabled -d:intpow (integer pow replacing libm pow with exponent 250/150), -march=native and LTO, while C was built at plain -O3 and C++ at -O2. Shortcomings to record: different algorithm (approximate inverse sqrt, integer pow), unequal flags, no compiler versions, an undated old table on an FX-8120. Metadata checked: MIT, 61 stars, last commit 2026-06-18.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/projects.xml>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/nim/RayTracer.nim>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/c/RayTracer.c>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/c++/RayTracer.cpp>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/nim/run.bat>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/nim/build.bat>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/c/run.bat>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/c/run.sh>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/c++/run.bat>
  - <https://github.com/edin/raytracer>
  - <https://github.com/edin/raytracer/commits/master>
- **Sources the enricher read:**
  - <https://github.com/edin/raytracer>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/projects.xml>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/nim/RayTracer.nim>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/c/RayTracer.c>
  - <https://raw.githubusercontent.com/edin/raytracer/HEAD/c++/RayTracer.cpp>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/nim/run.bat>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/nim/build.bat>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/c/run.bat>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/c/run.sh>
  - <https://raw.githubusercontent.com/edin/raytracer/80bb306/c++/run.bat>
  - <https://raw.githubusercontent.com/edin/raytracer/ce357dd/nim/RayTracer.nim>
  - <https://raw.githubusercontent.com/edin/raytracer/e8794d0/nim/RayTracer.nim>
  - <https://raw.githubusercontent.com/edin/raytracer/3c4a9b1/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/02fed97/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/1ca4ffb/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/67da4de/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/8ea9877/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/c30d417/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/2a2b53a/readme.md>
  - <https://raw.githubusercontent.com/edin/raytracer/b5b8044/readme.md>
  - <https://github.com/edin/raytracer/commits/master/readme.md>
  - <https://github.com/edin/raytracer/commits/master/nim/RayTracer.nim>
  - <https://github.com/edin/raytracer/commits/master/c/RayTracer.c>
  - <https://github.com/edin/raytracer/issues?q=is%3Aissue>
  - <https://github.com/edin/raytracer/issues/5>
  - <https://github.com/edin/raytracer/issues/11>
  - <https://github.com/edin/raytracer/issues/38>
  - <https://github.com/edin/raytracer/pull/4>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:nim/edin/raytracer#render-500x500`) · [data/wave14/enrich/raw/lang_nim_edin_raytracer_render_500x500.json](../../../data/wave14/enrich/raw/lang_nim_edin_raytracer_render_500x500.json) (enrichment confidence 0.2)

</details>
