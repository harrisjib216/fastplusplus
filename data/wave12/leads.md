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
