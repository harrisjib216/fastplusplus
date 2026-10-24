# Hands-On Design Patterns with C++ 2nd ed: virtual function call instead of dynamic_cast (chapter 1)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Polymorphic dispatch](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Teaching idiom: replace a dynamic_cast type test with a virtual member call; book example code, not a library.

| | |
|---|---|
| **Beats** | dynamic_cast&lt;Derived\*&gt; on a base-class pointer (type test to select behaviour) |
| **Claimed result** | Book (relayed via the seed lead from the book, not shown on any repo page I opened): about 1 ns for the virtual call against 5 to 10 ns for the dynamic_cast, absolute numbers hardware dependent; about 5x to 10x (derived from the relayed numbers). |
| **Workload** | Google Benchmark, 64 repeated operations per iteration on a one-level Base/Derived hierarchy: p-&gt;f() through a virtual function against dynamic_cast&lt;Derived\*&gt;(p) with the result kept alive by DoNotOptimize. |
| **Metric** | latency |
| **Compiler and flags** | Not stated. The repo has no build files (no CMakeLists.txt or Makefile at the root or in Chapter01) and the README's software table lists only 'GCC, Clang or Visual Studio'. Google Benchmark, version not stated. |
| **Adoption** | 137 stars; Packt companion repository of the book Hands-On Design Patterns with C++, 2nd ed. (2023) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition) · [benchmark](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter01/02_dynamic_cast.C) |

## Verdict

The book, as relayed by the seed lead and not shown anywhere in the repository, reports about 1 ns for the virtual call against 5-10 ns for dynamic_cast&lt;Derived\*&gt; on a one-level hierarchy (about 5-10x, derived), noting that absolute numbers depend on hardware. The repo holds only the Google Benchmark source; compiler, flags, ABI runtime and CPU are not stated, so the result is first-party (tier C) and the virtual row may be inflated by devirtualization.

## Use it when

- You own the class hierarchy and hot code branches on dynamic_cast&lt;Derived\*&gt;(p) != nullptr to pick behaviour: add a virtual hook in the base and call it instead.
- Loops over heterogeneous object collections that type-test every element before processing; the book figures relayed in the record put the virtual call near 1 ns against 5-10 ns for the cast (about 5-10x, derived).
- Code that would like to build with RTTI disabled (-fno-rtti): virtual dispatch needs no RTTI, a downcasting dynamic_cast does.
- Reviewing hot paths: a quick rule of thumb that an RTTI type test costs several virtual calls, before deciding whether CRTP or std::variant is worth the refactor.

## Skip it when

- The base class is not yours (third-party or frozen ABI): dynamic_cast, or a visitor, stays the tool.
- The operation does not belong in the base interface: adding one virtual per caller-specific question bloats the base and couples it to every client.
- Cross-casts between sibling bases, casts through virtual inheritance or checks that must fail cleanly with nullptr: the idiom does not answer 'what type is this', and the benchmark covers none of these cases.
- Expecting the 5-10x figure on your code: the benchmark uses the cheapest dynamic_cast (one level, always succeeds, since rand() is never seeded and returns non-zero first), and real cost depends on hierarchy depth, multiple inheritance, failing casts and the ABI runtime.
- The dispatch itself is the bottleneck and the concrete type is known at compile time: CRTP or std::variant removes the indirect call too (see the sibling CRTP entry).

## How it is fast

A virtual call loads the vtable pointer, loads the function slot and makes an indirect call; with a single target, as in this benchmark, the indirect branch is always predicted. dynamic_cast instead calls into the C++ ABI runtime (libsupc++ or libc++abi with GCC/Clang, the MSVC runtime), which reads the object's RTTI through the vtable and compares type information before returning the adjusted pointer, so even this best case (one-level hierarchy, cast always succeeds) pays a library call plus type checks.

## Compared with alternatives

The CRTP siblings (the same book's chapter 8 entry and Eli Bendersky's benchmark) remove the virtual call itself and need the concrete type at compile time; this entry is the step before that, replacing an RTTI type test with a virtual call when the set of derived types is only known at run time.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the idiom; the benchmark file needs Google Benchmark (not vendored, version not stated) |
| **Minimum toolchain** | any C++11 compiler for the idiom (the file uses override and std::unique_ptr); the repo ships no build files and the README names only GCC, Clang or Visual Studio |
| **Platforms** | any; README lists Windows, Mac OS X and Linux |
| **Thread safety** | not applicable to the idiom; the benchmark is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Asymmetric harness: BM_dynamic_cast passes every cast result through benchmark::DoNotOptimize, but BM_virtual never observes p-&gt;f()'s return value or the member it changes (no DoNotOptimize or ClobberMemory, and the object is deleted after the loop), so a compiler that speculatively devirtualizes and inlines Derived::f can fold the 64 calls; inspect the disassembly before trusting the virtual row.
- The rows do different work: the virtual row runs a loop-carried --i on a heap member (a read-modify-write chain through memory when f is really called), the cast row a side-effect-free type test, so the ratio compares idioms rather than equivalent operations.
- Google Benchmark's time column is per iteration and each iteration does 64 operations; the repo does not say whether the book's 1 ns and 5-10 ns are per operation or per iteration, so compare the items_per_second column (set by SetItemsProcessed(64\*iterations)) when rerunning.
- No CMakeLists.txt or Makefile exists for Chapter01, so optimisation level, compiler and Google Benchmark version are up to you; the .C extension is C++ to GCC and Clang, but tools that ignore case may compile it as C (MSVC needs /TP).

## Known shortcomings

- Book numbers only. Compares idioms rather than drop-in replacements; the cast always succeeds (no srand, so always Derived), a best case; the virtual result is never observed and may be devirtualised; dynamic_cast cost depends on the ABI runtime.
- Enricher: asymmetric harness (only the cast row uses DoNotOptimize; the rows do different work); unit of the book's figures unclear.

## Caveats and trade-offs

The two benchmarks do different jobs (a call that does work against a successful type test), so the ratio compares idioms, not a drop-in replacement. The cast is the cheapest case for dynamic_cast: a one-level hierarchy where the cast always succeeds (p is Derived unless rand() returns 0, and with no srand call glibc's first rand() value is non-zero, so it is always Derived there); cost grows with deep or multiple inheritance, cross-casts and failing casts, and depends on the C++ ABI runtime (libsupc++, libc++abi, MSVC). The virtual call's effect is never observed (no DoNotOptimize or ClobberMemory on the result or the member, and the object is deleted afterwards), so the compiler may speculatively devirtualize and inline the 64 calls; the virtual row may not measure a real indirect call. Numbers are the book's, not on any repo page; compiler, flags and CPU not stated, first-party. Tier C. Files opened: Chapter01/02_dynamic_cast.C, README.md, LICENSE. [retier] Enricher: asymmetric harness: only the cast row uses DoNotOptimize, so the virtual row's result is never observed and the compiler can devirtualise and fold the 64 calls; the virtual row is a --i chain through heap memory while the cast row is a side-effect-free type test, so the rows do different work. The repo never says whether the book's 1 ns versus 5-10 ns is per operation or per 64-operation iteration. No build files; the .C extension needs /TP on MSVC.

Moves the type-dependent behaviour into a virtual member (or a type tag), which needs the base class to know the operation; dynamic_cast stays the tool when the hierarchy cannot be changed.

## Maintenance

MIT-licensed Packt companion repo (137 stars, 42 forks, not archived) whose code commits end in 2023 and whose last commit (2024-08-29) only added README errata; stale, but the idiom needs no maintenance and the benchmark is small enough to copy and fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter01/02_dynamic_cast.C registers BM_virtual and BM_dynamic_cast with Google Benchmark, so the code compares the two idioms, but the repo holds code only: the 1 ns versus 5-10 ns figures are the book's own run relayed by the lead, with no build files, flags or CPU anywhere in the repo. First-party, so C.
- **Verifier notes:** Source matches the record (REPEAT64, one-level Base/Derived, dynamic_cast result through DoNotOptimize, virtual result discarded). The numbers appear nowhere in the repo; the book was not consulted. Set compared_against_cpp_std_directly to false (dynamic_cast and virtual calls are language features, not standard-library components) and added the observability and ABI-runtime caveats. Metadata confirmed: MIT, 137 stars, 42 forks, not a fork or archived, last commit 2024-08-29, stale.
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-81 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter01/02_dynamic_cast.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter01/02_dynamic_cast.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter01>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter01/02_dynamic_cast.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter01/01_cast.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter08/CMakeLists.txt>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-hands-on-design-patterns-with-cpp-second-edition-virtual-call-vs-dynamic-cast`) · [data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_virtual_call_vs_dynamic_cast.json](../../../data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_virtual_call_vs_dynamic_cast.json) (enrichment confidence 0.55)

</details>
