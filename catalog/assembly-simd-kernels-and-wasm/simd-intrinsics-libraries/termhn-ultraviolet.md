# ultraviolet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0 OR Zlib` · 🟢 active

> Rust graphics/game linear algebra with SoA 'wide' f32x4/f32x8 types; about 2-5x glam's one-lane code on batched math.

| | |
|---|---|
| **Beats** | glam single-lane types (glam_f32x1) in mathbench; nalgebra wide types tie |
| **Claimed result** | mathbench wide table, Ryzen 7 3800X, RUSTFLAGS -C target-feature=+avx2: ultraviolet_f32x8 vs glam_f32x1: euler 2d x80000 18.94 us vs 41.87 us (about 2.2x), euler 3d x80000 28.54 us vs 58.97 us (about 2.1x), matrix4 determinant x16 14.6545 ns vs 62.0342 ns (about 4.2x), vector3 normalize x16 7.3365 ns vs 35.2002 ns (about 4.8x), all ratios derived from page data; nalgebra_f32x8 is equal or within noise. The ray-sphere intersection x80000 row (25.26 us vs 497.6 us, about 20x) is struck: in benches/ray_sphere_intersect.rs (commit 8e5467c and still at HEAD) the wide ultraviolet and nalgebra kernels set ray_o to the zero vector (the sphere centre) so every lane hits and returns t = 10, while the glam_f32x1 baseline uses ray_o = (0, 0, -11) with random directions, so its hit/miss branches depend on the data; comparing per-element rates across the harness's own tables (scalar 13.37 us per 10,000 vs wide 25.26 us per 80,000) gives about 4.2x (derived from page data). Not faster everywhere: glam_f32x1 wins matrix4 transpose x16 and ties matrix4 mul matrix4 x16; ultraviolet_f32x4 is slower than glam on matrix2 and matrix3 transpose x16; gains shrink to ties at x256 sizes. |
| **Workload** | mathbench-rs 'wide' benchmarks processing batches of 16 to 80000 elements with structure-of-arrays f32x4 and f32x8 types: euler rotations, ray-sphere intersection, matrix4 determinant/inverse/multiply, vector3 cross/dot/normalize. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X, Linux |
| **Compiler and flags** | Rust 1.99.0 (b940084d7 2026-09-28), RUSTFLAGS='-C target-feature=+avx2' cargo bench --features wide wide; ultraviolet 0.10.0; tables produced at mathbench-rs commit 8e5467c (2026-10-10) |
| **Adoption** | 800 stars; about 1.35M crates.io downloads |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/fu5ha/ultraviolet) · [benchmark](https://github.com/bitshifter/mathbench-rs) |

## Verdict

mathbench-rs wide table (glam's author's shootout, mathbench commit 8e5467c, Rust 1.99.0, RUSTFLAGS=-C target-feature=+avx2, AMD Ryzen 7 3800X, Linux; ultraviolet 0.10.0, glam 0.34.1, nalgebra 0.35.0): ultraviolet_f32x8 ran Euler integration at 80,000 elements about 2.1-2.2x faster than glam's one-lane Vec2/Vec3A loop, matrix4 determinant x16 about 4.2x and vector3 normalize x16 about 4.8x faster, and stayed close to nalgebra_f32x8 (ties on Euler and ray-sphere). The 20x ray-sphere row compares different inputs (see gotchas); the like-for-like per-element rate gives about 4.2x.

## Use it when

- Batched game and graphics math (particle Euler integration, ray-primitive tests, transforming thousands of points) where you can store data as AoSoA blocks of 4 or 8
- Branch-heavy per-element tests (ray-sphere, culling) that turn into mask-and-select code and would otherwise mispredict
- x86-64 builds that can use -C target-feature=+avx2 (or target-cpu) for the 8-lane types; 4-lane types work on baseline SSE2 and on aarch64 NEON
- Projects that want rotors and fast compiles with no generics in the API

## Skip it when

- Single-object or AoS code: in mathbench's scalar table ultraviolet's scalar types mostly tie glam and are slower on several rows (for example matrix3 determinant 10.42 ns vs glam 2.19 ns), so use glam there
- Matrix-heavy kernels with few objects: glam's one-lane Mat4 beats ultraviolet_f32x8 on matrix4 transpose x16 (73.5 vs 96.3 ns), ties matrix4 multiply x16, and most x256 rows are ties
- Binaries that must pick AVX2 at runtime: wide only detects SIMD at build time, so a portable binary gets SSE2 paths, and an AVX2 build crashes on older CPUs
- If you already use nalgebra: its simba WideF32x8 types are close (ties on Euler and ray-sphere, nalgebra ahead on matrix4 transpose x16 at 87.0 vs 96.3 ns, ultraviolet ahead on vector3 normalize x16 at 7.34 vs 8.54 ns and matrix4 multiply x256), though nalgebra has no wide determinant or inverse rows in mathbench
- Code that needs integer i64 vectors, projective geometric algebra or Euler-angle extraction from rotors: open feature requests #101, #64/#65 and #44

## How it is fast

Vertical SIMD (AoSoA): each component of a Vec3x8 is one f32x8 register, so one vector instruction does the same operation for 8 objects and there are no horizontal shuffles. That is the batching idea behind ISPC and nalgebra's simba wide types. Branchy scalar code becomes branchless lane masks (simd_gt, then select/blend), which avoids branch mispredictions on data-dependent tests. The SIMD comes from the 'wide' crate (safe_arch intrinsics on SSE2/AVX/AVX2, NEON and wasm simd128, with a scalar fallback elsewhere).

## Compared with alternatives

Pick it over glam when your hot loop can process objects in blocks of 4 or 8 and you want ready-made wide vector, matrix and rotor types instead of hand-written intrinsics; nalgebra's wide types are equally fast, so the choice there is API taste. Unlike the C++ SIMD siblings (EVE, VCL, ISPC), it is a Rust-only domain library for 2D/3D math, not a general SIMD wrapper.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wide (0.7 in released 0.10.0, 1.7 at unreleased HEAD 0.11.0); optional serde, mint, bytemuck, num-traits, encase |
| **Minimum toolchain** | 0.10.0: edition 2018, rust-version not declared; HEAD 0.11.0: edition 2024 and wide 1.7, which requires Rust 1.89 |
| **Platforms** | any Rust target; explicit SIMD on x86/x86-64 (SSE2 by default, AVX/AVX2 only when enabled at build time), aarch64 NEON, wasm32 with +simd128; scalar fallback elsewhere |
| **Thread safety** | not documented; the types are plain Copy value structs with no shared state |
| **Drop-in for the baseline** | partial: the scalar types cover the same ground as glam, but the speedup only comes from the wide types, which need a data layout change and branchless rewrites |

## Gotchas

- Harness flaw behind the headline \~20x ray-sphere ratio: in mathbench-rs benches/ray_sphere_intersect.rs (commit 8e5467c and still at HEAD) the wide ultraviolet and nalgebra kernels set ray_o to the zero vector, the sphere's centre, so every lane hits and returns t = 10, while the glam_f32x1 baseline uses ray_o = (0, 0, -11) with random directions, so its hit/miss branches depend on the data. The README's claim that glam 'produces the same outputs that the wide versions would' does not hold for this row. Against the scalar table's per-element rate (13.3-13.37 us per 10,000 for every library), ultraviolet_f32x8 at 25.26 us per 80,000 is about 4.2x faster, not 20x (derived from page data).
- The wide unop/binop harness calls std::hint::black_box on every result, so the one-lane glam rows pay 16 barriers per batch of 16 against 2 for the 8-lane rows; this probably inflates the small-op ratios (vector3 normalize, determinant) somewhat.
- The comparison traits (CmpGt and the rest) used by the README's ray-sphere example are not re-exported (open issue #132); you have to depend on wide directly and match its version. HEAD renames blend to select as part of the wide 1.7 migration, which breaks 0.10 code.
- The README and lib.rs docs are stale: they say f64 and integer types are off by default, but Cargo.toml enables int and f64 by default, and the 'projective geometric algebra' features they mention are not implemented (#64, #65). The README's Vec3x8 setup example iterates over empty vectors while pushing to them. No license text files are in the repo (#154); the licence is declared only in Cargo.toml.

## Known shortcomings

- Wins mostly from SoA batching against one-lane glam_f32x1; ties nalgebra f32x8; glam wins matrix4 transpose x16; the ray-sphere 20x row is anomalous; no licence text file (licence only in Cargo.toml); the repo moved to fu5ha/ultraviolet. Rust crate, outside the C++ focus.
- Harness flaw in mathbench-rs benches/ray_sphere_intersect.rs (commit 8e5467c and still at HEAD): the wide ultraviolet and nalgebra kernels use ray_o = zero (the sphere centre), so every lane hits and gets t = 10, while the glam_f32x1 baseline uses ray_o = (0, 0, -11) with random directions, so its branches depend on the data; the \~20x row compares different inputs and the README's 'same outputs' claim is false for it; the like-for-like per-element rate (scalar table 13.37 us per 10,000 vs 25.26 us per 80,000) is about 4.2x (derived). Per-result black_box calls bias the small-op rows toward the wide types. Stale docs (int and f64 are on by default; projective GA #64/#65 unimplemented), Cmp traits not re-exported (#132), AVX2 is build-time only.

## Caveats and trade-offs

The comparison is against glam's one-lane scalar type doing the same amount of work, so the large ratios mostly measure SoA batching, not a better library; nalgebra's f32x8 types match ultraviolet, and glam_f32x1 still wins matrix4 transpose x16 and ties matrix4 mul matrix4 x16, while ultraviolet_f32x4 is slower than glam on matrix2 and matrix3 transpose x16. Gains shrink to ties at x256 sizes. In mathbench's scalar table ultraviolet wins outright only the matrix2 and matrix3 transpose rows. The ray-sphere ratio (about 20x for 4-8 lanes) suggests the glam_f32x1 path is unusually slow on that row: 497.6 us for x80000 is about 4.7x glam's own scalar-table rate of 13.37 us per x10000 (derived from page data). mathbench is written by glam's author. The tables predate mathbench 0.5.0 (2026-10-11 rewrite to batched per-element throughput at sizes 16 and 1024; wide 'return self' rows were deleted by hand), so HEAD does not reproduce the exact rows. The repository has moved to github.com/fu5ha/ultraviolet (Cargo.toml and crates.io still name termhn). No license text file exists in the repo (LICENSE, LICENSE-MIT, LICENSE-APACHE, LICENSE-ZLIB all 404); the MIT OR Apache-2.0 OR Zlib expression is only in Cargo.toml and crates.io metadata. HEAD is 0.11.0 (breaking migration to wide 1.7, unreleased; crates.io max is 0.10.0 from 2025-04-26); the benchmark used 0.10.0. Rust crate, not C++. [retier] The comparison is against glam's one-lane scalar type doing the same amount of work, so the ratios mostly measure SoA batching, not a better library; nalgebra's f32x8 types match ultraviolet. Harness flaw: the ray-sphere row compares different inputs (wide kernels all-hit at the sphere centre, glam baseline random directions), so the README's statement that glam 'produces the same outputs' is false for that row. The wide unop/binop harness calls std::hint::black_box on every result, so the one-lane glam rows pay 16 barriers per batch of 16 against 2 for the 8-lane rows, which probably inflates the small-op ratios (vector3 normalize, determinant). In mathbench's scalar table ultraviolet wins outright only the matrix2 and matrix3 transpose rows. The comparison traits (CmpGt and the rest) used by the README's ray-sphere example are not re-exported (open issue #132); HEAD renames blend to select (wide 1.7 migration); AVX2 width is chosen at build time. The README and lib.rs docs are stale (int and f64 features are on by default; the projective geometric algebra features are not implemented, #64/#65); no license text files are in the repo (#154).

Requires an SoA/AoSoA data layout (wide f32x4 and f32x8 types) rather than ordinary Vec3 structs; AVX2 must be enabled explicitly at build time. Rust only.

## Maintenance

Active but slow-moving: 0.10.0 (2025-04-26) is the latest release, HEAD (2026-10-04) carries an unreleased breaking wide 1.7 migration, and the repo moved from termhn to fu5ha; triple-licensed MIT/Apache-2.0/Zlib (declared in Cargo.toml only), widely used (about 1.35M crates.io downloads) and copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** mathbench-rs wide benchmarks are public code (benches/ in bitshifter/mathbench-rs, tables from commit 8e5467c) with compiler (Rust 1.99.0), flags (RUSTFLAGS='-C target-feature=+avx2', default bench profile) and CPU (AMD Ryzen 7 3800X) stated, comparing ultraviolet wide types against glam doing the same work with one lane and against nalgebra's wide types. All quoted numbers match the wide table.
- **Verifier notes:** Numbers verified against the mathbench-rs wide table; tier A stays. Repo moved to fu5ha/ultraviolet: consider a repo_url override. Shortcomings to record: wins mostly measure SoA batching vs one-lane glam, ties with nalgebra wide, glam wins matrix4 transpose x16, anomalous glam ray-sphere row, author-run shootout with tables predating the 0.5.0 methodology, license declared only in Cargo.toml.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-40 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/bitshifter/mathbench-rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/README.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/CHANGELOG.md>
  - <https://github.com/bitshifter/mathbench-rs/commits/master/README.md>
  - <https://github.com/termhn/ultraviolet>
  - <https://github.com/fu5ha/ultraviolet/commits>
  - <https://raw.githubusercontent.com/termhn/ultraviolet/HEAD/README.md>
  - <https://raw.githubusercontent.com/fu5ha/ultraviolet/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/ultraviolet>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/fu5ha/ultraviolet/HEAD/README.md>
  - <https://raw.githubusercontent.com/fu5ha/ultraviolet/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/fu5ha/ultraviolet/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/fu5ha/ultraviolet/HEAD/src/lib.rs>
  - <https://github.com/fu5ha/ultraviolet>
  - <https://github.com/fu5ha/ultraviolet/issues>
  - <https://github.com/fu5ha/ultraviolet/issues/132>
  - <https://github.com/fu5ha/ultraviolet/commits>
  - <https://crates.io/api/v1/crates/ultraviolet>
  - <https://crates.io/api/v1/crates/ultraviolet/0.10.0/dependencies>
  - <https://github.com/bitshifter/mathbench-rs/tree/8e5467c/benches>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/README.md>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/ray_sphere_intersect.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/eulerbench.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/matrix4.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/vector3.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/8e5467c/benches/support/macros.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/benches/ray_sphere_intersect.rs>
  - <https://raw.githubusercontent.com/bitshifter/mathbench-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/Lokathor/wide/HEAD/README.md>
  - <https://crates.io/api/v1/crates/wide>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/termhn/ultraviolet`) · [data/wave13/enrich/raw/github_com_termhn_ultraviolet.json](../../../data/wave13/enrich/raw/github_com_termhn_ultraviolet.json) (enrichment confidence 0.75)

</details>
