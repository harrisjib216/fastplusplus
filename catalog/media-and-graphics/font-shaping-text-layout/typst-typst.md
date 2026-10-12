# Typst

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust typesetting system (markup language, compiler, CLI) that built mail-merge PDFs 3-5x faster than pdfLaTeX in one shootout.

| | |
|---|---|
| **Beats** | pdfLaTeX (pdfTeX 1.40.24, TeX Live 2022) and LuaLaTeX (LuaHBTeX 1.15.0); the same shootout also ran WeasyPrint 68.1, Apache FOP 2.11 and speedata Publisher 5.3.18 Pro |
| **Claimed result** | speedata benchmark (MacBook Air M4 16 GB, Typst 0.14.2), wall clock: 500 pages Typst 156.6 ms vs pdflatex 712.3 ms (4.55x), LuaLaTeX 2.356 s (15.04x), FOP 1.607 s (10.27x), speedata sp 4.354 s (27.80x), WeasyPrint 8.672 s (55.38x); 1 page: Typst 105.7 ms vs pdflatex 329.1 ms (3.1x, derived), LuaLaTeX 518.6 ms (4.9x, derived); speedata sp fastest at 94.5 ms. The 500-page wall-clock ratio includes Typst's parallel page-run layout against single-threaded pdflatex: total CPU time is 308 vs 716 ms (about 2.3x) and the marginal per-page CPU ratio about 1.9x (derived from page data). |
| **Workload** | Mail-merge letters (logo, sender and recipient blocks, justified hyphenated 105 mm body text) built to PDF from XML, 1 page and 500 pages, timed end to end with hyperfine (--warmup 3 for 1 page; --warmup 1 --min-runs 3 for 500 pages). The 500-page input (generate_fakenames.py) is 500 identical copies of one record. Typst reads the XML natively (typst compile --input xml=...); pdflatex and lualatex are driven by a Python script that parses the XML, renders a Jinja2 template and runs one engine pass, and that Python start-up and rendering is inside the timing. |
| **Metric** | build-time |
| **Hardware** | MacBook Air M4 (Apple M4), 16 GB RAM, as stated in the README; run by pgundlach (speedata) in February 2026 (3 commits, 2026-02-10 and 2026-02-11). |
| **Compiler and flags** | Not applicable (prebuilt tools); versions are listed in the README (Typst 0.14.2, pdfTeX 3.141592653-2.6-1.40.24, LuaHBTeX 1.15.0, hyperfine 1.17.0, Python 3.14.3). |
| **Adoption** | 56.4k stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/typst/typst) · [benchmark](https://github.com/speedata/typesetting-benchmark) |

## Verdict

speedata's hyperfine runs on a MacBook Air M4 (Typst 0.14.2 against pdfTeX 1.40.24 and LuaHBTeX 1.15.0 from TeX Live 2022) put Typst at 105.7 ms for a one-page letter (3.1x faster than pdflatex, 4.9x than LuaLaTeX, derived from page data) and 156.6 ms for 500 identical letters (4.55x and 15.0x), with the LaTeX times including a Python and Jinja2 templating step. Typst's 500-page run used several cores (pagebreak() between letters enables parallel page-run layout) while pdflatex is single-threaded: on total CPU time (user plus system) the 500-page gap is 308 ms against 716 ms, about 2.3x, and the marginal cost per extra page is about 1.9x lower (both derived from page data), so roughly half of the 4.55x wall-clock win comes from parallelism and lower start-up. Zerodha's production report (blog blocked, search snippet only) gives about 3-4x faster than LaTeX overall and about 1 min against about 18 min with lualatex for 2000+ page table documents.

## Use it when

- Batch generation of many similar documents from structured data (letters, invoices, contract notes) where templates can be written in Typst: the speedata shootout and Zerodha's contract-note pipeline (search snippet) both report several-fold speedups over LaTeX.
- Interactive or watch-mode editing of long documents, where memoized relayout recompiles only what changed.
- Multi-page output on multi-core machines: page runs separated by explicit page breaks are laid out in parallel (tune with --jobs).
- Containers and CI where a single static binary is simpler than a TeX Live installation.

## Skip it when

- Existing LaTeX documents, classes or journal templates: there is no TeX compatibility, so every template must be ported and many CTAN packages have no Typst equivalent.
- When you need a stable performance profile across upgrades: open regressions include #7102 (10,000 identical list items: about 200 ms on 0.13, 1.5 s on 0.14-rc1) and #8611 (a 300-page document with a glossary: 1 min 17 s and 32 GB on 0.14.2, 14 min and 41 GB on 0.15.0), and, per the verifier's notes, texlode/luatex-benchmark measured 0.14+ incremental edits 1.6-2.2x slower than 0.12/0.13 on x86.
- Table-heavy or introspection-heavy documents without testing first: #4560 (slow PDF compilation with many tables) is open, and memory can grow very large (#8611 reports 32-41 GB; #3150 and #8628 request limits and graceful out-of-memory handling).
- Hosts with very many installed fonts: the CLI scans every system font file at start-up (#8561 reports about 50 s on one Linux machine); use --ignore-system-fonts with --font-path.
- C or C++ embedding: there is no C API; drive the CLI as a subprocess or write a Rust wrapper.

## How it is fast

Incremental compilation through comemo, constrained memoization: layout and evaluation functions are #[comemo::memoize]d over Tracked inputs that record which parts of the World or introspector a call actually read, so a cached result is reused whenever those parts are unchanged, across edits in watch mode and across identical content within one run. Since 0.12 the layout engine splits the document at explicit page breaks into page runs and lays them out in parallel (engine.parallelize over Item::Run in typst-layout pages/mod.rs; changelog: 'typical speedups are 2-3x for larger documents'). Justified paragraphs use Knuth-Plass optimal line breaking with a two-pass scheme: a cheap pass with approximate metrics yields an upper bound on cost that prunes the exact pass (linebreak_optimized_approximate then linebreak_optimized_bounded). Hyphenation comes from hypher's embedded automata, and the CLI is one native binary with no format files to load: the whole one-page benchmark compile took 105.7 ms.

## Compared with alternatives

It is the only full typesetting system in this category: pick it when you need finished paged PDFs from markup or data, and pick Parley (rich-text layout) or hypher (hyphenation only, which Typst itself uses) when you are building your own layout or rendering stack.

## Integration

| | |
|---|---|
| **Form** | CLI binary (typst-cli) or Rust crate (typst plus typst-layout, typst-pdf and related workspace crates) |
| **Dependencies** | Pure Rust; notable crates include comemo, rayon, hypher, rustybuzz, ttf-parser, fontdb, icu_segmenter/icu_properties, wasmi for plugins and krilla (pinned git revision) for PDF export |
| **Minimum toolchain** | Rust 1.92 (workspace rust-version for 0.15.x; 0.14.2 required 1.89) |
| **Platforms** | Any platform Rust targets; the speedata numbers are from macOS on Apple M4 |
| **Thread safety** | Compiler is internally multithreaded (layout, plugins); since 0.12 World implementations must be Send + Sync. |
| **Drop-in for the baseline** | no |

## Gotchas

- Parallel layout only kicks in at explicit page breaks (pagebreak() or separate page runs); a single long flowing document gets less benefit.
- Performance is version-sensitive (see the open regression issues), so pin the version you benchmarked; 0.14.0 and 0.14.1 also shipped a wasmi use-after-free fixed in 0.14.2.
- Hyphenation uses hypher, which ignores the TeX \hyphenation{} exception lists, so line breaks can differ from LaTeX on exception words.
- Tagged (accessible) PDF output arrived in 0.14; the --no-pdf-tags opt-out is hidden and marked deprecated in the current CLI source (removal planned for the 0.17 cycle).

## Known shortcomings

- Rust typesetting system (language-filter mismatch) measured by an independent run (pgundlach/speedata typesetting-benchmark, hyperfine, MacBook Air M4, versions stated) against pdflatex and LuaLaTeX, typesetting engines rather than shaping libraries. Setups are not equal: the LaTeX timings include Python plus Jinja2, fonts differ, the 500 pages are 500 identical records (memoisation favours Typst), TeX Live 2022.
- The 4.55x is wall clock with Typst 0.12+ laying out page runs in parallel against single-threaded pdflatex (retier-23): total CPU time is 308 against 716 ms, about 2.3x, and the marginal per-page CPU about 1.9x. Speed is version-sensitive: open regressions #7102 (0.13 at 200 ms against 0.14-rc1 at 1.5 s), #8611 (0.15.0 at 14 minutes and 41 GB against 0.14.2 at 1 min 17 s and 32 GB) and #8561 (50 s font scan).

## Caveats and trade-offs

Rust, not C or C++: outside the default C++ language filter. The baselines are document typesetting engines (pdfTeX 1.40.24 and LuaHBTeX 1.15.0 from TeX Live 2022, four years older than Typst 0.14.2), recognisable incumbents for TeX-style typesetting but not HarfBuzz, FreeType or ICU; Typst is a whole typesetting system, so this is a text-layout entry at most. The benchmark comes from speedata (pgundlach, 1-star repo, companion blog post on news.speedata.de that is blocked here; a search snippet says the author would not pick the fastest engine and that a mail merge is the 'hello world' of typesetting). The documents are not equivalent: Typst uses the system 'Helvetica', pdflatex the helvet package (URW Nimbus Sans, Type 1, T1 encoding) and LuaLaTeX TeX Gyre Heros via fontspec; LaTeX sets the sender block in a minipage beside the recipient while Typst places it absolutely; the PDFs are not committed, so page counts could not be checked (each template forces one letter per page). The LaTeX and LuaLaTeX timings include the Python interpreter, Jinja2 import and template rendering; Typst parses the XML itself. The 500-page input is one record repeated 500 times, which favours Typst's memoised layout: 500 pages take 156.6 ms against 105.7 ms for 1 page, about 0.1 ms per extra page (derived from page data), and Typst's user time (241.3 ms) exceeds its wall time, so it used more than one core while pdflatex runs single-threaded. speedata Publisher is fastest at 1 page (94.5 ms, 1.12x faster than Typst). The Typst README claims fast incremental compilation and gives no LaTeX comparison. texlode/luatex-benchmark (MIT, accompanying the TUGboat 2026 paper 'Real-Time LuaTeX: Recompiling Large Documents in 1 ms') reports Typst 0.14 and later about 1.6-2.2x slower per incremental edit than 0.12/0.13 at 300 pages on x86 (no difference on Apple M4), and says the paper's Typst figures came from an earlier script and do not reproduce with bench.mjs (issue #1).

A different markup language and ecosystem from LaTeX (fewer packages, no TeX compatibility); incremental compilation and an instant-preview mode are the design goal. Rust, not usable as a C++ library (CLI or Rust crate).

## Maintenance

Very active (0.15.1 released 2026-07-17, commits through 2026-09-30, 2.9M crates.io downloads, Apache-2.0); copyable as a Rust crate or used as a CLI, not as a C/C++ library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** speedata/typesetting-benchmark's README holds hyperfine output matching every claimed number, from public runners (benchmark.sh, run_typst.sh, run_latex.sh, run_lualatex.sh, mailmerge.typ, mailmerge_template\*.tex, mailmerge_\*latex.py) on a named machine (MacBook Air M4, 16 GB) with tool versions; it was run by pgundlach of speedata, a competing vendor whose own engine loses at 500 pages, so it is an independent measurement of Typst. Not A: binary builds are unstated, and the timed pipelines are not equivalent (the LaTeX timings include a Python 3.14 + Jinja2 wrapper, fonts differ, and the 500-page input is 500 identical records).
- **Verifier notes:** Numbers verified against the speedata README and its runner scripts; B kept as an independent but narrow, non-equivalent shootout. Language Rust is correct (language-filter mismatch). Category: Typst belongs under text layout/typesetting, not font shaping; pdflatex is a typesetting-engine incumbent, not a shaping library.
- **Fields the verifier corrected:** `workload`, `hardware`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** Zerodha contract-note pipeline (blog blocked; search snippet only): Typst 3-4x faster than LaTeX, 2000+ pages in about 1 minute against 18 minutes with LuaLaTeX.
- **Pages the verifier opened:**
  - <https://github.com/speedata/typesetting-benchmark>
  - <https://github.com/speedata/typesetting-benchmark/commits/main>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/run_typst.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/run_latex.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/run_lualatex.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/run_sp.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge.typ>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge_template.tex>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge_template_lualatex.tex>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge_latex.py>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge_lualatex.py>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/generate_fakenames.py>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/fakenames.xml>
  - <https://github.com/typst/typst>
  - <https://github.com/typst/typst/commits/main>
  - <https://github.com/texlode/luatex-benchmark>
  - <https://raw.githubusercontent.com/texlode/luatex-benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/typst/typst/HEAD/README.md>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/crates/typst/src/lib.rs>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/crates/typst-layout/src/pages/mod.rs>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/crates/typst-layout/src/inline/linebreak.rs>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/crates/typst-cli/src/args.rs>
  - <https://github.com/typst/typst/tree/main/docs>
  - <https://github.com/typst/typst/tree/main/docs/content>
  - <https://github.com/typst/typst/tree/main/docs/content/changelog>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/docs/content/changelog/0.12.0.typ>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/docs/content/changelog/0.13.0.typ>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/docs/content/changelog/0.14.0.typ>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/docs/content/changelog/0.14.2.typ>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/docs/content/changelog/0.15.0.typ>
  - <https://raw.githubusercontent.com/typst/typst/HEAD/docs/content/changelog/0.15.1.typ>
  - <https://github.com/typst/typst/releases>
  - <https://github.com/typst/typst/issues?q=is%3Aissue%20state%3Aopen%20label%3Aperformance>
  - <https://github.com/typst/typst/issues?q=is%3Aissue%20state%3Aopen%20slow>
  - <https://github.com/typst/typst/issues?q=is%3Aissue%20state%3Aopen%20label%3Aperf>
  - <https://github.com/typst/typst/issues/8561>
  - <https://github.com/typst/typst/issues/8611>
  - <https://github.com/typst/typst/issues/7102>
  - <https://crates.io/api/v1/crates/typst>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/run_typst.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/run_latex.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/run_lualatex.sh>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge.typ>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge_latex.py>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/mailmerge_template.tex>
  - <https://raw.githubusercontent.com/speedata/typesetting-benchmark/HEAD/generate_fakenames.py>
  - <https://raw.githubusercontent.com/laurmaedje/laurmaedje.github.io/main/posts/comemo.md>
  - <https://raw.githubusercontent.com/laurmaedje/laurmaedje.github.io/main/posts/layout-models.md>
  - <https://raw.githubusercontent.com/laurmaedje/laurmaedje.github.io/main/posts/hypher.md>
  - WebSearch: Zerodha "1.5 million PDFs in 25 minutes" Typst LaTeX (snippets of https://zerodha.tech/blog/1-5-million-pdfs-in-25-minutes/)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/typst/typst`) · [data/wave10/enrich/raw/github_com_typst_typst.json](../../../data/wave10/enrich/raw/github_com_typst_typst.json) (enrichment confidence 0.8)

</details>
