# Code Generation of Faster Formally Verified NTT with Plantard Reduction

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · ⚪ unknown

> Python generator emitting lazily-reduced Plantard NTTs (C/Jasmin) for ML-KEM/ML-DSA/FN-DSA; 1.5-2.5x faster than pq-crystals reference NTT.

| | |
|---|---|
| **Beats** | NIST PQC / pq-crystals reference C implementations of ML-KEM (Kyber ref) and ML-DSA (Dilithium ref) for end-to-end and NTT results, plus formosa-mlkem Jasmin (NTT only); mlkem-native/mldsa-native scalar C (OPT=0 AUTO=0) is compared only at NTT level |
| **Claimed result** | End-to-end vs pq-crystals reference C (Table 3): ML-KEM-512 decaps 1.32x, encaps 1.27x, keygen 1.17x (ML-KEM-768/1024 1.13-1.24x); ML-DSA-2 sign 1.26x, verify 1.16x, keygen 1.11x (ML-DSA-3/5 1.08-1.25x). NTT vs reference C: forward 1.47-1.83x, inverse 1.66-2.48x (Table 1). Vs formosa-mlkem Jasmin, ML-KEM NTT 1.26x and INTT 2.19x (round-trip 1.63x); these are kernel-level numbers, not end-to-end. Vs mlkem-native scalar C, the ML-KEM forward NTT is slower (0.86x) and INTT is 1.18x; vs mldsa-native, 1.66x/1.52x (Table 2). |
| **Workload** | ML-KEM-512 decapsulation/encapsulation/keygen and ML-DSA-2 signing/verification/keygen CPU cycle counts; also isolated forward/inverse NTT cycle counts |
| **Metric** | latency |
| **Hardware** | Intel Xeon E-2314 @ 2.80GHz, 4 cores, TurboBoost/Hyper-Threading disabled |
| **Compiler and flags** | gcc-11.4 -O3 -fomit-frame-pointer (C, matching the pq-crystals test_speed setup); Jasmin 2025.6.1 + clang-14 -O3 -march=native -fomit-frame-pointer -fwrapv (verified backend); 10k iterations, rdtsc with cpuid, median of three per-run medians |
| **Links** | [repository](https://anonymous.4open.science/r/pkc_anonymous_artifact-8F22) · [benchmark](https://eprint.iacr.org/2026/1624) |

## Verdict

On an Intel Xeon E-2314 with turbo and HT off, using gcc 11.4 -O3 -fomit-frame-pointer, the generated NTT was dropped into the pq-crystals reference C. It cut forward/inverse NTT cycles by 1.83x/2.48x for ML-KEM, 1.73x/1.78x for ML-DSA and 1.47x/1.66x for FN-DSA-1024. End to end that gives 1.08x-1.32x (ML-KEM-512 decaps 162,047 to 122,499 cycles; ML-DSA-2 sign 1.26x). It is 1.26x/2.19x vs the formosa-mlkem Jasmin NTT and 0.86x/1.18x vs mlkem-native scalar C, and the artifact's kyber.csv/dilithium.csv/falcon1024.csv medians match the paper's tables.

## Use it when

- Scalar or portable ML-KEM/ML-DSA builds derived from the pq-crystals reference C, such as generic x86-64 packages that cannot assume AVX2 or other 64-bit targets, where the NTT is a measurable share of decapsulation or signing.
- ML-DSA scalar code: the generated NTT beat mldsa-native's scalar C (OPT=0 AUTO=0) by 1.66x forward and 1.52x inverse in the paper's Table 2.
- Generating an NTT for a new NTT-friendly modulus (q prime, n a power of two, n | q-1; complete or incomplete NTT) without hand-tuning where reductions go.
- Verification or research work that needs a Plantard-based ML-KEM NTT with an EasyCrypt proof chain down to the formosa-mlkem spec (Jasmin backend, x86-64).

## Skip it when

- AVX2, AVX-512 or NEON-optimized ML-KEM/ML-DSA deployments: there is no vector backend. The authors measured their hand-tuned Plantard AVX2 about 10% (16-bit, ML-KEM) and 28% (32-bit, ML-DSA) slower than Montgomery AVX2.
- When mlkem-native scalar C is the baseline: under gcc -O3 the generated ML-KEM forward NTT is slower (0.86x) because its 32-bit intermediate halves auto-vectorization lanes. Only the inverse wins (1.18x).
- When you need a maintained, packaged library: the code exists only as an ephemeral double-blind anonymous.4open.science mirror with no releases, issue tracker or public git history.
- When you need verified C: the C backend, the ML-DSA/FN-DSA outputs and the Python generator are all unverified. The paper also notes that constant-time behavior of the C depends on the compiler.
- When you expect big whole-scheme wins: end-to-end gains are only 1.08x-1.32x because the NTT is a small share of total cycles (3,876 cycles of the roughly 91k-122k per ML-KEM-512 operation).

## How it is fast

It uses Plantard multiplication by a precomputed twiddle (Huang et al.). This needs one fewer multiplication per butterfly than Montgomery and leaves outputs in a tighter centered range, so fewer Barrett/Montgomery reduction passes are needed. At generation time, a static bound analyzer tracks per-layer coefficient growth: the CT butterfly grows additively and the GS plus-arm doubles. It inserts a reduction only on layers where the signed word would otherwise overflow. Per the paper, ML-KEM needs one reduction (inverse layer 3), ML-DSA none and FN-DSA-1024 several. Each layer is emitted as its own loop with len and k baked in as constants, so there is no runtime branch on the layer index.

## Compared with alternatives

Dilithium-AVX512 (ML-DSA) and VecFalcon (Falcon signing) are vector-ISA implementations and win only where AVX-512/AVX2/NEON etc. are available. Pick this for scalar/portable ML-KEM or ML-DSA built on the pq-crystals reference, or when you need a verified ML-KEM NTT; no sibling covers ML-KEM (fasthqc is HQC).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Generated C: none beyond &lt;stdint.h&gt; (__int128 when q &gt;= 2^32). Generator: Python &gt;= 3.9 with click, jinja2 and pycryptodome. Jasmin path: the Jasmin compiler. Proofs: EasyCrypt with the Jasmin library and an SMT solver. |
| **Minimum toolchain** | Generator needs Python 3.9+. The C output was tested only with gcc 11.4 (-O3 -fomit-frame-pointer), and the L=64 path needs GCC/Clang __int128. The Jasmin output was built with Jasmin 2025.6.1 and clang-14. |
| **Platforms** | Generated C is portable scalar code but was benchmarked only on x86-64 (Intel Xeon E-2314). Jasmin output is x86-64 only. No SIMD paths. |
| **Thread safety** | Not documented. The generated ntt()/invntt() read only const twiddle tables and transform the caller's array in place; the files read have no global mutable state. |
| **Drop-in for the baseline** | partial — Kyber keeps pq-crystals' ntt()/invntt() signatures, and in Dilithium invntt_tomont() becomes invntt(). Integration also replaces reduce.c/h and edits poly.c: the tomont constant, invntt_tomont now calls poly_tomont first, poly_reduce after ntt is removed, and basemul/pointwise use Plantard. The paper reports NIST KAT outputs bit-identical to the reference. |

## Gotchas

- The scalar plantard_reduce() added to reduce.c multiplies signed values that overflow (int32 x PLAN_QINV for Kyber, int64 x PLAN_QINV for Dilithium). That is undefined behavior in C, and the Makefiles do not pass -fwrapv. The generated plantard_mul_reduce in ntt.c avoids this with unsigned casts.
- The README says the generator also produces the EasyCrypt proofs, but it only renders code templates. The paper lists proof emission as future work, and only the q=3329 ML-KEM Jasmin instance is proved.
- analyzer.py computes the Plantard input range (plan_bnd), but its per-layer reduction decisions check only the signed storage bound. Outputs for new parameter sets should be tested, not assumed correct.
- The shipped harnesses are asymmetric. The baseline kyber/dilithium test_speed.c keeps NTESTS 1000 and has no NTT+INVNTT row, while the Plantard variants use 10000. The paper states 10k iterations for all runs.

## Known shortcomings

- Code is an anonymous review artifact (anonymous.4open.science, Apache-2.0), not a maintained repo. Baseline is the pq-crystals reference C, not mlkem-native: forward NTT is 0.86x (slower) than mlkem-native. Scalar code only; no gain over AVX2 implementations.
- Wins only against the pq-crystals scalar reference (NTT 1.47-2.48x, end-to-end 1.08-1.32x); no SIMD backend (a Plantard AVX2 variant was 10-28% slower than Montgomery). Only the Jasmin ML-KEM NTT is formally proven; the C output, ML-DSA/FN-DSA outputs and the generator are unverified, and the README overclaims proof generation. The plantard_reduce() added to reduce.c has signed-overflow UB and the Makefiles lack -fwrapv. Not drop-in (poly.c edits, Montgomery-to-Plantard domain switch). Baseline harness ships with NTESTS 1000 vs 10000.

## Caveats and trade-offs

This is a 2026 ePrint preprint and not yet peer-reviewed. The code lives only at a double-blind-review anonymous.4open.science mirror (https://anonymous.4open.science/r/pkc_anonymous_artifact-8F22). Its web UI redirects, but its API serves the files. Links like this are temporary. All wins are over scalar reference C: no AVX2 backend is provided (the authors measured Plantard \~28% slower than Montgomery under AVX2), so this does not beat the optimized AVX2 ML-KEM/ML-DSA implementations, and the forward ML-KEM NTT loses to mlkem-native scalar C (0.86x). The Apache-2.0 license is from an anonymous copyright holder.

Improves only the NTT component, not a full drop-in library; targets ML-KEM/ML-DSA/FN-DSA jointly from one code generator, so gains are shared but modest end-to-end (&lt;1.3x for most operations).

## Maintenance

Maintenance is unknown: this is a double-blind review mirror of a 2026 ePrint preprint (not yet peer-reviewed), Apache-2.0 from 'Anonymous Authors', and no public git repo was found. The code is small enough to copy, but expect the link to expire.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A. The paper's anonymous artifact is reachable through the anonymous.4open.science API (README, Apache-2.0 LICENSE, and the benchmark Makefiles all fetched). It ships generator/benchmark/kyber/ref and dilithium/ref (unmodified pq-crystals baselines) next to kyber_plan_plannorm/ref and dilithium_plan/ref, with 'make speed' test_speed harnesses at -O3 -fomit-frame-pointer. The paper states gcc-11.4, the flags and the Intel Xeon E-2314 CPU.
- **Verifier notes:** The artifact the search agent could not open (HTTP 401) is reachable via https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/&lt;path&gt;. repo_url could be set to the anonymous artifact URL, though it is ephemeral. The record's baseline was wrong: end-to-end gains are vs pq-crystals reference C, not mlkem-native/mldsa-native or liboqs.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2026/1624>
  - <https://eprint.iacr.org/2026/1624.pdf>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/files/>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/README.md>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/LICENSE>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/Makefile>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber/ref/Makefile>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium/ref/Makefile>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/Makefile>
- **Sources the enricher read:**
  - <https://anonymous.4open.science/r/pkc_anonymous_artifact-8F22>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/files/>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/files?path=generator>
  - https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/files?path=ec_verification (recursive directory listing via ?path=)
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/README.md>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/LICENSE>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/.gitignore>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/ntt.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/ntt.h>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/reduce.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/reduce.h>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/poly.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/test/test_speed.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber_plan_plannorm/ref/Makefile>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber/ref/poly.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber/ref/test/test_speed.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber/README.md>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/ntt.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/ntt.h>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/reduce.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/reduce.h>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/poly.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/poly.h>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium_plan/ref/test/test_speed.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium/ref/poly.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium/ref/poly.h>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium/ref/test/test_speed.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium/README.md>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/generator.py>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/analyzer.py>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/lazygenerator.py>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/requirement.txt>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/templates/ntt_template_c.jinja2>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/output_c/script.py>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/test_kyber.c>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/kyber.csv>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/dilithium.csv>
  - <https://anonymous.4open.science/api/repo/pkc_anonymous_artifact-8F22/file/generator/benchmark/falcon1024.csv>
  - <https://eprint.iacr.org/2026/1624>
  - <https://eprint.iacr.org/2026/1624.pdf>
  - <https://hn.algolia.com/api/v1/search?query=plantard%20ntt&tags=story>
  - gh search repos "plantard ntt" (github.com, no public copy found)
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `paper:code-generation-of-faster-formally-verified-ntt-with-plantard-reduction`) · [data/wave7/enrich/raw/paper_code_generation_of_faster_formally_verified_ntt_with_plantard_reduction.json](../../../data/wave7/enrich/raw/paper_code_generation_of_faster_formally_verified_ntt_with_plantard_reduction.json) (enrichment confidence 0.75)

</details>
