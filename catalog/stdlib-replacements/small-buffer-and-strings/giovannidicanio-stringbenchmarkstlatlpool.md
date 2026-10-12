# Pool-allocator string (Dicanio STL/ATL/Pool string benchmark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Fixed-chunk pool allocator for bulk wide-char strings, beating ATL CStringW and std::wstring on creation.

| | |
|---|---|
| **Beats** | std::string |
| **Claimed result** | Vector creation/fill sample run: ATL CStringW 954 ms, STL std::wstring 866 ms, pool-allocated strings 506 ms. The author calls this "about 47% faster than ATL's CString, and about 42% faster than STL's wstring" (\~1.7x vs std::wstring, derived from page data). Sorting: "STL and the custom pool strings perform very similarly". Tiny-string variant (TEST_TINY_STRINGS, SSO): "STL strings win by an important margin in both creation and sorting times". |
| **Workload** | Building a std::vector of many small wide-character strings via push_back and then sorting it, comparing std::wstring (MSVC STL), ATL CStringW, and strings allocated from a custom fixed-chunk pool allocator. |
| **Metric** | latency |
| **Hardware** | Windows 10 64-bit, Intel i7 (exact model/generation not stated) |
| **Compiler and flags** | Visual Studio 2019, 64-bit Release build |
| **Adoption** | 1 star |
| **Last commit** | 2023-12-01 |
| **Links** | [repository](https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool) · [benchmark](https://giodicanio.com/2023/12/01/c-plus-plus-string-benchmark-stl-vs-atl-vs-custom-pool-allocator/) |

## Verdict

On Windows 10 64-bit with VS2019 64-bit Release on an unspecified Intel i7, one sample run building a vector of \~3.2M shuffled std::wstring-length strings via push_back took 954ms for ATL CStringW, 866ms for MSVC STL std::wstring, and 506ms for the pool allocator (\~1.7x vs std::wstring, \~1.9x vs ATL); the subsequent sort was a near-tie between STL and pool, and a separate SSO/tiny-string run reversed the result, with STL winning both phases.

## Use it when

- Bulk-building a read-only collection of many small-to-medium wide strings in one pass (e.g. load, sort, discard) where the whole set is freed together
- Windows/MSVC codebases already comfortable linking Win32 (VirtualAlloc) or ATL
- Strings long enough to defeat std::wstring's SSO, so real heap allocation cost is being paid per element
- One-shot latency-sensitive construction of a vector of strings, not incremental mutation or long-lived per-string ownership
- Prototyping/benchmarking the pooling technique itself rather than needing a finished library

## Skip it when

- Tiny strings that fit std::wstring's SSO buffer: the author's own TEST_TINY_STRINGS run shows plain STL wins creation and sorting by 'an important margin'
- Sort/comparison-heavy workloads: the benchmark shows STL and pool strings 'perform very similarly' once sorting starts
- Any case needing to free or reuse a single string's memory before the whole pool is destroyed
- Non-Windows or non-wide-char code: implementation is Win32 VirtualAlloc/WCHAR only, not templated for char or portable
- Production dependencies: this is a demo class in a one-off benchmark repo (1 star, no tests/CI), not a maintained, packaged library

## How it is fast

Uses bump-pointer allocation within large chunks reserved via VirtualAlloc (default 512KB, rounded to system allocation granularity), so most string allocations are just a pointer increment instead of a heap call, and a new chunk is requested only when the current one fills up. This amortizes many small OS/heap allocations into a few large ones, based on the technique from the 'Old New Thing' blog post on dictionary-loading allocation patterns. It also sidesteps ATL CStringW's copy-on-write reference counting (_InterlockedIncrement/_InterlockedDecrement), which the author identifies as ATL's main slowdown.

## Compared with alternatives

Only for the specific pattern of bulk-creating many medium/long, read-only wide strings that are discarded together on Windows/MSVC — none of the catalogued siblings (to_static_string, buffet, FastString, fstring, Str, zuu_string_view, jank persistent_string) target this pool-and-discard arena shape; all of them are more general-purpose, portable, and actually packaged/usable as libraries, so prefer them for anything beyond this narrow demo.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Windows.h (VirtualAlloc/VirtualFree), crtdbg.h (_ASSERTE); the benchmark harness additionally links ATL (atlstr.h) but CStringPoolAllocator itself needs only Windows.h |
| **Minimum toolchain** | not documented precisely; built and measured with Visual Studio 2019, 64-bit Release (no explicit /std flag visible in the .vcxproj) |
| **Platforms** | Windows x86/x64 only (VirtualAlloc-based), MSVC toolchain |
| **Thread safety** | not documented; AllocString has no locking, so a CStringPoolAllocator instance is not safe for concurrent use without external synchronization |
| **Drop-in for the baseline** | partial — explain: AllocString takes a char range or NUL-terminated source and returns a raw PWSTR, not an object with std::wstring's API (no operator+, resize, iterators, or RAII per-string lifetime); call sites must be rewritten around vector&lt;const wchar_t\*&gt; and the shared pool's lifetime. |

## Gotchas

- No per-string free: individual allocations live until the whole CStringPoolAllocator is destroyed and all its chunks VirtualFree'd at once
- AllocString throws std::bad_alloc if VirtualAlloc fails or if a string exceeds kchMaxCharAlloc (1,048,576 WCHARs, \~2MB)
- Default minimum chunk size is 512KB; many short-lived or small allocators will over-reserve memory relative to std::wstring's SSO
- The destructor's chunk-walking logic explicitly fixes a leak/wrong-size bug present in the original 'Old New Thing' blog code that this class is based on (documented in comments)

## Caveats and trade-offs

First-party single sample run with no variance data; CPU is only "Intel i7"; only MSVC STL (VS2019) tested; the win is creation-only, sorting is a tie, and with short strings (SSO) std::wstring wins clearly on both creation and sorting; the pool string is a demo type in a benchmark repo, not a packaged library; baseline is std::wstring (wide chars).

The pool-allocated strings depend on a pre-allocated fixed-size chunk arena rather than being a drop-in std::string replacement, and require managing pool lifetime; the author notes plain STL SSO already wins for tiny strings, so the advantage is specific to bulk creation of many small/medium heap-backed strings.

## Maintenance

Stale since December 2023 (1 star, no CI/tests, last commit 2023-12-01) but MIT-licensed and small enough (one header) to vendor as a reference implementation of the pooling technique rather than as a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The blog post shows first-party sample-run numbers (ATL 954 ms, STL 866 ms, Pool 506 ms). The code is public (StringBenchmark/StringBenchmark.cpp, StringPool.h) and it was built with VS2019 in a 64-bit Release build. The CPU is only "Intel i7" and the exact flags are not stated, so it is not A.
- **Verifier notes:** The numbers match the post. The record left out that STL wins the tiny-string/SSO variant and ties on sorting, so I added both to claimed_speedup and caveats. last_commit corrected to 2023-12-01 (the default-branch commit date; 2023-12-04 was only pushed_at).
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://giodicanio.com/2023/12/01/c-plus-plus-string-benchmark-stl-vs-atl-vs-custom-pool-allocator/>
  - <https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool>
  - <https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool/tree/main/StringBenchmark/StringBenchmark>
- **Sources the enricher read:**
  - <https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool>
  - https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool (readme via gh api)
  - https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool (tree via gh api)
  - <https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool/blob/main/StringBenchmark/StringBenchmark/StringPool.h>
  - <https://github.com/GiovanniDicanio/StringBenchmarkStlAtlPool/blob/main/StringBenchmark/StringBenchmark/StringBenchmark.cpp>
  - <https://giodicanio.com/2023/12/01/c-plus-plus-string-benchmark-stl-vs-atl-vs-custom-pool-allocator/>
  - https://api.github.com/repos/GiovanniDicanio/StringBenchmarkStlAtlPool (repo metadata via gh api)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/giovannidicanio/stringbenchmarkstlatlpool`) · [data/wave1/enrich/raw/github_com_giovannidicanio_stringbenchmarkstlatlpool.json](../../../data/wave1/enrich/raw/github_com_giovannidicanio_stringbenchmarkstlatlpool.json) (enrichment confidence 0.5)

</details>
