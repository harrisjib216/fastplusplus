# Direct-indexed std::array maps in the matching-engine order book (Building Low Latency Applications with C++ companion code)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Matching-engine order book using preallocated direct-indexed std::array maps instead of std::unordered_map; about 7% fewer cycles in the book's run.

| | |
|---|---|
| **Beats** | std::unordered_map (nested std::unordered_map&lt;ClientId, std::unordered_map&lt;OrderId, MEOrder\*&gt;&gt; and std::unordered_map&lt;Price, MEOrdersAtPrice\*&gt; in UnorderedMapMEOrderBook) |
| **Claimed result** | Book, relayed by the seed lead and not present on the repo page: 142650 RDTSC cycles per operation with array maps against 152457 with std::unordered_map, i.e. the unordered_map version about 6 to 7% slower (array version about 1.07x faster, derived). |
| **Workload** | 100,000 pre-generated client requests (alternating NEW and CANCEL of a random earlier order, prices within 10 ticks of a random base) applied to one limit order book; RDTSC cycles around each add() and cancel() call; MEOrderBook (std::array maps indexed by order id and price modulo 256) against UnorderedMapMEOrderBook, which differs only in those two map members. |
| **Metric** | latency |
| **Hardware** | four-core ThinkPad X1 Carbon laptop at about 2.6 GHz (from the book via the seed lead; CPU model not stated) |
| **Compiler and flags** | g++ pinned in CMakeLists.txt (README lists GCC 11.3.0), -std=c++2a -Wall -Wextra -Werror -Wpedantic, built by scripts/build.sh with CMAKE_BUILD_TYPE=Release (CMake default Release flags -O3 -DNDEBUG). libstdc++ is inferred from g++ on Linux. |
| **Adoption** | 744 stars |
| **Last commit** | 2026-03-02 |
| **Links** | [repository](https://github.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP) · [benchmark](https://github.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/blob/main/Chapter12/benchmarks/hash_benchmark.cpp) |

## Verdict

The book reports 142650 against 152457 RDTSC cycles per operation (as printed, which is half the per-call figure) for the array-indexed book against the std::unordered_map copy, about 1.07x, on 100,000 alternating NEW and CANCEL requests for one client and one ticker, run on a four-core ThinkPad X1 Carbon at about 2.6 GHz with g++ (GCC 11.3.0 listed) and libstdc++. The harness and both variants are in the repo but no results are, and the timed region is dominated by logging and queue writes shared by both books, so the figure is first-party and says little about raw lookup cost.

## Use it when

- Keys are dense integers you assign yourself with a hard, small upper bound (exchange-assigned order ids, session or client slots, instrument ids) and the lookup sits on a latency-critical path.
- Inserts and removals are frequent and you want no allocation per operation.
- You can reserve the worst-case table up front and rely on lazily committed pages, so only touched entries cost resident memory.
- Price-level lookup in a book whose resting prices are guaranteed to stay inside a window narrower than the table (256 ticks here).

## Skip it when

- Sparse, unbounded or client-supplied keys: the order table is indexed by the raw client order id, and an id at or above 1,048,576 makes .at() throw inside a noexcept function, which terminates the process (issue #9 reproduces this with order id 2000000).
- Prices spanning 256 or more ticks: price % 256 has no collision handling, so levels 256 ticks apart, even on opposite sides, share a slot and get spliced together, which issue #9 reports ending in a SIGSEGV; the unordered_map variant keys on the same price % 256 index and shares the bug.
- Memory-constrained hosts or strict overcommit: each MEOrderBook carries about 2 GiB of pointers, the MatchingEngine constructor allocates one book per ticker (8), and each book's 1,048,576-entry MemPool&lt;MEOrder&gt; is filled at construction.
- When you need a general associative container (arbitrary key types, iteration over live entries, a size): this is a fixed table embedded in one class.
- When you expect a large payoff: the book's comparison shows only about 7% on add and cancel calls whose time is mostly logging and queue writes.

## How it is fast

Direct addressing: when keys are small dense integers with a known upper bound, the key itself is the slot index, so a lookup is one bounds-checked array access with no hashing, no bucket-chain walk and no node allocation on insert, and erase is a nullptr store. MEOrder and MEOrdersAtPrice objects come from preallocated MemPool arrays in both variants, so the two books differ only in the lookup structure. The price is memory sized for the worst case, about 2 GiB of pointers per order book.

## Compared with alternatives

The catalogued hash maps (absl::flat_hash_map, boost::unordered_flat_map, ankerl::unordered_dense) are general replacements for std::unordered_map with measured 2.4x to 6x gains; pick direct indexing only when the keys are bounded dense integers you assign yourself and you want no hashing at all, accepting worst-case memory and adding the bounds checks and collision handling this code lacks.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none outside the repo's own Chapter12 common/ headers (MemPool, Logger, LFQueue, types, rdtsc helpers) and pthread |
| **Minimum toolchain** | C++20 (-std=c++2a); CMakeLists.txt pins g++ and builds with -Wall -Wextra -Werror -Wpedantic, Release adds CMake's -O3 -DNDEBUG; the README lists GCC 11.3.0 on Linux |
| **Platforms** | Linux on x86-64: rdtsc is inline x86 assembly and thread pinning uses pthread_setaffinity_np; the README lists Linux only |
| **Thread safety** | none internal: each order book is meant to be driven only by the matching-engine thread |
| **Drop-in for the baseline** | partial — same order-book API and same lookups as UnorderedMapMEOrderBook, but only for integer keys below the compile-time bounds (256 clients, 1,048,576 order ids, 256 price slots); not a general std::unordered_map replacement |

## Gotchas

- The MEOrderBook constructor does not initialise cid_oid_to_order_ or price_orders_at_price_ (no member initialisers; only the destructor fills them with nullptr), so the tables read as empty only because a fresh multi-GiB allocation comes back as zeroed pages; a book built in recycled heap memory would return garbage pointers (reading of the source).
- hash_benchmark.cpp times 100,000 add() and cancel() calls but divides the RDTSC total by loop_count \* 2 (200,000), so the printed 'cycles per operation' is half the real per-call average; the ratio between the two books is unaffected.
- The timed calls include always-on logging common to both books: every add or cancel runs std::stringstream toString(), ctime()/sprintf timestamps and character-by-character Logger pushes via sendClientResponse, sendMarketUpdate and END_MEASURE, so map work is a small slice of each call, and the gap comes from one run with the array book always first.
- The unordered_map variant never erases: removal writes nullptr through operator[], and a cancel for an unknown order inserts a default entry, so that map only grows.

## Known shortcomings

- Book cycle numbers only. The two order books differ only in their map members, but the timed region includes always-on END_MEASURE logging and queue pushes; build.sh also builds a Debug tree. Code unchanged since 2023-08-14.
- Enricher: printed cycles per op are half the real value (divides by 200,000 for 100,000 calls); timed calls dominated by string formatting and logging; uninitialised std::array tables (undefined behaviour); open issue #9: price slot collisions SIGSEGV and order ids &gt;= 1048576 terminate via .at() in noexcept, in both variants.

## Caveats and trade-offs

[verify] Checked the two order books by diff: they differ only in the two map members (std::array&lt;std::array&lt;MEOrder\*, 1M&gt;, 256&gt; and std::array&lt;MEOrdersAtPrice\*, 256&gt; against nested std::unordered_map and std::unordered_map&lt;Price, ...&gt;), the array variant using bounds-checked .at() and the unordered_map variant using operator[] (which inserts default entries on cancel lookups of unknown orders) plus one extra find() in getOrdersAtPrice. The timed add()/cancel() calls also include the always-on END_MEASURE macro (rdtsc, getCurrentTimeStr and a Logger::log call) and the matching engine's client-response and market-update queue pushes, in both variants, which explains why map work is a small slice of each operation. scripts/build.sh builds both a Release (-O3 -DNDEBUG from CMake) and a Debug tree; which binary the book ran is not stated. The last code change in the repository was 2023-08-14; the 2025-2026 commits only edit README banners. [retier] Enricher: hash_benchmark divides the RDTSC total by loop_count\*2 (200,000) but times 100,000 calls, so the printed cycles per operation are half the real figure (the ratio is unaffected). The timed calls are dominated by stringstream toString, ctime/sprintf timestamps and char-by-char Logger pushes; single run, array book always first. The MEOrderBook constructor leaves both std::array tables uninitialised (undefined behaviour; it works only on zeroed fresh pages). Open issue #9 (2026-07-04, no reply): price % 256 slots have no collision handling (SIGSEGV), and an order id &gt;= 1048576 makes .at() throw inside noexcept (terminate), in both variants.

Direct indexing needs bounded dense ids and compile-time sizes (ME_MAX_NUM_CLIENTS 256 x ME_MAX_ORDER_IDS 1048576 pointers is about 2 GiB per order book, trading memory for no hashing and no allocation; the price index is price modulo ME_MAX_PRICE_LEVELS (256) in both book variants).

## Maintenance

The order-book code has not changed since 2023-08-14 (later commits only edit README banners) and issue #9, which reports the price-slot collision and order-id crashes, has no reply; MIT-licensed teaching code, fine as a source for the direct-indexing idea but not to deploy as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter12/benchmarks/hash_benchmark.cpp runs MEOrderBook (std::array maps) and UnorderedMapMEOrderBook (std::unordered_map) on the same 100,000 requests and prints RDTSC cycles, and the build files pin g++ with Release flags, but no results are committed and the CPU model is not public; the 142650 versus 152457 cycle figures are the book's own, so first-party tier C.
- **Verifier notes:** Numbers are book-only (not in repo); harness and build verified. Metadata confirmed: MIT, 744 stars, not a fork, last commit 2026-03-02 (README banner removal), so active by the commit rule though code is unchanged since 2023-08-14. Idiom difference (preallocated direct-indexed arrays against node-based std::unordered_map), about 1.07x.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/benchmarks/hash_benchmark.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/scripts/build.sh>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/me_order_book.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/me_order_book.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/unordered_map_me_order_book.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/unordered_map_me_order_book.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/me_order.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/perf_utils.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/types.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/LICENSE>
  - <https://github.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP>
  - <https://github.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/benchmarks/hash_benchmark.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/scripts/build.sh>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/me_order_book.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/me_order_book.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/unordered_map_me_order_book.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/unordered_map_me_order_book.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/me_order.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/matching_engine.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/exchange/matcher/matching_engine.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/perf_utils.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/macros.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/types.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/lf_queue.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/mem_pool.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/logging.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/time_utils.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/Chapter12/common/thread_utils.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/HEAD/README.md>
  - <https://github.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/issues/9>
  - <https://github.com/PacktPublishing/Building-Low-Latency-Applications-with-CPP/issues/4>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-building-low-latency-applications-with-cpp-array-indexed-order-book-maps`) · [data/wave1/enrich/raw/paper_book_building_low_latency_applications_with_cpp_array_indexed_order_book_maps.json](../../../data/wave1/enrich/raw/paper_book_building_low_latency_applications_with_cpp_array_indexed_order_book_maps.json) (enrichment confidence 0.75)

</details>
