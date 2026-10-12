# sha2-wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript` · `Apache-2.0` · 🟢 active

> AssemblyScript SHA-256/SHA-512, HMAC and PBKDF2 compiled to a 13 KB wasm; claims 5-7% over hash-wasm under Bun.

| | |
|---|---|
| **Beats** | hash-wasm (WebAssembly SHA-2 compiled from heavily optimised C); native C built with gcc -O3 -march=native |
| **Claimed result** | '+5-7%' faster than hash-wasm (SHA-256 1.05x, SHA-512 1.07x); about 68% of native C speed. Throughput: SHA-256 217 MB/s, SHA-512 314 MB/s on 500 MB; small hashes \~2.20M ops/s (SHA-256, 55 B). |
| **Workload** | SHA-256 and SHA-512 over a 500 MB in-RAM buffer filled with 0x5a, digest outside the timed region, 2 warmups then the median of 5 samples, sha2-wasm then hash-wasm sequentially in one Bun process (test/full.bench.ts). HMAC, HMAC-verify, PBKDF2, small-hash and file-streaming rows are sha2-wasm only and not compared against a baseline. |
| **Metric** | throughput |
| **Hardware** | 'a modern x86-64 processor' (README); CPU model not stated |
| **Compiler and flags** | asc release target from asconfig.json: optimizeLevel 3, shrinkLevel 2, noAssert, converge (max 64 iterations), runtime stub; 13.2 KB wasm; run with Bun (JavaScriptCore); AssemblyScript and hash-wasm versions not pinned (package.json declares no dependencies); the gcc -O3 -march=native C comparison has no code in the repo |
| **Adoption** | 1 star, 0 forks, 12 commits (2026-07-27 to 2026-07-29) |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/edison-manrique/sha2-wasm) · [benchmark](https://github.com/edison-manrique/sha2-wasm) |

## Verdict

The author's test/full.bench.ts, run under Bun (JavaScriptCore) on an unnamed 'modern x86-64' CPU, hashed a 500 MiB buffer of 0x5a with a streaming hasher (2 warm-ups, median of 5, digest outside the timed region) and reported SHA-256 at 217 MB/s and SHA-512 at 314 MB/s, 1.05x and 1.07x hash-wasm's results from the same process. The HMAC, PBKDF2, small-hash and file rows have no baseline, and the '\~68% of native C (gcc -O3 -march=native)' line has no code behind it.

## Use it when

- Browser or edge code that needs SHA-256, SHA-512, HMAC and PBKDF2 together in one dependency-free \~13 KB wasm with synchronous calls after a one-time load.
- Many small messages hashed in a synchronous loop where avoiding per-call GC allocation matters (README: about 2.2 M SHA-256 hashes/s of 55 B under Bun, with no baseline for that row).
- Synchronous PBKDF2-HMAC-SHA256/512 (for example BIP39 seeds at 2048 iterations) where WebCrypto's promise-based deriveBits is inconvenient; the PBKDF2 path pre-hashes long passwords correctly and was checked against node:crypto for one short password.
- Single-caller streaming of a large Blob or File with a progress callback (hashFile), when nothing else calls the library until it finishes (see gotchas).

## Skip it when

- HMAC with keys longer than the hash block size (64 B for SHA-256, 128 B for SHA-512): the one-shot path returns non-standard MACs for most such key lengths (see gotchas).
- Node, Bun or Deno server code: node:crypto is used here only as a correctness oracle and never timed, and the catalogued tape-sha256 entry found node:crypto about 2.3x faster than a SIMD wasm SHA-256 inside Node.
- Interleaved or concurrent use (several streaming hashers, or one-shot HMAC/PBKDF2 calls while a hasher or hashFile is in flight): everything shares one instance's fixed scratch memory, and streaming contexts can be overwritten silently.
- One-shot hashing or hmacVerify of inputs over 1 MiB: they write the whole input into the 1 MiB zone and throw RangeError; use createHasher instead. pbkdf2 caps dkLen at 8192 bytes.
- Security-critical code or anything needing SHA-224, SHA-384 or SHA-512/256: the README says the code is unaudited, the repo has 12 commits and 1 star, and only SHA-256 and SHA-512 are implemented.

## How it is fast

Plain scalar SHA-2 with no SIMD: the compression loop runs the first 16 rounds fully unrolled and the remaining 48 in 16-round unrolled blocks, keeps the message schedule in 16 rolling locals instead of a 64-word array, uses the reduced Ch and Maj forms and bswap for big-endian loads, and is built by asc at optimizeLevel 3, shrinkLevel 2, noAssert with converge on the stub runtime. Input is copied into a static 1 MiB input zone and hashed in place, so a call allocates nothing on the GC heap except the returned Uint8Array. PBKDF2 precomputes the HMAC ipad/opad states once per key, so each iteration costs two compressions instead of four.

## Compared with alternatives

Against its baseline hash-wasm, catalogued in this wave and covering many more algorithms (MD5, SHA-3, xxHash, Argon2 and others), the measured edge is 5-7% on one engine and the HMAC and scratch defects above are absent there, so prefer hash-wasm; for small batched SHA-256 messages the tape-sha256 SIMD build reports 1.55x over hash-wasm in Node. Pick sha2-wasm only for a tiny synchronous SHA-2, HMAC and PBKDF2 bundle used by one caller at a time with HMAC keys no longer than one block.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (package.json declares no dependencies); building needs AssemblyScript (asc), esbuild and tsc, and the benchmark needs hash-wasm, none of which package.json declares |
| **Minimum toolchain** | Node &gt;= 18 (package.json engines), or Bun, Deno or a browser with WebAssembly; AssemblyScript version for rebuilding not pinned |
| **Platforms** | any WebAssembly host (wasm32, no SIMD or threads needed); README lists Node.js, Bun, Deno and browsers through bundlers such as Vite and Webpack |
| **Thread safety** | not documented; a global singleton instance with fixed scratch regions, so calls are not reentrant and interleaved users of one instance share state |
| **Drop-in for the baseline** | no |

## Gotchas

- Long-key HMAC bug (found by reading assembly/sha256.ts and sha512.ts): hmac_compute zeroes the 64/128-byte key block at the start of CRYPTO_WORK, then hashes a long key with hash_raw, whose context sits at the same address, so after hashing the second half of the key block (bytes 32-63 for SHA-256, 64-127 for SHA-512) holds the key's leftover partial block instead of zeros. Any key longer than the block whose length is not a multiple of it (RFC 4231 test case 6 uses a 131-byte key) therefore gets a non-standard MAC from Sha256.hmac, Sha512.hmac and HMAC.digest whenever key plus message fit in the 1 MiB fast path, and from hmacVerify always; the &gt;1 MiB slow path pre-hashes the key in TypeScript and is correct, so the same key gives different MACs depending on message size. The tests cover only RFC 4231 case 1 (20-byte key), and the &gt;1 MiB HMAC test checks only output length.
- Scratch overlap: the AssemblyScript one-shot routines use CRYPTO_WORK from its first byte (SHA-256 hmacVerify up to 400 B, SHA-512 HMAC about 720 B, SHA-512 hmacVerify 784 B, PBKDF2 about 800 B or 1,536 B plus the salt, SHA-512 hash up to 464 B), but the TypeScript ring that holds streaming-hasher contexts starts 384 B in. A hasher placed early in the ring, such as the first one created or hashFile's, which awaits between chunks, can be overwritten mid-stream by one of those calls with no error. reset()'s collision check compares the context with the IV, which never matches after a digest, so every reuse takes a new slot and the 32 KB ring wraps silently after about 120 SHA-256 or 62 SHA-512 allocations, possibly onto a live context. The README's claim that it never silently produces a corrupt hash is not supported by the code.
- Benchmark harness: one sequential, non-interleaved run per library in one Bun process (sha2-wasm SHA-256 and SHA-512 first, then hash-wasm), median of 5 on an unnamed CPU with hash-wasm unpinned, so a 1.05x/1.07x margin cannot be told apart from noise. The documented 'bun run bench' and test/bench.ts do not exist (the file is test/full.bench.ts, package.json has no bench script or hash-wasm dependency, and .gitignore says dependencies come from a parent workspace). The 500 MB digests are not checked against node:crypto (only 'abc' and empty-string vectors are), MB means MiB, and the \~68%-of-native-C figure has no C code in the repo.
- The static API throws until Sha2Wasm.load() or fromBuffer() has been awaited once. The README is Spanish only, and its project tree lists files (test/bench.ts) that are not in the repo.

## Known shortcomings

- Only 5-7% over hash-wasm on an unnamed x86-64 CPU under Bun; the documented bun run bench is broken (real file test/full.bench.ts, no bench script, no hash-wasm dependency); the "68% of native C" claim has no C code behind it.
- Enricher: one-shot HMAC with a key longer than the block and a length that is not a block multiple (RFC 4231 case 6, 131 B) gives a non-standard MAC because hash_raw's context aliases the zeroed key block (hits the Sha256/Sha512.hmac fast path under 1 MiB and hmacVerify always); the one-shot HMAC-SHA512, hmacVerify and PBKDF2 scratch overlaps the TS ring at CRYPTO_WORK+384 and can silently clobber a live streaming hasher (hashFile included); reset()'s IV check fails after every digest and the 32 KB ring wraps silently; the bench is 1.05x/1.07x from one sequential Bun run on an unnamed CPU with the bun run bench script missing, 500 MB digests unchecked and no code for the 'native C 68%' figure.

## Caveats and trade-offs

Claim is a 5-7% margin over hash-wasm (SHA-256 1.05x, SHA-512 1.07x), small enough to be run-to-run noise, measured once per library in sequence on one unnamed x86-64 CPU under Bun, not V8. The README names test/bench.ts and 'bun run bench', but the file is test/full.bench.ts and package.json has neither a bench script nor a hash-wasm dependency, so the documented command does not run as written. Only the large-buffer compute rows are compared against hash-wasm; the \~68%-of-native-C figure has no C harness in the repo. Correctness of both libraries is checked against node:crypto before timing. Brand-new repo (12 commits, July 2026), 1 star; hash-wasm (daninet/hash-wasm) is already verified in wave 13.

Zero-allocation design with static scratchpad in the data segment; SHA-2 and HMAC/PBKDF2 only; README is in Spanish.

## Maintenance

Active but brand-new: 12 commits from 2026-07-27 to 2026-07-29, npm versions 1.0.0 to 1.2.0 published within two days, 1 star, and unaudited by its own README; Apache-2.0 and small enough to vendor, but the long-key HMAC and scratch-overlap bugs need fixing before HMAC or streaming use in production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README numbers with public harness test/full.bench.ts (sha2-wasm vs hash-wasm on a 500 MB buffer, median of 5), but CPU described only as 'a modern x86-64 processor', AssemblyScript and hash-wasm versions unpinned, and the native-C comparison has no code in the repo.
- **Verifier notes:** README numbers match the record. Confirm at C; main shortcoming: tiny 5-7% margin over hash-wasm on one unnamed CPU, documented bench command broken (file is test/full.bench.ts, no bench script or hash-wasm dependency), native-C ratio unbacked by code. baseline_in_list set true because daninet/hash-wasm is in wave13 verified.json.
- **Fields the verifier corrected:** `baseline_in_list`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/edison-manrique/sha2-wasm>
  - <https://github.com/edison-manrique/sha2-wasm/commits/main>
  - <https://github.com/edison-manrique/sha2-wasm/tree/HEAD/test>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/test/full.bench.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/asconfig.json>
- **Sources the enricher read:**
  - <https://github.com/edison-manrique/sha2-wasm>
  - <https://github.com/edison-manrique/sha2-wasm/commits/main>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/package.json>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/asconfig.json>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/tsconfig.json>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/assembly/index.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/assembly/memory.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/assembly/common.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/assembly/constants.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/assembly/sha256.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/assembly/sha512.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/assembly/pbkdf2.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/src/sha2-wasm.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/src/allocator.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/src/sha256.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/src/sha512.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/src/hmac.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/src/types.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/test/full.bench.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/test/index.test.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/test/stress.test.ts>
  - <https://raw.githubusercontent.com/edison-manrique/sha2-wasm/HEAD/examples/server.ts>
  - <https://registry.npmjs.org/@edison-manrique%2Fsha2-wasm>
  - <https://registry.npmjs.org/hash-wasm/latest>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/edison-manrique/sha2-wasm`) · [data/wave13/enrich/raw/github_com_edison_manrique_sha2_wasm.json](../../../data/wave13/enrich/raw/github_com_edison_manrique_sha2_wasm.json) (enrichment confidence 0.7)

</details>
