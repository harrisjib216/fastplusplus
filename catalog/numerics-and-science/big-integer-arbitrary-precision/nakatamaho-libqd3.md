# libQD3 (double-double, triple-double, quad-double, extended-double)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Maintained fork of the Hida-Li-Bailey QD library adding triple-double and binary80/binary32 expansions; fixed 106-212-bit floats, much cheaper than MPFR.

| | |
|---|---|
| **Beats** | MPFR (the MPLAPACK manual's Rgemm numbers for upstream QD against MPFR and GMP at their 512-bit default); libQD3's own docs/qd.tex also carries the original QD paper's per-operation timing table against Bailey's MPFUN |
| **Claimed result** | None for libQD3 itself. Lineage numbers: (1) MPLAPACK user manual (doc/manual/manual.pdf on master, titled 'MPLAPACK version 1.0.0 user manual', section 9 Benchmarks, upstream QD rather than libQD3): peak Rgemm, reference versions quad-double 33 MFlops, GMP 19 MFlops, MPFR 11 MFlops; OpenMP versions quad-double 1.3 GFlops, GMP 693 MFlops, MPFR 390 MFlops (about 3.0x MPFR single-threaded and 3.3x with OpenMP, derived from page data). (2) libQD3 docs/qd.tex timing table (original Hida/Li/Bailey QD, microseconds per operation, Pentium II 400 MHz): quad-double add 0.583, mul 1.965, sloppy mul 1.016, div 5.267 vs MPFUN add 5.729, mul 7.624, div 10.102 (about 9.8x, 3.9x and 1.9x, derived from page data); Power3 200 MHz: QD add 0.710, mul 1.131, div 6.699 vs MPFUN 4.651, 5.837, 9.180 (about 6.6x, 5.2x, 1.4x, derived from page data). |
| **Workload** | No benchmark of libQD3 itself found. Indirect lead: MPLAPACK's Rgemm (dense matrix multiply) benchmark with the upstream QD library as the quad-double back end, against MPFR and GMP back ends, on one machine. |
| **Metric** | throughput |
| **Hardware** | MPLAPACK Rgemm run: AMD Ryzen Threadripper 3970X, 256 GB DDR4-3200 (the manual says ECC is not enabled for the Rgemm runs and 'ECC Unbuffered' for the Raxpy runs), Docker. docs/qd.tex table: Intel Pentium II 400 MHz, Sun UltraSparc 333 MHz, PowerPC 750 266 MHz, IBM Power3 200 MHz. |
| **Compiler and flags** | MPLAPACK run: GCC 9.3.0 inside Docker, flags not stated. docs/qd.tex table: g++ 2.95.2 -O3 -funroll-loops -finline-functions -mcpu=i686 -march=i686 (Pentium II, PowerPC 750 without the -m flags), Sun CC 5.0 -xO5 -native (UltraSparc), IBM xlC -O3 -qarch=pwr3 -qtune=pwr3 -qstrict (Power3). |
| **Adoption** | 2 stars, 0 forks, 158 commits on main; MPLAPACK (same author, 108 stars) uses libQD3 as its QD back end per the MPLAPACK README |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/nakatamaho/libQD3) · [benchmark](https://raw.githubusercontent.com/nakatamaho/mplapack/master/doc/manual/manual.pdf) |

## Verdict

Nothing measures libQD3's current code. The inherited evidence is the original QD paper table in docs/qd.tex (Pentium II 400 MHz, g++ 2.95.2 -O3 -funroll-loops): quad-double add 0.583 us, mul 1.965 us, div 5.267 us vs Bailey's MPFUN 5.729, 7.624 and 10.102 us (about 9.8x, 3.9x, 1.9x, derived from page data), and the MPLAPACK manual's Rgemm peaks with upstream QD on a Threadripper 3970X (GCC 9.3.0, flags not stated): quad-double 33 MFlops vs 512-bit MPFR 11 MFlops single-threaded and 1.3 GFlops vs 390 MFlops with OpenMP, at unequal precision (212 vs 512 bits).

## Use it when

- C, C++ or Fortran inner loops that need 30-64 significant digits (ill-conditioned linear algebra, SDP solvers, Newton refinement) where 106, 159 or 212 bits is enough and MPFR's per-operation overhead dominates; the lineage evidence is upstream QD at 1.3 GFlops Rgemm vs 512-bit MPFR at 390 MFlops in MPLAPACK on a Threadripper 3970X.
- About 40-50 digits are needed: td_real does a default add in 41 flops vs 84 for qd_real and a multiply in 116 vs 182 flops with FMA (docs/td.tex flop counts, not timings), so you stop paying for QD's 63 digits.
- You want a maintained QD with complex types, exact int64/uint64 constructors, IEEE special-value handling in division and sqrt (1.4.0), MPFR/MPC oracle tests and a CMake package, instead of the older upstream QD releases.
- You build MPLAPACK or other code that already uses the QD API (dd_real/qd_real, fpu_fix_start), since libQD3 keeps that API and is MPLAPACK's QD back end.

## Skip it when

- You need more than about 212 bits, or precision chosen at run time: use MPFR, FLINT or LibBF. The exponent range is binary64's (about 1e308) and the legacy README says the types do not extend it.
- You need correctly rounded or IEEE-style error-bounded results: the defaults are sloppy add/multiply/divide, the qd.tex paper says the basic routines lack a full correctness proof, and TODO.md still lists 'sane handling of overflow / underflow / NaNs' and wider signed-zero/NaN/Inf oracle coverage as open.
- You need published throughput for this fork: no benchmark of libQD3 itself exists; the only numbers are a circa-2000 QD vs MPFUN table and MPLAPACK's upstream-QD Rgemm at unequal precision, and the new td_real, edd_real, binary32 and branch-free paths are untimed.
- edd_real on MinGW under Wine (EDD trig tests fail per the README) or on targets without binary80 long double/_Float64x, where EDD is not built.
- Low-adoption risk matters: a 2-star single-maintainer fork; upstream BL-highprecision/QD merged the same author's td_real (PR #15) on 2026-09-25, so upstream may be the more conservative pick if you only need DD/TD/QD.

## How it is fast

Each value is an unevaluated sum of non-overlapping hardware floats, and arithmetic is a short fixed sequence of error-free transformations (TwoSum, TwoProd via FMA or Dekker splitting) plus renormalization, all on the stack and inlinable, with no heap-allocated limb arrays or per-operation rounding-mode bookkeeping. The default build trades a few bits for speed: Cray-style sloppy addition, sloppy QD multiplication that computes the O(eps^3) terms in plain double arithmetic and skips the O(eps^4) terms, and sloppy division with fewer quotient corrections. FMA is auto-detected with a residual correctness probe (td.tex: TwoProd costs 2 flops with FMA vs 17 without, about 1.8x fewer flops for TD/QD multiplication), and optional branch-free add/multiply (Kouya and Zhang-Aiken algorithms, QD_ENABLE_BF\*) target SIMD-friendly, branch-predictable dataflow.

## Compared with alternatives

Pick libQD3 over MultiFloats.hpp (dzhang314/MultiprecisionBenchmarks) when you need a full transcendental and complex function set, triple-double, binary80 limbs or C/Fortran bindings rather than peak branch-free SIMD kernel throughput, which that sibling's SC '25 abstract claims at up to 11.7x QD; pick MPLAPACK on top of it when you need LAPACK routines, and MPFR, FLINT or LibBF when you need more than 212 bits.

## Integration

| | |
|---|---|
| **Form** | shared lib (a static library is also built by default; inline arithmetic lives in installed headers) |
| **Dependencies** | none at run time beyond libm (librt for clock_gettime where needed); a Fortran compiler for the optional Fortran modules; MPFR, GMP and MPC only for the optional oracle test suites |
| **Minimum toolchain** | C++11 (cxx_std_11), CMake 3.20; Autotools removed in 1.2.0; the compiler must accept -ffp-contract=off or -fp-model strict or configuration fails |
| **Platforms** | release gates on Linux amd64, macOS arm64 and amd64, Windows MinGW; Debian i386 x87 supported since 1.3.1; edd_real needs binary80 (x86); QD_ARCH can target generic, x86-64-v3 or native |
| **Thread safety** | not documented; qdrand() calls std::rand(), and fpu_fix_start/fpu_fix_end change the calling thread's x87 control word |
| **Drop-in for the baseline** | no |

## Gotchas

- Assigning a double literal gives only double accuracy: write qd_real a = "0.1" (string), not a = 0.1, as the qd.tex manual warns.
- On x87 (32-bit x86 without SSE2 math) call fpu_fix_start() before any DD/TD/QD arithmetic, or 80-bit registers break the error-free transformations; edd_real needs the opposite 80-bit mode (fpu_fix_start_80bit), which 1.3.1 had to separate.
- The library compiles itself with -ffp-contract=off (or -fp-model strict) but does not pass that flag to consumers unless QD_PROPAGATE_FP_CONTRACT_FLAG=ON, although QD_ENABLE_INLINE=ON puts the arithmetic in headers compiled with your flags; build your code without FP contraction or fast-math.
- The docs and build disagree on defaults: td.tex marks accurate QD multiplication as the default, but CMake defaults QD_ENABLE_SLOPPY_MUL=ON. The license files also differ: LICENSE is BSD-3-Clause, COPYING carries the LBNL notice asking commercial users to contact LBNL's Technology Transfer Department, and the td.tex abstract says BSD 2-clause.

## Known shortcomings

- Raised D to C on lineage only: every number covers the inherited upstream QD library, not libQD3 itself (docs/qd.tex QD vs MPFUN on a Pentium II with g++ 2.95.2; the MPLAPACK manual's Rgemm figures of QD 33 vs GMP 19 vs MPFR 11 MFlops, 1.3 GFlops vs 693 vs 390 MFlops with OpenMP). MPFR ran at 512 bits against QD's 212. The manual PDF on master is titled version 1.0.0, not 2.0.1. Fork of BL-highprecision/QD, 2 stars. Kouya's arXiv 1510.08642 and 2603.14926 (QD/TD vs MPFR matmul) were blocked and seen only as snippets.
- td.tex says accurate QD multiplication is the default, but CMake defaults QD_ENABLE_SLOPPY_MUL=ON. License mismatch: LICENSE is BSD-3, COPYING asks for LBNL commercial-use contact, td.tex says BSD 2-clause. -ffp-contract=off is not passed to consumers by default (QD_PROPAGATE_FP_CONTRACT_FLAG OFF) even though the arithmetic is inline in headers, so a consumer's FMA contraction can break the error-free transforms. Upstream BL-highprecision/QD merged td_real (PR #15, 2026-09-25), so the fork's main addition now exists upstream.

## Caveats and trade-offs

Why only C: no measurement of libQD3 itself exists; both number sets cover the QD double-double/quad-double code that libQD3 inherited (the README says the fork 'keeps the original double-double and quad-double functionality'), not its new td_real, edd_real or binary32 types or the optional branch-free paths (CHANGES.1.2.0.md says those follow the Kouya/Zhang-Aiken algorithms; no timings given). The MPLAPACK manual numbers predate libQD3 (upstream QD), compare unequal precisions (quad-double about 212 bits vs MPFR and GMP at 512 bits), run through MPLAPACK's C++ wrappers (in the Raxpy section the author suspects the MPFR C++ binding makes needless copies, since MPFR ran at half of GMP's speed), and are not peer reviewed; the manual opened is titled version 1.0.0 (search results title arXiv 2109.13406 'MPLAPACK version 2.0.1 user manual'; arXiv is blocked here and was not opened). The docs/qd.tex table is from about 2000 (Pentium II, g++ 2.95.2), compares against MPFUN rather than MPFR, and the MPFUN harness is not in the repo; tests/qd_timer.cpp times QD only. docs/td.tex gives flop counts, not timings: TD add 41 flops vs QD 84, TD mul 116/206 (FMA/no FMA) vs QD 182/332, and states FMA gives about 1.8x for multiplication and 1.6x for division (the 2.7x figure is DD's 24/9 ratio, derived from page data). Licensing: LICENSE is BSD-3-Clause; COPYING (LBNL notice) asks commercial users to contact LBNL's Technology Transfer Department, and the td.tex abstract says 'BSD 2-clause', which does not match LICENSE. Related lineage evidence not opened (arXiv blocked): Kouya, arXiv 1510.08642, a table titled 'Computational times of QD and MPFR/GMP (212 bits) matrix multiplication' (equal precision, upstream QD); Kouya, arXiv 2603.14926 (ICCSA 2026 workshops), branch-free TD/QD with SIMD; a search summary says TD 1.2-1.5x and QD 1.4-2.0x 'compared to MPFR' for matrix multiplication, unverified and possibly branch-free vs conventional.

Fixed-precision floating point built from 2 to 4 binary64 limbs (about 106, 159, 212 bits) or two binary80 limbs (EDD): binary64 exponent range, not correctly rounded, not arbitrary precision. Sloppy add, multiply and divide are on by default (a few bits of accuracy traded for speed); optional branch-free arithmetic (QD_ENABLE_BF\*), FMA selection and x86-64-v3 or native code generation. C, C++ and Fortran interfaces. EDD needs binary80 long double (x87), with known MinGW/Wine trigonometry test failures.

## Maintenance

Actively developed (1.5.0 released 2026-09-18, last commit 2026-09-19, 158 commits, no GitHub issues filed) and BSD-3-Clause with an LBNL commercial-use contact notice; copyable, but a 2-star single-maintainer fork whose main consumer is MPLAPACK, and its td_real was merged into upstream BL-highprecision/QD on 2026-09-25.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D to C on lineage. libQD3 has no benchmark of its own, but its repo carries first-party QD timings: docs/qd.tex has the original QD authors' per-operation table against Bailey's MPFUN (CPUs, compilers and flags stated; the QD timer tests/qd_timer.cpp is public, the MPFUN harness is not). The same author's MPLAPACK manual (section 9) has upstream-QD vs MPFR/GMP Rgemm peaks (Ryzen 3970X, GCC 9.3.0, flags unstated, unequal precision). Neither measures libQD3's current code, so the tier cannot go above C.
- **Verifier notes:** Tier raised D to C because libQD3's own docs/qd.tex carries QD vs MPFUN timings and the MPLAPACK manual numbers check out exactly (33/19/11 MFlops, 1.3 GFlops/693/390 MFlops). Every number covers inherited upstream QD code rather than libQD3's current build, so drop it back to D if the catalog wants project-specific measurements only. Metadata checked: BSD-3-Clause, fork of BL-highprecision/QD, last commit 2026-09-19, active.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/nakatamaho/libQD3>
  - <https://github.com/nakatamaho/libQD3/commits>
  - <https://github.com/nakatamaho/libQD3/tree/main>
  - <https://github.com/nakatamaho/libQD3/tree/main/docs>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/README.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/COPYING>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/docs/td.tex>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/docs/qd.tex>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/docs/edd.tex>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/tests/qd_timer.cpp>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/CHANGES.1.2.0.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/CHANGES.1.5.0.md>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/doc/manual/manual.pdf>
  - <https://github.com/nakatamaho/mplapack>
  - <https://github.com/nakatamaho/mplapack/tree/master/benchmark/results>
- **Sources the enricher read:**
  - <https://github.com/nakatamaho/libQD3>
  - <https://github.com/nakatamaho/libQD3/commits>
  - <https://github.com/nakatamaho/libQD3/issues?q=is%3Aissue>
  - <https://github.com/nakatamaho/libQD3/tree/main/cmake>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/README.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/README>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/COPYING>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/NEWS>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/QA.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/CHANGES.1.2.0.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/CHANGES.1.3.0.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/CHANGES.1.4.0.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/CHANGES.1.5.0.md>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/cmake/QD3CheckFMA.cmake>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/cmake/QD3BuildOptions.cmake>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/docs/qd.tex>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/docs/td.tex>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/tests/qd_timer.cpp>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/include/qd/qd_inline.h>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/src/fpu.cpp>
  - <https://raw.githubusercontent.com/nakatamaho/libQD3/HEAD/src/qd_real.cpp>
  - <https://github.com/BL-highprecision/QD/pull/15>
  - <https://github.com/dzhang314/MultiprecisionBenchmarks>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nakatamaho/libqd3`) · [data/wave8/enrich/raw/github_com_nakatamaho_libqd3.json](../../../data/wave8/enrich/raw/github_com_nakatamaho_libqd3.json) (enrichment confidence 0.65)

</details>
