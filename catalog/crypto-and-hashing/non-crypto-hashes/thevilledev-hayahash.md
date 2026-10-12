# hayahash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Unlicense` · 🟢 active

> Portable scalar 64/128-bit C hash; beats XXH3-64 by about 1.35x on 1 MiB bulk in SIMD-less wasm32.

| | |
|---|---|
| **Beats** | xxHash (XXH3-64 and XXH64) |
| **Claimed result** | wasm32 baseline build (no SIMD, no wide multiply) at 1 MiB: hayahash64 at 23.55 GB/s and hayahash128 at 23.34 GB/s, vs XXH3-64 at 17.41 GB/s and XXH64 at 14.71 GB/s. That is about 1.35x over XXH3-64 and 1.60x over XXH64 for hayahash64 (derived from page data). XXH64 still wins 8-byte chained latency (5.9 ns vs hayahash64's 7.7 ns); the raw record shows hayahash64 ahead of both from 32-byte keys up. |
| **Workload** | wasm32 build (Zig 0.16, -O3, no SIMD/wide-multiply) hashing 8-byte chained calls and 1 MiB bulk data under Node.js 26 / V8 on an Apple M1 Pro, comparing hayahash64/128 against ChibiHash v2, XXH3-64, XXH64, and rapidhash v3 |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (bare metal); wasm32 module run under Node 26.7.0 / V8 14.6.202.34 |
| **Compiler and flags** | zig cc 0.16.0 -O3 targeting baseline wasm32-wasi (no SIMD or wide-multiply instructions); timing loops run inside wasm; competitor sources fetched at pinned upstream revisions |
| **Adoption** | 2 stars (new project, created 2026-07-30) |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/thevilledev/hayahash) · [benchmark](https://github.com/thevilledev/hayahash/blob/main/docs/benchmarks.md) |

## Verdict

One baseline wasm32 module (zig cc 0.16.0 -O3, no SIMD or wide-multiply instructions) was run under Node 26.7.0 / V8 14.6 on a bare-metal Apple M1 Pro, with timing loops inside wasm. At 1 MiB it measured hayahash64 23.55 GB/s and hayahash128 23.34, vs XXH3-64 17.41 and XXH64 14.71 (about 1.35x and 1.60x); XXH64 kept the lowest 4-8-byte chained latency. xxHash and rapidhash sources were pinned to upstream commits, and there is a single host and a single run record dated 2026-08-09.

## Use it when

- Hashing inside WebAssembly without SIMD (browser or Node wasm32): at 1 MiB it measured 23.55 GB/s vs 17.41 for XXH3-64 and 14.71 for XXH64 on an M1 Pro under V8, and from 32-byte keys up it also had lower chained latency than both.
- Systems that must compute the same digest in several languages or byte orders (for example a Go or Rust server and a browser client), with everyone pinned to the same hayahash version.
- Chunked or streaming input where you want both a 64-bit and a 128-bit digest from one pass; on bulk input the 128-bit result costs only an extra finalizer (23.34 vs 23.55 GB/s in wasm).
- Targets without a fast 64x64-&gt;128 multiply (wasm32, 32-bit or exotic CPUs, MIPS64), where wide-multiply hashes fall back to emulation.

## Skip it when

- Native x86-64/AArch64 builds where XXH3 is available: the author makes no native 64-bit competitive claim, and in the SMHasher3 128-bit shootout XXH3-128 has higher bulk throughput (12.64 vs 9.77 B/cycle on M1, 48.91 vs 31.02 on Zen 5).
- Latency-critical keys of 4-16 bytes in wasm: XXH64 was faster at 4-8 bytes (5.9-6.0 vs 7.6-7.7 ns chained) and tied at 16 bytes.
- Anything that persists digests (on-disk indexes, wire formats, caches shared across deploys): digests changed in 0.3.0 and 0.5.0 (2026-08-09) and can change again before 1.0.
- Adversarial inputs or authentication: it is explicitly non-cryptographic, a secret seed only reduces HashDoS risk, and the design notes do not prove collision resistance for the full hash.
- Teams that need a proven dependency: the repo is about two months old with 2 stars, a single maintainer and no externally filed issues.

## How it is fast

It uses only 64-bit multiplication mod 2^64: no 64x64-&gt;128 multiply, no SIMD and no AES, which is all that baseline wasm32 provides. XXH3 and rapidhash must emulate wide multiplication there. Inputs of 320 bytes or more run 8 independent lanes over 64-byte blocks, where each absorb is h = (h ^ (w + rotl(prev_w, 27))) \* K, so the loop-carried chain is only add-&gt;mul. The 8 lanes then fold into 4, the tail uses overlapping wyhash-style reads, and inputs of 16 bytes or less take a dedicated two-multiply path. On Zen 4/5 with AVX-512DQ, GCC auto-vectorizes the bulk loop.

## Compared with alternatives

Over xxHash (XXH3-64/XXH64), pick it when the code runs as SIMD-less wasm32 or on hardware without wide multiply and keys are 32 bytes or more; natively, or for 4-16-byte keys, stay with xxHash. Over ChibiHash, which is in the same portable ordinary-multiply class, it was faster than ChibiHash v2 at every measured size on M1 and in wasm. Over haya32x64 by the same author, pick it when you are hashing bulk data through wasm or native code rather than tiny keys in pure JS.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C11 as built in CI; also compiled as C++11 and C++17 with g++ and clang++, and MSVC x64 is conformance-tested. Ports: Zig 0.16, Java 17+, .NET 8+, CPython 3.9+, Swift 5.9+, GHC 8.10+ |
| **Platforms** | any (portable scalar code); CI covers x86-64, AArch64, big-endian s390x, wasm32, MSVC x64 and MIPS64 n64 |
| **Thread safety** | Not documented; one-shot functions are static inline with no global state, and the streaming state is a caller-owned struct |
| **Drop-in for the baseline** | partial — the call shape (pointer, length, 64-bit seed) matches XXH3_64bits_withSeed/XXH64, but the function names, digest values and length type (signed ptrdiff_t) differ, so a thin wrapper is needed and stored hashes must be recomputed |

## Gotchas

- len is a signed ptrdiff_t and must be non-negative; the pointer may be null only when len is 0.
- hayahash128(...).lo is exactly hayahash64(...). Do not treat a 64-bit and a 128-bit digest of the same data as independent bits.
- The streaming state is about 544 bytes (a 448-byte buffer plus lane words). Totals under 448 bytes stay buffered and go through the one-shot path when you call digest.
- Speed depends on per-compiler dispatch shapes: GCC length tiers, Zen 4/5-only AVX-512DQ vectorization (without it Zen 5 bulk drops from about 61.6 to about 35 GB/s), and clang asm barriers. MSVC performance is untested. The wasm harness drops xxHash from -msimd128 builds, so there is no comparison against SIMD XXH3 in wasm.

## Known shortcomings

- WebAssembly (wasm32) hash: beats XXH3/XXH64 only inside WASM (zig 0.16.0, Node 26.7.0); native XXH3-128 is faster in bulk. New, single-author repo.
- Win holds only for wasm32 without SIMD, from one run on an M1 Pro/V8 (2026-08-09); the harness drops xxHash from -msimd128 builds, so there is no comparison with SIMD XXH3 in WASM; XXH64 is faster at 4-8 byte chained latency. Pre-1.0: digests changed in 0.3.0 and 0.5.0, so do not persist hashes. 2 months old, 2 stars, \~250 crates.io and \~290 npm downloads/month.

## Caveats and trade-offs

The win over XXH3-64 and XXH64 applies only to wasm32 without SIMD or wide multiply, which handicaps XXH3. docs/benchmarks.md explicitly makes no native 64-bit competitive claim against XXH3-64. In the native 128-bit SMHasher3 shootout, XXH3-128 has higher bulk throughput than hayahash128: 12.64 vs 9.77 B/cycle on M1 and 48.91 vs 31.02 on Zen 5, though XXH3-128 fails 26 test groups. Single host for the wasm run. Brand-new repo with negligible external usage.

Author explicitly states there is no current native (non-wasm) competitive claim vs wyhash/rapidhash/komihash/gxhash/mx3 since the digest last changed; the wasm baseline must emulate wide multiplication for rapidhash, which may unfairly penalize it relative to native builds.

## Maintenance

Actively developed by one author (v0.6.0 on 2026-09-13, several fixes committed 2026-09-26), Unlicense and one copyable header. It is still pre-1.0 with unstable digests and little outside use: 2 stars, about 250 crates.io downloads, about 290 npm downloads in the last month.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks.md's wasm32 table compares hayahash against XXH3-64 and XXH64, and the numbers match the raw record paper/results/apple-m1-pro-wasm-hayahash128.txt. The harness is public (tests/wasm/bench_wasm.c + driver.mjs), built with zig cc 0.16.0 -O3 for baseline wasm32-wasi, run under Node 26.7.0 / V8 14.6 on an Apple M1 Pro.
- **Verifier notes:** Numbers are accurate and the raw record matches the doc table. I added derived ratios, the exact toolchain and runtime versions, and the fact that xxHash wins natively. Metadata checks out: Unlicense, 2 stars, created 2026-07-30, last commit 2026-09-26.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thevilledev/hayahash>
  - <https://raw.githubusercontent.com/thevilledev/hayahash/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/thevilledev/hayahash/main/paper/results/apple-m1-pro-wasm-hayahash128.txt>
  - <https://github.com/thevilledev/hayahash/tree/main/tests/wasm>
- **Sources the enricher read:**
  - <https://github.com/thevilledev/hayahash>
  - <https://github.com/thevilledev/hayahash/blob/main/README.md>
  - <https://github.com/thevilledev/hayahash/blob/main/docs/benchmarks.md>
  - <https://github.com/thevilledev/hayahash/blob/main/paper/results/apple-m1-pro-wasm-hayahash128.txt>
  - <https://github.com/thevilledev/hayahash/blob/main/hayahash.h>
  - <https://github.com/thevilledev/hayahash/blob/main/docs/design.md>
  - <https://github.com/thevilledev/hayahash/blob/main/docs/stability.md>
  - <https://github.com/thevilledev/hayahash/blob/main/docs/quality.md>
  - <https://github.com/thevilledev/hayahash/blob/main/docs/implementation.md>
  - <https://github.com/thevilledev/hayahash/blob/main/docs/ports.md>
  - <https://github.com/thevilledev/hayahash/blob/main/SECURITY.md>
  - <https://github.com/thevilledev/hayahash/blob/main/CHANGELOG.md>
  - <https://github.com/thevilledev/hayahash/blob/main/VERSION>
  - <https://github.com/thevilledev/hayahash/blob/main/tests/wasm/Makefile>
  - <https://github.com/thevilledev/hayahash/blob/main/tests/wasm/bench_wasm.c>
  - <https://github.com/thevilledev/hayahash/blob/main/.github/workflows/ci.yml>
  - <https://github.com/thevilledev/hayahash/blob/main/rust/Cargo.toml>
  - <https://github.com/thevilledev/hayahash/issues>
  - <https://github.com/thevilledev/hayahash/pulls>
  - <https://github.com/thevilledev/hayahash/commits/main>
  - <https://hn.algolia.com/api/v1/search?query=hayahash&tags=story>
  - <https://crates.io/api/v1/crates/hayahash>
  - <https://api.npmjs.org/downloads/point/last-month/hayahash>
  - <https://pypi.org/pypi/hayahash/json>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/thevilledev/hayahash`) · [data/wave7/enrich/raw/github_com_thevilledev_hayahash.json](../../../data/wave7/enrich/raw/github_com_thevilledev_hayahash.json) (enrichment confidence 0.8)

</details>
