# Yew

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> React-style Rust/Wasm component framework whose keyed reconciler beats React 19 on row swaps; overall it ties React and trails vanilla JS.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README: 'Achieves high performance by minimizing DOM API calls for each page render' (no number). Suite data for the yew-v0.23.0-keyed entry (struct components, impl Component): unweighted geometric mean over the 9 CPU benchmarks of the median total duration is 0.819x the time of react-hooks-v19.2.0-keyed (about 1.22x faster, derived from page data); swap 1,000 rows 13.8 ms vs React 89.7 ms; create 1,000 rows 31.7 ms vs React 23.6 ms; create 10,000 rows 325.6 ms vs React 401.0 ms; versus react-classes-v19.0.0-keyed 0.822x; versus vanillajs-keyed 1.492x (slower). Excluding swap rows the geometric mean is 1.009x React hooks' time (no win), and Yew's own hooks implementation (yew-hooks-v0.23.0-keyed) is 1.030x React hooks' time, i.e. not faster (all derived from page data). |
| **Workload** | krausest/js-framework-benchmark (Chrome 154 snapshot): nine WebDriver-driven Chrome benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear; partial update, select, swap and clear run with 4x CPU throttling, remove with 2x), median of 15 runs (25 for select) of the total (script plus paint) duration. Yew entry is yew-v0.23.0-keyed (frameworks/keyed/yew, struct components); a separate yew-hooks-v0.23.0-keyed entry uses function components with hooks. |
| **Metric** | latency |
| **Hardware** | Not stated for the Chrome 154 snapshot (results commit 2026-10-04); webdriver-ts-results/releases.json labels Chrome 139-146 'macOS' but gives no note for Chrome 148-154 and no CPU model anywhere. |
| **Compiler and flags** | Rust release profile: lto=true, codegen-units=1, panic=abort; wasm-pack release, wasm-opt -O4 (frameworks/keyed/yew/Cargo.toml). |
| **Adoption** | 32.8k stars |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/yewstack/yew) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark (Chrome 154 snapshot, results committed 2026-10-04, CPU not stated), the medians of 15 runs (25 for select) of the total script plus paint time put the yew-v0.23.0-keyed struct-component build, compiled with LTO and wasm-opt -O4, at 0.819x react-hooks-v19.2.0-keyed's time as an unweighted geometric mean over the nine CPU tests. Swap is 13.8 ms against 89.7 ms. Without swap the ratio is 1.009x, the hooks entry is 1.030x, and vanilla JS is 1.492x faster than Yew. I re-derived all of these from results.ts.

## Use it when

- Rust teams writing a browser SPA who want a React-like component model (html! macro, struct or hook components) and want to share types and logic with a Rust backend.
- UIs whose hot path reorders keyed lists (drag-and-drop, sorting, swapping rows): the run-based keyed diff moves few DOM nodes, 13.8 ms against React 19.2 hooks' 89.7 ms on the suite's swap test.
- Apps that need server-side rendering plus hydration from the same Rust components (ssr and hydration crate features).
- Struct-component apps with stable callbacks, where the PartialEq props skip keeps select and partial update close to React (4.6 ms against 5.4 ms on select row; 13.2 against 14.7 ms on partial update).

## Skip it when

- When rendering speed is the goal. Unweighted geometric mean of the nine CPU tests, as a multiple of vanilla JS time: Yew 1.49x, against wasm-bindgen 1.06x, Silkenweb 1.13x, dominator 1.24x, Leptos 1.25x, Dioxus 1.27x and Sycamore 1.30x (derived from page data).
- Creation-heavy screens: Yew takes 1.34x React's time to create 1,000 rows (31.7 against 23.6 ms), 1.18x to replace all rows and 1.22x to append 1,000 rows.
- When bundle size or first paint matters: 56.8 compressed against React's 51.4 and vanilla's 2.5 (suite units), and first paint 262 ms against React's 227 ms.
- Strict Content-Security-Policy deployments: the suite flags Yew's bundle under issue #1139, which marks packages whose dist contains Function, eval or with.
- Hook-based code that builds fresh callbacks for every list item on each render, or that clones whole state in reducers: the suite's yew-hooks entry does both and is 1.26x slower than the struct entry (select row 11.9 against 4.6 ms).

## How it is fast

Re-rendering is skipped for a child whose Properties compare equal (PartialEq), so a select or update touches only the rows whose props changed. Keyed children are reconciled in BList::apply_keyed. It first diffs the matching runs at the end and the start, then splices out the mismatched middle and indexes it in a HashSet by key. It then puts that middle back by tracking runs of in-order nodes, deciding per run whether to shift it or commit to it so that as few DOM nodes as possible move. That is why swapping rows 2 and 999 takes 13.8 ms against React's 89.7 ms in the suite (paint 10 ms against 68 ms). The suite build uses LTO, codegen-units=1, panic=abort and wasm-opt -O4.

## Compared with alternatives

Pick Yew over Leptos, Sycamore, Silkenweb or rust-dominator when you want the React-like virtual-DOM and hooks model, the largest Rust web ecosystem (32.8k stars, 5.0M crate downloads) or a mature SSR and hydration path. Pick one of those fine-grained-signal frameworks, or hand-written wasm-bindgen, when update speed matters: in this suite they are 1.06-1.30x vanilla JS against Yew's 1.49x.

## Integration

| | |
|---|---|
| **Form** | crate (compiled to wasm32-unknown-unknown with wasm-bindgen; built with wasm-pack or trunk) |
| **Dependencies** | wasm-bindgen, web-sys, js-sys, gloo, yew-macro, indexmap, slab, implicit-clone, futures, serde, thiserror, tracing; wasm-bindgen-futures on wasm32; tokio on native targets (SSR) |
| **Minimum toolchain** | Rust 1.84.0 (rust-version of yew 0.23.0 on crates.io), edition 2021, wasm32-unknown-unknown target |
| **Platforms** | Browsers with WebAssembly for client-side rendering (csr feature); native and WASI targets for server-side rendering (ssr feature) |
| **Thread safety** | Not documented in the sources read. Rendering runs on the browser main thread, and the README suggests offloading heavy processing to background web workers. |
| **Drop-in for the baseline** | no |

## Gotchas

- The suite's yew-hooks entry carries a harness asymmetry. Every render it builds new on_select.reform and on_remove.reform callbacks for every row, which defeats Yew's props-equality skip so all 1,000 rows re-render on select, and its reducer deep-clones the whole Vec&lt;RowData&gt;, plus a second rows.clone() in the render. React's entry uses memo with a custom comparator and shallow array copies. The 'Yew hooks 1.030x React' result therefore measures that implementation more than hooks in Yew.
- The whole geometric-mean win over React comes from the swap test. Without it the struct entry is 1.009x React hooks' time, so outside list reordering expect parity at best.
- Duplicate keys in a keyed list are caught only with debug_assertions. In release builds blist.rs 'hope[s] for the best by pretending' and can lose track of mounted nodes, so test keyed lists in debug builds.
- The suite serves prebuilt Wasm (build-prod is a no-op), but the bundles were rebuilt in the same commit that moved to 0.23.0 (d54bfce, 2026-03-30), so they match the source. Master's later rendering work (perf #4088 DomSlot traversal, fix #4099 sibling re-renders) is unreleased and unmeasured. The memory rows are single samples: run memory reads 5.82 MB for the struct entry and 2.2 MB for the nearly identical hooks entry.

## Known shortcomings

- The entire win over React hooks (0.819x of its time) comes from swap rows; without swap Yew takes 1.009x React's time and Yew's own hooks variant 1.030x, so it is not faster; slower than vanilla JavaScript and nine keyed Rust frameworks; no CPU model (krausest Chrome 154 results, 2026-10-04); a UI framework, filed under wasm-libraries-and-apps.
- The suite's like-for-like yew-hooks entry builds fresh per-row callbacks every render (defeating the props-equality skip) and deep-clones the whole row Vec in its reducer, while React's entry uses memo with a custom comparator, so 'Yew hooks 1.030x React' measures an untuned implementation. Re-derived numbers match (0.819x React hooks' time overall, 1.009x without swap rows, 1.492x vanilla). Memory rows are single samples; duplicate keys are checked only under debug_assertions. Prebuilt bundles were rebuilt with the 0.23.0 bump (d54bfce), so the staleness worry is moot.

## Caveats and trade-offs

Independent public suite but the CPU model for this snapshot is not stated, so tier B not A. The whole geometric-mean win over React comes from swap rows (React hooks 89.7 ms vs 13.8 ms, a known React reconciliation weakness): excluding swap, Yew's struct-component entry is 1.009x React hooks' time. Yew is slower than React on create 1,000 rows (1.34x of React's time), replace all rows (1.18x) and append rows (1.22x). The like-for-like hooks implementation (yew-hooks-v0.23.0-keyed, function components) is 1.030x React hooks' time, so idiomatic modern Yew is not faster; the struct-component entry is 0.822x React classes. Not faster than vanilla JS (1.492x its time) or the best JS frameworks: geometric-mean slowdown versus the per-benchmark best over all keyed and non-keyed entries is 1.21 vanillajs-keyed, 1.34 Solid, 1.44 Svelte, 1.81 Yew (1.56 for Yew against keyed-only best); all derived from page data, unweighted, not the site's weighted geometric mean. Among keyed Rust/Wasm entries Yew ranks behind wasm-bindgen, spair, silkenweb, stdweb, dominator, leptos, dioxus, mogwai and sycamore; only yew-hooks and sauron are slower. Wasm implementations are checked in as prebuilt bundles ('build-prod is a no-op, the generated javascript is already provided'), so the shipped binary may not match current source. The implementation carries benchmark note #1139 (does not pass strict CSP), which does not affect timings. Category fit is weak: Yew is a Rust/Wasm UI framework, not a wasm-targeting language. [retier] Independent public suite but the CPU model for this snapshot is not stated, so tier B not A. The whole geometric-mean win over React comes from swap rows (React hooks 89.7 ms vs 13.8 ms, a known React reconciliation weakness): excluding swap, Yew's struct-component entry is 1.009x React hooks' time, and Yew is slower on create 1,000 rows (1.34x), replace all rows (1.18x) and append rows (1.22x). The like-for-like yew-hooks entry (1.030x React hooks' time) is untuned: it builds new on_select.reform and on_remove.reform callbacks for every row each render, defeating Yew's props-equality skip, and its reducer deep-clones the whole Vec&lt;RowData&gt;, while React's entry uses memo with a custom comparator. Yew is 1.492x vanilla JS's time. Prebuilt bundles were rebuilt with the 0.23.0 bump (d54bfce). Memory rows are single samples; duplicate keys are checked only under debug_assertions.

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 56.8 vs React 51.4 (suite units, presumably kB), first paint 262.1 vs 226.6 ms, run memory 5.82 vs 4.37 MB, ready memory 1.76 vs 1.19 MB. yew 0.23.0 csr, rand 0.9 and getrandom 0.3 (wasm_js backend).

## Maintenance

Actively maintained: last commit 2026-08-26, 0.23.0 released 2026-03-10 (0.22.1 yanked), MIT OR Apache-2.0, 32.8k stars. Copyable, but the speed case is narrow: it is evidence for keyed reorders, not a general win over React, and the evidence is tier B because the suite gives no CPU model.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent third-party suite (krausest/js-framework-benchmark, Chrome 154 results committed 2026-10-04) whose raw run arrays in webdriver-ts-results/src/results.ts contain both yew-v0.23.0-keyed and react-hooks-v19.2.0-keyed; benchmark code (webdriver-ts) and Yew's release profile (frameworks/keyed/yew/Cargo.toml) are public, but no CPU model or machine is stated for this snapshot (releases.json gives no note for Chrome 148-154), so B not A.
- **Verifier notes:** All quoted numbers match the yew-v0.23.0-keyed row of results.ts (medians re-derived: 0.819x vs React hooks, 1.492x vs vanilla). Main shortcomings: win rests entirely on swap rows (1.009x React's time without it), Yew's hooks variant is 1.030x React hooks (not faster), slower than vanilla JS and most Rust frameworks; the record's 'slowest Rust framework' caveat was wrong (sauron and yew-hooks are slower) and is corrected. Metadata checked on github.com: Apache-2.0 and MIT, 32.8k stars, last commit 2026-08-26, not archived; category would fit wasm-libraries-and-apps better than assemblyscript-and-wasm-langs.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-103 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew-hooks/Cargo.toml>
  - <https://github.com/krausest/js-framework-benchmark/blob/master/frameworks/keyed/yew/src/lib.rs>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/webdriver-ts-results>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://github.com/krausest/js-framework-benchmark/issues/1139>
  - <https://github.com/yewstack/yew>
  - <https://github.com/yewstack/yew/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yewstack/yew/HEAD/README.md>
  - <https://raw.githubusercontent.com/yewstack/yew/yew-v0.23.0/packages/yew/Cargo.toml>
  - <https://raw.githubusercontent.com/yewstack/yew/yew-v0.23.0/packages/yew/src/dom_bundle/blist.rs>
  - <https://github.com/yewstack/yew/commits/master>
  - <https://github.com/yewstack/yew/issues?q=is%3Aissue%20performance>
  - <https://crates.io/api/v1/crates/yew>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew-hooks/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew-hooks/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/yew-hooks/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/react-hooks/src/main.jsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/react-hooks/package.json>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/yew>
  - <https://github.com/krausest/js-framework-benchmark/commit/d54bfce>
  - <https://github.com/aclueless/spair>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/yewstack/yew`) · [data/wave13/enrich/raw/github_com_yewstack_yew.json](../../../data/wave13/enrich/raw/github_com_yewstack_yew.json) (enrichment confidence 0.75)

</details>
