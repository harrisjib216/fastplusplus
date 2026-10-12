# wasmoon

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (official Lua 5.4) compiled to WebAssembly, TypeScript bindings` · `MIT` · 🟡 stale

> Official PUC Lua 5.4 compiled to WebAssembly with JS bindings; runs pure-Lua code about 10x faster than Fengari.

| | |
|---|---|
| **Beats** | Fengari (Lua VM rewritten in JavaScript) |
| **Claimed result** | README: wasmoon 15.267 ms vs fengari 389.923 ms (about 25x, one cold run each); the project's newer harness on the 2.0 branches (5 warm-up, 100 iterations) gives 13.41 vs 137.36 ms, about 10x |
| **Workload** | Heap sort (bench/heapsort.lua): one timed call that sorts 2,000 random numbers ten times and asserts the order, including parsing the Lua source; harness bench/comparisons.js times a single cold run of each VM with console.time (fengari first, then wasmoon) in one Node process. |
| **Metric** | latency |
| **Compiler and flags** | emcc -O3 with emmalloc, WASM_BIGINT, ALLOW_MEMORY_GROWTH (build.sh release path); the README does not say which build produced the table, and its local build instructions use the -O0 dev build |
| **Adoption** | 701 stars |
| **Last commit** | 2025-01-18 |
| **Links** | [repository](https://github.com/ceifa/wasmoon) · [benchmark](https://github.com/ceifa/wasmoon) |

## Verdict

First-party only: on main, bench/heapsort.lua (ten heap sorts of 2,000 random numbers plus an order check, parse included) timed once per VM with console.time gave wasmoon 15.267 ms vs Fengari 0.1.4 389.923 ms (README, Nov 2022, \~25.5x); the 2.0 branches' warm 100-iteration harness gives 13.41 vs 137.36 ms (10.24x, Fengari 0.1.5). Neither table names the CPU, Node.js version or wasm build used (main's release build is emcc -O3, 2.0's is -Oz).

## Use it when

- Running compute-heavy Lua scripts (game logic, config evaluation, user scripting) inside Node.js, Deno or a browser where native Lua or a Node addon is not an option.
- You need real Lua 5.4 semantics (integers, goto, to-be-closed variables, 5.4 standard library) rather than Fengari's Lua 5.3 reimplementation.
- Long-running Lua code with few JS&lt;-&gt;Lua crossings per unit of work, so the roughly 10x VM speedup is not eaten by marshalling.
- Sandboxing: an instruction-count hook gives per-call timeouts (functionTimeout / run({timeout})) and an optional custom allocator caps Lua memory (traceAllocations with memoryMax).

## Skip it when

- Interop-heavy code (Lua calling many small JS functions or walking JS objects): the README warns the gain can vanish, and a third-party BabylonJS forum benchmark (search snippet only) had Fengari ahead on JS calls from Lua (13.3 vs 35.4, lower is better, units not given).
- Bundle size matters more than speed: main README lists 393 kB plain / 130 kB gzipped vs Fengari's 214 kB / 69 kB, and the wasm file must be hosted or fetched (browser default loads glue.wasm from unpkg.com).
- You need to await a Promise inside a JS-to-Lua callback or yield at a C boundary: README documents 'attempt to yield across a C-call boundary' and 'cannot resume dead coroutine' errors.
- You want the fastest Lua possible on a server: native Lua or LuaJIT outside the JS engine will be faster, and no wasmoon-vs-native-Lua number is published.
- Stable npm tooling matters: npm 'latest' is still 1.16.0 (2023-12-08), main stopped on 2025-01-18, and the 2.0 rewrite exists only as 2.0.0-next.0 and two feature branches.

## How it is fast

Instead of interpreting Lua bytecode in JavaScript objects (Fengari), it runs PUC Lua's own C interpreter (luaV_execute, Lua's own GC and table code) as WebAssembly, so the VM loop is compiled ahead of time by clang/binaryen and then by V8's wasm tiers. Main builds use emcc -O3 with emmalloc and WASM_BIGINT; the 2.0 branches build with -Oz -fno-inline-functions and a gufa-optimizing binaryen pass for size. The cost moves to the JS/wasm boundary: every value crossing it goes through cwrap calls, string copies into linear memory and type-extension lookups.

## Compared with alternatives

No other Lua-in-JS runtime is catalogued here; like markdown-wasm or libxml2-wasm it is the pattern of compiling the reference C implementation to wasm in place of a pure-JS port, and you pick it when you need real Lua 5.4 in a JS host. If you can run native code, the catalogued lua/lua itself is the faster choice.

## Integration

| | |
|---|---|
| **Form** | module (npm package with a separate glue.wasm; also a wasmoon CLI) |
| **Dependencies** | none at runtime beyond the bundled glue.js/glue.wasm (@types/emscripten for typings); building needs Emscripten (or Docker emscripten/emsdk) and the lua/lua git submodule |
| **Minimum toolchain** | Runtime: WebAssembly with BigInt integration (built with WASM_BIGINT); CI uses Node.js 22. Main is ESM-only since Jan 2025 (npm 1.16.0 predates that). |
| **Platforms** | any WebAssembly host: Node.js, Deno, browsers, web workers; bundlers need fallbacks for path/fs/child_process/crypto/url/module (README) |
| **Thread safety** | not documented; each engine wraps one lua_State in one wasm instance, so treat it as single-threaded and use one engine per worker |
| **Drop-in for the baseline** | partial — same Lua language (5.4 vs Fengari's 5.3) and a similar raw C API, but a different JS API, module loading and value-conversion layer |

## Gotchas

- The README's 25.5x (15.267 ms vs 389.923 ms) is one cold console.time run per VM in one process, Fengari first, so Fengari's JS tier-up is inside the timing. The project's own newer harness on the 2.0 branches (5 warm-ups, 100 iterations, fresh state per iteration, same heapsort.lua) reports 13.41 ms vs 137.36 ms average, 10.24x; the cold single run inflated Fengari's time about 2.8x (derived from page data).
- Harness history and state: before commit c9d49bb (Nov 2022, issue #58 by gottfriedleibniz) the benchmark only loaded the chunk and never ran the sort (old table: 0.177 ms vs 2.107 ms on 20k numbers). At main HEAD, bench/comparisons.js and bench/steps.js still use require/__dirname, but package.json has been "type": "module" since 012fd13 (Jan 2025) with no bench/package.json, so they should fail with 'require is not defined in ES module scope' (code reading, not run). The table cannot be reproduced from main.
- Both harnesses call the raw C API (luaL_loadstring + lua_callk/lua_pcallk) and bypass doString/thread.run and the type extensions that real users go through; no published number covers the interop layer.
- npm 1.16.0 lacks main's later fixes (memory leak after running code on a new thread #109, Jan 2025); open issues include multi-return values (#84), JS constructors (#123), removing keys after interop (#82) and an alignment fault on close (#128). In src/thread.ts the timeout hook closure keeps the deadline it was first created with and is never released with removeFunction (code reading).

## Known shortcomings

- README 15.267 ms vs fengari 389.923 ms (about 25.5x, derived from page data) from one cold run per VM, timing 10 sorts plus parse, no CPU, Node or fengari version, no comparison to native Lua; first-party (bench/comparisons.js, emcc -O3). WASM packaging of the catalogued lua/lua. Stale.
- Enricher: the README 25.5x (15.267 vs 389.923 ms) is one cold console.time run per VM with Fengari first; the project's own newer harness on the 2.0 branches (5 warm-up, 100 iterations) gives 13.41 vs 137.36 ms, 10.24x; main's bench scripts use require under a "type": "module" package.json (would fail at HEAD); before c9d49bb (November 2022) the bench never ran the sort; the bench calls the raw C API and bypasses the interop layer; npm latest 1.16.0 (2023) with 2.0.0-next.0 (2026-04) changing the API.

## Caveats and trade-offs

One single-shot micro-benchmark (no repetitions or warm-up) with no CPU model, Node.js, browser or fengari version and no date. The timed region covers all ten sorts plus parsing, so it is the total of the ten runs, not per run. The README warns that heavy JS-Lua interop can erase the advantage, and fengari is smaller (214 kB vs 393 kB plain). First-party. Lua itself (lua/lua) is already catalogued, and no comparison against native Lua (the category's same-library-native baseline) is given.

Larger bundle than Fengari (393 kB plain and 130 kB gzipped vs 214 kB and 69 kB); JS-to-Lua interop is expensive and can erase the gain; needs WebAssembly; wraps the real Lua 5.4 so semantics match PUC Lua rather than Fengari's Lua 5.3.

## Maintenance

Main is quiet since 2025-01-18 and npm 'latest' is 1.16.0 from 2023, but development continues on the better-async-model and new-apis-2 branches (updated Sep 2026) with a 2.0.0-next.0 pre-release (2026-04-25); MIT-licensed and copyable, but expect API breaks in 2.0 and do not rely on main's bench scripts, which no longer run under the ESM package.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README table (wasmoon 15.267 ms vs fengari 389.923 ms) is first-party; the harness (bench/comparisons.js, bench/heapsort.lua) and the release build flags (build.sh: emcc -O3) are public, but no CPU model, Node.js or fengari version is stated, so not A.
- **Verifier notes:** Numbers match the README exactly; the bench code resolves the 'per run or ten runs' ambiguity (ten runs in one timed call). Main shortcomings: single cold run, no hardware or runtime versions, first-party only, no native-Lua comparison.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-23 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ceifa/wasmoon>
  - <https://github.com/ceifa/wasmoon/commits>
  - <https://github.com/ceifa/wasmoon/tree/main/bench>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/README.md>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/bench/comparisons.js>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/bench/heapsort.lua>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/build.sh>
- **Sources the enricher read:**
  - <https://github.com/ceifa/wasmoon>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/README.md>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/bench/comparisons.js>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/bench/steps.js>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/bench/heapsort.lua>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/package.json>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/rolldown.config.ts>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/.github/workflows/publish.yml>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/src/engine.ts>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/src/factory.ts>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/src/global.ts>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/src/thread.ts>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/HEAD/src/luawasm.ts>
  - <https://github.com/ceifa/wasmoon/tree/main/bench>
  - <https://github.com/ceifa/wasmoon/commits/main>
  - <https://github.com/ceifa/wasmoon/commits/main/bench/comparisons.js>
  - <https://github.com/ceifa/wasmoon/commit/c9d49bb>
  - <https://github.com/ceifa/wasmoon/issues/58>
  - <https://github.com/ceifa/wasmoon/issues>
  - <https://github.com/ceifa/wasmoon/branches>
  - <https://github.com/lua/lua/commit/be908a7>
  - <https://registry.npmjs.org/wasmoon>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/README.md>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/package.json>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/bench/index.js>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/bench/comparisons.js>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/bench/utils.js>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/bench/heapsort.lua>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/utils/build-wasm.js>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/c66b3e32e48234b04686a794ff56054b82803ce2/utils/build-wasm.sh>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/better-async-model/README.md>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/new-apis-2/README.md>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/better-async-model/package.json>
  - <https://raw.githubusercontent.com/ceifa/wasmoon/new-apis-2/package.json>
  - WebSearch snippet: https://forum.babylonjs.com/t/babylua-lua-implementation-for-babylonjs/61706 (fetch failed: ENOTFOUND)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ceifa/wasmoon`) · [data/wave13/enrich/raw/github_com_ceifa_wasmoon.json](../../../data/wave13/enrich/raw/github_com_ceifa_wasmoon.json) (enrichment confidence 0.8)

</details>
