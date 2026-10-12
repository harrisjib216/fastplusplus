# http.c3l

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C3` · `MIT` · 🟢 active

> Sans-IO streaming HTTP/1.1 request parser in C3; ties picohttpparser with callbacks, \~13% faster only when extracting nothing.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | Typical (rounded) result on the bench page: the "no cb" run at \~99 ns/req (\~10.1M req/s, \~113% of pico) vs picohttpparser at \~112 ns/req (\~8.9M req/s), about 13% faster; the full callback-driven http::parser is at parity (\~112 ns/req, \~99% of pico's throughput). In bench/bench.c3 the "no cb" run registers no callbacks at all (empty Settings, null context), so it extracts no method/path/header data while pico fills its method/path and 32-entry header array; the equal-output comparison is therefore parity, not a win. The page also says the SSE2 path is \~1.5x faster than pico's scalar (non-SSE4.2) build, with no numbers table for that claim |
| **Workload** | pico's own benchmark request (request line + headers, no body) parsed in a tight loop on one pinned core, comparing http::parser's callback-driven and callback-free ("no cb") streaming request parser against vendored picohttpparser |
| **Metric** | latency |
| **Hardware** | "x86-64" only; exact CPU model not stated; author pins to one core with taskset |
| **Compiler and flags** | c3c build at O3 (c3c version not stated); vendored picohttpparser compiled as a c-source of the same bench project with cflags -O3 -msse4.2 (C compiler not stated); http::parser uses 16-byte char[&lt;16&gt;] vectors (SSE2 on x86-64, NEON on aarch64 per README/src/simd.c3), no -march=native |
| **Adoption** | 3 stars |
| **Last commit** | 2026-08-02 |
| **Links** | [repository](https://github.com/lsfratel/http.c3l) · [benchmark](https://github.com/lsfratel/http.c3l/blob/main/bench/README.md) |

## Verdict

Author's own microbenchmark (bench/bench.c3): pico's classic browser GET request (9 headers, no body) parsed 5M times after warmup on one pinned x86-64 core with unstated CPU model, c3c -O3 against vendored picohttpparser built -O3 -msse4.2 (compiler versions not stated). Rounded results are pico \~112 ns/req, callback-driven http::parser \~112 ns (\~99% of pico) and a callback-free run \~99 ns (\~113%) that extracts no fields, so at equal output it is parity; the '\~1.5x vs pico scalar build' claim has no numbers.

## Use it when

- Your server is written in C3 and needs an HTTP/1.1 request parser that handles fragmented reads without owning a buffer (raw recv loop, framed peek/consume, or in-memory buffer).
- You want body framing (Content-Length, chunked with trailers), keep-alive and pipelining from one parser object instead of pairing pico's request parse with a separate chunked decoder.
- Constant-memory request handling: the parser is a fixed-size value with no heap allocation (checked by a TrackingAllocator test), and bodies and multipart file uploads stream through callbacks, e.g. straight to disk.
- You want built-in smuggling-related rejects: Content-Length plus Transfer-Encoding, non-final chunked, differing duplicate Content-Length, whitespace before the colon, obs-fold and bare LF, with configurable line-size and header-count limits.

## Skip it when

- C or C++ projects looking for a faster picohttpparser: at equal output the measured result is parity (\~112 vs \~112 ns/req), and the library ships no C header or exported C API.
- When the parser must reject bad bytes: method, target, header names and header values are not checked for token characters or control bytes (NUL, DEL, a stray CR inside a value pass through), unlike picohttpparser.
- Response parsing or anything beyond HTTP/1.x: it parses requests only and accepts only the exact version strings HTTP/1.0 and HTTP/1.1.
- Windows or targets other than Linux/macOS on x64/aarch64: those four are the only targets in manifest.json and CI.
- Where maturity matters: v0.5.0 in source, 3 stars, one squashed commit, no tagged releases and no issue history.

## How it is fast

Delimiter finding uses a portable 16-byte vector byte search (`char[<16>]` equality compare, mask-to-int, count-trailing-zeros; SSE2 on x86-64, NEON on aarch64, no runtime CPU dispatch): first for LF, then for SP and ':' inside the completed line. Per the source, the request-line and header paths only check CRLF, the exact version string, whitespace before the colon and the framing headers; they skip picohttpparser's per-byte token-character and control-byte validation (which pico does with SSE4.2 PCMPESTRI range matching). Callbacks are coalesced to one indirect call per request line and per header, and the author attributes the whole gap between the callback-free run (\~99 ns) and the full run (\~112 ns) to that dispatch.

## Compared with alternatives

Pick it only when the host program is C3 and you want streaming body framing plus multipart in one zero-heap package. For a real speed margin over picohttpparser in C, the vkrasnov AVX2 fork (\~1.7-1.8x) or httpp (\~2.26x claimed) are stronger; in Rust use httparse or thhp; for a streaming C parser to replace llhttp, use iohttpparser.

## Integration

| | |
|---|---|
| **Form** | module (C3 .c3l library bundle, compiled from source) |
| **Dependencies** | none beyond the C3 standard library (picohttpparser is vendored only for the benchmark) |
| **Minimum toolchain** | c3c; CI pins c3c v0.8.1 (project langrev 1); no minimum version documented |
| **Platforms** | linux-x64, linux-aarch64, macos-x64, macos-aarch64 (per manifest.json); SIMD path is 16-byte vectors (SSE2/NEON), no -march=native needed |
| **Thread safety** | not documented; each Parser is a self-contained value with no global state, so use one parser per connection |
| **Drop-in for the baseline** | no |

## Gotchas

- Callback slices point into the caller's buffer and are valid only for the duration of the callback; copy anything you keep.
- An incomplete line returns 0 bytes consumed and is rescanned from its start on the next call, so a slowly dripping line is scanned repeatedly up to max_line_size (8 KiB default); the benchmark uses one whole, hot-cache buffer and does not measure this.
- The \~13% 'no cb' win registers no callbacks at all, so it extracts no method, path or headers, while pico fills its 32-entry header array in the same loop.
- Errors come back as C3 faults from `execute`; call `reset()` before reusing the parser on the connection.

## Known shortcomings

- The \~13% win comes from a run with no callbacks that extracts no fields while picohttpparser fills its header array; with equal output it is at parity (\~99%). Project's own benchmark with rounded figures, no CPU or compiler versions. Written in C3.
- Validates less than picohttpparser (no token-character or control-byte checks, so NUL/DEL/stray CR pass), requests only, HTTP/1.0-1.1 only, and ships no C header or exported C API, so it is not usable from C/C++ as shipped. Linux/macOS only; one squashed commit, 3 stars.

## Caveats and trade-offs

Author's own bench README frames this as "indicative, not a verdict" given the different parser shapes (streaming push parser with per-token callbacks vs one-shot array filling) and also notes http::parser does extra body-framing work; the only faster number (\~13%) comes from a run with no callbacks registered, which delivers no parsed fields while pico fills its header array, so at equal output the usable callback-driven parser is only at parity (\~99% of pico); figures are rounded "typical" values from a single fixed hot-cache request, no raw output, no CPU model or compiler versions; repo history shows a single commit (authored 2026-06-27, committed 2026-08-02)

http::parser is a sans-IO streaming push parser (callback per token, consume/re-present contract) vs picohttpparser's one-shot whole-buffer parse into caller arrays; the streaming design is what costs the \~10-15% callback overhead; written in C3, a young C-like systems language, not C or C++ directly (interoperable via C ABI)

## Maintenance

Active but new (single squashed commit pushed 2026-08-02, CI green on Linux and macOS, v0.5.0, no releases); MIT and only five source files, so easy to vendor into a C3 project but not usable from C/C++ without writing your own bindings.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party microbenchmark only: public code (bench/bench.c3, bench/project.json with vendored picohttpparser at -O3 -msse4.2) but no CPU model (just "x86-64"), no c3c or C compiler version, and only rounded "typical" (\~) figures with no raw output. It is neither peer-reviewed nor an independent suite, so B does not apply; the project's own code with partial methodology is C.
- **Verifier notes:** Downgraded B to C: first-party benchmark code with partial methodology does not qualify for B. Numbers match the page, but the headline win is from a no-callback mode that does less output work than pico; the equal-work comparison is parity, so treat this as a thin/borderline claim. Metadata checks out (MIT, 3 stars, last commit 2026-08-02, not a fork, not archived).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lsfratel/http.c3l>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/README.md>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/bench.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/project.json>
  - <https://github.com/lsfratel/http.c3l/blob/main/README.md>
  - <https://github.com/lsfratel/http.c3l/blob/main/src/simd.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/lsfratel/http.c3l>
  - <https://github.com/lsfratel/http.c3l/blob/main/README.md>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/README.md>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/bench.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/project.json>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/vendor/picohttpparser.c>
  - <https://github.com/lsfratel/http.c3l/blob/main/bench/vendor/picohttpparser.h>
  - <https://github.com/lsfratel/http.c3l/blob/main/src/parser.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/src/simd.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/src/helpers.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/src/version.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/src/multipart.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/manifest.json>
  - <https://github.com/lsfratel/http.c3l/blob/main/project.json>
  - <https://github.com/lsfratel/http.c3l/blob/main/.github/workflows/ci.yml>
  - <https://github.com/lsfratel/http.c3l/blob/main/tests/parser_test.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/tests/zero_alloc_test.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/fuzz/fuzz.c3>
  - <https://github.com/lsfratel/http.c3l/blob/main/examples/limits.c3>
  - <https://github.com/lsfratel/http.c3l/commits/main>
  - <https://github.com/lsfratel/http.c3l/issues>
  - <https://github.com/lsfratel/http.c3l/actions>
  - <https://github.com/lsfratel/http.c3l/tags>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/lsfratel/http.c3l`) · [data/wave5/enrich/raw/github_com_lsfratel_http_c3l.json](../../../data/wave5/enrich/raw/github_com_lsfratel_http_c3l.json) (enrichment confidence 0.6)

</details>
