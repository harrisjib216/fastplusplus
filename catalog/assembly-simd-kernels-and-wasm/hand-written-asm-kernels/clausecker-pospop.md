# pospop (positional population count, Go assembly + C)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (assembly kernels), with a C version in src.c` · `BSD-2-Clause` · 🟢 active

> Go (plus a newer C port) positional popcount in AVX-512/AVX2/SSE2/NEON assembly; about 5-24x the repo's best scalar Go kernel.

| | |
|---|---|
| **Beats** | the repo's own portable pure-Go kernels (generic8/16/32/64 positional popcount), compiled by Go 1.16 |
| **Claimed result** | README table (100 kB buffer, GB/s): amd64 avx512 82.1, avx2 34.8, sse2 16.0 versus generic8 1.02, generic16 1.71, generic32 2.66, generic64 3.43 (avx512 is 24x the best generic64 and 80x generic8; avx2 10x and 34x; derived from page data); arm64 neon 36.9 versus generic8 1.68 and generic64 6.56 (5.6x to 22x derived); 386 avx2 31.6 versus generic8 0.297. |
| **Workload** | positional population count (per-bit-position counts) over a 100 kB buffer, GB/s per kernel |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6138 @ 2.00 GHz (amd64 and 386); Apple M1 (arm64); ARM Cortex-A72 r0p3 on Raspberry Pi 4B (arm) |
| **Compiler and flags** | README says 'all using Go 1.16', but the amd64 rows (avx512, avx2, sse2, generic8-64) and the arm64 NEON row were re-measured for v1.4.0 (commit 18a8661, 2024-11-26) when the code needed Go 1.20 or newer (go.mod 'go 1.20', unsafe.StringData in dispatch.go), so the toolchain for those rows is unstated; the 386, arm and arm64 generic rows are unchanged since October 2021 and plausibly Go 1.16. Go has no optimisation flags; all amd64 kernels are compiled in regardless of GOAMD64. |
| **Adoption** | 70 stars |
| **Last commit** | 2025-11-28 |
| **Links** | [repository](https://github.com/clausecker/pospop) · [benchmark](https://raw.githubusercontent.com/clausecker/pospop/HEAD/README) |

## Verdict

The README table, produced by bench_test.go over a random 100 kB buffer, gives 82.1 GB/s (AVX-512), 34.8 GB/s (AVX2) and 16.0 GB/s (SSE2) on an Intel Xeon Gold 6138 at 2.00 GHz against 1.02-3.43 GB/s for the package's own scalar CSA Go kernels (generic8 to generic64), and 36.9 GB/s NEON versus 1.68-6.56 GB/s generic on an Apple M1; the stated 'Go 1.16' cannot be the toolchain for the amd64 and NEON rows re-measured for v1.4.0 (2024-11-26) under a go.mod requiring Go 1.20. An independent user (issue #2, Ryzen 7 2700X) measured the AVX2 count8 kernel at about 22-28 GB/s at 100 kB across 2020-2021 versions, without a scalar baseline.

## Use it when

- Go code that needs per-bit-position counts over large arrays: bit-sliced indexes, bitmap columns, bioinformatics and database workloads the paper abstract names.
- Buffers of roughly 10 kB and up, ideally around 100 kB per call and a multiple of 64 bytes, which is where the README and package doc say the kernels reach full speed.
- amd64 machines with AVX2+BMI2 or AVX-512 F/BW+BMI2 (82.1 GB/s AVX-512 and 34.8 GB/s AVX2 on a Xeon Gold 6138 at 100 kB) and arm64 with NEON (36.9 GB/s on Apple M1).
- C on ELF/SysV x86-64 or AArch64 Linux/BSD, via the src.c library, when you can patch the header for C++ (see gotchas).

## Skip it when

- Many tiny calls (tens of bytes): in issue #2 an AVX2 count8 call on 32 B took 13-15 ns (about 2 GB/s) on a Ryzen 7 2700X, and the newer carry kernel was slower than older code at 512 B and below.
- 32-bit ARM, ppc64le, RISC-V, s390x and other targets: only the generic Go/C kernels exist there (the README lists arm generic8 at 49 MB/s on a Cortex-A72).
- Plain (non-positional) popcount: a math/bits.OnesCount loop or a dedicated popcount package is simpler.
- C on macOS or Windows: the C port uses GNU ifunc and assumes an ELF ABI with SysV/AAPCS calling conventions; the README asks users to request other ports.
- When you need numbers against an external incumbent: the repo only compares with its own generic kernels; the comparison with Klarqvist-Mula-Lemire positional-popcount lives in the paper, which was not opened here.

## How it is fast

Each kernel first reduces 15 (then 16) input vectors with a carry-save adder (CSA) tree, the Harley-Seal technique built on VPTERNLOGD on AVX-512, so the expensive per-bit work is done once per 960/480/240-byte block instead of per word. The resulting place-value vectors are split by a bit-matrix transposition (masks 0x55/0x33/0x0f then byte/word shuffles) into 16-bit lane counters that are flushed to the 64-bit totals just before they could overflow. Heads are handled with masked or aligned loads and tails with overlapping aligned reads that never cross a page, which is the 'better handling of unaligned and very short arrays' the CCPE 2025 paper describes (abstract seen via search snippet).

## Compared with alternatives

Pick pospop when you need per-bit-position counts; tmthrgd/go-popcount and the other Go assembly siblings (go-and, vectorcmp) solve total popcount or bitwise ops, not this. Among positional popcount codes, mklarqvist/positional-popcount (listed elsewhere in this wave) is the earlier C/C++ library that the CCPE 2025 paper builds on and benchmarks against; pospop is the Go-native choice and its C port is newer (version 0.2, November 2025) with no published C numbers.

## Integration

| | |
|---|---|
| **Form** | module (Go); static lib or shared lib, or source-drop of the listed .S/.c files (C port) |
| **Dependencies** | golang.org/x/sys v0.7.0 (cpu feature detection; unix for the over-read test); C port: none (GNU assembler syntax .S files, GCC or clang) |
| **Minimum toolchain** | Go 1.20 (go.mod; uses unsafe.StringData); C port: C99 compiler with GNU ifunc support on ELF |
| **Platforms** | amd64 (AVX-512 F/BW+BMI2, AVX2+BMI2, SSE2), 386 (AVX2+BMI2, SSE2), arm64 (NEON); generic Go elsewhere. C port: x86-64 and AArch64 ELF, generic C elsewhere |
| **Thread safety** | not documented; the kernel is chosen once at package init (Go) or by an ifunc resolver (C) and the functions keep no shared mutable state, so concurrent calls with separate counts arrays are safe by construction |
| **Drop-in for the baseline** | partial — replaces the package's own generic Go/C kernels transparently (same functions, runtime dispatch); there is no standard-library positional popcount to drop it in for |

## Gotchas

- C++ users: src.c/pospop.h closes its extern "C" block under a misspelled guard ('#ifdef __cplusplis'), so the brace opened under __cplusplus is never closed; reproduced here with g++ 13 and clang++ ('expected '}' at end of input', or 'template with C linkage' when a C++ standard header follows). Fix the typo to __cplusplus before including it from C++, despite the README calling the port usable from C and C++.
- The C port's amd64 dispatcher (src.c/dispatch.c) picks AVX-512 or AVX2 from CPUID leaf 7 bits alone, with no OSXSAVE/XGETBV check that the OS has enabled the AVX or AVX-512 register state; Go's golang.org/x/sys/cpu does that check. On a system or VM that masks the state but not the CPUID bits, the C library would fault with SIGILL.
- Kernels read whole aligned 64-byte blocks beyond both ends of the slice (masked or discarded); TestOverread checks they never cross a page boundary, but byte-precise memory checkers may still flag the reads.
- Counts are added, not stored: reuse of a counts array accumulates across calls. Benchmark figures reuse one 100 kB buffer (L2-resident on the Xeon Gold 6138), and the 80x headline is against generic8, a byte-at-a-time CSA loop; generic64 (3.43 GB/s) is the fairer scalar baseline (24x).

## Known shortcomings

- Toolchain unstated: README says Go 1.16 but the amd64 and NEON rows were re-measured at v1.4.0 (18a8661, 2024-11-26), which needs Go 1.20; the baseline is the package's own generic Go code. CCPE 2025 paper (arXiv 2412.16370) unopened, retier candidate.
- Enricher: the C port's pospop.h closes its extern "C" block under a misspelled #ifdef __cplusplis, so the header fails to compile in C++ (reproduced with g++ 13 and clang++) although the README says C++ can use it; dispatch.c picks AVX-512/AVX2 from CPUID bits alone with no OSXSAVE/XGETBV check; the 80x headline is against generic8 (a byte-at-a-time loop) and generic64 is the fairer baseline (24x); kernels read past slice ends but never cross a page; issue #2 has independent Ryzen 7 2700X AVX2 numbers (22-28 GB/s at 100 kB) without a scalar baseline; the paper remains unopened.

## Caveats and trade-offs

The baseline is the repository's own portable Go code (generic8 to generic64), not an external incumbent; the README does not compare against the earlier Klarqvist-Mula-Lemire positional popcount (mklarqvist/positional-popcount, already in this wave's list), which the peer-reviewed paper by Clausecker, Lemire and Schintke (Concurrency and Computation: Practice and Experience 37(27-28), 2025, DOI 10.1002/cpe.70435, arXiv 2412.16370) benchmarks against according to search snippets; the paper itself was not opened (blocked). The README's 'Go 1.16' toolchain line is stale for the amd64 and NEON rows re-measured in November 2024 (the earlier 2021 table had avx512 90.2 GB/s, avx2 35.9 GB/s, generic64 3.59 GB/s). The 100 kB buffer fits in L2, so figures are cache-resident kernel throughput. A C/C++ port with the same kernels lives in src.c (ELF SysV/AAPCS only); the README gives no numbers for it.

AVX2/AVX-512/NEON/SSE2 kernels written as Go assembly (countavx2_amd64.s, countavx512_amd64.s, countneon_arm64.s); the arm32 build has no SIMD kernel. Specialised operation, not a general-purpose replacement for any standard library routine.

## Maintenance

Active (last commits 2025-11-28 adding C port version 0.2, after the CCPE 2025 paper), BSD-2-Clause, 70 stars, test suite covers overflow and page-boundary over-reads; the Go module is mature, the C port is new and has the C++ header bug above.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README table compares the assembly kernels with the repo's generic Go kernels at 100 kB, the benchmark code is public (bench_test.go, BenchmarkCount8/16/32/64 over every kernel) and CPUs are named, but the stated toolchain is wrong for the headline rows: the amd64 and arm64 NEON figures were re-measured in commit 18a8661 (2024-11-26, v1.4.0) when the package already required Go 1.20 (go.mod 'go 1.20', unsafe.StringData in dispatch.go), so 'all using Go 1.16' cannot hold and the compiler for those rows is unstated. The peer-reviewed CCPE 2025 paper could support B or A but was not reachable (arXiv and DOI blocked; search snippet only).
- **Verifier notes:** Numbers in the record match the README exactly and the derived ratios are correct; downgraded A to C because the stated Go 1.16 toolchain cannot have built the v1.4.0 code that produced the amd64/NEON rows (requires Go 1.20). Shortcomings: self-baseline (own generic Go kernels), no comparison with Klarqvist et al. in the repo, stale toolchain line, paper unopened (retier candidate when arXiv 2412.16370 is reachable). Not a duplicate of mklarqvist/positional-popcount (independent implementation of an improved algorithm). Metadata (BSD-2-Clause in COPYING, 70 stars, last commit 2025-11-28, active) confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-49 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/clausecker/pospop>
  - <https://github.com/clausecker/pospop/commits>
  - <https://github.com/clausecker/pospop/commits/master/README>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/README>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/README>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/COPYING>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/go.mod>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/dispatch.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/18a8661d1bee9d6b81b8df5db214aef89b902d0f/README>
  - <https://raw.githubusercontent.com/clausecker/pospop/18a8661d1bee9d6b81b8df5db214aef89b902d0f/go.mod>
  - <https://raw.githubusercontent.com/clausecker/pospop/18a8661d1bee9d6b81b8df5db214aef89b902d0f/dispatch.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/bb80bc35ac354a74dd6216e6630fd99b1136ec22/README>
  - <https://raw.githubusercontent.com/clausecker/pospop/bb80bc35ac354a74dd6216e6630fd99b1136ec22/go.mod>
- **Sources the enricher read:**
  - <https://github.com/clausecker/pospop>
  - <https://github.com/clausecker/pospop/commits/master>
  - <https://github.com/clausecker/pospop/issues?q=is%3Aissue>
  - <https://github.com/clausecker/pospop/issues/2>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/README>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/go.mod>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/dispatch.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/bench_test.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/COPYING>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/generic.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/overread_test.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/overflow_test.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/safe.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/select_amd64.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/select_386.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/select_arm64.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/count_test.go>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/countavx512_amd64.s>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/countavx2_amd64.s>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/README>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/dispatch.c>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/pospop.h>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/Makefile>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/internal.h>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/kernelavx2.S>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/kernelavx512.S>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/countavx2_64.S>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/countgeneric.c>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/test.c>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/dotest.sh>
  - <https://raw.githubusercontent.com/clausecker/pospop/HEAD/src.c/libpospop.map>
  - WebSearch snippet: arXiv 2412.16370 abstract (arxiv.org, refubium.fu-berlin.de and papers.cool not reachable)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/clausecker/pospop`) · [data/wave13/enrich/raw/github_com_clausecker_pospop.json](../../../data/wave13/enrich/raw/github_com_clausecker_pospop.json) (enrichment confidence 0.78)

</details>
