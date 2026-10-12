# hwc (Haskell wc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Haskell` · `BSD-3-Clause` · 🔴 abandoned

> Single-threaded Haskell wc (GHC LLVM backend, mmap input) that claims 4-6x over GNU coreutils wc, using ASCII-only word and width rules.

| | |
|---|---|
| **Beats** | GNU coreutils wc (C, single-threaded) |
| **Claimed result** | README: 'about 4-6 times faster than GNU coreutils' wc, depending on the exact subset of statistics being computed' (single-threaded Haskell vs single-threaded C). No per-run timings in the repository README. |
| **Workload** | wc-style counting of bytes, words, lines, UTF-8 characters and maximum line length; only the requested statistics are computed. |
| **Metric** | throughput |
| **Compiler and flags** | stack.yaml resolver lts-15.2 (GHC 8.8 series, bytestring 0.10.10.0) with package.yaml ghc-options -fllvm -O2 -Wall and executable RTS option -with-rtsopts=-A2m; LLVM version not stated. GNU wc version, build flags and the locale it ran in are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: statistics are computed in a composable, efficient manner so that only the ones the user requests are calculated; the implementation write-up (0xd34df00d.me blog post, derived from Chris Penner's wc post) was not opened (host blocked). |
| **Adoption** | 21 stars, 3 forks |
| **Last commit** | 2020-03-15 |
| **Links** | [repository](https://github.com/0xd34df00d/hwc) · [benchmark](https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/README.md) |

## Verdict

The only evidence is the README sentence 'about 4-6 times faster than GNU coreutils' wc, depending on the exact subset of statistics being computed', single-threaded against single-threaded. It refers to a build with GHC 8.8 (lts-15.2) -fllvm -O2 and RTS -A2m against an early-2020 GNU wc. The repository publishes no timings, input file, hardware, locale or wc version, and the author's blog post and Habr article could not be reached from here.

## Use it when

- Counting lines, words and bytes of large ASCII or UTF-8 files when splitting words on ASCII whitespace is acceptable and the output format does not matter.
- Hosts stuck on coreutils 8.x, where wc -w and -m in a UTF-8 locale go through the slow mbrtowc path.
- As a reference for composing several strict folds into one specialised loop in Haskell (GADTs, closed type families, Template Haskell dispatch).
- As the single-threaded counterpart to Chris Penner's parallel Haskell wc, when comparing per-core throughput.

## Skip it when

- As a drop-in wc in scripts. It prints one 'N bytes' style line per statistic with no file name or total, has no --files0-from, and the binary is named hwc-exe.
- Text with Unicode whitespace, East Asian wide characters or combining marks. Words split only on ASCII whitespace, and -L counts every byte from 32 up, including UTF-8 continuation bytes, as one column ('привет' gives 12, not 6).
- Any -L run on input that can contain backspace characters (see gotchas).
- Against current coreutils. 9.0 made wc -l up to 5x faster with AVX2, 9.5 made wc 'much faster in single-byte locales', and 9.11 sped up -m on non-ASCII UTF-8 by 2.6x and -l on Neon by 4.5x. The 2020 ratio has not been re-measured against any of these.
- Projects that need a maintained toolchain. It is pinned to Stackage lts-15.2 (GHC 8.8 series) with the LLVM backend, has no releases and is not on Hackage.

## How it is fast

Each statistic is a strict per-byte fold step over Word64 state. Characters are counted as bytes that are not UTF-8 continuation bytes, using bit arithmetic, and words as transitions into one of six ASCII whitespace codes. Requested statistics combine at the type level, so GHC compiles one fused BS.foldl' loop per subset, built with -fllvm -O2. Regular files are mmapped through bytestring-mmap, which keeps the data off the GC heap; issue #1 shows a run allocating 80,552 bytes in total. Part of the gap is doing less work: GNU wc 8.32 in a UTF-8 locale calls mbrtowc, iswprint and iswspace for every non-ASCII character (and wcwidth for -L), and hwc does none of that.

## Compared with alternatives

Pick hwc only to study a single-threaded, type-level composable wc in Haskell. For a faster wc to actually use, cw (Rust) publishes per-flag hyperfine ratios against GNU wc 8.30 on a named 341 MB file, and Chris Penner's Haskell wc shows that its own single-core version loses to BSD wc, so its only win is parallelism.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | base, bytestring, bytestring-mmap 0.2.2 (extra-dep), optparse-applicative, template-haskell, unix; an LLVM toolchain for -fllvm |
| **Minimum toolchain** | Stack resolver lts-15.2 (GHC 8.8 series) with an LLVM version supported by that GHC (not stated in the repo) |
| **Platforms** | POSIX only: it uses the unix package and mmap through bytestring-mmap; CPU architectures not documented |
| **Thread safety** | The library functions are pure over an immutable ByteString. The CLI is single-threaded and uses unsafeMMapFile, so a file changed or truncated while being counted gives undefined results (general mmap behaviour, not documented by the project). |
| **Drop-in for the baseline** | partial — same short and long flags as GNU wc, but a different output format (one line per statistic, no file name, no total), no --files0-from, and ASCII-only word and width rules |

## Gotchas

- Max-line-length underflow bug. The backspace rule `step MaxLLState {..} 8 = MaxLLState maxLen $ max 0 (curLen - 1)` (commit 'Handle backspace symbols in max line length', 2020-02-29) works on Word64, so at column 0 the subtraction wraps and max 0 does not clamp it. A backspace followed by a line end or end of file makes -L report 18446744073709551615, and '\babc' reports 2. GNU wc 8.32 ignores the non-printable backspace and reports 3. This was checked by simulating the exact step with 64-bit wraparound; hwc itself was not run, since no GHC is available here.
- Semantics differ from GNU wc. -m counts non-continuation bytes in every locale and does no UTF-8 validation (GNU 8.32 counts bytes in the C locale and skips invalid bytes in UTF-8 locales). -w splits on bytes 9-13 and 32 only, while GNU in a UTF-8 locale also splits on iswspace characters and no-break spaces, and before 9.5 GNU did not let non-printable characters start a word. The test suite checks words against Haskell's `words` after replacing non-ASCII spaces with '_', and has no -L test.
- Some subsets are not Haskell code wins. -l alone runs bytestring 0.10.10.0's fps_count, a plain C byte loop. -c alone is the mmapped length, while GNU wc also takes the size from fstat, so neither can show a codegen advantage.
- The claim has no methodology and the baseline has moved. The README gives one ratio sentence with no file, timings, hardware, locale or coreutils version (early 2020, so 8.31 or 8.32). A third-party Habr reply (search snippet only, per the record) measured a hand-written single-threaded C wc at 0.637 s against 2.811 s for a simple Haskell version on a 1.8 GB file.

## Known shortcomings

- README ratio only ('4-6x') with no method; does less work than GNU wc (ASCII words, no UTF-8 decode, -L wrong on multibyte); the -l path is the bytestring C helper fps_count; a Habr snippet shows hand-written C (0.637 s) beating the Haskell version.
- Correctness bug in -L: the backspace rule max 0 (curLen - 1) on Word64 underflows, so a backspace followed by a line end or EOF reports 18446744073709551615 and '\babc' gives 2 where GNU wc 8.32 gives 3 (simulated in Python; no GHC here). The output format is not wc's, word and width rules are ASCII-only, -l alone runs bytestring's C fps_count loop and -c alone is O(1), as in GNU. The baseline is stale: coreutils 9.0 made -l up to 5x faster with AVX2, 9.5 calls wc much faster, and 9.11 sped up -m 2.6x on non-ASCII UTF-8. No methodology in the README.

## Caveats and trade-offs

Numbers are a single ratio sentence in the README with no hardware, file size, GNU wc version, locale or timing method; the author's Habr article ('Побеждая C двадцатью строками Haskell: пишем свой wc', Feb 2020) and blog post could not be opened (hosts do not resolve here). hwc does less work than GNU wc: src/Data/WordCount.hs splits words on ASCII whitespace only (bytes 9-13 and 32), counts characters as non-continuation bytes without UTF-8 validation, and counts every byte &gt;= 32 as one column for max line length (no display-width handling, so -L is wrong for multibyte text), whereas GNU wc in a UTF-8 locale decodes multibyte characters. The line count is Data.ByteString.count, which in bytestring 0.10.10.0 calls the C helper c_count (fps_count), so the -l path is C code; input is mmapped via bytestring-mmap. Habr search snippets (snippet only) describe a third-party response that measured, on a 1.8 GB file, system wc 19.416 s, a simple Haskell version 2.811 s, a simple C version 3.067 s and an optimized hand-written single-threaded C version 0.637 s, so the gap is to GNU wc's general implementation, not to C; a Habr commenter also notes the simplified spec (Unicode ignored). Measured against a 2020 coreutils; later coreutils releases (which reworked wc's line counting) were not compared. Abandoned since March 2020. [retier] Numbers are a single ratio sentence in the README with no hardware, file size, GNU wc version, locale or timing method; the author's Habr article and blog post could not be opened. hwc does less work than GNU wc: ASCII-only whitespace for words, characters counted as non-continuation bytes without UTF-8 validation, output format not wc's. Correctness bug in -L: the backspace rule max 0 (curLen - 1) on Word64 underflows, so a backspace followed by a line end or EOF reports 18446744073709551615 and '\babc' gives 2 where GNU wc 8.32 gives 3 (simulated in Python; hwc not run here). -l alone runs bytestring's C fps_count loop and -c alone is O(1), as in GNU. The baseline is stale: coreutils 9.0 made -l up to 5x faster with AVX2, 9.5 calls wc much faster, and 9.11 sped up -m 2.6x on non-ASCII UTF-8. Pinned to GHC 8.8 with the LLVM backend; abandoned since 2020-03-15.

Depends on the GHC LLVM backend and bytestring-mmap; abandoned since 2020; counts UTF-8 characters only.

## Maintenance

Abandoned since 2020-03-15 (61 commits, no releases, one closed issue). It is BSD-3-Clause and small enough to read or vendor, but pinned to GHC 8.8 with the LLVM backend, and -L has a Word64 underflow bug on backspace input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives only a first-party ratio ('about 4-6 times faster than GNU coreutils' wc') with no timings, file, hardware, GNU wc version, locale or benchmark script; the author's write-ups (0xd34df00d.me post, Habr article) do not resolve from here, so no methodology could be checked.
- **Verifier notes:** Confirm at C; README ratio matches the record. Shortcomings: ratio-only claim with no methodology, reduced work versus GNU wc (ASCII-only words and line width, no UTF-8 validation), the -l path is bytestring's C code, and a third-party hand-written C wc was faster (snippet only); same_algorithm set to false. Not a language-level win.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/README.md>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/package.yaml>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/stack.yaml>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/src/Data/WordCount.hs>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/app/Main.hs>
  - <https://raw.githubusercontent.com/haskell/bytestring/0.10.10.0/Data/ByteString.hs>
  - <https://github.com/0xd34df00d/hwc>
  - <https://github.com/0xd34df00d/hwc/commits>
  - <https://github.com/0xd34df00d/hwc/tree/master/src/Data>
- **Sources the enricher read:**
  - <https://github.com/0xd34df00d/hwc>
  - <https://github.com/0xd34df00d/hwc/commits/master>
  - <https://github.com/0xd34df00d/hwc/issues?q=is%3Aissue>
  - <https://github.com/0xd34df00d/hwc/issues/1>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/README.md>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/package.yaml>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/stack.yaml>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/src/Data/WordCount.hs>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/src/Data/Dispatch.hs>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/app/Main.hs>
  - <https://raw.githubusercontent.com/0xd34df00d/hwc/HEAD/test/Spec.hs>
  - <https://raw.githubusercontent.com/haskell/bytestring/0.10.10.0/Data/ByteString.hs>
  - <https://raw.githubusercontent.com/haskell/bytestring/0.10.10.0/cbits/fpstring.c>
  - <https://raw.githubusercontent.com/coreutils/coreutils/v8.32/src/wc.c>
  - <https://raw.githubusercontent.com/coreutils/coreutils/master/NEWS>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/0xd34df00d/hwc`) · [data/wave14/enrich/raw/github_com_0xd34df00d_hwc.json](../../../data/wave14/enrich/raw/github_com_0xd34df00d_hwc.json) (enrichment confidence 0.7)

</details>
