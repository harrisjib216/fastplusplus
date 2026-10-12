# zeemo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Zig` · `no license` · 🟢 active

> Zig io_uring HTTP/1.1 benchmark server and young library; 1.35x nginx's HttpArena baseline rate, ties libreactorng.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native -DNDEBUG); same suite rows for libreactorng, libioma, mongoose, h2o (C) and Drogon, agensio, userver (C++) |
| **Claimed result** | baseline-4096: 4,422,489 req/s vs nginx 3,284,513 (1.35x, derived from page data), h2o 3,641,609 (1.21x), mongoose 3,707,598 (1.19x), libioma 4,255,834 (1.04x), libreactorng 4,377,377 (1.01x, within noise), Drogon 2,022,710 (2.19x). pipelined-4096: 49,860,224 vs libreactorng 43,424,448 (1.15x), nginx 4,037,345 (12.4x), Drogon 7,801,404 (6.4x). Not faster on limited-conn-4096: 2,606,127 vs nginx 2,626,297 (0.99x), libioma 2,707,029 (0.96x). |
| **Workload** | HttpArena baseline (mixed GET/POST with query parsing, 4096 connections), 16x pipelined and limited-conn profiles on a bare-metal Zig HTTP/1.1 server: one io_uring reactor process per logical CPU via SO_REUSEPORT, hand-written incremental parser, registered provided-buffer rings. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json, site/content/docs/hardware/_index.md). The server container is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) for these profiles and the load generator (gcannon for HTTP/1.1, wrk for the TLS profiles, h2load for h2c) runs on the other half over loopback; 5 s runs, best of 3 (scripts/lib/common.sh RUNS=3, scripts/lib/profiles.sh). current.json is undated and describes the machine now, not necessarily at the date of each results file. |
| **Compiler and flags** | zeemo: Zig 0.16.0 official tarball on ubuntu:24.04, zig build -Dtarget=x86_64-linux-musl --release=fast (ReleaseFast, stripped static musl binary on scratch); no -Dcpu is given, so Zig compiles for the baseline x86-64 CPU rather than the host, while the C rows use -march=native (frameworks/zeemo/Dockerfile, build.zig). C/C++ rows: nginx 1.31.4 with a custom C handler module, --with-cc-opt='-O3 -march=native -DNDEBUG' (debian:trixie); libreactorng 7a65f8b configured CFLAGS='-O3 -march=native' and its server built gcc -O3 -march=native (no LTO); libioma and mongoose gcc-14 -O3 -march=native -flto; h2o clang CMake Release -march=native -mtune=native, no LTO; agensio CMake Release -DAGENSIO_NATIVE=ON; userver service CMake Release -march=native on the prebuilt userver v3.2 image; Drogon handler only, CMake Release on the unpinned drogonframework/drogon:latest image (MDA2AV/HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | One reactor per CPU via SO_REUSEPORT, hand-written incremental parser and registered provided-buffer rings on io_uring (HttpArena meta.json); same thread-per-core io_uring design as libreactorng and libioma. |
| **Adoption** | 4 stars |
| **Last commit** | 2026-05-20 |
| **Links** | [repository](https://github.com/skylightis666/zeemo) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zeemo.json) |

## Verdict

HttpArena, Threadripper PRO 3995WX with the server pinned to 32 cores / 64 threads and gcannon on the other half over loopback, best of three 5 s runs. At 4096 keep-alive connections zeemo (Zig 0.16 ReleaseFast, baseline x86-64 target) served 4,422,489 req/s vs nginx with a custom C module at -O3 -march=native 3,284,513 (1.35x), libreactorng 4,377,377 (1.01x, a tie) and Drogon 2,022,710. At 16-deep pipelining it served 49.9M vs libreactorng 43.4M. With connections closed every 10 requests it was 0.99x nginx.

## Use it when

- As a 1,223-line reference (four files, tests included) for a fork-per-CPU io_uring HTTP/1.1 loop in Zig 0.16: multishot accept, an fd-indexed slot table and pipelined response batching.
- As a starting design for small fixed responses on Linux with many keep-alive connections, where per-response header bytes dominate.
- To study pipelined-response batching: 49.9M req/s at 16-deep pipelining on 64 hardware threads, though zix's 58.8M on the same profile is higher.
- For trying the library API on a Linux kernel 5.19 or later. The repo has no license, so you can read it but not ship it.

## Skip it when

- In any product or shipped code: the repo has no LICENSE, so it is not legally reusable.
- When you need HTTP/2, HTTP/3, non-Linux platforms or async handlers. Handlers are synchronous, so one blocking handler stalls that CPU's whole worker.
- When raw throughput is the only reason: on baseline-4096 it is level with libreactorng (+1%) and slightly behind zix (Zig, 4,442,329 req/s). It trails libioma, libreactorng, zix and nginx on limited-conn-4096, and zix beats it on pipelining.
- When an idle server's CPU cost matters: at the fixed 10k req/s latency profile it spends 30.5 us of CPU per request, against 25.2 for libreactorng, 27.5 for libioma and 27.3 for zix (from HttpArena cpu_per_req_us).
- When a client may send large requests: the measured engine closes the connection when headers exceed 2 KiB or a body exceeds 512 B, and closes any accepted fd numbered 4096 or higher in a worker. The library makes these buffer sizes configurable.

## How it is fast

It forks one shared-nothing worker process per CPU allowed by the cgroup and pins each one with sched_setaffinity. Each worker has its own SO_REUSEPORT listener and a 4096-entry io_uring ring with multishot accept. A recv is posted straight into the connection's 2 KiB parser buffer. drainAndSend parses every complete pipelined request in that buffer and writes the responses back to back into a 4 KiB per-connection buffer, then sends them with one send SQE. Responses carry only a status line plus Content-Type and Content-Length (66 bytes for /pipeline), with no Date or Server header. HttpArena's description also claims 'registered provided-buffer rings', but neither main.zig nor the library's server.zig sets up a buffer ring, registered buffers or multishot recv.

## Compared with alternatives

Rarely. zix (Zig) is faster on baseline-4096, pipelined-4096 and limited-conn-4096 and adds TLS and database routes, while libxev and the C# minima-sync entry land within 1% on baseline. Pick zeemo only to read a minimal, dependency-free single-binary io_uring loop, and only as reference, since it has no license.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Library: libc plus system OpenSSL (libssl and libcrypto, linked unconditionally because src/tls.zig references the symbols). The measured HttpArena engine depends only on Zig std. |
| **Minimum toolchain** | Zig 0.16.0 (build.zig.zon minimum_zig_version) |
| **Platforms** | Linux only (io_uring; docs say kernel 5.19 or later); x86-64 and aarch64 builds in the Dockerfile |
| **Thread safety** | Single-threaded event loop per forked worker process. Nothing is shared at runtime; state is seeded before fork and shared copy-on-write. |
| **Drop-in for the baseline** | no |

## Gotchas

- Measured code differs from the repo: the HttpArena numbers come from the raw-socket engine in MDA2AV/HttpArena frameworks/zeemo, last changed by its author 2026-05-18. The library's own HttpArena entry (zeemo-tuned, PR #739) has no results file (site/data/results/zeemo-tuned.json returns 404), so the library API has no published numbers.
- Description flaw: meta.json and the catalogue's why_faster credit 'registered provided-buffer rings', but neither main.zig nor the library's server.zig sets up a buffer ring, registered buffers or multishot recv. The phrase appears to be copied from libioma's and libreactorng's descriptions. The library README's 'multishot accept and recv' is also only half true: accept is multishot, recv is single-shot.
- Header-volume advantage: responses omit Date and Server. gcannon's bandwidth column uses binary units (3.06 GB/s / 49,860,224 req/s = 65.9 B, exactly the 66-byte /pipeline response), so per-response sizes at baseline-4096 are about 66 B for zeemo, 114 B for libreactorng and 142 B for nginx. These are about 5% above the verifier's decimal-unit figures, with the same ratios (derived from page data).
- The README's '#1 on json-4096' refers to a profile HttpArena removed on 2026-08-29 (#1375). That JSON handler copied item objects pre-rendered at startup (dataset.zig) and computed only the total per request. At baseline-4096 zeemo also used more CPU than libreactorng (6410.6% vs 6168.4%), so per CPU-second libreactorng served about 3% more requests (derived from page data).

## Known shortcomings

- 1% over libreactorng is noise; trails C on limited-conn; README '#1' is stale (zix ahead); built for baseline x86-64 while the C entries use -march=native; unequal response work; no license (reference). Best of 3, cross-run rows.
- The measured code is HttpArena's frameworks/zeemo raw-socket engine (2026-05-18 snapshot), not the library at the repo URL, whose own zeemo-tuned entry has no results file (404). meta.json and the record's why_faster claim 'registered provided-buffer rings', but neither main.zig nor the library's server.zig has buffer rings, registered buffers or multishot recv (single-shot recv; multishot accept only). Bandwidth over rps gives exactly the 66-byte /pipeline response (about 66 bytes per response against libreactorng's 114 and nginx's 142). libreactorng serves about 3% more requests per CPU-second at baseline-4096 (6168.4% vs 6410.6% CPU); latency-10k costs 30.5 us CPU per request against libreactorng's 25.2 (worst of the io_uring engines); zix is ahead on baseline, pipelined and limited-conn. The README's '#1 json-4096' refers to a profile removed on 2026-08-29 (#1375) whose handler used JSON pre-rendered at startup.

## Caveats and trade-offs

No LICENSE file in the repository (raw LICENSE, LICENSE.md and COPYING all 404; the repo page shows no license), so usability is reference. The margin over libreactorng at baseline-4096 is 1% (within run-to-run noise) and over libioma 4%; zeemo trails nginx (0.99x), libioma (0.96x), mongoose and libreactorng on limited-conn-4096, and the pipelined win (1.15x libreactorng) is on a reference-only profile. The README's '#1 on baseline-4096' is stale: zix (Zig) now leads at 4,442,329. The HttpArena entry is a minimal server built for the suite (forked worker processes pinned per CPU, routes /baseline11, /pipeline and /json) that sends no Date or Server header: bytes per response at baseline-4096 (derived from page data, bandwidth divided by req/s) are 62.9 against 108.7 for libreactorng (per-second cached Date header), 85.8 for libioma, 72.5 for mongoose, 98.2 for h2o and 135.4 for nginx, and at pipelined-4096 61.4 against libreactorng's 106.2, so part of each margin is header volume. The zeemo repo's later json-comp and TLS work (May 2026) is not part of the HttpArena entry, which runs only baseline, pipelined, limited-conn and the latency profiles. Each number is the best of 3 runs of 5 s with the server limited to 32 cores / 64 threads; results files are undated and rows come from different runs (zeemo.json last written 2026-08-30, libreactorng.json 2026-09-07, per git history). The C competitor entries are minimal hand-written handlers built by the suite maintainers or contributors; the C rows are compiled -O3 -march=native (nginx, libreactorng, libioma, mongoose; libioma and mongoose also with LTO) or clang CMake Release -march=native (h2o), and the Drogon entry builds only its handler against the unpinned drogonframework/drogon:latest image, so the Drogon ratios (2.19x, 6.4x) are weaker evidence. 4 stars, 20 commits. [retier] The measured code is HttpArena's frameworks/zeemo raw-socket engine (2026-05-18 snapshot), not the library at the repo URL (its zeemo-tuned entry has no results file). The 'registered provided-buffer rings' explanation is wrong: neither main.zig nor the library's server.zig has buffer rings, registered buffers or multishot recv. Responses are exactly 66 bytes against libreactorng's 114 and nginx's 142; libreactorng serves about 3% more requests per CPU-second at baseline-4096 and 30.5 vs 25.2 us CPU per request at latency-10k; zix is ahead on baseline, pipelined and limited-conn. The README's '#1 json-4096' refers to a profile removed on 2026-08-29 whose handler used JSON pre-rendered at startup.

Single-purpose HttpArena benchmark server (HTTP/1.1 only, a handful of endpoints), no TLS or HTTP/2 in this entry, Linux io_uring only; no license file found, so the code cannot be copied.

## Maintenance

A three-day project (20 commits, May 18-20, 2026), 4 stars, no open issues and no license file, so reference-only. The measured engine in the HttpArena repo has had only maintainer profile edits since May 18, 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Every quoted number matches site/data/results/zeemo.json and the sibling nginx, libreactorng, libioma, h2o, mongoose and drogon JSON files in MDA2AV/HttpArena; the code is public (frameworks/zeemo/{Dockerfile,build.zig,build.zig.zon,src/main.zig,src/handlers.zig}, frameworks/libreactorng/Dockerfile, frameworks/nginx/Dockerfile, scripts/lib/common.sh, scripts/lib/profiles.sh), Zig and C flags are in the Dockerfiles, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json, the HttpArena tier-A precedent.
- **Verifier notes:** All quoted numbers verified; tier A kept on the HttpArena precedent. Corrected: runs are best of 3, not one; same_algorithm set false (62.9 bytes per response without Date or Server header against 108.7 for libreactorng); Zig is built for baseline x86-64 against -march=native C, so same_opt_level true. Shortcomings to record: 1% over libreactorng at baseline (noise), behind four C servers on limited-conn, pipelined reference-only, README '#1' claim stale (zix ahead), no license (reference), 4 stars, cross-run rows. Metadata confirmed: no license, 4 stars, 0 forks, last commit 2026-05-20, not a fork, not archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-49 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zeemo.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/frameworks.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/build.zig.zon>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/src/handlers.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libioma/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://github.com/skylightis666/zeemo>
  - <https://github.com/skylightis666/zeemo/commits>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/COPYING>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zeemo>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zeemo/src>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/zeemo.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/libreactorng.json>
- **Sources the enricher read:**
  - <https://github.com/skylightis666/zeemo/commits>
  - <https://github.com/skylightis666/zeemo/issues>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/README.md>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/build.zig>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/src/lib.zig>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/src/server.zig>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/src/response.zig>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/docs/architecture.md>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/docs/deployment.md>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/docs/api-reference.md>
  - <https://raw.githubusercontent.com/skylightis666/zeemo/HEAD/examples/httparena-tuned/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/src/handlers.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/src/http.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zeemo/src/dataset.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zeemo.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zeemo-tuned.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/frameworks.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs/test-profiles>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs/test-profiles/h1>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/baseline/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/baseline/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/baseline/validation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/pipelined/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/short-lived/_index.md>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/zeemo>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/skylightis666/zeemo`) · [data/wave14/enrich/raw/github_com_skylightis666_zeemo.json](../../../data/wave14/enrich/raw/github_com_skylightis666_zeemo.json) (enrichment confidence 0.75)

</details>
