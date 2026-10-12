# needletail (Rust FASTA/FASTQ parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust zero-copy FASTA/FASTQ parser; 1.75x faster than C kseq.h on plain 4-line FASTQ in lh3's 2020 biofast run.

| | |
|---|---|
| **Beats** | kseq.h from klib (C FASTA/FASTQ parser) |
| **Claimed result** | lh3/biofast README and fqcnt/README.md, fqcnt table (CPU seconds, hyperfine average): needletail plain 0.8 s vs C kseq.h 1.4 s (1.75x, derived from page data); gzip input 9.3 s vs 9.7 s (about equal, since decompression dominates). For reference, rust-bio in the same table is 2.4 s plain and 10.0 s gzip. |
| **Workload** | Parsing a 4-line FASTQ file of 5,682,010 records and counting records, sequence length and quality length; plain and gzip-compressed input. |
| **Metric** | throughput |
| **Hardware** | CentOS 7 server with two EPYC 7301 CPUs and 1 TB memory |
| **Compiler and flags** | C: gcc-4.8.5 with -g -Wall -O2 (fqcnt/Makefile), not -O3. Rust: 'cargo install' (release profile, default opt-level 3) with needletail = "0.4" (biofast Cargo.toml); rustc version not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 214 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/onecodex/needletail) · [benchmark](https://github.com/lh3/biofast) |

## Verdict

lh3/biofast (2020, by the author of kseq.h) counted records, bases and quality characters in a 5,682,010-record 4-line FASTQ (M_abscessus_HiSeq.fq) on a CentOS 7 server with two EPYC 7301 CPUs, with hyperfine CPU time averaged over at least ten rounds. needletail 0.4 took 0.8 s against 1.4 s for C kseq.h (gcc 4.8.5, -g -Wall -O2, zlib gzread) on plain input, about 1.75x (derived from page data), and 9.3 s against 9.7 s on gzip input. The rustc version is not stated, and no newer needletail-versus-C run was found.

## Use it when

- Rust tools that stream short-read Illumina-style 4-line FASTQ or FASTA from uncompressed files and only need slices of id, sequence and quality (read counting, k-mer counting, QC statistics).
- You want one entry point that auto-detects FASTA or FASTQ and gzip, bzip2, xz or zstd input, including multi-member gzip and stdin.
- Pipelines that already use its k-mer helpers (canonical k-mers with reverse complement, 2-bit bit_kmers up to k=32) next to parsing.
- Python scripts that need a faster FASTX iterator than pure-Python parsers, through the PyO3 bindings (parse_fastx_file, parse_fastx_string).
- Files with Windows CRLF line endings, which are trimmed transparently and reported by line_ending().

## Skip it when

- Multi-line (wrapped) FASTQ: the FASTQ reader assumes exactly four lines per record and stops with an error, while kseq.h parses multi-line FASTA and FASTQ.
- Gzip-compressed input where decompression dominates: biofast shows no parser gain (9.3 s vs 9.7 s), so overall speed depends on the decompressor, not on needletail.
- Damaged or partially downloaded files you want to salvage: the first parse error (bad '@', bad '+', unequal sequence and quality lengths) sets the reader to finished, so later records are unreachable (open issue #118, August 2026).
- C or C++ code bases: there is no C API, and kseq.h is a single header with no dependencies.
- Parallel record-batch processing: parsing is single-threaded and multithreading optimisation is an open issue (#111); paraseq's documentation (search snippet only) claims higher throughput for record-set, multi-threaded use.

## How it is fast

Since 0.4 the parser is adapted from seq_io: it fills a 64 KiB buffer completely, finds the four line ends of each FASTQ record with memchr, and hands back the record as offsets into that buffer, so id, sequence and quality are never copied. Only the '@' start byte, the '+' separator and equal sequence/quality lengths are checked, and an incomplete record at the buffer end is shifted to the front (make_room) or the buffer is grown. kseq.h, the baseline, reads 16 KiB at a time and copies name, comment, sequence and quality into four growable kstrings for every record, finding the end of the name with a per-byte isspace loop. In biofast it also reads plain files through zlib's gzread. For multi-line FASTA, seq() strips newlines into a fresh Vec only when the record contains them.

## Compared with alternatives

Among the catalogued bioinformatics siblings, z-fasta is a CLI for indexing and extracting from FASTA, and A\*PA2 and Sassy are aligners; pick needletail when a Rust program has to stream FASTA or FASTQ records itself, and z-fasta when you need samtools-faidx-style random access.

## Integration

| | |
|---|---|
| **Form** | crate (rlib, plus cdylib for the Python extension) |
| **Dependencies** | buffer-redux, bytecount (runtime-dispatch-simd), memchr; the default 'compression' feature adds flate2, bzip2 0.6, liblzma and zstd; optional pyo3 0.29 for the 'python' feature |
| **Minimum toolchain** | Rust edition 2021 (1.56 or newer); no rust-version is declared, so the real floor set by memchr 2.7, pyo3 0.29 and the compression crates is not documented |
| **Platforms** | any Rust target with std; SIMD comes from memchr and bytecount's runtime dispatch; Python wheels built for macOS (x86 and ARM) and Ubuntu x86 per README |
| **Thread safety** | FastxReader requires Send, so a reader can be moved to another thread, but one reader is consumed by one thread and each record borrows the reader's buffer until the next call; no built-in parallel parsing. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness asymmetry: in lh3/biofast, fqcnt_c1_kseq.c copies name, comment, sequence and quality into kstrings per record, splits the name at whitespace and reads even the plain file through zlib's gzopen/gzread, while fqcnt_rs2_needletail.rs only takes the lengths of borrowed slices. The 1.4 s vs 0.8 s gap therefore measures zero-copy design and I/O path, not Rust against C (the Crystal kseq.h port lands at 1.5 s). The C side is gcc 4.8.5 at -O2, biofast has no Cargo.lock (needletail '0.4', rustc and the flate2 decoder backend are unrecorded), and the C program sums lengths in 32-bit int while the Rust one uses u64.
- FastxReader::next() is a lending iterator, not std::iter::Iterator: records borrow the internal buffer, so keep data by copying it (for example seq().into_owned()), and adapters such as map or collect are not available (issue #70).
- A record larger than the buffer makes it double up to 8 MiB and then grow in 8 MiB steps with no upper bound, so one huge FASTA record (a whole chromosome) is held in memory in full; for multi-line FASTA, seq() allocates a newline-free copy.
- bit_kmers panics with 'attempt to multiply with overflow' for k above 32 (issue #58). README still shows needletail = "0.6.0" and the CHANGELOG stops at 0.7.1, while crates.io is at 0.7.3.

## Known shortcomings

- Stale 2020 biofast run on needletail 0.4 (0.8 s vs kseq.h 1.4 s plain); the C side is gcc 4.8.5 -O2, not -O3, reads plain input through gzread, and the test is 4-line FASTQ only; no gain on gzip.
- Harness asymmetry in lh3/biofast: the kseq C side copies name, comment, seq and qual into kstrings, splits the name with a per-byte isspace and reads the plain file via zlib gzread, while the Rust side only takes borrowed slice lengths, so 1.4 s vs 0.8 s measures a zero-copy design, not the language; also gcc 4.8.5 -O2, no Cargo.lock, 32-bit int C counters. The first parse error ends iteration (#118); 4-line FASTQ only; README version stale (0.6.0 vs crate 0.7.3).

## Caveats and trade-offs

This is an independent benchmark by the author of kseq.h, but it dates from 2020 and measured needletail 0.4 (the current README shows 0.6.0), so the numbers are stale. The C baseline is gcc-4.8.5 at -O2, not -O3. Plain-file C input still goes through zlib's gzread, and needletail handles only 4-line FASTQ against kseq.h's multi-line parser, which favours needletail. gzip input shows no gain (9.3 s vs 9.7 s). Needletail's own README claims only to aim to be 'as fast as the readfq C library' and has no benchmark section. The Crystal, Nim and Julia ports of kseq.h do not beat C in the same table. [retier] Harness asymmetry in lh3/biofast: the kseq C side copies name, comment, seq and qual into kstrings, splits the name with a per-byte isspace and reads the plain file via zlib gzread, while the Rust side only takes borrowed slice lengths, so 1.4 s vs 0.8 s measures a zero-copy design, not the language; gcc 4.8.5 -O2, no Cargo.lock, 32-bit int C counters. The first parse error ends iteration (#118); 4-line FASTQ only.

Rust API (no C++ binding in repo). Parses FASTA and 4-line FASTQ only, while the baseline kseq.h also handles multi-line records, which the biofast table marks in its comments column.

## Maintenance

Actively maintained by One Codex (last commit 2026-10-06; 0.7.3 on crates.io since 2026-04-20; about 604,000 downloads), MIT-licensed, fuzz-tested and small, so it is safe to depend on, although the only C comparison is the 2020 biofast run on 0.4.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now C.
- **Tier reason:** lh3/biofast is an independent, well-known suite by the author of kseq.h, not of needletail. It has public code (fqcnt/fqcnt_rs2_needletail.rs, fqcnt/fqcnt_c1_kseq.c, fqcnt/Makefile), the C compiler and flags (gcc-4.8.5, -g -Wall -O2) and the CPU (2x EPYC 7301). The rustc version is not stated, so it falls short of A.
- **Retiered** B to C: Enricher: the kseq C baseline copies every record field into kstrings and splits the name per byte while the Rust side borrows slices, so lh3's 1.75x measures a zero-copy design rather than equal work (gcc 4.8.5 -O2, 2020 versions); unequal-work precedent (SHOGUN): B to C.
- **Verifier notes:** Numbers confirmed on lh3/biofast README and fqcnt/README.md (0.8 s vs 1.4 s plain, 9.3 s vs 9.7 s gzip). Shortcomings: stale 2020 run on needletail 0.4; C side gcc-4.8.5 -O2 rather than -O3; feature scope differs (4-line FASTQ only vs multi-line); C reads plain input through gzread; no gain on gzip input; the parser algorithm comes from seq_io. Metadata confirmed: MIT, 214 stars, last commit 2026-10-06 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/README.md>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/README.md>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/Makefile>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/fqcnt_rs2_needletail.rs>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/fqcnt_c1_kseq.c>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/Cargo.toml>
  - <https://github.com/onecodex/needletail>
  - <https://github.com/onecodex/needletail/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/README.md>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/src/parser/mod.rs>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/src/parser/fastq.rs>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/src/parser/fasta.rs>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/src/parser/utils.rs>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/src/parser/record.rs>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/src/errors.rs>
  - <https://raw.githubusercontent.com/onecodex/needletail/HEAD/benches/benchmark.rs>
  - <https://github.com/onecodex/needletail>
  - <https://github.com/onecodex/needletail/commits/master>
  - <https://github.com/onecodex/needletail/issues>
  - <https://github.com/onecodex/needletail/issues/34>
  - <https://github.com/onecodex/needletail/issues/118>
  - <https://crates.io/api/v1/crates/needletail>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/README.md>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/README.md>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/Makefile>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/fqcnt_rs2_needletail.rs>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/fqcnt_c1_kseq.c>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/fqcnt/fqcnt_rs1_rustbio.rs>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/lh3/biofast/HEAD/lib/kseq.h>
  - <https://crates.io/api/v1/crates/helicase>
  - <https://crates.io/api/v1/crates/paraseq>
  - <https://raw.githubusercontent.com/imartayan/helicase/HEAD/README.md>
  - <https://raw.githubusercontent.com/imartayan/helicase/HEAD/bench/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/onecodex/needletail`) · [data/wave14/enrich/raw/github_com_onecodex_needletail.json](../../../data/wave14/enrich/raw/github_com_onecodex_needletail.json) (enrichment confidence 0.8)

</details>
