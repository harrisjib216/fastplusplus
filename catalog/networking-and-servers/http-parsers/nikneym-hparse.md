# hparse

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig SIMD HTTP/1.x parser modeled on picohttpparser; about 1.14x faster than a gcc -O3 picohttpparser build on x86-64.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | hparse: 1.27s wall-time / 5.38G cpu_cycles / 8.01G instructions vs picohttpparser: 1.45s wall-time / 6.16G cpu_cycles / 34.7G instructions (\~12.5% faster wall-clock, \~12.6% fewer cycles, \~77% fewer instructions retired); also beats httparse (Rust) at 1.54s wall-time / 6.53G cycles. |
| **Workload** | poop (like hyperfine, but with hardware counters; bench.txt comes from `poop -d 10000`) runs standalone binaries for picohttpparser (C), httparse (Rust) and hparse (Zig). Each binary parses one fixed 430-byte HTTP/1.1 GET request with 9 headers into a 32-slot header array, 10,000,000 times. Metrics: wall time, peak RSS, CPU cycles, instructions retired, cache references and misses, branch misses. |
| **Metric** | other |
| **Hardware** | Unspecified x86-64 (AMD64) Linux machine, according to the maintainer's comment in PR #2. No CPU model is stated for the bench.txt run. |
| **Compiler and flags** | hparse: zig build -Doptimize=ReleaseFast (bench/hparse/build.zig uses standardTargetOptions, so the default target is the native CPU). httparse 1.10.0: cargo build --release with [profile.release] opt-level=3 and no target-cpu. picohttpparser: bench/picohttpparser/Makefile runs `gcc ./main.c ./picohttpparser.c -I. -O3` on a vendored copy, with no -msse4.2 or -march flag, not the upstream Makefile. No compiler versions are stated. |
| **Adoption** | 38 stars |
| **Last commit** | 2025-10-24 |
| **Links** | [repository](https://github.com/nikneym/hparse) · [benchmark](https://github.com/nikneym/hparse/blob/main/bench/bench.txt) |

## Verdict

On an unnamed x86-64 Linux machine (author's `poop` run, 10M parses of one 430-byte GET with 9 headers, no compiler versions stated), hparse built with Zig ReleaseFast for the native CPU took 1.27 s and 5.38G cycles, against 1.45 s and 6.16G cycles for a vendored picohttpparser built with plain `gcc -O3` (probably without its SSE4.2 path) and 1.54 s for httparse 1.10: about 1.14x faster, at about 801 vs 3,470 instructions per parse (derived from page data). A third-party re-run on a Ryzen 7 8745HS gave 1.01 s against 1.14 s, but on Apple M3 and M4 Pro hparse is 1.5-1.6x slower than picohttpparser.

## Use it when

- You are writing a Zig server, proxy or client and want a zero-allocation, zero-copy HTTP/1.x head parser that tolerates partial reads from an event loop.
- x86-64 Linux deployments built with ReleaseFast for the native CPU. The author's run and a third-party run on a Ryzen 7 8745HS both show 11-12.5% less wall time and cycles than picohttpparser on a 430-byte GET with 9 headers.
- Traffic uses only the nine standard methods (GET, POST, HEAD, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH) and HTTP/1.0 or 1.1, and parsing the request head is a measurable share of CPU.
- You want one small MIT-licensed file (src/root.zig, about 1,100 lines including tests) to vendor and patch yourself, for example as the reference for a C++ port of the same @Vector/SWAR scan.

## Skip it when

- C or C++ codebases. There is no `export fn` or C header, so you would have to write a Zig shim that turns slices into pointer/length pairs and build it with Zig 0.15.
- Apple Silicon and other aarch64 targets. In the maintainer's open issue #3, an M4 Pro runs hparse in 1.464 s against 0.965 s for picohttpparser, about 1.5x slower. PR #2 shows 2.015 s against 1.252 s on an M3.
- Untrusted network input on unpatched main. Truncated requests can read one byte past the input slice (see gotchas), and the fix in PR #7 has not been merged.
- Requests with extension methods (WebDAV PROPFIND, MKCOL, custom verbs), tabs inside header values, or obs-fold continuation lines. hparse returns `error.Invalid` for all of these, while picohttpparser accepts them.
- You need chunked transfer-encoding decoding (`phr_decode_chunked`) or picohttpparser's `last_len` quick completeness check. hparse has neither, and it re-scans the whole buffer on every `error.Incomplete` retry.

## How it is fast

Delimiter and validity scans use Zig's portable `@Vector` SIMD: each chunk is compared against byte-range masks; the resulting bool vector is bitcast to an integer, and `@ctz` of its complement gives the offset of the first delimiter or invalid byte, so the cursor skips a whole chunk per step. Paths and header values use the target's suggested vector width (capped at 32 bytes, even on AVX-512), header names use a fixed 16-byte vector, and the tails fall back to 8-byte SWAR 'has byte less than n' bit tricks and then 256-entry lookup tables. Methods and the version are matched by loading 4 or 8 bytes as an integer and switching on magic constants such as 'GET ' and 'HTTP/1.1'; in the benchmark this comes to about 800 instructions per 430-byte request, against about 3,470 for the scalar picohttpparser build (derived from page data).

## Compared with alternatives

Pick hparse only when you are already in Zig and want a native package; for C/C++, the vkrasnov AVX2 picohttpparser fork (1.68-1.79x, drop-in, but untouched since 2014) and httpp (header-only C, about 2.26x in its own benchmark) link directly and claim larger gains. picohttpparser-rs is the choice for a memory-safe Rust port that is differentially tested against the C original.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Zig std only) |
| **Minimum toolchain** | Zig 0.15.x. CI pins 0.15.1, `minimum_zig_version` is not declared, and a PR to move to Zig 0.16.0 was closed without merging. |
| **Platforms** | Any Zig target. CI runs tests on x86_64 Linux (gnu and musl), x86_64 Windows, and aarch64 and x86_64 macOS. Vector width is chosen at compile time from the target CPU, with SWAR and scalar fallbacks. Speed wins are shown only on x86-64; it is slower than picohttpparser on Apple Silicon. |
| **Thread safety** | Stateless free functions with no global mutable state (from reading the source), so concurrent calls with separate output buffers are safe. Not otherwise documented. |
| **Drop-in for the baseline** | partial — the call shape matches phr_parse_request/phr_parse_response (buffer in; header array and count out; returns bytes consumed, incomplete or invalid). But it is a Zig-only API (slices, enums, error unions) with no C ABI, a fixed set of 9 methods, no last_len, no phr_parse_headers, and no phr_decode_chunked. |

## Gotchas

- One-byte out-of-bounds read on truncated input. After a scan stops at the end of the buffer, `cursor.char()` is read without checking `idx < end`. This happens in parseHeader, at the top of the parseHeaders loop and in parsePath, so a partial request can inspect the byte just past your slice. Open PR #7 ('add cursor pos checks', July 2026) adds these checks for the header paths but not for parsePath. Until it is fixed, pad buffers or patch the source.
- Validation is looser than picohttpparser in places. Header names accept any byte above 0x20 except ':' and DEL, rather than an RFC token table. An empty request-target (`GET  HTTP/1.1` with two spaces) is accepted, whereas picohttpparser rejects zero-length paths. Do not rely on it alone for request-smuggling defense.
- Header values are not trimmed of trailing spaces, unlike picohttpparser, which strips trailing SP/HTAB. Tabs inside a value are rejected on purpose (commit 'don't allow tabs in header values').
- Running out of `headers` slots returns `error.Invalid`, although the doc comment says `error.TooManyHeaders`. Size the array for your worst case. Returned slices point into your buffer, so keep it alive and unchanged while you use them.

## Known shortcomings

- Narrow, likely unfair win: 1.27 vs 1.45 s wall time against a picohttpparser built with plain gcc -O3, which probably drops its SSE4.2 fast path; no CPU model stated. About 1.5x slower than picohttpparser on Apple Silicon (#3).
- One-byte out-of-bounds read on truncated input in main (fix PR #7 unmerged and partial). Zig-only, no C interface; tested on Zig 0.15.1 only. Stricter than picohttpparser (rejects unknown methods, tabs in values, obs-fold) and looser in others (header-name bytes, empty request-target). No chunked decoder; rescans the whole buffer after each incomplete result. Last commit 2025-10.

## Caveats and trade-offs

1) No CPU model or compiler versions are given for the bench.txt run (it only says AMD64 Linux, in PR #2), so it is capped at C. 2) The baseline build is not like-for-like. picohttpparser is compiled with plain `gcc -O3` and no -msse4.2 or -march, so its `#ifdef __SSE4_2__` fast path is probably compiled out on a default x86-64 GCC. It retires about 3470 instructions per parse, roughly 8 per byte (derived from page data), which is consistent with the scalar path. hparse is built for the native CPU. 3) The win depends on the platform. On Apple Silicon, hparse is slower than picohttpparser. The maintainer's open issue #3 shows M4 Pro hyperfine times of hparse 1.464s vs picohttpparser 0.965s vs httparse 0.753s, and PR #2 on an M3 shows hparse 2.015s vs picohttpparser 1.252s. 4) A third party reproduced the x86 result in PR #2 on an AMD Ryzen 7 8745HS: hparse 1.01s vs picohttpparser 1.14s wall time (-11.3%), 4.91G vs 5.54G cycles. 5) This is a microbenchmark that repeats one request from a single host. 12.5% less wall time is about 1.14x faster (derived from page data).

Zig-only public API (needs a C shim for direct C++ linkage); streaming/never-allocates design explicitly modeled after picohttpparser so it can be 'swapped in smoothly'. A separate skylake-tuned build target exists (-Dcpu=skylake) but its numbers are not published.

## Maintenance

Last commit 2025-10-24, with a July 2026 bounds-check fix (PR #7) still open and a Zig 0.16 bump (PR #6) closed unmerged, so treat it as lightly maintained; it is MIT-licensed and small enough to vendor as one Zig file, but C++ can only call it through a hand-written shim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** bench/bench.txt is first-party poop output comparing hparse with picohttpparser and httparse. The picohttpparser row (1.45s / 6.16G cycles / 34.7G instr) and the hparse row (1.27s / 5.38G / 8.01G, delta -12.5% / -12.6% / -76.9%) match the claim. The benchmark code and flags are public (bench/Makefile, bench/picohttpparser/Makefile, bench/hparse/build.zig), but no CPU model is given for this run, so it stays C. A third-party re-run in PR #2 names a CPU (Ryzen 7 8745HS), but I did not upgrade to A: the baseline is built without ISA flags while hparse targets the native CPU, and no compiler versions are given.
- **Verifier notes:** The claimed numbers are accurate, but the gain is modest and only shown on x86-64, against a picohttpparser build that probably lacks its SSE4.2 path; hparse is about 1.5x slower than picohttpparser on Apple Silicon (issue #3, still open). Metadata checks out: MIT, 38 stars, not a fork or archived, last commit 2025-10-24 (active). The record said picohttpparser was built via the 'upstream Makefile'; it actually uses a vendored copy with a custom gcc -O3 one-line Makefile, which I corrected.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nikneym/hparse>
  - <https://github.com/nikneym/hparse/commits/main>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench.txt>
  - <https://github.com/nikneym/hparse/blob/main/bench/Makefile>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench.json>
  - <https://github.com/nikneym/hparse/blob/main/bench/picohttpparser/Makefile>
  - <https://github.com/nikneym/hparse/blob/main/bench/picohttpparser/main.c>
  - <https://github.com/nikneym/hparse/blob/main/bench/picohttpparser/picohttpparser.c>
  - <https://github.com/nikneym/hparse/blob/main/bench/hparse/build.zig>
  - <https://github.com/nikneym/hparse/blob/main/bench/hparse/src/main.zig>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench-httparse/Cargo.toml>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench-httparse/src/main.rs>
  - <https://github.com/nikneym/hparse/blob/main/README.md>
  - <https://github.com/nikneym/hparse/blob/main/LICENSE>
  - <https://github.com/nikneym/hparse/pull/2>
  - <https://github.com/nikneym/hparse/issues/3>
  - <https://github.com/nikneym/hparse/issues/5>
  - <https://github.com/nikneym/hparse/pull/4>
- **Sources the enricher read:**
  - <https://github.com/nikneym/hparse>
  - <https://github.com/nikneym/hparse/blob/main/README.md>
  - <https://github.com/nikneym/hparse/blob/main/src/root.zig>
  - <https://github.com/nikneym/hparse/blob/main/src/bench.zig>
  - <https://github.com/nikneym/hparse/blob/main/build.zig>
  - <https://github.com/nikneym/hparse/blob/main/build.zig.zon>
  - <https://github.com/nikneym/hparse/blob/main/.github/workflows/test-x86_64-linux.yml>
  - <https://github.com/nikneym/hparse/blob/main/.github/workflows/test-macos.yml>
  - <https://github.com/nikneym/hparse/blob/main/.github/workflows/test-x86_64-windows.yml>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench.txt>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench.json>
  - <https://github.com/nikneym/hparse/blob/main/bench/Makefile>
  - <https://github.com/nikneym/hparse/blob/main/bench/picohttpparser/Makefile>
  - <https://github.com/nikneym/hparse/blob/main/bench/picohttpparser/main.c>
  - <https://github.com/nikneym/hparse/blob/main/bench/picohttpparser/picohttpparser.c>
  - <https://github.com/nikneym/hparse/blob/main/bench/hparse/src/main.zig>
  - <https://github.com/nikneym/hparse/blob/main/bench/hparse/build.zig>
  - <https://github.com/nikneym/hparse/blob/main/bench/hparse/build.zig.zon>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench-httparse/src/main.rs>
  - <https://github.com/nikneym/hparse/blob/main/bench/bench-httparse/Cargo.toml>
  - <https://github.com/nikneym/hparse/blob/main/bench/headparser/src/main.zig>
  - <https://github.com/nikneym/hparse/commits/main>
  - <https://github.com/nikneym/hparse/issues?q=is%3Aissue+is%3Apr>
  - <https://github.com/nikneym/hparse/issues/3>
  - <https://github.com/nikneym/hparse/issues/5>
  - <https://github.com/nikneym/hparse/pull/2>
  - <https://github.com/nikneym/hparse/pull/6>
  - <https://github.com/nikneym/hparse/pull/7>
  - <https://github.com/cebem1nt/httpp>
  - <https://github.com/logicpl4gue/picohttpparser-rs>
  - <https://github.com/vkrasnov/picohttpparser>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/nikneym/hparse`) · [data/wave5/enrich/raw/github_com_nikneym_hparse.json](../../../data/wave5/enrich/raw/github_com_nikneym_hparse.json) (enrichment confidence 0.55)

</details>
