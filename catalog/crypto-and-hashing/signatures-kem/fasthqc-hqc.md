# fasthqc/hqc (vectorized sparse-dense multiplication + syndrome generation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Signatures and key exchange](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C` · `no license` · 🔴 abandoned

> AVX2 patch to the HQC Round-2 KEM's sparse-dense multiply and BCH syndrome step; 34-46% fewer cycles than the optimized reference.

| | |
|---|---|
| **Beats** | HQC NIST Round 2 optimized reference implementation (Aguilar-Melchior et al.); HQC is a KEM historically supported by liboqs |
| **Claimed result** | The report states "about 34 to 46%" fewer clock cycles than the HQC Round-2 optimized implementation with both patches applied. On the i5-4690S (Table 4): keygen 34.9-42.8%, encryption 33.7-45.2%, decryption 45.0-46.3%. On the i5-8400H (Table 8): keygen 32.5-36.3%, encryption 30.9-37.9%, decryption 40.0-43.2%. As speed ratios this is about 1.45-1.86x (derived from page data). The vectorized sparse-dense multiplication alone is "about 70-75%" faster (Table 1). syndrome_gen drops from 400,209 to 18,101 cycles, about 22x (derived from page data). |
| **Workload** | Clock-cycle counts for HQC Round-2 keygen, encryption and decryption (KEM) across all six Round-2 parameter sets (N = 24677 to 70853). Each figure is the average over 50 random data sets of the minimum of 1,000 runs, after 1,000 warm-up runs. The report also micro-benchmarks sparse-dense polynomial multiplication and syndrome_gen. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-4690S @ 3.20GHz (4th gen); Intel Core i5-8400H @ 2.50GHz (8th gen) |
| **Compiler and flags** | gcc 7.4.0 (Ubuntu 7.4.0-1ubuntu1\~18.04.1), stated only for the i5-8400H (patch v3) runs; no compiler is stated for the i5-4690S runs. Flags from Fast_Implementation/hqc-256-3/Makefile: -O3 -std=c99 -mavx -mavx2. Turbo Boost disabled. |
| **Adoption** | 6 stars |
| **Last commit** | 2020-04-11 |
| **Links** | [repository](https://github.com/fasthqc/hqc) · [benchmark](https://github.com/fasthqc/hqc/blob/master/report-23072019.pdf) |

## Verdict

Against the HQC Round-2 optimized implementation on a 4th-gen Core i5-4690S (Turbo off, compiler not stated), both patches together cut keygen cycles 34.9-42.8%, encapsulation 33.7-45.2% and decapsulation 45.0-46.3% across all six parameter sets. On an i5-8400H with gcc 7.4.0 (-O3 -mavx2) the reductions were 30.9-43.2%, about 1.45-1.86x in speed. Each figure is the mean of per-dataset minimum cycle counts over 1,000 runs for 50 random data sets.

## Use it when

- Studying or reproducing HQC Round-2 performance on x86-64 with AVX2 (Haswell and later): keygen, encapsulation and decapsulation for N = 24,677-70,853.
- As a reference technique for multiplying a sparse position list by a dense polynomial in F2[X]/(X^N-1), in quasi-cyclic code-based schemes where the sparse operand has weight around 100 and N is tens of thousands of bits. The report puts the multiplication alone at about 64-75% faster.
- As a template for vectorized BCH syndrome computation with a precomputed power table (400,209 to 18,101 cycles, about 22x, for n1 = 766 in the report).

## Skip it when

- Anything deployed. The code is not constant-time: fastConvolutionMult indexes memory by the secret sparse positions (C256[vbi], tab[i64]), and syndrome_gen2 branches on bits of the decoded word.
- Current HQC. This targets the Round-2 code base and its six parameter sets (hqc-128-1 ... hqc-256-3). liboqs now ships HQC-1/3/5 from the official 20250822-spec implementation (re-enabled by default in 0.16.0, July 2026), so the percentages and code will not carry over as-is.
- Multi-threaded use. Scratch buffers (C2, TT, tmp8), syndrome_gen2's static tmp_array and the precomputed tables are process-global mutable state.
- Any use that needs a license. The repo has no LICENSE file and has been abandoned since April 2020 (6 stars, no issues, no releases).
- Non-x86 or pre-AVX2 CPUs; the Arith2020 experiments additionally need PCLMUL and, for several tables, the gf2x 1.2 library.

## How it is fast

The 'fast convolution' keeps the sparse operand as a list of its w nonzero positions (67-153), so the product is the XOR of w copies of the dense polynomial, each shifted by one of those positions. Each shift is done with AVX2 256-bit shifts (_mm256_slli/srli_epi64 plus a carry from the neighboring word) and XORed into a double-length accumulator, followed by one vectorized reduction mod X^N-1; the baseline instead used an NTL-inspired vectorized multiply. syndrome_gen2 spreads the received BCH codeword bits into bytes with a shuffle and mask, then XOR-accumulates rows of a precomputed alpha^(ij) table, 16 syndromes per ymm register, instead of evaluating each syndrome separately in GF(2^10).

## Compared with alternatives

It is the only key-encapsulation and code-based post-quantum entry in this category. ENG25519 and UltrafastSecp256k1 are classical elliptic-curve code and VecFalcon is a post-quantum signature. Pick it only to study HQC or quasi-cyclic binary-polynomial arithmetic on AVX2; it is not a deployable alternative to any of them.

## Integration

| | |
|---|---|
| **Form** | source-drop (compile-time patch over the HQC Round-2 optimized source tree) |
| **Dependencies** | OpenSSL libcrypto (SHA-512 wrapper; the NIST rng/seedexpander in lib/), make, gcc; gf2x 1.2 for the Arith2020 TABLE1/2/3/5 experiments |
| **Minimum toolchain** | C99; gcc 7.4.0 tested; flags -O3 -std=c99 -mavx -mavx2 |
| **Platforms** | x86-64 with AVX2 required (the Arith2020 folders also need PCLMUL); benchmarked on Intel Core i5-4690S and i5-8400H, the latter with gcc 7.4.0 on Ubuntu 18.04 |
| **Thread safety** | Not thread-safe: file-scope global scratch buffers in patch.c, a static buffer in syndrome_gen2, and global GF/alpha tables that must be initialized once by calling syndrome_gen_init() from main. |
| **Drop-in for the baseline** | partial — keeps the NIST crypto_kem_\* API and KAT-identical output for the Round-2 hqc-256-3 code, but only as a patch to that obsolete code base, not to any current HQC implementation |

## Gotchas

- The PATCH2 syndrome path reads global tables that syndrome_gen_init() must fill first. Forgetting that call leaves them NULL. The init also prints to stdout and never frees its roughly 200 KB alpha^(ij) table (796 x 128 int16 for hqc-256-3).
- Patches are switched on by rewriting src/patch.h, which script.sh overwrites with '#define PATCH' between builds. Building by hand gives whatever the header currently says.
- The randomized FastConvolution variant (Arith2020 Rand_FC) shuffles the order of the sparse positions using libc rand(), which is not a cryptographic RNG, and it keeps the same position-indexed accumulator writes (C256[vbi]).
- The report's 'speed-up %' is a reduction in cycles. 34-46% fewer cycles is about 1.45-1.86x in speed ratio, and the 70-75% figure applies to the multiplication kernel only, not the whole KEM.

## Known shortcomings

- Gain is 33.7-46.3% on i5-4690S and 30.9-43.2% on i5-8400H (not the claimed 35.1-46.3%); GCC 7.4.0 is stated only for the 8400H run. liboqs re-enabled HQC in 0.16.0, so the baseline has moved.
- Not constant-time: fastConvolutionMult indexes memory by secret positions and syndrome_gen2 branches on decoded bits (timing side channels); the Rand_FC variant shuffles with libc rand(). Not thread-safe (global scratch buffers); \~200 KB table never freed. No license, abandoned 2020, Round-2 HQC only (hqc-256-3); liboqs now ships the 2025-08-22 spec. Constant-time follow-up: Robert & Véron, JCE 2022.

## Caveats and trade-offs

The report and code predate HQC's selection for NIST standardization and its later parameter and spec changes, and the project has been abandoned since 2020. The repo has no license. The public patched harness under Fast_Implementation covers only hqc-256-3; the README says the implementation 'moved to ARITH2020', and that folder holds per-table experiments. The report does not state whether the patched code is constant-time; the repo's ARITH2020/TABLE4 also ships a randomized FastConvolution variant. liboqs disabled HQC by default in 0.13.0 (April 2025) over a reported security flaw. It re-enabled HQC by default in 0.16.0 (July 2026) using the updated 20250822-spec implementation. None of this concerns this specific patch.

No LICENSE file present (code can be studied/reimplemented but not safely reused/redistributed); targets HQC Round-2 parameter sets, which predate HQC's later NIST selection and parameter revisions, so exact percentages may not transfer to the current spec

## Maintenance

Abandoned since April 2020 and unlicensed, and it patches a superseded Round-2 HQC code base with non-constant-time kernels. Read it for the technique; do not vendor it. The authors' later constant-time Karatsuba/Toom-Cook multiplication work (Robert & Véron, J. Cryptographic Engineering 2022) is the more relevant follow-up.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The report compares the patch against the HQC Round-2 optimized implementation. For the i5-8400H runs it states gcc 7.4.0. The benchmark code (Fast_Implementation/hqc-256-3/src/main_hqc.c plus script.sh, which runs the code without and then with the patch) is public, and the Makefile gives CFLAGS -O3 -std=c99 -mavx -mavx2, so tier A holds. It holds only narrowly: the headline i5-4690S numbers state no compiler, and the public harness covers only hqc-256-3.
- **Verifier notes:** The numbers are on the page, but the record's '35.1-46.3%' range was misstated: the true minimum on the i5-4690S is 33.7% (encryption, N = 24677), and the i5-8400H results (30.9-43.2%) were left out. The liboqs caveat was out of date (HQC is now re-enabled). The repo describes the code as the 'Arith 27 conference submission 16', but crossref turned up no published ARITH 2020 paper, so none is claimed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/fasthqc/hqc/blob/master/report-23072019.pdf>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/report-23072019.pdf>
  - <https://github.com/fasthqc/hqc>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/Makefile>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/script.sh>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/main_hqc.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE4/Readme.md>
  - <https://github.com/open-quantum-safe/liboqs/releases/tag/0.13.0>
  - <https://github.com/open-quantum-safe/liboqs/releases/tag/0.14.0>
  - <https://github.com/open-quantum-safe/liboqs/releases/tag/0.16.0>
- **Sources the enricher read:**
  - <https://github.com/fasthqc/hqc>
  - <https://github.com/fasthqc/hqc/blob/master/Readme.md>
  - <https://github.com/fasthqc/hqc/blob/master/report-23072019.pdf>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/report-23072019.pdf>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/Makefile>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/script.sh>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/ccount.h>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/main_hqc.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/patch.h>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/patch.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/patch2.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/parameters.h>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/hqc.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/bch.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/vector.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/gf2x_avx2.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Fast_Implementation/hqc-256-3/src/kem.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE1/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE2/Toom3/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE2/Toom3Rec/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE4/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE5/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE6/Readme.md>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE5/Constant_Time_AVX_HQC_gf2x/README>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE6/Constant_Time_AVX_HQC_FC/README>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE6/Constant_Time_AVX_HQC_FC/hqc-128-1/src/gf2x_avx2.c>
  - <https://raw.githubusercontent.com/fasthqc/hqc/master/Arith2020/TABLE6/Constant_Time_AVX_HQC_Rand_FC/hqc-128-1/src/gf2x_avx2.c>
  - <https://api.archives-ouvertes.fr/search/?q=halId_s:hal-03520854&fl=abstract_s,doiId_s,title_s&wt=json>
  - https://api.archives-ouvertes.fr/search/?q=authFullName_t:%22Pascal%20V%C3%A9ron%22%20AND%20(HQC%20OR%20%22sparse%22%20OR%20convolution)
  - <https://github.com/open-quantum-safe/liboqs/releases/tag/0.13.0>
  - <https://github.com/open-quantum-safe/liboqs/releases/tag/0.16.0>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/fasthqc/hqc`) · [data/wave7/enrich/raw/github_com_fasthqc_hqc.json](../../../data/wave7/enrich/raw/github_com_fasthqc_hqc.json) (enrichment confidence 0.75)

</details>
