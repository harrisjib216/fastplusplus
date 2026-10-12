# sy_callback.hpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Header-only type-erased callback wrapper beating std::function on construct/destroy, move, and assign; no SBO.

| | |
|---|---|
| **Beats** | std::function |
| **Claimed result** | README.ENG.md tables (10M reps). Call, lambda without capture: sy_callback \~0.041s vs std::function \~0.073s (\~1.8x, derived from page data). Init+destroy, lambda without capture: \~0.08s vs \~0.51s (\~6.4x, derived from page data); large 1024-byte capture: \~0.1s vs \~1.5s (\~15x, derived from page data). Copy \~0.31s vs \~0.46s (\~1.5x, derived from page data). Move \~0.027s vs \~0.37s (\~14x, derived from page data). Assign \~0.26s vs \~1.9s (\~7.3x, derived from page data). Exception: calling a std::bind member function, sy_callback \~0.71s vs std::function \~0.135s, so sy_callback is \~5x slower there. |
| **Workload** | 10 million repetitions each of: callback invocation (member/global/lambda), construction+destruction, and copy/move/assign, for sy_callback::callback&lt;Signature&gt; vs std::function; also a compile-time/binary-size test instantiating 1000 callbacks |
| **Metric** | latency |
| **Hardware** | Apple M1 (MacOS), exact chip variant unstated |
| **Compiler and flags** | clang++ -O2 |
| **Adoption** | 0 stars |
| **Last commit** | 2025-09-18 |
| **Links** | [repository](https://github.com/ShigamiYune/sy_callback.hpp) · [benchmark](https://github.com/ShigamiYune/sy_callback.hpp/blob/main/README.ENG.md) |

## Verdict

First-party README benchmarks (clang++ -O2, Apple M1 macOS, libc++) over 10M reps claim sy_callback beats std::function on init+destroy (\~6x for non-capturing lambdas, \~15x for 1024-byte captures), move (\~14x), assign (\~7x), copy (\~1.5x), and most call-time paths (\~1.8x for non-capturing lambdas/global functions); std::function is \~5x faster specifically when the callback wraps a std::bind'd member function. Only the call-time numbers have a public harness (test.cpp); init/destroy, copy/move/assign, and compile-time tables are unverified first-party figures.

## Use it when

- Hot loops that construct, destroy, move, or assign large numbers of callbacks (per-frame game/embedded code) where std::function's allocation and vtable overhead dominates
- Callbacks are mostly non-capturing lambdas or plain function/static-member pointers, which avoid heap allocation entirely in this design
- Binary-size or compile-time sensitive code instantiating many distinct callback signatures (README's 1000-callback table shows much smaller generated code and faster compiles than std::function in most rows, though this table has no public benchmark source)
- Single-threaded callback ownership, or lifetime changes (move/assign/swap/reset) externally synchronized
- C++11-only toolchains/embedded targets where a minimal, dependency-free header is preferable to &lt;functional&gt;'s std::function

## Skip it when

- Callbacks built from std::bind-wrapped member functions: the README's own numbers show std::function \~5x faster than sy_callback there
- Multi-threaded code that moves, destroys, assigns, swaps, or resets a shared callback concurrently — only copy is documented thread-safe
- Expecting small-buffer optimization for small captures: there is none, so every capturing lambda or functor heap-allocates regardless of capture size
- Anything requiring production-grade maturity: single-contributor repo, 0 stars, no CI, no releases/tags, most benchmark tables (init/destroy, copy/move/assign, compile-time) have no published harness
- Code needing package-manager distribution or CMake config — it's a bare header plus a manual test.cpp, no build tooling included

## How it is fast

The object is 16 bytes: an object_ptr slot plus a thunk_fn that returns one of two static function pointers (invoke_fn, life_fn) rather than std::function's typical vtable/control-block scheme. Non-capturing lambdas and plain function pointers are stored directly in the pointer slot and invoked with no heap allocation, so construct/destroy/move for that common case is just pointer copies instead of allocator traffic. invoke_prediction&lt;T&gt;() lets a caller assert the concrete static type to skip the thunk indirection on the call, at a claimed \~10-20% gain per the README.

## Compared with alternatives

Among the std::function-beating siblings (woid, Delegate, stdext::inplace_function, SmallFunction), pick sy_callback when you specifically want zero heap allocation for non-capturing lambdas/plain functions and a minimal 16-byte base object, and can tolerate heap allocation for every capturing case; pick inplace_function or SmallFunction instead when you need true SBO for small captures, since those have broader validation than this single-contributor, 0-star repo.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library (&lt;functional&gt;, &lt;type_traits&gt;, &lt;typeindex&gt;) |
| **Minimum toolchain** | C++11 minimum; compiles an additional noexcept-function-pointer code path under C++17 (__cplusplus &gt;= 201703L) |
| **Platforms** | not documented beyond the benchmark machine (Apple M1 macOS, clang++); no CI workflows in the repo and no explicit platform support statement |
| **Thread safety** | Copying a callback across threads is documented safe; move, assign, swap, and reset are explicitly called out in DOCUMENT.ENG.md as potentially racing across threads |
| **Drop-in for the baseline** | partial — explain: operator= from a lambda/functor/function pointer mirrors std::function, and calling an empty callback throws the same std::bad_function_call, but wrapping a specific member function requires callback&lt;Sig&gt;::make&lt;Class,&Class::Func&gt;(obj) instead of std::bind, so call sites using std::bind/std::mem_fn need rewriting |

## Gotchas

- Calling an empty or moved-from callback throws std::bad_function_call() (reused from &lt;functional&gt;), not a library-specific exception type
- target&lt;T&gt;() relies on RTTI (typeid/std::type_index) internally
- invoke_prediction&lt;T&gt;() requires the caller to name the exact static type (or member-function pointer) to get the fast path; a wrong guess still works correctly but the speedup is only \~10-20% per the README, with some code-size increase
- No SBO: capturing lambdas and functors always heap-allocate, even for a single captured byte; only non-capturing lambdas and plain function pointers avoid the heap

## Caveats and trade-offs

First-party numbers, averaged and rounded from multiple compilations; test.cpp is a chrono-based harness for the call-time table only (direct vs sy_callback vs std::function); there is no published code for the init/destroy, copy/move/assign or compile-time tables; the clang version is unstated; std::function is \~5x faster in the std::bind member call row; repo has 0 stars and a single contributor, last pushed 2025-09-18.

No small-buffer optimization — every callable except a non-capturing lambda is heap-allocated behind a raw pointer; not safe to move/destroy concurrently across threads (only copy is thread-safe); C++11-only API; docs are bilingual Vietnamese/English machine-translated text mixed into the README.

## Maintenance

Stale: single-contributor repo created 2025-09-01, last pushed 2025-09-18, 0 stars, no releases/tags/CI; Apache-2.0 licensed and copyable as one header, so cheap to vendor and read despite the lack of outside validation.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README.ENG.md gives first-party averaged numbers (clang++ -O2, MacOS M1). test.cpp only covers the call-time table and names no compiler version. The init/destroy, copy/move/assign and compile-time numbers have no public harness, so it is not A.
- **Verifier notes:** The numbers match the README. The record's caveat that there is no benchmark source is partly wrong, because test.cpp does time calls against std::function; I corrected the caveat. baseline_stdlib is set to libc++ as an inference: the page says clang++ on macOS, whose only shipped standard library is libc++.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ShigamiYune/sy_callback.hpp>
  - <https://github.com/ShigamiYune/sy_callback.hpp/blob/main/README.ENG.md>
  - <https://github.com/ShigamiYune/sy_callback.hpp/blob/main/test.cpp>
- **Sources the enricher read:**
  - <https://github.com/ShigamiYune/sy_callback.hpp>
  - <https://github.com/ShigamiYune/sy_callback.hpp/blob/main/README.ENG.md>
  - <https://github.com/ShigamiYune/sy_callback.hpp/blob/main/DOCUMENT.ENG.md>
  - <https://github.com/ShigamiYune/sy_callback.hpp/blob/main/test.cpp>
  - <https://github.com/ShigamiYune/sy_callback.hpp/blob/main/sy_callback.hpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/shigamiyune/sy_callback.hpp`) · [data/wave1/enrich/raw/github_com_shigamiyune_sy_callback_hpp.json](../../../data/wave1/enrich/raw/github_com_shigamiyune_sy_callback_hpp.json) (enrichment confidence 0.5)

</details>
