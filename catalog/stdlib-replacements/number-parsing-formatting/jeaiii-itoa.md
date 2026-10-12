# jeaiii/itoa

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only branchless integer-to-ASCII conversion, \~7-9x faster than sprintf/MSVC _itoa, \~1.6-1.8x vs {fmt}.

| | |
|---|---|
| **Beats** | sprintf (C standard library, MSVC CRT) and MSVC _itoa/_ui64toa in the README's release charts; {fmt} in the godbolt table. No std::to_chars comparison exists. |
| **Claimed result** | README godbolt table (debug-built Google Benchmark): BM_jea 10.2ns vs BM_fmt 16.6ns (\~1.6x). README-embedded release win64 VC2019 chart (data in docs/release_win64_vc2019.js, y-axis 'cycle count'), uniform-random-length column: u32toa jeaiii::to_text 20.5 vs sprintf 160.5 (\~7.8x), vc/_ui64toa 174.5 (\~8.5x), fmt 33.5 (\~1.6x); u64toa 32.75 vs sprintf 226.75 (\~6.9x), vc 312 (\~9.5x), fmt 58 (\~1.8x). The README also says the latest version is '25% faster' than before. |
| **Workload** | u32toa/u64toa conversion of integers with 1..10 (u32) or 1..20 (u64) digits plus a uniform-random-digit-length case. Measured with the author's fork of miloyip/itoa-benchmark (jeaiii/itoa-benchmark), release win64 VC2019, against sprintf, MSVC _ui64toa, {fmt} and other itoa variants. There is also a debug-built Google Benchmark on godbolt vs {fmt}. |
| **Metric** | latency |
| **Compiler and flags** | Release win64 Visual C++ 2019 for the chart data (exact flags not stated on the page). The godbolt {fmt} comparison used Google Benchmark compiled in debug. |
| **Adoption** | 254 stars; algorithm write-up by dragonbox author Junekey Jeon; widely referenced across itoa benchmark shootouts (miloyip/itoa-benchmark, TobiSchluter/itoa-benchmark forks) |
| **Last commit** | 2022-11-24 |
| **Links** | [repository](https://github.com/jeaiii/itoa) · [benchmark](https://github.com/jeaiii/itoa/blob/main/README.md) |

## Verdict

Author-run release-mode benchmark (Visual C++ 2019, win64, hardware unstated) using jeaiii's fork of miloyip/itoa-benchmark shows, on uniform-random-digit-length inputs, u32toa at 20.5 cycles vs sprintf's 160.5 and MSVC _ui64toa's 174.5 (\~8x), and vs {fmt}'s 33.5 (\~1.6x); u64toa is 32.75 cycles vs sprintf's 226.75 and MSVC's 312 (\~7-9x), and vs {fmt}'s 58 (\~1.8x). A separate debug-built Google Benchmark on godbolt, which the author explicitly disclaims as not a good benchmark, shows 10.2ns vs {fmt}'s 16.6ns. No comparison against std::to_chars is published anywhere in the repo.

## Use it when

- Hot paths that serialize many plain base-10 integers to text (logging, JSON/CSV encoders, protocol formatting) on MSVC, clang, or gcc
- Fixed 8/16/32/64-bit integer types where you control the destination buffer size and will add the null terminator yourself
- Workloads with uniform or skewed digit-length distributions (IDs, counters) where branch-prediction-unfriendly random lengths matter
- Need a single self-contained, zero-dependency header (not even &lt;cstdint&gt;) that works from C++11 up, easy to vendor
- You're comfortable auditing/patching abandonware yourself rather than depending on upstream maintenance

## Skip it when

- Need floating-point-to-string conversion; integers only, no float/double support at all
- Need std::to_chars' API contract: error_code / bool success return, [first,last) bounds-checked span; this header has neither
- Need guaranteed-correct output without your own verification: the repo has shipped at least two silent, large-magnitude correctness bugs on big 64-bit inputs (issues #12, #18), both fixed only because users noticed
- Want zero-padding or fixed-point/decimal formatting; explicitly requested in issue #15 and not implemented
- Need a plain-C API; this is C++ template code with no official C binding (issue #10 still open, unresolved)

## How it is fast

Uses a per-digit-length unrolled code path chosen by a small binary-search branch tree on the number's decimal length, so short numbers take fewer branches than long ones instead of looping once per digit. Digits are produced two at a time via fixed-point multiply-shift arithmetic against a 100-entry '00'-'99' ASCII lookup table, avoiding per-digit division; only one true integer divide is used, to split 64-bit values into two 8-digit halves. The fixed-point constants follow the classic multiply-by-2^k/10^n itoa trick, refined using the mathematical analysis in dragonbox author Junekey Jeon's write-up, which removed a redundant addition.

## Compared with alternatives

Pick jeaiii/itoa over CharConv.h (rigtorp) or c4core when you want the smallest possible single header with zero includes and don't need from_chars/parsing or float formatting. Pick c4core or Boost.Charconv instead when you need a maintained, std::to_chars/from_chars-compatible API with float support and bounds-checked spans.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 (compiles on clang, MSVC, and gcc per README) |
| **Platforms** | any (no architecture-specific intrinsics in the header; author's benchmarks are x86/x64 Windows/VC2019) |
| **Thread safety** | not documented explicitly, but the function only reads compile-time constexpr tables and writes to the caller-supplied buffer, so concurrent calls with distinct buffers are safe |
| **Drop-in for the baseline** | partial — explain: same 'write digits, return end pointer' shape as std::to_chars, but no error_code, no bounds checking against a span, and no automatic null termination |

## Gotchas

- Output is not null-terminated; caller must write '\0' at the returned pointer (see test/main.cpp's to_string wrappers)
- No bounds checking: caller must size the buffer for the worst case (up to 20 digits + sign for 64-bit) or risk a buffer overflow
- History of silent large-magnitude correctness bugs on 64-bit inputs (issue #12: off by 10,000,000 on a 19-digit value; issue #18: wrong values near a specific 11-digit range), both fixed before the final 2022-11-24 commit but with no maintainer left to catch new regressions
- Repo contains multiple header variants (include/itoa/jeaiii_to_text.h is current; itoa/to_text_from_integer.h and itoa/int_to_chars_jeaiii.h are older macro-based versions) — include the one under include/itoa/, not the legacy ones

## Caveats and trade-offs

The in-repo godbolt comparison vs {fmt} is disclaimed by the author (Google Benchmark compiled in debug). The README says the release VC2019 charts are 'much more accurate'. Those charts compare against sprintf and MSVC _ui64toa (C runtime) but not std::to_chars. They are author-run, with hardware and flags unstated. The src/to_chars.cpp in the benchmark fork is jeaiii's own to_chars implementation, not std::to_chars.

Integers only, no floating point; single header, no dependencies; the classic itoa-benchmark shootout this project descends from (miloyip/itoa-benchmark) predates C++17 and explicitly disables the C++ standard-library competitors (ostringstream/to_string) by default, and neither it nor jeaiii/itoa's own README includes a std::to_chars comparison.

## Maintenance

Abandoned since its last commit on 2022-11-24 with no tagged releases; MIT-licensed and small enough (\~200-line single header) to vendor and patch yourself, but its history of correctness bugs on large 64-bit values means you should add your own exhaustive round-trip test before trusting it in production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README godbolt table (BM_jea 10.2ns vs BM_fmt 16.6ns) is disclaimed by the author as a debug-built Google Benchmark, so it is capped at C. The README also embeds a release win64 VC2019 chart, made with the author's fork of miloyip/itoa-benchmark (src/sprintf.cpp, src/vc.cpp), that compares against sprintf and MSVC _ui64toa. That run states no hardware and no flags, so it is still not A.
- **Verifier notes:** Baseline was a guess (std::to_chars). The README chart actually shows a win vs sprintf/MSVC _ui64toa, roughly 7-9x on random-length inputs, and \~1.6-1.8x vs {fmt}. baseline_stdlib is set to MSVC because the run is VC2019 win64, but sprintf/_ui64toa come from the MSVC C runtime (UCRT), not the STL headers proper. Metadata checked: MIT, 254 stars, last commit 2022-11-24, not a fork, not archived. [orchestrator: baseline_in_list=false, baseline outside category list]
- **Fields the verifier corrected:** `baseline`, `compared_against_cpp_std_directly`, `baseline_stdlib`, `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jeaiii/itoa>
  - <https://github.com/jeaiii/itoa/blob/main/README.md>
  - <https://github.com/jeaiii/itoa/blob/main/chart.png>
  - <https://github.com/jeaiii/itoa/blob/main/docs/release_win64_vc2019.js>
  - <https://jeaiii.github.io/itoa/>
  - <https://github.com/jeaiii/itoa-benchmark>
  - <https://api.github.com/repos/jeaiii/itoa-benchmark/contents/src/to_chars.cpp>
  - <https://api.github.com/repos/jeaiii/itoa-benchmark/contents/src/vc.cpp>
  - <https://api.github.com/repos/jeaiii/itoa-benchmark/readme>
- **Sources the enricher read:**
  - <https://github.com/jeaiii/itoa>
  - <https://github.com/jeaiii/itoa/blob/main/README.md>
  - <https://github.com/jeaiii/itoa/blob/main/include/itoa/jeaiii_to_text.h>
  - <https://github.com/jeaiii/itoa/blob/main/itoa/to_text_from_integer.h>
  - <https://github.com/jeaiii/itoa/blob/main/test/main.cpp>
  - <https://github.com/jeaiii/itoa/issues>
  - <https://github.com/jeaiii/itoa/issues/18>
  - <https://github.com/jeaiii/itoa/issues/12>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/jeaiii/itoa`) · [data/wave1/enrich/raw/github_com_jeaiii_itoa.json](../../../data/wave1/enrich/raw/github_com_jeaiii_itoa.json) (enrichment confidence 0.35)

</details>
