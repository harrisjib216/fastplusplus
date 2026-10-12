# Silkenweb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust/Wasm signals-based web UI library (no VDOM); about 1.6x faster than React 19.2 hooks in js-framework-benchmark, not faster than vanilla JS.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README: signals-based approach 'can provide better performance' (no number). Suite data (derived from page data): geometric mean over the 9 CPU benchmarks of the median total duration (medians computed by me from the raw run arrays in results.ts) is 0.622x the time of React 19.2 hooks (about 1.61x faster, derived from page data); swap 1,000 rows 11.7 ms vs React 89.7 ms; create 1,000 rows 23.5 ms vs React 23.6 ms; create 10,000 rows 246.0 ms vs React 401.0 ms; versus vanillajs-keyed the geometric mean is 1.133x (derived from page data). |
| **Workload** | krausest/js-framework-benchmark (Chrome 154 development snapshot, Puppeteer benchmark driver with reduced tracing): nine browser benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), 15 measured runs each (25 for select row) after 3-5 warmup runs; metric is the median of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | Apple MacBook Pro 14, 'M4, 14/20 cores' (14 CPU / 20 GPU cores, which matches the M4 Pro configuration; the page says 'M4'), 48 GB RAM, OSX 26.6.2, Chrome 154.0.8037.98 (arm64); stated in webdriver-ts-results/src/App.tsx for the Chrome 154 snapshot (results.ts commit 'Chrome 154 results', 2026-10-04). CPU throttling per benchmark: 4x for partial update, select, swap and clear, 2x for remove. |
| **Compiler and flags** | Rust release profile: lto=true, codegen-units=1, panic=abort; trunk build --release with wasm-bindgen =0.2.99 and wasm_opt version_121 pinned in Trunk.toml, Cargo.lock present (silkenweb 0.9.0, web-sys 0.3.76) (frameworks/keyed/silkenweb). The measured bundle in bundled-dist was prebuilt (last updated 2025-01-14, 'Update to latest Silkenweb version (0.9.0)'); rustc version not stated. |
| **Adoption** | 288 stars |
| **Last commit** | 2026-04-23 |
| **Links** | [repository](https://github.com/silkenweb/silkenweb) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark's Chrome 154 development snapshot (MacBook Pro 14 with Apple M4, 14/20 cores, 48 GB, OSX 26.6.2), the prebuilt silkenweb 0.9.0 keyed implementation had medians of total time across the 9 CPU benchmarks with an unweighted geometric mean 0.622x React 19.2 hooks' (about 1.61x faster) and 1.133x vanillajs-keyed's; most of the gain comes from swap rows (11.7 vs 89.7 ms) and create 10,000 rows (246 vs 401 ms), and these figures were recomputed from the raw run arrays in results.ts (derived from page data).

## Use it when

- You want a Rust/Wasm front end and care about DOM update cost: in the 2026-10 krausest snapshot it is the fastest keyed Rust framework measured (geometric mean 0.622x React's time vs Dominator 0.681, Leptos 0.684, Dioxus 0.698, Sycamore 0.711, Yew 0.819; derived from page data), behind only the hand-written wasm-bindgen implementation (0.584).
- Large keyed lists with reorders: swap 1,000 rows 11.7 ms vs React hooks 89.7 ms, and create 10,000 rows 246 ms vs 401 ms (derived from page data).
- You prefer plain Rust builder syntax (rustfmt, rust-analyzer completion, rustc errors) over a macro DSL, and want SSR with hydration, CSS Modules or Tauri in the same codebase.
- Sharing Rust domain logic between server and browser, with futures-signals as the state model.

## Skip it when

- You need the fastest possible page: vanilla JS and Solid 1.9.3 are faster (Silkenweb is 1.133x vanillajs-keyed's time, Solid 1.105x; derived from page data), and Wasm start-up costs show in first paint (217 ms vs 52 ms for Solid and 54 ms for vanilla JS) and ready memory (1.76 MB vs 0.60 MB for Solid).
- Typical React workloads without big reorders: excluding swap the gain over React drops to 0.756x, and create 1,000 rows is a tie (23.5 vs 23.6 ms).
- You need an ecosystem and momentum: one maintainer, no rendering-speed benchmark of its own, last release 0.10.0 on 2025-05-24, the 20 most recent commits (2026-03-09 to 2026-04-23) are dependency bumps, and 10 dependabot PRs have sat unmerged since May 2026.
- Strict Content-Security-Policy deployments: the suite flags the implementation with issue 1139 (does not pass strict CSP).
- Bundle size matters more than update speed: 44.3 kB compressed vs 4.5 kB for Solid and 9.7 kB for Svelte 5 in the same run.

## How it is fast

Fine-grained push reactivity instead of a virtual DOM: a signal change goes straight to the one DOM call it affects, and a MutableVec emits VecDiff operations (the benchmark's swap is two move_from_to diffs, i.e. two DOM moves) so no tree diff runs. The benchmark rows use the Template DOM (row_template.freeze(), on_instantiate), which builds the row once and instantiates it with cloneNode(true) plus per-row initialisation closures, the same template-cloning idea Solid uses. The measured build also enables the weak-refs feature (event closures handed to the JS GC via Closure::into_js_value instead of tracked in Rust), wasm-bindgen string interning, reference types, wasm-opt -O4, LTO, codegen-units=1 and panic=abort.

## Compared with alternatives

Pick it over Leptos, Sycamore, Dioxus or Yew when you want the fastest keyed DOM updates of the Rust frameworks in this snapshot and plain-Rust builder syntax; pick Dominator for a smaller bundle and faster first paint (40.1 kB, 179.6 ms) at similar speed, and Leptos or Dioxus for a larger ecosystem and server functions.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | futures-signals, wasm-bindgen, web-sys, js-sys and other crates (crossbeam, indexmap, html-escape, lightningcss/parcel_selectors via silkenweb-macros); tokio when built for non-wasm SSR; trunk (or wasm-bindgen CLI) to build for the browser |
| **Minimum toolchain** | not documented (Rust 2021 edition, no rust-version set; wasm32-unknown-unknown target; benchmark pins wasm-bindgen =0.2.99 and wasm-opt version_121) |
| **Platforms** | Browsers via wasm32-unknown-unknown (weak-refs feature needs JS WeakRef support); native targets for server-side rendering and Tauri |
| **Thread safety** | Single-threaded browser model: the DOM types use Rc/RefCell and are not Send; SSR runs per tokio task with a task-local microtask queue (changelog 0.5.0) |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured configuration is not the default one: the benchmark uses the weak-refs cargo feature plus data-weak-refs and data-reference-types in trunk, wasm-bindgen enable-interning, and opt-level 3, while the repo's own workspace release profile uses opt-level "z" (size). With weak-refs enabled but wasm-bindgen's weak references not turned on, every event listener is created with Closure::into_js_value, which wasm-bindgen documents as a memory leak that can 'overwhelm the page quickly and crash the wasm'.
- The benchmark rows are built with the lower-level Template DOM (freeze() and on_instantiate), which the changelog describes as an optimisation for hot code paths; idiomatic builder code as in the README is not what was measured.
- Selection is wired as one selected_row signal that every row subscribes to, so selecting a row wakes all rows' class signals (O(n)); it still measured 3.3 ms vs Solid 3.2 ms at 4x CPU slowdown, so this is a design note, not a flaw in the numbers.
- No harness defect found: the krausest implementation performs each operation the suite specifies (swap(1, 998) as two keyed moves, every 10th label appended with ' !!!', retain-based remove, clear resets selection). The measured Wasm is a prebuilt bundle from silkenweb 0.9.0 (2025-01-14) checked into the suite; crates.io's latest is 0.10.0, which has breaking API changes (prelude removed, TextParentElement split out).

## Known shortcomings

- Takes 1.133x vanilla JavaScript's time and is slower than Solid; the swap-rows row carries the win over React; measured 0.9.0 (latest 0.10.0); krausest snapshot labelled preliminary (MacBook Pro 14 M4, Chrome 154), Wasm bundles prebuilt, rustc version unstated. UI framework, filed under wasm-libraries-and-apps.
- No harness defect in the krausest implementation (swap is two keyed moves; update, remove and clear match the spec). Slower than vanillajs (1.133x) and Solid; first paint 217 ms vs 54 ms for vanilla; memory higher. The measured build is not the default one: weak-refs feature, data-weak-refs, interning, opt-level 3 and the Template DOM path, while the repo's release profile is opt-level 'z'; weak-refs without wasm-bindgen weak references leaks closures (Closure::into_js_value). Fastest keyed Rust framework in the snapshot (0.622x React vs Dominator 0.681, Leptos 0.684, Sycamore 0.711, Yew 0.819; derived from page data), behind hand-written wasm-bindgen (0.584). Maintenance only: last release 0.10.0 (2025-05-24), 10 dependabot PRs unmerged.

## Caveats and trade-offs

Independent public suite (krausest/js-framework-benchmark) and the snapshot states CPU, OS and browser, but results.ts at HEAD is a development snapshot (App.tsx: 'These results are preliminary and may mix browser versions or run counts'), and the measured Wasm is a prebuilt bundle checked into the suite ('build-prod' is a no-op; 'the generated javascript ... is already provided') whose rustc version is not stated, so tier B not A. Measured version is silkenweb 0.9.0; crates.io's latest is 0.10.0 (2025-05-24). Not faster than the plain JavaScript-in-V8 baseline: the geometric mean is 1.133x vanillajs-keyed's time (derived from page data), and it trails Solid 1.9.3 keyed (geometric-mean slowdown versus the per-benchmark best keyed median 1.156) while beating Svelte 5.42.1 keyed (1.240); this entry is 1.186, rank 54 of 196 keyed implementations with full CPU results (derived from page data). The win over React is concentrated in swap rows (React hooks 89.7 ms, itself 8.2x vanillajs's 11.0 ms, vs 11.7 ms here); excluding swap the geometric mean is 0.756x React's time, and create 1,000 rows is 1.00x (derived from page data). The suite flags the implementation with note #1139 ('Implementation doesn't pass strict CSP'). Ratios are unweighted geometric means of medians recomputed from the raw results.ts runs, not the site's weighted score. README makes only a design argument for signals ('can provide better performance'), no number.

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 44.3 vs React 51.4 (suite units, presumably kB), first paint 217.1 vs 226.6 ms, run memory 3.71 vs 4.37 MB, ready memory 1.76 vs 1.19 MB. silkenweb 0.9.0 with weak-refs feature and wasm-bindgen =0.2.99 with enable-interning.

## Maintenance

The library is labelled active but is in maintenance mode: one maintainer, last release 0.10.0 on 2025-05-24, last commit 2026-04-23 (a dependency bump), and dependabot PRs unmerged since May 2026. It is MIT OR Apache-2.0 and usable from crates.io, and no harness defect was found behind the suite numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent third-party suite (krausest/js-framework-benchmark, raw per-run data in webdriver-ts-results/src/results.ts) measures silkenweb-v0.9.0-keyed next to react-hooks-v19.2.0-keyed and vanillajs-keyed; I recomputed every number in the record exactly (geomean 0.622x React, 1.133x vanillajs; swap 11.7 vs 89.7 ms; create 23.5 vs 23.6 ms; create 10k 246.0 vs 401.0 ms). CPU model is stated in App.tsx, but the snapshot is labelled preliminary and the measured bundle is prebuilt with an unstated rustc version, so B not A.
- **Verifier notes:** All claimed numbers reproduce exactly from results.ts; record's 'per-benchmark best' slowdowns (vanilla 1.21, Solid 1.34, Svelte 1.44, this 1.37) also reproduce but only when the best is taken over keyed and non-keyed implementations together, so caveats were rewritten with keyed-only figures (vanilla 1.046, Solid 1.156, Svelte 1.240, Silkenweb 1.186). Hardware field was wrong: App.tsx states MacBook Pro 14 M4 (14/20 cores), 48 GB, OSX 26.6.2, Chrome 154.0.8037.98; tier kept B for prebuilt bundle and preliminary snapshot (if the orchestrator raises the krausest family to A, apply it to all siblings consistently). Shortcomings: slower than vanilla JS (1.133x) and Solid; win over React mostly from React's slow swap; measured 0.9.0, latest 0.10.0.
- **Fields the verifier corrected:** `hardware`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-102 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/Trunk.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/Cargo.lock>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/silkenweb>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/silkenweb>
  - <https://github.com/silkenweb/silkenweb>
  - <https://github.com/silkenweb/silkenweb/commits>
  - <https://crates.io/api/v1/crates/silkenweb>
- **Sources the enricher read:**
  - <https://github.com/silkenweb/silkenweb>
  - <https://github.com/silkenweb/silkenweb/commits>
  - <https://github.com/silkenweb/silkenweb/issues?q=is%3Aissue>
  - <https://github.com/silkenweb/silkenweb/issues/26>
  - <https://github.com/silkenweb/silkenweb/pulls>
  - <https://github.com/silkenweb/silkenweb/tree/main/packages/silkenweb/src/dom>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/README.md>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/packages/silkenweb/Cargo.toml>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/packages/silkenweb/src/lib.rs>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/packages/silkenweb/src/dom.rs>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/packages/silkenweb/src/dom/template.rs>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/packages/silkenweb/src/dom/wet.rs>
  - <https://raw.githubusercontent.com/silkenweb/silkenweb/HEAD/packages/silkenweb/src/dom/private.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/src/main.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/Trunk.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/silkenweb/package.json>
  - <https://raw.githubusercontent.com/Pauan/rust-signals/HEAD/src/signal_vec.rs>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/0.2.99/src/closure.rs>
  - <https://crates.io/api/v1/crates/silkenweb>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/silkenweb/silkenweb`) · [data/wave13/enrich/raw/github_com_silkenweb_silkenweb.json](../../../data/wave13/enrich/raw/github_com_silkenweb_silkenweb.json) (enrichment confidence 0.8)

</details>
