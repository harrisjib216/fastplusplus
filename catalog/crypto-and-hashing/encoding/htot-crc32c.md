# crc32c (htot)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause (crc32c/LICENSE, MIT copyright, with Intel slicing-by-8 under the same terms; the README says BSD 2-clause). crc32intelc.cc and crc32adler.cc are under the Zlib license, and crc_iscsi_v_pcl.asm is Intel BSD-3-Clause. GitHub's license API detects none.` · 🔴 abandoned

> C++ port of Intel's 3-way crc32q+pclmulqdq CRC-32C kernel that also runs on 32-bit x86; \~11x faster than slicing-by-8.

| | |
|---|---|
| **Beats** | CRC32 (CRC-32C/Castagnoli; SlicingBy8 software baseline is representative of the algorithm used by most CRC32 library implementations) |
| **Claimed result** | README, 4096-byte buffer, 64-bit i7-4770: SlicingBy8 is 5.1x faster than Sarwate, Hardware64 is 4.2x faster than SlicingBy8, and IntelC is 2.7x faster than Hardware64. Chaining those gives IntelC roughly 58x over the byte-at-a-time Sarwate (derived from page data). On 32-bit Edison, IntelC is 8.8x faster than SlicingBy8. Against the strongest bundled incumbent, Mark Adler's SSE4.2 crc32c, the log-scale chart shows IntelC only modestly ahead (roughly 1.2x on 64-bit i7-4770, read off the chart), and about level with Intel's own asm (IntelAsm), which it is ported from. |
| **Workload** | crc32cbench (crc32c/crc32cbench.cc) on a 4096-byte aligned buffer, as charted; the program also sweeps 16 B to 8 KiB. It compares Sarwate, SlicingBy4, SlicingBy8, Hardware32, Hardware64 (SSE4.2 crc32), Adler (Mark Adler's 3-way crc32), IntelC (this project's C port of Intel's crc32 + pclmulqdq code) and IntelAsm (Intel's original asm). |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4770 (Haswell; 32- and 64-bit builds), Intel Atom E3815 (NUC, 64-bit) and Intel Edison (x86-32 and x86-64), per the chart labels |
| **Compiler and flags** | g++ 6.3 (i7-4770 32- and 64-bit, Edison) and g++ 7.2 (i7-4770 64-bit, NUC E3815), per the chart labels. crc32c/Makefile uses -O3 -DNDEBUG -flto -msse4.2 -mpclmul, plus -m32/-m64 when CPU_TYPE is set. Intel's crc_iscsi_v_pcl.asm is assembled with yasm. DEBUG=TRUE builds with -g -O0. |
| **Adoption** | 96 stars |
| **Last commit** | 2017-11-01 |
| **Links** | [repository](https://github.com/htot/crc32c) · [benchmark](https://github.com/htot/crc32c#benchmarks) |

## Verdict

crc32cbench hashes one 4096-byte, 8-byte-aligned buffer repeatedly (so it stays in cache) and reports the median of 5 trials in MiB/s. The builds used g++ 6.3/7.2 with -O3 -flto -msse4.2 -mpclmul. On a 64-bit Haswell i7-4770, IntelC reached roughly 27,000 MiB/s (read off the log chart): 2.7x a single-stream crc32q loop, about 11x Intel's slicing-by-8 tables, about 1.2x Mark Adler's 3-way SSE4.2 code, and level with the Intel asm it ports. It was 8.8x slicing-by-8 on 32-bit Edison but lost to Hardware64 on 64-bit Silvermont Atoms.

## Use it when

- CRC-32C (iSCSI, ext4, Btrfs polynomial) on 32-bit i686 builds with SSE4.2 and PCLMULQDQ, such as Intel Edison or legacy 32-bit software, where the alternative is slicing-by-8 or a crc32l loop: 8.8x over SlicingBy8 on 32-bit Edison.
- Buffers of roughly 1-8 KiB on 64-bit Haswell/Skylake-class desktop cores without AVX-512: about 2.7x a single-stream crc32q loop at 4 KiB on an i7-4770.
- You want a readable C-level reference of Intel's 3-way crc32+pclmul CRC-32C algorithm to study or port, instead of the yasm assembly.
- Comparing CRC-32C implementations: crc32cbench sweeps 16 B to 8 KiB, aligned and misaligned, across all eight bundled variants.

## Skip it when

- zlib/gzip/PNG/Ethernet CRC-32: it computes CRC-32C only, and issue #3 is a user tripped up by exactly this difference.
- Silvermont-class Atoms (Edison in 64-bit mode, NUC E3815): the author's chart shows every 3-way path (Adler, IntelC, IntelAsm) slower there than the plain Hardware64 loop.
- Small or mid-size messages: at 216 B and below it is a single crc32q stream. In a third-party i7-8665U run, throughput fell from about 24.7 GB/s at 128 B to about 16 GB/s at 256 B, right after the 3-way path starts.
- Modern AVX-512/VPCLMULQDQ servers or aarch64: the corsix fast-crc32 README measures the pure three-way crc32 approach at about 15-24 GB/s, against 25-97 GB/s for its fusion and VPCLMULQDQ kernels. There is no ARM port.
- MSVC or long-term maintenance needs: it relies on GCC __builtin_ia32_crc32\* builtins, GNU inline asm and &lt;cpuid.h&gt;, and has been untouched since 2017.

## How it is fast

The SSE4.2 crc32 instruction has 3-cycle latency but single-cycle throughput. Above 216 bytes the buffer is therefore cut into three equal segments of up to 1024 bytes (128 eight-byte words), and three independent crc32q streams run interleaved, unrolled with Duff's device. The three partial CRCs are then merged: two of them are carry-less-multiplied (pclmulqdq) by precomputed x^n mod P constants from a block-size-indexed table and XOR-folded into the third. This is the method of Intel's 2011 whitepaper 'Fast CRC Computation for iSCSI Polynomial Using CRC32 Instruction' (Gopal et al.). On 32-bit builds each crc32q becomes two crc32l, and the merge uses movd/pextrd.

## Compared with alternatives

Pick it over fast-crc32 (corsix) only for 32-bit x86 or pre-AVX-512 Intel desktop chips where you want one small hand-written C++ file with no generator step; on 64-bit x86 corsix's fusion kernels supersede it and also cover aarch64. crc-fast offers runtime dispatch and many CRC widths, and crc32fast is Rust and computes zlib CRC-32, so neither replaces this for a C/C++ CRC-32C drop-in on 32-bit.

## Integration

| | |
|---|---|
| **Form** | source-drop (crc32intelc.cc, logging/crc32intelc.h and the K constant table in crc32inteltable.cc; the Makefile only builds the test and benchmark executables) |
| **Dependencies** | none for IntelC; yasm only for the IntelAsm variant; the tests use the bundled stupidunit |
| **Minimum toolchain** | Not documented. g++ with -msse4.2 -mpclmul (the chart shows g++ 6.3 and 7.2). The code is C++ (.cc) with GNU inline asm. |
| **Platforms** | x86 only (i686 and x86-64), requiring SSE4.2 and PCLMULQDQ; the IntelAsm variant is 64-bit only |
| **Thread safety** | Not documented. The kernels are pure functions over const tables, but the global `logging::crc32c` pointer rewrites itself on its first call with no synchronization. |
| **Drop-in for the baseline** | partial — same (crc, ptr, len) shape as typical slicing-by-8 CRC-32C code, but the caller must apply the 0xFFFFFFFF init and final inversion, the symbols live in namespace logging, and it is not a replacement for zlib's crc32(). |

## Gotchas

- The auto-dispatch pointer `logging::crc32c` (detectBestCRC32C) picks Hardware64/Hardware32 on any SSE4.2 CPU and never IntelC. It also checks only SSE4.2, not PCLMULQDQ. Call crc32cIntelC directly and do your own feature check.
- The kernels do no pre- or post-inversion. Without crc32cInit() and crc32cFinish() the results will not match standard CRC-32C test vectors (e.g. 0xE3069283 for '123456789').
- The 32-bit CombineCRC inline asm writes to operands declared only as inputs (crc32l into crc2's register, pextrd into %1), which GCC's inline-asm rules forbid. It passed the repo's tests with g++ 6.3/7.2 but could miscompile under newer compilers.
- The crc32cIntelAsm wrapper casts the size_t length to int, so that variant breaks on buffers of 2 GiB or more (IntelC keeps size_t).

## Known shortcomings

- The \~58x headline is only against the bytewise Sarwate table; against Adler's slicing code it is \~1.2x and about equal to Intel's assembly. Old setup (i7-4770 Haswell, g++ 6.3/7.2). License is BSD-3 plus Zlib-licensed parts.
- Auto-dispatch never selects the IntelC kernel (picks Hardware64) and checks SSE4.2 but not PCLMUL. 32-bit CombineCRC inline asm writes input-only operands (latent miscompile); IntelAsm wrapper casts length to int. Throughput dips past the 216-byte threshold (third-party i7-8665U: 24.7 GB/s at 128 B, 16 GB/s at 256 B); slower than Hardware64 on Silvermont. CRC-32C only, x86 and GCC only, abandoned since 2017; superseded by corsix/fast-crc32 on 64-bit.

## Caveats and trade-offs

All the implementations compared are bundled in this repo: evanjones' Sarwate and slicing-by-4/8, Mark Adler's SSE4.2 code, and Intel's asm. The headline \~58x is against byte-at-a-time Sarwate. Against Adler's hardware crc32c the gain is only modest, and IntelC merely matches Intel's own asm, which it ports. The main contribution is portable C that also runs on 32-bit. On 64-bit Edison and the NUC E3815 (Silvermont), the 3-way crc32q+pclmul paths (Adler, IntelC, IntelAsm) are slower than plain Hardware64. The IntelC path only pays off above 216 bytes. It computes CRC-32C (Castagnoli) only, not the zlib/gzip CRC-32. The code is actually C++ (.cc) with inline asm, and the last commit was in 2017.

IntelC path is only efficient above 216-byte buffers due to pclmulqdq combine overhead; 32-bit portability path needs inline assembly; unmaintained since 2017

## Maintenance

Abandoned since 2017-11-01 (12 commits, no open issues, none of its 18 forks active after 2020), but small and permissively licensed (MIT-style BSD-3 LICENSE, with Zlib-licensed headers on crc32intelc.cc and crc32adler.cc) and easy to vendor. It was last known to work with g++ 7.2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The README ratios are there verbatim, and the linked chart (crc32c-benchmarks.png, 4096-byte aligned buffer) names the CPUs (i7-4770, Atom E3815 NUC, Edison) and the compilers (g++ 6.3 and g++ 7.2). The benchmark code is public (crc32c/crc32cbench.cc), and the flags are in crc32c/Makefile (-O3 -DNDEBUG -flto -msse4.2 -mpclmul). It runs against the incumbent software CRC-32C (Sarwate, Intel slicing-by-8) and Mark Adler's widely used SSE4.2 code, so it meets A.
- **Verifier notes:** Tier raised to A because the chart names the CPU and g++ versions and the Makefile holds the flags. The honest incumbent win is small (IntelC is roughly 1.2x over Adler and about level with Intel's asm). The \~58x is only against Sarwate. 96 stars, not archived, not a fork, last commit 2017-11-01 (abandoned) all verified. The record's language 'C' should really be C++, and the '\~500MHz' Edison clock is not on the page.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/htot/crc32c>
  - <https://github.com/htot/crc32c#benchmarks>
  - <https://raw.githubusercontent.com/htot/crc32c/master/crc32c-benchmarks.png>
  - <https://github.com/htot/crc32c/blob/master/crc32c/LICENSE>
  - <https://github.com/htot/crc32c/blob/master/crc32c/Makefile>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32cbench.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32intelc.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32adler.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32intelasm.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc_iscsi_v_pcl.asm>
- **Sources the enricher read:**
  - <https://github.com/htot/crc32c>
  - <https://github.com/htot/crc32c#benchmarks>
  - <https://raw.githubusercontent.com/htot/crc32c/master/crc32c-benchmarks.png>
  - <https://github.com/htot/crc32c/blob/master/crc32c/LICENSE>
  - <https://github.com/htot/crc32c/blob/master/crc32c/Makefile>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32intelc.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/logging/crc32intelc.h>
  - <https://github.com/htot/crc32c/blob/master/crc32c/logging/crc32c.h>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32c.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32cbench.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32c_test.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32adler.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32intelasm.cc>
  - <https://github.com/htot/crc32c/blob/master/crc32c/crc32inteltable.cc>
  - <https://github.com/htot/crc32c/commits/master>
  - <https://github.com/htot/crc32c/issues/1>
  - <https://github.com/htot/crc32c/issues/3>
  - <https://github.com/htot/crc32c/forks>
  - <https://hn.algolia.com/api/v1/search?query=htot%20crc32c>
  - <https://github.com/corsix/fast-crc32#readme>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/htot/crc32c`) · [data/wave7/enrich/raw/github_com_htot_crc32c.json](../../../data/wave7/enrich/raw/github_com_htot_crc32c.json) (enrichment confidence 0.8)

</details>
