# hashtree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Batched SHA-256 of many fixed 64-byte inputs for Merkle trees; \~4.7x OpenSSL's per-message SHA256() on AVX2.

| | |
|---|---|
| **Beats** | OpenSSL SHA-256 |
| **Claimed result** | Unnamed x86-64 CPU without SHA extensions: OpenSSL SHA256() called one message at a time takes 30.519 ms, vs 6.519 ms for avx_x8 (AVX2, 8 blocks per call). That is about 4.7x (derived from page data); the README says '5 times faster'. Banana Pi BPI-R3, which the README describes as RISC-V: OpenSSL takes 465.372 ms vs 109.428 ms for riscv_zbb_x1, about 4.25x (derived from page data); the README says '450% improvement'. The Cascade Lake avx_x16 figure of 2.413 ms vs about 28.8 ms for a single block is about 12x, but against the library's own x1 kernel, not OpenSSL. The Go-binding benchmarks are about 6-11x faster than Prysm's earlier Go implementation (derived from page data), also not OpenSSL. |
| **Workload** | Batched SHA-256 compression of many 64-byte blocks per call (1/4/8/16 blocks at once) for Merkle-tree / beacon-chain hashing, built with HAVE_OPENSSL=1 to benchmark directly against OpenSSL's native SHA-256 |
| **Metric** | throughput |
| **Hardware** | Direct OpenSSL comparisons: an unnamed x86-64 CPU without SHA extensions (AVX2-capable), and a Banana Pi BPI-R3 that the README describes as having a RISC-V processor. Rows without OpenSSL: an unnamed Cascade Lake AVX-512 host and a Raspberry Pi 4 Model B. Go comparisons against Prysm: AMD Ryzen 5 3600, Intel Core i5-3570 and i5-7200U. |
| **Compiler and flags** | gcc/gas (Apple clang on Apple Silicon) via src/Makefile with CFLAGS -g -Wall -Werror -O3; RISC-V builds add -march=rv64gc_zbb_zk. HAVE_OPENSSL=1 links the system OpenSSL. The compiler and OpenSSL versions are not stated. |
| **Adoption** | 42 stars. The status-im/nimbus-eth2 source references hashtree through its Nim bindings. Prysm's go.mod depends on the separate Go-assembly port prysmaticlabs/gohashtree (25 stars), not on C bindings of this repo. |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/OffchainLabs/hashtree) · [benchmark](https://github.com/OffchainLabs/hashtree/blob/main/README.md) |

## Verdict

The README's bench.c hashes 75,000 random 64-byte messages (a 4.8 MB buffer). On an unnamed AVX2 x86-64 CPU without SHA-NI, the AVX2 x8 kernel in one call took 6.519 ms vs 30.519 ms for OpenSSL SHA256() called once per message (\~4.7x). On a board labelled 'Banana Pi BPI-R3 with a RISC-V processor', the single-buffer Zbb kernel took 109.4 ms vs OpenSSL's 465.4 ms (\~4.25x). Both runs were built with -O3 via src/Makefile, with no compiler or OpenSSL versions stated. The x86 gain is mostly multi-buffer vs single-buffer; the RISC-V gain is scalar (Zbb rotates plus the precomputed padding schedule). The Cascade Lake (\~12x) and Go-vs-Prysm (\~6-11x) figures are not against OpenSSL.

## Use it when

- Merkleizing large SSZ or Ethereum beacon-state trees, or any binary Merkle tree whose nodes are 32 bytes, when you can hand over a whole layer per call
- x86-64 CPUs without SHA-NI but with AVX2 or AVX-512: the README measures about 4.7x over per-message OpenSSL SHA256() with AVX2 x8, and about 12x over its own single-block kernel with AVX-512 x16 on Cascade Lake
- Throughput-bound batch hashing of thousands of 64-byte records where results must be byte-identical to standard SHA-256
- RISC-V boards with Zbb, where the README shows about 4.25x over the system OpenSSL for 64-byte messages
- Go, Rust or Nim codebases that need a vetted SHA-256 Merkle hasher; Prysm (behind its --enable-hashtree flag) and status-im/nim-ssz-serialization already consume it

## Skip it when

- Messages that are not exactly 64 bytes, or streaming or incremental hashing: there is no such API, so use OpenSSL or ISA-L
- Hashing one pair at a time (naive recursive Merkleization): the single-block kernels run at OpenSSL speed, and the author says one-at-a-time use is 'essentially the same as openssl's'
- SHA-NI CPUs where you expect a large gain over OpenSSL: the README gives no same-run OpenSSL number there, and OpenSSL also uses SHA-NI
- Raspberry Pi 4 class NEON-only ARM: the x4 NEON kernel is only 27% faster than its x1 kernel, with no OpenSSL comparison
- Settings that need audited crypto: the maintainer closed the audit request as won't-fix, and the only assurance cited is differential fuzzing (EF, Prysm, and the nim-ssz-serialization fuzz target)

## How it is fast

Multi-buffer SHA-256, taken from Intel's intel-ipsec-mb: 4, 8 or 16 independent messages are transposed into SIMD lanes (SSE/AVX x4, AVX2 x8, AVX-512 x16, NEON x4) and compressed together. On SHA-NI hardware it uses a 2-way interleaved SHA-NI kernel instead. Because every input is exactly 64 bytes, the second (padding) block is constant, so its message schedule is precomputed and stored as K+W constants (the `P`/`.LPADDING` tables), which skips that schedule on every hash. Kernels hand leftover blocks to the next narrower kernel (x16 to x8 to x4).

## Compared with alternatives

Pick it over Intel ISA-L Crypto's multi-buffer SHA when every input is a 64-byte node pair and you want one synchronous call with ARM/RISC-V kernels and Go/Rust/Nim bindings rather than a job-manager API for variable-length messages. Pick it over sha256mb or minio sha256-simd when you are outside Go or need AVX-512/SHA-NI paths, and over BLAKE3 when the protocol (e.g. Ethereum SSZ) mandates SHA-256.

## Integration

| | |
|---|---|
| **Form** | static lib (libhashtree.a plus hashtree.h, with pkg-config and `make install`); also a Go module with prebuilt .syso objects, the Rust crate hashtree-rs (builds the C library via make), and the Nim package hashtree_abi |
| **Dependencies** | none at runtime beyond stdint.h; cpuid.h on x86-64 builds; libm for benchmarks; optional OpenSSL (-lcrypto) for tests and benchmarks; the Go bindings need klauspost/cpuid/v2 |
| **Minimum toolchain** | A GCC/GNU-as compatible compiler; CI also builds with clang on Linux and with Apple clang's integrated assembler on macOS. Rust edition 2021, Nim &gt;= 1.6.0, Go 1.21/1.22 in CI (go.mod says 1.22.2). Minimum GCC or binutils versions are not documented. |
| **Platforms** | x86-64 (SSSE3/AVX/AVX2/AVX-512F+VL/SHA-NI kernels), aarch64 (NEON x1/x4 and SHA2-extension kernels, including Apple Silicon), riscv64 (base, Zbb, and Zknh+Zbkb kernels, selected via Linux riscv_hwprobe), and a scalar C fallback elsewhere; Linux, macOS and Windows (MinGW; benchmarks do not build on Windows) |
| **Thread safety** | Not documented. The kernels only touch caller-supplied buffers, but the `hashtree_hash` dispatcher lazily writes a plain global function pointer on the first call without synchronization, so call `hashtree_init(NULL)` once before hashing from several threads. |
| **Drop-in for the baseline** | partial — the digests equal OpenSSL SHA256() for exactly-64-byte inputs, but the API is a batch call over fixed-size chunks, not SHA256()/EVP; callers must restructure Merkleization to pass whole layers |

## Gotchas

- No bounds checks: `in` must hold 64\*count bytes and `out` 32\*count bytes. The Rust `hash(out, chunks, count)` is a safe fn that does not check the slice lengths, so a wrong `count` is memory-unsafe from safe Rust. Its `init()` also declares a c_int return for a void C function, so the return value is meaningless.
- Calling a named per-ISA kernel on a CPU without that ISA is undefined behavior (the header says so). Only `hashtree_hash` auto-detects, and on x86 it prefers SHA-NI x2 over AVX-512 x16 on purpose, because SHA-NI wins on small lists.
- Toolchain fragility: v0.2.4 (PR #61) fixed wrong SHA results on the AArch64 path when built with Apple clang 21 (macOS 26.4). Issue #2 reported GNU as 2.39/2.40 looping forever on the asm macros. Prebuilt Go .syso objects triggered missing .note.GNU-stack linker warnings (issue #52, still open).
- Go bindings: the assembly call cannot be preempted by the Go runtime, so before v0.2.6 (PR #71) one huge layer could stall every GC; calls are now capped at 2048 chunks. Open issue #48 reports erratic SHA-NI one-at-a-time timings on AMD.

## Known shortcomings

- First-party README numbers on an unnamed x86 CPU (retiered B to C). Specialised for 64-byte-pair Merkle hashing (Ethereum SSZ), not general SHA-256. Prysm's go.mod requires OffchainLabs/hashtree v0.2.6 behind the opt-in --enable-hashtree flag; Nimbus references the Nim bindings.
- The x86 \~4.7x is batched AVX2 against per-message OpenSSL SHA256(), with no OpenSSL run on SHA-NI CPUs; the RISC-V \~4.25x is single-buffer Zbb. No compiler or OpenSSL version. Rust hash() is a safe fn without a length check (memory-unsafe from safe Rust); the dispatcher global is set lazily without synchronization; no audit. A scalar C fallback exists since PR #43.

## Caveats and trade-offs

Both direct OpenSSL comparisons come from underspecified hardware: an x86 CPU identified only as lacking SHA extensions, and a board the README calls a 'Banana Pi BPI-R3 with a RISC-V processor'. The OpenSSL case calls the one-shot SHA256() once per 64-byte message, single-buffer, while hashtree takes many blocks per call. The gap is therefore mainly multi-buffer vs single-buffer, and on SHA-NI CPUs, where OpenSSL uses SHA-NI, no same-run OpenSSL number is given. The Cascade Lake and Raspberry Pi rows have no OpenSSL column. No compiler or OpenSSL versions are given.

Only wins when many independent 64-byte blocks (Merkle-tree leaves) can be hashed together; a single hash call is no faster than OpenSSL. Requires SIMD (AVX2/AVX-512/SHA-NI/NEON). Low-level C API (raw pointers, fixed sizes, no bounds checking); caller owns all buffers.

## Maintenance

Active: v0.2.6 was tagged 2026-09-22 with RISC-V, Apple clang and Go-GC fixes through 2026; the code is MIT-licensed and vendorable (about 16 C/asm sources with no runtime dependencies), and Prysm now depends on its Go bindings (opt-in flag) while status-im's nim-ssz-serialization uses the Nim ABI.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** These are first-party README runs of the public src/bench.c, built with HAVE_OPENSSL=1 and src/Makefile using -O3. The OpenSSL comparisons use an unnamed x86-64 CPU and an ambiguously named board, and give no compiler or OpenSSL versions. That is first-party numbers with partial methodology, so tier C. Tier B would need a peer-reviewed or independent suite.
- **Verifier notes:** The benchmark_url on the master branch redirects; the default branch is main. I added the RISC-V row, which the original record missed and which also has a same-run OpenSSL comparison. The BPI-R3 is commonly an ARM (MediaTek) board, so the README's board name may be a typo for a RISC-V Banana Pi; I did not verify this. The usage claim was wrong: Prysm uses the gohashtree Go port, not bindings of this repo.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/OffchainLabs/hashtree>
  - <https://github.com/OffchainLabs/hashtree/blob/master/README.md>
  - <https://raw.githubusercontent.com/OffchainLabs/hashtree/main/README.md>
  - <https://raw.githubusercontent.com/OffchainLabs/hashtree/main/src/Makefile>
  - <https://raw.githubusercontent.com/OffchainLabs/hashtree/main/src/bench.c>
  - <https://raw.githubusercontent.com/OffchainLabs/hashtree/main/LICENSE>
  - <https://github.com/prysmaticlabs/gohashtree>
  - <https://raw.githubusercontent.com/prysmaticlabs/gohashtree/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/OffchainLabs/hashtree>
  - <https://github.com/OffchainLabs/hashtree/blob/main/README.md>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/hashtree.h>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/hashtree.c>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/Makefile>
  - <https://github.com/OffchainLabs/hashtree/blob/main/Makefile>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/bench.c>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/sha256_generic.c>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/sha256_avx_x8.S>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/sha256_avx_x16.S>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/sha256_shani.S>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/sha256_armv8_neon_x4.S>
  - <https://github.com/OffchainLabs/hashtree/blob/main/Cargo.toml>
  - <https://github.com/OffchainLabs/hashtree/blob/main/build.rs>
  - <https://github.com/OffchainLabs/hashtree/blob/main/src/lib.rs>
  - <https://github.com/OffchainLabs/hashtree/blob/main/bindings.go>
  - <https://github.com/OffchainLabs/hashtree/blob/main/bindings_amd64.go>
  - <https://github.com/OffchainLabs/hashtree/blob/main/go.mod>
  - <https://github.com/OffchainLabs/hashtree/blob/main/hashtree_abi.nimble>
  - <https://github.com/OffchainLabs/hashtree/blob/main/.github/workflows/test.yml>
  - <https://github.com/OffchainLabs/hashtree/issues?q=is%3Aissue>
  - <https://github.com/OffchainLabs/hashtree/pulls?q=is%3Apr>
  - <https://github.com/OffchainLabs/hashtree/commits/main>
  - <https://github.com/OffchainLabs/hashtree/tags>
  - <https://github.com/OffchainLabs/hashtree/issues/2>
  - <https://github.com/OffchainLabs/hashtree/issues/3>
  - <https://github.com/OffchainLabs/hashtree/issues/4>
  - <https://github.com/OffchainLabs/hashtree/issues/7>
  - <https://github.com/OffchainLabs/hashtree/issues/39>
  - <https://github.com/OffchainLabs/hashtree/issues/48>
  - <https://github.com/OffchainLabs/hashtree/issues/52>
  - <https://github.com/OffchainLabs/hashtree/pull/61>
  - <https://github.com/OffchainLabs/hashtree/pull/71>
  - <https://crates.io/api/v1/crates/hashtree-rs>
  - <https://github.com/search?q=github.com%2FOffchainLabs%2Fhashtree+path%3Ago.mod&type=code>
  - <https://github.com/search?q=hashtree_abi+org%3Astatus-im&type=code>
  - <https://github.com/OffchainLabs/prysm/blob/develop/go.mod>
  - <https://github.com/OffchainLabs/prysm/blob/develop/crypto/hash/htr/hashtree.go>
  - <https://github.com/OffchainLabs/prysm/blob/develop/config/features/config.go>
  - <https://github.com/OffchainLabs/prysm/blob/develop/config/features/flags.go>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/offchainlabs/hashtree`) · [data/wave7/enrich/raw/github_com_offchainlabs_hashtree.json](../../../data/wave7/enrich/raw/github_com_offchainlabs_hashtree.json) (enrichment confidence 0.72)

</details>
