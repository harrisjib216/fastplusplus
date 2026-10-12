# WasmBoy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `AssemblyScript (TypeScript)` · `GPL-3.0-or-later` · 🔴 abandoned

> AssemblyScript Game Boy/Color emulator whose one core builds to both Wasm and JS; benchmark app compares them per frame.

| | |
|---|---|
| **Beats** | The same emulator core compiled to JavaScript through the TypeScript compiler (ES6), run in the browser |
| **Claimed result** | No numbers in the repo; the first-party Medium article ('WebAssembly is fast: a real-world benchmark of WebAssembly vs ES6', 2019) could not be fetched. Snippet only: De Macedo et al. 2022 ran six Game Boy games on WasmBoy in Chrome, Edge and Firefox (36 samples, Wasm core vs TypeScript-compiled JS core) and report Wasm faster in their regression model, with a language factor of 0.84 for Wasm vs 1 for JavaScript; the same study reports Firefox often favouring JavaScript (stated for its micro-benchmarks). |
| **Workload** | Game Boy / Game Boy Color emulator core frame throughput: the same AssemblyScript source built as Wasm (AssemblyScript compiler), as JS through the TypeScript compiler (memory interface mocked) and as TS plus Closure Compiler, timed per frame in the browser by demo/benchmark (optional extra cores: binjgb C compiled with Emscripten, GameBoy Online in JS) |
| **Metric** | throughput |
| **Adoption** | 1.5k stars |
| **Last commit** | 2022-10-12 |
| **Links** | [repository](https://github.com/torch2424/wasmboy) · [benchmark](https://github.com/torch2424/wasmboy#benchmark) |

## Verdict

No numbers are committed. The repo's runner times the AssemblyScript Wasm core (asc -O3 --converge) against the same source compiled by tsc to JS, and the same JS run through Closure, per emulated frame in the browser (default 2,500 frames, mean of the last 85%). The only figures seen are search snippets of De Macedo et al. 2022: six games in Chrome, Edge and Firefox, Wasm faster overall but Firefox favouring JavaScript, with no CPU or version stated. The first-party Medium article was out by 2018-12-20 (issue #214 asks to link it), so it measured a JS core that still had the non-integer-index bug fixed in PR #218 two days later, unless it was revised afterwards (the maintainer promised an update in issue #216; the article could not be opened here).

## Use it when

- Embedding a Game Boy / Game Boy Color emulator in a web page or Node tool where GPL-3.0-or-later is acceptable, for homebrew or playable commercial ROMs that do not need cycle accuracy.
- As a reference case of a large real-world AssemblyScript codebase compiled to both Wasm and JS from one source, to study Wasm-versus-JS frame-time differences per browser with the demo/benchmark runner.
- Teaching or debugging GB internals: the debugger demo exposes per-cycle CPU, PPU, APU, timer and memory state, breakpoints and tile and background map views.
- Low-end devices where the documented performance options (audioBatchProcessing, audioAccumulateSamples, tileCaching) are acceptable; the repo's own Node table shows audio batch processing cutting 1,250 frames from 3,338 ms to 2,032 ms on back-to-color.gbc.

## Skip it when

- Accuracy-critical emulation: the README says 'the emulator is still not very accurate. Expect bugs' and the project never reached 1.0; serial interrupts are not implemented, so many mooneye tests fail.
- Closed-source or permissive-licence products: the core and lib are GPL-3.0-or-later.
- Projects that need a maintained toolchain: last code release 0.7.1 on 2022-03-25, only dependabot bumps afterwards (last 2022-10-12), pinned to assemblyscript ^0.15.1 and typescript ^3.1.3, and one runtime dependency is a git URL to the author's fork of audiobuffer-to-wav.
- Expecting a published Wasm-versus-JS speedup figure: the repo commits no benchmark numbers, the first-party Medium article is unreachable here, and the gain is browser-dependent (the 2022 De Macedo et al. study reports Firefox favouring JavaScript; issue #308 reports the JS cores at about half Chrome's FPS in Firefox).
- Using the JS (TypeScript-compiled) core as a product: the maintainer said it 'wasn't meant to be playable as a user', and its memory mock is byte-granular, so save-state load&lt;i32&gt;/store&lt;i32&gt; calls read and write a single clamped byte.

## How it is fast

The core is written as statically typed AssemblyScript (i32/u8 integer arithmetic on a flat linear memory, with the Game Boy memory map, VRAM, frame buffer and audio buffers at fixed offsets) and compiled by asc with -O3 --converge, so the Wasm build runs integer-only code with no deoptimisation risk. The JS build of the same source keeps the arithmetic but relies on explicit \*Portable helpers (param & 0xff, | 0) to mimic Wasm integer wrap-around, and every load/store goes through a JS function indexing a Uint8ClampedArray, so engine type speculation and bounds checks are what Wasm saves. Lib-level speedups (audio batch processing, accumulated samples, tile caching) are config options applied equally to all cores in the benchmark.

## Compared with alternatives

Pick WasmBoy over tinymt-wasm-typescript-benchmark, Speedy.js or rsmod-pathfinder when you want a whole application (CPU, PPU, APU, timers) compiled from one AssemblyScript source to both Wasm and JS, rather than a single kernel. Pick rsmod-pathfinder or tinymt when you need committed, reproducible numbers, which WasmBoy does not ship.

## Integration

| | |
|---|---|
| **Form** | npm module (wasmboy; ESM, CJS, UMD and IIFE bundles with the Wasm core inlined) or build the AssemblyScript core yourself |
| **Dependencies** | idb, raf, responsive-gamepad 1.1.0, audiobuffer-to-wav (git URL to torch2424's es-module-rollup branch); build needs assemblyscript ^0.15.1, typescript ^3.1.3, rollup and Closure Compiler plugins |
| **Minimum toolchain** | AssemblyScript 0.15.x for the core (newer versions not tested by the project); browsers with WebAssembly and Web Workers; Node needs worker_threads (--experimental-worker on old Node) |
| **Platforms** | Chrome, Firefox and Safari targeted; Node via the headless option |
| **Thread safety** | Lib runs the core in Web Workers; a core instance is single-threaded with module-level global state (one emulator per instance) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the first-party numbers: the Medium article (linked from issue #214, opened 2018-12-20) predates fix PR #218 (commit 838af61, 2018-12-22). Before it, the JS core indexed its typed array with non-integer offsets such as 59853.5 from a division in channel3.ts (issue #216), because Wasm's integer division became a float division in JS. The JS baseline therefore read undefined audio samples, so it did different work from the Wasm core, and it triggered a SpiderMonkey recompilation loop (Bugzilla 1515620). The maintainer also said he had forgotten to recompile the Closure build that night ('it was definitely my fault'), so the article's JS and Closure columns, Firefox's especially, were measured on a buggy or stale baseline.
- The JS core's memory mock is a Uint8ClampedArray: stores saturate where Wasm's store8 wraps, and load/store ignore the type parameter. JS-versus-Wasm equivalence rests on hand-placed i32Portable/u8Portable calls (114 in cpu/opcodes.ts), and the benchmark never checks that the cores produce identical frames or audio.
- demo/benchmark times each executeFrame() with the microseconds package, which in a browser uses performance.now(). Browsers coarsen that clock (Spectre mitigations), and one emulated frame takes only about 1.4-2.7 ms (the repo's Node table: 1,250 frames in 1,690-3,338 ms), so the min, max and mode rows are quantised; only the mean is usable. Cores run one after another rather than interleaved, the first 15% of each run is dropped, and canvas rendering plus a growing times array copied every frame (garbage-collector pressure) sit between timed frames.
- The benchmark applies one config to all cores (audioBatchProcessing, audioAccumulateSamples and tileCaching on, boot ROM off), so its results are not default-config emulator speed. test/performance/results.md shows these options alone change frame time by up to 1.7x.

## Known shortcomings

- Raised D to C on snippets only: the peer-reviewed De Macedo et al. 2022 (IEEE) study used WasmBoy (Wasm factor 0.84 vs JS 1, Firefox often favoured JS); no numbers in the repo; Medium article unreachable; thesis PDF at repositorium.sdum.uminho.pt blocked (B candidate). Licence GPL-3.0-or-later; abandoned (last commit 2022-10-12).
- Harness flaw: the first-party Medium article (out by 2018-12-20, issue #214) predates fix PR #218 (2018-12-22); before it the JS core indexed its typed array with non-integer offsets (59853.5 in channel3.ts, issue #216), so the JS baseline read undefined audio samples and did different work than the Wasm core, and SpiderMonkey hit a recompile loop; the maintainer admits a stale Closure build that night. The JS memory mock is a Uint8ClampedArray (saturates where Wasm wraps); no output-equality check; performance.now() per 1.4-2.7 ms frame is quantised; issue #308 shows JS in Firefox at about half of Chrome. The paper, TNS, techpowerup and scitepress pages are DNS-blocked, so the numbers remain snippet-only.

## Caveats and trade-offs

No figures in the README; benchmark_url is the README section, which links the benchmark app (wasmboy.app, unreachable) and a 2019 Medium article (unreachable). The only numbers seen are WebSearch snippets of the De Macedo et al. 2022 study (master's thesis at repositorium.sdum.uminho.pt, paper behind IEEE paywall), which used WasmBoy as its real-world benchmark; snippets do not state CPU model or versions and one summary was unsure whether the study used WasmBoy itself or only its harness design. Toolchain is old (assemblyscript ^0.15.1, typescript ^3.1.3); last real development before the October 2022 dependency bumps. GPL-3.0-or-later (copyleft). [retier] No figures in the README; the benchmark app (wasmboy.app) and the 2019 Medium article are unreachable, and the only numbers seen are WebSearch snippets of the De Macedo et al. 2022 study (language factor 0.84 for Wasm vs 1 for JavaScript in a regression over six games, three browsers), with no CPU model or versions. Harness flaw behind the first-party numbers: the Medium article (linked from issue #214, opened 2018-12-20) predates fix PR #218 (commit 838af61, 2018-12-22); before it the JS core indexed its typed array with non-integer offsets such as 59853.5 from a division in channel3.ts (issue #216) because Wasm's integer division became a float division in JS, so the JS baseline read undefined audio samples and did different work, and SpiderMonkey hit a recompile loop; the maintainer admits a stale Closure build that night. The JS core's memory mock is a Uint8ClampedArray (stores saturate where Wasm's store8 wraps), equivalence rests on hand-placed i32Portable/u8Portable calls, and the benchmark never checks that the cores produce identical frames or audio. demo/benchmark times each executeFrame() with performance.now(), coarsened by browsers, over 1.4-2.7 ms frames, so min, max and mode rows are quantised; cores run one after another rather than interleaved; one config (audio batching, tile caching on, boot ROM off) applies to all cores and changes frame time by up to 1.7x. Issue #308 shows JS in Firefox at about half of Chrome. Toolchain is old (assemblyscript ^0.15.1).

GPL-3.0 copyleft. Core can be built to WebAssembly or to JS from the same AssemblyScript source, which makes the comparison like for like.

## Maintenance

Abandoned: last code release 0.7.1 (2022-03-25), only dependabot merges to 2022-10-12, 76 open issues. GPL-3.0-or-later, so copyable only into GPL-compatible projects, and the evidence is snippet-only and browser-dependent; the first-party article's JS baseline predates a correctness fix (issue #216, PR #218).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The repo's benchmark runner (demo/benchmark/index.js, benchmarkRunner.js) times the same core as AssemblyScript Wasm vs TypeScript-compiled JS vs TS+Closure JS, but no numbers are committed and the first-party Medium article is unreachable. Search snippets of a peer-reviewed study (De Macedo, Abreu, Pereira, Saraiva, 'WebAssembly versus JavaScript: Energy and Runtime Performance', 2022, IEEE) report WasmBoy as its real-world benchmark with Wasm faster than JS; snippet-only numbers cap it at C (upgraded from D), a candidate for B once the paper or thesis PDF is readable.
- **Retiered** C to D: Enricher: the first-party article predates fix PR #218, before which the JS core indexed typed arrays with non-integer offsets and read undefined audio samples, so the JS baseline did different work than the Wasm core (crippled baseline), there is no output-equality check, and the only other numbers are search snippets of a 2022 study. No valid measurement reachable: C to D.
- **Verifier notes:** Confirmed and upgraded D to C on snippet-only peer-reviewed evidence; record as a paper-access retier candidate to B (De Macedo et al. 2022, thesis PDF https://repositorium.sdum.uminho.pt/bitstream/1822/86805/1/Joao%20Goncalves%20De%20Macedo.pdf, DNS-blocked here). Stars 1.5k, last commit 2022-10-12 (dependabot bumps) so abandoned is correct; package.json declares GPL-3.0-or-later. Shortcomings: no committed numbers, first-party article unreachable, gain browser-dependent (Firefox favoured JS in the study), stale toolchain.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/torch2424/wasmboy>
  - <https://github.com/torch2424/wasmboy/commits/master>
  - <https://github.com/torch2424/wasmboy/tree/master/demo/benchmark>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/README.md>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/package.json>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/demo/benchmark/benchmarkRunner.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/demo/benchmark/index.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/demo/benchmark/benchmarkResults.js>
- **Sources the enricher read:**
  - <https://github.com/torch2424/wasmboy>
  - <https://github.com/torch2424/wasmboy/tree/master/core>
  - <https://github.com/torch2424/wasmboy/commits/master>
  - <https://github.com/torch2424/wasmboy/issues?q=is%3Aissue+benchmark>
  - <https://github.com/torch2424/wasmboy/issues/216>
  - <https://github.com/torch2424/wasmboy/issues/308>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/README.md>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/package.json>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/demo/benchmark/index.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/demo/benchmark/benchmarkRunner.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/demo/benchmark/benchmarkResults.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/demo/benchmark/loadrom.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/rollup.config.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/rollup.core.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/rollup.getcore.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/rollup.benchmark.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/tsconfig.json>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/index.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/execute.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/portable/portable.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/portable/wasmMock.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/portable/getTsCore.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/portable/getWasmCore.js>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/memory/store.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/memory/load.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/cpu/opcodes.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/cpu/cbOpcodes.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/cpu/cpu.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/graphics/graphics.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/sound/sound.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/core/sound/channel3.ts>
  - <https://raw.githubusercontent.com/torch2424/wasmboy/master/test/performance/results.md>
  - <https://raw.githubusercontent.com/kamicane/microseconds/master/now.js>
  - <https://raw.githubusercontent.com/kamicane/microseconds/master/index.js>
  - <https://registry.npmjs.org/microseconds/latest>
  - <https://registry.npmjs.org/wasmboy>
  - WebSearch: torch2424 "WebAssembly is fast" real-world benchmark (snippets: changelog.com news item, thenewstack.io)
  - WebSearch: WasmBoy De Macedo Abreu Pereira Saraiva (snippets: thenewstack.io, repositorium.sdum.uminho.pt thesis, techpowerup forum thread)
  - https://thenewstack.io/javascript-vs-wasm-which-is-more-energy-efficient-and-faster/ (DNS-blocked)
  - https://changelog.com/news/EaPk (DNS-blocked)
  - https://www.techpowerup.com/forums/threads/wasmboy-benchmarking-results.308903 (DNS-blocked)
  - https://scitepress.org/publishedPapers/2023/122056/pdf/index.html (DNS-blocked)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/torch2424/wasmboy`) · [data/wave13/enrich/raw/github_com_torch2424_wasmboy.json](../../../data/wave13/enrich/raw/github_com_torch2424_wasmboy.json) (enrichment confidence 0.6)

</details>
