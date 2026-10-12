# ultrachess (Rust chess library compiled to WebAssembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust (compiled to WebAssembly) with TypeScript` · `MIT` · 🟢 active

> Rust chess rules core compiled to a 158 KB WASM module with a TypeScript API, aimed at replacing chess.js; its speedup over chess.js is cited, not measured.

| | |
|---|---|
| **Beats** | chess.js (pure JavaScript chess library in V8/Node) |
| **Claimed result** | WASM startpos d6 on Node 25.7.0: 353.7 ms, 336.7 Mnps; on Bun 1.3.10: 204.9 ms, 581.0 Mnps. chess.js is listed at 5-7 Mnps (cited from upstream, Node 22), so the README claims about 55x chess.js on Node and about 95x on Bun (about 48-67x on Node and 83-116x on Bun if computed from the 5-7 Mnps range, derived from page data); native Rust is about 140x chess.js |
| **Workload** | Startpos perft depth 6 (119,060,324 nodes) through the WASM boundary via Chess.create() and chess.perft(6), plus geomean over six standard perft positions |
| **Metric** | throughput |
| **Hardware** | Apple M4 Max (arm64, macOS 26.4.1), single-threaded, min of N trials |
| **Compiler and flags** | rustc 1.95.0, cargo --release with LTO fat and codegen-units 1, no SIMD intrinsics; WASM perft via node rust/bench/wasm-perft.mjs --deep --trials 3 (Node 25.7.0, Bun 1.3.10) |
| **Adoption** | 7 stars |
| **Last commit** | 2026-04-18 |
| **Links** | [repository](https://github.com/yahorbarkouski/ultrachess) · [benchmark](https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/BENCH.md) |

## Verdict

On an Apple M4 Max, the npm build (rustc 1.95, fat LTO, codegen-units 1, wasm-opt -O4) ran startpos perft(6) inside one WASM call in 204.9 ms on Bun 1.3.10 (581 Mnps) and 353.7 ms on Node 25.7.0 (337 Mnps), 0.70x and 0.40x of its native Rust speed. chess.js was not measured: the 5-7 Mnps it is compared with is a cited figure, so the \~55-95x claim is a cross-run estimate. In the same native harness, all four perft wrappers bulk-count at depth 1, so the separate result of 836 vs 600 Mnps for cozy-chess 0.3.4 and 345 for shakmaty 0.30 (geomean 1.23x and 3.70x over six positions) is like-for-like.

## Use it when

- Bulk move-generation work in JS that can stay inside one WASM call: perft, legal-move counts, validating large position sets (startpos perft(6), 119M nodes, in 204.9 ms on Bun 1.3.10 and 353.7 ms on Node 25.7.0, Apple M4 Max).
- Server-side move validation or game-end detection for many concurrent games on Node, Bun, Deno, Cloudflare Workers or Vercel Edge, where chess.js is the CPU bottleneck and a 45 KB brotli WASM is acceptable.
- UI or search loops that call inCheck(), hash() or legal-move enumeration after every move: cached O(1) check and 64-bit Zobrist key, plus allocation-free packed moves.
- Building a JS or TS engine on the raw ABI (ultrachess/low-level) with direct linear-memory access.

## Skip it when

- Chess960 or other variants (atomic, antichess, crazyhouse, three-check): not supported; the README itself points to chessops.
- PGN tooling that must keep comments, NAGs or variations: COMPAT.md says the WASM ABI does not surface them, so Chess.loadPgn drops them when replaying the mainline, although the README advertises a NAG and comment round-trip.
- Code that creates many short-lived Chess objects without dispose() or `using`: the shipped dist has no FinalizationRegistry, so undisposed instances keep their WASM slab slots.
- Strict CSP without wasm-unsafe-eval: the README's runtime table marks both entries unsupported unless the .wasm is served from an allowed URL.
- If you need proof of a per-call speedup for move(), SAN or PGN work: only perft was measured, chess.js was never run in the same harness, and each of those calls crosses the JS/WASM boundary with string copies.

## How it is fast

Legal-only move generation with pin masks and check masks after Peter Ellis Jones's write-up (no pseudo-legal-then-filter pass), and fancy magic bitboards for sliders whose tables are searched at module init. The checkers bitboard and Zobrist key are kept incrementally, so inCheck() and hash() are O(1). perft adds two perft-only fast paths in rust/core/src/perft.rs: at depth 1 it popcounts target bitboards (count_legal_moves) instead of emitting moves, and at depth 2 and above it uses make_move_perft, which skips Zobrist, history and clock updates. The whole recursion runs inside one WASM call, and moves({raw:true}) reads a Uint32Array view over linear memory without allocating.

## Compared with alternatives

No chess library is catalogued in this category. Like berith or rsmod-pathfinder it is a Rust-to-WASM package that wins when the work stays inside one call; pick it when move-generation throughput in JS matters more than chess.js's synchronous API and variant-free scope is fine.

## Integration

| | |
|---|---|
| **Form** | module (npm package ultrachess 1.4.0, ESM and CJS, entries ultrachess, ultrachess/inline and ultrachess/low-level; the Rust crates ultrachess-core and ultrachess-wasm live in the repo and the wasm crate is publish = false) |
| **Dependencies** | none at runtime (the .wasm ships in the package); building needs cargo with the wasm32-unknown-unknown target, tsup, and optionally binaryen wasm-opt |
| **Minimum toolchain** | Rust 1.95 (workspace rust-version) to build; Node 18+, Bun 1.2+, Deno 1.40+ or an evergreen browser to run; `using` disposal needs TypeScript 5.2+ and Node 22+ |
| **Platforms** | any WebAssembly 2.0 runtime (wasm-opt run with bulk-memory, sign-ext, mutable-globals and nontrapping-float-to-int); no WASM SIMD |
| **Thread safety** | Single-threaded WASM instance with global scratch buffers ('WASM is single-threaded and ABI entry points never re-enter'); one instance per worker. |
| **Drop-in for the baseline** | partial — chess.js-style method names (move, moves, fen, pgn, history, put, remove), object-form move shim and aliases, but async construction, packed Move integers, typed exceptions instead of sentinel returns, put() returning the replaced piece and throwing on a second king, no clear() or validate_fen, and mandatory dispose() |

## Gotchas

- The headline \~55x (Node) and \~95x (Bun) over chess.js divides ultrachess's measured perft by a 5-7 Mnps chess.js figure cited without a source ('Node 22'), never run in rust/bench/wasm-perft.mjs even though chess.js ^1.4.0 is a devDependency. The two perfts also do different work: chess.js perft() generates pseudo-legal moves and makes, king-checks and unmakes every leaf (src/chess.ts), while ultrachess popcounts legal targets at depth 1 and skips Zobrist and history updates above it. The ratio is cross-run and overstates the gap for move-by-move use.
- 'Through the WASM boundary' means one boundary crossing per perft() call: the harness times only chess.perft(depth), after a warm-up and excluding Chess.create, min of 3. It measures compiled move-generation speed inside WASM, not the per-call cost of move(), moves() or SAN that a chess.js port actually exercises.
- Size figures in the README are understated: the published inline.js is 212,379 bytes (base64 of the 157,882-byte .wasm), not '\~60 KB', and the ESM TypeScript shim is 31,947 + 3,759 bytes unminified, not '\~10 KB'. The README puts magic-table init at about 1 ms while BENCH.md says embedding magics would save about 20 ms of WASM init.
- The README's '100k-game lock-step differential' is the manual pre-RC tier (just test-diff-100k, about 55 min); the default PR gate runs 200 games of up to 150 plies (test/differential/vs-chess-js.test.ts). The bench-wasm recipe also does not depend on bench-gate, although the README says every benchmark gate-runs the Rust tests (the WASM harness does check leaf counts itself).

## Known shortcomings

- The chess.js 5-7 Mnps figure is cited without source and never measured in the harness (cross-run comparison, tier D under the PostgreSQL/MySQL/ODB precedent); the perft bulk-counts at depth 1 while chess.js does not.
- The chess.js 5-7 Mnps figure behind the 55x/95x was cited, never run, although chess.js is a devDependency; chess.js perft makes and unmakes every pseudo-legal leaf while ultrachess popcounts depth 1 (make_move_perft), and the WASM harness times one perft() call so the boundary cost is not measured. README understates sizes (inline.js 212,379 bytes vs 'about 60 KB', TS shim about 36 KB vs 'about 10 KB'), loadPgn drops NAGs and comments despite a round-trip claim, undisposed handles leak (no FinalizationRegistry), and the '100k differential' is a manual pre-release tier (the PR gate runs 200 games). Like-for-like native perft against cozy-chess and shakmaty is 1.23x/3.70x geomean.

## Caveats and trade-offs

The chess.js (5-7 Mnps, 'Node 22') and chessops (2-3 Mnps) figures are cited without a source link and were never run in the project's harness, although chess.js is already a devDependency (used for differential fuzzing); the chess.js README has no perft numbers. The 55x/95x ratios are therefore cross-run comparisons on unknown hardware. BENCH.md caveat 6: ultrachess perft bulk-counts at depth 1 (popcount of target bitboards instead of materialising moves), while chess.js perft makes and unmakes every leaf move, so perft overstates the gap for real move-by-move use. Perft is a move-generation microbenchmark and says nothing about PGN/SAN parsing or full-library workloads. Single machine (Apple M4 Max), min of 3 trials. Young repo (43 commits, all in April 2026; latest 2026-04-18). [retier] The chess.js (5-7 Mnps, 'Node 22') and chessops (2-3 Mnps) figures are cited without a source and were never run in the project's harness although chess.js is a devDependency; the 55x/95x are cross-run comparisons on unknown hardware. The perfts do different work: ultrachess bulk-counts at depth 1 (popcount of target bitboards, make_move_perft) while chess.js makes, king-checks and unmakes every leaf; like-for-like native perft against cozy-chess and shakmaty (all bulk-count) is 1.23x/3.70x geomean. The WASM harness times one perft() call, so the JS boundary cost is not measured. README understates sizes (inline.js 212,379 bytes vs 'about 60 KB'; TS shim about 36 KB vs 'about 10 KB'); loadPgn drops NAGs and comments; undisposed handles leak (no FinalizationRegistry); the '100k differential' is a manual pre-release tier (the PR gate runs 200 games).

WASM path reaches only 0.40x (Node) to 0.70x (Bun) of native Rust speed; 45 KB brotli WASM plus about 10 KB TypeScript shim; async Chess.create() initialisation; no SIMD movegen because std::simd is not portable to WASM.

## Maintenance

Single-author project with 43 commits, all in April 2026 (last 2026-04-18), 7 stars, no issues filed; npm 1.4.0, MIT, well tested (perft gate, property tests, coverage gates), but young and unproven in production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The ultrachess WASM side is reproducible (rust/bench/wasm-perft.mjs, rustc 1.95.0, release LTO fat, codegen-units 1, Apple M4 Max, Node 25.7.0, Bun 1.3.10), but the chess.js baseline is a cited 5-7 Mnps figure that the repo never measures and whose upstream source is not linked (the chess.js README has no perft numbers), so the comparison is cross-run at best: C.
- **Retiered** C to D: Enricher: D stands; the chess.js figure behind the 55x/95x was cited, never run, and the two perfts do different work (bulk-count at depth 1 versus make/unmake of every leaf); caveats corrected.
- **Verifier notes:** Numbers in the record match BENCH.md and the README (Bun 204.9 ms / 581.0 Mnps, Node 353.7 ms / 336.7 Mnps, chess.js 5-7 Mnps cited, \~55x Node, \~95x Bun, \~140x native). Metadata confirmed: MIT, 7 stars, 2 forks, not a fork, npm package ultrachess 1.4.0, last commit 2026-04-18. The same BENCH.md carries same-harness native-Rust perft vs shakmaty 0.30, cozy-chess 0.3.4 and chess 3.2.0 (rust/bench/src/bin/nps.rs, geomean 3.70x shakmaty, 1.23x cozy) that would qualify as tier A for a Rust-library entry, but that is not this record's baseline; under the cross-run precedent (PostgreSQL, MySQL, ODB) the orchestrator may prefer D for the chess.js claim.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-118 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/BENCH.md>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/README.md>
  - <https://github.com/yahorbarkouski/ultrachess>
  - <https://github.com/yahorbarkouski/ultrachess/commits>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/bench/wasm-perft.mjs>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/package.json>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/justfile>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/COMPAT.md>
  - <https://raw.githubusercontent.com/jhlywa/chess.js/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/yahorbarkouski/ultrachess>
  - <https://github.com/yahorbarkouski/ultrachess/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/README.md>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/BENCH.md>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/COMPAT.md>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/TESTING.md>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/package.json>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/justfile>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/scripts/wasm-opt.mjs>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/bench/wasm-perft.mjs>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/bench/Cargo.toml>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/bench/src/lib.rs>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/bench/src/bin/nps.rs>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/core/Cargo.toml>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/core/src/perft.rs>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/wasm/Cargo.toml>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/rust/wasm/src/lib.rs>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/src/chess.ts>
  - <https://raw.githubusercontent.com/yahorbarkouski/ultrachess/HEAD/test/differential/vs-chess-js.test.ts>
  - <https://raw.githubusercontent.com/jhlywa/chess.js/HEAD/src/chess.ts>
  - <https://registry.npmjs.org/ultrachess>
  - <https://registry.npmjs.org/ultrachess/-/ultrachess-1.4.0.tgz>
  - <https://registry.npmjs.org/chess.js/latest>
  - <https://github.com/Gigantua/Gigantua>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/yahorbarkouski/ultrachess`) · [data/wave13/enrich/raw/github_com_yahorbarkouski_ultrachess.json](../../../data/wave13/enrich/raw/github_com_yahorbarkouski_ultrachess.json) (enrichment confidence 0.6)

</details>
