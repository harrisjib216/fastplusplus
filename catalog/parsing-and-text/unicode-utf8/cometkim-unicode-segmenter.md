# unicode-segmenter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `JavaScript` · `MIT` · 🟢 active

> Zero-dependency JavaScript UAX #29 grapheme segmenter, about 2x faster than built-in Intl.Segmenter on Node and Bun.

| | |
|---|---|
| **Beats** | Intl.Segmenter (the built-in JavaScript grapheme segmenter, ICU in V8/JavaScriptCore/SpiderMonkey); also graphemer, grapheme-splitter, @formatjs/intl-segmenter and a WebAssembly build of Rust unicode-segmentation |
| **Claimed result** | README: '1.3\~2.5x faster than built-in Intl.Segmenter', '3.5\~8x faster than WASM binding of the Rust unicode-segmentation' and '5\~48x faster than other JavaScript libraries' in Node.js/Bun/Deno. Record 20260727, Apple M4 Pro, node 26.5.0: ASCII 2.65 us vs Intl.Segmenter 5.30 us (2x), emojis 829.70 ns vs 2.24 us (2.7x), Hindi 2.75 vs 5.44 us (1.98x), demonic characters 457.21 ns vs 1.05 us (2.3x), tweet text 4.12 vs 8.53 us (2.07x), code snippet 9.99 vs 18.97 us (1.9x). Same machine, bun 1.3.14: 1.41x (Hindi) to 2.04x (ASCII) faster than Intl.Segmenter. Record 20251213, Intel Core Ultra 7 258V, node 25.2.1 x64-linux: ASCII 3.71 vs 8.07 us (2.17x), other corpora 2.13x to 3.05x. In Firefox 154.0b1 (20260727, same Mac) it is 1.49x to 1.97x SLOWER than Intl.Segmenter on every corpus. |
| **Workload** | Grapheme cluster segmentation (UAX #29) of six corpora (Lorem ipsum ASCII, emojis, Hindi, 'demonic' combining characters, tweet text, code snippet), per-iteration time in Node.js, Bun, Deno and browsers. |
| **Metric** | latency |
| **Hardware** | Apple M4 Pro (\~4.43 GHz), macOS 26.5, for the 20260727 Node/Bun/browser runs; Intel Core Ultra 7 258V (\~4.65 GHz), Linux, for the 20251213 runs; 48 archived record files from 2024-09-02 to 2026-07-27 (Node, Bun, Chrome, Firefox, Safari; no Deno record) in benchmark/grapheme/_records. |
| **Compiler and flags** | JavaScript, no compiler: `yarn perf:grapheme` runs `node --expose-gc benchmark/grapheme/perf.js` (mitata ^1.0.34, gc('inner') per bench); each record header states the runtime, e.g. 'node 26.5.0 (arm64-darwin)', 'bun 1.3.14 (arm64-darwin)', 'node 25.2.1 (x64-linux)'. Browser runs use the Vite page (perf:grapheme:browser) and report cpu/runtime as null. |
| **Adoption** | 112 stars, 4 forks, 324 commits; npm latest 0.17.3 (registry.npmjs.org); listed as an e18e recommendation in the README |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/cometkim/unicode-segmenter) · [benchmark](https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_records/20260727-apple_m4_pro-macos_26.5-nodejs_26.5.0.txt) |

## Verdict

The author's mitata harness, benchmark/grapheme/perf.js run as `node --expose-gc`, first asserts that segments equal Intl.Segmenter's. It then times [...graphemeSegments(s)] against [...Intl.Segmenter().segment(s)] on six short strings of 63-410 UTF-16 units. On an Apple M4 Pro with Node 26.5.0 (record 20260727, code at 0.17.2) unicode-segmenter was 1.9x-2.7x faster; it was 1.41x-2.04x faster on Bun 1.3.14 on the same machine and 2.13x-3.05x faster on an Intel Core Ultra 7 258V with Node 25.2.1 (record 20251213, 0.14.x code that still had the later-fixed GB9c/GB11 bugs, though not on these inputs), and 1.49x-1.97x slower in Firefox 154.0b1. The author's own benchmark/grapheme/_corpora.js says these short cases 'mostly measure call overhead'. An unofficial spot check this session (Node 22.22.0, shared Intel Xeon 2.10 GHz VM, simple hrtime loop, single run) measured 6.6x-8.2x on the same strings and 4.3x on a 39K-unit concatenation, so the lead depends heavily on the engine's Intl.Segmenter version.

## Use it when

- JavaScript engines without Intl.Segmenter or with an outdated one: React Native/Hermes, QuickJS, older browsers and some edge runtimes. The count/split entry is 2,321 bytes min+gzip and 15.8 kB of Hermes bytecode.
- Node.js or Bun server code that segments many short strings, such as chat messages, usernames or form fields: the author's records show 1.9x-2.7x faster than Intl.Segmenter on Node 26.5 and 1.41x-2.04x on Bun 1.3.14.
- Counting graphemes in hot paths (length limits, string width, cursor maths): countGraphemes allocates no segment objects and has its own loop.
- When results must be identical across runtimes: Unicode 17.0 data ships with the package instead of depending on each host's ICU version.
- Replacing graphemer or grapheme-splitter, which implement older Unicode rules (15.0 and 10.0 per the README table) and ran 15x-26x slower on the ASCII case in the M4 Pro record.

## Skip it when

- Browser code where Firefox matters: in the 20260727 Firefox 154.0b1 record it is 1.49x-1.97x slower than the built-in Intl.Segmenter on every corpus, and the README concedes it.
- Word or sentence segmentation, locale tailoring or backward iteration: only grapheme clusters are implemented (issues #25 word/sentence and #26 DoubleEndedIterator are open), and the adapter throws TypeError for 'word' and 'sentence'.
- Memory-tight cold starts: the author's memory stats show 217 kB of retained JS heap plus 19.1 kB of ArrayBuffers, against 86.1 kB for Intl.Segmenter. The tables are decoded at module load, which the 0.17.2 changelog puts at about 1.5 ms.
- C or C++ code: it is JavaScript only. The same author's Rust port, fast-grapheme-segmenter, is the native option.

## How it is fast

The work stays in plain JavaScript loops that the JIT optimizes, instead of crossing into the engine's native ICU iterator for every segment. Category lookup is a one-load read from flat Uint8Arrays for U+0000-U+309F, U+A660-U+ABFF and the U+1F000-U+1FAFF emoji block, arithmetic for CJK/Vai and Hangul syllables (LV every 28th code point), and a binary search over a packed Uint32Array tail for rare ranges, about 19 KiB in total. All UAX #29 pair rules are precomputed into a 256-entry PAIR mask table, and the GB9c, GB11 and GB12/13 context lives in one small integer, so each boundary test is `!(st & PAIR[before << 4 | after])`. The hot functions are sized to V8's inlining limits: nextState stays under the 100-bytecode Maglev cap and cat() under the 460-bytecode limit. countGraphemes and collectGraphemes each own a loop with no generator, so they skip per-segment objects entirely.

## Compared with alternatives

Pick it in JavaScript. Its Rust port fast-grapheme-segmenter (same author and algorithm, plus a \~41 KB wasm build) is the choice in Rust, ugrapheme in Python, and uni-algo or ICU4X in native code. None of those siblings is benchmarked against Intl.Segmenter.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | ES2015 runtime with String.prototype.codePointAt, typed arrays, generators and modules (README). Ships as ESM with CommonJS builds and TypeScript declarations from JSDoc. |
| **Platforms** | Any JavaScript engine: Node.js, Bun, Deno, browsers, Hermes (React Native) and QuickJS. |
| **Thread safety** | Not documented. JavaScript is single-threaded per realm; the lookup tables are module-level typed arrays that are only read after initialization, and each worker loads its own copy. |
| **Drop-in for the baseline** | partial — intl-adapter's Segmenter matches Intl.Segmenter's API for granularity 'grapheme' only. intl-polyfill installs it only when Intl.Segmenter is missing, so on modern runtimes it changes nothing. The fast paths (countGraphemes, collectGraphemes, splitGraphemes) are separate functions, not part of the Intl interface. |

## Gotchas

- The output follows Unicode 17 and can differ from the host's Intl.Segmenter. In a check this session on Node 22.22.0 (ICU 77.1, Unicode 16), Intl.Segmenter kept U+2701 ZWJ U+2701 as one cluster while unicode-segmenter split it, which matches the Unicode 17.0 GraphemeBreakTest.txt shipped in test/_unicode_testdata.js. Issues #149 and #150 reported this as a bug against Unicode 16 test data and were closed. All 766 Unicode 17 test cases passed in the same check.
- The intl-adapter wraps graphemeSegments in a second generator. Its Segments.containing(i) rescans from the start of the string on every call (O(n)), returns the internal object with the _hd/_catBegin/_catEnd fields, and returns the first segment for negative indices.
- Versions before 0.17.0 (2026-07-06) had GB9c and GB11 rule bugs that diverged from Intl.Segmenter: ZWNJ and InCB state leaks in Indic scripts (issue #124, fixed in 0.16.0 on 2026-04-23) and ZWJ joins to non-pictographic characters (fixed in 0.17.0). 0.17.3 also dropped Gurmukhi U+0A4D from the InCB linker set. Pin 0.17.3 or later.
- The benchmark's correctness assertion runs only in Node, Bun and Deno: the browser records (Chrome, Firefox, Safari) were timed without checking output. The graphemer, grapheme-splitter and wasm unicode-segmentation baselines behind the README's '5\~48x' and '3.5\~8x' claims are not checked either, because the harness notes they do not support Unicode 15.1.

## Known shortcomings

- JavaScript library (src/\*.js; language-filter mismatch) against Intl.Segmenter, a JavaScript engine built-in rather than ICU4C or HarfBuzz. Numbers match record 20260727 (Apple M4 Pro, Node 26.5.0) and the public benchmark/grapheme/perf.js; in Firefox 154.0b1 it runs 1.49-1.97x slower than Intl.Segmenter, and the README's 1.3x low end was not found (lowest seen 1.41x on Bun). Unicode segmentation, moved to wave 3's unicode-utf8 category.
- The 20251213 Intel record ran 0.14.x code, before the GB9c and GB11 fixes in 0.16.0 and 0.17.0 (bench inputs unaffected; the harness asserts equality on Node, but the browser records skip the correctness assert). The author's _corpora.js notes that the short test cases mostly measure call overhead; Firefox is 1.49-1.97x slower than Chrome; the ratio depends on the V8 version (enricher spot check on Node 22.22.0, Xeon VM: 6.6-8.2x over Intl.Segmenter). The intl polyfill is a no-op when Intl.Segmenter exists and the adapter's containing() is O(n).

## Caveats and trade-offs

JavaScript library, not C or C++: outside the default C++ language filter, and it cannot be called from C++ without embedding a JavaScript engine. The baseline is Intl.Segmenter, the JavaScript engine's built-in segmenter: a recognisable incumbent inside JavaScript runtimes, but the timing includes the engine's JS-to-native iterator overhead per segment, so it does not show a win over ICU4C's BreakIterator, HarfBuzz or any C++ library. The other JavaScript libraries (graphemer, grapheme-splitter, @formatjs/intl-segmenter) are weak baselines, and the Rust unicode-segmentation baseline runs as a wasm-bindgen build. Browser results differ: in the 20260727 Firefox 154.0b1 record unicode-segmenter is 1.49x to 1.97x slower than Intl.Segmenter, as the README concedes. The README's Deno claim has no archived record, and its 1.3x lower bound was not found in the three records read (lowest seen: 1.41x in Bun 1.3.14). The 20251213 Node record's file name says nodejs_24.2.1 while its header says node 25.2.1. Numbers are first-party; the harness checks output equality with Intl.Segmenter before timing. Category: this is Unicode text segmentation (wave 3's unicode-utf8 category), not font shaping or layout. The Rust port fast-grapheme-segmenter is a separate entry.

Grapheme segmentation only (a few KB; 2,321 bytes min+gzip for the count/split API); keeps lookup tables in typed arrays (about 217 kB JS heap plus 19 kB ArrayBuffers retained, versus 86 kB for Intl.Segmenter). Unicode 17.0.0 data bundled, whereas Intl.Segmenter's Unicode version depends on the host. Works where Intl.Segmenter is missing (Hermes, QuickJS, old browsers). JavaScript only, not usable from C++.

## Maintenance

Actively maintained: 324 commits, latest release 0.17.3 on 2026-07-29, 112 stars, an e18e recommendation, and 6 open issues that are mostly feature requests (Unicode 18, word/sentence). MIT-licensed pure JavaScript with no build step needed to vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The 20260727 record (Apple M4 Pro, node 26.5.0 arm64-darwin) is mitata output of the public harness benchmark/grapheme/perf.js, run by package.json's 'perf:grapheme' script (node --expose-gc benchmark/grapheme/perf.js), and every claimed number matches it; the harness asserts that unicode-segmenter's segments equal Intl.Segmenter's before timing. Runtime version stands in for the compiler for JavaScript (same treatment as pure-rand and ultimate-express), and the CPU model is in each record header, so A stands even though the numbers are first-party.
- **Verifier notes:** Numbers verified against three record files and perf.js; A kept on the JavaScript precedent (runtime version as compiler). Language corrected from TypeScript to JavaScript (src is .js with JSDoc types); verify.py may ignore the language key, so record a decision override if wanted. Recategorise to Unicode text processing (unicode-utf8), not font-shaping-text-layout.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/README.md>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_records/20260727-apple_m4_pro-macos_26.5-nodejs_26.5.0.txt>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_records/20251213-intel_x86_64-linux-nodejs_24.2.1.txt>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_records/20260727-apple_m4_pro-macos_26.5-firefox_154.0b1.txt>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_records/20260727-apple_m4_pro-macos_26.5-bun_1.3.14.txt>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/perf.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_corpora.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/package.json>
  - <https://github.com/cometkim/unicode-segmenter>
  - <https://github.com/cometkim/unicode-segmenter/commits/main>
  - <https://github.com/cometkim/unicode-segmenter/tree/main/benchmark/grapheme>
  - <https://github.com/cometkim/unicode-segmenter/tree/main/benchmark/grapheme/_records>
  - <https://github.com/cometkim/unicode-segmenter/tree/main/src>
  - <https://registry.npmjs.org/unicode-segmenter/latest>
- **Sources the enricher read:**
  - <https://github.com/cometkim/unicode-segmenter>
  - <https://github.com/cometkim/unicode-segmenter/commits/main>
  - <https://github.com/cometkim/unicode-segmenter/tree/main/test>
  - <https://github.com/cometkim/unicode-segmenter/issues?q=is%3Aissue>
  - <https://github.com/cometkim/unicode-segmenter/issues/124>
  - <https://github.com/cometkim/unicode-segmenter/issues/149>
  - <https://github.com/cometkim/unicode-segmenter/issues/150>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/README.md>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/package.json>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/perf.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_corpora.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_testcases.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/benchmark/grapheme/_records/20260727-apple_m4_pro-macos_26.5-nodejs_26.5.0.txt>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/grapheme.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/core.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/utils.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/general.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/index.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/_grapheme_data.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/intl-adapter.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/src/intl-polyfill.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/test/_unicode_testdata.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/test/grapheme.js>
  - <https://raw.githubusercontent.com/cometkim/unicode-segmenter/HEAD/test/_helper.js>
  - <https://raw.githubusercontent.com/cometkim/fast-grapheme-segmenter/HEAD/tests/testdata.rs>
  - <https://registry.npmjs.org/unicode-segmenter>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/cometkim/unicode-segmenter`) · [data/wave10/enrich/raw/github_com_cometkim_unicode_segmenter.json](../../../data/wave10/enrich/raw/github_com_cometkim_unicode_segmenter.json) (enrichment confidence 0.8)

</details>
