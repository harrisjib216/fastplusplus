# crc-fast (Rust core, C/C++ compatible) — generic SIMD CRC-16/32/64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust SIMD CRC library with a C ABI, covering every catalogued CRC-16/32/64 variant plus custom parameters; beats table-driven CRC crates.

| | |
|---|---|
| **Beats** | CRC32 |
| **Claimed result** | README asserts the `crc` crate is \~0.5 GiB/s by default, so crc-fast is 'up to &gt;220X faster'; baseline is unbenchmarked. README table: CRC-32/ISCSI \~111 GiB/s at 1 MiB (\~61 GiB/s at 1 KiB) on Sapphire Rapids EC2 c7i.metal-24xl, avx512-vpclmulqdq. 111 vs 0.5 GiB/s is \~222x (derived from page data) |
| **Workload** | CRC-32/ISCSI and CRC-32/ISO-HDLC checksum of 1KiB and 1MiB buffers on named cloud/desktop CPUs |
| **Metric** | throughput |
| **Hardware** | Intel Sapphire Rapids (EC2 c7i.metal-24xl), AMD Genoa (EC2 c7a.metal-48xl), AWS Graviton4/Graviton2, Apple M3 Ultra, Apple M4 Max |
| **Compiler and flags** | rustc version not stated (MSRV 1.89); Cargo release profile lto = true; runtime-dispatched target feature listed per row (e.g. avx512-vpclmulqdq, neon-pmull-sha3) |
| **Adoption** | 94 stars; \~56.3M crates.io downloads (\~23.4M recent) |
| **Last commit** | 2025-12-27 |
| **Links** | [repository](https://github.com/awesomized/crc-fast-rust) · [benchmark](https://github.com/awesomized/crc-fast-rust#readme) |

## Verdict

The author's own Criterion runs (random 1 KiB and 1 MiB buffers, release profile with LTO, rustc version not stated) give about 111 GiB/s CRC-32/ISCSI and about 88 GiB/s CRC-32/ISO-HDLC at 1 MiB on an EC2 c7i metal Sapphire Rapids using the AVX-512 VPCLMULQDQ path, and about 94-99 GiB/s on Apple M3 Ultra/M4 Max. The '&gt;220X' figure divides these by a one-line '\~0.5 GiB/s' claim for the `crc` crate that the repo never benchmarks, on unstated hardware. The README's link to that section points to a heading that does not exist.

## Use it when

- You need a CRC variant other than plain CRC-32 accelerated: CRC-64/NVME (the AWS S3 checksum), CRC-64/XZ or ECMA-182, CRC-32/BZIP2 or MPEG-2, CRC-16 protocols, or a custom polynomial via `CrcParams`.
- Bulk checksumming of buffers 1 KiB and up on AVX-512 + VPCLMULQDQ servers (Sapphire Rapids, Genoa) or Apple M3/M4 and Graviton4 with SHA3, where the published 1 MiB rates are about 54-111 GiB/s.
- Parallel or distributed checksumming where per-chunk CRCs are merged with `checksum_combine` (for example multipart uploads).
- C, C++ or PHP code that wants one prebuilt shared or static library covering many CRC variants instead of vendoring per-variant kernels.

## Skip it when

- x86_64 CPUs with VPCLMULQDQ but no AVX-512 (Zen 3, Alder Lake to Meteor Lake clients, Sierra Forest) fall back to the 128-bit SSE PCLMULQDQ kernel. An AVX2 tier is only an open PR (#56), so the headline numbers do not apply there.
- no_std on x86_64: 1.10.0 fails to compile because avx512.rs imports `std::arch` (issue #57; the fix, PR #42, is unmerged). no_std builds also have no runtime CPU detection and use only compile-time target features.
- Workloads that combine many checksums in a hot loop: `checksum_combine` is slow (issue #59 measured 13.6 ms for 256 CRC-64 combines; PR #60 reports about 125 us per combine at 1 MiB length on Zen 3). Precomputation fixes are open, not merged.
- Small messages (&lt;1 KiB): no published numbers below 1 KiB. On x86 the CRC-32/ISO-HDLC 1 KiB rate (\~28 GiB/s on SPR) is well under half the 1 MiB rate because there is no native instruction to fuse with.
- If you need prompt dependency and security maintenance: no commits since 2025-12-27, a yanked `spin` 0.10.0 dependency (#53) and 2026 dependency-bump PRs are unaddressed, and a contributor has started a fork, calling the author inactive.

## How it is fast

Uses PCLMULQDQ/PMULL polynomial folding from Intel's 'Fast CRC Computation for Generic Polynomials Using PCLMULQDQ' paper, folding 8 blocks at a time rather than 4, with per-algorithm fold constants. That makes one kernel work for any polynomial, including forward CRCs, which pay an extra byte-shuffle. On x86_64 it widens to 512-bit VPCLMULQDQ with AVX-512 ternary XOR, and on aarch64 it uses the SHA3 EOR3 three-way XOR. For CRC-32C (x86 and aarch64) and CRC-32/ISO-HDLC (aarch64 only), it 'fuses' SIMD CLMUL folding with the native CRC32 instructions (corsix/dougallj technique). The kernel is chosen once at runtime from CPUID/HWCAP and cached in a OnceLock.

## Compared with alternatives

Pick it over crc32fast when you need anything besides CRC-32/ISO-HDLC (CRC-32C, CRC-64/NVME, forward or custom CRCs), or a C ABI. For plain CRC-32 on AVX2-only VPCLMULQDQ x86, crc32fast 1.5.1+ has a 256-bit path that crc-fast lacks. Pick it over corsix fast-crc32 or htot crc32c when you want one runtime-dispatched package for many variants rather than C source kernels for CRC-32/CRC-32C only, which crc-fast's fusion paths borrow from.

## Integration

| | |
|---|---|
| **Form** | crate (also builds cdylib + staticlib with generated C header libcrc_fast.h) |
| **Dependencies** | spin 0.10 (on x86/x86_64/aarch64); digest 0.10 (pulled in by the default std/alloc features); hashbrown 0.16 only with the `cache` feature |
| **Minimum toolchain** | Rust 1.89 for 1.10.0 (1.9.x and earlier: Rust 1.81); stated MSRV policy is stable minus 2 |
| **Platforms** | x86_64 (SSE4.1+PCLMULQDQ baseline, AVX-512VL+VPCLMULQDQ fast path), x86 (SSE PCLMULQDQ), aarch64 (PMULL; SHA3/EOR3 preferred); table fallback elsewhere, tested on wasm32, Cortex-M and RISC-V32 |
| **Thread safety** | Not explicitly documented. The functions are pure; CPU dispatch is initialized once via std OnceLock (spin::Once in no_std); `Digest` is a plain Copy value with no shared state; the FFI error status is thread-local. |
| **Drop-in for the baseline** | partial — `crc32_iso_hdlc(&[u8]) -> u32` matches crc32fast::hash and the crc crate's CRC_32_ISO_HDLC output, but the streaming `Digest` (u64 finalize, algorithm enum) differs from both crc32fast::Hasher and crc's Crc&lt;u32&gt;/Digest API |

## Gotchas

- `checksum()` and `Digest::finalize()` return u64 for every width, so CRC-16/32 results need a cast.
- The C API returns 0 on error (null pointer, bad params, file I/O failure), and 0 is also a valid CRC, so check `crc_fast_get_last_error()`, which is thread-local. The header's error enum constants are unprefixed (`Success`, `NullPointer`, ...) and can collide in C.
- Default features include `ffi` and `panic-handler`. no_std binaries must set default-features = false, or they get the crate's `loop {}` panic handler and, with alloc, a stub global allocator that always returns null.
- Uses a lot of `unsafe` intrinsics (checked with Miri on x86_64 and libFuzzer). 1.4.0 raised SIGILL on non-AVX-512 CPUs, including via aws-sdk-s3 (issue #14, fixed in 1.4.1), so require &gt;=1.4.1.

## Known shortcomings

- Benchmark measures crc-fast only: the \~0.5 GiB/s crc-crate baseline behind the '&gt;220x' claim is an unmeasured one-liner, so the ratio is unsupported (retiered A to C).
- 111 GiB/s is the project's own number only. No AVX2+VPCLMULQDQ tier (Zen 3/Alder Lake fall back to SSE; PR #56 open); no_std on x86_64 broken in 1.10.0 (#57); slow checksum_combine (#59); FFI returns 0 on error. Idle since 2025-12-27 with its spin 0.10.0 dependency yanked (#53) and 2026 PRs unmerged. combine.rs is zlib-licensed (PR #41).

## Caveats and trade-offs

The baseline `crc` crate (\~0.5 GiB/s default) is never benchmarked side by side, with no hardware given for it. It is also a weak baseline: crc32fast, the common Rust CRC-32 incumbent, already uses PCLMULQDQ. Numbers are first-party and the rustc version is unstated. The C/C++ interface is an FFI shared/static library plus a generated header (libcrc_fast.h).

Rust core with C/C++ FFI bindings provided for non-Rust use; huge aggregate speedup spans many different cloud CPUs rather than one controlled machine

## Maintenance

Widely deployed (about 56M crates.io downloads; reverse deps include aws-smithy-checksums, object_store and uucore) and dual MIT/Apache-2.0, though src/combine.rs carries Mark Adler's zlib-licensed code (PR #41). It counts as active under the 12-month rule, but there have been no commits since the 1.10.0 release on 2025-12-27, and 2026 issues and fix PRs are unanswered.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** These are first-party numbers. The public benchmark (benches/benchmark.rs, Criterion) measures only crc-fast and never runs the `crc` crate baseline. The '\~0.5GiB/s' baseline and 'up to &gt;220X' are a one-line README assertion with no hardware stated, and the link points to an anchor that no longer exists. The rustc version is not stated either, and a &gt;50x gain with unstated flags is capped at C.
- **Verifier notes:** This is a real, widely downloaded crate, but the evidence for the &gt;220x claim is only an unmeasured baseline figure. The last commit (2025-12-27) is within 12 months, so it counts as active, not stale. GitHub detects only Apache-2.0, but Cargo.toml and the README give dual MIT OR Apache-2.0.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/awesomized/crc-fast-rust#readme>
  - <https://github.com/awesomized/crc-fast-rust>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/benches/benchmark.rs>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/benches/README.md>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/Cargo.toml>
  - <https://crates.io/api/v1/crates/crc-fast>
- **Sources the enricher read:**
  - <https://github.com/awesomized/crc-fast-rust>
  - <https://github.com/awesomized/crc-fast-rust#readme>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/Cargo.toml>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/CHANGELOG.md>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/benches/README.md>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/benches/benchmark.rs>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/libcrc_fast.h>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/src/lib.rs>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/src/feature_detection.rs>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/src/ffi.rs>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/src/combine.rs>
  - <https://github.com/awesomized/crc-fast-rust/blob/main/src/crc32/fusion/mod.rs>
  - <https://github.com/awesomized/crc-fast-rust/issues>
  - <https://github.com/awesomized/crc-fast-rust/issues/14>
  - <https://github.com/awesomized/crc-fast-rust/issues/47>
  - <https://github.com/awesomized/crc-fast-rust/issues/53>
  - <https://github.com/awesomized/crc-fast-rust/issues/54>
  - <https://github.com/awesomized/crc-fast-rust/issues/57>
  - <https://github.com/awesomized/crc-fast-rust/issues/59>
  - <https://github.com/awesomized/crc-fast-rust/pulls>
  - <https://github.com/awesomized/crc-fast-rust/pull/41>
  - <https://github.com/awesomized/crc-fast-rust/pull/56>
  - <https://github.com/awesomized/crc-fast-rust/commits/main>
  - <https://github.com/MuntasirSZN/crc-fast-rust>
  - <https://crates.io/api/v1/crates/crc-fast>
  - <https://crates.io/api/v1/crates/crc-fast/reverse_dependencies>
  - <https://hn.algolia.com/api/v1/search?query=crc-fast%20rust&tags=story>
  - <https://github.com/srijs/rust-crc32fast/pull/56>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/awesomized/crc-fast-rust`) · [data/wave7/enrich/raw/github_com_awesomized_crc_fast_rust.json](../../../data/wave7/enrich/raw/github_com_awesomized_crc_fast_rust.json) (enrichment confidence 0.8)

</details>
