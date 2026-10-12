# ls-qpack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> LiteSpeed's C QPACK (RFC 9204) codec. On one 2019 trace, its history-gated indexing out-compressed nghttp3 1.3-2.2x.

| | |
|---|---|
| **Beats** | nghttp3 (QPACK encoder compression ratio); nghttp2/nginx Huffman coder (shared HPACK/QPACK Huffman alphabet) |
| **Claimed result** | QPACK compression ratio on fb-resp.qif (Facebook response trace, 4KB dynamic table): ls-qpack 0.16 vs nghttp3 0.21 when risking blocked streams, 0.18 vs 0.39 with no blocked-stream risk (lower=better; roughly 1.3-2.2x more compact, derived from page data). ls-qpack is also best of the six encoders listed (with qthingey, proxygen, f5, quinn). Shared LiteSpeed HPACK/QPACK Huffman coder (2019 posts, same code as ls-hpack): decoder 1.15-1.96x faster than nginx 1.16.1's decoder; encoder 1.11-2.12x faster than nginx and 1.18-3.59x faster than h2o. It was also 2.37-5.77x faster than nghttp2's 2016 encoder (rev 0e1d0400d86a), but nghttp2 replaced that encoder ('Faster huffman encoding', committed 2019-10-12, nine days after the post), so the nghttp2 figure is stale. |
| **Workload** | Huffman encode/decode of four inputs: the string 'LiteSpeed'; a real x-fb-debug header value from the Facebook response QIF; the same value with backslashes inserted to force the slow path; and paragraphs of Jerome K. Jerome's Idle Thoughts. Each loops \~1e6-3.3e8 times, median of 5 runs, with code extracted into litespeedtech/benchmarks. Separately, QPACK compression ratio (compressed bytes / QIF source bytes) on fb-resp.qif from the qpackers/qifs corpus, 4KB table, with and without risking blocked streams. It uses encodings checked into that repo (nghttp3's committed 2019-02-17, ls-qpack's updated through 2019-10-21). |
| **Metric** | throughput |
| **Compiler and flags** | -Wall -DNDEBUG -O3 -g0 (litespeedtech/benchmarks Huffman Makefiles; compiler not named) |
| **Adoption** | 86 stars; used in OpenLiteSpeed, LiteSpeed Web Server and Web ADC |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/litespeedtech/ls-qpack) · [benchmark](https://blog.litespeedtech.com/2021/04/05/qpack-mnemonic-technique/) |

## Verdict

There are two first-party measurements. The first compares file sizes of encodings committed to qpackers/qifs for the Facebook response trace (351,937 bytes, 4 KB table): ls-qpack's Oct-2019 output was 0.16 of source bytes vs 0.21 for nghttp3's Feb-2019 draft-era output with blocked streams allowed, and 0.18 vs 0.39 without; this measures bytes, not speed, and was never re-run. The second times the Huffman coder that ls-qpack shares with ls-hpack, as standalone C built -O3 -DNDEBUG (median of 5; compiler and CPU not stated): the decoder was 1.15-1.96x faster than nginx 1.16.1, and the encoder was 1.11-2.12x faster than nginx, 1.18-3.59x faster than h2o and 2.37-5.77x faster than a 2016 nghttp2 encoder that nghttp2 replaced in Oct 2019.

## Use it when

- You are adding HTTP/3 in C/C++ on a QUIC transport that has no QPACK of its own. ls-qpack is the QPACK layer inside lsquic, and msh3 uses it on top of MsQuic.
- Header bytes on the wire matter more than codec CPU, for example on a server answering many requests per connection with repetitive but non-standard headers. With a 4 KB table on the Facebook response trace, it produced 0.16-0.18 of the source bytes, the best of the six encoders LiteSpeed compared.
- You run with max_risked_streams=0 (no blocked streams). In that mode the 2021 comparison showed the widest gap: 0.18 vs 0.39 for nghttp3's 2019 encoding and 0.25-0.61 for the others.
- You bridge HTTP/3 to HTTP/1.1. LSQPACK_DEC_OPT_HTTP1X writes 'name: value\r\n' straight into your buffer, and LSQPACK_DEC_OPT_HASH_NAME and LSQPACK_DEC_OPT_HASH_NAMEVAL fill in XXH32 hashes the caller can reuse.
- You must feed header blocks as they arrive without buffering the whole HEADERS frame. The decoder is streaming and tracks dynamic-table IDs modulo 2\*MaxEntries, so no counter can overflow.

## Skip it when

- You need evidence that it uses less CPU than nghttp3. No runtime benchmark of the QPACK codec exists. The Huffman timings compare against nginx, h2o and a 2016 nghttp2 encoder, and nghttp3 got its own table-driven Huffman encoder and decoder on 2019-10-04/05 (tuned again 2025-11-02), which were never compared.
- You need strict RFC 9204 conformance testing. The decoder accepts Sign=1 when Required Insert Count is 0, which §4.5.1.2 forbids (#90, open). The maintainer keeps this on purpose because the MUST was added during AUTH48.
- Your header names or values can exceed 64 KB. lsxpack_strlen_t is uint16 unless you build with LSXPACK_MAX_STRLEN=UINT32_MAX. Before v2.6.0, a header over 65535 bytes caused an infinite loop at 100% CPU (#69).
- L2 cache or binary size is tight. The default build carries the same 768 KB of read-only Huffman tables as ls-hpack. CMake MinSizeRel sets LS_QPACK_USE_LARGE_TABLES=0 and falls back to the slower small-table paths.
- You would use it through a pinned wrapper on untrusted input. pylsqpack and msh3 both pin v2.6.2 (1e9c5b8e59). That version predates the v2.6.3 hardening, the v2.6.5 fix for use-after-free #87 (introduced by baf1164 in Oct 2020) and the v2.6.6 double-free fix. The v2.6.3 hardening covers Huffman padding over 7 bits, WINR/WONR capacity checks, a shift UB, Header Ack for an in-progress block and ICI 32-bit overflow.

## How it is fast

The compression edge comes from the encoder's 'mnemonic' indexing. The encoder keeps a FIFO ring of 32-bit XXH32 hashes of recently seen names and name+value pairs, and it inserts a field into the dynamic table only if that field was seen recently. The ring is resized to follow a running average of dynamic-table entries, and indexing is skipped when two literals would push the cumulative output/input ratio above 0.95. The speed claims come from the Huffman coder that ls-qpack shares with ls-hpack. It has a 65,536-entry two-byte encode table (hencs, 512 KB) and a decode table indexed by 16 bits (hdecs, 256 KB) that emits 1-3 bytes per lookup, with fallback to the byte-at-a-time encoder and the 4-bit state-machine decoder. Static-table matching uses seeded XXH32 into 512-slot arrays, and dynamic-table matching uses chained hash buckets by name and by name+value.

## Compared with alternatives

None of the catalogued siblings is a standalone QPACK codec. LSQUIC already embeds ls-qpack, ngtcp2 normally pairs with nghttp3, and the rest are transports or DNS servers. Pick ls-qpack when your QUIC stack needs a QPACK layer and smaller header bytes on the wire matter. On ngtcp2+nghttp3, the only case for switching is the 2019-era compression-ratio data, since no CPU comparison exists.

## Integration

| | |
|---|---|
| **Form** | static lib by default via CMake (BUILD_SHARED_LIBS=ON for a shared lib); installs the ls-qpack::ls-qpack CMake export and lsqpack.pc. Also works as a source-drop: lsqpack.c + huff-tables.h + lsqpack.h + lsxpack_header.h + xxhash. |
| **Dependencies** | xxHash, bundled in deps/xxhash and on by default (LSQPACK_XXH=ON), or external through the xxHash CMake config or pkg-config libxxhash. &lt;sys/queue.h&gt; (a wincompat copy is used on Windows/Emscripten). &lt;math.h&gt; (fabsf, round); lsqpack.pc lists no -lm. Tools and tests need getopt on Windows. |
| **Minimum toolchain** | C99 ('vanilla C99' per README). CMakeLists declares cmake_minimum_required 3.1, which CMake 4.x rejects unless you pass -DCMAKE_POLICY_VERSION_MINIMUM=3.5. AppVeyor pins CMake 3.31.7 with VS 2017. |
| **Platforms** | Linux, macOS, FreeBSD/OpenBSD/NetBSD, Windows (MSVC), MinGW and Emscripten (#72). s390x big-endian was fixed in 2025 (#76, #77). Portable scalar C with no SIMD, with 32- and 64-bit code paths. On Windows and on any OS outside the endian #if chain, __BYTE_ORDER is undefined and the little-endian Huffman table layout is used. On v2.7.0 only AppVeyor (Windows) reports CI status; .travis.yml (xenial, gcc-8) and .cirrus.yml (FreeBSD 13.3) exist but posted no status. |
| **Thread safety** | Not documented. All mutable state is in caller-owned lsqpack_enc/lsqpack_dec structs, and lsqpack.c has no non-const file-scope globals, so separate instances are independent. Sharing one instance across threads needs external locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- Pass lsqpack_dec_init the same table capacity you advertise in SETTINGS_QPACK_MAX_TABLE_CAPACITY, because MaxEntries and ID mapping derive from it. A 2022 change that tolerated a mismatch (#44) was reverted in v2.6.3 as invalid.
- Do not free or modify the lsxpack_header inside dhi_process_header on versions before v2.6.5. Until then the library read name_len/val_len after the callback, a heap use-after-free (#87) that the still-open #38 described in 2021. OpenLiteSpeed did not free there, so the bug went unnoticed.
- v2.7.0 changed lsqpack_enc_cancel_header: it now cancels header blocks that use the dynamic table. Encoder-stream bytes already produced must still be sent. Entries inserted for a cancelled block can pin the table if the peer never sends Insert Count Increment.
- The CMake option LSQPACK_BIN defaults ON and builds and installs four tools: interop-encode, interop-decode, fuzz-decode and encode-int. On Windows this fails with FATAL_ERROR without getopt.h, so pass -DLSQPACK_BIN=OFF. No CMAKE_BUILD_TYPE is set by default. LSXPACK_MAX_STRLEN changes struct lsxpack_header's layout, so build the library and its callers with the same value.

## Known shortcomings

- The speed evidence is the Huffman coder shared with ls-hpack, whose 2.37-5.77x encoder win is against 2016 nghttp2 code that nghttp2 rewrote nine days after the 2019 post (stale). The ls-qpack-specific evidence is a compression ratio vs nghttp3 (0.16-0.18 vs 0.21-0.39), not speed, and the nghttp3 encodings date from 2019-02 and were never re-run. The nginx Huffman comparisons still hold. No compiler named (Makefiles use -O3 -DNDEBUG).
- No runtime benchmark of the QPACK codec against nghttp3 exists; nghttp3 got its own table-driven Huffman coder a day after LiteSpeed's 2019 post and tuned decoding again in 2025. The compression-ratio figures are 2019 draft-era encodings (4 KB table, one trace), never re-run, measuring bytes not speed. The decoder deliberately accepts Sign=1 with Required Insert Count 0, which RFC 9204 forbids (#90). Recent security fixes: heap use-after-free present Oct 2020 to v2.6.5 (#87), double-free fixed v2.6.6, decoder hardening in v2.6.3, infinite loop on &gt;65535-byte headers fixed v2.6.0 (#69); pylsqpack (aioquic) and msh3 still pin v2.6.2. Integration hazards: decoder capacity must match SETTINGS since v2.6.3, lsqpack_enc_cancel_header semantics changed in v2.7.0, fields over 64 KB need a rebuild with LSXPACK_MAX_STRLEN. 768 KB of Huffman tables; cmake_minimum_required(3.1) fails on CMake 4.x without a policy override; README still calls QPACK a draft. Unlike ls-hpack, the Huffman padding/UB fixes are in the tagged v2.6.3+.

## Caveats and trade-offs

All evidence is first-party (LiteSpeed blog). The QPACK comparison measures bytes on the wire, not runtime speed. Its nghttp3 baseline is a draft-era encoding committed to qpackers/qifs on 2019-02-17, about 2 years before the 2021 post and never re-run (nghttp3's lib/nghttp3_qpack.c had \~68 commits between then and the post), while ls-qpack's encodings date from Oct 2019. The Huffman speed numbers belong to the shared LiteSpeed coder: ls-hpack is already catalogued with them, and ls-qpack's lsqpack.c carries the same hencs/hdecs fast-path tables. The 2.37-5.77x vs nghttp2 figure is against a 2016 nghttp2 encoder that nghttp2 replaced on 2019-10-12, so it must not be cited as current. The nginx comparisons still hold: nginx's Huffman code has only been moved and had its logging adjusted since 1.16.1. The bench code is public with -O3, but no compiler or CPU model is stated, so tier C. Benchmark pages: 2021 QPACK post (benchmark_url), https://blog.litespeedtech.com/2019/10/03/fast-huffman-encoder/ and https://blog.litespeedtech.com/2019/09/16/fast-huffman-decoder/.

Vanilla C99 with a lower-level API (struct lsxpack_header); needs wrapping for higher-level languages (Go/Python/Rust/TS/Ruby wrappers exist but are separately maintained third-party projects).

## Maintenance

Actively maintained: five releases from v2.6.3 (2026-06-15) to v2.7.0 (2026-07-30). Unlike ls-hpack, the Huffman-padding and shift-UB fixes are in a tagged release, and lsquic pins v2.7.0. MIT-licensed; one .c file, a 4.4 MB generated table header and bundled xxHash make it easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party LiteSpeed blog numbers. The Huffman bench code is public (litespeedtech/benchmarks huffman-decoder/ and huffman-encoder/, Makefile CFLAGS -O3 -DNDEBUG) but no compiler or CPU model is given, and the QPACK ratios are just file sizes of qpackers/qifs encodings from different years that were never re-run. That is C.
- **Verifier notes:** Every claimed number checks out: encoder figures on the 2019-10-03 post, decoder figures on the 2019-09-16 post, and ratios on the 2021-04-05 post (they also match the qifs file sizes: 57632 and 64477 vs 75201 and 136396 over 351937 bytes). I rated it 'downgrade' at an unchanged tier C because the headline nghttp2 Huffman win is stale and the nghttp3 ratio baseline is a Feb-2019 encoder. benchmark_url now points to the ls-qpack-specific QPACK post. That post measures compression ratio, so the metric field ('throughput') does not match it, and the only runtime-speed evidence is the Huffman coder shared with ls-hpack.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://blog.litespeedtech.com/2019/10/03/fast-huffman-encoder/>
  - <https://blog.litespeedtech.com/2019/09/16/fast-huffman-decoder/>
  - <https://blog.litespeedtech.com/2021/04/05/qpack-mnemonic-technique/>
  - <https://github.com/litespeedtech/ls-qpack>
  - <https://raw.githubusercontent.com/litespeedtech/ls-qpack/master/lsqpack.c>
  - <https://github.com/litespeedtech/benchmarks>
  - <https://github.com/qpackers/qifs>
  - <https://github.com/nghttp2/nghttp2>
  - <https://github.com/nginx/nginx>
  - <https://github.com/ngtcp2/nghttp3>
- **Sources the enricher read:**
  - <https://github.com/litespeedtech/ls-qpack>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/README.md>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/lsqpack.h>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/lsxpack_header.h>
  - <https://raw.githubusercontent.com/litespeedtech/ls-qpack/master/lsqpack.c>
  - <https://raw.githubusercontent.com/litespeedtech/ls-qpack/master/huff-tables.h>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/CMakeLists.txt>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/CHANGELOG>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/MAINT>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/lsqpack.pc.in>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/.travis.yml>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/.cirrus.yml>
  - <https://github.com/litespeedtech/ls-qpack/blob/master/.appveyor.yml>
  - <https://github.com/litespeedtech/ls-qpack/tags>
  - <https://github.com/litespeedtech/ls-qpack/releases>
  - <https://github.com/litespeedtech/ls-qpack/commits/master>
  - <https://github.com/litespeedtech/ls-qpack/commit/baf116471eb7d14f1763c75ed9582edc13e5d040>
  - <https://github.com/litespeedtech/ls-qpack/commit/6f712f54d9>
  - <https://github.com/litespeedtech/ls-qpack/issues?q=is%3Aissue>
  - <https://github.com/litespeedtech/ls-qpack/pulls?q=is%3Apr>
  - <https://github.com/litespeedtech/ls-qpack/issues/90>
  - <https://github.com/litespeedtech/ls-qpack/issues/87>
  - <https://github.com/litespeedtech/ls-qpack/issues/82>
  - <https://github.com/litespeedtech/ls-qpack/issues/77>
  - <https://github.com/litespeedtech/ls-qpack/issues/74>
  - <https://github.com/litespeedtech/ls-qpack/issues/69>
  - <https://github.com/litespeedtech/ls-qpack/issues/51>
  - <https://github.com/litespeedtech/ls-qpack/issues/47>
  - <https://github.com/litespeedtech/ls-qpack/issues/44>
  - <https://github.com/litespeedtech/ls-qpack/issues/38>
  - <https://github.com/litespeedtech/ls-qpack/pull/83>
  - <https://blog.litespeedtech.com/2021/04/05/qpack-mnemonic-technique/>
  - <https://blog.litespeedtech.com/2019/10/03/fast-huffman-encoder/>
  - <https://blog.litespeedtech.com/2019/09/16/fast-huffman-decoder/>
  - <https://github.com/qpackers/qifs>
  - <https://github.com/nghttp2/nghttp2/commits/master/lib/nghttp2_hd_huffman.c>
  - <https://github.com/ngtcp2/nghttp3/commits/main/lib/nghttp3_qpack_huffman.c>
  - <https://github.com/litespeedtech/lsquic/blob/master/.gitmodules>
  - <https://github.com/litespeedtech/lsquic/tree/master/src/liblsquic>
  - <https://github.com/aiortc/pylsqpack>
  - <https://github.com/aiortc/pylsqpack/tree/main/vendor>
  - <https://github.com/aiortc/aioquic/blob/main/pyproject.toml>
  - <https://github.com/nibanks/msh3>
  - <https://cmake.org/cmake/help/latest/release/4.0.html>
  - <https://hn.algolia.com/api/v1/search?query=ls-qpack>
  - <https://export.arxiv.org/api/query?search_query=all:QPACK>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/litespeedtech/ls-qpack`) · [data/wave5/enrich/raw/github_com_litespeedtech_ls_qpack.json](../../../data/wave5/enrich/raw/github_com_litespeedtech_ls_qpack.json) (enrichment confidence 0.5)

</details>
