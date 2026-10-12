# CvsAssemblyBenchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Assembly (GNU as, AVX2/FMA) with C harness` · `MIT` · 🟢 active

> Toy benchmark: hand-written AVX2/FMA GNU-as i-k-j double matmul beating a GCC -O3 build restricted to SSE2.

| | |
|---|---|
| **Beats** | GCC 12.2.0 -O3 compiled C i-k-j dense matrix multiply (double precision) |
| **Claimed result** | Mean internal timer C 3.043 s vs assembly 1.823 s per 1,000 multiplications (1.66x); about 2.63 vs 4.39 GFLOP/s. |
| **Workload** | 200 x 200 x 200 double-precision matrix multiply repeated 1,000 times, five runs, outputs compared (max absolute difference 1.42e-14). |
| **Metric** | throughput |
| **Hardware** | x86-64 (AVX2/FMA-capable); CPU model not stated |
| **Compiler and flags** | gcc -O3 -Wall -Wextra -fPIE -pie (GCC 12.2.0); assembly built with GNU as 2.40 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-05-12 |
| **Links** | [repository](https://github.com/reza-ebrahimi/CvsAssemblyBenchmark) · [benchmark](https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/README.md) |

## Verdict

On an unnamed AVX2/FMA x86-64 CPU (GCC 12.2.0, binutils 2.40), 1,000 multiplications of 200x200 double matrices took a mean 3.043 s for the C i-k-j loop built with -O3 (baseline x86-64, so SSE2) against 1.823 s for the AVX2/FMA assembly over five runs (1.66x, about 2.63 vs 4.39 GFLOP/s); no AVX2/FMA build of the C loop and no BLAS were measured.

## Use it when

- As a readable teaching example of an AVX2/FMA broadcast-and-FMA inner loop in GNU as Intel syntax, including the System V calling details it had to fix (clock_gettime argument order, varargs stack order, vzeroupper).
- As a starting point for a classroom demonstration of compiler flags: rebuild matrix_benchmark.c with -O3 -march=x86-64-v3 (or -mavx2 -mfma) and compare against the shipped assembly.
- Only on x86-64 Linux CPUs with AVX2 and FMA (Haswell or Zen 1 and later), with square-ish matrices whose column count is a multiple of 8.

## Skip it when

- Any real dense matrix multiply: the kernel has no register or cache blocking, reaching about 4.4 GFLOP/s on 200x200 doubles; use a BLAS such as BLIS or OpenBLAS (wave 8 entries) instead.
- As evidence that hand-written assembly beats GCC: the C side was compiled for baseline x86-64 (SSE2, no FMA) and an AVX2/FMA build of the same C loop was never measured.
- Matrices whose B has fewer than 8 columns: the .scalar_only path jumps past `xor edx, edx`, so the column counter is uninitialised and results are wrong or the loop indexes out of bounds.
- Column counts that are not a multiple of 8 when bit-reproducibility or speed matters: the tail uses legacy-SSE mulsd/addsd (no FMA, non-VEX) after 256-bit code, mixing roundings and risking SSE/AVX transition stalls.
- Non-Linux, non-x86-64 or pre-AVX2 targets: there is no CPU dispatch or fallback, and the file is GNU as syntax only.

## How it is fast

The assembly inner loop broadcasts A[i][k] into a YMM register (vbroadcastsd) and updates eight doubles of the C row per iteration with two 256-bit vfmadd231pd, 2x unrolled; the C build has no -march/-mavx2/-mfma, so GCC can only emit 2-wide SSE2 mulpd plus addpd. The gain therefore comes from vector width and FMA, not from scheduling the compiler could not do; neither side uses register or cache blocking, so every k step re-loads and re-stores the C row and all of B is streamed once per output row.

## Compared with alternatives

Rarely: FP-ASM (TACITVS) measures its hand-written kernels against gcc -O3 -march=native and seelabs/nasm against g++ -O3 reference code, so their ratios say more about assembly versus a compiler; pick this only as a minimal AVX2/FMA matmul teaching example, and use a BLAS for actual matrix work.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | glibc (malloc, fopen/fread/fwrite, memset, clock_gettime, printf); Python 3 for verify.py |
| **Minimum toolchain** | GNU as with Intel-syntax AVX2/FMA support (README: binutils 2.40, GCC 12.2.0) |
| **Platforms** | x86-64 Linux, AVX2 and FMA required |
| **Thread safety** | not documented; matrix_mul uses only its arguments and registers (no globals), so separate output matrices can be computed concurrently |
| **Drop-in for the baseline** | partial — matrix_mul uses the same Matrix struct layout as the C harness but is a local label; it must be made .global and called with a column count that is a multiple of 8 and at least 8 |

## Gotchas

- Shipped output does not come from the FMA kernel: the committed output_asm.bin is bit-identical to output_c.bin (0 of 40,000 elements differ) and equals a non-FMA i-k-j recomputation from the committed matrix_a.bin/matrix_b.bin, while an FMA recomputation differs in 13,999 elements (max 2.84e-14, exactly the first README's table). The file was produced by the earlier scalar SSE2 assembly and never regenerated, so `make verify` on the repo's files shows no FMA difference, and the current README's 1.42e-14 figure came from a different random draw (gen_matrix seeds with time(NULL)).
- Baseline crippled by build flags: CFLAGS = -O3 -Wall -Wextra -fPIE with no -march, so the README's claim that gcc 'auto-vectorizes with AVX' and emits vmulpd + vaddpd cannot hold; the 1.66x mostly measures 4-wide FMA against 2-wide SSE2. The repo description's '\~150% faster' contradicts the README's 1.66x.
- The assembly timer passes clock id 0 (CLOCK_REALTIME) although its comments and the README say CLOCK_MONOTONIC (the C side uses CLOCK_MONOTONIC); the first README's numbers were wall-clock only because the original timer call had swapped arguments (fixed in a20dc02). The Makefile ITERS variable is never passed to either program, so the README's `make benchmark ... ITERS=500` example still runs 1,000 iterations.
- ABI shortcuts in the assembly: matrix_load, matrix_mul, matrix_save, matrix_create and matrix_free call into libc with a stack misaligned by 8 bytes, main overwrites callee-saved r12-r15 without saving them, and matrix_load ignores fread failures (the C version checks them).

## Known shortcomings

- Downgraded C to D: the C baseline is built -O3 -fPIE with no -march, -mavx2 or -mfma, so it can only use SSE2 while the asm uses AVX2/FMA (crippled-baseline precedent); the README's claim that the C build auto-vectorizes with AVX cannot hold for those flags; no CPU model; 0 stars.
- The C baseline is built without -march, so GCC 12.2 emits SSE2 only and the 1.66x is mostly 4-wide FMA against 2-wide SSE2. The committed output_asm.bin is a stale non-FMA file, bit-identical to output_c.bin, while an FMA recompute differs in 13,999 of 40,000 elements (max 2.84e-14, matching the first README), so 'make verify' shows 0 diffs and the README's 1.42e-14 came from another random draw. Assembly bugs: a B matrix with fewer than 8 columns jumps past 'xor edx, edx', leaving the column counter uninitialised (wrong results or out-of-bounds writes); the asm timer uses clock id 0 (CLOCK_REALTIME) although its comments claim MONOTONIC; the Makefile ITERS is never used; libc calls run with the stack misaligned by 8 bytes; main overwrites r12-r15 without saving them.

## Caveats and trade-offs

Baseline crippled by build flags: the Makefile builds the C benchmark with -O3 -Wall -Wextra -fPIE only, so GCC 12.2.0 targets baseline x86-64 (SSE2, 2-wide, no FMA) while the assembly uses 256-bit AVX2 vfmadd231pd; the 1.66x mostly measures vector width and FMA, not hand-written code, and an -O3 -march=x86-64-v3 (or -mavx2 -mfma) build of the same i-k-j loop was never measured. The README's statement that gcc -O3 'auto-vectorizes with AVX' and emits vmulpd + vaddpd cannot be true for the stated flags. The asm binary has no CPU dispatch and needs AVX2/FMA. The repo description says 'Assembly is \~150% faster' while the README data show 1.66x (66% faster). CPU model not stated; five runs of one 200x200 size; single-author toy project (4 commits on 2026-05-12, 0 stars). Outputs differ by up to 1.42e-14 (FMA single rounding); the asm does zero C and run 1,000 full multiplications, so the timing is not a no-op.

x86-64 AVX2/FMA only; single fixed matrix size; FMA changes rounding relative to separate multiply and add.

## Maintenance

Single-author experiment of four commits on 2026-05-12 with 0 stars and no issues; MIT-licensed and small enough to copy, but it is a demonstration program with a small-matrix correctness bug and a stale committed output file, not a reusable kernel.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** Code (matrix_benchmark.c, matrix_benchmark_gas.s, Makefile), GCC 12.2.0 and flags are public but no CPU model is given, so at most C; the comparison itself is ISA-unequal (hand-written AVX2/FMA against a C build with CFLAGS = -O3 -Wall -Wextra -fPIE and no -march/-mavx2/-mfma, so GCC can only emit baseline x86-64 SSE2 code), which follows the AssemblyScript precedent for a baseline crippled by a build default (C to D).
- **Verifier notes:** Numbers on the README match the record (C 3.043 s vs asm 1.823 s mean internal timer, 1.66x, about 2.63 vs 4.39 GFLOP/s). Main shortcoming: the C baseline was built without -mavx2/-mfma, so it cannot use the instructions the asm uses; no fair compiler comparison exists. MIT licence, last commit 2026-05-12, metadata otherwise correct.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-32 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/README.md>
  - <https://github.com/reza-ebrahimi/CvsAssemblyBenchmark>
  - <https://github.com/reza-ebrahimi/CvsAssemblyBenchmark/commits>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/matrix_benchmark.c>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/matrix_benchmark_gas.s>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/reza-ebrahimi/CvsAssemblyBenchmark>
  - <https://github.com/reza-ebrahimi/CvsAssemblyBenchmark/commits>
  - <https://github.com/reza-ebrahimi/CvsAssemblyBenchmark/commit/a20dc02>
  - <https://github.com/reza-ebrahimi/CvsAssemblyBenchmark/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/matrix_benchmark.c>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/matrix_benchmark_gas.s>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/gen_matrix.c>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/verify.py>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/matrix_a.bin>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/matrix_b.bin>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/output_c.bin>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/HEAD/output_asm.bin>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/65d89ed/README.md>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/65d89ed/matrix_benchmark_gas.s>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/a20dc02/README.md>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/a20dc02/matrix_benchmark_gas.s>
  - <https://raw.githubusercontent.com/reza-ebrahimi/CvsAssemblyBenchmark/fd0ac24/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/reza-ebrahimi/cvsassemblybenchmark`) · [data/wave13/enrich/raw/github_com_reza_ebrahimi_cvsassemblybenchmark.json](../../../data/wave13/enrich/raw/github_com_reza_ebrahimi_cvsassemblybenchmark.json) (enrichment confidence 0.85)

</details>
