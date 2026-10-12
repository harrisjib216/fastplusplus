# fast_zlib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Drop-in replacement for zlib's longest_match() that makes level 6-9 deflate about 2.5-10x faster on the author's data, output still standard deflate.

| | |
|---|---|
| **Beats** | zlib 1.2.11 (stock deflate, level 9) |
| **Claimed result** | Wiki Release 2 (VS 2019), level 9, C version vs original zlib: source code 5.1 s vs 10.7 s (28,858,611 vs 28,859,103 bytes); binaries 12.6 s vs 49.1 s (54,473,779 vs 54,485,836 bytes); geometry 18.2 s vs 180.0 s (114,915,875 vs 114,942,962 bytes). Wiki states the optimized version 'performs nearly 2.5-10 times faster'. Silesia (202.1 MB) level 9: 20.90 vs 8.51 MB/s; level 5: 29.82 vs 29.23 MB/s; level 1: 63.52 vs 62.10 MB/s. Derived from page data: 2.1x, 3.9x and 9.9x on the three level-9 sets, about 2.5x on Silesia level 9, about 1.02x at levels 5 and 1. |
| **Workload** | Compression at level 9 of Unreal Engine 4 source code (137 MB), UE4 Win64 binaries, and graphics files (TIF/PNG geometry and textures) up to 256 MB; also the Silesia corpus (202.1 MB). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4702MQ @ 2.2 GHz, Windows 8.1 64-bit |
| **Compiler and flags** | Visual Studio 2019 (Release 2 tests), VS 2013 (Release 1); optimization flags not stated |
| **Adoption** | 146 stars, 25 forks |
| **Last commit** | 2022-10-14 |
| **Links** | [repository](https://github.com/gildor2/fast_zlib) · [benchmark](https://github.com/gildor2/fast_zlib/wiki) |

## Verdict

Author's wiki, Release 2: Visual Studio 2019, Windows 8.1 x64, Core i7-4702MQ, zlib 1.2.11, level 9. Times fell from 10.7 to 5.1 s (UE4 source), 49.1 to 12.6 s (UE4 binaries) and 180.0 to 18.2 s (geometry), and Silesia level 9 went from 8.51 to 20.90 MB/s, about 2.5x (derived from page data), with marginally smaller output. The same table has the then-current zlib-ng at 8.61 MB/s on Silesia level 9 but 147.43 MB/s at level 1 versus fast_zlib's 63.52.

## Use it when

- You must keep the zlib API and byte-compatible deflate/gzip output, and compress at levels 6-9 (asset packing, archive building, PNG or zip writers at high levels).
- Highly redundant or binary data at level 9, where hash chains get long: the author's UE4 binaries went 49.1 s to 12.6 s and geometry 180.0 s to 18.2 s.
- Builds that vendor stock zlib 1.2.x and can patch deflate.c, but cannot switch to zlib-ng or libdeflate.
- Windows x86 builds where the 32-bit NASM version is usable (marginally faster than the C version per the wiki).

## Skip it when

- Levels 1-5: offset search is off, and the Silesia gains are about 2% (level 5 29.82 vs 29.23 MB/s, level 1 63.52 vs 62.10 MB/s).
- When you can use a modern deflate engine: zlib-ng, Cloudflare zlib, ISA-L or libdeflate change more of the pipeline than the match finder, and none of their current versions are in fast_zlib's tables.
- zlib 1.3 or newer: the 1.2.13 patch's first hunk expects the OF((...)) forward declaration of longest_match, which zlib 1.3.1's deflate.c no longer has, so it must be hand-applied; the match.h code also uses a K&R-style definition.
- Forks with a different hash or window layout (Cloudflare zlib, zlib-ng): match.h relies on stock zlib's UPDATE_HASH, prev/head chains and deflate_slow's string insertion; issue #5 notes it is not compatible with Cloudflare's fork.
- Strict-alignment CPUs: candidate and length compares read 16- and 32-bit words through ushf\*/uIntf\* casts at arbitrary window offsets.

## How it is fast

Stock zlib walks one hash chain per position and compares candidates byte by byte. fast_zlib's 'offset search' mode, once it has a match of length L, looks at the hash chains of every 3-byte substring inside the current match (via prev[] at cur_match+i and head[] at the match tail) and switches to the chain whose newest candidate is most distant, so far fewer candidates need checking to find a longer match. Candidate tests use 2-byte and 4-byte word compares (first 4 bytes plus the 2 bytes at best_len-1) and the length scan compares 2 bytes at a time. Offset mode is enabled only when max_chain_length &gt;= 64, which in stock zlib's config table means levels 6-9.

## Compared with alternatives

Pick fast_zlib when you are locked to stock zlib and compress at level 9 with long hash chains; otherwise Cloudflare zlib or zlib-ng give larger speedups across all levels without hand-patching, and libdeflate is faster still if you can drop the streaming zlib API.

## Integration

| | |
|---|---|
| **Form** | source-drop (replacement function compiled into your zlib build; optional 32-bit NASM object) |
| **Dependencies** | zlib source (1.2.11 tested; 1.2.13 via bundled patch); NASM for the assembly version; bash and perl for the test scripts |
| **Minimum toolchain** | C89-era C with K&R definitions (compile as C17 or earlier; C23 removed K&R definitions); tested with Visual Studio 2013/2019 and GCC 5.4.0 per the wiki |
| **Platforms** | C version: any CPU that tolerates unaligned 16/32-bit loads (x86, x86-64, modern ARM); assembly: 32-bit x86 only |
| **Thread safety** | same as zlib: per-stream state only, no globals besides a const copyright string (inferred from the code) |
| **Drop-in for the baseline** | partial — the zlib API and format are unchanged, but you must rebuild zlib with the replaced function |

## Gotchas

- Output is not byte-identical to stock zlib at levels 6-9 (Silesia level 9: 67.63 vs 67.64 MB), so tests that compare compressed bytes or hashes against stock zlib output will fail; the wiki says level 1 output is identical.
- The code itself flags open questions: '?? are MAX_DIST matches allowed ?!' and a TODO about the 'cur_match - offset + len &lt; s-&gt;strstart' restriction limiting RLE-like matches.
- Issue #3 reported intermittent Z_STREAM_ERROR in a managed wrapper around a fast_zlib build; it was closed with no recorded cause or fix.
- Building zlib with this file means you own the zlib version: the benchmarked base, zlib 1.2.11, predates the CVE-2018-25032 and CVE-2022-37434 fixes, so apply it to a patched zlib, not the tested one.

## Known shortcomings

- Gain is at level 9 only; at Silesia levels 5 and 1 the gain is about 2% (29.82 vs 29.23, 63.52 vs 62.10 MB/s). Patch targets zlib 1.2.13 and must be re-applied to newer zlib. Compression ratio can differ slightly from stock zlib.
- The 1.2.13 patch's first hunk needs the OF() declaration that zlib 1.3.1 deflate.c dropped, so 1.3+ needs a hand port; K&R definitions break under C23 defaults; unaligned ushf\*/uIntf\* loads. The offset search runs only at max_chain &gt;= 64 (levels 6-9) and output is not byte-identical to stock zlib there. Issue #3 Z_STREAM_ERROR closed with no recorded cause; issue #5 says incompatible with Cloudflare zlib. The wiki's zlib-ng rows show zlib-ng level 1 at 147.43 MB/s vs fast_zlib 63.52. Benchmarked base zlib 1.2.11 predates the CVE-2018-25032 and CVE-2022-37434 fixes.

## Caveats and trade-offs

First-party numbers on an old laptop CPU (i7-4702MQ, Windows 8.1) with MSVC; the key datasets (UE4 source, binaries, geometry/textures) are the author's own and are not published, and optimization flags are not given. The gain is only at high levels: on Silesia at levels 5 and 1 it is about 2% (29.82 vs 29.23 MB/s, 63.52 vs 62.10 MB/s). Baseline is zlib 1.2.11 only; no comparison with zlib-ng, libdeflate or Cloudflare/Intel zlib forks. It replaces zlib's longest_match only; zlib 1.2.13+ removed ASMV, so it needs the bundled patch (Sources/zlib_1.2.13.patch). Compressed output is slightly smaller than stock zlib output, not byte-identical to it.

Replaces only longest_match in deflate.c (C version or 32-bit x86 NASM assembly); zlib 1.2.13+ needs a patch because ASMV was removed upstream. Output format stays standard deflate, so any inflater reads it. Wiki says compressed sizes are equal to original zlib; the README says 'slightly smaller'.

## Maintenance

Abandoned since the October 2022 zlib 1.2.13 patch (open CMake request from 2025 unanswered); BSD-3-Clause and a single function, easy to vendor, but you will need to re-port it to each new zlib release yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Wiki gives first-party times against original zlib with CPU model (i7-4702MQ) and compiler (VS 2019), and the repo ships the test application and test.sh, but optimization flags are not stated and the main datasets are the author's private files, so not A; first-party so C.
- **Verifier notes:** All level-9 numbers match the wiki; added the Silesia level 5/1 rows that show almost no gain outside level 9. Metadata (BSD-3-Clause, 146 stars, 25 forks, last commit 2022-10-14, abandoned) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party wiki table
- **Pages the verifier opened:**
  - <https://github.com/gildor2/fast_zlib/wiki>
  - <https://raw.githubusercontent.com/gildor2/fast_zlib/HEAD/README.md>
  - <https://github.com/gildor2/fast_zlib>
  - <https://github.com/gildor2/fast_zlib/commits>
- **Sources the enricher read:**
  - <https://github.com/gildor2/fast_zlib>
  - <https://github.com/gildor2/fast_zlib/wiki>
  - <https://github.com/gildor2/fast_zlib/issues?q=is%3Aissue>
  - <https://github.com/gildor2/fast_zlib/issues/3>
  - <https://github.com/gildor2/fast_zlib/issues/5>
  - <https://github.com/gildor2/fast_zlib/issues/8>
  - <https://github.com/gildor2/fast_zlib/tree/master/zlib>
  - <https://raw.githubusercontent.com/gildor2/fast_zlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/gildor2/fast_zlib/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/gildor2/fast_zlib/HEAD/build.sh>
  - <https://raw.githubusercontent.com/gildor2/fast_zlib/HEAD/test.sh>
  - <https://raw.githubusercontent.com/gildor2/fast_zlib/HEAD/Sources/match.h>
  - <https://raw.githubusercontent.com/gildor2/fast_zlib/HEAD/Sources/zlib_1.2.13.patch>
  - <https://raw.githubusercontent.com/madler/zlib/v1.3.1/deflate.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/gildor2/fast_zlib`) · [data/wave9/enrich/raw/github_com_gildor2_fast_zlib.json](../../../data/wave9/enrich/raw/github_com_gildor2_fast_zlib.json) (enrichment confidence 0.8)

</details>
