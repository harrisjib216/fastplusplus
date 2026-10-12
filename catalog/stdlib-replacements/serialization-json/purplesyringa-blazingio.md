# blazingio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only mmap+SIMD std::cin/cout replacement, \~5x faster than libstdc++ iostream for competitive-programming I/O.

| | |
|---|---|
| **Beats** | iostream (std::cin/std::cout, with sync_with_stdio(false)) |
| **Claimed result** | README: '5x faster than libstdc++ with sync_with_stdio(false);' for reading and writing integers, strings and other primitives (64-bit Linux, gcc, libstdc++). Per-test ratios against iostream_detached in benchmark-results/linux-x86_64.json run from \~1x (line input) to \~80x (bitset input), with a geomean of \~4.7x over 74 test/mode pairs (derived from page data). |
| **Workload** | Reading/writing integers, floating-point numbers, strings, complex numbers, and bitsets via a cin/cout-compatible API, compared to libstdc++ iostream |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest x86_64 runner (per .github/workflows/benchmark.yml); CPU model not stated |
| **Compiler and flags** | g++ -std=c++17 -O2 (per test.py); gcc version not stated (GitHub Actions ubuntu-latest image) |
| **Adoption** | 62 stars |
| **Last commit** | 2024-11-23 |
| **Links** | [repository](https://github.com/purplesyringa/blazingio) · [benchmark](https://raw.githubusercontent.com/purplesyringa/blazingio/master/README.md) |

## Verdict

blazingio's own CI benchmarks it against std::cin/std::cout with sync_with_stdio(false) ('iostream_detached') on GitHub Actions ubuntu-latest x86_64 runners, g++ -std=c++17 -O2 (exact gcc version and CPU model not recorded). Across the 74 read/write test-and-mode pairs in benchmark-results/linux-x86_64.json (opened and spot-checked directly), per-test speedup ranges from about 1x (plain line input) to about 80x (bitset input), geomean about 4.7x; the README's headline '5x faster' figure describes typical integer/string I/O on Linux+libstdc++, with larger geomean speedups reported on macOS/libc++ (\~22x) and Windows/MSVC (\~15x) because those iostream implementations are slower.

## Use it when

- Competitive-programming/judge submissions (Codeforces, ejudge, etc.) where whole-program I/O time is scored and you control the entire source.
- Heavy reading/writing of integers, floats, strings, std::complex&lt;T&gt;, or std::bitset&lt;N&gt; where sync_with_stdio(false) iostream is still the bottleneck.
- Source-size-limited judges: copy-paste the pre-minified blazingio.min.hpp (single file, includes attribution link).
- Target CPU's SIMD extension is known ahead of time -- x86_64/i386 with AVX2 or SSE4.1, or aarch64 with NEON.
- You can tolerate UB on malformed input in exchange for maximum throughput on a single, short-lived process.

## Skip it when

- Any production or user-facing code -- the README explicitly warns invalid input can trigger UB 'including security vulnerabilities'.
- Code needs real std::istream/ostream (templates, manipulators, locale, non-decimal bases, precision/width, exception-based error handling).
- Need &gt;1 ulp float accuracy or std's scientific notation for magnitudes below 1.
- Multi-threaded I/O, or judges/hosts where the assumed SIMD extension might be absent (no runtime detection; wrong assumption is UB).
- Very large output (roughly &gt;0.5 GiB, or &gt;24 MiB on old-style ejudge problems) may be truncated depending on the judge.

## How it is fast

It avoids libstdc++'s buffered streambuf and virtual-dispatch-heavy formatting entirely: the whole input is mmap'd once, then parsed and printed with hand-written SIMD kernels (AVX2, SSE4.1, or NEON -- picked at compile time -- with a scalar SWAR/bit-trick fallback) that scan for whitespace and convert digit or bitset runs a vector-width at a time. There's no locale handling, no exceptions, and no runtime CPU-feature dispatch, and formatting is restricted to fixed decimal, 12-digit-fraction output.

## Compared with alternatives

Only scnlib is a close analog (std::stringstream/sscanf replacement); scnlib returns errors and stays safe on bad input, making it viable in production, while blazingio is faster and cin/cout-syntax-compatible but explicitly UB-on-error and competitive-programming-only -- pick blazingio when you want near-zero code changes from std::cin/cout, need bitset/complex I/O, and can accept unsafe behavior for maximum throughput in a single-shot batch program. The JSON-serialization siblings (cjson.cpp, json.cpp, Cap'n Proto, etc.) solve a different problem (structured data, not whole-program scalar I/O) and aren't real alternatives.

## Integration

| | |
|---|---|
| **Form** | header-only (ships a pre-generated single-file blazingio.min.hpp, plus a Python generator (minimize.py/common.py + config) to build custom platform/feature configurations) |
| **Dependencies** | none beyond the C++ standard library and platform headers (sys/mman.h, unistd.h on Linux/macOS; windows.h, io.h on Windows) |
| **Minimum toolchain** | C++17 (test.py compiles with -std=c++17); CI builds with g++, and also exercises clang/MSVC per repo workflows |
| **Platforms** | x86_64, i386 (AVX2 or SSE4.1 optional), aarch64 (NEON optional) on Linux/macOS/Windows; SIMD ISA is fixed at build time, no runtime CPU dispatch |
| **Thread safety** | not documented; no mutex/atomic/thread_local found in source -- design targets single-threaded, single-pass whole-program I/O |
| **Drop-in for the baseline** | partial — matches operator&gt;&gt;/&lt;&lt; syntax for the types it supports (char, integers, float/double, std::string/string_view, std::complex&lt;T&gt;, std::bitset&lt;N&gt;, std::getline), but blazingio::cin/cout aren't std::istream/ostream, integers can't have a leading '+', only decimal formats parse, precision/width aren't handled, and failures are UB instead of setting failbit |

## Gotchas

- SIMD extension is chosen at compile time via the config file's architecture= list; running on a CPU lacking that extension is undefined behavior, not a graceful fallback.
- No error handling beyond EOF detection (if (std::cin)); malformed input is UB, per the README's own security warning.
- std::bitset&lt;N&gt; input requires at least N input characters -- std zero-pads shorter input, blazingio does not.
- Output is capped at roughly 0.5 GiB generally, 24 MiB on old-style ejudge-based judges.

## Caveats and trade-offs

First-party benchmark run on GitHub Actions runners. The raw data and benchmark code are public, but no CPU model or compiler version is given. The headline 5x is for Linux libstdc++. Raw data also covers macOS (libc++, where the geomean is \~22x) and Windows MSVC (\~15x geomean), because iostream is slower there. The speedup varies widely by test, down to \~1x for line reading. The library does not guard against invalid input and targets competitive programming.

Targets competitive-programming use (whole-input buffering, exceptions off, etc.); only a subset of iostream semantics is drop-in compatible; no libc++ or MSVC STL comparison given, only libstdc++

## Maintenance

Effectively unmaintained (last commit 2024-11-23, zero open issues, one trivial closed issue) but MIT-licensed, small when pre-minified, and self-contained enough to vendor as-is; usability is 'copy blazingio.min.hpp and go', not a library you'd integrate into a build system.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README claims 5x over libstdc++ iostream with sync_with_stdio(false) and links raw data (benchmark-results/\*.json) and benchmark code (benchmarks/, test.py, which uses g++ -std=c++17 -O2). The runs were on GitHub Actions runners, so no CPU model or gcc version is stated. That makes it first-party with partial methodology, which is C.
- **Verifier notes:** The headline claim matches the README, and I checked the ratio against the raw JSON. The record's last_commit (2025-01-16) was the repo's pushed_at; the actual last commit is 2024-11-23, which is still stale. The repo has 62 stars, but the tier is C rather than D, so it is not a rejection candidate.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `baseline_stdlib`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/purplesyringa/blazingio/master/README.md>
  - <https://github.com/purplesyringa/blazingio>
  - <https://github.com/purplesyringa/blazingio/blob/master/LICENSE>
  - <https://github.com/purplesyringa/blazingio/tree/master/benchmark-results>
  - <https://github.com/purplesyringa/blazingio/blob/master/benchmark-results/linux-x86_64.json>
  - <https://github.com/purplesyringa/blazingio/blob/master/benchmark-results/macos-aarch64.json>
  - <https://github.com/purplesyringa/blazingio/blob/master/benchmark-results/windows-x86_64-msvc.json>
  - <https://github.com/purplesyringa/blazingio/blob/master/.github/workflows/benchmark.yml>
  - <https://github.com/purplesyringa/blazingio/blob/master/test.py>
- **Sources the enricher read:**
  - <https://github.com/purplesyringa/blazingio>
  - <https://raw.githubusercontent.com/purplesyringa/blazingio/master/README.md>
  - <https://github.com/purplesyringa/blazingio/blob/master/blazingio.hpp>
  - <https://github.com/purplesyringa/blazingio/blob/master/blazingio.min.hpp>
  - <https://github.com/purplesyringa/blazingio/blob/master/LICENSE>
  - <https://github.com/purplesyringa/blazingio/blob/master/test.py>
  - <https://github.com/purplesyringa/blazingio/blob/master/common.py>
  - <https://github.com/purplesyringa/blazingio/blob/master/config>
  - <https://github.com/purplesyringa/blazingio/blob/master/benchmark-results/linux-x86_64.json>
  - <https://github.com/purplesyringa/blazingio/issues?q=is%3Aissue>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/purplesyringa/blazingio`) · [data/wave1/enrich/raw/github_com_purplesyringa_blazingio.json](../../../data/wave1/enrich/raw/github_com_purplesyringa_blazingio.json) (enrichment confidence 0.6)

</details>
