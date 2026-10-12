# VROOM (RNS Montgomery arithmetic with AVX-512 IFMA, BLS12-381 and BN254)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 RNS Montgomery arithmetic on AVX-512 IFMA; BLS12-381 pairing 3.9x faster than BLST on Sapphire Rapids.

| | |
|---|---|
| **Beats** | BLST (supranational/blst at 8065152, a modified vendored copy in blst/ with benchmark wrappers); GMP is used only for parameter generation and validation, not timed |
| **Claimed result** | results/bench_bls12_381_vs_blst.txt, MatrixNoK (the production configuration), VROOM ns vs BLST ns: full pairing 128145.9 vs 500035.1 (ratio 3.902); Miller loop 49888.2 vs 215023.1 (4.310); final exponentiation 82491.2 vs 285421.3 (3.460); Fp12 mul 257.1 vs 1563.4 (6.082); Fp12 sqr 224.4 vs 1126.2 (5.019); G1 add 154.2 vs 585.8 (3.799); G1 scalar mult (GLV) 30647.5 vs 75949.8 (2.478); G2 scalar mult (GLS) 41245.7 vs 146934.4 (3.562); Fp mul 21.8 vs 29.0 (1.332 for a single mul, up to 2.272 amortized in a batch of 10). The slower row: Fp12 inversion with the BLST inverter 7599.8 vs 5560.4 (0.732); the RNS-assisted inversion reaches 3406.7 (1.632). The plain Matrix variant gives pairing 151066.7 vs 500035.1 (3.310). |
| **Workload** | Google Benchmark ns per operation for BLS12-381 field and curve operations (Fp mul, Fp2, Fp12, G1/G2 add, double, scalar multiplication, Miller loop, final exponentiation, full pairing), VROOM RNS code against BLST on the same machine; ratio = blst_ns / rns_ns. |
| **Metric** | latency |
| **Hardware** | AWS c7i.metal-24xl, Intel Xeon Platinum 8488C (Sapphire Rapids), Amazon Linux 2023 (README). Raw Google Benchmark JSON (results/bench_bls12_381.json): date 2026-06-17T19:11:18Z, num_cpus 96, mhz_per_cpu 3793, cpu_scaling_enabled false, library v1.9.4-89-g04ccbd86, threads = 1 for each benchmark (single-threaded). |
| **Compiler and flags** | clang++ 21.1.0 (LLVM 21 prebuilt, llvm-project 3623fe6) with Google Benchmark at 04ccbd8 (v1.9.4-89), --benchmark_min_time 0.5s (scripts/reproduce_cpu_bench.sh). VROOM benchmark: -std=c++20 -O3 -march=native -mavx512ifma -D__ADX__ (src/Makefile CXXFLAGS_BENCH). BLST baseline: blst/Makefile CFLAGS -O2 -fno-builtin -fPIC -D__x86_64__ (+ -D__ADX__ when /proc/cpuinfo shows adx), CC auto-detected as clang if present, field arithmetic from assembly_small.S. |
| **Adoption** | 5 stars, 1 fork, 42 commits (github.com page, opened 2026-10-03); research artifact (commit f12e58d 'update readme results to match camera ready', commit 26bd9ae 'update based on artifact evaluation feedback') |
| **Last commit** | 2026-08-28 |
| **Links** | [repository](https://github.com/SimonLangowski/VROOM) · [benchmark](https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/results/bench_bls12_381_vs_blst.txt) |

## Verdict

Single-threaded Google Benchmark on an AWS c7i.metal-24xl (Xeon Platinum 8488C, 3.79 GHz, CPU scaling off), VROOM built with clang 21.1.0 -O3 -march=native -mavx512ifma against the in-tree BLST fork at 8065152 (its own -O2 build with x86-64 assembly and ADX): full BLS12-381 pairing 128.1 us vs 500.0 us (3.9x), Miller loop 4.3x, final exponentiation 3.5x, single Fp multiply 1.33x. The repo's optional baseline log from the same CPU gives gnark-crypto 529 us, arkworks 1.02 ms and zkcrypto 1.07 ms per pairing, i.e. about 4.1x, 8.0x and 8.4x slower than VROOM (derived from page data); all numbers predate the August 2026 correctness fixes.

## Use it when

- Latency-critical BLS12-381 pairings, Miller loops or G1/G2 scalar multiplications on one core of an AVX-512 IFMA x86 server: measured 3.9x full pairing, 2.5x G1 GLV and 3.6x G2 GLS scalar multiplication over BLST on a Xeon Platinum 8488C.
- Pairing-heavy verification code (BLS signature aggregation checks, SNARK verifiers) where you are willing to wire the field and curve templates into your own protocol layer.
- Extension-field-heavy work (Fp12 mul 6.1x, Fp12 squaring 5.0x, cyclotomic squaring 3.6x over BLST) where the delayed-reduction formulas pay off.
- Research on RNS/IFMA arithmetic for other fixed moduli of similar size, using the Python generator (scripts/rns_secp256k1.py) that emits parameter headers.

## Skip it when

- Production signing or any secret-dependent use: the README says the code is research-grade and 'has not been vetted or audited for security'; the constant-time claim comes only from the paper abstract (search snippet) and was not checked.
- CPUs without avx512ifma in /proc/cpuinfo: the integer fallback build (Makefile.fallback) is for correctness only, not performance.
- Builds with GCC or older clang: the README says they are 'significantly slower' than clang 21.x on the IFMA path, so the published ns/op will not reproduce with distro compilers.
- Inversion-heavy code: Fp12 inversion using BLST's Fp inverter is slower than BLST (7.60 us vs 5.56 us, 0.73x), and the pairing itself still calls BLST for the base-field inversion.
- Other curves or large moduli: only BLS12-381 and BN254 parameters ship, MatrixNoK parameter search is exponential in the number of radix words, and RSA-size moduli are covered by the sibling vroomssl fork instead.

## How it is fast

A field element is stored as residues modulo a set of small moduli spread across zmm lanes, so one 381-bit multiply becomes lane-wise vpmadd52lo/hi products instead of a serial carry chain. RNS Montgomery reduction then needs a base extension (change-base) between two residue sets, which VROOM computes as small matrix products laid out to avoid cross-lane permutation overhead (paper abstract, via search snippet). The production MatrixNoK variant uses a cyclic r1 permutation found by an offline parameter search that removes the k-correction term, and delayed reduction lets Fp2/Fp12 formulas accumulate products before reducing, which is why compound operations gain far more (Fp12 mul 6.1x) than a single Fp multiply (1.33x).

## Compared with alternatives

Pick it over kevin-he-01/vroomssl (the same paper's BoringSSL/RSA fork, whose README carries no figures) when the target is BLS12-381 or BN254 pairing and curve arithmetic rather than RSA-size moduli, and over the Truncated batch SIMD AVX512 Montgomery code when you need low latency for one operation rather than throughput across 8 independent modexps; no other catalogued sibling covers pairing-friendly fields.

## Integration

| | |
|---|---|
| **Form** | header-only (C++20 templates in src/\*.hpp and cpu/, no shared library), plus a vendored BLST static library (libblst_small.a) for the pairing's base-field inversion |
| **Dependencies** | GMP and gmpxx (BigInt conversion, parameter setup, tests); the BLST fork in blst/ (Apache-2.0) for the BLST-inverter pairing path; Google Benchmark for the benches; Python for parameter regeneration |
| **Minimum toolchain** | C++20 (-std=c++20 with clang++, -std=c++2a with g++); clang 21.1.0 for paper-comparable speed, other compilers for correctness only |
| **Platforms** | Linux x86-64 with AVX-512 IFMA (Amazon Linux 2023 and Ubuntu documented; measured on Xeon Platinum 8488C, Sapphire Rapids); optional CUDA kernels need a separate NVIDIA host |
| **Thread safety** | not documented (all published benchmarks are single-threaded) |
| **Drop-in for the baseline** | no |

## Gotchas

- The production MatrixNoK path had a correctness bug: issue #1 (opened 2026-08-10) showed ConvertTo could select a negative CRT representative for a canonical BLS12-381 input, breaking import/export round-trip and multiply-by-one. Fixes landed 2026-08-14 (floor instead of ceiling rounding in generated constants, PR #2) and 2026-08-28, but results/ dates from 2026-06-17 and was not re-run.
- Per-operation ratios are not like-for-like: the BLST side is called through blst_fp_\* wrappers in a C glue file built with gcc -O2, while VROOM's header templates are built at -O3 -march=native, and even trivial Fp12 conjugation shows 2.2x. Trust the pairing, Miller loop and scalar-multiplication rows over the micro-op rows.
- A lone Fp multiply gains little (1.33x MatrixNoK, 1.03x for the Matrix variant); amortized gains of 2.0-2.3x need batches of 5-10 multiplies through BatchModMul or delayed reduction.
- MatrixNoK uses 50-bit (not 52-bit) words for integer-to-RNS conversion; regenerating parameters for a new modulus means rerunning the Python generator, rebuilding src/ and running scripts/smoke_test.sh.

## Known shortcomings

- Capped at C: the methodology is A-grade (every ratio verified, raw JSON shows threads=1) but the correctness fixes 145f864 and 0131695 (August 2026) touched the runtime conversion headers after the published results/ (2026-06-17), so the numbers predate the fixed code. The IACR ePrint venue could not be confirmed (eprint.iacr.org blocked).
- Issue #1 (2026-08-10): MatrixNoK ConvertTo could pick a negative CRT representative, breaking round-trip and multiply-by-one; fixed 2026-08-14 in PR #2, after results/ (2026-06-17). Micro-op rows are not like for like: BLST is called through gcc -O2 C glue while VROOM builds -O3 -march=native, and even the Fp12 conjugate shows 2.2x. The pairing still uses BLST's Fp inverter. Unaudited.

## Caveats and trade-offs

Tier capped at C under the project rule for numbers measured on code later fixed for correctness bugs: all files under results/ date from 2026-06-17 (path history: 8a6c6d0, 2abf635, 8619fe3, b8d936e, fd6d149), while 2785394 (2026-08-14, adds Fix.pdf, the corrected proof for floor rather than ceiling rounding reported by Peter Rindal), 145f864 (2026-08-14, 'matrix no k convert to negative'; changes precompute.hpp, cpu/vector/changebase.hpp and cpu/vector/conversion.hpp by a few lines each, plus parameter files) and 0131695 (2026-08-28, constants such as r1_shifted_quotient_estimations 65 to 64 and a floor flag) came later. The diffs look like constant and rounding-mode changes rather than extra hot-path operations, but the benchmarks were not re-run. Same-machine pair, but BLST is built at -O2 -fno-builtin with assembly_small.S (its upstream default) while VROOM uses -O3 -march=native; the pairing figure uses BLST's inverter for the Fp inversion inside the RNS pairing (BM_Pairing_RNS_BLST_Inverter); amortized batch rows exclude any batching cost on the caller side; BLST is a modified vendored copy (extern "C" changes, Apache-2.0 subtree under blst/). The README says timings depend strongly on clang 21; GCC and older clang are 'significantly slower'. Research-grade code, 'not vetted or audited for security' (README). Requires AVX-512 IFMA. The paper (IACR ePrint 2026/393) could not be opened (eprint.iacr.org blocked), so its venue and numbers are unchecked. The task lead's baselines (GMP, MPFR) are not what this repo benchmarks against; BLST is the relevant incumbent for BLS12-381.

Needs AVX-512 IFMA hardware (a slow integer fallback exists for correctness only) and, per the README, clang 21.x for paper-comparable timings, because GCC and older clang are significantly slower on the IFMA path. Gains are largest on batched or compound operations (Fp12, pairing, scalar mult); a single Fp multiply is only 1.33x. Ships parameter sets for BLS12-381 and BN254 only; the MatrixNoK parameter search is exponential in the number of radix words, so it suits small moduli. README says: research-grade, not vetted or audited for security. The blst/ subtree stays Apache-2.0; baselines/ vendors arkworks, zkcrypto, zksync and gnark with their own licenses.

## Maintenance

Research artifact for IACR ePrint 2026/393 (commits mention a camera-ready version and artifact-evaluation feedback; venue not confirmed), last commit 2026-08-28; MIT-licensed headers are small enough to vendor, but the code is explicitly unaudited.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** results/bench_bls12_381_vs_blst.txt carries every quoted ns value and ratio (VROOM vs vendored BLST, same run), and the methodology would otherwise reach A (scripts/reproduce_cpu_bench.sh, src/bench_bls12_381.cpp, clang 21.1.0, -O3 -march=native -mavx512ifma in src/Makefile, Xeon Platinum 8488C). Capped at C by the project rule for numbers measured on code later fixed for correctness bugs: results/ was last touched 2026-06-17, while 145f864 (2026-08-14) and 0131695 (2026-08-28) changed the radix-to-RNS conversion, including runtime headers cpu/vector/changebase.hpp and conversion.hpp; the paper is IACR ePrint 2026/393 with no venue confirmed, so not B.
- **Verifier notes:** All quoted ratios verified row by row on the results page; single-thread confirmed from the raw JSON. Tier stays C only because of the post-measurement correctness fixes; a re-run on HEAD would justify A.
- **Fields the verifier corrected:** `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; same-host baselines in results/baselines_bls12_bench.log (Xeon 8488C), per pairing: gnark-crypto 529,187 ns, arkworks 1.0229 ms, zkcrypto 1.0743 ms, zksync 1.515 ms vs VROOM 128,146 ns, about 4.1x/8.0x/8.4x/11.8x (derived from page data)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/results/bench_bls12_381_vs_blst.txt>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/results/bench_bls12_381.json>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/README.md>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/blst/Makefile>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/scripts/reproduce_cpu_bench.sh>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/LICENSE>
  - <https://github.com/SimonLangowski/VROOM>
  - <https://github.com/SimonLangowski/VROOM/commits>
  - <https://github.com/SimonLangowski/VROOM/commits/main/results>
  - <https://github.com/SimonLangowski/VROOM/commit/2785394>
  - <https://github.com/SimonLangowski/VROOM/commit/145f864>
  - <https://github.com/SimonLangowski/VROOM/commit/0131695>
- **Sources the enricher read:**
  - <https://github.com/SimonLangowski/VROOM/commits>
  - <https://github.com/SimonLangowski/VROOM/issues/1>
  - <https://github.com/SimonLangowski/VROOM/tree/main/results>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/README.md>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/ARTIFACT.md>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/results/bench_bls12_381_vs_blst.txt>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/results/baselines_bls12_bench.log>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/src/README.md>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/blst/Makefile>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/baselines/README.md>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/scripts/reproduce_cpu_bench.sh>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/examples/README.md>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/examples/02_singular_modmul.cpp>
  - <https://raw.githubusercontent.com/SimonLangowski/VROOM/HEAD/cpu/vector/avx512ifma.hpp>
  - <https://github.com/hchengv/avxbls>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/simonlangowski/vroom`) · [data/wave8/enrich/raw/github_com_simonlangowski_vroom.json](../../../data/wave8/enrich/raw/github_com_simonlangowski_vroom.json) (enrichment confidence 0.75)

</details>
