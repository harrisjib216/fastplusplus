# buffet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🟡 stale

> C buffer type with SSO and refcounted views beating std::string on append, but not on plain memcopy or views.

| | |
|---|---|
| **Beats** | std::string |
| **Claimed result** | SPLITJOIN: buffet 1397 ns vs C++ 3317 ns vs C 2782 ns (\~2.4x vs the C++ version, derived from page data). But SPLITJOIN_cpp in src/bench.cpp splits into vector&lt;std::string_view&gt; and joins into a malloc'd char\*, so it does not use std::string. Against real std::string (APPEND_cpp), buffet is 30.2 vs 36.5 ns at 8/16, 30.1 vs 49.0 ns at 24/4 and 28.8 vs 48.1 ns at 24/32 (\~1.2-1.7x, derived from page data), but slower at 8/4 (16.3 vs 10.9 ns). MEMVIEW: std::string_view 0.609 ns vs buffet 6.36 ns, so buffet is slower. MEMCOPY compares only against C, not std::string. |
| **Workload** | Google Benchmark microbenchmarks (memcopy, memview, append, split+join) on byte buffers from 8 to 8192 bytes, comparing buffet (a C SSO/refcounted buffer) against std::string/std::string_view and C string functions. |
| **Metric** | latency |
| **Hardware** | "weak Core i3" (exact CPU model/generation not stated) |
| **Compiler and flags** | g++ -std=c++2a -fpermissive -g -O2 for src/bench.cpp; libbuffet built with gcc -std=c11 -O2 -DNDEBUG (per repo Makefile); harness is Google Benchmark |
| **Adoption** | 414 stars |
| **Last commit** | 2023-11-16 |
| **Links** | [repository](https://github.com/alcover/buffet) · [benchmark](https://raw.githubusercontent.com/alcover/buffet/main/README.md) |

## Verdict

On an unnamed "weak Core i3" (no CPU model given), Google Benchmark via g++ -std=c++2a -O2 against libstdc++: buffet's append beats real std::string (built with operator+=) by \~1.2-1.7x at 8/16, 24/4 and 24/32 init/append byte sizes, but loses at 8/4 (16.3 vs 10.9 ns). The headline SPLITJOIN figure (1397ns vs 3317ns) is not a std::string comparison - src/bench.cpp's SPLITJOIN_cpp splits into vector&lt;string_view&gt; and joins into a malloc'd char\*, bypassing std::string entirely. std::string_view beats buffet's view construction by \~10x, and plain C memcpy beats buffet's memcopy at every size from 32 to 8192 bytes.

## Use it when

- Pure-C codebases that want std::string-like ergonomics (SSO, no-copy slicing) without pulling in C++
- Split/join-heavy workloads on many small-to-medium substrings, where view aliasing avoids per-substring allocation
- Incremental string building in roughly the 8-32 byte init/append range, matching the one workload buffet actually beats std::string on
- Short strings (&lt;=21 bytes) where SSO avoids heap allocation entirely
- GPL-3.0 licensing is acceptable for the project

## Skip it when

- Proprietary/closed-source code - GPL-3.0 requires the whole linked work to be GPL-compatible
- Multithreaded sharing of a Buffet or its views - README lists thread safety as a TODO; refcounts are plain, non-atomic
- Read-only scanning/viewing of existing memory - std::string_view beats buffet's view construction by \~10x (0.609 vs 6.36 ns) in the repo's own bench
- Plain memcopy of buffers 32 bytes and up - raw C malloc+memcpy beats buffet at every size from 32 to 8192 bytes in the bench; buffet only wins at 8 bytes
- Anything needing C++ ergonomics (operators, RAII) or long-term maintenance guarantees - C API only, manual bft_free, no commits since Nov 2023, and the author calls the lib 'not much optimized' and the bench 'maybe amateurish'

## How it is fast

Small strings (&lt;=21 bytes on 64-bit) live inline in the union, avoiding heap allocation and the pointer chase std::string sometimes needs. Substring 'views' (VUE/SSV/OWN-shared tags) alias the original data with a bumped refcount instead of copying, so split() returns a list of views rather than N allocated+copied strings, and join() writes them into one new store instead of many intermediate concatenations - this is what drives the SPLITJOIN number down. Appends resize via the same tagged-union/store machinery with -O2 codegen, giving a modest edge over std::string's growth strategy at some size pairs.

## Compared with alternatives

Pick buffet over the C++-only siblings (FastString, fstring, Str, zuu_string_view, jank persistent_string, to_static_string) specifically when the codebase is plain C and needs reference-counted no-copy slicing for split/join-heavy string work; none of the other catalogued entries offer a C API. For pure view/scan-heavy work or C++ projects, prefer std::string_view or zuu_string_view instead, since buffet's own bench shows it losing to string_view by \~10x on plain views.

## Integration

| | |
|---|---|
| **Form** | static lib (source-drop friendly: single buffet.c/buffet.h pair, `make` builds bin/libbuffet.a) |
| **Dependencies** | none for the library; Google Benchmark (libbenchmark-dev) only to build the optional bench target |
| **Minimum toolchain** | C11 for the library (gcc -std=c11); usable from C++ via the built-in extern "C" guard. Building the bundled benchmark harness needs C++20 (g++ -std=c++2a -fpermissive) |
| **Platforms** | not explicitly documented; the tagged-union layout is asserted at compile time for 64-bit size_t/pointers, and the README's own TODO list includes '"test 32-bit and small RAM"', i.e. 32-bit is unverified |
| **Thread safety** | not thread-safe. README lists "Todo: thread safety" up front; refcounts on SSO/store headers are plain integers, not atomics. Repo has an unbuilt-by-default src/threadtest.c |
| **Drop-in for the baseline** | false - C function-call API (bft_\*), not operator-overloaded, requires explicit bft_free; no RAII or STL-container compatibility |

## Gotchas

- Never alias a Buffet with plain `=`; refcounts get corrupted. Use bft_dup() instead - README calls this out explicitly.
- Appending to an SSO Buffet that has live views can fail (returns 0) rather than growing, because growth would invalidate the views; release views first.
- Freeing the last view of a shared OWN store frees the underlying memory - any remaining un-bft_dup'd alias becomes a dangling pointer (README's own Security section shows this failure case).
- MEMCHECK/DEBUG guards that catch aliasing/double-free bugs are opt-in (`MEMCHECK=1 make` / `DEBUG=1 make`), not default.

## Caveats and trade-offs

Author explicitly states "the lib is not much optimized and the bench maybe amateurish"; CPU model not stated ("weak Core i3"); only libstdc++ (via g++) exercised; the headline SPLITJOIN 'C++' baseline is a hand-written std::string_view split + malloc join, not std::string; against std::string proper (APPEND) the win is \~1.2-1.7x at some sizes and a loss at 8/4; std::string_view wins MEMVIEW by \~10x.

C API only (no operator overloading); uses reference-counted 'views' that can alias/share a buffer, adding lifetime caveats; GPL-3.0 license restricts embedding in proprietary code; results are workload-dependent (helps bulk split/join, hurts plain memory-view access).

## Maintenance

Stale: no commits since 2023-11-16 and the author's own README calls the library 'not much optimized' and the bench 'maybe amateurish'. Small enough to vendor as a single .c/.h pair, but GPL-3.0 blocks embedding in proprietary code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Bench section shows first-party Google Benchmark numbers from src/bench.cpp, built with g++ -std=c++2a -fpermissive -g -O2 per the Makefile, but the hardware is only "a weak Core i3" with no CPU model. That rules out A, so it stays C.
- **Verifier notes:** The numbers match the README exactly. The 'faster than std::string' framing for split/join is a mislabel, because that benchmark uses std::string_view. The legitimate std::string win is the APPEND benchmark (up to \~1.7x). The default branch is main, and the old master raw URL still redirects.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/alcover/buffet/master/README.md>
  - <https://raw.githubusercontent.com/alcover/buffet/main/README.md>
  - <https://github.com/alcover/buffet>
  - <https://github.com/alcover/buffet/blob/main/Makefile>
  - <https://github.com/alcover/buffet/blob/main/src/bench.cpp>
  - <https://github.com/alcover/buffet/blob/main/src/utilcpp.cpp>
- **Sources the enricher read:**
  - <https://github.com/alcover/buffet>
  - <https://github.com/alcover/buffet/blob/main/README.md>
  - <https://github.com/alcover/buffet/blob/main/Makefile>
  - <https://github.com/alcover/buffet/blob/main/src/buffet.h>
  - <https://github.com/alcover/buffet/blob/main/src/bench.cpp>
  - https://github.com/alcover/buffet (repo metadata: license, archived status, pushed_at, open issues via gh api)
  - https://github.com/alcover/buffet/issues (gh search issues, 2 closed, unrelated to performance/bugs)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/alcover/buffet`) · [data/wave1/enrich/raw/github_com_alcover_buffet.json](../../../data/wave1/enrich/raw/github_com_alcover_buffet.json) (enrichment confidence 0.55)

</details>
