# awasm-noble

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT` · 🟢 active

> WASM-SIMD (optionally multi-threaded) hashes and ciphers from Paul Miller; BLAKE3 about 8-19x single-threaded throughput of @noble/hashes in reported runs.

| | |
|---|---|
| **Beats** | @noble/hashes (pure-JavaScript hashes), measured for BLAKE3 |
| **Claimed result** | Ryzen 7 5800X table (third-party, blake3-wasm-rs author, UneBaguette/blake3.wasm README): awasm-noble 1,729 vs @noble/hashes 52 MB/s at 64 KB (33x), threaded 4,946 vs 50 at 10 MB (about 99x) (derived from page data). Apple M4 table in the same README (first-party: added by awasm-noble's author in that repo's PR #1, 2026-04-22): 843 vs 105 MB/s at 1 KB (8.0x), 1,898 vs 102 at 64 KB (18.6x), 1,943 vs 101 at 1 MB (19.2x), threaded 4,711 vs 101 at 1 MB (46.6x); its blake3-wasm cells at 64 KB (2,004) and 1 MB (1,893) match the Ryzen table exactly and were probably copied. The awasm-noble README itself states '6-10 GB/s for BLAKE3' on an Apple M4 and gives no baseline. |
| **Workload** | BLAKE3 hashing of 32 B to 10 MB inputs in Node.js v24; awasm-noble wasm and wasm_threads backends vs @noble/hashes, measured in the README of the third-party blake3.wasm repo. |
| **Metric** | throughput |
| **Hardware** | Apple M4; AMD Ryzen 7 5800X (third-party table). Own README: Apple M4 |
| **Compiler and flags** | Auditable JS-to-wasm compiler in the repo (wasm SIMD, optional web-worker threads); no flags; Node.js v24 |
| **Adoption** | 52 stars; by the author of noble-hashes |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/paulmillr/awasm-noble) · [benchmark](https://github.com/UneBaguette/blake3.wasm) |

## Verdict

Only BLAKE3 has a baseline comparison: in the blake3.wasm README (Node.js v24, measured with constant-filled buffers in what appears to be awasm-noble's own comparison harness), awasm-noble's single-threaded wasm backend did 843/1,898/1,943 MB/s at 1 KB/64 KB/1 MB versus 105/102/101 MB/s for pure-JS @noble/hashes on Apple M4 (rows contributed by awasm-noble's author), and 1,729 vs 52 MB/s at 64 KB on a Ryzen 7 5800X (run by the blake3-wasm-rs author); worker-thread figures reach 4.7-6.5 GB/s. awasm-noble's own README gives absolute Apple M4 numbers only (blake3 1,940 MB/s single-threaded, 6-11 GB/s threaded) with no baseline.

## Use it when

- Browser or Node/Bun/Deno code that hashes large buffers with BLAKE3 (file checksums, content addressing) and cannot use a native addon: about 1.9 GB/s single-threaded on Apple M4 versus about 0.1 GB/s for @noble/hashes.
- Hashing many independent messages at once (Merkle leaves, dedup indexes) with .parallel() or .chunks(), where multi-buffer SIMD and the worker pool apply even to SHA-256, SHA-512, SHA-3 and BLAKE2.
- Bulk ChaCha20/XChaCha20-Poly1305 or AES-CTR/GCM encryption of megabyte-scale data in the browser where WebCrypto is unavailable, async-only or lacks the mode (XChaCha, GCM-SIV, AES-SIV, KW).
- Libraries that want a noble-compatible API today and an opt-in faster backend later: stub.js plus the noble.js wrapper lets the application decide.
- Pages that already serve COOP/COEP headers (cross-origin isolated) and can afford the worker pool, for the threaded multi-GB/s figures.

## Skip it when

- Server-side Node for SHA-2/SHA-1/MD5 where node:crypto (OpenSSL) is available: the package's own harness benchmarks against node:crypto but publishes no result, and its single-threaded wasm SHA-256 figure is 553 MB/s on Apple M4.
- Strict CSP environments: the wasm backends need 'wasm-unsafe-eval', and wasm_threads needs Cross-Origin-Opener-Policy: same-origin plus Cross-Origin-Embedder-Policy: require-corp; without them use the js or noble backend and lose the speedup.
- Small messages: at 32 B the reported gain over @noble/hashes is only 3.1-3.75x, the threaded backend is no faster (94 vs 105 MB/s on M4), and blake3-wasm-rs was faster at 32 B on both CPUs.
- Code that must resist cache-timing attacks with AES or GHASH: the AES rounds use T-table lookups (T0..T3 plus S-box tables, lanes fixed at 1) and GHASH uses precomputed tables; wasm has no AES or carry-less-multiply instructions.
- Projects that need audited code or a stable API: version 0.1.x, about 50 commits, no published audit (the noble libraries it wraps are audited; this package is not), and SECURITY.md points to a README Security section that does not exist.

## How it is fast

Algorithms are written in a JS-embedded DSL and compiled by awasm-compiler to WebAssembly with 128-bit SIMD; batchFn lays out state so SIMD lanes process independent blocks: separate messages for SHA/MD/BLAKE2 (multi-buffer hashing, which is why .parallel()/.chunks() matter), and independent 1 KB chunks of one input for BLAKE3, whose Merkle tree is then folded by a parent-compression stack. The wasm_threads backend adds a Web Worker pool driven by Atomics on shared memory instead of postMessage, so BLAKE3 and parallelisable cipher modes (CTR, ECB, ChaCha20, the encryption half of GCM/SIV) split one large input across workers, and other hashes spread multiple inputs. The baseline @noble/hashes is scalar pure JavaScript, so the gain is SIMD plus wasm's predictable 32/64-bit integer code rather than a new algorithm.

## Compared with alternatives

Pick it over hash-wasm when you need BLAKE3 or AEAD ciphers at multi-GB/s with optional worker threads, multi-input .parallel() hashing, a noble-compatible API with swappable backends, or reproducible wasm built from auditable JS source; hash-wasm is the more established single-threaded wasm hash library and fast-noble-hashes targets SHA-2 against @noble/hashes. For small BLAKE3 inputs in Node, blake3-jit reports wins over a native addon, which awasm-noble does not claim.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at run time for the wasm/js backends (wasm binaries are embedded as base64 in JS); optional peers @noble/hashes 2.4.0 and @noble/ciphers 2.4.0 (noble.js backend) and @awasm/compiler 0.1.5 (runtime backend) |
| **Minimum toolchain** | Node.js &gt;= 22.22.0 (package.json engines); Bun and Deno supported; browsers with WebAssembly SIMD, plus SharedArrayBuffer and Atomics for wasm_threads |
| **Platforms** | any WebAssembly-SIMD runtime (browsers, Node, Bun, Deno, Vercel example included); wasm_threads needs cross-origin isolation in browsers |
| **Thread safety** | not documented beyond the threaded backend: one shared worker pool (bitmask of up to 31 workers) per process; Deno needs WP.stop() to exit because workers lack unref |
| **Drop-in for the baseline** | partial: same call shapes as @noble/hashes for hashes (hash(msg), create/update/digest), but import paths differ, async methods are hash.async rather than hashAsync, cmac and stream-cipher signatures differ from @noble/ciphers, and some noble functions (kmac, cshake, turboshake, kt128, ff1, PRNGs) are missing |

## Gotchas

- Correctness history: version 0.1.0 returned wrong BLAKE3 digests, silently, in the wasm and wasm_threads backends for input lengths in [4096k-63, 4096k-2] (62 lengths per 4 KiB band, about 1.5% of sizes) because a SIMD lane mask truncated the last-block length to its low bit (PR #2, fixed in 0.1.1 on 2026-04-20); the js backend and streaming path were unaffected. PR #1 fixed streaming digests ignoring create()'s dkLen. Pin &gt;= 0.1.1 and cross-check against @noble/hashes in tests.
- Provenance of the comparison: the Apple M4 table in UneBaguette/blake3.wasm (the source of the 8-19x figures) was added by awasm-noble's own author in PR #1 there (2026-04-22, 'readme: add awasm-noble entry'), so those numbers are first-party; only the Ryzen 7 5800X table comes from the blake3-wasm-rs author. The table's columns and sizes (32 B, 1 KB, 64 KB, 1 MB, 10 MB; old noble, wasm, threads, blake3-wasm-rs) match awasm-noble's benchmark/internal/hashes.ts, but no run log is published. In the M4 table the blake3-wasm cells at 64 KB (2,004) and 1 MB (1,893) are identical to that column in the earlier Ryzen table, so that column may be partly copied. The measured sizes fall outside the 0.1.0 bug's affected lengths.
- README Speed section is stale relative to its scripts: it says 'input: 32x1mb' and 'blake3 1x100mb' and 'ciphers, input: 1gb', while benchmark/2-parallel.ts uses 48 chunks, a 1x1gb BLAKE3 case and 10 MB cipher inputs; its multi-input hash figures (e.g. sha1 11,413 MB/s, blake3 11,058 MB/s) feed the same 1 MB buffer 48 times (Array(48).fill(data)), so the data stays cache-resident and the numbers are an upper bound for 48 distinct inputs. The M4 figures also predate the 'Improve perf of single-shot hashes' (2026-06-13) and new-compiler (2026-07-20) commits.
- Synchronous by default even with threads; the README does not say how a synchronous threaded call waits on a browser main thread, so test UI responsiveness and use the .async variants for large inputs.

## Known shortcomings

- The only baseline numbers come from a competitor's README (UneBaguette/blake3.wasm, 4 stars, no harness, BLAKE3 only); blake3-wasm-rs beats it single-threaded on Ryzen at every size; its own README has no baseline.
- Provenance flaw: the Apple M4 table in UneBaguette/blake3.wasm was added by awasm-noble's own author in that repo's PR #1 (2026-04-22), so the 8-19x claim is first-party; only the Ryzen 7 5800X table comes from the blake3-wasm-rs author. On M4 the blake3-wasm cells at 64 KB (2,004) and 1 MB (1,893) match the earlier Ryzen table exactly, so they were probably copied. v0.1.0 returned wrong BLAKE3 digests in the wasm and wasm_threads backends for 62 lengths per 4 KiB band (PR #2, fixed in 0.1.1); the benchmarked sizes were unaffected. The README speed labels are stale against benchmark/2-parallel.ts (32x1mb vs 48 chunks, 1x100mb vs 1x1gb, ciphers 1gb vs 10mb); the multi-input figures hash the same 1 MB buffer 48 times (cache-resident); AES and GHASH are table-based; unaudited.

## Caveats and trade-offs

The baseline comparison is not in awasm-noble's own README: its Speed section (Apple M4; blake3 1,940 MB/s single-threaded, 11,058 MB/s for 48x1 MB and 6,564 MB/s for 1x100 MB with threads, which is the '6-10 GB/s' headline) lists awasm figures only. awasm-noble ships a comparison harness (benchmark/internal/hashes.ts against node:crypto, hash-wasm, blake3-wasm-rs and @noble/hashes) but publishes no results from it. The third-party table comes from the README of UneBaguette/blake3.wasm (4 stars), whose author maintains the competing blake3-wasm-rs and whose repo holds no benchmark script; it covers only BLAKE3, so gains for other algorithms against @noble/hashes are unconfirmed. In that table blake3-wasm-rs beats single-threaded awasm-noble at every size on the Ryzen 7 5800X and at 32 B, 64 KB and 10 MB on the Apple M4. At 32 B awasm-noble is still 3.75x (M4, 105 vs 28 MB/s) and 3.1x (Ryzen, 34 vs 11 MB/s) faster than @noble/hashes; the large multiples (33x, about 99x) come from the Ryzen run, where @noble/hashes measured about half its M4 speed, and the threaded figures use web-worker threads. No native baseline (Node's OpenSSL has no BLAKE3; the third-party README says its native blake3-napi addon is faster for large inputs). Confidence reflects the second-hand source. [retier] The baseline comparison is not in awasm-noble's own README (its Speed section lists awasm figures only, and it publishes no results from its own comparison harness benchmark/internal/hashes.ts). The Apple M4 table in UneBaguette/blake3.wasm (source of the 8-19x figures) was added by awasm-noble's author in that repo's PR #1 (2026-04-22), so it is first-party, and two of its blake3-wasm cells duplicate the Ryzen table; only the Ryzen 7 5800X table comes from the blake3-wasm-rs author, whose 4-star repo holds no benchmark script. The tables cover only BLAKE3; the README Speed section is stale against benchmark/2-parallel.ts (it says 32x1mb, 1x100mb and 1 GB cipher inputs where the script uses 48 chunks, 1x1gb and 10 MB), and the multi-input figures hash the same 1 MB buffer 48 times (cache-resident upper bound). Correctness history: 0.1.0 returned wrong BLAKE3 digests silently in the wasm and wasm_threads backends for 62 input lengths per 4 KiB band (PR #2, fixed in 0.1.1 on 2026-04-20; the benchmarked sizes were unaffected); PR #1 fixed streaming digests ignoring dkLen. AES and GHASH are table-based (not constant-time); unaudited; synchronous threaded calls on a browser main thread are undocumented.

Wasm backends need the wasm-unsafe-eval content-security-policy; the threaded backend needs cross-origin isolation headers (COOP and COEP). Offers wasm, wasm_threads, js, noble, webcrypto and runtime backends behind one API, so apps can fall back. Wasm binaries are reproducibly generated from JS source for auditing.

## Maintenance

Active (last commit 2026-09-12, v0.1.4, 52 stars, MIT, sole maintainer with a strong track record from the audited noble libraries), but pre-1.0, unaudited and with a BLAKE3 wrong-digest bug fixed only in 0.1.1, so pin versions and keep cross-checks; copyable as an npm/JSR dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only baseline comparison is a README table in UneBaguette/blake3.wasm (author of the competing blake3-wasm-rs) with CPU and Node v24 stated but no benchmark script in that repo; awasm-noble's own README numbers (benchmark/1-hashes-ciphers.ts, 2-parallel.ts) have no baseline, so numbers without reproducible methodology: C.
- **Verifier notes:** Third-party numbers match the blake3.wasm README exactly, but that source is a competitor's README with no harness and BLAKE3 only; awasm-noble's own benchmarks have no baseline. Metadata checked: MIT, 52 stars, last commit 2026-09-12, not archived, not a fork.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-104 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/UneBaguette/blake3.wasm>
  - <https://raw.githubusercontent.com/UneBaguette/blake3.wasm/HEAD/README.md>
  - <https://github.com/paulmillr/awasm-noble>
  - <https://github.com/paulmillr/awasm-noble/commits/main>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/README.md>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/package.json>
  - <https://github.com/paulmillr/awasm-noble/tree/main/benchmark>
  - <https://github.com/paulmillr/awasm-noble/tree/main/benchmark/internal>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/1-hashes-ciphers.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/2-parallel.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/3-fastest.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/internal/hashes.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/internal/noble-hashes.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/internal/package.json>
- **Sources the enricher read:**
  - <https://github.com/paulmillr/awasm-noble>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/README.md>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/package.json>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/1-hashes-ciphers.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/2-parallel.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/3-fastest.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/internal/hashes.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/internal/noble-hashes.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/benchmark/internal/package.json>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/test/noble-all.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/src/workers.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/src/wasm_threads.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/src/hashes.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/src/modules/hashes.ts>
  - <https://raw.githubusercontent.com/paulmillr/awasm-noble/HEAD/src/modules/ciphers.ts>
  - <https://github.com/paulmillr/awasm-noble/tree/main/src>
  - <https://github.com/paulmillr/awasm-noble/tree/main/src/modules>
  - <https://github.com/paulmillr/awasm-noble/commits/main>
  - <https://github.com/paulmillr/awasm-noble/issues?q=is%3Aissue>
  - <https://github.com/paulmillr/awasm-noble/pulls?q=is%3Apr>
  - <https://github.com/paulmillr/awasm-noble/pull/2>
  - <https://github.com/paulmillr/awasm-compiler>
  - <https://github.com/UneBaguette/blake3.wasm>
  - <https://raw.githubusercontent.com/UneBaguette/blake3.wasm/HEAD/README.md>
  - <https://github.com/UneBaguette/blake3.wasm/commits/master>
  - <https://github.com/UneBaguette/blake3.wasm/commits/master/README.md>
  - <https://github.com/UneBaguette/blake3.wasm/commit/85b27b1>
  - <https://github.com/UneBaguette/blake3.wasm/pull/1>
  - <https://github.com/UneBaguette/blake3.wasm/pull/1/files>
  - WebSearch: "awasm" noble paulmillr wasm benchmark blake3 (snippets of paulmillr.com/awasm announcement: BLAKE3 10.8 GB/s multi-input, 6.3 GB/s single-input, ChaCha20 6.4 GB/s)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/paulmillr/awasm-noble`) · [data/wave13/enrich/raw/github_com_paulmillr_awasm_noble.json](../../../data/wave13/enrich/raw/github_com_paulmillr_awasm_noble.json) (enrichment confidence 0.65)

</details>
