# Chorba (table-less CRC32)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🟡 stale

> Table-less software CRC-32 using sparse zero polynomials; about 2x zlib 1.3.1.1's braided CRC on large buffers.

| | |
|---|---|
| **Beats** | zlib (zlib 1.3.1.1 CRC32 'braiding' implementation) |
| **Claimed result** | Abstract: CRC32 throughput increased by 100% (2x) across platforms vs the current state of the art (zlib 1.3.1.1 braiding) for table-less, non-hardware-accelerated CRC. Applying Chorba to hardware-accelerated (PCLMUL/AVX1 folding) implementations gives 5-20% depending on message length. The 2x applies to large messages; below a few MB the Chorba variants fall back to chorba_small and gains shrink. Per-size results appear only in figures. |
| **Workload** | CRC32 (IEEE) checksum of messages from 64KiB to 512MiB, 1000 iterations per size, on three platforms |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 5600 (desktop); AWS EC2 t4g.micro (Graviton2/Neoverse-N1); Raspberry Pi 4. AVX figures also on AMD Ryzen and Intel Skylake, with AVX512 discussed on an Intel Icelake server. |
| **Compiler and flags** | Not stated in the paper. Repo configure/Makefile.in: gcc (version not stated) with CFLAGS=-O3, plus -mno-avx on x86_64 and -DAVX1_PCLMUL=1 / -DAVX2_PCLMUL=1 when the CPU supports them. |
| **Adoption** | 6 stars; algorithm has been adopted by zlib-ng as the WITH_CRC32_CHORBA build option |
| **Last commit** | 2024-12-27 |
| **Links** | [repository](https://github.com/samrussell/chorba) · [benchmark](https://arxiv.org/abs/2412.16398) |

## Verdict

A single-author arXiv v1 preprint timed 1,000 iterations of IEEE CRC-32 over xorshift buffers on an AMD Ryzen 5 5600, an AWS t4g.micro (Graviton2) and a Raspberry Pi 4. Builds used gcc -O3 (version unstated), and the baseline was zlib 1.3.1.1's braided crc32(). Results exist only as seconds-per-TiB plots: the text lists sizes up to 512 MiB, but the plots stop at 256 MiB. They show the best non-destructive variant at roughly 2.2x braiding on Ryzen and about 3x on the two ARM systems at 16 MiB and above, which is consistent with the abstract's '100%'. A separate 5-20% gain is claimed for grafting the method onto AVX1 PCLMUL folding.

## Use it when

- You need a portable C CRC-32 for buffers of about 240 KB or more on 64-bit CPUs where CLMUL/PMULL or CRC32 instructions are unavailable or not allowed. At 16-256 MiB the paper's plots show chorba_118960_nondestructive at roughly 2.2x (Ryzen 5 5600) and 3x (Graviton2, Raspberry Pi 4) the throughput of zlib 1.3.1.1 braiding (plot readings are approximate).
- Cortex-A72-class boards such as the Raspberry Pi 4. The paper calls the non-destructive 118960 variant the best performer there, and its plot shows it at or slightly ahead of zlib's native-CRC32-instruction path for 16 MiB and larger.
- You already link zlib-ng 2.3.2 or later. You get Chorba automatically as the fallback ahead of braiding, with the bug fixes applied, which is better than copying this repo.
- You checksum data you own and can overwrite, as in cksum-style tools. On Ryzen and Graviton2 the destructive variants ran close to, or at, the hardware-accelerated reference speed in the plots.
- You want reference code for porting the zero-polynomial idea to other CRC widths; the paper lists CRC-32-XFER and CRC-64-ISO as future work.

## Skip it when

- Your CPU has CRC32 or carry-less-multiply instructions you can use. On Graviton2, zlib's native-CRC32 path plotted at \~55-75 s/TiB against \~150 for the best non-destructive Chorba, and the Chorba+PCLMUL tweak adds only 5-20%. The abstract's 'on par with hardware' claim holds in the plots only for some variants and CPUs.
- Your messages are small. Below 238,432 bytes everything falls back to chorba_small, which is only \~1.15x braiding at 64 KiB on the Ryzen plot, and the README says braiding is faster below 256 bytes.
- You would ship this repo's code in production. It is stale (last commit 2024-12-27) and has no correctness tests. Its 118960 variant still zeroes the ring buffer with a '+ 60' bound; zlib-ng changed that to '+ 64' in PR #2033 to fix wrong CRCs at lengths such as 615,336 bytes (zlib-ng #2029, shipped in the 2.3.2 hotfix).
- You target big-endian or 32-bit systems. The code does little-endian 64-bit loads with no byte-swapping. zlib-ng needed a big-endian fix (#1891) and a separate 32-bit small variant; this repo has neither.
- You care about memory or per-call cost, or run on a Pi-class memory system. Each large non-destructive call mallocs and zeroes 128 KiB, which the paper says outweighs the gains for smaller messages. The 733112 variants run \~1.5x (destructive) and \~2.4x (non-destructive) slower than braiding on the Raspberry Pi 4 plot.

## How it is fast

A zero polynomial Z(x) satisfies Z(x) mod G(x) = 0, so XORing it into the message leaves the CRC unchanged. Choosing one with few terms, such as x^14870 + x^22 + x^11 + x^7 + 1 with exponents scaled from bits to 64-bit words, cancels each input word by XORing shifted copies of it into a few words roughly 118.8-119 KB further ahead (hence the variant name 118960). The main loop is then plain 64-bit shifts and XORs, with no table loads and no serial dependency on the CRC register. Non-destructive variants keep these forward contributions in a 128 KiB power-of-two ring buffer (the wrap is a bitmask); destructive variants XOR them straight into the caller's buffer. The last \~72 bytes go through a 256-entry Sarwate table, and on x86 the same shift/XOR steps are interleaved between PCLMUL folds.

## Compared with alternatives

The catalogued CRC siblings (corsix fast-crc32, dougallj's M1 PMULL code, crc32fast, crc-fast, klauspost/crc32, komrad36/CRC, htot crc32c) get their headline numbers from CLMUL/PMULL or CRC32 instructions and win by a wide margin wherever those exist. Pick Chorba, preferably through zlib-ng, only for the no-hardware-assist case, where it is the fastest portable C CRC-32 in the catalog relative to zlib's braiding.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the CRC functions themselves, except that the caller must define the 256-entry `crc32_table` they reference as extern (test_crc.h supplies it); the benchmark harness needs the zlib_braiding and zlib_slicing submodules, and the latter uses an SSH (git@github.com) URL |
| **Minimum toolchain** | not documented; C99-style C that the Makefile hard-codes to gcc -O3 (version unstated), with -mno-avx on x86-64; chorba_pclmul needs GCC/Clang `#pragma GCC target("pclmul,avx")` and x86intrin.h |
| **Platforms** | generic variants assume a 64-bit little-endian CPU (tested on x86-64 Ryzen, Graviton2 aarch64 and Raspberry Pi 4); chorba_pclmul needs x86-64 with PCLMULQDQ and AVX; configure calls lscpu, so the build is Linux-oriented; the AVX2/AVX-512 variants benchmarked in the paper are not in the repo |
| **Thread safety** | not documented; each call keeps its state in locals and a per-call malloc'd buffer and only reads the global table, so calls look reentrant, but destructive variants overwrite the caller's buffer |
| **Drop-in for the baseline** | partial — produces the same CRC-32 as zlib's crc32(), but the signature is (uint32_t, char\*, size_t) with no header. The functions work on the raw register without zlib's \~ pre/post conditioning (the harness wraps zlib as crc32(crc ^ 0xffffffff, ...) ^ 0xffffffff for comparison). zlib-ng 2.3+ is the real drop-in. |

## Gotchas

- Conditioning differs from zlib: the functions take and return the un-inverted register, so a standard CRC-32 is f(0xFFFFFFFF, buf, len) ^ 0xFFFFFFFF. Passing a zlib-style running CRC directly gives wrong results.
- The \*_destructive variants overwrite the input buffer. Only the \*_nondestructive variants and chorba_standard leave the data intact.
- Loop indices are `int` while len is size_t, so a single call over 2 GiB overflows. Loads are unaligned type-punned `*(uint64_t*)` casts, which is alignment and strict-aliasing UB in ISO C (zlib-ng's port feeds the unaligned head through braid first). The 128 KiB malloc is not NULL-checked.
- 'Table-less' describes only the bulk loop: the tail (up to \~72 bytes) still uses a 1 KiB Sarwate table. The harness prints the CRC but never compares it with zlib, so the repo does not verify correctness.

## Known shortcomings

- arXiv preprint with no venue; GCC version unstated. Against PCLMUL/AVX code the gain is only 5-20%, and only where those instructions are the baseline; the big wins are over table-driven CRC32 on CPUs without carry-less multiply. Adopted by zlib-ng.
- Repo is stale with no correctness tests; its 118960 variant keeps the `+60` zeroing bound that produced wrong CRCs at 615,336-byte lengths in zlib-ng (#2029; fixed to +64 in PR #2033, 2.3.2 hotfix), so use zlib-ng 2.3.2+ instead. Numbers exist only as plots (\~2.2x over braiding on Ryzen, \~3x on Graviton2/RPi4 at 16 MiB and up); Graviton2's native CRC32 instruction is still \~2x faster. The paper's AVX2/AVX-512 code is not in the repo; little-endian only, int indices overflow above 2 GiB.

## Caveats and trade-offs

arXiv v1 preprint (cs.DS), no peer-reviewed venue found via Crossref. The compiler version is not stated; the repo builds with gcc -O3. Numeric results are only in figures, in seconds per 10^12 bytes, plus the abstract's summary. The 5-20% gain is for the PCLMUL/AVX1 path, not native CRC32-opcode platforms, which serve only as comparison points. The 2x holds for large messages, and destructive variants regress on the Raspberry Pi 4. zlib-ng 2.3.0 adopted Chorba (generic/SSE2/SSE4.1; PR #1837 by the author), but its release notes give no numbers.

Table-less: trades lookup tables for extra registers/local variables; several polynomial variants selected by message-length range; some variants are destructive (modify the input buffer in place)

## Maintenance

Stale research code (last commit 2024-12-27, 6 stars) under the permissive zlib license, fine to copy but unmaintained and missing later fixes. Use zlib-ng 2.3.2+ (WITH_CRC32_CHORBA on by default) for a maintained, bug-fixed version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** arXiv 2412.16398 is a single-author v1 preprint (cs.DS) and Crossref shows no peer-reviewed venue, so it is first-party evidence, not B. The repo has public benchmark code (test_crc.c, run_tests.sh; configure sets gcc CFLAGS=-O3) and the paper names the CPUs, but no gcc version is stated anywhere, so it is not A.
- **Verifier notes:** The paper's table confirms the zlib 1.3.1.1 braiding baseline, and the abstract's 100% and 5-20% figures match. The record overstated the 5-20% as covering native-CRC32-instruction platforms. The LICENSE file is the zlib license (GitHub reports NOASSERTION), so Zlib/copyable is right. 6 stars and the last commit of 2024-12-27 (stale) are confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2412.16398>
  - <https://arxiv.org/pdf/2412.16398>
  - <https://github.com/samrussell/chorba>
  - <https://github.com/samrussell/chorba/blob/master/LICENSE>
  - <https://github.com/samrussell/chorba/blob/master/Makefile.in>
  - <https://github.com/samrussell/chorba/blob/master/configure>
  - <https://github.com/samrussell/chorba/blob/master/run_tests.sh>
  - <https://api.crossref.org/works?query.bibliographic=Chorba+novel+CRC32+implementation&rows=5>
  - <https://github.com/zlib-ng/zlib-ng/releases>
  - <https://github.com/zlib-ng/zlib-ng/pull/1837>
- **Sources the enricher read:**
  - <https://github.com/samrussell/chorba>
  - <https://github.com/samrussell/chorba/blob/master/README.md>
  - <https://github.com/samrussell/chorba/blob/master/LICENSE>
  - <https://github.com/samrussell/chorba/blob/master/chorba_standard.c>
  - <https://github.com/samrussell/chorba/blob/master/chorba_small_nondestructive.c>
  - <https://github.com/samrussell/chorba/blob/master/chorba_118960_nondestructive.c>
  - <https://github.com/samrussell/chorba/blob/master/chorba_118960_destructive.c>
  - <https://github.com/samrussell/chorba/blob/master/chorba_pclmul.c>
  - <https://github.com/samrussell/chorba/blob/master/chorba_end.c>
  - <https://github.com/samrussell/chorba/blob/master/pclmul.c>
  - <https://github.com/samrussell/chorba/blob/master/braiding.c>
  - <https://github.com/samrussell/chorba/blob/master/test_crc.c>
  - <https://github.com/samrussell/chorba/blob/master/test_crc.h>
  - <https://github.com/samrussell/chorba/blob/master/run_tests.sh>
  - <https://github.com/samrussell/chorba/blob/master/Makefile.in>
  - <https://github.com/samrussell/chorba/blob/master/configure>
  - <https://github.com/samrussell/chorba/blob/master/.gitmodules>
  - <https://raw.githubusercontent.com/samrussell/chorba/master/figures/amdryzen.png>
  - <https://raw.githubusercontent.com/samrussell/chorba/master/figures/t4g.png>
  - <https://raw.githubusercontent.com/samrussell/chorba/master/figures/rpi4.png>
  - <https://arxiv.org/pdf/2412.16398>
  - <https://github.com/zlib-ng/zlib-ng/pull/1837>
  - <https://github.com/zlib-ng/zlib-ng/pull/2033>
  - <https://github.com/zlib-ng/zlib-ng/pull/1915>
  - <https://github.com/zlib-ng/zlib-ng/pull/1891>
  - <https://github.com/zlib-ng/zlib-ng/issues/2029>
  - <https://github.com/zlib-ng/zlib-ng/issues/1910>
  - <https://github.com/zlib-ng/zlib-ng/issues/1926>
  - <https://github.com/zlib-ng/zlib-ng/releases>
  - <https://github.com/zlib-ng/zlib-ng/releases/tag/2.3.2>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/CMakeLists.txt>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/arch/generic/crc32_chorba_c.c>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/crc32_chorba_p.h>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/samrussell/chorba`) · [data/wave7/enrich/raw/github_com_samrussell_chorba.json](../../../data/wave7/enrich/raw/github_com_samrussell_chorba.json) (enrichment confidence 0.75)

</details>
