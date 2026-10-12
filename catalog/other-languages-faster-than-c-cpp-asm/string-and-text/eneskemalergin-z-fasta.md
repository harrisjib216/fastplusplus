# z-fasta (Zig FASTA index, extract and stats tool)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig CLI that indexes and extracts uncompressed FASTA; builds samtools-compatible .fai indexes 6-21x faster than samtools faidx.

| | |
|---|---|
| **Beats** | samtools faidx 1.24 with HTSlib 1.24 (C); also measured: fastahack, SeqKit (Go), noodles and rust-bio (Rust), pyfaidx (Python). |
| **Claimed result** | README (v0.3.5, measured 2026-10-10) and bench/index/REPORT.md Table 5, .fai index build, z-fasta `index --emit-fai` vs samtools faidx: human genome 0.3824 s vs 8.1614 s (21.3x), transcriptome 0.1546 s vs 1.7112 s (11.1x), proteome 0.0113 s vs 0.0650 s (5.8x); fastahack (C++) 20.8901 s on the genome (54.6x, REPORT.md only). One 1 kbp positional GET through an existing index: human genome 2.3 ms vs 8.2 ms, transcriptome 8.2 ms (.zfi) or 28.3 ms (.fai) vs 301.8 ms, proteome 2.7 ms (.zfi) vs 17.9 ms. Stats is compared with noodles and SeqKit only, not samtools. |
| **Workload** | Build a samtools-compatible .fai index (`z-fasta index --emit-fai`) of uncompressed FASTA (human genome \~2.9 GiB, transcriptome \~459 MiB, proteome \~13 MiB), and fetch one 1 kbp region through an existing index; warm cache. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X (README Performance section); Linux x86_64 (glibc 2.43 target in the report provenance); zebrac 0.6.2, 5 measured samples after 3 warmups, 5000 ms budget per command, warm cache. |
| **Compiler and flags** | z-fasta 0.3.5 built with Zig 0.16.0, `zig build -Doptimize=ReleaseFast -Dstrip=true`; build.zig uses standardTargetOptions and no -Dtarget/-Dcpu is passed, so the binary targets the host (native) CPU. samtools 1.24 and HTSlib 1.24 built from source by tools/install.sh with plain `./configure` and `make`, i.e. package-default flags (htslib Makefile `-g -Wall -O2 -fvisibility=hidden`, samtools Makefile `-g -Wall -O2`) for generic x86-64; C compiler not named. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 9 stars, 0 forks (GitHub repo page, 2026-10-11); new project (v0.3.5, 244 commits). |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/eneskemalergin/z-fasta) · [benchmark](https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/README.md) |

## Verdict

On an AMD Ryzen 9 3950X (Linux, warm page cache, zebrac 0.6.2 with 5 samples after 3 warmups), z-fasta 0.3.5 (Zig 0.16.0 ReleaseFast, host CPU) built the `.fai` for the GRCh38 primary assembly in 0.382 s vs 8.161 s for samtools faidx 1.24 with HTSlib 1.24 (default -O2 build), 21.3x, plus 11.1x on GENCODE v46 transcripts and 5.8x on the UniProt human proteome, both tools single-threaded. One 1 kbp GET took 2.3 vs 8.2 ms on the genome and 8.2 vs 301.8 ms on the transcriptome, timings dominated by process startup and index loading.

## Use it when

- Pipelines that build or rebuild `.fai` indexes of large uncompressed references: human GRCh38 in 0.38 s vs 8.16 s for samtools faidx (warm cache), with byte-identical `.fai` output on the 20 samtools parity cases.
- One-shot command-line extraction from FASTA files with many records (transcriptomes, proteomes), where samtools spends most of its time loading the `.fai`: one 1 kbp region from GENCODE transcripts in 8.2 ms with `.zfi` vs 301.8 ms.
- BED batch extraction: 10,000 1 kbp rows from the transcriptome in 37 ms vs 377 ms for samtools and 771 ms for bedtools getfasta.
- Messy FASTA exports (mixed line widths, trailing whitespace, mixed CRLF/LF, blank lines) that samtools faidx refuses; the `.zfi` side tables index them.
- Memory-constrained hosts: indexing stayed near 3.6 MiB peak RSS from 1 MiB to 2.9 GiB inputs.

## Skip it when

- bgzip- or gzip-compressed FASTA, or FASTQ: not supported, so samtools faidx with BGZF remains the tool there.
- Inside a C, C++ or Zig program: there is no library API yet, and HTSlib's fai_load plus faidx_fetch_seq pays the index load once per process, which the per-invocation GET benchmark does not measure.
- Native Windows: no release; the author points Windows users to the Linux build under WSL.
- Cold-cache or disk-bound indexing: every published number is warm page cache (7.9 GiB/s on the genome); cold runs were not measured.
- Workflows that need many positional regions in one call (capped at 1,024 per invocation; use a BED or names file instead) or that cannot tolerate a young single-maintainer tool (9 stars, 0.3.x releases since July 2026).

## How it is fast

The indexer is single-threaded and streams 256 KiB read() buffers; once a record's first line fixes the line width, it accepts blocks of up to 256 lines at a time by checking the separator bytes at the expected stride and counting bytes at or below ASCII space with portable Zig @Vector code, and drops back to a general line state machine at the first anomaly. HTSlib's fai_build_core, behind samtools faidx, walks the file one character at a time through bgzf_getc, so the gap is per-byte work, not threads or compiler flags. For GET, the binary `.zfi` loads in milliseconds, while samtools takes about 0.3 s per call on GENCODE transcripts whatever the region count, consistent with parsing its text `.fai`, and names are scanned and de-duplicated with 16-byte vector compares and a hash set.

## Compared with alternatives

needletail is the catalogued sibling for streaming FASTA/FASTQ parsing (including gzip) and beats kseq.h; pick z-fasta instead when you need an index and random access to regions of uncompressed FASTA, or a `.fai` built quickly. The other string-and-text siblings (csv-zero, Sassy, A\*PA2) solve different problems.

## Integration

| | |
|---|---|
| **Form** | CLI executable (static binary, about 800 KiB); no library API |
| **Dependencies** | none at runtime; building from source needs only Zig |
| **Minimum toolchain** | Zig 0.16.0 (build.zig.zon minimum_zig_version); build.zig rejects ReleaseSmall, use -Doptimize=ReleaseFast |
| **Platforms** | Linux and macOS, x86_64 and arm64 release archives; Windows only through WSL |
| **Thread safety** | not applicable (CLI); the indexer is single-threaded |
| **Drop-in for the baseline** | partial — `z-fasta index --emit-fai ref.fa > ref.fa.fai` produces the same `.fai` bytes as samtools faidx for samtools-representable FASTA and `get` covers region and BED extraction, but the commands and flags differ, `.fai` goes to stdout only, and BGZF or gzip input is refused |

## Gotchas

- Version 0.3.4 indexed records with a space or tab inside a later sequence line as fixed-width, giving wrong lengths in both `.zfi` and `.fai` and returning the whitespace bytes from GET; 0.3.5 fixed it, the stale-index check (sidecar mtime plus source size and mtime, not a content hash) does not detect such sidecars, so re-index those files. The fix made indexing 10-40% slower on 15 of 30 cases (open issue #34); the README numbers are from 0.3.5, after the fix.
- Harness: the `--emit-fai` lane writes the `.fai` rows to a spool file in TMPDIR and then to /dev/null while samtools writes a sidecar next to the FASTA (a small difference); samtools 1.24 is a default `./configure && make` build (-O2, shared HTSlib, C compiler unnamed) against a z-fasta built for the host CPU; both sides are single-threaded and warm-cache. No correctness defect found behind the 0.3.5 index numbers: the SIMD fast path still checks every byte for whitespace.
- The genome GET gap is a near-constant 5-6 ms from 1 to 100 regions (2.3-2.7 ms vs 7.9-8.6 ms for samtools), and samtools stays near 0.30 s on the transcriptome from 1 to 1,000 regions, consistent with loading its text `.fai`; the GET ratios therefore measure process startup and index loading, not extraction speed.
- Index and GET treat every byte above ASCII space as a sequence symbol (alphabet checks happen only in `validate`), duplicate names keep the first occurrence by default, and the `rust-bio` peer lane is a custom FAI writer, not a rust-bio command. The stats report's only C program is seqtk comp (15.50 s vs 2.84 s on the genome), which it labels a partial reference whose output is not the same report.

## Known shortcomings

- Index-build 21.3x over samtools faidx is algorithmic (SIMD block validation vs HTSlib's per-character bgzf_getc loop, both single-thread), first-party; samtools at package-default -O2 generic x86-64 while z-fasta is built for the native CPU; C compiler unnamed; the emit-fai lane discards output while samtools writes its sidecar file; warm cache only. Tier A rests on samtools flags taken from public Makefiles.
- No defect behind the 0.3.5 index numbers (the SIMD path checks every byte); 0.3.4 had a whitespace wrong-length bug fixed in 0.3.5, and the README numbers are post-fix (issue #34: 10-40% slower). The GET ratios are mostly process start-up plus index load (genome gap a constant 5-6 ms; samtools about 0.30 s on the transcriptome at any N). emit-fai writes a spool file then /dev/null (minor). CLI only, no library API (#35).

## Caveats and trade-offs

First-party benchmark with the author's own runner and reports. Both sides are single-threaded (no threads in src/indexer.zig; HTSlib's fai_build_core is a per-character bgzf_getc loop), so the gap is algorithmic: z-fasta validates fixed-width line blocks with SIMD whitespace counts over 256 KiB reads. The cross-tool `--emit-fai` lane constructs the .fai bytes but discards the emitted stream while samtools writes a .fai sidecar file, so output destinations differ (REPORT.md says so). z-fasta is built for the native CPU while samtools uses its package-default -O2 generic build; the C compiler is unnamed. The 7.9 GiB/s genome throughput is a warm page-cache figure. The rust-bio lane is a custom FAI writer, not a rust-bio command. v0.3.5 indexing is 10-40% slower than v0.3.4 on 15 of 30 cases (genome .fai 382.4 ms vs 321.2 ms) after whitespace validation was added. FAI parity with samtools passed 20/20 structural edge cases. [retier] The GET ratios are mostly process start-up plus index load (genome gap a constant 5-6 ms; samtools about 0.30 s on the transcriptome at any N). 0.3.4 had a whitespace wrong-length bug fixed in 0.3.5; the README numbers are post-fix (issue #34: 10-40% slower). emit-fai writes a spool file then /dev/null. CLI only, no library API (#35).

Uncompressed FASTA only; own .zfi index plus samtools-compatible .fai for representable FASTA; one static executable (about 800 KiB) with no runtime dependencies; scope limited to index, get, validate and stats.

## Maintenance

Active single-maintainer project (244 commits, releases v0.3.0 to v0.3.5 from July to 2026-10-10, 9 stars, 13 open issues) under MIT with prebuilt Linux and macOS binaries; usable as a CLI today, but it has no library API, and 0.3.5 carries an open indexing slowdown (#34) left by the whitespace correctness fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code (bench/index/run.sh with the zebrac runner, bench/get, and tools/install.sh, which builds samtools/HTSlib 1.24 from pinned source archives), z-fasta compiler and flags stated (Zig 0.16.0, ReleaseFast, -Dstrip=true, recorded revision 1c114b6), CPU stated (AMD Ryzen 9 3950X), and the samtools flags are the package defaults readable in the public Makefiles (-g -Wall -O2); only the C compiler version is unnamed. All README and REPORT numbers match the record.
- **Verifier notes:** Numbers verified on README and bench/index/REPORT.md (Table 3 and Table 5). Shortcomings to record: first-party; samtools at package-default -O2 generic x86-64 versus z-fasta built for the native CPU, C compiler unnamed; emit-fai lane discards output while peers write files; warm cache only. Not a language-level claim.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/index/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/get/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/stats/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/tools/install.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/build.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/src/indexer.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/src/platform.zig>
  - <https://github.com/eneskemalergin/z-fasta>
  - <https://github.com/eneskemalergin/z-fasta/commits>
  - <https://github.com/eneskemalergin/z-fasta/tree/main/src>
  - <https://raw.githubusercontent.com/samtools/htslib/1.24/Makefile>
  - <https://raw.githubusercontent.com/samtools/samtools/1.24/Makefile>
  - <https://raw.githubusercontent.com/samtools/htslib/1.24/faidx.c>
- **Sources the enricher read:**
  - <https://github.com/eneskemalergin/z-fasta>
  - <https://github.com/eneskemalergin/z-fasta/releases>
  - <https://github.com/eneskemalergin/z-fasta/issues?q=is%3Aissue>
  - <https://github.com/eneskemalergin/z-fasta/issues/34>
  - <https://github.com/eneskemalergin/z-fasta/issues/35>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/index/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/index/run.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/get/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/bench/stats/REPORT.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/tools/install.sh>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/build.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/src/indexer.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/src/platform.zig>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/wiki/Limits-and-Supported-Formats.md>
  - <https://raw.githubusercontent.com/eneskemalergin/z-fasta/HEAD/wiki/Index-Formats.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/eneskemalergin/z-fasta`) · [data/wave14/enrich/raw/github_com_eneskemalergin_z_fasta.json](../../../data/wave14/enrich/raw/github_com_eneskemalergin_z_fasta.json) (enrichment confidence 0.8)

</details>
