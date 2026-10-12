# cisv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> SIMD-accelerated C CSV parser/writer (AVX-512/AVX2) beating csvkit and PapaParse; monorepo now deprecated.

| | |
|---|---|
| **Beats** | csvkit |
| **Claimed result** | \~178x faster than csvkit on 1M-row row counting (9.788s vs 0.055s; derived from page data); \~2.4x faster than PapaParse in Node.js sync mode (60.80 MB/s vs 25.12 MB/s; derived from page data) |
| **Workload** | Row counting on a 1M-row (98MB) CSV via CLI, wall-clock time vs miller, wc -l, rust-csv and csvkit (xsv is named in the methodology but absent from the results table); also Node.js synchronous parse throughput vs PapaParse/csv-parse |
| **Metric** | throughput |
| **Compiler and flags** | -O3 -march=native -mavx512f -mavx512bw (AVX-512/AVX2, scalar fallback on unsupported CPUs) |
| **Adoption** | 91 stars |
| **Last commit** | 2026-03-05 |
| **Links** | [repository](https://github.com/sanix-darker/cisv) · [benchmark](https://sanixdk.xyz/blogs/how-i-accidentally-created-the-fastest-csv-parser-ever-made) |

## Verdict

Author's blog, built with -O3 -march=native -mavx512f -mavx512bw on an unspecified Intel Core i9, reports CLI row-counting of a 1M-row/98MB CSV: miller 0.004s, cisv 0.055s, wc -l 0.083s, rust-csv 0.664s, csvkit 9.788s (\~178x over csvkit, but \~14x slower than miller in the same table). Separately, Node.js synchronous parsing measured cisv at 60.80 MB/s vs PapaParse 25.12 MB/s (\~2.4x) and csv-parse 14.67 MB/s.

## Use it when

- Row-counting or bulk parsing of large CSVs on x86-64 with AVX-512 or AVX2 available
- Embedding a small C parser/writer directly into a C/C++ codebase rather than shelling out to a Python tool
- Node.js/Python/PHP apps that need faster synchronous CSV parsing than PapaParse/csv-parse for one-shot batch jobs
- Workloads needing early-exit row iteration (stop after N matching rows) without loading the whole file
- Multi-core boxes where parallel chunked parsing of one large file is worth the added complexity

## Skip it when

- Production systems: the whole monorepo is archived/deprecated by its own author, moved to separate cisv-core/cisv-cli/bindings repos with unclear activity
- CPUs without AVX2/AVX-512 (older x86, some cloud instance types) — falls back to SSE2/NEON/scalar with speed not benchmarked
- Anywhere `miller` is an option: the author's own table shows miller \~14x faster than cisv on the same 1M-row count
- Windows — unsupported (README lists it as 'planned... maybe')
- Teams needing a mature, community-supported CSV toolkit rather than a single-author experimental project (91 stars, author calls it 'still evolving')

## How it is fast

Vectorized byte scanning for delimiters/quotes/newlines using AVX-512 mask compares (or AVX2/SSE2 movemask + ctz, ARM NEON fallback) instead of a byte-at-a-time state machine. Input files are zero-copy memory-mapped with kernel read-ahead hints and read through an L3-sized ring buffer. A chunk-splitting API (mmap + split-at-row-boundaries) enables multi-threaded parallel parsing, described in the header as a '1 Billion Row Challenge technique'.

## Compared with alternatives

Pick cisv only for a minimal, vendorable C library/CLI using raw SIMD intrinsics with no dependencies; zsv (same category) does the same mmap+SIMD row-counting approach but is faster in its own benchmarks, more actively maintained, and has broader language coverage, so prefer zsv unless you specifically want cisv's smaller C surface.

## Integration

| | |
|---|---|
| **Form** | source-drop / static lib (CMake or Makefile build) plus separate Node.js/Python/PHP native bindings |
| **Dependencies** | none for core C library; Node.js 14+, Python 3.7+, or PHP 7.4+ toolchains for the respective bindings |
| **Minimum toolchain** | GCC 7+ or Clang 6+, CMake 3.14+ |
| **Platforms** | x86-64 (AVX-512 or AVX2 preferred, SSE2 fallback), ARM64/NEON; Linux and macOS only, no Windows |
| **Thread safety** | not documented globally; parallel API requires one parser instance per thread, each parsing its own chunk |
| **Drop-in for the baseline** | partial — different C API/CLI flags than csvkit's Python interface, not a compatible replacement |

## Gotchas

- Repo is marked DEPRECATED in its own README; code has moved to split repos (cisv-core, cisv-cli, cisv-nodejs, cisv-python, cisv-php)
- Peak throughput requires AVX-512; on AVX2/SSE2/NEON hardware speed is unverified
- Author states the code changed during writing of the benchmark blog post, so published numbers may not match current source
- Row iterator's returned field pointers are only valid until the next call — no copy-out API mentioned for retention

## Known shortcomings

- Upstream marks this monorepo deprecated in favour of split cisv-core / cisv-cli / language-binding repos; the benchmark measures CLI row counting, not full parsing.

## Caveats and trade-offs

Repo is archived by its own author. CPU model not stated (compiler flags -O3 -march=native -mavx512f -mavx512bw given, hardware not), so evidence stops short of Tier A/B. The CLI test is row counting, not full parsing; the 178x is against csvkit (a Python tool), while miller is faster than cisv in the same table (0.004s) and cisv is only slightly faster than wc -l. Author notes the code evolved during the article so numbers may not match the current code.

Needs AVX-512/AVX2 for peak speed; author's own table shows `miller` was actually faster than cisv on the same 1M-row test (0.004s vs 0.055s), undercutting the 'fastest ever' title; repo has since been archived.

## Maintenance

Abandoned/archived, and the monorepo itself declares itself deprecated in favor of split successor repos; MIT-licensed and small enough to vendor, but pick a maintained fork or successor repo before depending on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Author's own blog shows a 'CLI ROW COUNTING PERFORMANCE (1M rows)' table (miller 0.004s, cisv 0.055s, wc -l 0.083s, rust-csv 0.664s, csvkit 9.788s) and Node.js sync throughput (cisv 60.80 MB/s vs papaparse 25.12 MB/s); compiler flags are given but no CPU model, so first-party partial methodology = C.
- **Verifier notes:** Numbers match the page; workload corrected from 'parsing' to 'row counting' and derived marker added to the PapaParse ratio. Archived, 91 stars, MIT, last commit 2026-03-05 confirmed.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://sanixdk.xyz/blogs/how-i-accidentally-created-the-fastest-csv-parser-ever-made>
  - <https://github.com/sanix-darker/cisv>
- **Sources the enricher read:**
  - <https://github.com/sanix-darker/cisv>
  - <https://github.com/sanix-darker/cisv/blob/HEAD/README.md>
  - <https://github.com/sanix-darker/cisv/blob/HEAD/core/include/cisv/parser.h>
  - <https://github.com/sanix-darker/cisv/blob/HEAD/core/include/cisv/simd.h>
  - <https://sanixdk.xyz/blogs/how-i-accidentally-created-the-fastest-csv-parser-ever-made>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/sanix-darker/cisv`) · [data/wave3/enrich/raw/github_com_sanix_darker_cisv.json](../../../data/wave3/enrich/raw/github_com_sanix_darker_cisv.json) (enrichment confidence 0.35)

</details>
