# ClangJIT (Clang with JIT extensions for C++ templates)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🔴 abandoned

> Research Clang 9 fork adding [[clang::jit]]: templates instantiated at run time; beats dynamic-size Eigen, ties size-specialized AoT.

| | |
|---|---|
| **Beats** | The same Eigen expression (m = Ones + 0.00005\*(m + m\*m)) compiled ahead of time with runtime-sized Matrix&lt;T,Dynamic,Dynamic&gt; and float/double/long double dispatch, by the same Clang at -march=native -ffast-math -O3; the wiki also reports an AoT build specialized for one fixed size, which matches the JIT. |
| **Claimed result** | Runtime, double, 40,000,000 repeats, times reported by the code (JIT compile time excluded): size 3 JIT 1.0 s vs AoT dynamic-size 8.05 s vs AoT single fixed-size specialization 1.01 s; size 7 JIT 8.34 s vs AoT 20 s vs single specialization 8.45 s; size 16 JIT 35.3 s vs AoT 36.2 s vs single specialization 35.1 s (about 8x, 2.4x and 1.03x over dynamic-size AoT and parity with size-specialized AoT, derived from page data). Compile time (user): JIT only 3.5 s vs AoT double only 5.3 s and AoT float/double/long double with dispatch 9.7 s; one fixed-size specialization 2.95-4.95 s; includes and main only 2.58 s. |
| **Workload** | Eigen bench/benchmark.cpp adapted: 40,000,000 repeats of small dense matrix operations; AoT runtime-sized matrices versus JIT-instantiated fixed-size matrices for sizes 3, 7 and 16, JIT compile time excluded from the runtime rows. |
| **Metric** | throughput |
| **Hardware** | Xeon E5-2699 (exact variant not stated) |
| **Compiler and flags** | ClangJIT (Clang fork, -fjit, [[clang::jit]] attribute) with -march=native -ffast-math -O3 on both sides per the wiki; the Clang used was built with GCC 8.2.0 in CMake RelWithDebInfo mode. Eigen version, ClangJIT commit and the benchmark's main() are not given. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Runtime values (matrix dimensions) become template arguments instantiated at run time, so the optimizer sees fixed sizes and can unroll and vectorize; only the sizes actually used are compiled (wiki: 'performance benefits of many AoT specializations, sometimes better, at a low compile-time cost'). |
| **Adoption** | 237 stars, 25 forks |
| **Last commit** | 2019-12-30 |
| **Links** | [repository](https://github.com/hfinkel/llvm-project-cxxjit) · [benchmark](https://github.com/hfinkel/llvm-project-cxxjit/wiki) |

## Verdict

Author's wiki benchmark (Eigen loop m = Ones + 0.00005\*(m + m\*m), double, 40,000,000 repeats, -march=native -ffast-math -O3, Intel Xeon E5-2699, JIT compile time excluded): JIT fixed-size code 1.0, 8.34 and 35.3 s for sizes 3, 7 and 16 vs 8.05, 20 and 36.2 s for dynamic-size AoT Eigen and 1.01, 8.45 and 35.1 s for AoT code specialized to that size. Build time with the JIT is 3.5 s vs 9.7 s for AoT float/double/long double with dispatch and 5.3 s for AoT double only.

## Use it when

- Research or prototyping of run-time template specialization in C++, for example reproducing the SC19 P3HPC ClangJIT paper (arXiv 1904.08555).
- Template-heavy numeric kernels (Eigen-style small fixed-size matrices) where the sizes or scalar types are only known at run time and few of the possible combinations are used in any one run.
- Codes where instantiating every size/type combination ahead of time inflates build time: the wiki's build drops from 9.7 s (float/double/long double with dispatch) to 3.5 s.
- Long-running jobs that call the JIT function once and loop inside it, so the one-time compile and the per-call dispatch are amortised.

## Skip it when

- Production code: the fork has had no commits since 2019-12-30, is based on LLVM 9.0, and crash and build reports (#17 UD2 trap with Blaze expression templates, #25 segfault on cxxjit-ni-9.0, #28 'Declaration may not be in a Comdat!' with the wiki's type-string example, #30 '-fjit' unknown) remain open.
- When the sizes or types are few and known: an AoT build specialized to the size ties the JIT (1.01 vs 1.0 s, 8.45 vs 8.34 s, 35.1 vs 35.3 s), so a switch over fixed-size instantiations gets the same speed with a stock compiler.
- Hot call sites that call a JIT template in a tight loop: issue #31 measured about 93 ns per call of an already-compiled empty [[clang::jit]] function.
- Larger matrices: the gain over dynamic-size Eigen falls from about 8x at size 3 to 2.4x at size 7 and 1.03x at size 16.
- Start-up-sensitive or size-sensitive binaries: the program carries its serialized AST and IR and links the Clang/LLVM libraries to compile at run time; compile latency is not reported.

## How it is fast

Runtime specialization: matrix sizes read at run time become template arguments, so Eigen takes its fixed-size path, where the optimizer sees constant trip counts and can fully unroll and vectorize. The compiler embeds a serialized AST of the translation unit, its IR and the original command line in the binary; on the first call the runtime (__clang_jit in clang/lib/CodeGen/JIT.cpp) reads the AST with ASTReader, instantiates the template through Sema, generates code with the stored -O3 options, links the program's IR as available_externally for inlining and loads the result with LLVM ORC. Later calls hit a hash-table cache keyed by the template key, the non-type argument bytes and the type strings.

## Compared with alternatives

Most siblings are managed-runtime JITs (HotSpot, .NET, Bun, LuaJIT) beating C or C++ programs; ClangJIT is C++ specialized at run time and only beats generic C++ code. Proteus (llnl/proteus) is the closer alternative: it specializes host, CUDA and HIP code on runtime values through a Clang pass plugin or compiler-independent frontends on LLVM 19-22 without a forked compiler, so pick ClangJIT only to study [[clang::jit]]'s template-level semantics (runtime non-type and type-string template arguments) or the SC19 paper.

## Integration

| | |
|---|---|
| **Form** | source-drop — build the whole LLVM/Clang fork (wiki CMake recipe with LLVM_ENABLE_PROJECTS=llvm;clang;openmp) and compile and link with its clang++ -fjit |
| **Dependencies** | the forked Clang/LLVM 9.0 toolchain and its libraries at run time; CUDA runtime (-lcudart) for the device-code JIT path present in the source |
| **Minimum toolchain** | the fork's own clang++ (LLVM 9.0.0 base); the wiki's Clang was built with GCC 8.2.0 in RelWithDebInfo mode |
| **Platforms** | Linux documented (benchmarked on an Intel Xeon E5-2699); Windows and Visual Studio support asked about in open issues #21 and #22 with no documented answer; source contains a CUDA device JIT path that the wiki does not document |
| **Thread safety** | Not documented on the wiki. The runtime guards the instantiation cache with a global mutex and serializes all compilation under a second global mutex (clang/lib/CodeGen/JIT.cpp), so concurrent calls are safe but contend. |
| **Drop-in for the baseline** | partial — the C++ source changes only by adding [[clang::jit]] and passing runtime template arguments, but it needs the forked compiler; stock compilers reject runtime template arguments. |

## Gotchas

- Harness gap: the runtime rows exclude JIT compilation time and the wiki never reports it, so the end-to-end cost (AST deserialization, Sema instantiation and -O3 codegen on the first call) is unknown; the benchmark also calls the JIT function once with the loop inside, which hides the about 93 ns per-call dispatch (global mutex plus hashing of the argument bytes and type strings in __clang_jit) that issue #31 measured.
- The win is over Eigen's dynamic-size path, not over AoT code quality: AoT built for the same fixed size matches the JIT within 1-2 percent at every size, and at size 16 the JIT is slightly slower (35.3 vs 35.1 s).
- The benchmark never uses m after the timed loop (no output or checksum), is a single run timed with system_clock, and its main(), the Eigen version and the ClangJIT commit are not published, so it cannot be rerun exactly.
- Language restrictions: decltype(auto) and other body-dependent deduction are unavailable on JIT templates, explicit specializations are not JIT-compiled, a runtime pointer argument creates one instantiation per pointer value, and type strings are parsed in the declaring context with unspecified visibility of later-declared types.

## Known shortcomings

- The wiki's own size-specialised ahead-of-time build ties the JIT (1.01/8.45/35.1 vs 1.0/8.34/35.3 s), so the 8x win holds only against dynamic-size Eigen; first-party, no main(), Eigen version or exact Xeon E5-2699 v3/v4 stated; arXiv 1904.08555 blocked. Abandoned 2019-12-30.
- Harness gaps: JIT compile time is excluded and never reported; issue #31 measured about 93 ns of dispatch per call of a cached JIT function (a global mutex plus argument hashing in __clang_jit, clang/lib/CodeGen/JIT.cpp), which the benchmark hides by calling once with the loop inside; the result m is never consumed; single run. The AoT size-specialised build ties the JIT at every size. Open crash issues #17, #25, #28; LLVM 9.0 base.

## Caveats and trade-offs

The run-time win is over Eigen's dynamic-size code path; the wiki's 'single specialization' AoT rows (1.01 s, 8.45 s, 35.1 s) equal the JIT rows, so JIT code is no faster than AoT C++ -O3 code that knows the size; the real advantage is lower compile time than instantiating many sizes or types ahead of time. JIT compile time is excluded from the runtime rows. First-party wiki, single runs without variance, CPU generation of the Xeon E5-2699 not stated, Eigen version not stated, main() omitted from the listings. The SC19 P3HPC paper (arXiv 1904.08555) was not reachable (arxiv.org, open-std.org P1609R0 and deepai blocked), so only the wiki was checked. Clang fork, last commit 2019-12-30. It is C++ with a JIT extension rather than another language, so it could also sit beside Easy::jit in wave 12 jits. [retier] JIT compile time is excluded and never reported; issue #31 measured about 93 ns of dispatch per call of a cached JIT function (global mutex plus argument hashing), hidden by calling once with the loop inside; the result is never consumed; single run; the AoT size-specialised build ties the JIT at every size. Open crash issues #17, #25, #28; LLVM 9.0 base.

Needs a custom Clang/LLVM fork (not upstream); the program links the compiler infrastructure and compiles templates at run time (JIT start-up cost, memory, requires source or serialized AST available at run time); restrictions on decltype(auto), explicit specializations and pointer arguments listed on the wiki; the WG21 proposal P1609 for [[jit]] has not been adopted.

## Maintenance

Abandoned research prototype (cxxjit branch last updated 2019-12-30, cxxjit-ni-9.0 2020-01-16, LLVM 9.0 base, open crash and build issues), Apache-2.0 WITH LLVM-exception; worth reading as a reference design, not as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party wiki by the author with code listings for the timed functions, flags (-march=native -ffast-math -O3) and CPU family, but no main(), Eigen version, ClangJIT commit, CPU generation (E5-2699 v3 or v4) or run count, so not A; the peer-reviewed paper (arXiv 1904.08555, SC19 P3HPC workshop) could not be opened and its snippets give no numbers. The wiki's own size-specialized AoT rows match the JIT, so the win holds only against dynamic-size code.
- **Verifier notes:** Numbers match the wiki exactly; license Apache-2.0 WITH LLVM-exception (llvm/LICENSE.TXT, legacy NCSA appended), 237 stars, 25 forks, last commit 2019-12-30 (abandoned) all check out. Shortcoming: the JIT beats only dynamic-size AoT Eigen; AoT code specialized to the same size ties it (1.01 vs 1.0 s, 8.45 vs 8.34 s, 35.1 vs 35.3 s), win shrinks to 1.03x at size 16, first-party wiki with partial methodology, paper unreachable. Not yet catalogued anywhere (wave 12 leads.md lists it as a lead); related to the wave 12 Easy::jit entry but not a duplicate.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-05 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/hfinkel/llvm-project-cxxjit/wiki>
  - <https://raw.githubusercontent.com/wiki/hfinkel/llvm-project-cxxjit/Home.md>
  - <https://github.com/hfinkel/llvm-project-cxxjit>
  - <https://github.com/hfinkel/llvm-project-cxxjit/commits/cxxjit>
  - <https://raw.githubusercontent.com/hfinkel/llvm-project-cxxjit/cxxjit/llvm/LICENSE.TXT>
  - <https://raw.githubusercontent.com/hfinkel/llvm-project-cxxjit/cxxjit/clang/LICENSE.TXT>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wiki/hfinkel/llvm-project-cxxjit/Home.md>
  - <https://raw.githubusercontent.com/hfinkel/llvm-project-cxxjit/cxxjit/README.md>
  - <https://raw.githubusercontent.com/hfinkel/llvm-project-cxxjit/cxxjit-ni-9.0/README.md>
  - <https://raw.githubusercontent.com/hfinkel/llvm-project-cxxjit/cxxjit/clang/lib/CodeGen/JIT.cpp>
  - <https://raw.githubusercontent.com/hfinkel/llvm-project-cxxjit/cxxjit/clang/lib/Driver/ToolChains/Clang.cpp>
  - <https://raw.githubusercontent.com/hfinkel/llvm-project-cxxjit/cxxjit/llvm/CMakeLists.txt>
  - <https://github.com/hfinkel/llvm-project-cxxjit>
  - <https://github.com/hfinkel/llvm-project-cxxjit/tree/cxxjit/clang/lib>
  - <https://github.com/hfinkel/llvm-project-cxxjit/branches/all>
  - <https://github.com/hfinkel/llvm-project-cxxjit/commits/cxxjit?author=hfinkel>
  - <https://github.com/hfinkel/llvm-project-cxxjit/issues>
  - <https://github.com/hfinkel/llvm-project-cxxjit/issues/31>
  - <https://github.com/hfinkel/llvm-project-cxxjit/issues/17>
  - <https://github.com/hfinkel/llvm-project-cxxjit/issues/28>
  - <https://github.com/llnl/proteus>
  - WebSearch: ClangJIT Finkel Poliakoff Richards (snippets only; arxiv.org/abs/1904.08555 and sc19.supercomputing.org unreachable, ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/hfinkel/llvm-project-cxxjit`) · [data/wave14/enrich/raw/github_com_hfinkel_llvm_project_cxxjit.json](../../../data/wave14/enrich/raw/github_com_hfinkel_llvm_project_cxxjit.json) (enrichment confidence 0.7)

</details>
