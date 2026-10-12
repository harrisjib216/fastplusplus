# Hinsightd MT (hin10)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> Tiny multi-threaded io_uring HTTP/1.1 static-file server in C; edges nginx 1-16% on a 102-byte file, loses on larger files.

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | benchmark5 (Feb 2024, hinsightd 0.10.2): 102-byte index.html at ab -c 50: 124,046 vs nginx 106,615 req/s (\~1.16x); at -c 1000: 75,520 vs 74,468 (\~1.01x) (derived from page data). Slower on the 89.7kB jquery.js with sendfile disabled (-c 50: 23,656 vs 34,927 req/s, \~0.68x) and on dynamic gzip of jquery (-c 50: 727 vs 973 req/s). benchmark4 (Nov 2023, 0.10.1): index.html -c 50 127,296 vs 117,021 (\~1.09x), essentially tied or slightly behind at -c 250 (106,621 vs 106,725); jquery.js -c 50 28,277 vs 36,029. |
| **Workload** | ApacheBench (ab) concurrency sweep c=50..1000 on one 4-core machine: 102-byte index.html, 89.7kB jquery.js with sendfile disabled on all servers, and dynamic gzip of jquery.js; hinsightd 0.10.2 (io_uring, epoll fallback) vs nginx 1.25.3, lighttpd 1.4.73, Apache 2.4.58, caddy 2.7.6 (benchmark5; benchmark4 used 0.10.1, lighttpd 1.4.72, caddy 2.7.5); hinsightd, nginx and lighttpd with 4 workers; best of several runs |
| **Metric** | throughput |
| **Hardware** | 4-core machine, no hyperthreading (CPU model not stated) |
| **Adoption** | 2 stars (GitLab) |
| **Last commit** | 2024-07-02 |
| **Links** | [repository](https://gitlab.com/tiotags/hin10) · [benchmark](https://tiotags.gitlab.io/blog/benchmark5.html) |

## Verdict

These are the author's own ApacheBench runs from February 2024. The page describes them as open-request-close tests, with client and server on one 4-core, non-hyperthreaded machine; the CPU model, compiler and flags are not stated, and each figure is the best of several runs. hinsightd 0.10.2 served a 102-byte file at 124,046 req/s against nginx 1.25.3's 106,615 at -c 50 (about 1.16x), shrinking to about 1.01x at -c 750-1000. With sendfile disabled on every server it reached 0.68-0.82x nginx on the 89.7 kB jquery.js and about 0.75x on dynamic gzip.

## Use it when

- Serving tiny static files (a few hundred bytes) to many short-lived connections on a recent Linux kernel. The author's test puts it 7-16% ahead of nginx at 50-250 concurrent ab clients.
- Studying or borrowing a compact per-thread io_uring accept/read/send loop in plain C. The core netcode is a few hundred lines per file, the project page says the binary is under 200 KB, and the licence is permissive (BSD-3-Clause text, readme says MIT).
- Hobby or dev-box static hosting where one small binary with HTTPS, range and 304 support is enough and pre-1.0 software is acceptable.
- A/B experiments of io_uring against epoll in the same server: --force_epoll switches the backend (the author says the epoll path is slower and not very well tested).

## Skip it when

- Files larger than a few KB. It has no sendfile, and on the 89.7 kB jquery.js it reached only 0.68-0.82x nginx's req/s, even with sendfile turned off in nginx to match.
- CPU-bound dynamic compression: gzip of jquery.js ran at about 0.75x nginx (727 vs 973 req/s at -c 50), and compression is fixed at zlib level 9.
- High concurrency: the tiny-file lead falls to about 1% at c=500-1000. That is within the noise of a best-of-N test with client and server on one machine.
- Internet-facing production. The README warns that denial-of-service bugs are 'still likely present', and the 2024 changelog fixes several use-after-free bugs. Keepalive to reverse-proxy backends is marked 'bugged'. There is no FastCGI, no HTTP/2 and no multi-range support.
- Non-Linux hosts, and container runtimes that block io_uring syscalls (the README says podman needs --security-opt seccomp=unconfined).

## How it is fast

Each worker thread (one per core by default) owns a thread-local io_uring ring created with IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_COOP_TASKRUN. Each thread keeps one accept SQE outstanding on the shared listening socket and then handles that whole connection itself, so little is locked. Submissions are batched: one io_uring_submit per loop pass, and up to 64 CQEs reaped per wait. File open, read, send and close are all asynchronous io_uring operations. Bodies smaller than the \~8 KB buffer are condensed with the headers, and TCP_CORK is set only for larger bodies. That suits the connect-request-close pattern of the tiny-file test. There is no sendfile or splice: file data is read into user-space buffers and then sent, which is why it falls behind nginx on the 89.7 kB file.

## Compared with alternatives

uWebSockets, libhv and io_uring-echo-server (frevib) are libraries or demos you build a server on, and F-Stack keeps nginx itself but moves its network path to DPDK. Pick hinsightd only if you want a ready-made, very small C static-file server whose per-thread io_uring loop you can read end to end. For real static serving, nginx remains the safer choice.

## Integration

| | |
|---|---|
| **Form** | Standalone server binary (hinsightd) built from source with CMake/Ninja. The build also produces and installs an undocumented libhin library with headers. This branch has no distro packages; a Dockerfile is provided. |
| **Dependencies** | liburing, zlib, pthreads, glibc or musl; OpenSSL or LibreSSL (on by default, can be turned off); libsystemd optional (off by default); CMake to build (the README uses Ninja). |
| **Minimum toolchain** | Any C compiler with GNU extensions (__thread, _GNU_SOURCE). CMakeLists.txt declares CMake 3.17 but calls cmake_path unconditionally, and cmake_path needs CMake 3.20. The README says Linux &gt;= 5.6, but the ring is created with IORING_SETUP_SINGLE_ISSUER (Linux 6.0+) and COOP_TASKRUN (5.19+). On older kernels ring setup fails and the server falls back to epoll. |
| **Platforms** | Linux only (io_uring with an epoll fallback, statx, signalfd); glibc and musl. CPU architectures: not documented. |
| **Thread safety** | Inside the server: one event loop and io_uring ring per thread in thread-local storage, each client stays on the thread that accepted it, and shared server, vhost and file-cache state uses locks and atomic helpers. libhin has no documented thread-safety contract. |
| **Drop-in for the baseline** | partial: it replaces nginx only for plain static-file serving (plus a basic reverse proxy since April 2024). It has its own CLI/ini config with no nginx.conf compatibility, and lacks FastCGI, HTTP/2 and sendfile. |

## Gotchas

- Kernel mismatch: the README says Linux &gt;= 5.6, but io_uring setup requests IORING_SETUP_SINGLE_ISSUER (6.0+). On older kernels it logs 'io_uring_init failed' and every thread runs the slower, less-tested epoll path, where file reads become blocking pread calls.
- The gzip comparison may not be like-for-like. hinsightd hard-codes deflateInit2(Z_BEST_COMPRESSION), while the benchmark's nginx.conf takes gzip_comp_level from a template variable whose value is not shown (nginx's default is 1).
- The README lags the code. Its roadmap still says 'readd reverse proxy', but rproxy landed in April 2024 commits (after the benchmarks). It also says MIT while docs/LICENSE.txt holds BSD-3-Clause text.
- The benchmarks cover 0.10.1 and 0.10.2 only. Later commits (reverse proxy, an SSL refactor, POST support, a global memory limit) are untagged and unbenchmarked.

## Known shortcomings

- Mixed results: \~1.16x nginx on index.html at -c 50 falling to \~1.01x at -c 1000, slower on jquery.js (\~0.68x) and gzip (\~0.75x); the readme itself says 'almost nginx level'. Stale since 2024-07. Licence conflict: docs/LICENSE.txt is BSD-3-Clause, the readme says MIT.
- The README's Linux 5.6 floor is wrong: io_uring setup uses SINGLE_ISSUER (6.0) and COOP_TASKRUN (5.19); older kernels fall back to a lightly tested epoll path with blocking pread. No sendfile or splice (files go through \~8 KB buffers), hence 0.68-0.82x nginx on the 89.7 kB file. The gzip comparison may be unfair (hinsightd hard-codes zlib level 9; nginx's level is a hidden template variable, default 1). The small-file win shrinks from 1.16x at -c 50 to \~1.01x at -c 500-1000, best-of-N with client and server on one 4-core machine. CMake 3.17 declared but cmake_path needs 3.20. README warns DoS bugs are still likely; 2024 changelog fixes many use-after-free bugs; proxy keepalive 'bugged'; Podman needs seccomp=unconfined; post-v0.10.3 commits untagged and unbenchmarked; no FastCGI, HTTP/2 or multi-range; 2 stars.

## Caveats and trade-offs

Author's own blog benchmark; client and server on the same 4-core machine; no CPU model, compiler or build flags stated; best-of-N runs rather than medians. The win is only on tiny-file connection handling and fades to \~1% at high concurrency; hinsightd is clearly slower than nginx on larger files and gzip. The README itself says 'almost nginx level of performance'. License conflict: readme.md says MIT but docs/LICENSE.txt contains BSD 3-Clause text (both OSI-approved). Development branch with a reduced feature set (no reverse proxy/fastcgi yet).

No sendfile support in this test; wins only on the tiny static file and only by a small margin (1-9%); loses to nginx on the larger jquery.js payload; author states the branch 'still needs some optimization and testing'

## Maintenance

Stale: last commit 2 July 2024 (last tag v0.10.3, Feb 2024), 2 GitLab stars, no issues filed, no packages for this branch. The code is permissively licensed and small enough to read or vendor, but treat it as an unmaintained hobby server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Author's own blog posts (benchmark4, benchmark5) give ApacheBench req/s tables against nginx 1.25.3 and others, but state no CPU model, compiler or flags, and take the best of several runs; first-party numbers with partial methodology, so C.
- **Verifier notes:** hin10 is the multi-threaded 0.10 branch of hinsightd (hin9 is the single-threaded legacy branch). It differs from the rejected hinsightd record only on licence: a licence file exists at docs/LICENSE.txt (BSD-3-Clause text; readme says MIT). Win/loss stays mixed and it stays stale (last commit 2024-07-02). The readme and the project MT page cite benchmark5, not benchmark4, so benchmark_url was moved there.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://gitlab.com/tiotags/hin10>
  - <https://gitlab.com/api/v4/projects/tiotags%2Fhin10>
  - <https://gitlab.com/api/v4/projects/48862888/repository/commits?per_page=3>
  - <https://gitlab.com/api/v4/projects/48862888/repository/tree?recursive=true&per_page=100>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/readme.md>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/docs/LICENSE.txt>
  - <https://tiotags.gitlab.io/blog/benchmark4.html>
  - <https://tiotags.gitlab.io/blog/benchmark5.html>
  - <https://tiotags.gitlab.io/hinsightd/mt.html>
- **Sources the enricher read:**
  - <https://gitlab.com/tiotags/hin10/-/raw/master/readme.md>
  - <https://gitlab.com/api/v4/projects/tiotags%2Fhin10>
  - <https://gitlab.com/api/v4/projects/48862888/repository/tree?recursive=true&per_page=100>
  - <https://gitlab.com/api/v4/projects/48862888/repository/tree?recursive=true&per_page=100&page=2>
  - <https://gitlab.com/api/v4/projects/48862888/repository/commits?per_page=10>
  - <https://gitlab.com/api/v4/projects/48862888/repository/tags>
  - <https://gitlab.com/api/v4/projects/48862888/issues?per_page=50&state=all>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/CMakeLists.txt>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/docs/changelog.md>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/docs/LICENSE.txt>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/hin/conf.h>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/hin/hin.h>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/netcode/uring.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/netcode/hin.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/netcode/server.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/netcode/epoll.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/netcode/pipe.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/http/server/file.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/http/utils/compress.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/system/main.c>
  - <https://gitlab.com/tiotags/hin10/-/raw/master/src/system/limits.c>
  - <https://tiotags.gitlab.io/blog/benchmark5.html>
  - <https://tiotags.gitlab.io/blog/benchmark4.html>
  - <https://tiotags.gitlab.io/hinsightd/mt.html>
  - <https://tiotags.gitlab.io/assets/f/f1/nginx.conf>
  - <https://nginx.org/en/docs/http/ngx_http_gzip_module.html>
  - <https://man7.org/linux/man-pages/man2/io_uring_setup.2.html>
  - <https://cmake.org/cmake/help/latest/command/cmake_path.html>
  - <https://hn.algolia.com/api/v1/search?query=hinsightd>
  - <https://hn.algolia.com/api/v1/search?query=tiotags>
  - <https://hn.algolia.com/api/v1/items/38302070>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://gitlab.com/tiotags/hin10`) · [data/wave5/enrich/raw/gitlab_com_tiotags_hin10.json](../../../data/wave5/enrich/raw/gitlab_com_tiotags_hin10.json) (enrichment confidence 0.45)

</details>
