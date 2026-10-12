# gridsort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense` · 🟡 stale

> Stable C sort using a cache-friendly bucketed grid; qsort-compatible interface; 1.4x-2.6x faster than std::stable_sort on 1M-int arrays.

| | |
|---|---|
| **Beats** | std::stable_sort |
| **Claimed result** | random order, 32-bit, 1M elements: std::stable_sort avg 0.073191s vs gridsort avg 0.051147s, \~1.4x faster (derived from page data); 'generic order' distribution: 0.041741s vs 0.016224s, \~2.6x faster (derived); against libc qsort() at 100,000 128-bit elements: 0.019996s vs 0.012730s, \~1.6x faster (derived) |
| **Workload** | In-memory stable sort of 1,000,000-element 32/64/128-bit arrays across multiple distributions (random order, ascending, descending, generic order, sawtooth, random tail/half, ascending tiles), 10 samples, via the author's wolfsort benchmark harness; a second, separate benchmark compares gridsort against the C library qsort() (a mergesort variant) at 100,000 elements |
| **Metric** | throughput |
| **Compiler and flags** | std::stable_sort comparison: g++ -O3 -w -fpermissive bench.c on WSL gcc 7.5.0 (Ubuntu 7.5.0-3ubuntu1\~18.04); qsort() comparison: gcc -O3 bench.c on WSL gcc 7.4.0 (Ubuntu 7.4.0-1ubuntu1\~18.04.1), comparisons not inlined |
| **Adoption** | 211 stars |
| **Last commit** | 2024-07-27 |
| **Links** | [repository](https://github.com/scandum/gridsort) · [benchmark](https://github.com/scandum/gridsort/blob/main/README.md) |

## Verdict

Against libstdc++ std::stable_sort (g++ -O3 -w -fpermissive, WSL gcc 7.5.0/Ubuntu 18.04, comparisons inlined, no CPU model stated), sorting 1,000,000 random-order 32-bit ints, 10-sample average: gridsort 0.051147s vs std::stable_sort 0.073191s (\~1.4x); on 'generic order' 1M 32-bit, 0.016224s vs 0.041741s (\~2.6x). A separate, older benchmark (gcc -O3, WSL gcc 7.4.0, comparisons not inlined) shows gridsort \~1.6x faster than glibc's qsort() (a mergesort variant, not std::sort) on 100,000 random-order 128-bit elements (0.012730s vs 0.019996s).

## Use it when

- C codebases already calling qsort() that want a stable, drop-in-signature replacement and can tolerate O(n) extra memory
- 1M-element-scale arrays of 8/16/32/64-bit ints or long doubles with partial existing order (ascending/descending runs, sawtooth, 'generic order') -- this is where gridsort showed its largest measured edge (\~2.6x vs std::stable_sort)
- Sorting arrays of pointers or handles (size_t/void\*-sized elements) to indirectly sort structs, since the sort itself only accepts elements of size 1/2/4/8/sizeof(long double)
- Projects wanting a small, dependency-free, public-domain (Unlicense) C source drop rather than a C++ template library

## Skip it when

- Elements whose size isn't exactly 1, 2, 4, 8, or sizeof(long double) bytes -- gridsort asserts on other sizes, and that assert compiles out under NDEBUG, silently skipping the sort
- Multi-threaded callers: gridsort.c/gridsort.h declare a single global size_t BSC_Z reused by every type specialization and recomputed at the start of each grid build -- observed directly in source, not documented, and not safe for concurrent gridsort() calls
- Memory-constrained environments: needs O(n) auxiliary allocation (2\*sqrt(n) blocks of sqrt(n) elements per the README) versus in-place alternatives
- C++ code wanting a literal std::stable_sort drop-in -- the interface is qsort-style (void\*, size_t, size_t, CMPFUNC\*), not iterators/functors, so it needs a wrapper and is only exercised on POD-like data in the benchmarks
- Chasing the best possible raw random-data throughput or an actively maintained option -- the README's own 'Porting' notes point to the author's newer fluxsort/quadsort as faster/simpler alternatives, and the repo has had no commits since 2024-07-27

## How it is fast

Speed comes from three layered techniques: a boundless binary search (README claims up to 2x faster than a bounds-checked binary search) to pin down the right bucket, a self-balancing grid ('binary cube') sized so buckets stay cache-resident, and quadsort's branchless merge (8-element memcpy blocks with head/tail branchless merges) used both to sort overflowing buckets and to do the final merge. It also switches to an adaptive binary search once it detects already-sorted runs, which is consistent with its larger lead over std::stable_sort on 'generic order' and ascending/descending inputs than on pure random data.

## Compared with alternatives

Among the sibling stable sorts from the same author/repo family (quadsort, fluxsort, blitsort), pick gridsort specifically for its bucket/binary-cube behavior on partially-ordered or structurally patterned data ('generic order', ascending/descending runs), where its README-measured lead over std::stable_sort was largest (\~2.6x vs \~1.4x on pure random order); for best raw random-data throughput or lower memory overhead, the README's own porting notes point to the newer fluxsort/quadsort instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the C standard library (stdlib.h, stdio.h, assert.h, errno.h; quadsort.h adds float.h, string.h); bundles its own copy of quadsort.h/quadsort.c in the same src/ directory |
| **Minimum toolchain** | not documented; bench.c's header comment lists gcc -O3, clang -O3, or g++ -O3 as working compile lines; plain C with no version-specific features observed |
| **Platforms** | any (portable C, no SIMD intrinsics or threading in gridsort.c/quadsort.c); note sizeof(long double) is platform/ABI-dependent, which affects the 128-bit type-size dispatch case |
| **Thread safety** | not documented; source shows a shared, non-thread-local global (BSC_Z) written at the start of every top-level call, which looks unsafe for concurrent gridsort() invocations |
| **Drop-in for the baseline** | partial -- qsort-compatible C signature (void \*array, size_t nmemb, size_t size, CMPFUNC \*cmp), not a std::stable_sort drop-in; C++ callers need a wrapper, and only elements of size 1/2/4/8/sizeof(long double) are accepted directly |

## Gotchas

- Only element sizes matching sizeof(char/short/int/long long/long double) are supported; other sizes hit an assert() that is a no-op under NDEBUG, so release builds can silently fail to sort
- Falls back to plain quadsort() for nmemb &lt; BSC_X\*BSC_X (1024 elements), so small arrays never exercise the grid/bucket logic
- Global BSC_Z is shared mutable state across all five type specializations (8/16/32/64/128-bit) -- not safe to call from multiple threads concurrently
- The 'long double' case is used as the stand-in for 128-bit elements; its actual byte width varies by platform/ABI, so the size dispatch is not portable as-is

## Caveats and trade-offs

No CPU model is stated for either benchmark (WSL/gcc version only), so it falls short of tier A. The benchmarks use old gcc 7.x toolchains. The qsort() comparison is against glibc's mergesort-based qsort, not std::sort; it is a separate, older benchmark (gcc 7.4.0, not inlined) from the std::stable_sort one. The Unlicense is a public-domain dedication with no patent grant.

stable comparison sort that stores data in an O(n) auxiliary 2-D self-balancing grid rather than sorting in-place; qsort()-compatible C interface; author states it 'was the fastest comparison sort for random data for a brief period' implying it has since been superseded on raw random-data speed by the author's own crumsort/fluxsort

## Maintenance

Stale: last commit 2024-07-27 (over two years old as of this writing) with zero open issues and no CPU model given for either benchmark; still Unlicense (public-domain, no patent grant) and small enough (two header + two source files, no dependencies) to vendor as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README benchmark states 'Comparisons for gridsort and std::stable_sort are inlined', and its table contains the quoted 1M-element averages (random 0.073191 vs 0.051147, generic 0.041741 vs 0.016224). The qsort table has 0.019996 vs 0.012730. Compiler and flags are stated and the wolfsort harness is public, but there is no CPU model, so it is C.
- **Verifier notes:** All quoted numbers match the README tables. I corrected compiler_and_flags because the qsort benchmark used a different toolchain (gcc 7.4.0, gcc -O3). Metadata verified: Unlicense, 211 stars, last commit 2024-07-27.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/scandum/gridsort>
  - <https://github.com/scandum/gridsort/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/scandum/gridsort>
  - <https://github.com/scandum/gridsort/blob/main/README.md>
  - <https://github.com/scandum/gridsort/blob/main/src/gridsort.h>
  - <https://github.com/scandum/gridsort/blob/main/src/gridsort.c>
  - <https://github.com/scandum/gridsort/blob/main/src/quadsort.h>
  - <https://github.com/scandum/gridsort/blob/main/src/quadsort.c>
  - <https://github.com/scandum/gridsort/blob/main/src/bench.c>
  - <https://github.com/scandum/gridsort/blob/main/LICENSE>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/scandum/gridsort`) · [data/wave1/enrich/raw/github_com_scandum_gridsort.json](../../../data/wave1/enrich/raw/github_com_scandum_gridsort.json) (enrichment confidence 0.6)

</details>
