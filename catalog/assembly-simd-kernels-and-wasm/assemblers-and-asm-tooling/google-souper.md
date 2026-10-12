# Souper (LLVM IR superoptimizer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> SMT-backed superoptimizer for LLVM IR that finds peephole rewrites stock LLVM misses; its published win is code size, not speed.

| | |
|---|---|
| **Beats** | stock LLVM optimisation pipeline output (clang -O2/-O3 without Souper) |
| **Claimed result** | Snippet only (page not opened): 'A fully automated optimization pass built with Souper yields a Clang binary about 3 MB (4.4%) smaller than the one LLVM produces.' No SPEC or other execution-time speedups found in any reachable source; the README gives no numbers. |
| **Workload** | Code size of a Clang/LLVM binary compiled with an automatic Souper-based optimisation pass, against the stock LLVM-built binary, per the arXiv 1711.04422 abstract (search snippet only). This is a code-size claim, not an execution-speed claim. |
| **Metric** | other |
| **Adoption** | 2.4k stars, 188 forks; suggested optimisations were hand-implemented in LLVM and MSVC per the paper abstract; repo archived 2025-10-30 |
| **Last commit** | 2024-08-28 |
| **Links** | [repository](https://github.com/google/souper) · [benchmark](https://arxiv.org/abs/1711.04422) |

## Verdict

The only figure is from arXiv 1711.04422, seen through search snippets because arxiv.org and its mirrors are unreachable here: an automatic Souper pass produced a Clang 3.9 binary about 3 MB (4.4%, 64.3 versus 67.2 MB) smaller than the stock LLVM build. The same paper reportedly found that binary about 2% slower when compiling C++. No hardware, flags or SPEC runtime results were read, and the SPEC CPU 2017 figure in later work (2.32x) measures Souper's own speed after dataflow pruning, not faster output code.

## Use it when

- Compiler engineers hunting missed InstCombine-style rewrites in LLVM: harvest real code, let Souper propose shorter integer expressions, then implement the good ones by hand in LLVM.
- Comparing LLVM's dataflow facts (known bits, demanded bits) against solver-derived ones; sclang exposes the harvesting switches.
- Research on superoptimisation, where Souper is the reference baseline (Minotaur and the dataflow-pruning work build on it).
- Experimental code-size reduction of a build already tied to LLVM 18 when a strong test suite can catch miscompiles.

## Skip it when

- Production builds aimed at runtime speed: the only published headline number is binary size, and the same paper reports (per search snippet) that the Souper-built Clang is about 2% slower.
- Any toolchain other than its pinned patched LLVM (regehr/llvm-project branch disable-peepholes-llvmorg-18.1.6): GCC, MSVC and newer LLVM releases are unsupported and the repository was archived on 2025-10-30.
- Floating-point or SIMD-heavy code: candidate harvesting skips every instruction whose type is not an integer (lib/Extractor/Candidates.cpp), so vector and FP code is untouched; Minotaur targets that gap.
- Large builds without a Redis cache: each candidate costs SMT queries, and sclang sets a 15-second solver timeout per query.
- Code where a UB-related miscompile is unacceptable: issue #311 (select turned into logic that introduces UB) has been open since 2018.

## How it is fast

It does not speed up code by itself; it finds missing peephole optimisations. Candidate expressions (plus path conditions and LLVM's known-bits and demanded-bits facts) are translated to SMT queries, and a synthesiser (enumerative synthesis or CEGIS, with optional Alive2 verification) searches for a shorter refinement; the pass then rewrites the IR and cleans up with DCE. Results are cached in RAM or Redis so repeated expressions skip the solver.

## Compared with alternatives

Pick Souper over Minotaur when the target is scalar integer LLVM IR peepholes and you want the mature harvesting, caching and sclang build integration; Minotaur is its successor for SIMD/vector code and is the one with published runtime speedups. STOKE works on x86-64 assembly and K2 on BPF, so choose those for their respective targets.

## Integration

| | |
|---|---|
| **Form** | LLVM pass plugin (libsouperPass.so) plus standalone tools (souper, sclang/sclang++ wrappers) built from source |
| **Dependencies** | patched LLVM/Clang 18.1.6 fork (regehr/llvm-project, branch disable-peepholes-llvmorg-18.1.6), KLEE fork (klee-for-souper-17-2), Alive2 fork (manasij7479, tag v7), Z3 4.13.0, hiredis (plus a Redis server for the external cache), zstd; build_deps.sh fetches and builds all of them |
| **Minimum toolchain** | C++20 (CMakeLists adds -std=c++20), CMake and Ninja; the README's GCC 4.9+ note predates that and is stale |
| **Platforms** | Linux and macOS hosts per the README; it rewrites target-independent LLVM IR, so output targets are whatever the bundled Clang supports |
| **Thread safety** | not documented; Pass.cpp keeps the solver in a file-level global (std::unique_ptr&lt;Solver&gt; S), so it is built for one compile per process, which is how sclang uses it |
| **Drop-in for the baseline** | partial — sclang/sclang++ replace CC/CXX in a configure/make build, but only as wrappers around Souper's own patched Clang 18, and they need Z3 and (by default) a running Redis |

## Gotchas

- Known wrong-code and crash bugs were never fixed before archiving: #311 (Souper treats a select whose untaken arm has an undefined shift as a no-op, printing -128 where Clang and GCC print 0; Regehr called it likely a showstopper), #562 (a missing break in Pass.cpp getValue falls through to an out-of-bounds operand access), #166 (blockpc is unsound; blockpc exploitation is opt-in via SOUPER_EXPLOIT_BLOCKPCS). sclang ships a SOUPER_SKIP_FILES list 'for example because they trigger known bugs' and enables -souper-double-check by default.
- Solver failures other than timeouts are printed as '[FIXME: Crash commented out] Unable to query solver' and skipped; the comment says this works around a protocol error seen once in SPEC 2017, so failed queries silently lose optimisations.
- The Redis cache is unversioned: the README says to stop Redis and delete its dump file after every Souper upgrade, otherwise stale results from an older build can be reused.
- The README's usage lines use the legacy pass manager ('-Xclang -load', 'opt -load ... -souper'); the current pass is a new-pass-manager plugin, and sclang passes both -Xclang -load and -fpass-plugin.

## Known shortcomings

- The only number is a code-size result (Clang binary 4.4% smaller) from an arXiv abstract snippet; no speed claim; archived 2025-10-30.
- Enricher: the only number is still code size (Clang binary 64.3 vs 67.2 MB, 4.4%, arXiv 1711.04422, snippet only), and the same paper reports the Souper-built Clang about 2% slower; the SPEC CPU 2017 2.32x is Souper's own tool speed after dataflow pruning, not output code. Open wrong-code bugs #311 (UB select), #562 and #166 were left at archive; the pass swallows solver errors; it harvests integer types only. Lead: a TU Delft bachelor thesis 'Evaluating Souper' (fork ebdemir/souper) reproduces the paper (repository.tudelft.nl blocked).

## Caveats and trade-offs

arxiv.org, ar5iv and web mirrors fail to resolve here (getaddrinfo ENOTFOUND), so the abstract claim is snippet only and the paper's evaluation (any SPEC CPU speedups or LLVM versions and flags) was not read; the lead's 'speedups on SPEC' could not be confirmed and the abstract snippet mentions no SPEC speedups. The one number is binary size, which does not fit the project's 'faster' qualification; kept as a tooling entry. Repo README and RESULTS file list bug reports and LLVM commits attributed to Souper, with no performance data. The paper is first-party (arXiv, not confirmed peer reviewed). Successor work Minotaur (already on the known list) reports speedups against Souper. Archived 2025-10-30, last commit 2024-08-28 ('StringRef::startswith was deprecated, use starts_with'). [retier] Enricher: the paper's only output metric is code size (4.4% smaller Clang binary) and it reports the Souper-built Clang about 2% slower; the SPEC 2.32x is Souper's own analysis speed; open wrong-code bugs #311, #562 and #166 remain at archive.

Needs an SMT solver (Z3 via -z3-path) and builds its own LLVM/Clang through build_deps.sh (last bump to LLVM 18 in May 2024); runs as an LLVM opt pass or the sclang/sclang++ drop-in compilers and adds compile time (the README says Redis query caching 'often gives a substantial speedup for large compilations'); targets LLVM IR peephole expressions; archived, so no further LLVM tracking.

## Maintenance

Archived by Google on 2025-10-30 (last commit 2024-08-28) and pinned to a patched LLVM 18.1.6, with several wrong-code, crash and unsoundness issues left open (#311, #562, #166, #631); Apache-2.0 and usable as a research and LLVM-development tool, not as a production optimiser.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only number is the arXiv 1711.04422 abstract's code-size result (Clang binary about 3 MB, 4.4%, smaller than the stock LLVM build), seen only in search snippets because arxiv.org, ar5iv and research.google are unreachable here; it is first-party, from a preprint not confirmed as peer reviewed, with no methodology read, so tier C at most. No execution-speed numbers were found in the README, the repo page or any snippet.
- **Verifier notes:** Record checked: archived 2025-10-30, last commit 2024-08-28 ('StringRef::startswith was deprecated, use starts_with'), Apache-2.0, 2.4k stars, 188 forks; the README links the arXiv paper but gives no performance data. The claim is binary size, not speed, so the entry does not meet the catalog's 'faster' bar; keep it as a tooling entry with that shortcoming recorded (arXiv 1711.04422 snippet only; any SPEC or runtime results in the paper unread). Successor Minotaur is already listed.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-122 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/google/souper>
  - <https://github.com/google/souper/commits>
- **Sources the enricher read:**
  - <https://github.com/google/souper>
  - <https://raw.githubusercontent.com/google/souper/HEAD/README.md>
  - <https://raw.githubusercontent.com/google/souper/HEAD/RESULTS>
  - <https://raw.githubusercontent.com/google/souper/HEAD/build_deps.sh>
  - <https://raw.githubusercontent.com/google/souper/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/google/souper/HEAD/lib/Pass/Pass.cpp>
  - <https://raw.githubusercontent.com/google/souper/HEAD/utils/sclang.in>
  - https://raw.githubusercontent.com/google/souper/HEAD/tools/CMakeLists.txt (404)
  - <https://raw.githubusercontent.com/google/souper/HEAD/include/souper/Inst/Inst.h>
  - <https://raw.githubusercontent.com/google/souper/HEAD/lib/Extractor/Candidates.cpp>
  - <https://github.com/google/souper/issues?q=is%3Aissue+miscompile+OR+unsound+OR+wrong+OR+incorrect>
  - <https://github.com/google/souper/issues?q=is%3Aissue+is%3Aopen+miscompile+OR+unsound+OR+incorrect>
  - <https://github.com/google/souper/issues/311>
  - <https://github.com/google/souper/issues/562>
  - <https://github.com/ebdemir/souper>
  - https://web3.arxiv.org/abs/1711.04422v2 (EGRESS: ENOTFOUND)
  - https://repository.tudelft.nl/file/File_e075faad-d676-4f64-9b5e-4655e54ee4b8 (EGRESS: ENOTFOUND)
  - WebSearch: "Souper: A Synthesizing Superoptimizer" SPEC CPU speedup evaluation Clang binary 4.4% smaller
  - WebSearch: souper synthesizing superoptimizer pdf site:github.com
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/google/souper`) · [data/wave13/enrich/raw/github_com_google_souper.json](../../../data/wave13/enrich/raw/github_com_google_souper.json) (enrichment confidence 0.6)

</details>
