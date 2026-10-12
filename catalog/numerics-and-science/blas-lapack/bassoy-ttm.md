# TTM / TLIB(TTM) (in-place tensor-times-matrix via loops-over-GEMM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `LGPL-3.0` · 🟡 stale

> Header-only C++17 mode-q tensor-times-matrix product on top of BLAS; paper claims it beats Eigen, LibTorch and MKL batched GEMM.

| | |
|---|---|
| **Beats** | Eigen (Tensor module) and LibTorch tensor-matrix products, plus Intel MKL batched GEMM; the paper reports parity with TBLIS |
| **Claimed result** | SNIPPET ONLY (search-engine summary of the paper abstract; the paper was not opened): best-performing algorithm reaches a median 2.47 TFLOPS on an Intel Xeon Gold 5318Y and 2.93 TFLOPS on an AMD EPYC 9354 for large tensor slices; 'outperforms batched GEMM implementation of Intel MKL by a factor of 2.57 with large tensor slices'; 'on average at least 6.21% and up to 334.31% faster' than frameworks implementing state-of-the-art approaches including Libtorch and Eigen; 'on par with TBLIS' for the majority of tensor shapes. The repo README gives no numbers ('For large tensors reaches peak matrix-times-matrix performance'). |
| **Workload** | Mode-q tensor-times-matrix product on dense tensors of many shapes and orders, large tensor slices highlighted, as reported in the author's Journal of Computational Science 2025 paper (details not seen). |
| **Metric** | throughput |
| **Hardware** | Per the search snippet only: Intel Xeon Gold 5318Y and AMD EPYC 9354. |
| **Compiler and flags** | Paper build not seen. Repo example/Makefile: g++ -Wall -O3 -std=c++17 -fopenmp with the BLAS chosen through BLAS_FLAG (OPENBLAS, MKL or BLIS makefile fragments). |
| **Adoption** | 5 stars, 1 fork; Python bindings (ttmpy) in repo; the README asks users to cite the Journal of Computational Science 2025 article (vol. 87, art. 102568) |
| **Last commit** | 2025-03-24 |
| **Links** | [repository](https://github.com/bassoy/ttm) · [benchmark](https://www.sciencedirect.com/science/article/pii/S1877750325000456) |

## Verdict

Nothing in the repository measures TTM against another library: example/measure.cpp times only TTM's own variants, and the README says only that large tensors reach peak GEMM performance. Per search-engine summaries of the two peer-reviewed papers (neither could be opened here), the Journal of Computational Science 2025 article reports a median 2.47 TFLOPS on a Xeon Gold 5318Y and 2.93 TFLOPS on an EPYC 9354, 2.57x over MKL batched GEMM for large slices and 6.21% (average) to 334.31% (best case) over LibTorch and Eigen; the ICCS 2024 conference version reports a median 1.37 double-precision TFLOPS on a Xeon Gold 6248R with MKL and at least 14.05% on average, up to 3.79x, over LibTorch and Eigen; compiler, flags and library versions are unknown.

## Use it when

- Repeated mode-q products of a dense 3rd-order-or-higher tensor with a matrix (Tucker/HOSVD, HOOI, tensor-train sweeps), float or double, on a multicore x86-64 Linux box with MKL, OpenBLAS or BLIS/AOCL already linked.
- Tensors stored in an arbitrary or row-major/column-major permuted layout where you do not want to pay for a transpose or a second buffer the size of the tensor.
- Large tensor slices, where the author reports reaching near-peak GEMM throughput and the largest margin over MKL's batched GEMM.
- Prototyping from Python with NumPy arrays when you can build the ttmpy extension yourself and want to replace np.einsum/tensordot for this one contraction.

## Skip it when

- General tensor contractions (more than one contracted index, tensor-tensor products): TTM does only tensor-times-matrix; use TBLIS or TCCG/GETT.
- Integer, half, bfloat16 or complex element types, strided or non-contiguous views: only contiguous float and double are supported.
- Windows, macOS or builds without a separate BLAS: CI is Ubuntu only, the build files are GNU make fragments with Ubuntu and TUHH cluster paths, and core detection shells out to lscpu through popen.
- Code that needs strict control of global threading state: every call resets the BLAS library's thread count (openblas_set_num_threads, mkl_set_num_threads or bli_thread_set_num_threads) and may turn on nested OpenMP.
- Production projects that need a support track record: 5 stars, one author, no releases, last commit March 2025, and the speed claims are not reproducible from the repo.

## How it is fast

Loops-over-GEMM (LoG): instead of transposing the tensor into a matrix (TTGT), it walks the free modes and hands each 2-D slice or larger q-order subtensor directly to BLAS gemm/gemv, so there is no copy and no extra memory. Eight policy combinations (sequential, multithreaded BLAS, OpenMP parallel-for or taskloop over slices with single-threaded BLAS, nested loop plus threaded BLAS, MKL gemm_batch; slice vs subtensor slicing; none/outer/all loop fusion) cover different shapes. The default 'combined' path is a runtime heuristic: if the outer loop count is at least the core count it runs an OpenMP loop over subtensors, else an OpenMP loop over 2-D slices if that gives enough work, else one multithreaded BLAS call per subtensor.

## Compared with alternatives

Pick TTM over TBLIS or TCCG/GETT when your only contraction is a single-mode tensor-times-matrix and the tensor layout varies at runtime: it needs no packing buffers and reuses your tuned BLAS, while TBLIS (per the paper's abstract, on par for most shapes) and TCCG cover general contractions. Pick Eigen's Tensor module only if you need its expression templates and no BLAS dependency.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | A CBLAS: Intel MKL (selected with -DUSE_MKL, configured as ILP64), OpenBLAS (-DUSE_OPENBLAS) or BLIS/AOCL (-DUSE_BLIS); OpenMP 4.5+; pybind11 and NumPy for the optional Python wrapper; GoogleTest for the unit tests. The shipped openblas.mk expects OpenBLAS under \$HOME/local and blis.mk a static libblis-mt.a under /usr/local, so paths usually need editing. |
| **Minimum toolchain** | C++17 for the library and examples (g++ -O3 -std=c++17 -fopenmp); the unit tests build with -std=c++2a; CI uses g++ on ubuntu-latest |
| **Platforms** | x86-64 Linux is the only tested target (GitHub Actions on Ubuntu with MKL and OpenBLAS); other platforms not documented. |
| **Thread safety** | Not documented. Each call sets process-wide BLAS thread counts and OpenMP nesting, so concurrent calls from several user threads are unsafe in practice (inferred from detail/ttm.h). |
| **Drop-in for the baseline** | partial — it replaces the tensor-times-matrix step that Eigen Tensor contract(), LibTorch tensordot or a hand-written MKL gemm_batch loop would do, but through its own API and tensor/pointer conventions; it is not a BLAS or LAPACK replacement. |

## Gotchas

- Unsupported parallel/slicing/fusion tag combinations hit a generic template that prints 'This type of ttm is not yet defined' to std::cout and returns without writing C; the batched_gemm policy compiles to a no-op for the general case unless built with USE_MKL.
- The wiki's policy names (threaded_gemm_t, omp_forloop_t, omp_forloop_and_threaded_gemm_t) and its claim that the high-level interface uses function 3 do not match the current tags.h (parallel_blas_t, parallel_loop_t, parallel_loop_blas_t, combined_t) or the operator\*, which uses the combined heuristic.
- Each translation unit that includes the header runs popen("lscpu ...") twice during static initialization to count physical cores, falling back to std::thread::hardware_concurrency.
- The shipped mkl.mk and ttmpy/setup.py link MKL statically with the ILP64 interface (-DMKL_ILP64); mixing with LP64 MKL elsewhere in the process breaks. 'pip install ttmpy' from PyPI installs an unrelated package (TTMPy 0.1 'toolbelt'); the wrapper must be built from the repo's ttmpy folder.

## Known shortcomings

- Downgraded B to D: no reachable page shows numbers. The claimed comparison lives in the peer-reviewed Journal of Computational Science 2025 article (vol. 87, 102568), blocked here, and example/measure.cpp times only TTM's own variants with no Eigen, LibTorch, MKL or TBLIS run. Paper-access retier candidate (likely B). Last commit 2025-03-24, stale.
- Each call resets process-wide BLAS threads and OpenMP nesting; unsupported policy tags print to cout and leave C unwritten; batched_gemm is a no-op without MKL; popen(lscpu) runs at static initialization; the MKL setup is ILP64; wiki policy names are stale and the CPP-Interfaces wiki page 404s. PyPI 'ttmpy' is an unrelated package. The ICCS 2024 paper (LNCS 14832; snippet: median 1.37 double-precision TFLOPS on a Xeon Gold 6248R with MKL, average at least 14.05% and up to 3.79x over LibTorch/Eigen) was blocked; retier candidate to B.

## Caveats and trade-offs

No numbers or baseline comparison in the repository: the README gives only a qualitative claim, the wiki home page has no benchmarks (the other three wiki pages failed to load), and example/measure.cpp (g++ -O3, cache flush between runs) times only TTM's own parallel/slicing/fusion variants. The comparison against Eigen, LibTorch, MKL batched GEMM and TBLIS exists only in the peer-reviewed article 'Design of a high-performance tensor-matrix multiplication with BLAS' (Bassoy, Journal of Computational Science 87, 2025, 102568; doi 10.1016/j.jocs.2025.102568), which neither the search agent nor the verifier could open (ScienceDirect, doi.org, arXiv and tore.tuhh.de are egress-blocked). Every number in claimed_speedup is from one search-engine summary of the abstract and is UNVERIFIED; per that summary the average gain over frameworks is as low as 6.21% and TBLIS is a tie for most shapes. It is the author's own benchmark of his own library; compiler, flags, library versions and whether the benchmark code is public are unknown. The author's GitHub account has no separate artifact repo (only ttm, ttv, tlib, simd, matrix and forks). The README badge says GPL while LICENSE.txt and GitHub show LGPL-3.0. A check that can open the paper should restore B (or A if it names a public artifact with compiler, flags and CPU), as for the sibling bassoy/ttv entry (B, ICCS 2019).

Header-only C++17 but requires an external BLAS (BLIS, MKL or OpenBLAS makefile fragments provided), so performance follows the chosen BLAS. float and double only, contiguously stored tensors, OpenMP 4.5 or newer for threading. In-place: no tensor transposition and no extra memory. Runtime choice of contraction mode, tensor order, extents and any linear layout. Task-loop parallelism added in late 2024.

## Maintenance

Stale (last commit 2025-03-24, no releases, no issues ever filed) and a single-author research code, but LGPL-3.0 and header-only, so vendoring the include/tlib folder is easy; the README badge says GPL while LICENSE.txt is LGPL-3.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now D.
- **Tier reason:** Nothing I could open has numbers: the README says only 'For large tensors reaches peak matrix-times-matrix performance', the wiki home page has no benchmarks, and example/measure.cpp times only TTM's own variants with no Eigen, LibTorch, MKL batched-GEMM or TBLIS run. The peer-reviewed Journal of Computational Science 2025 article (vol. 87, 102568, cited in the README) holds the claimed comparison, but ScienceDirect is egress-blocked here and the record's figures come only from the search agent's search-engine summary, which I could not re-check (WebSearch off-limits for this run).
- **Verifier notes:** Downgraded B to D because no reachable page shows numbers; do not reject: the peer-reviewed JoCS 2025 article exists (README bibtex) and the sibling bassoy/ttv is already verified at B. Add to the paper-access retier follow-ups (likely B). Metadata verified: LGPL-3.0, 5 stars, 1 fork, not a fork, last commit 2025-03-24 ('Update README.md'), stale.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/bassoy/ttm>
  - <https://github.com/bassoy/ttm/commits>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/README.md>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/example/measure.cpp>
  - <https://github.com/bassoy/ttm/wiki>
  - <https://github.com/bassoy?tab=repositories>
- **Sources the enricher read:**
  - <https://github.com/bassoy/ttm>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/README.md>
  - <https://github.com/bassoy/ttm/wiki>
  - <https://github.com/bassoy/ttm/wiki/CPP-Interfaces>
  - <https://raw.githubusercontent.com/wiki/bassoy/ttm/Home.md>
  - <https://raw.githubusercontent.com/wiki/bassoy/ttm/CPP-Functions.md>
  - <https://raw.githubusercontent.com/wiki/bassoy/ttm/Installation-&-Usage.md>
  - <https://github.com/bassoy/ttm/tree/master/include/tlib>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/include/tlib/ttm.h>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/include/tlib/detail/ttm.h>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/include/tlib/detail/tags.h>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/include/tlib/detail/tensor.h>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/example/Makefile>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/mkl.mk>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/openblas.mk>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/blis.mk>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/test/Makefile>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/.github/workflows/test.yml>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/ttmpy/setup.py>
  - <https://raw.githubusercontent.com/bassoy/ttm/HEAD/ttmpy/README.md>
  - <https://github.com/bassoy/ttm/issues?q=is%3Aissue>
  - <https://pypi.org/pypi/ttmpy/json>
  - WebSearch snippets for https://www.sciencedirect.com/science/article/pii/S1877750325000456 (JoCS 2025) and https://www.iccs-meeting.org/archive/iccs2024/papers/148320264.pdf (ICCS 2024, LNCS 14832; direct fetch EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bassoy/ttm`) · [data/wave8/enrich/raw/github_com_bassoy_ttm.json](../../../data/wave8/enrich/raw/github_com_bassoy_ttm.json) (enrichment confidence 0.7)

</details>
