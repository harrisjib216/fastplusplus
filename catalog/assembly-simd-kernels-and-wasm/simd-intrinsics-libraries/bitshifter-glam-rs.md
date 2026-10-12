# glam

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust f32/f64 3D game-math crate with SSE2/NEON storage; 2.5x faster Mat4 inverse than cgmath in mathbench.

| | |
|---|---|
| **Beats** | cgmath and nalgebra (scalar Rust linear algebra crates, as measured by mathbench) |
| **Claimed result** | mathbench scalar table, Ryzen 7 3800X, glam 0.34.1: matrix4 inverse 12.1455 ns vs cgmath 30.8124 ns and nalgebra 40.8410 ns (about 2.5x and 3.4x, derived from page data); matrix4 transpose 2.7248 ns vs 7.6718 ns and 7.7156 ns (about 2.8x, derived from page data); matrix4 determinant 4.3934 ns vs 7.1764 ns and 40.9609 ns; vector3 cross 1.0511 ns vs 1.5374 ns and 1.5364 ns; matrix4 mul matrix4 4.4589 ns vs 6.2970 ns and 4.7309 ns. Not faster everywhere: matrix4 mul vector4 x1 2.1002 ns vs nalgebra 1.9185 ns and cgmath 1.9625 ns; matrix2 mul matrix2 1.1531 ns vs cgmath 1.1030 ns; rotation3 mul vector3 x100 347.7 ns vs cgmath 307.8 ns; transform point2/vector2 x100 lose to euclid. |
| **Workload** | mathbench-rs Criterion micro-benchmarks of 3D game math (matrix4 inverse, transpose, determinant, multiply, vector3 cross/dot/normalize) on f32 data, with glam using SSE2 for Vec3A, Vec4, Quat, Mat2, Mat3A and Mat4. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 3800X, Linux |
| **Compiler and flags** | Rust 1.99.0 (b940084d7 2026-09-28), default cargo bench profile (no target-cpu, so SSE2 only on x86_64), command 'cargo bench --features scalar scalar'; tables produced at mathbench-rs commit 8e5467c (2026-10-10) |
| **Adoption** | 2.1k stars, 207 forks; about 158.8M crates.io downloads |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/bitshifter/glam-rs) · [benchmark](https://github.com/bitshifter/mathbench-rs) |

## Verdict

In mathbench-rs (glam's author's Criterion suite, commit 8e5467c, glam 0.34.1, rustc 1.99.0, default bench profile so SSE2 only, AMD Ryzen 7 3800X on Linux), glam's Mat4 inverse took 12.1 ns vs 30.8 ns for cgmath 0.18.0 and 40.8 ns for nalgebra 0.35.0, transpose 2.72 ns vs about 7.7 ns, and determinant 4.39 ns vs 7.18 ns and 40.96 ns, with equal no-op baselines for the 64-byte Mat4 types (3.33-3.39 ns); glam loses or ties on matrix4 mul vector4 x1, matrix2 mul matrix2, rotation3 mul vector3 and the 2D transform rows. The vector3 cross, dot and normalize and the matrix2 wins are smaller than the gap in the per-type no-op baseline (glam's padded Vec3A 1.09 ns vs 1.94-2.18 ns for 12-byte Vector3 types), so they measure type layout, not arithmetic.

## Use it when

- Per-object 3D game or graphics math in Rust (transform hierarchies, camera matrices, physics integration) where you process one Vec3/Mat4/Quat at a time rather than restructuring data into SIMD lanes.
- Code dominated by 4x4 matrix inverse, transpose and determinant, or affine transform inverse: these are the rows where mathbench shows clear wins (Mat4 inverse 12.1 ns vs 30.8 ns cgmath and 40.8 ns nalgebra; transpose 2.7 ns vs about 7.7 ns; Affine3A inverse 6.7 ns vs 20.7-40.6 ns) on equally sized types.
- Arrays of 3D vectors updated in bulk when you can afford the 16-byte padded Vec3A: the euler 3d x10000 workload runs 5.86 us vs about 16.5 us for the 12-byte Vector3 types of cgmath, nalgebra, euclid, vek and ultraviolet.
- Bevy or other Rust engines that already standardise on glam, and no_std or GPU (rust-gpu, CUDA-alignment) targets, which glam supports through the libm, nostd-libm and cuda features.

## Skip it when

- Throughput kernels you can lay out as AoSoA: wide types (ultraviolet f32x8, nalgebra WideF32x8) beat glam's one-vector-at-a-time types by 2-10x in mathbench's own wide table (ray-sphere x80000 25.3 us vs 497.6 us glam).
- Generic or arbitrary-dimension linear algebra (decompositions, NxM matrices, generic scalar types): glam is fixed 2/3/4-dimension only and has no generics; nalgebra covers that space.
- Memory-sensitive storage of millions of 3D vectors or 3x3 matrices: Vec3A and Mat3A carry a padding lane (16 vs 12 bytes, 48 vs 36 bytes), and the 12-byte Vec3/Mat3 types run scalar code and tie the competition (vector3 length row).
- wasm32 builds where speed matters: the README says simd128 passes tests but has never been benchmarked, and it is opt-in via -C target-feature=+simd128.
- C++ projects: it is a Rust crate with no C ABI; the C++ libraries glam ports from (DirectXMath, Realtime Math, GLM) are the native options.

## How it is fast

Vec3A, Vec4, Quat, Mat2, Mat3A, Mat4, Affine2 and Affine3A store each vector or column in one 128-bit register (__m128 on x86, NEON on aarch64, simd128 on wasm), so loads, stores and most operations are single SIMD instructions instead of three or four scalar ones. The hot matrix routines are hand-written shuffle/multiply sequences ported from C++ libraries (ATTRIBUTION.md): Mat4 transpose is DirectXMath's XMMatrixTranspose (four shuffle pairs), and Mat4 determinant and inverse follow GLM's glm_mat4_determinant_lowp and glm_mat4_inverse cofactor schemes with no branch or invertibility check on the default `inverse()` path. The SIMD back-ends use fused multiply-add when the target enables it.

## Compared with alternatives

Pick glam over ultraviolet when your code handles one vector, quaternion or matrix at a time and you want the faster single-lane type; pick ultraviolet (or nalgebra wide types) when you can batch work into AoSoA lanes, where they beat glam 2-20x in the same benchmark suite. The C++ SIMD siblings (EVE, VCL) are general SIMD wrappers, not 3D math types, and serve C++ code.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default (approx, bytemuck, mint, rand, serde, rkyv, speedy, encase, zerocopy, arbitrary, float_eq and libm are optional features) |
| **Minimum toolchain** | Rust 1.85.0, edition 2024 (glam 0.34.x); 0.33.x accepted 1.68.2; core-simd feature needs nightly |
| **Platforms** | any Rust target; SIMD storage on x86 and x86_64 (SSE2, default on x86_64), aarch64 (NEON, default) and wasm32/wasm64 (simd128, opt-in); scalar fallback elsewhere or with the scalar-math feature; no_std via libm |
| **Thread safety** | not documented; all types are plain Copy values with no shared or interior state |
| **Drop-in for the baseline** | no |

## Gotchas

- `Mat4::inverse()` (and the other matrix `inverse` methods) never checks invertibility: a singular or ill-conditioned matrix yields NaN or infinite output silently unless the glam-assert or debug-glam-assert feature is on. Use `try_inverse` or `inverse_or_zero` (added in 0.31.0, 2026-01-21) when inputs can be singular; mathbench still times the unchecked `inverse` against cgmath's `invert` and nalgebra's `try_inverse`, which return Option.
- The speed lives in the padded SIMD types: Vec3A, Mat3A and Affine3A are 16-byte aligned with an unused lane, while Vec3 and Mat3 are plain scalar structs. Component access on SIMD types goes through Deref to internal wrapper structs, so compiler errors mention those wrapper types.
- Results are not bit-identical across builds: the SIMD back-ends use FMA whenever the target enables it (the fast-math feature became a no-op in 0.33.8 and was removed in 0.34.0), and vector min/max NaN propagation differs between SIMD back-ends by design (0.30.2 changelog).
- Pre-1.0 churn: 0.34.0 (2026-10-03) removed the unversioned approx/mint/rand/rkyv/speedy/zerocopy/encase features and long-deprecated look_at/perspective matrix methods and raised the MSRV to 1.85; the old `rkyv` feature was deprecated as unsound in 0.33.11.

## Known shortcomings

- mathbench shootout run by glam's own author; SSE2-only default build; ties or losses on several rows; glam's inverse skips the invertibility check that cgmath and nalgebra perform (they return Option); README tables from mathbench commit 8e5467c predate the 2026-10-11 0.5.0 methodology rewrite. Rust crate, outside the C++ focus.
- Enricher: the mathbench x1 rows time per-type load/store (the padded Vec3A no-op at 1.0859 ns vs 1.94-2.18 ns for a 12-byte Vector3 exceeds the vector3 cross and dot gaps), so the vector3 and matrix2 wins measure type layout rather than arithmetic; glam's Mat4 transpose (2.72 ns) is below its own 3.33 ns no-op; the x100 rows stream a 52 MB Mat4 pool larger than the 32 MB L3; the harness times the unchecked inverse although try_inverse exists since 0.31.0; the Euler 3d 2.8x comes from the Vec3A layout and pathfinder's Vector4F ties; real wins are Mat4 inverse, transpose and determinant and Affine3A inverse.

## Caveats and trade-offs

mathbench is written by glam's author, so the shootout is not independent. Default bench profile is used (no target-cpu=native), so SIMD benefit is limited to SSE2 width. The glam README itself gives no numbers and says wasm SIMD has not been benchmarked. Several rows are ties within 2.5% or small losses (matrix4 mul vector4 x1, matrix2 mul matrix2, rotation3 mul vector3, 2D transforms vs euclid). glam's matrix inverse does not check invertibility while cgmath and nalgebra return an Option, which accounts for part of the inverse gap (mathbench README says so). The README tables are stale relative to the code at HEAD: they were measured at commit 8e5467c (2026-10-10), before the 0.5.0 methodology change of 2026-10-11 (batched operations at sizes 16 and 1024 reported per element, glam Mat3A instead of Mat3 for matrix3 rows, Vec3A for vector3 length and rotation3 rows); later commits only renamed 'return self' rows to 'no-op baseline' and deleted wide rows by hand, so rerunning HEAD gives different row names and per-element numbers. Rust crate, not C++.

128-bit SIMD storage on x86, x86_64, aarch64 and wasm32 for Vec3A, Vec4, Quat, Mat2, Mat3A, Mat4, Affine2 and Affine3A (SSE2 default on x86_64, NEON default on aarch64); padded Vec3A/Mat3A waste space. Rust only; usable from C++ only through FFI.

## Maintenance

Actively maintained (0.34.1 released 2026-10-06, about 159M crates.io downloads, heading for 1.0); MIT OR Apache-2.0 and copyable, but the evidence is a shootout written by glam's author, and the README tables predate mathbench 0.5.0's batched rewrite, so HEAD gives different rows and numbers. Harness findings: the single-op rows time one operation plus a type-dependent load/store per Criterion iteration (glam's matrix4 transpose at 2.72 ns runs below its own 3.33 ns no-op row, and subtracting the no-op from vector3 cross gives a negative cost); the x100 rows at 8e5467c stream a 52 MB Mat4 pool larger than the 32 MB L3, so they are memory-bound; and the 2.8x euler 3d win comes from the 16-byte Vec3A layout, which pathfinder's Vector4F matches (5.852 us).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** mathbench-rs is public Criterion benchmark code (benches/ in bitshifter/mathbench-rs; the README tables come from commit 8e5467c, 2026-10-10) with compiler (Rust 1.99.0 b940084d7), flags (default profile.bench, documented) and CPU (AMD Ryzen 7 3800X, Linux) stated, and it runs glam against cgmath and nalgebra on the same rows. Every quoted number matches the scalar table.
- **Verifier notes:** Numbers verified row by row against the mathbench-rs README; tier A holds because code, compiler, flags and CPU are all public. Shortcomings to record: author-run shootout, SSE2-only default build, mixed results on several rows, unchecked inverse vs Option-returning baselines, and README tables that predate the 2026-10-11 benchmark methodology rewrite (reproduce at commit 8e5467c, not HEAD).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-40 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/bitshifter/mathbench-rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/README.md>
  - <https://github.com/bitshifter/mathbench-rs/commits>
  - <https://github.com/bitshifter/mathbench-rs/commits/master/README.md>
  - <https://github.com/bitshifter/glam-rs>
  - <https://github.com/bitshifter/glam-rs/commits>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/README.md>
  - <https://crates.io/api/v1/crates/glam>
- **Sources the enricher read:**
  - <https://github.com/bitshifter/glam-rs>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/ATTRIBUTION.md>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/src/f32/sse2/mat4.rs>
  - <https://raw.githubusercontent.com/bitshifter/glam-rs/HEAD/src/f32/sse2/vec3a.rs>
  - <https://github.com/bitshifter/glam-rs/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/bitshifter/glam-rs/issues?q=is%3Aissue+performance>
  - <https://github.com/bitshifter/glam-rs/issues/721>
  - <https://crates.io/api/v1/crates/glam>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/README.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/support/macros.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/matrix4.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/vector3.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/eulerbench.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/src/lib.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/benches/matrix4.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/benches/vector3.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/benches/support/macros.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/transform3d.rs>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/bitshifter/glam-rs`) · [data/wave13/enrich/raw/github_com_bitshifter_glam_rs.json](../../../data/wave13/enrich/raw/github_com_bitshifter_glam_rs.json) (enrichment confidence 0.78)

</details>
