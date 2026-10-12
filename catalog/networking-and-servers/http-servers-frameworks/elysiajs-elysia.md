# Elysia (Bun)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `TypeScript` · `MIT` · 🟢 active

> Bun-first TypeScript web framework; ties actix-web on a hello-world GET because Bun serves that route natively.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop commit f673364): elysia-bun (Elysia 1.4 on Bun) 172,228 / 174,958 / 173,877 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 0.96x / 1.04x / 1.06x (derived from page data). The two earlier snapshots (older harness method, unchanged Elysia/Bun/actix configs) show elysia-bun slower at every level: commit 0fccb1d (2026-09-20, on master) 113,672 / 98,769 / 97,465 vs 115,638 / 102,329 / 99,835 = 0.98x / 0.97x / 0.98x; commit 8ae370a (2026-09-18) 116,632 / 99,157 / 95,487 vs 117,177 / 100,171 / 98,722 = 0.995x / 0.99x / 0.97x (derived from page data) |
| **Workload** | the-benchmarker/web-frameworks run of 2026-09-24 (data.json updated_at 2026-09-24 06:59 UTC, develop commit f673364): GET / (empty body) on the suite's minimal per-framework app, load from `zrk --plain --closed` (a closed loop over keep-alive connections, not wrk) after a 5 s warmup at c=50, 15 s runs at concurrency 64/256/512, server container on \~4 cores (server_cpu_cores \~3.95, saturation \~0.99) with the load generator on separate cores; values are averages of the stored samples; Elysia 1.4 on Bun 1.4, one Bun process per visible CPU via cluster.ts |
| **Metric** | throughput |
| **Hardware** | Single host per data.json: 16 CPUs, 7,733,008 kB RAM, Linux 7.2.6-200.fc44.x86_64 (x86_64); the cpu_name 'M1 Eight-Core Processor' is a string hard-coded in .tasks/db.rake, not a measured CPU model; server container used \~3.95 cores; run dated 2026-09-24 |
| **Compiler and flags** | Bun 1.4 runtime (oven/bun:1.4-slim image), `bun install --production`, started with `bun run cluster.ts`, which spawns one `bun ./app.ts` process per navigator.hardwareConcurrency; no build step. Baseline: actix-web 4.8 built with Rust 1.98 (rust:1.98-slim) `cargo build --release`, opt-level=3, lto=true, codegen-units=1, panic=abort |
| **Adoption** | 19.2k stars |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/elysiajs/elysia) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks run of 2026-09-24 (commit f673364; empty GET /, zrk closed-loop keep-alive, server limited to about 4 of 16 x86-64 cores on Linux 7.2, CPU model not recorded), Elysia 1.4 on Bun 1.4 (one process per CPU) did 172,228 / 174,958 / 173,877 req/s at c=64/256/512 vs actix-web 4.8 (Rust 1.98, LTO, opt-level 3) at 179,203 / 168,270 / 163,415, i.e. 0.96x-1.06x, and was 0.97x-0.995x in the two earlier snapshots: a tie. The Elysia route is a constant, so Bun served a pre-built Response without running Elysia code; the suite's raw-Bun entry, which uses a JavaScript callback per request, did 145,897 req/s at c=512.

## Use it when

- You already run Bun and want the lowest-overhead typed TypeScript framework: in the 2026-09-24 run elysia-bun did 173,877 req/s at c=512 vs hono-deno 130,540, fastify 68,128 and express 42,586.
- Fixed-content endpoints (health checks, version strings, redirects) that Elysia can hand to Bun as static responses.
- TypeScript teams that want one schema to drive runtime validation, OpenAPI docs and a typed frontend client without a codegen step.
- Linux hosts where you can run one Bun process per core behind SO_REUSEPORT (cluster mode).

## Skip it when

- As a reason to move off actix-web: on this suite it ties (0.96x-1.06x across c=64-512, 0.97x-0.995x in two earlier snapshots), and actix had lower p99 at c=64 (0.4 ms vs 0.7 ms).
- On Node.js: the same app through `@elysiajs/node` did 48,128 req/s at c=512, about 0.29x actix and 0.28x elysia-bun.
- Handler-heavy services (DB calls, JSON bodies, validation): the benchmark route is a pre-built static response, so it gives no evidence about Elysia's per-request code path.
- Very large typed APIs where editor speed matters: open issue #1031 reports 10-20 s IntelliSense delays; one reporter has 202 plugins and 1,168 endpoints.
- Large multipart uploads through the built-in parser: open issue #1744 reports a memory leak on 1.4.22, and the form-data normalizer was quadratic in the number of fields until 1.4.29 (CVE-2026-56669).

## How it is fast

On Bun, `listen()` hands every route to `Bun.serve({ routes })`, Bun's native router (built on uWebSockets' tree router). A handler given as a constant value, such as `.get('/', '')`, is turned into a pre-built `Response` (`nativeStaticResponse`, on by default) that Bun dispatches with zero allocation and without running any JavaScript per request. For function handlers, Elysia's JIT 'AOT' step (sucrose) reads each handler's source with `Function.prototype.toString()` to infer which of query/headers/body/cookie it uses, then emits a specialised handler compiled with `new Function()` that skips unused parsing. `SO_REUSEPORT` is on by default, so one Bun process per core can share a port.

## Compared with alternatives

Pick Elysia over hyper, Jooby or ActiveJ only when the service must be TypeScript on Bun; all four sit within about -4% to +9% of actix on this route. If raw JavaScript throughput is the only goal, fulmine.js posted more (203,996 req/s at c=512) in the same run.

## Integration

| | |
|---|---|
| **Form** | module (npm package `elysia`, ESM and CJS builds) |
| **Dependencies** | cookie, exact-mirror, fast-decode-uri-component, memoirist; peers @sinclair/typebox &gt;=0.34 &lt;1, file-type &gt;=20, openapi-types &gt;=12, exact-mirror; optional peers @types/bun &gt;=1.2, typescript &gt;=5.0; Node needs the @elysia/node adapter |
| **Minimum toolchain** | Bun (peer @types/bun &gt;=1.2; the benchmark used Bun 1.4); TypeScript &gt;=5.0 for type-checking; package.json has no engines field |
| **Platforms** | Wherever Bun runs (Elysia does not list platforms); Node.js via adapter; Cloudflare Workers adapter is experimental; SO_REUSEPORT port sharing works only on Linux per the deploy docs |
| **Thread safety** | Single-threaded per process ('Elysia is single-threaded by default'); scale out with cluster mode, one process per core |
| **Drop-in for the baseline** | no |

## Gotchas

- Constant-value routes (`.get('/', '')`) become native Bun static Responses built once at `listen()`; that is exactly the-benchmarker's GET / route, so its numbers measure Bun's static dispatch. Any `onRequest` or trace hook, or a higher-order function, disables these native static routes app-wide.
- AOT builds handlers as source strings run through `new Function()`. Unescaped schema property names and defaults allowed remote code execution (GHSA-gmm9-qwx3-2m3h, critical, &lt;=1.4.29, listed as fixed in the 1.4.30 changelog); cookie config injection was CVE-2025-66457. Never build schemas from untrusted input and stay on &gt;=1.4.30.
- AOT can regress badly: issue #1604 measured 3,853 req/s with defaults vs 175,951 with `aot: false` on 1.4.18 because `fetch` was recompiled per request (fixed in 1.4.19).
- Docs and code disagree: the configuration page says `aot` defaults to false, but the source enables it unless `ELYSIA_AOT=false`. Official packages moved from the `@elysiajs/*` npm scope to `@elysia/*` in 2026, and 2.0 is in beta (2.0.0-beta.19 on the npm `next` tag), so expect renames and breaking changes.

## Known shortcomings

- Not faster than actix: 0.96x/1.04x/1.06x at c=64/256/512 in the 2026-09-24 run and 0.5-3.5% slower at every level in the 2026-09-18 and 2026-09-20 runs, so a tie (verifier downgrade). Most of the speed is Bun's native HTTP server, not Elysia's code.
- The benchmark route runs no Elysia code per request: .get('/', '') is a constant that Elysia's default nativeStaticResponse turns into a pre-built Response dispatched natively by Bun.serve routes, so the number measures Bun's static dispatch (the suite's raw-Bun entry with a JS callback scores lower, 145,897 vs 173,877). On Node (elysia-node, same run) it does 48,128 req/s at c=512, \~0.29x actix. actix has lower p99 at c=64 (0.4 vs 0.7 ms). Handlers are compiled from source strings with new Function(): critical RCE via unescaped schema names/defaults (GHSA-gmm9-qwx3-2m3h, up to 1.4.29), cookie-config code injection (CVE-2025-66457); six advisories public since 2025-12, two critical. 1.4.18 recompiled handlers per request (3,853 vs 175,951 req/s, #1604, fixed 1.4.19). Open multipart memory leak (#1744); slow TypeScript IntelliSense on large apps (#1031); docs say aot defaults false but source enables it. 2.0 in beta; packages moving from @elysiajs to @elysia; SO_REUSEPORT multi-process only on Linux.

## Caveats and trade-offs

The win is not robust: in the cited run elysia-bun is 4% slower than actix at c=64 and only 4-6% ahead at c=256/512, and in the two previous snapshots (2026-09-18 and 2026-09-20, same framework configs, older harness method) it is 0.5-3.5% slower than actix at every concurrency. Most of the throughput comes from Bun's native HTTP server (Bun.serve), not Elysia's TypeScript layer. Single-route synthetic GET / benchmark; the suite's CPU name is a hard-coded label.

Requires the Bun runtime rather than Node.js; margin over actix is small (\~6%) on a minimal hello-world route, not representative of full-app performance

## Maintenance

Actively maintained (1.4.30 released 2026-08-26, about 1.24M npm downloads a week, MIT), but 2.0 is in beta and there are six public security advisories since December 2025 (two critical) plus four more fixed in 1.4.30, so pin versions and track releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs elysia-bun and actix in one run with public code (javascript/elysia-bun/app.ts, cluster.ts, javascript/config.yaml, javascript/bun.Dockerfile, rust/actix, rust/Dockerfile, .tasks/config.rake). Not A: the cpu_name is hard-coded in .tasks/db.rake, so no real CPU model is stated.
- **Verifier notes:** The c=512 numbers match data.json exactly (row id 1243 'elysia-bun'; actix id 3052), but the record left out the c=64 loss, and the earlier snapshots show Elysia slower than actix. So it is a tie, not a robust speedup, and the claim was corrected; the orchestrator may want to flag or drop it. The netlify result page is a JS app with no numbers in its HTML. Metadata verified via GraphQL: MIT, 19,193 stars, last commit 2026-08-26, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/8ae370ae89075281c056a138e57de25682d36e02/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/config.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/app.ts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/cluster.ts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun.Dockerfile>
  - <https://web-frameworks-benchmark.netlify.app/result?l=javascript>
  - <https://github.com/elysiajs/elysia>
- **Sources the enricher read:**
  - <https://github.com/elysiajs/elysia>
  - <https://github.com/elysiajs/elysia/blob/main/README.md>
  - <https://github.com/elysiajs/elysia/blob/main/package.json>
  - <https://github.com/elysiajs/elysia/blob/main/src/index.ts>
  - <https://github.com/elysiajs/elysia/blob/main/src/sucrose.ts>
  - <https://github.com/elysiajs/elysia/blob/main/src/compose.ts>
  - <https://github.com/elysiajs/elysia/blob/main/src/adapter/bun/index.ts>
  - <https://github.com/elysiajs/elysia/blob/main/src/adapter/bun/handler-native.ts>
  - <https://github.com/elysiajs/elysia/blob/main/src/adapter/bun/compose.ts>
  - <https://github.com/elysiajs/elysia/blob/main/CHANGELOG.md>
  - <https://github.com/elysiajs/elysia/blob/main/SECURITY.md>
  - <https://github.com/elysiajs/elysia/security/advisories>
  - <https://github.com/elysiajs/elysia/security/advisories/GHSA-gmm9-qwx3-2m3h>
  - <https://github.com/elysiajs/elysia/issues/1031>
  - <https://github.com/elysiajs/elysia/issues/1369>
  - <https://github.com/elysiajs/elysia/issues/1604>
  - <https://github.com/elysiajs/elysia/issues/1741>
  - <https://github.com/elysiajs/elysia/issues/1744>
  - <https://github.com/elysiajs/documentation/blob/main/docs/at-glance.md>
  - <https://github.com/elysiajs/documentation/blob/main/docs/key-concept.md>
  - <https://github.com/elysiajs/documentation/blob/main/docs/patterns/configuration.md>
  - <https://github.com/elysiajs/documentation/blob/main/docs/patterns/deploy.md>
  - <https://github.com/elysiajs/documentation/blob/main/docs/integrations/node.md>
  - <https://github.com/elysiajs/documentation/blob/main/docs/integrations/cloudflare-worker.md>
  - <https://github.com/elysiajs/documentation/blob/main/docs/essential/handler.md>
  - <https://registry.npmjs.org/elysia>
  - <https://api.npmjs.org/downloads/point/last-week/elysia>
  - <https://bun.com/docs/runtime/http/routing>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/app.ts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/cluster.ts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-bun/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun.Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/cluster.ts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-node/app.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-node/cluster.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-node/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/elysia-node/package.json>
  - <https://registry.npmjs.org/@elysia%2Fnode>
  - <https://registry.npmjs.org/@elysiajs%2Fnode>
  - <https://registry.npmjs.org/@elysia%2Fopenapi>
  - <https://github.com/elysiajs/documentation/commits/main/docs/integrations/node.md>
  - <https://github.com/elysiajs/elysia/blob/next/src/index.ts>
  - <https://hn.algolia.com/api/v1/search?query=elysia%20bun%20benchmark&tags=comment>
  - <https://news.ycombinator.com/item?id=45958510>
  - <https://news.ycombinator.com/item?id=45993888>
  - <https://news.ycombinator.com/item?id=45995975>
  - <http://export.arxiv.org/api/query?search_query=all:Elysia+AND+all:%22static+code+analysis%22>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/elysiajs/elysia`) · [data/wave5/enrich/raw/github_com_elysiajs_elysia.json](../../../data/wave5/enrich/raw/github_com_elysiajs_elysia.json) (enrichment confidence 0.4)

</details>
