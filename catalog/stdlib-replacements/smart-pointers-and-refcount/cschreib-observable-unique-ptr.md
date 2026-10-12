# observable_unique_ptr / observer_ptr (oup)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only unique-ownership smart pointer with observer_ptr; dereference is 3.5x-38.7x faster than std::weak_ptr::lock().

| | |
|---|---|
| **Beats** | std::weak_ptr |
| **Claimed result** | Dereference observer, relative to raw T\* = 1 (median across object types). gcc 9.4.0/libstdc++-9/Ryzen 5 2600: weak/shared 3.5 vs observer 1.0 (obs_unique and obs_sealed), \~3.5x. MSVC 16.11.3/MS-STL/i7-7800X: 9.4 vs 1.4 (obs_unique) and 0.8 (obs_sealed), \~6.7x-11.8x. Emscripten 2.0.34/libc++/Node.js 14.15.5/Ryzen 5 2600: 38.7 vs 1.0, \~38.7x. Create observer: 1.6 vs 1.6 (gcc), 5.3 vs 1.6 (MSVC), 14.8 vs 2.3 (Emscripten). (Ratios derived from page data.) |
| **Workload** | Median dereference/creation cost across int, float, std::string, std::array&lt;int,65536&gt; owned objects; oup::observer_ptr dereference vs std::weak_ptr::lock()-based dereference (also compares owner-pointer creation vs std::unique_ptr/shared_ptr) |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 5 2600, Linux 5.15.0 (gcc run); Intel i7-7800X, Windows 10.0.19043 (MSVC run); AMD Ryzen 5 2600, Node.js 14.15.5 + Linux 5.1.0 (Emscripten/libc++ run) |
| **Compiler and flags** | gcc 9.4.0 (libstdc++-9), MSVC 16.11.3 (MS-STL), Emscripten 2.0.34 (libc++); 'all optimizations turned on (except LTO)', exact flags not listed |
| **Adoption** | 42 stars |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/cschreib/observable_unique_ptr) · [benchmark](https://github.com/cschreib/observable_unique_ptr#speed-benchmarks) |

## Verdict

README's own speed_benchmark.cpp results (median across int/float/std::string/std::array&lt;int,65536&gt; objects, relative to raw T\*=1) show observer_ptr dereference beating std::weak_ptr::lock()-based dereference by \~3.5x on gcc 9.4.0/libstdc++-9/Ryzen 5 2600, \~9.4x-11.8x on MSVC 16.11.3/MS-STL/i7-7800X, and \~38.7x on Emscripten 2.0.34/libc++ under Node.js 14.15.5/Ryzen 5 2600. The same tables show creating the owner pointer itself is 1.1x-2.9x slower than std::unique_ptr/std::shared_ptr, so the win is specific to the observer/dereference path, not owner construction.

## Use it when

- Object has one clear owner and you only need to detect "has this been destroyed yet", not extend its lifetime
- Observer dereference/expiry-check happens in a hot loop and the object and its observers stay on a single thread
- You want observer-pointer semantics without std::shared_ptr's control-block allocation and atomic refcount overhead
- Header-only C++17 codebase where adding a single header is acceptable (no build system integration required)
- Multiple inheritance with observer_from_this()-style self-observation (std::enable_shared_from_this doesn't support this)

## Skip it when

- Observer pointers or the owner must be touched from more than one thread — no synchronization on the refcount, unlike std::shared_ptr/weak_ptr
- You need shared ownership (multiple owners) rather than unique ownership with observers
- You need arrays (T[]) or custom allocator support — both unimplemented
- Owner-pointer construction/creation is on the hot path — creating an oup owner is 1.1x-2.9x slower than std::unique_ptr/std::shared_ptr in the project's own benchmark table
- You need observable_sealed_ptr with a custom deleter, or a default-constructible/copyable/movable T combined with enable_observer_from_this_sealed (that path requires T's constructor to accept a control block)

## How it is fast

The reference/expiry counter is a plain (non-atomic) integer in a small heap control block, so dereferencing an observer_ptr is just a flag check plus pointer read, versus std::weak_ptr::lock() which does an atomic increment, constructs a temporary shared_ptr, then an atomic decrement. Dropping shared ownership also shrinks the control block to 4 bytes (vs shared_ptr's \~24-byte block), cutting a heap allocation's worth of bookkeeping touched per access.

## Compared with alternatives

Pick oup over CDRC atomic_weak_ptr (concurrent_deferred_rc) when you have single-threaded or thread-confined ownership and want the smallest, simplest observer pointer; pick CDRC instead when observers must be read/written concurrently across threads, since oup has no synchronization at all. The std::function alternatives in this category (woid, Delegate, stdext::inplace_function, SmallFunction, sy_callback) solve a different problem (callable storage) and aren't a substitute for either.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++17 (CMakeLists.txt sets cxx_std_17; cmake_minimum_required 3.8+ if using the provided CMake target) |
| **Platforms** | any; CI builds Linux (GCC/clang), Windows (MSVC 32/64), macOS (clang), WebAssembly (Emscripten) |
| **Thread safety** | Not thread-safe: refcount/control-block operations are unsynchronized. Unsafe for an owner on one thread to be observed from another thread. Safe in multithreaded programs as long as all observer_ptrs for a given object stay on that object's thread. |
| **Drop-in for the baseline** | partial — explain: API shape (expired(), deref) mirrors std::weak_ptr's locked-use pattern, but the ownership model is unique not shared, so it replaces unique_ptr+weak_ptr-style usage, not shared_ptr+weak_ptr call sites verbatim. |

## Gotchas

- enable_observer_from_this_sealed requires T's constructor to accept a control block argument, which makes T non-default-constructible, non-copyable, and non-movable
- enable_observer_from_this_unique uses virtual inheritance to support multiple inheritance, which has its own ABI/layout cost
- observable_sealed_ptr does not support a custom deleter (observable_unique_ptr does)
- observer_from_this() throws a documented exception type when called in situations where no valid control block exists yet (e.g., certain construction states)

## Caveats and trade-offs

oup is unique-ownership only and not thread-safe; std::weak_ptr::lock() does atomic refcount work, so part of the dereference advantage comes from dropping thread safety. Creating the owner pointer is slower than std::unique_ptr. The README says the benchmarks were last run for oup v0.7.1, so they may not reflect current code. The Emscripten/libc++ run is WebAssembly on Node.js, not native.

Not thread-safe (no atomic refcount), unlike std::shared_ptr/weak_ptr; no array support; no custom-allocator support; owner-pointer creation itself is 1.1-2.1x SLOWER than std::unique_ptr/shared_ptr in the same table, so the win is specific to the observer/dereference path.

## Maintenance

Actively maintained (last commit 2026-09-05, project at v0.7.3 per CMakeLists.txt, MIT licensed), but the README states the speed benchmarks were last run for v0.7.1, so current numbers are unverified against the latest code. Small single-header library with no open issues; safe to vendor given the license and size.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The README 'Speed benchmarks' section compares oup with std::weak_ptr/shared_ptr using public code (tests/speed_benchmark.cpp). Each run names the compiler and CPU: gcc 9.4.0 on a Ryzen 5 2600, MSVC 16.11.3 on an i7-7800X, and Emscripten on a Ryzen 5 2600. Flags are stated only as 'all optimizations turned on (except LTO)', so Tier A is borderline.
- **Verifier notes:** The record's numbers (1.0 vs 3.5 on gcc) match the README. I marked the \~3.5x ratio as derived and added the MSVC and Emscripten/libc++ rows, which show larger gaps. Metadata checks out: MIT, 42 stars, last commit 2026-09-05.
- **Fields the verifier corrected:** `baseline_stdlib`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cschreib/observable_unique_ptr#speed-benchmarks>
  - <https://github.com/cschreib/observable_unique_ptr>
  - <https://github.com/cschreib/observable_unique_ptr/blob/main/tests/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/cschreib/observable_unique_ptr>
  - <https://github.com/cschreib/observable_unique_ptr#speed-benchmarks>
  - <https://github.com/cschreib/observable_unique_ptr/blob/main/CMakeLists.txt>
  - <https://github.com/cschreib/observable_unique_ptr/blob/main/include/oup/observable_unique_ptr.hpp>
  - <https://github.com/cschreib/observable_unique_ptr/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/cschreib/observable_unique_ptr`) · [data/wave1/enrich/raw/github_com_cschreib_observable_unique_ptr.json](../../../data/wave1/enrich/raw/github_com_cschreib_observable_unique_ptr.json) (enrichment confidence 0.82)

</details>
