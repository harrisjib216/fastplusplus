# Kobold

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟡 stale

> Rust/Wasm UI framework with compile-time DOM templates; in js-framework-benchmark, non-keyed, near vanilla-JS speed and 0.53x keyed React's time.

| | |
|---|---|
| **Beats** | React 19.2 hooks (react-hooks-v19.2.0-keyed, JavaScript in Chrome/V8) in krausest/js-framework-benchmark; also compared with vanilla JavaScript |
| **Claimed result** | README: 'High performance and consistently the lowest Wasm footprint in the Rust ecosystem' (no number). Suite data, like-for-like non-keyed (derived from page data, unweighted geometric mean of the medians of the total duration over the 9 CPU benchmarks in results.ts): 0.967x the time of inferno-v8.2.2-non-keyed, 0.905x of svelte-classic-v5.13.0-non-keyed, 1.033x of vanillajs-non-keyed (slower than hand-written JS); rank 8 of 67 non-keyed entries. Cross-mode against keyed React 19.2 hooks (the suite has no non-keyed React entry, and keyed vs non-keyed results are kept in separate tables by the suite): 0.534x React's time (about 1.87x faster, derived from page data); swap 1,000 rows 7.9 ms vs 89.7 ms; create 1,000 rows 22.3 ms vs 23.6 ms; create 10,000 rows 240.1 ms vs 401.0 ms; replace all rows 9.5 ms vs 30.2 ms (non-keyed DOM reuse); remove row 15.9 ms vs 11.3 ms (slower). |
| **Workload** | krausest/js-framework-benchmark: nine WebDriver-driven Chrome benchmarks on a 1,000/10,000-row table (create, replace all, partial update, select, swap, remove, create 10k, append, clear), median of repeated runs of the total (script plus paint) duration. |
| **Metric** | latency |
| **Hardware** | MacBook Pro 14, Apple M4 (14/20 cores, 48 GB), OSX 26.6.2, Chrome 154.0.8037.98 arm64 (suite App.tsx for the Chrome 154 snapshot, which it labels a 'Development snapshot' that 'may mix browser versions or run counts') |
| **Compiler and flags** | Rust release profile: opt-level=3, lto=true, codegen-units=1, panic=abort; wasm-pack release, wasm-opt -O4 (frameworks/non-keyed/kobold/Cargo.toml). |
| **Adoption** | 399 stars |
| **Last commit** | 2024-05-05 |
| **Links** | [repository](https://github.com/maciejhirsz/kobold) · [benchmark](https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts) |

## Verdict

I reproduced these from results.ts in krausest/js-framework-benchmark's Chrome 154.0.8037.98 development snapshot (MacBook Pro 14, Apple M4, OSX 26.6.2 per App.tsx). Taking the unweighted geometric mean of the nine median total durations, kobold-v0.9.1-non-keyed needs 0.534x the time of keyed react-hooks-v19.2.0, a cross-mode comparison, and 0.967x Inferno non-keyed and 1.033x vanillajs-non-keyed, ranking 8th of 67 non-keyed entries. The gain over React comes from swap rows (7.9 vs 89.7 ms), replace all rows (9.5 vs 30.2 ms, helped both by non-keyed reuse and by the skipped stale labels) and create 10,000 rows (240.1 vs 401.0 ms).

## Use it when

- Rust frontends where download size matters most: in the suite the bundle is 9.7 kB compressed, the smallest of the 23 Rust entries (next is the hand-written wasm-bindgen entry at 14.5 kB; Leptos 48.8, Dioxus 114.9). First paint is 70.8 ms vs 226.6 ms for React hooks.
- Tables or lists updated in place by position, where non-keyed DOM reuse is acceptable. Create 1,000, partial update, select, swap and append are all within about 10% of vanillajs-non-keyed.
- Small widgets embedded in an existing page, where compile-time checks of templates and component props (rust-analyzer can rename props inside `view!`) are worth more than an ecosystem.
- Apps with simple local state, where re-running a component and doing a typed diff on every change is cheap.

## Skip it when

- When list items need stable identity (focus, animations, per-item component state): Kobold diffs lists by position only, and the suite has no keyed Kobold entry. Remove one row is 15.9 ms against 11.3 ms for React hooks.
- Lists of `VString` labels that are rebuilt: an unfixed diff bug can leave stale text on screen (see gotchas).
- When you need SSR, hydration, async data or a maintained ecosystem. On SSR the maintainer said it was 'not on the roadmap' and 'a major undertaking (like v2.0)' (issue #48), and the router exists only on unreleased master. The 1.0 tracking issue (#74) carries a 2024 edit that the release plan 'aged like milk'.
- Pages with a strict Content-Security-Policy: the suite flags the implementation with note 1139, and events depend on a global `window.koboldCallback` set by an inline module script.
- Memory-tight pages: ready memory is 1.72 MB and run memory 3.07 MB, against 0.56 and 1.77 MB for vanillajs-non-keyed. The wasm runtime has a fixed cost.

## How it is fast

There is no virtual DOM. The `view!` macro compiles each template's static elements into a generated JavaScript constructor imported through wasm-bindgen, so one benchmark row is a single JS call that creates the tr and its four tds; only the dynamic parts are passed in (class string, id and label text nodes, two handlers). Each dynamic expression keeps a typed memo: the value for integers, a String copy for &str, version plus pointer for `VString`, or a pointer for `Ref`. An update writes `textContent` only when the memo differs. Event listeners do not allocate: a JS closure calls the exported `koboldCallback` with pointers to the Rust closure and its Hook. Lists diff by position (non-keyed) over a paged `PageList` that never reallocates, and the small runtime yields a 9.7 kB compressed bundle.

## Compared with alternatives

Delorean is the only other non-keyed Rust entry. It takes 0.977x Kobold's time but ships 36.1 kB compressed against Kobold's 9.7 kB (derived from page data). Against keyed Leptos, Sycamore and Dioxus, Kobold's bundle is 4.9-12x smaller and its first paint 3.0-7.6x earlier (derived from page data), but it has no keyed lists, no SSR and no maintenance. Pick it for tiny embedded widgets where bundle size dominates; otherwise use Leptos or Sycamore.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wasm-bindgen, wasm-bindgen-futures, web-sys, itoa, console_error_panic_hook, kobold_macros; optional rlsf (TLSF allocator) and serde; build for wasm32-unknown-unknown with trunk or wasm-pack |
| **Minimum toolchain** | No rust-version is declared; edition 2021. The suite's bundle was built with rustc 1.69.0, wasm-bindgen 0.2.86 and walrus 0.19.0 (read from the shipped wasm's producers section). |
| **Platforms** | Browsers with WebAssembly (wasm32-unknown-unknown); there is no native or server renderer |
| **Thread safety** | Single-threaded on the browser main thread. State sits in a cell that throws 'Cyclic state borrowing' on re-entrant borrow. Nothing else is documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness bug behind the replace-all-rows number. The `VString` diff memo is `(ver << 32) | heap pointer`. When 'run' replaces 1,000 existing rows, the old labels are freed and the new ones (version 0) often land at the same addresses, so those rows count as unchanged and keep their old label text. I ran the suite's shipped wasm (bundled-dist/js-framework-benchmark-kobold_bg.wasm) in Node against a fake DOM I wrote; the downloaded JS glue was not executed. After the 5 warmup runs, the measured sixth 'run' left 5 to 185 of 1,000 labels stale across 9 RNG seeds, and the first row was stale every time. The suite's replace check reads only the first row's id cell, so the run passes. The 9.5 ms replace row therefore skips some label writes; the effect on the nine-benchmark geometric mean is about 1% at most. `into_memo` is unchanged on master. Create, update every 10th row, swap, remove, select, append and create 10,000 all rendered correctly in the same simulation.
- The benchmark bundle is prebuilt from crates.io 0.9.1 (crate VCS sha 6ffab77, May 2023) and `build-prod` is a no-op. The documented rebuild path, `build-prod-force`, calls a nonexistent `dep:rs` script (the real name is `deps:rs`), so it fails at its first step.
- Events need a global `koboldCallback`. Trunk users must add the pattern_script from the docs; without it, 0.9.1 only logs a console.error and clicks do nothing. Conditional `view!` branches need `#[component(auto_branch)]`, otherwise `if`/`match` arms are different types and do not compile.
- The record says the hardware is not stated, but the suite's App.tsx gives it for this snapshot: MacBook Pro 14, Apple M4 (14/20 cores, 48 GB), OSX 26.6.2, Chrome 154.0.8037.98 arm64. App.tsx also labels the results a 'Development snapshot' that 'may mix browser versions or run counts'.

## Known shortcomings

- The 1.87x over React compares non-keyed Kobold with keyed React (the krausest suite keeps those tables separate); like-for-like it takes 0.967x Inferno non-keyed's time and 1.033x vanillajs-non-keyed's (slower than vanilla JavaScript); prebuilt bundle from 2023; no CPU model. UI framework, filed under wasm-libraries-and-apps. Stale since 2024-05-05.
- Correctness bug behind the replace-all-rows row: the VString diff memo is (ver &lt;&lt; 32) | heap pointer, and replaced labels reuse freed addresses, so rows look unchanged and keep their old text; running the shipped wasm in Node with a fake DOM (glue not executed), the measured sixth 'run' left 5-185 of 1,000 labels stale over 9 seeds with row 1 always stale, while the suite checks only row 1's id; geomean effect at most about 1%; bug still on master. Record correction: App.tsx states the hardware (MacBook Pro 14 M4, OSX 26.6.2, Chrome 154.0.8037.98) but labels the results a 'Development snapshot'. The bundle was built with rustc 1.69.0 and wasm-bindgen 0.2.86; the footprint claim holds (9.7 kB compressed, smallest of 23 Rust entries).

## Caveats and trade-offs

The headline 1.87x over React is a cross-mode comparison: Kobold is a NON-KEYED implementation (reuses DOM nodes) measured against keyed React 19.2 hooks; the suite keeps keyed and non-keyed results in separate tables and has no non-keyed React entry. Non-keyed DOM reuse explains the 0.31x replace-all-rows ratio; remove-one-row is 1.41x slower than React. Like-for-like, Kobold is only 0.967x Inferno non-keyed's time and 1.033x vanillajs-non-keyed's time (derived from page data), i.e. not faster than hand-written JavaScript. Independent public suite but the CPU model and Chrome flags for the Chrome 154 snapshot are not stated (releases.json labels Chrome 144-146 'macOS' and gives no note for 148-154; the README says the runner was switched to /snap/bin/chromium on Linux in July 2026), so tier B not A. The Wasm bundle is checked in prebuilt ('build-prod is a no-op, the generated javascript is already provided'); it was last rebuilt on 2023-05-26 ('Update kobold to 0.9.1', 'Built'), which is the latest crates.io release, but the repo's master has commits after it (to 2024-05-05). The suite's build-prod-force script calls 'dep:rs' while the script is named 'deps:rs', so the documented rebuild-from-source path is broken. Carries suite note #1139 (does not pass strict CSP). Ratios are the verifier's own unweighted geometric means from the raw results.ts, not the site's weighted score. Repo has not had a commit since 2024-05-05 (stale). [retier] The headline 1.87x over React is a cross-mode comparison: Kobold is a NON-KEYED implementation measured against keyed React 19.2 hooks; like-for-like it is 0.967x Inferno non-keyed's time and 1.033x vanillajs-non-keyed's time (derived from page data), i.e. not faster than hand-written JavaScript. Correctness bug behind the replace-all-rows number: the VString diff memo is (ver &lt;&lt; 32) | heap pointer, and when 'run' replaces 1,000 rows the freed labels' addresses are reused by the new ones (version 0), so those rows count as unchanged and keep their old text; running the suite's shipped wasm (bundled-dist, crates.io 0.9.1) in Node against a fake DOM, the measured sixth 'run' left 5-185 of 1,000 labels stale over 9 seeds with row 1 always stale, while the suite checks only row 1's id; the effect on the geometric mean is at most about 1%, but the 0.31x replace-all-rows ratio comes from a path that skips label updates; the bug is still on master. The bundle is prebuilt from 0.9.1 (rustc 1.69.0, wasm-bindgen 0.2.86; build-prod is a no-op and build-prod-force calls a nonexistent script). Hardware per App.tsx: MacBook Pro 14 M4, Chrome 154.0.8037.98, labelled a development snapshot. The footprint claim holds: 9.7 kB compressed, smallest of 23 Rust entries. Events need a global koboldCallback; conditional view! branches need #[component(auto_branch)].

Rust/Wasm implementation drives the DOM through wasm-bindgen glue; suite rows for this build: compressed size 9.7 vs React 51.4 (suite units, presumably kB), first paint 70.8 vs 226.6 ms, run memory 3.07 vs 4.37 MB, ready memory 1.72 vs 1.19 MB. Non-keyed list diffing semantics (DOM nodes are reused by position); README highlights lowest Wasm footprint in the Rust ecosystem.

## Maintenance

Stale: last commit 2024-05-05, last crates.io release 0.9.1 on 2023-05-26, and master's 0.10.0 was never published; 398 stars, 6 open issues. It is MPL-2.0 (file-level copyleft) and small enough to vendor, but it carries an unfixed VString stale-text bug that the suite's replace-all-rows check does not catch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** Well-known independent suite (krausest/js-framework-benchmark): raw run arrays in webdriver-ts-results/src/results.ts (Chrome 154 results commit 2026-10-04) contain kobold-v0.9.1-non-keyed and react-hooks-v19.2.0-keyed, implementation code and Cargo release profile are public in frameworks/non-keyed/kobold, but no CPU model or Chrome flags are stated for this snapshot, so B not A.
- **Retiered** B to C: Enricher: a VString diff-memo bug (version plus reused heap pointer) makes replaced rows look unchanged, so the measured 'run' rows leave 5-185 of 1,000 labels stale (reproduced on the shipped wasm; bug still on master) and the replace-rows numbers come from a path that skips work; hardware is now known from App.tsx but the suite labels the snapshot a development run. Numbers measured on code with a hot-path correctness bug (uniwidth precedent): B to C.
- **Verifier notes:** All numbers in the record reproduce exactly from results.ts (medians and geometric means recomputed). Downgraded for an overstated headline: the 1.87x-over-React ratio pits non-keyed Kobold against keyed React, a comparison the suite itself does not make; like-for-like it is about 3% faster than Inferno non-keyed and 3% slower than vanilla JS non-keyed. Tier stays B; metadata (MPL-2.0, 399 stars, last commit 2024-05-05, stale, not a fork) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `hardware`
- **Shortcomings recorded by:** verifier batch-101 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/frameworks/non-keyed/kobold>
  - <https://github.com/krausest/js-framework-benchmark/commits/master/webdriver-ts-results/src/results.ts>
  - <https://github.com/maciejhirsz/kobold>
  - <https://github.com/maciejhirsz/kobold/commits>
  - <https://crates.io/api/v1/crates/kobold>
- **Sources the enricher read:**
  - <https://github.com/maciejhirsz/kobold>
  - <https://github.com/maciejhirsz/kobold/commits/master>
  - <https://github.com/maciejhirsz/kobold/tree/master/crates/kobold/src>
  - <https://github.com/maciejhirsz/kobold/issues?q=is%3Aissue>
  - <https://github.com/maciejhirsz/kobold/issues/48>
  - <https://github.com/maciejhirsz/kobold/issues/74>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/README.md>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/crates/kobold/Cargo.toml>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/crates/kobold/src/lib.rs>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/crates/kobold/src/diff.rs>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/crates/kobold/src/diff/vstring.rs>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/crates/kobold/src/list.rs>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/crates/kobold/src/stateful.rs>
  - <https://raw.githubusercontent.com/maciejhirsz/kobold/HEAD/crates/kobold/src/value.rs>
  - <https://crates.io/api/v1/crates/kobold>
  - <https://static.crates.io/crates/kobold/kobold-0.9.1.crate>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/frameworks/non-keyed/kobold/bundled-dist>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/Cargo.toml>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/package.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/README.md>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/src/lib.rs>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/bundled-dist/index.html>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/bundled-dist/js-framework-benchmark-kobold.js>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/frameworks/non-keyed/kobold/bundled-dist/js-framework-benchmark-kobold_bg.wasm>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/results.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/App.tsx>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/releases.json>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts-results/src/helpers/issues.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts/src/benchmarksCommon.ts>
  - <https://raw.githubusercontent.com/krausest/js-framework-benchmark/HEAD/webdriver-ts/src/benchmarksPuppeteer.ts>
  - <https://github.com/krausest/js-framework-benchmark/tree/master/webdriver-ts/src>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/maciejhirsz/kobold`) · [data/wave13/enrich/raw/github_com_maciejhirsz_kobold.json](../../../data/wave13/enrich/raw/github_com_maciejhirsz_kobold.json) (enrichment confidence 0.8)

</details>
