# parasail

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `LicenseRef-Battelle-BSD-style` · 🟡 stale

> C99 SIMD library of local, global and semi-global pairwise sequence alignment kernels; beats SSW on protein database search.

| | |
|---|---|
| **Beats** | SSW (Complete-Striped-Smith-Waterman-Library, C, SSE2 striped Smith-Waterman); the same page also times Opal, SWIPE and ssearch36 |
| **Claimed result** | performance.md, Intel Haswell E5-2670 v3 table (seconds per database search for the 110/195/390/513-residue queries, mean of three runs): SSW (SSE2) 12.0 / 25.6 / 41.5 / 48.7; parasail AVX2 16-bit 9.3 / 12.0 / 17.4 / 21.5 (about 1.3x, 2.1x, 2.4x and 2.3x faster than SSW, derived from page data); parasail SSE4.1 16-bit 10.8 / 15.9 / 27.4 / 33.8 (about 1.1x to 1.6x, derived from page data). MacBook Pro i5 table: SSW (SSE2) 13.2 / 27.1 / 41.7 / 52.4 vs parasail SSE4.1 16-bit 11.3 / 15.9 / 25.8 / 36.9 (about 1.2x to 1.7x, derived from page data). SWIPE (SSSE3) is faster than parasail SSE4.1 16-bit on all four queries on the MacBook (7.6 / 13.3 / 24.7 / 32.0 s) but on Haswell only at 110 residues (9.6 vs 10.8 s); there parasail SSE4.1 16-bit is faster at 195, 390 and 513 residues and parasail AVX2 16-bit beats SWIPE, Opal AVX2 and ssearch36 on all four queries. |
| **Workload** | Score-only Smith-Waterman search of four query sequences (110, 195, 390 and 513 residues) against UniProtKB/Swiss-Prot (547,964 sequences), BLOSUM50, gap open 3, gap extend 1, one thread, mean of three runs, whole-database wall time in seconds. |
| **Metric** | throughput |
| **Hardware** | Haswell table: Intel Xeon E5-2670 v3 at 2.3 GHz, 64 GB DDR4-2133. Second table: MacBook Pro, Intel i5 at 2.53 GHz, 8 GB (SSE4.1 only). |
| **Compiler and flags** | Haswell table: Intel ICC 15.0.1, -O3. MacBook table: Apple LLVM 6.0 (clang-600.0.57), flags not stated. Command lines are given: parasail_aligner -x -t 1 -a sw_striped_profile_avx2_256_16 -o 3 -e 1 -m blosum50 -f uniprot_sprot -q &lt;query&gt;; ssw_test -p uniprot_sprot.fasta &lt;query&gt;. |
| **Adoption** | 289 stars; cited BMC Bioinformatics 2016 library |
| **Last commit** | 2025-08-27 |
| **Links** | [repository](https://github.com/jeffdaily/parasail) · [benchmark](https://github.com/jeffdaily/parasail/blob/master/performance.md) |

## Verdict

On a 2.3 GHz Xeon E5-2670 v3 with Intel ICC 15.0.1 -O3, one thread, BLOSUM50, gap open 3 and extend 1, score-only search of four queries (110-513 residues) against 547,964 Swiss-Prot sequences took 9.3-21.5 s with parasail's AVX2 16-bit striped profile kernel versus 12.0-48.7 s for SSW's SSE2 ssw_test, and 10.8-33.8 s with parasail SSE4.1 16-bit (mean of three runs, 2015). The SSW timer includes database parsing and suboptimal-score work, so part of the gap is harness rather than kernel.

## Use it when

- Protein or DNA database search where one query is aligned against many targets: build a profile once and call the striped profile functions per target.
- You need several alignment modes (local, global, semi-global with free end gaps on either sequence) from one library with one calling convention.
- x86-64 hosts with AVX2 where queries are a few hundred residues or longer: the AVX2 16-bit striped kernel was 2.1x to 2.4x faster than SSW at 195-513 residues on Haswell.
- You want to compare vectorization strategies (striped vs scan vs diagonal) for your own sequence-length mix; parasail ships all of them behind the same API.
- Python, Java or Rust callers who want a maintained binding (parasail-python, parasail-java, parasailors) to the same kernels.

## Skip it when

- Pure many-target protein database search on SSSE3-class hardware: SWIPE (inter-sequence vectorization) was faster than parasail SSE4.1 16-bit on every query in the MacBook table, and the author's own text says SWIPE remains fastest for that problem.
- Long-read or highly similar DNA alignment: banded or difference-recurrence methods such as ksw2 or wavefront alignment (WFA2-lib) do far less work than a full striped DP.
- Hosts with AVX-512 or modern Apple Silicon expecting tuned kernels: there are no AVX-512 kernels (issue #80 open since 2020) and Apple M1 install problems are open (#85, #89).
- Pipelines that need the SSW secondary (suboptimal) score: parasail's SSW emulation omits it.
- Projects that need an OSI-approved licence: the Battelle BSD-style licence adds a clause that redistributions and publications should cite the 2016 BMC Bioinformatics paper.

## How it is fast

Intra-sequence (query-parallel) vectorization: Farrar's striped layout (2007), the author's prefix-scan formulation (Daily 2015), anti-diagonal (Wozniak 1997) and blocked (Rognes and Seeberg 2000) kernels, each written for SSE2, SSE4.1, AVX2, AltiVec and NEON with 8, 16, 32 and 64-bit lanes. A reusable query profile removes per-target substitution lookups, and the 'sat' variants run 8-bit lanes first (32 lanes on AVX2) and redo the alignment at 16 bits only when the score overflows. The benchmarked win over SSW comes mostly from 256-bit AVX2 lanes and from skipping the 8-bit first pass on long queries.

## Compared with alternatives

Pick parasail over SSW when you want AVX2 kernels, several alignment modes or reusable profiles for database search, and over ksw2 or WFA2-lib when sequences are short-to-medium proteins and you need exact full DP across local, global and semi-global modes; pick ksw2 for global nucleotide alignment with banding (its README measures it ahead of parasail) and WFA2-lib for long similar sequences.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (autotools preferred; CMake and contributed Meson builds also provided) |
| **Dependencies** | none for the library; zlib optional (gzipped FASTA/FASTQ parsing), OpenMP optional (multi-threaded parasail_aligner) |
| **Minimum toolchain** | C99 compiler; CMakeLists.txt declares CMake 3.2 as minimum (open issue #114 reports that minimum as too old for current CMake); Windows via CMake and Visual Studio 2010-2013 as tested in the README |
| **Platforms** | x86 and x86-64 (SSE2, SSE4.1, AVX2 with runtime CPU dispatch), POWER (AltiVec), ARM and aarch64 (NEON; cross-compilation documented); no AVX-512 kernels |
| **Thread safety** | not documented in the README; parasail_aligner calls the profile functions concurrently from OpenMP threads on shared read-only profiles, each call allocating its own result |
| **Drop-in for the baseline** | partial — parasail_ssw and parasail_ssw_profile return an SSW-like struct with CIGAR but no secondary score, under a different API and profile type; the core functions are not SSW-compatible |

## Gotchas

- Width choice is the caller's job: _8 and _16 kernels can saturate, so check parasail_result_is_saturated() or use _sat; open issue #111 (2025) reports parasail_sg_qb_db_diag_avx2_256_16 returning -32757 instead of 21 with the saturated flag at 0, which the maintainer agreed would be a bug.
- Calling an instruction-set-specific function on a CPU that lacks the extension returns NULL with errno ENOSYS rather than faulting; unchecked NULL results crash later. Gap opening applies only the open penalty (README note), which differs from BLAST-style G+kE conventions used by tools such as SWIPE.
- Harness flaw in the SSW baseline: SSW's ssw_test (current src/main.c) starts its clock() timer before the loop that re-opens and parses the whole database FASTA for each query, so database parsing sits inside SSW's timed region although performance.md says read time was not measured (only output suppression is mentioned as a modification). ssw_test also computes SSW's suboptimal score (maskLen = readLen/2) on every target, work parasail skips. Both inflate SSW's times by an unquantified amount.
- Strategy mismatch behind the headline: ssw_test builds its profile with score_size 2 (8-bit first, 16-bit on overflow), which is the same strategy as parasail's 'sat' rows; like for like, parasail SSE4.1 sat is slower than SSW at 390 and 513 residues on Haswell (44.4 vs 41.5 s and 55.2 vs 48.7 s), and the faster parasail rows skip the 8-bit pass entirely.

## Known shortcomings

- Numbers are from 2015 (ICC 15.0.1 -O3, Xeon E5-2670 v3) on unpinned pre-1.0 code; on Haswell SWIPE beats parasail SSE4.1 only at 110 residues. Usability is reference: the Battelle licence is BSD-3-like with a citation clause and is not OSI-approved.
- Enricher: asymmetric harness on the SSW side: ssw_test starts its clock() before re-reading and parsing the whole Swiss-Prot FASTA for every query (performance.md says read time was not measured) and computes the suboptimal score on every target, which parasail skips; ssw_test uses the same 8-then-16-bit strategy as parasail 'sat', and like for like parasail SSE4.1 sat is slower than SSW at 390 and 513 residues (44.4 vs 41.5 s, 55.2 vs 48.7 s). Open wrong-score issue #111 (16-bit sg_qb_db returns -32757 with the saturated flag 0); no AVX-512; stale since v2.6.2 (2023). Downgraded from A to C.

## Caveats and trade-offs

The win is against SSW only in the narrow sense of a 2015-era SSE2 kernel: AVX2 rows compare different instruction sets than SSW's SSE2, and the page names one compiler and -O3 for the Haswell runs without saying how each competitor was built. The numbers were committed in June-July 2015 (performance.md history ends 2015-07-11) against a pre-1.0 parasail whose commit is not pinned. SWIPE (a database-search specialist) is faster than parasail SSE4.1 on every MacBook query and at 110 residues on Haswell, and parasail's 8-bit 'sat' SSE4.1 variant is slower than SSW at the longer queries on Haswell (44.4 vs 41.5 s at 390 and 55.2 vs 48.7 s at 513 residues). Only scores are computed, not alignments or tracebacks. The Swiss-Prot release is not stated. No SeqAn or scalar Smith-Waterman row appears on the page. The BMC Bioinformatics 2016 paper was not opened (NCBI blocked); a search-result summary only says SWIPE is 1.2 to 2.4 times faster than parasail for sequences under 500 residues and parasail is faster for longer ones (snippet, not verified; this disagrees with the Haswell SSE4.1 16-bit rows). The license (LICENSE.md, Battelle Memorial Institute) is BSD-3-Clause-like text plus a clause that redistributions and publications 'should include' a citation of the 2016 BMC paper; it is not an SPDX-listed or OSI-approved license, so usability is reference. Last commit seen on the master branch (2025-08-27); the develop branch was not checked. [retier] Enricher: SSW's timer includes FASTA parsing per query and the suboptimal score; like for like parasail SSE4.1 sat is slower than SSW at 390 and 513 residues (44.4 vs 41.5 s, 55.2 vs 48.7 s); open wrong-score issue #111; no AVX-512; stale since v2.6.2.

C99 library with SSE2, SSE4.1, AVX2, AltiVec and NEON kernels (README), many striped, scan and diagonal variants for global, semi-global and local alignment, with optional statistics or SAM CIGAR traceback (slower than score-only). Several 8-bit, 16-bit and saturating-width variants must be chosen by the user; the 8-bit 'sat' variants fall back to 16-bit on overflow. Language bindings are listed in the README (Python via parasail-python, Rust, Java).

## Maintenance

Stale: last version bump v2.6.2 (March 2023; no GitHub releases are published), one fix commit since (2025-08-27) and 33 open issues including an open wrong-score report (#111); usability is reference because the Battelle BSD-style licence carries a citation clause and is not OSI-approved, though the code is permissive enough for most research use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** performance.md times parasail against SSW, Opal, SWIPE and ssearch36 with exact command lines (harness apps/parasail_aligner.cpp in the repo), compiler Intel ICC 15.0.1 -O3 and CPU Xeon E5-2670 v3 for the Haswell table, so A; all quoted numbers are on the page.
- **Retiered** A to C: Downgraded from A to C (asymmetric-harness precedent): ssw_test charges re-reading and parsing the whole Swiss-Prot FASTA per query and a suboptimal-score computation to SSW only, and like for like (parasail 'sat', same 8-then-16-bit strategy) parasail SSE4.1 is slower than SSW at 390 and 513 residues.
- **Verifier notes:** All quoted numbers are on performance.md; the claim that SWIPE beats parasail SSE4.1 on both machines was wrong for Haswell (SWIPE wins only at 110 residues) and is corrected. Usability changed to reference because the Battelle licence is not OSI-approved (BSD-3-like plus a soft citation clause; orchestrator may judge it copyable). Shortcomings: 2015 numbers on unpinned pre-1.0 code, AVX2 vs SSE2 instruction-set asymmetry, SWIPE faster on the MacBook, score-only workload.
- **Fields the verifier corrected:** `claimed_speedup`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-125 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/performance.md>
  - <https://github.com/jeffdaily/parasail>
  - <https://github.com/jeffdaily/parasail/commits/master>
  - <https://github.com/jeffdaily/parasail/commits/master/performance.md>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/LICENSE.md>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/apps/parasail_aligner.cpp>
- **Sources the enricher read:**
  - <https://github.com/jeffdaily/parasail>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/README.md>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/performance.md>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/apps/parasail_aligner.cpp>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/LICENSE.md>
  - <https://raw.githubusercontent.com/jeffdaily/parasail/master/CMakeLists.txt>
  - <https://github.com/jeffdaily/parasail/commits/master>
  - <https://github.com/jeffdaily/parasail/issues>
  - <https://github.com/jeffdaily/parasail/issues?q=is%3Aissue+bug>
  - <https://github.com/jeffdaily/parasail/issues/73>
  - <https://github.com/jeffdaily/parasail/issues/111>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/master/src/main.c>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/master/src/ssw.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jeffdaily/parasail`) · [data/wave13/enrich/raw/github_com_jeffdaily_parasail.json](../../../data/wave13/enrich/raw/github_com_jeffdaily_parasail.json) (enrichment confidence 0.8)

</details>
