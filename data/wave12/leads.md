# Wave 12 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

- GNU Guile 3.0.10: drujensen/fib README has fib(47) in 102.9 s vs Lua 5.4.7 at 203.7 s (embedded-scripting shootouts search, 2026-10-06); gnu.org and git.savannah.gnu.org were blocked, so no repo page was opened.

## Retier candidates (paper found in a GitHub mirror)

- SETTLED 2026-10-06 (enricher opened the paper; tier stays B, caveats in retier-01). WasmNow (sillycross/wasmnow, verified B): the OOPSLA 2021 copy-and-patch paper PDF is reachable at raw.githubusercontent.com/fredrikbk/fredrikbk.github.io/master/publications/copy-and-patch.pdf and in the sillycross/sillycross.github.io repo (i7-7700HQ, Clang++ 10 -O3 -DNDEBUG, LLVM 10); the PochiVM verifier used it for an A. Check whether the WasmNow numbers (4.9-6.5x compile, 39-63% faster code than Liftoff) and the Liftoff build are in that paper and retier accordingly.
- Instrew (aengelke/instrew, verified C): VEE'21 paper at home.cit.tum.de/~engelke/pubs/2104-vee.pdf (blocked here) would likely raise it to B. Also TPDE (CGO 2026 paper, same host), Box64 (EuroSys 2026, ACM), aWsm (Sledge paper), WARP (Valent-Blocks, IEEE), rv32emu (VMIL'24), HHVM (OOPSLA 2014), Deegen/LuaJIT Remake (OOPSLA 2026, arXiv), Pallene (SBLP/SCP), YJIT (ACM) are paper-access retier candidates.
- cinderx (facebookincubator/cinderx, MIT, 282 stars): the Cinder JIT moved here; seed candidate if it carries its own numbers.
- lumen (lucid-softworks/lumen, Rust JS engine): 3953 on macOS v8-v7 in ahaoboy CI (QuickJS enricher, 2026-10-06); seed candidate.
- vnmakarov/ruby rtl_mjit_branch (https://github.com/vnmakarov/ruby/tree/rtl_mjit_branch): RTL instructions plus GCC/LLVM MJIT for CRuby, README claims 6.18x geomean over Ruby 2.0 with GCC, optcarrot 2.7x (Dino enricher, 2026-10-06); vnmakarov/mir is already catalogued.
- BEAM.com (sntran/BEAM.com): Erlang/OTP plus Elixir in one Cosmopolitan binary with docs/BENCHMARKS.md startup and fib numbers (BeamAsm enricher, 2026-10-06); seed candidate, modified runtime.
- Topaz (topazproject/topaz, kostya fork): Ruby on RPython, beats CRuby 2.7 in kostya/jit-benchmarks (Cython enricher, 2026-10-06); seed candidate.
- ThePhD/lua-bindings-shootout: multi-library Lua binding benchmark harness (the LuaBridge3 bench derives from it); a neutral re-run would settle the LuaBridge3 vs sol2 claims (LuaBridge3 enricher, 2026-10-06).
- LekKit/shadow_pgt: kernel module claiming native speed on VisionFive 2, no numbers (RVVM enricher).
- Quirrel (GaijinEntertainment/quirrel): Squirrel fork in the dasProfile table, not catalogued (Luau enricher, 2026-10-06); seed candidate.
- TinyKVM (same author as libriscv, likely github.com/varnish/tinykvm, not opened) and the Segue and ColorGuard ASPLOS 2025 SFI paper (Wasmtime/WAMR): leads from the LFI and libriscv enricher (2026-10-06).
- ncruces/wasm2go: separate project from goccy/wasm2go, wazero numbers on a Core Ultra 7 258V in go-sqlite3 discussion #361 (batch 49 verifier, 2026-10-06); seed candidate.
- FEX-Emu/FEX: x86 and x86-64 emulator for ARM64 with a JIT, not in data (Box64 enricher, 2026-10-06); seed candidate (baseline QEMU, like Box64 and rv8).
- dstogov/ir: the IR JIT framework behind the PHP 8.4+ JIT; README claims code about 5% slower than gcc -O2 compiled about 40x faster (PHP JIT enricher, 2026-10-06); seed candidate.
- TurboPython (trozen/tpy-lang): typed Python to C++ without GC, named in the Shed Skin README, benchmark claims unchecked (Shed Skin enricher, 2026-10-06); seed candidate.
- Wastrel (Andy Wingo, codeberg.org/andywingo/wastrel): Wasm-to-C compiler supporting Wasm 3.0, snippet claims CoreMark 2-5% slower than native (w2c2 enricher, 2026-10-06); codeberg blocked here; seed candidate.
- treVM (arXiv 2604.27570, repo unknown): mentioned by the wasm3 enricher (2026-10-06), unverified.
- faasm (faasm/faasm): WAVM-based serverless runtime (WAVM enricher, 2026-10-06); weak lead.
- ykjit/ykcbf (yk-enabled interpreter) and the yk-benchmarks mruby awfy suite (yklua enricher, 2026-10-06); weak leads.
- HashLink (HaxeFoundation/hashlink): Neko successor, README has no numbers (NekoVM enricher, 2026-10-06); weak lead.
- aengelke/fadec (x86 decoder), aengelke/rellume (lifter), okitec/farmdec, the EOS VM Optimized Compiler in AntelopeIO/spring (LLVM AOT) and the Biotite static binary translator (repo unknown): leads from the Instrew and EOS VM enricher (2026-10-06).
- jrsonnet (Rust jsonnet implementation, faster than sjsonnet on most cases in its docs/benchmarks.adoc; batch 60 verifier, 2026-10-06); seed candidate.
- atJIT (kavon/atJIT, autotuning JIT built on Easy::jit) and ClangJIT (Hal Finkel, arXiv 1904.08555, repo not checked): leads from the Easy::jit enricher (2026-10-06).
- revm (bluealloy/revm): 84.8 ms vs geth 235 ms in evm-bench (evmone enricher, 2026-10-06); seed candidate alongside evmone.
- radfordneal/xsum (exact FP64 summation, MIT, paper in repo as xsum-paper.pdf, timing programs vs iFastSum and OnlineExact) and radfordneal/matprod (GPL, SIMD reproducible matmul, NEWS says slower than OpenBLAS): wave 8 numerics leads from the pqR enricher (2026-10-06).
- OpenISA/riscv-sbt (RISC-V static binary translator; snippet claims MiBench slowdown 1.12x against rv8 3.16x and QEMU 7.07x) and BlindMindStudios/AngelScript-JIT-Compiler (scriptorium 1.859 s, AngelScript 2.31.0, inactive): leads from the rv8 and AngelScript enrichers (2026-10-06).
- ecraven/r7rs-benchmarks all.csv (raw reachable): gambit/gambit about 1.95x faster than Guile 3.0.11 (geomean over 53 shared benchmarks), Loko and Bigloo about 1.6x (Guile enricher, 2026-10-06); Scheme seed candidates.
- revmc (README chart is an image only) and ncruces/wasm2go (go-sqlite3 discussion #361): wasm gh-any search leads (2026-10-06).
- ml-rust/splintr (LLM BPE tokenizer on the regexr backend, claims unchecked; regexr enricher, 2026-10-06); weak lead.
- klippa-app/go-pdfium experimental/BENCHMARKS.md (wazero vs wazy on 144 PDFs; wazy enricher, 2026-10-06); seed candidate for a wazy cross-check.
- polkavm-ffi (rotkonetworks/romio): third-party C FFI for PolkaVM, 25 downloads (PolkaVM enricher, 2026-10-06); weak lead.
- qj (6/qj, Rust plus simdjson, MIT, 16 stars): README on an M5 Max claims 25-190x over jq on NDJSON with jaq and gojq columns (jaq enricher, 2026-10-06); wave 4 json seed candidate.
- rsjsonnet (eduardosm/rsjsonnet, Rust): jrsonnet's table shows it beating go-jsonnet everywhere (kube-prometheus 57.9 vs 1068.4 ms) (sjsonnet enricher, 2026-10-06); seed candidate.
- eBay/tsv-utils (D): faster than frawk per core on every TSV task per frawk's own tables (frawk enricher, 2026-10-06); wave 3 csv-tabular seed candidate.
- guamoko995/expr-cls (Go expression evaluator from typed closures): README claims 9.015 ns/op vs expr 172.0 and cel-go 267.9 on X+(6.0*Y), Ryzen 5 5600H, 3 stars, unchecked (Expr enricher, 2026-10-06).
- tamnd/bento (Go JavaScript runtime by the katsu author; katsu enricher, 2026-10-06); weak lead.
- AssemblyScript plus json-as (TypeScript-to-native peers named in Perry's benchmarks/README.md) and Turso (Rust SQLite rewrite, Go driver turso.tech/database/tursogo): leads from the Perry and musql enricher (2026-10-06), repos not opened.
- risechain/pevm (parallel EVM on revm): README claims 2x average over sequential revm on Ethereum blocks and 22x on a Gigagas Uniswap block, numbers in crates/pevm/benches/README.md (revm enricher, 2026-10-06, not read); seed candidate.
- 0xjojoex/evm.zig and cryptuon/zig-evm (claims 5-6x parallel transaction execution): Zig EVM leads from WebSearch, unverified (Guillotine enricher, 2026-10-06).
- Seed leads from the weval/jz enrichment (2026-10-06): Porffor (CanadaHonk/porffor), scriptc (vercel-labs/scriptc), TypeScriptCompiler (ASDAlexander77/TypeScriptCompiler). Life/Wago enrichment: no new leads.
- Paper-access retier candidate: mutable (mutable-org/mutable, verified C): EDBT 2023 paper on openproceedings.org blocked here; snippets show compile-time wins over HyPer only (batch 78 verifier, 2026-10-06). Topaz: consider a repo_url override to kostya/topaz, the fork that was actually measured.
- LC Scheme BBV JIT (bsaleil/lc, BSD-3, 33 stars): README has no baseline numbers, papers only (Higgs enricher, 2026-10-06); weak lead. 0xjojoex/evm.zig has numbers vs evmone-base and revm-int (seed-d, 2026-10-06); seed candidate.
- goant (robomotionio/goant): pure-Go JS engine, ahaoboy Ubuntu V8 v7 score 981 vs goja 264 (Paserati enricher, 2026-10-06); seed candidate.
- RealNeGate/Cuik (TB backend, named by MiniVM's README as its JIT base): unverified (MiniVM enricher, 2026-10-06); weak lead.
- Paper-access retier lead: mutable via the independent ADC 2023 study arXiv 2311.04692 (PostgreSQL LLVM JIT vs mutable) (mutable enricher, 2026-10-06).
- riscv-sbt repo now redirects to lmcad-unicamp/riscv-sbt (batch 88 verifier, 2026-10-06): repo_url override candidate.
- Box86 (ptitSeb/box86): not catalogued; the 2022 box86.org article gives 7z 3117 vs QEMU 691 on an x86 guest (FEX enricher, 2026-10-06); seed candidate alongside Box64.
- Static Hermes (facebook/hermes, already catalogued) and Perry (repo unknown) named in the jlucaso1/js-compiled harness, whose results live only on blocked GitHub Pages (scriptc enricher, 2026-10-06).
- angelsea (AsuMagic/angelsea, BSD-2): MIR-based JIT for AngelScript 2.37+, README claims 0-40% over the BlindMindStudios JIT in a real application and about 5x on a generic-call benchmark (AngelScript JIT enricher, 2026-10-06); seed candidate.
- LayerZero-Labs/fafo (Rust, revm-based parallel EVM, Apache-2.0/MIT, 65 stars) and the Supra AFT 2025 BTM paper (arXiv 2503.03203, up to 1.33x over pevm, snippet only, no repo found) (pevm enricher, 2026-10-06); seed candidates.
- MOSFHET (lmcad-unicamp/MOSFHET, optimised TFHE software): unverified lead from the riscv-sbt enricher (2026-10-06); crypto, outside wave 12.
- HaxeFoundation/hxcpp (beats Neko and HashLink in both gist runs, not catalogued) and the benchs.haxe.org multi-target suite (blocked here; HaxeBenchmarks/benchmark-runner commits no results) (HashLink enricher, 2026-10-06). mighty-gerbils/gerbil is weak (1.13x over Guile in all.csv).
- asumagic/asllvm (LLVM AngelScript JIT, no numbers in README; weak) and Hazelight UnrealEngine-Angelscript StaticJIT (gated fork, unreachable): angelsea enricher leads (2026-10-07).
- Pycket (pycket/pycket, Racket tracing JIT on RPython): not catalogued (hxcpp/LC enricher, 2026-10-07); seed candidate.
- QMDB (LayerZero-Labs/qmdb, Merkleized state database under FAFO; upstream README is a stub): not catalogued (FAFO enricher, 2026-10-07); wave 5 databases lead.

## Backfill round 2, 2026-10-11 (seeds w12-mine-d to g)
- CNTK vs TensorFlow: HKBU dlbench paper blocked; szilard keras_backend.md used instead. ChaiScript: every number slower than Lua (maintainer says so). V7: javascript-zoo-data Richards 4.944 vs QuickJS 746, far slower. MuJS canonical repo is https://codeberg.org/ccxvii/mujs (blocked); GitHub stub used as repo_url.
- Enricher w12 pair-010 lead: NVIDIA DALI (https://github.com/NVIDIA/DALI), GPU JPEG decode and augmentation vs CPU loaders; uncatalogued.
