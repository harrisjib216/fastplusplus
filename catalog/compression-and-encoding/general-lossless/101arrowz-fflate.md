# fflate

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript` · `MIT` · 🟢 active

> Pure-JavaScript DEFLATE/gzip/zlib/ZIP codec, up to 25% faster decode and 50% faster encode than pako.

| | |
|---|---|
| **Beats** | pako (JavaScript port of zlib); README also says its compressor beats Info-ZIP and often zlib's ratio |
| **Claimed result** | README table (pako = 1x): decompression 'Up to 25% faster', compression 'Up to 50% faster'; text says about 25% faster than UZIP.js. Sync ZIP compression 'compresses both more quickly and with a higher compression ratio than most compression software (even Info-ZIP, a C program)'; async mode 'over 3x the performance of virtually any other utility'. Against native zlib (Node bindings) the README itself says fflate is 'around 30% slower in decompression and 10% slower in compression'. |
| **Workload** | DEFLATE, gzip, zlib and ZIP compression and decompression in JavaScript (Node and browsers) |
| **Metric** | throughput |
| **Adoption** | 3.0k stars |
| **Last commit** | 2026-05-16 |
| **Links** | [repository](https://github.com/101arrowz/fflate) · [benchmark](https://github.com/101arrowz/fflate#readme) |

## Verdict

First-party README table rates fflate against pako as up to 25% faster in decompression and up to 50% faster in compression, with no data, runtime version, CPU or flags published; npm test writes timings to test/results but none are checked in. The same README states it is about 30% slower than native zlib to decompress and 10% slower to compress.

## Use it when

- Browser or edge-runtime code that needs synchronous, in-memory gzip/zlib/DEFLATE (CompressionStream is stream-only and has no level control).
- Replacing pako in a JS bundle: decompression-only build is about 3 kB minified versus 45.6 kB for pako.
- Creating or reading ZIP archives client-side, with per-file levels and a filter to skip entries before inflating.
- Multi-file ZIP compression of large files where the async API can use several worker threads.
- A C++ host that already embeds a JS engine (V8, QuickJS) and must keep compression inside script code.

## Skip it when

- Any native C or C++ program: by the README's own figures fflate is about 30% slower than native zlib in decompression and 10% slower in compression, and the catalogue's zlib-ng, libdeflate and ISA-L are much faster than zlib itself.
- Node services that can use the built-in zlib bindings; the author recommends those for best performance.
- Untrusted input where integrity matters: the sync decoders do not verify the gzip CRC-32, the zlib Adler-32 or ZIP entry CRCs (read in src/index.ts), so corruption is not detected.
- Streaming Deflate/Zip/ZipDeflate at levels 2-9 on v0.8.x: open issues #260 and #282 (May and June 2026) report output with invalid back-references that zlib rejects; zipSync and deflateSync are not affected per the reporters.
- Small payloads (under about 50 kB) through the async API: worker start-up costs about 50 ms per function.

## How it is fast

Derived from UZIP.js rather than a line-by-line zlib port: the inflater decodes through flat 2^maxbits lookup tables (one typed-array read per symbol, 16-bit bit-reader), and the deflater uses a hash-chain LZ77 matcher with a 'nice length' early exit and a trick that re-hashes on the rarest 2-byte sequence inside the current match to cut chain walks. Everything works on typed arrays with closures avoided in hot loops (the source notes 'closures have awful performance'), and gzip/ZIP decompression preallocates the output from the stored size so the buffer is never grown. The async API parallelises multi-file ZIP across workers.

## Compared with alternatives

Only when the code must stay in JavaScript: every C/C++ sibling (zlib-ng, libdeflate, miniz, Wuffs) beats it and native zlib on raw speed, and Zippy plays the same role for Nim. Pick fflate over pako-style JS ports, not over native libraries.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | Any ES3-level JavaScript engine with typed arrays (README); async API needs Worker or Node worker_threads; TypeScript typings shipped |
| **Platforms** | any JavaScript runtime (browsers back to IE11 for workers, Node, Deno, Bun); not callable from C++ without an embedded JS engine |
| **Thread safety** | Sync functions are pure over their inputs; stream objects are single-owner; async APIs run on separate workers. |
| **Drop-in for the baseline** | partial: produces and reads the same formats as pako/zlib, but the API differs from pako's (different function names, Uint8Array only, callbacks for async) |

## Gotchas

- gunzipSync allocates the output from the 4-byte ISIZE trailer and unzipSync from the ZIP header size, and a caller-supplied buffer is never grown; from the source, a wrong or wrapped (over 4 GiB) size leads to silently truncated output since typed-array writes past the end are dropped and no checksum is checked.
- Issue #298 (Sept 2026, open): unzipSync treats ZIP64 0xFFFFFFFF size sentinels as real sizes when there is no ZIP64 end-of-central-directory locator and tries a \~4 GiB allocation on a 33 MiB file; the streaming Unzip handles it. A tiny crafted archive can trigger large allocations the same way.
- The sync API has no output-size cap, so decompression bombs must be limited by the caller (unzip filter on originalSize helps only for ZIP).
- Async APIs serialise functions into workers by name-recovery tricks; issues #288 (minified builds), #266 (Deno) and #294 (Firefox WebExtensions) report breakage in some bundlers and sandboxes.

## Known shortcomings

- JavaScript, not C++. Only 'up to' percentages vs pako. The README itself says about 30% slower decompress and 10% slower compress than native zlib.
- Sync decoders (gunzipSync, unzlibSync, unzipSync) never check CRC-32 or Adler-32. The output buffer is sized from the ISIZE trailer or ZIP header and never grown, so a wrong or wrapped size gives silently truncated output. Open issues #260 and #282 (2026): streaming Deflate at levels 2-9 emits invalid back-references that zlib rejects. Issue #298: a ZIP64 sentinel in unzipSync causes an about 4 GiB allocation; no output cap, so bomb risk. Async breaks in minified builds, Deno and Firefox extensions (#288, #266, #294). Pure JS; needs an embedded JS engine from C++.

## Caveats and trade-offs

The win is against pako (a JS port of zlib), not native zlib: the README states fflate is about 30% slower than native zlib in decompression and 10% slower in compression, and that the native CompressionStream API ranges from 30% faster to 10% slower. Only 'up to' percentages, no data, Node version, CPU or flags; results of npm test (test/results) are not published. The 'beats Info-ZIP' and '3x' statements are unsupported by tables. Worth listing as the fast pure-JS option where native zlib is unavailable (browsers without a sync API).

Pure JavaScript, so usable from C++ only through an embedded JS engine; 8 kB bundle; async mode uses Web Workers with about 50 ms start overhead per function; the README says outputs are checked to be no more than 5% larger than competitors at max compression.

## Maintenance

Active (v0.8.3, last commit May 2026) and MIT-licensed (0BSD for SheetJS), with about 3.0k stars, but several data-corruption reports against the streaming compressor from 2026 are still open with no maintainer reply visible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README gives only 'up to 25%/50% faster than pako' percentages with no data, runtime, CPU or flags; npm test writes metrics to test/results but none are published.
- **Verifier notes:** Kept as a JS-ecosystem entry: faster than pako, but by its own README slower than native zlib, which matters for a catalog benchmarked against zlib. Metadata checked: MIT (SheetJS-derived part 0BSD), about 3.0k stars, not archived, not a fork; last commit 2026-05-16 (v0.8.3).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party claim
- **Pages the verifier opened:**
  - <https://github.com/101arrowz/fflate>
  - <https://github.com/101arrowz/fflate/commits/master>
  - <https://raw.githubusercontent.com/101arrowz/fflate/HEAD/README.md>
  - <https://raw.githubusercontent.com/101arrowz/fflate/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/101arrowz/fflate/HEAD/README.md>
  - <https://raw.githubusercontent.com/101arrowz/fflate/HEAD/package.json>
  - <https://raw.githubusercontent.com/101arrowz/fflate/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/101arrowz/fflate/HEAD/src/node-worker.ts>
  - <https://raw.githubusercontent.com/101arrowz/fflate/HEAD/src/worker.ts>
  - <https://github.com/101arrowz/fflate/issues?q=is%3Aissue+crc>
  - <https://github.com/101arrowz/fflate/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/101arrowz/fflate/issues/260>
  - <https://github.com/101arrowz/fflate/issues/282>
  - <https://github.com/101arrowz/fflate/issues/298>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/101arrowz/fflate`) · [data/wave9/enrich/raw/github_com_101arrowz_fflate.json](../../../data/wave9/enrich/raw/github_com_101arrowz_fflate.json) (enrichment confidence 0.7)

</details>
