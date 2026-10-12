# Bun (Bun.serve)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Rust/C++/C` · `MIT for Bun's own code, per LICENSE.md (GitHub reports NOASSERTION). Bun statically links JavaScriptCore/WebKit (LGPL-2) and tinycc (LGPL-2.1), plus permissive libraries such as BoringSSL, a uWebSockets fork and uSockets (Apache-2.0), mimalloc (MIT) and zstd (BSD OR GPL-2.0).` · 🟢 active

> Bun's built-in JavaScript HTTP server (Bun.serve); 2.0-2.2x Go net/http throughput on a 3-route hello-world API, 4 cores.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | At 512 connections: Bun 145,896.6 req/s vs Go net/http (nethttp) 67,239.1 req/s, \~2.17x (derived from page data). Same run at 64 connections: 144,254.3 vs 71,498.7 (\~2.02x). At 256 connections: 145,871.0 vs 67,381.9 (\~2.16x). Each figure is the mean over the 3 contract routes. The older master-branch run (commit 0fccb1d, 2026-09-20, a different method) gives only 93,972.0 vs 83,963.5 at 512 connections (\~1.12x) (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks route contract: GET / (empty body), GET /user/:id (returns the id), POST /user (empty body). Load is zrk --closed over keep-alive connections, 15-second runs at 64, 256 and 512 connections. The headline total_requests_per_s is the average over the 3 routes (avg() in the .tasks/db.rake export SQL). The server container used about 4 cores (server_cpu_cores 3.95 for Bun, 3.91 for net/http; saturation 98-99%). Bun runs Bun.serve with a routes table under node:cluster, one reusePort worker per core; Go runs net/http with http.ServeMux. |
| **Metric** | throughput |
| **Hardware** | CPU model not reliably stated. data.json hardware.cpu_name 'M1 Eight-Core Processor' and memory 7,733,008 are hard-coded constants in .tasks/db.rake. The live fields from Etc.uname report Linux 7.2.6-200.fc44.x86_64, machine x86_64, 16 host CPUs. The server container used about 4 cores. |
| **Compiler and flags** | Bun: oven/bun:1.4-slim Docker image (javascript/bun.Dockerfile), 'bun install --production', 'bun run cluster.ts', Bun.serve development:false. data.json labels the Bun version 1.2.5 (from javascript/bun/config.yaml), which differs from the image tag. Go net/http: golang:1.27 image, CGO_ENABLED=1, 'go build -trimpath', GOAMD64=v3 when built for amd64 (go/Dockerfile). |
| **Adoption** | 96k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/oven-sh/bun) · [benchmark](https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks run of 2026-09-24 (commit f673364; zrk closed-loop keep-alive, 15 s per level, mean of GET /, GET /user/:id and POST /user; server pinned to cpuset 0-3 and load generator to CPUs 4-15 of a 16-CPU x86-64 Linux 7.2 host, CPU model not recorded), Bun 1.4.x (oven/bun:1.4-slim, mislabelled 1.2.5 in data.json) running Bun.serve routes as one reusePort node:cluster worker per core did 144,254 / 145,871 / 145,897 req/s at c=64/256/512 vs 71,499 / 67,382 / 67,239 for Go 1.27 net/http with http.ServeMux (go build -trimpath, GOAMD64=v3), i.e. 2.02-2.17x. p99 latency was 0.90 vs 3.05 ms at c=64 and 4.38 vs 15.51 ms at c=512; an earlier 2026-09-20 snapshot of the suite, measured differently, gave only \~1.12x.

## Use it when

- JS/TS HTTP APIs on Linux where per-request stack overhead dominates. In the 2026-09-24 the-benchmarker run on 4 cores, Bun.serve with JS route callbacks did 145,897 req/s at c=512 vs 67,239 for Go net/http, with p99 latency of 4.4 ms vs 15.5 ms.
- Node.js services that want more throughput without leaving JavaScript: in the same run raw Bun.serve beat Fastify on Node (68,128 req/s) by \~2.1x and Express (42,586) by \~3.4x.
- Health checks, redirects, fixed JSON and static files: constant `Response` routes are dispatched with no allocation (the docs claim at least 15% faster than returning a new Response), and `{ dir }` routes (1.4+) stream files with sendfile and handle ETag, 304 and Range.
- WebSocket fan-out servers that want built-in topic pub/sub, per-socket backpressure limits and permessage-deflate without extra packages.
- Linux deployments where one worker process per core behind `reusePort` (or node:cluster) is acceptable.

## Skip it when

- As a speed-only reason to leave Go: in the same run Go fasthttp (125,657 req/s) and Fiber (123,666) came within \~1.16-1.18x of Bun, and an earlier 2026-09-20 snapshot of this suite, measured differently, showed Bun only \~1.12x ahead of net/http.
- macOS or Windows production, or any host without SO_REUSEPORT: `reusePort` is ignored there, and Bun's docs say node:cluster can only load-balance HTTP on Linux. You get one JS thread per server, while the Go binary in this run used 3.9 cores from a single process with no cluster code.
- CPU-heavy handlers or state shared in memory across requests: each worker is a separate process with its own heap and one event-loop thread, so a slow synchronous handler stalls every connection on that worker.
- gRPC, or anything that needs production HTTP/2 or HTTP/3: both are experimental in Bun.serve. There is no WebSocket over HTTP/2, no server push and no response trailers. The 1.4 notes say not to ship `http3: true` to production yet, since 0-RTT is disabled and server.upgrade() returns false over H3.
- Risk-averse deployments: Bun 1.4 (2026-08-20) is the first release of a Zig-to-Rust port done mostly by Claude agent workflows in 11 days. About 4% of the Rust sits in `unsafe` blocks. Advisories for the 1.4 security fixes are held back until people upgrade, and a request-smuggling bug (issue #29732, fixed 2026-04-27) has an open request for a CVE (#30921).

## How it is fast

Sockets, parsing and routing stay in native code: uSockets (C) runs an epoll (epoll_pwait2) or kqueue loop, not io_uring, and Bun's uWebSockets fork (C++) parses requests with SWAR word-at-a-time scanning (the `hasLess` bit trick on 8-byte words, with 32 bytes of required buffer post-padding) and a Bloom filter over header names, then dispatches through uWS's tree router. The glue layer (Rust since 1.4, Zig before) takes request contexts from a pre-allocated pool of 2,048 and writes response metadata inside uWS 'corked' sections, while ServerRouteList keeps route callbacks in a fixed array and caches one JavaScriptCore Structure per route's params object so the JIT sees a single shape; params are percent-decoded with SIMD. Constant `Response` routes are served with no allocation and no JS. Multi-core throughput comes from one process per core sharing the port through `reusePort` (Linux SO_REUSEPORT), with the kernel spreading connections across them.

## Compared with alternatives

Pick Bun.serve over fasthttp only when the service is, or should become, JS/TS: staying in Go, fasthttp reached 0.86x Bun's throughput in the same run with no runtime switch. Bun.serve is the zero-dependency base under Elysia, which scored 173,877 req/s largely because its benchmark routes are constants Bun serves natively; uWebSockets.js scored 174,621 on Node with a lower-level API, so pick it instead if you must stay on Node.

## Integration

| | |
|---|---|
| **Form** | runtime built-in (Bun.serve ships inside the single `bun` executable; nothing to install beyond Bun itself, optional @types/bun for TypeScript types; cannot be linked into C/C++/Rust programs) |
| **Dependencies** | none beyond the bun binary, which statically links JavaScriptCore/WebKit, a uWebSockets fork, uSockets, BoringSSL, lsquic/ls-hpack/ls-qpack, mimalloc and others |
| **Minimum toolchain** | Bun 1.4.x as benchmarked (oven/bun:1.4-slim image); `{ dir }` folder routes are new in 1.4.0; no compiler needed |
| **Platforms** | Linux x64/arm64 (glibc 2.17+ or musl builds; kernel 5.6+ recommended; the installation docs say 3.10 is the minimum, the README says 5.1), macOS 13+ x64/arm64, Windows 10 1809+ x64/arm64, FreeBSD 14.3+ x64/aarch64 (new in 1.4), experimental Android. x64 needs SSE4.2 (Nehalem): one binary picks AVX2/AVX-512 code paths at runtime. Multi-process port sharing (`reusePort`) works only on Linux. |
| **Thread safety** | Each Bun.serve instance runs its handlers on its process's single JS event-loop thread, so handlers never run in parallel within one process. Scaling across cores means separate processes sharing the port through `reusePort` (Linux SO_REUSEPORT) or node:cluster, and HTTP load balancing across processes is Linux-only. Running Bun.serve from Worker threads is not documented as a scaling path. |
| **Drop-in for the baseline** | no |

## Gotchas

- `idleTimeout` defaults to 10 s and counts a handler that is still working but has not written a byte as idle, so slow handlers see connection resets. The maximum is 255 s (open issue #15589 asks to raise it). For SSE or long streams, call `server.timeout(req, 0)` for that request.
- Multi-core scaling fails silently: `reusePort` is ignored on macOS and Windows, and open issue #43690 (2026-09-21) reports that node:http `listen({ reusePort: true })` is ignored even on Bun, while node:net honours it.
- Since 1.3.4, requests with malformed Content-Length, Transfer-Encoding or chunked framing get 400 and the connection is closed without calling your handler or logging anything. Check a hand-written client's framing headers first.
- Constant `Response` routes are cached for the server's lifetime; call `server.reload()` to change them. WebSockets (`server.upgrade()`) work only over HTTP/1.1, so `http1: false` disables them.

## Known shortcomings

- The older 2026-09-20 run (different method) shows only \~1.12x over Go net/http (93,972 vs 83,964 req/s); in the current run Bun beats Go fasthttp (the fastest Go option) by only \~1.16x. The image was oven/bun:1.4-slim though data.json labels Bun 1.2.5. The CPU name is hard-coded (uname reports x86_64, 16 CPUs). Bun's code is MIT but it statically links LGPL-2 JavaScriptCore/WebKit.
- Bun 1.4 (2026-08-20, the benchmarked image) is a Rust rewrite; the HTTP core is still uSockets (C) plus Bun's uWebSockets fork (C++), on epoll/kqueue, not io_uring. The exact version is unknown (image tag floats at 1.4). Go was built with GOAMD64=v3 while Bun ships a Nehalem-baseline binary with runtime AVX2/AVX-512 dispatch. Routes don't match exactly (Bun 204 vs Go 200 with empty body). Raw Bun.serve with JS callbacks sat below uWebSockets.js on Node in the same run. Multi-core scaling works only on Linux (reusePort ignored on macOS/Windows; node:http ignores reusePort, #43690); Bun needed one process per core while Go used 3.9 cores in one. No published GitHub security advisories; request smuggling #29732 fixed without a CVE (#30921 open). 1.4 is the first release of a Zig-to-Rust port done largely by AI agents in 11 days (\~4% unsafe); HTTP/2 and HTTP/3 in Bun.serve are experimental (no gRPC trailers, no WebSockets over h2/h3; HTTP/3 not for production). idleTimeout defaults to 10 s and counts a slow handler as idle (max 255 s, #15589); malformed framing gets 400 and close with no handler call or log; docs disagree on minimum kernel (5.1 vs 3.10).

## Caveats and trade-offs

Numbers come from a third-party multi-language suite run on one unnamed host. The CPU model is unknown: data.json's cpu_name and memory are hard-coded in .tasks/db.rake, while uname reports Linux x86_64 with 16 CPUs. The ratio depends heavily on method: the older master-branch run (2026-09-20) shows only \~1.12x at 512 connections, and the README says results from different revisions are not comparable. The workload is a trivial 3-route API (empty body or path-parameter echo), so the gain measures HTTP-stack overhead, not application work. Bun runs as a node:cluster of reusePort workers. The Bun version label 1.2.5 in data.json differs from the oven/bun:1.4-slim image actually used. In the same run, Go fasthttp reaches 125,656.7 req/s at 512 connections, so Bun's margin over the fastest Go option is only \~1.16x. Bun's own code is MIT, but the binary statically links LGPL-2 JavaScriptCore/WebKit, which carries relinking obligations.

Bun statically links LGPL-2 licensed JavaScriptCore/WebKit; caveat noted for LGPL relinking obligations. Not a drop-in for Go net/http (different language/runtime), uses io_uring/kqueue-backed Zig HTTP server under the hood, not a C++ library usable from C++ directly.

## Maintenance

Very active (last push 2026-09-26, v1.4.2 on 2026-09-05, 96k stars, owned by Anthropic since December 2025) and MIT for Bun's own code, but the binary statically links LGPL-2 JavaScriptCore/WebKit and LGPL-2.1 tinycc, and 1.4 is the first release of the Rust rewrite, so expect a few releases of settling.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** the-benchmarker/web-frameworks is a well-known independent third-party suite. Its data.json at commit f673364 (2026-09-24) lists bun (framework_id 1189) at 145,896.6 req/s and nethttp (framework_id 811, Go stdlib http.ServeMux) at 67,239.1 req/s at 512 connections. The benchmark code (javascript/bun/cluster.ts, go/nethttp/main.go, javascript/bun.Dockerfile, go/Dockerfile) and build flags are public, but the CPU model is not reliably stated: cpu_name is a string hard-coded in .tasks/db.rake while uname reports x86_64. So B, not A.
- **Verifier notes:** The numbers match data.json exactly for Bun's own row and the nethttp row. benchmark_url was pinned to commit f673364 (identical SHA-1 content to develop HEAD). Bun appears in known_list.txt only because this record was merged; it has no separate earlier entry, so this is not a known-project duplicate. Metadata checked: 96,041 stars, not archived or a fork, last commit 2026-09-26; usability 'mixed' kept, following the F-Stack precedent for a permissive core with statically linked copyleft parts.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/cluster.ts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun.Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/main.go>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/go.mod>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://github.com/oven-sh/bun>
  - <https://raw.githubusercontent.com/oven-sh/bun/main/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/oven-sh/bun>
  - <https://github.com/oven-sh/bun/blob/main/README.md>
  - <https://github.com/oven-sh/bun/tree/main>
  - <https://raw.githubusercontent.com/oven-sh/bun/main/LICENSE.md>
  - <https://github.com/oven-sh/bun/releases>
  - <https://github.com/oven-sh/bun/releases/tag/bun-v1.4.0>
  - <https://github.com/oven-sh/bun/releases/tag/bun-v1.4.1>
  - <https://github.com/oven-sh/bun/releases/tag/bun-v1.4.2>
  - <https://bun.com/1.4>
  - <https://bun.com/blog/bun-v1.4>
  - <https://bun.com/blog/bun-in-rust>
  - <https://github.com/oven-sh/bun/blob/main/docs/runtime/http/server.mdx>
  - <https://github.com/oven-sh/bun/blob/main/docs/runtime/http/routing.mdx>
  - <https://github.com/oven-sh/bun/blob/main/docs/runtime/http/metrics.mdx>
  - <https://github.com/oven-sh/bun/blob/main/docs/guides/http/cluster.mdx>
  - <https://github.com/oven-sh/bun/blob/main/docs/installation.mdx>
  - <https://github.com/oven-sh/bun/blob/main/docs/runtime/nodejs-compat.mdx>
  - <https://github.com/oven-sh/bun/blob/main/src/jsc/bindings/ServerRouteList.cpp>
  - <https://github.com/oven-sh/bun/blob/main/src/runtime/server/RequestContext.rs>
  - <https://github.com/oven-sh/bun/blob/main/packages/bun-uws/src/HttpParser.h>
  - <https://github.com/oven-sh/bun/blob/main/packages/bun-usockets/src/eventing/epoll_kqueue.c>
  - <https://github.com/oven-sh/bun/blob/main/packages/bun-usockets/src/internal/internal.h>
  - <https://github.com/oven-sh/bun/security/advisories>
  - <https://github.com/advisories?query=ecosystem%3Anpm+bun>
  - <https://github.com/oven-sh/bun/issues?q=Bun.serve+memory+leak>
  - <https://github.com/oven-sh/bun/issues?q=request+smuggling>
  - <https://github.com/oven-sh/bun/issues?q=Bun.serve+reusePort>
  - <https://github.com/oven-sh/bun/issues?q=Bun.serve+idleTimeout>
  - <https://github.com/oven-sh/bun/issues/29732>
  - <https://github.com/oven-sh/bun/issues/30921>
  - <https://github.com/oven-sh/bun/issues/15589>
  - <https://github.com/oven-sh/bun/issues/14727>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/cluster.ts>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/bun.Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/main.go>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.env>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/collect.rake>
  - <https://github.com/the-benchmarker/web-frameworks/tree/f673364fb30748e5bb8e57319ec2772bc872f78a>
  - <https://hn.algolia.com/api/v1/search?query=bun%20http%20server%20benchmark%20go&tags=comment>
  - <https://hn.algolia.com/api/v1/search?query=bun%20serve%20benchmark%20misleading&tags=comment>
  - <https://hn.algolia.com/api/v1/search?query=Rewriting%20Bun%20in%20Rust&tags=story>
  - <https://news.ycombinator.com/item?id=48837877>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/oven-sh/bun`) · [data/wave5/enrich/raw/github_com_oven_sh_bun.json](../../../data/wave5/enrich/raw/github_com_oven_sh_bun.json) (enrichment confidence 0.55)

</details>
