# rproxy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🟢 active

> Rust io_uring HTTP/1.1 filtering reverse proxy; first-party 1.24x nginx-as-proxy throughput on a 2-byte keep-alive response.

| | |
|---|---|
| **Beats** | nginx as a reverse proxy (version and config not stated); HAProxy 2.8.5 (vendored build) as a second row |
| **Claimed result** | June run (bench/BENCHMARK_RESULTS.md, 2026-06-27, median of 3 after warmup, proxies pinned to cores 2-3 with 2 workers each): rproxy 189,810.00 req/s (557 us) vs nginx reverse proxy 153,484.52 (662 us) = 1.24x; rproxy before its hot-path optimisation 135,700.79 (0.88x); backend ceiling 362,163.20. August run (README, measured 2026-08-16 with bench/haproxy_baseline.sh, labelled median of 3 but the script keeps the best of 3): rproxy 323,035 (352 us) vs nginx reverse proxy 282,032 (400 us) = 1.15x and HAProxy 2.8.5 266,603 (395 us) = 1.21x; ceiling 632,175. rproxy with TLS 134,168 req/s (no TLS comparison against nginx). |
| **Workload** | HTTP/1.1 reverse proxy in front of an nginx backend answering '200 OK' with a 2-byte body, wrk -t4 -c100 -d10s keep-alive, two proxy workers each for rproxy and nginx on two pinned cores, loopback. |
| **Metric** | throughput |
| **Hardware** | 12th Gen Intel Core i5-12450H, 12 logical cores; June run: wrk on cores 4-7, backend nginx on cores 0-1, proxy on cores 2-3. The August script does no pinning: backend nginx and the nginx proxy each run worker_processes 4, HAProxy and rproxy use their defaults, all on the same box. |
| **Compiler and flags** | Cargo release profile: lto = 'fat', codegen-units = 1, panic = 'abort', opt-level = 3, debug = true; monoio 0.2.4 with io_uring. nginx version and build flags not stated (installed from the system, per the script's 'command -v nginx'); HAProxy 2.8.5 vendored build, flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Prefork thread-per-core monoio workers on io_uring with a zero-allocation hot path (README architecture section). |
| **Adoption** | 0 stars, 2 commits |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/PipelineDude/rproxy) · [benchmark](https://github.com/PipelineDude/rproxy) |

## Verdict

On the author's i5-12450H laptop-class box (wrk -t4 -c100 -d10s keep-alive over loopback, nginx backend returning a 2-byte 'OK'), the June run with 2 pinned workers each gave rproxy 189,810 req/s against an nginx reverse proxy at 153,484 (1.24x), median of 3; a later unpinned run reported 323,035 vs nginx 282,032 (1.15x) and HAProxy 2.8.5 266,603 (1.21x), but those are best-of-3 with unequal worker counts. nginx's version and build flags are not stated; rproxy is built with fat LTO, codegen-units 1 and opt-level 3.

## Use it when

- You already run nginx (or a load balancer) for TLS and static files and want JWT, IP ACL, rate-limit and request-validation policy in one YAML file instead of nginx if/location blocks or Lua.
- Linux hosts with io_uring (kernel 5.6+, 5.11+ recommended) serving HTTP/1.1 keep-alive API traffic with small responses, the shape where its measured lead over nginx appeared.
- You need ACL-safe path canonicalisation (/x/../admin, //admin, /%61dmin) applied identically to routing, filters, cache key and the forwarded request.
- Small internal deployments where per-worker rate limits and caches (limit roughly multiplied by worker count) are acceptable.

## Skip it when

- As a front-line edge proxy replacing nginx or HAProxy: the author positions it only as a filter behind one, and it has no HTTP/2 or HTTP/3, no config reload on SIGHUP and no graceful drain on SIGTERM.
- When you need global rate limits or a shared cache: rate_limit, the LRU cache, the backend pool and leastconn counts are all per worker.
- TLS-heavy paths: the only TLS number is rproxy alone at 134,168 req/s against a plaintext backend ceiling, with no nginx or HAProxy TLS row to compare.
- Anything that needs a licence: the repository has no LICENSE file, so it can only be studied, not legally reused.
- Production-critical use: 0 stars, 2 public commits (2026-08-18 and 2026-08-25), one author, no releases.

## How it is fast

Each worker is a forked single-threaded monoio (io_uring) process accepting through SO_REUSEPORT, so there are no locks or cross-thread hand-offs; per-request state lives in thread_local! structures and pooled buffers, and the README says the hot path allocates nothing at log level info. The response head is rebuilt in one pass from httparse output and, for small bodies, written together with the body in a single write; the June results file attributes the jump from 0.88x to 1.24x of nginx to that head+body coalescing, removing a double parse and a load-balancer fix. Backend connections are kept alive in a per-worker pool, and backend liveness and counters live in a MAP_SHARED region read without locks.

## Compared with alternatives

Pick rproxy over routez, Arc or monolake when the job is a policy filter (JWT, ACL, rate limit, validation, canonical paths) behind an existing nginx rather than a general reverse proxy; routez publishes a broader nginx and HAProxy comparison (1.26x as a keep-alive reverse proxy), and monolake uses the same monoio io_uring runtime with a larger team and history.

## Integration

| | |
|---|---|
| **Form** | standalone binary (cargo build --release; Dockerfile builds a glibc binary on a scratch image) |
| **Dependencies** | monoio 0.2.4 (io-uring), io-uring 0.6, httparse, rustls 0.23 with monoio-rustls and rustls-native-certs, tokio, hyper and reqwest (health/metrics process only), serde_yaml, regex, lru, hmac/sha2, nix, socket2 |
| **Minimum toolchain** | Rust edition 2021 (exact MSRV not documented); Linux kernel 5.6+ with io_uring, 5.11+ recommended |
| **Platforms** | Linux only (io_uring, MAP_SHARED, fork); x86-64 per the Dockerfile; glibc required (musl lacks syscalls monoio needs, per the Dockerfile comment) |
| **Thread safety** | Not applicable as a library; each worker is a separate single-threaded process, shared state is MAP_SHARED counters only |
| **Drop-in for the baseline** | partial — it proxies HTTP/1.1 like an nginx proxy_pass location, but uses its own YAML config, lacks HTTP/2, static files and reload, and is meant to run behind nginx rather than replace it |

## Gotchas

- Harness flaw in the August three-proxy run: bench/haproxy_baseline.sh prints 'median-of-3' but keeps the best of three wrk runs, pins no cores, and gives the backend nginx and the nginx proxy worker_processes 4 each while HAProxy runs its default thread count (bench/haproxy.cfg sets no nbthread) and rproxy reads its worker count from bench_config.yml, which is not in the repo; when that count is below the 12 allowed CPUs rproxy's cpu_affinity 'auto' policy (src/platform.rs) pins each worker to its own core while nginx stays unpinned, so the August 1.15x and 1.21x ratios are not equal-resource comparisons. The script also expects haproxy.cfg and a built haproxy-2.8.5/ at the repo root, neither of which is published (the config is at bench/haproxy.cfg), so it cannot run as published.
- Only the June 2026-06-27 run (bench/BENCHMARK_RESULTS.md: median of 3 after a warmup, 2 workers each on pinned cores 2-3) is close to like-for-like; its nginx proxy config was not published, and the repo's bench/nginx_proxy.conf listens on 8081 and proxies to 8081 (a self-loop) while bench/backend_nginx.conf listens on 8080, the rproxy port, so none of the checked-in configs is what was measured. A pre-existing system nginx was running on the box during the June run (the first nginx-proxy attempt collided with it on :8082).
- Both measured runs predate the first public commit (2026-08-18), the README contradicts itself (a measured HAProxy row, then 'HAProxy was not measured on the current rig'), and bench/rproxy.yaml sets log_level: debug, which the README says enables per-request logging and allocation; it listens on 8083 and was evidently not the measured config.
- Unknown YAML keys are silently ignored, so a typo disables a filter without an error; rate_limit is per worker, so the effective global limit is about rate_limit x workers.

## Known shortcomings

- haproxy_baseline.sh keeps the best of 3 while claiming a median, pins nothing and needs a bench_config.yml missing from the repo; the June nginx config is unpublished (the repo copy proxies to itself); both runs predate the first public commit; HAProxy statements contradict each other; 2-byte body; no license, 0 stars.
- bench/haproxy_baseline.sh labels best-of-3 as 'median-of-3' and pins no cores; the backend nginx and the nginx proxy each get worker_processes 4; HAProxy runs default threads (no nbthread); rproxy reads its worker count from a missing bench_config.yml, and if that count is under 12 CPUs its cpu_affinity auto pins its workers while nginx stays unpinned, so the August 1.15x/1.21x is not equal-resource. The script also needs a root haproxy.cfg and haproxy-2.8.5/, neither published; the June run had a system nginx already running on the box; bench/rproxy.yaml uses log_level debug and is not the measured config. No LICENSE.

## Caveats and trade-offs

First-party; both runs (2026-06-27 and 2026-08-16) predate the repo's first public commit (2026-08-18), so the measured revisions are not in public history. The August three-proxy run's script (bench/haproxy_baseline.sh) labels its result 'median-of-3' but keeps the best of 3 runs, pins no cores, gives the nginx proxy worker_processes 4 and reads rproxy's worker count from bench_config.yml, which is not in the repo, so the equal-core claim holds only for the June run; that also explains the ceiling jump from 362k (2 pinned backend cores) to 632k (4 unpinned workers). The June nginx proxy config is not published and its upstream keep-alive is not stated (bench/nginx_proxy.conf in the repo listens on 8081 and proxies to 8081, so it is not the config used). The README is internally inconsistent about HAProxy: it shows a measured HAProxy row and then says 'HAProxy was not measured on the current rig' and no HAProxy comparison is claimed. Tiny 2-byte keep-alive body, same box, no TLS comparison; larger bodies, no keep-alive or TLS may differ. No LICENSE file, so reference. 0 stars, 2 commits. The README positions rproxy as a filter behind nginx, not a replacement. The win is architectural (prefork thread-per-core monoio workers on io_uring, coalesced head+body writes), not a Rust language effect. [retier] bench/haproxy_baseline.sh labels best-of-3 as 'median-of-3' and pins no cores; the backend nginx and nginx proxy each get worker_processes 4; HAProxy runs default threads; rproxy reads its worker count from a missing bench_config.yml, and under 12 CPUs its cpu_affinity auto pins its workers while nginx stays unpinned, so the August 1.15x/1.21x is not equal-resource. The script needs an unpublished root haproxy.cfg and haproxy-2.8.5/; the June run had a system nginx already running; bench/rproxy.yaml (log_level debug) is not the measured config.

Not a general reverse proxy: the author positions it as a filtering layer (JWT, rate limiting, ACL and canonicalization checks) behind nginx; Linux with io_uring (kernel 5.6+); rate limit and cache state are per worker; TLS rate 134,168 req/s vs ceiling 629,459.

## Maintenance

Active (last commit 2026-08-25) but a 0-star, 2-commit solo project with no LICENSE file, so reference only; the most comparable benchmark (June) used configs and code not in the public history, and the published three-proxy script reports best-of-3 as a median on unpinned, unequal worker counts.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers in the README and bench/BENCHMARK_RESULTS.md match the record (June 189,810 vs nginx 153,484; August 323,035 vs 282,032 and HAProxy 266,603); the August script bench/haproxy_baseline.sh is public but needs a missing bench_config.yml and a vendored HAProxy not in the repo, and nginx's version and build flags are not stated, so C.
- **Verifier notes:** Numbers match README and bench/BENCHMARK_RESULTS.md; tier C stands. Shortcomings: haproxy_baseline.sh reports best-of-3 labelled median and pins nothing, needs a bench_config.yml absent from the repo; June nginx config unpublished (repo copy is a self-loop); measured code predates public history; contradictory HAProxy statements; 2-byte keep-alive body only; no licence; 0 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-52 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/PipelineDude/rproxy>
  - <https://github.com/PipelineDude/rproxy/commits/main>
  - <https://github.com/PipelineDude/rproxy/tree/main/bench>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/README.md>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/haproxy_baseline.sh>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/nginx_proxy.conf>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/backend_nginx.conf>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/haproxy.cfg>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/rproxy.yaml>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/perf_gate.sh>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/perf_report.txt>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/PipelineDude/rproxy>
  - <https://github.com/PipelineDude/rproxy/commits/main>
  - <https://github.com/PipelineDude/rproxy/tree/main/src>
  - <https://github.com/PipelineDude/rproxy/tree/main/docs>
  - <https://github.com/PipelineDude/rproxy/issues>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/README.md>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/docs/DESIGN-NOTES.md>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/haproxy_baseline.sh>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/tls_bench.sh>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/nginx_proxy.conf>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/backend_nginx.conf>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/haproxy.cfg>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/rproxy.yaml>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/perf_gate.sh>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/bench/perf_report.txt>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/src/fast_proxy.rs>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/src/platform.rs>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/PipelineDude/rproxy/HEAD/src/main.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/pipelinedude/rproxy`) · [data/wave14/enrich/raw/github_com_pipelinedude_rproxy.json](../../../data/wave14/enrich/raw/github_com_pipelinedude_rproxy.json) (enrichment confidence 0.6)

</details>
