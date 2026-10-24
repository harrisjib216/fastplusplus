# Rust-for-CPP-Developers: matrix_multiply_simd (std::simd f32x4 inner product)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Book example: nightly std::simd f32x4 inner product in a naive Vec&lt;Vec&lt;f32&gt;&gt; matrix multiply, book-reported 1.7x over its scalar loop.

| | |
|---|---|
| **Beats** | same-language scalar unsafe-indexing matrix multiply (the repo's matrix_multiply_unsafe_indexing) |
| **Claimed result** | Book-reported (per the lead): improved by about 41 percent to roughly 208 microseconds versus the scalar unsafe-indexing version (about 1.7x versus 359 microseconds, derived from the quoted figures); cumulative about 2.24 ms to 208 microseconds (about 10.8x, derived). |
| **Workload** | 100x100 f32 Vec&lt;Vec&lt;f32&gt;&gt; matrix multiply (random inputs from make_random), Criterion benchmark via cargo +nightly bench --features nightly: scalar get_unchecked loop versus a 4-lane std::simd f32x4 dot product (row slice load, column gathered by four scalar loads) with a horizontal swizzle-add; inputs cloned inside the timed closure. |
| **Metric** | latency |
| **Hardware** | Not stated (author's own machine per the book). |
| **Compiler and flags** | Criterion 0.5.1 (Cargo.lock) via cargo bench, which inherits the release profile ([profile.release] debug = true in chapter_10/Cargo.toml, opt-level otherwise default); the repo README asks for Rust 1.82.0 or newer and a nightly toolchain for the SIMD step (cargo +nightly bench --features nightly, portable_simd); no rust-toolchain.toml, no .cargo/config.toml, no RUSTFLAGS or target-cpu, and no exact compiler version recorded. |
| **Adoption** | 11 stars (Packt companion repository for the book Rust for C++ Developers) |
| **Last commit** | 2026-03-13 |
| **Links** | [repository](https://github.com/PacktPublishing/Rust-for-CPP-Developers) |

## Verdict

Nothing is measured in the repo. The book, as relayed by the lead, reports the Criterion 100x100 f32 benchmark at about 359 us for the scalar get_unchecked loop and about 208 us for the f32x4 version (about 41 percent less time, about 1.7x derived; about 10.8x cumulative over the 2.24 ms naive loop), with the release profile, the scalar run on the default toolchain and the SIMD run on nightly, no RUSTFLAGS and an unstated CPU.

## Use it when

- Learning Rust's portable SIMD API on nightly: it shows a slice load (from_slice), building a vector from scattered scalars (from_array) and a swizzle-based horizontal sum in about 35 lines.
- As a starting template for a hand-vectorized dot-product kernel, after adding a scalar tail loop and transposing or packing b so both operands load contiguously.
- When you need a float reduction in Rust to vectorize without fast-math flags: a lane-wise accumulator like this one is the explicit, portable way to permit the reordering.
- Code that must run on both x86-64 and aarch64 without target-cpu flags: f32x4 is a 128-bit vector, inside the baseline SSE2 and NEON feature sets.

## Skip it when

- Any shared dimension that is not a multiple of 4: the loop skips the last partial group (if p + 4 &lt;= a_cols), so the product is silently wrong, and all zeros when a_cols &lt; 4.
- Stable Rust or production builds: std::simd needs #![feature(portable_simd)] on nightly, the repo pins no nightly date, and the unstable API can change under it.
- Results that must match the scalar versions bit for bit: four partial sums plus the horizontal add change the summation order and therefore the rounding.
- Real matrix multiplies or larger sizes: the book figure is about 9.6 GFLOPS at 100x100 (derived: 2\*100^3 flops in 208 us), with column gathers through a Vec&lt;Vec&lt;f32&gt;&gt; and no blocking; the catalogued BLAS-class siblings are far faster.
- Untrusted shapes: the b loads use get_unchecked and nothing validates dimensions, so a b with too few rows or ragged rows is undefined behavior rather than a panic.

## How it is fast

A four-lane accumulator: four independent partial sums cut the serial floating-point add chain per output element from 100 dependent scalar adds to 25 dependent vector adds, and each vector multiply does four products. Rust will not reassociate float sums, so the compiler cannot vectorize the scalar reduction itself; the explicit lanes grant that reordering. The gain is capped by the b side, which is not transposed or packed: every b vector is gathered from four different row Vecs (four row-pointer loads, four element loads and lane inserts), so the book reports about 1.7x rather than anything near 4x; there is no FMA, only one accumulator and no blocking.

## Compared with alternatives

Never as a replacement for the catalogued GEMM libraries: for real multiplies in Rust pick faer, and for sizes around 100 consider BLASFEO, which targets small matrices. Pick this entry only to study the std::simd idiom; the sibling Rust-for-CPP-Developers entries (hoisted accumulator, unsafe indexing) are the stable-Rust steps that precede it.

## Integration

| | |
|---|---|
| **Form** | source-drop (a 36-line function in chapter_10/src/simd.rs, compiled only with the performance_test crate's nightly feature) |
| **Dependencies** | none for the function beyond std::simd; the chapter crate pulls rand 0.8.5, elapsed 0.1.2 and flame 0.2.2, plus criterion 0.5.1 as a dev-dependency (Cargo.lock) |
| **Minimum toolchain** | nightly Rust with portable_simd (README: run cargo +nightly bench --features nightly); no rust-toolchain file, so no nightly date is pinned; the README asks for Rust 1.82.0 or newer for the repo overall |
| **Platforms** | any target std::simd supports; the 128-bit f32x4 needs no extra target features on x86-64 (SSE2) or aarch64 (NEON); the repo sets no RUSTFLAGS or target-cpu |
| **Thread safety** | pure function on owned inputs with no shared state; single-threaded |
| **Drop-in for the baseline** | partial — same signature as matrix_multiply_unsafe_indexing, but it needs nightly, gives wrong results unless the shared dimension is a multiple of 4, and rounds differently |

## Gotchas

- Tail bug: for p in (0..a_cols).step_by(4) with an if p + 4 &lt;= a_cols guard drops the last a_cols % 4 terms of every dot product; the 100x100 benchmark never hits it, and the repo has no tests comparing the output with the scalar versions.
- The baseline and SIMD figures come from separate runs on possibly different compilers: the README runs the scalar alias with cargo bench (default toolchain) and the SIMD alias with cargo +nightly bench --features nightly; the book's numbers, CPU and rustc versions are not in the repo.
- The Criterion closure clones both inputs (about 202 heap allocations and 80 KB of copying) and allocates and drops the 101-allocation output inside the timed region; that fixed cost dilutes the ratio, more so at the faster 208 us step.
- Only the a side is bounds-checked (the a[i][p..p + 4] slice); the b gathers and the output store use get_unchecked, so there is no panic path for malformed b.

## Known shortcomings

- Off-baseline for blas-lapack: the only baseline is the book's own scalar Rust (no OpenBLAS, MKL, Eigen or BLIS). The SIMD version drops tail terms when a_cols is not a multiple of 4 (all zeros if a_cols &lt; 4); clone, allocation and drop of all matrices sit inside the Criterion timed region; the SIMD step runs on nightly and the baseline on the default toolchain in separate runs; a second single-run harness (cli.rs) exists and the repo does not say which produced the book figures; 3 commits, no tests.
- Enricher: tail bug confirmed; baseline on stable and SIMD on an unpinned nightly in separate runs; no FMA, single accumulator.

## Caveats and trade-offs

Code check: simd.rs loops p in steps of 4 and skips any tail (if p + 4 &lt;= a_cols), so a shared dimension that is not a multiple of four silently drops terms and returns a wrong product (all zeros when a_cols &lt; 4); the speedup holds only for the multiple-of-four case the benchmark uses. The b column is gathered with four scalar get_unchecked loads from four separate row Vecs per step (no transpose or packing), and the gain over the scalar loop comes largely from four independent partial sums breaking the scalar reduction's dependency chain (the summation order, and so the rounding, differs from the scalar versions). Per the README's run commands the SIMD step runs under cargo +nightly while the scalar baseline runs under the default toolchain, so the two figures may differ in compiler version as well as code, and they are separate runs. Baseline is the book's own scalar Rust, not an optimized library. The repo carries the code for this step (chapter_10/src/lib.rs, chapter_10/src/simd.rs, Criterion bench chapter_10/benches/multiply.rs; Cargo.lock pins criterion 0.5.1 and rand 0.8.5) but no benchmark results, no CPU and no compiler version; the quoted timings come only from the book text as paraphrased in the lead and appear on no page opened here, so they are first-party and unverified. The bench times only the alias matrix_multiply (the unsafe-indexing version on a default build; the SIMD version with --features nightly), and its closure clones both 100x100 input matrices, allocates the Vec&lt;Vec&lt;f32&gt;&gt; result and drops all three matrices inside the timed region, which dilutes every step; reproducing the earlier steps needs editing the alias in lib.rs. A second harness, chapter_10/src/bin/cli.rs, times one matrix_multiply call with elapsed::measure_time (a single run, no warm-up) and writes a flame graph; which harness produced the book's figures is not stated in the repo. All steps compare Rust against its own earlier Rust version; no BLAS, ndarray, nalgebra or C++ baseline appears anywhere in the repo (none of the blas-lapack baselines OpenBLAS, MKL, Eigen or BLIS), so baseline_in_list is false (derived: 2\*100^3 flops in 208 microseconds is about 9.6 GFLOPS, in 2.24 ms about 0.9 GFLOPS). Safety: the unchecked versions never validate dimensions, so ragged rows or a b with fewer than a_cols rows is undefined behavior instead of a panic. The repo has only 3 commits, 11 stars, and no tests that check the results. [retier] Enricher: tail bug confirmed (if p + 4 &lt;= a_cols drops a_cols % 4 terms; all zeros when a_cols &lt; 4); undefined behaviour on short or ragged b. The baseline runs on stable cargo bench and the SIMD version on cargo +nightly, separate runs with possibly different compilers, and no nightly is pinned (no rust-toolchain file). b is gathered by four unchecked strided loads into a single accumulator with no FMA; rounding differs from the scalar version. The Criterion closure clones the inputs (about 202 allocations, 80 KB) and allocates and drops the output (101 allocations) inside the timed loop; the cost is fixed, so ratios are diluted, not inflated.

Needs nightly Rust (portable_simd) behind the nightly cargo feature. The b matrix is not transposed, so each lane group is gathered with four strided loads; matrix sizes must be multiples of four.

## Maintenance

A Packt book companion snapshot (MIT, 11 stars, 3 commits, content committed 2026-03-13, an unmerged Dependabot PR #2 bumping rand to 0.8.6) rather than a maintained library; the function is short enough to copy, but fix the tail before using it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** chapter_10/benches/multiply.rs (Criterion) times matrix_multiply, aliased to simd.rs's matrix_multiply_simd under --features nightly and to matrix_multiply_unsafe_indexing otherwise, so the comparison code is public; the 359 to 208 microsecond figures are the book's own run relayed by the lead, with no CPU, exact compiler version or results in the repo, so first-party C.
- **Verifier notes:** Code matches the lead (simd.rs, lib.rs alias, Criterion bench); book figures not checked (book not consulted per harness), kept at C per the wave11/wave12 book-record precedent. Off-baseline for blas-lapack (own scalar loop only), tail-dropping correctness bug and unchecked-index UB on bad dimensions are shortcomings to record; metadata (MIT, 11 stars, 3 commits, last commit 2026-03-13) confirmed.
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `workload`, `caveats`
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
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:book-rust-for-cpp-developers-simd-f32x4`) · [data/wave8/enrich/raw/paper_book_rust_for_cpp_developers_simd_f32x4.json](../../../data/wave8/enrich/raw/paper_book_rust_for_cpp_developers_simd_f32x4.json) (enrichment confidence 0.6)

</details>
