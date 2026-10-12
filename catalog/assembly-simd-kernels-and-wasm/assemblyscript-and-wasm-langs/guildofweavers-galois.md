# galois (finite-field arithmetic with AssemblyScript WebAssembly acceleration)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `AssemblyScript` · `MIT` · 🔴 abandoned

> TypeScript prime-field library whose AssemblyScript WASM backend runs 128-bit vector field ops about 9x faster than its JS BigInt path.

| | |
|---|---|
| **Beats** | JavaScript BigInt arithmetic (256-bit and 128-bit prime fields) in the same library on Node.js |
| **Claimed result** | Additions 44,000,000 ops/s (WASM 128-bit) vs 5,000,000 (JS BigInt 128-bit) vs 3,200,000 (256-bit); multiplications 16,300,000 vs 1,850,000 vs 950,000; exponentiations 97,000 vs 10,500 vs 3,200 (about 8.8x, 8.8x and 9.2x vs 128-bit BigInt, derived from page data). |
| **Workload** | Prime-field operations for modulus 2^128-k: additions, multiplications and exponentiations per second, JS BigInt vs the WASM implementation; README also says vector, matrix and polynomial operations speed up 6x-10x. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-7300U @ 2.60GHz (single thread) |
| **Compiler and flags** | AssemblyScript 0.8.1 (package-lock.json); WASM module built by gulpfile.js with 'npx asc ... --validate --importMemory --enable bulk-memory -O3'; Node.js/V8 version not stated |
| **Adoption** | 43 stars |
| **Last commit** | 2022-05-22 |
| **Links** | [repository](https://github.com/GuildOfWeavers/galois) · [benchmark](https://github.com/GuildOfWeavers/galois) |

## Verdict

On an Intel Core i5-7300U, single thread, Node.js version unstated, the README reports rounded element-wise ops/s for the library's 128-bit WASM field against its own JS BigInt field: additions 44.0M vs 5.0M, multiplications 16.3M vs 1.85M, exponentiations 97,000 vs 10,500 (about 8.8x, 8.8x and 9.2x, derived from page data); the 256-bit BigInt column is lower still (3.2M, 0.95M, 3,200). The numbers come from one Date.now() pass over 2^18-element vectors in tests/benchmarks.ts, which checks every WASM result against the JS result; AssemblyScript 0.8.x with asc -O3.

## Use it when

- Node.js STARK or polynomial-commitment prototypes that work in a 128-bit prime field of the form 2^128 - k (k &lt; 2^64) and process vectors of thousands to hundreds of thousands of elements.
- Bulk element-wise add/sub/mul/exp, matrix products, FFT-based evaluation and interpolation where data can stay in WASM vectors between calls.
- You already use the JS BigInt field of this library and want the roughly 8.8x (add, mul) to 9.2x (exp) vector speedup by passing useWasm or a WebAssembly.Memory.
- Short-lived processes or flows that create a bounded number of vectors, since WASM memory is never released.

## Skip it when

- Scalar arithmetic: WasmPrimeField128.add/mul/exp/inv on single bigints delegate to the JS BigInt field, so per-element call patterns get no speedup.
- 256-bit or other moduli (for example BN254 or BLS12-381 scalar fields): no WASM path exists (issue #9 open since 2019), and the README's 256-bit column is plain BigInt.
- Long-running services: WASM memory used by vectors and matrices is never freed (README note, issue #10 open since 2019), so fields must be re-created periodically.
- Browsers without a bundler shim: the loader reads prime128.wasm with fs.readFileSync and __dirname (issue #29 'Building for browser?' is unanswered).
- Secret-dependent cryptographic code: the maintainer says to assume nothing is constant time (issue #13), and the WASM modAdd/modMul still branch on zero operands and on comparisons.

## How it is fast

Vector and matrix elements live in WebAssembly linear memory as two u64 limbs each, and the AssemblyScript kernel (lib/assembly/prime128.as.ts, built with asc -O3) loops over them without allocating a JS BigInt per result. Modular multiplication is an unrolled two-iteration word-by-word reduction that estimates the quotient as z &gt;&gt; 128, which works because the modulus is 2^128 - k with k &lt; 2^64; 64x64-bit products are assembled from 32-bit halves since WASM has no wide multiply. Exponentiation is square-and-multiply and inversion is binary extended GCD, both in WASM.

## Compared with alternatives

Pick galois over long.js (64-bit integers with a WASM multiply/divide fast path) or berith (fixed Ed25519/X25519 curves) when you need general prime-field vector, matrix and FFT polynomial arithmetic in a 2^128 - k field on Node; for any other field size or a browser target none of these fits and a maintained library is the better choice.

## Integration

| | |
|---|---|
| **Form** | module (npm package @guildofweavers/galois 0.4.22, compiled TypeScript plus prime128.wasm) |
| **Dependencies** | @assemblyscript/loader 0.8.x at runtime; AssemblyScript 0.8.x, TypeScript, gulp and mocha to build |
| **Minimum toolchain** | Node.js 12.7 or newer (package.json engines; needs BigInt and BigUint64Array); WASM bulk-memory support |
| **Platforms** | Node.js (any CPU V8 runs on); browser use not supported out of the box |
| **Thread safety** | not documented; each field instance owns one WASM instance with shared input/output scratch buffers and no locking |
| **Drop-in for the baseline** | partial: same FiniteField API as the library's JS BigInt field, enabled by a flag, but only for moduli in (2^128 - 2^64, 2^128), and Vector/Matrix objects from a JS field cannot be passed to WASM-field methods (they are cast to WasmVector128 without checks) |

## Gotchas

- Harness flaw behind the README table: tests/benchmarks.ts times one pass of 2^18 elements per operation with Date.now() (1 ms resolution), no warm-up or repetition, JS section first; the 44M additions/s figure corresponds to a single interval of about 6 ms (derived: 262,144 / 44M), so plus or minus 1 ms is about 17%. The WASM timings exclude copying inputs into WASM memory (timed separately) and never copy results back, the benchmark pre-allocates a 256 MB WebAssembly.Memory where the default is 10 pages that grow on demand, and the 256-bit JS section is commented out (and calls f1.divVectorElements on 256-bit vectors), so the 256-bit column cannot be regenerated.
- WasmVector128.load and setValue do not reduce inputs mod p: setValue only rejects values above 2^128 - 1 and load silently splits any bigint into two u64 words, while the WASM kernels assume canonical elements below the modulus; pass only reduced, non-negative values.
- The modulus is not validated as prime (issue #5 open), and the README example uses a 256-bit modulus that gets no WASM acceleration.
- The maintainer said in issue #11 (Aug 2019) that enabling -O3 made no noticeable difference; the arrayElementOp loop dispatches each element through a function-pointer call, so the kernel is not inlined.

## Known shortcomings

- Numbers from an informal single Date.now() pass (tests/benchmarks.ts, asc -O3 on AssemblyScript 0.8.1) with the Node version unstated; the table cannot be regenerated (256-bit section commented out). Abandoned since 2022-05-22.
- Harness flaw: tests/benchmarks.ts times one Date.now() pass per operation (1 ms resolution, no warm-up), so the 44M additions/s figure is a single \~6 ms interval (about +/-17%); WASM timings exclude copying data in and out, memory is preallocated at 256 MB, the 256-bit JS section is commented out, scalar add/mul/exp still use JS BigInt, load/setValue do not reduce inputs mod p, and WASM memory is never freed. Abandoned since 2022-05-22 on AssemblyScript 0.8.x.

## Caveats and trade-offs

The README calls these 'very informal benchmarks' and gives rounded ops/s figures. The harness is tests/benchmarks.ts (not linked from the README): one Date.now() pass per operation over 2^18-element vectors, with no warm-up or repetition. It prints milliseconds, not the README's ops/s, and its 256-bit JS section is commented out in the current code, so the table cannot be regenerated as-is. The harness checks every WASM result against the JS BigInt result. The Node.js version is unstated and AssemblyScript 0.8.1 is very old. The comparison is against the library's own JS BigInt path only, not C++ or other WASM toolchains. The WASM path covers only moduli 2^128-k with k &lt; 2^64, and WASM memory is never freed (README note). Last commit 2022-05-22.

WASM path exists only for prime fields with modulus 2^128-k (k &lt; 2^64). README notes WASM memory cannot be freed, so FiniteField objects may need re-creation to avoid leaks.

## Maintenance

Abandoned: last code change 2022-05-22 (a merged PR adding binomial support to interpolateRoots), the substantive work dates from 2019, 8 open issues and 18 open PRs sit unanswered, and it is pinned to AssemblyScript 0.8.x; MIT-licensed and small enough to vendor if you can live with the WASM memory leak.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section has the exact ops/s table (JS BigInt 256-bit, JS BigInt 128-bit, WASM 128-bit) on an Intel Core i5-7300U, and the harness is public (tests/benchmarks.ts) with build flags in gulpfile.js (asc -O3, AssemblyScript 0.8.1 per package-lock.json). It stays C because the Node.js/V8 version that runs both sides is not stated, the author calls the numbers 'very informal', and the table is a rounded hand conversion that the current script cannot regenerate (it prints milliseconds per 2^18-element pass and its 256-bit section is commented out).
- **Verifier notes:** Numbers match the README exactly (additions 44.0M vs 5.0M vs 3.2M, multiplications 16.3M vs 1.85M vs 0.95M, exponentiations 97,000 vs 10,500 vs 3,200 ops/s); derived ratios of 8.8x, 8.8x and 9.2x over 128-bit BigInt are correct. The README's separate claim that vector, matrix and polynomial ops speed up 6x-10x also appears there. Shortcomings: informal single-pass harness, Node version unstated, baseline is the library's own JS BigInt code, abandoned (last commit 2022-05-22, 43 stars, MIT).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-54 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/README.md>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/package.json>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/package-lock.json>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/gulpfile.js>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/tests/benchmarks.ts>
  - <https://github.com/GuildOfWeavers/galois>
  - <https://github.com/GuildOfWeavers/galois/commits>
  - <https://github.com/GuildOfWeavers/galois/tree/master/tests>
- **Sources the enricher read:**
  - <https://github.com/GuildOfWeavers/galois>
  - <https://github.com/GuildOfWeavers/galois/commits/master>
  - <https://github.com/GuildOfWeavers/galois/tree/master/lib>
  - <https://github.com/GuildOfWeavers/galois/tree/master/lib/assembly>
  - <https://github.com/GuildOfWeavers/galois/issues?q=is%3Aissue>
  - <https://github.com/GuildOfWeavers/galois/issues/11>
  - <https://github.com/GuildOfWeavers/galois/issues/13>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/README.md>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/package.json>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/gulpfile.js>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/tests/benchmarks.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/index.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/PrimeField.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/utils.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/subfields/index.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/subfields/WasmPrimeField128.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/assembly/index.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/assembly/prime128.as.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/structures/index.ts>
  - <https://raw.githubusercontent.com/GuildOfWeavers/galois/HEAD/lib/structures/WasmVector128.ts>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/guildofweavers/galois`) · [data/wave13/enrich/raw/github_com_guildofweavers_galois.json](../../../data/wave13/enrich/raw/github_com_guildofweavers_galois.json) (enrichment confidence 0.65)

</details>
