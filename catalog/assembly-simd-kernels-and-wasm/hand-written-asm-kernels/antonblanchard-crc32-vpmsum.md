# crc32-vpmsum (POWER8 vpmsum CRC32 and CRC32C in hand-written assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0-or-later OR Apache-2.0` · 🔴 abandoned

> POWER8+ vpmsum carry-less-multiply CRC32/CRC32C kernel in assembly (and intrinsics C); 41x a slice-by-8 table CRC on 32 kB.

| | |
|---|---|
| **Beats** | slice-by-8 table-driven CRC32 in C (based on Linux kernel lib/crc32.c, shipped in the repo as slice_by_8_bench.c, linked into the same crc32_bench.c driver); it computes the big-endian, non-reflected 0x04C11DB7 CRC rather than the reflected CRC32C (0x1EDC6F41) the default vpmsum build computes |
| **Claimed result** | The vpmsum accelerated CRC is 'just over 41x faster' than slice-by-8: 2.937 seconds (crc32_bench) vs 122.220 seconds (slice_by_8_bench) for 5 000 000 x 32 kB. About 52 GiB/s or 13.6 bytes/cycle on a 4.1 GHz POWER8 (theoretical limit 16 bytes/cycle). The kernel btrfs write test is 3.8x faster. |
| **Workload** | CRC32C (polynomial 0x11EDC6F41) over a 32 kB buffer, 5 000 000 iterations, L1-resident, timed with the shell time command; separate kernel test of btrfs writes to a ramdisk. |
| **Metric** | throughput |
| **Hardware** | 4.1 GHz POWER8 (exact model not stated) |
| **Compiler and flags** | Makefile CFLAGS: -m64 -g -O2 -mcpu=power8 -mcrypto -mpower8-vector -maltivec -mvsx (assembly built with -m64 -g); gcc is implied by the README but no compiler version is stated |
| **Adoption** | 33 stars; its crc32c-vpmsum code (Copyright 2015 Anton Blanchard, IBM) is in mainline Linux as lib/crc/powerpc/crc32c-vpmsum_asm.S |
| **Last commit** | 2020-03-26 |
| **Links** | [repository](https://github.com/antonblanchard/crc32-vpmsum) · [benchmark](https://github.com/antonblanchard/crc32-vpmsum) |

## Verdict

First-party README run: 5,000,000 CRC32C passes over one 32 kB L1-resident buffer took 2.937 s with the vpmsum assembly versus 122.220 s for a Linux-kernel-derived slice-by-8 C table CRC (different polynomial, Makefile -O2, compiler version unstated), about 41.6x, or 52 GiB/s and 13.6 bytes/cycle on an unnamed 4.1 GHz POWER8, timed with shell `time`.

## Use it when

- CRC32C (iSCSI, ext4/btrfs, Ceph, RocksDB style) or zlib/Ethernet CRC32 on IBM POWER8, POWER9 or POWER10 Linux, buffers of hundreds of bytes and up.
- Storage or network paths that checksum 4 kB to multi-MB blocks, where a table-driven CRC costs about 3 cycles per byte on POWER8 (0.33 bytes/cycle in the README's slice-by-8 run).
- You need a non-standard 32-bit polynomial accelerated: crc32_constants generates the folding and Barrett constants for any polynomial, reflected or not.
- Codebases that cannot pull in a whole crypto or compression library and want a small, dual-licensed (Apache-2.0 or GPL-2.0+) source drop.

## Skip it when

- Any non-POWER target, or POWER7 and older: the code needs the ISA 2.07 vpmsum instructions and has no portable fallback beyond a byte-wise table loop; check AT_HWCAP2 & PPC_FEATURE2_VEC_CRYPTO at run time yourself.
- Tiny inputs: below 31 bytes the wrapper runs a one-byte-per-step table loop, slower than slice-by-8; the Linux kernel's glue only enters the vector path at 528 bytes or more (VECTOR_BREAKPOINT 512 plus 16) and uses the table code below that.
- If you already use zlib-ng (arch/power/crc32_power8.c), Go's hash/crc32 on ppc64le, the Linux kernel, Ceph or RocksDB on POWER: each ships a derived copy of this code, so vendoring it again gains nothing.
- You need CRC-64, CRC-16/T10-DIF or crc32_combine: the generator covers 32-bit CRCs only and there is no combine function (issue #10 asked for one).
- Projects that need active upstream maintenance: no commits since 2020-03-26.

## How it is fast

CRC folding with carry-less multiplication: the main loop keeps 8 independent 16-byte accumulators (8 x 16 B per iteration) to hide the 6-cycle vpmsumd latency at one issue per cycle, folds up to 32 kB (MAX_SIZE) down to 1024 bits with precomputed x^n mod P constants, reduces 1024 bits to 64, then finishes with a fixed-point Barrett reduction. Bit-reflected CRCs are handled by loading bytes reversed (vperm) instead of reflecting bits. Unaligned heads, tails and inputs under 31 bytes go through a byte-at-a-time Sarwate table loop in the C wrapper; inputs of 16 to 255 aligned bytes use a separate short path with per-length constants.

## Compared with alternatives

Pick it over libgcrypt, Nettle or CRYPTOGAMS when you need only a POWER CRC32/CRC32C (or a custom 32-bit polynomial) as a few vendorable files rather than a whole crypto library; none of the other catalogued hand-written kernels in this category targets CRC on POWER.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at run time; the constants header is generated at build time by the repo's crc32_constants tool (buildable on non-POWER hosts for cross builds) |
| **Minimum toolchain** | GCC or Clang targeting POWER8 with -mcpu=power8 -mcrypto -mpower8-vector -maltivec -mvsx (Clang 7+ needed the 2020 workaround in clang_workaround.h); exact minimum versions not documented |
| **Platforms** | ppc64 and ppc64le Linux, POWER8 or later (vpmsum required); big- and little-endian both handled |
| **Thread safety** | Stateless pure function over caller memory (running CRC passed in and returned), so reentrant; not otherwise documented |
| **Drop-in for the baseline** | partial: same CRC result as a table-driven CRC for the polynomial the header was generated for, but under its own function name and signature, and only after generating constants per polynomial; the repo's slice-by-8 baseline computes a different CRC (big-endian 0x04C11DB7) than the default build (reflected CRC32C) |

## Gotchas

- Only one size was ever measured: the 41x figure is for a 32 kB page-aligned buffer, which is exactly the kernel's MAX_SIZE fold block (the best case, one block, no head or tail work); no numbers exist for small, unaligned or multi-block inputs, and the repo's own vec_crc32_bench (intrinsics C) has no published figure, so the gain of hand-written assembly over the intrinsics version is unknown.
- The baseline is slice-by-8 for a different polynomial and bit order (big-endian Ethernet CRC32 versus reflected CRC32C) built at the Makefile's -O2; it ran at about 1.34 GB/s (0.33 bytes/cycle, derived from page data), so a stronger table method such as slice-by-16 or zlib's braided CRC would narrow the gap. The slice-by-8 harness was refactored in 2017 (commit aadb491) after the README numbers, but its inner loop is unchanged.
- The 3.8x btrfs figure in the README does not match the Linux commit 6dd7a82cc54e message, which (per search-result text, page not opened) says 'over 3.7x faster' for a dd 4 GiB btrfs write test.
- The assembly saves non-volatile vector and GPR registers below the stack pointer (in the ABI's protected zone) and reads constants TOC-relative through r2; Ceph's separate crc32c_ppc_fast_zero_asm.S, not this repo's crc32.S, broke with a relocation-out-of-range error in shared libraries (issue #14, fixed in ceph#59558). The intrinsics C version gave wrong results on big-endian ppc64 with Clang until commit c520cfb (2018).

## Known shortcomings

- Compiler and POWER8 model unstated; the slice-by-8 baseline uses a different polynomial (big-endian 0x04C11DB7 vs CRC32C) and is slow (about 0.33 B/cycle, derived); no number for the repo's own intrinsics version; the code lives in mainline Linux lib/crc/powerpc/crc32c-vpmsum_asm.S.
- Enricher: the 41x was measured at one size only (a 32 kB page-aligned buffer, exactly the MAX_SIZE fold block, the best case) against slice-by-8 for a different CRC (big-endian Ethernet vs reflected CRC32C) built -O2 at about 0.33 bytes per cycle; the repo's own vec_crc32_bench has no published figure; the Linux kernel uses the vector path only from 528 bytes (VECTOR_BREAKPOINT 512) and its commit 6dd7a82cc54e claims 'over 3.7x' for btrfs; derived copies live in Linux lib/crc/powerpc, Go hash/crc32 ppc64le, zlib-ng, Ceph and RocksDB.

## Caveats and trade-offs

First-party numbers from a loop of 5,000,000 calls on a 32 kB L1-resident buffer timed with shell 'time'; compiler version and exact POWER8 model unstated, so tier C although the benchmark source is public. The baseline is a table-driven C slice-by-8 for a different polynomial and bit order (big-endian 0x04C11DB7 versus reflected CRC32C), equivalent work per byte but not the same checksum; it runs at about 1.34 GB/s, roughly 0.33 bytes/cycle at 4.1 GHz (derived from page data), so it is a modest baseline. No compiler auto-vectorized or carry-less-multiply C version is timed against the assembly: the repo's own vec_crc32.c intrinsics version of the same algorithm has a vec_crc32_bench target but no published figure, so the win is not attributable to hand-written assembly versus C. The btrfs 3.8x figure is a kernel-side ramdisk test with no details. Hardware is old and the repo has not been updated since 2020-03-26.

POWER8 and later only (needs the vpmsum vector crypto instructions). Constants are generated by make for a chosen CRC polynomial (CRC32C or Ethernet CRC32 shown), so each polynomial needs its own constants header and renamed symbols. Two variants ship: pure assembly (crc32.S plus crc32_wrapper.c) and a gcc vector-intrinsics version (vec_crc32.c).

## Maintenance

Dormant since 2020-03-26 (54 commits, one open issue about a Ceph-side file) but small, dual Apache-2.0/GPL-2.0+ licensed and copyable; the same algorithm lives on, maintained, in mainline Linux (lib/crc/powerpc), Go hash/crc32, zlib-ng, Ceph and RocksDB.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** README Performance section shows slice_by_8_bench 122.220 s versus crc32_bench 2.937 s (32 kB x 5,000,000), 'just over 41x faster', on a 4.1 GHz POWER8; the benchmark code (crc32_bench.c, slice_by_8_bench.c) and Makefile flags are public, but the compiler and exact CPU model are not stated, so not A; first-party, so C.
- **Verifier notes:** Numbers match the README (122.220/2.937 = 41.6x; 52 GiB/s and 13.6 bytes/cycle consistent with 32 kB x 5M in 2.937 s). Main shortcomings: compiler and CPU model unstated, baseline is a different CRC polynomial at modest speed, no comparison with the repo's own intrinsics C version. Not a duplicate of the wave 7 CRC entries (those are x86/ARM kernels).
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-106 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/README.md>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/Makefile>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/crc32_bench.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/slice_by_8_bench.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/LICENSE.TXT>
  - <https://github.com/antonblanchard/crc32-vpmsum>
  - <https://github.com/antonblanchard/crc32-vpmsum/commits/master>
  - <https://raw.githubusercontent.com/torvalds/linux/master/lib/crc/powerpc/crc32c-vpmsum_asm.S>
- **Sources the enricher read:**
  - <https://github.com/antonblanchard/crc32-vpmsum>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/README.md>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/Makefile>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/crc32_bench.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/slice_by_8_bench.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/crc32_wrapper.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/crc32.S>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/vec_crc32.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/crc32_constants.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/crc32_test.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/crc32_two_implementations.c>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/ppc-opcode.h>
  - <https://raw.githubusercontent.com/antonblanchard/crc32-vpmsum/HEAD/LICENSE.TXT>
  - <https://github.com/antonblanchard/crc32-vpmsum/commits/master>
  - <https://github.com/antonblanchard/crc32-vpmsum/commit/aadb491>
  - <https://github.com/antonblanchard/crc32-vpmsum/issues?q=is%3Aissue>
  - <https://github.com/antonblanchard/crc32-vpmsum/issues/14>
  - <https://raw.githubusercontent.com/torvalds/linux/master/lib/crc/powerpc/crc32.h>
  - <https://raw.githubusercontent.com/golang/go/master/src/hash/crc32/crc32_ppc64le.s>
  - <https://raw.githubusercontent.com/zlib-ng/zlib-ng/develop/arch/power/crc32_power8.c>
  - <https://raw.githubusercontent.com/facebook/rocksdb/main/util/crc32c_ppc_asm.S>
  - <https://raw.githubusercontent.com/ceph/ceph/main/src/common/crc32c_ppc_asm.S>
  - <https://raw.githubusercontent.com/MariaDB/server/main/mysys/crc32/crc32_ppc64.c>
  - WebSearch snippet: git.beagleboard.org mirror of Linux commit 6dd7a82cc54e 'crypto: powerpc - Add POWER8 optimised crc32c' (page not opened)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/antonblanchard/crc32-vpmsum`) · [data/wave13/enrich/raw/github_com_antonblanchard_crc32_vpmsum.json](../../../data/wave13/enrich/raw/github_com_antonblanchard_crc32_vpmsum.json) (enrichment confidence 0.8)

</details>
