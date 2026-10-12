# otfcc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> Archived C library and CLI pair that dumps OpenType fonts to JSON and builds them back, claimed far faster than ttx and makeotf.

| | |
|---|---|
| **Beats** | ttx (fontTools, Python) for dumping fonts to text; Adobe makeotf for building a fully-optimized CFF OTF |
| **Claimed result** | 4x faster than ttx on CFF OTF, and 40x on TTF; 900x faster than makeotf for building a fully-optimized CFF OTF (README key features, verbatim) |
| **Workload** | Converting OpenType fonts to and from a text/JSON form: otfccdump against ttx on CFF OTF and on TTF files, and otfccbuild against makeotf when building a fully-optimized CFF OTF; the README does not say which fonts, how many runs or how time was measured. |
| **Metric** | throughput |
| **Adoption** | 435 stars, 69 forks; archived by owner 2022-06-04 (read-only) |
| **Last commit** | 2022-06-03 |
| **Links** | [repository](https://github.com/caryll/otfcc) · [benchmark](https://github.com/caryll/otfcc) |

## Verdict

The README alone states otfccdump is 4x faster than ttx (fontTools, Python) on CFF OTF and 40x on TTF, and otfccbuild 900x faster than Adobe makeotf for a fully optimized CFF OTF; no fonts, hardware, compiler, tool versions, -O level or timing method are given and the repo has no benchmark script, though both tools have a --time flag that logs per-step times, so the claims are easy to re-measure but unmeasured by anyone in public.

## Use it when

- Batch dump/patch/rebuild pipelines over many fonts or large CJK fonts where ttx's Python XML round trip takes minutes per file.
- Producing a subroutinized CFF OTF from a font you already hold as JSON or binary, for example as the last step of a build that generates outlines programmatically and emits otfcc JSON.
- Scripting font edits from any language that can read and write JSON, instead of linking a font-tooling library.
- Embedding a small, dependency-free C font reader/writer under Apache-2.0 in a C or C++ build after hardening it yourself.

## Skip it when

- Parsing fonts from untrusted sources: otfccdump has many 2022 fuzzing CVEs (heap out-of-bounds writes, CWE-787, CVSS 6.5, public PoCs) filed after the repo was archived, so none are fixed upstream.
- When byte-exact or validator-clean round trips matter: issue #68 (rsms, 2020) reports Inter-Regular.otf grows and fails Font Book and OTS 7.1.7 validation after dump/build even at -O0 on master, and the maintainer replied the project had stalled; issue #58 reports added GPOS kerning on an older release.
- Fonts with legacy kern tables, bitmap tables (issue #64) or variable-font building: kern is not processed (maintainer in #58) and variable support stayed alpha (v0.10.0-alpha dumps fvar/gvar).
- Building fonts from UFO or feature-file (FEA) sources: otfccbuild only takes its own JSON, so it does not replace makeotf or fontmake for source compilation.
- Any project that needs fixes or new OpenType features: archived 2022-06-04, last release v0.10.4.

## How it is fast

It is compiled C with a JSON DOM (udp json-parser/json-builder), sds strings, uthash tables and a vendored fast double-to-string routine (dep/extern/emyg-dtoa), against ttx, which is pure Python and emits XML. The 900x build row rests mostly on its CFF Type 2 charstring subroutinizer (lib/libcff/subr.c), which runs the SEQUITUR (Nevill-Manning) grammar-inference algorithm over operator-level tokens in a single pass instead of a costly repeated-substring search; how makeotf subroutinizes was not read. Table writing goes through a block graph (lib/bk/bkgraph.c) that hashes and deduplicates identical subtables, orders them by height and copies blocks to untangle 16-bit offset overflows.

## Compared with alternatives

Pick otfcc over ttf-parser, Fontations (skrifa / read-fonts) or Typr.js when you must write fonts back out, not only read them: those siblings are read-side parsers with active maintenance and are the better choice for parsing untrusted fonts or extracting outlines. None of the siblings is a ttx-style full dump/rebuild tool, so otfcc has no direct catalogued competitor for that job.

## Integration

| | |
|---|---|
| **Form** | static lib (libotfcc plus a deps static lib) and two CLI tools; prebuilt Windows and macOS binaries on the releases page |
| **Dependencies** | none external; vendored json-parser, json-builder, sds, uthash and emyg-dtoa under dep/ and include/dep/; premake5 is needed to generate build files |
| **Minimum toolchain** | C11 (gnu11); README recommends Clang/LLVM, GCC 5.1+ otherwise; Windows builds used Clang-CL via vs2015/vs2017 toolsets |
| **Platforms** | Linux, macOS, Windows; x64 and x86 build configurations (an arm64 macOS zip request, #71, was closed at archive time) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same job as ttx (dump to text, rebuild) but JSON instead of TTX XML with a different schema, so ttx files and fontTools scripts do not carry over; not a makeotf replacement because it does not compile UFO or FEA sources |

## Gotchas

- Dumped JSON is not always valid UTF-8 text per issue #51 (open): non-Windows name records holding legacy encodings break strict JSON readers such as Python json.load; the maintainer said they should come out as Base64, but the report was never closed.
- otfccbuild -O2 and -O3 rewrite the font (merge features, drop glyph names via --short-post, subroutinize, force CID, ignore glyph order); use --keep-glyph-order or -O1 when glyph IDs must stay stable.
- otfccdump holds the whole parsed font, the full JSON DOM and the complete output string in memory at once (src/otfccdump.c measures, callocs and serializes one buffer), so very large CJK fonts need several times the JSON size in RAM.
- Offset overflow is silent: bk_untangleGraph gives up after 16 passes, and getoffset() in lib/bk/bkgraph.c has its 'Unable to fit offset' warning commented out and casts the distance before bufwrite16b, so an oversized GSUB/GPOS that cannot be untangled is written with wrapped 16-bit offsets instead of failing.

## Known shortcomings

- README claims (4x and 40x vs ttx, 900x vs makeotf) are verbatim with no method or benchmark script, and ttx is Python; archived 2022-06-04 with unfixed otfccdump heap-overflow CVEs (CVE-2022-35035, CVE-2022-35448, CVE-2022-35463, snippet only). Loose fit for font-shaping-text-layout (font serializer, not shaping).
- Enricher: the 900x build row is not like-for-like (otfccbuild reads its own JSON and takes no UFO or FEA input; its speed comes from the SEQUITUR CFF subroutinizer in lib/libcff/subr.c); lib/bk/bkgraph.c getoffset() has its overflow warning commented out, so an untangle failure after 16 passes writes wrapped 16-bit offsets silently; open round-trip bugs #68 (Inter fails OTS and Font Book even at -O0, maintainer says the project stalled), #51 (JSON not valid UTF-8), #58 (GPOS kerning).

## Caveats and trade-offs

First-party README claim only: no hardware, font files, font sizes, tool versions, run counts, compiler or flags are given, and the visible tests directory (cffdump-opcode-check.js, ttf-roundtrip-test.js, payload) holds correctness checks, not a benchmark (the github.com listing was truncated, so a hidden timing script cannot be fully ruled out). otfccdump has a --time flag that times substeps, so the claim is easy to re-measure but nobody published such a run. ttx is a Python tool (fontTools), so the 4x and 40x rows are C against Python, not C against another C/C++ implementation; makeotf is Adobe's AFDKO build tool and probably takes different input than otfccbuild, so the build job may not be identical (inference, not stated in the README); the README does not say which -O level the 900x build used, and a 900x gain with unstated method is implausible enough to cap it at C on its own. Undated numbers; both baselines have changed since the repo was archived (2022-06-04). Web search snippets (typedrawers.com forum posts by the author, page not opened) say early TrueType-only builds parsed a 26 MB Chinese TTF in about 10 s versus about 10 min for ttx and built a 24 MB font in about 6 s versus about 4 min for ttx; snippet only, not used for the tier. Security: several 2022 fuzzing CVEs report heap buffer overflows in otfccdump (CVE-2022-35035 at commit 617837b, CVE-2022-35448 and CVE-2022-35463 at v0.10.4, CVSS 6.5, public PoCs in github.com/Cvjark/Poc); they were published after the repo was archived, so they are presumably unfixed upstream (snippet only from osv.dev/tenable search results, advisories not opened). Do not feed untrusted fonts to otfccdump. Category fit is loose: otfcc is an OpenType serializer/compiler (font file tooling), not a shaping or layout engine. Bundled third-party code under dep/ was not audited for licences.

Works by serializing a font to JSON and building it back from JSON, so it is a dump/build pipeline and a C library for parsing and writing OpenType files, not an in-place editing API or a text shaper. Archived and read-only, so no fixes will land. The README says it was developed and optimized for Clang/LLVM and prefers GCC 5.1 or later otherwise. Higher -O levels of otfccbuild (-O2, -O3) change the output font (merge features, subroutinize, force CID, ignore glyph order).

## Maintenance

Archived and read-only since 2022-06-04 (last release v0.10.4) with unfixed fuzzing CVEs and open round-trip bugs, so treat it as Apache-2.0 code to vendor and harden rather than a maintained dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Key features' list states verbatim '4x faster than ttx on CFF OTF, and 40x on TTF' and '900x faster than makeotf for building a fully-optimized CFF OTF', with no fonts, hardware, compiler, flags, tool versions or timing method, and no benchmark script in the repo (tests/ holds cffdump-opcode-check.js, ttf-roundtrip-test.js and payload/). First-party numbers without methodology are tier C; the 900x row would also hit the &gt;50x unstated-flags cap.
- **Verifier notes:** README numbers match the record verbatim; metadata confirmed on github.com (Apache-2.0, 435 stars, 69 forks, not a fork, archived by owner Jun 4 2022, last commit Jun 3 2022 'Merge pull request #70'). Shortcomings to record: first-party claim without methodology, Python baseline for the 4x/40x rows, non-identical makeotf build job for the 900x row, archived repo with unfixed 2022 otfccdump heap-overflow CVEs (snippet only), loose fit to the font-shaping category.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-118 (wave 10); enricher w10 pair-026
- **Pages the verifier opened:**
  - <https://github.com/caryll/otfcc>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/README.md>
  - <https://github.com/caryll/otfcc/commits>
  - <https://github.com/caryll/otfcc/tree/master/tests>
- **Sources the enricher read:**
  - <https://github.com/caryll/otfcc>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/README.md>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/premake5.lua>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/include/otfcc/font.h>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/include/otfcc/sfnt.h>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/src/otfccdump.c>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/src/otfccbuild.c>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/lib/libcff/subr.c>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/lib/libcff/subr.h>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/lib/libcff/charstring-il.c>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/lib/bk/bkgraph.c>
  - <https://raw.githubusercontent.com/caryll/otfcc/HEAD/LICENSE>
  - <https://github.com/caryll/otfcc/tree/master/lib>
  - <https://github.com/caryll/otfcc/tree/master/lib/libcff>
  - <https://github.com/caryll/otfcc/tree/master/lib/bk>
  - <https://github.com/caryll/otfcc/tree/master/dep/extern>
  - <https://github.com/caryll/otfcc/tree/master/include/dep>
  - <https://github.com/caryll/otfcc/issues?q=is%3Aissue>
  - <https://github.com/caryll/otfcc/issues/58>
  - <https://github.com/caryll/otfcc/issues/51>
  - <https://github.com/caryll/otfcc/issues/68>
  - <https://github.com/caryll/otfcc/releases>
  - WebSearch: otfcc otfccdump CVE-2022 heap buffer overflow (opencve.io and stack.watch snippets only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/caryll/otfcc`) · [data/wave10/enrich/raw/github_com_caryll_otfcc.json](../../../data/wave10/enrich/raw/github_com_caryll_otfcc.json) (enrichment confidence 0.7)

</details>
