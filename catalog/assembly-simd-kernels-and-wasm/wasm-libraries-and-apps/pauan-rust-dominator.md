# rust-dominator

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust/Wasm DOM library driven by futures-signals, no virtual DOM; about 1.47x faster than React 19.2 hooks in js-framework-benchmark.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README: 'Dominator is one of the fastest DOM frameworks in the world (it is just as fast as Inferno)'. Suite data (derived from page data): geometric mean over the 9 CPU benchmarks of the median total duration (medians computed by me from the raw run arrays in results.ts) is 0.681x the time of React 19.2 hooks (about 1.47x faster, derived from page data); swap 1,000 rows 11.9 ms vs React 89.7 ms; create 1,000 rows 26.5 ms vs React 23.6 ms; create 10,000 rows 282.7 ms vs React 401.0 ms; versus vanillajs-keyed the geometric mean is 1.241x (derived from page data). |
| **Workload** | krausest/js-framework-benchmark: nine WebDriver-driven Chrome benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), median of repeated runs of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14, Apple M4 (14/20 cores, 48 GB), OSX 26.6.2, Chrome 154.0.8037.98 arm64 (suite App.tsx for the Chrome 154 snapshot, which it labels a 'Development snapshot' that 'may mix browser versions or run counts') |
| **Compiler and flags** | Rust release profile: lto=true, panic=abort; built through webpack (frameworks/keyed/dominator/Cargo.toml and package.json). |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-04-07 |
| **Links** | [repository](https://github.com/Pauan/rust-dominator) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark's Chrome 154 run (results.ts, CPU model and Chrome flags not stated), the keyed dominator 0.5.0 entry's median total time averages 0.681x React 19.2 hooks' time over the nine CPU benchmarks (about 1.47x faster, unweighted geometric mean derived from the raw run arrays), but the swap benchmark (11.9 ms vs 89.7 ms) carries most of that: without it the geometric mean is 0.836x. It is slower than React on create 1,000 rows and append, and slower than vanilla JS, Inferno, Solid and Svelte.

## Use it when

- You already want a Rust/Wasm front end and need fine-grained updates of large keyed lists (reorders, partial updates, row selection), where it beats React 19.2 hooks by 1.2x to 7.5x per operation in the suite
- Apps whose state is naturally expressed as futures-signals Mutable and MutableVec values shared between Rust logic and the view
- Wasm bundles where a moderate size budget is acceptable: the suite build is 40.1 kB compressed versus React's 51.4 kB, with first paint at 179.6 ms versus 226.6 ms
- Long-lived single-page apps that do not need server-side rendering

## Skip it when

- You need the fastest DOM layer: in the same suite run it takes 1.24x the time of vanilla JavaScript, 1.13x Inferno 8.2.2 (the README's 'just as fast as Inferno' does not hold), 1.12x Solid 1.9.3, 1.05x Svelte 5.42.1, 1.17x a hand-written wasm-bindgen entry and 1.10x Silkenweb 0.9.0 (unweighted geometric means, derived from page data)
- Bulk creation: creating 1,000 rows takes 26.5 ms versus React's 23.6 ms and appending 1,000 rows 30.6 ms versus 29.3 ms; clearing removes children one at a time (13.0 ms versus 8.7 ms for vanilla JS)
- Server-side rendering or hydration: not supported, and the maintainer argues in issue #29 that signals make standard SSR unworkable
- Memory-tight pages: ready memory 1.76 MB versus React's 1.19 MB and 2.65 MB versus 1.98 MB after five create/clear cycles in the suite
- Teams that need an actively developed framework: the last release is 0.5.38 (August 2024), with one compatibility commit since (April 2026) and open issues #87 (update web-sys) and #89 (panic in Chrome 147)

## How it is fast

There is no virtual DOM or diffing pass: each signal binding is a small future that writes to the one DOM node it owns, and children_signal_vec turns MutableVec change events (VecDiff InsertAt, RemoveAt, Move, Push, Replace) straight into insertBefore and removeChild calls, which is why moving two rows (the suite's swap benchmark) costs 11.9 ms against React's 89.7 ms. Element and attribute names are interned through wasm-bindgen to cut string crossing costs, and the README says the builder API inlines down to raw DOM operations.

## Compared with alternatives

Among the catalogued Rust/Wasm frameworks it sits mid-pack in the same run: 0.96x the time of Sycamore 0.9.0-beta.2, level with Leptos 0.7.0 (0.996x) and Dioxus 0.7.2 (0.975x), 0.83x the time of Yew 0.23.0 struct components, but 1.10x the time of Silkenweb 0.9.0. Pick it when its signal-first, macro-built API without components or a virtual DOM suits you and you accept a slower release cadence; pick Leptos or Dioxus for SSR, hydration and a larger ecosystem.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasm-bindgen, web-sys, js-sys, wasm-bindgen-futures, futures-signals, futures-util, futures-channel, gloo-events, once_cell, discard, pin-project |
| **Minimum toolchain** | Rust 1.80 (rust-version in the current Cargo.toml; the crates.io 0.5.38 release declares none), edition 2018, plus a wasm-bindgen toolchain such as wasm-pack |
| **Platforms** | wasm32 in a browser with a DOM (web-sys); no server-side rendering |
| **Thread safety** | Single-threaded: built on Rc, RefCell and thread_local state, and signal futures run on the wasm-bindgen-futures local executor |
| **Drop-in for the baseline** | no |

## Gotchas

- The suite does not measure current dominator: build-prod is a no-op and the checked-in bundled-dist/accca9b65c226d0a493c.module.wasm embeds the author's cargo registry paths for dominator-0.5.0 (released 2019-06-21), wasm-bindgen-0.2.47 and futures-channel-preview-0.3.0-alpha.16, so the numbers come from a 2019 build that is 38 releases behind 0.5.38
- Signal-driven DOM updates run inside futures spawned with wasm_bindgen_futures::spawn_local, so they are applied when the local executor polls them after Mutable::set returns, not inline with the state change
- style() verifies every property by removing it, setting it and reading it back; if the browser reports an empty value it panics in builds with debug assertions ('style is incorrect') and silently does nothing in release builds; issue #89 reports this panic for style("border", "none") in Chrome 147
- Despite the README's 'updates are always O(1)', the suite implementation gives every row its own subscription to the shared selected-row signal, so one selection wakes all 1,000 row closures (still 3.1 ms versus React's 5.4 ms)

## Known shortcomings

- Beats React (0.681x its time) but takes 1.24x vanilla JavaScript's time and 1.13x Inferno's, so the README "just as fast as Inferno" does not hold; the prebuilt bundle is probably years old; no CPU model. UI framework, filed under wasm-libraries-and-apps.
- The checked-in suite wasm (accca9b65c226d0a493c.module.wasm) embeds dominator-0.5.0 (2019-06-21), wasm-bindgen-0.2.47 and futures-channel-preview-0.3.0-alpha.16, so the suite measures a 2019 build 38 releases behind 0.5.38. Ratios reproduce: 0.681x React, 0.836x React without swap rows; slower than Silkenweb (1.10x), level with Leptos and Dioxus. Issue #89 (style('border', 'none') panics in Chrome 147 debug builds) is open; last release August 2024.

## Caveats and trade-offs

Independent public suite but the CPU model and Chrome flags for the Chrome 154 snapshot are not stated (releases.json labels Chrome 144-146 'macOS', no note for 148-154), so tier B not A. The Wasm bundle is checked in prebuilt ('build-prod is a no-op, the generated javascript is already provided'); the suite directory's commit history shows no rebuild-titled commit since at least January 2021 (only lockfile, metadata and note commits since; titles only), and Cargo.toml asks for dominator 0.5.0 with wasm-bindgen 0.2.46 and wasm-bindgen-futures 0.3, so the measured binary is probably an old 0.5.x build while crates.io's latest is 0.5.38. The geometric-mean win over React is dominated by the swap-rows benchmark (React hooks 89.7 ms vs 11.9 ms here); on create 1,000 rows dominator takes 1.12x React's time. Not faster than hand-written JavaScript or the fastest JS frameworks: 1.241x the time of vanillajs-keyed, 1.123x Solid 1.9.3 keyed, 1.047x Svelte 5.42.1 keyed (derived from page data); rank 77 of 196 keyed entries by geometric-mean slowdown. The README's 'just as fast as Inferno' does not hold in this snapshot: 1.13x the time of inferno-v8.2.2-keyed (derived from page data); the README's table link is an old rawgit copy (not opened). Ratios are the verifier's own unweighted geometric means from the raw results.ts, not the site's weighted score. Carries suite note #1139 (does not pass strict CSP). [retier] Independent public suite (krausest/js-framework-benchmark, Chrome 154 snapshot) whose App.tsx names the hardware but labels the run a development snapshot. The suite does not measure current dominator: build-prod is a no-op and the checked-in bundled-dist/accca9b65c226d0a493c.module.wasm embeds the author's cargo registry paths for dominator-0.5.0 (released 2019-06-21), wasm-bindgen-0.2.47 and futures-channel-preview-0.3.0-alpha.16, so the numbers come from a 2019 build 38 releases behind 0.5.38. Ratios reproduce from results.ts: 0.681x React's time (about 1.47x faster), 0.836x without the swap-rows benchmark; slower than Silkenweb (1.10x) and level with Leptos and Dioxus; 1.241x vanillajs-keyed's time. Signal-driven DOM updates run inside futures spawned with spawn_local, so they apply when the local executor polls them; style() verifies every property by reading it back and panics in debug builds when the browser reports an empty value (open issue #89, style('border', 'none') in Chrome 147); despite the README's 'updates are always O(1)', the suite implementation gives every row its own subscription to the shared selected-row signal. Last release August 2024.

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 40.1 vs React 51.4 (suite units, presumably kB), first paint 179.6 vs 226.6 ms, run memory 3.76 vs 4.37 MB, ready memory 1.76 vs 1.19 MB. Benchmark entry is dominator 0.5.0 with wasm-bindgen 0.2.46 and web-sys 0.3.23 pinned in Cargo.toml (old dependency versions).

## Maintenance

Lightly maintained: the last crates.io release is 0.5.38 (2024-08-22) and the repo's last commit, a web-sys compatibility fix, is from 2026-04-07; MIT-licensed, 1.1k stars and about 400k downloads, usable today, but the benchmark entry measures a 2019 build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (krausest/js-framework-benchmark): raw run arrays in webdriver-ts-results/src/results.ts (Chrome 154, commit 2026-10-04) contain dominator-v0.5.0-keyed and react-hooks-v19.2.0-keyed; implementation and Cargo release profile are public in frameworks/keyed/dominator, but CPU model and Chrome flags are not stated, so B not A.
- **Verifier notes:** All numbers reproduce exactly from results.ts. Real, valid win over React 19.2 hooks (0.681x its time), but slower than vanilla JS (1.24x), Inferno (1.13x, contradicting the README's 'just as fast as Inferno'), Solid and Svelte; the suite's prebuilt bundle is likely years old. Metadata confirmed: MIT, 1.1k stars, last commit 2026-04-07, active, not a fork.
- **Fields the verifier corrected:** `caveats`, `hardware`
- **Shortcomings recorded by:** verifier batch-101 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dominator/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dominator/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/dominator>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://github.com/Pauan/rust-dominator>
  - <https://github.com/Pauan/rust-dominator/commits>
  - <https://crates.io/api/v1/crates/dominator>
- **Sources the enricher read:**
  - <https://github.com/Pauan/rust-dominator>
  - <https://github.com/Pauan/rust-dominator/commits/master>
  - <https://github.com/Pauan/rust-dominator/issues>
  - <https://github.com/Pauan/rust-dominator/issues/89>
  - <https://github.com/Pauan/rust-dominator/issues/29>
  - <https://raw.githubusercontent.com/Pauan/rust-dominator/HEAD/README.md>
  - <https://raw.githubusercontent.com/Pauan/rust-dominator/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Pauan/rust-dominator/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Pauan/rust-dominator/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Pauan/rust-dominator/HEAD/src/dom.rs>
  - <https://raw.githubusercontent.com/Pauan/rust-dominator/HEAD/src/operations.rs>
  - <https://raw.githubusercontent.com/Pauan/rust-dominator/HEAD/src/bindings.rs>
  - <https://crates.io/api/v1/crates/dominator>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dominator/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dominator/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dominator/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dominator/src/lib.rs>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/dominator/bundled-dist>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dominator/bundled-dist/accca9b65c226d0a493c.module.wasm>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/pauan/rust-dominator`) · [data/wave13/enrich/raw/github_com_pauan_rust_dominator.json](../../../data/wave13/enrich/raw/github_com_pauan_rust_dominator.json) (enrichment confidence 0.8)

</details>
