# fast_float

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 OR MIT OR BSL-1.0` · 🟢 active

> Header-only C++ from_chars for float/double/int; 3-5x faster than glibc strtod, exact IEEE rounding.

| | |
|---|---|
| **Beats** | std::stod/strtod |
| **Claimed result** | 'Three to five times faster than the strtod function available in the GNU standard library... often more than twice as fast as the state-of-the-art abseil library' (verbatim from paper Section 12); e.g. Table 9, Intel Skylake, canada dataset: 45 Mfloat/s (fast_float) vs 9.0 Mfloat/s (strtod) = 5x (derived from page data) |
| **Workload** | Parsing 64-bit IEEE-754 floating point numbers with fast_float::from_chars vs. the system strtod (glibc, default locale) over three datasets - a 111k-line real-world 'canada' JSON coordinate corpus, synthetic uniform floats in [0,1), and synthetic 32-bit integers - run single-threaded on four different CPU architectures (millions of floats/sec). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 (Skylake x64, 3.7GHz effective); also tested on AMD EPYC 7262 (Zen2 x64, 3.39GHz), an Ampere ARM server (Skylark aarch64, 3.2GHz), and IBM POWER9 (ppc64le, 3.77GHz) - see Table 8/9 of the paper |
| **Compiler and flags** | GNU GCC 10.2, -O3 -DNDEBUG, single-threaded, in a privileged Ubuntu 20.10 Docker container on Linux (main Table 9); also MSVC 19.26.28806 /O2 /Ob2 /DNDEBUG (Table 13) and Apple clang 12.0.0 -O3 -DNDEBUG (Fig. 3) |
| **Adoption** | 2.1k stars; part of GCC 12's std::from_chars, and used in Chromium, WebKit/Safari, MySQL, DuckDB, Boost JSON, Blender, Apache Arrow, Google Jsonnet, ClickHouse |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/fastfloat/fast_float) · [benchmark](https://arxiv.org/abs/2101.11408) |

## Verdict

Peer-reviewed benchmark (Lemire, Software: Practice and Experience 51(8), 2021) measured fast_float::from_chars against glibc strtod, single-threaded, GCC 10.2 -O3 -DNDEBUG, on an Intel Skylake i7-6700: 45 Mfloat/s vs 9.0 Mfloat/s (5x) on the 111k-line 'canada' JSON coordinate corpus (Table 9); comparable 3-5x wins held on AMD Zen2, ARM Ampere, and IBM POWER9 CPUs, and against MSVC STL's std::from_chars on an Intel i7-7700K (Table 13).

## Use it when

- Parsing large volumes of floats/doubles from text (JSON, CSV, scientific/columnar data) where strtod or std::from_chars throughput is a bottleneck
- Header-only C++11+ codebases that want a from_chars-shaped API without adding a build dependency
- Need locale-independent, correctly-rounded parsing with round-to-even tie-breaking
- Need JSON, JavaScript-literal, or Fortran-literal number grammars without hand-rolling the format checks
- Compile-time (constexpr) float parsing in C++20

## Skip it when

- Need long double parsing - unsupported; only float, double, and fixed-width float16/32/64/bfloat16 are covered
- Need hexadecimal floating-point literals - decimal format only
- Building with -ffast-math: infinity()/NaN handling is documented-incompatible in open issue #397 (unresolved as of 2026-09-24)
- Only parsing a handful of floats and every byte of compile time / include overhead matters, since it is a template-heavy header-only include vs. a plain libc call
- Want locale-aware parsing out of the box - the default from_chars is locale-independent; locale behavior requires the separate from_chars_advanced API

## How it is fast

Uses the Eisel-Lemire algorithm (named directly in a comment in include/fast_float/parse_number.h): a fast path that combines the decimal significand with precomputed power-of-five tables to compute the correctly-rounded binary value from one or two 64-bit multiplications (compute_product_approximation in decimal_to_binary.h). When that approximation cannot be proven correct, which is rare, it falls back to exact big-integer digit comparison (bigint.h / digit_comparison.h) instead of a slow generic parser, so the common case stays branch-light and allocation-free.

## Compared with alternatives

fast_float parses text to binary (beats strtod/std::from_chars); Dragonbox, Ryu, and {fmt} format binary to text (beat sprintf/std::to_chars) - they solve the opposite problem, so pick fast_float for the parsing side of a pipeline and pair it with one of those for the formatting side rather than treating them as substitutes.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 for the core library (CMakeLists.txt sets FASTFLOAT_CXX_STANDARD 11 by default); C++20 needed for constexpr parsing; CMake 3.14+ for the build/install targets |
| **Platforms** | Windows/MSVC, macOS, Linux, FreeBSD per README; supports big- and little-endian, 32-bit and 64-bit systems; CI also exercises ARM, RISC-V, and s390x (big-endian) |
| **Thread safety** | not documented explicitly, but from_chars/from_chars_advanced are stateless, non-throwing, and non-allocating (per README), with no shared mutable state, so concurrent calls on independent buffers are safe |
| **Drop-in for the baseline** | partial - explain: call shape tracks C++17 std::from_chars (same argument order, chars_format enum), but the result is returned via from_chars_result{ptr, ec} rather than strtod's return-value+errno+endptr convention, so strtod call sites need updating, not just relinking |

## Gotchas

- -ffast-math builds break infinity/NaN handling (open issue #397 as of 2026-09-24; no fix merged yet)
- Locale-dependent decimal separators (e.g. comma) require the separate from_chars_advanced + parse_options call, not the default from_chars
- chars_format::json rejects bare inf/nan by default; use the non-standard json_or_infnan variant to allow them
- v8.2.0 had a big-endian regression on s390x (issue #354, closed/fixed) - use a current release rather than pinning that tag if targeting big-endian

## Caveats and trade-offs

Peer-reviewed paper (Daniel Lemire, Software: Practice and Experience 51(8), 2021). Benchmark code: github.com/lemire/simple_fastfloat_benchmark (git tag v0.1.0). The main Linux comparison is against glibc strtod, because GCC/libstdc++ had no float std::from_chars at the time. The paper also tests Visual Studio 2019's std::from_chars (MSVC STL) and strtod on an Intel 7700K (Table 13, canada: 37 vs 6.7 Mfloat/s for from_chars, \~5.5x, derived from page data), plus Apple's strtod on an M1 (Fig. 3). libc++ from_chars was not tested. Ratios vary by dataset: the integer dataset shows smaller wins (e.g. 61 vs 20 Mfloat/s on Skylake).

Only supports float/double (and, with recent extensions, fixed-width float16/32/64/bfloat16) and integer types, not long double; header-only by design so adds compile-time/include overhead vs a plain libc call; locale-independent by default (needs from_chars_advanced for locale-style decimal separators).

## Maintenance

Actively maintained (last commit 2026-09-23, tagged v8.3.0), triple-licensed Apache-2.0/MIT/BSL-1.0, header-only and small enough to vendor; already embedded in GCC 12's std::from_chars and used by Chromium, WebKit/Safari, MySQL, DuckDB, Boost.JSON, ClickHouse, Blender, and Apache Arrow, which makes it low-risk to adopt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** The arXiv paper (published in SPE 51(8), 2021) compares against glibc strtod in Section 12. Its setup names GCC 10.2 with -O3 -DNDEBUG, and Table 8 lists the CPUs (i7-6700, EPYC 7262, Ampere Skylark, POWER9). The benchmark code is public at lemire/simple_fastfloat_benchmark (tag v0.1.0 exists). Table 9 shows Skylake canada at 45 vs 9.0 Mfloat/s.
- **Verifier notes:** The Section 12 quote and the Table 9 Skylake canada numbers (45 vs 9.0) are verbatim in the paper. The existing caveat wrongly said MSVC STL was not tested, because Table 13 does test it. The license is triple (Apache/MIT/Boost) per the README and LICENSE-\* files, not only Apache-2.0. Metadata checked: 2114 stars, last commit 2026-09-23, active.
- **Fields the verifier corrected:** `license`, `baseline_stdlib`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2101.11408>
  - <https://github.com/fastfloat/fast_float>
  - <https://github.com/lemire/simple_fastfloat_benchmark>
- **Sources the enricher read:**
  - <https://github.com/fastfloat/fast_float>
  - <https://github.com/fastfloat/fast_float/blob/HEAD/README.md>
  - <https://github.com/fastfloat/fast_float/blob/HEAD/CMakeLists.txt>
  - <https://github.com/fastfloat/fast_float/blob/HEAD/SECURITY.md>
  - <https://github.com/fastfloat/fast_float/blob/HEAD/include/fast_float/fast_float.h>
  - <https://github.com/fastfloat/fast_float/blob/HEAD/include/fast_float/decimal_to_binary.h>
  - <https://github.com/fastfloat/fast_float/blob/HEAD/include/fast_float/bigint.h>
  - <https://github.com/fastfloat/fast_float/blob/HEAD/include/fast_float/parse_number.h>
  - <https://github.com/fastfloat/fast_float/issues/397>
  - <https://github.com/fastfloat/fast_float/issues?q=bug>
  - <https://arxiv.org/abs/2101.11408>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/fastfloat/fast_float`) · [data/wave0-seed/enrich/raw/github_com_fastfloat_fast_float.json](../../../data/wave0-seed/enrich/raw/github_com_fastfloat_fast_float.json) (enrichment confidence 0.9)

</details>
