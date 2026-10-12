# fastcpp::str::parse_u64 / u64_to_chars (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only uint64 decimal parse (SWAR) and format (two-digit table): \~3x strtoull/snprintf, 1.5x from_chars, 1.2x to_chars.

| | |
|---|---|
| **Beats** | strtoull (parse_u64), snprintf (u64_to_chars) |
| **Claimed result** | parse_u64: 2.98x vs strtoull (12.306ns vs 36.713ns); 1.49x vs std::from_chars (18.337ns) and 11.5x vs std::istringstream (141.749ns) (derived from page data). u64_to_chars: 3.12x vs snprintf (16.624ns vs 51.83ns); 1.82x vs std::to_string (30.318ns) and 7.91x vs std::ostringstream (131.548ns) (derived from page data); only \~1.27x vs std::to_chars (21.074ns), which results/fastest.json itself flags: 'HONEST CAVEAT ... Kept as a readable reference implementation, not as an improvement on the standard library.' |
| **Workload** | bench/bench_doing_less.cpp parses 20,000 uint64 values from decimal text (fastcpp::str::parse_u64, SWAR 8-digit-word decode) and formats 20,000 uint64 values to decimal text (fastcpp::str::u64_to_chars, 2-digit table), single-threaded, minimum-of-7-samples timing. |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz (AVX2, SSE4.2, BMI2), 4 cores, Ubuntu 24.04 / Linux 6.18, shared cloud VM |
| **Compiler and flags** | gcc 13.3.0, -O2 -g -DNDEBUG -std=c++20 -march=native (RelWithDebInfo), commit dfa74f2 (run id '2026-09-02-core') |
| **Adoption** | 0 stars (private repository) |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](private:developer-source) · [benchmark](private:developer-source/blob/main/results/fastest.json) |

## Verdict

First-party numbers from results/fastest.json (run 2026-09-02-core, commit dfa74f2, gcc 13.3.0 -O2 -march=native -std=c++20 with libstdc++, Intel Xeon @ 2.10GHz shared cloud VM, minimum of 7 samples) cover two single-threaded workloads. Parsing 20k std::to_string'd random uint64 values took 12.3 ns each, against 36.7 ns for strtoull (2.98x) and 18.3 ns for std::from_chars; formatting 20k random uint64 values took 16.6 ns each, against 51.8 ns for snprintf (3.12x) and 21.1 ns for std::to_chars. A later CI smoke run at 2fa7d3d (-O3, GitHub x86-64 runner, same gcc, all checksums agreeing) gives the same ordering: parsing 9.9 / 29.5 / 14.2 ns (parse_u64 / strtoull / from_chars) and formatting 13.4 / 44.7 / 15.7 ns (u64_to_chars / snprintf / to_chars), though the workflow itself says CI runners cannot measure reliably.

## Use it when

- Hot loops that parse long unsigned decimal fields (IDs, nanosecond timestamps, counters with 16+ digits) out of text you have already tokenized, such as CSV, log or wire-protocol parsers where std::from_chars is the measured bottleneck.
- Fixed-width 8-digit fields whose shape you have already validated (YYYYMMDD dates, fixed protocol headers): parse_exactly_8_digits is the branch-free kernel with no checks.
- Output paths that still use snprintf("%llu"), std::to_string or ostringstream to write integers into a buffer you own (3.1x faster than snprintf, 1.8x faster than to_string and 7.9x faster than ostringstream on this benchmark).
- When you want a tiny, dependency-free, noexcept, allocation-free piece of code to vendor: two \~125-line headers plus fastcpp/core/bits.hpp and core/macros.hpp, MIT-licensed.

## Skip it when

- You already use std::from_chars, std::to_chars or {fmt}. The remaining margin is about 1.5x (parse) and 1.2-1.3x (format) on one benchmark, and results/fastest.json itself calls u64_to_chars 'a readable reference implementation, not an improvement on the standard library.'
- Short numbers. Only uniformly random uint64 values were measured, and about 95% of those have 19-20 digits. Inputs under 8 digits never reach the SWAR path, and their speed was not measured.
- You need strtoull semantics: leading-whitespace skipping, bases other than 10 or 0x/0 prefixes, locale handling, errno, or an end pointer that separates 'no digits' from 'overflow'.
- Signed parsing, until it is fixed. parse_i64 negates a signed int64 at parse.hpp:106, which is undefined behavior for "-9223372036854775808", and the repo's own asan+ubsan CI job fails on exactly that line. It happens to give the right value in optimized gcc builds.
- You need a maintained, public dependency. The repo is private with 0 stars, has 13 commits made over 2-4 Sept 2026, has no releases, and every CI run is red (other jobs also fail to build the vendored xsimd benchmarks).

## How it is fast

parse_u64 uses SWAR (SIMD within a register). It memcpy-loads 8 bytes as one uint64, checks that all eight are '0'-'9' with a single add-and-mask test, and combines them in three multiply-shift-mask rounds (8 one-digit lanes, then 4 two-digit, 2 four-digit, 1 value). Any remaining digits (fewer than 8) go through a scalar loop. u64_to_chars counts the digits first with `bit_width*1233>>12` plus one powers-of-10 table correction, then divides by 100 and writes two characters per step from a 200-byte '00'..'99' table straight into their final positions. Most of the gain over strtoull and snprintf comes from skipping locale, whitespace, base-prefix, errno and format-string work. The repo's own notes say libstdc++'s to_chars already uses the same table-plus-digit-count method, which is why that margin is only \~1.2x.

## Compared with alternatives

No siblings catalogued yet. The realistic competitors are std::from_chars (1.49x slower here) and std::to_chars (1.27x slower), and both offer end-pointer bounds checks and error codes that this lacks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for these headers beyond fastcpp/core/bits.hpp and fastcpp/core/macros.hpp from the same repo; note that the repo's CMake target fastcpp::fastcpp links every vendored third_party library (fmt, phmap, xsimd, simdjson, yyjson, CRoaring, ...), so copying the four headers is the lighter route |
| **Minimum toolchain** | C++20 for these headers (&lt;bit&gt; std::bit_width, std::is_constant_evaluated, constexpr-lambda tables). The repo as a whole targets C++23, and its README lists gcc 13+, clang 17+ and MSVC 19.35+. Benchmarked with gcc 13.3 at -std=c++20. |
| **Platforms** | Portable C++ with no intrinsics, but little-endian only: the SWAR decode has no byte swap. Tests pass in CI only on x86-64 Linux with gcc 13.3. The macOS arm64 AppleClang 21 job compiles test_strings, but its tests never run because the build fails in the xsimd benchmarks. |
| **Thread safety** | not documented; the functions are stateless and noexcept (they touch only constexpr lookup tables and caller-owned buffers), so concurrent calls are safe by construction |
| **Drop-in for the baseline** | no |

## Gotchas

- parse_u64 stops silently at the first non-digit ("12345abc" gives 12345 with consumed=5), and consumed=0 is returned for empty input, a leading non-digit and overflow alike. Check `consumed == size` if the whole field must be numeric.
- The overflow guard in the 8-digit loop (parse.hpp:69) is conservative. It rejects a value &gt; 184467440736 at a word boundary, even when the next word would still fit. As a result, values from 18446744073700000000 to UINT64_MAX written with exactly 4 (or 12, 20, ...) leading zeros are reported as overflow. This comes from modeling the source, and the tests do not cover it.
- u64_to_chars and i64_to_chars do no bounds checking. The caller must provide 20 and 21 writable bytes respectively, no NUL is written, and the length is the return value, unlike std::to_chars, which takes an end pointer.
- The SWAR decode expects the first digit in the low byte of a plain memcpy load, so it is wrong on big-endian targets. parse_exactly_8_digits also reads 8 bytes unconditionally and does no validation.

## Caveats and trade-offs

PRIVATE repo, readable only via the authenticated gh CLI (private:developer-source), not publicly browsable, so capped below tier A even though results/fastest.json states full compiler/flags/CPU/commit. include/fastcpp/string/parse.hpp:106, inside parse_i64 (`-static_cast<std::int64_t>(magnitude.value)`), overflows on signed negation when the magnitude is 2^63 (INT64_MIN text). CI confirms it: the asan+ubsan job's test_strings fails with 'parse.hpp:106:31: runtime error: negation of -9223372036854775808 cannot be represented in type long int' (run 33828450197 at 2fa7d3d), and that job has failed on all 21 CI runs. That contradicts the README's claim of INT64_MIN round-trips and UBSan-clean tests. parse.hpp has been touched only by its introducing commit 9e6b8a6 (2026-09-02) out of the repo's 13 commits, so it is unfixed. The workload favors SWAR: inputs are std::to_string of uniformly random 64-bit values, so nearly all are 19-20 digits (two full 8-digit words), and short numbers are not measured. parse_u64 is not a drop-in strtoull: no whitespace skipping, sign, base prefix, locale or errno. Shared cloud VM: results/fastest.json's own caveat says absolute ns are not stable across runs, so only ratios within one row are meaningful.

parse_u64 drops locale handling, leading-whitespace skipping, base-prefix detection and errno that strtoull provides; it requires an 8-byte unaligned load per word (load_unaligned) and only accepts ASCII decimal digits, reporting overflow/non-digit input by returning consumed=0 rather than an error code. u64_to_chars needs a caller-provided 20-byte buffer and writes no NUL terminator; digit count is estimated from bit-width via a lookup table rather than computed by division.

## Maintenance

Lives in a PRIVATE repository (private:developer-source, 0 stars, not publicly browsable). The last commit was on 2026-09-04, and the parse/itoa headers are unchanged since the first commit. The code is MIT-licensed and small enough to vendor if you have access, but fix parse_i64's INT64_MIN UB first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** results/fastest.json rows parse_u64 and u64_to_chars (run 2026-09-02-core) give exact ns vs strtoull/snprintf plus std::from_chars/to_chars/to_string/stream alternatives, with gcc 13.3.0, flags, Xeon CPU and commit stated; the bench code (bench/bench_doing_less.cpp bench_parsing/bench_integer_formatting) sits in a PRIVATE repo, so it is not public and cannot be A, and there is no paper or independent suite for B. First-party numbers, so C.
- **Verifier notes:** Every number checks out against results/fastest.json and bench/bench_doing_less.cpp (20k values, min of 7 samples, 30ms budget per bench_harness.hpp). I fixed three things: marked the cross-alternative ratios as derived; the 'HONEST CAVEAT' quote is in results/fastest.json, not the README; the 'single commit in this repo's history' wording was wrong (13 commits exist, only one touches parse.hpp). The UB claim is verified from the CI job log.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <private:developer-source>
  - <private:developer-source/commits/main>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/main/bench/bench_doing_less.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/LICENSE>
  - <private:developer-source/blob/main/include/fastcpp/string/parse.hpp>
  - <private:developer-source/blob/main/include/fastcpp/string/itoa.hpp>
  - <private:developer-source/blob/main/tests/test_strings.cpp>
  - <private:developer-source/blob/main/.github/workflows/ci.yml>
  - <private:developer-source/blob/main/CMakePresets.json>
  - <private:developer-source/actions/runs/33828450197>
  - <private:developer-source/actions/runs/33828450197/job/100886052547>
- **Sources the enricher read:**
  - <private:developer-source>
  - <private:developer-source/tree/main>
  - <private:developer-source/commits/main>
  - <private:developer-source/commits/main/include/fastcpp/string/parse.hpp>
  - <private:developer-source/commits/main/include/fastcpp/string/itoa.hpp>
  - <private:developer-source/blob/main/README.md>
  - <private:developer-source/blob/main/include/fastcpp/string/parse.hpp>
  - <private:developer-source/blob/main/include/fastcpp/string/itoa.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/bits.hpp>
  - <private:developer-source/blob/main/include/fastcpp/core/macros.hpp>
  - <private:developer-source/blob/main/CMakeLists.txt>
  - <private:developer-source/blob/main/CMakePresets.json>
  - <private:developer-source/blob/main/LICENSE>
  - <private:developer-source/blob/main/results/fastest.json>
  - <private:developer-source/blob/main/bench/bench_doing_less.cpp>
  - <private:developer-source/blob/main/bench/bench_harness.hpp>
  - <private:developer-source/blob/main/tests/test_strings.cpp>
  - <private:developer-source/blob/main/tests/CMakeLists.txt>
  - <private:developer-source/blob/main/.github/workflows/ci.yml>
  - <private:developer-source/actions>
  - <private:developer-source/actions/runs/33828450197>
  - <private:developer-source/actions/runs/33828450197/job/100886052547>
  - <private:developer-source/actions/runs/33828450197/job/100886052702>
  - <private:developer-source/actions/runs/33828450197/job/100886052824>
  - <private:developer-source/actions/runs/33828450197/job/100886052892>
  - <private:developer-source/actions/runs/33828450197/job/100886052902>
  - <private:developer-source/issues>
  - <private:developer-source/pulls>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source#number-parsing-formatting`) · [data/wave1-phf/enrich/raw/private_developer_source_number_parsing_formatting.json](../../../data/wave1-phf/enrich/raw/private_developer_source_number_parsing_formatting.json) (enrichment confidence 0.85)

</details>
