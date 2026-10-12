# PDFOxide (pdf_oxide, Rust PDF text extraction)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust PDF toolkit (text, Markdown, images, editing) whose README claims 5x PyMuPDF; its own owner's later runs show it slower on real text-bearing PDFs.

| | |
|---|---|
| **Beats** | MuPDF (via PyMuPDF) and PDFium (via pypdfium2), C and C++ PDF engines measured through their Python bindings |
| **Claimed result** | README Python table: PDFOxide 0.8 ms mean (p99 9 ms, 100% pass) vs PyMuPDF 4.6 ms (p99 28 ms, 99.3%) and pypdfium2 4.1 ms (p99 42 ms, 99.2%); README text: '5x faster than PyMuPDF'. Ratios 5.8x and 5.1x are derived from page data. |
| **Workload** | Text extraction from 3,830 PDFs (veraPDF 2,907, Mozilla pdf.js 897, DARPA SafeDocs 26), single thread, 60 s timeout, no warm-up, mean and p99 time per document; text-only libraries, no OCR (README Performance section). |
| **Metric** | latency |
| **Compiler and flags** | Not stated for the README table. Cargo.toml [profile.release]: opt-level 3, lto = true, codegen-units = 1; rustc version not stated. Baseline versions not stated (scripts/benchmark_requirements.txt only sets minimums: pymupdf&gt;=1.28.2, pypdfium2&gt;=5.13.0). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/yfedoseev/pdf_oxide) · [benchmark](https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/README.md) |

## Verdict

The README reports a 0.8 ms mean per document vs 4.6 ms for PyMuPDF and 4.1 ms for pypdfium2 over 3,830 veraPDF, pdf.js and SafeDocs files, single thread, with no hardware, compiler or library versions and no published runner. The owner's later interleaved CPU-time runs (pdf_oxide 0.3.73 Python bindings, PyMuPDF 1.27.2.2, shared loaded machine) found 2.83x faster only on the veraPDF corpus and 0.47x on 200 real documents, and a 2026-09-24 rerun on the v0.3.79 branch found text 3.0x slower and open 2.49x faster than PyMuPDF 1.28.2.

## Use it when

- You need a permissively licensed (MIT or Apache-2.0) PDF text extractor where PyMuPDF's AGPL is unacceptable and some speed loss on text-heavy files is acceptable.
- Bulk triage of many small or mostly text-free PDFs (conformance fixtures, scanned image-only files, metadata or page-count passes) where open time dominates; this is where the measured wins are.
- You want one extraction core reachable from Rust, Python, Go, JS/WASM, C#, Java and others with the same output.
- A pure-Rust build with no C toolchain in the default feature set (WASM, C# AOT, musl wheels).

## Skip it when

- Text extraction from ordinary text-bearing documents: the owner measured 0.47x PyMuPDF's speed on the mean over 200 real documents (median 853 KB) and 3.0x slower than PyMuPDF 1.28.2 on 54 documents on the v0.3.79 branch (issues #1387, #1400).
- Long documents: page scaling measured O(n^1.33) vs PyMuPDF's O(n^0.80), about 2.6x slower at 512 pages; a 10,000-page veraPDF file exceeded 30 s where PyMuPDF took 3.96 s (#1387, #1389).
- Rendering: 72 dpi RGBA rendering measured 3.4x slower than PyMuPDF (#1400, 2026-09-24).
- Memory-constrained hosts: peak RSS about 2.1-2.2x PyMuPDF (32-36 MB vs 15-16 MB mean, #1387).
- Multithreaded extraction of one document: threads sharing a document scale to about 1.9x and 8 threads ran slower than 4 (#1589), and there is no parallel whole-document extraction from Python (#2284).

## How it is fast

Its advantage is in fixed per-file cost: a nom-based lexer and lazy xref and object loading make document open cheap (owner's issue #1400 measured open 2.49x faster than PyMuPDF 1.28.2, winning on 39 of 54 files), and early-outs such as skipping pages without BT operators make text-free files nearly free (1 ms vs 15 ms on a veraPDF fixture). Glyph decoding runs at about PyMuPDF's whole-pipeline cost per character (0.93x), but char-to-word assembly takes 72-93% of extract_text time and makes text-heavy pages 2-5x slower than MuPDF or PDFium (issues #1389, #1400).

## Compared with alternatives

No PDF sibling is catalogued in string-and-text; the relevant listed baselines are MuPDF and PDFium (wave 10), which are faster on text-heavy documents per the owner's own runs. Pick PDFOxide only for licence (vs MuPDF's AGPL) or binding reach, or for open-dominated workloads of small files.

## Integration

| | |
|---|---|
| **Form** | crate (also Python wheels via PyO3, a C ABI cdylib, CLI and WASM package) |
| **Dependencies** | Pure-Rust stack by default (qcms ICC, RustCrypto with legacy-crypto); optional C deps behind features: lcms2 (icc-lcms2), aws-lc-rs (fips), tract-onnx/pdfium-render (ml, ocr) |
| **Minimum toolchain** | Rust 1.88 (MSRV in Cargo.toml); Python &gt;=3.9 on PyPI (the README still says 3.8) |
| **Platforms** | Wheels for Linux x86-64 and aarch64 (manylinux_2_28 and musllinux_1_2), macOS x86-64 and arm64, Windows x64 and arm64; WASM |
| **Thread safety** | Not documented in what was read; issue #1589 reports poor scaling when threads share one document, and a Rust ParallelExtractor exists (repeats the document-wide artifact pass per worker, #2284). |
| **Drop-in for the baseline** | partial — similar page-oriented Python API to PyMuPDF and pypdfium2, but different names and output; text, words and Markdown differ in layout from MuPDF's |

## Gotchas

- Harness flaw behind the headline: the README table's corpus is 2,907 veraPDF fixtures out of 3,830 files, with a median file of 3.8 KB and 76.2% of files yielding zero characters from either library; the owner's own same-work interleaved runs give 2.83x faster on veraPDF but 0.47x on real documents, and 0.31x vs PyMuPDF and 0.23x vs pypdfium2 on a 25-document mix (issues #1387, #1400, #1352). Issue #2275 (2026-10-07) states the 5x claim has not been verified on real files. The README still carries 0.8 ms and '5x faster'.
- The table's runner is not published: scripts/bench_pymupdf.py times only the PyMuPDF side, bench/ has no Python runner (#2543), and the older scripts/benchmark_all_libraries.py times pdf_oxide's to_markdown_all against PyMuPDF's get_text with the output-file write inside the timer, so the work differs by tool.
- '100% pass rate' rounds 7 failing files out (pdf.js suite 99.2%), and scripts/bench_compare.py counts pymupdf errors, 'oxide has more text' and any output whose character set is a superset of PyMuPDF's as clean, so the 99.5% parity figure is lenient.
- Before 0.3.78 (2026-09-09) self-referential form XObjects could overflow the stack and five valid files aborted the host process, AES-256 encryption wrote files nothing could decrypt, and incremental updates dropped /Encrypt while appending plaintext objects; use 0.3.78 or later.

## Known shortcomings

- No hardware, versions or harness for the README table; the PDFOxide row is identical in the Python and Rust tables, so the comparison is possibly native Rust vs Python-wrapped MuPDF/PDFium; the corpus is mostly tiny veraPDF fixtures; MuPDF and PDFium are listed (wave 10); the methodology page (pdf.oxide.fyi) was unreachable.
- The maintainer's own issues contradict the README's '0.8 ms, 5x PyMuPDF': #1387 reports 2.83x faster on veraPDF but 0.47x on 200 real documents; #1400 reports 0.31x vs PyMuPDF and 0.23x vs pypdfium2, with the v0.3.79 branch's text extraction 3.0x slower than PyMuPDF 1.28.2 and only document open faster (2.49x); #2275 says the speed claim is 'not verified on real files'. Cause: the corpus median file is 3.8 KB and 76.2% of files extract zero characters; bench/ has no Python runner (#2543); peak memory is about 2.1x PyMuPDF. The record's 'does not render' is wrong: rendering exists and is 3.4x slower.

## Caveats and trade-offs

Hardware, compiler, library versions and the harness behind the README table are not published: scripts/bench_pymupdf.py times PyMuPDF open plus a Python per-page get_text loop with time.perf_counter over the same three corpora (trying up to 9 passwords on encrypted files and skipping bomb files), but no matching pypdfium2 or PDFOxide runner with the stated 60 s timeout and p99 was found. The CHANGELOG (0.3.5) says the PDFOxide corpus numbers come from a Rust verify_corpus example binary, which is no longer at examples/verify_corpus.rs. The PDFOxide row is identical (0.8 ms, p99 9 ms) in the 'Python Libraries' and 'Rust Libraries' tables, so it may be a native Rust measurement compared against Python-wrapped C and C++ engines; that it went through the Python binding is not established. 2,907 of the 3,830 PDFs are small veraPDF compliance fixtures, so the mean per document mostly measures fixed per-file overhead; lopdf (parse only, no extraction) shows 0.3 ms. Pass rate and output differ by tool (scripts/bench_compare.py counts a file as 'clean' even when only PDFOxide's character set is a superset of PyMuPDF's), so equal work is not shown. CHANGELOG 0.3.5 reported p50 0.6 ms and p99 33 ms on the same corpus, and the README does not say which version was measured. MuPDF and PDFium are already listed (wave 10). First-party claim from a project whose stated motive is replacing PyMuPDF. [retier] The maintainer's own issues contradict the README: #1387 reports 2.83x faster on veraPDF but 0.47x on 200 real documents; #1400 reports 0.31x vs PyMuPDF and 0.23x vs pypdfium2, with text extraction 3.0x slower than PyMuPDF 1.28.2 and only document open faster (2.49x); #2275 says the speed claim is not verified on real files. The README corpus median file is 3.8 KB and 76.2% of files extract zero characters; bench/ has no Python runner (#2543); peak memory is about 2.1x PyMuPDF. Rendering exists and is 3.4x slower (the earlier 'does not render' note was wrong).

Text and image extraction, PDF creation and editing; accuracy claims are 99.5% text parity with PyMuPDF and pypdfium2. MuPDF and PDFium also render pages, which this tool does not.

## Maintenance

Very active (0.3.78 on PyPI and crates.io 2026-09-08, 1.1k stars, 445 open issues, 1.24M crate downloads) and MIT/Apache-licensed, but the speed claim is contradicted by the maintainer's own issues #1387 and #1400 on text-bearing documents and holds only for open time and near-empty files; a retier below C (or a not-faster flag) is warranted.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README table against PyMuPDF (MuPDF) and pypdfium2 (PDFium) with no hardware, compiler, library versions or published harness for the table's 60 s-timeout/p99 run; scripts/bench_pymupdf.py covers only the PyMuPDF side, so not A, and nothing independent was found for B.
- **Retiered** C to D: Enricher: the maintainer's own issues (#1387, #1400, #2275) show PDFOxide 0.31-0.47x of PyMuPDF on real documents and text extraction 3.0x slower, and the README corpus has a 3.8 KB median file with 76.2% of files extracting zero characters; degenerate-workload precedent with a contradicted claim: C to D.
- **Verifier notes:** README numbers match the record (0.8 ms vs 4.6 ms and 4.1 ms; ratios 5.8x and 5.1x derived from page data). Main shortcomings for the record: no hardware, versions or published harness for the table, the PDFOxide row may be native Rust against Python-wrapped baselines, and the corpus is dominated by tiny conformance fixtures. pdf.oxide.fyi/docs/performance (the full-methodology page) did not resolve (ENOTFOUND).
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-104 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/README.md>
  - <https://github.com/yfedoseev/pdf_oxide>
  - <https://github.com/yfedoseev/pdf_oxide/commits>
  - <https://github.com/yfedoseev/pdf_oxide/tree/main/bench>
  - <https://github.com/yfedoseev/pdf_oxide/tree/main/benches>
  - <https://github.com/yfedoseev/pdf_oxide/tree/main/scripts>
  - <https://github.com/yfedoseev/pdf_oxide/tree/main/tools>
  - <https://github.com/yfedoseev/pdf_oxide/tree/main/docs>
  - <https://github.com/yfedoseev/pdf_oxide/tree/main/examples>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/benchmark_all_libraries.py>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/bench_compare.py>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/bench_pymupdf.py>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/benchmark_requirements.txt>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/tools/benchmark-harness/README.md>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/docs/VERIFICATION_RESULTS.md>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/examples/verify_corpus.rs>
  - <https://pypi.org/pypi/pdf_oxide/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/README.md>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/bench_pymupdf.py>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/bench_compare.py>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/benchmark_all_libraries.py>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/scripts/benchmark_requirements.txt>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/tools/benchmark-harness/README.md>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/docs/VERIFICATION_RESULTS.md>
  - <https://raw.githubusercontent.com/yfedoseev/pdf_oxide/HEAD/bench/README.md>
  - <https://github.com/yfedoseev/pdf_oxide>
  - <https://github.com/yfedoseev/pdf_oxide/tree/main/src>
  - <https://github.com/yfedoseev/pdf_oxide/issues?q=is%3Aissue+benchmark+OR+performance+OR+slow>
  - <https://github.com/yfedoseev/pdf_oxide/issues/2275>
  - <https://github.com/yfedoseev/pdf_oxide/issues/2543>
  - <https://github.com/yfedoseev/pdf_oxide/issues/1387>
  - <https://github.com/yfedoseev/pdf_oxide/issues/1352>
  - <https://github.com/yfedoseev/pdf_oxide/issues/1389>
  - <https://github.com/yfedoseev/pdf_oxide/issues/1400>
  - <https://pypi.org/pypi/pdf_oxide/json>
  - <https://crates.io/api/v1/crates/pdf_oxide>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/yfedoseev/pdf_oxide`) · [data/wave14/enrich/raw/github_com_yfedoseev_pdf_oxide.json](../../../data/wave14/enrich/raw/github_com_yfedoseev_pdf_oxide.json) (enrichment confidence 0.8)

</details>
