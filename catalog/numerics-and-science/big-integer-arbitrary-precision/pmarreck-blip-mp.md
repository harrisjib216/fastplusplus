# blip_mp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Zig` · `no license` · 🟢 active

> Pure-Zig arbitrary-precision integers stored as variable-length BLIP bytes; beats GMP mpz on Apple M4 at i64-sized and 128-8192-bit add/sub/mul.

| | |
|---|---|
| **Beats** | GMP 6.3.0 (mpz_t; built with assembly and with --disable-assembly) |
| **Claimed result** | Apple M4 vs GMP with assembly, from RESULTS.md. All i64-fitting adds are 1.95-2.66x faster (RESULTS.md: immediate add 2.06 ns vs 4.83 ns, 2.34x). Mul: 12 of 15 sizes from 128 to 8192 bits are faster, including RSA-1024 1.20x (210 vs 252 ns), RSA-2048 1.19x (673 vs 800 ns), RSA-3072 1.37x (1265 vs 1733 ns) and 1536 bits 1.45x; 16384 bits is 0.87x and 32768 bits 0.55x. Sub is 1.03-2.11x faster from 256 to 8192 bits (768 bits: 4.38 vs 9.23 ns). Add is 1.04-1.28x faster at 768 bits and above. powm is 13% faster at 2048 bits (3333 vs 3839 us), 3% at 1024 and 8% at 3072. The public Mp.divMod is 1.25-2.00x SLOWER than mpz_tdiv_qr from 256 to 8192 bits (2048: 526.7 vs 416.5 ns). The README's 'divMod 1.31x' is blip vs GMP-noasm on x86 (452.8 vs 593.2 ns), and its '24% faster long division' is a limb-only inner kernel (\~470 vs 614 ns). invMod is 3.25-5.36x slower. On Zen 4 vs GMP with assembly, only i64-fitting adds win (immediate add 3.36 vs 4.44 ns); mul at 2048-32768 bits loses by 2.24-3.36x, powm at 2048 by 1.99x and divMod at 2048 by 2.09x. |
| **Workload** | Own bench executable (blip_mp_bench) timing add/sub/mul/divMod/powm/invMod on pre-built pools of values at sizes from i64-range up to 98304 bits, e.g. 5M iterations of r = pool[i % 256] + pool[(i+1) % 256], against mpz_\* in a C program using the same libc malloc. |
| **Metric** | latency |
| **Hardware** | Apple M4, aarch64-darwin (stated in RESULTS.md and BENCHMARK_RESULTS.md Run 17); cross-check on an AMD Ryzen 9 7940HS (Zen 4) Framework laptop under NixOS (BENCHMARK_RESULTS.md Run 18) |
| **Compiler and flags** | Zig 0.16.0, zig build bench -Doptimize=ReleaseFast (tests/benchmark/blip_mp_bench.zig); GMP harness tests/benchmark/gmp_bench.c compiled with -O3 -Wall -Wextra and linked against nixpkgs GMP (nixos-unstable pinned in flake.lock rev 1c3fe55a) and against a --disable-assembly GMP override; libc malloc on both sides; run via nix build .#bench; 3-run hand medians |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/pmarreck/blip_mp) · [benchmark](https://github.com/pmarreck/blip_mp/blob/yolo/RESULTS.md) |

## Verdict

On an Apple M4 with Zig 0.16.0 ReleaseFast against nixpkgs GMP 6.3.0 (with and without assembly, harness built at -O3, libc malloc on both sides), the author's 3-run medians show i64-range adds 1.95-2.66x faster, 12 of 15 mul sizes from 128 to 8192 bits faster (RSA-2048 mul 673 vs 800 ns), and 2048-bit powm 13% faster, while full divMod is 1.25-2.00x and invMod 3.25-5.36x slower. A Zen 4 rerun of the same Nix package shows GMP-with-asm winning everything except i64-sized adds.

## Use it when

- Zig code on Apple Silicon that does large numbers of operations on values that mostly fit in an i64 but may overflow (accumulators, counters, exact arithmetic): adds measured 1.95-2.66x faster than GMP-with-asm on an M4.
- aarch64 workloads dominated by 384-8192-bit multiplication or 256-8192-bit subtraction, where RESULTS.md shows 1.08-1.56x (mul) and 1.03-2.11x (sub) wins over GMP-with-asm on an M4.
- Projects that want arbitrary-precision integers without linking LGPL GMP and can accept a pure-Zig dependency (or its C static library).
- Protocols where the integer's serialized BLIP bytes are the wire format, so you skip an mpz_export/mpz_import round-trip.

## Skip it when

- x86-64: on a Zen 4 laptop GMP's assembly beats blip_mp by 1.5-4x at 1024-8192-bit add, mul, divMod and powm (RSA-2048 powm about 3.8 ms vs 1.9 ms); only i64-sized adds win there.
- Division-heavy or modular-inverse-heavy code: full Mp.divMod is 1.25-2.00x slower than mpz_tdiv_qr at 256-8192 bits even on the M4, and invMod is 3.25-5.36x slower than mpz_invert.
- Operands of 16K bits and above (mul 0.87x at 16384 and 0.55x at 32768 bits): FFT multiplication exists but is gated off, so large-number workloads should stay on GMP or FLINT.
- Secret-dependent cryptography: powm uses sliding-window exponentiation and no constant-time mode or side-channel analysis is documented.
- Anything you need to ship legally today: there is no LICENSE file (the README says MIT or Apache-2.0 'TBD before tagging a release'), version 0.0.1, no tagged release, one star.

## How it is fast

Small-buffer optimization: a 72-byte Mp struct holds values up to 24 encoded bytes inline, and maintains a sign-extended i64 copy at inline_buf[1..9] so i64-range arithmetic is one 64-bit load plus native overflow-checked math, with no malloc round-trip. Larger values use byte-direct two's-complement add/sub that reads u512/u256/u128/u64 chunks straight from the payload (compiling to ADCS carry chains on aarch64), direct-write into the result heap buffer via a header offset, Karatsuba with a carry-bit trick that keeps sub-products 8-byte aligned, Toom-3 above 16K bits, and cached payload metadata to skip header parsing. powm uses CIOS Montgomery multiplication with sliding windows and dedicated squaring; division is u64-base Knuth Algorithm D with Moller-Granlund reciprocal quotient estimates; invMod is a wider-window Lehmer extended Euclid.

## Compared with alternatives

Pick blip_mp over the Rust small-value libraries (dashu, ibig, Malachite) only when you are in Zig or want a C ABI without Rust, and over ctbignum when widths are not known at compile time; for C++ code that wants small-value speed with GMP-class large-operand performance, mp++ (SBO over GMP) is the safer choice, and on x86-64 none of blip_mp's mid-size wins hold.

## Integration

| | |
|---|---|
| **Form** | module (Zig package via build.zig.zon) or static lib with C header include/blip_mp.h |
| **Dependencies** | none for the library (libc for the C API's malloc/free); GMP and Nix only for benchmarks and cross-checks |
| **Minimum toolchain** | build.zig.zon declares minimum_zig_version 0.15.0; benchmarks and docs use Zig 0.16.0 via Nix |
| **Platforms** | Validated on aarch64-darwin (Apple M4) and x86_64-linux (Zen 4); README says Garnix CI cross-builds aarch64/x86_64 Linux, Darwin and Windows. Fast paths are tuned for Apple Silicon; NEON FFT code is gated off. |
| **Thread safety** | not documented; each Mp carries its own allocator, the FFT scratch cache is thread-local (CODE_MINIMAP.md) and the README mentions per-thread scratch caches, but no guarantee for sharing one Mp across threads is stated |
| **Drop-in for the baseline** | partial — covers most mpz integer operations with GMP-matching semantics, but a different type, function names and error-code convention; no mpf/mpfr equivalents |

## Gotchas

- The README headline overstates results: its 'RSA-2048 trifecta' divMod win (1.31x) is blip vs GMP-noasm on x86, and the '24% faster long division' is a limb-only inner kernel; RESULTS.md's own table has full Mp.divMod 1.26x slower than GMP at 2048 bits on the M4. Its 'honest losses' list (128-256-bit mul 0.40-0.67x) is stale against RESULTS.md (128-bit mul 1.38x faster).
- 128-bit add and sub are still slower than GMP (0.56x and 0.65x) because of the heavier 72-byte struct and per-op bookkeeping; the win zone starts at i64 values and resumes around 256-768 bits.
- blip_mp_set_u64 returns BLIP_MP_ERR_OUT_OF_RANGE for values above INT64_MAX, and pointers from blip_mp_bytes() are invalidated by the next mutating call on that handle.
- Benchmarks are 3-run hand medians (hyperfine aggregation is listed as a to-do), and the docs disagree on cross-check counts (8240, 12029, 13029) and on whether rationals are supported.

## Known shortcomings

- README overstates the claim: 'divMod 1.31x' is x86 vs GMP built without asm and '24% faster' is a limb-only inner kernel; the public divMod is 1.25-2.00x slower than GMP on M4; wins are Apple-Silicon-only (Zen 4 vs GMP with asm loses 1.5-4x); stale losses list and internal number conflicts; no LICENSE file (reference); Zig, not C++.
- RESULTS.md TL;DR contradicts its own table (claims a win on RSA-2048 divMod; table shows 1.26x slower); docs disagree on rational support; powm is variable-time sliding window with no constant-time mode (unsafe for secret exponents).

## Caveats and trade-offs

First-party 3-run hand medians, and the author lists hyperfine aggregation as to-do. The README headline mixes runs and machines. Its RSA-2048 'trifecta' divMod win (1.31x) is not supported on Apple Silicon, where RESULTS.md's own table shows the full divMod 1.26x slower. The '24% faster' long-division figure is an inner-kernel microbenchmark against a GMP timing (614 ns) about 1.5x higher than the 400-417 ns mpz_tdiv_qr timings in other tables. The README's 'honest losses' list (128-256-bit mul 0.40-0.67x) is stale against RESULTS.md (128-bit mul 1.38x faster). BENCHMARK_RESULTS.md Run 17's sub table has raw timings that contradict its ratios (256 bits: 6.87 ns vs 5.49 ns is marked a 1.28x win). Cross-check counts differ between documents (8240, 12029, 13029). The wins are Apple Silicon only: on Zen 4, GMP's assembly is 1.65-3.88x faster than GMP-noasm, and blip_mp loses every tier-3 size to it by 1.5-4x. Modular inverse is 2.5-5x slower than GMP. There is no LICENSE file; the README says 'MIT or Apache-2.0 (TBD before tagging a release)', so usability is reference. The repo has 1 star, the project is research-grade, and the benchmark runs are dated 2026-05-02 to 2026-05-04.

Variable-length self-describing byte storage with small-buffer optimization instead of limb arrays; pure Zig, no inline assembly, C FFI exists. Integers only (no mpf/mpq/mpfr). FFT multiplication is implemented but disabled because Toom-3 still wins in the supported range, so it falls behind GMP past \~16K bits. Win is specific to Apple Silicon: on x86_64 GMP's hand-written assembly beats it by 1.5-4x on large operands.

## Maintenance

Actively developed by one author (last commit 2026-09-27, mostly feature work through June 2026) as a research-grade 0.0.1 library with no license file yet, so treat it as reference material until a release with a license is tagged.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Upgraded C to A. The benchmark code is public: tests/benchmark/blip_mp_bench.zig and tests/benchmark/gmp_bench.c, built by build.zig's bench step and flake.nix packages.bench. Zig 0.16.0 is used with -Doptimize=ReleaseFast, and the GMP harness is compiled with -O3. nixpkgs is pinned in flake.lock (rev 1c3fe55a), which fixes the GMP build, plus a --disable-assembly variant. RESULTS.md and BENCHMARK_RESULTS.md Run 17 name the CPU as an Apple M4, and Run 18 names an AMD Ryzen 9 7940HS. The numbers are first-party 3-run hand medians, and the README overstates some of them (see claimed_speedup).
- **Verifier notes:** Real entry with a reproducible harness, so the tier rises to A. The claim was overstated, though: drop the divMod win and treat 'long division 24% faster' as an inner-kernel-only result; this is worth recording as a shortcoming. License null and usability reference are confirmed (LICENSE, LICENSE-MIT, LICENSE-APACHE, LICENSE.md and COPYING all 404, and none is in the root listing). Last commit 2026-09-27, 1 star, active.
- **Fields the verifier corrected:** `benchmark_url`, `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pmarreck/blip_mp>
  - <https://github.com/pmarreck/blip_mp/tree/yolo>
  - <https://github.com/pmarreck/blip_mp/commits/yolo>
  - <https://github.com/pmarreck/blip_mp/blob/yolo/RESULTS.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/README.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/flake.lock>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/build.zig>
- **Sources the enricher read:**
  - <https://github.com/pmarreck/blip_mp>
  - <https://github.com/pmarreck/blip_mp/commits/yolo>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/README.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/build.zig>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/include/blip_mp.h>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/CODE_MINIMAP.md>
  - <https://raw.githubusercontent.com/pmarreck/blip_mp/HEAD/SPEC.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/pmarreck/blip_mp`) · [data/wave8/enrich/raw/github_com_pmarreck_blip_mp.json](../../../data/wave8/enrich/raw/github_com_pmarreck_blip_mp.json) (enrichment confidence 0.8)

</details>
