# ITensors.jl (Julia) vs C++ ITensor v3.1.6 in ITensorBenchmarks.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `Apache-2.0` · 🟢 active

> Julia tensor-network library (DMRG, TRG, CTMRG) that matches or beats C++ ITensor v3 at large bond dimension on MKL.

| | |
|---|---|
| **Beats** | C++ ITensor v3.1.6 (github.com/ITensor/ITensor), same tensor-network algorithms, Intel MKL BLAS/LAPACK on both sides |
| **Claimed result** | Julia faster at large bond dimension: DMRG 2D conserve_ky maxdim 10000 6245.4 s vs C++ 8944.8 s (1.43x, derived from page data); maxdim 1000 622.8 s vs 1035.0 s (1.66x); DMRG 1D QN maxdim 1000 173.2 s vs 225.0 s (1.30x); DMRG 1D dense maxdim 1000 3323.7 s vs 3857.2 s (1.16x); DMRG 2D QN maxdim 5000 6430.1 s vs 6721.0 s (1.05x). Julia slower at small sizes: DMRG 2D QN maxdim 1000 405.8 s vs 334.8 s; DMRG 1D QN maxdim 200 18.0 s vs 16.9 s; TRG maxdim 10 1.11 s vs 0.16 s; CTMRG maxdim 50 2.33 s vs 0.92 s. Near parity: TRG maxdim 50 256.6 s vs 264.2 s; CTMRG maxdim 400 104.7 s vs 115.8 s. |
| **Workload** | Wall-clock time of DMRG (1D Heisenberg dense and with QN block sparsity, 2D QN and 2D conserve_ky), TRG and CTMRG runs at increasing maximum bond dimension, 1 BLAS thread and 1 block-sparse thread, ITensors.jl v0.1.37 against C++ ITensor v3.1.6; per-run seconds are one number per maxdim_N.txt file under data/julia/v0.1.37 and data/c++/v3.1.6. |
| **Metric** | latency |
| **Compiler and flags** | C++: g++ -O2 with MKL 2020.4.304 (link line mixes -lmkl_rt with layered MKL libraries); Julia 1.5.2/1.5.3 with MKL as BLAS vendor, ITensors.jl v0.1.36 per the logs and Manifest (the data folder says v0.1.37). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 686 stars (ITensors.jl); ITensorBenchmarks.jl 5 stars |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/ITensor/ITensors.jl) · [benchmark](https://github.com/ITensor/ITensorBenchmarks.jl/tree/main/data) |

## Verdict

ITensorBenchmarks.jl ran identical DMRG (1D Heisenberg dense and QN, 2D Hubbard QN and momentum-conserving), TRG and CTMRG problems single-threaded in January-February 2021 on a Flatiron cluster node whose CPU is not stated, timing ITensors.jl v0.1.36 on Julia 1.5 with MKL against C++ ITensor v3.1.6 built with g++ -O2 and MKL 2020.4. Julia was 1.05-1.7x faster at large bond dimension (2D momentum-conserving Hubbard at maxdim 10000: 6245 s vs 8945 s, one run each, final energies matching), C++ was ahead at small 2D QN sizes, and the small TRG/CTMRG losses are inflated by uncompiled QuadGK reference code in Julia's first timed run.

## Use it when

- DMRG on quantum-number-conserving 1D and 2D lattice models at bond dimensions of roughly 1000 and up, where the 2021 runs show Julia 1.05-1.7x faster than C++ ITensor v3 single-threaded.
- New tensor-network projects where Julia is acceptable: active development (ITensors.jl v0.9.32, last commit 2026-09-27), MKL or OpenBLAS backends, plus extensions for HDF5, TensorOperations and Zygote-based autodiff.
- Prototyping TRG, CTMRG or custom contractions interactively, where named-index contraction cuts bookkeeping code and the JIT cost is paid once per session.
- Workloads that benefit from block-sparse multithreading (Julia started with -t N) instead of BLAS threads; the benchmark runner refuses to combine the two.

## Skip it when

- Short runs or one-shot scripts: compilation and package load cost seconds, which dominates jobs that run for well under a minute.
- Embedding in an existing C++ code base; C++ ITensor stays the natural choice there, and calling Julia from C++ adds a runtime.
- Expecting the 2021 numbers to hold today: they were measured with ITensors.jl v0.1.36 on Julia 1.5; the package has since been restructured (NDTensors rewrite, MPS code split into ITensorMPS.jl) and nobody has re-run the comparison.
- Small bond dimension 2D QN DMRG: the same data show C++ ahead (DMRG 2D QN maxdim 1000: 405.8 s Julia vs 334.8 s C++; DMRG 1D QN maxdim 200: 18.0 s vs 16.9 s).
- Relying on multi-threaded BLAS for speed: in the logs neither side scales with MKL threads on these block-sparse problems (Julia per-sweep 1303, 1091, 1042 s at 1, 4, 8 threads).

## How it is fast

Heavy lifting is dense GEMM/SVD/eigensolver calls in BLAS/LAPACK (Intel MKL in the benchmark, through MKL.jl), so at large bond dimension both versions mostly run the same MKL kernels. The Julia side's block-sparse contraction code in NDTensors.jl, Strided.jl permutations and KrylovKit Lanczos/Davidson steps are compiled by Julia's LLVM JIT for the concrete element and block types. The benchmark sources give no reason for the gap; the logs show it per sweep (for example 1303 s per sweep for Julia against 1875 s wall and 1640 s CPU for C++ at maxdim 10000), which points at the block-sparse bookkeeping and contraction layer rather than BLAS. An optional splitblocks transform (sparser MPO blocks) existed only in Julia, but the compared rows do not use it.

## Compared with alternatives

The siblings in this category are single kernels or solvers (TriangularSolve.jl and Gaius.jl against MKL/OpenBLAS, OrdinaryDiffEq.jl against Sundials, Yao.jl for state-vector circuits); pick ITensors.jl when the job is a tensor-network algorithm such as DMRG on large, QN-conserving systems, where it is the only catalogued Julia library with a matched comparison against a mature C++ code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia packages NDTensors, Strided, Dictionaries, StaticArrays, TimerOutputs, TupleTools and others from the General registry; ITensorMPS.jl for DMRG and MPS/MPO; MKL.jl recommended in the README for performance; optional HDF5, TensorOperations, VectorInterface, ZygoteRules extensions |
| **Minimum toolchain** | Julia 1.10 (current Project.toml compat); the benchmarked v0.1.36 ran on Julia 1.5.2 and 1.5.3 |
| **Platforms** | any platform Julia supports; BLAS backend selectable (OpenBLAS default, MKL through MKL.jl) |
| **Thread safety** | not documented in what was read; block-sparse multithreading is enabled with ITensors.enable_threaded_blocksparse() and Julia threads, and the benchmark runner errors out when both block-sparse threads and BLAS threads exceed 1 |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the 'Julia slower at small size' TRG and CTMRG rows: the warm-up call runs with outputlevel 0, but the timed call uses outputlevel 1, which executes @show of exp(-beta \* ising_free_energy(beta)) (a QuadGK.quadgk integral from ITensors.jl examples/src/2d_classical_ising.jl) and ising_magnetization. The first timed run in each Julia process therefore includes JIT compilation of QuadGK and the reference integral, work the C++ side never does. The log 2021-01-26T16:09 shows TRG maxdim 10 at 1.111 s for the first (1 BLAS thread) run, then 0.090, 0.077 and 0.078 s at 2, 3 and 4 threads in the same process, against C++ 0.158-0.174 s; CTMRG maxdim 50 (first run of the 2021-01-22 process) is 2.33 s against 1.32-1.46 s for the later Julia runs. The published 1.11 s vs 0.16 s TRG row is a compile artifact; once compiled Julia is about 2x faster there, though C++ timing also includes process launch.
- Version label mismatch: the data folder is data/julia/v0.1.37 and the runner default says v0.1.37, but the run logs print 'Using ITensors.jl v0.1.36' and wrote to data/julia/v0.1.36 (2464.746600888 s for conserve_ky maxdim 6000 appears in both); the committed Manifest.toml also pins ITensors 0.1.36 and NDTensors 0.1.22. The logs do give what the record lacks: Julia v1.5.2 and v1.5.3, Julia BLAS vendor mkl, and the actual C++ build line (g++ -m64 -std=c++17 -fconcepts -fPIC -O2 -DNDEBUG -fopenmp, Intel Parallel Studio 2020.4.304 MKL). Julia's MKL version is not recorded, so the two sides may use different MKL builds.
- C++ single-thread wall time exceeds its CPU time by about 14% (conserve_ky maxdim 10000 sweep 7: CPU 27m26s, wall 31m20s; maxdim 6000: 11m24s vs 12m57s), so the C++ process was waiting on something (memory or contention on the shared cluster node). Julia prints wall time only. Using C++ CPU time instead of wall, the maxdim 10000 last-sweep gap shrinks from 1.44x to about 1.26x (1303 s vs 1640 s), still a Julia win.
- The C++ link line mixes the single dynamic library -lmkl_rt with the layered -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core; at 4 and 8 MKL threads the C++ CPU time rises 4x and 8x while wall time stays at about 31 minutes per sweep, so the multi-thread C++ data say little. Results agree numerically (final energies -26.6761544 on both sides at maxdim 6000, TRG kappa identical to 15 digits), so the work matches; each figure is a single run with no variance.

## Known shortcomings

- No CPU; C++ at -O2 from the sample options.mk; the C++ timing includes process launch; 2021 data; Julia slower at small bond dimension.
- Harness flaw: warm-up runs use outputlevel 0 but the timed run uses outputlevel 1, which @shows ising_free_energy, a QuadGK integral, so the first timed Julia run in each process includes QuadGK JIT compilation; the published 'Julia slower' TRG maxdim 10 row (1.11 s vs 0.16 s) is a compile artefact (the same process at 2-4 BLAS threads gives 0.077-0.090 s against C++ 0.158-0.174 s), as is the CTMRG maxdim 50 row (2.33 s vs 1.32-1.46 s for later Julia runs). Logs fill gaps: Julia 1.5.2/1.5.3 with MKL, C++ g++ -O2 with MKL 2020.4.304; the data folder says v0.1.37 but logs and Manifest show ITensors.jl v0.1.36. C++ single-thread wall time is about 14% above its CPU time (on CPU time the maxdim 10000 last sweep is 1.26x, not 1.44x; Julia still wins); the C++ link line mixes -lmkl_rt with layered MKL libraries and its wall time stays flat at 4 and 8 threads. Energies match on both sides.

## Caveats and trade-offs

Numbers read from the raw .txt files under data/ (for example data/c++/v3.1.6/bench_dmrg_2d_conserve_ky/blas_num_threads_1/blocksparse_num_threads_1/maxdim_10000.txt and the same path under data/julia/v0.1.37); every cited figure matches. Same model, sweeps, maxdim schedule, noise, zero cutoff and initial state on both sides, and ITensors.jl v0.1.37's eigsolve_krylovdim 3 / maxiter 1 is documented in its dmrg.jl as equivalent to C++ Niter 2, so the work is matched. Timing asymmetry: Julia is warmed up first (maxdim 10, 2 sweeps) and timed with @elapsed in-process, while C++ is timed with @elapsed around a bash script that launches the binary, so C++ rows include process start and library loading (matters only for the sub-second TRG/CTMRG rows). C++ built at -O2 (sample options), not -O3, though large-bond-dimension time is dominated by MKL on both sides. No CPU model for this data (the TeNPy comparison page in the same repo names 4 x Xeon Gold 6128 for its own runs only). Data from February 2021 (benchmark repo last commit 2021-12-06, stale); ITensors.jl has since been rewritten around NDTensors and C++ ITensor has moved on. Single runs, no variance. Julia is not uniformly faster: it loses at small bond dimension (TRG maxdim 10 1.11 s vs 0.16 s, CTMRG maxdim 50 2.33 s vs 0.92 s, DMRG 2D QN maxdim 1000 405.8 s vs 334.8 s). The SciPost Phys. Codebases 4 (2022) paper (arXiv 2007.14822) has a Julia-versus-C++ benchmark section per a search snippet; scipost.org and arxiv.org were not reachable, so its figures were not checked against these data. [retier] Warm-up runs use outputlevel 0 but the timed run uses outputlevel 1, which @shows ising_free_energy (a QuadGK integral), so the first timed Julia run in each process includes QuadGK JIT compilation: the published 'Julia slower' TRG maxdim 10 row (1.11 s vs 0.16 s) is a compile artefact (the same process at 2-4 BLAS threads gives 0.077-0.090 s against C++ 0.158-0.174 s), as is the CTMRG maxdim 50 row. C++ single-thread wall time is about 14% above its CPU time, so on CPU time the maxdim 10000 last sweep is 1.26x, not 1.44x (Julia still wins); C++ wall time stays flat at 4 and 8 threads. Energies match on both sides.

Needs the Julia runtime and JIT warm-up (the small-size rows are slower than C++, plausibly from startup and compile overhead, not stated by the source). Julia version adds splitblocks (sparser MPO), absent from C++ ITensor; the plain runs above do not use it. C++ ITensor stays the smaller dependency for embedding in C++ programs.

## Maintenance

ITensors.jl is active (v0.9.32, last commit 2026-09-27, Apache-2.0, 686 stars) and installable from the General registry, but the benchmark repo is stale since 2021-12 and pinned to ITensors 0.1.36 and Julia 1.5, so its numbers describe a five-year-old code base on both sides.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party ITensor benchmark repo with public code for both sides (src/bench_\*/runbenchmark.jl and runbenchmark.h, src/runbenchmarks.jl) and raw timings under data/, but no CPU model, no Julia version and only a sample options.mk for the C++ build; the SciPost Codebases paper (Section 12.1 compares the Julia and C++ versions) was seen only as a search snippet, so C.
- **Verifier notes:** Keep at C with shortcomings 'first-party, no CPU model, C++ at -O2 from a sample options file, C++ timing includes process launch, stale 2021 data, Julia slower at small bond dimension'. All cited numbers verified against the raw data files; same_algorithm confirmed from the paired benchmark sources. Metadata checked: 686 stars, Apache-2.0, last commit 2026-09-27, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-100 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/ITensor/ITensorBenchmarks.jl/tree/main/data>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/c++/v3.1.6/bench_dmrg_2d_conserve_ky/blas_num_threads_1/blocksparse_num_threads_1/maxdim_10000.txt>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/julia/v0.1.37/bench_dmrg_2d_conserve_ky/blas_num_threads_1/blocksparse_num_threads_1/maxdim_10000.txt>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/deps/options.mk.sample>
  - <https://github.com/ITensor/ITensorBenchmarks.jl/tree/main/src>
  - <https://github.com/ITensor/ITensorBenchmarks.jl/tree/main/src/bench_dmrg_2d_conserve_ky>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_dmrg_2d_conserve_ky/runbenchmark.h>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_dmrg_2d_conserve_ky/runbenchmark.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/runbenchmarks.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensor/v3.1.6/itensor/mps/sweeps.h>
  - <https://raw.githubusercontent.com/ITensor/ITensors.jl/v0.1.37/src/mps/dmrg.jl>
  - <https://github.com/ITensor/ITensors.jl>
  - <https://github.com/ITensor/ITensors.jl/commits/main>
  - <https://github.com/ITensor/ITensorBenchmarks.jl/commits/main>
- **Sources the enricher read:**
  - <https://github.com/ITensor/ITensors.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensors.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/ITensor/ITensors.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/ITensor/ITensors.jl/v0.1.36/examples/src/2d_classical_ising.jl>
  - <https://github.com/ITensor/ITensors.jl/issues?q=is%3Aissue+performance+slower>
  - <https://github.com/ITensor/ITensors.jl/issues?q=is%3Aissue+label%3Aperformance>
  - <https://github.com/ITensor/ITensorBenchmarks.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/Manifest.toml>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/ITensorBenchmarks.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/runbenchmarks.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/deps/options.mk.sample>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_dmrg_2d_conserve_ky/runbenchmark.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_dmrg_2d_conserve_ky/runbenchmark.h>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_trg/runbenchmark.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_trg/runbenchmark.h>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_ctmrg/runbenchmark.jl>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/src/bench_ctmrg/runbenchmark.h>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/docs/src/index.md>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/docs/make.jl>
  - <https://github.com/ITensor/ITensorBenchmarks.jl/tree/main/logs>
  - <https://github.com/ITensor/ITensorBenchmarks.jl/tree/main/data/julia>
  - https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/logs/2021-01-22T18:02:18.798_benchmark_["ctmrg", "dmrg_1d", "dmrg_1d_qns", "dmrg_2d_conserve_ky", "dmrg_2d_qns", "trg"]_blas_num_threads_1:8_blocksparse_num_threads_1.log
  - https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/logs/2021-01-28T21:45:43.189_benchmark_["dmrg_2d_conserve_ky"]_blas_num_threads_[1, 4, 8]_blocksparse_num_threads_1.log
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/logs/2021-01-26T16:09:43.929_benchmark_["trg"]_blas_num_threads_1:4_blocksparse_num_threads_1.log>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/julia/v0.1.37/bench_dmrg_2d_conserve_ky/blas_num_threads_1/blocksparse_num_threads_1/maxdim_6000.txt>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/julia/v0.1.37/bench_dmrg_2d_conserve_ky/blas_num_threads_1/blocksparse_num_threads_1/maxdim_10000.txt>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/c++/v3.1.6/bench_dmrg_2d_conserve_ky/blas_num_threads_1/blocksparse_num_threads_1/maxdim_6000.txt>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/c++/v3.1.6/bench_dmrg_2d_conserve_ky/blas_num_threads_1/blocksparse_num_threads_1/maxdim_10000.txt>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/julia/v0.1.37/bench_trg/blas_num_threads_1/blocksparse_num_threads_1/maxdim_10.txt>
  - <https://raw.githubusercontent.com/ITensor/ITensorBenchmarks.jl/HEAD/data/c++/v3.1.6/bench_trg/blas_num_threads_1/blocksparse_num_threads_1/maxdim_10.txt>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/itensor/itensors.jl`) · [data/wave14/enrich/raw/github_com_itensor_itensors_jl.json](../../../data/wave14/enrich/raw/github_com_itensor_itensors_jl.json) (enrichment confidence 0.75)

</details>
