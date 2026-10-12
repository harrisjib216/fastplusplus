# Counting Quotient Filter (CQF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> C counting quotient filter: approximate membership plus per-item counts, faster and smaller than counting Bloom filters.

| | |
|---|---|
| **Beats** | counting Bloom filter (and Bloom filter generally) |
| **Claimed result** | "In-memory inserts and queries up to an order-of-magnitude faster than the original [quotient] filter, several times faster than a Bloom filter"; on SSD, CQF "outperforms all structures by a factor of at least 2" due to better data locality (as quoted by the independent paper-summary blog blog.acolyer.org, "the morning paper") |
| **Workload** | In-memory and SSD-resident insert/query throughput for approximate membership + counting, per the SIGMOD 2017 paper "A General-Purpose Counting Filter: Making Every Bit Count" |
| **Metric** | throughput |
| **Adoption** | 132 stars; used as a component in several genomics/bioinformatics k-mer counting tools |
| **Last commit** | 2022-09-22 |
| **Links** | [repository](https://github.com/splatlab/cqf) · [benchmark](https://blog.acolyer.org/2017/08/08/a-general-purpose-counting-filter-making-every-bit-count/) |

## Verdict

The SIGMOD 2017 paper by the CQF's authors (as quoted on the morning paper) reports in-memory inserts and queries up to an order of magnitude faster than the original quotient filter, several times faster than a Bloom filter, and similar to a cuckoo filter. It also reports at least 2x over every other structure it tested (Bloom, QF, cuckoo, counting Bloom) on SSD, on uniform-random and Zipfian inputs. The figures are qualitative: the paper PDF returned 403, so compiler and hardware are unknown, and the repo's bm.c benchmarks only the CQF (built with gcc -Ofast -msse4.2).

## Use it when

- Approximate counting over large multisets such as k-mer counting in genomics. splatlab's own Squeakr and Mantis vendor this code under include/gqf.
- Skewed or Zipfian streams, where a counting Bloom filter wastes fixed-width counters. Here 1 to 3 copies use 1 to 3 slots, and larger counts use about 2 + log(C)/r slots (maintainer, issue #4).
- Filters larger than RAM: qf_initfile/qf_usefile mmap the filter from a file, and the paper reports at least 2x over every other structure it tested on SSD.
- When you need deletes, resize (manual or auto-doubling), a linear-scan merge of several filters, or iteration. QF_HASH_INVERTIBLE gives exact answers when keys fit in key_bits.
- Insert-heavy multi-threaded workloads on Linux x86-64 using QF_WAIT_FOR_LOCK or QF_TRY_ONCE_LOCK, which use region spinlocks instead of a global lock.

## Skip it when

- Any target other than Linux x86-64. popcnt, bsr and rdtsc are unconditional x86 inline asm, and even the NH=1 build only removes PDEP/TZCNT. partitioned_counter.c includes &lt;sys/sysinfo.h&gt; and &lt;linux/unistd.h&gt; and calls sched_getcpu, so macOS, aarch64 and MSVC need porting.
- Static sets built once: xor or ribbon filters are smaller. For pure membership at loose false-positive rates, a Bloom filter can also be smaller; the paper says the RSQF only beats Bloom on space below about a 1/64 false-positive rate (as quoted in an HN comment).
- Reads that must be consistent with concurrent writes: qf_query and qf_count_key_value ignore the lock flags and read without locking.
- Production code that cannot absorb maintenance risk. Last commit was 2022-09-22, and issue #9 (segfaults during auto-resize and merge, open since 2019) is unresolved. The library calls exit() on allocation failure and writes resize messages to stdout and stderr.
- Keys wider than 64 bits or string keys used directly: the API takes a uint64_t key, and the maintainers said in 2024 (issue #17) that 128-bit support is not on the roadmap.

## How it is fast

It is a rank-and-select quotient filter (RSQF). Each hash is split into a quotient, which picks a home slot, and a remainder. Remainders sit in sorted runs placed by linear probing. Each block of 64 slots stores occupieds and runends bitvectors plus one 8-bit offset (2.125 metadata bits per slot), so finding a run costs one POPCNT rank and one PDEP+TZCNT select within a block or two, instead of k random probes as in a Bloom filter. That locality also explains the SSD result, and it lets the filter run up to 95% full, compared with about 75% for the original quotient filter. Counts are stored inside the remainder slots with a variable-length encoding, so an item with no duplicates costs nothing extra, and skewed counts grow roughly logarithmically.

## Compared with alternatives

Pick it over the Cuckoo Filter (efficient/cuckoofilter), Vacuum Filter or Xor/BuRR filters when you need true multiset counts, deletes, resize or merge, or an SSD-resident filter; the paper puts its in-memory speed close to the cuckoo filter. Prefer Xor/BuRR for static sets where space is what matters, and the cuckoo filter for portable pure-membership C++ with no counting.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | The core (gqf.c, gqf_file.c, hashutil.c, partitioned_counter.c) needs only libc, libm and pthreads. libssl/libcrypto are used only by the bundled test programs (RAND_bytes), but the Makefile links them into every target. There is no library or install target. |
| **Minimum toolchain** | GCC or Clang with GNU extensions (-std=gnu11, __uint128_t, GNU inline asm). The Makefile uses gcc -std=gnu11 -Ofast -msse4.2. No minimum version is documented. |
| **Platforms** | Linux x86-64. The fast select path needs BMI2 PDEP plus TZCNT (Haswell or newer); build with NH=1 for a broadword select fallback on older x86 CPUs. |
| **Thread safety** | Insert, remove and set_count are thread-safe with QF_WAIT_FOR_LOCK or QF_TRY_ONCE_LOCK, which take spinlocks over 65,536-slot regions and neighbouring regions near boundaries; QF_NO_LOCK is for single-threaded use. Queries take no locks. Auto-resize replaces the whole filter inside qf_insert with no global lock, so it is unsafe to combine with concurrent inserts (from reading the source). |
| **Drop-in for the baseline** | partial — it fills the counting Bloom filter role (insert, count, delete) but has a different C API over uint64_t keys, needs a power-of-two slot count up front, and returns QF_NO_SPACE at about 95% load instead of letting the false-positive rate degrade. |

## Gotchas

- qf_malloc uses malloc, and qf_init's memset of the buffer is commented out, so a new filter can start with garbage metadata. Open issue #9 (segfaults in shift_remainders/run_end during resize and merge) went away for one user after switching to calloc. Call qf_reset after qf_malloc; resize still goes through qf_malloc internally.
- qf_use and qf_usefile allocate the lock array while num_locks is still 0, and never set it afterwards (only qf_deserialize does). Locking flags on a reopened or mmapped filter can therefore index past that array, so use QF_NO_LOCK there. This comes from reading the source and is not documented.
- The filter counts as full at 95% of nslots, or when an insert lands more than 1000 slots from its home slot. Occupancy and element counters are batched per CPU with a threshold of 100, so qf_get_\* values lag until qf_sync_counters is called.
- In QF_HASH_NONE mode, keys must already be reduced modulo the filter's range; the issue #3 segfault came from skipping this. The header also warns of very bad performance on skewed inputs in this mode. QF_HASH_INVERTIBLE only gives exact answers for keys that fit in key_bits.

## Known shortcomings

- The repo's bm.c has no Bloom baseline, so the 'order of magnitude faster than Bloom' comes only from the SIGMOD 2017 paper.
- Linux x86-64 only (x86 asm even with NH=1; partitioned_counter.c uses sched_getcpu). Open segfault on resize/merge since 2019 (#9); qf_malloc does not zero memory (call qf_reset); qf_use/qf_usefile leave num_locks at 0 so lock flags overrun the lock array (from source reading); queries take no locks. Full at 95%; the library calls exit() and prints to stdout.

## Caveats and trade-offs

The claims are qualitative (up to an order of magnitude, several times, at least 2x) with no exact figures. They are the paper authors' own statements, quoted verbatim on blog.acolyer.org ("the morning paper"), not independent measurements by the blog. I could not fetch the paper PDF: dl.acm.org and the author's Stony Brook PDF both returned 403, although Semantic Scholar lists the paper as gold open access. The repo's bm.c benchmarks only the CQF and has no Bloom baseline code. The Makefile builds with gcc -Ofast -msse4.2 and needs Haswell+ for the fast select path (NH=1 for older CPUs).

Fastest path needs Haswell+ select instructions (has a slower fallback for older CPUs); depends on libssl; smaller ecosystem/tooling than Bloom filters

## Maintenance

Abandoned: last commit 2022-09-22 (a merge of README build-instruction fixes), with an unresolved 2019 segfault issue. It is BSD-3-Clause and only about four C files, so vendoring it, as splatlab's Squeakr and Mantis do, is the realistic way to use it on Linux x86-64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The claims come from a peer-reviewed SIGMOD 2017 paper (DOI 10.1145/3035918.3035963, pp. 775-787, confirmed via Crossref) that benchmarks against Bloom and counting Bloom filters. The morning paper page quotes them verbatim. It is not A: the repo's own src/bm.c benchmarks only the CQF (through gqf_wrapper.h) with no Bloom baseline, and I could not open the paper to check its compiler and CPU details.
- **Verifier notes:** The quotes match the blog page verbatim, and the page does compare against Bloom and counting Bloom filters. Metadata checks out: BSD-3-Clause, 132 stars, not archived, last commit 2022-09-22, so abandoned. I could not verify the claim about genomics tools using it and left it uncorrected.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://blog.acolyer.org/2017/08/08/a-general-purpose-counting-filter-making-every-bit-count/>
  - <https://github.com/splatlab/cqf>
  - <https://github.com/splatlab/cqf/blob/master/src/bm.c>
  - <https://github.com/splatlab/cqf/blob/master/Makefile>
  - <https://api.crossref.org/works/10.1145/3035918.3035963>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3035918.3035963?fields=title,openAccessPdf,externalIds>
  - <https://www3.cs.stonybrook.edu/~ppandey/files/p775-pandey.pdf>
  - <https://dl.acm.org/doi/pdf/10.1145/3035918.3035963>
- **Sources the enricher read:**
  - <https://github.com/splatlab/cqf>
  - <https://github.com/splatlab/cqf/blob/master/README.md>
  - <https://github.com/splatlab/cqf/blob/master/include/gqf.h>
  - <https://github.com/splatlab/cqf/blob/master/include/gqf_int.h>
  - <https://github.com/splatlab/cqf/blob/master/include/gqf_file.h>
  - <https://github.com/splatlab/cqf/blob/master/include/partitioned_counter.h>
  - <https://github.com/splatlab/cqf/blob/master/src/gqf.c>
  - <https://github.com/splatlab/cqf/blob/master/src/gqf_file.c>
  - <https://github.com/splatlab/cqf/blob/master/src/hashutil.c>
  - <https://github.com/splatlab/cqf/blob/master/src/partitioned_counter.c>
  - <https://github.com/splatlab/cqf/blob/master/src/test.c>
  - <https://github.com/splatlab/cqf/blob/master/src/test_threadsafe.c>
  - <https://github.com/splatlab/cqf/blob/master/src/bm.c>
  - <https://github.com/splatlab/cqf/blob/master/Makefile>
  - <https://github.com/splatlab/cqf/commits/master>
  - <https://github.com/splatlab/cqf/issues?q=is%3Aissue>
  - <https://github.com/splatlab/cqf/issues/1>
  - <https://github.com/splatlab/cqf/issues/2>
  - <https://github.com/splatlab/cqf/issues/3>
  - <https://github.com/splatlab/cqf/issues/4>
  - <https://github.com/splatlab/cqf/issues/5>
  - <https://github.com/splatlab/cqf/issues/6>
  - <https://github.com/splatlab/cqf/issues/9>
  - <https://github.com/splatlab/cqf/issues/13>
  - <https://github.com/splatlab/cqf/issues/17>
  - <https://github.com/splatlab/cqf/pull/16>
  - <https://blog.acolyer.org/2017/08/08/a-general-purpose-counting-filter-making-every-bit-count/>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3035918.3035963?fields=title,openAccessPdf,externalIds,citationCount>
  - <https://dl.acm.org/doi/pdf/10.1145/3035918.3035963>
  - <https://www3.cs.stonybrook.edu/~ppandey/files/p775-pandey.pdf>
  - <https://prashantpandey.github.io/>
  - <https://prashantpandey.github.io/publications/>
  - <https://github.com/splatlab/squeakr>
  - <https://github.com/splatlab/mantis>
  - <http://export.arxiv.org/api/query?search_query=all:%22counting%20quotient%20filter%22>
  - <https://hn.algolia.com/api/v1/search?query=counting%20quotient%20filter>
  - <https://hn.algolia.com/api/v1/items/14959646>
  - <https://hn.algolia.com/api/v1/items/15880176>
  - <https://hn.algolia.com/api/v1/items/14963873>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/splatlab/cqf`) · [data/wave6/enrich/raw/github_com_splatlab_cqf.json](../../../data/wave6/enrich/raw/github_com_splatlab_cqf.json) (enrichment confidence 0.62)

</details>
