# RSLAB (pure-Rust sparse LDL^T, LU and KLU solver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust sparse LDL^T/LU/KLU direct solver; solve phase 2.3-3.3x faster than MKL PARDISO, factorization usually slower.

| | |
|---|---|
| **Beats** | Intel MKL PARDISO |
| **Claimed result** | Ratios to PARDISO time (below 1 is faster): solve 0.34 / 0.43 / 0.37 / 0.30 on the four classes (about 2.3x to 3.3x faster, derived from page data); factor 1.35 / 3.97 / 0.95 / 4.76 and refactor 1.38 / 4.28 / 0.90 / 1.83 (faster only on MoM near field); one-shot analysis+factor+solve 1.05 / 1.06 / 0.74 / 1.12 (faster only on MoM near field). |
| **Workload** | Wall time relative to PARDISO on 28 systems exported from production codes (6 FEM curl-curl, 2 power grid, 7 MoM near field, 13 SuiteSparse circuits), 12 threads each, geometric mean per class. |
| **Metric** | latency |
| **Hardware** | 12 threads; CPU model not stated |
| **Adoption** | 12 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/milanofthe/rslab) · [benchmark](https://github.com/milanofthe/rslab) |

## Verdict

The README table gives wall time relative to MKL PARDISO (pardisoinit defaults, taking the faster of classic and two-level factorization) on 28 non-public production systems at 12 threads, as a geomean per class. Solve time is 0.30-0.43 of PARDISO's (2.3-3.3x faster), while factorization is 0.95-4.76 and one-shot 0.74-1.12, so RSLAB is ahead end-to-end only on MoM near field. Both solvers are timed from the same Python harness (benches/pardiso_corpus.py), PARDISO through ctypes against pip-installed MKL; CPU model, Rust version and flags are not stated.

## Use it when

- Many solves per factorization (multiple right-hand sides, iterative refinement, Krylov preconditioning), where the solve phase at 0.30-0.43x PARDISO's time dominates.
- Method-of-moments near-field systems (complex): the one class where factor (0.95), refactor (0.90) and one-shot (0.74) time also beat PARDISO.
- Rust or Python projects that want a PARDISO-style solver without an MKL, BLAS or LAPACK dependency, or that need factors bit-identical across thread counts.
- Embedded or scheduled solves that must check memory before factoring: `memory_plan` and `estimate_memory` predict the heap peak from the analysis alone.
- Circuit-simulation sweeps on a fixed pattern through KLU `refactor`, or GMRES/COCG with a factor of a nearby matrix that never fails thanks to static pivoting.

## Skip it when

- Workloads dominated by factorization or one-shot solves on FEM curl-curl (factor 1.35x PARDISO's time), power-grid (3.97x) or circuit (4.76x) matrices, where PARDISO is faster.
- Medium-size circuit matrices with frequent refactorization: open issue #88 reports KLU refactor 3-8x behind PARDISO.
- Large complex-symmetric factorizations under memory pressure (#87: peak memory 2.3x PARDISO's), or x86 machines with many cores (#82: factorization scales poorly; #83: symbolic analysis takes 2.8x PARDISO's time).
- Saddle-point matrices with zero diagonals on the LU path with the default `lu_matching = true`. Issue #74 reports 154-408 floored pivots and 5e-5 relative accuracy on a complex EM saddle matrix, vs 1e-12 with matching off.
- C or C++ codebases (no C API; FFI exists only in the Python bindings), or teams that need a mature solver: 12 stars, and 31 PyPI releases between 2026-06-29 and 2026-09-29.

## How it is fast

LDL^T and LU are left-looking and supernodal, run in parallel over the elimination tree in a scoped rayon pool, and do their dense updates with the pure-Rust `gemm` crate (runtime AVX2/AVX-512 dispatch). Several fill-reducing orderings (AMD, AMF, RCM, parallel nested dissection) are tried and raced on the exact fill each produces, with MC64-style matching and scaling. The solve-phase advantage comes from supernodal, tree-parallel triangular solves over the factor's panels. The KLU path factors independent BTF blocks in parallel and refactors without a new pivot search.

## Compared with alternatives

Against GSS (trial binaries only, also benchmarked against PARDISO), pick RSLAB when you need MIT source and fast repeated solves. Pick CKTSO for C/C++ circuit simulators that care most about parallel factorization speed against KLU, and BaSpaCho for SPD Cholesky in C++. RSLAB covers indefinite, complex-symmetric and unsymmetric matrices in Rust or Python.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon, gemm 0.19, num-complex, serde/serde_json, plus in-workspace ordering crates (AMD, AMF, METIS-style nested dissection); optional ureq/flate2/tar (feature matgen-download) and sysinfo (feature tuning); Python wheels need numpy&gt;=1.21 and scipy&gt;=1.7 |
| **Minimum toolchain** | Rust 2021 edition on current stable (rust-toolchain.toml tracks stable; no rust-version/MSRV declared); Python &gt;= 3.9 for the bindings |
| **Platforms** | pure Rust (runtime AVX2/AVX-512 dispatch on x86, wasm32 clock shim in source); PyPI abi3 wheels for Linux x86-64 and aarch64 (manylinux_2_28), macOS x86-64 and arm64, and Windows x86-64 |
| **Thread safety** | Each factorization runs in its own scoped pool. Threads::Auto caps workers at 4 'so concurrent solves coexist', Threads::Ambient runs on the caller's rayon pool, and a caller-owned flag can interrupt a running factorization. Sharing one factor object across threads is not documented. |
| **Drop-in for the baseline** | partial — same phases (analyze, factor, solve) and matrix classes as PARDISO mtype 2, 6, 11 and 13, but a Rust/Python API, not the pardiso() C/Fortran interface |

## Gotchas

- The crates.io name `rslab` belongs to an unrelated slab-allocator crate (versions 0.1-0.2 from 2022). Depend on the git tag as the README shows; `cargo add rslab` pulls the wrong crate.
- The default Threads::Auto caps workers at 4. The README benchmark passed 12 threads explicitly, so pass `threads=0` (all cores) or `'auto'` to match it.
- The dense kernels allocate per product. The docs recommend a caching global allocator such as mimalloc, especially on Windows.
- Licensing: the code is MIT and forked from feral (MIT), with Hungarian/MC64 routines translated from SPRAL (BSD-3-Clause). Releases 0.20.0-0.23.0 contained METIS-derived Apache-2.0 code (see NOTICE).

## Known shortcomings

- Only the solve phase is faster than PARDISO; factorization is slower on 3 of 4 classes; the test corpus is private; Rust.
- Rust only, no C API. Correctness issue #74: default LU matching gives 5e-5 accuracy on saddle matrices (1e-12 with matching off). Open perf issues: #88 KLU refactor 3-8x behind PARDISO, #87 peak memory 2.3x PARDISO, #82/#83 x86 scaling and analysis. The crates.io name rslab is an unrelated slab allocator. 31 PyPI releases in 3 months; benchmark corpus not public.

## Caveats and trade-offs

Mixed result: the win is the solve phase; factorization and one-shot time are slower than PARDISO on three of four classes. The corpus is exported from production codes and the benchmark scripts take a corpus path, so the table cannot be reproduced from the README alone. CPU model, Rust version and flags are not given. MKL PARDISO is a proprietary baseline. The project started from the feral crate (MIT) and its commit history is very recent.

No BLAS, LAPACK or MKL needed; factor is bit-identical for every thread count; Python bindings (pip install rslab); built-in Krylov solvers use the factor as preconditioner; Threads::Auto is capped at 4 workers by default.

## Maintenance

Very active but young: 624 commits, v1.1.0 released 2026-09-29, 12 stars, one listed author, and open performance issues against PARDISO (#82, #83, #87, #88). MIT-licensed, installed from git or from PyPI wheels.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance table matches every ratio quoted; bench code is public (benches/pardiso_corpus.py) but the 28-system corpus is not, and no CPU model, Rust version or flags are given, so first-party C.
- **Verifier notes:** Mixed result recorded correctly: solve phase 2.3x to 3.3x faster than MKL PARDISO, factorization and one-shot slower on three of four classes (faster only on MoM near field). Metadata confirmed: MIT, 12 stars, 624 commits, release v1.1.0 on 2026-09-29, not a GitHub fork (README says it started from jkitchin/feral, MIT). PARDISO is loaded from pip-installed MKL runtime with pardisoinit defaults.
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/README.md>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/benches/pardiso_corpus.py>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/Cargo.toml>
  - <https://github.com/milanofthe/rslab>
  - <https://github.com/milanofthe/rslab/commits>
- **Sources the enricher read:**
  - <https://github.com/milanofthe/rslab>
  - <https://github.com/milanofthe/rslab/issues?q=is%3Aissue>
  - <https://github.com/milanofthe/rslab/issues/74>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/README.md>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/benches/pardiso_corpus.py>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/python/pyproject.toml>
  - <https://raw.githubusercontent.com/milanofthe/rslab/HEAD/python/docs/api.md>
  - <https://crates.io/api/v1/crates/rslab>
  - <https://pypi.org/pypi/rslab/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/milanofthe/rslab`) · [data/wave8/enrich/raw/github_com_milanofthe_rslab.json](../../../data/wave8/enrich/raw/github_com_milanofthe_rslab.json) (enrichment confidence 0.75)

</details>
