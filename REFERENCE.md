# Reference

No license, unclear/non-OSI license, mixed licensing, or paper-only. Study the idea and reimplement clean-room; do not copy the code.

## Verified

### ordered-maps-trees

#### S+ tree (Algorithmica static B-tree array layout)  `C++`  `no license`  `abandoned`  `Tier A`

SIMD (AVX2) static B+-tree array layout beating std::lower_bound/std::set on batched int32 lookups.

**Beats:** std::lower_bound (primary), std::set (bench code binsearch/set.cc actually uses std::multiset), absl::btree — Reciprocal-throughput microbenchmarks on an AMD Zen 2 CPU with Clang 10 (-O3 -march=native) show the S+ tree up to ~15x faster than std::lower_bound on cache-resident sorted int32 arrays (~8x for arrays >1e6, up to 2^25 elements), up to ~30x faster than std::multiset::lower_bound, and (pointer variant) ~15x faster than Abseil's absl::btree on large arrays; the author explicitly notes real single-query latency gains are much smaller than these throughput figures.

**How:** The sorted array is rearranged into a B-ary tree (16 keys per node/cache line, branching factor 17) stored as one flat array with compile-time layer offsets instead of pointers (the 'S+ tree' = separate internal/leaf layers, vs. the pointer/Eytzinger-numbered 'S-tree'). Each node comparison loads 16 keys into two AVX2 256-bit registers, does _mm256_cmpgt_epi32 SIMD compares, permutes/packs the masks, and extracts the branch index with tzcnt, replacing several scalar branchy comparisons per level with one branchless SIMD step; large trees also use aligned_alloc + madvise(MADV_HUGEPAGE) to cut TLB misses. The headline numbers are reciprocal-throughput over batches of independent queries, which lets the CPU overlap several independent tree descents (~3x ILP per the article) rather than shrinking single-query latency much.

**Use it when:**
- Read-mostly/static sorted 32-bit-integer key sets that are bulk-built once (or rarely rebuilt), not mutated incrementally
- Workloads that issue many independent lookups that can be batched/pipelined (joins, index probes, columnar scans) so the reciprocal-throughput gains actually materialize
- x86-64 targets with AVX2 where you can build with -march=native and enable transparent huge pages for large (>1e6-element) arrays
- Arrays that fit or mostly fit in cache, where the article's ~15x-over-std::lower_bound number applies (~8x still holds up to 2^25 elements)
- You're willing to vendor and adapt a single .cc file into your own build rather than link a maintained library

**Skip it when:**
- You need insert/delete or any online mutation of the key set -- no dynamic update path is implemented, only a full prepare() rebuild
- Latency-sensitive single-query paths with data-dependent lookups (pointer chasing between queries) -- the author states real per-query latency gains are much smaller than the throughput numbers
- Non-x86 or AVX2-unavailable targets -- the article says porting to AVX-512 or Arm NEON needs 'non-trivial changes', and none is provided in this repo
- You need arbitrary key/value types, comparators, or a runtime-chosen array size -- N is a compile-time constant baked into the offset/height calculations
- Anything beyond experimentation/benchmarking in production -- no LICENSE file, abandoned since 2022, and the author frames this as teaching/reference code

**Vs siblings:** Pick this over tlx::btree or boost::container::flat_set/fast-containers when your key set is effectively static (bulk-loaded, then read-heavy) and lookups can be batched for throughput; those siblings are actual libraries supporting online insert/erase/find, whereas amh-code is an unpackaged technique reference you'd have to adapt, re-tune, and maintain yourself.

**Gotchas:**
- Array size N is a preprocessor/constexpr constant (binsearch.hh defaults to 1<<20), so each key-set size effectively needs its own compiled variant rather than being a runtime parameter
- Requires AVX2 codegen (-march=native or explicit target attributes); there is no scalar fallback path in these files
- Large-array speedups depend on aligned_alloc + madvise(MADV_HUGEPAGE) actually getting huge pages from the OS; without that configured, expect smaller gains than reported
- Headline speedups are reciprocal-throughput over batches of independent queries -- single dependent-query ('real') latency shows a much smaller win, per the author's own caveat in the article

**Status:** Abandoned reference code (last commit 2022-10-06, no LICENSE file) published as teaching/benchmark material for the Algorithmica HPC book, not a maintained library -- treat it as a technique to study and port, not a dependency to pull in.

[repo](https://github.com/sslotin/amh-code) · [benchmark](https://en.algorithmica.org/hpc/data-structures/s-tree/)

## Unverified claims (tier C/D)

### number-parsing-formatting

#### fast_io  `C++`  `Anti-Tivo License (ATL) v1.0 (custom, non-OSI-approved)`  `active`  `Tier C`

Header-only C++20 I/O library replacing iostream/cstdio and std::to_chars with buffered, syscall-near I/O.

**Beats:** iostreams (std::fstream); std::to_chars (MSVC, for double formatting) — Author-run benchmarks (no CPU model or optimization flags stated) show fast_io's buffered file I/O beating std::fstream by roughly 6-15x for writing/reading 10 million integers on GCC 11 (Linux and MinGW-W64) and MSVC 19.26, and beating MSVC's std::to_chars(charconv) by about 23% (~1.29x throughput) for round-trip formatting of 10 million doubles, also on MSVC 19.26.

**How:** Devices are abstracted through C++20 concepts (static polymorphism), avoiding the vtable dispatch, locale machinery, and sentry-object overhead that <iostream>/streambuf carry on every call. I/O goes through the library's own buffered file objects close to the raw syscall/native-handle level rather than through libc FILE* layering. Integer formatting uses the jeaiii digit-pair method (include/fast_io_core_impl/integers/jeaiii_method.h, the same technique as the jeaiii/itoa sibling entry). Double round-trip formatting is implemented in include/fast_io_unit/floating/roundtrip.h, whose header comment attributes the algorithm to 'Dragonbox' (Jk Jeon) even though the readme's benchmark section calls it the 'Ryu algorithm' — these are different, related fast float-to-string algorithms.

**Use it when:**
- Bulk sequential file I/O (writing/reading millions of integers or lines) where std::fstream or stdio throughput is the bottleneck.
- Already on C++20 with a concepts-capable compiler (GCC>=14, Clang>=17, or MSVC per current support.md) and able to adopt a non-drop-in API.
- Low-level, embedded, kernel-driver, or freestanding/WASM targets that need direct handle/syscall-level I/O and small binaries (readme's static-link comparison: 155KB fast_io vs 925KB fstream).
- Need Unicode-aware (UTF-8/16/32) transcoding I/O in the same layer as raw throughput.
- Can accept the Anti-Tivo License's non-standard terms in exchange for the speed.

**Skip it when:**
- Need a true drop-in replacement for std::iostream or std::to_chars without touching call sites — fast_io's API shape and exceptions-only error model differ substantially.
- Legal review requires an OSI-approved permissive or conventional copyleft license — Anti-Tivo License v1.0 is custom and not OSI-approved.
- Toolchain can't reach the current minimum (GCC>=14/Clang>=17 per support.md), which is notably newer than the GCC 11/MSVC 19.26 used in the readme's own benchmark numbers.
- Need independently reproduced numbers before adopting — all published results are the author's own, with no CPU model or optimization flags stated, and the readme's cited benchmark paths no longer exist in the reorganized benchmark/ directory.
- Multithreaded writers by default — the fast unbuffered types are not thread-safe; the thread-safe *_mutex variants give up much of the speed edge (readme: 0.049s to 0.146s output time on MinGW for the mutex variant).

**Vs siblings:** Pick fast_io over Boost.Charconv, c4core, fast_double_parser, rigtorp/CharConv, or jeaiii/itoa when the goal is whole-file/stream I/O throughput via buffered file objects and syscall-near handles, not just isolated number<->string conversion — those siblings only replace to_chars/from_chars/stoi/strtod, while fast_io replaces the entire iostream/cstdio layer (and internally reuses jeaiii's itoa method for its own integer formatting).

**Gotchas:**
- readme's cited benchmark source paths (benchmarks/0000.10m_size_t/unit, benchmarks/0001.10m_double/charconv) do not exist in the current repo; benchmark/ has been reorganized into numbered dirs (e.g. 0002.file_io_tsc, 0004.file_io_floating).
- readme calls the double round-trip formatting the 'Ryu algorithm', but the implementation header (include/fast_io_unit/floating/roundtrip.h) is commented 'Algorithm: Dragonbox, Author: Jk Jeon' — a different, related algorithm.
- MinGW benchmark numbers required the author to patch libstdc++'s BUFSIZ from 512 bytes to 1MB before comparing against fstream; the out-of-the-box gap on stock MinGW would be smaller.
- License is the custom Anti-Tivo License v1.0 (non-OSI-approved, GitHub reports it as NOASSERTION) — review it before shipping, it is not a standard permissive or copyleft license.

**Status:** Actively maintained (last commit 2026-07-02 on the 'next' branch, 2026-03-13 on master); usability is capped at 'reference' because of the non-OSI Anti-Tivo License, not because of code immaturity — 851 stars and an extensive examples/benchmark/fuzzing tree.

[repo](https://github.com/cppfastio/fast_io) · [benchmark](https://github.com/cppfastio/fast_io/blob/master/readme.md)
