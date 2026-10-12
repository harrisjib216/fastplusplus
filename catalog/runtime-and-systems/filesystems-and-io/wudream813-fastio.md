# wudream813/fastio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++17 fast integer reader/writer for competitive programming: mmap plus 2-digit lookup tables, about 7-8x faster than std::cin.

| | |
|---|---|
| **Beats** | std::cin / std::cout (also scanf/printf, fread, getchar_unlocked as rows in the same table) |
| **Claimed result** | make benchvar: read 100 MiB std::cin 565 ms vs mmap + 2-byte table 66.5 ms (8.5x), main library fastio.hpp 70.7 ms (8.0x); write std::cout 473 ms vs fwrite + 4-digit table 148 ms (3.2x), main library 155 ms (3.05x). The README header says 69 ms (7.4x cin) read and 132 ms (3.25x cout) write. The make benchlib table gives cin/ifstream 489.6 ms vs 66.5 ms (7.4x) and cout/ofstream 469.5 ms vs 94.3 ms (5.0x). |
| **Workload** | Reading and writing 100 MiB of about 9.98 million random signed 9-digit integers; the fast read path memory-maps stdin and parses with a 2-byte lookup table. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon @ 2.60 GHz, 2 cores (exact model not stated) |
| **Compiler and flags** | g++ 14.2 -O2 |
| **Adoption** | 3 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/wudream813/fastio) · [benchmark](https://github.com/wudream813/fastio) |

## Verdict

First-party runs on a shared 2-core Intel Xeon @2.60 GHz VM (model not stated), g++ 14.2 -O2, 100 MiB of about 9.98 million 9-digit integers in a warm /tmp file, median of 3 after a warm-up with checksums checked: read std::ifstream 489.6 ms vs fastio 66.5 ms (7.4x), write std::ofstream 469.5 ms vs 94.3 ms (5.0x) in make benchlib; make benchvar gives cin 565 ms vs 70.7 ms and cout 473 ms vs 155 ms. Unsyncing cin does not help here (578 ms), so the win is parsing and formatting, measured on page-cached data rather than disk I/O.

## Use it when

- Competitive programming or batch tools that read or write millions of decimal integers from redirected files (100 MiB of 9-digit ints: about 66-71 ms vs 490-565 ms for cin/ifstream)
- Single-file submissions to online judges on Linux with GCC, where you can paste one header
- Large integer output where cout or printf formatting dominates (about 94-155 ms vs 470 ms for cout on 100 MiB)
- Input you control and can promise properties of (non-negative, fixed separators, known digit count) to unlock the compile-time fast options (reported 40% further on reads)

## Skip it when

- General file I/O, binary data or throughput-bound disk reads: the gain is decimal parsing and formatting, not faster I/O syscalls
- Code that mixes this with scanf/cin on the same stream: the buffers do not see each other's consumed bytes
- Interactive problems unless you flush after each round or build with FASTIO_STREAM; FASTIO_INPUT_MAX blocks until EOF
- MSVC or non-GNU toolchains if you need __int128; Windows loses the mmap path (auto-disabled) and falls back to fread
- Production code needing iostream formatting, locales, error reporting on malformed input, or a stable versioned API (3 stars, single author)

## How it is fast

For a regular file on stdin the Reader reserves an anonymous region, maps the file into it with MAP_FIXED|MAP_POPULATE and fills a trailing anonymous page with 0xFF sentinels, so the whitespace-skip and digit loops run without bounds checks. Integers are parsed two characters at a time through a 65536-entry uint16 table (v = v\*100 + tbl[w] - 1) in a fixed unrolled sequence, with branchless sign handling and an optional 8-byte SWAR fold (FASTIO_SWAR8) for long 64-bit values. The Writer formats through a 10000-entry table of packed 4-digit ASCII words, computes 4-digit groups with independent constant divisions, stores them with one 16-byte SSE movups, and keeps a module-level fixed buffer with an index cursor so GCC keeps the cursor in a register; the hot path is forced always_inline.

## Compared with alternatives

None of the catalogued filesystems-and-io siblings (liburing, SPDK, file_io_benchmark, fcp and the rest) parse text; pick fastio when the bottleneck is decimal integer parsing and formatting on stdin/stdout, and pick liburing or file_io_benchmark-style unbuffered reads when the bottleneck is raw bytes from storage.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (POSIX mmap/read on Unix; SSE intrinsics on x86 unless FASTIO_NO_WRITE_SSE) |
| **Minimum toolchain** | C++17; tested with g++ 14.2 -O2 (GCC-specific pragmas and always_inline; __int128 is a GNU extension) |
| **Platforms** | Linux/Unix with mmap for the fastest path; pipes, terminals and Windows fall back to read()/fread streaming; write SSE path is x86-only with a scalar fallback |
| **Thread safety** | not documented; the global io object and module-level output buffer are shared state, so treat it as single-threaded |
| **Drop-in for the baseline** | partial — FASTIO_REPLACE_CIN_COUT aliases global cin/cout/endl for &gt;&gt; and &lt;&lt; on basic types, but iostream manipulators, tie, locales and error states are absent |

## Gotchas

- Compile-time options are promises about the data: FASTIO_INPUT_MAX silently drops input beyond the limit, FASTIO_OUTPUT_MAX overruns the heap buffer if exceeded, and FASTIO_NO_WS_SKIP or FASTIO_ASSUME_UNSIGNED produce wrong values on non-conforming input.
- The author's own note says FASTIO_OUTPUT_MAX was once recommended for large output and was about 15% slower (24.5 MB output: 57 ms vs 49 ms streaming); keep it for tiny outputs only.
- Buffered output is flushed by the destructor; _Exit() or a crash loses it, and reading -1 into an unsigned type is not treated specially.
- The README's headline figures (69 ms / 132 ms), the benchvar table (70.7 / 155 ms), the benchlib table (66.5 / 94.3 ms) and the report.html table (65.3 / 123.6 ms) disagree; the author notes plus or minus 15% noise on a shared 2-core VM.

## Known shortcomings

- The win is parsing a page-cached /tmp file, not I/O. The README tables disagree with each other (66.5/70.7 ms read; 94.3/123.6/132/155 ms write). The mmap plus sentinel code and the benchmark checksums were checked; no correctness bug.

## Caveats and trade-offs

The workload is integer parsing and formatting, so most of the gain is parsing rather than file I/O. The baseline is cin/cout with default sync; cin with sync off is about equal (578 ms). The README's headline numbers differ between its benchvar, benchlib and bench tables. The CPU model is not stated (2-core Xeon @2.60 GHz, 1.9 GiB RAM). __int128 support is a GNU extension. Repro commands: make benchvar, make benchlib and make bench.

Header-only C++17 for competitive programming; mmap path falls back to streaming for pipes and terminals; many compile-time unsafe-speed knobs (e.g. FASTIO_NO_EOF_CHECK).

## Maintenance

Actively developed by one author (last commit 2026-09-25, 3 stars, MIT, v1.3.0 features), with a CI workflow running self-tests and an 8 MiB quick benchmark; small enough to vendor as one header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README variant table (make benchvar) has std::cin 565 ms vs fio_mmap 66.5 ms and std::cout 473 ms vs fio_fread 148 ms; it states g++ 14.2 -O2 and the benchmark code is in the repo's src/ and Makefile. The CPU is given only as a 2-core Intel Xeon @2.60 GHz with no model, and the numbers are first-party, so the tier is C.
- **Verifier notes:** Metadata checked on github.com: MIT, 3 stars, not a fork, last commit 2026-09-25 (active). The README is in Chinese.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/wudream813/fastio>
  - <https://github.com/wudream813/fastio/commits>
  - <https://raw.githubusercontent.com/wudream813/fastio/HEAD/README.md>
  - <https://raw.githubusercontent.com/wudream813/fastio/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wudream813/fastio/HEAD/README.md>
  - <https://raw.githubusercontent.com/wudream813/fastio/HEAD/include/fastio.hpp>
  - <https://raw.githubusercontent.com/wudream813/fastio/HEAD/src/bench_lib.cpp>
  - <https://raw.githubusercontent.com/wudream813/fastio/HEAD/src/variants_bench.cpp>
  - <https://raw.githubusercontent.com/wudream813/fastio/HEAD/Makefile>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/wudream813/fastio`) · [data/wave11/enrich/raw/github_com_wudream813_fastio.json](../../../data/wave11/enrich/raw/github_com_wudream813_fastio.json) (enrichment confidence 0.7)

</details>
