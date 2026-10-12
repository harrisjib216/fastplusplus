# FastBinarySearch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Searching](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++ library for O(1)/vectorized insertion-point search in sorted float arrays, beating std::lower_bound scalar and SIMD-batched.

| | |
|---|---|
| **Beats** | std::lower_bound |
| **Claimed result** | up to two orders of magnitude (100x) throughput vs classic binary search (paper abstract); README benchmark on gcc 7 libstdc++: DirectCacheFMA scalar 496.44 M searches/s vs LowerBound (std::lower_bound) scalar 14.02 M searches/s, single precision (\~35x, derived from page data); AVX-2 DirectFMA 992.87 M searches/s vs LowerBound scalar 14.02 M searches/s (\~71x, derived from page data) |
| **Workload** | Scalar and vectorial (SSE-4/AVX-2) insertion-point search for random query points in a sorted array of 2048 single- or double-precision floats |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2620 v3 @ 2.40GHz |
| **Compiler and flags** | gcc 7 (README); default benchmark build flags from source/paper/Makefile: g++ -c -std=c++0x -O3 -mfma -mavx2 (flags come from the build file, not restated next to the results) |
| **Adoption** | 153 stars; subset shipped in NAG Library routine m01ndc |
| **Last commit** | 2024-12-19 |
| **Links** | [repository](https://github.com/fabiocannizzo/FastBinarySearch) · [benchmark](https://github.com/fabiocannizzo/FastBinarySearch/blob/master/README.md) |

## Verdict

On an Intel Xeon E5-2620 v3 (Haswell, 2014) with gcc 7 / libstdc++, the README's own benchmark (2048-element sorted array, single precision) shows the O(1) DirectCacheFMA method at 496.44M scalar searches/s vs std::lower_bound's 14.02M/s scalar -- about 35x, apples-to-apples. The larger '\~71x/100x' figures instead compare AVX-2 batched throughput (992.87M/s) against std::lower_bound's scalar-only number, which only reflects real-world gains if the caller actually issues batched queries.

## Use it when

- Repeated point-location queries against the same static sorted float/double array (spline interpolation, ECDF lookup) where upfront index preprocessing pays off
- Queries arrive in batches so the SIMD vectorial() path can be used -- this is where the largest (\~35x scalar, \~70x+ batched) gains actually show up
- The array's values are close to log-uniformly distributed across their range, keeping the O(1) Direct index table compact
- Target is x86-64 with AVX2/FMA (or at least SSE4.1) available at compile time
- You can accept a template-heavy, per-array engine object instead of a generic iterator-based lower_bound(first,last,val) call

## Skip it when

- You need a generic, iterator-based drop-in for std::lower_bound over arbitrary containers/types -- this only supports float/double arrays via its own engine object
- The array is mutated often -- Direct/DirectCache methods need their index table rebuilt on every change, and preprocessing isn't free
- Target is ARM/other non-x86 -- no NEON/ARM port exists (open, unclaimed issue since 2023)
- Memory is tight -- DirectCache/Direct2 variants need extra memory for the index table on top of the array itself
- Workload is a single occasional scalar query -- realistic scalar-to-scalar gain is \~35x at best (per README numbers), not the headline \~100x figure, which mixes batched SIMD throughput against std::lower_bound's scalar number

## How it is fast

Its headline technique (Direct/DirectCache, the O(1) family) precomputes a linear scaling function that maps a float key straight to a bucket index in a preprocessed table, replacing comparison-based search with arithmetic and a table lookup for roughly log-uniformly distributed data. Other included algorithms (Eytzinger-layout cache-friendly binary search, branchless BitSet search, k-ary ternary/pentary/nonary search) cut iteration count or branch mispredicts more conventionally. The vectorial() path uses SSE4.1/AVX2 and FMA intrinsics to compute several insertion points per call instead of one.

## Compared with alternatives

Pick FastBinarySearch when the data is a sorted array of floats/doubles and you can preprocess it once and batch queries -- no sibling here offers an O(1) indexed technique or documented AVX2-batched throughput this large. Pick sb_lower_bound instead when you need a true drop-in, single-query, iterator-based replacement with zero preprocessing (its own gain, \~1.8x, is far more modest but has no setup cost or type restriction to floats).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (STL only); Intel MKL is only an optional comparison target in the benchmark harness, not a library dependency |
| **Minimum toolchain** | C++11-class syntax (paper benchmark builds with -std=c++0x); the library's own demo Makefile defaults to -std=c++17. Needs a compiler exposing SSE4.1/AVX2/FMA intrinsics (GCC/Clang -mavx2 -mfma, or MSVC equivalent) for the fast paths |
| **Platforms** | x86-64 (SSE4.1/AVX2/FMA needed for the fastest scalar and all vectorial paths); no ARM/NEON support (issue #2, open, unclaimed as of 2023) |
| **Thread safety** | not documented; the engine object is built once over an immutable array and scalar()/vectorial() only read from it, so concurrent read-only use looks safe by inspection, but the author states nothing about this |
| **Drop-in for the baseline** | partial -- functionally equivalent (returns the same insertion index as std::lower_bound), but the call shape differs: construct a BinAlgo&lt;InstrSet,T,Algo&gt; engine per array/algorithm and call .scalar()/.vectorial() rather than passing iterators to lower_bound() |

## Gotchas

- A 2020 memory-alignment bug (issue #1) made release/non-DEBUG builds return wrong results for some SIMD levels; the author fixed it and the reporter confirmed correct output on master, but the issue itself is still open on GitHub and this session did not re-derive the fix's correctness independently
- That same issue shows -mavx (plain AVX, no AVX2/FMA) failing to compile on gcc 7 with an 'inlining failed... target specific option mismatch' error -- stick to the FMA/AVX2 or SSE2 SIMDLEVEL options that the README benchmarks actually use
- O(1) Direct/DirectCache methods validate the computed index range and throw std::invalid_argument if the array's value range would overflow a uint32 index, rather than silently corrupting results
- No ARM/NEON port; x86-only today

## Caveats and trade-offs

Benchmark CPU (Xeon E5-2620 v3, Haswell, 2014) and gcc 7 are dated. Compiler flags come from the repo Makefile default build, not from the README text. The README table dates from 2017-2019; I did not check it against the JPDC 2018 paper's own figures. The biggest ratios compare vectorial (batched SSE-4/AVX-2) throughput with LowerBound's scalar-only figure. That is apples-to-oranges unless the caller does batched queries. The scalar-to-scalar ratio (\~35x) is the fair per-query figure. Workload is floats/doubles in a 2048-element array only. The Direct methods need precomputed index memory.

Best suited to roughly log-uniform/logarithmically distributed sorted float arrays; the O(1) indexed variant needs extra memory and upfront preprocessing of the array; header-only C++ API differs from std::lower_bound's iterator-based signature; largest gains require SSE/AVX vectorial batch queries, scalar-only gains are smaller

## Maintenance

Stale: last commit 2024-12-19 with sporadic activity, and both open GitHub issues (an unclaimed ARM-port request, and a 2020 miscompile report the author says he fixed but never closed) remain open. Still MIT-licensed, header-only, and small enough to vendor; a subset ships in NAG's commercial m01ndc routine, which is some evidence of real-world use beyond the 153 stars.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. README table (Xeon E5-2620 v3, LowerBound = std::lower_bound from gcc 7 STL) is produced by public benchmark code source/paper/paper.cpp. Its build file source/paper/Makefile (committed 2017, before the table) sets the default flags g++ -std=c++0x -O3 -mfma -mavx2. Code, compiler, flags and CPU are all available, and the JPDC 2018 peer-reviewed paper backs the method.
- **Verifier notes:** Numbers verified exactly in README: 496.44 vs 14.02 M searches/s scalar single, 992.87 AVX-2. Metadata matches gh: MIT, 153 stars, last commit 2024-12-19 (stale). Tier moved B to A because Makefile flags plus public paper.cpp harness make it reproducible.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fabiocannizzo/FastBinarySearch>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/README.md>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/paper/Makefile>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/Makefile>
- **Sources the enricher read:**
  - <https://github.com/fabiocannizzo/FastBinarySearch>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/README.md>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/Makefile>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/paper/Makefile>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/include/BinAlgo.h>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/include/Portable.h>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/include/BinSearch.h>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/include/Type.h>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/source/include/Algo-Direct-Common.h>
  - <https://github.com/fabiocannizzo/FastBinarySearch/blob/master/LICENSE>
  - <https://github.com/fabiocannizzo/FastBinarySearch/issues/1>
  - <https://github.com/fabiocannizzo/FastBinarySearch/issues/2>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/fabiocannizzo/fastbinarysearch`) · [data/wave1/enrich/raw/github_com_fabiocannizzo_fastbinarysearch.json](../../../data/wave1/enrich/raw/github_com_fabiocannizzo_fastbinarysearch.json) (enrichment confidence 0.85)

</details>
