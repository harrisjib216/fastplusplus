# agensio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Pre-alpha C++ static-file, FastCGI and reverse-proxy web server on Asio; outpaces nginx on most HttpArena infrastructure rows.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (HttpArena nginx entry with a custom C handler module); HttpArena rows for h2o and Drogon also compared |
| **Claimed result** | static-tls-1024: 1,191,970 vs nginx 720,869 req/s (1.65x, derived from page data). baseline-h2-1024: 14,210,433 vs 3,320,285 (4.3x, derived). baseline-h2c-1024: 14,782,707 vs 2,490,271 (5.9x, derived). json-h2c-1024: 4,567,724 vs 1,730,838. static-h2-1024: 1,420,432 vs 796,607. baseline-h3-64: 8,634,941 vs 4,849,624. static-h3-64: 745,030 vs 361,025. baseline-4096 (HTTP/1.1): 3,558,559 vs 3,284,513 (1.08x); json-tls-4096: 1,716,076 vs 1,313,755. limited-conn-4096: 2,577,049 vs nginx 2,626,297 (nginx 2% ahead). Memory on baseline-4096: 297MiB vs nginx 3.5GiB. Against zix (the Zig leader entry): baseline-h2c-256 15,185,367 vs 13,956,726 (1.09x), -1024 14,782,707 vs 14,569,901, -4096 13,627,524 vs 13,411,078, at 1648.6% vs 3999.4% CPU; but zix is ahead on baseline-4096 (4,442,329), json-h2c (6,821,589 vs 4,567,724) and pipelined (58,761,616 vs 4,958,241). Against h2o and Drogon: ahead of Drogon on baseline-4096 (3,558,559 vs 2,022,710), json-tls (1,716,076 vs 253,055), limited-conn (2,577,049 vs 1,694,883) but behind Drogon on pipelined (4,958,241 vs 7,801,404); behind h2o on baseline-4096 (3,641,609), baseline-h2-1024 (15,633,023) and limited-conn (2,651,569), ahead of h2o on static-h2-1024 (1,420,432 vs 341,251) and json-tls (1,716,076 vs 1,229,462). |
| **Workload** | HttpArena public leaderboard profiles (gcannon, h2load, h2load-h3 load generators; best of several runs per profile): HTTP/1.1, h2, h2c, h3 and TLS rows serving the arena's baseline, JSON and static-file endpoints. agensio's arena handler module is compiled in, as is nginx's. |
| **Metric** | throughput |
| **Hardware** | HttpArena current.json: AMD Ryzen Threadripper PRO 3995WX 64-Cores (128 threads), 251Gi RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), CPU governor performance. |
| **Compiler and flags** | From frameworks/agensio/Dockerfile (agensio tag v0.1.0-alpha.23): debian:trixie with build-essential (GCC, version not pinned in the Dockerfile; Debian 13 ships GCC 14.2, which the agensio CLAUDE.md names), cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DAGENSIO_TESTS=OFF -DAGENSIO_NATIVE=ON -DAGENSIO_HTTPARENA=ON, which adds -march=native; AGENSIO_HARDEN is on by default in CMakeLists.txt (-fstack-protector-strong, -ftrivial-auto-var-init=zero, _FORTIFY_SOURCE=2, _GLIBCXX_ASSERTIONS, PIE with -z relro -z now), and CMake's Release default for GCC is -O3 -DNDEBUG (inferred). nginx entry: 1.31.4 on debian:trixie built with --with-cc-opt='-O3 -march=native -DNDEBUG', HTTP/2 and HTTP/3 modules, ngx_brotli and the custom ngx_http_httparena_module, linked against Debian trixie's OpenSSL from libssl-dev (the Dockerfile comment mentions quictls, but no step builds it). |
| **Adoption** | 1 star; HttpArena leaderboard entry added 2026-10-06 (PR #1511) |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/YiannisBourkelis/agensio) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json) |

## Verdict

On HttpArena's public board (AMD Threadripper PRO 3995WX, Ubuntu 24.04, Docker; agensio v0.1.0-alpha.23 built with GCC from Debian trixie at CMake Release plus -march=native and its hardening defaults, nginx 1.31.4 at -O3 -march=native with a custom C handler module), agensio led nginx on static-tls (1.19M vs 0.72M req/s), the HTTP/2 and h2c baselines (14.2-14.8M vs 2.5-3.3M) and HTTP/3 rows, edged it on HTTP/1.1 baseline-4096 (1.08x), and trailed it by 2 percent on limited-conn; h2o stays ahead on baseline-4096 and baseline-h2, zix on json-h2c and pipelined, Drogon on pipelined.

## Use it when

- Serving static sites whose assets fit in the memory cache (default 4 MB per file, 256 MB total), especially over TLS and HTTP/2, where the HttpArena static-tls and static-h2 rows show 1.65x and 1.8x nginx's req/s.
- Small VPS hosting where CPU and memory per request matter: the author's single-worker Ryzen 9 9900X runs show 1.9-2.0 us vs nginx 3.0 us of CPU per plain 1 KB request and 2.7-2.8 vs 4.3-4.4 us over HTTPS, and HttpArena records 297 MiB against nginx's 3.5 GiB on baseline-4096.
- Many small HTTP/2 or HTTP/3 requests per connection, where agensio reached 4.3-5.9x nginx on the h2/h2c baseline rows at about a quarter of nginx's CPU.
- PHP hosting (Laravel, WordPress, Statamic, Drupal) on a single Linux box, if you can accept pre-alpha software and want the bundled per-application hardening presets.

## Skip it when

- Anything you cannot afford to have exposed or down: the project started 2026-09-19, has one star and a handful of users, and its README warns of undiscovered bugs, some possibly security bugs; alpha.56 and alpha.57 fixed an HTTP/2 timeout loop that could stall a worker and a TLS slow-client cut-off found by the author's own audit.
- Deployments that need on-the-fly compression, directory listing, rate limiting, wildcard or DNS-01 certificates, OCSP stapling or HTTP/3 0-RTT; none are implemented.
- Non-Linux production hosts: macOS builds and Windows compiles, but only Linux is tested release by release.
- Large streamed files over TLS: the author's own tables show nginx level or ahead on 10 MB streams (no kTLS yet, so TLS uses the copy path).
- HTTP/1.1 pipelining-heavy load: on HttpArena's pipelined profile agensio does 4.96M req/s against Drogon 7.8M and zix 58.8M.

## How it is fast

One Asio io_context per worker thread, each with its own SO_REUSEPORT acceptor, so a connection never leaves its core and the request path takes no locks. Static files come from a two-level in-memory cache (a shared store touched under a mutex only on miss, insert or evict, plus a per-worker index that makes hits lock-free) holding prebuilt header blocks and pre-compressed .br/.gz twins, revalidated by stat() at most once per interval. The HTTP/2 layer batches a read's answers into one send (one sendmsg per \~57 answers in the author's profile) and uses an HPACK dynamic table so a small response's header block shrinks from 48 to 8 bytes; small HTTP/1 responses go out as one gathered write of prebuilt fragments with a once-per-second Date header.

## Compared with alternatives

Pick agensio over Drogon or cinatra when you want a configured server in front of static files, PHP or a proxied app rather than a C++ framework to write handlers in; over Lwan or Kore when you need HTTP/2, HTTP/3, ACME and FastCGI out of the box and can tolerate pre-alpha maturity. Pick Drogon if you write C++ request handlers or depend on pipelining throughput.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (CMake build) |
| **Dependencies** | standalone Asio 1.38+ (fetched if absent), vendored toml++ 3.4.0; optional OpenSSL 3 for TLS (3.5+ for HTTP/3), optional zlib (archive installs) and libxcrypt (password auth) |
| **Minimum toolchain** | C++20 (CMakeLists sets CMAKE_CXX_STANDARD 20), GCC 12+, Clang 16+, Apple clang 15+ or MSVC 2022 per README, CMake 3.24+; the design notes target GCC 14+ and Clang 18+ |
| **Platforms** | Linux (epoll, SO_REUSEPORT) supported; macOS (kqueue) builds and runs; Windows compiles but is untested |
| **Thread safety** | Not applicable as a library; internally one worker per hardware thread with no cross-worker state on the request path |
| **Drop-in for the baseline** | partial — covers nginx's static, FastCGI and reverse-proxy roles with its own TOML configuration; nginx.conf does not carry over and several nginx features (gzip on the fly, rate limiting, OCSP stapling) are missing |

## Gotchas

- The baseline and JSON rows run a benchmark-only handler (src/handlers/httparena.cpp, compiled only with -DAGENSIO_HTTPARENA=ON and 'never in a release'), and its JSON path pre-serializes every item except the total at dataset load (load_httparena_dataset builds item.prefix; still the same code at HEAD), while nginx's module runs ngx_sprintf over every field per request; HttpArena's infrastructure rule for json-tls and json-h2c requires per-request serialization, so the 1.31x json-tls and 2.64x json-h2c leads over nginx partly measure skipped work. The PR #1511 review (merged 2026-10-06) raised no comment on this.
- The h2 and h2c rows are load-generator bound: the author's own CLAUDE.md notes h2load at 1200 percent bounds the pinned row and that agensio, h2o and zix all land at 12-16M req/s; compare the CPU column (agensio 1.5-1.9k percent vs 3-4k for zix and h2o) rather than req/s there.
- The static rows depend on serving the arena's pre-compressed .br twins: the author's first local run, before twins were served, had agensio at 0.36-0.42 of nginx's req/s because nginx sent 15 KB brotli bodies against 58-60 KB raw ones. The HttpArena nginx entry also runs without open_file_cache, which the infrastructure tier allows and which widens the static-tls gap.
- Numbers come from the alpha.23 build while releases have reached alpha.72. The alpha.57 change that splits large cached bodies into 64 KB pieces touches the HTTP/1 static path, but only for bodies beyond the first write plus one 64 KB piece; the arena's brotli twins and binary files are all under about 60 KB, so the measured static-tls path is unaffected. agensio's hardening flags (stack protector, _FORTIFY_SOURCE=2, _GLIBCXX_ASSERTIONS, zero-init locals, PIE and RELRO) were on during the run.

## Known shortcomings

- HttpArena rows match the agensio, nginx, zix, h2o and Drogon result files, but the JSON profiles pre-serialise item JSON at load time (against HttpArena's infrastructure rule and unlike the nginx module's per-request sprintf), so json-tls 1.31x and json-h2c 2.64x are not like-for-like; h2 and h2c rows against zix and h2o look load-generator bound. agensio ran with hardening on and nginx links Debian OpenSSL, not quictls. Loses to nginx on limited-conn, to zix on baseline-4096 and json-h2c, to Drogon on pipelined. Numbers are from v0.1.0-alpha.23; the repo is now at alpha.72, pre-alpha with 1 star.
- Enricher: the JSON harness flaw holds at HEAD (load_httparena_dataset in src/handlers/httparena.cpp pre-serialises item JSON at load, breaking HttpArena's per-request serialisation rule; PR #1511 merged without comment on it), so json-tls 1.31x and json-h2c 2.64x partly measure skipped work. Baseline and JSON rows run a benchmark-only handler (-DAGENSIO_HTTPARENA=ON, 'never in a release'). h2 and h2c rows are load-generator bound (the author's own notes show h2load at 1200%). Static rows depend on precompressed .br twins; before them the author's lite run had agensio at 0.36-0.42 of nginx req/s. The alpha.57 large-body chunking fix does not touch the measured static-tls path.

## Caveats and trade-offs

Pre-alpha: the project started 2026-09-19 (CHANGELOG alpha.1), the README status line still reads 0.1.0-alpha.23 while tags have reached v0.1.0-alpha.72 (2026-10-12), and the README warns of unfound bugs, some possibly security bugs; post-alpha.23 releases fixed security issues found by the author's own audit (alpha.56: the HTTP/2 per-stream timeout check could stall a worker), none of which appears to change the measured request path. The HttpArena entry was submitted by the project author (meta.json maintainer YiannisBourkelis) and the committed numbers come from the alpha.23 build (frameworks/agensio/Dockerfile AGENSIO_REF=v0.1.0-alpha.23), while the repo has since moved on. In HttpArena the benchmark endpoints are a handler module compiled into each server, so the rows measure the server's request path on tiny canned responses, not real applications. JSON rows are not like-for-like: agensio's handler (src/handlers/httparena.cpp, load_httparena_dataset) pre-serializes every item's JSON except the total at dataset load and only appends prefixes and total\*m per request, while nginx's ngx_http_httparena_module.c deliberately keeps typed fields and runs ngx_sprintf over every field per request; HttpArena's infrastructure rule for json-tls says the body must be serialized per request and no pre-serialized response cache qualifies, so the json-tls 1.31x and json-h2c 2.64x leads over nginx partly measure skipped serialization. On the h2 and h2c rows agensio, zix and h2o all land at 14-16M req/s while agensio uses 1.5-1.9k percent CPU against 3-4k for zix and h2o, so those rows look load-generator bound and the gap to zix and h2o is within noise; the CPU column is the better discriminator there, and nginx at 2.5-3.4M and about 6400% CPU is clearly server bound. nginx's config has no open_file_cache and 65536 worker_connections, which probably explains its 3.5GiB memory and part of the static-TLS gap against agensio's in-memory file cache (which revalidates by stat at most once a second; the infrastructure tier allows in-memory caching); nginx also offers TLS 1.3 only and links Debian trixie's OpenSSL (its Dockerfile comment mentions quictls but no step builds it). agensio was measured with its hardening defaults on (stack-protector-strong, _FORTIFY_SOURCE=2, _GLIBCXX_ASSERTIONS, -ftrivial-auto-var-init=zero, PIE and full RELRO), a cost nginx's -O3 -march=native build does not carry. agensio also loses to nginx on limited-conn, to h2o on baseline and baseline-h2, to zix on baseline-4096 and json-h2c, and to Drogon on pipelined. All servers here are typed 'infrastructure' (Drogon is 'flagship'). The agensio repo's own CLAUDE.md reports a CPU-per-request advantage over nginx on an M1 Pro (2026-09-15) and a Ryzen 9 9900X (2026-09-16, GCC 14.2, nginx 1.26.3, wrk 4.1), with result files committed under bench/results/ (for example 20260916-1951\*.md); a few rows (10 MB streams, HTTPS 10 MB, HTTP 100 KB on macOS) favour nginx by the author's own table. Rows are the best of several runs per profile. [retier] Enricher: JSON rows pre-serialise item JSON at load (src/handlers/httparena.cpp), so json-tls 1.31x and json-h2c 2.64x partly measure skipped work; baseline and JSON rows use a benchmark-only build flag (-DAGENSIO_HTTPARENA=ON); h2 and h2c rows are load-generator bound; static rows depend on precompressed .br twins.

Static-file, reverse-proxy and FastCGI (PHP) server on standalone Asio with its own HTTP/1.1, HTTP/2 and HTTP/3 (QUIC, needs OpenSSL 3.5) layers; one event loop per core and a lock-free in-memory file cache. No on-the-fly compression (serves pre-compressed .br/.gz twins), no directory listing, no rate limiting, no wildcard or DNS-01 certificates, no OCSP stapling, no HTTP/3 0-RTT; Linux only. Memory per idle HTTP/2 connection is 19 KB vs nginx 7.5 KB (agensio CLAUDE.md).

## Maintenance

Very active pre-alpha (317 commits, releases almost daily, alpha.72 on 2026-10-12) and MIT-licensed, but one star and a few weeks of field use, so treat it as an experiment rather than an nginx replacement for production yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Every quoted number matches site/data/results/agensio.json and the sibling nginx.json, zix.json, h2o.json and drogon.json in MDA2AV/HttpArena; the code is public (frameworks/agensio/{Dockerfile,agensio.toml,start.sh}, agensio src/handlers/httparena.cpp at v0.1.0-alpha.23, frameworks/nginx/{Dockerfile,nginx.conf,ngx_http_httparena_module.c}), the build flags are stated (CMake Release -march=native, nginx --with-cc-opt='-O3 -march=native -DNDEBUG' on debian:trixie GCC) and site/data/current.json names the Threadripper PRO 3995WX, so A on the HttpArena precedent (zix, nilo, dusty, actix).
- **Verifier notes:** All rps, CPU and memory figures for agensio, nginx, zix, h2o and Drogon check out against the HttpArena result JSONs; MIT, 1 star, 317 commits, last commit 2026-10-12, latest tag v0.1.0-alpha.72. Shortcomings: json-tls and json-h2c wins come partly from pre-serializing item JSON at load, against the profile's infrastructure rule and unlike nginx's per-request sprintf; h2/h2c rows look load-generator bound; numbers from alpha.23 while the project is at alpha.72; author-submitted entry; the record's claim that raw result files are absent was wrong (bench/results/ holds them).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 5 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/agensio>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/agensio.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/start.sh>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/nginx>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/ngx_http_httparena_module.c>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/static-tls/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-tls/implementation.md>
  - <https://github.com/YiannisBourkelis/agensio>
  - <https://github.com/YiannisBourkelis/agensio/commits>
  - <https://github.com/YiannisBourkelis/agensio/tags>
  - <https://github.com/YiannisBourkelis/agensio/tree/main/bench>
  - <https://github.com/YiannisBourkelis/agensio/tree/main/bench/results>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/README.md>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/v0.1.0-alpha.23/src/handlers/httparena.cpp>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/v0.1.0-alpha.23/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/YiannisBourkelis/agensio>
  - <https://github.com/YiannisBourkelis/agensio/tree/main/bench>
  - <https://github.com/YiannisBourkelis/agensio/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/README.md>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/bench/nginx.conf>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/HEAD/src/handlers/httparena.cpp>
  - <https://raw.githubusercontent.com/YiannisBourkelis/agensio/v0.1.0-alpha.23/src/handlers/httparena.cpp>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/agensio.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/data/dataset.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-tls/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/static-tls/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h2/json-h2c/implementation.md>
  - <https://github.com/MDA2AV/HttpArena/pull/1511>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/yiannisbourkelis/agensio`) · [data/wave5/enrich/raw/github_com_yiannisbourkelis_agensio.json](../../../data/wave5/enrich/raw/github_com_yiannisbourkelis_agensio.json) (enrichment confidence 0.75)

</details>
