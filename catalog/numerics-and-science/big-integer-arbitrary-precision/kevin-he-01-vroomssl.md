# VROOM (vectorized RNS modular multiplication, BoringSSL fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Research BoringSSL fork that swaps Montgomery multiplication for AVX-512 IFMA residue-number-system arithmetic to speed up RSA modexp.

| | |
|---|---|
| **Beats** | BoringSSL BN_mod_mul_montgomery / BN modular exponentiation and RSA (same binary, multiplication backend swapped), OpenSSL at commit 7a53925 including its AVX-512 IFMA almost-Montgomery routines ossl_rsaz_amm52x{20,30,40} (separate harness kevin-he-01/vroom-openssl), FLINT 3.2.1 (GMP-based mpn_mod_mul / fmpz_mod_mul), and Arkworks (Rust, modmul only) |
| **Claimed result** | The repository README gives no figures; it says 'the relative speedup of VROOM over each baseline is the paper's claim' and points to the paper (IACR ePrint 2026/393). A WebSearch result summarizing the paper abstract (the ePrint and USENIX pages themselves could not be opened, egress blocked) states that VROOM accelerates RSA-4096 signatures by 4.0x (verify) and 1.3x (sign) over OpenSSL, and BLS signature verification by 3.43x over the assembly-optimized BLST library (the BLS result is not covered by this repository). These figures are not verified from an opened page. |
| **Workload** | Modular multiplication versus modulus size, modular exponentiation (public e = 65537, secret exponent, RSA-CRT) and RSA sign/verify latency using AVX-512 IFMA with a residue number system, single core pinned with taskset, versus BoringSSL Montgomery, OpenSSL and FLINT. |
| **Metric** | latency |
| **Hardware** | AWS c7i.metal-24xl, Intel Xeon Platinum 8488C (Sapphire Rapids, AVX-512 IFMA required), Amazon Linux 2023; README says relative speedups also reproduce on c7i-flex.large |
| **Compiler and flags** | Clang 21.1.8 (official LLVM prebuilt, installed by install_deps.sh); configure.sh runs 'cmake -GNinja -B build -DCMAKE_BUILD_TYPE=Release'; CMakeLists.txt adds -O3 to the Release flags and -mavx512f -mavx512ifma for the RNS path; FLINT 3.2.1; runs pinned with 'taskset -c 0 ./build/bssl_bench' |
| **Adoption** | 8 stars, 1 fork, 11 commits; artifact repository for the USENIX Security 2026 paper by Langowski, He and Devadas (MIT) |
| **Last commit** | 2026-06-18 |
| **Links** | [repository](https://github.com/kevin-he-01/vroomssl) · [benchmark](https://github.com/kevin-he-01/vroomssl) |

## Verdict

The repository prints no figures; it says the relative speedup over each baseline is the paper's claim and provides ./reproduce.sh, which runs bssl_bench pinned with taskset to core 0 (Clang 21.1.8, CMake Release -O3 plus -mavx512f -mavx512ifma, Xeon Platinum 8488C) for VROOM, BoringSSL BN_mod_mul_montgomery and FLINT 3.2.1, with OpenSSL and Arkworks in separate harnesses. Search summaries of the paper abstract (eprint 2026/393, not opened because the host is blocked) report 4.0x faster RSA-4096 verification over OpenSSL and, from the verifier's earlier search, 1.3x faster signing; two summaries disagree on the BLS figure (3.43x versus 4.05x), and BLS is not in this repository.

## Use it when

- Measuring or prototyping faster RSA verification and modular exponentiation latency on a single core of a CPU with AVX-512 IFMA (tested on Xeon Platinum 8488C, Sapphire Rapids, AWS c7i).
- Moduli of exactly 1024, 1536, 2048, 3072 or 4096 bits (the sizes instantiated in BN_MONT_CTX_set_use_rns), for example RSA-4096 verify or RSA-CRT with 2048-bit primes.
- Single-operation latency where you cannot batch independent multiplications: VROOM vectorizes inside one modular multiply rather than across eight.
- Reproducing the paper's Sections 6.1-6.3 tables with ./reproduce.sh against BoringSSL, FLINT 3.2.1 and the separate OpenSSL and Arkworks harnesses.

## Skip it when

- Production or any security-sensitive use: the README says it is not production-ready, was tested only on random inputs to select functions, and may contain memory errors and security bugs; commit 616817a (2026-05-22) fixed buffer over-reads in rns/vector/changebase.hpp and conversion.hpp.
- CPUs without AVX-512 IFMA: the Release build adds -mavx512f -mavx512ifma to all C and C++ flags, so treat the whole libcrypto build as AVX-512-only.
- Other modulus sizes: BN_MONT_CTX_set_use_rns prints a warning and leaves the ordinary Montgomery path in place for any bit length other than the five instantiated sizes.
- General big-integer arithmetic (arbitrary-size add, multiply, division, string conversion): it is a modular-multiplication backend for crypto, not a GMP replacement.
- Builds that cannot pull in GMP and FLINT: CMakeLists.txt stops with FATAL_ERROR without FLINT and includes GMP/FLINT headers into bcm.cc ('TODO: REMOVE GMP DEPENDENCY'), and install_deps.sh says 'The RNS code links GMP for radix&lt;-&gt;RNS helpers', although the README says the VROOM code calls only BoringSSL BN_\* routines.

## How it is fast

Operands are held in two RNS bases of 52-bit residues and multiplied lane-wise with the AVX-512 IFMA instructions vpmadd52lo/hi (_mm512_madd52lo/hi_epu64), so the per-residue products are independent and fill 8-lane vectors. Modular reduction is an RNS Montgomery reduction: a per-residue Montgomery step followed by two base-extension ('CRNS') matrix products that move the value between the bases, described in rns/vector/batching_vs_no_batching_call_graph.md. Modulus size is a compile-time template parameter, so loops over limbs are fully unrolled, and exponentiation uses fixed-window tables with constant-time selection.

## Compared with alternatives

Pick VROOM over the truncated batch AVX-512 Montgomery code (lea-gl) when you need one RSA-size modexp faster rather than eight independent ones at once, and over FLINT or GMP-based code when the modulus is one of the five RSA sizes and the CPU has AVX-512 IFMA; for BLS12-381 or non-RSA moduli the authors' separate standalone repository (SimonLangowski/VROOM, MIT) is the better starting point, and CGBN only wins if a GPU is available.

## Integration

| | |
|---|---|
| **Form** | static lib (BoringSSL fork; RNS core is header-only C++ templates under rns/) |
| **Dependencies** | BoringSSL build tooling (CMake, Ninja); GMP and FLINT 3.x found at configure time; Google Benchmark for bssl_bench and the OpenSSL harness; Rust 1.86 only for the Arkworks baseline |
| **Minimum toolchain** | C++17 and C11 per CMakeLists.txt; tested only with Clang 21.1.8 (official LLVM prebuilt) |
| **Platforms** | x86-64 with AVX-512F and AVX-512 IFMA; tested on Linux (Amazon Linux 2023) on Xeon Platinum 8488C, README says c7i-flex.large also reproduces relative speedups |
| **Thread safety** | not documented for the RNS code; RSA_set_use_rns(int) takes no RSA argument and acts as a process-wide switch, and the BigInt wrapper keeps a thread_local BN_CTX |
| **Drop-in for the baseline** | partial — same BoringSSL BN/RSA API with RNS enabled per BN_MONT_CTX or globally for RSA, but only for 1024/1536/2048/3072/4096-bit moduli and only inside this fork; not a drop-in for OpenSSL, GMP or FLINT |

## Gotchas

- The BigInt wrapper used to build RNS contexts (rns/precompute/gmp_wrapper.hpp) includes the plain ossl_wrapper.hpp; the constant-time ossl_wrapper_consttime.hpp include is commented out, so precomputation on secret moduli (the p and q contexts in RSA-CRT) may not be constant-time. Not checked further this session.
- Ring&lt;modulus_bits&gt; fixes the size at compile time; a modulus longer than the template size makes the constructor print to stderr and abort().
- AVXVector::load reads whole 8-lane vectors, which caused the out-of-bounds reads fixed in 616817a by copying into padded buffers; other call sites that load unpadded data could have the same problem.
- CMakeLists.txt carries a TODO about large stack frames in the RNS Montgomery code and has the -Wframe-larger-than check commented out.

## Known shortcomings

- Security: README calls it a research prototype that may have memory and security bugs, and commit 616817a 'Fix buffer overflow in several files' confirms such bugs; not for production RSA. Repo has no numbers; the 4.0x verify / 1.3x sign for RSA-4096 vs OpenSSL is from the paper (ePrint 2026/393), seen only via search summary.
- README says no GMP but install_deps.sh links GMP for radix&lt;-&gt;RNS helpers; CMake fails without FLINT; Release adds -mavx512f -mavx512ifma to all flags; RNS only for exactly 1024/1536/2048/3072/4096-bit moduli; precompute BigInt uses a non-constant-time ossl_wrapper (consttime include commented out), a possible side channel on RSA-CRT p,q (unconfirmed).

## Caveats and trade-offs

The README warns that this is a research prototype, 'not a production-ready library', tested only on random inputs to select functions, and that it may contain memory leaks, memory errors and other (security) bugs; commit 616817a (2026-05-22) is titled 'Fix buffer overflow in several files'. No speedup figures appear in the repository; the headline numbers come from the paper abstract and were only seen in a search summary here. The VROOM code itself uses only BoringSSL BN_\* routines (no GMP/FLINT). OpenSSL and Arkworks columns come from separate harnesses (baselines/openssl submodule, baselines/arkworks). FLINT is the GMP-based baseline, not GMP itself. Requires AVX-512 IFMA (Sapphire Rapids class CPU). Fork of BoringSSL commit 3fb010b, licensed Apache-2.0. The GPU and elliptic-curve/pairing results of the paper live in other repositories not covered here.

Needs a CPU with AVX-512 IFMA (the README says the RNS code path will not run without avx512ifma); research prototype built on BoringSSL BN_\* routines, runtime switch via BN_MONT_CTX_set_use_rns / RSA_set_use_rns; the README warns it is not production-ready and was only tested on random inputs for selected functions.

## Maintenance

Active research artifact (last commit 2026-06-18, 11 commits, 8 stars), Apache-2.0 like upstream BoringSSL; usable for benchmarking and study, but the authors themselves say not to use it in production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Public artifact harness (bench/ built into ./build/bssl_bench, run via reproduce.sh; OpenSSL baseline harness in kevin-he-01/vroom-openssl) benchmarks VROOM against BoringSSL BN_mod_mul_montgomery, FLINT 3.2.1 and OpenSSL, with compiler (Clang 21.1.8), flags (CMake Release -O3 plus -mavx512f -mavx512ifma in CMakeLists.txt) and CPU (Xeon Platinum 8488C) all stated; the results are in a peer-reviewed USENIX Security 2026 paper. The repo itself prints no numbers; the headline figures were seen only in a WebSearch summary of the paper abstract because eprint.iacr.org and usenix.org are blocked here.
- **Verifier notes:** Harness, flags and CPU check out; eprint.iacr.org, usenix.org, kevin-he-01.github.io and api.semanticscholar.org were all egress-blocked, so the paper's tables were not read and the 4.0x/1.3x RSA-4096 figures rest on a WebSearch abstract summary; re-check from the PDF on an unrestricted machine. Record the research-prototype security warning and the buffer-overflow fix as shortcomings.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/README.md>
  - <https://github.com/kevin-he-01/vroomssl>
  - <https://github.com/kevin-he-01/vroomssl/commits/main>
  - <https://github.com/kevin-he-01/vroomssl/commit/5a1dc6c>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/configure.sh>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/kevin-he-01/vroom-openssl/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/kevin-he-01/vroomssl>
  - <https://github.com/kevin-he-01/vroomssl/commits/main>
  - <https://github.com/kevin-he-01/vroomssl/commit/616817a>
  - <https://github.com/kevin-he-01/vroomssl/tree/main/rns>
  - <https://github.com/kevin-he-01/vroomssl/tree/main/rns/vector>
  - <https://github.com/kevin-he-01/vroomssl/tree/main/rns/reduction>
  - <https://github.com/kevin-he-01/vroomssl/tree/main/rns/crypto>
  - <https://github.com/kevin-he-01/vroomssl/tree/main/rns/precompute>
  - <https://github.com/kevin-he-01/vroomssl/tree/main/crypto/fipsmodule/bn>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/README.md>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/configure.sh>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/install_deps.sh>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/reproduce.sh>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/rns/vector/batching_vs_no_batching_call_graph.md>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/rns/vector/avx512ifma.hpp>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/rns/crypto/ring.hpp>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/rns/crypto/exponentiation.hpp>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/rns/precompute/gmp_wrapper.hpp>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/rns/precompute/wrappers/ossl_wrapper.hpp>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/rns/precompute/wrappers/ossl_wrapper_consttime.hpp>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/include/openssl/rsa.h>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/include/openssl/bn.h>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/crypto/fipsmodule/bn/montgomery.cc.inc>
  - <https://raw.githubusercontent.com/kevin-he-01/vroomssl/HEAD/crypto/fipsmodule/bn/internal.hpp>
  - <https://github.com/commonwarexyz/monorepo/issues/4767>
  - <https://github.com/SimonLangowski/VROOM>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kevin-he-01/vroomssl`) · [data/wave8/enrich/raw/github_com_kevin_he_01_vroomssl.json](../../../data/wave8/enrich/raw/github_com_kevin_he_01_vroomssl.json) (enrichment confidence 0.7)

</details>
