# Loki flex_string

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `MIT for the Loki library (SourceForge listing; headers such as SmallObj.h carry the MIT text); the flex_string headers carry Andrei Alexandrescu's 2001 HPND-style permission notice; the GitHub mirror has no LICENSE file. Boost.Wave ships a BSL-1.0 copy (boost/wave/util/flex_string.hpp)` · 🔴 abandoned

> Alexandrescu's 2001 policy-based std::basic_string clone; only evidence is an anecdotal 5-10% Boost.Wave speedup.

| | |
|---|---|
| **Beats** | std::string (std::basic_string) of an unstated standard library, inside Boost.Wave |
| **Claimed result** | 5-10% faster (Boost.Wave with flex_string dropped in, per doc/flex/flex_string.html; the same page states 'no performance comparison suite is available at this time') |
| **Workload** | Boost.Wave (the Boost preprocessor library) with std::string replaced by flex_string, as reported to the author by Hartmut Kaizer; input unspecified ('depending on input'). |
| **Metric** | throughput |
| **Adoption** | 251 stars, 72 forks (GitHub mirror); SourceForge Loki 4.4/5 across 7 reviews; a modified flex_string copy ships in Boost.Wave as boost/wave/util/flex_string.hpp |
| **Last commit** | 2013-08-06 |
| **Links** | [repository](https://github.com/snaewe/loki-lib) · [benchmark](https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/doc/flex/flex_string.html) |

## Verdict

The only number is second-hand: Hartmut Kaiser told the author that dropping flex_string (in Boost.Wave's default copy-on-write configuration) into the Boost.Wave preprocessor made it 5-10% faster depending on input, against an unstated 2001-2005 era std::string, with no compiler, hardware or benchmark code; the doc page itself says no performance comparison suite exists, and the repo's test/flex_string/main.cpp is a randomized correctness comparison against std::string with no timing.

## Use it when

- Maintaining legacy C++03 code (or Boost.Wave-era code) that already uses flex_string and you need to understand or tune its storage policy.
- Copy-heavy, single-threaded workloads such as token or symbol strings that are copied far more often than mutated, where a COW policy saves allocations.
- Studying or teaching policy-based design: each storage policy is a few hundred lines and the interface contract is documented at the top of every policy header.
- Experiments that need a custom string layout (arena-backed, fixed-size SSO threshold, malloc/realloc growth) without writing the full basic_string surface yourself.

## Skip it when

- Any new C++11-or-later code: flex_string has no move constructor or move assignment, so std::move, vector&lt;flex_string&gt; reallocation and swaps through generic code fall back to deep copies (or refcount traffic) where std::string moves in O(1).
- C++20 builds with std::allocator: the Loki copy reads A::reference, A::pointer, A::const_pointer and calls A::allocate(n, hint), all removed in C++20; Boost.Wave had to patch exactly this (boostorg/wave PR #72, 2020) and the Loki mirror has not changed since 2013.
- Strings shared across threads with CowStringOpt: the reference count is a plain unsigned char/short in the buffer, incremented and decremented without atomics, so concurrent copies of one string are a data race.
- Workloads built from many small appends (s += "ab" in a loop): Storage::append reserves exactly size()+n, so with the default AllocatorStringStorage every append that overflows reallocates and copies the whole string (quadratic); only push_back doubles capacity.
- Search-heavy code: find(const char\*, pos, n) calls traits::compare at every position and find(char) is implemented as a 1-character compare per position, with no memchr first-character skip as in libstdc++.

## How it is fast

There is no single algorithmic trick: the speed argument is that you pick the storage layout per workload. SimpleStringStorage grows with realloc (can extend in place, which std::allocator cannot), SmallStringOpt avoids heap allocation for short strings, and CowStringOpt makes copies O(1) by sharing a buffer whose reference count is stored in the buffer's first character. Character moves use memcpy/memmove and fills use a Duff's-device loop (flex_string_details.h). Boost.Wave's reported gain came from its default CowString&lt;AllocatorStringStorage&lt;char&gt;&gt; configuration, i.e. cheap copies of token strings.

## Compared with alternatives

Pick it only when you specifically want a C++03 policy-based string (COW, realloc growth or tunable SSO behind one interface); FastString and MengRao/str have measured wins over a modern std::string with numbers you can reproduce, and buffet or to_static_string cover the narrower append and number-formatting cases.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (the rest of Loki needs src/\*.cpp for SmallObj, Singleton and OrderedStatic, but flex_string does not) |
| **Minimum toolchain** | C++03; README lists GCC 3.4-4.1 and MSVC 7.1/8.0; the Loki copy does not compile as C++20 with std::allocator (removed allocator members) |
| **Platforms** | any (portable C++, no intrinsics) |
| **Thread safety** | Not documented. Separate strings are independent; CowStringOpt shares buffers with a non-atomic in-buffer reference count, and c_str() (a const member) writes the terminating zero into the buffer, so concurrent const access is formally a data race. |
| **Drop-in for the baseline** | partial — C++03 std::basic_string interface only: no move semantics, none of the C++11 members (pop_back, front, back, shrink_to_fit), data() is not guaranteed null-terminated (only c_str() writes the terminator), and const at(n) accepts n == size() instead of throwing. |

## Gotchas

- CowStringOpt keeps the reference count in the first element of the buffer, typed as the unsigned variant of the character type (unsigned char for char), so after 255 sharers a copy silently becomes a deep copy; the count is not atomic.
- data() returns the buffer without writing a terminator; only c_str() writes E() at pEnd_, so passing data() to C APIs reads whatever byte follows the string.
- AllocatorStringStorage computes its allocation in bytes and passes byte counts to A::allocate(1 + (sz-1)/sizeof(E)) but A::deallocate(p, bytes), which mismatches for wchar_t under sized deallocation; Boost.Wave also hit gcc 11 -Wfree-nonheap-object warnings on the shared emptyString_ sentinel (boostorg/wave issue #159).
- The SmallStringOpt threshold is capped at 126 characters by a compile-time check, and its size/flag byte lives in the last buffer slot, so sizeof(flex_string) grows with the threshold.

## Known shortcomings

- Only evidence is a second-hand 5-10% gain of flex_string in Boost.Wave against std::string with no methodology; pre-SSO era anecdote, abandoned 2013, mixed licence (Boost.Wave still ships a BSL-1.0 copy with later bug fixes).
- Enricher: the Boost.Wave 5-10% gain came from Wave's COW configuration (CowString&lt;AllocatorStringStorage&gt;); test/flex_string/main.cpp checks correctness only, no timing. No move semantics; the Loki copy fails C++20 with std::allocator (Wave patched this in PR #72); the COW refcount is a non-atomic unsigned char (deep copy after 255 sharers); Storage::append reserves the exact size so repeated += is quadratic; naive find without memchr; data() not null-terminated; const at(size()) does not throw.

## Caveats and trade-offs

Anecdotal, second-hand number with no methodology, hardware, compiler or standard-library version, from the pre-C++11 era (CUJ articles 2001 and 2005); the page misspells the reporter as 'Harmut Kaizer' (Hartmut Kaiser, Boost.Wave's author) and its first paragraph describes SafeFormat ('Type-Safe Formatting', CUJ July 2005, a printf emulation), apparently a copy-paste error. Boost.Wave adopted flex_string as boost/wave/util/flex_string.hpp under BSL-1.0, and its change log records correctness fixes on top of Alexandrescu's code (#HK030306 'Fixed a string terminating bug in append'), so the 5-10% may predate fixes; modern std::string implementations with SSO (libstdc++ since GCC 5, libc++, MSVC STL) differ from the 2001-era baselines. The project's other components have benchmark code but no published results: test/SmallObj/SmallObjBench.cpp compares Loki::SmallObject with new/delete, malloc and std::allocator (and optionally Boost.Pool) but results must be run locally, and a web snippet reports Loki::AssocVector slower than std::map on insert and lookup in a third-party run. Licence mixed: SourceForge lists MIT and SmallObj.h states MIT, but flex_string.h still carries the older Alexandrescu permission notice (HPND-style, not a verbatim SPDX licence). Last GitHub commit 2013-08-06 ('Improved SmartAssert component.'); SourceForge status Beta, last update 2013-08-06; README targets GCC 3.4-4.1 and MSVC 7.1/8.0.

Policy-based basic_string (storage policies: simple, allocator, vector, small-string optimisation, copy-on-write) that is a drop-in std::string replacement; storage policy choice (for example copy-on-write) changes thread-safety and iterator-invalidation behaviour relative to std::string. Loki code targets compilers of 2005 to 2013 (Gcc 3.4 to 4.1, MSVC 7.1 and 8.0 listed in README).

## Maintenance

Abandoned since 2013 (last mirror commit 2013-08-06, README last updated 2005, one open unrelated issue); permissively licensed (Alexandrescu notice, Loki MIT, BSL-1.0 copy in Boost.Wave) and small enough to vendor, but the maintained copy is Boost.Wave's boost/wave/util/flex_string.hpp, which carries C++20 and warning fixes the Loki mirror lacks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number is a second-hand 5-10% speedup of Boost.Wave after dropping in flex_string for std::string, reported to the author and quoted in doc/flex/flex_string.html with no methodology, input, compiler or hardware; the page itself says no performance comparison suite is available.
- **Verifier notes:** The 5-10% figure is on the page as stated; it is second-hand with no methodology, so C stays (arguably the weakest C). Metadata checks out (251 stars, no LICENSE in mirror, SourceForge MIT 4.4/5 7 reviews, last update 2013-08-06, abandoned). New fact: Boost.Wave still ships a BSL-1.0 flex_string copy with later correctness fixes; shortcomings to record: anecdotal second-hand claim, pre-SSO-era baseline, abandoned since 2013, mixed licence.
- **Fields the verifier corrected:** `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 11); enricher w11 pair-030
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/doc/flex/flex_string.html>
  - <https://github.com/snaewe/loki-lib>
  - <https://github.com/snaewe/loki-lib/commits>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/flex_string.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/flex_string_shell.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/SmallObj.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/README>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/test/SmallObj/SmallObjBench.cpp>
  - <https://raw.githubusercontent.com/boostorg/wave/HEAD/include/boost/wave/util/flex_string.hpp>
  - <https://sourceforge.net/projects/loki-lib/>
- **Sources the enricher read:**
  - <https://github.com/snaewe/loki-lib>
  - <https://github.com/snaewe/loki-lib/issues?q=is%3Aissue>
  - <https://github.com/snaewe/loki-lib/tree/master/test/flex_string>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/doc/flex/flex_string.html>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/README>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/flex_string.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/flex_string_shell.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/flex_string_details.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/simplestringstorage.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/allocatorstringstorage.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/vectorstringstorage.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/smallstringopt.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/include/loki/flex/cowstringopt.h>
  - <https://raw.githubusercontent.com/snaewe/loki-lib/HEAD/test/flex_string/main.cpp>
  - <https://raw.githubusercontent.com/boostorg/wave/HEAD/include/boost/wave/util/flex_string.hpp>
  - <https://raw.githubusercontent.com/boostorg/wave/HEAD/include/boost/wave/wave_config.hpp>
  - <https://github.com/boostorg/wave/issues?q=flex_string>
  - <https://github.com/boostorg/wave/pull/72>
  - <https://github.com/boostorg/wave/pull/46>
  - <https://github.com/boostorg/wave/issues/159>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/snaewe/loki-lib`) · [data/wave11/enrich/raw/github_com_snaewe_loki_lib.json](../../../data/wave11/enrich/raw/github_com_snaewe_loki_lib.json) (enrichment confidence 0.75)

</details>
