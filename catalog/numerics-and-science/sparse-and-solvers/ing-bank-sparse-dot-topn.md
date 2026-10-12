# sparse_dot_topn

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Python package with a C++17 OpenMP kernel for sparse A\*B that keeps only the top-n values per row; multithreaded, so it beats single-threaded SciPy.

| | |
|---|---|
| **Beats** | SciPy sparse CSR matrix multiplication (scipy.sparse A.dot(B), SciPy 1.12.0) |
| **Claimed result** | Apple M2 Pro, 8 threads: plain sp_matmul 5.1x faster than SciPy (0.032 s vs 0.165 s min time); sp_matmul_topn with top_n=10 and 8 threads 6.9x faster (0.024 s). Intel i9 2.3 GHz 8-core, 8 threads: sp_matmul 3.4x. Single-thread plain product about 1.0x on M2 Pro. |
| **Workload** | Sparse matrix product A.dot(B) of two TF-IDF CSR matrices of shape (20,000 x 193,190) by (193,190 x 20,000) built from SEC EDGAR company names, with and without keeping only the top-n values per row; 30 repeats. |
| **Metric** | latency |
| **Hardware** | Apple MacBook Pro M2 Pro (32GB RAM); MacBook Pro 2.3 GHz 8-core Intel Core i9 (16GB RAM) |
| **Adoption** | 425 stars; PyPI package sparse-dot-topn |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/ing-bank/sparse_dot_topn) · [benchmark](https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/master/bench/README.md) |

## Verdict

The project's richbench run (30 repeats, SciPy 1.12.0 vs sparse-dot-topn v1.0.0, two 20,000 x 193,190 TF-IDF matrices of SEC EDGAR company names) shows the plain product 5.1x faster on 8 threads of an Apple M2 Pro (0.032 s vs 0.165 s) and 3.4x on an 8-core 2.3 GHz Intel i9. top_n=10 reaches 6.9x (M2 Pro) and 12.7x (i9) at 8 threads. Single-thread plain product is about 1.0x, and top_n&gt;=100 on one thread is slower than SciPy. The compiler and flags of the benchmarked build are not stated.

## Use it when

- Top-k similarity joins (cosine similarity of L2-normalised TF-IDF or other non-negative sparse vectors) where you need only the best 10-30 matches per row: 5.5-6.9x over SciPy on 8 M2 Pro threads in the project's benchmark.
- Large A x B^T products whose full result would not fit in memory, but whose top-n result does.
- Multi-core machines running Python where SciPy's single-threaded sparse matmul is the bottleneck: the plain sp_matmul scales to 5.1x at 8 threads.
- Matching jobs too large for one machine (O(10M+) rows): split A and B into row blocks, run each pair anywhere (the README mentions Spark), merge with zip_sp_matmul_topn and vstack.

## Skip it when

- Large top_n on few threads: top_n=1000 is 6.2x slower than SciPy on one M2 Pro thread and still 1.2x slower at 8 threads; top_n=100 on one thread is 1.9x slower.
- Single-threaded use of the plain product: about 1.0x on the M2 Pro and the i9, so there is nothing to gain.
- Signed data with the default threshold=None (see gotchas): from reading the source, float results at or below the smallest positive float are dropped.
- General C++ SpGEMM: the headers include nanobind through common.hpp and the API exists for Python; use a C++ sparse library instead.
- Very large top-n jobs on the multithreaded path: memory for the nrows x top_n buffers is allocated up front, whatever the real output size.

## How it is fast

The kernel is SciPy's own row-wise Gustavson SpGEMM (a modified csr_binop/csr_matmat: a dense accumulator plus a linked list of touched columns) parallelised over rows of A with OpenMP. Each thread has its own accumulator. With top-n, each row's candidates go through a fixed-size heap (std::push_heap/pop_heap, O(top_n) memory per row instead of O(n_columns)), so the full product row is never stored. In the multithreaded path each row writes into a preallocated nrows x top_n buffer, which is compacted at the end. On one thread the plain product is the same algorithm as SciPy, which is why single-thread speed is about 1.0x.

## Compared with alternatives

Of the catalogued siblings, only VBCSR also targets SciPy sparse. Pick sparse_dot_topn for unstructured TF-IDF-style similarity search with a small top-n, and VBCSR for block-structured operators. For general multithreaded SpGEMM inside C++ code, TACO-generated kernels or ALP/GraphBLAS fit better, because this package's kernels are tied to its Python bindings.

## Integration

| | |
|---|---|
| **Form** | module (Python package with a nanobind C++ extension; the core kernels are header-only templates under src/sparse_dot_topn_core/include) |
| **Dependencies** | numpy&gt;=1.18, scipy&gt;=1.4.1, psutil; nanobind and scikit-build-core to build; OpenMP optional (bundled in the PyPI wheels per the README; non-bundled wheels on the releases page) |
| **Minimum toolchain** | C++17 compiler for source builds; CMake 3.15+; CPython 3.9-3.14 wheels (stable-ABI cp312 wheels for 3.12+) |
| **Platforms** | Wheels for Windows x86-64, Linux 64-bit, macOS x86-64 and arm64. Wheels are generic builds with arch flags off; source builds add -march=native on Apple arm64 and SSE/AVX flags on x86. |
| **Thread safety** | not documented (from the source: each call allocates its own buffers and the kernels keep no global state) |
| **Drop-in for the baseline** | partial — sp_matmul(A, B) returns the same CSR product as A.dot(B), and sp_matmul_topn(A, B, top_n=B.shape[1]) dispatches to it, but the top-n API, parameters and defaults (unsorted output, threshold disabled) differ and B is auto-transposed when only its transpose fits |

## Gotchas

- Possible correctness bug, from reading the source and not reproduced: when threshold is None the bindings use std::numeric_limits&lt;eT&gt;::min() as the floor. For float/double that is the smallest positive normal (about 1.2e-38), not the lowest value, so negative and zero results never enter the top-n heap. This contradicts the README's claim that disabling threshold makes negative values work. Integer dtypes are unaffected.
- Possible correctness bug, from reading the source and not reproduced: plain sp_matmul sizes C_indptr with a symbolic pass that counts every touched column, but the numeric pass skips sums that are exactly 0. If values cancel, or the input stores explicit zeros, the single-thread path shifts later rows' entries against indptr and the multithreaded path leaves unwritten slots, so the output holds uninitialised memory. The tests use only non-negative sparse.random data.
- The multithreaded top-n path computes nrows\*top_n and per-row offsets in the index type (int32 when indices fit) and sums row counts with an int accumulator. Very large nrows x top_n (above 2^31) can overflow.
- n_threads=None means one thread, and -1 means physical cores minus one. Without OpenMP the call warns and runs single-threaded. COO and CSC inputs are converted to CSR first, which costs time.

## Known shortcomings

- Speedup comes mostly from threads (1.0x single-thread); baseline SciPy; Python package.
- Correctness bug from source reading (not reproduced): threshold=None sets the floor to std::numeric_limits&lt;eT&gt;::min() (\~1.2e-38 for float), so negative and zero top-n results are silently dropped, against the README claim that negatives work. Suspected second bug: plain sp_matmul sizes indptr symbolically but skips sums that are exactly 0, so cancelling values or stored zeros give misaligned rows or uninitialised memory. Tests use non-negative data only. MT top-n index maths can overflow int32 when nrows\*top_n &gt; 2^31.

## Caveats and trade-offs

First-party benchmark (tier C): bench code is public and hardware is named but compiler and flags are not. SciPy's sparse matmul is single-threaded, so almost all of the speedup comes from multithreading; single-thread plain product is about 1.0x. The top-n variant is slower than SciPy for large n (for example 6.2x slower at top_n=1000 on one thread on the M2 Pro). SciPy CSR matmul is not SuiteSparse, Eigen or PETSc, so baseline_in_list is false and the category fit is partial.

Python package with a C++17 extension (OpenMP vendored); uses a max-heap to keep memory low when only the top-n entries per row are needed. Result type and API differ from plain SciPy products. Not a general SpGEMM replacement.

## Maintenance

Active (v1.2.0 adds CPython 3.14 wheels; last commit 2026-09-14), Apache-2.0, 425 stars and 3 open issues. Easy to pip install, but the kernels are coupled to nanobind, so vendoring them into a C++ project takes some unpicking.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** bench/README.md tables (SciPy 1.12.0 vs sparse-dot-topn v1.0.0, richbench, 30 repeats) contain every quoted number on a named M2 Pro and Intel i9; bench code is public but the pip wheel's compiler and flags are not stated, so first-party C.
- **Verifier notes:** Numbers verified: M2 Pro sp_matmul 8 threads 0.032 s vs 0.165 s (5.1x), top_n=10 8 threads 0.024 s (6.9x), single-thread 1.0x; Intel i9 sp_matmul 8 threads 3.4x (the i9 also shows top_n=10 at 8 threads 12.7x by min time, and 1.7x single-thread). Metadata confirmed: Apache-2.0, 425 stars, 231 commits, last commit 2026-09-14 (CI bump).
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/master/bench/README.md>
  - <https://github.com/ing-bank/sparse_dot_topn>
  - <https://github.com/ing-bank/sparse_dot_topn/commits>
- **Sources the enricher read:**
  - <https://github.com/ing-bank/sparse_dot_topn>
  - <https://github.com/ing-bank/sparse_dot_topn/issues?q=is%3Aissue>
  - <https://github.com/ing-bank/sparse_dot_topn/issues?q=negative>
  - <https://github.com/ing-bank/sparse_dot_topn/tree/master/src/sparse_dot_topn_core/include/sparse_dot_topn>
  - <https://github.com/ing-bank/sparse_dot_topn/tree/master/tests>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/README.md>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/INSTALLATION.md>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn_core/cmake/ConfigureTarget.cmake>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn_core/include/sparse_dot_topn/maxheap.hpp>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn_core/include/sparse_dot_topn/sp_matmul_topn.hpp>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn_core/include/sparse_dot_topn/sp_matmul.hpp>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn_core/include/sparse_dot_topn/sp_matmul_bindings.hpp>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn_core/include/sparse_dot_topn/sp_matmul_topn_bindings.hpp>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn_core/include/sparse_dot_topn/common.hpp>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/src/sparse_dot_topn/api.py>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/tests/test_api.py>
  - <https://raw.githubusercontent.com/ing-bank/sparse_dot_topn/HEAD/tests/conftest.py>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ing-bank/sparse_dot_topn`) · [data/wave8/enrich/raw/github_com_ing_bank_sparse_dot_topn.json](../../../data/wave8/enrich/raw/github_com_ing_bank_sparse_dot_topn.json) (enrichment confidence 0.8)

</details>
