# ryg_rans

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `CC0-1.0` · 🔵 finished

> Public-domain reference rANS coders in C/C++ headers; interleaved and SSE 4.1 decoders run 1.6-3.7x the scalar decode.

| | |
|---|---|
| **Beats** | Scalar (non-interleaved) rANS in the same repo (rans_byte, rans64) |
| **Claimed result** | book1, i7-2600K, decode: rans_byte scalar 22.0-23.5 clocks/symbol (137.5-147.1 MiB/s) versus 2-way interleaved 13.7-14.2 (227.2-236.2 MB/s); rans64 scalar 18.5-19.6 (165.0-174.6 MiB/s) versus interleaved 10.6-11.2 (287.7-305.7 MB/s); rans_word_sse41 8-way decode 5.9-6.2 clocks/symbol (520.1-550.8 MB/s). The SIMD decoder is roughly 3.7x rans_byte scalar decode (derived from page data). |
| **Workload** | Encode and decode of book1 (about 770 KB, order-0 static model) with rans_byte and rans64, scalar versus 2-way interleaved versus 8-way SSE 4.1 SIMD decoder. |
| **Metric** | throughput |
| **Hardware** | Sandy Bridge i7-2600K |
| **Adoption** | 371 stars; widely referenced reference rANS implementation |
| **Last commit** | 2018-11-25 |
| **Links** | [repository](https://github.com/rygorous/ryg_rans) · [benchmark](https://raw.githubusercontent.com/rygorous/ryg_rans/master/README) |

## Verdict

On book1 (order-0 static model, 14-bit probabilities for rans_byte) on a Sandy Bridge i7-2600K, the author's README shows decode at 22.0-23.5 clocks/symbol for scalar rans_byte, 13.7-14.2 for 2-way interleaved rans_byte, 10.6-11.2 for interleaved rans64 and 5.9-6.2 (520-551 MB/s) for the 8-way SSE 4.1 decoder, about 3.7x scalar rans_byte (derived from page data). The baseline is the author's own scalar rANS; compiler and flags are not stated and the author calls the setup 'not great' on a short file.

## Use it when

- You are writing your own compressor and want a small, readable, CC0 rANS core to copy and adapt rather than a full library
- Static (per-block) order-0 or context-model probabilities where you can precompute encoder reciprocals and a decode slot table
- Decode speed matters more than encode speed and you can split data into 2, 4 or 8 independent streams (interleaved or SIMD decode)
- 64-bit x86 targets where rans64 gives near-entropy precision with 32-bit word output
- Learning or teaching rANS: the headers carry long comments explaining the math and the reciprocal trick

## Skip it when

- You need a drop-in compressor or a stable file format: the author states the code is 'not intended to be industrial strength' and only illustrates the idea
- Peak throughput on modern AVX2/AVX-512 or NEON CPUs: the 16-way AVX2 version promised in the README never landed, and later siblings (hypersonic-rANS, htscodecs, rans_static) are several times faster
- Non-x86 SIMD: rans_word_sse41.h requires SSE 4.1 and platform.h includes x86intrin.h; NEON support was requested in issue #6 and not added
- Portable bitstreams across endianness with rans64 (README says its output is not endian-neutral), or 32-bit targets with rans64 (uses unsigned __int128 / __umulh; issue #8 reports '__int128 is not supported on this target')
- Adaptive (per-symbol updated) models: rANS encodes in reverse, so adaptive coding needs buffering of symbols; an arithmetic or range coder is simpler there

## How it is fast

rANS keeps the coder state in one integer, so several independent coders can share one byte stream with no signalling; interleaving 2 streams lets an out-of-order CPU overlap their dependency chains (the interleaving design is in Giesen's arXiv 1402.3392 paper). The encoders replace division with a precomputed fixed-point reciprocal (Alverson's integer division by reciprocals; 31-bit or 63-bit states so exact reciprocals fit). The SSE 4.1 decoder uses a fully unrolled slot table (freq/bias per slot, scale_bits 12) and branchless renormalization via a movemask-indexed pshufb shuffle table, so four lanes refill 16-bit words without branches. main_alias.cpp adds the alias method for O(1) symbol lookup with table size proportional to the alphabet.

## Compared with alternatives

Pick ryg_rans when you want the smallest, public-domain, well-commented rANS core to embed or study; for raw speed take hypersonic-rANS or htscodecs (AVX2/AVX-512 32-way rANS, several GB/s) or rans_static, and note that sserangecoding already reports beating ryg_rans' SSE decoder (577-619 vs 513-566 MiB/s).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (rans_word_sse41.h needs &lt;smmintrin.h&gt; and the ALIGNSPEC macro from the example platform.h) |
| **Minimum toolchain** | C99 for rans_byte.h and rans64.h (stdint.h); rans_word_sse41.h must be compiled as C++; rans64 needs GCC/Clang unsigned __int128 or MSVC __umulh; examples use MSVC or GCC on Windows or Linux |
| **Platforms** | rans_byte: any 32/64-bit; rans64: 64-bit targets only; rans_word_sse41: x86 with SSE 4.1 |
| **Thread safety** | Stateless inline functions over caller-owned state and buffers; safe across threads with separate state (not documented explicitly) |
| **Drop-in for the baseline** | partial: the scalar and interleaved coders share the same API in rans_byte.h/rans64.h, but the SSE 4.1 decoder uses a different 16-bit-word stream format and needs a matching encoder layout |

## Gotchas

- Encode runs backwards: symbols last-to-first, output pointer starts at the buffer end and moves down; the SIMD renormalizer reads up to 8 bytes past the input end, so pad the buffer or finish with the scalar decoder
- A single-symbol alphabet (freq equal to the full scale) expands output: issue #11 (open) shows 72 bytes of 'a' becoming 148 bytes with rans_word_sse41; reading RansWordEncPut, the renormalization bound overflows to 0 in that case so every symbol emits a 16-bit word. Special-case single-symbol blocks
- The example drivers use a fixed 32 MB output buffer (out_max_size = 32&lt;&lt;20 in main.cpp); issue #10 reports 'bad decoder' and a free() crash on Silesia mozilla (\~133 MB, \~39.8 MB compressed), which exceeds that buffer. Size buffers yourself
- rans_word_sse41 is hard-wired to scale_bits 12 and an 8-bit alphabet; rans_byte asserts scale_bits &lt;= 16 and frequency-1 symbols use a special reciprocal path

## Known shortcomings

- Tier C: README numbers reproduce (rans64 interleaved up to 305.7 MB/s); CC0; last commit 2018-11-25.
- The README says the code is 'not intended to be industrial strength'. Issue #11 open: single-symbol input expands output (72 B to 148 B with rans_word_sse41), and by the enricher's reading the renormalisation bound overflows when a frequency equals the full scale. Issue #10: the example driver's fixed 32 MB output buffer makes Silesia mozilla fail with 'bad decoder' and a free() crash. The promised AVX2 version never shipped, NEON (#6) was never added, and rans64 hits an __int128 error on some targets (#8).

## Caveats and trade-offs

Public domain dedication (no patent grant). No compiler or flags stated; author says the measurement setup is not great and the file is short. Baseline is the same author's scalar rANS, not Huffman. The README mentions a 16-way AVX2 version 'soon' that is not in the repo. Interleaving paper (arXiv 1402.3392) and blog not opened (blocked).

rans_word_sse41 has lower precision than rans_byte/rans64 and needs at least 4 independent streams; rans64 bitstream not endian-neutral and slower on 32-bit; includes alias-method example (main_alias.cpp).

## Maintenance

Finished reference code (last commit 2018-11-25, README dated Feb 2014) with two open issues and no maintainer replies since; CC0 public domain and only three headers, so trivial to vendor and adapt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows first-party clocks/symbol and MiB/s on a Sandy Bridge i7-2600K for scalar versus interleaved versus 8-way SSE 4.1 decode; example programs are public but compiler and flags are not stated and the author says the measurement setup is not great.
- **Verifier notes:** Numbers confirmed in README (rans64 interleaved range extends to 10.6 clocks / 305.7 MB/s, corrected). Public domain (CC0, 'Clarify public domain license'), 371 stars, last commit 2018-11-25 confirmed; baseline is only the author's own scalar rANS, which is a weak but named comparison for a widely referenced reference implementation.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/README>
  - <https://github.com/rygorous/ryg_rans>
  - <https://github.com/rygorous/ryg_rans/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/README>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/LICENSE>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/rans_byte.h>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/rans64.h>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/rans_word_sse41.h>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/platform.h>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/main.cpp>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/main64.cpp>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/main_simd.cpp>
  - <https://raw.githubusercontent.com/rygorous/ryg_rans/master/main_alias.cpp>
  - <https://github.com/rygorous/ryg_rans/issues?q=is%3Aissue>
  - <https://github.com/rygorous/ryg_rans/pulls?q=is%3Apr>
  - <https://github.com/rygorous/ryg_rans/issues/11>
  - <https://github.com/rygorous/ryg_rans/issues/10>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/rygorous/ryg_rans`) · [data/wave9/enrich/raw/github_com_rygorous_ryg_rans.json](../../../data/wave9/enrich/raw/github_com_rygorous_ryg_rans.json) (enrichment confidence 0.85)

</details>
