# SPIDER (Succinct Predictive InDEx for Rank and select)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🟡 stale

> Research C code for a \~3.8%-overhead rank/select bit vector that interleaves rank counters with data and predicts select positions.

| | |
|---|---|
| **Beats** | pasta-flat and pasta-wide, poppy (cs-poppy), Vigna's rank9 and SDSL rank/select structures (competitor list from WebSearch snippets of the SEA 2024 paper; paper not opened) |
| **Claimed result** | Snippets of the SEA 2024 paper / arXiv 2405.05214 (snippet only, paper blocked): 3.82-3.83% space overhead; 'the fastest known structure for bit vectors of 8 billion bits or more, outperforming pasta-flat by 22%' for rank; for select it improves on the state of the art with under 5% extra space and 'nearly matches' the best known succinct structure that uses 12.5% space (i.e. not faster than that one). No per-baseline ratio against SDSL seen. |
| **Workload** | Rank and select queries on large bit vectors (datasets of 8 billion or more bits are where the rank win is reported). |
| **Metric** | latency |
| **Adoption** | 5 stars |
| **Last commit** | 2024-05-28 |
| **Links** | [repository](https://github.com/williams-cs/spider) · [benchmark](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SEA.2024.21) |

## Verdict

The SEA 2024 paper (seen only as search snippets; Dagstuhl and arXiv are blocked here) reports 3.82-3.83% space overhead, the fastest rank for bit vectors of 8 billion bits or more (22% better than pasta-flat) and select up to 41% faster than existing succinct structures while nearly matching the best 12.5%-space select; compiler, flags beyond the Makefile's gcc -O9 -march=native, and CPU are not visible. An independent Rust reimplementation in QuadRank's repo (i7-10750H at 3.0 GHz, n=2^35 bits) measured the SPIDER-style block at 29.39 ns/query in a single-thread loop vs 17.75 ns for sux-rs Rank9 and 33.99 ns for RankSmall&lt;1,11&gt; at similar 3% space (derived from page data).

## Use it when

- Reference design when you are writing your own rank/select for very large bit vectors (the paper reports the gain at 8 billion bits or more, snippet only) and want low space overhead.
- Studying or porting the interleaved-counter layout; QuadRank's BinaryBlock16Spider is a Rust reimplementation of the same block layout.
- Prototyping select with prediction (linear interpolation from sampled positions) on x86-64 with BMI2.

## Skip it when

- Any production use: there is no LICENSE file, so the code cannot legally be copied, and it is not packaged as a library.
- Programs that need more than one bit vector or thread-safe reentrant objects: all state lives in non-static globals declared in helper.h, so even including the header in two translation units collides.
- Non-x86 targets: it includes x86intrin.h and uses _pdep_u64 and _lzcnt_u64 (BMI2/LZCNT), built with -march=native.
- Small or cache-resident bit vectors, where the single-cache-miss layout gives little; or workloads needing the fastest rank at any space, where 25%-overhead Rank9 still led in plain loops in QuadRank's measurements.
- When you need reproducible competitor numbers: the repo only times SPIDER itself, and a reproduction question in issue #1 is unanswered.

## How it is fast

Each 512-bit cache line stores 496 data bits plus a 16-bit rank counter relative to a 64-bit top-level count kept every 63,488 bits, so a rank query costs one cache-line access plus a small top-level array that usually stays in cache, then up to 8 popcounts. Select samples the position of every k-th one (16-bit low-level and 64-bit high-level sample arrays), linearly interpolates between samples to predict the target cache line, corrects with a short scan of the interleaved counters, and finishes inside the 64-bit word with PDEP + LZCNT. The ni-\* variants keep the counters in a separate array for comparison.

## Compared with alternatives

Only as a design reference: for a usable \~3.3%-overhead single-cache-miss rank, QuadRank/BiRank (MIT, Rust crate) implements the same layout and in its own benchmark streamed 2.63 ns vs 2.81 ns for its SPIDER-style block at 12 threads; for select, SPIDER's predictive scheme is the distinctive part, and splatlab rankselect (PTSelect) is the sibling to compare for in-word select.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C standard library, x86intrin.h) |
| **Minimum toolchain** | GCC with -march=native -mpopcnt -mlzcnt (Makefile uses gcc -O9); C standard not stated |
| **Platforms** | x86-64 with POPCNT, LZCNT and BMI2 (PDEP) |
| **Thread safety** | Not thread-safe to build (global arrays); read-only queries after construction share the globals, and concurrent queries are not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Bits are packed MSB-first: the builder shifts each input byte in from the low end of a 64-bit word, and the 16-bit counter occupies the top 16 bits of the first word of every cache line, so input layout differs from SDSL/sux LSB-first bit vectors.
- The builder reads the file one byte at a time with fgetc and ignores a failed fopen beyond printing perror, so construction is slow and a bad path crashes.
- speedtest.h times independent random queries in a loop with clock() (CPU time, not wall time) and generates indices from two 31-bit rand() calls, so the figure is loop throughput rather than dependent-query latency; issue #1 (Dec 2025, Ragnar Groot Koerkamp) asks why the paper's numbers sit between typical latency (\~80 ns) and loop throughput, and is unanswered.
- The 16-bit in-line counter limits each top-level block to 63,488 bits; this is fixed by #define, not configurable.

## Known shortcomings

- Downgraded B to C: the repo has no numbers and the SEA 2024 paper (LIPIcs.SEA.2024.21, Dagstuhl blocked) is known only from snippets (22% faster than pasta-flat at 8B+ bits; select only near the best 12.5%-space structure, not faster). No license, x86-only. Retier to B when the paper is readable.
- Not a library: global state in non-static helper.h globals, an fgetc builder and an MSB-first bit layout; speedtest.h times only SPIDER with clock() over an independent-query loop. Issue #1 (2025-12-18) asks for competitor bench code, a reproduction command and why latency looks low, with no reply. No LICENSE.

## Caveats and trade-offs

Peer-reviewed at SEA 2024 (LIPIcs vol. 301, paper 21), but the paper (Dagstuhl, arXiv) is blocked here, so the claim text is from WebSearch snippets only (snippet only); tier B is likely once the paper can be read. The repo README has no benchmark numbers, flags or CPU, and no LICENSE file exists (LICENSE, LICENSE.md, LICENSE.txt, COPYING all 404; no license header in spider.c), so code must not be copied. Code is x86-only (includes x86intrin.h; Makefile builds with gcc -O9 -march=native -mpopcnt -mlzcnt). Rank benefit is reported for very large vectors (8 billion bits or more); select is close to, not faster than, the best 12.5%-space structure.

Interleaves rank metadata with the bit vector (single cache miss per rank); select uses a prediction model. C code is a set of standalone test executables (spider.c, ni-spider.c, select variants), not a library API.

## Maintenance

Stale research artifact (10 commits, last 2024-05-28, 5 stars, no releases) with no license, so treat it as a reference to read, not code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The benchmark_url (repo) has no numbers and its speedtest.h only times SPIDER itself; the peer-reviewed SEA 2024 paper (LIPIcs.SEA.2024.21, arXiv 2405.05214) is the real evidence but Dagstuhl, arXiv and review sites are egress-blocked, so its claims were seen only as WebSearch snippets. Snippet-only numbers cap at C until a paper-access retier can confirm B.
- **Verifier notes:** Repo exists (5 stars, 1 fork, 10 commits, last commit 2024-05-28 'minor fix', no license); metadata in the record is correct. Downgraded B to C only because the paper could not be opened; queue a paper-access retier (Dagstuhl PDF LIPIcs.SEA.2024.21.pdf) to restore B.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; independent Rust reimplementation in quadrank's evals/rank-laptop.csv (n=2^35, 1 thread, plain loop): Spider-style block 29.39 ns vs Rank9 17.75 ns vs RankSmall&lt;1,11&gt; 33.99 ns (derived from page data)
- **Pages the verifier opened:**
  - <https://github.com/williams-cs/spider>
  - <https://github.com/williams-cs/spider/commits>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/README.md>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/Makefile>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/spider.c>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/speedtest.h>
- **Sources the enricher read:**
  - <https://github.com/williams-cs/spider>
  - <https://github.com/williams-cs/spider/issues>
  - <https://github.com/williams-cs/spider/issues/1>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/README.md>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/Makefile>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/spider.c>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/speedtest.h>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/helper.h>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/ni-spider.c>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/spider-1L-select.c>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/ni-helper.h>
  - <https://raw.githubusercontent.com/williams-cs/spider/HEAD/ni-spider-2L-select.c>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/src/binary/blocks.rs>
  - <https://raw.githubusercontent.com/RagnarGrootKoerkamp/quadrank/HEAD/evals/rank-laptop.csv>
  - WebSearch snippets of https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SEA.2024.21 and https://arxiv.org/html/2405.05214 (pages blocked; drops.dagstuhl.de PDF fetch returned CONNECT 403)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/williams-cs/spider`) · [data/wave9/enrich/raw/github_com_williams_cs_spider.json](../../../data/wave9/enrich/raw/github_com_williams_cs_spider.json) (enrichment confidence 0.6)

</details>
