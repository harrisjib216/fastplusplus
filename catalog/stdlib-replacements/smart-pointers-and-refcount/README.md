# Smart pointers and reference counting

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::shared_ptr, std::unique_ptr, std::function  
**10 entries:** 3 tier A · 2 tier B · 4 tier C · 1 tier D · 9 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**observable_unique_ptr / observer_ptr (oup)**](cschreib-observable-unique-ptr.md) | Header-only unique-ownership smart pointer with observer_ptr; dereference is 3.5x-38.7x faster than std::weak_ptr::lock(). | **A** | C++ | MIT | 🟢 active |
| 2 | [**woid**](akopich-woid.md) | Header-only C++23 type-erasure toolkit; woid::Fun beats std::function via configurable SBO storage and const/noexcept-correct signatures. | **A** | C++ | MIT | 🟢 active |
| 3 | [**CDRC atomic_weak_ptr (concurrent_deferred_rc)**](cmuparlay-concurrent-deferred-rc.md) | Header-only C++20 lock-free atomic weak/shared pointers, beating a commercial atomic&lt;weak_ptr&gt; implementation under contention. | **A** | C++ | MIT | 🔴 abandoned |
| 4 | [**stdext::inplace_function (WG21-SG14/SG14)**](wg21-sg14-sg14.md) | Header-only, fixed-capacity callable wrapper beating std::function's invocation speed in 5 of 7 shootout categories. | **B** | C++ | BSL-1.0 | 🔴 abandoned |
| 5 | [**SimpleSignal**](larspensjo-simplesignal.md) | 223-line CC0 header of single-threaded C++11 signals; beats Boost.Signals2 (st) and libsigc++ in a community MSVC shootout. | **B** | C++ | CC0-1.0 | 🔴 abandoned |
| 6 | [**sy_callback.hpp**](shigamiyune-sy-callback-hpp.md) | Header-only type-erased callback wrapper beating std::function on construct/destroy, move, and assign; no SBO. | **C** | C++ | Apache-2.0 | 🟡 stale |
| 7 | [**cpgf callback (GCallback / GCallbackList)**](cpgf-cpgf.md) | Discontinued C++ callback and callback-list (signal) headers; 2011 numbers beat Boost.Signals2 and tie libsigc++ on single calls. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 8 | [**SmallFunction (LoopPerfect/smallfunction)**](loopperfect-smallfunction.md) | Header-only, fixed-capacity alternative to std::function that placement-news the callable into an inline stack buffer instead of the heap. | **C** | C++ | MIT | 🔴 abandoned |
| 9 | [**Delegate (bdiamand/Delegate)**](bdiamand-delegate.md) | Fixed-size, heapless C++17 delegate beating std::function's invocation speed by 1.1-1.4x in a third-party benchmark. | **C** | C++ | Custom permissive notice in… (study only) | 🔴 abandoned |
| 10 | [**Yomm2**](jll63-yomm2.md) | Archived C++17 open multi-methods library; plain dispatch is slower than virtual calls, and its 5x virtual_ptr win is a cache-layout artifact. | **D** | C++ | BSL-1.0 | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
