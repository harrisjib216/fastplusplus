# noodles (noodles-fasta FAI indexer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust bioinformatics format libraries; noodles-fasta builds samtools-compatible .fai indexes about 6x faster than samtools faidx.

| | |
|---|---|
| **Beats** | samtools faidx (samtools 1.24 with HTSlib 1.24, C) |
| **Claimed result** | bench/index/REPORT.md Table 3 (zebrac mean, warm cache): Genome 1.3640 s (noodles) vs 8.1614 s (samtools), about 6.0x faster (derived from page data); Table 4 throughput 2203.5 MiB/s vs 368.3 MiB/s. Transcriptome 0.4111 s vs 1.7112 s, about 4.2x (derived from page data). Proteome 0.0176 s vs 0.0650 s, about 3.7x (derived from page data). Synthetic scaling (Table 12, 100 records): 1000 MiB 0.3981 s vs 2.7896 s, about 7.0x (derived from page data). Peak RSS on the genome is 3.59 MiB vs 9.31 MiB. |
| **Workload** | Build a samtools-compatible .fai index of the Homo sapiens GRCh38 primary assembly (Ensembl release 113, about 2.9 GiB uncompressed FASTA), warm page cache, 5 measured samples after 3 warmups, timed with zebrac v0.6.2; the noodles lane is a small CLI wrapper written by the z-fasta author around noodles-fasta 0.66.0 (fs::index then fai::fs::write). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X, Linux x86_64, warm page cache (named in the z-fasta README for the v0.3.5 run of 2026-10-10, whose index table matches REPORT.md exactly; REPORT.md itself names no CPU). |
| **Compiler and flags** | noodles wrapper (tools/noodles_wrapper, noodles-fasta 0.66.0, noodles-core 0.20): cargo build --locked --release with the default release profile (opt-level 3, no LTO, no custom RUSTFLAGS), rustc version not stated; binary stripped with strip --strip-unneeded. samtools 1.24 and HTSlib 1.24 built from release tarballs by tools/install.sh with plain ./configure and make and no explicit CFLAGS, so the upstream Makefile default CFLAGS = -g -Wall -O2 applies (htslib and samtools Makefiles at tag 1.24); C compiler and version not stated; samtools linked against the shared libhts; binary stripped. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 727 stars; noodles-fasta crate 484,738 downloads on crates.io (latest 0.67.0) |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/zaeleus/noodles) · [benchmark](https://github.com/eneskemalergin/z-fasta/blob/main/bench/index/REPORT.md) |

## Verdict

An independent benchmark in the z-fasta repository (zebrac v0.6.2, 5 samples after 3 warmups, warm cache, AMD Ryzen 9 3950X per the z-fasta README) timed 'rm -f x.fai; tool index x' for a noodles-fasta 0.66.0 wrapper (cargo release profile, rustc version not stated) and samtools 1.24 faidx (HTSlib 1.24, default -O2, compiler not stated): GRCh38 primary assembly 1.364 s against 8.161 s (about 6.0x), GENCODE v46 transcripts 0.411 s against 1.711 s (about 4.2x), UniProt human proteome 0.018 s against 0.065 s (about 3.7x).

## Use it when

- Rust pipelines that need to build or read .fai indexes of large, uniformly wrapped FASTA (genomes, transcriptomes) without shelling out to samtools.
- Batch indexing of many reference or assembly files where samtools' per-file start-up and byte-at-a-time scan dominate (about 2.2 GB/s against 0.37 GB/s on GRCh38, warm cache).
- Projects that already use noodles for BAM, CRAM or VCF and want one consistent, MIT-licensed Rust dependency for reference handling.
- Low-memory environments: peak RSS was 3.6 MiB on the genome against 9.3 MiB for samtools.

## Skip it when

- FASTA with ragged line widths, trailing whitespace or mixed LF/CRLF endings: the indexer rejects them (as samtools does); a lenient tool such as z-fasta's .zfi mode is needed.
- bgzip-compressed FASTA: fs::index opens the file as plain text and writes no .gzi, while samtools faidx indexes BGZF FASTA directly; region queries on bgzipped FASTA were also far slower than samtools in issue #146 (12.8 s against 0.024 s before PR #147 in 2023, still about 10x slower after it).
- You need a command-line tool: noodles ships examples, not a supported faidx binary, and its README calls the API experimental.
- Maximum indexing speed: in the same benchmark the Zig z-fasta indexer is about 3.6x faster than noodles on the genome.

## How it is fast

The indexer reads through a BufReader and finds line ends with memchr (SIMD-accelerated byte search) on each buffered chunk, counting a whole line's bases at once and only checking the first byte of each line for '&gt;'. HTSlib 1.24's fai_build_core, which samtools faidx uses, instead pulls every byte through bgzf_getc into a per-character state machine that also tests each byte with isgraph/isspace and inserts names into a hash table to reject duplicates. The samtools build in the comparison is the upstream default -O2 with a shared libhts, and the scaling table suggests roughly 15 ms of fixed samtools startup against about 3.5 ms for the noodles wrapper (derived from page data).

## Compared with alternatives

Among the bioinformatics siblings (mosdepth for depth, sambamba and mako against samtools view/sort, rasusa for subsampling), noodles is the one to pick when you need a Rust library rather than a finished command-line tool, here for FASTA indexing; pick z-fasta instead when raw indexing speed or tolerance of messy FASTA matters more than a broad format library.

## Integration

| | |
|---|---|
| **Form** | crate (noodles-fasta 0.67.0, or the noodles meta crate with the fasta feature) |
| **Dependencies** | bstr, memchr, noodles-bgzf, noodles-core; tokio only with the async feature |
| **Minimum toolchain** | Rust 1.91.0 (workspace rust-version), edition 2024 |
| **Platforms** | any platform Rust supports (pure Rust; memchr picks SIMD paths at run time) |
| **Thread safety** | not documented; the Indexer owns its reader and is used from one thread |
| **Drop-in for the baseline** | partial — writes a samtools-compatible .fai for well-formed uncompressed FASTA, but it is a library call, not the samtools faidx CLI, and does not handle bgzipped input or .gzi files |

## Gotchas

- Output parity with samtools was never checked for noodles: the z-fasta report's byte comparison of .fai files covers only z-fasta, and its messy-FASTA table records exit codes, not output.
- Semantics differ at the edges: HTSlib counts only isgraph characters as bases, warns and keeps the first of duplicate sequence names, and skips whitespace after '&gt;'; noodles counts every byte of a line except a trailing CR and has no duplicate-name check in the indexer code read.
- The small-file ratios are mostly process start-up (1 MiB: 3.7 ms against 17.5 ms); the asymptotic gap is about 7x per MiB.
- noodles' API is versioned 0.x and changes often (fasta 0.66.0 was measured, 0.67.0 is current), so pin versions.

## Known shortcomings

- Downgraded from A to B: the z-fasta REPORT numbers (1.364 s vs samtools 8.161 s on GRCh38, about 6.0x) state the CPU (Ryzen 9 3950X) but no rustc or C compiler version, and samtools was built at HTSlib's default -O2. The win comes from a memchr line scan against byte-at-a-time bgzf_getc, not the language, and noodles' .fai output was never checked against samtools'. Peak RSS is 3.59 vs 9.31 MiB, not equal.
- Enricher: harness symmetric and no correctness bug found, but noodles' .fai is never byte-checked against samtools', and edge semantics differ (HTSlib counts only isgraph bases and drops duplicate names; noodles counts all bytes except a trailing CR and has no duplicate check). Small-file ratios are mostly samtools start-up (about 15 ms vs 3.5 ms). No bgzip FASTA indexing; issue #146 showed bgzip region queries far slower than samtools.

## Caveats and trade-offs

The evidence lives in a competitor's repo: eneskemalergin/z-fasta is a Zig FASTA tool whose benchmark ranks itself first (0.3824 s on the genome, 3.6x faster than noodles); the noodles row is incidental but independent of both noodles and samtools. The noodles lane is a 373-line wrapper CLI whose index subcommand just calls noodles_fasta::fs::index and fai::fs::write; both lanes are timed as 'rm -f &lt;fasta&gt;.fai; &lt;tool&gt; index &lt;fasta&gt;' in bench/index/run.sh, so the comparison is symmetric. samtools is HTSlib's default -O2 build, not -O3 (same_opt_level false), though this is the shipping upstream configuration and not a crippled build. The speedup is an implementation difference, not a language effect: HTSlib 1.24 faidx.c fai_build_core walks the file one byte at a time through an inlined bgzf_getc with a per-character state machine, while noodles-fasta's io::Indexer scans BufReader chunks with memchr for line feeds and counts bases per line. Output byte-equality of the noodles .fai against samtools is not checked in the report (FAI parity covers z-fasta only; Table 2 records exit codes, not output validation). Single machine, 5 samples after warmups, warm cache only. Peak RSS is lower for noodles (3.59 MiB vs 9.31 MiB on the genome, 46.65 vs 65.49 MiB on the transcriptome); the earlier caveat calling it equal was wrong. On the smallest synthetic file (1 MiB) noodles takes 0.0037 s vs 0.0175 s for samtools, so the lead holds across sizes.

Rust library family (FASTA, FASTQ, SAM/BAM/CRAM, VCF/BCF and more), not a drop-in samtools CLI; the .fai scanner is strict about uniform line widths (the z-fasta report shows noodles and samtools both exit non-zero on ragged, mixed-width or mixed CRLF FASTA).

## Maintenance

Actively maintained (last commit 2026-10-08), MIT-licensed and widely used (727 stars, about 485k noodles-fasta downloads), but still a 0.x API that its author calls experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now B.
- **Tier reason:** Independent third-party measurement: the z-fasta author benchmarked noodles and samtools with a public harness (bench/index/run.sh, tools/install.sh, tools/noodles_wrapper/src/main.rs), and the README names the CPU (Ryzen 9 3950X) for the same 2026-10-10 v0.3.5 run with identical numbers. It falls short of A because neither the rustc nor the C compiler version is stated anywhere, and the flags are only implied by build defaults (Rust release profile, HTSlib/samtools Makefile -O2).
- **Verifier notes:** Numbers match REPORT.md Tables 3-4 and the README; the harness, install script and wrapper are public and the timed commands are symmetric. Downgraded A to B because no compiler versions are stated and samtools is the default -O2 build; the win is memchr-based line scanning against HTSlib's byte-at-a-time loop, and noodles' .fai output was not checked against samtools. HTSlib (samtools' library) is already listed in wave 8.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-116 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/eneskemalergin/z-fasta/blob/main/bench/index/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/index/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/tools/install.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/tools/noodles_wrapper/Cargo.toml>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/tools/noodles_wrapper/src/main.rs>
  - <https://github.com/eneskemalergin/z-fasta/tree/main/bench/index>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/index/run.sh>
  - <https://raw.githubusercontent.com/samtools/htslib/1.24/Makefile>
  - <https://raw.githubusercontent.com/samtools/samtools/1.24/Makefile>
  - <https://raw.githubusercontent.com/samtools/htslib/1.24/faidx.c>
  - <https://raw.githubusercontent.com/zaeleus/noodles/master/noodles-fasta/src/fs/index.rs>
  - <https://raw.githubusercontent.com/zaeleus/noodles/master/noodles-fasta/src/io/indexer.rs>
  - <https://github.com/zaeleus/noodles>
  - <https://github.com/zaeleus/noodles/commits>
  - <https://crates.io/api/v1/crates/noodles-fasta>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/index/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/index/run.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/tools/noodles_wrapper/src/main.rs>
  - <https://raw.githubusercontent.com/zaeleus/noodles/master/README.md>
  - <https://raw.githubusercontent.com/zaeleus/noodles/master/Cargo.toml>
  - <https://raw.githubusercontent.com/zaeleus/noodles/master/noodles-fasta/Cargo.toml>
  - <https://raw.githubusercontent.com/zaeleus/noodles/master/noodles-fasta/src/fs/index.rs>
  - <https://raw.githubusercontent.com/zaeleus/noodles/master/noodles-fasta/src/io/indexer.rs>
  - <https://raw.githubusercontent.com/samtools/htslib/1.24/faidx.c>
  - <https://github.com/zaeleus/noodles/issues?q=is%3Aissue+fasta+index>
  - <https://github.com/zaeleus/noodles/issues/146>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/zaeleus/noodles`) · [data/wave14/enrich/raw/github_com_zaeleus_noodles.json](../../../data/wave14/enrich/raw/github_com_zaeleus_noodles.json) (enrichment confidence 0.75)

</details>
