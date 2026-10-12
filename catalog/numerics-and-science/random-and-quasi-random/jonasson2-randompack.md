# Randompack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> C11 bulk random-variate library (xoshiro/PCG/Philox/ChaCha, 20+ distributions); \~10-15x faster than C++ &lt;random&gt; for U(0,1)/N(0,1) fills.

| | |
|---|---|
| **Beats** | C++ std &lt;random&gt; (std::mt19937_64 + std::uniform_real_distribution / std::normal_distribution), NumPy, Base-R, Julia, oneMKL |
| **Claimed result** | Paper Table 8 (Linux workstation, clang), ns/value: U(0,1) Randompack 0.42 vs C++ std 6.3 (\~15x, derived from page data), NumPy 1.8, Julia 0.7, MKL 0.5; N(0,1) Randompack 1.4 vs C++ std 14.3 (\~10x, derived from page data), NumPy 8.9, Julia 1.4, MKL 2.3 |
| **Workload** | Bulk U(0,1) and N(0,1) sampling, ns per value, with xoshiro/PCG64/Philox/ChaCha20 engines and SIMD (AVX2/AVX-512/NEON) |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-1335U (main); also Xeon Platinum 8358, Cortex-X925, Apple M4 |
| **Compiler and flags** | clang (version not stated in paper; gcc 1-16% slower, icx 6% slower); meson buildtype=release (via scripts/meson-setup.sh) with -ffp-model=precise -ffp-contract=off; C++ bench built with -U_GLIBCXX_ASSERTIONS |
| **Adoption** | 3 stars; conda-forge; bindings for Fortran, R, Python, Julia |
| **Last commit** | 2026-08-27 (CHANGELOG 0.1.11; commit page blocked by robots.txt) |
| **Links** | [repository](https://github.com/jonasson2/randompack) · [benchmark](https://arxiv.org/html/2605.05099) |

## Verdict

On an Intel Core i5-1335U with clang, the author's paper (Table 8) reports bulk U(0,1) at 0.42 ns/value vs 6.3 for C++ std::mt19937_64 + uniform_real_distribution (\~15x) and N(0,1) at 1.4 vs 14.3 ns/value for std::normal_distribution (\~10x); NumPy, Julia and MKL are also listed, with Julia and MKL close. The C++ comparison code (benchmark/TimeDistCpp.cpp) is public; the C++ standard library and clang version are not stated.

## Use it when

- Filling large arrays (thousands+) of U(0,1), normal, exponential or gamma variates in Monte Carlo or simulation code where std::mt19937_64 + &lt;random&gt; distributions dominate the profile.
- Projects that need the same stream across C, C++, Fortran, Python, R and Julia, or across x86-64, ARM and Windows/macOS/Linux (bit-identical for the core distributions, optional bitexact mode for the rest).
- Parallel simulations needing reproducible independent substreams (spawn keys, jumps, Philox/squares keys) and checkpoint/restart via state serialization.
- Code that wants a choice of engines behind one API, including ChaCha20 when a cryptographically secure generator is required.

## Skip it when

- One-at-a-time draws inside a hot loop: the speed comes from bulk fills, and per-call use (n=1) does not get the buffered/SIMD benefit (only bulk timings are published).
- If you already have oneMKL: the paper reports MKL faster for U(0,1) (about 1.3x) and for some distributions such as beta and gamma; Julia is on par for normals and faster for permutations/sampling.
- If you need a header-only or std::-compatible URBG to plug into existing &lt;random&gt; code or templates.
- If you need a mature, widely used dependency: young project (0.1.x, first release 2026), 3 stars, single author, paper submitted to ACM TOMS but not yet peer reviewed.
- Non-bitexact mode gives tolerance (about 2 ulp) rather than bit reproducibility for secondary distributions; bitexact mode costs 2-4x on some distributions.

## How it is fast

Bulk generation through an internal 144-word (1152-byte) buffer and tight inlined loops instead of one virtual-ish call per sample. The default engine x256++simd runs eight xoshiro256++ streams in parallel on AVX2, AVX-512 or NEON (unrolled scalar fallback elsewhere). Normals use a 256-strip ziggurat (Marsaglia-Tsang with McFarland's 2016 refinements), uniforms use a 52-bit mantissa bit trick, and vectorized log/exp come from Sleef.

## Compared with alternatives

Pick Randompack when you need full distributions (normal, gamma, beta, etc.) in bulk with cross-language reproducibility; SIMDxorshift and Randen only give raw bits, and cxx-ziggurat covers only the normal distribution as a header-only C++ piece. Use Randen when you need backtracking-resistant output with an std-compatible C++ engine.

## Integration

| | |
|---|---|
| **Form** | shared lib (Meson/Ninja build, default_library=shared; also conda-forge librandompack) |
| **Dependencies** | Meson &gt;= 1.3, Ninja, pkg-config; BLAS/LAPACK for multivariate normal (Accelerate/OpenBLAS/MKL auto-detected, bundled reference fallback); README says a Fortran compiler is required for the source build; uses OpenLibm-derived transcendental code and Sleef vector math per the paper |
| **Minimum toolchain** | C11 compiler (clang, gcc, icx, MSVC, nvc tested); C++17 for the C++ benchmark |
| **Platforms** | x86-64 (AVX2/AVX-512 paths), aarch64/NEON (Apple M, Linux ARM), Windows; scalar fallback without SIMD or 128-bit multiply; requires 32-bit int and 64-bit long long |
| **Thread safety** | Thread-safe if each thread uses its own rng object; no global state |
| **Drop-in for the baseline** | no |

## Gotchas

- meson.build defaults to buildtype=debug; pass --buildtype=release (as the README and scripts/meson-setup.sh do) or the benchmarked speed will not appear.
- The default engine is x256++simd (eight interleaved xoshiro256++ streams), so its output is not the same sequence as a scalar xoshiro256++ with the same seed.
- For Philox and squares, do not change the counter via randompack_set_state while in use; the library advances counters internally as it fills buffers.
- Multivariate normal is double precision only and pulls in BLAS/LAPACK.

## Known shortcomings

- Paper only submitted to ACM TOMS, not yet peer reviewed; standard library and clang version not stated; the C++ std baseline is weak (Julia and MKL come close); 3 stars.
- Speedup only in bulk array fills; oneMKL faster for U(0,1) (\~1.3x) and beta/gamma, Julia matches on normals and wins on permutations/sampling; meson.build defaults to a debug build; source build needs a Fortran compiler; single author.

## Caveats and trade-offs

Paper submitted to ACM TOMS (April 2026), not yet peer reviewed; first-party measurement; standard library implementation and clang version for the C++ column not stated; std::normal_distribution and mt19937_64 are known-slow baselines, while Julia and MKL are close; meson.build default buildtype is debug (the setup script and docs use release); 3 stars

C API library covering many engines and 20+ distributions; speedup comes from buffering/SIMD bulk generation rather than a new engine

## Maintenance

Actively maintained (0.1.11 on 2026-08-27, frequent releases with PyPI, CRAN, Julia and conda-forge packaging); MIT-licensed and copyable, but young and single-author.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Tier changes from B (paper is only submitted to ACM TOMS, not peer reviewed) to A: the C++ comparison code is public (benchmark/TimeDistCpp.cpp, std::mt19937_64 + std uniform/normal distributions), the CPU is stated (i5-1335U), the compiler is clang, and the flags come from the repo build (meson release via scripts/meson-setup.sh, -ffp-model=precise -ffp-contract=off).
- **Verifier notes:** Corrected the claim wording: the record's '15x slower' meant C++ std is \~15x slower. Commits page blocked by robots.txt, so last_commit comes from the CHANGELOG date.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/html/2605.05099>
  - <https://github.com/jonasson2/randompack>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/README.md>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/INTERFACES.md>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/benchmark/TimeDistCpp.cpp>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/benchmark/meson.build>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/meson.build>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/scripts/meson-setup.sh>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/CHANGELOG.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/README.md>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/INTERFACES.md>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/benchmark/TimeDistCpp.cpp>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/meson.build>
  - <https://arxiv.org/html/2605.05099>
  - <https://github.com/jonasson2/randompack/issues>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jonasson2/randompack`) · [data/wave8/enrich/raw/github_com_jonasson2_randompack.json](../../../data/wave8/enrich/raw/github_com_jonasson2_randompack.json) (enrichment confidence 0.75)

</details>
