# Hoedown

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `ISC` · 🔴 abandoned

> Callback-driven C Markdown-to-HTML library (Sundown fork); edged out cmark 0.21 s vs 0.29 s in cmark's own 2015-era benchmark.

| | |
|---|---|
| **Beats** | cmark (CommonMark reference implementation) |
| **Claimed result** | cmark benchmarks.md (tags 0.21.0 to 0.29.0): hoedown 0.21 s vs cmark 0.29 s (\~1.4x, derived from page data) and vs discount 1.85 s (\~8.8x, derived from page data) on the same table; at tag 0.20.0 the table read hoedown 0.21 s vs cmark 0.35 s. why-cmark-and-not-x.md repeats 'slightly faster than cmark in our benchmarks (0.21s vs. 0.29s)'. |
| **Workload** | Markdown to HTML conversion of an 11 MB file built by concatenating all localizations of the first edition of Pro Git, timed by cmark's 'make bench PROG=...' target with time -p (time with empty input subtracted to remove startup, median of ten runs, process reniced). |
| **Metric** | throughput |
| **Hardware** | ancient Thinkpad, Intel Core 2 Duo at 2GHz (exact model not stated) |
| **Adoption** | 995 stars |
| **Last commit** | 2015-12-07 |
| **Links** | [repository](https://github.com/hoedown/hoedown) · [benchmark](https://github.com/commonmark/cmark/blob/0.29.0/benchmarks.md) |

## Verdict

cmark's benchmarks.md (tags 0.21.0 to 0.29.0) times each CLI on an 11 MB concatenation of all Pro Git first-edition translations on a 2 GHz Core 2 Duo laptop with time -p (0.01 s resolution), subtracting an empty-input run and taking the median of 10: hoedown 0.21 s vs cmark 0.29 s (about 1.4x, derived from page data) and discount 1.85 s. No compiler, flags or hoedown version are given, the hoedown binary presumably ran with its CLI defaults (no extensions, max nesting 16), and the two programs implement different Markdown dialects, so the outputs being timed are not the same.

## Use it when

- Rendering trusted Markdown (your own docs or sites) in C or C++ where throughput matters and CommonMark conformance does not.
- Keeping output compatible with existing Sundown or Redcarpet-family renderers and their extension set.
- Custom output formats or streaming HTML with low memory, using the renderer callback struct instead of walking an AST.
- Dependency-free embedding under ISC on GCC, Clang or MSVC (Makefile.win provided).

## Skip it when

- When CommonMark or GFM conformance is required: it targets the Markdown 1.0.x test suites, CommonMark support was never added (issue #119 open), and cmark's why-cmark-and-not-x.md lists list-nesting, heading, reference and title-escaping bugs as of v3.0.3.
- Untrusted input on a server: 50,000 nested brackets took 17.84 s (cmark 0.073 s), and 160,000 reference definitions with 10,000 references took 8.78 s (open issue #223); out-of-memory calls abort().
- Pages that need link sanitizing: the HTML renderer percent-escapes hrefs but does not filter schemes, so javascript: links pass through even with HOEDOWN_HTML_ESCAPE.
- Non-ASCII text that relies on Unicode case folding or punctuation: reference labels are folded with byte-wise tolower and non-ASCII punctuation and whitespace count as word characters.
- Projects that need a maintained dependency: last commit 2015-12-07 (version 3.0.7).

## How it is fast

There is no AST: a first pass strips reference definitions into a small hash table and expands tabs into one buffer, then a recursive-descent block parser calls renderer callbacks that append straight to the output buffer. Inline parsing copies runs of ordinary bytes in bulk and dispatches only on 'active' characters through a 256-entry lookup table into a function-pointer array. Temporary buffers come from per-document pooled stacks reused across nesting levels, and the output buffer is pre-grown to 1.5x the input, so allocation is rare; the Makefile builds with -O3.

## Compared with alternatives

MD4C is the catalogued Markdown sibling: it is CommonMark-compliant, still maintained and itself measured 1.4-7.7x faster than cmark, so prefer it by default; pick hoedown only to keep Sundown/Redcarpet-style output or its bundled SmartyPants and TOC renderer on trusted input.

## Integration

| | |
|---|---|
| **Form** | source-drop (9 .c files in src/; make also builds libhoedown.a and libhoedown.so) |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | C99 per README (the Makefile compiles with -O3 -ansi -pedantic); MSVC via Makefile.win, with buffer.h stubbing __attribute__ and __builtin_expect |
| **Platforms** | any; no architecture-specific code |
| **Thread safety** | Not documented. Parse state (reference table, work-buffer pools) lives in the hoedown_document and TOC state in the renderer, so use one document and renderer per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Reference links are matched by a 32-bit sdbm-style hash only: struct link_ref stores no label and find_link_ref returns the first entry whose hash matches, so two different labels with equal hashes resolve to the same URL, and a reference to an undefined label can silently link to another definition. Computing the same hash in Python found colliding 10-character labels ('f3yy839674' and 'bpnm1bsoj2') after about 150,000 random tries (hash computed, not run through hoedown). Footnotes use the same hash-only id.
- The reference table has only 8 buckets (REF_TABLE_SIZE 8), so lookups degrade to linear chain scans on documents with many references, which is the cause behind the 8.78 s case in issue #223.
- Anything nested deeper than max_nesting (the CLI default is 16) is silently dropped: parse_block and parse_inline return without emitting the text.
- hoedown_buffer grows by a fixed unit (arithmetic, not geometric growth); give large documents a large unit or pre-grow the buffer to avoid repeated reallocs.

## Known shortcomings

- cmark benchmarks.md (tags 0.21.0-0.29.0): hoedown 0.21 s vs cmark 0.29 s vs discount 1.85 s on an 11 MB Pro Git input, Core 2 Duo 2 GHz, public make bench but no compiler or flags; the row was dropped at cmark 0.30.0. Pathological input takes 17.84 s and the parser has known bugs. Abandoned since 2015-12-07.
- Enricher: reference links are matched by a 32-bit sdbm hash only (link_ref stores no label), so colliding labels resolve to the wrong URL (collision pair found: 'f3yy839674'/'bpnm1bsoj2'); REF_TABLE_SIZE 8 explains issue #223 (160,000 refs take 8.78 s); content nested past max_nesting 16 is silently dropped; no javascript: scheme filtering. The cmark bench ran CLI defaults (no extensions), a different dialect from cmark.

## Caveats and trade-offs

Numbers are from the cmark team's benchmark (a competing project), circa 2015 (hoedown 3.x era; the table does not name versions), and were dropped from cmark's benchmarks.md at tag 0.30.0; the current page uses a 1106 KB input on a 2.3GHz 8-core i9 MacBook Pro and lists only commonmark.js, cmark and md4c, and cmark has been optimized since. No compiler or flags for any implementation. hoedown implements original Markdown plus extensions, not CommonMark, so the two produce different output for the same input. why-cmark-and-not-x.md reports hoedown taking 17.84 s on a 50000-deep nested bracket input where cmark took 0.073 s user time, and lists many parsing bugs as of hoedown v3.0.3. The README's own claim ('up to 40 times faster than other native alternatives' when wrapped in Python or Ruby) names no baseline and has no data. Repository dormant since 2015-12-07; fork of vmg/sundown. [retier] cmark benchmarks.md (tags 0.21.0-0.29.0): hoedown 0.21 s vs cmark 0.29 s vs discount 1.85 s on an 11 MB Pro Git input, Core 2 Duo 2 GHz, public make bench, no compiler or flags; the bench ran hoedown's CLI defaults (no extensions), a different dialect from cmark, and the row was dropped at cmark 0.30.0. Pathological input takes 17.84 s. Correctness: reference links are matched by a 32-bit sdbm hash only (link_ref stores no label), so colliding labels resolve to the wrong URL; REF_TABLE_SIZE 8 makes 160,000 references take 8.78 s (issue #223); content nested past max_nesting 16 is silently dropped; no javascript: scheme filtering. Abandoned since 2015-12-07.

Pure C99 library with no dependencies and a separate renderer. Targets the original Markdown 1.0.x test suites, not CommonMark. Does not sanitize HTML unless HTML_ESCAPE or HTML_SKIP is set. Treats non-ASCII punctuation and whitespace as word characters.

## Maintenance

Abandoned since 2015-12-07 at version 3.0.7; ISC-licensed and small enough to vendor, but the hash-only reference matching, the open many-references slowdown (#223) and the lack of URL scheme filtering make it a poor fit for untrusted input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded C to B: cmark's own benchmarks.md (tags 0.21.0 to 0.29.0) lists hoedown 0.21 s vs cmark 0.29 s and discount 1.85 s, measured by the CommonMark team (independent of hoedown, and a competitor reporting a loss) with a public harness (cmark Makefile 'bench' target, bench/stats.py, Pro Git input). Not A: no compiler or flags, CPU given only as 'Intel Core 2 Duo at 2GHz', hoedown version unstated.
- **Verifier notes:** Better source found: cmark benchmarks.md at tags 0.21.0-0.29.0 carries the full table with methodology and a direct discount row (no chaining needed), so tier raised to B as an independent measurement; benchmark_url, claimed_speedup, workload, hardware corrected. Metadata verified on github.com: ISC LICENSE, 995 stars, 125 forks, fork of vmg/sundown, last commit 2015-12-07 (abandoned).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Shortcomings recorded by:** cmark benchmarks.md (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/commonmark/cmark/blob/master/why-cmark-and-not-x.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/HEAD/why-cmark-and-not-x.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/HEAD/benchmarks.md>
  - <https://github.com/commonmark/cmark/blob/0.29.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.21.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.20.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.30.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/Makefile>
  - <https://github.com/hoedown/hoedown>
  - <https://github.com/hoedown/hoedown/commits/master.atom>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/README.md>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/README.md>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/Makefile.win>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/document.h>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/document.c>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/html.h>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/html.c>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/buffer.h>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/buffer.c>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/stack.c>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/autolink.c>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/escape.c>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/src/version.h>
  - <https://raw.githubusercontent.com/hoedown/hoedown/HEAD/bin/hoedown.c>
  - <https://github.com/hoedown/hoedown/issues?q=is%3Aissue+crash+OR+overflow+OR+segfault+OR+quadratic+OR+slow>
  - <https://github.com/hoedown/hoedown/issues/223>
  - <https://github.com/hoedown/hoedown/issues/142>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/Makefile>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/bench/stats.py>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/why-cmark-and-not-x.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/HEAD/why-cmark-and-not-x.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/hoedown/hoedown`) · [data/wave3/enrich/raw/github_com_hoedown_hoedown.json](../../../data/wave3/enrich/raw/github_com_hoedown_hoedown.json) (enrichment confidence 0.8)

</details>
