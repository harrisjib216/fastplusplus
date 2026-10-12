# wa-ulid

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust compiled to WebAssembly (Cargo.toml in repo) with a TypeScript wrapper` · `MIT` · 🟡 stale

> Rust-to-WebAssembly ULID generator with the ulid npm API; about 43x faster ulid() than ulid 2.3.0 in Node.

| | |
|---|---|
| **Beats** | ulid 2.x (ulid/javascript, the reference pure-JavaScript ULID generator; devDependency ^2.3.0) |
| **Claimed result** | ulid(): 44,758 ops/s (ulid) vs 1,933,859 ops/s (wa-ulid) = 43.20x; decodeTime 1,951,730 vs 5,336,862 (2.73x); monotonic ulid 2,382,881 vs 3,505,757 (1.47x); encodeTime 3,863,741 vs 4,904,495 (1.27x). |
| **Workload** | ULID generation (ulid(), monotonicFactory()) and time encode/decode, ops/sec measured with Benchmark.js in Node (benchmark.js, pnpm benchmark). |
| **Metric** | throughput |
| **Hardware** | Apple M2 Pro |
| **Compiler and flags** | wasm-pack build --target web --release with Cargo release lto=true; .node-version pins Node 20.12.2; rustc version not stated |
| **Adoption** | 21 stars |
| **Last commit** | 2024-05-11 |
| **Links** | [repository](https://github.com/yujiosaka/wa-ulid) · [benchmark](https://github.com/yujiosaka/wa-ulid) |

## Verdict

Author's Benchmark.js run in Node (.node-version pins 20.12.2; the version used is not stated) on an Apple M2 Pro, comparing wa-ulid 1.0.0 with ulid 2.3.0 (pnpm-lock), wasm init done before timing: ulid() 1,933,859 vs 44,758 ops/s (43.2x), decodeTime 5,336,862 vs 1,951,730 (2.73x), monotonic ulid 3,505,757 vs 2,382,881 (1.47x), encodeTime 4,904,495 vs 3,863,741 (1.27x). The 43x row measures ChaCha12-in-wasm against 16 crypto.randomBytes(1) calls per ULID, and the current ulid 3.0.2 still draws one byte per character (now through getRandomValues on a 1-byte array), but no run against ulid 3.x exists.

## Use it when

- Node.js 20+ backends that mint many non-monotonic ULIDs per second with ulid 2.x and where ULID generation shows up in profiles (about 22 us per ulid() call in the baseline vs about 0.5 us here, as measured by the author).
- Code already written against the ulid 2.x API that can absorb one `await init()` at startup.
- Services that want a CSPRNG-backed ULID without paying one native crypto call per character.

## Skip it when

- Browser bundles: the package adds about 110 KB of JavaScript (a 68 KB wasm binary inlined as base64, once in the ESM and once in the UMD build) versus 4.7 KB for ulid, and the wasm is compiled synchronously at import time.
- Monotonic ULID generation inside one millisecond, encodeTime or decodeTime alone: the gains there are 1.27x to 2.73x, and a JavaScript implementation that avoids per-call allocations would probably close them (not measured).
- When a pure JavaScript ULID library that draws its randomness in batches is acceptable: the 43x comes from replacing per-byte crypto calls, which JS can also do, without a 110 KB module or an init step (uniku's README claims a 116x ULID speedup in TypeScript; not verified here).
- Projects that need maintenance or a working npm install: one release (1.0.0, 2024-05-05), four commits, nothing since 2024-05-11.
- Custom PRNGs via factory(prng): wasm calls back into JavaScript once per character, and that path was never benchmarked.

## How it is fast

The headline gain is random-number plumbing, not wasm code generation: ulid 2.3.0 draws one byte per character through Node's crypto.randomBytes(1), which means 16 native calls and Buffer allocations per ULID, while wa-ulid fills all 16 characters inside wasm from rand 0.8's ThreadRng (a userspace ChaCha12 CSPRNG, rand_chacha 0.3.1) seeded through getrandom's js feature, then returns one string. decodeTime gains 2.7x because the baseline builds arrays (substr/split/reverse/reduce with Math.pow per character) where the Rust code runs a plain loop. encodeTime and the monotonic path, which mostly increments the previous random part within the same millisecond, gain only 1.27x and 1.47x once the RNG is out of the picture.

## Compared with alternatives

No other ULID generator is catalogued. Siblings such as hash-wasm and xxhash-wasm win through compute kernels in wasm, while wa-ulid's 43x win comes from avoiding per-byte crypto calls. Pick it only for a Node backend locked into the ulid 2.x API; a pure JavaScript ULID with batched randomness is the likelier better choice.

## Integration

| | |
|---|---|
| **Form** | module (npm package wa-ulid 1.0.0: ESM and UMD builds with the wasm inlined as base64, plus a CLI) |
| **Dependencies** | none at runtime; building from source needs Rust, wasm-pack and pnpm (crates rand 0.8.5, rand_chacha 0.3.1, getrandom 0.2.14 with the js feature, wasm-bindgen 0.2.92) |
| **Minimum toolchain** | Node.js 20 (package engines field; .node-version pins 20.12.2); Rust version not documented |
| **Platforms** | Node.js 20+ (benchmarked on Apple M2 Pro); browsers are claimed, but the synchronous compile of a 68 KB module is a risk there |
| **Thread safety** | not documented; each JavaScript realm or worker gets its own wasm instance and its own thread-local RNG, and a monotonicFactory() keeps its state in its own wasm-side context |
| **Drop-in for the baseline** | partial: same function names and signatures as ulid 2.x, but an `await init()` is required before use, detectPrng arguments are ignored, and invalid non-ASCII inputs can trap instead of throwing ulid's errors |

## Gotchas

- The published npm tarball (1.0.0) still declares "postinstall": "pnpm build" but ships only dist/, bin/, README and LICENSE (no Cargo.toml, src or rollup config). npm and Yarn classic run dependency postinstall scripts, so `npm install wa-ulid` would try to run pnpm and wasm-pack inside node_modules and should fail unless scripts are skipped (--ignore-scripts, or pnpm's default blocking of dependency build scripts). Not tested here; inferred from the tarball's package.json.
- The 68 KB wasm is listed under @rollup/plugin-wasm's `sync` option, so importing the package runs `new WebAssembly.Module()` synchronously on a base64-decoded buffer. The plugin's own README says runtimes allow synchronous compilation only for small modules (under 4 KB), so the README's 'fully functional in browsers' is doubtful on a browser main thread. The import-time compile cost is also excluded from the benchmark, which awaits init() before timing.
- Byte and character indexing are mixed in the Rust code: decode_time checks the byte length and then slices &id[0..10], and replace_char_at compares an index against the byte length but indexes a Vec&lt;char&gt;. Non-ASCII input can therefore panic, which in wasm surfaces as a RuntimeError ('unreachable') rather than ulid's 'malformed ulid' error.
- The README says randomness 'does not utilize the browser or Node.js crypto APIs', but this holds per call only: the shipped glue imports crypto.getRandomValues and randomFillSync, which getrandom uses to seed the ChaCha12 generator. Characters come from a uniform float in [0,1) times 32, slightly better than ulid 2.3.0, whose byte/0xff mapping with a clamp over-weights 'Z'.

## Known shortcomings

- The 43x row's baseline calls crypto.randomBytes(1) per character while wa-ulid uses a buffered ChaCha12 thread_rng; stale since 2024-05-11, 21 stars.
- The npm 1.0.0 tarball still declares postinstall 'pnpm build' but ships only dist/ (no Cargo.toml or src), so a plain npm install should fail unless scripts are skipped (inferred from the tarball's package.json, not run). The 68 KB wasm is compiled synchronously with new WebAssembly.Module at import, which browsers allow only for small modules, so 'fully functional in browsers' is doubtful; non-ASCII input to decode_time or replace_char_at can trap. The 43x row is RNG batching against 16 crypto.randomBytes(1) calls, measured against ulid 2.3.0 only (ulid 3.0.2 still draws one byte per character).

## Caveats and trade-offs

First-party, 4 commits, untouched since May 2024. The 43x ulid() row measures random-number batching, not wasm codegen: ulid 2.3.0 calls Node crypto.randomBytes(1) once per character (16 calls and Buffer allocations per ULID), while wa-ulid fills the 16 characters from rand::thread_rng (a userspace ChaCha12 CSPRNG seeded once through getrandom's js feature). Both are cryptographically secure, so the row is a real API-level win, but a JS implementation that batches getRandomValues would close most of the gap (not measured). The README's statement that randomness does not use browser or Node crypto APIs is only true per call; the seed comes from them through getrandom. The other rows are 1.27x-2.73x. A user-supplied PRNG path calls back into JS once per character and was not benchmarked. Single machine; numbers not reproduced independently. [retier] First-party, 4 commits, untouched since May 2024. The 43x ulid() row measures random-number batching, not wasm codegen: ulid 2.3.0 (and still 3.0.2) calls crypto.randomBytes(1) once per character while wa-ulid fills 16 characters from a userspace ChaCha12 generator seeded once; a JS implementation that batches getRandomValues would close most of the gap. The npm 1.0.0 tarball still declares postinstall 'pnpm build' but ships only dist/, so a plain npm install should fail unless scripts are skipped (inferred from the tarball, not run). The 68 KB wasm is compiled synchronously with new WebAssembly.Module at import, which browsers allow only for small modules. Non-ASCII input to decode_time or replace_char_at traps ('unreachable') instead of raising ulid's error.

Wasm module adds about 110 KB versus 4.7 KB for ulid; README recommends it mainly for backend use.

## Maintenance

Stale: four commits, all in May 2024, one npm release (1.0.0 on 2024-05-05) and one closed issue. It is MIT-licensed and small (about 170 lines of Rust), so vendoring or rebuilding is easy, but the published npm package's leftover postinstall hook and the synchronous 68 KB wasm compile make the package itself risky to depend on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table against the ulid npm package on an Apple M2 Pro, with the Benchmark.js harness public in benchmark.js; rustc version and run conditions are not stated (Node 20.12.2 is only pinned in .node-version), so not A.
- **Verifier notes:** README numbers match the record exactly (44,758 vs 1,933,859 ops/s = 43.20x; 2.73x, 1.47x, 1.27x). Shortcomings: the headline 43x comes from the baseline's per-character crypto.randomBytes(1) calls versus a buffered in-wasm ChaCha12 RNG, first-party only, stale (last commit 2024-05-11), 21 stars.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/yujiosaka/wa-ulid>
  - <https://github.com/yujiosaka/wa-ulid/commits>
  - <https://github.com/yujiosaka/wa-ulid/tree/main/src>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/README.md>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/package.json>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/.node-version>
  - <https://raw.githubusercontent.com/ulid/javascript/v2.3.0/lib/index.ts>
- **Sources the enricher read:**
  - <https://github.com/yujiosaka/wa-ulid>
  - <https://github.com/yujiosaka/wa-ulid/commits/main>
  - <https://github.com/yujiosaka/wa-ulid/issues?q=is%3Aissue>
  - <https://github.com/yujiosaka/wa-ulid/issues/1>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/README.md>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/benchmark.js>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/package.json>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/pnpm-lock.yaml>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/rollup.config.js>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/src/index.ts>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/test/index.test.ts>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/bin/cli.js>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yujiosaka/wa-ulid/HEAD/.node-version>
  - <https://registry.npmjs.org/wa-ulid>
  - <https://registry.npmjs.org/wa-ulid/-/wa-ulid-1.0.0.tgz>
  - <https://raw.githubusercontent.com/ulid/javascript/v2.3.0/lib/index.ts>
  - <https://raw.githubusercontent.com/ulid/javascript/v2.3.0/package.json>
  - <https://raw.githubusercontent.com/ulid/javascript/HEAD/package.json>
  - <https://raw.githubusercontent.com/ulid/javascript/HEAD/source/ulid.ts>
  - <https://raw.githubusercontent.com/ulid/javascript/HEAD/source/utils.ts>
  - <https://github.com/ulid/javascript/tree/master/source>
  - <https://raw.githubusercontent.com/rollup/plugins/master/packages/wasm/README.md>
  - <https://github.com/jkomyno/uniku>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/yujiosaka/wa-ulid`) · [data/wave13/enrich/raw/github_com_yujiosaka_wa_ulid.json](../../../data/wave13/enrich/raw/github_com_yujiosaka_wa_ulid.json) (enrichment confidence 0.75)

</details>
