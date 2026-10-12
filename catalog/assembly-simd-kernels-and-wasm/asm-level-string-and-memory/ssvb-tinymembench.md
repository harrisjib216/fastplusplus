# tinymembench (NEON, prefetching and SSE2 copy and fill kernels against libc memcpy and memset)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C and assembly (ARM, AArch64, x86 SSE2, MIPS)` · `MIT` · 🔴 abandoned

> Memory bandwidth and latency benchmark whose NEON, ARM and SSE2 copy/fill kernels beat old ARM libc memcpy up to 2.2x.

| | |
|---|---|
| **Beats** | the libc memcpy and memset ('standard memcpy', 'standard memset') of each tested board's OS image |
| **Claimed result** | No headline claim; results are per-board wiki tables (ratios derived from page data). BeagleBone Black (Cortex-A8 AM3358 r2.1 at 1 GHz, tinymembench v0.4.9): standard memcpy 258.3 MB/s vs 'C copy prefetched (32 bytes step)' 505.1 MB/s (1.96x), 'ARM copy prefetched (wrap pld)' 508.4 MB/s (1.97x) and 'NEON copy prefetched (32 bytes step)' 563.5 MB/s (2.18x); standard memset 1511.9 MB/s is level with every custom fill (1510.6 to 1512.0 MB/s). Allwinner A13 (v0.2.9): standard memcpy 249.8 vs 'C copy prefetched (32 bytes step)' 406.5 MB/s (1.63x) and 'NEON unrolled copy' 499.9 MB/s (2.00x). Intel Core i7-8700T (v0.4.9): standard memcpy 16647.8 vs 'SSE2 nontemporal copy' 17273.1 MB/s (1.04x); standard memset 32815.6 vs 'SSE2 nontemporal fill' 41097.4 MB/s (1.25x). Raspberry Pi BCM2835 at stock 700 MHz with Raspbian 2015-01-31: libc memcpy 387.6 MB/s is level with the best custom copy (392.6 MB/s) and libc memset 1458.5 MB/s ties 'ARM fill (STM with 4 registers)' 1458.4 MB/s; on the same page's overclocked run with a custom 4.1.15 kernel, standard memcpy 307.9 vs 'C copy prefetched' 543.5 MB/s (1.77x). AMD Ryzen 7 9800X3D: standard memcpy 81381.2 vs best custom 'SSE2 copy prefetched (64 bytes step)' 81804.8 MB/s (1.005x, a tie), standard memset 156460.7 vs 'SSE2 fill' 162148.8 MB/s (1.04x), and the SSE2 nontemporal copy (32028.6 MB/s) is 2.5x slower than libc. |
| **Workload** | Sequential copy and fill bandwidth on large aligned blocks, reporting MB/s for libc memcpy and memset next to C, NEON, VFP, ARM LDM/STM, SSE2 and non-temporal copy and fill kernels with different prefetch strategies; the wiki holds 68 community-submitted boards and PCs. |
| **Metric** | throughput |
| **Hardware** | Per wiki page: ARM Cortex-A8 AM3358 at 1 GHz (BeagleBone Black), Allwinner A13, Intel Core i7-8700T (6 cores, DDR4-2666), Raspberry Pi BCM2835 and 60+ other boards and PCs |
| **Compiler and flags** | Not recorded on the wiki pages; the readme.txt build examples use CFLAGS=-O2 with a per-board -mcpu (for example -mcpu=cortex-a9, -mcpu=cortex-a8 -static) |
| **Adoption** | 418 stars; a sibling report says amd/aocl-libmem bundles it in its benchmark tooling |
| **Last commit** | 2017-02-14 |
| **Links** | [repository](https://github.com/ssvb/tinymembench) · [benchmark](<https://github.com/ssvb/tinymembench/wiki/BeagleBone-Black-(AM3358)>) |

## Verdict

Community wiki runs of the project's own harness (best MB/s over 32 MiB aligned buffers, compiler, flags and libc not recorded) show NEON prefetched copy at 563.5 MB/s against 258.3 MB/s for libc memcpy on a 1 GHz Cortex-A8 BeagleBone Black (2.18x) and NEON unrolled copy at 499.9 vs 249.8 MB/s on an Allwinner A13 (2.0x). Libc memset ties every custom fill on those ARM boards; on x86 the only gains are 1.04x (non-temporal copy) and 1.25x (non-temporal fill) on an i7-8700T, and on the Ryzen 9800X3D libc ties in a run that fits in L3.

## Use it when

- Characterising a new ARM, AArch64, MIPS or x86 board: it shows in one run whether the system libc memcpy/memset reaches the memory bus's achievable bandwidth or leaves a 1.5-2x gap that a prefetching or NEON copy would close.
- Choosing a copy strategy (prefetch distance, NEON vs LDM/STM, non-temporal vs cached stores) before writing or picking a memcpy for an embedded Linux image or a framebuffer driver; it also measures uncached framebuffer readback on ARM.
- Comparing against the 68 community result pages on the project wiki, which use the same harness and output format across boards from the Raspberry Pi 1 to recent desktop CPUs.
- Measuring random-access latency with and without transparent huge pages (MADV_HUGEPAGE) to see TLB costs.

## Skip it when

- As a memcpy or memset replacement: the kernels assume sizes in whole blocks and aligned pointers, have no small-copy, misalignment or overlap handling, and are not exported as a library.
- Modern x86 with a current glibc: on the i7-8700T libc memcpy is within 4% of the best kernel (non-temporal copy) and on the Ryzen 9800X3D libc memcpy ties the best SSE2 copy, so there is nothing to copy across.
- Machines whose last-level cache holds 64 MiB or more: the two 32 MiB buffers are fixed at compile time, so the 'memory bandwidth' rows measure cache bandwidth there (see gotchas).
- Multi-threaded bandwidth: the program is single-threaded (multi-thread support is an open request, issue #22), so it understates total DRAM bandwidth on multi-core parts.
- Clang or MSVC toolchains: clang fails to assemble the .S files (issue #20, open), and Windows builds go only through mingw/msys (Win64 via mingw64 since 2017-02-13).

## How it is fast

The faster rows use software prefetch a fixed 256 bytes ahead (pld on ARM, prefetchnta on x86, prfm on AArch64), wide NEON vld1/vst1 transfers of 32-128 bytes per iteration with 256-bit alignment hints, and non-temporal stores (movntdq, stnp) that skip the read-for-ownership of the destination. On 2012-2017 Cortex-A8 and Allwinner A13 boards the libc memcpy issued no prefetch, so a prefetching loop roughly doubled copy bandwidth; the 2-pass rows stage 2 KB blocks through L1 to test whether separating reads and writes helps.

## Compared with alternatives

Pick tinymembench to diagnose whether a board's libc copy is leaving bandwidth on the table; to actually ship faster copies, use a packaged replacement such as copies-and-fills (libcofi_rpi) or arm-mem on 32-bit ARM, or Arm Optimized Routines on AArch64. rvv-bench plays the same benchmark-program role for RISC-V Vector boards, which tinymembench does not support (RISC-V is an open request, issue #31).

## Integration

| | |
|---|---|
| **Form** | source-drop (standalone benchmark program built with make) |
| **Dependencies** | libc and libm; Linux /dev/fb0 optional for framebuffer tests |
| **Minimum toolchain** | GCC with GNU as (C89-style C plus GNU assembler macros); clang assembly fails per issue #20 |
| **Platforms** | x86 and x86-64 (SSE2; Linux and mingw Win64), 32-bit ARM (ARMv4 to ARMv7, VFP, NEON), AArch64, MIPS32 |
| **Thread safety** | single-threaded benchmark; not applicable as a library |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw on large-cache CPUs: main.c fixes the buffers at #define SIZE (32 \* 1024 \* 1024) with no compile-time override (unlike MAXREPEATS), so src plus dst is 64 MiB. The Ryzen 7 9800X3D has 96 MB of L3, and its wiki page reports libc memcpy at 81381.2 MB/s copied (about 163 GB/s of read plus write traffic) and memset at 156460.7 MB/s, both above the 96 GB/s peak of the page's dual-channel DDR5-6000 (derived from page data). That page measures L3, not DRAM, and its 'non-temporal copy 2.5x slower than libc' result reflects non-temporal stores going to DRAM while cached copies stay in L3, not a general verdict on modern x86.
- C-kernel rows are compiler-sensitive: issue #7 showed forward and backward C copies swapping 3.5-4x between gcc 4.6.3 and 4.7.2 on a Cortex-A7, and store order was only forced with volatile on 2016-03-29 (v0.4). The Allwinner A13 run (v0.2.9) and the Raspberry Pi runs (v0.3.9) predate that fix, and no wiki page records compiler, flags or libc version, so cite the NEON/ARM assembly rows rather than the C rows.
- Kernels are not safe on arbitrary input: loops are do-while style (subs/jg), so size 0 still writes one block; sizes are processed in 32, 64 or 128-byte steps and the NEON unrolled copy rounds size down with bic #127, silently dropping a tail; NEON stores carry :256 alignment hints and SSE2 uses movdqa, which fault on unaligned pointers; the non-temporal SSE2 kernels end without sfence.
- Baselines vary per page: the overclocked Raspberry Pi run on a custom 4.1.15 kernel shows libc memcpy at 307.9 MB/s, below the stock run's 387.6 MB/s despite higher clocks, so the libc (or preloaded copy routines) differed between runs on the same page; issue #30 (open) reports a segfault in aligned_block_copy_movsb under MSYS2 gcc 13.3 on Windows.

## Known shortcomings

- First-party harness with no compiler, flags or libc version recorded; wins only against 2012-2017 ARM libcs, and libc memcpy ties the best custom copy on a Ryzen 9800X3D and stock Raspbian; benchmark loops, not a drop-in library. Abandoned since 2017-02-14.
- Harness flaw: the buffer is fixed at #define SIZE 32 MiB with no override, so src plus dst (64 MiB) fits the Ryzen 7 9800X3D's 96 MB L3, and that wiki page measures L3 rather than DRAM (memcpy 81.4 GB/s copied, about 163 GB/s of traffic, and memset 156 GB/s, both above the 96 GB/s DDR5-6000 dual-channel peak, derived); its 'non-temporal 2.5x slower than libc' row is a cache artifact. C rows are compiler-sensitive (issue #7: a 3.5-4x swing between gcc 4.6.3 and 4.7.2) and the volatile fix came only on 2016-03-29, after the A13 (v0.2.9) and Pi (v0.3.9) runs. Kernels are not memcpy-safe: size 0 still writes a block, tails are dropped, aligned-only loads, no sfence after non-temporal stores.

## Caveats and trade-offs

The harness is the project's own benchmark program, and the wiki pages (68 pages, community-submitted; the BeagleBone Black page came from a third-party contributor in March 2017) record neither compiler, flags nor libc version, so the baseline is whatever libc memcpy each OS image shipped. The ARM wins come from 2012 to 2017 era boards (Cortex-A8, Allwinner A13) whose glibc memcpy lacked prefetching or NEON loops; they may not hold for current glibc, Bionic or Arm optimized-routines, and stock Raspbian (which preloads its own copy routines) already matches the best kernel. On modern x86 libc memcpy ties or beats every custom copy (Ryzen 9800X3D 81381.2 vs 81804.8 MB/s; nontemporal copies 2.5x slower there), and the only x86 wins are 4 to 25 percent from nontemporal stores on an i7-8700T. Libc memset is level with the custom fills on BeagleBone Black and Raspberry Pi. Runs span tinymembench v0.2.9 to v0.4.9 and many contributors. Results are large-block bandwidth with aligned buffers, not small-copy latency or correctness-checked memcpy replacements: the kernels are benchmark loops inside a test program (MIT), not a packaged memcpy library. The code repository has had no commit since 2017-02-14, though the wiki still receives runs (Ryzen 9800X3D, Core i9-13900K pages). [retier] The harness is the project's own benchmark program, and the wiki pages (68 pages, community-submitted) record neither compiler, flags nor libc version, so the baseline is whatever libc memcpy each OS image shipped. The ARM wins come from 2012-2017 era boards (Cortex-A8, Allwinner A13) whose glibc memcpy lacked prefetching or NEON loops and may not hold for current glibc, Bionic or Arm optimized-routines; stock Raspbian already matches the best kernel. Harness flaw on large-cache CPUs: main.c fixes the buffers at #define SIZE 32 MiB with no override, so src plus dst (64 MiB) fits the Ryzen 7 9800X3D's 96 MB L3, and that page's libc memcpy 81381.2 MB/s copied (about 163 GB/s of traffic) and memset 156460.7 MB/s both exceed the 96 GB/s peak of its dual-channel DDR5-6000 (derived from page data), so it measures L3, not DRAM, and its 'non-temporal 2.5x slower than libc' row is a cache artifact rather than evidence about streaming stores. C-kernel rows are compiler-sensitive (issue #7: forward and backward C copies swapping 3.5-4x between gcc 4.6.3 and 4.7.2 on a Cortex-A7), and store order was only forced with volatile on 2016-03-29 (v0.4), after the Allwinner A13 (v0.2.9) and Raspberry Pi (v0.3.9) runs, so cite the NEON/ARM assembly rows rather than the C rows. Baselines vary within a page (the overclocked Raspberry Pi run shows libc memcpy at 307.9 MB/s against 387.6 MB/s stock). Kernels are not memcpy-safe: do-while loops write one block even at size 0, tails are rounded away (bic #127), NEON stores carry :256 alignment hints and SSE2 uses movdqa, and the non-temporal SSE2 kernels end without sfence; issue #30 (open) reports a segfault in aligned_block_copy_movsb under MSYS2 gcc 13.3.

A benchmark program rather than a library: the kernels (arm-neon.S, aarch64-asm.S, x86-sse2.S, mips-32.S) are bandwidth tests on aligned blocks, not memcpy replacements (no small-size, misalignment or overlap handling). Prefetch distance is tuned per core, and non-temporal stores avoid cache pollution at the price of making later reads of the copy slow.

## Maintenance

Abandoned since 2017-02-14 (71 commits, 418 stars, 102 forks, 12 open issues, 9 open PRs) but MIT-licensed, small and still used: the wiki keeps receiving runs from current CPUs; build with GCC and treat the numbers as diagnostics, not as a library recommendation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The wiki pages time libc memcpy/memset ('standard memcpy', 'standard memset') and the project's own C, NEON, ARM and SSE2 kernels in the same run, and every number in the record matches the raw wiki markdown; but the harness is the project's own program (main.c, asm-opt.c, arm-neon.S, x86-sse2.S) and no page records compiler, flags or libc version, so it is not A, and a first-party harness run by community contributors (the BeagleBone Black page was added by a third-party account on 2017-03-21) is not an independent suite, so C rather than B.
- **Verifier notes:** Numbers verified line by line against the raw wiki markdown (BeagleBone Black, Allwinner A13, i7-8700T, Raspberry Pi BCM2835, Ryzen 9800X3D); downgraded B to C because the harness is first-party and no compiler, flags or libc versions are recorded. Shortcomings: no compiler/flags/libc version on any page; wins only against 2012-2017 ARM libcs; libc memcpy ties or beats every custom copy on modern x86 and stock Raspbian; benchmark kernels rather than a drop-in library; code abandoned since 2017. Metadata (MIT, 418 stars, 102 forks, last commit 2017-02-14, not a fork) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-49 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ssvb/tinymembench>
  - <https://github.com/ssvb/tinymembench/commits>
  - <https://github.com/ssvb/tinymembench/wiki>
  - https://github.com/ssvb/tinymembench/wiki/BeagleBone-Black-(AM3358)
  - https://github.com/ssvb/tinymembench/wiki/BeagleBone-Black-(AM3358)/_history
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/readme.txt>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/LICENSE>
  - https://raw.githubusercontent.com/wiki/ssvb/tinymembench/BeagleBone-Black-(AM3358).md
  - <https://raw.githubusercontent.com/wiki/ssvb/tinymembench/Allwinner-A13.md>
  - <https://raw.githubusercontent.com/wiki/ssvb/tinymembench/Intel-Core-i7-8700T-6-Core-Processor.md>
  - https://raw.githubusercontent.com/wiki/ssvb/tinymembench/Raspberry-Pi-(BCM2835).md
  - <https://raw.githubusercontent.com/wiki/ssvb/tinymembench/AMD-Ryzen-9800x3D-DDR5-6000.md>
- **Sources the enricher read:**
  - <https://github.com/ssvb/tinymembench>
  - <https://github.com/ssvb/tinymembench/commits/master>
  - <https://github.com/ssvb/tinymembench/issues?q=is%3Aissue>
  - <https://github.com/ssvb/tinymembench/issues/7>
  - <https://github.com/ssvb/tinymembench/issues/30>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/readme.txt>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/version.h>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/main.c>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/util.c>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/util.h>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/asm-opt.c>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/asm-opt.h>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/arm-neon.S>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/x86-sse2.S>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/aarch64-asm.S>
  - <https://raw.githubusercontent.com/ssvb/tinymembench/HEAD/mips-32.S>
  - https://raw.githubusercontent.com/wiki/ssvb/tinymembench/BeagleBone-Black-(AM3358).md
  - <https://raw.githubusercontent.com/wiki/ssvb/tinymembench/Allwinner-A13.md>
  - <https://raw.githubusercontent.com/wiki/ssvb/tinymembench/Intel-Core-i7-8700T-6-Core-Processor.md>
  - https://raw.githubusercontent.com/wiki/ssvb/tinymembench/Raspberry-Pi-(BCM2835).md
  - <https://raw.githubusercontent.com/wiki/ssvb/tinymembench/AMD-Ryzen-9800x3D-DDR5-6000.md>
  - WebSearch: AMD Ryzen 7 9800X3D L3 cache 96MB (retailer spec snippets: 96 MB L3, 8 MB L2)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ssvb/tinymembench`) · [data/wave13/enrich/raw/github_com_ssvb_tinymembench.json](../../../data/wave13/enrich/raw/github_com_ssvb_tinymembench.json) (enrichment confidence 0.75)

</details>
