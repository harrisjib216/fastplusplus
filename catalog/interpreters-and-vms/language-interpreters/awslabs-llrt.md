# LLRT (Low Latency Runtime)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (embeds the QuickJS C engine)` · `Apache-2.0` · 🟢 active

> AWS Labs JavaScript runtime for Lambda (Rust plus QuickJS-NG, no JIT) that cuts Node.js 20 cold starts.

| | |
|---|---|
| **Beats** | Node.js 20 (V8) on AWS Lambda |
| **Claimed result** | README screenshots (2024-01-31): p50 Lambda cold start 64.16 ms vs 1511.93 ms, HTTP round trip 235.61 vs 1719.00 ms against Node 20; not like for like (see caveats). Independent user report, issue #1166: LLRT v0.7.0-beta at 128 MB p50 HTTP 275 ms vs Node 22 at 512 MB 409-681 ms (about 1.5-2.5x). ahaoboy CI v8-v7 throughput: LLRT 972 vs Node 40333 on ubuntu (about 41x lower). |
| **Workload** | AWS Lambda DynamoDB Put function (example/functions/src/v3-lib.mjs), ARM, 128MB: 64 cold starts and 20000 warm starts, percentiles p0-p100 of Lambda-reported Init Duration plus Function Duration and of HTTP round-trip time; results only as two PNG screenshots in the README. |
| **Metric** | startup |
| **Hardware** | AWS Lambda ARM, 128MB memory (no CPU model) |
| **Adoption** | 8.8k stars (AWS Labs) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/awslabs/llrt) · [benchmark](https://github.com/awslabs/llrt) |

## Verdict

AWS Labs' own load test of a DynamoDB Put Lambda (ARM, 128MB, 64 cold starts, 20000 warm starts), shown only as two README screenshots from January 2024, gives cold-start p50 Init+Function duration 64.16 ms for LLRT vs 1511.93 ms for Node.js 20 (about 23.6x) and HTTP round trip 235.61 vs 1719.00 ms (about 7.3x); warm p50 is 14.94 vs 33.20 ms (Lambda) and 43.72 vs 62.08 ms (HTTP), all ratios derived from page data. No CPU model, Node.js deployment variant or harness code is published, and the '2x lower cost' claim has no numbers.

## Use it when

- Short-lived, I/O-bound Lambda functions (DynamoDB/S3/SQS/SNS calls, validation, authorization, small data transformations) where cold-start latency dominates.
- Low-memory Lambda configurations such as 128MB on ARM, which is where the published comparison was run (cold-start p50 Init+Function 64 ms vs 1512 ms for Node.js 20).
- Functions that use AWS SDK v3 clients included in the std-sdk or full-sdk builds, so the SDK comes precompiled with the runtime instead of being bundled or loaded from disk.
- Teams willing to run their code through LLRT's built-in Jest-like test runner (llrt test) before deploying, since compatibility must be checked per function.

## Skip it when

- CPU-heavy work (large data processing, Monte Carlo simulation, loops with hundreds of thousands to millions of iterations): the README says JIT runtimes win there, and independent ahaoboy/js-engine-benchmark CI (V8 v7 suite, 2026) scores LLRT 0.9.0-beta 972 vs Node.js 26.10.0 40333 on ubuntu (about 41x lower, derived from page data), 949 vs 37405 on macOS arm64 and 609 vs 35121 on Windows; LLRT also trails Bellard's QuickJS 2026.06.04 (1217 on ubuntu).
- Code that needs node:http/https/tls servers or clients, worker_threads, vm, cluster, node:test, readline, querystring or WebAssembly; these are missing or only planned.
- Production systems that need a stable API: the README calls LLRT experimental and intended only for evaluation, and every release so far is a beta (latest v0.9.0-beta, 2026-09-06).
- Unbundled node_modules or TypeScript run directly: LLRT requires bundling, minification and ahead-of-time transpilation to ES2023.
- Windows on ARM (the Makefile marks aarch64 Windows as not yet supported).

## How it is fast

It runs on QuickJS-NG (via the rquickjs 0.14 crate), a small bytecode interpreter with no JIT, so there is no JIT warm-up or large engine to initialise. At build time llrt_core/build.rs precompiles the bundled JS (stdlib and AWS SDK clients) to QuickJS bytecode, stores it in a phf perfect-hash map inside the binary and zstd-compresses it with a trained dictionary, so startup loads bytecode instead of parsing JS. Hashing and XML parsing used by the SDK are native Rust, the binary is a static musl build with LTO, opt-level 3, codegen-units 1 and the snmalloc allocator, and LLRT_SDK_CONNECTION_WARMUP (on by default) opens SDK TLS connections in parallel during init.

## Compared with alternatives

None of the catalogued siblings runs JavaScript: PyPy, GraalPy, LuaJIT, YJIT and TruffleRuby buy peak throughput with a JIT, while LLRT gives up the JIT to win cold start, so pick it only for JavaScript Lambda handlers where startup and memory dominate and pick a JIT runtime (or plain Node.js) for long-running or compute-bound code.

## Integration

| | |
|---|---|
| **Form** | standalone runtime binary (Lambda custom-runtime bootstrap zip, Lambda layer, container binary, or local CLI); also a Rust workspace of crates |
| **Dependencies** | none at deploy time (static musl binary with embedded SDK bytecode); building from source needs a nightly Rust toolchain, zig and cargo-zigbuild, make, zstd, Node.js with corepack/yarn and git submodules |
| **Minimum toolchain** | Rust nightly-2026-08-26 (pinned in the Makefile) with cargo-zigbuild; prebuilt binaries need no toolchain |
| **Platforms** | Lambda arm64 and x86-64 (provided.al2023); Linux musl x86-64/aarch64, macOS x86-64/arm64 and Windows x86-64 builds; Windows arm64 not supported |
| **Thread safety** | JavaScript runs on a single engine thread with an async (tokio) event loop; worker_threads is not available |
| **Drop-in for the baseline** | partial — same handler signature and Node-style module names, but only a fraction of Node.js APIs, ES2023 only, and dependencies must be bundled for the browser platform |

## Gotchas

- Harness gap: the README labels both screenshots 'DynamoDB Put, ARM, 128MB (example/functions/src/v3-lib.mjs)', but the repo's CDK stack (example/infrastructure/src/index.ts) deploys v3-lib.mjs only for LLRT; its Node.js 20 DynamoDB functions use v3.mjs or v3-mono.mjs with the SDK either bundled (esbuild, minified) or left to the Lambda-provided copy, and the README does not say which Node.js variant produced the 1512 ms row. The load generator that printed the percentile tables is not in the repo.
- Independent user report (issue #1166, open): LLRT v0.7.0-beta at 128MB had p50 HTTP 275 ms vs 409-681 ms for four Node.js 22 SDK setups at 512MB (about 1.5x to 2.5x, derived from page data), far less than the README's 7.3x HTTP gap; the same user measured LLRT's cold-start overhead outside the Lambda-reported duration about 50 ms higher than Node.js 22 (193 vs 144 ms), so Init Duration alone flatters LLRT. The issue also notes binaries grew 2+ MB since the January 2024 screenshots, and maintainers had not replied.
- The cold-start number includes LLRT-specific work beyond the engine: the AWS SDK ships as precompiled bytecode in the binary and SDK TLS connections are pre-opened during init (LLRT_SDK_CONNECTION_WARMUP=1 by default), so the gain is runtime packaging plus a no-JIT engine, not QuickJS speed alone.
- Issue #959: a user saw \~200 ms LLRT function time but \~750 ms end-to-end, similar to Node.js, and suspected a Cognito RSA authorizer in front of the function; gains shrink when other layers dominate latency. Default GC threshold is 20MB (LLRT_GC_THRESHOLD_MB) and only TLS 1.2 and HTTP/1.1 are on by default.

## Known shortcomings

- Vendor first-party README screenshots only, committed 2024-01-31 and never refreshed, harness not in the repo; cold-start-only win (p50 Lambda 64.16 vs 1511.93 ms, HTTP round trip 235.61 vs 1719.00 ms), experimental and not Node-compatible, and the '2x cost' claim has no numbers. Rust wrapper around QuickJS.
- Enricher: the README labels both screenshots v3-lib.mjs, but example/infrastructure/src/index.ts deploys v3-lib.mjs only for LLRT while the Node 20 functions run v3.mjs or v3-mono.mjs (SDK bundled or Lambda-provided), the load generator is not in the repo, and the cold start counts LLRT-only tricks (SDK precompiled to zstd bytecode, TLS warmup on by default). A user report in issue #1166 measures LLRT v0.7.0-beta at 128 MB p50 HTTP 275 ms against Node 22 at 512 MB 409-681 ms, about 1.5-2.5x rather than 7.3x. The engine is quickjs-ng via rquickjs 0.14, not Bellard QuickJS.

## Caveats and trade-offs

Only first-party numbers, shown as screenshots committed once on 2024-01-31 ('Add perf screenshots') and never refreshed, so they reflect the launch-era LLRT against Node.js 20, not current versions of either. The win is cold start, where a no-JIT QuickJS runtime with a bundled SDK wins by design; warm p50 HTTP latency is only about 1.4x better (derived from page data) and CPU-heavy code would favor V8's JIT. The load-test harness that produced the tables is not in the repo (benchmarks/ holds the PNGs, fetch-streaming.mjs and a v8-v7 suite). The README calls LLRT experimental and 'intended only for evaluation purposes', and says it is not a drop-in Node.js replacement (many node: modules missing, e.g. http, tls, worker_threads). Written in Rust on QuickJS, so it is a runtime to adopt, not a C++ library. The '2x lower cost' claim has no published numbers. [retier] Cold-start-only win from vendor screenshots never refreshed since 2024-01-31; the LLRT function runs v3-lib.mjs while the Node 20 functions run v3.mjs or v3-mono.mjs (example/infrastructure/src/index.ts), the load generator is not published, and LLRT precompiles the SDK to zstd bytecode and warms TLS by default. Engine is quickjs-ng via rquickjs 0.14 (no JIT): throughput about 41x below Node on ahaoboy CI. Experimental, not Node-compatible.

No JIT, so peak compute is far slower than V8 and not recommended for compute-heavy work; partial Node.js API compatibility; ES2023 only; README marks it experimental and for evaluation purposes.

## Maintenance

Actively developed (last commit 2026-10-05, v0.9.0-beta released 2026-09-06, Apache-2.0) but still labelled experimental and evaluation-only, and the headline benchmark has not been refreshed since January 2024 despite an open request to rerun it (issue #1166).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party (AWS Labs) README screenshots of a cold/warm Lambda load test against Node.js 20 on ARM 128MB; the test function (example/functions/src/v3-lib.mjs) is public but the load-test harness, CPU model and build flags are not, so it falls short of A and there is no independent measurement.
- **Verifier notes:** README claim and screenshot numbers verified; tier C stays (vendor first-party, harness not public, no CPU model). Main shortcomings: 2024 screenshots never refreshed, cold-start-only win, experimental and not Node-compatible; metadata (Apache-2.0, 8.8k stars, last commit 2026-10-05, active) checked and correct.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/awslabs/llrt>
  - <https://github.com/awslabs/llrt/commits>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/README.md>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/benchmarks/llrt-ddb-put.png>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/benchmarks/node20-ddb-put.png>
  - <https://github.com/awslabs/llrt/tree/main/benchmarks>
  - <https://github.com/awslabs/llrt/commits/main/benchmarks/llrt-ddb-put.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/README.md>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/example/functions/src/v3-lib.mjs>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/example/functions/src/v3.mjs>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/example/functions/src/v3-mono.mjs>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/example/functions/build.mjs>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/example/functions/package.json>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/example/infrastructure/src/index.ts>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/example/infrastructure/package.json>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/llrt/Cargo.toml>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/llrt_core/Cargo.toml>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/llrt_core/build.rs>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/lambda-server.js>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/benchmarks/llrt-ddb-put.png>
  - <https://raw.githubusercontent.com/awslabs/llrt/HEAD/benchmarks/node20-ddb-put.png>
  - <https://github.com/awslabs/llrt/tree/main/example>
  - <https://github.com/awslabs/llrt/tree/main/example/infrastructure>
  - <https://github.com/awslabs/llrt/tree/main/example/infrastructure/src>
  - <https://github.com/awslabs/llrt/issues?q=is%3Aissue+slow+OR+performance+OR+memory+leak>
  - <https://github.com/awslabs/llrt/issues/959>
  - <https://github.com/awslabs/llrt/issues/1166>
  - <https://github.com/awslabs/llrt/releases>
  - <https://github.com/awslabs/llrt/releases/tag/v0.9.0-beta>
  - <https://github.com/DelSkayn/rquickjs>
  - <https://crates.io/api/v1/crates/rquickjs-sys>
  - <https://raw.githubusercontent.com/ahaoboy/js-engine-benchmark/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/awslabs/llrt`) · [data/wave12/enrich/raw/github_com_awslabs_llrt.json](../../../data/wave12/enrich/raw/github_com_awslabs_llrt.json) (enrichment confidence 0.75)

</details>
