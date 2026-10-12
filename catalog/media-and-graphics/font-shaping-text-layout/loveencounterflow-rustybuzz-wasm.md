# rustybuzz-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Font shaping and text layout](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust (compiled to WebAssembly, driven from NodeJS)` · `unclear: Cargo.toml declares 'MIT/Apache-2.0' (left from the wasm-pack template, authors 'Your Name &lt;you@example.com&gt;'), but the LICENSE file only says 'the liecense goes here'` · 🔴 abandoned

> Abandoned wasm-bindgen wrapper around rustybuzz 0.4 for Node.js; claims about 1.5x harfbuzzjs 0.1.5 on Latin text shaping.

| | |
|---|---|
| **Beats** | harfbuzzjs (HarfBuzz compiled to WebAssembly, driven from NodeJS); also the HarfBuzz command-line tools spawned per line, opentype.js and fontkit |
| **Claimed result** | Parity with harfbuzzjs once the harness asymmetry is accounted for: the harfbuzzjs loop pays the font load per run, WASM initialisation on the first run and a per-line buffer leak, while rustybuzz-wasm's setup is outside the timing; on the JSON output format rustybuzz-wasm is 1.01x and 1.26x of harfbuzzjs (derived from page data). README figures: 1.5x harfbuzzjs, over 3x opentype.js (own table 4.6x; the '20x' and '280,000 glyphs/s' lines count UTF-16 units), over 12x the HarfBuzz command line spawned once per line. |
| **Workload** | Shaping 100 lines of text with 100 words per line (65,732 Unicode code units), measured as items per second from NodeJS; several runs in randomized order. |
| **Metric** | throughput |
| **Hardware** | '2015 customer grade, not fast, not new, not fancy laptop' (no CPU model) |
| **Compiler and flags** | Not stated for the benchmark; README says to build with 'wasm-pack build --target nodejs' (release) because debug builds are orders of magnitude slower. Node.js version not stated. |
| **Adoption** | 4 stars |
| **Last commit** | 2022-02-08 |
| **Links** | [repository](https://github.com/loveencounterflow/rustybuzz-wasm) · [benchmark](https://github.com/loveencounterflow/rustybuzz-wasm) |

## Verdict

These are the author's own Node.js runs on an unnamed 2015 laptop (Node.js version and build flags unstated). 100 lines x 100 French dictionary words (65,732 UTF-16 code units) in EB Garamond 12 Italic, 3 shuffled repetitions averaged. The 'rusty' string format reached 218,840 Hz vs harfbuzzjs 0.1.5 at 176,392 Hz in one run (about 1.24x) and 220,399 vs 143,434 Hz in another (about 1.54x). The JSON format, the closest to harfbuzzjs's per-glyph output, was 1.01x and 1.26x in those runs (derived from page data). The 12x-17.7x figures are against hb-shape spawned as a child process per line.

## Use it when

- Prototyping Node.js typesetting of Latin-script text where you want shaping, SVG glyph outlines and hyphenated line wrapping from one WASM package, and can parse the returned strings yourself.
- Batch-shaping many short left-to-right lines with a font's default features, where per-call overhead dominates. The benchmark shaped 100 lines of 100 random French dictionary words in EB Garamond 12 Italic.
- As a small worked example of wrapping rustybuzz with wasm-bindgen (the whole API is in one src/lib.rs).

## Skip it when

- Anything needing maintenance or a clear licence: last commit 2022-02-08, 4 stars, and LICENSE contains only 'the liecense goes here'. Cargo.toml's 'MIT/Apache-2.0' line comes from the wasm-pack template.
- Right-to-left or complex scripts, or language-specific shaping: shape_text hard-codes Direction::LeftToRight and language 'English', leaves script unset and uses BufferClusterLevel::Characters. Script, language and face selection are on the to-do list.
- OpenType feature control (dlig, smcp, ss01 and so on): the features list is always empty, so you get only the font's default features.
- Current shaping correctness: it pins rustybuzz 0.4 (2021) and ttf-parser 0.11, while rustybuzz itself reached 0.20.1 and has been succeeded by HarfRust.
- C/C++ or native code: use HarfBuzz directly. The benchmark never measures native HarfBuzz, only harfbuzzjs (WASM) and the hb-shape CLI spawned once per line.

## How it is fast

There is no novel technique. Shaping is rustybuzz 0.4's port of HarfBuzz's algorithm, compiled to WASM by wasm-pack in release mode. The measured edge comes from crossing the JS/WASM boundary once per line and returning one string, where harfbuzzjs's buffer.json() builds a JS object per glyph. The author's own to-do list says he does not know why the 'rusty' format is faster than the minimal 'short' one.

## Compared with alternatives

Rarely. text-shaper (wiedymi) is the catalogued JS shaper that beats a much newer harfbuzzjs (^0.4.13) across Latin, Arabic, Hebrew, Indic and CJK and is maintained, and Parley or HarfRust-based stacks cover Rust. Pick rustybuzz-wasm only to study or salvage its rustybuzz-plus-textwrap typesetting glue.

## Integration

| | |
|---|---|
| **Form** | module (wasm-pack --target nodejs package; prebuilt pkg/ committed to the repo, version 4.6.0) |
| **Dependencies** | rustybuzz 0.4, ttf-parser 0.11, textwrap 0.13 (smawk, hyphenation, unicode-width), hyphenation 0.8, wasm-bindgen 0.2 (serde-serialize), serde/serde_json, svgtypes 0.5, regex, html-escape, hex, plus pico-args, libc, lazy_static and unicode-linebreak, left as normal dependencies because the [dev-dependencies] header is commented out |
| **Minimum toolchain** | Rust edition 2018 with wasm-pack (release build required); Node.js version not documented |
| **Platforms** | Node.js through the nodejs wasm-pack target; browser use not documented |
| **Thread safety** | Not documented; fonts live in 16 global `static mut` byte vectors accessed in unsafe blocks, so treat the module as single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- The committed pkg/ artefacts may be debug builds. The README warns they can be 'orders of magnitude slower' and says to rebuild with `wasm-pack build --target nodejs` before measuring anything.
- Fonts must be sent as hex strings (twice the byte size, then hex-decoded in WASM) into slots 0-15. An unregistered slot calls alert and then panics, and a malformed font hits .unwrap() on Face::from_slice. Both trap the WASM instance.
- Each shape_text call parses the font twice (rustybuzz::Face and ttf_parser::Face) and deserialises the config with into_serde, so per-call cost grows with call count, not only with text length.
- Outputs are strings: 'rusty' is HarfBuzz's serialized text with glyph names and flags, and 'json' is a JSON string. Callers pay JSON.parse or custom parsing, which the published benchmark does not time.

## Known shortcomings

- WASM-vs-WASM comparison (1.24x-1.54x over harfbuzzjs, the official HarfBuzz WASM build) from the hengist bench with no CPU, Node version or flags; the harfbuzzjs row is now commented out of the source and rustybuzz-wasm ran with no OpenType features while the harfbuzzjs wrapper was not found, so work parity is unconfirmed. Licence unclear (Cargo.toml MIT/Apache-2.0 from a template, LICENSE placeholder): reference. Native rustybuzz is 1.5-2x slower than HarfBuzz.
- Not faster once the harness asymmetry is removed (retier-17): the harfbuzzjs timed loop includes the font load on every run, WASM initialisation on the first run and a per-line buffer leak plus validation, while rustybuzz-wasm's setup is outside the timing; on the JSON format rustybuzz-wasm is 1.01x and 1.26x of harfbuzzjs. The README's '280,000 glyphs per second, 20x opentype.js' contradicts the harness (counts UTF-16 units) and its own table (4.6x). Hard-coded LTR English with no features; placeholder LICENSE.

## Caveats and trade-offs

WebAssembly versus WebAssembly: the comparable baseline, harfbuzzjs, is HarfBuzz's official WASM build (a recognisable incumbent, but not native HarfBuzz), and the 12x-17.7x figures are against the HarfBuzz command-line tool spawned once per line, which the author says 'does not tell you how fast HarfBuzz itself is'. Rust compiled to WASM, so it does not match the catalog's default C++ language filter. The benchmark (hengist textshaping.benchmarks.coffee) shapes Latin text in EBGaramond12-Italic.otf, counts text.length (UTF-16 code units, not glyphs), runs 3 shuffled repetitions, and calls rustybuzz-wasm with no OpenType features (lib.rs sets features to an empty list) and its 'rusty' serialized-string output, while the harfbuzzjs wrapper is handed a features object {liga, clig, dlig, hlig}; that wrapper (hengist apps/glyphshapes-and-typesetting-with-harfbuzz) was not found, so work parity and output format cannot be checked, though the README says harfbuzzjs then 'does not support font features'. In the current source the harfbuzzjs row is commented out, so the published harfbuzzjs numbers cannot be regenerated as is. The two published runs disagree (1.24x vs 1.54x). No CPU (a '2015 customer grade' laptop), Node.js version or build flags; README stresses release builds via wasm-pack. Uses rustybuzz 0.4 (2021), which predates HarfRust; behdad's 2025-09-10 note that HarfRust is within 25% of native HarfBuzz (1.06x on Roboto) concerns a later library. The LICENSE file is a placeholder, so usability stays reference. Last commit 2022-02-08; the README calls it a work in progress. [retier] Not faster than harfbuzzjs on a like-for-like basis (harness timed the baseline's font load and leak). WebAssembly versus WebAssembly: harfbuzzjs is HarfBuzz's official WASM build, not native HarfBuzz, and the 12x-17.7x figures are against the HarfBuzz command-line tool spawned once per line. Rust compiled to WASM (language-filter mismatch). Hard-coded LTR English with no OpenType features; placeholder LICENSE file (reference).

Not feature-complete with rustybuzz: values cross the WASM boundary as JSON and hex-encoded strings; the README says harfbuzzjs does not allow arbitrarily long lines and does not support font features, and that rustybuzz-wasm is not feature-complete with rustybuzz yet. The repo also does SVG glyph rendering via ttf-parser and line wrapping via textwrap. Needs a Rust toolchain and wasm-pack to build; WASM artifacts are committed and may be unoptimized. Not callable from C++.

## Maintenance

Abandoned since 2022-02-08 (the README says the code is under development and will probably be incorporated into InterText) and has a placeholder LICENSE, so it stays reference-only; nothing here is safe to vendor without the author's licence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables from the author's own public benchmark (loveencounterflow/hengist dev/glyphshapes-and-typesetting-with-harfbuzz/src/textshaping.benchmarks.coffee), with no CPU model, Node.js version or build flags; the harfbuzzjs row cannot be regenerated from the current source, where harfbuzzjs_shaping is commented out of test_names.
- **Verifier notes:** Benchmark code was found and read (the record had not opened it); the README numbers match the record. Metadata from github.com: 4 stars, 0 forks, not a fork, not archived, last commit 2022-02-08 (abandoned). Language field is right.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/loveencounterflow/rustybuzz-wasm>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/src/lib.rs>
  - <https://github.com/loveencounterflow/rustybuzz-wasm/commits/master>
  - <https://raw.githubusercontent.com/loveencounterflow/hengist/master/dev/glyphshapes-and-typesetting-with-harfbuzz/src/textshaping.benchmarks.coffee>
  - <https://github.com/harfbuzz/harfrust/discussions/257>
- **Sources the enricher read:**
  - <https://github.com/loveencounterflow/rustybuzz-wasm>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/loveencounterflow/rustybuzz-wasm/HEAD/pkg/package.json>
  - <https://raw.githubusercontent.com/loveencounterflow/hengist/master/dev/glyphshapes-and-typesetting-with-harfbuzz/src/textshaping.benchmarks.coffee>
  - <https://github.com/loveencounterflow/hengist/tree/master/dev/glyphshapes-and-typesetting-with-harfbuzz/src>
  - <https://github.com/loveencounterflow/hengist/tree/master/apps>
  - <https://raw.githubusercontent.com/loveencounterflow/hengist/master/apps/glyphshapes-and-typesetting-with-harfbuzz>
  - <https://raw.githubusercontent.com/loveencounterflow/hengist/master/lib/benchmarks.js>
  - <https://raw.githubusercontent.com/loveencounterflow/hengist/master/lib/data-providers-nocache.js>
  - <https://raw.githubusercontent.com/loveencounterflow/glyphshapes-and-typesetting-with-harfbuzz/HEAD/README.md>
  - <https://raw.githubusercontent.com/loveencounterflow/glyphshapes-and-typesetting-with-harfbuzz/HEAD/package.json>
  - <https://raw.githubusercontent.com/loveencounterflow/glyphshapes-and-typesetting-with-harfbuzz/HEAD/src/main.coffee>
  - <https://raw.githubusercontent.com/loveencounterflow/glyphshapes-and-typesetting-with-harfbuzz/HEAD/src/demo-harfbuzzjs.coffee>
  - <https://raw.githubusercontent.com/loveencounterflow/glyphshapes-and-typesetting-with-harfbuzz/HEAD/lib/demo-harfbuzzjs.js>
  - <https://raw.githubusercontent.com/loveencounterflow/glyphshapes-and-typesetting-with-harfbuzz/HEAD/src/demo-harfbuzz.coffee>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzzjs/0.1.5/hbjs.js>
  - <https://raw.githubusercontent.com/harfbuzz/harfbuzzjs/HEAD/package.json>
  - <https://crates.io/api/v1/crates/rustybuzz>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/loveencounterflow/rustybuzz-wasm`) · [data/wave10/enrich/raw/github_com_loveencounterflow_rustybuzz_wasm.json](../../../data/wave10/enrich/raw/github_com_loveencounterflow_rustybuzz_wasm.json) (enrichment confidence 0.8)

</details>
