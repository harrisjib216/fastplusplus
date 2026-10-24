# C++ standard library replacements

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Containers, algorithms and utilities that beat the C++ standard library's own: hash maps, sorting, number parsing, allocators, regex and more.

**300 entries in 25 categories:** 118 tier A · 24 tier B · 143 tier C · 15 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Allocators](allocators/README.md) | 17 | 4 | 4 | 8 | 1 | std::allocator, operator new/delete, std::pmr |
| [Async tasks and thread pools](async-tasks-threadpools/README.md) | 8 | 5 | 1 | 1 | 1 | std::async, std::thread, std::future |
| [Bitsets and succinct bit vectors](bitsets-and-succinct/README.md) | 7 | 3 | 0 | 4 | 0 | std::bitset, std::vector&lt;bool&gt; |
| [Concurrent queues and locks](concurrency-queues-locks/README.md) | 9 | 6 | 0 | 3 | 0 | std::mutex, std::atomic, std::queue+mutex, std::condition_variable |
| [Graph algorithms](graph-algorithms/README.md) | 2 | 0 | 1 | 1 | 0 | NetworkX 2.4 (pure Python); SNAP 5.0.0 as a second row; Boost Graph Library (Boost.Graph… |
| [Hash maps and sets](hash-maps-sets/README.md) | 26 | 18 | 1 | 7 | 0 | std::unordered_map, std::unordered_set |
| [I/O and filesystem](io-and-filesystem/README.md) | 4 | 1 | 0 | 3 | 0 | iostreams, fstream, std::filesystem, fread/fwrite |
| [JSON serialization](serialization-json/README.md) | 17 | 7 | 0 | 9 | 1 | iostreams + std::string, std::format (record actual baseline) |
| [k-mer dictionaries](k-mer-dictionaries/README.md) | 3 | 1 | 2 | 0 | 0 | SSHash; Pufferfish (and dBG-FM, BLight k-mer dictionaries); Pufferfish |
| [Math, SIMD and linear algebra](math-simd-linear-algebra/README.md) | 25 | 5 | 3 | 14 | 3 | std::valarray, std::transform, std::reduce, &lt;cmath&gt; |
| [Minimal perfect hash functions](minimal-perfect-hash-functions/README.md) | 20 | 14 | 2 | 4 | 0 | BBHash; CMPH; RecSplit |
| [Number parsing and formatting](number-parsing-formatting/README.md) | 22 | 9 | 2 | 11 | 0 | std::to_chars, std::from_chars, std::stod, std::format, iostreams |
| [Ordered maps and trees](ordered-maps-trees/README.md) | 10 | 4 | 0 | 5 | 1 | std::map, std::set, std::multimap |
| [Perfect hashing and static tables](perfect-hash-static-tables/README.md) | 21 | 9 | 0 | 12 | 0 | std::unordered_map; gperf; phf (rust-phf) static compile-time hash maps |
| [Priority queues and heaps](priority-queues-heaps/README.md) | 5 | 4 | 0 | 1 | 0 | std::priority_queue, std::make_heap |
| [Random numbers](random/README.md) | 9 | 4 | 2 | 3 | 0 | std::mt19937, std::uniform_\*_distribution, std::shuffle |
| [Ranges and views](ranges-and-views/README.md) | 1 | 0 | 0 | 1 | 0 | std::ranges / std::views (libstdc++ 13): filter, chunk… |
| [Regex](regex/README.md) | 9 | 3 | 3 | 3 | 0 | std::regex |
| [Searching](searching/README.md) | 7 | 2 | 0 | 5 | 0 | std::lower_bound, std::binary_search, std::find, std::search |
| [Sequence containers](sequence-containers/README.md) | 12 | 3 | 0 | 7 | 2 | std::vector, std::deque, std::list, std::array |
| [Small-buffer containers and strings](small-buffer-and-strings/README.md) | 15 | 1 | 0 | 11 | 3 | std::string, std::string_view, SSO |
| [Smart pointers and reference counting](smart-pointers-and-refcount/README.md) | 10 | 3 | 2 | 4 | 1 | std::shared_ptr, std::unique_ptr, std::function |
| [Sorting](sorting/README.md) | 28 | 7 | 0 | 20 | 1 | std::sort, std::stable_sort, std::partial_sort, std::nth_element |
| [String search and hashing](string-search-and-hashing/README.md) | 10 | 5 | 1 | 4 | 0 | std::string::find, std::hash, std::search |
| [Utilities](utilities/README.md) | 3 | 0 | 0 | 2 | 1 | std::copy_if (and a hand-written for loop); ncurses (wide-char build); glibc memcpy /… |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**folly F14 (F14ValueMap)**](hash-maps-sets/facebook-folly.md) | SIMD 14-way probing hash map (F14) in Facebook's Folly library; 2-4x faster build/find/churn, 16x faster iteration than std::unordered_map. | [Hash maps and sets](hash-maps-sets/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 2 | [**{fmt}**](number-parsing-formatting/fmtlib-fmt.md) | Type-safe C++ formatting library beating printf/iostreams; its Dragonbox-based float formatter is the speed driver here. | [Number parsing and formatting](number-parsing-formatting/README.md) | **A** | C++ | MIT | 🟢 active |
| 3 | [**abseil (absl::flat_hash_map, Swiss tables)**](hash-maps-sets/abseil-abseil-cpp.md) | SwissTable-based hash map beating std::unordered_map on build, find, churn, and iteration speed. | [Hash maps and sets](hash-maps-sets/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**mimalloc**](allocators/microsoft-mimalloc.md) | General-purpose malloc drop-in replacement using sharded per-thread free lists; beats jemalloc/tcmalloc on multi-threaded workloads. | [Allocators](allocators/README.md) | **A** | C | MIT | 🟢 active |
| 5 | [**EASTL hash_map / hash_set (eastl::hash_map)**](hash-maps-sets/paper-eastl-hash-map-hash-set.md) | EA's chained hash table (eastl::hash_map/hash_set), about 1.3x faster than libstdc++ std::unordered_map in Ankerl's 2019 suite. | [Hash maps and sets](hash-maps-sets/README.md) | **A** | C++ | BSD-3-Clause | 🟢 active |
| 6 | [**oneTBB concurrent_bounded_queue**](concurrency-queues-locks/uxlfoundation-onetbb.md) | Bounded/blocking FIFO queue in Intel's oneTBB parallelism library; non-blocking try_push/try_pop mode cuts round-trip latency \~3.9x vs std::mutex. | [Concurrent queues and locks](concurrency-queues-locks/README.md) | **A** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**Highway (vqsort)**](sorting/google-highway.md) | SIMD-dispatched vectorized quicksort/quickselect for built-in key types; \~10x faster than LLVM std::sort on large arrays. | [Sorting](sorting/README.md) | **A** | C++ | Apache-2.0 OR BSD-3-Clause | 🟢 active |
| 8 | [**uthash**](hash-maps-sets/troydhanson-uthash.md) | Header-only intrusive C hash table (macros); in one third-party benchmark it iterates and erases faster than std::unordered_map but loses most lookups. | [Hash maps and sets](hash-maps-sets/README.md) | **A** | C | BSD-1-Clause | 🟢 active |
| 9 | [**klib khash (khash.h)**](hash-maps-sets/attractivechaos-klib.md) | Single-header C macro hash table (open addressing, 2-bit flags); about 4x less CPU and 3x less memory than std::unordered_map on integer counting. | [Hash maps and sets](hash-maps-sets/README.md) | **A** | C | MIT | 🟢 active |
| 10 | [**moodycamel::ReaderWriterQueue**](concurrency-queues-locks/cameron314-readerwriterqueue.md) | Header-only lock-free SPSC queue for C++11; beats a mutex-guarded queue by \~7x in ping-pong latency. | [Concurrent queues and locks](concurrency-queues-locks/README.md) | **A** | C++ | BSD-2-Clause | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
