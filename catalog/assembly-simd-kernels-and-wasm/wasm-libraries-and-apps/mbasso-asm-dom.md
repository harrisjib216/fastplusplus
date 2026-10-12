# asm-dom

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> C++ port of the snabbdom virtual DOM compiled to WebAssembly; wins pure-diff rows against snabbdom, loses where DOM writes cross into JavaScript.

| | |
|---|---|
| **Beats** | snabbdom 0.7.0 (JavaScript virtual DOM library, in-browser; version pinned in benchmarks/package.json) |
| **Claimed result** | README text says apps written with it 'will run until 4 times faster', a projection, not a measured row. Measured table (lower is better; units not stated on the page, but Perf.js times each run with performance.now(), so milliseconds per call of a 100-iteration loop): Firefox 67.0.1: create nodes 1.0 vs 0.0, diff equal nodes 2.0 vs 9.0, diff different nodes 20.0 vs 23.0, add/remove nodes 22.0 vs 25.0 (asm-dom vs snabbdom). Chrome 75.0.3770.80: create nodes 0.585 vs 0.455, diff equal nodes 2.395 vs 3.11, diff different nodes 17.795 vs 11.405, add/remove nodes 15.17 vs 15.63. Ratios (derived from page data): Chrome diff equal nodes 1.30x faster, add/remove 1.03x faster, diff different nodes 1.56x slower, create nodes 1.29x slower; Firefox diff equal nodes 4.5x faster, diff different nodes 1.15x faster, add/remove 1.14x faster, create nodes slower at timer resolution. |
| **Workload** | Four virtual DOM micro-benchmarks (create 700 nodes, diff 100 times with equal nodes, diff 100 times with different attributes, add/remove 100 children) run in Firefox 67 and Chrome 75, asm-dom (C++ compiled to WebAssembly with Emscripten) versus snabbdom. |
| **Metric** | latency |
| **Hardware** | MacBook Pro (Retina, 13-inch, Late 2013), 2.4 GHz Intel Core i5, 8 GB 1600 MHz DDR3 |
| **Compiler and flags** | Emscripten emcc (version not stated), benchmarks/package.json compile:wasm: -O3 --bind --memory-init-file 0 --llvm-lto 3 --llvm-opts 3 --js-opts 1 --closure 1 -s MODULARIZE=1 -s ALLOW_MEMORY_GROWTH=1 -s AGGRESSIVE_VARIABLE_ELIMINATION=1 -s ABORTING_MALLOC=1 -s NO_EXIT_RUNTIME=1 -s NO_FILESYSTEM=1 -s DISABLE_EXCEPTION_CATCHING=2 -s BINARYEN=1 -s BINARYEN_TRAP_MODE='allow'; snabbdom 0.7.0 bundled with webpack 2.4.1 and babel 6.24.1. |
| **Adoption** | 2.8k stars, 87 forks |
| **Last commit** | 2022-08-28 |
| **Links** | [repository](https://github.com/mbasso/asm-dom) · [benchmark](https://github.com/mbasso/asm-dom/tree/master/benchmarks) |

## Verdict

The author's harness timed 100-iteration loops of create/patch on a 2013 MacBook Pro (2.4 GHz Core i5), asm-dom built with an unstated Emscripten version at -O3 with fastcomp flags (--llvm-lto 3, --closure 1, BINARYEN=1) against snabbdom 0.7.0 under webpack 2/Babel 6: asm-dom won diff-equal-nodes (Firefox 67 2 vs 9 ms, Chrome 75 2.395 vs 3.11 ms) and add/remove by 3-14%, and diff-different-nodes in Firefox (20 vs 23 ms), but lost diff-different-nodes in Chrome (17.795 vs 11.405 ms) and create-nodes in both browsers; first-party numbers only.

## Use it when

- You already have a C++ codebase (model, algorithms, shared desktop/mobile logic) and want a browser UI without writing a JS binding layer.
- Re-render-heavy UIs where most patches find nothing to change: the 'diff equal nodes' row (100 patches of a 100-child tree) was 4.5x faster in Firefox 67 and 1.30x in Chrome 75 than snabbdom 0.7.0.
- Experiments or teaching about WASM/DOM interop, where the small (a few hundred lines per module) snabbdom-shaped core is easy to read and fork.
- Server-side rendering from C++ via asm-dom-server's toHTML when the same views must also render in the browser.

## Skip it when

- Attribute-heavy updates: the 'diff different nodes' row was 1.56x slower than snabbdom in Chrome 75 (derived from page data) because each setAttribute is an EM_ASM call that decodes two UTF-8 strings in JavaScript.
- Plain JS/TS apps: rewriting into C++ for a virtual DOM gives no measured app-level win; the README's 'until 4 times faster' is a projection for app logic, not a benchmark row.
- Anything needing a maintained toolchain: last commit 2022-08-28, last release v0.7.0 (2020-08-16), and issue #185 (2025) reports the C++ sources fail to compile with Emscripten 4.0.10.
- Teams that want garbage-collected vnodes: you own raw VNode\* memory, and mistakes (patching a freed tree with clearMemory=false, forgetting deleteVNode on unpatched trees) are use-after-free or leaks.
- If you want a WASM UI framework with third-party numbers, the Rust entries measured in krausest/js-framework-benchmark are better evidenced; asm-dom was never in that suite (issue #122 asks, no answer).

## How it is fast

The diff is snabbdom's two-ended updateChildren algorithm rewritten in C++, with each VNode's selector, node type, key presence and attribute/child flags packed into one integer hash so sameVNode is a couple of mask compares; selectors are interned to small integers in a global table. Attribute maps are diffed in C++ (std::unordered_map&lt;std::string,std::string&gt;), so a patch that changes nothing never leaves wasm. DOM nodes are referenced by integer handles into a JS-side node table and every actual DOM write is an EM_ASM inline-JS call, which is why rows that touch the DOM gain little or lose.

## Compared with alternatives

Pick asm-dom only when the UI must be written in C++ with Emscripten; Leptos, Sycamore or rust-dominator are the choice for a WASM UI in Rust, with independent js-framework-benchmark data and active maintenance, whereas asm-dom's only evidence is its own mixed four-row micro-benchmark.

## Integration

| | |
|---|---|
| **Form** | source-drop (unity build of src/cpp/asm-dom.cpp compiled with emcc --bind) or npm module asm-dom 0.7.0 with prebuilt wasm/asm.js |
| **Dependencies** | Emscripten with embind (emscripten::val, EM_ASM); asm-dom's JS glue (Module.nodes table, DOM helper functions); optional gccx for CPX/JSX-like syntax |
| **Minimum toolchain** | Emscripten fastcomp-era toolchain (Travis used trzeci/emscripten:sdk-incoming-64bit); C++ standard not documented (code uses C++11 features); fails with Emscripten 4.0.10 per issue #185 |
| **Platforms** | Browsers with WebAssembly (asm.js fallback build), Node.js for the server-side toHTML build |
| **Thread safety** | not documented; the library keeps global mutable state (currentNode, the selector hash table, CLEAR_MEMORY/UNSAFE_PATCH flags), so treat it as single-threaded main-thread only |
| **Drop-in for the baseline** | partial: same h/patch model and diff algorithm as snabbdom, but the API is C++ (or a pointer-returning JS API), memory is manual, and modules/hooks differ |

## Gotchas

- Harness flaws behind the numbers: Perf.js takes the 'median' of 10 runs with Array.prototype.sort() and no comparator (lexicographic sort of numbers, wrong whenever runs straddle a power of ten) at index 5 of 10; the asm-dom suite runs first and snabbdom second in the same page; setup bodies are eval'd from Function.toString() with 'var ' text-replaced by 'window.'; the snabbdom create-nodes loop discards every vnode it builds, so the JIT may elide work (inference), which fits its 0.0 ms Firefox row; Firefox values are whole milliseconds, so its create row (1 vs 0) is at timer resolution.
- The diff rows reuse two prebuilt trees and swap them, so neither library's per-render vnode construction is timed, and asm-dom runs with clearMemory=false and unsafePatch=true; with the default clearMemory=true a real patch also recursively deletes the old tree, a cost absent from these rows. The asm-dom create row does include deleteVNode while snabbdom's teardown is left to the GC.
- With the default unsafePatch=false, patch() silently does nothing and returns NULL (undefined in JS) unless oldVnode is the result of the previous patch; any app with several independent roots must set unsafePatch=true.
- normalize() rewrites attributes: a value of "false" removes the attribute, "true" becomes an empty boolean attribute, and a 'key' attr is moved out of the attribute map; updateChildren also copies the old children vector by value on every call.

## Known shortcomings

- Mixed results: slower than snabbdom 0.7.0 on 2 of 4 Chrome rows (diff different nodes 1.56x, create nodes 1.29x, derived from page data); perf.js sorts timings as strings so its "median" is not a true median; the bench runs with unsafePatch=true and clearMemory=false; Emscripten version and CPU unstated. Last commit 2022-08-28.
- More harness flaws: the asm-dom suite runs before snabbdom in the same page; setup bodies are eval'd from Function.toString() with 'var ' replaced by 'window.'; the snabbdom create loop throws away every vnode, so the JIT may skip work (inference; fits the 0.0 ms Firefox row); the diff rows swap two prebuilt trees, so per-render vnode construction and the default clearMemory teardown are not timed for either library. Issue #185: no longer builds with Emscripten 4.0.10 (VNode.hpp:49 'extractSel = \~0 &lt;&lt; 13', left shift of a negative value); the bench flags are fastcomp-only (--llvm-lto, BINARYEN=1, BINARYEN_TRAP_MODE), so the numbers cannot be rebuilt as written; the safe patch path silently returns NULL. Abandoned since 2022-08-28.

## Caveats and trade-offs

Weak and mixed evidence: asm-dom is slower than snabbdom on two of four rows in Chrome (diff different nodes 1.56x slower, create nodes 1.29x slower, derived from page data) and on create nodes in Firefox. The '4 times faster' figure is a stated expectation for whole apps, not a benchmark result. Harness flaws seen in benchmarks/src/Perf.js: the 'median' of 10 runs uses Array.prototype.sort() with no comparator, which sorts the timings as strings, and then takes index ceil(10/2)=5, so the reported value is not a true median whenever runs straddle a power of ten (e.g. 9.x and 1x.x ms); runs reuse one setup and swap vnode pairs between iterations. asm-dom runs with config.unsafePatch=true and clearMemory=false and pre-grows its heap in main(), settings an app would not normally use. The create-nodes row for asm-dom includes deleteVNode while snabbdom leaves deletion to the garbage collector, and neither create test touches the DOM. Firefox values are whole numbers, consistent with Firefox's coarsened performance.now() resolution (inference), so the Firefox create row (1 vs 0) is at timer resolution. Units are not stated in the README (code shows milliseconds). Emscripten version unstated; CPU model number unstated; 2013 hardware and 2019 browsers; README typo 'snabbbom'. README badge marks the project 'experimental'. Last commit 2022-08-28, last version v0.7.0 (2020-08-16). Kept as a documented flagged entry, not as a clear win.

Every DOM update still goes through JavaScript, so the JS to WASM binding overhead sits inside the measured path (the README says so itself). Requires Emscripten and writing the whole SPA in C++. asm.js fallback is mentioned in the README. Gains depend on moving application logic into C++, not on the virtual DOM itself.

## Maintenance

Abandoned since 2022-08-28 (maintainer said in issue #125 he is busy elsewhere; experimental badge), MIT-licensed and small enough to vendor, but it no longer builds with Emscripten 4.0.10 (issue #185: 'extractSel = \~0 &lt;&lt; 13' rejected as a left shift of a negative value) and its benchmark flags are fastcomp-only, so the published numbers cannot be rebuilt as written; a C++23-only fork, theo-dep/wasm-dom (3 stars, no published numbers), targets current Emscripten.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party table in benchmarks/README.md backed by public harness code (benchmarks/src/index.cpp, index.js, Perf.js) and stated emcc flags (benchmarks/package.json), but the Emscripten version is not stated and the CPU is given only as '2.4 GHz Intel Core i5' (MacBook Pro Late 2013) with no model number, so it falls short of A; no independent measurement, so C.
- **Verifier notes:** Numbers in the record match benchmarks/README.md exactly; added derived ratios, the emcc flags from benchmarks/package.json, and harness flaws read from Perf.js (string-sorted 'median') and index.cpp (unsafePatch=true, clearMemory=false). MIT licence confirmed from LICENSE.md (with snabbdom portions credited); 2.8k stars, 87 forks, not archived on the page; last commit 2022-08-28 makes it abandoned. Shortcomings to record: mixed results (slower on 2 of 4 Chrome rows), mis-sorted median statistic, unstated Emscripten version and CPU model, abandoned since 2022.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier batch-98 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/mbasso/asm-dom>
  - <https://github.com/mbasso/asm-dom/commits/master>
  - <https://github.com/mbasso/asm-dom/tree/master/benchmarks>
  - <https://github.com/mbasso/asm-dom/tree/master/benchmarks/src>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/README.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/package.json>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/index.html>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/src/Perf.js>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/src/index.js>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/src/index.cpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/Makefile>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/package.json>
- **Sources the enricher read:**
  - <https://github.com/mbasso/asm-dom>
  - <https://github.com/mbasso/asm-dom/commits/master>
  - <https://github.com/mbasso/asm-dom/tree/master/src/cpp>
  - <https://github.com/mbasso/asm-dom/issues>
  - <https://github.com/mbasso/asm-dom/issues/185>
  - <https://github.com/mbasso/asm-dom/issues/186>
  - <https://github.com/mbasso/asm-dom/issues/122>
  - <https://github.com/mbasso/asm-dom/issues/125>
  - <https://github.com/theo-dep/wasm-dom>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/README.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/package.json>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/src/Perf.js>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/src/index.js>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/benchmarks/src/index.cpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/src/cpp/asm-dom.cpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/src/cpp/Config/Config.hpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/src/cpp/Patch/patch.cpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/src/cpp/Diff/diff.cpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/src/cpp/VNode/VNode.cpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/src/cpp/VNode/VNode.hpp>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/docs/js.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/Makefile>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/package.json>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mbasso/asm-dom/HEAD/.travis.yml>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mbasso/asm-dom`) · [data/wave13/enrich/raw/github_com_mbasso_asm_dom.json](../../../data/wave13/enrich/raw/github_com_mbasso_asm_dom.json) (enrichment confidence 0.75)

</details>
