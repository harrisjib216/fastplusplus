# rankselect (PTSelect, splatlab)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Research fork of CMU's CS-Poppy rank/select bitvector that swaps word-level select for PTSelect (PDEP+TZCNT); benchmarked against SDSL.

| | |
|---|---|
| **Beats** | SDSL rank/select support (also CS-Poppy) |
| **Claimed result** | Snippet only (arXiv 1706.00990, not opened): PTSelect, a 4-instruction machine-word select (PDEP + TZCNT), is 2x-4x faster than the previous state-of-the-art 64-bit word select; select on bit vectors is 2.2x-6x faster than CS-Poppy and SDSL. |
| **Workload** | Rank and select queries on uncompressed bit vectors, plus select on single 64-bit words using PDEP and TZCNT (PTSelect); the repo has bitmap_bench.cc and bitmap_bench_sdsl.cc that time the same queries on this code and on SDSL. |
| **Metric** | latency |
| **Compiler and flags** | Makefile: g++ -std=c++11 -O9 -mpopcnt -msse4 -I. -Iinclude/ -Iinclude/sdsl |
| **Adoption** | 15 stars, 3 forks (fork of efficient/rankselect, 55 stars) |
| **Last commit** | 2017-04-14 |
| **Links** | [repository](https://github.com/splatlab/rankselect) · [benchmark](https://arxiv.org/abs/1706.00990) |

## Verdict

The only performance numbers come from search-result snippets of arXiv 1706.00990: PTSelect is 2x-4x faster than prior 64-bit word select, and plugging it into CS-Poppy and SDSL makes bit-vector select 2.2x-6x faster; the repo has the benchmark drivers (bitmap_bench.cc, bitmap_bench_sdsl.cc, bitmap_bench_word.cc) with -O9 -mpopcnt -msse4, but no published results, CPU model, or correctness checks.

## Use it when

- Studying or reproducing the 2017 PTSelect result, or lifting the 4-instruction select64_pdep_tzcnt routine (Apache-2.0) into your own rank/select structure.
- Static, uncompressed bit vectors on Intel Haswell or later (or AMD Zen 3 or later) where select latency dominates.
- As a comparison point when benchmarking newer rank/select structures against CS-Poppy and SDSL.

## Skip it when

- As a production select: in the current head, BitmapPoppy::select passes a 1-based in-word rank to the 0-based select64_pdep_tzcnt and uses LSB-first word select while the index and construction loop use MSB-first bit order, so select results do not match the structure's rank convention; no correctness test exists in the repo.
- Memory-constrained hosts: this fork enlarged BitmapPoppy's member arrays from 2^16 to 2^31 entries (uint32\* loc_[1ULL&lt;&lt;31] and uint64 locCount_[1ULL&lt;&lt;31], about 32 GiB of object), and the constructor memsets the 16 GiB locCount_ array.
- CPUs without fast BMI2: PDEP is missing before Haswell and microcoded on AMD Zen 1/Zen 2 (search snippets report about 300-cycle latency on Zen 2), where PTSelect loses badly; there is no runtime fallback.
- When you need compressed bit vectors, updates, or a maintained library: newer catalogued entries (SPIDER, 3star-rankselect, QuadRank, pasta/sux-based designs) target the same queries and are actively developed; this repo's last commit is 2017-04-14.

## How it is fast

Bit-vector select uses CS-Poppy's layout: a 3-level rank index (64-bit L1 entries every 2^32 bits, L2 entries every 2048 bits holding three 10-bit sub-block counts) plus a sampled position array every 8192 ones, so select jumps near the target, scans L2 entries, then finishes inside one 512-bit basic block. The final in-word step is PTSelect: select(x, r) = TZCNT(PDEP(1 &lt;&lt; r, x)), two BMI2/LZCNT-era instructions instead of the 50-80-instruction broadword or table-lookup routines. The repo keeps the older select64_sdsl, broadword and popcount-search variants in popcount.h for comparison.

## Compared with alternatives

Pick it only to borrow the PTSelect word routine or to reproduce the 2017 CS-Poppy/SDSL comparison; for a usable rank/select bit vector, SPIDER, 3star-rankselect or QuadRank are newer, benchmarked against Poppy and SDSL in their own repos, and do not carry this fork's select-convention and 32 GiB-object problems. succinct-bitvec-cpp is a smaller self-contained alternative with published SDSL comparisons.

## Integration

| | |
|---|---|
| **Form** | source-drop (bitmap.cc, bitmap.h, popcount.h, shared.h; Makefile builds benchmark binaries only) |
| **Dependencies** | none for the structure; the SDSL comparison benchmark uses SDSL sources bundled under include/sdsl |
| **Minimum toolchain** | C++11 (Makefile: g++ -std=c++11 -O9 -mpopcnt -msse4); GCC-style inline asm required |
| **Platforms** | x86-64 only; select needs BMI2 (PDEP) and TZCNT, i.e. Intel Haswell+ or AMD Zen 3+ for usable speed, injected via inline asm so the compiler flags do not check for it |
| **Thread safety** | not documented; queries only read the index, construction is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Allocations are made inside assert(posix_memalign(...) &gt;= 0) in bitmap.cc (and assert(... == 0) in the benches), so any build with -DNDEBUG (e.g. CMake Release) compiles the allocation away and leaves the index pointers uninitialized.
- select64_pdep_tzcnt computes 1ULL &lt;&lt; rank, which is undefined for rank 64; select512 can pass k = 64 for a full word, and a rank beyond the word's popcount returns 64 rather than an error.
- The benchmark code at commit 952ad74 ('Final commit to collect benchmarks', 2017-02-17) still routed select64 to select64_sdsl; PTSelect became the default only in the last commit (29bc174, 2017-04-14), so which variant produced published numbers is not stated in the repo.
- Timing uses gettimeofday and random synthetic bits with a density parameter; bitmap_bench_word times selectWord on a single fixed word (index 2279) through a non-inlined call and discards the result.

## Known shortcomings

- Tier C: numbers come only from snippets of arXiv 1706.00990 (blocked): 2x-4x word select, 2.2x-6x over CS-Poppy and SDSL. Fork of efficient/rankselect; last commit 2017-04-14.
- Correctness bug at head: BitmapPoppy::select passes a 1-based in-word rank to the 0-based select64_pdep_tzcnt, and the word select counts bits from the LSB while the index is MSB-first, so select disagrees with rank; no test in the repo. The benchmark commit 952ad74 (2017-02-17) still routed select64 to select64_sdsl and PTSelect became the default only in 29bc174 (2017-04-14). The fork grew loc_/locCount_ from 1&lt;&lt;16 to 1ULL&lt;&lt;31 entries (object about 32 GiB, the constructor memsets 16 GiB), and the posix_memalign calls sit inside assert, so -DNDEBUG builds skip allocation.

## Caveats and trade-offs

Speedup numbers come only from search snippets of arXiv preprint 1706.00990 (arXiv and a third-party summary blog are blocked here). The README is one line with no numbers, and no CPU model appears in the repo. The repo is a GitHub fork of efficient/rankselect (CMU's CS-Poppy code, Apache-2.0, copyright 2013 CMU); this fork adds PTSelect (select64_pdep_tzcnt in popcount.h, used by select64) and the SDSL benchmark. It needs a Haswell-or-later CPU with BMI2, although the Makefile passes only -mpopcnt -msse4 because PDEP/TZCNT come in through inline asm. Timing uses gettimeofday. It bundles an older SDSL version (2017). Newer work (pasta bit_vector, sux) is already catalogued and likely faster. Preprint; peer-review status not verified.

Select via PDEP needs a Haswell-or-later x86 CPU (BMI2). Rank/select over uncompressed bit sequences only. Bundles an old copy of SDSL headers for the comparison.

## Maintenance

Abandoned since 2017-04-14, Apache-2.0; usable as a reference for the PTSelect idea, but the structure itself needs fixes (select bit order and rank base, 32 GiB member arrays, asserts around allocation) before anyone vendors it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo ships benchmark code that times the same rank/select queries on this code (bitmap_bench.cc, bitmap_bench_word.cc) and on SDSL (bitmap_bench_sdsl.cc) with stated flags, but it publishes no numbers or CPU model. The only numbers are in arXiv preprint 1706.00990, which is blocked here and known only from search snippets (2x-4x on 64-bit words; 2.2x-6x over CS-Poppy and SDSL), so C stays with a snippet-only caveat.
- **Verifier notes:** Record mostly accurate. Repo is a GitHub fork of efficient/rankselect (set is_fork_of). Last commit 2017-04-14 ('using pdep-tzcnt select.') confirmed; license Apache-2.0 confirmed from the LICENSE file.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/splatlab/rankselect>
  - <https://github.com/splatlab/rankselect/commits>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/README.md>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/Makefile>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap_bench.cc>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap_bench_sdsl.cc>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap_bench_word.cc>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap.cc>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/popcount.h>
  - <https://github.com/efficient/rankselect>
- **Sources the enricher read:**
  - <https://github.com/splatlab/rankselect>
  - <https://github.com/splatlab/rankselect/commits>
  - <https://github.com/splatlab/rankselect/commits/master/popcount.h>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/README.md>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/Makefile>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/popcount.h>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap.h>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap.cc>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap_bench.cc>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/bitmap_bench_word.cc>
  - <https://raw.githubusercontent.com/splatlab/rankselect/HEAD/shared.h>
  - <https://raw.githubusercontent.com/splatlab/rankselect/952ad74/popcount.h>
  - <https://raw.githubusercontent.com/efficient/rankselect/HEAD/bitmap.h>
  - <https://raw.githubusercontent.com/efficient/rankselect/HEAD/bitmap.cc>
  - <https://raw.githubusercontent.com/efficient/rankselect/HEAD/popcount.h>
  - https://www.adrian.idv.hk/2018-11-05-pbj17-fastx86/ (WebSearch snippet only)
  - https://arxiv.org/pdf/1706.00990 (WebSearch snippet only; arXiv blocked, paperhub mirror returned 403)
  - https://news.ycombinator.com/item?id=40985258 (WebSearch snippet only, Zen 2/Zen 3 PDEP latency)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/splatlab/rankselect`) · [data/wave9/enrich/raw/github_com_splatlab_rankselect.json](../../../data/wave9/enrich/raw/github_com_splatlab_rankselect.json) (enrichment confidence 0.65)

</details>
