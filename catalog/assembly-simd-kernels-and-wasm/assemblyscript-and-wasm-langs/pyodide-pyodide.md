# Pyodide (NumPy inv in WebAssembly vs math.js)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MPL-2.0` · 🟢 active

> CPython plus NumPy and SciPy compiled to WebAssembly; one informal test inverted a 200x200 matrix about 20x faster than math.js.

| | |
|---|---|
| **Beats** | math.js (JavaScript) in Chrome and Safari |
| **Claimed result** | numpy in Pyodide 0.024 s vs math.js in Chrome 0.475 s (about 20x faster, derived from page data) and Safari 2.403 s; native numpy 0.009 s, Octave 0.005 s. |
| **Workload** | Matrix inverse inv(rand(200,200)): numpy running in Pyodide (CPython and NumPy compiled to WebAssembly) in the browser vs math.js in Chrome and Safari, with native Python 3.10 numpy and Octave as references. |
| **Metric** | latency |
| **Adoption** | 14.9k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/pyodide/pyodide) · [benchmark](https://github.com/josdejong/mathjs/discussions/2744) |

## Verdict

One informal timing in math.js discussion #2744 (2023-02-11; machine, browser versions and run counts not stated): inverting a freshly generated random 200x200 matrix took 0.024 s with NumPy in Pyodide in the browser, 0.475 s with math.js in Chrome (about 20x, derived from page data) and 2.403 s with math.js in Safari. Native NumPy on Python 3.10 took 0.009 s and Octave 0.005 s. Download and initialization time were not included.

## Use it when

- Browser or Node.js apps that need real NumPy, SciPy or pandas behaviour on the client (notebooks, teaching tools, offline data apps) when the alternative is rewriting the numerics in JavaScript.
- Dense linear algebra on matrices of a few hundred rows where math.js's generic matrices are the incumbent: 0.024 s vs 0.475 s (Chrome) for one 200x200 inverse.
- Long-lived sessions where the multi-megabyte download and the seconds of startup are paid once, run in a module Web Worker so synchronous Python does not block the UI.
- Porting existing Python numerical code to the web with little rewriting.

## Skip it when

- One-off or latency-sensitive page loads: the roadmap cites a 6.4 MB first download and 4 to 5 s of initialization for the core, and NumPy adds about 2.8 MB compressed (issue #3763). The comparison measured none of this.
- Heavy BLAS-3 work: Pyodide's reference BLAS ran dgemm 15-35x slower than native (issue #3763), a 1024x1024 float32 np.dot took about 3 s vs 0.005 s natively (issue #1574), and native NumPy did the 200x200 inverse 2.7x faster than Pyodide.
- Data that lives in JavaScript: every array has to cross the JS-Python FFI (issue #2232 reports costly NumPy-to-tfjs transfers). The benchmark avoided this cost by generating its data inside Python.
- Multithreaded work: threading, multiprocessing and subprocess raise RuntimeError (FAQ).
- A single kernel such as a matrix product or an inverse, where a typed-array JS library or a small Emscripten or Rust wasm module needs far less code and download.

## How it is fast

The speedup comes from NumPy's compiled C, not from anything Pyodide adds. np.linalg.inv copies the matrix into a contiguous buffer and calls LAPACK gesv (LU with partial pivoting) against an identity matrix. Pyodide builds NumPy with -Dallow-noblas=true and no BLAS dependency, so gesv runs NumPy's f2c-translated lapack_lite reference code (NumPy calls these '(slow!) internal fallback routines'), compiled by Emscripten at -O2 with no blocking, SIMD or threads. math.js's inv does Gauss-Jordan elimination over nested JS arrays and sends every scalar step through typed-function dispatch: about 12 million addScalar(multiply()) steps for a 200x200 matrix (derived from inv.js). The gap therefore measures that dispatch overhead, not WebAssembly against JavaScript.

## Compared with alternatives

Pick Pyodide over single-kernel siblings such as wasm-perf (Emscripten SIMD matmul) or the Rust matmul in JavaScript-vs-WebAssembly-Comparative-Analysis when you need the whole Python scientific stack rather than one hand-written routine. Pick those siblings, or a typed-array JS library, when you need one operation with a small download and no interpreter startup.

## Integration

| | |
|---|---|
| **Form** | module (JavaScript loader pyodide.mjs plus the pyodide.asm.wasm runtime, python_stdlib.zip and per-package wheels, from the jsDelivr CDN or npm) |
| **Dependencies** | none for the runtime; NumPy and other packages load separately as wheels through loadPackage or micropip |
| **Minimum toolchain** | Node.js 18+ (npm engines field) or a modern browser with WebAssembly; current main builds Python 3.14.2 with Emscripten 5.0.3; Web Workers must be module-type |
| **Platforms** | wasm32 in browsers and Node.js; no pthreads |
| **Thread safety** | Single-threaded: threading, multiprocessing and subprocess raise RuntimeError; run Pyodide in a module Web Worker to keep the main thread responsive. |
| **Drop-in for the baseline** | partial — it replaces math.js only if you rewrite the maths as Python/NumPy calls behind the FFI; there is no math.js-compatible API |

## Gotchas

- The evidence is one informal post (dvd101x, math.js discussion #2744, 2023-02-11). It gives no machine, browser versions, Pyodide or math.js version, run count or warm-up, and every timed expression includes generating the random matrix. The stable Pyodide release on that date was 0.22.1 (2023-01-25), whose NumPy 1.23.5 recipe was built with --disable-optimization.
- The 20x mostly measures math.js's generic typed-function dispatch: a math.js maintainer named that indirection as the main cause of its slowness in December 2024, and math.js ran 5x slower in Safari than in Chrome. It is not a WebAssembly-vs-JavaScript result: native NumPy is still 2.7x faster than Pyodide on the same inverse, and no plain typed-array JavaScript loop was measured.
- Pyodide's NumPy has no optimized BLAS or LAPACK. It uses the lapack_lite fallback, the OpenBLAS evaluation (issue #3763, open since 2023-04) has not landed, and a NumPy maintainer said in that issue that NumPy is considering dropping lapack-lite, so large matrices fall far behind native.
- Releases are now numbered after the Python version (314.0.7 on 2026-09-14, with 0.29.x and 0.27.x stable branches). Compiled packages must be built for the matching Pyodide ABI.

## Known shortcomings

- Informal third-party post (mathjs discussion #2744, 0.024 s vs 0.475 s in Chrome) with no machine or run count; timing includes random-matrix generation; really LAPACK compiled to WebAssembly against pure-JavaScript math.js; loose category fit.
- No code bug; the evidence is a single informal anecdote. The 20x comes from math.js's typed-function dispatch (about 12M addScalar(multiply()) steps, derived from inv.js) against NumPy's lapack_lite gesv (Pyodide builds NumPy with -Dallow-noblas, no BLAS); native NumPy is 2.7x faster than Pyodide; download, startup and FFI cost are excluded; category fit is loose.

## Caveats and trade-offs

There is one informal timing table from a math.js collaborator (dvd101x, 2023-02-11) in mathjs discussion #2744. It states no machine, OS, browser version, Pyodide version or run count. The poster calls it 'only a quick comparison' and notes that math.js's flexibility adds overhead. Each timed expression includes random-matrix generation (math.random / np.random.rand) as well as the inverse. The win comes from NumPy's compiled LAPACK routines running as WebAssembly against math.js's generic pure-JS matrix code, so it compares implementations more than languages. Native numpy is still about 2.7x faster than numpy in Pyodide (derived from page data). Load and warm-up time are not included. Pyodide publishes no such benchmark; its repo has a benchmark/ directory but no README figures. Fit with assemblyscript-and-wasm-langs is loose: Pyodide is CPython plus scientific packages compiled to WebAssembly with Emscripten.

Large download and startup cost for the Python runtime and NumPy (not measured in this comparison); results depend on browser Wasm engine.

## Maintenance

Actively maintained (last commit 2026-09-22, 14.9k stars, MPL-2.0, latest release 314.0.7 on 2026-09-14) and widely used. The only performance evidence is a third-party anecdote that pits NumPy's compiled reference LAPACK against math.js's generic dispatch, and the category fit is loose because Pyodide is a Python runtime, not a wasm language.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** In mathjs discussion #2744 ('Accelerated computations with WASM'), dvd101x posted on 2023-02-11 a single table: mathjs in Safari 2.403 s, mathjs in Chrome 0.475 s, numpy in Pyodide in the browser 0.024 s, native numpy (Python 3.10) 0.009 s, Octave 0.005 s for inv of a random 200x200 matrix. It is an informal third-party post with no machine, browser version, run count or harness, not a peer-reviewed or well-known suite, so it is C.
- **Verifier notes:** All five numbers in claimed_speedup match the post exactly, and the roughly 20x ratio over math.js in Chrome (0.475/0.024) is correctly marked as derived. Metadata checks out: MPL-2.0, 14.9k stars, last commit 2026-09-22, active. Shortcomings: single informal third-party run with no methodology, generation time included, a LAPACK-vs-pure-JS implementation gap, loose category fit.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-54 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/josdejong/mathjs/discussions/2744>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/README.md>
  - <https://github.com/pyodide/pyodide>
  - <https://github.com/pyodide/pyodide/commits>
- **Sources the enricher read:**
  - <https://github.com/josdejong/mathjs/discussions/2744>
  - <https://raw.githubusercontent.com/josdejong/mathjs/develop/src/function/matrix/inv.js>
  - <https://github.com/pyodide/pyodide>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/README.md>
  - <https://github.com/pyodide/pyodide/tree/main/benchmark>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/benchmark/benchmark.py>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/Makefile.envs>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/docs/project/roadmap.md>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/docs/usage/faq.md>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/docs/usage/downloading-and-deploying.md>
  - <https://raw.githubusercontent.com/pyodide/pyodide/HEAD/docs/usage/webworker.md>
  - <https://raw.githubusercontent.com/pyodide/pyodide/0.22.1/packages/numpy/meta.yaml>
  - <https://raw.githubusercontent.com/pyodide/pyodide-recipes/HEAD/packages/numpy/meta.yaml>
  - <https://github.com/pyodide/pyodide/issues?q=is%3Aissue%20BLAS>
  - <https://github.com/pyodide/pyodide/issues/1120>
  - <https://github.com/pyodide/pyodide/issues/1574>
  - <https://github.com/pyodide/pyodide/issues/3763>
  - <https://raw.githubusercontent.com/numpy/numpy/main/meson.options>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/linalg/meson.build>
  - <https://raw.githubusercontent.com/numpy/numpy/main/numpy/linalg/umath_linalg.cpp>
  - <https://pypi.org/pypi/pyodide-py/json>
  - <https://registry.npmjs.org/pyodide>
  - <https://github.com/BertrandBev/eigen-js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/pyodide/pyodide`) · [data/wave13/enrich/raw/github_com_pyodide_pyodide.json](../../../data/wave13/enrich/raw/github_com_pyodide_pyodide.json) (enrichment confidence 0.75)

</details>
