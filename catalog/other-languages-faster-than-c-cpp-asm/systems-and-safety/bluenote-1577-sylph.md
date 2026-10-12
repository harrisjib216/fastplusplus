# sylph

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust k-mer-sketch metagenome profiler giving species abundances and containment ANI with far less CPU and memory than Kraken2.

| | |
|---|---|
| **Beats** | Kraken2 (C++) |
| **Claimed result** | Paper abstract (search-snippet text only, PMC and bioRxiv blocked): for multisample profiling sylph took more than 10-fold less CPU time than Kraken2 and used 30-fold less memory. Artifact repo bluenote-1577/sylph-test/times: kraken2.time reports 72,628.96 s user + 5,582.99 s system, 1:47:10 wall, 73,857,640 kB max RSS; sylph_sketch_reads.time (sylph sketch -t 20 on 45 paired read sets) 2,186.65 s + 101.51 s, 5:48 wall, 2,831,688 kB; sylph_contain_gtdb.time (sylph contain -t 20, 45 samples) 1,497.39 s + 57.60 s, 2:00 wall, 9,567,920 kB. If these files are the paired runs, sylph uses about 20x less CPU time, about 13.7x less wall time and about 7.7x less peak memory (derived from page data; pairing not confirmed, and the 7.7x memory ratio does not match the paper's 30-fold). README: 'can be &gt; 50x faster than other methods' (no baseline named). |
| **Workload** | Multisample taxonomic profiling of shotgun metagenomes against large genome databases, CPU time and peak memory, as reported in the Nature Biotechnology paper (Shaw and Yu, 2025, 43(8):1348-59); a separate paper figure profiles against 85,205 prokaryotic plus 2,917,516 viral genomes. |
| **Metric** | throughput |
| **Compiler and flags** | Rust; Cargo release profile sets panic=abort and lto=true. The sylph version, toolchain and Kraken2 build used for the paper timings are not stated in the artifact repo files I saw. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | k-mer sketching: subsampled k-mer sketches of reads and genomes (default compression c=200 in the changelog) with containment-based abundance estimation instead of classifying every read, multithreaded and multi-sample; per the paper abstract text and the repo README/CHANGELOG. |
| **Adoption** | 325 stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/bluenote-1577/sylph) · [benchmark](https://pmc.ncbi.nlm.nih.gov/articles/PMC12339375/) |

## Verdict

The Nature Biotechnology paper (Shaw and Yu) reportedly says sylph took more than 10-fold less CPU time and 30-fold less memory than Kraken2 for multisample profiling (abstract text seen only in search snippets). The authors' artifact repo holds raw /usr/bin/time outputs for 45 paired gut samples: Kraken2 78,212 CPU-seconds, 1:47:10 wall and 73.9 GB peak against sylph sketch plus contain (-t 20) at 3,843 CPU-seconds, 7:48 wall and 9.6 GB peak, about 20x CPU, 13.7x wall and 7.7x memory (derived from page data), on an unstated CPU with unknown Kraken2 version, database and command; the tools produce different outputs, so this is an algorithmic gap, not a Rust-over-C++ one.

## Use it when

- Species-level abundance profiling of many shotgun samples against GTDB-scale databases (100k-200k genomes) on a workstation; the README cites about 5 GB of RAM for GTDB-R232.
- Low-coverage samples where you want containment ANI to reference genomes or your own MAGs (the README claims accurate ANI down to 0.1x coverage).
- Large cohorts where Kraken2's per-sample run with a roughly 70 GB database would dominate: in the authors' artifact time files, 45 paired samples took 78,212 CPU-seconds for Kraken2 against about 3,843 for sylph's sketch plus profile.
- Nanopore or PacBio long-read metagenomes as well as short reads, with custom databases built from your own genomes.

## Skip it when

- You need per-read classification (binning reads, extracting reads of a taxon, host-read removal): sylph assigns no reads, and Kraken2 or a read mapper is the tool.
- Taxonomic resolution above or below species without reference genomes, or organisms absent from the database: sylph only reports genomes in the sketched database, and unknown fractions are rough estimates (-u option).
- Small genomes or very low-abundance taxa near the detection floor: profiling needs at least 10 sampled k-mers per genome (-M) and 7 contained k-mers by default, so short viral genomes can drop out.
- Pipelines that cannot tolerate format churn: sketch formats changed across versions (.sylqueries/.sylsample, then .syldb/.sylsp, now optional .syl2db readable only by v1.0.0+), and the pseudotax option once required regenerated files.

## How it is fast

It replaces per-read classification against a large k-mer hash table with FracMinHash sketching: only k-mers (k=31 by default) whose 64-bit mixed hash falls below u64::MAX/c are kept (c=200, so about 1 in 200), hashed four lanes at a time with AVX2 when the CPU has it; reads are deduplicated through a hash set or scalable cuckoo filter. Abundance and ANI come from containment counts corrected by a zero-inflated Poisson model of low coverage, with winner-take-all k-mer reassignment between similar genomes, so the database and sample sketches stay a few GB. v1.0.0 (September 2026) adds an optional two-stage .syl2db database (a sparse c=3000 screen, then Golomb-Rice-compressed dense blocks loaded on demand) and multithreaded read sketching.

## Compared with alternatives

Among the siblings, skani (same author, same sketching approach) estimates ANI between assembled genomes or MAGs, while sylph profiles raw reads against a whole database; pick sylph for read-level metagenome profiling and skani for genome-to-genome comparison. The other bioinformatics siblings (mosdepth, sambamba, noodles, rasusa, mako) handle alignments, FASTA indexing or subsampling, not taxonomic profiling.

## Integration

| | |
|---|---|
| **Form** | CLI binary (Rust crate built with cargo from the GitHub repo; the crates.io name 'sylph' belongs to an unrelated 2016 crate; a conda package is referenced in issue #2) |
| **Dependencies** | needletail 0.5 (FASTA/FASTQ parsing), rayon, crossbeam-channel, boomphf, fxhash, scalable_cuckoo_filter, flate2 with the zlib-ng backend, statrs, nalgebra, bincode, serde; tikv-jemallocator on musl builds |
| **Minimum toolchain** | Rust edition 2021 (no rust-version declared in Cargo.toml); release profile uses lto=true and panic=abort |
| **Platforms** | x86-64 Linux primary (AVX2 k-mer hashing chosen at runtime with is_x86_feature_detected and a scalar fallback; static musl target configured in .cargo/config.toml); other targets presumably via the scalar path, not documented here |
| **Thread safety** | not applicable as a library; the CLI parallelizes over samples and, since v1.0.0, within read sketching (-t threads, default 3; -s samples processed concurrently) |
| **Drop-in for the baseline** | no |

## Gotchas

- Kraken2 comparison harness is lopsided and unverifiable: the artifact kraken2.time ran ./scripts/kraken2.sh, which is missing from sylph-test (404), and records 599,547,602 minor page faults (about 2.2 TiB of 4 KiB pages) and 204,536,960 file-system output blocks (about 97.5 GiB at 512 bytes per block) with a 73.9 GB peak RSS, which points to the roughly 70 GB database being reloaded per sample and per-read output being written inside Kraken2's timed run, while sylph writes one small TSV (inferred from the time file; the script itself is unseen).
- The artifact sylph timings use the legacy .sylqueries and .sylsample formats (still accepted as old suffixes in src/constants.rs), so they come from an early sylph release; the paper's 30-fold memory figure does not match the 7.7x ratio in these files (73.9 GB against 9.6 GB peak), and the database sketching run (1:31 wall at 1727% CPU) is excluded on the sylph side, as is Kraken2's database build.
- Release builds use panic=abort, so one corrupted FASTQ aborts the whole multi-sample run with a needletail slice-index panic (issue #65, 180 metagenomes against GlobDB); validate inputs first.
- Default thread count is 3 (-t), so throughput figures quoted at -t 20 need the flag; read deduplication with cuckoo filters raised sketching memory 3-4x when it was introduced (CHANGELOG).

## Known shortcomings

- Downgraded from B to C: the paper's Kraken2 claim (more than 10x less CPU, 30x less memory) was seen only in snippets; the sylph-test raw time files give about 20x CPU, 13.7x wall and 7.7x memory (derived) but the pairing is unconfirmed, no CPU model is stated and kraken2.sh returns 404. Sketch-based profiling against read classification is an algorithmic win, not a language one. Licence MIT.
- Enricher: the Kraken2 side of the artifact is lopsided: kraken2.sh is missing, and kraken2.time shows 599,547,602 minor faults (about 2.2 TiB) and about 97.5 GiB of file-system output at 73.9 GB RSS, consistent with the database being reloaded per sample and per-read output counted inside Kraken2's time (inferred). The sylph time files use legacy formats from an early release. Derived ratios 20x CPU, 13.7x wall, 7.7x memory (the paper says 30x); panic=abort means one corrupt FASTQ kills the whole run (#65).

## Caveats and trade-offs

Snippet only: the PMC, Nature and bioRxiv pages are unreachable from this environment, so the paper's Kraken2 figures come from search-result text; paper tables, thread counts, CPU model, database sizes and the MetaPhlAn comparison were not seen. The two tools differ in algorithm (sylph sketches reads and genomes with subsampled k-mers and estimates containment-based abundance; Kraken2 classifies every read's k-mers against a large hash table), so the ratios compare tools with different outputs and are not a language effect. The sylph-test/times files are raw /usr/bin/time outputs with no CPU model: Kraken2 ran a ./scripts/kraken2.sh that is not in the repo (404), at about 12 cores of CPU (1216%), while sylph ran with -t 20; the files do not say which database Kraken2 used or that they are the pair behind the paper figure, and their memory ratio (about 7.7x) differs from the paper's 30-fold. The README names no baseline for its '&gt;50x faster' claim and compares precision with 'Kraken', not speed. The repo LICENSE file is MIT only, although Cargo.toml declares 'MIT OR Apache-2.0' and no Apache-2.0 text ships. Kraken2 is not in the catalog's verified lists. Documentation moved to sylph-docs.github.io, which is blocked here. [retier] Enricher: kraken2.sh is missing; kraken2.time shows about 2.2 TiB of minor faults and 97.5 GiB of output at 73.9 GB RSS, consistent with per-sample database reloads and per-read output inside Kraken2's time (inferred); derived ratios 20x CPU, 13.7x wall, 7.7x memory.

Abundance-corrected k-mer sketching: reports containment ANI and abundances against a pre-sketched database, species-level only, and trades per-read classification for sketch lookups. The README says it is about as precise and sensitive as marker-gene methods (MetaPhlAn, mOTUs) and has fewer false positives than Kraken, but no numbers are on the README.

## Maintenance

Actively developed (v1.0.0 with the two-stage database and multithreaded read sketching in September 2026, last commit 2026-10-10, 325 stars, 7 open issues), MIT-licensed per the LICENSE file (Cargo.toml says MIT OR Apache-2.0); it is a standalone tool to install, not code to vendor into C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The peer-reviewed comparison with Kraken2 was seen only through search-result snippets (PMC, Nature and bioRxiv unreachable: getaddrinfo ENOTFOUND), so under the snippet-only rule it cannot hold B. The paper's artifact repo (bluenote-1577/sylph-test/times) carries first-party /usr/bin/time outputs for Kraken2 and sylph, but with no CPU model, no Kraken2 command or database, and no statement of which files back the paper figure.
- **Verifier notes:** Downgraded B to C: the peer-reviewed Kraken2 comparison is snippet-only, and the artifact repo's raw time files (Kraken2 78,212 CPU-seconds against sylph's 3,843 for sketch plus contain, about 20x derived) are first-party, lack a CPU model and Kraken2 command, and give a 7.7x memory ratio rather than the paper's 30x. Sketch containment against read classification is an algorithmic win, not a Rust-over-C++ one. License corrected to MIT (LICENSE file); baseline_in_list left as recorded, though Kraken2 has no catalog entry.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-116 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/bluenote-1577/sylph>
  - <https://github.com/bluenote-1577/sylph/commits>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/LICENSE>
  - <https://github.com/bluenote-1577/sylph-test>
  - <https://github.com/bluenote-1577/sylph-test/tree/main/times>
  - <https://github.com/bluenote-1577/sylph-test/tree/main/scripts>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/kraken2.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/sylph_contain_gtdb.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/sylph_sketch_reads.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/sylph_sketch_gtdb.time>
- **Sources the enricher read:**
  - <https://github.com/bluenote-1577/sylph>
  - <https://github.com/bluenote-1577/sylph/commits/main>
  - <https://github.com/bluenote-1577/sylph/tree/main/src>
  - <https://github.com/bluenote-1577/sylph/issues?q=is%3Aissue+memory+OR+slow+OR+bug>
  - <https://github.com/bluenote-1577/sylph/issues/65>
  - <https://github.com/bluenote-1577/sylph/issues/41>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/README.md>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/src/constants.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/src/avx2_seeding.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/src/seeding.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/src/sketch.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/src/contain.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/src/cmdline.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph/HEAD/src/twostage_db.rs>
  - <https://github.com/bluenote-1577/sylph-test/tree/main/times>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/README.md>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/kraken2.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/sylph_contain_gtdb.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/sylph_sketch_reads.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/sylph_sketch_gtdb.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/metaphlan_20_threads_time.time>
  - <https://raw.githubusercontent.com/bluenote-1577/sylph-test/main/times/mash_screen_gtdb.time>
  - <https://crates.io/api/v1/crates/sylph>
  - WebSearch snippets: Rapid species-level metagenome profiling and containment estimation with sylph (Nature Biotechnology, DOI 10.1038/s41587-024-02412-y; full text unreachable)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/bluenote-1577/sylph`) · [data/wave14/enrich/raw/github_com_bluenote_1577_sylph.json](../../../data/wave14/enrich/raw/github_com_bluenote_1577_sylph.json) (enrichment confidence 0.6)

</details>
