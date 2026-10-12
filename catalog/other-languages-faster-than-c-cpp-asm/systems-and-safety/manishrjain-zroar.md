# zroar (Zig serialized Roaring bitmaps)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `Apache-2.0` · 🟢 active

> Zig 64-bit Roaring bitmap whose in-memory buffer is its serialized form; 2.2x faster than CRoaring roaring64 on warm operations.

| | |
|---|---|
| **Beats** | CRoaring 5.0.0 (roaring64 API, portable and frozen serialization) |
| **Claimed result** | README and BENCHMARKS.md (generated 2026-08-20; CRoaring time / zroar time, geometric means): realdata with bitmaps in memory 2.20x (36 cells, zroar faster in 31; SuccessiveUnion64 0.90-1.04x and ToArray64 0.86-1.25x near parity, IterateAll64 6.50-19.11x and ComputeCardinality64 12.21-13.41x); cold open 6.92x vs portable and 3.44x vs frozen (40 cells); synthetic operations 2.18x (132 cells); Serialize plus Deserialize 615x vs portable and 259x vs frozen (56 cells; zroar's deserialize is a pointer cast); all synthetic families 8.92x. Faster in 339 of 360 cells counting the portable and frozen columns separately. By total time per data set 1.46-6.81x warm and 1.84-5.69x cold (BENCHMARKS.md; README rounds to 1.5x-6.8x and 1.8x-5.7x). README: cardinality 4.8x geomean, up to about 290x on cold opens. Losses: InsertRemoveRandom 0.60x typical (0.33-0.40x on the key-index masks, CRoaring about 3x faster) and synthetic Insert by total time 0.89x (CRoaring faster), although its typical row is 2.21x. |
| **Workload** | CRoaring's benchmark suite ported to Zig plus warm-open and cold-open variants and a zipfian OLTP synthetic dataset: contains, insert, remove, random access, set operations, cardinality, serialize and deserialize; 360 benchmark cases. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5950X, performance governor, boost on with frequency range fixed at 4.00-4.00 GHz, SMT on, benchmark process pinned to CPU 6 (BENCHMARKS.md) |
| **Compiler and flags** | Zig 0.16.0; bench/run_all.sh runs zig build bench-exe, which defaults the bench to ReleaseFast, with the default native target. CRoaring 5.0.0 (tag v5.0.0 pinned by bench/fetch_croaring.sh) is compiled inside the same zig build through addCSourceFiles: Zig passes -O2 -DNDEBUG (not -O3) to C sources in ReleaseFast (checked in Zig 0.15.1 src/Compilation.zig; the 0.16.0 tag is not on the GitHub mirror), plus -DCROARING_COMPILER_SUPPORTS_AVX512=0 from build.zig's croaringFlags on CPUs without AVX-512 such as the 5950X. CRoaring's own CMake Release build would use -O3. Both sides allocate through libc malloc (std.heap.c_allocator in bench/bench.zig). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | README 'Why Is It Faster': one contiguous buffer used in place with few dependent loads, versus CRoaring reaching a container through a chain of dependent loads and an adaptive radix tree index for the high 48 bits. |
| **Adoption** | 17 stars |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/manishrjain/zroar) · [benchmark](https://raw.githubusercontent.com/manishrjain/zroar/HEAD/README.md) |

## Verdict

The author ported CRoaring 5.0.0's own bench.cpp and synthetic_bench.cpp roaring64 rows to Zig 0.16.0 (ReleaseFast, with CRoaring compiled in the same build at -O2) and ran them on a Ryzen 9 5950X fixed at 4.00 GHz and pinned to one core. Geometric means of CRoaring time over zroar time: 2.20x on warm real data (zroar ahead in 31 of 36 cells), 6.92x and 3.44x on cold opens against the portable and frozen formats, 2.18x on synthetic operations, and 615x and 259x on serialize plus deserialize. CRoaring wins random interleaved insert/remove (0.60x typical, 0.39x by total time) and synthetic Insert by total time (0.89x).

## Use it when

- Posting lists or secondary indexes stored as bytes (on disk, in a KV store, over the network) and opened per query: opening is a pointer cast, and the cold-open rows average 6.92x against CRoaring portable and 3.44x against frozen.
- Read-heavy 64-bit set work in Zig: contains, iteration, cardinality and pairwise intersection or cardinality on real data sets (2.20x geometric mean warm; ComputeCardinality64 12.2-13.4x).
- Append-mostly maintenance with increasing row ids, or batched writes sorted first: MixedOLTP (90% contains, 10% append) is 1.94-4.65x against portable, and the README reports sorted inserts 1.3-4x faster.
- Ordered probe streams (merges, range checks, ordered id scans), which the thread-local neighbour hint turns into constant-time key lookups.

## Skip it when

- Random interleaved inserts and removes across many keys: CRoaring is about 2.5-3x faster (0.33-0.40x on the key-index masks, 0.39x by total time), because a growing container in the middle of the buffer has to move.
- Run-heavy data: zroar has no run containers, and the data sets built to show them off were left out of the benchmark. Even on the included sets, CRoaring's portable encoding is 0.85-0.96x the size of compacted zroar, and its frozen encoding 0.95-0.97x.
- When you need 32-bit values, CRoaring portable-format interop, or use from C, C++ or any language other than Zig: none of these exist.
- On untrusted buffers: beyond the version and size checks, buffer contents are validated only by debug assertions, so a corrupt buffer in ReleaseFast can read out of bounds. Checksum the bytes in the layer above.
- When you need a stable dependency: the library is pre-1.0 with calendar versioning (API changes between release series), one author, 27 commits since 2026-08-10, and big-endian targets are rejected at compile time.

## How it is fast

It uses offsets instead of pointers. A lookup is a search over the contiguous sorted key pairs plus an add into the same buffer, where CRoaring walks an adaptive radix tree (ART) and three more pointer hops to separately malloc'd containers, five to six dependent loads. Containers sit next to each other, so scans walk memory forward for the hardware prefetcher; container headers cache cardinality; and set operations, container searches and array extraction use portable @Vector SIMD. A thread-local hint remembers the last key index, so ascending lookups cost two compares (1.4 ns against 21 ns for a bisection on a million-key node, per keys.zig). Because the buffer is also the serialized form, opening a bitmap costs nanoseconds.

## Compared with alternatives

No catalogued sibling in systems-and-safety is a compressed bitmap or posting-list structure, so the real choice is against the baseline, CRoaring roaring64. Pick zroar in Zig code that stores bitmaps as bytes and reads far more than it writes at random. Keep CRoaring for cross-language format interop, 32-bit sets, run-heavy data and random-write workloads.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none for the library (Zig std only); the benchmark and difftest need a CRoaring checkout (bench/fetch_croaring.sh pins v5.0.0) and libc |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon) |
| **Platforms** | little-endian targets only (x86-64, ARM64, RISC-V and WASM per DESIGN.md; big-endian is a compile error); SIMD through portable @Vector, with no intrinsics and no runtime CPU dispatch |
| **Thread safety** | Not documented as a guarantee. Read methods take \*const Bitmap, and the lookup hint is thread-local and re-checked before use. Mutation (including the copy-out of a borrowed buffer) changes the bitmap, so writers need external synchronisation. |
| **Drop-in for the baseline** | partial — it replaces CRoaring's roaring64_bitmap_t for 64-bit array and bitmap workloads in Zig, but the API differs, there are no C bindings, no run containers, no 32-bit variant and no CRoaring serialized-format compatibility |

## Gotchas

- Harness deviation in IterateAll64 (6.50-19.11x) and ColdIterateAll64 (6.80-17.55x): CRoaring 5.0.0's bench.cpp loop makes two library calls per value (roaring64_iterator_has_value and roaring64_iterator_advance). The Zig port loops on hasValue() and then calls the wrapper's next(), which calls has_value, value and advance again: four calls into C per value that cannot be inlined, so CRoaring does double the per-value calls of its own benchmark. ToArray64 likewise adds a roaring64_bitmap_get_cardinality call per bitmap that CRoaring's body does not make, while zroar's side allocates per bitmap. These rows overstate zroar's margin by an unmeasured amount; the docs' claim that the bodies are 'copied line for line' does not hold for these rows.
- The ContainsHit and ContainsMiss rows (2.95-3.01x geometric mean) probe keys in ascending order, faithfully ported from CRoaring's synthetic_bench.cpp. That is exactly the pattern zroar's thread-local neighbour hint short-circuits, while the plain roaring64_bitmap_contains has none (zroar's own comment points to CRoaring's caller-held bulk context as the equivalent, which is not used here). With random probes (ContainsRandom) the result is 0.92-1.85x.
- 'Cold' means re-opened from in-memory bytes inside the timed loop, which runs one warm-up call and then 500 ms of calls; the bytes stay in cache, so it is not cache-cold or disk I/O. The Deserialize and cold rows set zroar's pointer cast plus version check against CRoaring's bounds-checked portable_deserialize_safe and frozen_view, so the 615x, 259x and up to 286x figures measure skipped parsing and validation.
- On the build side, Zig compiles CRoaring at -O2 rather than its CMake -O3, with no cross-language inlining, and CRoaring's realdata bitmaps are run_optimize'd as in CRoaring's bench.h, so its cardinality and iteration paths cross run containers that zroar does not have. BENCHMARKS.md was generated on 2026-08-20, before the 'Optimize Iteration' commit (2026-08-21) and the compact change in v0.2608.1 (2026-08-25).

## Known shortcomings

- Zig ReleaseFast compiles the CRoaring C sources at -O2 (Zig 0.15.1 Compilation.zig) rather than CMake's -O3; roaring64 only; run-container sets excluded; the cold/deserialize rows pit an unchecked pointer cast against portable_deserialize_safe; CRoaring is about 3x faster on random insert/remove and the synthetic Insert total is 0.89x; library design, not language.
- Harness flaw: the IterateAll64 port makes 4 C calls per value against CRoaring bench.cpp's 2 (the wrapper's next() repeats has_value and adds value) and ToArray64 adds a get_cardinality call, inflating the 6.50-19.11x by an unmeasured amount. The Contains rows probe in ascending order, which zroar's thread-local hint short-circuits; random probes give 0.92-1.85x. 'Cold' means bytes hot in cache.

## Caveats and trade-offs

Author benchmark of the author's own library on one host. CRoaring is compiled by Zig's C toolchain at -O2 instead of its CMake -O3 Release build (same_opt_level false; not a debug build). Only CRoaring's 64-bit roaring64 (ART index) is compared. zroar has no run containers and the data sets designed to showcase them were excluded. Cold-open and Deserialize rows set zroar's pointer cast plus version check (buffers are trusted input with no integrity check) against CRoaring's bounds-checked roaring64_bitmap_portable_deserialize_safe or frozen_view, so the 615x and 8.92x figures reflect that design difference. Most of the gain comes from the data layout (one flat buffer with offsets instead of an ART plus per-container heap allocations), not from Zig codegen. CRoaring wins random interleaved insert/remove by about 3x and synthetic Insert by total time. 27 commits, created August 2026, 17 stars; the 'Optimize Iteration' commit (2026-08-21) postdates the BENCHMARKS.md run. [retier] The IterateAll64 port makes 4 C calls per value against CRoaring bench.cpp's 2 (the wrapper's next() repeats has_value and adds value) and ToArray64 adds a get_cardinality call, inflating the 6.50-19.11x by an unmeasured amount. The Contains rows probe in ascending order, which zroar's thread-local hint short-circuits; random probes give 0.92-1.85x. 'Cold' means bytes hot in cache.

64-bit integers only; no run container; does not read or write CRoaring's portable serialization format; random interleaved insert/remove is about 3x slower than CRoaring; pre-1.0 with calendar versioning and a format-version check.

## Maintenance

Active (created 2026-08-10; 27 commits, last 2026-08-25 at v0.2608.1). Apache-2.0 and small (about 2,000 lines of library code), with CI that runs the unit and property tests in Debug, ReleaseSafe and ReleaseFast plus a five-minute differential soak against CRoaring. Copyable as a Zig module, but pre-1.0, single-author and 17 stars.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** Public benchmark code (bench/bench.zig, a line-for-line port of CRoaring's bench.cpp and synthetic_bench.cpp roaring64 rows, run by bench/run_all.sh; CRoaring v5.0.0 pinned in bench/fetch_croaring.sh), compiler (Zig 0.16.0), flags (ReleaseFast for zroar; CRoaring's C flags fixed by the public build.zig) and CPU (Ryzen 9 5950X at a fixed 4.00 GHz, pinned) are all stated. The CRoaring side is built at Zig's -O2 for C rather than CRoaring's CMake -O3, a release level and not a crippled build, so the tier stays A with the mismatch documented.
- **Retiered** A to C: Enricher: the ported CRoaring iteration harness makes 4 C calls per value against bench.cpp's 2 and ToArray64 adds a cardinality call, inflating the largest wins by an unmeasured amount, and the Contains rows probe in ascending order where zroar's thread-local hint short-circuits (random probes 0.92-1.85x). Asymmetric-harness precedent: A to C.
- **Verifier notes:** Numbers in the record match README and BENCHMARKS.md. Correct same_opt_level to false: Zig ReleaseFast builds CRoaring's C at -O2 while zroar's Zig code gets -O3-equivalent optimisation; not crippled, so no tier cap. Shortcomings to record: first-party single host, roaring64 only, run-container data sets excluded, cold-open and deserialize rows compare an unchecked pointer cast with a validating parse, CRoaring faster on random interleaved insert/remove and synthetic Insert total time.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-73 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/README.md>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/build.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/fetch_croaring.sh>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/run_all.sh>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/bench.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/roaring64.zig>
  - <https://github.com/manishrjain/zroar>
  - <https://github.com/manishrjain/zroar/commits/main>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.1/src/Compilation.zig>
- **Sources the enricher read:**
  - <https://github.com/manishrjain/zroar>
  - <https://github.com/manishrjain/zroar/commits/main>
  - <https://github.com/manishrjain/zroar/tree/main/src>
  - <https://github.com/manishrjain/zroar/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/README.md>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/DESIGN.md>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/build.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/fetch_croaring.sh>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/run_all.sh>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/bench.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/roaring64.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/bench/datasets.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/src/zroar.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/src/keys.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/src/iterator.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/src/container.zig>
  - <https://raw.githubusercontent.com/manishrjain/zroar/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/RoaringBitmap/CRoaring/v5.0.0/microbenchmarks/bench.cpp>
  - <https://raw.githubusercontent.com/RoaringBitmap/CRoaring/v5.0.0/microbenchmarks/synthetic_bench.cpp>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/manishrjain/zroar`) · [data/wave14/enrich/raw/github_com_manishrjain_zroar.json](../../../data/wave14/enrich/raw/github_com_manishrjain_zroar.json) (enrichment confidence 0.8)

</details>
