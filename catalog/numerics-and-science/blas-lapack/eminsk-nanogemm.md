# NanoGEMM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Tiny AVX2/NEON float32 GEMM C kernel behind a Python extension; beats NumPy/OpenBLAS call latency for matrices up to \~64x64.

| | |
|---|---|
| **Beats** | OpenBLAS (through NumPy 2.2.x sgemm / matmul) |
| **Claimed result** | NanoGEMM vs NumPy: 16x16 1.71 us vs 4.05 us (2.36x; 0.68 us for the C kernel, 5.5x); 24x24 2.67 us vs 19.39 us (7.26x); 32x32 4.21 us vs 7.14 us; 48x48 11.15 us vs 12.65 us; 64x64 13.89 us vs 19.69 us (1.42x); 128x128 115.90 us vs 89.44 us (0.77x, slower). |
| **Workload** | Single-threaded float32 square matmul (16x16 to 128x128) called from Python through NumPy arrays. The README states 'median latency across 10,000 iterations with cache pre-warming', but benchmarks/bench_vs_numpy.py times the mean per-call latency of one loop (25,000 to 50 iterations depending on size) and notebooks/benchmark.ipynb takes the best of 3 loop means (10,000/3,000/1,000 iterations); NumPy's `A @ B` allocates a new output each call while NanoGEMM writes into a preallocated `out=` buffer. |
| **Metric** | latency |
| **Hardware** | Unnamed x86-64 CPU with AVX2+FMA (no model given); INT8 and batched tests on Google Colab CPU |
| **Compiler and flags** | GCC -O3 -mavx2 -mfma / MSVC /O2 /arch:AVX2; NumPy 2.2+ linked against OpenBLAS; single thread |
| **Adoption** | 3 stars; packaged on PyPI, conda-forge and an APT PPA |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/eminsk/nanogemm) · [benchmark](https://github.com/eminsk/nanogemm) |

## Verdict

First-party README table, timed through Python on an unnamed AVX2+FMA x86-64 CPU (GCC -O3 -mavx2 -mfma, single thread) against NumPy 2.2.3 '@' backed by OpenBLAS: 1.71 vs 4.05 us at 16x16, 4.21 vs 7.14 us at 32x32, 13.89 vs 19.69 us at 64x64, and slower at 128x128 (115.90 vs 89.44 us). The shipped benchmark reports mean loop time (the notebook takes best of 3), not the median the README states, NanoGEMM writes into a preallocated buffer while NumPy allocates each result, and the 7.26x headline at 24x24 rests on an outlying NumPy timing.

## Use it when

- Many tiny float32 matmuls (16x16 to \~64x64) called from Python in a loop, where NumPy's per-call overhead dominates and you can reuse a preallocated out= buffer.
- You need a few hundred lines of dependency-free C to vendor for small row-major float32 GEMM on AVX2+FMA or NEON, and can live with a non-BLAS API.
- Free-threaded or multi-threaded Python where you run independent small GEMMs in parallel threads (the kernel releases the GIL and is single-threaded per call).
- Reading material: a compact example of a 6x16 AVX2 micro-kernel with boundary tiles.

## Skip it when

- Matrices of 128x128 and up: the project's own table shows it slower than NumPy/OpenBLAS at 128x128 (0.77x), and with no packing or threading it falls further behind at larger sizes.
- Anything needing float64, complex, transposed or column-major operands, or the rest of BLAS/LAPACK.
- x86 machines without AVX2+FMA: the x86 build uses -mavx2 -mfma with no CPUID check, so the module will fault with an illegal instruction instead of falling back.
- Production code that needs a mature, tested library: 3 stars, 0 forks, released in 2026, and its CI cannot fail (every step ends in '|| true'); pytest collects only the ISA test from tests/test_correctness.py because the other checks are named run_\* rather than test_\*.
- Fast int8 inference: the int8 kernels widen to int32 and use _mm256_mullo_epi32 (no VNNI or vpmaddubsw path) and have no K blocking.

## How it is fast

Register-blocked outer-product micro-kernels: on x86 a 6x16 AVX2/FMA tile held in 12 ymm accumulators (broadcast an A element, two 8-wide B loads, two FMAs), with 4x16, 2x16 and 6/4/2x8 boundary kernels; on ARM a 4x8 NEON tile. Loops are cache-blocked (64x128x128) but nothing is packed, so there is no packing cost, no threading and no runtime dispatch; the Python wrapper calls the kernel through the buffer protocol with the GIL released. The speedup over NumPy at small sizes comes mostly from skipping per-call dispatch and output allocation rather than from faster arithmetic.

## Compared with alternatives

Pick it over BLASFEO or Eigen only when the call site is Python and per-call overhead on tiny float32 matrices is the bottleneck; from C or C++, BLASFEO (small dense linear algebra with packed panel-major storage and LAPACK-style factorizations) or Eigen's fixed-size products are more complete and better tested.

## Integration

| | |
|---|---|
| **Form** | source-drop (two C files) or Python extension (pip/conda; PyPI 0.3.8 ships only a cp314 win_amd64 wheel plus an sdist, so other platforms compile from source) |
| **Dependencies** | none for the C kernel; NumPy for the Python package |
| **Minimum toolchain** | C99-style C with GCC/Clang target attributes or MSVC /arch:AVX2; Python &gt;= 3.8 for the extension (exact compiler versions not documented) |
| **Platforms** | x86-64 with AVX2+FMA (required), aarch64/Apple Silicon NEON; scalar fallback only on other architectures |
| **Thread safety** | Kernels keep no global state and allocate nothing, so concurrent calls on distinct outputs are safe (by code reading); the extension releases the GIL and declares Py_MOD_GIL_NOT_USED for free-threaded CPython. |
| **Drop-in for the baseline** | partial — ng.matmul/ng.sgemm can replace NumPy '@' for 2D float32 row-major arrays, and nanogemm_sgemm resembles cblas_sgemm minus layout/transpose arguments; not ABI- or API-compatible with OpenBLAS |

## Gotchas

- Possible memory-safety bug (code read, not run): ng.matmul without a backend argument calls the C fast path first, and that path checks only ndim and the inner dimension, not dtype, contiguity or the out= shape. float64 or non-contiguous inputs are read as if contiguous float32 (silent wrong results), and an undersized out= array is written past its end; the wrapper's own validation runs only if the C call raises.
- Built with -ffast-math (/fp:fast on MSVC), so NaN/Inf propagation and summation order differ from IEEE-strict BLAS results.
- get_simd_isa() reports the compile-time macros, not the running CPU; on MSVC (which does not define __FMA__) it reports 'AVX2' even though the FMA kernels are used.
- Uses int for M, N, K and index arithmetic, so very large matrices can overflow (not an issue in the small-size range it targets).

## Known shortcomings

- README says median but the bench reports a mean (notebook: best of 3); only NumPy pays to allocate its output while NanoGEMM writes into a preallocated buffer; the 7.26x headline at 24x24 rests on a NumPy outlier; the INT8 table uses NumPy's int8 matmul, which skips BLAS and returns wrapping int8 (not like-for-like); no CPU model.
- Possible memory-safety bug (code read): ng.matmul with no backend calls _ext.matmul_fast, which checks only ndim and K, not dtype, contiguity or out= shape, so float64 or strided input gives silently wrong results and an undersized out= is written past its end; every CI step ends in '|| true' and pytest collects only the ISA test; no CPUID check (faults without AVX2); -ffast-math.

## Caveats and trade-offs

First-party; CPU model not stated. Timed through Python, so NumPy per-call dispatch (README quotes 3-5 us fixed cost) dominates the small sizes; no direct cblas_sgemm call is compared. The README says 'median over 10,000 iterations' but the shipped benchmark code reports mean loop time (notebook: best of 3), and only the baseline pays for allocating its output (NanoGEMM uses a preallocated out= buffer). The headline 7.26x at 24x24 rests on a NumPy outlier (19.39 us at 24x24 vs 7.14 us at 32x32); 24 and 48 come from the Colab notebook, not bench_vs_numpy.py. NumPy/OpenBLAS thread count is not pinned. Slower than NumPy at 128x128 (0.77x). The INT8 table compares against NumPy int8 `@`, which does not use BLAS and returns int8 (wrapping) while NanoGEMM returns int32, so it is not a like-for-like baseline. Very new project (3 stars) with a marketing-style README; the dev.to article was not checked.

Static AVX2/FMA (6x16) and ARM NEON (4x8) register-tiled micro-kernels, no JIT, no threads, about 100 KB binary. Strongest only for matrices up to about 64x64; float32 and int8 only. The C kernel is in src/nanogemm_kernel.c/.h so it can be used from C or C++, but the project is packaged and documented as a Python extension.

## Maintenance

Actively developed (last commit 2026-09-28, 62 commits, 0 issues), MIT-licensed and small enough to vendor, but very young, single-author and marketing-heavy; treat it as a Python micro-optimization rather than a BLAS replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table vs NumPy 2.2.3 (OpenBLAS) with public benchmark code (benchmarks/bench_vs_numpy.py, notebooks/benchmark.ipynb) and flags (-O3 -mavx2 -mfma), but the CPU model is never named ('Intel/AMD x86-64 CPU', 'Google Colab CPU'), so not A.
- **Verifier notes:** README numbers match the record exactly. Methodology mismatches worth recording: README claims median timing but code reports mean/best-of-3, the baseline alone allocates its output, and the INT8 'vs NumPy' table compares against a non-BLAS int8 matmul with a different (overflowing) output type. Last commit 2026-09-28, MIT, 3 stars, 0 forks confirmed.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/eminsk/nanogemm>
  - <https://github.com/eminsk/nanogemm/commits>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/benchmarks/bench_vs_numpy.py>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/notebooks/benchmark.ipynb>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/eminsk/nanogemm>
  - <https://github.com/eminsk/nanogemm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/src/nanogemm_kernel.c>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/src/nanogemm_kernel.h>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/src/nanogemm_pyext.c>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/nanogemm/core.py>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/nanogemm/__init__.py>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/benchmarks/bench_vs_numpy.py>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/tests/test_correctness.py>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/setup.py>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/eminsk/nanogemm/HEAD/LICENSE>
  - <https://pypi.org/pypi/nanogemm/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/eminsk/nanogemm`) · [data/wave8/enrich/raw/github_com_eminsk_nanogemm.json](../../../data/wave8/enrich/raw/github_com_eminsk_nanogemm.json) (enrichment confidence 0.75)

</details>
