# simdsearch (Needle-Hammer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Searching](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Header-only SIMD substring search with a linear-time worst-case fallback; \~30x libc memmem on Apple M-series.

| | |
|---|---|
| **Beats** | memmem (platform libc; the headline figure is on an Apple M-series core) |
| **Claimed result** | About 45 GB/s on an Apple M-series core, roughly 30x the platform's memmem |
| **Workload** | Substring search over ordinary text at memory speed; needle-in-haystack throughput measured on an Apple M-series core |
| **Metric** | throughput |
| **Hardware** | An unspecified 'Apple M-series core' for the headline 45 GB/s/30x figure; AVX-512F+BW required on x86-64, NEON on AArch64 |
| **Compiler and flags** | GCC 14/15 or Apple clang 17 (library is C++17, benchmark driver needs C++23 for std::print); g++ -std=c++17 -O2 -mavx512f -mavx512bw on x86-64, plain -O2 on AArch64; tuning constants were fitted on Emerald Rapids, Zen 5 and Apple M4 Max |
| **Adoption** | 9 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/lemire/simdsearch) · [benchmark](https://github.com/lemire/simdsearch#readme) |

## Verdict

The README claims about 45 GB/s substring-search throughput on an unnamed Apple M-series core, roughly 30x the platform's libc memmem, measured on ordinary text at memory speed. The repo's own benchmark/README.md notes Apple's memmem 'uses a much simpler scan and lands well behind strstr,' so the 30x figure is against a weak platform baseline, and the top-level README tells readers to reproduce numbers on their own machine rather than publishing a results table for this specific claim.

## Use it when

- Substring/byte search over ordinary text or binary data on x86-64 with AVX-512F+BW, or any AArch64 core (NEON is architectural there)
- Throughput-bound scanning (log grepping, large-buffer search) rather than a single short lookup, since the design targets memory-speed scanning
- You can tolerate adversarial-input inputs falling back only to two-way's O(n+m), not needing sublinear worst-case behavior
- You can vendor a header-only, dependency-free library and compile per target machine (a checked-in single header and single-header releases exist)
- You need byte-exact, NUL-safe, non-UTF-8-aware search rather than a character-aware routine

## Skip it when

- Shipping one binary to x86-64 machines with unknown/mixed CPUs — there is no runtime dispatch; a CPU without AVX-512F+BW hits an illegal instruction
- Targeting mainstream x86-64 client parts (most Intel client chips have AVX-512 fused off, pre-Zen4 AMD lacks it) or 32-bit/RISC-V/POWER, all unsupported
- Building with MSVC — unsupported, since the headers use GCC/Clang builtins and attributes
- Needing a licensed dependency for production use — the repo ships no LICENSE file
- Wanting a published, apples-to-apples comparison against std::search or std::string::find — the benchmark driver includes both but no numbers for them are in the README

## How it is fast

Needle-Hammer picks 2-4 selective bytes from the needle as anchors and SIMD-filters 256 haystack positions per AVX-512 iteration (64 on NEON) against them, narrowing survivors byte by byte. A per-call work counter caps how much filtering it does; once the budget is spent on adversarial input it hands off to a Crochemore-Perrin two-way search, so every call stays O(n+m) instead of degrading like an unguarded anchor filter.

## Compared with alternatives

The catalogued siblings (sb_lower_bound, scandum/binary_search, SIMD Quad search, FastBinarySearch) all accelerate binary search over sorted arrays; simdsearch instead accelerates unsorted substring/byte search, i.e. memmem/strstr territory. Pick it when the task is finding a byte pattern inside a buffer, not locating a key in an already-sorted sequence.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself; the benchmark driver additionally fetches a 'counters' library and StringZilla via CPM (network access needed at configure time) and can optionally link Rust's memchr crate |
| **Minimum toolchain** | C++17 for the library (GCC 14+ or a recent Clang, tested on GCC 14/15 and Apple clang 17); the benchmark driver needs C++23 for std::print; MSVC unsupported |
| **Platforms** | x86-64 requiring AVX-512F and AVX-512BW at compile time with no runtime dispatch, or AArch64 with NEON; other architectures fail to compile with #error |
| **Thread safety** | Documented as reentrant and thread-safe: no allocation, no global or static state; needle preprocessing happens fresh inside every call with nothing to amortize across calls |
| **Drop-in for the baseline** | partial — matches memmem/std::string::find first-occurrence semantics, but the call shape differs: explicit length-delimited pointers or string_view in, {bool,index} pair or npos out, no iterators |

## Gotchas

- No runtime CPU dispatch: an AVX-512-compiled binary executes illegal instructions on hardware without AVX-512F+BW; the caller must detect the CPU and keep a fallback path itself
- find_unguarded skips the work-counter guard entirely (a few percent faster on ordinary text) but reverts to O(n·m) worst case; documented as safe only on input the caller controls
- Tuning constants (NH2_START_ANCHORS, NH2_BUDGET_DEN, etc.) were fitted on Emerald Rapids, Zen 5 and Apple M4 Max; the README says you shouldn't need to touch them but does not claim they are optimal on other hardware
- No LICENSE file anywhere in the repo, so there is no stated legal basis for use, modification, or redistribution

## Caveats and trade-offs

No LICENSE file in the repo (reference usability only). The '45 GB/s, 30x memmem' figure names only an 'Apple M-series core', and the README says benchmark numbers should be measured on your own machine. benchmark/README.md notes Apple's libc memmem 'uses a much simpler scan and lands well behind strstr', so 30x is against a weak baseline. The benchmark driver includes strstr and std::search variants, but no numbers against them are published. Requires AVX-512F+BW on x86-64 (no runtime dispatch) or NEON.

x86-64 build requires AVX-512F+BW at compile time with no runtime fallback (illegal instruction on CPUs without it, which excludes most Intel client parts and pre-Zen4 AMD); MSVC unsupported; benchmarked against C-library memmem/strstr, StringZilla and SSEF rather than against std::search

## Maintenance

Active: created 2026-07-28, last commit 2026-09-21, with one merged PR already fixing kernel correctness issues, but it is a brand-new, single-contributor project (9 stars, no LICENSE file), so treat it as reference material rather than something to depend on directly.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states 'about 45 GB/s on an Apple M-series core, 30x the platform memmem'. It gives no exact CPU model, compiler version, or results table for that figure. The README says benchmark numbers should be run on your own machine. First-party numbers with partial methodology: C.
- **Verifier notes:** The headline claim is quoted correctly. The baseline is memmem, a POSIX/GNU extension rather than ISO C, and Apple's implementation is weak per the repo's own docs. Metadata verified: no license, 9 stars, last commit 2026-09-21, not a fork.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lemire/simdsearch#readme>
  - <https://github.com/lemire/simdsearch>
  - <https://github.com/lemire/simdsearch/blob/main/benchmark/README.md>
- **Sources the enricher read:**
  - <https://github.com/lemire/simdsearch#readme>
  - <https://github.com/lemire/simdsearch/blob/main/benchmark/README.md>
  - <https://github.com/lemire/simdsearch>
  - <https://github.com/lemire/simdsearch/issues>
  - <https://github.com/lemire/simdsearch/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/lemire/simdsearch`) · [data/wave1/enrich/raw/github_com_lemire_simdsearch.json](../../../data/wave1/enrich/raw/github_com_lemire_simdsearch.json) (enrichment confidence 0.6)

</details>
