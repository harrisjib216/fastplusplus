# crumsort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense` · 🟡 stale

> Branchless in-place unstable C quicksort/quadsort hybrid, \~1.4-1.5x faster than pdqsort on random 32/64-bit ints.

| | |
|---|---|
| **Beats** | pdqsort |
| **Claimed result** | 64-bit ints: pdqsort avg 0.002668s vs crumsort avg 0.001927s, \~1.4x faster (derived from page data); 32-bit ints show a similar edge; on 128-bit long doubles pdqsort is faster than crumsort (crumsort is explicitly documented as slower there because of its partitioning scheme) |
| **Workload** | In-memory sort of 100,000-element arrays of 32/64/128-bit primitive types (int/long/long double) in random order, 100 samples, via the author's wolfsort benchmark harness (bench.c) |
| **Metric** | throughput |
| **Compiler and flags** | g++ -O3 -w -fpermissive bench.c, on WSL gcc version 7.5.0 (Ubuntu 7.5.0-3ubuntu1\~18.04) |
| **Adoption** | 336 stars |
| **Last commit** | 2024-07-27 |
| **Links** | [repository](https://github.com/scandum/crumsort) · [benchmark](https://github.com/scandum/crumsort/blob/main/README.md) |

## Verdict

Author's own wolfsort/bench.c harness (g++ -O3 -w -fpermissive, WSL gcc 7.5.0 on Ubuntu 18.04, no CPU model given) shows crumsort averaging 0.001927s vs pdqsort's 0.002668s on 100,000 random 64-bit ints (\~1.4x) and 0.001812s vs 0.002705s on 32-bit ints (\~1.5x), each best-of/avg-of 100 runs; on 128-bit long doubles pdqsort is faster (0.005975s vs crumsort's 0.008316s). No comparison against std::sort or std::stable_sort appears on the page.

## Use it when

- Sorting large arrays (README cites &gt;1,000,000 elements) of random-order 32/64-bit integers or pointer-sized keys where stability is not required
- Sorting 'tables' (structs/rows) by a 64-bit key or pointer, including tables that embed long doubles, since crumsort only moves the pointer, not the 128-bit payload
- Data with many duplicate/low-cardinality values (e.g. gender, age columns) thanks to the dual-pivot-style reverse partition on repeated pivots
- Environments where you can vendor plain C source (no package manager) and want a qsort drop-in with better throughput on primitives
- Throughput-oriented batch sorts rather than latency-sensitive incremental/partial sorts

## Skip it when

- Sorting arrays of long double (128-bit) directly as the array element type — README and this session's benchmark both show pdqsort winning there (0.005975s vs 0.008316s avg, 100K elements)
- Any workload requiring stability (equal keys must keep relative order) — crumsort is explicitly unstable; use fluxsort or quadsort instead
- Large nearly-sorted arrays where fluxsort will outperform it — crumsort runs on only 512 elements of auxiliary stack memory and, being unstable, scrambles pre-existing order more than fluxsort's mid-partition ordered-run detection
- Projects wanting an actively maintained dependency — last commit 2024-07-27, tagged stale, and the author's own TODO admits the long-double slowdown is unfixed
- Codebases wanting a single, normally-linked translation unit — crumsort.h uses macro-based generic instantiation that re-#includes crumsort.c per type, which is source-drop only, not a conventional compiled library

## How it is fast

Its 'fulcrum' partitioning scheme (a BlockQuicksort-style branchless variant of Hoare partitioning) holds the pivot in a swap slot so each element move takes 2 assignments instead of 3, and widens the swap buffer to batch 16 boundless comparisons branchlessly. Pivot selection scales pseudomedian-of-9/median-of-16 for small partitions up to median-of-128/256/512 for large ones. An analyzer pre-scans for sortedness and reverts to quadsort per segment, and quadsort (not insertion sort) handles partitions under 24 elements. Pivot retention (borrowed from pdqsort) triggers a reverse partition on runs of duplicate pivots for generic/low-cardinality data.

## Compared with alternatives

Over fluxsort (same author, catalogued sibling): pick crumsort when you don't need stability and want the extra throughput crumsort gets from being truly in-place, especially sorting large random-order integer/pointer arrays or tables with long-double payloads — fluxsort remains the better choice for large near-sorted data or when stability matters. crumsort is not shown against BlockQuicksort, Boost.Sort spreadsort, or IPS⁴o in this repo, so no direct comparison to those siblings is documented.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (crumsort.h pulls in quadsort.h/quadsort.c from the same repo; both are vendored together) |
| **Minimum toolchain** | C11 (crumsort.h includes stdalign.h); README's own benchmark compiles it with g++ -O3 -w -fpermissive, so it also compiles as permissive C++ |
| **Platforms** | not restricted to any ISA in source — plain portable C with no explicit SIMD intrinsics (branchlessness relies on compiler codegen, not intrinsics); README benchmark run was WSL/x86-64 only, no other platform is documented |
| **Thread safety** | not documented; no internal global/static mutable state was found in crumsort.c, so concurrent sorts of separate arrays look safe, but this is not stated by the author |
| **Drop-in for the baseline** | partial — qsort-API-compatible (same call shape as C's qsort), not std::sort's iterator/comparator interface, and it is unstable so it cannot substitute for std::stable_sort |

## Gotchas

- Header/source layering is macro-driven: crumsort.h does #define VAR/FUNC then #include "crumsort.c" repeatedly to generate typed variants — you vendor and #include the .c files, you don't link a normal compiled object
- crumsort_prim() only covers 32/64-bit signed/unsigned integers (size must be sizeof(int)/sizeof(long long), +1 for unsigned per an internal assert); other primitive/custom types require editing crumsort.h/quadsort.h yourself
- Uses 512 elements of stack swap memory shared with quadsort, plus O(log n) recursion stack — not a strictly O(1)-memory sort despite being 'in-place' in the informal sense
- The `cmp` macro must be defined (uncommented, per README) to get the fully branchless comparison path; without it you fall back to a normal function-pointer comparator with lower throughput

## Caveats and trade-offs

No CPU model is stated for the benchmark (only 'WSL gcc version...'), so it falls short of tier A; the README never benchmarks against std::sort/std::stable_sort directly, only against pdqsort and fluxsort (both already-catalogued projects), so baseline is recorded as pdqsort with baseline_in_list=false; numbers are from a 2024 README and result is type-dependent (crumsort loses to pdqsort on 128-bit types); The Unlicense is a public-domain dedication with no explicit patent grant

unstable, in-place, qsort()-compatible C API; branchless median/partition optimizations mainly benefit primitive integer types, not large value types (long double); porting guidance points to the simpler fluxsort/piposort instead

## Maintenance

Maintenance is stale (last commit 2024-07-27) but the Unlicense public-domain dedication and small source-drop footprint (two headers, two .c files) make it cheap to vendor and freeze at a known-good revision regardless.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks table compares crumsort against pdqsort (a recognizable incumbent unstable sort) with the quoted 64-bit averages 0.002668 vs 0.001927. Compiler and flags are stated (WSL gcc 7.5.0, g++ -O3 -w -fpermissive, wolfsort bench.c) but there is no CPU model, so it is C.
- **Verifier notes:** The numbers match (32-bit random: pdqsort 0.002705 vs crumsort 0.001812, about 1.5x, derived; 128-bit: pdqsort 0.005975 vs crumsort 0.008316, so crumsort is slower as the README says). There is no std::sort comparison on the page, so baseline=pdqsort with compared_against_cpp_std_directly=false is correct. Metadata verified: Unlicense, 336 stars, last commit 2024-07-27.
- **Pages the verifier opened:**
  - <https://github.com/scandum/crumsort>
  - <https://github.com/scandum/crumsort/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/scandum/crumsort>
  - <https://github.com/scandum/crumsort/blob/main/README.md>
  - <https://github.com/scandum/crumsort/blob/main/src/crumsort.h>
  - <https://github.com/scandum/crumsort/blob/main/src/crumsort.c>
  - <https://github.com/scandum/crumsort/blob/main/src/quadsort.h>
  - <https://github.com/scandum/crumsort/issues>
  - <https://github.com/scandum/crumsort/issues/4>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/scandum/crumsort`) · [data/wave1/enrich/raw/github_com_scandum_crumsort.json](../../../data/wave1/enrich/raw/github_com_scandum_crumsort.json) (enrichment confidence 0.85)

</details>
