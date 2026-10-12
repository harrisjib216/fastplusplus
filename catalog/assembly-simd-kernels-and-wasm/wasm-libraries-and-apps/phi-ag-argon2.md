# @phi-ag/argon2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Argon2 password hashing as a 48 KB npm package with a WebAssembly SIMD build; 1.4-2.1x faster than hash-wasm and libsodium.js.

| | |
|---|---|
| **Beats** | hash-wasm Argon2 and libsodium.js Argon2 (both WebAssembly builds) |
| **Claimed result** | 'defaults' 5.6066 hz vs 3.3434 hz for hash-wasm (1.68x faster); 'fast' 330.46 hz vs 159.50 hz (2.07x); 'libsodium' parameters 4.3063 hz vs 3.1743 hz for libsodium.js (1.36x). |
| **Workload** | Argon2 hash-and-verify with default, 'fast' and libsodium-compatible parameter sets using vitest bench. |
| **Metric** | throughput |
| **Compiler and flags** | emcc -std=c89 -O3 -flto -msimd128 -mavx2 -sSTRICT -sPURE_WASI -sNO_ASSERTIONS -sNO_FILESYSTEM -sMALLOC=emmalloc -sALLOW_MEMORY_GROWTH -DARGON2_NO_THREADS -D__AVX2__ on the unmodified phc-winner-argon2 submodule (build.sh); CI builds with the docker image emscripten/emsdk:6.0.12 (.github/actions/emscripten/action.yml), but the README example results do not say which build or Node version produced them |
| **Adoption** | 13 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/phi-ag/argon2) · [benchmark](https://github.com/phi-ag/argon2#benchmark) |

## Verdict

The author's vitest bench (hash then verify per iteration, argon2id, ASCII password) shows 5.61 vs 3.34 ops/s against hash-wasm (4.12.0 in today's package.json) at t=3, m=64 MiB, p=4 (1.68x), 330 vs 160 ops/s at t=8, m=512 KiB, p=1 (2.07x), and 4.31 vs 3.17 ops/s against libsodium-wrappers-sumo (0.8.4 today) at t=4, m=64 MiB, p=1 (1.36x); all are wasm-versus-wasm on an unnamed machine and Node version, printed by vitest 3.1.4 from a harness that has since been rewritten. Native Argon2 (node:crypto, OpenSSL, libargon2) was not measured.

## Use it when

- Argon2id hashing or verification in browsers, Cloudflare Workers or other wasm-only runtimes with WebAssembly SIMD, where no native Argon2 is available.
- You already ship hash-wasm or libsodium.js only for Argon2 and want roughly 1.4-1.7x lower latency at 64 MiB memory cost with a 48 KB package.
- Client-side key derivation where blocking the calling thread for one hash (about 89 ms per hash at 64 MiB on the author's unnamed machine, derived from page data) is acceptable, or the work already runs in a Web Worker.
- You need output that matches node:crypto argon2 bit-for-bit (tests compare every Argon2 type against argon2Sync) on 0.6.0 or later.

## Skip it when

- Node.js or Bun servers: the README itself points to the native crypto.argon2 implementations, which offer async APIs and real lane parallelism; native speed was never compared.
- Runtimes without WebAssembly SIMD128: there is no scalar fallback build (hash-wasm runs there).
- Throughput-bound servers: hash and verify are synchronous and block the event loop, and parallelism &gt; 1 is computed sequentially (ARGON2_NO_THREADS), so p=4 buys no speed.
- Existing hashes of non-ASCII passwords created with 0.5.28 or earlier: they no longer verify on 0.6.x (issue #923 fix), and there is no byte-array password API to re-derive them yet.
- You need other hash functions, keyed hashing (secret) or associated data: the API exposes only password, salt and the cost parameters.

## How it is fast

The speedup comes from the build, not new code. Emscripten compiles phc-winner-argon2's optimized opt.c with -msimd128 -mavx2 -D__AVX2__, so the AVX2 BlaMka round (__m256i rotations via _mm256_shuffle_epi8, _mm256_permute4x64_epi64 diagonalization) is lowered through Emscripten's emulation of 256-bit intrinsics onto pairs of WebAssembly SIMD128 operations; the baselines hash-wasm (scalar uint64 C, its Makefile leaves -msimd128 commented out) and libsodium.js run scalar wasm. The wrapper keeps one instantiated module and emmalloc heap alive across calls, while hash-wasm instantiates fresh argon2 and BLAKE2b instances and grows new linear memory on every call.

## Compared with alternatives

Pick it over hash-wasm when Argon2 is the only algorithm you need and every target runtime has wasm SIMD: it is 1.7x (64 MiB) to 2.1x (512 KiB) faster there and offers a synchronous API; stay with hash-wasm for its many other hashes, async API, or runtimes without SIMD128.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (one bundled argon2.wasm); building it needs Emscripten (CI uses the emscripten/emsdk:6.0.12 docker image) and the phc-winner-argon2 git submodule pinned at f57e61e |
| **Minimum toolchain** | ESM JavaScript runtime with WebAssembly SIMD128 and crypto.getRandomValues (minimum browser or Node versions not documented); e2e tests run on Chromium, Firefox and WebKit via Playwright; development uses Node 26.x and TypeScript 6 |
| **Platforms** | any WebAssembly runtime with SIMD128: Node.js, Deno, Bun, browsers (Vite or vanilla), Cloudflare Workers |
| **Thread safety** | not documented; one synchronous Argon2 instance per JS thread or Worker, single-threaded internally (ARGON2_NO_THREADS) |
| **Drop-in for the baseline** | partial: produces standard PHC-encoded argon2 strings interoperable with hash-wasm, libsodium and node:crypto (on 0.6.0+), but the API is synchronous and differs from hash-wasm's async argon2id/argon2Verify and libsodium's crypto_pwhash_str |

## Gotchas

- Security bug fixed only in 0.6.0 (2026-09-29, issue #923): from 0.0.1 to 0.5.28 tryHash and tryVerify passed the UTF-16 password.length as the byte count, so non-ASCII passwords were hashed over a truncated UTF-8 prefix ("Zürich2026?" verified against the hash of "Zürich2026!"); such hashes do not match other Argon2 implementations and stop verifying after upgrading. Benchmark passwords were ASCII, so the measured numbers are unaffected.
- Harness flaw: the README example (vitest 3.1.4 output, about May 2025) came from the old bench file that ran 10 s per task and gave hash-wasm a 1 s warmup; commit d152440 (2026-09-08) rewrote it to vitest 5 bench.compare without those settings and the README was not re-run, and no CPU or Node version is given. The hash-wasm task also pays per-call WebAssembly instantiation of argon2 and BLAKE2b instances plus fresh 64 MiB memory growth, which @phi-ag/argon2 does once outside the timed loop.
- Per-pass costs derived from page data (hash plus verify = two Argon2 runs per iteration): @phi-ag/argon2 about 29-30 ms per 64 MiB pass in both 'defaults' and 'libsodium' rows, libsodium.js about 39 ms, hash-wasm about 50 ms; the 1.36x libsodium.js row is the cleanest SIMD-versus-scalar-wasm figure, and hash-wasm's larger gaps include its per-call setup.
- WebAssembly memory never shrinks: after one 64 MiB hash the instance keeps at least 64 MiB of linear memory (ALLOW_MEMORY_GROWTH with emmalloc) for its lifetime.

## Known shortcomings

- Wasm-against-wasm only (hash-wasm, itself listed at tier A, and libsodium.js), native Node crypto argon2 not compared; hash-wasm creates a new wasm instance per call; no CPU or Node version.
- Security bug: up to 0.5.28 non-ASCII passwords were hashed over a truncated UTF-8 prefix (tryHash and tryVerify passed the UTF-16 password.length as the byte count, issue #923); fixed in 0.6.0 (2026-09-29), and old hashes for such passwords no longer verify; the benchmark used ASCII passwords, so the numbers are unaffected. Harness flaw: the README output comes from the old bench file (vitest 3.1.4, 10 s per task, a 1 s warm-up for hash-wasm only), rewritten in d152440 (2026-09-08) without the README being re-run; hash-wasm is built without -msimd128 and re-instantiated with fresh 64 MiB memory on every call. Per 64 MiB pass (derived): @phi-ag/argon2 about 29-30 ms, libsodium.js about 39 ms, hash-wasm about 50 ms, so the 1.36x vs libsodium.js is the cleanest gain; native node:crypto argon2 was never timed.

## Caveats and trade-offs

Baselines are other wasm libraries (hash-wasm 4.12.0, itself a listed tier-A entry, and libsodium-wrappers-sumo 0.8.4 per package.json), not native argon2, Node's built-in crypto.argon2 (the README itself points to the native Node.js and Bun implementations) or a JS implementation, so this is a wasm-versus-wasm win that does not meet the category's native or JS baselines. The gain comes from building phc-winner-argon2's opt.c AVX2 path through Emscripten's AVX2-to-SIMD128 emulation (requires wasm SIMD support in the runtime). The hash-wasm side creates a new WASMInterface and grows its memory to memorySize on every argon2id call (lib/argon2.ts), while @phi-ag/argon2 reuses one initialized instance outside the timed loop; that is a real API cost of hash-wasm but inflates the 'fast' (512 KiB, about 3 ms) ratio. Hardware and Node version are not stated; the example output was printed by vitest 3.1.4 while package.json now pins vitest 5.0.3, so the library versions behind the example are uncertain. Single-threaded on both sides (ARGON2_NO_THREADS) even with parallelism 4. [retier] Baselines are other wasm libraries (hash-wasm 4.12.0, built without -msimd128, and libsodium-wrappers-sumo 0.8.4), not native argon2, Node's built-in crypto.argon2 or a JS implementation, so this is a wasm-versus-wasm win that does not meet the category's native or JS baselines. The gain comes from building phc-winner-argon2's opt.c AVX2 path through Emscripten's AVX2-to-SIMD128 emulation. Harness flaw: the README example (vitest 3.1.4 output, about May 2025) came from the old bench file that ran 10 s per task and gave hash-wasm a 1 s warm-up; commit d152440 (2026-09-08) rewrote it to vitest 5 bench.compare without those settings and the README was not re-run; no CPU or Node version is given. The hash-wasm task also pays per-call WebAssembly instantiation of argon2 and BLAKE2b instances plus fresh 64 MiB memory growth, which @phi-ag/argon2 does once outside the timed loop; per 64 MiB pass (derived from page data, hash plus verify = two runs per iteration) @phi-ag/argon2 is about 29-30 ms, libsodium.js about 39 ms and hash-wasm about 50 ms, so the 1.36x libsodium.js row is the cleanest SIMD-versus-scalar-wasm figure. Security bug fixed only in 0.6.0 (2026-09-29, issue #923): from 0.0.1 to 0.5.28 non-ASCII passwords were hashed over a truncated UTF-8 prefix, such hashes do not match other Argon2 implementations and stop verifying after upgrading (benchmark passwords were ASCII). WebAssembly memory never shrinks (at least 64 MiB kept after one hash).

Wasm SIMD build only (a minimal Argon2 module). Single-threaded (ARGON2_NO_THREADS), reference C code unmodified.

## Maintenance

Actively maintained (release 0.6.1 on 2026-10-10, Renovate-driven dependency updates, 13 stars), MIT-licensed and copyable, but upgrade past 0.6.0 for the non-ASCII password truncation fix and rehash affected passwords.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party vitest bench output in the README matches every claimed number, and the harness (src/index.bench.ts) and build flags (build.sh; CI pins the emscripten/emsdk:6.0.12 image) are public, but no CPU model or Node version accompanies the example results and the bench workflow page shows no output, so not A; no independent measurement, so C.
- **Verifier notes:** README numbers, harness and build script verified; metadata holds (MIT, 13 stars, last commit 2026-10-11, active, not a fork). Off-baseline (baseline_in_list false is correct): it beats other wasm builds, including the listed hash-wasm, not the native library or JS. Shortcomings to record: wasm-vs-wasm only, native Node crypto.argon2 not compared, per-call instantiation on the hash-wasm side, no hardware or Node version, example output from an older vitest.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/phi-ag/argon2>
  - <https://github.com/phi-ag/argon2/commits>
  - <https://github.com/phi-ag/argon2/actions/workflows/bench.yml>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/README.md>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/build.sh>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/src/index.bench.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/package.json>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/.github/actions/emscripten/action.yml>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/argon2.ts>
- **Sources the enricher read:**
  - <https://github.com/phi-ag/argon2>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/README.md>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/build.sh>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/package.json>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/src/index.bench.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/src/node.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/src/fetch.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/src/index.test.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/vitest.config.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/playwright.config.ts>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/phi-ag/argon2/HEAD/.github/actions/emscripten/action.yml>
  - <https://github.com/phi-ag/argon2/commits/main/src/index.bench.ts>
  - <https://github.com/phi-ag/argon2/commit/d152440>
  - <https://github.com/phi-ag/argon2/commits/main/build.sh>
  - <https://github.com/phi-ag/argon2/commit/9e87bf4>
  - <https://github.com/phi-ag/argon2/issues?q=is%3Aissue>
  - <https://github.com/phi-ag/argon2/issues/923>
  - <https://registry.npmjs.org/@phi-ag%2Fargon2/latest>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/argon2.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/WASMInterface.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/src/argon2.c>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/Makefile-clang>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/P-H-C/phc-winner-argon2/f57e61e/src/opt.c>
  - <https://raw.githubusercontent.com/P-H-C/phc-winner-argon2/f57e61e/src/blake2/blamka-round-opt.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/phi-ag/argon2`) · [data/wave13/enrich/raw/github_com_phi_ag_argon2.json](../../../data/wave13/enrich/raw/github_com_phi_ag_argon2.json) (enrichment confidence 0.75)

</details>
