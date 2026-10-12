# blitsort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense` · 🟡 stale

> In-place, stable, adaptive C sort beating std::stable_sort via rotations instead of an O(n) swap buffer.

| | |
|---|---|
| **Beats** | std::stable_sort |
| **Claimed result** | random order, 64-bit: std::stable_sort avg 0.006207s vs blitsort avg 0.002518s, \~2.5x faster (derived from page data); random order, 32-bit: 0.006025s vs 0.002341s, \~2.6x faster (derived); much larger gaps on structured distributions (e.g. descending order: 0.000921s vs 0.000055s, \~17x, derived) |
| **Workload** | In-memory stable sort of 100,000-element 32/64/128-bit arrays across many distributions (random order, random % 100, ascending, descending, sawtooth, random tail/half, etc.), 100 samples, via the author's wolfsort benchmark harness; README explicitly states 'Stablesort is g++'s std:stable_sort function' |
| **Metric** | throughput |
| **Compiler and flags** | g++ -O3 -w -fpermissive bench.c, on WSL 2 gcc version 7.5.0 (Ubuntu 7.5.0-3ubuntu1\~18.04) |
| **Adoption** | 715 stars |
| **Last commit** | 2024-07-27 |
| **Links** | [repository](https://github.com/scandum/blitsort) · [benchmark](https://github.com/scandum/blitsort/blob/main/README.md) |

## Verdict

On the author's wolfsort harness (g++ -O3 -w -fpermissive, WSL2 gcc 7.5.0, libstdc++'s std::stable_sort as baseline), blitsort sorted 100,000 random-order 64-bit ints in avg 0.002518s vs 0.006207s for std::stable_sort (\~2.5x) and 32-bit ints in 0.002341s vs 0.006025s (\~2.6x); gains are far larger on structured distributions (e.g. \~17x on descending order) but shrink to roughly parity on 128-bit long doubles. No CPU model was reported for the runs.

## Use it when

- Need a stable sort in C with a small, bounded auxiliary-memory footprint (no O(n) swap buffer) rather than std::stable_sort's allocation.
- Input has structure (ascending/descending runs, sawtooth, pipe-organ, partially sorted tails) — the adaptive analyzer gives the largest wins here (README table: \~17x on 100K descending 32-bit ints vs std::stable_sort).
- Sorting primitive 32/64-bit integers, doubles, or long doubles, or larger records via pointer indirection (e.g. strings) under a qsort-compatible call site.
- Codebase can vendor a small C source drop (blitsort.h/.c + bundled quadsort.h/.c) rather than link a library, and wants roughly 2.5x throughput over libstdc++ std::stable_sort on random 64-bit data.
- Migrating qsort() call sites incrementally without adopting a templated/iterator C++ API.

## Skip it when

- 128-bit / long double keys: the README's own table shows blitsort roughly at parity with std::stable_sort on random order (0.011423s vs 0.011047s avg) and clearly behind pdqsort/crumsort there.
- 'Ascending tiles' and 'bit reversal' distributions: blitsort is measurably slower than std::stable_sort in the README's own data (0.001397s vs 0.000948s; 0.002160s vs 0.001355s), so gains aren't universal.
- Stability isn't required and raw speed on plain random order is the goal: the README's own benchmark shows pdqsort and crumsort both beating blitsort on random-order 32/64-bit ints.
- Need a modern templated/iterator C++ API, exceptions, or custom allocator support: blitsort is a C, qsort()-signature function, not a std::sort drop-in.
- Want active upstream maintenance or CI/test coverage signals: last commit 2024-07-27, no CI config visible in the tree, and the published benchmarks run on gcc 7.5.0 inside WSL2 with no bare-metal CPU model given.

## How it is fast

Two custom primitives do most of the work: a 'trinity rotation' (the author's own array-rotation algorithm, described as significantly faster than standard triple-reversal rotation) used to move partitions in place instead of copying to a swap buffer, and a 'monobound binary search' used to locate rotation points, claimed up to 2x faster than a typical binary search. An analyzer detects already-sorted, reverse-sorted, and mostly-sorted runs up front and routes them to rotate quadsort/fluxsort fast paths. On primitive types, uncommenting the `cmp` macro (or defining it before include) switches to branchless comparisons, which the README says roughly doubles throughput.

## Compared with alternatives

Pick blitsort over its own siblings quadsort/fluxsort when you need stability but can't spare their O(n) auxiliary buffer, and over crumsort/pdqsort when stability is required (both are unstable, and crumsort is faster than blitsort on plain random-order data per the README's own pdqsort/crumsort table). Pick fluxsort or quadsort instead when O(n) scratch memory is available and stability plus a bit more raw speed matters more than memory footprint.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | quadsort.c/quadsort.h (bundled in src/, required include); otherwise only the C standard library |
| **Minimum toolchain** | not documented precisely; header uses &lt;stdalign.h&gt; (C11) and assert/errno/string/stdio/float.h; README benchmarks built with gcc 7.5.0 / g++ -O3 -w -fpermissive |
| **Platforms** | any (portable C, no intrinsics in the public API); all published benchmarks are x86-64 under WSL2, no other platform data given |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — matches qsort(void\*, size_t, size_t, CMPFUNC\*) exactly, but std::stable_sort callers need an adapter since there is no template/iterator API |

## Gotchas

- Full branchless speedup requires manually defining the `cmp` macro before including blitsort.h (or editing bench.c); without it, primitive comparisons go through a function pointer and the README says throughput roughly halves.
- blitsort_prim() only supports 32/64-bit signed/unsigned integers (size codes 4/5/8/9); other sizes hit an assert.
- blitsort() itself only dispatches sizes matching char/short/int/long long/long double; any other element size falls through to an assert rather than a qsort() fallback (that fallback line is commented out in blitsort.h).
- 'In-place' is the loose community definition: it still uses up to 512 elements of swap memory by default (configurable down to 32 or sqrt(n)) plus O(log n) recursion stack, not strict O(1).

## Caveats and trade-offs

No CPU model is stated (only WSL 2/gcc 7.5.0), and the run is inside WSL rather than bare metal, so it falls short of tier A. The benchmark uses an old libstdc++ (gcc 7.5) and may not match current blitsort or current libstdc++. The biggest speedups are on already-ordered or patterned data, which favors adaptive sorts. On the same table blitsort is not faster everywhere: on 128-bit random order the averages are 0.011047s (std::stable_sort) vs 0.011423s (blitsort), and blitsort is slower on 'ascending tiles' (0.000948 vs 0.001397) and 'bit reversal' (0.001355 vs 0.002160). The Unlicense is a public-domain dedication with no patent grant.

stable, in-place (uses rotations instead of an O(n) swap buffer), qsort()-compatible C interface rather than a template/iterator-based API; also benchmarked against gfx::cpp-TimSort in the same table, where blitsort is faster in most but not all distributions

## Maintenance

Stale since the last commit on 2024-07-27 (0 open issues, all 5 historical issues closed with no unresolved bugs), but Unlicense (public domain, no patent grant) and a small qsort-compatible C source make it cheap to vendor and freeze at a known-good commit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README section 'Benchmark: blitsort vs std::stable_sort vs gfx::timsort' has a data table with all quoted averages (64-bit random 0.006207 vs 0.002518, 32-bit random 0.006025 vs 0.002341, descending 0.000921 vs 0.000055), states compiler and flags (WSL 2 gcc 7.5.0, g++ -O3 -w -fpermissive bench.c) and uses the public wolfsort harness, but no CPU model is given, so it is C, not A.
- **Verifier notes:** All claimed numbers match the README table rows exactly, and the metadata checks out (Unlicense, 715 stars, last commit 2024-07-27, not a fork or archived). I only expanded the caveats to cover the 128-bit parity and the distributions where blitsort loses.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/scandum/blitsort>
  - <https://github.com/scandum/blitsort/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/scandum/blitsort>
  - <https://github.com/scandum/blitsort/blob/main/README.md>
  - <https://github.com/scandum/blitsort/blob/main/src/blitsort.h>
  - <https://github.com/scandum/blitsort/blob/main/LICENSE>
  - <https://github.com/scandum/blitsort/issues>
  - <https://github.com/scandum/blitsort/issues/3>
  - <https://github.com/scandum/blitsort/issues/5>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/scandum/blitsort`) · [data/wave1/enrich/raw/github_com_scandum_blitsort.json](../../../data/wave1/enrich/raw/github_com_scandum_blitsort.json) (enrichment confidence 0.62)

</details>
