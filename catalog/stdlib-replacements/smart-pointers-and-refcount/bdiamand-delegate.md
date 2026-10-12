# Delegate (bdiamand/Delegate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Custom permissive notice in the delegate.h header (not an OSI-approved license; no LICENSE file)` · 🔴 abandoned

> Fixed-size, heapless C++17 delegate beating std::function's invocation speed by 1.1-1.4x in a third-party benchmark.

| | |
|---|---|
| **Beats** | std::function |
| **Claimed result** | Delegate beats std::function in all 7 invocation categories of the CxxFunctionBenchmark various.cpp sample result (MSVC 15.9.4): function_pointer 0.2101s vs 0.2640s (\~1.26x); compile_time_function_pointer 0.1324 vs 0.1884 (\~1.42x); compile_time_delegate 0.1395 vs 0.1906 (\~1.37x); heavy_functor 0.1586 vs 0.1897 (\~1.20x); non_assignable 0.1402 vs 0.1860 (\~1.33x); lambda_capture 0.1585 vs 0.1757 (\~1.11x); stateless_lambda 0.1325 vs 0.1799 (\~1.36x). Ratios are derived from page data. Delegate is the fastest of the 13 implementations in 5 of 7 categories; in heavy_functor and lambda_capture others are equal or slightly faster (stdex::function 0.1579, func::function 0.1578). |
| **Workload** | Invocation timing in CxxFunctionBenchmark various.cpp, int(int) signature, across seven call patterns: function_pointer, compile_time_function_pointer, compile_time_delegate, heavy_functor, non_assignable, lambda_capture, and stateless_lambda. |
| **Metric** | throughput |
| **Compiler and flags** | MSVC 64-bit, Visual Studio 15.9.4, Release build, Boost 1.69.0 |
| **Adoption** | 43 stars |
| **Last commit** | 2022-07-27 |
| **Links** | [repository](https://github.com/bdiamand/Delegate) · [benchmark](https://github.com/jamboree/CxxFunctionBenchmark#sample-result) |

## Verdict

On MSVC 15.9.4 (Visual Studio, 64-bit Release, Boost 1.69.0, CPU unspecified) in jamboree/CxxFunctionBenchmark's various.cpp, Delegate beat MSVC STL's std::function in all 7 invocation categories (e.g. function_pointer 0.210s vs 0.264s, \~1.26x; compile_time_function_pointer 0.132s vs 0.188s, \~1.42x), and was the fastest of 13 implementations in 5 of 7 categories (stdex::function and func::function tied or edged it out in heavy_functor and lambda_capture).

## Use it when

- Callback/handler slots where the callable's capture state is small and known ahead of time (fits in \~12-20 bytes, adjustable via DELEGATE_ARGS_SIZE)
- Hot paths that construct/copy/destroy callables frequently and need to avoid heap allocation and its jitter
- Embedded or latency-sensitive code that wants predictable, allocation-free memory behavior
- Code that already avoids RTTI/exceptions and does not need std::function's arbitrary-size type erasure
- Move-only captures (e.g. unique_ptr) via the MoveDelegate variant, where std::function historically disallows or complicates this

## Skip it when

- Captures larger than the fixed buffer size — code fails to compile (static_assert), unlike std::function's silent heap fallback
- Codebases that rely on std::function's RTTI/exception interplay or allocator-aware construction
- Projects needing an OSI-approved license: this ships a custom permissive header notice, not MIT/Apache/BSD
- Long-term maintenance risk: repo has been inactive since 2022-07-27 and only 43 stars
- Multi-threaded use without external synchronization — no thread-safety guarantees are documented or implemented

## How it is fast

Never allocates: captured state is stored inline in a fixed-size aligned byte buffer (default 12 bytes, resizable via DELEGATE_ARGS_SIZE macro), so there is no heap round-trip on construction, copy, move, or destruction. Dispatch uses a raw function pointer plus a small static per-type vtable (copy/move/destroy) built once via templates, avoiding the extra indirection and RTTI/exception bookkeeping std::function implementations carry. No dynamic memory management and no exception-safety machinery to execute on the hot call path.

## Compared with alternatives

Pick Delegate over stdext::inplace_function or SmallFunction when you want the smallest reported invocation times in this same benchmark suite for pointer/lambda-heavy call patterns; pick stdext::inplace_function instead if you need an OSI-approved (SG14/Boost-style) license, since Delegate's license is a non-standard permissive notice.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself (Catch2 is a test-only dependency for delegate_ut.cpp) |
| **Minimum toolchain** | C++17 (uses std::is_same_v, std::invoke_result_t) |
| **Platforms** | not documented (no platform-specific code observed; standard C++17, no intrinsics) |
| **Thread safety** | not documented; no synchronization primitives in delegate.h, so treat as not thread-safe without external locking |
| **Drop-in for the baseline** | partial — explain: constructor/call/bool syntax mirrors std::function, but capture size is fixed at compile time (static_assert on overflow instead of heap fallback), and there is no support for RTTI, exceptions, or allocators |

## Gotchas

- Default capture buffer is only sizeof(int)+sizeof(int\*) (12 bytes on typical 64-bit builds), plus 8 bytes of vtable/call-pointer overhead; override via #define DELEGATE_ARGS_SIZE / DELEGATE_ARGS_ALIGN before including the header if captures don't fit
- Copying a Delegate built from a non-copyable functor calls std::terminate() at runtime rather than failing to compile (only FuncCopyable's copy path is affected; use MoveDelegate to avoid this class of captures entirely)
- No exception awareness at all — the header does not catch or propagate exceptions from the wrapped callable differently than a normal call would
- No LICENSE file; licensing is a custom notice embedded in the delegate.h comment block requiring the comment block to remain in derived works

## Caveats and trade-offs

The Delegate author (bdiamand) produced the sample-result numbers via PRs to jamboree/CxxFunctionBenchmark in Jan 2019. The run is independent-suite code, not independently run. CPU model not stated. Tested only against MSVC STL std::function. Delegate is not the fastest in every category. The license is a custom permissive header notice, not OSI-approved, so usability is 'reference'. Delegate's own repo has no benchmark.

Fixed-size capture (8 bytes + capture size on 32-bit, +8 more on 64-bit); no arbitrary-size type erasure or allocator support like std::function; no LICENSE file included.

## Maintenance

Abandoned since the last commit on 2022-07-27; usability is 'reference' because the custom header license is not OSI-approved, though the code is small (\~350 lines) and easy to vendor or re-license by copying and adapting.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The CxxFunctionBenchmark suite (various.cpp) is public, but its README 'Sample Result' says only MSVC 15.9.4 Release, with no CPU model. The Delegate author (bdiamand) generated these numbers in PRs #23 and #25, which added Delegate and rewrote the sample-result block, so they are first-party numbers in a modest (98-star) suite: Tier C, not B.
- **Verifier notes:** Downgrade for two reasons. First, 'consistently fastest of 13' is false for heavy_functor and lambda_capture (the vs-std::function wins do hold in all 7 categories). Second, the numbers came from the Delegate author's own PRs, so the tier drops B to C. Metadata checks out: 43 stars, last commit 2022-07-27 (abandoned), not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jamboree/CxxFunctionBenchmark#sample-result>
  - <https://github.com/jamboree/CxxFunctionBenchmark>
  - <https://github.com/bdiamand/Delegate>
  - <https://github.com/bdiamand/Delegate/blob/master/delegate.h>
- **Sources the enricher read:**
  - <https://github.com/bdiamand/Delegate>
  - https://github.com/bdiamand/Delegate (README via gh api)
  - <https://github.com/bdiamand/Delegate/blob/master/delegate.h>
  - https://github.com/bdiamand/Delegate (repo metadata via gh api)
  - https://github.com/bdiamand/Delegate/issues (via gh issue list)
  - <https://github.com/jamboree/CxxFunctionBenchmark#sample-result>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/bdiamand/delegate`) · [data/wave1/enrich/raw/github_com_bdiamand_delegate.json](../../../data/wave1/enrich/raw/github_com_bdiamand_delegate.json) (enrichment confidence 0.65)

</details>
