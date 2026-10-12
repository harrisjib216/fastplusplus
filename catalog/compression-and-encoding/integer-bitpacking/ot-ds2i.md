# ds2i (Partitioned Elias-Fano and OptPFor indexes)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Research C++ library of compressed posting-list encodings (partitioned Elias-Fano, OptPFD, Varint-G8IU, Interpolative, QMX) for inverted-index query experiments.

| | |
|---|---|
| **Beats** | OptPFD (OptPFor), Interpolative coding, Varint-G8IU, SIMD-BP128 era codecs |
| **Claimed result** | Paper (SIGIR 2014, read via WebSearch snippets only; PDF blocked): partitioned Elias-Fano indexes are slightly larger but significantly faster than Interpolative, both faster and smaller than OptPFD, and slightly slower but significantly smaller than Varint-G8IU. No numbers read. |
| **Workload** | Query processing time and index size on compressed inverted indexes (Gov2/ClueWeb09-style collections) for Elias-Fano, partitioned Elias-Fano, OptPFD and Interpolative. |
| **Metric** | throughput |
| **Adoption** | 150 stars |
| **Last commit** | 2018-01-27 |
| **Links** | [repository](https://github.com/ot/ds2i) · [benchmark](http://groups.di.unipi.it/~ottavian/files/elias_fano_sigir14.pdf) |

## Verdict

No benchmark numbers were readable this session: the SIGIR 2014 paper PDF host (groups.di.unipi.it) and the later Clustered Elias-Fano and survey papers (pages.di.unipi.it, iris.cnr.it) are blocked, and search snippets only say partitioned Elias-Fano gives the best compression/query-time trade-off on Gov2 and ClueWeb09, with Varint-G8IU 2.5 to 3 times larger than Elias-Fano. The repo states only GCC 4.9 or Clang, a CMake Release build and -march=native; no hardware or result tables are in the repo.

## Use it when

- Reproducing or extending the SIGIR 2014 / WSDM 2015 inverted-index compression experiments on Gov2- or ClueWeb09-style collections.
- Sorted docID lists where random access and next_geq skipping (conjunctive queries, WAND) matter as much as sequential decode.
- Studying space/time trade-offs between Elias-Fano family encodings and block codecs (OptPFD, Varint-G8IU, Interpolative, QMX) on one harness.
- Lifting the partitioned_sequence or compact_elias_fano templates into your own monotone-sequence store, given Apache-2.0 licensing.

## Skip it when

- Production search engines: unmaintained since 2018; its maintained fork PISA (pisa-engine/pisa) carries the same codecs.
- Non-monotone integer arrays or general bit-packing: the Elias-Fano types need sorted sequences; FastPFor, simdcomp or TurboPFor fit generic data.
- Lists with duplicate values: open PR #16 (2022) reports that partitioned_sequence construction breaks when a partition cut falls between two equal values.
- Projects that cannot take Boost (iostreams, unit_test_framework, filesystem, system) plus three git submodules and -march=native builds.
- Large 64-bit universes: positions in optimal_partition are uint32_t (posting_t), and a third-party fork (ncook111/ds2i_u64) exists only to add 'bugfixes to allow u64 pef encoding/decoding'.

## How it is fast

Partitioned Elias-Fano (SIGIR 2014) splits each list into chunks, encodes the chunk endpoints with Elias-Fano and each chunk with whichever of Elias-Fano, a ranked bitvector or an implicit all-ones run is smallest (indexed_sequence), with chunk boundaries chosen by an approximately optimal partition (optimal_partition.hpp, sliding cost windows with eps1/eps2 parameters). Elias-Fano enumerators use sampled pointers into the high-bit array plus a linear scan for skips of up to 8 elements, so next_geq skips without decoding whole blocks. The WSDM 2015 tool optimal_hybrid_index picks, per 128-integer block, the codec that best trades space for decode time using a query-log profile and a linear decode-time model.

## Compared with alternatives

Pick it over FastPFor, simdcomp or Stream VByte when the data is sorted posting lists and you need skipping (next_geq) and compression near Elias-Fano bounds rather than raw sequential decode speed; versus opt_vbyte (also optimally partitioned, but VByte chunks) choose ds2i when space matters more than decode speed, and for anything maintained use its fork PISA.

## Integration

| | |
|---|---|
| **Form** | header templates built into command-line tools with CMake (no installable library target) |
| **Dependencies** | Boost &gt;= 1.51 per README (CMake asks for 1.42 with iostreams, unit_test_framework, filesystem, system); git submodules succinct (ot/succinct), FastPFor (ot fork) and stxxl |
| **Minimum toolchain** | C++11, CMake &gt;= 2.8; tested with GCC 4.9 on Linux and Clang on OS X Yosemite |
| **Platforms** | x86-64 (CMake sets -march=native; Varint-G8IU block uses SSSE3 pshufb); other architectures not documented |
| **Thread safety** | not documented; block codecs use thread_local scratch buffers, index builds use stxxl and threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Builds with -march=native unconditionally, so binaries and saved timings are tied to the build machine.
- The README's only numbers (block_mixed 9.955 vs block_optpfor 11.125 mean query time) come from the toy test collection queried with the same queries the model was trained on; the README itself says this is cheating.
- Input must be converted to ds2i's own binary collection format (32-bit little-endian length-prefixed sequences).
- optimal_hybrid_index training needs Python with Numpy, Scipy, Pandas and Theano (dec_time_regression.py).

## Known shortcomings

- Downgraded B to D: no numbers could be read (the SIGIR 2014 PDF on groups.di.unipi.it is blocked); kept as the reference code of the Partitioned Elias-Fano paper. Candidate for a paper-access retier.
- Open PR #16: partitioned_sequence build breaks on duplicate values at a partition cut; uint32_t positions (a third-party fork ncook111/ds2i_u64 carries u64 PEF fixes); forced -march=native; Boost plus three submodules. Still no paper numbers (unipi, iris.cnr.it blocked), so tier D pending a paper-access retier.

## Caveats and trade-offs

Evidence is the SIGIR 2014 best paper (Partitioned Elias-Fano Indexes) and WSDM 2015 paper, not opened here (PDF host blocked); tier D pending a paper read. Speed claim is index query time, not raw decode throughput, and baselines are OptPFD/Interpolative/Varint-G8IU rather than FastPFor/Simple-8b. Tested with GCC 4.9 and Clang on OSX Yosemite; depends on FastPFor, succinct and stxxl submodules plus Boost. Research code, last commit 2018-01-27; its successor is the PISA engine. The paper's own code was first published as ot/partitioned_elias_fano, now folded into ds2i.

Elias-Fano family needs sorted (monotone) sequences, not generic bit-packing; Boost dependency; research code; the experiments repo ot/partitioned_elias_fano is archived-for-history and now part of ds2i.

## Maintenance

Abandoned since 2018 (last commit 2018-01-27; PR #16 open since 2022) but Apache-2.0; the pisa-engine/pisa README calls PISA a fork of ds2i, so that is the maintained route to the same encodings.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now D.
- **Tier reason:** No numbers could be read: benchmark_url was null, the README has no comparison tables (only a toy 9.955 vs 11.125 query mean on test data for block_mixed vs block_optpfor, trained on the same queries), and the SIGIR 2014 paper PDF (groups.di.unipi.it) is EGRESS_BLOCKED. WebSearch snippets only confirm the qualitative claim (faster and smaller than OptPFD, slower but smaller than Varint-G8IU), so D until the paper is read; a paper-access retier would likely restore B.
- **Verifier notes:** Not rejected: SIGIR 2014 best-paper code, widely referenced (basis of PISA), despite 150 stars. License Apache-2.0 confirmed from LICENSE; last commit 2018-01-27 (abandoned) confirmed. Candidate for a paper-access retier in an environment that reaches di.unipi.it or ACM.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/ot/ds2i>
  - <https://github.com/ot/ds2i/commits>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/README.md>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/ot/ds2i>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/README.md>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/index_types.hpp>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/partitioned_sequence.hpp>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/uniform_partitioned_sequence.hpp>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/compact_elias_fano.hpp>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/block_codecs.hpp>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/optimal_partition.hpp>
  - <https://raw.githubusercontent.com/ot/ds2i/HEAD/freq_index.hpp>
  - <https://github.com/ot/ds2i/issues?q=is%3Aissue>
  - <https://github.com/ot/ds2i/issues/2>
  - <https://github.com/ot/ds2i/pulls?q=is%3Apr>
  - <https://github.com/ot/ds2i/pull/16>
  - <https://github.com/ncook111/ds2i_u64>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/README.md>
  - http://groups.di.unipi.it/\~ottavian/files/elias_fano_sigir14.pdf (blocked: host not in allowlist)
  - https://pages.di.unipi.it/pibiri/papers/ii_compression.pdf (blocked: CONNECT 403)
  - https://iris.cnr.it/retrieve/5ac325f7-c86f-43fe-88a6-d8f3cee31654/prod_385702-doc_166152.pdf (blocked: CONNECT 403)
  - https://en.wikipedia.org/wiki/Partitioned_Elias%E2%80%93Fano_indexes (blocked: EGRESS_BLOCKED)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ot/ds2i`) · [data/wave9/enrich/raw/github_com_ot_ds2i.json](../../../data/wave9/enrich/raw/github_com_ot_ds2i.json) (enrichment confidence 0.65)

</details>
