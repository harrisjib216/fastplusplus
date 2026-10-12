# Constantine (inline x86-64 assembly field arithmetic)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Nim (C, Rust and Go bindings; x86-64 inline assembly emitted by Nim macros)` · `MIT OR Apache-2.0` · 🟢 active

> Constant-time pairing-curve cryptography in Nim whose macro-generated x86-64 MULX/ADCX/ADOX inline assembly beats its own compiler-built field arithmetic.

| | |
|---|---|
| **Beats** | the same big-integer / finite-field code compiled without assembly (CTT_ASM=0) by GCC and Clang |
| **Claimed result** | 'The speed improvement on finite field arithmetic is up 60% with MULX, ADCX, ADOX on BLS12-381 (6 limbs)'; '2.4x perf ratio between using plain GCC vs GCC with inline assembly'; Clang/MSVC/ICC generate code 'up to 20\~25% faster than GCC' for add-with-carry code |
| **Workload** | finite field arithmetic on BLS12-381 (6 limbs) and elliptic-curve primitives using MULX, ADCX and ADOX carry chains that compilers cannot generate |
| **Metric** | throughput |
| **Hardware** | No CPU named for the asm-versus-compiler statements; the charts in README-PERFORMANCE.md are Constantine-only runs on an AMD Ryzen 7 7840U (Zen 4; EVM precompiles, KZG, BLS signatures, BLS12-381 summary and MSM) and an i9-9980XE (BN254 MSM), none with an assembly-off comparison |
| **Compiler and flags** | CC=clang nimble bench_\* recommended; GCC used for the 2.4x comparison; compiler versions not stated. The release flags set no -march, -mbmi2 or -madx, so the CTT_ASM=0 (no-assembly) build cannot use MULX at all; the asm kernels are 'asm volatile' with a 'memory' clobber. |
| **Adoption** | 500 stars |
| **Last commit** | 2026-08-04 |
| **Links** | [repository](https://github.com/mratsim/constantine) · [benchmark](https://github.com/mratsim/constantine/blob/master/README-PERFORMANCE.md) |

## Verdict

First-party prose only, in README-PERFORMANCE.md: MULX/ADCX/ADOX assembly is 'up 60%' faster for BLS12-381 (6-limb) field arithmetic and '\~60% faster than Clang', and there is a '2.4x perf ratio' between plain GCC and GCC with inline asm. No CPU, compiler version, table or run log stands behind these figures, and the same file's GCC-versus-Clang figures disagree (up to 2x, \~50%, 20-25%). The published charts (Ryzen 7 7840U; i9-9980XE for BN254 MSM) show asm-on Constantine timings only. The nimble bench tasks can reproduce an on/off pair (outputs are suffixed _asmIfAvailable or _noAsm via CTT_ASM=0), subject to the harness caveats above.

## Use it when

- Ethereum consensus or execution clients and provers that need constant-time BLS12-381 or BN254 primitives (BLS signatures, KZG for EIP-4844, EIP-2537 and BN254 precompiles) on x86-64 servers with ADX and BMI2 (Broadwell or Zen and later).
- Builds that must use GCC: the asm path removes most of GCC's carry-handling penalty, and the first-party figure is 2.4x for GCC with inline asm over plain GCC.
- Rust, Go or C projects that want a pairing-curve backend with no runtime dependencies (GMP is only used in tests).
- Many-core MSM and batched KZG verification, where its threadpool runs nested parallel loops (three parallel MSMs, each with three nested parallel loops, for batch KZG verification).

## Skip it when

- When you need an audited or stable library. The README carries an 'experimental' badge and says the library is provided as-is, without guarantees, at least until it is audited and formal proofs exist.
- When you need evidence that the assembly pays off on your platform. No asm-off numbers or external-library comparisons are published; the charts are asm-on Constantine timings only.
- CPUs or VMs without ADX. The fallback x86 asm is marked in limbs_montgomery.nim as 'faster than GCC but slower than Clang', so a Clang build there may do better with CTT_ASM=0.
- MSVC (not configured; Windows is tested with MinGW only), Apple Clang with LTO (no Intel asm syntax), GCC 15 with LTO (#588: cyclotomic exponentiation tests fail, which affects BLS signatures and KZG), or GCC on ARM64 (#582: 'more than 30 operands in asm').
- Fields wider than 6 limbs (384 bits) on x86-64, and full-width moduli with no spare bit: Montgomery multiplication there takes the compiler path (mulMont_FIPS or generic CIOS), not the ADX kernels.

## How it is fast

Nim macros act as a compile-time assembler. They emit size-specialised inline asm for each limb count: CIOS Montgomery multiplication, squaring and reduction ('sparebit' variants for moduli with a free top bit). On x86-64 these use MULX with the two independent carry chains of ADCX/ADOX, which C compilers do not emit. A runtime hasAdx() check picks the ADX kernels for 2-6 limbs and otherwise falls back to plain ADD/ADC assembly. The assembly also sidesteps GCC's poor _addcarry_u64 code generation (setc/addb round trips, shown in README-PERFORMANCE.md), and the inline-asm blocks keep the compiler from turning branchless constant-time code back into branches. ARM64 has its own inline-asm generators (2-8 limbs).

## Compared with alternatives

Pick Constantine over CryptOpt when you need a complete constant-time pairing-curve stack (BLS signatures, KZG, EVM precompiles, MSM) with asm specialised per limb count. Pick CryptOpt, or CRYPTOGAMS-style perlasm kernels, when you need field arithmetic for Curve25519, P-256 or secp256k1 checked for equivalence against Fiat Cryptography with measured gains over GCC and Clang, which Constantine does not offer (its README says formal proofs are not yet produced).

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime; build needs Nim v2.2.0 plus a C compiler (Clang recommended); Rust crates by git dependency invoke nimble with CC=clang from build.rs; Go bindings link the static library |
| **Minimum toolchain** | Nim v2.2.0; GCC 7+ or Clang 14+ (Clang 14 for -masm=intel, required with LTO); Homebrew Clang on macOS |
| **Platforms** | x86-64 (MULX/ADCX/ADOX kernels with runtime ADX dispatch, ADD/ADC asm fallback), x86-32 asm, ARM64 inline asm with Clang (GCC broken per #582), generic code elsewhere; Linux, macOS, Windows via MinGW |
| **Thread safety** | not documented for the primitives; the core arithmetic does no heap allocation, CPU-feature globals are set at load, and parallel MSM/KZG APIs take an explicit threadpool |
| **Drop-in for the baseline** | yes |

## Gotchas

- The asm-versus-compiler comparison is not like-for-like. The release flags set no -march, -mbmi2 or -madx, so the CTT_ASM=0 build cannot use MULX at all; only the ADCX/ADOX dual carry chain is something compilers truly cannot emit. In addition, bench_fields_template.nim's Multiplication and Squaring loops reuse loop-invariant inputs with preventOptimAway placed only before the loop. The asm kernels are 'asm volatile' with a 'memory' clobber and cannot be hoisted, while the plain C path can be, and bench_blueprint.nim itself warns that 'the simplest operations might be optimized away by the compiler'.
- The 'CPU cycles' column in the published benchmarks (for example Fp[BLS12_381] multiplication 68 cycles) is rdtsc ticks at the nominal clock; the harness prints a warning that turbo and overclocking skew it.
- Every generated asm block that writes through a pointer carries a full 'memory' clobber (a comment says the Poly1305 MAC test fails without it). This forces the compiler to reload operands around each kernel and limits scheduling across calls. Issue #446 (open) reports that a 1.7x field-arithmetic advantage on secp256k1 shrinks to a 0.85x disadvantage at the elliptic-curve level, traced to cache misses.
- The README is stale on ARM: it says 'Assembly is planned for ARM', and the Rust install notes say Constantine has no ARM assembly, yet constantine/math/arithmetic/assembly holds limbs_asm_\*_arm64.nim generators that config.nim enables (UseASM_ARM64) for any GCC-compatible compiler.

## Known shortcomings

- The 60% and 2.4x assembly claims are prose only (no table, CPU or log); GCC-vs-Clang figures are inconsistent and the charts are Constantine-only with no assembly-off column.
- Harness flaw: the CTT_ASM=0 baseline is built without -march, -mbmi2 or -madx, so the compiler path can never use MULX, and the field multiplication and squaring bench loops reuse loop-invariant inputs with preventOptimAway placed only before the loop (the asm kernels are asm volatile with a memory clobber and cannot be hoisted; the C path can; bench_blueprint itself warns about this). The non-ADX x86 fallback asm is commented as slower than Clang. The README is stale: ARM64 inline asm exists and is enabled by default for GCC-compatible compilers; the GCC build fails (#582); GCC 15 with LTO breaks pairings (#588). No asm-off numbers are published.

## Caveats and trade-offs

The asm-versus-compiler percentages are prose statements with no table, CPU, compiler version or run log for the 60% and 2.4x figures, and the same file's compiler figures disagree with each other (GCC 'up to 2x slower than Clang', '\~50% slower than Clang', and Clang/MSVC/ICC 'up to 20\~25% faster than GCC'). The 2.4x is plain GCC versus GCC with inline assembly, roughly the product of GCC's carry-handling penalty and the MULX/ADCX/ADOX gain, so against a Clang build the asm gain is the stated \~60%. The published benchmark charts (Ryzen 7 7840U, i9-9980XE) show only Constantine's own absolute timings (for example Fp[BLS12_381] multiplication 20 ns / 68 cycles), with no CTT_ASM=0 column and no comparison against blst, mcl, gnark-crypto or other libraries. Assembly is x86-64 only; ARM builds use the compiler path. [retier] The asm-versus-compiler percentages are prose statements with no table, CPU, compiler version or run log, and the same file's compiler figures disagree with each other. The comparison is not like-for-like: the release flags set no -march, -mbmi2 or -madx, so the CTT_ASM=0 build cannot use MULX (only the ADCX/ADOX dual carry chain is something compilers truly cannot emit); bench_fields_template.nim's Multiplication and Squaring loops reuse loop-invariant inputs with preventOptimAway placed only before the loop, so the plain C path can be hoisted while the asm volatile kernels cannot (bench_blueprint itself warns about this). The 2.4x is plain GCC versus GCC with inline assembly; against a Clang build the asm gain is the stated \~60%. No asm-off numbers are published; the published charts (Ryzen 7 7840U, i9-9980XE) show only Constantine's own absolute timings, and the 'CPU cycles' column is rdtsc ticks at the nominal clock. The non-ADX x86 fallback asm is commented as slower than Clang; every generated asm block carries a full 'memory' clobber that limits scheduling, and open issue #446 reports a 1.7x field-arithmetic advantage on secp256k1 turning into a 0.85x disadvantage at the curve level. The README is stale on ARM (ARM64 inline asm exists and is enabled by default for GCC-compatible compilers); the GCC build fails (#582) and GCC 15 with LTO breaks pairings (#588).

Assembly only on x86-64 (ARM has none yet); fastest path needs BMI2 and ADX; Nim toolchain with C ABI; Intel assembly syntax is unsupported by Apple Clang; constant-time guarantees are the stated reason for inline assembly.

## Maintenance

Actively maintained (last commit 2026-08-04, Nim 2.2.x regression #628 open), MIT OR Apache-2.0 and copyable. It is unaudited and labelled experimental, its speedup over its own compiler path is an undocumented first-party claim, and toolchain-specific failures (GCC 15 LTO #588, GCC ARM64 asm #582) mean Clang is the only well-trodden build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README-PERFORMANCE.md states the asm-versus-compiler gains only in prose ('up 60% with MULX, ADCX, ADOX on BLS12-381 (6 limbs)', '\~60% faster than Clang', '2.4x perf ratio between using plain GCC vs GCC with inline assembly', 'GCC is up to 2x slower than Clang'); the benchmark tasks are public but no table, CPU, compiler version or run log backs these figures, and the published charts (Ryzen 7 7840U, i9-9980XE) show Constantine-only absolute timings with no assembly-off column, so first-party numbers without methodology: C.
- **Verifier notes:** Quotes match README-PERFORMANCE.md verbatim; C stands as first-party prose numbers without methodology. Shortcomings: no table, CPU or run log behind the 60%/2.4x claims; internally inconsistent GCC-versus-Clang figures; charts carry no asm-off or external-library comparison; asm only on x86-64. Metadata (MIT OR Apache-2.0, 500 stars, last commit 2026-08-04, active, not a fork) confirmed.
- **Fields the verifier corrected:** `hardware`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-49 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/mratsim/constantine>
  - <https://github.com/mratsim/constantine/commits>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/README-PERFORMANCE.md>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/README.md>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/media/bench-summary_bls12_381-R7_7840U.png>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/media/bench-eth_bls_signatures-R7_7840U.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/README.md>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/README-PERFORMANCE.md>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine.nimble>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/platforms/config.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/platforms/abstractions.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/platforms/primitives.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/platforms/isa_x86/macro_assembler_x86.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/platforms/isa_x86/macro_assembler_x86_att.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/math/arithmetic/limbs_montgomery.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/math/arithmetic/assembly/limbs_asm_mul_mont_x86_adx_bmi2.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/constantine/math/arithmetic/assembly/limbs_asm_mul_mont_arm64.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/benchmarks/bench_blueprint.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/benchmarks/bench_fields_template.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/benchmarks/bench_fp.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/benchmarks/bench_gmp_modmul.nim>
  - <https://raw.githubusercontent.com/mratsim/constantine/HEAD/benchmarks/platforms.nim>
  - <https://github.com/mratsim/constantine/tree/master/constantine/math/arithmetic/assembly>
  - <https://github.com/mratsim/constantine/tree/master/benchmarks>
  - <https://github.com/mratsim/constantine/tree/master/media>
  - <https://github.com/mratsim/constantine/issues?q=is%3Aissue+blst+OR+performance+OR+gcc+OR+assembly>
  - <https://github.com/mratsim/constantine/issues/446>
  - <https://github.com/mratsim/constantine/issues/357>
  - <https://github.com/mratsim/constantine/issues/588>
  - <https://github.com/mratsim/constantine/issues/582>
  - https://ethresear.ch/t/releasing-constantine-v0-2-0-jan-2025-a-modular-cryptography-stack-for-ethereum/19990 (ENOTFOUND; search snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mratsim/constantine`) · [data/wave13/enrich/raw/github_com_mratsim_constantine.json](../../../data/wave13/enrich/raw/github_com_mratsim_constantine.json) (enrichment confidence 0.74)

</details>
