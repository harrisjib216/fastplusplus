# runiq (Rust duplicate-line filter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust tool and library that drops duplicate lines with one hashing pass, no sort; beats GNU sort -u and uniq.

| | |
|---|---|
| **Beats** | GNU sort -u and uniq (coreutils; versions not stated); also uq and huniq |
| **Claimed result** | README tables (25M lines, 1.9 GB, 20.67% duplicates, unsorted): runiq -f quick 12.1 s vs sort -u 380.2 s (about 31x) and sorted input runiq -f sorted 10.3 s vs uniq 24.9 s (about 2.4x), first-party and unreproducible. Independent run in zkxs/cuniq PERFORMANCE.md (Ryzen 7 7800X3D, Windows 11, 32 GiB, Git Bash): runiq 2.0.0 -f quick \| wc -l 7m19s vs 8-thread GNU 8.32 sort -u \| wc -l 14m12s, about 1.94x (derived from page data); huniq 6m05s was faster. |
| **Workload** | Filtering duplicate lines from 25,000,000 JSON documents (1.9 GB, 20.67% duplicates) and 100,000,000 documents (7.7 GB, 55.69% duplicates), sorted and unsorted input, output to /dev/null. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the measurements; Cargo.toml release profile now sets lto = true (added 2025-12-13, after the README tables were last changed in January 2024). rustc version, coreutils version and build, and locale not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: filters that use hash sets, a bloom filter ('compact') or a streaming sequential check ('sorted') instead of sorting the whole input; memory and speed optimised. |
| **Adoption** | 229 stars, 22 forks; crates.io 18,606 downloads (runiq 2.1.0) |
| **Last commit** | 2025-12-13 |
| **Links** | [repository](https://github.com/whitfin/runiq) · [benchmark](https://github.com/whitfin/runiq) |

## Verdict

First-party README tables (January 2024, runiq 2.0.0 era, before LTO was enabled; no CPU, rustc, coreutils version or locale stated) dedupe jen-generated JSONL to /dev/null. On 25M lines (1.9 GB, 20.67% duplicates), runiq -f quick took 12.1 s vs GNU sort -u 380.2 s on unsorted input, and runiq -f sorted 10.3 s vs uniq 24.9 s on sorted input; on 100M lines (7.7 GB), 34.7 s vs 2529.9 s and 24.9 s vs 105.8 s. An independent run (cuniq's PERFORMANCE.md: Ryzen 7 7800X3D, Windows 11, 32 GiB Wikipedia text at 1.3% cardinality) puts runiq 2.0.0 -f quick | wc -l at 7m19s vs GNU 8.32 sort -u | wc -l on 8 threads at 14m12s, only 1.94x faster (derived from page data).

## Use it when

- Deduplicating large unsorted log or JSONL streams where first-seen order is fine and you do not need sorted output, e.g. replacing sort -u or awk '!seen[\$0]++' in a pipeline.
- Inputs with millions to tens of millions of distinct lines that fit in RAM as 8-byte digests (about 300 MB per 20M distinct lines with -f quick).
- Memory-constrained deduplication where a tiny false-drop rate is acceptable: -f compact used 162 MB for 19.8M uniques in the README, about half of quick, at 1.5x to 1.9x quick's time.
- Already-sorted input: -f sorted streams with about 1.3 MB of memory and was 2.4x to 4.2x faster than GNU uniq in the author's tables.
- Embedding duplicate detection in a Rust program (a log shipper, an ingestion filter) via the Filter trait without pulling in the CLI dependencies.

## Skip it when

- When you need uniq's other modes: no -c counts per line, no -u (lines that occur once), no -d/-D, no field or character skipping, no case folding. Issue #13 (more uniqueness flags) and issue #6 (benchmark suite) have been open since 2021 and 2019.
- Exact deduplication where even a 64-bit hash collision is unacceptable: quick and compact keep only XXH3 digests, so a colliding unique line is silently dropped. Use -f simple, which stores full lines (2.33 GB for 19.8M uniques).
- Very high-cardinality inputs that do not fit in memory: there is no spill to disk, so sort -u (external merge) or a HyperLogLog estimate is the only option at that scale.
- Counting distinct lines on very large files: in cuniq's independent 32 GiB test, runiq 2.0.0 -f quick | wc -l took 7m19s, against 6m05s for huniq and 1m57s for single-threaded cuniq (hash-only mode), and only 1.94x less than 8-thread GNU sort -u | wc -l (14m12s).
- Multi-core throughput: runiq is single-threaded, reads its inputs one after another and does not memory-map files.

## How it is fast

The quick filter hashes each line with XXH3-64 (xxhash-rust xxh3_64) and stores only the u64 digest in a std HashSet (SwissTable) with an identity hasher. That is a single O(n) pass using about 15 bytes per distinct line (298.7 MB for 19.8M uniques in the README), where GNU sort -u does an O(n log n) external sort, with locale collation unless LC_ALL=C. Lines are read through bytelines, which calls BufReader::read_until('\n') into one reused buffer, so reading a line does not allocate. compact inserts the digest into a scalable Bloom filter (growable-bloom-filter: 1M initial capacity, error ratio 1e-8, growth 2, tightening 0.5). sorted compares each line with the previous one, as uniq does. The likely reason it beats GNU uniq (24.9 s vs 10.3 s) is line reading: uniq's gnulib readlinebuffer_delim fetches one byte at a time with getc, while read_until searches for the newline with memchr. Both tools compare lines with memcmp.

## Compared with alternatives

huniq (koraa/huniq) uses the same hash-only approach, matches or beats runiq -f quick in runiq's own README (11.9 s vs 12.1 s) and in cuniq's 32 GiB test (6m05s vs 7m19s), and adds count mode, so prefer it for plain dedup or counts. cuniq is far faster for counting distinct lines. Pick runiq when you want the Bloom-filter compact mode for the lowest memory, a uniq-compatible sorted mode, or its filters as an embeddable Rust library.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | library: growable-bloom-filter 2.1, identity-hash 0.1, strum and strum_macros 0.25, xxhash-rust 0.8; the cli feature (default) adds bytelines 2.5, bytesize 2.3, clap 4.4, cli-table 0.5, format_num 0.1 |
| **Minimum toolchain** | Rust edition 2018; no rust-version declared (the jen dev-dependency was updated in Aug 2024 so the crate builds with Rust 1.80); CI builds stable, beta and nightly |
| **Platforms** | any Rust target; CI runs on ubuntu-latest, macos-latest and windows-latest; no prebuilt binaries (issue #22 asks for a Windows x86_64 release) |
| **Thread safety** | Filters take &mut self and have no internal locking; to share one across threads, wrap it in a Mutex or shard by hash. The CLI is single-threaded. |
| **Drop-in for the baseline** | partial — runiq -f sorted replaces plain uniq on sorted input (same adjacent-line semantics, but no -c/-u/-d/-f/-s/-i options), and runiq replaces sort -u only when you do not need sorted output |

## Gotchas

- Line endings are normalised. bytelines strips a trailing \r before the \n, so 'abc\r\n' and 'abc\n' count as the same line, CRLF input comes out with LF endings, and a missing final newline is added. GNU uniq keeps lines byte-exact.
- -i (invert) prints every repeat occurrence: a line seen 3 times is printed twice. That is neither uniq -d (one copy per duplicated group) nor uniq -D (all copies).
- Output is a locked Stdout, not wrapped in a BufWriter. Rust's Stdout is line-buffered even when it is not a terminal (rust-lang/rust#60673, still open), so the CLI likely makes one write(2) per printed line (19.8M in the 25M-line test). GNU uniq and sort use fully buffered stdio there, so the README's /dev/null timings, if anything, understate runiq.
- Small code-level issues. The quick and compact filters hash with xxh3_64 (XXH3), not XXH64, although runiq's Cargo.toml enables only xxhash-rust's 'xxh64' feature; it compiles because growable-bloom-filter 2.1.1 enables 'xxh3' through Cargo feature unification. CompactFilter's doc comment says a 1e-7 error rate where the code sets 1e-8. A missing input file panics through File::open().unwrap() instead of printing an error. SortedFilter allocates a fresh Vec for every distinct line instead of reusing its buffer.

## Known shortcomings

- The unsorted 31x/73x rows are hashing vs GNU sort -u (algorithmic); no hardware, versions or locale; tables date from January 2024; the only like-for-like rows (sorted runiq vs uniq, 2.4-4.2x) are unexplained.
- Independent run found in cuniq's PERFORMANCE.md (Ryzen 7 7800X3D, Windows 11, 32 GiB): runiq 2.0.0 -f quick | wc -l 7m19s against 8-thread GNU 8.32 sort -u | wc -l 14m12s, only 1.94x (derived), not the README's 31-73x; huniq was faster (6m05s). Corrections: the quick filter hashes with xxh3_64, not xxh64, and builds only because growable-bloom-filter enables xxh3 (feature unification); bytelines strips \r, so CRLF and LF lines dedupe as equal; the likely cause of the uniq gap is gnulib's getc-per-byte reader against memchr; stdout is not a BufWriter, likely one write(2) per line, so the README timings understate runiq.

## Caveats and trade-offs

The author says the numbers are a reference for his own tuning, 'not meant to be a competition'; no hardware, compiler, coreutils version, locale or timing tool is given, and the tables date from the January 2024 README updates. The unsorted comparisons are algorithmic (hash set against GNU sort's full external sort, which also produces sorted output rather than first-occurrence order), and GNU sort's speed depends heavily on the locale, which is not stated. The 'quick' filter keeps only xxh64 digests, so a hash collision could drop a unique line (negligible at these sizes but not exact). The sorted-input comparison with uniq is the like-for-like one (src/filters.rs SortedFilter compares each line with the previous one, as uniq does); its 2.4x to 4.2x margin is not explained. huniq, another Rust tool, matches runiq. [retier] The independent cuniq run gives only 1.94x over 8-thread GNU sort -u, not the README's 31-73x. The quick filter hashes with xxh3_64 (not xxh64) and builds only through feature unification; bytelines strips \r, so CRLF and LF lines dedupe as equal; stdout is not a BufWriter, likely one write(2) per line, so the README timings understate runiq; the likely cause of the uniq gap is gnulib's getc-per-byte reader against memchr.

Compact filter is probabilistic; simple filter uses 2.3 GB to 5 GB of memory; sorted filter only detects adjacent duplicates, like uniq.

## Maintenance

Maintained at a slow pace: v2.1.0 shipped on 2025-12-13 (dependency refresh and LTO), with 18.6k crates.io downloads in total. MIT-licensed and about 600 lines of Rust (tests included), so it is easy to vendor, but the 31x to 73x ratios over sort -u come from one undocumented machine and probably include locale-collation cost (issue #6 asks for LC_ALL=C runs). The independent cuniq run shows a 1.9x margin on a low-cardinality file.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** First-party README tables against GNU sort -u and uniq; the data generator template is in the repo (templates/basic.tera via jen) but no hardware, compiler, coreutils version, locale or timing method is stated, so not A, and no independent measurement exists.
- **Retiered** C to B: Enricher: an independent run in cuniq's PERFORMANCE.md (Ryzen 7 7800X3D, Windows 11) measures runiq 2.0.0 -f quick at 1.94x over 8-thread GNU sort -u on a 32 GiB file, an independent measurement with hardware stated; the README's 31-73x is unsupported by it. C to B with the claim corrected.
- **Verifier notes:** Numbers match the README exactly. Keep at C: first-party, no hardware or versions, unsorted ratios are hashing against sorting (not a language win); only the sorted runiq-vs-uniq rows compare the same algorithm, and that 2.4x to 4.2x gap is unexplained. same_opt_level unknown (distribution coreutils build not stated).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/whitfin/runiq>
  - <https://github.com/whitfin/runiq/commits/main>
  - <https://github.com/whitfin/runiq/commits/main/README.md>
  - <https://github.com/whitfin/runiq/commit/2a66c5066a87497b100699cd778095c5f76c9b59>
  - <https://github.com/whitfin/runiq/tree/main/src>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/README.md>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/src/filters.rs>
  - <https://crates.io/api/v1/crates/runiq>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/README.md>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/src/filters.rs>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/src/options.rs>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/src/statistics.rs>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/templates/basic.tera>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/examples/basic.rs>
  - <https://raw.githubusercontent.com/whitfin/runiq/HEAD/.github/workflows/rust.yml>
  - <https://github.com/whitfin/runiq/commits/main>
  - <https://github.com/whitfin/runiq/issues?q=is%3Aissue>
  - <https://github.com/whitfin/runiq/issues/6>
  - <https://raw.githubusercontent.com/whitfin/bytelines/HEAD/src/std.rs>
  - <https://raw.githubusercontent.com/whitfin/bytelines/HEAD/src/util.rs>
  - <https://raw.githubusercontent.com/whitfin/bytelines/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/whitfin/bytelines/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/coreutils/coreutils/master/src/uniq.c>
  - <https://raw.githubusercontent.com/coreutils/gnulib/master/lib/linebuffer.c>
  - <https://crates.io/api/v1/crates/runiq>
  - <https://crates.io/api/v1/crates/growable-bloom-filter/2.1.1/dependencies>
  - <https://github.com/rust-lang/rust/issues/60673>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/README.md>
  - https://whitfin.io/blog/filtering-unique-logs-using-rust/ (not reachable: ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/whitfin/runiq`) · [data/wave14/enrich/raw/github_com_whitfin_runiq.json](../../../data/wave14/enrich/raw/github_com_whitfin_runiq.json) (enrichment confidence 0.75)

</details>
