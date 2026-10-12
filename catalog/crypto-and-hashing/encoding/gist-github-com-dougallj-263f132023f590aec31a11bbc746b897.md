# Faster CRC32 on Apple M1 (dougallj, PMULL multi-chain)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> Single-file C++17 AArch64 CRC-32/CRC-32C kernel with 12 PMULL folding chains; about 2.5x zlib's crc32 on Apple M1.

| | |
|---|---|
| **Beats** | zlib crc32() function |
| **Claimed result** | The original 12-chain test code runs at 'about 70GB/s on the M1, reaching up to 75GB/s if the assembly is adjusted to always have valid fusion pairs', vs the zlib crc32 function at 'around 30GB/s' on the same M1 (\~2.3x, derived from page data). This gist is the 'slightly cleaner/faster version using inline assembly and C++ templates' and 'reaches \~76GB/s'. The CRC32X instruction's theoretical best case is 25.6GB/s. |
| **Workload** | CRC32/CRC32C throughput on large buffers (author profiled 128KB and up; the test harness uses 2 MiB) on the Apple M1. It uses PMULL/PMULL2+EOR folding with 12 independent latency chains, building on Intel's 2009 PCLMULQDQ folding technique. |
| **Metric** | throughput |
| **Hardware** | Apple M1, 3.2GHz |
| **Compiler and flags** | clang++ -std=c++17 -O3 (build comment in the companion test-code gist a15a0feac92e2126932b0fbe1de7863d/main.cpp; clang version not stated; this gist has no build line) |
| **Adoption** | 343 HN points; follow-on state-of-the-art (corsix/fast-crc32, already catalogued) is a direct descendant of this work |
| **Last commit** | 2022-06-06 |
| **Links** | [repository](https://gist.github.com/dougallj/263f132023f590aec31a11bbc746b897) · [benchmark](https://dougallj.wordpress.com/2022/05/22/faster-crc32-on-the-apple-m1/) |

## Verdict

On a 3.2 GHz Apple M1 the author measured zlib's crc32 (a separate, unpublished test of Apple's system zlib, version unknown) at about 30 GB/s; the companion 12-chain gist reached about 70-75 GB/s on a 2 MiB buffer (clang++ -std=c++17 -O3), and this cleaner template/asm version about 76 GB/s. corsix/fast-crc32 independently measured this gist at 77.55 GB/s on M1 (512 KiB default buffer) against 25.03 GB/s for Chromium zlib's scalar code and 26.57 GB/s for its vector code, but only 17.41 GB/s on Ampere Altra, where the Chromium scalar code wins at 22.68 GB/s.

## Use it when

- Bulk CRC-32 or CRC-32C over large buffers (the author profiled 128 KB and up; the test harness uses 2 MiB) on Apple M-series cores, where the checksum is the throughput bottleneck, e.g. zip/PNG/gzip writers or storage checksums on macOS/iOS.
- Studying or porting the N-chain PMULL+EOR folding technique: about 270 readable lines, with the constants derived by constexpr code rather than magic numbers.
- Arbitrary reflected 32-bit CRC polynomials on AArch64: pass the polynomial as a template parameter (NO_CRC_INSNS builds without the ARMv8 CRC instructions, using a table plus Barrett reduction).

## Skip it when

- Non-Apple ARM cores. The PMULL+EOR fusion it depends on is, per the author, probably unique to Apple CPUs. corsix/fast-crc32 measured it at 17.41 GB/s on Ampere Altra, slower than Chromium zlib's scalar CRC32X loop at 22.68 GB/s.
- x86 or any non-AArch64 target: there is no fallback path, since it includes arm_neon.h and uses PMULL inline asm unconditionally.
- Small or latency-sensitive buffers. Below 192 bytes (after 16-byte alignment) it drops to a single serial CRC32X chain, and the author warns its 5 ops per 16 bytes (vs 3 for CRC32X) can hurt when the checksum shares the core with other work.
- Shipping code that needs a clear license. The gist carries only an 'AS IS' warranty disclaimer and no license grant.
- When you want the fastest M1 result: the author's 2024 update points to corsix/fast-crc32 at 85.05 GB/s vs 77.55 GB/s for this gist.

## How it is fast

It uses Intel's 2009 carry-less-multiply folding ("Fast CRC Computation for Generic Polynomials Using PCLMULQDQ") ported to ARM PMULL/PMULL2, but with 12 independent 16-byte accumulators (192 bytes per iteration) instead of the usual 4. The chain count is sized to M1 Firestorm's latency: the Apple core fuses PMULL/PMULL2 with a following EOR into one 3-cycle uop, so each chain costs 6 cycles and 2 fused uops, and 12 chains fill the 4-per-cycle SIMD pipes. The fold step is inline asm to keep valid fusion pairs. The final 128-to-32-bit reduction uses two CRC32X/CRC32CX instructions, or a Barrett reduction for other polynomials.

## Compared with alternatives

corsix/fast-crc32 is the direct successor: it ships explicit license files, is about 10% faster on M1 (85.05 vs 77.55 GB/s by blending EOR3 and CRC32X) and covers x86 and non-Apple ARM, while crc-fast and crc32fast are packaged libraries. Pick this gist only as a compact, readable C++17 reference for 12-chain PMULL+EOR folding; for shipping code use corsix/fast-crc32.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (arm_neon.h, plus arm_acle.h unless NO_CRC_INSNS) |
| **Minimum toolchain** | C++17 (inline constexpr variables, if constexpr); written for clang: the inline asm uses Apple-dialect mnemonics (`pmull.1q`, `eor.16b`) and the code relies on implicit NEON vector-type conversions. The companion test gist builds with `clang++ -std=c++17 -O3`, clang version not stated. |
| **Platforms** | AArch64 with the crypto (PMULL) and, by default, CRC extensions; tuned for Apple M1 (Firestorm). Other AArch64 cores run it correctly but lose the fusion advantage. |
| **Thread safety** | Reentrant by code reading: a pure function over its arguments, with only constexpr tables and no mutable global state. Not documented by the author. |
| **Drop-in for the baseline** | partial — same zlib crc32 semantics (initial value 0, pre/post inversion, chainable calls), but the signature takes a non-const `uint8_t*` and `size_t` instead of zlib's `(uLong, const Bytef*, uInt)`. It is an unnamespaced C++-linkage function also named crc32, and there is no crc32_combine or other zlib API. |

## Gotchas

- It does not build as-is outside Apple clang. corsix/fast-crc32's vendored copy had to rewrite the asm to standard syntax (`pmull v0.1q, %[val].1d, %[consts].1d`), add the missing `#include <cstring>` for memcpy, add an extern "C" wrapper, and compile with `-march=armv8-a+crypto+crc -flax-vector-conversions` under g++ on Linux.
- Speed depends on fusion pairs, i.e. each PMULL immediately followed by its dependent EOR. The author reports about 70 GB/s without them and about 75 GB/s with them; the inline asm pins this order, so do not 'clean it up' into intrinsics without re-measuring.
- The final fold from 12 accumulators to one is serial (about 72 cycles, per the author's TODO), a fixed cost per call on top of the small-buffer fallback.
- This gist has no test or harness of its own. The companion gist's harness checks only one 2 MiB buffer against a slice-by-4 table, but corsix's bench.c (which checks every length from 1 to 4,160 bytes and every split point against a table CRC) runs this code before benchmarking it.

## Known shortcomings

- A gist, not a library: Apple M1 only (PMULL multi-chain), untouched since 2022-06-06. \~76 GB/s is this gist's own figure (70/75 GB/s from an earlier test gist); zlib is not in the harness, so the \~2.3x over zlib is derived. clang++ -O3.
- No license. Builds only with Apple clang as published (corsix had to add &lt;cstring&gt; and -flax-vector-conversions). Loses on Ampere Altra (17.41 vs 22.68 GB/s); inputs under 192 bytes take a serial path. Superseded by corsix/fast-crc32 (\~85 GB/s on M1).

## Caveats and trade-offs

Distributed only as GitHub gists with an 'AS IS' warranty disclaimer and no license grant. The zlib comparison was measured separately and is not in the published harness, which checks correctness against a slice-by-4 table CRC. The speed depends on PMULL+EOR fusion, which the author says is likely unique to Apple-designed CPUs. The author also says it may hurt performance on small buffers and that the test code is 'not suitable for real-world use as-is'. By the author's 2024 update it is superseded by corsix/fast-crc32 (85GB/s on M1, \~10% faster, already catalogued).

ARM64/NEON-specific technique (PMULL + fusion pairs tuned to Apple's execution ports); not portable to x86 as written.

## Maintenance

Abandoned: last edited 2022-06-06, and the author's 2024 blog update names corsix/fast-crc32 as the new state of the art. With no license grant it is a reference implementation, not code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are the author's own blog numbers on a named CPU (M1 at 3.2GHz). The companion test gist (a15a0fe, main.cpp) has a timing harness and a clang++ -O3 build line, but the harness does not run zlib: zlib's \~30GB/s was measured separately and its code is not published. The clang version is not stated either.
- **Verifier notes:** The blog numbers match the record. 70/75GB/s belong to the original test gist (a15a0fe), and the cleaner version under this record's URL reaches \~76GB/s. The gist file is crc32.cpp (C++ templates plus inline asm), so the record's language 'C' should be C++; that field is not correctable here. I changed maintenance to abandoned because the code was last touched 2022-06-06 and the author never calls it complete. HN story 31469295 has 343 points, as the record says.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `last_commit`, `maintenance_status`, `workload`, `caveats`
- **Shortcomings recorded by:** corsix/fast-crc32 independent run: 77.55 GB/s on M1 vs Chromium zlib 25-27 GB/s; Ampere Altra 17.41 vs 22.68 GB/s.
- **Pages the verifier opened:**
  - <https://gist.github.com/dougallj/263f132023f590aec31a11bbc746b897>
  - <https://dougallj.wordpress.com/2022/05/22/faster-crc32-on-the-apple-m1/>
  - <https://gist.github.com/dougallj/a15a0feac92e2126932b0fbe1de7863d>
  - <https://hn.algolia.com/api/v1/search?query=Faster%20CRC32%20on%20the%20Apple%20M1&tags=story>
- **Sources the enricher read:**
  - <https://gist.github.com/dougallj/263f132023f590aec31a11bbc746b897>
  - <https://gist.github.com/dougallj/a15a0feac92e2126932b0fbe1de7863d>
  - <https://dougallj.wordpress.com/2022/05/22/faster-crc32-on-the-apple-m1/>
  - <https://github.com/corsix/fast-crc32>
  - <https://github.com/corsix/fast-crc32/blob/main/README.md>
  - <https://github.com/corsix/fast-crc32/blob/main/third_party/dougallj.cpp>
  - <https://github.com/corsix/fast-crc32/blob/main/third_party/Makefile>
  - <https://github.com/corsix/fast-crc32/blob/main/Makefile>
  - <https://github.com/corsix/fast-crc32/blob/main/bench.c>
  - <https://hn.algolia.com/api/v1/items/31469295>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://gist.github.com/dougallj/263f132023f590aec31a11bbc746b897`) · [data/wave7/enrich/raw/gist_github_com_dougallj_263f132023f590aec31a11bbc746b897.json](../../../data/wave7/enrich/raw/gist_github_com_dougallj_263f132023f590aec31a11bbc746b897.json) (enrichment confidence 0.82)

</details>
