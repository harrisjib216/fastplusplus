# Tachyon.JSON v6

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Proprietary (TACHYON PROPRIETARY SOURCE LICENSE v1.0; LICENSE file allows free personal/commercial use but forbids redistribution of source, sub-licensing, and modifying the ASM/SIMD kernels)` · 🟢 active

> Single-header AVX2 JSON parser under a proprietary license; benchmarks nlohmann/simdjson but times only its structural-bitmask build, not full parsing.

| | |
|---|---|
| **Beats** | nlohmann::json (also compared against simdjson and Glaze) |
| **Claimed result** | README table: Large Array (25MB) Tachyon 4,577 MB/s vs Nlohmann 25 MB/s (\~183x, derived from page data) and vs Simdjson OnDemand 1,886 MB/s (\~2.4x, printed on page). canada.json: Tachyon 5,585 MB/s vs Nlohmann 31 MB/s (\~180x, derived from page data) and vs Simdjson 3,541 MB/s (\~1.6x, derived from page data). The README headline says \~2.4x vs simdjson and \~200x vs nlohmann. The 'within 1-2% of simdjson on 256MB' statement does not appear on the page. |
| **Workload** | bench_scientific.cpp: in-memory generated 25MB large-array JSON and canada.json, CPU pinned. Tachyon is timed only on parse_view (structural bitmask index, no value materialization). nlohmann is timed on full DOM parse, glaze on glz::generic DOM read, simdjson on ondemand parser.iterate(). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon (Haswell), exact model unspecified |
| **Compiler and flags** | g++ (version unstated), Makefile: -std=c++23 -O3 -march=native -flto |
| **Adoption** | 0 stars |
| **Last commit** | 2026-01-04 |
| **Links** | [repository](https://github.com/mrcodechef/Tachyon.JSON) · [benchmark](https://github.com/mrcodechef/Tachyon.JSON) |

## Verdict

README claims Tachyon's parse_view() (builds only a structural bitmask index, no value materialization) reaches 4,577 MB/s on a 25MB in-memory generated array and 5,585 MB/s on canada.json, vs simdjson's ondemand parser.iterate() at 1,886/3,541 MB/s (\~2.4x/\~1.6x) and nlohmann::json's full json::parse() DOM build at 25/31 MB/s (\~183x/\~180x), built with g++ -std=c++23 -O3 -march=native -flto (compiler version unstated) on an unspecified Intel Xeon (Haswell). The harness runs 1000 iterations for Tachyon and simdjson, 100 for Glaze, and only 10 for nlohmann, despite the README stating a uniform 'median of 1000 iterations'.

## Use it when

- Read-heavy code that only probes a few keys/values from a large document via Cursor-based lazy lookup and never needs a materialized DOM
- x86-64 deployments where AVX2 is guaranteed and build flags can be tuned per machine (e.g. -march=native)
- Studying/benchmarking a PSHUFB structural-classification + branchless quote-escape-bitmask technique, given the license blocks reusing the code itself
- Data that is only integers, strings, and booleans -- no fractional numbers anywhere in the document
- Throwaway internal tooling where a 0-star, single-maintainer, unlicensed-for-redistribution header is acceptable

## Skip it when

- Any JSON containing floating-point values: materialize() and the lazy number accessor both parse bare numbers as int64_t via std::from_chars, so "3.14" silently becomes 3, and dump() has no serialization case for the double variant (a json built from a double prints the literal string "null")
- Anything needing portability: the scan hard-requires AVX2 (_mm256_\* intrinsics) with no scalar fallback and no runtime CPU dispatch like simdjson's -- it won't build/run on non-AVX2 x86 or ARM
- Commercial or open-source products you need to redistribute, fork, or modify -- the TACHYON PROPRIETARY SOURCE LICENSE v1.0 forbids redistribution and forbids modifying the ASM/SIMD kernels
- CBOR or MessagePack support -- from_cbor()/from_msgpack() are stubs that throw std::runtime_error
- Trusting the throughput numbers as apples-to-apples: the README times Tachyon's index-only parse_view() against nlohmann's/simdjson's/glaze's full value decode, runs nlohmann for only 10 iterations vs 1000 for Tachyon/simdjson (README claims uniform 'median of 1000') and has no CPU model, compiler version, or public CI run behind the numbers

## How it is fast

The structural scan (SIMD::compute_structural_mask) loads 128 bytes at a time into four 256-bit AVX2 registers, uses a PSHUFB (_mm256_shuffle_epi8) nibble lookup table to classify bytes as quote/backslash/structural in one pass, and derives a per-32-byte token-boundary bitmask with _mm256_movemask_epi8. String/escape state is tracked with a branchless XOR-prefix-sum over the quote bitmask rather than a byte-by-byte state machine, falling back to a scalar loop only when a chunk contains a backslash. Because parse_view() stops at building this index and never allocates or decodes individual values, the benchmarked 'parse' step skips the DOM construction that nlohmann, simdjson OnDemand, and Glaze all pay for in the same loop -- which accounts for most of the measured gap.

## Compared with alternatives

Rarely: the catalogued siblings (cjson.cpp, json.cpp, DAW JSON Link, utl::json) all measure the same operation on both sides of their comparison and ship under permissive licenses. Tachyon's index-only benchmark isn't measuring the same thing as a full nlohmann/simdjson parse, and its DOM path silently mangles floating-point data, so pick it only to study the AVX2 structural-bitmask/PSHUFB technique in isolation -- not for production parsing, redistribution, or any dataset with fractional numbers.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself (bench_scientific.cpp separately pulls in nlohmann/json, simdjson, and Glaze only for the comparison harness) |
| **Minimum toolchain** | C++20 minimum (uses &lt;concepts&gt;, std::countr_zero/std::popcount from &lt;bit&gt;, string_view); README badge says C++20 but the shipped Makefile compiles the benchmark with -std=c++23 -O3 -march=native -flto -- unclear if C++23 is actually required by Tachyon.hpp itself |
| **Platforms** | x86-64 with AVX2 required (immintrin.h 256-bit intrinsics: _mm256_shuffle_epi8, _mm256_movemask_epi8, etc.); no aarch64/NEON path and no runtime feature detection, so it must be compiled for an AVX2-capable target |
| **Thread safety** | Not documented. A parsed Document is held behind a std::shared_ptr and read through a Cursor, which looks safe for concurrent read-only lazy lookups, but json::materialize() mutates a node's std::variant in place with no synchronization, so concurrently materializing the same json object from multiple threads is unsafe. |
| **Drop-in for the baseline** | false -- different namespace/types (Tachyon::json vs nlohmann::json), no double/float decoding, no CBOR/MessagePack, error handling via out_of_range/runtime_error rather than nlohmann's exception hierarchy |

## Gotchas

- Materializing to DOM (or calling as_int64() on any lazy node) parses every bare number as int64_t via std::from_chars, silently truncating fractional values (3.14 -&gt; 3); there is no reachable path that produces a double from parsed text
- json::dump() has no case for the double variant -- a json constructed from a C++ double (e.g. json(3.14)) serializes to the literal string "null"
- No scalar/fallback path for non-AVX2 hardware: compute_structural_mask and skip_whitespace assume 256-bit AVX2 registers are available at compile time
- from_cbor()/from_msgpack() exist as API stubs and always throw std::runtime_error("... not fully implemented")

## Caveats and trade-offs

The benchmark code is committed (bench_scientific.cpp, Makefile), but it is apples-to-oranges. Tachyon's timed loop only builds a structural bitmask (parse_view), while nlohmann builds a full DOM. The README says 'median of 1000 iterations', but the code runs nlohmann 10 times and glaze 100 times. There is no compiler version and no exact CPU model. The 180x+ figure is far above the 50x plausibility threshold. The repo has 0 stars and is not a GitHub fork. Its commits (2026-01-02 to 2026-01-04) are authored by wilkolbrzym-coder and the google-labs-jules bot, so this looks like a copy of the now-404 wilkolbrzym-coder/Tachyon.JSON. The license is proprietary, so it is reference-only.

Licensed under a proprietary 'TACHYON PROPRIETARY SOURCE LICENSE v1.0' that explicitly prohibits redistribution and modification/extraction of its ASM/SIMD kernels -- code can be studied but not reused or copied. No public benchmark harness file was found alongside the README (numbers appear to be self-run and pasted in, not scripted/reproducible).

## Maintenance

Repo history spans only 2026-01-02 to 2026-01-04 (created and last pushed within days of each other), 0 stars, and the proprietary license permits free use but forbids redistribution, forking, or modifying the SIMD kernels -- reference/study-only despite counting as 'active' under a 12-month recency rule.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** These are first-party README numbers. The repo does hold bench_scientific.cpp and a Makefile (g++ -std=c++23 -O3 -march=native -flto), but it states no compiler version and no exact CPU model ('Intel Xeon (Haswell)'). The \~183x vs nlohmann is implausible and apples-to-oranges, so C is the cap.
- **Verifier notes:** README numbers match the record, but the '1-2% on 256MB' claim is absent and the nlohmann ratio compares index-only vs full-DOM work. The record wrongly said there was no benchmark code, all commits landed in one day, and status was 'finished'. Last commit 2026-01-04 is under 12 months old, so status is active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `license`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mrcodechef/Tachyon.JSON>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/README.md>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/Makefile>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/LICENSE>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/bench_scientific.cpp>
  - <https://github.com/wilkolbrzym-coder/Tachyon.JSON>
- **Sources the enricher read:**
  - <https://github.com/mrcodechef/Tachyon.JSON>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/README.md>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/Makefile>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/bench_scientific.cpp>
  - <https://github.com/mrcodechef/Tachyon.JSON/blob/main/Tachyon.hpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mrcodechef/tachyon.json`) · [data/wave1/enrich/raw/github_com_mrcodechef_tachyon_json.json](../../../data/wave1/enrich/raw/github_com_mrcodechef_tachyon_json.json) (enrichment confidence 0.25)

</details>
