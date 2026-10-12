# rust-sort (Rust GNU sort replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟡 stale

> Rust `sort` clone (crate gnu-sort) with rayon, mmap and an integer radix path; timed only against the macOS system sort.

| | |
|---|---|
| **Beats** | macOS system /usr/bin/sort (Apple's BSD-derived sort shipped with macOS 15.5), labelled 'GNU sort (system)' in the README; benchmark.sh defaults REFERENCE_SORT to the system 'sort' and its own usage text labels /usr/bin/sort as BSD and /usr/local/bin/gsort as GNU. uutils (rust_coreutils) sort is a second column. Current GNU coreutils sort was not measured. |
| **Claimed result** | README table (one timed run each) against the macOS system /usr/bin/sort labelled 'GNU sort (system)': 1M lines -n 1.00 vs 0.03 s (33.3x); 1M text 0.57 vs 0.03 (19.0x); 1M -rn 0.95 vs 0.03; 10M -n 6.21 vs 0.45 (13.8x); 10M text 6.00 vs 0.43 (14.0x); 10M -f 8.09 vs 0.42 (19.3x); 10M -g 24.17 vs 2.24; 10M -u 2.50 vs 0.55; 10M -s 3.28 vs 0.55. The 10M -f row timed a plain byte sort (see caveats) and the -n and -rn rows run paths that misorder or reverse their output, so only the plain text rows against the BSD sort stand. |
| **Workload** | benchmark.sh: 100K, 1M and 10M lines generated deterministically with seq/awk (not random): numbers (i\*7919) mod 32749 (at most 32749 distinct small integers), strings 'str_'+((i\*13) mod 9973)+'_text' (9973 distinct values), floats and i mod 100 duplicates; flags -n, text, -rn, -u, -nu, -f, -R, -s, -g, -nru; each command timed once with /usr/bin/time -l (10 ms resolution) in the user's default locale. |
| **Metric** | throughput |
| **Hardware** | Apple M2 Max MacBook Pro, 32 GB, macOS 15.5 |
| **Compiler and flags** | rust-sort: Cargo.toml [profile.release] opt-level = 3, lto = true, codegen-units = 1, panic = abort; rustc version not stated (rust-version 1.70). Baseline: Apple's prebuilt system sort, build flags unknown. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: zero-copy operations, SIMD acceleration and intelligent algorithm selection; multi-threaded. |
| **Adoption** | 1 star; crates.io 982 downloads (gnu-sort 1.0.5, metadata says MIT OR Apache-2.0) |
| **Last commit** | 2025-09-11 |
| **Links** | [repository](https://github.com/acefsm/rust_sort) · [benchmark](https://github.com/acefsm/rust_sort) |

## Verdict

benchmark.sh timed each case once with /usr/bin/time (10 ms resolution) on an Apple M2 Max under macOS 15.5. The column labelled 'GNU sort' is the macOS system sort, not GNU coreutils. Rows like 1M -n 1.00 s vs 0.03 s (33x) and 10M -n 6.21 s vs 0.45 s (13.8x) pit rayon on all cores against that system binary, on low-cardinality arithmetic data (at most 32749 distinct integers, 9973 distinct strings). Against uutils sort the same table gives 0.6x to 3.0x, and the 10M text and -f rows ran a code path that ignores -f (see gotchas).

## Use it when

- Experiments with sorting single plain-integer files (every line an optionally signed integer of at most 18 digits) on a multi-core machine, where its parallel radix path applies.
- Sorting a single ASCII file under 100 MiB in ascending byte or C-locale order with no -r, where the code path is the simple mmap and par_sort one.
- As reading material on mmap plus rayon line sorting, not as a production `sort`.

## Skip it when

- Any pipeline that depends on GNU-correct output: by code reading, several common flag combinations give wrong order or keep duplicates (see gotchas), and the README says it has not been run against the GNU coreutils test suite.
- Several input files, or very large inputs: each file is mapped and sorted whole in memory on its own thread. Open issue #1 (January 2026, unanswered) reports `LC_ALL=C sort -u large_file*txt` on 1.5 TB being OOM-killed at about 92 GB RSS on a 96 GB Debian 13 box.
- Reading stdin beyond 2 GB: sort_stdin reads through take(2 GiB) and silently drops the rest.
- -u or -s on many duplicates: its own table loses to uutils sort (10M -u 0.55 s vs 0.39 s, -s 0.55 s vs 0.31 s).
- Locale-sensitive work: LC_COLLATE support calls strcoll per comparison and is labelled experimental.

## How it is fast

Zero-copy line slices into an mmap with rayon par_sort_unstable_by, compared by an AVX2, SSE4.2 or NEON memcmp-style byte loop. For -n on 1000 or more lines whose first 100 lines are plain integers, each line is parsed to an i64 and sorted with an LSD byte radix sort (2 passes for the benchmark's values below 32749). -R groups identical lines in a HashMap and shuffles the groups. The reference sort is the macOS system sort, so much of the reported gap is all cores against one process, plus a radix sort on low-cardinality integers.

## Compared with alternatives

Rarely: uutils coreutils sort is the more mature Rust `sort`, is tested against GNU behaviour and beats rust-sort on -u and -s in rust-sort's own table. For dedup or counting jobs, huniq, runiq or cuniq were measured against real GNU sort. Pick rust-sort only to experiment with its integer radix path on a single plain-integer file.

## Integration

| | |
|---|---|
| **Form** | crate (binary `sort` from crates.io package gnu-sort; source build via cargo build --release) |
| **Dependencies** | clap =4.4.18, rayon =1.7.0, memmap2, crossbeam-channel, tempfile, num_cpus, itertools, rand 0.8, parking_lot, libc, thiserror |
| **Minimum toolchain** | Rust 1.70 (rust-version in Cargo.toml) |
| **Platforms** | Benchmarked only on macOS 15.5 aarch64 (Apple M2 Max); SIMD compare has runtime-detected AVX2/SSE4.2 (x86-64) and NEON (aarch64) paths; commits mention i686 and Windows line-ending fixes; issue #1 ran it on Debian x86_64 |
| **Thread safety** | Not applicable (CLI); uses the global rayon pool, sized by RAYON_NUM_THREADS |
| **Drop-in for the baseline** | partial — it parses GNU sort's flags, but by code reading -r is applied twice outside the numeric path, inputs over 100 MiB drop most flags, and multi-file merges ignore -n/-r/-f/-u, so its output differs from GNU sort on common inputs |

## Gotchas

- By code reading at HEAD (not executed), the benchmark's 10M text and -f rows ran a different code path than the smaller rows. Single files over 100 MiB go to external_sort.rs, whose API passes only the numeric and unique flags, so -f, -r, -g, -k/-t, -R, -s and -b are ignored there. The 10M strings file is 138.9 MB. Its -f row (0.42 s) costs the same as the plain text row (0.43 s), while at 1M lines -f costs 0.05 s vs 0.03 s. The all-lowercase test data hid this from the correctness check, so the '19x faster case-insensitive' headline timed a plain byte sort.
- Global -r without -k is reversed twice for non-numeric modes: zero_copy.rs compare_with_config already reverses on config.reverse, and core_sort.rs sort_lines_direct and compare_lines_direct reverse again on args.reverse, which lib.rs copies from config.reverse. So `sort -r`, `-rf`, `-rg` and `-sr` should come out ascending. -rn escapes because its radix path reverses the vector once, and -rn and -nru are the only reverse cases the benchmark runs.
- The -n radix fast path checks only the first 100 lines for 'simple integer'. parse_integer_fast then computes (byte - b'0') for every byte with no validation, which wraps in release builds. Later lines with a decimal point, spaces, text or more than 18 digits get garbage keys and are silently misordered. -u also dedups by exact bytes when no -k is given, so `sort -nu` keeps both '1' and '01', and `sort -fu` keeps both 'A' and 'a'.
- Other merge paths are broken. The external k-way merge (used when a file exceeds the computed chunk, e.g. above 448 MB on macOS where available memory is hard-coded to 4096 MB) reverses MergeItem::cmp and then wraps items in Reverse inside a max-heap, so it pops the largest head first and emits unsorted output. It also ignores -n. The multi-file merge compares raw bytes and never deduplicates.

## Known shortcomings

- Off-baseline: the 'GNU sort' column is the macOS system sort (BSD-derived; benchmark.sh defaults to system sort and its usage text calls /usr/bin/sort BSD); rayon parallelism vs a single-process sort; low-cardinality arithmetic data; one /usr/bin/time run; the two tables disagree.
- Harness flaw by code reading: files over 100 MiB go through external_sort.rs, which passes only the numeric and unique flags, and the 10M-line strings file is 138.9 MB, so the 10M -f row (0.42 s vs 0.43 s for plain text) timed a plain byte sort and the '19x case-insensitive' headline is invalid. Correctness bugs: -r without -k is reversed twice outside the numeric path (ascending output); -n's radix path checks only the first 100 lines and then uses an unvalidated byte - b'0' (wraps in release), misordering later decimal or text lines; -nu and -fu dedupe by exact bytes; the external merge's double-reversed heap emits unsorted output; multi-file merge ignores -n, -r, -f and -u; stdin is silently truncated at 2 GB. Issue #1: 92 GB RSS and OOM on 1.5 TB input. The baseline is the macOS BSD sort labelled 'GNU sort'.

## Caveats and trade-offs

Baseline mislabelled: the 'GNU sort (system)' column is the macOS system sort, which is Apple's BSD-derived sort, not GNU coreutils (benchmark.sh defaults to the system 'sort' and its usage text itself names /usr/bin/sort BSD and gsort GNU); eBay tsv-utils TipsAndTricks reports current GNU sort is often more than twice as fast as the macOS sort, and uutils sort beats the same column by about 8x at 10M lines, so the speedup over current GNU sort is probably far smaller than 33x. rust-sort runs rayon parallel sorts (par_sort_unstable_by, parallel radix and hash sort) above 8192 lines on a 12-core M2 Max against a single-process system sort. Test data are low-cardinality arithmetic sequences (at most 32749 distinct small integers, 9973 distinct strings), which suit its radix and hash paths, although the README says 'randomly generated'. Each case is one /usr/bin/time run with 10 ms resolution, though performance_comparison_table.md claims 'average of multiple runs'; the two result tables disagree slightly and both are dated December 2024 while the repo's code is from 2025. macOS only; not validated against the GNU coreutils test suite. LICENSE file is MIT while Cargo metadata says MIT OR Apache-2.0. 1 star; marketing-style README. [retier] Baseline mislabelled: the 'GNU sort (system)' column is Apple's BSD-derived macOS sort (benchmark.sh defaults to the system sort and its own usage text names /usr/bin/sort BSD and gsort GNU); eBay tsv-utils reports current GNU sort often more than twice as fast as the macOS sort and uutils sort beats the same column by about 8x at 10M lines. Harness flaw by code reading: files over 100 MiB go through external_sort.rs, which passes only the numeric and unique flags, and the 10M-line strings file is 138.9 MB, so the 10M -f row (0.42 s vs 0.43 s for plain text) timed a plain byte sort and the '19x case-insensitive' headline is invalid. Correctness bugs: -r without -k is reversed twice outside the numeric path (ascending output); -n's radix path validates only the first 100 lines and then uses an unvalidated byte - b'0' (wraps in release), misordering later decimal or text lines; -nu and -fu dedupe by exact bytes; the external merge's double-reversed heap emits unsorted output; multi-file merge ignores -n, -r, -f and -u; stdin is silently truncated at 2 GB. Issue #1: 92 GB RSS and OOM on 1.5 TB input. One run per cell, macOS 15.5, no CPU model.

Not byte-identical GNU behaviour in every flag; unique and stable modes lose to uutils per its own table.

## Maintenance

Stale since 2025-09-11 (44 commits written 2025-09-07 to 09-11), 1 star, one open unanswered OOM bug. MIT LICENSE file, but the crate metadata says MIT OR Apache-2.0. The code is small enough to read but has the correctness bugs listed in gotchas, so it is not usable as a `sort` replacement without fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** First-party README table produced by the repo's benchmark.sh (one /usr/bin/time run per case) on an Apple M2 Max; rustc version is not stated and the baseline is a prebuilt macOS system binary of unknown build, so not A. The column labelled 'GNU sort' is the macOS system sort, which is not GNU coreutils, so the claim against GNU sort is overstated.
- **Retiered** C to D: Enricher: the headline -f row timed a plain byte sort (files over 100 MiB bypass case folding), the baseline is the macOS BSD sort labelled 'GNU sort', and the -n and -r paths emit misordered or ascending output, so no row is a valid like-for-like measurement against GNU sort. Crippled or mislabelled baseline with wrong work in the measured rows: D (stb-zip precedent applies to the -f row, kept and documented per the keep-and-document rule).
- **Verifier notes:** Numbers match the README, but the baseline is the macOS system sort (BSD-derived), not GNU coreutils sort, so the 'faster than GNU sort' claim is untested; record shortcomings: mislabelled baseline, multi-threaded vs single-threaded, low-cardinality deterministic data, single 10 ms-resolution run, conflicting tables. Tier stays C; consider D if the orchestrator treats an off-baseline system sort as no valid measurement against GNU sort.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-83 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/performance_comparison_table.md>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/core_sort.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/locale.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/simd_compare.rs>
  - <https://github.com/acefsm/rust_sort>
  - <https://github.com/acefsm/rust_sort/commits>
  - <https://github.com/acefsm/rust_sort/tree/main/src>
  - <https://crates.io/api/v1/crates/gnu-sort>
  - <https://github.com/eBay/tsv-utils/blob/master/docs/TipsAndTricks.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/performance_comparison_table.md>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/core_sort.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/external_sort.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/radix_sort.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/zero_copy.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/locale.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/simd_compare.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/adaptive_sort.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/hash_sort.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/src/config.rs>
  - <https://raw.githubusercontent.com/acefsm/rust_sort/HEAD/scripts/check.sh>
  - <https://github.com/acefsm/rust_sort>
  - <https://github.com/acefsm/rust_sort/commits>
  - <https://github.com/acefsm/rust_sort/issues?q=is%3Aissue>
  - <https://github.com/acefsm/rust_sort/issues/1>
  - <https://github.com/acefsm/rust_sort/tree/main/scripts>
  - <https://crates.io/api/v1/crates/gnu-sort>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/acefsm/rust_sort`) · [data/wave14/enrich/raw/github_com_acefsm_rust_sort.json](../../../data/wave14/enrich/raw/github_com_acefsm_rust_sort.json) (enrichment confidence 0.75)

</details>
