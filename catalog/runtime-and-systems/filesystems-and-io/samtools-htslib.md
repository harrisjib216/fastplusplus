# htslib

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT AND BSD-3-Clause` · 🟢 active

> C library for SAM/BAM/CRAM/VCF/BCF I/O; 5x faster BAM read-write and 13x faster BAM-to-SAM than Samtools 0.1.19 at 16 threads.

| | |
|---|---|
| **Beats** | Samtools 0.1.19 (the original libbam-based implementation HTSlib grew out of) |
| **Claimed result** | BAM read-write loop running 5 times faster and BAM to SAM conversion 13 times faster (both using 16 threads, compared to Samtools 0.1.19). |
| **Workload** | BAM read-write loop and BAM to SAM conversion using 16 threads, HTSlib-based samtools against Samtools 0.1.19, as reported in the HTSlib paper abstract (GigaScience 2021). |
| **Metric** | throughput |
| **Adoption** | 953 stars; core library of samtools and bcftools; downloaded more than 1 million times from GitHub and conda and used directly by an estimated 900 GitHub projects (paper abstract) |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/samtools/htslib) · [benchmark](https://github.com/samtools/htslib) |

## Verdict

The peer-reviewed GigaScience 2021 paper (abstract reproduced in the README) reports HTSlib-based tools running a BAM read-write loop 5x faster and BAM-to-SAM 13x faster than Samtools 0.1.19, both at 16 threads, with no hardware or compiler visible from here. A separate first-party page in samtools/www.htslib.org (Sep 2019, Intel Core i5-4570 named in the page source, compiler not stated, data file not public) shows libdeflate inside HTSlib reading a BAM in 43 s versus 77 s with zlib 1.2.11 (1.79x) and rewriting BAM at level 6 with 4 threads in 1m20s versus 3m12s (2.4x), both derived from page data.

## Use it when

- Any C or C++ program that reads or writes BAM, CRAM, SAM, VCF or BCF: it is the reference implementation, and bindings exist for Python (pysam), Perl, R and Rust.
- Throughput-bound BAM/CRAM pipelines on multi-core machines: give the file a shared thread pool so BGZF or CRAM slice (de)compression scales with cores.
- Random access by genomic region through BAI/CSI/TBI/CRAI indexes, including remote files over HTTPS, S3 and GCS when built with libcurl.
- Writing compact archives: CRAM 3.1 (the default since 1.22) stores the project's 10M-read NovaSeq set in 176 MB versus 515 MB of default BAM, encoding in 5.4 s versus 9.2 s wall at 8 threads, though decoding takes 1.9 s versus 0.8 s (Apr 2025 benchmark page, Skylake Xeon).

## Skip it when

- Parsing untrusted CRAM or BCF with an old release: 1.23.1 (Mar 2026) fixed ten CRAM-decoder CVEs (CVE-2026-31962 to 31971) and 1.24 (Jul 2026) removed CRAM v4 and tightened BCF checks after further advisories; pin 1.24 or later.
- Single-threaded BAM writing at default or high levels with plain zlib: BAM level 9 encode costs 1661 CPU-seconds versus 61.7 at the default on the NovaSeq set, and without libdeflate compression is roughly 2x slower.
- Seeking in multi-threaded SAM text input: NEWS says the threaded SAM reader does not support seeks and drops back to single-threaded mode for iterator range requests.
- Generic file I/O or archive handling: it only speaks genomics formats and BGZF; the filesystems-and-io siblings (liburing, libarchive) are the tools for anything else.

## How it is fast

BAM and bgzipped VCF/SAM are sequences of independently DEFLATE-compressed blocks of at most 64 KB (BGZF), so HTSlib farms block (de)compression out to a shared thread pool (hts_tpool) whose ordered process queues keep output in sequence; SAM text parsing/formatting, CRAM slice encode/decode and index building also run in the pool. Builds probe for libdeflate, which the project's own Sep 2019 benchmark shows reading a BAM 1.79x faster than zlib 1.2.11 on one core. CRAM 3.1 uses the htscodecs codecs (rANS Nx16 with SSE4.1/AVX2/AVX-512 variants chosen at configure time, fqzcomp qualities, a read-name tokeniser), and NEWS lists many targeted speedups (nibble2base SIMD on x86 and ARM, kputll, SAM header parsing).

## Compared with alternatives

None of the filesystems-and-io siblings handles sequencing formats: pick HTSlib for BAM/CRAM/VCF/BCF and BGZF, and reach for liburing or SPDK only when the bottleneck is raw block I/O beneath it; libarchive covers generic archives, not BGZF random access by index.

## Integration

| | |
|---|---|
| **Form** | static lib (libhts.a) and shared lib, built with autoconf/configure and GNU make; also bundled inside pysam and other bindings |
| **Dependencies** | zlib (required); libbz2 and liblzma required by default (--disable-bz2/--disable-lzma, at the cost of reading some CRAM files); optional libdeflate (probed and used if found), libcurl (HTTPS/S3/GCS), libcrypto (S3 on non-macOS); htscodecs as a git submodule or external library |
| **Minimum toolchain** | C compiler such as gcc or clang (README: compatible with gcc, g++ and clang); GNU make; autoconf, autoheader and autoreconf when building from git |
| **Platforms** | Linux, macOS and Windows via MinGW64/MSYS2 (CI on all three); x86 SIMD rANS paths need SSE4.1, AVX2 or AVX-512 detected at configure time, with scalar fallbacks |
| **Thread safety** | Internal worker threads via hts_set_threads (per-file) or the recommended shared hts_tpool (hts_set_thread_pool); sharing one htsFile between caller threads is not documented in the headers read, so use one handle per thread |
| **Drop-in for the baseline** | partial — samtools commands keep their names and file formats, but the C API differs from Samtools 0.1.19's libbam, so programs linking the old library need porting |

## Gotchas

- The headline 5x/13x compares 16-thread HTSlib with Samtools 0.1.19, which (per a snippet of the 'Twelve years of SAMtools and BCFtools' paper) only threaded sorting and BAM writing, so the BAM-to-SAM gain is largely multi-threaded decoding; per-core speedup, hardware, compiler and dataset are not visible (the paper full text was unreachable; a bioRxiv snippet says chromosome 1 of one ENA run with HTSlib 1.10.2-32-ga22a0af, HTSJDK 2.22.0, Sambamba 0.7.1 and Scramble 1.14.13).
- Performance depends on build options: libdeflate is used only if found at configure time, and with it BGZF levels 1-9 are remapped onto libdeflate's 1-12 scale, so file sizes differ from zlib builds (Sep 2019 page: level 6 BAM 6.53 GB with libdeflate vs 6.50 GB with zlib).
- Pipe-fed bgzip lost about 26% throughput in 1.17-1.19 (issue #1767: 351 to 260 MiB/s at -@ 128 on a 64-core EPYC) because pipes reported a 4 KB preferred block size; PR #1768 raised the input block size. Issue #1869 (open) asks for a way to disable the periodic hflush during multi-threaded writes.
- README says HTSlib depends only on zlib, but INSTALL makes libbz2 and liblzma required unless disabled, and git checkouts need the htscodecs submodule; setting a thread pool on an htsFile twice is rejected since 1.23.1.

## Known shortcomings

- Claim (5x BAM read-write loop, 13x BAM to SAM, 16 threads vs Samtools 0.1.19) is the GigaScience 2021 abstract cited in the README; full text unreachable (doi, OUP, PMC, bioRxiv blocked). Baseline is its own predecessor and the gain is partly threading. No wave-8 category fits a genomics file-format library; filed under filesystems-and-io.
- Enricher: the 5x and 13x figures are 16 threads against Samtools 0.1.19, which only threaded sort and BAM writing, so the 13x BAM-to-SAM is mostly threaded decode and the per-core gain is unknown (paper full text still unreachable; bioRxiv snippet: chr1 of one ENA run, HTSlib 1.10.2-32-ga22a0af). The htslib.org benchmark pages are reachable through raw.githubusercontent.com/samtools/www.htslib.org (benchmarks/zlib.md: Sep 2019, i5-4570, compiler unstated, data file private, libdeflate read 43 s vs zlib 1.2.11 77 s, 1.79x derived; BAM rewrite level 6 at 4 threads 1m20s vs 3m12s, 2.4x derived; benchmarks/CRAM.md: Apr 2025, Skylake Xeon, -@8). 2026 CVEs in the CRAM decoder (CVE-2026-31962 to 31971, fixed in 1.23.1); 1.24 dropped CRAM v4; bgzip pipe regression 351 to 260 MiB/s in 1.17-1.19 (#1767, fixed by #1768); the threaded SAM reader cannot seek.
- Domain set to runtime-and-systems to match its filesystems-and-io category.

## Caveats and trade-offs

The peer-reviewed paper (Bonfield et al., GigaScience 2021, giab007) is the source; its full text, hardware, compiler and per-tool tables (HTSlib versus HTSJDK 2.22.0, Sambamba 0.7.1 and Scramble 1.14.13 at HTSlib 1.10.2) were not reachable (PMC, bioRxiv, OUP and eprints.gla.ac.uk all ENOTFOUND), so only the abstract, which appears in the repo README as a BibTeX entry, is quoted. The baseline is HTSlib's own predecessor, not an independent competitor, and the 16-thread setting means part of the gain is better use of threading rather than per-core speed. Project NEWS also says libdeflate makes compression 'twice as fast and decompression faster' than zlib, with 'results vary by CPU' and no method. The CRAM benchmark page at htslib.org/benchmarks/CRAM.html was not reachable. The lead's guessed category big-integer-arbitrary-precision is wrong; genomics-file-formats is not one of wave 8's seven categories, so it may need re-filing. [retier] 5x and 13x at 16 threads vs Samtools 0.1.19 (which only threaded sort and BAM writing); per-core gain unknown; benchmarks/zlib.md (Sep 2019, i5-4570, compiler unstated, private data file): libdeflate read 43 s vs zlib 77 s (1.79x derived), BAM rewrite at 4 threads 2.4x derived; benchmarks/CRAM.md (Apr 2025, Skylake Xeon, -@8) has full tables; CRAM decoder CVEs fixed in 1.23.1; threaded SAM reader cannot seek.

C library for SAM, BAM, CRAM, VCF and BCF with BGZF thread pools, CSI/BAI/TBI indexes, optional libdeflate, libcurl, bzip2 and xz; depends only on zlib in the minimal build; MIT/Expat outside cram/, 3-clause BSD inside cram/; wrapped from Perl, Python, Rust and R.

## Maintenance

Very active (release 1.24 on 9 Jul 2026, commits through 8 Oct 2026, OSS-Fuzz harness added), MIT/Expat outside cram/ and 3-clause BSD inside it; the de facto standard library for these formats, with a steady stream of 2026 security fixes for malformed CRAM, BCF and index input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The claim (BAM read-write loop 5x faster, BAM to SAM 13x faster, both at 16 threads vs Samtools 0.1.19) is the abstract of the peer-reviewed GigaScience 2021 paper (giab007), reproduced verbatim in the repo README's BibTeX entry; the paper is first-party but peer-reviewed, so B. Full text, hardware, compiler and tables were unreachable, so it cannot be A.
- **Verifier notes:** Abstract numbers verified in the README; the paper full text (doi.org, OUP, PMC, bioRxiv, eprints.gla.ac.uk) was unreachable from this environment (ENOTFOUND/blocked), so per-tool comparisons against HTSJDK, Sambamba and Scramble mentioned in the record could not be checked. Shortcomings: baseline is HTSlib's own predecessor (Samtools 0.1.19), not an independent competitor; the 16-thread setting means much of the gain is threading; no hardware or compiler visible. Category 'genomics-file-formats' is not one of wave 8's seven categories (nearest existing ones: wave 11 filesystems-and-io or wave 4 binary-schemas); the orchestrator should re-file it with a category override. Metadata checked: MIT/Expat outside cram/ and Modified 3-Clause BSD inside cram/ (LICENSE), 953 stars, default branch develop, last commit 2026-10-08, active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-174 (wave 8); enricher w8 pair-038; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://github.com/samtools/htslib>
  - <https://github.com/samtools/htslib/blob/develop/README.md>
  - <https://github.com/samtools/htslib/blob/develop/LICENSE>
  - <https://github.com/samtools/htslib/commits/develop>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/samtools/htslib/develop/README.md>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/NEWS>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/INSTALL>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/LICENSE>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/configure.ac>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/htslib/hts.h>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/htslib/bgzf.h>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/htslib/thread_pool.h>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/htslib/sam.h>
  - <https://github.com/samtools/htslib/commits/develop>
  - <https://github.com/samtools/htslib/issues?q=is%3Aissue%20slow%20OR%20performance>
  - <https://github.com/samtools/htslib/issues/1767>
  - <https://github.com/samtools/htslib/issues/1780>
  - <https://github.com/orgs/samtools/repositories>
  - <https://raw.githubusercontent.com/samtools/www.htslib.org/master/benchmarks/zlib.md>
  - <https://raw.githubusercontent.com/samtools/www.htslib.org/master/benchmarks/CRAM.md>
  - https://www.htslib.org/benchmarks/zlib.html (ENOTFOUND)
  - https://eprints.gla.ac.uk/254019/1/254019.pdf (ENOTFOUND)
  - https://www.ebi.ac.uk/europepmc/webservices/rest/search (ENOTFOUND)
  - WebSearch snippets: bioRxiv 10.1101/2020.12.16.423064 and 'Twelve years of SAMtools and BCFtools' (not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/samtools/htslib`) · [data/wave8/enrich/raw/github_com_samtools_htslib.json](../../../data/wave8/enrich/raw/github_com_samtools_htslib.json) (enrichment confidence 0.75)

</details>
