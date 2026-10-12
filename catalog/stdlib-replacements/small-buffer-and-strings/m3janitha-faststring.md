# FastString

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Fixed-capacity, stack-allocated, constexpr string class that avoids the heap allocation std::string needs past SSO.

| | |
|---|---|
| **Beats** | std::string |
| **Claimed result** | From const char: std::string 498ns vs FastString 46.9ns (\~10.6x, derived from page data); large string construction: 1048ns vs 153ns (\~6.8x, derived); append: 190ns vs 164ns (\~1.2x, derived); append (large): 50.0ns vs 61.5ns (FastString \~0.8x, i.e. slightly slower, derived) (raw ns numbers verbatim from README table) |
| **Workload** | Constructing small (fixed-capacity, stack-allocated) and large strings from const char\*/buffer, and append operations, measured with Google Benchmark. |
| **Metric** | latency |
| **Hardware** | Reported only as "8 x 1498 MHz CPU" (Google Benchmark auto-detected core count/clock) with L1d 48KiB x4, L1i 32KiB x4, L2 512KiB x4, L3 8192KiB — no explicit CPU model name given |
| **Compiler and flags** | MSVC 19.28.29334.0 (README); optimization flags not stated. The x86-64 gcc-trunk section is only a Godbolt codegen comparison, with no timings. |
| **Adoption** | 27 stars |
| **Last commit** | 2024-03-31 |
| **Links** | [repository](https://github.com/m3janitha/FastString) · [benchmark](https://raw.githubusercontent.com/m3janitha/FastString/master/README.md) |

## Verdict

On MSVC 19.28.29334.0 (Windows; CPU reported only as "8 x 1498 MHz" with L1d 48KiB x4, L1i 32KiB x4, L2 512KiB x4, L3 8MiB — no CPU model given, no optimization flags stated), Google Benchmark shows constructing a short string from const char\* averaging 498ns wall / 148ns CPU for std::string versus 46.9ns / 16.3ns for fixed_size_str&lt;15&gt; (\~10.6x on wall time), and constructing a 45-character string in 1048ns versus 153ns (\~6.8x). Append is roughly at parity (190ns vs 164ns for a fixed_size_str&lt;63&gt; case) while a small-buffer append case is slightly slower for FastString (50.0ns vs 61.5ns).

## Use it when

- Short strings with a length bound known at compile time (order IDs, tickers, fixed-format codes) in latency-sensitive hot paths.
- Struct/message fields where predictable, allocation-free stack storage and fixed sizeof matter more than a general string API.
- Code that already consumes std::string_view and can call .str() to hand off for further processing.
- Compile-time (constexpr) string construction and simple manipulation.
- Workloads that can tolerate silent truncation of oversized input rather than needing growth or errors.

## Skip it when

- Any string whose length can exceed the chosen template capacity at runtime — it truncates silently instead of growing or signaling an error.
- Code expecting std::string's full interface (find, mutating substr, operator+, resize/reserve, stream extraction) — FastString's surface is much smaller.
- Append-heavy workloads on strings already inside SSO range: the project's own numbers show FastString roughly at parity (190ns vs 164ns) or slightly slower (50.0ns vs 61.5ns, i.e. \~0.8x) than std::string append in two of the four benchmarked scenarios.
- Toolchains without mature C++20 constexpr support — the repo's own open issue shows GCC 12.2.1 fails to compile the bundled example over a constexpr std::string_view::substr() error.
- Projects that need an actively maintained dependency: last commit 2024-03-31, 27 stars, and two pull requests (missing &lt;cstdint&gt; include, smaller size-type) sitting open and unmerged.

## How it is fast

Storage is a single fixed `CharT buffer_[max_length + 1]` plus a `std::size_t` length counter, both on the stack, so there is never a heap allocation, unlike std::string once an input exceeds small-string-optimization capacity (typically \~15-22 chars). Construction, append, and reset are just `Traits::copy`/`std::copy` calls capped at the compile-time capacity, and most member functions are `constexpr`, so short/compile-time-known strings can be folded away entirely. The repo's own Godbolt comparison (compiler_analysis.jpg) shows visibly smaller MSVC/gcc-trunk codegen for FastString versus std::string's allocation/SSO-branch logic for the same construct-and-return-length function.

## Compared with alternatives

Pick FastString when you specifically want stack-only, compile-time-sized strings with a minimal-dependency, genuinely constexpr-friendly header for constructing short strings in latency-critical code and can accept silent truncation. The other cataloged siblings solve different problems — to_static_string targets numeric-to-string conversion, buffet/fstring/Str/the Dicanio pool-allocator benchmark target more general-purpose (still growable or heap-backed) string replacements, zuu_string_view targets search over views, and jank's persistent_string is a language runtime's immutable string — none offer FastString's fixed-capacity, constexpr, stack-only design.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself (single header uses only &lt;string_view&gt;, &lt;algorithm&gt;, &lt;string&gt;, &lt;ostream&gt;); benchmark/test targets pull Google Benchmark and Google Test via CMake FetchContent |
| **Minimum toolchain** | C++20 (constexpr std::copy is required); README states MSVC 19.27.29111+ or x86-64 gcc-trunk; open issue #4 shows GCC 12.2.1 fails to compile the example over a constexpr std::string_view::substr() limitation |
| **Platforms** | any (portable C++20, no architecture-specific intrinsics); the only published benchmark numbers are from MSVC on Windows, and a multi-platform CMake CI workflow exists but its results were not inspected |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same construct/append/compare shape as std::string but fixed compile-time capacity, silent truncation instead of growth, and a much smaller API (no find, no mutating substr, no operator+, no resize/reserve) |

## Gotchas

- Construction/append/reset silently truncate any input longer than the compile-time capacity — no exception, no error flag, no way to detect truncation at the call site.
- remove_prefix/remove_suffix perform no bounds checking (string_view-style); an out-of-range length is undefined behavior.
- Length is stored as a full std::size_t per instance (8 bytes on 64-bit) even for tiny fixed strings; an open, unmerged PR (#5) proposes a smaller configurable size type to cut this overhead.
- GCC 12.2.1 fails to compile the bundled example (open issue #4, unresolved as of the last commit) due to a constexpr std::string_view::substr() error — check your exact GCC version before adopting.

## Caveats and trade-offs

Optimization flags and CPU model are not stated (hardware is only Google Benchmark's '8 X 1498 MHz' with cache sizes). Wall Time is about 3x CPU time on every row (e.g. 498 ns vs 148 ns for std::string), which suggests a noisy measurement. FastString is fixed-capacity and silently truncates, so it is not a drop-in std::string replacement. It is slower on the large-append case (61.5 vs 50.0 ns).

Fixed-size, stack-allocated string with a compile-time capacity template parameter; cannot grow beyond that capacity, so it is not a general-purpose std::string replacement; the project's own numbers show append-heavy workloads can be at parity or slightly slower than std::string.

## Maintenance

Stale (last commit 2024-03-31) with two open, unmerged pull requests and one unresolved GCC 12.2.1 compile-failure issue; MIT-licensed and small enough (\~140-line single header) to vendor and patch yourself if you accept the maintenance risk.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Google Benchmark output directly compares std::string with fixed_size_str, and all quoted ns values match the Time column. Benchmark code is public (benchmark/benchmark_test.cpp) and the compiler is given as MSVC 19.28, but optimization flags are not stated and the CPU model is not named (only '8 X 1498 MHz'), so this is C.
- **Verifier notes:** The default branch (master, the only branch) last had a commit on 2024-03-31. The 2024-06-09 date was repo pushed_at, not a commit. MIT, 27 stars, stale.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/m3janitha/FastString>
  - <https://raw.githubusercontent.com/m3janitha/FastString/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/m3janitha/FastString>
  - <https://raw.githubusercontent.com/m3janitha/FastString/master/README.md>
  - <https://github.com/m3janitha/FastString/blob/master/include/FastString.h>
  - <https://github.com/m3janitha/FastString/blob/master/CMakeLists.txt>
  - <https://github.com/m3janitha/FastString/blob/master/benchmark/benchmark_test.cpp>
  - <https://github.com/m3janitha/FastString/issues/4>
  - <https://github.com/m3janitha/FastString/issues>
  - <https://github.com/m3janitha/FastString/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/m3janitha/faststring`) · [data/wave1/enrich/raw/github_com_m3janitha_faststring.json](../../../data/wave1/enrich/raw/github_com_m3janitha_faststring.json) (enrichment confidence 0.6)

</details>
