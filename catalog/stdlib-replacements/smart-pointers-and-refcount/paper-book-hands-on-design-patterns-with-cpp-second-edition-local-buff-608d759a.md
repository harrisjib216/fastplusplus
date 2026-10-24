# Hands-On Design Patterns with C++ 2nd ed: type-erased smart pointer with local-buffer deleter (smartptr_te_static / smartptr_te_vtable)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Teaching sketch of a single-owner pointer that type-erases its deleter inline; the book times it against std::shared_ptr with a custom deleter.

| | |
|---|---|
| **Beats** | std::shared_ptr&lt;int&gt; with a custom deleter (and std::make_shared&lt;int&gt;) |
| **Claimed result** | Book (relayed via the seed lead from the book, not shown on any repo page I opened): about 9.58 ns (static-function variant) and 10.4 ns (vtable variant) against 22.9 ns for std::shared_ptr with a custom deleter and 17.5 ns for make_shared; raw pointer 8.72 ns and unique_ptr 8.82 ns as floor. About 2.4x and 2.2x against shared_ptr-with-deleter (derived from the relayed numbers). |
| **Workload** | Google Benchmark, construct and destroy one smart pointer to a new int(0) allocated in a separate translation unit: the book's smartptr_te_static and smartptr_te_vtable (deleter stored inline, no control-block allocation) against std::shared_ptr with a custom deleter and make_shared; raw pointer and std::unique_ptr with a deleter as floor. |
| **Metric** | latency |
| **Compiler and flags** | The book's sample build line is -g -O3 --std=c++20 with whole-program optimisation off (relayed via lead); the opened sources (07_smartptr.C, 07_smartptr.h, 07_smartptr_ext.C) carry no build line and the README lists no flags. |
| **Adoption** | 137 stars; Packt companion repository of the book Hands-On Design Patterns with C++, 2nd ed. (2023) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition) · [benchmark](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter06/07_smartptr.C) |

## Verdict

The book (relayed through the seed lead; no numbers in the repository) reports a construct-plus-destroy cost of about 9.58 ns for smartptr_te_static and 10.4 ns for smartptr_te_vtable, against 22.9 ns for std::shared_ptr&lt;int&gt; with a custom deleter, 17.5 ns for make_shared, 8.82 ns for std::unique_ptr and 8.72 ns for a raw pointer. These are Google Benchmark rows built with -g -O3 --std=c++20 and whole-program optimisation off; the compiler version, standard library and CPU are not stated. The harness is sound for what it times: every row allocates new int(0) in a separate translation unit (07_smartptr_ext.C) and destroys it in the benchmark file, so allocation cannot be elided and the type-erased destroy calls stay indirect.

## Use it when

- You need a single-owner pointer whose deleter type must not appear in the pointer type (for example, uniform handles from different allocators or pools), and std::shared_ptr's control-block allocation shows up in profiles
- The deleter is stateless or holds at most 8 bytes (one pointer to a pool or arena)
- Very frequent create/destroy of small objects, where a second allocation per object dominates
- As a reference implementation to adapt into a production unique-ownership pointer with a type-erased deleter

## Skip it when

- You need shared ownership, weak_ptr, or thread-safe reference counting: these pointers have none of it, so they do not replace std::shared_ptr
- The deleter type can be part of the pointer type: std::unique_ptr&lt;T, D&gt; has no type-erasure cost and the book's own unique_ptr row is at least as fast
- Deleters larger than 8 bytes or over-aligned beyond 8: static_assert rejects larger ones, there is no heap fallback, and alignment is never checked
- Anything that copies or moves the pointer: no copy or move operations are declared, so the implicitly generated copy would delete the pointee twice

## How it is fast

The deleter object goes into an 8-byte aligned buffer inside the pointer, so the only allocation is the pointee itself; std::shared_ptr(p, d) allocates a separate control block for the deleter and reference counts. smartptr_te_static stores one function pointer to a static invoke_destroy&lt;Deleter&gt; instantiation, so destruction makes one indirect call. smartptr_te_vtable points to a constexpr static table holding destroy and destructor entries, which costs one more load and call but supports deleters that are not trivially destructible. This is hand-rolled type erasure with small-buffer storage in place of a heap-allocated virtual deleter.

## Compared with alternatives

No catalogued sibling offers this exact shape: observable_unique_ptr adds weak observers to unique ownership, and the publishing pointer from The Art of Writing Efficient Programs targets concurrent access. Use these classes as a pattern to copy and harden when you need unique ownership with a type-erased inline deleter.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the classes (the benchmark needs Google Benchmark) |
| **Minimum toolchain** | C++17 language features (static_assert without a message, _v type traits, a constexpr static variable-template member); the book builds with --std=c++20 |
| **Platforms** | any; the buffer is a fixed alignas(8) char[8] |
| **Thread safety** | not documented; there is no shared state, so it behaves like any single-owner object |
| **Drop-in for the baseline** | no |

## Gotchas

- No copy or move constructor is declared and the destructor is user-defined, so a copy compiles and then double-deletes; factories work only because C++17 guarantees copy elision for the prvalue return.
- The sibling local-buffer variants in the same header (smartptr_te_lb and smartptr_te_lb0) check sizeof(Deleter) against their 16-byte buffer but place destroy&lt;Deleter&gt;, which adds a vtable pointer, so a 9-16-byte deleter overflows the buffer. The benchmark's empty deleter fits, so the bug never shows there.
- The headline comparison is against std::shared_ptr, which also allocates a control block and reference counts. Most of the gap is that extra allocation and bookkeeping rather than a faster type-erasure mechanism: against the raw-pointer floor the book's variants add only about 0.9 to 1.7 ns (derived from the relayed numbers).
- The fairest stdlib baseline for a type-erased single-owner pointer, std::unique_ptr&lt;T, std::function&lt;void(T\*)&gt;&gt;, is not benchmarked.

## Known shortcomings

- Book numbers only. The local-buffer smart pointers do not beat std::unique_ptr (8.82 ns); the closer baselines in the same file are BM_smartptr_te (heap type-erased), _lb, _lb0 and unique_ptr. Teaching code: copying would double-delete.
- Enricher: lopsided shared_ptr baseline (the variants do not beat unique_ptr); sibling smartptr_te_lb classes overflow the buffer for 9-16 byte deleters; no copy or move operations (copies double-delete).

## Caveats and trade-offs

Not feature-equal: std::shared_ptr allocates a control block and does atomic reference counting, while the book's pointers have unique ownership. The benchmark does contain closer like-for-like rows: BM_smartptr_te (the book's own type-erased deleter on the heap, virtual call) and the local-buffer virtual variants BM_smartptr_te_lb and BM_smartptr_te_lb0, plus std::unique_ptr&lt;int, deleter&gt; (no type erasure); a std::unique_ptr with a std::function deleter is not benchmarked. Net overhead over the raw-pointer floor is only about 0.9 to 1.7 ns (derived from the relayed numbers), so most of the gap to shared_ptr is the control-block allocation and atomic counting. Factory functions sit in a separate translation unit (07_smartptr_ext.C) so new/delete cannot be elided, which keeps the rows comparable. smartptr_te_static and smartptr_te_vtable declare no copy or move operations, so the implicit copy would double-delete: teaching code, not a drop-in smart pointer. The book's chapter 10 repeats the idea with different absolute numbers (21.0, 44.2 and 22.3 ns, recorded in the no-evidence file), so absolute figures vary between runs or machines. First-party, compiler and CPU not stated in the repo. Tier C. [retier] Enricher: the harness is sound (allocation in a separate file, the destroy call stays indirect), but the baseline is lopsided: shared_ptr pays for a control block and reference counting, and the book's variants do not beat unique_ptr. Sibling classes smartptr_te_lb and smartptr_te_lb0 compare sizeof(Deleter) with the buffer instead of sizeof(destroy&lt;Deleter&gt;), which adds a vtable pointer, so a 9-16 byte deleter overflows the buffer (the benchmark's empty deleter hides it). No copy or move operations, so any copy double-deletes.

Single-owner, move-only pointer with a type-erased deleter stored inline; no reference counting and no weak pointers. The static variant stores a function pointer plus the deleter object in a small buffer, the vtable variant a pointer to a constexpr vtable.

## Maintenance

Stale (last commit 2024-08-29) MIT-licensed book companion code; copyable, but it lacks copy and move semantics and most of a smart-pointer API, so treat it as a pattern rather than a component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter06/07_smartptr.C (with 07_smartptr.h and 07_smartptr_ext.C) benchmarks smartptr_te_static and smartptr_te_vtable against std::shared_ptr with a custom deleter, std::make_shared, std::unique_ptr and a raw pointer, but the repo shows no results, compiler, flags or CPU; numbers are the book's own, so C.
- **Verifier notes:** Benchmark code matches the record; corrected the caveat that the like-for-like baseline is absent (the book's heap type-erased smartptr_te row is in the file). Comparison against shared_ptr is apples-to-oranges (shared vs unique ownership); unique_ptr row is the fairer stdlib baseline and the book's pointers do not beat it. Metadata confirmed: MIT, 137 stars, last commit 2024-08-29 (stale).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-83 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter06/07_smartptr.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/07_smartptr.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/07_smartptr.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/07_smartptr_ext.C>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/07_smartptr.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/07_smartptr.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter06/07_smartptr_ext.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/README.md>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter06>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter10>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/HEAD/Chapter10/09_smartptr.C>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-hands-on-design-patterns-with-cpp-second-edition-local-buffer-smartptr`) · [data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_local_buffer_smartptr.json](../../../data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_local_buffer_smartptr.json) (enrichment confidence 0.6)

</details>
