# komrad36/CRC ("Golden" hardware-accelerated CRC32)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> x86-64 CRC-32C in one function: three interleaved SSE4.2 crc32 streams recombined with PCLMULQDQ, \~2.9x a single-stream crc32 loop.

| | |
|---|---|
| **Beats** | The author's own C++/asm reimplementations of bitwise (naive) and slicing-by-1..16 tabular CRC-32C, plus a single-stream SSE4.2 _mm_crc32_u64 loop. zlib is never mentioned or tested. |
| **Claimed result** | Golden: \~62 bits/cycle vs 8.00 bits/cycle for the 16-byte tabular version (7.75x, derived from page data) and vs 21.30 bits/cycle for a plain 8-byte hardware crc32 loop (\~2.9x, derived from page data). The page says naive implementations are 'more than 150x slower than our final Golden result' (0.09-0.33 bits/cycle). |
| **Workload** | CRC-32C (Castagnoli poly 0x82F63B78 reflected, the polynomial hard-wired in the x86 SSE4.2 crc32 instruction) of a 900 KB buffer of mt19937 (seed 5) random bytes, repeated 20-10000 runs per option. It compares 13 implementations from bitwise through 16-byte tabular and 1/8-byte hardware crc32 up to 'Golden': 3 parallel SSE4.2 crc32 streams recombined with a PCLMULQDQ carry-less multiply and a LUT of shift constants. There is also a 2-way AMD Jaguar variant. |
| **Metric** | throughput |
| **Hardware** | unspecified "high-end modern x86 CPU" |
| **Compiler and flags** | MSVC v142 (Visual Studio 2019), Release x64: /O2 (MaxSpeed), /Oi intrinsics, /arch:AVX2 (per CRC/CRC.vcxproj). The README table does not state which build produced it. |
| **Adoption** | 352 stars |
| **Last commit** | 2021-04-25 |
| **Links** | [repository](https://github.com/komrad36/CRC) · [benchmark](https://github.com/komrad36/CRC#readme) |

## Verdict

The README table comes from CRC/main.cpp, which times each method on the same 900 KiB mt19937 buffer for 20-10000 runs and converts wall-clock ns to 'bits/cycle' by assuming a 4 GHz clock. The CPU is described only as a 'high-end modern x86 CPU', and the compiler is unstated; the repo's project is MSVC v142 /O2 /arch:AVX2. Golden's 62 bits/cycle (about 31 GB/s under the 4 GHz assumption) compares with 21.3 for a single-stream 8-byte crc32 loop (\~2.9x) and 8.0 for slicing-by-16 (\~7.75x), all of them the author's own implementations rather than zlib or a named library. Independently, corsix measured the same three-way structure at 53.7-56.5 bits/cycle (27-33 GB/s) on 4 KiB buffers across Broadwell, Skylake and Ice Lake, and 23.5 GB/s on AMD Rome.

## Use it when

- x86-64 code that must checksum KB-to-MB buffers with CRC-32C (the iSCSI/ext4/Btrfs polynomial) and is limited by a plain _mm_crc32_u64 loop. Here Golden measured 62 vs 21.3 bits/cycle, and an HN user reported \~32 GB/s on an i7-4770K.
- You want a small MIT-licensed function to vendor (one .cpp, a 2 KB LUT, no dependencies) rather than a library with a build system.
- Game-engine style integrity checks (save data, cooked assets, memory-stomp detection), which are the author's stated use case. Use the 2-way option_14_golden_amd on AMD Jaguar consoles, where crc32 reciprocal throughput is 2 cycles.
- Learning or teaching CRC optimization: the README walks from bitwise CRC through slicing-by-N to the parallel crc32 + CLMUL recombine, and HN commenters cite it as the standard overview.

## Skip it when

- You need IEEE CRC-32 (zlib, gzip, PNG, ZIP, Ethernet). The x86 crc32 instruction hard-codes the Castagnoli polynomial, and the author confirms in issue #2 that Golden cannot be changed to match zlib. Use a PCLMULQDQ-folding implementation such as crc32fast, klauspost/crc32 or crc-fast instead.
- You want the fastest CRC-32C on current x86. corsix's 'fusion' of crc32 and pclmulqdq streams measured \~93 bits/cycle against \~54-57 for this three-way design on Broadwell/Skylake/Ice Lake, and corsix/fast-crc32 AVX-512 kernels reach 97.30 GB/s on Sapphire Rapids.
- Short messages. Below LEAF_SIZE (144 bytes on Intel, 112 on AMD) it only runs the plain 8-byte crc32 loop, so there is no gain over the single-stream baseline, and there is also a byte-wise alignment prologue.
- Non-x86 targets, or binaries that must run on CPUs without SSE4.2 and PCLMULQDQ. There is no runtime dispatch or portable fallback in the Golden files, and the tabular options are demo code (see gotchas). On ARM, see dougallj's M1 gist or corsix/fast-crc32.
- You need a maintained, tested library. The only build is a Windows VS2019 solution, there are no unit tests (main.cpp just prints each option's CRC for visual comparison), and the last commit was in April 2021.

## How it is fast

A single _mm_crc32_u64 chain is latency-bound (3-cycle latency, 1-per-cycle throughput on Intel), which caps it at about 21.3 bits/cycle. Golden splits each block of up to 6 KiB into three equal parts and runs three independent crc32 chains in parallel. It then merges them by carry-less multiplying (PCLMULQDQ) the A and B partial CRCs with precomputed constants CRC(x^k) from a 256-entry LUT, and folds the result into C's last 8-byte word with one more crc32. Block sizes are dispatched through a fully unrolled 255-case switch generated by 'doubler' macros (765 crc32 instructions), and a multiply-shift (x\*2731&gt;&gt;16) replaces division by 24. The technique matches Intel's 2011 'Fast CRC Computation for iSCSI Polynomial Using CRC32 Instruction' whitepaper, and the README derives it from first principles.

## Compared with alternatives

Pick it when you want the most readable, easily vendored x86-64 CRC-32C (one MIT-licensed function) together with the best-known derivation of the three-way crc32 + CLMUL technique. For more throughput use corsix/fast-crc32. For IEEE CRC-32 or ARM use crc32fast, crc-fast or klauspost/crc32. htot/crc32c wraps Intel's original crc_iscsi_v_pcl assembly for the same algorithm, adds a 32-bit port and is BSD-2-licensed.

## Integration

| | |
|---|---|
| **Form** | source-drop (copy golden_intel.cpp or golden_amd.cpp; the repo itself is a Visual Studio benchmark solution, not a library) |
| **Dependencies** | none (compiler intrinsics from &lt;immintrin.h&gt; only) |
| **Minimum toolchain** | The repo builds with Visual Studio 2019 (v142 toolset) for x64; options 1-4 need MASM. Golden itself is C++11-level code (constexpr, a default argument). The README discusses GCC and other compilers' codegen, but only MSVC project files ship; with GCC or Clang you would need -msse4.2 -mpclmul or equivalent (inferred, not tested). |
| **Platforms** | x86-64 only, with SSE4.2 (crc32) and PCLMULQDQ. It uses _mm_crc32_u64 and pointer-to-uint64_t casts, so the solution's Win32 configurations cannot build it. The Intel variant is tuned for crc32 at 3-cycle latency and 1/cycle throughput, the AMD variant for Jaguar's 1 per 2 cycles. |
| **Thread safety** | Not documented. The Golden functions only read a static const LUT and write no globals, so concurrent calls look safe from the source. |
| **Drop-in for the baseline** | partial — the (buffer, length, prev) -&gt; uint32_t shape fits a CRC-32C routine, but by default it skips the standard \~init/\~final inversion, so outputs differ from iSCSI CRC-32C until two commented lines are enabled. It can never replace zlib's IEEE crc32(). |

## Gotchas

- The shipped code does not produce standard CRC-32C. golden_intel.cpp and golden_amd.cpp start from prev and return the raw register with the \~ lines commented out, while the README's listing inverts both. Issue #2 shows 'hello-world' giving 1585878819 here against 4099351003 from htot/crc32c; the author's answer was to uncomment those two lines.
- The tabular 'portable' options are demos. Options 9 and 10 loop while (bytes) { ...; bytes -= 8 or 16; } on a uint32_t, so any length that is not a multiple of 8 or 16 wraps around and reads far past the buffer; the issue #2 reporter hit a segfault going down this path. They also read native-endian 32-bit words and apply no init or final XOR.
- There is no CPU feature check: calling Golden on a CPU without SSE4.2/PCLMULQDQ faults with an illegal instruction. The provided Release x64 project compiles everything with /arch:AVX2, so rebuild with a lower /arch before targeting AVX-only CPUs such as Jaguar, which option 14 exists for.
- The length is a uint32_t, so each call handles under 4 GiB; chain larger buffers through prev. Loads are type-punned (\*(uint64_t\*)p), and for n == 256 the _mm_loadu_si128 of g_lut_intel[n-1] nominally reads 8 bytes past the 256-entry LUT, although only the low 8 bytes are used.

## Known shortcomings

- Computes CRC-32C (Castagnoli), not zlib's CRC-32. 'Golden' is three crc32-instruction streams combined with CLMUL, not PCLMULQDQ folding. CPU unnamed; bits/cycle figures assume 4 GHz. MSVC /O2 /arch:AVX2.
- Default output is not standard CRC-32C: the initial/final inversion is commented out (issue #2). Tabular fallback options 9/10 underflow the length on inputs not a multiple of 8/16 and read far past the buffer. No CPU feature check, MSVC-only project, no tests, 32-bit length. corsix measured the same 3-way design at \~54-57 bits/cycle versus \~93 for corsix's fused kernel.

## Caveats and trade-offs

This computes CRC-32C (Castagnoli), not the IEEE CRC-32 used by zlib, gzip, PNG and ZIP. The x86 crc32 instruction cannot compute IEEE CRC-32, so it is not a drop-in for zlib crc32(). The README is an educational derivation with a self-reported bits/cycle table on an unnamed 'high-end modern x86 CPU'. main.cpp computes bits/cycle from wall-clock time assuming a 4 GHz clock. The project is a Windows-only MSVC solution and needs SSE4.2 + PCLMULQDQ.

Hardware-accelerated "Golden" path requires SSE4.2 (crc32 instruction) plus PCLMULQDQ; earlier tabular options in the same repo are the portable fallback for non-x86/embedded targets.

## Maintenance

Abandoned since 2021-04-25 (the last commits were typo and comment fixes, and the one open issue is corsix's 2022 'alloy' note), but MIT-licensed and small enough to vendor: copy golden_intel.cpp, decide on the \~init/\~final lines, and compile with SSE4.2 and PCLMUL enabled.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README's 'Performance comparison table' lists Option 1-13 in bits/cycle (Golden 62.00, 16-byte tabular 8.00, 8-byte hardware 21.30, naive 0.09-0.33), and the benchmark code (CRC/main.cpp) plus an MSVC v142 project with Release x64 /O2 /Oi /arch:AVX2 (CRC/CRC.vcxproj) are public. No CPU model is named anywhere, and main.cpp derives 'bits/cycle' from wall-clock ns by assuming a 4 GHz clock, so this is first-party data short of A.
- **Verifier notes:** The numbers match the README table exactly and &gt;150x vs naive is stated on the page. The record wrongly framed the baseline as zlib-style CRC32 and the algorithm as 'PCLMULQDQ folding'. It is 3-way crc32-instruction interleaving with a CLMUL recombine, and the polynomial is CRC-32C. Metadata checked: MIT, 352 stars, last commit 2021-04-25, not a fork, not archived.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** corsix/fast-crc32 notes: 3-way crc32+CLMUL design \~54-57 bits/cycle vs corsix fusion \~93; HN user reports \~32 GB/s on i7-4770K.
- **Pages the verifier opened:**
  - <https://github.com/komrad36/CRC>
  - <https://github.com/komrad36/CRC#readme>
  - <https://github.com/komrad36/CRC/blob/master/CRC/main.cpp>
  - <https://github.com/komrad36/CRC/blob/master/CRC/CRC.vcxproj>
- **Sources the enricher read:**
  - <https://github.com/komrad36/CRC>
  - <https://github.com/komrad36/CRC#readme>
  - <https://github.com/komrad36/CRC/tree/master>
  - <https://github.com/komrad36/CRC/commits/master>
  - <https://github.com/komrad36/CRC/blob/master/CRC/main.cpp>
  - <https://github.com/komrad36/CRC/blob/master/CRC/golden_intel.cpp>
  - <https://github.com/komrad36/CRC/blob/master/CRC/golden_amd.cpp>
  - <https://github.com/komrad36/CRC/blob/master/CRC/hardware_methods.cpp>
  - <https://github.com/komrad36/CRC/blob/master/CRC/naive_methods_cpp.cpp>
  - <https://github.com/komrad36/CRC/blob/master/CRC/naive_methods_asm.asm>
  - <https://github.com/komrad36/CRC/blob/master/CRC/tabular_methods.cpp>
  - <https://github.com/komrad36/CRC/blob/master/CRC/CRC.vcxproj>
  - <https://github.com/komrad36/CRC/issues?q=>
  - <https://github.com/komrad36/CRC/issues/2>
  - <https://github.com/komrad36/CRC/issues/4>
  - <https://www.corsix.org/content/fast-crc32c-4k>
  - <https://github.com/corsix/fast-crc32#readme>
  - <https://github.com/htot/crc32c#readme>
  - <https://hn.algolia.com/api/v1/search?query=komrad36%20CRC&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=github.com/komrad36/CRC>
  - <https://news.ycombinator.com/item?id=31471207>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/komrad36/crc`) · [data/wave7/enrich/raw/github_com_komrad36_crc.json](../../../data/wave7/enrich/raw/github_com_komrad36_crc.json) (enrichment confidence 0.8)

</details>
