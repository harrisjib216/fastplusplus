# wasm-i128-div-bench (reciprocal 128-bit division for the Wasm wide-arithmetic proposal)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Rust` · `no license` · 🟢 active

> Rust research benchmark: Moeller-Granlund reciprocal 128-bit division vs __udivti3, native and Wasm wide-arithmetic; wins mainly with hoisted divisors.

| | |
|---|---|
| **Beats** | Rust u128/i128 division operators lowering to compiler-builtins __udivti3/__umodti3 (compiler-rt libcall) on wasm32 |
| **Claimed result** | Loop-invariant divisor (reciprocal hoisted, 5,000 divrems per call): V8 d8 29.67 us to 18.24 us (-38.5%), wasmtime 52.51 us to 13.97 us (-73.4%), native 134.44 us to 9.73 us (-92.8%); these rows run a degenerate workload in which 3,144 of 5,000 iterations have quotient 0 (reciprocal path exits through its Y &gt; X shortcut with no multiply) and 1,856 have quotient 1, while the Wasm builtin early-outs every iteration (5.93 ns per iteration on d8 vs 18.27 ns for a single general op, derived from page data). Single divisions: native reciprocal is faster (udivrem128 27.86 ns to 17.18 ns, -38.3%; -28.5% to -38.3% across the six ops), but on Wasm it is slower: V8 +19.6% to +33.4% (udivrem128 18.27 ns builtin vs 24.38 ns reciprocal), wasmtime -0.7% to +10.3%. |
| **Workload** | criterion microbenchmarks of 128-bit unsigned/signed divide, remainder and divrem, including a loop-invariant-divisor case, native vs V8 (d8) vs wasmtime (Cranelift), reciprocal (Moeller-Granlund) path vs the builtin operators. |
| **Metric** | latency |
| **Hardware** | Intel Core i9-9880H @ 2.30GHz, macOS 15.7.7 x86_64 |
| **Compiler and flags** | rustc 1.98.0-nightly (61d7280f3 2026-06-06), release profile opt-level=3, lto=fat, codegen-units=1, panic=abort, profile rustflags -Z mir-opt-level=5 -Z inline-mir=yes -Z cross-crate-inline-threshold=always; native x86_64 built with -C target-cpu=native; wasm32 target features +bulk-memory,+multivalue,+reference-types,+wide-arithmetic with build-std (compiler-builtins rebuilt with the same features); criterion 0.8.2 (300 samples, 3 s measurement); d8 15.1.52; wasmtime 45.0.1 |
| **Adoption** | 0 stars |
| **Last commit** | 2026-06-09 |
| **Links** | [repository](https://github.com/MaxGraey/wasm-i128-div-bench) · [benchmark](https://github.com/MaxGraey/wasm-i128-div-bench/blob/main/report/RESULTS-4db0b805.md) |

## Verdict

Criterion slope estimates (300 samples, 3 s) on an Intel Core i9-9880H under macOS 15.7.7, rustc 1.98.0-nightly opt-level 3 with fat LTO: with the reciprocal hoisted out of a 5,000-iteration loop, the reciprocal path took 18.24 vs 29.67 us under d8 15.1.52, 13.97 vs 52.51 us under wasmtime 45.0.1 and 9.73 vs 134.44 us natively against Rust's u128 operators, but that loop only produces quotients 0 and 1; single general divisions favour the builtin on V8 (18.27 vs 24.38 ns for udivrem128), tie on wasmtime, and favour the reciprocal natively (17.18 vs 27.86 ns).

## Use it when

- Designing or evaluating Wasm engine or toolchain support for 128-bit division on top of the wide-arithmetic proposal; the report and the i64.recip128 / i64.divrem_recip128 sketch are the point of the repo.
- Native x86_64 code that divides many 128-bit values by one fixed divisor on a CPU where the 128/64 DIV instruction is slow (the measured machine is a Coffee Lake i9-9880H): port the 2-by-1/3-by-2 kernels and hoist recip128.
- Wanting a readable, unit-tested Rust reference of Moeller-Granlund reciprocal division (500,000-case random and edge-value tests against the native operators).

## Skip it when

- One-off 128-bit divisions in Wasm: the builtin libcall is faster on V8 (reciprocal 19.6% to 33.4% slower) and about equal on wasmtime (-0.7% to +10.3%).
- Production code: no LICENSE file (raw LICENSE returns 404), not a library crate, nightly-only (edition 2024, #![feature(likely_unlikely)], cargo-features profile-rustflags, build-std).
- Stock Node or browsers: the d8 script notes that stock Node rejects the wide-arithmetic opcodes; V8 needs --experimental-wasm-wide-arithmetic and wasmtime needs -W wide-arithmetic=y (45 or later).
- Expecting the loop-invariant speedups for general quotients: the benchmarked loop only produces quotients 0 and 1 (see gotchas), so throughput with a hoisted reciprocal on large quotients is unmeasured.
- Other microarchitectures: all numbers come from one macOS laptop with an Intel Core i9-9880H; no aarch64 or newer x86 runs are reported.

## How it is fast

Division by an invariant integer via a precomputed reciprocal (Moeller and Granlund, 'Improved division by invariant integers'): a 256-entry u16 table seeds Algorithm 2's Newton steps to get floor((2^128-1)/d) - 2^64, then 2-by-1 (64-bit divisor) or 3-by-2 (full-width divisor) kernels replace the divide with a multiply-high, a multiply-low and at most two correction steps. Splitting the reciprocal (recip128) from the divide (divrem_recip128) lets a caller compute it once outside a loop, which the opaque libcall cannot do. Shortcuts return early when the divisor's high word exceeds the dividend's (quotient 0) or when the divisor is already normalised (quotient 0 or 1).

## Compared with alternatives

No sibling covers 128-bit division: long.js gives a Wasm fast path for 64-bit multiply/divide from JavaScript and galois does finite-field arithmetic in AssemblyScript, so use this only as the reference when you need 128-bit divide in Rust-to-Wasm or are arguing for engine support.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | kernels use only core/std; the benchmark harness pulls criterion 0.8.2, rand 0.10.1, getrandom 0.4.2, num-traits 0.2.19 |
| **Minimum toolchain** | Rust nightly (rust-toolchain.toml channel nightly; report used rustc 1.98.0-nightly 2026-06-06) with rust-src and wasm32-wasip1; d8 15.1.52 with --experimental-wasm-wide-arithmetic; wasmtime 45.0.1 |
| **Platforms** | native x86_64 (built with -C target-cpu=native) and wasm32-wasip1 with +wide-arithmetic,+multivalue,+bulk-memory,+reference-types; other targets not tested |
| **Thread safety** | pure functions over values with a read-only 512-byte static table; no shared mutable state |
| **Drop-in for the baseline** | partial: udiv128/urem128/sdiv128 etc. take and return u128/i128 with the operators' semantics (panics on divide by zero and on i128::MIN / -1), but they live in a binary crate, are unlicensed, and only beat the operator on Wasm when the divisor is loop-invariant and recip128 is hoisted by hand |

## Gotchas

- Harness flaw in the headline loop-invariant bench: the divisor is the dividend's own high word with the top bit cleared, and the dividends only flip its low 13 bits (i &lt; 5,000). Reproducing the seeded operands (rand 0.10.1 Xoshiro128PlusPlus::seed_from_u64(0x9E3779B97F4A7C15), checked against rand's own seed_from_u64(0) test vector) gives d_hi = 0x59a28c5de09aec48: 3,144 of 5,000 iterations (62.9%) have quotient 0 and leave the reciprocal path through its Y &gt; X shortcut with no multiply, and the other 1,856 have quotient 1.
- On Wasm the builtin __udivti3 is compiler-builtins' trifecta algorithm (selected for target_family wasm in the current rust-lang/rust source), whose div_lz &lt;= duo_lz branch returns quotient 0 or 1 after one compare; divisor and every dividend here have one leading zero, so every builtin iteration takes that early-out (5.93 ns per iteration on d8 vs 18.27 ns for a single general udivrem128, derived from page data). The -38.5% (d8) and -73.4% (wasmtime) therefore compare libcall overhead on a trivial quotient against a mostly-shortcut inlined kernel, not hoisted-reciprocal division on real quotients.
- Native -92.8%: on x86_64 compiler-builtins (with its arch feature) uses the asymmetric algorithm, which issues a hardware 128/64 DIV for any divisor with a nonzero high word and has no quotient-0/1 early-out; the native builtin costs 26.9 ns per loop iteration, the same as its single-op cost (26.7 to 27.9 ns), versus 1.95 ns for the reciprocal path (derived from page data).
- Single-op benches time one fixed operand pair shared by all six ops: unsigned quotient 9 (3-by-2 kernel, shift 3) and signed |quotient| 1 (negative dividend, positive divisor); the 2-by-1 path for 64-bit divisors is never benchmarked.

## Known shortcomings

- Wasm wins only with a loop-invariant divisor; single operations are slower on V8 (+19.6% to +33.4%), each single-op bench times one fixed operand pair, the loop workload is narrow with tiny quotients, and the native -92.8% row probably reflects a slow native __udivti3. No licence (reference); loose category fit.
- Harness flaw behind the loop-invariant headline: the divisor is the dividend's own high word with the top bit cleared, and reproducing the seeded operands (rand 0.10.1 Xoshiro128PlusPlus, checked against rand's test vector) shows 3,144 of 5,000 iterations (62.9%) with quotient 0 that leave the reciprocal path through its Y &gt; X shortcut with no multiply, and the other 1,856 with quotient 1; the Wasm builtin (compiler-builtins trifecta) also early-outs every iteration (d8 5.93 ns per iteration vs 18.27 ns for a single general op). So the -38.5% (d8) and -73.4% (wasmtime) rows compare libcall overhead on trivial quotients, the native -92.8% is 5,000 hardware DIVs (26.9 ns per iteration, the same as a single op) against a mostly-shortcut kernel, and the hoisting benefit for general quotients is unmeasured. Single-op benches use one operand pair (unsigned quotient 9, signed |quotient| 1); the 2-by-1 path is never benchmarked.

## Caveats and trade-offs

Mixed result by design: the reciprocal path wins on Wasm only when the divisor is loop-invariant and the reciprocal is hoisted by hand (the bench calls recip128 once before the loop; the builtin libcall cannot be hoisted); for one-off divisions the builtin is faster on V8 and about equal on wasmtime. Each single-op bench times one fixed seeded operand pair, so it measures one kernel path with warm branch predictors. The loop-invariant workload is narrow: one seeded divisor in (0, 2^127) whose high word equals the dividend's high word up to the low 13 bits and the top bit, so quotients are 0 or small and the reciprocal path's Y &gt; X shortcut can fire. The native -92.8% probably reflects a slow native __udivti3 (likely the hardware 128/64 DIV path on this Coffee Lake laptop CPU; verifier inference): the same builtin compiled to Wasm takes 77.9% less time on the loop under d8 than natively (134.44 us native vs 29.67 us d8). Baseline is Rust's compiler-builtins (__udivti3/__umodti3), not TypeScript/JS or Emscripten C++. Single macOS laptop; research micro-benchmark and proposal sketch (extended wide-arithmetic i64.recip128/i64.divrem_recip128), not a library; no license file, 0 stars. Correctness of the reciprocal loop is checked against native division by a unit test (divrem_with_loop_invariant_divisor_matches_native). [retier] Harness flaw in the headline loop-invariant bench: the divisor is the dividend's own high word with the top bit cleared and the dividends only flip its low 13 bits; reproducing the seeded operands (rand 0.10.1 Xoshiro128PlusPlus::seed_from_u64(0x9E3779B97F4A7C15), checked against rand's test vector) gives d_hi = 0x59a28c5de09aec48, so 3,144 of 5,000 iterations (62.9%) have quotient 0 and leave the reciprocal path through its Y &gt; X shortcut with no multiply, and the other 1,856 have quotient 1. On Wasm the builtin __udivti3 is compiler-builtins' trifecta algorithm, whose div_lz &lt;= duo_lz branch returns quotient 0 or 1 after one compare, so every builtin iteration takes that early-out; the -38.5% (d8) and -73.4% (wasmtime) rows compare libcall overhead on trivial quotients against a mostly-shortcut inlined kernel. Native -92.8%: x86_64 compiler-builtins uses the asymmetric algorithm with a hardware 128/64 DIV and no early-out (26.9 ns per iteration, the same as its single-op cost) against 1.95 ns for the shortcut-heavy reciprocal loop. The hoisting benefit for general quotients is unmeasured. Single-op benches time one fixed operand pair shared by all six ops (unsigned quotient 9 via the 3-by-2 kernel, signed |quotient| 1); the 2-by-1 path for 64-bit divisors is never benchmarked; on V8 the reciprocal is 19.6-33.4% slower than the builtin for single divisions and about equal on wasmtime. Nightly rustc with -Z mir-opt-level=5 and fat LTO; one Coffee Lake laptop.

Requires the wide-arithmetic Wasm proposal (V8 nightly, wasmtime 45 or later) and Rust nightly with build-std. Repo has no LICENSE file, so the code is reference-only. The README also sketches proposed i64.recip128 / i64.divrem_recip128 instructions.

## Maintenance

Active research repo (39 commits, last 2026-06-09, report regenerated in that commit) but unlicensed with 0 stars, so reference only; its loop-invariant headline was measured on a degenerate quotient-0-or-1 workload where 62.9% of iterations skip the division entirely and the Wasm builtin takes its own early-out, so the hoisting benefit for general quotients is unproven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now D.
- **Tier reason:** report/RESULTS-4db0b805.md (generated by scripts/report.py from criterion runs of src/divrem_by_recip.rs vs src/divrem_builtin.rs, driven by src/main.rs) lists every quoted number, with rustc 1.98.0-nightly, d8 15.1.52, wasmtime 45.0.1 and CPU Intel Core i9-9880H; flags are public in Cargo.toml and .cargo/config.toml. The report was regenerated after the last benchmark-affecting commit (6b22b87, xoshiro128++ operand parity).
- **Retiered** A to D: Enricher: the loop-invariant headline uses a divisor equal to the dividend's own high word, so 62.9% of the 5,000 iterations have quotient 0 and exit the reciprocal path through its Y &gt; X shortcut and the rest have quotient 1, while the Wasm builtin early-outs every iteration (degenerate workload, ThreadPool precedent); the only like-for-like single-op Wasm rows show the reciprocal slower than the builtin on V8 and about equal on wasmtime, and the native single-op win (28-38%) is not the catalogued Wasm claim. No valid measurement of the Wasm claim: A to D.
- **Verifier notes:** Numbers match the report exactly; added native single-op rows and full flags. Metadata: no LICENSE file (license null, reference usability correct), 0 stars, 39 commits, last commit 2026-06-09 (active). Category fit is loose: a Rust/Wasm 128-bit division micro-benchmark rather than an AssemblyScript or Wasm language. Shortcomings: one operand pair per single-op bench, narrow loop-invariant workload with tiny quotients, native win driven by a slow native builtin (d8 runs the same builtin loop 4.5x faster), Wasm single ops slower.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-52 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/MaxGraey/wasm-i128-div-bench>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/commits>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/commits/main>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/commits/main/report>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/tree/main/src>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/tree/main/report>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/report/RESULTS-4db0b805.md>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/scripts/bench.sh>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/divrem_builtin.rs>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/divrem_by_recip.rs>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/utils.rs>
- **Sources the enricher read:**
  - <https://github.com/MaxGraey/wasm-i128-div-bench>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/commits/main>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/commits/main/report>
  - <https://github.com/MaxGraey/wasm-i128-div-bench/tree/main/report>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/report/RESULTS-4db0b805.md>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/package.json>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/scripts/bench.sh>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/scripts/bench-d8.sh>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/scripts/bench-wasmtime.sh>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/scripts/report.py>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/utils.rs>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/divrem_builtin.rs>
  - <https://raw.githubusercontent.com/MaxGraey/wasm-i128-div-bench/HEAD/src/divrem_by_recip.rs>
  - <https://raw.githubusercontent.com/rust-random/rand/0.10.1/src/rngs/xoshiro128plusplus.rs>
  - <https://raw.githubusercontent.com/rust-random/rand/0.10.1/src/distr/integer.rs>
  - <https://raw.githubusercontent.com/rust-random/rand_core/v0.10.0/src/utils.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/main/library/compiler-builtins/compiler-builtins/src/int/specialized_div_rem/mod.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/main/library/compiler-builtins/compiler-builtins/src/int/specialized_div_rem/trifecta.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/main/library/compiler-builtins/compiler-builtins/src/int/specialized_div_rem/asymmetric.rs>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/maxgraey/wasm-i128-div-bench`) · [data/wave13/enrich/raw/github_com_maxgraey_wasm_i128_div_bench.json](../../../data/wave13/enrich/raw/github_com_maxgraey_wasm_i128_div_bench.json) (enrichment confidence 0.75)

</details>
