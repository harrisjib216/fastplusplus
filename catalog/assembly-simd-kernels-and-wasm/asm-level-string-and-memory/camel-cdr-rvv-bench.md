# rvv-bench (RISC-V Vector memcpy, memset and strlen assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Assembly (RISC-V Vector 1.0) with a C harness` · `MIT` · 🟢 active

> Hand-written RISC-V Vector 1.0 memcpy, memset and strlen kernels; memcpy averages 2x a board's scalar libc in cache.

| | |
|---|---|
| **Beats** | libc memcpy, memset and strlen of the benchmarked RISC-V board (hosted libc, version not stated); the same harness also times musl's C memcpy/strlen, a byte-wise scalar loop and a compiler auto-vectorized scalar loop |
| **Claimed result** | No headline number in the README; the numbers are in the per-board results pages. Derived from page data (SpacemiT X60 results, fixed variant rvv_m4 against the libc row, bytes/cycle at the nearest recorded size): memcpy 4.73x at 66 B (1.941 vs 0.410), 2.71x at about 1 KB (4.298 vs 1.585), 2.71x at about 16 KB (5.040 vs 1.860), 2.05x at about 265 KB (3.438 vs 1.674), 1.07-1.11x at 8-64 MB; never below libc over all 233 sizes (geomean 2.0x). memset 3.55x at 66 B, 1.64x at about 1 KB, 1.72x at about 16 KB, 1.79x at about 265 KB, parity (1.00-1.02x) from 8 MB up (geomean 1.5x over 245 sizes). strlen is noisy and mixed: 1.36x at 61 B (but 0.72x at 55 B and 1.15x at 67 B), 1.81x at about 1 KB, 2.44x at about 16 KB; the 2.89x at about 260 KB is an isolated spike (0.65x at 245 KB, 0.95x at 275 KB), and above about 280 KB rvv_m4 is slower than libc (about 0.30 vs 0.45 B/cycle, 0.65-0.7x); rvv_m4 is slower than libc at 135 of 262 strlen sizes (geomean 1.15x). Other strlen variants do better: rvv_m1 stays about 2x libc at multi-MB sizes (0.98 vs 0.46 B/cycle at 3.6 MB) and rvv_page_aligned_m8 reaches 4.9x at 16 KB (6.388 vs 1.308 B/cycle), a best-variant selection. |
| **Workload** | Bytes per cycle (hardware cycle counter) of memcpy (random misalignment and aligned), memset and strlen for sizes from 1 byte to tens of MB, comparing hand-written RVV assembly variants (LMUL m1 to m8, aligned, tail-handling and vlmax strategies) with libc, musl and scalar code. |
| **Metric** | throughput |
| **Hardware** | SpacemiT X60 cores of the SpacemiT K1 (Banana Pi BPI-F3), 1.6 GHz, RVV 1.0 with VLEN 256, for the figures quoted; the results repository also has folders for SiFive P870, XuanTie C920V2, SpacemiT A100 and X100, Tenstorrent X280 and others, Sipeed Lichee Pi 4A, CanMV K230 and more |
| **Compiler and flags** | config.mk default: cc -march=rv64gcv -O3 -Wall -Wextra -DUSE_PERF_EVENT (native build; the compiler name and version are not stated in the files opened; the results page labels the compiler auto-vectorized scalar row 'scalar_autovec_clang18') |
| **Adoption** | 154 stars (rvv-bench), 50 stars (rvv-bench-results) |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/camel-cdr/rvv-bench) · [benchmark](https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/memcpy.html) |

## Verdict

On a SpacemiT X60 (K1, 1.6 GHz, VLEN 256), the author's cycle-counter harness (-march=rv64gcv -O3, compiler labelled clang 18) measured the plain LMUL-4 RVV memcpy at 2.0x the board's unnamed libc by geomean over 233 sizes (4.7x at 66 B, 2.7x at 1-16 KB, 1.07x from 8 MB, never slower) and memset at 1.5x (parity from 8 MB). strlen was mixed: LMUL 4 was 1.15x by geomean and slower at 135 of 262 sizes, while LMUL 1 was about 2x at multi-MB sizes (ratios derived from page data).

## Use it when

- Writing or picking memcpy, memset or strlen for an RVV 1.0 core whose libc has no vector path. On a SpacemiT X60 (VLEN 256) the 7-instruction LMUL-4 memcpy ran 2.7x libc at 1-16 KB and was never slower over 233 sizes.
- Freestanding, embedded or custom-libc RISC-V builds: the harness builds freestanding (nolibc.h) for rv64gcv and rv32 Zve32f, and the kernels need nothing but the vector unit.
- Tuning LMUL and alignment strategy for a specific core: rvv-bench-results publishes the same kernels measured on many cores (SpacemiT X60, SiFive P870, XuanTie C920V2, Tenstorrent X280, CanMV K230 and others) next to instruction-throughput tables.
- In-cache fills and copies (up to about 1 MB), where LMUL-4 memset ran 1.6-1.8x libc and memcpy 2.0-2.7x on the X60.
- Long strings on the X60: the LMUL-1 vle8ff strlen held about 2x libc from 1 MB to 16 MB.

## Skip it when

- Buffers larger than the caches: memcpy and memset converge to 1.0-1.1x libc from 8 MB up on the X60 because DRAM bandwidth is the limit.
- strlen without per-core tuning: the LMUL-4 variant is slower than libc at 135 of 262 sizes and runs at 0.65-0.7x above about 280 KB, and the best in-cache variant (page_aligned_m8, 4.9x at 16 KB) drops to 0.64x at 260 KB.
- Systems whose libc already dispatches an RVV routine: the measured gap is against an unnamed, apparently scalar board libc. A glibc RVV memcpy IFUNC series was still unmerged in patchwork per search snippets.
- XTheadVector 0.7.1 cores (C906/C910) or RISC-V cores without V: the kernels are RVV 1.0 only.
- Overlapping buffers or a drop-in libc: there is no memmove kernel, no ifunc or hwprobe dispatch and no packaging, so you must extract, rename and wire the routines in yourself.

## How it is fast

The kernels are RVV strip-mining loops: vsetvli sets vl = min(remaining, VLMAX), so each vle8.v/vse8.v moves a whole register group (128 bytes at LMUL 4 on VLEN 256) and the last partial chunk needs no scalar tail loop. strlen loads with fault-only-first vle8ff.v (or with page-bounded plain loads in the page_aligned variant) and finds the NUL with vmseq.vi plus vfirst.m. The baseline appears to be scalar code: on the X60 the board's libc memset is no faster than musl's 64-bit SWAR C at 16 KB and 1.46x slower at 265 KB (derived from page data).

## Compared with alternatives

It is the only RISC-V Vector entry here: sve-string-routines-benchmarks and Arm Optimized Routines target Arm SVE/NEON, and tinymembench and copies-and-fills target older ARM boards. Pick rvv-bench for RVV 1.0 cores and for per-core LMUL tuning data; pick Arm Optimized Routines when you need a maintained, packaged library on Arm.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the kernels; the harness uses the repo's nolibc.h and optionally Linux perf_event for user-mode cycle counting |
| **Minimum toolchain** | GCC or Clang with an RVV 1.0 assembler (-march=rv64gcv). CI builds with clang-20 and Ubuntu's riscv64-linux-gnu-gcc; the X60 results label the compiler clang 18. |
| **Platforms** | RISC-V with the V 1.0 extension (rv64gcv; rv32 with Zve32f also builds in CI); not XTheadVector |
| **Thread safety** | not documented; the kernels are stateless leaf routines that touch only argument, temporary and vector registers |
| **Drop-in for the baseline** | partial — the C signatures and calling convention match memcpy, memset and strlen, but the symbols are macro-generated (memcpy_rvv_m4 and so on through bench/template.S), so you extract and rename them; there is no memmove semantics and no runtime dispatch |

## Gotchas

- The memcpy page's 'scalar_autovec' row tracks libc within about 1% at most sizes (geomean 1.02x), which fits the compiler turning the byte loop into a libc memcpy call, so that row is not real auto-vectorized code. Memset's scalar_autovec row, by contrast, reaches 1.56x libc at 16 KB and 1.80x at 265 KB, so a plain C loop built with -march=rv64gcv already captures much of the memset gain (derived from page data).
- Each plotted point is a trimmed mean of the middle 60% of 10-64 single-call timings (bench.h), not a median. Misalignment is re-randomized per repetition, and before every timed call the destination is pre-written by a libc memset outside the timed region, so copies hit a warm destination. Small sizes include call and cycle-counter overhead (the same for every implementation).
- LMUL choice changes the verdict per kernel: LMUL-1 memset loses to libc at 137 of 245 sizes (0.70x at 16 KB) while LMUL 4 wins, and LMUL-8 memcpy dips to 0.78x at its worst size.
- strlen_rvv_page_aligned hardcodes 4096-byte pages and, after the first page boundary, issues plain VLMAX-byte loads. That is safe only while VLEN\*LMUL/8 &lt;= 4096 bytes (VLEN up to 4096 bits at LMUL 8); CI validates the kernels in QEMU at VLEN 128-1024 with tail-agnostic all-ones on and off.

## Known shortcomings

- strlen 2.89x at 260 KB is a noise spike and rvv_m4 strlen is slower than libc at 135 of 262 sizes and above about 280 KB; memcpy geomean 2.0x and memset 1.5x hold; libc version unrecorded, compiler known only from a clang18 label; each point is a median of 10-64 repeats.
- Enricher: the memcpy 'scalar_autovec' row equals libc (geomean 1.02x), likely the loop turned into a memcpy call; the memset scalar_autovec row is already 1.56x libc at 16 KB and libc memset is 1.46x slower than musl's SWAR at 265 KB, so the baseline is weak; the point is a trimmed mean of the middle 60%, not a median; the destination is pre-written untimed before each call; LMUL-1 memset loses at 137 of 245 sizes; page_aligned strlen hardcodes a 4096-byte page (unsafe above VLEN 4096 at LMUL 8); kernels are checked in QEMU at VLEN 128-1024. Lead (weak): glibc RVV memcpy IFUNC patch series (unmerged).

## Caveats and trade-offs

The baseline is whatever libc the board ran (distribution and version not recorded; most likely a scalar glibc without an RVV string path), so much of the gap is the absence of RVV code in that libc, not a better algorithm; the author's own observations on the X60 index page compare against musl's SWAR code. Ratios are derived from the chart data embedded in the results HTML at the nearest recorded size, for one fixed variant; best-variant figures are selections. Each point is the median of 10 to 64 repeats (bench/config.h MIN_REPEATS 10, MAX_REPEATS 64) with output validated against a reference on the first repetition, but no spread is shown, and strlen in the 30-400 KB range swings between 0.33x and 3.5x of libc from one size to the next. memcpy and memset gains shrink to parity once data leaves the caches (8 MB and up). The compiler is only identified by the 'scalar_autovec_clang18' label; config.mk's default is CC=cc. The rendered results site is on github.io (blocked here), so the HTML in the rvv-bench-results repository was parsed. Other kernels in the repo (utf8_count, memreverse, mergelines, byteswap, base64) have no libc counterpart and are not part of this claim. The routines are benchmark kernels in bench/\*.S, not a packaged library.

RISC-V Vector 1.0 hardware only (rv64gcv); an XTheadVector instruction-timing directory exists but the README says it is no longer maintained. The kernels are benchmark implementations in bench/\*.S, meant to be studied or copied rather than a drop-in libc; the best variant (LMUL, alignment strategy) differs per core, and the page-aligned strlen needs the page size to be known.

## Maintenance

Active (135 commits, last on 2026-08-14; CI validates every bench kernel under QEMU at four VLENs) and MIT-licensed, so copyable: lift the few-instruction kernels you need and rename the MX() symbols rather than linking the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** The X60 results pages carry 'libc' and 'musl' rows next to the RVV variants, the harness and kernels are public (bench/memcpy.c, memcpy.S, memset.c, memset.S, strlen.c, strlen.S, bench.h, config.h), flags are in config.mk (-march=rv64gcv -O3 -DUSE_PERF_EVENT), the CPU is named (SpacemiT X60, 1.6 GHz, VLEN 256) and the run is pinned to rvv-bench commit e1b462f; the compiler is only given by the 'scalar_autovec_clang18' label, which suffices for hand-written assembly, so tier A stands. Downgrade is for the overstated strlen claim.
- **Verifier notes:** Tier A kept; downgraded because the strlen figures were cherry-picked: 2.89x at 260 KB is a single noisy point and rvv_m4 strlen is slower than libc at more than half the recorded sizes and at every size above about 280 KB. memcpy (geomean 2.0x, never slower) and memset (1.5x in cache, parity in DRAM) hold up. Baseline libc identity and version are unrecorded.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-48 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/memcpy.html>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/memset.html>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/strlen.html>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/index.html>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/config.mk>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/memcpy.c>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/strlen.c>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/config.h>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/Makefile>
  - <https://github.com/camel-cdr/rvv-bench>
  - <https://github.com/camel-cdr/rvv-bench/commits>
  - <https://github.com/camel-cdr/rvv-bench/commit/e1b462f1263e3940a72d7dcac11b68d8e5fddb09>
  - <https://github.com/camel-cdr/rvv-bench-results>
  - <https://github.com/camel-cdr/rvv-bench-results/tree/main/spacemit_x60>
- **Sources the enricher read:**
  - <https://github.com/camel-cdr/rvv-bench>
  - <https://github.com/camel-cdr/rvv-bench/commits/main>
  - <https://github.com/camel-cdr/rvv-bench/commit/accbe17b3d2ce21712ea480a87bb8d3c58e6d671>
  - <https://github.com/camel-cdr/rvv-bench/issues?q=is%3Aissue>
  - <https://github.com/camel-cdr/rvv-bench/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/config.mk>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/run.sh>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/nolibc.h>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/Makefile>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/config.h>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/bench.h>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/template.S>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/memcpy.c>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/memcpy.S>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/memset.c>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/memset.S>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/strlen.c>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/bench/strlen.S>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/.github/workflows/validate-bench.yml>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/.github/workflows/rv64-config-hosted.mk>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/.github/workflows/rv64-run.sh>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench/HEAD/.github/workflows/rv32-config.mk>
  - <https://github.com/camel-cdr/rvv-bench-results/tree/main/spacemit_x60>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/README.md>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/index.html>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/memcpy.html>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/memset.html>
  - <https://raw.githubusercontent.com/camel-cdr/rvv-bench-results/HEAD/spacemit_x60/strlen.html>
  - WebSearch: glibc RISC-V vector RVV memcpy strlen ifunc merged release (snippets of patchwork.sourceware.org daichengrong v7 'RISC-V: add riscv vector support for memcpy', State: New)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/camel-cdr/rvv-bench`) · [data/wave13/enrich/raw/github_com_camel_cdr_rvv_bench.json](../../../data/wave13/enrich/raw/github_com_camel_cdr_rvv_bench.json) (enrichment confidence 0.78)

</details>
