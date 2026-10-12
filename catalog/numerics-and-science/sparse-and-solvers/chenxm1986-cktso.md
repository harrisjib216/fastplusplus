# CKTSO (parallel sparse direct solver for circuit simulation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C (prebuilt shared libraries with a C header; source not published)` · `Proprietary freeware binaries with no license text; the library requires a signed key file (license/cktso.lic) whose EXPIRE field is 2028-12-31` · 🟢 active

> Closed-source parallel sparse LU solver for SPICE circuit matrices; first-party claims &gt;3x over KLU sequential, &gt;25x at 16 threads.

| | |
|---|---|
| **Beats** | KLU from SuiteSparse (sequential, approximate minimum degree ordering); README also names NICSLU, Intel MKL PARDISO and two GPU-based sparse solvers |
| **Claimed result** | IEEE TCAD 2025 paper (doc/tcad.pdf), 56 SuiteSparse circuit matrices, Xeon Gold 6130, best case where fast refactorization never re-pivots: 5.9x over NICSLU and 11.9x over oneMKL PARDISO at 16 threads, about 20% lower when 10% of runs re-pivot. README (first-party, no hardware): more than 3x over sequential KLU and more than 25x with 16 threads; the 2022 results PDF shows about 2.8x and 14.6x over KLU. |
| **Workload** | LU factorization and solve of 66 circuit matrices from the SuiteSparse collection (dimensions 1K to 5M). |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6130 (16 cores, 2.1 GHz), 256 GB RAM (doc/results(version202205).pdf); README averages give no hardware |
| **Compiler and flags** | gcc 4.8.5 on CentOS 7.9 for the version-202205 comparison PDF; flags not stated; prebuilt binaries are shipped per platform (centos6 gcc482, centos7 gcc485, rocky8 gcc850, win7) |
| **Adoption** | 47 stars |
| **Last commit** | 2026-03-26 |
| **Links** | [repository](https://github.com/chenxm1986/cktso) · [benchmark](https://github.com/chenxm1986/cktso/blob/master/doc/tcad.pdf) |

## Verdict

The README's 'on average &gt;3x faster than sequential KLU (AMD ordering) when sequential and &gt;25x with 16 threads' on 66 SuiteSparse circuit matrices is first-party with no hardware or method; the 2022 results PDF (old version, Xeon Gold 6130 16 cores, gcc 4.8.5, KLU given NICSLU's ordering) shows about 2.8x and 14.6x. The author's IEEE TCAD 2025 paper, shipped in the repo as doc/tcad.pdf, compares only with NICSLU and oneMKL PARDISO on 56 circuit matrices on the same Xeon Gold 6130, mostly in the best case where fast factorization never re-pivots: 5.9x over NICSLU and 11.9x over PARDISO at 16 threads, about 20% lower when 10% of runs re-pivot. The shipped demo/benchmark.cpp likewise times 100 Factorize(ax, fast=true) calls on unchanged values, so its numbers are also that best case.

## Use it when

- SPICE-style transient or DC simulation on x86-64 with AVX2/FMA, where the same sparsity pattern is factorized hundreds of times and KLU's sequential refactorization dominates run time.
- Large post-layout, power-grid or mesh-like circuit matrices, where its nested-dissection ordering cuts fill-in sharply versus AMD-based KLU or NICSLU (the paper names G3_circuit, G2_circuit, memchip, meg1 and FullChip).
- Multi-core workstations (the paper uses a 16-core Xeon Gold 6130) where you want parallel factorization with KLU-style full-row threshold partial pivoting rather than a partitioned BBD approach.
- Commercial or in-house simulators that can accept a binary dependency and want KLU-like call structure (analyze / factorize / refactorize / solve) with a separate GPU add-on (CKTSO-GPU) available later.

## Skip it when

- Anything that must be open source, auditable, rebuilt, or shipped on non-x86 hardware: only x86-64 Linux (CentOS 6/7, Rocky 8) and Windows binaries exist; Apple Silicon support is an open request (issue #3).
- Deployments that cannot depend on a licence key: the library refuses to run (error -99) without license/cktso.lic next to the .so/.dll, and the shipped key carries an expiry date (2028-12-31).
- One-shot solves or non-circuit matrices: analysis is slow by design (it races 10 orderings), the first factorization and first parallel solve are much slower than later ones, and the author says the implementation is tuned for circuit matrices; on several of the largest matrices MKL PARDISO factorized faster in the 2022 results PDF.
- Single-precision, or complex-heavy workloads where speed matters: only double (real or complex) is offered and the user guide says complex performance is not yet fully optimised.
- Projects needing responsive support: open issues on parallel slowdown on Windows (#12), thread auto-detection (#14), natural-ordering failures (#16) and a demo crash in an MSVC debug build (#18) have no maintainer replies.

## How it is fast

Ordering: it runs 10 fill-reducing orderings (8 minimum-degree variants, 2 nested-dissection variants) and keeps the one with the fewest predicted flops; the TCAD paper reports NICSLU's AMD-style ordering produces 39.8% and METIS-based PARDISO 188% more factorization flops than CKTSO's on 56 circuit matrices. Factorization: a pivoting-reduction 'fast factorization' reuses the previous pivot order and symbolic structure while checking each pivot, falling back to partial pivoting from the first bad row, which lets it parallelise like a refactorization. Solving: a structure-adaptive hybrid parallel forward/backward substitution, plus supernode detection and adaptive kernel selection, with AVX2 and FMA required.

## Compared with alternatives

Pick CKTSO over GSS (also binary-only, compared with an old PARDISO) or RSLAB (pure-Rust KLU-style solver measured against PARDISO) when the matrices come from SPICE and you can run on x86-64 with a licence key and want multi-core refactorization; pick PanguLU instead for distributed multi-GPU LU on general matrices, and stay with KLU when source access, portability or a sequential embedded build matters more than speed.

## Integration

| | |
|---|---|
| **Form** | shared lib (prebuilt .so / .dll per platform) plus one C/C++ header; no source |
| **Dependencies** | none beyond the C/C++ runtime per the README; a licence key file cktso.lic must sit beside the library |
| **Minimum toolchain** | Binaries built with gcc 4.8.2 (CentOS 6), gcc 4.8.5 (CentOS 7), gcc 8.5.0 (Rocky 8) and for Windows 7+ x64; the demos compile with g++ -O3 -std=c++11; the header also works from C99 (stdbool.h) |
| **Platforms** | x86-64 only, CPU must support AVX2 and FMA (CKTSO_CreateSolver returns -10 otherwise; CKTSO_CreateSolverNoCheck skips the check for VMs that hide the flags); Linux and Windows |
| **Thread safety** | One solver instance owns a thread pool created at Analyze; the tips document says several instances may run in parallel only if each runs in its own thread, and one instance may handle several matrices in turn |
| **Drop-in for the baseline** | partial — same analyze/factor/refactor/solve flow as KLU, but a different API, CSR (row) rather than KLU's CSC input unless column mode is selected, and a licence file to deploy |

## Gotchas

- Pass representative values (not NULL) to CKTSO_Analyze: with ax=NULL static pivoting is disabled and ordering is structure-only, which the tips document warns can increase fill-in dramatically.
- Fast factorization (Factorize with fast=true) is unsafe after a big change in values: the tips say to disable it for the first factorization of each DC method or stepping value and after a time-step rollback.
- Parallel solve needs a setup costing about 2-5x a sequential solve each time the LU structure changes, and the tips do not recommend parallel solve for column-mode matrices on Windows; the library may silently fall back to one thread based on matrix features (check oparm[18]).
- Default threads=0 uses all physical cores as detected; the user guide recommends setting the count explicitly, and auto-detection in cloud VMs is reported as unreliable (issue #14).

## Known shortcomings

- Binary only with no license text and a signed key file that expires 2028-12-31; its 2022 results PDF shows about 2.8x/14.6x over KLU (KLU given NICSLU's ordering), and MKL PARDISO is faster on some of the largest matrices.
- README's &gt;3x/&gt;25x over KLU is first-party with no hardware or method; the 2022 results PDF (Xeon Gold 6130, gcc 4.8.5, KLU given NICSLU's ordering) shows \~2.8x and \~14.6x. The peer-reviewed IEEE TCAD 2025 paper shipped as doc/tcad.pdf compares only with NICSLU and oneMKL PARDISO, mostly in the best case where fast refactorization never re-pivots (about 20% lower at 10% re-pivot); demo/benchmark.cpp also times that best case. Binary-only distribution. Open issues #12/#14/#16/#18 have no maintainer replies.

## Caveats and trade-offs

Binary-only: the repository ships compiled libraries, a header, demos and docs, not source, so it cannot be audited or copied. The library needs license/cktso.lic, a signed key file with EXPIRE = 2028-12-31, so a pinned binary can stop working when the key expires. The README averages (&gt;3x, &gt;25x) are first-party without hardware or method; the 2022 PDF is from an old version ('results are from an old version') and shows lower KLU ratios (about 2.8x and 14.6x), in part because KLU there used NICSLU's ordering. Its scatter plots show MKL PARDISO factorizing several of the largest matrices (over 1M rows) faster than CKTSO, so the averages hide losses on big cases. The GPU-solver comparisons reuse numbers from other papers rather than running those solvers. The IEEE TCAD 2025 paper was not opened.

x86-64 binaries only (CentOS 6/7, Rocky 8, Windows 7 x64); needs a license key file (license/cktso.lic) next to the library; specialised for SPICE-style circuit matrices; races 10 reordering methods, so analysis is slow by design.

## Maintenance

Actively updated (latest version 20260321, last commit 2026-03-26) but distributed as proprietary binaries with no licence text and a time-limited key, so it is a reference to call, not code to copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** The README's KLU averages are first-party and doc/results(version202205).pdf adds first-party charts with partial methodology (gcc 4.8.5 without flags, Intel Xeon Gold 6130 16-core, KLU 1.3.9, NICSLU 202110, MKL PARDISO 2022.0.2, 66 SuiteSparse circuit matrices); the solver is closed-source binaries and no harness is published, so C. The IEEE TCAD 2025 paper could not be opened (dl.acm.org and arxiv.org blocked) and search results did not show its abstract numbers.
- **Retiered** C to B: Peer-reviewed IEEE TCAD 2025 paper, shipped in the repo as doc/tcad.pdf, measures CKTSO against NICSLU and oneMKL PARDISO on 56 circuit matrices on a Xeon Gold 6130; the README's KLU figures remain first-party.
- **Verifier notes:** Opened the results PDF (rendered pages 1-4) and the license directory: no licence text, only a readme and a signed key file with an expiry date (shortcoming worth recording). Repo page: 47 stars, 8 forks, 88 commits, not a fork; latest commit 2026-03-26 ('20260321').
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `license`, `caveats`, `benchmark_url`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/chenxm1986/cktso/HEAD/README.md>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/doc/results%28version202205%29.pdf>
  - <https://github.com/chenxm1986/cktso>
  - <https://github.com/chenxm1986/cktso/commits>
  - <https://github.com/chenxm1986/cktso/tree/master/license>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/license/readme.txt>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/license/cktso.lic>
- **Sources the enricher read:**
  - <https://github.com/chenxm1986/cktso>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/HEAD/README.md>
  - <https://github.com/chenxm1986/cktso/tree/master/include>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/include/cktso.h>
  - <https://github.com/chenxm1986/cktso/tree/master/doc>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/doc/changelog.txt>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/doc/tcad.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/doc/tips%20and%20faqs.pdf>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/doc/ug.pdf>
  - <https://github.com/chenxm1986/cktso/tree/master/demo>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/demo/readme.txt>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/demo/Makefile>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/demo/benchmark.cpp>
  - <https://github.com/chenxm1986/cktso/tree/master/rocky8_x64_gcc850>
  - <https://raw.githubusercontent.com/chenxm1986/cktso/master/license/readme.txt>
  - <https://github.com/chenxm1986/cktso/issues>
  - <https://github.com/chenxm1986/cktso/issues/12>
  - <https://github.com/chenxm1986/cktso/issues/14>
  - <https://github.com/chenxm1986/cktso/issues/16>
  - <https://github.com/chenxm1986/cktso/issues/18>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/chenxm1986/cktso`) · [data/wave8/enrich/raw/github_com_chenxm1986_cktso.json](../../../data/wave8/enrich/raw/github_com_chenxm1986_cktso.json) (enrichment confidence 0.8)

</details>
