# ChaChaCha

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [TLS](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Experimental AVX-512 ChaCha20-Poly1305 assembly for x86-64 Linux; 19-48% fewer cycles/byte than OpenSSL's assembly on AMD Zen 5.

| | |
|---|---|
| **Beats** | OpenSSL ChaCha20/ChaCha20-Poly1305 (assembly and EVP), BoringSSL stitched AVX2 ChaCha20-Poly1305 |
| **Claimed result** | Page percentages are cycles/byte reductions, (theirs - ours)/theirs, not throughput ratios. Zen 5 AEAD real-world bands vs OpenSSL (vendored asm, called without EVP): seal +19.3% to +45.4% (WireGuard 1360-1420B +45.4%, i.e. 1.83x throughput derived from page data; 16384B +22.4%); open +20.9% to +47.6%. Zen 5 vs BoringSSL stitched AVX2: seal +49.4% to +57.1%, open +53.5% to +57.4%. Zen 5 vs Intel IPsec-MB (best of its two entry points): seal +3.8% to +16.8%, open +4.7% to +19.9%. Zen 4 AEAD vs OpenSSL: seal +8.9% to +33.0%, open +9.2% to +32.5%; vs BoringSSL +30.8% to +37.5%; vs Intel -1.3% to +8.9% (loses at Jumbo 8900-9000B). Raw AVX-512 ChaCha20: +25.0% to +33.1% vs the best other implementation (Intel) on Zen 5 for bands of 4KB and above (vs OpenSSL 16x about +29% to +35%, derived from page data); Zen 4 +5.0% to +7.6% vs best other (vs OpenSSL about +8% to +15%, derived from page data); ours loses to Intel at QUIC/WireGuard sizes (-7.5%/-3.9% Zen 5, -26.0%/-16.5% Zen 4). Raw AVX2 ChaCha20 vs best other (OpenSSL/BoringSSL): +10.0% to +10.8% on Zen 5 and +5.4% to +8.1% on Zen 4 for bands of 4KB and above; about 0% at 1200-1420B. |
| **Workload** | ChaCha20 and ChaCha20-Poly1305 AEAD seal/open at protocol-realistic sizes (QUIC 1200-1350B, WireGuard 1360-1420B, 4KB TLS record, 9000B jumbo, 16384B TLS 1.3 max record, 32-64KiB bulk) measured in core cycles/byte via perf_event_open, pinned to one core, best-of-7 internal reps x best-of-3 runs, on AMD EPYC 9655 (Zen 5) and AMD EPYC 4244P (Zen 4) |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9655 (Zen 5, Turin) and AMD EPYC 4244P (Zen 4) |
| **Compiler and flags** | gcc (version not stated; README requires Linux x86-64 with gcc and make), Makefile CFLAGS ?= -O2 -Wall for C harness/glue, ASFLAGS=-Wa,--noexecstack; kernels are perlasm-generated assembly assembled by gcc plus NASM (-f elf64) for poly1305_ifma.asm and the Intel vendor kernels |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/soda4fries/ChaChaCha) · [benchmark](https://github.com/soda4fries/ChaChaCha/blob/master/result.md) |

## Verdict

The author measured core cycles per byte (perf_event_open, one pinned core, best of 7 repetitions x 3 runs, 13-byte AAD, hot-cache loop over one buffer with a fixed key, round-trip check before timing) on AMD EPYC 9655 (Zen 5) and EPYC 4244P (Zen 4), with gcc -O2 C glue around hand-written assembly. Baselines were OpenSSL's vendored chacha-x86_64/poly1305-x86_64 assembly (commit bee02b7d) called directly, BoringSSL's stitched AVX2 AEAD and Intel IPsec-MB 3.0.0-dev. On Zen 5, AEAD seal used 19-45% fewer cycles per byte than OpenSSL's assembly across 1.2 KB-64 KiB bands and 49-57% fewer than BoringSSL; on Zen 4 it used 9-33% fewer than OpenSSL and roughly tied Intel IPsec-MB (-1.3% to +8.9%).

## Use it when

- Linux x86-64 servers on AMD Zen 5 or Zen 4 (AVX-512F/BW/VL, AVX-512 IFMA and BMI2 present) where ChaCha20-Poly1305 record encryption is a measurable share of CPU time.
- WireGuard, QUIC and TLS-record-sized payloads (about 1.2-1.5 KB) on Zen 5: seal takes 0.94 c/B against 1.72 for OpenSSL's assembly and 2.00 for BoringSSL's stitched AVX2 at 1360-1420 B.
- Bulk ChaCha20 keystream of 4 KB or more with AVX-512: 0.36 c/B against 0.54 for OpenSSL's 16x kernel at 32-64 KiB on Zen 5.
- A custom data plane (userspace VPN, own QUIC stack) that can call a raw C AEAD function directly instead of going through EVP.
- As reference code for port-level stitching, dual-state ILP and single-dispatch key generation, to port into a maintained crypto library.

## Skip it when

- CPUs without AVX-512 IFMA (every AVX2-only machine, Skylake-SP-family Xeons): the AEAD then runs OpenSSL-derived ChaCha plus a portable C radix-2^26 Poly1305, a path result.md does not benchmark and that has no assembly Poly1305.
- Messages of 256 bytes or less: Zen 5 seal is 20-24% slower than OpenSSL's assembly at 64-256 B (Zen 4: 9.5-23% slower), and fixed per-call cost is 762 cycles against 650.
- Raw AVX-512 ChaCha20 at 1200-1420 B: it loses to Intel IPsec-MB by 4-8% on Zen 5 and 17-26% on Zen 4; on Zen 4 the AEAD only ties Intel at 4-9 KB (-1.3% at jumbo frames).
- Production or compliance-bound systems: single author, 3 commits, no releases, no audit, fuzzing or FIPS story, hand-written crypto assembly; Intel CPUs, AVX-512 frequency effects and SMT neighbours are untested.
- Non-Linux or non-x86-64 targets (macOS, Windows, ARM), or protocols needing XChaCha20 or extra_in: the build emits ELF only, the nonce is 12 bytes, and seal_scatter rejects extra_in.

## How it is fast

It uses function stitching: raw ChaCha20 runs one extra block in scalar GPRs alongside 8 (AVX2, 9x) or 16 (AVX-512, 17x) vector blocks, and ChaCha20_32x interleaves two independent 16-block ZMM states to raise instruction-level parallelism from 4 to 8, reloading the initial state from broadcast memory operands so no registers are spilled. The AEAD is a BoringSSL/Cloudflare-style stitched loop ported to AVX-512: ChaCha on vector ports encrypts chunk i while two scalar mulx Poly1305 chains on the integer ports authenticate two contiguous 512-byte halves of chunk i-1, joined as A\*r^32+B, with Intel IPsec-MB's staggered issue order. For 1025-2048-byte packets, 'key-mode' kernels (25x/33x) compute the counter-0 Poly1305 key block in scalar registers in the same call as the payload, which removes a second kernel launch the README puts at about 400 cycles. Tails larger than 768 bytes use an AVX-512 IFMA52 Poly1305 and a modular power ladder to merge the split accumulators.

## Compared with alternatives

Pick ChaChaCha only when ChaCha20-Poly1305 record encryption itself is the bottleneck on AVX-512 IFMA x86 servers and you can call a raw AEAD function, as in a custom WireGuard or QUIC data plane. For a complete, maintained TLS stack pick AWS-LC or wolfSSL; for AES-GCM traffic, picotls's fusion engine is the equivalent stitched-AEAD choice.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none at runtime; the build needs GNU make, gcc, Perl (perlasm), NASM and GNU ld; `make test` also links OpenSSL libcrypto to cross-check results; the benchmark harness dlopens Intel's libIPSec_MB |
| **Minimum toolchain** | gcc with GNU as 2.25+ (the inherited perlasm emits the AVX-512 paths only when it detects GNU as &gt;= 2.25); exact gcc and NASM versions not documented |
| **Platforms** | Linux x86-64 (ELF) only. The fast AEAD path needs AVX2, BMI2, AVX-512F/BW/VL and AVX-512 IFMA; benchmarked only on AMD Zen 4 and Zen 5; other x86-64 CPUs get the fallback |
| **Thread safety** | Not documented. Seal/open keep no shared state beyond CPU-feature globals set by a load-time constructor; chacha20_poly1305_set_avx512_enabled() rewrites those globals without synchronisation, so do not call it while other threads encrypt. CHACHA20_CTX is per-caller state. |
| **Drop-in for the baseline** | partial — BoringSSL-style C functions (CRYPTO_chacha_20, chacha20_poly1305_seal/open, seal_scatter/open_gather), not an OpenSSL EVP cipher, provider or BoringSSL EVP_AEAD; call sites must change |

## Gotchas

- Symbol clashes: the library exports CRYPTO_chacha_20 (a BoringSSL public name) and ChaCha20_ctr32, and defines OPENSSL_ia32cap_P unless built with -DCHACHA20_USE_OPENSSL_CAP. Static linking next to OpenSSL or BoringSSL can therefore fail; the repo's own Makefile renames the vendored OpenSSL symbols with -D flags for this reason.
- The README example links build/chacha20poly1305.a, but the Makefile builds only build/aead512.o and build/chacha20poly1305.o (no archive target). The Makefile also warns that aead_mac_partial.o must stay before aead512_core.o in link order to avoid a Zen 5 MAC-drain alignment regression.
- On the AVX-512 path, open decrypts into the output buffer before it compares the tag, and zeroes the buffer on failure. Check the return value before using the output.
- Batch-boundary lengths (1024, 2048, 4096 B) flatter the kernels; the author says the 2048 B margin is about double the margin 200 B to either side. Benchmark at your real packet sizes.

## Known shortcomings

- Slower than OpenSSL assembly on small messages (64-256 B). Kernels only (not a TLS stack), x86-64 AVX2/AVX-512; a one-person project with 1 star.
- The fast AEAD path needs AVX2, BMI2, AVX-512F/BW/VL and IFMA; every other CPU (all AVX2-only machines, Skylake-SP Xeons) falls back to OpenSSL-derived ChaCha plus portable Poly1305, which is not benchmarked. Loses to OpenSSL at 64-256 B (20-24% slower seal on Zen 5, 9.5-23% on Zen 4) and to Intel IPsec-MB at 1200-1420 B. BoringSSL-style API, 12-byte nonce only, no XChaCha20. Exports CRYPTO_chacha_20, ChaCha20_ctr32 and OPENSSL_ia32cap_P, which can clash when statically linked beside OpenSSL/BoringSSL. README example links an archive the Makefile never builds; link order affects Zen 5 speed; Linux ELF only. The AVX-512 open path decrypts into the output before the tag check (zeroed on failure). One author, 3 commits, 1 star, no audit or fuzzing; tested only on AMD Zen 4/5; hot-cache single-buffer benchmark at batch-friendly lengths.

## Caveats and trade-offs

Single-author project with 1 GitHub star and no independent reproduction. Only two AMD CPUs tested (Zen 5 EPYC 9655, Zen 4 EPYC 4244P); no Intel CPU results. The AEAD 'OpenSSL' column is OpenSSL's vendored assembly called directly (no stitched AEAD in OpenSSL); OpenSSL EVP has higher fixed per-call cost (1419/1773 cycles vs 650/550 for asm). Ours is slower than OpenSSL asm on small messages (Zen 5 seal 64-256B: -19.6% to -24.0%; Zen 4 seal 64-256B: -9.5% to -23.4%) and roughly equal at exactly 1024B. Page flags power-of-two lengths (1024/2048/4096...) as flattering batch boundaries and uses realistic protocol-size bands for headline tables. Page GB/s figures assume a nominal 3.0 GHz; c/B is the real metric. Methodology is careful: perf_event_open core cycles, pinned core, alternating order, best of 7 x best of 3, round-trip correctness check before timing.

x86-64 AVX2/AVX-512 only (no portable/scalar-only fallback path shown as competitive); OpenSSL is measured both as raw vendored assembly (openssl-asm) and via EVP (openssl-evp) which carries provider dispatch overhead, so the EVP-vs-EVP comparison would show an even larger margin than the asm-vs-asm numbers quoted; BoringSSL comparison for AVX-512 is AEAD-only since BoringSSL has no AVX-512 ChaCha20 raw kernel; single author, very new/unreviewed project

## Maintenance

Active but brand new: 3 commits between 2026-08-14 and 2026-09-21 by one author, 1 star, no releases or issues. Apache-2.0 with retained OpenSSL, BoringSSL/Cloudflare (ISC) and Intel (BSD-3) code, and small enough to vendor, but the crypto assembly is unaudited.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** result.md compares against the vendored OpenSSL chacha-x86_64/poly1305-x86_64 assembly (pinned commit bee02b7d) and OpenSSL EVP, BoringSSL stitched AVX2 AEAD and Intel IPsec-MB, with raw per-run CSVs in results/raw; benchmark code is public (vendor/bench_aead_matrix.c, vendor/bench_raw_bands.c, vendor/bench_raw_chacha.c, report generator tools/report/result_report.py), the compiler (gcc) and flags (Makefile CFLAGS ?= -O2 -Wall, ASFLAGS -Wa,--noexecstack) are stated, and so are the CPU models (AMD EPYC 9655 Zen 5, AMD EPYC 4244P Zen 4). The gcc version is not stated, but the timed kernels are hand-written perlasm/NASM assembly.
- **Verifier notes:** Record's benchmark_url used /blob/main/ which returns 404; default branch is master, fixed. Record's 'seal +19.3% to +47.6%' merged seal and open ranges and its raw AVX-512 '+25-33% vs OpenSSL' is the README's figure, which on result.md is really vs the best other implementation (Intel); vs OpenSSL the margin is larger. License Apache-2.0, 1 star, last commit 2026-09-21, not fork, not archived: metadata confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/soda4fries/ChaChaCha>
  - <https://github.com/soda4fries/ChaChaCha/blob/main/result.md>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/result.md>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/README.md>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/Makefile>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/vendor/README.md>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/tools/report/result_report.py>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/results/raw/zen5_aead1.csv>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/results/raw/zen5_bands1.csv>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/results/raw/zen5_direct1.csv>
- **Sources the enricher read:**
  - <https://github.com/soda4fries/ChaChaCha>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/README.md>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/result.md>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/chacha20poly1305.h>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/chacha20poly1305.c>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/Makefile>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/NOTICE>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/vendor/README.md>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/chacha_kernels.pl>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/aead512.pl>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/tools/report/result_report.py>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/tools/test/test_api.c>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/vendor/bench_aead_matrix.c>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/vendor/vendor_aead.c>
  - <https://github.com/soda4fries/ChaChaCha/blob/master/vendor/bench_perf.h>
  - <https://github.com/soda4fries/ChaChaCha/commits/master>
  - <https://github.com/soda4fries/ChaChaCha/issues>
  - <https://hn.algolia.com/api/v1/search?query=soda4fries>
  - <https://hn.algolia.com/api/v1/search?query=ChaChaCha>
  - <https://hn.algolia.com/api/v1/search_by_date?tags=story&query=chacha20>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/soda4fries/chachacha`) · [data/wave5/enrich/raw/github_com_soda4fries_chachacha.json](../../../data/wave5/enrich/raw/github_com_soda4fries_chachacha.json) (enrichment confidence 0.8)

</details>
