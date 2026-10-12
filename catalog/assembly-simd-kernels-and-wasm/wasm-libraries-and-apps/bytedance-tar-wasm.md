# @bytedance/tar-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust compiled to WebAssembly (Cargo.toml in repo) with a TypeScript wrapper` · `MIT` · 🔴 abandoned

> Rust tar crate compiled to WebAssembly behind a TarBuilder JS class; builds in-memory tars 50-160x faster than tar-js and tarts.

| | |
|---|---|
| **Beats** | tar-js and tarts (pure-JavaScript tar writers on npm) |
| **Claimed result** | README: 'it can be 50-160x faster than existing JavaScript implementations on NPM'. Printed run: @bytedance/tar-wasm 24.63 ms; tar-js 3943.50 ms (160.1x slower); tarts 1251.60 ms (50.8x slower). |
| **Workload** | Building an uncompressed tar archive in memory from 1,001 generated lorem-ipsum text files (3 paragraphs each) in Node.js (examples/nodejs-benchmark/bench.ts); each library runs once, cold, one after the other in the same process, with no warm-up, repetitions or output comparison. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8269CY @ 2.50GHz |
| **Compiler and flags** | wasm-pack build --target nodejs (Makefile) with the Cargo release profile opt-level = "s" (Cargo.toml); rustc, wasm-pack, wasm-bindgen and Node versions not stated; benchmark run via ts-node |
| **Adoption** | 106 stars |
| **Last commit** | 2023-01-24 |
| **Links** | [repository](https://github.com/bytedance/tar-wasm) · [benchmark](https://github.com/bytedance/tar-wasm) |

## Verdict

With the repo's Node.js script (ts-node; Node, rustc and wasm-pack versions not stated) on a Xeon Platinum 8269CY, building one in-memory tar of 1,001 generated lorem-ipsum text files took 24.6 ms with tar-wasm, against 3,943.5 ms for tar-js 0.3.x (160x) and 1,251.6 ms for tarts 2.0.x (51x), one cold run each. Both baselines copy the whole archive on every append, so the ratio reflects quadratic versus linear buffer growth more than WebAssembly.

## Use it when

- A web app that packs hundreds to thousands of in-memory files (exports, bundles for download or upload) and currently uses tar-js or tarts.
- Isomorphic code that needs the same tar writer in a bundler-built browser app and in Node.js, with total archive size comfortably below the wasm32 memory limit.
- Large archives built inside a Web Worker or worker_threads, as the README recommends, to keep the main thread responsive.
- Producing a .tar.gz by piping finish() output through the platform CompressionStream('gzip') rather than the built-in set_gzip.

## Skip it when

- You need to read, list or extract archives: issue #2 (read and write support) has been open since August 2022.
- You need real metadata: every entry gets mode 0777, uid/gid 0 and mtime 0, and there is no way to add directories or links.
- Very large or streamed archives: the whole archive is held in a Rust Vec inside wasm linear memory and then copied out to JS, so peak memory is several times the archive size; use a streaming writer such as tar-stream or node-tar (neither was benchmarked against it).
- Server-side Node.js archiving to disk, where node-tar or tar-stream are the standard choices and no comparison exists.
- Anything that needs maintenance or security updates: the repository was archived on 2025-07-21 and the last npm release (0.1.7) is from 2022-10-27.

## How it is fast

About 50 lines of Rust wrap the tar crate's `Builder<Vec<u8>>` (tar 0.4.38): each file is copied into wasm memory, gets a 512-byte GNU header and is appended to a Vec that grows geometrically, so the total work is linear in archive size. The two JS baselines reallocate and copy the whole archive for every appended file (tar-js `extend` plus a byte-by-byte zero fill; tarts concatenates with `reduce`), which is quadratic. The speedup is therefore mostly algorithmic buffer management rather than wasm compute; the crate is even built with `opt-level = "s"` (size).

## Compared with alternatives

No other tar writer is catalogued in this category; siblings such as hash-wasm or fast-pako win by moving compute-bound kernels to wasm, while tar-wasm wins mainly through linear buffer growth, so pick it only to replace tar-js or tarts for in-memory archive building, and pair it with fast-pako or CompressionStream for compression.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (tar 0.4.38, yazi 0.1.4, wasm-bindgen 0.2.82 and console_error_panic_hook are compiled into the wasm); rebuilding needs Rust, wasm-pack and jq |
| **Minimum toolchain** | any JS runtime with WebAssembly; a bundler that handles wasm imports for the ESM build, or Node.js for the CommonJS build (versions not documented) |
| **Platforms** | browsers and Node.js (wasm32); browser use shown only by an unpublished examples/nextjs-benchmark page |
| **Thread safety** | not documented; a TarBuilder lives in one wasm instance and is single-threaded, so use one builder per worker |
| **Drop-in for the baseline** | no |

## Gotchas

- set_gzip(true) compresses with yazi Format::Zlib, so the output is a zlib (RFC 1950) stream, not gzip; gunzip and `tar -xz` will reject it. Use CompressionStream('gzip') instead, as the README suggests.
- add_file throws for absolute paths or `..` components (tar crate: 'paths in archives must be relative' / 'must not have `..`'); names longer than 100 bytes are written with a GNU ././@LongLink entry rather than POSIX pax headers.
- finish() takes the builder by value (Rust `self`), so the JS object cannot be reused afterwards; wasm linear memory grown for a big archive is not returned while the module instance lives.
- Benchmark harness flaw: both baselines are quadratic writers, so the 50-160x mostly measures their O(n^2) buffer growth. Each library also runs once, cold, in sequence, with no warm-up, no repeats and no output check (the only test asserts the archive length is &gt; 0). The wasm module loads through the top-level import before the timer starts, the README output comes from an earlier bench.ts (labels differ), and no browser numbers are shown despite 'depending on the browser'.

## Known shortcomings

- Both JavaScript baselines grow buffers quadratically (tar-js extend per file, tarts reduce concat), so the 50-160x mostly measures O(n^2) copying in the baselines; single cold run, versions unstated; set_gzip emits zlib, not gzip. Archived 2025-07-21.
- Enricher: the 50-160x is mostly baseline buffer growth: tar-js extend (with a byte-loop zero fill) and the tarts reduce-concat copy the whole archive per file (quadratic); single cold run each with no warm-up and no output check (the test asserts only len &gt; 0); no browser numbers; set_gzip emits zlib rather than gzip; mode 0777, uid/gid 0 and mtime 0 are fixed and absolute or '..' paths throw; archived 2025-07-21. Retiered to D.

## Caveats and trade-offs

Single cold run of each library on small text files, results from 'my machine' (Xeon Platinum 8269CY), Node and toolchain versions not stated; the README output was printed by an earlier version of bench.ts (labels differ from the current script). Both baselines are quadratic writers: tar-js 0.3.0 (lib/utils.js extend) allocates a buffer just large enough, rounded to 10,240 bytes, zero-fills it with a byte-by-byte JS loop and copies the whole archive, up to twice per appended file; tarts 2.0.1 (tarts.js) builds the archive with reduce, allocating a new Uint8Array of size a+b and copying the whole archive for every file. tar-wasm wraps the Rust tar crate (tar 0.4.38) over a Vec&lt;u8&gt; with amortized growth, so the 50-160x mostly measures the baselines' O(n^2) buffer growth; widely used JS tar writers (tar-stream, node-tar) were not compared. The README asterisk says 'depending on the browser' but only a Node run is shown. Every entry gets mode 0777, uid/gid 0 and mtime 0. set_gzip(true) compresses with yazi Format::Zlib, so the 'gzip' option emits a zlib stream rather than a gzip file (not on the benchmarked path). Repository archived by the owner on 2025-07-21; last commit 2023-01-24.

Experimental ('faster\*') wasm tar builder; benchmark exercises only TarBuilder.add_file/finish; repository archived read-only by its owner on 2025-07-21.

## Maintenance

Abandoned: archived by ByteDance on 2025-07-21, last commit 2023-01-24, npm 0.1.7 from 2022-10-27. It is MIT-licensed and a thin wrapper around the maintained Rust tar crate, so it is easy to rebuild or reimplement, but nobody maintains it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README output (24.63 ms vs tar-js 3,943.50 ms and tarts 1,251.60 ms on a Xeon Platinum 8269CY) from the public harness examples/nodejs-benchmark/bench.ts; Node, rustc and wasm-pack versions are not stated and the &gt;50x gain is capped at C anyway. The large ratio comes mostly from both JS baselines reallocating and copying the whole archive on every appended file (quadratic), not from wasm.
- **Retiered** C to D: Enricher (2026-10-12): crippled baselines with no valid measurement. The JS baselines copy the whole archive per added file (tar-js extend with a byte-loop zero fill, tarts reduce-concat), so the 50-160x is quadratic buffer growth rather than wasm speed; a single cold run each with no warm-up and no output check.
- **Verifier notes:** README numbers and harness match the record; metadata holds (MIT, 106 stars, archived 2025-07-21, last commit 2023-01-24, abandoned). Shortcomings to record: both JS baselines are quadratic buffer-growth writers (tar-js extend per file, tarts reduce concat), so the ratio overstates a wasm advantage; single cold run, no warm-up, no output check; versions not stated; set_gzip emits zlib not gzip; archived.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/bytedance/tar-wasm>
  - <https://github.com/bytedance/tar-wasm/commits>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nodejs-benchmark/bench.ts>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nodejs-benchmark/package.json>
  - <https://raw.githubusercontent.com/beatgammit/tar-js/HEAD/lib/tar.js>
  - <https://raw.githubusercontent.com/beatgammit/tar-js/HEAD/lib/utils.js>
  - <https://registry.npmjs.org/tarts/latest>
  - <https://raw.githubusercontent.com/porsager/tarts/HEAD/tarts.js>
- **Sources the enricher read:**
  - <https://github.com/bytedance/tar-wasm>
  - <https://github.com/bytedance/tar-wasm/commits>
  - <https://github.com/bytedance/tar-wasm/issues>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/DEVELOPMENT.md>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/src/utils.rs>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/tests/web.rs>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nodejs-benchmark/bench.ts>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nodejs-benchmark/package.json>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nodejs-benchmark/README.md>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nextjs-benchmark/README.md>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nextjs-benchmark/pages/index.tsx>
  - <https://raw.githubusercontent.com/bytedance/tar-wasm/HEAD/examples/nextjs-benchmark/package.json>
  - <https://registry.npmjs.org/@bytedance%2ftar-wasm>
  - <https://raw.githubusercontent.com/beatgammit/tar-js/HEAD/lib/tar.js>
  - <https://raw.githubusercontent.com/beatgammit/tar-js/HEAD/lib/utils.js>
  - <https://raw.githubusercontent.com/porsager/tarts/HEAD/tarts.js>
  - <https://raw.githubusercontent.com/alexcrichton/tar-rs/0.4.38/src/builder.rs>
  - <https://raw.githubusercontent.com/alexcrichton/tar-rs/0.4.38/src/header.rs>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/bytedance/tar-wasm`) · [data/wave13/enrich/raw/github_com_bytedance_tar_wasm.json](../../../data/wave13/enrich/raw/github_com_bytedance_tar_wasm.json) (enrichment confidence 0.8)

</details>
