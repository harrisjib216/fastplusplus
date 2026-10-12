# gkurt/quickjs (performance-optimised QuickJS-NG fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Personal QuickJS-NG fork with inline caches and interpreter fast paths; Octane 2022 to 2385 (+18%) against upstream quickjs-ng on CI.

| | |
|---|---|
| **Beats** | Upstream quickjs-ng master (QuickJS-NG, the maintained fork of Bellard's QuickJS) |
| **Claimed result** | PR #8 (fork 4679cbc vs upstream quickjs-ng 19dbe85, medians of 3 alternating runs): Octane 2.0 total score 2022 to 2385 (+18%; Gameboy -5%); upstream tests/microbench.js 1.18x faster (geomean); bench/runtime.js 1.57x faster with instructions down 35%; peak memory over full Octane +18% and qjs code size +12%. PR #9 (against the fork's own previous head, next ef7671b): Octane geomean 2324 to 2838 (+22.1%), DeltaBlue -2.8%. PR #12 (against next c861d16): time 19 faster, 0 slower, 20 unchanged (threshold 5%), geomean -21.2%; instructions 22 fewer, 0 more, 17 unchanged, geomean -20.9%; Octane same work in 2.4% fewer instructions. |
| **Workload** | A CI workflow builds the fork and upstream quickjs-ng in Release mode and runs Octane 2.0, upstream tests/microbench.js and bench/runtime.js (with cachegrind instruction counts), alternating sides for 3 runs each and comparing medians. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest runner (Linux/X64); CPU model not stated |
| **Compiler and flags** | make BUILD_TYPE=Release for both fork and upstream on the same toolchain (CMake Release defaults); compiler not named. |
| **Adoption** | 0 stars (personal fork of quickjs-ng, 3.9k stars upstream) |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/gkurt/quickjs) · [benchmark](https://github.com/gkurt/quickjs/pull/8) |

## Verdict

On a GitHub-hosted ubuntu-latest runner (CPU not stated, compiler not named, both sides built with make BUILD_TYPE=Release), medians of 3 alternating runs put the fork at 2385 vs 2022 Octane 2.0 geomean score against upstream quickjs-ng 19dbe85 (+18%), 1.18x faster on upstream's tests/microbench.js and 1.57x on the fork's runtime.js with 35% fewer instructions, at +18% peak memory and +12% code size. Later PRs report further gains against the fork's own earlier heads only.

## Use it when

- You already embed quickjs-ng and want more interpreter throughput on object-heavy or array-heavy scripts without a JIT (Octane total +18% vs upstream in PR #8, with more gains claimed by PRs #9 and #12 against the fork's own earlier heads).
- Scripts dominated by property access on stable object shapes, global variable traffic, numeric sort with a - b comparators, JSON.stringify/parse, or regexp scans with a literal first character.
- WASI or Rust (rquickjs) embeddings where you can take the fork's prebuilt npm or rquickjs-sys artefacts and track one maintainer's release tags (v0.17.0-gkurt.N).
- Throughput matters more than peak memory or binary size.

## Skip it when

- Memory-constrained targets: PR #8 measured peak memory over full Octane +18% (CodeLoad 60 to 84 MB, PdfJS 18 to 23 MB) and qjs code size +12% versus upstream.
- You need a maintained, reviewed engine: the fork is three weeks old (13 PRs, 2026-09-14 to 2026-09-29), has 0 stars, 0 issues, one human maintainer, and its commits are written by an AI assistant on claude/... branches; nothing has been proposed upstream.
- You exchange precompiled bytecode or snapshots with stock quickjs-ng: BC_VERSION is 35 in the fork and each side rejects the other's bytecode; @gkurt/quickjs-wasi 0.2.0 snapshots do not restore in 0.3.0.
- Your code is written against current quickjs-ng master: upstream changed JSInterruptHandler to take a JSContext \*, the fork still passes a JSRuntime \*, so it is not a drop-in for the newest upstream API.
- Workloads like Gameboy (-5%) or microbench global_write (+50% time) and array_for (+16%), which PR #8 lists as slower than upstream.

## How it is fast

Shape-keyed inline caches for property reads, writes and adds (two-way, including adds that shadow prototype properties), a 256-entry per-context cache of global variable slots that validates itself on each hit, and dictionary-mode shapes for objects with up to 1024 properties. The interpreter gains fused opcodes (OP_to_propkey_cond for obj[key] = v, OP_to_int32, compare-and-branch fusion), dense-array recovery for arrays that went slow, interrupt polling only on backward jumps and calls, and in-place string appends. Library paths add computed-goto regexp dispatch with memchr skip-ahead (REOP_skip_to_char, REOP_skip_to_range), a native numeric sort when the comparator's bytecode is exactly (a, b) =&gt; a - b or b - a, direct-to-buffer JSON.stringify, atom-keyed JSON.parse, and properties allocated inline with the object.

## Compared with alternatives

Pick it over Bellard's QuickJS or stock quickjs-ng when you want that exact engine and C API but faster, and can accept an unreviewed single-maintainer fork; PrimJS claims a similar Octane gain over QuickJS (3735 vs 2904) from a company-backed codebase, and Escargot or Hermes are better choices if you can switch engines and want a long-maintained one.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (libc and libm; optional mimalloc as upstream) |
| **Minimum toolchain** | C11 compiler, CMake 3.10+ (also Meson and a Makefile wrapper); computed-goto regexp dispatch needs GCC or Clang, not MSVC or Emscripten |
| **Platforms** | same as quickjs-ng: Linux, macOS, Windows (MSVC, including ARM64 with Visual Studio 18), WASI; 32-bit NaN-boxing builds syntax-checked per PR #9 |
| **Thread safety** | As upstream: one JSRuntime per thread, no locking; the new caches live in JSContext/JSRuntime and the fork adds no process-wide mutable state |
| **Drop-in for the baseline** | partial — source-compatible with quickjs-ng 0.17.0 plus extra APIs, but bytecode (BC_VERSION 35) is incompatible and the JSInterruptHandler signature differs from current upstream master |

## Gotchas

- Only PR #8 (fork 4679cbc vs quickjs-ng 19dbe85) measures against upstream; PRs #9 and #12 measure the fork against its own previous head, so their +22.1% Octane and -21% runtime.js figures do not multiply with PR #8's +18%. The weekly bench-upstream job keeps running (run #10 on 2026-10-05) but its summary sits behind a GitHub sign-in, so no post-PR #12 fork-vs-upstream number was readable here. The 1.57x runtime.js figure comes from the fork's own micro benchmarks, which bench/README.md says are written to exercise the paths each optimization targets; upstream's tests/microbench.js (1.18x) and Octane (+18%) are the less biased numbers.
- Harness read in full (bench-upstream.yml, bench/octane.js, bench/upstream.js, upstream tests/microbench.js): both sides use identical CMake/Makefile flags (diffed against upstream; the fork only adds a QJS_DISABLE_TYPESCRIPT option and test targets), run alternately on one runner, and the cachegrind counts run upstream's calibrated iteration counts on both. No correctness bug found; one small flaw: the Octane total is the geometric mean of each side's successful benchmarks only, so a suite that errors on one side would change the set compared (the report prints such failures, none were reported in PR #8).
- Interrupt handlers are polled only on backward jumps and function entry, so long straight-line code is checked less often than upstream.
- TypeScript type erasure is compiled in by default (QJS_DISABLE_TYPESCRIPT turns it off), part of the code-size growth.

## Known shortcomings

- PR #8 against upstream matches (Octane 2022 to 2385, about 18%) but costs peak memory +18% and code size +12%; PR #12 is really 19 faster, 0 slower and 20 unchanged of 39 (geomean -21.2% time), and PRs #9 and #12 are measured against the fork's own heads. CI on ubuntu-latest with the CPU unknown; 0-star AI-written QuickJS-NG fork.
- Enricher: the Octane total is a geomean over each side's own successful benchmarks only; the 1.57x runtime.js figure comes from the fork's own targeted microbenchmarks (the less biased numbers are 1.18x on microbench.js and +18% Octane); the API is not identical (JSInterruptHandler takes JSRuntime\* against upstream's JSContext\*, extra TypeScript and async-module APIs) and bytecode BC_VERSION 35 is incompatible.

## Caveats and trade-offs

Numbers come from PR descriptions and the fork's own CI workflow, not an independent run, and the runner CPU is unknown (shared cloud VMs). Only PR #8 compares against upstream quickjs-ng; PRs #9 and #12 measure against the fork's own earlier heads, so their gains are not additive with PR #8 against upstream without a fresh upstream run. PR #8 also reports costs: peak memory +18% over full Octane (CodeLoad 60 to 84 MB, PdfJS 18 to 23 MB), qjs code size +12%, Gameboy -5%, and regressions on microbench global_write (+50%) and array_for (+16%). The fork is days to weeks old (13 PRs, 2026-09-14 to 2026-09-29), has no stars, and its branches and commits are authored by an AI assistant (claude/... branches); bytecode version was bumped (BC_VERSION 35), so bytecode is not compatible with upstream. PR #12 states test262 shows 14 errors out of 82220, the same 14 as upstream's list, and Debug plus ASan/UBSan builds were clean. The baseline is upstream quickjs-ng, not Bellard's QuickJS. No indication the changes were proposed upstream.

Same C API and engine as QuickJS-NG. Adds inline caches, dense-array fast paths, cached global slots, computed-goto regexp execution and similar. Octane peak memory rose 18% in the PR #8 comparison (mostly CodeLoad and PdfJS); PR #9 reports +1.6% geomean peak memory; PR #12 reports memory mostly slightly lower.

## Maintenance

Active (last commit 2026-09-29, release v0.17.0-gkurt.1, weekly benchmark job still running) and MIT-licensed, but a 0-star, AI-authored personal fork three weeks old with no upstream review, so vendor it only with your own test262 and fuzzing runs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #8 reports a first-party CI comparison against upstream quickjs-ng master; the workflow (.github/workflows/bench-upstream.yml, bench/runtime.js, upstream tests/microbench.js, Octane pinned to a commit) is public, but it runs on a GitHub-hosted ubuntu-latest runner with no CPU model and no named compiler, so it falls short of A.
- **Verifier notes:** PR #8 numbers match; the record misreported PR #12 (it is 19 faster / 0 slower / 20 unchanged in time out of 39 benchmarks, geomean -21.2%; 22 is the instruction-count tally) and omitted PR #8's memory +18% and binary +12% costs, corrected above. Shortcomings: first-party CI only, CPU unknown, new 0-star AI-written fork, higher memory and code size than upstream.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gkurt/quickjs/pull/8>
  - <https://github.com/gkurt/quickjs/pull/9>
  - <https://github.com/gkurt/quickjs/pull/12>
  - <https://github.com/gkurt/quickjs>
  - <https://github.com/gkurt/quickjs/commits/next>
  - <https://github.com/gkurt/quickjs/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/.github/workflows/bench-upstream.yml>
- **Sources the enricher read:**
  - <https://github.com/gkurt/quickjs>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/README.md>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/.github/workflows/bench-upstream.yml>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/bench/README.md>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/bench/octane.js>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/bench/upstream.js>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/bench/runtime.js>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/bench/compare.js>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/bench/instructions.js>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/quickjs.c>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/quickjs.h>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gkurt/quickjs/next/Makefile>
  - <https://raw.githubusercontent.com/quickjs-ng/quickjs/master/quickjs.c>
  - <https://raw.githubusercontent.com/quickjs-ng/quickjs/master/quickjs.h>
  - <https://raw.githubusercontent.com/quickjs-ng/quickjs/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/quickjs-ng/quickjs/master/Makefile>
  - <https://raw.githubusercontent.com/quickjs-ng/quickjs/master/tests/microbench.js>
  - <https://github.com/gkurt/quickjs/pull/8>
  - <https://github.com/gkurt/quickjs/pull/9>
  - <https://github.com/gkurt/quickjs/pull/12>
  - <https://github.com/gkurt/quickjs/pull/13>
  - <https://github.com/gkurt/quickjs/pulls?q=is%3Apr>
  - <https://github.com/gkurt/quickjs/commits/next>
  - <https://github.com/gkurt/quickjs/issues>
  - <https://github.com/gkurt/quickjs/actions/workflows/bench-upstream.yml>
  - <https://github.com/gkurt/quickjs/actions/runs/37265759071>
  - <https://registry.npmjs.org/@gkurt%2Fquickjs-wasi>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/gkurt/quickjs`) · [data/wave12/enrich/raw/github_com_gkurt_quickjs.json](../../../data/wave12/enrich/raw/github_com_gkurt_quickjs.json) (enrichment confidence 0.6)

</details>
