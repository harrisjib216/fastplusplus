# cpgf callback (GCallback / GCallbackList)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Discontinued C++ callback and callback-list (signal) headers; 2011 numbers beat Boost.Signals2 and tie libsigc++ on single calls.

| | |
|---|---|
| **Beats** | Boost.Signals2 1.46.0 and libsigc++ 2.2.8 (signal/slot and callback invocation) |
| **Claimed result** | Single-slot calls (VC 9): inline member 781 ms vs Boost.Signals2 3547 ms (4.5x, derived from page data) and libsigc++ 766 ms (parity); global function 719 vs 3578 ms (5.0x, derived); functor 468 vs 3156 ms (6.7x, derived). GCC 4.5.2: inline member 1047 vs 1875 ms (1.8x, derived), functor 515 vs 1547 ms (3.0x, derived), libsigc++ about equal (1000 and 516 ms). Signal emission (VC 9): 5 slots 641 ms vs libsigc++ 2734 ms (4.3x, derived) and Boost.Signals2 8797 ms (13.7x, derived); 10 slots 1109 vs 3328 ms (3.0x vs libsigc++) and 15203 ms; 50 slots 6735 vs 7875 ms (1.17x vs libsigc++) and 64813 ms (9.6x vs Boost). GCC 5 slots: 578 vs 2547 ms (libsigc++) vs 7515 ms (Boost). |
| **Workload** | Invoking a callback bound to an inline member, non-inline member, virtual member, global function or functor taking one int (100M calls), and emitting a signal with 0, 5, 10 and 50 connected slots (10M emissions), timed with clock() on Windows XP. |
| **Metric** | throughput |
| **Hardware** | Intel Pentium Dual CPU E2180 2GHz, 4G RAM, Windows XP SP2 |
| **Compiler and flags** | VC 9 (Visual Studio 2008 Express) with -O2, _SECURE_SCL=0, _HAS_ITERATOR_DEBUGGING=0; MinGW GCC 4.5.2 with -O3. Harness source: test/benchmark/callback/benchmarkcallback.cpp in the repo. |
| **Adoption** | 221 stars |
| **Last commit** | 2022-05-22 |
| **Links** | [repository](https://github.com/cpgf/cpgf) · [benchmark](https://github.com/cpgf/cpgf/blob/master/doc/callback-benchmark.md) |

## Verdict

doc/callback-benchmark.md (migrated in 2019 from cpgf.org, harness committed 2011) times 100M single-callback calls and 10M emissions of signals with 0 to 50 slots on a Pentium Dual E2180 under Windows XP with VC 9 -O2 and MinGW GCC 4.5.2 -O3: cpgf ties libsigc++ 2.2.8 on single calls and is 1.8x to 6.7x faster than invoking a Boost.Signals2 1.46 slot; on emission it is 4.3x faster than libsigc++ at 5 slots (VC 9, 641 vs 2734 ms), 1.17x at 50 slots, and 9.6x to 13.7x faster than the default mutex-protected Boost.Signals2 signal. Those numbers belong to the pre-2017 C++03 implementation.

## Use it when

- Maintaining code that already uses cpgf (for example the author's gincu engine) and needs its callback lists.
- Single-threaded event dispatch with a handful of listeners per event, where an unsynchronized vector-of-callbacks is all you need.
- Reading a compact example of std::function-style type erasure with a function-pointer table instead of virtual functions.
- New code only if you cannot take the author's successor, eventpp, which the README recommends for the callback list feature.

## Skip it when

- Any new project: the README says cpgf is not continued and points callback-list users to eventpp (already catalogued).
- Multi-threaded emit or connect: GCallbackList has no locking and its const operator() erases cleared entries from a mutable deque during dispatch.
- When you need connection objects, scoped disconnection, slot return values or combiners, or lifetime tracking (Boost.Signals2 and libsigc++ features absent here).
- When the target is plain std::function speed: no benchmark against std::function exists, and the invoke path (base pointer, table pointer, indirect call) is not obviously cheaper.
- Signals with dozens of slots: the lead over libsigc++ falls to 1.17x (VC 9) and 1.31x (GCC) at 50 slots, within the noise of this harness.

## How it is fast

GCallback stores the target in a small inline buffer and dispatches through a static per-type table of function pointers (a hand-rolled vtable: destroy, clone, invoker, isSame), so a call is two dependent loads and one indirect call with no locking. GCallbackList is a plain std::deque of GCallback walked by index, with no mutex, no copied slot-list snapshot, no combiner and no tracked-object locking; that missing machinery is where the 4x to 14x gap to the default thread-safe Boost.Signals2 signal comes from, and lower per-emission setup is why it leads libsigc++ at 5 to 10 slots.

## Compared with alternatives

SimpleSignal is the closer sibling (also beats Boost.Signals2 and libsigc++, measured against a single-thread Boost build) and the author's own eventpp supersedes cpgf's callback list, so prefer either for new code; pick cpgf only when you already depend on it. For a single type-erased callable, the std::function replacements (inplace_function, bdiamand Delegate, SmallFunction, woid) have current benchmarks against std::function, which cpgf lacks.

## Integration

| | |
|---|---|
| **Form** | header-only (include/cpgf/gcallback.h and gcallbacklist.h plus a few cpgf utility headers: gfunctiontraits.h, gtypetraits.h, gcompiler.h, gpp.h, gtypelist.h, gassert.h, genableif.h); the rest of cpgf is a CMake-built static library |
| **Dependencies** | none beyond the C++ standard library for the callback headers |
| **Minimum toolchain** | C++11 since cpgf 1.6 (README: VC 2015 and GCC 4.9.1 tested, later GCC 7.3.0 and Clang 5.0.2 on Ubuntu 18.04); the library requires exceptions and RTTI, and an empty GCallback throws std::bad_function_call |
| **Platforms** | any (README lists Windows, Linux and macOS builds) |
| **Thread safety** | none documented; GCallbackList has no mutex and mutates its deque inside the const call operator |
| **Drop-in for the baseline** | no: different API from Boost.Signals2 and libsigc++ (no connections, combiners, slot tracking or return collection); GCallback alone is close to std::function but not a drop-in |

## Gotchas

- The published numbers measured the 2011 C++03 implementation (GCallbackList with GCallbackConnection over std::list, per the harness's commented typedef). Callback and callback list were rewritten in C++11 in March 2017 (commit history of gcallbacklist.h), while the harness (committed 2011-10-04, never updated) calls callbackList.add(&obj, &member) with two arguments, which the current one-argument add() does not accept; the harness also includes cpgf/testcase/benchmark/benchmarkcallback.h, a path that does not exist, and uses GWiseMap, which the callback headers no longer provide. The table therefore cannot be reproduced against today's code.
- Harness timing is coarse: all 64 cells are exact multiples of 15.625 ms, the Windows XP clock() tick (checked arithmetically), each cell is one run (Iterates_Generations = 1), so the single-slot cpgf vs libsigc++ differences (781 vs 766, 719 vs 672, 468 vs 438 ms) are one to three ticks and not meaningful. The 46-47 ms 'native call' rows are about one cycle per iteration at 2 GHz, so the compiler collapsed those loops rather than timing a call. Boost.Signals2 ran with its default mutex (a thread-safe signal against two unsynchronized ones; a dummy_mutex signal was not tried), and the Boost single-slot rows invoke a signals2::slot directly.
- Current GCallbackList::operator() forwards the same argument pack to every callback with std::forward inside the loop: for a by-value parameter such as void (std::string) called with an rvalue, the first slot moves the string out and later slots receive a moved-from value (read in the code; a self-written mimic of the same forwarding loop printed 'payload' then two empty strings). Its operator= overloads also lack return statements and call swap(std::move(other)) on a non-const lvalue-reference swap.
- The inline buffer is sized as one pointer plus one member-function pointer (24 bytes on x86-64 GCC/Clang), but a member-function callback stores the table pointer, object pointer and member pointer (32 bytes in a self-written layout mimic), so every member-function callback is heap-allocated on construction and on every copy (add() copies). Removing or clearing a callback from inside its own invocation destroys it mid-call.

## Known shortcomings

- Tier A on test/benchmark/callback/benchmarkcallback.cpp (VC 9 -O2, GCC 4.5.2 -O3, Pentium E2180), but the toolchain is from 2011, each cell is one clock() run, cpgf ties libsigc++ on single-slot calls, and the Boost single-slot rows time signals2::slot, not signal. Project discontinued; the author points to eventpp as the successor.
- Enricher: the 2011 numbers measured the old C++03 GCallbackList; the callback library was rewritten in C++11 in March 2017 and the harness (2011-10-04, never updated) calls a two-argument add() the current code lacks, plus a nonexistent include path and GWiseMap, so the table cannot be reproduced against today's code. All 64 cells are exact multiples of 15.625 ms (Windows XP clock() tick) from one run each, so the cpgf vs libsigc++ single-slot gaps are 1-3 ticks of noise; the native 46-47 ms rows are collapsed loops; Boost.Signals2 ran with its default mutex against two unlocked libraries. Current-code bugs (checked with self-written mimics): GCallbackList::operator() forwards the same arguments to every slot, so a by-value rvalue moves into the first slot and later slots get moved-from values; operator= overloads have no return; the 24-byte inline buffer is too small for 32-byte member callbacks, which always heap-allocate. C++11 required since 1.6, not C++03.

## Caveats and trade-offs

The numbers date from about 2011 (Pentium Dual E2180, Windows XP SP2, VC 9, MinGW GCC 4.5.2, Boost 1.46.0, libsigc++ 2.2.8) and the page itself says newer hardware will produce quite different results; newer Boost.Signals2 and libsigc++ releases were not measured. The harness runs one generation (Iterates_Generations = 1), timed with clock() at millisecond resolution, so each cell is a single run with no repeat or variance. In the single-slot rows the Boost column invokes a boost::signals2::slot object directly (slot::operator() locks tracked objects on every call), not a signal; only the signal rows use the default mutex-protected boost::signals2::signal. Single-slot cpgf calls are at parity with libsigc++ and sometimes slightly slower (VC 9: inline 781 vs 766 ms, virtual 719 vs 672 ms, functor 468 vs 438 ms; GCC: 1047 vs 1000 ms inline) and 10 to 22 times slower than an inlinable native call (46-47 ms); the clear wins are against Boost.Signals2 and in signal emission with few slots (5 slots 641 vs 2734 ms libsigc++), shrinking to 1.17x against libsigc++ at 50 slots. The page says FastDelegate code from CodeProject was 'one time faster' (about twice as fast) than cpgf callback and libsigc++ slots but left it out of the table; the harness also needs FastDelegate.h and delegate.hpp unless NO_FD and NO_SR are defined, and it includes the header under a cpgf/testcase/benchmark/ path while the repo keeps it next to the .cpp, with no build script for the benchmark. No comparison against std::function or a modern signal library. The project is discontinued: its README says it is not continued and points callback users to the author's eventpp (already listed as eventpp::SpinLock) and reflection users to metapp. The benchmark covers only the callback component, not the reflection, serialization or script-binding parts. Filed under smart-pointers-and-refcount, where the catalogue files signal and delegate libraries (same placement as larspensjo/simplesignal and bdiamand/delegate). The harness source was read but not built or rerun. [retier] 2011 table (VC 9 -O2, GCC 4.5.2 -O3, Pentium E2180) measured the pre-2017 C++03 GCallbackList; harness no longer compiles against current code. All 64 cells are multiples of the 15.625 ms clock() tick, one run each (single-slot gaps vs libsigc++ are noise); native rows are collapsed loops; Boost.Signals2 ran locked vs unlocked competitors; Boost single-slot rows time signals2::slot. Current code: operator() forwards the same arguments to every slot (moved-from values after the first), operator= overloads lack a return, member callbacks always heap-allocate. C++11 required since 1.6. Project discontinued; author points to eventpp.

Part of the larger cpgf library (reflection, serialization, Lua/V8/Python/SpiderMonkey binding, callback, tweening); the callback headers (gcallback.h, gcallbacklist.h) are the relevant piece. C++03 code base, requires C++ exceptions and RTTI per the README. The author states the project is not continued and points to eventpp for the callback list feature.

## Maintenance

Abandoned: the README says cpgf is not continued and sends callback users to eventpp and reflection users to metapp; last commit 2022-05-22, last change to the callback headers 2017-03-05; Apache-2.0 and the two callback headers are small enough to vendor, but the current GCallbackList has the forwarding and assignment bugs noted above.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now C.
- **Tier reason:** doc/callback-benchmark.md compares cpgf GCallback/GCallbackList with libsigc++ 2.2.8 and Boost.Signals2 1.46.0, and every number in claimed_speedup matches its table; the harness is public (test/benchmark/callback/benchmarkcallback.cpp plus benchmarkcallback.h), and compilers (VC 9 -O2 with _SECURE_SCL=0, MinGW GCC 4.5.2 -O3) and CPU (Pentium Dual E2180 2 GHz) are stated, which meets A.
- **Retiered** A to C: Not reproducible: the 2011 harness targets the C++03 GCallbackList that was rewritten in C++11 in 2017 and no longer compiles against current code (numbers-on-since-changed-code precedent); every cell is a single run quantised to the 15.625 ms Windows XP clock() tick, so the single-slot gaps against libsigc++ are 1-3 ticks of noise, and Boost.Signals2 ran with its default mutex against unlocked libraries.
- **Verifier notes:** Every claimed number re-derived from the page table (for example 8797/641 = 13.7x and 2734/641 = 4.3x). Metadata confirmed on github.com: Apache-2.0, 221 stars, 61 forks, not archived or a fork, last commit 2022-05-22, abandoned (README says the project is not continued). Not a duplicate of eventpp, which is a separate successor project. Shortcomings: 2011-era toolchain and library versions, single clock() run per cell, parity or slight losses against libsigc++ on single-slot calls, Boost single-slot rows time a signals2::slot rather than a signal.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 4); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/doc/callback-benchmark.md>
  - <https://github.com/cpgf/cpgf>
  - <https://github.com/cpgf/cpgf/commits>
  - <https://github.com/cpgf/cpgf/tree/master/test/benchmark>
  - <https://github.com/cpgf/cpgf/tree/master/test/benchmark/callback>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/test/benchmark/callback/benchmarkcallback.cpp>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/test/benchmark/callback/benchmarkcallback.h>
- **Sources the enricher read:**
  - <https://github.com/cpgf/cpgf>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/readme.md>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/doc/callback-benchmark.md>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/test/benchmark/callback/benchmarkcallback.cpp>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/test/benchmark/callback/benchmarkcallback.h>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/include/cpgf/gcallback.h>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/include/cpgf/gcallbacklist.h>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/include/cpgf/gfunctiontraits.h>
  - <https://raw.githubusercontent.com/cpgf/cpgf/HEAD/include/cpgf/gtypetraits.h>
  - <https://github.com/cpgf/cpgf/commits/master/include/cpgf/gcallbacklist.h>
  - <https://github.com/cpgf/cpgf/commits/master/test/benchmark/callback/benchmarkcallback.cpp>
  - <https://github.com/cpgf/cpgf/commits/master/doc/callback-benchmark.md>
  - <https://github.com/cpgf/cpgf/issues?q=is%3Aissue>
  - <https://github.com/cpgf/cpgf/issues/75>
  - <https://github.com/cpgf/cpgf/issues/83>
  - <https://github.com/cpgf/cpgf/tree/master/benchmark>
  - <https://github.com/cpgf/cpgf/tree/master/benchmark/tests>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/cpgf/cpgf`) · [data/wave4/enrich/raw/github_com_cpgf_cpgf.json](../../../data/wave4/enrich/raw/github_com_cpgf_cpgf.json) (enrichment confidence 0.75)

</details>
