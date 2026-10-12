# @mtcute/wasm (mtcute)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT; the tgcrypto-derived AES code in packages/wasm/lib/crypto is LGPL-3.0 (COPYING.lesser, per the package README)` · 🟢 active

> WebAssembly blob from the mtcute Telegram library: libdeflate gzip, tgcrypto AES-IGE/CTR and SHA hashes, beating pure-JS equivalents.

| | |
|---|---|
| **Beats** | pako (pure JS zlib) and Node.js built-in zlib for deflate/gunzip; @cryptography/aes (pure JS) for AES-IGE/CTR |
| **Claimed result** | @mtcute/wasm README: 'Up to 10x faster than pure JS implementations' (no numbers there). mtcute/benchmarks results.md, which times standalone component blobs, 73 KB payload: gunzip libdeflate-wasm 4,981 ops/s vs pako 1,409 (3.5x), Node zlib 3,301 (1.5x) and fast-zlib 3,271 (1.5x); the MB/s column overstates the pako gap (345.6 vs 63.5 MB/s, 5.4x) because the pako and fast-zlib scripts count compressed bytes while the zlib and libdeflate scripts count uncompressed bytes. At 48 B gunzip libdeflate 1,095,136 vs pako 117,917 ops/s (9.3x) and zlib 162,193 (6.8x). Deflate at 73 KB: libdeflate 34.6 MB/s vs pako 10.9 (3.2x) and zlib 16.9 (2.0x); the no-unroll build matching the shipped flags gives 27.3 MB/s (2.5x pako, 1.6x zlib) but is slower than Node zlib at 48 B (1.35 vs 3.07 MB/s), 443 B (9.75 vs 15.79) and 13 KB (43.7 vs 46.0). AES-IGE tgcrypto-wasm 134.9 MB/s encrypt vs @cryptography/aes 57.8 (2.3x); AES-CTR 137.1 vs 87.5 MB/s (1.6x); SHA-1 teeny-sha1-wasm 280.6 vs rusha 137.7 MB/s (2.0x, rusha's timed region also runs an OpenSSL SHA-1 check); SHA-256 lekkit-sha256 223.4 vs pure-JS sha256-uint8array 205.8 MB/s (1.09x) and slower at 48 B (50.4 vs 53.4) (ratios derived from page data). |
| **Workload** | Randomised JSON payloads of about 48 B, 443 B, 13 KB, 73 KB and 545 KB (MTProto usage sizes): deflate, gunzip, AES-IGE, AES-CTR, SHA-1, SHA-256 in Node.js, each test in its own child process, 2 s warm-up then 10 runs of 1 s. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5700U 1.8 GHz, NixOS |
| **Compiler and flags** | Benchmarked blobs: mtcute/benchmarks vendor/wasm/lib/Makefile and build.sh, clang (version unstated) -target wasm32-unknown-unknown -nostdlib -ffreestanding -mbulk-memory -O3 -flto=full, without -msimd128; the 'no-unroll' rows add -fno-inline -fno-unroll-loops. Shipped package: packages/wasm/lib/Dockerfile (alpine:3.18.4 with clang16, lld, binaryen) runs lib/Makefile with -O3 -flto=full -fno-inline -fno-unroll-loops, plus a separate mtcute-simd.wasm build. |
| **Adoption** | 570 stars (mtcute repo); TypeScript MTProto library used by Telegram bots and web clients |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/mtcute/mtcute) · [benchmark](https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/results.md) |

## Verdict

Author-run mtcute/benchmarks (AMD Ryzen 7 5700U, Node.js v18.17.1, NixOS; 2 s warm-up then ten 1 s samples per child process) shows libdeflate-wasm gunzip at 4,981 vs 1,409 ops/s for pako (3.5x) and 3,301 for Node zlib (1.5x) on 73 KB randomised JSON, tgcrypto-wasm AES-IGE at 135 vs 58 MB/s for @cryptography/aes (2.3x) and teeny-sha1 at 281 vs 138 MB/s for rusha, all on standalone non-SIMD blobs rather than the shipped package. Native OpenSSL or the tgcrypto Node addon beats the wasm crypto by 1.7x to 13x at 73 KB.

## Use it when

- Browser, Deno, Bun or worker Telegram clients that need synchronous AES-IGE/CTR, SHA-1/256 and zlib on MTProto-sized payloads: at 48 B tgcrypto-wasm IGE encrypt ran 1,219,546 vs 322,174 ops/s for @cryptography/aes (3.8x) and libdeflate gunzip 1,095,136 vs 117,917 ops/s for pako (9.3x, derived from page data).
- Small authenticated gunzip workloads even on Node: the no-unroll libdeflate build beat zlib.gunzipSync at every size (949,255 vs 162,193 ops/s at 48 B, 4,854 vs 3,301 at 73 KB), partly because it skips the CRC32 check zlib performs.
- Bundle-size-sensitive web apps: the committed mtcute.wasm is 57,363 B raw and about 26 KB gzipped for every primitive, against 47.4 KiB rendered / 15.1 KiB gzipped for pako alone (zlib only).
- Synchronous hashing where WebCrypto's per-call async overhead dominates: WebCrypto SHA-256 managed 37,005 ops/s at 48 B vs 1,107,333 for lekkit-sha256 wasm.

## Skip it when

- On Node.js for anything except AES-IGE: native OpenSSL does AES-CTR at 1,791 vs 137 MB/s and SHA-256 at 1,065 vs 223 MB/s on 73 KB, and mtcute's own NodeCryptoProvider uses node:crypto and node:zlib for those.
- Deflating small payloads with the shipped no-unroll build: it trails Node zlib below 73 KB (29,523 vs 67,343 ops/s at 48 B; 3,521 vs 3,702 at 13 KB), and fast-zlib beats it on small inputs.
- As a general gzip decoder or AES library for untrusted or unpadded input: CRC32 is not verified, the output size comes from the gzip trailer, IGE does not check the 16-byte length rule, and the T-table AES is not constant-time.
- When SHA-256 speed matters: lekkit-sha256 wasm is about level with pure-JS sha256-uint8array (223 vs 206 MB/s at 73 KB; 50.4 vs 53.4 MB/s at 48 B, slower).
- If LGPL-3.0 code is unacceptable: the AES sources under packages/wasm/lib/crypto derive from tgcrypto (LGPL-3.0) inside an otherwise MIT package.

## How it is fast

Compiled C replaces JavaScript: a size-trimmed libdeflate (table-driven Huffman decoding, fast matchfinding), tgcrypto's T-table AES-256 (Te0-Te3/Td0-Td3 lookups) with IGE and CTR chaining on 16-byte vector types, teeny-sha1 and LekKit sha256. Per-call overhead is small: the compressor and decompressor are allocated once at init, a bump allocator serves buffers from the heap tail, and key, IV and digest travel through shared static buffers, which is why the biggest wins are on 48-byte payloads (gunzip 9.3x pako, IGE 3.8x @cryptography/aes in ops/s). The gzip path also compiles out CRC32 verification (it relies on MTProto's msg_key integrity) and sizes the output from the gzip ISIZE trailer, removing work the JavaScript and zlib baselines do.

## Compared with alternatives

Pick hash-wasm when you only need hashes (wider algorithm set, streaming API), and fast-pako or zip.js's wasm zlib for general-purpose gzip/zlib with streaming and CRC checks; pick @mtcute/wasm when you need the MTProto set (AES-IGE/CTR, zlib deflate, gunzip, SHA-1/256) synchronously in one blob of about 26 KB gzipped.

## Integration

| | |
|---|---|
| **Form** | module (npm @mtcute/wasm 0.32.0, published 2026-08-27: TypeScript wrapper plus mtcute.wasm and mtcute-simd.wasm) |
| **Dependencies** | none at runtime (freestanding C, no libc or Emscripten runtime); rebuilding the blobs needs clang 16, lld and binaryen (Dockerfile on alpine:3.18.4) |
| **Minimum toolchain** | any WebAssembly engine with bulk-memory (built with -mbulk-memory); the SIMD blob needs wasm SIMD128; benchmarks ran on Node.js v18.17.1 |
| **Platforms** | any WebAssembly host (browsers, Node.js, Deno, Bun); Cloudflare Workers (issue #54) and Expo/React Native (issue #57) are open requests; a Bun 1.2.11 CompileError at byte 150 (issue #98, maintainer suspected SIMD) was closed without a confirmed cause |
| **Thread safety** | Not thread-safe within one instance: one module-global heap, compressor, decompressor and shared key/IV/output buffers; use one instance per worker. |
| **Drop-in for the baseline** | partial — replaces pako/node:zlib zlib-deflate and gunzip and @cryptography/aes IGE/CTR for MTProto use, but through a different synchronous Uint8Array API with no streaming, levels, gzip compression or CRC check |

## Gotchas

- Benchmark-to-shipped gap: mtcute/benchmarks times blobs from vendor/wasm/lib/Makefile (clang -O3 -flto=full; the no-unroll rows add -fno-inline -fno-unroll-loops) built without -msimd128, so neither the shipped mtcute.wasm (different source set) nor the mtcute-simd.wasm that SIMD-capable engines load was measured. The flags are stated in that Makefile and build.sh, correcting the record's 'not stated'; the clang version is not.
- gunzip does not verify CRC32: the check sits under #ifdef CRC32, which no Makefile defines, and neither the benchmarked nor the shipped blobs contain a CRC32 table or polynomial, while zlib.gunzipSync and pako.inflate verify the gzip CRC32 inside their timed calls. The gunzip ratios therefore include work the wasm side skips (small against native zlib, larger against pure-JS pako).
- Input-trusting wrappers (found by reading src/index.ts and lib/utils/allocator.c, not executed): gunzip sizes its output from the gzip ISIZE trailer (returned as int32) through a bump allocator that ignores memory.grow failure and does not guard 32-bit overflow, so a lying trailer can grow wasm memory permanently or leave the heap pointer past the end; its error paths throw before freeing the input and output blocks; ige256Encrypt/Decrypt write whole 16-byte blocks without checking the length, overrunning the output block when it is not a multiple of 16. MTProto's padded, msg_key-authenticated payloads avoid these.
- Packaging drift: the README's '47 KB raw, 24 KB gzipped' is stale (committed mtcute.wasm 57,363 B, 25,982 B with gzip -9; SIMD blob 59,241 B), and the Dockerfile runs plain make, whose default goal builds only mtcute.wasm, then copies mtcute-simd.wasm.

## Known shortcomings

- The gunzip MB/s against pako is inflated by a unit mismatch in the harness (pako counts compressed bytes; ops/s gives 3.5x, not 5.4x); the rusha timing includes an OpenSSL check; the shipped no-unroll deflate is slower than Node zlib below 73 KB; the benchmarks time vendor blobs, not the shipped package. MIT plus LGPL-3.0 AES.
- Harness flaw: the gunzip under test skips CRC32 (the check sits under #ifdef CRC32, never defined; no CRC table or polynomial in the benchmarked or shipped blobs) while zlib and pako verify CRC32 inside their timed calls. Record correction: the vendor build flags are stated in benchmarks vendor/wasm/lib/Makefile and build.sh (-O3 -flto=full; no-unroll adds -fno-inline -fno-unroll-loops); neither those blobs nor the shipped mtcute-simd.wasm were benchmarked as shipped. Code-read risks: gunzip trusts the gzip ISIZE trailer, the allocator ignores failed memory.grow and 32-bit overflow, error paths leak, IGE has no 16-byte length check, the T-table AES is not constant-time; README size stale (57,363 B, not 47 KB).

## Caveats and trade-offs

Benchmarks are by the mtcute authors (mtcute/benchmarks, results on Node 18.17.1, AMD Ryzen 7 5700U, NixOS; repo not updated since 2023) and time standalone component blobs from vendor/wasm (libdeflate, tgcrypto, teeny-sha1, lekkit-sha256), not the published @mtcute/wasm build, whose libdeflate is modified and whose flags (-fno-inline -fno-unroll-loops) match the slower 'no-unroll' rows. Harness inconsistencies: gunzip MB/s for pako and fast-zlib is computed from compressed bytes but for zlib and libdeflate from uncompressed bytes (compare ops/s instead); the deflate scripts pass JS strings to zlib and pako (UTF-8 encoding inside the timed call) but a pre-built Buffer to libdeflate; rusha's SHA-1 timing includes an OpenSSL SHA-1 validation while teeny-sha1's does not. The no-unroll libdeflate deflate is slower than Node's native zlib at 48 B, 443 B and 13 KB and wins only from 73 KB up; fast-zlib beats it on small payloads; wasm-miniz_oxide deflates 2.8x faster than libdeflate at 73 KB (1,397 vs 498 ops/s) at a worse ratio (67.42% vs 64.65%). Native OpenSSL is far faster than the wasm crypto (AES-CTR 1,791 vs 137 MB/s encrypt at 73 KB; SHA-256 1,065 vs 223; OpenSSL-based IGE 507 vs 135) and tgcrypto as a Node addon beats the wasm build (236 vs 135 MB/s IGE); WebCrypto SHA-1 beats teeny-sha1 at 545 KB (578 vs 292 MB/s). SHA-256 in wasm is about level with pure-JS sha256-uint8array. The authors' own conclusion is to prefer native crypto on Node and use wasm elsewhere. libdeflate compression level not stated. The AES code is LGPL-3.0 (weak copyleft) inside an otherwise MIT package. [retier] Benchmarks are by the mtcute authors (mtcute/benchmarks, Node 18.17.1, AMD Ryzen 7 5700U, NixOS; not updated since 2023) and time standalone component blobs from vendor/wasm (libdeflate, tgcrypto, teeny-sha1, lekkit-sha256), not the published @mtcute/wasm build; neither those blobs nor the shipped mtcute-simd.wasm were benchmarked as shipped. Harness asymmetry: the gunzip under test does not verify CRC32 (the check sits under #ifdef CRC32, which no Makefile defines; no CRC table or polynomial exists in the benchmarked or shipped blobs) while zlib.gunzipSync and pako.inflate verify the gzip CRC32 inside their timed calls, so the gunzip ratios include work the wasm side skips (small against native zlib, larger against pure-JS pako). The MB/s column overstates the pako gap because the pako and fast-zlib scripts count compressed bytes while the zlib and libdeflate scripts count uncompressed bytes (compare ops/s); the deflate scripts pass JS strings to zlib and pako. Input-trusting wrappers (read, not executed): gunzip sizes its output from the gzip ISIZE trailer through a bump allocator that ignores memory.grow failure and 32-bit overflow, error paths leak the input and output blocks, ige256Encrypt/Decrypt write whole 16-byte blocks without a length check, and the T-table AES is not constant-time. Packaging drift: the README's '47 KB raw, 24 KB gzipped' is stale (57,363 B committed, 25,982 B gzip -9; SIMD blob 59,241 B).

47 KB raw / 24 KB gzipped wasm. AES-IGE code derives from tgcrypto (LGPL-3.0, source kept in the lib/crypto directory), deflate is a modified libdeflate (MIT), so the licensing is mixed. Optional SIMD blob.

## Maintenance

Actively maintained (last commit 2026-10-07, @mtcute/wasm 0.32.0 on npm) and copyable (MIT with LGPL-3.0 AES sources), but the benchmark repo dates from 2023 and times unshipped non-SIMD blobs, part of the gunzip win comes from skipping CRC32, and the input-trusting gunzip and IGE wrappers need validation before reuse outside MTProto.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The harness is public (mtcute/benchmarks tests_\*/ scripts, results.md) with CPU (AMD Ryzen 7 5700U) and Node.js v18.17.1 stated, but the wasm blobs it times are prebuilt files in vendor/wasm with unstated build flags and are not the shipped @mtcute/wasm build; first-party numbers short of A, so C stands.
- **Verifier notes:** Numbers match results.md, but the gunzip MB/s ratio vs pako is inflated by a unit mismatch in the harness (ops/s gives 3.5x, not 5.4x), rusha's timing includes an OpenSSL check, and the shipped no-unroll deflate loses to Node's native zlib below 73 KB. Usability changed from mixed to copyable because every part is OSI-licensed (MIT plus LGPL-3.0 AES); revert if the catalog treats LGPL parts as mixed. Metadata checked: 570 stars, last commit 2026-10-07, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-104 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/results.md>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/build-vendor.sh>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/benchmark-all.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/functions.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_gunzip/1.%20zlib.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_gunzip/2.%20fast-zlib.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_gunzip/3.%20pako.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_gunzip/4.%20libdeflate.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_deflate/1.%20zlib.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_deflate/3.%20pako.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_deflate/4.%20libdeflate.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_ige/2.%20%40cryptography%20aes.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_ige/3.%20tgcrypto-wasm.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_ctr/2.%20%40cryptography%20aes.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_ctr/3.%20tgcrypto-wasm.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_sha1/3.%20rusha.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_sha1/7.%20teeny-sha1.js>
  - <https://github.com/mtcute/benchmarks>
  - <https://github.com/mtcute/benchmarks/tree/master/tests_gunzip>
  - <https://github.com/mtcute/benchmarks/tree/master/vendor>
  - <https://github.com/mtcute/mtcute>
  - <https://github.com/mtcute/mtcute/commits/master>
  - <https://github.com/mtcute/mtcute/tree/master/packages/wasm>
  - <https://github.com/mtcute/mtcute/tree/master/packages/wasm/lib>
  - <https://github.com/mtcute/mtcute/tree/master/packages/wasm/lib/crypto>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/README.md>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/Makefile>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/Dockerfile>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/package.json>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/build.config.js>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/mtcute/mtcute/tree/master/packages/wasm/src>
  - <https://github.com/mtcute/mtcute/tree/master/packages/node/src/utils>
  - <https://github.com/mtcute/mtcute/issues?q=is%3Aissue%20wasm>
  - <https://github.com/mtcute/mtcute/issues/98>
  - <https://github.com/mtcute/mtcute/issues/44>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/README.md>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/package.json>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/build.config.js>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/src/index.ts>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/src/mtcute.wasm>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/src/mtcute-simd.wasm>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/Makefile>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/Dockerfile>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/wasm.h>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/utils/allocator.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/libdeflate/allocator.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/libdeflate/gzip_decompress.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/crypto/aes256.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/crypto/ige256.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/crypto/ctr256.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/hash/sha1.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/wasm/lib/hash/sha256.c>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/node/src/utils/crypto.ts>
  - <https://raw.githubusercontent.com/mtcute/mtcute/HEAD/packages/web/src/crypto.ts>
  - <https://registry.npmjs.org/@mtcute/wasm>
  - <https://github.com/mtcute/benchmarks/tree/master/vendor/wasm>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/results.md>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/build-vendor.sh>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/functions.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_gunzip/1.%20zlib.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_gunzip/3.%20pako.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_gunzip/4.%20libdeflate.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_deflate/1.%20zlib.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_deflate/3.%20pako.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/tests_deflate/4.%20libdeflate.js>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/build.sh>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/_init.mjs>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/libdeflate.mjs>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/tgcrypto.mjs>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/teeny-sha1.mjs>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/lib/Makefile>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/lib/mtcute.wasm>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/lib/mtcute-no-unroll.wasm>
  - <https://raw.githubusercontent.com/mtcute/benchmarks/HEAD/vendor/wasm/lib/libdeflate/gzip_decompress.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mtcute/mtcute`) · [data/wave13/enrich/raw/github_com_mtcute_mtcute.json](../../../data/wave13/enrich/raw/github_com_mtcute_mtcute.json) (enrichment confidence 0.7)

</details>
