# Mison (speculative structural-index JSON parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · ⚪ unknown

> VLDB 2017 JSON parser (no public code) that jumps straight to queried fields; reports 5.5-9.1x over best of RapidJSON/Jackson/Gson.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | Paper Sec 6.1.1 / Fig. 8 (Twitter, Q1-Q8, single thread, throughput in GB/s): 'Mison is between 5.5 and 9.1 times faster than the best competitor in this experiment. The best case for Mison (8\~9X) is for simple queries on mandatory fields (Q1-Q4)'. RapidJSON is one of the three competitors, so Mison is at least 5.5x faster than RapidJSON on Q1-Q8 (derived from page data; in the Fig. 8 bars Jackson, not RapidJSON, is the best competitor). Sec 6.1.2 (Fig. 9, GitHub dataset, all 31 fields, no projection push-down): Mison 'still outperforms the best existing JSON parser (Jackson) by a factor of 2'. Sec 6.1.4 / Fig. 11 (Twitter, first+last field query): basic (non-speculative) Mison beats Jackson by 3.6x, speculative Mison by 10.2x. |
| **Workload** | Single-threaded field-projection queries over real-world JSON loaded into memory: Twitter Q1-Q8 (records have 25-30 top-level fields and a nested user object of 37-38 fields), Yelp business records (16 top-level fields), and GitHub user records (31 fixed fields). The paper compares parsing throughput (GB/s) of Mison against Gson, Jackson and RapidJSON, each using its streaming-mode API. It also runs TPC-H queries through Spark with Mison vs Jackson. |
| **Metric** | throughput |
| **Hardware** | 3.5GHz Intel Xeon E5-1620 v3 (the paper calls it 'Broadwell-EP'), 16GB DDR3, 64-bit Windows 10; single-threaded runs with the JSON data preloaded into memory (I/O excluded) |
| **Compiler and flags** | Mison is a C++ static library; the first structural-index step uses 256-bit AVX2 SIMD and the bit-parallel steps use 64-bit instructions. The paper does not state the compiler, its version, or the flags for Mison or RapidJSON, nor the JVM version used for Jackson and Gson. |
| **Adoption** | Published VLDB 2017 (PVLDB Vol. 10, No. 10, pp. 1118-1129) by Microsoft Research and University of Pittsburgh; no official source release found |
| **Links** | [benchmark](http://www.vldb.org/pvldb/vol10/p1118-li.pdf) |

## Verdict

The authors' own single-threaded benchmark ran field-projection queries on a 3.5 GHz Xeon E5-1620 v3 under Windows 10, with data preloaded into memory and no compiler or flags stated. On Twitter records, Mison was 5.5-9.1x faster than the best of Jackson, Gson and RapidJSON (all using their streaming APIs; Jackson, not RapidJSON, was the strongest), and about 2x faster than Jackson when all 31 GitHub fields were read. No one has reproduced the full parser; Sparser's authors reimplemented only the index step, found Mison over 2 GB/s per core and over 5x RapidJSON, and noted that the implementation 'is not open source'.

## Use it when

- In-memory scans of newline-delimited record streams where a query needs 1-2 fields out of dozens (the Twitter records had 25-30 top-level fields plus a 37-38-field user object). That is where the paper shows its 8-9x best case.
- Record collections that share a few layouts in a stable field order, such as the paper's GitHub user records (31 fields, always in the same order) or Twitter's user field, which sat at position 11 in 80.7% of tweets and 12 in the rest. Speculation pays off there.
- Selective filters that can be evaluated before projection. In the Spark TPC-H runs, queries with 0.5-3.7% selectivity on lineitem ran 16.3-32.5x faster with Mison than with Spark's Jackson path.
- As a design reference for a query-on-raw-JSON engine. The leveled colon/comma bitmap index is implemented in C++ in AutomataLab/Pison (MIT). The full algorithm, including pattern-tree speculation, exists in the Rust crate pikkr (MIT).

## Skip it when

- You need a maintained library. No official code exists, and the reimplementations are research or hobby code: pikkr's last push was 2017, and its open issue #76 reports it doesn't build on Rust 1.80. The misosoup README says 'DO NOT use for production use'. gomison contains only a README and a LICENSE.
- Full-document parsing, DOM building or serialization. With all 31 GitHub fields read, the lead over Jackson falls to about 2x. Mison has no writer and builds no tree.
- Untrusted or possibly malformed input. The simdjson paper notes that Mison does not validate documents and assumes pure ASCII rather than UTF-8. pikkr, which follows the same design, accepts {"x":0,} and returns the value '0,'.
- Highly irregular or schema-drifting data, optional fields, and arrays. In the paper, Q5 (a field with 7 root-level patterns) was slower, and Q6-Q8 needed Bloom filters or leveled comma bitmaps, which cut Mison's advantage.
- Data you will query many times. The paper itself finds converting to Parquet faster (Spark+Parquet was 1.6x faster than Spark+Mison, geometric mean over TPC-H SF1, not counting about 100 s of conversion). A single huge JSON document is also a poor fit: Mison indexes each record serially, and Pison was built to parallelize that case.

## How it is fast

First it builds a per-record structural index. AVX2 compares 32 bytes at a time against quote, backslash, colon and braces (and brackets or commas when arrays are queried), and the results become bitmaps. 64-bit bit tricks (x&(x-1), x&-x, x^(x-1), popcnt) then drop escaped quotes, build a string mask, and use a brace stack to split colons into 'leveled colon bitmaps', one per nesting depth, built only down to the deepest queried field. The k-th set bit therefore locates the k-th field's key/value boundary without tokenizing. Second, it parses speculatively. 'Pattern trees', trained on a sample (the first 1,000 records in the paper, keeping patterns seen more than 1% of the time), predict each queried field's ordinal position. The parser jumps there, checks that the key name matches, tries less frequent patterns if it doesn't, and falls back to scanning every colon at that level if none match. In the paper's Fig. 11, index-only (basic) Mison was 3.6x faster than Jackson and speculation raised that to 10.2x.

## Compared with alternatives

For shipping code, use simdjson's On-Demand API: the simdjson paper says it follows Mison's structural-index outline but with branchless stage-1 code, and On-Demand skips fields you never access while validating the ones you use. Reach for Mison, in practice pikkr or Pison, only to study or reproduce pattern-tree speculation and leveled-bitmap projection. For full parsing or writing, yyjson or glaze fit better.

## Integration

| | |
|---|---|
| **Form** | static lib (per the paper; never released, no public source or binary) |
| **Dependencies** | not documented (unreleased) |
| **Minimum toolchain** | not documented: the paper gives no compiler, version or flags (C++, tested on 64-bit Windows 10). The closest runnable code has its own requirements: Pison builds with g++ 7.4+ using -std=c++11 -mavx2 -mpclmul on Linux, and pikkr needs Rust nightly with target-cpu=native. |
| **Platforms** | x86-64 with AVX2 (the character-classification step uses 256-bit AVX2; the other steps use 64-bit integer ops plus popcnt). It was evaluated only on a Xeon E5-1620 v3 under Windows 10. |
| **Thread safety** | not documented. The paper says only that separate threads over independent data partitions scaled near-linearly (results omitted). Each parser carries mutable training and pattern-tree state. |
| **Drop-in for the baseline** | no |

## Gotchas

- Keys are assumed unique within an object (the paper states this assumption), and input is assumed to be ASCII. Neither is checked.
- A missing queried field makes Mison either skip the whole record or return null, depending on configuration. Choosing skip silently drops rows; the Anghagaed/MISON reimplementation lists exactly this as a known bug compared with Spark.
- Speculation depends on a one-time training sample, and patterns below the weight threshold are pruned. The paper describes no retraining, so if the data layout drifts, every record falls back to the slower basic parse.
- The training cost is included in the paper's timings, but the paper does not report how much of the total it is.

## Caveats and trade-offs

No official Mison source was found: the MSR publication page and the paper link no code or artifact. Only unofficial reimplementations exist, none benchmarked against the paper: pikkr/pikkr (Rust, 641 stars, MIT), ubnt-intrepid/misosoup (Rust, 9 stars), leocassarani/mison (Rust, 10 stars, no license), Anghagaed/MISON (21 stars, no license) and indiependente/gomison (Go, 0 stars). The compiler and flags are unstated, and in Fig. 8 RapidJSON (SAX/streaming API on Windows) is slower than Java's Jackson, so the C++ comparison point may not be well tuned. The paper calls the E5-1620 v3 'Broadwell-EP', but v3 Xeon E5 parts are Haswell-EP (a 2014-era CPU). The speedups rely on projection/filter push-down; when all fields are parsed the gain drops to about 2x over Jackson.

Requires an offline training phase to build 'pattern trees' from sample data before speculative parsing works well; benefit shrinks as the fraction of queried fields grows (Fig. 12) and for highly irregular/schema-varying JSON; only helps analytical/partial-field workloads, not full-document parse+build (Sec 6.1, 'if all fields are needed... [binary formats are] still the most efficient approach').

## Maintenance

Nothing was ever released: the MSR page carries only the PDF, and Microsoft's FishStore used Mison in its SIGMOD 2019 paper but ships simdjson in the open-source repo, so treat Mison as a reference design whose nearest usable code is pikkr (Rust, MIT, dormant since 2017) or Pison (C++, MIT, index only, no speculation).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 10(10) 2017 paper whose Sec 6.1 benchmarks Mison against RapidJSON (plus Jackson and Gson). It reports Mison 5.5-9.1x faster than the best competitor on Twitter Q1-Q8 (Fig. 8) and states the CPU (Xeon E5-1620 v3). No code, compiler or flags are published, so it cannot be A. Under this verifier's rubric that is B, the same tier the wave-3 no-code ASPLOS paper StreamTok received.
- **Verifier notes:** I raised the tier from C to B. The search prompt (faster-than-std-agent-prompt.md:97) says no-code papers go in as C, but this verifier rubric makes a peer-reviewed paper B, and the wave-3 StreamTok precedent (no code) was B. If the orchestrator wants the no-code cap to win, set C. All quoted numbers (5.5-9.1x, 8-9x, 2x, 3.6x, 10.2x) appear verbatim in the paper. The only error was the figure reference for the 2x claim: it is Sec 6.1.2 / Fig. 9, not Fig. 10.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol10/p1118-li.pdf>
  - <https://www.microsoft.com/en-us/research/publication/mison-fast-json-parser-data-analytics/>
  - <https://github.com/ubnt-intrepid/misosoup>
  - <https://github.com/indiependente/gomison>
  - <https://github.com/pikkr/pikkr>
  - <https://github.com/leocassarani/mison>
  - <https://github.com/Anghagaed/MISON>
- **Sources the enricher read:**
  - <http://www.vldb.org/pvldb/vol10/p1118-li.pdf>
  - <https://www.microsoft.com/en-us/research/publication/mison-fast-json-parser-data-analytics/>
  - <https://api.crossref.org/works?query.bibliographic=Mison%20A%20Fast%20JSON%20Parser%20for%20Data%20Analytics&rows=3>
  - <https://arxiv.org/pdf/1902.08318>
  - <http://www.vldb.org/pvldb/vol11/p1576-palkar.pdf>
  - <https://github.com/pikkr/pikkr>
  - <https://github.com/pikkr/pikkr/blob/master/src/pikkr.rs>
  - <https://github.com/pikkr/pikkr/issues>
  - <https://github.com/pikkr/pikkr/issues/5>
  - <https://github.com/pikkr/pikkr/issues/9>
  - <https://github.com/pikkr/pikkr/issues/72>
  - <https://github.com/pikkr/pikkr/issues/76>
  - <https://github.com/ubnt-intrepid/misosoup>
  - <https://github.com/leocassarani/mison>
  - <https://github.com/Anghagaed/MISON>
  - <https://github.com/indiependente/gomison>
  - <https://github.com/AutomataLab/Pison>
  - <https://github.com/AutomataLab/Pison/blob/master/makefile>
  - <https://github.com/AutomataLab/Pison/blob/master/src/SerialBitmap.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/SerialBitmapIterator.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/ParallelBitmapIterator.cpp>
  - <https://github.com/AutomataLab/Pison/blob/master/src/BitmapIterator.h>
  - <https://github.com/AutomataLab/JSONSki>
  - <https://github.com/stanford-futuredata/sparser>
  - <https://github.com/microsoft/FishStore>
  - <https://github.com/simdjson/simdjson/blob/master/doc/ondemand_design.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `paper:mison-speculative-structural-index-json-parser`) · [data/wave4/enrich/raw/paper_mison_speculative_structural_index_json_parser.json](../../../data/wave4/enrich/raw/paper_mison_speculative_structural_index_json_parser.json) (enrichment confidence 0.8)

</details>
