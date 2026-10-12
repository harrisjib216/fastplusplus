# Dioxus (web renderer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust UI framework whose web renderer runs a WebAssembly virtual DOM; about 1.43x faster than React 19.2 hooks in js-framework-benchmark.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README claims are about size ('Simple "hello world" at about 50kb, comparable to React', 'Build WebApps weighing less than 50kb'); it gives no rendering-speed number. Suite data, my unweighted geometric means over the 9 CPU benchmarks of median total duration from the raw run arrays in results.ts (derived from page data): 0.698x the time of react-hooks-v19.2.0-keyed (about 1.43x faster; 0.838x excluding swap rows); 0.715x preact-hooks; 1.002x vue-v3.5.39-keyed; 1.272x vanillajs-keyed; 1.151x solid-v1.9.3-keyed; 1.073x svelte-v5.42.1-keyed. Swap 1,000 rows 14.6 ms vs React 89.7 ms; create 1,000 rows 24.1 ms vs 23.6 ms; create 10,000 rows 257.9 ms vs 401.0 ms. Rank 90 of 196 keyed implementations by slowdown versus the per-benchmark best (1.331). |
| **Workload** | krausest/js-framework-benchmark: nine browser benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), driven by the Puppeteer benchmark driver with reduced tracing (15 runs per benchmark, 25 for select), median of the total (script plus paint) duration per benchmark. |
| **Metric** | latency |
| **Hardware** | Apple M4 (MacBook Pro 14, '14/20 cores', 48 GB RAM), macOS 26.6.2, Chrome 154.0.8037.98 (arm64), per the 'Test environment & methodology' block in webdriver-ts-results/src/App.tsx, which ships with the Chrome 154 results (results.ts commit c097071 'Chrome 154 results', 2026-10-04). The same page sets isOfficial = false and labels itself a development snapshot that 'may mix browser versions or run counts'. |
| **Compiler and flags** | rustc 1.92.0 (ded5c06cf) release build, wasm-bindgen 0.2.106, walrus 0.24.4, dioxus-core/web/signals 0.7.2 (recovered from the shipped wasm; matches the declared source) |
| **Adoption** | 39.4k stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/DioxusLabs/dioxus) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark's Chrome 154.0.8037.98 development snapshot (MacBook Pro 14, Apple M4, macOS 26.6.2), the keyed Dioxus 0.7.2 build took 0.698x the time of react-hooks-v19.2.0-keyed. That figure is the unweighted geometric mean of the nine median total durations, and I reproduced it from results.ts. The gain is mostly swap rows (14.6 vs 89.7 ms) and create 10,000 rows (257.9 vs 401.0 ms); without swap it is 0.838x, and create 1,000 rows is 2% slower. The same data puts it level with Vue 3.5 (1.002x) and behind vanillajs (1.272x), Solid (1.151x) and Svelte 5 (1.073x).

## Use it when

- Rust teams that want one component codebase for web, desktop (webview), mobile and SSR, and still want keyed-list DOM performance at or above React 19 hooks.
- Large keyed tables or lists that are reordered, partly updated or selected often (swap 6.1x, select 1.9x and create 10,000 rows 1.55x faster than React hooks in the suite, derived from page data).
- Apps whose domain logic is already in Rust, which can share types with an axum backend through Dioxus server functions instead of a JSON layer.
- Interactive single-page apps where per-interaction latency matters more than first load.

## Skip it when

- First-load-sensitive pages: in the same run the bundle is 114.9 kB brotli vs React's 51.4 kB, and first paint is 540.9 vs 226.6 ms. The README's '50kb hello world' is not this app's size.
- When you need the fastest DOM framework: Dioxus takes 1.27x the time of vanillajs-keyed, 1.15x Solid, 1.07x Svelte and 1.20x the hand-written wasm-bindgen entry, and ties Vue 3.5 (derived from page data). Clearing rows is its weakest benchmark (16.6 vs 8.7 ms for vanilla). The removeAllChildren fast path, issue #573, has been open since 2022.
- Memory-constrained or long-lived pages with heavy row churn: memory after 5 create/clear cycles is 6.74 MB, against 1.98 MB for React hooks, 4.59 MB for Leptos and 3.55 MB for Sycamore. The figure is higher than after a single 1k run (6.12 MB).
- Sites that enforce a strict Content-Security-Policy: the suite flags the implementation with note 1139 (fails `default-src 'self'`).
- SSR-heavy or Safari-heavy workloads: issue #4216 (open) says dioxus-ssr performs worse than other templating engines. #3076 reported 20-30 s updates in Safari 17.6 on a page of about 2,000 items; it was closed without a fix being named, and maintainers attributed it to Safari's style recalculation.

## How it is fast

rsx! splits markup into static templates and dynamic slots at compile time. dioxus-core diffs only the dynamic parts, and the JS side clones a saved template with `cloneNode(true)` instead of rebuilding it element by element. DOM edits are not one wasm-bindgen call each: dioxus-interpreter-js (sledgehammer_bindgen) writes them as op codes into u8/u16/u32 buffers in wasm memory, decodes strings once per batch with a TextDecoder, caches attribute and namespace names, and replays the whole batch in one `run()` call after each `render_immediate`. Signals re-render only the components that read them, so the keyed swap row does not re-render the list. That row is where React hooks is slow: 14.6 vs 89.7 ms.

## Compared with alternatives

Against the other Rust/Wasm siblings, the CPU rows are a tie: Dioxus takes 1.02x Leptos's time, 0.98x Sycamore's and 1.03x rust-dominator's, all derived from page data. Leptos and Sycamore ship well under half the bundle (48.8 and 47.2 kB vs 114.9 kB compressed) and use less memory. Pick Dioxus for its desktop and mobile renderers, hot-patching dx tooling and fullstack server functions, not for raw DOM speed or size.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | dioxus-core, dioxus-html, dioxus-signals, dioxus-web, dioxus-interpreter-js (sledgehammer_bindgen, sledgehammer_utils), wasm-bindgen, js-sys, web-sys; build with the dx CLI or trunk for wasm32-unknown-unknown |
| **Minimum toolchain** | Rust 1.80 (rust-version of the dioxus 0.7.2 crate); main is edition 2024 with 0.8.0-alpha.1. The benchmark binary was built with rustc 1.92.0 and wasm-bindgen 0.2.106 (read from the shipped wasm). |
| **Platforms** | Any browser with WebAssembly for the web renderer. Other renderers cover desktop and mobile (webview), SSR and liveview, plus an experimental WGPU native renderer. |
| **Thread safety** | not documented in the files read; the web renderer runs one VirtualDom event loop on the browser main thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw, load-time only: the benchmark loads frameworks/keyed/dioxus/bundled-dist/index.html (customURL since 2026-01-24), which is hand-edited. An added inline module script starts dioxus_benchmark.js. Trunk-generated preload tags and a second `await init(...)` script are left in, and they point to server-root files (/dioxus_benchmark-32c73e936749f4d4.js, its _bg.wasm, /snippets/...) that are not in the repository. Those requests fail at page load, which can touch the first-paint and size rows but not the nine CPU rows. The top-level index.html points at a third build (dioxus_benchmark-1e3bca78-...) whose files are also missing.
- Toolchain behind the prebuilt bundle, recovered from the shipped wasm: strings for dioxus-core, dioxus-web and dioxus-signals 0.7.2, a producers section with wasm-bindgen 0.2.106 (11831fb89) and walrus 0.24.4, and rustc commit ded5c06cf ('[stable] prepare Rust 1.92.0'). So the binary matches the declared 0.7.2 source (commit 5ac9bd0, 2026-01-14). There is no Cargo.lock, and `build-prod` is a no-op.
- Dioxus core developers tuned the suite implementation (jkelleyrtp 2022; ealmloff 2024, 'optimize the dioxus implementation and don't leak memory'). It uses a `Signal<String>` per row updated with `write_unchecked`, a `use_set_compare` selector for the selected row, and `use_drop` + `manually_drop` for row signals. Signals created with `Signal::new` in an event handler belong to the enclosing scope and leak in long lists unless dropped like this.
- Benchmarked version is 0.7.2 (December 2025); crates.io has 0.7.10 (2026-07-30) and 0.8.0-alpha.1, and the suite has not re-measured them.

## Known shortcomings

- 0.698x React's time (0.838x excluding swap rows) and level with Vue 3.5 (1.002x), but 1.272x vanillajs-keyed, 1.151x Solid and 1.073x Svelte; krausest development snapshot (MacBook Pro 14 M4, Chrome 154, Puppeteer driver) with toolchain versions behind the prebuilt bundle unstated. UI framework, filed under wasm-libraries-and-apps.
- Enricher: results.ts recomputes to 0.698x React hooks time (0.838x without swap); the bundled-dist/index.html is hand-edited with leftover Trunk tags and a second await init pointing to missing server-root files, so some requests fail at page load (affects first-paint and size rows, not the 9 CPU rows); the toolchain is recoverable from the shipped wasm (dioxus-core/web/signals 0.7.2, wasm-bindgen 0.2.106, walrus 0.24.4, rustc 1.92.0 at ded5c06cf) and matches the declared source; the implementation is tuned by Dioxus core developers (per-row signals, use_set_compare); memory after 5 create/clear cycles 6.74 MB vs React 1.98; clear rows is the weakest row (16.6 vs 8.7 ms vanillajs, issue #573); benchmarked 0.7.2, current 0.7.10. Retiered to A with the toolchain recorded.

## Caveats and trade-offs

Independent public suite with the CPU (Apple M4) and Chrome 154.0.8037.98 stated, but the toolchain versions behind the checked-in prebuilt bundle are not stated ('build-prod' is a no-op: 'the generated javascript is already provided'), so the shipped binary may not match the source, and the results page is marked a development snapshot (isOfficial = false). The win over React hooks is largest on swap rows (89.7 vs 14.6 ms, React hooks' known weak spot); without swap it is 0.838x React's time, and create 1,000 rows is 1.02x React's time. Not faster than the best JavaScript entries (1.272x vanillajs-keyed, 1.151x Solid, 1.073x Svelte, level with Vue 3.5); slowdown versus the per-benchmark best is 1.54 across all implementations, against vanillajs keyed 1.21, Solid keyed 1.34 and Svelte keyed 1.44 (derived from page data). Flagged by suite note 1139 ('Implementation doesn't pass strict CSP'). Bundle sizes are larger than React's in the same results (compressed 114.9 kB vs 51.4 kB; first paint 540.9 vs 226.6 ms). Ratios are my own unweighted geometric means from the raw results.ts, not the site's weighted score. [retier] Implementation tuned by Dioxus core developers (per-row signals, use_set_compare); bundled-dist/index.html hand-edited with requests failing at page load (first-paint and size rows only); clear rows is the weakest row (16.6 vs 8.7 ms vanillajs, issue #573); memory after 5 create/clear cycles 6.74 MB vs React 1.98 MB; benchmarked 0.7.2, current 0.7.10; results page is a dev snapshot

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 114.9 vs React 51.4 (suite units, presumably kB), first paint 540.9 vs 226.6 ms, run memory 6.12 vs 4.37 MB, ready memory 1.90 vs 1.19 MB. Dioxus 0.7.2 with dioxus-web, default features off; trunk build --release.

## Maintenance

Active and copyable: 39.4k stars, MIT OR Apache-2.0, dioxus-web 0.7.10 released 2026-07-30 and 0.8.0-alpha.1 on main, 661 open issues. The suite numbers are for 0.7.2, eight patch releases old, measured on a development snapshot; the bundle's build is load-time-sloppy but traceable to the declared source.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Well-known independent suite (implementation in frameworks/keyed/dioxus, driver in webdriver-ts), and my medians from results.ts reproduce the record exactly. The run's CPU (Apple M4) and Chrome build are stated in webdriver-ts-results/src/App.tsx and the Cargo.toml flags are public. It stays B, not A, because the checked-in prebuilt bundle names no rustc, trunk or wasm-bindgen version and the results page is flagged as a development snapshot.
- **Retiered** B to A: Enricher (2026-10-12): the toolchain the verifier found unstated is recoverable from the shipped wasm binary and matches the declared source (dioxus-core/web/signals 0.7.2, wasm-bindgen 0.2.106, walrus 0.24.4, rustc 1.92.0 at commit ded5c06cf); the js-framework-benchmark harness, implementation and results.ts are public and the CPU rows recompute exactly (0.698x React hooks time, 0.838x without swap). The results page remains a development snapshot and the bundled index.html is hand-edited, which touches only first-paint and size rows.
- **Verifier notes:** Numbers verified exactly from the raw run arrays; React hooks is a fair keyed JS baseline and Dioxus beats it on 7 of 9 benchmarks, but it is level with Vue and slower than vanilla JS, Solid and Svelte. Hardware found in the results app's App.tsx (MacBook Pro 14, Apple M4, macOS 26.6.2, Chrome 154.0.8037.98 arm64). Tier B rather than A only because the prebuilt bundle's toolchain is unstated and the results page is a development snapshot. Metadata matches: 39.4k stars, MIT or Apache-2.0, last commit 2026-10-09.
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
  - <https://github.com/DioxusLabs/dioxus>
  - <https://github.com/DioxusLabs/dioxus/commits>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/dioxus>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/build.sh>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/trunk.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/src/main.rs>
- **Sources the enricher read:**
  - <https://github.com/DioxusLabs/dioxus>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/HEAD/README.md>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/HEAD/packages/web/Cargo.toml>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/HEAD/packages/web/src/lib.rs>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/HEAD/packages/web/src/mutations.rs>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/HEAD/packages/interpreter/Cargo.toml>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/v0.7.2/packages/dioxus/Cargo.toml>
  - <https://raw.githubusercontent.com/DioxusLabs/dioxus/v0.7.2/packages/web/Cargo.toml>
  - <https://crates.io/api/v1/crates/dioxus-web>
  - <https://github.com/DioxusLabs/dioxus/issues?q=is%3Aissue%20label%3Aperformance>
  - <https://github.com/DioxusLabs/dioxus/issues/573>
  - <https://github.com/DioxusLabs/dioxus/issues/3076>
  - <https://github.com/krausest/js-framework-benchmark/issues/1139>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/dioxus>
  - <https://github.com/krausest/js-framework-benchmark/commit/13b2d83>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/dioxus/bundled-dist>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/build.sh>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/trunk.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/trunk.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/src/main.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/bundled-dist/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/bundled-dist/dioxus_benchmark.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/bundled-dist/dioxus_benchmark_bg.wasm>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/bundled-dist/snippets/dioxus-interpreter-js-ce7056f341163470/inline0.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/dioxus/bundled-dist/snippets/dioxus-interpreter-js-ce7056f341163470/src/js/set_attribute.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts/src/benchmarksCommon.ts>
  - <https://github.com/rust-lang/rust/commit/ded5c06cf21d2b93bffd5d884aa6e96934ee4234>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/dioxuslabs/dioxus`) · [data/wave13/enrich/raw/github_com_dioxuslabs_dioxus.json](../../../data/wave13/enrich/raw/github_com_dioxuslabs_dioxus.json) (enrichment confidence 0.8)

</details>
