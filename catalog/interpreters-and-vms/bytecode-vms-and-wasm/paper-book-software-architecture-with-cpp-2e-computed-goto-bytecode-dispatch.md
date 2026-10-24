# Software Architecture with C++ 2E: computed-goto bytecode dispatch versus a single switch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Book sample: computed-goto (labels-as-values) dispatch for a toy 7-opcode VM, reported about 1.29x faster than a switch loop.

| | |
|---|---|
| **Beats** | switch-based bytecode interpreter loop (single large switch in a while loop, same repo) |
| **Claimed result** | Directional only. The book's sample run (relayed via seed lead, not on a repo page) shows about 1.41 ns versus 1.82 ns per call, about 1.29x (derived from the relayed numbers), but the timed workload is an unknown, run-dependent prefix of about 7 opcodes, so the figure measures call overhead and a missing bounds check as much as dispatch. |
| **Workload** | Catch2 BENCHMARK_ADVANCED of two seven-opcode toy stack-less VMs (HALT, INC, DEC, MUL2, DIV2, REM2, NEG on one int64 accumulator), switch_vm::bytecode_interpreter against computed_goto_vm::bytecode_interpreter (GCC labels-as-values), both run on the same randomly generated array of 2^24 opcodes. |
| **Metric** | latency |
| **Hardware** | Not stated for this benchmark. |
| **Compiler and flags** | Repo: optimization_2 target is built only when not MSVC, with cxx_std_23, Catch2 3.12.0, Chapter13 Conan profile GCC 15 gnu20 libstdc++11 and a CMake Release build (CMake default flags, normally -O3 -DNDEBUG on GCC, not spelled out). The compiler and flags of the book's run are not stated. |
| **Adoption** | 74 stars, 22 forks; Packt companion repository of the book Software Architecture with C++, 2nd ed. |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E) · [benchmark](https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/blob/main/Chapter13/optimization/main_2.cpp) |

## Verdict

The book reports (relayed by the seed lead, not on any repo page) a mean of about 1.41 ns per call for the computed-goto VM against 1.82 ns for the switch VM, about 1.29x faster (derived from the relayed numbers), with compiler, flags and CPU unstated; the repo's recipe would be GCC 15, C++23, CMake Release and Catch2 3.12.0. Because the program halts after a few random opcodes, this measures a short, cached, perfectly predictable call, not sustained dispatch throughput.

## Use it when

- Writing your own bytecode interpreter in C or C++ built with GCC or Clang, where per-opcode work is a few instructions and dispatch dominates the loop.
- Bytecode that is produced or validated by your own compiler or loader, so every opcode is known to index inside the dispatch table.
- As a minimal, copyable template for measuring switch against computed-goto dispatch on your own CPU and real programs before committing to either.
- Hot interpreters for long, varied instruction streams on Linux or macOS toolchains, the case the per-handler jump is meant to help (this sample does not measure that case).

## Skip it when

- MSVC builds: labels as values is a GNU extension, and the repo's CMake skips the optimization_2 target when MSVC is the compiler.
- Untrusted or unvalidated bytecode: the computed-goto version indexes its 7-entry table with no bounds check, so an opcode of 7 or more jumps through an out-of-range pointer (undefined behaviour), where the switch version returns through its default case.
- Code that must be portable standard C++, or where a switch already compiles to a jump table and per-opcode handlers are large enough that dispatch cost is noise.
- As evidence of how much computed goto gains: the timed workload is a handful of opcodes, not a 2^24-instruction program, and the book's numbers cannot be reproduced.
- When you need a production VM: the sibling runtimes (wasm3, Wasmi, WAMR fast interpreter) ship tuned dispatch, validation and tooling that this sample does not have.

## How it is fast

Computed goto (GCC/Clang labels as values, the dispatch scheme often called threaded code) ends every handler with its own `goto *dispatch[opcode]`, so each opcode has a separate indirect jump that the branch predictor can track, where the switch funnels every opcode through one shared jump at the loop head. It also drops the switch's range check (the default case the compiler must keep because an enum class can hold any int) and the jump back to the top of the loop. In this harness the predictor advantage hardly applies: each timed call executes only a short, fixed prefix of the program that the predictor learns for both versions, so the reported gap mostly reflects the removed range check and loop structure.

## Compared with alternatives

The siblings are complete runtimes (wasm3, Wasmi, WAMR fast interpreter, Silverfir-nano) that already use tuned dispatch; pick this roughly 100-line sample only when you are writing a small interpreter yourself and want the bare computed-goto pattern. The same book's musttail sample is a recursion example, not a dispatch loop, so it does not cover tail-call dispatch.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the technique; the benchmark uses Catch2 3.12.0 via Conan 2 and CMake 3.28 |
| **Minimum toolchain** | GCC or Clang (labels as values); the target is compiled as C++23 because it uses std::to_underlying; the chapter README lists GCC 15 or Clang 20 |
| **Platforms** | any target GCC or Clang supports; not MSVC |
| **Thread safety** | not documented; from the source, both interpreters only read the bytecode array and the static dispatch table is never written, so concurrent calls on separate accumulators do not share mutable state |
| **Drop-in for the baseline** | partial — same function signature as the switch interpreter, but it needs a GCC/Clang extension and pre-validated opcodes |

## Gotchas

- Early-HALT harness defect: opcodes are drawn uniformly from 0 to 6 and OP_HALT is 0, so each slot is HALT with probability 1/7 and both interpreters stop at the first one; a timed call runs about 7 opcodes on average (geometric), the same prefix every iteration, not the 2^24-opcode array the setup suggests.
- The generator is seeded from std::random_device, so the executed prefix (and its length, which can be a single HALT) changes from run to run; two runs of the same binary can differ by more than the switch-versus-goto gap, and the book's exact workload cannot be recreated.
- The relayed timings, about 1.41 ns versus 1.82 ns per call, are only a few clock cycles, so call overhead and the switch's range check weigh as much as dispatch itself.
- Removing the bounds check is part of the speedup: add a validation pass over the bytecode at load time, or the computed-goto path turns a bad opcode into a wild jump.

## Known shortcomings

- Harness defect: opcode 0 is HALT and opcodes are drawn uniformly from 7, so each timed call runs about 7 opcodes, not the 2^24 program; the book's 1.41/1.82 ns figures are a few cycles per call; random_device seeding makes the run unreproducible; the switch keeps a range check the computed-goto path lacks; book numbers first-party, no CPU or flags in the repo.
- Retiered C to D by enrichment: no valid measurement. Both interpreters stop at the first HALT (about 7 opcodes per timed call), the random_device seed makes the book's run unreproducible and its executed prefix unknown, and part of the gap is the switch's range check that computed goto drops (a bad opcode is undefined behaviour).

## Caveats and trade-offs

The printed numbers are the book's own sample run, relayed through the seed lead; they are not on any repo page (the repo carries the benchmark source only, no result files), so they could not be checked against a page. Harness defect visible in the source: opcodes are drawn uniformly from 0 to OP_SENTINEL (6) and OP_HALT is 0, so each of the 2^24 slots is HALT with probability 1/7 and both interpreters return at the first HALT. A timed call therefore runs only a short prefix of the array (about 7 opcodes on average, geometric), the same prefix on every iteration, fully cached and learnable by the branch predictor; it does not exercise a long random dispatch stream as the 2^24 size suggests. The reported 1.41 and 1.82 ns per call amount to only a few clock cycles, consistent with a handful of opcodes, so call overhead and the per-dispatch bounds check weigh heavily in the gap. The prefix also changes between runs because the generator is seeded from std::random_device, so the book's exact workload cannot be reproduced. The switch version carries a default-case range check (needed because enum class op_code can hold any int) that the computed-goto version lacks, so part of the gap is the missing bounds check (a real but documented property of computed-goto dispatch). Computed goto is a GCC/Clang extension; the target is skipped on MSVC. Tier C: first-party book run, compiler, flags and CPU unstated. Only one program per VM, no real bytecode workload, no comparison with a real interpreter such as CPython. The book also notes CPython moved from switch to computed goto in 2008 and to a tail-call interpreter in 2025 (per the lead; not opened). Repo files opened: Chapter13/optimization/main_2.cpp and CMakeLists.txt, Chapter13/conanfile.py, CMakeLists.txt and README.md. [retier] Enricher: std::random_device seeding means the book's run cannot be reproduced; two runs of the same binary can differ by more than the switch-versus-goto gap. The relayed timings are a few clock cycles, so call overhead and the switch's range check weigh as much as dispatch itself; computed goto drops that check, so a bad opcode jumps out of the table (undefined behaviour). The target is skipped on MSVC. To measure dispatch, build a long HALT-free stream and validate opcodes at load time.

Computed goto is a GCC/Clang extension (labels as values), not standard C++, and is excluded from the MSVC build; the dispatch table has no opcode bounds check, so an invalid opcode is undefined behaviour while the switch version has a default case. Per-opcode replicated indirect jumps help branch prediction on real programs.

## Maintenance

Active book companion repo (MIT, 74 stars, last commit 2026-09-27, recent commits are README edits); the sample is short and copyable but is teaching code, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now D.
- **Tier reason:** Chapter13/optimization/main_2.cpp benchmarks switch_vm against computed_goto_vm with Catch2 BENCHMARK_ADVANCED on the same bytecode array, but the repo holds code only; the 1.41 versus 1.82 ns figures are the book's own run (relayed by the lead), with compiler, flags and CPU unstated, so first-party tier C.
- **Retiered** C to D: C to D: no valid measurement. Both interpreters stop at the first HALT (about 7 opcodes per timed call), the bytecode is seeded from std::random_device so the book's executed prefix is unknown and could be a single HALT, and part of the gap is the switch's range check that computed goto drops; the relayed 1.29x has no defined workload.
- **Verifier notes:** Source matches the record (7 opcodes, OP_HALT = 0, uniform 0..6, 2^24 array, last slot HALT, Catch2 3.12.0, cxx_std_23, non-MSVC only). Early-HALT harness defect confirmed; caveats strengthened (few-cycle timings, unreproducible random prefix). Metadata confirmed: MIT, 74 stars, 22 forks, not a fork, last commit 2026-09-27.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-101 (book seed pass, 2026-10-24); enrichment (wave 12 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/conanfile.py>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/README.md>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/blob/main/Chapter13/optimization/main_2.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/main_2.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/conanfile.py>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/optimization/main_2.cpp>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `paper:book-software-architecture-with-cpp-2e-computed-goto-bytecode-dispatch`) · [data/wave12/enrich/raw/paper_book_software_architecture_with_cpp_2e_computed_goto_bytecode_dispatch.json](../../../data/wave12/enrich/raw/paper_book_software_architecture_with_cpp_2e_computed_goto_bytecode_dispatch.json) (enrichment confidence 0.75)

</details>
