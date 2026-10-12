# Ferron

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust web server and reverse proxy with automatic TLS and built-in tracing; markets nginx-class speed but publishes no numbers.

| | |
|---|---|
| **Beats** | nginx (C); the HN threads also name Caddy, Apache httpd and HAProxy |
| **Claimed result** | No numbers in the repository. The Show HN title 'I'm rewriting a web server written in Rust for speed and ease of use' and a thread on the marketing claim 'faster than all ...'; a commenter who ran nginx reverse-proxy benchmarks said Ferron is close to nginx, not faster. |
| **Workload** | Static-file serving and reverse proxying benchmark charts on the project's website, which Hacker News commenters said show different server sets per chart; no benchmark data or methodology is in the repository. |
| **Metric** | throughput |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 2.2k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/ferronweb/ferron) |

## Verdict

Nothing has been measured that can be checked: the README says only 'fast and consistent under load', the website charts (ferron.sh, unreachable here) come from an unpinned h2load-over-HTTPS/2 harness with no committed results or hardware, and the only third-party statement (HN, snippet only) puts Ferron near nginx as a reverse proxy.

## Use it when

- Small to mid-size sites and API gateways that want automatic TLS and a short config file without tuning, where nginx-level throughput is enough rather than required to be beaten.
- Debugging-heavy deployments: per-request traces linked to logs, OTLP, Prometheus and StatsD export are built in.
- Teams that want a memory-safe (Rust) replacement for a Caddy- or nginx-style front server and can run release-candidate software.
- Mixed workloads on one box: static files, reverse proxy with round-robin and keep-alive upstreams, PHP through FastCGI.

## Skip it when

- When you need a measured speed win over nginx: no benchmark data, hardware or results are published in any repository, and an HN commenter who ran reverse-proxy tests found Ferron roughly on par with nginx.
- Security-sensitive edges before 3.0 final: seven advisories were published on 2026-09-25, including a critical auth_to fail-open with proxy, an HTTP/2 Rapid Reset variant in the in-house HTTP/2 stack and an unauthenticated HTTP/3 SETTINGS CPU DoS.
- Existing nginx configurations with complex location logic, Lua or third-party modules: there is no config compatibility.
- Production that needs a stable major release: 3.x is still rc.9 and its runtime has changed between major versions (tokio and hyper in 1.x, Monoio in 2.x per HN comments, zincio in 3.x).

## How it is fast

Ferron 3 runs on zincio, the project's own thread-per-core async runtime (one primary thread per CPU core, io_uring on Linux when the io_uring directive is turned on, otherwise epoll via mio), with zincio-http's in-house HTTP/2 and HTTP/3 stacks and splice-based zero-copy sending for HTTP/1.x static responses. TLS is rustls (aws-lc-rs provider for QUIC and the proxy client), the Unix build links jemalloc, and the release profile uses LTO with codegen-units=1 and panic=abort. The cross-build scripts offer an optional PGO build trained with wrk/h2load scenarios, which the project says gives 10-20%; no measurement backs that figure.

## Compared with alternatives

Pick Ferron over Caddy (the other batteries-included server here, also without a verified win over nginx) when you want Rust memory safety and built-in request tracing and can accept release-candidate status; if you need numbers showing a win over nginx, the measured siblings routez (1.19-1.26x reported) or rproxy are better-evidenced, though they are narrower proxies rather than full servers.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (Rust workspace; modules compiled in, custom builds possible) |
| **Dependencies** | zincio and zincio-http (own runtime and HTTP stack), tokio, hyper 1 (proxy client), rustls 0.23 with aws-lc-rs, quinn (QUIC), async-compression (zstd, brotli, gzip), tikv-jemallocator on Unix, mimalloc on Windows; git submodules opentelemetry-proto and phc-winner-argon2 |
| **Minimum toolchain** | Rust stable via rustup, edition 2021; no rust-version or rust-toolchain file in the repository |
| **Platforms** | Linux (cross-build targets x86_64, i686, aarch64, armv7, riscv64, s390x, ppc64le; glibc and musl), Windows (IOCP, Windows service), macOS/BSD via mio |
| **Thread safety** | not applicable (server); multi-threaded data plane with one primary thread per CPU core by default, set by the cpu_affinity directive |
| **Drop-in for the baseline** | partial: serves the same roles as nginx (static files, reverse proxy, TLS termination) but needs a rewritten configuration |

## Gotchas

- Harness behind ferron.sh/benchmarks (ferronweb/benchmarking, 3 commits on 2026-09-02) builds nginx from unpinned master with plain ./auto/configure, so nginx gets its default -O (i.e. -O1) plus -g with no --with-cc-opt, while Ferron gets LTO, codegen-units=1 and panic=abort; every server is built from an unpinned branch and no results, hardware or versions are committed.
- The 'static files with Zstd compression' scenario does not compress with the committed client: client/benchmark.py runs h2load with no -H option and h2load sends no Accept-Encoding, so both servers serve identity responses; if the header is added by hand (as the server README's manual example does), nginx compresses at level 3 and Ferron at a hard-coded level 4 with window_log 17 and hash_log 10, and medium.bin is 2 MB of random, incompressible bytes.
- Charts history: the 2025 reverse-proxy chart left nginx out 'due to possible misconfiguration'; in issue #185 the maintainer said nginx lacked upstream keepalive and later called his rerun's nginx numbers possibly unreliable; nginx was only added to the static charts in January 2026. The sweep's req/s counts every completed stream including non-2xx (h2load req_success), with errors only in a separate CSV column.
- io_uring is off by default (the benchmark configs do not enable it), compression levels are fixed at 4 for every algorithm, and the static compressor treats .bin and other unknown extensions as compressible.

## Known shortcomings

- No numbers in the repo, no HttpArena entry, ferron.sh unreachable; HN comments call it close to nginx, not faster; marketing claim only.
- Website harness found (ferronweb/benchmarking, 3 commits on 2026-09-02): nginx is built from unpinned master with nginx's own default -O (-O1) -g while Ferron gets LTO and codegen-units=1; the committed client benchmark.py runs h2load with no Accept-Encoding header, so the 'Zstd compression' scenario does no compression (with the header added by hand it is nginx level 3 against Ferron level 4); no results, hardware or versions are committed. Issue #185: nginx was left off the charts because of the maintainer's own misconfiguration. Seven GHSA advisories on 2026-09-25 (one critical); 3.x is still rc.9.

## Caveats and trade-offs

The README (default branch develop-3.x) says only 'Predictable performance - fast and consistent under load, right out of the box. No runtime tuning required.'; older branches say 'High performance - thoroughly optimized for speed' (develop-2.x) and 'built with Rust's async capabilities for optimal speed' (main, develop). No benchmark code, data or methodology is in the repository (docs/ holds configuration, installation, migration, module-development and use-cases pages only), and Ferron has no HttpArena entry. The website charts could not be opened (ferron.sh: getaddrinfo ENOTFOUND), so nothing was measured or read; the HN statements in the record (nginx left out of the static-file charts, Ferron roughly on par with nginx as a reverse proxy) are snippet only. Kept as a tier D claim with no numbers for notability (2.2k stars) and for a verifier with wider network access to read the website charts. A web search for Ferron benchmarks returned nothing about Ferron itself. [retier] Website harness (ferronweb/benchmarking, 2026-09-02): nginx built from unpinned master with its default -O (-O1) -g while Ferron gets LTO and codegen-units=1; benchmark.py runs h2load with no Accept-Encoding header, so the 'Zstd compression' scenario does no compression; no results, hardware or versions committed. Issue #185: nginx was left off the charts because of the maintainer's own misconfiguration. Seven GHSA advisories on 2026-09-25 (one critical); 3.x still rc.9.

Not assessed; the repository describes a web server built for production debugging.

## Maintenance

Very active (commits to 2026-10-10, 3.0.0-rc.9 on 2026-10-04, 2.2k stars, MIT) and usable today via the stable 2.x LTS line, but the 3.x line is a release candidate that just shipped seven security fixes and has no reproducible performance evidence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No numbers anywhere reachable: the README on the default branch develop-3.x says only 'Predictable performance - fast and consistent under load, right out of the box', the develop-2.x and main READMEs only say 'High performance', the repo has no benchmark directory or docs page on performance, HttpArena has no Ferron entry (site/data/results/ferron.json 404), and the project website (ferron.sh) did not resolve.
- **Verifier notes:** Tier D confirmed: no numbers in the repo, no HttpArena entry, website unreachable; claim is marketing only and HN snippets say it is on par with nginx, not faster. Shortcomings to record: no benchmark data or methodology, website charts reportedly omit nginx from static-file tests (snippet only). Metadata confirmed: MIT, 2.2k stars, last commit 2026-10-10 on develop-3.x, not a fork, not archived.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-102 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ferronweb/ferron>
  - <https://github.com/ferronweb/ferron/commits>
  - <https://github.com/ferronweb/ferron/tree/develop-3.x/docs>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/README.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop-2.x/README.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop/README.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/main/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/README.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/cross-build/README.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/cross-build/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/core/Cargo.toml>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/entrypoint/Cargo.toml>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/modules/http-server/Cargo.toml>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/modules/http-static/Cargo.toml>
  - <https://raw.githubusercontent.com/ferronweb/ferron/HEAD/modules/http-proxy/Cargo.toml>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop-3.x/docs/configuration/content/compression.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop-3.x/docs/configuration/content/static-files.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop-3.x/docs/configuration/server/core-directives.md>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop-3.x/docs/links.json>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop-3.x/modules/http-static/src/util/compression.rs>
  - <https://raw.githubusercontent.com/ferronweb/ferron/develop-3.x/modules/http-static/src/util/file_stream.rs>
  - <https://github.com/ferronweb/ferron/tree/develop-3.x/docs>
  - <https://github.com/ferronweb/ferron/tree/develop-3.x/docs/configuration>
  - <https://github.com/ferronweb/ferron/tree/develop-3.x/docs/configuration/content>
  - <https://github.com/ferronweb/ferron/tree/develop-3.x/modules/http-static/src>
  - <https://github.com/ferronweb/ferron/tree/develop-3.x/modules/http-static/src/util>
  - <https://github.com/ferronweb/ferron/issues?q=is%3Aissue+performance>
  - <https://github.com/ferronweb/ferron/issues/185>
  - <https://github.com/ferronweb/ferron/releases>
  - <https://github.com/ferronweb/ferron/security>
  - <https://github.com/ferronweb>
  - <https://github.com/orgs/ferronweb/repositories?page=2>
  - <https://github.com/orgs/ferronweb/repositories?q=bench>
  - <https://github.com/ferronweb/benchmarking>
  - <https://github.com/ferronweb/benchmarking/commits/main>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/README.md>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/client/benchmark.py>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/bench>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/README.md>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/lib/env.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/lib/fetch.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/lib/build.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/lib/config.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/payloads/generate.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/scenarios/scenario1-zstd/nginx.conf.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/scenarios/scenario1-zstd/ferron3.conf.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/scenarios/scenario2-reverse-proxy/nginx.conf.sh>
  - <https://raw.githubusercontent.com/ferronweb/benchmarking/HEAD/server/scenarios/scenario2-reverse-proxy/ferron3.conf.sh>
  - <https://raw.githubusercontent.com/nginx/nginx/master/auto/cc/gcc>
  - <https://raw.githubusercontent.com/nginx/nginx/master/auto/cc/conf>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/master/src/h2load.cc>
  - <https://raw.githubusercontent.com/ferronweb/zincio/HEAD/README.md>
  - <https://raw.githubusercontent.com/ferronweb/zincio-http/HEAD/README.md>
  - <https://crates.io/api/v1/crates/zincio>
  - <https://crates.io/api/v1/crates/zincio-http>
  - <https://crates.io/api/v1/crates/ferron>
  - https://ferron.sh/benchmarks (getaddrinfo ENOTFOUND)
  - WebSearch: news.ycombinator.com results for Ferron (snippets of items 45653350, 43555249, 43228231, 43590608, 43592305, 43592054)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ferronweb/ferron`) · [data/wave14/enrich/raw/github_com_ferronweb_ferron.json](../../../data/wave14/enrich/raw/github_com_ferronweb_ferron.json) (enrichment confidence 0.6)

</details>
