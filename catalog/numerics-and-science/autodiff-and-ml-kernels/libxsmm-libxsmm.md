# LIBXSMM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> JIT-generated small GEMM, batch-reduce GEMM and element-wise kernels; DL layers built on it beat MKL-DNN by 1.1-1.7x.

| | |
|---|---|
| **Beats** | MKL-DNN (oneDNN) |
| **Claimed result** | LSTM cell forward 1.2-1.3x and bwd/upd 1.1-1.7x faster than MKL-DNN; fully connected layers 1.16x (C=K=256), 1.36x (512), 1.09x (1024); ResNet-50 forward convolutions 83% vs MKL-DNN 81% efficiency (MKL-DNN 2.5% slower fwd, 1% bwd, 7% upd) (paper body, arXiv 1906.06440, published IEEE IPDPS 2020; abstract itself has no numbers) |
| **Workload** | Batch-reduce GEMM based LSTM, fully-connected and CNN (ResNet-50) primitives built on LIBXSMM, on Skylake-SP. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8180 (Skylake-SP), 28 cores/socket, AVX-512 |
| **Compiler and flags** | Intel compiler 18.0.0 (flags not stated); turbo disabled |
| **Adoption** | 977 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/libxsmm/libxsmm) · [benchmark](https://arxiv.org/abs/1906.06440) |

## Verdict

In Georganas et al. (IPDPS 2020, arXiv 1906.06440), Intel authors built LSTM, fully-connected and ResNet-50 convolution layers on LIBXSMM's batch-reduce GEMM and measured them against 2019 MKL-DNN on a 28-core Xeon Platinum 8180 with Intel compiler 18.0.0: LSTM 1.2-1.3x faster forward and 1.1-1.7x backward/update, FC 1.09-1.36x, ResNet-50 conv efficiency 83% vs 81%. Flags were not stated and the paper notes the gains shrink for large matrices.

## Use it when

- Many repeated multiplications of small matrices, roughly (M\*N\*K)^(1/3) &lt;= 64, e.g. block-sparse or spectral-element/DG codes (CP2K/DBCSR, SeisSol, Nek5000, PETSc block kernels).
- Writing custom CPU DL operators (conv, FC, RNN, attention blocks) as blocked loops around BRGEMM plus fused element-wise TPPs.
- Low-precision CPU kernels (BF16, FP16, FP8 variants, int8/int4, MX formats) on AVX-512 VNNI/AMX, Arm SVE/SME or POWER10 without hand-writing assembly.
- Shipping one binary that should pick the right ISA at runtime ('build once, deploy everywhere') without -march flags.

## Skip it when

- Large GEMMs: there is no multi-level M/N/K cache blocking; large sizes generate excessive unrolled code and miss cache tiling, so use MKL/OpenBLAS/BLIS.
- You want ready-made DL layers: in 2.0 they moved to libxsmm-dnn and the PyTorch integration to tpp-pytorch-extension; the core repo only gives primitives.
- Full BLAS semantics: JIT GEMM kernels are limited to alpha=1, beta in {0,1}, transA='N' (BLAS-style wrapper falls back otherwise).
- Windows deployments needing more than the MM domain: the Compatibility wiki lists Windows JIT as MM-only without prefetch kernels.
- GPU workloads: CPU-only.

## How it is fast

Runtime code specialization: for each (M,N,K,ld,datatype,flags) it emits machine code fully unrolled for that shape, using the best ISA found via CPUID (AVX-512/VNNI/BF16, AMX, NEON/SVE/SME, RVV, POWER10 MMA), with operand prefetch hints for batches. The batch-reduce GEMM kernel (C = beta\*C + sum_i A_i\*B_i) keeps the output block in registers across a whole sequence of A/B block pairs, so higher-level layers become loops around one tuned microkernel instead of separate GEMM calls with C round-trips through memory.

## Compared with alternatives

Pick LIBXSMM over Fastor when shapes are runtime values or you need low-precision/AMX/SVE kernels rather than compile-time fixed-size C++ tensors (Fastor can even use LIBXSMM as its JIT backend); pick it over the AVX512 DGEMM tutorial kernels or llamafile tinyBLAS when you need a maintained, multi-ISA library of small/batched GEMMs rather than large-GEMM or LLM-specific kernels.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (GNU Make or CMake 3.13+), or header-only via libxsmm_source.h |
| **Dependencies** | none for the core; libxsmmext and the Fortran module need an OpenMP runtime; Fortran compiler optional (FORTRAN=0) |
| **Minimum toolchain** | C compiler; GCC 5.1+ recommended (older GCC degrades CPUID-dispatched code); Clang, Intel; Fortran 2003 for the module |
| **Platforms** | x86-64 (SSE through AVX-512/AMX), AArch64 (NEON/SVE/SME), RISC-V RVV, POWER10 ppc64le; Linux, macOS, FreeBSD, Windows (limited JIT) |
| **Thread safety** | Thread-safe: core routines can be called concurrently; threading-runtime agnostic (PGI and TinyCC builds have caveats). |
| **Drop-in for the baseline** | partial — libxsmm_?gemm is BLAS-ABI compatible for small GEMM, but it does not replace oneDNN; DL layers must be composed from TPPs or taken from libxsmm-dnn |

## Gotchas

- Shapes over the JIT limits (operand &gt;2 GiB, or &gt;2 MB stack scratch for VNNI reformatting) silently fall back to a slow reference kernel; check libxsmm_get_kernel_info or run with LIBXSMM_VERBOSE=2.
- The public header is generated at build time (not in the repo); header-only use exposes internals and compiles your settings (e.g. NDEBUG) into LIBXSMM.
- No error returns from the frontend: failures are reported only via verbose mode, so a NULL kernel pointer must be checked by the caller.
- With verbosity on it installs SIGABRT/SIGSEGV handlers; set LIBXSMM_SIGNAL=0 if the host application owns signals.

## Known shortcomings

- Authors are from Intel, same vendor as the MKL-DNN baseline; paper gives no code link; flags not stated (Intel compiler 18.0.0).
- Since 2.0 the paper's DL layers (LSTM, FC, conv) live in libxsmm/libxsmm-dnn; core covers small matrices only ((MNK)^(1/3) &lt;= 64), larger shapes silently fall back to a slow reference kernel; JIT GEMM only alpha=1, beta 0/1, no transpose of A; Windows JIT limited to matmul.

## Caveats and trade-offs

Numbers are in the paper body, not the abstract; venue is IPDPS 2020, not SC'19. Authors are Intel (same vendor as MKL-DNN). Paper gives no code link for the DL primitives (built on LIBXSMM's batch-reduce GEMM); numbers are vs 2019 MKL-DNN at small/medium sizes; full compiler flags not stated. LIBXSMM README has no oneDNN comparison.

JIT code generation; library ABI or header-only; x86 (SSE-AMX), AArch64, RISC-V, PowerPC targets.

## Maintenance

Actively developed (commits in late Sept 2026, 2.0 release restructured the repo) and BSD-3-Clause, packaged in Debian/Fedora/Ubuntu/Spack/Conda; note the benchmarked DL operators now live in libxsmm-dnn.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (Georganas et al., 'Harnessing Deep Learning via a Single Building Block', IEEE IPDPS 2020; arXiv 1906.06440) shows LIBXSMM batch-reduce-GEMM primitives beating MKL-DNN on Xeon Platinum 8180 with Intel compiler 18.0.0; no code link or full flags in the paper, so not A.
- **Verifier notes:** Record numbers check out against the paper text; fixed the venue/abstract attribution. Metadata (BSD-3-Clause, 977 stars, last commit 2026-09-28, not archived) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1906.06440>
  - <https://arxiv.org/abs/1906.06440v1>
  - <https://arxiv.org/pdf/1906.06440>
  - <https://github.com/libxsmm/libxsmm>
  - <https://github.com/libxsmm/libxsmm/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/libxsmm/libxsmm/HEAD/README.md>
  - <https://raw.githubusercontent.com/libxsmm/libxsmm/HEAD/documentation/libxsmm_mm.md>
  - <https://github.com/libxsmm/libxsmm/wiki/Compatibility>
  - <https://arxiv.org/abs/1906.06440>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/libxsmm/libxsmm`) · [data/wave8/enrich/raw/github_com_libxsmm_libxsmm.json](../../../data/wave8/enrich/raw/github_com_libxsmm_libxsmm.json) (enrichment confidence 0.8)

</details>
