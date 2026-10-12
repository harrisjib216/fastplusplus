# DigitsOnTurbo (DoT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · ⚪ unknown

> Research SIMD (AVX-512/IFMA) kernels for bignum add/sub and base-case multiply, patched into GMP and OpenSSL.

| | |
|---|---|
| **Beats** | GMP 6.3.0 (also OpenSSL 3.5.2 bignum) |
| **Claimed result** | DoTMP vs GMP geomean: addition 3.81x, subtraction 3.73x, multiplication 1.41x (512-32768-bit operands); DoTSSL vs OpenSSL: addition 2.95x, subtraction 4.08x; pi computation up to 19.3% faster; larger-operand multiplication up to 48.7% (Emerald Rapids, AVX-512) |
| **Workload** | Large-number addition, subtraction, multiplication with x86 SIMD intrinsics, plus pi computation |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6548Y+ (Emerald Rapids) and Xeon Max 9462 (Sapphire Rapids) |
| **Compiler and flags** | clang 14.0.0-1ubuntu1.1, -O2 -march=native |
| **Links** | [benchmark](https://arxiv.org/html/2604.21566v1) |

## Verdict

Against stock GMP 6.3.0, DoT-patched GMP gives geomean 3.81x add, 3.73x sub and 1.41x multiply over 512-32,768-bit operands, up to 48.7% on large multiplies and +19.3% on pi. Against OpenSSL 3.5.2 it gives 2.95x add and 4.08x sub. All results are from clang 14 -O2 -march=native on Xeon Gold 6548Y+ (Emerald Rapids) and Xeon Max 9462 (Sapphire Rapids), measured by the authors.

## Use it when

- Research or prototyping on AVX-512 (Sapphire/Emerald Rapids class) Xeons where GMP mpn add/sub dominates the profile
- Mid-size operands (about 6,144-32,768 bits), where the paper reports its largest gains
- Reproducing or extending SIMD bignum work; the four-phase carry design is a clear reference
- Estimating headroom before investing in your own SIMD mpn kernels

## Skip it when

- Production work: there is no public repository or license, and the code sits at an anonymous review URL
- CPUs without AVX-512: the paper reports SSE addition at 0.7x (slower than scalar) and AVX2 at only 1.2x
- Huge-operand multiplication dominated by FFT: DoT replaces only the base case, so whole-program gains shrink (GMPbench +7.8% overall)
- Crypto code that needs constant time: the data-dependent cascading-carry slow path is not analysed for timing leaks
- Adversarial inputs built to trigger cascading carries, where the paper's advantage drops to 0.7-2.0x versus prior SIMD methods

## How it is fast

Add/sub runs in four phases: lane-parallel limb add, carry detection with SIMD compares, a single parallel carry-propagation step, and a deferred scalar slow path for cascading carries. A cascade requires limbs equal to 2^64-1, so on random inputs it practically never fires. Multiplication uses a 'vertical and crosswise' scheme that exposes all m^2 partial products as independent AVX-512 IFMA multiplies (52-bit radix, with conversion from 64-bit limbs) before reducing columns, which removes read-after-write chains on a shared accumulator. Karatsuba/Toom recursion in GMP bottoms out in this base case.

## Compared with alternatives

Pick it over ctbignum or mp++ only if you want faster stock GMP/OpenSSL arithmetic at thousands of bits on AVX-512 without changing your code, and you can live with unpublished code. FLINT is the shippable choice for big-number workloads, and the truncated-batch AVX-512 Montgomery code fits better when you batch modular exponentiations.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | GMP 6.3.0 or OpenSSL 3.5.2 source tree to patch |
| **Minimum toolchain** | evaluated with clang 14, -O2 -march=native; others not documented |
| **Platforms** | x86-64; AVX-512 (plus IFMA for multiply) needed for the reported gains |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — it patches GMP/OpenSSL internals (about 40 lines) so the public API stays the same, but you must rebuild those libraries from patched source |

## Gotchas

- The code was not verifiable: anonymous.4open.science blocks fetchers, and no license is stated
- The headline 3.81x/3.73x geomeans are for the add/sub primitives alone; end-to-end gains are much smaller (pi +19.3%, divide +8.4%, RSA/FFDH/DSA throughput +3-5%)
- The multiply needs a 64-to-52-bit radix conversion for the 4x4 routine to stay compatible with GMP/OpenSSL limbs, which adds overhead

## Known shortcomings

- Code only at an anonymous review link that blocked fetch (unverified); no license; preprint with no venue named.
- Without AVX-512 gains mostly vanish (SSE add 0.7x, AVX2 1.2x); whole-program gains small (pi +19.3%, GMPbench +7.8%, RSA/FFDH/DSA +3-5%); constant-time behaviour not analysed.

## Caveats and trade-offs

Code only at anonymous.4open.science/r/DigitsOnTurbo (blocked to fetchers, not verified); no license found; preprint with no venue stated; headline geomeans are on AVX-512 Emerald Rapids.

1,013 lines of portable C with intrinsics; integrates into GMP and OpenSSL with \~40 lines of changes.

## Maintenance

Preprint with no stated venue and code only at an anonymous review link with no license, so treat it as a reference design, not a dependency; maintenance status unknown.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** arXiv preprint (Das, Bichhawat, Patel) compares DoT-integrated GMP 6.3.0 and OpenSSL 3.5.2 against stock versions with clang 14 -O2 -march=native on named Xeons, but the code is only at an anonymous review URL that could not be opened (robots-disallowed) and no venue is stated, so neither A nor B.
- **Verifier notes:** Numbers verified in Section 4.4 of the arXiv HTML. Record the shortcomings: no public repo or license, and the code was not verifiable.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** DoTMP (the GMP integration in arXiv 2604.21566) reports +7.8% on GMPbench (search snippet only); code still only at anonymous.4open.science.
- **Pages the verifier opened:**
  - <https://arxiv.org/html/2604.21566v1>
  - <https://arxiv.org/abs/2604.21566>
- **Sources the enricher read:**
  - <https://arxiv.org/html/2604.21566v1>
  - <https://arxiv.org/abs/2604.21566>
  - https://anonymous.4open.science/r/DigitsOnTurbo/ (robots-disallowed, not readable)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:digitsonturbo-dot`) · [data/wave8/enrich/raw/paper_digitsonturbo_dot.json](../../../data/wave8/enrich/raw/paper_digitsonturbo_dot.json) (enrichment confidence 0.6)

</details>
