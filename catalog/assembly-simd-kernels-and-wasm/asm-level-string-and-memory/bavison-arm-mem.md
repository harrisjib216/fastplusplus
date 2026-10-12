# arm-mem (bavison): ARM-accelerated memcpy, memmove, memset, memcmp and strlen

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Assembly` · `BSD-3-Clause (per-file headers: Copyright 2013 Raspberry Pi Foundation and RISC OS Open Ltd, later files 2015-2019 RISC OS Open Ltd; no LICENSE file; test.c and test-strlen.c carry no header)` · 🟡 stale

> Hand-written 32-bit ARM assembly memcpy, memmove, memset, memcmp and strlen for Raspberry Pi cores; preloaded over glibc by Raspberry Pi OS, but never benchmarked against it.

| | |
|---|---|
| **Beats** | generic glibc memcpy, memmove, memset, memcmp and strlen on 32-bit ARM (baseline implied by the description, not named in the README) |
| **Claimed result** | No numbers against glibc in the README, the test harness or the commit history. The only figures are self-relative commit titles from the memcpy tuning in 2013 and 2015 ('Improve L1 and L2 results by around 5% and 2% respectively', 'Extra 3-5% speed boost for Cortex-A7 memcpy'). The description claims only 'ARM-accelerated versions of selected functions from string.h'. |
| **Workload** | No benchmark numbers published. test.c (built by the 'test' make target, CFLAGS -std=gnu99 -O2 -fno-inline) runs correctness checks and then times a single CANDIDATE routine (memcpy, memset or memcmp chosen by #if) over L1-, L2- and memory-sized buffers, subtracting a no-op control function, so a glibc comparison needs two runs with and without LD_PRELOAD of libarmmem. |
| **Metric** | throughput |
| **Hardware** | ARMv6 (-v6l) and ARMv7 (-v7l) builds; NEON strlen and memcmp tuned for Cortex-A53; Raspberry Pi class targets |
| **Adoption** | 57 stars, 13 forks (including RPi-Distro/arm-mem and kobolabs/arm-mem); built into Raspberry Pi OS / Raspbian's raspi-copies-and-fills package (RPi-Distro/arm-mem debian/changelog: 0.5-1 initial release June 2015 through 0.13 April 2019) and enabled through /etc/ld.so.preload; Arch Linux ARM replaced libcofi with it (forum snippet only) |
| **Last commit** | 2024-03-18 |
| **Links** | [repository](https://github.com/bavison/arm-mem) |

## Verdict

Nothing was measured against glibc: the README, test harness and commits publish no comparison, and the only figures are self-relative commit titles ('Improve L1 and L2 results by around 5% and 2%' for ARM1176 memcpy in January 2013, 'Extra 3-5% speed boost for Cortex-A7 memcpy' in February 2015). Search snippets found an Arch Linux ARM forum thread saying it is faster than its predecessor libcofi, also without numbers (snippet only; the forum host is unreachable here).

## Use it when

- 32-bit Raspberry Pi OS (armhf) on Pi 1/Zero (ARMv6) or Pi 2/3 (Cortex-A7/A53 in AArch32), where it is already installed and preloaded; keep it unless a measurement on your board says otherwise.
- Embedded 32-bit little-endian ARM Linux images based on an ARM1176 or Cortex-A7/A53 core where you can LD_PRELOAD or statically link a BSD-licensed string library and will measure the result yourself.
- Bulk copies, fills and compares of hundreds of bytes and up, where the burst and preload tuning matters more than call overhead.
- As readable reference assembly for pld-prefetched ARMv6 copy loops and NEON memset/memcmp/strlen on ARMv7.

## Skip it when

- AArch64 (64-bit) userlands: there is no ARMv8/AArch64 build (issue #10 'v8 aarch64 version' closed); the package only symlinks the v7 library to the v8 and aarch64 platform names for 32-bit processes on such hosts.
- Other ARM cores without your own measurement: the maintainer answered issue #2 ('memcpy slower than libc on Allwinner A20') that the library 'was really only ever targeted at the Raspberry Pi' and that an optimal routine for one ARM core is often not for another.
- Anywhere you need published evidence of a speedup over glibc: none exists in the repo, its issues, or its commit history (only self-relative 5%, 2% and 3-5% commit titles).
- Valgrind- or sanitizer-checked builds: the NEON strlen's in-page overread triggers Memcheck 'Invalid read of size 8' reports (open issues #13 and #14), and Valgrind could not redirect libarmmem symbols before the 2024 function-size commit, which Raspberry Pi OS has not packaged (issue #11).
- Big-endian ARM or Thumb-only (ARMv7-M) targets: the code is ARM-state assembly and 'Operate only in little endian' (2017).

## How it is fast

The ARMv6 routines (for the ARM1176JZF-S) move data in 32-byte ldmia/stmia bursts of eight registers aligned to the destination, issue pld preloads a fixed number of cache lines ahead (prefetch_distance 3 for memcpy, 2 for memcmp), and handle a misaligned source by shifting and merging whole words instead of byte copies. The ARMv7 routines use NEON: memset fills with 2x32-byte vst1 stores per iteration on 16-byte-aligned addresses, memcmp compares 32-byte blocks after a short scalar head (the source notes that most differences occur in the first few bytes), and strlen tests 16 bytes per iteration with vceq and falls back to bytes only when the next load would cross a 4 KiB page. The memcpy loops were tuned per core (2013 ARM1176, 2015 Cortex-A7; NEON strlen and memcmp tuned for Cortex-A53 in 2019).

## Compared with alternatives

It is the only catalogued string/memory routine set for 32-bit ARM and the only one deployed by default in a mainstream distribution (Raspberry Pi OS); rvv-bench covers RISC-V vectors and memx-cdy and the gist entries target x86 glibc, each with actual measurements, so prefer them on their platforms and treat arm-mem as a Pi-specific default whose gain you must measure.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none (GNU assembler via gcc and make to build; static libarmmem-v6l.a / libarmmem-v7l.a also built) |
| **Minimum toolchain** | GCC/binutils for 32-bit ARM (ARM-state, .altmacro, .fpu neon for v7l); exact minimum version not documented; Makefile supports CROSS_COMPILE=arm-linux-gnueabihf- |
| **Platforms** | 32-bit little-endian ARM Linux only: ARMv6 (ARM1176JZF-S) and ARMv7 with NEON (Cortex-A7, Cortex-A53 in AArch32); strlen only in the v7l build |
| **Thread safety** | not documented; the routines are leaf functions working in registers and the stack with no global state, so they are reentrant like the libc versions |
| **Drop-in for the baseline** | yes |

## Gotchas

- Harness flaw: the shipped test program cannot produce a library-versus-glibc number by itself. The Makefile links test from test.o alone, so it times whichever memcpy/memset/memcmp the dynamic linker resolves (glibc unless libarmmem is preloaded); the routine is chosen by editing an #if chain (strlen is not an option); the correctness checks sit under '#if 0' and, if enabled, '#define mymemcpy memcpy' makes them compare the routine with itself until edited; cache sizes are hard-coded (L1 16 KiB, L2 128 KiB); timing is gettimeofday with a no-op control subtracted, and each bench loop makes times+1 calls but counts times x len bytes. Test-strlen likewise checks the page-boundary safety of whatever strlen is linked.
- The ARMv7 strlen reads up to 15 bytes past the terminator inside the same 4 KiB page by design (it drops to byte loads before a load could cross a page), which is safe on Linux but reported by Valgrind Memcheck as invalid reads (issues #13 on a Pi 3B+ with Raspbian 12, and #14, both open).
- Correctness history: memset failed for negative byte values (#1) and for n &gt; 255 (fixed May 2015), a unified Cortex-A7 object crashed a Pi 1 when preloaded (#3, 2015), the NEON strlen shipped in raspi-copies-and-fills 0.8 needed 'ARMv7 strlen: fix stupid bug' (0.12), ARMv7 memcmp now returns exactly -1/0/+1 (b48ea15, 0.13), and the April 2019 Cortex-A53 memcpy rewrite was reverted eleven days later (the 0.13 package built from the reverted tree).
- No LICENSE file: every .S file and arm-mem.h carries BSD-3-Clause text (Raspberry Pi Foundation and RISC OS Open Ltd), but test.c and test-strlen.c have no licence header.

## Known shortcomings

- No numbers against glibc (tier D); kept because Raspberry Pi OS ships it by default (raspi-copies-and-fills); 2019 strlen/memcmp fixes, the Cortex-A53 rewrite was reverted. BSD-3-Clause.
- Enricher: the Makefile links the test from test.o only, so it times whatever memcpy the dynamic linker resolves (glibc unless preloaded); the correctness checks sit under #if 0 and, if enabled, '#define mymemcpy memcpy' compares libc with itself; still no numbers against glibc; the NEON strlen reads past the terminator within the page (Valgrind issues #13, #14 open); Raspberry Pi OS ships 0.13 (April 2019). Leads: asb/copies-and-fills (libcofi, claims 2-3x over generic libc memcpy), fastarm ARM memcpy variants.

## Caveats and trade-offs

No evidence of speed against glibc: no published numbers, and the harness measures one routine at a time against a no-op control. Kept for deployment, not evidence: it is the libarmmem preloaded by default on 32-bit Raspberry Pi OS. Correctness history: the NEON strlen tuned for Cortex-A53 shipped in raspi-copies-and-fills 0.8 (January 2019) and needed 'ARMv7 strlen: fix stupid bug' (March 2019, package 0.12), memcmp return values were then limited and later forced to -1/0/+1 (package 0.13), and the April 2019 'Rewrite memcpy / memmove to tune for Cortex-A53' was reverted eleven days later; CNX Software reported (snippet only) that a March 2019 package update broke programs including SSH logins on some boards. The latest commit (2024-03-18, 'Add function type and sizes', by a contributor) is metadata only; the last code change is from 2019. 32-bit ARMv6/ARMv7 only (v7 symlinked to v8/aarch64 in the package only for qemu hosts). Licence is BSD-3-Clause in every library source file but there is no LICENSE file and the test programs have no header. Not a duplicate of simonjhall/copies-and-fills (libcofi, LGPL-2.1): it is a separate codebase by Ben Avison that replaced libcofi in Raspbian and Arch Linux ARM.

32-bit ARM only; strlen exists for ARMv7 only; typically deployed via LD_PRELOAD or linking; NEON variants need NEON. No licence file or licence text on the repo page, so the code cannot be copied.

## Maintenance

Stale: last code change April 2019 (memcmp return values), last commit March 2024 (Paul Floyd's ELF function type and size directives for Valgrind, not in the Raspberry Pi OS package, whose packaging branch stops at 0.13 in April 2019); BSD-3-Clause in the source headers, so copyable, and still preloaded on 32-bit Raspberry Pi OS. The shipped test program measures only the routine the dynamic linker resolves, so there is no harness-backed speed evidence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No benchmark_url and no numbers against glibc anywhere: the README has none, test.c benchmarks one CANDIDATE routine against a no-op control rather than against libc, and the only percentages are self-relative commit titles ('Improve L1 and L2 results by around 5% and 2%', 'Extra 3-5% speed boost for Cortex-A7 memcpy'). An Arch Linux ARM forum thread (snippet only) says arm-mem is faster than libcofi but that no benchmarks could be found.
- **Verifier notes:** Tier D stands (no numbers at all) but the entry is notable enough to keep: Raspberry Pi OS ships it as raspi-copies-and-fills via ld.so.preload, confirmed from the RPi-Distro/arm-mem debian changelog. Licence corrected from null to BSD-3-Clause (all .S files and arm-mem.h carry the 3-clause text), so usability becomes copyable. Shortcomings to record: no measurement against glibc, harness lacks a side-by-side baseline, 2019 correctness fixes and a reverted rewrite, stale since 2019 apart from a metadata commit.
- **Fields the verifier corrected:** `license`, `usability`, `compared_against_cpp_std_directly`, `claimed_speedup`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/bavison/arm-mem>
  - <https://github.com/bavison/arm-mem/commits/master>
  - <https://github.com/bavison/arm-mem/network/members>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/README.md>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/test.c>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/arm-mem.h>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memcpymove-v7l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memcpymove-v6l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memcmp-v7l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/strlen-v7l.S>
  - <https://raw.githubusercontent.com/RPi-Distro/arm-mem/debian/debian/changelog>
- **Sources the enricher read:**
  - <https://github.com/bavison/arm-mem/commits/master>
  - <https://github.com/bavison/arm-mem/issues?q=is%3Aissue>
  - <https://github.com/bavison/arm-mem/issues/2>
  - <https://github.com/bavison/arm-mem/issues/13>
  - <https://github.com/bavison/arm-mem/issues/14>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/README.md>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/test.c>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/test-strlen.c>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/arm-mem.h>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memcpymove-v6l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memcpymove-v7l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memcmp-v6l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memcmp-v7l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memset-v6l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/memset-v7l.S>
  - <https://raw.githubusercontent.com/bavison/arm-mem/HEAD/strlen-v7l.S>
  - <https://github.com/RPi-Distro/arm-mem/commits/master>
  - <https://github.com/RPi-Distro/arm-mem/commits/debian>
  - <https://github.com/RPi-Distro/arm-mem/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/RPi-Distro/arm-mem/debian/debian/changelog>
  - <https://raw.githubusercontent.com/RPi-Distro/arm-mem/debian/debian/postinst>
  - <https://raw.githubusercontent.com/RPi-Distro/arm-mem/debian/debian/control>
  - <https://raw.githubusercontent.com/RPi-Distro/arm-mem/debian/debian/rules>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/bavison/arm-mem`) · [data/wave13/enrich/raw/github_com_bavison_arm_mem.json](../../../data/wave13/enrich/raw/github_com_bavison_arm_mem.json) (enrichment confidence 0.6)

</details>
