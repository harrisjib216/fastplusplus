# woid

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++23 type-erasure toolkit; woid::Fun beats std::function via configurable SBO storage and const/noexcept-correct signatures.

| | |
|---|---|
| **Beats** | std::function |
| **Claimed result** | Read from the FunBench SVG plot geometry, so approximate (derived from page data). benchVectorStdLess: woid::Fun variants are \~1.0x at vector sizes 1-2, peak \~1.3x (Fun&lt;Any&lt;8&gt;&gt;) to \~1.64x (Fun&lt;TrivialAny&lt;&gt;&gt;) around size 2^8, and \~1.2-1.3x at large sizes vs std::function. The 1x-6x axis is driven by the plain-lambda Id&lt;std::less&lt;int&gt;&gt; series (\~6.3x peak), not by woid. benchVectorBigLess (companion plot): up to \~2.55x (Fun&lt;TrivialAny&lt;32&gt;&gt;) and \~1.9x (Fun&lt;Any&lt;32&gt;&gt;) around 2^8, \~1.4-1.5x at large sizes. The README only says woid "ranks first in most cases". |
| **Workload** | std::sort over vectors of ints (sizes 2^0 to 2^18, RangeMultiplier(2)-&gt;Range(1,N)) using a comparator wrapped in woid::Fun vs std::function vs function2 vs a plain lambda (bench/fun_bench.cpp, targets benchVectorStdLess and benchVectorBigLess) |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-10850K CPU @ 3.60GHz |
| **Compiler and flags** | Clang 21.1.6; bench/plot.py builds CMAKE_BUILD_TYPE=Release -&gt; -O3 -DNDEBUG -fno-rtti -fno-exceptions, linked with lld and -Wl,--shuffle-sections (random seed per rep); GCC 15 mentioned only as a supported compiler |
| **Adoption** | 7 stars |
| **Last commit** | 2026-02-09 |
| **Links** | [repository](https://github.com/akopich/woid) · [benchmark](https://github.com/akopich/woid/blob/main/bench/plots/FunBench_benchVectorStdLess_speedup.svg) |

## Verdict

Benchmark (bench/fun_bench.cpp, run via bench/plot.py) sorts vectors of ints (sizes 2^0-2^18) with a comparator wrapped in woid::Fun vs std::function&lt;bool(int,int)&gt; vs function2 vs a plain lambda, built Release (-O3 -DNDEBUG -fno-rtti -fno-exceptions) with Clang 21.1.6 on an Intel i9-10850K. Per the verifier's reading of the SVG plot geometry, woid::Fun is \~1.0x at the smallest sizes and roughly 1.2x-1.6x vs std::function on the std::less&lt;int&gt; comparator (up to \~2.55x on the 32-byte BigLess comparator around size 2^8); the README itself only claims woid 'ranks first in most cases' without giving exact multipliers.

## Use it when

- Hot loops that repeatedly construct/invoke small comparator or callback closures (e.g. sort comparators), where std::function's heap fallback and call overhead show up in profiles
- Callables whose captures fit a known small size — size Any&lt;N&gt;/TrivialAny&lt;N&gt; to match the capture so SBO always applies and heap allocation is designed out
- You need call-signature const/noexcept correctness that std::function does not enforce
- You also want a non-intrusive virtual-function alternative (InterfaceBuilder) so unrelated types can share an interface without a base class, especially when the concrete type set is closed (SealedInterfaceBuilder + std::variant)
- C++23-only toolchains (tested with Clang 21 / GCC 15) where you're willing to vendor a single young header and re-verify before relying on it in production

## Skip it when

- Project is stuck on C++20 or earlier — woid requires C++23
- Need a battle-tested, widely-deployed std::function replacement; woid has 7 GitHub stars, 0 filed issues, and a first commit from 2025-10-23, so edge cases are largely unexercised outside the author's own tests
- Need documented thread-safety guarantees — none are stated for any woid type, so a shared Fun/Any used across threads needs synchronization you verify yourself
- Move-only captures needed alongside copyable ones elsewhere — you must pick a Copy::DISABLED storage up front; there's no separate move_only_function-style type or runtime toggle
- At the smallest input sizes (vector length 1-2 in the sort benchmark) woid::Fun is only \~1.0x vs std::function, so the win is workload-size-dependent, not universal

## How it is fast

Speed comes from configurable small-buffer optimization: callers size the inline buffer (Any&lt;N&gt;) to the actual capture, avoiding the heap allocation std::function often falls back to for anything beyond a word-sized capture. TrivialAny skips the stored copy/move/destroy function-pointer indirection entirely for trivially-movable/copyable callables, treating the buffer as raw bytes instead; ExceptionGuarantee::NONE (usable as a Storage policy) further removes strong-guarantee bookkeeping that std::function-like wrappers pay for. InterfaceBuilder avoids vtable indirection by storing function pointers directly in (or referenced from) the wrapper, and SealedInterfaceBuilder replaces indirection with std::variant + visitation when the polymorphic type set is known at compile time.

## Compared with alternatives

Pick woid over Delegate/inplace_function/SmallFunction/sy_callback.hpp when you need const/noexcept-correct call signatures and configurable SBO storage shared with a broader type-erasure toolkit (Any + a virtual-function replacement) in one header; those siblings are narrower, longer-established std::function replacements with more real-world usage and no C++23 requirement.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself (single header include/woid.hpp); building the tests/benchmarks pulls in GTest, google/benchmark, Boost 1.76+, and the third_party submodules function2/boost::te/microsoft::proxy |
| **Minimum toolchain** | C++23 (CMakeLists requires CMake 3.21+); tested with Clang 21.1.6 and GCC 15 |
| **Platforms** | not documented — no architecture/OS restriction stated in README; author's benchmarks ran on x86-64 (Intel i9-10850K) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: same call syntax (f(args...)) but Fun requires choosing a Storage template parameter (unlike std::function's single fixed type), and its call signature can be const/noexcept-qualified in ways std::function's signature cannot express |

## Gotchas

- TrivialAny silently falls back to heap allocation for non-trivial or non-trivially-movable/copyable objects unless kCanAllocate is disabled, in which case it becomes a compile error instead
- ExceptionGuarantee::NONE (a configurable, non-strict default) is UB if the stored callable's copy/move constructor throws; opting into STRONG costs performance and also disables SBO for non-nothrow-movable types
- No separate move-only Fun type: copyability of Fun/Any is inherited from the chosen Storage's Copy policy, so move-only captures require picking Copy::DISABLED explicitly
- 0 issues have ever been filed on the repo (young project), so failure modes beyond the author's own GTest suite are unverified

## Caveats and trade-offs

Single-author, single-machine benchmark (i9-10850K, Clang 21.1.6); only 7 GitHub stars and young (first commit 2025-10-23); speedups exist only as SVG plots, so the numbers here are approximations read from the plot geometry; woid::Fun is \~1.0x at tiny sizes and \~1.2-1.6x on the std::less comparator; the plot's larger ratios belong to the plain-lambda reference series; standard library implementation not stated.

Requires C++23; woid::Fun/FunRef are type-erased wrappers with configurable SBO size/alignment (via woid::Any/TrivialAny storages) and, unlike std::function, they respect const/noexcept on the call signature; no separate move-only wrapper type is needed since copyability follows the chosen Storage instead. Benchmark also compares woid::Any vs std::any and woid::InterfaceBuilder vs virtual functions/boost::te/microsoft::proxy, so std::function is only one of several targets.

## Maintenance

Active (pushed 2026-02-09) but very young — first commit 2025-10-23, 7 GitHub stars, 0 issues filed; MIT-licensed and a single header, so it's cheap to vendor and drop if it stalls.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The benchmark code is public (bench/fun_bench.cpp, driven by bench/plot.py). plot.py builds with CMAKE_BUILD_TYPE=Release and clang, giving -O3 -DNDEBUG -fno-rtti -fno-exceptions from CMakeLists.txt. The README states Clang 21.1.6 and an i9-10850K @ 3.60GHz, and the plot is explicitly speedup vs std::function&lt;bool(int,int)&gt;.
- **Verifier notes:** I decoded the SVG paths against the y-tick positions to estimate the ratios. The record's '1x-6x' hint is misleading because the tallest curve is the non-type-erased plain lambda. Tier A holds: code, compiler, flags (via the Release build type in plot.py) and the CPU model are all available.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/akopich/woid>
  - <https://github.com/akopich/woid/blob/main/README.md>
  - <https://github.com/akopich/woid/blob/main/bench/plots/FunBench_benchVectorStdLess_speedup.svg>
  - <https://github.com/akopich/woid/blob/main/bench/plots/FunBench_benchVectorBigLess_speedup.svg>
  - <https://github.com/akopich/woid/blob/main/CMakeLists.txt>
  - <https://github.com/akopich/woid/blob/main/bench/plot.py>
  - <https://github.com/akopich/woid/blob/main/bench/fun_bench.cpp>
- **Sources the enricher read:**
  - <https://github.com/akopich/woid>
  - <https://github.com/akopich/woid/blob/main/README.md>
  - <https://github.com/akopich/woid/blob/main/CMakeLists.txt>
  - <https://github.com/akopich/woid/blob/main/LICENSE>
  - <https://github.com/akopich/woid/blob/main/include/woid.hpp>
  - <https://github.com/akopich/woid/blob/main/bench/fun_bench.cpp>
  - <https://github.com/akopich/woid/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/akopich/woid`) · [data/wave1/enrich/raw/github_com_akopich_woid.json](../../../data/wave1/enrich/raw/github_com_akopich_woid.json) (enrichment confidence 0.6)

</details>
