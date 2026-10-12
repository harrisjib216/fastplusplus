# crc32fast (Rust CRC32 SIMD)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust CRC-32 (IEEE) crate that picks PCLMULQDQ, VPCLMULQDQ or ARMv8 CRC32 kernels at runtime; beats the table-driven `crc` crate.

| | |
|---|---|
| **Beats** | CRC32 |
| **Claimed result** | README table: `crc` crate 1.8.1 at 4,926 ns/iter (207 MB/s); crc32fast 1.0.0 baseline at 683 ns/iter (1,499 MB/s); crc32fast pclmulqdq at 140 ns/iter (7,314 MB/s). That is about 7.2x and 35x over `crc` (derived from page data). |
| **Workload** | CRC32 (IEEE) checksum throughput, comparing this crate's baseline/pclmulqdq implementations to the `crc` crate |
| **Metric** | throughput |
| **Adoption** | 338 stars; about 712M all-time crates.io downloads and 1,296 reverse dependencies; flate2 1.1.10 and png 0.18.1 both depend on crc32fast ^1.2.0 (crates.io) |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/srijs/rust-crc32fast) · [benchmark](https://github.com/srijs/rust-crc32fast#readme) |

## Verdict

The only comparison against `crc` is a 1.0.0-era README table: crc 1.8.1 at 207 MB/s, the crc32fast table baseline at 1,499 MB/s and PCLMULQDQ at 7,314 MB/s. It states no CPU, compiler or input size, and the current Criterion bench does not include `crc`. Newer maintainer-run self-comparisons in PR #56 (EC2 Sapphire Rapids, before the final tuning) give 1 MiB at 25.0 GB/s (SSE), 51.0 (AVX2) and 68.6 (AVX-512), and an AMD EPYC 7763 went from 11.0 to 24.2 GB/s with the AVX2 path.

## Use it when

- Any Rust code computing zlib/gzip/PNG/zip CRC-32. It is already a transitive dependency of flate2, png, zip, image and zlib-rs, so using it directly adds nothing.
- Streaming or chunk-parallel checksums: `Hasher::update` over pieces, then merge per-chunk results with `Hasher::combine` (table-driven x^2^n combine).
- Mixed x86 fleets. The same binary uses SSE PCLMULQDQ on older CPUs, 256-bit VPCLMULQDQ on AVX2-only parts (Zen 3, Alder Lake) and 512-bit on AVX-512 parts; the maintainer measured 25.0 / 51.0 / 68.6 GB/s at 1 MiB on Sapphire Rapids.
- Short or odd-length buffers of 16 B or more: since 1.5.1 the clmul path goes down to 16 bytes, which PR #56 reports as 3.3-7.2x faster than before for 16-127 B inputs.
- Projects that need a low MSRV (1.63) or embedded/wasm builds, where the portable slicing-by-16 fallback is enough.

## Skip it when

- You need CRC-32C (iSCSI/ext4), CRC-64, CRC-16 or a custom polynomial. It is IEEE-only, and the request for other polynomials has been open since 2019 (#9); use crc-fast or a crc32c crate.
- no_std builds lose runtime detection, so SIMD is used only if the matching target features are enabled at compile time; otherwise you get the table baseline.
- Old or specific toolchains: before rustc 1.89 the VPCLMULQDQ paths are silently compiled out, before 1.80 aarch64 has no hardware path, and on rustc 1.87 a compiler regression made the specialized path slower than baseline (#48).
- Unoptimized debug builds are very slow (a user saw about 2 MB/s on M1 before 1.3.1, and wasm debug builds slowed zip decompression 150x), so give this dependency an opt-level in the dev profile.
- Peak aarch64 throughput: the ARM path uses only the scalar CRC32 instruction, with no PMULL folding or CRC+CLMUL fusion (the corsix/crc-fast technique), and the repo publishes no aarch64 numbers.

## How it is fast

On x86 it uses carry-less-multiply folding from Intel's Gopal et al. 2009 paper 'Fast CRC Computation for Generic Polynomials Using PCLMULQDQ': 4 streams with SSE, 8 streams with AVX2+VPCLMULQDQ from 256 B, and 16 streams with AVX-512 from 2 KiB, plus a clmul fold for the final partial block. On aarch64 it uses the hardware `crc32d` instruction with three interleaved accumulators, rejoined by GF(2) CRC combination, to hide instruction latency on inputs of 1.5 KiB and up. Everything else uses a slicing-by-16 table ('baseline'). The kernel is chosen by runtime CPU detection when a `Hasher` is constructed.

## Compared with alternatives

Pick it over crc-fast when you only need IEEE CRC-32 in Rust and want one tiny dependency, MSRV 1.63 and the crate the ecosystem already uses, or when you run on AVX2-only VPCLMULQDQ x86 (Zen 3, Alder Lake), where crc-fast has no 256-bit tier. Choose crc-fast, corsix fast-crc32 or htot crc32c for CRC-32C, other widths, or a C/C++ interface.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if 1.0 |
| **Minimum toolchain** | Rust 1.63 (MSRV); rustc 1.80+ for the aarch64 CRC path and 1.89+ for the AVX2/AVX-512 VPCLMULQDQ paths, detected by build.rs |
| **Platforms** | any; accelerated on x86/x86_64 (SSE2+SSSE3+SSE4.1+PCLMULQDQ base; AVX2 or AVX-512F with VPCLMULQDQ for the wide paths) and aarch64 (CRC extension); CI cross-tests i686, aarch64, riscv64gc and s390x, and checks wasm32 |
| **Thread safety** | Not documented explicitly. `Hasher` is a plain Clone value with no global mutable state (CPU detection uses std's cached feature macros), so one hasher per thread is safe. |
| **Drop-in for the baseline** | partial — same CRC-32/ISO-HDLC value as the `crc` crate's CRC_32_ISO_HDLC and zlib crc32(), but the API differs (`hash()`/`Hasher` instead of `Crc::<u32>::new(&CRC_32_ISO_HDLC)`) |

## Gotchas

- `Hasher::reset()` sets the state to 0 and discards any initial value passed to `new_with_initial`.
- It implements `core::hash::Hasher` (`finish` returns the CRC as u64). Do not use it as a HashMap hasher: the output is 32 bits and it is not DoS-resistant.
- `hash()` builds a new `Hasher` per call, which runs CPU feature detection (about 14 ns on an EPYC 7763 per PR #56). For many tiny buffers, build one `Hasher` and clone it.
- Throughput is not monotonic in size. Around the stride edges the maintainer still measured AVX-512 at 31.1 GB/s against AVX2 at 47.0 GB/s for 2303 B inputs on Sapphire Rapids, and there is no `std::io::Write` impl (#30 open).

## Known shortcomings

- README comparison table is 2018-era (crc 1.8.1 at 207 MB/s vs 1,499 / 7,314 MB/s); the current benchmark no longer includes the crc crate. Rust-only.
- CRC-32 IEEE only. SIMD paths need rustc &gt;= 1.89 (wide x86) / &gt;= 1.80 (aarch64); 1.87 regression (#48); no_std detection is compile-time only; debug builds are slow. aarch64 uses the scalar crc32 instructions only (no PMULL). reset() drops the initial value.

## Caveats and trade-offs

The README benchmark table gives no CPU model or compiler flags. It is historical: it compares crc32fast 1.0.0 against `crc` 1.8.1, both 2018-era versions, and does not cover the newer vpclmulqdq AVX2/AVX-512 and aarch64 3-way paths. The current criterion benchmark (benches/bench.rs) measures only crc32fast itself, so nothing in the repo can reproduce the comparison. The GitHub license API reports only Apache-2.0, but Cargo.toml and the README declare MIT OR Apache-2.0, and both LICENSE files are present.

Rust-only crate, no C API; runtime CPU feature detection requires std (no_std loses SIMD paths)

## Maintenance

Actively maintained: 1.5.1 (2026-08-22) added the VPCLMULQDQ and ARM 3-way paths, 1.5.2 shipped 2026-09-12 and the last commit is 2026-09-21. It is dual MIT/Apache-2.0 with about 712M downloads and 1,296 reverse dependencies (flate2, png, zip, image, parquet, zlib-rs), so it is the de facto Rust CRC-32.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance table compares crc32fast 1.0.0 (baseline and pclmulqdq variants) with the `crc` crate 1.8.1 in ns/iter and MB/s. It gives no CPU model, compiler or flags, and the current criterion harness (benches/bench.rs) no longer benchmarks the `crc` crate, so these are first-party numbers without methodology: tier C.
- **Verifier notes:** The numbers, license, stars and last commit (2026-09-21, 'Centralize state handling') all match. The baseline here is the Rust `crc` crate, not zlib. Adoption is very high (flate2 and png depend on it).
- **Fields the verifier corrected:** `claimed_speedup`, `compared_against_cpp_std_directly`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** PR #56 self-run (Sapphire Rapids, 1 MiB): SSE 25.0, AVX2 51.0, AVX-512 68.6 GB/s.
- **Pages the verifier opened:**
  - <https://github.com/srijs/rust-crc32fast>
  - <https://github.com/srijs/rust-crc32fast#readme>
  - <https://github.com/srijs/rust-crc32fast/blob/master/Cargo.toml>
  - <https://github.com/srijs/rust-crc32fast/blob/master/benches/bench.rs>
  - <https://crates.io/api/v1/crates/crc32fast>
  - <https://crates.io/api/v1/crates/crc32fast/reverse_dependencies>
  - <https://crates.io/api/v1/crates/flate2/1.1.10/dependencies>
  - <https://crates.io/api/v1/crates/png/0.18.1/dependencies>
- **Sources the enricher read:**
  - <https://github.com/srijs/rust-crc32fast>
  - <https://github.com/srijs/rust-crc32fast#readme>
  - <https://github.com/srijs/rust-crc32fast/blob/master/Cargo.toml>
  - <https://github.com/srijs/rust-crc32fast/blob/master/build.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/src/lib.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/src/specialized/mod.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/src/specialized/pclmulqdq.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/src/specialized/aarch64.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/src/baseline.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/src/combine.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/benches/bench.rs>
  - <https://github.com/srijs/rust-crc32fast/blob/master/.github/workflows/ci.yml>
  - <https://github.com/srijs/rust-crc32fast/commits/master>
  - <https://github.com/srijs/rust-crc32fast/issues>
  - <https://github.com/srijs/rust-crc32fast/issues/13>
  - <https://github.com/srijs/rust-crc32fast/issues/24>
  - <https://github.com/srijs/rust-crc32fast/issues/30>
  - <https://github.com/srijs/rust-crc32fast/issues/41>
  - <https://github.com/srijs/rust-crc32fast/issues/48>
  - <https://github.com/srijs/rust-crc32fast/issues/51>
  - <https://github.com/srijs/rust-crc32fast/pull/56>
  - <https://crates.io/api/v1/crates/crc32fast>
  - <https://crates.io/api/v1/crates/crc32fast/reverse_dependencies>
  - https://hn.algolia.com/api/v1/search?query=crc32fast&tags=(story,comment)
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/srijs/rust-crc32fast`) · [data/wave7/enrich/raw/github_com_srijs_rust_crc32fast.json](../../../data/wave7/enrich/raw/github_com_srijs_rust_crc32fast.json) (enrichment confidence 0.85)

</details>
