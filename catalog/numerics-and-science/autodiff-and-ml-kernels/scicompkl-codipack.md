# CoDiPack (operator-overloading AD, expression templates)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> Header-only C++17 operator-overloading AD with expression templates; peer-reviewed paper reports it beats ADOL-C and roughly matches Adept.

| | |
|---|---|
| **Beats** | ADOL-C and Adept (other C++ operator-overloading AD tools); none of the listed baselines (oneDNN, cuDNN, XNNPACK, Eigen tensor) apply |
| **Claimed result** | Per search-result summaries of the TOMS paper (not opened): CoDiPack's tapes perform similarly to Adept, with tape memory reduced by 15% (1-argument statements) to 5% (4-argument statements) relative to Adept's Jacobian-taping layout, and the index-handling tapes cut reverse interpretation time; the comparison against ADOL-C (primal taping) is in the paper but its factors were not seen. No speedup figure was verified. |
| **Workload** | Tape recording and reversal time and tape memory for a coupled Burgers-equation PDE test and for SU2 CFD (inviscid flow over the LM1021 supersonic aircraft), versus Adept and ADOL-C, with GCC and Intel compilers (per the TOMS paper as described by search results; paper not opened). |
| **Metric** | throughput |
| **Adoption** | 119 stars; evaluated on the SU2 CFD suite in its paper and reported (search snippets) in the ISSM ice-sheet model; developed at TU Kaiserslautern (RPTU) |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/SciCompKL/CoDiPack) · [benchmark](https://arxiv.org/abs/1709.07229) |

## Verdict

Not reproduced here: the only evidence is the peer-reviewed ACM TOMS 45(4) 2019 paper, which per search-result text compares CoDiPack's tape types with Adept and ADOL-C on a coupled Burgers test and on SU2 with GCC and Intel compilers, finding CoDiPack faster and lighter than ADOL-C and close to Adept, with index tapes speeding up reverse interpretation. CPU model, compiler versions, flags and exact ratios were not seen because the paper hosts are blocked from this session.

## Use it when

- Gradients of large simulation codes (CFD, PDE solvers; the paper evaluates SU2) where tape memory, not only speed, limits what you can differentiate
- Existing double-based C++ code where you can substitute a type, and you want to trade memory for generality by switching among RealReverse, RealReverseIndex, RealReversePrimal and RealReversePrimalIndex without changing user code
- MPI or OpenMP parallel codes, via MeDiPack and the RealReverseIndexOpenMP / OpDiLib bindings
- Mixed workflows that need external functions, preaccumulation, tape editing, tape writing to disk or Enzyme-generated derivatives inserted into the tape (helper since v2.2.0)
- Open-source (GPL-3.0) projects, or teams willing to negotiate a different license with the RPTU group

## Skip it when

- Closed-source distribution without a separate license: CoDiPack is GPL-3.0
- When raw speed over Adept 2 is the goal: per search-result summaries the TOMS paper shows rough parity with Adept (a few percent less tape memory), and no public benchmark harness exists to check it
- Small statically known expression graphs, where FastAD's paper claims 2-10x over Adept (not measured against CoDiPack)
- Plain multithreaded code using the default types: the default active types share one static tape per type, so threads need the OpenMP-specific types
- Projects stuck on C++11/14: CoDiPack 3.x requires C++17 (use the 2.x series otherwise)

## How it is fast

Expression templates collapse each full right-hand-side statement into one tape entry instead of one entry per elementary operation. Two taping strategies are offered: Jacobian taping (stores the statement's partial derivatives, as Adept and dco/c++ do) and primal value taping (stores primal values and re-evaluates the statement's derivative from generated code during the reverse sweep, as ADOL-C does, but with expression templates). Index managers either hand out linear identifiers or reuse freed ones (the \*Index types), which shrinks the adjoint vector; per search-result text of the TOMS paper, that smaller footprint is what makes the index-reuse tapes faster in the reverse interpretation.

## Compared with alternatives

Pick CoDiPack over Adept 2 or XAD when you need primal-value tapes, index-reuse memory savings, MPI/OpenMP support or Enzyme integration for a large simulation code, and GPL-3.0 is acceptable; XAD has the stronger published head-to-head numbers (vendor-run) and Adept 2 a more permissive Apache-2.0 license. Enzyme and Clad avoid operator overloading altogether but need an LLVM/Clang toolchain.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optional: Eigen, MPI via MeDiPack, OpenMP/OpDiLib, Enzyme) |
| **Minimum toolchain** | C++17 for 3.x (CMake target sets cxx_std_17; 2.x for C++11); README says tested with GCC, Clang and Intel; CMake 3.12+ for the package config |
| **Platforms** | any platform with a C++17 compiler; CI runs clang++ on Ubuntu; MSVC compile problems were reported and closed in issues 5, 16 and 29 |
| **Thread safety** | Default types use a static global tape per active type (not safe across threads); RealReverseIndexOpenMP and OpDiLib bindings (since v2.1.0) provide thread-safe taping with atomic adjoint updates |
| **Drop-in for the baseline** | partial — swapping double for the active type is source-compatible in most code, but the tape API differs from Adept and ADOL-C, so driver code must be rewritten |

## Gotchas

- Performance depends on inlining, and the README's recommended -DCODI_UseForcedInlines is stale: include/codi/config.h in 3.1.2 only reads CODI_ForcedInlines (default 0), so define that name to actually force inlining
- The \*Index types do not support C-style memory operations such as memcpy on active values; RealReverse and RealReversePrimal do
- Open issue 49 (v2.3.2, clang 16): with a variable repeated in one statement and a 1e30 term, forward returns 0 and reverse -14 (or the reverse when operands are swapped); per-occurrence partials are summed in an order that loses the small term, and splitting the statement fixes it. Closed issue 46 shows a similar cancellation with no documented fix
- The static tape makes gdb output verbose; the README suggests 'set print static-members off'

## Known shortcomings

- Win over Adept is marginal (parity plus 5-15% less tape memory); no harness in the repo; paper (arXiv 1709.07229) not opened here.
- Open #49: forward and reverse derivatives disagree (0 vs -14) through cancellation when a variable repeats in one statement; closed #46 is similar with no documented fix. README flag -DCODI_UseForcedInlines is stale (config.h 3.1.2 reads only CODI_ForcedInlines). Default types share one static tape, not thread-safe. Paper numbers unverified here.

## Caveats and trade-offs

I could not open the evidence: the README of the repo (opened) cites the peer-reviewed paper 'High-Performance Derivative Computations using CoDiPack' (Sagebaum, Albring, Gauger, ACM TOMS 45(4), 2019, doi 10.1145/3356900, arXiv 1709.07229), but dl.acm.org, arxiv.org, ar5iv, researchgate, arxiv-vanity, groundai and scicomp.rptu.de were all blocked by the egress proxy. Everything below about numbers comes from web-search result snippets and is UNVERIFIED: (a) CoDiPack vs Adept performance quite similar, CoDiPack slightly faster at recording and reversal and 7% (250 MB) less memory; (b) SU2 LM1021 test with 5,730,841 interior elements: relative runtime factors of 3.1 to 4.47 for recording and 0.4 to 0.86 for interpretation of one flow iteration without preaccumulation (baseline of that ratio not confirmed); (c) an independent third-party paper (AD-HOC, arXiv 2412.05300, snippet only) lists first-order derivative-to-primal runtime ratios ADOL-C 8.36x, dco/c++ 3.03x, CoDiPack 3.63x, i.e. CoDiPack about 2.3x faster than ADOL-C there (derived from snippet data). Hardware, compiler versions and flags are unknown. The repo itself has no benchmark directory (tests/ has events, functional, general only) and its README and docs make no numeric performance claim. Tier B rests on peer review only; a verifier able to open the paper should confirm the numbers, the CPU model and the flags, which could move this to A (benchmark code for the paper may not be public) or down to C. Not a numerical-kernel library of the listed baselines (oneDNN, cuDNN, XNNPACK, Eigen tensor): competes with other AD tools, so category fit is loose.

Header-only, C++17 (2.x release for C++11). GPL-3.0 (other licensing on request), so linking proprietary code needs a commercial arrangement. Operator overloading with expression templates: needs the active type substituted into the code, tapes cost memory proportional to the number of operations, and performance depends on forced inlining (-DCODI_UseForcedInlines recommended in the README). Several tape types (RealReverse, RealReverseIndex, RealReversePrimal, RealReversePrimalIndex) trade memory against generality.

## Maintenance

Actively maintained by the RPTU Scientific Computing group (v3.1.2 released 2026-07-13, regular feature releases since 2015); GPL-3.0 header-only, so easy to vendor for open-source projects but a licensing question for proprietary ones.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The only evidence is the peer-reviewed ACM TOMS 45(4) 2019 paper cited in the README; search results confirm it benchmarks CoDiPack's four tape types against Adept and ADOL-C (coupled Burgers test, GCC and Intel compilers), but the paper itself (arXiv 1709.07229, dl.acm.org) is blocked here, so no number, CPU or flag was seen. Kept at B on the peer-review precedent; the repo has no benchmark code, so A is not reachable from it.
- **Verifier notes:** arxiv.org and deepai.org returned EGRESS_BLOCKED; dl.acm.org not retried (blocked per harness). Metadata confirmed (GPL-3.0, 119 stars, last commit 2026-07-29 'Update version to 3.1.2'). Record shortcoming: win over Adept is marginal (parity plus a few percent memory), numbers unverified, no public benchmark harness in the repo.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/SciCompKL/CoDiPack>
  - <https://github.com/SciCompKL/CoDiPack/commits>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/SciCompKL/CoDiPack>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/README.md>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/cmake/codipack-include.cmake>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/include/codi.hpp>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/include/codi/config.h>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/include/codi/expressions/activeType.hpp>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/include/codi/tools/parallel/openmp/codiOpenMP.hpp>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/documentation/Changelog.md>
  - <https://raw.githubusercontent.com/SciCompKL/CoDiPack/HEAD/.github/workflows/tests.yml>
  - <https://github.com/SciCompKL/CoDiPack/tree/master/documentation>
  - <https://github.com/SciCompKL/CoDiPack/tree/master/.github/workflows>
  - <https://github.com/SciCompKL/CoDiPack/issues?q=is%3Aissue>
  - <https://github.com/SciCompKL/CoDiPack/issues/49>
  - <https://github.com/SciCompKL/CoDiPack/issues/46>
  - <https://github.com/SciCompKL/CoDiPack/issues/28>
  - WebSearch: High-Performance Derivative Computations using CoDiPack (result snippets for arxiv.org/abs/1709.07229 and dl.acm.org/doi/10.1145/3356900; pages not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/scicompkl/codipack`) · [data/wave8/enrich/raw/github_com_scicompkl_codipack.json](../../../data/wave8/enrich/raw/github_com_scicompkl_codipack.json) (enrichment confidence 0.6)

</details>
