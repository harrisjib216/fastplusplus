# Software Architecture with C++ 2E: tail-recursive Fibonacci with musttail versus naive recursion

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Book microbenchmark of musttail tail recursion against loops and plain recursion; shows parity, no speedup from musttail.

| | |
|---|---|
| **Beats** | naive double-recursive Fibonacci (same repo; also iterative Fibonacci as a second reference) |
| **Claimed result** | No speedup attributable to musttail. Book sample run (relayed via seed lead, not on a repo page): factorial 32768 and 65536, iterative, plain-recursive and tail-recursive all about equal (20 to 40 microseconds); Fibonacci(32), tail-recursive about 6.94 ns versus iterative about 6.74 ns (parity, tail-recursive marginally slower). The naive double-recursive Fibonacci(32) at about 2,389,913 ns is an exponential-time algorithm; the about 344,000x ratio against it (derived from the relayed numbers) measures the algorithm change to a linear accumulator, not tail calls. |
| **Workload** | Google Benchmark of iterative, plain-recursive and musttail tail-recursive factorial (n = 32768 and 65536) and Fibonacci (n = 16 to 32, doubling) over uint64_t, with DoNotOptimize on the result. |
| **Metric** | latency |
| **Hardware** | Not stated for this benchmark. |
| **Compiler and flags** | Repo: optimization_1 target, cxx_std_20, Google Benchmark 1.9.4, Chapter13 Conan profile GCC 15 gnu20 libstdc++11 and a CMake Release build (CMake default flags, normally -O3 -DNDEBUG on GCC, not spelled out). The compiler and flags of the book's run are not stated. |
| **Adoption** | 74 stars, 22 forks; Packt companion repository of the book Software Architecture with C++, 2nd ed. |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E) · [benchmark](https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/blob/main/Chapter13/optimization/main_1.cpp) |

## Verdict

No speedup from musttail was measured: the book's own run, relayed by the seed lead and not on any repo page, has iterative, plain-recursive and tail-recursive factorial of 32768 and 65536 all at about 20 to 40 microseconds and tail-recursive Fibonacci(32) at about 6.94 ns against 6.74 ns iterative; naive double-recursive Fibonacci(32) at about 2.39 ms differs only because it is exponential-time. Compiler, flags and hardware for that run are not stated; the repo builds optimization_1 as a C++20 CMake Release target with a GCC 15/libstdc++ Conan profile.

## Use it when

- Deep recursion that must not grow the stack even in Debug or -O0 builds, where the optimizer would not turn the tail call into a jump.
- Tail-call-threaded interpreters or parsers (one handler per opcode that ends by calling the next), where a guaranteed jump keeps state in registers and the stack flat; wasm3 is a catalogued interpreter built in this style.
- You want a compile error rather than silent stack growth when a refactor moves the recursive call out of tail position.
- As a copyable feature-test pattern: test __has_cpp_attribute(clang::musttail), then musttail, else expand to nothing.

## Skip it when

- As a speed optimization for self-recursive functions in optimized builds: every same-algorithm row in this benchmark shows parity with the loop.
- MSVC and GCC before 15: the macro expands to nothing, so the musttail variant is ordinary recursion that depends on the optimizer (MSVC still builds the optimization_1 target).
- Calls whose signature does not match the caller's or that are not in tail position: musttail cannot apply and compilation fails.
- When the cost is algorithmic: naive double-recursive Fibonacci is slow because of its exponential call count, which no call-convention change fixes.

## How it is fast

It is not faster. musttail makes the compiler emit the recursive call as a jump or refuse to compile, so stack use stays constant at any depth; in the book's Release-build run the tail-recursive versions time like the loops (Fibonacci(32) about 6.94 ns versus 6.74 ns), consistent with the optimizer already eliminating these self tail calls. The large Fibonacci gap comes from replacing exponential double recursion with a linear accumulator, an algorithm change. Guaranteed tail calls pay off in interpreter dispatch instead: wasm3's interpreter notes describe operations that end by calling the next one so the compiler tail-call optimizes them and virtual registers map to CPU registers.

## Compared with alternatives

It does not compete with the VM siblings; read it as a primer on guaranteed tail calls, then look at wasm3, whose interpreter is built on operations that tail-call the next one, or at the same repo's computed-goto versus switch dispatch entry, which is the actual interpreter-dispatch measurement in this book's code.

## Integration

| | |
|---|---|
| **Form** | source-drop (a feature-test macro plus an attribute on the return statement) |
| **Dependencies** | none for the technique; the benchmark needs Google Benchmark 1.9.4 via Conan 2 |
| **Minimum toolchain** | A compiler with [[clang::musttail]]: Clang, or GCC 15, whose C-family frontends implement [[clang::musttail]] and [[gnu::musttail]] per a search snippet of the GCC 15.1 release announcement (page not reachable); the target builds as cxx_std_20 with the repo's GCC 15 Conan profile and CMake 3.28 |
| **Platforms** | any target where the compiler can emit the tail call; the attribute is non-standard |
| **Thread safety** | not applicable (pure functions with no shared state) |
| **Drop-in for the baseline** | partial — the one-argument wrappers keep the loop's signature, but inside they are accumulator-passing rewrites, not the naive double recursion they are compared against |

## Gotchas

- Every benchmarked factorial result is 0: n! for n of 66 or more holds at least 64 factors of 2, so the uint64_t product wraps to zero at 32768 and 65536; the timings still measure the multiply chain, but the outputs are meaningless.
- iteration::fibonacci(1) returns 0 because its loop never runs, and tail_recursion::factorial(0) wraps n to 4294967295 and recurses about 4.3 billion times because it stops only at n == 1; neither input is benchmarked.
- The macro is named musttail, so any header included after it that spells [[gnu::musttail]] or __attribute__((musttail)) gets rewritten; use a prefixed name when copying the pattern.
- The harness runs only Release builds and shallow depths (32 calls for Fibonacci, 65536 for factorial), so it never shows musttail's real benefit, bounded stack use where the optimizer would not eliminate the call.

## Known shortcomings

- Not a musttail win: the 344,000x gap compares exponential naive Fibonacci with a linear tail-recursive one; same-algorithm rows show parity (factorial equal, tail-recursive 6.94 vs iterative 6.74 ns); downgraded to D.

## Caveats and trade-offs

The printed numbers are the book's own sample run, relayed through the seed lead; they are not on any repo page (the repo carries the benchmark source only, no result files). The Fibonacci gap is not caused by musttail: the baseline is the exponential-time double recursion while the tail-recursive version is a linear accumulator recursion, so the 2.39 ms versus 6.94 ns gap is an algorithm change, and the tail-recursive version only matches the iterative one (6.94 versus 6.74 ns). The only same-algorithm comparison, factorial, shows the three variants about equal, i.e. no speedup from musttail (an optimizing compiler likely turns the plain accumulator-free factorial recursion into a loop as well). musttail guarantees a jump instead of a call, which matters for stack depth (deep recursion without overflow) rather than speed at these sizes. The musttail macro tests __has_cpp_attribute(clang::musttail) first; GCC 15 implements [[clang::musttail]] (per a WebSearch snippet of the GCC 15.1 release announcement, not opened), so with the repo's GCC 15 Conan profile and with Clang the macro does expand to [[clang::musttail]]; it expands to nothing only on older GCC and MSVC, where the 'musttail' variant is ordinary optimizer-dependent tail recursion. Overflowing uint64_t factorial results are meaningless but harmless to timing; tail_recursion::factorial(0) would not terminate early (checks n == 1 only), irrelevant for the benchmarked n. Category is a best fit only: this is a recursion microbenchmark, not a VM measurement; the technique matters to interpreter design (CPython tail-call interpreter) but nothing here runs a bytecode VM. Tier D: no valid measurement of a speedup from the named technique; the book's run has compiler, flags and CPU unstated. Repo files opened: Chapter13/optimization/main_1.cpp and CMakeLists.txt, Chapter13/conanfile.py, CMakeLists.txt and README.md.

musttail forces a guaranteed tail call (Clang attribute, GCC 15 and later via its own attribute) and fails to compile if the call cannot be a tail call; constant stack use, but the attribute is non-standard and the function signatures must match.

## Maintenance

Active Packt companion repository (last commit 2026-09-27, mostly README edits; CI builds only Chapter10/customer, not this benchmark), MIT-licensed; the macro is small enough to copy but brings no speed in optimized builds.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): downgrade; tier before verification C, tier now D.
- **Tier reason:** Chapter13/optimization/main_1.cpp times iterative, plain-recursive and musttail tail-recursive factorial and Fibonacci, but the only large gap (naive Fibonacci 2.39 ms versus tail-recursive 6.94 ns, book numbers relayed by the lead, not on any page) is exponential versus linear algorithm, not musttail; every same-algorithm comparison (factorial, all three equal; tail-recursive versus iterative Fibonacci, 6.94 versus 6.74 ns) shows parity, so there is no valid measurement of a speedup from the named technique.
- **Verifier notes:** Downgraded to D: claimed 344,000x is exponential versus linear Fibonacci, not musttail; same-algorithm rows show parity. A reject for not-faster would also be defensible; kept as downgrade under the keep-flagged policy. Fixed caveat: GCC 15 accepts [[clang::musttail]], so the macro is not empty on the repo's toolchain.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-101 (book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/conanfile.py>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/README.md>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/blob/main/Chapter13/optimization/main_1.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/main_1.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/issues>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/commits/main>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/tree/main/.github/workflows>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/tree/main/Chapter13/optimization>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/.github/workflows/github-ci.yml>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/conanfile.py>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/main_1.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/main_2.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/README.md>
  - <https://raw.githubusercontent.com/wasm3/wasm3/HEAD/docs/Interpreter.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `paper:book-software-architecture-with-cpp-2e-tail-recursive-fibonacci-musttail`) · [data/wave12/enrich/raw/paper_book_software_architecture_with_cpp_2e_tail_recursive_fibonacci_musttail.json](../../../data/wave12/enrich/raw/paper_book_software_architecture_with_cpp_2e_tail_recursive_fibonacci_musttail.json) (enrichment confidence 0.6)

</details>
