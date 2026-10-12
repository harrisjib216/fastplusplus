# opt_vbyte

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Research code that partitions posting lists into VByte and bitmap blocks, cutting VByte index space 30-47% at equal query speed.

| | |
|---|---|
| **Beats** | Plain unpartitioned VByte (varint) |
| **Claimed result** | README table (i7-4790K): VByte docs 10.498 bpi, freqs 8.031 bpi, build 0.704 s, 4.316 microseconds/query; VByte optimal partitioning docs 7.388 bpi, freqs 4.268 bpi, build 0.739 s, 4.378 microseconds/query. That is about 30% (docs) and 47% (freqs) smaller at about 1.4% slower query time (derived from page data); not faster than plain VByte. |
| **Workload** | Inverted index compressed with VByte vs uniform / eps-optimal / optimal partitioning; space in bits per integer, index build time and query time. |
| **Metric** | memory |
| **Hardware** | Intel Core i7-4790K at 4 GHz, Linux 4.13.0 (Ubuntu 17.10), 64-bit |
| **Compiler and flags** | gcc 7.3.0 (README: 'tested on Linux Ubuntu with gcc 7.3.0'; table compiled at 'the highest optimization setting'); CMakeLists.txt Release flags -std=c++14 -march=native -O3 |
| **Adoption** | 17 stars |
| **Last commit** | 2021-11-10 |
| **Links** | [repository](https://github.com/jermp/opt_vbyte) · [benchmark](https://github.com/jermp/opt_vbyte) |

## Verdict

On the repository's sample collection (113,306 lists, 3.3 M postings, 500 AND queries), on an i7-4790K at 4 GHz under Ubuntu 17.10 with -O3 -march=native (GCC 7.3.0 per the README), optimal partitioning shrinks docIDs from 10.498 to 7.388 bits per integer and frequencies from 8.031 to 4.268 versus unpartitioned Masked-VByte, with build time 0.739 vs 0.704 s and query time 4.378 vs 4.316 microseconds. The 2x compression on Gov2, ClueWeb09 and CCNews is the paper's claim (search snippet only; paper not opened).

## Use it when

- Search-engine inverted indexes with sorted docID lists that contain dense clusters, where plain VByte wastes a full byte per small gap.
- You already use VByte for decode speed and want about 30% smaller docID lists and 47% smaller frequency lists without giving up that speed.
- Reproducing or extending the TKDE 2019/2020 paper's experiments on ds2i-format collections (Gov2, ClueWeb09, CCNews).
- x86-64 build machines where -march=native with SSE4 is available for Masked-VByte.

## Skip it when

- You need speed over VByte: query time is level with or slightly slower than unpartitioned VByte (4.378 vs 4.316 microseconds per AND query).
- Unsorted integer arrays or general bitpacking: the partitioner assumes monotone docID lists (frequencies are handled as prefix sums via positive_sequence).
- You want a small embeddable library: it pulls in Boost (iostreams, filesystem, thread, unit_test_framework), stxxl, succinct, FastPFor, streamvbyte and MaskedVByte submodules.
- Long-lived production code: research code, last commit 2021-11-10, no releases, no tests enabled (test subdirectory commented out in CMakeLists.txt).
- Non-x86 targets: Masked-VByte and VarIntG8IU paths use SSE intrinsics and the build forces -march=native.

## How it is fast

The speed comes from VByte itself: sparse blocks are decoded with Masked-VByte (SSE shuffle-table decoding), and dense runs become compact ranked bit vectors, which are both smaller and fast to scan. The win is space: a single-pass, linear-time partitioning algorithm (optimizer.hpp) tracks the running bit-cost difference between VByte and bit-vector encoding of each run, with a fixed per-block cost F (default 64 bits), and cuts a block when switching encoders saves more than that cost. Block endpoints and sizes are stored with Elias-Fano so NextGEQ can skip partitions.

## Compared with alternatives

Pick it over MaskedVByte or Stream VByte when the data is sorted posting lists and space matters as much as VByte-speed decoding; pick ds2i (partitioned Elias-Fano) for faster NextGEQ at even smaller size, or FastPFor/simdcomp when raw decode throughput is the goal.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Boost &gt;= 1.42 (iostreams, unit_test_framework, filesystem, system, thread), CMake &gt;= 2.8, git submodules: FastPFor, stxxl, succinct, streamvbyte, MaskedVByte; OpenMP optional |
| **Minimum toolchain** | C++14; README says tested with GCC 7.3.0 on Ubuntu; Clang builds add -stdlib=libc++ |
| **Platforms** | x86-64 Linux tested (SSE4 via -march=native for Masked-VByte); macOS install notes for Boost only; other platforms not documented |
| **Thread safety** | not documented; index building uses a Boost basic_thread_pool sized by DS2I_THREADS (default hardware_concurrency) |
| **Drop-in for the baseline** | partial — same VByte byte format inside VByte blocks, but the index layout (partitions, bit-vector blocks, Elias-Fano endpoints) is new and needs this codebase to read |

## Gotchas

- configuration's constructor creates a Boost thread pool, and pvb::opt_vbyte::encode holds a function-local static configuration, so the first encode call spawns hardware_concurrency worker threads.
- Tuning is through environment variables (DS2I_FIXCOST, DS2I_K, DS2I_EPS1-3, DS2I_LOG_PART, DS2I_THREADS) read at construction, not through an API.
- Uses Boost's experimental executors and task_region (BOOST_THREAD_PROVIDES_EXECUTORS, parallel::v2), which may need adjustment on recent Boost versions; not tested this session.
- external/CMakeLists.txt runs 'git submodule update --init' at configure time, so a tarball without .git will not configure as-is.

## Known shortcomings

- Upgraded B to A (README states i7-4790K and gcc 7.3.0, CMakeLists -O3 -march=native, harness in src/queries.cpp), but the win is space only: docs 10.498 to 7.388 bits per integer and freqs 8.031 to 4.268, while query time is 4.378 vs 4.316 us, about 1.4% slower than plain VByte. Last commit 2021-11-10, abandoned.
- Research code (ds2i-style CLI tools, not a general codec) with heavy dependencies (Boost experimental thread executors, stxxl, succinct, FastPFor, streamvbyte, MaskedVByte submodules); x86-only via -march=native/SSE; the first encode starts a Boost thread pool with static configuration; tests disabled; 0 issues, last commit 2021-11-10.

## Caveats and trade-offs

Space win, not a speed win: optimal partitioning cuts docs from 10.498 to 7.388 bpi and freqs from 8.031 to 4.268 bpi, while AND-query time is 4.378 vs 4.316 microseconds (about 1.4% slower, derived from page data). The 'up to 2x better compression with fast decoding' framing comes from the TKDE 2019 paper (arXiv 1804.10949), not opened (arXiv and pages.di.unipi.it blocked). README ties gcc 7.3.0 to testing generally rather than explicitly to the table run. Depends on Boost and ds2i-derived submodules. Last commit 2021-11-10.

Partitioning step adds build time and requires sorted lists; decode speed equal to VByte, no speedup.

## Maintenance

Abandoned research code (last commit 2021-11-10, no issues filed) under MIT; the partitioning algorithm (optimizer.hpp, about 130 lines) is the reusable part and is easy to port into another index.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B: the README benchmark table compares partitioned VByte indexes against un-partitioned VByte (block_maskedvbyte) on an i7-4790K at 4 GHz under Linux 4.13 / Ubuntu 17.10, the README says the code is built with gcc 7.3.0 at the highest optimization setting and CMakeLists.txt sets -O3 -march=native, and the benchmark code is public (src/create_freq_index.cpp, src/queries.cpp, scripts/). The win is space at equal query speed, not speed.
- **Verifier notes:** Record's caveat that the README gives no CPU or compiler was wrong; they are stated, so tier upgraded to A for the space claim. It is not faster than plain VByte (query time parity, slightly slower); keep only if memory-metric entries are in scope. Metadata checked: MIT, 17 stars, not archived or a fork, last commit 2021-11-10 (abandoned, under the &gt;3 years rule).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/jermp/opt_vbyte>
  - <https://github.com/jermp/opt_vbyte/commits>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/src/queries.cpp>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/src/create_freq_index.cpp>
- **Sources the enricher read:**
  - <https://github.com/jermp/opt_vbyte>
  - <https://github.com/jermp/opt_vbyte/commits/master>
  - <https://github.com/jermp/opt_vbyte/issues?q=is%3Aissue>
  - <https://github.com/jermp/opt_vbyte/tree/master/include>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/README.md>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/master/include/opt_vbyte.hpp>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/master/include/optimizer.hpp>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/master/include/partitioned_vb_sequence.hpp>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/master/include/block_codecs.hpp>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/master/include/configuration.hpp>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/master/external/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jermp/opt_vbyte/master/src/CMakeLists.txt>
  - WebSearch: "optimally partitioning variable-byte codes" Pibiri Venturini (snippets of arxiv.org/pdf/1804.10949 and pages.di.unipi.it TKDE20.pdf; pages not opened)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jermp/opt_vbyte`) · [data/wave9/enrich/raw/github_com_jermp_opt_vbyte.json](../../../data/wave9/enrich/raw/github_com_jermp_opt_vbyte.json) (enrichment confidence 0.75)

</details>
