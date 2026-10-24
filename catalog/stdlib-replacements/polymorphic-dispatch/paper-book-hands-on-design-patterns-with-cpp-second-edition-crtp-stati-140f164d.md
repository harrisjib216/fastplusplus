# Hands-On Design Patterns with C++ 2nd ed: CRTP static polymorphism instead of virtual calls (chapter 8)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Polymorphic dispatch](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book example: CRTP base-class call versus a virtual call through a base pointer; about 5.8x per 32-call loop.

| | |
|---|---|
| **Beats** | virtual member function call through a base-class pointer |
| **Claimed result** | Book (relayed via the seed lead from the book, not shown on any repo page I opened): per iteration of 32 calls, virtual call 9.04 ns against 1.55 ns for the CRTP call and 1.60 ns for the plain non-virtual call. About 5.8x (derived from the relayed numbers). |
| **Workload** | Google Benchmark, 32 repeated calls per iteration of a trivial member f(int) that adds to a member counter: through a base pointer to a virtual function (BM_dynamic), through a CRTP base (BM_static, BM_static1) and a plain non-virtual class (BM_none). |
| **Metric** | latency |
| **Compiler and flags** | Not stated. The repo has no build files (no CMakeLists.txt or Makefile at the root or in Chapter08) and the README's software table lists only 'GCC, Clang or Visual Studio'. Google Benchmark, version not stated. |
| **Adoption** | 137 stars; Packt companion repository of the book Hands-On Design Patterns with C++, 2nd ed. (2023) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition) · [benchmark](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter08/01_function_call.C) |

## Verdict

Reported by the book and relayed by the seed lead, not shown anywhere in the repo: 9.04 ns per iteration of 32 virtual calls through a base pointer against 1.55 ns for the CRTP call and 1.60 ns for the plain non-virtual call, about 5.8x (derived). Compiler, flags, Google Benchmark version and CPU are not stated; the repo holds only the benchmark source, which matches that description.

## Use it when

- Hot loops calling small customisation-point methods where the concrete type is known at compile time and the virtual call blocks inlining.
- Mixin-style code reuse (shared base logic calling derived hooks) where you never need a container of heterogeneous base pointers.
- Template-heavy libraries that already instantiate per type, where one more template parameter on the base costs nothing extra in code organisation.
- As a runnable starting point for measuring virtual versus static dispatch on your own compiler and CPU, since the repo carries the Google Benchmark source.

## Skip it when

- When the concrete type is chosen at run time or objects of different derived types must live behind one base pointer or in one container; CRTP gives each derived class an unrelated base type B&lt;D&gt;.
- When the method body does real work: the 5.8x gap comes from a one-add body, and the dispatch share shrinks as the body grows (the per-call figures are about 0.28 ns virtual and 0.05 ns CRTP, derived from the relayed numbers).
- When the compiler can already devirtualize the virtual call (final classes, a dynamic type visible at the call site, LTO); the gap may be small or absent and the extra template machinery buys nothing.
- When code size or compile time matters: every derived class instantiates its own base, and the base must live in headers.
- As evidence for a specific speedup on your platform: compiler, flags and CPU are not stated anywhere in the repo, and the figures are the book's own run.

## How it is fast

CRTP (curiously recurring template pattern) resolves the call at compile time: B&lt;D&gt;::f() does static_cast&lt;D\*&gt;(this)-&gt;f(i), so there is no vtable lookup and the compiler can inline the derived body. In this benchmark the inlined body lets the compiler fold the 32 additions per iteration, so the reported gap measures inlining and loop folding as much as the cost of an indirect call. The plain non-virtual class runs at the same speed as the CRTP versions, which shows the CRTP layer itself costs nothing once inlined.

## Compared with alternatives

Against the Bendersky CRTP-versus-virtual sibling (about 6x on an Intel i7-4771, code inline in a 2013 post with no license seen), pick this one when you want MIT-licensed, runnable Google Benchmark source to rerun on your own machine; read Bendersky for the original inlining argument and a stated CPU. The chapter 1 sibling from the same repo covers replacing dynamic_cast type tests with a virtual call, a different decision.

## Integration

| | |
|---|---|
| **Form** | source-drop (language idiom; example classes inside a single Google Benchmark .C file) |
| **Dependencies** | none for the idiom; the benchmark file needs Google Benchmark (version not stated); the repo has no CMakeLists.txt, Makefile or other build files in Chapter08 or at the root |
| **Minimum toolchain** | the CRTP idiom needs only class templates (C++98); the benchmark's range-for over benchmark::State needs C++11 plus whatever Google Benchmark requires; README lists GCC, Clang or Visual Studio |
| **Platforms** | any |
| **Thread safety** | not applicable (dispatch idiom, no shared state); the example objects are not synchronised |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmarked CRTP base uses the same name f for the base and derived method; if a derived class forgets to define f, static_cast&lt;D\*&gt;(this)-&gt;f(i) finds B&lt;D&gt;::f and recurses without end. The repo's own Chapter08/02_bad_crtp.C shows this case, and 03_good_crtp.C fixes it by naming the derived hooks f_impl and g_impl so a missing hook fails to compile or falls back to a base default.
- static_polymorphism::B keeps a virtual destructor, so the CRTP object still carries a vtable pointer; the static_polymorphism1 variant drops it, and deleting a derived object through a B&lt;D&gt;\* without a virtual destructor is undefined behaviour (that variant uses a stack object to avoid it).
- Harness: BM_dynamic allocates new D in the same function, so the compiler sees the dynamic type and may devirtualize the call (the about one cycle per virtual call implied by the relayed 9.04 ns per 32 calls suggests it did, at least speculatively; inferred, not compiled). Nothing opaque runs inside the timed loop and the counter is only read through DoNotOptimize after the loop, so the inlined rows fold the 32 adds.
- Harness: the counters are signed int and the loop adds 32 increments per iteration with no reset; the summed i_ passes INT_MAX after about 2,000 iterations in every row, and at the iteration counts Google Benchmark picks for a 1.5 ns body (hundreds of millions) i itself overflows too, which is undefined behaviour. It likely does not change the timing in practice, but the code is not well-defined as written.

## Known shortcomings

- Book numbers only. CRTP rows are below one cycle per call, so the loop was folded; the virtual row (0.28 ns per call, object made by new D in the same function) is likely devirtualised (inferred, not compiled). The CRTP base keeps a virtual destructor. No build files in the repo; stale (last commit 2024-08-29).
- Enricher: signed counter overflow (undefined behaviour) in every row; possible loop folding and devirtualisation; no build files.

## Caveats and trade-offs

Per-call figures work out to about 0.28 ns for the virtual call and about 0.05 ns for the CRTP and non-virtual calls (derived from the relayed numbers), below one cycle for the inlined versions, so the compiler folded the 32 inlined additions (the timed loop calls nothing opaque and the counter is read only after the loop) and the gap measures inlining and loop folding as much as dispatch cost. The virtual row is suspect too: BM_dynamic creates the object with new D in the same function, so its dynamic type is visible to the compiler, and about one cycle per call for a body that loads and stores the same member is hard to reach with a real indirect call, which suggests the compiler devirtualized it, likely speculatively with a guard (inferred from the source and the relayed numbers, not compiled). The CRTP base static_polymorphism::B keeps a virtual destructor, so the CRTP object still carries a vtable pointer; BM_static1 uses a stack object and a free apply() helper. Virtual dispatch gives runtime flexibility that the CRTP version cannot, so the comparison is not feature-equal. Compiler, flags and CPU not stated, first-party, one tiny function. Tier C. Files opened: Chapter08/01_function_call.C, README.md, LICENSE. [retier] Enricher: the signed int counters i_ (after about 2,000 iterations) and i (at Google Benchmark's iteration counts) overflow in every row, undefined behaviour though timing is likely unaffected; the verifier's loop-folding and devirtualisation notes are confirmed. Base and derived share the name f, so a derived class without f recurses forever (the repo's own 02_bad_crtp.C; 03_good_crtp.C fixes it with f_impl). No build files in Chapter08; last code upload 2023-06-19.

Static dispatch fixes the derived type at compile time: no heterogeneous containers of base pointers, no runtime selection, code duplication per derived class. CRTP also lets the compiler inline the call.

## Maintenance

Stale publisher companion repo (last commit 2024-08-29, a README errata update; the benchmark file was added 2023-02-22 and no code has changed since mid-2023), MIT-licensed and copyable, but it is a teaching example of an idiom rather than a component to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter08/01_function_call.C registers BM_none, BM_dynamic, BM_static and BM_static1 with Google Benchmark, so the code compares CRTP against a virtual call, but the repo holds code only: the 9.04/1.55/1.60 ns figures are the book's own run relayed by the lead, with no build files, flags or CPU anywhere in the repo. First-party, so C.
- **Verifier notes:** Source matches the record's workload (REPEAT32 of f(++i), counter read through DoNotOptimize after the loop). The numbers appear nowhere in the repo; the book was not consulted. Set compared_against_cpp_std_directly to false (the baseline is a language feature, not a standard-library component; same as the bendersky virtual-vs-CRTP record) and added the devirtualization and loop-folding caveats. Metadata confirmed: MIT, 137 stars, 42 forks, not a fork or archived, last commit 2024-08-29 (README errata), stale.
- **Fields the verifier corrected:** `compared_against_cpp_std_directly`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-81 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter08/01_function_call.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter08/01_function_call.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter08>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter08/01_function_call.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter08/02_bad_crtp.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter08/03_good_crtp.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-hands-on-design-patterns-with-cpp-second-edition-crtp-static-polymorphism`) · [data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_crtp_static_polymorphism.json](../../../data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_crtp_static_polymorphism.json) (enrichment confidence 0.55)

</details>
