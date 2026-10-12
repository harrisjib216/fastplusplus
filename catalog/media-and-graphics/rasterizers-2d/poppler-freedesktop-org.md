# Poppler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-2.0-or-later` · 🟢 active

> xpdf-derived C++ PDF library and pdftotext tool; about 19x faster text extraction than pure-Python pdfminer.six.

| | |
|---|---|
| **Beats** | pdfminer.six (pure-Python PDF text extractor; pypdf and pdfplumber are also in the table) |
| **Claimed result** | Text extraction average 0.3 s for pdftotext (Poppler) against 5.5 s for pdfminer.six, 3.3 s for pypdf and 8.6 s for pdfplumber in the README table (rounded to 0.1 s). From the unrounded cache.json, the 14-document totals give about 19x against pdfminer.six (76.5 s against 4.008 s), about 11.7x against pypdf and about 30x against pdfplumber (derived from page data); per document the gain over pdfminer.six ranges from 3.5x to 47x (2201.00214, 0.726 s against 34.273 s), geometric mean about 13x (derived from page data). README per-document rows: GeoTopo-book (117 pages) 1.0 s against 14.0 s for pdfminer.six; 2201.00214 0.7 s against 34.3 s; 1707.09725 (134 pages) 0.8 s against 5.4 s. Text-quality score 90% for pdftotext against 88% (pdfminer.six) and 95% (pypdf). In the same table pdftotext is about 2.5x slower than pypdfium2 (PDFium) and PyMuPDF (MuPDF), and slower than Tika (0.2 s average). |
| **Workload** | Text extraction from 14 pure PDFs (7 to 134 pages) with the Poppler pdftotext command against pure-Python extractors, in the independent py-pdf/benchmarks suite; page rendering is not measured. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz |
| **Compiler and flags** | not stated: pdftotext is the system /usr/bin/pdftotext binary, recorded in the suite's HISTORY.md as Poppler 24.02.0 (a distribution build); the README's '0.86.1' is a hard-coded label for the Python pdftotext package, which the harness does not call; pdfminer.six 20260107, pypdf 6.19.0, pdfplumber 0.11.10 |
| **Adoption** | no GitHub star count (canonical repo is on gitlab.freedesktop.org); the suite's table links pdftotext to poppler.freedesktop.org |
| **Links** | [repository](https://poppler.freedesktop.org/) · [benchmark](https://github.com/py-pdf/benchmarks) |

## Verdict

In the independent py-pdf/benchmarks suite on an Intel Core i7-6700HQ, one timed run per document over 14 born-digital PDFs, the distribution Poppler 24.02.0 pdftotext binary (compiler and flags unstated, run as a subprocess) extracted text in 4.008 s in total against 76.527 s for pdfminer.six 20260107, 46.83 s for pypdf 6.19.0 and 121.0 s for pdfplumber 0.11.10, about 19x, 12x and 30x (derived from page data); rendering was not measured.

## Use it when

- Shell and batch pipelines on Linux where poppler-utils is already a distro package and pdfminer.six, pypdf or pdfplumber is the current tool: about 19x, 12x and 30x less total time on the py-pdf suite.
- Multi-column documents where you want reading-order reconstruction (default mode) or a physical-layout dump (-layout), which PDFium's content-stream-order text API does not provide.
- Jobs that need word or line bounding boxes as plain files (-tsv, -bbox-layout) without writing code.
- GPL-compatible desktop or server software that wants a maintained PDF engine with GLib/Cairo or Qt integration.

## Skip it when

- Speed-first text extraction: on the same suite pypdfium2 (PDFium, 1.591 s) and PyMuPDF (MuPDF, 1.604 s) are both about 2.5x faster, and even Tika (Java, over HTTP to a local server) totals 2.912 s against 4.008 s.
- Closed-source or permissively licensed products: the README says programs calling Poppler must be GPL, and the xpdf commercial licence does not extend to Poppler.
- Code built on the internal poppler/ C++ headers: the README marks that API unstable, liable to change even between minor versions.
- Untrusted PDFs in an unsandboxed process: CVE-2026-10118 (integer overflow in Splash tilingPatternFill leading to a heap out-of-bounds write, per search-result summaries of the Debian tracker), and NEWS lists 'Fix crashes in malformed documents' in most monthly releases.
- Old toolchains: current master (26.09.90) sets CMAKE_CXX_STANDARD 23 and requires CMake 3.28.

## How it is fast

Against the pure-Python extractors the gain is mostly compiled C++ versus interpreted content-stream parsing and layout analysis in Python. TextOutputDev collects glyphs into words, lines, blocks and flows (TextPage::coalesce) and orders blocks with a depth-first topological sort following Breuel's 'High Performance Document Layout Analysis' (2003), all in native code. Rendering uses the xpdf-derived Splash rasterizer (with optional Boost 'for Splash backend performance') or Cairo, but no rendering was measured.

## Compared with alternatives

Pick Poppler over PDFium and MuPDF only when GPL is acceptable and you want its ready-made pdftotext modes (reading order, -layout, -tsv word boxes) or GLib/Qt integration; on raw extraction speed both siblings are about 2.5x faster in the same suite, and PDFium is permissively licensed.

## Integration

| | |
|---|---|
| **Form** | shared lib (libpoppler plus libpoppler-cpp, -glib, -qt5, -qt6 front-ends) and command-line tools (poppler-utils) |
| **Dependencies** | FreeType and Fontconfig required (Android uses the system font lookup instead); optional or soft-mandatory: libjpeg, OpenJPEG, LCMS2, libpng, libtiff, zlib, brotli, libcurl, NSS3, GPGME, HarfBuzz (required for font subsetting since 26.09), Boost, Cairo and GLib, Qt5/Qt6 |
| **Minimum toolchain** | C++23 compiler and CMake 3.28 (master at 26.09.90); the benchmarked 24.02.0 is an older distribution build |
| **Platforms** | not documented in the README; build files handle Fontconfig-based Unix systems, Android and Windows (relocatable build option) |
| **Thread safety** | not documented in the stable C++ or Qt6 headers read; poppler-glib serialises per-page calls with a per-page std::mutex (26.07.0 fixed a macOS crash caused by that mutex not being constructed) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness detail (read this session): the timed path is /usr/bin/pdftotext launched with subprocess.run after each PDF is written to a temp file, so process start, GlobalParams set-up and file I/O are inside every timing; charging the smallest pdftotext time (0.037 s) as fixed cost on all 14 documents would cut the total to about 3.49 s, which makes the pdfminer.six ratio about 22x rather than 19x (derived from page data). The README's '0.86.1' version and libpoppler-cpp dependency describe the Python pdftotext package, which library_code.py never imports.
- The measured Poppler is 24.02.0, about 30 releases behind the current 26.09.0 in NEWS, so newer pdftotext changes (for example -remove-hyphens in 26.x) are not reflected; timings are single time.time() runs, and the four committed cache.json snapshots give pdftotext totals of 4.039, 4.690, 4.539 and 4.008 s (the ratio to pdfminer.six stays between 17.6x and 20.1x, derived from page data).
- The suite's quality score is asymmetric: pypdf and pypdfium2 output pass through the harness's own post-processing (ligature replacement, de-hyphenation, page-label removal) before scoring, while pdftotext is scored raw, so its 90% understates it relative to those two.
- Licence nuance: xpdf-derived code is 'GPL v2 or v3' and explicitly NOT 'any later version' (README-XPDF), while Poppler's own changes are GPL version 2 or later, so the combined library is effectively GPL-2.0-only or GPL-3.0-only rather than GPL-2.0-or-later.

## Known shortcomings

- Only win is over pure-Python extractors in py-pdf/benchmarks (pdfminer.six 19x, pypdf 11.7x, pdfplumber 30x on raw totals); about 2.5x slower than PDFium and MuPDF in the same table, so it is really the incumbent those entries beat. Timed through the pdftotext CLI including process start; the row is Poppler 24.02.0 per HISTORY.md (the README's 0.86.1 is a hard-coded label). Licence, stars and last commit unverified (freedesktop hosts blocked).
- Enricher: ranks 4th of 7 on speed in py-pdf/benchmarks (Tika over HTTP at 2.912 s also beats its 4.008 s); the measured 24.02.0 is about 30 releases behind 26.09.0 (README label 0.86.1 wrong); pdfminer ratio 17.6-20.1x across the four committed runs, about 22x minus start-up. Licence: the xpdf code is GPL v2 or v3 explicitly not any-later-version (README-XPDF), so the combined library is effectively GPL-2.0-only or GPL-3.0-only. Working source mirror: tsdgeos/poppler_mirror (master 26.09.90, needs C++23).

## Caveats and trade-offs

The headline wins are over pure-Python libraries, a weak baseline that is not a C or C++ incumbent, and Poppler is not the fastest engine in the same table: pypdfium2 (PDFium) and PyMuPDF (MuPDF) are both about 2.5x faster on the unrounded totals (1.591 s and 1.604 s against 4.008 s), and Tika averages 0.2 s; Poppler is in effect the incumbent that the PDFium and MuPDF entries beat. Independent suite (py-pdf organisation, BSD-3-Clause, code public; the organisation maintains pypdf, one of the baselines) but compiler and flags not stated, so B not A. The Poppler number is the pdftotext executable launched with subprocess after writing each PDF to a temp file, so it includes process start and temp-file I/O and does not measure in-process libpoppler speed (the README's libpoppler-cpp dependency and '0.86.1' label describe the Python pdftotext package, which is not used; HISTORY.md says Poppler 24.02.0). One run per document timed with time.time(), no warm-up or repeats, times rounded to 0.1 s in the README (raw seconds in cache.json, re-measured only when a cache entry is cleared). Measured job is text extraction, not rasterisation, so category rasterizers-2d is a best fit. Licence taken from the list tag and not verified: poppler.freedesktop.org and gitlab.freedesktop.org do not resolve here and the github.com/freedesktop/poppler mirror returns 404, so last_commit and stars are unknown. Maintenance inferred from search snippets only (Debian tracker shows poppler 26.07.0 uploaded to experimental on 2026-07-23 and a Debian security entry naming 26.09.0 as a fix version), not from an opened page. Rendering comparisons against MuPDF, PDFium and Ghostscript (PDF Association 2021 survey, Alfresco blog) were not readable.

GPL (list tag GPLv2/GPLv3) copyleft, so linking it into permissive or closed products is restricted. The fast path in this suite is the command-line tool, not the library API.

## Maintenance

Actively maintained with monthly releases (26.09.0 is the newest in NEWS; the GitHub mirror tsdgeos/poppler_mirror shows commits on 2026-10-03, while gitlab.freedesktop.org and poppler.freedesktop.org were unreachable here); copyable only under the GPL, and the claim is valid but rests on a weak pure-Python baseline, with Poppler slower than PDFium and MuPDF in the same table.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Same independent py-pdf/benchmarks suite: public harness (benchmark.py, pdf_benchmark/library_code.py), stated CPU (Intel Core i7-6700HQ), Poppler's pdftotext timed against pdfminer.six, pypdf and pdfplumber on the same 14 PDFs; compiler and flags of the distro Poppler 24.02.0 binary are not stated, so not A.
- **Verifier notes:** Numbers match the README rows and cache.json; ratios against pure-Python extractors are slightly understated in the record (19x, 11.7x, 30x on unrounded totals). Keep with shortcomings: the only measured win is over pure-Python libraries, Poppler is about 2.5x slower than PDFium and MuPDF in the same table, and the timed path is the pdftotext CLI including process start; licence, last_commit and stars could not be checked (freedesktop hosts unreachable).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-116 (wave 10); enricher w10 pair-034
- **Pages the verifier opened:**
  - <https://github.com/py-pdf/benchmarks>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/benchmark.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/pdf_benchmark/library_code.py>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/HISTORY.md>
  - <https://raw.githubusercontent.com/py-pdf/benchmarks/HEAD/cache.json>
- **Sources the enricher read:**
  - https://poppler.freedesktop.org/ (not reachable from this environment)
  - https://gitlab.freedesktop.org/poppler/poppler/-/raw/master/README.md (connection failed)
  - https://raw.githubusercontent.com/freedesktop/poppler/HEAD/README.md (404)
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/README.md>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/README-XPDF>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/COPYING>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/COPYING3>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/NEWS>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/utils/pdftotext.cc>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/utils/pdftotext.1>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/poppler/TextOutputDev.cc>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/poppler/TextOutputDev.h>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/cpp/poppler-page.h>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/cpp/poppler-document.h>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/qt6/src/poppler-qt6.h>
  - <https://raw.githubusercontent.com/tsdgeos/poppler_mirror/HEAD/glib/poppler-page.cc>
  - <https://github.com/tsdgeos/poppler_mirror/commits/master>
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
  - WebSearch: poppler CVE 2026 pdftotext heap overflow fixed version (Debian security tracker CVE-2026-10118, osv.dev, vulert summaries)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://poppler.freedesktop.org`) · [data/wave10/enrich/raw/poppler_freedesktop_org.json](../../../data/wave10/enrich/raw/poppler_freedesktop_org.json) (enrichment confidence 0.7)

</details>
