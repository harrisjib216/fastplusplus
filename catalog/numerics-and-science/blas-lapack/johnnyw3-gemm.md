# gemm (johnnyw3, AVX/AMX kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `no license` · 🟢 active

> Hand-written AVX2/AVX-512/AMX square GEMM kernels; 3-4% faster than OpenBLAS/MKL only on Granite Rapids AMX (bf16).

| | |
|---|---|
| **Beats** | OpenBLAS or Intel MKL, whichever was faster on each machine (OpenBLAS built with BUILD_BFLOAT16=1 for AMX) |
| **Claimed result** | AMX on Granite Rapids Xeon 6972P: 1279 vs 1229 GFLOPS single-threaded (1.04x) and 4810 vs 4675 with 4 threads (1.03x); but slower on AVX2 Kaby Lake i5-8350U (78 vs 103, 0.76x; 213 vs 282 with 4 threads) and AVX-512 Tiger Lake i5-1135G7 (106 vs 122, 0.87x; 380 vs 465 with 4 threads). |
| **Workload** | fp32 (AVX2, AVX-512) and bf16-input/fp32-output (AMX) GEMM, n=4096, single-threaded and 4 threads, average of 10 runs. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon 6972P (Granite Rapids), Core i5-1135G7 (Tiger Lake), Core i5-8350U (Kaby Lake) |
| **Compiler and flags** | clang++ (version not stated; clang 16+ or gcc 13+ required for AMX), -march=\$(TARGET) -O3 -flto -g -fsave-optimization-record -DNUM_THREADS=&lt;n&gt; (Makefile); TARGET used on each machine not stated |
| **Adoption** | 1 star |
| **Last commit** | 2025-10-08 |
| **Links** | [repository](https://github.com/johnnyw3/gemm) · [benchmark](https://github.com/johnnyw3/gemm) |

## Verdict

With clang++ -O3 -flto -march=&lt;target&gt; at n=4096, averaged over repeated runs, the README reports 1279 vs 1229 GFLOPS (1.04x) single-threaded and 4810 vs 4675 GFLOPS (1.03x) with 4 threads for the AMX bf16 kernel on a Xeon 6972P, against whichever of OpenBLAS sbgemm and MKL bf16 GEMM was faster. On AVX2 and AVX-512 it is 13-24% slower. The README does not say which library won each row, its version or thread setting (bench.cxx does not limit BLAS threads), or which -march target was used.

## Use it when

- Intel Sapphire/Granite Rapids-class CPUs with AMX, bf16 inputs and FP32 output, square n that is a multiple of the superblock size (n=4096 measured), 1-4 threads.
- Learning or teaching how an AMX bf16 GEMM is built (tile config, VNNI relayout of B, packing) from about 950 lines of readable intrinsics.
- Small fixed-shape experiments where you control NUM_THREADS and -march at build time and can verify results against a BLAS.

## Skip it when

- AVX2 or AVX-512 machines: it is slower than the better of OpenBLAS/MKL, 0.76x on a Kaby Lake i5-8350U and 0.82-0.87x on a Tiger Lake i5-1135G7.
- Any shape other than square n divisible by the superblock size (AMX: 2048 rows, 1024 columns and depth; AVX2: 512; AVX-512: 1024 rows, 512 columns, 256 depth): there is no edge handling, and the source says matrices must be padded.
- More than about 8 threads, or a thread count that does not split n into whole superblocks: the partitioning arithmetic then hands some threads rows past the end of the matrix (12 threads on the AVX2 path at n=4096 starts threads 8-11 at row 4096 and beyond), or splits K across threads that read-modify-write the same C tiles without synchronization (16 threads on AMX at n=4096). The default NUM_THREADS is nproc.
- Production or redistribution: no LICENSE file, no tests beyond the bench's exact-equality check on integer matrices from utils/random_gen.py (values 0-100), no issues or releases, single author.

## How it is fast

Goto/BLIS-style cache blocking with two levels ('superblocks' of blocks): panels of A and B are packed into contiguous, 64-byte-aligned stack buffers sized for L1/L2, then a register-blocked micro-kernel runs. The AVX2/AVX-512 micro-kernels compute a 2-row x 8-column patch of C as dot products along K (two passes of 4 columns, 16 vector accumulators) with FMAs over a pre-transposed B and finish with unpack/permute horizontal reductions; the AMX kernel keeps four 16x16 FP32 accumulator tiles and issues TDPBF16PS on two A tiles and two B tiles, with B re-laid into the VNNI pair-interleaved format by AVX-512 expand-loads inside the packing step (commit history credits that move for a 1.15-1.2x gain). Threads split the i and j dimensions of C.

## Compared with alternatives

It is the only catalogued CPU entry with an Intel AMX bf16 kernel, so pick it to study or prototype on Sapphire/Granite Rapids. For FP32 on AVX2/AVX-512 it loses to its baseline, so GEMM_AVX2_FMA3 (2-3% over MKL 2019), cpu_gemm_opt or sgemm.c (salykova, whose article inspired this code) are better references; for production, use OpenBLAS, MKL or BLIS.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | pthreads; OpenBLAS (built with BUILD_BFLOAT16=1 for AMX) or Intel MKL only for the bench program |
| **Minimum toolchain** | C++ compiler with x86 intrinsics; clang 16+ or gcc 13+ for the AMX path (__bf16); the Makefile uses clang++ with -march=\$(TARGET) -O3 -flto |
| **Platforms** | x86-64 only: AVX2 minimum, AVX-512 or AMX-TILE/AMX-BF16 paths selected at compile time; Linux assumed (pthreads, aligned_alloc) |
| **Thread safety** | Spawns and joins its own NUM_THREADS pthreads per call; concurrent calls on different outputs look independent (packing buffers are per-thread stack arrays), but this is not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The kernels are non-inline function definitions in gemm.h, so include it in exactly one translation unit, compiled with the right -march and -DNUM_THREADS; the installed libgemm.a holds only gemm.cxx's unused amx_relayout helper.
- simd_gemm accumulates into C (C += A\*B), so zero C first; the AVX paths expect B already transposed (bench.cxx calls cpu_transpose before the timed loop, so that cost is not in the AVX numbers), while the AMX path takes B as-is.
- Nothing in the repository calls arch_prctl(ARCH_REQ_XCOMP_PERM); Linux traps the first AMX tile instruction until the process requests that permission (kernel xstate documentation). bench.cxx calls the BLAS first, so a standalone program must request it itself.
- Per-thread packing buffers live on the stack: about 6 MiB per thread on the AMX path (4 MiB A panel plus 2 MiB B panel) and 2 MiB on AVX2, so small thread stacks will overflow.

## Known shortcomings

- Wins only on AMX (3-4%) and is 13-24% slower on AVX2/AVX-512; which of OpenBLAS/MKL won each row, their versions and thread limits are unstated; README says 10 runs but the code does 30; no license.
- Memory/correctness bugs (code read): the thread partition overruns the matrix when NUM_THREADS does not split n into whole superblocks (AVX2, 12 threads, n=4096: threads 8-11 start past row 4096); the K split across threads races on C (AMX, 16 threads; a code comment admits the missing combine); no arch_prctl AMX permission request (works in the bench only because the BLAS call runs first); B transpose excluded from AVX timing; non-inline kernels in gemm.h.

## Caveats and trade-offs

Beats the baseline only on AMX hardware (3-4%); on AVX2 and AVX-512 it is 13-24% slower; the baseline is the better of OpenBLAS and MKL chosen per machine, but the README does not say which library won each row, their versions, or how the baseline was limited to one thread (bench.cxx does not set the BLAS thread count); the README says 'average of 10 runs' while bench.cxx averages 30 timed calls per invocation; the AMX comparison is bf16-input/fp32-output against OpenBLAS sbgemm or MKL bf16 GEMM; no LICENSE file in the repository, so the code cannot be copied; one size (n=4096); compiler version not stated; multithreading does not scale beyond 8 threads per the README.

x86 only (AVX2, AVX-512, AMX); the AMX path takes bf16 inputs; multithreaded code does not scale well beyond 8 threads; README says the best results are single/lightly threaded; no license file.

## Maintenance

Single-author hobby/study project, last commit 2025-10-08 (47 commits, 1 star, no issues); there is no license, so it is reference-only and cannot be vendored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README tables give GFLOPS for this library vs the faster of OpenBLAS/MKL on three named CPUs at n=4096; the benchmark code is public (bench.cxx times cblas_sgemm / cblas_sbgemm or MKL cblas_gemm_bf16bf16f32_compute against the library), and the Makefile states clang++ with -march=\$(TARGET) -O3 -flto. Compiler version and per-machine TARGET are not given, which is within past A precedent (compiler named, flags in build file, CPU model stated).
- **Verifier notes:** All six speedup pairs match the README. Metadata checked on github.com: no license (LICENSE, LICENSE.md, COPYING all 404), 1 star, not a fork, last commit 2025-10-08 (within 12 months, active). Small win against an under-specified baseline; worth recording as a shortcoming.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/johnnyw3/gemm>
  - <https://github.com/johnnyw3/gemm/commits>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/bench.cxx>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/bench.h>
- **Sources the enricher read:**
  - <https://github.com/johnnyw3/gemm>
  - <https://github.com/johnnyw3/gemm/commits>
  - <https://github.com/johnnyw3/gemm/issues>
  - <https://github.com/johnnyw3/gemm/tree/master/utils>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/gemm.h>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/gemm.cxx>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/simd_common.h>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/bench.cxx>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/bench.h>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/utils/random_gen.py>
  - <https://raw.githubusercontent.com/johnnyw3/gemm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/torvalds/linux/master/Documentation/arch/x86/xstate.rst>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/johnnyw3/gemm`) · [data/wave8/enrich/raw/github_com_johnnyw3_gemm.json](../../../data/wave8/enrich/raw/github_com_johnnyw3_gemm.json) (enrichment confidence 0.8)

</details>
