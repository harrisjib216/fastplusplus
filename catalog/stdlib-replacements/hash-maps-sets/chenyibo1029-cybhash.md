# CYBHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Header-only bit-packing + BMI2 pext lookup for fixed-format Chinese futures/stock/option ticker symbols, vs std::unordered_map.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | README states 'approximately 10 times faster than std::unordered_map'; the repo's own GitHub description separately states 'approximately 5-30 times faster than std::unordered_map' -- the two first-party figures are inconsistent, and no benchmark script, raw numbers, or workload size is published. |
| **Workload** | Mapping Chinese futures/stock/option ticker symbols to values by converting the symbol string into an int64 key at runtime (borrowing ideas from qlibs/mph and MengRao/str) and then doing fast lookup, versus keying a std::unordered_map directly on the symbol. |
| **Metric** | throughput |
| **Compiler and flags** | g++ -std=c++17 -mbmi2 -O3 -DNDEBUG (from the repo's test.sh; not stated as the configuration behind the README's 10x figure) |
| **Adoption** | 10 stars |
| **Last commit** | 2025-03-14 |
| **Links** | [repository](https://github.com/chenyibo1029/CYBHash) · [benchmark](https://github.com/chenyibo1029/CYBHash/blob/main/README.md) |

## Verdict

The README states CYBHash is 'approximately 10 times faster than std::unordered_map' for symbol-to-value lookup, while the repo's separate GitHub description says 'approximately 5-30 times faster' -- the two first-party figures disagree. testCYBHash.cc + test.sh do contain a real benchmark harness (bench_file_unordered_map alongside the symbol-table benches, run via g++ -std=c++17 -mbmi2 -O3 -DNDEBUG over bundled combine.txt/shfe.txt/stock.txt/dce.txt/option.txt files), but no output numbers, hardware, or compiler version tied to the README's claim are published anywhere in the repo.

## Use it when

- Keys are exactly Chinese futures/stock/option ticker symbols (5-16 ASCII chars, e.g. '600000.SSE', 'eb2505-C-10000') that fit this project's packing rules
- The key set is known/stable before the hot lookup loop (build via sync_with_unordered_map() once, then read-only queries)
- Running on x86-64 hardware with BMI2 (pext) available
- Throughput on symbol-&gt;value lookup matters more than general-purpose map semantics
- You are prototyping/studying the technique rather than shipping it verbatim (no license to redistribute)

## Skip it when

- Any key format other than these narrow ticker patterns -- get_id()'s bit layout is hard-coded per table type, not a general string hash
- Keys are inserted/removed continuously; the design assumes a build-then-freeze workflow, not interleaved mutation
- Target platform lacks BMI2 (older x86, most ARM/aarch64) -- pext isn't available, and the code isn't portable around it
- You need a license to copy/redistribute the code -- no LICENSE file exists at the repo root
- You need verified performance numbers before adopting -- no benchmark output, hardware, or run data is published, and the project shows no CI, tests-as-assertions beyond ad hoc checks, or recent activity

## How it is fast

Each fixed-length ticker string (5-16 bytes) is packed into a uint64 id via per-table bit-selection logic (get_id), then find_min_mask_by_cost greedily/bruteforce-searches for a small bit mask whose _pext_u64 (BMI2 pext instruction) extraction gives few collisions across the known key set. Lookups become one pext plus linear-probe over a flat vector&lt;pair&lt;id,value&gt;&gt;, skipping std::unordered_map's string hashing and bucket-chain traversal entirely. The idea is borrowed from qlibs/mph (pext-based hashing) and MengRao/str (fast fixed-size string keys, bundled as Str.h/StrHash.h though unused in the active benchmark path).

## Compared with alternatives

Only if your keys are literally these Chinese exchange ticker formats and you're willing to vendor unlicensed, unbenchmarked code for a niche win; for general string/integer key hashing, catalogued siblings like emhash, tsl::robin_map, or Verstable are general-purpose, actively tested, and (unlike CYBHash) carry reproducible benchmark data and clear licenses.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required for CYB_Hash.h itself; repo also bundles Str.h/StrHash.h (MengRao/str, MIT) but those are not used by the active benchmark code paths (bench_hash&lt;&gt; calls are commented out in testCYBHash.cc main()) |
| **Minimum toolchain** | C++17, g++ with -mbmi2 (per test.sh: g++ -std=c++17 -mbmi2 -O3 -DNDEBUG) |
| **Platforms** | x86-64 with BMI2 (pext instruction) required; testEndian() throws at construction on big-endian; aarch64/ARM not supported |
| **Thread safety** | not documented -- no locks/atomics in CYB_Hash.h; build phase (operator[] + sync_with_unordered_map) is unsynchronized like std::unordered_map, and get_value() reads are plain vector indexing with no protection against concurrent writes |
| **Drop-in for the baseline** | partial — explain: population uses std::unordered_map's operator[] syntax (it inherits from unordered_map), but you must call sync_with_unordered_map()/sync_with_additional_symbols() before querying, and lookups go through get_value(sym) rather than find()/operator[], so call sites must change |

## Gotchas

- Symbol length is constrained to 5-16 characters; if length is 16 the last byte must be '0', otherwise sync_with_unordered_map() prints an error and calls std::exit(0)
- Table size is capped at 1&lt;&lt;MAX_BIT_SIZE (2^25) entries; sync returns false / prints 'table size too large' beyond that
- get_id() bit-packing differs per subclass (option/stock/stock6/future) and is specific to real Chinese exchange symbol formats (e.g. '.SSE'/'.SZE'/'.BSE' suffixes, 'eb2505-C-10000' style option codes) -- using it outside those formats gives undefined/garbage ids
- future_symbol_table's calculate_mask disallows id conflicts and can abort (exit(0)) if no collision-free mask is found within the search space

## Caveats and trade-offs

No LICENSE file in the repo, so all rights are reserved by default. The speedup claim differs between the README ('approximately 10 times') and the repo description ('approximately 5-30 times'). A benchmark harness exists (testCYBHash.cc, with bench_file_unordered_map and the symbol-table benches, driven by test.sh on bundled symbol files), but no results, hardware or compiler version are published. The numbers cannot be checked without running it. It needs BMI2 (pext).

Only applicable to a narrow, domain-specific key space (Chinese futures/stock/option ticker symbols that can be packed into an int64); it is closer to a specialized key-encoding trick than a general-purpose hash map, and has no license, so the code cannot legally be reused/copied (study-only).

## Maintenance

Last commit 2025-03-14 with 10 stars; maintenance looks stale (no issues, PRs, releases, or CI found). Usability stays reference-only: GitHub reports license: null (no repo-root LICENSE file), even though CYB_Hash.h itself carries an inline MIT header (Copyright 2023 Chen Yibo) and the bundled StrHash.h/Str.h carry a separate inline MIT header (Copyright 2019 Meng Rao) -- the absence of a formal LICENSE file leaves redistribution rights ambiguous despite these in-file notices.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states a bare first-party ratio ('approximately 10 times faster than std::unordered_map'). No results, hardware or run data are published. The repo does contain a benchmark harness against std::unordered_map (testCYBHash.cc, test.sh), so C.
- **Verifier notes:** The record's claim of 'no benchmark script' is wrong: test.sh and testCYBHash.cc benchmark against std::unordered_map, and I fixed the caveats. No license means usability stays 'reference'. Metadata checked: 10 stars, last commit 2025-03-14 (stale), not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/chenyibo1029/CYBHash>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/README.md>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/test.sh>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/testCYBHash.cc>
- **Sources the enricher read:**
  - <https://github.com/chenyibo1029/CYBHash>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/README.md>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/CYB_Hash.h>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/test.sh>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/testCYBHash.cc>
  - <https://github.com/chenyibo1029/CYBHash/blob/main/StrHash.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/chenyibo1029/cybhash`) · [data/wave1/enrich/raw/github_com_chenyibo1029_cybhash.json](../../../data/wave1/enrich/raw/github_com_chenyibo1029_cybhash.json) (enrichment confidence 0.35)

</details>
