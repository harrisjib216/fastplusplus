# JavaScript (browser JIT engines and Node.js) in Fourmilab floating_point_benchmarks: fbench

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `JavaScript` · `CC-BY-SA-4.0` · 🔴 abandoned

> 2017 run of John Walker's fbench: Firefox 55 beat GCC 5.4.0 -O3 C by 2.7x through SpiderMonkey's trig memo cache, while the V8 engines lost to C by 1.33-1.50x.

| | |
|---|---|
| **Beats** | C fbench (src/c/fbench.c, glibc libm trig functions) built with GCC 5.4.0 'gcc -Wall -O3 -lm' (src/c/Makefile, no -march), 166,051,660 iterations, mean 296.536 s, 1.7858 us per iteration on a Dell laptop under Xubuntu (src/javascript/README says the comparisons were made against GCC 5.4.0; the fbench.html table labels the C row 'GCC 3.2.3 -O3'). |
| **Claimed result** | fbench.html relative time (C = 1): Firefox 55.0.2 0.372, Safari 11.0 0.424, Brave 0.18.36 1.334, Chrome 61 1.378, Chromium 60 1.386, Node.js v6.11.3 1.495. src/javascript/README: Firefox 457,577,013 iterations, five runs averaging 303.863 s (the README prints 'mean of 393.863', a typo; derived from the listed runs) = 0.6641 us/iteration, ratio 0.3719 (about 2.7x faster than C, derived from page data); Safari measured 1.6865 us/iteration on a 2008 Mac Pro and multiplied by a Perl-derived speed ratio of 0.4487 to an estimated 0.7567 us/iteration, ratio 0.4237 (estimate, not a same-machine run); the four V8 engines are 1.33-1.50x slower than C. |
| **Workload** | fbench, a trigonometry-heavy optical ray-tracing kernel; run time per iteration relative to the C version on the same machine, iteration counts adjusted to about five minutes, single-threaded. |
| **Metric** | latency |
| **Hardware** | Dell laptop running Xubuntu Linux (CPU model not stated) for C, Firefox and the V8 engines; Safari ran on a 2008 Mac Pro (CPU not stated) and was rescaled with a Perl-measured speed ratio of 0.4487. |
| **Compiler and flags** | C: GCC 5.4.0, 'gcc -Wall -O3 -lm' without -march, glibc libm. JavaScript: Firefox 55.0.2 (SpiderMonkey; the README wrongly calls it Rhino), Safari 11.0 (11604.1.38.1.7, JavaScriptCore) on macOS, Brave 0.18.36, Chrome 61.0.3163.91, Chromium 60.0.3112.113 and Node.js v6.11.3 (all V8), default engine settings, src/javascript/fbench.js unchanged from 2005 apart from strict-mode declarations. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 6 stars; fbench has been ported to many languages since 1980 |
| **Last commit** | 2021-09-24 |
| **Links** | [repository](https://github.com/Fourmilab/floating_point_benchmarks) · [benchmark](https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/Web_pages/fbench.html) |

## Verdict

In October 2017, on a Dell laptop under Xubuntu (CPU not named), fbench.js in Firefox 55.0.2 averaged 0.6641 us per iteration (five runs of 457,577,013 iterations, about 304 s each). The C version built with GCC 5.4.0 'gcc -Wall -O3 -lm' averaged 1.7858 us, for a ratio of 0.372 (about 2.7x). Chrome 61, Chromium 60, Brave 0.18.36 and Node.js v6.11.3 (all V8) were 1.33-1.50x slower than C, and Safari 11's 0.424 is a 2008 Mac Pro run rescaled by a Perl speed ratio.

## Use it when

- As a cautionary example when reading JIT-versus-C claims on maths-heavy code: check whether the engine memoises transcendental functions and whether the benchmark repeats its arguments.
- As a small, self-validating, trig-heavy test of a JavaScript engine's Math accuracy: fbench.js compares its output with the C reference strings and reports any mismatch.
- To compare JavaScript engines with each other on one machine: on the 2017 laptop the four V8-based engines (Brave, Chrome, Chromium, Node.js) landed within 1.33-1.50x of C.

## Skip it when

- As evidence that JavaScript JITs beat C on floating-point code: the only same-machine win is Firefox 55's cache hits, and every V8 engine was slower than C.
- For current engines: every number is from October 2017 (Firefox 55.0.2, Chrome 61, Safari 11, Node.js v6.11.3), and the repository has not been touched since 2021.
- For workloads that do not repeat their arguments: a 4096-entry cache keyed on exact doubles does not help real ray tracing over varied rays.
- As a comparison against tuned C: the baseline is 'gcc -Wall -O3 -lm' with no -march, linked against a glibc 2.23-era libm on an unnamed CPU.
- When you need a permissive software license: the code is CC BY-SA 4.0, which is share-alike and not an OSI license.

## How it is fast

The speedup comes from memoisation, not code generation. Firefox 55's SpiderMonkey sends Math.sin, cos, tan and asin through a 4096-entry direct-mapped MathCache keyed on the input double, and that includes Ion-compiled calls: CodeGenerator::visitMathFunctionD calls the cached \*_impl variant whenever the MIR node carries a cache. A miss calls the same system sin that C uses. Every fbench iteration traces the same three marginal rays through the same lens, so its roughly 71 trig calls per iteration (3 traces x 4 curved surfaces x 5-6 calls, plus 2; derived from fbench.js) repeat identical arguments and hit the cache from the second iteration on. Safari's 0.424 is an estimate rescaled from another machine, and no mechanism was examined for it.

## Compared with alternatives

The Chapel fbench sibling (0.528) uses the same suspect GCC 5.4.0 C run, and its win is also unexplained. For a credible numeric win over C, look at the same-machine, named-compiler entries such as the gfortran plb2 matmul or the Mojo SIMD Mandelbrot. Use this entry only as a historical, memoisation-inflated JavaScript data point.

## Integration

| | |
|---|---|
| **Form** | source-drop (one JavaScript file plus an HTML runner page) |
| **Dependencies** | none (a browser or node.js) |
| **Minimum toolchain** | any ES5 engine that supports 'use strict'; measured on Firefox 55.0.2, Safari 11.0, Brave 0.18.36, Chrome 61.0.3163.91, Chromium 60.0.3112.113 and Node.js v6.11.3 |
| **Platforms** | any JavaScript engine; published runs on a Dell laptop under Xubuntu (CPU not named), Safari on a 2008 Mac Pro, plus an iPad Air side test |
| **Thread safety** | not applicable (single-threaded; state lives in module-level variables, so it is not re-entrant) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the headline: the Firefox 0.372 row measures SpiderMonkey 55's MathCache, not JavaScript speed. Identical sin, asin and tan arguments recur every iteration, so after the first iteration the trig work the C side does is skipped (4096-entry table, SizeLog2 = 12, in FIREFOX_55_0_2_RELEASE js/src/jsmath.h; the Ion path is in jit/CodeGenerator.cpp visitMathFunctionD). The results are still correct, which is why the entry stays at D instead of being rejected under the MQF/wazero cache precedent.
- The Safari 0.424 is not a measurement on the same machine: 1.6865 us per iteration on a 2008 Mac Pro was multiplied by a Perl-derived speed ratio of 0.4487, and macOS libm is not glibc.
- The C baseline looks slow. At 1.7858 us per iteration, at most about 25 ns per trig call including arithmetic (derived from page data). Serial Chapel, which compiles through C, ran 0.528 on the same laptop, and the author blames a slow new libm. GCC 5.4.0 points to Ubuntu 16.04 with glibc 2.23, which has a 2-4x slowdown of sin, cos and other libm functions on Sandy Bridge to Broadwell CPUs from AVX register saves in _dl_runtime_resolve (Launchpad 1663280, fixed in glibc 2.25; search snippet only). fbench.html also labels the C row 'GCC 3.2.3 -O3', while the README run used GCC 5.4.0.
- Port details: both the HTML page (a form .value) and the node.js main (process.argv[2]) pass the iteration count as a string, so 'itercount &lt; niter' compares a number with a string on every outer iteration. This works against JavaScript, by an amount nobody measured. The README calls Firefox's engine Rhino (it is SpiderMonkey) and prints the Firefox mean as 393.863 s, where the listed runs average 303.863 s.

## Known shortcomings

- The Firefox 2.7x comes from SpiderMonkey 55's MathCache memoising repeated trig arguments (jsmath.h, MCallOptimize.cpp, CodeGenerator.cpp at FIREFOX_55_0_2_RELEASE), a cache hit rather than computation (wazero precedent, kept as D); the Safari 2.4x is a cross-machine estimate scaled by a Perl run; V8 engines are 1.33-1.50x slower than C. CC-BY-SA-4.0, reference usability.
- The Firefox 0.372 is SpiderMonkey 55's MathCache (jsmath.h, 4096 entries; CodeGenerator visitMathFunctionD) hitting about 71 identical trig arguments per iteration, confirmed in source; the Safari row is a cross-machine estimate. The C baseline is suspect: Chapel's 0.528 on the same laptop and a glibc 2.23 slowdown (Launchpad 1663280, snippet only). The iteration count is passed as a string, so a number-versus-string compare runs each loop (hurts JS). README typos: Rhino, 393.863.

## Caveats and trade-offs

Firefox row: SpiderMonkey 55 routes Ion-inlined Math.sin, cos, tan and asin through MathCache (4096 entries keyed on the input double; the uncached path calls the same system libm sin as C), and every fbench iteration traces the same rays with the same arguments, so after the first iteration the trig calls are cache hits; the benchmark is, by the author's own description, dominated by trig library speed, so the 2.7x measures memoisation, not JavaScript codegen (close to the wazero and MQF cache precedents; kept as D, not rejected, because the result is correct and the C side is a real run). Safari row: cross-machine estimate from a 2008 Mac Pro scaled by a Perl run, and macOS libm differs from glibc; JavaScriptCore removed its own transcendental cache in 2013 (WebKit bug 123574, search snippet only). V8 rows (Brave, Chrome, Chromium, Node) are slower than C. The author attributes the gap to a slow GCC-era libm ('perhaps by as much as a factor of two'); a glibc 2.23 AVX-SSE transition regression in sin/cos (Ubuntu Launchpad 1663280) is a candidate, search snippet only. The fbench.html C label (GCC 3.2.3) contradicts the README's GCC 5.4.0 run. CPU not named. License is CC BY-SA 4.0 (LICENSE.md), not an OSI software license. [retier] SpiderMonkey 55's MathCache (jsmath.h, 4096 entries; CodeGenerator visitMathFunctionD) hits about 71 identical trig arguments per iteration, confirmed in source; the Safari row is a cross-machine estimate. The C baseline is suspect (Chapel's 0.528 on the same laptop; a glibc 2.23 slowdown, Launchpad 1663280, snippet only). The iteration count is passed as a string, so a number-versus-string compare runs each loop.

## Maintenance

Abandoned reference material: 5 commits, the last on 2021-09-24, 6 stars, one open PR from 2021, JavaScript numbers from 2017 never re-run, CC BY-SA 4.0. The JS file is small and self-validating, so re-running it on current engines is easy, but the published win is a cache artefact.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The page numbers are real, but neither winning row is a valid same-work measurement: Firefox 55's SpiderMonkey memoises Math.sin/cos/tan/asin in a 4096-entry MathCache (FIREFOX_55_0_2_RELEASE js/src/jsmath.h, jsmath.cpp, jit/MCallOptimize.cpp inlineMathFunction, jit/CodeGenerator.cpp visitMathFunctionD) and fbench feeds identical arguments every iteration, so the trig work C does is skipped; Safari's 0.4237 is a cross-machine estimate (2008 Mac Pro run scaled by a Perl speed ratio). The V8 rows (1.33-1.50) are slower than C. No valid measurement of a JavaScript win remains, so D under the cross-run precedent.
- **Verifier notes:** Downgrade C to D: Firefox lead comes from SpiderMonkey 55's MathCache memoising repeated trig arguments (verified in Firefox 55.0.2 source), Safari lead is a cross-machine estimate, V8 engines lose to C; baseline is GCC 5.4.0 -O3 not 3.2.3. The Firefox row alone would fit the wazero/MQF cache reject precedent; kept as D since the record also holds legitimate (slower) rows. License corrected to CC-BY-SA-4.0.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-80 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/Web_pages/fbench.html>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/LICENSE.md>
  - <https://github.com/Fourmilab/floating_point_benchmarks>
  - <https://github.com/Fourmilab/floating_point_benchmarks/commits>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/fbench.c>
  - <https://github.com/Fourmilab/floating_point_benchmarks/tree/master/src/javascript>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/README>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/fbench.js>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jsmath.h>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jsmath.cpp>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jit/MCallOptimize.cpp>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jit/CodeGenerator.cpp>
- **Sources the enricher read:**
  - <https://github.com/Fourmilab/floating_point_benchmarks>
  - <https://github.com/Fourmilab/floating_point_benchmarks/commits>
  - <https://github.com/Fourmilab/floating_point_benchmarks/pulls>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/Web_pages/fbench.html>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/c/fbench.c>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/README>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/Makefile>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/fbench.js>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/javascript/fbench.html>
  - <https://raw.githubusercontent.com/Fourmilab/floating_point_benchmarks/HEAD/src/chapel/README>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jsmath.h>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jsmath.cpp>
  - <https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jit/CodeGenerator.cpp>
  - https://raw.githubusercontent.com/mozilla-firefox/firefox/FIREFOX_55_0_2_RELEASE/js/src/jit/MCallOptimize.cpp (HTTP 429 twice; relied on the verifier's reading)
  - https://bugs.launchpad.net/ubuntu/+source/glibc/+bug/1663280 (DNS failure; WebSearch snippets of edge.launchpad.net/bugs/1663280 and the Red Hat bug 1421121 listing only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:javascript/fourmilab/floating_point_benchmarks#fbench`) · [data/wave14/enrich/raw/lang_javascript_fourmilab_floating_point_benchmarks_fbench.json](../../../data/wave14/enrich/raw/lang_javascript_fourmilab_floating_point_benchmarks_fbench.json) (enrichment confidence 0.8)

</details>
