# Picozig (zig-pico)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Zig` · `no license` · 🟢 active

> Pure-Zig port of picohttpparser's request parser. A self-run bench claims \~1.6x over scalar picohttpparser, but the baseline was not re-measured.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | Readme: '&gt;5 million requests per second (without SSE4)'; 'Result: 5086000 RPS on AMD 8845H mobile CPU'; 'Outperforms the original picohttpparser (\~3.2M headers/sec without SSE4)'. About 1.6x (derived from page data; the units differ, req/s vs headers/s) |
| **Workload** | Parsing HTTP request lines/headers in a tight loop via `zig run -O ReleaseFast src/request/bench.zig`, reported as requests-per-second and headers-per-second |
| **Metric** | throughput |
| **Hardware** | AMD 8845H mobile CPU (for the Picozig side only; the picohttpparser figure is not stated to have been measured on the same machine) |
| **Compiler and flags** | zig run -O ReleaseFast (Zig version not stated; build.zig.zon minimum_zig_version 0.14.0) |
| **Adoption** | 0 stars |
| **Last commit** | 2025-10-11 |
| **Links** | [repository](https://github.com/solenopsys/zig-pico) · [benchmark](https://github.com/solenopsys/zig-pico/blob/master/readme.md) |

## Verdict

src/request/bench.zig parses picohttpparser's bench.c 'kittyhell' request (10 headers, 32-slot array) 10 million times in one run, timed with a millisecond wall clock. Built with zig run -O ReleaseFast (Zig version not stated; the code targets 0.15.1) for the native CPU, it printed 5,086,000 requests/s on an AMD Ryzen 8845H mobile CPU. The '\~3.2M headers/sec without SSE4' picohttpparser figure has no stated source and was not re-measured: upstream bench.c has no timer and was not run on that machine. The units also differ, so the \~1.6x is only indicative.

## Use it when

- Reading or forking a compact example: about 275 lines of Zig in src/request/picozig.zig that map almost one-to-one onto picohttpparser's parse_request/parse_headers
- Zig prototypes and internal services that want zero-allocation request parsing with no C in the build, where you control the clients and can hand the parser at least 100 header slots
- Code that already calls picohttpparser's request API and wants the same i32 return convention in native Zig types instead of @cImport
- Targets where you would build picohttpparser without SSE4.2 anyway (aarch64, other non-x86). The code is portable Zig, but no speed number exists for those targets

## Skip it when

- Internet-facing servers. The header array can overflow (see gotchas), request-line validation is looser than upstream, and there is no fuzzing or audit. The project has one contributor and 0 stars
- You need responses, headers-only parsing, chunked transfer-encoding, or incremental re-parse with last_len. Only the request path is ported
- You already build picohttpparser with SSE4.2 or use an AVX2 fork. The claim is only against the scalar build, and it was not measured on the same machine
- Clients that send bare-LF line endings or several spaces between request-line tokens. Picozig returns -2 or -1 where picohttpparser accepts them
- Anything that needs clear reuse terms. There is no license file, and the code is a translation of Perl/MIT-licensed picohttpparser without its copyright notice

## How it is fast

It uses the same scalar design as picohttpparser without SSE4.2: a stateless single pass over the buffer, a 256-entry comptime lookup table for header-name token characters, and a byte-by-byte printable-ASCII scan (c -% 0x20 &lt; 0x5F) for header values. The only 'fast' helper, findCharFast, loads 16 bytes into a @Vector(16, u8) on x86-64/aarch64 but then tests each lane in a scalar loop. It has no vector compare and no PCMPESTRI, and it is only used for the method and path tokens. The README's 'without SSE4' means no hand-written SIMD. It does not mean a no-SSE4 build: zig run targets the host CPU by default, so LLVM was free to auto-vectorize with the benchmark machine's extensions.

## Compared with alternatives

Among the Zig siblings, hparse also beats picohttpparser and reports wall time, cycles and instructions against it, which makes it the better-evidenced choice. Picozig is mainly worth picking as a minimal, readable scalar translation of pico's request path to study or fork. For production use, the vkrasnov AVX2 fork, httparse or httpp (about 2.26x at -O3) have stronger benchmark evidence and more complete APIs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Zig std only) |
| **Minimum toolchain** | Zig 0.15.x in practice: the last commits port it to 0.15.1, and the response helper uses the 0.15 unmanaged ArrayList API. build.zig.zon still declares minimum_zig_version 0.14.0. Not verified on Zig 0.16.0 (released 2026-04-13) |
| **Platforms** | Any Zig target: pure Zig with no intrinsics and no syscalls in the parser. findCharFast uses 16-byte vectors on x86-64/aarch64 and 8-byte vectors elsewhere. Benchmarked only on x86-64 (AMD Ryzen 8845H) |
| **Thread safety** | Not documented. From the source, parseRequest is stateless and writes only to the caller's HttpRequest and header array, so concurrent calls with separate outputs look safe |
| **Drop-in for the baseline** | partial — it mirrors phr_parse_request's return codes and zero-copy output, but it is a Zig API with no C ABI. phr_parse_response, phr_parse_headers, phr_decode_chunked and the last_len argument are missing. It also ignores the caller's num_headers capacity |

## Gotchas

- Header-array overflow: parseRequest ignores params.num_headers and slices the many-item pointer as headers[0..100]. A request with more headers than your array writes past its end, and Zig cannot bounds-check a [\*]T slice in any build mode. The repo's own bench and a zig-httpuring test pass 32 slots, and test.zig passes 4-14. Always supply at least 100
- Looser than picohttpparser on the request line. test.zig asserts success for an empty method (' / HTTP/1.0') and an empty target ('GET  HTTP/1.0'), where upstream test.c expects -1. The method is not checked against token characters, so ':GET' is accepted. Multiple spaces between tokens, which upstream accepts, are rejected
- Header values keep trailing spaces and tabs (upstream trims them). A request whose final empty line is a lone LF at the end of the buffer returns -2 (incomplete) until more bytes arrive. test.zig asserts this for 'GET / HTTP/1.0\nHost: example.com\n\n'
- HttpRequest.body is never filled in. Errors come back only as i32 codes, because the internal ParseError is not surfaced. The bundled response formatter heap-allocates a StringHashMap and an ArrayList for every response

## Known shortcomings

- Memory-safety bug: parseRequest ignores the caller's num_headers and slices headers[0..100] on a many-item pointer (picozig.zig:265), so a request with more headers than the caller's array writes past its end in every build mode; callers must supply at least 100 slots (the repo's own bench passes 32). Looser than picohttpparser: accepts an empty method or target, doesn't check method token characters, rejects multiple spaces upstream accepts, keeps trailing whitespace in values. The '\~3.2M headers/sec' pico baseline has no source and wasn't run on the same machine; units differ (requests/s vs headers/s); one 10M-iteration run; host-CPU build may auto-vectorize despite 'without SSE4'. Partial port: no response parser, chunked decoder or last_len path; body never filled. No licence file and no picohttpparser copyright notice; 9 commits, 0 stars; build.zig.zon says Zig 0.14 but code needs 0.15, untested on 0.16.

## Caveats and trade-offs

The picohttpparser baseline (\~3.2M 'headers/sec') has no stated source and was not re-measured on the AMD 8845H. It is also in a different unit from Picozig's requests/sec, so the \~1.6x ratio is only indicative. src/request/bench.zig reuses the kittyhell request and 10M-iteration loop from picohttpparser's bench.c, so the workloads are comparable in principle, but the C baseline was not run alongside it. The project is a partial Zig translation of picohttpparser (MIT) without chunked encoding. It has no license file, 0 stars and a single contributor.

Partial translation of picohttpparser to pure Zig; explicitly does not implement chunked transfer-encoding; no SSE4/SIMD path at all, so the comparison is scalar-vs-scalar; single-file, unaudited, no test suite visible in README.

## Maintenance

Counts as active under the 12-month rule (last commit 2025-10-11, a port to Zig 0.15.1). In practice it is a 9-commit, single-author, unlicensed side project that only the author's own repos use (zig-httpuring and buddy-blocks, via a relative ../zig-pico path), so treat it as reference code rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The readme says '5086000 RPS on AMD 8845H mobile CPU' and 'Outperforms the original picohttpparser (\~3.2M headers/sec without SSE4)'. The picohttpparser figure has no stated source, was not measured on the same machine, and uses a different unit (headers/s versus requests/s). The benchmark code (src/request/bench.zig) and -O ReleaseFast are given, but the Zig version is not, so this is first-party C.
- **Verifier notes:** The record's benchmark_url was dead: the default branch is 'master' and the file is 'readme.md', so blob/main/README.md returns 404. It has been corrected. The last commit, 2025-10-11, is under 12 months before 2026-09-26, so maintenance_status changes from stale to active. License (none), stars (0) and fork status (not a fork) were checked and are correct.
- **Fields the verifier corrected:** `benchmark_url`, `maintenance_status`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/solenopsys/zig-pico>
  - <https://github.com/solenopsys/zig-pico/blob/main/README.md>
  - <https://github.com/solenopsys/zig-pico/blob/master/readme.md>
  - <https://raw.githubusercontent.com/solenopsys/zig-pico/master/readme.md>
  - <https://raw.githubusercontent.com/solenopsys/zig-pico/master/src/request/bench.zig>
  - <https://raw.githubusercontent.com/solenopsys/zig-pico/master/build.zig.zon>
  - <https://raw.githubusercontent.com/h2o/picohttpparser/master/README.md>
  - <https://raw.githubusercontent.com/h2o/picohttpparser/master/bench.c>
- **Sources the enricher read:**
  - <https://github.com/solenopsys/zig-pico>
  - <https://github.com/solenopsys/zig-pico/blob/master/readme.md>
  - <https://github.com/solenopsys/zig-pico/blob/master/build.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/build.zig.zon>
  - <https://github.com/solenopsys/zig-pico/blob/master/src/root.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/src/request/picozig.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/src/request/fast.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/src/request/bench.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/src/request/test.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/src/response/response-generator.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/src/response/date.zig>
  - <https://github.com/solenopsys/zig-pico/blob/master/.gitignore>
  - https://github.com/solenopsys/zig-pico/commits/master (GraphQL: 9 commits, 0 issues, 0 PRs, 2 forks, no license)
  - <https://github.com/TarasShu/zig-pico>
  - <https://github.com/ajafri2001/zig-pico>
  - https://github.com/solenopsys (GraphQL repository listing)
  - <https://github.com/solenopsys/zig-httpuring/blob/master/build.zig.zon>
  - <https://github.com/solenopsys/zig-httpuring/blob/master/src/http-request-parser.zig>
  - <https://github.com/solenopsys/zig-httpuring/blob/master/src/http-processor.zig>
  - <https://github.com/solenopsys/buddy-blocks/blob/master/build.zig.zon>
  - <https://github.com/solenopsys/zig-shock/blob/master/build.zig.zon>
  - <https://github.com/h2o/picohttpparser/blob/master/README.md>
  - <https://github.com/h2o/picohttpparser/blob/master/picohttpparser.c>
  - <https://github.com/h2o/picohttpparser/blob/master/test.c>
  - <https://github.com/h2o/picohttpparser/blob/master/bench.c>
  - <https://ziglang.org/download/index.json>
  - <https://hn.algolia.com/api/v1/search?query=picozig>
  - <https://hn.algolia.com/api/v1/search?query=zig-pico>
  - <https://hn.algolia.com/api/v1/search?query=solenopsys>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/solenopsys/zig-pico`) · [data/wave5/enrich/raw/github_com_solenopsys_zig_pico.json](../../../data/wave5/enrich/raw/github_com_solenopsys_zig_pico.json) (enrichment confidence 0.8)

</details>
