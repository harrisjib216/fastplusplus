# xoroshiro128starstar (AssemblyScript WebAssembly seeded PRNG)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript` · `BSD-2-Clause` · 🔴 abandoned

> 262-byte AssemblyScript WebAssembly xoroshiro128\*\* giving a seeded Math.random replacement for Node; about 10% faster than 2018 V8 Math.random.

| | |
|---|---|
| **Beats** | Math.random (V8) and the seedrandom npm package |
| **Claimed result** | wasmrandom 81,321,598.18 op/s vs Math.random 73,658,101.35 op/s (about 1.10x, derived from page data) vs seedrandom 24,057,933.98 op/s (about 3.4x, derived); the 262-byte module keeps its state in two u64 globals. |
| **Workload** | Generating random integers 0 &lt;= n &lt; 10, 'wasmrandom' vs Math.random vs seedrandom, via do-you-even-bench in Node.js. |
| **Metric** | throughput |
| **Compiler and flags** | README numbers were measured on the August 2018 build: asc --baseDir assembly -Oz -b index.wasm -t index.wat index.ts --sourceMap --noDebug (package.json at commits c7cf3b3 and e5e290b), with AssemblyScript from GitHub master, unpinned. The current -O3 --validate build and the 52-bit next() float conversion came in commit bc56b66 (2019-01-02) and were never re-benchmarked. Run with Node.js v10.3.0, node --expose-gc bench.js (do-you-even-bench). |
| **Adoption** | 13 stars |
| **Last commit** | 2019-01-02 |
| **Links** | [repository](https://github.com/krisselden/xoroshiro128starstar) · [benchmark](https://github.com/krisselden/xoroshiro128starstar) |

## Verdict

First-party README run on Node v10.3.0 (CPU not stated) with do-you-even-bench (a Benchmark.js wrapper) in a loop of freq[(f() \* 10) | 0]++ calling a global function: the 2018 -Oz Wasm build did 81,321,598 op/s against V8 Math.random at 73,658,101 op/s (about 1.10x, derived from page data) and seedrandom's default ARC4 at 24,057,933 op/s (about 3.4x, derived), with uniform 0-9 frequency counts printed for all three. That build is the one on npm today; the 2019 master build was never measured.

## Use it when

- Node.js code that needs a reproducible, seedable stream of doubles in [0, 1) with a Math.random-shaped API (simulations, tests, procedural generation, the random npm package's random.use()).
- Replacing seedrandom's default ARC4 generator when per-call speed matters: the README run shows about 3.4x its throughput (derived from page data).
- Many independent generators in one process: each factory call creates its own Wasm instance with 16 bytes of state and no memory pages.
- Code that wants a tiny dependency: the published package is a 262-byte module plus a 1.3 KB loader and no runtime dependencies.

## Skip it when

- Anything security-sensitive (tokens, keys, shuffles that must not be predicted): xoroshiro128\*\* is not a cryptographic generator; use crypto.getRandomValues or crypto.randomBytes.
- Browsers without a bundler: index.js reads the .wasm with fs.readFileSync(__dirname + ...), so it only runs on Node as published (issue #4, open since 2020).
- Bulk generation (filling typed arrays with millions of values): there is no batch API, so every number pays a JS-to-Wasm call; a generator that writes into linear memory, or a pure-JS xorshift on 32-bit halves, may be faster on current engines.
- When you need integers, 64-bit outputs or bit-exact streams that match other xoroshiro128\*\* implementations: only next() as a double is exported, and the seeding is not the reference splitmix64 sequence (see gotchas).
- Projects that need a maintained dependency or the newer xoshiro256\*\* family: no release since August 2018, last commit January 2019, and the request for xoshiro256 (issue #3) was declined.

## How it is fast

The generator is a handful of 64-bit multiplies, rotates, shifts and xors, which WebAssembly runs natively as i64 ops instead of emulating 64-bit arithmetic in JS doubles or 32-bit halves the way pure-JS seeded generators must. State lives in Wasm globals rather than linear memory, so each call is a bare global load/store plus one u64-to-double conversion (the published 1.1.1 build multiplies a 53-bit integer by 2^-53; GitHub master ORs 52 bits into the exponent-1 mantissa and subtracts 1.0). The cost that remains is the JS-to-Wasm call per number, which is why the margin over V8's own Math.random was small.

## Compared with alternatives

Among catalogued AssemblyScript entries, pick this over tinymt-wasm-typescript-benchmark when you want a published npm package with a Math.random-compatible double API and xoroshiro128\*\*'s 64-bit outputs rather than a TinyMT32 benchmark repo; galois, superfasthash and long.js solve different problems (field arithmetic, hashing, 64-bit integer ops).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (Node fs and WebAssembly); the build needs the AssemblyScript compiler (asc), pinned only to GitHub master in devDependencies |
| **Minimum toolchain** | Node.js with WebAssembly support (benchmarked on Node v10.3.0); a browser needs a bundler or a custom loader |
| **Platforms** | Node.js on any CPU with a WebAssembly engine; browser use not supported out of the box |
| **Thread safety** | Each factory call creates its own Wasm instance with its own two globals; a single next() function is not meant to be shared across worker threads (instances are per-isolate). Not documented beyond that. |
| **Drop-in for the baseline** | partial — next() has Math.random's signature and range, so assigning it where a () =&gt; number is expected works, but it is a separate function you must create and seed, not a patch of Math.random, and the README's `const Math.random = require(...)(SEED)` snippet is not valid JavaScript |

## Gotchas

- npm and GitHub differ: the latest npm release, 1.1.1 (2018-08-26), ships the -Oz build with the 53-bit next() that the README benchmarked; the -O3 --validate build and 52-bit mantissa conversion merged from PR #2 (commit bc56b66, 2019-01-02) were never published, and the .wasm is gitignored, so using master means building it yourself. The master next() tops out at 1 - 2^-52 even though the comments still say 0.9999999999999999.
- Seed 0 (or -0) and any non-number seed silently fall back to Math.random() for the seed, so the stream is not reproducible; the seed is used as the raw IEEE-754 bit pattern of the double.
- Seeding is not the reference splitmix64 procedure: s1 = splitmix64(s0) chains the first output instead of advancing the splitmix state by the golden-ratio constant, so streams will not match other xoroshiro128\*\* ports seeded with splitmix64 from the same value (the core next() step itself matches the reference algorithm).
- The README benchmark is a single Benchmark.js run through do-you-even-bench, which prints only ops/s (no relative margin of error), with no CPU named and on Node 10.3 (V8 6.7); the 10% lead over Math.random has not been re-measured on any later engine.

## Known shortcomings

- Only about 1.10x over V8 Math.random on Node 10.3 with no CPU; README numbers come from a 2018 -Oz --noDebug build, not a current -O3 build.
- npm 1.1.1 (2018-08-26) is the -Oz, 53-bit next() build the README benchmarked; GitHub master (-O3, 52-bit, PR #2 / bc56b66) was never published and the wasm is gitignored. The benchmark is one Benchmark.js run via do-you-even-bench printing ops/s only, no margin of error, no CPU. Seed 0 or a non-number silently reseeds from Math.random; s1 = splitmix64(s0) chains the output rather than the reference splitmix sequence, so streams differ from other ports; master's comments claim a maximum of 0.9999999999999999 while the actual is 1 - 2^-52; the README's 'const Math.random =' snippet is invalid JS; Node-only (issue #4). No correctness bug in next().

## Caveats and trade-offs

Node 10.3 era numbers (V8 6.7), no CPU stated; the margin over Math.random is only about 10% (derived from page data), and the seeded JS competitor is seedrandom's default ARC4 generator (a slower algorithm). The README numbers predate the 2019-01-02 commit that switched the build from -Oz to -O3 and changed next() from a 53-bit multiply to a 52-bit mantissa trick; that commit fixed no correctness bug (the 2018 xoroshiro128\*\* update is equivalent to the reference), but the published numbers are for the older build. Each call crosses the JS-to-WASM boundary; there is no batch API. Abandoned since 2019.

Small 262-byte module with no memory pages; seeded and reproducible unlike Math.random. Includes the JS/Wasm call overhead per number.

## Maintenance

Abandoned since January 2019 (npm 1.1.1 from August 2018, two open issues answered in 2022 without code changes), but BSD-2-Clause and a 262-byte module plus a 40-line loader, so it is trivial to vendor or rebuild, and the algorithm is equivalent to the public-domain reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmark section shows first-party do-you-even-bench output (bench.js is public) with wasmrandom 81,321,598.18 op/s vs Math.random 73,658,101.35 op/s vs seedrandom 24,057,933.98 op/s and a uniform frequency check, Node v10.3.0 stated, but no CPU model and an unpinned AssemblyScript master build, so C, not A.
- **Verifier notes:** Numbers match the README exactly and the benchmark is real (bench.js increments a frequency array and prints uniform counts, so not a no-op). Main shortcomings: no CPU model, only about 1.10x over V8 Math.random on Node 10.3, and the numbers were taken on the 2018 -Oz build rather than the current -O3 one. License BSD-2-Clause (LICENSE.md), 13 stars, last commit 2019-01-02, all as recorded.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/krisselden/xoroshiro128starstar>
  - <https://github.com/krisselden/xoroshiro128starstar/commits>
  - <https://github.com/krisselden/xoroshiro128starstar/commit/bc56b66>
  - <https://github.com/krisselden/xoroshiro128starstar/commit/95a342b>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/README.md>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/bench.js>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/package.json>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/index.js>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/assembly/index.ts>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/c7cf3b3/package.json>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/c7cf3b3/assembly/index.ts>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/e5e290b/package.json>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/e5e290b/README.md>
- **Sources the enricher read:**
  - <https://github.com/krisselden/xoroshiro128starstar/commits>
  - <https://github.com/krisselden/xoroshiro128starstar/issues?q=is%3Aissue>
  - <https://github.com/krisselden/xoroshiro128starstar/issues/1>
  - <https://github.com/krisselden/xoroshiro128starstar/issues/3>
  - <https://github.com/krisselden/xoroshiro128starstar/issues/4>
  - <https://github.com/krisselden/xoroshiro128starstar/pull/2>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/README.md>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/bench.js>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/package.json>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/index.js>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/index.d.ts>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/assembly/index.ts>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/c7cf3b3/assembly/index.ts>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/c7cf3b3/package.json>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/c7cf3b3/index.js>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/e5e290b/assembly/index.ts>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/e5e290b/package.json>
  - <https://raw.githubusercontent.com/krisselden/xoroshiro128starstar/e5e290b/index.js>
  - <https://registry.npmjs.org/xoroshiro128starstar>
  - <https://registry.npmjs.org/xoroshiro128starstar/-/xoroshiro128starstar-1.1.1.tgz>
  - <https://registry.npmjs.org/do-you-even-bench>
  - <https://registry.npmjs.org/do-you-even-bench/-/do-you-even-bench-1.0.5.tgz>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/krisselden/xoroshiro128starstar`) · [data/wave13/enrich/raw/github_com_krisselden_xoroshiro128starstar.json](../../../data/wave13/enrich/raw/github_com_krisselden_xoroshiro128starstar.json) (enrichment confidence 0.72)

</details>
