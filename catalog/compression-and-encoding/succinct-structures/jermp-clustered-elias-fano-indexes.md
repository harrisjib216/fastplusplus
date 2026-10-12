# Clustered Elias-Fano Indexes (CPEF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Research inverted-index codec that encodes clusters of posting lists against a shared reference list; smaller than partitioned Elias-Fano.

| | |
|---|---|
| **Beats** | Partitioned Elias-Fano (PEF) and Binary Interpolative Coding (BIC) inverted index compression |
| **Claimed result** | CPEF 4.23 bits per posting vs PEF 5.15 (+17.86%) and BIC 4.60 (+8.04%). Space only. |
| **Workload** | Space of inverted index posting lists on a Gov2 sample, bits per posting. |
| **Metric** | memory |
| **Compiler and flags** | gcc 5.4.1, CMake Release with -std=c++11 -march=native (from CMakeLists.txt) |
| **Adoption** | 14 stars |
| **Last commit** | 2018-06-04 |
| **Links** | [repository](https://github.com/jermp/clustered_elias_fano_indexes) · [benchmark](https://github.com/jermp/clustered_elias_fano_indexes) |

## Verdict

On the 244-list Gov2 sample checked into test_data, the README reports 4.23 bits per posting for the clustered index against 5.15 for partitioned Elias-Fano (+17.86%) and 4.60 for Binary Interpolative Coding (+8.04%), all built by this repo's ds2i-based tools with gcc 5.4.1 and -march=native; space does not depend on the CPU, and no CPU model is given. The full Gov2/ClueWeb09 results and any query-time comparison are only in the TOIS 2017 paper, which could not be opened here.

## Use it when

- Read-only inverted index (Gov2/ClueWeb-style docID + frequency postings) where index size matters more than build time and you can afford a clustering step.
- Reproducing or extending the TOIS 2017 clustered Elias-Fano experiments inside a ds2i-derived codebase.
- Collections with many long, overlapping posting lists, where a shared reference list removes redundancy that per-list codecs (PEF, BIC) cannot see.

## Skip it when

- As a general integer or bitvector library: it is tied to ds2i's posting-list formats, Boost and command-line tools, with no standalone API or packaging.
- When query latency is the priority: decoding merges two Elias-Fano segments plus a reference lookup per posting, and the README publishes no query-time numbers against PEF.
- Updatable indexes: construction is offline and needs the whole collection plus a positions file and a gzip'd cluster file.
- New projects needing modern toolchains: the build forces -std=c++11, uses std::result_of and std::iterator (removed or deprecated in later standards), Boost.Thread experimental executors, and was tested only with gcc 5.4.1 on Ubuntu.

## How it is fast

The gain is space, not speed. Each list is split into the part shared with the cluster's reference list (stored as a 'mapped intersection': ranks inside the reference, a much smaller universe) and a residual; both segments are encoded with partitioned Elias-Fano (optimal_partition from ds2i), so next_geq still works by skipping in both segments and merging. Reference lists are chosen per cluster either by docID frequency in the cluster (fb) or by bits saved (sb), and compute_clusters splits lists recursively with 2-means (k-means++ seeding, 1 - cosine similarity over inverse-term-frequency weighted docIDs) restricted to postings in Elias-Fano-coded blocks.

## Compared with alternatives

Pick it over Sliced Indexes (jermp/s_indexes) when the goal is the smallest docID+frequency inverted index rather than fast intersections; s_indexes beats PEF on intersection time, while CPEF beats PEF and BIC on bits per posting.

## Integration

| | |
|---|---|
| **Form** | source-drop (CMake-built executables plus headers; no installable library) |
| **Dependencies** | Boost &gt;= 1.58 (iostreams, unit_test_framework, filesystem, system, thread), git submodules ot/succinct, ot/FastPFor and stxxl |
| **Minimum toolchain** | C++11, CMake &gt;= 2.8; tested only with gcc 5.4.1 on Linux Ubuntu |
| **Platforms** | Linux x86-64 tested (builds with -march=native, uses mmap/posix_madvise); others not documented |
| **Thread safety** | not documented; building uses a Boost thread pool sized by DS2I_THREADS, and the mapped index is read-only |
| **Drop-in for the baseline** | partial: same ds2i collection input format and enumerator interface as ds2i's PEF index (queries.cpp runs both), but needs an extra clustering step and separate build tools |

## Gotchas

- Possible edge-case decoding bug (read in clustered_freq_index.hpp and clustered_sequence.hpp, not reproduced): add_reference writes the reference length only when ceil_log2(size) &gt; 1 and the reader then assumes size 1, so a 2-element reference decodes as length 1; a 1-element reference calls write_gamma_nonzero(0), which underflows to write_gamma(UINT64_MAX). Real clusters with MAX_REF_SIZE around 800,000 should not hit this; run the builders with --check.
- clustered_freq_index::warmup() is an empty stub ('XXX implement this') while ds2i indexes prefetch their lists, so queries.cpp timings of clustered_opt vs PEF are not warmed up the same way.
- No input validation: binary collections, positions and cluster files are trusted (atoi/stoull parsing, unchecked offsets into the mmapped file); a malformed file reads out of bounds. queries.cpp also dereferences argv[1..3] without checking argc.
- README names the positions file test_collection.lists_positions.gz but the example command uses test_collection.plists_positions.gz; scripts/filter_plists.py, which generates positions files for other collections, is Python 2.

## Known shortcomings

- Space win (4.23 vs PEF 5.15 bits per posting) from the TOIS 2017 paper, which is blocked here and was not opened. Flags -march=native -std=c++11 Release; no CPU stated. LICENSE is an Apache-2.0 notice, so copyable.
- Possible edge-case decoding bug read in source, not reproduced: add_reference skips writing the length when ceil_log2(size) &lt;= 1, so a 2-element reference decodes as length 1, and a 1-element reference calls write_gamma_nonzero(0), which underflows to write_gamma(UINT64_MAX). warmup() is an empty stub, so query timings against PEF are not warmed alike. No input validation (atoi, unchecked mmap offsets; queries.cpp reads argv without checking argc). Builds only with -std=c++11 on gcc 5.4.1 (Boost experimental executors, std::result_of); scripts/filter_plists.py is Python 2; README file names mismatch. Space-only claim; query speed is only in the paper.

## Caveats and trade-offs

README numbers come from a 244-list Gov2 sample checked into test_data, not the full Gov2/ClueWeb09 of the paper. The TOIS 2017 paper was not opened (pages.di.unipi.it is blocked). Space win, not speed. Based on ds2i, with git submodules (FastPFor, stxxl, succinct) under their own licences. The LICENSE file holds the Apache-2.0 notice text, not the full licence.

Needs clustering step and Boost; built on ds2i with submodules (FastPFor, stxxl, succinct); query-time cost versus PEF is in the paper, not the README.

## Maintenance

Abandoned since 2018-06-04 (18 commits, 14 stars, no open issues) but Apache-2.0; usable as research code to vendor into a ds2i/PISA-style engine, not as a maintained dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** README table shows CPEF 4.23 bits per posting vs PEF 5.15 (+17.86%) and BIC 4.60 (+8.04%) on the in-repo Gov2 sample; the method is peer-reviewed (Pibiri and Venturini, ACM TOIS 2017). Not A: the repo states gcc 5.4.1 and CMakeLists flags but no CPU model (the space metric does not depend on hardware anyway).
- **Verifier notes:** The record said no licence, but the LICENSE file is an Apache-2.0 notice (Copyright 2017 Pibiri, Venturini), so usability becomes copyable. 14 stars, last commit 2018-06-04, abandoned. The tier rests on the peer-reviewed paper, which is real (search result) but was not opened.
- **Fields the verifier corrected:** `license`, `usability`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper (ACM TOIS 2017)
- **Pages the verifier opened:**
  - <https://github.com/jermp/clustered_elias_fano_indexes>
  - <https://github.com/jermp/clustered_elias_fano_indexes/commits>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/jermp/clustered_elias_fano_indexes>
  - <https://github.com/jermp/clustered_elias_fano_indexes/tree/master/scripts>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/clustered_sequence.hpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/clustered_freq_index.hpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/clustered_index_types.hpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/clustered_binary_collection.hpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/create_clustered_freq_index_fb.cpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/compute_clusters.cpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/queries.cpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/configuration.hpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/integer_codes.hpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/util.hpp>
  - <https://raw.githubusercontent.com/jermp/clustered_elias_fano_indexes/HEAD/scripts/filter_plists.py>
  - WebSearch: "Clustered Elias-Fano Indexes" Pibiri Venturini TOIS abstract (snippets of dl.acm.org/doi/10.1145/3052773 and semanticscholar; pages not opened)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jermp/clustered_elias_fano_indexes`) · [data/wave9/enrich/raw/github_com_jermp_clustered_elias_fano_indexes.json](../../../data/wave9/enrich/raw/github_com_jermp_clustered_elias_fano_indexes.json) (enrichment confidence 0.75)

</details>
