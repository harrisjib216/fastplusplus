# fast-noble-hashes (@r1ck404/fast-noble-hashes)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `WebAssembly (SHA-2, SHA-1, MD5, PBKDF2 loop, scrypt ROMix) with JavaScript, drop-in for @noble/hashes` · `MIT` · 🟢 active

> @noble/hashes 1.8.0 drop-in with SHA-2, SHA-1, MD5, PBKDF2 and scrypt in WebAssembly; 1.7-7.8x faster than noble's JS.

| | |
|---|---|
| **Beats** | @noble/hashes 1.8.0 (pure JavaScript) |
| **Claimed result** | sha512 on typescript 5.9.3 tarball (4.4 MB) 30.47 ms vs 5.68 ms (5.4x Node, 6.0x Chromium); sha256 1 MB 3.65 ms vs 2.12 ms (1.7x Node, 2.3x Chromium); sha1 1 MB 2.64 ms vs 1.01 ms (2.6x, 4.3x Chromium); md5 1 MB 8.95 ms vs 1.15 ms (7.8x); pbkdf2(sha512) c=10000 24.17 ms vs 3.36 ms (7.2x Node, 8.2x Chromium); scrypt N=2^14 36.32 ms vs 16.06 ms (2.3x). |
| **Workload** | One-shot and streaming hashes, HMAC, PBKDF2 and scrypt calls on npm tarballs and short strings, best of 3 rounds, Node 24.16 and headless Chromium. |
| **Metric** | latency |
| **Hardware** | Ryzen 7 7800X3D, Node 24.16 and Chromium 149 |
| **Compiler and flags** | No external compiler for the SHA-2/SHA-1/MD5/PBKDF2 kernels: hand-written WebAssembly emitted by the in-repo assembler (wasm/kernels.mjs, wasm/asm.mjs) and expanded at first use; scrypt ROMix assembled from wasm/scrypt.wat with binaryen (^132.0.0 devDependency); WASM SIMD required. Benchmarks run as node --expose-gc --max-old-space-size=8192 via bench/interleave.mjs on Node 24.16, plus headless Chromium 149. |
| **Adoption** | 1 star (fast-packages repo) |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/r1ck404/fast-packages/tree/main/packages/fast-noble-hashes) · [benchmark](https://github.com/R1ck404/fast-packages) |

## Verdict

First-party run on a Ryzen 7 7800X3D, Node 24.16 and headless Chromium 149, alternating fresh processes and keeping the best of 3 per-process medians, against pure-JS @noble/hashes 1.8.0: sha512 of the 4.4 MB typescript tarball 30.47 vs 5.68 ms (5.4x; 6.0x in Chromium), md5 1 MB 8.95 vs 1.15 ms (7.8x), sha1 1 MB 2.64 vs 1.01 ms (2.6x), sha256 1 MB 3.65 vs 2.12 ms (1.7x; about 494 MB/s in both Node and Chromium, so the WASM kernel, not OpenSSL), PBKDF2-SHA512 c=10000 24.17 vs 3.36 ms (7.2x), scrypt N=2^14 36.32 vs 16.06 ms (2.3x). node:crypto, WebCrypto and hash-wasm were not compared.

## Use it when

- Browser or in-browser-runtime code pinned to @noble/hashes 1.8.x that hashes large buffers with SHA-512/384 (npm lockfile SRI: 5.4x in Node, 6.0x in Chromium), MD5 (7.8x / 5.7x) or SHA-1 (2.6x / 4.3x), where node:crypto is not available.
- PBKDF2 key derivation in the browser or in a crypto polyfill: PBKDF2-SHA512 c=10000 7.2x (8.2x in Chromium), PBKDF2-SHA256 3.4x; scrypt N=2^14, r=8 2.3x.
- Many short one-shot hashes (56-character strings: 4-7x) such as cache keys or content IDs.
- Dependency trees where several packages import @noble/hashes 1.x: one npm alias or pnpm override redirects every import, with no call-site changes.

## Skip it when

- Projects on @noble/hashes 2.x (2.4.0 is current; ESM-only, .js import paths, no string inputs): there is no matching version, and the 1.8.0 baseline also predates noble's own 2.3.0 speedups (+10-45% on 32-byte inputs, +20% PBKDF2/HKDF).
- Node server code hashing large buffers: call node:crypto (OpenSSL) or WebCrypto directly; the package itself now defers to node:crypto for one-shot inputs of 64 KiB or more.
- SHA-3/Keccak, BLAKE2/BLAKE3, RIPEMD-160 or Argon2: these run noble's unchanged JS (1.0x); hash-wasm or awasm-noble accelerate them.
- Hosts without WebAssembly SIMD or with a CSP lacking wasm-unsafe-eval: the accelerated functions throw, there is no JS fallback.
- Security-critical code that relies on noble's audits: the WASM kernels and patches are an unaudited, weeks-old re-implementation by one author, assured only by its differential and mutation tests; streaming small updates (1.2x) and HMAC on short strings (1.3x) gain little anyway.

## How it is fast

The kernels are fully unrolled WASM (SHA-256 8.8 KB, SHA-512 11.3 KB) with state and message words in locals, expanded on first use from 244-541-byte templates written with an in-repo assembler (wasm/kernels.mjs, wasm/asm.mjs). SHA-512 uses native i64 arithmetic where noble's JS splits every 64-bit word into two 32-bit halves, which is why SHA-512/384 gain 5x while SHA-256 gains only 1.7x (V8's JIT already does 32-bit rotates well). One-shot hashers skip instance creation and UTF-8 encode strings straight into WASM memory; PBKDF2 runs all c iterations of HMAC inside WASM from the precomputed inner/outer states; scrypt's ROMix runs salsa20/8 on SIMD v128 registers (wasm/scrypt.wat).

## Compared with alternatives

Pick it over hash-wasm when existing code or dependencies already call @noble/hashes 1.8 synchronously and you need identical results and instance state with no call-site changes; pick hash-wasm (its own async API, SHA-3, BLAKE3, Argon2 and more in WASM) for new code or other algorithms, and awasm-noble when BLAKE3 throughput is the goal.

## Integration

| | |
|---|---|
| **Form** | module (npm package @r1ck404/fast-noble-hashes; noble's ESM and CommonJS entry points, WASM shipped as text templates inside _fast.js) |
| **Dependencies** | none at run time (binaryen ^132 and esbuild 0.28.2 only to rebuild the kernels) |
| **Minimum toolchain** | WebAssembly SIMD: Node 16.4+, Chrome/Edge 91+, Firefox 89+, Safari 16.4+ (README; the engines field says ^14.21.3 \|\| &gt;=16); the node:crypto path only where process.getBuiltinModule exists |
| **Platforms** | any WebAssembly host with SIMD (browser suite runs in Chromium, Firefox and WebKit, main thread and module worker) |
| **Thread safety** | not documented; each hash family keeps one module-level WASM instance (64 KiB, wiped after every call) per JS realm, and every call copies state in and out synchronously, so async PBKDF2/scrypt slices in one realm do not clash and each worker has its own instances |
| **Drop-in for the baseline** | partial — same exports, digests, errors and instance fields as @noble/hashes 1.8.0 when installed under its name, but it requires WebAssembly SIMD (throws without it), scrypt memory must fit in 4 GiB of WASM memory, pbkdf2Async/scryptAsync yield a different number of event-loop turns, and noble's private constant tables are gone; useless for noble 2.x |

## Gotchas

- The published Node rows describe an older code path: they were measured on 2026-09-28, before commit 7df1749 (2026-09-30, 1.8.2) routed one-shot Uint8Array/Buffer inputs of at least 64 KiB and strings of at least 65,536 code units to node:crypto. The repo's bench uses exactly such inputs (1 MB and 64 KB plain Uint8Arrays, npm tarballs), so rerunning it on current code in Node times OpenSSL, not the WASM kernels; the Chromium rows still measure WASM.
- The root README summary row (sha512 5x, md5 6.9x, sha1 2.4x, sha256 1.6x, pbkdf2 3.3-5.7x, scrypt 3.1x) is taken from the older 2026-09-27 run (results/noble-hashes-orig_vs_fast-interleaved-2026-09-27T13-31-54-604Z.md), in which the noble baseline itself ran about 1.5x slower than on 2026-09-28 (scrypt 55.30 vs 36.32 ms, sha512 4.4 MB tarball 46.55 vs 30.47 ms) while the fast scrypt barely moved (17.89 vs 16.06 ms): the 3.1x scrypt figure comes from a slow baseline run, and the detailed table gives 2.3x.
- npm 1.8.0 (2026-09-27) wraps the WASM init in a /\* @__PURE__ \*/ IIFE (esm/_fast.js line 99), so bundlers drop it and bundled apps silently get noble's JS speed; fixed in f8aa157 (1.8.1). The npm latest 1.8.3 (2026-09-30 19:12 UTC) has no commit in the repository and changes the glue to share one WASM memory across all hash families, reloading round constants on every family switch.
- The package LICENSE still says the kernels are re-implemented in Rust (rust/src), but that directory was replaced by WASM templates in f8aa157; only noble's MIT licence applies.

## Known shortcomings

- Numbers match README and results/\*2026-09-28\*, measured before commit 7df1749 (2026-09-30) added a node:crypto path for inputs of 64 KiB and more, so the measured sha256 (about 494 MB/s) is WASM while current 1.8.2 runs large Node inputs on OpenSSL and those rows are stale; the README summary contradicts the results (scrypt 3.1x vs 2.3x); the only baseline is pure-JS noble; LICENSE still names removed Rust kernels.
- Since 1.8.2 one-shot inputs of 64 KiB or more go to node:crypto, so rerunning the bench in Node times OpenSSL while the published rows are the WASM kernel. The root README summary (scrypt 3.1x and others) comes from a 2026-09-27 run in which the noble baseline ran about 1.5x slower (scrypt 55.30 vs 36.32 ms) than in the detailed table (2.3x). npm 1.8.0 marks the wasm init /\* @__PURE__ \*/ (esm/_fast.js:99), so tree-shaking bundlers shipped noble's JS; npm 1.8.3 is not in the repo and shares one wasm memory across hash families. Baseline stale: noble 1.8.0 versus current 2.4.0 (2.3.0 added 10-45% on short inputs and 20% on pbkdf2).

## Caveats and trade-offs

First-party numbers on a days-old repository with 1 star (published numbers measured 2026-09-28). The record's earlier worry that the Node column measures OpenSSL does not hold for the published numbers: they were measured before commit 7df1749 (2026-09-30) added the node:crypto path for one-shot inputs of 64 KiB or more, and the measured Node sha256 1 MB time (2.12 ms, about 494 MB/s, the same as in Chromium) is the WASM kernel, not SHA-NI OpenSSL. The reverse problem applies now: the current 1.8.2 package hands large one-shot hashes in Node to node:crypto, so the large-input Node rows describe an older code path, and the README tables were not re-measured after that change. The root README summary table disagrees with its own results table (scrypt 3.1x vs 2.3x measured, pbkdf2 3.3-5.7x vs 3.4x/7.2x, md5 6.9x vs 7.8x). The only baseline is pure-JS @noble/hashes 1.8.0; hash-wasm, node:crypto and WebCrypto, which are much faster on large inputs, are not compared. Short-input gains are smaller for streaming (sha256 64 KB in 100 B updates 1.2x, hmac sha256 1.3x). Each row keeps the best (minimum) per-process median of 3 interleaved fresh-process rounds. The package LICENSE still says the kernels are re-implemented in Rust (rust/src), but that directory is gone (replaced by wasm templates in f8aa157). Before f8aa157, bundled builds silently ran noble's JS because the wasm init was marked /\* @__PURE__ \*/. SHA-3, BLAKE, RIPEMD-160 and Argon2 run noble's code unchanged (1.0x). The repo URL points at the package directory of R1ck404/fast-packages. [retier] First-party numbers on a days-old repository with 1 star (measured 2026-09-28). The published Node rows are the WASM kernel (sha256 1 MB 2.12 ms, about 494 MB/s, same as Chromium), measured before commit 7df1749 (2026-09-30, 1.8.2) routed one-shot inputs of 64 KiB or more to node:crypto; rerunning the bench in Node now times OpenSSL. The root README summary (scrypt 3.1x and others) comes from a 2026-09-27 run in which the noble baseline ran about 1.5x slower (scrypt 55.30 vs 36.32 ms) than in the detailed table (2.3x). npm 1.8.0 marks the wasm init /\* @__PURE__ \*/ (esm/_fast.js:99), so tree-shaking bundlers shipped noble's JS instead; npm 1.8.3 is not in the repo and shares one wasm memory across hash families. Baseline stale: noble 1.8.0 versus current 2.4.0 (2.3.0 added 10-45% on short inputs and 20% on pbkdf2).

Needs WebAssembly with SIMD (accelerated functions throw without it); SHA-3, BLAKE, RIPEMD-160 and Argon2 run noble's unchanged code; a single sha256 or md5 import is larger than noble's.

## Maintenance

Active but brand new (first npm release 2026-09-27, single author, 1 star, no issues), MIT, installable by npm alias; it mirrors noble 1.8.0 while upstream is at 2.4.0, and the npm latest (1.8.3) is not reproducible from the repository, so pin a version and re-run its differential tests before trusting it with security-relevant hashing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers: the root README 'fast-noble-hashes vs @noble/hashes 1.8.0' table matches the committed raw data (results/noble-hashes-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-40-08-521Z.md and the -browser- 2026-09-28T10-49-01-639Z file), with the harness public (bench/interleave.mjs, noble-hashes suites), CPU (Ryzen 7 7800X3D) and runtimes (Node 24.16, Chromium 149) stated. Not upgraded to A because the measured build is not pinned to a commit: the results predate the commits that hold them, the Rust kernels were replaced by assembler templates around the measurement (f8aa157, 2026-09-29), and HEAD (7df1749, 2026-09-30) changed the Node code path for large inputs, so the current harness on the current code does not reproduce the large-input Node rows.
- **Verifier notes:** Every claimed number matches the README results table and the committed raw files, both Node and Chromium columns. Shortcomings to record: first-party only, 1 star, days old; pure-JS noble is the only baseline; the README tables predate HEAD's native node:crypto path, so the large-input Node rows no longer describe what the shipped package runs; the README summary table contradicts the measured table (scrypt 3.1x vs 2.3x); the LICENSE text describes the removed Rust kernels. Could be argued up to A (public harness, CPU, runtime versions, no external compiler for the hash kernels) if reproduction from git history at f8aa157/73a1829 is accepted.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-22 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/R1ck404/fast-packages>
  - <https://github.com/R1ck404/fast-packages/commits/main>
  - <https://github.com/R1ck404/fast-packages/tree/main/results>
  - <https://github.com/R1ck404/fast-packages/tree/main/packages/fast-noble-hashes>
  - <https://github.com/R1ck404/fast-packages/commit/7df1749>
  - <https://github.com/R1ck404/fast-packages/commit/f8aa157>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/interleave.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/LICENSE>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/test/native.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/noble-hashes-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-40-08-521Z.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/noble-hashes-browser-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-49-01-639Z.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/README.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/package.json>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/LICENSE>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/packages/fast-noble-hashes/esm/_fast.ts>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/noble-hashes.bench.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/noble-hashes-browser.bench.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/harness.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/interleave.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/bench/corpus.mjs>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/noble-hashes-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-40-08-521Z.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/noble-hashes-browser-orig_vs_prev_vs_fast-interleaved-2026-09-28T10-49-01-639Z.md>
  - <https://raw.githubusercontent.com/R1ck404/fast-packages/HEAD/results/noble-hashes-orig_vs_fast-interleaved-2026-09-27T13-31-54-604Z.md>
  - <https://github.com/R1ck404/fast-packages/tree/main/results>
  - <https://github.com/R1ck404/fast-packages/commits/main>
  - <https://github.com/R1ck404/fast-packages/issues?q=is%3Aissue>
  - <https://registry.npmjs.org/@r1ck404%2ffast-noble-hashes>
  - <https://registry.npmjs.org/@r1ck404/fast-noble-hashes/-/fast-noble-hashes-1.8.0.tgz>
  - <https://registry.npmjs.org/@r1ck404/fast-noble-hashes/-/fast-noble-hashes-1.8.2.tgz>
  - <https://registry.npmjs.org/@r1ck404/fast-noble-hashes/-/fast-noble-hashes-1.8.3.tgz>
  - <https://registry.npmjs.org/@noble%2fhashes>
  - <https://github.com/paulmillr/noble-hashes/releases>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `paper:r1ck404-fast-packages-fast-noble-hashes`) · [data/wave13/enrich/raw/paper_r1ck404_fast_packages_fast_noble_hashes.json](../../../data/wave13/enrich/raw/paper_r1ck404_fast_packages_fast_noble_hashes.json) (enrichment confidence 0.7)

</details>
