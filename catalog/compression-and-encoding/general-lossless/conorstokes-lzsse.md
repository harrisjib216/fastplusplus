# LZSSE

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> LZSS codec whose format is built for branchless SSE4.1 decoding; decodes about 1.3x faster than LZ4HC at similar ratio.

| | |
|---|---|
| **Beats** | LZ4 |
| **Claimed result** | lzbench 2.4 (EPYC 9555P): lzsse8 -6 decompress 5007 MB/s at ratio 35.61% vs lz4hc 1.10.0 -12 3813 MB/s at 36.45% (1.31x, derived from page data); lzsse4 -6 4714 MB/s at 35.91%. Compression is slow (about 9 MB/s at -6). The repo README itself gives no current numbers. |
| **Workload** | SSE-based decompression of silesia.tar single thread, via lzbench rows for lzsse2/4/8 vs lz4hc. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 151 stars |
| **Last commit** | 2019-04-18 |
| **Links** | [repository](https://github.com/ConorStokes/LZSSE) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In lzbench 2.4 (gcc 15.2.0 release binary, single thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar), lzsse8 2019-04-18 -6 decompressed at 5007 MB/s for 35.61% and lzsse4 -6 at 4714 MB/s for 35.91%, vs lz4hc 1.10.0 -12 at 3813 MB/s for 36.45% (1.31x and 1.24x, derived from page data); both LZSSE rows compress at about 9 MB/s, and lzsse2 -6 (3850 MB/s) is level with plain lz4 (3832 MB/s). The author's 2016 blog benchmarks are on a blocked host; a search snippet says LZSSE8 decode stays above 2607 MB/s on binary data where LZ4 dropped to 2115 MB/s on enwik8 (snippet only).

## Use it when

- Assets or data blobs compressed once offline and decompressed many times on x86-64 (games, read-only stores), where decode MB/s matters more than encode time.
- Text and mixed corpora at LZ4HC-class ratio: lzsse8 -6 on silesia.tar decodes 5007 MB/s at 35.61% vs lz4hc -12 at 3813 MB/s and 36.45% (lzbench 2.4, EPYC 9555P).
- Highly compressible text with LZSSE2, which the README recommends for text with short literal runs.
- Code that can vendor a small BSD-2-Clause C++ source drop and wants decode speed with steady per-file throughput.

## Skip it when

- Anything that compresses at runtime: optimal-parse levels run at about 8-9 MB/s, and the only fast mode in lzbench (lzsse4fast, 266 MB/s, 45.26%) is slower and worse than plain LZ4 (550 MB/s, 47.60%, 3832 MB/s decode) on the same run.
- Non-x86 targets: requires SSE4.1 and 64-bit x86; no ARM/NEON or scalar fallback (issue #1 'Portable version' open since 2016), and the header warns it performs poorly on 32-bit x86.
- LZSSE8 fast-parse output: issue #14 (open, labelled bug, March 2025) has a reproducible file whose LZSSE8_CompressFast output fails to decompress; lzbench flags the same bug.
- Untrusted input or tight buffers: issue #7 (open since 2016) reports LZSSE2_Decompress writing outside the buffer for very short data under AddressSanitizer.
- Projects needing a maintained dependency: last commit 2019-04-18, 25 commits, and the README itself says the code is only 'approaching production readiness'.

## How it is fast

The stream is a sequence of 4-bit control nibbles packed 16 bytes at a time; the decoder loads one control block, uses pshufb (_mm_shuffle_epi8) lookup tables, compare masks and blendv to compute per-step input and output byte counts and literal/match selection, then each step does an unconditional 16-byte load of the match source, masks in literals and writes 16 bytes, with no data-dependent branches. Matches are short (LZSSE8: 4-byte minimum, up to 15 bytes per control, longer matches chained by carry nibbles) and offsets are 16-bit, so copies stay in a 64 KiB window and in L1/L2. Ratio comes from the optimal parser (binary-tree match finder similar to LzFind plus a Storer-Szymanski style parse), which is why compression is slow.

## Compared with alternatives

Pick LZSSE8 over LZ4HC for x86-64-only read-heavy data when about 30% faster decoding at slightly better ratio is worth an unmaintained, SSE4.1-only dependency with open correctness issues; pick LZ4/LZ4HC for portability and maintenance, or misa77 or ZXC for a maintained decode-speed-first codec. LZAV and zstd are better whenever compression speed matters.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (SSE4.1 intrinsics via &lt;x86intrin.h&gt; or &lt;intrin.h&gt;) |
| **Minimum toolchain** | C++ compiler with SSE4.1 enabled (e.g. -msse4.1): MSVC, Clang or GCC; any other compiler hits '#error Platform not supported'; premake4 project for the example |
| **Platforms** | x86-64 with SSE4.1 only (lzbench: Windows builds via MinGW-w64 only) |
| **Thread safety** | Per the header: one parse state must not be used by concurrent calls; separate states may run in parallel. Decompress is stateless. |
| **Drop-in for the baseline** | no |

## Gotchas

- Decompress expects outputLength to equal the original size: issue #16 (open, Jan 2026) shows LZSSE8 level-17 data decoded into a buffer 32 bytes larger returns 15 bytes short, and issue #12 shows the same for LZSSE2 when the block buffer exceeds the input.
- Decompress returns a byte count below outputLength on error rather than an error code, and does no hash check; 'corrupt data can still be valid to decompress' per the header.
- The optimal-parse state is large: a 2^20-entry hash root table, a binary-tree node array for the 64 KiB window, and an Arrival record per input byte sized by MakeOptimalParseState(bufferSize).
- Compressed output is never larger than the input (stored raw instead), but outputLength for compression must be at least inputLength or the call returns 0.

## Known shortcomings

- Tier B on lzbench (lzsse8 -6 decode 5007 vs lz4hc -12 3813 MB/s, 1.31x derived from page data); compression is slow and lzsse8fast has an open bug (issue #14).
- Four open correctness bugs, none answered: #14 LZSSE8_CompressFast output fails to decompress; #16 (Jan 2026) LZSSE8 output truncated when the decode buffer is larger than the original; #12 the same truncation in LZSSE2; #7 (2016) LZSSE2_Decompress writes out of bounds on tiny inputs (ASan). x86-64 SSE4.1 only; compression about 9 MB/s; lzsse2 -6 at 3850 MB/s is level with plain lz4 (3832), so only lzsse8 -6 wins.

## Caveats and trade-offs

Repo says its blog-post figures are out of date; numbers here come from lzbench. Decompress-only win (compression about 9 MB/s at the optimal-parse levels), 64-bit x86 with SSE4.1 only; lzbench notes lzsse8fast has a bug (ConorStokes/LZSSE issue #14). Plain lz4 1.10.0 decodes at 3832 MB/s, close to lzsse2.

Requires SSE4.1-class x86; compression is very slow (about 8-9 MB/s at -6 in lzbench); no ARM path.

## Maintenance

Abandoned since 2019-04-18 (151 stars, open bug reports from 2016 to 2026 unanswered); BSD-2-Clause and small enough to vendor, but fuzz and round-trip test it yourself and avoid LZSSE8_CompressFast.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent, well-known lzbench suite (public code, gcc 15.2.0 release binary, single thread of an EPYC 9555P) lists lzsse8 2019-04-18 -6 at 5007 MB/s decompress, 35.61% and lzsse4 -6 at 4714 MB/s, 35.91% vs lz4hc 1.10.0 -12 at 3813 MB/s, 36.45%; compile flags are not stated on the page (only implicit in the Makefile), so B, not A, consistent with other lzbench-based entries.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** License BSD-2-Clause, 151 stars, last commit 2019-04-18 (1847c3e, the version lzbench integrates); abandoned status correct. The blog posts on conorstokes.github.io are on a blocked host and were not opened.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/ConorStokes/LZSSE>
  - <https://raw.githubusercontent.com/ConorStokes/LZSSE/HEAD/README.md>
  - <https://github.com/ConorStokes/LZSSE/commits/master>
- **Sources the enricher read:**
  - <https://github.com/ConorStokes/LZSSE>
  - <https://raw.githubusercontent.com/ConorStokes/LZSSE/HEAD/README.md>
  - <https://raw.githubusercontent.com/ConorStokes/LZSSE/HEAD/lzsse8/lzsse8.h>
  - <https://raw.githubusercontent.com/ConorStokes/LZSSE/HEAD/lzsse8/lzsse8.cpp>
  - <https://raw.githubusercontent.com/ConorStokes/LZSSE/HEAD/lzsse8/lzsse8_platform.h>
  - <https://raw.githubusercontent.com/ConorStokes/LZSSE/HEAD/lzsse4/lzsse4.h>
  - <https://raw.githubusercontent.com/ConorStokes/LZSSE/HEAD/lzsse2/lzsse2.h>
  - <https://github.com/ConorStokes/LZSSE/issues?q=is%3Aissue>
  - <https://github.com/ConorStokes/LZSSE/issues/14>
  - <https://github.com/ConorStokes/LZSSE/issues/16>
  - <https://github.com/ConorStokes/LZSSE/issues/7>
  - <https://github.com/ConorStokes/LZSSE/issues/12>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/conorstokes/lzsse`) · [data/wave9/enrich/raw/github_com_conorstokes_lzsse.json](../../../data/wave9/enrich/raw/github_com_conorstokes_lzsse.json) (enrichment confidence 0.85)

</details>
