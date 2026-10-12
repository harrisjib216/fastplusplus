# xenium

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only lock-free MPMC queue templates (Michael-Scott, Ramalhete, Vyukov) beating std::mutex latency 2.5-5.7x.

| | |
|---|---|
| **Beats** | std::mutex |
| **Claimed result** | xenium::ramalhete_queue mean round-trip latency 56ns vs std::mutex 320ns -&gt; \~5.7x lower; xenium::vyukov_bounded_queue 60ns (\~5.3x lower); xenium::michael_scott_queue 128ns (\~2.5x lower). |
| **Workload** | Same third-party SPSC/MPMC round-trip ping-pong benchmark as the atomic_queue shootout, on AMD Ryzen 5950X; xenium's michael_scott_queue, ramalhete_queue and vyukov_bounded_queue implementations were each run in place of the SPSC/MPMC queue. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 5950X, Linux, mitigations=off |
| **Compiler and flags** | gcc-14.2.0, -march=native -O3 -mtune=native -DNDEBUG (reference Makefile BUILD=release, commit 632bae1) |
| **Adoption** | 657 stars |
| **Last commit** | 2025-07-29 |
| **Links** | [repository](https://github.com/mpoeter/xenium) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html) |

## Verdict

Independent third-party shootout (max0x7ba/atomic_queue benchmarks.cc, gcc-14.2.0, xenium commit f6416d3, -O3 -march=native -mtune=native, libstdc++, AMD Ryzen 5950X, mitigations=off) measured mean round-trip ping-pong latency of 56ns for ramalhete_queue, 60ns for vyukov_bounded_queue, and 128ns for michael_scott_queue against 320ns for std::mutex — roughly 5.7x, 5.3x, and 2.5x lower respectively; xenium's own benchmark suite has no std::mutex comparison.

## Use it when

- Low-latency SPSC/MPMC ping-pong or handoff paths where std::mutex+std::queue's lock overhead dominates (measured 56-128ns vs 320ns round trip)
- Fixed, known-capacity workloads where an allocation-free bounded ring buffer is acceptable -&gt; vyukov_bounded_queue
- Value types that are raw pointers, std::unique_ptr, or small trivially copyable PODs and you want the fastest of the three -&gt; ramalhete_queue
- Arbitrary movable value types where ramalhete_queue's type restriction is unacceptable and you can absorb per-push allocation -&gt; michael_scott_queue
- C++17 codebases willing to vendor a header-only dependency and explicitly choose a reclamation-scheme policy

## Skip it when

- High push contention with ramalhete_queue: an open, maintainer-confirmed double-free bug in the node destructor when pop_idx/push_idx wrap (issue #44, opened Oct 2025, unresolved)
- Object destructors that themselves push to a xenium queue using the same reclamation scheme can recurse into reclamation and double-destruct (issue #41, open; workaround is using a different reclaimer per structure)
- Repo has had no commits in \~14 months (last push 2025-07-29); treat as stale, not actively developed
- Need arbitrary non-trivial value types and want the fastest queue: ramalhete_queue's type restriction (pointer-like or small trivially copyable) rules it out
- Teams that want to avoid template-heavy header-only code and reclamation-scheme decisions versus the simplicity of std::mutex+std::queue

## How it is fast

ramalhete_queue implements Ramalhete & Correia's FAAArrayQueue: array-segmented linked-list nodes with fetch-and-add push/pop index cursors instead of a CAS per element, cutting contention on the fast path. michael_scott_queue is the classic Michael & Scott (1996) CAS-based lock-free linked-list queue. vyukov_bounded_queue uses Vyukov's bounded MPMC ring-buffer design with per-slot sequence numbers so producers and consumers avoid contending on shared head/tail counters. In the benchmark that produced these numbers, both node-based queues were configured with xenium::reclamation::new_epoch_based (confirmed in atomic_queue's benchmarks.cc), avoiding hazard-pointer-style per-op bookkeeping.

## Compared with alternatives

Pick xenium when you also want a reusable library of composable reclamation schemes (hazard pointers, epoch-based, stamp-it) shared across other lock-free structures like hash maps and sets, not just a queue; atomic_queue and moodycamel::ReaderWriterQueue are narrower, simpler, and measured faster (33-51ns) with no reclamation-scheme decision to make, and Boost.Lockfree/oneTBB trade some speed for being part of a more widely vetted, already-deployed library.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for library use (C++17 standard library only); googletest, taocpp/json, taocpp/config are only needed as submodules to build the unit tests/benchmarks |
| **Minimum toolchain** | C++17; CI validates gcc9, clang10, Visual Studio 2019 |
| **Platforms** | x86-64 confirmed in the cited benchmark (Ryzen 5950X, Linux); CI also covers Windows/VS2019; no documented architecture restriction, ARM not verified |
| **Thread safety** | not a single blanket guarantee - each operation documents its own progress guarantee individually in the Doxygen comments (e.g. push is 'lock-free, may allocate', try_pop is 'lock-free') |
| **Drop-in for the baseline** | partial — explain: API is push/try_pop/pop, not std::queue's interface; michael_scott_queue and ramalhete_queue require choosing a reclamation-scheme template policy, and vyukov_bounded_queue requires a fixed capacity at construction |

## Gotchas

- Open, maintainer-confirmed bug: ramalhete_queue's node destructor can double-free under high push contention when pop_idx/push_idx wrap around (issue #44, unresolved as of this writing)
- Pushing to a queue from inside an object's destructor while that object is being reclaimed by the same scheme can recurse and double-destruct (issue #41); maintainer recommends a different reclamation scheme per data structure
- ramalhete_queue only accepts raw pointers, std::unique_ptr (custom deleters not yet supported), or trivially copyable types no larger than a pointer
- stamp_it reclaimer emits -Winvalid-memory-model warnings under gcc12 with -Werror (issue #26, open since 2022, documented one-line workaround)

## Caveats and trade-offs

Evidence is entirely from the independent max0x7ba/atomic_queue shootout, not from xenium's own repo (which has no README benchmark section vs std::mutex). Repo has had no commits in over a year (last push 2025-07-29), so treat as stale rather than actively maintained, though the code itself is described by other users as feature-complete. [retier] Compiler and CPU are stated on benchmarks.html; the flags are not on that page and come from the reference Makefile's default release build.

Requires choosing a memory-reclamation scheme (hazard pointers, epoch-based, etc.) as a template parameter, which adds API and mental overhead versus std::mutex+std::queue; michael_scott_queue and ramalhete_queue are unbounded (allocate nodes), vyukov_bounded_queue is fixed-capacity; header-only but template-heavy, can affect compile times.

## Maintenance

Stale: no commits since 2025-07-29 (\~14 months) though the maintainer still replies to issues; MIT-licensed, header-only, and small enough to vendor, but two open double-free/double-destruction bug reports (#41, #44) remain unresolved.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent atomic_queue shootout (src/benchmarks.cc; gcc-14.2.0, xenium commit f6416d3, Ryzen 5950X) shows ramalhete_queue at 56ns, vyukov_bounded_queue at 60ns and michael_scott_queue at 128ns, against 320ns for std::mutex. xenium's own benchmarks/ suite has no std::mutex baseline.
- **Retiered** B to A: atomic_queue shootout: code src/benchmarks.cc in max0x7ba/atomic_queue; gcc-14.2.0 and AMD Ryzen 9 5950X stated on benchmarks.html and in results/632bae1.ryzen_5950x.smt1.20260914T121940.gcc-14.32.33.txt; flags from the reference Makefile default BUILD=release at commit 632bae1: -march=native -O3 -mtune=native -DNDEBUG (+ -fno-stack-protector, -falign-functions=64). Independent run against std::mutex: ramalhete_queue 56ns, vyukov_bounded_queue 60ns, michael_scott_queue 127-128ns vs std::mutex 320-321ns.
- **Verifier notes:** The latency figures match the page exactly. In the throughput data, ramalhete_queue and vyukov_bounded_queue stay well ahead of std::mutex at every thread count, while michael_scott_queue is roughly at parity. Last commit 2025-07-29 (\~14 months ago), so 'stale' is correct; MIT and 657 stars verified. The 'feature-complete per other users' remark in caveats was not verified.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://max0x7ba.github.io/atomic_queue/html/benchmarks.html>
  - <https://max0x7ba.github.io/atomic_queue/html/results.js>
  - <https://github.com/mpoeter/xenium>
  - <https://github.com/mpoeter/xenium/blob/main/README.md>
  - <https://github.com/mpoeter/xenium/blob/main/benchmarks/queues.hpp>
- **Sources the enricher read:**
  - <https://github.com/mpoeter/xenium>
  - <https://github.com/mpoeter/xenium/blob/main/README.md>
  - <https://github.com/mpoeter/xenium/blob/main/xenium/ramalhete_queue.hpp>
  - <https://github.com/mpoeter/xenium/blob/main/xenium/vyukov_bounded_queue.hpp>
  - <https://github.com/mpoeter/xenium/blob/main/xenium/michael_scott_queue.hpp>
  - <https://github.com/mpoeter/xenium/issues/44>
  - <https://github.com/mpoeter/xenium/issues/41>
  - <https://github.com/mpoeter/xenium/issues/26>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/src/benchmarks.cc>
  - <https://max0x7ba.github.io/atomic_queue/html/benchmarks.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mpoeter/xenium`) · [data/wave1/enrich/raw/github_com_mpoeter_xenium.json](../../../data/wave1/enrich/raw/github_com_mpoeter_xenium.json) (enrichment confidence 0.75)

</details>
