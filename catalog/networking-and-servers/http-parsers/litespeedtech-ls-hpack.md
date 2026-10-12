# ls-hpack (LiteSpeed HPACK)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> LiteSpeed's C HPACK (RFC 7541) codec with 64K-entry two-byte Huffman tables; beat a 2016 nghttp2 Huffman encoder 2.4-5.8x.

| | |
|---|---|
| **Beats** | nghttp2 (HPACK); the numeric benchmark covers only nghttp2's HPACK Huffman encoder (nghttp2_hd_huffman.c at revision 0e1d0400d86a) |
| **Claimed result** | ls-hpack's fast Huffman encoder vs nghttp2's encoder, in seconds (median of 5): 'LiteSpeed' 8.67 vs 20.59 (2.37x), x-fb-debug 5.25 vs 30.31 (5.77x), x-fb-backslash 7.22 vs 32.21 (4.46x), idle text 9.32 vs 52.25 (5.61x). The same post also has it 1.11x-2.12x faster than nginx's encoder and 1.18x-3.59x faster than h2o's. The companion 'Fast Huffman Decoder' post (2019-09-16) reports 1.15x-1.96x faster than nginx 1.16.1's decoder, which it says derives from nghttp2's 4-bit decoder. Bun's build script separately says ls-hpack is "faster than nghttp2's for our workloads", with no numbers. |
| **Workload** | HPACK Huffman string encoding microbenchmark (RFC 7541 Huffman code). Code extracted from each project into litespeedtech/benchmarks/huffman-encoder and run for a fixed iteration count on 4 inputs: 'LiteSpeed' (small), a real x-fb-debug header value from the Facebook response QIF (medium), the same value with backslashes to force the fallback path, and several paragraphs of prose (large). Median of 5 runs. The companion decoder benchmark compares only against nginx 1.16.1's Huffman decoder. |
| **Metric** | other |
| **Compiler and flags** | Makefile CFLAGS=-Wall -DNDEBUG -O3 -g0; compiler and version not stated |
| **Adoption** | 56 stars; vendored by oven-sh/bun (scripts/build/deps/lshpack.ts) and a git submodule of litespeedtech/lsquic (1,876 stars); used in LiteSpeed Web Server |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/litespeedtech/ls-hpack) · [benchmark](https://blog.litespeedtech.com/2019/10/03/fast-huffman-encoder/) |

## Verdict

LiteSpeed's 2019 post timed only the Huffman string encoder, with each project's code extracted into standalone C: ls-hpack rev a1f1ea8ce298f against nghttp2 rev 0e1d0400d86a (2016, called through its nghttp2_bufs chain). Runs used fixed iteration counts on four inputs and report the median of 5, built -O3 -DNDEBUG with CPU and compiler not stated. Results: 2.37x on 'LiteSpeed' (8.67 vs 20.59 s), 5.77x on an 88-byte x-fb-debug value (5.25 vs 30.31 s), 4.46x when a backslash forces the fallback, and 5.61x on prose. The same run shows 1.11-2.12x over nginx 1.16.1 and 1.02-2.14x over ls-hpack's own previous encoder; the decoder post reports 1.15-1.96x over nginx 1.16.1 only.

## Use it when

- You are building an HTTP/2 server, proxy or client in C/C++ that already handles framing and needs only HPACK. This is the codec shipped in LiteSpeed/OpenLiteSpeed and lsquic and vendored by Bun.
- Your headers carry medium or long Huffman-coded values (tokens, cookies, base64 debug headers). On an 88-byte x-fb-debug value and on prose, the two-byte table ran 1.7-2.1x faster than ls-hpack's own byte-at-a-time encoder (derived from the post's numbers).
- You proxy HTTP/2 to HTTP/1.1. With the defaults, the decoder writes 'name: value\r\n' straight into your buffer and fills in XXH32 name and name+value hashes that the encoder (or ls-qpack) can reuse.
- You are on a 64-bit target with cache to spare. The 64-bit build flushes 8 output bytes per step; 32-bit builds take a 4-byte path.

## Skip it when

- You need a full HTTP/2 stack. ls-hpack does HPACK only: framing, flow control and RFC 9113 field-name validation must come from elsewhere. The maintainer says in #22 that validation does not belong in ls-hpack.
- Memory or L2 cache is tight. The default build carries 768 KB of read-only Huffman tables (512 KB encoder + 256 KB decoder). The CMake MinSizeRel build sets LS_HPACK_USE_LARGE_TABLES=0 and falls back to the small tables and the slower paths.
- You need the speedup to hold against current nghttp2. The only comparison used nghttp2 revision 0e1d0400d86a (2016). nghttp2 committed 'Faster huffman encoding' and 'Faster huffman decoding' on 2019-10-08, five days after LiteSpeed's post, and changed decoding again in 2025. No re-run exists, and the decoder was never compared with nghttp2 at all.
- Your header values are short, or most headers hit the static table. On the 9-byte 'LiteSpeed' input the two-byte table gave nothing over ls-hpack's old encoder (8.67 s vs 8.80 s); the post says strings under 14 bytes see no speedup.
- You must run a tagged release on untrusted input. v2.3.5 (the latest tag, and what Bun pins) still has a fast decoder that accepts EOS padding longer than 7 bits, against RFC 7541 §5.2 (#24), plus UBSan-found undefined behaviour (#26). Both were fixed only on master, on 2026-09-13.

## How it is fast

The Huffman encoder looks up the next two input bytes at once in a 65,536-entry table (hencs, 8 B per entry, 512 KB) that holds their combined code of up to 32 bits, and shifts it into a 64-bit accumulator. Pairs whose code would be longer are marked lens=64, and the encoder backs up and finishes with the byte-at-a-time loop. The Huffman decoder uses a 65,536-entry table (hdecs, 256 KB) indexed by 16 input bits that emits 1-3 bytes per lookup. It falls back to the classic 4-bit state-machine decoder for codes longer than 16 bits. Static-table matching hashes the name and the name+value with XXH32 (seed found by bin/find-xxh.c and shared with ls-qpack) into 512-slot index arrays. The dynamic table is two chained hash tables (by name and by name+value). The decoder can also hand those hashes and ready-made 'name: value\r\n' lines to the caller, so a proxy can skip rehashing and reformatting.

## Compared with alternatives

None of the catalogued http-parsers siblings do HPACK. picohttpparser and its forks, httparse, iohttpparser, zttp and the Puma parser all parse HTTP/1.x text, and Ada, lucid-url and sorug parse URLs. Pick ls-hpack when HTTP/2 header (de)compression is the bottleneck, and pair it with one of those for HTTP/1.x or URL work.

## Integration

| | |
|---|---|
| **Form** | static lib via CMake (SHARED=1 for a shared lib) or source-drop (lshpack.c + deps/xxhash/xxhash.c, as Bun builds it) |
| **Dependencies** | xxHash (bundled in deps/xxhash; build xxhash.c yourself, set LSHPACK_XXH to compile it into the lib, or point XXH_INCLUDE_DIR at your own); &lt;sys/queue.h&gt; (a compat copy ships for musl/Windows) |
| **Minimum toolchain** | Minimum C standard not documented; the code uses C99 designated array initializers. CI covers gcc-8 and clang (Travis), MSVC (AppVeyor) and FreeBSD 13.3 (Cirrus). CMakeLists declares 2.8, and modern CMake needs -DCMAKE_POLICY_VERSION_MINIMUM=3.5 (#21). |
| **Platforms** | README lists Linux, FreeBSD and Windows as tested. musl works via compat/queue, OpenBSD via SIMPLEQ shims. 32- and 64-bit builds are handled. Portable scalar C with no SIMD. The encoder table's byte order comes from __BYTE_ORDER/__LITTLE_ENDIAN. |
| **Thread safety** | Not documented. All mutable state lives in caller-owned lshpack_enc/lshpack_dec structs and the only globals are const tables, so separate instances share nothing mutable. A single instance is not safe to share. |
| **Drop-in for the baseline** | no |

## Gotchas

- A plain `cmake .` without -DCMAKE_BUILD_TYPE=Release builds with -O0 -g3 -fsanitize=address and LS_HPACK_EMIT_TEST_CODE. Bun's build notes it had to pin Release because of this. The CMake file also has no install() rules (#21).
- The compile-time macros LSHPACK_DEC_HTTP1X_OUTPUT and LSHPACK_DEC_CALC_HASH (both default 1) change decoder output: 4 extra bytes per header for ': ' and CRLF, plus hash computation. lshpack.h reads them, so the library and its callers must be built with the same values. Name and value lengths are uint16 unless LSXPACK_MAX_STRLEN=UINT32_MAX.
- The encoder expects lowercase header names but does not enforce this (maintainer reply in #10). v2.3.4 and earlier silently stripped trailing whitespace from decoded names (#22, a regression per PR #23, fixed in v2.3.5).
- The two-byte encoder table's layout is chosen with `#if __BYTE_ORDER == __LITTLE_ENDIAN`. On a toolchain that defines neither macro, both evaluate to 0 and the little-endian layout is picked, which is right only on little-endian targets.

## Known shortcomings

- Evidence covers only the HPACK Huffman encoder (2.37-5.77x over a 2019 copy of nghttp2's), not full HPACK; the decoder post compares only against nginx. No CPU model or compiler version.
- The 2.37-5.77x claim is against a 2016 nghttp2 encoder; nghttp2 committed faster Huffman encoding and decoding five days after the 2019 post and changed decoding again in 2025, and nobody has re-run it. Against ls-hpack's own byte-at-a-time encoder the two-byte table gains only 1.02-2.14x, nothing under 14 bytes. Default build carries 768 KB of read-only tables. The latest tag v2.3.5 (what Bun pins) still accepts over-long EOS padding (#24) and has UBSan-found undefined behaviour (#26), fixed only on master. v2.3.4 and earlier stripped trailing whitespace from header names (#22). A plain cmake build is -O0 with ASan. No independent numbers.

## Caveats and trade-offs

The only numbers are first-party (LiteSpeed blog, 2019) and cover the HPACK Huffman encoder component only, not full HPACK encode/decode against nghttp2's HPACK API. Each project's code was extracted into standalone C files, and the nghttp2 copy is a 2019 revision (0e1d0400d86a), so current nghttp2 may differ. No CPU model or compiler version is stated. The litespeedtech/benchmarks repo has no license file (the benchmark harness only; ls-hpack itself is MIT). The decoder benchmark compares only against nginx's decoder, not nghttp2's. Bun's adoption comment gives no numbers.

depends on xxhash at runtime; library itself ships no benchmark suite or numbers, so the speed claim is entirely third-party and unverified from ls-hpack's own repo

## Maintenance

Actively maintained by LiteSpeed: the last commits (2026-09-13) fix UB and RFC 7541 §5.2 padding handling, though the last tag, v2.3.5 (2026-05-24), predates them. MIT-licensed, and two .c files plus bundled xxHash make it easy to vendor at a pinned commit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D. LiteSpeed's own 'Fast Huffman Encoder' post (2019-10-03) publishes median timings of ls-hpack's HPACK Huffman encoder against nghttp2's, nginx's and h2o's. The code is public in litespeedtech/benchmarks/huffman-encoder (comp-enc driver, bench.pl, Makefile CFLAGS -O3 -DNDEBUG -g0), but the post gives no CPU model and no compiler version, so it is first-party C, not A.
- **Verifier notes:** benchmark_url was null. A brief search of LiteSpeed's blog and repos found real numbers against nghttp2 (the Huffman encoder post plus its public harness in litespeedtech/benchmarks), so benchmark_url is corrected and the tier goes from D to C. page_compares_against_baseline and numbers_found_on_page refer to that corrected URL. The record's 'metric: other' could reasonably become 'throughput' (time for a fixed iteration count), but metric is not a correctable field.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/litespeedtech/ls-hpack>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/README.md>
  - <https://github.com/oven-sh/bun/blob/main/scripts/build/deps/lshpack.ts>
  - <https://github.com/litespeedtech/benchmarks>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-encoder/README.txt>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-encoder/Makefile>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-encoder/bench.pl>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-decoder/README.txt>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-decoder/Makefile>
  - <https://blog.litespeedtech.com/?s=huffman>
  - <https://blog.litespeedtech.com/2019/10/03/fast-huffman-encoder/>
  - <https://blog.litespeedtech.com/2019/09/16/fast-huffman-decoder/>
  - <https://github.com/litespeedtech/lsquic/blob/master/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/litespeedtech/ls-hpack>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/README.md>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/lshpack.h>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/lsxpack_header.h>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/lshpack.c>
  - <https://raw.githubusercontent.com/litespeedtech/ls-hpack/master/huff-tables.h>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/CMakeLists.txt>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/test/CMakeLists.txt>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/.travis.yml>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/.cirrus.yml>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/.appveyor.yml>
  - <https://github.com/litespeedtech/ls-hpack/blob/master/bin/find-xxh.c>
  - <https://github.com/litespeedtech/ls-hpack/issues?q=is%3Aissue>
  - <https://github.com/litespeedtech/ls-hpack/pulls?q=is%3Apr>
  - <https://github.com/litespeedtech/ls-hpack/issues/24>
  - <https://github.com/litespeedtech/ls-hpack/issues/22>
  - <https://github.com/litespeedtech/ls-hpack/issues/21>
  - <https://github.com/litespeedtech/ls-hpack/issues/14>
  - <https://github.com/litespeedtech/ls-hpack/issues/10>
  - <https://github.com/litespeedtech/ls-hpack/pull/23>
  - <https://github.com/litespeedtech/ls-hpack/pull/26>
  - <https://github.com/litespeedtech/ls-hpack/pull/27>
  - <https://github.com/litespeedtech/ls-hpack/commits/master>
  - <https://github.com/litespeedtech/ls-hpack/tags>
  - <https://blog.litespeedtech.com/2019/10/03/fast-huffman-encoder/>
  - <https://blog.litespeedtech.com/2019/09/16/fast-huffman-decoder/>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-encoder/README.txt>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-encoder/Makefile>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-encoder/nghttp2.c>
  - <https://github.com/litespeedtech/benchmarks/blob/master/huffman-encoder/comp-enc.c>
  - <https://github.com/litespeedtech/benchmarks>
  - <https://github.com/oven-sh/bun/blob/main/scripts/build/deps/lshpack.ts>
  - <https://github.com/litespeedtech/lsquic/blob/master/.gitmodules>
  - <https://github.com/nghttp2/nghttp2/commits/master/lib/nghttp2_hd_huffman.c>
  - <https://github.com/nghttp2/nghttp2/blob/master/lib/nghttp2_hd_huffman.c>
  - <https://github.com/nghttp2/nghttp2/commit/0d855bfc1ba6>
  - <https://github.com/nghttp2/nghttp2/commit/5d6964cf81aa>
  - <https://github.com/nghttp2/nghttp2/commit/e72f4af5dede>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/litespeedtech/ls-hpack`) · [data/wave5/enrich/raw/github_com_litespeedtech_ls_hpack.json](../../../data/wave5/enrich/raw/github_com_litespeedtech_ls_hpack.json) (enrichment confidence 0.45)

</details>
