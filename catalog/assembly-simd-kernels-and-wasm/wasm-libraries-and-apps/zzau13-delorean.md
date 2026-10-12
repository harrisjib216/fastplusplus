# Delorean (Rust web framework)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🔴 abandoned

> Tiny no_std message-loop runtime for Rust/Wasm apps; its hand-written DOM benchmark matches vanilla JS, not faster.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README bullet: 'Fastest than vanillajs', linking to the suite site; the suite does not support it. Suite data, my unweighted geometric means over the 9 CPU benchmarks of median total duration from the raw run arrays in results.ts (derived from page data): versus vanillajs-non-keyed 1.010x the time (not faster); versus vanillajs-3-non-keyed 1.112x (slower); versus svelte-classic-v5.13.0-non-keyed 0.885x. Rank 7 of 67 non-keyed implementations by slowdown versus the per-benchmark best (1.138), behind vanillajs-3, mikado, deleight, solarite, vanillajs-1 and vanillajs non-keyed. Cross-mode (non-keyed versus keyed, not like-for-like): 0.522x the time of react-hooks-v19.2.0-keyed (0.649x excluding swap rows) and 0.951x vanillajs-keyed. Swap 1,000 rows 8.2 ms vs React 89.7 ms; create 1,000 rows 22.9 ms vs 23.6 ms; create 10,000 rows 237.4 ms vs 401.0 ms. |
| **Workload** | krausest/js-framework-benchmark: nine browser benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), driven by the Puppeteer benchmark driver with reduced tracing (15 runs per benchmark, 25 for select), median of the total (script plus paint) duration per benchmark. |
| **Metric** | latency |
| **Hardware** | Apple M4 (MacBook Pro 14, '14/20 cores', 48 GB RAM), macOS 26.6.2, Chrome 154.0.8037.98 (arm64), per the 'Test environment & methodology' block in webdriver-ts-results/src/App.tsx, which ships with the Chrome 154 results (results.ts commit c097071 'Chrome 154 results', 2026-10-04). The same page sets isOfficial = false and labels itself a development snapshot that 'may mix browser versions or run counts'. |
| **Compiler and flags** | Rust release profile lto=true, panic=abort (opt-level left at the default); wasm-pack through @wasm-tool/wasm-pack-plugin 0.4.2 with webpack 4.33.0 (frameworks/non-keyed/delorean). The benchmark Cargo.toml depends on the crates.io delorean 0.2.1 (published 2020-10-06), although the suite labels the entry v0.1.0 and the latest crate is 0.3.0 (2023-03-30). The bundled-dist is checked in prebuilt; the rustc and wasm-bindgen versions that built it are not stated. |
| **Adoption** | 4 stars |
| **Last commit** | 2023-03-30 |
| **Links** | [repository](https://github.com/zzau13/delorean) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

In krausest/js-framework-benchmark's Chrome 154.0.8037.98 development snapshot (Apple M4 MacBook Pro 14, macOS 26.6.2, isOfficial = false), the delorean-v0.1.0-non-keyed build (delorean 0.2.1, release lto, panic=abort) took 0.522x the time of react-hooks-v19.2.0-keyed. That is the unweighted geometric mean of the nine median total durations, which I reproduced from results.ts, and it compares non-keyed with keyed. Against like-for-like non-keyed vanilla JS it is 1.010x (vanillajs-non-keyed) and 1.112x (vanillajs-3-non-keyed), i.e. not faster; per row, create 1,000 is 22.9 vs 23.6 ms for React and create 10,000 is 237.4 vs 401.0 ms.

## Use it when

- Small Rust/Wasm widgets where you would write direct web-sys DOM updates anyway and want a minimal single-threaded message-loop skeleton (dispatch, then one render) with no framework runtime.
- Non-keyed tables and lists whose rows can be rewritten in place: the suite build ran swap rows in 8.2 ms and replace-all in 12.7 ms on an Apple M4 in Chrome 154.
- Studying how fast plain web-sys DOM code can get from Rust: in the same suite data it is level with vanillajs-non-keyed (1.010x the time) and ranks 7th of 67 non-keyed entries, the fastest Rust entry.
- no_std Wasm builds that only need alloc.

## Skip it when

- Speed over plain JavaScript: across the nine CPU benchmarks it takes 1.010x vanillajs-non-keyed's time and 1.112x vanillajs-3-non-keyed's (derived from page data), so the README's 'Fastest than vanillajs' is not supported.
- Apps that need templates, components, keyed lists, SSR or reactivity: the crate provides none, and the measured speed belongs to the hand-written DOM code you would have to write yourself.
- Bundle-size-sensitive pages: the suite build ships 36.1 kB compressed (101.1 kB uncompressed) against Kobold's 9.7 kB and Svelte 5's 6.7 kB (suite units, presumably kB); ready memory is 1.75 MB vs React's 1.19 MB.
- Anything that needs maintenance or a community: last commit 2023-03-30, 4 stars, 23 commits, about 6k all-time crates.io downloads and 19 recent ones.
- Non-Wasm targets or multi-threaded use: lib.rs has compile_error!("only compile in wasm32") for every other target, and the runtime is single-threaded by design.

## How it is fast

The speed in the suite comes from the benchmark's hand-written web-sys code, not from the crate. That code clones a prebuilt &lt;tr&gt; template with cloneNode(true) and keeps direct references to each row's id, label and delete nodes. It updates only text marked dirty in per-row and app-level u8 bitmasks, and reuses rows non-keyed: swap rewrites two rows' text, and replace-all rewrites text in place. Delete removes the row node directly. The crate itself adds only message batching (all queued messages are dispatched, then one render) through a leaked static with no reference counting or RefCell.

## Compared with alternatives

Against Kobold, the other catalogued non-keyed Rust entry, CPU time is a tie (0.978x Kobold's time, derived from page data), but Kobold ships 9.7 kB compressed against 36.1 kB and offers a real view macro, so Kobold wins. Delorean also adds little over the hand-written wasm-bindgen/web-sys entry (0.893x its time, cross-mode non-keyed vs keyed). Pick Leptos, Sycamore or rust-dominator for an actual framework; consider DeLorean only as a minimal message-loop skeleton for hand-written DOM code.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none at runtime (no_std plus alloc); build-dependency yarte_helpers \~0.15.8 (toolchain detection). The benchmark app adds wasm-bindgen, web-sys, js-sys, serde, serde_json and rand 0.7. |
| **Minimum toolchain** | Rust 1.65 per the README (edition 2021; no rust-version field in Cargo.toml); built with wasm-pack for wasm32-unknown-unknown |
| **Platforms** | wasm32 only (compile_error! on other targets since 'fix: remove native implementations', 2023-03-30); browser via wasm-bindgen |
| **Thread safety** | Single-threaded only. The context holds Cell and UnsafeCell, so the handle cannot be shared across threads; on nightly it is also marked !Send and !Sync explicitly. Re-entrancy is guarded by a ready flag, and send() during a dispatch only queues the message. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark-code bug (does not affect the measured numbers): run_n, behind Create 1,000 and Create 10,000, overwrites existing rows and only appends, never truncating. Clicking Create 1,000 after Create 10,000 therefore leaves 10,000 rows, with only the first 1,000 replaced. The suite's measured sequences (create from empty, replace 1,000 with 1,000, create 10,000 from empty) never shrink the table, so the timings stand. Also, clicking an already selected row deselects it (a toggle the other implementations do not have). The same code is in the repo at examples/js-framework-benchmark (handler.rs and app.rs identical to the suite copy).
- build.rs sets cfg(nightly) whenever a nightly compiler is detected. That turns the queue's unwrap into core::intrinsics::unreachable (undefined behaviour if it is ever None) and needs the unstable core_intrinsics and negative_impls features, so behaviour and buildability change silently with the toolchain.
- run! wraps the unsafe A::run, which must be called exactly once. The app is leaked with Box::leak and never freed, and Addr's Drop panics in release builds. The __render, __hydrate and __dispatch hooks are #[doc(hidden)] defaults that do nothing unless you override them.
- Version labels are stale: the suite calls the entry v0.1.0, its Cargo.toml pins delorean 0.2.1 (2020-10-06), and the checked-in bundled-dist was built with an unrecorded rustc and wasm-bindgen; the current 0.3.0 (2023-03-30) is unmeasured. The comparison with React is cross-mode (non-keyed vs keyed hooks): swap 8.2 vs 89.7 ms carries most of the 0.522x. The results.ts snapshot is marked unofficial (isOfficial = false).

## Known shortcomings

- Non-keyed entry compared against keyed React hooks (cross-mode); like-for-like it takes 1.010x vanillajs-non-keyed's time (not faster) and 1.112x vanillajs-3-non-keyed's; the benchmark is hand-written web-sys DOM code on a 2020 prebuilt bundle (delorean 0.2.1 labelled v0.1.0); the "fastest than vanillajs" claim is unsupported; 4 stars. UI framework, filed under wasm-libraries-and-apps.
- Benchmark-code bug that does not affect the timings: run_n never truncates, so Create 1,000 after Create 10,000 leaves 10,000 rows, and Select toggles off on a second click; the measured sequences never shrink the table. The crate is about 200 lines of message queue and the speed comes from hand-written web-sys code (1.010x vanillajs-non-keyed time; 0.978x Kobold's time at 36.1 vs 9.7 kB). build.rs on nightly swaps in an unchecked unwrap (UB if None). Abandoned since 2023-03-30.

## Caveats and trade-offs

Non-keyed implementation: the suite's README says non-keyed mode 'can be more performant, since costly DOM operations can be avoided', so the win over keyed React hooks (largest on swap rows, 8.2 vs 89.7 ms, and replace all, 0.42x) is partly a mode difference. The suite has no non-keyed React entry. Against non-keyed vanilla JS the entry is not faster (1.010x vanillajs-non-keyed, 1.112x vanillajs-3-non-keyed), so the README's 'Fastest than vanillajs' is unsupported. The benchmark code hand-writes the App trait's __render and __hydrate methods with direct web-sys DOM calls and dirty bitmasks (src/app.rs, src/row.rs), in effect manual DOM manipulation, although the suite flags it only with note 1139 ('Implementation doesn't pass strict CSP') and not with note 772; delorean itself is described on crates.io as 'A simple single thread reactor pattern for wasm', so the measured speed is mostly that of the hand-written DOM code. The prebuilt bundle was built against delorean 0.2.1 (2020) while the suite labels it v0.1.0. results.ts is shipped with a page marked as a development snapshot (isOfficial = false). Ratios are my own unweighted geometric means from the raw results.ts, not the site's weighted score. Repo last commit 2023-03-30, 4 stars; the crates.io record points at github.com/botika/delorean, apparently the same author's earlier account name. [retier] Non-keyed implementation, so the win over keyed React hooks (swap rows 8.2 vs 89.7 ms, replace all 0.42x) is partly a mode difference; the suite has no non-keyed React entry. Against non-keyed vanilla JS the entry is not faster (1.010x vanillajs-non-keyed, 1.112x vanillajs-3-non-keyed), so the README's 'Fastest than vanillajs' is unsupported; 0.978x Kobold's time at 36.1 vs 9.7 kB. The crate is about 200 lines of message queue and the speed comes from hand-written web-sys code in the benchmark entry. Benchmark-code bug that does not affect the timings: run_n never truncates (Create 1,000 after Create 10,000 leaves 10,000 rows) and Select toggles off on a second click; the measured sequences never shrink the table. build.rs on nightly swaps in an unchecked unwrap. Abandoned since 2023-03-30.

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 36.1 vs React 51.4 (suite units, presumably kB), first paint 48.6 vs 226.6 ms, run memory 3.17 vs 4.37 MB, ready memory 1.75 vs 1.19 MB. Non-keyed list semantics; tiny single-thread reactor pattern library; the GitHub page redirects from delorean-rs/delorean to zzau13/delorean.

## Maintenance

Abandoned since 2023-03-30 (4 stars, crate 0.3.0, 19 recent downloads); MIT or Apache-2.0 and only about 200 lines, so easy to vendor, but it contributes only a message queue and the speed comes from DOM code you write yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The independent krausest suite (implementation in frameworks/non-keyed/delorean) has the numbers, and my medians from results.ts reproduce the record exactly, but the headline win compares a NON-KEYED implementation with keyed React hooks, a mode the suite's README says can avoid costly DOM operations. Against the like-for-like JS baseline, vanillajs-non-keyed, the geometric mean is 1.010x (not faster). Asymmetric-baseline precedent (GStreamer B to C), so C.
- **Verifier notes:** Real third-party numbers, verified exactly, but the React comparison is non-keyed versus keyed and the like-for-like vanilla JS non-keyed baseline is as fast or faster (1.010x, 1.112x). The measured code is hand-written web-sys DOM manipulation, so little of the speed is attributable to the delorean crate. Shortcomings: cross-mode baseline, not faster than vanilla JS, manual DOM code, stale prebuilt bundle from a 2020 crate version, abandoned repo with 4 stars.
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
  - <https://github.com/zzau13/delorean>
  - <https://github.com/zzau13/delorean/commits>
  - <https://crates.io/api/v1/crates/delorean>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/non-keyed/delorean>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/index.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/app.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/row.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/handler.rs>
- **Sources the enricher read:**
  - <https://github.com/zzau13/delorean>
  - <https://github.com/zzau13/delorean/commits>
  - <https://github.com/zzau13/delorean/issues?q=is%3Aissue>
  - <https://github.com/zzau13/delorean/tree/master/examples>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/README.md>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/build.rs>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/LICENSE-APACHE>
  - https://raw.githubusercontent.com/zzau13/delorean/HEAD/CHANGELOG.md (404)
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/src/wasm.rs>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/src/queue.rs>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/examples/js-framework-benchmark/Cargo.toml>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/examples/js-framework-benchmark/src/app.rs>
  - <https://raw.githubusercontent.com/zzau13/delorean/HEAD/examples/js-framework-benchmark/src/handler.rs>
  - <https://crates.io/api/v1/crates/delorean>
  - https://crates.io/api/v1/crates/delorean/reverse_dependencies (empty response)
  - <https://crates.io/api/v1/crates/yarte>
  - <https://raw.githubusercontent.com/zzau13/yarte/HEAD/README.md>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/non-keyed/delorean>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/Cargo.toml>
  - https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/Cargo.lock (404)
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/index.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/webpack.config.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/app.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/row.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/delorean/src/handler.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/zzau13/delorean`) · [data/wave13/enrich/raw/github_com_zzau13_delorean.json](../../../data/wave13/enrich/raw/github_com_zzau13_delorean.json) (enrichment confidence 0.8)

</details>
