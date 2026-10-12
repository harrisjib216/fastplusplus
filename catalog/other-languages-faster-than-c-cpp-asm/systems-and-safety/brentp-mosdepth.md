# mosdepth (Nim BAM/CRAM depth calculator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim` · `MIT` · 🟢 active

> Nim command-line tool for BAM/CRAM coverage; about 2x faster per-base than the pre-2021 pileup-based samtools depth.

| | |
|---|---|
| **Beats** | samtools depth (C, htslib); README table also lists bedtools genomecov (C++) and sambamba depth (D) |
| **Claimed result** | Per-base depth about 2x as fast as samtools depth (BAM: mosdepth 25:23 vs samtools 50:12, relative 1.98; CRAM samtools 1.79x slower); sambamba 5.71x and bedtools 5.31x slower; window depth genome-wide in under 9 minutes of user time with 3 threads (8:44, relative 0.34); exome in 1 minute 38 seconds on one CPU. |
| **Workload** | Per-base depth on a 30X whole-genome BAM/CRAM with one thread, 500-base window mean depth with three threads, and an exome BAM against 1,195,764 exons. |
| **Metric** | throughput |
| **Compiler and flags** | Nim with --mm:refc (nim.cfg) and -d:release; nim.cfg comment: nim c -a -d:static -d:release mosdepth.nim with htslib configured --with-libdeflate --disable-libcurl. Nim's release build passes -O3 -fno-ident -fno-math-errno to gcc (nim-lang/Nim config/nim.cfg gcc.options.speed). samtools' default Makefile uses CFLAGS -g -Wall -O2; the flags of the samtools, bedtools and sambamba builds actually timed are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: depth is kept in an array that is incremented at each read start and decremented at its end, summed cumulatively at output; no extra allocations or objects, whereas samtools depth goes through the pileup machinery. |
| **Adoption** | 878 stars; Bioinformatics 2018 paper (doi 10.1093/bioinformatics/btx699) |
| **Last commit** | 2026-05-02 |
| **Links** | [repository](https://github.com/brentp/mosdepth) · [benchmark](https://raw.githubusercontent.com/brentp/mosdepth/HEAD/README.md) |

## Verdict

On one unstated machine with a 30X human WGS BAM, single-threaded per-base depth took 25:23 for mosdepth vs 50:12 for samtools depth (1.98x) and 2:24:53 for sambamba and 2:14:44 for bedtools genomecov; CRAM samtools was 1.79x slower. These were 2017-era tool versions (samtools depth still pileup-based) with unknown build flags. The Bioinformatics 2018 paper repeats the same table (search snippet only).

## Use it when

- Whole-genome or exome QC where you need per-window or per-BED-region mean or median depth, thresholds (e.g. bases at 1X/10X/20X/30X per exon) or genome-wide coverage distributions from a single pass.
- CNV-style binned depth on WGS (`-n --fast-mode --by 500`), where the README reports under 9 minutes of user time with 3 threads on a 30X genome.
- Callable-loci style quantized output (`--quantize 0:1:5:150:`) as a lighter replacement for GATK CallableLoci.
- Pipelines that already pull mosdepth from bioconda, brew or the static release binary (nf-core/Sarek calls it), so no Nim toolchain is needed.

## Skip it when

- Small one-off regional queries: the README says it is slower than samtools there, because it builds the whole-chromosome array first.
- Memory-constrained jobs: about 4 bytes times the longest chromosome (about 1.2 GB on human, against 27 MB for samtools depth in the README table).
- When you just need samtools-compatible per-position output and already run samtools 1.13 or later: its rewritten, non-pileup `depth` (3-30x faster than 1.11 in the samtools PR) has never been benchmarked against mosdepth by the project.
- RNA-seq with --fast-mode: fast mode counts from alignment start to end, so deletions and spliced introns (N) are counted as covered; use the default mode there (an independent Megadepth paper, search snippet only, reports mosdepth 2.7x slower than Megadepth on RNA-seq BAMs).
- Unindexed or unsorted input, or CRAM without a reference (-f or REF_PATH): it exits with an error.

## How it is fast

For each chromosome it allocates one int32 array of chromosome length, adds +1 at every aligned-block start and -1 at every block end, then takes a cumulative sum (a difference array, like BEDTools genomecov), so no per-base pileup objects are built. Regions, windows, thresholds and distributions are read off the finished array in one pass. In --fast-mode it uses only alignment start and end, skips mate-overlap correction and asks htslib to decode only the needed CRAM fields (CRAM_OPT_REQUIRED_FIELDS), which the changelog says made CRAM up to 2x faster.

## Compared with alternatives

Pick mosdepth over sambamba (the D sibling, which wins on view, flagstat and markdup) for depth: its own README table has sambamba depth 5.71x slower on the same 30X BAM. Other genomics siblings (mako for sorting, rasusa for subsampling, skani for ANI) solve different problems and pair with it rather than compete.

## Integration

| | |
|---|---|
| **Form** | CLI binary (static release binary, bioconda, brew, quay.io container) or built from source with nimble |
| **Dependencies** | htslib &gt;= 1.4 (the static release binary bundles htslib and libdeflate), hts-nim &gt;= 0.3.31, docopt 0.7.1, d4-nim plus the Rust libd4binding for optional --d4 output |
| **Minimum toolchain** | Nim &gt;= 1.0.0 per mosdepth.nimble; CI builds with Nim 1.6.18 and 2.0.2; must be compiled with --mm:refc (set in nim.cfg) and -d:release |
| **Platforms** | Linux x86-64 (static release binary, CI on ubuntu-22.04) and macOS (CI on macos-14 with Homebrew htslib); other platforms not documented |
| **Thread safety** | Not applicable (single process); -t sets htslib BGZF/CRAM decompression threads only, with no benefit past about 4 threads per the README. |
| **Drop-in for the baseline** | false: different command line and output (run-length BED.gz with CSI index, summary and distribution files) from samtools depth's per-position TSV. |

## Gotchas

- Stale baseline and harness asymmetry: the 2x claim is against pileup-based samtools depth (2017-era: the same numbers are in the 2018 paper and the scaling plot dates from October 2017, so the table predates --fast-mode, tagged in v0.2.4 on 2018-11-19, and timed the default CIGAR-and-overlap mode). samtools 1.13 (July 2021, PR #1428) rewrote depth without pileup, 3.3x faster than 1.11 on a 30-50x BAM (19.755 s vs 6.049 s) and 33x on deep CRAM, so the README's 'why faster' no longer describes current samtools. The two tools also wrote different outputs (uncompressed per-position text vs run-length bgzipped BED plus index), and no hardware, versions or commands are given.
- The timing table predates correctness fixes that changed depth values: 0.2.2 fixed wrong values on consecutive chromosomes of the same length, 0.2.5 stopped double counting fully overlapping mates, and 0.2.0 fixed distribution output for chromosomes over 2.1 Gb.
- Must be built with --mm:refc: the README warns other memory managers (Nim 2's default ORC) hurt performance and correct operation. Default mode keys mate-overlap correction on read names in a hash table and only for proper pairs on the same chromosome; fast mode does no overlap correction and counts D/N spans as covered.
- Histogram and median caps: the distribution clamps depths above 400,000 to 399,990, and --use-median uses a 65,536-bin counter, so region medians above 65,535 are clamped. Open issue #268 (May 2026): the static v0.3.14 binary reported CRAM 3.1 'Slice decode failure' on a file samtools reads (maintainer could not reproduce).

## Known shortcomings

- README table has no hardware or versions; the paper is confirmed only through a search snippet (OUP, PMC and bioRxiv blocked); the speedup comes from the algorithm rather than Nim, with htslib and libdeflate as possible confounders; overlap correction is on by default.
- Stale baseline: the README 2x is against pileup-based samtools depth (2017; the table predates --fast-mode, v0.2.4 of 2018-11-19). samtools 1.13 (July 2021, PR #1428) rewrote depth without pileup, 3.3x faster than 1.11 on a 30-50x BAM (19.755 s vs 6.049 s) and 33x on deep CRAM, and was never re-compared with mosdepth. Output asymmetry: per-position text vs run-length bgzipped BED plus index. The table predates fixes 0.2.2 (wrong values on same-length chromosomes) and 0.2.5 (full mate-overlap double count). --mm:refc is required; fast mode counts D/N spans as covered (RNA-seq); the median is clamped at 65,535 and the histogram at 400,000; open #268 (CRAM 3.1 static-binary decode failure).

## Caveats and trade-offs

The README table lists no hardware, tool versions or commands; tier B would rest on the Bioinformatics 2018 paper, which was not opened (publisher, PMC and bioRxiv blocked; a search snippet confirms the comparison but gives no numbers). Results date from 2017 samtools and htslib. Both mosdepth and samtools decode BAM/CRAM with htslib (C); mosdepth's documented build links htslib with libdeflate, and the htslib build used by samtools in the table is not stated, so part of the gap may be decompression rather than mosdepth's code. By default mosdepth corrects mate overlaps and walks CIGAR operations; --fast-mode (-x) skips both; the README does not say which mode the timing table used, and its accuracy check compared samtools depth defaults with mosdepth without overlap detection. The speedup is algorithmic (difference array against samtools' pileup), not a Nim-versus-C effect; mosdepth uses far more memory (1196 MB vs 27 MB for samtools). Opt levels are not matched if default builds were used (Nim release -O3, samtools Makefile -O2). [retier] The README table lists no hardware, tool versions or commands; the Bioinformatics 2018 paper was not opened. Stale baseline: the 2x is against pileup-based samtools depth (2017; the table predates --fast-mode, v0.2.4 of 2018-11-19). samtools 1.13 (July 2021, PR #1428) rewrote depth without pileup, 3.3x faster than 1.11 on a 30-50x BAM (19.755 s vs 6.049 s) and 33x on deep CRAM, and was never re-compared with mosdepth. Output asymmetry: per-position text vs run-length bgzipped BED plus index. The table predates fixes 0.2.2 (wrong values on same-length chromosomes) and 0.2.5 (full mate-overlap double count). Both tools decode through htslib; mosdepth's documented build links libdeflate. Fast mode counts D/N spans as covered; the median is clamped at 65,535 and the histogram at 400,000; open #268 (CRAM 3.1 static-binary decode failure).

Memory is about 32 bits times the longest chromosome (about 1 GB for chr1, against 27 MB for samtools); slower than samtools for small one-off regional queries; no gain past about 4 threads; links htslib (C) for decoding.

## Maintenance

Active (last commit 2026-05-02, v0.3.14, 879 stars, MIT), widely used through bioconda; the performance evidence is first-party and dates from 2017, before samtools 1.13's depth rewrite, so treat the 2x figure as historical until someone re-runs it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README table gives first-party run times with no hardware, tool versions, commands or benchmark script; the Bioinformatics 2018 paper is peer-reviewed and a search snippet confirms it compares against samtools depth, BEDTools genomecov and Sambamba, but its numbers could not be opened (OUP, PMC and bioRxiv blocked), and wave-14 rules keep snippet-only paper evidence at C.
- **Verifier notes:** Numbers match the README table exactly (BAM samtools 50:12 vs mosdepth 25:23, relative 1.98; CRAM 1.79; sambamba 5.71; bedtools 5.31; 3-thread window 8:44). Downgraded to C because the only openable evidence is first-party and lacks methodology; the record's caveat that mosdepth skips mate-overlap correction by default was wrong and is corrected. Notable (878 stars, widely cited Bioinformatics paper, bioconda); keep as a project entry with language_level_claim false.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/README.md>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/nim.cfg>
  - <https://github.com/brentp/mosdepth>
  - <https://github.com/brentp/mosdepth/commits/master>
  - <https://raw.githubusercontent.com/samtools/samtools/HEAD/Makefile>
  - <https://raw.githubusercontent.com/nim-lang/Nim/HEAD/config/nim.cfg>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/README.md>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/nim.cfg>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/mosdepth.nim>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/mosdepth.nimble>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/depthstat.nim>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/int2str.nim>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/scripts/install.sh>
  - <https://raw.githubusercontent.com/brentp/mosdepth/HEAD/.github/workflows/build.yml>
  - <https://github.com/brentp/mosdepth>
  - <https://github.com/brentp/mosdepth/commits/master>
  - <https://github.com/brentp/mosdepth/issues?q=is%3Aissue+samtools>
  - <https://github.com/brentp/mosdepth/issues/268>
  - <https://github.com/brentp/mosdepth/issues/234>
  - <https://raw.githubusercontent.com/samtools/samtools/HEAD/NEWS.md>
  - <https://github.com/samtools/samtools/pull/1428>
  - <https://raw.githubusercontent.com/ChristopherWilks/megadepth/HEAD/README.md>
  - <https://raw.githubusercontent.com/38/d4-format/HEAD/README.md>
  - WebSearch: mosdepth vs samtools depth speed benchmark (snippets of the Bioinformatics 2018 paper and the Megadepth Bioinformatics 2021 paper)
  - <https://github.com/brentp/mosdepth/tags?after=v0.2.6>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/brentp/mosdepth`) · [data/wave14/enrich/raw/github_com_brentp_mosdepth.json](../../../data/wave14/enrich/raw/github_com_brentp_mosdepth.json) (enrichment confidence 0.75)

</details>
