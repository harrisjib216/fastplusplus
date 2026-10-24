# Hands-On Design Patterns with C++ 2nd ed: type-erased ScopeGuard with a fixed inline buffer (chapter 11)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Utilities](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book example: type-erased scope guard with a 16-byte inline buffer, under 1 ns faster than a std::function guard.

| | |
|---|---|
| **Beats** | ScopeGuard holding its cleanup in a std::function&lt;void()&gt; |
| **Claimed result** | Book (relayed via the seed lead from the book; no numbers anywhere in the repo): buffer-based guard 5.48 ns against 6.29 ns for the std::function guard in the null-pointer case (rand() call, pointer stays null; BM_nodelete_\* rows by the book's description), and 12.7 ns against 13.4 ns when always allocating (BM_delete_\* rows); explicit delete 4.48 and 4.54 ns. About 1.15x and 1.06x, i.e. 0.8 and 0.7 ns saved per guard (derived from the relayed numbers). |
| **Workload** | Google Benchmark of a scope guard that deletes a pointer: ScopeGuardTypeErasedFast (16-byte alignas(8) inline buffer plus a function-pointer invoker) against a guard holding a std::function&lt;void()&gt;, the template ScopeGuard and a hand-written explicit delete, in four cases: noop (guard on a null pointer created outside the loop), nodelete (rand() call, pointer stays null), nodelete2 (two pointers, 16-byte capture) and delete (rand() call plus new int and delete every iteration). All guards capture by reference ([&]). |
| **Metric** | latency |
| **Compiler and flags** | Not stated. No build line in the opened source file and the README lists no flags. |
| **Adoption** | 137 stars; Packt companion repository of the book Hands-On Design Patterns with C++, 2nd ed. (2023) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition) · [benchmark](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter11/11_scopeguard_te_benchmark.C) |

## Verdict

Reported by the book and relayed by the seed lead, not present in the repo: with a rand() call and a pointer that stays null, the buffer guard took 5.48 ns against 6.29 ns for the std::function guard (about 1.15x); with new and delete every iteration, 12.7 ns against 13.4 ns (about 1.06x); explicit delete measured 4.48 and 4.54 ns. Compiler, flags, standard library, Google Benchmark version and CPU are not stated; the repo holds only the benchmark source, which matches that description.

## Use it when

- You need one guard type that does not depend on the lambda type (a class member, an array of guards, a non-template function signature) and the cleanup lambdas capture by reference or capture a few pointers (at most 16 bytes by default).
- Cleanup paths so hot that 0.7 to 0.8 ns per guard matters, for example a guard created on every iteration of a tight loop.
- As a template for writing your own small-buffer type-erased callable when std::function's manager and empty-check overhead shows up in a profile, after fixing the commit flag.

## Skip it when

- When the guard type need not be erased: the template guard in the same file (sibling entry) is faster again (4.50 and 4.56 ns relayed, matching explicit delete) and has working commit() and move.
- Copying the code as is: commit() does not cancel the cleanup and a moved-from guard still fires, so the cleanup can run twice (see gotchas).
- Callables larger than S bytes, capturing non-trivially-copyable or non-trivially-destructible objects (std::string, std::shared_ptr, std::vector by value), or passed as lvalues: these fail to compile, with no heap fallback.
- When the saving matters less than code you can trust: the gain is 6 to 15 percent (under 1 ns per guard) from one unstated compiler, standard library and CPU.

## How it is fast

Small-buffer type erasure with a single function-pointer thunk: the constructor placement-news the callable into the inline buffer and stores invoke&lt;Callable&gt;, a static function that casts the buffer back and calls it. Compared with std::function there is no manager function to call on destruction, no empty check that can throw bad_function_call, and no heap fallback path, so destruction is one test of the commit flag plus one indirect call. Because the benchmarked [&] lambdas already fit std::function's small-object storage, the gap measured is only that extra indirection, not an allocation.

## Compared with alternatives

Against the template ScopeGuard from the same chapter, pick this only when the guard's type must not depend on the lambda; otherwise the template guard is faster and correct. The other catalogued utilities (micron.cpp memory routines, netbsd-curses, FunctionalPlus keep_if) solve unrelated problems.

## Integration

| | |
|---|---|
| **Form** | source-drop (class inside a single Google Benchmark .C file) |
| **Dependencies** | none for the guard (standard library only); the benchmark needs Google Benchmark (version not stated); the file includes only &lt;functional&gt; and benchmark.h and relies on transitive includes for std::exchange, the type traits, placement new and rand(); no build files in Chapter11 or at the repo root |
| **Minimum toolchain** | C++17 (std::is_trivially_destructible_v and is_trivially_copyable_v, static_assert without a message); README lists GCC, Clang or Visual Studio |
| **Platforms** | any |
| **Thread safety** | not documented; a guard is a scope-local object with no shared state |
| **Drop-in for the baseline** | partial — same construct-from-lambda and commit() interface as the std::function guard, but only for rvalue callables that are trivially copyable, trivially destructible and at most S bytes, and commit() and move are broken as written |

## Gotchas

- ScopeGuardTypeErasedFast::ScopeGuard declares its own 'mutable bool commit_ = false' that hides CommitFlag::commit_. commit() sets the base flag but the destructor tests the derived one, so commit() never cancels the cleanup. The defaulted move constructor marks only the base flag of the source as committed and copies the derived flag as false, so the moved-from guard and the new guard both run the cleanup (double delete). Delete the derived member before using it; the benchmark never calls commit() or moves a guard, so its timings do not reveal the bug.
- The buffer is alignas(8) and the static_asserts check size, trivial copyability and trivial destructibility but not alignment, so a 16-byte callable that captures an over-aligned value (alignas(16) data, SIMD types) is constructed misaligned, which is undefined behaviour.
- The guard is constructed with invoke&lt;Callable&gt; where Callable is the forwarding-reference parameter, so passing a named lambda (an lvalue) makes Callable a reference type and fails the trivially-copyable static_assert; pass std::move(lambda) or a temporary.
- Harness: every nodelete and delete row includes a rand() call (and new plus delete in the delete rows) inside the timed loop, so the guard's cost is a 0.7 to 0.8 ns difference on top of 4.5 to 13 ns of fixed work, with no repetitions or error bars in the repo.

## Known shortcomings

- Book numbers only (about 0.8 and 0.7 ns saved, derived from page data). commit_ is shadowed; the defaulted move leaves the moved-from guard firing (double cleanup); accepts only trivially copyable callables up to 16 bytes and an lvalue callable fails to compile. Neither guard allocates ([&] fits std::function's small buffer), and the template guard (4.50/4.56 ns) beats this one.
- Enricher: shadowed commit_ means commit() never disarms the guard and a moved-from guard runs the cleanup again (confirmed); no alignment check for over-aligned captures; gain only 0.7-0.8 ns.

## Caveats and trade-offs

Marginal gain (6 to 15%, under 1 ns per guard). By reading the source (not compiled or run here), ScopeGuardTypeErasedFast declares its own 'mutable bool commit_' that shadows CommitFlag::commit_, so commit() (which sets the base flag) does not suppress the cleanup, and the defaulted move constructor copies the derived flag as false, so a moved-from guard still fires (the cleanup would run twice): the fast guard is not behaviourally equivalent to the std::function guard, and the benchmark never calls commit() or moves a guard, so the timing does not show it. Narrower than the baseline: static_asserts that the callable is trivially copyable, trivially destructible and at most 16 bytes, has no heap fallback, and an lvalue callable fails to compile because Callable deduces to a reference type. The benchmarked [&] lambdas (8 or 16 bytes, trivially copyable) also fit std::function's small-object storage in libstdc++ and libc++, so neither guard allocates and the gap is std::function's extra manager and invoker indirection only. The template ScopeGuard (separate entry) beats this guard in both cases (4.50 and 4.56 ns relayed), so the buffer guard only matters where type erasure is needed. Baseline is the book's own std::function guard, not a library guard. Compiler, flags, standard library and CPU not stated, first-party, teaching code rather than a packaged library. Tier C. File opened: Chapter11/11_scopeguard_te_benchmark.C. [retier] Enricher: bugs confirmed from source and by a reduced build: ScopeGuardTypeErasedFast redeclares mutable bool commit_, shadowing the base flag, so commit() never disarms the guard and a moved-from guard still runs the cleanup (twice in total). The alignas(8) buffer has no alignof static_assert, so an over-aligned capture is undefined behaviour; an lvalue callable fails the static_assert; the file relies on transitive includes. rand() plus new/delete dominate the timed loop; the gain is only 0.7-0.8 ns.

Accepts only trivially copyable and trivially destructible callables up to 16 bytes (static_assert); no heap fallback.

## Maintenance

Stale publisher companion repo (last commit 2024-08-29, a README errata update; no code changes since mid-2023), MIT-licensed and small enough to copy, but the guard is teaching code with a broken commit()/move that must be fixed first; no issue in the tracker reports it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter11/11_scopeguard_te_benchmark.C is public Google Benchmark code that times ScopeGuardTypeErasedFast against the std::function guard (ScopeGuardTypeErased), the template guard and explicit delete, but the file has no comments or results and the repo carries no build line, flags or CPU; the ns figures exist only in the book (first-party), so C.
- **Verifier notes:** Code matches the record; the shadowed commit_ and broken move are confirmed by reading the source. Added the narrower-callable and no-allocation-on-either-side caveats and named the benchmark rows. Metadata confirmed on github.com: MIT (LICENSE: Copyright (c) 2022 Packt), 137 stars, not fork or archived, last commit 2024-08-29 'Update README.md with errata' (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-84 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter11/11_scopeguard_te_benchmark.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter11/11_scopeguard_te_benchmark.C>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter11>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter11>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter11/11_scopeguard_te_benchmark.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-hands-on-design-patterns-with-cpp-second-edition-inline-buffer-scopeguard`) · [data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_inline_buffer_scopeguard.json](../../../data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_inline_buffer_scopeguard.json) (enrichment confidence 0.5)

</details>
