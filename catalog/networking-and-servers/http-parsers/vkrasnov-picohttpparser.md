# picohttpparser AVX2 fork (vkrasnov)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT OR Perl License (Artistic-1.0-Perl OR GPL-1.0-or-later), stated in source-file headers and README (no LICENSE file; GitHub spdx_id null); inherited unchanged from upstream` · 🔴 abandoned

> AVX2 bitmap rewrite of picohttpparser's header scanner; 1.7-1.8x the SSE4.2 PCMPESTRI version on Haswell.

| | |
|---|---|
| **Beats** | picohttpparser |
| **Claimed result** | bench.c: 3,900,156 -&gt; 6,963,788 (1.79x); fukamachi.c: 4,807,692 -&gt; 8,064,516 (1.68x). Page does not label the unit (higher is better; consistent with requests/second). |
| **Workload** | Single-threaded req/s over two request corpora: pico's own bench.c request and fukamachi/fast-http's benchmark request (fukamachi.c), comparing the original PCMPESTRI (SSE4.2) token-matching path against a new AVX2+BMI2 bitmask path processing 128 bytes at a time. |
| **Metric** | throughput |
| **Hardware** | Intel Haswell i5-4278U, turbo disabled for consistency |
| **Compiler and flags** | gcc 4.9.2; -mavx2 -mbmi2 -O3 |
| **Adoption** | 20 stars (fork); submitted as h2o/picohttpparser PR #10, left open/unmerged until closed 2020-07-17 |
| **Last commit** | 2014-12-18 |
| **Links** | [repository](https://github.com/vkrasnov/picohttpparser) · [benchmark](https://blog.cloudflare.com/improving-picohttpparser-further-with-avx2/) |

## Verdict

On a Haswell i5-4278U with turbo off, built with GCC 4.9.2 -O3 -mavx2 -mbmi2, the AVX2 build parsed bench.c's 703-byte, 9-header request 1.79x faster than December 2014 picohttpparser's PCMPESTRI path (6.96M vs 3.90M per second, consistent with 10M iterations taking 1.436 s vs 2.564 s), and fukamachi.c's 430-byte request 1.68x faster (8.06M vs 4.81M). The fukamachi figures match a 100,000-iteration loop, so those runs lasted only about 12-21 ms; both tests repeatedly parse one complete, hot-cache request.

## Use it when

- Studying or porting the technique: the whole change is a single \~309-line diff to picohttpparser.c, a compact example of replacing per-token PCMPESTRI searches with 128-byte AVX2 bitmaps plus TZCNT.
- Throughput experiments on x86-64 Haswell-or-newer CPUs where HTTP/1 header scanning dominates CPU time and requests run a few hundred bytes with many headers (the benchmark requests were 430 and 703 bytes, 9 headers each).
- Parsing complete, well-formed header blocks from a trusted source (behind a proxy that already validated framing, or replaying captured traffic), where you can guarantee the whole header block is in the buffer before calling.
- A/B testing against picohttpparser without touching call sites, because the four exported functions keep the 2014 upstream signatures.

## Skip it when

- Internet-facing servers parsing untrusted or partially received requests. Reading the code, malformed header names and values are accepted, and truncated input can move the cursor past len (see gotchas). The author's own PR says the code 'was not tested much, so it might contain some bugs'.
- Peers that send bare-LF line endings: the AVX2 path returns -1 for them, while upstream and the fork's non-AVX2 path accept them.
- Portable binaries: AVX2 is chosen at compile time with no runtime dispatch, so a -mavx2 build needs a Haswell-class CPU. Windows (LLP64), MSVC and C++ builds are also out because the code uses GNU inline asm, void\* arithmetic and 64-bit unsigned long shifts.
- Chunked bodies from untrusted peers: phr_decode_chunked is the 2014 code. It lacks upstream's 2023-2025 hardening (rejecting suspicious chunk sizes, capping chunk overhead, requiring CRLF in chunk headers) and has no phr_decode_chunked_is_in_data.
- Anything that needs upstream's later fixes or testing: upstream is 98 commits ahead of the fork's base, including ASan/UBSan CI and MSVC/g++ build fixes.

## How it is fast

Upstream finds each delimiter with SSE4.2 PCMPESTRI. That instruction covers 16 bytes, has about 11 cycles of latency and runs once per token, so short header fields make the parser latency-bound (the blog puts the ceiling at about 1.45 bytes/cycle). The fork classifies 128 bytes at a time with plain AVX2 compare/and/or ops, treating bytes as signed so that 0x00-0x1F, ':', TAB and DEL can be tested without unsigned compares. It packs the results with PMOVMSKB into two 128-bit bitmaps, one for name/value delimiters and one for line ends, then walks them with TZCNT and reuses them across several headers before rescanning, which trades one latency-bound search per token for bulk, throughput-bound classification.

## Compared with alternatives

Choose it only when you specifically want picohttpparser's C API with this AVX2 bitmap design, for study or a controlled experiment. The siblings saw commits in 2025-2026: httpp (header-only C, which reports \~2.26x over picohttpparser on its own hardware), hparse (Zig SIMD, streaming) and picohttpparser-rs (a safe-Rust port that reports 133,352 differential cases matching the C original), so they are the better production picks.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc plus &lt;immintrin.h&gt; intrinsics) |
| **Minimum toolchain** | C with GNU extensions (void\* arithmetic, AT&T inline asm) on GCC or Clang with -mavx2 (the published build used GCC 4.9.2 -O3 -mavx2 -mbmi2); not MSVC, not compilable as C++ |
| **Platforms** | x86-64 with AVX2 and TZCNT (Haswell or newer) on an LP64 OS (Linux/macOS/BSD) for the fast path; other targets get the 2014 SSE4.2/scalar code |
| **Thread safety** | Not documented. The functions are stateless, allocate nothing and only read static const tables, so concurrent calls on separate buffers are safe by construction. |
| **Drop-in for the baseline** | partial: same four functions and signatures as 2014 picohttpparser, so it is a one-file swap, but it behaves differently on malformed or truncated input and lacks upstream's later API (phr_decode_chunked_is_in_data) and hardening |

## Gotchas

- The AVX2 code is only on the 'avx2' branch; 'master' is unmodified upstream from 2014-12-16. The Makefile and .travis.yml never pass -mavx2, so 'make test' only exercises the old code path.
- The header-name scan stops at any byte 0x00-0x1F as well as ':' and never checks that it stopped on ':'. As a result 'a\0b: c' parses as name 'a' with value 'b: c' instead of returning -1, and by my reading the fork's own 'NUL/CTL in header name' tests would fail under -mavx2.
- 'two_char & 0x0a == 0x0a' parses as 'two_char & 1' because == binds tighter than &. So bare-LF line endings are rejected, while a lone CR, ESC or DEL ends a header value instead of producing an error ('CTL in header value' test).
- Despite the 128-byte window, callers need no buffer alignment (all loads are unaligned). For the final &lt;128 bytes, though, the bitmap comes from an uninitialized 32-byte stack copy, zero padding or a stale upper half, and '\*(unsigned short\*)buf' reads 2 bytes. So by code reading, a truncated first parse (last_len=0) can advance past len instead of returning -2.

## Known shortcomings

- An unmerged 2015 fork (upstream PR #10 closed 2020); the AVX2 path is not in upstream picohttpparser. Needs AVX2 and BMI2; measured on a Haswell laptop with gcc 4.9.2. Licence is MIT or Perl licence from the source headers (GitHub shows none).
- Correctness bugs in the AVX2 path (source reading, not run): an operator-precedence bug rejects bare-LF line endings and accepts lone CR/ESC/DEL as value terminators; the header-name scan never checks it stopped on ':' ('a\0b: c' parses as name 'a'); on truncated input it reads past the buffer and can advance past len instead of returning -2. CI never builds with -mavx2, so the AVX2 path is untested. 98 commits behind upstream, missing the 2023-2025 chunked-decoder hardening; GNU C/LP64 only. The AVX2 code is on the 'avx2' branch, not master.

## Caveats and trade-offs

Benchmark is from 2014 (gcc 4.9.2, Haswell laptop CPU) so absolute numbers are over a decade old, though methodology (CPU model, compiler, flags, public code) is fully specified, meeting tier A. PR was never merged into h2o/picohttpparser and the fork has had no commits since 2014.

Requires AVX2+BMI2 (Haswell or newer), so it is not a drop-in for older or non-x86 hardware; upstream maintainer never merged it, so it only exists as an unmerged fork/branch; requires 128-byte-aligned buffer handling per the design change from latency- to throughput-oriented processing.

## Maintenance

Abandoned since its single 2014-12-18 commit and never merged upstream (h2o/picohttpparser PR #10 closed in 2020). It is MIT/Perl dual-licensed and a single .c/.h pair, so it is easy to vendor, but treat it as a prototype that needs an audit and fuzzing before use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Cloudflare blog (Vlad Krasnov, 2014-12-18) table compares original PCMPESTRI picohttpparser vs the AVX2 version: bench.c 3,900,156 -&gt; 6,963,788 (1.79x), fukamachi.c 4,807,692 -&gt; 8,064,516 (1.68x), stating gcc 4.9.2, -mavx2 -mbmi2 -O3 for both, Haswell i5-4278U turbo off. Benchmark code is public: bench.c on the fork's avx2 branch (10M-iteration phr_parse_request loop) and fukamachi.c on the fork's kazuho/expr/fukamachi-fast-http-bench branch.
- **Verifier notes:** The AVX2 code lives on the fork's avx2 branch (last commit 2014-12-18); master stops at 2014-12-16 (upstream commit). Upstream PR h2o/picohttpparser#10 was closed unmerged 2020-07-17 after kazuho said the maintenance cost was not worth it; the PR body says 1.78x for bench.c, up to 2x on other inputs. The 'req/s' unit in the record is inferred, not printed on the page, so I added that to claimed_speedup.
- **Fields the verifier corrected:** `claimed_speedup`, `license`
- **Pages the verifier opened:**
  - <https://blog.cloudflare.com/improving-picohttpparser-further-with-avx2/>
  - <https://github.com/vkrasnov/picohttpparser>
  - <https://github.com/vkrasnov/picohttpparser/tree/avx2>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/bench.c>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/picohttpparser.c>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/README.md>
  - <https://github.com/vkrasnov/picohttpparser/tree/kazuho/expr/fukamachi-fast-http-bench>
  - <https://github.com/h2o/picohttpparser/pull/10>
- **Sources the enricher read:**
  - <https://blog.cloudflare.com/improving-picohttpparser-further-with-avx2/>
  - <https://github.com/vkrasnov/picohttpparser>
  - <https://github.com/vkrasnov/picohttpparser/tree/avx2>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/README.md>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/picohttpparser.c>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/picohttpparser.h>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/bench.c>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/test.c>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/Makefile>
  - <https://github.com/vkrasnov/picohttpparser/blob/avx2/.travis.yml>
  - <https://github.com/vkrasnov/picohttpparser/compare/master...avx2>
  - <https://github.com/vkrasnov/picohttpparser/tree/kazuho/expr/fukamachi-fast-http-bench>
  - <https://github.com/vkrasnov/picohttpparser/blob/kazuho/expr/fukamachi-fast-http-bench/fukamachi.c>
  - <https://github.com/h2o/picohttpparser/pull/10>
  - <https://github.com/h2o/picohttpparser/compare/3dedc7dc82b7...master>
  - <https://github.com/h2o/picohttpparser/blob/master/picohttpparser.c>
  - <https://github.com/h2o/picohttpparser/blob/master/picohttpparser.h>
  - <https://github.com/h2o/picohttpparser/pull/65>
  - <https://github.com/h2o/picohttpparser/commit/b820122>
  - <https://github.com/h2o/picohttpparser/pull/82>
  - <https://github.com/cebem1nt/httpp>
  - <https://github.com/nikneym/hparse>
  - <https://github.com/logicpl4gue/picohttpparser-rs>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/vkrasnov/picohttpparser`) · [data/wave5/enrich/raw/github_com_vkrasnov_picohttpparser.json](../../../data/wave5/enrich/raw/github_com_vkrasnov_picohttpparser.json) (enrichment confidence 0.8)

</details>
