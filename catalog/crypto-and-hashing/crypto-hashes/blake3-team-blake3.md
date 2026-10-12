# BLAKE3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception` · 🟢 active

> Official Rust/C implementation of BLAKE3, a Merkle-tree hash/XOF/MAC about 4x faster than SHA-256 on long single-core inputs.

| | |
|---|---|
| **Beats** | SHA-256 and SHA3-256: the fastest of SUPERCOP's implementations, whose candidates include OpenSSL-backed ones. BLAKE2b is also compared. The project's own chart used OpenSSL 1.1.1d SHA-256/SHA3-256 and BLAKE2b via blake2b_simd. |
| **Claimed result** | eBASH long-message medians on 'panther' (Intel Core i7-1165G7, Tiger Lake, SUPERCOP 20260831): BLAKE3 0.51 cycles/byte vs SHA-256 2.21 (\~4.3x), SHA3-256 5.50 (\~10.8x), BLAKE2b 2.99 (\~5.9x). Ratios are derived from page data. Each figure is the fastest SUPERCOP implementation of that primitive, and the candidates include the OpenSSL-backed sha256/sha3256 implementations. At 1536-byte messages BLAKE3 (2.88 c/b) is slower than SHA-256 (2.34 c/b) on this SHA-NI CPU. |
| **Workload** | Single-core, long-message hashing throughput in cycles/byte. eBASH defines this as 1/16384 of the cycle difference between 18208-byte and 1824-byte messages, taking the median of many runs. |
| **Metric** | throughput |
| **Hardware** | eBASH 'panther': Intel Core i7-1165G7 (Tiger Lake, AVX-512 + SHA-NI, 2.8 GHz). Also eBASH 'hertz': AMD Ryzen 7 7700 (Zen 4). |
| **Compiler and flags** | SUPERCOP 20260831. The eBASH implementation page lists the best build per implementation: crypto_hash/blake3/avx512 used clang -mcpu=native -O3 -fwrapv -Qunused-arguments -fPIC -fPIE (Debian Clang 14.0.6); the sha256/openssl wrapper used gcc -march=native -mtune=native -O2 -fwrapv -fPIC -fPIE and links the system OpenSSL (version not stated). The long-message table does not say which implementation or compiler produced each best figure. |
| **Adoption** | 6.4k stars |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/BLAKE3-team/BLAKE3) · [benchmark](https://bench.cr.yp.to/results-hash/amd64-panther.html) |

## Verdict

On eBASH (SUPERCOP 20260831; single-core 'long message' = cycle difference between 18208- and 1824-byte inputs), the BLAKE3 avx512 build (Clang 14, -O3) on an Intel Core i7-1165G7 (Tiger Lake, AVX-512 + SHA-NI) takes a median 0.51 cycles/byte versus 2.21 for the fastest SHA-256 implementation, 5.50 for SHA3-256 and 2.99 for BLAKE2b (about 4.3x, 10.8x, 5.9x), and a Ryzen 7 7700 gives 0.60 vs 2.02 for SHA-256. The project's own 2020 chart (16 KiB, one thread, Xeon 8275CL without SHA-NI, OpenSSL 1.1.1d) shows about 14x over SHA-256, a gap that does not carry over to CPUs with SHA instructions.

## Use it when

- Content addressing, deduplication, build caches and file-integrity checks on inputs of several KiB or more, where you choose the hash (the README lists Cargo, ccache, Bazel, Nix, LLVM and OpenZFS as adopters).
- x86-64 hosts with AVX2 or AVX-512: on eBASH, single-thread long-message cost is 0.51-0.60 cycles/byte, against 2.02-2.21 for SHA-NI SHA-256 and 5.5-6.5 for SHA3-256.
- Hashing large in-memory buffers or files on many cores: update_rayon, update_mmap_rayon and blake3_hasher_update_tbb split the tree across threads, and the spec shows near-linear scaling up to 16 threads.
- When you need a MAC, a KDF or arbitrary-length/seekable output and would otherwise layer HMAC/HKDF/SHAKE on a plain hash.
- Verified streaming or incremental verification of large blobs through the tree structure (the Bao project).

## Skip it when

- Formats or protocols that mandate SHA-256/SHA-3 (FIPS-validated modules, TLS, X.509, existing on-disk or wire formats): the digest is not compatible.
- Short and medium messages on CPUs with SHA-256 instructions. eBASH shows SHA-256 ahead at 576 and 1536 bytes on Tiger Lake (2.34 vs 2.88 cycles/byte at 1536 B) and on Zen 4 (2.10 vs 3.76), and issue #315 reports single-thread b3sum slower than `openssl sha256` on Apple Silicon.
- Password storage or deriving keys from passwords: the README says to use Argon2 instead.
- Low-end cores without wide SIMD: here BLAKE3 performs like BLAKE2s (spec Figure 5, ARM1176), and issue #403 reports the NEON build slower than the portable one on a Cortex-A9.
- Multithreaded hashing of small inputs or of big files on spinning disks: update_rayon is slower than update below about 128 KiB on x86-64, and parallel mmap reads thrash HDDs (issue #31).

## How it is fast

The input is cut into 1 KiB chunks that form the leaves of a binary Merkle tree (derived from the Bao tree mode), so chunks are independent and the SIMD code compresses 4, 8 or 16 of them at once, one 32-bit word per vector lane (SSE4.1/AVX2/AVX-512). This 'word-based' parallelism is why throughput jumps between 2 and 16 KiB. The compression function is BLAKE2s's 32-bit ARX core, with rounds cut from 10 to 7 and a message schedule simplified to one repeated permutation. On x86-64, runtime CPU detection selects hand-written assembly, and optional Rayon (Rust) or oneTBB (C) spreads subtrees across cores.

## Compared with alternatives

Pick BLAKE3 over sha256-simd, Intel ISA-L multi-buffer SHA, j-lanes or S-HASH when you are free to change the digest: those keep SHA-256 compatibility or need many independent buffers, while BLAKE3 parallelizes a single message. Pick it over KangarooTwelve (XKCP) for peak speed at shorter lengths (1 KiB vs 8 KiB leaves), built-in multithreading and keyed/KDF modes; pick K12 when you want a Keccak/SHA-3-family primitive.

## Integration

| | |
|---|---|
| **Form** | crate (blake3, plus the b3sum CLI crate) and a C static/shared library, built with CMake or by compiling the .c/.S files directly |
| **Dependencies** | Rust: arrayvec, constant_time_eq, cfg-if, cpufeatures (x86 only). Optional: rayon-core, memmap2, digest, serde, zeroize. Build dependency: cc. C: none, with optional oneTBB for multithreading. |
| **Minimum toolchain** | Rust 1.85 (edition 2024; CI builds on 1.85.1, but there is no formal MSRV policy). C: GCC, Clang or MSVC (tested in CI), CMake 3.9+. The TBB path needs a C++20 compiler and -fno-exceptions. |
| **Platforms** | x86 and x86-64 (SSE2/SSE4.1/AVX2/AVX-512, runtime dispatch, assembly for Unix, Windows MSVC and Windows GNU). AArch64 NEON is on by default. ARMv7 NEON and WASM SIMD are compile-time opt-ins. Other targets use the portable fallback, and CI covers big-endian powerpc64 and s390x. |
| **Thread safety** | A Hasher/blake3_hasher is a plain value with no shared state, so use one per thread or clone it. Only update_rayon/update_mmap_rayon (Rust) and blake3_hasher_update_tbb (C) are multithreaded internally; all other APIs are single-threaded. The C CPU-feature cache uses atomics when stdatomic.h is available and Interlocked calls on MSVC. |
| **Drop-in for the baseline** | partial — the API shape (init/update/finalize) matches a SHA-256 streaming hasher, but the output values differ, so existing stored or exchanged digests cannot be checked. RustCrypto digest traits exist only behind the traits-preview feature, which has no SemVer guarantee. |

## Gotchas

- The widely quoted 10-20x-over-SHA-256 figures come from multithreaded mmap hashing (b3sum's default) or from a 2019 Cascade Lake CPU without SHA-NI. The single-thread lead over hardware SHA-256 is about 3.4-4.3x at long lengths and turns into a loss around 0.5-1.5 KiB.
- sizeof(blake3_hasher) is 1912 bytes on x86-64 because it holds a 55-entry chaining-value stack. That is large for per-object or on-stack state, and the C library does not implement the spec's reduced-maximum-length option.
- The Rust build compiles C/assembly through cc. If no suitable C compiler (or no AVX-512-capable one) is found, it quietly falls back to a slower pure-Rust build. NEON on non-AArch64 targets and WASM SIMD are not runtime-detected: enabling them produces binaries that assume the feature.
- Outputs shorter than 32 bytes give proportionally less security, and the XOF seek offset should not be treated as secret. Compare Hash values with the type's constant-time == rather than as byte slices.

## Known shortcomings

- Headline chart is first-party with no rustc version. Independent eBASH figure is \~4.3x over SHA-256 per core (0.51 vs 2.21 cycles/byte), not the \~14x multi-threaded chart; SHA-NI SHA-256 narrows the gap further.
- Not compatible with SHA-2/SHA-3 digests. Short and mid-size messages lose to SHA-NI SHA-256 (eBASH 1536 B: 2.88 vs 2.34 cycles/byte on Tiger Lake, 3.76 vs 2.10 on Zen 4), and Apple Silicon hardware SHA-256 is faster (#315). The 10-20x headline needs multithreading/mmap or an old non-SHA-NI Xeon; single-core lead is \~3.4-4.3x on long messages. 1,912-byte hasher state; the Rust crate silently falls back to pure Rust without a C compiler; rayon mode is slower under 128 KiB.

## Caveats and trade-offs

The project's own headline chart (BLAKE3-specs/benchmarks/bar_chart.py, 2020) shows 6866 MiB/s vs OpenSSL 1.1.1d SHA-256 at 484 MiB/s (\~14.2x) and SHA3-256 at 394 MiB/s (\~17.4x) for 16 KiB, 1-thread input on an AWS c5.metal Xeon Platinum 8275CL. That is a Cascade Lake CPU without SHA-NI, and the rustc version was not stated. The chart's RUSTFLAGS=-C target-cpu=native applied only to BLAKE2b/BLAKE2s. That helped BLAKE2, so it narrowed BLAKE3's lead over BLAKE2b rather than inflating it (the original caveat had this backwards). On CPUs with SHA-NI the lead over SHA-256 shrinks to \~3.4-4.3x at long messages: eBASH hertz (Ryzen 7 7700) gives 0.60 vs 2.02 c/b. For inputs up to \~1.5 KiB, hardware SHA-256 is faster than BLAKE3. The benchmarks Cargo.toml has since moved to blake3 1.3.1 and vendored openssl 0.10.40, so rerunning it will not reproduce the 2020 setup.

Different digest from SHA-2/SHA-3/BLAKE2 (not a bit-compatible drop-in); Merkle-tree construction parallelizes across threads and SIMD lanes; official optimized implementations in Rust and C; explicitly not recommended for password hashing.

## Maintenance

Actively maintained (v1.8.7 released 2026-08-20, commits through 2026-09-10, about 189M crates.io downloads) and licensed CC0 or Apache-2.0 (with or without the LLVM exception), so the C files can be vendored into any build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now B.
- **Tier reason:** The record's bar_chart.py is first-party. It hard-codes 2020 `cargo bench` results (6866 vs 484/394 MiB/s, which match the record exactly) with the CPU stated but no rustc version, so on its own it is C. Tier B comes from eBASH (bench.cr.yp.to), a well-known independent suite. Its long-message table for Core i7-1165G7 gives BLAKE3 0.51 c/b vs SHA-256 2.21 and SHA3-256 5.50, and the Ryzen 7 7700 gives 0.60 vs 2.02 and 6.52. It is not A: SUPERCOP code and per-implementation compilers are public, but the table only reports the fastest implementation per primitive, so the OpenSSL run is not isolated at long lengths.
- **Verifier notes:** The headline numbers in bar_chart.py are verified verbatim, and the spec PDF adds that SHA-2 came from OpenSSL 1.1.1d. I switched benchmark_url to the independent eBASH page, which gives more honest modern figures on SHA-NI CPUs, and kept the first-party chart in caveats. GitHub reports the repo language as Assembly (it is mostly Rust + C + asm); the record's 'C' is not a correctable field.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `hardware`, `compiler_and_flags`, `license`, `caveats`
- **Shortcomings recorded by:** eBASH (panther): BLAKE3 0.51 vs SHA-256 2.21 cycles/byte.; eBASH 1536-byte messages: BLAKE3 2.88 vs SHA-256 (SHA-NI) 2.34 cycles/byte (Tiger Lake); 3.76 vs 2.10 (Zen 4).
- **Pages the verifier opened:**
  - <https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/benchmarks/bar_chart.py>
  - <https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/benchmarks/Cargo.toml>
  - <https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/benchmarks/README.md>
  - <https://raw.githubusercontent.com/BLAKE3-team/BLAKE3-specs/master/blake3.pdf>
  - <https://github.com/BLAKE3-team/BLAKE3>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/README.md>
  - <https://bench.cr.yp.to/primitives-hash.html>
  - <https://bench.cr.yp.to/results-hash.html>
  - <https://bench.cr.yp.to/results-hash/amd64-panther.html>
  - <https://bench.cr.yp.to/results-hash/amd64-hertz.html>
  - <https://bench.cr.yp.to/web-impl/amd64-panther-crypto_hash.html>
- **Sources the enricher read:**
  - <https://github.com/BLAKE3-team/BLAKE3>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/README.md>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/c/README.md>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/Cargo.toml>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/src/lib.rs>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/.github/workflows/ci.yml>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/c/blake3_dispatch.c>
  - <https://github.com/BLAKE3-team/BLAKE3/blob/master/c/blake3.h>
  - <https://github.com/BLAKE3-team/BLAKE3/issues?q=slow>
  - <https://github.com/BLAKE3-team/BLAKE3/issues?q=bug>
  - <https://github.com/BLAKE3-team/BLAKE3/issues/315>
  - <https://github.com/BLAKE3-team/BLAKE3/issues/220>
  - <https://github.com/BLAKE3-team/BLAKE3/issues/403>
  - <https://github.com/BLAKE3-team/BLAKE3/issues/565>
  - <https://crates.io/api/v1/crates/blake3>
  - <https://raw.githubusercontent.com/BLAKE3-team/BLAKE3-specs/master/blake3.pdf>
  - <https://bench.cr.yp.to/results-hash/amd64-panther.html>
  - <https://bench.cr.yp.to/results-hash/amd64-hertz.html>
  - <https://bench.cr.yp.to/web-impl/amd64-panther-crypto_hash.html>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/blake3-team/blake3`) · [data/wave7/enrich/raw/github_com_blake3_team_blake3.json](../../../data/wave7/enrich/raw/github_com_blake3_team_blake3.json) (enrichment confidence 0.88)

</details>
