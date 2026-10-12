# scandum/binary_search (monobound / boundless binary search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Searching](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense` · 🟡 stale

> C binary-search variants; monobound_bsearch() is a bsearch()-compatible drop-in \~1.4-2.35x faster than libc bsearch().

| | |
|---|---|
| **Beats** | bsearch() (C standard library) |
| **Claimed result** | README: monobound binary search 'executes two to four times faster than the standard binary search on arrays smaller than 1 million 32 bit integers' and is 'up to 60% faster than the standard binary search when comparing 32 bit integers'. Both compare against the repo's own standard_binary_search, not bsearch. Boundless binary search gain 'should be around 20% when comparing 32 bit integers'. Against libc bsearch() with the same comparator-callback interface (monobound_bsearch.c): 0.000136 vs 0.000202 s at 10 elements, 0.000265 vs 0.000623 s at 1000, 0.002641 vs 0.003784 s at 10M, about 1.4-2.35x faster across sizes (derived from page data). |
| **Workload** | 32-bit integer sorted arrays, sizes from 1 to 10 million elements; 1,000-10,000 iterations per size, best-of run timed |
| **Metric** | latency |
| **Hardware** | Intel i3 quad-core, under WSL2 (exact CPU model/SKU not given) |
| **Compiler and flags** | gcc -O3, GCC 7.5.0 (Ubuntu 7.5.0-3ubuntu1\~18.04) |
| **Adoption** | 683 stars, 44 forks |
| **Last commit** | 2025-06-20 |
| **Links** | [repository](https://github.com/scandum/binary_search) · [benchmark](https://github.com/scandum/binary_search/blob/master/README.md) |

## Verdict

In the repo's own monobound_bsearch() vs. libc bsearch() table (gcc -O3, GCC 7.5.0 on Ubuntu 18.04 under WSL2, CPU stated only as 'Intel i3 quad-core', 1,000 runs best-of, 32-bit integer arrays), monobound_bsearch() beats bsearch() by roughly 1.4x-2.35x across sizes from 10 to 10,000,000 elements (e.g. 0.000136s vs 0.000202s at 10 elements; 0.002641s vs 0.003784s at 10,000,000). The more prominently stated 'two to four times faster' and 'up to 60% faster' README claims are against the repo's own standard_binary_search (a textbook algorithm), not against bsearch() or std::binary_search.

## Use it when

- Sorted 32-bit-int (or similarly cheap-to-compare primitive) arrays where code already calls libc bsearch() and you want a same-signature swap with a measured 1.4-2.35x speedup (repo's own gcc -O3 benchmark).
- Small-to-medium arrays (well under 1M elements), where the README reports the largest monobound gains ('two to four times faster' vs the repo's own textbook binary search, not vs bsearch()).
- C or C-callable codebases that can vendor a single small .c file under a public-domain-equivalent license (Unlicense) with zero third-party dependencies.
- Builds that reliably use -O1/-O2/-O3 — the README states monobound 'degrades badly under -O0'.
- Cases needing a stable binary search (README states all variants return the rightmost index on duplicate keys) and defined zero-length-array behavior.

## Skip it when

- C++ code calling std::lower_bound/std::binary_search/std::equal_range directly — there's no header-only C++ template here; you'd have to hand-port the algorithm into your own templated function.
- Workloads wanting SIMD/vectorized search or the largest possible speedups on very large arrays — sibling entries (FastBinarySearch, SIMD Quad, simdsearch, sb_lower_bound) target that more directly with more rigorous, more recent hardware.
- Projects needing active maintenance — last commit 2025-06-20, single maintainer, no releases/tags/CI, no test suite beyond the benchmark harness.
- Decisions that need current-hardware evidence — every published number is from one 2018-era Ubuntu 18.04 / GCC 7.5.0 WSL2 machine described only as 'Intel i3 quad-core' (no exact SKU); real gains on modern CPUs/compilers are unverified here.
- Non-integer or expensive-comparator keys — all headline numbers are for 32-bit integer comparisons; the README only speculates (unbenchmarked) that the deferred-equality tradeoff changes for string comparisons.

## How it is fast

Monobound search replaces the classic bot/mid/top bookkeeping with a single running offset and a size that is halved each iteration, giving one key check, one integer compare and dynamic loop unrolling (README claims this unrolling, not fewer comparisons, is the real source of the gain, unlocking further compiler/CPU-level optimization). Boundless binary search similarly drops the explicit upper-bound variable tracked by the textbook algorithm to cut per-iteration integer assignments, worth about 20% per the README. A GitHub issue (#7) challenged the README's explanation of why unrolling helps (ILP/branch-removal wording), but the reporter walked the objection back in the same thread; the loop-unrolling mechanism itself is not otherwise disputed in what I read.

## Compared with alternatives

Pick this when you need a bsearch()-compatible C drop-in with a same-signature comparator interface and are fine with a dated but directly-against-bsearch() benchmark; sb_lower_bound, FastBinarySearch, and SIMD Quad/simdsearch all target C++ std::lower_bound/std::binary_search or memmem with more recent, more rigorous hardware evidence and larger claimed speedups, and are the better pick if you can use C++ templates or need SIMD-scale gains.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standard C headers only: stdlib.h, stdio.h, string.h; sys/time.h and time.h are used only by the benchmark harness, not the search functions themselves) |
| **Minimum toolchain** | not documented beyond 'C' compiled with gcc -O1/-O2/-O3 (benchmarks used GCC 7.5.0); no C99/C11 requirement is stated |
| **Platforms** | not documented; only benchmarked on x86-64 Linux (WSL2/Ubuntu 18.04). The code itself is portable C with no architecture-specific intrinsics in the two files read |
| **Thread safety** | not documented; the search functions read only their input array and local variables (no globals), so concurrent reads of an immutable array should be safe, but the repo makes no explicit claim |
| **Drop-in for the baseline** | partial — explain: monobound_bsearch() in monobound_bsearch.c matches libc bsearch()'s exact call signature, so it is a true drop-in for bsearch(); monobound_binary_search() in binary_search.c uses a different (array, size, key) signature and is not iterator/template-based, so it does not drop into std::lower_bound/std::binary_search call sites. |

## Gotchas

- monobound_binary_search must be compiled with -O1/-O2/-O3; the README explicitly warns it 'degrades badly under -O0'.
- Default semantics are stable/rightmost-index on duplicate keys (per README) — check this matches your needs if you actually want lower_bound-style leftmost-index behavior.
- Quaternary, monobound-interpolated and adaptive variants are described in the README prose but only monobound_interpolated_search appears in the benchmark tables I read; quaternary/adaptive have no benchmark numbers in this repo.
- Issue #7 disputes part of the README's technical explanation for the speedup (ILP/branch-removal wording); worth a skim before citing the 'why' verbatim, though the numbers themselves aren't challenged there.

## Caveats and trade-offs

Baseline is C's bsearch() and a generic 'textbook' binary search, not std::lower_bound/std::binary_search directly, so this is an indirect (but explicitly named) comparison; CPU model is imprecise ('i3 quad-core'); all numbers come from one 2018-era Ubuntu/GCC 7.5 machine.

monobound variant needs -O1/-O2/-O3 to see its gain (degrades badly under -O0); plain C, not a templated drop-in for std::lower_bound/std::binary_search; benchmark's baseline is bsearch()/a textbook binary search, not the C++ standard library templates named in this category

## Maintenance

Stale but stable: last commit 2025-06-20, single-maintainer repo with no releases, CI, or test suite beyond the benchmark harness itself; Unlicense (public domain equivalent) and a single small .c file make it cheap to vendor and audit despite the inactivity.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** Code is public (binary_search.c, monobound_bsearch.c benchmarks bsearch from stdlib.h), and the compiler and flags are stated (GCC 7.5.0, gcc -O3, WSL 2). The CPU is only 'Intel i3 quad-core processor' with no model, so tier A is not met: C.
- **Verifier notes:** The record misattributed the README's 'up to 60% faster' claim to bsearch(). That claim is vs the textbook standard binary search. The real bsearch table shows \~1.4-2.35x. Metadata verified: Unlicense, 683 stars, 44 forks, last commit 2025-06-20 (stale).
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/scandum/binary_search/blob/master/README.md>
  - <https://github.com/scandum/binary_search>
  - <https://github.com/scandum/binary_search/blob/master/monobound_bsearch.c>
- **Sources the enricher read:**
  - <https://github.com/scandum/binary_search>
  - <https://github.com/scandum/binary_search/blob/master/README.md>
  - <https://github.com/scandum/binary_search/blob/master/monobound_bsearch.c>
  - <https://github.com/scandum/binary_search/blob/master/binary_search.c>
  - <https://github.com/scandum/binary_search/issues/7>
  - <https://github.com/scandum/binary_search/issues>
  - <https://github.com/scandum/binary_search/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/scandum/binary_search`) · [data/wave1/enrich/raw/github_com_scandum_binary_search.json](../../../data/wave1/enrich/raw/github_com_scandum_binary_search.json) (enrichment confidence 0.65)

</details>
