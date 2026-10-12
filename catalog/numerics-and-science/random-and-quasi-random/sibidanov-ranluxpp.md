# RANLUX++ (sibidanov/ranluxpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `LGPL-3.0-or-later` · 🔴 abandoned

> RANLUX recast as a 576-bit LCG with x86-64 assembly modmul; about 8x faster than classic RANLUX implementations.

| | |
|---|---|
| **Beats** | std::ranlux (GCC libstdc++ RANLUX) in the repo README and tests/std_random_test.cxx; ROOT's TRandom1 (James' RANLUX implementation) in the independent ROOT measurement |
| **Claimed result** | Independent (ROOT blog, AMD Ryzen 9 3900, GCC 8.3.1): Sibidanov's implementation 'comes in at around 8ns per number' vs TRandom1 RANLUX 'around 62ns per number' (single-precision only), about 7.8x (derived from page data); ROOT's own portable RANLUX++ reaches about 9 ns after tuning. First-party README: 'generation speed achieved (20 clock/float) is order of magnitude faster than the usual approach, for example, GCC C++ RANLUX implementation where 198 clock/float is measured at Haswell CPU'; the optimized conventional RANLUX reaches 40 clock/float, and 'The SSE2 and AVX2 versions is approximately 4 and 8 times faster correspondingly' (README does not name the reference; the SIMD classes run 4 or 8 independent RANLUX lanes, so this is aggregate throughput). |
| **Workload** | Generation of single-precision floats from the RANLUX family: an LCG formulation of RANLUX (modulus 2^576 - 2^240 + 1, 576x576-bit modular multiplication in x86-64 assembly) versus GCC's std::ranlux and a SIMD-optimized conventional RANLUX. |
| **Metric** | throughput |
| **Hardware** | README: Haswell (GCC RANLUX 198 clock/float) and Skylake (155 clocks per 576-bit modular multiplication), microarchitectures only; the CPU for the 20 clock/float figure is not named. ROOT blog: single core of an AMD Ryzen 9 3900. |
| **Compiler and flags** | Repo Makefile: g++ -O3 -Iinc -mavx2 -DASMSKIP (compiler version not stated). Independent ROOT measurement: GCC 8.3.1 on CentOS 8.2.2004 (flags not stated). |
| **Adoption** | 11 stars, 4 forks; the algorithm was adopted in ROOT 6.24 as TRandomRanluxpp/RanluxppEngine through a portable C++ reimplementation (not this x86-64 assembly code); described in Computer Physics Communications 2017 (arXiv 1705.03123) |
| **Last commit** | 2018-01-17 |
| **Links** | [repository](https://github.com/sibidanov/ranluxpp) · [benchmark](https://github.com/root-project/web/blob/main/blog/_posts/2020-11-30-ranluxpp.md) |

## Verdict

A ROOT developer measured Sibidanov's assembly implementation at about 8 ns per number against about 62 ns for ROOT's TRandom1 RANLUX (single precision only) on one core of an AMD Ryzen 9 3900, CentOS 8.2, GCC 8.3.1, 10 repetitions with under 1% standard deviation, flags not stated (about 7.8x, derived from page data). The README's own figure, 20 versus 198 clocks per float against GCC's std RANLUX on Haswell, is first-party, mixes CPUs and does not say whether ranlux24 or ranlux48 was timed.

## Use it when

- HEP, lattice or other Monte Carlo codes that must use a RANLUX-family generator for its theoretical mixing guarantees and are bottlenecked by std::ranlux24/48 or James-style RANLUX (TRandom1)
- x86-64 Linux with GCC, where the assembly and function multiversioning build as shipped
- Many independent streams: seeds map to jumps of 2^96\*seed states, and jump(n) skips n RANLUX numbers in O(log n) modmuls
- Research or testing that needs the RANLUX-to-LCG state mapping (getlcgstate / getranluxseq) or a fast reference to check another RANLUX++ port against

## Skip it when

- Throughput-first simulations: RANLUX++ is still slower than Mersenne Twister (ROOT measured TRandom3 at about 3 ns versus about 8 ns), and xoshiro/PCG/Philox are faster still
- Non-x86-64 targets, Windows/MSVC, or non-GCC toolchains: the assembly uses the System V register ABI and the dispatch relies on GCC target attributes; ROOT's portable RanluxppEngine (about 9 ns after tuning on the same Ryzen) or Randompack's MIT ranlux++ cover those cases
- Code that needs bit-exact RANLUX output or the full theoretical guarantees: ROOT's reimplementation documents fixes to this code (canonical modulo result, converting the LCG state back to RANLUX numbers to avoid a bias in the upper state bits, 48 rather than 52 bits per double)
- Projects that cannot accept LGPL-3.0-or-later or an unmaintained dependency (last commit 2018-01-17, 6 commits)
- Code that expects a std:: engine: there is no result_type/min()/max() interface, so &lt;random&gt; distributions cannot use it directly

## How it is fast

Classic RANLUX generates and throws away most of its subtract-with-borrow outputs to decorrelate them; the LCG view replaces all that skipping with a single 576x576-bit modular multiplication. That multiply is hand-written AT&T x86-64 assembly (schoolbook, 81 64x64 products) with mulx and adcx/adox variants picked by GCC function multiversioning, plus a reduction specialized to the sparse modulus: 155 cycles per modmul on Skylake per the README. One modmul yields 24 floats (24-bit) or 11 doubles (52-bit) unpacked directly from the state bits.

## Compared with alternatives

No other catalogued sibling is a RANLUX-family generator except Randompack, whose MIT-licensed ranlux++ engine is reported (per a search snippet of its paper) to be as fast as or up to 2x faster than this code; pick this repo only as the reference assembly on x86-64 Linux with GCC. If RANLUX-grade theory is not required, xoshiro, PCG or Philox siblings (e.g. benchmark-rngs PhiloxSIMD, simdrng) are several times faster.

## Integration

| | |
|---|---|
| **Form** | static lib (Makefile builds libranlux++.a from C++ and GNU as assembly) |
| **Dependencies** | none beyond GCC and GNU as |
| **Minimum toolchain** | GCC with function multiversioning (target("arch=...") overloads); C++11 delegating constructors plus GNU extensions (__attribute__, __builtin_expect, hex-float literals); exact GCC version not documented |
| **Platforms** | x86-64 only (System V ABI assembly); the Makefile builds everything with -mavx2, so the shipped build needs an AVX2 CPU even though mul9x9mod has a generic fallback |
| **Thread safety** | Not documented; all state (LCG words, multiplier, float/double caches) is per instance, so use one object per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Outputs are unpacked from the LCG state, not from the RANLUX base-2^24 sequence, so the numbers differ from std::ranlux24/48 and TRandom1 even when the states are equivalent; primitive() changes the multiplier to a^2048 + 13, which leaves RANLUX equivalence altogether
- init(seed) multiplies the current state instead of resetting to x_0, and it does not clear the float/double caches, so reseeding a used object does not reach the documented x_0\*A^(2^96\*seed) state (read from src/ranluxpp.cxx)
- Multiversion dispatch is keyed to arch=haswell/broadwell/skylake; GCC selects arch= versions by CPU model, so other CPUs (AMD Zen, newer Intel cores) likely run the generic mul path (inferred from src/mulmod.cxx, not documented)
- operator() reinterprets a uint32_t/uint64_t cache as float/double through pointer casts (a strict-aliasing violation) and is marked noinline, so per-call overhead is a real function call; getarray is the fast path

## Known shortcomings

- Faster than ROOT's TRandom1 (RANLUX, \~8 ns vs \~62 ns) but still slower than MT (\~3 ns); last commit 2018-01-17; COPYING and COPYING.LESSER exist (record said no license files).
- ROOT's RanluxppEngineImpl.cxx lists fixes to this code: the modulo result is not always the smallest value, reading output straight from the LCG state biases the upper bits, and it uses 52 instead of 48 bits per double; ROOT's fixed portable version measured \~9 ns vs \~8 ns here, so the speed largely holds after the fixes. init() does not reset state or caches; Makefile builds everything with -mavx2. Randompack's MIT ranlux++ reportedly as fast or up to 2x faster (paper snippet only).

## Caveats and trade-offs

The README's 10x figure mixes CPUs: GCC's 198 clock/float was measured on Haswell, the 155-cycle modmul on Skylake, and the CPU for 20 clock/float is not named. The README does not say whether std::ranlux24 (p=223) or std::ranlux48 (p=389) gave 198 clock/float, while ranluxpp defaults to p=2048 (higher luxury, so the comparison is conservative on quality). ranluxpp's float/double output is unpacked directly from the 576-bit LCG state, not the RANLUX base-2^24 sequence, so the numbers differ from std::ranlux even though the state is provably equivalent; tests/ranluxpp_test.cxx modes 0 and 1 check the LCG state against the conventional RANLUX for 1e8 steps. The SIMD (SSE2/AVX2) conventional-RANLUX classes run 4 or 8 independent RANLUX lanes; their claimed 4x/8x is aggregate multi-stream throughput, and the same-seed consistency check (ranlux_test mode 7) only prints values for visual comparison. RANLUX++ is x86-64 assembly only (mulx/adx variants via GCC function multiversioning). It is faster than other RANLUX implementations but slower than Mersenne Twister: the ROOT blog measures TRandom3 at about 3 ns per number on the same machine. The CPC 2017 paper could not be opened (arxiv.org blocked). License: LGPL-3.0-or-later per source headers, with COPYING (GPLv3) and COPYING.LESSER (LGPLv3) texts at the repo root (there is no LICENSE file).

x86-64 assembly (mulx/adcx/adox variants chosen by GCC function multiversioning), so not portable to other architectures; LGPL-3.0 (COPYING and COPYING.LESSER in repo). The win is inside the RANLUX family: RANLUX is itself far slower than mt19937/PCG/xoshiro, so this does not beat the category baselines.

## Maintenance

Abandoned since January 2018 (6 commits) and LGPL-3.0-or-later; the algorithm lives on in ROOT 6.24+ (TRandomRanluxpp / RanluxppEngine, portable and with correctness fixes) and in Randompack's MIT reimplementation, which are the better choices for new code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. An independent measurement by a ROOT/CERN developer (ROOT blog 'Implementing and tuning RANLUX++ for ROOT', 2020) puts Sibidanov's assembly implementation at about 8 ns per number, against about 62 ns for ROOT's RANLUX (TRandom1), on one core of an AMD Ryzen 9 3900 with GCC 8.3.1. Compiler flags are not given, and the harness used for the assembly version is not identified (rootbench PR #200 benchmarks ROOT's TRandom classes), so not A. The repo README's own 20 vs 198 clock/float figure is first-party only.
- **Verifier notes:** Upgraded to B on the ROOT blog's independent numbers (opened via its GitHub source; root.cern is egress-blocked). The README quote matches the record. The record's 'no license text at HEAD' was wrong: COPYING and COPYING.LESSER exist. Last commit is 2018-01-17 (6 commits total).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/sibidanov/ranluxpp>
  - <https://github.com/sibidanov/ranluxpp/commits/master>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/Makefile>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/COPYING>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/COPYING.LESSER>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/tests/ranluxpp_test.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/tests/std_random_test.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/tests/ranlux_test.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/src/ranluxpp.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/inc/ranluxpp.h>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/inc/ranlux.h>
  - <https://github.com/root-project/web/blob/main/blog/_posts/2020-11-30-ranluxpp.md>
  - <https://raw.githubusercontent.com/root-project/web/main/blog/_posts/2020-11-30-ranluxpp.md>
  - <https://github.com/root-project/rootbench/pull/200>
- **Sources the enricher read:**
  - <https://github.com/sibidanov/ranluxpp/issues?q=is%3Aissue>
  - <https://github.com/sibidanov/ranluxpp/issues/2>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/Makefile>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/inc/ranluxpp.h>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/inc/ranlux.h>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/inc/mulmod.h>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/inc/cpuarch.h>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/src/ranluxpp.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/src/mulmod.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/src/cpuarch.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/src/mul9x9mod.asm>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/tests/ranluxpp_test.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/tests/ranlux_test.cxx>
  - <https://raw.githubusercontent.com/sibidanov/ranluxpp/HEAD/tests/std_random_test.cxx>
  - <https://raw.githubusercontent.com/root-project/web/main/blog/_posts/2020-11-30-ranluxpp.md>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/src/RanluxppEngineImpl.cxx>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sibidanov/ranluxpp`) · [data/wave8/enrich/raw/github_com_sibidanov_ranluxpp.json](../../../data/wave8/enrich/raw/github_com_sibidanov_ranluxpp.json) (enrichment confidence 0.8)

</details>
