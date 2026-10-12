# SimpleSignal

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `CC0-1.0` · 🔴 abandoned

> 223-line CC0 header of single-threaded C++11 signals; beats Boost.Signals2 (st) and libsigc++ in a community MSVC shootout.

| | |
|---|---|
| **Beats** | Boost.Signals2 (single-thread build) and libsigc++ |
| **Claimed result** | MSVC thread-unsafe table: emission 137,345 vs Boost Signals2 st 44,228 (3.1x) and libsigcplusplus 72,139 (1.9x); score 170,724 vs 62,979 (2.7x) and 80,450 (2.1x); connect 9,994 vs 3,655 (2.7x) vs Boost Signals2 st; construction 4,897 vs 286 (17x) and destruction 6,766 vs 592 (11x) vs Boost Signals2 st, but those two columns are excluded from the score. Ratios derived from page data. Higher is better (samples per unit time over sizes [2, 64]). |
| **Workload** | Community signal-slot shootout (NoAvailableAlias/signal-slot-benchmarks), MSVC (Windows) results, thread-unsafe table: construction, destruction, connect, disconnect, reconnect, N-slot emission, combined and threaded runs over sample sizes [2, 64]; higher score is better. |
| **Metric** | throughput |
| **Compiler and flags** | Visual Studio 2019 x64 release build (stated for the size metrics only; flags not stated); C++17 and Boost needed to build the suite |
| **Adoption** | 179 stars |
| **Last commit** | 2019-07-24 |
| **Links** | [repository](https://github.com/larspensjo/SimpleSignal) · [benchmark](https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/results/benchmarks_msvc/README.md) |

## Verdict

In NoAvailableAlias/signal-slot-benchmarks (MSVC, Visual Studio 2019 x64 release, flags, CPU and Boost version not stated), SimpleSignal's thread-unsafe-table averages over N = 2..64 handlers are emit 137,345 vs Boost Signals2 st 44,228 (3.1x) and libsigc++ 72,139 (1.9x), connect 9,994 vs 3,655 (2.7x), disconnect 9,745 vs 9,734 (tie), combined 4,619 vs 2,265 (2.0x) and 1,201 (3.8x), for a total score of 170,724 vs 62,979 and 80,450 (derived from page data). Harness caveat: each emit sample is one 2-64-handler emission between two high_resolution_clock::now() calls and the score truncates the mean to whole nanoseconds (size_t limit/count) before inverting, so the emit column, which makes up 80% of SimpleSignal's score, clusters at 130,000-137,345 for 14 of 24 thread-unsafe libraries and does not separate lightweight implementations.

## Use it when

- Single-threaded event plumbing (UI, game loop, tool code) where a handful of handlers are connected once and emitted often, and Boost.Signals2's features are not needed.
- Projects that want a vendorable public-domain (CC0) header with no dependencies beyond the standard library and only C++11.
- Replacing Boost.Signals2 in its single-thread configuration or libsigc++ where profiling shows connect or emit overhead: the shootout shows 2.7x faster connect and 3.1x faster emit than Boost Signals2 st on MSVC.
- Handlers that take arguments by reference or pointer (as the benchmark's Rng& does), so per-slot argument copies cost nothing.

## Skip it when

- Any handler that may disconnect itself or another handler while emit() is running: since the 2018 std::list rewrite this erases list nodes under the running range-for (use-after-free, skipped handlers), even though the header comment still promises it is safe.
- Multi-threaded code: nothing is synchronised; connect, disconnect and emit from different threads race.
- When you need the fastest lightweight signal: in the same shootout jeffomatic jl_signal (score 415,278), vdksoft signals st (309,575), Nuclex Events (215,607) and nano-signal-slot st (196,413) all score higher, and on the combined connect/emit/disconnect column SimpleSignal (4,619) ranks 17th of 24, about 5.4x behind jl_signal (24,950).
- Code that needs automatic disconnection when the receiver dies, scoped connections, slot groups or blocking: none exist, and IDs must be stored and disconnected by hand.
- Long-lived projects: the repo has had no commits since 2019-07-24, no issues ever filed and no test for recursion or disconnect-during-emit.

## How it is fast

Since a 2018 pull request (#4, leira) each signal is a plain std::list of std::shared_ptr&lt;std::function&gt;, and emit() is a range-for over that list with no locking, no connection bookkeeping and no reference counting per step; that PR reported 4.7 ns per emission versus 22.4 ns for Tim Janik's original ref-counted linked ring. There is no mutex, no slot-group ordering, no tracked-object checks and no combiner machinery, which is where Boost.Signals2 spends its time even in its dummy-mutex build. The signal object is 16 bytes on MSVC (a std::list).

## Compared with alternatives

The siblings (Delegate, stdext::inplace_function, SmallFunction, woid, sy_callback.hpp) replace a single std::function; SimpleSignal is a multicast list built on std::function, so pick it only when you need one-to-many callbacks with result collectors, and consider storing one of those faster delegates instead of std::function if you patch it. CDRC and observable_unique_ptr solve ownership, not callbacks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library: &lt;memory&gt;, &lt;functional&gt;, &lt;list&gt;, &lt;vector&gt;, &lt;algorithm&gt;) |
| **Minimum toolchain** | C++11 (test.cpp builds with g++ -std=gnu++11; the shootout built it with Visual Studio 2019 x64 under C++17) |
| **Platforms** | any platform with a C++11 standard library |
| **Thread safety** | None: no locking anywhere; a signal must be used from one thread (the shootout lists it as not thread-safe and runs no threaded test for it). |
| **Drop-in for the baseline** | partial — same connect/disconnect/emit idea, but connect returns a size_t ID instead of a boost::signals2::connection, there are no scoped connections, tracking, groups or shared_connection_block, and the default return-value collector returns the last result rather than an optional. |

## Gotchas

- Disconnect during emission is undefined behaviour in the current code (and in the copy the shootout benchmarked): disconnect() runs std::remove_if plus erase on the std::list that emit() is iterating, and emit() holds only a reference to the current shared_ptr. If the last handler disconnects itself, its list node is freed and the loop then increments a dangling iterator; if an earlier handler disconnects itself, its std::function is destroyed while executing and the next handler is skipped for that emission. The original ref-counted ring (removed in PR #4, August 2018) deferred deletion and was safe; the header's 'safe against recursion, so callbacks may be removed ... during a signal emission' comment was not updated, and the leftover if (slot) check never fires.
- Connection IDs are the heap address of the stored std::function (size_t(ptr.get())); after a disconnect the allocator can hand the same address to a later connect, so a stale ID can disconnect an unrelated newer handler.
- Each connect costs two heap allocations (the std::list node and the make_shared block), plus any heap storage std::function needs for a large callable; disconnect is a linear scan of the whole list, so removing all N handlers is O(N^2).
- Arguments are taken by value in emit() and again per handler in the internal invoke() and std::function call, so a by-value std::string parameter is copied several times per emission; use const references in the signature. Handlers connected during an emission are appended and called in that same emission.

## Known shortcomings

- NoAvailableAlias signal-slot-benchmarks (MSVC page, no CPU or flags): ranks 15th of 24, emit 137,345 within 1% of 8 libraries, constructor/destructor excluded from the score; the suite lists std::vector but the library uses std::list; baselines are Boost.Signals2 and libsigc++, not std::function. No spec category fits signals; filed with the std::function-row libraries under smart-pointers-and-refcount.
- Enricher: PR #4 (Aug 2018) swapped the ref-counted ring for std::list&lt;shared_ptr&lt;std::function&gt;&gt;, so disconnect() erases nodes under emit()'s range-for (self-disconnect during emit is a use-after-free on the last slot or skips the next slot) while the header still promises recursion safety. The benchmark score truncates the mean to whole nanoseconds before inverting, emit samples are one emission of 2-64 handlers, emit is 80% of the score and 14 of 24 thread-unsafe libraries cluster at 130k-137k; combined column 17th of 24. Leads: jl_signal, vdksoft/signals, nano-signal-slot.

## Caveats and trade-offs

Ranks 15th of 24 libraries by score in the thread-unsafe table; jeffomatic jl_signal (415,278), vdksoft signals st (309,575), Nuclex Events (215,607) and nano-signal-slot st (196,413) all score higher. Its emission figure (137,345) is the highest in the column but within 1% of eight other libraries (mwthinker Signal 137,227, jl_signal 136,499, Wink-Signals 136,024, Nuclex 135,934), so emission is at a shared ceiling and the large ratios are against Boost.Signals2 and libsigc++ rather than against other lightweight signals. Construction and destruction are marked 'excluded from scoring'; the score is the sum of connect, disconnect, reconnect, emit, all and threaded (threaded is 0 for every thread-unsafe library). Windows MSVC results only (refreshed May-June 2020 per the suite's commits); the GCC page is marked 'HELP NEEDED' and has no SimpleSignal row. CPU, compiler flags and Boost version are not stated, and the suite's own foreword says the benchmarks do not depict real-world usage. The suite's metadata row lists SimpleSignal's data structure as std::vector, but the library (and the vendored copy, identical to upstream except a const on size()) stores a std::list of std::shared_ptr&lt;std::function&gt;. The original Simple::Signal comparison (Tim Janik's testbit.eu post, referenced from the README) was not opened; the repo's own test.cpp times only Simple::Signal against a plain callback loop and publishes no numbers. Repo last updated 2019-07-24. CC0-1.0 dedication: no patent grant. The seed's guessed category (serialization-json) was wrong; this is a signal/slot (observer callback) library.

Single header of under 300 lines (SimpleSignal.h, public-domain CC0 code by Tim Janik, packaged on GitHub by Lars Pensjo); callbacks stored in a std::vector, signal object is 16 bytes. Not thread-safe, and none of Boost.Signals2's extras (blocking handlers, tracking of connected object lifetimes, cross-thread emission).

## Maintenance

Abandoned since 2019-07-24 (26 commits, no issues filed); CC0 public domain and small enough to vendor, but patch disconnect() (defer removal, for example by nulling the slot and compacting after emission) before relying on the header's recursion-safety promise.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent community shootout (NoAvailableAlias/signal-slot-benchmarks, run by the nano-signal-slot author, not SimpleSignal's) with public harness code (benchmark.hpp, benchmark/hpp/benchmark_lss.hpp, vendored lib/larspensjo/SimpleSignal) showing SimpleSignal ahead of Boost Signals2 st and libsigc++; only 'Visual Studio 19 x64 release' is stated and flags and CPU are not, so it falls short of A.
- **Verifier notes:** All numbers match the SimpleSignal, Boost Signals2 st and libsigcplusplus rows on the MSVC results page; metadata confirmed (179 stars, 42 forks, CC0-1.0, not a fork, 26 commits, last commit 2019-07-24, so abandoned). No spec category fits exactly: signals-and-callbacks is off-spec; the closest Wave 1 category is smart-pointers-and-refcount (its std::function row, where delegate, sy_callback.hpp, SmallFunction and woid are filed), though SimpleSignal's baseline is Boost.Signals2/libsigc++ rather than std::function, so keep baseline_in_list false and consider a category override to smart-pointers-and-refcount with that shortcoming recorded.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** signal-slot-benchmarks (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/results/benchmarks_msvc/README.md>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/results/benchmarks_gcc/README.md>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark.hpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark/hpp/benchmark_lss.hpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark/hpp/benchmark_sss.hpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark/lib/larspensjo/SimpleSignal/SimpleSignal.h>
  - <https://github.com/NoAvailableAlias/signal-slot-benchmarks>
  - <https://github.com/NoAvailableAlias/signal-slot-benchmarks/commits>
  - <https://github.com/NoAvailableAlias/signal-slot-benchmarks/tree/master/benchmark>
  - <https://github.com/NoAvailableAlias/signal-slot-benchmarks/tree/master/benchmark/lib>
  - <https://github.com/NoAvailableAlias/signal-slot-benchmarks/tree/master/benchmark/hpp>
  - <https://github.com/larspensjo/SimpleSignal>
  - <https://github.com/larspensjo/SimpleSignal/commits>
  - <https://raw.githubusercontent.com/larspensjo/SimpleSignal/HEAD/README.md>
  - <https://raw.githubusercontent.com/larspensjo/SimpleSignal/HEAD/SimpleSignal.h>
  - <https://raw.githubusercontent.com/larspensjo/SimpleSignal/HEAD/test.cpp>
- **Sources the enricher read:**
  - <https://github.com/larspensjo/SimpleSignal/commits>
  - <https://github.com/larspensjo/SimpleSignal/issues?q=is%3Aissue>
  - <https://github.com/larspensjo/SimpleSignal/pull/4>
  - <https://github.com/larspensjo/SimpleSignal/pull/4/files>
  - <https://raw.githubusercontent.com/larspensjo/SimpleSignal/HEAD/README.md>
  - <https://raw.githubusercontent.com/larspensjo/SimpleSignal/HEAD/SimpleSignal.h>
  - <https://raw.githubusercontent.com/larspensjo/SimpleSignal/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/results/benchmarks_msvc/README.md>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark.hpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark_utility.hpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark/hpp/benchmark_lss.hpp>
  - <https://raw.githubusercontent.com/NoAvailableAlias/signal-slot-benchmarks/HEAD/benchmark/lib/larspensjo/SimpleSignal/SimpleSignal.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/larspensjo/simplesignal`) · [data/wave1/enrich/raw/github_com_larspensjo_simplesignal.json](../../../data/wave1/enrich/raw/github_com_larspensjo_simplesignal.json) (enrichment confidence 0.75)

</details>
