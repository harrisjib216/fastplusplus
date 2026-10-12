# PochiVM (copy-and-patch baseline compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🔴 abandoned

> C++-embedded JIT DSL whose copy-and-patch backend generates code about 100x faster than LLVM -O0, with 14% faster output.

| | |
|---|---|
| **Beats** | LLVM 10.0.0 JIT backend of the same metaprogramming system at -O0 (also -O1/-O2/-O3) for code-generation time and generated-code speed, plus an in-house AST interpreter (about 1.5x faster than the Peloton interpreter) |
| **Claimed result** | OOPSLA 2021 paper, Section 7.3 and Fig. 24: on 8 TPC-H queries copy-and-patch generates code two orders of magnitude faster than LLVM -O0 (up to 276x) and three orders of magnitude faster than -O1/-O2/-O3 (1083x-1435x, average 1286x); the generated code runs on average 14% faster than LLVM -O0 but 22% slower than -O1, 25% slower than -O2 and 24% slower than -O3; the AST interpreter executes 6x-27x slower than copy-and-patch (Fig. 25). Example: TPC-H Q5 code generation takes 178 us versus 0.25 s with LLVM -O3, whose code is 1.2% faster. |
| **Workload** | Eight TPC-H queries (Q1, Q3, Q5, Q6, Q10, Q12, Q14, Q19) with hand-coded query plans over a dbgen scale-factor-0.3 database (about 380 MB), lowered through PochiVM's C-like DSL to copy-and-patch, LLVM -O0..-O3 or an AST interpreter; plus Fibonacci, Euler sieve and quicksort microbenchmarks. Harness: test_mini_db_backend_unit_test.cpp (PaperBenchmark.TpchQuery\*) and test_paper_microbenchmarks.cpp; each configuration repeated at least 100 times, average reported. |
| **Metric** | compile-time |
| **Hardware** | Intel Core i7-7700HQ at 2.80 GHz, single socket, 8 logical cores, turbo boost on, 32 GB RAM, Ubuntu 20.04 (paper Section 6.1, reused in 7.1) |
| **Compiler and flags** | Stencils and copy-and-patch runtime compiled by Clang++ 10 with -O3 -DNDEBUG; LLVM backend uses the LLVM 10.0.0 library (paper Section 7.1); repo CMakeLists.txt production flavor: clang++ -O3 -DNDEBUG -pthread |
| **Adoption** | 111 stars |
| **Last commit** | 2021-09-09 |
| **Links** | [repository](https://github.com/sillycross/PochiVM) · [benchmark](https://raw.githubusercontent.com/fredrikbk/fredrikbk.github.io/master/publications/copy-and-patch.pdf) |

## Verdict

In the authors' OOPSLA 2021 paper (Xu and Kjolstad), on 8 hand-planned TPC-H queries over a scale-factor-0.3 database on an Intel i7-7700HQ, copy-and-patch generated code up to 276x faster than LLVM 10.0.0 at -O0 and 1083x-1435x faster than -O1..-O3 (stencils built by Clang++ 10 -O3 -DNDEBUG, LLVM limited to x86-64 baseline features). Its code ran 14% faster than -O0 and 22%-25% slower than -O1..-O3 on average, and the AST interpreter was 6x-27x slower; the public harness reproduces these runs but reports the best of 10-20 runs rather than the paper's stated averages.

## Use it when

- A C++ engine that generates many short-lived programs (query, rule or expression engines) where compile latency dominates: TPC-H Q5 generates code in 178 us versus 0.25 s with LLVM -O3, and the query itself runs in under 0.1 s.
- Replacing an AST or bytecode interpreter: the paper measures copy-and-patch code 6x-27x faster than its AST interpreter for 2-3x the (still negligible) setup cost.
- A two-tier design: the same DSL program can go to copy-and-patch first and to LLVM -O2/-O3 later for hot, long-running code, since all three backends take one AST.
- Studying or prototyping copy-and-patch itself: the stencil generator, CPS/GHC calling-convention tricks and paper harness are all in the repo.

## Skip it when

- Long-running generated code: LLVM -O1..-O3 output is 22%-25% faster; in the paper's Q5 example the -O3 compile cost pays back only after about 21 s of execution.
- Anything other than Linux on x86-64: the docs say only Linux is supported, the build runs in an Ubuntu 18.04 Docker image with the x86_64 LLVM 10.0.0 release, and stencils are x86-64 machine code.
- Production dependencies: abandoned since 2021-09-09, an open build failure (issue #4, 2024: cp of libtinfo.so.5 into shared_libs gets Permission denied), no packaged release (the project template is marked UNDONE), and the docs say the test suite fails in the production build.
- When you already emit LLVM IR: PochiVM only compiles programs written through its own DSL.
- Tight footprint: the stencil library takes 14 min on 6 threads to build and 17.5 MB of memory at runtime.

## How it is fast

Copy-and-patch: at install time Clang compiles 98,831 pre-built machine-code 'stencils' (one per AST node type and configuration) with holes for constants, jump targets and stack offsets; at runtime code generation just memcpys the matching stencils and patches the holes, with no instruction selection or IR. Stencils use continuation-passing style with tail calls lowered to jumps and the GHC calling convention, so the next stencil is reached by a jump and values stay in registers (a lightweight register-allocation protocol); further gains come from jump removal, supernodes and block alignment. Generation is linear in program size, unlike LLVM's non-linear passes.

## Compared with alternatives

TPDE takes ordinary LLVM IR, compiles 10-20x faster than LLVM -O0 at similar code quality and is maintained, so prefer it when you have IR. PochiVM's copy-and-patch is roughly ten times faster again at code generation but requires its DSL and is abandoned; pick it to embed a C++ code generator with interpreter-like startup, or as the reference for the technique also used by WasmNow and CPython's copy-and-patch JIT.

## Integration

| | |
|---|---|
| **Form** | source-drop (fork the repository and build your project inside its Docker/CMake tree; no installable library) |
| **Dependencies** | Clang and LLVM 10.0.0 (pinned in dockerfile/Dockerfile), Docker, CMake with Ninja, ccache (CMakeLists aborts without it), Python 3 build script, libtinfo; gtest vendored |
| **Minimum toolchain** | C++17 with Clang/LLVM 10.0.0 as pinned by the Docker image; other LLVM versions not documented |
| **Platforms** | Linux x86-64 only (docs: 'Only Linux is supported at the moment') |
| **Thread safety** | Build state lives in a thread_local PochiVMContext (thread_pochiVMContext), so each thread builds its own modules; sharing a module across threads is not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Known unfixed miscompile risk: pochivm/cast_expr_fastinterp.cpp carries 'TODO: FIXME: casting int to float changes the register location..' (commit 591c506, July 2021); the copy-and-patch path emits reinterpret_cast between integer and floating types as a no-op even though the value must move between register classes. Avoid int/float bit casts in copy-and-patch mode; the TPC-H queries do not use them and their correctness tests check copy-and-patch output against expected results.
- Harness differs from the paper's stated method: the paper reports averages of at least 100 runs, but the public BenchmarkTpchQuery and GetBestResultOfRuns report the minimum of 10 runs (20 for copy-and-patch code generation). Each LLVM timing also builds a fresh LLJIT, about 1 ms of fixed startup that the paper amortizes only in the microbenchmarks. This is a reproduction gap, not invalid evidence.
- For a fair comparison the benchmark LLVM JIT is pinned to the x86-64 baseline target (SSE2, no AVX), the same as the stencils. Neither backend uses AVX, so absolute -O3 numbers are below what -march=native would give.
- The DSL has no const, volatile or rvalue-reference types, and generated function prototypes may take and return only fundamental types. C++ call inlining and LLVM optimization happen only in release/production builds.

## Known shortcomings

- Upgraded C to A on the OOPSLA 2021 copy-and-patch paper (PDF reachable at raw.githubusercontent.com/fredrikbk/fredrikbk.github.io/master/publications/copy-and-patch.pdf: i7-7700HQ, Clang++ 10 -O3 -DNDEBUG, LLVM 10) with the harness in the repo (test_mini_db_backend_unit_test.cpp PaperBenchmark.TpchQuery\*, test_paper_microbenchmarks.cpp). The win is compile time: generated code is 22-25% slower than LLVM -O1 to -O3, the prototype query compiler covers only 8 TPC-H queries, the licence is stated in the README only (no LICENSE file), abandoned 2021.
- Enricher: the paper says an average of 100+ runs while the public harness reports the minimum of 10 runs (20 for copy-and-patch codegen); LLVM timing builds a fresh LLJIT per query (about 1 ms fixed cost) and LLVM is pinned to the SSE2 baseline. A known unfixed miscompile (FIXME in pochivm/cast_expr_fastinterp.cpp, commit 591c506) emits int/float reinterpret_cast as a no-op, unused by the TPC-H queries, whose correctness tests do check the copy-and-patch output. Linux x86-64 only, LLVM 10 Docker build, open build issue #4.

## Caveats and trade-offs

Numbers are from the authors' peer-reviewed OOPSLA 2021 paper (Xu and Kjolstad, 'Copy-and-Patch Compilation'), not an independent run; the README itself has no numbers. Generated code beats only LLVM -O0 and is 22%-25% slower than -O1..-O3; the win is compile latency. The query compiler is a 600-line prototype with hand-coded plans for only 8 TPC-H queries (no SQL parser or planner). The stencil library takes 14 minutes on 6 threads to build at install time and uses 17.5 MB at runtime. The repo has no LICENSE file; the Apache-2.0 WITH LLVM-exception grant is stated only in the README, alongside a non-binding request not to use it for harmful projects. Abandoned research prototype (last commit 2021-09-09, a July 2021 commit adds a FIXME for a known, unfixed bug). The WebAssembly numbers in the same paper belong to WasmNow (already catalogued). Baseline is not one of PyPy, LuaJIT, V8, HotSpot.

Generated code is written through a C-like C++ API; research prototype, last touched 2021.

## Maintenance

Abandoned research prototype (last commit 2021-09-09, open 2024 build-failure issue). The Apache-2.0 WITH LLVM-exception grant is stated only in the README (no LICENSE file), so treat it as reference code or a fork starting point, not a maintained dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A: the peer-reviewed OOPSLA 2021 paper (PDF reached via the author's fredrikbk.github.io repo) names PochiVM as the system measured, states the CPU (Intel i7-7700HQ), compiler and flags (Clang++ 10 -O3 -DNDEBUG, LLVM 10.0.0), and the public harness is in the repo (test_mini_db_backend_unit_test.cpp PaperBenchmark.TpchQuery1/3/5/6/10/12/14/19 and test_paper_microbenchmarks.cpp, both timing copy-and-patch against LLVM -O0..-O3 and the interpreter). The debug-build cap does not apply: the metric is code-generation time, where LLVM -O0 is LLVM's fastest mode, and the paper also reports the -O1..-O3 comparison.
- **Verifier notes:** Paper PDF reached at raw.githubusercontent.com/fredrikbk/fredrikbk.github.io/master/publications/copy-and-patch.pdf (also usable for a WasmNow retier: same paper, same i7-7700HQ). Record upgraded C to A with full methodology. Shortcomings: generated code slower than LLVM -O1+, prototype query compiler with 8 hand-planned TPC-H queries, no LICENSE file (README grant only), abandoned since 2021.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/README.md>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/LICENSE>
  - <https://github.com/sillycross/PochiVM>
  - <https://github.com/sillycross/PochiVM/commits>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/test_paper_microbenchmarks.cpp>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/test_mini_db_backend_unit_test.cpp>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fredrikbk/fredrikbk.github.io/master/publications/copy-and-patch.pdf>
- **Sources the enricher read:**
  - <https://github.com/sillycross/PochiVM>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/README.md>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/test_mini_db_backend_unit_test.cpp>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/test_paper_microbenchmarks.cpp>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/test_util_helper.h>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/pochivm-build>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/dockerfile/Dockerfile>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/pochivm/pochivm_context.h>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/pochivm/cast_expr_fastinterp.cpp>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/sphinx/index.rst>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/sphinx/intro.rst>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/sphinx/jit_compile.rst>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/sphinx/build_and_test.rst>
  - <https://raw.githubusercontent.com/sillycross/PochiVM/master/sphinx/use_pochivm.rst>
  - <https://github.com/sillycross/PochiVM/issues?q=is%3Aissue>
  - <https://github.com/sillycross/PochiVM/issues/4>
  - <https://github.com/sillycross/PochiVM/commits/master>
  - <https://github.com/sillycross/PochiVM/commit/591c5067a31474cb3c3fec260b7f83212fcbdf15>
  - <https://raw.githubusercontent.com/fredrikbk/fredrikbk.github.io/master/publications/copy-and-patch.pdf>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/sillycross/pochivm`) · [data/wave12/enrich/raw/github_com_sillycross_pochivm.json](../../../data/wave12/enrich/raw/github_com_sillycross_pochivm.json) (enrichment confidence 0.7)

</details>
