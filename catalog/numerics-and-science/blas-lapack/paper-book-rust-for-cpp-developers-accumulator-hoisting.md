# Rust-for-CPP-Developers: matrix_multiply_indexing_opt (accumulator hoisted into a local sum)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Book example: keep a matrix-multiply dot product in a local sum, storing once; book-reported 4.1x over in-place accumulation.

| | |
|---|---|
| **Beats** | naive nested-loop matrix multiply with in-place accumulation (out[i][j] += a[i][k]\*b[k][j]), same language (the repo's matrix_multiply_original) |
| **Claimed result** | Book-reported (per the lead): about 2.24 ms down to about 540 microseconds, a 75.9 percent improvement (about 4.1x, derived from the quoted figures). |
| **Workload** | 100x100 f32 Vec&lt;Vec&lt;f32&gt;&gt; matrix multiply, Criterion benchmark, naive triple loop versus the same loop with the running sum kept in a local variable and stored once. |
| **Metric** | latency |
| **Hardware** | Not stated (author's own machine per the book). |
| **Compiler and flags** | Criterion 0.5 via cargo bench (release profile, [profile.release] debug = true in Cargo.toml); Rust 1.82.0 or newer per the book, nightly toolchain for the SIMD step (portable_simd); no RUSTFLAGS or target-cpu stated. |
| **Adoption** | 11 stars (Packt companion repository for the book Rust for C++ Developers) |
| **Last commit** | 2026-03-13 |
| **Links** | [repository](https://github.com/PacktPublishing/Rust-for-CPP-Developers) |

## Verdict

Nothing is measured in the repo. The book, as relayed by the lead, reports the Criterion 100x100 f32 benchmark at about 2.24 ms for matrix_multiply_original and about 540 us for matrix_multiply_indexing_opt (75.9 percent less time, about 4.1x derived), built with the release profile on an unstated rustc (README: 1.82.0 or newer) with no RUSTFLAGS and on an unstated CPU; derived throughput is about 0.9 and 3.7 GFLOPS.

## Use it when

- Any hot Rust loop that accumulates into an indexed heap element or a field (out[i][j] += ..., self.total += ..., \*p += ...): keep the running value in a local and store it once after the loop.
- The same pattern in C++ code, where an output pointer that may alias the inputs (no __restrict) also forces the compiler to keep the load-add-store; a local accumulator removes the dependence on alias analysis.
- When you want a safe-Rust fix with no unsafe blocks and no new dependency: the function keeps the baseline's signature and its bounds checks.
- As the first exercise in profiling a naive kernel: it is the largest single step (book-reported 2.24 ms to about 540 us) in the chapter's chain before unchecked indexing and SIMD.

## Skip it when

- As a matrix multiply for real work: the book figure works out to about 3.7 GFLOPS at 100x100 (derived: 2\*100^3 flops in 540 us), far below the BLAS-class siblings; use a tuned library.
- Larger matrices: it still walks b down a column of a Vec&lt;Vec&lt;f32&gt;&gt;, one row-Vec dereference and one cache line per element, with no transpose, packing or blocking, so cache misses take over as n grows.
- Code that already accumulates in a local or a register-held variable: there is nothing to hoist, and the 4.1x figure belongs to this naive Vec&lt;Vec&lt;f32&gt;&gt; baseline on an unstated machine.
- Untrusted shapes: a_cols and b_cols come from a[0].len() and b[0].len(), so empty input panics, a b with fewer than a_cols rows panics, and extra rows in b are silently ignored; nothing checks that the dimensions agree.

## How it is fast

Scalar replacement (register promotion) of the accumulator. In the baseline every k step is a read-modify-write of a heap f32 reached through two Vec indirections; rustc emits no type-based alias information and the row buffers are reached through pointers loaded from memory, so LLVM most likely cannot prove that the f32 store leaves the Vec headers and elements of a, b and out untouched, and it keeps the load-add-store, reloads the row headers and re-checks bounds on each step, putting a memory round trip into the 100-long dependency chain of every output element. With a local sum the loop body has no stores, the accumulator stays in a register and only the floating-point add chain remains; this mechanism is inferred from the code, since the repo publishes no assembly or profile.

## Compared with alternatives

Never as a replacement for the catalogued GEMM libraries: for real multiplies in Rust pick faer, and for sizes around 100 consider BLASFEO, which targets small matrices. Use this entry when the lesson itself is the point, a safe one-line accumulator fix in your own loop; the sibling Rust-for-CPP-Developers entries (unsafe indexing, f32x4 SIMD) are the next steps of the same chain.

## Integration

| | |
|---|---|
| **Form** | source-drop (an 18-line function in chapter_10/src/lib.rs of the book's performance_test example crate) |
| **Dependencies** | none for the function (std only); the chapter crate pulls rand 0.8.5, elapsed 0.1.2 and flame 0.2.2, plus criterion 0.5.1 as a dev-dependency (Cargo.lock) |
| **Minimum toolchain** | stable Rust, edition 2021; the repo README asks for Rust 1.82.0 or newer (no rust-toolchain file is checked in) |
| **Platforms** | any Rust target (scalar code, no target-specific features) |
| **Thread safety** | pure function on owned inputs with no shared state; single-threaded |
| **Drop-in for the baseline** | partial — same signature as matrix_multiply_original and the same summation order, so the output is bit-identical; it is an edit you apply to your own loop rather than a component you link |

## Gotchas

- The repo's Criterion bench (benches/multiply.rs, 'multiply 100x100') times only the matrix_multiply alias, which lib.rs points at matrix_multiply_unsafe_indexing on stable and matrix_multiply_simd with --features nightly; reproducing this comparison means editing the pub use line, and no results, CPU or rustc version are in the repo.
- The timed closure clones both 100x100 inputs (about 202 heap allocations and 80 KB of copying) and allocates and then drops the 101-allocation output on every iteration; that fixed cost is the same for both versions, so it shrinks the measured ratio rather than inflating it.
- The safe version still bounds-checks a[i][k], b[k] and b[k][j] on every step (a_cols is taken from a[0] only, so the compiler cannot drop the checks for other rows); removing them is the chapter's next, unsafe step.
- The repo has no tests; equivalence with matrix_multiply_original rests on reading the code (both add the k terms in the same order starting from 0.0).

## Known shortcomings

- Verifier: timings appear only in the book (relayed via the seed lead), first-party; code and Criterion bench are in chapter_10.
- Enricher: mechanism inferred from code only (no assembly or profile); the repo bench cannot run this pair without editing lib.rs; input clones and output allocation inside the timed loop dilute the ratio.

## Caveats and trade-offs

Baseline is the book's own deliberately naive Rust version, so this is a small idiom fix, not a library win. The repo carries the code for this step (chapter_10/src/lib.rs, chapter_10/src/simd.rs, Criterion bench chapter_10/benches/multiply.rs, Cargo.lock pins criterion 0.5.1 and rand 0.8.5) but no benchmark results, no CPU and no compiler version; the quoted timings come only from the book text as paraphrased in the lead and appear on no page opened here, so they are first-party and unverified. The bench times only the alias matrix_multiply (the unsafe-indexing version on a default build; the SIMD version with --features nightly) and its closure clones both 100x100 input matrices and allocates the Vec&lt;Vec&lt;f32&gt;&gt; result inside the timed region, which dilutes every step; reproducing the earlier steps needs editing the alias in lib.rs. All three steps compare Rust against its own earlier Rust version; no BLAS, ndarray, nalgebra or C++ baseline appears anywhere in the repo (derived: 2\*100^3 flops in 208 microseconds is about 9.6 GFLOPS, in 2.24 ms about 0.9 GFLOPS). The repo has only 3 commits, 11 stars, and no tests that check the results. [retier] Enricher: the summation order is unchanged, so the output is bit-identical to the original. The mechanism (Rust emits no type-based alias information here, so a store into the output may alias the Vec headers and forces a load-add-store each step) is inferred from code only; the repo has no assembly or profile. The safe version still bounds-checks a[i][k], b[k] and b[k][j]. The repo bench cannot run this pair without editing the pub use alias in lib.rs. The Criterion closure clones the inputs (about 202 allocations, 80 KB) and allocates and drops the output (101 allocations) inside the timed loop; the cost is fixed, so ratios are diluted, not inflated. No results, CPU or rustc version in the repo; unmerged Dependabot PR #2.

Safe Rust, same API and result type; pure source-level change in the inner loop; still bounds-checked and still strides down b's columns (no transpose or blocking).

## Maintenance

A Packt book companion snapshot (MIT, 11 stars, 3 commits, content committed 2026-03-13, an unmerged Dependabot PR #2 bumping rand to 0.8.6) rather than a maintained library, but the idiom is a few lines and free to copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** chapter_10/src/lib.rs holds both matrix_multiply_original (out[i][j] += inside the k loop) and matrix_multiply_indexing_opt (local sum stored once) and chapter_10/benches/multiply.rs is a Criterion bench, but the repo has no results, CPU, rustc version or RUSTFLAGS; the 2.24 ms to 540 us figures come only from the book as relayed by the lead, so first-party C (same as the wave11 book-record precedent).
- **Verifier notes:** Code and caveats checked: Cargo.toml has [profile.release] debug = true and a nightly feature; Cargo.lock pins criterion 0.5.1 and rand 0.8.5; the bench clones both inputs inside b.iter and times only the matrix_multiply alias (matrix_multiply_unsafe_indexing by default, simd with --features nightly). Both versions give the same summation order, so results match. Metadata confirmed: MIT, 11 stars, 3 commits, last 2026-03-13. No benchmark_url exists; none found.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-182 (wave 8 book seed pass, 2026-10-24); enrichment (wave 8 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/commits>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/lib.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/simd.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/benches/multiply.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.toml>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.lock>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/commits/main>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/issues>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/pulls>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/pull/2>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/tree/main/chapter_10>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.toml>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.lock>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/lib.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/simd.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/benches/multiply.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/bin/cli.rs>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:book-rust-for-cpp-developers-accumulator-hoisting`) · [data/wave8/enrich/raw/paper_book_rust_for_cpp_developers_accumulator_hoisting.json](../../../data/wave8/enrich/raw/paper_book_rust_for_cpp_developers_accumulator_hoisting.json) (enrichment confidence 0.55)

</details>
