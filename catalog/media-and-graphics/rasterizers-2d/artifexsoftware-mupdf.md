# MuPDF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `AGPL-3.0` · 🟢 active

> Artifex's C PDF/XPS/EPUB engine; about 2.5x faster text extraction than poppler's pdftotext and 2x faster image extraction than PDFium.

| | |
|---|---|
| **Beats** | poppler (the pdftotext command-line tool from poppler-utils, run as a subprocess) and PDFium (via pypdfium2) |
| **Claimed result** | Text extraction average 0.1 s for PyMuPDF against 0.3 s for pdftotext (poppler); per document 0.3 s against 1.0 s (GeoTopo-book) and 0.2 s against 0.8 s (1707.09725); from the suite's cache.json the 14-document totals are 1.604 s for PyMuPDF against 4.008 s for pdftotext (about 2.5x, derived from page data). pypdfium2 (PDFium) ties PyMuPDF at 0.1 s average and is ranked first (1.591 s total, marginally faster). Image extraction average 0.5 s for PyMuPDF against 1.0 s for pypdfium2 (7.333 s against 14.523 s total in cache.json, about 2x, derived from page data); poppler is not in the image row. |
| **Workload** | py-pdf/benchmarks: wall-clock time to extract the text of 14 pure (non-scanned) PDFs, and to extract their images, driven from Python through PyMuPDF (MuPDF), pdftotext (poppler) and pypdfium2 (PDFium). |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz |
| **Compiler and flags** | not stated: PyMuPDF 1.28.2 and pypdfium2 5.13.0 are prebuilt PyPI wheels; pdftotext is the system /usr/bin/pdftotext binary, which HISTORY.md records as Poppler 24.02.0 (the README's '0.86.1' is a hard-coded label in benchmark.py) |
| **Adoption** | 3.0k stars on the GitHub mirror; backs PyMuPDF and is embedded in many viewers and tools |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/ArtifexSoftware/mupdf) · [benchmark](https://github.com/py-pdf/benchmarks) |

## Verdict

py-pdf/benchmarks (independent, BSD-3-Clause harness) on an Intel Core i7-6700HQ timed 14 born-digital PDFs once each through Python: PyMuPDF 1.28.2 text extraction totalled 1.604 s against 4.008 s for the Poppler 24.02.0 pdftotext binary (about 2.5x, derived from page data) and 1.591 s for pypdfium2 5.13.0 (a tie), and image extraction 7.333 s against 14.523 s for pypdfium2 (about 2x, derived from page data); compiler and flags are unstated (prebuilt wheels and a distro binary). Rendering speed is not measured there; the only rendering numbers found are first-party: PyMuPDF's Appendix 4 (367 s versus 646 s for XPDF pdftopng at 150 DPI) and, snippet only, an Artifex-authored PDF Days 2021 survey (Ghent file at 600 dpi: MuPDF 5.4-9.2 s, Poppler 17.6 s, PDFium 37.5 s).

## Use it when

- Bulk text extraction from born-digital PDFs where poppler's pdftotext is the current tool: about 2.5x less total time on the py-pdf suite, with a higher text-quality score (94% versus 90%).
- Extracting embedded images in bulk: PyMuPDF's extract_image path took about half PDFium's time across 14 papers (7.3 s versus 14.5 s).
- Applications that need one engine for rendering, text, annotations, forms, redaction and PDF rewriting, plus XPS and e-book formats, from C, C++, Python, Java or JavaScript.
- Multi-page batch rendering on many cores: record a display list per page on one thread, then rasterise lists on worker threads with cloned contexts.
- Projects that can ship under AGPL-3.0 or buy Artifex's commercial licence.

## Skip it when

- Closed-source products or network services that will not release source and will not pay Artifex: AGPL-3.0 applies to the whole linked program.
- Text extraction when PDFium is already in use: pypdfium2 ties MuPDF on the same suite (1.591 s versus 1.604 s total) and ranks first on text quality (95% versus 94%).
- Drawing your own vector graphics (UI, charts, SVG-like scenes): MuPDF is a document interpreter, not a general 2D canvas; Blend2D, Skia or ThorVG are built for that.
- Untrusted PDFs in a privileged process without sandboxing: crafted files keep producing memory-safety CVEs (e.g. CVE-2026-3308, an integer overflow in pdf_load_image_imp leading to a heap out-of-bounds write in 1.27.0).
- Sharing one document across threads without your own locking: the docs forbid simultaneous calls on the same context, document or device.

## How it is fast

Pages are interpreted once into a device call stream, and an fz_display_list can record that stream so it can be replayed for rendering, hit-testing or text extraction without re-parsing the content stream; display lists can be rendered on several threads at once. The rasterizer is a global-edge-list scan converter in fixed point with tunable anti-aliasing (17x15 subsamples at the default 8-bit level, down to 2x2 or none), plus Ghostscript-style any-part-of-pixel and centre-of-pixel edge-buffer converters, and span painters specialised per component count (1, 3, 4 channels, with and without alpha). A shared resource store (256 MB by default) caches decoded images, fonts and glyphs across pages. No explicit SIMD intrinsics appear in the paint code; speed comes from these structural choices.

## Compared with alternatives

Pick MuPDF when the input is a PDF, XPS or e-book that must be parsed and rendered or mined for text; the catalogued siblings (Blend2D, Skia-class rasterizers, ThorVG, AGG) draw paths you supply and do not interpret PDF. For drawing your own vector scenes, Blend2D remains the faster general-purpose CPU rasterizer.

## Integration

| | |
|---|---|
| **Form** | static lib (libmupdf.a plus libmupdfthird.a) or shared lib; also prebuilt PyMuPDF wheels, an npm WASM module and Java/Android bindings |
| **Dependencies** | vendored git submodules: freetype, harfbuzz, libjpeg, openjpeg, jbig2dec, lcms2, zlib, brotli, gumbo-parser, mujs, extract, curl, freeglut, zxing-cpp, zint, cmark-gfm; optional tesseract and leptonica (OCR); system copies selectable |
| **Minimum toolchain** | C compiler with GNU make on Linux, BSD and macOS (default release build -O2); Visual Studio solution on Windows; generated C++ wrappers build with -std=c++14 |
| **Platforms** | Linux, BSDs, macOS, Windows (x86, x64, arm64 configuration), Android, WebAssembly |
| **Thread safety** | Thread-safe only with a caller-supplied fz_locks_context (FZ_LOCK_ALLOC, FZ_LOCK_FREETYPE, FZ_LOCK_GLYPHCACHE) and one cloned fz_context per thread; a document, context or device must never be used by two threads at once, but display lists can be rendered concurrently. |
| **Drop-in for the baseline** | no |

## Gotchas

- C errors are setjmp/longjmp exceptions (fz_try, fz_always, fz_catch); locals modified inside fz_try need fz_var(), and C++ callers should use the generated mupdf:: wrappers, which convert them into C++ exceptions and handle reference counting.
- Harness flaw in py-pdf/benchmarks (read this session): PyMuPDF's get_text is called with its default sort=False (no reading-order re-synthesis), while pdftotext runs in its default mode without -raw as a separate process after the PDF is written to a temp file, so the tools do different text work and poppler also pays process start-up; the startup share is at most about 0.04 s per document (the smallest pdftotext timing is 0.037 s) and cannot close the gap on large files (GeoTopo 0.308 s versus 0.999 s, 1707.09725 0.190 s versus 0.765 s).
- py-pdf/benchmarks cache.json is keyed by library name, not version, and has_doc skips any document that already has a quality score, so timings survive version bumps unless the cache is cleared; HISTORY.md reports 'Speed: no change' for PyMuPDF 1.26.1 to 1.28.2, which the public files cannot distinguish from a stale row. Each cell is a single time.time() run with no warm-up.
- The image-extraction comparison is not output-checked: PyMuPDF returns each xref's image in its stored format via extract_image, while the pypdfium2 path calls PdfImage.extract per page object and names every file .jpg; image counts and bytes are never compared.

## Known shortcomings

- py-pdf/benchmarks: poppler ran as a /usr/bin/pdftotext subprocess writing a temp file, not libpoppler-cpp; single unrepeated runs rounded to 0.1 s in the README; PDFium ties on text extraction and ranks first; the '0.86.1' pdftotext label is stale (HISTORY.md says Poppler 24.02.0). The work is text and image extraction, not rasterisation, so the rasterizers-2d baselines (Skia, Cairo, Blend2D) are not compared. AGPL-3.0.
- Enricher: py-pdf/benchmarks compares PyMuPDF get_text (sort=False) with pdftotext's default mode as a subprocess plus temp file, so the text work differs (startup at most \~0.04 s/doc; large docs still \~3-4x, GeoTopo 0.308 vs 0.999 s); cache.json is keyed by library name not version and has_doc skips scored docs, so rows survive version bumps; single time.time() runs; the image row is never output-checked (pypdfium2 names every image .jpg). Rendering evidence is first-party only (PyMuPDF app4 367 vs 646 s XPDF; Artifex-authored PDF Days 2021 survey, snippet only). CVE-2026-3308 heap OOB write in pdf_load_image_imp (1.27.0).

## Caveats and trade-offs

Independent suite (py-pdf organisation, BSD-3-Clause, runs the same script for every library; code public) but compiler and flags are not stated, so it is B not A. Harness: one run per document timed with time.time(), no warm-up or repetition, results rounded to 0.1 s in the README (raw seconds are in cache.json); the poppler row is not libpoppler-cpp but the /usr/bin/pdftotext binary launched with subprocess after writing the PDF to a temp file, so it pays process start-up and temp-file I/O that the in-process PyMuPDF and pypdfium2 calls do not (too small to explain the 2.5x total gap, since small documents show pdftotext at 0.0-0.1 s); pypdfium2 text timings include Python post-processing that PyMuPDF's do not. The README's Libraries table labels pdftotext '0.86.1' (hard-coded in benchmark.py) while HISTORY.md says Poppler 24.02.0. PDFium ties MuPDF on text extraction and is ranked first, so the text-extraction win is over poppler only; the image-extraction win is over PDFium only (poppler not measured there), and the two image paths (PyMuPDF extract_image versus pypdfium2 PdfImage.extract) are not checked for equivalent output. The measured jobs are text and image extraction through Python bindings, not page rasterisation, so category rasterizers-2d is a best fit and neither baseline is in that category's list (Skia, Cairo, Blend2D); the orchestrator may prefer a document-parsing category. First-party rendering evidence also exists: PyMuPDF docs Appendix 4 (https://github.com/pymupdf/PyMuPDF/blob/main/docs/app4.rst) report 150 DPI page rendering totals of 367.04 s for PyMuPDF against 646 s for XPDF pdftopng.exe (rate 1.76) and 851.52 s for pdf2jpg across eight sample PDFs, and plain text extraction 8.01 s against 27.42 s for XPDF (3.42x); that page states no CPU, compiler or date, includes file-writing time, and XPDF is poppler's ancestor rather than poppler, so it is tier C and was not used as the headline. The PDF Association survey (pdfa.org, 2021) and an Alfresco blog compare MuPDF, poppler and PDFium rendering but both hosts are blocked here, so their figures were not read. The GitHub repository is a mirror of Artifex's own git server; AGPL-3.0 with commercial licensing from Artifex.

AGPL-3.0 (commercial licence from Artifex for closed-source use), so copyleft applies to network services and products. The py-pdf numbers were taken through the PyMuPDF Python binding and pdftotext's Python binding, so both include Python call and string-copy overhead.

## Maintenance

Actively developed by Artifex (1.28 adds Markdown input, a new options API and checked arithmetic; last commit 2026-10-06 on the GitHub mirror of Artifex's own git server, bugs tracked on bugs.ghostscript.com); copyable under AGPL-3.0 or a paid commercial licence, and the py-pdf numbers stand as B with harness caveats rather than flaws that invalidate them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** py-pdf/benchmarks is an independent third-party suite (py-pdf organisation, BSD-3-Clause) whose public harness (benchmark.py, pdf_benchmark/library_code.py) times PyMuPDF, the poppler pdftotext tool and pypdfium2 on the same 14 PDFs on a stated CPU (Intel Core i7-6700HQ); compiler and flags are not stated (prebuilt PyPI wheels and a distro poppler-utils binary), so it falls short of A.
- **Verifier notes:** All claimed numbers match the py-pdf/benchmarks README and its cache.json; MuPDF beats poppler's pdftotext about 2.5x on total text-extraction time and pypdfium2 about 2x on image extraction, but ties PDFium on text extraction (PDFium ranked first). Shortcomings to record: poppler timed as a subprocess CLI with temp-file I/O, single unrepeated runs rounded to 0.1 s, stale '0.86.1' pdftotext label, extraction rather than rasterisation, baselines outside the rasterizers-2d list. Metadata checked: AGPL-3.0, about 3.0k stars and 499 forks, last commit 2026-10-06, not archived; not a duplicate of any listed entry.
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** py-pdf/benchmarks cache.json (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/py-pdf/benchmarks>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/benchmark.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/library_code.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/data_structures.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/output.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/cache.json>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/HISTORY.md>
  - <https://github.com/ArtifexSoftware/mupdf>
  - <https://github.com/ArtifexSoftware/mupdf/commits/master.atom>
  - <https://raw.githubusercontent.com/pymupdf/PyMuPDF/HEAD/docs/app4.rst>
- **Sources the enricher read:**
  - <https://github.com/ArtifexSoftware/mupdf>
  - <https://github.com/ArtifexSoftware/mupdf/tree/master/docs>
  - <https://github.com/ArtifexSoftware/mupdf/tree/master/docs/guide>
  - <https://github.com/ArtifexSoftware/mupdf/tree/master/source/fitz>
  - <https://github.com/ArtifexSoftware/mupdf/tree/master/platform>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/README>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/COPYING>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/Makerules>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/Makethird>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/include/mupdf/fitz/context.h>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/docs/guide/install.md>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/docs/guide/what-is-mupdf.md>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/docs/reference/c/overview.md>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/docs/cookbook/mupdf-explored.md>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/docs/examples/multi-threaded.c>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/source/fitz/draw-rasterize.c>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/source/fitz/draw-edge.c>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/source/fitz/draw-edgebuffer.c>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/source/fitz/draw-paint.c>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/scripts/mupdfwrap.py>
  - <https://raw.githubusercontent.com/ArtifexSoftware/mupdf/HEAD/scripts/wrap/__main__.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/benchmark.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/library_code.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/data_structures.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/output.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/cache.json>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/HISTORY.md>
  - <https://raw.githubusercontent.com/pymupdf/PyMuPDF/HEAD/docs/app4.rst>
  - <https://raw.githubusercontent.com/pymupdf/PyMuPDF/HEAD/docs/page.rst>
  - https://pdfa.org/wp-content/uploads/2021/06/Survey-of-OpenSource-Solutions.pdf (EGRESS_BLOCKED; figures and Artifex authorship from WebSearch snippets only)
  - https://gitlab.freedesktop.org/poppler/poppler/-/raw/master/utils/pdftotext.1 (blocked, 403)
  - https://raw.githubusercontent.com/freedesktop/poppler/HEAD/utils/pdftotext.1 (404)
  - WebSearch: MuPDF CVE 2025 heap overflow mutool vulnerability (CVE-2026-3308, CVE-2025-46206 snippets)
  - WebSearch: MuPDF vs poppler vs PDFium page rendering speed benchmark
  - WebSearch: Survey of OpenSource Solutions pdfa.org 2021 author
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/artifexsoftware/mupdf`) · [data/wave10/enrich/raw/github_com_artifexsoftware_mupdf.json](../../../data/wave10/enrich/raw/github_com_artifexsoftware_mupdf.json) (enrichment confidence 0.75)

</details>
