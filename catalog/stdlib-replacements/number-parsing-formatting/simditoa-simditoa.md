# simditoa

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT OR Apache-2.0` · 🟢 active

> AVX-512 IFMA int64/uint64-to-decimal conversion; 2.8x std::to_chars throughput on 12-19 digit integers, slower at 1-4 digits.

| | |
|---|---|
| **Beats** | std::to_chars |
| **Claimed result** | From the raw google/benchmark max aggregates in RESULTS.md (2026-05-19, derived from page data): default simditoa::to_chars (heterogeneous) vs std::to_chars on the realistic subset: UNIFORM_POS 186.2M vs 54.9M ints/s (3.39x), LOG_HEAVY 135.3M vs 39.6M (3.42x), FIXED:12 189.8M vs 99.9M (1.90x), FIXED:16 189.7M vs 74.0M (2.57x), FIXED:19 186.2M vs 59.4M (3.13x); geomean 176.0M vs 62.5M (2.82x). The specialized homogeneous variant reaches 295.7M / 295.6M / 239.8M at FIXED:12/16/19 (4.04x at 19 digits) but drops to 65.9M on LOG_HEAVY. Batch API (to_chars_batch) geomean 186.1M vs std::to_chars batch 58.0M (3.21x). Signed: UNIFORM 101.2M vs 43.3M (2.34x), LOG 80.1M vs 43.9M (1.83x). Slower than std::to_chars at FIXED:1 (267.3M vs 402.5M) and FIXED:4 (225.4M vs 319.6M), faster at FIXED:8 (225.3M vs 149.5M). Fastest other contender on the realistic subset is yy_itoa (geomean 136.3M; simditoa default 1.29x ahead), and yy_itoa beats simditoa on signed UNIFORM (128.6M vs 101.2M). RESULTS.md's own headline (219M vs 105M geomean) mixes the homogeneous and heterogeneous variants and mislabels columns. |
| **Workload** | github.com/simditoa/benchmarks (benchmarks/\*.cpp, common/bench_data.hpp): 1,000,000 int64 values per distribution (UNIFORM, UNIFORM_POS, LOG, LOG_HEAVY, FIXED:1/4/8/12/16/19) converted into a 32-byte stack buffer, google/benchmark v1.9.5, 10 repetitions, max-throughput aggregate, plus a batch sweep with per-element output buffers for unsigned distributions; simditoa fetched at GIT_TAG main. |
| **Metric** | throughput |
| **Hardware** | GCP c3-standard-8, Intel Xeon Platinum 8481C @ 2.70 GHz (AVX-512 IFMA + VBMI) |
| **Compiler and flags** | CMake Release (-O3 -DNDEBUG) with CMAKE_CXX_FLAGS -mavx512f -mavx512dq -mavx512bw -mavx512vl -mavx512ifma -mavx512vbmi (printed in the run's metadata); compiler not printed, but the public pipeline (terraform/main.tf image ubuntu-os-cloud/ubuntu-2204-lts, scripts/build-and-run.sh apt build-essential) gives Ubuntu 22.04's GCC 11 (derived from public scripts) |
| **Adoption** | 103 stars |
| **Last commit** | 2026-05-19 |
| **Links** | [repository](https://github.com/simditoa/simditoa) · [benchmark](https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/RESULTS.md) |

## Verdict

In the author's separate google/benchmark repo (1,000,000 int64 values per distribution, 10 repetitions, max-throughput aggregate, -O3 plus AVX-512 IFMA/VBMI flags, Ubuntu 22.04 GCC 11 libstdc++, GCP c3-standard-8 with Xeon Platinum 8481C), the default simditoa::to_chars converts 176.0M ints/s vs 62.5M for std::to_chars over UNIFORM_POS, LOG_HEAVY and FIXED:12/16/19 (2.82x geomean; 3.1-3.4x at 18-19 digits). It loses at 1-4 digits and on random-sign int64 to yy_itoa (derived from page data).

## Use it when

- Serializing many large integers (IDs, nanosecond timestamps, Snowflake IDs, counters of 12-19 digits) on Ice Lake or later Intel, or Zen 4 or later AMD, built with -mavx512ifma -mavx512vbmi: about 186-190M ints/s vs std::to_chars 59-100M on FIXED:12/16/19 (Xeon 8481C).
- Mixed-length positive inputs where branch prediction fails: on LOG_HEAVY (40-63 bit values) 135.3M vs 39.6M ints/s for std::to_chars (3.4x) and vs 74.9M for yy_itoa.
- Bulk output of same-length values (fixed-width IDs): to_chars_homogeneous reaches 295.7M ints/s at 12 and 16 digits, and to_chars_batch selects it automatically when at least 95% of a 1% sample share one length.
- Hot JSON, CSV or log writers that already provide at least 21 bytes of slack at the write cursor.

## Skip it when

- Mostly short numbers (1-4 digits): the SIMD setup cost is constant, so the default path is slower than std::to_chars at 1 digit (267.3M vs 402.5M ints/s) and 4 digits (225.4M vs 319.6M), and far behind jeaiii (1,011M) and fmt (986M) at 1 digit.
- Random-sign signed data: the negative-value branch mispredicts, and throughput drops from 186.2M (UNIFORM_POS) to 101.2M ints/s on full-range int64, where yy_itoa is faster (128.6M).
- Portable binaries or generic x86-64 builds: implementation choice is compile-time only (no runtime CPU dispatch). The default CMake build without the AVX-512 flags silently gives the scalar fallback, which was never benchmarked, and a build with the flags crashes with an illegal instruction on CPUs without IFMA/VBMI. MSVC support for the AVX-512 path is not documented (it is gated on __AVX512IFMA__/__AVX512VBMI__ and uses __builtin_unreachable).
- Code that relies on std::to_chars' bounded-buffer contract (returns errc::value_too_large instead of overflowing), or that needs bases other than 10, 8/16/32-bit types or floating point.
- Projects that need a mature dependency: version 0.1.0, 22 commits all between 2026-05-03 and 2026-05-19, no tagged release, no CI workflow in the library repo, and the one outside PR (#7, RISC-V fallback, 2026-06-19) is unmerged.

## How it is fast

It implements Champagne Gareau and Lemire's method (arXiv:2604.26019): the value is broadcast into eight 64-bit lanes, vpmadd52lo multiplies it by the constants floor(2^52/10^k) to get each digit's fractional remainder, and vpmadd52hi multiplies by 10 to pull out the ASCII digit, so 8 digits come out in parallel with no division or lookup table. 16-digit values run two such kernels on the high and low 8-digit halves and gather the bytes with a VBMI vpermt2b permute; 17-20 digit values add a 4-digit scalar tail. The heterogeneous variant uses one 3-way branch plus masked stores (length from a branchless clz-table digit count), and the homogeneous variant uses a 20-way switch with unmasked 16-byte stores.

## Compared with alternatives

Pick it over jeaiii/itoa, {fmt}'s format_int or the SSE2 (Mula) itoa when most values have 9-19 digits and you control the deployment CPU (AVX-512 IFMA): in the same run jeaiii reaches 127.6M and fmt 83.4M ints/s realistic geomean against 176.0M. Pick jeaiii/itoa, which is header-only, portable and 1,011M ints/s at 1 digit, for short or mixed-small numbers or portable builds, and std::to_chars or Boost.Charconv when you need bounds-checked output.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (C++17 standard library only; CMake 3.14+ for the provided build, single source file src/simditoa.cpp) |
| **Minimum toolchain** | C++17; the fast path needs a GCC or Clang that accepts -mavx512f -mavx512dq -mavx512bw -mavx512vl -mavx512ifma -mavx512vbmi (benchmarked with Ubuntu 22.04's GCC 11, derived from the public scripts) |
| **Platforms** | x86-64 with AVX-512 IFMA + VBMI (Ice Lake and later Intel, Zen 4 and later AMD) for the SIMD path; any platform with the portable scalar fallback |
| **Thread safety** | not documented; the functions are stateless (constexpr tables, no global mutable state in the source), so concurrent calls on separate buffers are safe |
| **Drop-in for the baseline** | partial — same job as integer std::to_chars, but the signature is to_chars(value, char\*) returning a length, with no end pointer or error code, base 10 only and int64_t/uint64_t only, so call sites must be rewritten and buffers sized to 21 bytes |

## Gotchas

- Buffer contract: to_chars_homogeneous does full-width 16-byte stores, writing up to 16 bytes from the start of the buffer even for a 9-digit number (the extra bytes are zeros). Appending into a larger output buffer therefore clobbers whatever follows the digits unless 21 bytes of slack are reserved; the default heterogeneous path uses masked stores and writes only the digits. The usage comment in include/simditoa.h names simditoa::MAX_INT64_CHARS, which does not exist; the constant is MAX_DIGITS.
- Benchmark presentation, not code: RESULTS.md's prose and tables were written by OpenAI gpt-5.4-mini and mislabel columns (the 'UNIFORM_POS' column holds FIXED:1 data, and the 219M headline geomean mixes the homogeneous and heterogeneous variants); the README's 194.8M and 269.7M figures come from an earlier LLM summary. Use the raw google/benchmark output. Recomputed from it, the default heterogeneous path has a realistic-subset geomean of 176.0M vs std::to_chars 62.5M (2.82x), with yy_itoa next at 136.3M (derived from page data).
- No harness defect found that favours simditoa: every contender uses the same 1M pre-generated values, the same 32-byte stack buffer with DoNotOptimize, and the same global AVX-512 flags. simditoa is linked as a separate static library, so each call is out of line (no LTO), while std::to_chars is inlined from the header. Two limits remain: only one CPU (Sapphire Rapids) and one standard library (GCC 11 libstdc++) were measured, and the library was fetched at GIT_TAG main, so the exact commit measured is not recorded.
- The single-value numbers are throughput of independent conversions in a tight loop. With per-element output buffers (batch sweep) the realistic geomean is 186.1M vs 58.0M (3.21x), but to_chars_batch on UNIFORM_POS (158.6M) is slower than single calls (186.2M). The tests (basic_test.cpp: edge cases, powers of 10, 100,000 random values, buffer isolation) only exercise the AVX-512 path when built with the flags; a Python model of the 8-digit IFMA formula matched exact digits on 700,000 inputs in this review.

## Known shortcomings

- Raised C to A (public google/benchmark repo, Xeon 8481C, flags printed, GCC 11 from the Ubuntu 22.04 provisioning scripts), but the LLM-written RESULTS.md mislabels columns (its UNIFORM_POS column is FIXED:1); re-derived from raw output: 2.82x geomean vs libstdc++ std::to_chars, 3.4x on UNIFORM_POS/LOG_HEAVY, slower at 1-4 digits. Filed under number-parsing-formatting.
- Domain set to stdlib-replacements to match the number-parsing-formatting category.
- No correctness or harness bug: the same inputs and flags for all contenders, simditoa called out of line (no LTO), and a Python model of the 8-digit IFMA kernel matched 700,000 inputs. Shortcomings: compile-time dispatch only (the default CMake build gives an unbenchmarked scalar fallback; the AVX-512 build crashes on CPUs without IFMA/VBMI); random-sign int64 drops from 186.2M to 101.2M ints/s where yy_itoa is faster; the homogeneous variant writes 16 bytes regardless of length; the signature is not std::to_chars-compatible; version 0.1.0 by one author with no CI or releases.

## Caveats and trade-offs

First-party benchmark (separate repo by the same author, run by a GitHub Actions workflow on one GCP c3-standard-8 VM). The RESULTS.md prose and tables were written by OpenAI gpt-5.4-mini and mislabel columns: per the D_ enum in common/bench_data.hpp (dist 3 = UNIFORM_POS, dist 4 = LOG_HEAVY), the headline 'UNIFORM_POS' column actually holds FIXED:1 numbers and the 'LOG_HEAVY' column holds UNIFORM_POS numbers, and simditoa's FIXED:12/16/19 headline cells come from the specialized homogeneous variant, so the 219M geomean mixes variants; use the raw output at the bottom of the file. The main README's 2026-05-07 figures (194.8M geomean, 269.7M 'UNIFORM_POS') come from an earlier LLM summary and likely share the mislabel. std::to_chars was only measured from GCC 11's libstdc++; libc++ and MSVC STL were not tested. Requires AVX-512 IFMA + VBMI (Ice Lake or Zen 4 and later); the scalar fallback was not benchmarked. Slower than std::to_chars at 1-4 digit outputs, and slower than jeaiii, yy_itoa, rapidjson and fmt at 1-8 digits. Algorithm from Champagne Gareau & Lemire, arXiv:2604.26019 (not checked; arXiv blocked here).

Fast path needs AVX-512 IFMA + VBMI (Ice Lake and later, Zen 4 and later), otherwise a portable scalar fallback; constant SIMD setup cost so short outputs are slower than scalar methods; uint64 batch API. Based on arXiv:2604.26019 (Champagne Gareau and Lemire), a preprint that was not opened.

## Maintenance

The library is new and small (version 0.1.0, written by one author in May 2026 with some AI co-authored commits, no release tags and no activity since 2026-05-19) but MIT OR Apache-2.0 and one source file, so it is easy to vendor. No correctness or harness defect was found behind the numbers; the RESULTS.md and README summaries are LLM-written and mislabelled, so quote the raw output.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the benchmark code is public (github.com/simditoa/benchmarks: benchmarks/std_to_chars.cpp, benchmarks/simditoa.cpp, common/bench_data.hpp, google/benchmark v1.9.5), RESULTS.md carries the raw output with CPU model (Xeon Platinum 8481C) and cxx_flags, and the public pipeline pins the compiler (terraform/main.tf image ubuntu-os-cloud/ubuntu-2204-lts plus apt build-essential in scripts/build-and-run.sh, i.e. Ubuntu 22.04's GCC 11 and libstdc++, derived from public scripts). The LLM-written summary tables mislabel columns, so claimed_speedup is re-derived from the raw output.
- **Verifier notes:** Real win against std::to_chars (2.82x geomean on the realistic subset for the default entry point, 3.1-3.4x on 18-19 digit inputs), but the record's per-workload numbers inherited the LLM summary's mislabelled columns (its 'slower on UNIFORM_POS' row is really FIXED:1); claimed_speedup rewritten from the raw output. Tier raised to A because code, flags, CPU model and the provisioned compiler are all public; cap at C if a printed compiler version is required. Metadata confirmed: MIT OR Apache-2.0, 103 stars, last commit 2026-05-19, active. Fits number-parsing-formatting (where jeaiii/itoa is filed) better than simd-intrinsics-libraries.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-26 (wave 13); orchestrator domain fix 2026-10-11; enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/README.md>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/README.md>
  - <https://github.com/simditoa/benchmarks>
  - <https://github.com/simditoa/benchmarks/tree/main/benchmarks>
  - <https://github.com/simditoa/benchmarks/tree/main/common>
  - <https://github.com/simditoa/benchmarks/commits/main>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/common/bench_data.hpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/std_to_chars.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/simditoa.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/simditoa_homogeneous.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/script.sh>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/scripts/run-bench.sh>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/scripts/build-and-run.sh>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/terraform/main.tf>
  - <https://github.com/simditoa/simditoa>
  - <https://github.com/simditoa/simditoa/commits>
- **Sources the enricher read:**
  - <https://github.com/simditoa/simditoa>
  - <https://github.com/simditoa/simditoa/commits/main>
  - <https://github.com/simditoa/simditoa/issues?q=is%3Aissue>
  - <https://github.com/simditoa/simditoa/pulls?q=is%3Apr>
  - <https://github.com/simditoa/simditoa/tree/main/src>
  - <https://github.com/simditoa/simditoa/tree/main/include>
  - <https://github.com/simditoa/simditoa/tree/main/include/simditoa>
  - <https://github.com/simditoa/simditoa/tree/main/tests>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/README.md>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/include/simditoa.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/include/simditoa/base.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/include/simditoa/common_defs.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/include/simditoa/compiler_check.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/include/simditoa/implementation_detection.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/include/simditoa/portability.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/include/simditoa/simditoa_version.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/src/simditoa.cpp>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/src/avx512.cpp>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/src/fallback.cpp>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/src/digit_count.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/src/digit_utils.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/src/base.h>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/tests/basic_test.cpp>
  - <https://raw.githubusercontent.com/simditoa/simditoa/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/common/bench_data.hpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/simditoa.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/simditoa_homogeneous.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/simditoa_batch.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/std_to_chars.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/std_to_chars_batch.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/yy_itoa.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/jeaiii_itoa.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/null.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/scripts/build-and-run.sh>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/scripts/run-bench.sh>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/simditoa/simditoa`) · [data/wave13/enrich/raw/github_com_simditoa_simditoa.json](../../../data/wave13/enrich/raw/github_com_simditoa_simditoa.json) (enrichment confidence 0.8)

</details>
