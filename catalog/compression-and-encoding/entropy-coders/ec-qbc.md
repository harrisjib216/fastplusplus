# qbc (Quick adaptive Binary Arithmetic Coder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Tiny adaptive order-0 binary arithmetic coder for short strings, pitched as a replacement for Quake 3's adaptive Huffman Huff_ functions.

| | |
|---|---|
| **Beats** | Quake 3 / ioquake3 adaptive Huffman Huff_Compress()/Huff_Decompress() (\~50k memory) |
| **Claimed result** | encode/decode speed about 20% faster; compression rate about 10% better; memory more than 50 times lower (&lt;1k vs \~50k) |
| **Workload** | Compression of connect-command infostrings with a 0-order adaptive binary model, versus the engine's Huff_ functions; no corpus or sizes stated. |
| **Metric** | throughput |
| **Adoption** | 2 stars |
| **Last commit** | 2022-06-02 |
| **Links** | [repository](https://github.com/ec-/qbc) · [benchmark](https://github.com/ec-/qbc) |

## Verdict

The only evidence is three README bullets by the author comparing against Quake 3's adaptive Huffman Huff_ functions on connect infostrings: about 10% smaller output, about 20% faster encode/decode, and under 1 KB vs about 50 KB of memory. No corpus, timings, compiler or CPU are given and the repo contains no benchmark; the memory figure matches the code (256-byte probability array plus a 512-byte table).

## Use it when

- Compressing short text records or network packets (hundreds of bytes) where an adaptive model with no transmitted table beats static Huffman and memory must stay under 1 KB.
- Replacing Quake 3 / ioquake3 Huff_Compress()/Huff_Decompress() in a mod or engine fork that controls both client and server.
- Embedded or per-connection codec state where a \~50 KB adaptive Huffman context per stream is too expensive.
- As a compact teaching example of a binary adaptive range coder (about 250 lines, MIT).

## Skip it when

- Bulk data or throughput-critical paths: bit-at-a-time coding with a renormalization branch is far from table-driven Huffman, tANS or interleaved rANS decoders, and no MB/s figure is published.
- Interoperating with existing Quake 3 clients or servers, or any other format; the stream is new and undocumented.
- Data that is not text-like or needs higher-order context: the model is order-0 only and resets per init().
- Hostile input fed through the C API or decode_string with a buffer sized exactly to len (see gotchas).
- Any claim-sensitive decision: the 20% speed and 10% ratio figures have no benchmark code, corpus or hardware behind them.

## How it is fast

Each byte is coded as 8 binary decisions through a 255-node bit-tree context (an adaptive order-0 byte model), each with an 8-bit probability updated by a 2x256 lookup table instead of arithmetic. The coder is a carryless 32-bit low/high range coder: the interval update is written as range[bit] = split + (bit^1) to avoid a branch, and one byte is shifted out whenever low and high agree in their top 20 bits. State is 256 probability bytes plus a 512-byte shared table, so it stays in L1, whereas adaptive Huffman must rebuild its tree as it goes.

## Compared with alternatives

FSE/Huff0, FPC, TurboRC and the rANS coders target large buffers with static or block-adaptive models and reach hundreds of MB/s to GB/s; qbc only makes sense for very short messages where shipping a frequency table would cost more than the payload and per-stream memory must be under 1 KB. For anything bigger, TurboRC's adaptive range coders or Huff0 are the better-supported choice.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (memset from &lt;string.h&gt;, which the files do not include themselves) |
| **Minimum toolchain** | not documented; plain C (qbc.c) or C++98-style class (qbc.cpp) |
| **Platforms** | any with 32-bit unsigned int |
| **Thread safety** | Per-instance state; one qbc / bitcodec_t per stream. The shared probability-update table is read-only. |
| **Drop-in for the baseline** | partial: function-for-function replacement of Huff_Compress/Huff_Decompress at the call site, but the wire format changes, so both peers must switch |

## Gotchas

- qbc.c's bc_encode_byte takes 'unsigned char value' and signals overrun with 'value = -1; break;', so it returns 255 instead of -1; bc_encode_string never sees the error, keeps going after the output buffer is full, and if overrun hits while coding the terminating NUL it continues reading past the end of the source string.
- decode_string / bc_decode_string decode up to len bytes and then always write a terminating NUL at str[len], so the buffer must be len+1 bytes; the repo's own test passes sizeof(buf2) as len, a one-byte overflow if a corrupted or crafted stream decodes 1024 non-zero bytes.
- encode_flush / bc_encode_flush stops silently when the output buffer runs out and still returns 0, so a truncated stream is not reported; the decoder then stops early and returns a shortened string without an error.
- test.cpp declares 'void main', which C++ compilers reject; test.c and test.cpp also print strlen with %i. The tests only round-trip one infostring and time nothing.

## Known shortcomings

- Baseline is the Quake 3 Huff_ functions, not a listed coder. No timing code in the repo; test.c/test.cpp only round-trip one infostring. 2 stars, last commit 2022-06-02, abandoned.
- bc_encode_byte sets value=-1 on an unsigned char and returns 255, so overrun goes undetected and encoding can read past the source string's NUL. decode_string writes the NUL at str[len], and the repo's own test passes sizeof(buf), a 1-byte overflow on crafted input. encode_flush truncates silently and returns 0. test.cpp has 'void main' and does not compile as C++. No benchmark exists for the 20%/10% claims; the memory claim matches the code.

## Caveats and trade-offs

First-party README claim in three bullet points. No benchmark code, corpus, compiler, flags or CPU stated; test.c/test.cpp are round-trip correctness checks on a single Quake 3 connect infostring with no timing and no Huff_ baseline. Baseline is a game-engine adaptive Huffman, not a general incumbent such as zlib Huffman or Huff0. Output stream is not compatible with the existing Huffman format. Repo has only 3 commits (May 29 - June 2, 2022), last over 3 years ago. Repo holds both qbc.c and qbc.cpp; language shown as C++ with a C version.

Not compatible with existing Huffman bitstreams. 8-bit probabilities with 32-bit carryless arithmetic; under 1 KB for a 0-order model. Tiny scope (adaptive order-0 only).

## Maintenance

Abandoned after three commits in May-June 2022, MIT-licensed and about 250 lines, so easy to vendor, but fix the C overrun bug and the decode_string terminator before using it on network input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README states three first-party comparisons against the Quake 3 Huff_Compress()/Huff_Decompress() functions (about 10% better compression, about 20% faster encode/decode, under 1k vs \~50k memory) with no benchmark code, corpus, compiler, flags or CPU. The repo's test.c/test.cpp only round-trip one sample connect infostring and print the encoded size; they do not time anything or call Huff_ functions.
- **Verifier notes:** Claim text matches the README exactly. License MIT confirmed (LICENSE file, Copyright 2022 Eugene C.), 2 stars, 0 forks, not a fork, not archived. Last commit 2022-06-02 is more than 3 years before 2026-10-01, so maintenance_status corrected from stale to abandoned.
- **Fields the verifier corrected:** `maintenance_status`, `caveats`
- **Shortcomings recorded by:** first-party claim
- **Pages the verifier opened:**
  - <https://github.com/ec-/qbc>
  - <https://github.com/ec-/qbc/commits>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/README.md>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/qbc.c>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/qbc.cpp>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/test.c>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/test.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/README.md>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/qbc.c>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/qbc.cpp>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/test.c>
  - <https://raw.githubusercontent.com/ec-/qbc/HEAD/test.cpp>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ec-/qbc`) · [data/wave9/enrich/raw/github_com_ec_qbc.json](../../../data/wave9/enrich/raw/github_com_ec_qbc.json) (enrichment confidence 0.75)

</details>
