# zttp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `BSD-3-Clause` · 🟢 active

> Sans-IO HTTP/1.1 (plus HTTP/2, HTTP/3) parser for Python with a Zig core; out-parses httptools/llhttp on 13 of 14 microbenchmarks.

| | |
|---|---|
| **Beats** | llhttp (via MagicStack/httptools 0.8.0, the Python binding over llhttp) |
| **Claimed result** | beats httptools on 13 of 14 workloads, 1.04x-2.06x faster (e.g. 1.16x on wrk default GET, 2.42M vs 2.09M msg/s; 2.06x on 16KB upload in MTU pieces, 441k vs 214k msg/s; 1.18x on 'Chunked POST (llhttp bench)', 875k vs 741k msg/s; 1.14x on 'Real-world GET (pico/llhttp)', 947k vs 831k msg/s); 0.94x (slower) on the synthetic TFB plaintext 16x-pipelined workload, 151k vs 161k msg/s |
| **Workload** | 14-workload HTTP/1.1 parser microbenchmark suite (wrk/TFB/httparse/pico/llhttp/Chrome-nav/k8s-ingress/upload shapes) measuring messages/sec parsed via zttp's Zig core (Python binding) vs MagicStack/httptools, whose HttpRequestParser/HttpResponseParser are fulfilled through llhttp |
| **Metric** | throughput |
| **Hardware** | "an Apple Silicon machine" (exact CPU model not stated) |
| **Compiler and flags** | Zig ReleaseSafe build (safety checks on); the page gives no Zig version (the repo's pyproject.toml pins ziglang==0.16.0 as a build requirement); CPython 3.14; httptools 0.8.0 |
| **Adoption** | 57 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/Kludex/zttp) · [benchmark](https://zttp.marcelotryle.com/reference/performance/) |

## Verdict

The author's docs site ran a Python harness over 14 HTTP/1.1 request and response shapes (from wrk, TFB, httparse, pico/llhttp, browser, ingress and upload fixtures). It compared zttp's ReleaseSafe Zig core with httptools 0.8.0 (llhttp) on CPython 3.14 and an unspecified Apple Silicon machine; the page gives no Zig version, and the build pins 0.16.0. zttp parsed 1.04x-2.06x more messages/s on 13 workloads and ran 0.94x on 16x-pipelined TFB plaintext, with about 5% run-to-run spread. The repo's newer table (CPython 3.14.3, zttp 0.0.27.dev38, median of 15 interleaved batches), not yet deployed to the site, reports 1.01x-2.55x on all 14.

## Use it when

- A Python ASGI/HTTP server or proxy that drives httptools or h11 today and wants a pull-based sans-IO parser at native speed. The author's Uvicorn-shaped benchmark, which builds equivalent ASGI scopes, reports 1.16x-1.52x over httptools.
- Request handling that reads only a few headers through get()/getall(): the lazy HeaderBlock never materializes the rest as Python objects.
- Bodies arriving in many TCP-segment-sized pieces. The 16 KB upload fed in 1448-byte pieces is its largest published win (2.06x on the docs site, 2.55x in the repo's newer table).
- One Python event API for both HTTP/1.1 and HTTP/2 (its own benchmark puts it 6.6x-50x ahead of the pure-Python h2), on Linux (glibc/musl, x86_64/aarch64), macOS or Windows (amd64/arm64) wheels.
- Free-threaded CPython 3.14t/3.15t: wheels are built for those ABIs and the module declares it does not need the GIL.

## Skip it when

- Production services today: the README says it is experimental and not ready for production, the API may change at any time, the PyPI classifier is Alpha, and versions are still 0.0.x.
- Heavily pipelined HTTP/1.1 (TechEmpower-style 16x pipelining): the published docs page has it 6% slower than httptools there. The repo's newer, not yet deployed table claims 1.25x faster.
- Deployments that need to tune DoS limits: HTTP/1.1 and HTTP/2 limits (16 KiB line, 100 headers, 64 KiB header block, 8 MiB buffer) are hard-coded and cannot be set from Python (issue #49 is open).
- HTTP/3 clients on untrusted networks: the QUIC/TLS client does no certificate chain or hostname verification (issue #144 is open), and THREAT_MODEL.md calls HTTP/3 the least battle-tested path.
- Peers that need lenient parsing (bare LF, obs-fold, odd Content-Length forms), PyPy, or any consumer outside CPython: strictness toggles are not exposed to Python, and the only documented distribution is the CPython wheel/sdist.

## How it is fast

The HTTP/1.1 hot loops scan with Zig @Vector blocks. LF search uses std.mem.findScalarPos, which checks two SIMD vectors per iteration. Request-target and field-value checks skip whole clean blocks with lane compares, then fall back to comptime-built 256-entry character-class tables. Parse results are slices into one reused receive buffer that is compacted only past 64 KiB, and an incremental head scanner resumes at the first new byte when a head arrives in fragments. At the Python edge, headers stay in one packed HeaderBlock until you access them (no bytes object or tuple per header), each body span becomes a single Data event, and large Content-Length bodies can keep the Python-owned input span instead of being copied.

## Compared with alternatives

The catalogued siblings (iohttpparser against llhttp; picohttpparser forks, httparse, hparse and http.c3l against picohttpparser) are native C/Rust/Zig/C3 parsers meant to be embedded in native code. Pick zttp only when the consumer is CPython and you want a pull-based sans-IO parser that also serializes messages and covers HTTP/2. For native servers, iohttpparser (llhttp baseline) or hparse (Zig) fit better.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | typing-extensions&gt;=4.6 at runtime (despite the README's 'No dependencies'); a source build pulls ziglang==0.16.0 and hatch-ziglang as isolated build requirements, so no system Zig is needed |
| **Minimum toolchain** | CPython 3.10-3.15, including free-threaded 3.14t/3.15t; source builds use the pinned Zig 0.16.0 |
| **Platforms** | Wheels for manylinux_2_28 and musllinux_1_2 on x86_64 and aarch64, macOS 11+ on arm64 and x86_64, and Windows amd64 and arm64 (32-bit i686 skipped); the SIMD width comes from std.simd.suggestVectorLength for each target |
| **Thread safety** | Every Connection method runs inside a CPython critical section on that connection object; HTTP/3 session-ticket paths also lock a module-level object. Concurrent calls on a shared connection are therefore serialized, and a test exercises this. The module declares Py_MOD_GIL_NOT_USED. |
| **Drop-in for the baseline** | partial — it fills the same role as httptools in a Python server, but the interface is different: you pull events instead of passing a protocol object with on_\* callbacks. Headers come back as a lazy HeaderBlock, and you must call start_next_cycle() between keep-alive messages, so the integration layer has to be rewritten. |

## Gotchas

- The HTTP/1.1 microbenchmark times each parser's default API, and that favors zttp. zttp's timed loop never materializes headers and never reads Data payloads. The httptools harness appends a (name, value) tuple for every header and joins url and body with Python `+=`. That tilts the header-heavy and fragmented-body rows, so the Uvicorn-shaped scope benchmark (1.16x-1.52x) is the fairer comparison.
- Strict by default, and Python cannot relax it: bare LF, obs-fold, lenient Content-Length, non-1\*HEXDIG chunk sizes, missing or duplicate Host, and CL/TE conflicts all raise RemoteProtocolError, and that poisons the connection for good. Legacy clients that other parsers tolerate will be rejected.
- zttp has no tunnel awareness. After Upgrade/CONNECT/101 you must stop feeding bytes as HTTP/1.1 and must not call start_next_cycle(); THREAT_MODEL.md calls this the highest-risk integration point. HTTP/1.0 keep-alive and chunked policy, timeouts, and connection caps are also left to the host. Parsing a response on a connection that never sent the request desyncs HEAD/1xx/204/304 framing.
- Open bug #282 (2026-09-19): if an allocation fails while flushing HTTP/2 DATA, a later flush resends bytes that were already emitted and debits the flow-control window twice.

## Known shortcomings

- Author's own benchmark on unspecified Apple Silicon against llhttp via httptools 0.8.0 (Python); pipelined requests are slower (0.94x). A Zig core with Python bindings, not a C/C++ library. The live docs page lags the repo's newer numbers.
- The harness favours zttp: in the timed loop zttp never builds header objects or reads bodies, while the httptools side builds tuples and concatenates; the fairer Uvicorn-shaped benchmark shows 1.16-1.52x. The HTTP/3 client does no certificate or hostname verification (#144). Self-described experimental, 0.0.x alpha.

## Caveats and trade-offs

Only a first-party benchmark. Hardware is described only as "an Apple Silicon machine", with no exact CPU model, and the page gives no Zig compiler version. The author puts run-to-run spread at about 5%, which is about the size of several of the smaller wins (1.04x-1.08x). The benchmark measures parser throughput in isolation through Python bindings on both sides, not a full server. The live docs page is stale: the repo's docs/reference/performance.md at HEAD (refreshed in commit 50248abe, 2026-08-27; CPython 3.14.3, zttp 0.0.27.dev38, median of 15 batches) reports zttp faster on all 14 workloads, 1.01x-2.55x (pipelined 1.25x, MTU-pieces upload 2.55x), but the deployed site has not been rebuilt with those numbers.

httptools is a thin C-parser binding while zttp's Zig core is sans-IO and event-based (Request/Data/EndOfMessage), which changes the integration API; zttp also ships HTTP/2 and experimental HTTP/3 support in the same package; explicitly marked experimental/not production-ready by the author

## Maintenance

Actively developed (v0.0.34 on 2026-09-19, near-daily commits, 57 stars), BSD-3-Clause, pip-installable with prebuilt wheels, but self-described as experimental/Alpha with an unstable API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party benchmark (the author's own docs site, code in benchmarks/http1.py) against httptools 0.8.0, which wraps llhttp. The page gives no CPU model (only "an Apple Silicon machine") and no Zig compiler version, so it is not A. It is not an independent suite or a paper, so it is not B either: first-party code with partial methodology is C.
- **Verifier notes:** The live page's numbers match the record except for one mislabel: 1.14x is the Real-world GET (pico/llhttp) row, while the llhttp chunked-POST row is 1.18x (fixed in claimed_speedup). The tier was B, but this is first-party code with partial methodology, so it is C. The newer, stronger numbers in the repo docs are recorded in caveats, and enrichment may prefer them once they are deployed.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://zttp.marcelotryle.com/reference/performance/>
  - <https://github.com/Kludex/zttp>
  - <https://github.com/Kludex/zttp/blob/main/docs/reference/performance.md>
  - <https://github.com/Kludex/zttp/blob/main/benchmarks/http1.py>
  - <https://github.com/Kludex/zttp/blob/main/pyproject.toml>
- **Sources the enricher read:**
  - <https://github.com/Kludex/zttp>
  - <https://github.com/Kludex/zttp/blob/main/README.md>
  - <https://zttp.marcelotryle.com/reference/performance/>
  - <https://github.com/Kludex/zttp/blob/main/docs/reference/performance.md>
  - <https://github.com/Kludex/zttp/blob/main/benchmarks/http1.py>
  - <https://github.com/Kludex/zttp/blob/main/pyproject.toml>
  - <https://github.com/Kludex/zttp/blob/main/src/core/scanner.zig>
  - <https://github.com/Kludex/zttp/blob/main/src/core/tables.zig>
  - <https://github.com/Kludex/zttp/blob/main/src/core/h1/reader.zig>
  - <https://github.com/Kludex/zttp/blob/main/src/core/h1/headers.zig>
  - <https://github.com/Kludex/zttp/blob/main/src/python/connection_obj.zig>
  - <https://github.com/Kludex/zttp/blob/main/src/python/module.zig>
  - <https://github.com/Kludex/zttp/blob/main/zttp/config.py>
  - <https://github.com/Kludex/zttp/blob/main/THREAT_MODEL.md>
  - <https://github.com/Kludex/zttp/blob/main/docs/architecture.md>
  - <https://github.com/Kludex/zttp/blob/main/docs/usage/install.md>
  - <https://github.com/Kludex/zttp/blob/main/docs/usage/http1.md>
  - <https://github.com/Kludex/zttp/blob/main/docs/reference/api.md>
  - <https://github.com/Kludex/zttp/blob/main/tests/test_free_threading.py>
  - <https://github.com/Kludex/zttp/issues>
  - <https://github.com/Kludex/zttp/issues/49>
  - <https://github.com/Kludex/zttp/issues/144>
  - <https://github.com/Kludex/zttp/issues/195>
  - <https://github.com/Kludex/zttp/issues/282>
  - <https://github.com/Kludex/zttp/commits/main>
  - <https://github.com/Kludex/zttp/releases>
  - <https://pypi.org/pypi/zttp/json>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/kludex/zttp`) · [data/wave5/enrich/raw/github_com_kludex_zttp.json](../../../data/wave5/enrich/raw/github_com_kludex_zttp.json) (enrichment confidence 0.72)

</details>
