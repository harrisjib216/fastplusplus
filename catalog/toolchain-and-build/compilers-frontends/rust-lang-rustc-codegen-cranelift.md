# rustc_codegen_cranelift (cg_clif)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compilers and front ends](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Drop-in Cranelift codegen backend for rustc that replaces LLVM to cut debug-build compile times.

| | |
|---|---|
| **Beats** | rustc |
| **Claimed result** | rustc-perf wall time, cg_clif vs cg_llvm (Nov 2024 nightly, after rustc allowed lld with non-LLVM backends): 'most benchmarks being 10-50% faster'; a couple of secondary (pathological) benchmarks still regressed. Earlier 2020 run (issue #878, debug profile): clean and baseline-incremental builds about 10-60% faster (often about 40%), but clean-incremental builds much slower (up to about 200%) because object files were not cached. |
| **Workload** | Debug-mode cargo builds using the Cranelift codegen backend in place of rustc's default LLVM backend |
| **Metric** | compile-time |
| **Adoption** | 2.1k stars; distributed as an official rustup component (rustc-codegen-cranelift-preview) for nightly Rust |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/rust-lang/rustc_codegen_cranelift) · [benchmark](https://bjorn3.github.io/2024/11/14/progress-report-nov-2024.html) |

## Verdict

First-party numbers only. bjorn3's Nov 2024 progress report says that on the rustc-perf suite, after enabling lld for non-LLVM backends, cg_clif was '10-50% faster' than cg_llvm on most benchmarks, with a couple of pathological benchmarks still regressed; no hardware, exact rustc version, or raw data are given. Separately, issue #878 (2020) reported debug-profile clean and baseline-incremental builds about 10-60% faster (often \~40%) versus cg_llvm, but clean-incremental builds up to \~200% slower due to uncached object files.

## Use it when

- Local dev-loop cargo build/cargo check cycles where debug binaries are compiled and rerun repeatedly and compile latency matters more than runtime speed
- Projects already on Rust nightly, running on Linux, macOS, or x86_64 Windows
- Codebases that avoid heavy std::arch SIMD intrinsics and unwinding-based panic handling (or already build with -Cpanic=abort)
- Willing to opt in per-profile via Cargo.toml/.cargo/config.toml so only the debug profile uses cg_clif
- Crates that hit an unsupported feature can fall back to the default LLVM backend without any code change

## Skip it when

- Release/optimized builds -- cg_clif is not a target here and produces slower-running code than LLVM -O
- Code leaning on std::arch SIMD intrinsics beyond the partially-supported subset (std::simd portable SIMD does work fully)
- Programs that unwind on panic when targeting Windows or macOS -- unwinding support there is experimental and unsupported
- Crates with 'pathological' codegen shapes -- the Nov 2024 report notes a few secondary benchmarks still regress vs cg_llvm
- Anyone who needs stable (non-nightly) Rust, since it's only distributed for nightly via rustup

## How it is fast

Cranelift is a simpler, JIT-oriented code generator with far less optimization machinery than LLVM, so it spends much less time per function translating MIR to machine code, trading away optimized codegen quality that doesn't matter for debug builds. The Nov 2024 progress report attributes the bulk of the observed win to switching the link step to lld for non-LLVM backends (rust-lang/rust PR #132774) and to adding a BufWriter around object-file writes, which fixed a specific regression on the 'coercions' rustc-perf benchmark.

## Compared with alternatives

The catalogued siblings (zapcc, MIR/c2m, TinyCC) all target C/C++ toolchains; cg_clif is the only Rust-ecosystem entry here, so it's the pick whenever the baseline being replaced is rustc/cargo rather than gcc/clang.

## Integration

| | |
|---|---|
| **Form** | compiler backend, distributed as a rustup component and loaded via -Zcodegen-backend |
| **Dependencies** | none for the user; Cranelift is pulled in by the backend itself |
| **Minimum toolchain** | Rust nightly (requires the unstable -Zcodegen-backend / codegen-backend cargo feature) |
| **Platforms** | Linux x86-64/AArch64/RISC-V/s390x, macOS x86-64/AArch64, Windows x86-64 (fully tested per README matrix); FreeBSD and some Linux targets are unverified |
| **Thread safety** | not documented (this is a compiler backend, not a concurrent data structure) |
| **Drop-in for the baseline** | partial -- explain: no source changes to the crate being compiled, but requires nightly Rust plus an explicit opt-in (CARGO_PROFILE_DEV_CODEGEN_BACKEND=cranelift or an equivalent Cargo.toml/.cargo/config.toml setting), and is meant for the debug profile only |

## Gotchas

- -Cpanic=abort is enabled by default because stack unwinding is experimental and unsupported on Windows/macOS
- std::arch SIMD intrinsics are only partially supported; std::simd portable SIMD is fully supported
- 2020 measurements (issue #878) showed clean-incremental builds up to \~200% slower because compiled object files were not cached in the incremental cache (#760); the Nov 2024 report does not say whether this was fixed
- JIT mode requires all dependencies to be available as dynamic libraries and lacks incremental compilation, so it can be slower than normal AOT builds

## Caveats and trade-offs

First-party figures only, read from blog/issue prose. The underlying result tables are images, and no hardware, nightly version or raw data are given. The Nov 2024 report does not state the build profile, though cg_clif targets debug builds. Issue #878's 2020 numbers are stale, and there the maintainer points to the Nov 2024 report as the latest results. Regressions remain on some stress-test benchmarks, and slower linking dominated some 2020 results. Release/optimized builds are not a target.

No SIMD support beyond std::simd (std::arch only partial), unwinding-on-panic is experimental and unsupported on Windows/macOS, recommended for debug builds only, still marked experimental overall

## Maintenance

Actively maintained (commit as of 2026-09-23) and distributed as an official nightly-only rustup component, but still labeled experimental overall; MIT/Apache-2.0 dual-licensed and adopted by adding a build flag rather than vendoring a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D. In his Nov 2024 progress report, the maintainer (bjorn3) says that on the rustc-perf suite, after lld was enabled for non-LLVM backends, 'most benchmarks [were] 10-50% faster' than cg_llvm. Issue #878 (2020) gives debug-build figures of about 10-60% (often about 40%) with the rustc-perf patch. Both are first-party numbers without hardware or version details, so C.
- **Verifier notes:** Numbers do exist: issue #878 has them in its body text, and the maintainer's Nov 2024 progress report (linked from #878 as 'latest results') has more. So the tier moves from D to C, and benchmark_url is set to that report. The repo is dual-licensed MIT/Apache-2.0 (LICENSE-MIT and LICENSE-APACHE, and the README says so); GitHub shows only Apache-2.0. Other metadata checked: 2141 stars, last commit 2026-09-23, and the README confirms the rustup rustc-codegen-cranelift-preview component.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rust-lang/rustc_codegen_cranelift>
  - <https://github.com/rust-lang/rustc_codegen_cranelift/blob/master/README.md>
  - <https://github.com/rust-lang/rustc_codegen_cranelift/issues/878>
  - <https://bjorn3.github.io/2024/11/14/progress-report-nov-2024.html>
- **Sources the enricher read:**
  - <https://github.com/rust-lang/rustc_codegen_cranelift>
  - <https://github.com/rust-lang/rustc_codegen_cranelift/blob/master/README.md>
  - <https://github.com/rust-lang/rustc_codegen_cranelift/blob/master/docs/usage.md>
  - <https://github.com/rust-lang/rustc_codegen_cranelift/issues/878>
  - <https://bjorn3.github.io/2024/11/14/progress-report-nov-2024.html>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/rust-lang/rustc_codegen_cranelift`) · [data/wave2/enrich/raw/github_com_rust_lang_rustc_codegen_cranelift.json](../../../data/wave2/enrich/raw/github_com_rust_lang_rustc_codegen_cranelift.json) (enrichment confidence 0.4)

</details>
