# cuniq (Rust unique-line counter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `GPL-3.0-or-later` · 🟢 active

> Rust CLI that counts distinct lines (or per-line occurrences) with a hash table instead of GNU sort -u / sort | uniq -c.

| | |
|---|---|
| **Beats** | GNU coreutils 8.32 `sort -u \| wc -l` and `sort \| uniq -c`, and GNU awk 5.3.2 (`a[$0]++`), all C programs. |
| **Claimed result** | PERFORMANCE.md, 32 GiB Wikipedia test (bash time, one run each): count, `sort -u huge.txt \| wc -l` (GNU 8.32, 8 threads) 14m11.935s vs `cuniq --memmap --threads=1` 2m47.462s (5.1x, derived from page data) and `cuniq --memmap --mode=near-exact` (16 threads, stores hashes only) 59.387 s (14.3x, derived from page data); `--mode=estimate` (HyperLogLog, 0.74% error, 16 threads) 9.038 s. Report: `sort huge.txt \| uniq -c` 28m46.811s and gawk 5.3.2 `a[$0]++` 25m03.082s vs unsorted `cuniq --memmap -c` 3m07.817s (9.2x and 8.0x, derived from page data); like-for-like sorted report `cuniq --memmap -cs` 3m26.898s vs `sort \| uniq -c` (8.3x, derived from page data). README: 'For counting cuniq reliably outperforms GNU sort in all cases', with one stated exception for sorted reports on inputs with almost no duplicates. |
| **Workload** | Count distinct lines (and per-line occurrence counts) of a 32 GiB preprocessed Wikipedia text dump with 6,028,206,370 lines, 78,035,032 of them unique; also a 4,000,000-line random-number file in criterion benches. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 7800X3D (16 threads), 5200 MT/s memory, 6950 MB/s sequential disk read, Windows 11 24H2 |
| **Compiler and flags** | Build used for the 32 GiB table not stated. PERFORMANCE.md gives `RUSTFLAGS="-C target-cpu=native" cargo +nightly bench -Z build-std=std ... --target=x86_64-pc-windows-msvc` for the criterion benches and a `release-optimized-debug` profile build for profiling; README mentions profile-guided optimization and recommends `-C target-cpu=native` installs. GNU coreutils 8.32 and gawk 5.3.2 are Git Bash (Windows) binaries, build flags and locale unknown. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | PERFORMANCE.md optimization list: hash table instead of sorting (O(n)), memory-mapped input, memchr newline search, no UTF-8 validation, ahash, leaking large structures instead of freeing, multithreaded hashing and HyperLogLog for the estimate mode. |
| **Adoption** | 4 stars, 1 fork (GitHub repo page, 2026-10-11); crates.io cuniq 2.0.0 (2025-10-14), 4,635 downloads; AUR package per README. |
| **Last commit** | 2025-12-22 |
| **Links** | [repository](https://github.com/zkxs/cuniq) · [benchmark](https://raw.githubusercontent.com/zkxs/cuniq/HEAD/PERFORMANCE.md) |

## Verdict

The author timed single bash `time` runs on Windows 11 (Ryzen 7 7800X3D, 16 threads) over a private 32 GiB Wikipedia dump with 6.03 billion lines, 78 million distinct: exact count 2m47s on 1 thread against Git for Windows GNU sort 8.32 `sort -u | wc -l` at 14m12s on 8 threads (about 5.1x), report `cuniq -c` 3m08s against `sort | uniq -c` 28m47s and gawk 5.3.2 25m03s, and the sorted report 3m27s (about 8.3x). The cuniq build flags and sort's locale are not stated, and the -c rows are listed as 1 thread although the shown command defaults to all 16 threads; the criterion benches on a 4-million-line file check the count but publish only plots.

## Use it when

- Counting distinct lines in multi-gigabyte logs or dumps where duplicates dominate (the author's file had 1.3% distinct lines); expect several times the speed of `sort -u | wc -l`.
- Per-line occurrence counts (`uniq -c` style) when output order does not matter, or when sorting the deduplicated set afterwards with -cs is acceptable.
- Approximate distinct counts on very large inputs with --mode=estimate: fixed 64 KiB of registers by default (tunable with --size), about 1% error, scales with cores until disk read is the limit.
- Quick cardinality checks with --mode=near-exact when a 64-bit hash collision (undercount by one) is acceptable; the README says this is safe below roughly 10 million distinct lines.
- Embedding the same counters in a GPL-compatible Rust program through the line_cardinality crate.

## Skip it when

- You need the unique lines themselves (`sort -u` as a filter): cuniq only prints a count or a count report; the TODO file suggests piping `cuniq -cs` into awk.
- Nearly every line is distinct and you want a sorted report: the README says `sort | uniq -c` wins there because cuniq builds the hash table and then sorts almost the whole input anyway.
- The distinct set does not fit in RAM: exact mode keeps every distinct line in its own heap allocation and never spills to disk, unlike GNU sort; peak memory is not reported in the benchmark table.
- You need sort's key, field, numeric, case-folding or locale-collation options: cuniq compares raw bytes and only splits on \n.
- Licensing or maturity matter: GPL-3.0-or-later, a single author, 4 stars and no external issue reports, so edge cases have had little outside testing.

## How it is fast

It swaps the O(n log n) external merge sort for O(n) inserts into a hashbrown HashTable keyed by ahash, copying a line into the table only the first time it is seen (entry API with deferred clone). Files are memory-mapped and split on newlines with memchr; with more than one thread, workers hash 128 MiB newline-aligned chunks while a single thread does all table inserts, so exact mode barely scales (2m47s on 1 thread vs 2m49s on 16) while near-exact mode, which inserts only hashes, drops to 59 s. Estimate mode keeps one 64 KiB HyperLogLog sketch per thread and merges them by register max, so it is fully parallel (9 s on 32 GiB). Large tables are leaked at exit to skip destructor time.

## Compared with alternatives

Pick cuniq over huniq or runiq when you want a count or a count report, not the unique lines: the author's own run on the same 32 GiB file has huniq 2.7.0 at 6m05s (count) and 9m32s (-c) and runiq's quick filter at 7m19s against cuniq's 2m47s exact count and 3m08s report. Use huniq or runiq when you need deduplicated output, and hist-rs when you want the report ranked by frequency like `sort | uniq -c | sort -n`.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | ahash, bstr, cfg-if, clap, memchr, line_cardinality (hashbrown, voracious_radix_sort); optional memmap2, crossbeam-channel and num_cpus (default features) |
| **Minimum toolchain** | Rust 1.85 (edition 2024); the release workflow and the author's benchmark builds use nightly -Z build-std |
| **Platforms** | any platform with Rust std; release binaries for x86-64 Windows, x86-64 Linux (gnu), x86-64 and aarch64 macOS; AUR package |
| **Thread safety** | Command-line tool; line_cardinality counters are single-owner structs, and only HyperLogLog supports merging per-thread copies |
| **Drop-in for the baseline** | partial — the count output matches `sort -u \| wc -l` and the -c report uses uniq -c's 7-wide count column, but -c output is unsorted unless -s, -s sorts by raw bytes (LC_ALL=C order, not locale collation), none of sort's or uniq's other flags exist, and the deduplicated lines are never printed |

## Gotchas

- Empty-line edge case in the multithreaded path (found by reading cuniq/src/io/util.rs): ChunkIterator ends each chunk just before the first newline at or after the cut point, and the line splitter only emits a trailing piece when it is non-empty. When a cut lands exactly on the newline of an empty line, that empty line is dropped; a Python transcription of ChunkIterator and LineIterator turns 'a\n\nb\n' into only 'a' and 'b' at chunk sizes 0 and 2. Estimate mode on a single file uses chunk size = file length / threads, so a file smaller than the thread count is split at size 0 and loses every empty line. The default on any multi-core machine is the multithreaded path, so `cuniq` can undercount the empty line by one and `cuniq -c` can under-report its count; the effect on the 32 GiB table (about 256 cuts of 128 MiB) is negligible.
- Line endings depend on the input path: stdin and --no-memmap reads use bstr for_byte_line, which strips a trailing \r before \n, while memory-mapped and multithreaded file reads split on \n only and keep the \r. Files with mixed CRLF and LF endings, or stdin mixed with file arguments, can give different counts than the same data read another way and than GNU sort, which keeps the \r.
- With more than one thread (the default) every file argument is memory-mapped and --no-memmap is ignored, because parallel_process_input never checks it; on Unix the single-threaded default is memmap too. Pipes passed as file arguments (for example bash process substitution) therefore cannot be mapped and fail with 'failed to memmap file' unless you pipe through stdin or use --threads=1 --no-memmap, and a file modified while mapped is outside the code's safety contract.
- ahash is built with compile-time-rng only, so the hash seed is fixed per binary and shared by everyone using a released binary; near-exact mode's collision undercount is therefore reproducible for crafted input. Released binaries are also built without -C target-cpu=native, which the README recommends for speed, so they may not match the benchmarked build.

## Known shortcomings

- First-party single bash-time runs on Windows (Git Bash GNU coreutils 8.32, flags and locale unknown); the 32 GiB input is private; hash vs sort comparison (sort -u on 8 threads vs cuniq on 1); the like-for-like sorted-report ratio is 8.3x; 4 stars.
- Edge-case bug by reading cuniq/src/io/util.rs ChunkIterator (the default multithreaded path): when a chunk cut lands on an empty line's newline, that empty line is dropped (a Python transcription turns 'a\n\nb\n' into a, b), and in estimate mode a file smaller than the thread count is split with chunk size 0, so every empty line is lost; the effect on the 32 GiB table is negligible. CRLF handling depends on the input path (bstr strips \r on stdin, memmap keeps it); --no-memmap is ignored when threads &gt; 1, so pipes passed as file arguments fail with 'failed to memmap file'; the ahash seed is fixed at compile time; the README's 'PGO' is flamegraph profiling only; the table lists -c rows as 1 thread but the shown command defaults to 16. cuniq cannot print the unique lines themselves.

## Caveats and trade-offs

First-party, Windows-only harness: GNU coreutils 8.32 and gawk 5.3.2 run under Git Bash with unknown build flags and unstated locale (GNU sort in a UTF-8 locale collates far slower than LC_ALL=C), and the 32 GiB input file is not published; single bash `time` runs. The headline count compares cuniq at 1 thread against sort -u at 8 threads; the near-exact and estimate rows store only hashes or estimate, so they are not exact counts. The 9.2x report figure compares an unsorted cuniq report with a sorted `sort | uniq -c`; the sorted `cuniq -cs` row gives 8.3x. The win is an algorithm change (hash versus sort), not a language effect. The author's table also measures huniq 2.7.0 (6m04.595s count), runiq and sortuniq. GPL-3.0-or-later. [retier] The default multithreaded ChunkIterator drops an empty line when a chunk cut lands on its newline, and in estimate mode a file smaller than the thread count loses every empty line (negligible for the 32 GiB table). CRLF handling depends on the input path (bstr strips \r on stdin, memmap keeps it); --no-memmap is ignored when threads &gt; 1; the ahash seed is fixed at compile time; the README's 'PGO' is flamegraph profiling only; the table lists -c rows as 1 thread but the shown command defaults to 16.

Exact mode keeps every distinct line in memory; near-exact mode ignores 64-bit hash collisions; estimate mode is approximate; -c output is unsorted unless -s; hashing loses to sorting when nearly every line is unique.

## Maintenance

Single-author project: 2.0.0 released 2025-10-14, dependency and CI bumps through 2025-12-22, no issues filed; usable as a CLI today, but GPL-3.0-or-later limits copying the line_cardinality code into non-GPL projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party table in PERFORMANCE.md timed by hand with bash `time` on a private 32 GiB Wikipedia dump; CPU stated (Ryzen 7 7800X3D) but the build used for the table is not stated and the GNU binaries are Git for Windows builds with unknown flags. Criterion bench code is public but its results are only plots.
- **Verifier notes:** Numbers match PERFORMANCE.md; added the sorted-report ratio and thread counts. Shortcomings to record: first-party single runs on Windows with Git Bash GNU tools (flags and locale unknown), private 32 GiB input, hash-vs-sort algorithm change, approximate modes in the headline list. Low notability (4 stars, 4,635 crate downloads).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/README.md>
  - <https://github.com/zkxs/cuniq>
  - <https://github.com/zkxs/cuniq/commits>
  - <https://crates.io/api/v1/crates/cuniq>
- **Sources the enricher read:**
  - <https://github.com/zkxs/cuniq>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/README.md>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/MAINTENANCE.md>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/Cargo.toml>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/build.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/main.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/hash.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/cli_args.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/io/mod.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/io/parallel.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/io/memmap.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/io/buf.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/io/read.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/src/io/util.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/cuniq/benches/benches.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/line_cardinality/Cargo.toml>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/line_cardinality/src/lib.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/line_cardinality/src/count_unique_impl/mod.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/line_cardinality/src/count_unique_impl/hashtable_lossless.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/line_cardinality/src/count_unique_impl/hashtable_lossy.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/line_cardinality/src/count_unique_impl/hyperloglog.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/line_cardinality/src/count_unique_impl/radixsort_lossy.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/.github/workflows/ci.yml>
  - <https://github.com/zkxs/cuniq/commits/master>
  - <https://github.com/zkxs/cuniq/issues?q=is%3Aissue>
  - <https://github.com/zkxs/cuniq/releases>
  - <https://crates.io/api/v1/crates/cuniq>
  - <https://crates.io/api/v1/crates/line_cardinality>
  - <https://raw.githubusercontent.com/BurntSushi/bstr/master/src/io.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/zkxs/cuniq`) · [data/wave14/enrich/raw/github_com_zkxs_cuniq.json](../../../data/wave14/enrich/raw/github_com_zkxs_cuniq.json) (enrichment confidence 0.72)

</details>
