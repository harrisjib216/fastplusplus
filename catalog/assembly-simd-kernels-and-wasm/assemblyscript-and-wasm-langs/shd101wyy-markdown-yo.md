# markdown_yo (Yo-language Markdown renderer, WASM build)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Yo (new systems language) compiled to WebAssembly via Emscripten and to native` · `MIT` · 🟢 active

> Markdown-to-HTML converter in the Yo language (native and WebAssembly) that outputs markdown-it-compatible HTML 4.5-7.6x faster natively.

| | |
|---|---|
| **Beats** | markdown-it (JavaScript Markdown parser on Node.js/V8) |
| **Claimed result** | WASM vs markdown-it: 64 KB 12.9 vs 1.6 ms (0.1x, slower), 256 KB 13.1 vs 6.7 ms (0.5x), 1 MB 13.5 vs 28.8 ms (2.1x), 5 MB 32.6 vs 158.9 ms (4.9x), 20 MB 121.5 vs 722.8 ms (6.0x); native build 4.5x to 7.6x |
| **Workload** | Markdown-to-HTML conversion of one synthetic \~1.2 KB block (headings, nested lists, blockquote, code fence, table, links, an image and entities, no raw HTML), repeated to 64 KB, 256 KB, 1 MB, 5 MB and 20 MB (benchmark/generate_samples.js). markdown-it is timed in-process on render() only: median of 10 runs after 3 warmups. Native and WASM are timed as the wall time of a whole child process (startup, file read, then 20 conversions with output discarded under --repeat 20) divided by 20. |
| **Metric** | throughput |
| **Hardware** | Apple M4, macOS |
| **Compiler and flags** | The numbers were last updated 2026-04-09 (commit 885e989, 'update benchmarks for -O3 optimization'). The Yo compiler version used then was not recorded; .yo-version did not exist, and the pin to Yo 0.2.58 was added on 2026-10-10. Native build: Yo Optimize.ReleaseFast to C, then clang -O3 -flto (clang version not stated; devenv.nix takes clang from nixpkgs). WASM CLI build (markdown_yo_wasm_exe): Yo Optimize.ReleaseSmall, then emcc -O3 -flto -mbulk-memory -sNODERAWFS -sEXIT_RUNTIME=1 -sALLOW_MEMORY_GROWTH -sINITIAL_MEMORY=67108864 -sWASM_BIGINT (Emscripten version not stated). Baseline: markdown-it ^14.1.1 called with {html: true} on Node (devenv.nix nodejs_22; exact version not stated). The harness is benchmark/run.js. |
| **Adoption** | 2 stars, 1 fork, 116 commits since 2026-04-01 |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/shd101wyy/markdown_yo) · [benchmark](https://github.com/shd101wyy/markdown_yo) |

## Verdict

On an Apple M4 with macOS, the native CLI (Yo ReleaseFast to C, clang -O3 -flto) was 4.5-7.6x faster than markdown-it 14 render() on Node 22 for one synthetic block repeated to 64 KB-20 MB, and the Emscripten WASM CLI was 2.1-6.0x faster only at 1 MB and above (0.1x at 64 KB, 0.5x at 256 KB). The Yo-side times are whole child processes divided by 20 (startup included, so conservative), the Yo, clang, Emscripten and Node versions were not recorded, and the table has not been re-run since the October 2026 fixes and Yo migrations.

## Use it when

- Batch or CLI conversion of large Markdown files (1 MB and up) where you want markdown-it-style HTML without running Node.
- Node or browser jobs that render multi-megabyte documents in one call: the WASM CLI measured 2.1x at 1 MB rising to 6.0x at 20 MB over markdown-it.
- Editor previews that already spawn an external renderer (the author wires it into Crossnote / Markdown Preview Enhanced as a binary path) and need the built-in extensions without loading markdown-it plugins.
- Projects already written in Yo that want a Markdown renderer as a package dependency.

## Skip it when

- Small documents through the WASM CLI: whole-process WASM time is about 12.9 ms at 64 KB versus 1.6 ms for markdown-it, and the in-process npm API that would avoid that startup has no published benchmark.
- Code that depends on markdown-it plugins, token streams, custom renderer rules or linkify: none of these exist, and no linkify switch is exposed in the CLI or npm flags.
- Inputs needing full CommonMark Unicode behaviour: reference labels are matched with ASCII case folding only, and IDN/Punycode autolinks are not decoded (both listed as skipped in issues/skipped-fixture-tests.md).
- Long-lived, security-sensitive hosts that cannot tolerate a young codebase: it is pre-1.0 (0.0.16), single-author, built on a compiler whose own README says 'WIP NOT READY', and a heap buffer overflow plus a per-render leak were only fixed on 2026-10-01.

## How it is fast

md4c-style SAX design: block rules call HtmlRenderer methods directly instead of building markdown-it's Token array, and inline rules push \~40-byte value-type tokens into a reused buffer before resolving emphasis delimiters. Text is handled as zero-copy slices of the source, block starts and inline specials go through 128/256-byte dispatch tables, HTML escaping scans 8 bytes at a time against a lookup table, and the output buffer is preallocated at about 1.5x the input. Yo transpiles to C, so the native build is clang -O3 -flto output and the WASM build is the same C through Emscripten.

## Compared with alternatives

Like svgo.mbt (a MoonBit rewrite of svgo), it is a new-language rewrite of a popular JS tool with a large native and a smaller WASM win; pick it for markdown-it-compatible HTML on large inputs, but for small documents rendered in-process the older md4c-based markdown-wasm and md4w (catalogued under wasm-libraries-and-apps) are the safer choice.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime for the npm WASM package or the native binary; building needs the Yo compiler, a C compiler (clang) and Emscripten for the WASM targets |
| **Minimum toolchain** | Yo 0.2.58 (pinned in .yo-version since 2026-10-10) plus clang; npm package needs a JS runtime with WebAssembly and TextEncoder/TextDecoder |
| **Platforms** | Native macOS, Linux and Windows (lld on Windows); WebAssembly in browsers and Node.js |
| **Thread safety** | not documented; the WASM API keeps the last result length in a global, Yo reference counting is non-atomic, and lookup tables are lazily initialised shared singletons, so treat it as single-threaded |
| **Drop-in for the baseline** | partial: HTML output is meant to match markdown-it (default preset with tables and strikethrough on, html off), but the API differs (async createRenderer, boolean option flags) and there is no plugin system |

## Gotchas

- The README table (2026-04-09) was measured on code whose hot escape path, escape_html_buf, wrote escape sequences through raw pointers into space reserved as input + 12.5% + 64 bytes; issues/escape-dense-text-overflows-the-output-buffer.md records this as a critical heap overflow on quote-heavy text, fixed 2026-10-01. The synthetic benchmark block is escape-light, the author reports benchmark/run.js unchanged after the fix, and escape-dense text got slower (10.9 to 12.8 ms).
- Throughput depends on the document: the benchmark repeats one \~1.2 KB block, while the author's own Crossnote measurements on x86_64 Linux (issue #5) give about 53 ms render-only for a 1 MB file, roughly 11x the README's 4.8 ms for 1 MB on an Apple M4.
- Every markdown_to_html call leaked a 256-byte table until 2026-10-01 (issues/inline-special-table-leaks-on-every-render.md), so long-running WASM hosts on the April 2026 npm releases (0.0.3-0.0.5) grow without bound; 0.0.9 was published the same day as the fix, so use 0.0.10 or later.
- The '98.7% CommonMark (815/826)' figure comes from a runner that compares the native binary with markdown-it and skips every fixture where markdown-it itself fails; WASM output is not checked by that runner, and the benchmark does not compare outputs at all.

## Known shortcomings

- Table dated 2026-04-09 with the Yo compiler version unrecorded (pin to Yo 0.2.58 added 2026-10-10); clang, Emscripten and Node versions unstated; WASM is slower than markdown-it below 1 MB and its rows include process startup amortised over 20 runs; no LICENSE file (reference).
- The table (2026-04-09) was measured on code with a heap buffer overflow in the hot escape_html_buf path (raw pointer writes, confirmed at 885e989), fixed 2026-10-01 together with a per-render 256-byte leak; the author says the benchmark is unchanged (later-fixed-bug rule, C stands). The author's own issue #5 (x86_64 Linux) gives about 53 ms render-only for a 1 MB document against the README's 4.8 ms, so speed depends on the input; the 815/826 conformance figure skips fixtures markdown-it fails and never checks WASM output; the in-process npm API is not benchmarked; no LICENSE file; the Yo compiler is self-described 'WIP NOT READY'.

## Caveats and trade-offs

The license is declared as MIT only in yo.toml and npm/package.json; the repository has no LICENSE file. The benchmark input is one synthetic block repeated many times, not real documents. The table dates from 2026-04-09 and the code has gone through many Yo language migrations since, so it has not been re-measured on the current code. The harness does not compare outputs between implementations; CommonMark conformance (815/826 spec tests) is checked separately. markdown-it runs with html: true while markdown_yo runs without --html; the samples contain no raw HTML, so this is probably immaterial. The WASM rows divide whole-process time, including Node startup and wasm compilation, by 20. At 64 KB that is about 0.26 s per process (12.9 ms x 20, derived from page data), and WASM is slower than markdown-it below about 1 MB (0.1x at 64 KB, 0.5x at 256 KB). Single-shot use is far slower than the table suggests. The in-process wasm_api build shipped in the npm package is not benchmarked. The project started 2026-04-01 and checks in AI-assistant planning files (AGENTS.md, PLAN.md); it has a single author and is pre-1.0 (0.0.16).

WASM module is 383 KB and has about 12 ms Node.js compile startup, so it loses to markdown-it below roughly 1 MB; 98.7% CommonMark spec pass (815/826), not full parity with markdown-it plugins; written in the young Yo language, so building needs the Yo toolchain.

## Maintenance

Active single-author project (116 commits since 2026-04-01, npm 0.0.16 published 2026-10-11, recent commits mostly mechanical Yo-language migrations); MIT is declared only in yo.toml and npm/package.json with no LICENSE file, and the toolchain it needs is self-described as not ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** These are first-party numbers from a public harness (benchmark/run.js and generate_samples.js) on a named CPU (Apple M4) with stated flags. The compiler that decides the generated code is not recorded, though: the table was last updated 2026-04-09 (commit 885e989), the Yo version was pinned only on 2026-10-10, and the clang, Emscripten and Node versions are not stated. The record's claim that the Yo version is pinned in .yo-version does not hold for these numbers, so this is partial methodology and the tier is C.
- **Verifier notes:** The numbers match the README table exactly; the native build is 4.5-7.6x faster than markdown-it and WASM is 2.1-6.0x faster only at 1 MB and above. Downgraded from A to C because the Yo compiler version, along with clang, Emscripten and Node, was not recorded when the April 2026 numbers were taken, and the code has changed substantially since. The harness is otherwise reasonable and, if anything, conservative toward markdown_yo, since process startup is included on its side only. The record's 'one month old' was wrong: the first commit is 2026-04-01.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-116 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/shd101wyy/markdown_yo>
  - <https://github.com/shd101wyy/markdown_yo/commits>
  - <https://github.com/shd101wyy/markdown_yo/commits/master/README.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/README.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/benchmark/run.js>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/benchmark/generate_samples.js>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/build.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/yo.toml>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/.yo-version>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/package.json>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/npm/package.json>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/src/main.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/devenv.nix>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/devenv.yaml>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/885e989/README.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/885e989/build.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/885e989/benchmark/run.js>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/885e989/devenv.nix>
- **Sources the enricher read:**
  - <https://github.com/shd101wyy/markdown_yo>
  - <https://github.com/shd101wyy/markdown_yo/commits/master>
  - <https://github.com/shd101wyy/markdown_yo/issues?q=is%3Aissue>
  - <https://github.com/shd101wyy/markdown_yo/issues/5>
  - <https://github.com/shd101wyy/markdown_yo/tree/master/issues>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/README.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/benchmark/run.js>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/benchmark/generate_samples.js>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/build.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/yo.toml>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/.yo-version>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/package.json>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/npm/package.json>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/npm/index.js>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/npm/index.d.ts>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/docs/WASM.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/src/main.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/src/types.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/src/wasm_api.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/src/lib.yo>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/scripts/run_fixture_tests.js>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/devenv.nix>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/PLAN.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/profile_output.txt>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/issues/escape-dense-text-overflows-the-output-buffer.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/issues/inline-special-table-leaks-on-every-render.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/issues/skipped-fixture-tests.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/HEAD/issues/wasm-empty-output-missing-trailing-newline.md>
  - <https://raw.githubusercontent.com/shd101wyy/markdown_yo/885e989/src/common/utils.yo>
  - <https://registry.npmjs.org/markdown_yo>
  - <https://github.com/shd101wyy/Yo>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/shd101wyy/markdown_yo`) · [data/wave13/enrich/raw/github_com_shd101wyy_markdown_yo.json](../../../data/wave13/enrich/raw/github_com_shd101wyy_markdown_yo.json) (enrichment confidence 0.75)

</details>
