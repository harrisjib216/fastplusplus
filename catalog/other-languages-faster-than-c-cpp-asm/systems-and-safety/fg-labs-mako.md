# mako (fg-labs, Rust SAM/BAM sorter built on the fgumi sort engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust SAM/BAM sorter packaging fgumi's external merge-sort engine; claims about 1.9x over samtools sort in template-coordinate order.

| | |
|---|---|
| **Beats** | samtools sort (C, htslib), template-coordinate order |
| **Claimed result** | README: 'On a 30M-read WGS BAM, the engine sorts roughly 1.9x faster than samtools sort for template-coordinate order'; detailed benchmarks are deferred to the fgumi documentation. |
| **Workload** | Sorting a 30M-read whole-genome-sequencing BAM into template-coordinate order. |
| **Metric** | throughput |
| **Compiler and flags** | Cargo [profile.release] lto = "fat", codegen-units = 1, mimalloc allocator (Cargo.toml); rustc version, samtools version, build and command line not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 9 stars, 0 forks, 29 commits; published on crates.io as fg-mako and on Bioconda; sort engine comes from fulcrumgenomics/fgumi (57 stars) |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/fg-labs/mako) · [benchmark](https://raw.githubusercontent.com/fg-labs/mako/HEAD/README.md) |

## Verdict

A single first-party sentence says the engine sorts a 30M-read WGS BAM into template-coordinate order about 1.9x faster than samtools sort; no hardware, thread count, memory limit, samtools version, compression level or command is given anywhere in mako or fgumi, and the two tools' defaults differ in output compression level (1 vs 6).

## Use it when

- Template-coordinate sorting before UMI grouping or deduplication (fgumi group/dedup), where samtools sort --template-coordinate also ignores the tc tag on secondary and supplementary reads.
- Large WGS BAMs that spill to disk on a box with a generous open-file limit and fast or several temp volumes (-T is repeatable).
- Pipelines that pipe sorted output straight into another tool: --compression-level 0 writes stored BGZF with no DEFLATE.
- Checking whether a BAM is already sorted without rewriting it (--verify).

## Skip it when

- When you need a measured, reproducible win over samtools: the only number is one README sentence with no hardware, thread count, memory limit, samtools version or command.
- As a literal command-line drop-in for `samtools sort in.bam -o out.bam`: input needs -i, the default order is template-coordinate (not coordinate), and plain `queryname` is lexicographic, not samtools -n natural order.
- When output size matters and you keep defaults: output is BGZF level 1 by default versus htslib's level 6, so files are larger unless --compression-level is raised.
- If you want a stable, independently maintained engine: mako has 9 stars and 0 forks, all sort logic lives in fgumi (pre-1.0, APIs may change), and engine bugs are routed to the fgumi tracker.

## How it is fast

The fgumi-sort engine packs each record's order into a precomputed sort key, sorts in-memory chunks with a parallel radix sort (voracious_radix_sort, an MSD hybrid for template-coordinate keys) and merges spilled runs with a loser tree, so merge comparisons are fixed-width key compares rather than record decodes. BGZF goes through libdeflate (C, via libdeflater), spill files use zstd level 1 instead of BGZF, input is prefetched with an adaptive number of positional reads, and spilled-run consolidation is sized from `ulimit -n` so the final k-way merge usually skips a rewrite pass. Release builds use fat LTO and codegen-units=1.

## Compared with alternatives

The closest sibling for this job is sambamba (D), whose catalogued CRG comparison has samtools winning on sort; pick mako when you need template-coordinate order or a currently maintained spill-to-disk sorter, and keep samtools when compatibility with existing scripts and default output size matter more than a speedup that has never been published with methodology.

## Integration

| | |
|---|---|
| **Form** | CLI binary (crate fg-mako, Bioconda fg-mako, prebuilt Linux and macOS binaries); the engine is usable as the fgumi-sort library crate |
| **Dependencies** | fgumi 0.7.0 (fgumi-sort, noodles, rayon, crossbeam, voracious_radix_sort), libdeflate via libdeflater (C), zstd (C libzstd), mimalloc (C), clap, env_logger |
| **Minimum toolchain** | Rust 1.93.0 (rust-version and rust-toolchain.toml pin), edition 2024 |
| **Platforms** | Linux and macOS on x86_64 and aarch64 (release binaries); other targets not documented |
| **Thread safety** | not applicable (CLI); --threads (default 1), --sort-threads and --merge-threads control the internal pools, and the output is byte-identical across thread splits per the help text |
| **Drop-in for the baseline** | partial: same sort orders, a samtools-like 768M-per-thread memory default and 1-thread default, but different flags (-i/-o), a template-coordinate default order, lexicographic queryname by default, and output compression level 1 instead of 6 |

## Gotchas

- Unequal default work behind the 1.9x claim: mako/fgumi write output at libdeflate level 1 (CompressionOptions default_value_t = 1), while samtools sort leaves htslib's default (level 6; bgzf.c maps -1 to 6 for libdeflate) and spills at level 1; temp spills are zstd level 1 in mako. The command behind the 1.9x is unpublished, so a default-versus-default run would credit cheaper output compression to the sorter.
- The compared outputs are not the same order for every record: fgumi's best-practices.md says samtools sort --template-coordinate does not consult the tc tag for secondary and supplementary reads and is not a substitute; fgumi's CI (PR #577) only gates sort correctness against an unpinned apt samtools, tie-insensitively, and records no timings.
- Running mako without --order produces template-coordinate output, and --write-index is accepted only for coordinate order to a seekable file.
- CRC32 checking is on for file input and off by default for stdin; the engine is being refactored (the legacy sort path was removed for fgumi 0.8.0, where a release candidate briefly stopped enforcing --max-temp-files, issue #991, fixed before release; mako 0.1.7 is on 0.7.0 and unaffected).

## Known shortcomings

- One first-party README sentence ('1.9x vs samtools sort', also in fgumi src/lib/commands/sort.rs) with no hardware, threads, memory or samtools version; outputs differ (samtools ignores the tc tag on secondary/supplementary reads); a thin packaging of the fulcrumgenomics/fgumi engine (not listed).
- Unequal default work behind the 1.9x: mako/fgumi write output at BGZF level 1 (fgumi CompressionOptions) while samtools sort defaults to level 6 (htslib bgzf.c), so the unpublished command may credit cheaper compression to the sorter. The default --order is template-coordinate with lexicographic queryname, so it is not a CLI drop-in. fgumi PR #577 gates correctness against samtools only, with no timings.

## Caveats and trade-offs

One first-party sentence with no hardware, thread count, memory limit, samtools version or command. The README defers 'detailed benchmarks' to the fgumi documentation, but fgumi's README, docs/src/guide/performance-tuning.md and best-practices.md (opened) carry no samtools timings; the only other occurrence is the bare '1.9x faster than samtools on template-coordinate sort' line in fgumi src/lib/commands/sort.rs. The two tools do not produce the same order: fgumi's best-practices.md says samtools sort --template-coordinate does not consult the tc tag when ordering secondary and supplementary reads and is not a substitute for fgumi sort, so the compared work differs. fgumi does BGZF (de)compression through libdeflate (C, via libdeflater) and uses mimalloc (C); whether the samtools build used libdeflate is unknown. mako is a thin packaging of fgumi's sort engine (all sort logic lives upstream); if fgumi is listed later, mako folds into it. [retier] mako/fgumi write output at BGZF level 1 while samtools sort defaults to level 6, so the unpublished 1.9x command may credit cheaper compression to the sorter. The default --order is template-coordinate with lexicographic queryname, so it is not a CLI drop-in. fgumi PR #577 gates correctness against samtools only, with no timings.

Drop-in only for the common cases of samtools sort; some sort orders and options differ. Spills sorted runs to temp files (--max-temp-files auto).

## Maintenance

Active (0.1.7 on 2026-08-25, tracking fgumi releases; MIT; 198 crates.io downloads) and easy to install through cargo or Bioconda, but it is a thin wrapper over a fast-moving pre-1.0 engine and its speed claim is unreproducible and possibly inflated by a lower default output compression level.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number is one first-party README sentence ('roughly 1.9x faster than samtools sort for template-coordinate order' on a 30M-read WGS BAM), repeated as '1.9x faster than samtools on template-coordinate sort' in fgumi's src/lib/commands/sort.rs help text; no benchmark code, hardware, thread count, memory limit or samtools version anywhere, so C.
- **Verifier notes:** Claim confirmed as a single unsupported first-party sentence; tier C stands. Shortcomings: no methodology at all (hardware, threads, memory, samtools version), compared outputs differ (samtools ignores the tc tag on secondary/supplementary reads), and mako is only a packaging of fulcrumgenomics/fgumi's engine (fgumi is not in the list; if it is added, record mako as duplicate). Metadata checked: MIT, last commit 2026-08-25, active.
- **Fields the verifier corrected:** `stars_or_usage`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-108 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/README.md>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/LICENSE>
  - <https://github.com/fg-labs/mako>
  - <https://github.com/fg-labs/mako/commits>
  - <https://github.com/fulcrumgenomics/fgumi>
  - <https://github.com/fulcrumgenomics/fgumi/tree/main/docs/src>
  - <https://github.com/fulcrumgenomics/fgumi/tree/main/docs/src/guide>
  - <https://github.com/fulcrumgenomics/fgumi/tree/main/benches>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/docs/src/guide/performance-tuning.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/docs/src/guide/best-practices.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/docs/src/guide/migration-from-fgbio.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/README.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/src/lib/commands/sort.rs>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/README.md>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/THIRDPARTY.toml>
  - <https://raw.githubusercontent.com/fg-labs/mako/HEAD/CONTRIBUTING.md>
  - <https://github.com/fg-labs/mako/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/fg-mako>
  - <https://crates.io/api/v1/crates/fgumi>
  - <https://crates.io/api/v1/crates/fgumi-sort>
  - <https://crates.io/api/v1/crates/voracious_radix_sort>
  - <https://github.com/fulcrumgenomics/fgumi>
  - <https://github.com/fulcrumgenomics/fgumi/tree/main/docs/src>
  - <https://github.com/fulcrumgenomics/fgumi/tree/main/scripts>
  - <https://github.com/fulcrumgenomics/fgumi/issues?q=is%3Aissue+sort>
  - <https://github.com/fulcrumgenomics/fgumi/issues/991>
  - <https://github.com/fulcrumgenomics/fgumi/pull/541>
  - <https://github.com/fulcrumgenomics/fgumi/pull/577>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/README.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/src/lib/commands/sort.rs>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/src/lib/commands/common.rs>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/docs/src/guide/performance-tuning.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/docs/src/guide/best-practices.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/crates/fgumi-sort/Cargo.toml>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/crates/fgumi-sort/README.md>
  - <https://raw.githubusercontent.com/fulcrumgenomics/fgumi/HEAD/crates/fgumi-sort/src/lib.rs>
  - <https://raw.githubusercontent.com/samtools/htslib/develop/bgzf.c>
  - <https://raw.githubusercontent.com/samtools/samtools/develop/bam_sort.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/fg-labs/mako`) · [data/wave14/enrich/raw/github_com_fg_labs_mako.json](../../../data/wave14/enrich/raw/github_com_fg_labs_mako.json) (enrichment confidence 0.6)

</details>
