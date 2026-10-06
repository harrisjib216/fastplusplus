# Wave 12 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

- GNU Guile 3.0.10: drujensen/fib README has fib(47) in 102.9 s vs Lua 5.4.7 at 203.7 s (embedded-scripting shootouts search, 2026-10-06); gnu.org and git.savannah.gnu.org were blocked, so no repo page was opened.

## Retier candidates (paper found in a GitHub mirror)

- WasmNow (sillycross/wasmnow, verified B): the OOPSLA 2021 copy-and-patch paper PDF is reachable at raw.githubusercontent.com/fredrikbk/fredrikbk.github.io/master/publications/copy-and-patch.pdf (i7-7700HQ, Clang++ 10 -O3 -DNDEBUG, LLVM 10); the PochiVM verifier used it for an A. Check whether the WasmNow numbers (4.9-6.5x compile, 39-63% faster code than Liftoff) and the Liftoff build are in that paper and retier accordingly.
- Instrew (aengelke/instrew, verified C): VEE'21 paper at home.cit.tum.de/~engelke/pubs/2104-vee.pdf (blocked here) would likely raise it to B. Also TPDE (CGO 2026 paper, same host), Box64 (EuroSys 2026, ACM), aWsm (Sledge paper), WARP (Valent-Blocks, IEEE), rv32emu (VMIL'24), HHVM (OOPSLA 2014), Deegen/LuaJIT Remake (OOPSLA 2026, arXiv), Pallene (SBLP/SCP), YJIT (ACM) are paper-access retier candidates.
- cinderx (facebookincubator/cinderx, MIT, 282 stars): the Cinder JIT moved here; seed candidate if it carries its own numbers.
- lumen (lucid-softworks/lumen, Rust JS engine): 3953 on macOS v8-v7 in ahaoboy CI (QuickJS enricher, 2026-10-06); seed candidate.
- vnmakarov/ruby rtl_mjit_branch (https://github.com/vnmakarov/ruby/tree/rtl_mjit_branch): RTL instructions plus GCC/LLVM MJIT for CRuby, README claims 6.18x geomean over Ruby 2.0 with GCC, optcarrot 2.7x (Dino enricher, 2026-10-06); vnmakarov/mir is already catalogued.
