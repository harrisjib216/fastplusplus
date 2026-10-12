# Discount

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [HTML, Markdown and markup](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> C Markdown-to-HTML library and CLI implementing original Markdown.pl syntax; converts orders of magnitude faster than Markdown.pl.

| | |
|---|---|
| **Beats** | Markdown.pl |
| **Claimed result** | discount 1.86 s vs Markdown.pl 2921.24 s (about 1570x faster, derived from page data); vs peg-markdown 5.45 s (about 2.9x faster, derived from page data); vs Python markdown 291.25 s (about 157x, derived from page data); vs PHP markdown 20.82 s (about 11x, derived from page data). In the same table cmark takes 0.36 s and sundown 0.34 s, both about 5x faster than discount. |
| **Workload** | Convert an 11 MB Markdown file (Pro Git first edition sources concatenated across localizations) to HTML; wall time is the difference between running with the input and with no input, median of ten runs, in the cmark project's benchmark table. |
| **Metric** | throughput |
| **Hardware** | 'ancient Thinkpad running Intel Core 2 Duo at 2GHz' (cmark benchmarks.md) |
| **Adoption** | 891 stars |
| **Last commit** | 2026-08-29 |
| **Links** | [repository](https://github.com/Orc/discount) · [benchmark](https://raw.githubusercontent.com/commonmark/cmark/0.18/benchmarks.md) |

## Verdict

The cmark project's benchmarks.md (tag 0.18) timed conversion of an 11 MB concatenation of Pro Git first-edition Markdown sources on an unnamed Core 2 Duo 2 GHz laptop (median of ten runs of wall time with input minus without input): Discount 1.86 s against Markdown.pl 2921.24 s, Python-Markdown 291.25 s, PHP Markdown 20.82 s and peg-markdown 5.45 s; Discount's version, compiler and flags are not stated, and the run used a 2014-15 era Discount, not today's 3.0.2.0.

## Use it when

- You need Markdown.pl-compatible output (original Gruber syntax, MKD_STRICT available) from C or C++ and Markdown.pl itself is too slow.
- You want Discount's specific extensions in one library: pandoc-style title/author/date headers, generated table of contents, PHP-Markdown-Extra footnotes and definition lists, SmartyPants, div quotes, image size suffixes.
- Batch or server-side rendering of many documents where a scripting-language Markdown (Python-Markdown, PHP Markdown, kramdown) is the bottleneck.
- Small dependency-free C build that runs on Unix-likes, macOS and Plan 9 (configure.sh plus make, no third-party libraries).

## Skip it when

- You need CommonMark or GFM conformance: Discount makes no CommonMark claim and its output differs from cmark/md4c on edge cases.
- Raw speed among C parsers: in the same cmark table hoedown (0.21 s), cmark (0.29-0.36 s) and sundown (0.34 s) are 5-9x faster than Discount (1.85-1.86 s); even commonmark.js (1.93-2.09 s) and marked (1.94-1.99 s) are within about 10%.
- Untrusted input in a hardened service without fuzzing of your own: the tracker shows a long run of ASan finds (heap overflows #189, #277, #280; use-after-free #281; stack overflow #239), an open uninitialized-memory report against 3.0.1 extended attributes (#298), and deep-nesting stack exhaustion (#305) only addressed by the recursion cap added in 3.0.2.0.
- You need byte-identical, deterministic output: e-mail autolinks are obfuscated with random() entity encoding unless the library is configured with --debian-glitch.
- Code written against the 2.x API: 3.x replaced the integer flag bitmask with an opaque mkd_flag_t blob and #defines mkd_in, markdown and friends to mkd3_\* variants.

## How it is fast

No regular expressions: input is split once into a linked list of Line records with the leading indent precomputed, block structure is built by hand-written line classifiers (islist, ishdr, iscode, isfootnote and so on in markdown.c), and inline markup is a single-pass byte scanner (peek/pull over an in-memory buffer) with an emphasis block queue resolved afterwards. Reference links and footnotes are sorted with qsort once and found with bsearch; block-level HTML tags are a pre-sorted table searched with bsearch. This is ordinary compiled-C parsing, which is why it beats regex-substitution implementations such as Markdown.pl and Python-Markdown by large factors but not other C parsers.

## Compared with alternatives

Pick Discount over Hoedown or MD4C only when you need original Markdown.pl semantics or Discount's particular extensions (pandoc headers, TOC, Extra-style footnotes and definition lists); for pure speed Hoedown was about 8.8x faster in the same cmark table, and MD4C is the faster choice if CommonMark/GFM conformance is wanted.

## Integration

| | |
|---|---|
| **Form** | static lib (shared with configure.sh --shared) plus CLI tools |
| **Dependencies** | none (libc only) |
| **Minimum toolchain** | C compiler and POSIX shell for configure.sh; no language standard stated (not documented) |
| **Platforms** | Unix-like systems, macOS, NetBSD, Plan 9/9Front per INSTALL notes; Windows not documented |
| **Thread safety** | not documented; per-document state lives in the MMIOT/Document, but mkd_initialize() seeds the global random() generator through an unsynchronized static flag and e-mail mangling calls random() |
| **Drop-in for the baseline** | partial — the markdown CLI reads a file and writes HTML like Markdown.pl and MKD_STRICT targets Markdown.pl behaviour, but default output enables Discount extensions (SmartyPants, tables, etc.) and it is a C library, not a Perl module |

## Gotchas

- Benchmark harness: cmark's 'make bench' runs 'sudo renice 99 \$\$', which sets the lowest scheduling priority (nice is clamped to 19), while benchmarks.md says the process was 'reniced to a high priority'; on a busy machine every timing, including Markdown.pl's 2921 s run, is exposed to background load. The 2921.24 s figure is also identical in every table from 0.13 to 0.29.0, so it was not re-run beside each Discount number.
- The 1570x ratio is for one 11 MB concatenated document; no per-file or typical-page-size timings exist, so do not expect that factor on small inputs.
- C++ callers must build with configure.sh --cxx-binding (or wrap the include themselves) to get extern "C" in mkdio.h.
- String buffers grow by a fixed 100 elements per realloc (EXPAND/RESERVE in cstring.h) and output is appended a character at a time (Qchar), so throughput on very large documents depends on the allocator resizing in place (code reading, not measured).

## Known shortcomings

- Tier B on the cmark 0.18 benchmark table (1.86 s vs Markdown.pl 2921.24 s) but the baseline is weak and sundown, cmark and hoedown are about 5x faster; Core 2 Duo, no version or flags; the Markdown.pl figure is identical in every table, so it was measured once and never re-run. Discount stays in the table through cmark 0.29.0 (1.85 s) and was dropped at 0.30.0. BSD-3-Clause-style licence.
- Enricher: the cmark 0.18 Makefile bench runs 'sudo renice 99 \$\$', which sets the lowest priority (nice 19) although benchmarks.md says 'reniced to a high priority'; the Markdown.pl 2921.24 s figure is identical from 0.13 to 0.29.0, so it was never re-run; the 1570x comes from one 11 MB document with no per-page numbers (ratios stand). ASan history (#189, #277, #280, #281, #239); #298 uninitialized memory in 3.0.1 extended attributes still open; #305 stack exhaustion still open (recursion cap 200 added in 3.0.2.0); random() email mangling makes output nondeterministic unless --debian-glitch; 3.x flag API break; C++ needs --cxx-binding; Cstring buffers grow by 100 elements per realloc (code reading).

## Caveats and trade-offs

The numbers come from the cmark project's own benchmarks.md (tag 0.18), measured on an old Core 2 Duo laptop, not from Discount's repo, which has no benchmark. Discount version, compiler and flags are not stated; the benchmark driver is the public 'make bench' target in the cmark Makefile (time -p with and without input, median of ten runs) and the input is built from the public progit/progit repository. The cmark 0.13 table gave discount 1.705 s on the same input; Discount stayed in the table (1.85 s) through cmark 0.29.0 and was dropped at 0.30.0, when the table was re-run on an i9 MacBook Pro with only commonmark.js, cmark and md4c. The Markdown.pl figure (2921.24 s) is identical in every table from 0.13 to 0.29.0, so it was apparently measured once and carried over rather than re-run beside each Discount timing. Markdown.pl is a regex-based Perl reference implementation, so beating it is a weak result; Discount is not the fastest C Markdown library (sundown 0.34 s and cmark 0.36 s are about 5x faster in the same table, and hoedown 0.21 s in later tables). The measured Discount is a 2014-era release; the repo is now at 3.0.2.0. [retier] cmark 0.18 table: Discount 1.86 s vs Markdown.pl 2921.24 s on one 11 MB document (weak baseline, measured once and copied through 0.29.0); sundown, cmark and hoedown about 5x faster; Core 2 Duo, no versions or flags; the Makefile bench renices to nice 19 (lowest), not high priority. Open #298 uninitialized memory and #305 stack exhaustion; random() email mangling nondeterministic unless --debian-glitch; 3.x API break; C++ needs --cxx-binding.

Implements the original Markdown syntax (README: passes MarkdownTest_1.0, no CommonMark conformance claim) plus extensions; C library with command-line tools. Faster than scripting-language Markdown implementations but about 5x slower than cmark and sundown on the same input.

## Maintenance

Actively maintained by a single author (last commit 2026-08-29, version 3.0.2.0 adding a configurable recursion cap of 200), BSD-3-Clause-style licence and small enough to vendor, but its memory-safety history means untrusted input should be fuzzed or sandboxed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party table from the cmark (CommonMark reference) project's benchmarks.md lists discount 1.86 s vs Markdown.pl 2921.24 s on an 11 MB input with a public 'make bench' driver, but the CPU is only 'Intel Core 2 Duo at 2GHz' (no model) and Discount's version, compiler and flags are unstated, so it falls short of A.
- **Verifier notes:** Numbers match cmark 0.18 benchmarks.md exactly; corrected the caveat that later cmark releases dropped Discount (it stays through 0.29.0 at 1.85 s). Shortcomings: weak baseline (Markdown.pl), about 5x slower than sundown/cmark/hoedown in the same table, old unnamed Core 2 Duo, no compiler/flags/version, Markdown.pl number carried over across releases. Metadata (BSD-3-Clause-style COPYRIGHT with 'Neither my name' clause, 891 stars, last commit 2026-08-29) confirmed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/commonmark/cmark/0.18/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.13/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.19.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.30.0/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/master/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.18/Makefile>
  - <https://github.com/Orc/discount>
  - <https://github.com/Orc/discount/commits>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/COPYRIGHT>
- **Sources the enricher read:**
  - <https://github.com/Orc/discount>
  - <https://github.com/Orc/discount/commits>
  - <https://github.com/Orc/discount/issues?q=is%3Aissue+overflow+OR+crash+OR+CVE+OR+segfault>
  - <https://github.com/Orc/discount/issues/305>
  - <https://github.com/Orc/discount/issues/298>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/README>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/COPYRIGHT>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/VERSION>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/INSTALL>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/configure.sh>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/mkdio.h.in>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/markdown.h>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/markdown.c>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/generate.c>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/setup.c>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/tags.c>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/cstring.h>
  - <https://raw.githubusercontent.com/Orc/discount/HEAD/Csio.c>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.18/benchmarks.md>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.18/Makefile>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.18/bench/stats.py>
  - <https://raw.githubusercontent.com/commonmark/cmark/0.29.0/benchmarks.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/orc/discount`) · [data/wave1/enrich/raw/github_com_orc_discount.json](../../../data/wave1/enrich/raw/github_com_orc_discount.json) (enrichment confidence 0.8)

</details>
