# wasm-bindgen with web-sys (hand-written benchmark implementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust-to-JavaScript binding generator; hand-written Rust DOM code built with it takes 0.58x React 19.2 hooks' time in js-framework-benchmark.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | No performance claim by the project; evidence only from the suite. Suite data (derived from page data): geometric mean over the 9 CPU benchmarks of the median total duration (medians computed by me from the raw run arrays in results.ts) is 0.584x the time of React 19.2 hooks (about 1.71x faster, derived from page data); swap 1,000 rows 11.6 ms vs React 89.7 ms; create 1,000 rows 22.4 ms vs React 23.6 ms; create 10,000 rows 234.7 ms vs React 401.0 ms; versus vanillajs-keyed the geometric mean is 1.064x (derived from page data). |
| **Workload** | krausest/js-framework-benchmark (Chrome 154 development snapshot, Puppeteer benchmark driver with reduced tracing): nine browser benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), 15 measured runs each (25 for select row) after 3-5 warmup runs; metric is the median of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14, Apple M4 (14/20 cores, 48 GB), OSX 26.6.2, Chrome 154.0.8037.98 arm64 (suite App.tsx for the Chrome 154 snapshot, which it labels a 'Development snapshot' that 'may mix browser versions or run counts') |
| **Compiler and flags** | Checked-in suite bundle (producers section): rustc 1.69.0-nightly (658fad6c5 2023-02-03), wasm-bindgen 0.2.84 (cea8cc3d2), walrus 0.19.0; Rust release profile lto = true, panic = abort (no codegen-units = 1); trunk build --release; old heap-array object-table JS glue, no externref (reference types are on by default only since Rust 1.82). Current wasm-bindgen 0.2.129 output is unmeasured. |
| **Adoption** | 9.2k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/wasm-bindgen/wasm-bindgen) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark's Chrome 154 snapshot on a MacBook Pro 14 (M4, 14/20 cores, 48 GB, macOS 26.6.2), the suite's hand-written wasm-bindgen 0.2.84 keyed implementation needs 0.584x the time of react-hooks-v19.2.0-keyed (unweighted geometric mean of the median total duration over nine benchmarks; swap rows 11.6 vs 89.7 ms) and 1.064x the time of vanillajs-keyed. The wasm-bindgen project itself makes no speed claim; these are the suite's numbers recomputed from results.ts.

## Use it when

- You already have a Rust/Wasm app and want the cheapest possible DOM layer for a hot table or list: the hand-written web-sys version takes 0.58x React 19.2 hooks' time over nine benchmarks and is faster than every Rust framework in the suite (Leptos 0.7 takes 1.17x its time, Dioxus 0.7 1.20x, Yew 0.23 1.40x, derived from page data).
- Reorder-heavy keyed lists where React is weak: swap rows 11.6 ms vs React's 89.7 ms; create 10,000 rows 234.7 vs 401.0 ms.
- Startup- and size-sensitive Rust pages: first paint 73.9 ms vs 226.6 ms for React and 239.6 ms for Leptos; compressed bundle 14.5 vs React's 51.4 and Leptos's 48.8 (suite units).
- As the substrate under any Rust web framework (Leptos, Yew, Dioxus, Sycamore, dominator and Silkenweb all sit on wasm-bindgen and web-sys); use it directly where a framework's reactivity costs too much.

## Skip it when

- If JavaScript is acceptable and speed is the goal: vanillajs-keyed takes 0.939x this build's time and Solid 1.9.3 only 1.038x, with far smaller memory (ready memory 0.48 MB vanilla vs 1.72 MB here) (derived from page data).
- Large UIs that need components, state management or SSR: this is imperative DOM code with no rendering model; you hand-write every update, as the 285-line benchmark program shows.
- Workloads dominated by short strings and many small DOM calls: every web-sys call goes through a JS shim and strings are copied and transcoded UTF-8 to UTF-16 per call (maintainers in issue #1185); the uibench port there lost to vanilla innerHTML.
- Pages behind a strict Content-Security-Policy: the suite flags this entry with note #1139 ('Implementation doesn't pass strict CSP').
- Teams that need non-Rust toolchains or a stable build pipeline: the wasm-bindgen CLI and the crate must have exactly matching schema versions, so the CLI has to be pinned with the crate.

## How it is fast

There is no virtual DOM, no reactive graph and no diff: the code keeps a Vec of rows holding the row element and its label text node, clones a pre-parsed &lt;tr&gt; template, mutates only the nodes it knows changed and uses one delegated click listener on #main. wasm-bindgen's 'only pay for what you use' glue keeps the bundle small (29.6 kB wasm plus 15.9 kB JS in the measured build, 14.5 kB compressed in the suite). The speed over React comes from doing the minimal DOM work by hand, not from Wasm compute; each DOM call still crosses a JS shim.

## Compared with alternatives

Pick raw wasm-bindgen plus web-sys over Leptos (1.171x its time), rust-dominator (1.166x), Dioxus (1.195x) or Yew (1.401x) when one hot view justifies hand-written DOM code; Silkenweb (1.065x) comes closest among the keyed Rust frameworks if you want a framework at near-raw speed (derived from page data). The non-keyed Kobold and Delorean entries post lower times but reuse DOM nodes, so they are not like-for-like.

## Integration

| | |
|---|---|
| **Form** | crate (wasm-bindgen, web-sys, js-sys) plus the wasm-bindgen-cli post-processor, usually run by Trunk or wasm-pack |
| **Dependencies** | wasm-bindgen-macro and wasm-bindgen-shared (pulled in by the crate); web-sys with one cargo feature per Web API type used (the benchmark enables Document, DomTokenList, Element, Event, EventTarget, HtmlElement, Node, Window); js-sys for Math.random |
| **Minimum toolchain** | Library MSRV Rust 1.81 and CLI MSRV 1.86 as of 0.2.129 (README MSRV table); the measured bundle was built with rustc 1.69.0-nightly (2023-02-03) and wasm-bindgen 0.2.84 |
| **Platforms** | wasm32-unknown-unknown in browsers (Chrome, Firefox, Safari) and Node.js; experimental wasm32-unknown-emscripten support in 0.2.129 |
| **Thread safety** | JsValue and web-sys handles are !Send and !Sync and live on one JS thread; threads need the experimental atomics build with a shared WebAssembly.Memory (CHANGELOG) |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured bundle is a 2023 artifact checked into the suite: its wasm producers section records rustc 1.69.0-nightly (658fad6c5 2023-02-03), wasm-bindgen 0.2.84 (cea8cc3d2) and walrus 0.19.0, so a nightly compiler, and its JS glue uses the old heap-array object table, not the externref glue that current toolchains emit by default (reference types on by default since Rust 1.82, per the guide). Current wasm-bindgen 0.2.129 output is unmeasured. The bundle does match the checked-in src/lib.rs (same label word lists, row template and the imported DOM calls the source uses).
- Part of the 6% gap to vanillajs-keyed is implementation choice, not Wasm overhead: vanilla detaches the empty tbody before bulk-appending rows and stores the id as an expando property, while the Rust code appends into the live tbody and calls setAttribute('data-id') on every row and crosses into JS for Math.random three times per row.
- The 1.71x geometric-mean win over React leans on React hooks' slow swap rows (89.7 ms, 8.2x vanilla); without swap the Rust code takes 0.706x React's time and create 1,000 rows is a near tie (22.4 vs 23.6 ms) (derived from page data).
- wasm-bindgen-cli must match the crate's schema version exactly or it aborts with 'it looks like the Rust project used to create this Wasm file was linked against version of wasm-bindgen that uses a different bindgen format than this binary'; pin both together (Trunk and wasm-pack download a matching CLI).

## Known shortcomings

- The suite's own hand-written wasm-bindgen implementation, not a project claim; 2023 toolchain (0.2.84, latest 0.2.129); 1.064x vanilla JavaScript's time, beats Solid and Svelte; preliminary snapshot, rustc unstated. Filed under wasm-libraries-and-apps.
- The suite's checked-in bundle's producers section records rustc 1.69.0-nightly (658fad6c5, 2023-02-03), wasm-bindgen 0.2.84 (cea8cc3d2) and walrus 0.19.0, so a nightly compiler with the old heap-array glue and no externref; current 0.2.129 is unmeasured; the bundle matches src/lib.rs. Part of the 1.064x gap to vanillajs is implementation choice (per-row setAttribute, no tbody detach). No invalid evidence; Silkenweb 1.065x, Leptos 1.171x and Yew 1.401x its time (derived).

## Caveats and trade-offs

Independent public suite (krausest/js-framework-benchmark) and the snapshot states CPU, OS and browser, but results.ts at HEAD is a development snapshot (App.tsx: 'These results are preliminary and may mix browser versions or run counts'), and the measured Wasm is a prebuilt bundle checked into the suite ('build-prod' is a no-op; 'the generated javascript ... is already provided') whose rustc version is not stated, so tier B not A. The measured code is the suite's own hand-written Rust using wasm-bindgen and web-sys directly (suite note #772 'Implementation uses manual DOM manipulations', like vanillajs-keyed), not a library claim by the wasm-bindgen project, and it was built with a 2023 toolchain (wasm-bindgen 0.2.84 requested; crates.io's latest is 0.2.129). The wasm-bindgen README only promises 'only pay for what you use' and a future 'even-faster-than-JavaScript DOM access' via the Web IDL bindings proposal. Not faster than hand-written JavaScript: the geometric mean is 1.064x vanillajs-keyed's time (derived from page data). It does beat the leading JS frameworks: geometric-mean slowdown versus the per-benchmark best keyed median is 1.114 against Solid 1.9.3 keyed 1.156, Svelte 5.42.1 keyed 1.240 and vanillajs-keyed 1.046, rank 24 of 196 keyed implementations with full CPU results (derived from page data). The win over React is concentrated in swap rows (React hooks 89.7 ms, itself 8.2x vanillajs's 11.0 ms, vs 11.6 ms here); excluding swap the geometric mean is 0.706x React's time; create 1,000 rows is 0.95x (derived from page data). The suite also flags note #1139 ('Implementation doesn't pass strict CSP'). Ratios are unweighted geometric means of medians recomputed from the raw results.ts runs, not the site's weighted score. Useful as a near-upper bound for Rust/Wasm DOM work: 1.06x of vanilla JS keyed. [retier] Independent public suite (krausest/js-framework-benchmark) whose App.tsx names the hardware but labels the run a development snapshot; the measured Wasm is a prebuilt 2023 bundle checked into the suite (build-prod is a no-op) built with a nightly rustc 1.69.0 and wasm-bindgen 0.2.84, so B not A. The measured code is the suite's own hand-written Rust using wasm-bindgen and web-sys directly (not a framework), matching src/lib.rs. Part of the 1.064x gap to vanillajs-keyed is implementation choice rather than Wasm overhead: vanilla detaches the empty tbody before bulk-appending rows and stores the id as an expando property, while the Rust code appends into the live tbody, calls setAttribute('data-id') on every row and crosses into JS for Math.random three times per row. The 1.71x geometric-mean win over React leans on React hooks' slow swap rows (89.7 ms); without swap the Rust code takes 0.706x React's time and create 1,000 rows is a near tie (22.4 vs 23.6 ms) (derived from page data). Silkenweb takes 1.065x, Leptos 1.171x and Yew 1.401x its time (derived). wasm-bindgen-cli must match the crate's schema version exactly or it aborts.

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 14.5 vs React 51.4 (suite units, presumably kB), first paint 73.9 vs 226.6 ms, run memory 2.87 vs 4.37 MB, ready memory 1.72 vs 1.19 MB. It is the thin-glue baseline for the Rust frameworks above; every DOM call still crosses the JS/Wasm boundary.

## Maintenance

Very active (last commit 2026-10-10, release 0.2.129 on 2026-09-25, 9.2k stars, about 578 million crates.io downloads, now under the wasm-bindgen GitHub organisation after the rustwasm working group), dual Apache-2.0/MIT and the default Rust/JS binding layer; the benchmark number reflects a 2023 nightly-built bundle, not the current release.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent third-party suite (krausest/js-framework-benchmark, raw per-run data in webdriver-ts-results/src/results.ts) measures wasm-bindgen-v0.2.84-keyed next to react-hooks-v19.2.0-keyed and vanillajs-keyed; I recomputed every number in the record exactly (geomean 0.584x React, 1.064x vanillajs; swap 11.6 vs 89.7 ms; create 22.4 vs 23.6 ms; create 10k 234.7 vs 401.0 ms). CPU model is stated in App.tsx, but the snapshot is labelled preliminary and the measured bundle was prebuilt in 2023 with no Cargo.lock and unstated rustc version, so B not A.
- **Verifier notes:** All claimed numbers reproduce exactly from results.ts; the record's caveat that it is 'not faster than the best JavaScript entries (Solid 1.34, Svelte 1.44 ... against 1.29)' was misleading, since by its own figures (best pooled over keyed and non-keyed) and by keyed-only figures (1.114 vs Solid 1.156, Svelte 1.240) it beats Solid and Svelte and trails only vanilla-style entries; caveats rewritten. Hardware field corrected from App.tsx (MacBook Pro 14 M4 14/20 cores, 48 GB, OSX 26.6.2, Chrome 154.0.8037.98). Shortcomings: benchmark's own hand-written code, not a project claim; 2023 toolchain (0.2.84 vs current 0.2.129); slower than vanilla JS (1.064x); win over React mostly from React's slow swap.
- **Fields the verifier corrected:** `hardware`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-102 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/Trunk.toml>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/keyed/wasm-bindgen>
  - <https://github.com/wasm-bindgen/wasm-bindgen>
  - <https://github.com/wasm-bindgen/wasm-bindgen/commits>
  - <https://crates.io/api/v1/crates/wasm-bindgen>
- **Sources the enricher read:**
  - <https://github.com/wasm-bindgen/wasm-bindgen>
  - <https://github.com/wasm-bindgen/wasm-bindgen/commits/main>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/guide/src/reference/cli.md>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/guide/src/reference/reference-types.md>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/guide/src/web-sys/index.md>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/crates/cli-support/src/lib.rs>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/crates/cli-support/src/decode.rs>
  - <https://raw.githubusercontent.com/wasm-bindgen/wasm-bindgen/HEAD/crates/cli-support/src/wit/mod.rs>
  - <https://github.com/wasm-bindgen/wasm-bindgen/issues?q=is%3Aissue%20performance%20DOM%20slow>
  - <https://github.com/wasm-bindgen/wasm-bindgen/issues/1185>
  - <https://crates.io/api/v1/crates/wasm-bindgen>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/Trunk.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/src/lib.rs>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/keyed/wasm-bindgen/bundled-dist>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/bundled-dist/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/bundled-dist/js-framework-benchmark-wasm-bindgen-c09c5ae7ae721ce5.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/wasm-bindgen/bundled-dist/js-framework-benchmark-wasm-bindgen-c09c5ae7ae721ce5_bg.wasm>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/keyed/vanillajs/src/Main.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wasm-bindgen/wasm-bindgen`) · [data/wave13/enrich/raw/github_com_wasm_bindgen_wasm_bindgen.json](../../../data/wave13/enrich/raw/github_com_wasm_bindgen_wasm_bindgen.json) (enrichment confidence 0.8)

</details>
