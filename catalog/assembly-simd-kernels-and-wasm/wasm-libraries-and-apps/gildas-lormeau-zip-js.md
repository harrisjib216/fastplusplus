# zip.js (@zip.js/zip.js WebAssembly zlib codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `JavaScript with bundled WebAssembly zlib and AES codecs` · `BSD-3-Clause` · 🟢 active

> ZIP library whose bundled WebAssembly zlib inflates about 2x faster than pako/jszip and its own JS port.

| | |
|---|---|
| **Beats** | zip.js's own pure-JavaScript zlib port, jszip (pako) and fflate; also native CompressionStream and node:zlib shown for reference |
| **Claimed result** | Head-to-head (benchmarks/bench.js, fresh Node v26.10.0 process per row, median of 3, level 6): decompress 20 MB text WASM zlib 71 ms vs zip.js pure-JS zlib 155 ms, jszip/pako 140 ms, fflate 116 ms; compress 20 MB incompressible WASM 460 ms vs pure-JS 787 ms, jszip 854 ms (fflate 298 ms is faster); compress 20 MB text WASM 1098 ms vs pure-JS 1229 ms, jszip 1753 ms (fflate 908 ms is faster at 2% larger output); 5,000 x \~2 KB files compress WASM 551 ms vs pure-JS 962 ms, jszip 846 ms (fflate 278 ms is faster). Codec alone (benchmarks/bench-codecs.js, in-process, warm): WASM inflate 41 ms (483.7 MB/s) vs Node DecompressionStream 56 ms, pure-JS 108 ms, fflate 122 ms, i.e. 27% faster than Node's native zlib stream; WASM deflate level 5 493 ms for 6,562,182 bytes vs fflate level 5 534 ms for 6,648,574 bytes; at level 6 WASM 1025 ms is slower than CompressionStream 695 ms. AES-256 WinZip entry, 20 MB stored, write/read (benchmarks/bench-aes.js): WebAssembly 134/135 MB/s vs JavaScript engine 119/108 on Node, 119/121 vs 115/117 on Bun, 124/124 vs 144/133 on Deno (JS faster there); browsers WASM 125/125 vs JS 79/79 (Firefox 156) and 136/138 vs 104/104 (Chrome 153). |
| **Workload** | Compress/decompress 20 MB of compressible text, 20 MB incompressible data and 5,000 x \~2 KB text files in Node, each (library, operation, workload) in a fresh process, median of 3 runs. |
| **Metric** | throughput |
| **Hardware** | Apple M2, 8 cores (4 performance + 4 efficiency), 16 GB RAM, macOS 27.0 arm64 |
| **Compiler and flags** | JavaScript baselines and host code on Node.js v26.10.0 (also Bun 1.4.2, Deno 2.9.7; Firefox 156 and Chrome 153 for the browser AES table). The WebAssembly codec is the committed binary lib/core/streams/zlib-wasm/zlib-streams.wasm, built with Emscripten from gildas-lormeau/zlib-streams (madler/zlib submodule plus chunked-inflate, 64-bit compare256 and braided-CRC options): emcc with WASM_CFLAGS -O2 -flto -DDYNAMIC_CRC_TABLE -DBUILDFIXED -DZ_SOLO -DDEFLATE_COMPARE256_64LE -DUSE_ZLIB_RABIN_KARP_ROLLING_HASH -DINFLATE_CHUNK_GENERIC -DINFLATE_CHUNK_READ_64LE, then -Oz -flto -s STANDALONE_WASM=1, then wasm-opt -Oz --enable-bulk-memory-opt (zlib-streams Makefile, target dist/zip-module.wasm). Emscripten version not stated; Makefile read at HEAD, not at the commit that produced the vendored binary. |
| **Adoption** | 3.9k stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/gildas-lormeau/zip.js) · [benchmark](https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/BENCHMARKS.md) |

## Verdict

The author ran zip.js 2.19.0 on Node v26.10.0 on an Apple M2 (2026-09-30), one fresh process per row, median of 3, every library at its own level 6. The WASM zlib backend decompressed a 20 MB text archive in 71 ms vs 155 ms (zip.js pure-JS port), 140 ms (jszip/pako) and 116 ms (fflate), and compressed 20 MB of incompressible data in 460 ms vs 787 and 854 ms; warm, codec-only inflate took 41 ms vs 56 ms for Node's DecompressionStream. It loses to native zlib on compression and to fflate on incompressible data and small files.

## Use it when

- Browser, Deno, Bun or Node apps that need real ZIP features (Zip64, AES, split archives, streaming) with a faster bundled codec than jszip/pako: 20 MB text read 71 ms vs 140 ms jszip and 155 ms for zip.js's pure-JS port.
- Non-default compression levels, which bypass CompressionStream: on Node, WASM level 5 took 512 ms vs 691 ms for the level-6 native stream (7% more bytes), level 1 runs at about 116 MB/s.
- Archives of many small entries: 5,000 x \~2 KB files compressed in 551 ms vs 731 ms through CompressionStream and read in 342 ms vs 485 ms, because the per-entry cost of a WASM stream is lower than a native one.
- Hosts without CompressionStream, or output that must not depend on the host's zlib (useCompressionStream: false gives madler-identical bytes on every runtime).
- AES-encrypted entries in browsers: WASM 125-138 MB/s vs 79-104 MB/s for the JavaScript engine (Firefox 156, Chrome 153).

## Skip it when

- Large entries at the default level on Node, Bun or Deno: native CompressionStream and node:zlib compress 20 MB of text in 678-730 ms vs 1098 ms, and concurrent add() spreads native streams across the libuv threadpool (602 ms vs 3402 ms for WASM on 8 x 8 MB) while the WASM codec stays on one thread.
- Many small files where fflate is acceptable: fflate compressed the 5,000-file set in 278 ms and read it in 101 ms vs 551 ms and 342 ms for the WASM backend, and won on incompressible data (298 vs 460 ms).
- Memory-constrained hosts: the zip.js rows had the highest peaks (139 MB vs 68 MB for fflate compressing 20 MB of text; 171 MB vs 97 MB decompressing).
- Short-lived processes or tiny archives: a fresh process pays about 20 ms of module instantiation before the first byte.
- Throughput-critical encryption: the AES kernel is software (WebAssembly has no AES instructions), 119-138 MB/s against 9.4 GB/s for OpenSSL with ARMv8 AES on the same M2, and on Deno the JavaScript engine is faster (144/133 vs 124/124 MB/s).

## How it is fast

The codec is madler zlib compiled to a standalone WebAssembly module with Emscripten (-Oz -flto, then wasm-opt -Oz), with Chromium zlib's chunked inflate fast path (INFLATE_CHUNK_GENERIC with 64-bit bit-buffer reads), 8-bytes-at-a-time match extension in longest_match (DEFLATE_COMPARE256_64LE) and an 8-byte braided CRC-32 that the Makefile says is about 12x faster than zlib's Z_SOLO byte loop. Compiled C with native 64-bit integer ops beats JIT-compiled JavaScript ports (pako, zip.js's port, fflate) and, warm, Node's DecompressionStream on inflate. No WebAssembly SIMD is used (issue #677 measured -msimd128 within noise), and the deflate output stays byte-identical to madler zlib because the Rabin-Karp hash is kept.

## Compared with alternatives

Pick zip.js when you need a full ZIP container (Zip64, AES, streaming, worker pool) with the WASM codec bundled; for raw deflate/gzip buffers without a ZIP container, fast-pako (4.2-5.8x pako on inflate) or @mtcute/wasm are narrower pako replacements, and @bytedance/tar-wasm covers tar rather than zip.

## Integration

| | |
|---|---|
| **Form** | module (npm @zip.js/zip.js and JSR, ES module and CommonJS builds; the WASM binary ships with the package and is also exported as dist/zip-module.wasm) |
| **Dependencies** | none at runtime (package.json lists only devDependencies) |
| **Minimum toolchain** | Node &gt;= 18, Deno &gt;= 1.0, Bun &gt;= 0.7 (package.json engines); browsers with WebAssembly and Web Streams |
| **Platforms** | any JavaScript runtime with WebAssembly (Node, Deno, Bun, browsers); falls back to the JavaScript engine where the module cannot load, e.g. a Content Security Policy without 'wasm-unsafe-eval' |
| **Thread safety** | The WASM codec runs on the calling thread (or inside zip.js Web Workers when useWebWorkers is on); the module heap is fixed (16.9 MB per issue #677), so the number of streams alive at once is bounded and exhaustion fails with Z_MEM_ERROR 'allocation failed'. |
| **Drop-in for the baseline** | partial — replaces jszip/pako only by moving to zip.js's ZipWriter/ZipReader API; the standalone zlib-streams classes mirror the CompressionStream interface but not pako's |

## Gotchas

- Backend choice is implicit: the default level 6 runs the host CompressionStream when it exists, any other level or useCompressionStream: false runs the WASM codec, and a module that fails to load falls back silently (the benchmark adapter's own comment warns that a failed initModule makes zip.js measure the native stream instead), so check which codec your configuration actually runs.
- CRC-32 is not verified on read by default (checkCrc32 defaults to false). Issue #661 shows why it matters: Deflate64 entries came back truncated with a bad CRC-32 and no error until v2.8.28. Turning the check on costs about 7 ms per 20 MB on the WASM codec.
- The zlib-streams driver rejects trailing data after the end of a stream and does not decode concatenated gzip members; AES authentication codes are checked by default (checkAuthenticationCode true), so the AES read numbers include HMAC verification.
- Harness notes: the numbers come from zip.js 2.19.0 while HEAD is 2.23.0, and the corpus is synthetic: seeded word salad from a vocabulary of about 170 English and JavaScript words, not real files. BENCHMARKS.md says the codec script does one warmup run, but bench-codecs.js's measure() has none: its median of 3 includes the cold run. The WASM module was already warm from the compression rows before the inflate rows ran, so this does not change the 41 ms vs 56 ms inflate result.

## Known shortcomings

- The WASM zlib is slower than CompressionStream, node:zlib and fflate on most compress rows and wins only against the pure-JavaScript port and pako (plus warm inflate 27% faster than DecompressionStream); Emscripten version unstated (flags public in gildas-lormeau/zlib-streams); AES figures on Node are 134/135 vs 119/108 MB/s and JavaScript is faster on Deno.
- Enricher: BENCHMARKS.md says the codec script runs one warm-up but bench-codecs.js measure() has none (the median of 3 includes the cold run; the 41 vs 56 ms inflate result stands); measured on 2.19.0 (HEAD 2.23.0) on a synthetic word-salad corpus; checkCrc32 defaults to false and issue #661 shows Deflate64 entries silently truncated until 2.8.28; the WASM heap is fixed at 16.9 MB (#677); the codec silently falls back to another backend if the module fails to load; AES is software only (134 MB/s vs 9.4 GB/s OpenSSL with ARMv8 AES). gildas-lormeau/zlib-streams is the same codec (would be a duplicate).

## Caveats and trade-offs

The wasm backend is not the fastest option overall: native CompressionStream and node:zlib beat it on compression (text 678-730 ms vs 1098 ms) and fflate beats it on incompressible data (298 ms) and on small files (278 ms compress, 101 ms decompress); on Node zip.js uses CompressionStream by default at level 6, so the WASM codec runs only for other levels, with useCompressionStream: false, or where no native stream exists. The win is WASM versus the JS port of the same codec and versus pako/fflate, plus a warm inflate 27% faster than Node's DecompressionStream. No decompression row verifies CRC-32 (page says enabling it costs about 7 ms per 20 MB on WASM). Fresh-process rows include about 20 ms of wasm instantiation. Author-run on one Apple M2 machine; levels are not equal work across libraries, which the page handles by printing output sizes. The AES figures in the original record (131 vs 114 MB/s, release 2.15.0 page on jsr.io) are not on BENCHMARKS.md and were replaced with the page's numbers.

WASM module instantiation costs about 20 ms per fresh process; peak memory is higher than fflate (139 MB vs 68 MB delta on the 20 MB text compress); the codec is used only when native CompressionStream is unavailable or the wasm backend is configured.

## Maintenance

Actively maintained (last commit 2026-10-03, v2.23.0 at HEAD, frequent releases), BSD-3-Clause with no runtime dependencies; the WASM codec is a committed binary built from gildas-lormeau/zlib-streams (madler zlib plus Chromium inflate/deflate options, -Oz).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: harness is public (benchmarks/bench.js, run-one.js, bench-codecs.js, bench-aes.js, run logs in benchmarks/results), runtime (Node.js v26.10.0, Bun 1.4.2, Deno 2.9.7) and CPU (Apple M2) are stated, the measured wasm is the committed binary lib/core/streams/zlib-wasm/zlib-streams.wasm, and its Emscripten build flags are public in the gildas-lormeau/zlib-streams Makefile (-Oz -flto, wasm-opt -Oz). Only the Emscripten version is unstated, which the committed binary makes moot for reproduction; demote to C if a pinned compiler version is required.
- **Verifier notes:** Every compression and decompression number in the record appears in BENCHMARKS.md; the AES numbers came from another page and were replaced. Harness (run-one.js, bench-codecs.js) times the operation fairly per library in isolated processes; the wasm codec is zlib-streams (same author, madler zlib compiled by Emscripten). Metadata confirmed: BSD-3-Clause, 3.9k stars, last commit 2026-10-03, not a fork; tier upgraded C to A on public build flags plus committed binary (Emscripten version unstated).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-91 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/BENCHMARKS.md>
  - <https://github.com/gildas-lormeau/zip.js>
  - <https://github.com/gildas-lormeau/zip.js/commits/master>
  - <https://github.com/gildas-lormeau/zip.js/tree/master/lib>
  - <https://github.com/gildas-lormeau/zip.js/tree/master/lib/core/streams/codecs>
  - <https://github.com/gildas-lormeau/zip.js/tree/master/lib/core/streams/zlib-wasm>
  - <https://github.com/gildas-lormeau/zip.js/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/bench.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/bench-codecs.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/run-one.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/package.json>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/lib/zip-module-wasm-base.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/rollup.config.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/package.json>
  - <https://github.com/gildas-lormeau/zlib-streams>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/Makefile>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/README.md>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/README.md>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/package.json>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/index.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/index.d.ts>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/lib/zip-module-wasm-base.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/lib/zip-fs-wasm.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/lib/core/configuration.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/lib/core/streams/zlib-wasm/zlib-streams-loader.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/bench.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/run-one.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/bench-codecs.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/bench-aes.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/package.json>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/adapters/zipjs.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/adapters/fflate.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/adapters/jszip.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/lib/settings.js>
  - <https://raw.githubusercontent.com/gildas-lormeau/zip.js/HEAD/benchmarks/lib/corpus.js>
  - <https://github.com/gildas-lormeau/zip.js/commits/master>
  - <https://github.com/gildas-lormeau/zip.js/issues?q=is%3Aissue+wasm>
  - <https://github.com/gildas-lormeau/zip.js/issues/677>
  - <https://github.com/gildas-lormeau/zip.js/issues/661>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/README.md>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/Makefile>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/gildas-lormeau/zlib-streams/HEAD/LICENSE>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gildas-lormeau/zip.js`) · [data/wave13/enrich/raw/github_com_gildas_lormeau_zip_js.json](../../../data/wave13/enrich/raw/github_com_gildas_lormeau_zip_js.json) (enrichment confidence 0.8)

</details>
