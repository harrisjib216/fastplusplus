# fast-md5-web

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust compiled to WebAssembly with a TypeScript Web Worker pool` · `MIT` · 🟢 active

> Browser MD5 library: RustCrypto md-5 in WebAssembly plus a Web Worker pool, claimed 8-16x faster than spark-md5.

| | |
|---|---|
| **Beats** | spark-md5 (pure-JavaScript MD5) |
| **Claimed result** | README: '\~8x faster than spark-md5' in single-thread mode and '\~16x faster' with multi-thread workers ('in specific scenarios'). The only data is a screenshot of the example app (docs/a3d25c4789a9937d8a1fc76c12b61152.png): 174 files, 100.0% hash match, SparkMD5 total 109,271.50 ms vs Fast-MD5-Web worker pool 6,329.50 ms, labelled a 1626.4% improvement (17.3x, derived from page data). No measurement is shown for the 8x single-thread claim. README also: a 10 MB file with 4 workers takes \~151 ms with SharedArrayBuffer vs \~200 ms without (\~25% faster). |
| **Workload** | Browser MD5 of a user-selected set of 174 files (sizes unstated, not in the repo) in the example Vue app: SparkMD5 on the main thread reading 2 MB FileReader chunks for all files under Promise.all, then fast-md5-web's Md5CalculatorPool with navigator.hardwareConcurrency workers; hashes cross-checked. |
| **Metric** | throughput |
| **Compiler and flags** | RustCrypto md-5 0.10.6 via wasm-bindgen, [profile.release] opt-level = "s" (wasm/Cargo.toml); Rust, wasm-bindgen and browser versions for the screenshot run unstated |
| **Adoption** | 98 stars |
| **Last commit** | 2026-03-15 |
| **Links** | [repository](https://github.com/XueHua-s/fast-md5-web) · [benchmark](https://github.com/XueHua-s/fast-md5-web) |

## Verdict

The only data is one screenshot from the repo's Vue example app: 174 user-selected files, all hashes matching, spark-md5 on the main thread with 2 MB FileReader chunks 109,271.50 ms vs the fast-md5-web pool 6,329.50 ms (17.3x, derived from page data), with hardware, browser, core count and file sizes unstated; the README's 8x single-thread figure and the SharedArrayBuffer 151 vs 200 ms example have no published measurement.

## Use it when

- Browser apps that checksum many user-selected files before upload (deduplication, resumable or instant uploads to object storage that wants an MD5) and can spread them over several cores.
- When hashing must stay off the UI thread and you want a ready-made pool with per-file timeouts, progress callbacks, priorities and cancellation rather than writing your own worker plumbing.
- Sites that already serve Cross-Origin-Opener-Policy: same-origin and Cross-Origin-Embedder-Policy: require-corp, so the SharedArrayBuffer path is available (but see the large-file race in gotchas).
- Interop with existing MD5-based APIs where the checksum format is fixed; it is a checksum, not a security primitive.

## Skip it when

- Anything security-related (signatures, password hashing, integrity against an adversary): MD5 is not collision resistant.
- Hashing one file or a few small buffers: the pool brings no speedup there and the 8x single-thread claim has no published measurement; hash-wasm publishes a reproducible MD5 throughput table.
- Large files (above chunkSize) with SharedArrayBuffer enabled until the slot-overwrite race described in gotchas is fixed; disable shared memory or cross-check results.
- Node.js servers: node:crypto is native and faster; this package's pool calls new Worker(..., {type: 'module'}) and navigator.hardwareConcurrency, has no worker_threads code despite the README, and WasmInit() by default fetches the .wasm from a URL relative to import.meta.url.
- CommonJS projects or toolchains that cannot resolve the worker and wasm files next to dist/ (issue #8 was a Vite import-resolution failure).

## How it is fast

The MD5 compression function is the RustCrypto md-5 0.10.6 crate compiled to WebAssembly with wasm-bindgen (release profile opt-level "s", a 59 KB .wasm in the npm package), so the 32-bit add/rotate rounds run as wasm i32 ops instead of JavaScript number arithmetic. Most of the headline speedup comes from parallelism: the pool runs one file per worker, sized by default to navigator.hardwareConcurrency, and a SharedArrayBuffer allocator avoids structured-clone copies when cross-origin isolation is on. MD5 is sequential within one input, so a single large file is hashed by one worker and gains nothing from the pool beyond keeping the UI thread free.

## Compared with alternatives

Against hash-wasm, which publishes a reproducible single-thread MD5 table (850.31 MB/s vs spark-md5 171.73 MB/s on 1 MB) and covers many algorithms, pick fast-md5-web only when you want its ready-made multi-file worker pool with progress, priority and timeouts and will verify its output; for one file, Node.js or audited numbers, hash-wasm (run in your own worker if needed) is the safer choice.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | uuid 11.1.0 at runtime; ships dist/index.js, dist/md5-worker.js and wasm/pkg (wasm-pack --target web output), which the bundler must serve at their relative URLs |
| **Minimum toolchain** | ES2020 ESM consumers; ES module Worker support in the browser; building from source needs Rust, wasm-pack and pnpm (Node &gt;= 18 per engines) |
| **Platforms** | Browsers (README lists Chrome 68+, Firefox 79+, Safari 15.2+ for SharedArrayBuffer, with HTTPS and COOP/COEP headers); Deno via npm: specifier per README; Node.js only for the direct Md5Calculator with manually supplied wasm bytes |
| **Thread safety** | Each worker owns one Md5Calculator; incremental sessions are keyed by task id in a thread_local map inside the wasm module; the pool object is meant to be driven from one thread; not otherwise documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Large-file race (code reading, not reproduced): in SharedArrayBuffer mode processLargeFile writes every chunk into the same single slot, posts calculate_chunk, and moves on after only a microtask yield, with no acknowledgement from the worker; the worker copies the slot when it dequeues the message, so whenever file reads outpace hashing (or the worker is still in WasmInit) a later chunk overwrites an unread one and the MD5 is silently wrong. The same design is in npm 1.1.2 and repo HEAD, and the only large-file e2e test hashes a 300 MB file filled with the single byte 17, where every chunk is identical, so it cannot detect the race.
- The published 1.1.2 worker handles messages with an async onmessage and no queue, so chunks of a stream started on a fresh worker can run before WasmInit finishes and fail with 'Stream state not found'; the serial-queue fix exists only in unpublished HEAD (March 2026), which also adds a postinstall that runs pnpm install in the example folder and is not in the package's files list.
- Harness flaws behind the 16-17x: the example app times a pool of navigator.hardwareConcurrency workers against spark-md5 running single-threaded on the main thread, always runs spark-md5 first (cold reads) and reports one run on 174 undisclosed files with no hardware or browser; it also configures memorySize 6400 MiB while the comment says 64MB.
- md5Length 16 returns the first 16 hex characters (64 bits; the README calls it a '128-bit half'), not the middle 16 that substr(8, 16)-style '16-bit MD5' tools return; small-file SharedArrayBuffer allocations are released only on error or timeout, so the shared region fills and later files silently fall back to copying; calculate_md5_async 'yields' with an already resolved promise, which does not let the browser render, so calling it on the main thread still blocks.

## Known shortcomings

- Screenshot numbers (109,271.50 vs 6,329.50 ms, 17.3x derived) compare a worker pool against single-threaded spark-md5 in a fixed run order; the 8x single-thread claim is unmeasured; a wrapper over the RustCrypto md-5 crate built at opt-level s.
- Correctness race (code reading, not reproduced) in the SharedArrayBuffer streaming path: every chunk is written into one shared slot without waiting for a worker acknowledgement, so a later chunk can overwrite an unread one and yield a silently wrong MD5; present in npm 1.1.2 and HEAD, and the only large-file e2e test hashes 300 MB of a single byte value so it cannot see it. 1.1.2 also has a 'Stream state not found' worker race (fixed only in unpublished HEAD), small-file shared allocations leak, md5Length 16 returns the first 16 characters rather than the middle 16, and the example allocates a 6400 MiB SharedArrayBuffer where its comment says 64 MB. The only evidence is a first-party screenshot dominated by worker parallelism.

## Caveats and trade-offs

Screenshot only: no hardware, browser, core count, file sizes or repetition; the 174 input files are not in the repo (example/test-fast-md5/public/test-files holds small fixtures). The harness compares a worker pool sized to navigator.hardwareConcurrency against single-threaded SparkMD5 on the main thread, so the 16-17x is mostly parallelism, not per-core speed; SparkMD5 always runs first, so the second run may benefit from warm file caches. The 8x single-thread claim has no published measurement. The MD5 core is the RustCrypto md-5 crate built with opt-level 's' (size); the project is a wasm-bindgen and worker-pool wrapper around it. The listed hash-wasm (wave 13) also benchmarks MD5 against spark-md5 and was not compared here. The README calls it 'possibly the fastest'. [retier] Screenshot only: no hardware, browser, core count, file sizes or repetition; the 174 input files are not in the repo. The harness compares a worker pool sized to navigator.hardwareConcurrency against single-threaded SparkMD5 on the main thread, so the 16-17x is mostly parallelism; SparkMD5 always runs first. The 8x single-thread claim has no published measurement. Correctness race (code reading): in SharedArrayBuffer streaming mode every chunk is written into one shared slot without waiting for a worker acknowledgement, so a later chunk can overwrite an unread one and give a silently wrong MD5 (npm 1.1.2 and HEAD; the only large-file e2e test hashes 300 MB of one byte value and cannot see it). 1.1.2 also has a 'Stream state not found' worker race fixed only in unpublished HEAD; small-file shared allocations leak; md5Length 16 returns the first 16 characters, not the middle 16; the example allocates a 6400 MiB SharedArrayBuffer.

Worker pool and SharedArrayBuffer path (cross-origin isolation headers) give the 16x; ESM-only package; MD5 is not collision resistant.

## Maintenance

Active (last commit 2026-03-15, MIT, 98 stars) but npm latest is still 1.1.2 from 2025-11-27, so HEAD's worker-queue fix is unpublished; evidence is a single first-party screenshot dominated by parallelism, and the shared-memory large-file path has an unguarded slot-overwrite race that its fixed-byte test file cannot catch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README ratios plus one screenshot from the repo's example app (example/test-fast-md5/src/App.vue, public); no hardware, browser, file set or run count, and the 8x single-thread figure has no data at all.
- **Retiered** C to D: Enricher: the only evidence is a first-party screenshot (no hardware, browser, file sizes or repetition) dominated by worker parallelism, the single-thread 8x has no measurement at all, and the shared-memory streaming path can silently produce wrong MD5 digests (unacknowledged slot overwrite, present in npm 1.1.2 and HEAD). No valid like-for-like measurement: D.
- **Verifier notes:** Record accurate in substance; added the screenshot's numbers (17.3x for the worker pool, derived) and the harness flaws. Shortcomings to record: multi-thread pool versus single-thread spark-md5, fixed run order, undisclosed hardware/browser/files, 8x single-thread claim unmeasured, thin wrapper over RustCrypto md-5. Metadata checked: MIT, 98 stars, last commit 2026-03-15, not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-85 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/XueHua-s/fast-md5-web>
  - <https://github.com/XueHua-s/fast-md5-web/commits>
  - <https://github.com/XueHua-s/fast-md5-web/tree/main/example/test-fast-md5>
  - <https://github.com/XueHua-s/fast-md5-web/tree/main/example/test-fast-md5/src>
  - <https://github.com/XueHua-s/fast-md5-web/tree/main/example/test-fast-md5/e2e>
  - <https://github.com/XueHua-s/fast-md5-web/tree/main/example/test-fast-md5/scripts>
  - <https://github.com/XueHua-s/fast-md5-web/tree/main/example/test-fast-md5/public/test-files>
  - <https://github.com/XueHua-s/fast-md5-web/tree/main/wasm>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/README.md>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/docs/a3d25c4789a9937d8a1fc76c12b61152.png>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/package.json>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/src/App.vue>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/package.json>
- **Sources the enricher read:**
  - <https://github.com/XueHua-s/fast-md5-web/commits/main>
  - <https://github.com/XueHua-s/fast-md5-web/issues?q=is%3Aissue>
  - <https://github.com/XueHua-s/fast-md5-web/tree/main/example/test-fast-md5/e2e>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/README.md>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/package.json>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/tsconfig.json>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/tsup.config.ts>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/scripts/postinstall.mjs>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/src/md5-worker.ts>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/src/types.ts>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/src/shared-memory-allocator.ts>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/wasm/src/utils.rs>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/README-zh.md>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/src/App.vue>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/package.json>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/vite.config.ts>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/e2e/api-comprehensive.test.ts>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/public/test-files/manifest.json>
  - <https://raw.githubusercontent.com/XueHua-s/fast-md5-web/HEAD/example/test-fast-md5/scripts/generate-fixtures.mjs>
  - <https://registry.npmjs.org/fast-md5-web>
  - <https://registry.npmjs.org/fast-md5-web/-/fast-md5-web-1.1.2.tgz>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/xuehua-s/fast-md5-web`) · [data/wave13/enrich/raw/github_com_xuehua_s_fast_md5_web.json](../../../data/wave13/enrich/raw/github_com_xuehua_s_fast_md5_web.json) (enrichment confidence 0.7)

</details>
