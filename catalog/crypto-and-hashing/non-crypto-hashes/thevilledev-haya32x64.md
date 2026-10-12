# haya32x64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Unlicense` · 🟢 active

> 64-bit non-cryptographic hash built only from 32-bit operations. In pure JS it beats xxhash-wasm XXH64 on 4-8 byte keys.

| | |
|---|---|
| **Beats** | xxHash (XXH64, via xxhash-wasm) |
| **Claimed result** | 4-byte one-shot latency with pure-JS haya32x64: 22.9 ns (C8a) and 34.0 ns (C8g), vs xxhash-wasm XXH64 at 39.4 ns and 63.9 ns. That is about 1.7x-1.9x faster (derived from page data). Against the pure-JS xxhashjs XXH64 (1939.3 ns / 2691.0 ns at 4 B; 37 / 28 MB/s at 1 MiB) the gap is far larger. XXH64 via wasm still leads 1 MiB bulk: 15,973 MB/s vs haya32x64's 4,462 MB/s pure-JS and 10,971 MB/s hybrid (C8a). cyrb53 (53-bit output) is faster at 4 B (4.7 ns). |
| **Workload** | Pure-JavaScript and wasm one-shot hashing of a 4-byte key and 1 MiB bulk data on AWS EC2 C8a (AMD EPYC 9R45) and C8g (Arm Neoverse V2), Node.js 24.18 / V8 13.6, medians of nine warmed public-API samples, comparing haya32x64 (32-bit-only state/arithmetic) against hayahash64, xxhash-wasm's XXH64, and cyrb53 |
| **Metric** | latency |
| **Hardware** | AWS EC2 c8a.2xlarge (AMD EPYC 9R45) and c8g.2xlarge (Arm Neoverse V2), timed work pinned to one core |
| **Compiler and flags** | Node.js 24.18.0 / V8 13.6.233.17 on Ubuntu 26.04 for the JS/wasm figures (node --expose-gc bench/js.mjs; xxhash-wasm 1.1.0 and xxhashjs 0.2.2 pinned). Native SMHasher3 built with GCC 15.2.0 -O3 -march=native -DNDEBUG. |
| **Adoption** | 0 stars (new project, created 2026-08-08) |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/thevilledev/haya32x64) · [benchmark](https://github.com/thevilledev/haya32x64/blob/main/README.md) |

## Verdict

On one AWS c8a.2xlarge (EPYC 9R45) and one c8g.2xlarge (Neoverse V2), Node.js 24.18 / V8 13.6, the author took medians of nine warmed public-API samples. The pure-JS engine hashed 4-byte Uint8Arrays in 22.9 / 34.0 ns vs 39.4 / 63.9 ns for xxhash-wasm 1.1.0 XXH64, about 1.7-1.9x (derived); at 8 B the gap is about 1.8-2.1x. XXH64 via wasm still led at 1 MiB (15,973 vs 10,971 MB/s hybrid on C8a) and on string inputs. Native SMHasher3 (GCC 15.2 -O3 -march=native) shows it far behind 64-bit-multiply hashes.

## Use it when

- JavaScript hashing of very short binary keys (Uint8Array, 4-8 bytes) where you need 64 output bits without BigInt or wasm: 22.9 ns vs 39.4 ns for xxhash-wasm XXH64 at 4 B on EPYC 9R45
- CSP-restricted or edge JS runtimes where WebAssembly may be unavailable: the pure-JS engine alone reaches about 3.9-4.5 GB/s at 1 MiB, over 100x the pure-JS xxhashjs XXH64 package (28-37 MB/s)
- Cross-language digests that must match exactly between C, JS and wasm (bit-exact engines checked against 180 shared KAT vectors and a C-reference differential corpus)
- 32-bit targets without a 64-bit multiply (Cortex-M, RV32) or shaders, which are the stated design targets; in native SMHasher3 it is the fastest 32-bit-arithmetic row listed (7.50 B/cycle vs t1ha0 5.21 and XXH-32 4.89 on C8a)
- Content fingerprints or cache keys in mixed JS/C systems where Unlicense/public-domain licensing matters

## Skip it when

- Any native 64-bit C/C++ host: XXH3-64 runs at 60.59 vs 7.50 B/cycle bulk, and rapidhash, wyhash and a5hash-128 are also faster on both small keys and bulk. The README itself says to use a 64-bit-native hash there
- JavaScript string keys: through the string API xxhash-wasm is about 4.5x faster (59.2 ns vs 267.9 ns for 8 ASCII chars on C8a) because haya32x64 runs TextEncoder first; cyrb53 is 6.5 ns if 53 bits are enough
- Bulk JS hashing where wasm is allowed: at 1 MiB on C8a, xxhash-wasm XXH64 (15,973 MB/s) and hayahash64 wasm (16,034 MB/s) beat the haya32x64 hybrid (10,971 MB/s). With 64 KiB chunks, xxhash-wasm streaming is about 3.7x faster than haya32x64's pure-JS-only stream
- Persisted digests that must stay stable: the digest is labeled experimental and frozen only at an interim verification value (0x431563D2). Output for inputs of 128 bytes or more already changed between published releases (v0.1.x to v0.2.0)
- Hash tables keyed by attacker-controlled data, or any authentication use: it is non-cryptographic and makes no keyed collision-resistance claim

## How it is fast

Short keys (8 bytes or less) take a dedicated path of two complete 32x32 products, and the JS engine keeps inputs under 16 bytes out of wasm. That avoids the JS-to-wasm copy and call overhead that xxhash-wasm pays on every call, and it avoids BigInt. Inputs of 128 bytes or more use a 'pair-lane' kernel: four lane pairs over 32-byte blocks, where each 8-byte stripe feeds one complete 32x32 multiply, m = (u0 + a) \* (u1 + b), with the product's low and high words cross-fed back into the lanes. Per the author's profiling, that halves instructions per byte compared with the earlier one-multiply-per-word kernel. The 16-127-byte mid path absorbs 16-byte stripes through four multiply lanes plus a serial carry, and a two-round Feistel seed premix keeps all 64 seed bits.

## Compared with alternatives

Pick it over xxHash (XXH64 via xxhash-wasm, or xxhashjs) and over its sibling hayahash only for JS code that hashes very short byte keys with no BigInt and optionally no wasm, or for hardware with only 32-bit multiplies. On 64-bit native hosts, and for JS bulk or string hashing where wasm is allowed, xxHash (XXH3/XXH64) or hayahash wins.

## Integration

| | |
|---|---|
| **Form** | header-only (C); npm module (ESM) for JavaScript |
| **Dependencies** | none (C: stddef.h, stdint.h, string.h only; npm package has no runtime dependencies) |
| **Minimum toolchain** | C11 as tested in CI (GCC, Clang, MSVC /std:c11; the header also compiles as C++11/C++17); Node.js &gt;= 18 for the npm package |
| **Platforms** | any C target with uint64_t for the 32x32 product. CI covers x86-64, x86 ILP32, AArch64, big-endian s390x (qemu), MSVC x64 and wasm32. Endian-independent output. No Cortex-M, RV32 or GLSL builds are tested or shipped despite being the stated targets |
| **Thread safety** | C: no global mutable state (all static inline functions over caller-owned haya32x64_state), so concurrent calls on distinct states are safe; not otherwise documented. JS: one module-level wasm instance per realm, which is safe because JS runs single-threaded per isolate |
| **Drop-in for the baseline** | no |

## Gotchas

- Different digest from xxHash and from the same author's hayahash, so switching means migrating stored data. Digests of inputs 128 bytes and longer changed in v0.2.0 (pair-lane, then cross-feed kernel); digests under 128 bytes have been stable since the original 0xEAA8E435 version
- The JS API returns [low32, high32] word pairs, not a BigInt or a 16-byte string; use haya32x64Hex/digestHex for hex. Strings passed to stream.update() are UTF-8 encoded one at a time, so a surrogate pair split across two calls hashes differently from the one-shot form
- The hybrid engine copies every input of 16 bytes or more into one shared wasm memory that grows to the largest input seen and never shrinks (WebAssembly memory cannot shrink). Use haya32x64Pure or the ./pure export to avoid wasm entirely
- The digest is defined only for lengths 0..UINT32_MAX. The C one-shot takes size_t but casts the length to 32 bits for the finalizer, and the streaming API requires the caller to keep the cumulative length within UINT32_MAX

## Known shortcomings

- Pure-JavaScript hash: its win (4-byte keys 22.9 vs 39.4 ns, derived) is only against xxhash-wasm's XXH64 inside JS; native XXH3 is far faster. New repo (last commit 2026-09-19).
- Wins only on 4-8 byte binary keys in JS (1.7-2.1x vs xxhash-wasm); the string API is \~4.5x slower than xxhash-wasm (TextEncoder) and it loses at 1 MiB. Far behind native hashes on 64-bit hosts (XXH3 60.59 vs 7.50 bytes/cycle). Digest still experimental (output of 128 B and up changed from v0.1 to v0.2); stated Cortex-M/RV32/GLSL targets untested. 0 stars, \~28 npm downloads/month, solo author, 7 weeks old.

## Caveats and trade-offs

The win is only for short keys in JavaScript, and xxhash-wasm's latency includes JS-to-wasm call overhead. XXH64 via wasm wins 1 MiB bulk. In native SMHasher3 builds, 64-bit-multiply hashes are much faster: XXH3-64 runs at 60.59 B/cycle vs 7.50 on C8a. haya32x64 beats only 32-bit-arithmetic designs natively, e.g. XXH-32 bulk at 4.89 vs 7.50 B/cycle. One instance per host type and one Node/V8 version, and the author says to repeat before trusting small differences. Zero-star, roughly 7-week-old project from the same solo author as hayahash.

Restricted to 32-bit state/arithmetic to target pure JS, CSP-restricted/edge runtimes, Cortex-M, RV32 and GLSL; loses on bulk throughput to 64-bit-multiply hashes like XXH64; digest is still labeled experimental and frozen at an interim verification value.

## Maintenance

Active (last default-branch commit 2026-09-19, mostly dependabot), with 0 stars and about 28 npm downloads in the past month. It is a roughly 7-week-old solo-author project at v0.2.0 with an experimental digest, though the Unlicense single header is trivial to vendor and has an unusually thorough CI and test suite.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README table and docs/benchmarks.md compare against xxhash-wasm XXH64 and xxhashjs XXH64. The harness is public (bench/js.mjs, pinned xxhash-wasm 1.1.0), with raw JSON results in bench/results. Runtime (Node.js 24.18.0 / V8 13.6.233.17), GCC 15.2.0 -O3 -march=native -DNDEBUG for SMHasher3, and CPUs (EPYC 9R45, Neoverse V2) are all stated.
- **Verifier notes:** Numbers match the README and docs/benchmarks.md exactly. The record's \~1.7x-1.9x ratio was not marked as derived, so I fixed that and last_commit (default branch 2026-09-19; pushed_at 2026-09-26 comes from a dependabot/cursor branch). The language field says C, but the claimed win is for the pure-JS engine; the C header is the reference.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thevilledev/haya32x64>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/README.md>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/thevilledev/haya32x64/main/bench/package.json>
- **Sources the enricher read:**
  - <https://github.com/thevilledev/haya32x64>
  - <https://github.com/thevilledev/haya32x64/blob/main/README.md>
  - <https://github.com/thevilledev/haya32x64/blob/main/docs/benchmarks.md>
  - <https://github.com/thevilledev/haya32x64/blob/main/docs/design.md>
  - <https://github.com/thevilledev/haya32x64/blob/main/docs/quality.md>
  - <https://github.com/thevilledev/haya32x64/blob/main/docs/smhasher3.md>
  - <https://github.com/thevilledev/haya32x64/blob/main/haya32x64.h>
  - <https://github.com/thevilledev/haya32x64/blob/main/js/README.md>
  - <https://github.com/thevilledev/haya32x64/blob/main/js/package.json>
  - <https://github.com/thevilledev/haya32x64/blob/main/js/index.js>
  - <https://github.com/thevilledev/haya32x64/blob/main/js/wasm.js>
  - <https://github.com/thevilledev/haya32x64/blob/main/bench/README.md>
  - <https://github.com/thevilledev/haya32x64/blob/main/.github/workflows/ci.yml>
  - <https://github.com/thevilledev/haya32x64/issues?q=is%3Aissue>
  - <https://github.com/thevilledev/haya32x64/commits/main>
  - <https://github.com/thevilledev/haya32x64/tags>
  - <https://github.com/thevilledev/haya32x64/compare/v0.2.0...main>
  - <https://registry.npmjs.org/haya32x64>
  - <https://api.npmjs.org/downloads/point/last-month/haya32x64>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/thevilledev/haya32x64`) · [data/wave7/enrich/raw/github_com_thevilledev_haya32x64.json](../../../data/wave7/enrich/raw/github_com_thevilledev_haya32x64.json) (enrichment confidence 0.8)

</details>
