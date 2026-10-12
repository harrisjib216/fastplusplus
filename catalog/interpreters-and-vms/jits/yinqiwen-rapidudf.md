# RapidUDF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> LLVM-JIT C-like expression/UDF engine for C++ with SIMD column ops; 6-10x over scalar native loops, scalar code slightly slower than native.

| | |
|---|---|
| **Beats** | native scalar C++ (GCC -O2 for the fib comparison; native loops for the vector cases) |
| **Claimed result** | README: trigonometric expression over a 4099-element double array, vectorised JIT 33,962 ns vs native 207,145 ns and scalar JIT 207,713 ns (6.10x, derived from page data); Wilson CTR over floats, vectorised JIT 6,661 ns vs native 69,961 ns ('10.5x'), but the native baseline used double literals (1.96) and ran in f64, so this is f32 SIMD against f64 scalar; the PR #9 rerun with T(1.96) gives 9.3x f32 against f32 (32-core Skylake, debug bazel build). Scalar JIT fib is 5-17% slower than native -O2. |
| **Workload** | LLVM-JIT compiled expressions/UDFs: Fibonacci function, a trigonometric expression over a 4099-element double array, and a Wilson CTR formula over float vectors, JIT with SIMD vectorisation versus the equivalent native C++ function. |
| **Metric** | throughput |
| **Hardware** | a CPU supporting AVX2 (model not stated) |
| **Compiler and flags** | README: optimisation flag -O2 for the vectorised tests; native fib built at GCC -O0 and -O2; JIT at RapidUDF's default LLVM optimize_level 2 (LLVM 18+); compiler version and -march not stated. Current harness rapidudf/tests/BUILD builds benchmark.cc with copts -O2. |
| **Adoption** | 100 stars |
| **Last commit** | 2026-05-24 |
| **Links** | [repository](https://github.com/yinqiwen/rapidudf) · [benchmark](https://github.com/yinqiwen/rapidudf) |

## Verdict

The README (AVX2 CPU unnamed, -O2, 4099-element arrays, Google Benchmark) shows the vectorised JIT computing a sin/cos expression over doubles in 33,962 ns vs 207,145 ns for a native scalar loop (6.1x, derived from page data). A float Wilson CTR formula ran in 6,661 ns vs 69,961 ns (10.5x), but against a baseline evaluated in double precision. Scalar JIT fib was 17% slower than GCC -O2 native (22,557 vs 19,246 ns). A later rerun with the rewritten harness (PR #9, 32-core Skylake, debug Bazel build) reports 7.4x, 3.6x (f64) and 9.3x (f32) over scalar native, with fib 5% slower than native.

## Use it when

- Rule engines, ranking or feature pipelines that evaluate user-supplied formulas over float/double columns of thousands of rows, where scalar libm calls dominate (sin, cos, log10, sqrt): 6-10x over a plain scalar C++ loop in the vendor's AVX2 runs.
- You need formulas changed at run time without recompiling the service, with near-native scalar speed (fib JIT 22.5 us vs 19.2 us for GCC -O2 native in the README).
- Filter/topk/group_by over columnar data built from protobuf, flatbuffers or plain structs inside a C++ server, without embedding a full query engine.
- Single-node x86-64 servers with AVX2 or AVX-512, where Highway's dynamic dispatch picks the widest target.

## Skip it when

- You can write the kernel ahead of time: a C++ loop calling Highway or SLEEF directly (or GCC with -O2 -ffast-math and libmvec) gets the same SIMD gain without LLVM in the process. The JIT adds nothing to scalar speed, which is 5-17% slower than GCC -O2 native on fib (PR #9 and README).
- You need results bit-identical to glibc libm: vector sin, cos and log10 use Highway approximations (up to 3 ULP for sin/cos), and sin/cos are only valid within [-39000, +39000].
- Latency-critical paths that cannot absorb 10-100 ms compile time per new expression, or binaries that cannot take LLVM 18+, Highway, SLEEF, x86-simd-sort, abseil, Boost, protobuf and flatbuffers as dependencies.
- ARM or non-x86 hosts: the CMake build links only LLVM's X86 code generator, and an ARM build is not documented, although NEON SLEEF paths were added to the SIMD kernels.
- Projects that need a stable ABI, a shared library or an active issue tracker: the CMake file says no ABI stability, the issue tracker is empty, and there are no tagged releases.

## How it is fast

Scalar UDFs are lowered to LLVM IR and compiled by ORC LLJIT for the host CPU (JITTargetMachineBuilder::detectHost, -O2 pass pipeline by default), so they run at roughly native speed. Vector UDFs are strip-mined into 64-element chunks (kVectorUnitSize) held as LLVM &lt;64 x T&gt; vectors for arithmetic. Transcendental functions call precompiled Google Highway kernels with runtime CPU dispatch (HWY_DYNAMIC_DISPATCH): hn::Sin, hn::Cos, hn::Log10 and similar polynomial approximations, with SLEEF for tan, cosh, erf and other functions Highway lacks. The speedup is SIMD plus approximate vector math against scalar libm calls, not the JIT itself.

## Compared with alternatives

Pick RapidUDF over AsmJit or sljit when you want a high-level expression/DSL front end with columnar SIMD built in instead of emitting machine code yourself. Pick it over PochiVM or Easy::jit when expressions arrive as strings at run time rather than as C++ code to be specialised; for raw scalar JIT speed none of these beat a GCC -O2 build.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | LLVM 18+, Google Highway 1.4.0, SLEEF 3.9.0, x86-simd-sort, abseil-cpp, fmtlib, spdlog, Boost (preprocessor, parser, thread, system), protobuf, flatbuffers, nlohmann/json |
| **Minimum toolchain** | C++17; LLVM 18+; Bazel or CMake 3.14+ |
| **Platforms** | x86-64 Linux (CMake links LLVM x86codegen only; Highway dispatches SSE2 to AVX-512 at run time); ARM NEON kernels exist for the SIMD functions, but an ARM JIT build is not documented |
| **Thread safety** | README: compiled JIT functions are stateless and thread-safe; each call that allocates vectors needs its own rapidudf::Context arena. JitCompiler thread safety is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the README's 10.5x Wilson CTR figure: the native baseline is declared float wilson_ctr(float, float) but uses double literals (1.96, 1.96 \* 1.96), so C++ evaluates it in double precision. The f32 SIMD JIT was compared against a scalar f64 computation. The rewritten harness (rapidudf/tests/benchmark.cc) casts the literals with T(1.96) to avoid this, and the PR #9 rerun reports 9.3x for f32 vs f32 scalar native.
- The benchmark binary is built with copts -O2 and no -march, so the native side targets baseline x86-64 (SSE2) and makes scalar libm calls, which GCC will not vectorise without -ffast-math. The JIT side uses detectHost and Highway dynamic dispatch (AVX2/AVX-512). README numbers also come from an older harness whose benchmark names no longer exist, with no CPU model or compiler version. The PR #9 rerun was a 'bazel-built debug binary' on a '32-core Skylake'.
- Vector tails are handled by copying the remaining n elements into a buffer padded with 1s (LoadNVector), so reductions are not polluted. Bit (1-bit) vectors, however, are loaded and stored as a full 64-lane word regardless of n (compiler/codegen_vector.cc), so bit buffers must be padded.
- Vector UDFs need a rapidudf::Context argument for arena allocation, and runtime errors arrive as rapidudf::UDFRuntimeException, so callers must catch exceptions. Older JIT builds had correctness bugs fixed in May 2026: signed casts emitted zext instead of sext, string literals over 12 characters dangled (PR #6), and scalar float casts used swapped FPExt/FPTrunc (PR #9).

## Known shortcomings

- The 6.1x/10.5x win is Highway SIMD math against scalar libm, not JIT against ahead-of-time code; the fib JIT is 17% slower than native -O2, the README numbers come from an older harness (benchmark.cc has since been rewritten), and CPU and compiler are unstated.
- Enricher: the README Wilson CTR native baseline (float wilson_ctr(float, float)) uses double literals such as 1.96, so the baseline ran in f64 and the 10.5x is f32 SIMD against f64 scalar; the current harness casts T(1.96) and the PR #9 rerun gives 9.3x f32 against f32 (32-core Skylake, debug bazel build). The native benchmark is built -O2 without -march (SSE2) using scalar libm while the JIT uses detectHost plus Highway dynamic dispatch; Highway sin and cos are valid only within [-39000, 39000] at up to 3 ULP. PR #6 fixed a zext/sext cast bug.

## Caveats and trade-offs

The 6x and 10.5x wins come from SIMD vectorisation (Highway, AVX2) against a scalar native loop that GCC cannot auto-vectorise at -O2 because of libm calls; scalar JIT is 17% slower than native -O2 on fib, and the only 'faster than native' scalar result is against a -O0 build. In the current code sin, cos and log10 on vectors use Highway contrib math (hn::Sin, hn::Cos, hn::Log10, a few ULP and range-limited) rather than glibc libm, with SLEEF only for cosh, tan, erf, pow and similar, so results are not bit-identical to the native baseline. The README numbers come from an older harness: their benchmark names do not appear in the current rapidudf/tests/benchmark.cc, which now runs scalar/vector x native/JIT for trig, Wilson CTR f32/f64, an order rule and fib(20). CPU model and compiler version unstated. Baseline is native C++, not one of PyPy, LuaJIT, V8, HotSpot. [retier] The wins are Highway SIMD math (detectHost plus dynamic dispatch) against a scalar libm loop built -O2 without -march (SSE2 baseline) that GCC cannot auto-vectorise, not JIT against ahead-of-time code; the Wilson CTR baseline ran in f64 (double literals), so the 10.5x is not like for like (9.3x in the PR #9 rerun). Highway sin and cos are valid only within [-39000, 39000] at up to 3 ULP. The README numbers come from an older harness (benchmark.cc has since been rewritten); CPU and compiler unstated; PR #6 fixed a zext/sext cast bug.

Requires LLVM 18+, highway, x86-simd-sort, sleef, abseil and others; C++17; supports a C-like DSL and table API.

## Maintenance

Active (last commit 2026-05-24, 125 commits, a burst of correctness fixes and a benchmark rewrite in May 2026), Apache-2.0 and copyable, but a single-maintainer project with 100 stars, no releases, no ABI promise and a heavy dependency stack; its README numbers predate the current harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance section gives first-party Google Benchmark output against native C++ with only 'a CPU that supports AVX2' and '-O2'; no CPU model or compiler version, and the printed benchmark names (BM_rapidudf_vector_expr_func, BM_native_wilson_ctr, BM_rapidudf_fib_func) are not in the current harness rapidudf/tests/benchmark.cc, which was rewritten, so not A.
- **Verifier notes:** Record accurate apart from the fib wording (JIT 17% slower than native -O2, not on par). Shortcomings: win is SIMD math versus scalar libm, not JIT versus AOT; README numbers from an older, since-rewritten harness; CPU and compiler unstated; vector sin/cos/log10 use lower-precision Highway approximations.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/README.md>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/LICENSE>
  - <https://github.com/yinqiwen/rapidudf>
  - <https://github.com/yinqiwen/rapidudf/commits>
  - <https://github.com/yinqiwen/rapidudf/tree/main/rapidudf>
  - <https://github.com/yinqiwen/rapidudf/tree/main/rapidudf/tests>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/tests/benchmark.cc>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/tests/BUILD>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/tests/CMakeLists.txt>
  - <https://github.com/yinqiwen/rapidudf/tree/main/rapidudf/functions>
  - <https://github.com/yinqiwen/rapidudf/tree/main/rapidudf/functions/simd>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/functions/simd/sleef_dispatch-inl.h>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/functions/simd/vector_unary.cc>
- **Sources the enricher read:**
  - <https://github.com/yinqiwen/rapidudf>
  - <https://github.com/yinqiwen/rapidudf/commits/main>
  - <https://github.com/yinqiwen/rapidudf/issues?q=is%3Aissue>
  - <https://github.com/yinqiwen/rapidudf/pull/9>
  - <https://github.com/yinqiwen/rapidudf/pull/6>
  - <https://github.com/yinqiwen/rapidudf/tree/main/rapidudf>
  - <https://github.com/yinqiwen/rapidudf/tree/main/rapidudf/compiler>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/README.md>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/LICENSE>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/WORKSPACE>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/cmake/rapidudf-deps.cmake>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/rapidudf.h>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/copts/configure_copts.bzl>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/tests/benchmark.cc>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/tests/BUILD>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/compiler/options.h>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/compiler/codegen.cc>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/compiler/codegen_vector.cc>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/compiler/compiler.cc>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/functions/simd/vector_unary.cc>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/functions/simd/sleef_dispatch-inl.h>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/functions/simd/vector.h>
  - <https://raw.githubusercontent.com/yinqiwen/rapidudf/main/rapidudf/types/vector.h>
  - <https://raw.githubusercontent.com/google/highway/master/hwy/contrib/math/math-inl.h>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/yinqiwen/rapidudf`) · [data/wave12/enrich/raw/github_com_yinqiwen_rapidudf.json](../../../data/wave12/enrich/raw/github_com_yinqiwen_rapidudf.json) (enrichment confidence 0.7)

</details>
