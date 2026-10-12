# Julia vs C++11 random-walk Monte Carlo (jlapeyre/ranwalk-Julia-vs-Cxx)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Julia` · `no license` · 🟡 stale

> 2014 toy random-walk benchmark: Julia 0.3's dSFMT-backed randbool() beats libstdc++ mt19937 plus bernoulli_distribution(0.5) about 3x.

| | |
|---|---|
| **Beats** | C++11 std::mt19937 with std::bernoulli_distribution(0.5), compiled with c++ -std=c++11 -O3 (Debian gcc 4.9.1) |
| **Claimed result** | C++-11 3.88 s vs Julia v0.3 1.27 s and Julia v0.4 1.68 s: about 3.1x and 2.3x faster (derived from page data); the README says 'The Julia code runs three times faster than the C++ code'. |
| **Workload** | 100,000 random walks of 3,000 coin flips each, accumulating a histogram of final displacements. |
| **Metric** | throughput |
| **Compiler and flags** | c++ -std=c++11 -O3 (Debian 4.9.1-15 gcc 4.9.1; -march=native was slower); Julia 0.3.4-pre and 0.4 |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Stated by the README: the time is almost all random number generation, and Julia's rand(Bool) is much faster than the GNU C++11 &lt;random&gt; bernoulli_distribution path; the author says this does not support 'Julia is faster than C++'. |
| **Adoption** | 4 stars |
| **Last commit** | 2024-09-09 |
| **Links** | [repository](https://github.com/jlapeyre/ranwalk-Julia-vs-Cxx) · [benchmark](https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/README.md) |

## Verdict

Single 'typical' timings from 2014-2015 on an undocumented CPU: 3e8 coin flips took 3.88 s in C++ (Debian gcc 4.9.1, -std=c++11 -O3, libstdc++ std::mt19937 with std::bernoulli_distribution(0.5), std::clock CPU time) against 1.27 s in Julia 0.3 (randbool(), one ccall into C dSFMT per flip) and 1.68 s in Julia 0.4 (rand(Bool) from a dSFMT-filled buffer). That is about 3.1x and 2.3x, or about 12.9 ns versus 4.2 ns per flip (derived from page data).

## Use it when

- As a cautionary example that libstdc++ std::bernoulli_distribution(0.5) costs two 32-bit engine calls plus a floating-point division per bit; for coin flips in C++, take bits from one engine output instead (one bit per draw, or 32 flips per mt19937 word).
- As a historical data point that Julia's 2014 global RNG (C dSFMT) was a faster Boolean source than GNU libstdc++ &lt;random&gt; on gcc 4.9.1.
- As a minimal teaching pair showing that the RNG and its front end, not loops or function calls, dominate a simple Monte Carlo kernel, which is what the README itself concludes.

## Skip it when

- As evidence that a JIT beats ahead-of-time C++: in Julia 0.3 every flip is a ccall into compiled C (libdSFMT), so the faster side's inner work is AOT C code, and the README says the result does not support 'Julia is faster than C++'.
- As a current benchmark: Julia 0.3/0.4 and gcc 4.9.1 are obsolete, Julia 1.7+ defaults to Xoshiro256++, and the September 2024 script update was not re-timed.
- As copyable code: the repository has no licence file.
- As a statistics reference: the C++ histogram array is never zeroed (see gotchas).

## How it is fast

Almost all of the time is random-number generation. In Julia 0.3, randbool() is ((dsfmt_randui32() & 1) == 1), and dsfmt_gv_genrand_uint32 is a ccall into the C library libdSFMT, which returns one 64-bit word per call from a state block that dSFMT (SIMD-oriented Fast Mersenne Twister) regenerates in bulk every 382 draws. In Julia 0.4, rand(Bool) is rand_ui52_raw(r) % Bool, an inlined pop from a Julia buffer filled in bulk by dsfmt_fill_array_close1_open2!. The C++ side calls std::bernoulli_distribution, which in gcc 4.9's libstdc++ goes through __detail::_Adaptor and generate_canonical&lt;double, 53&gt;: two mt19937 calls, a floating-point multiply-add and a division per flip, then a compare with p. The gap is one dSFMT word per flip against two MT19937 words plus floating point, not JIT versus AOT code generation.

## Compared with alternatives

Do not pick it for a decision; it is the weakest evidence in runtime-jit-beats-aot. For a JIT language beating C++ on comparable code with named toolchains, the kostya/LangArena entries (Julia 1.13 Sort::Self, Java and C# rows) or the Julia no-BLAS matmul entry in kostya/benchmarks are better; keep this one only as an RNG-overhead example.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Julia (the timed rwtest_simple.jl of 2015 needs Julia 0.3 for randbool(); the 2024 scripts use stderr and need Julia 0.7 or later); a C++11 compiler and standard library with &lt;random&gt; |
| **Minimum toolchain** | C++11 (README: Debian gcc 4.9.1, c++ -std=c++11 -O3; -march=native was slower); Julia 0.3.4-pre for the published number |
| **Platforms** | Any; the CPU of the published runs is not documented |
| **Thread safety** | Not applicable: single-threaded programs using a global RNG (std::mt19937 global in C++, the global dSFMT state in Julia 0.3) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the 'Julia' side's hot path is C. Julia 0.3 base/random.jl defines randbool() = ((dsfmt_randui32() & 1) == 1), and base/dSFMT.jl defines dsfmt_gv_genrand_uint32() as ccall((:dsfmt_gv_genrand_uint32, :libdSFMT), Uint32, ()). The 1.27 s figure times a Julia loop around 3e8 calls into compiled C dSFMT, so it is evidence about RNG libraries, not about a runtime JIT beating AOT compilation.
- Unequal work per flip: libstdc++ 4.9 bernoulli_distribution::operator() builds an _Adaptor whose operator() calls generate_canonical&lt;double, 53&gt;; with a 32-bit engine k = (53 + 32 - 1) / 32 = 2, so the C++ program makes 6e8 mt19937 calls plus 3e8 divisions against 3e8 dSFMT words in Julia 0.3. The README concedes a faster C++ program is possible; none was tried with one engine call per flip.
- C++ correctness bugs (output only, not timing): counts_on_lattice_sites is allocated with new int[] and never zeroed, so the printed histogram adds to indeterminate values (Julia uses zeros()), and it is freed with delete instead of delete[], which is undefined behaviour.
- The scripts at HEAD are not the timed code: the 2015 rwtest_simple.jl called randbool() and println(STDERR, ...), the 2024 commit 'Update Julia scripts from 2014 to 2024' replaced them with rand(Bool) and stderr, which do not run on Julia 0.3. Timers also differ (std::clock CPU time in C++, @elapsed wall time in Julia), and the README gives one 'typical' time per language with no CPU model.

## Known shortcomings

- Unequal work: C++ bernoulli_distribution takes two mt19937 draws per flip via generate_canonical while Julia rand(Bool) uses dSFMT; no CPU model; the author disclaims a language win; no licence (reference only).
- Harness flaw: Julia 0.3's randbool() is ((dsfmt_randui32() & 1) == 1) and dsfmt_gv_genrand_uint32 is a ccall into libdSFMT, so the 1.27 s 'Julia' time is a loop calling the C dSFMT library 3e8 times, not JIT code; the C++ side pays two mt19937 calls plus a division per flip (gcc 4.9 libstdc++ generate_canonical&lt;double,53&gt;, k=2). C++ bugs affecting only the output: new int[] is never zeroed and it frees with delete instead of delete[]. The scripts at HEAD (2024) are not the code that was timed.

## Caveats and trade-offs

Not the same work: libstdc++ std::bernoulli_distribution(0.5) goes through generate_canonical&lt;double&gt;, which consumes two 32-bit std::mt19937 outputs plus floating-point arithmetic per coin flip, while Julia 0.3/0.4 rand(Bool) drew from its dSFMT-backed global MersenneTwister (a different SIMD generator), so this compares RNG front ends and generators, not compilers (verifier inference from rwtest_simple.cc, rwtest_simple.jl and libstdc++ &lt;random&gt;; the README itself says the result does not support 'Julia is faster than C++' and that a faster C++ program is possible). The C++ timer is std::clock (CPU time) while Julia uses @elapsed (wall time). The Julia scripts were updated in Sep 2024 ('Update Julia scripts from 2014 to 2024') but the numbers are from Julia 0.3/0.4 and gcc 4.9.1 in 2014-2015; current Julia defaults to Xoshiro256++, so a rerun today would compare a different generator. No licence file (LICENSE and LICENSE.md return 404), so the code is reference only. CPU model not stated, single timing per language. [retier] Harness flaw: Julia 0.3's randbool() is ((dsfmt_randui32() & 1) == 1) with dsfmt_gv_genrand_uint32 a ccall into libdSFMT, so the 1.27 s 'Julia' time is a loop calling the C dSFMT library 3e8 times, not JIT code; the C++ side pays two mt19937 calls plus a division per flip (gcc 4.9 libstdc++ generate_canonical&lt;double,53&gt;). C++ bugs affecting only the output: new int[] never zeroed, freed with delete instead of delete[]. The scripts at HEAD (2024) are not the code that was timed.

Toy benchmark; Julia versions 0.3 and 0.4 are obsolete (the 2024 commit only updated the scripts).

## Maintenance

Stale toy repository (code from 2014-2015, Julia scripts ported to Julia 1.x syntax in September 2024 without new timings) with no licence, so reference only; the measured gap is libstdc++ &lt;random&gt; front-end overhead against the C dSFMT generator, and it supports neither a JIT nor a Julia-over-C++ claim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** README lists 3.88 s C++-11 vs 1.27 s Julia v0.3 and 1.68 s Julia v0.4, with public code (rwtest_simple.cc, rwtest_simple.jl), compiler (Debian gcc 4.9.1) and flags (-std=c++11 -O3), but no CPU model, so not A; author's own single-timing comparison, so C.
- **Retiered** C to D: Enricher: the timed 'Julia' hot path is a loop of 3e8 ccalls into the C dSFMT library while the C++ side draws two mt19937 outputs plus a division per flip, so the gist compares RNG libraries and the code at HEAD is not the code timed; no valid JIT-versus-AOT measurement: C to D.
- **Verifier notes:** Numbers and flags match the README; tier C stands. Shortcomings: different RNG work per flip (two mt19937 draws via generate_canonical vs one dSFMT draw), author disclaims a language-level conclusion, no CPU model, single timings from 2014-2015 toolchains, no licence (reference only).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-57 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/README.md>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/rwtest_simple.cc>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/rwtest_simple.jl>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/rwtest.cc>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/NOTES>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/LICENSE>
  - <https://github.com/jlapeyre/ranwalk-Julia-vs-Cxx>
  - <https://github.com/jlapeyre/ranwalk-Julia-vs-Cxx/commits/master>
- **Sources the enricher read:**
  - <https://github.com/jlapeyre/ranwalk-Julia-vs-Cxx>
  - <https://github.com/jlapeyre/ranwalk-Julia-vs-Cxx/commits/master>
  - <https://github.com/jlapeyre/ranwalk-Julia-vs-Cxx/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/README.md>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/NOTES>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/rwtest_simple.cc>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/rwtest_simple.jl>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/rwtest.cc>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/rwtest.jl>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/master/LICENSE>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/e41eb1f/rwtest_simple.jl>
  - <https://raw.githubusercontent.com/jlapeyre/ranwalk-Julia-vs-Cxx/e41eb1f/rwtest.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/release-0.3/base/random.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/release-0.3/base/dSFMT.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/release-0.4/base/random.jl>
  - <https://raw.githubusercontent.com/MersenneTwister-Lab/dSFMT/master/dSFMT.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-4.9/libstdc%2B%2B-v3/include/bits/random.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-4.9/libstdc%2B%2B-v3/include/bits/random.tcc>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/jlapeyre/ranwalk-julia-vs-cxx`) · [data/wave14/enrich/raw/github_com_jlapeyre_ranwalk_julia_vs_cxx.json](../../../data/wave14/enrich/raw/github_com_jlapeyre_ranwalk_julia_vs_cxx.json) (enrichment confidence 0.8)

</details>
