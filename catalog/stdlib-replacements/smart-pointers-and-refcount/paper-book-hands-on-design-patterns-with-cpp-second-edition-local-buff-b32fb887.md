# Hands-On Design Patterns with C++ 2nd ed: local-buffer type-erased Function

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> About 60-line std::function-style wrapper for trivially copyable callables of up to 16 bytes; the book reports cheaper calls than std::function.

| | |
|---|---|
| **Beats** | std::function&lt;int(int,int,int,int)&gt; |
| **Claimed result** | Book (relayed via the seed lead from the book, not shown on any repo page I opened): about 0.884 ns per call for Function against 1.33 ns for std::function; a direct lambda call takes 0.219 ns. About 1.5x (derived from the relayed numbers). |
| **Workload** | Google Benchmark of invoking a callable with four int arguments: the book's Function class (16-byte inline buffer plus a function-pointer executor; accepts only trivially copyable, trivially destructible callables) against std::function&lt;int(int,int,int,int)&gt; holding the same callable, in three pairs: a noinline free function through an invoke helper (BM_invoke_fast_function / BM_invoke_std_function), a lambda capturing x by reference through the helper (BM_invoke_fast_lambda / BM_invoke_std_lambda) and the same lambda called directly (BM_fast_lambda / BM_std_lambda), with plain lambda, inlined function and virtual-call rows as reference; results kept alive with DoNotOptimize and ClobberMemory. |
| **Metric** | latency |
| **Compiler and flags** | The book's example build line is -g -O3 --std=c++20 with g++-11 or clang++ (relayed via lead); the opened source file has no build line (it needs C++20: it uses a requires clause) and the README lists no flags. |
| **Adoption** | 137 stars; Packt companion repository of the book Hands-On Design Patterns with C++, 2nd ed. (2023) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition) · [benchmark](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter06/09_function.C) |

## Verdict

The book (relayed through the seed lead; no numbers in the repository) reports about 0.884 ns per call for Function against 1.33 ns for std::function&lt;int(int,int,int,int)&gt;, roughly 1.5x, with a direct lambda call at 0.219 ns. These are Google Benchmark rows built with -O3 --std=c++20 using g++-11 or clang++; the CPU, standard library and the exact rows the figures come from are not stated. The repository holds the benchmark source only, in three pairs: a noinline function through an invoke helper, a reference-capturing lambda through the helper, and the same lambda called directly.

## Use it when

- Hot callback slots that hold captureless lambdas, function pointers or lambdas capturing one or two references or pointers (up to 16 bytes, or a larger Size you pick)
- Code that must never heap-allocate for a callable and would rather fail at compile time than fall back to the heap
- Small embedded or latency-sensitive loops where a sub-nanosecond saving per indirect call matters and the wrapper's restrictions are acceptable
- As a readable starting point for writing your own small-buffer callable

## Skip it when

- Callables that capture std::string, std::vector, std::shared_ptr or anything else non-trivially copyable or destructible: static_assert rejects them, and there is no heap fallback
- Move-only callables (use std::move_only_function in C++23, or a sibling such as zoo::Function)
- APIs that need operator bool, target(), target_type(), swap or nullptr assignment: none exist, so an empty Function can only be detected by calling it and catching std::bad_function_call
- When std::function's call cost is not measurable in your profile: the book's gap is under half a nanosecond per call, and std::function is the safer, general tool
- Production code that wants maintenance: it is unmaintained teaching code from a 2023 book's companion repository

## How it is fast

It is a manual vtable reduced to one entry: the constructor stores a pointer to a static executor&lt;Callable&gt; instantiation, and a call jumps through it with the arguments passed by value plus a this pointer. A null-object default executor that throws std::bad_function_call replaces the empty-check branch that libstdc++'s std::function::operator() runs on every call. libstdc++'s invoker type also takes its arguments as _ArgTypes&&, so scalar arguments go through memory, while this executor takes Args... by value. Restricting it to trivially copyable, trivially destructible callables removes the manager function, so copying is a byte copy and destruction does nothing.

## Compared with alternatives

Pick it over stdext::inplace_function (SG14) or zoo::Function only when you want a page of code you fully understand and every callable is trivially copyable and small; inplace_function handles non-trivial callables with the same no-heap guarantee and has published comparisons against std::function, and zoo covers move-only captures. Delegate, SmallFunction and sy_callback publish their own numbers, while this one has numbers only in the book.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the class (the benchmark in the same file needs Google Benchmark) |
| **Minimum toolchain** | C++20 (requires clause and std::same_as); the file uses std::same_as without including &lt;concepts&gt; and relies on a transitive include |
| **Platforms** | any; the default buffer is 2\*sizeof(void\*) with alignof(void\*) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial: same call syntax and copy semantics for trivially copyable callables that fit the buffer, but larger or non-trivial callables fail to compile, and there is no operator bool, target(), swap or nullptr comparison |

## Gotchas

- Closure size grows with the captures (the size of a by-reference capture is implementation-defined), so a lambda that captures several variables can exceed the 16-byte default and trip the static_assert; raise the Size template argument.
- The static_assert messages read 'Use Function for non-trivially-copyable callables', pointing at a more general Function the file does not contain (the Chapter10 variants are separate files).
- libstdc++'s std::function also stores trivially copyable callables of up to 16 bytes inline, so for the benchmarked callables neither side allocates; the gain is in the call path (no empty check, arguments by value), not in avoided allocation.
- Each benchmark builds the wrapper in the same function as its timed loop, so the compiler can see the stored target and may devirtualize part of either wrapper's call. The measured gap depends on the compiler and standard library, and the repo shows no results or assembly.

## Known shortcomings

- Benchmark code is public but the repo has no results, flags or CPU; the ns numbers are the book's. Lambdas capture by reference, not by value. A type-erased callable filed under smart-pointers-and-refcount, a loose category fit. Repo stale (last commit 2024-08-29).
- Enricher: wrapper built next to its timed loop, so devirtualisation is compiler-dependent; gap under 0.5 ns; neither side allocates; category fits poorly.

## Caveats and trade-offs

Narrower than std::function: Function static_asserts that the callable is trivially copyable, trivially destructible and at most 16 bytes, has no heap fallback, no target() and no empty check before the call (a null Function throws through its default executor). The benchmarked lambda captures by reference ([&], an 8-byte capture), which also fits std::function's small-buffer storage, so neither side allocates and the gap is call-path overhead only. First-party book numbers: the repo has no results, build line or CPU, and the file holds several pairs (BM_invoke_fast_function/BM_invoke_std_function, BM_invoke_fast_lambda/BM_invoke_std_lambda, BM_fast_lambda/BM_std_lambda, plus BM_lambda, BM_invoke_lambda, BM_invoke_virtual); which rows the book's 0.884 / 1.33 / 0.219 ns figures come from is not stated in the repo. Teaching example, not a packaged library. Tier C. [retier] Enricher: each wrapper is built in the same function as its timed loop, so the compiler sees the stored target and the amount of devirtualisation depends on the compiler; the gap is under 0.5 ns per call. libstdc++ std::function also stores trivially copyable callables up to 16 bytes inline, so neither side allocates; the gain is in the call path (no empty check per call, arguments by value rather than _ArgTypes&&). Fits smart-pointers-and-refcount poorly.

Function only accepts trivially copyable and trivially destructible callables that fit the inline buffer (two pointers by default, enforced with static_assert), so there is no heap fallback, no move-only callables and no non-trivial captures; storage is a char array accessed through reinterpret_cast; an empty Function throws std::bad_function_call when invoked.

## Maintenance

Stale (last commit 2024-08-29) MIT-licensed book companion code; small enough to copy, but it is a teaching sketch with no tests, and none of the repo's 5 open issues covers Chapter06.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter06/09_function.C is public Google Benchmark code comparing the book's Function (16-byte inline buffer plus function-pointer executor) with std::function on the same callables, but the repo carries no results, compiler, flags or CPU; the ns figures exist only in the book (first-party), so C.
- **Verifier notes:** Code matches the description; record said value-capturing lambda but the lambdas capture by reference ([&]), corrected in workload. Category smart-pointers-and-refcount fits poorly for a std::function replacement; orchestrator may want a category override (callables/utilities). Repo metadata confirmed on github.com: MIT, 137 stars, not fork/archived, last commit 2024-08-29 (stale).
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-83 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter06/09_function.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/09_function.C>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/09_function.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/04_std_function.C>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter06>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter10>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter10/10_local_buffer.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter10/11_local_buffer_vtable.C>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/std_function.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-hands-on-design-patterns-with-cpp-second-edition-local-buffer-function`) · [data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_local_buffer_function.json](../../../data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_local_buffer_function.json) (enrichment confidence 0.6)

</details>
