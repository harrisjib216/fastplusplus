# svgo.mbt (@rivus/svgo)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `MoonBit (wasm-gc)` · `MIT` · 🟢 active

> svgo's 34-plugin preset-default rewritten in MoonBit as a 188 KB wasm-gc module; 1.7-4.8x faster than svgo 4.1.0 in Node.

| | |
|---|---|
| **Beats** | svgo 4.1.0 (JavaScript, Node 24) |
| **Claimed result** | '3.6x faster than svgo at the median', range 1.7x to 4.8x per file. Table (svgo.mbt wasm-gc vs svgo-js, ms): sketch-icon.svg 0.095 vs 0.286 (3.0x); inkscape-drawing.svg 0.165 vs 0.637 (3.9x); SVG_logo.svg 0.470 vs 1.695 (3.6x); Tux.svg 5.679 vs 12.833 (2.3x); Ghostscript_Tiger.svg 10.096 vs 41.113 (4.1x); World map 10.605 vs 50.433 (4.8x). Output within 1.3% of svgo size. |
| **Workload** | SVG optimisation with svgo preset-default (34 plugins), multipass, same plugin set (svgo run with moveGroupAttrsToElems off), same Node process, ms per call over ten corpus files. |
| **Metric** | latency |
| **Compiler and flags** | MoonBit wasm-gc build (svgo.wasm 188,316 bytes per app/website/data.json, built by scripts/build-wasm.sh; MoonBit toolchain version and flags not stated); harness node packages/compare/collect.mjs on Node v24.18.0 with svgo 4.1.0, data generated 2026-09-27; one warmup call then the mean of 20/100/300 calls by file size, svgo.mbt timed before svgo-js in the same process |
| **Adoption** | 1 star; \~831 npm downloads per month |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/PerfectPan/svgo.mbt) · [benchmark](https://github.com/PerfectPan/svgo.mbt) |

## Verdict

In one Node v24.18.0 process on unstated hardware, the wasm-gc build of svgo.mbt against svgo 4.1.0 (preset-default with moveGroupAttrsToElems off, multipass on) took 0.158 to 10.6 ms against 0.265 to 50.4 ms per call over ten SVGs of 366 B to 85 KB: 1.68x to 4.76x faster, median 3.59x, 28.2 vs 110.6 ms summed over the ten files (derived from page data), with output 0.4% larger in total.

## Use it when

- Build pipelines, bundler plugins or asset servers on Node 24+, Bun 1.4+ or Deno 2 that run svgo's default preset over many icons or illustrations: 3.6x median per-call speedup, up to 4.8x on an 85 KB path-heavy map.
- Optimising SVGs in the browser (editors, playgrounds, upload previews) where a 188 KB (69 KB gzipped) self-contained wasm module is easier to ship than svgo plus css-tree/csso.
- CI or pre-commit hooks that optimise a few files per run, where the native CLI's \~10 ms cold start beats the svgo CLI's \~160 ms (scripts/cli-bench.sh, mean of 20 fresh processes).
- MoonBit projects that want an SVG DOM, path optimiser and plugin pipeline as a library, including custom plugins written in MoonBit.

## Skip it when

- You depend on custom JavaScript plugins or svgo's opt-in plugins other than removeDimensions, removeTitle and moveGroupAttrsToElems: the npm build runs only the built-in plugins, and 17 opt-in plugins are missing.
- Older engines: the module needs WebAssembly GC plus JS String Builtins, and fails at instantiate on Node 22/23, Bun 1.2 and browsers older than Chrome 130, Firefox 134 or Safari 18.4; there is no JS fallback build on npm.
- You need byte-identical output to svgo (snapshot tests, cache keys): per-file output differs from svgo by -4.2% to +1.3% on the corpus (sketch-icon 276 vs 288 B, Ghostscript tiger 52,690 vs 52,029 B), 0.4% larger in total.
- Risk-averse production use: one maintainer, 1 star, first commits in September 2026, version 0.3.1, and a path-data correctness bug fixed only on 2026-09-27.
- Tiny icons where both tools finish in well under a millisecond (0.158 vs 0.265 ms on a 570 B file, 1.7x); the gain only matters at volume or on large files.

## How it is fast

The pipeline (parse, plugin passes, serialise) is compiled ahead of time to WebAssembly GC with JS String Builtins, so a MoonBit String is a JS string and the call boundary is two strings in and one out, with config and results encoded as length-prefixed tokens instead of JSON. The XML parser dispatches on the code unit after '&lt;', slices substrings and never backtracks (68 KB parses in about 0.25 ms per docs/ARCHITECTURE.md). Path numbers are scanned by folding up to 15 significant digits into an Int64 with one exact power-of-ten division, and the writer computes a packed length 'shape' so the absolute-vs-relative choice per segment needs no string building; a per-call cache skips path data that convertPathData already left unchanged, so passes 2 and 3 cost little. SVG vocabulary tables are kept as compact strings and expanded lazily.

## Compared with alternatives

Most siblings in this category are language-level comparisons (MoonBit core, J2CL WasmGC, Kotlin/Wasm, wasm_of_ocaml) or ports of other tools (sasso against dart-sass, markdown_yo against markdown-it); pick svgo.mbt when you actually need svgo's optimisations faster, or want a real-world case of MoonBit wasm-gc beating a mature JS library on the same V8. Outside the catalogue, the Rust optimiser oxvg (napi and wasm builds) claims up to 50x over svgo and is the other option to evaluate.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at run time (index.mjs loader plus svgo.wasm; the host supplies Math trig functions, Number.parseFloat and String for number formatting); MoonBit library has no external dependencies listed |
| **Minimum toolchain** | Node 24+, Bun 1.4+, Deno 2, Chrome 130+, Firefox 134+, Safari 18.4+; MoonBit library tracks the latest MoonBit release (CI installs it); no pinned toolchain version |
| **Platforms** | any engine with WebAssembly GC and JS String Builtins; native CLI binaries for linux x86_64, linux arm64 and macOS arm64, other platforms via moon build --target native |
| **Thread safety** | not documented; init() instantiates one module per JS realm and optimize is a pure string-to-string call with no I/O |
| **Drop-in for the baseline** | partial: same plugin names, parameter shapes, precision and multipass options, but optimize is async (await it), the result object adds originalSize/size/passes/applied, moveGroupAttrsToElems is off by default (svgo has it on), custom JS plugins are not supported and most opt-in plugins are missing |

## Gotchas

- Benchmark method (packages/compare/collect.mjs, output app/website/data.json): mean ms of 20/100/300 calls per file after untimed warm-up calls, svgo.mbt timed before svgo in the same Node v24.18.0 process, one run with no variance reported, and no CPU or MoonBit compiler version recorded. The plugin sets are matched (svgo given preset-default with moveGroupAttrsToElems off) and output sizes are within 1.3% per file, so the comparison is like-for-like apart from small output differences.
- The other same-process speed script, packages/compare/wasm-speed.mjs (the one docs/ARCHITECTURE.md names and 'npm run speed' runs), calls svgo with { multipass: true } only, so svgo runs its full preset including moveGroupAttrsToElems while svgo.mbt does not; on the Ghostscript tiger that plugin changes svgo's output from 52,029 to 68,101 B. Its ratios are not like-for-like; reproduce the README numbers with collect.mjs.
- Multipass stops on different criteria: svgo.mbt repeats the pipeline while any plugin reports a change (at most 10 passes; 2-3 on the corpus), svgo repeats while the output shrinks. The cross-pass cache of unchanged path data lives in the per-call Context; the JS loader does not memoise results across calls, so repeated benchmark calls do real work.
- Version 0.3.1 (PR #31, 2026-09-27) fixed path data where a number in scientific notation was glued onto a preceding fractional number ('.03127e-5' for '.0312 7e-5'), which changed geometry or dropped the rest of the path, mainly at precision 5 and above; use 0.3.1 or later. docs/ARCHITECTURE.md is partly stale (its diagram says 25 plugins, and it lists matrix folding as not implemented while the README says convertPathData bakes element transforms into path data).

## Known shortcomings

- Table and the 3.6x median reproduce from app/website/data.json (Node v24.18.0, svgo 4.1.0) but no hardware or MoonBit version is given; mean of N runs after one warmup.
- The published numbers reproduce from packages/compare/collect.mjs with matched plugin sets (median 3.59x); no hardware or MoonBit version, mean of N after warm-up, one run. packages/compare/wasm-speed.mjs ('npm run speed', named in ARCHITECTURE.md) runs svgo's full default with moveGroupAttrsToElems on, so it is not like-for-like, but the README numbers do not use it. v0.3.1 (PR #31) fixed a path-data bug where scientific-notation numbers were glued to a preceding fraction.

## Caveats and trade-offs

First-party numbers; hardware and MoonBit toolchain version not stated; timings are a mean after a single warmup, not a median. svgo runs preset-default with moveGroupAttrsToElems off to match svgo.mbt's default (svgo's own default output is larger on the Ghostscript tiger, so this does not favour svgo.mbt). Output sizes in app/website/data.json are within 1.3% of svgo per file (tiger 52,690 vs 52,029 B, derived from page data) and 0.4% larger in total; the README reports 0 differing pixels on the website samples and only sub-pixel precision effects on the benchmark corpus. Requires WebAssembly GC and JS String Builtins (Node 24+, Bun 1.4+, Deno 2). Young repo (98 commits, history from at least September 2026), 1 star; npm download count not checked (npm API blocked here).

Needs WebAssembly GC and JS String Builtins (Node 24+, Bun 1.4+, Deno 2, Chrome 130+, Firefox 134+, Safari 18.4+). Only the 34 built-in preset-default plugins run; custom JavaScript plugins cannot run inside the wasm module. A native MoonBit CLI is also provided (about 10 ms cold start vs about 160 ms for the svgo CLI).

## Maintenance

Active solo project (98 commits since September 2026, v0.3.1, last commit 2026-10-01, 1 star), MIT, with CI running svgo's fixture suite through the shipped wasm under Node, Bun and Deno; usable as an npm dependency now, but young enough that versions should be pinned.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party table in the README (svgo/README.mbt.md) backed by the public harness packages/compare/collect.mjs and its output app/website/data.json (Node v24.18.0, svgo 4.1.0), but no hardware and no MoonBit toolchain version, so not A.
- **Verifier notes:** All six table rows and the 1.7x-4.8x range / 3.6x median reproduce from app/website/data.json (median 3.59x over ten files, derived). Confirm at C; shortcomings: no hardware or toolchain version, mean-of-N timing with one warmup, tiny repo.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/PerfectPan/svgo.mbt>
  - <https://github.com/PerfectPan/svgo.mbt/commits/main>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/README.md>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/svgo/README.mbt.md>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/compare/collect.mjs>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/compare/package.json>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/app/website/data.json>
- **Sources the enricher read:**
  - <https://github.com/PerfectPan/svgo.mbt>
  - <https://github.com/PerfectPan/svgo.mbt/commits/main>
  - <https://github.com/PerfectPan/svgo.mbt/issues?q=is%3Aissue>
  - <https://github.com/PerfectPan/svgo.mbt/issues/45>
  - <https://github.com/PerfectPan/svgo.mbt/tree/main/packages/svgo-mbt>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/README.md>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/svgo/README.mbt.md>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/docs/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/compare/collect.mjs>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/compare/wasm-speed.mjs>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/compare/package.json>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/app/website/data.json>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/scripts/build-wasm.sh>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/scripts/cli-bench.sh>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/svgo-mbt/index.mjs>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/svgo-mbt/package.json>
  - <https://raw.githubusercontent.com/PerfectPan/svgo.mbt/HEAD/packages/svgo-mbt/CHANGELOG.md>
  - <https://github.com/noahbald/oxvg>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/perfectpan/svgo.mbt`) · [data/wave13/enrich/raw/github_com_perfectpan_svgo_mbt.json](../../../data/wave13/enrich/raw/github_com_perfectpan_svgo_mbt.json) (enrichment confidence 0.7)

</details>
