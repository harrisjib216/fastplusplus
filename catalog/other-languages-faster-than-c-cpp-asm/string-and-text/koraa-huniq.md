# huniq (Rust sort | uniq replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟡 stale

> Rust command-line filter that drops duplicate lines with a hash set, replacing sort -u and sort | uniq -c when order does not matter.

| | |
|---|---|
| **Beats** | GNU `sort -u` (uniq mode) and `sort \| uniq -c` (count mode), awk (`!visited[$0]++` / associative count), GNU datamash (`-s groupby`), and the author's earlier C++ huniq version 1 (SoftwearDevelopment/huniq: std::getline on std::cin, tsl::sparse_set of 128-bit MetroHash128 values, tsl::sparse_map&lt;std::string,size_t&gt; for counts). |
| **Claimed result** | readme.md tables (seconds / peak KB), input = /usr/share/dict/\* repeated N times. Uniq mode (the 'shell' lane is `sort -u` per benchmark.sh, not `sort \| uniq`): 1 repetition huniq2-rust 0.26 s vs huniq1-c++ 1.67 s, awk 1.63 s, datamash 1.78 s, sort -u 7.30 s; 100 repetitions 43.65 s vs 154.99 s (C++), 239.66 s (awk), 285.94 s (datamash), 1062.07 s (sort -u). Count mode (shell = `sort \| uniq -c`), 100 repetitions: 90.80 s vs 150.41 s (C++), 163.13 s (awk), 322.70 s (datamash), 933.67 s. README: 'beats the C++ implementation by a factor of between 6.5 ... and 3.5', 'Compared to sort -u: huniq is around 30 times faster' (28x at 1 repetition, 24x at 100, derived from page data), count mode 'between 25% and 50% faster than the C++ implementation and between 5x and 10x faster than sort \| uniq -c'. Memory: about 29.5 MB vs 26.2 MB (C++) in uniq mode, 132 MB vs 60 MB in count mode. |
| **Workload** | Removing duplicate lines (and, in -c mode, counting them) from /usr/share/dict/\* concatenated 1 to 100 times, timed with the unix time tool via benchmark.sh. |
| **Metric** | throughput |
| **Compiler and flags** | Measured build: huniq 2.1.0 (benchmark_results.txt, commit 78a0680), Rust release profile as of that commit; the fat-LTO and ahash configuration belongs to 2.7.0, not the measured build. Baseline tools' versions and compilers not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: hash tables / hash sets instead of sorting the input ('Sorting is slow'). |
| **Adoption** | 265 stars, 12 forks (GitHub repo page, 2026-10-11); crates.io huniq 2.7.0 (2022-04-20), 354,765 downloads (59,268 recent). |
| **Last commit** | 2024-01-26 |
| **Links** | [repository](https://github.com/koraa/huniq) · [benchmark](https://github.com/koraa/huniq) |

## Verdict

Author-run in January 2020 on an unstated machine with unstated compiler and tool versions: huniq 2.1.0 (no LTO, C xxHash for uniq mode) against the author's C++ v1 (-O3, synced iostreams, tsl::sparse_set of 128-bit MetroHash), awk, datamash and GNU sort -u in the default locale, on /usr/share/dict/\* repeated 1-100 times. The README shows 0.26 s vs 1.67 s (C++) and 7.30 s (sort -u) at 1 repetition and 43.65 vs 154.99 vs 1062.07 s at 100, but the second pass in benchmark_results.txt gives 0.38 vs 2.39 vs 10.40 s and 32.65 vs 130.76 s (4.0x vs C++), so cells move by up to 46% between passes. A competitor's run (cuniq PERFORMANCE.md, Ryzen 7 7800X3D, Windows 11, 32 GiB with 6.03 billion lines) gives a more modest current figure: huniq 2.7.0 6m04.6s vs GNU sort -u 8.32 (8 threads) 14m11.9s (2.3x) and huniq -c 9m32.0s vs sort | uniq -c 28m46.8s (3.0x, derived from page data).

## Use it when

- Deduplicating log lines, URLs, IDs or word lists in a shell pipeline where first-occurrence order is fine or preferred, and you would otherwise run sort -u.
- Streaming dedupe of a live feed (tail -f | huniq): each new distinct line is written as soon as it is seen.
- Frequency reports with huniq -c or -cS when sorted keys are not needed, and the distinct set fits in RAM (the README shows about 132 MB for /usr/share/dict/\* in -c mode).
- Inputs with long records and moderate cardinality: uniq mode holds 8 bytes of hash per distinct record regardless of record length.

## Skip it when

- You need sorted output or uniq -c's padded format: output is in input order (uniq) or random order (-c), and the -c format is 'count record' without padding (open issue #30).
- Short numeric keys: in issue #25 a hyperfine run on 1M seq lines measured awk '!a[\$0]++' at 281.9 ms vs huniq 407.4 ms, and on 60M lines huniq was only about 2 s faster than awk (30 s vs 32 s); the maintainer says numeric keys are not a case huniq optimizes for.
- Very large files where speed matters most: cuniq's PERFORMANCE.md measured huniq 2.7.0 at 6m04.6s vs cuniq --memmap --threads=1 at 2m47.5s on the same 32 GiB file; huniq is single-threaded with no memory-mapped input.
- Distinct sets larger than RAM: unlike GNU sort it never spills to disk, and -c keeps every distinct record in memory.
- Workloads that cannot tolerate a silently dropped distinct line: uniq mode compares 64-bit hashes only.

## How it is fast

It replaces the O(n log n) sort that `sort -u` and `sort | uniq -c` need with a single pass over a hash table (hashing instead of sorting). In uniq mode it stores only a 64-bit aHash of each distinct record in a std HashSet keyed through an identity hasher, so memory grows with the number of distinct records, not their length; input is split with bstr's for_byte_record_with_terminator (memchr), and the set is leaked with mem::forget at exit instead of being freed. Count mode keeps every distinct record as a Vec&lt;u8&gt; in an aHash HashMap.

## Compared with alternatives

Pick huniq over cuniq when you want the deduplicated lines themselves, streamed in first-occurrence order, rather than a count or report; cuniq was 2.2x faster on the 32 GiB count test and adds memory-mapped, multithreaded and HyperLogLog modes. Over runiq it is the simpler choice and was faster in both third-party tables (6m04.6s vs runiq --filter=quick 7m19.4s); hist-rs fits better when you want a count-sorted histogram.

## Integration

| | |
|---|---|
| **Form** | crate (command-line binary; cargo install huniq) |
| **Dependencies** | clap 3.1, anyhow, ahash 0.7.6, bstr 0.2.17 |
| **Minimum toolchain** | not documented (edition 2018; Cargo.lock pins clap 3.x) |
| **Platforms** | any Rust target; no prebuilt binaries (GitHub releases and a musl binary are requested in open issues #23 and #21) |
| **Thread safety** | single-threaded process; not a library |
| **Drop-in for the baseline** | partial — replaces `sort -u` and `sort \| uniq -c` only when sorted output is not required; flags and -c output format differ from GNU uniq. |

## Gotchas

- Correctness bug behind the published numbers: the README tables are the first pass of benchmark_results.txt, last changed in commit 78a0680 'Release 2.1.0' (2020-01-19). In 2.1.0, uniq mode hashed each line with C xxHash's XXH3_64bits_withSecret (vendored, called through bindgen FFI) using `let mut secret = [0u8, 8];`, a 2-byte array instead of 8 bytes, while xxHash requires at least XXH3_SECRET_SIZE_MIN = 136 bytes; every hash therefore read stack memory past the array (an out-of-bounds read in the hot path). Commit f3c1eb0 ('Fix secret... Should be 32 byte', 2.2.1, 2020-05-13) changed it to [0u8; 32], still below 136; aHash replaced it in 2.4. benchmark.sh sends every output to /dev/null and never checks it, so whether 2.1.0 removed duplicates correctly was not verified.
- Uniq mode keeps only a 64-bit aHash per distinct record with a per-process random seed, so a collision silently drops a distinct line and differs from run to run (about a 2.7% chance of at least one collision at 1e9 distinct lines, derived from the birthday bound). The author's C++ v1 used 128-bit MetroHash because 'It has to be 128 bits because of the birthday problem.'
- Errors are printed with println! to stdout and the process exits 0; when the reader closes the pipe early (huniq | head) it panics with 'failed printing to stdout: Broken pipe (os error 32)' (open issue #32, also #26).
- Since commit c51e62c (2.2) removed the BufWriter, output goes through Rust's StdoutLock, which std always wraps in a LineWriter, so every newline-terminated output record is its own write(2) call; the README timings were taken with 2.1.0's BufWriter. Count mode also allocates a fresh Vec&lt;u8&gt; for every input line (BufRead::split) and its output order changes between runs.

## Known shortcomings

- No hardware, compiler or version stated; the uniq-mode 'shell' lane is sort -u; the C++ v1 comparator is built -O3 but uses synced std::getline plus tsl::sparse_set, so the gain is I/O and hash-table choice, not the language; 64-bit hash-only dedup; last commit 2024-01-26.
- Correctness bug behind the numbers: the README tables come from huniq 2.1.0 (benchmark_results.txt, commit 78a0680), whose uniq mode called C xxHash XXH3_64bits_withSecret with a 2-byte secret [0u8, 8] (minimum 136 bytes), so every hash read past the array; fix f3c1eb0 in 2.2.1 moved it to 32 bytes, still under 136; outputs were never checked. The record's compiler_and_flags (fat LTO, ahash) describes 2.7.0, not the measured build. The second pass varies up to 46% (4.0x vs C++ at 100 repetitions); sort -u ran in the default locale; since c51e62c one write(2) per output line (LineWriter); broken-pipe panic (issue #32 open). A third-party cuniq run of 2.7.0: 2.3x vs GNU sort -u, with cuniq itself 2.2x faster than huniq.

## Caveats and trade-offs

Author-run with no machine, compiler or tool versions stated, and the huniq version measured is not named; benchmark.sh loops until aborted and times each tool with `time` while a shell loop cats /usr/share/dict/\* into it, so the producer can bound the fastest lanes. Uniq mode stores only 64-bit ahash values (128-bit MetroHash in v1), so collisions can drop lines. The C++ comparator is the author's own v1 built at -O3 but reading with std::getline on std::cin without sync_with_stdio(false) and using the memory-optimised tsl::sparse_set/sparse_map, so the 3.5x to 6.5x reflects I/O and hash-table choices rather than Rust versus C++. Hash versus sort is an algorithm difference. Licence BSD-3-Clause per Cargo.toml and the readme text; GitHub detects no LICENSE file. A competitor's table (cuniq PERFORMANCE.md) measured huniq 2.7.0 at 6m04.595s on a 32 GiB file against 14m11.935s for `sort -u | wc -l`. [retier] The README tables come from huniq 2.1.0, whose uniq mode called C xxHash XXH3_64bits_withSecret with a 2-byte secret [0u8, 8] (minimum 136 bytes), so every hash read past the array (fix f3c1eb0 in 2.2.1 moved it to 32 bytes, still under 136); outputs were never checked. The second pass varies up to 46% (4.0x vs C++ at 100 repetitions); sort -u ran in the default locale; since c51e62c one write(2) per output line; broken-pipe panic (issue #32 open). A third-party cuniq run of 2.7.0: 2.3x vs GNU sort -u, with cuniq itself 2.2x faster than huniq.

Output is in first-occurrence order, not sorted; memory is much higher than sort | uniq (29.5 MB vs 9.7 MB in unique mode, 132 MB vs about 12 MB in -c mode per README tables); -c output order is unstable.

## Maintenance

Stale: last release 2.7.0 on 2022-04-20 and last commit 2024-01-26 (a trivial trim_end change), with the broken-pipe panic still open; BSD-3-Clause per Cargo.toml and the readme text (GitHub detects no LICENSE file), one 217-line Rust file and easy to vendor; 265 stars and 355,150 crates.io downloads; the README benchmark measured 2.1.0, whose hash call had an out-of-bounds read, and has not been re-run since.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party readme table produced by the public benchmark.sh, but no CPU, compiler versions or tool versions are stated and the measured huniq version is not named, so it falls short of A.
- **Verifier notes:** Numbers match the readme; corrected the uniq-mode 'shell' lane to `sort -u` (benchmark.sh meas_shell). Shortcomings to record: no hardware, compiler or version info; producer-bound pipeline harness; C++ comparator is the author's own v1 with synced iostreams and tsl::sparse_set (C++ side at -O3); 64-bit hash-only dedup. maintenance stale (last commit 2024-01-26).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/readme.md>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/SoftwearDevelopment/huniq/HEAD/Makefile>
  - <https://raw.githubusercontent.com/SoftwearDevelopment/huniq/HEAD/readme.md>
  - <https://raw.githubusercontent.com/SoftwearDevelopment/huniq/HEAD/huniq.cc>
  - <https://github.com/koraa/huniq>
  - <https://github.com/koraa/huniq/commits>
  - <https://crates.io/api/v1/crates/huniq>
- **Sources the enricher read:**
  - <https://github.com/koraa/huniq>
  - <https://github.com/koraa/huniq/commits/master>
  - <https://github.com/koraa/huniq/commits/main>
  - <https://github.com/koraa/huniq/commits/main/benchmark_results.txt>
  - <https://github.com/koraa/huniq/commit/f3c1eb0>
  - <https://github.com/koraa/huniq/commit/c51e62c>
  - <https://github.com/koraa/huniq/issues?q=is%3Aissue>
  - <https://github.com/koraa/huniq/issues/25>
  - <https://github.com/koraa/huniq/issues/26>
  - <https://github.com/koraa/huniq/issues/32>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/readme.md>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/benchmark_results.txt>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/koraa/huniq/HEAD/test.sh>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/Cargo.toml>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/src/main.rs>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/src/xxhash.rs>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/src/xxhash_bindings.rs>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/src/xxhash_bindings.h>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/build.rs>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/benchmark.sh>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/readme.md>
  - <https://raw.githubusercontent.com/koraa/huniq/78a068002b894c6b216797f4722b9a8652217e3c/.gitmodules>
  - <https://raw.githubusercontent.com/SoftwearDevelopment/huniq/HEAD/huniq.cc>
  - <https://raw.githubusercontent.com/SoftwearDevelopment/huniq/HEAD/Makefile>
  - <https://raw.githubusercontent.com/SoftwearDevelopment/huniq/HEAD/readme.md>
  - <https://raw.githubusercontent.com/Cyan4973/xxHash/v0.7.2/xxhash.h>
  - <https://raw.githubusercontent.com/Cyan4973/xxHash/v0.7.2/xxh3.h>
  - <https://raw.githubusercontent.com/Cyan4973/xxHash/v0.7.3/xxhash.h>
  - <https://raw.githubusercontent.com/Cyan4973/xxHash/v0.7.3/xxh3.h>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/io/stdio.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/1.80.0/library/std/src/io/buffered/linewritershim.rs>
  - <https://raw.githubusercontent.com/zkxs/cuniq/HEAD/PERFORMANCE.md>
  - <https://crates.io/api/v1/crates/huniq>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/koraa/huniq`) · [data/wave14/enrich/raw/github_com_koraa_huniq.json](../../../data/wave14/enrich/raw/github_com_koraa_huniq.json) (enrichment confidence 0.75)

</details>
