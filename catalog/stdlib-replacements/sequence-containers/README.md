# Sequence containers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::vector, std::deque, std::list, std::array  
**12 entries:** 3 tier A · 0 tier B · 7 tier C · 2 tier D · 12 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**plf::colony (plf::hive)**](mattreecebentley-plf-colony.md) | Unordered container beating std::vector/deque/list on erase-heavy workloads via O(1) erase that never invalidates other iterators. | **A** | C++ | Zlib | 🟢 active |
| 2 | [**plf::list**](mattreecebentley-plf-list.md) | Node-clustering drop-in replacement for std::list; faster insertion, erasure, sort, and much faster clear/destruction. | **A** | C++ | Zlib | 🟢 active |
| 3 | [**ankerl::svector (martinus/svector)**](martinus-svector.md) | Single-header C++17 small vector packing 7 inline bytes into an 8-byte object; avoids std::vector's heap allocation for tiny sequences. | **A** | C++ | MIT | 🟢 active |
| 4 | [**eastl::vector (EASTL)**](electronicarts-eastl.md) | EA's from-scratch STL reimplementation for games; eastl::vector targets faster push_back/indexing than std::vector. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 5 | [**ETL static containers (etl::vector, etl::map…**](etlcpp-etl.md) | Heap-free, fixed-capacity STL-style containers (vector, map, unordered_map) for embedded C++03+; no maintained speed claim against std. | **C** | C++ | MIT | 🟢 active |
| 6 | [**CTL (C Container Template Library)**](rurban-ctl.md) | Header-only macro-templated C99/C11 copies of the STL containers; benchmarks show parity with libstdc++, not a general speedup. | **C** | C | MIT | 🟢 active |
| 7 | [**veque**](shmoopty-veque.md) | Header-only C++20 double-ended vector: std::vector's contiguous storage plus std::deque's fast front growth. | **C** | C++ | BSL-1.0 | 🟢 active |
| 8 | [**plf::stack**](mattreecebentley-plf-stack.md) | Header-only LIFO container on chained, never-relocated memory blocks; author reports it beats std::stack over std::deque. | **C** | C++ | Zlib | 🟢 active |
| 9 | [**libcdada**](msune-libcdada.md) | Pure C API (list, set, map, queue, stack, string, bitmap) wrapping libstdc++ containers; matches libstdc++ at best, never beats it. | **C** | C | BSD-2-Clause | 🟢 active |
| 10 | [**fast_vector (sigerror/fast-vector)**](sigerror-fast-vector.md) | Header-only C++17 vector without zero-init, exceptions, or a real allocator; beats std::vector on trivial-type push_back workloads. | **C** | C++ | MIT | 🔴 abandoned |
| 11 | [**sfl-library small and static containers (sfl::small_vector…**](slavenf-sfl-library.md) | Header-only C++11 small_vector, static_vector and small_flat_map that avoid heap allocation for up to N elements; no benchmark numbers. | **D** | C++ | Zlib | 🟢 active |
| 12 | [**rpp (TheNumbat/rpp) compile-time-oriented containers and…**](thenumbat-rpp.md) | Rust-style C++20 base library (Vec, Map, String, allocators, threads, async) that avoids STL headers to cut compile time. | **D** | C++ | MIT | 🟡 stale |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
