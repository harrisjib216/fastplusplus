# Quantum++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 quantum-computing library on Eigen; its 2018 paper says single-core runs beat Qiskit (QFT) and QuTiP (partial trace).

| | |
|---|---|
| **Beats** | Qiskit (QFT) and QuTiP (partial trace, memory ceiling) |
| **Claimed result** | Snippet only, no numeric times available: single-core Quantum++ 'over-performs' QuTiP on partial trace and Qiskit 'by a large margin' on QFT; QuTiP is faster than Quantum++ on QFT (it uses sparse matrices); QuTiP runs out of memory after 21 qubits whereas Quantum++ simulates up to 28 qubits. |
| **Workload** | Wall-clock time of a quantum Fourier transform on an n-qubit pure state (stress_tests/src/qft.cpp vs python/qft_qiskit.py and python/qft_qutip.py) and of a partial trace of one qubit from a random 2^n x 2^n matrix (src/ptrace.cpp vs python/ptrace_qutip.py; no Qiskit partial-trace script), swept by run.sh over 1-8 threads and 2-24 qubits, single-threaded Quantum++ vs Qiskit and QuTiP, plus the largest qubit count each simulates in 16 GB (harness at github.com/softwareQinc/qpp/tree/v1.1/stress_tests). |
| **Metric** | other |
| **Hardware** | 8-core x86-64 Debian 9.5, Intel Core i7-7700K 4.20 GHz, 16 GB RAM |
| **Compiler and flags** | g++ 6.3 per the paper (WebSearch snippet only); Qiskit and QuTiP on Python 3.5 (snippet only). The public harness stress_tests/CMakeLists.txt at tag v1.1 defaults to CMAKE_BUILD_TYPE Release (CMake's -O3 -DNDEBUG) and adds -std=c++11 -fopenmp -DEIGEN_NO_DEBUG -pedantic -Wall -Wextra -Weffc++; whether the paper's runs used this default is not stated in anything seen here. |
| **Adoption** | 675 stars |
| **Last commit** | 2026-04-17 |
| **Links** | [repository](https://github.com/softwareQinc/qpp) · [benchmark](https://doi.org/10.1371/journal.pone.0208073) |

## Verdict

The only performance evidence is the author's 2018 PLoS ONE paper (i7-7700K, 4 cores/8 threads, 16 GB, Debian 9.5, g++ 6.3, Python 3.5), whose figures could not be opened here; search snippets say single-core Quantum++ beat Qiskit on a QFT and QuTiP on a one-qubit partial trace, QuTiP was faster on QFT, and Quantum++ fit more qubits in 16 GB (28 vs 21, unconfirmed). No timing number was seen, and the public harness times different scopes on each side.

## Use it when

- C++ research code that needs exact dense state-vector or density-matrix simulation up to the mid-20s of qubits (memory-bound) with quantum-information primitives (partial trace, partial transpose, entanglement measures, Kraus channels) in one header-only library.
- Qudit systems (d &gt; 2), which many qubit-only simulators do not support.
- Projects already on Eigen that want quantum operations on Eigen types without a Python runtime.
- Teaching or prototyping circuits from C++ or Python (pyqpp) with OpenQASM 2.0 input.

## Skip it when

- Maximum-throughput state-vector simulation: nothing seen here compares current Quantum++ with Qulacs, QuEST, qsim or Qiskit Aer; a 2024 independent comparison (arXiv 2401.09076, search summary only) lists it at 22 qubits, below Qiskit, Qulacs and QuEST.
- Sparse or structured states and operators: all fundamental types are dense, and the maintainer said in issue #58 (2019) that QuTiP can be faster because it uses sparse matrices (the paper reports QuTiP faster on QFT).
- Memory-limited runs near the RAM ceiling: apply()/applyCTRL() are out of place (each call deep-copies the state and returns a new vector), so peak memory is a multiple of the 2^n state.
- GPU or distributed simulation: CPU only with optional OpenMP; no MPI or CUDA backend.
- Mixed states beyond about 13-14 qubits: a dense 2^n x 2^n complex density matrix needs 4 GB at n=14.

## How it is fast

It is compiled C++ over dense Eigen vectors and matrices, so there is no Python dispatch and no per-gate construction of full-space operators. Since v7.0.0 (March 2026) all-qubit systems take dedicated kernels (internal/kernels/qubit): bit-shift index arithmetic applies a 1-, 2-, 3- or k-qubit gate pairwise over amplitudes, and ptrace sums precomputed stride offsets, with OpenMP parallel loops; the changelog claims 10x to 1000x over the earlier generic multi-index code. The 2018 paper's numbers were measured on that older generic code.

## Compared with alternatives

No quantum-simulation sibling is catalogued in blas-lapack; Quantum++ sits on top of Eigen rather than competing with it, so pick it over hand-written Eigen code when you need gates, partial traces and measurements on qubit or qudit states, and keep Eigen, Armadillo or xtensor for general linear algebra.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen (fetched by CMake if missing); optional OpenMP 3.0+, MATLAB headers, Python 3 plus pybind11 for pyqpp |
| **Minimum toolchain** | C++17 (GCC, Clang, MSVC); CMake 3.20 for install; AppleClang needs Homebrew libomp or clang for OpenMP |
| **Platforms** | any (UNIX, macOS, Linux, Windows); CPU only |
| **Thread safety** | not documented per function; uses thread_local singletons (RNG, gates) unless QPP_NO_THREAD_LOCAL is set, and parallelises internally with OpenMP |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws in the 2018 comparison (stress_tests at tag v1.1): the Qiskit timer spans circuit building plus execute() on the first local Aer backend with shots=1, and the QuTiP QFT timer spans qft_gate_sequence() and propagators(), which expand every gate to a full 2^n x 2^n operator, while the C++ timer covers only gate application; the Qiskit script uses crz rotations where the C++ and QuTiP versions use controlled-phase gates, so it is not the same unitary; and the Python scripts set OPENBLAS_NUM_THREADS/MKL_NUM_THREADS after numpy, qiskit or qutip are already imported and never set OMP_NUM_THREADS, so the 'single-core' Qiskit/QuTiP framing is assumed (the paper says they 'do not seem to be using parallelization'), not enforced.
- The partial-trace race is not like for like either: QuTiP traces a qutip.rand_herm matrix (a sparse Qobj) while Quantum++ traces a dense cmat::Random matrix and discards the result, and no Qiskit partial-trace script exists.
- The measured code is gone: v7.0.0 (2026-03-15) rewrote apply/applyCTRL/ptrace/syspermute with claimed 10x-1000x gains, stress_tests/ was removed, and the current benchmarks/ (Catch2, e.g. qft_bench) time only Quantum++ with no published numbers, so the 2018 ratios describe neither current Quantum++ nor current Qiskit Aer or QuTiP.
- In the v7 qubit kernels the OpenMP loop runs over the outer block loop, which has 2^i iterations for big-endian target qubit i, so a gate on qubit 0 runs on one thread and on qubit 1 on two; ptrace opens one parallel region per output column (read from source, not measured).

## Known shortcomings

- Downgraded C to D: the only numbers source, PLoS ONE paper doi 10.1371/journal.pone.0208073, was unreachable (plos, ncbi, uwspace, inspirehep ENOTFOUND, arXiv blocked) and snippets carry no timings. Public harness at tag v1.1 stress_tests (Release default, g++ 6.3, i7-7700K per snippet), so A or B possible once the paper is readable. Harness asymmetries: Qiskit timer includes circuit build and transpile, QuTiP timer includes building propagators, C++ times only gate application.
- Enricher: paper still unreachable (arXiv, Europe PMC, ar5iv blocked). v1.1 harness: the Qiskit timer covers circuit build plus execute(), the QuTiP timer covers building full 2^n operators, the C++ timer covers gate application only; Qiskit uses crz rather than a controlled-phase, so not the same unitary; OPENBLAS/MKL thread variables are set after numpy, qiskit and qutip import with no OMP_NUM_THREADS, so single-core Python is not enforced; partial trace compares QuTiP sparse rand_herm with C++ dense cmat::Random. v7.0.0 (2026-03) rewrote apply, applyCTRL and ptrace (changelog claims 10x-1000x), so the 2018 code is gone; v7 runs a gate on qubit 0 on one thread. Any paper-access retier should cap near C because the timers differ in scope.

## Caveats and trade-offs

No numbers verified: the evidence is the author's own PLoS ONE paper 'Quantum++: A modern C++ quantum computing library' (doi 10.1371/journal.pone.0208073, PMC6287823, arXiv 1412.4704), which could not be opened here (journals.plos.org, ncbi.nlm.nih.gov, uwspace.uwaterloo.ca, inspirehep.net and arXiv unreachable); search snippets say single-core Quantum++ beats QuTiP on partial trace and Qiskit on QFT, QuTiP is faster on QFT, and Quantum++ fits more qubits in 16 GB, but the timings live in the paper's figures and were not seen. The harness is public (stress_tests/ at tag v1.1; removed from the current tree, whose benchmarks/ directory only benchmarks Quantum++ with Catch2). Harness asymmetries: the Qiskit QFT timer covers circuit construction, execute() (transpile and job overhead) on the first local Aer backend with shots=1, and the QuTiP QFT timer covers building full sparse 2^n propagators per gate, while the C++ timer covers only gate application; the C++ partial trace discards its result. The '8-core' i7-7700K has 4 physical cores and 8 hardware threads. Measurements date from 2018 (old Qiskit and QuTiP, Python 3.5); a 2024 independent comparison (arXiv 2401.09076, search summary only) lists Q++ at 22 qubits, below Qiskit, Qulacs and QuEST. Quantum++ is built on Eigen, the category's own incumbent, so blas-lapack is approximate; Qiskit and QuTiP are not blas-lapack baselines. The list URL github.com/vsoftco/qpp now resolves to softwareQinc/qpp.

Header-only C++17 library built on Eigen with optional OpenMP; the full state vector or density matrix must fit in RAM; Python wrapper pyqpp available.

## Maintenance

Actively maintained (v7.0.3 on 2026-03-25, last commit 2026-04-17, 2 open issues) and MIT-licensed header-only code that is easy to vendor, but its speed claim rests on unseen 2018 figures from code since rewritten.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** benchmark_url was null and the only numbers source, the PLoS ONE paper (doi 10.1371/journal.pone.0208073, PMC6287823, arXiv 1412.4704), could not be opened here (journals.plos.org, www.ncbi.nlm.nih.gov, uwspace.uwaterloo.ca and inspirehep.net all failed DNS; arXiv blocked); WebSearch snippets confirm a Qiskit/QuTiP comparison on an i7-7700K but show no timing numbers, so no number could be checked and the record cannot stay above D. The benchmark code is public (stress_tests/ at tag v1.1), so a paper-access retier could lift it to A or B.
- **Verifier notes:** Downgrade C to D for lack of any number seen: the paper is blocked here and the search snippets carry no timings; the record's '21 vs 28 qubits' memory ceiling also came from a snippet not reproduced here. Paper-access retier candidate: public harness (stress_tests at v1.1, Release build by default) plus g++ 6.3 and i7-7700K from the paper could support A once the figures are read. Metadata checked: MIT, 675 stars, 142 forks, last commit 2026-04-17 (active), v7.0.3 tagged 2026-03-25.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-173 (wave 8); enricher w8 pair-040
- **Pages the verifier opened:**
  - <https://github.com/softwareQinc/qpp>
  - <https://github.com/softwareQinc/qpp/commits/main>
  - <https://github.com/softwareQinc/qpp/tags>
  - <https://github.com/softwareQinc/qpp/tree/main/benchmarks>
  - <https://github.com/softwareQinc/qpp/tree/v1.1>
  - <https://github.com/softwareQinc/qpp/tree/v1.1/stress_tests>
  - <https://github.com/softwareQinc/qpp/tree/v1.1/stress_tests/python>
  - <https://github.com/softwareQinc/qpp/tree/v1.1/stress_tests/src>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/README.md>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/run.sh>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/src/qft.cpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/src/ptrace.cpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/python/qft_qiskit.py>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/python/qft_qutip.py>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/python/ptrace_qutip.py>
- **Sources the enricher read:**
  - <https://github.com/softwareQinc/qpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/README.md>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/INSTALL.md>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/CHANGES.md>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/cmake/qpp_openmp.cmake>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/include/qpp/operations.hpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/include/qpp/internal/kernels/qubit/apply.hpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/include/qpp/internal/kernels/qubit/ptrace.hpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/main/benchmarks/src/qft_bench.cpp>
  - <https://github.com/softwareQinc/qpp/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/README.md>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/run.sh>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/src/qft.cpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/src/ptrace.cpp>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/python/qft_qiskit.py>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/python/qft_qutip.py>
  - <https://raw.githubusercontent.com/softwareQinc/qpp/v1.1/stress_tests/python/ptrace_qutip.py>
  - <https://github.com/softwareQinc/qpp/issues?q=is%3Aissue+performance+OR+slow+OR+benchmark>
  - <https://github.com/softwareQinc/qpp/issues/58>
  - https://arxiv.org/pdf/1412.4704 (EGRESS_BLOCKED; WebSearch snippets only)
  - https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6287823/fullTextXML (EGRESS_BLOCKED)
  - https://ar5iv.labs.arxiv.org/html/1412.4704 (DNS failure)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/softwareqinc/qpp`) · [data/wave8/enrich/raw/github_com_softwareqinc_qpp.json](../../../data/wave8/enrich/raw/github_com_softwareqinc_qpp.json) (enrichment confidence 0.55)

</details>
