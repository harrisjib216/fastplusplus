# Swift-BigInt (BInt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Swift` · `MIT` · 🟢 active

> Pure-Swift arbitrary-precision integers (BInt) and fractions (BDouble), claimed about 2x faster than mini-gmp, not full GMP.

| | |
|---|---|
| **Beats** | mini-gmp (GMP's portable minimal subset without assembly kernels); the README says full GMP was not counted because it needs to be installed and is not portable |
| **Claimed result** | README 'About performance': 'BInt about twice as fast as mini-gmp, as of now (not counting the normal gmp, because it needs to be installed and is not portable). For example, BInt can add numbers about 2 times faster than GMP (272ms vs 530ms for fib(100,000)), and multiplication is more than twice as fast. When given the task of calculating and printing factorials successively, BInt performs significantly better than GMP.' In context 'GMP' in the later sentences refers to the mini-gmp comparison; no comparison with full GMP is claimed. |
| **Workload** | README claim: fib(100,000) via big-integer addition, multiplication, and successive factorials with printing, BInt vs mini-gmp. The repo's Sources/Benchmarks (Benchmarks.swift, main.swift) time BInt-only workloads (factorial of 40,000, Fib 100000, 10^300000, matrix power, Mersenne search) for regression comparison and contain no GMP or mini-gmp code. |
| **Metric** | throughput |
| **Adoption** | 259 stars |
| **Last commit** | 2026-03-29 |
| **Links** | [repository](https://github.com/mkrd/Swift-BigInt) · [benchmark](https://github.com/mkrd/Swift-BigInt) |

## Verdict

The only comparison is one first-party README sentence: BInt is about 2x faster than mini-gmp (GMP's portable C subset without assembly), adding via fib(100,000) in 272 ms vs 530 ms and multiplying more than twice as fast. No hardware, compiler, build mode, date or comparison harness is given; the repo's benchmarks time only BInt against its own saved baseline.

## Use it when

- Swift apps on iOS, macOS, watchOS, tvOS or Linux that need big integers or exact rationals without linking GMP, for licensing or packaging reasons.
- Moderate-size combinatorics, factorials, Fibonacci or exact-fraction arithmetic where multiplication and addition dominate.
- Teaching or prototyping, where a single readable source file you can vendor beats a C dependency.
- Generic Swift code over BinaryInteger that should also work with arbitrary-size integers.

## Skip it when

- Anything in C or C++: Swift only, with no C ABI. Use Boost.Multiprecision, mp++, FLINT or GMP instead.
- Division-heavy or modular work (mod_exp, gcd on large values, modulo loops): multi-limb divMod is a bit-at-a-time shift-subtract loop with a full remainder shift per bit, so it is quadratic with a large constant. There is no Knuth Algorithm D, Barrett/Montgomery or subquadratic division.
- Very large operands (millions of digits): no Toom-Cook or FFT multiplication beyond Karatsuba, and quadratic base-10^18 string conversion.
- Cryptography: arithmetic is not constant-time and mod_exp is plain square-and-multiply over the slow division.
- Workloads that need proven correctness: the tracker shows past wrong-result bugs (#78, Int(5) += BInt(10) gave 20; #80, a comparison returned the wrong answer for a variable Int vs a BInt, closed 2026-03-29), and #83 (BDouble nthroot(1024000, 2) loops forever) is still open.

## How it is fast

Multiplication is Karatsuba above 48 limbs and schoolbook below, on 64-bit limbs using multipliedFullWidth. Decimal I/O works in base 10^18 chunks. Addition and multiplication skip zero limbs. The baseline, mini-gmp, is GMP's portable subset without assembly kernels, so the comparison measures portable code against portable code. A 2026-03 rewrite (PR #90) reported 70x on its own Fib 100000 benchmark, 6.5x on 270k-bit multiplication and 3.56x on factorial of 40,000 against the previous BInt, but division was unchanged (0.99x).

## Compared with alternatives

Pick it only for Swift projects that cannot link GMP; every sibling in the catalog is C, C++ or Rust, and in C++ Boost.Multiprecision cpp_int or mp++ fill the same 'no external GMP' role with far better division and stronger evidence. Rust users have Malachite, ibig or dashu, which carry measured comparisons against real GMP.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Foundation; Glibc on Linux) |
| **Minimum toolchain** | Swift 5.5+ in practice, since BInt and BDouble declare Sendable; Package.swift and the podspec still say Swift 4.2 and the README says Xcode 9+/Swift 4+. Podspec targets iOS 11, macOS 10.11, watchOS 4, tvOS 11. |
| **Platforms** | Apple platforms and Linux; any CPU Swift targets (pure Swift, no assembly or SIMD) |
| **Thread safety** | BInt and BDouble are value types declared Sendable, but BDouble.precision is a mutable global static that is not synchronised; not otherwise documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark numbers in the README (fib(100,000): 272 ms vs 530 ms for mini-gmp) predate the 2026-03 performance rewrite and give no hardware or build mode. The README says debug builds are more than 10x slower than release, so measure in release (-O).
- In the README's performance paragraph 'GMP' means mini-gmp; full GMP was deliberately not compared and would likely win on large operands.
- BDouble is an exact rational that auto-reduces by gcd, so long chains of operations grow numerators and denominators, and every gcd uses the slow division. pow and nthroot on BDouble are only accurate to the precision setting (docs say to compare with nearlyEqual).
- Errors stop the program rather than being recoverable: division by zero, negative exponents and invalid bases trigger precondition or fatalError traps; String initialisers return nil on bad input.

## Known shortcomings

- Baseline is really mini-gmp (README says full GMP is not counted; no GMP code in the repo), so the record's 'beats GMP' framing was wrong; Swift.
- README fib numbers are stale (predate the PR #90 rewrite; Fib 100000 is now 70x faster); multi-limb divMod is bit-by-bit O(n^2); correctness history #78 (Int(5)+=BInt(10) gave 20) and #80 comparison bug, #83 nthroot infinite loop still open; not constant-time; needs Swift 5.5+ though manifests say 4.2.

## Caveats and trade-offs

The baseline is mini-gmp, not full GMP (the README explicitly excludes normal GMP), so this is not a GMP-beater. First-party README sentence only: no hardware, compiler, build configuration, date or comparison code; the README notes release builds run more than 10x faster than Xcode debug builds. Swift library, not callable from C++ directly.

Swift-only arbitrary-precision integers and fractions (BInt, BDouble) with an operator-based API; unusable from C++ without a bridge. No assembly, portable.

## Maintenance

Maintained (v2.4.0 and a large performance rewrite merged 2026-03-29, 259 stars, MIT); one Swift file small enough to vendor, but irrelevant to C++ users and with a history of correctness bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The only numbers are one first-party README sentence (272 ms vs 530 ms for fib(100,000)) with no hardware, compiler, build mode or comparison code; Sources/Benchmarks/Benchmarks.swift only times BInt itself against a saved BInt baseline and contains no GMP or mini-gmp code.
- **Verifier notes:** Downgraded for overstated baseline: the record framed GMP as the baseline, but the README's numbers are against mini-gmp and say full GMP was not counted; tier stays C. Metadata confirmed on github.com: MIT, 259 stars, 59 forks, not fork/archived, last commit 2026-03-29 ('Performance improvements (#90)').
- **Fields the verifier corrected:** `baseline`, `baseline_in_list`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mkrd/Swift-BigInt/HEAD/README.md>
  - <https://github.com/mkrd/Swift-BigInt>
  - <https://github.com/mkrd/Swift-BigInt/commits>
  - <https://github.com/mkrd/Swift-BigInt/tree/master/Tests>
  - <https://github.com/mkrd/Swift-BigInt/tree/master/Tests/BigNumberTests>
  - <https://github.com/mkrd/Swift-BigInt/tree/master/Sources>
  - <https://github.com/mkrd/Swift-BigInt/tree/master/Sources/Benchmarks>
  - <https://raw.githubusercontent.com/mkrd/Swift-BigInt/HEAD/Sources/Benchmarks/Benchmarks.swift>
  - <https://raw.githubusercontent.com/mkrd/Swift-BigInt/HEAD/Sources/Benchmarks/main.swift>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mkrd/Swift-BigInt/HEAD/README.md>
  - <https://raw.githubusercontent.com/mkrd/Swift-BigInt/HEAD/Sources/BigNumber/Swift-Big-Number-Core.swift>
  - <https://raw.githubusercontent.com/mkrd/Swift-BigInt/HEAD/Package.swift>
  - <https://raw.githubusercontent.com/mkrd/Swift-BigInt/HEAD/Swift-BigInt.podspec>
  - <https://github.com/mkrd/Swift-BigInt/tree/master/Sources>
  - <https://github.com/mkrd/Swift-BigInt/tree/master/Sources/BigNumber>
  - <https://github.com/mkrd/Swift-BigInt/issues?q=is%3Aissue>
  - <https://github.com/mkrd/Swift-BigInt/issues/80>
  - <https://github.com/mkrd/Swift-BigInt/issues/78>
  - <https://github.com/mkrd/Swift-BigInt/pull/90>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mkrd/swift-bigint`) · [data/wave8/enrich/raw/github_com_mkrd_swift_bigint.json](../../../data/wave8/enrich/raw/github_com_mkrd_swift_bigint.json) (enrichment confidence 0.75)

</details>
