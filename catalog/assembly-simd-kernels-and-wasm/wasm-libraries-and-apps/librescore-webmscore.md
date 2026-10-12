# webmscore

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-3.0-only` · 🟡 stale

> MuseScore's engraving library compiled to WebAssembly; a no-layout metadata mode claims 3x over MuseScore's native batch converter.

| | |
|---|---|
| **Beats** | The MuseScore 3 desktop binary's batch converter (spawn('musescore3', ['-j', batch.json]) exporting 200 .metajson files; installed version unstated), which is not told to skip layout |
| **Claimed result** | Boost Mode is about 3x faster than the batch converter feature (-j) of MuseScore (README, measured by web-example/benchmark.js; no per-run numbers on the page). |
| **Workload** | 200 rounds of loading a score (Aequale_No_1.mscz) and calling saveMetadata in Boost Mode (no layout) versus converting 200 copies with MuseScore's built-in batch converter. |
| **Metric** | throughput |
| **Compiler and flags** | Emscripten v2.0.6 with Qt5 for WebAssembly 5.15.2 and patches (README Compiling section); optimisation flags not checked |
| **Adoption** | 182 stars |
| **Last commit** | 2023-01-24 |
| **Links** | [repository](https://github.com/LibreScore/webmscore) · [benchmark](https://github.com/LibreScore/webmscore#boost-mode) |

## Verdict

The README says Boost Mode is about 3x faster than MuseScore's '-j' batch converter, from web-example/benchmark.js: 200 rounds of loading Aequale_No_1.mscz without layout and calling saveMetadata in Node, against one 'musescore3 -j' run converting 200 copies to .metajson with layout, first-file time subtracted. No per-run numbers, hardware, Node or MuseScore version are given, and the measurement dates from webmscore 0.7.0 (May 2020).

## Use it when

- Extracting metadata (title, parts, measures, key and time signatures, tempo, lyrics) from many MuseScore files in Node.js or a browser without installing MuseScore: use Boost Mode.
- Rendering MuseScore scores to SVG, PNG, PDF, MIDI or audio inside a web page or PWA, where shipping the desktop program is not possible.
- Server-side conversion pipelines pinned to Node 16 that can accept GPL-3.0 code.

## Skip it when

- You need PDF or sheet images fast: Boost Mode cannot produce PDF, and with layout enabled the README gives no speed comparison against native MuseScore.
- You need MusicXML or MXL from Boost Mode: the benchmark script notes saveXml and saveMxl 'cannot work properly' without layout.
- Long batch jobs: open issue #13 reports a bus error after thousands of load/saveMidi/destroy cycles in one Node process (10 files work), with no reply.
- Current Node.js or recent MuseScore 4 files: issue #12 says it only works on Node 16 (ERR_INVALID_URL on 18 and 20; a member blamed an upstream undici bug in April 2024, no fix), and issue #14 (Sep 2024) reports blank output for recent MuseScore 4 files, unanswered.
- Proprietary or permissively licensed products: GPL-3.0 as a MuseScore fork.

## How it is fast

There is no speed technique in the code: the release build uses -Oz (size optimisation) through Emscripten and Qt5 for WebAssembly. The claimed 3x comes from Boost Mode (doLayout=false), which loads the score with updates locked and never runs layout, so metadata or MIDI export skips the engraving pass, and from reusing one warm in-process instance instead of a batch run of the desktop program.

## Compared with alternatives

No catalogued sibling handles music notation; pick webmscore when the job is reading or rendering MuseScore files in a browser or Node, the way DuckDB-Wasm or Essentia.js bring their native C++ engines to the web, and accept that its speed claim rests on skipping layout rather than on faster code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime beyond the bundled wasm and data files (webmscore.lib.wasm about 7.4 MB plus webmscore.lib.mem.wasm about 3.9 MB as of 0.22.0); extra fonts (e.g. @librescore/fonts) for CJK text; an sf2/sf3 soundfont for audio; building from source needs Emscripten 2.0.6 and patched Qt5 5.15.2 for WebAssembly |
| **Minimum toolchain** | Node.js 16 in practice (README says v8.9.0+, issue #12 says 18 and 20 fail); browsers Chrome 57, Firefox 53, Edge 16, Safari 11 |
| **Platforms** | any WebAssembly runtime: browsers (Web Worker wrapper) and Node.js (in-process) |
| **Thread safety** | Single global wasm instance with process-wide state (current project, one shared soundfont file); in browsers calls are serialised through one Web Worker; scores must be freed with destroy() |
| **Drop-in for the baseline** | partial — replaces 'musescore -j' conversions with a JavaScript API (one call per output), not the command line or job file |

## Gotchas

- Harness flaw: web-example/benchmark.js times load(doLayout=false) plus saveMetadata in a warm in-process wasm instance, returning a string in memory, against 'musescore3 -j' doing full layout and writing 200 .metajson files to disk, with process teardown inside the timed span; the 3x measures skipped layout and I/O, not WebAssembly beating native code, and no timings, hardware or MuseScore version were published.
- The two sides do not produce the same output: metaJson writes json["pages"] = score-&gt;npages(), which only layout fills, so Boost Mode metadata most likely reports 0 pages where MuseScore's batch converter reports the real count (read in src/converter/internal/compat/notationmeta.cpp and web/main.cpp, not run).
- The claim is stale: benchmark.js was last changed on 2020-05-31 ('feat: boost mode, 3x faster than the musescore software', webmscore 0.7.0, MuseScore 3 based) and still spawns musescore3, while webmscore 1.0.0 (2023-01-13) was rebuilt on MuseScore 4.0; the current release has never been measured.
- Without extra fonts, characters outside the bundled FreeFont render as tofu in SVG/PNG/PDF; CJK fonts are not bundled since 0.6.0.

## Known shortcomings

- Only "about 3x" is stated; Boost Mode skips layout while the native musescore3 -j baseline does not, so the work is unequal. Last commit 2023-01-24.
- Harness flaw (read in code, not run): Boost Mode loads with doLayout=false and calls saveMetadata in a warm in-process wasm instance, while the native side runs full musescore3 -j layout, writes 200 .metajson files and includes process teardown in the timed span; metaJson 'pages' = score-&gt;npages() is only filled by layout, so Boost Mode output most likely reports 0 pages and differs from musescore3 -j. The wasm build is -Oz, so the 3x comes from skipped work, not faster code. The claim is stale: benchmark.js last changed 2020-05-31 (0.7.0, MuseScore 3 base) while 1.0.0 was rebuilt on MuseScore 4.0 and never re-measured; open issues #12 (broken on Node 18+), #13 (bus error after thousands of loads), #14 (blank output for recent MuseScore 4 files).

## Caveats and trade-offs

First-party; the README gives only 'about 3x' with no per-run numbers, hardware or MuseScore version. web-example/benchmark.js loads with doLayout=false (Boost Mode) and calls saveMetadata, while the native side runs a full musescore3 -j batch conversion, so the gap mostly measures skipped layout rather than WebAssembly beating native code. The native time is wall-clock around a spawned process with the first file's time subtracted via fs.watch as 'initialization'; the webmscore side excludes its own initialization. GPL-3.0-only with a font exception. Last commit 2023-01-24 on the webmscore branch. [retier] First-party; the README gives only 'about 3x' with no per-run numbers, hardware or MuseScore version. Harness flaw: web-example/benchmark.js times load(doLayout=false) plus saveMetadata in a warm in-process wasm instance, returning a string in memory, against 'musescore3 -j' doing full layout and writing 200 .metajson files to disk with process teardown inside the timed span (the first file's time is subtracted via fs.watch as 'initialization' while the webmscore side excludes its own initialization); the 3x measures skipped layout and I/O rather than WebAssembly beating native code. The two sides do not produce the same output: metaJson writes json['pages'] = score-&gt;npages(), which only layout fills, so Boost Mode most likely reports 0 pages (read in src/converter/internal/compat/notationmeta.cpp and web/main.cpp, not run). The wasm build is -Oz. The claim is stale: benchmark.js was last changed 2020-05-31 (webmscore 0.7.0, MuseScore 3) and still spawns musescore3, while 1.0.0 (2023-01-13) was rebuilt on MuseScore 4.0 and never measured; open issues #12 (broken on Node 18+), #13 (bus error after thousands of loads) and #14 (blank output for recent MuseScore 4 files). GPL-3.0-only with a font exception; last commit 2023-01-24.

Boost Mode (doLayout=false) cannot produce PDF and some outputs (saveXml, saveMxl) do not work properly in it. GPL-3.0 because it is a fork of MuseScore. Built against Qt5 for WebAssembly.

## Maintenance

Stale: last commit and npm release 1.2.1 on 2023-01-24, 12 open issues with no fixes since (Node 18+ broken, recent MuseScore 4 files give blank output, bus error in long batches); GPL-3.0, copyable only into GPL-compatible projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README states only 'about 3x faster' than musescore -j, backed by the public script web-example/benchmark.js, with no published timings, hardware, MuseScore version or build flags; Boost Mode skips layout, so the two sides do unequal work.
- **Retiered** C to D: Enricher: web-example/benchmark.js times Boost Mode (doLayout=false, metadata only, warm in-process instance) against a full musescore3 -j batch conversion that lays out every score, writes 200 files and includes process teardown; the outputs differ (metaJson pages comes from layout, so Boost Mode most likely reports 0) and the -Oz wasm build gains from skipped work, not faster code; no numbers, hardware or MuseScore version were ever published and the 2020 claim was never re-measured on the MuseScore 4 rebuild. No like-for-like measurement: C to D.
- **Verifier notes:** Claim matches the README ('about 3x faster than the batch converter feature (-j)'); numbers exist only as that ratio. The comparison is unequal work (layout skipped on the wasm side only); maintenance corrected from abandoned to stale (last commit 2023-01-24, under 3 years). License confirmed GPL-3.0-only from LICENSE.GPL; 182 stars, fork of musescore/MuseScore.
- **Fields the verifier corrected:** `maintenance_status`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-90 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/LibreScore/webmscore>
  - <https://github.com/LibreScore/webmscore/commits>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/README.md>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-example/benchmark.js>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/LICENSE.GPL>
- **Sources the enricher read:**
  - <https://github.com/LibreScore/webmscore>
  - <https://github.com/LibreScore/webmscore/commits/webmscore>
  - <https://github.com/LibreScore/webmscore/commits/web/web-example/benchmark.js>
  - <https://github.com/LibreScore/webmscore/issues>
  - <https://github.com/LibreScore/webmscore/issues/4>
  - <https://github.com/LibreScore/webmscore/issues/12>
  - <https://github.com/LibreScore/webmscore/issues/13>
  - <https://github.com/LibreScore/webmscore/issues/14>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/README.md>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/LICENSE.GPL>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-example/benchmark.js>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-example/package.json>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-public/package.json>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-public/rollup.config.js>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-public/src/index.js>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-public/src/utils.js>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-public/src/worker.js>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web-public/src/worker-helper.js>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web/Makefile>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/web/main.cpp>
  - <https://raw.githubusercontent.com/LibreScore/webmscore/HEAD/src/converter/internal/compat/notationmeta.cpp>
  - <https://registry.npmjs.org/webmscore>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/librescore/webmscore`) · [data/wave13/enrich/raw/github_com_librescore_webmscore.json](../../../data/wave13/enrich/raw/github_com_librescore_webmscore.json) (enrichment confidence 0.8)

</details>
