# Sycamore

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust/Wasm fine-grained-reactive UI library; its 2023 beta ran the keyed DOM benchmark about 1.4x faster than React 19.2 hooks.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README says 'Lightning Speed' with no number. Suite data (derived from page data): geometric mean over the 9 CPU benchmarks of the median total duration (medians computed by me from the raw run arrays in results.ts) is 0.711x the time of React 19.2 hooks (about 1.41x faster, derived from page data); swap 1,000 rows 13.1 ms vs React 89.7 ms; create 1,000 rows 24.8 ms vs React 23.6 ms; create 10,000 rows 263.7 ms vs React 401.0 ms; versus vanillajs-keyed the geometric mean is 1.296x (derived from page data). |
| **Workload** | krausest/js-framework-benchmark (Chrome 154 development snapshot, Puppeteer benchmark driver with reduced tracing): nine browser benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), 15 measured runs each (25 for select row) after 3-5 warmup runs; metric is the median of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14, Apple M4 (14/20 cores, 48 GB), OSX 26.6.2, Chrome 154.0.8037.98 arm64 (suite App.tsx for the Chrome 154 snapshot, which it labels a 'Development snapshot' that 'may mix browser versions or run counts') |
| **Compiler and flags** | Rust release profile: lto=true, codegen-units=1, panic=abort; wasm-pack build --release --target web with wasm-opt -O4 (frameworks/keyed/sycamore/Cargo.toml and package.json build-prod-force). No Cargo.lock in the directory and the bundle was prebuilt (last rebuilt 2023-10-07, 'Update Sycamore to 0.9.0-beta.2'), so the wasm-bindgen and rustc versions behind the measured binary are not stated. |
| **Adoption** | 3.4k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/sycamore-rs/sycamore) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

Independent krausest/js-framework-benchmark snapshot (Chrome 154, MacBook Pro 14 M4 14/20 cores, OSX 26.6.2, 15 runs per test): the prebuilt sycamore 0.9.0-beta.2 keyed bundle (lto, codegen-units 1, wasm-opt -O4; rustc version not stated) takes 0.711x React 19.2 hooks' median total time over 9 CPU tests (about 1.41x faster) but 1.296x vanilla JS's time; the gain is mostly swap rows (13.1 vs 89.7 ms) and 10k creation (263.7 vs 401.0 ms) (derived from page data, recomputed this session from results.ts).

## Use it when

- A team that wants to write the whole front end in Rust and share types and logic with a Rust backend
- List-heavy UIs with reordering (swap, move) where React's keyed reconciliation is slow: swap 1,000 rows 13.1 ms vs 89.7 ms in the suite
- Large table creation: create 10,000 rows 263.7 ms vs React 401.0 ms, and lower run memory (2.10 vs 4.37 MB) in the suite
- Apps that need SSR with streaming and hydration from the same component code
- Developers who like SolidJS's model and want it in Rust with Copy, 'static signals and no lifetime parameters

## Skip it when

- If raw DOM speed is the goal: the suite has it at 1.296x vanilla JS's time and behind Solid 1.9.3, Silkenweb, Leptos 0.7.0, rust-dominator and Dioxus 0.7.2 (derived from page data)
- Small create-heavy pages: create 1,000 rows is 24.8 ms vs React's 23.6 ms, and ready memory is higher (1.68 vs 1.19 MB)
- Sites with a strict Content-Security-Policy: the suite flags the implementation with issue #1139 (does not pass strict CSP), as for most Wasm-instantiating builds
- When the published numbers must describe the version you ship: they come from a 2023 beta whose rendering path no longer exists
- Teams needing a large ecosystem or many maintainers: development is mostly one maintainer, and the README itself points to Leptos's larger community

## How it is fast

Fine-grained reactivity: each signal knows its dependents, so an update re-runs only the effect bound to one text node or attribute, with no virtual-DOM diff (the reactive graph lives in a slotmap under one Root, 'Reactivity v3'). Keyed lists are reconciled with a udomdiff-style prefix/suffix/swap-backwards/map algorithm (reconcile_fragments), which is why swapping two rows costs 13.1 ms against React's 89.7 ms. The measured 0.9.0-beta.2 build also cloned cached &lt;template&gt; elements to create rows; the current 0.9.x code creates each element with document.createElement, using wasm-bindgen string interning (default feature) to cut JS string crossings.

## Compared with alternatives

In the same Chrome 154 snapshot the keyed Rust entries rank, as geometric-mean fraction of React 19.2's time: hand-written wasm-bindgen 0.584, Silkenweb 0.622, rust-dominator 0.681, Leptos 0.684, Dioxus 0.698, Sycamore 0.711, Yew 0.819, ElementaryUI 0.877 (derived from page data), so pick Sycamore for its Solid-like API, SSR streaming and small bundle rather than for speed; pick Leptos or Silkenweb if suite speed decides it.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasm-bindgen, web-sys, js-sys, slotmap, smallvec, once_cell, paste and the sycamore-\* sub-crates; optional futures/serde for suspense and serde features |
| **Minimum toolchain** | Rust 1.94 (MSRV raised in 0.9.3), edition 2024; wasm32-unknown-unknown target plus Trunk or wasm-pack for browser builds |
| **Platforms** | Browsers via wasm32-unknown-unknown (DOM backend); any native target for SSR (selected by target arch, or --cfg sycamore_force_ssr for server-side Wasm) |
| **Thread safety** | Single-threaded: the reactive Root is a thread-local global and signals are not Send; SSR's render_to_string keeps one root per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Measured code path is gone: the suite's sycamore-v0.9.0-beta.2 bundle (prebuilt 2023-10) creates rows by cloning cached &lt;template&gt; content (the beta.2 view! macro emits a static Template per element root, instantiated from TEMPLATE_CACHE in dom_node_template.rs), while View v2 in 0.9.0 removed GenericNode/Html and the 0.9.4 sources build each element with document.createElement; nobody has published js-framework-benchmark numbers for 0.9.x, although the in-repo examples/js-framework-benchmark is already ported to the 0.9 API.
- Bugs fixed after the measured beta: Keyed/Indexed wrong node order (#795, map index i instead of b_start+i, fixed in PR #796, 2025-04), dead dependents piling up after disposing memos (PR #831, 0.9.3) and event callbacks firing after drop ('closure invoked recursively or destroyed', #433, fixed by PR #837 in 0.9.4). Tracing the beta.2 reconcile_fragments shows the suite's swap, remove, append and replace-all operations take the prefix/suffix/swap paths or reach the map path with b_start 0, so the measured rows did not hit the #795 bug.
- No event delegation (issue #176 open since 2021): every on:click is its own wasm-bindgen Closure plus addEventListener (dom_node.rs), so each benchmark row allocates two closures; the suite does not isolate this cost, but it is extra per-row work that delegating JS frameworks avoid.
- create_root leaks its Root struct by design (Box::leak, documented 'lives until the end of the program'); code that creates a fresh root per request or per test grows memory, while render_to_string reuses a thread-local root.

## Known shortcomings

- Measured at the 2023 beta 0.9.0-beta.2 (current 0.9.4); takes 1.296x vanilla JavaScript's time, slower than Solid and Svelte, and create-1k is 1.05x React (slower); preliminary snapshot, prebuilt bundle, rustc unstated. UI framework, filed under wasm-libraries-and-apps.
- The measured 0.9.0-beta.2 bundle cloned cached &lt;template&gt; rows (TEMPLATE_CACHE, the view! macro emitted a Template); 0.9.0's View v2 removed that path and 0.9.4 creates each element with createElement, so the suite numbers describe a dead renderer. Post-beta fixes: #795/#796 keyed order bug, #831 dependents leak, #433/#837 callback after drop; tracing the beta.2 reconcile_fragments shows the suite's operations avoid the #795 bug, so the numbers stand. Keyed Rust rank vs React: Sycamore 0.711, behind wasm-bindgen 0.584, Silkenweb 0.622, dominator 0.681, Leptos 0.684 and Dioxus 0.698, ahead of Yew 0.819 and ElementaryUI 0.877.

## Caveats and trade-offs

Independent public suite (krausest/js-framework-benchmark) and the snapshot states CPU, OS and browser, but results.ts at HEAD is a development snapshot (App.tsx: 'These results are preliminary and may mix browser versions or run counts'), and the measured Wasm is a prebuilt bundle checked into the suite ('build-prod' is a no-op; 'the generated javascript ... is already provided') whose rustc version is not stated, so tier B not A. Measured version is the 0.9.0-beta.2 pre-release bundled in October 2023; the current release is 0.9.4 (crates.io, 2026-10-06), so the numbers do not describe current Sycamore. Not faster than the plain JavaScript-in-V8 baseline: the geometric mean is 1.296x vanillajs-keyed's time (derived from page data), and it is slower than Solid 1.9.3 keyed and Svelte 5.42.1 keyed (geometric-mean slowdown versus the per-benchmark best keyed median: Solid 1.156, Svelte 1.240, this entry 1.356, rank 95 of 196 keyed implementations with full CPU results; derived from page data). The win over React is concentrated in swap rows (React hooks 89.7 ms, itself 8.2x vanillajs's 11.0 ms, vs 13.1 ms here); excluding swap the geometric mean is 0.867x React's time; create 1,000 rows is 1.05x React's time (slower) and select row 1.00x (derived from page data). The suite flags the implementation with note #1139 ('Implementation doesn't pass strict CSP'). Ratios are unweighted geometric means of medians recomputed from the raw results.ts runs, not the site's weighted score. README claim is qualitative ('Lightning Speed', 'full control over performance'), no number. [retier] Independent public suite (krausest/js-framework-benchmark) whose App.tsx names the hardware but labels the run a development snapshot; the measured Wasm is a prebuilt bundle checked into the suite (build-prod is a no-op) with the rustc version not stated, so B not A. The measured code path is gone: the suite's sycamore-v0.9.0-beta.2 bundle (prebuilt October 2023) creates rows by cloning cached &lt;template&gt; content (the beta.2 view! macro emits a static Template per element root, instantiated from TEMPLATE_CACHE), while View v2 in 0.9.0 removed that path and the 0.9.4 sources build each element with document.createElement; nobody has published suite numbers for 0.9.x (current release 0.9.4, 2026-10-06). Bugs fixed after the measured beta: keyed/indexed wrong node order (#795, fixed in PR #796, April 2025), dead dependents piling up after disposing memos (PR #831, 0.9.3) and event callbacks firing after drop (#433, fixed by PR #837 in 0.9.4); tracing the beta.2 reconcile_fragments shows the suite's swap, remove, append and replace-all operations avoid the #795 bug, so the numbers stand. Keyed Rust ranking in the snapshot vs React 19.2 hooks (time ratios, derived from page data): wasm-bindgen 0.584, Silkenweb 0.622, dominator 0.681, Leptos 0.684, Dioxus 0.698, Sycamore 0.711, Yew 0.819, ElementaryUI 0.877; 1.296x vanillajs-keyed's time. No event delegation (issue #176 open since 2021): every on:click is its own wasm-bindgen Closure plus addEventListener; create_root leaks its Root struct by design.

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 47.2 vs React 51.4 (suite units, presumably kB), first paint 209.2 vs 226.6 ms, run memory 2.10 vs 4.37 MB, ready memory 1.68 vs 1.19 MB. sycamore 0.9.0-beta.2 build.

## Maintenance

Active and MIT-licensed (0.9.4 released 2026-10-06, about 313k crates.io downloads), usable today for Rust front ends, but the only independent speed numbers describe a 2023 beta with a since-removed template-cloning renderer, so current performance is unmeasured.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent third-party suite (krausest/js-framework-benchmark, raw per-run data in webdriver-ts-results/src/results.ts) measures sycamore-v0.9.0-beta.2-keyed next to react-hooks-v19.2.0-keyed and vanillajs-keyed; I recomputed every number in the record exactly (geomean 0.711x React, 1.296x vanillajs; swap 13.1 vs 89.7 ms; create 24.8 vs 23.6 ms; create 10k 263.7 vs 401.0 ms). CPU model is stated in App.tsx, but the snapshot is labelled preliminary and the measured bundle is a 2023 prebuilt beta with no Cargo.lock and unstated rustc version, so B not A.
- **Verifier notes:** All claimed numbers reproduce exactly from results.ts; record's 'per-benchmark best' slowdowns (Sycamore 1.57 etc.) reproduce only when non-keyed implementations are pooled into the best, so caveats now give keyed-only figures. Hardware field corrected from App.tsx (MacBook Pro 14 M4 14/20 cores, 48 GB, OSX 26.6.2, Chrome 154.0.8037.98). Shortcomings: measured a 2023 beta (0.9.0-beta.2) not current 0.9.4; slower than vanilla JS (1.296x), Solid and Svelte; win over React mostly from React's slow swap; create 1k slower than React.
- **Fields the verifier corrected:** `hardware`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-102 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/README.md>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/sycamore>
  - <https://github.com/sycamore-rs/sycamore>
  - <https://github.com/sycamore-rs/sycamore/commits>
  - <https://crates.io/api/v1/crates/sycamore>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/README.md>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore/Cargo.toml>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/Cargo.toml>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-reactive/Cargo.toml>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-reactive/src/root.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/lib.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/iter.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/events.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/elements.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/utils.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/components.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/view.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/attributes.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/node/mod.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/node/dom_node.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/node/ssr_node.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-web/src/node/ssr_render.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/sycamore-view-parser/src/codegen.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/examples/js-framework-benchmark/src/main.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/examples/js-framework-benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/tools/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/packages/tools/bench-diff/src/main.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/HEAD/docs/posts/announcing-v0-9-0.md>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/0.9.0-beta.2/packages/sycamore-core/src/render.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/0.9.0-beta.2/packages/sycamore-web/src/dom_node.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/0.9.0-beta.2/packages/sycamore-web/src/dom_node_template.rs>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/0.9.0-beta.2/packages/sycamore-web/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/sycamore/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://crates.io/api/v1/crates/sycamore>
  - <https://github.com/sycamore-rs/sycamore>
  - <https://github.com/sycamore-rs/sycamore/tree/main/packages/tools/bench>
  - <https://github.com/sycamore-rs/sycamore/tree/main/packages/sycamore-web/src>
  - <https://github.com/sycamore-rs/sycamore/tree/main/docs>
  - <https://github.com/sycamore-rs/sycamore/issues?q=is%3Aissue+performance+OR+slow+OR+leak>
  - <https://github.com/sycamore-rs/sycamore/pull/796>
  - <https://github.com/sycamore-rs/sycamore/pull/831>
  - <https://raw.githubusercontent.com/sycamore-rs/sycamore/0.9.0-beta.2/packages/sycamore-macro/src/view/codegen.rs>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/sycamore-rs/sycamore`) · [data/wave13/enrich/raw/github_com_sycamore_rs_sycamore.json](../../../data/wave13/enrich/raw/github_com_sycamore_rs_sycamore.json) (enrichment confidence 0.65)

</details>
