# Clamp loop with conditional store instead of std::min (The C++ Programmer's Mindset, ch. 4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Book micro-idiom: an if-guarded store clamp loop beats a std::min (cmov) clamp loop by about 1.2x, vectorisation off.

| | |
|---|---|
| **Beats** | std::min-based clamp loop (ct::clamp_min, branch-free/cmov form), same function with auto-vectorisation disabled on both sides |
| **Claimed result** | Average 605 ns for the std::min (cmov) version versus 500 ns for the conditional-store version, about 1.2x faster (derived from those figures); book figures as paraphrased in the seed lead, not on the repo page. The book calls the improvement modest. |
| **Workload** | Clamp 1,000 uint16_t values to a maximum of 0xFF (255) in place; values drawn uniformly from 0..65535 and regenerated outside the timed region each iteration (PauseTiming/ResumeTiming); Google Benchmark time per call. |
| **Metric** | latency |
| **Hardware** | Not stated. |
| **Compiler and flags** | Not stated; the lead says GCC assembly is shown. clamp_loop.cpp marks both functions [[gnu::optimize("no-tree-vectorize")]], a GCC-only attribute that Clang ignores; both functions sit in a separate static library (clamp_loop) so they are not inlined into the benchmark. CMakeLists.txt sets C++20 and no build type or optimisation flags. |
| **Adoption** | 20 stars (Packt companion repository for the 2025 book) |
| **Last commit** | 2026-01-22 |
| **Links** | [repository](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset) · [benchmark](https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_clamp_loop.cpp) |

## Verdict

The repository holds code only; the book's own run, relayed by the seed lead, gives 605 ns per call for the std::min loop against 500 ns for the conditional-store loop when clamping 1,000 uniform uint16_t values to 255 in place, about 1.2x, with tree vectorisation disabled for both through a GCC attribute. Compiler version, flags and CPU are not stated, and the times include Google Benchmark's PauseTiming/ResumeTiming overhead.

## Use it when

- Scalar loops where the clamp or saturate condition is highly predictable, either almost always true (as in this benchmark, 99.6% of values over the limit) or almost never true (rare outliers in sensor or audio samples).
- Loops the compiler will not vectorise anyway (per-element function calls, pointer chasing, loop-carried state), where the choice between a branch and a conditional move is what is left to tune.
- In-place updates where most elements are already in range: the if-form skips the store for them, so read-mostly data are not rewritten.
- As a template for measuring your own data: the two-function harness is small enough to copy and rerun with your real value distribution before committing to either form.

## Skip it when

- Unpredictable data, for example a threshold near the median of the input: roughly every other branch can mispredict, which costs far more than a conditional move, and the repo never measures this case.
- Loops that can be vectorised: the benchmark switches tree vectorisation off for both functions, while a normal optimised build can turn the std::min loop into SIMD min instructions over 16 uint16_t lanes per 256-bit register; the conditional-store form needs masked stores to vectorise and can lose that speedup, so the 1.2x is against an artificially scalar baseline.
- Code that needs a portable or guaranteed win: the gain is about 1.2x on one undisclosed machine and compiler, and a compiler may if-convert or lay out the branch differently from version to version.
- Clamping whole arrays for throughput: a SIMD library min (xsimd, Vc) or an auto-vectorised std::min/std::clamp loop is the bigger lever.

## How it is fast

The std::min form is the branch-free (compare plus conditional move) version named in the record's baseline: every element is loaded, compared, selected and stored, and the stored value depends on that load-compare chain. The if-form is a real branch: when the predictor guesses right the CPU runs ahead past the compare, the stored value is the constant 0xFF, and in-range elements are not stored at all. With a threshold of 255 and uniform 16-bit input about 99.6% of elements exceed the limit (derived from the repo constants), so the branch is almost perfectly predictable; this is branch prediction against predication (if-conversion, cmov), and the advantage reverses when the branch becomes unpredictable.

## Compared with alternatives

Use this idiom only for scalar loops that will not vectorise; for bulk clamping of arrays, an auto-vectorised std::min/std::clamp loop or xsimd/Vc min operations process 16 or more uint16_t values per instruction, which dwarfs a 1.2x scalar gain.

## Integration

| | |
|---|---|
| **Form** | source-drop (a loop idiom; the repo sample is the clamp_loop static library plus a Google Benchmark executable) |
| **Dependencies** | none for the idiom; the benchmark needs Google Benchmark, and the shared Chapter-04 CMake project also requires GTest, Threads and OpenMP (and optionally BLAS) at configure time; Chapter-04 has no vcpkg.json at HEAD |
| **Minimum toolchain** | C++20 for std::span (CMakeLists sets CMAKE_CXX_STANDARD 20), CMake 3.30+; the no-tree-vectorize switch uses the GCC-only [[gnu::optimize]] attribute |
| **Platforms** | any (portable C++); the branch-versus-cmov balance depends on the CPU's branch predictor and the compiler's code layout |
| **Thread safety** | Not documented; both functions modify the span in place, so concurrent calls need disjoint spans. |
| **Drop-in for the baseline** | partial: if (v &gt; max) v = max gives the same result as v = std::min(v, max) for these unsigned integers, but whether it is faster depends on how predictable the data are and on whether the loop would otherwise vectorise. |

## Gotchas

- The workload is the predictable extreme: about 99.6% of uniform uint16_t values exceed 0xFF, so both versions store nearly every element and the branch is almost always taken. Open issue #15 notes that the book text implies an [[unlikely]] hint on this branch; the maintainer replied that the code is correct and the compiler already places the store path out of line without the attribute, yet with this benchmark's data that path runs 99.6% of the time, so an [[unlikely]] hint would be the wrong hint here.
- Vectorisation is disabled with [[gnu::optimize("no-tree-vectorize")]], which only GCC honours (Clang ignores the unknown attribute, so a Clang build can vectorise both loops). The GCC manual says the optimize attribute is for debugging only and not for production, and kernel and GCC discussions report it can drop other command-line optimisation settings for the function (per WebSearch snippets; gcc.gnu.org was unreachable). It applies to both functions, so the comparison stays symmetric but unrepresentative of production builds.
- Chapter-04/CMakeLists.txt sets no CMAKE_BUILD_TYPE or -O flags; a plain single-config configure builds without optimisation, where std::min stays an out-of-line function call and the comparison means something else. Reproduce with -DCMAKE_BUILD_TYPE=Release, and note the book's compiler, flags and CPU are not recorded in the repo.
- Each iteration calls PauseTiming/ResumeTiming around a roughly 500 ns kernel; that timer overhead lands in both measurements, so absolute times are overstated and the 605 versus 500 ns ratio is compressed (the absolute gap is about 105 ns per 1,000 elements, about 0.1 ns per element, derived). Each benchmark also seeds its generator from std::random_device, so the two series see different value sequences.

## Known shortcomings

- Book numbers only. PauseTiming/ResumeTiming overhead around a \~500 ns kernel compresses the ratio; gnu::optimize("no-tree-vectorize") is GCC-only, Clang ignores it.
- Enricher: no build type in the chapter CMakeLists (a plain configure is unoptimised); [[gnu::optimize]] is a debugging aid that can drop other flags; PauseTiming overhead compresses the ratio; issue #15 on the branch hint.

## Caveats and trade-offs

The numbers are the book's own figures as paraphrased in the seed lead; they are not printed anywhere on the repository pages opened (the repo holds the benchmark code and no results), and the book itself was deliberately not consulted. With a threshold of 0xFF and uniform uint16_t input, about 99.6% of elements exceed the threshold (derived from the repo constants), so the branch is almost always taken and well predicted: the favourable case for the branchy version, and both versions store almost every element. Vectorisation is switched off for both functions via a GCC-only attribute (a Clang build would vectorise both), which hides the SIMD min a normal -O3 build would use for std::min and makes the comparison unrepresentative of production builds. Each iteration calls PauseTiming/ResumeTiming around a sub-microsecond kernel; Google Benchmark documents these calls as costly, and part of the timer start/stop cost lands in the measured time, so the absolute ns figures overstate the kernel time and the ratio is only indicative. CPU, compiler version and flags not stated. Tier C: first-party book measurement. [retier] Enricher: the Chapter-04 CMakeLists sets no build type, so a plain configure builds unoptimised and std::min stays a function call. GCC documents [[gnu::optimize]] as a debugging aid that can drop other optimisation flags (search snippet; gcc.gnu.org unreachable), affecting both sides. Open issue #15 (2026-03-05): the book text implies [[unlikely]] on the clamp branch; the maintainer says the code is right and the compiler puts the store path out of line anyway; the data make the branch 99.6% taken, so such a hint would be wrong.

Micro-idiom, not a library: whether a branch beats cmov depends on how predictable the data are, so the result flips on other distributions.

## Maintenance

Packt companion repository, MIT-licensed, 20 stars and 8 forks; last commit 2026-01-22 (a README; code last changed in November 2025), with one open issue (#15) about this exact loop; there is nothing to vendor because the idiom is two lines.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter-04/bench_clamp_loop.cpp times ct::clamp_min (std::min) against ct::clamp_conditional on 1,000 uint16_t values with Google Benchmark, but the repo holds code only; the 605 versus 500 ns figures are the book's own run relayed by the lead, with compiler, flags and CPU unstated, so first-party C.
- **Verifier notes:** Source matches the record (1,000 uint16_t, max 0xFF, refill under PauseTiming, both functions no-tree-vectorize). Added the PauseTiming/ResumeTiming overhead on a \~500 ns kernel and the GCC-only attribute to caveats. Metadata confirmed: MIT, 20 stars, last commit 2026-01-22 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/blob/main/Chapter-04/bench_clamp_loop.cpp>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-04>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_clamp_loop.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/clamp_loop.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/clamp_loop.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/tree/main/Chapter-04>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/commits/main>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues>
  - <https://github.com/PacktPublishing/The-CPP-Programmers-Mindset/issues/15>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/bench_clamp_loop.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/clamp_loop.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/clamp_loop.h>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/Chapter-04/vcpkg.json>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-CPP-Programmers-Mindset/HEAD/LICENSE>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-cpp-programmers-mindset-clamp-conditional-store`) · [data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_clamp_conditional_store.json](../../../data/wave1/enrich/raw/paper_book_the_cpp_programmers_mindset_clamp_conditional_store.json) (enrichment confidence 0.6)

</details>
