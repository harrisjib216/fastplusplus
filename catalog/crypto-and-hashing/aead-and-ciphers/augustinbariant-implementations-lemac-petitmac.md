# LeMac

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [AEAD and ciphers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `CC0-1.0 (reference implementation) / MIT (bundled boppreh/aes component)` · 🟡 stale

> Designers' AES-NI C code for LeMac, a nonce-based AES-round MAC about 4-7x faster than AES-128-GCM's GHASH on long messages.

| | |
|---|---|
| **Beats** | AES-GCM in associated-data-only mode (GHASH/GMAC-style authentication), using Romain Dolbeau's public-domain AES-NI/PCLMUL implementation (benchmark/GCM/aesenc-int.c, from SUPERCOP), not OpenSSL |
| **Claimed result** | LeMac 0.068 cycles/byte vs 0.286 cycles/byte for GCM (AD only) on 256 kB messages on Intel Ice Lake Xeon Gold 5320 (\~4.2x, derived from page data). Other CPUs: Zen3 EPYC 7513 0.072 vs 0.451 (\~6.3x, derived); Skylake Xeon Gold 6130 0.126 vs 0.370 (\~2.9x, derived); Haswell Xeon E5-2630 v3 0.131 vs 0.605 (\~4.6x, derived). The abstract's '60% throughput improvement' is measured against the Jean-Nikolic rate-2 MAC (0.113 cycles/byte on Ice Lake), the fastest prior MAC in the authors' benchmarks, not against GCM. |
| **Workload** | MAC throughput in cycles/byte on 1 kB, 16 kB and 256 kB messages. Each MAC runs 1000 times over the same in-cache random message, and the most frequent rdpmc cycle count is reported. The AEADs (GCM, Rocca, Rocca-S, AEGIS, Tiaoxin) are run in associated-data-only mode. |
| **Metric** | throughput |
| **Hardware** | Intel Ice Lake Xeon Gold 5320 (headline); also Intel Haswell Xeon E5-2630 v3, Intel Skylake Xeon Gold 6130, AMD Zen1 EPYC 7301, AMD Zen3 EPYC 7513 |
| **Compiler and flags** | gcc 12.2.0 (paper Section 7.2); -Wall -Wextra -O3 -march=native (benchmark/LeMac/Makefile, shared by benchmark/GCM) |
| **Adoption** | 2 stars (reference implementation repo); algorithm published IACR Trans. Symmetric Cryptol. (ToSC) 2024/2 |
| **Last commit** | 2025-07-10 |
| **Links** | [repository](https://github.com/AugustinBariant/Implementations_LeMac_PetitMac) · [benchmark](https://tosc.iacr.org/index.php/ToSC/article/download/11619/11111) |

## Verdict

Peer-reviewed ToSC 2024(2) Table 4: gcc 12.2.0, -O3 -march=native, in-cache message, rdpmc, most frequent of 1000 runs. It measured LeMac-0 at 0.068 c/B against 0.286 for Romain Dolbeau's SUPERCOP AES-128-GCM (AD only) on a Xeon Gold 5320 at 256 kB, about 4.2x. The 2025 corrigendum re-measured the corrected LeMac at 0.079 vs 0.321 (Ice Lake), 0.069 vs 0.466 (Zen 3), 0.128 vs 0.637 (Haswell) and 0.126 vs 0.414 (Skylake). The GCM baseline is 128-bit PCLMULQDQ with 8-block aggregation, not VPCLMULQDQ or OpenSSL. Its timed call includes key expansion and H-power setup, while LeMac's key setup sits outside the timed loop, which mostly affects the 1 kB column.

## Use it when

- Authenticating large in-memory buffers (16 KB and up) on x86-64 servers with AES-NI, where you control both ends. In the 2025 corrigendum's rerun at 256 kB, corrected LeMac ran at 0.079 c/B against 0.321 for AES-128-GCM in AD-only mode on a Xeon Gold 5320 (about 4.1x), and 0.069 against 0.466 on a Zen 3 EPYC 7513 (about 6.8x).
- As the MAC half of an encrypt-then-MAC design with a fast stream cipher, when GHASH or GMAC is the bottleneck. At 256 kB it also beats single-lane AEGIS-128L used for AD only (0.079 vs 0.195 c/B on Ice Lake) and Tiaoxin (0.123).
- Keyed integrity checks of bulk data where unique 128-bit nonces are available, for the claimed 128-bit security. With repeated or fixed nonces, the paper claims security up to about 2^64 data.
- Benchmarking AES-round MACs. The benchmark/ folder builds and times LeMac, LeMac-0, PetitMac, Jean-Nikolic, GCM, Rocca, Rocca-S, AEGIS-128/128L/128X2, Tiaoxin, HiAE, EliMAC and smac1x8 with rdpmc under one harness.

## Skip it when

- Short messages. At 1 kB, LeMac costs 0.285 c/B on Ice Lake, 3.6x its 256 kB rate. On Haswell at 1 kB it roughly ties Jean-Nikolic (0.460 vs 0.451) and Tiaoxin (0.494). zig-lemac's Zen 4 table has AEGIS-128L-MAC ahead at 256 B (40.4 vs 32.2 Gb/s).
- Anything that needs encryption, an AEAD, or a standardized algorithm for TLS, IPsec or QUIC. LeMac is only a MAC, and this session found no standard or RFC for it.
- Non-x86 targets or CPUs without AES-NI. The code uses only x86 intrinsics, with no fallback or runtime CPU check. PetitMac is the designers' pick for small cores (18.3 c/B on a Cortex-M4, using separate T-table code that is not in this repo). pauldreik/lemac supports arm64.
- CPUs with VAES or AVX-512, if you want the most throughput. At 64 KiB on Zen 4, zig-lemac measured single-lane LeMac at 416.6 Gb/s, AEGIS-128X4-MAC at 439.7 and the 4-lane LeMac-X4 at 764.1. The parallel variants are only an unmerged PR here (#3, open since 2025-03).
- Shipping this code as a library. The API is one-shot only, with no streaming and no verify or constant-time tag compare, and two correctness issues have gone unanswered (see gotchas).

## How it is fast

LeMac's universal hash keeps a 9 x 128-bit state. Each 64-byte chunk updates it with 8 independent AESENC instructions, one per wire, with the message words used as AESENC round keys, plus only 4 128-bit XORs. That is 2 AES rounds per 16-byte block ('rate 2'). On Ice Lake and Zen, AESENC and XOR compete for ports 0/1, so the design caps XORs at half the AESENC count and avoids long dependency chains. The rate-2 floor there is 0.0625 c/B, and candidates were compiled and benchmarked automatically during the MILP security search to find one that nears it. GCM's GHASH instead spends carry-less multiplications and reductions on every 16-byte block.

## Compared with alternatives

Pick LeMac over libaegis, Rocca, Tiaoxin and AEZ when you need only authentication of long messages on AES-NI x86 and can pair it with your own cipher. At 256 kB it is 1.5-2.5x faster than their single-lane AD-only modes on Ice Lake. Pick libaegis, HiAE or intel-ipsec-mb when you need a complete AEAD, short-message speed, ARM support or a maintained library, and for a production LeMac prefer the maintained ports (jedisct1/zig-lemac, pauldreik/lemac for C++20) over this reference repo.

## Integration

| | |
|---|---|
| **Form** | source-drop (single-file lemac.c or petitmac.c; the top-level Makefile builds lemac.so and petitmac.so only for the Python test harness) |
| **Dependencies** | none beyond libc and &lt;immintrin.h&gt;. The Python reference uses a bundled pure-Python AES (aes.py from boppreh/aes, MIT). The benchmarks need Linux, make, perf and optionally sudo. |
| **Minimum toolchain** | GCC or Clang with AES-NI enabled (the Makefiles use -O3 -march=native). The code XORs __m128i values with ^ as a GNU vector extension, so MSVC is not supported as written. The paper used gcc 12.2.0. |
| **Platforms** | x86-64 with AES-NI only. There is no ARM path, portable fallback or runtime dispatch. The benchmarks use getrandom, perf and Linux sysfs knobs. |
| **Thread safety** | Not documented. From the code, the context is read-only after lemac_init and lemac_MAC keeps its state on the stack, so concurrent MACs sharing one initialised context look safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- The famous 0.068 c/B was measured on LeMac-0, the version with the message-schedule error. The 2025 corrigendum's rerun of the corrected LeMac gives 0.079 c/B on Ice Lake and 0.069 on Zen 3, so the gain over Jean-Nikolic on Ice Lake is about 39%, not 60%. The designers no longer claim 128-bit security for LeMac-0 (proven bound 25 active S-boxes, only 20 without the linear-incompatibility constraints), yet benchmark/LeMac-0\* is still in the tree. Use the root lemac.c.
- lemac_AU and lemac_MAC cast uint8_t pointers for the message, key, nonce and tag to __m128i\* and dereference them. That is undefined behaviour for unaligned buffers and can fault if the compiler emits aligned loads. Issue #5 (2026-08-20) is unanswered, so pass 16-byte-aligned buffers. The code also assumes a little-endian host and whole-byte message lengths.
- Padding appends the byte 0x01 then zeros, while the paper writes M||10\*. Issue #2 (2025-03) asking which is right is unanswered. Check test vectors before interoperating with the Zig or C++ ports.
- lemac.c and petitmac.c both define global, non-static AES, AES_KS and AES_modified functions, so they cannot be linked into one binary as-is. AES_128_ASSIST is plain C99 `inline`, which can leave an unresolved symbol in unoptimised builds. Verifying a tag means recomputing it and comparing in constant time yourself.

## Known shortcomings

- MAC only, not an AEAD. Baseline is Dolbeau's SUPERCOP AES-NI GHASH (AD-only GCM), not OpenSSL; the '60%' figure is against Jean-Nikolić, not GCM. Research code for a 2024 design with limited cryptanalysis.
- The 0.068 cycles/byte headline is LeMac-0 (the buggy original spec); the ToSC 2025(1) corrigendum re-measured fixed LeMac at 0.079 vs GCM 0.321 (\~4.1x, Ice Lake) and 0.069 vs 0.466 (\~6.8x, Zen 3); gain over Jean-Nikolić is \~39%, not 60%. Baseline GCM is SUPERCOP AES-128 with PCLMUL only (no VPCLMUL/OpenSSL) and times its key/H setup while LeMac's init is excluded. One-shot API, no verify function, x86 AES-NI only; unaligned __m128i casts (#5); padding differs from the paper (#2); duplicate global symbols between lemac.c and petitmac.c. Loses to AEGIS-128L-MAC at 256 B. Better-maintained ports: jedisct1/zig-lemac, pauldreik/lemac (C++20, arm64).

## Caveats and trade-offs

The baseline is a public-domain SUPERCOP AES-GCM (Dolbeau aesenc-int.c) run in AD-only mode, not OpenSSL's GHASH, and LeMac is a MAC only (no encryption). The paper benchmarked LeMac-0, whose specification erratum was later fixed and renamed; the README says performance is unaffected. The repo, with its benchmark code, was first committed on 2024-09-13, after the paper's 2024-06-18 publication, and ships no result files. Code is CC0 plus an MIT-licensed bundled AES from boppreh/aes, with no patent grant under CC0.

LeMac is a MAC/universal-hash primitive, not a complete AEAD; it must be paired with a stream cipher (e.g. AES-CTR) to form a full AES-GCM replacement, so it cannot be dropped in on its own; a sibling construction (LeMac-0) had a message-schedule bug in the original paper, fixed in this repo; CC0-1.0 dedication carries no patent grant

## Maintenance

Stale: the last commit (2025-07-10) merged Frank Denis's extra benchmarks. The repo has 2 stars, two unanswered issues and an open PR from 2025-03. The code is CC0 with the bundled Python AES under MIT, and lemac.c is about 7 KB, so it is easy to vendor. For maintained code, jedisct1/zig-lemac (MIT, pushed 2026-09-25) adds 2- and 4-lane variants, and pauldreik/lemac (C++20, BSL-1.0) covers x86-64 and arm64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The paper's Table 4 (ToSC 2024/2, peer-reviewed) benchmarks LeMac directly against GCM in associated-data-only mode on named CPUs (Xeon Gold 5320 Ice Lake and others) and states gcc 12.2.0. The benchmark code is public in this repo (benchmark/benchmarks script, benchmark/LeMac/bench.c, benchmark/GCM/bench.c), with -O3 -march=native set in benchmark/LeMac/Makefile, which benchmark/GCM uses as well.
- **Verifier notes:** The abstract figures (0.068 c/B on Ice Lake, a 60% improvement) are correct, but the 60% is relative to the Jean-Nikolic MAC; the GCM comparison is in Table 4 of the PDF. All parts carry OSI or CC0 licenses, so usability is copyable rather than mixed. The last commit is 2025-07-10 (stale), and the benchmarks for HiAE, EliMAC and aegis128x2 were added in 2025 with no published results.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `usability`, `caveats`
- **Shortcomings recorded by:** LeMac paper Table 4 (Xeon 5320, GCC 12.2 -O3 -march=native): 0.068 vs GCM AD-only 0.286 cycles/byte (\~4.2x).; ToSC 2025(1) corrigendum: fixed LeMac 0.079 vs GCM 0.321 cycles/byte (Ice Lake); 0.069 vs 0.466 (Zen 3).
- **Pages the verifier opened:**
  - <https://tosc.iacr.org/index.php/ToSC/article/view/11619>
  - <https://tosc.iacr.org/index.php/ToSC/article/download/11619/11111>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/README.md>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/benchmark/benchmarks>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/benchmark/LeMac/Makefile>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/benchmark/GCM/Makefile>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/benchmark/GCM/aesenc-int.c>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/benchmark/GCM/bench.c>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AugustinBariant/Implementations_LeMac_PetitMac/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/README.md>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/LICENSE>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/COPYING>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/Makefile>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/lemac.c>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/petitmac.c>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/lemac_petitmac.py>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/test_vectors.py>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/benchmark/README.md>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/benchmark/benchmarks>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/benchmark/LeMac/Makefile>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/benchmark/LeMac/bench.c>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/benchmark/GCM/bench.c>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/blob/main/benchmark/GCM/aesenc-int.c>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/commits/main>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/issues/2>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/issues/5>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/pull/3>
  - <https://github.com/AugustinBariant/Implementations_LeMac_PetitMac/forks>
  - <https://tosc.iacr.org/index.php/ToSC/article/download/11619/11111>
  - <https://tosc.iacr.org/index.php/ToSC/article/view/12089>
  - <https://tosc.iacr.org/index.php/ToSC/article/download/12089/11929>
  - <https://eprint.iacr.org/search?q=LeMac>
  - <https://api.crossref.org/works?query.bibliographic=LeMac+PetitMac+AES+MAC>
  - <https://api.crossref.org/works/10.46586/tosc.v2024.i2.35-67>
  - <https://github.com/pauldreik/lemac>
  - <https://github.com/jedisct1/zig-lemac>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/augustinbariant/implementations_lemac_petitmac`) · [data/wave7/enrich/raw/github_com_augustinbariant_implementations_lemac_petitmac.json](../../../data/wave7/enrich/raw/github_com_augustinbariant_implementations_lemac_petitmac.json) (enrichment confidence 0.84)

</details>
