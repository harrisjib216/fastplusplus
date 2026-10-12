# FPC (Fast Prefix Coder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `ISC` · 🔴 abandoned

> Single-file ISC C Huffman (prefix) coder decoding silesia.tar about 1.25x faster than FSE's Huff0 and 3.7x faster than zlib's Huffman.

| | |
|---|---|
| **Beats** | zlib Huffman (zlibh) and FSE Huff0 (fsehuf) as packaged in TurboBench |
| **Claimed result** | silesia.tar (Core i5-4460, TurboBench): fpc 32 decodes at 897.28 MB/s versus 715.36 MB/s for fsehuf, 591.30 MB/s for rans_static16, 483.55 MB/s for fse and 243.08 MB/s for zlibh (about 1.25x fsehuf and 3.7x zlibh, derived from page data); fpc 16 compresses at 476.96 MB/s versus 248.55 MB/s for zlibh and decodes at 821.30 MB/s. Ratios are within 0.1 percentage points (61.4% for fpc 32 and fsehuf). On the Allwinner H3 board, enwik8: fpc 32 decodes at 90.70 MB/s versus 61.11 MB/s for fsehuf and 62.90 MB/s for zlibh. Independent powturbo Entropy Coder Benchmark (snippet only, file and CPU not seen): FPC 32 decode 928.53 MB/s versus FSEhuf 32 at 831.45 MB/s. |
| **Workload** | Order-0 entropy coding of silesia.tar (211 MB) on a Core i5-4460 and of enwik8 on an Orange Pi PC Plus (Allwinner H3), run through TurboBench. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-4460 @ 3.20GHz (silesia.tar); Orange Pi PC Plus, Allwinner H3 (enwik8) |
| **Compiler and flags** | Not stated for the benchmark run; the standalone Makefile uses -Wall -O2 -std=c99 -DNDEBUG |
| **Adoption** | 33 stars |
| **Last commit** | 2022-04-24 |
| **Links** | [repository](https://github.com/kagiannis/FPC) · [benchmark](https://raw.githubusercontent.com/kagiannis/FPC/HEAD/README.md) |

## Verdict

The author ran TurboBench (compiler and flags not stated) on silesia.tar on a Core i5-4460: fpc with 32 KB blocks decoded at 897 MB/s versus 715 for Huff0 (fsehuf), 591 for rans_static16, 484 for FSE and 243 for zlib's Huffman, at the same 61.4% ratio as Huff0, while Huff0 still encoded slightly faster (575 versus 548 MB/s). On an Allwinner H3 board, enwik8 decode was 90.7 MB/s versus 61.1 for Huff0; an independent powturbo entropy-coder benchmark figure (928.53 versus 831.45 MB/s decode) is known only from a search snippet.

## Use it when

- Order-0 entropy stage of a custom compressor (after LZ, BWT or transform stages) where decode throughput matters more than the last 1-2% of ratio.
- Byte data with non-skewed distributions such as text: on silesia.tar it matches Huff0's ratio (61.4%) and decodes 897 MB/s versus 715 MB/s on a Core i5-4460.
- Small in-order ARM cores: on an Allwinner H3 board, enwik8 decoded at 90.7 MB/s versus 61-63 MB/s for Huff0, zlib Huffman and FSE.
- Projects that want a permissively licensed (ISC) single C file to vendor, with no dependencies and big-endian support.
- Data with shifting statistics, using bsize = 0 so adaptive block subdivision picks block sizes.

## Skip it when

- Skewed or sparse distributions (well under 1 bit per byte): prefix codes cost at least 1 bit per symbol, and issue #3 (open) reports FSE compressing most files of a sparse binary set better.
- Multithreaded encoding or decoding within one process: the prefix-length header code uses non-static global state (byte_pos, init_pos, byte_end, c, nibble_count), so concurrent calls race.
- When you need the fastest current Huffman decoder: PIVCO-Huffman and hypersonic-rANS report several GB/s, and the FPC tables compare against TurboBench's Huff0 build from the 2017-2018 era, not today's zstd Huffman.
- Inputs larger than one block per call without the wrapper format: block APIs require size &lt; 64 KB and the length fields are 16-bit.
- Untrusted input in safety-critical code: no fuzzing is documented, and FPC_decompress returns 0 for both errors and empty output.

## How it is fast

Code lengths are capped at MAX_BIT_LEN = 11 bits with the package-merge algorithm, so decoding is a single 2048-entry table lookup per symbol with no multi-level tables. Bytes are split round-robin across 3 interleaved bit streams (NUM_STREAMS) to give the CPU independent dependency chains, and each stream's 64-bit bit buffer is refilled branchlessly with one unaligned word load every RENORM_NUM = 5 symbols (5 x 11 bits fits in 56); the decode loop is unrolled twice and prefetches on ARM. The encoder mirrors this with table lookups and unconditional 64-bit stores, and the adaptive mode chooses block boundaries by dynamic programming over 2 KB steps using integer log2 entropy estimates.

## Compared with alternatives

Pick FPC over FiniteStateEntropy's Huff0 when you want a small ISC-licensed C file whose decoder was measured faster than Huff0 at equal ratio on silesia.tar and enwik8 in TurboBench. Prefer PIVCO-Huffman or hypersonic-rANS for top decode speed on modern x86 or Apple cores, and FSE or an rANS coder for skewed or sparse data.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | C99 (Makefile uses -O2 -std=c99); GCC/Clang builtins used when available |
| **Platforms** | any 32- or 64-bit CPU with detectable endianness (little and big endian); tuned constants for x86-64, i386, ARM and AArch64 |
| **Thread safety** | not thread-safe: block header encode/decode uses non-static global variables |
| **Drop-in for the baseline** | no |

## Gotchas

- Compile fpc.c as C, not C++: fpc.c does not include fpc.h, so building it with g++ yields C++-mangled symbols and 'undefined reference to FPC_compress' link errors (issue #2, open); the reported workaround was #include "fpc.c".
- fpc.c exports non-static symbols with generic names (global variable c, byte_pos, and functions brev, byte_count, sort_inc, build_prefix_codes), which can collide with other code at link time; fpc.h has no include guard and does not include stddef.h for size_t.
- Tuning (NUM_STREAMS, MAX_BIT_LEN, ADAPTIVE_STEP) is by #define in fpc.c, and the stream format depends on them, so encoder and decoder must be built with the same values.
- Issue #4 (closed 2020) reported uninitialized reads under Valgrind in the adaptive block-size path producing outputs over 15000 bytes for inputs under 100 bytes; no fix commit is linked from the issue, though earlier history mentions 'fixed unitialised read'.

## Known shortcomings

- Tier B on TurboBench tables (FPC 32 decode 897 MB/s vs fsehuf 715 on silesia.tar); the powturbo Entropy Coder Benchmark page (928.53 vs 831.45 MB/s) is blocked and snippet-only. Last commit 2022-04-24, abandoned.
- Not thread-safe: non-static globals byte_pos, c and nibble_count are used in the block header code. fpc.c does not include fpc.h, so a g++ build yields mangled symbols and link errors (issue #2, open). Exported generic symbol names can clash at link time. Issue #4 Valgrind uninitialized reads in the adaptive path closed with no fix commit linked. Issue #3 open: sparse data loses to FSE. FPC_decompress returns 0 on error.

## Caveats and trade-offs

The README tables were run by the project author through the TurboBench harness; no compiler or flags stated for that run (the standalone Makefile uses -O2). The independent powturbo Entropy Coder Benchmark figure is from a WebSearch snippet only, since sites.google.com is blocked here; its file, CPU and date were not seen. fsehuf compresses faster than fpc 32 (574.79 versus 548.16 MB/s), so the win is decode speed. Last commit April 2022. The older owner name algorithm314/FPC (still linked from TurboBench's README) redirects to kagiannis/FPC.

Prefix (Huffman) coder with length-limited package-merge codes (default max 11 bits), 3 interleaved streams by default, adaptive block subdivision. Static per block, so it cannot reach the ratio of adaptive arithmetic coders such as fpaq0p_sh (58.7% on silesia.tar).

## Maintenance

Abandoned since April 2022 (last commits only touched the Makefile; two issues open, no releases) but ISC-licensed and only about 1,100 lines of C, so it is easy to vendor if you fix the global state for threaded use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** The README tables come from the well-known third-party TurboBench harness (FPC is an integrated TurboBench codec) and show fpc 32 decoding silesia.tar at 897.28 MB/s versus 715.36 for fsehuf and 243.08 for zlibh on a Core i5-4460. A WebSearch snippet of powturbo's own Entropy Coder Benchmark (sites.google.com/site/powturbo/entropy-coder, blocked here) shows FPC 32 at 928.53 MB/s decode versus FSEhuf 32 at 831.45 MB/s, an independent run consistent with the claim. No compiler or flags are stated, so not A.
- **Verifier notes:** Every number in the record matches the README. Kept B on the strength of the TurboBench harness plus the snippet of powturbo's independent entropy-coder benchmark listing FPC ahead of FSEhuf on decode; the orchestrator may drop to C if snippet-only third-party evidence is not accepted. Metadata confirmed: ISC, 33 stars, last commit 2022-04-24 (abandoned, over 3 years), not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kagiannis/FPC/HEAD/README.md>
  - <https://github.com/kagiannis/FPC>
  - <https://github.com/kagiannis/FPC/commits>
  - <https://raw.githubusercontent.com/kagiannis/FPC/HEAD/Makefile>
  - <https://raw.githubusercontent.com/powturbo/TurboBench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/kagiannis/FPC>
  - <https://raw.githubusercontent.com/kagiannis/FPC/HEAD/README.md>
  - <https://raw.githubusercontent.com/kagiannis/FPC/HEAD/Makefile>
  - <https://raw.githubusercontent.com/kagiannis/FPC/HEAD/fpc.h>
  - <https://raw.githubusercontent.com/kagiannis/FPC/HEAD/fpc.c>
  - <https://raw.githubusercontent.com/kagiannis/FPC/HEAD/cli.c>
  - <https://github.com/kagiannis/FPC/issues?q=is%3Aissue>
  - <https://github.com/kagiannis/FPC/issues/2>
  - <https://github.com/kagiannis/FPC/issues/3>
  - <https://github.com/kagiannis/FPC/issues/4>
  - <https://github.com/kagiannis/FPC/commits>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/kagiannis/fpc`) · [data/wave9/enrich/raw/github_com_kagiannis_fpc.json](../../../data/wave9/enrich/raw/github_com_kagiannis_fpc.json) (enrichment confidence 0.8)

</details>
