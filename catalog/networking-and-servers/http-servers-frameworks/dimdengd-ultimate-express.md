# Ultimate Express

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `JavaScript` · `Apache-2.0` · 🟢 active

> Express 4 API re-implemented on uWebSockets.js; README shows 3-12x Express req/s, but Node 24 narrows most gaps.

| | |
|---|---|
| **Beats** | Express.js (Node.js) |
| **Claimed result** | README table (wrk -d 60 -t 1 -c 200, Node.js 20.17.0, Ryzen 5 3600): 3.10x-11.78x across 8 scenarios, e.g. routing/simple-routes 75.14k vs 11.16k req/s (6.73x), routing/lot-of-routes 54.57k vs 4.63k req/s (11.78x), middlewares/compression-file 14.92k vs 4.81k req/s (3.10x, the smallest gain). The express-static row's printed 4.87x is the MB/s throughput ratio; by req/s it is 32.45k vs 6.58k = 4.93x (derived from page data). |
| **Workload** | wrk -d 60 -t 1 -c 200 against 8 single-process test apps from tests/tests/ (routing/simple-routes, routing/lot-of-routes, routing/some-middlewares, routers/nested-routers, middlewares/express-static, engines/ejs, middlewares/body-urlencoded, middlewares/compression-file), each run once as Express 4 and once as Ultimate Express (uWebSockets.js-based drop-in replacement) on Node.js 20.17.0, Ubuntu 22.04. |
| **Metric** | throughput |
| **Hardware** | Ubuntu 22.04, AMD Ryzen 5 3600, 64GB RAM |
| **Compiler and flags** | Node.js 20.17.0 (JavaScript, no compile step); µExpress runs on the uWebSockets.js native addon (C++). Scenario servers are likely started via tests/singular.js as `node -r ./tests/preload.cjs <scenario>` (inferred, not stated on the page) |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/dimdenGD/ultimate-express) · [benchmark](https://github.com/dimdenGD/ultimate-express/blob/77ca8a2119b01e852d136cd8d5847cf29358a41c/README.md#performance-against-express) |

## Verdict

The README table (wrk -t1 -c200 -d60, one run, Node.js 20.17.0, Ubuntu 22.04, Ryzen 5 3600, measured around v1.2 in 2024 against an unstated Express 4.x) shows 3.10x (compressed small file) to 11.78x (route 999 of 1000) over Express, with 6.73x on a simple route. The project's own newer CI harness (benchmark/run.js, GitHub Actions ubuntu-latest, Node 24, wrk -t1 -c200 -d20) gave these results at the same commit 77ca8a2 on 2026-07-31: 2.57x hello-world, 11.64x routes-1000, 1.05x compression, and 0.69x (slower) for a 100-middleware chain.

## Use it when

- An existing Express 4 app on Node 22 where per-process routing/dispatch overhead, not the database, limits req/s: the project's CI on Node 22 (April-July 2026) showed 6.3-8.2x Express on hello-world and 1.7-3.7x on express.static.
- Large tables of plain string routes (hundreds to thousands of paths without ':' params): routes-1000 stays 7.9-11.9x ahead of Express even in the Node 24 CI runs of 2026-07-30/31.
- Apps that must keep the Express 4 middleware and view-engine ecosystem but want HTTP/3 or native uWS WebSockets on the same port without a rewrite to hyper-express or raw uWS.
- Linux x64/arm64 (glibc), macOS or Windows x64 deployments on Node 22, 24 or 26, the only targets the pinned uWebSockets.js v20.69.0 ships binaries for.

## Skip it when

- Node 24+ with ordinary handler chains: after the CI moved from Node 22 to 24 (2026-07-30), Express hello-world rose from about 7.6k-11k to 14.6k-43k req/s, while a contributor in #364 says µExpress stayed flat. As a result hello-world fell to 2.6-4.1x, compression-file to 1.0-1.1x, and a 100-middleware chain to 0.53-0.73x (slower than Express). The maintainer opened #364, 'UltimateExpress is officially pointless?', about this.
- Large bodies and streaming: in the 2026 CI runs a 512 KB JSON body is 0.89-1.04x and streamed responses are 0.70-1.37x, so there is nothing to gain there.
- Anything that instruments or needs node:http: Sentry tracing produces no spans (#286), http.on('upgrade') cannot be used, req.socket is a partial shim, and res.writableEnded never becomes true (#372, breaks pino-http).
- Alpine/musl, Bun, odd Node releases (23/25) or Windows arm64: uWebSockets.js is glibc-only, has prebuilt binaries only for Node 22/24/26, and is pulled from GitHub rather than the npm registry (#231, #232, #258).
- Express 5 codebases: the target is the Express 4 API (a contributor reports running an Express 5 app on it, but that is not claimed in the README); fulmine.js is the Express 5 variant.

## How it is fast

HTTP parsing, socket I/O and response writes run in uWebSockets.js (C++ via N-API); responses are written inside res.cork() batches with tryEnd/onWritable backpressure instead of Node's stream stack. At listen(), every route whose path is a plain string (no ':' params and no regex characters) under case-sensitive routing is registered on the native uWS router, with the middleware that matches it resolved once ahead of time; Express instead scans its layer stack on every request, which is why the 1000-route test shows the largest gain (about 11x). A handler simple enough to pass an acorn parse of its source (only res.set/status/send/end with req.query/req.params, no variables, calls or control flow) is compiled into a uWS DeclarativeResponse that is answered without entering JavaScript. Smaller wins: headers are materialised lazily, query strings go through fast-querystring, bodies are read only for POST/PUT/PATCH, and sendFile/static reads of files under 768 KB run on a worker thread (1 by default).

## Compared with alternatives

Pick it over fulmine.js when the app is on the Express 4 API: fulmine.js is derived from µExpress, targets Express 5 only, and its README says Express 4 users should use ultimate-express. Pick either over Elysia (Bun) when you cannot leave Node.js or rewrite handlers.

## Integration

| | |
|---|---|
| **Form** | module (npm package ultimate-express, plain JavaScript, with a git dependency on the uWebSockets.js native addon) |
| **Dependencies** | uWebSockets.js v20.69.0 (github: dependency with prebuilt .node binaries), acorn, fast-querystring, fast-zlib, tseep, qs, plus Express helper packages (accepts, cookie, cookie-signature, etag, fresh, mime-types, proxy-addr, range-parser, statuses, type-is, vary, ...) |
| **Minimum toolchain** | Node.js &gt;= 22 (engines field); binaries exist for Node 22, 24 and 26 only. ultimate-express@2.1.0 is the last release for Node 19-21, and the node-v18 tag (1.4.10) covers Node 18. |
| **Platforms** | Linux x64/arm64 (glibc only; no Alpine/musl), macOS x64/arm64, Windows x64; not Bun |
| **Thread safety** | Single event loop per process, as with Express. One worker thread (the 'threads' option, 0 on single-core machines) does file reads and is shared by all app instances. Under node:cluster, worker processes listen on a shared port (uWS non-exclusive listen, from src/application.js); the README does not document multi-process use. |
| **Drop-in for the baseline** | partial — the same Express 4 API and most middleware work after a one-line require change, but routing is case-sensitive by default, the header limit is 4 KB, body parsing only covers POST/PUT/PATCH, there is no http.Server (TLS and HTTP/3 go through uwsOptions), express-async-errors does not work (use app.set('catch async errors', true)), and req.route/req.socket/express.request/express.response are partial |

## Gotchas

- Case-sensitive routing is on by default, unlike Express. Turning it off, or using ':param', wildcard or regex paths, drops those routes off the native uWS router onto the slower JS matcher. The README only mentions regex characters; the ':' exclusion is in src/router.js.
- uWS caps request headers at 4096 bytes against Node's 16384; apps with large cookies or JWTs need the UWS_HTTP_MAX_HEADERS_SIZE environment variable.
- Request bodies are read only for POST, PUT and PATCH. A DELETE, or a GET that carries a body, leaves req.body empty unless you add the method to the 'body methods' setting (the README says reading bodies costs about 15%).
- Response extends Writable but end() bypasses Node's Writable state, so writableEnded/writableFinished stay false (#372). Reported quirks include 'close' not firing when no response is sent (#287) and morgan logging 200 where the client got a 304 (#206).

## Known shortcomings

- The README table (2024, Node 20.17, v1.2) is stale: after the project's own CI moved to Node 24 (2026-07-30), Express got much faster and the ratios fell to 2.6-4.1x hello-world, 1.0-1.1x compression-file, 0.53-0.73x on a 100-middleware chain (slower than Express), 0.89-1.04x on 512 KB JSON bodies and 0.70-1.37x streaming; only routes-1000 still wins big (7.9-11.9x). The maintainer opened #364 'UltimateExpress is officially pointless?' and there have been no commits since 2026-07-31. :param routes use the JS matcher, not native routing. Compatibility gaps: no node:http (Sentry tracing has no spans, #286), res.writableEnded never true (breaks pino-http, #372), 4 KB header limit vs Node's 16 KB, bodies read only for POST/PUT/PATCH, case-sensitive routing by default, express-async-errors doesn't work. uWebSockets.js comes from GitHub (not npm), glibc-only, Node 22/24/26 binaries only, no Bun. Express 4 API (fulmine.js covers Express 5).

## Caveats and trade-offs

First-party, single-machine, single-run numbers without repeated trials. They are old: the table rows were last edited 2024-09-26..2024-10-02 (compression row 2025-05-04), when µExpress was about v1.2 (package.json then pinned express ^4.19.2). The package is now 2.2.1 and requires Node &gt;=22, and the table has not been re-run. The /benchmark directory (benchmark/run.js, added 2026-04-02) is a newer harness with different scenarios (hello-world, routes-1000, static-250kb, art-render, ...); it did not produce these numbers and its results are not published. The Express 4 minor version measured is not stated. The gains come from the uWebSockets.js C++ core. There are documented behavioural differences from Express (case-sensitive routing by default, a 4 KB default header limit vs Node's 16 KB, HTTPS via uwsOptions). The baseline (Express.js) is not one of the category's named baselines, so baseline_in_list=false.

Built on uWebSockets.js (native C++ core via N-API); not a 100% Express match (documented differences: case-sensitive routing by default, opt-in body parsing, different HTTPS setup)

## Maintenance

Maintained by one main author (dimdenGD, 808 commits) with contributors, v2.2.1 released 2026-07-30, about 34k npm downloads a month and Apache-2.0 (plus EXPRESS_LICENSE), but there have been no commits since 2026-07-31, the day the maintainer asked in #364 whether Node 24 made the project pointless.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now A.
- **Tier reason:** The README table compares Express with µExpress on 8 scenarios. It states the load command (wrk -d 60 -t 1 -c 200), the runtime (Node.js 20.17.0; JavaScript has no compile flags) and the CPU (AMD Ryzen 5 3600). Each scenario name is a public test app under tests/tests/ (e.g. tests/tests/routing/simple-routes.js), runnable as either framework through tests/singular.js with tests/preload.cjs disabling process.exit. That the table was produced this way is my inference; the README does not name the script.
- **Verifier notes:** Downgraded because the record's range 4.87x-11.78x left out the 3.10x compression-file row. It also wrongly said the /benchmark directory produced the table. Tier A holds, since the scenario code is public and runtime, command and CPU are stated, but the table is about two years old and was measured on a v1.x release. Metadata checks out: Apache-2.0 (plus an EXPRESS_LICENSE for Express-derived code), 1,109 stars, last commit 2026-07-31, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dimdenGD/ultimate-express>
  - <https://raw.githubusercontent.com/dimdenGD/ultimate-express/main/README.md>
  - <https://raw.githubusercontent.com/dimdenGD/ultimate-express/main/benchmark/README.md>
  - <https://raw.githubusercontent.com/dimdenGD/ultimate-express/main/benchmark/run.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/package.json>
  - <https://github.com/dimdenGD/ultimate-express/blob/52d9d72/README.md>
  - <https://github.com/dimdenGD/ultimate-express/blob/0eadc8c/tests/tests/routing/simple-routes.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/0eadc8c/tests/singular.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/0eadc8c/tests/preload.cjs>
  - <https://github.com/dimdenGD/ultimate-express/blob/0eadc8c/package.json>
- **Sources the enricher read:**
  - <https://github.com/dimdenGD/ultimate-express>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/README.md>
  - <https://github.com/dimdenGD/ultimate-express/blob/77ca8a2119b01e852d136cd8d5847cf29358a41c/README.md#performance-against-express>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/package.json>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/index.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/application.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/router.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/declarative.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/utils.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/worker.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/response.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/src/request.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/benchmark/README.md>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/benchmark/run.js>
  - <https://github.com/dimdenGD/ultimate-express/blob/main/.github/workflows/benchmark.yml>
  - <https://github.com/dimdenGD/ultimate-express/commit/b204754>
  - <https://github.com/dimdenGD/ultimate-express/commit/77ca8a2119b01e852d136cd8d5847cf29358a41c#commitcomment-194490788>
  - https://api.github.com/repos/dimdenGD/ultimate-express/comments (all github-actions benchmark commit comments, 2025-04 to 2026-07)
  - <https://api.github.com/repos/dimdenGD/ultimate-express/commits?since=2026-07-29>
  - <https://api.github.com/repos/dimdenGD/ultimate-express/contributors>
  - <https://github.com/dimdenGD/ultimate-express/issues/364>
  - <https://github.com/dimdenGD/ultimate-express/issues/372>
  - <https://github.com/dimdenGD/ultimate-express/issues/287>
  - <https://github.com/dimdenGD/ultimate-express/issues/286>
  - <https://github.com/dimdenGD/ultimate-express/issues/228>
  - <https://github.com/dimdenGD/ultimate-express/issues/206>
  - <https://github.com/dimdenGD/ultimate-express/issues/83>
  - <https://github.com/dimdenGD/ultimate-express/issues/258>
  - <https://github.com/dimdenGD/ultimate-express/issues/232>
  - <https://github.com/dimdenGD/ultimate-express/issues/231>
  - https://github.com/dimdenGD/ultimate-express/issues?q=memory OR crash OR slower OR alpine OR pnpm OR bun
  - <https://github.com/dimdenGD/ultimate-express/security/advisories>
  - <https://github.com/advisories?query=ultimate-express>
  - <https://raw.githubusercontent.com/uNetworking/uWebSockets.js/v20.69.0/README.md>
  - <https://raw.githubusercontent.com/uNetworking/uWebSockets.js/v20.69.0/uws.js>
  - <https://github.com/uNetworking/uWebSockets.js/tree/v20.69.0>
  - <https://github.com/nigrosimone/fulmine.js>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/package.json>
  - <https://api.npmjs.org/downloads/point/last-month/ultimate-express>
  - <https://registry.npmjs.org/ultimate-express>
  - <https://hn.algolia.com/api/v1/search?query=ultimate-express&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/dimdengd/ultimate-express`) · [data/wave5/enrich/raw/github_com_dimdengd_ultimate_express.json](../../../data/wave5/enrich/raw/github_com_dimdengd_ultimate_express.json) (enrichment confidence 0.6)

</details>
