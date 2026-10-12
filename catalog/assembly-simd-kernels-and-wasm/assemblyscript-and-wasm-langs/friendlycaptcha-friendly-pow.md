# friendly-pow (Friendly Captcha proof-of-work solver in AssemblyScript)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `AssemblyScript` · `Friendly Captcha License (source-available)` · 🔴 abandoned

> Friendly Captcha's BLAKE2b proof-of-work solver in AssemblyScript WASM, claimed an order of magnitude faster than its own JS fallback.

| | |
|---|---|
| **Beats** | the library's own JavaScript fallback solver |
| **Claimed result** | README: 'The WASM build is an order of magnitude faster in most browsers' (no numbers given). |
| **Workload** | Proof-of-work puzzle solving in browsers: WASM build (compiled from AssemblyScript) vs JavaScript fallback for very old browsers. |
| **Metric** | throughput |
| **Compiler and flags** | AssemblyScript ^0.16.1 (package.json devDependency, an older release; custom loader to reduce bundle size); optimized build: asc src/entryWasm.ts --runtime stub -O3 --noAssert, then wasmwrap into a TypeScript module |
| **Adoption** | 212 stars; used by Friendly Captcha |
| **Last commit** | 2022-12-01 |
| **Links** | [repository](https://github.com/FriendlyCaptcha/friendly-pow) · [benchmark](https://github.com/FriendlyCaptcha/friendly-pow) |

## Verdict

The README's 'order of magnitude faster in most browsers' has no numbers. First-party figures exist only in issues and tests, never on one machine: issue #1 (2020) gives about 3M hashes/s for WASM on a powerful desktop vs 170k hashes/s as the slowest JS fallback seen and says WASM could cut solve time 5-10x on an old phone; PR #2 (Node 12.13.1) took the WASM solver from about 2.25M to 4.0M hashes/s after MaxGraey's unrolling; a test comment records 2.3M/s on a Ryzen 3900X.

## Use it when

- You are integrating or auditing Friendly Captcha v1 (friendly-challenge) and need to know which solver a client ran (diagnostics byte 0: 1 = JS fallback, 2 = WASM).
- You want a compact reference for a single-block BLAKE2b PoW inner loop in AssemblyScript, using native i64 and locals instead of 32-bit word-pair emulation.
- Browser or web-worker PoW where the input is exactly one 128-byte block and only a 4-byte counter changes per attempt.
- Studying how much a 64-bit-arithmetic hash gains from WASM over JS: the repo holds both implementations plus a 32/64-bit equivalence test (test/blake2b64.astest.ts).

## Skip it when

- As a general BLAKE2b library: the solver path assumes an unkeyed, single 128-byte block and skips buffer resets ('Danger: ... only possible because our input is exactly 128 bytes').
- When you need an OSI licence: the README states 'Friendly Captcha License; source-available only' and there is no LICENSE file at the root.
- When you need maintained tooling: last commit 2022-12-01, pinned to AssemblyScript ^0.16.1 with a hand-pruned loader, and the README warns an upgrade needs loader changes.
- Browsers or hardened modes without WebAssembly or with the JIT off: the JS fallback is the path that runs there, and it is the slow one (maintainer's slowest JS figure: 170k hashes/s).
- When you need published, reproducible speed numbers: the WASM vs JS ratio has never been measured on one machine in the repo.

## How it is fast

The WASM path (src/blake2b/blake2b64.ts) runs BLAKE2b on native i64 adds and rotr with the 16 working words held in locals, the G function unrolled for all 8 column/diagonal mixes, SIGMA read from a static memory segment, unchecked loads and --noAssert -O3. Per attempt it only resets the 8-word chain value and compresses a single final block read straight from the caller's buffer as 16 u64 loads, with no allocation. The JS fallback (src/blake2b/blake2b.ts, adapted from dcposch's CC0 blake2b.js) must emulate every 64-bit add and rotate with pairs of 32-bit words in Uint32Arrays and re-reads the 128-byte block byte by byte each attempt, which is where the WASM build's advantage comes from.

## Compared with alternatives

Pick it over long.js (also a WASM fast path behind its own JS fallback with a no-numbers 'twice as fast' claim) only if your workload is BLAKE2b proof-of-work. superfasthash and galois carry actual measured WASM-vs-JS tables (1.21x and about 9x on additions), so they are better evidence of what AssemblyScript buys; friendly-pow is the production-deployed example with no measured ratio.

## Integration

| | |
|---|---|
| **Form** | module (npm package friendly-pow 0.2.2; WASM embedded as base64 through wasmwrap) |
| **Dependencies** | none at runtime; build needs assemblyscript ^0.16.1, wasmwrap, TypeScript 3.x, as-pect and jest |
| **Minimum toolchain** | Browser or Node with WebAssembly MVP (i64, no SIMD or threads) for the WASM path; any ES5-era engine with typed arrays and DataView for the JS fallback |
| **Platforms** | any JS engine; WASM path needs WebAssembly |
| **Thread safety** | not documented; each WASM instance keeps one shared 128-byte input array, so one solver per worker (friendly-challenge runs one per Web Worker) |
| **Drop-in for the baseline** | partial — the WASM and JS solvers share one interface and are interchangeable, but the JS solver mutates the caller's buffer while the WASM solver returns views into its own linear memory |

## Gotchas

- WASM loop bound wraps: solverWasm.ts computes end = start + n in u32, so with the API default n = 4294967295 any nonzero starting counter in bytes 124-127 makes end &lt; start and the call returns an empty 'no solution' array after zero attempts. friendly-challenge is unaffected because the wrapper copies the caller's untouched buffer (counter 0) into WASM memory each call; direct callers resuming from a nonzero counter are not.
- Built with --runtime stub, so nothing is ever freed: every solve call allocates a fresh Context (including an unused 128-byte b buffer) and a result array, and __release is a no-op, so memory grows with each call in a long-lived instance. The returned solution and hash are views into WASM memory and are overwritten by the next call; copy them first.
- The JS solver checks a global ASC_TARGET (friendly-challenge sets self.ASC_TARGET = 0 before use); without it, reaching a solution throws a ReferenceError. It also writes the nonce through new DataView(input.buffer) at offset 124, ignoring byteOffset, so a subarray input gets the wrong bytes overwritten.
- The only speed evidence in the repo is test assertions: WASM must exceed 1,250,000 hashes/s ('I hit 2.3M/s on Ryzen 3900X', test/solver.astest.ts) and JS must exceed 50,000 hashes/s (test/solver.test.ts, no machine). These are pass thresholds, not measurements, and their 25x ratio is not a speedup. The 'Can solve over and over' test is degenerate: after the first call the input keeps the found nonce, so 999 of 1,000 calls succeed on their first attempt.

## Known shortcomings

- README "order of magnitude" line only, no numbers or benchmark code; source-available Friendly Captcha License, reference only.
- Enricher: no same-machine JS vs WASM measurement anywhere (issue #1: WASM about 3M hashes/s on desktop vs 170k for the slowest JS seen; PR #2 took WASM from 2.25M to 4.0M hashes/s on Node 12.13.1; the test hash-rate floors are thresholds, not measurements); the WASM end = start + n wraps u32 with the default n (zero attempts when the start counter is nonzero; the friendly-challenge wrapper resets the buffer), --runtime stub never frees memory, the JS fallback needs a global ASC_TARGET, and the 'can solve over and over' test is degenerate (999 of 1,000 calls hit on the first try).

## Caveats and trade-offs

The claim has no numbers, hardware or benchmark code; test/ contains unit tests (blake2b, solver, puzzle) but no benchmark. The baseline is the library's own JS fallback, not a third-party JS blake2b. Directional only: a GrapheneOS forum thread (WebSearch snippet only) reports minutes-long solves when the browser falls back to the JS solver with the JIT disabled. The license is the source-available Friendly Captcha License (README; no LICENSE file in the root), so reference only. Notability is modest (212 stars, 22 forks), but it is the production proof-of-work component of Friendly Captcha. Last commit 2022-12-01.

Source-available licence, not OSI-approved; pinned to an old AssemblyScript version, upgrade is non-trivial.

## Maintenance

Abandoned since 2022-12-01 (two dependabot PRs left open) and source-available under the Friendly Captcha License, so reference only. The evidence stays directional because no same-hardware JS-vs-WASM hash rate was ever published, though issue #1 and PR #2 give first-party absolute WASM hash rates.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README says only 'The WASM build is an order of magnitude faster in most browsers' than the repo's own JavaScript fallback solver; there are no numbers, hardware or benchmark code (test/ holds unit tests only), and one WebSearch found no published hash rates, so D.
- **Verifier notes:** Kept at D: real production component, but the only evidence is a no-numbers README sentence. Main shortcomings: no measurement at all and a non-OSI source-available license. Metadata checked: 212 stars, last commit 2022-12-01 (abandoned), not archived, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/FriendlyCaptcha/friendly-pow>
  - <https://github.com/FriendlyCaptcha/friendly-pow/commits>
  - <https://github.com/FriendlyCaptcha/friendly-pow/tree/master/test>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/README.md>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/package.json>
- **Sources the enricher read:**
  - <https://github.com/FriendlyCaptcha/friendly-pow>
  - <https://github.com/FriendlyCaptcha/friendly-pow/commits/master>
  - <https://github.com/FriendlyCaptcha/friendly-pow/tree/master/src>
  - <https://github.com/FriendlyCaptcha/friendly-pow/tree/master/src/blake2b>
  - <https://github.com/FriendlyCaptcha/friendly-pow/tree/master/src/api>
  - <https://github.com/FriendlyCaptcha/friendly-pow/tree/master/test>
  - <https://github.com/FriendlyCaptcha/friendly-pow/issues?q=is%3Aissue>
  - <https://github.com/FriendlyCaptcha/friendly-pow/issues/1>
  - <https://github.com/FriendlyCaptcha/friendly-pow/pulls?q=is%3Apr>
  - <https://github.com/FriendlyCaptcha/friendly-pow/pull/2>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/README.md>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/package.json>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/entryWasm.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/solver.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/solverWasm.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/loader.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/puzzle.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/constants.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/diagnostics.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/blake2b/blake2b.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/blake2b/blake2b64.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/api/js.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/src/api/wasm.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/test/solver.astest.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/test/solver.test.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/test/blake2b64.astest.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-pow/HEAD/test/blake2b.test.ts>
  - <https://raw.githubusercontent.com/FriendlyCaptcha/friendly-challenge/HEAD/src/worker.ts>
  - <https://github.com/FriendlyCaptcha/friendly-challenge>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/friendlycaptcha/friendly-pow`) · [data/wave13/enrich/raw/github_com_friendlycaptcha_friendly_pow.json](../../../data/wave13/enrich/raw/github_com_friendlycaptcha_friendly_pow.json) (enrichment confidence 0.6)

</details>
