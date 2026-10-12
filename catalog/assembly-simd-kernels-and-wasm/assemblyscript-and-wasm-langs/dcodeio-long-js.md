# long.js (64-bit integer library with a WebAssembly fast path)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `Apache-2.0` · 🟡 stale

> Closure-derived int64/uint64 class for JavaScript; a tiny hand-written WebAssembly module beats its own float-based JS fallback on mul, div and rem.

| | |
|---|---|
| **Beats** | the library's own floating-point-based JavaScript fallback for 64-bit multiply, divide and remainder |
| **Claimed result** | README: slow operations like division are 'around twice as fast' with the WebAssembly module. |
| **Workload** | 64-bit integer multiplication, division and remainder through a tiny hand-written WebAssembly module (wasm.wat) vs the JavaScript fallback. |
| **Metric** | throughput |
| **Adoption** | 918 stars; widely depended on (npm long) |
| **Last commit** | 2025-04-17 |
| **Links** | [repository](https://github.com/dcodeIO/long.js) · [benchmark](https://github.com/dcodeIO/long.js) |

## Verdict

The README says only that 'slow operations like division are around twice as fast' with the Wasm module, with no code, engine or hardware. A third-party run in issue #88 (Node v10.20.1, AMD Threadripper 2950X, 10M iterations x 10, Wasm vs --no-expose-wasm, benchmark file attached to the issue) measured an xor+mul+add+shr+sub chain at 89.57 vs 170.53 ns (1.9x) and the same chain plus div at 125.41 vs 589.22 ns (4.7x; the div step alone is about 36 vs 419 ns, about 11.7x, derived from page data). An enricher run (Node v22.22.0, Intel Xeon @ 2.10 GHz VM, 200,000 random operand pairs, median of 7, fallback forced by nulling the Wasm instance) measured mul 3.5x, div 10-16x and mod 13-19x over the JS fallback, with BigInt + asIntN at 0.6-1.1x the Wasm path's time. So the README understates the gain on current V8.

## Use it when

- Exact wrapping int64/uint64 arithmetic in JavaScript where BigInt is unavailable, disallowed, or not what an API expects (protobufjs and Closure-style code pass Long objects).
- Division- and remainder-heavy 64-bit work (ID and hash arithmetic, 64-bit decoders) in engines with WebAssembly: about 10-19x faster than the forced JS fallback in the enricher's Node 22 run.
- Code that needs direct access to the low and high 32-bit words, or must run unchanged in browsers, Node, Deno and older engines with automatic fallback.

## Skip it when

- Modern-only targets: native BigInt with BigInt.asIntN/asUintN took 0.6-1.1x the Wasm path's time per op in the enricher run, and it needs no library or Long allocations.
- Pages with a strict CSP that blocks WebAssembly compilation (issue #58), or engines without Wasm: it silently falls back to JS, which was 3.5x (mul) to 19x (mod) slower in the enricher run.
- Node 16.1+ on ARMv6: the import-time Wasm probe crashed the process instead of throwing (issue #107, closed as not planned).
- Signed division by -1 of values near MIN_VALUE, or code that catches Error from mod(0): see gotchas.
- Allocation-sensitive hot loops: each op creates a new Long object, and there are no in-place or mutable variants (issue #88's 'Q' variant proposal was not merged).

## How it is fast

At import, index.js synchronously instantiates an inline module of about 200 bytes (source in wasm.wat) that exports mul, div_s, div_u, rem_s, rem_u and get_high. Each export rebuilds an i64 from the two 32-bit halves, runs one native i64.mul, i64.div or i64.rem, returns the low half, and leaves the high half in a mutable Wasm global that JS reads with get_high(). This replaces the Closure Library algorithms: a 16-bit-limb schoolbook multiply, and a division loop that approximates rem/divisor in doubles and corrects downward, with modulo computed as this - (this/d)\*d. Add, subtract, shifts and comparisons stay in JS.

## Compared with alternatives

Pick long.js when you need a complete int64/uint64 value type in plain JavaScript with automatic Wasm acceleration and fallback. wasm-i128-div-bench is a 128-bit reciprocal-division technique for Rust-compiled Wasm, and galois targets finite-field arithmetic through AssemblyScript; neither is a general 64-bit integer type.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | ES5-level JavaScript for the fallback; WebAssembly MVP with synchronous new WebAssembly.Module for the fast path; BigInt only for fromBigInt/toBigInt (added when typeof BigInt === 'function') |
| **Platforms** | any JavaScript engine (browsers, Node.js, Deno, Bun); the Wasm path needs Wasm compilation to be allowed |
| **Thread safety** | Long values are immutable; each realm or worker gets its own Wasm instance, whose mutable 'high' global is read immediately after each call, so it is safe in ordinary single-threaded JS (from source, not documented) |
| **Drop-in for the baseline** | partial — the Wasm path and the JS fallback share one API and are selected automatically at load, but the Wasm path returns a different result for signed x.div(-1) when x is within 2^32 of MIN_VALUE, and throws a different error type for mod(0) |

## Gotchas

- Correctness bug on the Wasm path, which is the default in every current engine. The signed-division overflow guard tests this.high === -0x80000000 and divisor === -1 but not this.low === 0, so x.div(-1) returns x unchanged for all 2^32 signed values from MIN_VALUE to MIN_VALUE + 2^32 - 1. For example, Long.fromBits(5, 0x80000000).div(-1) gives -9223372036854775803 instead of 9223372036854775803. The JS fallback is correct. Reproduced with 5.3.2 HEAD on Node v22.22.0; tests/index.js does not cover it and no issue has been filed.
- modulo() has no zero-divisor check on the Wasm path: x.mod(0) throws WebAssembly.RuntimeError 'remainder by zero', whereas div(0) and the JS fallback throw Error 'division by zero'. 20,000 random signed operand pairs otherwise matched BigInt on both paths for mul, div and mod.
- The Wasm probe runs at import time. Under a CSP that blocks Wasm compilation it reports a violation and falls back (issue #58). Node 12 on Apple M1 died with 'wasm code commit Allocation failed' (issue #95, fixed by newer Node), and ARMv6 with Node 16.1+ hits a V8 trap (issue #107).
- Mixing the ESM and CommonJS builds yields two different Long classes (README). isLong() checks the __isLong__ brand, so values still interoperate, but instanceof does not.

## Known shortcomings

- One README phrase only (division "around twice as fast"), no benchmark code; the baseline is the library's own JavaScript fallback; hand-written WAT, loose fit for the AssemblyScript category.
- Enricher: correctness bug in the measured Wasm path, reproduced on Node v22.22.0 with 5.3.2: the div guard skips the low-word check so x.div(-1) returns x for all 2^32 values from MIN_VALUE to MIN_VALUE+2^32-1 (JS fallback correct, unreported), and mod(0) throws WebAssembly.RuntimeError rather than Error; independent run in issue #88 (Node v10.20.1, Threadripper 2950X, --no-expose-wasm): mul chain 1.9x, div step about 11.7x (derived); the enricher's own run: mul 3.5x, div 10-16x, mod 13-19x, BigInt plus asIntN on par. Tier kept at C because of the unfixed hot-path bug. Lead: consento-org/longfn.

## Caveats and trade-offs

The only evidence is one README phrase ('slow operations like division are around twice as fast'), with no benchmark code in the repo, no hardware, no engine or Node.js version and no operand distribution. The phrase covers division only; multiplication and remainder also use the WASM path (index.js calls wasm mul, div_s/div_u and rem_s/rem_u) but have no stated figure. One WebSearch found no independent measurement; the claim only reappears in README mirrors (forks, @xtuc/long, purescript-int64). The baseline is the library's own JavaScript fallback, not C++ or Emscripten. Fit with assemblyscript-and-wasm-langs is loose: this is a hand-written WAT module (wasm.wat, 213 lines) inside a JavaScript library, not AssemblyScript output. Widely depended on as npm 'long' (for example by protobufjs).

Falls back to the JS implementation where WebAssembly is unavailable; module is hand-written WAT, not a compiled language.

## Maintenance

Stale but stable: npm 5.3.2 (2025-04-17) is the last release (143 commits, 918 stars, one open feature request). It is Apache-2.0, one dependency-free file, and widely depended on (about 4M weekly npm downloads per a 2022 comment in issue #107). The Wasm-path div(-1) bug near MIN_VALUE is unreported upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 'WebAssembly support' section has one first-party ratio: slow operations like division are 'around twice as fast' with the wasm.wat module than with the JavaScript fallback. The repo has no benchmark code (tests/ holds unit tests and TypeScript checks; scripts/ only build.js) and no hardware or engine version, so this is a stated ratio without methodology, which is tier C (same as the lodepng 'twice as fast as libpng' precedent).
- **Verifier notes:** Metadata checks out: Apache-2.0, 918 stars, 206 forks, not archived or forked, last commit 2025-04-17, so 'stale' is correct. Shortcomings: unmeasured 'around twice as fast' claim for division only, no benchmark code, baseline is the library's own JS fallback, loose category fit. It is notable through npm usage, so it stays listed even though the evidence is thin.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-54 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/README.md>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/index.js>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/wasm.wat>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/package.json>
  - <https://github.com/dcodeIO/long.js>
  - <https://github.com/dcodeIO/long.js/commits>
  - <https://github.com/dcodeIO/long.js/tree/main/tests>
  - <https://github.com/dcodeIO/long.js/tree/main/scripts>
- **Sources the enricher read:**
  - <https://github.com/dcodeIO/long.js>
  - <https://github.com/dcodeIO/long.js/issues>
  - <https://github.com/dcodeIO/long.js/pulls>
  - <https://github.com/dcodeIO/long.js/issues?q=is%3Aissue+div>
  - <https://github.com/dcodeIO/long.js/issues?q=is%3Aissue+wasm>
  - <https://github.com/dcodeIO/long.js/issues/88>
  - <https://github.com/dcodeIO/long.js/issues/107>
  - <https://github.com/dcodeIO/long.js/issues/95>
  - <https://github.com/dcodeIO/long.js/issues/58>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/README.md>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/index.js>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/index.d.ts>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/types.d.ts>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/wasm.wat>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/package.json>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/umd/package.json>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/scripts/build.js>
  - <https://raw.githubusercontent.com/dcodeIO/long.js/HEAD/tests/index.js>
  - <https://registry.npmjs.org/long>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/dcodeio/long.js`) · [data/wave13/enrich/raw/github_com_dcodeio_long_js.json](../../../data/wave13/enrich/raw/github_com_dcodeio_long_js.json) (enrichment confidence 0.8)

</details>
