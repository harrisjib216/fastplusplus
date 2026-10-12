# mogwai

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust/Wasm browser GUI crate without a virtual DOM; its 2023 benchmark build beats React 19.2 hooks, but not vanilla JS.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript (vanillajs-keyed) |
| **Claimed result** | README makes no speed claim. Suite data for the mogwai 0.6.5 keyed entry (derived from page data): geometric mean over the 9 CPU benchmarks of the median total duration (medians computed from the raw run arrays in results.ts) is 0.719x the time of React 19.2 hooks (about 1.39x faster) and 1.310x the time of vanillajs-keyed. The non-keyed mogwai 0.6.5 entry is 1.313x the time of vanillajs-non-keyed (0.679x keyed React, a cross-mode comparison). Medians for the keyed entry: create 1,000 rows 23.9 ms vs React 23.6 ms and vanilla 20.6 ms; swap 1,000 rows 13.0 ms vs React 89.7 ms; create 10,000 rows 357.4 ms vs React 401.0 ms; append rows 37.8 ms vs React 29.3 ms. |
| **Workload** | krausest/js-framework-benchmark: nine WebDriver-driven Chrome benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), median of repeated runs of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14, Apple M4 (14/20 cores), 48 GB RAM, OSX 26.6.2, Chrome 154.0.8037.98 (arm64), as named in webdriver-ts-results/src/App.tsx; the results page labels this a development snapshot that may mix browser versions or run counts (Chrome 154 results commit c097071, 2026-10-04). |
| **Compiler and flags** | frameworks/keyed/mogwai/Cargo.toml: mogwai-dom 0.2.2, wasm-bindgen 0.2.83, benchmark app crate mogwai-js-framework-benchmark (lives in the mogwai repo); release profile codegen-units = 1, lto = true, panic = abort; wasm-pack release with wasm-opt -O4. Bundle checked in prebuilt. |
| **Adoption** | 427 stars; crates.io mogwai 0.8.0 (2026-09-26), about 54k downloads |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/schell/mogwai) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark (MacBook Pro 14 M4, Chrome 154, development snapshot), the keyed mogwai 0.6.5 entry has a median total duration geometric mean of 0.719x React 19.2 hooks over the nine CPU benchmarks (recomputed here from results.ts), driven by swap rows (13.0 vs 89.7 ms), select (3.3 vs 5.4 ms) and update every 10th row (11.5 vs 14.7 ms), and is 1.31x slower than vanillajs-keyed. Create and replace-all timings benefit from the app's DOM row pool, and the prebuilt wasm bundle's toolchain is not recorded.

## Use it when

- A Rust-only team building an interactive browser UI that wants no JavaScript framework and no virtual DOM.
- Lists that are reordered or patched in place (swaps, single-row inserts and removals), where direct DOM patching beats React's keyed diff by a wide margin.
- Code that should render both in the browser and on the server from the same widget types (the ssr feature).
- Small to medium apps where an async, futures-based event model fits better than callback closures.

## Skip it when

- You need the fastest DOM code: vanilla JavaScript is faster on all nine CPU benchmarks (about 1.31x less time on geometric mean), and other Rust/Wasm entries in the same run (spair 0.662x, Leptos 0.684x, Dioxus 0.698x, Sycamore 0.711x of React's time) edge out mogwai's 0.719x.
- Startup, memory or download size matter: the measured build paints first at 306 ms against 227 ms for React, uses 9.65 MB against 4.37 MB after running, and ships 66.3 against 51.4 compressed units.
- Large appends: appending 1,000 rows to 1,000 takes 37.8 ms against 29.3 ms for React.
- You want benchmark numbers that describe the current crate: the suite measures mogwai 0.6.5 from 2023, and 0.8.0 (2026) has a different API that has not been submitted.
- Projects that need a mature ecosystem: three open issues, a small user base (about 427 stars) and a single main author.

## How it is fast

There is no virtual DOM diff: views create real DOM nodes through web-sys once, and updates go straight to the bound text or attribute (fine-grained reactivity). In the measured 0.6.5/mogwai-dom 0.2 build, lists are a ListPatchModel whose remove, replace and insert patches move existing DOM nodes, which is why swapping two of 1,000 rows costs 13.0 ms against 89.7 ms for React's keyed reconciliation. The benchmark app also uses two app-level tricks: one delegated click handler on the container that reads a 'key' attribute, and a pool that keeps cleared or removed Row objects with their DOM nodes and reuses them for new rows.

## Compared with alternatives

Against spair, the only Rust/Wasm UI sibling catalogued here, mogwai is slightly slower on the same suite run (0.719x against 0.662x of React's time) but has a newer release (0.8.0, September 2026) and server-side rendering; pick it for its futures-based event model, not for speed.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasm-bindgen, wasm-bindgen-futures and web-sys (web feature), async-channel (ssr feature), futures-core, mogwai-macros |
| **Minimum toolchain** | Rust edition 2024 (rustc 1.85+) for mogwai 0.8.0, wasm32-unknown-unknown target, wasm-bindgen; trunk recommended |
| **Platforms** | browsers through wasm32-unknown-unknown; native targets for server-side rendering |
| **Thread safety** | not documented; browser code runs on the single JS thread via wasm_bindgen_futures::spawn_local |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured keyed entry recycles DOM rows: mogwai-js-framework-benchmark 0.1.0 (src/lib.rs, the App the suite builds) moves cleared and removed Row objects with their captured &lt;tr&gt; nodes into an 11,000-slot cache and dequeue() reuses them for new ids and labels. The suite warms up 'create rows' with run and clear, and 'replace all rows' with repeated runs, so the timed create and replace reattach 1,000 recycled rows instead of building new ones (1,000 of 10,000 in 'create many rows'). The suite's keyed check only counts added and removed &lt;tr&gt; mutations, so it passes, yet this breaks the 1:1 data-item-to-DOM-node rule that defines keyed mode. Dropping those three benchmarks still leaves mogwai at 0.635x React's time, so the React claim survives, but the replace-all win (26.3 vs 30.2 ms) rests on the recycling.
- The same app uses manual event delegation (one click handler on #main matching #run, .lbl and .remove and parsing a 'key' attribute) and keeps selection state on each row model, which the suite flags for other entries as notes #801 and #800; the mogwai entry carries only note #1139 (strict CSP).
- The benchmark app in the current repository (crates/mogwai-js-framework-benchmark 0.2.0, mogwai 0.8) is non-keyed: its swap copies ids and labels between rows 1 and 998, and clear empties the tbody with set_text_content; it also logs at Trace level on every click. If submitted, it belongs in the non-keyed table.
- No LICENSE file at the repository root; the MIT licence comes from Cargo.toml metadata (the benchmark app crate is MIT OR Apache-2.0).

## Known shortcomings

- Measures mogwai 0.6.5 (2023), not the current 0.8.0; slower than vanilla JS on all nine operations and the win over React rests on the swap rows; MacBook Pro 14 M4, Chrome 154 development snapshot; among keyed entries the best-entry gap is 1.37x; no licence file in the repo (MIT only on crates.io); CSP note #1139.
- Enricher: the keyed app keeps cleared and removed rows with their &lt;tr&gt; nodes in a cache and reuses them for new ids, so the timed create-1k and replace-all runs reuse warm-up rows and create-10k reuses the 1k rows; the suite's keyed check only counts tr mutations, so it passes. Without rows 01, 02 and 07 mogwai is still 0.635x React, so the React claim holds, but the replace-all win (26.3 vs 30.2 ms) rests on recycling. Manual event delegation and row-model selection (suite notes #800 and #801 missing). The repo's current bench app (0.2.0) is non-keyed.

## Caveats and trade-offs

Independent public suite measured on a MacBook Pro 14 M4 with Chrome 154.0.8037.98 (App.tsx), but the page labels the run a development snapshot and the prebuilt bundle's Rust toolchain is not recorded, so tier B not A (same rules as Leptos and Sycamore). The measured build is mogwai 0.6.5 (crates.io 2023-02-01) with the mogwai-js-framework-benchmark 0.1.0 app crate (2023-02-02) and mogwai-dom 0.2.x (last release 0.2.6, 2023-10-29); the current crate is 0.8.0 (2026-09-26) and its API (View trait, rsx! macro, events as futures) differs, so the suite numbers describe the old version, not current mogwai. The suite attaches note #1139 (implementation does not pass the strict CSP check). Slower than vanilla JavaScript on all 9 CPU benchmarks (1.31x geometric-mean time, derived), slower than React on append rows (1.29x React's time) and create 1,000 rows (1.01x), and worse than React on first paint (306.3 vs 226.6 ms), memory (run memory 9.65 vs 4.37 MB) and compressed size (66.3 vs 51.4 kB). The geometric-mean win over React is dominated by swap rows (13.0 ms vs 89.7 ms). Against the per-benchmark best keyed entry it is 1.37x behind (derived; the earlier 1.59x figure mixed in non-keyed entries). Ratios are unweighted geometric means from results.ts, not the site's weighted score. No LICENSE or COPYING file exists at the repository root; the MIT licence comes from crates.io metadata (every listed version declares MIT). The bundle is checked in prebuilt (build-prod is a no-op). [retier] Enricher: the keyed app recycles cleared rows and their &lt;tr&gt; nodes for new ids, so create-1k, create-10k and replace-all reuse earlier rows (the suite's keyed check misses it); without rows 01, 02 and 07 mogwai is still 0.635x React.

Rust/Wasm GUI crate with events as futures and a Proxy-based update model; also builds for non-browser views. Suite rows for the keyed entry: compressed size 66.3 vs React 51.4 (suite units, presumably kB), first paint 306.3 vs 226.6 ms, run memory 9.65 vs 4.37 MB, ready memory 2.82 vs 1.19 MB. Flagged in the suite with note #1139 (strict CSP), unrelated to speed.

## Maintenance

Actively developed (0.8.0 released 2026-09-26, three open issues), MIT-licensed per crates.io metadata, but the only public speed data describe the 2023 0.6.5 release built with an app that recycles rows and delegates events by hand.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent public suite (krausest/js-framework-benchmark; implementation in frameworks/keyed/mogwai, raw runs in webdriver-ts-results/src/results.ts) and my recomputed medians match every quoted number; hardware and browser are named in App.tsx, but the run is labelled a development snapshot and the prebuilt wasm bundle's rustc, wasm-pack and wasm-bindgen versions are not recorded, so B as for Leptos and Sycamore.
- **Verifier notes:** Numbers recompute exactly from results.ts (0.719x React, 1.310x vanilla keyed). Corrections: hardware now named from App.tsx; per-benchmark-best gap is 1.37x among keyed entries (1.59x mixed in non-keyed); non-keyed entry compared to vanillajs-non-keyed (1.313x); CSP note #1139 and missing repo licence file recorded. Shortcomings: measures a 2023 version, slower than vanilla JS everywhere, win over React rests on swap rows, worse memory and first paint.
- **Fields the verifier corrected:** `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-125 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/Common.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/mogwai/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/mogwai/package.json>
  - <https://github.com/krausest/js-framework-benchmark/issues/1139>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://github.com/schell/mogwai>
  - <https://github.com/schell/mogwai/commits>
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/mogwai>
  - <https://crates.io/api/v1/crates/mogwai-dom>
  - <https://crates.io/api/v1/crates/mogwai-js-framework-benchmark>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/README.md>
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/crates/mogwai/Cargo.toml>
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/crates/mogwai-benches/Cargo.toml>
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/crates/mogwai-js-framework-benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/crates/mogwai-js-framework-benchmark/src/lib.rs>
  - <https://raw.githubusercontent.com/schell/mogwai/HEAD/crates/mogwai-js-framework-benchmark/src/app.rs>
  - <https://github.com/schell/mogwai/issues>
  - <https://crates.io/api/v1/crates/mogwai-js-framework-benchmark/versions>
  - <https://static.crates.io/crates/mogwai-js-framework-benchmark/mogwai-js-framework-benchmark-0.1.0.crate>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/mogwai/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/mogwai/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/mogwai/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/mogwai/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts/src/isKeyed.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts/src/benchmarksPuppeteer.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/Common.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/schell/mogwai`) · [data/wave13/enrich/raw/github_com_schell_mogwai.json](../../../data/wave13/enrich/raw/github_com_schell_mogwai.json) (enrichment confidence 0.8)

</details>
