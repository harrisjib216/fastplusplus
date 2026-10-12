# copies-and-fills (libcofi_rpi.so)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly` · `LGPL-2.1` · 🔴 abandoned

> ARMv6 assembly memcpy and memset for the original Raspberry Pi, LD_PRELOADed over the generic libc versions.

| | |
|---|---|
| **Beats** | generic libc memcpy and memset on Raspberry Pi (ARM) |
| **Claimed result** | memcpy reaches performance parity with generic libc at around \~150 byte copies and 'eventually gains 2-3x throughput, especially when the source buffer is uncached' (up to 680 MB/s, effective 339 MB/s copy); memset reaches parity at around 100 bytes and peaks at 1390 MB/s, '\~7x faster than the libc version' |
| **Workload** | Modified ssvb-membench with random numbers, iterating over sizes and source/destination alignments; memcpy and memset on a Raspberry Pi. |
| **Metric** | throughput |
| **Hardware** | Raspberry Pi (model and CPU not stated in the README; the notes mention a single-issue core) |
| **Adoption** | 72 stars, 9 forks; packaged as libcofi (libcofi_rpi.so) in Buildroot (package/libcofi, e.g. 2017.08) and Exherbo (sys-rpi/copies-and-fills), and shipped by Arch Linux ARM until arm-mem replaced it (search snippets only) |
| **Last commit** | 2012-08-03 |
| **Links** | [repository](https://github.com/simonjhall/copies-and-fills) · [benchmark](https://github.com/simonjhall/copies-and-fills) |

## Verdict

The 2012 README reports runs of a modified, unpublished ssvb-membench (random sizes and source/destination alignments) on an unnamed Raspberry Pi against the distribution's generic libc memcpy and memset (version not stated). memcpy reaches parity at about 150 bytes and gains 2-3x later, peaking at 680 MB/s (339 MB/s effective copy); memset reaches parity at about 100 bytes and peaks at 1390 MB/s, about 7x libc. There are no tables, no compiler details and no CPU model.

## Use it when

- 32-bit Linux on an ARM1176 board (original Raspberry Pi; the README names no model) where a profile shows memcpy or memset on buffers well above \~150 bytes
- Copies from uncached or streaming source buffers, where the README says the 2-3x gain shows up
- Large fills: memset reaches libc parity at about 100 bytes and peaked at 1390 MB/s in the author's runs
- Old Buildroot or Exherbo images that already package libcofi, as a no-recompile speedup
- As compact reference code (about 440 lines of assembly) for LDM/STM plus PLD copy loops on in-order ARM cores

## Skip it when

- Raspberry Pi 2 and later, other ARMv7 cores or AArch64: the code is tuned for the single-issue ARM1176 and is 32-bit only; Raspbian and Arch Linux ARM moved to bavison/arm-mem
- Workloads dominated by small copies: every size below 32 bytes except exactly 4 and 8 goes through a backward byte-at-a-time loop, and the README puts parity with libc at about 150 bytes for memcpy
- When you need memmove, memcmp, strlen or the EABI __aeabi_\* entry points: only memcpy and memset exist
- When you need reproducible evidence: the modified ssvb-membench harness, result tables, libc version and board model were never published
- Statically linking into proprietary code: the source is LGPL-2.1 (no 'or later'), and there is no LICENSE file in the repo

## How it is fast

memcpy byte-aligns the destination to 4 bytes, steps a word at a time to 32-byte destination alignment, then moves 32 bytes per iteration with paired 4-register LDMIA/STMIA and a PLD issued 128 bytes ahead of the source, which the README calls the key to the gain on the single-issue ARM1176 core. A misaligned source is read as aligned words and merged with LSR/ORR shifts in three specialised loops (offset 1, 2 or 3; the inner loop is derived from the glibc ARM port). memset replicates the byte into a word, aligns the destination the same way and writes 32 bytes per iteration as two 16-byte STMIAs, which the README measured at 1300-1400 MB/s against 1000-1100 MB/s for one 32-byte store.

## Compared with alternatives

Pick it over bavison/arm-mem only if you want the smallest LGPL two-function replacement for an ARM1176 board or readable reference code; arm-mem is its successor on Raspbian, also covers memmove, memcmp and strlen, and has ARMv7 variants (neither publishes numbers against glibc). tinymembench is the benchmark family its harness came from, not a library, and hglm/test-arm-kernel-memcpy targets the kernel's copies rather than userland libc.

## Integration

| | |
|---|---|
| **Form** | shared lib (libcofi_rpi.so via LD_PRELOAD or /etc/ld.so.preload); also usable as a source-drop of two .S files |
| **Dependencies** | none (GNU as and a C compiler driver to link the .so) |
| **Minimum toolchain** | GNU binutils assembling in ARM (not Thumb) mode with pre-UAL conditional mnemonics such as ldrgtb/strgeb; ARMv5TE+ for PLD, ARMv6 hardware unaligned access for the 4- and 8-byte paths |
| **Platforms** | 32-bit ARM Linux, tuned for ARMv6 ARM1176 (BCM2835); no AArch64, no x86 |
| **Thread safety** | Reentrant: no global state, registers and stack only (from the source) |
| **Drop-in for the baseline** | partial — same memcpy/memset signatures and return value via LD_PRELOAD, but only calls bound through the dynamic memcpy/memset symbols are redirected; compiler-inlined copies, __aeabi_memcpy/__aeabi_memset and memmove are untouched |

## Gotchas

- 4- and 8-byte copies use plain LDR/STR on possibly unaligned pointers ('we're relying on the cpu misalignment support here'); this needs the ARMv6 hardware unaligned mode Linux enables and is unsafe on bare metal in legacy alignment mode or on device memory.
- Sizes 1-31 bytes (other than 4 and 8) are copied backwards one byte at a time with no prefetch, so the small-copy path is slower than libc by the author's own parity figures.
- The libcofi_rpi.so Raspbian preloaded by default included a third-party fork's memcmp that crashed under QEMU (issue #4; a 2014 QEMU list thread, search snippet only, blames SETEND, which this repo never uses), so emulated Raspbian images commonly commented out /etc/ld.so.preload.
- Harness flaw: the README admits that enabling the pld path in the libc source 'certainly does improve' libc, so part of the 2-3x and 7x gaps may reflect a distribution libc built without prefetch rather than a better algorithm; the figures are peak MB/s ('speeds of up to'), not averages, and the harness is not public.

## Known shortcomings

- First-party 2012 README prose with no CPU model, compiler, flags, libc version or result tables; the modified ssvb-membench harness is not in the repo; parity with libc only from 100-150 bytes, so small copies gain nothing; the about 7x memset figure is a peak MB/s, not an average.
- The assembly reads correct; no bug behind the numbers. Harness flaw: the README admits libc 'certainly does improve' with its pld path enabled, so the 2-3x and 7x gaps may come from a distribution libc built without prefetch; the figures are peak MB/s and the harness is unpublished. Sizes 1-31 bytes (except 4 and 8) use a backward byte loop; 4 and 8 bytes use unaligned LDR/STR; the Raspbian-preloaded build included a fork's memcmp that crashed QEMU (issue #4).

## Caveats and trade-offs

First-party claim in a 2012 README with no CPU model, compiler, flags, libc version or result tables; the benchmark harness is a modified copy of ssvb-membench that is not in this repo. The README says the library only reaches parity with libc at 100-150 bytes, so small copies gain nothing. The \~7x memset figure is a peak MB/s compared to libc, not a general average. Hardware is unnamed; in July 2012 the only shipping board was the Raspberry Pi Model B (BCM2835, ARM1176JZF-S), so the code is ARMv6-specific (inference). Licence is stated as LGPL version 2.1 without 'or later' in the README and asm headers; there is no LICENSE file. Last commit 2012-08-03; Raspbian and Arch Linux ARM later moved to Ben Avison's arm-mem (libarmmem.so), and a commenter reported no gain on Raspberry Pi 3B/3B+ (search snippets only). The Makefile still names the pre-rename lowercase .s files.

Hand-written ARM assembly (memcpy.s, memset.s) tuned for the original single-issue Raspberry Pi core; used by setting LD_PRELOAD=/full/path/to/libcofi_rpi.so. The misaligned-copy inner loop is derived from the GNU libc ARM port, hence LGPL. Not portable to other ARM cores or to 64-bit.

## Maintenance

Abandoned since 2012-08-03 (13 commits, 4 closed issues); LGPL-2.1, two small .S files that are easy to vendor, but superseded on Raspbian and Arch Linux ARM by bavison/arm-mem.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README prose (2012) compares against the generic libc memcpy/memset with peak MB/s figures and parity points, but gives no result tables, CPU model, compiler, flags or libc version, and the modified ssvb-membench harness is not in the repo.
- **Verifier notes:** README numbers match the record (parity at \~150 B memcpy and \~100 B memset, 2-3x memcpy, 680 MB/s, 1390 MB/s memset \~7x). Shortcomings to record: first-party prose only, no hardware/compiler/libc details, harness not public, ARMv6-only and superseded by arm-mem, abandoned since 2012. Lead: bavison/arm-mem (successor used by Raspbian as libarmmem.so) is not in the catalog.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 13), file only (agent killed by the spend limit before reporting); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/simonjhall/copies-and-fills>
  - <https://github.com/simonjhall/copies-and-fills/commits>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/README.md>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/Makefile>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/memcpy.S>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/memset.S>
- **Sources the enricher read:**
  - <https://github.com/simonjhall/copies-and-fills>
  - <https://github.com/simonjhall/copies-and-fills/commits>
  - <https://github.com/simonjhall/copies-and-fills/issues?q=is%3Aissue>
  - <https://github.com/simonjhall/copies-and-fills/issues/1>
  - <https://github.com/simonjhall/copies-and-fills/issues/4>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/README.md>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/Makefile>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/memcpy.S>
  - <https://raw.githubusercontent.com/simonjhall/copies-and-fills/HEAD/memset.S>
  - <https://github.com/ssvb/ssvb-membench>
  - WebSearch: libcofi_rpi.so raspbian ld.so.preload replaced by libarmmem arm-mem (snippets from archlinuxarm.org forum, forum.snapcraft.io and a lore.kernel.org QEMU thread; archlinuxarm.org and lore.kernel.org fetches failed with ENOTFOUND)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/simonjhall/copies-and-fills`) · [data/wave13/enrich/raw/github_com_simonjhall_copies_and_fills.json](../../../data/wave13/enrich/raw/github_com_simonjhall_copies_and_fills.json) (enrichment confidence 0.7)

</details>
