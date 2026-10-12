# bigfft

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🔴 abandoned

> Pure-Go Schonhage-Strassen multiplication for math/big integers: 3-25x faster than math/big from 1 Mbit, 1.2-3x slower than GMP.

| | |
|---|---|
| **Beats** | Go math/big (README also benchmarks GMP, which is faster) |
| **Claimed result** | vs math/big multiplication: 1 Mb 105237800 ns -&gt; 28446400 ns (-72.97%), 10 Mb -89.43%, 100 Mb 147599836000 -&gt; 5921594000 ns (-95.99%); decimal scan of 1e6 digits 1776707489 -&gt; 144867502 ns (-91.85%). Versus GMP, bigfft is slower at every size (e.g. 1 Mb 12100000 ns GMP vs 22391830 ns bigfft; 100 Mb 2673000000 vs 5228991000 ns). |
| **Workload** | Multiplication of random big integers from 1 kB to 100 MB and decimal-string scanning of 10^3 to 10^7 digits, bigfft Schonhage-Strassen vs Go math/big and vs GMP. |
| **Metric** | latency |
| **Hardware** | Core 2 Quad Q8200 (2.33 GHz) for multiplication; Core i5-4590 for decimal scanning |
| **Adoption** | 92 stars |
| **Last commit** | 2023-01-29 |
| **Links** | [repository](https://github.com/remyoudompheng/bigfft) · [benchmark](https://github.com/remyoudompheng/bigfft) |

## Verdict

First-party Go benchmarks: on a Core 2 Quad Q8200 (Go version unstated), multiplication of equal-size random integers is 3.7x faster than math/big at 1 Mbit and 24.9x at 100 Mbit, but 1.85x-1.96x slower than GMP; a later Go 1.8 run on a Core i5-4590 (benchmarks/ directory) shows 3.0x-28.8x over math/big and 2.0x-2.6x slower than GMP 6.1.2 (gmpbench), all derived from page data. Decimal scanning is 12x faster than SetString at 1e6 digits on the i5-4590.

## Use it when

- A pure-Go program (no cgo) that multiplies integers of roughly 1 Mbit or more: README shows 3.7x at 1 Mbit and 24.9x at 100 Mbit over math/big on a Core 2 Quad (derived from page data).
- Parsing decimal strings of 100,000+ digits into big.Int: 12x faster at 1e6 digits and 56x at 1e7 digits than SetString on a Core i5-4590 (derived from benchmarks/scan.\*), with about 53x less allocation at 1e6 digits.
- Number-theory or pi-digit experiments in Go where cgo bindings to GMP are not allowed.
- Already pulled in transitively (modernc.org/sqlite uses it, per issue #22) and you want FFT products for your own big multiplications too.

## Skip it when

- C or C++ code: GMP is faster at every size the README measured (1.2x to 3.1x; bigfft 1.85x slower at 1 Mbit and 1.96x slower at 100 Mbit, derived from page data), and FLINT is faster still.
- Operands below about 1 Mbit: math/big is equal or faster; in the Go 1.8 run, bigfft.Mul at 1 kbit took 525 ns vs math/big's 298 ns (1.76x slower, derived from benchmarks/bench and bench.big).
- Division, modular exponentiation, GCD or decimal output: only multiplication and decimal input are provided (division request issue #20 is open).
- Production code that needs a maintained dependency: the author's README calls it a toy proof of concept, the last commit is 2023-01-29, and 5 issues and 4 PRs (loong64, gccgo, wasm) sit unanswered.
- gccgo builds: the package reaches into math/big's internal kernels with go:linkname, and the 2021 gccgo build fix (PR #14) was never merged; gccgo support after the 2023 linkname switch is not documented.

## How it is fast

Schonhage-Strassen: operands are cut into 2^k chunks and transformed with a recursive radix-2 FFT over the ring Z/(2^n+1) (fermat.go), where roots of unity are powers of two, so twiddle multiplications are bit shifts (with a sqrt(2) half-shift trick). Pointwise products are a single level that calls math/big's Karatsuba, not a recursive FFT. Inner loops reuse math/big's assembly kernels (addVV, subVV, mulAddVWW and others) via go:linkname. FromDecimalString splits the string in halves and multiplies by precomputed powers of 10, so parsing cost follows multiplication cost instead of math/big's quadratic digit loop.

## Compared with alternatives

Pick bigfft only in pure Go with Mbit-scale operands; holiman/uint256 is the Go sibling for fixed 256-bit math, and for C/C++ FLINT or GMP itself beat bigfft at every size, as do the GPU/NTT multipliers (TzdLanguage) on huge operands.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none outside the Go standard library (math/big internals via go:linkname) |
| **Minimum toolchain** | go.mod says go 1.12; CI was set up for Go 1.12, 1.17 and latest in January 2023 |
| **Platforms** | any GOARCH of the standard gc toolchain since the January 2023 switch from per-arch assembly stubs to go:linkname (no .s files remain in the repo root); gccgo not documented |
| **Thread safety** | not documented; Mul and FromDecimalString keep no package-level mutable state in fft.go/scan.go (each call allocates its own buffers), so concurrent calls on distinct inputs look safe, but this is not stated |
| **Drop-in for the baseline** | partial — bigfft.Mul(x, y) has the same semantics as new(big.Int).Mul(x, y) but every call site must be changed, and it always allocates a fresh result |

## Gotchas

- Depends on go:linkname into math/big internals (addVV, subVV, addVW, subVW, shlVU, mulAddVWW, addMulVVW). Go master keeps these symbols explicitly for bigfft ('hall of shame' comments citing go.dev/issue/67401), so builds work today, but the package relies on Go not removing them.
- FromDecimalString ignores the ok result of big.Int.SetString on each chunk and expects digits only: no sign, no error return, so malformed input yields a wrong number rather than an error.
- The FFT path switches on at 1800 words (about 115 kbit on 64-bit), a hard-coded package variable; the README says 200 kbits. Below that, Mul just calls math/big and adds an allocation.
- Old releases (pseudo-version v0.0.0-20170806...) used assembly jump stubs and fail on some setups with 'missing function body' (issue #21); use the 2023 commit.

## Known shortcomings

- README calls it a 'toy proof-of-concept'; slower than GMP at every size and loses to Go math/big below \~1 Mbit; Go.
- Below the threshold bigfft.Mul is up to 1.76x slower than math/big (allocates a new result each call); FromDecimalString ignores SetString's ok, so bad input gives a wrong number without error; relies on go:linkname into math/big internals; 2.0-2.6x slower than GMP 6.1.2 (benchmarks/ dir); abandoned 2023-01-29.

## Caveats and trade-offs

The author calls it 'a toy proof-of-concept implementation' of Schonhage-Strassen, not meant for production. It does not beat GMP: the README's GMP table shows GMP about 1.2x to 3.1x faster at every size (derived from page data: bigfft ns/op divided by GMP ns/op). Versus Go's math/big it only wins above roughly 1 Mbit (FFT switches on above 200 kbits; at 1 kb to 100 kb it is up to 4.9% slower), and decimal scanning is slower up to 1e4 digits. Old CPUs; Go version unstated; last commit 2023-01-29. Go library, not callable from C++ without cgo glue.

Go package using FFT (Schonhage-Strassen) multiplication above about 200 kbits and plugging into math/big types; the README says it is a toy proof of concept that is not expected to be used in production. Go only.

## Maintenance

Abandoned since January 2023 and self-described as a toy, but BSD-3-Clause, about 700 lines of Go (4 source files), used in production by modernc.org/sqlite (issue #22) and kept building because Go's math/big preserves its linkname targets.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables compare bigfft with Go math/big (and GMP) and name the CPUs (Core 2 Quad Q8200, Core i5-4590), but give no Go version or build settings; benchmark code exists only as the repo's Go test files, so the evidence falls short of A.
- **Verifier notes:** All quoted numbers match the README (math/big table, GMP table, decimal-scan table). Metadata confirmed on github.com: BSD-3-Clause, 92 stars, 20 forks, not fork/archived, last commit 2023-01-29 (abandoned by the &gt;3-year rule).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/README>
  - <https://github.com/remyoudompheng/bigfft>
  - <https://github.com/remyoudompheng/bigfft/commits>
- **Sources the enricher read:**
  - <https://github.com/remyoudompheng/bigfft>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/README>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/go.mod>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/arith_decl.go>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/fft.go>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/fermat.go>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/scan.go>
  - <https://github.com/remyoudompheng/bigfft/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/benchmarks/bench>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/benchmarks/bench.big>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/benchmarks/bench.fft>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/benchmarks/bench.gmp>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/benchmarks/scan.big>
  - <https://raw.githubusercontent.com/remyoudompheng/bigfft/HEAD/benchmarks/scan.bigfft>
  - <https://github.com/remyoudompheng/bigfft/issues?q=is%3Aissue>
  - <https://github.com/remyoudompheng/bigfft/issues/21>
  - <https://github.com/remyoudompheng/bigfft/issues/22>
  - <https://github.com/remyoudompheng/bigfft/pulls>
  - <https://github.com/remyoudompheng/bigfft/commits/master>
  - <https://raw.githubusercontent.com/golang/go/master/src/math/big/arith_decl.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/math/big/arith.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/math/big/natmul.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/math/big/natconv.go>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/remyoudompheng/bigfft`) · [data/wave8/enrich/raw/github_com_remyoudompheng_bigfft.json](../../../data/wave8/enrich/raw/github_com_remyoudompheng_bigfft.json) (enrichment confidence 0.8)

</details>
