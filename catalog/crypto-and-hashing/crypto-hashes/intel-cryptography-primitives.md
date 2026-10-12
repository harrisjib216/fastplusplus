# Intel Cryptography Primitives Library

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Cryptographic hashes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Intel's C crypto-primitives library (ex-IPP Crypto) with SHA-NI/AVX2/AVX-512 SHA-1/2/3 kernels; claimed but unbenchmarked alternative to OpenSSL.

| | |
|---|---|
| **Beats** | OpenSSL SHA-2/SHA-3 (implied incumbent only; no published comparison against it) |
| **Claimed result** | unquantified ("fast and lightweight", CPU-specific optimized code paths incl. SHA-NI); no numbers found in README, OVERVIEW.md, or BUILD.md |
| **Workload** | No benchmark numbers published in the repository; README/OVERVIEW.md only describe runtime CPU dispatching (SSE4.2/AVX2/AVX-512/AVX10.2 code paths) for SHA-1/224/256/384/512, SHA3-224/256/384/512, SHAKE128/256, MD5, SM3 and other primitives, marketed as 'a secure, fast and lightweight library ... highly-optimized for various Intel CPUs' |
| **Metric** | throughput |
| **Adoption** | 388 stars; formerly Intel IPP Cryptography (intel/ipp-crypto, which now redirects here); vendored as a git submodule in intel/QAT_Engine (crypto_mb multi-buffer backend) |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/intel/cryptography-primitives) |

## Verdict

Nothing has been measured publicly. The README, OVERVIEW, BUILD and CHANGELOG say only 'fast' and 'optimized performance for SHA3-...', with no hardware, compiler or baseline named. The repo ships a perfsys tool (ps_ippcp) to benchmark its own functions but publishes no results and no OpenSSL comparison, so any speedup over OpenSSL SHA-2/SHA-3 is unverified.

## Use it when

- x86-64 C/C++ code that already uses IPP-style APIs or needs SHA-2, SHA-3/SHAKE, SM3, AES, RSA/ECC and ML-KEM/ML-DSA from one Apache-2.0 vendor library
- Deployments on recent Intel parts where the SHA-NI, SHA512 or SM3 instruction paths and the AVX-512 Keccak kernel apply
- Projects that need CAVP-tested algorithm implementations (certificates listed for the AVX-512 builds) and FIPS self-test hooks, and will do their own CMVP module validation
- Kernel-mode or footprint-sensitive builds: supports non-PIC static builds, per-ISA single-CPU libraries, and a custom-library tool that trims unused functions

## Skip it when

- When you need a measured win over OpenSSL: no published first- or third-party SHA-2/SHA-3 numbers exist, and OpenSSL also dispatches at runtime to SHA-NI/AVX2 assembly
- Hashing many independent streams in parallel: there is no public multi-buffer SHA-2/SHA-3 API (the multi-buffer library covers SM3 mb16 plus public-key and SM4 operations); see ISA-L Crypto for multi-buffer SHA
- Non-x86 targets (ARM, RISC-V) or macOS: code paths are x86 only, and the 1.4.0 changelog says it removed outdated macOS-specific code; validated on RHEL 8 and Windows Server 2022
- If you need a drop-in or a FIPS 140-3 certificate: the API is not EVP-compatible, and README_FIPS says the library is 'FIPS-Compliant' (CAVP only), not CMVP-certified
- Lightweight builds: needs CMake, NASM and Python, plus OpenSSL 3.5.7+/BoringSSL/Tongsuo unless the multi-buffer part is disabled

## How it is fast

The library contains several builds of each function: generic, SSE4.2 (y8), AVX2 (l9), AVX-512 Skylake (k0), AVX-512 Ice Lake (k1) and AVX10.2 (d1). A dispatcher picks one per CPU at init, and a second layer of feature checks turns on SHA-NI, the SHA512 and SM3 instructions (Lunar Lake/Arrow Lake), VAES and similar extensions. SHA-2 comes as hand-written NASM kernels: an AVX2 message schedule (pcpsha256l9as.asm), a SHA-NI path (pcpsha256nias.asm) and a SHA512-instruction path (pcpsha512l9ni.asm). SHA-3/SHAKE on AVX-512 builds use an assembly Keccak that keeps all 25 lanes in xmm0-xmm24 and uses vpternlogq/vprolq, with a 4-way variant used internally for SHAKE.

## Compared with alternatives

Choose it over ISA-L Crypto or sha2-with-c-intrinsic when you want one maintained Intel library that covers single-stream SHA-2 (SHA-NI and SHA512-instruction paths), SHA-3/SHAKE and SM3 alongside ciphers and PQC, with CAVP certificates. Use ISA-L Crypto for multi-buffer throughput across many streams, and BLAKE3/KangarooTwelve if you can change the hash function.

## Integration

| | |
|---|---|
| **Form** | static lib and shared lib (CMake; can also be pulled in via add_subdirectory) |
| **Dependencies** | Build: CMake 3.18+, NASM (3.01 tested), Python 3.12; OpenSSL 3.5.7+/BoringSSL/Tongsuo only for the crypto_mb multi-buffer part (drop with -DNO_CRYPTO_MB=TRUE) |
| **Minimum toolchain** | C; tested with GCC 8.5-16.1, Clang 16/21, MSVC 19.44 (VS 2022), Intel oneAPI icx 2026.2 |
| **Platforms** | x86-64 Linux/Windows (32-bit IA-32 deprecated); ISA paths y8 SSE4.2, l9 AVX2, k0/k1 AVX-512, d1 AVX10.2, plus a generic mx build; crypto_mb k1 also validated on FreeBSD |
| **Thread safety** | README claims a thread-safe design, with caller-allocated per-operation state and no hidden allocation; issue #106 (ML-KEM concurrent stack smash, fixed) shows this has had bugs |
| **Drop-in for the baseline** | no |

## Gotchas

- Fetch the hash-method pointer once, outside hot loops: calling ippsHashMethod_SHA256_TT() per hash writes a shared static and collapsed multi-thread scaling on a 24-core Xeon (issue #93)
- In the develop source, the first call to ippsHashMethod_SHA256_TT() ends with the non-SHA-NI update routine; only later calls switch it to SHA-NI, and all states share that static. So a pointer fetched once may not use SHA-NI; benchmark it
- Update/Message lengths are int, so feed inputs over 2 GiB in chunks; the non-_rmf hash APIs are slated for removal in 3.0.0 (issue #107)
- develop is an unstable snapshot; production code lives on cryptography-primitives_&lt;release&gt; branches. Pin a release, and use -DIPPCP_FIPS_MODE=on for the FIPS self-test build

## Known shortcomings

- No published performance numbers anywhere (the perfsys tool ships without results), so there is no measured speedup. Not FIPS 140-3 validated as claimed: FIPS-compliant with CAVP certificates only. Listed as a notable, widely used library (e.g. QAT_Engine submodule).
- By source reading: the first ippsHashMethod_SHA256_TT() call returns a non-SHA-NI update and later calls switch a shared static, so a cached method pointer may skip SHA-NI; issue #93: calling the getter in a hot loop wrecks multithreaded scaling. No public multi-buffer SHA-2/3 API (multi-buffer is SM3 only). x86 only; not an EVP drop-in; `int` lengths.

## Caveats and trade-offs

No first-party or third-party benchmark numbers found (README, OVERVIEW.md, CHANGELOG.md, perfsys docs, QAT_Engine docs); 'fast' is unquantified. The repo ships a perfsys performance tool (ps_ippcp, ps_crypto_mb) but publishes no results. Not FIPS 140-3 certified: README_FIPS.md says it is 'FIPS-Compliant' (CAVP algorithm testing only), not CMVP-certified. OpenSSL is not a generic no-dispatch baseline; it also has runtime-dispatched SHA-NI/AVX2 paths. Kept as a single Tier-D entry because it is Intel's widely referenced crypto primitives library.

C API with a runtime CPU-feature dispatcher (multiple codepaths compiled in, best one selected at init); large surface area beyond just hashing (AES, RSA, ECC, PQC, etc.); Intel-specific tuning means gains are concentrated on Intel CPUs with AVX-512/SHA-NI, may not help on AMD or older hardware.

## Maintenance

Actively maintained by Intel (last commit 2026-09-25, v2.4.0 changelog, 3.0.0 API cleanup under discussion) under Apache-2.0, so usable in proprietary code. It is a large build, not something to vendor as a snippet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** No benchmark page exists. README, OVERVIEW.md and CHANGELOG.md have only qualitative claims ('fast', 'Optimized performance for SHA3-...'), and the perfsys tool (tools/perfsys, documented in doc/source/performance-test-tool-perfsys-cli-options.rst) measures only the library itself, with no published results or OpenSSL comparison.
- **Verifier notes:** Metadata all check out (Apache-2.0, not archived or forked, last commit 2026-09-25, default branch develop). Main fixes: 'FIPS 140-3 validated' is false per README_FIPS.md, and the baseline wording wrongly said OpenSSL has no CPU dispatch. Not rejected despite &lt;1k stars because it is widely referenced (Intel QAT_Engine submodule, formerly IPP Crypto).
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/intel/cryptography-primitives>
  - <https://github.com/intel/cryptography-primitives/blob/develop/README.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/OVERVIEW.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/CHANGELOG.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/README_FIPS.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/doc/source/performance-test-tool-perfsys-cli-options.rst>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/crypto_mb/Readme.md>
  - <https://github.com/intel/QAT_Engine>
  - <https://github.com/intel/ipp-crypto>
- **Sources the enricher read:**
  - <https://github.com/intel/cryptography-primitives>
  - <https://github.com/intel/cryptography-primitives/blob/develop/README.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/OVERVIEW.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/BUILD.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/CHANGELOG.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/README_FIPS.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/SECURITY.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/include/ippcp.h>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/pcpvariant.h>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/hash/sha256/pcphashmethod_sha256_tt.c>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/hash/sha256/pcpsha256stuff.h>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/hash/sha3/pcpsha3ca.c>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/hash/sha3/sha3-256/pcphashmethod_sha3_256.c>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/hash/pcphashinit_rmf.c>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/hash/pcphashupdate_rmf.c>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/asm_intel64/pcpsha3_avx512vl.asm>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/asm_intel64/pcpsha3_avx512vl_mb4.asm>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/asm_intel64/pcpsha3_utils.inc>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/asm_intel64/pcpsha256l9as.asm>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/asm_intel64/pcpsha512l9ni.asm>
  - <https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/crypto_mb/Readme.md>
  - <https://github.com/intel/cryptography-primitives/blob/develop/doc/source/performance-test-tool-perfsys-cli-options.rst>
  - <https://github.com/intel/cryptography-primitives/issues?q=is%3Aissue>
  - <https://github.com/intel/cryptography-primitives/issues/93>
  - <https://github.com/intel/cryptography-primitives/issues/87>
  - <https://github.com/intel/cryptography-primitives/issues/22>
  - <https://github.com/intel/cryptography-primitives/issues/107>
  - <https://hn.algolia.com/api/v1/search?query=ipp-crypto&tags=story>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/intel/cryptography-primitives`) · [data/wave7/enrich/raw/github_com_intel_cryptography_primitives.json](../../../data/wave7/enrich/raw/github_com_intel_cryptography_primitives.json) (enrichment confidence 0.3)

</details>
