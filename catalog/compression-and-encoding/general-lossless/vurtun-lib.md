# mmx sdefl/sinfl (single-header deflate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT OR Unlicense` · 🟡 stale

> Two tiny single-header C files for raw deflate and zlib: compressor about 1.8x zlib 1.2.11, decoder 1.2-1.4x (first-party).

| | |
|---|---|
| **Beats** | zlib 1.2.11 (also miniz 1.0) |
| **Claimed result** | Header table vs zlib 1.2.11 (no CPU, compiler, flags or corpus; comparison harness not public): sdefl -5 compresses faster than zlib -6 in the first-commit run, sinfl decompression 355-436 MB/s after the Oct 2021 re-measurement (201-230 MB/s in Dec 2020, slower than zlib); libdeflate 1.3 faster both ways in the same table. Ratio column says 36.46 vs 36.55 but the byte counts show sdefl -5 at 36,577,183 vs zlib -6 at 36,548,921 (sdefl larger). |
| **Workload** | Deflate compression and inflate decompression of a roughly 100,000,000-byte text corpus (ratio column implies 100 MB, probably enwik8; the header does not name it), compared at several compression levels. |
| **Metric** | throughput |
| **Adoption** | 1.4k stars (vurtun/lib) |
| **Last commit** | 2025-03-19 |
| **Links** | [repository](https://github.com/vurtun/lib) · [benchmark](https://raw.githubusercontent.com/vurtun/lib/HEAD/sdefl.h) |

## Verdict

The first-party table in both headers gives, for an unnamed input of about 100 MB (probably enwik8) with no CPU, compiler, flags or harness: sdefl compresses at 127/45/38 MB/s (levels 0/5/7) against zlib 1.2.11's 72/24/20 MB/s (levels 1/6/9), and sinfl decodes sdefl output at 355-436 MB/s against zlib's 307-314 MB/s. Git history shows only the sdefl decompression column was re-measured (201-230 MB/s in Dec 2020, slower than zlib, then 233-276, 371-423 and 355-436 by Oct 2021), while the zlib, miniz and libdeflate rows and sdefl's compression columns are unchanged since the first commit; the sdefl ratio column also disagrees with its own byte counts (sdefl -5 writes 36,577,183 bytes, more than zlib -6's 36,548,921, though the column shows 36.46 vs 36.55).

## Use it when

- Small C or C++ programs, games and WebAssembly modules where about 3.7 KB per side matters and vendoring zlib or libdeflate is too heavy (raylib vendors both headers for CompressData/DecompressData).
- Compressing your own in-memory buffers (assets, save files, PNG IDAT) at levels 0-7, where the header table shows about 1.8x zlib 1.2.11's compression speed at similar ratio.
- Round-tripping data your own program produced and stored with its decompressed size, so the one-shot sinflate output buffer can be sized exactly.
- x86-64 or ARM/AArch64 hosts, where sinfl's 16-byte SIMD match copies apply.

## Skip it when

- Any untrusted or third-party compressed input: sinfl has no input-end check in Huffman blocks, no back-reference distance check and an unbounded code-length repeat loop that overflows a 320-byte stack array (open issues #66 and #69, no maintainer reply).
- When speed is the goal: libdeflate 1.3 in the same table compresses faster at level 1 (147 vs 127 MB/s at a smaller output) and decodes about 1.6x faster (667-689 vs 355-436 MB/s).
- Streaming, gzip files, preset dictionaries, inputs of 2 GB or more (int sizes) or unknown decompressed size: only one-shot buffer calls exist.
- Incompressible inputs above about 1 MiB when the output buffer is sized with sdefl_bound() (see gotchas).
- Level 8: an 8192-entry chain (32x level 7) that the table does not cover; a raylib/rpng user reported 14 s versus 4 s for stb_image_write on a 4096x4096 RGBA PNG (issue #35, level not stated).

## How it is fast

The compressor uses hash chains over a 32 KB window (15-bit multiplicative hash of 4 bytes) with chain length 2^(level+1) (2 at level 0, 256 at level 7, 8192 at level 8), greedy parsing below level 5 and one-step lazy matching from level 5, skips hash insertion inside long matches at levels 0-1, and emits per-256 KB-block dynamic Huffman (14-bit literal code limit) or stored blocks, never fixed ones. The decoder keeps a 64-bit bit buffer with a branchless refill (8-byte unaligned load, bitcnt |= 56), two-level lookup tables (10-bit literal/length root, 8-bit distance root), decodes two literals per refill, and copies matches 16 bytes at a time (SSE2/NEON) or 8 bytes at a time, with a broadcast for distance 1, whenever 48 bytes of output headroom remain. It also omits the input-end and back-reference distance checks a validating decoder performs (open issue #66), so its decode speed is not like-for-like with zlib's.

## Compared with alternatives

Pick it over miniz when you want the smallest encoder and decoder pair and more speed (127 vs 122 MB/s compression at a much better ratio, 355-436 vs 208-261 MB/s decompression in the same table). Pick libdeflate when speed matters, since it wins both ways in the same table, and Wuffs, zlib-ng or libdeflate for any input you did not produce yourself.

## Integration

| | |
|---|---|
| **Form** | header-only (two single-header files; define SDEFL_IMPLEMENTATION / SINFL_IMPLEMENTATION in one translation unit) |
| **Dependencies** | none beyond the C standard library (string.h, assert.h, limits.h); emmintrin.h or arm_neon.h when SIMD is enabled |
| **Minimum toolchain** | sdefl targets C89 with a portable ilog2 fallback; sinfl needs C99-level features in practice (unsigned long long, a // comment, a declaration after a statement in zsinflate) plus __builtin_clz (GCC/Clang/TCC) or _BitScanReverse (MSVC), with no portable fallback; usable from C++ via extern "C" |
| **Platforms** | any for sdefl; sinfl uses SSE2 on x86-64/Windows and NEON on ARM/AArch64, a scalar 64-bit path elsewhere (SINFL_NO_SIMD forces it), and assumes a little-endian host because native 64-bit loads feed its LSB-first bit buffer (not documented) |
| **Thread safety** | Not documented; by code reading reentrant (only static const tables), with one struct sdefl per concurrent compression and about 8 KB of decoder state on the stack |
| **Drop-in for the baseline** | partial: output is standard raw deflate or zlib that zlib reads, but the API is one-shot buffers with no z_stream, and sinfl mis-decodes some valid third-party streams (see gotchas) |

## Gotchas

- sdefl_bound() still under-reports for incompressible input after the 2025 fix (by code reading and arithmetic, not executed): every 256 KB block falls back to five stored chunks (25 bytes overhead) while the bound budgets about 20 bytes per 256 KB, so random data passes the bound from about 1 MiB (zsdeflate) or 1.5 MiB (sdeflate); zsdeflate overruns it by 60 bytes at 4 MiB and 1,260 bytes at 64 MiB. Callers that allocate sdefl_bound() bytes overflow the heap; raylib's CompressData does, with the older, smaller formula.
- The per-block sequence array (87,382 entries per 256 KB) assumes at most one sequence per 3 bytes, but alternating 1-byte literals and 4-byte matches give 2 per 5 bytes (104,858). Only assert() guards it, so NDEBUG builds can write past seq[] into the rest of struct sdefl and beyond on crafted input. Real image data already hit the earlier one-per-4-bytes cap (issue #39, which led to the current size). sdeflate also never resets seq_cnt (open issue #58), so zero the struct before first use.
- sinfl's refill reads 8 bytes past the current position even on valid streams (issue #69): pad input buffers by 8 bytes. Malformed input can read before the output buffer (unchecked distances) and overflow the stack through code-length repeats (issue #66). Raw sinflate returns the bytes decoded so far, not an error, on corrupt input. The fast path can also consume a literal plus a full match (up to 63 bits) after a refill that guarantees only 56, a gap guarded only by assert(), so rare valid streams with near-15-bit codes may mis-decode (code reading only).
- sinfl_build replaces any incomplete Huffman code with symbol 0. A valid block whose only distance code is not code 0 (miniz's tdefl emits a single 1-bit code; RFC 1951 allows it) therefore decodes with distance 1, silently wrong under sinflate and caught only by the Adler-32 check in zsinflate (code reading, not executed).

## Known shortcomings

- Tier C: the sdefl/sinfl header table (vs zlib 1.2.11) names no CPU, compiler, flags or corpus and the comparison harness is not public (tests/defl_test.c times sdefl only); the numbers predate PR #56 (March 2025), which fixed a sinflate output-buffer overflow and sdefl_bound being 3 bytes short; libdeflate 1.3 is faster in the same table. Repo renamed from vurtun/mmx; stale (last commit 2025-03-19).
- Enricher (git history): only the sdefl decompression column was ever re-measured (201-230 MB/s in Dec 2020, slower than zlib; 355-436 by Oct 2021); the zlib, miniz and libdeflate rows and sdefl's compression columns date from the first commit, whose dynamic-block header declared 288 literal codes (fixed Jan 2021, issue #34), and predate the May 2023 fix for invalid length code 286 (issue #40). The ratio column contradicts its own byte counts (sdefl -5 writes 36,577,183 bytes vs zlib -6 36,548,921 but the column says 36.46 vs 36.55), so the 'ratio about equal' claim is backwards. Code-reading bugs: sdefl_bound() is still too small for incompressible input over 1-1.5 MiB (+60 B at 4 MiB, +1,260 B at 64 MiB; raylib CompressData sizes by it); seq[] holds 87,382 entries per 256 KB block but crafted input can need 104,858, guarded only by assert(); sinfl turns any incomplete Huffman code into symbol 0, so valid miniz streams with one distance code decode wrong; the sinfl fast path can need 63 bits after a refill that guarantees 56. Open issues without maintainer reply: #66 (stack overflow, over-read, unchecked distances), #69 (8-byte over-read), #58 (seq_cnt not reset); not C89, little-endian only; level 8 unbenchmarked (issue #35: 14 s vs 4 s for stb_image_write).

## Caveats and trade-offs

First-party table in the sdefl.h/sinfl.h header comments with no CPU, compiler, flags or corpus name; the ratio column implies a 100,000,000-byte input (probably enwik8). The table is laid out like lzbench output, but the comparison harness is not public: the repo's tests/defl_test.c only times sdeflate/sinflate on a file given on the command line (CLOCK_REALTIME, one pass per level) and never calls zlib, miniz or libdeflate. Library versions (sdefl 1.0, zlib 1.2.11, libdeflate 1.3, miniz 1.0) place the run around 2020. The numbers predate correctness fixes merged in March 2025 (PR #56 by lelegard): sinflate()/zsinflate() could overflow the caller's output buffer when it was too small, sdefl_bound() under-reported the worst-case size by 3 bytes (zsdeflate wrote past the reported bound under fuzzing), and decompress-size handling was wrong; the fixes add bounds checks in the decoder, so post-fix speed is unmeasured. The same table shows libdeflate 1.3 clearly ahead of sdefl (147 MB/s compress at -1, 667 to 689 MB/s decompress), so sdefl is faster than zlib but not the fastest deflate. Listed repo vurtun/mmx has been renamed vurtun/lib (the Readme title still says mmx); the comparison picks the sdefl and sinfl components out of a five-header collection (json.h, sched.h, web.h carry zlib/BSD licences). No independent measurements were found (one WebSearch returned nothing on sdefl). Ratios are derived from the page table. Unlicense option carries no patent grant. [retier] Baseline rows and sdefl compression columns measured on the first commit with a malformed dynamic-block header (#34) and before the invalid-length-code fix (#40); only decompression re-measured. sdefl_bound() under-sizes incompressible input above 1-1.5 MiB (heap overflow for callers such as raylib CompressData); seq[] overflow guarded only by assert(); sinfl mis-decodes incomplete Huffman codes and can over-read; open #66, #69, #58 with no maintainer reply. Repo renamed from vurtun/mmx; stale since 2025-03-19.

Small ANSI C (C89) single-header deflate (525 lines) and inflate (320 to 500 lines), about 3.7 KB each as WebAssembly; API is one-shot buffers (sdeflate/zsdeflate, sinflate/zsinflate) for raw deflate and zlib framing, with no gzip container or streaming interface found; the repo's other headers (json.h, sched.h, web.h) carry no performance claims.

## Maintenance

Stale since 2025-03-19, with security issues #66 and #69 open and unanswered as of 2026-10, but MIT or Unlicense and short enough to vendor; patch the bounds yourself or start from raylib's partly hardened copy (it adds input-end and distance checks, not the repeat bound), and use it only on data you produced.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The benchmark table in the sdefl.h and sinfl.h header comments compares sdefl 1.0 against zlib 1.2.11, miniz 1.0 and libdeflate 1.3, but gives no CPU, compiler, flags or corpus name, and the repo's only timing code (tests/defl_test.c) times sdefl/sinfl alone with no zlib harness; first-party numbers without methodology are C.
- **Retiered** C to D: The header table mixes runs: its baseline rows and sdefl compression columns come from the first commit, whose encoder emitted a malformed dynamic-block header (288 literal codes, fixed in issue #34) and predate the length-code-286 fix (#40), only the decompression column was re-measured, and the ratio column contradicts the listed byte counts; no harness, CPU, compiler or flags are public. Directional only (numbers-before-correctness-fix precedent).
- **Verifier notes:** Every number in claimed_speedup matches the header table; tier C stands (no methodology, no public comparison harness). Shortcomings to record: no CPU/compiler/flags/corpus, harness not in repo, numbers predate the 2025 decoder buffer-overflow and sdefl_bound fixes (PR #56), libdeflate 1.3 beats it in the same table, last commit 2025-03-19 (stale).
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-69 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/sinfl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/tests/defl_test.c>
  - <https://github.com/vurtun/lib>
  - <https://github.com/vurtun/lib/commits>
  - <https://github.com/vurtun/lib/tree/master>
  - <https://github.com/vurtun/lib/tree/master/tests>
  - <https://github.com/vurtun/lib/pull/56>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/sinfl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/vurtun/lib/HEAD/tests/defl_test.c>
  - <https://github.com/vurtun/lib/pull/56>
  - <https://github.com/vurtun/lib/issues?q=is%3Aissue>
  - <https://github.com/vurtun/lib/issues/66>
  - <https://github.com/vurtun/lib/issues/69>
  - <https://github.com/vurtun/lib/issues/58>
  - <https://github.com/vurtun/lib/issues/39>
  - <https://github.com/vurtun/lib/issues/35>
  - <https://github.com/vurtun/lib/issues/40>
  - <https://github.com/vurtun/lib/issues/52>
  - <https://github.com/vurtun/lib/commits/master>
  - <https://github.com/vurtun/lib/commits/master/sdefl.h>
  - <https://github.com/vurtun/lib/commits/master/sinfl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/956ac0477aa99be2082768c816c365a514e716c1/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/ba74d5d65ad17749f7c32e6f9f8e896085f3cdc4/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/85d2cd7d85a83f82c61995c63fdd1bef10eef326/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/c26fcf8f4ed4670aea0f989b9c66ba73484329a6/sinfl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/177d6bc7b59b5d579e8292ecfb4943726e086218/sinfl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/4f93c8255a031af643d24d60ec4a2237b8ef7ba7/sinfl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/8252ab92429f3b14ce792f052ad821c84357bf92/sinfl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/71382a1d14dad58219e7f6634d2381fa30dab175/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/d41cf94679443efc14174cac103c9c15bb115860/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/7f77450007297c8e7312795c31db6299c0f66d3f/sdefl.h>
  - <https://raw.githubusercontent.com/vurtun/lib/5a3f3aba052e63ffae8eb0214c6bb8ffffedea3c/sdefl.h>
  - <https://raw.githubusercontent.com/raysan5/raylib/HEAD/src/external/sdefl.h>
  - <https://raw.githubusercontent.com/raysan5/raylib/HEAD/src/external/sinfl.h>
  - <https://raw.githubusercontent.com/raysan5/raylib/HEAD/src/rcore.c>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_tdef.c>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/vurtun/lib`) · [data/wave1/enrich/raw/github_com_vurtun_lib.json](../../../data/wave1/enrich/raw/github_com_vurtun_lib.json) (enrichment confidence 0.8)

</details>
