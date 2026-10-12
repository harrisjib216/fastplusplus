# rsmod-pathfinder

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (wasm-pack), with AssemblyScript and TypeScript variants benchmarked` · `ISC` · 🔴 abandoned

> Rust/wasm port of rsmod's BFS tile pathfinder; about 5.5x faster per path than its earlier TypeScript build on Node.

| | |
|---|---|
| **Beats** | TypeScript implementation of the same rsmod pathfinder on Node.js (the package's own 4.2.5 TypeScript release, commit 1114386, built with tsc); also the package's 5.0.x AssemblyScript WebAssembly release (commit 8ff4033) |
| **Claimed result** | Per call, 100k paths on the Lumbridge map square: Rust native about 2.8 us (278-281 ms per 100k); Rust WebAssembly on Node about 7.0 us (699-705 ms); AssemblyScript WebAssembly about 15.3 us (1519-1544 ms); TypeScript about 38.5 us (3820-3858 ms). So Rust wasm is about 5.5x and AssemblyScript wasm about 2.5x faster than TypeScript (derived from page data). Separately, cargo bench pathfinder/find_path (native Rust, criterion) reports 7.19 us, 2.6x slower than the native main.rs loop. README adds that the wasm build takes about 850 ms per 100k in a real server, without data. |
| **Workload** | 100k pathfinding requests on a reconstruction of the Lumbridge map square (64x64 tiles, full clipping flags), destination 10 tiles north with a single access point. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 3900X 12-Core Processor 3.80 GHz |
| **Compiler and flags** | Rust: [profile.release] lto = true, opt-level = 3; wasm-pack release wasm-opt flags in Cargo.toml (--generate-global-effects --optimize-instructions --memory-packing --intrinsic-lowering --flexible-inline-max-function-size 4294967295 --inlining --inlining-optimizing -O4); wasm-pack build --target nodejs; native run in release on Windows x64. AssemblyScript 5.0.x: asc ^0.27.27 release target optimizeLevel 3, shrinkLevel 0, converge, noAssert, runtime minimal (asconfig.json at commit 8ff4033). TypeScript 4.2.5: tsc ^5.3.3, target esnext (tsconfig.json at commit 1114386). Rust, Node and V8 versions not stated. |
| **Adoption** | 1 star, 5 forks; crates.io rsmod-pathfinder 2,620 total downloads (19 recent); npm @2004scape/rsmod-pathfinder downloads not re-checked (npm API blocked here) |
| **Last commit** | 2024-10-26 |
| **Links** | [repository](https://github.com/2004scape/rsmod-pathfinder) · [benchmark](https://github.com/2004scape/rsmod-pathfinder) |

## Verdict

On one AMD Ryzen 9 3900X under Windows, 100k pathfinding calls on the Lumbridge map square (10-tile route north, rsmod BFS) took about 279 ms in native Rust (2.8 us per call), about 702 ms for the Rust wasm build on Node (7.0 us), about 1,530 ms for the earlier AssemblyScript 5.0.x wasm release (15.3 us) and about 3,840 ms for the earlier TypeScript 4.2.5 release (38.5 us), so Rust wasm was about 5.5x faster than TypeScript (derived from page data). The Rust drivers (src/main.rs, src/main.js) are in the repo; the AssemblyScript and TypeScript drivers are not, and Node and V8 versions are not given.

## Use it when

- A Node or Rust server for a 2004-era RuneScape-style game (tile grid with wall and loc collision flags) where per-tick NPC and player pathfinding is hot.
- You need rsmod pathfinding semantics exactly (BFS, closest-approach fallback within 10 tiles, waypoint cap such as 25) from JavaScript without running the Kotlin original on the JVM.
- Many short routes per tick on one thread: about 2.8 us per 10-tile route natively and about 7 us through wasm on Node on a Ryzen 9 3900X (first-party).
- You want a small ISC-licensed pathfinder to vendor and adapt; the Rust source is a direct, readable port of the Kotlin code.

## Skip it when

- General graph, navmesh or weighted-cost pathfinding: this is an unweighted BFS confined to a 128x128 window, with no A\* heuristic.
- Several worlds per process or calls from multiple workers sharing one instance: the wasm API keeps a single global collision map and PathFinder in static mut state.
- Memory-tight hosts: the collision table reserves 16,777,216 pointer slots (64 MB of wasm32 linear memory, 128 MB of zeroed virtual memory natively) before any zone is allocated, and wasm memory never shrinks.
- You need a maintained dependency: the repository was archived on 2026-02-17 (last commit 2024-10-26) and its issue tracker has no issues at all.
- You relied on the 4.x TypeScript input checks: that version threw on coordinates outside 0..0x7fff or levels outside 0..3, while the Rust port masks coordinates with bit operations and never errors.

## How it is fast

Unweighted 8-direction BFS over a 128x128 window centred on the source, using flat arrays (i8 direction grid, i32 distance grid) and a 4096-entry ring-buffer queue, with collision tested as bit-mask ANDs against per-direction BLOCK_\* masks. The Rust port reads flags through unchecked raw-pointer indexing into a zone table of 16,777,216 Option&lt;Box&lt;[u32; 64]&gt;&gt; slots, built with LTO, opt-level 3 and wasm-opt -O4 for the wasm package. Part of the gain over TypeScript is data layout rather than language: the 4.2.5 TypeScript version used an Int32Array direction grid and a 2,457,600-slot holey JS Array of Int32Array|null read with optional chaining for every flag lookup.

## Compared with alternatives

Pick it when you need a RuneScape-style tile pathfinder in Node or Rust; unlike general wasm-versus-JS demos such as wasm-and-ffi-performance-comparison-in-node or tinymt-wasm-typescript-benchmark, it times Rust wasm, AssemblyScript and TypeScript ports of the same real library, though at different code versions.

## Integration

| | |
|---|---|
| **Form** | crate (rsmod-pathfinder 5.0.4, lib name rsmod) and npm module (@2004scape/rsmod-pathfinder 5.0.4, wasm-pack --target nodejs) |
| **Dependencies** | wasm-bindgen 0.2.95, once_cell, serde, serde_json, rand, getrandom (js feature); criterion 0.5.1 for benches |
| **Minimum toolchain** | Rust 2021 edition (no rust-version declared); wasm-pack with wasm-opt for the npm build; Node for the published package |
| **Platforms** | any Rust target natively; the npm package is a wasm32 build for Node (CommonJS, --target nodejs), no browser or bundler build is published |
| **Thread safety** | Native PathFinder::find_path takes &mut self, so use one PathFinder per thread; a CollisionFlagMap can be shared read-only. The wasm exports mutate global static mut state and are not reentrant. |
| **Drop-in for the baseline** | partial — same algorithm and argument order as the 4.x TypeScript findPath, but 5.x returns a Uint32Array of packed coordinates instead of a Route, and the collision map lives inside wasm (updated through __set and change\* calls) instead of a JS CollisionFlagMap object |

## Gotchas

- Harness flaw in cargo bench: benches/pathfinder.rs uses iter_batched with BatchSize::SmallInput, cloning a roughly 112 KB PathFinder (16 KB i8 directions, 64 KB distances, two 16 KB ring buffers) per iteration in setup and consuming it inside the timed routine, so each timed call runs on a cold copy and also pays its four frees. That explains why criterion reports 7.19 us while the src/main.rs loop, which reuses one warm PathFinder, reports 2.8 us; quote the main.rs figure for steady-state server use.
- Baseline mismatch: the TypeScript row (4.2.5, January 2024) and the AssemblyScript row (5.0.x, May 2024) ran earlier code with no driver anywhere in the repo, and Node/V8 versions are not stated. Besides the language change, the Rust port shrank the direction grid from 32-bit to 8-bit entries (each call clears 80 KB instead of 128 KB) and dropped the TS holey-Array zone table, so the 5.5x mixes runtime and data-layout gains.
- Every find_path call clears the full 128x128 direction and distance grids regardless of route length, so very short routes pay a fixed reset cost that a generation-counter scheme would avoid.
- lumbridge.json holds 4096 rows of 64 values with exactly one non-zero flag per row (2,338 flagged tiles) at the position the harness reads, so the map reconstruction is consistent. The source tile (3232,3205) has ROOF, WALL_NORTH and WALL_NORTH_PROJ_BLOCKER and the tile north of it holds a LOC, so the benchmark route has to detour rather than walk straight north.

## Known shortcomings

- The TypeScript and AssemblyScript baselines are earlier package releases (4.2.5 TS, 5.0.x AS) with no driver at HEAD; Node version unstated. Archived 2026-02-17.
- Enricher: benches/pathfinder.rs uses iter_batched with SmallInput, cloning a roughly 112 KB PathFinder per iteration and dropping it inside the timed routine, so each call runs cache-cold (criterion 7.19 us vs 2.8 us in the main.rs loop that reuses one warm PathFinder); the TypeScript baseline (4.2.5, January 2024) used Int32Array directions (128 KB reset per call vs 80 KB) and a 2,457,600-slot holey JS Array zone table, so the 5.5x mixes language and data-layout gains; the AssemblyScript row (5.0.x, May 2024) ran earlier code with no driver in the repo and unstated Node versions; each call resets the full 128x128 grids; the collision table reserves 64 MB of wasm32 memory; the wasm API uses global static mut state; archived 2026-02-17.

## Caveats and trade-offs

Repository archived by the owner on 2026-02-17 (read-only); last commit 2024-10-26. The Rust drivers are in the repo (src/main.rs native, src/main.js loads dist/ from wasm-pack, timed with Date.now() over 100k calls), but the TypeScript and AssemblyScript rows have no driver at HEAD: they appear to measure the package's earlier 4.2.5 TypeScript and 5.0.x AssemblyScript releases (in git history), so the three implementations are different code versions and the TS/AS rows cannot be reproduced from HEAD. Node version not given. Synthetic single-map, single-route workload (destination 10 tiles north). The criterion bench (7.19 us native) disagrees with the native main.rs loop (2.8 us) without explanation; its iter_batched routine clones a PathFinder per iteration and drops it inside the timed region. The \~850 ms 'real world' figure is unexplained. First-party numbers.

Single-purpose pathfinder for a RuneScape-style tile map; the README also mentions a 'real world' \~850 ms figure for the wasm build on a TypeScript server.

## Maintenance

Archived on 2026-02-17 with the last commit on 2024-10-26 (crate 5.0.4, 2,620 total downloads), but ISC-licensed, small and dependency-light enough to vendor if you need rsmod pathfinding semantics.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README numbers match exactly and the Rust drivers are public (src/main.rs native, src/main.js for the wasm build, benches/pathfinder.rs) with CPU (Ryzen 9 3900X) and release flags in Cargo.toml, but the TypeScript and AssemblyScript rows have no driver in the repo and come from earlier package versions, and Node/V8 versions are not stated, so the JS baseline is not reproducible: tier C.
- **Verifier notes:** Record accurate on numbers, CPU, ISC licence and archived status; its caveat that main.js/main.rs are missing was wrong (both are in src/). Shortcomings to record: TypeScript and AssemblyScript baselines are earlier package releases with no driver at HEAD; Node version unstated; single synthetic route; archived 2026-02-17.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/2004scape/rsmod-pathfinder>
  - <https://github.com/2004scape/rsmod-pathfinder/commits>
  - <https://github.com/2004scape/rsmod-pathfinder/commits/main>
  - <https://github.com/2004scape/rsmod-pathfinder/tree/main/src>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/README.md>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/main/Cargo.toml>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/main/package.json>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/main/LICENSE.md>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/main/src/main.js>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/main/src/main.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/main/benches/pathfinder.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/1114386/package.json>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/1114386/tsconfig.json>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/8ff4033/package.json>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/8ff4033/asconfig.json>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/8ff4033/README.md>
  - <https://crates.io/api/v1/crates/rsmod-pathfinder>
- **Sources the enricher read:**
  - <https://github.com/2004scape/rsmod-pathfinder>
  - <https://github.com/2004scape/rsmod-pathfinder/tree/main/src/rsmod>
  - <https://github.com/2004scape/rsmod-pathfinder/commits/main>
  - <https://github.com/2004scape/rsmod-pathfinder/issues?q=is%3Aissue>
  - <https://github.com/2004scape/rsmod-pathfinder/pull/1>
  - <https://github.com/2004scape/rsmod-pathfinder/pull/3>
  - <https://github.com/2004scape/rsmod-pathfinder/tree/1114386/src>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/README.md>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/package.json>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/main.js>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/benches/pathfinder.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/rsmod.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/rsmod/pathfinder.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/rsmod/collision/collision.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/rsmod/collision/collision_strategy.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/src/rsmod/flag/collision_flag.rs>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/HEAD/lumbridge.json>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/1114386/README.md>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/1114386/src/index.ts>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/1114386/src/rsmod/PathFinder.ts>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/1114386/src/rsmod/collision/CollisionFlagMap.ts>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/8ff4033/README.md>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/8ff4033/src/rsmod/PathFinder.ts>
  - <https://raw.githubusercontent.com/2004scape/rsmod-pathfinder/8ff4033/src/rsmod/collision/CollisionFlagMap.ts>
  - <https://crates.io/api/v1/crates/rsmod-pathfinder>
  - <https://registry.npmjs.org/@2004scape%2frsmod-pathfinder>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/2004scape/rsmod-pathfinder`) · [data/wave13/enrich/raw/github_com_2004scape_rsmod_pathfinder.json](../../../data/wave13/enrich/raw/github_com_2004scape_rsmod_pathfinder.json) (enrichment confidence 0.78)

</details>
