# qoi-asm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `x86-64 assembly (GNU as, Intel syntax) with a C test and benchmark harness` · `MIT` · 🟢 active

> Hand-written x86-64 assembly QOI codec, bit-identical to qoi.h and 1.07x-2.16x faster than its gcc -O3 build.

| | |
|---|---|
| **Beats** | QOI reference implementation qoi.h (phoboslab/qoi) compiled with gcc -O3 -march=x86-64-v3 |
| **Claimed result** | 1.07x-2.16x faster than gcc -O3 -march=x86-64-v3 on all 18 benchmark rows (examples: 1080p RGBA random encode 1.95x, 1080p RGBA photo-like encode 1.83x, 512x512 RGBA random decode to 4 channels 2.16x, 512x512 RGB photo-like decode to 3 channels 1.07x); also 1.57x-3.47x over its own first assembly port. |
| **Workload** | Encode and decode of 7 generated inputs (1080p and 512x512, RGB and RGBA: random, runs, photo-like gradient plus noise, 16-colour palette), 18 rows, median of 11 reps (images of 1 Mpx or more) or 31 reps, timed with lfence/rdtsc and clock_gettime. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-14700F (Raptor Lake, AVX2, no AVX-512), WSL2 Linux kernel 5.15, pinned with taskset -c 3; invariant TSC about 2.07-2.08 GHz. |
| **Compiler and flags** | Baseline C is the untouched c/qoi.c, a two-line shim around c/qoi.h, which is byte-identical to phoboslab/qoi master qoi.h (sha256 7de6fca1a285b1c20d38f2723dec8b774eb9f144edb9710800a95feeea09375a, checked). Makefile: the -O3 baseline is gcc -O2 -g -Wall -Wextra followed by -O3 -march=x86-64-v3 (the later -O3 wins); the -O2 oracle is also timed; harness gcc -O2 -g; assembly via GNU as --64. The bench output does not print the compiler version; the committed ref_asm/qoi_O2.s and ref_asm/qoi_O3_x86v3.s carry .ident 'GCC: (Ubuntu 13.3.0-6ubuntu2\~24.04.1) 13.3.0', presumably the bench host's compiler. Reproduce with make bench BENCH_CMD='taskset -c 3 ./build/bench'. |
| **Adoption** | 0 stars, 1 fork, 1 commit (2026-09-26) |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/aplghl/qoi-asm) · [benchmark](https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/docs/BENCHMARKS.md) |

## Verdict

tests/bench.c links qoi.h (byte-identical to upstream, sha256 checked in CI) at gcc -O2 and at -O3 -march=x86-64-v3 into one binary with the assembly, checks every output bit for bit, then reports median TSC ticks over 11 or 31 single-call reps after 3 warm-ups. On an i7-14700F under WSL2 (gcc 13.3.0, taskset -c 3) the ASM was 1.07x-2.16x faster than -O3 on all 18 rows of 7 synthetic 512x512 and 1080p inputs; against -O2 the range is 0.88x-2.92x (derived from page data). The unchanged C rows agree within about 1-2% (worst about 7%) across the three committed result files, bench_after_M1, E2 and D1 (derived from page data).

## Use it when

- You already use qoi.h on x86-64 Linux and want faster encode/decode without changing a line of calling code or the output bytes.
- Encode-heavy pipelines (screenshots, frame dumps, texture caches): the published encode gains are 1.10x-1.99x over gcc -O3 -march=x86-64-v3, with 1.83x on the 1080p photo-like RGBA row.
- High-entropy or RGBA-op-heavy content, where gains are largest (about 2x encode and decode on the random rows).
- Projects that need a single reviewed object file with no dependencies beyond libc and an exact behavioural match to qoi.h, verified by in-process differential tests.

## Skip it when

- Non-x86 targets (ARM, RISC-V, WebAssembly), Windows x64 calling convention, or MSVC/MASM/NASM toolchains: there is only a GNU as, System V object.
- You rely on qoi.h compile-time options: QOI_MALLOC/QOI_FREE overrides and QOI_NO_STDIO cannot apply to the prebuilt object, which always calls libc malloc and stdio.
- Photo-like decode is the bottleneck: the gain there is only 1.07x-1.22x over gcc -O3, and on the run-heavy 1080p RGBA decode the ASM is slower than the plain -O2 C build (0.88x).
- You want independent or real-image evidence: all inputs are synthetic, the numbers come from one WSL2 host, and the repo is a single LLM-generated commit with no users yet.
- You need CET-hardened binaries: the object carries no GNU property note or endbr64, so linking it strips IBT/shadow-stack marking from the final executable.

## How it is fast

The loops keep px, px_prev, run and the input/output cursors in registers instead of stack slots, and dispatch once on channels==3 or channels==4 into two specialised loops, removing qoi.h's per-pixel channel test. The QOI index hash (r\*3+g\*5+b\*7+a\*11)&63 becomes one 64-bit multiply of the byte-spread pixel by 0x0C001C0014002C00 and a shift by 58, which is exact because lower partial products stay below 2^58. Encode computes the three channel deltas with SSE4.1 psubb/pmovsxbd and folds the three DIFF range tests into one unsigned compare; decode applies DIFF/LUMA deltas with pinsrb/paddb; the trailing-run flush is moved out of the hot run loop.

## Compared with alternatives

Pick qoi-asm over the reference QOI (qoi.h) when you are on x86-64 Linux and want the same symbols and bytes, only faster. Pick qoixx (C++), rapid-qoi or the qoi Rust crate when you need ARM or Windows support or a source-level library; none of those was measured against qoi-asm, so no ranking among them exists.

## Integration

| | |
|---|---|
| **Form** | static lib (build/libqoi.a) or a single object (build/qoi_asm.o) used with the unmodified qoi.h header |
| **Dependencies** | none beyond libc (malloc, memset, free, fopen, fread, fwrite, fseek, ftell, fflush, ferror, fclose); building needs GNU binutils as |
| **Minimum toolchain** | GNU as (binutils) with Intel-syntax support; any C compiler for the consumer; tested with gcc 13.3.0 on Ubuntu 24.04 |
| **Platforms** | x86-64 Linux/System V only. Documented requirement is x86-64-v3 (Haswell or newer), but the file uses no AVX, AVX2, BMI or FMA instructions; the highest ISA extension it uses is SSE4.1 (pinsrb, pextrd, pmovsxbd) |
| **Thread safety** | Reentrant like qoi.h: all state (including the 64-entry index) lives on the stack or in registers; only read-only constants are global |
| **Drop-in for the baseline** | partial — same header, symbols, ABI and output bytes as qoi.h, but you must remove QOI_IMPLEMENTATION and link the object, and the build is x86-64 System V only |

## Gotchas

- If any translation unit still defines QOI_IMPLEMENTATION, linking qoi_asm.o gives duplicate symbols, while linking libqoi.a silently keeps the C code because the archive member is never pulled in. The README's first snippet still shows #define QOI_IMPLEMENTATION.
- The ISA baseline is overstated: the README says x86-64-v3 and warns of SIGILL on older CPUs, but only SSE4.1 is actually needed. There is no CPUID check, so a CPU without SSE4.1 faults at the first SIMD instruction.
- Like qoi.h, qoi_decode can read a few bytes past size on a truncated stream; the port reproduces this exactly, so validate or pad untrusted input.
- The bench's 'cycles/op' are invariant-TSC ticks (about 2.07 GHz on the host), not core cycles; use the ratios or ns/op.

## Known shortcomings

- Synthetic inputs only, and the assembly is slower than the -O2 C build on the 1080p_rgba_runs decode4 row (0.88x, derived from page data); the baseline qoi.h is the QOI reference, not a category incumbent; single commit, 0 stars. Harness tests/bench.c, Makefile flags, tests/bench_after_D1.txt, gcc 13.3.0 and i7-14700F all public.
- Enricher (e97, 2026-10-04): numbers hold (bit-identical gate before timing, hash constant checked by algebra, committed runs agree within 1-2%, worst 7%); against -O2 the range is 0.88x-2.92x (derived from page data). Photo-like decode gains only 1.07x-1.22x; the top ratios all come from random-pixel rows. Doc errors: README claims x86-64-v3 but the assembly uses nothing above SSE4.1 and has no CPUID check; the README snippet keeps QOI_IMPLEMENTATION defined, so libqoi.a silently keeps the C code; no QOI_MALLOC or QOI_NO_STDIO support; no CET note, so linking strips IBT/SHSTK marking.

## Caveats and trade-offs

Outputs are bit-identical to qoi.h: tests/bench.c compares ref -O2, -O3 and asm output bit for bit before timing (bench_after_D1.txt prints 'all encode/decode outputs bit-identical (ref == O3 == ASM)'), and the repo reports 19,185 differential cases plus ASan and UBSan runs. Drop-in for the qoi.h implementation: asm/qoi.asm exports the same four symbols (qoi_encode, qoi_decode, qoi_write, qoi_read) with the System V AMD64 ABI, so consumers keep the header and link qoi_asm.o or libqoi.a instead of defining QOI_IMPLEMENTATION; it needs x86-64-v3 (SIGILL on older CPUs) and does not run on non-x86 targets or the Windows x64 ABI. Weaknesses: single host under WSL2; all 7 inputs are generated by splitmix64-based fill functions in bench.c (random, 32x8 block runs, a 'photo-like' synthetic gradient plus noise, a 16-colour palette), not real photographs, and no qoibench corpus was used; cycles are invariant-TSC ticks that can understate core cycles by up to 2.4x, so only ratios and ns/op mean anything (run-to-run drift 6-8 percent); the three implementations run in a fixed order per row (C-O2, C-O3, ASM) rather than interleaved. Against the -O2 build of the same C, ASM is slower on one row (1080p_rgba_runs decode4: 2,299,300 vs 2,030,050 ticks, 0.88x, derived from page data), and the -O3 -march=x86-64-v3 build is slower than -O2 on several decode rows, so the 2.11x and 2.16x decode figures partly reflect an -O3 regression (vs -O2 those rows are 1.97x and 2.01x, derived from page data). The baseline is qoi.h, not libpng, libwebp or the other listed incumbents. README says it was produced by a multi-agent LLM workflow; the 'independent verifier' it mentions is part of that workflow. One commit, zero stars, published 2026-09-26, no outside reproduction.

Requires x86-64-v3 (Haswell 2013 or newer): older CPUs raise SIGILL, no ARM or other ISA, GNU as only. Drop-in for the four qoi.h symbols (qoi_encode, qoi_decode, qoi_write, qoi_read) with no algorithmic change, so the format and compression ratio are the same as qoi.h. Like qoi.h, qoi_decode may read a few bytes past the end on a truncated stream.

## Maintenance

Published 2026-09-26 as a single commit with 0 stars and no issues, produced by a multi-agent LLM workflow (the same author also publishes stb-image-opt and stb-image-write-opt). It is MIT-licensed, one roughly 1,000-line assembly file, and CI runs the differential, ASan/UBSan and benchmark-correctness suites on ubuntu-latest.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness tests/bench.c (built by the Makefile's bench target) links the untouched qoi.h oracle at -O2 and at -O3 -march=x86-64-v3 with asm/qoi.asm in one binary, checks all outputs bit for bit before timing, and reports median TSC ticks and ns; the committed tests/bench_after_D1.txt matches every docs/BENCHMARKS.md row (1.07x-2.16x over -O3), on a named CPU (i7-14700F) with flags in the Makefile and gcc 13.3.0 shown by the .ident of the committed ref_asm/\*.s files.
- **Verifier notes:** Harness, flags and result file check out; the oracle is byte-identical to upstream qoi.h and every BENCHMARKS.md ratio recomputes from tests/bench_after_D1.txt. Notability (0 stars, 1 commit, LLM-generated) and synthetic inputs are shortcomings, not grounds to reject; the one row slower than the -O2 C build is worth recording.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party harness, bit-identical output
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/tests/bench.c>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/tests/bench_after_D1.txt>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/docs/CHANGES_VS_UPSTREAM.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/docs/PORTING.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/c/qoi.c>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/c/qoi.h>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/ref_asm/qoi_O3_x86v3.s>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/ref_asm/qoi_O2.s>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/phoboslab/qoi/master/qoi.h>
  - <https://github.com/aplghl/qoi-asm>
  - <https://github.com/aplghl/qoi-asm/commits>
- **Sources the enricher read:**
  - <https://github.com/aplghl/qoi-asm>
  - <https://github.com/aplghl/qoi-asm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/README.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/docs/CHANGES_VS_UPSTREAM.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/docs/PORTING.md>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/asm/qoi.asm>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/tests/bench.c>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/tests/bench_after_D1.txt>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/tests/bench_after_E2.txt>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/tests/bench_after_M1.txt>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/c/qoi.c>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/c/qoi.h>
  - <https://raw.githubusercontent.com/aplghl/qoi-asm/HEAD/LICENSE>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/aplghl/qoi-asm`) · [data/wave10/enrich/raw/github_com_aplghl_qoi_asm.json](../../../data/wave10/enrich/raw/github_com_aplghl_qoi_asm.json) (enrichment confidence 0.8)

</details>
