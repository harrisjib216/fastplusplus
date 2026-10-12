# AMD C++ Compiler (AOCC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compilers and front ends](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Proprietary AMD EULA, binary-only (the Spack recipe declares LicenseRef-AMD-Proprietary, redistribute(source=False, binary=False) and needs +license-agreed)` · 🟢 active

> AMD's closed-source LLVM/Clang-based C/C++/Fortran compiler for Zen whose binaries ran about 8% faster than GCC 11.2's.

| | |
|---|---|
| **Beats** | GCC 11.2 (also compared with LLVM Clang 14.0) |
| **Claimed result** | AOCC 3.2 about 8% faster than GCC 11.2 built binaries (geometric mean over 56 C/C++ benchmarks); AOCC was fastest in 66% of the tests, GCC 11.2 in 19.6% and LLVM Clang 14.0 in 14%. Clang 14.0 was about 2% faster than GCC 11.2 by the same geometric mean. |
| **Workload** | Run time of binaries built by each compiler for 56 C/C++ Phoronix Test Suite benchmarks on a dual-socket AMD EPYC 7773X Milan-X server running Ubuntu 22.04. |
| **Metric** | throughput |
| **Hardware** | 2P AMD EPYC 7773X (Milan-X, Zen 3, 1.5 GB L3 in total, 128 cores / 256 threads), Ubuntu 22.04 LTS |
| **Compiler and flags** | AOCC 3.2 (based on upstream LLVM/Clang 13.0) vs GCC 11.2 and LLVM Clang 14.0, the Ubuntu 22.04 LTS default packages; CFLAGS and CXXFLAGS '-O3 -march=native -flto' for all three (per search snippets of the article, page not opened) |
| **Adoption** | AMD's vendor C/C++/Fortran compiler for Zen CPUs, free to download under the EULA; packaged in Spack by AMD's amd-toolchain-support account (versions 3.2.0 to 5.2.0, 5.2.0 added 2026-05-29); search results show HPC-center docs (Purdue RCAC) and a Gentoo wiki page |
| **Links** | [repository](https://www.amd.com/en/developer/aocc.html) · [benchmark](https://www.phoronix.com/review/amd-aocc-milanx/6) |

## Verdict

Phoronix built 56 C/C++ Phoronix Test Suite programs with AOCC 3.2 (LLVM 13 base), Ubuntu 22.04's GCC 11.2 and Clang 14.0, all at -O3 -march=native -flto, on a 2P EPYC 7773X Milan-X server; AOCC binaries were about 8% faster than GCC's by geometric mean and fastest in 66% of tests, Clang 14 about 2% (so AOCC roughly 6% over Clang 14, derived from page data). These figures come from search snippets because phoronix.com and the OpenBenchmarking result 2204117-NE-EPYC7773X86 are blocked here; later Phoronix runs report AOCC 4.0 about 17% over GCC 12.2 on 4th Gen EPYC (68 tests, GCC 12 lacked znver4 tuning) and about 4% on Zen 4 Ryzen, and AOCC 5.0 on Zen 5 often close to upstream Clang.

## Use it when

- Compute-bound C, C++ or Fortran (HPC kernels, codecs, simulation) deployed on AMD EPYC or Ryzen Zen machines that you can rebuild per target; SVT-AV1 showed the largest AOCC 5.0 gains on Zen 5
- Codebases that already build cleanly with Clang, where a few percent more throughput without source changes is worth a per-workload benchmark (GCC or Clang still won about a third of the 56 Milan-X tests)
- HPC sites with Spack or EasyBuild that can install the EULA tarball (spack install aocc +license-agreed, EasyBuild accept_eula) and expose it as a module
- Fortran or mixed codes such as WRF that ship an AOCC configure stanza with AMD-tuned flags and AMDLIBM
- A new Zen generation before upstream compilers carry its tuning: AOCC 4.0 beat GCC 12.2, which lacked znver4 tuning, by about 17% geomean on 4th Gen EPYC

## Skip it when

- You need the source, redistribution or distro packaging: binary-only AMD EULA, Spack declares redistribute(source=False, binary=False) and LicenseRef-AMD-Proprietary
- Targets other than x86 Linux (Windows, macOS, aarch64, RISC-V): AOCC targets 32- and 64-bit Linux x86 only
- Code that needs C++ language or library support newer than Clang 17: AOCC 5.0, 5.1 and 5.2 all stay on LLVM 17.0.6 (Nov 2023)
- Intel CPUs or mixed fleets: tuning targets Zen and no published gains exist elsewhere (EasyBuild's AOCC 5.1 test only shows it installs on an Intel i7-1260P)
- Workloads where upstream Clang already matches it (Phoronix's AOCC 5.0 run on 2P EPYC 9755 found minimal differences from upstream LLVM/Clang in many tests), or when the goal is faster compilation rather than faster binaries

## How it is fast

Upstream LLVM -O3 plus AMD passes tuned with Zen cost models: whole-program structure peeling and pointer/integer field compression under -flto (-fstruct-layout=1..7, per a search snippet of the AOCC user guide), extra loop transformations exposed as -mllvm switches (-enable-loop-reversal, -enable-gather, -vectorize-non-contiguous-memory-aggressively), aggressive inlining (-finline-aggressive), and, per Phoronix's AOCC 5.0 coverage, improved SLP/loop vectorization, LICM and control/data-flow optimizations plus Zen 5 tuning. Vectorized math calls can be routed to AMD's AOCL-LibM with -fveclib=AMDLIBM (5.2 bundles a Zen 5-tuned AOCL-LibM 5.3). Which of these passes run at plain -O3 -march=native -flto, the setting Phoronix measured, is not documented in anything readable here.

## Compared with alternatives

The catalogued siblings (zapcc, TinyCC, MIR/c2m, cg_clif) make compilation faster; AOCC is the only one aimed at the run time of the generated code, so pick it when binary throughput on AMD Zen matters and build time does not (c2m's code runs at about 92% of gcc -O2, while AOCC's ran about 8% faster than GCC 11.2 at -O3 in Phoronix's Milan-X test).

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (prebuilt binary tarball: clang, clang++, flang, lld, LLVM tools, libomp) |
| **Dependencies** | A GCC installation for libstdc++ headers and runtime (and libquadmath for flang); libxml2, zlib, ncurses, libtool per the Spack recipe; binutils, ncurses, zlib, libxml2, libffi per the EasyBuild 5.1.0 easyconfig |
| **Minimum toolchain** | Linux x86-64; EasyBuild pairs AOCC 3.2 with GCCcore 11.2/11.3 and AOCC 5.1 with GCCcore 15.2; C++ language level is that of the pinned Clang (17 for AOCC 5.x) |
| **Platforms** | x86-64 Linux only, tuned for AMD Zen 1 to Zen 5; installs and runs on Intel x86-64 but no gains shown there |
| **Thread safety** | Not applicable (compiler); OpenMP programs use the bundled LLVM libomp |
| **Drop-in for the baseline** | partial: a clang-compatible driver that can replace gcc/g++ through CC/CXX and compiles C++ against GCC's libstdc++, so objects link with GCC-built libraries; but it is binary-only, x86-64 Linux only, does not accept every GCC-only flag or extension, and AMD-specific -mllvm flags tie build files to AOCC |

## Gotchas

- GCC selection is silent: AOCC's clang picks whatever GCC install it finds for headers and libstdc++ unless told; Spack writes clang.cfg with --gcc-toolchain and EasyBuild writes --gcc-install-dir cfg files (5.0+) or wrapper scripts (before 5.0) and sanity-checks the 'Selected GCC installation' line. Its binaries are named clang, clang++, flang and lld like upstream LLVM, so PATH order decides which compiler a build gets; Spack issue #49543 reports 'spack compiler find' producing an unusable entry for AOCC 4.2/5.0 until cc was pointed at clang-16/clang-17.
- Optimizer bug history: OpenBLAS PR #2665 (2020) traced complex and double-complex lapack-test failures to AOCC flang over-optimization; OpenBLAS's Makefile.system still adds -fno-unroll-loops whenever flang --version reports AMD on Linux x86-64, for every AOCC version.
- The best results lean on AMD-only knobs: WRF's AOCC stanza uses -fveclib=AMDLIBM, -finline-aggressive and linker-passed -mllvm -enable-loop-reversal/-enable-gather/-vectorize-non-contiguous-memory-aggressively at -Ofast -ffast-math (which changes floating-point semantics), and says optimized flags must be requested from AMD toolchain support; -fstruct-layout acts only under -flto. Of these, only -fveclib=AMDLIBM reached upstream (Clang 19; absent in 18).
- Version lag: each release pins one LLVM base (3.2 on 13.0, 4.0 on 14.0.6, 4.1/4.2 on 16.0.3, 5.0 to 5.2 on 17.0.6), so upstream LLVM fixes, diagnostics and C++ features after 17 are missing, and the Milan-X comparison pitted an LLVM 13-based AOCC against a newer Clang 14.

## Known shortcomings

- Binary-only vendor compiler (AMD EULA, has_code false, reference entry like CKTSO, HYLU and UDisk): evidence is Phoronix search snippets only (phoronix.com, openbenchmarking.org and amd.com blocked), a small gain of about 8% geomean over GCC 11.2 across 56 tests on a 2P EPYC 7773X (-O3 -march=native -flto, 2022 compilers; a second article puts AOCC 4.0 about 4% over GCC 12.2 on a Ryzen 9 7950X). Retier to B or A possible once Phoronix is reachable.
- Phoronix and OpenBenchmarking pages, amd.com and docs.amd.com all blocked, so the 8% geomean rests on search snippets only (confidence 0.6). The AOCC 4.0 Genoa 17% geomean (68 tests) is against GCC 12.2 without znver4 tuning, a handicapped baseline; AOCC 5.0 often matches upstream Clang on Zen 5; AOCC 3.2 was roughly 6% over Clang 14 (derived from page data). Upstream Clang 19 gained -fveclib=AMDLIBM, so part of AOCC's math edge is upstream now. Binary-only EULA; each release pinned to one LLVM base (3.2 Clang 13.0, 4.0 14.0.6, 4.1/4.2 16.0.3, 5.0-5.2 17.0.6 per the EasyBuild easyblock); silent GCC/libstdc++ selection (needs clang.cfg); OpenBLAS Makefile.system still adds -fno-unroll-loops for AMD flang (PR #2665, lapack-test complex failures); best flags are AMD-only. Retier waits on Phoronix/OpenBenchmarking access.

## Caveats and trade-offs

Snippet only: phoronix.com, openbenchmarking.org and amd.com are EGRESS_BLOCKED here, so the 8% geomean, the 66%/19.6%/14% win shares, the flags and the CPU come from two WebSearch summaries of the Phoronix article, not from the opened page; the per-test results (OpenBenchmarking 2204117-NE-EPYC7773X86) were not seen. Single 2022 run on one dual-socket Zen 3 server; AOCC 3.2 is based on LLVM 13.0, older than the Clang 14.0 it beat, and both GCC 11.2 and Clang 14 are now several releases old. The gain is modest (about 8% geomean, with GCC or Clang fastest in about a third of the tests) and tuned for AMD Zen; with -march=native the comparison includes each compiler's znver3 tuning. A later Phoronix article (AOCC 4.0, Ryzen 9 7950X, 190 tests, snippet only) reports about 4% geomean over GCC 12.2 with AOCC first in about 55% of tests; the AOCC 5.0 article on 2P EPYC 9755 (Zen 5, LLVM 17.0.6 base) shows clear wins in some workloads and minimal differences from upstream Clang in others, with no geomean visible in snippets. Binary-only under an AMD EULA: no source for AMD's LLVM changes, cannot be redistributed or packaged by distributions, x86-64 Linux only.

Binary-only download under an AMD EULA, no public source for AMD's changes, so it cannot be copied or packaged; x86-64 Linux only; tuned for AMD Zen, gains elsewhere not shown; lags upstream LLVM (AOCC 5.0 is based on LLVM 17.0.6).

## Maintenance

Actively released (Spack and EasyBuild carry 3.2.0 to 5.2.0, 5.2.0 added to Spack 2026-05-29, all 5.x on LLVM 17.0.6) but binary-only under an AMD EULA, so it is a reference entry that can be installed and used but not copied, patched or redistributed; the numbers are snippet-only and a retier waits on phoronix.com or openbenchmarking.org access.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** Phoronix is an independent third party and two WebSearch snippets of https://www.phoronix.com/review/amd-aocc-milanx/6 agree on every figure in the record: 56 C/C++ tests, AOCC 3.2 fastest 66% vs GCC 11.2 19.6% and Clang 14.0 14%, geomean about 8% over GCC 11.2 and Clang about 2% over GCC, flags '-O3 -march=native -flto', 2P EPYC 7773X, Ubuntu 22.04 LTS. The page, the OpenBenchmarking result 2204117-NE-EPYC7773X86 and amd.com were all EGRESS_BLOCKED, so this is snippet-only verification and stays at C; it would qualify for B, or A from the public Phoronix Test Suite profiles plus stated compilers, flags and CPU, once the article or the result file is opened.
- **Verifier notes:** Keep as a reference entry: AOCC is a widely deployed, actively released vendor compiler (5.1.0 added to Spack 2026-01-09, 5.2.0 on 2026-05-29) with independent third-party numbers against GCC across two Phoronix articles, and the catalog already keeps binary-only references (CKTSO, HYLU, UDisk); usability reference and has_code false are correct. No public repository exists, so last_commit stays null and maintenance_status 'active' rests on the release cadence seen in the Spack recipe history. Queue a retier for when phoronix.com or openbenchmarking.org is reachable (likely B, possibly A); fetch attempts to phoronix.com/review/amd-aocc-milanx/6, www.amd.com/en/developer/aocc.html and openbenchmarking.org returned EGRESS_BLOCKED.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `license`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** Phoronix snippets (verifier); enricher (wave 2)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/spack/spack-packages/develop/repos/spack_repo/builtin/packages/aocc/package.py>
  - <https://github.com/spack/spack-packages/commits/develop/repos/spack_repo/builtin/packages/aocc/package.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/spack/spack-packages/develop/repos/spack_repo/builtin/packages/aocc/package.py>
  - <https://github.com/spack/spack/issues?q=aocc+is%3Aissue>
  - <https://github.com/spack/spack/issues/49543>
  - <https://github.com/llvm/llvm-project/issues?q=aocc>
  - <https://raw.githubusercontent.com/easybuilders/easybuild-easyblocks/develop/easybuild/easyblocks/a/aocc.py>
  - <https://github.com/easybuilders/easybuild-easyconfigs/tree/develop/easybuild/easyconfigs/a/AOCC>
  - <https://raw.githubusercontent.com/easybuilders/easybuild-easyconfigs/develop/easybuild/easyconfigs/a/AOCC/AOCC-5.1.0-GCCcore-15.2.0.eb>
  - <https://github.com/easybuilders/easybuild-easyconfigs/issues?q=AOCC>
  - <https://github.com/easybuilders/easybuild-easyconfigs/pull/25050>
  - <https://raw.githubusercontent.com/wrf-model/WRF/master/arch/configure.defaults>
  - <https://github.com/OpenMathLib/OpenBLAS/issues?q=aocc>
  - <https://github.com/OpenMathLib/OpenBLAS/pull/2665>
  - <https://raw.githubusercontent.com/OpenMathLib/OpenBLAS/develop/Makefile.system>
  - <https://raw.githubusercontent.com/llvm/llvm-project/release/17.x/clang/include/clang/Driver/Options.td>
  - <https://raw.githubusercontent.com/llvm/llvm-project/release/18.x/clang/include/clang/Driver/Options.td>
  - <https://raw.githubusercontent.com/llvm/llvm-project/release/19.x/clang/include/clang/Driver/Options.td>
  - <https://github.com/orgs/amd/repositories?q=aocc>
  - <https://github.com/amd/aocl-libm-ose>
  - <https://raw.githubusercontent.com/amd/aocl-libm-ose/master/LICENSE>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://amd.com/en/developer/aocc.html`) · [data/wave2/enrich/raw/amd_com_en_developer_aocc_html.json](../../../data/wave2/enrich/raw/amd_com_en_developer_aocc_html.json) (enrichment confidence 0.6)

</details>
