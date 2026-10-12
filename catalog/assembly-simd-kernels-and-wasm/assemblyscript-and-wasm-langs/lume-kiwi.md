# LUME Kiwi (@lume/kiwi, TypeScript Cassowary constraint solver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript` · `BSD-3-Clause` · 🟡 stale

> TypeScript Cassowary linear-constraint solver for UI layout; 10x faster setup, 2.3x faster re-solve than Cassowary.js.

| | |
|---|---|
| **Beats** | Cassowary.js (slightlyoff/cassowary.js), the JavaScript Cassowary implementation |
| **Claimed result** | Creation: Cassowary.js 2,597 ops/sec vs kiwi 26,243 ops/sec (printed as about 10.11x faster); the 'kiwi new API' row is 20,840 ops/sec (about 8.0x, derived from page data). Solving: Cassowary.js 260,002 vs kiwi 595,455 ops/sec (printed as about 2.29x faster). |
| **Workload** | Benchmark.js ops/sec for creating constraint problems (creation benchmark) and for solving them (solving benchmark), Kiwi against Cassowary.js in Node.js; the README says an AssemblyScript/WebAssembly build is planned ('Soon it will be compiled to WebAssembly'). |
| **Metric** | throughput |
| **Compiler and flags** | TypeScript 5 build run under Node.js via `npm run bench`; Node.js version and flags not stated |
| **Adoption** | 214 stars (GitHub assemblyscript topic page) |
| **Last commit** | 2025-05-20 |
| **Links** | [repository](https://github.com/lume/kiwi) · [benchmark](https://github.com/lume/kiwi) |

## Verdict

The README's 'Sample result output' (added 2023-10-23; Node.js version and hardware not stated) runs Benchmark.js on a single two-subview layout. Building the solver ran at 26,243 ops/s for kiwi versus 2,597 for Cassowary.js 0.0.2 (10.1x; 8.0x with kiwi's createConstraint API). Two suggestValue and re-solve rounds ran at 595,455 versus 260,002 ops/s (2.29x). Part of the creation gap comes from Cassowary.js's default autoSolve, which re-optimizes and rewrites all variables after every added constraint.

## Use it when

- Auto-layout in the browser or Node.js (Apple Auto Layout-style constraints between views) with tens to hundreds of variables, where constraints are built once and edit variables are then dragged or resized interactively.
- Replacing Cassowary.js in an existing JavaScript codebase where building solvers is a hot path (README sample: 10.1x more solver constructions per second).
- Interactive suggestValue and re-solve loops: the dual-simplex re-solve ran 2.29x Cassowary.js in the README sample.
- Projects that want a dependency-free, BSD-3-Clause ES module with TypeScript types (the npm 0.4.4 tarball is about 125 KB unpacked, including the TypeScript sources and source maps).

## Skip it when

- When you want WebAssembly or AssemblyScript: there is none. The README has said 'Soon it will be compiled to WebAssembly' since 2021-05-30, and the repo holds only TypeScript.
- Integer, nonlinear or general optimization problems: it is a linear Cassowary solver only, and open issues ask for integer constraints (#10), an objective function (#5) and distance constraints (#9).
- When a strict strength hierarchy is required: strengths are a single double, so a lower-level error that is about 1000x larger can outweigh a higher-level one.
- Very large or degenerate systems: Solver.maxIterations is 1000 (its doc comment says 10,000), and a single optimize that needs more pivots throws 'solver iterations exceeded'.
- When you need active maintenance: the last npm release is 0.4.4 (2024-09-17), the last commit is from 2025-05-20, and the package is ESM-only with no UMD or CommonJS build since 0.4.0.

## How it is fast

It follows Chris Colbert's kiwi redesign of Cassowary. Only the incremental primal simplex (add and remove constraint) and the dual simplex (suggestValue) are kept, stay constraints are dropped, and each strength is folded into one double (Strength.create: strong 1e6, medium 1e3, weak 1). Rows and symbol tables are an IndexedMap: a dense array of pairs plus a plain-object index keyed by integer id, which gives O(1) lookup and linear iteration without generic hashing. Variable values are written only when updateVariables() is called. Cassowary.js 0.0.2, by contrast, defaults to autoSolve = true and re-optimizes and rewrites every external variable after each addConstraint.

## Compared with alternatives

No catalogued sibling solves constraints. The category's other entries (as-proto, json-as, xoroshiro128starstar) ship real AssemblyScript or WebAssembly builds, while Kiwi is plain TypeScript beating another JavaScript library. Pick it when you need a Cassowary layout solver in JavaScript, not as an example of a Wasm speed-up.

## Integration

| | |
|---|---|
| **Form** | module (npm ES module @lume/kiwi; compiled dist/ plus TypeScript sources) |
| **Dependencies** | none at run time (benchmark, cassowary 0.0.2, mocha and TypeScript 5 are dev-only) |
| **Minimum toolchain** | A JavaScript runtime with ES modules. It is compiled by TypeScript 5 at target esnext, so older runtimes need transpiling. It is ESM-only since 0.4.0 (the UMD global build was removed). |
| **Platforms** | any JavaScript runtime with ES modules (browsers via import maps or bundlers, Node.js, Deno) |
| **Thread safety** | Not documented. A Solver is mutable single-threaded JavaScript state. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the 10x creation figure. bench/main.js leaves Cassowary.js at its default autoSolve = true (confirmed in the cassowary 0.0.2 npm build), so each of its 18 addConstraint and addEditVar calls also runs optimize plus _setExternalVariables over every variable. Kiwi optimizes per added constraint but writes variable values once, in updateVariables(). The ratio therefore partly measures an API default; Cassowary.js was never timed with autoSolve off and a single resolve(). In the other direction, kiwi's creation path pays for two assert.equal calls that Cassowary.js skips, because its checks are commented out after the return statement.
- Narrow, stale benchmark. It pins cassowary@0.0.2, an npm build published 2013-02-02 from slightlyoff/cassowary-js-refactor. The workload is one tiny layout (18 variables, 16 constraints, 2 edit variables). The README numbers were added in commit 45fa466 (2023-10-23) with no Node.js version, hardware or date, so scaling to large layouts is untested.
- Errors are thrown, not returned: addConstraint throws 'unsatisfiable constraint' or 'duplicate constraint', suggestValue throws 'unknown edit variable', and optimize throws 'solver iterations exceeded' after 1000 pivots. Wrap interactive edits in try/catch.
- The npm package lags GitHub: Variable.subscribe and unsubscribe (PR #8, merged 2025-05-20) are on main but absent from npm's latest release, 0.4.4 (2024-09-17).

## Known shortcomings

- README numbers match (10.11x creation, 2.29x solving vs Cassowary.js) but there is no hardware or Node version; plain TypeScript with no Wasm build, so a poor fit for the category; a continuation of IjzerenHein/kiwi.js. Stale since 2025-05-20.
- Harness asymmetry: bench/main.js leaves Cassowary.js 0.0.2 (an npm build from 2013-02-02) at its default autoSolve = true (confirmed in the npm build), so each of its 18 addConstraint/addEditVar calls also runs optimize and _setExternalVariables, while kiwi writes values once in updateVariables(); the 10x creation ratio partly measures that default. Tiny workload (18 variables, 16 constraints); README numbers added in 45fa466 (2023-10-23) with no hardware or Node version; no wasm build exists. maxIterations is 1000 (the doc comment says 10,000); npm 0.4.4 lacks the Variable.subscribe now on main.

## Caveats and trade-offs

The numbers are a 'sample result output' in the README with no hardware, Node.js version or date; they are not in the predecessor IjzerenHein/kiwi.js README, so they were added by the LUME maintainer after May 2021. First-party benchmark with partial methodology. The harness (bench/main.js) builds the same two-subview layout in both libraries and the solving test runs two suggestValue/resolve cycles on each, so the work looks equivalent, but the result checks are commented out. The category fit is weak: the speed-up is a TypeScript implementation over another JS library (Cassowary.js), not WebAssembly; the AssemblyScript/WebAssembly build has only been announced since May 2021. Lineage: the repo continues IjzerenHein/kiwi.js (its git history includes IjzerenHein's commits and the commit 'Removed c++ and python code', and the kiwi.js README now says it is unmaintained and points to lume/kiwi), which was a TypeScript port of nucleic/kiwi's C++ solver. Licence text is in COPYING.txt (Modified BSD, BSD-3-Clause; there is no LICENSE file), matching package.json.

Pure TypeScript/JavaScript, no wasm delivered yet; API differs from Cassowary.js (a 'new API' variant is also benchmarked at 20,840 ops/sec for creation).

## Maintenance

Stale (last commit 2025-05-20, last npm release 0.4.4 on 2024-09-17, 214 stars) but BSD-3-Clause, dependency-free and about 1,700 lines of TypeScript, so easy to vendor. The WebAssembly build announced in May 2021 still does not exist.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Sample result output' prints Benchmark.js ops/sec for kiwi vs Cassowary.js from the repo's own harness bench/main.js (npm run bench), but gives no hardware, Node.js version, date or browser, so first-party with partial methodology: C.
- **Verifier notes:** Numbers match the README exactly; the harness compares like for like in Node.js. Shortcomings: no hardware or runtime version, sample output of unknown date, weak fit for the wasm-langs category (no Wasm build exists), stale (last commit 2025-05-20), 214 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-95 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/lume/kiwi>
  - <https://github.com/lume/kiwi/commits>
  - <https://github.com/lume/kiwi/commits/main/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/package.json>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/bench/main.js>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/COPYING.txt>
  - <https://raw.githubusercontent.com/IjzerenHein/kiwi.js/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/lume/kiwi>
  - <https://github.com/lume/kiwi/tree/main/src>
  - <https://github.com/lume/kiwi/commits/main>
  - <https://github.com/lume/kiwi/commits/main/README.md>
  - <https://github.com/lume/kiwi/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/package.json>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/bench/main.js>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/COPYING.txt>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/tsconfig.json>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/src/solver.ts>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/src/variable.ts>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/src/strength.ts>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/src/maptype.ts>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/src/constraint.ts>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/src/expression.ts>
  - <https://raw.githubusercontent.com/lume/kiwi/HEAD/src/kiwi.ts>
  - <https://raw.githubusercontent.com/lume/kiwi/8aaaced/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/66cae42/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/cee5245/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/87dfb85/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/f3ddee1/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/a29e49e/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/45fa466/README.md>
  - <https://raw.githubusercontent.com/lume/kiwi/282ba66/README.md>
  - <https://registry.npmjs.org/@lume%2fkiwi>
  - <https://registry.npmjs.org/@lume/kiwi/-/kiwi-0.4.4.tgz>
  - <https://registry.npmjs.org/cassowary>
  - <https://registry.npmjs.org/cassowary/-/cassowary-0.0.2.tgz>
  - <https://github.com/nucleic/kiwi>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lume/kiwi`) · [data/wave13/enrich/raw/github_com_lume_kiwi.json](../../../data/wave13/enrich/raw/github_com_lume_kiwi.json) (enrichment confidence 0.8)

</details>
