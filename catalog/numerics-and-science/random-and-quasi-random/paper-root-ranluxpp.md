# ROOT RanluxppEngine (portable RANLUX++)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-2.1-or-later` · 🟢 active

> Portable C++ RANLUX++ in ROOT mathcore: RANLUX-quality doubles at about 9 ns, versus 62 ns for ROOT's classic TRandom1 RANLUX.

| | |
|---|---|
| **Beats** | ROOT TRandom1 (RANLUX); ROOT TRandom3 (Mersenne Twister) is faster than RANLUX++ in the same benchmark |
| **Claimed result** | ROOT blog 'Implementing and tuning RANLUX++ for ROOT' (2020-11-30): initial portable version about 30 ns per double, Sibidanov's assembly version about 8 ns, TRandom1 (RANLUX, single precision) about 62 ns, after tuning about 9 ns per number ('very close to the assembly version'), slightly slower than TRandom3 at about 3 ns. Derived from page data: about 6.9x faster than TRandom1 (62 ns versus 9 ns); 2x faster than TRandom1 already at the untuned 30 ns. Tuning gains reported: loop unrolling up to 30 percent, overflow handling up to 15 percent, native __int128 multiplication over 40 percent, carry propagation over 20 percent on GCC 7.5.0. |
| **Workload** | Average time per generated random double from a Google Benchmark microbenchmark (BM_Rndm calling Rndm() once per iteration, rootbench TRandomBenchmarks.cxx) for TRandom1, TRandom3, TRandomMixMax and TRandomRanluxpp, 10 repetitions with standard deviation under 1 percent. |
| **Metric** | latency |
| **Hardware** | Single core of an AMD Ryzen 9 3900, CentOS 8.2.2004 |
| **Compiler and flags** | GCC 8.3.1 (default); graph also covers Clang 9.0.1 and GCC 7.5.0 built from source; optimisation flags not stated in the post. |
| **Adoption** | ROOT: 3.3k stars; used across high-energy physics; RANLUX++ shipped in ROOT 6.24 |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/root-project/root) · [benchmark](https://raw.githubusercontent.com/root-project/web/main/blog/_posts/2020-11-30-ranluxpp.md) |

## Verdict

The ROOT blog (Jonas Hahnfeld, 2020-11-30) reports a Google Benchmark of Rndm() on one core of an AMD Ryzen 9 3900 under CentOS 8.2 with GCC 8.3.1 (plus Clang 9.0.1 and GCC 7.5.0 in the graph): tuned TRandomRanluxpp about 9 ns per double versus TRandom1 (James' RANLUX, 24-bit single precision) about 62 ns, Sibidanov's assembly about 8 ns, and TRandom3 about 3 ns; the blog also cites Luescher's newer ranlxd at 30 ns per double, so against modern RANLUX the gain is about 3.3x (derived from page data), and optimisation flags are not stated.

## Use it when

- You already use ROOT and want a better default than TRandom3 or TRandom1 for Monte Carlo where the generator's theoretical mixing guarantees matter (lattice QCD, detector simulation).
- You currently pay for RANLUX (TRandom1, gsl_rng_ranlxd, std::ranlux48) and want the same family at a much higher luxury level (p=2048) for less time per number.
- You need reproducible parallel streams: Skip(n) jumps ahead in logarithmic time through modular exponentiation, and SetSeed(s) starts at a^(s x 2^96) times a fixed initial state, so different seeds sit far apart in the same sequence.
- You must stay portable (non-x86, or compilers that cannot take Sibidanov's assembly) but want close to the assembly version's speed (about 9 ns versus 8 ns in the ROOT blog).

## Skip it when

- Raw speed is the goal: in the same benchmark TRandom3 (Mersenne Twister) ran at about 3 ns per number, and xoshiro/PCG-class generators in the sibling entries are faster still.
- You do not want ROOT as a dependency: the engine lives in libMathCore, derives from ROOT's TRandomEngine, and is LGPL-2.1-or-later, so extracting it means copying RanluxppEngine.h, RanluxppEngineImpl.cxx and the src/ranluxpp helper headers and stripping the base class.
- Your compiler lacks unsigned __int128 (for example MSVC): mulmod.h then falls back to 32-bit partial products, and the blog attributes more than 40 percent of the tuned speed to __int128.
- You need bit-for-bit continuity with ROOT 6.24.00 output: the June 2021 bias fix (PR #8293) changed the generated sequence.

## How it is fast

RANLUX normally discards hundreds of subtract-with-borrow outputs per kept block (that is its 'luxury level'); RANLUX++ instead skips p steps at once by multiplying the 576-bit state by a precomputed a^p mod m (m = 2^576 - 2^240 + 1), so a luxury level of 2048 costs one big multiply-and-reduce per block of 12 48-bit numbers. The multi-word multiply uses unsigned __int128 where the compiler has it (the blog credits this with more than 40 percent), plus fully unrolled loops via #pragma GCC unroll / #pragma unroll, branch-free overflow handling and carry propagation, and a modulo reduction that exploits the special form of m. Skip(n) is O(log n) through modular exponentiation (powermod) rather than generating and discarding.

## Compared with alternatives

Pick it over sibidanov/ranluxpp when you need portability beyond x86-64 assembly or the 2021 bias and modulo fixes (Sibidanov's version was about 8 ns versus this one's 9 ns in the ROOT blog, but lacks those fixes); pick xoshiro, PCG, SFMT or Philox siblings instead when throughput matters more than RANLUX's theoretically founded mixing. A standalone C port derived from this code and Sibidanov's exists (jirka-h/ranluxpp-portable) if you want it without ROOT.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | ROOT (libMathCore; TRandomEngine base, TRandomGen wrapper). The ranluxpp/\*.h helpers themselves need only &lt;cstdint&gt;. |
| **Minimum toolchain** | C++17 (ROOT's minimum; the engine code itself uses only C++11 features). GCC 8+ or Clang for the unroll pragmas to take effect; __int128 support for full speed. |
| **Platforms** | any platform ROOT builds on; the helpers are portable C++ and their unroll pragmas also cover __CUDACC__ and the Intel compiler |
| **Thread safety** | not documented; each engine instance holds mutable state (9 x 64-bit words, carry, bit position) without locking, so use one engine per thread |
| **Drop-in for the baseline** | partial: TRandomRanluxpp drops in wherever a TRandom (TRandom1) is used, but its sequence differs from TRandom1's; RanluxppCompatEngineJamesP3/P4 reproduce James' RANLUX sequence (gsl_rng_ranlux) and RanluxppCompatEngineStdRanlux24/48 reproduce std::ranlux24/48 sequences through ROOT's TRandomEngine interface, not the std::uniform_random_bit_generator interface. |

## Gotchas

- The 2020 timings (30 ns initial, about 9 ns tuned) were measured before the June 2021 fixes that made mod_m return the smallest representative, convert the LCG state back to RANLUX numbers on every block (to_lcg/to_ranlux), and cut output from 52 to 48 bits per double; the shipped generator has not been re-timed in a public source read here.
- ROOT 6.24.00 shipped the biased version, and issue #8503 reported undefined behaviour (left shift of -1 in mulmod.h) in 6.24, fixed by PR #8522 in June 2021; use a later release.
- RanluxppEngine is a pimpl (std::unique_ptr to the implementation) whose operator() is defined in the library, and TRandomRanluxpp::Rndm() is virtual, so each number pays a non-inlinable call; batch with RndmArray() where possible.
- Doubles carry 48 random bits (multiples of 2^-48), not the full 53-bit mantissa; RanluxppEngine24 is the low-luxury variant and is not what TRandomRanluxpp uses (it uses p=2048).

## Known shortcomings

- Tier C: the blog numbers (Ryzen 9 3900, GCC 8.3.1) come from rootbench TRandomBenchmarks.cxx with unstated flags and were measured before the June 2021 fixes. The same post puts Luescher's newer RANLUX at 30 ns per double, so the gain over that is about 3.3x (derived from page data), not the 6.9x headline against the old RANLUX.
- The 2020 figure of about 9 ns was measured before the June 2021 bias fix (PR #8293), which changed the output sequence and added a to_lcg/to_ranlux conversion on every block; the shipped code was never re-timed. ROOT 6.24.00 shipped the biased code plus undefined behaviour (issue #8503, fixed by PR #8522). The engine uses a pimpl with a virtual Rndm(), so calls cannot be inlined, and without __int128 (MSVC) it falls back to a slower path. TRandom3 (about 3 ns) is still faster and gRandom still defaults to TRandom3.

## Caveats and trade-offs

The benchmark compares against TRandom1 (original RANLUX) and does not beat std::mt19937, PCG or xoshiro: in the same post TRandom3 (Mersenne Twister) is about 3 ns per number, about 3x faster. TRandom1 yields only 24-bit single-precision numbers while RANLUX++ yields 48-52 bits per double, so the work per number differs. The post itself notes that Luescher's newer RANLUX (ranlxd) was measured at 30 ns for double values in a cited review, so against modern RANLUX the tuned 9 ns is about 3.3x faster (derived from page data), not 6.9x; std::ranlux24/std::ranlux48 from &lt;random&gt; were not measured. The measured code predates correctness changes in June 2021 (commits '[mathcore] Ensure full modulo operation in mod_m', 'RANLUX++: Convert LCG state to RANLUX numbers', 'RANLUX++: Extract only 48 bits per number', per the RanluxppEngineImpl.cxx history page; the blog says 52 bits per double), so the 9 ns figure was not re-measured for the shipped implementation and the tier is capped at C. Optimisation flags are not stated; the benchmark source is public (root-project/rootbench PR #200, merged 2020-12-15, root/math/mathcore/TRandomBenchmarks.cxx) but no results are checked in. The last commit shown for RanluxppEngineImpl.cxx was 2021-06-23 (the June 2021 commit 'Move RANLUX++ implementation to directory' split helpers into a subdirectory not covered by that file history); last_commit above is the overall ROOT repo (large project, judged only for math/mathcore RanluxppEngine\*).

Portable C++ (uses unsigned __int128 where available, with unrolling pragmas) instead of Sibidanov's x86 assembly; 576-bit LCG state stored as 9 x 64-bit words, and the generator advances in blocks via a multiply and modulo. It gives 48 random bits per double and passes TestU01 per the blog, but it is about 3x slower than ROOT's Mersenne Twister and the code sits inside ROOT (mathcore) with ROOT dependencies (TRandomEngine base class), so extracting it needs the src/ranluxpp helper headers. Provides RanluxppEngine24 and RanluxppEngine2048 plus compatibility engines for James/Luescher RANLUX.

## Maintenance

Actively maintained inside ROOT (LGPL-2.1-or-later, copyable with attribution and LGPL terms); the RANLUX++ code last changed functionally with the June 2021 bias and UB fixes (later commits are typo and Doxygen edits from 2022 and 2023), an attempt to move it into ROOT's builtins folder was closed unmerged on 2026-09-23, and gRandom still defaults to TRandom3. Geant4 11.0 release notes list a Ranlux++ engine requiring CLHEP 2.4.5.1 (search snippet only; not checked whether it is this code).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The ROOT blog post (author Jonas Hahnfeld, ROOT developer) gives 30 ns initial, about 9 ns tuned, 62 ns for TRandom1, about 3 ns for TRandom3 and 8 ns for Sibidanov's assembly, on one core of an AMD Ryzen 9 3900 with GCC 8.3.1; the benchmark code (rootbench root/math/mathcore/TRandomBenchmarks.cxx, BM_Rndm over TRandom1, TRandom3, TRandomMixMax, TRandomRanluxpp) is public, but optimisation flags are not stated and the measured code predates the June 2021 correctness changes, so first-party C, not A.
- **Verifier notes:** Every number in claimed_speedup and the hardware/compiler fields match the raw blog markdown; ROOT license LGPL v2.1+, 3.3k stars and newest commit 2026-10-02 confirmed. Added the post's own caveat that Luescher's newer RANLUX runs at 30 ns per double, which shrinks the derived gain to about 3.3x.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/root-project/web/main/blog/_posts/2020-11-30-ranluxpp.md>
  - <https://github.com/root-project/rootbench/pull/200>
  - <https://raw.githubusercontent.com/root-project/rootbench/HEAD/root/math/mathcore/TRandomBenchmarks.cxx>
  - <https://raw.githubusercontent.com/root-project/rootbench/HEAD/root/math/mathcore/CMakeLists.txt>
  - <https://github.com/root-project/root/commits/master/math/mathcore/src/RanluxppEngineImpl.cxx>
  - <https://github.com/root-project/root>
  - <https://github.com/root-project/root/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/root-project/web/main/blog/_posts/2020-11-30-ranluxpp.md>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/inc/Math/RanluxppEngine.h>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/src/RanluxppEngineImpl.cxx>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/src/ranluxpp/mulmod.h>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/src/ranluxpp/ranlux_lcg.h>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/src/ranluxpp/helpers.h>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/inc/TRandomGen.h>
  - <https://raw.githubusercontent.com/root-project/root/master/math/mathcore/src/TRandom3.cxx>
  - <https://raw.githubusercontent.com/root-project/root/master/LICENSE>
  - <https://raw.githubusercontent.com/root-project/root/master/cmake/modules/CheckCompiler.cmake>
  - <https://raw.githubusercontent.com/root-project/rootbench/HEAD/root/math/mathcore/TRandomBenchmarks.cxx>
  - <https://github.com/root-project/root/issues?q=ranluxpp>
  - <https://github.com/root-project/root/pull/8293>
  - <https://github.com/root-project/root/issues/8503>
  - <https://github.com/root-project/root/pull/23467>
  - <https://github.com/root-project/root/commits/master/math/mathcore/src/ranluxpp>
  - <https://github.com/jirka-h/ranluxpp-portable>
  - https://www.epj-conferences.org/articles/epjconf/abs/2021/05/epjconf_chep2021_03008/epjconf_chep2021_03008.html (WebSearch snippet only; cds.cern.ch PDF EGRESS_BLOCKED)
  - https://geant4-data.web.cern.ch/ReleaseNotes/ReleaseNotes.11.0.html (WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:root-ranluxpp`) · [data/wave8/enrich/raw/paper_root_ranluxpp.json](../../../data/wave8/enrich/raw/paper_root_ranluxpp.json) (enrichment confidence 0.8)

</details>
