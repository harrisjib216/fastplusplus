# plf::bitset (plf_bitsets)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Bitsets and succinct bit vectors](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C++` · `Computing For Good License v1.01 (non-OSI; zlib-style terms plus ethical field-of-use restrictions 4a-4e)` · 🟢 active

> Header-only bitset beating std::bitset at ranged set/reset, shifts, and bit search, minus from-string constructors.

| | |
|---|---|
| **Beats** | std::bitset |
| **Claimed result** | Release (O2, AVX2): 24% (GCC)/20% (MSVC) faster overall test suite; 34,652%/67,612% faster set_range/reset_range; \~101%/98% faster left/right shift (GCC), 35%/22% (MSVC); 6%/204% faster set(pos,val); 3%/0% faster operator[]. Debug builds show much larger gaps (up to 428,127%/750,726% for set_range/reset_range). |
| **Workload** | Full bitset test-suite exercised in a loop (set/reset/shift/index/etc.); separately, set_range/reset_range on a 128000-bit bitset over 10000 randomly chosen ranges per run. |
| **Metric** | throughput |
| **Hardware** | Intel i7-9750H, Windows 10 (safe mode) |
| **Compiler and flags** | GCC 13.2 (nuwen mingw) and MSVC 2022; release build: O2, AVX2, C++23 |
| **Adoption** | 14 stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/mattreecebentley/plf_bitsets) · [benchmark](https://plflib.org/bitsets.htm) |

## Verdict

First-party benchmark (plflib.org/bitsets.htm, author's own numbers, methodology and code published) on an Intel i7-9750H under Windows 10, GCC 13.2 (libstdc++) and MSVC 2022 (MSVC STL), O2/AVX2/C++23 release build: plf::bitset beat std::bitset by 24%/20% overall on a full-operation test-suite loop, \~101%/98% (GCC) and 35%/22% (MSVC) on left/right shift, and 34,652%/67,612% on set_range/reset_range across 10,000 random ranges of a 128,000-bit bitset - the last figure mostly reflects that std::bitset has no bulk range-set primitive at all rather than a raw constant-factor win.

## Use it when

- Fixed-size bit flags where you already use std::bitset and don't rely on its from-string constructor
- Workloads that set/clear/query contiguous ranges of bits (set_range/reset_range) instead of single bits in a loop
- Need a runtime-sized or user-buffer-backed bitset (plf::bitsetb) - e.g. per-instance variable size, or placement over pre-allocated/arena memory
- GCC or MSVC targets on x86-64, where the author's release numbers were actually measured (i7-9750H, O2/AVX2, C++23)
- Want first/last-one/zero search or an allocation-free swap that std::bitset doesn't offer

## Skip it when

- Code that constructs std::bitset from a string or unsigned long/long long - those constructors aren't implemented here
- Organizations that require an OSI-approved license - Computing For Good v1.01 is zlib-like but adds ethical-use restrictions (4a-4e) and is not OSI-approved
- Clang/libc++ targets - the author states libc++ was not tested or benchmarked
- Projects that need independently-reproduced numbers - all benchmark results are first-party (author's own page and repo), with 14 stars and no third-party reproduction found
- Code paths hitting the four currently-open correctness issues (overflow-bit restoration, not-found sentinels - see gotchas) until they're resolved

## How it is fast

Same word-array layout as std::bitset (array of storage_type words), but set_range/reset_range write whole words with masks instead of looping bit-by-bit like std::bitset callers have to (std::bitset has no bulk range primitive at all, which is why that number is \~340x-676x rather than a small constant factor). Bit search (first/next/prev one or zero) uses compiler builtins directly (__builtin_ctz/_BitScanForward64, or std::countr_zero/std::popcount under C++20's &lt;bit&gt;) instead of a generic scan loop. No SIMD/AVX intrinsics are used in the header itself despite the AVX2 benchmark flag - the \~20-24% overall test-suite gain comes from tighter, more branch-light word-level code (e.g. compile-time-eliminated overflow-bit handling, template-gated bounds checks) rather than a different algorithm.

## Compared with alternatives

Pick plf::bitset over CRoaring, pasta::bit_vector, better_bitset, BitLib, and sul::dynamic_bitset when you specifically want std::bitset's fixed-size, non-succinct, no-rank/select shape (not a compressed/sparse structure like CRoaring, not a rank/select index like pasta::bit_vector) but need faster ranged set/reset or shifts than std::bitset provides; use plf::bitsetb instead of BitLib or sul::dynamic_bitset when you want that same std::bitset-shaped API with a runtime-determined size or a user-supplied buffer rather than a vector&lt;bool&gt;-style resizable container.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library (&lt;cmath&gt; &lt;cassert&gt; &lt;string&gt; &lt;stdexcept&gt; &lt;limits&gt; &lt;ostream&gt; &lt;cstring&gt; &lt;algorithm&gt;; &lt;bit&gt; under C++20; bitsetb also uses &lt;memory&gt; for allocator_type support) |
| **Minimum toolchain** | C++11 minimum via feature-detection macros in plf_tools.h (supports back to MSVC 2015 / GCC 4-era compilers with reduced feature use); takes advantage of constexpr/consteval, if-constexpr, and &lt;bit&gt; under C++20/23 when the compiler and standard library support them. Author's benchmark used GCC 13.2 and MSVC 2022 with C++23. |
| **Platforms** | portable C++ - no architecture-specific intrinsics in the header (relies on portable __builtin_ctz/_BitScanForward64/std::countr_zero paths per compiler). AVX2 in the benchmark build is a codegen flag only, not a hard requirement. |
| **Thread safety** | not documented - no mention in the README or headers; assume the same as std::bitset (no internal synchronization, concurrent writes to one instance are unsafe) |
| **Drop-in for the baseline** | partial — explain: same core operation set and semantics as std::bitset (test/set/reset/flip/any/all/none/count/operator[]/to_string/to_ulong), but the from-string and from-ulong/ullong constructors are missing, and the template signature adds a storage_type and a hardened (bounds-checking) parameter not present on std::bitset. |

## Gotchas

- Four issues are open on the repo (#3, #4, #5 filed against overflow-bit restoration in set_overflow_to_one, all_range's empty-range path, and next/prev_zero's not-found path; #6 requests a proper not-found sentinel for the search functions) - check these before relying on exact behavior at bitset-size edges
- from-string / from-ulong / from-ullong constructors aren't implemented - existing std::bitset(str) call sites need to be rewritten, not just retyped
- The third template parameter (hardened, default false) controls bounds checking; with it left at default, operator[] is unchecked like std::bitset's, while test() still throws - read the header if you rely on a specific check point
- License is Computing For Good v1.01, not a standard permissive license - clauses 4a-4e restrict use by field/purpose, which needs a legal read some organizations won't accept

## Caveats and trade-offs

First-party benchmark (the author's own numbers), not independently reproduced, but methodology (compiler, flags, hardware) and full benchmark source are published. The extreme set_range/reset_range percentages (up to \~677x) mostly reflect that std::bitset has no ranged-set primitive (callers loop bit-by-bit), so they are partly an algorithmic win rather than a raw constant-factor speedup; the overall test-suite numbers (\~20-24%) better represent general use. Not every operation wins: MSVC's std::bitset to_string (which uses an intrinsic) beats plf, and the author says other operations perform about the same. Licensed under 'Computing For Good License v1.01' (zlib-like with ethical-use restrictions 4a-4e, not OSI-approved), so usability is 'reference'.

plf::bitset omits std::bitset's from-string/from-ulong constructors; adds set_range/reset_range, range-based any/all/none/count, an allocation-free XOR swap, index-bounds-checking via a template flag, and a user-supplied-buffer variant (plf::bitsetb) not present in std::bitset.

## Maintenance

Actively maintained (last commit 2026-09-19, four open bug-tracking issues under active triage); usability is marked 'reference' rather than drop-in because the non-OSI Computing For Good v1.01 license's ethical-use clauses (4a-4e) call for a legal review before production adoption at most companies.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** plflib.org/bitsets.htm benchmarks plf::bitset against std::bitset under GCC 13.2 (nuwen mingw, libstdc++) and MSVC 2022 (MSVC STL), O2/AVX2/C++23 release, on an Intel i7-9750H. The benchmark code is public (plflib.org/plf_bitset_benchmarks_15-02-2025.zip, also in the repo root).
- **Verifier notes:** Every release and debug percentage in claimed_speedup matches the page (the page's summary lists left/right shift as 101%/35% and 98%/22% for GCC/MSVC; its body text says +35%/20% for MSVC, a small inconsistency on the page itself). The author states libc++ was not tested. Stars (14), last commit (2026-09-19) and non-fork status confirmed; the license field is filled from the LICENSE file (spdx=NOASSERTION).
- **Fields the verifier corrected:** `license`, `caveats`
- **Pages the verifier opened:**
  - <https://plflib.org/bitsets.htm>
  - <https://github.com/mattreecebentley/plf_bitsets>
- **Sources the enricher read:**
  - <https://github.com/mattreecebentley/plf_bitsets>
  - <https://github.com/mattreecebentley/plf_bitsets/blob/main/README.md>
  - <https://github.com/mattreecebentley/plf_bitsets/blob/main/plf_bitset.h>
  - <https://github.com/mattreecebentley/plf_bitsets/blob/main/plf_bitsetb.h>
  - <https://github.com/mattreecebentley/plf_bitsets/blob/main/plf_tools.h>
  - <https://github.com/mattreecebentley/plf_bitsets/blob/main/LICENSE>
  - <https://github.com/mattreecebentley/plf_bitsets/issues>
  - <https://plflib.org/bitsets.htm>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mattreecebentley/plf_bitsets`) · [data/wave1/enrich/raw/github_com_mattreecebentley_plf_bitsets.json](../../../data/wave1/enrich/raw/github_com_mattreecebentley_plf_bitsets.json) (enrichment confidence 0.85)

</details>
