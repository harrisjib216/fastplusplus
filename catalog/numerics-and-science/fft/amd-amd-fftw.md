# AOCL-FFTW (AMD-optimized FFTW)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `GPL-2.0-or-later` · 🟢 active

> AMD's AOCL build of FFTW 3.3.10 with Zen-tuned kernels, copies, transposes and planners; vendor claims beating stock FFTW, no published numbers.

| | |
|---|---|
| **Beats** | FFTW 3.3.10 (upstream MIT/FFTW release it is derived from) |
| **Claimed result** | No numbers on the page. Qualitative claim in README_AMD.md: 'AOCL-FFTW achieves high performance as a result of its various optimizations involving improved SIMD Kernel functions, improved copy functions ..., improved 256-bit kernels selection by Planner and an optional in-place transpose for large problem sizes', a faster in-place MPI transpose, and a new fast planner mode that shortens planning time. |
| **Workload** | General FFTs on AMD EPYC CPUs (Naples, Rome, Milan and later), including in-place MPI FFTs and large in-place transposes; no concrete workload given on the page. |
| **Metric** | throughput |
| **Hardware** | Targeted at AMD EPYC; no benchmark hardware stated |
| **Compiler and flags** | configure --enable-sse2 --enable-avx --enable-avx2 --enable-avx512 --enable-mpi --enable-openmp --enable-shared --enable-amd-opt --enable-amd-mpifft --enable-dynamic-dispatcher (build recipe only, not a benchmark setup) |
| **Adoption** | 64 stars, 23 forks; AMD's official FFT library in AOCL (releases 3.0.1 through 5.3), packaged in Spack (amdfftw, versions up to 5.3) and AUR (fftw-amd) |
| **Last commit** | 2026-05-19 |
| **Links** | [repository](https://github.com/amd/amd-fftw) · [benchmark](https://github.com/amd/amd-fftw/blob/HEAD/README_AMD.md) |

## Verdict

Nothing measured: the README and release notes only list optimisations (SIMD kernels, copy routines, 256-bit kernel selection, MPI transpose, faster planning) with no baseline numbers, compiler setup or hardware. The only figures seen are third-party search snippets (GFFT, ICPP 2023) comparing against AOCL-FFTW rather than measuring AOCL-FFTW against FFTW, and an open user issue says stock FFTW 3.3.10 was faster.

## Use it when

- HPC codes already built on FFTW 3 (Quantum ESPRESSO, VASP-style plane-wave codes) running on AMD EPYC Zen 1-5 nodes, where relinking costs nothing and you can A/B test
- Distributed in-place 3-D FFTs with fftw_mpi on Open MPI, where the AMD MPI transpose (--enable-amd-mpifft, optionally --enable-amd-mpi-vader-limit with btl_vader_eager_limit=65536) targets the transpose step
- Applications that plan the same sizes repeatedly and suffer from FFTW_PATIENT planning time or run-to-run plan variation (fast planner, Top-N planner, app layer with wisdom)
- Sites that standardise on the AOCL stack (Spack amdfftw, AOCC) and want one vendor-supported FFTW build

## Skip it when

- When you need a measured win: no repository page publishes a single number, issue #24 (Aug 2025, open, no AMD reply) reports stock FFTW 3.3.10 built with --enable-float --enable-avx2 --enable-avx512 was faster than this library built as the README says, and issue #19 reports it 'very slow' against MKL FFT on a Genoa machine
- Intel or non-x86 CPUs: --enable-amd-opt only takes effect when configure runs on an AuthenticAMD host, and the kernels and flags target Zen; there is no ARM or POWER work beyond upstream FFTW
- Thread-parallel single-node FFTs where performance matters: a search snippet of the ICPP 2023 GFFT paper (not opened) reports GFFT averaging 9.87x over AOCL-FFTW at 16 threads on EPYC, against 1.18x single-threaded
- Projects that cannot accept GPL-2.0-or-later: the source is GPL like FFTW, and the verifier found Spack linking an AMD EULA for the prebuilt AOCL binaries
- Builds with GCC through CMake with threads: issue #26 (open) shows the default ENABLE_AVX2 build failing because -mavx2 is not added, plus a link-order error

## How it is fast

The README credits improved SIMD kernels, a planner rule that prefers 256-bit AVX2 kernels (kernel/ifftw.h only allows 128-bit AVX2 kernels below size 1024), AVX2 intrinsic versions of the cpy2d and cpy2d_pair copy routines used by rank-0 and buffered plans, and an optional cache-tuned in-place transpose (Toms513-based) for large sizes. MPI FFTs get a block-based in-place transpose that overlaps memcpy with MPI communication. Planning time drops with a hash-table 'fast planner'; the Top-N planner stores the best three plans in wisdom to cut run-to-run variance; the application layer forces FFTW_PATIENT plans but caches them in an in-memory hash and a wisdom file so re-planning is cheap. Release 4.0 added AVX-512 DFT kernels and AVX-512 copy/transpose routines.

## Compared with alternatives

Pick AOCL-FFTW when you must keep the exact FFTW API and MPI/wisdom features on AMD EPYC and want the vendor-supported build; KFR, Admiral or VectorFFT have published single-node wins over FFTW or MKL but require a different API, so use them for new code where speed is measured.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools or CMake); prebuilt AOCL binaries from AMD |
| **Dependencies** | none for the serial library; MPI (Open MPI assumed by the vader options) for MPI FFTs; OpenMP or pthreads for threaded builds |
| **Minimum toolchain** | C compiler with AVX2/FMA; GCC 9+ to get -march=znver2, AOCC 4.0 / Clang 14+ for the dynamic dispatcher (configure errors out on older Clang); MSVC or Clang via CMake on Windows |
| **Platforms** | x86-64 Linux and Windows; AMD optimisations only on AMD Zen (Naples, Rome, Milan, Genoa, Zen 5 via AMD_ARCH=znver1..znver5); dynamic dispatcher is Linux-only (CMake stops with a fatal error on Windows); quad precision not available on Windows |
| **Thread safety** | As upstream FFTW: fftw_execute\* on distinct plans is thread-safe, the planner is not. With --enable-amd-app-opt, planning also reads and writes a global flag and the file wis.dat, so serialise plan creation. The Top-N planner is single-thread only (configure rejects it with threads, OpenMP or MPI). |
| **Drop-in for the baseline** | partial — same FFTW 3 API, symbol names and library names, so it relinks in place; but the AMD code paths compile in only with --enable-amd-opt on an AMD build host, several AMD options are mutually exclusive or restricted (fast planner vs Top-N, app layer not for MPI/r2r/long double/quad/split arrays), and the app layer changes planner behaviour |

## Gotchas

- configure reads /proc/cpuinfo: if it does not run on an AuthenticAMD machine (CI runner, Intel login node) or --enable-debug is set, --enable-amd-opt is silently ignored and you get plain FFTW 3.3.10
- --enable-amd-app-opt overrides the caller's planner flags to FFTW_PATIENT, imports wisdom from ./wis.dat and exports new plans to ./wis.dat in the current working directory, and allocates a scratch copy of the input array during planning
- Do not combine --enable-amd-opt with --enable-generic-simd128/256; the 256-bit-only switch (AMD_OPT_PREFER_256BIT_FPU) is incompatible with wisdom
- Static libraries have had duplicate-symbol problems (issues #22 closed, #27 open, Mar 2026) and a 5.1 shared-library segfault on dlopen from Python (issue #23, closed)

## Known shortcomings

- Tier D: no numbers anywhere reachable; an independent ICPP 2023 paper (GFFT, search snippet) found it only 'comparable' to FFTW on EPYC; kept as AMD's official AOCL build; GPL-2.0-or-later; a vendor fork of the FFTW baseline.
- No numbers anywhere. Open issue #24 (no AMD reply): stock FFTW 3.3.10 with --enable-float --enable-avx2 --enable-avx512 was faster; #19: very slow vs MKL on Genoa. configure enables --enable-amd-opt only on an AuthenticAMD build host and silently ignores it otherwise (also under --enable-debug). App-opt layer forces FFTW_PATIENT and reads/writes ./wis.dat. Open build bugs: GCC+CMake+threads (#26), static-lib duplicate symbols (#27).

## Caveats and trade-offs

Tier D: vendor claim with no numbers on any repository page (README_AMD.md, README, releases). AMD's benchmark pages (amd.com, docs.amd.com), openbenchmarking.org and the AUR page were blocked in this container. Search snippets (not opened) point both ways: an independent ICPP 2023 paper (GFFT, dl.acm.org/doi/10.1145/3605573.3605587) is summarised as finding AOCL-FFTW 'comparable' to FFTW in double-complex runs on EPYC, while another snippet of unknown origin reports about 30% over stock FFTW on a Ryzen 3700X; neither was verified. Code is derived from FFTW 3.3.10, but GitHub shows no 'forked from' parent, so is_fork_of stays null. COPYRIGHT gives GPL-2.0-or-later; GitHub labels it GPL-2.0; Spack lists GPL-2.0-only and links an AMD EULA for AOCL binaries; the NOTICES file also lists BSD-2-Clause notices for some FFTW 3.3.10 files. Recent releases (5.2, 5.3) say 'No major change'. Notable enough for a tier D entry as AMD's vendor build.

Drop-in FFTW 3 API and feature set; GPL; optimised for AMD Zen with extra configure flags and a dynamic dispatcher for portable x86 builds; adds Top-N planner and AMD application optimisation layer.

## Maintenance

Active as AMD's AOCL component (releases 3.0.1 to 5.3; last commit 2026-05-19), but 5.2 and 5.3 say 'No major change', open build issues get no maintainer replies, and the code is GPL-2.0-or-later like FFTW.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** README_AMD.md only describes optimizations (improved SIMD kernels, copy functions, 256-bit kernel selection, in-place MPI transpose, fast planner) with no numbers, and the releases page lists features without figures. AMD's own performance pages and the third-party pages found by search (openbenchmarking.org, AUR, dl.acm.org) are blocked here, so no measurement was seen.
- **Verifier notes:** No numbers anywhere reachable, so tier D stands; kept because it is AMD's official AOCL component (Spack and AUR packages), not rejected as not notable despite 64 stars. Shortcoming worth recording: an independent paper (via search snippet) is summarised as finding no clear gain over FFTW on EPYC. License refined to GPL-2.0-or-later from the COPYRIGHT file. Last commit 2026-05-19 (merge of the 5.3 release branch), active.
- **Fields the verifier corrected:** `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/amd/amd-fftw>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/README_AMD.md>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/README.md>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/COPYING>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/COPYRIGHT>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/NOTICES>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/NEWS>
  - <https://github.com/amd/amd-fftw/commits>
  - <https://github.com/amd/amd-fftw/releases>
  - <https://raw.githubusercontent.com/spack/spack-packages/develop/repos/spack_repo/builtin/packages/amdfftw/package.py>
- **Sources the enricher read:**
  - <https://github.com/amd/amd-fftw>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/README_AMD.md>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/README.md>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/NEWS>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/NOTICES>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/COPYRIGHT>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/api/fftw3.h>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/api/apiplan.c>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/kernel/ifftw.h>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/kernel/planner.c>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/kernel/cpy2d.c>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/kernel/cpy2d-pair.c>
  - <https://raw.githubusercontent.com/amd/amd-fftw/HEAD/kernel/transpose.c>
  - <https://github.com/amd/amd-fftw/releases>
  - <https://github.com/amd/amd-fftw/issues?q=is%3Aissue>
  - <https://github.com/amd/amd-fftw/issues/24>
  - <https://github.com/amd/amd-fftw/issues/19>
  - <https://github.com/amd/amd-fftw/issues/26>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/amd/amd-fftw`) · [data/wave8/enrich/raw/github_com_amd_amd_fftw.json](../../../data/wave8/enrich/raw/github_com_amd_amd_fftw.json) (enrichment confidence 0.7)

</details>
