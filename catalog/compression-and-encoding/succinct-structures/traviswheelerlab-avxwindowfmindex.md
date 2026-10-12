# AWFM-index (AvxWindowFmIndex)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> C FM-index for DNA/RNA/protein exact k-mer count and locate; paper reports 2-6x faster than SeqAn3's FM-index.

| | |
|---|---|
| **Beats** | SeqAn3 FM-index (built on sdsl-lite) |
| **Claimed result** | Paper abstract (search snippet): count and locate queries faster than SeqAn3's FM-index across comparable memory footprints; when optimized for speed about 2 to 4x faster for nucleotide search and about 2 to 6x faster for amino acid search, and about 4x faster at similar memory footprint with the suffix array on SSD. The per-query-type split (count vs locate) in the original record was not confirmed. |
| **Workload** | Exact-match count and locate k-mer queries on nucleotide and amino acid FM-indexes, thread-parallel. |
| **Metric** | throughput |
| **Hardware** | 32-core Intel Xeon E5-2630 v3 at 2.40 GHz, 64 GB RAM (from search snippet of the paper) |
| **Adoption** | 36 stars |
| **Last commit** | 2024-12-09 |
| **Links** | [repository](https://github.com/TravisWheelerLab/AvxWindowFmIndex) · [benchmark](https://almob.biomedcentral.com/articles/10.1186/s13015-021-00204-6) |

## Verdict

The Algorithms for Molecular Biology 2021 paper (read only through search snippets; BMC, bioRxiv, PMC and OSTI copies are blocked here) reports exact-match count and locate about 2-4x faster than SeqAn3's FM-index for nucleotides and 2-6x for amino acids in a single-threaded context when configured for speed, about 4x at similar memory with the suffix array on SSD, and 35-50% strong-scaling efficiency up to 20 threads, on a 32-core Xeon E5-2630 v3. The SeqAn3 version, compiler and flags were not confirmed, and the repo carries the AWFM timing driver but not the SeqAn3 side.

## Use it when

- Large batches of exact-match k-mer count or locate queries against a genome or protein database, where throughput across many queries matters more than single-query latency.
- Nucleotide or amino-acid alphabets only; queries free of ambiguity codes (N, X and the like).
- x86-64 with AVX2 or aarch64 with Neon, built with GCC and OpenMP on Linux or macOS.
- Memory-constrained hosts that can leave the sampled suffix array on SSD and still need locate; the paper abstract reports about 4x over SeqAn3 at a similar footprint in that mode.

## Skip it when

- General text, byte alphabets, or approximate/inexact matching: the README says the index is unsuitable for general text and the API offers exact match only.
- Queries that may contain ambiguity characters: the header documents undefined behaviour for them in count and locate, and issue #39 was a segfault on the k-mer NNNNNNNNTAACC (fixed March 2024 only for the seed-table part).
- Builds that must use Clang or MSVC, Windows, or x86 CPUs without AVX2: the build requires GCC with OpenMP, uses POSIX pread, and compiles with -march=native.
- Projects that need an actively maintained dependency: last commit 2024-12-09, and the 2024 issues on wrong 0 counts (#41, #43) and memory growth with very long queries (#45) show recent correctness churn.
- Locate of very short or highly repetitive k-mers on large genomes, where hit lists get huge and the per-k-mer count field is 32-bit (see gotchas).

## How it is fast

The BWT is stored as a strided bit-vector: each 256-position block keeps one 256-bit vector per bit of the letter code (3 for nucleotides, 5 for amino acids) plus block-base counts, so the occurrence function is a few AVX2 (or two-lane Neon) AND/ANDNOT ops on one block followed by a masked popcount. A k-mer seed table memoises the suffix-array range of every length-k suffix (k=12 for DNA is 268 MB, k=5 for protein is 51 MB), skipping the first k backward-search steps. Queries are processed 32 at a time per thread in lock-step with prefetches (non-temporal hint on x86) to overlap cache misses, and OpenMP spreads blocks of 32 across threads.

## Compared with alternatives

Pick AWFM-index when you need a ready C library with build, FASTA handling and batched count/locate for DNA or protein today; QuadRank/BiRank's QuadFm (Rust) reports up to 4x over genedex and lists AWRY among its FM-index competitors, so check it first if Rust is acceptable. The bit-vector and wavelet siblings (QWT, SPIDER, h0_bv) are building blocks, not complete sequence indexes.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake or legacy Makefile) |
| **Dependencies** | libdivsufsort (64-bit build) and TravisWheelerLab/FastaVector as git submodules; OpenMP (libgomp) |
| **Minimum toolchain** | C17 per CMakeLists (legacy Makefile uses gnu11); GCC required (Apple Clang lacks OpenMP per README); CMake 3.21+ |
| **Platforms** | x86-64 with AVX2, aarch64 with Neon; Linux and macOS (POSIX pread); no Windows support documented |
| **Thread safety** | Not documented as a guarantee. Search functions take a const index and parallelise internally with OpenMP; on-disk suffix array reads use pread on a shared descriptor; each AwFmKmerSearchList is written in place, so concurrent calls need separate lists. |
| **Drop-in for the baseline** | no |

## Gotchas

- Ignored allocation failure: parallelSearchTracebackPositionLists calls setPositionListCount but ignores its false return when realloc fails, then writes rangeLength positions into the old, smaller positionList (heap overflow on out-of-memory). setPositionListCount also takes a uint32_t count while the hit range is size_t, so a k-mer with 2^32 or more hits truncates the capacity and overflows the buffer; awFmParallelSearchCount returns void and also stores the count in a 32-bit field.
- Correctness history: before commit 4f9440b (2024-08-08) and 7e6a7e0 (2024-08-13), k-mers longer than 255 caused undefined behaviour and wrong 0 counts (issues #41, #43); the 2021 paper's numbers predate these fixes but used short k-mers, so they are not obviously affected. Use a build from August 2024 or later.
- The README quick-start code does not compile as written (undeclared searchData, AwFmAlphabetNucleotide instead of AwFmAlphabetDna, wrong awFmCreateIndexFromFasta arguments, kmerString set to &argv[i+1]); use src/AwFmIndex.h and tuning/ as the reference.
- Builds with -march=native and -mtune=native, so binaries are not portable to older CPUs. The bundled tuning/search/timeSearch.c times with clock(), which sums CPU time across threads (not wall time) for multithreaded runs, and its query sampler retries the same file offset forever if that offset hits an ambiguity code; the SeqAn3 comparison harness is not in the repo.

## Known shortcomings

- Tier C: the AMB paper (biomedcentral, biorxiv blocked) is known only from a snippet (2-4x nucleotide, 2-6x amino acid vs SeqAn3). Paper-access retier candidate.
- Read in code: parallelSearchTracebackPositionLists ignores the false return of setPositionListCount when realloc fails and then writes past the old positionList (heap overflow on OOM); a uint32_t count truncates ranges of 2^32 or more hits. Ambiguity characters in queries are documented UB (issue #39 segfault). k-mers over 255 gave UB or wrong 0 counts (#41, #43), fixed 2024-08 after the 2021 paper (the paper's short k-mers are likely unaffected). README quick-start does not compile. Needs GCC + OpenMP, -march=native, POSIX pread, no Windows. timeSearch.c times with clock() (CPU time summed over threads) and loops forever on an ambiguous offset. The SeqAn3 harness is not in the repo. Stale since 2024-12-09. Paper copies blocked here.

## Caveats and trade-offs

Numbers were read from WebSearch snippets of the peer-reviewed Algorithms for Molecular Biology paper (doi 10.1186/s13015-021-00204-6); the paper pages (PMC, BMC) are blocked here, so snippet only. Compiler flags and benchmark code not confirmed. Tier C under the snippet-only rule; likely B or A after the paper is read. The README itself carries no numbers.

Strided bit-vector layout using AVX2 (also ARM Neon) and an optional k-mer seed table that trades memory for speed; optional on-disk suffix array. Index is specialised for DNA/protein alphabets, not a general succinct-structure library. C library with C API, callable from C++.

## Maintenance

Stale since 2024-12-09 (590 commits, 0 open issues, 36 stars); BSD-3-Clause, about ten C files plus two submodules, small enough to vendor, but take a post-August-2024 commit for the long-k-mer fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The peer-reviewed Algorithms for Molecular Biology paper (and its bioRxiv preprint) is blocked here (almob.biomedcentral.com and biorxiv.org EGRESS_BLOCKED); a search snippet of the abstract confirms 'approximately 2-4x faster than SeqAn3 for nucleotide search, and approximately 2-6x faster for amino acid search'. The README carries no numbers, so the record stays C under the snippet-only rule; likely B once the paper is read.
- **Verifier notes:** Repo page confirms BSD-3-Clause, 36 stars, last commit 2024-12-09 (stale). Hardware (Xeon E5-2630 v3) could not be checked; left as recorded. Candidate for a paper-access retier to B.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`
- **Shortcomings recorded by:** verifier; peer-reviewed paper (BMC Bioinformatics 2021), seen in snippets
- **Pages the verifier opened:**
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/commits/master>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/README.md>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/issues?q=is%3Aissue>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/issues/39>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/issues/41>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/issues/43>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/issues/45>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/commits/master>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/Makefile_legacy>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmIndex.h>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmSimdConfig.h>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmSimdConfig.c>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmOccurrence.c>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmParallelSearch.c>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmKmerTable.c>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmLetter.c>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmSuffixArray.c>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/src/AwFmFile.c>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/tree/master/tuning>
  - <https://github.com/TravisWheelerLab/AvxWindowFmIndex/tree/master/tuning/search>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/tuning/search/makefile>
  - <https://raw.githubusercontent.com/TravisWheelerLab/AvxWindowFmIndex/HEAD/tuning/search/timeSearch.c>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/traviswheelerlab/avxwindowfmindex`) · [data/wave9/enrich/raw/github_com_traviswheelerlab_avxwindowfmindex.json](../../../data/wave9/enrich/raw/github_com_traviswheelerlab_avxwindowfmindex.json) (enrichment confidence 0.75)

</details>
