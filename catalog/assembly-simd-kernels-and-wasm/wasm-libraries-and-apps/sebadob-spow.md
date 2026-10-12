# spow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust (server crate, browser WASM and JS-only solvers)` · `Apache-2.0` · 🟢 active

> Self-hosted Hashcash-style proof-of-work captcha in Rust with a browser WASM solver, about 20x faster than its own async-WebCrypto JS solver.

| | |
|---|---|
| **Beats** | the JS-only browser solver shipped in prebuilt/browser, and optimised native Rust (the wasm build is slower than native) |
| **Claimed result** | README: the wasm version 'is up to \~20 times faster than JS only' and needs 'roughly 2.5 - 3 times the amount of time' of optimised native Rust ('first tests'). Source of the ratios (a comment in examples/svelte-wasm/src/routes/+page.svelte, December 2023, one solve of one difficulty-20 challenge, counter 230289, unnamed machine and browser): backend about 250 ms, WASM about 680 ms, JS about 13,600 ms; the JS solver awaits crypto.subtle.digest per candidate, so the 20x is WebCrypto call overhead, not a JS hashing comparison. |
| **Workload** | Time to solve a Hashcash-style proof of work (the README says 'Hashcat'): SHA-256 over challenge plus counter until the hash has `difficulty` leading zero bits (difficulty 10-99, default 20), in the browser with the prebuilt WASM solver vs the prebuilt JS-only solver (prebuilt/browser/js/spowJs.js), and vs native Rust (src/pow.rs, sha2 crate). |
| **Metric** | latency |
| **Adoption** | 43 stars; crates.io spow |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/sebadob/spow) · [benchmark](https://github.com/sebadob/spow) |

## Verdict

One author run on an unnamed machine and browser, difficulty-20 challenge solved at counter 230289: optimised native Rust (sha2 crate) about 250 ms, the prebuilt WASM solver about 680 ms (2.7x native) and the async WebCrypto JS solver about 13,600 ms (20x the WASM time); no compiler flags, hardware, browser version or repeat count are given, and the native Criterion bench covers only Pow::work at difficulty 14 and Pow::validate.

## Use it when

- Self-hosted bot friction on login, registration or contact forms where you want no third-party captcha service and can add a Rust (axum, leptos) or Node backend.
- Browser clients that can load WASM: use the WASM solver at the default difficulty 20 and run it in a Web Worker (examples/svelte-wasm/src/lib/pow.ts) so the synchronous call does not freeze the page.
- Rust mobile or desktop clients, which can call `Pow::work` natively and solve the same challenge 2.5-3x faster than browser WASM (author's single run).
- Per-action difficulty tuning: validation cost is one SHA-256 regardless of difficulty, so heavier challenges for registration and lighter ones for cheap actions cost the server nothing extra.

## Skip it when

- As real protection against a motivated attacker: the challenge is plain SHA-256 leading-zero search, which native SHA-NI or GPU code solves orders of magnitude faster than browser WASM; it only raises cost for naive bots.
- JS-only clients at difficulty 20: the author's own example machine needed about 13.6 s for a lucky challenge (230,290 hashes), against about 1.05 million expected hashes on average; the code comment says JS needs a much lower difficulty.
- When you need replay protection without your own cache: a solved PoW validates again until it expires; the docs only advise a short validity.
- Low-end phones with a fixed latency budget: solve time is a geometric random variable (lucky and unlucky challenges differ by large factors) and the README gives no device data; the maintainer suggests measuring 100 challenges on your slowest target device (issue #6).

## How it is fast

There is no special algorithm: the WASM solver is the RustCrypto `sha2` software SHA-256 compiled to wasm32 (wasm-builder profile opt-level "s", LTO, one codegen unit) running a tight synchronous loop, while the JS baseline it beats awaits one `crypto.subtle.digest('SHA-256')` promise per candidate and allocates a new TextEncoder and ArrayBuffer slice each iteration. The 20x therefore comes from removing per-hash async WebCrypto round trips, not from faster hashing. Neither solver caches the SHA-256 midstate of the constant 64-byte challenge prefix, so each candidate costs two compression blocks where one would do.

## Compared with alternatives

Pick spow when you need a whole self-hosted PoW captcha protocol (signed challenge, expiry, difficulty, server validation, browser solver); if you only need fast SHA-256 or other hashes in the browser, hash-wasm (SHA-256 426 MB/s vs noble-hashes 110 MB/s at 1 MB) or awasm-noble are general-purpose and benchmarked.

## Integration

| | |
|---|---|
| **Form** | crate (spow 0.7.0, features `server` and `client`) plus prebuilt wasm-bindgen modules in prebuilt/browser/wasm and prebuilt/server/wasm and a plain ES module in prebuilt/browser/js |
| **Dependencies** | nom 8 and sha2 0.11 always; base64 0.23, chrono 0.4, serde, thiserror 2 and getrandom 0.4 with `server`; the browser WASM glue imports the .wasm as an ES module, so it needs a bundler with WASM support (the example uses vite-plugin-wasm and vite-plugin-top-level-await) |
| **Minimum toolchain** | Rust 1.85.1 (edition 2024); wasm32 builds need `--cfg getrandom_backend="wasm_js"` in .cargo/config.toml |
| **Platforms** | any Rust target, wasm32-unknown-unknown; browsers with WebAssembly for the WASM solver, any browser with WebCrypto (secure context) for the JS solver |
| **Thread safety** | Pow::work and Pow::validate are pure functions; the secret lives in a OnceLock, so concurrent validation is safe; the browser WASM call is synchronous and blocks its thread |
| **Drop-in for the baseline** | partial: pow_work_wasm takes and returns the same challenge strings as powWorkJs, but it is synchronous (block a Web Worker, not the page) and returns undefined silently on bad input where powWorkJs also logs an error |

## Gotchas

- Measurement provenance: the README ratios come from one solve of one difficulty-20 challenge on an unnamed machine, recorded in a comment in examples/svelte-wasm/src/routes/+page.svelte (backend \~250 ms, WASM \~680 ms, JS \~13,600 ms, counter 230289, December 2023); timing is a single Date difference, the WASM run goes first and cold, and no browser is named.
- Harness flaw behind the 20x: spowJs.js awaits crypto.subtle.digest once per candidate (about 59 us per hash in that run, derived from page data, against about 2.95 us for WASM), so the baseline is dominated by async WebCrypto overhead; a synchronous pure-JS SHA-256 loop was never compared and would likely close much of the gap.
- The 2.5-3x native-vs-WASM ratio is stale: it was measured in December 2023, when the sha2 `asm` feature was still on by default (made opt-in in v0.3.0, removed in v0.7.0 with the move to sha2 0.11), and the WASM is built at opt-level "s" for size; the native Criterion bench (benches/main.rs) never runs the WASM or JS solvers.
- Small correctness and security nits: validate_difficulty uses the range 10..99, so difficulty 99 is rejected although the README and the bin target allow 10-99; the challenge MAC is compared with a non-constant-time string ==; a second Pow::init call is silently ignored; the README calls the scheme 'Hashcat' where Hashcash is meant.

## Known shortcomings

- "About 20x vs JS" is a ratio from "first tests" with no data; the JavaScript baseline awaits one crypto.subtle.digest call per candidate hash, so it is weak; benches/main.rs is native-only Criterion.
- The README ratios trace to one December 2023 run in a code comment (examples/svelte-wasm/src/routes/+page.svelte: native about 250 ms, WASM about 680 ms, JS about 13,600 ms, difficulty 20, counter 230289, unnamed machine), a single Date timing with the WASM run first and cold. Harness flaw: the JS baseline awaits one crypto.subtle.digest per hash (about 59 us per hash vs about 2.95 us for WASM, derived), so the 20x is mostly async WebCrypto overhead and no synchronous pure-JS SHA-256 loop was compared. The 2.5-3x native ratio is stale (measured while the sha2 asm feature was default; opt-in in v0.3.0, removed in v0.7.0); the WASM is built at opt-level 's'; no solver caches the SHA-256 midstate. Small bugs: validate_difficulty's 10..99 range rejects 99; the challenge MAC is compared non-constant-time; replay is allowed until expiry.

## Caveats and trade-offs

The README gives ratios only ('first tests'), with no table, hardware, browser, difficulty or sample count. benches/main.rs is a native-only Criterion bench (Pow::work on five difficulty-14 challenges, Pow::validate) and the bin target (src/main.rs, 'cargo run --features server --release 20 100') prints native percentiles; neither measures WASM or JS. The JS baseline is weak: spowJs.js awaits crypto.subtle.digest('SHA-256') once per candidate and allocates a new TextEncoder each iteration, so the \~20x mostly measures per-hash async WebCrypto/promise overhead rather than JS hashing speed; a synchronous pure-JS SHA-256 loop was not compared. The wasm build is itself 2.5-3x slower than native Rust, so it beats only the JS baseline. [retier] The README gives ratios only ('first tests') with no table, hardware, browser, difficulty or sample count; the only provenance is a code comment recording one solve of one difficulty-20 challenge in December 2023, timed with a single Date difference with the WASM run first and cold. Harness flaw: spowJs.js awaits crypto.subtle.digest('SHA-256') once per candidate and allocates a new TextEncoder each iteration (about 59 us per hash against about 2.95 us for WASM, derived from page data), so the \~20x measures per-hash async WebCrypto and promise overhead; a synchronous pure-JS SHA-256 loop was never compared. The 2.5-3x native-vs-WASM ratio is stale: measured while the sha2 'asm' feature was still on by default (opt-in in v0.3.0, removed in v0.7.0), and the WASM is built at opt-level 's' for size; benches/main.rs is a native-only Criterion bench that never runs the WASM or JS solvers; no solver caches the SHA-256 midstate (two blocks per hash where one would do). Small bugs: validate_difficulty's 10..99 range rejects 99; the challenge MAC is compared with a non-constant-time ==; a second Pow::init call is silently ignored; replay is allowed until expiry.

Solve time grows exponentially with difficulty (10-99); wasm needs a getrandom backend setting in .cargo/config.toml; server-side validation time is independent of difficulty.

## Maintenance

Active small single-maintainer project (v0.7.0 on 2026-08-25, 76 commits, 43 stars, about 32,000 crates.io downloads, 0 open issues), Apache-2.0 and a few hundred lines, so easy to vendor; its speed claim rests on one 2023 example run against a deliberately weak async JS baseline.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README ratios from 'first tests' ('up to \~20 times faster than JS only', 'roughly 2.5 - 3 times' native time) with no table, browser, hardware, difficulty or sample count; benches/main.rs is a native-only Criterion bench of Pow::work and Pow::validate and never runs the WASM or JS solvers.
- **Retiered** C to D: Enricher: the README ratios come from one December 2023 solve recorded in a code comment, with a single cold Date timing; the JS baseline awaits crypto.subtle.digest once per candidate (about 59 us per hash against about 2.95 us for WASM), so the 20x measures async WebCrypto overhead rather than JavaScript hashing (crippled baseline with no valid measurement); the 2.5-3x native ratio predates the removal of the sha2 asm feature. C to D.
- **Verifier notes:** Ratios on README confirmed verbatim; no measurement data. Main shortcoming: JS baseline awaits one async crypto.subtle.digest call per candidate hash (prebuilt/browser/js/spowJs.js), an inherently slow pattern, and the repo's Criterion bench is native-only. Metadata checked: Apache-2.0, 43 stars, last commit 2026-08-25, not a fork.
- **Fields the verifier corrected:** `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-121 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/sebadob/spow>
  - <https://github.com/sebadob/spow/commits>
  - <https://github.com/sebadob/spow/tree/main/benches>
  - <https://github.com/sebadob/spow/tree/main/prebuilt/browser>
  - <https://github.com/sebadob/spow/tree/main/prebuilt/browser/js>
  - <https://github.com/sebadob/spow/tree/main/src>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/README.md>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/benches/main.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/prebuilt/browser/js/spowJs.js>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/src/pow.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/sebadob/spow>
  - <https://github.com/sebadob/spow/commits>
  - <https://github.com/sebadob/spow/issues?q=is%3Aissue>
  - <https://github.com/sebadob/spow/issues/6>
  - <https://github.com/sebadob/spow/issues/20>
  - <https://github.com/sebadob/spow/tree/main/wasm-builder>
  - <https://github.com/sebadob/spow/tree/main/prebuilt/browser>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/README.md>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/justfile>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/benches/main.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/src/pow.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/src/wasm.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/prebuilt/browser/js/spowJs.js>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/prebuilt/browser/wasm/spow-wasm.js>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/prebuilt/browser/wasm/spow-wasm.d.ts>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/wasm-builder/Cargo.toml>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/wasm-builder/src/lib.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/wasm-builder/tests/web.rs>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/examples/svelte-wasm/src/routes/+page.svelte>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/examples/svelte-wasm/src/lib/pow.ts>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/examples/svelte-wasm/vite.config.js>
  - <https://raw.githubusercontent.com/sebadob/spow/HEAD/examples/svelte-wasm/package.json>
  - <https://crates.io/api/v1/crates/spow>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/sebadob/spow`) · [data/wave13/enrich/raw/github_com_sebadob_spow.json](../../../data/wave13/enrich/raw/github_com_sebadob_spow.json) (enrichment confidence 0.7)

</details>
