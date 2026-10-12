# Web49 (miniwasm interpreter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Small C WebAssembly interpreter (miniwasm) plus wat/wasm tools; first-party charts show it 1.06-2.6x faster than wasm3 in 2023.

| | |
|---|---|
| **Beats** | wasm3 (the fastest WebAssembly interpreter incumbent; wasmtime, wasmer, WAMR and V8 are not in the published charts) |
| **Claimed result** | Bar charts only, no numeric table. Values read off the chart images by eye (approximate): fib_i32 40 about 3.0 s (wasm3) vs 1.17 s (miniwasm), roughly 2.6x (derived from page data); binary-trees 16 about 3.0 s vs 1.95 s (1.5x); fannkuch-redux 10 about 1.63 s vs 1.15 s (1.4x); nbody about 1.95 s vs 1.57 s (1.25x); mandelbrot 2000 about 1.46 s vs 1.30 s (1.1x); mandelbrot-simd about 1.06 s vs 0.91 s (1.2x); coremark 3000 about 3.4 s vs 3.2 s (1.06x). Trap test is slower: about 0.0055 s (wasm3) vs 0.027 s (miniwasm), roughly 5x worse. |
| **Workload** | Wall-clock time of C benchmarks compiled with emcc -O2 and run once each by wasm3 and by miniwasm: binary-trees 16, coremark 3000, fannkuch-redux 10, fib_i32 40, mandelbrot 2000 (plain and SIMD), nbody 2000000, and a trap-execution test. |
| **Metric** | throughput |
| **Hardware** | 2020 MacBook Air (Apple M1, 8 GiB RAM) |
| **Compiler and flags** | Benchmark wasm modules built with emcc -O2 (bench.py default; no extra emcc flags). README build line is 'make CC=gcc' ('gcc is fastest in my tests'); at the chart commit 70dd3e6 (2023-01-09) the makefile default was OPT ?= -O2 for compile and link. The wasm3 version and build flags, and the gcc/clang version, are not stated. The CI workflow (.github/workflows/all.yml) uses OPT='-O3 -flto -fomit-frame-pointer' and wasm3 built from source with cmake on ubuntu-latest, but the README charts are from the M1 laptop, not CI. |
| **Adoption** | 331 stars |
| **Last commit** | 2025-11-06 |
| **Links** | [repository](https://github.com/FastVM/Web49) · [benchmark](https://github.com/FastVM/Web49#benchmarks) |

## Verdict

On a 2020 MacBook Air (M1, 8 GiB), single wall-clock runs of emcc -O2 C benchmarks put miniwasm ahead of wasm3 (wasm3 version and build unstated) by about 2.6x on fib(40), 1.5x on binary-trees 16, 1.4x on fannkuch-redux 10, 1.25x on nbody and 1.06-1.2x on mandelbrot and coremark. A trap was about 5x slower. All figures are read by eye from first-party PNG charts made at commit 70dd3e6 (January 2023), with no output or exit-code checks.

## Use it when

- Running trusted, compute-bound wasm32 modules (recursion, integer and float loops such as fib, fannkuch, binary-trees) where a small C interpreter with no JIT is required and the 2023 numbers against wasm3 are enough evidence.
- Projects that want a wasm interpreter and a wat2wasm/wasm2wat toolchain in one small MIT-licensed C codebase that builds with a plain makefile and gcc, clang or tcc.
- Experiments or teaching on interpreter design (lazy stack-to-register translation, superinstructions, threaded dispatch), where readable C source matters more than spec conformance.
- Shrinking LLVM-emitted .wasm files with wasm2wasm, which re-encodes over-long LEB128 numbers (0-4 bytes saved per 32-bit number, per the README).

## Skip it when

- Untrusted or sandboxed code: at HEAD the bounds check computes addr + size in 32-bit arithmetic, so accesses within 7 bytes of 4 GiB pass the check and touch host memory past the linear-memory buffer; random_get writes through &memory[ptr] with no check at all, and base + offset effective addresses wrap instead of trapping in both versions checked (70dd3e6 and HEAD).
- Anything that needs a conformant engine: the committed results.txt passes 39 of the 147 spec .wast files (39 of 90 non-SIMD, 0 of 57 SIMD), well below the README's '\~75%'; issue #4 (jedisct1, open since 2023-01-09) reports libsodium's scalarmult crashing and xchacha20 giving wrong results.
- Programs that write to stdout: the current WASI fd_write ignores the fd and prints every iovec to stderr with an extra newline (the 2023 version wrote correctly); only a handful of WASI calls are implemented.
- Workloads that trap often or run many short-lived modules where trap cost matters: the trap chart is about 5x slower than wasm3 (about 0.027 s vs 0.0055 s). At HEAD every trap is a __builtin_trap() process crash, not a recoverable error.
- Production or long-term use: development stopped in May 2023 apart from one build-system refactor commit (2025-11-06); there is one release (v0.0.1), the API is unversioned and 8 issues are open.

## How it is fast

Each function is translated lazily, on first call, from stack bytecode into a register-style threaded code: operands are local-slot indices or inline constants, so most pushes and pops disappear. Before that, an expression-tree pass (src/opt/tree.c) and a tee-to-set pass (src/opt/tee.c) rebuild operand trees, and compares that feed a branch are fused into compare-and-branch instructions (IF_I32_EQ, IF_I32_LT_S and so on). At the benchmarked commit, dispatch was computed-goto direct threading (goto \*head++-&gt;opcode). The record's claim that it uses basic-block versioning from MiniVM does not show up in the interpreter source.

## Compared with alternatives

Choose wasm3 (the incumbent) or WAMR's fast interpreter whenever you need spec conformance, sandboxing or an embedding API. UWVM2 has much broader evidence of beating wasm3 (geomean 0.5957 over 383 modules). Web49 only makes sense for trusted modules where you want a very small C interpreter and wat/wasm tooling in one codebase and can live with its gaps.

## Integration

| | |
|---|---|
| **Form** | source-drop (makefile builds the miniwasm, wat2wasm, wasm2wat, wasm2wasm and wat2wat binaries; no installed library or package) |
| **Dependencies** | none beyond libc and libm (getentropy for WASI random_get); bench.py needs Python 3 with matplotlib, emcc and the engines it compares |
| **Minimum toolchain** | GNU C extensions (statement expressions, __builtin_trap, and computed goto when WEB49_USE_SWITCH is 0); gcc, clang or tcc per the README; MSVC needs the NEXT/LABEL macros rewritten; compiler versions not documented |
| **Platforms** | Portable C; CI built Linux, macOS and Windows (gcc) release binaries in 2023; the published benchmarks ran on Apple M1 (aarch64) |
| **Thread safety** | not documented; the interpreter passes a web49_interp_t by value and keeps a function-static dispatch table, and no threads proposal or shared memory is supported |
| **Drop-in for the baseline** | partial: as a command it runs the same WASI .wasm files as the wasm3 CLI (for the WASI calls it implements), but the embedding API differs from wasm3's |

## Gotchas

- Harness flaws: bench.py times one run per test (ten for trap) with time.time() around subprocess.call, ignores both engines' exit codes and sends stdout to DEVNULL, so a crashed or wrong run would still be charted. The 'mandelbrot-simd' test uses GCC vector extensions, but bench.py passed no -msimd128 to emcc at the chart commit, so neither engine executed wasm SIMD. 'fib_i32' computes with uint64_t (i64 ops), which is why its chart matches fib_i64.
- The charts (commit 70dd3e6, 2023-01-09) are not reproducible from HEAD: the 2025 makefile typo 'CLAGS_opt = -O3' means the README's 'make CC=gcc' builds miniwasm without any -O flag (link-only -flto); src/config.h now defaults to WEB49_USE_SWITCH 1 (switch dispatch rather than the benchmarked computed goto); and bench.py now also runs wasmer and wasmtime and leaves coremark out.
- Memory-safety bugs at HEAD (src/interp/interp.h web49_interp_addr, src/wasi/wasi.c random_get) let a module read or write host memory near linear-memory base + 4 GiB. At 70dd3e6 the size check was done in 64-bit arithmetic, but the uint32 effective-address wrap was already there.
- Unpublished charts in res/ (nop, fib_f32, fib_f64, fib_i64) are also favorable: fib_f32/fib_f64 about 4.85 s vs 1.85 s, fib_i64 about 3.1 s vs 1.2 s, nop about 5 ms vs 1.6 ms (read by eye). So the README selection is not cherry-picked against miniwasm, but none of these were rerun on current code.

## Known shortcomings

- Numbers come from res/\*.png bar charts at commit 70dd3e6 (2023-01-09): wasm3 build unstated, runs=1, code reworked since. Spec tests pass about 75%. HEAD makefile typo 'CLAGS_opt' means the default build gets no -O flag. Trap test about 5x slower than wasm3. No comparison with Wasmtime, wasmer, WAMR or V8.
- Enricher (chart commit 70dd3e6 and HEAD): bench.py ignores exit codes, sends stdout to DEVNULL and runs once; 'mandelbrot-simd' was built without -msimd128 so no Wasm SIMD ran; fib_i32.c computes in uint64_t. HEAD bugs: the bounds check addr + size wraps in uint32 so host memory near base + 4 GiB is reachable, random_get writes with no check, base+offset effective addresses wrap, WASI fd_write sends all output to stderr with an extra newline, config.h defaults to switch dispatch, and the makefile typo CLAGS_opt builds without -O. results.txt passes 39 of 147 spec files (0 of 57 SIMD) against the README's about 75%. Issue #4 open: libsodium crashes or gives wrong results. Unpublished res/ charts (nop, fib_f32/f64/i64) also favour miniwasm, so no cherry-picking. Dormant since May 2023 apart from one 2025 build refactor.

## Caveats and trade-offs

Numbers exist only as PNG bar charts (my visual readings, not page text), each benchmark was run once by default (bench.py runs=1; wall-clock time.time() around a subprocess, so process start and module load are included), on one M1 laptop with no noise control. Margins on coremark (about 1.06x) and mandelbrot (about 1.1x) are within laptop run-to-run noise; only fib_i32, binary-trees and fannkuch-redux show clear gaps. Executing a trap is about 5x slower than wasm3. The charts date from commit 70dd3e6 (2023-01-09); the interpreter was reworked afterwards (new block system, f64 ops, simde, through May 2023), so they do not describe current code. Current HEAD cannot reproduce them as-is: bench.py now always appends wasmer and wasmtime and has coremark commented out, and the makefile has a typo ('CLAGS_opt = -O3' instead of CFLAGS_opt), so the default build compiles miniwasm without any -O flag. README says the wasm spec test suite is only \~75% complete, so miniwasm is not a fully conformant engine, unlike wasm3. No claim against wasmtime, wasmer, WAMR or V8 is published; CI chart artifacts are not available. The Hacker News thread was not readable here (HN blocked). [retier] Bar charts only (res/\*.png at commit 70dd3e6, 2023-01-09): one run each, bench.py ignores exit codes and discards stdout, the SIMD case was built without -msimd128, wasm3 build unstated, M1 laptop. HEAD has since been reworked and carries bounds-check wraparound (addr + size in uint32) and an unchecked random_get, passes 39 of 147 spec files (0 of 57 SIMD), and its default makefile builds without -O (CLAGS_opt typo). No Wasmtime, wasmer, WAMR or V8 column; trap test about 5x slower than wasm3; libsodium issue #4 open.

Single-threaded interpreter; wasm text format about 95%, binary format about 100%, spec tests about 75% complete per README (v0.0.1 first release). Bundles a custom WASI implementation and a small wat2wasm/wasm2wat/wasm2wasm toolkit that is much smaller than WABT or Binaryen. Uses threaded-code dispatch and basic-block versioning from the author's MiniVM; the README says computed-goto style macros (NEXT, LABEL) would need rewriting for MSVC.

## Maintenance

Effectively dormant since May 2023 (one build-refactor commit on 2025-11-06 that introduced the -O typo); MIT-licensed and small enough to vendor, but its HEAD has memory-safety and WASI-output bugs, so a vendored copy should start from a reviewed commit and be limited to trusted code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** README benchmarks section shows first-party PNG bar charts (wasm3 vs miniwasm, 2020 MacBook Air M1, emcc -O2, bench.py and test/bench/\*.c public); my readings of the charts match the record. Not A: the wasm3 baseline's version and build are unstated, the compiler version is unstated, each test ran once, and the charts (commit 70dd3e6, 2023-01-09) cannot be regenerated from current HEAD because bench.py and the makefile changed.
- **Verifier notes:** Chart values confirmed by viewing res/\*.png (wasm3 vs miniwasm, fib_i32 3.0 vs 1.17 s etc.); tier stays C (borderline A on code/flags/CPU, held at C because the wasm3 baseline build is unstated and the charts predate a rewrite). Shortcomings: chart-only single-run numbers, trap 5x slower, \~75% spec-test pass rate, current makefile typo builds without optimisation, no comparison with the category baselines (wasmtime, wasmer, WAMR, V8).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** stated wasm3 build and flags, repeated runs, comparison with a category baseline; fixed bounds checks and a repeated-run harness with exit-code checks
- **Pages the verifier opened:**
  - <https://github.com/FastVM/Web49>
  - <https://github.com/FastVM/Web49#benchmarks>
  - <https://github.com/FastVM/Web49/commits>
  - <https://github.com/FastVM/Web49/commits/main/makefile>
  - <https://github.com/FastVM/Web49/commits/main/res/fib_i32.png>
  - <https://github.com/FastVM/Web49/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/README.md>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/bench.py>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/makefile>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/res/fib_i32.png>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/res/coremark.png>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/res/trap.png>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/.github/workflows/all.yml>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/makefile>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/bench.py>
- **Sources the enricher read:**
  - <https://github.com/FastVM/Web49>
  - <https://github.com/FastVM/Web49/tree/main/res>
  - <https://github.com/FastVM/Web49/issues?q=is%3Aissue>
  - <https://github.com/FastVM/Web49/issues/4>
  - <https://github.com/FastVM/Web49/commits/main>
  - <https://github.com/FastVM/Web49/commit/91d8213>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/README.md>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/makefile>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/bench.py>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/.github/workflows/all.yml>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/results.txt>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/config.h>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/lib.h>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/lib.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/interp/interp.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/interp/interp.h>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/interp/interp0.inc>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/interp/interp1.inc>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/interp/interp2.inc>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/wasi/wasi.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/opt/tree.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/src/opt/tee.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/main/miniwasm.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/res/nop.png>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/res/fib_f32.png>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/res/fib_f64.png>
  - <https://raw.githubusercontent.com/FastVM/Web49/HEAD/res/fib_i64.png>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/makefile>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/bench.py>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/README.md>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/src/interp/interp.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/src/interp/interp.h>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/src/interp/interp1.inc>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/src/api/wasi.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/test/bench/mandelbrot-simd.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/test/bench/fib_i32.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/test/bench/trap.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/test/bench/binary-trees.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/test/bench/nbody.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/test/bench/fannkuch-redux.c>
  - <https://raw.githubusercontent.com/FastVM/Web49/70dd3e6/test/bench/mandelbrot.c>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/fastvm/web49`) · [data/wave12/enrich/raw/github_com_fastvm_web49.json](../../../data/wave12/enrich/raw/github_com_fastvm_web49.json) (enrichment confidence 0.75)

</details>
