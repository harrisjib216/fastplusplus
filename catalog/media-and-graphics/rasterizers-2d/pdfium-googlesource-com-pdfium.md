# PDFium

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause AND Apache-2.0` · 🟢 active

> Google's C++ PDF engine behind Chromium's viewer; about 2.5x faster text extraction than Poppler's pdftotext.

| | |
|---|---|
| **Beats** | Poppler (the pdftotext command-line tool, poppler 'pdftotext' row of py-pdf/benchmarks) |
| **Claimed result** | Text extraction average 0.1 s for pypdfium2 (PDFium) against 0.3 s for pdftotext (Poppler) in the README table (rounded to 0.1 s). From the suite's unrounded cache.json, the 14-document totals are 1.591 s for pypdfium2 against 4.008 s for pdftotext, about 2.5x (derived from page data), not 3x; per document the gap ranges from 1.36x (2201.00214, 0.535 s against 0.726 s) to 6.32x (2201.00069, 0.045 s against 0.285 s), geometric mean about 2.4x (derived from page data). README per-document rows: GeoTopo-book (117 pages) 0.2 s against 1.0 s, 1707.09725 (134 pages) 0.2 s against 0.8 s, 2201.00214 0.5 s against 0.7 s, 2201.00151 0.2 s against 0.3 s; pdftotext is never faster on any of the 14 documents (three ties after rounding, pypdfium2 ahead on all 14 in the raw seconds). Text-quality score 95% (pypdfium2) against 90% (pdftotext). |
| **Workload** | Text extraction from 14 pure PDFs (7 to 134 pages) via the pypdfium2 binding of PDFium against the Poppler pdftotext command, in the independent py-pdf/benchmarks suite; page rendering is not measured. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz |
| **Compiler and flags** | not stated: pypdfium2 5.13.0 is a prebuilt PyPI wheel bundling a PDFium binary from bblanchon/pdfium-binaries; pdftotext is the system /usr/bin/pdftotext binary, which the suite's HISTORY.md records as Poppler 24.02.0 (the README's '0.86.1' is a hard-coded label in benchmark.py, the version of the Python pdftotext package, which the harness does not call) |
| **Adoption** | canonical repo on pdfium.googlesource.com (no star count); the read-only GitHub mirror chromium/pdfium (archived 2023-08-04) shows 541 stars; PDFium is the PDF engine of Chromium; bblanchon/pdfium-binaries tracks it with release chromium/8086 (PDFium 157.0.8086.0) on 2026-10-05, and pypdfium2 5.14.0 was released on PyPI on 2026-10-04 |
| **Links** | [repository](https://pdfium.googlesource.com/pdfium/) · [benchmark](https://github.com/py-pdf/benchmarks) |

## Verdict

In the independent py-pdf/benchmarks suite on an Intel Core i7-6700HQ, one timed run per document over 14 born-digital PDFs (7 to 134 pages), pypdfium2 5.13.0 with a prebuilt pdfium-binaries Clang release build extracted text in 1.591 s in total against 4.008 s for the distro Poppler 24.02.0 pdftotext binary run as a subprocess, about 2.5x (geometric mean 2.4x, derived from page data); only text extraction was measured, not rendering.

## Use it when

- Bulk text extraction from born-digital PDFs (LaTeX papers, generated reports) whose content-stream order is already reading order: 1.59 s against 4.01 s for pdftotext over 14 documents, with the suite's top quality score (95%).
- Products that must embed a PDF engine under a permissive licence: BSD-3-Clause (LICENSE also carries the Apache-2.0 text), where Poppler is GPL and MuPDF is AGPL-3.0 or commercial.
- Applications needing rendering, text with character boxes (FPDFText_GetCharBox), forms and page editing from one library, from C/C++, Python (pypdfium2), .NET (NuGet) or WASM.
- Cross-platform shipping without building it yourself: pdfium-binaries publishes weekly prebuilt libraries for Linux glibc and musl, macOS, Windows (x86, x64, arm64), Android, iOS and WASM.

## Skip it when

- Multi-column or complex layouts where reading order matters: PDFium emits content-stream order with no column analysis, while pdftotext's default mode reconstructs reading order and -layout preserves physical layout.
- Parallel extraction inside one process: fpdfview.h states that none of the PDFium APIs are thread-safe, so every call must be serialised; use a process pool instead.
- Teams that must build from source with their own toolchain: GN, Ninja and depot_tools with Chromium's Clang; GCC support is community patches only and MSVC patches are not accepted.
- Opening untrusted PDFs in a privileged process: Chrome keeps shipping PDFium use-after-free fixes (CVE-2026-11303 to CVE-2026-11307, fixed in Chrome 149.0.7827.53, per search-result summaries); sandbox it the way Chrome does.
- Tools that need raw PDF object access (dictionaries, streams, name trees): the public API does not expose it (crbug.com/pdfium/1694, per the pypdfium2 README).

## How it is fast

Text extraction (CPDF_TextPage) is a single pass over the page's text objects in content-stream order: each object is compared with the previous one and spaces or line breaks are generated from geometry thresholds (ProcessInsertObject), with no word, line or block clustering and no reading-order sort. Poppler's default pdftotext mode (TextOutputDev::coalesce) builds words, lines, blocks and flows and topologically sorts blocks into reading order, so part of the measured gap is less layout work rather than a faster parser. The benchmarked binary is a Clang release build from bblanchon/pdfium-binaries (is_debug=false, Chromium toolchain, PartitionAlloc off, no V8/XFA) running in-process, while Poppler runs as a separate process; no SIMD-specific text code was found. Upstream checks changes for speed regressions with SafetyNet (testing/tools/safetynet_compare.py), which compares two PDFium versions by time or instruction counts on a set of PDFs, Linux only.

## Compared with alternatives

Against MuPDF, which ties it on text speed (1.604 s against 1.591 s) and is about 2x faster at image extraction, pick PDFium when the licence must be permissive rather than AGPL; against Poppler, pick PDFium for speed and licence unless you need reading-order reconstruction or a ready-made CLI. The path rasterizers in this category (Blend2D, ThorVG, Skia-class engines) do not parse PDF.

## Integration

| | |
|---|---|
| **Form** | shared lib (static with pdf_is_complete_lib); usually consumed as prebuilt pdfium-binaries archives or pypdfium2 wheels |
| **Dependencies** | DEPS-pinned and vendored: FreeType, libjpeg-turbo, libpng, zlib, ICU, abseil, fast_float, simdutf, Highway, dragonbox, fp16, cpu_features, PartitionAlloc; OpenJPEG bundled unless use_system_libopenjpeg2; optional V8 (JavaScript and XFA) and Skia |
| **Minimum toolchain** | C++20 (default build), Clang under Chromium's toolchain policy, GN plus Ninja from depot_tools; GCC community patches only, no MSVC |
| **Platforms** | x64 default on Windows, Linux and macOS, x86 on Windows, arm for Android per README; pdfium-binaries adds Linux arm/arm64/x86/ppc64 and musl, Windows arm64, iOS and WASM; big-endian is not a priority |
| **Thread safety** | None of the PDFium APIs are thread-safe (fpdfview.h): embedders must ensure only one PDFium call runs at a time; pypdfium2 repeats this as a known limitation. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness noise (read this session): each cell is one time.time() run, and the four committed cache.json snapshots give pypdfium2 totals of 1.537 s, 3.970 s, 1.715 s and 1.591 s against pdftotext 4.039 s, 4.690 s, 4.539 s and 4.008 s; in the 2026-10-02 run (commit c323a47) 2201.00214 took 2.816 s instead of about 0.5 s, cutting the total advantage to 1.18x, while the per-document geometric mean stayed 2.3x to 2.5x in all four runs (derived from page data).
- Not the same work: pypdfium2 runs in-process and returns content-stream-order text, while pdftotext is launched with subprocess after a temp-file write and does reading-order analysis; even charging the smallest pdftotext time (0.037 s) as fixed start-up cost on all 14 documents leaves about 3.49 s against 1.59 s (about 2.2x, derived from page data).
- FPDFText_GetText, which pypdfium2's get_text_range calls, 'ignores characters without UCS-2 representations' and also returns characters outside the crop box; pypdfium2 points to get_text_bounded for full Unicode.
- The quality comparison is asymmetric: pypdfium2 and pypdf output pass through the suite's own postprocess (ligature replacement, de-hyphenation, page-label removal) before scoring, while pdftotext and PyMuPDF are scored raw, so the 95% against 90% gap is partly the harness's cleanup (that Python work does count against PDFium's time).

## Known shortcomings

- py-pdf/benchmarks text extraction: README rounding gave 3x, raw cache.json totals are 1.591 s vs 4.008 s for pdftotext, about 2.5x (1.36x to 6.32x per document); harness unequal (Poppler run as a subprocess with a temp file, PDFium in-process with Python post-processing), single time.time() run, compiler and flags unstated. Licence BSD-3-Clause AND Apache-2.0; last commit unknown (googlesource blocked).
- Enricher: each py-pdf/benchmarks cell is a single time.time() run; four committed cache.json snapshots give pypdfium2 1.537/3.970/1.715/1.591 s vs pdftotext 4.039/4.690/4.539/4.008 s (in run c323a47 doc 2201.00214 took 2.816 s and the total edge fell to 1.18x, per-doc geomean 2.3-2.5x in all four runs). Unequal work: one content-stream-order pass (CPDF_TextPage, no sort) vs pdftotext's reading-order analysis (Breuel topological sort) run as a subprocess with a temp file; charging the smallest pdftotext time as start-up on all 14 docs still leaves about 2.2x; the harness postprocess cleans pypdfium2 and pypdf output only. get_text_range is UCS-2 only; no API is thread-safe.

## Caveats and trade-offs

Independent suite (py-pdf organisation, BSD-3-Clause, one script for every library, code public) but compiler and flags are not stated, so B not A. The README's 0.1 s against 0.3 s averages are rounded; the unrounded cache.json totals give about 2.5x, not 3x. Not a like-for-like harness: PDFium is driven in-process through the pypdfium2 ctypes binding (PdfDocument from bytes, get_textpage, get_text_range per page, plus Python post-processing that re-joins hyphenated words and adds page labels, which counts against PDFium), while Poppler is the /usr/bin/pdftotext executable run with subprocess after writing each PDF to a temp file, so Poppler's time includes process start and temp-file I/O; that overhead matters on the small documents (tens of milliseconds) but does not explain the large-document gaps (GeoTopo-book 0.238 s against 0.999 s). One run per document timed with time.time(), no warm-up or repeats; timings are cached in cache.json and only re-measured when an entry is cleared (the 2026-10-02 HISTORY.md entry reports no speed change for pypdfium2 4.30.1 to 5.13.0 or for pdftotext). The README labels pdftotext '0.86.1' while HISTORY.md says Poppler 24.02.0. The measured job is text extraction (content-stream parsing and text layout), not page rasterisation, so category rasterizers-2d is a best fit (the sibling MuPDF entry uses the same suite and category); PyMuPDF (MuPDF) ties PDFium at 0.1 s average (1.604 s against 1.591 s total). Licence: the LICENSE file in the chromium/pdfium mirror carries the BSD-3-Clause notice followed by the full Apache-2.0 text, and pypdfium2's README calls PDFium 'a BSD-style license'; pdfium.googlesource.com did not resolve from this environment, so the current upstream LICENSE and last_commit were not read (activity inferred from pdfium-binaries and pypdfium2 releases). Other PDFium-versus-Poppler rendering comparisons (PDF Association 2021 survey, Alfresco blog) were not read.

Large C++ codebase with many bundled third-party dependencies (each carrying its own licence, per the pypdfium2 README), normally consumed through binary builds such as pypdfium2 or bblanchon/pdfium-binaries. Strong text extraction quality in the same suite (95% against Poppler's 90%).

## Maintenance

Actively developed as Chromium's PDF engine (the GitHub mirror chromium/pdfium, flagged archived since 2023-08-04, still lists commits to 2025-11-19; pdfium-binaries builds weekly and pypdfium2 5.14.0 shipped 2026-10-04); copyable under BSD-3-Clause, the numbers stand as tier B with harness caveats (one-shot timings, unequal text work) rather than flaws that invalidate them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** py-pdf/benchmarks is an independent third-party suite (py-pdf organisation, BSD-3-Clause, 337 stars) whose public harness (benchmark.py and pdf_benchmark/library_code.py) times pypdfium2 (PDFium) and the Poppler pdftotext tool on the same 14 PDFs on a stated CPU (Intel Core i7-6700HQ); compiler and flags are not stated (prebuilt pdfium-binaries build inside the pypdfium2 wheel, distro Poppler 24.02.0 binary), so it falls short of A.
- **Verifier notes:** Numbers match the py-pdf/benchmarks README rows; the 3x headline came from rounded averages and the raw cache.json gives about 2.5x, now corrected. Harness asymmetry (Poppler run as a subprocess with a temp file, PDFium in-process with Python post-processing) and single-run time.time() timing are documented; baseline_in_list true depends on the Poppler record in this same batch being kept.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-116 (wave 10); enricher w10 pair-034
- **Pages the verifier opened:**
  - <https://github.com/py-pdf/benchmarks>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/benchmark.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/library_code.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/data_structures.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/HISTORY.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/cache.json>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pyproject.toml>
  - <https://github.com/chromium/pdfium>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/LICENSE>
  - <https://github.com/bblanchon/pdfium-binaries/releases>
  - <https://pypi.org/pypi/pypdfium2/json>
- **Sources the enricher read:**
  - https://pdfium.googlesource.com/pdfium/ (ENOTFOUND, not reachable)
  - <https://github.com/chromium/pdfium/commits/main>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/README.md>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/public/fpdfview.h>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/public/fpdf_text.h>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/docs/getting-started.md>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/BUILD.gn>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/DEPS>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/core/fpdftext/cpdf_textpage.cpp>
  - <https://raw.githubusercontent.com/chromium/pdfium/HEAD/docs/safetynet.md>
  - <https://raw.githubusercontent.com/pypdfium2-team/pypdfium2/HEAD/README.md>
  - <https://raw.githubusercontent.com/pypdfium2-team/pypdfium2/HEAD/src/pypdfium2/_helpers/textpage.py>
  - <https://pypi.org/pypi/pypdfium2/json>
  - <https://raw.githubusercontent.com/bblanchon/pdfium-binaries/HEAD/README.md>
  - <https://github.com/bblanchon/pdfium-binaries/tree/master/steps>
  - <https://raw.githubusercontent.com/bblanchon/pdfium-binaries/HEAD/steps/05-configure.sh>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/benchmark.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/library_code.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/data_structures.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/text_extraction_post_processing.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/score.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/HISTORY.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/cache.json>
  - <https://github.com/py-pdf/benchmarks/commits/main/cache.json>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/1c3fe78/cache.json>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/c323a47/cache.json>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/612bad6/cache.json>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/poppler/TextOutputDev.cc>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/utils/pdftotext.1>
  - WebSearch: PDFium CVE 2026 use after free Chrome security fix (sentinelone, feedly, radar.offseq summaries)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://pdfium.googlesource.com/pdfium`) · [data/wave10/enrich/raw/pdfium_googlesource_com_pdfium.json](../../../data/wave10/enrich/raw/pdfium_googlesource_com_pdfium.json) (enrichment confidence 0.75)

</details>
