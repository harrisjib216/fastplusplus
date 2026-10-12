# CKTSO-GPU

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++ (CUDA; solver shipped as prebuilt x86-64 Windows/Linux binaries, demos in C++)` · `None stated: no LICENSE file, and README.md and ug.pdf give no terms; prebuilt x86-64 Windows/Linux binaries only, used on top of the separately distributed CKTSO library` · 🔴 abandoned

> Closed-source CUDA add-on to CKTSO for sparse LU refactorization and solve; first-party 13.3x geomean refactorization speedup over KLU.

| | |
|---|---|
| **Beats** | KLU 1.3.9 (SuiteSparse; run with CKTSO's ordering); also CKTSO version 20221123 on 1 CPU thread |
| **Claimed result** | Re-factorization: CKTSO-GPU is 28.80X (arithmetic mean) / 13.29X (geometric mean) faster than KLU and 12.01X / 6.11X faster than CKTSO (1 thread). Solving: 2.41X / 1.72X faster than KLU and 1.98X / 1.46X faster than CKTSO (1 thread). Per-matrix times appear only as bar charts. |
| **Workload** | Sparse LU re-factorization time and forward/backward solve time for 29 SuiteSparse circuit matrices with Flops/NZ(L+U) &gt; 50, on an RTX 3090 versus single-thread CPU CKTSO and sequential KLU. |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6130 (16 cores, 2.1 GHz), NVIDIA GeForce RTX 3090 (24 GB), 256 GB RAM |
| **Compiler and flags** | gcc 4.8.5 and nvcc 11.0 on CentOS 7.9.2009 x64 (optimization flags not stated); 32-bit integer interface |
| **Adoption** | 6 stars |
| **Last commit** | 2023-04-01 |
| **Links** | [repository](https://github.com/chenxm1986/cktso-gpu) · [benchmark](https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/results.pdf) |

## Verdict

First-party results.pdf (CKTSO-GPU 20221207), 29 SuiteSparse circuit matrices with Flops/NZ(L+U) &gt; 50: refactorization on an RTX 3090 is 13.29x faster on geometric mean (28.80x arithmetic) than sequential KLU 1.3.9 given CKTSO's ordering, and 6.11x (12.01x) faster than CKTSO on one thread of a Xeon Gold 6130. Solve is 1.72x (2.41x) faster than KLU and 1.46x (1.98x) faster than one-thread CKTSO. Built with gcc 4.8.5 and nvcc 11.0 on CentOS 7.9; flags are not stated, there is no benchmark code, and per-matrix results appear only as bar charts.

## Use it when

- SPICE Newton/transient loops that refactor the same circuit-matrix pattern thousands of times while the pivot order from one CPU factorization stays acceptable.
- Slightly dense circuit matrices that pass the user guide's flops/NNZ(L+U) &gt; 50 test, the only class it was benchmarked on.
- You already use CKTSO on x86-64 Windows or Linux and have an NVIDIA GPU of compute capability 3.5-8.0 with a CUDA 11 driver.
- Real or complex matrices with a single right-hand side per solve.

## Skip it when

- Highly sparse circuit matrices: the user guide itself says it cannot accelerate them efficiently and that multicore CKTSO is best there.
- You have a many-core CPU: the GPU was compared only with one-thread CKTSO and sequential KLU. The CKTSO README separately claims more than 25x over KLU at 16 threads (66 matrices, a different set), which exceeds this module's 13.29x geomean over KLU, so multithreaded CKTSO may match or beat it (cross-document, not like-for-like).
- You need pivoting on the GPU: factorization with pivoting stays on the CPU, and every CPU refactorization that changes the LU structure requires calling InitializeGpuAccelerator again.
- You need source code, a license, non-x86-64 hosts, AMD GPUs, or post-Ampere GPUs: it ships only prebuilt x86-64 binaries with no license terms, built with CUDA 11.0, and the listed compute capabilities stop at 8.0.
- Long-term support: the last commit was 2023-04-01, and the CKTSO README lists a 'faster GPU acceleration method' as work in progress.

## How it is fast

Refactorization reuses the pivot order and LU pattern fixed by the CPU factorization, so there is no pivot search and the column dependencies are known in advance; the GPU can then factor independent columns in parallel. The guide exposes a threshold (iparm[1], default 128) that switches refactorization between a 'bulk' and a 'pipeline' mode, and it picks blocks per multiprocessor and threads per block automatically. This matches the author's published GPU left-looking LU (DAC 2012, TPDS 2015), which uses a cluster mode for early dependency levels with many sparse independent columns and a pipeline mode for late levels with few, denser columns (per search snippets; the source is closed, so the exact algorithm is not visible). Gains come from matrices with enough work per factor nonzero; the guide's threshold is flops/NNZ(L+U) &gt; 50.

## Compared with alternatives

Use it only if you already run CKTSO and your matrices pass the flops/NNZ(L+U) &gt; 50 test. Otherwise multithreaded CKTSO (same author, maintained, TCAD 2025 paper) or BSD-licensed Basker on the CPU is the safer choice, and GLU is a public-source GPU circuit LU you can build and modify.

## Integration

| | |
|---|---|
| **Form** | shared lib (prebuilt libcktsogpu.so / cktsogpu.dll + .lib, with _l variants for 64-bit indices; header cktso-gpu.h) |
| **Dependencies** | CKTSO shared library and header plus its cktso.lic file (separate repo; CKTSO 20230325 or later); NVIDIA CUDA 11.0 runtime and driver (Linux 450.51.05, Windows 451.48 or newer) |
| **Minimum toolchain** | Prebuilt with gcc 4.8.5 on CentOS 7 and Visual Studio 2019 on Windows, CUDA 11.0; plain C API usable from C or C++ (demo Makefile uses g++ -O3) |
| **Platforms** | x86-64 Windows or Linux only; NVIDIA GPUs with compute capability 3.5, 3.7, 5.0, 5.2, 6.0, 6.1, 7.0, 7.5 or 8.0 listed (RTX 3090 used in results); V100 needs the disabledL1cache build |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Wrong results on some GPUs: disabledL1cache/readme.txt says the V100 needs the L1-cache-disabled libraries, which cost about 20% performance. Check residuals on your GPU.
- GpuRefactorize does no pivoting. If changed values make a pivot unacceptable, fall back to CKTSO factorization with pivoting on the CPU and re-initialize the accelerator; CKTSO's scaling option (its iparm[7]) is not supported on the GPU.
- Values and vectors are passed in host memory, and results.pdf does not say whether its timings include host-device transfers; oparm[1]/oparm[2] report the module's own timings.
- Return codes are mixed: negative values are CKTSO errors (-51 to -53 are GPU-specific), and positive values are raw cudaError_t codes (e.g. 209, no kernel image, on an unsupported GPU). Call CKTSO_SortFactors before initializing, or initialization is slower.

## Known shortcomings

- Tier C: every ratio (refactor 28.80x/13.29x vs KLU, solve 2.41x/1.72x) comes from the vendor's results.pdf with no benchmark code or flags; binaries only, no license stated. Per ug.pdf the GPU module only pays off when flops/NNZ(L+U) &gt; 50; on sparse matrices the multicore CKTSO is the better pick. It is the GPU add-on of the already-listed CKTSO.
- GpuRefactorize does no pivoting. V100 gives wrong results unless the L1-cache-disabled libraries are used (about 20% slower). Compute capabilities are listed only up to 8.0 with CUDA 11.0 builds. Benchmarked only against 1-thread CKTSO and sequential KLU; the CKTSO README claims over 25x over KLU at 16 threads on a different matrix set, above the GPU's 13.29x geomean, and lists 'Faster GPU acceleration method' as ongoing work.

## Caveats and trade-offs

First-party results.pdf (CKTSO-GPU version 20221207; the PDF is dated 2022-12-07) only; no benchmark code is public and the solver source is not available (prebuilt x86-64 Windows/Linux libraries plus C/C++ demos), so this cannot be rerun. The GPU is compared only with CKTSO on ONE thread and with sequential KLU, not with multithreaded CKTSO, NICSLU, cuSOLVER or GLU, so the speedup is partly a GPU-vs-one-core comparison. The user guide (ug.pdf, version 20230325) itself says CKTSO-GPU cannot efficiently accelerate highly sparse circuit matrices, that plain CKTSO on multicore CPUs gives the best performance on extremely sparse ones, and recommends the GPU module only when flops/NNZ(L+U) &gt; 50, where it 'tends to perform faster than CKTSO (1 thread)'; the 29 test matrices were selected with exactly that filter. KLU is given CKTSO's ordering. Compiler versions are stated (gcc 4.8.5, nvcc 11.0) but optimization flags are not. GpuRefactorize and GpuSolve take the matrix values and vectors in host memory, but results.pdf does not say whether the reported times include host-device transfers. disabledL1cache/readme.txt says some GPUs (V100 named) give wrong results unless L1 cache is disabled, at about 20% performance loss. No license text in the repo (reference only), and it needs the separately distributed CKTSO library. Last commit 2023-04-01 (GitHub commits page), more than 3 years before today, so abandoned. Per-matrix times appear only as bar charts.

Closed-source: the repo ships only prebuilt x86-64 libraries (libcktsogpu.so, cktsogpu.dll, plus _l 64-bit-integer variants), a header, and demo sources; it also needs the CKTSO library and its cktso.lic from the sibling repo. NVIDIA/CUDA only. Per its own user guide it only helps slightly-dense circuit matrices (recommended when flops/NNZ(L+U) &gt; 50) and cannot efficiently accelerate highly sparse circuit matrices; plain multicore CKTSO is best for those. One right-hand side per solve call. Pivoting factorization still runs on the CPU; only re-factorization and solve run on the GPU.

## Maintenance

Abandoned since 2023-04-01 (22 commits, 6 stars), binary-only with no license terms, so reference only; tied to CUDA 11.0-era builds and an external licensed CKTSO library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** results.pdf is first-party and compares CKTSO-GPU with KLU 1.3.9 and CKTSO (1 thread); every ratio in claimed_speedup appears verbatim on it (28.80X/13.29X and 12.01X/6.11X refactor, 2.41X/1.72X and 1.98X/1.46X solve). Compilers and CPU/GPU models are stated, but there is no public benchmark code and no optimization flags, so it cannot be A.
- **Verifier notes:** All numbers, versions, hardware and compilers in the record match results.pdf exactly; I only filled in the license text and added the user guide's own limits (GPU module worthwhile only for Flops/NNZ(L+U) &gt; 50; multicore CPU CKTSO is best for very sparse matrices). This is a GPU add-on module of CKTSO (already listed), with its own repo, binaries and claims, so I kept it as a separate entry; fold it into the CKTSO entry if you prefer.
- **Fields the verifier corrected:** `license`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/results.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/ug.pdf>
  - <https://github.com/chenxm1986/cktso-gpu>
  - <https://github.com/chenxm1986/cktso-gpu/commits>
  - <https://github.com/chenxm1986/cktso-gpu/tree/master/disabledL1cache>
- **Sources the enricher read:**
  - <https://github.com/chenxm1986/cktso-gpu>
  - <https://github.com/chenxm1986/cktso-gpu/commits>
  - <https://github.com/chenxm1986/cktso-gpu/issues>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/results.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/ug.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/disabledL1cache/readme.txt>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/howto.txt>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/cktso-gpu.h>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/demo.cpp>
  - <https://raw.githubusercontent.com/chenxm1986/cktso-gpu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/chenxm1986/cktso-gpu`) · [data/wave8/enrich/raw/github_com_chenxm1986_cktso_gpu.json](../../../data/wave8/enrich/raw/github_com_chenxm1986_cktso_gpu.json) (enrichment confidence 0.75)

</details>
