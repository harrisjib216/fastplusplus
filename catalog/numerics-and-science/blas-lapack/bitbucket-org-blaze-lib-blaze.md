# Blaze

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Header-only C++14 dense/sparse linear-algebra library with smart expression templates; claims Eigen/MKL-class speed, but no checkable numbers.

| | |
|---|---|
| **Beats** | Eigen, Intel MKL/BLAS and other C++ linear-algebra libraries: the Blazemark suite's Configfile has switches for BLAS (MKL), Boost uBLAS, Blitz++, GMM++, Armadillo, FLENS, MTL and Eigen. The result pages (Bitbucket Benchmarks wiki) were unreachable, so the comparison set actually published is unconfirmed. |
| **Claimed result** | README: 'one of the most intuitive and fastest C++ math libraries available'; 'impressive performance in the Benchmarks section'. No numbers on any page that was opened. |
| **Workload** | Dense and sparse vector/matrix arithmetic with smart expression templates; dense matrix multiplication and other BLAS-level operations through manually tuned kernels or a linked BLAS. |
| **Metric** | throughput |
| **Adoption** | vcpkg port blaze 3.8.2 (port-version 1); Conan Center recipe versions 3.7, 3.8 and 3.8.2; read-only GitHub mirror live-clones/blaze has 12 stars and 4 forks; latest release 3.8.2 (2020-08-15) |
| **Last commit** | 2024-12-30 |
| **Links** | [repository](https://bitbucket.org/blaze-lib/blaze) |

## Verdict

No Blaze-vs-baseline number could be checked: the Bitbucket Benchmarks wiki returned 404, and the repo has only the Blazemark harness (switches for MKL/BLAS, Eigen, Armadillo, uBLAS, Blitz++, GMM++, FLENS, MTL), no results. The one third-party measurement opened (Fastor wiki; Blaze 3.7, GCC 7.4 -O3 with AVX-512 flags, Xeon Gold 6128, double, M=1-32, N=7/13/21/31, K=31) puts Blaze with padding at parity to over 2x slower than Fastor, about 50% slower on average, and generally behind MKL JIT.

## Use it when

- Code that mixes dense and sparse vectors and matrices in one expression syntax (for example sparse matrix times dense vector inside an iterative solver)
- Small and medium fixed-size or bounded-size algebra (StaticMatrix/HybridMatrix) where padding to the SIMD width is acceptable
- HPC codes already on HPX: Blaze has an HPX parallel backend, and STEllAR's blaze_tensor and blaze_cuda extend it
- Large dense products where you will link MKL or OpenBLAS anyway: BLAZE_BLAS_MODE routes gemm to the BLAS and keeps the expression syntax

## Skip it when

- If you need evidence that it beats Eigen or MKL: the Benchmarks wiki is unreachable, results quoted on HN date from 2016-17, and the one third-party benchmark found (Fastor wiki) has Blaze about 50% slower than Fastor and MKL JIT for small fixed-size products
- Projects that need an active upstream: the last release is 3.8.2 (August 2020), and the stated compiler testing stops at GCC 10.2, Clang 10 and VS2017
- Running several Blaze operations at once from different threads (OpenMP sections, task pools): the docs say Blaze 'does not support concurrent parallel computations', so you have to serialize them
- Memory-tight code with many tiny matrices: padding makes aligned StaticVector/StaticMatrix larger than their elements, and zeroing the padding costs time
- Builds without LAPACK: the CMake package does find_package(LAPACK REQUIRED) by default, and decompositions, inverse, eigen and svd fail to link without it

## How it is fast

'Smart expression templates': operators build expression objects that are dispatched at assignment to hand-written SIMD kernels (SSE through AVX-512/FMA, optional SLEEF or XSIMD), so it does not just fuse element-wise loops. Dense vectors and matrices are padded and aligned by default, so the kernels need no scalar remainder loops. Large dense products go through a blocked, packed mmm() kernel (blaze/math/dense/MMM.h copies K x N panels of A and B into temporaries) or, if BLAZE_BLAS_MODE is set, to cblas gemm. Shared-memory parallelism (OpenMP by default, or C++11/Boost threads or HPX) starts only above per-operation size thresholds in blaze/config/Thresholds.h.

## Compared with alternatives

Choose Blaze over Eigen if you want one expression syntax over dense and sparse types and an HPX backend, and you can accept a stale upstream and no current evidence on speed; Eigen is the safer default and is the one with published, monitored numbers. For many tiny matrices, BLASFEO has measured wins over OpenBLAS and BLIS, which Blaze does not.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for basic arithmetic; LAPACK for decompositions/inversion/eigen/svd (required by the default CMake config); optional BLAS (cblas.h), OpenMP, Boost.Thread, HPX, SLEEF, XSIMD |
| **Minimum toolchain** | C++14 (cxx_std_14); README says it is tested with GCC 6.0-10.2, Clang 5.0-10.0 and Visual C++ 2017 (Win64 only) |
| **Platforms** | Any C++14 target; SIMD kernels for x86 SSE through AVX-512/FMA and SVML; other ISAs only through the optional XSIMD/SLEEF paths or scalar code |
| **Thread safety** | Separate objects can be used from separate threads, but Blaze's own parallelization assumes one operation at a time: concurrent Blaze operations (e.g. in OpenMP sections) must be wrapped in serial() or run with parallelization disabled; BLAZE_SERIAL_SECTION is undefined behavior if used from several threads |
| **Drop-in for the baseline** | partial: it is not an Eigen API or BLAS ABI replacement, but BLAZE_BLAS_MODE lets it call your existing BLAS for gemm inside Blaze expressions |

## Gotchas

- Aliasing like x = A \* x is detected and fixed with a temporary; noalias() turns this check off, and the docs warn that misuse is undefined behavior
- Padding is on by default (BLAZE_USE_PADDING=1, blaze::padded); turning it off sends remainders to scalar code, which is what the Fastor benchmark saw
- Thread counts come from BLAZE_NUM_THREADS or OMP_NUM_THREADS, or setNumThreads(); OpenMP is the default backend in CMake and drops silently to one thread (with a CMake warning) if OpenMP is not found
- With BLAZE_BLAS_MODE, BLAZE_BLAS_IS_PARALLEL has to match the BLAS you link; otherwise Blaze threads and BLAS threads can oversubscribe the cores

## Known shortcomings

- Tier D: the Bitbucket wiki Benchmarks page is 404 and blazemark/ code has no published results here; the Fastor wiki shows Blaze \~50% slower than Fastor (up to 2x); stale (last commit 2024-12-30).
- Docs say Blaze cannot run concurrent parallel operations (must use serial()); default CMake requires LAPACK; last release 3.8.2 (2020).

## Caveats and trade-offs

Tier D: the Bitbucket wiki Benchmarks page returned 404 to this verifier as well, so no number could be checked. The benchmark code itself (blazemark/) is in the repo. The one third-party benchmark opened (Fastor wiki: Blaze 3.7 vs Eigen 3.3.7, MKL JIT, LIBXSMM and Fastor on small fixed-size matrix products) says Blaze with padding is 'in general being about 50% slower' than Fastor and 'over 2X slower in some cases', and that Blaze without padding falls back to scalar remainder code. The canonical Bitbucket repo's last commit is 2024-12-30 (Bitbucket API), the same as the mirror, and there has been no release since 3.8.2 in 2020. The peer-reviewed SIAM SISC 2012 paper by Iglberger et al. ('Expression Templates Revisited') benchmarks Blaze, but its PDF host was egress-blocked; a search summary suggests it shows MKL-level parity for dgemm rather than a win.

Header-only; uses a BLAS (or its own kernels) for large dense products; SSE/AVX/AVX-512/FMA vectorisation; threading through OpenMP, HPX or C++11/Boost threads; padding is used for aligned SIMD access.

## Maintenance

Stale: last commit 2024-12-30 and no release since 3.8.2 (2020-08-15). It is BSD-3-Clause and header-only, ships as vcpkg and Conan packages, and is fine to vendor, but plan to maintain it yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null, and the Bitbucket Benchmarks wiki (and every wiki page tried) returns 404 here. The repo has the Blazemark suite (blazemark/, whose Configfile can enable Eigen, MKL/BLAS, Armadillo, Boost uBLAS, Blitz++, GMM++, FLENS and MTL) but no result numbers, so no Blaze-vs-baseline number was seen. The only third-party numbers opened (Fastor's wiki) show Blaze slower than Fastor and state no Blaze-vs-Eigen result.
- **Verifier notes:** Confirmed at D rather than rejected: Blaze is widely referenced (vcpkg and Conan ports, mirrors, a CRAN wrapper in search results) even though the mirror has few stars. A retier check could open the Blaze Benchmarks wiki or the SISC 2012 paper if Bitbucket wiki or blogs.fau.de becomes reachable. A WebSearch snippet (HN thread, not opened) says the Blaze benchmarks date from 2016-17 and that Eigen ran without its MKL backend; this is unverified. License BSD-3-Clause was confirmed from the mirror's LICENSE ('New (Revised) BSD') and the vcpkg manifest.
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://bitbucket.org/blaze-lib/blaze>
  - <https://bitbucket.org/blaze-lib/blaze/wiki/Benchmarks>
  - <https://bitbucket.org/blaze-lib/blaze/wiki/Home>
  - <https://bitbucket.org/blaze-lib/blaze/wiki/Benchmarks.md>
  - <https://api.bitbucket.org/2.0/repositories/blaze-lib/blaze/commits?pagelen=1>
  - <https://github.com/live-clones/blaze>
  - <https://github.com/live-clones/blaze/commits>
  - <https://github.com/live-clones/blaze/tree/master/blazemark>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/README.md>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blazemark/Configfile>
  - <https://github.com/romeric/Fastor/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/blaze/vcpkg.json>
  - <https://raw.githubusercontent.com/conan-io/conan-center-index/master/recipes/blaze/config.yml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/README.md>
  - <https://github.com/live-clones/blaze>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/config/BLAS.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/config/Optimizations.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/config/Vectorization.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/config/Thresholds.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/config/SMP.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/config/Padding.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/config/Alignment.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/math/expressions/DMatDMatMultExpr.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/math/dense/MMM.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/system/Thresholds.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/Tutorial.h>
  - <https://raw.githubusercontent.com/live-clones/blaze/HEAD/blaze/Blaze.h>
  - https://bitbucket.org/blaze-lib/blaze/issues?status=new&status=open (404)
  - <https://github.com/romeric/Fastor/wiki/Benchmarks>
  - https://news.ycombinator.com/item?id=34407106 (egress-blocked; WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://bitbucket.org/blaze-lib/blaze`) · [data/wave8/enrich/raw/bitbucket_org_blaze_lib_blaze.json](../../../data/wave8/enrich/raw/bitbucket_org_blaze_lib_blaze.json) (enrichment confidence 0.6)

</details>
