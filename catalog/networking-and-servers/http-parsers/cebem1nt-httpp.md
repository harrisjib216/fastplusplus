# httpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Single-header, zero-allocation C HTTP/1.1 request parser; \~2.26x picohttpparser's scalar build on one sample request, with far less validation.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | At -O3: httppv2 (2.0.0) 8,893,776.12 req/s (1.124382s) vs picohttpparser 3,939,350.39 req/s (2.538490s), \~2.26x (derived from page data); httppv1 (1.0.0) 2,855,841.74 req/s (3.501595s), slower than pico at -O3. At -O0: httppv1 2,008,030.68 and httppv2 3,475,424.44 req/s vs picohttpparser 1,130,465.28 req/s. |
| **Workload** | Single-threaded repeated parse of picohttpparser's own classic sample GET request (image request with UA/cookie headers), 10,000,000 iterations x 5 runs, averaged. |
| **Metric** | throughput |
| **Hardware** | Ryzen 7, \~4.79GHz peak frequency (exact SKU not given) |
| **Compiler and flags** | gcc 15.2.1 20251112; -O0 and -O3 only, no -march/-msse4.2 (benchmarks/run.sh), so picohttpparser's SSE4.2 fast path is not compiled in; picohttpparser is cloned unpinned from h2o master at run time |
| **Adoption** | 9 stars |
| **Last commit** | 2025-12-21 |
| **Links** | [repository](https://github.com/cebem1nt/httpp) · [benchmark](https://github.com/cebem1nt/httpp#benchmark) |

## Verdict

This is the project's own benchmark: 10M parses x 5 runs of picohttpparser's classic 9-header 'hello-kitty' GET, timed with clock() and built with gcc 15.2.1 -O3 and no -march on an unspecified 'Ryzen 7' (4.79 GHz peak). httpp 2.0.0 took 1.12 s (\~8.9M req/s) against picohttpparser's 2.54 s (\~3.9M req/s), about 2.26x, while httpp 1.0.0 was slower than pico. Pico was built without -msse4.2, so its SSE4.2 path was off; it was cloned unpinned and built as a separate TU, and an earlier README run on the same stated hardware had pico at 4.91M req/s, a 1.83x ratio.

## Use it when

- Small or hobby C servers where you control the client or sit behind a validating proxy, and want one dependency-free header with no heap use on the parse path.
- The whole request is already in one NUL-terminated buffer, has at most \~20 headers, and you only need route, header and body spans.
- Throughput-bound parsing of known-good HTTP/1.1 requests on x86-64/glibc, such as test harnesses, load generators or internal tooling.
- You also want a trivial response serializer (status-text table plus header list to a malloc'd raw response) in the same file.
- As a short, readable base to fork; the README explicitly invites changes such as replacing the fixed header array with a hash table.

## Skip it when

- Internet-facing servers: no token/CTL validation of the method, route or header names/values, whitespace before ':' is accepted, and duplicate Content-Length headers are not detected, so smuggling and injection defenses are left to you.
- Incremental reads from a socket: there is no 'incomplete' result like pico's -2, and a header block cut mid-line returns success with the unterminated tail treated as the body.
- Buffers that are not NUL-terminated (raw recv() buffers): header lines are found with strstr, which ignores n and can read past the end of the buffer.
- HTTP/1.0 clients, pipelining or chunked bodies: HTTP/1.0 is rejected unless HTTPP_DONT_CHECK_VERSION is defined (then any 8-byte version string passes), the source says pipelined requests are 'not handled well', and chunked decoding is left to the caller.
- Production dependencies in general: one maintainer, 9 stars, no issues ever filed, and the latest commit broke the README example and the v2 benchmark, which still call the removed httpp_init_req.

## How it is fast

Zero-copy, zero-allocation parsing: v2.0.0 replaced v1.0.0's per-request malloc/realloc and per-header string copies with spans into the input and a caller-owned stack array, which is why v2 is \~3.1x faster than v1 at -O3 in the project's own table. Field and line boundaries are found with libc memchr (space, CR, ':') and strstr("\r\n") rather than a byte-at-a-time state machine, so scanning runs in glibc's SIMD string routines. It does almost no per-byte validation (no token/CTL tables, no incremental-parse state), so the hot path is delimiter search plus span bookkeeping. There is no hand-written SIMD.

## Compared with alternatives

Pick httpp only for a tiny self-contained C header with a response builder when the input is known to be complete, well-formed and NUL-terminated; for a speedup that keeps pico's API, validation and -2 incremental parsing, the vkrasnov AVX2 fork (1.68-1.79x) is safer, picohttpparser-rs covers Rust, and hparse reports a smaller \~12.5% wall-time gain but \~4x fewer instructions than pico.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond libc (memchr, strstr, strncmp) and POSIX strncasecmp from &lt;strings.h&gt; |
| **Minimum toolchain** | Not documented; the code uses C99 features (designated initializers, compound literals, stdbool) and a commit mentions C11 compatibility. The only compiler named is gcc 15.2.1, in the benchmarks. |
| **Platforms** | Not documented; portable C with no arch-specific code, but it needs POSIX strncasecmp (MSVC/Windows is not addressed). |
| **Thread safety** | Not documented; the parser keeps no global mutable state (everything lives in caller-provided structs), so separate buffers and structs per thread appear safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Body handling is 'lazy' by default: everything after the blank line is the body. HTTPP_CONSIDER_CONTENT_LENGTH makes it honor Content-Length (it mallocs and atol()s the value), and a Content-Length larger than the remaining buffer returns -1, not 'need more data'.
- If there are more headers than the array capacity (default 20), the whole parse returns -1, which you cannot tell apart from a malformed request.
- Methods outside the nine built-in ones become HTTPP_METHOD_UNKNOWN, and httpp_req_t has no method span, so the text of methods such as PROPFIND is lost. Methods over 10 bytes are rejected.
- Spans are not NUL-terminated and point into your buffer, so the buffer must outlive the request; httpp_span_to_str returns a malloc'd copy. httpp_res_to_raw prints headers with %s, so response header strings must be NUL-terminated. The implementation also leaks unprefixed macros (LTRIM, RTRIM, SETSTR) and reserved __-prefixed names into the translation unit that defines HTTPP_IMPLEMENTATION.

## Known shortcomings

- The \~2.26x over picohttpparser is inflated: picohttpparser was built without -msse4.2 (scalar path), and httpp does far less validation (no token/control-character checks, no incomplete-request handling). CPU given only as 'Ryzen 7'; ignore the -O0 rows.
- The benchmark and README example no longer compile at HEAD (functions renamed). The ratio is unstable (1.83x on an earlier run, 2.26x later, with picohttpparser unpinned). Header lines are found with strstr, which ignores the length and can over-read non-NUL-terminated buffers; no 'incomplete' result, so truncated headers parse as success; over 20 headers is reported as malformed. HTTP/1.0 rejected by default. One author, last commit 2025-12.

## Caveats and trade-offs

CPU given only as 'Ryzen 7' (no SKU); first-party benchmark, 5 runs averaged, clock()-based timing. The comparison is not like-for-like: picohttpparser runs its scalar path (no -msse4.2) while httpp calls libc memchr/strstr, which are SIMD in glibc. httpp also does far less validation: no token/CTL character checks on method, path or header names/values, no incomplete-request (-2) handling, and strstr over the input assumes NUL-termination. httpp is header-only and inlined into the bench TU, while pico is a separate TU. The -O0 rows are debug builds and should be ignored. Very new single-maintainer project (9 stars).

Header-only C, fixed-size stack-allocated header array, no SIMD (wins via lower per-call overhead, not vectorization). Only the v2.0.0 variant beats picohttpparser at -O3; v1.0.0 is slower at -O3 despite winning at -O0.

## Maintenance

The record says active, but the last commit was 2025-12-21, about 9 months ago (33 commits from one author since 2025-11-18). It is MIT-licensed and small enough (\~730 lines) to vendor and audit; vendor the 2.0.0 release asset, since the init functions were renamed after it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README #benchmark tables compare httppv1, httppv2 and picohttpparser at -O0 and -O3 and match the claimed numbers. The code is public (benchmarks/run.sh, bench-httppv2.c, bench-pico.c) and gcc 15.2.1 with -O0/-O3 is stated, but the CPU is given only as 'Ryzen 7 with 4.79GHz peek frequency', with no model. That makes it the project's own benchmark with partial methodology: tier C, not B (no peer review or independent suite).
- **Verifier notes:** I downgraded B to C: CPU model missing and the numbers are first-party, not an independent suite. Metadata checks out (MIT, not a fork, 9 stars, last commit 2025-12-21, active; releases 1.0.0 2025-11-29, 2.0.0 2025-12-05; benchmarks/httppv2.h is identical to the root httpp.h). The 2.26x is real on the page but inflated by the scalar-pico build and much lighter validation.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cebem1nt/httpp>
  - <https://github.com/cebem1nt/httpp#benchmark>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/README.md>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/run.sh>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/bench-pico.c>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/bench-httppv2.c>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/httppv2.h>
  - <https://github.com/cebem1nt/httpp/blob/main/httpp.h>
- **Sources the enricher read:**
  - <https://github.com/cebem1nt/httpp>
  - <https://github.com/cebem1nt/httpp#benchmark>
  - <https://github.com/cebem1nt/httpp/blob/main/httpp.h>
  - <https://github.com/cebem1nt/httpp/blob/main/example.c>
  - <https://github.com/cebem1nt/httpp/blob/main/test.c>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/README.md>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/run.sh>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/bench-httppv1.c>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/bench-httppv2.c>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/bench-pico.c>
  - <https://github.com/cebem1nt/httpp/blob/main/benchmarks/httppv2.h>
  - <https://github.com/cebem1nt/httpp/commits/main>
  - <https://github.com/cebem1nt/httpp/commit/e7dc721>
  - <https://github.com/cebem1nt/httpp/compare/f80ef57...8f77144>
  - <https://github.com/cebem1nt/httpp/blob/f80ef57/httpp.h>
  - <https://github.com/cebem1nt/httpp/releases>
  - <https://github.com/cebem1nt/httpp/releases/download/1.0.0/httpp.h>
  - <https://github.com/cebem1nt/httpp/releases/download/2.0.0/httpp.h>
  - <https://github.com/cebem1nt/httpp/issues>
  - <https://github.com/h2o/picohttpparser/blob/master/picohttpparser.c>
  - <https://github.com/h2o/picohttpparser/blob/master/picohttpparser.h>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cebem1nt/httpp`) · [data/wave5/enrich/raw/github_com_cebem1nt_httpp.json](../../../data/wave5/enrich/raw/github_com_cebem1nt_httpp.json) (enrichment confidence 0.8)

</details>
