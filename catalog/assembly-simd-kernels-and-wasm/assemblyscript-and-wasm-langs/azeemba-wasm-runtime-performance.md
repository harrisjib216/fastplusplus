# wasm-runtime-performance (boost::graph Floyd-Warshall via Emscripten)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C++ (Boost.Graph, std::priority_queue) compiled to WebAssembly with Emscripten` · `no license` · 🔴 abandoned

> 2017 browser benchmark: Boost.Graph Floyd-Warshall compiled to wasm by Emscripten versus graphlib.js; std::priority_queue loses to JS heaps.

| | |
|---|---|
| **Beats** | graphlib.js alg.floydWarshall (JavaScript, in the browser JS engine) |
| **Claimed result** | With emcc -O3: JS graphlib 61.1135 ms vs WASM boost::graph 10.1569 ms per Floyd-Warshall run (V=100, E=500), about 6.0x faster (derived from page data); unoptimised wasm: JS 62.16 ms vs WASM 1235.41 ms (about 20x slower, derived from page data). Priority-queue test at -O3 (300,000 elements, wasm slower throughout): inserts WASM 58.44 ms (bulk 51.99 ms) vs FastPriorityQueue.js 9.86 ms and Heap.js 13.42 ms (wasm 4-6x slower, derived from page data); peek+pop WASM 39.93 ms (bulk 33.07 ms) vs FastPriorityQueue.js 27.37 ms and Heap.js 32.31 ms. |
| **Workload** | JS side: graphlib graph of 111 vertices (newline-polluted ids) with one-way edge traversal; wasm side: Boost undirected graph of 100 vertices; outputs never compared |
| **Metric** | latency |
| **Compiler and flags** | emcc from a 2017 emsdk (version not stated) with Boost headers (README links Boost 1.64 docs; include path /home/azeem/temp/include). generate_output.sh: unoptimised build `emcc main.cpp -o output/data.html -D COMPILING_TO_WASM -s WASM=1 --shell-file shell_call.html -std=c++11`; optimised build adds -O3 (output/data_O3.html). Browser and JS engine not stated. |
| **Adoption** | 6 stars |
| **Last commit** | 2017-05-07 |
| **Links** | [repository](https://github.com/azeemba/wasm-runtime-performance) · [benchmark](https://github.com/azeemba/wasm-runtime-performance) |

## Verdict

In one unnamed 2017 browser on unstated hardware, averaged over 100 runs, building a 100-vertex, 500-edge graph and running Floyd-Warshall took 10.16 ms with Boost.Graph compiled by emcc -O3 versus 61.11 ms with graphlib.js (about 6.0x, derived from page data), but the JS side actually processed a 111-vertex graph because of newline characters in the digit source, and the two sides computed different paths. In the same setup, 300,000 std::priority_queue inserts took 58.44 ms (51.99 ms with the loop inside wasm) versus 9.86 ms for FastPriorityQueue.js and 13.42 ms for Heap.js.

## Use it when

- As a historical data point (2017, wasm MVP, Emscripten fastcomp era) on porting an O(V^3) dense graph kernel from a generic JS library to C++ in wasm.
- As a template for wiring Boost.Graph or STL containers into a browser page through EMSCRIPTEN_KEEPALIVE exports and Module.cwrap.
- To show that -O3 is not optional for Emscripten builds of template-heavy C++ (about 122x between the unoptimised and -O3 builds, derived from page data).
- As a cautionary example that fine-grained JS-to-wasm calls (one call per heap push or pop) can make wasm slower than a good JS data structure.

## Skip it when

- As evidence of current wasm versus JS speed: browser, JS engine, CPU and emsdk version are not stated, and engines and toolchains have changed since 2017.
- As a graph library: it handles one global graph, exposes only Floyd-Warshall, and returns only the largest finite distance.
- For priority-queue workloads: std::priority_queue in wasm was 3.9-5.9x slower on inserts and 1.02-1.46x slower on peek+pop than FastPriorityQueue.js and Heap.js in the README run (derived from page data).
- Where licensing matters: the repository has no licence file, so reuse rights are unclear.
- For sparse graphs or large V, where Dijkstra or Johnson per source beats any O(V^3) Floyd-Warshall in either language.

## How it is fast

The wasm side runs boost::floyd_warshall_all_pairs_shortest_paths over an int boost::multi_array distance matrix, a contiguous N x N array of machine integers, while graphlib's runFloydWarshall walks an object of objects keyed by string node ids, allocates a {distance, predecessor} object per pair and loops with nested forEach closures. The gain is data layout plus ahead-of-time optimisation by emcc -O3; without -O3 the same wasm is about 20x slower than the JS. The priority-queue test shows the opposite: per-element JS-to-wasm calls and even an all-in-wasm loop lose to JIT-compiled JS heaps.

## Compared with alternatives

Prefer wasm-perf (Emscripten SIMD matmul versus JS, Node 16, stated versions) or JavaScript-vs-WebAssembly-Comparative-Analysis (median of 20 reps in Chromium) for numeric kernels with stated environments; this repo is only of interest for STL and Boost data-structure code under Emscripten, and like Speedy.js it documents 2017-era engines.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Boost headers (graph, multi_array; README links the 1.64 docs; generate_output.sh points at /home/azeem/temp/include), emsdk; the JS side vendors graphlib 0.8.1-pre, FastPriorityQueue.js and Heap.js (CoffeeScript 1.8.0 build) in external_js/ |
| **Minimum toolchain** | C++11 (-std=c++11), an emcc from a 2017 emsdk (version not documented) |
| **Platforms** | WebAssembly in a browser (engine not documented); main.cpp also has a native timing path when built without COMPILING_TO_WASM, with no published numbers |
| **Thread safety** | not thread-safe: the graph G and queue Q are globals and the exports mutate them |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw, unequal graphs: pi_minus_3.js stores the digits in a String.raw template literal that begins with a newline and keeps its line breaks, so node ids read two characters at a time that straddle a break ('\n1', '6\n', and so on) become 11 extra graphlib nodes. The JS run therefore solves a 111-vertex graph (25 of the 500 edges touch the extra nodes), while the wasm side parseInt()s the same strings back into vertices 0-99. graphlib's triple loop does 111^3 / 100^3, about 1.37x, as many relaxations, so a like-for-like ratio would be nearer 4.4x than 6.0x (estimate derived from the code, assuming time scales with V^3).
- Harness flaw, different answers: the JS graph is created with {directed: false}, but alg.floydWarshall is called without an edgeFn, so it uses g.outEdges, which for an undirected graphlib graph lists each edge only under its lexicographically smaller endpoint. The JS run therefore computes paths in a one-way orientation of the graph, not in the undirected graph Boost solves. Neither result is checked: wasmLargest is computed but never printed or compared with the JS 'largest'.
- Both timed regions include graph construction (string slicing of the pi digits, 500 setEdge calls in JS versus 500 cwrap addEdge calls into wasm) and a pass over the result, and doFloydWarshall takes the Boost graph by value, so each wasm iteration also copies the graph.
- The README's '3 orders of magnitude' from -O0 to -O3 is about 122x (1235.41 ms to 10.16 ms), and each published number is one pasted console run with no variance reported.

## Known shortcomings

- 2017 single-run study with no CPU, browser or emsdk version and no licence (reference); mixed result (Boost Floyd-Warshall 6.0x at -O3 but std::priority_queue in wasm 4-6x slower on inserts); graphlib.js stores its graph in string-keyed objects; the README's "3 orders of magnitude" from -O0 to -O3 is about 122x.
- Enricher: unequal workloads: pi_minus_3.js's String.raw literal keeps newlines, so the JS graphlib graph gets 111 vertices (11 ids containing a newline, 25 of 500 edges) while the wasm side's parseInt maps them back to 100, about 1.37x more JS work (like-for-like ratio about 4.4x, not 6.0x, derived); the undirected graphlib with the default outEdges edge function makes JS solve a one-way orientation rather than the undirected graph Boost solves; results are never compared (wasmLargest unused). Retiered to D.

## Caveats and trade-offs

2017 repo (10 commits, April 22 to May 7 2017), single representative run pasted into the README, no CPU, browser or emsdk version, no licence file. Mixed result: the Floyd-Warshall win appears only at -O3, and the std::priority_queue test shows wasm slower than both JS heaps even when the loop runs entirely inside wasm (bulkInsert/bulkPops). The -O0 to -O3 gap is about 122x (1235.41 ms to 10.16 ms, derived from page data), roughly two orders of magnitude; the README's 'improved by 3 orders of magnitude' overstates it. Both timed regions include graph construction (graphlib setNode/setEdge in JS, 500 cwrap addEdge calls into wasm) and a result scan, so the harness is symmetric, but the JS baseline is a generic string-keyed object graph library, not an equivalent data layout to Boost's adjacency_list plus multi_array distance matrix. main.cpp also has a native C++ timing path (non-wasm) with no published numbers. The live benchmark pages are on azeemba.github.io (not opened; host blocked here).

Needs boost and emsdk to rebuild; wasm in 2017-era browsers; wasm module startup excluded (the README says it only times execution after loading).

## Maintenance

Abandoned since 7 May 2017 (10 commits, no licence file, 6 stars); a reference data point with the harness flaws above, not reusable code, and its 6.0x headline compares unequal graph sizes and different path problems, which may justify a downgrade to D.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** README pastes single-run console output of the repo's own harness (shell_call.js floydWarshallBenchmark and priorityQueueBenchmark, 100-iteration averages via performance.now) comparing boost::graph Floyd-Warshall compiled with emcc -O3 against graphlib.js; build commands are public in generate_output.sh, but the emsdk version, browser/JS engine and CPU model are not stated, so first-party with partial methodology is C.
- **Retiered** C to D: Enricher (2026-10-12): the two sides solve different problems. The JS graph is built from a String.raw literal that keeps newlines, giving graphlib 111 vertices and malformed ids while the wasm side parses them back to 100 vertices, and the undirected graphlib with the default outEdges edge function solves a one-way orientation rather than the undirected graph Boost solves; outputs are never compared. No valid like-for-like measurement.
- **Verifier notes:** Numbers on the README match the record exactly; emcc flags are in generate_output.sh (the record wrongly said they were not shown) and the caveat about three orders of magnitude was corrected to about 122x. It is a 2017 study of C++ via Emscripten against JS libraries rather than a library, mixed by design (wasm slower on the heap test); keep as tier C reference with no licence.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-119 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/azeemba/wasm-runtime-performance>
  - <https://github.com/azeemba/wasm-runtime-performance/commits>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/README.md>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/generate_output.sh>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/graph_work.h>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/fw.cpp>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/shell_call.js>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/shell_call.html>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/pi_minus_3.js>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/pi.h>
- **Sources the enricher read:**
  - <https://github.com/azeemba/wasm-runtime-performance>
  - <https://github.com/azeemba/wasm-runtime-performance/commits/master>
  - <https://github.com/azeemba/wasm-runtime-performance/tree/master/external_js>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/README.md>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/generate_output.sh>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/graph_work.h>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/fw.cpp>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/shell_call.js>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/shell_call.html>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/pi_minus_3.js>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/pi.h>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/external_js/graphlib.js>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/external_js/FastPriorityQueue.js>
  - <https://raw.githubusercontent.com/azeemba/wasm-runtime-performance/HEAD/external_js/heap.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/azeemba/wasm-runtime-performance`) · [data/wave13/enrich/raw/github_com_azeemba_wasm_runtime_performance.json](../../../data/wave13/enrich/raw/github_com_azeemba_wasm_runtime_performance.json) (enrichment confidence 0.75)

</details>
