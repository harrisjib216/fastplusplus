# memcpy_benchmark (AVX-256, AVX-512 and rep movsb NASM memcpy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C / NASM assembly` · `Unlicense` · 🔴 abandoned

> Toy NASM AVX/AVX-512/rep movsb copy loops timed against libc memcpy on one huge buffer; not a usable memcpy.

| | |
|---|---|
| **Beats** | libc built-in memcpy (glibc version not stated) |
| **Claimed result** | result.txt, seconds per copy of one 512 MiB buffer (MEM_ALLOC at the result commit; units from memcpy_bench.c's printf), lower is better. Xeon Platinum 8269CY: libc memcpy min 0.3494 / avg 0.3853 vs AVX-256 asm min 0.2711 / avg 0.2987 (about 1.29x), AVX-512 asm min 0.2854 / avg 0.3150 (about 1.22x), rep movsb min 0.3020 / avg 0.3333 (about 1.16x). AMD A8-6410: libc min 0.5464 / avg 0.6221 vs AVX asm min 0.4471 / avg 0.4967 (about 1.22-1.25x) and plain rep movsb min 0.4450 / avg 0.4970 (about 1.23-1.25x); AVX-512 not supported. Ratios derived from page data. |
| **Workload** | Single-threaded copy of one large buffer per run (512 MiB when result.txt was recorded on 2020-09-20; the current code uses 128 MiB), 11 runs per routine; each run mallocs a fresh source (memset before timing) and a fresh, untouched destination, times one copy with gettimeofday, then checks it with memcmp. Routines: libc memcpy, NASM AVX-256 and AVX-512 unrolled copies with prefetcht1, and a three-instruction rep movsb. The multithreaded mode (option 5, libs/memcpy_multithread.c) was added later and is not in result.txt. |
| **Metric** | latency (run time; unit not stated) |
| **Hardware** | AMD A8-6410 APU (2 GHz, no AVX-512) and Intel Xeon Platinum 8269CY (2.5 GHz; cpuinfo flags include 'hypervisor', so a cloud VM); README tells users to set the performance governor, not confirmed for these runs |
| **Compiler and flags** | Harness built with gcc at default -O0 at the result commits (Makefile sets no optimisation flag); NASM for the assembly routines |
| **Adoption** | 13 stars |
| **Last commit** | 2020-09-22 |
| **Links** | [repository](https://github.com/ammarfaizi2/memcpy_benchmark) · [benchmark](https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/result.txt) |

## Verdict

On an Intel Xeon Platinum 8269CY cloud VM, one 512 MiB single-threaded copy took min 0.2711 s with the AVX-256 routine versus 0.3494 s with the prebuilt libc memcpy (glibc version unknown), about 1.29x, with AVX-512 at 0.2854 s and rep movsb at 0.3020 s; on an AMD A8-6410 the AVX routine and plain rep movsb both ran at about 0.445 s versus 0.546 s for libc (about 1.2x). Timings include first-touch page faults on the destination, and an earlier run of the same AVX-256 code on the same Xeon showed no gain over libc.

## Use it when

- As a reading example of how an unrolled AVX/AVX-512 register-block copy and a bare rep movsb compare on very large buffers.
- As a starting harness for your own large-copy experiments, after fixing the averaging and page-fault issues listed under gotchas.
- Only memcpy_movsb is safe to lift as-is (any length, returns dst); it suits large copies on CPUs with ERMS/FSRM.

## Skip it when

- As a drop-in memcpy: memcpy_avx256 and memcpy_avx512 are correct only for non-zero lengths that are exact multiples of 512 and 2048 bytes; any other length overruns both buffers (see gotchas).
- Small or medium copies: there is no small-size path, and every call issues at least one full 512- or 2048-byte block.
- Non-x86-64 targets, or the AVX-512 routine on CPUs without AVX-512F (it faults with an illegal instruction; the harness has no CPUID check).
- When you need a measured win: on the AMD A8 rep movsb alone matches the AVX routine, and on the Xeon the author's own earlier run with identical AVX-256 code tied libc.
- Production use of the multithreaded mode: memcpy_mt_exec drops the len % 4 tail and coordinates workers with plain bools and unfair mutex hand-offs.

## How it is fast

The AVX routines are fully unrolled block copies: 16 ymm loads then 16 ymm stores per 512-byte block (AVX-256), or 32 zmm per 2048-byte block (AVX-512; 16 zmm per 1024-byte block in the version that was timed), each block preceded by prefetcht1 on every source and destination line. memcpy_movsb is just rep movsb, relying on the CPU's ERMS microcode. There is no alignment handling, no non-temporal stores and no size dispatch.

## Compared with alternatives

Pick it only to study block-unrolled AVX copies versus rep movsb at the 512 MiB scale; for a usable faster memcpy, FastMemcpy (skywind3000) has real size dispatch and covers small and medium sizes, and asmlib (abiiranathan) benchmarks against a stated glibc 2.44.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | nasm (to assemble the .asm files); pthreads only for the multithreaded mode |
| **Minimum toolchain** | nasm with AVX-512 support and any C compiler; versions not documented (result commit built the harness with gcc -Wall -O0) |
| **Platforms** | x86-64 System V (Linux ELF64); AVX for memcpy_avx256, AVX-512F for memcpy_avx512, ERMS recommended for memcpy_movsb |
| **Thread safety** | Single-threaded routines are reentrant (no state); the multithreaded wrapper uses global state and unsynchronised bool flags, so it is not safe to call concurrently |
| **Drop-in for the baseline** | partial — memcpy_movsb is a valid memcpy; memcpy_avx256/memcpy_avx512 only work for non-zero lengths that are multiples of 512/2048 bytes and return src instead of dst |

## Gotchas

- Correctness bug in both AVX routines (and in the gen_avx_memcpy.php generator): the size dispatch is 'cmp rcx, 512' followed by an unconditional 'jmp .jge_512' (not jge), and it compares the running offset rcx rather than the remaining length rdx. Every iteration therefore copies a full 512-byte (AVX-512: 2048-byte) block and loops until rdx reaches exactly zero; for any length that is not a non-zero multiple of the block size, rdx wraps negative and the loop runs past both buffers until it faults. The benchmark's 128/512 MiB buffers are exact multiples, so its memcmp check passes and hides the bug.
- Both AVX routines start with 'mov rax, rsi', so they return the source pointer, not dst as memcpy must; neither executes vzeroupper before returning, so callers' later SSE code can pay AVX-SSE transition penalties.
- Harness flaws behind result.txt: 11 timed copies are averaged over 10 (every Avg exceeds its Max); each copy writes to a freshly malloc'd, never-touched destination, so roughly 131,072 first-touch page faults per 512 MiB run are inside the timed region (derived copy rates of only about 1.5-2.0 GB/s on the Xeon); timing uses gettimeofday. At the result commits the Makefile built the harness with 'gcc -Wall -O0', not the -O3 now in the Makefile (the libc memcpy baseline is prebuilt, so this does not change it).
- The Xeon headline is not stable: result.txt at commits 8be9917 and a955014 (same memcpy_bench.c, Makefile and byte-identical memcpy_avx256.asm) recorded libc min 0.3486 s vs AVX-256 min 0.3464 s (a tie; AVX avg 0.3844 vs libc 0.3838) on the same Xeon 8269CY VM; commit 7d431e0 replaced it with the current libc 0.3494 vs AVX-256 0.2711 s (1.29x). The AVX-512 row was also measured on two different routines (1024-byte blocks, then 2048-byte blocks). The AMD A8 rows were consistent across runs (about 1.2x for both AVX and rep movsb).

## Known shortcomings

- Downgraded A to C: no compiler or glibc version; Avg is 11 runs divided by 10 so Avg exceeds Max; the timed copy includes page faults on a fresh 512 MiB destination; plain rep movsb matches AVX on the A8; single-threaded, seconds per 512 MiB copy.
- Enricher: both AVX routines (and gen_avx_memcpy.php) dispatch with 'cmp rcx, 512' followed by an unconditional jmp, comparing the running offset rather than the remaining length, so every call copies whole 512/2048-byte blocks and any length that is not a non-zero multiple overruns both buffers until it faults (the 128/512 MiB benchmark buffers hide it); the routines return the source pointer and lack vzeroupper; result.txt at commits 8be9917/a955014 shows libc 0.3486 vs AVX-256 0.3464 s (a tie) before commit 7d431e0 wrote the current 1.29x, the AVX-512 row was measured on two different routines, and the result commits built the harness with gcc -O0. Retiered to D, reference only; only the rep movsb routine is safe to reuse.

## Caveats and trade-offs

Author's own runs; the README makes no speed claim. Harness flaws: the loop runs TEST_COUNT+1 = 11 copies but divides the total by 10, so every reported Avg exceeds its Max (Xeon libc Avg 0.3853 vs Max 0.3533); ratios survive because all routines share the bug. The destination is a fresh 512 MiB malloc (mmap) never touched before timing, so each timed copy includes about 131,072 first-touch page faults; derived copy rates of about 0.9-2.0 GB/s are well below memory bandwidth, so the numbers mix fault cost with copy speed and may reflect how each store pattern interacts with faulting rather than kernel efficiency. On the A8 the plain rep movsb routine matches the AVX routine, so the gain there is not from the AVX kernel. AVX-512 is slower than AVX-256 on the Xeon. glibc version (which selects the memcpy variant and its non-temporal threshold), compiler and NASM versions are unknown; one result set per machine. The current code uses a 128 MiB buffer, so rerunning it does not reproduce the recorded configuration. The asm measured equals today's libs/memcpy_avx256.asm (only a comment changed).

x86-64 only; AVX-512 variant needs AVX-512 (reported 'CPU is not supported' on the AMD A8); rep movsb performance depends on ERMS/FSRM support; routines are plain memcpy without small-size dispatch.

## Maintenance

Abandoned since 2020-09-22 (24 commits in four days, no issues or releases) and Unlicense public domain, but the AVX routines have an out-of-bounds bug for any length that is not a non-zero multiple of 512/2048 bytes, so treat it as reference material rather than copyable code; only the rep movsb routine is safe to reuse.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now D.
- **Tier reason:** First-party result.txt from the author's own harness (memcpy_bench.c, libs/\*.asm) with the C flags in the Makefile and CPU models in the file, but no compiler, NASM or glibc version (the baseline is the prebuilt libc memcpy, so its version is the key unknown), no units in the file, and harness flaws (off-by-one average, timed first-touch page faults), so it falls short of A.
- **Retiered** C to D: Enricher (2026-10-12): the headline 1.29x is not a stable measurement. result.txt at commits 8be9917 and a955014 shows libc 0.3486 s vs AVX-256 0.3464 s (a tie) from the same harness, Makefile, byte-identical assembly and Xeon before commit 7d431e0 recorded 0.3494 vs 0.2711; the AVX-512 row was measured on two different routines (1024-byte then 2048-byte blocks); the result commits built the harness with gcc -O0, not -O3; and the AVX routines overrun both buffers for any length that is not a non-zero multiple of the block size (stb-zip precedent for the measured code, hidden by the 512 MiB buffers).
- **Verifier notes:** Downgrade A to C: numbers match result.txt but the record's 'multithreaded harness' caveat and 'unit not stated' were wrong (single-threaded modes 1-4, seconds per 512 MiB copy); the harness averages 11 runs over 10 and times first-touch faults on a fresh destination. Metadata on github.com: Unlicense (public domain, OSI-approved, no patent grant), 13 stars, 2 forks, 24 commits, last commit 2020-09-22 (abandoned), not a fork. Shortcomings to record: no compiler/glibc versions, off-by-one Avg, page-fault-laden timing, rep movsb alone matches AVX on AMD, about 1.2-1.3x only.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`, `usability`
- **Shortcomings recorded by:** verifier batch-36 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ammarfaizi2/memcpy_benchmark>
  - <https://github.com/ammarfaizi2/memcpy_benchmark/commits>
  - <https://github.com/ammarfaizi2/memcpy_benchmark/commits/master>
  - <https://github.com/ammarfaizi2/memcpy_benchmark/commit/2eecebd76b8eda620abc97655718d3d7969cc14c>
  - <https://github.com/ammarfaizi2/memcpy_benchmark/commit/d455950c06899d403e4146e1011890dc868766dc>
  - <https://github.com/ammarfaizi2/memcpy_benchmark/commit/a955014ed2091abf24e262dc5625dbdb040a05bd>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/memcpy_bench.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/libs/memcpy_avx256.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/libs/memcpy_movsb.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/libs/memcpy_multithread.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/memcpy_bench.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/memcpy_avx256.asm>
- **Sources the enricher read:**
  - <https://github.com/ammarfaizi2/memcpy_benchmark>
  - <https://github.com/ammarfaizi2/memcpy_benchmark/commits/master>
  - <https://github.com/ammarfaizi2/memcpy_benchmark/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/memcpy_bench.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/libs/memcpy_avx256.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/libs/memcpy_avx512.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/libs/memcpy_movsb.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/libs/memcpy_multithread.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/HEAD/gen_avx_memcpy.php>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/memcpy_bench.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/memcpy_avx256.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/memcpy_avx512.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/memcpy_movsb.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/Makefile>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/8be9917b2b3cf1ea9a1154e0ae2d5aa9f3610653/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/a955014/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/d455950c06899d403e4146e1011890dc868766dc/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/d455950c06899d403e4146e1011890dc868766dc/Makefile>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/7d431e0/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/7d431e0/memcpy_bench.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/7d431e0/memcpy_avx256.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/7d431e0/memcpy_avx512.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/7d431e0/Makefile>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/5242f18/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/2eecebd76b8eda620abc97655718d3d7969cc14c/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/70f19e4/result.txt>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/70f19e4/memcpy_avx256.asm>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/70f19e4/memcpy_bench.c>
  - <https://raw.githubusercontent.com/ammarfaizi2/memcpy_benchmark/70f19e4/Makefile>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ammarfaizi2/memcpy_benchmark`) · [data/wave13/enrich/raw/github_com_ammarfaizi2_memcpy_benchmark.json](../../../data/wave13/enrich/raw/github_com_ammarfaizi2_memcpy_benchmark.json) (enrichment confidence 0.85)

</details>
