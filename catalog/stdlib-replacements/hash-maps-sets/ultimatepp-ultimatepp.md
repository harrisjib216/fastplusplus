# Ultimate++ (U++ Core: VectorMap, String, Stream, heap)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> U++ framework's VectorMap/Index hash containers plus String and heap; 1.8-2.4x over std::unordered_map in a first-party word-index test.

| | |
|---|---|
| **Beats** | std::map and std::tr1::unordered_map with std::string and std::ifstream (libstdc++ shipped with GCC 4.1.3) |
| **Claimed result** | 2007 vsstd page: U++ Core 4.5x to 5.1x vs std::map and tr1::unordered_map (GCC 4.1.3 -O3, Core 2 Duo 2.7 GHz, mixed container, stream and allocator effects); 2020 idmapBench rerun about 2.4x (U++ heap) and 1.8x (malloc) with unequal tokenizing and I/O on the two sides; SortedVectorMap 1.11x slower than std::map. |
| **Workload** | Scan a C source file, collect every C identifier with the lines where it occurs, and sort the identifiers by name, repeated 10000 times with output omitted; U++ VectorMap&lt;String, Vector&lt;int&gt;&gt; and FileIn vs std::map and tr1::unordered_map with std::string and std::ifstream, both with the standard heap and with the U++ allocator. |
| **Metric** | throughput |
| **Hardware** | Core 2 Duo, 2.7 GHz, 2GB RAM (no CPU model number given) |
| **Compiler and flags** | GCC 4.1.3 20070929 prerelease (Ubuntu 4.1.2-16ubuntu2) on Ubuntu 7.10 i386 and AMD64, -O3; benchmark defines NDEBUG; the page does not say how the standard-allocator runs were built (the current benchmark package uses the U++ USEMALLOC config flag). 2020 rerun: CLANGx64 Release (Blitz, full debug info), flags not listed. |
| **Adoption** | 994 stars on the GitHub mirror; U++ framework in continuous development since the early 2000s |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/ultimatepp/ultimatepp) · [benchmark](https://raw.githubusercontent.com/ultimatepp/ultimatepp/HEAD/uppbox/uppweb/www.tpp/vsstd_en-us.tpp) |

## Verdict

First-party only: the 2007 vsstd page times 10,000 passes of an identifier index (scan a .cpp file, map each identifier to its line list, sort) built with GCC 4.1.3 -O3 against libstdc++'s pre-GCC-5 copy-on-write std::string, std::map and tr1::unordered_map on an unnamed 2.7 GHz Core 2 Duo, reporting U++ 4.5-5.1x faster (3.5-4.1x when the STL also runs on the U++ heap). The repo's 2020 rerun (benchmarks/idmapBench/info.txt, CLANGx64 Release on Windows, probably libc++ via U++'s llvm-mingw toolchain, hardware and flags not stated; 1000 passes over alice30.txt) gives VectorMap 1.37 s vs std::unordered_map 3.27 s (2.4x) on the U++ heap and 2.26 s vs 4.06 s (1.8x) with malloc for both, reading the printed 'ms' figures as the microseconds TimeStop returns (derived from page data); U++'s own SortedVectorMap was 1.11x slower than std::map in the same run.

## Use it when

- The program already uses U++ (TheIDE or umk builds) and needs string-keyed maps on a hot path: VectorMap&lt;String, T&gt; with GetAdd/FindAdd is the idiomatic choice there.
- Build-once, insertion-ordered dictionaries such as identifier or word indexes, symbol tables and string interning, where contiguous keys and positional access (GetKey(i), GetSortOrder(map.GetKeys())) make iteration and sorting cheap.
- Short string keys of 14 bytes or fewer, which stay in U++ String's inline buffer; this is exactly the case the first-party benchmark exercises.
- Allocation-heavy code where adopting the U++ heap is acceptable: in the 2020 rerun the heap alone made the std::unordered_map pass 1.24x faster (4.06 s to 3.27 s per 1000 passes, derived from page data).

## Skip it when

- You want a standalone std::unordered_map replacement: using VectorMap means adopting U++ Core types, its build system and a heap that replaces global new/delete for the whole program.
- Code that keeps references, pointers or iterators into the map across inserts: Index documents that Add invalidates both, and VectorMap values live in a Vector that moves on growth (ArrayMap or std::unordered_map keep them stable).
- Large maps or adversarial keys without your own measurement: the only benchmark uses about 3,000 distinct keys, and a 2019 U++ forum reply (search snippet only, forum unreachable) reported Index find time rising from 250 ms to 2 minutes when the item count grew 10x because of hash clustering; whether today's FoldHash code still behaves that way is not documented.
- Key or value types that are not trivially relocatable (self-referencing types, many std types) unless marked is_upp_guest, which falls back to move-construct plus destroy.
- More than 2^31-1 entries or big-endian targets: Vector stores int counts, Index uses int links, and Core's config.h stops with 'Big endian CPUs are not supported anymore'.

## How it is fast

Index is array-based separate chaining: keys sit contiguously in a Vector, a parallel array holds a {next, hash, prev} record per entry forming circular doubly linked bucket chains, and a power-of-two array of int bucket heads is rebuilt from the stored hashes (keys are not rehashed) when the count reaches the mask. Hashes are folded by a multiply and byte swap (FoldHash), and String keys of up to 14 bytes are stored inline, so hashing and equality for them are two 64-bit word operations with no heap traffic. Vector growth relocates elements with memcpy because element types must be trivially relocatable, and global new/delete go to the U++ heap (23 small size classes carved from 4 KB pages, free-block caches, buffered cross-thread frees), which also speeds up STL containers in the same program.

## Compared with alternatives

Pick VectorMap when the code base already uses U++ (or wants its String, streams and heap anyway) and an insertion-ordered, position-addressable map is useful. For a standalone std::unordered_map replacement that does not take over the global allocator, the catalogued absl::flat_hash_map, boost::unordered_flat_map and ankerl::unordered_dense entries show larger measured margins (4.8-6.0x build+destroy on u64 keys) from benchmarks broader than a 3,000-key word index.

## Integration

| | |
|---|---|
| **Form** | static lib (the U++ Core package, normally built by TheIDE or umk; it is not header-only) |
| **Dependencies** | U++ Core itself; zlib (bundled plugin/z on Windows, system zlib elsewhere) and pthread, dl and rt on Linux per Core.upp |
| **Minimum toolchain** | C++17 (Core's Topt.h uses if constexpr and inline constexpr variables); TheIDE supports GCC, Clang, MinGW and Visual C++ |
| **Platforms** | Windows, macOS, GNU/Linux and FreeBSD at production level (README); config.h also recognizes other BSDs, Solaris and Android; x86 and ARM, little-endian only |
| **Thread safety** | Not documented for the containers and Index.hpp has no locking, so concurrent writers need external synchronization; the U++ heap is thread-aware (per-heap caches, buffered remote frees, a StaticMutex for shared state). |
| **Drop-in for the baseline** | partial: Index offers begin()/end() for range-for, but the core API (GetAdd, FindAdd, Find returning an int position, positional access), duplicate-accepting Add, lazy Unlink removal, relocation requirements and reference invalidation all differ from std::unordered_map, and the speedup assumes U++ String keys and usually the U++ heap. |

## Gotchas

- AMap::Get(k) is value[Find(k)] with no check, so a missing key indexes value[-1] and only a debug ASSERT catches it; use Find, FindPtr or Get(k, default). Add does not look for an existing key (Index is multi-key), so use GetAdd, FindAdd or Put when keys must be unique.
- Removal is lazy: Unlink is O(1) but the slot stays in the key and value arrays until Put reuses it or Sweep() compacts, so positional loops over 0..GetCount() see unlinked entries unless they test IsUnlinked. FindAdd compares keys along the bucket chain without first comparing the stored hash, which is cheap for short Strings but costs a full equality call per chain entry for expensive key types.
- Linking Core without USEMALLOC (or outside a shared-library SO build) replaces the global operator new/delete with the U++ heap; allocation failure calls Panic('Out of memory!') instead of throwing std::bad_alloc, and the heap's static_asserts on block-header sizes fail on 32-bit PowerPC Darwin (issue #278, open).
- Harness flaws in benchmarks/idmapBench/main.cpp (read this session): the U++ path uses inline ASCII IsAlpha/IsAlNum/IsDigit and the buffered FileIn::Get while the STL path uses locale-aware &lt;cctype&gt; isalpha/isalnum/isdigit and per-character std::ifstream::get, so the ratio is not a container comparison (the 2007 page used isalpha on both sides); and info.txt prints TimeStop::Elapsed() as 'ms' although it returns microseconds (usecs() - starttime), so 1365093 means 1.37 s for 1000 passes. The default input alice30.txt (148,545 ASCII bytes, 27,342 words, 2,960 distinct, longest 14 characters, counted this session) keeps every key inside String's 14-byte inline buffer and the map at about 3,000 entries.

## Known shortcomings

- Downgraded A to C: the 2007 vsstd page (U++ Core 4.5x to 5.1x vs std::map and tr1::unordered_map, GCC 4.1.3 -O3) names only 'Core 2 Duo 2.7 GHz', leaves input files unnamed and the allocator setup unstated, and mixes container, stream and allocator effects; the repo's own 2020 rerun (benchmarks/idmapBench/info.txt, Clang x64) shows only about 2.4x with the U++ heap and 1.8x with malloc. Filed under hash-maps-sets.
- Enricher: the current benchmarks/idmapBench/main.cpp gives the U++ side inline ASCII IsAlpha/IsAlNum/IsDigit plus buffered FileIn::Get while the STL side gets locale cctype isalpha/isalnum plus per-char std::ifstream::get, so the 2020 ratio (about 2.4x with the U++ heap, 1.8x with malloc) is not container-only; info.txt labels TimeStop::Elapsed() as ms but it returns microseconds (1365093 = 1.37 s per 1000 passes); the input alice30.txt (148,545 ASCII bytes, 27,342 words, 2,960 distinct, longest 14 chars) fits U++ String's 14-byte inline buffer entirely, a best case on a tiny map; the 2020 baseline was likely libc++ (llvm-mingw), the 2007 std::string pre-GCC-5 COW; SortedVectorMap 1.11x slower than std::map in the same run. AMap::Get on a missing key indexes value[-1] (debug ASSERT only); Add allows duplicate keys; references invalidated on Add; the U++ heap replaces global new/delete and calls Panic on OOM, no bad_alloc; issue #278 open (PowerPC Darwin).
- Domain set to stdlib-replacements to match its hash-maps-sets category.

## Caveats and trade-offs

Benchmark is first-party and 2007-vintage (GCC 4.1.3, tr1::unordered_map, Core 2 Duo), and the repo's own 2020 rerun of the updated benchmark (benchmarks/idmapBench/info.txt, Clang x64 on Windows, std::unordered_map) shows the gap shrinking to about 2.4x on the U++ heap and about 1.8x with malloc for both, so the 4.5-5.1x headline is outdated. The measured ratio mixes four effects (container, String vs std::string, U++ FileIn::Get vs per-character std::ifstream::get, and the allocator), so it is not a container-only result; the page itself says the main reason for not using the standard library is not performance. Input files of the 2007 run are not identified (the default input is the benchmark's own main.cpp; the 58 KB file is unnamed), the CPU has no model number, and the allocator switch is not described, so the 2007 run cannot be reproduced exactly. Page only reports GCC rows although the code has an MSVC branch. The rendered ultimatepp.org page was not opened; the repo copy of the topic file was. Category is a judgement call: the benchmark is a word-index container test and fits hash-maps-sets (or allocators) better than filesystems-and-io. [retier] Input alice30.txt: 2,960 distinct words, all within U++ String's 14-byte inline buffer; 2020 baseline likely libc++ via llvm-mingw; 2007 std::string pre-GCC-5 COW; AMap::Get on a missing key indexes value[-1]; Add allows duplicates; U++ heap replaces global new/delete and Panics on OOM.

U++ is a whole framework (its own String, Vector/VectorMap containers with move-only assignment semantics, streams, global operator new/delete overload via the U++ heap, and an IDE/build system, TheIDE), not a drop-in replacement for std containers; adopting the speedup means adopting U++ Core types and its allocator.

## Maintenance

Actively maintained (last commit 2026-10-07, 16,464 commits, BSD-2-Clause, 994 stars) and usable today, but only as part of U++ Core with its heap and build system, and the only evidence is a first-party benchmark whose current harness gives the U++ side a buffered reader and inline ASCII classifiers while the STL side uses per-character std::ifstream::get and &lt;cctype&gt;, and labels microsecond timings as ms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party page (uppbox/uppweb/www.tpp/vsstd_en-us.tpp) carries the full benchmark code, GCC 4.1.3 and -O3, but the CPU is given only as 'Core 2 Duo, 2.7 Ghz' with no model number, the two input files (a 3.93 KB and a 58 KB .cpp file) are not identified, and how the standard-allocator runs were configured is not stated, so it is not reproducible enough for A; the in-repo rerun (benchmarks/idmapBench/info.txt, 2020) states neither hardware nor flags.
- **Verifier notes:** Numbers on the page match the record exactly, but tier A is not supported: CPU without model number, unnamed input files, unstated allocator configuration; downgraded to C. The repo's newer run (benchmarks/idmapBench/info.txt) shows only about 1.8-2.4x on Clang x64, which the orchestrator may want as the headline; category filesystems-and-io looks wrong (hash-maps-sets fits). Metadata confirmed: BSD-2-Clause, 994 stars, last commit 2026-10-07, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 11); enricher w11 pair-032; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/HEAD/uppbox/uppweb/www.tpp/vsstd_en-us.tpp>
  - <https://github.com/ultimatepp/ultimatepp>
  - <https://github.com/ultimatepp/ultimatepp/commits>
  - <https://github.com/ultimatepp/ultimatepp/tree/master/benchmarks>
  - <https://github.com/ultimatepp/ultimatepp/tree/master/benchmarks/idmapBench>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/idmapBench/main.cpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/idmapBench/info.txt>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/idmapBench/idmapBench.upp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppbox/uppweb/www.tpp/vsstd_en-us.tpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/idmapBench/main.cpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/idmapBench/info.txt>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/idmapBench/idmapBench.upp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/idmapBench/alice30.txt>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/README.md>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Index.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Index.hpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Index.cpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Map.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Map.hpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Vcont.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Topt.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/String.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Util.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/TimeDate.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Ops.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Hash.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/CharSet.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Stream.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Defs.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/config.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/Core.upp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/HeapImp.h>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/heap.cpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/heaputil.cpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/srcdoc.tpp/Moveable_en-us.tpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/srcdoc.tpp/NTL_en-us.tpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/uppsrc/Core/src.tpp/Index_en-us.tpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/IndexStd/IndexStd.cpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/AllMaps/AllMaps.cpp>
  - <https://raw.githubusercontent.com/ultimatepp/ultimatepp/master/benchmarks/HashBench/HashBench.cpp>
  - <https://github.com/ultimatepp/ultimatepp>
  - <https://github.com/ultimatepp/ultimatepp/commits/master>
  - <https://github.com/ultimatepp/ultimatepp/commits/master/benchmarks/idmapBench/main.cpp>
  - <https://github.com/ultimatepp/ultimatepp/commit/d273b3d.diff>
  - <https://github.com/ultimatepp/ultimatepp/tree/master/benchmarks>
  - <https://github.com/ultimatepp/ultimatepp/issues?q=is%3Aissue+VectorMap+OR+Index+OR+heap>
  - <https://github.com/ultimatepp/ultimatepp/issues/278>
  - <https://raw.githubusercontent.com/mstorsjo/llvm-mingw/master/README.md>
  - <https://raw.githubusercontent.com/mstorsjo/llvm-mingw/master/build-libcxx.sh>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/ultimatepp/ultimatepp`) · [data/wave11/enrich/raw/github_com_ultimatepp_ultimatepp.json](../../../data/wave11/enrich/raw/github_com_ultimatepp_ultimatepp.json) (enrichment confidence 0.75)

</details>
