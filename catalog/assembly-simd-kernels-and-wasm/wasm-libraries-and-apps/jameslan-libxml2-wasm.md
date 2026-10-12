# libxml2-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (libxml2) compiled to WebAssembly with Emscripten; TypeScript wrapper` · `MIT` · 🟢 active

> libxml2 compiled to WebAssembly with a TypeScript DOM API; parses XML faster than pure-JS parsers, roughly level with native libxmljs2.

| | |
|---|---|
| **Beats** | libxmljs2 0.32.x (native N-API binding of libxml2) and the pure-JavaScript XML parsers @rgrove/parse-xml, fast-xml-parser and xmldoc |
| **Claimed result** | docs/performance.md (ops/s, Apple M3 Max, Node v18.19.0). Like-for-like string input (both bindings parse a JS string): libxml2-wasm String API 120,578 vs libxmljs2 78,688 ops/s on the 780-byte file (1.53x), 6,013 vs 12,414 on 35,562 bytes (0.48x, slower) and 43 vs 50 on 2,337,522 bytes (0.86x, slower). Buffer API rows: 167,479, 17,114 and 62 ops/s, i.e. 2.1x, 1.4x and 1.2x libxmljs2, but the harness gives the Buffer API a pre-read UTF-8 Buffer while libxmljs2 gets the string and pays the UTF-16 to UTF-8 conversion in its timed call even though it also accepts a Buffer. Buffer API vs pure-JS parsers fed strings: 2.1x, 3.4x and 3.3x over @rgrove/parse-xml; 3.2x, 6.3x and 3.9x over fast-xml-parser (ratios derived from page data). |
| **Workload** | DOM-tree parse of three XML fixtures (780 B, 35,562 B and 2,337,522 B) under Node.js, via the benchmark/ suite in the repo (cd benchmark && npm install && npm test). |
| **Metric** | throughput |
| **Hardware** | Apple M3 Max (Darwin arm64), Node.js v18.19.0 |
| **Compiler and flags** | Measured build (numbers unchanged since commit 9ed22d8, 2023-12-26, package v0.1.0): Emscripten, CI pinned EM_VERSION 3.1.44 but the local Apple M3 Max run does not state its version; libxml2 master 30d22be configured through gulpfile.babel.js (emconfigure autogen.sh --without-python --without-http --without-sax1 --without-modules --without-html --without-threads --without-zlib --without-lzma --disable-shared --enable-static, no explicit CFLAGS) and linked with emcc -s MODULARIZE -s ALLOW_MEMORY_GROWTH -s SINGLE_FILE and no -O level. Current HEAD differs: CFLAGS='-O2' and link flags -O2 -flto --closure 1 (binding/emcc.txt), EM_VERSION 5.0.2. Baseline libxmljs2 ^0.32.0 is a prebuilt native addon bundling libxml2 2.9.9 (vendor/libxml/include/libxml/xmlversion.h), flags not stated. Node.js v18.19.0. |
| **Adoption** | 54 stars; published on npm as libxml2-wasm |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/jameslan/libxml2-wasm) · [benchmark](https://github.com/jameslan/libxml2-wasm/blob/master/docs/performance.md) |

## Verdict

The repo's benny run (Node v18.19.0, Apple M3 Max, v0.1.0 build) parses 780 B, 35 KB and 2.3 MB fixtures into a DOM: the Buffer API reached 167,479 / 17,114 / 62 ops/s versus native libxmljs2 0.32 (libxml2 2.9.9) at 78,688 / 12,414 / 50 fed strings, and versus @rgrove/parse-xml at 78,790 / 5,049 / 19; the like-for-like String API rows (120,578 / 6,013 / 43) beat libxmljs2 only on the small file. First-party, single machine, numbers unchanged since 2023-12-26.

## Use it when

- You need a real libxml2 DOM (XPath 1.0, XSD/RelaxNG/DTD validation, C14N, XInclude) in a browser or in Node without a native addon or node-gyp toolchain.
- Node or serverless deployments where per-platform prebuilt native binaries (libxmljs2, libxmljs) break across libc, OS or Node versions; one wasm build runs everywhere Node 18+ runs.
- Parsing many small documents (under a few KB) from Buffers or Uint8Arrays: the measured Buffer-API row was 2.1x libxmljs2 and 2.1x @rgrove/parse-xml on the 780-byte file.
- Replacing pure-JS parsers (fast-xml-parser, xmldoc, @rgrove/parse-xml) when the input arrives as bytes and parse time dominates: 3.3-6.3x faster on the 35 KB and 2.3 MB files in the repo's run.

## Skip it when

- Your input is a JS string and documents are tens of KB or larger: the String API measured 0.48x (35 KB) and 0.86x (2.3 MB) of native libxmljs2 in the same run.
- Very large documents or streaming: no SAX or xmlTextReader API is exported, the whole tree must fit in a 32-bit wasm heap (binding/emcc.txt sets ALLOW_MEMORY_GROWTH without MAXIMUM_MEMORY, so Emscripten's default cap applies), and wasm memory grows but never shrinks.
- Code that walks the whole tree from JS: every property access (name, content, next, firstChild) is a JS-to-wasm call plus a UTF8ToString copy, so parse-plus-traverse can lose the edge that the parse-only benchmark shows over JS object trees.
- HTML parsing (built --without-html; issue #72 open), async resolution of XInclude or XSD imports (issues #143-145 open), or code that cannot guarantee dispose() calls.
- Teams wanting a libxmljs2-compatible API: porting means rewriting calls and adding explicit lifetime management.

## How it is fast

Parsing runs entirely inside libxml2's C parser (xmlCtxtReadMemory) compiled to wasm; parse() returns only a handle to the C tree, so no JS object is created per node until code asks for one. The Buffer API copies the UTF-8 bytes into the wasm heap with one HEAPU8.set and skips the UTF-16 to UTF-8 conversion that the String API (lengthBytesUTF8 + stringToUTF8) pays on every call. Against libxmljs2 it also carries less per-allocation work: libxmljs2 routes every libxml2 malloc/free through xmlMemMalloc/xmlMemFree wrappers that query xmlMemUsed() and report external memory to V8, plus per-node register/deregister callbacks, while the wasm build uses plain malloc and is configured --without-threads.

## Compared with alternatives

Pick it over sax-wasm when you need a full DOM with XPath, schema validation or C14N rather than a streaming event parser; pick sax-wasm for huge or streamed inputs where holding the whole tree in the wasm heap is not acceptable.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (libxml2 2.15.1 is compiled into the single-file module); building from source needs Emscripten (CI pins 5.0.2) and the libxml2 git submodule |
| **Minimum toolchain** | Node.js 18+, Chrome/Edge 89+, Safari 15+ (ES module with top-level await); TypeScript typings included |
| **Platforms** | any JavaScript runtime with WebAssembly and ES modules; CI runs Node 18/20/22/24 on Linux, macOS and Windows |
| **Thread safety** | not documented; libxml2 is configured --without-threads and each module instance has one wasm heap, so do not share documents across workers |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the headline: benchmark/index.mts gives the Buffer API a pre-read UTF-8 Buffer but passes libxmljs2 the JS string, although libxmljs2's FromXml (src/xml_document.cc) takes a Buffer too; on like-for-like strings the wasm build wins only on the 780-byte file. The pure-JS rows compare a parse that builds no JS objects with parsers that build full JS object trees.
- Baseline overhead not of wasm's making: libxmljs2 0.32 installs xmlMemSetup wrappers (xmlMemMalloc plus an xmlMemUsed() check and Nan::AdjustExternalMemory) and node register/deregister callbacks, and its documents are freed by GC finalizers inside the timed loop while libxml2-wasm calls dispose(); part of the small-file win is binding design rather than codegen.
- Published numbers come from v0.1.0 (Dec 2023: libxml2 master of late 2023, no -O level at link, unstated local Emscripten) and were not re-run for the current -O2 -flto --closure 1 build on libxml2 2.15.1 and Emscripten 5.0.2.
- Node and attribute wrappers hold raw pointers into the wasm heap: using them after the owning document is disposed is a use-after-free (issue #137 fixed one such path); FinalizationRegistry frees forgotten documents eventually, but the README still calls dispose() required.

## Known shortcomings

- The headline Buffer API rows feed pre-read UTF-8 bytes to the wasm side while libxmljs2 receives a JavaScript string and converts it inside the timed call; fair string-vs-string rows give 1.53x on 780 B and slower on 35 KB (0.48x) and 2.3 MB (0.86x); numbers from the 2023-12-26 v0.1.0 build with no -O at link and the Emscripten version unstated; the baseline bundles libxml2 2.9.9 against a late-2023 master on the wasm side.
- Harness flaw confirmed: benchmark/index.mts gives the Buffer API a pre-read UTF-8 Buffer while libxmljs2 gets the JS string although its FromXml also takes a Buffer; on like-for-like strings the wasm build wins only on the 780-byte file. Baseline overhead not of wasm's making: libxmljs2 0.32 routes every libxml2 allocation through xmlMemSetup wrappers (xmlMemMalloc, xmlMemUsed() check, Nan::AdjustExternalMemory) plus per-node callbacks, and its documents are freed by GC finalizers inside the timed loop. Pure-JS rows compare a parse that builds no JS objects against full JS trees. Numbers are from the v0.1.0 build; HEAD now ships libxml2 2.15.1 at -O2 -flto on Emscripten 5.0.2, unmeasured.

## Caveats and trade-offs

First-party benchmark (docs/performance.md, numbers unchanged since 2023-12-26). Harness asymmetry: benchmark/index.mts passes the Buffer API a pre-read UTF-8 Buffer but passes libxmljs2 the JS string, so libxmljs2's timing includes UTF-16 to UTF-8 conversion although its fromXml also takes a Buffer; on like-for-like string input libxml2-wasm is faster only on the 780-byte file and slower than native libxmljs2 on the 35 KB (0.48x) and 2.3 MB (0.86x) files. libxml2-wasm calls dispose() on each document while libxmljs2 documents are freed by GC finalizers inside the timed loop. Version gap: the wasm side was built from libxml2 master 30d22be (late 2023) while libxmljs2 0.32.x bundles libxml2 2.9.9, so part of the gain may come from newer libxml2 rather than the binding. The measured build predates the current -O2/-flto/--closure flags (no -O at link then); the local Emscripten version is not stated and libxmljs2 is a prebuilt binary with unstated flags. Single machine, Node 18, no warm-up or iteration policy stated beyond benny defaults. The bundled libxml2 carries its own license (LICENSE.libxml2).

ES module only; needs Node.js 18+ or Chrome/Edge 89+, Safari 15+ (README). libxml2 is built without the HTML parser, SAX1, catalogs, threads, modules and debug support. The String API converts UTF-16 to UTF-8 on every call; the docs recommend the Buffer API for speed. Wrapper licence is MIT and the bundled libxml2 keeps its own notice (LICENSE.libxml2).

## Maintenance

Actively maintained (last commit 2026-10-05, npm latest 0.7.2 released 2026-09-07, 54 stars) under MIT with libxml2's own notice bundled, while its main native competitor libxmljs2 is marked no longer maintained; usable as a dependency today, but the benchmark has not been refreshed since v0.1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** Benchmark code is public (benchmark/index.mts, benny) and the CPU is stated (Apple M3 Max, Node v18.19.0), but the headline Buffer-API rows hand libxml2-wasm pre-encoded UTF-8 bytes while libxmljs2, which also accepts a Buffer (src/xml_document.cc FromXml), is fed a JS string and converts it inside the timed call; the like-for-like String API rows lose to native on the 35 KB and 2.3 MB files. The numbers have been unchanged since commit 9ed22d8 (2023-12-26, v0.1.0), whose build used no optimisation flag at link and an unstated local Emscripten version, not the HEAD flags the record lists, so these are first-party numbers short of A.
- **Verifier notes:** Real wasm binding with public benchmark code, but the headline 2.1x/1.4x/1.2x over native libxmljs2 compares a no-conversion Buffer path against a string path; the fair String-vs-string rows show it slower than native on medium and large documents. Measured build flags (Dec 2023, v0.1.0) differ from the HEAD flags the record cited; metadata checked: MIT wrapper, 54 stars, last commit 2026-10-05, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-104 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/benchmark/index.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/benchmark/package.json>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/binding/emcc.txt>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/9ed22d8/docs/performance.md>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/272b015/docs/performance.md>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/9ed22d8/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/9ed22d8/package.json>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/9ed22d8/gulpfile.babel.js>
  - <https://github.com/jameslan/libxml2-wasm>
  - <https://github.com/jameslan/libxml2-wasm/commits/master>
  - <https://github.com/jameslan/libxml2-wasm/commits/master/docs/performance.md>
  - <https://github.com/jameslan/libxml2-wasm/tree/9ed22d8>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/HEAD/src/xml_document.cc>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/src/xml_document.cc>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/lib/document.js>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/vendor/libxml/include/libxml/xmlversion.h>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/package.json>
- **Sources the enricher read:**
  - <https://github.com/jameslan/libxml2-wasm>
  - <https://github.com/jameslan/libxml2-wasm/issues?q=is%3Aissue>
  - <https://github.com/jameslan/libxml2-wasm/issues?q=is%3Aissue&page=2>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/benchmark/index.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/benchmark/package.json>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/binding/emcc.txt>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/binding/exported-functions.txt>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/src/document.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/src/libxml2.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/src/disposable.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/src/nodes.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/src/index.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/src/utils.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2-wasm/HEAD/src/libxml2raw.d.mts>
  - <https://raw.githubusercontent.com/jameslan/libxml2/f52e859efe97cf3f0b78d731976402748878529a/VERSION>
  - <https://registry.npmjs.org/libxml2-wasm>
  - <https://github.com/marudor/libxmljs2>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/README.md>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/index.js>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/lib/document.js>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/src/xml_document.cc>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/src/libxmljs.cc>
  - <https://raw.githubusercontent.com/marudor/libxmljs2/v0.32.0/binding.gyp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jameslan/libxml2-wasm`) · [data/wave13/enrich/raw/github_com_jameslan_libxml2_wasm.json](../../../data/wave13/enrich/raw/github_com_jameslan_libxml2_wasm.json) (enrichment confidence 0.8)

</details>
