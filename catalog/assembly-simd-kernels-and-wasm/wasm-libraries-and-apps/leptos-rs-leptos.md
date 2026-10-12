# Leptos

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust/Wasm fine-grained-reactive web UI framework; about 1.46x faster than React 19.2 hooks in js-framework-benchmark, slower than vanilla JS.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README claim (no number): Leptos is 'much faster at both creating and updating the UI than Yew'. Suite data (derived from page data): geometric mean over the 9 CPU benchmarks of the median total duration (medians computed by me from the raw run arrays in results.ts) is 0.684x the time of React 19.2 hooks (about 1.46x faster, derived from page data); swap 1,000 rows 12.2 ms vs React 89.7 ms; create 1,000 rows 25.1 ms vs React 23.6 ms; create 10,000 rows 267.1 ms vs React 401.0 ms; versus vanillajs-keyed the geometric mean is 1.246x (derived from page data). |
| **Workload** | krausest/js-framework-benchmark: nine WebDriver-driven Chrome benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), median of repeated runs of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14, Apple M4 (14/20 cores, 48 GB), OSX 26.6.2, Chrome 154.0.8037.98 arm64 (suite App.tsx for the Chrome 154 snapshot, which it labels a 'Development snapshot' that 'may mix browser versions or run counts') |
| **Compiler and flags** | Rust release profile: lto=true, codegen-units=1, panic=abort; wasm-pack release build, wasm-opt -O4, esbuild minify (frameworks/keyed/leptos/Cargo.toml and package.json). |
| **Adoption** | 21.4k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/leptos-rs/leptos) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark (Chrome 154 snapshot, CPU model not stated), leptos-v0.7.0-keyed needs 0.684x the time of react-hooks-v19.2.0-keyed as an unweighted geometric mean of the medians of nine table benchmarks, with swap rows (12.2 vs 89.7 ms) driving most of the gap; create 1,000 rows is slower (25.1 vs 23.6 ms) and it is 1.246x slower than vanilla JS. The README's only performance claim is qualitative ('much faster ... than Yew'), and the suite shows Leptos about 1.20x faster than Yew 0.23.

## Use it when

- You want to write a browser UI in Rust (shared types with an Axum or Actix backend, server functions) and need DOM update speed at least as good as React's.
- Large keyed tables or lists with reorder, partial-update and select patterns: in the suite Leptos takes 0.136x React hooks' time on swap rows, 0.574x on select row, 0.776x on partial update and 0.666x on create 10,000 rows.
- SSR plus hydration or streaming HTML apps where the same Rust components render on server and client.
- Teams already on Rust that are choosing between Rust UI frameworks: Leptos is within a few percent of Sycamore, Dioxus and rust-dominator on suite speed and has the largest ecosystem of the Rust options.

## Skip it when

- If raw DOM speed is the goal and JavaScript is acceptable: on the same suite Leptos takes 1.246x vanillajs-keyed's time, 1.128x Solid 1.9.3, 1.135x Inferno and 1.052x Svelte 5.42.1 (derived from page data).
- Startup- or memory-sensitive pages: first paint 239.6 ms vs React's 226.6 ms, ready memory 1.77 vs 1.19 MB, run memory 5.45 vs 4.37 MB, and about 190 kB uncompressed / 48.8 kB compressed bundle vs Solid's 11.5 / 4.5 kB.
- Workloads dominated by creating or clearing rows: create 1,000 rows is 1.06x React's time, append is a tie, clear rows is 15.6 ms vs 8.7 ms for vanilla JS.
- Projects that need long-term active development: the May 2026 status update (issue #4707) calls Leptos feature-complete and 'lightly maintained going forward', with 0.9 a semver-breaking cleanup release.
- Sites that require a strict Content-Security-Policy: the suite tags the Leptos entry with note #1139 (does not pass strict CSP).

## How it is fast

Fine-grained reactivity in the SolidJS style: each component runs once, creates real DOM nodes and wires signals to the exact text node, class or attribute that depends on them, so there is no virtual-DOM re-render or diff (reactive_graph plus the tachys renderer). Keyed lists use the &lt;For&gt; component's keyed diff, Selector gives O(1) selection changes, the template! macro renders static HTML into a &lt;template&gt; at compile time and clones it, and the optional delegation feature installs one event listener per event type instead of one per element. Release builds use LTO, codegen-units=1, panic=abort and wasm-opt -O4.

## Compared with alternatives

Pick Leptos over Yew when speed matters (Yew 0.23 takes about 1.20x Leptos's time, Yew hooks about 1.51x) and over Sycamore, Dioxus or rust-dominator (all within 4% of Leptos) when you want SSR, streaming and server functions in one framework; pick hand-written wasm-bindgen code (Leptos takes 1.171x its time) or Silkenweb (1.099x) when only the last bit of DOM speed and lower memory matter (derived from page data).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasm-bindgen, web-sys and js-sys for the browser; reactive_graph, tachys, leptos_macro, server_fn and related workspace crates; getrandom with its JS backend if the app uses rand on wasm; build with cargo-leptos, Trunk or wasm-pack |
| **Minimum toolchain** | Rust 1.88 (workspace rust-version, edition 2024 on main); the measured build used the 'nightly' feature, which needs a nightly toolchain |
| **Platforms** | Browsers with WebAssembly (wasm32-unknown-unknown) for client rendering; any Rust server target for SSR |
| **Thread safety** | Signals are Copy + 'static handles owned by a reactive owner; Arc\* variants (ArcRwSignal) are Send + Sync for server use; browser rendering is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured build is not the default configuration: the suite builds Leptos 0.7 with the 'nightly' and 'delegation' features (main's own examples/js-framework-benchmark says 'for actual benchmarking, add nightly and delegation features') and uses the template! macro; a stock csr build attaches one listener per element.
- The 1.46x geometric-mean win over React is mostly one row: React hooks takes 89.7 ms on swap rows against 11-14.6 ms for Leptos, Solid, Inferno, Svelte and vanilla JS. Without swap rows the geometric mean is 0.837x React's time, about 1.19x faster (derived from page data).
- The suite measures Leptos 0.7 from a prebuilt bundle checked into the benchmark repo (no Cargo.lock, 'build-prod is a no-op'), while crates.io's latest stable is 0.8.22 and main moved to 0.9.0-beta2 on 2026-10-10; current versions are unmeasured.
- COMMON_BUGS.md warns that writing to a signal from an Effect creates update chains and can loop forever, and that value=... on &lt;input&gt; only sets the default value (use prop:value).

## Known shortcomings

- Beats React 19.2 hooks (0.684x its time) but takes 1.25x vanilla JavaScript keyed's time and is slower than Inferno, Solid and Svelte; the suite measures 0.7 while the current release is 0.8.22; no CPU model or Chrome flags. UI framework, filed under wasm-libraries-and-apps.
- Suite numbers reproduce from results.ts. The 0.684x-of-React geomean is mostly one row (swap rows 12.2 vs 89.7 ms); without it the geomean is 0.837x (derived from page data). The measured build is tuned past the defaults: 'nightly' and 'delegation' features plus the template! macro (main's own example says to add them for benchmarking); the measured 0.7 bundle has no Cargo.lock and the current 0.8.22 / 0.9.0-beta2 are unmeasured; the author called the project 'lightly maintained' in issue #4707 (May 2026). Roughly even with Sycamore, Dioxus and dominator; slower than Silkenweb (1.099x) and hand-written wasm-bindgen (1.171x).

## Caveats and trade-offs

Independent public suite but the CPU model and Chrome flags for the Chrome 154 snapshot are not stated (releases.json labels Chrome 144-146 'macOS', no note for 148-154), so tier B not A. Wasm implementations are checked in as prebuilt bundles ('build-prod is a no-op, the generated javascript is already provided'); the suite pins leptos 0.7 (bundle last touched by build commits on 2025-10-12/15), while crates.io's latest is 0.8.22 and main merged the leptos_0.9 branch on 2026-10-10, so the measured version is one to two minor versions behind. The build uses Leptos's 'nightly' feature (nightly Rust toolchain). The geometric-mean win over React is dominated by the swap-rows benchmark (React hooks 89.7 ms vs 12.2 ms here); on create 1,000 rows Leptos takes 1.06x React's time. Not faster than hand-written JavaScript or the fastest JS frameworks: 1.246x the time of vanillajs-keyed, 1.135x Inferno keyed, 1.128x Solid 1.9.3 keyed, 1.052x Svelte 5.42.1 keyed (derived from page data); rank 78 of 196 keyed entries by geometric-mean slowdown. Ratios are the verifier's own unweighted geometric means from the raw results.ts, not the site's weighted score. README says Leptos is 'much faster at both creating and updating the UI than Yew'; in this data Leptos is 1.20x faster than Yew 0.23 on the same geometric mean (derived from page data). Carries suite note #1139 (does not pass strict CSP).

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 48.8 vs React 51.4 (suite units, presumably kB), first paint 239.6 vs 226.6 ms, run memory 5.45 vs 4.37 MB, ready memory 1.77 vs 1.19 MB. Leptos 0.7 with csr, nightly and delegation features; benchmark-specific build.

## Maintenance

Active and widely used (21.4k stars, 5.2M crates.io downloads, last commit 2026-10-10 merging the 0.9 branch) but declared feature-complete and lightly maintained by its author in May 2026; MIT-licensed and usable as a crate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (krausest/js-framework-benchmark): raw run arrays in webdriver-ts-results/src/results.ts (Chrome 154, commit 2026-10-04) contain leptos-v0.7.0-keyed and react-hooks-v19.2.0-keyed; implementation and Cargo release profile are public in frameworks/keyed/leptos, but CPU model and Chrome flags are not stated, so B not A.
- **Verifier notes:** All numbers reproduce exactly from results.ts. Real, valid win over React 19.2 hooks (0.684x its time), but slower than vanilla JS (1.25x), Inferno, Solid and Svelte, so the record should not read as 'faster than JS in V8' generally; the suite also measures Leptos 0.7, not the current 0.8/0.9. Metadata confirmed: MIT, 21.4k stars, last commit 2026-10-10, active, not a fork.
- **Fields the verifier corrected:** `caveats`, `hardware`
- **Shortcomings recorded by:** verifier batch-101 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/leptos/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/leptos/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/leptos>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://github.com/leptos-rs/leptos>
  - <https://github.com/leptos-rs/leptos/commits>
  - <https://crates.io/api/v1/crates/leptos>
- **Sources the enricher read:**
  - <https://github.com/leptos-rs/leptos>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/README.md>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/leptos/Cargo.toml>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/tachys/Cargo.toml>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/tachys/src/html/event.rs>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/leptos_macro/src/lib.rs>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/examples/js-framework-benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/examples/js-framework-benchmark/src/lib.rs>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/docs/COMMON_BUGS.md>
  - <https://raw.githubusercontent.com/leptos-rs/leptos/HEAD/SECURITY.md>
  - <https://github.com/leptos-rs/leptos/commits/main>
  - <https://github.com/leptos-rs/leptos/issues?q=is%3Aissue+performance+OR+slow+OR+%22memory+leak%22>
  - <https://github.com/leptos-rs/leptos/issues/4291>
  - <https://github.com/leptos-rs/leptos/issues/4707>
  - <https://crates.io/api/v1/crates/leptos>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/leptos/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/leptos/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/leptos/src/lib.rs>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/leptos>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/leptos-rs/leptos`) · [data/wave13/enrich/raw/github_com_leptos_rs_leptos.json](../../../data/wave13/enrich/raw/github_com_leptos_rs_leptos.json) (enrichment confidence 0.8)

</details>
