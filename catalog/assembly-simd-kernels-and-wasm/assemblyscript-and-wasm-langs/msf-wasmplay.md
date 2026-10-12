# Zig wasm32-wasi build in msf/wasmplay

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟡 stale

> Zig-vs-C++-vs-Go benchmark repo: Zig ReleaseFast wasm32-wasi edges Emscripten -O2 C++ on one integer matmul loop.

| | |
|---|---|
| **Beats** | C++ compiled to WebAssembly with Emscripten (em++ -O2), run on the same WASM runtime; also Go (GOOS=wasip1) wasm |
| **Claimed result** | Zig to WasmEdge 15,305 ops/sec vs C++ (em++ -O2) to WasmEdge 11,855 ops/sec, about 1.29x (derived from page data); Go to WasmEdge 3,230 ops/sec. Only the WasmEdge row is reported for Zig wasm; C++ wasm on other runtimes: Wasmer LLVM 11,160, Wasmtime 6,988, Wasmer Cranelift 6,911 ops/sec. The README note that Zig WASM is 'nearly matching C++ optimized native' is contradicted by its own numbers: C++ optimized native (-O3 -march=native) is 49,279 ops/sec, about 3.2x faster than Zig wasm (derived from page data); Zig wasm instead matches Zig native ReleaseFast (15,386 ops/sec). |
| **Workload** | 64x64 integer matrix multiplication with FNV-1a hash, 10,000 chained iterations, ops/sec, pinned to one core with taskset |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen AI 9 HX 370 (12 cores, 24 threads, up to 5.16 GHz), Ubuntu 24.04 (Linux 6.14.0-29-generic), single core pinned (CPU 0) |
| **Compiler and flags** | Zig: zig build-exe -O ReleaseFast -target wasm32-wasi (Zig version only given as 0.13+). C++ wasm baseline: em++ -std=c++20 -O2 (emsdk 'latest', version unstated), no hardening flags. C++ native: g++ -std=c++20 -O2 plus OpenSSF hardening flags (_FORTIFY_SOURCE=3, _GLIBCXX_ASSERTIONS, stack protector) for 'standard', -O3 -march=native -mtune=native -flto -DNDEBUG plus the same hardening flags for 'optimized'. Go: GOOS=wasip1 GOARCH=wasm go build (Go 1.24+). Runs pinned with taskset -c 0; WasmEdge run with --enable-jit. |
| **Adoption** | 0 stars |
| **Last commit** | 2025-09-01 |
| **Links** | [repository](https://github.com/msf/wasmplay) · [benchmark](https://github.com/msf/wasmplay#performance-results) |

## Verdict

On one pinned core of an AMD Ryzen AI 9 HX 370 (Ubuntu 24.04), the Zig ReleaseFast wasm32-wasi build ran 15,305 ops/sec under WasmEdge JIT against 11,855 for the same 64x64 u64 matmul + FNV-1a loop compiled by em++ -O2, about 1.29x (derived from page data). Each figure is a single run with unstated compiler and runtime versions, and native GCC -O3 -march=native C++ (49,279 ops/sec) beats both wasm builds by more than 3x.

## Use it when

- As a template for comparing standalone WASI runtimes on a scalar 64-bit integer kernel: make bench-wasm-runtimes loops the Go, C++ and Zig modules over Wasmer Cranelift, Wasmer LLVM, Wasmtime and WasmEdge JIT.
- To sanity-check that Zig's wasm32-wasi output keeps up with Emscripten's for a CPU-bound, non-SIMD integer loop running outside a browser (WASI command modules).
- When choosing between Zig and Go for WASI modules: Go's wasip1 build ran 3,230 vs Zig's 15,305 ops/sec on WasmEdge (4.7x, derived from page data).
- To see how much the runtime matters: the same C++ module ran 11,855 ops/sec on WasmEdge and 6,911 on Wasmer Cranelift (1.7x, derived from page data).

## Skip it when

- As evidence that Zig beats C++ for wasm: the baseline is em++ -O2 rather than -O3, and the Zig wasm row exists only for WasmEdge; rebuild the C++ module at -O3 before concluding anything.
- For browser, Node.js or V8 workloads: nothing runs in a JavaScript engine and there are no JavaScript or TypeScript rows.
- For SIMD-heavy or floating-point kernels: neither wasm build enables simd128, and the only workload is a 64x64 u64 matmul plus FNV-1a hash.
- As reusable code: there is no library, no tests and no CI; 0 stars, 8 commits all made on 2025-09-01.
- For statistically sound numbers: each README row is one process run with one wall-clock timing, no repeat count, no variance and unstated compiler and runtime versions.

## How it is fast

No special technique: all three sources are the same naive i-j-k triple loop over stack arrays with wrapping 64-bit multiplies. The Zig build is ReleaseFast (LLVM at full optimisation, safety checks off) while the Emscripten build is -O2, and neither enables wasm SIMD (no -msimd128, no simd128 CPU feature), so both emit scalar i64 code and the 1.29x gap more plausibly reflects the optimisation level than the language. Zig wasm under WasmEdge's LLVM-based JIT (15,305 ops/sec) lands on Zig native ReleaseFast (15,386), so for this scalar loop the runtime recovers native code quality.

## Compared with alternatives

Unlike wasm-perf, Speedy.js or the Chankse JavaScript-vs-WebAssembly matmul study, which measure wasm against JavaScript in V8, this repo compares source languages (Zig, C++, Go) on standalone WASI runtimes, so it only fits a server-side WASI runtime or language question; for C++-to-wasm compiler quality, Cheerp's claim against Emscripten is the closer catalogued comparison, and neither is strong evidence.

## Integration

| | |
|---|---|
| **Form** | source-drop (three standalone benchmark programs and a Makefile; not a library) |
| **Dependencies** | Zig 0.13+, Emscripten (emsdk 'latest', unpinned), Go 1.24+, g++ or clang++, taskset, and the Wasmer, Wasmtime and WasmEdge CLIs |
| **Minimum toolchain** | Zig 0.13+ and Go 1.24+ per the README; C++20; Emscripten version not stated |
| **Platforms** | Linux host for the Makefile (taskset, \~/.wasmedge/bin path); the wasm32-wasi modules run on any WASI runtime |
| **Thread safety** | not applicable (single-threaded programs) |
| **Drop-in for the baseline** | no |

## Gotchas

- Stack-size asymmetry (possible harness flaw, not reproduced here because nothing was built): matmul_and_hash keeps three 64x64 u64 arrays on the stack, about 96 KB per call. Zig 0.13 gives wasm32-wasi executables a 16 MiB stack by default (src/link/Wasm.zig), but Emscripten's default STACK_SIZE is 64 KB and overflow is unchecked at -O2 (settings.js: 'it will fail silently'); the em++ line sets no -sSTACK_SIZE. A rebuild of the C++ wasm module may therefore trap or corrupt memory, and the README omits the printed Result hashes that would show all builds computed the same value.
- The per-language targets (make bench-cpp-wasm, bench-zig-wasm, bench-go-wasm) run under Wasmer's default engine; the WasmEdge rows come from make bench-wasm-runtimes, which also runs the Zig module on Wasmer Cranelift, Wasmer LLVM and Wasmtime, yet the README publishes no Zig numbers for those three runtimes.
- The README note that Zig WASM is 'nearly matching C++ optimized native' contradicts its own table (15,305 vs 49,279 ops/sec, 3.2x slower). The 4.2x 'C++ optimized' native gain mixes -O2 to -O3, LTO and -march=native on a Zen 5 CPU with AVX-512; GCC's -O3 loop interchange plus 64-bit vector multiplies is a likely cause (not measured), so it says nothing about wasm.
- Makefile has dead targets: bench-cpp-wasm-opt depends on an undefined build-cpp-wasm-opt and runs a bench-cpp-opt.wasm nothing builds, and the help text lists a bench-wasm target that does not exist.

## Known shortcomings

- Downgraded A to C: Emscripten baseline built -O2 against Zig ReleaseFast; one run per row; Zig wasm on WasmEdge only; toolchain versions unstated; 0 stars; the README's 'nearly matching C++ optimized native' contradicts its own numbers (49,279 vs 15,305, 3.2x).
- Possible harness flaw, unconfirmed (nothing built): the C++ frame holds three 32 KB arrays (96 KB) while Emscripten's default STACK_SIZE is 64 KB with overflow unchecked at -O2 ('fail silently'), and Zig 0.13 gives wasm32-wasi a 16 MiB stack, so the em++ baseline may overflow; the README omits the result hashes that would prove parity. -O2 vs ReleaseFast; Zig rows for Wasmer and Wasmtime are omitted although bench-wasm-runtimes runs them; dead Makefile targets; the 'nearly matching native' note is wrong (3.2x slower).

## Caveats and trade-offs

Unequal optimisation levels: the Zig WASM is ReleaseFast (LLVM -O3, no safety checks) while the Emscripten C++ WASM is -O2. Compiler and runtime versions are not stated. Single toy microbenchmark (64x64 u64 matmul + FNV-1a), one run per row, no variance or repeat count. Zig wasm is reported on WasmEdge only. Not run in V8, so it shows nothing against the TypeScript/JS baseline. The README note claiming Zig WASM nearly matches C++ optimized native is wrong by its own figures (3.2x slower). 0 stars, 8 commits all on 2025-09-01.

Runs as WASI modules under WasmEdge, Wasmer or Wasmtime, not in a browser or V8; results depend on the runtime JIT (WasmEdge beat Wasmtime and Wasmer Cranelift for C++).

## Maintenance

Stale since 2025-09-01 (8 commits in one day, 0 stars, no issues), MIT-licensed and trivially copyable, but it is a benchmark playground rather than a component, and the -O2 vs ReleaseFast baseline plus a probable 64 KB Emscripten stack overflow in the C++ wasm build (not reproduced) mean the 1.29x should not be relied on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** Public code (benchmark.cpp, benchmark.zig, Makefile) and a stated CPU, but the Emscripten baseline is built at -O2 while the Zig contender is ReleaseFast, compiler versions are unstated (Zig '0.13+', emsdk 'latest'), each row is a single run with no variance, and the 1.29x margin rests on one runtime (WasmEdge); first-party numbers with a handicapped baseline are C.
- **Verifier notes:** Sources implement the same algorithm and print the chained result, so the evidence is not invalid, but the baseline is built at a lower optimisation level than the contender and every row is one run, so A drops to C. Shortcomings to record: -O2 vs ReleaseFast, single run, WasmEdge only, unversioned toolchains, misleading README note, toy repo with 0 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-18 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/msf/wasmplay#performance-results>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/README.md>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/Makefile>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/benchmark.zig>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/benchmark.go>
  - <https://github.com/msf/wasmplay>
  - <https://github.com/msf/wasmplay/commits/main>
- **Sources the enricher read:**
  - <https://github.com/msf/wasmplay>
  - <https://github.com/msf/wasmplay/commits/main>
  - <https://github.com/msf/wasmplay/commit/a15e99c>
  - <https://github.com/msf/wasmplay/issues>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/README.md>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/Makefile>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/benchmark.cpp>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/benchmark.zig>
  - <https://raw.githubusercontent.com/msf/wasmplay/HEAD/benchmark.go>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/main/src/settings.js>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/main/src/settings_internal.js>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/main/tools/building.py>
  - <https://raw.githubusercontent.com/emscripten-core/emscripten/main/tools/link.py>
  - <https://raw.githubusercontent.com/ziglang/zig/0.13.0/src/link/Wasm.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.13.0/src/Compilation.zig>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/msf/wasmplay`) · [data/wave13/enrich/raw/github_com_msf_wasmplay.json](../../../data/wave13/enrich/raw/github_com_msf_wasmplay.json) (enrichment confidence 0.6)

</details>
