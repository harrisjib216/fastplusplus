# lanehash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust SIMD non-cryptographic 64/128-bit hash with a C99 port. First-party Zen 4 numbers show 1.5-2.2x xxh3 at 1-64 KiB, but it is slower on tiny keys.

| | |
|---|---|
| **Beats** | xxHash (xxh3), rapidhash |
| **Claimed result** | Default algorithm, first-party README, Ryzen 5 7600: at 64 KiB 27.0 B/cycle vs 18.5 (xxh3 AVX-512) vs 8.8 (rapidhash v3), about 46% faster than xxh3 (derived from page data). At 4 KiB 21.8 vs 12.8 vs 8.1 B/cycle. On 4-16 B keys it is slower than xxh3 (11.4-12.0 vs 9.5-10.1 cycles/hash). Independent SMHasher numbers cover the AES variant, named lanehash64/lanehash128 there: on the EPYC 9554P table, 107601.64 MiB/s vs xxh3 45761.99 MiB/s, about 2.35x (derived from page data). The main SMHasher README row (43802.63 MiB/s) comes from a 12-thread run logged at 2712 MHz on unstated hardware, not the Ryzen 3350G used for the xxh3 row. In bytes/cycle that row is 16.936 vs 7.289. |
| **Workload** | Own benchmark harness on AMD Ryzen 5 7600 (Zen 4): 4B-64KiB inputs, cycles/hash and bytes/cycle, same binary/buffers for lanehash, xxh3 (AVX-512), and rapidhash v3; the AES variant (lanehash64/lanehash128 in SMHasher naming) is separately timed on different hardware inside rurban/smhasher. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 7600 (Zen 4) for the first-party numbers; AMD EPYC 9554P for the independent SMHasher AES-variant row |
| **Compiler and flags** | cargo build --release using the workspace profile (opt-level=3, lto="fat", codegen-units=1), with runtime dispatch selecting AVX-512. The rustc version is not stated (MSRV 1.89). The xxh3 baseline is the xxhash-rust 0.8.18 crate. SMHasher runs use CMake Release with -march=native and an unstated compiler. |
| **Adoption** | 1 star (brand-new project, created 2026-09-18) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/ccipherx/lanehash) · [benchmark](https://github.com/ccipherx/lanehash/blob/main/README.md) |

## Verdict

The first-party harness on a Ryzen 5 7600 (cargo release, fat LTO, AVX-512 dispatch, rustc unstated, xxh3 from the xxhash-rust 0.8.18 crate) measured the default algorithm at 27.0 vs 18.5 B/cycle at 64 KiB (+46%) and 21.8 vs 12.8 at 4 KiB, but slower below 32 B. The repo's separate C-reference run (gcc 13) puts upstream C xxh3 at about 13 B/cycle at 64 KiB, so the Rust-port baseline does not look weak. The only independent data is rurban SMHasher (CMake Release, -march=native, compiler unstated), and it covers only the AES variant: 107,602 vs 45,762 MiB/s for xxh3 on an EPYC 9554P (about 2.35x).

## Use it when

- Rust bulk hashing of 1 KiB-1 MiB buffers on x86-64 with AVX2/AVX-512: first-party Zen 4 numbers are 13.6 / 21.8 / 27.0 bytes/cycle at 1 / 4 / 64 KiB, against 6.3 / 12.8 / 18.5 for xxh3
- Medium keys around 256 B in throughput mode: 42-45 cycles/hash vs 101 for xxh3 and 72 for rapidhash v3 on the same Ryzen 5 7600
- Checksums or dedup keys that must be identical across x86, aarch64, wasm and C. Every backend and the C port are differentially tested against the scalar reference, and hash128 did 4 KiB page dedup in 526 cycles/page vs 588 for xxh3-128
- Maximum bulk speed on VAES CPUs (Zen 4 class) via `lanehash::aes`: rurban SMHasher EPYC 9554P shows 107,602 MiB/s vs xxh3 45,762
- A general Rust HashMap hasher: the author's map workloads show roughly half of std SipHash-1-3's cycles per op and parity with foldhash/rapidhash on string keys

## Skip it when

- Tiny keys: at 4-16 B it takes 11.4-12.0 cycles/hash vs 9.5-10.1 for xxh3 in throughput mode, and 25.4 vs 23.5 cycles for rapidhash v3 in dependent-chain latency
- Latency-bound keys of 65-128 B: they switch to the long path, and latency-final.csv shows 70.6 cycles at 128 B vs 39.7 for xxh3 and 44.1 for rapidhash v3
- DRAM-bound streaming such as big-file checksums: the README reports a 64 MiB checksum at 45.8 GB/s, below xxh3's 50.9 and gxhash's 49.9
- Production code that needs a mature, reviewed format. The repo was created 2026-09-18 and has 1 star and one author, the crate-root algorithm was swapped a week later, 0.2.0 is still 'unreleased', and quality evidence is statistical only (SMHasher, SMHasher3, Miri) with no security claims
- Scalar-only targets, or no_std builds without target-feature flags. Scalar execution is 'substantially slower', no_std x86-64 picks the backend at compile time only (SSE2 by default, about 14.5 B/cycle at 64 KiB), and the C port has no NEON backend

## How it is fast

Inputs over 64 bytes are split into 64-byte stripes dealt round-robin to 8 independent chains of 8 64-bit lanes (512-byte blocks). Each lane step is an NH-32-style `x = A ^ w; A = x + lo32(x) * hi32(x)`, a 32x32-&gt;64 multiply that maps onto vector multiply units. Sixty-four independent lanes keep AVX-512/AVX2 pipelines busy and hide multiply latency. The lanes are merged with one extra step per chain and finished with 64x64-&gt;128 multiply-folds. Inputs of 0-64 bytes use a scalar wyhash/rapidhash-style 'protected mum' multiply-fold path. The AES variant replaces the lane step with AESENC rounds (two lanes per ymm with VAES), and the backend is detected once and cached in an atomic.

## Compared with alternatives

Pick it over xxHash (xxh3) and rapidhash for 256 B-1 MiB buffers in Rust on AVX2/AVX-512 hardware, or when you need bit-identical results across x86, ARM, wasm and C. Pick it over gxhash when you cannot rely on AES, since the default algorithm needs none; with VAES, the AES variant only roughly ties gxhash (107,602 vs 103,530 MiB/s on EPYC 9554P).

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none at runtime (libc is a dev-dependency); an optional self-contained C99 source-drop lives in lanehash-c/ |
| **Minimum toolchain** | Rust 1.89 (edition 2021); the C port is C99 for GCC/clang, with unsigned __int128 optional via LANEHASH_NO_INT128 |
| **Platforms** | Any Rust target. SIMD backends: x86-64 SSE2/AVX2/AVX-512F (runtime-detected with std), aarch64 NEON, wasm32 SIMD128. The AES variant uses AES-NI/VAES/Armv8 AES, or T-table software AES elsewhere. The C port picks x86 SIMD at compile time and uses scalar code elsewhere. |
| **Thread safety** | One-shot functions are pure. The chosen backend is cached in an AtomicUsize and RandomState's per-process seed in a OnceLock. Stream and LaneHasher are ordinary owned values with no further documented guarantees. |
| **Drop-in for the baseline** | partial — the API shape matches seeded xxh3 (64/128-bit one-shot, streaming, BuildHasher), but the outputs differ, so it cannot replace stored xxh3 hashes |

## Gotchas

- Version mismatch: the README says `lanehash = "0.2"`, but crates.io only has 0.1.0 (2026-09-18, 15 downloads), whose crate root is the AES function. 0.2 changes the output of `lanehash::hash64`, so use a git dependency or pin exactly and check the verification values (0xD048C22B default, 0x9FF60BEF AES).
- Naming confusion: rurban SMHasher's `lanehash64`/`lanehash128` rows are the AES variant (verification 0x9FF60BEF, log header 'AES lanes + mum short path'). The repo now uses `lanehash64` for the new default and `lanehash_aes64` for AES, and 'lanehash' rows in docs/bench/TABLES.md also mean AES.
- HashMap output (FixedState/RandomState via LaneHasher) is a different function from hash64 and may change between minor releases. Do not persist it.
- Without hardware AES, the AES variant falls back to T-table software AES (data-indexed table lookups), which is much slower. Use the default algorithm on such targets.

## Known shortcomings

- Only the maintainer's SMHasher runs exist (EPYC 9554P: AES variant 107,602 vs xxh3 45,762 MiB/s); the README's SMHasher row is not from the Ryzen 3350G it implies. Top speed needs the AES variant (hardware AES).
- Default-algorithm numbers are first-party only (Zen 4, rustc unstated); the only independent data (rurban) is for the AES variant, whose naming differs from the repo. crates.io has only 0.1.0 (root = AES function); README describes an unreleased 0.2 with a breaking output change. 1 star, created 2026-09-18. Slow on tiny keys and 65-128 B (70.6 vs xxh3 39.7 cycles); slower than xxh3 on 64 MiB DRAM-resident input.

## Caveats and trade-offs

Brand new (created 2026-09-18, 1 star). The default-algorithm numbers are first-party only, with rustc version unstated, and the xxh3 baseline is the xxhash-rust Rust port rather than upstream C xxHash. The independent SMHasher evidence covers only the AES variant (lanehash::aes, which needs AES-NI/VAES for speed). Its README row is from unstated hardware. The i7-6820HQ table row (147839.99 MiB/s) is the author's originally submitted figure from a run that logged a timer-resolution warning, so treat it as unreliable. The lanehash README states a 64 MiB checksum is slower than xxh3 (45.8 vs 50.9 GB/s).

By the author's own admission, dependent-chain latency is worse than rapidhash for 4-16B and \~128B inputs; scalar fallback is much slower than the SIMD backends; core implementation is Rust, with a separate lanehash-c crate/build for C/C++ consumption.

## Maintenance

Brand new and in flux: created 2026-09-18, 1 star, last commit 2026-09-23, a breaking algorithm swap in its first week and 0.2.0 unpublished on crates.io. It is MIT OR Apache-2.0 with no dependencies, and the C99 port is small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B. The first-party harness (bench/src/main.rs, bench/run_tables.sh, flags in the workspace Cargo.toml, Ryzen 5 7600) does not state the rustc version, so it is not A on its own. The independent rurban/smhasher EPYC 9554P table, added by the maintainer in commit 6c5aec1c, shows the AES variant at 107601.64 MiB/s vs xxh3 at 45761.99 MiB/s on the same machine.
- **Verifier notes:** The license is confirmed as MIT OR Apache-2.0 via lanehash/Cargo.toml, LICENSE-MIT and LICENSE-APACHE; gh spdx reports only Apache-2.0. The lanehash README maps SMHasher names differently (lanehash_aes64 for AES), but the rurban lanehash64 row's verification value 0x9FF60BEF matches the AES 64-bit vector, so those rows are the AES variant. Last commit 2026-09-23 and 1 star are correct.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** Maintainer SMHasher run, EPYC 9554P: lanehash-AES 107,602 vs xxh3 45,762 MiB/s bulk.
- **Pages the verifier opened:**
  - <https://github.com/ccipherx/lanehash/blob/main/README.md>
  - <https://raw.githubusercontent.com/ccipherx/lanehash/main/README.md>
  - <https://github.com/ccipherx/lanehash>
  - <https://github.com/ccipherx/lanehash/blob/main/Cargo.toml>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/Cargo.toml>
  - <https://github.com/ccipherx/lanehash/blob/main/bench/Cargo.toml>
  - <https://github.com/ccipherx/lanehash/blob/main/bench/build.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/docs/bench/lanehash/latency-final.csv>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/lanehash64.txt>
  - <https://rurban.github.io/smhasher/doc/epyc.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/i7.html>
  - <https://github.com/rurban/smhasher/commit/6c5aec1c>
- **Sources the enricher read:**
  - <https://github.com/ccipherx/lanehash>
  - <https://raw.githubusercontent.com/ccipherx/lanehash/main/README.md>
  - <https://github.com/ccipherx/lanehash/blob/main/README.md>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/README.md>
  - <https://github.com/ccipherx/lanehash/blob/main/Cargo.toml>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/Cargo.toml>
  - <https://github.com/ccipherx/lanehash/blob/main/CHANGELOG.md>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/CHANGELOG.md>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/src/lib.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/src/spec.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/src/short.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/src/hasher.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/src/dispatch.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/src/aes/spec.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash/src/aes/lanes.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/bench/Cargo.toml>
  - <https://github.com/ccipherx/lanehash/blob/main/bench/build.rs>
  - <https://github.com/ccipherx/lanehash/blob/main/bench/run_tables.sh>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash-c/README.md>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash-c/lanehash.h>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash-c/lanehash.c>
  - <https://github.com/ccipherx/lanehash/blob/main/lanehash-c/Makefile>
  - <https://github.com/ccipherx/lanehash/blob/main/docs/bench/lanehash/refhash-c.txt>
  - <https://github.com/ccipherx/lanehash/blob/main/docs/bench/lanehash/workloads-final.txt>
  - <https://github.com/ccipherx/lanehash/blob/main/docs/bench/lanehash/throughput-L2-final.csv>
  - <https://github.com/ccipherx/lanehash/blob/main/docs/bench/lanehash/latency-final.csv>
  - <https://github.com/ccipherx/lanehash/commits/main>
  - <https://github.com/ccipherx/lanehash/issues>
  - <https://github.com/ccipherx/lanehash/pulls>
  - <https://crates.io/api/v1/crates/lanehash>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/lanehash64.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/table.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/epyc.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/i7.html>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/ccipherx/lanehash`) · [data/wave7/enrich/raw/github_com_ccipherx_lanehash.json](../../../data/wave7/enrich/raw/github_com_ccipherx_lanehash.json) (enrichment confidence 0.5)

</details>
