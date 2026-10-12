# ElementaryUI (SwiftWasm)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Swift` · `Apache-2.0` · 🟢 active

> SwiftUI-style browser UI framework in Swift compiled to WebAssembly; 1.14x faster than React 19 hooks overall, all from swap rows.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | Project makes no speed claim; README claims only size ('Full Embedded Swift support means kB-sized wasm bundles instead of MB'). Suite data, my unweighted geometric means over the 9 CPU benchmarks of median total duration from the raw run arrays in results.ts (derived from page data): 0.877x the time of react-hooks-v19.2.0-keyed (about 1.14x faster), but 1.081x React's time (slower) when swap rows is excluded; 0.898x preact-hooks; 1.258x vue-v3.5.39-keyed; 1.597x vanillajs-keyed; 1.446x solid-v1.9.3-keyed; 1.348x svelte-v5.42.1-keyed. Per benchmark versus React: swap 14.7 vs 89.7 ms, create 10,000 rows 349.6 vs 401.0 ms and clear faster (0.91x); create 1,000 rows 31.9 vs 23.6 ms (1.35x), replace all 1.22x, append 1.30x, partial update 1.03x and select 1.06x slower; remove level. Rank 136 of 196 keyed implementations by slowdown versus the per-benchmark best (1.671 keyed-only, 1.937 across all). |
| **Workload** | krausest/js-framework-benchmark: nine browser benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), driven by the Puppeteer benchmark driver with reduced tracing (15 runs per benchmark, 25 for select), median of the total (script plus paint) duration per benchmark. |
| **Metric** | latency |
| **Hardware** | Apple M4 (MacBook Pro 14, '14/20 cores', 48 GB RAM), macOS 26.6.2, Chrome 154.0.8037.98 (arm64), per the 'Test environment & methodology' block in webdriver-ts-results/src/App.tsx, which ships with the Chrome 154 results (results.ts commit c097071 'Chrome 154 results', 2026-10-04). The same page sets isOfficial = false and labels itself a development snapshot that 'may mix browser versions or run counts'. |
| **Compiler and flags** | Embedded Swift: vite.config.js calls swiftWasm({ useEmbeddedSDK: true, linkEmbeddedUnicodeDataTables: false }) from @elementary-swift/vite-plugin-swift-wasm 0.2.0 with vite 8.3.1; Package.swift pins elementary-ui exact 0.8.0 and JavaScriptKit from 0.58.0 (swift-tools-version 6.3, Swift 5 language mode). The swiftc toolchain version and optimisation flags are not stated; bundled-dist is checked in prebuilt. |
| **Adoption** | 511 stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/elementary-swift/elementary-ui) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark's Chrome 154 development snapshot (Apple M4, macOS 26.6.2), elementaryui-v0.8.0-keyed (Embedded Swift build) against react-hooks-v19.2.0-keyed median totals were: swap 14.7 vs 89.7 ms, create 10k 349.6 vs 401.0, clear 16.1 vs 17.6, remove 11.3 vs 11.3, select 5.7 vs 5.4, partial update 15.2 vs 14.7, replace 36.9 vs 30.2, append 38.1 vs 29.3, create 1k 31.9 vs 23.6 ms. I recomputed the unweighted geometric mean from results.ts: 0.877x React's time (1.081x without swap) and 1.597x vanilla JS's time (derived from page data). The project itself makes no speed claim.

## Use it when

- A team that already writes Swift (server-side Elementary/Hummingbird/Vapor or Apple apps) and wants browser UI in the same language with SwiftUI-like syntax.
- Keyed lists that are frequently reordered or have rows moved: the LIS-based diff beats React 19 hooks by about 6x on the suite's swap-rows test (14.7 vs 89.7 ms).
- Large one-shot table builds and clears where it measured slightly ahead of React hooks (create 10,000 rows 349.6 vs 401.0 ms; clear 16.1 vs 17.6 ms).
- Shipping Swift-written widgets into an existing site as custom elements via ElementaryWebComponents.

## Skip it when

- When raw DOM speed is the goal: in the same run it takes 1.6x vanilla JS's time and 1.26-1.45x Vue 3.5, Svelte 5 and Solid 1.9, and is slower than the Rust Wasm frameworks Leptos, Dioxus and Sycamore (1.23-1.28x their time) (unweighted geometric means derived from page data).
- Typical CRUD rendering against React: excluding swap rows it takes 1.081x React hooks' time and is slower on 5 of 9 tests (create 1,000 rows 31.9 vs 23.6 ms, append 38.1 vs 29.3 ms, replace all 36.9 vs 30.2 ms).
- Load-time-sensitive pages: first paint 815.9 vs 226.6 ms for React, compressed size 143.7 vs 51.4 kB and uncompressed 720.4 vs 190.3 kB (a 666 KB .wasm plus a 55 KB JS loader in the benchmark bundle).
- Sites with a strict Content-Security-Policy: the suite flags the implementation with note 1139 (does not pass its strict same-origin CSP).
- Projects that need API stability: the README calls it 'an actively developed passion project in its early days', and 0.7.0 and 0.8.0 both shipped breaking changes (runtime removal and a Swift 6.4 minimum).

## How it is fast

Views are ahead-of-time compiled Swift (optionally Embedded Swift for a smaller module), and state changes are tracked by a Reactivity module modelled on Swift's Observation framework, so updates are queued and run in one microtask-scheduled cycle that separates reconciliation from a batched DOM commit phase. Keyed lists are diffed by KeyedDiffEngine: it trims the unchanged prefix and suffix, takes fast paths for pure insertions and deletions, and uses a longest-increasing-subsequence (LIS) pass to move only the out-of-order nodes, which is why swapping two rows costs 14.7 ms against React hooks' 89.7 ms. DOM calls still cross the Wasm-to-JavaScript boundary through JavaScriptKit, so creation-heavy work is slower than in the JS frameworks.

## Compared with alternatives

Pick it over Leptos, Dioxus, Sycamore or Yew only when the codebase is Swift rather than Rust; in the same Chrome 154 run those Rust Wasm frameworks are 7-28% faster by geometric mean and ship smaller first paint, so on speed alone they win.

## Integration

| | |
|---|---|
| **Form** | Swift package (SwiftPM library products ElementaryUI and ElementaryWebComponents) compiled to a .wasm module and bundled by Vite |
| **Dependencies** | JavaScriptKit (0.59.x), elementary 0.8.2+, swift-collections 1.7.1+ with the UnstableContainersPreview and UnstableHashedContainers traits, swift-syntax 600-604 for the macros; at build time Node, Vite and @elementary-swift/vite-plugin-swift-wasm |
| **Minimum toolchain** | Swift 6.4 or later with the matching swift.org Swift SDK for WebAssembly (required since 0.8.0); package manifest uses swift-tools-version 6.4 and experimental features (Lifetimes, RawLayout, BuiltinModule, Extern) |
| **Platforms** | Browsers with WebAssembly (wasm32), built either with the Embedded Swift SDK (small module) or the full Swift SDK; benchmarked in Chrome 154 on Apple M4 |
| **Thread safety** | Single-threaded browser main-thread model; the README lists 'isolation and @MainActor stuff for reusable types' as unresolved |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline win over React hooks rests on one test: the 0.877x unweighted geometric mean becomes 1.081x (slower) once swap rows, React hooks' known weak spot, is removed; ElementaryUI is also slower than every Rust Wasm sibling in the same run except near-parity with Yew (1.071x).
- The benchmark implementation in krausest/js-framework-benchmark was written and version-bumped by the ElementaryUI author (sliemeobn commits 6b79cfb, 0e53da5, 5cdcee2), and the suite runs a prebuilt bundled-dist (build-prod is a no-op) whose Swift 6.4+ toolchain version and optimisation flags are not recorded; the results page is a development snapshot (isOfficial = false). The implementation itself follows the suite's rules (swapAt(1, 998), ' !!!' on every 10th row, 'danger' class on select).
- Embedded Swift limits: KeyedDiffEngine.swift notes that 'Hashing a stored view key traps on the embedded Wasm target', the README says Codable/JSON is not available in Embedded Swift yet, and the benchmark build sets linkEmbeddedUnicodeDataTables: false while its Row == compares label.utf8 bytes instead of String equality, so Unicode-aware string handling in an app may need the tables linked and a larger bundle (inference from the config; size impact not measured).
- Strict-CSP failure (suite note 1139): the bundled JS loader contains no eval or new Function but instantiates WebAssembly via instantiateStreaming, so the cause is probably that compiling Wasm needs 'wasm-unsafe-eval' (inference; the issue page does not say).

## Known shortcomings

- The win over React (0.877x) comes from swap rows only; excluding swap it is 1.081x slower, slower on 5 of 9 rows and 1.6x slower than vanilla JavaScript; built with the Embedded Swift SDK; development snapshot, toolchain unstated. UI framework, filed under wasm-libraries-and-apps.
- Enricher: the results.ts medians match the record, but the win over React hooks comes from the swap rows alone (1.081x React's time without them); slower than Leptos, Dioxus and Sycamore (1.23-1.28x) and about level with Yew (1.071x); the benchmark implementation was written and version-bumped by the ElementaryUI author; the prebuilt 666 KB wasm bundle needs a Swift 6.4+ toolchain with the exact version and flags unrecorded; the strict-CSP flag (1139) probably stems from Wasm compilation rather than eval.

## Caveats and trade-offs

Independent suite with the CPU (Apple M4) and Chrome 154.0.8037.98 stated, but the swiftc toolchain and flags behind the checked-in prebuilt bundle are not, and the results page is marked a development snapshot (isOfficial = false). The 1.14x geometric-mean win over React hooks comes entirely from swap rows (React hooks' known weak spot, 89.7 vs 14.7 ms): without it ElementaryUI is 1.081x React's time, and it is slower than React on 5 of 9 benchmarks (create 1,000 rows 1.35x, append 1.30x, replace all 1.22x). It is 1.6x slower than vanilla JS (the category's JS-in-V8 baseline) and slower than Vue, Solid and Svelte. Flagged by suite note 1139 ('Implementation doesn't pass strict CSP'). Bundle size and first paint are larger than React's (compressed 143.7 kB vs 51.4 kB; first paint 815.9 vs 226.6 ms). Ratios are my own unweighted geometric means from the raw results.ts, not the site's weighted score.

Swift compiled to Wasm; suite rows for this build: compressed size 143.7 vs React 51.4 (suite units, presumably kB), first paint 815.9 vs 226.6 ms, run memory 4.77 vs 4.37 MB. README advertises kB-sized Embedded Swift bundles but the suite shows a much larger compressed size and 3.6x slower first paint than React.

## Maintenance

Actively developed (0.8.0 released 29 Sep 2026, last commit 2026-10-09, 511 stars) and Apache-2.0, but pre-1.0 with breaking changes in recent minors and a Swift 6.4 minimum; usable for Swift-first teams, not a performance upgrade over the fast JS or Rust frameworks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (implementation in frameworks/keyed/elementaryui) with a keyed React hooks row, and my medians from results.ts reproduce the record exactly. The CPU (Apple M4) and Chrome build are stated in webdriver-ts-results/src/App.tsx, but no swiftc version or optimisation flags are, the bundle is prebuilt and the page is a development snapshot, so B, not A.
- **Verifier notes:** Numbers verified exactly from the raw arrays. The 'faster than React' result rests on one benchmark (swap rows); excluding it the entry is 1.08x slower than React, and it is 1.6x slower than vanilla JS. Record the shortcoming 'faster than React hooks only on swap, create 10k and clear; slower on 5 of 9; not faster than the JS baseline'. The benchmark build uses the Embedded Swift SDK (useEmbeddedSDK: true), which the record left unstated. Metadata matches: 511 stars, Apache-2.0, last commit 2026-10-09.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-100 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://github.com/krausest/js-framework-benchmark/issues/1139>
  - <https://github.com/elementary-swift/elementary-ui>
  - <https://github.com/elementary-swift/elementary-ui/commits>
  - <https://github.com/elementary-swift/elementary-ui/tree/main/Benchmarks>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/elementaryui>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/Package.swift>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/vite.config.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/Sources/App/main.swift>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/elementary-swift/elementary-ui/HEAD/README.md>
  - <https://raw.githubusercontent.com/elementary-swift/elementary-ui/HEAD/Package.swift>
  - <https://github.com/elementary-swift/elementary-ui/releases>
  - <https://github.com/elementary-swift/elementary-ui/tree/main/Benchmarks>
  - <https://github.com/elementary-swift/elementary-ui/tree/main/Benchmarks/PerformanceBenchmarks>
  - <https://github.com/elementary-swift/elementary-ui/tree/main/Sources/ElementaryUI>
  - <https://github.com/elementary-swift/elementary-ui/tree/main/Sources/ElementaryUI/Reconciling>
  - <https://raw.githubusercontent.com/elementary-swift/elementary-ui/HEAD/Sources/ElementaryUI/Reconciling/KeyedDiffEngine.swift>
  - <https://raw.githubusercontent.com/elementary-swift/elementary-ui/HEAD/Sources/ElementaryUI/Reconciling/Scheduler.swift>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/Package.swift>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/vite.config.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/Sources/App/main.swift>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/bundled-dist/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/elementaryui/bundled-dist/assets/index-Dup2zEm0.js>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/elementaryui/bundled-dist>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/elementaryui>
  - <https://github.com/krausest/js-framework-benchmark/commit/5cdcee2>
  - <https://github.com/krausest/js-framework-benchmark/issues/1139>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/elementary-swift/elementary-ui`) · [data/wave13/enrich/raw/github_com_elementary_swift_elementary_ui.json](../../../data/wave13/enrich/raw/github_com_elementary_swift_elementary_ui.json) (enrichment confidence 0.75)

</details>
