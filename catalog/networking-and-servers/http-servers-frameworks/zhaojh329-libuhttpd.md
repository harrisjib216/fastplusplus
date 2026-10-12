# libuhttpd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Small embeddable C HTTP/1.1 server library on libev for embedded Linux; one first-party wrk run shows 1.74x nginx req/s.

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | libuhttpd 281328.83 requests/sec vs nginx 161390.39 requests/sec with identical wrk parameters (about 1.74x, derived from page data); latency avg 2.12 ms vs 3.54 ms. |
| **Workload** | wrk -t4 -c400 -d10s fetching a small static test.html over localhost from nginx on port 80 and from libuhttpd on port 8080. |
| **Metric** | throughput |
| **Adoption** | 432 stars |
| **Last commit** | 2025-08-08 |
| **Links** | [repository](https://github.com/zhaojh329/libuhttpd) · [benchmark](https://github.com/zhaojh329/libuhttpd) |

## Verdict

One first-party wrk -t4 -c400 -d10s run per server over localhost fetching test.html: libuhttpd on port 8080 did 281,328.83 req/s (2.12 ms average latency) against nginx on port 80 at 161,390.39 req/s (3.54 ms), about 1.74x (derived from page data). No compiler or flags, CPU, kernel, nginx version or configuration, libuhttpd version, server binary or process count is given, and responses differed in size (about 249 vs 203 bytes).

## Use it when

- OpenWrt or embedded Linux devices that need a web UI or REST endpoint inside an existing C daemon (opkg packages libuhttpd and libuhttpd-nossl exist)
- Programs that already run a libev loop and want HTTP handlers on it without a separate server process
- Small static files plus CGI or C handlers at modest concurrency, where a few hundred KB of library beats shipping nginx
- TLS on constrained targets, where mbedTLS or wolfSSL are supported backends next to OpenSSL

## Skip it when

- As an nginx replacement: no config file, reverse proxy, caching, HTTP/2 or virtual hosts; the features list names HTTP/1.1, CGI, plugins, ranges and uploads only
- Throughput-critical public services: the only evidence is one 2021 localhost wrk run against an nginx of unknown version and configuration
- Non-Linux platforms: the code relies on accept4, sendfile from sys/sendfile.h, SO_REUSEPORT and prctl (examples)
- Long-term security-sensitive deployments: it depends on the nodejs http-parser, whose upstream says it is not actively maintained (llhttp is its successor), and the project itself is stale (last code change 2025-08-08)
- Requests with 50 or more headers (UHTTPD_MAX_HEADER_NUM 50 is a compile-time limit) or idle connections that need more than the fixed 30 s timeout

## How it is fast

Each worker is one libev event loop with non-blocking accept4() sockets. Requests are parsed by the callback-driven nodejs http-parser, which stores header and URL offsets into the connection's read buffer instead of copying them. Responses are printf'd into a per-connection write buffer; files over 2 KB go out with sendfile() and smaller ones are read into the buffer. Multi-core scaling comes from nginx-style pre-forked worker processes, either sharing one listening socket or each with its own SO_REUSEPORT listener.

## Compared with alternatives

Pick it over Kore, Lwan or Sogou Workflow when the target is an OpenWrt or embedded Linux C program that needs a small embeddable HTTP/1.1 server on its existing libev loop. For server-class throughput, Kore (best-of-four wrk runs against nginx) and Lwan (TechEmpower results) have stronger evidence and more features.

## Integration

| | |
|---|---|
| **Form** | shared lib by default; static lib with -DBUILD_STATIC=ON |
| **Dependencies** | libev; git submodules nodejs/http-parser, zhaojh329/buffer, zhaojh329/log and zhaojh329/ssl; optional OpenSSL, mbedTLS (3.x since 3.14.2) or wolfSSL; libdl for plugins |
| **Minimum toolchain** | C (gnu99) with CMake 3.5+; builds with -O (that is, -O1) and -Werror by default (BUILD_WERROR option) |
| **Platforms** | Linux only, including OpenWrt cross builds |
| **Thread safety** | not documented; each uh_server runs on one libev loop and scaling is by forked processes, not threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the README Benchmark section (added 2021-01-03, commit 8070cc2) shows one 10 s wrk run per server and does not say which libuhttpd binary or how many processes ran, nor the nginx version, worker count or access_log setting. nginx's stock config logs every request, while libuhttpd's examples log nothing below LOG_ERR; with the README's '-v' run example they would log two lines per request. At about 249 bytes per nginx response versus 203 for libuhttpd (wrk binary units), test.html must be tiny, so the run measures per-request overhead, not file serving.
- Bug in the file handler (src/file.c __serve_file): files of 2 KB or less are read with 'while (len) len -= buffer_put_fd(...)'. buffer_put_fd returns 0 at EOF and -1 on a read error, so a file that shrinks between stat() and read(), or a read error, spins that loop forever and hangs the whole event loop. This matters for status files in /tmp that are rewritten on embedded devices.
- Bug in the multi-process examples (example/multi_process_server.c and multi_process_server_reuseport.c): they keep worker PIDs in pid_t workers[MAX_WORKER=10], but the worker count defaults to get_nprocs() and -w is unchecked, so on hosts with 12 or more CPUs (11 or more for the reuseport variant) the fork loop writes past the stack array.
- Open build issues (#18 nossl not compiling, #25 cmake error) and -Werror on by default can break builds on newer compilers; pass -DBUILD_WERROR=OFF. A report of random 5-22 s stalls behind an nginx HTTPS reverse proxy (#28) was closed as not planned.

## Known shortcomings

- First-party single wrk run (281,329 vs nginx 161,390 req/s, 1.74x derived) with the nginx config and worker count unknown, differing response sizes (about 249 vs 203 bytes) and no build or hardware details. Last commit 2025-08-08.
- Enricher: the benchmark (commit 8070cc2, 2021-01-03) gives no binary, process count, nginx config or access_log setting, and test.html is tiny (about 249 vs 203 bytes), so it measures per-request overhead. Bugs: src/file.c __serve_file loops forever for files of 2 KB or less at EOF or on a read error (buffer_put_fd returns 0 or -1), hanging the event loop; example/multi_process_server\*.c overflows workers[MAX_WORKER=10] on hosts with 12+ CPUs. The library builds at -O1 with -Werror by default; the bundled nodejs/http-parser is unmaintained upstream.

## Caveats and trade-offs

README only (Benchmark section, undated; current release 3.14.2); no compiler, flags, CPU, kernel, nginx version or nginx configuration (worker_processes, access logging, sendfile) stated, so tier C. The bundled example/simple_server.c is a single libev event loop serving files from a docroot; the README does not say which server binary or how many processes libuhttpd used, nor how many nginx workers ran. Response sizes differ: wrk reports binary units, so nginx read 385.09 MB for 1,622,012 requests (about 249 bytes each) and libuhttpd 547.18 MB for 2,826,394 requests (about 203 bytes each); the servers returned different headers, so the comparison is not like for like. Single 10 s run on localhost with client and server sharing the machine, no repeats; test.html is not described. Last commit is a CMake 4 compatibility fix merged 2025-08-08.

Embedded-Linux oriented HTTP/HTTPS server library on libev and http-parser (OpenSSL, mbedtls or wolfssl); CGI, plugins, range requests and nginx-style multi-process model, but far fewer features than nginx.

## Maintenance

Stale but usable: release 3.14.2 (2024-10-26), last commit a CMake 4 compatibility fix merged 2025-08-08, MIT-licensed, small and packaged for OpenWrt; issues get sporadic answers, and the bundled http-parser is unmaintained upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark section shows two wrk runs (nginx on port 80: 161390.39 req/s, 3.54 ms avg latency; libuhttpd on port 8080: 281328.83 req/s, 2.12 ms), so the 1.74x ratio (derived from page data) is correct. These are first-party numbers with no benchmark script, no compiler or flags, no CPU, no nginx version or configuration, which is tier C.
- **Verifier notes:** Numbers and metadata check out (MIT, 432 stars, 75 forks, not a fork, last commit 2025-08-08, so stale). Shortcomings to record: first-party single wrk run with unknown nginx configuration and worker count, different response header sizes (about 249 vs 203 bytes per response), no build or hardware details.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/zhaojh329/libuhttpd>
  - <https://github.com/zhaojh329/libuhttpd/commits>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/README.md>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/example/simple_server.c>
- **Sources the enricher read:**
  - <https://github.com/zhaojh329/libuhttpd/commits>
  - <https://github.com/zhaojh329/libuhttpd/blame/master/README.md>
  - <https://github.com/zhaojh329/libuhttpd/commit/8070cc20c990557c42d418a8307472ae59bad41b>
  - <https://github.com/zhaojh329/libuhttpd/issues?q=is%3Aissue>
  - <https://github.com/zhaojh329/libuhttpd/issues/28>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/README.md>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/BUILDOPENWRT.md>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/config.h.in>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/uhttpd.h>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/uhttpd.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/connection.h>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/connection.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/file.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/cgi.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/src/utils.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/example/CMakeLists.txt>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/example/simple_server.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/example/multi_process_server.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/example/multi_process_server_reuseport.c>
  - <https://raw.githubusercontent.com/zhaojh329/libuhttpd/HEAD/example/handler.c>
  - <https://raw.githubusercontent.com/zhaojh329/log/HEAD/log.h>
  - <https://raw.githubusercontent.com/zhaojh329/log/HEAD/log.c>
  - <https://raw.githubusercontent.com/zhaojh329/buffer/HEAD/buffer.c>
  - <https://raw.githubusercontent.com/zhaojh329/buffer/HEAD/buffer.h>
  - <https://raw.githubusercontent.com/nodejs/http-parser/HEAD/README.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/zhaojh329/libuhttpd`) · [data/wave5/enrich/raw/github_com_zhaojh329_libuhttpd.json](../../../data/wave5/enrich/raw/github_com_zhaojh329_libuhttpd.json) (enrichment confidence 0.6)

</details>
