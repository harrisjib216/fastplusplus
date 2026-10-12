# hx (binary-to-hex-simd, NEON table lookup)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `GPL-3.0` · 🔴 abandoned

> Hobby Rust crate that hex-encodes bytes with an AArch64 NEON tbl lookup in inline asm, \~7.9x its own scalar loop.

| | |
|---|---|
| **Beats** | naive byte-by-byte hex encoding |
| **Claimed result** | neon_tbl 6.24 GiB/s vs byte_by_byte 0.79 GiB/s (\~7.9x, derived from page data); portable_simd 3.46 GiB/s (\~4.4x, derived from page data). The best single run was 1,794,971 ns for 12 MiB, i.e. 6.53 GiB/s. |
| **Workload** | Converting 12 MiB of binary data to ASCII hexadecimal, comparing byte-by-byte, portable_simd, and hand-written NEON table-lookup (neon_tbl) implementations |
| **Metric** | throughput |
| **Hardware** | Apple M1 MacBook (author notes it was not a quiet machine, on battery power) |
| **Compiler and flags** | Rust nightly required (#![feature(portable_simd)] and #![feature(test)] in src/lib.rs); rustc version and flags not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2023-01-25 |
| **Links** | [repository](https://github.com/eddieantonio/binary-to-hex-simd) · [benchmark](https://github.com/eddieantonio/binary-to-hex-simd#readme) |

## Verdict

On an Apple M1 MacBook (on battery, not a quiet machine), nightly cargo bench over 12 MiB of random bytes measured the repo's own branchy scalar loop at 14.86 ms per iteration (0.79 GiB/s), the std::simd arithmetic version at 3.39 ms (3.46 GiB/s) and the NEON tbl asm at 1.88 ms (6.24 GiB/s). That is about 7.9x and 4.4x over scalar, with a best single run of 6.53 GiB/s. The rustc version and flags are not given, and nothing was compared against the hex crate, const-hex or std formatting.

## Use it when

- Learning material: about 100 lines that show a NEON tbl hex encoder, Rust inline asm (asm!, clobber_abi, post-indexed ldp/stp) and a cargo bench harness comparing it with std::simd and scalar code on the same 12 MiB input.
- Reproducing or extending the M1 experiment (0.79 -&gt; 3.46 -&gt; 6.24 GiB/s) on an AArch64 machine with a Rust nightly toolchain.
- As a sketch to port the five-instruction core (ushr/and/zip/tbl/stp) into your own code after fixing the over-read and asm-operand issues listed under gotchas, and only if GPL-3.0 is acceptable for the copied code.

## Skip it when

- Any production use. The sibling const-hex uses the same NEON technique (vqtbl1q_u8 lookup plus vzipq_u8) through intrinsics on stable Rust 1.64+, with runtime NEON detection, x86 SIMD paths, lower- and upper-case output, validated decoding and an MIT OR Apache-2.0 license.
- x86-64 or other non-AArch64 targets. neon_tbl.rs is compiled unconditionally and contains AArch64 asm, and to_ascii_hex picks the backend with cfg!() (both branches are compiled), so as written the crate should fail to build there even though a portable_simd fallback exists. This is inferred from the source and was not tested.
- Stable Rust, or a current nightly without edits. lib.rs needs #![feature(portable_simd)] and #![feature(test)], and portable_simd.rs imports std::simd::SimdPartialOrd, which current nightly docs list only under std::simd::cmp and the prelude. No toolchain is pinned and there is no Cargo.lock.
- Projects under MIT, Apache or other permissive licenses, because the code is GPL-3.0.
- When you need lower-case hex (what the hex crate and {:02x} produce), decoding, or an allocation-free API.

## How it is fast

The neon_tbl loop takes 16 input bytes per iteration. It splits them into high-nibble and low-nibble vectors (ushr #4 and and 0x0F), interleaves those into output order with zip1/zip2, then runs two tbl.16b lookups against the 16-byte table "0123456789ABCDEF" held in a register, and writes all 32 output bytes with one stp. This is the standard SIMD shuffle-table hex encoder (pshufb on x86), hand-written as Rust inline asm; the first len % 16 bytes are converted scalar before the loop. The portable_simd variant computes digits arithmetically instead (a nibble &gt;= 10 compare selects an offset of 'A'-10 or '0', which is then added) on std::simd u8x16 and interleaves the results. The baseline pushes two bytes per input byte into a Vec, with one branch per nibble.

## Compared with alternatives

Only as a teaching reference. For real code pick const-hex (the same NEON tbl technique plus x86 SIMD and decoding on stable Rust, permissively licensed), or fast-hex (zbjornson) for C++ on AVX2. hx's only unique value is its side-by-side comparison of std::simd and hand-written NEON asm.

## Integration

| | |
|---|---|
| **Form** | source-drop (an unpublished crate named hx; it could be used as a git dependency) |
| **Dependencies** | None at runtime. Dev-dependencies are fastrand 1.8 and lazy_static 1.4. Cargo.toml also declares a cc 1.0.78 build-dependency, but the tree has no build.rs; it is left over from a C extension removed in January 2023. |
| **Minimum toolchain** | Rust nightly, edition 2021, with the portable_simd and test features. The nightly version is not pinned; the code comments date it to 2023-01-24. |
| **Platforms** | In practice AArch64 with NEON only; benchmarked on an Apple M1. The portable_simd path is written for any target but cannot be reached on non-AArch64 targets while neon_tbl is compiled unconditionally. |
| **Thread safety** | Not documented. Every function takes an input slice and returns a new String with no shared mutable state, so concurrent calls look safe from the source. |
| **Drop-in for the baseline** | partial — same shape as the in-repo byte_by_byte (slice in, upper-case String out), but not a drop-in for hex::encode or format!("{:02x}"), which produce lower-case output |

## Gotchas

- The asm loop loads with `ldp q0, q1, [src], #16`, which reads 32 bytes but advances only 16, and q1 is never used. The last iteration therefore reads 16 bytes past the end of the input slice. That is an out-of-bounds read that can fault when the input ends at a page boundary, and it also doubles load traffic.
- The asm post-increments the source and destination pointers and decrements the length counter in operands declared only as in(reg). The Rust Reference says registers not declared as outputs must hold the same value on exit, or behavior is undefined. The code only works when register allocation happens to overlap those inputs with clobber_abi("C") lateouts, which the Reference says code should not rely on.
- Test coverage is one 57-byte vector checked across all three implementations plus two 4-byte doc-tests, which never reach the SIMD loop. There are no fuzz, property, empty-input or unaligned-length tests.
- Every benchmark iteration includes allocating a fresh 24 MiB output String, the reported GiB/s counts input bytes, and there is only a single noisy laptop run with no rustc version or flags.

## Known shortcomings

- Baseline is the author's own naive scalar loop (7.9x derived); NEON table lookup on M1 only, noisy benchmark; nightly Rust with no rustc version stated.
- NEON asm reads out of bounds (`ldp q0,q1,[src],#16` loads 32 bytes but advances 16, overrunning the input by 16 bytes) and writes registers declared input-only (UB per the Rust Reference). AArch64 asm has no cfg gate, and current nightly moved SimdPartialOrd, so it likely does not build unmodified. GPL-3.0, not on crates.io, uppercase only, one test vector; const-hex uses the same NEON tbl technique on stable Rust.

## Caveats and trade-offs

The author says the benchmark machine was noisy ('on battery power, so take these results with a grain of salt'). The baseline is the repo's own naive scalar loop (branchy per-nibble, uppercase output), not a named hex library such as the hex crate. It needs nightly Rust. The author calls it a coding exercise to learn cargo bench and inline assembly.

ARM64/NEON-specific hand-written assembly; a learning/hobby project rather than a hardened library, no fallback dispatch story for other ISAs shown in README.

## Maintenance

Abandoned: 26 commits between 2023-01-22 and 2023-01-25, with 0 stars, forks, issues or PRs. It is GPL-3.0, unpublished, and needs nightly Rust (probably with edits) to build today, so treat it as a reference rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table gives first-party cargo-bench results on an M1 MacBook, and the bench code is public (src/lib.rs, tests::benchmark, 12 MiB of random data). The rustc version and flags are not stated, and the author calls the machine noisy.
- **Verifier notes:** The README numbers match the record, and I marked the ratio as derived. Metadata checks out: GPL-3.0, 0 stars, not a fork, last commit 2023-01-25 (abandoned). The in-repo scalar baseline is kept, following the precedent of other own-scalar-baseline encoding entries.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/eddieantonio/binary-to-hex-simd>
  - <https://github.com/eddieantonio/binary-to-hex-simd#readme>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/lib.rs>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/implementations/byte_by_byte.rs>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/eddieantonio/binary-to-hex-simd>
  - <https://github.com/eddieantonio/binary-to-hex-simd#readme>
  - <https://github.com/eddieantonio/binary-to-hex-simd/tree/main>
  - <https://github.com/eddieantonio/binary-to-hex-simd/commits/main>
  - <https://github.com/eddieantonio/binary-to-hex-simd/issues?q=>
  - <https://github.com/eddieantonio/binary-to-hex-simd/pulls?q=>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/Cargo.toml>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/.gitignore>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/lib.rs>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/main.rs>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/implementations/mod.rs>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/implementations/byte_by_byte.rs>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/implementations/portable_simd.rs>
  - <https://github.com/eddieantonio/binary-to-hex-simd/blob/main/src/implementations/neon_tbl.rs>
  - <https://crates.io/api/v1/crates/hx>
  - <https://github.com/DaniPopes/const-hex>
  - <https://github.com/DaniPopes/const-hex/blob/master/src/arch/aarch64.rs>
  - <https://github.com/DaniPopes/const-hex/blob/master/Cargo.toml>
  - <https://doc.rust-lang.org/nightly/std/simd/index.html>
  - <https://doc.rust-lang.org/nightly/std/simd/cmp/trait.SimdPartialOrd.html>
  - <https://doc.rust-lang.org/nightly/std/simd/struct.Simd.html>
  - <https://doc.rust-lang.org/nightly/std/simd/struct.Mask.html>
  - <https://doc.rust-lang.org/reference/inline-assembly.html>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/eddieantonio/binary-to-hex-simd`) · [data/wave7/enrich/raw/github_com_eddieantonio_binary_to_hex_simd.json](../../../data/wave7/enrich/raw/github_com_eddieantonio_binary_to_hex_simd.json) (enrichment confidence 0.75)

</details>
