# spair

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Rust/WebAssembly single-page-app framework without a virtual DOM; its 2022 build runs the js-framework-benchmark about 1.5x faster than React 19.2 hooks.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript (vanillajs-keyed) |
| **Claimed result** | README: 'Both small and fast', then says that was correct for previous versions, the main branch is a complete redesign and there are 'No benchmarks for the new design yet'. Suite data for the spair 0.0.8 keyed entry (derived from page data): geometric mean over the 9 CPU benchmarks of the median total duration (medians computed by me from the raw run arrays in results.ts) is 0.662x the time of React 19.2 hooks (about 1.51x faster) and 1.205x the time of vanillajs-keyed; the spair-qr 0.0.8 variant is 0.616x React (about 1.62x faster) and 1.122x vanillajs-keyed. Medians for the main entry: create 1,000 rows 24.6 ms vs React 23.6 ms and vanilla 20.6 ms; swap 1,000 rows 12.5 ms vs React 89.7 ms and vanilla 11.0 ms; create 10,000 rows 262.7 ms vs React 401.0 ms and vanilla 213.3 ms. |
| **Workload** | krausest/js-framework-benchmark: nine WebDriver-driven Chrome benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), median of repeated runs of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14, Apple M4 (14/20 cores), 48 GB RAM, OSX 26.6.2, Chrome 154.0.8037.98 (arm64), as named in webdriver-ts-results/src/App.tsx; the results page labels this a development snapshot that may mix browser versions or run counts (Chrome 154 results commit c097071, 2026-10-04). |
| **Compiler and flags** | frameworks/keyed/spair/Cargo.toml: spair 0.0.8 with keyed-list feature, getrandom 0.2 js, rand 0.8; release profile lto = true, codegen-units = 1 (no opt-level or panic = abort set); the build runs through build.sh (not opened) and the bundle is checked in prebuilt. |
| **Adoption** | 68 stars; crates.io spair 0.0.9 (2022-11-20), about 11.7k downloads |
| **Last commit** | 2026-02-10 |
| **Links** | [repository](https://github.com/aclueless/spair) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark (WebDriver-driven Chrome 154.0.8037.98 on an Apple M4 MacBook Pro 14, a development snapshot), the author-submitted spair 0.0.8 keyed implementation's median total times give a geometric mean of 0.662x React 19.2 hooks over the nine CPU rows (spair-qr 0.616x), but 1.205x vanilla JavaScript (spair-qr 1.122x); medians recomputed from results.ts match the record (create 1,000 rows 24.6 vs 23.6 ms, swap 12.5 vs 89.7 ms, create 10,000 rows 262.7 vs 401.0 ms).

## Use it when

- You are already writing the front end in Rust/Wasm and want one of the faster Rust frameworks in krausest/js-framework-benchmark: spair-qr's geometric mean is 0.616x React's time and spair's is 0.662x, ahead of leptos 0.7.0 (0.684x), dominator (0.681x), dioxus 0.7.2 (0.698x), sycamore (0.711x), mogwai 0.6.5 (0.719x) and yew 0.23 (0.819x) in the same results.ts (derived from page data).
- Keyed tables or lists where rows are reordered or swapped: swap rows is 12.5 ms against React's 89.7 ms, the largest single gap in the suite rows.
- Large initial renders: create 10,000 rows 262.7 ms vs React 401.0 ms (but 1.23x vanilla JavaScript's 213.3 ms).
- Pages where first paint and download size matter more than heap: first paint 137.3 ms vs 226.6 ms and 31.8 kB vs 51.4 kB brotli-compressed against React.

## Skip it when

- You need the fastest possible DOM updates: spair is slower than hand-written vanilla JavaScript on all 9 CPU rows (1.205x geometric-mean time) and slower than the suite's hand-written wasm-bindgen entry (0.584x React), and it is effectively tied with React on create 1,000 rows (24.6 vs 23.6 ms).
- Memory-constrained pages: ready memory 1.70 MB vs React 1.19 MB, run memory 4.97 vs 4.37 MB, and memory after creating and clearing rows 3.54 vs 1.98 MB (spair-qr 2.99 MB).
- Production apps that need a stable API, SSR, event delegation, real routing, documentation or a community: the README lists all of these as missing and the main branch was redesigned again in January 2026.
- Sites with a strict Content Security Policy: the suite flags both spair entries with issue #1139 (Function/eval-style code in the generated bundle).
- You want the benchmarked code: the numbers are for crates.io 0.0.8 (November 2022); the main branch (0.0.10, unpublished) is a complete redesign the README says has no benchmarks yet.

## How it is fast

No virtual DOM: in the current main branch the proc macros work out at compile time which DOM nodes can change, build each view from an HtmlTemplateElement fragment clone, and on update write only those nodes. Keyed lists are reconciled by trimming the common prefix and suffix, detecting single forward or backward moves, and running a longest-increasing-subsequence pass (code copied from the axelf4/lis crate) on the middle so only rows outside the LIS are moved, keyed through an FxHashMap. The measured 0.0.8 design instead re-ran a render function that compared new values with cached ones in place, with static_nodes/static_attributes markers to skip parts that never change; the spair-qr variant adds queue render (QrVec/QrVal containers that push only the changed pieces), which is why it is faster on select (2.5 ms vs 3.7 ms).

## Compared with alternatives

Among the Rust/Wasm siblings measured by the same suite, pick spair (preferably its queue-render mode) over mogwai when keyed-list update speed is the deciding factor (0.616-0.662x React vs mogwai's 0.719x); pick mogwai or the more established Rust frameworks when you need a published, documented API, since spair's fast build is a 2022 release and its current code is an unbenchmarked rewrite.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasm-bindgen, js-sys, web-sys, wasm-bindgen-futures, log, rustc-hash, and the spair-macros proc-macro crate (syn 2, quote, proc-macro2); examples are built with Trunk |
| **Minimum toolchain** | main branch uses Rust edition 2024 (Rust 1.85 or newer) with the wasm32-unknown-unknown target; the benchmarked 0.0.8 crate's minimum is not documented |
| **Platforms** | Browsers only (wasm32-unknown-unknown with web-sys DOM bindings); tests run under wasm-pack test --headless --firefox |
| **Thread safety** | not documented; it runs on the browser main thread and components are single-threaded (Rc-based component handles) |
| **Drop-in for the baseline** | no |

## Gotchas

- The published crate and the benchmark lag the repository: crates.io stops at 0.0.9 (2022-11-20) and the js-framework-benchmark entry pins 0.0.8, while main is an unpublished 0.0.10 rewrite with a different macro API, so code written from the current README will not match either the crate or the measured build.
- The benchmark bundle is prebuilt: build-prod is a no-op that serves the checked-in Trunk output last rebuilt by the author on 2022-11-19, so the Rust and wasm-bindgen versions behind the Chrome 154 numbers are those of late 2022 and are not recorded.
- The view syntax depends on attribute macros rewriting Rust code that looks like function calls; the README warns this 'is a kind of abusing Rust, and may become invalid by changes in Rust in the future'. HTML names that clash with Rust keywords need raw identifiers (r#type, r#for).
- The spair-qr benchmark's swap handler calls swap(1, 998).unwrap_throw() without the bounds guard the plain spair version has, so it throws if fewer than 999 rows exist; this does not affect the suite's 1,000-row runs but shows the queue-render API returns errors the caller must handle.

## Known shortcomings

- Measures the 2022 0.0.8 design that the main branch has replaced; slower than vanilla JS and uses more memory than React; same M4 Chrome 154 snapshot; best keyed-entry gap 1.26x; CSP note #1139.
- Enricher: medians from results.ts match; the numbers measure spair 0.0.8, a prebuilt bundle from 2022-11-19, while the main branch is an unpublished 0.0.10 rewrite with no benchmarks (crates.io stops at 0.0.9); memory after clear is 3.54 vs React 1.98 MB; among Rust frameworks only the hand-written wasm-bindgen entry beats it (0.584x React; spair-qr 0.616x, spair 0.662x).

## Caveats and trade-offs

Independent public suite measured on a MacBook Pro 14 M4 with Chrome 154.0.8037.98 (App.tsx), but the page labels the run a development snapshot and the prebuilt bundle's Rust toolchain is not recorded, so tier B not A (same rules as the catalogue's Yew, Leptos and Sycamore rows). The measured build is spair 0.0.8 (crates.io 2022-11-19); the repository's main branch is a redesign that the README says has no benchmarks yet, so the numbers describe the old design, not current main. The suite attaches note #1139 (implementation does not pass the strict CSP check) to both spair entries. The main entry is slower than vanilla JavaScript on all 9 CPU benchmarks (1.205x geometric-mean time; spair-qr 1.122x and tied on select row at 2.5 ms, derived), and against the per-benchmark best keyed entry it is 1.26x behind (spair-qr 1.17x, derived; the earlier 1.46x figure mixed in non-keyed entries). On create 1,000 rows it is 1.04x React's time and the win over React is dominated by the swap-rows row (12.5 ms vs 89.7 ms). Memory is worse than React (ready 1.70 vs 1.19 MB, run 4.97 vs 4.37 MB) while first paint (137.3 vs 226.6 ms) and compressed size (31.8 vs 51.4 kB) are better. Ratios are unweighted geometric means from results.ts, not the site's weighted score. Prebuilt bundles are checked in ('build-prod is a no-op'; build-prod-force runs build.sh), so the shipped binary may not match current source.

Rust/Wasm framework with no virtual DOM (attribute macros find update sites at compile time) but no event delegation, minimal routing and no SSR, as the README admits. Suite rows for this build: compressed size 31.8 vs React 51.4 (suite units, presumably kB), first paint 137.3 vs 226.6 ms, run memory 4.97 vs 4.37 MB, ready memory 1.70 vs 1.19 MB. The suite flags Rust/Wasm entries with note #1139 (does not pass strict Content Security Policy), which is unrelated to speed.

## Maintenance

Single-author MPL-2.0 project still committed to in February 2026, but the actively developed main branch is an unpublished, undocumented rewrite while the benchmarked and published versions date from November 2022, so treat it as experimental rather than production-ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent public suite (krausest/js-framework-benchmark; implementation in frameworks/keyed/spair, raw runs in webdriver-ts-results/src/results.ts) and my recomputed medians match every quoted number; hardware and browser are named in App.tsx, but the run is labelled a development snapshot and the prebuilt bundle's toolchain is not recorded, so B as for Leptos and Sycamore.
- **Verifier notes:** Numbers recompute exactly from results.ts (0.662x React, 1.205x vanilla keyed; spair-qr 0.616x and 1.122x). Corrections: hardware now named from App.tsx; per-benchmark-best gap is 1.26x among keyed entries (1.46x mixed in non-keyed); CSP note #1139 recorded. Shortcomings: measures the 2022 0.0.8 design that main has replaced, slower than vanilla JS, win over React rests on swap rows, more memory than React.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-125 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/Common.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/package.json>
  - <https://github.com/krausest/js-framework-benchmark/issues/1139>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://github.com/aclueless/spair>
  - <https://github.com/aclueless/spair/commits>
  - <https://crates.io/api/v1/crates/spair>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/README.md>
  - <https://github.com/aclueless/spair>
  - <https://github.com/aclueless/spair/commits/main>
  - <https://github.com/aclueless/spair/issues?q=is%3Aissue>
  - <https://github.com/aclueless/spair/tree/main/spair/src>
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/spair/Cargo.toml>
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/spair-macros/Cargo.toml>
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/test.sh>
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/spair/src/keyed_list.rs>
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/spair/src/lib.rs>
  - <https://raw.githubusercontent.com/aclueless/spair/HEAD/spair/src/component.rs>
  - <https://crates.io/api/v1/crates/spair>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/spair>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/spair/src>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/spair>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/build.sh>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/Trunk.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair/src/main.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/spair-qr/src/main.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/aclueless/spair`) · [data/wave13/enrich/raw/github_com_aclueless_spair.json](../../../data/wave13/enrich/raw/github_com_aclueless_spair.json) (enrichment confidence 0.8)

</details>
