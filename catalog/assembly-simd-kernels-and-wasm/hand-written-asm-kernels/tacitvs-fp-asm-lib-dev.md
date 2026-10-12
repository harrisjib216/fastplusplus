# FP-ASM (FP_ASM_LIB_DEV)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (NASM x86-64 AVX2) with a C API` · `MIT` · 🟢 active

> NASM AVX2 kernels with a C API for float reductions, dot products and batched vec3/mat4 math; beats strict-order scalar C loops.

| | |
|---|---|
| **Beats** | Scalar C reference loops compiled with gcc 13 -O3 -march=native |
| **Claimed result** | reduce sum (f32) 85.0 us scalar -O3 vs 9.9 us (8.6x); dot product (f32) 96.0 vs 18.9 us (5.1x); mat4 x vec3 batch 189 vs 122 us (1.5x); axpy 34.4 vs 34.2 us and scale 25.8 vs 25.7 us (parity). swarm_bench 1 thread on Emerald Rapids: total 7.01 vs 14.48 ms/frame (2.1x). |
| **Workload** | 100k-element f32 arrays, best of 200 runs: reduce sum, dot product, axpy, scale and a mat4 x vec3 batch transform; plus a 1M-star simulation (swarm_bench) FP-ASM versus plain C. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4600M (Haswell, AVX2) for the kernel table; Intel Xeon Emerald Rapids (AVX-512), 4 vCPUs for swarm_bench |
| **Compiler and flags** | gcc 13; benchmarks/bench_math.c is built by the Makefile bench target at -O3 -march=native (scalar reference and library caller alike); swarm_bench is built with the library CFLAGS -O3 -std=c11 -march=&lt;ISA, default native&gt;; reproduce with make bench and make run-swarm-bench |
| **Adoption** | 1 star |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/TACITVS/FP_ASM_LIB_DEV) · [benchmark](https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/README.md) |

## Verdict

On an Intel Core i7-4600M (Haswell) with gcc 13, both the library caller and scalar C reference loops built at -O3 -march=native, 100k-element f32 arrays, best of 200: sum 85.0 vs 9.9 us (8.6x), dot 96.0 vs 18.9 us (5.1x), batch mat4 x vec3 189 vs 122 us (1.5x), axpy and scale at parity; the reference is a single-accumulator strict-order loop gcc cannot vectorize without fast-math. swarm_bench (1M stars, Emerald Rapids Xeon, 1 thread) checks FP-ASM against plain C and reports 7.01 vs 14.48 ms per frame (2.1x), dropping to 1.4x with 4 threads while rendering.

## Use it when

- Hot f32/f64 sums, dot products, sums of squares or SAD over arrays of thousands of elements or more, in code you cannot build with -ffast-math or -fassociative-math, and where reassociated rounding is acceptable (README: 8.6x sum, 5.1x dot at 100k f32 on Haswell).
- int8/uint8 dot products on AVX-VNNI or AVX-512 VNNI CPUs, for example quantized vector scoring (fpasm-info --bench: 14-16x over the library's own AVX2 kernel on i7-13700HX and Emerald Rapids).
- CPU-side batched vertex transforms by a column-major mat4 in an x86-64 game or renderer (1.5x vs scalar -O3 at 100k vertices), with helpers for D3D11/D3D12/Vulkan/Metal/OpenGL projection conventions.
- C projects or FFI hosts (Common Lisp CFFI, Chez Scheme, Rust, Zig, Python ctypes) that want batch kernels behind a plain-C, pointer-plus-count ABI with an ABI version check.

## Skip it when

- Anything that is not x86-64 with AVX2 + FMA (no ARM/Apple Silicon path; pre-Haswell CPUs cannot run it).
- Memory-bound element-wise maps such as axpy and scale: the project's own table shows parity with autovectorized -O3 C.
- When results must match a sequential scalar sum bit for bit, or when you can enable -ffast-math, #pragma omp simd reduction or write a multi-accumulator C loop yourself; the project never measures those stronger C baselines, which likely close much of the reduction gap.
- Production-critical code that needs a mature dependency: single author, 1 star, and PORTING_STATUS.md lists many hot-kernel correctness and ABI bugs fixed only in July-October 2026.
- Performance-sensitive use of the L1 functional layer (closures, State monad): FP_COVERAGE.md says these allocate on every bind and run 1-2 orders of magnitude slower than an imperative loop.

## How it is fast

Reductions keep four independent YMM accumulators (32 floats per iteration) so the float add dependency chain that a strict-order C loop cannot break without -ffast-math is split across 32 partial sums; dot products use vfmadd231ps into the same four accumulators. The batch transform loads the four matrix columns once and does broadcast + FMA per vertex, two vertices per iteration, and the quaternion batch converts the quaternion to a 3x3 rotation matrix once per call. A runtime dispatcher selects AVX-512 or AVX-VNNI (vpdpbusd) variants of selected folds when the CPU has them.

## Compared with alternatives

Pick it over CvsAssemblyBenchmark (a single matmul demo) or seelabs/nasm (hex codec only) when you want a linkable, tested x86-64 library of float reductions and game-math batch kernels; ESP-DSP is the analogue for Xtensa/RISC-V microcontrollers, and asmlib targets libc string/memory replacements rather than numeric folds.

## Integration

| | |
|---|---|
| **Form** | static lib + shared lib (libfpasm.a / libfpasm.so / libfpasm.dll), Makefile or CMake target fpasm::fpasm |
| **Dependencies** | none at runtime; NASM &gt;= 2.13 and a C11 compiler (gcc or clang) to build |
| **Minimum toolchain** | NASM 2.13+, C11 gcc/clang (gcc &gt;= 13 or clang &gt;= 16 only for ISA=raptorlake) |
| **Platforms** | x86-64 Linux (System V) and Windows x64 (MinGW/MSYS2), AVX2 + FMA required; AVX-512 and AVX-VNNI variants of some folds picked at runtime |
| **Thread safety** | Documented as safe for concurrent calls: no mutable global state, constants in read-only memory, CPU-detection and dispatch tables initialized run-once; output buffers of concurrent calls must not overlap (tested with 16 threads and ThreadSanitizer). |
| **Drop-in for the baseline** | no |

## Gotchas

- Float results are reassociated (32 partial sums, FMA in dot) so they differ in the last bits from a strict-order loop; a NULL input pointer silently returns 0.0 (1.0 for products) instead of reporting an error.
- fp_mat4_mul_vec3_batch takes an int count but the SysV shim copies it with a 64-bit mov (mov r9, rcx) and the kernel tests only r9d before looping on the full 64-bit r9, so it relies on the caller leaving the upper 32 bits zero, which neither x86-64 ABI guarantees; counts are also capped at INT_MAX. Vec3f is 16 bytes (x, y, z, pad) and the kernel writes the fourth lane.
- The README kernel table was published with the v2 code on 2026-07-19; that version of fp_fold_dotp_f32 dropped four lanes of partial sums whenever n &gt;= 8 and n % 8 != 0 (VEX scalar tail op on xmm0 zeroed ymm0[255:128]), fixed 2026-10-04. The benchmark's n = 100,000 is a multiple of 32 so the timed work is unaffected, but benchmarks/bench_math.c times only and never compares outputs.
- swarm_bench harness asymmetry: in the motion stage fp_map_quat_rotate_vec3_f32 builds a 3x3 rotation matrix once per batch while the plain C c_rotate evaluates the full quaternion formula per star, so the 2.2x motion win is mostly algorithmic hoisting a C programmer could also do; the analysis-stage C loops (c_vsum, c_sumsq, c_sqdiff) are single-accumulator strict-order loops.

## Known shortcomings

- benchmarks/bench_math.c builds both sides -O3 -march=native (i7-4600M), but the baseline is a strict-order single-accumulator loop, so the reduce/dot wins are mostly float reassociation; axpy/scale at parity; the bench does not check results.
- The README kernel table dates from the v2 code (2026-07-19), in which fp_fold_dotp_f32 dropped four lanes of partial sums whenever n % 8 != 0 (a VEX scalar tail op on xmm0 zeroed ymm0[255:128]); fixed 2026-10-04. The benchmark's n = 100,000 never hits it and bench_math.c never checks outputs. Harness flaw in the swarm motion stage: the asm builds the rotation matrix once per batch while the plain C c_rotate runs the full quaternion formula per star, so the 2.2x motion win is hoisting, not assembly; the analysis-stage C loops are single-accumulator. Latent bug: fp_mat4_mul_vec3_batch tests r9d but loops on the full 64-bit r9, relying on the caller zeroing the upper 32 bits of the int count, which neither ABI guarantees.

## Caveats and trade-offs

The reduction wins come from multiple SIMD accumulators: the scalar reference (benchmarks/bench_math.c) is a single-accumulator strict-order loop that gcc cannot vectorize without -ffast-math or -fassociative-math, so a hand-unrolled or -ffast-math C loop would close much of the 8.6x/5.1x gap; outputs are not bit-identical to the strict-order loop. bench_math.c times only (best of 200, volatile sink) and does not compare results; swarm_bench does check FP-ASM vs plain C within float reassociation. Memory-bound kernels (axpy, scale) are at parity. Kernel table is one older laptop CPU (i7-4600M); the Emerald Rapids swarm numbers ran with the 100 MB working set in a large L3, and the demo rows under rendering drop to 1.4x total. Young project (1 star, 0 forks). [retier] The reduction wins come from multiple SIMD accumulators against a single-accumulator strict-order scalar loop that gcc cannot vectorize without -ffast-math, so a hand-unrolled or -ffast-math C loop would close much of the 8.6x/5.1x gap; outputs are not bit-identical to the strict-order loop. The README kernel table was published with the v2 code on 2026-07-19; that version of fp_fold_dotp_f32 dropped four lanes of partial sums whenever n &gt;= 8 and n % 8 != 0 (a VEX scalar tail op on xmm0 zeroed ymm0[255:128]), fixed 2026-10-04; the benchmark's n = 100,000 is a multiple of 32 so the timed work was unaffected, but benchmarks/bench_math.c times only (best of 200, volatile sink) and never compares outputs, so the measured kernel's correctness was never checked by the harness. swarm_bench harness asymmetry: in the motion stage fp_map_quat_rotate_vec3_f32 builds a 3x3 rotation matrix once per batch while the plain C c_rotate evaluates the full quaternion formula per star, so the 2.2x motion win is mostly algorithmic hoisting a C programmer could also do; the analysis-stage C loops are single-accumulator strict-order loops. Memory-bound kernels (axpy, scale) are at parity. The kernel table is one older laptop CPU (i7-4600M). Latent bug: fp_mat4_mul_vec3_batch takes an int count but the kernel tests only r9d before looping on the full 64-bit r9, relying on the caller zeroing the upper 32 bits, which neither x86-64 ABI guarantees; a NULL input pointer silently returns 0.0 (1.0 for products).

x86-64 AVX2 only (NASM required); float reductions use several SIMD accumulators so results differ in rounding from a strict scalar sum. Memory-bound element-wise kernels gain nothing.

## Maintenance

Active (238 commits, last 2026-10-07) and MIT-licensed, small enough to vendor, but a 1-star single-author project whose hot kernels had several correctness and ABI bugs fixed only in October 2026 (including a lost-lanes tail bug in fp_fold_dotp_f32 present when the README table was published, though not exercised at its n = 100,000), and whose microbenchmark never checks results.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** README kernel table (gcc 13, -O3 -march=native for both sides, Intel Core i7-4600M) comes from public benchmarks/bench_math.c, which the Makefile bench target builds at -O3 -march=native and times best-of-200 against scalar C reference loops; swarm_bench (examples/swarm/swarm_bench.c, Emerald Rapids Xeon, gcc 13) also checks FP-ASM output against plain C before timing.
- **Retiered** A to C: Enricher: the README kernel table was measured on the v2 code (2026-07-19) whose fp_fold_dotp_f32 dropped four lanes of partial sums for n % 8 != 0 (fixed 2026-10-04) while bench_math.c never checks outputs, and the swarm 2.2x motion win comes from hoisting the rotation matrix per batch that the plain C baseline recomputes per star. Numbers measured on a kernel later fixed for a correctness bug (libfacedetection precedent): A to C.
- **Verifier notes:** Numbers on the README match the record exactly (8.6x reduce, 5.1x dot, 1.5x mat4 batch, parity axpy/scale; swarm_bench 7.01 vs 14.48 ms/frame). Benchmark source opened and is honest about using the same -O3 -march=native for the C reference; main shortcoming is that the baseline is a strict-order scalar loop, so the reduction speedups mostly reflect float reassociation. Metadata confirmed: MIT, 1 star, last commit 2026-10-07, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-30 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/README.md>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/commits>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/Makefile>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/benchmarks/bench_math.c>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/examples/swarm/swarm_bench.c>
- **Sources the enricher read:**
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/commits/main>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/issues?q=is%3Aissue>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/tree/main/src/asm>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/commits/main/benchmarks/bench_math.c>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/commits/main/src/asm/fp_core_fused_folds_f32.asm>
  - <https://github.com/TACITVS/FP_ASM_LIB_DEV/commits/main/README.md>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/README.md>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/Makefile>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/benchmarks/bench_math.c>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/examples/swarm/swarm_bench.c>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/examples/swarm/swarm_sim.c>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/examples/swarm/swarm_sim.h>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/src/asm/fp_core_reductions_f32.asm>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/src/asm/fp_core_fused_folds_f32.asm>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/src/asm/3d_math_kernels.asm>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/src/asm/fp_core_matrix.asm>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/src/asm/abi.inc>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/include/fp_types.h>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/tests/test_reductions.c>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/FP_COVERAGE.md>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/HEAD/PORTING_STATUS.md>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/2ce7f6a/README.md>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/2ce7f6a/PORTING_STATUS.md>
  - <https://raw.githubusercontent.com/TACITVS/FP_ASM_LIB_DEV/2ce7f6a/src/asm/fp_core_fused_folds_f32.asm>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tacitvs/fp_asm_lib_dev`) · [data/wave13/enrich/raw/github_com_tacitvs_fp_asm_lib_dev.json](../../../data/wave13/enrich/raw/github_com_tacitvs_fp_asm_lib_dev.json) (enrichment confidence 0.8)

</details>
