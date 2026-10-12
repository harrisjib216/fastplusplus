# wasm2c (WABT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> wasm2c translates a Wasm module to portable C; compiled natively, it outran Wasmtime, Wasmer and V8 on libsodium.

| | |
|---|---|
| **Beats** | Wasmtime, Wasmer (Cranelift, LLVM, Singlepass) and V8 (Node.js) |
| **Claimed result** | Derived from page data (wasm2c.csv vs the other runtimes' CSVs, geomean of per-test time ratios over the 61 tests that have native results): wasm2c 0.68x Wasmtime, 0.71x Wasmer Cranelift, 0.82x Wasmer LLVM, 0.61x Node/V8, 0.22x Wasmer Singlepass; wasm2c geomean 2.36x native vs Wasmtime 3.46x, Wasmer Cranelift 3.34x, Wasmer LLVM 2.89x, Node 3.91x. Not faster than WAMR: iwasm (AOT per the 2023 post, snippet only) is 2.30x native, wasm2c 1.03x iwasm time, slower on 31 of 61 tests. |
| **Workload** | libsodium benchmark suite, 2022-12 run: 61 tests with results for every listed runtime plus native; wasm2c translates Wasm to C which is then compiled natively. |
| **Metric** | throughput |
| **Adoption** | 8.1k stars (WABT toolkit; wasm2c is one tool in it) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/WebAssembly/wabt) · [benchmark](https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasm2c.csv) |

## Verdict

In Frank Denis's 2022-12 libsodium suite (61 tests, per-test times in jedisct1/webassembly-benchmarks/2022-12/res), wasm2c output compiled natively took 0.68x Wasmtime's, 0.71x Wasmer Cranelift's, 0.82x Wasmer LLVM's and 0.61x Node/V8's time by geomean (derived from page data; 2.36x native vs Wasmtime 3.46x); CPU, C compiler and flags are not stated in the results repo, and the C compile step is not timed.

## Use it when

- Sandboxing a C/C++/Rust library inside a native host (the Firefox sandbox use case discussed in issue #2046) where you can add a build step and want near-native speed: 2.36x native geomean vs Wasmtime 3.46x on the 2022-12 libsodium suite.
- CPU-bound modules known at build time (crypto, codecs, parsers) on x86-64 or aarch64 Linux/macOS where guard-page bounds checks are available.
- Targets where a JIT is not allowed or no Wasm runtime exists but a C compiler does: the output is portable C99 with a small runtime.
- When you want to reuse your existing C toolchain, sanitizers, profilers and debuggers on Wasm code.

## Skip it when

- Modules that arrive at run time (plugins, user uploads): every module needs a C compile, and wasm2c itself took about 1 minute (Ryzen 7950X) to over 3 minutes (Apple M3) on one Firefox build module (issue #2343).
- When WAMR AOT is an option: in the same 2022-12 run iwasm AOT was at par (wasm2c used 1.03x iwasm's time geomean, slower on 31 of 61 tests).
- Modules needing proposals the README table marks unsupported in wasm2c: relaxed-simd, function-references, wide-arithmetic (and GC, which is not in the table; issue #2348 'Plan for GC and beyond' is open).
- Memory64 modules, 32-bit hosts, or builds that cannot install a SIGSEGV handler: wasm-rt.h falls back to explicit bounds checks (BOUNDS_CHECK), and on Windows or without the signal handler to stack-depth counting, which costs speed.
- If you need a full runtime with WASI built in: the generated code expects the host to supply WASI imports (the Dhrystone example links uvwasi and libuv).

## How it is fast

Ahead-of-time translation hands the whole module to an optimizing C compiler (clang or gcc at -O2/-O3, optionally -march=native and LTO), so the code gets the same register allocation, inlining and vectorization as native C. On 64-bit hosts linear memory is reserved with mmap and protected by guard pages, so most loads and stores need no explicit bounds check (an empty inline-asm FORCE_READ keeps the compiler from deleting loads that must trap); call_indirect uses a pointer-equality fast path on the function type before a cold slow path. An optional Segue mode (Linux/FreeBSD x86-64, clang 9+, -mfsgsbase, WASM_RT_ALLOW_SEGUE) keeps the linear-memory base in the %gs segment register.

## Compared with alternatives

Pick wasm2c over w2c2 when you want the spec-tracking reference translator (exceptions, tail calls, memory64, multi-memory, SIMD) maintained in the WebAssembly org with production use in Firefox; pick it over WAMR AOT or aWsm when you want plain C output you can build with your own compiler and toolchain rather than a separate AOT compiler, accepting that WAMR AOT matched it on libsodium.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Generated code: libc and libm (pthreads for shared memory); WASI needs a host implementation such as uvwasi. The wasm2c tool itself: CMake 3.16+ build of WABT. |
| **Minimum toolchain** | Generated code: C99 (C11 for threads/atomics); Segue needs clang 9+. Building WABT: C++20 (CMAKE_CXX_STANDARD 20), CMake 3.16. |
| **Platforms** | Any C99 target; guard-page bounds checks need a 64-bit host with mmap and gcc/clang (or clang-cl since a 2026-09 commit); Segue only Linux/FreeBSD x86-64 with clang; big-endian (s390x) supported with stack counting. |
| **Thread safety** | Module instances are separate structs; each extra host thread that runs Wasm code must call wasm_rt_init_thread()/wasm_rt_free_thread() (per-thread trap and stack state, after the race fixes tracked in issue #2046). Shared memories use a lock for memory.grow. |
| **Drop-in for the baseline** | partial: runs the same .wasm modules as Wasmtime/Wasmer/V8, but replaces their runtime embedding API with generated C functions and a compile step; WASI and other imports must be provided by the host. |

## Gotchas

- Spec conformance at -O2/-O3 needs extra flags (wasm2c/README.md): GCC 11 '-fno-optimize-sibling-calls -frounding-math -fsignaling-nans', clang 14 '-fno-optimize-sibling-calls -frounding-math'; without them signalling NaNs survive, OOB-trapping dead loads can be deleted and infinite recursion may not trap (issue #1925). The repo's own Dhrystone/Segue benchmark Makefile compiles with plain -O3 and none of these flags, and the 2022-12 libsodium results do not say which flags were used.
- The default build installs a SIGSEGV handler for guard-page traps and stack exhaustion; hosts with their own signal handling must coordinate or set WASM_RT_SKIP_SIGNAL_RECOVERY (then an OOB access may abort instead of trapping). Without the handler, stack depth counting traps at WASM_RT_MAX_CALL_STACK_DEPTH (default 500), which deep-recursive modules can hit.
- Doc drift: wasm2c/README.md says 'cd wasm2c/benchmarks/segue && make', but the directory is wasm2c/benchmarks/dhrystone; the top-level proposal table leaves threads blank for wasm2c although wasm2c/README.md documents shared memories and atomics.
- Benchmark caveats from the 2022-12 CSVs (recomputed this session): wasm2c was slower than Wasmtime on 2 of 61 tests (auth3 1.32x, keygen 1.43x) and recorded times below native on verify1 and sodium_utils, which points to run-to-run noise in this harness; the CSVs carry no unit, CPU, compiler or flags. The 2026 figures (0.814x Wasmtime, 0.887x Wasmer, search snippet of the blocked 00f.net post) used wide-arithmetic support the author added himself: the upstream README marks wide-arithmetic unsupported in wasm2c and no wasm2c wide-arithmetic PR by him appears in the repo.

## Known shortcomings

- Derived from the jedisct1 2022-12 CSVs, wasm2c beats Wasmtime, Wasmer and V8 but not WAMR (iwasm AOT takes 1.03x wasm2c's time and wasm2c is slower on 31 of 61 tests); no CPU or compiler stated.
- Enricher: the jedisct1 2022-12 CSVs have no unit, CPU, compiler or flags; wasm2c is below native on verify1 and sodium_utils (noisy runs) and slower than Wasmtime on auth3 (1.32x) and keygen (1.43x); the conformance flags (-fno-optimize-sibling-calls -frounding-math) are not stated for the run and the repo's own dhrystone Makefile uses plain -O3. The 2026 figures (0.814x Wasmtime, 0.887x Wasmer) come from Denis's own wide-arithmetic patch (upstream README marks wide-arithmetic unsupported in wasm2c); translating one Firefox module takes 1-3 minutes (#2343).

## Caveats and trade-offs

Not a win over every category baseline: in the same 2022-12 run WAMR iwasm (AOT-compiled per the 00f.net 2023 post, search snippet only) is at par or slightly ahead (wasm2c 1.03x iwasm time geomean over 61 tests, wasm2c slower on 31 of them; iwasm 2.30x native vs wasm2c 2.36x, derived from page data). The results repo (archived 2026-08-19) has no compiler, flags or CPU model for the 2022-12 run (methodology lives in the blocked 00f.net post) and the CSV unit is not stated; lower is better (native lowest, wasm3 highest), so only ratios are used. The native column uses hardware AES on the AEGIS tests (about 74x faster than any Wasm runtime there), which inflates every runtime's x-native geomean equally. Frank Denis's 2026 post (search snippet only, 00f.net blocked) reports wasm2c built with zig cc -O3 -march=native at 0.814x Wasmtime and 0.887x Wasmer geomean with wide_arithmetic, and WAMR AOT at about 1.57x native. The wasm2c C-compile step is not part of the measured time, and the C compiler and flags used to build the wasm2c output in 2022-12 are not public.

Ahead-of-time only: the generated C must be compiled by a C compiler per module, so no JIT and an extra build step. Optional Segue optimisation (Linux x86-64, clang with -mfsgsbase) and optional extra sanity checks (WASM_RT_SANITY_CHECKS, high overhead, meant for debug builds) are described in wasm2c/README.md.

## Maintenance

Actively maintained in the WebAssembly org (wasm2c fixes on 2026-09-16 and 2026-10-05), Apache-2.0; the generated C plus two runtime files are easy to vendor into any build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party libsodium suite by Frank Denis (jedisct1/webassembly-benchmarks 2022-12/res/\*.csv, per-test times for wasm2c, Wasmtime, Wasmer, Node, iwasm and native); recomputing the geomeans from the CSVs reproduces every ratio in the record. The results repo states no CPU model, compiler or flags (methodology is in the blocked 00f.net post), so not A; same treatment as the WAVM entry from this suite.
- **Verifier notes:** All record ratios reproduced exactly from the 12 CSVs (61 common tests). Main shortcoming to record: WAMR iwasm AOT in the same run ties or beats wasm2c (1.03x, 31 of 61 tests slower), so the win is over Wasmtime, Wasmer and V8 only; no CPU or compiler stated in the results repo. Related entry w2c2 (turbolent/w2c2) is a separate Wasm-to-C translator, not a duplicate.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasm2c.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmtime.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-cranelift.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-llvm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-singlepass.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/node.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/native.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/iwasm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasm3.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/bun.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmedge.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wazero.csv>
  - <https://github.com/jedisct1/webassembly-benchmarks>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12/res>
  - <https://github.com/WebAssembly/wabt>
  - <https://github.com/WebAssembly/wabt/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/WebAssembly/wabt/HEAD/wasm2c/README.md>
  - <https://raw.githubusercontent.com/WebAssembly/wabt/HEAD/README.md>
  - <https://raw.githubusercontent.com/WebAssembly/wabt/HEAD/wasm2c/wasm-rt.h>
  - <https://raw.githubusercontent.com/WebAssembly/wabt/HEAD/src/template/wasm2c.declarations.c>
  - <https://raw.githubusercontent.com/WebAssembly/wabt/HEAD/wasm2c/benchmarks/dhrystone/Makefile>
  - <https://raw.githubusercontent.com/WebAssembly/wabt/HEAD/CMakeLists.txt>
  - <https://github.com/WebAssembly/wabt/tree/main/wasm2c>
  - <https://github.com/WebAssembly/wabt/commits/main>
  - <https://github.com/WebAssembly/wabt/issues?q=is%3Aissue+wasm2c+performance>
  - <https://github.com/WebAssembly/wabt/issues/2343>
  - <https://github.com/WebAssembly/wabt/issues/1925>
  - <https://github.com/WebAssembly/wabt/issues/2046>
  - <https://github.com/WebAssembly/wabt/pulls?q=is%3Apr+wide+arithmetic>
  - <https://github.com/WebAssembly/wabt/pulls?q=is%3Apr+author%3Ajedisct1>
  - <https://github.com/jedisct1/webassembly-benchmarks/tree/master/2022-12>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasm2c.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmtime.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/iwasm.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/native.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/node.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-cranelift.csv>
  - <https://raw.githubusercontent.com/jedisct1/webassembly-benchmarks/HEAD/2022-12/res/wasmer-llvm.csv>
  - https://00f.net/2026/07/08/webassembly-compilation-to-c-2026/ (search snippet only, host blocked)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/webassembly/wabt`) · [data/wave12/enrich/raw/github_com_webassembly_wabt.json](../../../data/wave12/enrich/raw/github_com_webassembly_wabt.json) (enrichment confidence 0.75)

</details>
