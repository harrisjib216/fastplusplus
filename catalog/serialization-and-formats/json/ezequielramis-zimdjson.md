# zimdjson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟡 stale

> Zig port of simdjson with streaming and reflection decoding; its On-Demand parser beats simdjson on 3 of 5 author benchmarks.

| | |
|---|---|
| **Beats** | simdjson |
| **Claimed result** | zimdjson (On-Demand) beats simdjson (On-Demand) on 3 of the 5 tasks in bench_ondemand.png: find-system \~1.74 vs \~1.17 GB/s (\~1.5x), top-factions \~1.59 vs \~1.04 GB/s (\~1.5x), coordinates \~1.63 vs \~1.06 GB/s (\~1.5x). simdjson (On-Demand) is faster on top-tweet (\~2.84 vs \~2.64 GB/s) and partial-tweets (\~2.82 vs \~2.43 GB/s). Values are read off the bar chart, and the ratios are derived from page data. |
| **Workload** | On-Demand-style parsing/field extraction over a 626MB systemsPopulated.json dump and twitter.json, measuring GB/s for tasks 'find-system', 'top-factions', 'coordinates', 'top-tweet', 'partial-tweets', run head-to-head against simdjson On-Demand/DOM and yyjson in the project's own benchmark harness. |
| **Metric** | throughput |
| **Hardware** | 3.30GHz Intel Skylake processor |
| **Compiler and flags** | Zig build system (`zig build bench/...`) for all contenders. The simdjson and yyjson C++ benchmarks are compiled through Zig's addCSourceFile (Zig's bundled Clang) with the same standardOptimizeOption mode as the Zig code. The Zig version and optimize mode used for the published charts are not stated. |
| **Adoption** | 174 stars |
| **Last commit** | 2025-04-29 |
| **Links** | [repository](https://github.com/EzequielRamis/zimdjson) · [benchmark](https://github.com/EzequielRamis/zimdjson#performance) |

## Verdict

The author ran their own Linux perf_event harness on a 3.30 GHz Skylake (model not given), with every contender built by `zig build --release=fast` (ReleaseFast, per scripts/bench_ondemand.py). simdjson v3.10.1 was compiled with Zig's bundled Clang, and the Zig version is not recorded. zimdjson's On-Demand FullParser beat simdjson On-Demand by about 1.5x on three extraction tasks over the 626 MB systemsPopulated.json (find-system \~1.74 vs \~1.17 GB/s, for example) but lost both twitter.json tasks. Throughput is file size divided by the mean wall time, including reading the file, over at least 3 runs and up to 10 s.

## Use it when

- A Zig program that pulls a few fields out of large JSON (hundreds of MB, such as the 626 MB EDSM systemsPopulated dump) and wants simdjson On-Demand behaviour without C++ interop.
- A single JSON document too large to hold in memory, or over 4 GiB: StreamParser parses it with constant memory. The README lists this as a feature zimdjson adds on top of simdjson.
- Decoding a known schema into Zig structs. In the author's twitter.json chart, Schema mode runs at \~1.07 GB/s, compared with \~0.83 GB/s for serde_json::from_str and \~0.33 GB/s for std.json.parseFromSlice.
- Builds you control that target x86-64 with AVX/PCLMUL or AArch64, on Linux, macOS or Windows.

## Skip it when

- C or C++ codebases: use simdjson directly. In the author's own chart, simdjson won both twitter.json On-Demand tasks (\~2.84 vs \~2.64 and \~2.82 vs \~2.43 GB/s) and all five DOM tasks (for example find-system \~0.90 vs \~0.80 GB/s).
- Projects on Zig 0.15 or 0.16. main pins Zig 0.14.0 and its API is built on std.io.AnyReader. PR #11 reports that the 0.15.x branch still fails on 0.15.2, and the 0.16 port (PR #13) is unmerged.
- Reading On-Demand fields in a different order from the document. The author's schema chart shows 'On-Demand, Unordered' at \~0.23 GB/s, slower than std.json. The README suggests switching to schema mode to avoid this.
- Binaries that must run on unknown CPUs. SIMD features are fixed at compile time: there is no runtime dispatch (issue #4) and no scalar fallback (issue #3), targets without SIMD fail with a compile error, and architectures other than x86-64 and AArch64 hit @compileError.
- Code that needs an active upstream. The last commit on main is from 2025-04-29 and the last tag, 0.1.1, is from 2025-03-23.

## How it is fast

Stage 1 follows the Langdale-Lemire simdjson design. It classifies characters with nibble-lookup shuffles (inline vpshufb on x86-64, tbl on AArch64). It finds string spans by applying a carry-less-multiply prefix-XOR (vpclmulqdq) to the quote mask, plus odd/even backslash-run arithmetic. It then extracts structural positions into a u32 index with tzcnt/clz loops, processing two 64-byte masks per iteration on x86. On-Demand walks that index lazily and parses only the values you access; the number parser sits in modules named eisel_lemire, digit_comp and BigInt. StreamParser keeps the bytes and a u16/u32 chunk-relative index in mirrored ring buffers (memfd+mmap on POSIX, VirtualAlloc2 placeholders on Windows), which is how memory stays constant.

## Compared with alternatives

Pick zimdjson over simdjson only when your code is Zig or you need constant-memory streaming of one huge document. Pick it over yyjson when you touch only a few fields: in the author's chart, yyjson ran at 0.46-1.72 GB/s and zimdjson On-Demand at 1.59-2.64 GB/s. For Rust or C++, simd-json, simdjson, yyjson or glaze are the natural choices.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | None at runtime (Zig std only). simdjson v3.10.1, yyjson 0.10.0, a RapidJSON fork and test-data archives are lazy dependencies used only by the benchmarks and tests. |
| **Minimum toolchain** | Zig 0.14.0 (minimum_zig_version in build.zig.zon; CI pins 0.14.0). Newer Zig versions need the unmerged 0.15.x branch or community PRs. |
| **Platforms** | Linux, macOS and Windows (streaming needs Windows 10 or later). CPUs: x86-64 with AVX and PCLMULQDQ (VEX-encoded inline asm) or AArch64 (NEON tbl). Vector width comes from the compile target. |
| **Thread safety** | Not documented. Each parser owns its buffers and handles one document at a time, and the docs say to use several parser instances for several documents. There is no internal multithreading (issue #5 is open). |
| **Drop-in for the baseline** | partial — it mirrors simdjson's On-Demand and DOM ideas: in the paired benchmark code, at()/atOrdered() stand in for simdjson's operator[], and it also has getArraySize and raw strings. But it is a Zig-only API with no C/C++ ABI, so moving to it means rewriting call sites in Zig. |

## Gotchas

- On-Demand checks only the parts of the document you read ('validate what you use'), so malformed JSON can parse without error. The OutOfOrderIteration misuse check exists only in Debug builds, so release builds do not report out-of-order access.
- StreamParser returns error.StreamChunkOverflow in three cases: a string or number longer than the chunk (64 KiB by default), a whitespace run longer than the chunk, or a rewind past the current chunk. RawString values become invalid when the chunk advances, and asString results become invalid on the next parse. On macOS each ring buffer is asserted to be at most 4 MiB, which limits chunk_length.
- The README's install line pins tag 0.1.1 (2025-03-23). That tag predates the fix for issue #8, where large structs in schema mode exceed the comptime backward-branch quota. The fix exists only on main (commit aa22af4).
- The benchmark harness is not symmetric. For On-Demand, simdjson calls padded_string::load inside every timed run, allocating a new buffer each time, while zimdjson reuses a buffer pre-sized with expectDocumentSize. For DOM, simdjson uses parser.load. zimdjson DOM loses to simdjson DOM on all five tasks, so part of the \~1.5x On-Demand win on the 626 MB file may come from buffer allocation rather than parsing. This was not measured separately.

## Known shortcomings

- Mixed against simdjson On-Demand: about 1.5x faster on find-system, top-factions and coordinates, but simdjson wins top-tweet and partial-tweets. CPU model, Zig version and optimize mode are not stated, and the two README charts disagree on the same task. Stale since 2025-04.
- Not like-for-like: the simdjson On-Demand harness loads a fresh padded_string inside every timed run while zimdjson reuses a presized buffer; zimdjson's DOM is slower than simdjson's on all 5 tasks. main builds only with Zig 0.14.0; the README's 0.1.1 pin predates the schema-mode fix (#8). No runtime CPU detection or scalar fallback (x86-64 AVX+PCLMUL or AArch64 only). Out-of-order field access runs at about 0.23 GB/s, slower than std.json.

## Caveats and trade-offs

First-party benchmark (project's own repo/author). Numbers are read off bar charts (images), not a table. The CPU is given only as '3.30GHz Intel Skylake' (no model). No Zig version or optimize mode is recorded with the results. The two charts disagree for the same tasks (for example, find-system zimdjson On-Demand is \~2.0 GB/s in bench_ondemand_find_tweet.png but \~1.74 GB/s in bench_ondemand.png), which suggests run-to-run variance. Results depend on the workload, not a uniform win: simdjson On-Demand wins both twitter.json tasks. The author's README note says 'do not trust any benchmark'. The last commit on the default branch is 2025-04-29, and the newest commit on any branch (0.15.x) is 2025-08-24.

Zig-only reimplementation of simdjson's On-Demand API (not usable from C++ directly); mixed results (loses on 2 of 5 published tasks); README itself cautions 'do not trust any benchmark, always verify it yourself'; author also notes zimdjson's unordered On-Demand mode is the slowest of all tested parsers on the schema benchmark.

## Maintenance

Stale: main was last touched on 2025-04-29 and the last tag is 0.1.1 (2025-03-23); Zig 0.15 and 0.16 ports sit in an unmerged branch and in community PRs. It is MIT-licensed pure Zig, so the practical path is to vendor it and pin Zig 0.14.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section has bar charts (docs/assets/bench_ondemand.png and bench_ondemand_find_tweet.png) comparing zimdjson with simdjson DOM/On-Demand and yyjson. The benchmark code is public (bench/&lt;task&gt;/\*.zig and \*.cpp, bench/runner.zig, build/bench.zig), but the CPU is given only as '3.30GHz Intel Skylake' with no model, and no Zig version or optimize mode is stated, so this is first-party partial methodology: C.
- **Verifier notes:** The chart readings in the record match the image within reading error. The last_commit of 2026-04-18 in the record was the repo pushed_at date. The newest commit on the main branch is 2025-04-29 (0.15.x branch: 2025-08-24), both more than 12 months ago, so maintenance_status is now stale. MIT license, not a fork, 174 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/EzequielRamis/zimdjson>
  - <https://github.com/EzequielRamis/zimdjson#performance>
  - <https://raw.githubusercontent.com/EzequielRamis/zimdjson/main/docs/assets/bench_ondemand.png>
  - <https://raw.githubusercontent.com/EzequielRamis/zimdjson/main/docs/assets/bench_ondemand_find_tweet.png>
  - <https://github.com/EzequielRamis/zimdjson/tree/main/bench>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/find-system/simdjson_ondemand.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/find-system/zimdjson_ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/build.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/build/bench.zig>
- **Sources the enricher read:**
  - <https://github.com/EzequielRamis/zimdjson>
  - <https://github.com/EzequielRamis/zimdjson#performance>
  - <https://github.com/EzequielRamis/zimdjson/commits/main>
  - <https://github.com/EzequielRamis/zimdjson/commits/0.15.x>
  - <https://github.com/EzequielRamis/zimdjson/issues?q=is%3Aissue>
  - <https://github.com/EzequielRamis/zimdjson/issues/3>
  - <https://github.com/EzequielRamis/zimdjson/issues/4>
  - <https://github.com/EzequielRamis/zimdjson/issues/5>
  - <https://github.com/EzequielRamis/zimdjson/issues/6>
  - <https://github.com/EzequielRamis/zimdjson/issues/8>
  - <https://github.com/EzequielRamis/zimdjson/issues/9>
  - <https://github.com/EzequielRamis/zimdjson/issues/10>
  - <https://github.com/EzequielRamis/zimdjson/pull/11>
  - <https://github.com/EzequielRamis/zimdjson/pull/12>
  - <https://github.com/EzequielRamis/zimdjson/pull/13>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/build.zig.zon>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/.github/workflows/ci.yaml>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/zimdjson.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/intrinsics.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/common.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/indexer.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/types.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/tokens/iterator.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/tokens/stream.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/ring_buffer.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/src/dom.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/build/bench.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/build/parsers.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/runner.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/template.hpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/traced_allocator.hpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/find-system/zimdjson_ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/find-system/simdjson_ondemand.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/find-system/simdjson_dom.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/find-system/zimdjson_dom.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/top-tweet/zimdjson_ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/top-tweet/simdjson_ondemand.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/top-factions/simdjson_ondemand.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/top-factions/simdjson_dom.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/top-factions/zimdjson_ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/coordinates/simdjson_ondemand.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/coordinates/simdjson_dom.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/coordinates/zimdjson_ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/partial-tweets/simdjson_ondemand.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/partial-tweets/simdjson_dom.cpp>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/partial-tweets/zimdjson_ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/schema/zimdjson_ondemand.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/bench/schema/zimdjson_ondemand_unordered.zig>
  - <https://github.com/EzequielRamis/zimdjson/blob/main/scripts/bench_ondemand.py>
  - <https://raw.githubusercontent.com/EzequielRamis/zimdjson/main/docs/assets/bench_ondemand.png>
  - <https://raw.githubusercontent.com/EzequielRamis/zimdjson/main/docs/assets/bench_schema.png>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ezequielramis/zimdjson`) · [data/wave4/enrich/raw/github_com_ezequielramis_zimdjson.json](../../../data/wave4/enrich/raw/github_com_ezequielramis_zimdjson.json) (enrichment confidence 0.5)

</details>
