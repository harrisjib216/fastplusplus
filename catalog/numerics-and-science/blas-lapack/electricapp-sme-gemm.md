# sme-gemm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust crate of hand-written Apple M4/M5 SME GEMM kernels; edges out Accelerate sgemm/dgemm at mid-to-large sizes.

| | |
|---|---|
| **Beats** | Apple Accelerate (cblas_sgemm, which may use AMX); also candle and burn |
| **Claimed result** | Unpacked strided GEMM vs Accelerate on Apple M5, TF/s: f32 512^3 1.97 vs 1.61, 1024^3 2.34 vs 2.03, 4096^3 2.14 vs 2.07, 4096x512x512 2.29 vs 1.94, 16384x512x512 2.30 vs 2.00; Accelerate leads at 256^3 (1.50 vs 1.67) and 2048^3 (2.04 vs 2.14). f64 ahead at every shape: 256^3 0.46 vs 0.44, 512^3 0.58 vs 0.46, 1024^3-4096^3 0.55 vs 0.52, tall shapes 0.61 vs 0.52. f16 (Accelerate has no f16 path; compared with upcast + sgemm + downcast): 1024^3 3.83 vs 1.40, 2048^3 4.32 vs 1.70, 4096x11008x4096 3.32 vs 1.89. Dispatch latency (us/call, f32): Accelerate cblas_sgemm is faster at every square size 8^3-256^3 (e.g. 128^3 3.2 vs 7.9 packed SME); packed SME wins the 1x4096x4096 decode shape (634 vs 836). |
| **Workload** | Unpacked strided GEMM TF/s on an Apple M5 for f32, f16 and f64 across 256^3 to 4096^3 and rectangular shapes, via examples/vs_accelerate, vs_candle and vs_burn. |
| **Metric** | throughput |
| **Hardware** | Apple M5 (SVL=512, P- and E-cluster SME units), best-of-N |
| **Compiler and flags** | C kernels (csrc/, arm_sme.h) built by build.rs through the cc crate with -mcpu=apple-m4 -ffp-contract=fast -O3; M5-only TUs add +sme-f16f16/+sme-b16b16/+sme-f64f64/+sme-i16i64 target features behind a runtime probe. Rust release profile opt-level=3, lto="thin"; rust-version 1.97 (MSRV). Apple clang and rustc versions not stated. examples/vs_accelerate.rs: 3 warm-up calls each plus a 60-call clock warm-up, then 12 interleaved passes of 40 iterations (4 for large shapes), best per-call time kept for both backends. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/electricapp/sme-gemm) · [benchmark](https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/README.md) |

## Verdict

First-party README tables from examples/vs_accelerate.rs on an Apple M5 (interleaved best-of-12 rounds, row-major no-transpose cblas_sgemm/cblas_dgemm writing preallocated C): f32 1.97 vs 1.61 TF/s at 512^3, 2.34 vs 2.03 at 1024^3, 2.14 vs 2.07 at 4096^3, but behind at 256^3 (1.50 vs 1.67) and 2048^3 (2.04 vs 2.14); f64 ahead at every shape (0.46-0.61 vs 0.44-0.52 TF/s). Kernels built with -mcpu=apple-m4 -ffp-contract=fast -O3 and Rust opt-level 3 with thin LTO; Apple clang and rustc versions not stated.

## Use it when

- Rust code on Apple M4/M5 doing f32 GEMM in the 512^3 to 4096^3 range or tall-skinny shapes like 4096x512x512, where the README shows 1.03-1.22x over Accelerate cblas_sgemm on an M5.
- f16/bf16 inference on M4/M5 from Rust, where Accelerate has no half-precision GEMM: about 2.3-2.8x over an upcast-to-f32 Accelerate path at 1024^3-4096^3, and native 16-bit accumulate on M5.
- Inference layers that want GEMM plus bias/activation/dequant fused into one pass (README: fused bias+relu adds 5-27% to GEMM time, while the separate bias+relu row is 4-12x the GEMM time), int8/int16 GEMM, or 4-bit weights with a 4x smaller resident weight set.
- Single-row decode shapes (1x4096x4096) against resident pre-packed weights, where packed SME measured 634 us vs 836 us for Accelerate.
- f64 GEMM on an M5 specifically (0.46-0.61 vs 0.44-0.52 TF/s for Accelerate cblas_dgemm, ahead at every measured shape).

## Skip it when

- Small matrices or latency-bound calls: Accelerate cblas_sgemm has lower per-call time at every square size from 8^3 to 256^3 (e.g. 3.2 vs 7.9 us at 128^3), and below a flop floor (2^18, or 2^12 when m\*n&gt;=8) the crate runs its scalar reference at about 1 GFLOP/s.
- f64 or i16 on an M4: those kernels need M5 features (FEAT_SME_F64F64, FEAT_SME_I16I64), so on M4 matmul_f64 silently falls back to the scalar reference, far slower than Accelerate dgemm.
- Anything that is not macOS on Apple M4+ (Intel Macs, M1-M3, Linux/Windows aarch64, x86): no SME path, only the scalar fallback.
- C/C++/Fortran code expecting a BLAS ABI, or Rust projects needing a crates.io release: there is no CBLAS interface, the crate is not on crates.io (404), and it needs Rust 1.97 (edition 2024) plus Apple clang 16+.
- Production use needing maturity: first commit August 2026, 10 commits, 0 stars, no releases; the f32 win over Accelerate is small and mixed (Accelerate leads at 256^3 and 2048^3).

## How it is fast

Kernels are C against arm_sme.h running in SME streaming mode with SVL=512: each output tile is accumulated in the 4 KB ZA array by outer-product MOPA instructions, two ZA tiles kept in lockstep so consecutive MOPAs do not collide. Because Apple has one SME unit per CPU cluster rather than per core, M-tile (or, for flat decode shapes, N-tile) chunks are spread over both the P- and E-cluster units with GCD dispatch_apply and work-stealing from an atomic cursor. Large problems use BLIS-style jc/ic blocking sized to the E-cluster L2, A is packed through ZA transposes while cache-resident, and small-B problems skip packing and load B directly.

## Compared with alternatives

Pick sme-gemm when you are in Rust on an M4/M5 and need half-precision, int8/int16 or 4-bit GEMM with fused epilogues; for f32/f64 against Accelerate, MTGEMM-A reports a larger 1.18x f32 geomean over 24 workloads and apple-bottom targets DGEMM, while MPGEMM reports 1.23x average over Accelerate on SME.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | half; build-time cc crate and an Apple clang 16+ (Xcode 16) that accepts -mcpu=apple-m4, linking clang_rt.osx from the same toolchain; optional candle-core 0.11, burn 0.21, ort 2.0.0-rc.13 for adapters/benchmarks |
| **Minimum toolchain** | Rust 1.97 (MSRV, edition 2024); Apple clang 16 / Xcode 16 for the C kernels |
| **Platforms** | macOS aarch64 on Apple M4+ for SME (f64, i16, native f16/bf16 accumulate and Q4 need M5); scalar reference fallback elsewhere |
| **Thread safety** | Safe to call from multiple threads: per-thread scratch buffers, capabilities cached in a OnceLock, and tests/concurrency.rs checks bit-identical results from many threads sharing one pre-packed B; but each call already uses both clusters' SME units, so concurrent calls contend for the same two units |
| **Drop-in for the baseline** | no |

## Gotchas

- Native f16/bf16 accumulate (Accum::F16/Bf16, M5) is about 2x the widening rate but its error grows about sqrt(K); a mismatched or unsupported Accum silently falls back to F32.
- The fused relu/gelu/silu/tanh/sigmoid shortcuts share one in-register rational tanh with about 4e-2 error, visible on a bare .tanh() or .sigmoid(); scalar-divisor DIV is a reciprocal multiply about 1 ULP off (ARCHITECTURE.md section 6).
- Integer SMOPA accumulation wraps silently on overflow (the oracle uses wrapping adds to match).
- Benchmarks are best-of-N with constant-valued inputs (0.01/0.02), the f32 bench has no packed entry point, and some f16 cells in the comparison table come from the candle adapter or the inference_value example rather than vs_accelerate.

## Known shortcomings

- Off-category baseline (Apple Accelerate); f32 wins are mixed and Accelerate has lower per-call latency up to 256^3; the large f16 margin is against an upcast path; no clang or rustc version stated; kernels are C with Rust bindings.
- f64/i16 on M4 silently fall back to a scalar reference (\~1 GFLOP/s); not on crates.io; wins only 1.03-1.22x on f32.

## Caveats and trade-offs

Baseline is Apple Accelerate, not OpenBLAS/MKL/Eigen/BLIS, so it is off the category's usual incumbents (Accelerate may itself use the SME/AMX unit). Wins are small and mixed for f32 (Accelerate leads at 256^3 and 2048^3, and has lower per-call latency for every size up to 256^3); f64 margins are 5-26%; the large f16 margin is against an upcast-to-f32 path because Accelerate has no f16 GEMM. Some f16 cells come from the candle adapter or the inference_value example rather than vs_accelerate. Apple Silicon M4+ on macOS only (scalar reference fallback elsewhere); the kernels are C behind Rust bindings and use both the P- and E-cluster SME units via GCD. First-party, best-of-N timing, constant-valued inputs, brand-new repo (first commit 2026-08-03) with 0 stars.

Rust crate of hand-written SME kernels for Apple M4 and newer (f16/bf16/f32/f64, i8/i16, 4-bit weights), fused epilogues, batched and pre-packed GEMM, flash attention. Rust-only API, not a BLAS ABI. Native f16 accumulation changes numerical behavior (error grows about sqrt(K)).

## Maintenance

Brand-new (first commit 2026-08-03, last 2026-09-30), single-author, active, 0 stars, not on crates.io; Apache-2.0 OR MIT, with a strict lint setup and 169 tests (oracle, proptest, guard-page, concurrency) that make it reasonable to vendor as a git dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables vs Apple Accelerate cblas_sgemm/cblas_dgemm on a named CPU (Apple M5) with public benchmark code (examples/vs_accelerate.rs, interleaved best-of-12) and flags in build.rs (-mcpu=apple-m4 -ffp-contract=fast -O3) and Cargo.toml (opt-level 3, thin LTO), but neither the Apple clang nor the rustc version is stated (only MSRV 1.97), so not A under the rustc-version precedent.
- **Verifier notes:** All record numbers appear in the README's 'vs. other backends' table; claimed_speedup extended with the other shapes, f64 rows and the dispatch-latency table where Accelerate wins small sizes. The benchmark is fair in shape (both write preallocated C, interleaved rounds). Kernels are C (csrc/\*.c with arm_sme.h) wrapped in a Rust crate, so the language field could read 'C, Rust'. Apache-2.0 OR MIT, 0 stars, last commit 2026-09-30 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/electricapp/sme-gemm>
  - <https://github.com/electricapp/sme-gemm/commits>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/examples/vs_accelerate.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/build.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/LICENSE-MIT>
- **Sources the enricher read:**
  - <https://github.com/electricapp/sme-gemm>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/build.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/examples/vs_accelerate.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/src/probe.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/src/kernels/f64.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/src/kernels/f32.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/src/exec/guard.rs>
  - <https://raw.githubusercontent.com/electricapp/sme-gemm/HEAD/tests/concurrency.rs>
  - https://crates.io/api/v1/crates/sme-gemm (404, not published)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/electricapp/sme-gemm`) · [data/wave8/enrich/raw/github_com_electricapp_sme_gemm.json](../../../data/wave8/enrich/raw/github_com_electricapp_sme_gemm.json) (enrichment confidence 0.85)

</details>
