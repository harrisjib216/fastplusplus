# Hands-On Design Patterns with C++ 2nd ed: template ScopeGuard instead of a std::function-based guard (chapter 11)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Utilities](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book example: a scope guard templated on its cleanup lambda, removing std::function type erasure and its per-guard overhead.

| | |
|---|---|
| **Beats** | ScopeGuard holding its cleanup in a std::function&lt;void()&gt; (the book's type-erased guard) |
| **Claimed result** | Book (relayed via the seed lead from the book, not shown on any repo page I opened): in the null-pointer (nodelete) rows the template guard matches explicit code while the std::function guard costs about 1.7-1.8 ns more, about 1.4x (derived from the relayed numbers). The delete rows (template 4.56 ns, explicit 4.54 ns, std::function 13.4 ns, about 2.9x) are not valid evidence: the compiler elides new/delete in the explicit and template rows but not in the std::function row. |
| **Workload** | Google Benchmark of a scope guard that deletes a pointer: template ScopeGuard (callable stored by value, no type erasure) against a guard holding a std::function&lt;void()&gt;, a local-buffer function-pointer guard (ScopeGuardTypeErasedFast) and a hand-written explicit delete, in four cases: noop (guard on a null pointer created outside the loop), nodelete (rand() call, pointer stays null), nodelete2 (two pointers) and delete (rand() call plus new int and delete every iteration). |
| **Metric** | latency |
| **Compiler and flags** | Not stated. No build line in the opened source file and the README lists no flags. |
| **Adoption** | 137 stars; Packt companion repository of the book Hands-On Design Patterns with C++, 2nd ed. (2023) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition) · [benchmark](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter11/11_scopeguard_te_benchmark.C) |

## Verdict

The book reports (relayed by the seed lead; the repo holds only the Google Benchmark source) template guard 4.50 ns against 6.29 ns for the std::function guard with explicit code at 4.48 ns when no delete happens, and 4.56 ns against 13.4 ns (explicit 4.54 ns) when an int is allocated and deleted each iteration; compiler, flags and CPU are not stated, and every row except noop includes a rand() call, which is most of the 4.5 ns. Because only the std::function row pays a real new/delete in the delete case, subtracting its own nodelete-to-delete step (7.1 ns) leaves about 1.7 ns of guard overhead, matching the nodelete gap of about 1.8 ns, roughly 1.4x on this rand()-dominated loop (derived from the relayed numbers).

## Use it when

- Rollback or cleanup (delete, close, undo) in functions with several return paths or exceptions, where the cleanup is a short lambda over locals.
- Hot paths that create a guard per call or per iteration, where std::function setup and an indirect call (about 1.8 ns per guard in the book's run, derived from the relayed numbers) show up.
- Local guards that can be declared with auto, which is the normal way scope guards are used.
- C++17 code that also wants success-only or failure-only cleanup: the chapter's ON_SCOPE_SUCCESS and ON_SCOPE_FAILURE macros use the same template approach.

## Skip it when

- Guards that must share one type: stored as a class member, in a container or returned through a non-template interface; that needs type erasure (std::function or the buffer-based sibling).
- When a maintained guard is already available: Boost.ScopeExit, folly::ScopeGuard and std::experimental::scope_exit use the same template design.
- Cleanup code that can throw: the destructor is implicitly noexcept, so a throwing cleanup calls std::terminate.
- Expecting the book's 2.9x delete-case gain in real code: the clean comparison is about 1.8 ns per guard, negligible next to I/O or allocation in the guarded scope.

## How it is fast

The callable's type is a template parameter and the lambda is stored by value, so the destructor calls it directly and the compiler inlines it: no std::function construction, no manager/invoker function pointers and no indirect call. In a reduced copy compiled to assembly by the enricher (GCC 13.3 and Clang 18, -O2 and -O3), the template-guard loop compiled to the same code as the hand-written explicit delete, while the std::function guard kept an indirect call through its invoker.

## Compared with alternatives

Against the catalogued inline-buffer type-erased guard from the same chapter, this one is as fast as hand-written cleanup, has no size or trivially-copyable limits on the lambda, and does not have that class's commit() bug; take the buffer guard only when one non-template guard type is required (after fixing it). The other catalogued utilities are unrelated.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the guard itself (it needs &lt;utility&gt; for std::exchange, which the file only gets through benchmark/benchmark.h; with &lt;functional&gt; alone GCC 13 libstdc++ rejects std::exchange). The benchmark needs Google Benchmark; there are no build files, and unmerged third-party PR #11 adds a Chapter11 CMakeLists.txt (C++20, benchmark v1.7.1, no build type or flags). |
| **Minimum toolchain** | C++14 (std::exchange); enricher compiled a reduced copy with GCC 13.3 and Clang 18 at -std=c++17. The ON_SCOPE_SUCCESS/FAILURE variants need C++17 (std::uncaught_exceptions). |
| **Platforms** | any |
| **Thread safety** | not documented; a guard is a local object used by one thread, and the captured state's safety is up to the caller |
| **Drop-in for the baseline** | partial — same construct/commit/run-at-exit behaviour, but the guard's type depends on the lambda, so it is declared with auto via MakeGuard and cannot replace the std::function guard where a single named type is needed |

## Gotchas

- Benchmark defect in the delete case: in a reduced copy compiled to assembly (GCC 13.3, Clang 18, -O2/-O3), both compilers removed the new int(42)/delete pair entirely from the explicit and template rows (only the rand() call remains), while the std::function and buffer-guard rows keep operator new and the indirect delete. The 13.4 ns against 4.56 ns (2.9x) row therefore compares a real allocation against none; use the nodelete row.
- MakeGuard with a named (lvalue) lambda does not compile: Callable deduces to a reference, the two constructors collapse to one signature (GCC 13.3: 'cannot be overloaded'; Clang 18: 'multiple overloads of ScopeGuard instantiate to the same signature'). Pass the lambda inline or std::move it.
- The plain guard fires on every exit, success included, until commit() is called (checked on a reduced copy: commit() disarms it); use the chapter's ON_SCOPE_FAILURE variant for failure-only rollback.
- Do not copy the file's ScopeGuardTypeErasedFast class alongside it: it redeclares mutable bool commit_, shadowing the base flag, so commit() never disarms it and a moved-from guard still fires (reduced copy: cleanup ran once after commit(), twice after a move).

## Known shortcomings

- Book numbers only; rand() is called in every iteration. The explicit and template delete rows (4.54, 4.56 ns) equal the nodelete rows, which suggests the compiler removed new/delete there but not in the std::function guard, so the 2.9x is likely overstated; the 1.8 ns nodelete gap is the cleaner figure (inferred, not built).
- Enricher: the 2.9x delete-row figure is invalid (new/delete elided in the explicit and template rows only); the valid nodelete figure is about 1.4x; lvalue lambdas do not compile.

## Caveats and trade-offs

The baseline is the book's own std::function guard, not a library guard (Boost.ScopeExit, folly::ScopeGuard, std::experimental::scope_exit), which are template designs like the winner and were not benchmarked. Each nodelete and delete iteration calls rand(), so the about 4.5 ns explicit and template rows are mostly rand(). Possible harness asymmetry (inferred from the source and the relayed numbers, not measured here): in BM_delete_explicit and BM_delete_template the new int(42) and delete sit in the same inlined scope, so the compiler may elide the allocation pair, which would explain why those rows (4.54 and 4.56 ns) equal the nodelete rows (4.48 and 4.50 ns); the std::function guard calls the delete through type erasure, so its allocation cannot be elided. The 2.9x delete-case ratio may therefore overstate the guard overhead; the nodelete case (6.29 against 4.50 ns, about 1.8 ns of std::function overhead) is the cleaner comparison. Compiler, flags and CPU not stated, first-party. Tier C. [retier] Enricher: assembly of a reduced copy (GCC 13.3, Clang 18, -O2/-O3) shows the explicit and template delete rows drop new/delete entirely while the std::function and buffer-guard rows keep operator new, so the 2.9x delete-row figure compares elided allocation with real allocation and is not valid; the guard's real overhead is the nodelete row, about 1.7-1.8 ns (about 1.4x). MakeGuard on an lvalue lambda does not compile (both constructors collapse to one signature), and with only &lt;functional&gt; GCC 13 rejects std::exchange (the file never includes &lt;utility&gt;).

The guard type depends on the callable's type (use auto or a factory function), so it cannot be stored or returned under one common type without type erasure; code is generated per lambda.

## Maintenance

Stale Packt companion repo (last commit 2024-08-29; CMake PR #11 for Chapter11 unmerged since 2023-01-23), MIT; the guard is about 30 lines, so copy it with an explicit #include &lt;utility&gt;, or use a maintained library guard.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter11/11_scopeguard_te_benchmark.C benchmarks the template ScopeGuard against a std::function-based guard, a function-pointer local-buffer guard and explicit delete, but the repo has no results, compiler, flags or CPU; numbers come only from the book, so C.
- **Verifier notes:** Code matches the record; the old caveat assumed the explicit-delete row contains a real new/delete pair, but it equals the nodelete row within 0.06 ns, which points to allocation elision on the explicit and template sides only; enricher should check this with a build or compiler-explorer reasoning. Metadata confirmed: MIT, 137 stars, last commit 2024-08-29 (stale).
- **Fields the verifier corrected:** `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-83 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter11/11_scopeguard_te_benchmark.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter11/11_scopeguard_te_benchmark.C>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/Chapter11/11_scopeguard_te_benchmark.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/Chapter11/07b_scopeguard_lambda_cpp17.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/Chapter11/08_scopeguard_on_exit.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/Chapter11/10a_scopeguard_on_fail_cpp17.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/README.md>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter11>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/pulls>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/pull/11/files>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-hands-on-design-patterns-with-cpp-second-edition-template-scopeguard`) · [data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_template_scopeguard.json](../../../data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_template_scopeguard.json) (enrichment confidence 0.75)

</details>
