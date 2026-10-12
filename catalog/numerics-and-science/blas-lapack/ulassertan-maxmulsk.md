# MaxMulSK

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Single-threaded FP32 SME/SME2 GEMM for Apple M4; published v3 beats an SME-enabled OpenBLAS build, trails Accelerate.

| | |
|---|---|
| **Beats** | OpenBLAS (tuned build reaching its own SME kernels, one thread) and Apple Accelerate |
| **Claimed result** | README: v5.1 (development kernel, code not yet published) is 1.86x tuned OpenBLAS (geometric mean of paired ratios, ahead on 33 of 35 shapes, tied on 2) and 1.16x Apple Accelerate (behind at 256^3: 0.74x). For the published v3 kernel (2026-09-09 session): 1.40 to 1.77 TFLOP/s end to end on squares 256^3 to 4096^3, 1.01x to 1.31x OpenBLAS on squares and 1.36x to 2.23x on LLM shapes, but 5 to 17% behind Accelerate at most sizes. |
| **Workload** | Single-thread FP32 GEMM over 35 shapes (squares, LLM-shaped, DeepSeek-V3 and LLaMA shapes) with allocation, packing and writeback inside every timed call, on an Apple M4 using Arm SME2. |
| **Metric** | throughput |
| **Hardware** | Apple M4, macOS 26.6.2, AC power |
| **Compiler and flags** | Homebrew LLVM/Clang 22.1.8 (docs/BENCHMARKS.md). The bench_headline target compiles bench/bench_headline.cpp with -O3 -Wall -Wextra -mcpu=apple-m4 (no -fopenmp), and the v3 SME kernel and gemm_tuning sources with -march=armv8.7-a+sme+sme2 (CMakeLists.txt). OpenBLAS is loaded by dlopen with openblas_set_num_threads(1) and OPENBLAS_NUM_THREADS=1. Accelerate is limited with VECLIB_MAXIMUM_THREADS=1; the 29 September session pinned it with BLASSetThreading. For the SME-capable OpenBLAS the author built the develop branch with DYNAMIC_ARCH=1 (OPENBLAS_DIRECT_LIMIT=1792 in the 29 September session). |
| **Adoption** | 0 stars, 39 commits |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/UlasSertan/MaxMulSK) · [benchmark](https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/README.md) |

## Verdict

The reproducible claim is the 9 September 2026 session of bench/bench_headline.cpp: Homebrew Clang 22.1.8, -mcpu=apple-m4 and -march=armv8.7-a+sme+sme2, Apple M4 on macOS 26.6.2, one thread, FP32, allocation and packing inside the timed call. There the published v3 reached 1396-1768 GFLOP/s on squares 256^3-4096^3, which is 1.01-1.31x an OpenBLAS develop build reaching its SME kernels and 1.36-2.23x on LLM shapes, but only 0.83-1.05x of Accelerate. The 29 September table (v5.1: 1.86x OpenBLAS and 1.16x Accelerate, geometric mean over 35 shapes) comes from unpublished code.

## Use it when

- Single-threaded FP32 row-major GEMM on an Apple M4 where Accelerate is not an option and OpenBLAS is the alternative. The published v3 is 1.01-1.31x an SME-enabled OpenBLAS develop build on squares 256^3-4096^3 and 1.36-2.23x on M=64/128 LLM shapes.
- Replacing Homebrew's OpenBLAS on M4. That build cannot reach its own SME kernels and falls off above 1024^3, per the README.
- Large squares (1024^3, 4096^3), where the published v3 edged Accelerate by 1.05x and 1.02x in the 9 September session.
- Learning SME kernel design. The repo documents every generation, the ablations and the failed experiments (bdirect, pack-once) with dated raw data.

## Skip it when

- You can call Accelerate. The published v3 trails it on most shapes: 0.83x at 256^3, 0.93x at 512^3, 0.97x at 2048^3 and 0.92-0.95x on the LLM shapes. v4c also trails it by 3-5% on the LLaMA shapes.
- You want the headline numbers (1.86x OpenBLAS, 1.16x Accelerate, 1.06x MpGEMM). Those come from the v5.1 kernel, whose code is not in the repository, measured with a separate harness.
- You need multithreading, FP64, transposed or strided (lda) operands, column-major data, or C = alpha\*A\*B + beta\*C. None of these are supported, and SME multi-threading is listed as future work.
- Any chip other than Apple M4. M1-M3 lack SME. pack_A's transpose is hard-coded for a 512-bit streaming vector length (TODO.md: 'Not portable').
- Production use that needs a stable API. It is a 0-star single-student project with no library target, and the namespace-level entry point changes from generation to generation.

## How it is fast

It runs a BLIS-style blocked GEMM on Arm SME. A 1x4 geometry (a 16x64 FP32 output tile spread over four 16x16 ZA tiles) does four FMOPA outer products per A vector. A is packed through a ZA-tile transpose and B through SVE stores. The v2/v3 change keeps ZA live across the whole K panel, with K innermost: ZA is zeroed once per C tile and drained once with one svst1_f32_x4 per row, and the first K panel stores without a read-modify-write. That cut per-call fixed cost from 357 ns to 52 ns. v3 adds an outer Kc panel so the packed buffers scale with Kc rather than K. Blocking comes from a small per-shape table (gemm_tuning) whose entries are kept only if they won in three separate runs.

## Compared with alternatives

MTGEMM-A (MIT, all code public) covers the same M4 SME niche with FP64, alpha/beta, leading dimensions, both storage orders and two-SME-unit threading, and MPGEMM's code is now public too, so prefer those for real use. Pick MaxMulSK only for single-threaded FP32 row-major work on an M4 where you want its documented kernel history, or once v5.1 (reported 1.06x MpGEMM on the same M4) is published.

## Integration

| | |
|---|---|
| **Form** | source-drop (copy sme/v3/sme-1x4-acc-kcout.{hpp,cpp} and sme/support/gemm_tuning.{hpp,cpp}; the CMake project builds only executables) |
| **Dependencies** | The kernel needs only the ACLE headers arm_sme.h and arm_sve.h. The repo build also needs Homebrew libomp and CMake 3.30+. OpenBLAS (dlopen), KleidiAI (fetched at v1.30.0, can be turned off), llama.cpp/ggml, NumPy and PyTorch are needed only for benchmarks. |
| **Minimum toolchain** | C++20; Homebrew LLVM/Clang (README: Apple's bundled Clang lacks the SME/SME2 intrinsics; results used Clang 22.1.8); kernel sources compiled with -march=armv8.7-a+sme+sme2 |
| **Platforms** | Apple M4 only (SME/SME2, 512-bit streaming vector length), macOS |
| **Thread safety** | Not documented. The library is single-threaded internally. The v3 entry point allocates its own buffers per call, keeps no shared mutable state, and reads the MAXMULSK_BLOCKING environment variable on every call. |
| **Drop-in for the baseline** | no |

## Gotchas

- The v3 KcOut kernel overwrites C (C = A\*B). Its header says every other MaxMulSK SME kernel accumulates (C += A\*B), so swapping kernels changes semantics.
- Each call std::aligned_alloc's about 8.5 MB of packing buffers (1024x2048 floats for A plus 64x2048 for B at the default blocking) and does not check for a null return.
- MAXMULSK_BLOCKING='M_tile,N_tile,Kc,ir_outer' overrides the blocking on every call. The parser rejects only zero values, while the header requires N_tile to be a multiple of the kernel's N_step.
- Sibling kernels in the repo returned silently wrong results before fixes (4x1 pack_A when M_tile &gt; 64; the same latent bug 'still sits in the v1 kernel', per gemm_tuning.cpp). Use only the v3 1x4 path the README documents. Timings of short calls such as 256^3 depend on the work that ran just before.

## Known shortcomings

- Tier A covers only the published v3 claim (bench/bench_headline.cpp, Clang 22.1.8, M4); the v5.1 headline code is unpublished.
- Published v3 trails Accelerate on most shapes (0.83x at 256^3, 0.92-0.95x on LLM shapes); allocates \~8.5 MB per call with std::aligned_alloc and no null check; MAXMULSK_BLOCKING env override read every call without checking N_tile is a multiple of N_step; other kernels in the repo had silent wrong-result bugs and one is still latent in v1; Apple M4 only (pack_A hard-coded for 512-bit vectors).

## Caveats and trade-offs

The headline v5.1 numbers (29 September 2026) come from a kernel whose code is not in the repository, measured with what the README calls 'the project's separate benchmark harness'. The reproducible claims are the published v3 path (bench/bench_headline.cpp, raw CSV in bench/results/2026-09-09/) and v4c versus Accelerate (bench/results/2026-09-13/v4c3.csv). v5.1 loses to Accelerate at 256^3 (0.74x) and is within 5% of OpenBLAS at 256^3 and 512^3 (0.98x, 1.03x). It trails MpGEMM at 256^3 (0.82x), at 512^3 (0.94x) and on two DeepSeek-V3 M=64 shapes (0.94x). MpGEMM's code is public (github.com/mpgemm/MPGEMM, MIT), and MaxMulSK benchmarks its row_sgemm entry point through the bench_vs_mpgemm target. The README says v3 trails Accelerate 'by 5 to 17% elsewhere', but its own 9 September table shows 0.97x at 2048^3. Timings of small calls depend on what ran just before them. macOS offers no thread pinning, run-to-run variance reaches 12% on the worst shapes, and the author treats differences under about 5% as noise. Homebrew's OpenBLAS cannot reach its SME kernels and falls off above 1024^3, so the author built OpenBLAS develop. Results are single-threaded FP32 on Apple M4 only (SME/SME2 required). It is a single-maintainer student project in a brand-new repository with 0 stars.

C++20 library for Apple M4 only (needs SME/SME2); single-threaded FP32 row-major C = A\*B with packing and blocking done internally; Homebrew clang and libomp required. Not a BLAS ABI drop-in.

## Maintenance

Active (39 commits, last 2026-09-29) and Apache-2.0, so it is copyable. It is a 0-star single-maintainer student project with no releases, and its best kernel (v5.1) is not yet published.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** bench/bench_headline.cpp (MaxMulSK v3 vs Apple Accelerate vs OpenBLAS) is public with raw CSVs under bench/results/2026-09-09/; the compiler (Homebrew Clang 22.1.8, docs/BENCHMARKS.md), the flags (CMakeLists.txt) and the CPU (Apple M4) are all stated. Tier A covers the published v3 claim only. The v5.1 headline cannot be reproduced until its code is published.
- **Verifier notes:** The README numbers match the record: v3 1.01-1.31x on squares and 1.36-2.23x on LLM shapes against OpenBLAS; v5.1 4096^3 1732/1246/1595 GFLOP/s and 128x32768x512 1280 vs 370. The record wrongly calls MpGEMM code-less: github.com/mpgemm/MPGEMM exists (MIT, 11 stars, IPDPS '26, arXiv 2512.21473). The wave8 entry paper:mpgemm-arm-sme (repo_url null, has_code false) should be updated with that repository.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/UlasSertan/MaxMulSK>
  - <https://github.com/UlasSertan/MaxMulSK/commits>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/README.md>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/bench/bench_headline.cpp>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/LICENSE>
  - <https://github.com/mpgemm/MPGEMM>
- **Sources the enricher read:**
  - <https://github.com/UlasSertan/MaxMulSK>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/README.md>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/sme/v3/sme-1x4-acc-kcout.hpp>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/sme/v3/sme-1x4-acc-kcout.cpp>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/sme/support/gemm_tuning.hpp>
  - <https://raw.githubusercontent.com/UlasSertan/MaxMulSK/HEAD/sme/support/gemm_tuning.cpp>
  - <https://github.com/mpgemm/MPGEMM>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ulassertan/maxmulsk`) · [data/wave8/enrich/raw/github_com_ulassertan_maxmulsk.json](../../../data/wave8/enrich/raw/github_com_ulassertan_maxmulsk.json) (enrichment confidence 0.8)

</details>
