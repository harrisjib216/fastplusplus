# BenchmarkingWebAssembly (Understanding the Performance of WebAssembly Applications)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C (PolyBenchC and CHStone) compiled by Cheerp to WebAssembly and JavaScript; Python test scripts` · `no license` · 🔴 abandoned

> IMC 2021 study artifact timing Cheerp-compiled WebAssembly against Cheerp-compiled JavaScript on PolyBenchC and CHStone in three browsers.

| | |
|---|---|
| **Beats** | JavaScript produced from the same C programs by Cheerp 2.0 |
| **Claimed result** | README RQ1: with extra-small and small inputs WebAssembly is faster than JavaScript in almost all benchmarks (97.6% and 95.1%), averaging 26.99x (extra-small) and 8.22x (small); with medium inputs 18 of 41 benchmarks become slower in WebAssembly (average slowdown 1.71x) and the remaining 23 average 6.70x faster. Example: 3mm is 47.71x, 10.54x and 1.12x faster in WebAssembly for extra-small, small and medium inputs. WebAssembly also uses 3.39-6.20x more memory than JavaScript across browsers. |
| **Workload** | 41 PolyBenchC and CHStone benchmarks plus other subjects at extra-small, small and medium input sizes, WASM vs JS execution time in Chrome 79, Firefox 71 and Edge 79, desktop and mobile. |
| **Metric** | latency |
| **Compiler and flags** | Cheerp 2.0, tested at -O1, -O2, -Ofast and -Oz (README); Chrome 79, Firefox 71, Edge 79 |
| **Adoption** | 3 stars |
| **Last commit** | 2021-05-28 |
| **Links** | [repository](https://github.com/benchmarkingwasm/benchmarkingwebassembly) · [benchmark](https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly) |

## Verdict

The README (abstract of the IMC 2021 paper, DOI 10.1145/3487552.3487827) reports Cheerp 2.0 WebAssembly averaging 26.99x and 8.22x faster than Cheerp's JavaScript output on 41 PolyBenchC and CHStone programs at extra-small and small inputs, with 18 of 41 slower at medium input, in Chrome 79, Firefox 71 and Edge 79 on unstated desktop and mobile hardware, 5 cold runs averaged; the small-input gap is dominated by JavaScript warm-up, and the shipped WebAssembly loaders cannot reproduce the timings because they stop the clock before the module runs.

## Use it when

- Citing evidence that WebAssembly's lead over JavaScript depends heavily on input size and is largest for short, cold, run-once kernels.
- Needing PolyBenchC or CHStone sources already patched to compile under Cheerp (malloc instead of posix_memalign, calloc-free timer init) as a starting point for your own browser benchmarks.
- Comparing browser engines' relative WebAssembly vs JavaScript behaviour circa Chrome 79, Firefox 71 and Edge 79, desktop and mobile, from the raw CSVs.
- Looking for input-size tables (input_size.md) mapping PolyBench MINI..EXTRALARGE and CHStone sizes to concrete dimensions.

## Skip it when

- Choosing a WebAssembly library for production: there is nothing to link, and the repo has no license, so the patched sources cannot be reused legally.
- Judging hand-written or modern JavaScript: the baseline is Cheerp 2.0's machine-generated JS, and the engines are from late 2019.
- Reproducing the published numbers from compiled_benchmarks as shipped: the WebAssembly loaders stop the timer before the module even runs (see gotchas).
- Drawing peak-memory conclusions: the memory columns are post-run heap snapshots, not peak usage.
- Expecting maintenance: last commit 2021-05-28, 3 stars, 24 commits, no releases.

## How it is fast

Nothing in the repo is a speed technique; the WebAssembly-over-JavaScript gap it reports comes from the engines. WebAssembly modules are compiled ahead of execution (Liftoff/TurboFan in Chrome, Baseline/Ion in Firefox) and use typed linear memory, while the Cheerp JavaScript output starts in the engine's interpreter and must warm up its JIT in a single cold run, which dominates the extra-small and small inputs where the 26.99x and 8.22x averages come from. At medium and larger inputs the warm-up share vanishes and the two converge or JavaScript wins (18 of 41 benchmarks at medium; gemm LARGE in input_size.csv is 1,499 ms JS vs 4,789 ms WASM).

## Compared with alternatives

Pick this when you need a cross-browser, input-size-swept study of WebAssembly versus compiler-generated JavaScript rather than a component; for a usable component with a JS-backend comparison the TensorFlow.js WebAssembly backend is the catalogued choice, and iswasmfast is the smaller hands-on micro-benchmark that also includes a native N-API addon.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Cheerp 2.0 toolchain (/opt/cheerp/bin/clang), Python 2.7 for the compile scripts and SimpleHTTPServer; for auto.py Python 3.7+, Selenium, a matching chromedriver and the Windows-only wmi module |
| **Minimum toolchain** | Cheerp 2.0; Chrome 79, Firefox 71, Edge 79 as tested |
| **Platforms** | any browser with WebAssembly; auto.py runs only on Windows with Chrome |
| **Thread safety** | not applicable (single-threaded benchmark programs) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the shipped artifact: every compiled_benchmarks/\*_load.js (File Ver 200531 2200; checked 3mm and covariance at all five sizes and CHStone dfsin XXXL) starts t0, calls fetchBuffer(...).then(WebAssembly.instantiate).then(... i.exports.bX()), then takes t1 = performance.now() synchronously and logs (t1-t0)/1000. The fetch, compilation, instantiation and the benchmark's main all run in later promise callbacks, so the logged WebAssembly time excludes the benchmark entirely, while the .js files call main synchronously before t1. The repo's CSVs scale with kernel cost (gesummv medium 0.0005 s vs 3mm 0.15 s), so the published data were not produced by these loaders, and the repo does not document what scope the published WebAssembly times covered.
- Asymmetric scope even in the best case: the JavaScript time covers the whole script from its first statement in one cold page load per run (init_array, interpreter and JIT warm-up, kernel), and the PolyBench C timer calls (polybench_start/stop_instruments) are commented out in the modified sources although the README still compiles with -DPOLYBENCH_TIME. The 26.99x extra-small average is mostly JavaScript warm-up on microsecond kernels (gesummv MINI: 0.229 ms JS vs 0.008 ms WASM).
- Memory figures are heap snapshots taken after the program finished: JavaScript reads 877-889 KB at every size, including covariance EXTRALARGE whose arrays alone exceed 100 MB, because the typed arrays were already garbage-collected, while WebAssembly linear memory never shrinks. The '3.39-6.20x more memory' claim compares retained memory after the run, not peak use.
- auto.py counts failed runs: a ReferenceError run is stored as -1 and included in the average (sum over non-zero entries divided by their count), it sleeps a fixed 1 s and parses only the first console message, and it is hard-wired to the MEDIUM -O2 files and to Windows process killing via wmi.

## Known shortcomings

- Raised C to B on the IMC 2021 paper (DOI 10.1145/3487552.3487827, snippet only): a study artifact whose baseline is Cheerp-generated JS; WASM is slower on 18 of 41 programs at medium input; no hardware stated; manual timing; no licence (reference).
- Enricher: every shipped compiled_benchmarks/\*_load.js reads t1 right after starting fetch() while WASM compile, instantiate and the kernel run later in promise callbacks, so the shipped artifact times nothing for WASM while the JS files run main before t1; the published CSVs scale with kernel cost, so they came from other loaders with the timing scope undocumented; C timers are commented out; JS time is one cold run, so the small-input 26.99x is mostly JIT warm-up; memory is a post-run heap snapshot (JS about 885 KB even with over 100 MB arrays), so '3.39-6.20x more memory' is retained memory, not peak; auto.py counts ReferenceError runs as -1 in its average; no licence. Retiered to C.

## Caveats and trade-offs

A measurement study (IMC 2021 artifact) rather than a reusable library: the 'project' is Cheerp 2.0's WebAssembly output, and the JavaScript baseline is Cheerp's own JS output from the same C sources, not hand-written JS. Mixed outcome: the WebAssembly lead shrinks with input size and reverses for 18 of 41 benchmarks at medium inputs; WebAssembly uses 3.4-6.2x more memory. Browsers are from 2019-2020 (Chrome 79, Firefox 71, Edge 79), hardware is not stated in the README, and timings are copied manually from the browser console. Peer review confirmed only from a search-result snippet of the OpenAlex record (DOI 10.1145/3487552.3487827); the paper itself was not reachable. No license file, so reference only. [retier] Shipped loaders time nothing for WASM; CSV provenance undocumented; JS single cold run; memory is retained heap after GC, not peak; C timers commented out; auto.py averages ReferenceError runs as -1; no licence

A study, not a library: the JS baseline is machine-generated by Cheerp rather than idiomatic hand-written JavaScript, and WASM's advantage shrinks or reverses as input grows; repo has no license, so the code is reference only.

## Maintenance

Abandoned study artifact (last commit 2021-05-28, 3 stars) with no license, so reference only; its data and figures are useful context, but treat the speedups as cold-start, compiler-generated-JS results and do not reuse the shipped loaders for timing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo is the artifact of the peer-reviewed paper 'Understanding the Performance of WebAssembly Applications', ACM Internet Measurement Conference (IMC) 2021, DOI 10.1145/3487552.3487827, first author Yutian Yan (venue confirmed from an OpenAlex record in a WebSearch result, snippet only; doi.org, dl.acm.org and api.openalex.org are blocked here). The README's RQ1 numbers match the claim; not A because the README states no CPU or device models and timings are read by hand from browser developer tools.
- **Retiered** B to C: Enricher (2026-10-12): the published numbers cannot be reproduced from the shipped artifacts. Every shipped \*_load.js reads its start time right after launching fetch() while the WASM compile, instantiate and kernel run later in promise callbacks, so the artifact times nothing on the WASM side; the published CSVs scale with kernel cost and so came from undocumented loaders; JS times are single cold runs (small-input ratios are JIT warm-up) and memory is a post-run retained-heap snapshot, not peak. Harness-flaw precedent; peer-reviewed status no longer carries B.
- **Verifier notes:** Upgraded C to B: the README is the abstract of the IMC 2021 paper (DOI 10.1145/3487552.3487827, snippet only). Metadata confirmed: 3 stars, 24 commits, no license, last commit 2021-05-28 (abandoned). Shortcomings: study artifact, Cheerp-generated JS baseline, WebAssembly slower on 18 of 41 benchmarks at medium input, no hardware stated, manual timing.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-21 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly>
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly/commits/master>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly>
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly/commits/master>
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly/tree/master/test_results>
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly/tree/master/modified_benchmarks>
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly/tree/master/compiled_benchmarks>
  - <https://github.com/BenchmarkingWasm/BenchmarkingWebAssembly/tree/master/other_benchmarks>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/README.md>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/input_size.md>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/auto.py>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/test_results/input_size.csv>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/test_results/browser_desktop.csv>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/test_results/opt_level_JS_WASM.csv>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compiled_benchmarks/3mm_-DMINI_DATASET_O2.js>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compiled_benchmarks/3mm_-DMINI_DATASET_O2_load.js>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compiled_benchmarks/3mm_-DLARGE_DATASET_O2_load.js>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compiled_benchmarks/covariance_-DEXTRALARGE_DATASET_O2_load.js>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compiled_benchmarks/dfsin_-DXXXL_DATASET_O2_load.js>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compiled_benchmarks/server.py>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/modified_benchmarks/polybench-c-4.2.1-beta/utilities/polybench.c>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/modified_benchmarks/polybench-c-4.2.1-beta/utilities/polybench.h>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/modified_benchmarks/polybench-c-4.2.1-beta/linear-algebra/kernels/3mm/3mm.c>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/modified_benchmarks/polybench-c-4.2.1-beta/datamining/covariance/covariance.c>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compilation_scripts/poly.py>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compilation_scripts/poly2.py>
  - <https://raw.githubusercontent.com/BenchmarkingWasm/BenchmarkingWebAssembly/HEAD/compilation_scripts/chs.py>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/benchmarkingwasm/benchmarkingwebassembly`) · [data/wave13/enrich/raw/github_com_benchmarkingwasm_benchmarkingwebassembly.json](../../../data/wave13/enrich/raw/github_com_benchmarkingwasm_benchmarkingwebassembly.json) (enrichment confidence 0.75)

</details>
