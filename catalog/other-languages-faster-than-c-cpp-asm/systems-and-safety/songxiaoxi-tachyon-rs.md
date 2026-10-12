# tachyon-rs (Rust SIMD AES-GCM, ChaCha20-Poly1305, MD5, SHA, BLAKE3, Base64)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Pure-Rust SIMD crypto, hash and Base64 crate that edges OpenSSL AES-128-GCM on ARM but ties it on x86; unaudited.

| | |
|---|---|
| **Beats** | OpenSSL libcrypto (C and assembly; versions 3.2.1 to 3.6.1 depending on platform) for AES-128-GCM, ChaCha20-Poly1305 and MD5; ring 0.17.14 and the blake3 1.8.2 crate are also compared |
| **Claimed result** | AES-128-GCM 64 KiB, tachyon vs OpenSSL (MiB/s): Apple M4 12212 vs 11043; M1 8411 vs 8143; A16 9225 vs 7330; Snapdragon 888 4759 vs 3972; RPi4 BCM2711 56.4 vs 23.4; Ryzen Z1 Extreme 18458 vs 16407; Ryzen 9 9950X 33179 vs 33121 (tie); ring 0.17.14 is behind everywhere (9950X 15613). ChaCha20-Poly1305 64 KiB: Ryzen 9 9950X 7576 vs OpenSSL 6900 vs ring 3714; Apple M4 2855 only with the nightly tune-cpu=generic build, default build 1730 vs OpenSSL 2356 and ring 2350 (M1 default 1148 vs OpenSSL 1816, A16 default 1241 vs 1933); i7-3770 1122 vs OpenSSL 1106 while ring is 1151. MD5 beats OpenSSL on 9 of 10 platforms (e.g. Ryzen 9 9950X 1289 vs 1187), loses on Apple M4 (966 vs 982). BLAKE3 beats the blake3 1.8.2 crate on Apple and Snapdragon 888 (M4 3459 vs 2572) and loses on x86 and RPi4 (Ryzen 9 9950X 13348 vs 13441; BCM2711 347 vs 358). SHA-1 and Base64 are compared only with Rust crates (ring, data-encoding, base64). |
| **Workload** | Single-call throughput on 64 KiB buffers (AES-128-GCM and ChaCha20-Poly1305 encryption, MD5, SHA-1, BLAKE3) and 192 KiB Base64 encoding, MiB/s, on up to eleven x86-64 and ARM platforms. |
| **Metric** | throughput |
| **Hardware** | Apple M4, M1, A16, A12z; Snapdragon 888 and 6 Gen 1; BCM2711 (RPi4); Intel i7-10700K and i7-3770; AMD Ryzen 9 9950X and Ryzen Z1 Extreme |
| **Compiler and flags** | Cargo [profile.bench] opt-level 3, lto = "fat", codegen-units 1; rustc version and target-cpu not stated (build.rs enables AVX-512 paths on Rust 1.89+ or nightly); nightly -Ztune-cpu=generic for the 'tune-cpu=generic' ChaCha20 column; OpenSSL builds (3.2.1 to 3.6.1) and how they were timed not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README claims hand-tuned SIMD intrinsics (AVX/SSE, NEON) 'outperform even hand-tuned assembly in many cases'; no per-primitive mechanism is given. |
| **Adoption** | 4 stars; 205 commits |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/SongXiaoXi/tachyon-rs) · [benchmark](https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/README.md) |

## Verdict

First-party README tables give single-call 64 KiB throughput in MiB/s on 11 CPUs. AES-128-GCM beats OpenSSL 3.2.1 to 3.5.0 by 3-26% on Apple and Snapdragon (M4 12212 vs 11043), by 12% on the Ryzen Z1 Extreme and by 2.4x on an RPi4 software path, and ties on the Ryzen 9 9950X (33179 vs 33121). ChaCha20-Poly1305 beats OpenSSL 3.4.1 on the 9950X (7576 vs 6900) but trails it on Apple chips in the default build. Only the ring and md5-crate columns come from the repo's Criterion benches (opt-level 3, fat LTO, codegen-units 1); the rustc version and target-cpu are not stated.

## Use it when

- Bulk AES-128-GCM on Apple or Snapdragon CPUs, in experiments or code you will audit yourself. README: A16 9225 vs OpenSSL 7330 MiB/s (1.26x), Snapdragon 888 1.20x, M4 1.11x at 64 KiB.
- Non-cryptographic MD5 checksums: 1-17% above OpenSSL on 9 of 10 platforms (Ryzen 9 9950X 1289 vs 1187 MiB/s, RPi4 326 vs 279) and up to 1.8x the md5 crate.
- Legacy SHA-1 in Rust: 1.7x to 6.7x ring's SHA-1 (M1 2301 vs 343 MiB/s).
- Base64 encoding of large buffers: README shows 2.3x to 4.6x the base64 and data-encoding crates (M4 26433 vs 5805 MiB/s), but the repo has no bench target for this table.
- As readable, MIT OR Apache-2.0 reference code for intrinsics-based AES-GCM, ChaCha20-Poly1305 and BLAKE3 kernels in Rust.

## Skip it when

- Production TLS, storage or messaging encryption: the README says the library is not formally audited, is meant for benchmarking and experimentation, and should not be used in production.
- AES-GCM on modern x86: it ties OpenSSL on the Ryzen 9 9950X (33179 vs 33121 MiB/s), so it offers nothing over OpenSSL or an OpenSSL-backed crate there.
- ChaCha20-Poly1305 on Apple silicon with a stable default build: 27-37% slower than OpenSSL and ring (M1 1148 vs 1816 MiB/s); only a nightly -Ztune-cpu=generic build wins. On the i7-3770 it is also behind ring.
- BLAKE3 on x86 or RPi4: the official blake3 1.8.2 crate is faster (Ryzen Z1 Extreme 8364 vs 8096 MiB/s, Ryzen 9 9950X 13441 vs 13348).
- When you need a crates.io release, semver, a documented MSRV or documented constant-time guarantees: none exist, and Cargo.toml pins most dependencies as '\*'.

## How it is fast

Each primitive has hand-written intrinsics per instruction set. On x86 that covers SSE2, AVX, AVX2 and AVX-512: GCM uses VAES and VPCLMULQDQ, Poly1305 uses AVX-512 IFMA with 44-bit limbs, and ChaCha20 has an AVX-512 path. On ARM it uses NEON with the ARMv8 AES and PMULL instructions. A 6-block GHASH path (build.rs cfg ghash_block_x6) is enabled on x86 and Apple aarch64. ChaCha20-Poly1305 interleaves the stream cipher with Poly1305 over 16 or 64 blocks at a time. Without target-feature flags, union-based Dynamic types dispatch at runtime. Chips without AES instructions fall back to RustCrypto's fixsliced software AES.

## Compared with alternatives

Only two catalogued siblings overlap: Usuba (a compiler emitting bitsliced C for AES-CTR and similar primitives) and the Zig base64 entry. Pick tachyon for AES-GCM, ChaCha20-Poly1305 or Base64 inside a Rust program on ARM, and only after your own audit. Pick Usuba for constant-time bitsliced kernels in C. For production Rust crypto, ring or OpenSSL remain the safer choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, unsafe_target_feature ('\*'), libc ('\*'), the in-repo path crates tachyon-macros and optional instr_hex; build dependencies rustc_version ('\*') and cfg_aliases. Git dependency only. |
| **Minimum toolchain** | Rust 2021 edition on stable; AVX-512 paths need Rust 1.89+ or nightly (build.rs); the Apple ChaCha20 win needs nightly -Ztune-cpu=generic; MSRV not documented |
| **Platforms** | x86-64 (SSE2 to AVX-512 with runtime dispatch) and aarch64 (NEON plus AES/PMULL) per the README; the code also has 32-bit x86 and arm cfgs and portable software fallbacks |
| **Thread safety** | Not documented. Cipher and hash objects are plain owned values. The Dynamic dispatch types lazily initialise unsynchronised `static mut` index globals (for example IDX in aes/dynamic.rs) on first new(). Commit 992ce47 (2026-07-26) narrowed a race there by storing the index once, but the accesses are still not atomic. |
| **Drop-in for the baseline** | no |

## Gotchas

- Poly1305 is not RFC 8439 Poly1305 when used on its own: update() (scalar mod.rs and x86_avx512.rs) zero-pads a partial final block and sets the 2^128 bit, which is the AEAD pad16 rule. As a standalone MAC it therefore gives different tags for messages that are not a multiple of 16 bytes, and since there is no internal buffer, each update() call pads independently. It is only correct inside the bundled ChaCha20-Poly1305.
- Harness flaw (correctness): the Ryzen 9 9950X and Z1 Extreme ChaCha20-Poly1305 rows (README commit e171231, 2026-03-23; 9950X rose from 4121 to 7576 MiB/s) were measured on an AVX-512 IFMA Poly1305 added 2026-03-21/22. Until commit 09c2cb6 (2026-03-31), that code applied raw-Poly1305 0x01 padding instead of pad16, so tags were wrong whenever AAD or message length was not a multiple of 16 bytes. The 64 KiB, empty-AAD benchmark never reaches that branch, and the benches never check their output.
- The OpenSSL column is cross-run and stale. Commit e171231 changed only tachyon cells and ea37614 (2026-03-31) changed only tachyon and ring cells. The OpenSSL cells (mixed versions 3.2.1 to 3.6.1) were not re-measured alongside, and no repo code produces them. Only the ring and md5-crate comparisons are same-run Criterion measurements, and even those run against unpinned '\*' versions with no Cargo.lock.
- Fixed correctness bugs in less-tested paths: the 32-bit software AES (fixslicing32.rs, used only when target_pointer_width is 32) emitted its output words in the wrong order until commit 5e51145 (2026-06-01). CI runs `cargo test` only on 64-bit ubuntu-latest and ubuntu-24.04-arm runners. AVX-512 paths are tested only where the runner's CPU has them. The crates.io name `tachyon` belongs to an unrelated crate (nh13/tachyon), so `cargo add tachyon` without --git installs the wrong package.

## Known shortcomings

- The public benches time only the ring and md5 crates while the OpenSSL column comes from a separate unstated tool (cross-harness); BLAKE3 and Base64 have no bench target; ties or losses on x86; on Apple the default ChaCha20 build loses and wins only with nightly tune-cpu=generic; README says unaudited, not for production.
- Harness and correctness flaw: the 9950X and Z1 ChaCha20 rows (e171231, 2026-03-23) were measured on an AVX-512 IFMA Poly1305 that gave wrong tags for AAD or tails that are not multiples of 16 until 09c2cb6 (2026-03-31); the 64 KiB empty-AAD bench never hits that branch and the benches never check output. The OpenSSL column was never re-measured when the tachyon and ring cells changed (e171231, ea37614), so the OpenSSL comparison is cross-run and stale; only the ring and md5 columns are same-run. The public Poly1305 uses the AEAD pad16 rule in update() rather than RFC 8439 for non-16-multiple messages with no internal buffer; fixslicing32 (32-bit software AES) had wrong output order until 5e51145 (2026-06-01) and CI runs only 64-bit; dispatch globals are still non-atomic static mut; the crates.io tachyon is an unrelated crate.

## Caveats and trade-offs

Wins are mostly on ARM and Apple chips; on x86 it ties or loses (AES-GCM Ryzen 9 9950X tie, BLAKE3 slower on all x86 and RPi4, ChaCha20 on i7-3770 behind ring), and on Apple chips the default ChaCha20 build is 25-40 percent slower than OpenSSL and ring, winning only with nightly -Ztune-cpu=generic. The OpenSSL column is not produced by the repo's bench code (bench/\*.rs compare tachyon only with ring and the md5 crate; Cargo.toml has no openssl dependency), so tachyon-vs-OpenSSL rows are cross-harness comparisons with different OpenSSL versions per platform. BLAKE3 and Base64 tables have no bench target in Cargo.toml (only aes_gcm, chacha20_poly1305, md5, sha1, sha512). README security notice: not formally audited, intended for benchmarking and experimentation, do not use in production. Recent correctness fixes (inv_bitslice byte transmutation 2026-06-01, index-initialisation race 2026-07-26) postdate an unknown measurement date. Not on crates.io (git dependency only). First-party tables only. [retier] The 9950X and Z1 ChaCha20 rows (e171231, 2026-03-23) were measured on an AVX-512 IFMA Poly1305 that gave wrong tags for AAD or tails that are not multiples of 16 until 09c2cb6 (2026-03-31); the 64 KiB empty-AAD bench never hits that branch and the benches never check output. The OpenSSL column was never re-measured when the tachyon and ring cells changed, so the OpenSSL comparison is cross-run and stale; only the ring and md5 columns are same-run. fixslicing32 had wrong output order until 5e51145 (2026-06-01) and CI runs only 64-bit; dispatch globals are non-atomic static mut.

README security notice: not formally audited, for benchmarking and experimentation, do not use in production. Pure Rust (no C), x86-64 and aarch64 only.

## Maintenance

Active single-author project (205 commits, last 2026-09-18, 4 stars, no issues or releases), dual MIT/Apache-2.0 and so copyable, but git-only and self-declared unaudited; its OpenSSL comparisons are cross-run, and its x86 ChaCha20 numbers predate an AVX-512 Poly1305 tag fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables with CPU models; the public criterion benches (bench/aes_gcm.rs, chacha20_poly1305.rs, md5.rs) time only tachyon against ring and the md5 crate, while the OpenSSL column comes from an unstated separate tool with per-platform OpenSSL builds, and rustc version and target flags are not stated, so not A.
- **Verifier notes:** Every number in the record matches the README; added the BLAKE3 RPi4 loss, the Apple default-build ChaCha20 losses and the missing-harness detail. Same-harness evidence exists only against ring 0.17.14, whose AES-GCM and ChaCha20 cores are BoringSSL-derived assembly (general knowledge, not re-checked here); the OpenSSL comparison is cross-tool. Shortcomings to record: x86 ties or losses, Apple ChaCha20 needs nightly tune flag, OpenSSL column outside public bench code, BLAKE3/Base64 bench code absent, unaudited crypto with a do-not-use-in-production notice.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-109 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/README.md>
  - <https://github.com/SongXiaoXi/tachyon-rs>
  - <https://github.com/SongXiaoXi/tachyon-rs/tree/main/bench>
  - <https://github.com/SongXiaoXi/tachyon-rs/commits/main>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/aes_gcm.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/chacha20_poly1305.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/md5.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/build.rs>
- **Sources the enricher read:**
  - <https://github.com/SongXiaoXi/tachyon-rs>
  - <https://github.com/SongXiaoXi/tachyon-rs/commits/main>
  - <https://github.com/SongXiaoXi/tachyon-rs/commits/main/README.md>
  - <https://github.com/SongXiaoXi/tachyon-rs/commit/ea37614>
  - <https://github.com/SongXiaoXi/tachyon-rs/commit/e171231>
  - <https://github.com/SongXiaoXi/tachyon-rs/commit/09c2cb6>
  - <https://github.com/SongXiaoXi/tachyon-rs/commit/5e51145>
  - <https://github.com/SongXiaoXi/tachyon-rs/commit/992ce47>
  - <https://github.com/SongXiaoXi/tachyon-rs/issues?q=is%3Aissue>
  - <https://github.com/SongXiaoXi/tachyon-rs/tree/main/src/utils>
  - <https://github.com/SongXiaoXi/tachyon-rs/tree/main/src/crypto/poly1305>
  - <https://github.com/SongXiaoXi/tachyon-rs/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/build.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/LICENSE-APACHE>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/crypto/mod.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/crypto/poly1305/mod.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/crypto/poly1305/x86_avx512.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/crypto/chacha20_poly1305.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/crypto/gcm/mod.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/crypto/aes/dynamic.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/crypto/aes/soft/mod.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/src/utils/bench.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/aes_gcm.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/chacha20_poly1305.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/md5.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/sha1.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/bench/sha512.rs>
  - <https://raw.githubusercontent.com/SongXiaoXi/tachyon-rs/HEAD/.github/workflows/rust.yml>
  - <https://crates.io/api/v1/crates/tachyon>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/songxiaoxi/tachyon-rs`) · [data/wave14/enrich/raw/github_com_songxiaoxi_tachyon_rs.json](../../../data/wave14/enrich/raw/github_com_songxiaoxi_tachyon_rs.json) (enrichment confidence 0.72)

</details>
