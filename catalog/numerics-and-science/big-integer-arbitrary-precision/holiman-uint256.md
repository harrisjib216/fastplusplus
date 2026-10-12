# uint256 (holiman)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Allocation-free fixed 256-bit unsigned integer type for Go; 1.2-17x faster than math/big.Int on 256-bit arithmetic.

| | |
|---|---|
| **Beats** | Go math/big (big.Int) |
| **Claimed result** | README: 'uint256 wins over math/big in every single case, often with orders of magnitude' (as of 2020-03-18). Examples: Add/single 1.99 ns vs 18.11 ns (-89.02%), Mul/single 12.10 ns vs 57.69 ns (-79.03%), Square/single 12.49 ns vs 56.10 ns (-77.74%), SDiv/large 94.64 ns vs 642.10 ns (-85.26%), FromDecimalString 7973 ns vs 32850 ns (-75.73%), zero allocations. |
| **Workload** | Go benchmarks (go test -bench) of fixed 256-bit unsigned arithmetic: add, sub, mul, square, div, sqrt, shifts, bitwise ops, hex/decimal conversion, uint256 vs big.Int with time/op, B/op and allocs/op. |
| **Metric** | latency |
| **Adoption** | 383 stars; used by go-ethereum and erigon |
| **Last commit** | 2026-08-23 |
| **Links** | [repository](https://github.com/holiman/uint256) · [benchmark](https://github.com/holiman/uint256) |

## Verdict

First-party `go test -bench` tables in the README compare uint256.Int with Go's math/big.Int on fixed 256-bit inputs and show uint256 faster on every listed row, from -18.6% (MulMod/mod64) to -94.2% (Exp/small, about 17x), e.g. Add 1.99 vs 18.11 ns, Mul 12.10 vs 57.69 ns, SDiv/large 94.64 vs 642.10 ns, with zero allocations on most rows; the README gives the commands but no CPU, OS or Go version, and the status line is dated 2020-03-18.

## Use it when

- EVM, blockchain or cryptographic Go code whose values are always at most 256 bits (balances, hashes as integers, gas math).
- Hot loops where big.Int allocations dominate: SDiv, Sqrt, Exp, MulMod and decimal parsing go from several allocations per op to zero.
- Simple 256-bit add/sub/mul/compare in Go, where the README shows about 2 ns vs 17-18 ns (add/sub) and 12.1 vs 57.7 ns (mul).
- Modular arithmetic with 256-bit moduli, e.g. MulMod/mod256 188.8 ns vs 489.2 ns, or about 77 ns when the reciprocal is reused (MulModWithReciprocal).

## Skip it when

- Values that can exceed 256 bits or need arbitrary precision: results silently wrap modulo 2^256 unless you use the \*Overflow variants.
- C or C++ projects: it is a pure Go package with no C API; a C++ codebase would look at fixed-width C++ types instead.
- Code that relies on big.Int's divide-by-zero panic: Div, Mod, DivMod, AddMod and MulMod return 0 for a zero divisor.
- Decimal formatting-heavy workloads expecting large wins: ToDecimal is only 19% faster than big.Int and still allocates (248 allocs/op in the README table).
- Workloads dominated by 64-bit-modulus MulMod: only 18.6% faster (91.7 vs 112.6 ns).

## How it is fast

Values live in a fixed four-word array, so operations are straight-line code over 4 limbs using math/bits intrinsics (Add64, Sub64, Mul64) with no heap allocation, length checks or normalisation, unlike big.Int's variable-length slices. Division uses Knuth-style long division with a reciprocal-based 2-by-1 step ported from chfast/intx ('Improved division by invariant integers', Algorithm 4), and MulMod for 192-256-bit moduli reduces the 512-bit product with a precomputed 320-bit reciprocal refined by Newton-Raphson. There is no Go assembly; the README says assembly is deferred.

## Compared with alternatives

Pick uint256 only when you are writing Go and need 256-bit words; for C++ the catalogued fixed-width options are ctbignum (constexpr, compile-time limb count), Boost.Multiprecision fixed cpp_int and Unsigned Bigint (ADX/BMI2), and the arbitrary-precision siblings (GMP-beating mp++, FLINT, ibig/malachite in Rust) solve a different, variable-width problem.

## Integration

| | |
|---|---|
| **Form** | module (Go package github.com/holiman/uint256) |
| **Dependencies** | none outside the Go standard library (math/bits, math/big, encoding/binary) |
| **Minimum toolchain** | Go 1.19 (go.mod) |
| **Platforms** | any Go target (pure Go, no assembly) |
| **Thread safety** | not documented; Int is a plain value array mutated in place by its methods, so shared instances need external synchronisation |
| **Drop-in for the baseline** | partial: method names mirror big.Int (z.Op(x, y)) and FromBig/ToBig convert, but the type is fixed-width and unsigned with wrap-around, and zero-divisor and String/marshal behaviour differ in places |

## Gotchas

- Division and modulo by zero return 0 instead of panicking (documented as 'OBS: differs from the big.Int').
- SetBytes with more than 32 bytes silently keeps the last 32 bytes; FromBig reports overflow through a bool, while MustFromBig panics.
- The README benchmark tables date from 2020 (no CPU, Go version or OS given), and v1.3.0 later changed Mul, Exp and DivMod, so current numbers may differ in either direction.
- The big.Int baselines differ slightly per benchmark: Add/single lets the big.Int grow without truncation, while Mul truncates to 256 bits with a helper, so per-row ratios are not perfectly like-for-like.

## Known shortcomings

- 'Orders of magnitude' not borne out: max \~17x (Exp/small), some rows only \~19%; baseline Go math/big; Go.
- 2020 tables; big.Int Add baseline grows untruncated while Mul is truncated, so rows are not exactly like-for-like.

## Caveats and trade-offs

Baseline is Go's math/big, not GMP or MPFR, so baseline_in_list is false; included as the incumbent for Go big-integer use. The README gives the benchmark commands (go test -run - -bench . -benchmem) but no CPU model or Go version for the tables; the only date is 'As of 2020-03-18' in the status line. The 'orders of magnitude' wording is not borne out by the tables: the largest gain is Exp/small at -94.21% (about 17x), and some rows are small (MulMod/mod64 -18.60%, Decimal/ToDecimal -19.23%). Fixed-width versus arbitrary-width comparison favors the specialised type. Go library, not callable from C++ directly.

Fixed 256-bit width only (not arbitrary precision), alloc-free value type replacing big.Int in Ethereum clients; overflow wraps modulo 2^256.

## Maintenance

Actively maintained (last commit 2026-08-23, 352 commits, latest tagged release v1.3.2 fixing an unmarshalling overflow) and BSD-3-Clause; production-hardened through go-ethereum and erigon, with 100% test coverage claimed since v1.0.0 and an OSS-Fuzz script in the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README benchmark tables (u256 vs big.Int time/op, B/op, allocs/op) with the go test -bench commands, but no CPU model, Go version or date for the tables, so short of A.
- **Verifier notes:** All quoted rows (Add/single, Mul/single, Square/single, SDiv/large, FromDecimalString) match the README. Metadata confirmed on github.com: BSD-3-Clause, 383 stars, 82 forks, last commit 2026-08-23; README names go-ethereum and erigon as users.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/README.md>
  - <https://github.com/holiman/uint256>
  - <https://github.com/holiman/uint256/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/README.md>
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/go.mod>
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/uint256.go>
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/mod.go>
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/div.go>
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/conversion.go>
  - <https://raw.githubusercontent.com/holiman/uint256/HEAD/benchmarks_test.go>
  - <https://github.com/holiman/uint256>
  - <https://github.com/holiman/uint256/issues?q=is%3Aissue+bug>
  - <https://github.com/holiman/uint256/releases>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/holiman/uint256`) · [data/wave8/enrich/raw/github_com_holiman_uint256.json](../../../data/wave8/enrich/raw/github_com_holiman_uint256.json) (enrichment confidence 0.8)

</details>
