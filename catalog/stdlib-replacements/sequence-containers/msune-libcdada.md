# libcdada

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Pure C API (list, set, map, queue, stack, string, bitmap) wrapping libstdc++ containers; matches libstdc++ at best, never beats it.

| | |
|---|---|
| **Beats** | libstdc++ std::set, std::map and std::list (native C++ code on the same libstdc++) |
| **Claimed result** | No speedup claimed. README: 'Reasonable performance - comparable to libstdc++'. Table (average ticks per op, std vs cdada): uint32 set insert 752 vs 746, erase 698 vs 743; uint32 map insert 830 vs 809, erase 722 vs 1009; uint32 list push_back 20 vs 28, pop_back 17 vs 20; 69-byte set insert 1410 vs 1623 (custom container 1433); 69-byte list push_back 42 vs 67 (custom 44), pop_back 22 vs 40 (custom 25); 444-byte custom containers within about 4 percent except map erase 1472 vs 2021. |
| **Workload** | test/benchmark.cc: 500,000 uint32_t keys from test/array.s3 (also wrapped in 69-byte and 444-byte structs) inserted then erased in set and map, and push_back then pop_back in list (and stack), each pass repeated 10 times; RDTSC ticks summed and divided by 500,000 x 10, so the table is average ticks per operation. The std::set/std::map baseline does find() then a hinted insert/erase to mimic cdada's E_EXISTS/E_NOT_FOUND semantics. Thread runs under SCHED_FIFO max priority. Measures libcdada's wrapper overhead over libstdc++. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8565U 1.80GHz/4.6GHz, 16GB DDR4 2667 MHz, cpufreq governor set to performance |
| **Compiler and flags** | -O3 (libcdada configured with ../configure, per doc); compiler name and version not stated, only 'Standard Debian10 libstdc++ package'; benchmark source test/benchmark.cc |
| **Adoption** | 30 stars |
| **Last commit** | 2026-03-01 |
| **Links** | [repository](https://github.com/msune/libcdada) · [benchmark](https://github.com/msune/libcdada/blob/master/doc/Benchmarks.md) |

## Verdict

doc/Benchmarks.md times 500,000 unique shuffled uint32 keys (also inside 69- and 444-byte packed structs), inserted then erased, 10 repetitions, averaged RDTSC ticks per op at -O3 against libstdc++ from Debian 10 on an Intel Core i7-8565U (compiler version unstated, one run, no variance). libcdada ties native on uint32 set/map insert (746 vs 752, 809 vs 830) and on custom containers for large structs, and is slower on map erase (about 1.4x), list push_back (28 vs 20) and padded 69-byte lists (67 vs 42, 40 vs 22); there is no speedup.

## Use it when

- C code bases (network daemons such as pmacct, which builds libcdada in-tree per issue #7) that want tested ordered set/map/list containers without writing a red-black tree
- Fixed-size POD keys whose size is 1, 2, 4 or 8 bytes, where the default containers run close to native libstdc++ (uint32 set insert 746 vs 752 ticks)
- Larger or odd-sized structs (for example 69 or 444 bytes) if you add a custom-container C++ file, which keeps set rows within 2 percent of native and list rows within 3 ticks (69-byte list pop_back 25 vs 22)
- Single-threaded, Linux/POSIX user-space code that already links libstdc++

## Skip it when

- You want something faster than the STL: it is the STL plus a call, a switch and a key copy; plf::list or ankerl::svector are the entries that actually beat std containers
- Erase-heavy map workloads: cdada_map_erase does find() and then erase(key), a second tree lookup, so map erase runs 1.37-1.54x slower than native (1009 vs 722 ticks uint32, 1768 vs 1148 for 69-byte keys, 2021 vs 1472 for 444-byte custom)
- You need a hash table: despite the README's 'hashmap' wording, cdada_map is std::map (O(log n), ordered); wrapping std::unordered_map is still an open feature request (#13)
- Concurrent access (README: not thread-safe), keys over 256 bytes without custom containers, or variable-length string keys (open request #12)
- Non-x86 or non-glibc toolchains with -Werror: configure forces -Werror, and an OpenWrt ARM g++ build fails on a memcpy overflow warning in __list_internal.h (open issue #14)

## How it is fast

It adds no new algorithm: every call dispatches through a switch on key size to a pre-instantiated std::set/std::map/std::list of uint8/16/32/64_t or a padded 16-256 byte POD (compared with memcmp). Default containers round keys up to the next power of two (memset plus memcpy into a padded temporary on every call); 'custom containers' (CDADA_\*_CUSTOM_GEN macros or the cdada-gen script) instantiate the libstdc++ container for your exact struct type in a small C++ file, removing the padding cost.

## Compared with alternatives

Pick libcdada only when the caller must be C: every sibling in this category (plf::list, plf::colony, plf::stack, ankerl::svector, veque, fast_vector, EASTL vector) is a C++ template that actually beats the std container, while libcdada at best ties libstdc++. From C++ code, use std containers or those siblings directly.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | libstdc++ (C++98); autotools (autoconf, automake, libtool) to build; python3 only for the cdada-gen custom-container generator |
| **Minimum toolchain** | C (gnu89) plus any gcc-compatible C++98 compiler (gcc, clang, icc per README) |
| **Platforms** | POSIX (Linux tested; a FreeBSD build error inside pmacct was fixed in closed issue #7); Windows not supported; the benchmark's RDTSC timer is x86-only and prints zeros elsewhere |
| **Thread safety** | Not thread-safe (README); no internal locking |
| **Drop-in for the baseline** | partial — same libstdc++ containers underneath, but a C void\* API with E_EXISTS/E_NOT_FOUND return codes instead of templates and iterators; C++ code gains nothing by switching |

## Gotchas

- Harness and code finding: the std::set/std::map baseline in test/benchmark.cc is written to mirror cdada's own insert pattern (find(), then insert(it, k) with it == end()), which for the 500,000 shuffled keys in array.s3 is a wrong hint and triggers a second full tree descent; idiomatic set.insert(k) or lower_bound plus hinted insert does one descent, so the 'comparable to libstdc++' parity is against a baseline slowed to cdada's double-lookup pattern, and real overhead versus idiomatic C++ code is larger than the table shows.
- Map erase is the one row where the baseline does not mirror the library: the baseline erases by iterator, while cdada_map_erase_u (also used by custom maps) calls find() and then erase(\*key), a redundant second lookup; switching to erase(it) is a one-line fix that would likely remove the 1.4x map-erase gap.
- Default containers pad keys to a power of two and order them by memcmp of the padded bytes, so traversal order of struct keys is byte-wise little-endian rather than numeric, and non-power-of-two keys pay a memset plus memcpy per call (69-byte list pop_back 40 vs 22 ticks).
- Positional access is linear: cdada_list_get and cdada_set_get_pos walk the container with std::advance (O(n)), as std::list would.

## Known shortcomings

- Not faster: the benchmark is an overhead test of the C wrapper over libstdc++, level on uint32 set/map insert and slower on map erase (1.4x), list push_back (1.4x) and 69-byte list pop_back (1.8x); compiler version missing; list rows time push_back/pop_back, not insert/erase; ticks are per-op averages over 10 runs. Kept and documented. BSD-2-Clause, active.
- Enricher: cdada_map_erase_u (and custom maps) calls find() then erase(key), a second tree lookup that explains the 1.37-1.54x slower map erase (erase(it) is a one-line fix; set erase already uses erase(it) and is at parity). Harness flaw: the std::set/std::map baseline copies cdada's find() plus insert(end() hint) pattern, and on 500,000 shuffled unique keys that hint is wrong, so the baseline does two tree descents per insert; 'comparable to libstdc++' is against that slowed baseline and the overhead vs idiomatic insert() is larger. README calls the map a hashmap but it is std::map (unordered_map request #13 open); configure forces -Werror and the ARM OpenWrt build fails (#14); padded keys ordered by memcmp; not thread-safe; never faster than std.

## Caveats and trade-offs

Not a faster-than-std result: the doc is an overhead measurement of a C wrapper built on libstdc++ itself, and cdada is level with libstdc++ only on uint32 set/map inserts (within about 3 percent, in the noise) and on custom containers for large structs. It is slower on most other rows: uint32 map erase about 1.4x slower, list push_back about 1.4x slower, 69-byte list pop_back about 1.8x slower, 444-byte map erase about 1.37x slower (derived from page data). One 'random execution' of the binary, no variance given; compiler version missing; Debian 10 era libstdc++ only (no libc++ or MSVC STL). The 'list' rows time push_back/pop_back, not insert/erase. README calls map a hashmap, but it is backed by std::map. Not thread-safe. Kept for the C-callable container wrapper role. [retier] Overhead test of a C wrapper over libstdc++, never faster than std. The std baseline copies cdada's find() plus insert(end() hint) pattern, so on 500,000 shuffled keys it does two tree descents per insert (slowed baseline). Map erase 1.37-1.54x slower from a find()-then-erase(key) double lookup; list push_back 1.4x and pop_back 1.8x slower. Compiler version missing; 'hashmap' is std::map; -Werror configure; not thread-safe.

C API wrapper over libstdc++ containers, so it needs the C++ runtime; default containers support 1-256 byte keys padded to a power of two (custom containers for larger or unpadded keys); not thread-safe; POSIX build with autotools; values are copied by value through a void\* API.

## Maintenance

Maintained by a single author (v0.6.4 bug-fix release on 2026-02-27, last commit 2026-03-01, 30 stars, BSD-2-Clause) and small enough to vendor, but it is a convenience C wrapper, not a performance win, and four feature/bug issues (#12, #13, #14, #21) remain open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party doc/Benchmarks.md with public code (test/benchmark.cc), -O3 and CPU (i7-8565U) stated, but no compiler name or version (only 'Debian10 libstdc++ package'), so not A; numbers are first-party, so C. The numbers show parity or a slowdown, not a win.
- **Verifier notes:** All table numbers verified on doc/Benchmarks.md; benchmark.cc shows ticks are per-operation averages over 10 runs (the record's 'tick normalisation not stated' was wrong) and that list rows are push_back/pop_back. Metadata confirmed: BSD-2-Clause, 30 stars, not a fork, last commit 2026-03-01 (active). Shortcoming to record: not faster than libstdc++ (it wraps it), slower on erase and list rows; category sequence-containers fits only the list part (set/map are associative).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/msune/libcdada>
  - <https://github.com/msune/libcdada/commits/master>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/README.md>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/test/benchmark.cc>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/test/array.s3>
- **Sources the enricher read:**
  - <https://github.com/msune/libcdada>
  - <https://github.com/msune/libcdada/commits/master>
  - <https://github.com/msune/libcdada/tree/master/src>
  - <https://github.com/msune/libcdada/issues?q=is%3Aissue>
  - <https://github.com/msune/libcdada/issues/14>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/README.md>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/doc/Custom.md>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/VERSION>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/config_m4/debug.m4>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/config_m4/rdtsc.m4>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/test/Makefile.am>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/test/benchmark.cc>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/test/array.s3>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/test/u552.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/src/Makefile.am>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/src/set.cc>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/src/map.cc>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/src/list.cc>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/set.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/map.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/list.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/utils.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/__common_internal.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/__set_internal.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/__map_internal.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/__list_internal.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/set_custom_cc.h>
  - <https://raw.githubusercontent.com/msune/libcdada/HEAD/include/cdada/map_custom_cc.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/msune/libcdada`) · [data/wave1/enrich/raw/github_com_msune_libcdada.json](../../../data/wave1/enrich/raw/github_com_msune_libcdada.json) (enrichment confidence 0.85)

</details>
