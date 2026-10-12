# wjr (WJR big integer and utility library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `LGPL-2.1` · 🟢 active

> x64-tuned C++17 big-integer library with GMP-style mpn kernels, Toom-Cook and FFT multiplication; has a GMP harness but publishes no numbers.

| | |
|---|---|
| **Beats** | GMP (mpn_\* low-level functions in the repo's own benchmark) |
| **Claimed result** | No numbers found: the README (Chinese), docs/modules/README.md, issues (none open) and the PR pages (#13, #20) contain no speedup versus GMP. CI (benchmarks.yml, weekly) uploads benchmark-results.json artifacts and a regression summary versus the previous run, not versus GMP, and runs without GMP in the default core profile. |
| **Workload** | Google Benchmark micro-benchmarks in benchmarks/src/biginteger.cpp: wjr addc_1, addc_n, subc_1, subc_n, mul_1, addmul_1, submul_1, addlsh_n, rsblsh_n, mul, sqr, div_qr and biginteger to/from chars against the GMP mpn_add_1, mpn_add_n, mpn_sub_n, mpn_mul_1, mpn_addmul_1, mpn_submul_1, mpn_lshift/rshift counterparts (built with WJR_USE_GMP); no results published. |
| **Metric** | throughput |
| **Hardware** | CI uses ubuntu-24.04 GitHub-hosted runners; no CPU model stated |
| **Compiler and flags** | CMake Release with -march=native for non-MSVC (CMakeLists.txt); compiler not stated; optional NASM assembly modules for x64 |
| **Adoption** | 7 stars, 1 fork; 1,150 commits, single maintainer |
| **Last commit** | 2026-08-27 |
| **Links** | [repository](https://github.com/wjr-z/wjr) |

## Verdict

Nothing was measured publicly: benchmarks/src/biginteger.cpp pairs wjr_\* and gmp_\* Google Benchmark cases (mpn_add_n, mpn_mul, mpn_tdiv_qr, mpn_get_str and others) at 4 to 1024 limbs, built Release with -march=native, but no result files, tables or CPU models are published and the weekly CI on ubuntu-24.04 runners builds without GMP by default.

## Use it when

- You want a GMP-style integer class in C++17 on x86-64 without linking libgmp, and are willing to benchmark it yourself first.
- Operand sizes of a few to roughly a thousand 64-bit limbs, which is the range the repository's own benchmark sweeps (4 to 256 limbs for most kernels, up to 1024 for mul_n and sqr).
- Code that already uses WJR's JSON or string modules, where the big-integer type comes for free.
- Studying a modern C++ restructuring of GMP's mpn algorithms (Toom, FFT, division, radix conversion).

## Skip it when

- You need evidence: there are no published results against GMP anywhere in the README, docs, issues or CI summaries; the CI benchmark only compares to its own previous run.
- Non-x64 targets or AMD-specific tuning: the README says most optimizations are x64-only and AMD has not been tested or tuned.
- Code that relies on exceptions: the README says exception handling is poorly supported.
- Shared-library builds: the README TODO list says unique_stack_allocator under a dynamic library still needs fixing.
- You need gcd, integer square root, rationals or floats: none of these appear in the biginteger header (GMP, FLINT or Boost.Multiprecision cover them).

## How it is fast

Small and medium sizes use hand-tuned x64 kernels (optional NASM assembly modules, intrinsics guarded by WJR_HAS_\* macros) for carry-propagating add/sub and multiply-accumulate. Larger products switch through Toom-2 to Toom-5 thresholds (toom22 to toom55, plus unbalanced toom32/42/43/53/63) and then to a Schönhage-Strassen FFT with mulmod_bnm1 and mulmod_bknp1 wrapping, whose sources keep GMP's mpn_mul_fft structure, comments and macro names through a gmp-helper.hpp shim. Temporary limbs come from a stack allocator (unique_stack_allocator) instead of malloc.

## Compared with alternatives

Pick wjr over Boost.Multiprecision cpp_int or libzahl only if you need GMP-scale algorithms (Toom-Cook, FFT) in a C++ class without libgmp and can verify speed yourself; mp++ or FLINT are the safer choices when linking GMP is acceptable and you want measured, maintained speedups.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | fmt (git submodule in third-party/); optional NASM for x64 assembly; GMP only for the comparison benchmarks and tests |
| **Minimum toolchain** | C++17, 64-bit, CMake; CI tests Clang 17-20, GCC 9 and 11-14 on Linux and MSVC/Clang on Windows |
| **Platforms** | x86-64 Linux and Windows (main optimizations); other 64-bit targets via generic fallbacks |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the class method names mirror mpz (addmul, tdiv_qr, powmod, ...) but it is a C++ class, not the mpz_t/mpn C API |

## Gotchas

- The top-level CMakeLists.txt adds -march=native for every GCC/Clang build, so binaries built this way are tied to the build machine's CPU.
- C++20 is disabled by default (WJR_DISABLE_CXX_20=ON); -DWJR_DISABLE_EXCEPTIONS=ON compiles with -fno-exceptions.
- License provenance: the FFT and mulmod files (src/biginteger/detail/fft.cpp, mulmod_bknp1.cpp) carry GMP's comments and macros but only a 2025 wjr copyright header, while the repository is LGPL-2.1; GMP itself is LGPLv3+/GPLv2+, so check provenance before redistributing.
- To get GMP numbers you must configure with -DWJR_BUILD_BENCHMARKS=ON, -DWJR_BENCHMARK_PROFILE=all and libgmp installed; the CI 'all' profile runs 1 repetition at 0.03 s minimum time.

## Known shortcomings

- Verifier rejected as not notable at tier D: 7 stars and no published numbers against any baseline.
- Still no numbers vs GMP. CMake forces -march=native. FFT/mulmod sources keep GMP comments and macros but carry only a wjr 2025 header under LGPL-2.1 while GMP is LGPLv3+/GPLv2+, so licence provenance is a risk. README TODO: unique_stack_allocator broken in shared-library builds.

## Caveats and trade-offs

Evidence-free record: the harness exists (benchmarks/src/biginteger.cpp has wjr_, fallback_ and gmp_ prefixed cases and benchmarks/tools/compare.py plots wjr vs fallback vs gmp from Google Benchmark JSON) but no numbers are published anywhere I could open (README, docs, issues, PR descriptions, workflow runs page showing only durations; wjr-z.github.io coverage page is blocked). The default CI profile builds without GMP, and the 'all' profile with GMP uses 1 repetition and 0.03 s min time (benchmarks.yml), so CI is a regression tracker, not a GMP shootout. Tier D kept per the seed-pass rule although the repo has fewer than 1k stars. A reader must build with -DWJR_BUILD_BENCHMARKS=ON -DWJR_BENCHMARK_PROFILE=all and libgmp to get numbers.

C++17, 64-bit only, most optimizations x64-only, AMD not tuned (TODO list), exception handling poorly supported, JSON wrapper not zero-overhead. LGPL-2.1. Bundles biginteger, json, string, ring_buffer and other modules; README is in Chinese.

## Maintenance

Actively developed (last commit 2026-08-27, 1,150 commits) by one maintainer with 7 stars and no issues filed; LGPL-2.1, so it is usable via dynamic or relinkable linking, but treat it as unproven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now D.
- **Tier reason:** No number anywhere: README and benchmarks/ (src, tools, CMakeLists.txt) publish no results; .github/workflows/benchmarks.yml only uploads CI artifacts and a step summary versus the previous run, and builds GMP comparisons only in the manually triggered 'all' profile (1 repetition, 0.03 s min time).
- **Verifier notes:** Tier D with 7 stars, 1 fork and a single maintainer, no outside references found: not notable under the tier-D rule (precedent: cxx-ziggurat, batch-05). Metadata confirmed: LGPL-2.1, 1,150 commits, last commit 2026-08-27. If the orchestrator keeps it as a flagged lead, the shortcoming is 'harness vs GMP mpn_\* exists, no published numbers'.
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/wjr-z/wjr>
  - <https://github.com/wjr-z/wjr/commits>
  - <https://github.com/wjr-z/wjr/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/.github/workflows/benchmarks.yml>
- **Sources the enricher read:**
  - <https://github.com/wjr-z/wjr>
  - <https://github.com/wjr-z/wjr/issues?q=is%3Aissue>
  - <https://github.com/wjr-z/wjr/tree/main/include/wjr/biginteger>
  - <https://github.com/wjr-z/wjr/tree/main/include/wjr/math>
  - <https://github.com/wjr-z/wjr/tree/main/src>
  - <https://github.com/wjr-z/wjr/tree/main/src/biginteger>
  - <https://github.com/wjr-z/wjr/tree/main/src/biginteger/detail>
  - <https://github.com/wjr-z/wjr/tree/main/src/math>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/README.md>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/docs/modules/README.md>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/benchmarks/src/biginteger.cpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/include/wjr/biginteger.hpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/include/wjr/biginteger/biginteger.hpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/include/wjr/biginteger/detail.hpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/include/wjr/math/mul.hpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/src/biginteger/detail/gmp-helper.hpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/src/biginteger/detail/fft.cpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/src/biginteger/detail/mul.cpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/src/biginteger/detail/mulmod_bknp1.cpp>
  - <https://raw.githubusercontent.com/wjr-z/wjr/HEAD/src/biginteger/detail/high-toom.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/wjr-z/wjr`) · [data/wave8/enrich/raw/github_com_wjr_z_wjr.json](../../../data/wave8/enrich/raw/github_com_wjr_z_wjr.json) (enrichment confidence 0.65)

</details>
