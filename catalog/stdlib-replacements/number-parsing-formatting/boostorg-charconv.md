# Boost.Charconv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Portable std::to_chars/from_chars reimplementation for pre-C++17 toolchains and MSVC, winning there and near-parity on GCC.

| | |
|---|---|
| **Beats** | std::to_chars, std::from_chars |
| **Claimed result** | Scores relative to std::printf/std::strtoX (higher is faster). Boost vs std, from benchmarks.adoc: Linux GCC 13.1 to_chars float/double 4.46/6.20 vs 4.01/6.03; from_chars float/double 3.28/5.75 vs 3.23/5.77; integer from_chars u32/u64 2.54/1.78 vs 1.97/1.68 (\~1.29x on u32). Windows MSVC 14.3: float/double from_chars 2.06/5.21 vs std 1.01/1.23 (\~2.0x/\~4.2x, the largest wins); double to_chars 15.26 vs 15.77 and u64 to_chars 2.06 vs 2.10 (Boost slightly slower). ARM macOS GCC 13.2: to_chars float/double 7.25/6.86 vs 6.78/6.47; from_chars float/double 1.28/1.63 vs 1.32/1.65 (slightly slower). Overall: parity to \~1.1x vs std in most cells. Clear wins are MSVC float/double from_chars (\~2-4x) and Linux u32 from_chars (\~1.3x). A few cells show small regressions (\~0.97-0.98x). |
| **Workload** | Round-trip shortest to_chars/from_chars formatting and parsing of float/double and base-10 uint32_t/uint64_t integers, scored relative to std::printf/std::strtoX, on GCC 13.1 (Linux), MSVC 14.3 (Windows), and GCC 13.2 (macOS ARM). |
| **Metric** | throughput |
| **Hardware** | x86_64 Linux (unspecified CPU model); x86_64 Windows (unspecified CPU model); Apple M1 Pro (ARM macOS) |
| **Compiler and flags** | GCC 13.1.0 on Ubuntu 23.04 (b2 cxxstd=20, release); MSVC 14.3 (V17.7.0) on Windows 11; Homebrew GCC 13.2.0 on macOS Ventura 13.5.2 (M1 Pro, ARM) |
| **Adoption** | 32 stars; part of the Boost C++ Libraries collection |
| **Last commit** | 2026-08-13 |
| **Links** | [repository](https://github.com/boostorg/charconv) · [benchmark](https://github.com/boostorg/charconv/blob/master/doc/charconv/benchmarks.adoc) |

## Verdict

Maintainer-run benchmarks (test/STL_benchmark.cpp) on Linux GCC 13.1/libstdc++, Windows MSVC 14.3, and macOS ARM (M1 Pro) GCC 13.2 score Boost.Charconv against std::to_chars/from_chars, itself scored against std::printf/std::strtoX; results run from near-parity to \~1.3x in most cells, with the clearest wins on MSVC float/double from_chars (\~2.0x/\~4.2x) and Linux uint32_t from_chars (\~1.3x), and a few Windows/ARM cells (double/uint64_t to_chars, ARM from_chars) slightly slower than std.

## Use it when

- Targeting MSVC and needing float/double from_chars roughly 2-4x faster than std::from_chars (the largest measured win)
- Building for a C++11/14 toolchain (GCC 5+, Clang 3.8+, MSVC 2015+) that lacks &lt;charconv&gt; entirely
- Need to_chars/from_chars for __float128 or 80-bit long double, which std &lt;charconv&gt; doesn't cover
- Already depend on Boost and want one to_chars/from_chars-shaped API across compilers instead of per-compiler fallbacks
- High-volume uint32_t from_chars parsing on Linux/GCC, where Boost measures \~1.3x over std::from_chars

## Skip it when

- Already on a recent GCC/libstdc++ or Clang target, where most cells are near parity (0.97-1.0x) with std::to_chars/from_chars
- Want a true header-only drop-in: charconv ships src/to_chars.cpp and src/from_chars.cpp as separately-compiled sources, plus Boost.Assert/Config/Core as dependencies
- Parsing untrusted long double/__float128 strings over 1024 bytes, the one documented path where it allocates
- Need an independent (non-maintainer) benchmark; the published numbers are run and maintained by the library's own authors
- On Windows double/uint64_t to_chars, where Boost measured very slightly slower than std (15.26 vs 15.77; 2.06 vs 2.10)

## How it is fast

to_chars for floats uses the Dragonbox shortest-round-trip algorithm (detail/dragonbox/dragonbox.hpp, floff.hpp for fixed format); from_chars for floats uses Daniel Lemire's fast_float parser (detail/fast_float/); 80-bit/128-bit long double and __float128 go through Ryu's generic 128-bit path (detail/ryu/ryu_generic_128.hpp); integer to_chars uses precomputed digit-count/significand lookup tables (integer_search_trees.hpp, significand_tables.hpp) for branch-light itoa. These are the same published algorithms most std::to_chars/from_chars implementations already use, so gains show up mainly where the target stdlib (MSVC's) hasn't adopted them as aggressively.

## Compared with alternatives

Pick Boost.Charconv when you need an actual std::to_chars/from_chars-compatible surface (same enums, same result types) on a pre-C++17 toolchain, MSVC, or for __float128/long double, not a different API or output format. Pick c4core, rigtorp/CharConv, or jeaiii/itoa instead when you want larger, unambiguous wins on a modern GCC/Linux stack and don't need std-API compatibility.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (compiled sources in src/; not header-only) |
| **Dependencies** | Boost.Assert, Boost.Config, Boost.Core; optional libquadmath for __float128/std::float128_t |
| **Minimum toolchain** | C++11 (GCC 5+, Clang 3.8+, MSVC 2015 / 19.24+, NVCC 12.8+ for optional CUDA); constexpr paths need C++14 |
| **Platforms** | x86/x86_64/ARM on Linux, macOS, Windows; libquadmath path limited to Linux x86/x86_64/PPC64/IA64; partial CUDA and SYCL device support |
| **Thread safety** | not documented explicitly; functions are stateless, non-allocating, non-throwing with no shared mutable state, so concurrent calls are safe like std::to_chars/from_chars |
| **Drop-in for the baseline** | partial — matches std::to_chars/from_chars signatures, enums, and result types exactly, but lives in boost::charconv:: rather than std::, so call sites must be renamed, not just #include-swapped |

## Gotchas

- Parsing a long double/__float128 string longer than 1024 bytes is the one documented path that allocates, despite the library's non-allocating claim elsewhere
- The fixed-format float path (floff, Dragonbox-based) had buffer-overflow and internal-overflow bugs (issues #186, #190) fixed in 2024; a to_chars-with-precision correctness bug (#158) was also fixed; issue #166 (more to_chars problems) was still open as of the last check
- __float128/std::float128_t support needs libquadmath and only builds on Linux x86/x86_64/PPC64/IA64
- b2/CMake auto-detect and link libquadmath when available; other build systems must define BOOST_CHARCONV_HAS_QUADMATH and link it manually

## Caveats and trade-offs

Not a uniform large win — several results are near-ties or slight regressions vs std (e.g. Windows uint64 to_chars: 2.06x Boost vs 2.10x std). Numbers come from the maintainers' own in-repo benchmark, not an independent third party, though methodology, compiler, and hardware are all disclosed and the benchmark is reproducible via `-a release` b2 build.

Wraps/duplicates functionality already in C++17 &lt;charconv&gt;; main value is C++11 portability and marginal speed; requires Boost; benchmark run and maintained by the library's own authors (not independent third party).

## Maintenance

Actively maintained (last master commit 2026-08-13, CI/fuzzing/codecov all wired up); BSL-1.0 licensed and copyable, but as a Boost library it pulls in Boost.Assert/Config/Core and a compiled component rather than being a single vendorable header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** In-repo benchmark code (test/STL_benchmark.cpp, plus to_chars_float_STL_comp.cpp/from_chars_STL_comp.cpp) is run via the documented b2 command (cxxstd=20, -a release) directly against std::to_chars/std::from_chars. Compiler versions are given for all three runs, and the ARM run names its hardware (M1 Pro). The x86_64 Linux/Windows runs give no CPU model.
- **Verifier notes:** The per-cell numbers in the record match the page exactly. Only the summary sentence was wrong: it said 'at least as fast' and 'up to \~1.3x in most cases', but most cells are near parity and the biggest wins (MSVC from_chars) were left out. last_commit 2026-08-13 is the master branch; the default branch (develop) last commit is 2026-07-09. Both are active, so the field was left unchanged.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/boostorg/charconv>
  - <https://github.com/boostorg/charconv/blob/master/doc/charconv/benchmarks.adoc>
  - <https://github.com/boostorg/charconv/tree/master/test>
  - <https://github.com/boostorg/charconv/blob/master/test/Jamfile>
- **Sources the enricher read:**
  - <https://github.com/boostorg/charconv>
  - <https://github.com/boostorg/charconv/blob/master/README.md>
  - <https://github.com/boostorg/charconv/blob/master/doc/charconv/benchmarks.adoc>
  - <https://github.com/boostorg/charconv/blob/master/doc/charconv/overview.adoc>
  - <https://github.com/boostorg/charconv/blob/master/doc/charconv/build.adoc>
  - <https://github.com/boostorg/charconv/tree/master>
  - <https://github.com/boostorg/charconv/issues?q=performance>
  - <https://github.com/boostorg/charconv/issues?q=label%3Abug>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/boostorg/charconv`) · [data/wave1/enrich/raw/github_com_boostorg_charconv.json](../../../data/wave1/enrich/raw/github_com_boostorg_charconv.json) (enrichment confidence 0.88)

</details>
