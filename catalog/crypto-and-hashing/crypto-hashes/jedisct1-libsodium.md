# libsodium (BLAKE2b)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `ISC` · 🟢 active

> libsodium's crypto_generichash BLAKE2b: \~1.2-2.7x OpenSSL EVP BLAKE2b-512 on 64 B-1 KB inputs, roughly even from 4 KB.

| | |
|---|---|
| **Beats** | OpenSSL BLAKE2b (EVP_blake2b512) |
| **Claimed result** | libsodium's BLAKE2b beats OpenSSL's BLAKE2b at small-to-medium sizes (means of 5 repetitions): \~2.70x at 64B (577.8 vs 213.7 MB/s), \~1.91x at 256B (1243.6 vs 650.3 MB/s), \~1.18x at 1024B (1307.0 vs 1107.2 MB/s), about tied at 4096B (1338.4 vs 1333.9 MB/s); OpenSSL retakes the lead by \~4% at 16384B (1402.7 vs 1349.3 MB/s) (all derived from page data) |
| **Workload** | BLAKE2b one-shot hashing of 64/256/1024/4096/16384-byte buffers using Google Benchmark, with Crypto++ 8.9.0, OpenSSL 3.6.0, Botan 3.9.0, libsodium 1.0.20 and mbedTLS 4.0.0 all statically linked and built with identical compiler flags |
| **Metric** | throughput |
| **Hardware** | Host 'sccdeMacBook-Air.local' (Apple Silicon MacBook Air; the chip model is not named), 8 logical CPUs. The result.json context block reports 64KB L1D / 128KB L1I / 4MB L2, a release build, and a run dated 2025-11-05. |
| **Compiler and flags** | The README says -O3 -march=native -mtune=native -flto -funroll-loops -fomit-frame-pointer (PGO optional) is applied to all libraries. However, cmake/FetchLibsodium.cmake configures libsodium with CFLAGS=\${CMAKE_C_FLAGS_RELEASE}, not the shared CRYPTO_BENCH_C_FLAGS that OpenSSL gets, so libsodium's flags probably differ. result.json does not record the compiler, its version, or whether PGO was used. |
| **Adoption** | 13,965 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/jedisct1/libsodium) · [benchmark](https://github.com/scc-tw/cryptobench-cpp/blob/main/result.json) |

## Verdict

scc-tw/cryptobench-cpp (Google Benchmark, means of 5 repetitions) ran once on 2025-11-05 on an unnamed Apple Silicon MacBook Air, with no compiler recorded. It compared libsodium 1.0.20's one-shot crypto_generichash_blake2b (64-byte output) against OpenSSL 3.6.0's EVP_blake2b512 with a new EVP_MD_CTX per call: 577.8 vs 213.7 MB/s at 64 B (\~2.7x), 1243.6 vs 650.3 at 256 B (\~1.9x), 1307.0 vs 1107.2 at 1 KB (\~1.18x), a tie at 4 KB, and 1349.3 vs 1402.7 at 16 KB, where OpenSSL is \~4% ahead. Both sides ran portable C compression on this ARM machine. The README claims identical flags, but libsodium was configured with CMAKE_C_FLAGS_RELEASE rather than the shared -march=native/-flto set.

## Use it when

- Hashing many short inputs (64 B-1 KB), such as keys, IDs, short records or dedup fingerprints, where per-call overhead dominates. In this run, a 64-byte hash took \~111 ns vs \~300 ns through OpenSSL EVP with a fresh context.
- Keyed BLAKE2b as a MAC or PRF, or salt/personalization for domain separation, through a one-call API with no context to manage.
- x86-64 hosts with AVX2, where the runtime-dispatched AVX2 compression applies. The blake2b_simd README measured libsodium at 3.07 cycles/byte, only \~9% behind its own 2.81.
- Projects that already link libsodium, or want one small dependency-free C library. The README lists Windows (MinGW/MSVC on x86, x64 and arm64), iOS, Android, JavaScript and WebAssembly.
- Variable-length digests (for example the 32-byte default) where the length is a real BLAKE2b parameter, not a truncation.

## Skip it when

- Bulk hashing of large buffers. From 4 KB up it only ties OpenSSL, and at 16 KB it is \~4% slower (1349 vs 1403 MB/s). BLAKE2b has no NEON path, so ARM gets portable C.
- Maximum-throughput hashing. BLAKE3 is a different and much faster hash, and blake2b_simd adds BLAKE2bp and multi-message hashing; libsodium offers neither parallel mode.
- Code that already reuses its OpenSSL digest context. The small-message win largely comes from the harness allocating and freeing an EVP_MD_CTX on every hash, and reused contexts were not measured.
- Code that selects algorithms by name through OpenSSL's EVP/provider layer. libsodium's API is fixed-function, so swapping it in means touching call sites.
- Wherever the only evidence you would rely on is this benchmark. It is one laptop run from a 0-star repo, with no CPU model or compiler recorded, and libsodium was built with different CFLAGS than the other libraries.

## How it is fast

sodium_init() picks a compression function via CPUID: Samuel Neves's AVX2 BLAKE2b (added in 1.0.9), then SSE4.1, SSSE3, or portable C (blake2b_compress_ref). There is no NEON path, so on the Apple Silicon machine that produced these numbers both libsodium and OpenSSL ran portable C compression. The gap there is call overhead. The one-shot function keeps its state on the stack with no allocation or provider lookup, while the harness's OpenSSL path runs EVP_MD_CTX_new, EVP_DigestInit_ex(EVP_blake2b512()), Final and free on every hash: about 111 ns vs 300 ns per 64-byte hash. At large sizes, libsodium's update copies every 128-byte block through its 256-byte internal buffer, whereas OpenSSL's blake2b_prov.c compresses runs of blocks straight from the input. That is consistent with OpenSSL pulling ahead by \~4% at 16 KB.

## Compared with alternatives

Pick libsodium when you need standard, keyed or personalized BLAKE2b from C/C++ (or any of its language bindings) inside a stable, dependency-free library. blake2b_simd is Rust and \~9% faster on AVX2, with BLAKE2bp and many-message hashing; minio/blake2b-simd is Go-only; BLAKE3 is far faster but produces different digests. Take one of those when throughput matters more than BLAKE2b compatibility or a C API.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (autotools configure/make, build.zig, or MSVC solutions from VS2010 to VS2026), also consumable as a Zig dependency |
| **Dependencies** | none |
| **Minimum toolchain** | Not documented as a single minimum. It ships autotools, Zig and MSVC (vs2010-vs2026) build files, and 1.0.21 fixed builds with GCC on aarch64 and gcc 4.x. |
| **Platforms** | Any (Linux, macOS, Windows x86/x64/arm64, iOS, Android, JavaScript/WebAssembly). BLAKE2b SIMD runs only on x86/x86-64 (AVX2 &gt; SSE4.1 &gt; SSSE3, runtime-dispatched); ARM and everything else use portable C. |
| **Thread safety** | Per the docs, all functions are thread-safe once sodium_init() has returned, and sodium_init() is safe to call repeatedly and from several threads. Hash states are caller-owned. |
| **Drop-in for the baseline** | partial: it produces the same RFC 7693 BLAKE2b digest as EVP_blake2b512 if you ask for 64 bytes of output, but through a different C API, and the default output is 32 bytes |

## Gotchas

- Call sodium_init() first. The compression pointer starts as blake2b_compress_ref and is switched to AVX2/SSE4.1/SSSE3 only inside sodium_init(), so skipping it silently leaves x86 on the portable C path.
- Output length is a BLAKE2b parameter, not a truncation. crypto_generichash's default 32-byte digest is BLAKE2b-256 and will not equal the first 32 bytes of EVP_blake2b512's output; request 64 bytes to match OpenSSL.
- BYTES_MIN (16) and KEYBYTES_MIN (16) are documented minimums that are not enforced: the code accepts any output of 1-64 bytes and keys of 0-64 bytes (issue #1131). crypto_generichash_final() returns -1 if called twice, and it wipes the state.
- Static builds export internal blake2b_init/blake2b_init_key symbols, which can clash with other embedded BLAKE2 copies. Issue #1434 reports this with static Qt 6.8.1 on wasm, and the maintainer says Qt fixed it on its side.

## Known shortcomings

- Evidence is an obscure suite (0 stars, one laptop run, no CPU model or compiler). The small-input win mostly reflects OpenSSL's per-hash EVP_MD_CTX_new/free and init overhead, and libsodium was not built with the suite's shared -march/-flto flags. Comparison is BLAKE2b vs SHA-2 (cross-algorithm).
- The small-message win is mostly harness overhead (OpenSSL creates/initializes/frees an EVP_MD_CTX per hash: 111 vs 300 ns at 64 B); libsodium has no NEON BLAKE2b, so both ran portable C on the Apple Silicon machine, and at 16 KB OpenSSL is 4% ahead. SIMD paths activate only after sodium_init(); default 32-byte output differs from a BLAKE2b-512 digest; KEYBYTES_MIN not enforced (#1131); static builds export blake2b_\* symbols (#1434).

## Caveats and trade-offs

This is a harvested shootout result, not a claim libsodium makes about itself. It is a single local run (2025-11-05) on a MacBook Air by the author of an obscure 0-star benchmark repo; the CPU model and compiler are not recorded. The small-size gap is inflated by the harness: the OpenSSL adapter calls EVP_MD_CTX_new, EVP_DigestInit_ex(EVP_blake2b512()) and EVP_MD_CTX_free on every hash, while libsodium makes one crypto_generichash_blake2b call. The 64-256B gains therefore mostly measure OpenSSL EVP per-call overhead rather than the BLAKE2b compression function, and at 16KB OpenSSL is \~4% faster. The README says flags are identical, but the build scripts pass libsodium CMAKE_C_FLAGS_RELEASE rather than the shared -march=native/-flto flags.

libsodium's crypto_generichash BLAKE2b API differs from OpenSSL's EVP interface; the advantage shrinks and reverses as the buffer grows past \~8KB, so it is a small-message win rather than an across-the-board one.

## Maintenance

Actively maintained: 1.0.22 was released 2026-04-09, commits run to 2026-09-22, and it has \~14k stars. The library is ISC-licensed with no dependencies, and security fixes go to the stable branch first. The BLAKE2b code has been essentially unchanged for years (the AVX2 path dates to 1.0.9), and ARM still has no SIMD path for it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** result.json from scc-tw/cryptobench-cpp (harness: src/benchmarks/hash_benchmarks.cpp plus src/adapters/{libsodium,openssl}_adapter.cpp) has BM_Libsodium_BLAKE2b and BM_OpenSSL_BLAKE2b means that match every claimed number exactly. It still falls short of A because the CPU model and the compiler and version are not recorded. It is not B either: this is an obscure personal repo (0 stars, no LICENSE file, last commit 2025-11-05) and one local laptop run, not a well-known independent suite or a peer-reviewed paper, so it is third-party numbers with partial methodology, which is C.
- **Verifier notes:** All five libsodium and OpenSSL BLAKE2b means in result.json match the record exactly, and the ratios are correct. libsodium metadata checks out: 13,965 stars, last commit 2026-09-22, not archived or a fork, GitHub reports NOASSERTION but the LICENSE file is ISC. The hardware L1D was wrong (64KB, not 32KB). Tier cut from B to C because the suite is not well known. The OpenSSL per-call EVP context allocation makes the small-message win largely an API-overhead artifact.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/scc-tw/cryptobench-cpp/blob/main/result.json>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/result.json>
  - <https://github.com/scc-tw/cryptobench-cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/README.md>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/CompilerFlags.cmake>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/FetchOpenSSL.cmake>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/FetchLibsodium.cmake>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/openssl_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/libsodium_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/benchmarks/hash_benchmarks.cpp>
  - <https://github.com/jedisct1/libsodium>
  - <https://raw.githubusercontent.com/jedisct1/libsodium/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/jedisct1/libsodium>
  - <https://github.com/jedisct1/libsodium/blob/master/README.markdown>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/include/sodium/crypto_generichash_blake2b.h>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/include/sodium/crypto_generichash.h>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/crypto_generichash/blake2b/ref/generichash_blake2b.c>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/crypto_generichash/blake2b/ref/blake2b-ref.c>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/crypto_generichash/blake2b/ref/blake2.h>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/crypto_generichash/blake2b/ref/blake2b-compress-ref.c>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/crypto_generichash/blake2b/ref/blake2b-compress-avx2.c>
  - <https://github.com/jedisct1/libsodium/blob/master/src/libsodium/sodium/core.c>
  - <https://github.com/jedisct1/libsodium/blob/master/ChangeLog>
  - <https://github.com/jedisct1/libsodium/releases>
  - <https://github.com/jedisct1/libsodium/tags>
  - <https://github.com/jedisct1/libsodium/issues?q=blake2b>
  - <https://github.com/jedisct1/libsodium/issues?q=neon>
  - <https://github.com/jedisct1/libsodium/issues/949>
  - <https://github.com/jedisct1/libsodium/issues/1131>
  - <https://github.com/jedisct1/libsodium/issues/1434>
  - <https://github.com/jedisct1/libsodium/issues/1471>
  - <https://doc.libsodium.org/hashing/generic_hashing>
  - <https://doc.libsodium.org/usage>
  - <https://github.com/scc-tw/cryptobench-cpp>
  - <https://github.com/scc-tw/cryptobench-cpp/blob/main/result.json>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/result.json>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/README.md>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/cmake/FetchLibsodium.cmake>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/libsodium_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/adapters/openssl_adapter.cpp>
  - <https://raw.githubusercontent.com/scc-tw/cryptobench-cpp/main/src/benchmarks/hash_benchmarks.cpp>
  - <https://raw.githubusercontent.com/openssl/openssl/master/providers/implementations/digests/blake2b_prov.c>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/jedisct1/libsodium`) · [data/wave7/enrich/raw/github_com_jedisct1_libsodium.json](../../../data/wave7/enrich/raw/github_com_jedisct1_libsodium.json) (enrichment confidence 0.75)

</details>
