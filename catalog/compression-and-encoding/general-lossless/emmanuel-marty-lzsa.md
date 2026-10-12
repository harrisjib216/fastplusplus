# LZSA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🔴 abandoned

> Byte-aligned LZ formats with an optimal packer: better ratio than LZ4_HC, and decompression as fast as LZ4 on 8-bit CPUs.

| | |
|---|---|
| **Beats** | LZ4_HC (lz4) |
| **Claimed result** | README table 'Decompression speed vs. LZ4' (ZX Spectrum/C64 file set): LZSA1 90%, LZSA2 75%, LZ4_HC -19 -B4 -BD 100%, i.e. slower than LZ4 at default settings. The README's pareto_graph.png (ZX Spectrum, decompression rate in bytes per frame) plots the fastest LZSA1 variants (LZSA1-m4, LZSA1-m5) at about 2,400-2,570 bytes/frame against about 2,170-2,360 for the two LZ4 decompressors, roughly 9% faster at the top end (derived from page data, read off the graph, approximate), while also compressing better. Compression ratio beats LZ4_HC -19 on every listed corpus, e.g. Silesia LZSA1 34.78% and LZSA2 32.52% versus LZ4_HC 36.47%; enwik9 35.54% / 33.49% versus 37.18%. The README also says the compressor is about 2x slower than LZ4_HC. |
| **Workload** | Compression ratio and relative decompression speed on a ZX Spectrum/C64 file set (1,289,127 bytes) plus Canterbury, Silesia, Calgary, Large and enwik9 corpora; speed measured on 8-bit Z80/6502 decompressors. |
| **Metric** | other |
| **Hardware** | 8-bit micros (Z80, 6502, 8088); host CPU not stated |
| **Adoption** | 261 stars |
| **Last commit** | 2023-02-27 |
| **Links** | [repository](https://github.com/emmanuel-marty/lzsa) · [benchmark](https://github.com/emmanuel-marty/lzsa) |

## Verdict

First-party README only: on a 1,289,127-byte ZX Spectrum/C64 file set and on Canterbury, Silesia, Calgary, Large and enwik9, LZSA1 and LZSA2 compress smaller than LZ4_HC -19 -B4 -BD (enwik9 35.54% and 33.49% vs 37.18%). Relative decompression speed (LZSA1 90%, LZSA2 75% of LZ4) and the Pareto graph (fastest LZSA1 modes about 9% faster than LZ4 on Z80, read off the graph) are measured on ZX Spectrum 8-bit depackers. No host CPU, compiler, flags or harness is given.

## Use it when

- Compressing assets for Z80, 6502, 8088 or 6809 machines (demos, ROMs, retro games), where a ready-made assembly depacker from 67 bytes upward exists.
- Embedded targets with small RAM and a 64 KB window, where you want a better ratio than LZ4_HC (e.g. Silesia 34.78% LZSA1 and 32.52% LZSA2 vs 36.47%) and a tiny decoder.
- Pack-once, decode-many data where a slower, optimal compressor is acceptable.
- Replacing ZX7 with LZSA2: the README reports better ratio (52.49% vs 53.30%) and faster decode (75% vs 47.73% of LZ4's speed) on its ZX Spectrum/C64 set.

## Skip it when

- Speed on modern x86 or Arm: no host throughput numbers are published, and the README's own table puts LZSA1 at 90% and LZSA2 at 75% of LZ4's decompression speed. Use LZ4, LZSSE or Lizard there.
- Fast compression: the packer is about 2x slower than LZ4_HC (suffix-array build per block), so it does not suit online or streaming compression.
- Interop with existing LZ4 or zlib tooling: LZSA is its own format.
- Untrusted input in production without fuzzing: the C decoder has no fuzz harness or sanitizer CI, and see the LZSA2 over-read under gotchas.
- Projects needing an active upstream: last commit 2023-02-27. Open issue #69 (6502 backward raw-block depacker runs past the data) is unanswered.

## How it is fast

The compressor finds matches with a suffix array (libdivsufsort plus a wimlib-derived interval match finder) and parses optimally, picking the sequence of commands with the smallest output that still decodes fast. The formats avoid bit-packing in the hot path: LZSA1 is byte-aligned with 8-bit short offsets and a 3-byte minimum match, and LZSA2 adds nibble-coded lengths, 5/9/13/16-bit offsets and rep-matches, so an 8-bit CPU decodes without 16-bit arithmetic. The host C decoder uses fixed 8/16/18-byte memcpy fast paths with bounds-checked slow paths.

## Compared with alternatives

Pick LZSA over LZ4 or lz4ultra (same author, LZ4 format) when you control the decoder on an 8-bit or tiny embedded target and want 3-6% better ratio than LZ4_HC at similar decode cost. On modern CPUs prefer LZ4, LZSSE or Lizard for decode speed. For ratio-first 8-bit packing, BriefLZ or blz4 are alternatives with simpler formats.

## Integration

| | |
|---|---|
| **Form** | source-drop (C files plus bundled libdivsufsort); Makefile builds the lzsa CLI, and there is no install target or packaged library |
| **Dependencies** | none external (libdivsufsort, MIT, is vendored under src/libdivsufsort) |
| **Minimum toolchain** | C99-ish C compiler (Makefile defaults to clang -O3); issue #45 reported and closed gcc C++11 incompatibilities |
| **Platforms** | Packer: any platform with a C compiler. Decompressors: portable C plus assembly for Z80, 6502, 8088, 6809, 6309; external i8080, PDP-11, 68000 and Game Boy ports. |
| **Thread safety** | not documented (state lives in per-call compression/decompression contexts) |
| **Drop-in for the baseline** | no |

## Gotchas

- Possible 1-byte input over-read on malformed LZSA2 data (read in source this session, not reproduced): in src/expand_block_v2.c, the 13-bit-offset case (offset mode 0x80) calls lzsa_get_nibble_v2, which may consume the last block byte, then reads \*pInBlock++ with no bounds check. In raw-block mode the block ends at the caller's buffer end. LZSA1 (expand_block_v1.c) checks two bytes before reading the offset.
- lzsa_decompress_inmem and lzsa_get_max_decompressed_size_inmem return size_t but signal errors with -1, so compare against (size_t)-1, not &lt; 0. Size the output buffer with lzsa_get_max_decompressed_size_inmem (64 KB per block).
- Issue #65 (closed): a segfault on every input when compressing, bisected to commit 5e404e9 (2021-06-04), reported with clang 11 on Debian 11. No later commit message names the fix, so test the packer on your toolchain before relying on it.
- Licensing is split: the code is Zlib, but src/matchfinder.c is CC0 (wimlib-derived, no patent grant) and the vendored libdivsufsort is MIT.

## Known shortcomings

- No speed win on modern hosts: the README table reads slower than LZ4 (LZSA1 90%, LZSA2 75% of LZ4 decode); only Z80 decompression is about 9% faster (read off pareto_graph.png, approximate). Ratio beats LZ4_HC on all corpora; the compressor is about 2x slower than LZ4_HC. Abandoned, last commit 2023-02-27. Zlib licence plus CC0 matchfinder.c.
- Read in source, not reproduced: src/expand_block_v2.c's 13-bit-offset case (0x80) reads \*pInBlock++ unchecked after the nibble fetch, a possible 1-byte over-read on malformed LZSA2 input; the LZSA1 path is checked. The in-memory API returns size_t with -1 on error. Issue #65 compress segfault closed with no fix commit named; #69 6502 backward depacker open. No fuzz harness. Licence is Zlib plus CC0 matchfinder.c plus vendored MIT libdivsufsort.

## Caveats and trade-offs

The speed win exists only for 8-bit decompressors (Z80 graph) and only for the speed-tuned LZSA1 modes; the README's own table reads slower than LZ4 on decompression (90% and 75%), and the compressor is about 2x slower than LZ4_HC, so on modern CPUs this is a ratio win, not a speed win. No host CPU, compiler, flags or benchmark harness; the graph values are approximate readings. Licensing is mixed but all OSI/CC0: Zlib for the code, CC0 for src/matchfinder.c (no patent grant for that file). Last commit 2023-02-27, over 3 years old.

Targets 8-bit decompressors in assembly; the host-side packer is portable C (matchfinder.c is CC0 from wimlib) but compression is about 2x slower than LZ4_HC. Not a modern x86/Arm speed play.

## Maintenance

Unmaintained since 2023-02-27 but feature-complete, Zlib/CC0/MIT-licensed and small enough to vendor; widely used in the retro scene (Commander X16 ROM, RomWBW, rasm).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table and pareto_graph.png compare LZSA against LZ4/LZ4_HC on ratio (Silesia, Canterbury, Calgary, enwik9) and on ZX Spectrum (Z80) decompression rate; no compiler, flags or host CPU and no benchmark harness, so C.
- **Verifier notes:** Pareto graph shows LZSA1-m4/m5 beating LZ4 on Z80 decompression speed, so the 'faster than LZ4 on 8-bit' prose has numbers behind it (graph only); not faster on any axis on modern hosts. Metadata confirmed: 261 stars, not archived, not a fork, last commit 2023-02-27 (abandoned).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README table
- **Pages the verifier opened:**
  - <https://github.com/emmanuel-marty/lzsa>
  - <https://github.com/emmanuel-marty/lzsa/commits/master>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/pareto_graph.png>
- **Sources the enricher read:**
  - <https://github.com/emmanuel-marty/lzsa>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/README.md>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/Makefile>
  - <https://github.com/emmanuel-marty/lzsa/tree/master/src>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/src/expand_block_v1.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/src/expand_block_v2.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/src/expand_inmem.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/src/expand_inmem.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/src/frame.c>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/src/lib.h>
  - <https://raw.githubusercontent.com/emmanuel-marty/lzsa/HEAD/src/shrink_inmem.h>
  - <https://github.com/emmanuel-marty/lzsa/issues?q=is%3Aissue>
  - <https://github.com/emmanuel-marty/lzsa/issues/65>
  - <https://github.com/emmanuel-marty/lzsa/issues/69>
  - <https://github.com/emmanuel-marty/lzsa/commits/master>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/emmanuel-marty/lzsa`) · [data/wave9/enrich/raw/github_com_emmanuel_marty_lzsa.json](../../../data/wave9/enrich/raw/github_com_emmanuel_marty_lzsa.json) (enrichment confidence 0.6)

</details>
