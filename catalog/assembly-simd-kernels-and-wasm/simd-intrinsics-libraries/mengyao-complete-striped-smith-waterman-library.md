# SSW (Complete-Striped-Smith-Waterman-Library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> SSE2 striped Smith-Waterman C library (Farrar method) returning score, positions and CIGAR; claims \~50x over scalar SW.

| | |
|---|---|
| **Beats** | ordinary (non-SIMD) Smith-Waterman local alignment |
| **Claimed result** | README: 'Current version of our implementation is \~50 times faster than an ordinary Smith-Waterman.' Absolute CPU time for the E. coli test: AMD CPU about 880 s (default penalties) or about 460 s (-m1 -x3 -o5 -e2); Intel CPU about 960 s or about 500 s; about 40 MB memory. |
| **Workload** | Smith-Waterman alignment of 1000 Ion Torrent E. coli reads (about 25 to 540 bp) against the 4,938,920-nucleotide E. coli 536 reference using SIMD striped scoring; the README gives CPU time for SSW only. |
| **Metric** | throughput |
| **Hardware** | unspecified AMD and Intel CPUs |
| **Adoption** | 323 stars, 119 forks; packaged in Debian as libssw |
| **Last commit** | 2026-01-15 |
| **Links** | [repository](https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library) · [benchmark](https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library) |

## Verdict

The '\~50 times faster than an ordinary Smith-Waterman' headline has no baseline program, data, compiler or CPU behind it in the repo; the only measured numbers are SSW's own CPU time from ssw_test (clock() around the read loop, Makefile default -O2) aligning 1000 Ion Torrent reads to the 4.94 Mbp E. coli 536 genome: about 880 s (AMD) and 960 s (Intel) with the default -m2 -x2 -o3 -e1, about 460 s and 500 s with -m1 -x3 -o5 -e2, about 40 MB. If reads average 200 bp that is roughly 1.1 billion cell updates per second (derived from page data); the PLoS ONE 2013 paper with the SSEARCH/Farrar comparison could not be opened here.

## Use it when

- Aligning many short reads (tens to a few hundred bp) against a reference or contig when you need the exact local score plus position and CIGAR, e.g. a local realignment step; the paper abstract says MOSAIK, SCISSORS, TANGRAM and RZMBLR swapped in SSW for their ordinary or banded SW modules.
- Protein-vs-protein local alignment with BLOSUM/PAM matrices (ssw_test -p, Blosum50 default) at single-core scale.
- You want two MIT files (ssw.c, ssw.h) to vendor into a C or C++ project, with SSE2 as the only ISA requirement on x86-64 and NEON via the bundled sse2neon.h on ARM.
- Scoring with small penalties (e.g. match 1, mismatch -3) so most scores fit under the 8-bit ceiling and the 16-lane kernel never falls back to 16-bit lanes.
- You need a cheap second-best score (the ZS tag) for mapping-quality style uniqueness checks.

## Skip it when

- End-to-end alignment of long sequences (genomes, contigs of tens of kb): 16-bit scores saturate at 32767 with no warning (open issue #94), the CIGAR traceback buffer grows with band width x query length, and open issue #90 reports a segfault aligning a 110,456 bp contig with -c.
- You want AVX2/AVX-512 width or inter-sequence (batch) vectorization: SSW is 128-bit SSE2 only (issue #89 'avx support' is open); parasail (jeffdaily/parasail, not yet catalogued) offers more ISAs and vectorization strategies.
- Global or semi-global alignment, plain edit distance or non-affine gap models: SSW does local SW only.
- Custom matrices that include a stop-codon (\*) row: open issue #96 reports a '\*' match scored +4 instead of the matrix's +1.
- Scoring schemes where the mismatch penalty is far larger than gap open: issue #93 returned CIGARs whose rescored value did not match the reported score until the 'cigar fixed' commit of 2025-11-17; check s_align.flag (1 = banded traceback failed, 2 = path may miss a part).

## How it is fast

Farrar's striped Smith-Waterman (2007): the query is split into interleaved segments so one 128-bit SSE2 register updates 16 cells (unsigned saturating 8-bit lanes with a bias) or 8 cells (16-bit lanes) per instruction, with a precomputed query profile per reference residue and a lazy-F correction loop (taken from SWPS3) that usually exits after one pass. The 8-bit kernel runs first and the whole scan is redone in 16-bit lanes only when the score reaches 255 minus the bias. The begin position comes from a second striped pass over the reversed read and reference prefix that stops once the best score is reached, and the CIGAR from a scalar banded SW over just the aligned window with a doubling band, so the full-reference scan needs memory linear in read length.

## Compared with alternatives

The catalogued siblings are generic SIMD kernels; the closest in kind is Quickenshtein, which computes only Levenshtein distance in .NET. Pick SSW when you need affine-gap local alignment with a substitution matrix and a CIGAR from C or C++; EVE or VCL would only give you the vector primitives to write such a kernel yourself.

## Integration

| | |
|---|---|
| **Form** | source-drop (ssw.c + ssw.h, optional ssw_cpp.cpp/ssw_cpp.h); the Makefile also builds libssw.so, and Debian packages it as libssw |
| **Dependencies** | none for the library (emmintrin.h, or the bundled sse2neon.h when __ARM_NEON is defined); ssw_test needs zlib |
| **Minimum toolchain** | C99 (ssw.c declares variables in for loops); the C++ wrapper uses only C++98 features (std::vector, std::string, ostringstream) |
| **Platforms** | x86-64 with SSE2; ARM/aarch64 with NEON through sse2neon.h |
| **Thread safety** | Not documented for the C API; ssw.c holds no mutable global state (only the const encoded_ops table) and ssw_align takes a const profile, so separate calls look reentrant. The README calls the Java Aligner thread-safe. Issue #66 (core dumps under std::async) was attributed to caller misuse but its backtrace pointed into banded_sw and no root cause was confirmed. |
| **Drop-in for the baseline** | no |

## Gotchas

- Gap cost convention: a gap of length L costs gapO + (L - 1) x gapE (the README says the gap open penalty alone is applied on opening, and cigar_alignment_score in ssw.c uses that formula), unlike tools that charge open + extend for the first base; convert penalties before comparing scores with other aligners.
- ssw_init keeps the read and matrix pointers without copying them, so both must outlive the profile; with score_size 0 a score that reaches 255 makes ssw_align print a message and return NULL; the library also writes warnings to stderr (maskLen &lt; 15, partial traceback), and score2 is heuristic (column maxima outside a masked window) and only returned when maskLen &gt;= 15.
- Code reading: banded_sw sizes its traceback buffer with the int32 product width_d \* readLen \* 3, which overflows once (2 x band + 1) x query length passes about 7.2e8 (a 110 kb query with a band over about 3,240), consistent with but not proven as the cause of open segfault #90; with the full-band retry added for issue #93 the buffer becomes about 3 x (2 x length) x length bytes, roughly 5.4 GB for two 30 kb sequences.
- The lazy-F loop is 'revised to disallow adjacent insertion and then deletion' (ssw.c comment), and the __m128i work buffers come from plain malloc/calloc but are read with aligned _mm_load_si128, which relies on the allocator returning 16-byte-aligned blocks (true for glibc x86-64 and macOS, not guaranteed on every 32-bit platform or custom allocator).

## Known shortcomings

- The "about 50x vs ordinary SW" claim is first-party with no method and the E. coli CPU times have no baseline column; the PLoS ONE paper (blocked) compares against SSEARCH 36.3.5c and Farrar, not plain Smith-Waterman; loose category fit.
- No ordinary-SW baseline exists in the repo behind the '\~50x'. The README CPU times come from ssw_test, whose timed clock() loop re-opens and re-parses the whole reference FASTA once per read, and the README is silent on -c; the default-penalty run is about 2x slower, likely because 200 bp reads score above 253, overflow the 8-bit kernel and force a full 16-bit re-scan. Code reading: banded_sw sizes its buffer with the int32 product width_d \* readLen \* 3, so overflow is possible on long queries (fits open #90, a segfault on a 110,456 bp contig, cause unproven); open #94 (silent 32767 saturation) and #96 (stop-codon matrix scoring); #93 CIGAR/score mismatch fixed 2025-11-17. Paper not opened (doi.org and doaj.org blocked).

## Caveats and trade-offs

The '\~50 times' headline names no comparison program, data, compiler, flags or hardware, and the README's E. coli CPU-time figures have no baseline column. The PLoS ONE 2013 paper (doi 10.1371/journal.pone.0082138; arXiv 1208.6350) could not be opened here (doi.org, journals.plos.org, PMC and arXiv blocked); per search snippets only, it benchmarks SSW single-threaded on a 2 GHz x86-64 AMD machine against Farrar's striped SW and SSEARCH 36.3.5c and finds SSW fastest or equally fast on protein database search, with no quoted multiple and no ordinary (non-SIMD) SW baseline seen. The abstract says MOSAIK, SCISSORS, TANGRAM and RZMBLR got faster after swapping their ordinary or banded SW module for SSW. It is a SIMD application library (sequence alignment) rather than a general SIMD intrinsics library. The LICENSE.txt (MIT) file was only added on 2026-01-15; earlier releases carried the licence in source headers.

C API with a C++ wrapper (also Python, Java and R wrappers); integer penalties only, small penalty values recommended for shorter run time; returns score, location and CIGAR for the optimal alignment and heuristic sub-optimal score. Uses SIMD instructions (the README page does not name the instruction set).

## Maintenance

Active (a 'cigar fixed' commit on 2025-11-17 and an MIT LICENSE.txt on 2026-01-15) and small enough to vendor, but the README speed figures are weak evidence: no ordinary-SW baseline exists in the repo, the README does not say whether -c (CIGAR) was on, the timed ssw_test loop re-opens and re-parses the whole reference FASTA for every read, and the default-penalty run is about 2x slower apparently because a 200 bp read scoring above 253 overflows the 8-bit kernel and forces a full 16-bit re-scan; open issues #94 (silent 32767 saturation), #96 (stop-codon scoring) and #90 (segfault on a 110 kb contig) remain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README carries a first-party '\~50 times faster than an ordinary Smith-Waterman' sentence with no comparison program, data, compiler, flags or CPU model, and its E. coli CPU-time figures (AMD \~880 s / \~460 s, Intel \~960 s / \~500 s, \~40 MB) have no baseline column. The PLoS ONE 2013 paper is peer-reviewed but could not be opened (doi.org, journals.plos.org, PMC and ar5iv all blocked or unresolvable); search snippets say it compares SSW with SSEARCH 36.3.5c and Farrar's striped SW, not with an ordinary scalar SW, so it cannot lift the tier from here.
- **Verifier notes:** README numbers match the record; metadata checked on github.com (MIT LICENSE.txt, 323 stars, 119 forks, last commit 2026-01-15 'added LICENSE.txt file', not archived or a fork). Kept at C: the 50x claim is first-party with no methodology and the paper's own comparison is against SIMD incumbents (SSEARCH, Farrar), not the record's ordinary-SW baseline; a paper-access retier could move it to B against SSEARCH if Figure 2 is read. Category fit is loose (bioinformatics alignment library using SSE2/NEON via sse2neon).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/README.md>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/LICENSE.txt>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/README.md>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/src/ssw.h>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/src/ssw.c>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/src/ssw_cpp.h>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/src/ssw_cpp.cpp>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/mengyao/Complete-Striped-Smith-Waterman-Library/HEAD/LICENSE.txt>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/commits/master>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/issues?q=is%3Aissue>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/issues/93>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/issues/94>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/issues/96>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/issues/66>
  - <https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library/issues/90>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mengyao/complete-striped-smith-waterman-library`) · [data/wave13/enrich/raw/github_com_mengyao_complete_striped_smith_waterman_library.json](../../../data/wave13/enrich/raw/github_com_mengyao_complete_striped_smith_waterman_library.json) (enrichment confidence 0.75)

</details>
