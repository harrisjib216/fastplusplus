# avxbls-sig (AVX-512 BLS signatures on BLS12-381)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> AVX-512 IFMA BLS12-381 BLS signature code (keygen, sign, aggregate, verify) layered on blst; paper claims at least 1.57x over blst.

| | |
|---|---|
| **Beats** | blst (supranational/blst x64 assembly: blst_sign_pk_in_g1/g2, hash_to_g1/g2, pairing aggregation) |
| **Claimed result** | Repository publishes no numbers (test.c prints scalar/baseline versus vec average cycles at run time). Paper 'Efficient SIMD Implementation of the BLS Signature Scheme Using Intel AVX-512' (TCHES 2026, ePrint 2026/947; abstract seen as a WebSearch snippet only): the vectorised BLS software using AVX-512 (AVX-512IFMA, 8-way 52x52-bit multiplies) is at least 1.57 times faster than an x64 assembly implementation of blst, benchmarked on an Intel Core i3-1005G1 (Ice Lake). Per-operation figures not read. |
| **Workload** | Per-operation cycle counts (rdtsc average over many iterations) in test.c, AVX-512 vector routines versus blst scalar calls for scalar multiplication, point add/double, sk_to_pk, subgroup checks, hash-to-curve, signing in G1 and G2, and pairing-based aggregate/verify; the BLS scheme operations keygen, signing, aggregation, verification. |
| **Metric** | latency |
| **Hardware** | Not stated in the repo; the paper snippet names an Intel Core i3-1005G1 (Ice Lake, AVX-512 IFMA). |
| **Compiler and flags** | makefile: /opt/gcc-13.3/bin/gcc -O3 -fomit-frame-pointer -m64 -mbmi2 -fwrapv -mtune=native -march=native -z noexecstack -w, linked against libblst.a built by build.sh (blst flags -O3 -fno-builtin -fPIC, -D__ADX__ when the CPU has ADX, -mno-avx). |
| **Adoption** | 0 stars, 0 forks; sibling of the catalogued hchengv/avxbls (optimal ate pairing) |
| **Last commit** | 2026-03-12 |
| **Links** | [repository](https://github.com/ganqin-liu/avxbls-sig) · [benchmark](https://eprint.iacr.org/2026/947) |

## Verdict

The repo publishes no numbers; test.c prints rdtsc-averaged cycles (cpuid-serialised TSC reference cycles, 10,000-100,000 iterations after a 1,000-10,000 iteration warm-up) for each blst call next to its \*_vec counterpart, with blst built from the vendored ADX x64 assembly and the vector code by GCC 13.3 -O3 -march=native. The only headline is the TCHES 2026 paper (ePrint 2026/947, abstract seen through search snippets only, eprint.iacr.org EGRESS_BLOCKED): at least 1.57x faster than blst's x64 assembly on an Intel Core i3-1005G1 (Ice Lake), without per-operation tables or a statement of which hash-to-curve the aggregation rows used.

## Use it when

- Single-thread latency of BLS12-381 signing, aggregation or verification on Intel Ice Lake, Tiger Lake, Sapphire Rapids or newer, or AMD Zen 4 and newer (AVX-512 IFMA present).
- Prototyping or researching vectorised pairing-based cryptography where you want per-operation cycle counts of a blst call and its AVX-512 counterpart from one harness (test.c prints both).
- Code that already links blst and wants to swap selected hot calls (sk_to_pk, subgroup checks, final verify) for vector versions while keeping blst types and serialization.
- Closed systems that control both signer and verifier, where the non-standard SwiftEC hash is acceptable, or builds that set SWIFTEC_ON to 0 to keep standard SSWU hashing.

## Skip it when

- Interoperable BLS (Ethereum consensus, Filecoin, Chia, IETF ciphersuites) with the default build: bindings/fp12_avx.h sets SWIFTEC_ON 1, so messages hash with SwiftEC instead of RFC 9380 SSWU and signatures will not verify against standard implementations.
- CPUs without AVX-512 IFMA (AMD before Zen 4, Intel Alder Lake and later client parts with AVX-512 disabled, ARM): there is no runtime dispatch or scalar fallback for the \*_vec routines.
- Production signing services: research prototype with 0 stars, no releases, no API documentation, self-tests that print error counts instead of failing, and all compiler warnings suppressed (-w).
- Throughput-oriented batch verification across many cores: only single-call, single-thread paths are vectorised and measured; blst's multi-threaded and batch paths are not compared.

## How it is fast

Fp elements of the 381-bit prime are held as 8 limbs in radix 2^48 and multiplied with AVX-512IFMA vpmadd52lo/hi (52x52-bit multiply-accumulate), with several independent field operations packed into one register (2x2, 4x2 and 8x1 lane layouts for Fp and Fp2). Point addition and doubling formulas in G1 and G2 are rescheduled so their independent multiplications fill parallel lanes. G1 scalar multiplication keeps blst's constant-time structure (GLV split via the beta endomorphism, Booth-encoded width-5 windows, full-table masked gather), the G1 subgroup check uses the sigma/times(-z) endomorphism test, and the Miller loop and final exponentiation reuse the sibling avxbls pairing code. Hash-to-curve is available both as vectorised standard SSWU (hash_to_g1_vec/hash_to_g2_vec) and as vectorised SwiftEC, a cheaper SWIFT-style encoding using sqrt(-3), which is the compiled default.

## Compared with alternatives

Pick it over hchengv/avxbls when you need the signature-scheme layer (hash-to-curve, signing, subgroup checks, aggregate and final verify) rather than only the optimal ate pairing it builds on. VROOM (SimonLangowski) reports a larger pairing gain over BLST (3.9x on its own bench) with RNS Montgomery arithmetic but offers no BLS signing API.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | blst (vendored source in src_blst/ and build_blst/, built into libblst.a by build.sh; a prebuilt libblst.a is also committed) |
| **Minimum toolchain** | GCC with AVX-512 IFMA intrinsics; makefile hard-codes /opt/gcc-13.3/bin/gcc with -O3 -march=native -mtune=native; C11 (aligned_alloc) |
| **Platforms** | x86-64 with AVX-512F/VL and AVX-512IFMA, Linux-oriented makefile |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the \*_vec functions take blst structs and mirror blst signatures, but they are separate names, and the default SwiftEC hashing changes H(m) and therefore every signature; rebuild with SWIFTEC_ON 0 for blst-compatible hashing |

## Gotchas

- Harness flaw: with the committed SWIFTEC_ON 1, the aggregation benchmarks (bench_g1/g2_aggmode1, bench_g1/g2_aggregate) time vendored blst_pairing_chk_n_aggr_\* and chk_n_mul_n_aggr_\*, which hash with standard SSWU (Hash_to_G2/G1 in src_blst/aggregate.c), against \*_vec versions that hash with SwiftEC (src/aggregate_avx.c), so the aggregation speedup mixes vectorisation with a cheaper, non-standard hash-to-curve. The signing rows compare the authors' scalar blst_swiftec_g1/g2 plus blst signing, not stock blst signing.
- Self-tests are soft: p1signtest, p2signtest, maptog1test and maptog2test count mismatches and print 'error=N' but return 0, aggcorrecttest prints FAIL without stopping, and no test checks that a bad signature is rejected; read ./test output rather than trusting the exit code.
- bench_coreverify_g2 (commented out of main) is broken: under SWIFTEC_ON it writes a 288-byte G2 point from swiftec_g2_vec into a 144-byte blst_p1 (stack overflow hidden by -w) and derives the G2 public key from the G1 generator BLS12_381_G11; do not re-enable it as is.
- SwiftEC hash_to_field reads 48 bytes of expand_message_xmd output per Fp element (swiftec_g1_vec, swiftec_e1_impl, swiftec_g2_vec) instead of RFC 9380's 64, so field elements carry modulo-p bias, and blst_swiftec_g2 ignores the aug argument. README says to run ./bin/test, but the makefile builds ./test.

## Known shortcomings

- Repo has bench code and public flags but no numbers; the TCHES 2026 / ePrint 2026/947 claim of at least 1.57x over blst on an i3-1005G1 is from search snippets only (eprint.iacr.org blocked); reuses the catalogued avxbls pairing code.
- Enricher: bindings/fp12_avx.h sets SWIFTEC_ON 1, so the aggregation benches run vendored blst with the standard SSWU hash_to_G2/G1 (src_blst/aggregate.c) against the \*_vec paths using SwiftEC, mixing vectorisation with a cheaper hash, and the sign rows compare the authors' scalar blst_swiftec_\* code rather than stock blst signing. The default SwiftEC output is not RFC 9380, so signatures are not interoperable; self-tests print error=N and return 0 with no bad-signature test; the disabled bench_coreverify_g2 writes a 288-byte G2 point into a 144-byte blst_p1 (warning hidden by -w); the 48-byte hash_to_field gives modulo-p bias; README says ./bin/test while the makefile builds ./test. Paper 1.57x still snippet only.

## Caveats and trade-offs

Tier B rests on search snippets of the paper abstract (TCHES 2026, ePrint 2026/947), not on the paper itself: eprint.iacr.org and iacr.org are blocked here, so the per-operation cycle tables, the compiler version used and turbo settings were not read, and the 'at least 1.57x' lower bound cannot be mapped to specific operations. The repo README has no paper link; the link is inferred from the matching first author (Ganqin Liu, repo owner) and topic. test.c averages rdtsc (reference cycles, not core cycles) over 10,000-100,000 iterations after a 1,000-iteration warm-up, for scalar multiplication, point add/double, isogeny maps, sk_to_pk, subgroup checks, hash-to-curve, signing in G1 and G2, pairing aggregation (blst_pairing_chk_n_mul_n_aggr_pk_in_g1/g2), core verify and final verify. The baseline is the single-signature blst API built from a vendored blst copy (src_blst/server.c plus build_blst/assembly.S via build.sh: -O3 -fno-builtin -fPIC, -D__ADX__ when the CPU has ADX, -mno-avx), not blst's multi-threaded or batch-verification paths. The signing benchmarks hash with SwiftEC (blst_swiftec_\* from src/swiftec_blst.c, the authors' addition, not part of upstream blst) when the SWIFTEC_ON switch is set and with standard blst_hash_to_g1/g2 otherwise; where SWIFTEC_ON is defined was not located. A prebuilt libblst.a binary is committed and the makefile hard-codes /opt/gcc-13.3/bin/gcc. The pairing code builds on hchengv/avxbls (already listed, tier B), so verification gains overlap that entry. Needs AVX-512 IFMA (Ice Lake or newer). Retier to A if the paper names the compiler and flags matching the makefile. [retier] Repo has bench code and public flags but no numbers; the 'at least 1.57x over blst on an i3-1005G1' claim is a search snippet of ePrint 2026/947 (blocked). The aggregation benches run vendored blst with the standard SSWU hash against \*_vec paths using the cheaper SwiftEC hash (SWIFTEC_ON 1), and the sign rows compare the authors' scalar SwiftEC code, not stock blst; default SwiftEC signatures are not RFC 9380 interoperable. Reuses the catalogued avxbls pairing code; self-tests never fail on bad signatures.

Latency-optimised AVX-512 (IFMA-style 52-bit limb) code for x86-64 only, Linux oriented; built on blst (bundled in src_blst and a committed libblst.a) and links it for scalar fallbacks. Makefile hard-codes /opt/gcc-13.3/bin/gcc and -march=native. Covers keygen, signing, aggregation and verification on BLS12-381 (G1 and G2 variants). Research code with a cycle-count harness, no stable API documented.

## Maintenance

Active research code (22 commits from December 2025 to 2026-03-12, 0 stars, no issues, no releases) under Apache-2.0 and small enough to vendor, but a prototype: hard-coded /opt/gcc-13.3 compiler path, warnings suppressed, soft self-tests and non-standard SwiftEC hashing on by default.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Peer-reviewed TCHES 2026 paper (ePrint 2026/947; Ganqin Liu, Hao Cheng, Georgios Fotiadis, Jipeng Zhang, Johann Großschädl) reports the AVX-512 BLS software at least 1.57x faster than blst x64 assembly on an Intel Core i3-1005G1, seen only as search snippets (eprint.iacr.org and iacr.org EGRESS_BLOCKED). The repo has public bench code for both sides (test.c MEASURE_CYCLES rdtsc loops, vendored blst built by build.sh) and makefile flags, but the paper's tables, compiler version and a repo-to-paper link could not be read, so B not A; upgraded from C for consistency with hchengv/avxbls (B on a TCHES snippet).
- **Retiered** B to C: B to C (DASP precedent: harness and correctness evidence): the only numbers are search snippets of the ePrint 2026/947 abstract, and the committed harness compares vectorised SwiftEC hashing against blst's standard SSWU hash and the authors' own scalar SwiftEC signing rather than stock blst, so the speedup is not a like-for-like measurement; the default output is not RFC 9380 interoperable.
- **Verifier notes:** Repo has bench code but no numbers; paper claim (&gt;=1.57x vs blst on i3-1005G1, TCHES 2026) from two WebSearch snippets only, ePrint and iacr.org EGRESS_BLOCKED (one try each). Metadata confirmed on github.com: Apache-2.0 (LICENSE read), 0 stars, 0 forks, not a fork, 22 commits, last commit 2026-03-12 (active). Distinct from hchengv/avxbls (signature scheme vs pairing) but reuses its pairing code; benchmark_url set to the ePrint page found by search (not openable here).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** paper tables once ePrint is reachable; same-hash comparison against stock blst
- **Pages the verifier opened:**
  - <https://github.com/ganqin-liu/avxbls-sig>
  - <https://github.com/ganqin-liu/avxbls-sig/commits>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/README.md>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/test.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/makefile>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/bindings/blst.h>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src/fp12_avx.h>
- **Sources the enricher read:**
  - <https://github.com/ganqin-liu/avxbls-sig>
  - <https://github.com/ganqin-liu/avxbls-sig/commits>
  - <https://github.com/ganqin-liu/avxbls-sig/issues>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/README.md>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/test.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/makefile>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/build.sh>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/bindings/fp12_avx.h>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/bindings/intrin.h>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src/aggregate_avx.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src/e1ops_avx.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src/e2ops_avx.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src/swiftec_blst.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src/rdtsc64.S>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src/fp12_avx.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src_blst/aggregate.c>
  - <https://raw.githubusercontent.com/ganqin-liu/avxbls-sig/HEAD/src_blst/server.c>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ganqin-liu/avxbls-sig`) · [data/wave8/enrich/raw/github_com_ganqin_liu_avxbls_sig.json](../../../data/wave8/enrich/raw/github_com_ganqin_liu_avxbls_sig.json) (enrichment confidence 0.6)

</details>
