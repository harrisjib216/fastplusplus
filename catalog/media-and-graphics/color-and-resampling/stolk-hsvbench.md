# hsvbench (branchless HSV to RGB)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense` · 🔴 abandoned

> Branchless, expression-only HSV-to-RGB float function in a public-domain C header, about 5.7x faster than the textbook 6-way switch on random input.

| | |
|---|---|
| **Beats** | the repo's own hsv_to_rgb in hsv.h: the common 6-way switch formula seen in StackOverflow answers (calls double-precision floor() and branches on the hue sector); a naive in-repo baseline, not an incumbent library |
| **Claimed result** | Wall time of the run: standard 3.745 s, branchless 'fast' 0.655 s, table 1.865 s; README: 'Branchless HSV to RGB conversion pays off big time: I measured almost a factor 6' and the table lookup 'beats it by a factor 2' (about 5.7x and 2.0x, derived from page data). |
| **Workload** | 300 passes over 1,048,576 HSV triples from rand() (uniform random hue, saturation and value), converting to float RGB in a global array; three separate process runs (bench=standard, bench=fast, bench=table) each timed end to end with time, so setup (3M rand() calls, table init) is included in every figure. |
| **Metric** | throughput |
| **Hardware** | not stated |
| **Compiler and flags** | Makefile: clang-10 -std=c99 -D_GNU_SOURCE -O2 -g, linked with -lm (no -march); timed with the shell's time over the whole process |
| **Adoption** | 2 stars |
| **Last commit** | 2020-12-08 |
| **Links** | [repository](https://github.com/stolk/hsvbench) · [benchmark](https://github.com/stolk/hsvbench) |

## Verdict

On the author's unnamed CPU, with clang-10 -O2 (no -march), 300 passes over 1,048,576 random float HSV pixels took 3.745 s for the switch formula, 0.655 s for the branchless expression and 1.865 s for the lookup table, measured as whole-process wall time (about 5.7x and 2.0x, derived from page data). The baseline is the repo's own textbook switch, not a library, and no CPU model or repeat count is given.

## Use it when

- Per-pixel or per-vertex HSV-to-RGB in C or C++ code (colour pickers, procedural palettes, particle and heat-map colouring) where pulling in OpenCV or a colour library is overkill.
- Hot loops over float HSV data whose hues vary unpredictably from one element to the next, where the switch version mispredicts most.
- Code you want to auto-vectorise or port to SIMD intrinsics or shaders: the function is branch-free and uses only abs, min/max, multiply and add.
- Projects that need public-domain (Unlicense) code to paste in without attribution.

## Skip it when

- Whole-image 8-bit conversions: OpenCV cvtColor (COLOR_HSV2RGB) or a SIMD colour converter works on packed u8 buffers and threads; hsvbench never compares against any library.
- When you need bit-identical output with an existing switch implementation: 396 of 65,536 test pixels differ by 1 LSB in 8-bit (README ppmhist), partly because the bundled switch version scales hue by 5.9999 rather than 6.
- Hue values outside [0,1] or in degrees: the expression does not wrap (h = 1.2 clamps to pure red instead of hue 0.2), so wrap and normalise before calling.
- Spatially coherent real images, where the switch's branches predict well; the 5.7x was measured on uniformly random hues, the worst case for the baseline, so expect a smaller gain.
- Anyone wanting a maintained library: 7 commits on one day (2020-12-08), no tests, no issues or releases.

## How it is fast

Each channel is a piecewise-linear 'tent' of the hue: r = |6h-3|-1, g = 2-|6h-2|, b = 2-|6h-4|, each clamped to [0,1] and blended with saturation and value, so there is no sector index, no floor() and no switch. fabsf and the ternary clamp compile to andps and min/max instructions, so the loop body is straight-line float code with no data-dependent branches and is a candidate for compiler auto-vectorisation (not confirmed by disassembly in the repo). The baseline it beats branches six ways on the hue sector and calls double-precision floor() per pixel, which at -O2 without -march (no SSE4.1 round instruction on baseline x86-64) is typically a libm call (inference from the Makefile flags, not measured).

## Compared with alternatives

Pick this over OpenCV, CompV or DeltaCV when you need a single-pixel float HSV-to-RGB function to paste into C code rather than an image-wide cvtColor call; like fast-srgb8 it is a scalar per-value transform measured only against a naive reference, so for bulk 8-bit image conversion the library siblings remain the better-evidenced choice.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | libm (&lt;math.h&gt; must be included before hsv.h; the header uses fabsf, floor and powf without including it) |
| **Minimum toolchain** | C99 with the GNU __inline__ keyword (GCC or Clang); the Makefile uses clang-10 -std=c99 -O2. MSVC needs a #define for __inline__ (not documented). |
| **Platforms** | any (portable scalar float code; no intrinsics) |
| **Thread safety** | Not documented; the header functions are pure and stateless, so they are reentrant (from reading hsv.h). |
| **Drop-in for the baseline** | partial: same signature as the header's switch-based hsv_to_rgb(h, s, v, rgb), but outputs differ by up to 1 LSB in 8-bit and there is no image-level or integer API |

## Gotchas

- CLAMP01 is an unprefixed function-like macro that evaluates its argument up to three times and does not parenthesise the second use of x; it can collide with or misbehave beside other macros.
- hsv.h is not self-contained: include &lt;math.h&gt; first, and it defines generic names (hsv_to_rgb, hsl_to_rgb, linear_to_srgb) that may clash with other colour code.
- The benchmark times whole processes with time(1), including identical setup (3M rand() calls and table init) in each run; the fast run moves about 7.5 GB of array traffic in 0.655 s (about 11.5 GB/s, derived from page data), so it may be near single-core memory bandwidth and the compute-only ratio is not isolated.
- Building hsvbench.c at -O0 is likely to fail to link: hue_sat_val_lookup is a non-static C99 inline definition with no external definition; the -O2 Makefile build inlines it. The table benchmark also maps byte hue to h/256 while the reference uses h/255, so part of the table's visible error is a mapping mismatch.

## Known shortcomings

- The baseline is the repo's own 6-way switch hsv_to_rgb (double floor(), random hues), not an incumbent library; 3.745 s against 0.655 s is whole-process time with clang-10 -O2 and no CPU; 396 of 65536 pixels differ by 1 LSB.
- Enricher (e122, 2026-10-05): no correctness bug, only a 1-LSB output drift (the switch variant scales hue by 5.9999). Measurement flaws: the switch baseline calls double floor() per pixel (likely a libm call at -O2 without -march); uniformly random hues are the worst case for branches; the fast run moves about 7.5 GB in 0.655 s (about 11.5 GB/s, derived), so it is likely near single-core memory bandwidth. Gotchas: hsv.h needs &lt;math.h&gt; included first; GNU __inline__; an unprefixed multiple-evaluation CLAMP01 macro; no hue wrap; the table function in hsvbench.c is non-static C99 inline, so it likely fails to link at -O0. Tier C stands.

## Caveats and trade-offs

Public-domain (Unlicense) dedication carries no patent grant. The baseline is a naive in-repo function, not an incumbent library such as OpenCV or libswscale; with uniformly random hues its 6-way switch mispredicts heavily and it calls double-precision floor() per pixel, while the branchless expression is amenable to auto-vectorisation (no disassembly or counters given), so the 5.7x (derived from page data) reflects branch-free code against a branchy scalar loop on random data. Whole-process timing includes identical setup in each run, which slightly understates the per-function ratio. No CPU model; single compiler setting. The branchless output is not bit-identical: per the README ppmhist output, 396 of 65,536 test pixels differ by 1 LSB from the standard version; the table version is visibly inaccurate. The branchless formula comes from a Hacker News comment (item 21158888, not opened: HN blocked), so the repo is a measurement rather than the origin of the technique.

Branchless version is a short header function (hsv.h) usable from C and C++ and near identical output to the switch version; the table lookup version is faster than the switch but visibly inaccurate.

## Maintenance

Abandoned since 2020-12-08 (all 7 commits on one day, no issues or PRs), but Unlicense and only a 20-line function, so it is trivial to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows `time ./hsvbench` runs (standard 3.745 s, fast 0.655 s, table 1.865 s) from the public hsvbench.c and hsv.h built by the Makefile with clang-10 -O2, but no CPU model is given and the baseline is the repo's own 6-way-switch function, not a library, so first-party C.
- **Verifier notes:** Baseline confirmed as an in-repo naive switch, not an incumbent; numbers match the README exactly. Metadata on github.com: Unlicense, 2 stars, 0 forks, 7 commits, last commit 2020-12-08, abandoned.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party micro-benchmark
- **Pages the verifier opened:**
  - <https://github.com/stolk/hsvbench>
  - <https://github.com/stolk/hsvbench/commits>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/hsvbench.c>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/hsv.h>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/stolk/hsvbench>
  - <https://github.com/stolk/hsvbench/commits>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/hsvbench.c>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/hsv.h>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/stolk/hsvbench/HEAD/LICENSE>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/stolk/hsvbench`) · [data/wave10/enrich/raw/github_com_stolk_hsvbench.json](../../../data/wave10/enrich/raw/github_com_stolk_hsvbench.json) (enrichment confidence 0.8)

</details>
