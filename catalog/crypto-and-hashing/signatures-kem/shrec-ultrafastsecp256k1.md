# UltrafastSecp256k1

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 secp256k1 ECDSA/Schnorr engine: about 1.5x faster CT signing and 1.1x faster verify than libsecp256k1, and 11-22x faster than OpenSSL.

| | |
|---|---|
| **Beats** | OpenSSL (ECDSA_do_sign/ECDSA_do_verify, secp256k1); also benchmarked against libsecp256k1 (bitcoin-core) |
| **Claimed result** | Versus OpenSSL ECDSA_do_sign/ECDSA_do_verify on secp256k1: ECDSA sign 21.56x and verify 10.89x faster (FAST path), 21.70x for constant-time signing, and generator multiplication 44.53x (ratios printed on the page). Versus the in-tree libsecp256k1 (derived from page data): constant-time ECDSA sign about 1.52x (29,406.82 vs 19,311.25 ns), constant-time Schnorr sign about 1.48x (22,544.75 vs 15,232.60 ns), ECDSA verify about 1.13x (41,501.75 vs 36,772.26 ns) and Schnorr verify about 1.15x (42,088.13 vs 36,754.89 ns). The 19,441.6 ns figure the record labeled CT-vs-CT is actually the non-CT FAST sign. In Bitcoin Core bench_bitcoin ConnectBlock runs (README and docs/BITCOIN_CORE_BENCH_RESULTS.json, measured 2026-05-12, not this page) the gain is +0.9-1.5% with LTO and -0.5 to -1.0% without LTO. |
| **Workload** | Single-operation ECDSA sign/verify and Schnorr (BIP-340) sign/verify on secp256k1, via the project's bench_unified microbenchmark (RDTSCP timer, 11 passes, 500-iteration warmup, pinned core, turbo disabled) |
| **Metric** | latency |
| **Hardware** | Intel Core i5-14400F; governor=performance, intel_pstate/no_turbo=1, pinned to core 0 via taskset, TSC 2.496GHz |
| **Compiler and flags** | GCC 14.2.0, Release+LTO, -O3 -flto -march=native (libsecp256k1 comparison compiled -O3 -march=native, no LTO, in the same binary) |
| **Adoption** | 55 stars; Bitcoin Core PR #35469 (opt-in secondary secp256k1 backend) was closed unmerged with a Concept NACK on 2026-06-05 |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/shrec/UltrafastSecp256k1) · [benchmark](https://github.com/shrec/UltrafastSecp256k1/blob/main/docs/bench_unified_2026-09-07_gcc14_x86-64.json) |

## Verdict

The project's own bench_unified was run with GCC 14.2.0 Release+LTO (-O3 -march=native) on an i5-14400F with turbo off and a pinned core, taking the median of 11 passes. CT ECDSA sign took 19.3 us, versus 29.4 us for an in-tree libsecp256k1 snapshot (f9a944f, compiled without LTO) and 419 us for system OpenSSL ECDSA_do_sign (version not recorded). ECDSA verify took 36.8 us, versus 41.5 us and 400 us. Bitcoin Core's bench_bitcoin ConnectBlock shrinks the advantage to +0.9-1.5% with LTO.

## Use it when

- Signing-heavy x86-64 services (wallet signers, Taproot key-path and script-path signing) where roughly 1.5x lower CT sign latency than libsecp256k1 matters and you can build with LTO. bench_bitcoin shows +10% on SignTransaction and +35% on SignSchnorrWithMerkleRoot.
- Code that currently does secp256k1 ECDSA through OpenSSL's generic EC code (ECDSA_do_sign/ECDSA_do_verify): about 11x faster verify and 22x faster sign, with no OpenSSL dependency.
- Projects that need many secp256k1 protocols in one library (MuSig2, FROST, BIP-352 Silent Payments scanning, Ethereum ecrecover, BIP-32), optionally with GPU batch verify or scanning. Sparrow's Frigate uses it for Silent Payments scanning.
- Polyglot stacks that want one engine behind the C ABI through its Python, Node.js, Rust, Go, C#, Java or Swift bindings.
- Differential testing or evaluation of an alternative backend for code written against libsecp256k1, using the link-time shim.

## Skip it when

- Consensus-critical block validation. The real bench_bitcoin ConnectBlock gain is only +0.9-1.5% with LTO and 0.5-1.0% slower without LTO. Bitcoin Core closed the backend PR (#35469) with a Concept NACK because it lacked human review.
- Anywhere that requires an independent security audit. None exists, all audit evidence is self-generated, and serious correctness bugs were fixed as recently as September 2026: Schnorr batch verify accepted invalid signatures (#400), FieldElement::sqrt was wrong for about 18% of inputs (#402), and Pippenger MSM returned wrong points (#401).
- Memory- or startup-constrained processes that use the variable-time k\*G path. By default it builds a window_bits=18 fixed-base table of about 250 MB (about 5 s of arithmetic) on first use and caches it to a per-user cache directory. Bitcoin Core backend mode uses a compiled-in w=8 table instead.
- Browser/WASM, where the README calls CT evidence incomplete, and iOS builds via SPM or CocoaPods, which have CT guards disabled.
- Protocols that need libsecp256k1-identical ECDSA nonces with ndata, or custom noncefp callbacks. The shim rejects custom noncefp, and its nonce bytes differ unless you build with SECP256K1_SHIM_RFC6979_COMPAT=ON.

## How it is fast

Field elements use 5x52-bit limbs (FE52, needs __int128), with optional x86-64 BMI2/ADX assembly and safegcd (Bernstein-Yang) inversion. Verification uses a Strauss/Shamir dual multiplication: GLV endomorphism split plus wNAF, precomputed w=15 odd-multiple tables for G and 2^128\*G (8192 entries each, built on the first verify), and an effective-affine (isomorphic-curve) w=5 table for the public key. Constant-time signing uses a libsecp-style signed-digit multi-comb for k\*G (11 blocks x 32 entries, Hamburg encoding) with AVX2-vectorized constant-time table scans. The variable-time k\*G path uses a large windowed fixed-base table.

## Compared with alternatives

None of the siblings is an alternative for the same curve. ENG25519 does X25519/Ed25519, fasthqc is the HQC KEM and VecFalcon is Falcon signing. Pick this one only when the protocol requires secp256k1 ECDSA or BIP-340 Schnorr, as Bitcoin and Ethereum do.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake-built libfastsecp256k1; optional libufsecp C ABI library and a libsecp256k1-compatible shim target) |
| **Dependencies** | None for the CPU build (no Boost or OpenSSL). The GPU backends need the CUDA toolkit, an OpenCL runtime or the Metal SDK. OpenSSL is used only by the benchmark. |
| **Minimum toolchain** | C++20 and CMake 3.18+. The README says GCC 11+, Clang 15+ or MSVC 2022. The FAQ says GCC 10+ or Clang 14+, and the shim README says GCC 13+ or Clang 16+. |
| **Platforms** | x86-64 (the optional asm needs BMI2/ADX; AVX2 is used for CT lookups when available), ARM64, RISC-V RV64GC, Android, iOS, WASM (experimental), ESP32 and STM32. GPU: CUDA 12+, OpenCL, Metal. ROCm/HIP is not validated. |
| **Thread safety** | CPU functions are stateless and re-entrant. Global generator tables are built once (call_once, or a mutex-guarded shared_ptr snapshot) and then only read. A ufsecp context or GPU context must not be shared across threads. The shim applies context_randomize blinding per thread, not per context. |
| **Drop-in for the baseline** | partial — the shim can replace libsecp256k1 at link time with no source changes, but it rejects custom noncefp, produces different nonce bytes when ndata is used (unless built with the compat flag), keeps blinding per thread, and holds MuSig2 keyagg state in a process-global map. There is no drop-in path for OpenSSL's EC API. |

## Gotchas

- `secp256k1::ecdsa_sign()` in the fast namespace is variable-time: it has data-dependent branches in scalar reduction and the source says not to use it with real keys. Production signing must call `ct::ecdsa_sign` (the C ABI and shim already do). The 21.56x OpenSSL 'FAST' sign ratio was measured on this unsafe path; the CT ratio is 21.70x.
- The first variable-time k\*G call can take seconds and write a file of about 250 MB (cache_w18.bin) under \~/.cache/secp256k1, \~/Library/Caches or %LOCALAPPDATA%. Set SECP256K1_FIXED_BASE_DISK_CACHE=OFF to prevent this. The precompute path can throw std::runtime_error.
- The speedups depend on LTO and a locked CPU frequency. Without LTO, ConnectBlock is slower. In an unlocked-frequency run, libsecp256k1 was 7.5% faster on ConnectBlockAllEcdsa; the repo calls that result a measurement artifact.
- The docs contradict each other. For example, the shim README still shows CT ECDSA sign 9% slower than libsecp256k1 and cites 'OpenSSL 3.x', while the canonical benchmark shows 1.52x faster and does not record the OpenSSL version. The verify tables (about 1.3 MB) stay allocated at exit and trigger leak checkers unless you call release_process_resources().

## Known shortcomings

- Headline 'CT' figure (19,441.6 ns) is actually the fast, variable-time path; the constant-time path is 1.52x slower. ConnectBlock numbers come from the README, not the benchmark page. Bitcoin Core PR #35469 to adopt it was closed with a Concept NACK.
- Against the real incumbent, libsecp256k1, gains are only 1.1-1.5x in microbenchmarks, and Bitcoin Core ConnectBlock improves \~1% with LTO and is slower without. No third-party audit; Sep 2026 fixes for Schnorr batch verify accepting invalid signatures (#400), wrong sqrt on \~18% of inputs (#402) and wrong Pippenger points (#401). Fast k\*G builds a \~250 MB table on first use and caches it under \~/.cache. The 21.56x-vs-OpenSSL signing ratio uses the variable-time `fast` path (constant-time ratio 21.70x vs OpenSSL, but see docs contradictions). Benchmark build set experimental REPSEARCH_\* flags not in public sources (retiered A to C).

## Caveats and trade-offs

The benchmark is first-party and self-reported, with no third-party reproduction. The JSON does not record the OpenSSL version (system library). OpenSSL uses its generic prime-curve code for secp256k1, so the &gt;10x OpenSSL ratios reflect a weak baseline; the relevant incumbent, libsecp256k1, is beaten by only about 1.1-1.5x in micro-benchmarks. In those comparisons libsecp256k1 was compiled without LTO while Ultra used LTO. The ConnectBlock gain is about 1% and needs LTO; without LTO it turns negative. That benchmark also reuses only 5 pubkeys, which the repo itself says inflates the ECDSA-verify share of the gain through caching. The repo's metadata admits an earlier benchmark file mislabeled the libsecp256k1 version (the actual version is a pre-v0.8.0 master snapshot, f9a944f). No external security audit exists; all audit evidence is self-generated. Bitcoin Core rejected the backend PR (#35469, Concept NACK, citing its human-review bar). [retier] Benchmark build used experimental REPSEARCH_\* flags absent from public sources; Sep 2026 correctness fixes (#400 batch verify accepted invalid signatures, #401 Pippenger, #402 sqrt) postdate the numbers; OpenSSL version not recorded.

The large margin over OpenSSL mostly reflects OpenSSL's unoptimized generic EC code path for secp256k1 (a curve OpenSSL does not special-case the way it does NIST P-curves), so it is a much easier target than the curve's actual production incumbent, libsecp256k1; against libsecp256k1 the realistic block-validation workload shows near-parity

## Maintenance

Actively developed: v4.6.0 was released 2026-09-24 and the dev branch has commits through 2026-09-26. It is MIT-licensed and ships as CMake builds plus apt, brew, pip, npm and NuGet packages. Adoption is thin (55 stars, one publicly known production adopter) and there is no third-party audit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now C.
- **Tier reason:** The benchmark JSON contains OpenSSL ECDSA_do_sign/ECDSA_do_verify and libsecp256k1 rows measured in the same harness, and states the compiler (GCC 14.2.0), flags (Release+LTO -O3 -flto -march=native; libsecp -O3 -march=native) and CPU (i5-14400F). The harness src/cpu/bench/bench_unified.cpp (with libsecp_provider.c) is public, so the result is first-party but reproducible: tier A.
- **Retiered** A to C: Enrichment found the benchmark build set experimental REPSEARCH_\* flags that are not in the main/dev sources, so the published numbers cannot be reproduced from public code; correctness bugs in Schnorr batch verify (accepted invalid signatures, #400), sqrt (#402) and Pippenger (#401) were fixed in Sep 2026 after the numbers were taken; the 21.56x OpenSSL signing ratio uses the variable-time path. First-party only, no third-party audit.
- **Verifier notes:** The OpenSSL ratios and the libsecp raw numbers are on the page. The ConnectBlock numbers come from the README and docs/BITCOIN_CORE_BENCH_RESULTS.json, not the benchmark_url. The record's last_commit of 2026-09-27 was the repo pushed_at timestamp; the default branch (main) last commit is 2026-09-24, and the dev branch has a commit from 2026-09-26. The 'proposed, not yet merged' Bitcoin Core wording was misleading because the PR was closed with a Concept NACK.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/docs/bench_unified_2026-09-07_gcc14_x86-64.json>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/docs/bench_unified_2026-09-07_gcc14_x86-64.json>
  - <https://github.com/shrec/UltrafastSecp256k1>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/README.md>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/src/cpu/bench/bench_unified.cpp>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/docs/BITCOIN_CORE_BENCH_RESULTS.json>
  - <https://github.com/bitcoin/bitcoin/pull/35469>
- **Sources the enricher read:**
  - <https://github.com/shrec/UltrafastSecp256k1>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/README.md>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/docs/bench_unified_2026-09-07_gcc14_x86-64.json>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/docs/BITCOIN_CORE_BENCH_RESULTS.json>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/docs/THREAD_SAFETY.md>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/docs/FAQ.md>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/compat/libsecp256k1_shim/README.md>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/bench/bench_unified.cpp>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/include/secp256k1/ecmult_gen_comb.hpp>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/include/secp256k1/precompute.hpp>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/src/precompute.cpp>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/src/point.cpp>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/src/ct_point.cpp>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/src/ecdsa.cpp>
  - <https://github.com/shrec/UltrafastSecp256k1/blob/main/src/cpu/src/ct_sign.cpp>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/src/cpu/src/ct_scalar.cpp>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/src/cpu/src/ct_field.cpp>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/src/cpu/include/secp256k1/config.hpp>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/main/src/cpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shrec/UltrafastSecp256k1/dev/src/cpu/src/ct_point.cpp>
  - <https://github.com/shrec/UltrafastSecp256k1/issues>
  - <https://github.com/shrec/UltrafastSecp256k1/issues/400>
  - <https://github.com/shrec/UltrafastSecp256k1/issues/402>
  - <https://github.com/shrec/UltrafastSecp256k1/issues/174>
  - <https://github.com/shrec/UltrafastSecp256k1/releases>
  - <https://github.com/bitcoin/bitcoin/pull/35469>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/shrec/ultrafastsecp256k1`) · [data/wave7/enrich/raw/github_com_shrec_ultrafastsecp256k1.json](../../../data/wave7/enrich/raw/github_com_shrec_ultrafastsecp256k1.json) (enrichment confidence 0.8)

</details>
