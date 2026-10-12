# Minarrow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Lean Rust Apache Arrow implementation with enum-dispatched typed arrays; about 1.7x faster than arrow-rs on a 1,000-element sum microbenchmark.

| | |
|---|---|
| **Beats** | Apache Arrow |
| **Claimed result** | Sum of 1,000 i64, averaged over 1,000 runs: Minarrow IntegerArray direct 88 ns vs arrow-rs Int64Array (struct) 147 ns and arrow-rs Int64Array (dyn) 181 ns, about 1.7x-2.1x faster (derived from page data). Minarrow via enum dispatch is 124 ns (about 1.2x-1.5x vs arrow-rs, derived from page data), and a raw Vec&lt;i64&gt; is 85 ns. The Rust-&gt;Python handoff (1M rows, 2 cols) is 165 ns and Python-&gt;Rust is 2.5 us, but these are standalone figures with no Arrow/pyarrow comparison. |
| **Workload** | Sum of 1,000 i64 integers averaged over 1,000 runs, comparing raw Vec&lt;i64&gt;, Minarrow's IntegerArray (direct and via enum dispatch), and arrow-rs's Int64Array (struct and dyn-dispatched), plus a separate Rust&lt;-&gt;Python zero-copy roundtrip test on 1M rows x 2 columns via PyO3 |
| **Metric** | latency |
| **Hardware** | Intel Core Ultra 7 155H, 32GB RAM, Ubuntu 24.04 |
| **Compiler and flags** | rustc 1.97-nightly, release build (cargo bench; the repo sets no custom [profile], so default opt-level 3). The bench file header recommends RUSTFLAGS="-C target-cpu=native", but the README does not confirm it was used for the published numbers. |
| **Adoption** | 100 stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/SpaceCell/minarrow) · [benchmark](https://github.com/SpaceCell/minarrow#benchmarks) |

## Verdict

The benchmark summed 1,000 i64 values, with array construction inside the timed region, and averaged 1,000 Instant-timed runs on an Intel Core Ultra 7 155H under Ubuntu 24.04 (release build; the footnote says Rust 1.97-nightly). Minarrow IntegerArray took 88 ns (124 ns through the Array enum), against 147 ns for arrow-rs Int64Array as a struct, 181 ns through an ArrayRef downcast, and 85 ns for a raw Vec. The same five figures have been in src/lib.rs since v0.1.0 (2025-08-13, built against arrow 55.2.0), so they were probably not re-measured on the stated toolchain or against the current arrow 59.2 dependency.

## Use it when

- Rust code that keeps Arrow-layout columns in memory and wants typed access (arr.num().i64()) without dyn Array downcasting, especially in latency-sensitive loops over primitive i64/f64 columns.
- Rust-to-Python handoff of tables to PyArrow/Polars through PyCapsule or the C Data Interface. Export is zero-copy, and the README reports 165 ns Rust-&gt;Python and 2.5 us Python-&gt;Rust for 1M rows x 2 columns. Import is zero-copy only for 64-byte-aligned buffers.
- Projects that want a small dependency tree and fast builds. The base build pulls in only num-traits, vec64 and log, and the README claims compiles under 2 s.
- Custom SIMD kernels that need every owned buffer guaranteed 64-byte aligned.
- Passing numeric data to PyTorch, JAX or NumPy through DLPack (the ndarray and dlpack features).

## Skip it when

- You need nested Arrow types (List, Struct). They are not implemented, and Interval and Null arrays panic on C Data Interface import.
- You must build on stable Rust. The crate requires nightly for allocator_api and portable_simd; CONTRIBUTING asks for 1.89.0-nightly or later, and CI runs only on nightly.
- You need broad compute kernels, SQL, or Parquet/IPC file I/O in the same crate. arrow-rs plus DataFusion covers far more; Minarrow ships a small kernel set and leaves IPC streaming to the separate lightstream crate.
- Your arrow-rs code already sums over values() slices or uses arrow compute kernels. The headline gap was measured against per-index value(i) calls, and the crate's own SIMD table in src/lib.rs shows Minarrow via enum at 170 ns vs arrow-rs dyn at 173 ns (parity).
- You need API stability or an open contribution model. Pre-1.0 releases break often (0.17.0 switched integer division to floor semantics, 0.18.0 added enum variants), there is effectively one maintainer, and contributors must sign a CLA that assigns copyright to him.

## How it is fast

Type dispatch goes through nested enums (Array -&gt; NumericArray -&gt; Arc&lt;IntegerArray&lt;T&gt;&gt;) instead of arrow-rs's Arc&lt;dyn Array&gt; plus as_any().downcast_ref, so the compiler can inline the match and hand back a concrete typed array. Every owned buffer is a Vec64 (the author's 64-byte-aligned Vec, built on the nightly allocator_api), so values are read as a plain aligned slice and fed to std::simd (portable_simd) kernels whose lane counts build.rs fixes from the target's features (SSE2, AVX2, AVX-512 or NEON). There is no new algorithm, and in the published benchmark part of the gap comes from the access pattern: the Minarrow paths iterate a slice, while the arrow-rs paths call the bounds-asserting value(i) once per element.

## Compared with alternatives

None of the catalogued siblings is an in-memory Arrow array library. Pick Apache DataFusion (built on arrow-rs) when you need SQL or query execution, and Vortex or Lance when the problem is on-disk columnar encoding. Pick Minarrow when you want a lean, typed in-memory Arrow container in Rust with a fast Python handoff and can accept nightly Rust and no nested types.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Base: num-traits, vec64 (the author's 64-byte-aligned Vec crate) and log (a default feature). Optional, behind feature flags: arrow/arrow-schema 59.2, polars-core/polars-arrow 0.55.2, rayon, time, phf, ahash, hashbrown, parking_lot, regex, ryu, memchr and libc. |
| **Minimum toolchain** | Rust nightly, edition 2024 (CONTRIBUTING says 1.89.0-nightly or later). Needs the allocator_api and portable_simd features. |
| **Platforms** | x86-64, with SIMD width picked at build time from target features (SSE2, AVX2 or AVX-512); aarch64 (NEON); wasm32 (simd128); scalar fallback elsewhere. CI runs tests on Linux, macOS and Windows but only compile-checks aarch64 and armv7 Linux. The memfd and vmap64 features are Linux-only. |
| **Thread safety** | Buffer&lt;T&gt; is declared Send + Sync (subject to T), and arrays sit behind Arc inside the Array and NumericArray enums, so sharing them read-only across threads works. Mutating a shared buffer copies it first. Concurrent mutation is not documented, except through the lbuffer feature, which Cargo.toml marks experimental and not recommended for production. |
| **Drop-in for the baseline** | partial — it is not API-compatible with arrow-rs (different types and accessors). It shares the Arrow memory layout and converts to/from arrow-rs ArrayRef/RecordBatch through the C Data Interface under the cast_arrow feature, zero-copy when buffers are 64-byte aligned. It lacks List/Struct types and arrow-rs's compute, IPC and Parquet stack. |

## Gotchas

- Accessors such as Array::num() and NumericArray::i64() return a shared Arc handle only when the variant matches. Otherwise they allocate and convert (for example Int32 or Float64 to i64), and they panic on Null or a failed cast. Use the try_ variants in library code.
- Zero-copy import requires 64-byte-aligned buffers. Data from pandas and Polars is typically not aligned that way, so each such column is copied into a Vec64 and a log warning is emitted (issue #57). String offsets, categorical dictionaries and Utf8View arrays are always copied on import.
- build.rs bakes SIMD lane counts in from compile-time target features. The repo's .cargo/config.toml forces x86-64-v3 only for builds run inside the repository, so a downstream x86-64 build without -C target-cpu gets 128-bit SSE2 lanes.
- Hot paths use unchecked access. Issue #200 (fixed in 0.18.2) showed out-of-bounds reads reachable from safe code in the string kernels and in Buffer::from_shared_column. Cargo.toml also warns that vmap64 combined with any FFI export (cast_arrow, cast_polars, memfd) is undefined behaviour.

## Known shortcomings

- The arrow-rs side sums via value(i) rather than slices, so the comparison favors Minarrow; a micro-benchmark of one hot loop.
- The benchmark numbers are stale: the same five figures have sat in src/lib.rs since v0.1.0 (2025-08, arrow 55.2) and were not re-measured against the current arrow 59.2 dependency; its own SIMD table shows parity (170 vs 173 ns). Nightly only; no List/Struct; Interval/Null FFI import panics; zero-copy import needs 64 B-aligned buffers (pandas/Polars columns get copied, #57); .num()/.i64() convert and allocate on variant mismatch and panic on failure. An unsound out-of-bounds bug in string kernels (#200) was fixed in 0.18.2; vmap64 with FFI is UB; pre-1.0 churn; single maintainer with a CLA assigning copyright.

## Caveats and trade-offs

This is a micro-benchmark of a single primitive (a scalar sum over 1,000 elements), not a query-engine workload, and the results may not generalize. The benchmark code is benches/hotloop_benchmark_avg_std.rs; no raw output is published. Each timed region includes wrapping the pre-built Vec into the array. The arrow-rs paths sum through per-index int.value(i) calls rather than iterating the values() slice, while the Minarrow paths iterate a slice. The gap may therefore reflect the access pattern chosen for Arrow, not an inherent arrow-rs cost. Timings are nanosecond-scale Instant measurements and are noise-sensitive.

Deliberately minimal Arrow implementation (no List/Struct nested types yet); nightly Rust toolchain required for allocator_api/portable_simd; requires CLA for contributions. Gains come from a leaner enum-dispatch array representation vs arrow-rs's more general struct/dyn-trait design, not from a different algorithm.

## Maintenance

Actively developed under Apache-2.0 by essentially one maintainer (0.18.2 released 2026-09-19, with frequent minor releases since v0.1.0 in August 2025); it installs from crates.io (about 7.8k downloads, 9 reverse dependencies including the author's lightstream, simd-kernels and minarrow-pyo3) but is nightly-only and pre-1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Benchmarks table (sum of 1,000 integers, averaged over 1,000 runs) lists Minarrow IntegerArray direct 88 ns and via enum 124 ns against arrow-rs Int64Array struct 147 ns and dyn 181 ns. It states the CPU (Intel Core Ultra 7 155H), the compiler (Rust 1.97-nightly) and a release build. The code is public in benches/hotloop_benchmark_avg_std.rs (N=1000, ITERATIONS=1000, harness=false, cast_arrow feature), and its header gives the run command RUSTFLAGS="-C target-cpu=native" cargo bench.
- **Verifier notes:** Every number in the claim is on the page. The record's caveat that the benchmark code "lives in examples" was wrong: it is in benches/ (only the Python roundtrip points to the pyo3 examples), so I corrected it. The fairness caveat about arrow-rs value(i) versus slice iteration is worth keeping. The metadata (Apache-2.0, 100 stars, last commit 2026-09-21, not a fork) all checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/SpaceCell/minarrow>
  - <https://github.com/SpaceCell/minarrow#benchmarks>
  - <https://github.com/SpaceCell/minarrow/blob/main/benches/hotloop_benchmark_avg_std.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/benches/hotloop_benchmark_avg_simd.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/SpaceCell/minarrow>
  - <https://github.com/SpaceCell/minarrow#benchmarks>
  - <https://github.com/SpaceCell/minarrow/blob/main/benches/hotloop_benchmark_avg_std.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/benches/hotloop_benchmark_avg_simd.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/Cargo.toml>
  - <https://github.com/SpaceCell/minarrow/blob/main/.cargo/config.toml>
  - <https://github.com/SpaceCell/minarrow/blob/main/build.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/src/lib.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/src/structs/variants/integer.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/src/structs/buffer.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/src/enums/collections/numeric_array.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/src/enums/array.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/src/ffi/arrow_rs.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/src/ffi/arrow_c_ffi.rs>
  - <https://github.com/SpaceCell/minarrow/blob/main/CHANGELOG.md>
  - <https://github.com/SpaceCell/minarrow/blob/main/CONTRIBUTING.md>
  - <https://github.com/SpaceCell/minarrow/blob/main/.github/workflows/features.yaml>
  - <https://github.com/SpaceCell/minarrow/blob/main/pyo3/README.md>
  - <https://github.com/SpaceCell/minarrow/issues?q=is%3Aissue>
  - <https://github.com/SpaceCell/minarrow/issues/200>
  - <https://github.com/SpaceCell/minarrow/issues/88>
  - <https://github.com/SpaceCell/minarrow/issues/66>
  - <https://github.com/SpaceCell/minarrow/issues/57>
  - <https://github.com/SpaceCell/minarrow/commits/main/.cargo/config.toml>
  - <https://github.com/SpaceCell/minarrow/commits/main/README.md>
  - <https://github.com/SpaceCell/minarrow/commits/main/src/lib.rs>
  - <https://github.com/SpaceCell/minarrow/blob/7e61644/src/lib.rs>
  - <https://github.com/SpaceCell/minarrow/blob/7e61644/Cargo.toml>
  - <https://github.com/SpaceCell/minarrow/blob/08d9b9a/README.md>
  - <https://github.com/apache/arrow-rs/blob/main/arrow-array/src/array/primitive_array.rs>
  - <https://crates.io/api/v1/crates/minarrow>
  - <https://crates.io/api/v1/crates/minarrow/reverse_dependencies>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/minarrow>
  - <https://hn.algolia.com/api/v1/search?query=minarrow&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/spacecell/minarrow`) · [data/wave6/enrich/raw/github_com_spacecell_minarrow.json](../../../data/wave6/enrich/raw/github_com_spacecell_minarrow.json) (enrichment confidence 0.8)

</details>
