# hash-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C (compiled to WebAssembly) + TypeScript` · `MIT` · 🟡 stale

> Hash and password-KDF functions in C compiled to tiny wasm modules; 1.5-16x faster than the best pure-JS libraries tested.

| | |
|---|---|
| **Beats** | Pure-JavaScript hash libraries in V8 (crypto-js, spark-md5, jsSHA, noble-hashes, node-forge, xxhashjs) and other WASM hash packages |
| **Claimed result** | 1 MB throughput: MD5 850.31 MB/s vs spark-md5 171.73 and crypto-js 46.71 MB/s; SHA256 426.16 vs noble-hashes 110.02, crypto-js 65.17 MB/s; SHA3-512 234.40 vs noble-hashes 14.19 MB/s; XXHash64 15 989 MB/s vs xxhashjs 42.26 MB/s; PBKDF2-SHA512 588 ops vs crypto-js 29 ops; Argon2id 438 ops vs argon2-browser 213 ops |
| **Workload** | Hash throughput at 32-byte and 1 MB inputs (MD5, SHA1, SHA256, SHA3-512, XXHash64) plus PBKDF2-SHA512 and Argon2id ops/s, in Chrome via the hash-wasm-benchmark app |
| **Metric** | throughput |
| **Hardware** | Ryzen 9 7900X desktop CPU, Chrome v131 |
| **Compiler and flags** | clang --target=wasm32 -flto -O3 -nostdlib -fno-builtin -ffreestanding -mexec-model=reactor, wasm-ld --strip-all (scripts/Makefile-clang, identical at tag v4.10.0); the measured 4.10.0 binaries were built in an alpine:3.18.4 Docker image (scripts/Dockerfile at v4.10.0; HEAD now uses alpine:3.20.3), clang version implied by the Alpine release but not printed in the README; WASM SIMD flags commented out. Baselines are JavaScript run by Chrome v131's V8. |
| **Adoption** | 1.2k stars |
| **Last commit** | 2024-11-19 |
| **Links** | [repository](https://github.com/Daninet/hash-wasm) · [benchmark](https://github.com/Daninet/hash-wasm#benchmark) |

## Verdict

Author's in-browser benchmark (hash-wasm-benchmark app, Chrome 131 on a Ryzen 9 7900X, hash-wasm 4.10.0 built with clang -O3 -flto in Alpine 3.18.4, every library's digest checked against hash-wasm's during warm-up, about 1 s per scenario): at 1 MB MD5 850 MB/s vs spark-md5 172 (4.95x), SHA-256 426 vs noble-hashes 1.3.2 110 (3.9x), SHA3-512 234 vs 14.2 (16.5x), xxHash64 15,989 vs xxhashjs 42 MB/s but level with xxhash-wasm; PBKDF2-SHA512 588 vs 395 ops/s for noble-hashes (1.49x) and Argon2id 438 vs 213 ops/s for argon2-browser (2.06x), ratios derived from page data. No native WebCrypto or node:crypto baseline was measured.

## Use it when

- Browser or Deno code hashing large in-memory buffers or file chunks with algorithms that WebCrypto's digest() does not provide, such as MD5, xxHash, BLAKE2/BLAKE3, CRC32/CRC64 or SHA-3 (MD5 850 MB/s vs spark-md5 172 MB/s at 1 MB).
- Streaming or resumable hashing: synchronous update()/digest() inside a worker, or save()/load() to split hashing of a big file across invocations.
- Password hashing in a JS runtime without native bindings: Argon2id 438 vs 213 ops/s for argon2-browser, PBKDF2-SHA512 588 vs 395 ops/s for noble-hashes, plus bcrypt and scrypt.
- Many tiny inputs where per-call cost matters: the shorthand path reached 110 MB/s on 32-byte MD5 inputs vs 39 MB/s for spark-md5.
- Bundle-size-sensitive apps: each algorithm is a separate tree-shakable module of 3-11 kB gzipped.

## Skip it when

- SHA-1/SHA-2 where crypto.subtle.digest or node:crypto createHash is available: neither native path is in the author's benchmark, user-submitted MeasureThat.net runs (search snippets only; the pages were unreachable) show WebCrypto SHA-256 at roughly 2-4x hash-wasm's ops/s, and issue #47 reports hash-wasm about 9x slower than crypto.subtle with Chrome DevTools open.
- Pages with a strict Content-Security-Policy that lacks 'unsafe-eval' or 'wasm-unsafe-eval': WebAssembly.compile of the embedded base64 module fails (issue #3, open; the maintainer declined an injectable WebAssembly option).
- xxHash64 on large inputs as the only need: hash-wasm and xxhash-wasm are level at 1 MB (15,989 vs 15,929 MB/s).
- Fastest possible Argon2, or Argon2 with parallelism above 1: the sibling @phi-ag/argon2 measures 1.68-2.07x hash-wasm's Argon2, and hash-wasm's lib/argon2.ts fills the lanes one after another in a single wasm instance, so extra lanes add no speed (multithreading is only a README future plan).
- Long-lived Firefox pages that hash thousands of files or call argon2id repeatedly: several users report memory growth until out-of-memory (issue #69, open, not reproduced on Node or Chromium).

## How it is fast

Each algorithm is portable scalar C (for example Solar Designer's public-domain MD5 and an RHash-style SHA-256 with rounds fully unrolled by #pragma clang loop unroll(full)) compiled freestanding with clang -O3 -flto into its own wasm module of a few kB with a fixed 128 KiB memory. Input is copied into a 16 KiB staging buffer in linear memory and hashed chunk by chunk; for inputs under 16 KiB the shorthand functions run init, update and final in a single JS-to-wasm call and format hex into a preallocated buffer. The largest gains are on 64-bit-word algorithms (SHA3-512 16.5x over noble-hashes, xxHash64 378x over xxhashjs, which emulates 64-bit math), consistent with wasm's native i64 arithmetic; there is no WASM SIMD or threading (the README lists both as future plans).

## Compared with alternatives

Pick hash-wasm when one dependency must cover many algorithms, from MD5 to Argon2, with streaming and resumable state; pick xxhash-wasm when xxHash alone is needed (equal at 1 MB), @phi-ag/argon2 for faster Argon2, and awasm-noble or blake3-jit when BLAKE3 throughput is the only concern, since hash-wasm publishes no BLAKE3 number.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (each wasm binary is embedded as base64 in its JS module) |
| **Minimum toolchain** | Chrome 57+, Safari 11+, Firefox 53+, Edge 16+, Node.js 8+, Deno 1+ per the README; rebuilding the wasm needs Docker with Alpine's clang and lld (alpine:3.20.3 at HEAD) |
| **Platforms** | any WebAssembly host (wasm32 scalar code, no SIMD); not Internet Explorer |
| **Thread safety** | single-threaded JS API: one-shot functions share one cached wasm instance per algorithm, createXXX() hashers hold separate state; usable in Web Workers with one set of instances per worker |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness details behind the README tables (author's hash-wasm-benchmark app): it measures both the shorthand md5() and createMD5() variants but the README shows one hash-wasm row per table without saying which; the xxhash-wasm row wraps h64Raw in an async function inside addSync and allocates a Buffer and a BigInt per call, which inflates hash-wasm's 2.1x lead at 32 bytes; bench.js addAsync batches calls as Promise.all([array]), so the batch is never awaited (harmless here because these libraries finish their work synchronously or in microtasks, but it would mis-time a truly asynchronous function such as WebCrypto); the SHA3-512 table labels jsSHA 3.2.0 although the app pins jssha 3.3.1. The tables measure the npm 4.10.0 build, not the shipped 4.12.0.
- Strings are hashed as their UTF-8 bytes with no normalisation, so visually equal strings (precomposed vs combining characters) hash differently; normalize() first, as the README advises.
- One-shot functions return Promises even though the work is synchronous once the module is cached; createXXX() instantiates a new wasm module each call, so call it once and reuse it with init() rather than creating hashers in a loop.
- save() output contains plaintext input bytes and is tagged with a hash of the exact wasm build, so load() throws across hash-wasm versions; users report Chrome running hash-wasm roughly 9-10x slower while DevTools is open (issue #47, open).

## Known shortcomings

- README numbers match the Daninet/hash-wasm-benchmark harness (digests checked before timing; flags in scripts/Makefile-clang; measured 4.10.0 built in alpine:3.18.4, not 3.20.3), but there is no Node crypto or WebCrypto baseline, XXHash64 ties xxhash-wasm, and the run is first-party. Filed under wasm-libraries-and-apps.
- Enricher: bench.js's Promise.all([array]) never awaits the batch (benign here); the async xxhash-wasm wrapper inflates the 2.1x lead at 32 B; the README shows one hash-wasm row of unclear shorthand; the SHA3 table labels jsSHA 3.2.0 while the app pins 3.3.1; no WebCrypto or node:crypto baseline (MeasureThat snippets put WebCrypto SHA-256 about 2-4x faster); open issues: Firefox memory growth #69, CSP #3.

## Caveats and trade-offs

First-party numbers from the author's benchmark app (Daninet/hash-wasm-benchmark; the live github.io app was not reachable). The harness checks every library's digest against hash-wasm's output during warm-up, calibrates a per-call divisor, then times about 1 s per scenario (bench.js). The README table is for hash-wasm 4.10.0 (the version the benchmark app pins), while the latest release is 4.12.0. Neither Node's native crypto module (OpenSSL) nor the browser's native WebCrypto digest is in the comparison, so this does not show it beats native hashing. The XXHash64 1 MB figure (15 989 MB/s) is about equal to xxhash-wasm 1.0.2 (15 929 MB/s); its win there is only over pure-JS xxhashjs. No WASM SIMD. Project is C compiled to wasm, so it fits the wasm-libraries-and-apps category (baseline: the JS equivalent in-browser) better than assemblyscript-and-wasm-langs.

Each algorithm ships as a separate base64-embedded WASM binary, so there is a WASM instantiation cost on first use. Async init for the streaming createXXXX() API. Browsers and Node.js only.

## Maintenance

Stale since 4.12.0 (2024-11-19) with 9 open issues (Firefox memory growth #69, CSP #3, a WASM SIMD request #66), but MIT-licensed, dependency-free, 1.2k stars and small per-algorithm modules, so it is a safe pick for hashing in JS runtimes when native crypto is unavailable or lacks the algorithm.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmark tables (Chrome v131, Ryzen 9 7900X) compare hash-wasm 4.10.0 against pure-JS hash libraries (spark-md5, crypto-js, noble-hashes, jsSHA, node-forge, xxhashjs) and other wasm packages; the harness is public in Daninet/hash-wasm-benchmark (src/benchmark/bench.js plus per-algorithm \*.worker.js, package.json pins every competitor version) and the wasm build flags are in scripts/Makefile-clang (clang from a pinned Alpine Docker image). Code, compiler, flags and CPU model are all stated.
- **Verifier notes:** All claimed figures match the README tables exactly (MD5 850.31 vs spark-md5 171.73 and crypto-js 46.71 MB/s at 1 MB; SHA256 426.16 vs noble-hashes 110.02; SHA3-512 234.40 vs 14.19; XXHash64 15 989 vs xxhashjs 42.26; PBKDF2-SHA512 588 vs crypto-js 29 ops; Argon2id 438 vs argon2-browser 213 ops). Metadata checked: MIT, 1.2k stars, not a fork, last commit 2024-11-19 (stale). Shortcomings: no native-crypto/WebCrypto baseline, XXHash64 ties xxhash-wasm, first-party run; consider a category override to wasm-libraries-and-apps.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-04 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Daninet/hash-wasm>
  - <https://github.com/Daninet/hash-wasm/commits/master>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/Makefile-clang>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/Dockerfile>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/v4.10.0/scripts/Makefile-clang>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/v4.10.0/scripts/Dockerfile>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/LICENSE>
  - <https://github.com/Daninet/hash-wasm-benchmark>
  - <https://github.com/Daninet/hash-wasm-benchmark/tree/master/src>
  - <https://github.com/Daninet/hash-wasm-benchmark/tree/master/src/benchmark>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/package.json>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/bench.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/md5.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/sha256.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/xxhash64.worker.js>
- **Sources the enricher read:**
  - <https://github.com/Daninet/hash-wasm>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/v4.9.0/README.md>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/v4.10.0/README.md>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/v4.11.0/README.md>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/Makefile-clang>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/Dockerfile>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/WASMInterface.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/md5.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/argon2.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/xxhash64.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/mutex.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/util.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/lib/index.ts>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/src/md5.c>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/src/sha256.c>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/src/hash-wasm.h>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm/HEAD/src/xxhash64.c>
  - <https://github.com/Daninet/hash-wasm/commits/master>
  - <https://github.com/Daninet/hash-wasm/issues>
  - <https://github.com/Daninet/hash-wasm/issues/3>
  - <https://github.com/Daninet/hash-wasm/issues/47>
  - <https://github.com/Daninet/hash-wasm/issues/66>
  - <https://github.com/Daninet/hash-wasm/issues/69>
  - <https://github.com/Daninet/hash-wasm-benchmark/tree/master/src/benchmark>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/package.json>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/bench.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/md5.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/sha1.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/sha256.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/sha3.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/xxhash64.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/pbkdf2.worker.js>
  - <https://raw.githubusercontent.com/Daninet/hash-wasm-benchmark/HEAD/src/benchmark/argon2id.worker.js>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/daninet/hash-wasm`) · [data/wave13/enrich/raw/github_com_daninet_hash_wasm.json](../../../data/wave13/enrich/raw/github_com_daninet_hash_wasm.json) (enrichment confidence 0.74)

</details>
