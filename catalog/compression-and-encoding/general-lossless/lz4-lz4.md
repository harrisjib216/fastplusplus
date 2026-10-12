# LZ4

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> In-memory block/frame compressor beating zlib deflate on speed, trading compression ratio for GB/s decode.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | LZ4 default (v1.9.0): 780 MB/s compression, 4970 MB/s decompression, ratio 2.101 vs zlib deflate 1.2.11 -1: 100 MB/s compression, 415 MB/s decompression, ratio 2.730 (\~7.8x faster compression, \~12.0x faster decompression, derived from page data, at a lower ratio). vs Snappy 1.1.4: 565 MB/s / 1950 MB/s, ratio 2.091 (LZ4 \~1.38x faster compression, \~2.55x faster decompression, derived from page data). |
| **Workload** | Single-thread in-memory compression/decompression speed and ratio on the Silesia corpus, using lzbench. |
| **Metric** | throughput |
| **Hardware** | Core i7-9700K @ 4.9GHz (w/ turbo boost), Ubuntu 64-bit (kernel 4.18.0-17) |
| **Compiler and flags** | GCC v8.2.0 (lzbench build; lzbench version and optimization flags not stated in README) |
| **Adoption** | 12.1k stars; used in Linux kernel, ZFS, FreeBSD, and many package/container systems |
| **Last commit** | 2026-06-01 |
| **Links** | [repository](https://github.com/lz4/lz4) · [benchmark](https://github.com/lz4/lz4) |

## Verdict

First-party lzbench run (LZ4 v1.9.0, GCC 8.2.0, Core i7-9700K @4.9GHz, Ubuntu 4.18.0-17) reports LZ4 default at 780/4970 MB/s (compress/decompress) and ratio 2.101, versus zlib deflate 1.2.11 -1 at 100/415 MB/s and ratio 2.730 — roughly 7.8x faster compression and 12.0x faster decompression at a lower ratio. An independent lzbench 2.0.1 run (gcc 14.2.0, AMD EPYC 9554) corroborates the direction: lz4 1.10.0 at 577/3716 MB/s vs zlib 1.3.1 -1 at 93.0/323 MB/s.

## Use it when

- Hot-path in-memory compression where decompression speed dominates (caches, IPC payloads, columnar/log formats)
- Read-heavy data where you decompress far more often than you compress
- Need dictionary compression for many small, similar payloads (frame API supports a 64KB dictionary window)
- Embedded/freestanding targets: single C90 source pair (lz4.c/lz4.h), optional LZ4_FREESTANDING build removes libc dependency
- Already have LZ4_HC available when you need a higher ratio at the same decompression speed but slower compression

## Skip it when

- Compression ratio matters more than speed: zlib -6 (3.099) and zstd both beat LZ4's 2.101 default ratio
- Need a drop-in replacement for a zlib/deflate API surface — LZ4's API and block/frame formats are different
- Want one universal knob for ratio/speed tradeoffs across a wide range — zstd's level range is broader than LZ4's acceleration + HC split
- Pulling in a released package manager build: the current tagged release (v1.10.0, 2024-07-22) predates a 2025-06-01 fix for unhandled NULL-pointer args in lz4frame (CVE-2025-62813); only the dev branch has it
- Need built-in multithreading: LZ4 itself is single-thread per call; parallelism is the caller's responsibility

## How it is fast

LZ4 uses a byte-oriented LZ77 variant with a simple hash-chain match finder and no entropy coding stage (no Huffman/range coding like deflate), so both compression and decompression are dominated by cheap memcpy-style literal/match copies instead of bit-level decoding. Decompression in particular is just a sequence of length-prefixed copy operations, which is why it reaches multi-GB/s per core. A tunable "acceleration" factor lets the compressor skip more match-search work for more speed at a lower ratio, and LZ4_FAST_DEC_LOOP enables an optimized decode loop on x86/x64/aarch64.

## Compared with alternatives

Pick LZ4 over Zstandard when decompression throughput and minimal-dependency portability (down to freestanding C90) matter more than ratio; zstd's -1 level already beats LZ4's ratio (2.883 vs 2.101) at somewhat lower speed, and zstd exposes a much wider ratio/speed level range, so pick zstd when you want one tunable knob spanning LZ4-like speed to gzip-beating ratio.

## Integration

| | |
|---|---|
| **Form** | source-drop (lz4.c+lz4.h minimum) \| static lib \| shared lib |
| **Dependencies** | none for block API; frame API (lz4frame) additionally needs xxhash.c/xxhash.h from the same repo; lz4file adds a &lt;stdio.h&gt; dependency |
| **Minimum toolchain** | C90 (with long long and optional variadic macros); C99+ used opportunistically (e.g. restrict) with a C90 fallback |
| **Platforms** | any C90 target incl. 32-bit and freestanding/embedded (LZ4_FREESTANDING=1 drops libc); LZ4_FAST_DEC_LOOP auto-enabled on x86, x64, aarch64 |
| **Thread safety** | not documented in lz4.h beyond context objects (LZ4_stream_t / LZ4_streamDecode_t) being per-call state the caller owns; no explicit thread-safety statement found |
| **Drop-in for the baseline** | partial — different API and wire format from zlib, not a compile-time swap |

## Gotchas

- Block API (lz4.h) is not self-describing: caller must transmit/store the compressed size and a max decompressed-size bound separately
- Advanced/experimental symbols behind LZ4_STATIC_LINKING_ONLY are excluded from the shared-library ABI and can break between versions — static-link only
- Repo license is split by directory: lib/ is BSD-2-Clause, programs/ (CLI, tests) is GPL-2.0-or-later; check which files you actually vendor
- Open issue #1779 (as of 2026-08) flags the streaming-decompression "synchronized mode" docs as wrong/misleading — verify ring-buffer streaming behavior against source, not just the header comment

## Caveats and trade-offs

The license is split by directory: lib/ (the codec) is BSD-2-Clause, and the CLI, tests and examples are GPL-2.0-or-later. Both are OSI-approved, so the library is copyable. The numbers are reported first-party in the README from an lzbench run of LZ4 v1.9.0 against zlib 1.2.11. The compiler, CPU and OS are stated, but the compile flags and the lzbench version are not, so the evidence is not tier A. LZ4 wins on speed at a lower compression ratio than zlib -1 (2.101 vs 2.730). Independent corroboration: the lzbench README (lzbench 2.0.1, gcc 14.2.0, AMD EPYC 9554) lists lz4 1.10.0 at 577/3716 MB/s against zlib 1.3.1 -1 at 93.0/323 MB/s. License: the library (lib/) is BSD-2-Clause; the command-line programs (programs/) are GPL-2.0-or-later.

Lower compression ratio than zlib/zstd in exchange for very high speed, especially decompression; LZ4_HC trades compression speed for ratio while keeping decompression speed constant; acceleration factor tunable.

## Maintenance

Actively maintained (dev branch commit 2026-06-01) but the latest tagged release is v1.10.0 from 2024-07-22, so a NULL-pointer-arg fix (CVE-2025-62813, merged 2025-06-01) is not yet in any released tag; usability is 'copyable' since every file carries an OSI license (BSD-2-Clause in lib/, GPL-2.0-or-later elsewhere).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification A, tier now B.
- **Tier reason:** The README table uses lzbench, a public, well-known third-party suite, and states GCC 8.2.0 and a Core i7-9700K. However, it does not state the compile flags or the lzbench version, and the rule says missing flags means not A. This is B because the win comes from a well-known independent benchmark suite.
- **Verifier notes:** All numbers match the README Benchmarks table, and the ratios are correctly marked as derived. Usability changed from 'mixed' to 'copyable' because every file is under an OSI license (BSD-2-Clause or GPL-2.0-or-later) and none is unlicensed. last_commit is taken from the default branch 'dev' (2026-06-01); the 2026-07-01 value was the repo pushed_at date. [orchestrator 2026-09-24: license recorded as the library's BSD-2-Clause; CLI GPL noted in caveats]
- **Fields the verifier corrected:** `compiler_and_flags`, `usability`, `last_commit`, `caveats`, `license`
- **Pages the verifier opened:**
  - <https://github.com/lz4/lz4>
  - <https://github.com/lz4/lz4/blob/dev/LICENSE>
  - <https://github.com/lz4/lz4/blob/dev/lib/LICENSE>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/inikep/lzbench/blob/master/Makefile>
- **Sources the enricher read:**
  - <https://github.com/lz4/lz4>
  - <https://github.com/lz4/lz4/blob/dev/README.md>
  - <https://github.com/lz4/lz4/blob/dev/lib/README.md>
  - <https://github.com/lz4/lz4/blob/dev/lib/lz4.h>
  - <https://github.com/lz4/lz4/blob/dev/SECURITY.md>
  - <https://github.com/lz4/lz4/blob/dev/LICENSE>
  - <https://github.com/lz4/lz4/blob/dev/lib/LICENSE>
  - <https://github.com/lz4/lz4/blob/dev/programs/COPYING>
  - <https://github.com/lz4/lz4/blob/dev/INSTALL>
  - <https://github.com/lz4/lz4/blob/dev/CODING_STYLE>
  - <https://github.com/lz4/lz4/blob/dev/lib/Makefile>
  - <https://github.com/lz4/lz4/issues/1667>
  - <https://github.com/lz4/lz4/pull/1593>
  - <https://github.com/lz4/lz4/issues/1779>
  - <https://github.com/lz4/lz4/releases>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/lz4/lz4`) · [data/wave0-seed/enrich/raw/github_com_lz4_lz4.json](../../../data/wave0-seed/enrich/raw/github_com_lz4_lz4.json) (enrichment confidence 0.85)

</details>
