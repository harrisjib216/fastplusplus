# curve25519-voi

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Go Ed25519/X25519/sr25519 library ported from curve25519-dalek; \~1.9x faster signing, \~1.7x faster verification than Go 1.17 crypto/ed25519.

| | |
|---|---|
| **Beats** | Go standard library crypto/ed25519 and golang.org/x/crypto/curve25519 (X25519) for single operations; ed25519consensus (hdevalence) for batch verification, since stdlib has no batch verify; Cloudflare CIRCL also benchmarked |
| **Claimed result** | Native (AVX2) build, Go 1.17, i7-10510U. Ed25519 Verify: 125us (stdlib) to 75us, about 1.67x (derived from page data). Sign: 52.7us to 27.5us, about 1.92x (derived from page data). NewKeyFromSeed: 42.8us to 24.3us. X25519 ScalarBaseMult: 107us (x/crypto) to 24us, about 4.5x (derived from page data). X25519 ScalarMult shows no gain (107us vs 106us), and CIRCL is faster there at 65us. Batch verification is measured against ed25519consensus, not stdlib: VerifyBatch_1024 goes from 61.8ms to 31.7ms, about 1.95x (derived from page data), and to 24.0ms with precomputed expanded public keys. With the purego build (no assembly), Verify goes from 181us to 121us and Sign from 73.3us to 50.9us. |
| **Workload** | Ed25519 sign/verify/batch-verify (batch sizes 1-1024) and X25519 scalar multiplication |
| **Metric** | latency |
| **Hardware** | Intel Core i7-10510U @ 1.80GHz, turbo disabled |
| **Compiler and flags** | Go 1.17 toolchain, AMD64 with AVX2 assembly backend enabled; also measured with assembly disabled ("purego") |
| **Adoption** | 79 stars; oasis-core's go.mod pins curve25519-voi and replaces golang.org/x/crypto/ed25519 and x/crypto/curve25519 with it |
| **Last commit** | 2025-11-14 |
| **Links** | [repository](https://github.com/oasisprotocol/curve25519-voi) · [benchmark](https://github.com/oasisprotocol/curve25519-voi/blob/master/PERFORMANCE.md) |

## Verdict

The author's in-repo go test benchmarks (Go 1.17, Intel i7-10510U at 1.80 GHz, turbo off, AVX2 assembly on) show Ed25519 Verify at 75 us versus 125 us for crypto/ed25519 (\~1.67x) and Sign at 27.5 versus 52.7 us (\~1.92x). X25519 ScalarBaseMult was 24 us versus 107 us for x/crypto (\~4.5x), while ScalarMult was unchanged. Batch verification of 1,024 signatures was measured against ed25519consensus, not stdlib: 31.7 ms versus 61.8 ms (\~1.95x). With assembly disabled (purego), Verify was 121 us versus stdlib's 181 us.

## Use it when

- Go services whose throughput is bound by Ed25519 verification, such as consensus, gossip or transparency logs on AVX2 amd64: 75 us versus 125 us per verify in the author's Go 1.17 run.
- Verifying hundreds to thousands of mostly valid signatures at once, where you need cofactored or ZIP-215 semantics: 1,024 signatures took 31.7 ms versus 61.8 ms with ed25519consensus, and 24.0 ms when the keys were pre-expanded.
- Workloads that repeatedly verify against the same public keys, such as validator sets. An ExpandedPublicKey costs about 11.3 us and 1.5 KB to build and saves about 9 us per verify, so it pays for itself from the second verification.
- Generating many X25519 key pairs (fixed-base ScalarBaseMult): 24 us versus 107 us with x/crypto on the benchmark machine.
- Code that needs explicit, selectable Ed25519 acceptance rules (stdlib-compatible, FIPS 186-5/RFC 8032, ZIP-215) or sr25519/Merlin/ECVRF in Go without cgo.

## Skip it when

- X25519 Diffie-Hellman with arbitrary peer points (variable-base ScalarMult): 106 us versus 107 us with x/crypto, so there is no gain, and Cloudflare CIRCL (BMI2) was faster at 65 us.
- You need signatures accepted exactly as crypto/ed25519 accepts them, and in batches: the default semantics differ from stdlib, and the stdlib-compatible preset cannot be batch-verified.
- You need numbers for current Go: every figure is from Go 1.17 on one 2021 laptop CPU. The baselines have since changed (x/crypto/curve25519 is now a thin wrapper over crypto/ecdh), and the repo publishes no newer comparison.
- Secret-key hygiene or constant-time guarantees on every target: the README says it makes no attempt at memory sanitisation, and warns that wasm gives no constant-time assurances.
- Toolchains or platforms off the supported list: gccgo is rejected, Go 1.18+ is enforced, CI runs only Go 1.18 on amd64 (arm64 CI is open issue #66), and no external audit is documented (issue #3 was closed without a linked report).

## How it is fast

On amd64 it runs dalek's AVX2 backend, rewritten as avo-generated Go assembly: four field elements in radix 2^25.5 are packed into YMM registers so Edwards point additions and doublings proceed four lanes at a time, and scalar field multiplication uses assembly taken from George Tankersley's ristretto255. Signing, keygen and X25519 ScalarBaseMult use a precomputed Edwards basepoint table (then convert to Montgomery form) instead of a Montgomery ladder. Single cofactored verification uses ABGLSV-Pornin multiplication, where 2-D lattice reduction shortens the scalars so fewer doublings are needed. Batch verification uses Straus's method for small batches and Pippenger multiscalar multiplication above an internal threshold, and can cache per-key NAF tables through ExpandedPublicKey.

## Compared with alternatives

Pick it when you are in Go and want cgo-free Ed25519/X25519 with batch verification and configurable acceptance rules. ENG25519 (AVX-512 IFMA) and the SUPERCOP amd64-64-24k Ed25519 code are C/assembly aimed at raw cycles, and watsign targets JavaScript/wasm.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/crypto, golang.org/x/sys |
| **Minimum toolchain** | Go 1.18+ with the gc compiler (enforced by a compile-time gate in internal/toolchain; go.mod still says go 1.17); the README says it tracks the latest two Go releases |
| **Platforms** | 64-bit backend: amd64 (AVX2 assembly when available), arm64, ppc64, ppc64le, s390x; 32-bit backend: 386, arm, mips, mipsle, mips64, mips64le, riscv64, loong64, wasm; everything else unsupported |
| **Thread safety** | not documented; Sign/Verify are stateless functions over byte slices, while BatchVerifier holds mutable state and documents no locking |
| **Drop-in for the baseline** | partial — primitives/ed25519 and primitives/x25519 copy the crypto/ed25519 and x/crypto/curve25519 function shapes, but default Verify semantics differ from stdlib (pass VerifyOptionsStdLib via VerifyWithOptions for identical acceptance), and batch verification has no stdlib equivalent |

## Gotchas

- Default Verify is cofactored, rejects small-order and non-canonical A, rejects non-canonical R and requires S &lt; L. Mixing it with crypto/ed25519 in a consensus system can split acceptance, so pin a preset explicitly.
- BatchVerifier.Verify is only faster than serial verification when every signature is valid. One bad signature triggers per-entry re-verification, and VerifyBatchOnly just returns false without saying which entry failed.
- A batch containing any entry with CofactorlessVerify (for example the StdLib preset) always returns false from VerifyBatchOnly, and AddWithOptions panics on nil options.
- The deprecated ScalarMult writes all zeroes for low-order points; use X25519, which returns an error. Sign allocates (64 B, 1 alloc per call) where stdlib allocates nothing.

## Known shortcomings

- Go library. The batch-verify gain (61.8 to 31.7 ms) is against ed25519consensus, not Go's stdlib; baselines are Go (stdlib, CIRCL), not OpenSSL or libsodium.
- All numbers are Go 1.17 on one 2021 laptop; the baseline has since moved (x/crypto/curve25519 now wraps crypto/ecdh) with no newer benchmark. X25519 variable-base scalar multiplication is no faster than x/crypto, and CIRCL is faster. Default Verify semantics differ from the stdlib; the stdlib-compatible preset cannot batch; one bad signature makes a batch slower than serial verification. No documented audit; CI is Go 1.18 amd64 only.

## Caveats and trade-offs

The batch-verify baseline is ed25519consensus, not Go stdlib, which has no batch verification. X25519 variable-base ScalarMult is no faster than x/crypto, and CIRCL (which uses BMI2) beats it. The benchmark harness for the CIRCL and ed25519consensus comparisons is not in the repo; only the stdlib and x/crypto comparisons are. All numbers come from a single 2021-era laptop CPU on Go 1.17. There is no comparison with OpenSSL or libsodium.

Precomputed public keys cost \~1.47KiB memory each; Go-only, not usable directly from C++; some batch-verify configurations allocate more memory than stdlib

## Maintenance

Slow but maintained: the last commit is 2025-11-14 (String methods on key types), preceded by feature work in 2022-2023. It is BSD-3-Clause, used by oasis-core, and has 89 known importers of primitives/ed25519 on pkg.go.dev.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now A.
- **Tier reason:** PERFORMANCE.md states Go 1.17, Intel Core i7-10510U with turbo disabled, and native (AVX2 assembly) versus purego builds. The stdlib head-to-heads are reproducible from in-repo benchmark code: primitives/ed25519/ed25519_test.go (BenchmarkSigning and BenchmarkVerification, with voi and stdlib sub-benchmarks), primitives/ed25519/batch_verify_test.go and primitives/x25519/x25519_test.go (voi vs x/crypto). Go's gc compiler has no optimisation flags beyond the build tag, so tier A holds.
- **Verifier notes:** This is a downgrade for a misattributed claim, not for the tier (it stays A). The record credited the 61.8ms to 31.7ms VerifyBatch_1024 win to stdlib, but that column is ed25519consensus. The record's /blob/main/ benchmark URL returns 404 because the default branch is master. The last commit on master is 2025-11-14, about 10 months ago, so the project is active, not stale.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/oasisprotocol/curve25519-voi>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/main/PERFORMANCE.md>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/PERFORMANCE.md>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/go.mod>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/README.md>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/ed25519/ed25519_test.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/ed25519/batch_verify_test.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/x25519/x25519_test.go>
  - <https://github.com/oasisprotocol/oasis-core/blob/master/go/go.mod>
- **Sources the enricher read:**
  - <https://github.com/oasisprotocol/curve25519-voi>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/README.md>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/PERFORMANCE.md>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/go.mod>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/.github/workflows/ci-tests.yml>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/internal/toolchain/constraints.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/internal/toolchain/version_is_recent.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/internal/toolchain/compiler_is_gc.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/x25519/x25519.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/ed25519/ed25519.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/ed25519/batch_verify.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/ed25519/ed25519_precomputation.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/primitives/ed25519/ed25519_test.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/curve/scalar_mul_vartime_double_base.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/curve/scalar_mul_abglsv_pornin.go>
  - <https://github.com/oasisprotocol/curve25519-voi/blob/master/curve/edwards_vector_amd64.go>
  - <https://github.com/oasisprotocol/curve25519-voi/commits/master>
  - <https://github.com/oasisprotocol/curve25519-voi/issues?q=is%3Aissue>
  - <https://github.com/oasisprotocol/curve25519-voi/issues/3>
  - <https://github.com/oasisprotocol/curve25519-voi/issues/66>
  - <https://github.com/oasisprotocol/curve25519-voi/issues/74>
  - <https://github.com/oasisprotocol/curve25519-voi/issues/112>
  - <https://github.com/golang/crypto/blob/master/curve25519/curve25519.go>
  - <https://pkg.go.dev/github.com/oasisprotocol/curve25519-voi/primitives/ed25519?tab=importedby>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/oasisprotocol/curve25519-voi`) · [data/wave7/enrich/raw/github_com_oasisprotocol_curve25519_voi.json](../../../data/wave7/enrich/raw/github_com_oasisprotocol_curve25519_voi.json) (enrichment confidence 0.78)

</details>
