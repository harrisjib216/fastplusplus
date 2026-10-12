# VecFalcon (Vectorized Falcon-Sign)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT (root LICENSE). The C-FN-DSA-derived opt/ and ref/ directories carry the Unlicense. opt/fft_neon.c is Apache-2.0 (derived from GMUCERG Falcon_NEON).` · 🟢 active

> Falcon/FN-DSA signing with a batched SIMD Gaussian BaseSampler and RISC-V FFT; sign_core runs 1.13-1.59x faster than C-FN-DSA.

| | |
|---|---|
| **Beats** | C-FN-DSA (Thomas Pornin's FN-DSA/Falcon implementation, github.com/pornin/c-fn-dsa at commit 96e3b92), SHAKE256X4 variant |
| **Claimed result** | Falcon-512 sign_core cycles vs the C-FN-DSA reference: 1.13x SSE2, 1.23x AVX2, 1.36x AVX-512F, 1.17x NEON, 1.37x RV64GC, 1.36x RV64GCB, 1.58x RV64GCV, 1.59x RV64GCVB (the paper reports these as 13-59% improvements). Falcon-1024: 1.14x-1.59x. The BaseSampler core without PRNG is 4.2x (SSE2), 8.4x (AVX2), 9.8x (AVX-512F), 7.7x (RVV), 3.8x (RV64IM) and 1.8x (NEON) faster than the C-FN-DSA ref core. With PRNG included it is 1.3x-2.7x. RVV FFT/iFFT is 4.1x-4.7x faster than ref on the SpacemiT X60, and RV64D FFT/iFFT is 2.7x-3.0x faster. |
| **Workload** | Falcon-512/1024 sign_core (SHAKE256X4 PRNG variant; SHAKE256X8 on AVX-512F) CPU-cycle medians over 10,000 runs (x86, ARM) or 2,000 runs (RISC-V) across SSE2, AVX2, AVX-512F, NEON, RV64GC, RV64GCB, RV64GCV and RV64GCVB. Also micro-benchmarks of the vectorized BaseSampler and the RVV/RV64D FFT/iFFT. |
| **Metric** | throughput |
| **Hardware** | Intel i7-11700K (Rocket Lake, 3.6GHz, Turbo Boost and Hyper-Threading disabled); ARM Cortex-A72 (Raspberry Pi 4B, 1.5GHz); SpacemiT X60, RVV v1.0 VLEN=256 (Milk-V Jupiter, 2.0GHz) |
| **Compiler and flags** | GCC 13.3.0 (x86-64, Ubuntu 24.04); Clang 10.0.0 (ARM, Ubuntu 20.04); GCC 13.2.0 (RISC-V, Bianbu 1.0.15). All builds use -O2 -DFNDSA_SHAKE256X4=1. x86 builds pin the ISA with -msse2, -mavx2 or -mavx512f plus -mno-\* flags for higher extensions. RISC-V builds use -march=rv64gc, rv64gc_zba_zbb, rv64gcv or rv64gcv_zba_zbb. |
| **Adoption** | 4 stars; IACR TCHES 2026 accepted paper artifact |
| **Last commit** | 2025-12-05 |
| **Links** | [repository](https://github.com/Ji-Peng/VecFalcon) · [benchmark](https://eprint.iacr.org/2025/1867) |

## Verdict

The paper compares median sign_core cycles of VecFalcon against C-FN-DSA commit 96e3b92, with both built at -O2 using the SHAKE256X4 PRNG (10,000 runs on x86 and ARM, 2,000 on RISC-V). Falcon-512 gains 1.13x (SSE2), 1.23x (AVX2) and 1.36x (AVX-512F) on an i7-11700K with GCC 13.3.0, 1.17x (NEON) on a Cortex-A72 with Clang 10, and 1.36-1.59x across RV64GC/GCB/GCV/GCVB on a SpacemiT X60 with GCC 13.2.0; Falcon-1024 gains 1.14-1.59x. Micro-benchmarks put the BaseSampler core (excluding PRNG) at 1.8-9.8x and the RVV FFT/iFFT at 4.1-4.7x faster than the reference, and the repo's raw speed files match the paper's Table 6.

## Use it when

- Falcon signing on RISC-V application cores with RVV 1.0 and VLEN=256 (SpacemiT X60 class): sign_core runs 1.58-1.59x faster, the largest gain in the paper.
- Signing-latency-bound Falcon on x86-64 servers with AVX-512F or AVX2: sign_core runs 1.36x and 1.23x faster on Falcon-512 (full fndsa_sign about 1.23x and 1.18x).
- You are porting Falcon signing to another SIMD ISA and want a worked, correctness-checked template for a batched RCDT BaseSampler or a deeply layer-merged double-precision FFT.
- Your deployment only needs signatures that verify, not ones that match test vectors, and you control the signer's build flags and CPU target.

## Skip it when

- You need interoperability with FIPS 206 or current c-fn-dsa. The code is frozen on Feb 2025 pre-draft C-FN-DSA. In July 2026 upstream changed key and signature encodings, the public-key format, the signature norm bound and message hashing (an ML-DSA-style 'mu' value that includes a public-key hash), and it explicitly does not promise backward compatibility.
- You need KAT reproducibility or identical output across builds: the vectorized sampler reorders PRNG use, and AVX-512F builds use a different PRNG (SHAKE256X8) from all other builds.
- Keygen- or verify-heavy workloads: only signing was optimized, and verify cycles match the reference within noise in the repo's raw data.
- You need portable binaries or Windows/MSVC builds. Each build targets one ISA with no runtime dispatch for the new sampler, the RVV code assumes VLEN=256 (the paper only suggests how to adapt it for VLEN=128 cores such as the C908), and the sample store is allocated with posix_memalign, which MSVC does not provide.
- Production or no-heap embedded use: every signing attempt heap-allocates the \~1 KB sample store and never checks the allocation for NULL. The project is a 4-star paper artifact with no releases, issues or downstream users found.

## How it is fast

Falcon's BaseSampler scans a 72-bit reverse cumulative distribution table (RCDT) inside SamplerZ and takes about 30% of signing time in the paper's profile. It is normally scalar because matching the known-answer tests (KATs) fixes the order in which PRNG output is consumed. VecFalcon drops that ordering and computes 16-64 samples at once in 32-bit SIMD lanes (three 24-bit limbs per value, with a compare/subtract/shift borrow chain). It folds the bimodal sign flip and the squaring into the same pass and buffers 128 samples in a per-signature GAUSSIAN0_STORE. On RISC-V it adds hand-written RVV FFT/iFFT that uses strided vlse64/vsse64 loads with 4+4 (Falcon-512) and 4+5 (Falcon-1024) layer merging, plus a 3-layer-merged scalar RV64D FFT. The rest of the gain comes from third-party Keccak and FFT code: XKCP 8-way Keccak on AVX-512 (as a SHAKE256X8 PRNG), Becker-Kannwischer hybrid 4-way Keccak and the Nguyen-Gaj NEON FFT on ARM, and the Zhang et al. RV64I/RV64IB Keccak on RISC-V.

## Compared with alternatives

No siblings catalogued yet.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | None at runtime beyond libc (posix_memalign). The ARM and RISC-V paths add assembly files (.S) built by the C compiler. gperftools and pprof are needed only to reproduce the profiling table. |
| **Minimum toolchain** | Not documented. Tested with GCC 13.3.0 (x86-64), Clang 10.0.0 (AArch64) and GCC 13.2.0 (RISC-V; needs -march=rv64gcv with RVV 1.0 support) |
| **Platforms** | x86-64 (a separate build for each of SSE2, AVX2 and AVX-512F), AArch64 NEON (tested on Cortex-A72), RV64GC/RV64GCB, and RV64GCV/RV64GCVB with RVV 1.0 at VLEN=256 only. Linux-oriented (posix_memalign, perf-based cycle counting). |
| **Thread safety** | Not documented. No mutable globals were found. Sampler state and its heap-allocated store live per call, so concurrent calls on separate buffers look safe. |
| **Drop-in for the baseline** | partial — it keeps C-FN-DSA's fndsa.h API (commit 96e3b92) and its signatures verify, but output differs for a given seed, each build targets one ISA, and the code predates c-fn-dsa's July 2026 FN-DSA-draft format changes |

## Gotchas

- The headline numbers are for sign_core, which excludes hash-to-point and key decoding. Full fndsa_sign gains in the repo's raw files are smaller on Falcon-512: 1.09x SSE2, 1.18x AVX2, 1.23x AVX-512F, 1.12x NEON and 1.28-1.43x on RISC-V.
- The x86 BaseSampler is selected at compile time (#if FNDSA_AVX512F / FNDSA_AVX2) and its AVX2/AVX-512 intrinsics lack upstream's per-function target attribute. The Makefile therefore compiles whole files with -mavx2 or -mavx512f (plus -mno-\* flags to pin the ISA), and the binary needs that ISA at runtime. FNDSA_AVX2 still defaults to 1 on x86, so an SSE2 build must pass -DFNDSA_AVX2=0 -DFNDSA_SSE2=1.
- opt/test_fndsa.c comments out test_sampler, test_sign_core, test_keygen_ref and test_kat, which ref/ still runs. Signing correctness rests on sign-then-verify self tests plus a subroutine-level BaseSampler comparison against the reference in profiling/ (make run_test).
- The RISC-V benchmark reads cycles with rdcycle, which the README says traps with Illegal Instruction on newer kernels (e.g. 6.6.63); use perf stat as the RISC-V Makefile does.

## Known shortcomings

- Research code (4 stars): sign_core speedup is per-signature cycle latency, not throughput; the 8.4x figure is the AVX2 BaseSampler core only (max 9.8x on AVX-512F), and full signing with PRNG gains only 1.3-2.7x over C-FN-DSA. Part of the gain comes from third-party Keccak and NG23 FFT code.
- Frozen on the Feb 2025 pre-draft C-FN-DSA: upstream changed key/signature formats and hashing in Jul 2026, so no FIPS 206 or current c-fn-dsa interop. Full fndsa_sign gains are small (Falcon-512: 1.09-1.23x x86, 1.12x NEON, 1.28-1.43x RISC-V). Not KAT-reproducible (AVX-512 build uses a different PRNG); one ISA per build, no runtime dispatch; RVV assumes VLEN=256; posix_memalign blocks MSVC; heap allocation per signing attempt with unchecked NULL; opt/ tests disable sampler/sign_core/KAT tests.

## Caveats and trade-offs

Gains are for signature generation (sign_core) only, not keygen or verify, and are measured on the SHAKE256X4 variant, which is not KAT-compatible with default Falcon signing (interoperable for verification). Part of the gain comes from integrated third-party code: XKCP 8-way Keccak on AVX-512F; the BK22 hybrid Keccak and NG23 NEON FFT on ARM; ZYHK25 Keccak on RISC-V. The paper measured C-FN-DSA as faster than the NIST-submission AVX2 code on the i7-11700K, so it is a strong baseline. The only direct comparison with other optimized prior work is at the BaseSampler level (NG23 NEON is slower than ref). Licensing is mixed: MIT, Unlicense (public-domain dedication, no patent grant) and Apache-2.0 files. GitHub's detector reports NOASSERTION.

Baseline is the C-FN-DSA reference implementation, not liboqs's own bundled Falcon backend directly, though the two are architecturally related (liboqs's Falcon derives from the same lineage of reference/optimized code); the vectorized BaseSampler deliberately breaks bit-for-bit KAT reproducibility with official test vectors while preserving verification interoperability

## Maintenance

This is a TCHES 2026 paper artifact whose last commit was 2025-12-05, with no releases, issues or forks. Its MIT, Unlicense and Apache-2.0 files make it copyable, but it is frozen on pre-draft C-FN-DSA code, so treat it as a source of techniques to port onto current c-fn-dsa rather than as a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The ePrint 2025/1867 paper (published in TCHES 2026, DOI 10.46586/tches.v2026.i1.302-324) benchmarks sign_core against the C-FN-DSA reference at commit 96e3b92 (Table 6) and states the compiler (GCC 13.3.0, Clang 10.0.0, GCC 13.2.0), the flags (-O2, -DFNDSA_SHAKE256X4=1, per-ISA -m/-march flags) and the CPUs (i7-11700K, Cortex-A72, SpacemiT X60). The artifact repo ships the benchmark code for both sides (opt/speed_fndsa.c and ref/speed_fndsa.c with per-platform Makefiles, plus profiling/ for BaseSampler and FFT) and the raw outputs (opt/ and ref/speed_fndsa_\*.txt), which match Table 6.
- **Verifier notes:** All claimed numbers check out against Tables 4-6 of the paper and the repo's raw speed files. The one overstatement was 'up to 8.4x faster than prior work': 8.4x is the AVX2 BaseSampler core vs the C-FN-DSA ref, and the maximum is 9.8x on AVX-512F. The record's metric is 'throughput', but the paper measures per-signature cycle latency. Metadata verified: 4 stars, not a fork, not archived, last commit 2025-12-05 (active), usability copyable (all components are under OSI licenses).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `workload`, `license`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** TCHES 2026 (ePrint 2025/1867) Tables 4-6: vs C-FN-DSA ref @96e3b92, GCC 13.3/Clang 10, -O2 -DFNDSA_SHAKE256X4=1; BaseSampler 8.4x AVX2 / 9.8x AVX-512F; signing 1.3-2.7x.
- **Pages the verifier opened:**
  - <https://eprint.iacr.org/2025/1867>
  - <https://eprint.iacr.org/2025/1867.pdf>
  - <https://github.com/Ji-Peng/VecFalcon>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/LICENSE>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/LICENSE>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/ref/LICENSE>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/README.md>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/Makefile>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/speed_fndsa_11700k.txt>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/ref/speed_fndsa_11700k.txt>
  - <https://api.crossref.org/works?query.bibliographic=Vectorized+Falcon-Sign+Implementations+SSE2+AVX2+AVX-512F+NEON+RVV&rows=3>
- **Sources the enricher read:**
  - <https://github.com/Ji-Peng/VecFalcon>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/README.md>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/LICENSE>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/LICENSE>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/README.md>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/Makefile>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/Makefile.armv8a>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/Makefile.rv>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/fndsa.h>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/inner.h>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/sign_sampler.c>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/sign_core.c>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/sign_inner.h>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/sha3.c>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/util.c>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/test_fndsa.c>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/ref/test_fndsa.c>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/speed_fndsa_11700k.txt>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/ref/speed_fndsa_11700k.txt>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/speed_fndsa_cortex_a72.txt>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/ref/speed_fndsa_cortex_a72.txt>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/opt/speed_fndsa_x60.txt>
  - <https://github.com/Ji-Peng/VecFalcon/blob/main/ref/speed_fndsa_x60.txt>
  - <https://github.com/Ji-Peng/VecFalcon/issues?q=is%3Aissue>
  - <https://github.com/Ji-Peng/VecFalcon/commits/main>
  - <https://eprint.iacr.org/2025/1867>
  - <https://eprint.iacr.org/2025/1867.pdf>
  - <https://api.crossref.org/works/10.46586/tches.v2026.i1.302-324>
  - <https://github.com/pornin/c-fn-dsa>
  - <https://github.com/pornin/c-fn-dsa/commits/main>
  - <https://hn.algolia.com/api/v1/search?query=VecFalcon>
  - <https://hn.algolia.com/api/v1/search?query=%22Vectorized%20Falcon%22>
  - <https://github.com/search?q=gaussian0_rvv_bisq&type=code>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/ji-peng/vecfalcon`) · [data/wave7/enrich/raw/github_com_ji_peng_vecfalcon.json](../../../data/wave7/enrich/raw/github_com_ji_peng_vecfalcon.json) (enrichment confidence 0.8)

</details>
