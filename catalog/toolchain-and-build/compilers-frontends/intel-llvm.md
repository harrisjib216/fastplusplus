# Intel oneAPI DPC++/C++ Compiler (icpx)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compilers and front ends](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Apache-2.0 WITH LLVM-exception (intel/llvm LICENSE.TXT, the open-source base); the benchmarked icpx 2025.3.3 binary and its SVML/libimf runtimes came from the proprietary intel/oneapi-basekit image` · 🟢 active

> Intel's LLVM-based C++ compiler (icpx); under relaxed FP it ran a math-heavy pipeline 1.5-1.8x faster than GCC/Clang.

| | |
|---|---|
| **Beats** | GCC 13.3.0 and Clang 18.1.8 |
| **Claimed result** | icpx-fast finishes the pipeline 1.79x faster than gcc-strict (13700 ms vs 24536 ms total, single-threaded, median of 7 reps). The README text says 1.44x faster than the best non-Intel variant (clang-fast-zmm, 20453 ms), but its own table gives 1.49x (derived from page data); against gcc-fast (21554 ms) it is 1.57x (derived from page data). Under strict IEEE the field compresses to 1.00-1.23x (icpx-strict 19920 ms vs gcc-strict 24536 ms vs clang-strict 22475 ms). Stage detail for icpx-fast vs gcc-strict: SVI fit 2385 ms vs 8879 ms (3.7x) and greeks 770 ms vs 2571 ms (3.3x); on the Newton IV stage gcc-fast is faster (3.07 vs 2.83 Mq/s). |
| **Workload** | Runtime of a single-threaded equity-volatility quant pipeline (parse \~30M option quotes from a 1 GB pcap, Black-Scholes implied-vol Newton inversion, SVI smile fits, greeks) built with GCC, Clang and icpx from identical source in strict-IEEE and fast-math variants. |
| **Metric** | throughput |
| **Hardware** | 4-vCPU KVM guest on a 5th-gen Xeon Scalable (Emerald Rapids, family 6 model 207; hypervisor masks the retail SKU), AVX-512 exposed; shared cloud host, single session |
| **Compiler and flags** | gcc 13.3.0 -O3 -march=native -funroll-loops [-ffast-math]; clang 18.1.8 -O3 -march=native [-ffast-math -fveclib=libmvec]; icpx (IntelLLVM 2025.3.3) -O3 -xHost -fp-model=precise (strict) or -fp-model=fast -fimf-precision=high (fast); zmm variants add -mprefer-vector-width=512 or -qopt-zmm-usage=high |
| **Adoption** | intel/llvm 1.5k stars (open-source base of the oneAPI DPC++ compiler); benchmark repo yzia2000/qr_cpp_compiler 0 stars, 8 commits Aug 1-2 2026 |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/intel/llvm) · [benchmark](https://github.com/yzia2000/qr_cpp_compiler) |

## Verdict

In one 2026 session on a 4-vCPU KVM guest of an Emerald Rapids Xeon, a single-threaded C++20 quant pipeline over 29.9M option quotes (Newton implied vol, LM SVI fits, greeks; median of 7 reps) took 13.7 s built with icpx 2025.3.3 -O3 -xHost -fp-model=fast -fimf-precision=high versus 24.5 s with GCC 13.3.0 -O3 -march=native -funroll-loops (1.79x), 21.6 s with GCC plus -ffast-math (1.57x) and 20.5 s with the best Clang 18.1.8 build (1.49x); with strict IEEE flags icpx led by only 1.23x. Most of the gap sits in the SVI least-squares stage rather than in the SVML-vectorized erf sweeps, and cross-build validation was run on a 299k-quote dev file, not the timed one.

## Use it when

- Single-threaded double-precision kernels on Intel Xeon with AVX-512 where flat loops are dense in erf/exp/log (greeks-style sweeps: 770 ms vs 2571 ms for gcc -O3, 3.3x) and the numerics can be qualified under -fp-model=fast -fimf-precision=high
- Small dense least-squares or normal-equation accumulation loops (5x5 LM fits): the SVI stage was 2.0x faster than gcc-strict even under -fp-model=precise, though equal iteration counts were not verified
- HPC codes that already carry Intel-tuned paths: LAMMPS's INTEL package measured 1.17-3.48x vs GCC 14 on most inputs on a Cascade Lake Xeon Gold 6248 (icpx 2026.1, -xHost -fp-model fast=2), but that GCC baseline ran the same Intel-tuned package, which the issue says is slower under GCC than its OPENMP package for lj and rhodo
- As an extra CI build target to A/B hot kernels against GCC and Clang before committing to one compiler
- When the same toolchain must also compile SYCL device code for Intel GPUs (the open-source DPC++ part)

## Skip it when

- Code that must keep strict IEEE semantics: under strict FP the three compilers were within 1.00-1.23x, and most of icpx's lead needed -fp-model=fast
- Branchy scalar iterative code: gcc -ffast-math beat icpx-fast on the Newton implied-vol stage (3.07 vs 2.83 Mquotes/s), and LAMMPS's lc and dpd inputs showed 0.91x and 1.02x
- AMD or non-x86 hosts: -xHost, SVML and the measured gains are Intel-hardware oriented and nothing here was measured on AMD (see AOCC)
- Projects that need the exact optimizer to be open source or reproducible from source: the measured binary, its SVML/libimf runtimes and its Intel-only flags come from the proprietary oneAPI product, not from intel/llvm
- Expecting wider vectors to help: forcing 512-bit vectors (-qopt-zmm-usage=high) made the pipeline 14.8% slower than icpx's 256-bit default

## How it is fast

The product ships SVML, a vector math library with 4- and 8-wide erf/exp/log (__svml_erf4 and friends) that its vectorizer calls in flat transcendental sweeps, and libimf, faster scalar libm replacements that the benchmark credits for icpx's edge over Clang in the scalar Newton loop; upstream LLVM 18 has no vector erf mapping for libmvec or SVML, so Clang leaves those loops scalar. The largest single saving in the measured pipeline, though, is the Levenberg-Marquardt normal-equations loop (sqrt, divide and FMA into 21 accumulators, no transcendental calls), which icpx ran 2.0x (precise) to 3.7x (fast) faster than gcc -O3; the benchmark does not explain why and did not check that every build ran the same number of LM iterations. -fp-model=fast allows the reassociation that reduction vectorization needs.

## Compared with alternatives

Pick icpx over AOCC when the hosts are Intel Xeons and the hot loops are vectorizable transcendental or reduction math you can run under relaxed FP; AOCC's evidence is an 8% geomean over GCC 11.2 on AMD hardware. zapcc, TinyCC, MIR/c2m and cg_clif target compile time rather than generated-code speed, and MSVC's entry is about Windows build time, so they do not compete on this workload.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (proprietary oneAPI binary; intel/llvm builds an open-source clang++ with SYCL from source or nightly archives) |
| **Dependencies** | product binaries link Intel runtimes (libsvml, libimf) found next to the compiler, plus the system GCC's libstdc++; building intel/llvm needs CMake, Python, Ninja and hwloc &gt;= 2.3 on Linux |
| **Minimum toolchain** | benchmark used icpx (IntelLLVM) 2025.3.3 on C++20 code against Ubuntu's g++ 13 libstdc++; intel/llvm follows upstream LLVM's build requirements |
| **Platforms** | x86-64 Linux and Windows 64-bit (intel/llvm build guide); -xHost targets the build host's Intel ISA; the cited run was only on an Emerald Rapids Xeon guest |
| **Thread safety** | not applicable (compiler); the benchmark was single-threaded by design |
| **Drop-in for the baseline** | partial — GCC/Clang-style driver that links the system libstdc++, but its default floating-point model is fast (relaxed), and the Intel flags used in the benchmark (-xHost, -fp-model=, -fimf-precision=, -qopt-zmm-usage=) do not exist in the open-source intel/llvm driver |

## Gotchas

- Intel's documentation (search snippet; intel.com blocked here) says icx/icpx default to -fp-model fast=1 with math errno disabled, unlike GCC and Clang; a plain compiler swap silently relaxes FP semantics, so pass -fp-model=precise for parity. The strict GCC/Clang builds in the benchmark kept the Linux -fmath-errno default, which by itself can stop sqrt loops from vectorizing, so the 'strict' rows may not be matched on errno semantics.
- Harness flaw: the SVI stage, which supplies 60% of icpx-fast's lead over gcc-strict and 90% of its lead over gcc-fast (derived from page data), has no transcendental calls in its LM hot loop and stops on data-dependent tests (relative SSE gain below 1e-12, lambda above 1e8, or 50 iterations). validate.py compares only the five fitted parameters (max drift up to 1.7e-8) and never the per-slice iteration count the bindings export, so equal work across builds is not shown, and the README's attribution of the win to SVML misreads its own stage table. The timed SVI region also includes a 30M-quote bucketing pass with exp, log and push_back.
- The README's reason that GCC stays scalar ('glibc's libmvec has no vector erf') is wrong for GCC: glibc 2.39's math-vector.h declares a SIMD erf for GCC 6+ under __FAST_MATH__, yet gcc-fast emitted no _ZGV calls, so the GCC fast-math baseline failed to vectorize for an unexplained reason. For Clang 18 the limit is real (LLVM 18's libmvec table has no erf). Only GCC got -funroll-loops.
- The open-source intel/llvm driver (Options.td) has -ffp-model=, -ffp-accuracy=, -fveclib=SVML and -faltmathlib=SVMLAltMathLibrary but none of -xHost, -fp-model=, -fimf-precision= or -qopt-zmm-usage=, so the benchmarked build cannot be reproduced from the repo this entry links.

## Known shortcomings

- Tier A on the yzia2000/qr_cpp_compiler table, but it is a 0-star, AI co-authored repo with a single run on a cloud VM whose SKU is masked. The README's '1.44x vs best non-Intel' is an arithmetic slip (table gives 1.49x). The win comes from proprietary SVML/libimf; the README claim that libmvec has no vector erf is wrong (glibc math-vector.h declares it), so the gcc/clang fast-math baselines may be under-tuned. Validation ran on the 298,720-quote dev file, not the timed file. Licence Apache-2.0 WITH LLVM-exception.
- Enricher: the SVI stage accounts for 60% of the icpx-fast lead over gcc-strict and 90% over gcc-fast (derived from page data), yet its Levenberg-Marquardt hot loop has no transcendental calls, so the README credits SVML wrongly; the LM exit is data-dependent (1e-12 relative SSE, lambda above 1e8, 50 iterations) and validate.py checks 5 parameters only and never the iteration count, so equal work is not shown; the timed SVI region also includes bucketing 30M quotes with exp/log/push_back. glibc 2.39 math-vector.h declares SIMD erf for GCC, so the README's reason for gcc staying scalar is wrong and the gcc-fast vectorization failure is unexplained (the LLVM 18 libmvec table has no erf, so the Clang limit is real). Intel's default fp-model fast=1 with errno off against strict gcc/clang keeping -fmath-errno. The benchmark flags -xHost, -fp-model=, -fimf-precision and -qopt-zmm-usage are absent from the open intel/llvm Options.td, so the run is not reproducible from the linked repo. LAMMPS #5213's GCC baseline ran the Intel-tuned package.

## Caveats and trade-offs

Benchmark is a small personal repo (0 stars, 0 forks, no LICENSE file, 8 commits on 2026-08-01/02, all co-authored by 'claude', i.e. AI-assisted) on a transcendental-heavy workload chosen to favour SVML; one session on a shared 4-vCPU cloud VM, so numbers are relative; CPU SKU is masked (only family 6 model 207, Emerald Rapids), so tier A is borderline. The README's headline '1.44x faster than the best non-Intel variant' is an arithmetic slip; its own table gives 1.49x. Most of the gain comes from Intel's proprietary math runtimes (SVML vector erf/exp/log in the SVI and greeks sweeps, and libimf's faster scalar erf/exp in the IV loop per the README appendix), which are not part of the open-source intel/llvm repo that repo_url points at. The README and src/implied_vol.cpp say glibc's libmvec has no vector erf, but current glibc's sysdeps/x86/fpu/bits/math-vector.h declares __DECL_SIMD_erf for x86_64 under __FAST_MATH__, so the stated reason the gcc/clang fast-math builds stay scalar is doubtful and those baselines may be under-tuned (clang's -fveclib=libmvec mapping may also lack erf). Only gcc gets -funroll-loops. Cross-compiler validation (results/validation.md: all nine builds agree to about 2e-14 vol points) was run on quotes_dev.pcap (298,720 quotes), not the 29.9M-quote timed file. The README notes gcc-fast beats icpx-fast on the Newton IV stage (3.07 vs 2.83 Mq/s), strict-IEEE advantage is only 1.23x, and forcing 512-bit vectors made icpx 14.8% slower. Corroboration, opened: LAMMPS issue #5213 (akohlmey, 2026-09-25, 2x20-core Xeon Gold 6248 Cascade Lake, RHEL 10; icpx 2026.1 -xHost -fp-model fast=2 relative to GCC 14 '-sf intel') reports icpx at lj 1.70, rhodo 1.62, eam 1.17, sw 1.85, water 1.88, airebo 1.85, tersoff 1.49, snap 3.48, but lc 0.91 and dpd 1.02, so it is not uniformly faster. Counter-evidence, opened by the search agent: gist kaityo256/d41481467df504c5039715d38954ab8a shows GCC 40-60x faster than ICC 18-19.1 on a degenerate std::uniform_real_distribution loop. Search-snippet only: SPEC withdrew over 2,000 SPEC CPU 2017 results that used a benchmark-specific oneAPI DPC++ optimization. The listed 'Intel C++ Compiler' is the proprietary product; intel/llvm's README says it is a technical foundation for the oneAPI DPC++ Compiler and that feature parity with downstream products is not guaranteed. [retier] Single run on a masked cloud VM by a 0-star, AI co-authored repo. SVI stage (60-90% of the lead, derived from page data) has no transcendental calls, so the SVML explanation is wrong; its LM solver exits on data-dependent criteria and validate.py never compares iteration counts; the timed region includes 30M-quote bucketing. glibc 2.39 declares SIMD erf, so the gcc-stays-scalar explanation is wrong. icpx defaults to fp-model fast=1 with errno off; the benchmark's icpx flags are not in the open Options.td. Table ratio 1.49x, not the README's 1.44x. Apache-2.0 WITH LLVM-exception for the open repo; the measured icpx binary is proprietary.

Most of the gain needs -fp-model=fast (relaxed floating point) and Intel's SVML/libimf vector math; Intel hardware oriented (-xHost); closed-source optimizer components in the shipped product; proprietary terms for the shipped binary.

## Maintenance

intel/llvm is active (1.5k stars, daily DPC++ nightly releases, latest 2026-10-06) and Apache-2.0 WITH LLVM-exception, but the measured icpx binary, its SVML/libimf runtimes and its Intel-only flags belong to the proprietary oneAPI product, so usability is mixed: usable as a free-standing compiler, not reproducible or forkable from this repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now C.
- **Tier reason:** The yzia2000/qr_cpp_compiler README results table times GCC 13.3.0, Clang 18.1.8 and IntelLLVM 2025.3.3 on identical source; the benchmark code is public (src/implied_vol.cpp, src/svi_fit.cpp, src/greeks.cpp, python/bench.py, CMakeLists.txt with per-compiler flags, CMakePresets.json Release presets) and the CPU is named as an Emerald Rapids 5th-gen Xeon Scalable (family 6 model 207) KVM guest. Tier A holds on the precedent that a VM CPU model string without a retail SKU still counts, with that weakness kept in caveats.
- **Retiered** A to C: The yzia2000/qr_cpp_compiler run is a single cloud-VM run with a masked SKU, and its icpx flags (-xHost, -fp-model=, -fimf-precision, -qopt-zmm-usage) and the proprietary SVML/libimf runtime are absent from the open intel/llvm repo, so the result is not reproducible from public sources (flags-absent-from-public-sources precedent); the dominant SVI stage has a data-dependent iteration count that the validation never checks.
- **Verifier notes:** Every table number in the record matches the README; only the '1.44x vs best non-Intel' headline is wrong on the page itself (table gives 1.49x), now corrected. Metadata checked: intel/llvm 1.5k stars, 863 forks, not a fork, not archived, last commit 2026-10-06 on the sycl branch; license refined to Apache-2.0 WITH LLVM-exception. Shortcomings to record: AI-assisted 0-star single-session cloud-VM benchmark with masked SKU, proprietary SVML/libimf carry the win, gcc/clang fast-math baselines possibly under-tuned (libmvec does declare vector erf), validation on a smaller dev file.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 2); enricher (wave 2)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/README.md>
  - <https://github.com/yzia2000/qr_cpp_compiler>
  - <https://github.com/yzia2000/qr_cpp_compiler/commits>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/results/validation.md>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/src/implied_vol.cpp>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/python/bench.py>
  - <https://github.com/intel/llvm>
  - <https://github.com/intel/llvm/commits>
  - <https://raw.githubusercontent.com/intel/llvm/sycl/LICENSE.TXT>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/x86/fpu/bits/math-vector.h>
  - <https://github.com/lammps/lammps/issues/5213>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/results/validation.md>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/src/implied_vol.cpp>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/src/svi_fit.cpp>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/src/greeks.cpp>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/include/qr/black_scholes.hpp>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/include/qr/svi.hpp>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/python/bench.py>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/python/bench_worker.py>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/python/validate.py>
  - <https://raw.githubusercontent.com/yzia2000/qr_cpp_compiler/HEAD/python/bindings.cpp>
  - <https://github.com/intel/llvm>
  - <https://github.com/intel/llvm/releases>
  - <https://github.com/intel/llvm/issues?q=is%3Aissue+slower+than+gcc>
  - <https://raw.githubusercontent.com/intel/llvm/sycl/README.md>
  - <https://raw.githubusercontent.com/intel/llvm/sycl/LICENSE.TXT>
  - <https://raw.githubusercontent.com/intel/llvm/sycl/sycl/doc/GetStartedGuide.md>
  - <https://raw.githubusercontent.com/intel/llvm/sycl/clang/include/clang/Options/Options.td>
  - <https://raw.githubusercontent.com/llvm/llvm-project/release/18.x/llvm/include/llvm/Analysis/VecFuncs.def>
  - <https://raw.githubusercontent.com/bminor/glibc/release/2.39/master/sysdeps/x86/fpu/bits/math-vector.h>
  - <https://github.com/lammps/lammps/issues/5213>
  - WebSearch snippet: Intel oneAPI DPC++/C++ Compiler Developer Guide, Floating-Point Optimizations (intel.com, blocked; default -fp-model fast=1, -fno-math-errno)
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/intel/llvm`) · [data/wave2/enrich/raw/github_com_intel_llvm.json](../../../data/wave2/enrich/raw/github_com_intel_llvm.json) (enrichment confidence 0.65)

</details>
