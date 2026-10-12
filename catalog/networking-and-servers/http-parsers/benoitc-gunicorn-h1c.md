# gunicorn_h1c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> CPython C extension over vendored picohttpparser that parses HTTP/1.1 requests for Gunicorn; claims \~1.1-2.1x httptools throughput.

| | |
|---|---|
| **Beats** | httptools (MagicStack, llhttp-based) / CPython pure-Python HTTP parser |
| **Claimed result** | gunicorn_h1c (fast): \~2,500,000 req/s; gunicorn_h1c (H1CProtocol, reused): \~4,700,000 req/s; httptools: \~2,200,000 req/s; Pure Python: \~150,000 req/s. That is \~1.14x vs httptools for parse_request_fast and \~2.1x for reused H1CProtocol (derived from page data). |
| **Workload** | HTTP/1.1 request-parsing loop from Python, requests/sec on Apple M4 Pro (single thread). gunicorn_h1c is a CPython C extension that wraps the vendored picohttpparser. The README says the H1CProtocol row is a Simple GET with a reused parser (209 ns/op); the request type for the other rows is not stated. The comparison is against httptools (llhttp-based) and a 'Pure Python' parser. |
| **Metric** | throughput |
| **Hardware** | Apple M4 Pro (single thread) |
| **Compiler and flags** | -O3 (setup.py extra_compile_args; plus -msse4.2 on x86 only); compiler and Python version not stated |
| **Adoption** | 10 stars |
| **Last commit** | 2026-08-23 |
| **Links** | [repository](https://github.com/benoitc/gunicorn_h1c) · [benchmark](https://github.com/benoitc/gunicorn_h1c#performance) |

## Verdict

The README reports single-thread Python-loop throughput on an Apple M4 Pro: parse_request_fast \~2.5M req/s and a reused H1CProtocol on a simple GET \~4.7M req/s (209 ns/op), against httptools (llhttp) \~2.2M and a pure-Python parser \~150K, i.e. \~1.14x and \~2.1x httptools. Compiler, Python version and the httptools harness are not stated, the CHANGELOG's own note that reused H1CProtocol is only 7% faster than the pull API suggests the table rows use different requests, and on this ARM machine picohttpparser runs its scalar path.

## Use it when

- You run Gunicorn 25+ (WSGI or ASGI workers) and want the faster parser: pip install gunicorn[fast] and it is picked up by http_parser='auto'.
- A Python asyncio server whose data_received() currently feeds httptools, and you want callback parsing plus Gunicorn's limits and RFC 9110/9112 framing checks (duplicate Content-Length, CL+TE, bare CR in chunk extensions, duplicate Host) in C.
- Header-heavy request handling where most requests only need method, path and a few framing headers, so parse_request_fast's lazy object creation saves allocations.
- Code that needs a WSGI environ or ASGI scope built straight from a byte buffer without a Python-level header loop.

## Skip it when

- You need a verified speedup over httptools/llhttp: the \~2.2M req/s httptools row and the \~150K Pure Python row have no script in the repo, request shapes for most rows are not stated, and the only benchmark (benchmarks/bench_protocol.py) compares this library's own two APIs. Gunicorn's benchmarks/http_parser_benchmark.py also omits httptools.
- Free-threaded CPython (3.13t/3.14t): the modules do not declare Py_mod_gil, so importing them re-enables the GIL; issue #16 reports this erases the gthread gain, and PR #18 adding support is still open.
- Platforms without a C toolchain: PyPI has one wheel (cp314 macOS arm64); everything else, including Linux x86-64, builds from the sdist.
- You need httptools' full surface: there is no callback response parser (parse_response returns a dict, no body decoding), no on_chunk_header/on_chunk_complete/on_status callbacks, and no parse_url.
- Maturity-sensitive deployments: first release March 2026, Development Status 4 - Beta, and 0.6.x releases in 2026 still fixed framing bugs (e.g. 0.6.9: bodies of any request with an Upgrade header were silently dropped on Gunicorn's ASGI worker).

## How it is fast

The scanning is picohttpparser's: a stateless parser that finds token and field-value boundaries with SSE4.2 PCMPESTRI range matching (_mm_cmpestri) when built with -msse4.2, and an 8-byte-unrolled scalar loop otherwise. The wrapper's own speed comes from not building Python objects it does not need: parse_request_fast keeps pointers into the caller's buffer and creates method/path/header bytes only on first access, pulls Content-Length, chunked and Connection out in C during the parse, and H1CProtocol reuses one growable C buffer across keep-alive requests via reset(). There is no NEON code despite the README: on arm64 (including the Apple M4 Pro used for the numbers) the scalar path runs.

## Compared with alternatives

Pick it over zttp (the other Python-level httptools challenger in the catalog, which publishes a 14-workload comparison) when you are on Gunicorn or need Gunicorn-compatible limits, exceptions and WSGI/ASGI builders; pick zttp when you want a documented, reproducible margin over httptools. The C-level picohttpparser variants (vkrasnov AVX2 fork, httparse, hparse) are faster parsing cores but are not Python bindings.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (vendored picohttpparser); C compiler and setuptools&gt;=61 to build from sdist |
| **Minimum toolchain** | Python 3.9+ (CI tests 3.13 and 3.14 only); any C compiler setuptools can drive, built with -O3 (plus -msse4.2 on x86) |
| **Platforms** | Linux and macOS in CI; SIMD only on x86 built with SSE4.2, scalar picohttpparser path elsewhere (including arm64); Windows not tested |
| **Thread safety** | Not documented; parser objects hold mutable state with no locking and rely on the GIL (free-threading support pending in PR #18). |
| **Drop-in for the baseline** | partial — H1CProtocol reuses httptools' callback names, but callbacks are constructor kwargs rather than a protocol object, the method is feed() not feed_data(), method/path/headers are properties, on_headers_complete may return True to skip the body, upgrades are reported via should_upgrade/remaining() instead of an HttpParserUpgrade exception, and errors are gunicorn_h1c exceptions; requests only |

## Gotchas

- x86 builds use -msse4.2 unconditionally, so a binary built on x86 needs an SSE4.2 CPU; on ARM the README's NEON claim is false and parsing is scalar.
- parse_request_raw returns offsets only and skips every limit, RFC and framing check the other entry points run; do not feed it untrusted input without your own validation.
- HttpRequest from parse_request_fast holds a buffer export on your input and embeds a 256-entry phr_header array (about 8 KB per object on 64-bit); keeping it alive pins a bytearray against resizing.
- While in the header state, H1CProtocol buffers everything fed until the header block is complete; the request-line limit is only checked once a CRLF appears and field limits only after a full parse, so the caller must bound bytes per request. After completion, bytes are kept for remaining() up to limit_remaining (64 KB) and dropped by reset() unless you read them first (pipelining).

## Known shortcomings

- No harness for the httptools (\~2.2M) or pure-Python rows; table rows disagree with the CHANGELOG, so like-for-like is unclear; compiler and Python version not stated. The README's NEON claim is false: arm64 (including the M4 Pro used) runs picohttpparser's scalar path; SIMD is SSE4.2 on x86 only. Importing it on free-threaded 3.13t/3.14t re-enables the GIL (#16, PR #18 open). One wheel on PyPI (cp314 macOS arm64); others need a C compiler (#1). parse_request_raw skips all validation; H1CProtocol can buffer without bound before the header block completes. 'Zero-copy' is overstated (headers and body chunks are copied). HttpRequest embeds \~8 KB and pins bytearray buffers. 0.6.x fixed several 2026 framing bugs (Upgrade bodies dropped in the ASGI worker); still Beta. Only a partial httptools replacement (different callbacks, no parse_url, no response parser). Adoption: Gunicorn 25+ uses it automatically via gunicorn[fast].

## Caveats and trade-offs

The README table has no benchmark script for the httptools or Pure Python rows. The only script (benchmarks/bench_protocol.py) compares the callback API with the pull API. The \~4.7M row reuses the parser, and httptools' setup is not described, so like-for-like is unclear. The README claims NEON SIMD on ARM, but the vendored picohttpparser and the module sources contain only an SSE4.2 path. On the Apple M4 Pro used for the numbers, parsing is therefore scalar. httptools wraps llhttp, so this is only an indirect llhttp comparison. Very low adoption: 10 stars.

Python C-extension wrapping picohttpparser with hand-added SIMD (SSE4.2/NEON); zero-copy with lazy Python object creation; only wraps request/response line + header parsing, not a full server; GitHub license detector shows NOASSERTION despite an included MIT LICENSE file

## Maintenance

Active (v0.6.9, last commit 2026-08-23), MIT-licensed including the vendored picohttpparser, and shipped as Gunicorn's optional fast parser (\~36.6K PyPI downloads/month) despite only 10 GitHub stars.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table: Apple M4 Pro, single thread, gunicorn_h1c \~2.5M / \~4.7M req/s vs httptools \~2.2M and Pure Python \~150K. The repo's only benchmark script (benchmarks/bench_protocol.py) compares gunicorn_h1c's callback API with its pull API. No code reproduces the httptools or Pure Python rows, and no compiler is stated.
- **Verifier notes:** Numbers match the README. GitHub reports NOASSERTION only because LICENSE appends picohttpparser's MIT notice. The project's own code is MIT, so license=MIT and usability copyable stay. Last commit 2026-08-23, active.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/benoitc/gunicorn_h1c>
  - <https://github.com/benoitc/gunicorn_h1c#performance>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/LICENSE>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/benchmarks/bench_protocol.py>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/setup.py>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/picohttpparser/picohttpparser.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_parser_fast.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_parser_module.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_protocol.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_utils.h>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/CHANGELOG.md>
- **Sources the enricher read:**
  - <https://github.com/benoitc/gunicorn_h1c>
  - <https://github.com/benoitc/gunicorn_h1c#performance>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/README.md>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/setup.py>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/pyproject.toml>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/MANIFEST.in>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/LICENSE>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/CHANGELOG.md>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/.github/workflows/ci.yml>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/benchmarks/bench_protocol.py>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/__init__.py>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_parser_fast.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_parser_module.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_protocol.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/pico_utils.h>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/picohttpparser/picohttpparser.c>
  - <https://github.com/benoitc/gunicorn_h1c/blob/main/src/gunicorn_h1c/picohttpparser/picohttpparser.h>
  - <https://github.com/benoitc/gunicorn_h1c/issues>
  - <https://github.com/benoitc/gunicorn_h1c/pulls>
  - <https://github.com/benoitc/gunicorn_h1c/issues/1>
  - <https://github.com/benoitc/gunicorn_h1c/issues/10>
  - <https://github.com/benoitc/gunicorn_h1c/issues/16>
  - <https://github.com/benoitc/gunicorn_h1c/pull/18>
  - <https://github.com/benoitc/gunicorn/blob/HEAD/benchmarks/http_parser_benchmark.py>
  - <https://github.com/benoitc/gunicorn/blob/HEAD/docs/content/reference/settings.md>
  - <https://github.com/benoitc/gunicorn/blob/HEAD/docs/content/2026-news.md>
  - <https://github.com/MagicStack/httptools/blob/master/README.md>
  - <https://pypi.org/pypi/gunicorn_h1c/json>
  - <https://pypistats.org/api/packages/gunicorn-h1c/recent>
  - https://hn.algolia.com/api/v1/search?query=gunicorn_h1c&tags=(story,comment)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/benoitc/gunicorn_h1c`) · [data/wave5/enrich/raw/github_com_benoitc_gunicorn_h1c.json](../../../data/wave5/enrich/raw/github_com_benoitc_gunicorn_h1c.json) (enrichment confidence 0.75)

</details>
