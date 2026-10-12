# iohttpparser (stateful-strict/lenient profiles)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Pull-based C23 HTTP/1.1 parser with strict framing checks; beats llhttp on header-heavy messages, not on tiny requests.

| | |
|---|---|
| **Beats** | llhttp |
| **Claimed result** | summary.md median req/s, 22 scenarios (21 common + 1 CONNECT). The best iohttpparser profile (stateful-strict alone gives the same count) beats llhttp in 16 and loses in 6. Wins include: req-headers 9.12M vs 7.87M (stateful-strict, 1.16x); resp-headers 12.08M vs 9.55M (stateful-lenient, 1.26x); hdr-value-ascii-clean 7.72M vs 5.16M (1.50x); hdr-count-32-minimal 2.89M vs 1.93M (1.50x); req-connect 14.32M vs 11.36M (1.26x). All ratios are derived from page data. llhttp wins req-small (22.91M vs best 18.36M, 0.80x), req-line-only, req-line-connect, hdr-name-heavy, hdr-uncommon-valid and hdr-count-04-minimal. picohttpparser is fastest in 21 of 22 scenarios. The exception is hdr-count-32-minimal, where stateful-strict edges it (2.89M vs 2.86M req/s). |
| **Workload** | req/s, MiB/s and ns/req for 22 fixed scenarios: 21 common request, response and header-stress fixtures of 33-703 bytes, plus one 99-byte CONNECT request. Each timed iteration parses one complete single-message buffer from scratch. Every call re-initializes the parser: llhttp_init plus llhttp_finish, or a fresh ihtp state for the stateful profiles. Each run does 200,000 iterations after 1,000 warmups, and the reported figure is the median of 5 runs. The comparison covers four iohttpparser profiles against vendored picohttpparser and llhttp 9.3.1 (bench/bench_throughput_compare.c). |
| **Metric** | throughput |
| **Hardware** | KVM guest with a generic QEMU 'AMD EPYC Processor' vCPU (family 23 model 1 stepping 2), 8 vCPU, 8 MiB L3; host CPU SKU not stated (per host.txt lscpu) |
| **Compiler and flags** | clang 22.1.0, CMAKE_BUILD_TYPE=Release with CMAKE_INTERPROCEDURAL_OPTIMIZATION=ON, -fuse-ld=lld -flto=thin (clang-release CMake preset) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-03-14 |
| **Links** | [repository](https://github.com/ioplane/iohttpparser) · [benchmark](https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/summary.md) |

## Verdict

The project's own harness parses one standalone 33-703 byte message per iteration with fresh parser state (200,000 iterations, median of 5 runs). It was built with Clang 22.1.0 (CMake Release + ThinLTO, lld) and run on an 8-vCPU KVM guest that reports only a generic 'AMD EPYC Processor' (host SKU unknown). The best iohttpparser profile (usually stateful-strict) beat vendored llhttp 9.3.1 in 16 of 22 scenarios by 1.01-1.50x and lost the other 6 (down to 0.80x on req-small); llhttp registers no header callbacks in this harness, and framing semantics are not included in these parse-only numbers.

## Use it when

- C servers, proxies or HTTP firewalls on Linux x86-64 that call llhttp today and would prefer a pull API that returns a typed struct of zero-copy header spans.
- Header-heavy HTTP/1.1 traffic (about 115-703 byte messages with many or long header values). This is where the benchmark shows 1.15-1.50x over llhttp, e.g. 7.72M vs 5.16M req/s on hdr-value-ascii-clean and 2.89M vs 1.93M on 32 minimal headers.
- Security-boundary ingress that needs strict RFC 9112 framing. The strict profile rejects TE+CL, conflicting Content-Length, duplicate or missing Host, bare LF and obs-fold. In the project's chunked-request benchmark the semantics pass adds about 1 ns (130.66 vs 131.74 ns).
- Event loops that read into one contiguous, growing buffer and want an explicit resumable parser state plus separate chunked and fixed-length body decoders.

## Skip it when

- When raw parse speed matters and you handle framing yourself: picohttpparser was 1.07-2.46x faster in 21 of the 22 scenarios on the same harness.
- Tiny requests and request-line-dominated traffic: llhttp won req-small (49 bytes, 22.91M vs 18.36M req/s, 0.80x), req-line-only, req-line-connect, hdr-name-heavy, hdr-uncommon-valid and hdr-count-04-minimal. Wins on the other request-line cases are 1.01-1.07x, which is within noise on a shared VM.
- Callback-driven streaming, ring buffers or scatter I/O: the API needs one contiguous accumulated buffer. Only HTTP/1.0 and 1.1 are parsed, and there is no llhttp-style pause/callback model.
- Non-Linux or non-x86 targets, MSVC, or pre-C23 compilers. Only Linux x86-64 is tested, the build turns on -msse4.2/-mavx2 by default, and the code uses GNU memrchr under _GNU_SOURCE.
- Anywhere that needs proven maturity: the only release is the pre-release 0.1.0-rc.2, from a single contributor, with 0 stars and no known third-party users or independent benchmark reproductions.

## How it is fast

The parser core uses block scans instead of llhttp's generated per-byte state machine. libc memchr finds each LF and header colon, and memrchr finds the space before the HTTP version. SWAR checks (8 bytes per 64-bit word, two words per loop iteration) reject control bytes and DEL in request targets and field values. A 256-entry token table is fused with the method/first-space search, methods resolve through a length switch plus memcmp, and results go straight into a caller-owned struct with no allocation or callbacks. The advertised SSE4.2 (PCMPESTRI) and AVX2 scanner is used only for token checks in the semantics layer, and the AVX2 path is a blocked scalar loop, so most of the SIMD comes from libc's memchr.

## Compared with alternatives

Pick it over the picohttpparser-class siblings (the vkrasnov AVX2 fork, hparse, http.c3l) only when you want framing semantics (TE/CL, Host, Connection, upgrade) and a chunked decoder in the same C library; for raw speed those siblings, or plain picohttpparser, win (pico is 1.07-2.46x faster than iohttpparser in 21 of 22 scenarios here). zttp is the llhttp alternative for Python code on httptools; iohttpparser is for C code that calls llhttp directly.

## Integration

| | |
|---|---|
| **Form** | static lib (a shared-lib target, CMake package and pkg-config file are also installed; six .c files of about 1.9k lines, small enough to vendor as a source drop) |
| **Dependencies** | none at runtime beyond a libc that provides memrchr (glibc/musl); CMake 3.25+ to build |
| **Minimum toolchain** | C23 required (CMAKE_C_STANDARD 23; uses nullptr and [[nodiscard]]); CMake 3.25+. Developed and benchmarked with Clang 22.1.0, and GCC presets exist, but the minimum compiler version is not documented. |
| **Platforms** | Linux x86-64 is the only tested platform (CI runs ubuntu-latest with an Oracle Linux 10 dev container). The IOHTTPPARSER_SIMD_SSE42/AVX2 options default ON and add -msse4.2/-mavx2, so other architectures must turn them OFF (inferred from CMakeLists; not documented). macOS and MSVC are not supported as-is because of memrchr and C23. |
| **Thread safety** | Not documented. Parse, semantics and decoder calls touch only caller-owned state and output, so independent parsers on separate threads are fine. The SIMD dispatch table used by the semantics layer is lazily initialized through a plain static bool with no atomic or call_once, which is a formal data race if two threads make the first call at the same time. |
| **Drop-in for the baseline** | false. llhttp is a callback-driven state machine; this is a pull API with typed output structs over a caller-owned accumulated buffer, so the llhttp callback glue has to be rewritten. |

## Gotchas

- ihtp_request_t and ihtp_response_t each embed a fixed IHTP_MAX_HEADERS array (default 64, about 2 KB per struct), and the stateless wrappers memset the whole struct on every call. IHTP_MAX_HEADERS changes the struct layout, so the library and every translation unit that includes the headers must be built with the same value. The header comment names a nonexistent -DHP_MAX_HEADERS; the real macro is IHTP_MAX_HEADERS.
- The stateful API stores header spans from earlier calls as raw pointers into your accumulated buffer, while its own cursor is only an offset. If you realloc or move that buffer between calls, parsing carries on without error but the earlier spans dangle.
- The 'SIMD-accelerated' label mostly does not apply to the parse hot path. ihtp_parse_request/response/headers never call the scanner vtable, so throughput depends largely on your libc's memchr.
- IHTP_POLICY_LENIENT relaxes only obs-fold, bare LF, TE+CL and spaces in the request target. The semantics stage still rejects HTTP/1.1 requests without Host, comma-list Content-Length (e.g. '5, 5') and Transfer-Encoding chains that do not end in chunked, and ihtp_decode_chunked() rewrites your buffer in place.

## Known shortcomings

- llhttp 9.3.1 wins 6 of 22 scenarios (including req-small, 0.80x) and picohttpparser is faster in almost every scenario; each iteration parses one short message with a re-initialized parser. The CPU is a generic KVM 'AMD EPYC Processor' string.
- The 'SIMD-accelerated' claim is mostly hollow: the parse hot path uses memchr/SWAR and a lookup table, and the AVX2 backend is a scalar loop in 32-byte blocks. Several wins are 1-7%; the llhttp harness registers only on_message_complete while iohttpparser's framing checks are skipped. Needs C23 and GNU memrchr; SSE4.2/AVX2 options default ON (non-x86 must disable); first-use dispatch init is a data race; stateful parsing keeps raw pointers into earlier buffers. Single contributor, rc release only.

## Caveats and trade-offs

Zero-star, single-contributor project published in March 2026, with no independent adoption or third-party reproduction. The benchmark ran in a KVM guest whose lscpu shows only the generic 'AMD EPYC Processor' vCPU model, so the real host CPU is unknown and results carry shared-cloud noise. Each iteration parses one tiny (33-703 byte) standalone message with per-call parser init, which measures small-message latency rather than streaming throughput. Wins over llhttp are not uniform: llhttp wins 6 of 22 scenarios, including req-small (0.80x), three request-line cases and three header cases. picohttpparser is 1.07-2.46x faster than the best iohttpparser profile in 21 of 22 scenarios.

Pull-based API with explicit parser state and a separate semantics/body-decoder stage, unlike llhttp's callback-driven model; adds framing-ambiguity rejection (TE+CL, conflicting Content-Length) that llhttp only partially covers; consistently slower than picohttpparser across all measured scenarios.

## Maintenance

Pre-release only (v0.1.0-rc.2, 2026-03-14) from a single contributor, with no commits to main since 2026-03-14 (only Dependabot PRs and one maintainer PR open since); dual MIT OR LGPL-2.1-or-later and small enough to vendor on Linux x86-64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** summary.md compares four iohttpparser profiles with picohttpparser and vendored llhttp 9.3.1. The code is public (bench/bench_throughput_compare.c, scripts/run-throughput-median.sh), clang 22.1.0 is in toolchain.txt, and the flags come from the clang-release preset. The CPU model is not identified: host.txt lscpu shows only the generic QEMU/KVM vCPU string 'AMD EPYC Processor' (family 23 model 1, hypervisor KVM) with no host SKU or generation, so the numbers are first-party and fall short of A.
- **Verifier notes:** All four numbers in the claim are on the page. The original claim was wrong that picohttpparser wins every scenario (iohttpparser edges it in hdr-count-32-minimal), and it understated llhttp's wins (req-small and three header scenarios also go to llhttp). The workload's '\~8GiB per case keep-alive stream' is wrong: 200,000 iterations of a single 33-703 byte message is about 7-140 MB per case. License MIT, 0 stars, not fork or archived, last main commit 2026-03-14 (active); record metadata is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/summary.md>
  - <https://github.com/ioplane/iohttpparser>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/host.txt>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/toolchain.txt>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/manifest.json>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/throughput-median.tsv>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/throughput-connect-median.tsv>
  - <https://github.com/ioplane/iohttpparser/blob/main/CMakePresets.json>
  - <https://github.com/ioplane/iohttpparser/blob/main/CMakeLists.txt>
  - <https://github.com/ioplane/iohttpparser/blob/main/bench/bench_throughput_compare.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/scripts/run-throughput-compare.sh>
  - <https://github.com/ioplane/iohttpparser/blob/main/scripts/run-throughput-median.sh>
  - <https://github.com/ioplane/iohttpparser/blob/main/README.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/third_party/llhttp/llhttp.h>
- **Sources the enricher read:**
  - <https://github.com/ioplane/iohttpparser>
  - <https://github.com/ioplane/iohttpparser/blob/main/README.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/summary.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/summary-extended.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/throughput-median.tsv>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/scanner-bench.tsv>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/host.txt>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/toolchain.txt>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/manifest.json>
  - <https://github.com/ioplane/iohttpparser/blob/main/tests/artifacts/pmi-psi/runs/20260313T210231Z-3b9c398/run.txt>
  - <https://github.com/ioplane/iohttpparser/blob/main/include/iohttpparser/iohttpparser.h>
  - <https://github.com/ioplane/iohttpparser/blob/main/include/iohttpparser/ihtp_types.h>
  - <https://github.com/ioplane/iohttpparser/blob/main/include/iohttpparser/ihtp_parser.h>
  - <https://github.com/ioplane/iohttpparser/blob/main/include/iohttpparser/ihtp_scanner.h>
  - <https://github.com/ioplane/iohttpparser/blob/main/include/iohttpparser/ihtp_semantics.h>
  - <https://github.com/ioplane/iohttpparser/blob/main/include/iohttpparser/ihtp_body.h>
  - <https://github.com/ioplane/iohttpparser/blob/main/src/ihtp_internal.h>
  - <https://github.com/ioplane/iohttpparser/blob/main/src/ihtp_parser.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/src/ihtp_scanner_scalar.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/src/ihtp_scanner_sse42.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/src/ihtp_scanner_avx2.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/src/ihtp_semantics.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/CMakeLists.txt>
  - <https://github.com/ioplane/iohttpparser/blob/main/CMakePresets.json>
  - <https://github.com/ioplane/iohttpparser/blob/main/bench/bench_throughput_compare.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/bench/bench_extended_contract.c>
  - <https://github.com/ioplane/iohttpparser/blob/main/docs/en/02-comparison.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/docs/en/03-production-hardening.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/docs/en/06-parser-state.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/docs/en/07-body-decoder.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/docs/en/09-test-results.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/docs/plans/2026-03-11-sprint-11-comparison-report.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/SECURITY.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/CHANGELOG.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/CONTRIBUTING.md>
  - <https://github.com/ioplane/iohttpparser/blob/main/deploy/podman/Containerfile>
  - <https://github.com/ioplane/iohttpparser/blob/main/.github/workflows/ci.yml>
  - <https://github.com/ioplane/iohttpparser/issues>
  - <https://github.com/ioplane/iohttpparser/pulls>
  - <https://github.com/ioplane/iohttpparser/releases>
  - <https://github.com/ioplane/iohttpparser/commits/main>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ioplane/iohttpparser`) · [data/wave5/enrich/raw/github_com_ioplane_iohttpparser.json](../../../data/wave5/enrich/raw/github_com_ioplane_iohttpparser.json) (enrichment confidence 0.5)

</details>
