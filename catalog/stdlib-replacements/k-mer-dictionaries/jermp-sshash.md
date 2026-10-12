# SSHash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [k-mer dictionaries](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Compressed static DNA k-mer dictionary: \~5x smaller than Pufferfish, 1.6-2.4x faster streaming lookups, but slower random lookups.

| | |
|---|---|
| **Beats** | Pufferfish (and dBG-FM, BLight k-mer dictionaries) |
| **Claimed result** | Human dataset, canonical SSHash, from Tables 4-7. Streaming membership: 253 ns/k-mer (high-hit) vs Pufferfish dense 402 and Blight b=0 440; 183 ns/k-mer (low-hit) vs 435 and 1,088. The paper summarizes this as 'comparable to or faster (by 2-3x) than Pufferfish and Blight'. Space: 9.39 bits/k-mer vs Pufferfish dense 45.04 and Blight b=0 20.17. Build: 16.2 min and 17.3 GB peak vs Pufferfish dense 70.7 min and 14.0 GB, and Blight 25.0 min and 7.5 GB. Random lookups: 990 ns positive and 854 ns negative, which is slower than Pufferfish dense (720 and 519) but faster than Blight b=0 (1,780 and 1,610). |
| **Workload** | Exact membership/lookup queries over billions of DNA k-mers (human and bacterial pangenome datasets) using an MPHF (PTHash) plus minimizer-based bucketing, benchmarked single-threaded. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-9940X @ 3.30 GHz, 128 GB RAM, single core used; Ubuntu 19.10, Linux kernel 5.3.0, 64-bit |
| **Compiler and flags** | gcc 11.2.0, -O3 -march=native |
| **Adoption** | 109 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/jermp/sshash) · [benchmark](https://pmc.ncbi.nlm.nih.gov/articles/PMC9235479/) |

## Verdict

In the 2022 Bioinformatics paper (gcc 11.2.0 -O3 -march=native, Intel i9-9940X, one thread, human genome with 2.5 billion 31-mers), canonical SSHash answered streaming membership in 253/183 ns per k-mer (high/low hit rate), against 402/435 ns for Pufferfish dense and 440/1,088 ns for BLight. It used 9.39 bits/k-mer (vs 45.04 and 20.17) and built in 16.2 min (vs 70.7 and 25.0), but its random lookups (990/854 ns) were slower than Pufferfish dense (720/519 ns); no standard-library baseline was involved, and only the SSHash side of that harness is public.

## Use it when

- Static sets of 10^8 to 10^10 DNA k-mers (bacterial pangenomes, human, HPRC) built from unitigs/eulertigs, where you need k-mer-to-ID and ID-to-k-mer, e.g. as the k-mer index inside a read mapper (the repo carries merged PRs for submodule integration into COMBINE-lab's piscem).
- Streaming membership over FASTQ reads, where consecutive k-mers overlap: v6 measures 76 ns/k-mer on Human k=31 (high-hit), against 266 ns for SBWT and 1,176 ns for FMSI on the same hardware in jermp/kmer_sets_benchmark.
- Memory-constrained indexing: 7.4-10.6 bits/k-mer at k=31 and 3.8-7.6 at k=63 in the current benchmarks (2.75 GB for human k=31), with an --mmap option to query the index from disk.
- Workloads that need Access (rank to k-mer) or navigational queries: Access takes 0.35 us/k-mer on Human k=31, against 10.81 us for SBWT and 18.62 us for FMSI.
- Pipelines that rebuild often: human k=31 builds in 2:35 with 64 threads under a 16 GB RAM cap, using an external-memory builder with a RAM limit (-g) and a temp directory (-d).

## Skip it when

- Isolated random point lookups with RAM to spare: in the 2022 paper Pufferfish dense answered them faster (720/519 ns positive/negative vs 990/854 ns) while using about 5x the space (45.04 vs 9.39 bits/k-mer).
- When the smallest index matters most: FMSI takes 3.2-4.4 bits/k-mer at k=31, against 7.4-10.6 for SSHash, though its lookups and streaming queries are more than 10x slower.
- Dynamic sets: the index is immutable, so any insert or delete means a full rebuild.
- Raw reads or sequences with duplicate or non-ACGT k-mers: the README requires deduplicated, N-free, one-sequence-per-line input, so you must run GGCAT/BCALM2 first. For membership-only use on inputs with duplicate k-mers (e.g. matchtigs), the author points to SSHash-Lite.
- General keys or tiny sets: it is not a general hash map or MPHF (use PTHash directly for that), and the author says the smallest input worth indexing is a single bacterial genome (issue #33).

## How it is fast

Sparse and skew hashing: consecutive k-mers of the input strings are grouped into super-k-mers by their minimizer, and a PTHash minimal perfect hash is built over the distinct minimizers only (about 6.5x fewer keys than k-mers at k=31, m=20 in the 2022 paper), so a lookup hashes the minimizer to a small bucket of offsets into the 2-bit-packed strings and verifies the k-mer against the text instead of storing k-mers. Singleton buckets resolve with one text comparison, buckets with fewer than 2^6 super-k-mers are scanned, and the rare heavy buckets go to a 'skew index' of per-size-class PTHash functions over the k-mers themselves, which caps string accesses. Streaming queries skip hashing while a read follows a stored string: after a hit the next query k-mer is compared with the next k-mer of the same unitig ('extension'), and v6 memoizes the last minimizer's bucket to shortcut negatives. Since v6 a forward minimizer scheme with a centre-closest tie-break puts a k-mer and its reverse complement in the same bucket, so every lookup is a single probe.

## Compared with alternatives

Over RSHash, which claims 1.4x faster streaming on average, pick SSHash for maturity and features: Bioconda packaging, a Rust port, releases since 2022, navigational queries, compressed weights and k up to 63 (RSHash has 8 stars, and its README builds with g++-14 and seqan3). Over BLight, pick SSHash when space and query speed matter: in the 2022 paper it used 9.39 vs 20.17 bits/k-mer and was faster on both streaming and random lookups, though BLight's build peaked at less RAM (7.5 vs 17.3 GB).

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | PTHash (git submodule, which brings bits, essentials, fastmod, xxHash and mm_file), zlib; CityHash vendored in external/ |
| **Minimum toolchain** | C++17, CMake 3.5+; CI builds with GCC 11-14 and Clang 16-18 on Ubuntu; k up to 63 needs __uint128_t (GCC/Clang) |
| **Platforms** | x86-64 (CMake always adds -mavx2 -mbmi2, so AVX2/BMI2 CPUs are required) and aarch64 (builds since the Sep 2025 fix for issue #77); tested on Linux with gcc and macOS with clang; Windows not documented |
| **Thread safety** | Not documented. Build is multi-threaded (-t) with a RAM cap. The dictionary's query methods are const; streaming_query keeps mutable per-stream state, so use one per thread. All published query benchmarks are single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- The builder does not screen its input: build with the same k that produced the unitigs, and supply deduplicated, ACGT-only sequences with one per line. Use --check to verify the built index.
- The default 2-bit nucleotide encoding is non-standard (A=00, C=01, T=10, G=11), so passing packed-integer k-mers from other tools needs -DSSHASH_USE_TRADITIONAL_NUCLEOTIDE_ENCODING=On. Max k (31 or 63) is also fixed at compile time.
- Performance and size depend on the minimizer length m, which you must choose. The builder prints a warning only in --verbose mode when m &lt; ceil(log4(N))+1, and the benchmarks tune m per dataset (19-21 for k=31, 23-31 for k=63).
- The index format is versioned: v6.0.0 (Aug 2026) removed the canonical/regular modes, and loading an index with a different major version throws 'SSHash index needs rebuilding'.

## Known shortcomings

- Benchmarked only against other k-mer dictionaries (Pufferfish, BLight, SBWT, FMSI), never against std::unordered_map or a standalone MPHF. Pufferfish (dense) is faster on random lookup; SSHash's wins are streaming queries, space and build time.

## Caveats and trade-offs

All comparisons are against other k-mer dictionaries (dBG-FM, Pufferfish, BLight; later SBWT and FMSI), never against std::unordered_map, CMPH, BBHash or a bare MPHF. Pufferfish dense is faster than SSHash on random lookups. SSHash wins on space (2-5x), on streaming queries (up to 2-3x) and on build time. No public harness or commit pins exist for the competitor runs in the 2022 paper. The newer benchmarks (jermp/kmer_sets_benchmark, benchmarks/README.md, Pibiri and Patro 2026) cover only SBWT and FMSI.

Specialized to fixed-length DNA k-mer keys (not a general-purpose MPHF library); static/immutable once built; relies on PTHash internally so inherits its construction-time/space tradeoffs; needs minimizer sampling tuned per dataset.

## Maintenance

Actively maintained (v6.0.0 shipped 2026-08-29 with a breaking index-format change; last commit 2026-09-03), MIT-licensed, on Bioconda with a Rust port, and consumed as a CMake static-library target with submodules rather than a header-only drop.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): reject; tier before verification A, tier now B.
- **Tier reason:** This tier covers only the off-category comparison. The peer-reviewed paper (Bioinformatics 38 Suppl. 1, Sec. 5, Tables 3-7) states gcc 11.2.0, -O3 -march=native and an Intel i9-9940X. Only the SSHash side of the harness is public (src/bench.cpp, src/query.cpp, script/benchmark_dictionary.sh at v1.0.0). The Pufferfish, BLight and dBG-FM runs have no published scripts or pinned commits, so the tier is B, not A.
- **Verifier notes:** The record's absolute numbers (990/854 ns, 9.39 bpk, 16.2 min, 17.3 GB) all appear in the paper, but they are not wins: SSHash is slower than Pufferfish dense on random lookup. The rejection is on category scope only. SSHash is notable (Bioconda, Rust port) and would qualify under a k-mer-dictionary category. Repo metadata checked: MIT license, not a fork, not archived, 109 stars, last commit 2026-09-03 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://pmc.ncbi.nlm.nih.gov/articles/PMC9235479/>
  - <https://github.com/jermp/sshash>
  - <https://github.com/jermp/sshash/blob/master/benchmarks/README.md>
  - <https://github.com/jermp/sshash/tree/v1.0.0>
  - <https://github.com/jermp/kmer_sets_benchmark>
  - <https://pmc.ncbi.nlm.nih.gov/articles/PMC13340181/>
  - <https://www.biorxiv.org/content/10.1101/2024.11.26.625346v1.full.pdf>
- **Sources the enricher read:**
  - <https://github.com/jermp/sshash>
  - <https://github.com/jermp/sshash/blob/master/README.md>
  - <https://github.com/jermp/sshash/blob/master/benchmarks/README.md>
  - <https://github.com/jermp/sshash/blob/master/CMakeLists.txt>
  - <https://github.com/jermp/sshash/blob/master/.gitmodules>
  - <https://github.com/jermp/sshash/blob/master/.github/workflows/build.yml>
  - <https://github.com/jermp/sshash/blob/master/include/dictionary.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/dictionary_types.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/sparse_and_skew_index.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/minimizers_control_map.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/constants.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/streaming_query.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/util.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/kmer.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/hash_util.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/minimizer_iterator.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/offsets.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/cover/parse_file.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/builder/util.hpp>
  - <https://github.com/jermp/sshash/blob/master/include/builder/dictionary_builder.hpp>
  - <https://github.com/jermp/sshash/blob/master/src/builder/build.cpp>
  - <https://github.com/jermp/sshash/blob/master/src/builder/encode_strings.cpp>
  - <https://github.com/jermp/sshash/blob/master/src/dictionary.cpp>
  - <https://github.com/jermp/sshash/blob/master/src/query.cpp>
  - <https://github.com/jermp/sshash/blob/master/tools/build.cpp>
  - <https://github.com/jermp/sshash/blob/master/tools/query.cpp>
  - <https://github.com/jermp/sshash/issues?q=is%3Aissue>
  - <https://github.com/jermp/sshash/issues/7>
  - <https://github.com/jermp/sshash/issues/10>
  - <https://github.com/jermp/sshash/issues/11>
  - <https://github.com/jermp/sshash/issues/33>
  - <https://github.com/jermp/sshash/issues/42>
  - <https://github.com/jermp/sshash/issues/45>
  - <https://github.com/jermp/sshash/issues/77>
  - <https://github.com/jermp/sshash/pull/89>
  - <https://github.com/jermp/sshash/pull/90>
  - <https://github.com/jermp/sshash/pull/93>
  - <https://github.com/jermp/sshash/pull/94>
  - <https://github.com/jermp/sshash/commit/1e46db4dbe2c4934b42c2cce26f71e245493d438>
  - <https://github.com/jermp/sshash/releases>
  - <https://github.com/jermp/sshash/commits/master>
  - <https://pmc.ncbi.nlm.nih.gov/articles/PMC9235479/>
  - <https://pmc.ncbi.nlm.nih.gov/articles/PMC13340181/>
  - <https://github.com/jermp/kmer_sets_benchmark>
  - <https://github.com/jonsmcode/rshash>
  - <https://github.com/jonsmcode/rshash/blob/master/benchmarks/README.md>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/jermp/sshash`) · [data/wave1-phf/enrich/raw/github_com_jermp_sshash.json](../../../data/wave1-phf/enrich/raw/github_com_jermp_sshash.json) (enrichment confidence 0.8)

</details>
