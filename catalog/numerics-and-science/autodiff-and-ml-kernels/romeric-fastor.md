# Fastor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ fixed-size tensor library whose small-GEMM kernels match MKL JIT and beat padded Blaze.

| | |
|---|---|
| **Beats** | Eigen 3.3.7 / Blaze 3.7 / MKL JIT 2021.01 / LIBXSMM (small fixed-size GEMM, single-threaded) |
| **Claimed result** | Wiki text: 'Fastor's performance is on par with Intel's MKL JIT API' for small matrix multiplication; Blaze (with padding) is 'between the same speed to being over 2X slower in some cases while in general being about 50% slower'. Eigen comparison only in plots, no numbers in text. |
| **Workload** | Small fixed-size tensor/matrix operations and tensor-network contractions with compile-time operation minimisation. |
| **Metric** | throughput |
| **Hardware** | Intel i5-8259U (macOS), Intel Xeon E3-1240 v6, Intel Xeon Gold 6128 (Linux) |
| **Compiler and flags** | GCC 9.2 -O3 -DNDEBUG -mavx2 -mfma; GCC 7.4.0 -O3 -DNDEBUG -mavx512f -mavx512vl -mavx512cd -mavx512bw -mavx512dq -mfma |
| **Adoption** | 844 stars |
| **Last commit** | 2025-07-08 |
| **Links** | [repository](https://github.com/romeric/Fastor) · [benchmark](https://github.com/romeric/Fastor/wiki/Benchmarks) |

## Verdict

The wiki's small-GEMM benchmarks (cbrt(MNK) &lt;= 128, single-threaded, float/double/complex) against Eigen 3.3.7, Blaze 3.7, LIBXSMM (Apr 2020 devel) and MKL JIT 2021.01, built with GCC 9.2 -O3 -DNDEBUG -mavx2 -mfma on i5-8259U and Xeon E3-1240 v6 and GCC 7.4 with AVX-512 flags on Xeon Gold 6128, show Fastor at parity with MKL JIT and padded Blaze roughly 50% slower (up to 2x in some cases). Results are plots only, and the Eigen gap is not quantified in text.

## Use it when

- Many repeated small dense ops (roughly 2x2 to 64x64, sizes known at compile time), e.g. per-element or per-quadrature-point kernels in finite-element / continuum mechanics codes.
- Higher-order tensor contractions and einsum with fixed dimensions, where compile-time contraction-order optimisation cuts FLOPs.
- Embedded / FPGA / no-heap environments: no dynamic allocation and no RTTI.
- When you want small-GEMM speed near MKL JIT/LIBXSMM without linking a vendor library.

## Skip it when

- Medium or large matrices: issue #42 reports Fastor \~2x slower than Eigen at 128x128 (fine at 8x8, equal at 64x64); matmul is a register-blocked loop nest without the cache tiling/packing/threading of a BLAS.
- Runtime-sized data: there is no dynamic-size tensor type.
- Non-x86 SIMD: the built-in SIMDVector layer covers SSE2..AVX-512 only; other architectures fall back to scalar unless you configure the Vc or std::experimental::simd backend.
- Large dot products/reductions over long vectors: open issue #141 shows einsum \~2.3x slower than hand-written OpenMP-SIMD/AVX2 at 100k elements (while far faster on small ones).
- Projects that need a broad, actively developed library: commits are sparse (two in 2025, two in 2024).

## How it is fast

All sizes are template parameters, so SIMD kernels (SSE2 to AVX-512, FMA) for matmul and contractions are statically dispatched and fully unrolled for the exact shape, with no runtime dispatch or heap allocation. 'Smart' expression templates rewrite expressions at compile time (e.g. trace(A^T B) to inner(A,B), det(inv(A)) to 1/det(A), matrix-chain reordering) and a compile-time cost model picks a FLOP-minimal contraction order for tensor networks. Optional LIBXSMM or MKL-JIT backends can take over matmul.

## Compared with alternatives

Pick Fastor over LIBXSMM when you want a header-only, high-level tensor API (einsum, views, small LU/QR/inverse) for fixed shapes rather than a JIT GEMM library; LIBXSMM is the better choice for runtime-shaped small GEMM or DL primitives. Pick it over TCL when tensor shapes are compile-time and small; TCL targets larger runtime-shaped contractions.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optional: LIBXSMM, MKL JIT, sleef, Vc) |
| **Minimum toolchain** | C++14 (config.h #errors below it); tested GCC 5.1-10.1, Clang 3.6-10, ICC 16-19, MSVC 2019 |
| **Platforms** | x86 / x86-64 with SSE2-AVX-512 kernels; other CPUs via scalar fallback or Vc/std::experimental::simd backend |
| **Thread safety** | not documented (value-type tensors on the stack; no shared state described) |
| **Drop-in for the baseline** | no |

## Gotchas

- Performance depends on -march/-mavx2 -mfma/-mavx512\* flags and -DNDEBUG; without them it compiles to SSE2 or scalar code.
- auto on an expression or view holds an unevaluated expression/reference; assign to a Tensor to materialise it.
- matmul(A, transpose(B)) creates a temporary transpose (per maintainer in issue #42).
- Large fixed sizes live on the stack and inflate compile time and binary size.

## Known shortcomings

- Results only as plots, no numbers in text; headline claim is only parity with MKL JIT; padded Blaze is 'in general about 50% slower'.
- Benchmarked library versions date from 2020; issue #42: \~2x slower than Eigen at 128x128 (\~2x faster at 8x8); open issue #141: einsum \~2.3x slower than hand-written SIMD on 100k dot products; sparse commits (2 in 2025, 2 in 2024); built-in SIMD x86 only.

## Caveats and trade-offs

All numbers are in plots, none stated in text; the headline claim is parity with MKL JIT, not a win; Eigen comparison not quantified in text. Library versions are from \~2020. README also has plots vs hand-written C/Fortran loops (-O3 -mavx, Xeon E5-2650 v2).

Header-only, fixed-size tensors only, no dynamic allocation; compile-time cost for large expressions.

## Maintenance

MIT-licensed, not archived, but low activity (last commits July 2025, previous ones 2024); v0.6.4 is the latest release and the benchmark library versions date from 2020.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgrade: the wiki Benchmarks page compares Fastor against Eigen 3.3.7, Blaze 3.7, LIBXSMM and MKL JIT 2021.01 with public code (benchmark/external, make + benchmark_plot.py), stating GCC 9.2 -O3 -DNDEBUG -mavx2 -mfma on i5-8259U and Xeon E3-1240 v6, and GCC 7.4.0 with AVX-512 flags on Xeon Gold 6128. Results are plots only.
- **Verifier notes:** Upgraded C-&gt;A on reproducibility grounds, but the actual 'faster' claim is weak (parity with MKL JIT, about 50% faster than padded Blaze); the orchestrator may want to record 'plot-only evidence' as a shortcoming. Metadata (MIT, 844 stars, last commit 2025-07-08, not archived) confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/romeric/Fastor>
  - <https://github.com/romeric/Fastor/commits>
  - <https://github.com/romeric/Fastor/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/romeric/Fastor/HEAD/README.md>
  - <https://raw.githubusercontent.com/romeric/Fastor/HEAD/benchmark/external/README.md>
- **Sources the enricher read:**
  - <https://github.com/romeric/Fastor>
  - <https://github.com/romeric/Fastor/commits>
  - <https://github.com/romeric/Fastor/releases>
  - <https://github.com/romeric/Fastor/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/romeric/Fastor/HEAD/README.md>
  - <https://raw.githubusercontent.com/romeric/Fastor/HEAD/Fastor/config/config.h>
  - <https://raw.githubusercontent.com/romeric/Fastor/HEAD/CMakeLists.txt>
  - <https://github.com/romeric/Fastor/issues/42>
  - <https://github.com/romeric/Fastor/issues/141>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/romeric/fastor`) · [data/wave8/enrich/raw/github_com_romeric_fastor.json](../../../data/wave8/enrich/raw/github_com_romeric_fastor.json) (enrichment confidence 0.75)

</details>
