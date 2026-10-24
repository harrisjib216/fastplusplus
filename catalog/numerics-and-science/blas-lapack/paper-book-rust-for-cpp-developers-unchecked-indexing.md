# Rust-for-CPP-Developers: matrix_multiply_unsafe_indexing (get_unchecked bounds-check removal)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Book example: naive Rust f32 matrix multiply that swaps safe indexing for get_unchecked, about 1.5x over the safe loop (book figure).

| | |
|---|---|
| **Beats** | same-language safe indexed matrix multiply with the hoisted accumulator (the repo's matrix_multiply_indexing_opt) |
| **Claimed result** | Book-reported (per the lead): about 540 microseconds down to about 359 microseconds, a 33.7 percent improvement over the previous step (about 1.5x, derived from the quoted figures); cumulative about 2.24 ms to 359 microseconds (about 6.2x, derived). |
| **Workload** | 100x100 f32 Vec&lt;Vec&lt;f32&gt;&gt; matrix multiply, Criterion benchmark, safe indexing versus get_unchecked / get_unchecked_mut in the inner loop. |
| **Metric** | latency |
| **Hardware** | Not stated (author's own machine per the book). |
| **Compiler and flags** | Criterion 0.5.1 (Cargo.lock) via cargo bench, which inherits the release profile ([profile.release] debug = true in chapter_10/Cargo.toml, opt-level otherwise default); the repo README asks for Rust 1.82.0 or newer and a nightly toolchain for the SIMD step (cargo +nightly bench --features nightly, portable_simd); no rust-toolchain.toml, no .cargo/config.toml, no RUSTFLAGS or target-cpu, and no exact compiler version recorded. |
| **Adoption** | 11 stars (Packt companion repository for the book Rust for C++ Developers) |
| **Last commit** | 2026-03-13 |
| **Links** | [repository](https://github.com/PacktPublishing/Rust-for-CPP-Developers) |

## Verdict

The book's figures (relayed by the lead; not in the repository) put one 100x100 f32 multiply under Criterion at about 540 microseconds for the safe hoisted-accumulator loop and about 359 microseconds with get_unchecked, about 1.5x (derived), on an unstated CPU and Rust version. The repository carries the code and the Criterion bench but no results, CPU or compiler version, and the two figures necessarily come from separate cargo bench runs.

## Use it when

- As a worked, minimal illustration of what bounds checks cost in a hot Rust inner loop before you decide to use unsafe in your own code.
- Porting a C++ loop that relied on unchecked operator[] when profiling shows the Rust bounds checks dominate and the shapes are validated once at the API boundary.
- Small dense f32 products (the bench uses 100x100) inside code that cannot take a BLAS or linear-algebra dependency and whose callers you control.
- As one step of the chapter's sequence (original, hoisted accumulator, unchecked indexing, unchecked init, SIMD) when teaching or learning Rust optimization with Criterion.

## Skip it when

- Any real matrix workload: the repo has no BLAS, ndarray, nalgebra, faer or C++ comparison, and the book's 359 microseconds for 100x100 works out to about 5.6 GFLOPS (derived from the quoted figure), far below the optimized GEMM entries in this category.
- Inputs whose shapes you do not control: ragged rows or a b with fewer than a[0].len() rows read out of bounds, which is undefined behaviour instead of the safe version's panic.
- Crates that forbid unsafe code; the safe hoisted-accumulator version in the same file is the fallback, about 1.5x slower by the book's figure.
- Large matrices or multithreaded use: single-threaded, each row is a separate heap allocation and b is walked by column; nothing beyond 100x100 is benchmarked in the repo.

## How it is fast

It removes Rust's per-access bounds checks (a compare and branch for a[i][p], b[p] and b[p][j]) from the innermost loop; with jagged Vec&lt;Vec&lt;f32&gt;&gt; storage and the loop bound taken from a[0].len(), the compiler has no proof that those indices are in range, so the safe version keeps the checks inside the loop. Nothing else changes: the loop stays scalar with one sequential f32 accumulator and a column-wise walk of b (the repo's next step, simd.rs, adds f32x4 vectorization by hand), and the summation order matches the safe hoisted-accumulator version, so valid inputs give the same results.

## Compared with alternatives

Not as a GEMM: for real throughput use faer (the Rust entry in this category), BLASFEO for matrices in the tens, or Eigen/OpenBLAS-class libraries. Pick this only as a reference for how much Rust bounds checks cost in a naive loop.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the function itself (the chapter crate pulls rand 0.8, elapsed 0.1 and flame 0.2; criterion 0.5 for the bench) |
| **Minimum toolchain** | Rust 1.82.0 or newer per the repo README (stable; nightly only for the later SIMD step) |
| **Platforms** | any (portable scalar Rust, no target-specific code) |
| **Thread safety** | Pure function over owned inputs with no shared state; not documented beyond that |
| **Drop-in for the baseline** | partial: same fn(Matrix, Matrix) -&gt; Matrix signature as matrix_multiply_indexing_opt, but mismatched or ragged shapes become undefined behaviour instead of a panic |

## Gotchas

- Unsound safe API: it is a plain pub fn whose unsafe blocks never check that rows are rectangular or that b has at least a[0].len() rows, so safe callers can trigger undefined behaviour; only empty inputs still panic (on a[0] or b[0]).
- The Criterion bench (benches/multiply.rs) clones both 100x100 inputs and allocates and drops the result matrix inside the timed closure, so allocation and copying add a fixed cost to every step and compress the ratios between steps.
- Which version is timed is chosen by a compile-time alias in lib.rs (pub use ... as matrix_multiply), so comparing two steps needs a source edit and a second cargo bench run; the safe and unchecked versions are never measured side by side in one run, and Criterion's change percentage is against the previously saved run.
- No RUSTFLAGS, target-cpu or rust-toolchain file, and [profile.release] only adds debug = true, so results depend on the default target ISA and whatever compiler version was installed.

## Known shortcomings

- Off-baseline for blas-lapack: the only baseline is the book's own checked-indexing Rust. The unchecked versions never check dimensions, so bad dimensions are undefined behaviour; clone, allocation and drop of all matrices sit inside the Criterion timed region; a second single-run harness (cli.rs) exists and the repo does not say which produced the book figures; 3 commits, no tests.
- unsound safe API: shapes never validated, ragged input reaches unchecked reads; safe and unchecked timed in separate cargo bench runs

## Caveats and trade-offs

Baseline is the book's own safe version (matrix_multiply_indexing_opt), not a C++ or BLAS routine; the gain is the cost of Rust's bounds checks on the inner loop's a[i][k] and b[k][j] reads (the get_unchecked_mut write sits outside the inner loop). Each step is a separate cargo bench run after editing the alias. The repo carries the code for this step (chapter_10/src/lib.rs, chapter_10/src/simd.rs, Criterion bench chapter_10/benches/multiply.rs; Cargo.lock pins criterion 0.5.1 and rand 0.8.5) but no benchmark results, no CPU and no compiler version; the quoted timings come only from the book text as paraphrased in the lead and appear on no page opened here, so they are first-party and unverified. The bench times only the alias matrix_multiply (the unsafe-indexing version on a default build; the SIMD version with --features nightly), and its closure clones both 100x100 input matrices, allocates the Vec&lt;Vec&lt;f32&gt;&gt; result and drops all three matrices inside the timed region, which dilutes every step; reproducing the earlier steps needs editing the alias in lib.rs. A second harness, chapter_10/src/bin/cli.rs, times one matrix_multiply call with elapsed::measure_time (a single run, no warm-up) and writes a flame graph; which harness produced the book's figures is not stated in the repo. All steps compare Rust against its own earlier Rust version; no BLAS, ndarray, nalgebra or C++ baseline appears anywhere in the repo (none of the blas-lapack baselines OpenBLAS, MKL, Eigen or BLIS), so baseline_in_list is false (derived: 2\*100^3 flops in 208 microseconds is about 9.6 GFLOPS, in 2.24 ms about 0.9 GFLOPS). Safety: the unchecked versions never validate dimensions, so ragged rows or a b with fewer than a_cols rows is undefined behavior instead of a panic. The repo has only 3 commits, 11 stars, and no tests that check the results. [retier] Enricher: the Criterion closure clones both inputs and allocates and drops the result inside the timed region, which shrinks the gap between steps; which version is timed is set by a compile-time alias, so the safe and unchecked versions only run in separate cargo bench runs (cross-run, probably one machine). No target-cpu flag and no rust-toolchain file. The safe public function never validates shapes, so ragged input reaches the unchecked reads (unsound API, undefined behaviour). The book figure is about 5.6 GFLOPS (derived), far from BLAS.

Uses unsafe get_unchecked with no checks that the matrices are rectangular or that a's column count equals b's row count; a bad shape is undefined behaviour instead of a panic. Default build of the repo's matrix_multiply alias.

## Maintenance

Packt companion repository with 3 commits (last 2026-03-13), 11 stars and one open Dependabot PR (rand 0.8.5 to 0.8.6); MIT-licensed example code to copy rather than a maintained crate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** chapter_10/src/lib.rs holds both matrix_multiply_indexing_opt and matrix_multiply_unsafe_indexing and chapter_10/benches/multiply.rs times the aliased one with Criterion, so the code is public; the 540 to 359 microsecond figures are the book's own run relayed by the lead, with no CPU, exact compiler version or results in the repo, so first-party C.
- **Verifier notes:** Code matches the lead (safe hoisted-accumulator loop versus get_unchecked reads); book figures not checked (book not consulted per harness), kept at C per book-record precedent. Off-baseline for blas-lapack (compares against its own safe Rust loop) and unchecked-index UB on bad dimensions are shortcomings to record; same repo metadata as the SIMD record, confirmed.
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-183 (wave 8 book seed pass, 2026-10-24); enrichment (wave 8 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/commits/main>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/tree/main/chapter_10>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/tree/main/chapter_10/src>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/tree/main/chapter_10/src/bin>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.toml>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.lock>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/lib.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/simd.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/bin/cli.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/benches/multiply.rs>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/commits/main>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/pulls>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/pull/2>
  - <https://github.com/PacktPublishing/Rust-for-CPP-Developers/tree/main/chapter_10>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.toml>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/Cargo.lock>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/lib.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/simd.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/src/bin/cli.rs>
  - <https://raw.githubusercontent.com/PacktPublishing/Rust-for-CPP-Developers/HEAD/chapter_10/benches/multiply.rs>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:book-rust-for-cpp-developers-unchecked-indexing`) · [data/wave8/enrich/raw/paper_book_rust_for_cpp_developers_unchecked_indexing.json](../../../data/wave8/enrich/raw/paper_book_rust_for_cpp_developers_unchecked_indexing.json) (enrichment confidence 0.6)

</details>
