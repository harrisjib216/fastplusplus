# StringZilla

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only SIMD string kernels (search, hashing, sort, UTF-8) beating std::string::find and find_first_of.

| | |
|---|---|
| **Beats** | std::string::find |
| **Claimed result** | Find first \~5-byte random word: STL std::string::find 9.1 GB/s vs StringZilla sz_find 21.0 GB/s on Xeon4 (\~2.3x, derived from page data) and 10.9 vs 37.1 GB/s on M5 Pro (\~3.4x, derived from page data); glibc strstr 21.3 GB/s on Xeon4 matches sz_find (3.5 GB/s on M5 Pro). Split lines on \n/\r: STL std::string::find_first_of 1.1 vs sz_find_byteset 13.8 GB/s on Xeon4 (\~12.5x, derived from page data) and 4.1 vs 23.7 GB/s on M5 Pro (\~5.8x, derived from page data); libc strcspn 9.2 / 3.8 GB/s (numbers verbatim from README Performance table) |
| **Workload** | Find the first occurrence of a random \~5-byte word in text, measured as throughput (GB/s) on an Intel Xeon4 (Sapphire Rapids, GCC+glibc) and an Apple M5 Pro (Apple Clang+libc++). |
| **Metric** | throughput |
| **Hardware** | Intel Sapphire Rapids ('Xeon4', exact SKU not given); Apple M5 Pro (18-core) |
| **Compiler and flags** | GCC with glibc on Xeon4; Apple clang with libc++ on M5 Pro. Compiler versions and optimization flags for the published numbers are not stated (CONTRIBUTING.md only gives generic CMake Release build instructions). |
| **Adoption** | 3,563 stars |
| **Last commit** | 2026-08-12 |
| **Links** | [repository](https://github.com/ashvardanian/StringZilla) · [benchmark](https://github.com/ashvardanian/StringZilla/blob/main/README.md) |

## Verdict

README Performance table: finding the first occurrence of a \~5-byte random word, std::string::find (STL, GCC+glibc) hit 9.1 GB/s vs sz_find 21.0 GB/s (\~2.3x) on an Intel Sapphire Rapids Xeon4, and 10.9 vs 37.1 GB/s (\~3.4x) on Apple M5 Pro (Apple Clang+libc++). Splitting lines on \n/\r, std::string::find_first_of hit 1.1 GB/s vs sz_find_byteset 13.8 GB/s on Xeon4, and 4.1 vs 23.7 GB/s on M5 Pro.

## Use it when

- Hot substring search over large text buffers where std::string::find shows up in a profile
- Splitting/tokenizing on multiple delimiter bytes (replacing find_first_of/strcspn) via sz_find_byteset
- Multi-language pipelines that need identical search/hash/sort kernels across C/C++/Python/Rust/Go/Swift/JS/C#/Java
- Unicode case-folding, segmentation, or normalization at C speed instead of ICU/ICU4X
- Apple Silicon or ARM server targets, where the README reports the widest gap over the system libc strstr

## Skip it when

- Multi-pattern literal matching: no Aho-Corasick automaton is shipped; README points to hyperscan or pyahocorasick instead
- Need a std::hash-compatible hasher: sz's hash is a separate AES-based non-standard function, not a std::hash specialization
- Building for i386 — currently broken (open issue #341)
- Need find_all() match offsets relative to the parent string — reported broken in open issue #278
- Very short, early-diverging comparisons (equality/order checks) — README itself says vectorization is 'almost useless' there
- Risk-averse adoption of sz::argsort right now — open crash report (#337) and an open UBSAN misaligned-write report (#279)

## How it is fast

Per-ISA SIMD kernels (SSE4.2/AVX2/AVX-512 on x86, NEON/SVE/SVE2 on ARM, plus WASM SIMD128, RISC-V RVV, PowerPC VSX, LoongArch) selected at compile time or via a runtime dispatch table in the optional shared build. Needle-length-adaptive algorithm choice: brute-force SIMD comparisons at multiple needle offsets for short needles, Boyer-Moore-Horspool with a bad-character shift table and Raita-style character-anomaly detection for mid/long needles, and SWAR (64-bit word) fallback with no SIMD.

## Compared with alternatives

sse4-strstr is the closest sibling but covers only substring search as a single header with no bindings; pick StringZilla when you also need byte-set scanning, hashing, sorting, or non-C++ language bindings and can accept a larger, fast-moving dependency. Pick sse4-strstr instead when you want a small, frozen, single-purpose kernel to vendor with nothing else attached.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (freestanding build available via SZ_AVOID_LIBC=1); optional precompiled shared library for runtime dispatch |
| **Minimum toolchain** | C99 / C++11 minimum to compile; CI-validated on GCC 12+, Clang 16+, MSVC 2022, NVCC CUDA 12+ (GCC 10 and older fail STL insert conformance needed by the test suite) |
| **Platforms** | x86-64 (SSE4.2/AVX2/AVX-512 tiers), aarch64 (NEON/SVE/SVE2), WebAssembly (SIMD128 via wasm32-wasip1), RISC-V (RVV), PowerPC (VSX), LoongArch; i386 currently fails to build (issue #341) |
| **Thread safety** | not documented explicitly as a guarantee; the library keeps no global/thread-local state and every allocating function takes an explicit sz_memory_allocator_t, which implies reentrant kernels |
| **Drop-in for the baseline** | partial — explain: sz::string_view/sz::string implement the std::string_view/std::string member surface (data/size/substr/compare/iterators/operator&lt;=&gt;), so passing them around is drop-in, but calling the faster search itself means rewriting std::string::find(...) as sz::find(...)/sz_find(...) |

## Gotchas

- sz_find_byte_serial historically mis-compared bytes &gt; 0x7F when compiled with -fsigned-char (issue #306, closed/fixed) — a signed-char caution sign for anyone pinning old versions
- find_all() results reportedly cannot recover the match's position within the parent string (open issue #278)
- sz::argsort has an open crash report (#337)
- UBSAN reports a misaligned-address write in a SWAR code path (open issue #279)

## Caveats and trade-offs

First-party numbers. The README says 'Treat these as a first impression, not a benchmark suite' and 'These will not reproduce exactly'. Compiler versions and flags are not stated. glibc strstr is on par with sz_find on Xeon4, so the big wins are over std::string::find and find_first_of and over the weaker Apple libc.

Header-only C core plus C++/Python/Rust/Go/Swift/JS/C#/Java bindings; adopting it means switching from std::string::find to sz::find/sz::string (a search-and-replace, per the README's own comparison table), not a drop-in override of std::string itself; portability across NEON/AVX2/AVX-512/SVE/RVV/WASM backends adds build-system complexity; its own hash function (AES-based) is a separate, non-standard hasher, not a std::hash specialization.

## Maintenance

Actively maintained (last commit 2026-08-12, 3,563 stars, Apache-2.0); header-only core is easy to vendor ('copyable'), but several open bugs (i386 build failure, argsort crash, misaligned-write UBSAN report) mean trusting specific kernels rather than the whole surface unverified.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The README Performance table directly compares STL std::string::find and find_first_of with sz_find and sz_find_byteset, and all the quoted GB/s numbers match. Benchmark code is public (bench/find.cpp), but compiler versions and flags for the published numbers are not stated, the Xeon is given only as 'Sapphire Rapids', and the README says 'Treat these as a first impression, not a benchmark suite', so this is C.
- **Verifier notes:** The default branch (main) last had a commit on 2026-08-12. The 2026-09-22 date is pushed_at from another branch; the repo is still active. Apache-2.0, 3,563 stars. The claim now adds the std::string::find_first_of row, since std::string is the named baseline.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ashvardanian/StringZilla>
  - <https://github.com/ashvardanian/StringZilla/blob/main/bench/README.md>
  - <https://github.com/ashvardanian/StringZilla/blob/main/CONTRIBUTING.md>
- **Sources the enricher read:**
  - <https://github.com/ashvardanian/StringZilla>
  - <https://github.com/ashvardanian/StringZilla/blob/main/README.md>
  - <https://github.com/ashvardanian/StringZilla/blob/main/bench/README.md>
  - <https://github.com/ashvardanian/StringZilla/blob/main/include/stringzilla/README.md>
  - <https://github.com/ashvardanian/StringZilla/blob/main/CONTRIBUTING.md>
  - <https://github.com/ashvardanian/StringZilla/blob/main/bench/find.cpp>
  - <https://github.com/ashvardanian/StringZilla/issues?q=label%3Abug>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ashvardanian/stringzilla`) · [data/wave1/enrich/raw/github_com_ashvardanian_stringzilla.json](../../../data/wave1/enrich/raw/github_com_ashvardanian_stringzilla.json) (enrichment confidence 0.85)

</details>
