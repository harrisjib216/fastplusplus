# vcflib (vcfputtogetheragain)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> Plain C VCF tool merging overlapping records into multi-allelic records; claimed \~200x faster than vcflib's own zig vcfcreatemulti.

| | |
|---|---|
| **Beats** | vcfcreatemulti zig implementation (vcflib's own earlier tool for merging overlapping VCF records) |
| **Claimed result** | \~200x faster on large VCFs (release notes wording) |
| **Workload** | Merging overlapping records back into multi-allelic VCF records on large VCF files (the companion step to vcfwave); the 13.8 MB scaffold612 sample is the only large input named in the commit. |
| **Metric** | throughput |
| **Adoption** | 686 stars; packaged in Guix, Homebrew, Debian and Conda |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/vcflib/vcflib) · [benchmark](https://github.com/vcflib/vcflib/blob/master/RELEASE_NOTES.md) |

## Verdict

The only number is one first-party sentence added to the unreleased 'ChangeLog ongoing' section of RELEASE_NOTES.md (commit 779cf28, 2026-09-18): '\~200x faster on large VCFs' than the zig implementation of vcfcreatemulti, with no input file, timings, compiler, flags or hardware in the release notes, commit messages, source or tests. The baseline is vcflib's own zig path (now off by default) driven by a C++ loop that parses and deep-copies every record, not bcftools norm or another incumbent, and the two tools do not produce identical output (merged records lose non-GT FORMAT fields in the C tool).

## Use it when

- Rebuilding multi-allelic records with genotypes after vcfwave on a default vcflib build: zig is now off by default (NO_ZIG=ON), and the fallback vcfcreatemulti C++ path is documented in its own help text as 'old C++ implementation does not do genotypes'.
- Pipelines that must avoid a zig compiler and C++/htslib linkage: the tool is two plain C files with no dependency beyond libc.
- Inputs already split to one ALT per record (for example by bcftools norm -m-), where the default mode reproduces the zig tool's ALTs and genotypes on the repo's shared regression inputs.
- Large multi-sample VCFs where most records do not overlap, since those lines pass through untouched without per-sample parsing.
- When strict VCFv4.5 checking of every data line is wanted as a side effect (add --validate for per-sample GT range checks).

## Skip it when

- Inputs that contain multi-allelic records, with or without --norm-multiallelic: default mode drops their ALT alleles (spec-violating output flagged MULTI=ALTPROBLEM), and --norm-multiallelic renumbers genotypes wrongly (see gotchas).
- When merged records must keep FORMAT fields other than GT (DS, GP, GQ, AD): the tool drops them from every merged record.
- Compressed input: it reads plain text only (fopen plus getline, no zlib or htslib), so bgzipped VCFs must be piped through bgzip -dc first.
- Older or loosely formatted VCFs: any data line failing the strict VCFv4.5 checks aborts the run with exit 1, and there is no lenient mode.
- Complex regions or production normalization: bcftools norm -m+ is the widely used incumbent and was never compared; the merge rule lets a later record's allele overwrite an earlier call on the same haplotype, and the vcfcreatemulti doc itself says such results can be incorrect.

## How it is fast

There is no new algorithm: the windowing (grow the window while POS is below the furthest REF end seen) is a line-by-line port of vcfcreatemulti's main loop and the zig merge code. The gain comes from skipping vcflib's C++ Variant object model: each line is split in place on tabs, only GT is parsed per sample and only for merged windows, non-overlapping lines are echoed instead of parsed and re-serialized, and there is no per-record deep copy (the baseline's C++ driver copies a full Variant with `auto first = vars.front()` for every incoming record and pushes Variant copies into the window). Every data line still passes a linear-scan VCFv4.5 validator (vcf-std) before merging.

## Compared with alternatives

None of the catalogued csv-tabular siblings understands VCF semantics; zsv, xan or frawk are the tools for selecting, filtering or counting columns of a VCF body as TSV. Pick vcfputtogetheragain only for the VCF-specific job of merging overlapping records with REF expansion and genotype renumbering, which no sibling does.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc (src/vcf-std.c ships alongside); building it through vcflib's CMake pulls in the whole project's requirements (htslib, tabixpp via pkg-config) |
| **Minimum toolchain** | any C compiler with POSIX getline (_GNU_SOURCE); CMakeLists.txt pins no C standard; Release builds add -march=native |
| **Platforms** | POSIX systems (Linux, macOS); no SIMD or architecture-specific code |
| **Thread safety** | single-threaded command-line tool with static warning flags; no library API |
| **Drop-in for the baseline** | partial — same input and invocation as vcfcreatemulti, and the same ALTs and genotypes on the repo's shared regression inputs, but merged records lose non-GT FORMAT fields, pass-through lines keep QUAL '.', the INFO header description names vcfputtogetheragain, and the --quiet/--legacy options are absent |

## Gotchas

- --norm-multiallelic genotype renumbering bug: expand_alt() runs split_inplace() on each record's ALT field (commas become NUL bytes) before print_merged() counts commas in that same field to build the genotype offsets, so the count is always zero and offsets equal the window index, as in zig mode. Alleles from any record that follows a multi-allelic record in the same window point at the wrong merged ALT. The repo's own expected output shows it: in test/data/regression/vcfputtogetheragain-norm_3.vcf at scaffold612:11809 (CTT&gt;CTTT,C,CT followed by C&gt;A), sample I269_FCB068JABXX_L8_COLcalRBBDIAAPE's 0|1 call for the A SNP is written as 0|2 (the C deletion) instead of 0|4 (ATT). vcfvalidate still passes because index 2 is in range, so the release note's '256 previously invalid records' fix can yield valid-looking but wrong genotypes.
- FORMAT truncation: sample_gt() splits the record's FORMAT column in place at ':', so on every merged record FORMAT collapses to GT and DS/GP and other keys disappear. The source comment says other FORMAT fields keep the first record's values ('Same behaviour here'), and the test doc says outputs compare one-to-one with vcfcreatemulti, but the expected vcfputtogetheragain_7.vcf has FORMAT=GT on all 8 merged records while the zig output vcfcreatemulti_8.vcf for the same scaffold612 input keeps GT:DS:GP.
- Default mode follows the zig semantics: ALTs of multi-allelic input records are skipped while their renumbered genotypes and INFO values are kept, so records can carry GT indices beyond the ALT count and AF lists longer than ALT (scaffold612:15108 has ALT=C with AF=0.166,0.949,0.034), flagged MULTI=ALTPROBLEM; a warning is printed only once per run.
- The window's furthest REF end is recomputed over all window records for each incoming line (quadratic in window size), and the strict validator stops the whole run at the first invalid data line.

## Known shortcomings

- Tier C, weak: the only evidence is one '\~200x faster on large VCFs' line in the unreleased RELEASE_NOTES section with no timings or harness; the baseline is vcflib's own zig vcfcreatemulti, which had a use-after-free crash fixed the same week and is now off by default (NO_ZIG=ON); loose fit for csv-tabular; the 2022 PLoS paper predates the tool (blocked).
- Enricher: correctness bugs in vcfputtogetheragain itself. With --norm-multiallelic, expand_alt() runs split_inplace() on the ALT field (commas become NUL) before print_merged() counts commas to build genotype offsets, so the count is always 0 and the offset equals the window index; the repo's own expected output test/data/regression/vcfputtogetheragain-norm_3.vcf shows it at scaffold612:11809 (a 0|1 A SNP written as 0|2, should be 0|4) while vcfvalidate still passes, so the 'fixes 256 invalid records' claim can yield valid-looking wrong genotypes. sample_gt() splits FORMAT in place, so all merged records drop DS/GP (vcfputtogetheragain_7.vcf FORMAT=GT vs the zig vcfcreatemulti_8.vcf keeping GT:DS:GP), contradicting the one-to-one test doc. The \~200x has no harness, input, timings or hardware (RELEASE_NOTES commit 779cf28 only) and the zig baseline's C++ driver deep-copies Variant per record; no bcftools norm comparison. Plain-text input only; strict VCFv4.5 validator aborts on the first bad line; default mode emits spec-violating ALTPROBLEM records; unreleased and not in the README.

## Caveats and trade-offs

Weak entry. The only number is one first-party phrase in the unreleased 'ChangeLog ongoing' section of RELEASE_NOTES.md ('\~200x faster on large VCFs'); no timings, input file, hardware, compiler flags or benchmark script exist in the repo, and the speedup is above 50x with no methodology. The baseline is vcflib's own zig code path of vcfcreatemulti, not an incumbent such as bcftools norm -m+, htslib or vcftools, so this is an internal before/after comparison. That zig path crashed with a use-after-free (zig 'index out of bounds' panic) on files with overlapping multi-allelic records until the commit just before vcfputtogetheragain was added, and zig is now disabled by default (NO_ZIG=ON), so the shipped vcfcreatemulti falls back to the legacy C++ implementation, which was not compared. vcfputtogetheragain is a 1:1 C port of the zig logic with documented 'DIFFERENCE' points, and by default it keeps the zig semantics that drop multi-allelic input records (--norm-multiallelic changes this; 256 previously invalid records on the scaffold612 sample), so outputs are not guaranteed identical to the baseline. The 2022 PLoS Comput Biol paper predates this 2026 tool and cannot hold its benchmarks. The vcf-std validation figure (about 0.11 s to 0.04 s) is again self-comparison. Category fit is loose: this is a VCF record-merging transformation tool, not a CSV/tabular parser. [retier] '\~200x faster on large VCFs' from the unreleased RELEASE_NOTES section (commit 779cf28): no harness, input, timings or hardware; baseline is vcflib's own zig vcfcreatemulti (use-after-free fixed the same week, now off by default, C++ driver deep-copies each Variant). Output bugs: --norm-multiallelic renumbers genotypes wrongly (offset always equals the window index; repo's own regression file shows 0|1 written as 0|2), and FORMAT is truncated to GT (DS/GP dropped). Plain-text input only; strict validator aborts on the first bad line; ALTPROBLEM records violate the spec. Loose fit for csv-tabular.

vcfputtogetheragain is plain C, with no C++ or zig dependency, and passes non-overlapping records through verbatim. Its --norm-multiallelic option deliberately differs from the zig semantics (keeps all ALT alleles, mirrors bcftools norm -m-), so outputs are identical to the zig tool only on shared inputs without that flag. vcflib as a whole is a collection of VCF tools, not a general CSV or VCF parsing library.

## Maintenance

Added 2026-09-18 to actively maintained, MIT-licensed vcflib (last commit 2026-10-02) but not yet in a tagged release or the README tool list, with no outside users found; it is two copyable C files, but the --norm-multiallelic renumbering bug and the FORMAT truncation are baked into its regression expected outputs, so check merged records before relying on them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now D.
- **Tier reason:** RELEASE_NOTES.md (section 'ChangeLog ongoing', not yet in a tagged release) states vcfputtogetheragain is '\~200x faster on large VCFs' than the zig implementation of vcfcreatemulti; that is a first-party one-line claim with no timings, input, hardware, compiler or harness anywhere in the repo (the commit messages and the src/vcfputtogetheragain.c header carry no numbers), so C.
- **Retiered** C to D: The only number is an unmeasured '\~200x' release-notes line against vcflib's own crashing zig path, and the measured tool has genotype-renumbering and FORMAT-truncation bugs in its output (bug-in-measured-path precedent). Directional only.
- **Verifier notes:** Claim text verified verbatim in RELEASE_NOTES.md; metadata matches (MIT, 686 stars, not a fork, last commit 2026-10-02). Shortcomings: single unmeasured first-party ratio, self baseline (zig path that crashed before a same-week fix and is now off by default), no harness, loose csv-tabular category fit.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 3); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/README.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/src/vcfputtogetheragain.c>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/pytest/vcfputtogetheragain.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/doc/vcfcreatemulti.md>
  - <https://github.com/vcflib/vcflib>
  - <https://github.com/vcflib/vcflib/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/RELEASE_NOTES.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/README.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/src/vcfputtogetheragain.c>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/src/vcf-std.h>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/src/vcfcreatemulti.cpp>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/doc/vcfcreatemulti.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/pytest/vcfputtogetheragain.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/pytest/vcfputtogetheragain-norm.md>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain_2.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain_7.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain_8.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain-norm_2.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain-norm_3.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain-norm_4.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfcreatemulti_8.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/inputs/issue-scaffold612-mini.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/inputs/scaffold612-uaf-region.vcf>
  - <https://github.com/vcflib/vcflib/commits/master>
  - <https://github.com/vcflib/vcflib/commit/70bb247>
  - <https://github.com/vcflib/vcflib/commit/779cf28>
  - <https://github.com/vcflib/vcflib/issues?q=is%3Aissue+vcfcreatemulti>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain_3.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain_4.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain_5.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfputtogetheragain_6.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfcreatemulti_2.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfcreatemulti_3.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfcreatemulti_4.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfcreatemulti_5.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfcreatemulti_6.vcf>
  - <https://raw.githubusercontent.com/vcflib/vcflib/HEAD/test/data/regression/vcfcreatemulti_7.vcf>
  - WebSearch: vcfputtogetheragain vcflib (no outside mention found)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/vcflib/vcflib`) · [data/wave3/enrich/raw/github_com_vcflib_vcflib.json](../../../data/wave3/enrich/raw/github_com_vcflib_vcflib.json) (enrichment confidence 0.6)

</details>
