# zlib-ng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Zlib` · 🟢 active

> Maintained zlib fork with SIMD deflate, inflate and CRC32/Adler32; about 2.2-2.5x faster compression and 1.5x faster decompression than zlib.

| | |
|---|---|
| **Beats** | zlib (including its CRC32/Adler32 checksum routines) |
| **Claimed result** | lzbench 2.0.1 (AMD EPYC 9554, gcc 14.2.0, Silesia, single thread), zlib-ng 2.2.3 vs zlib 1.3.1. Compression: 202 vs 93.0 MB/s at -1, 62.1 vs 25.3 MB/s at -6, 24.6 vs 10.3 MB/s at -9 (\~2.2-2.5x). Decompression: 471-518 vs 323-348 MB/s (\~1.5x) (ratios derived from page data). The project README separately claims "x86-64 can be about 4x faster than stock zlib". |
| **Workload** | General deflate/inflate throughput plus CRC32-B and Adler32 checksum computation on x86-64, using SIMD (SSE2/SSE4.1/PCLMULQDQ/AVX2/AVX512) and ARMv8 PMULL+EOR3 code paths as a drop-in zlib replacement |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9554 @ 3.10 GHz, single thread, performance governor, turbo disabled, Ubuntu 24.04.1 |
| **Compiler and flags** | gcc 14.2.0 (lzbench 2.0.1 build). Flags are not stated on the page; the lzbench Makefile defaults to -O3 -DNDEBUG. |
| **Adoption** | 2.1k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/zlib-ng/zlib-ng) · [benchmark](https://github.com/inikep/lzbench#benchmarks) |

## Verdict

In the independent lzbench 2.0.1 table (gcc 14.2.0 with the Makefile's default -O3, one thread of an AMD EPYC 9554 at 3.10 GHz with turbo off, silesia.tar), zlib-ng 2.2.3 compressed 2.2x (-1), 2.5x (-6) and 2.4x (-9) faster than zlib 1.3.1 and decompressed 1.46-1.49x faster (471-518 vs 323-348 MB/s), with a much worse ratio at -1 and about equal ratios at -6 and -9. The README's '4x' only appears in the maintainers' own deflatebench runs (discussion #2022: 4.1-4.9x at level 6 on a Ryzen 8700GE and an i7-11700K, against a zlib develop build with unstated flags), and the CRC32/Adler32 speedups have no published numbers.

## Use it when

- Servers, log shippers or batch jobs that must emit standard gzip/zlib/DEFLATE at levels 1-9 and are bound by compression CPU: independent lzbench numbers show 2.2-2.5x zlib 1.3.1's compression throughput.
- Speeding up an existing zlib-linked application or a whole distro without code changes: build with ZLIB_COMPAT=ON and relink or LD_PRELOAD. Fedora 40 adopted zlib-ng-compat as its system zlib.
- Code that runs crc32()/adler32() over large buffers (gzip trailers, PNG, zip, framing) on x86-64 with PCLMULQDQ/AVX2/AVX-512 or on aarch64 with PMULL, where the SIMD kernel is picked at runtime.
- One portable binary for many CPUs: runtime dispatch covers x86, ARM, POWER, RISC-V, LoongArch, MIPS and IBM Z (including DFLTCC hardware deflate), so a baseline x86-64 build still uses AVX-512 where the CPU has it.
- Latency-sensitive callers that want every allocation to happen in deflateInit/inflateInit. zlib-ng allocates one block at init and can then only fail at init.

## Skip it when

- You control both ends and do not need DEFLATE. In the same lzbench run, zstd 1.5.6 -1 compresses 2.1x faster than zlib-ng -1 (422 vs 202 MB/s), gives a much better ratio (34.64% vs 44.41%) and decompresses 2.9x faster (1347 vs 471 MB/s).
- Level 1 when output size matters. zlib-ng -1 output is about 22% larger than zlib -1 on Silesia (44.41% vs 36.45%), because deflate_quick uses static Huffman trees. Use level 2 or higher.
- Maximum whole-buffer decompression speed: libdeflate 1.23 (not catalogued) decompresses Silesia at 860-919 MB/s against zlib-ng's 471-518 MB/s in the same lzbench table, but libdeflate has no streaming API.
- Tests, caches or golden files that depend on zlib's exact compressed bytes or lengths. PORTING.md says the output differs from zlib, and Z_DEFLATE_REPRODUCIBLE only guarantees identical output within an identical zlib-ng build.
- Apps that feed zlib a fixed pre-sized zalloc pool (the nginx pattern): zlib-ng needs more memory, about 350 KB for deflate and 42 KB for inflate on 64-bit, because inflate always allocates the full window. The README also warns against manually replacing the system libz.

## How it is fast

At first use, a runtime-filled function table (functable.c, using cpuid/hwcap) picks SIMD kernels for Adler32 (SSSE3 up to AVX512-VNNI, Neon dot-product), CRC32, compare256 match-length search, slide_hash and inflate's chunked match copy (chunkmemset). The CRC32 kernels are Intel's PCLMULQDQ/VPCLMULQDQ folding, a PMULL+EOR3 kernel from corsix/fast-crc32, and the Chorba algorithm (arXiv 2412.16398) for CPUs without carry-less multiply. Deflate swaps zlib's level-1 and level 3-6 match finders for Intel-derived strategies: deflate_quick (level 1 reads only the hash-chain head and emits static Huffman trees) and deflate_medium (levels 3-6). It also uses a 64K-entry Knuth multiplicative hash, and inflate adds a wider bit buffer and SIMD match copies.

## Compared with alternatives

Pick zlib-ng over zstd or LZ4 when the format must stay zlib/gzip/DEFLATE (HTTP gzip, PNG, zip, existing archives, readers you do not control) or when you want existing zlib callers to get faster with no code changes. If you control both ends, zstd -1 beats it on speed and ratio, and LZ4 decompresses about 8x faster (3716 vs 471 MB/s in lzbench) at a worse ratio.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake or configure build; vcpkg port) |
| **Dependencies** | none at runtime (libc only). Tests use Google Test and benchmarks use Google Benchmark, both optional build options. |
| **Minimum toolchain** | C11 by default (CMake also accepts C99); CMake 3.14+ for 2.3.x; the project wiki recommends GCC 8.5+, Clang 11+ and MSVC 2022 |
| **Platforms** | x86/x86-64 (SSE2 through AVX-512/VNNI/VPCLMULQDQ, runtime-detected), ARM/aarch64 (ARMv6, Neon, ARMv8 CRC/PMULL, EOR3), POWER8/9, RISC-V (RVV, Zbc), LoongArch (LSX/LASX), MIPS MSA and IBM Z (VX, DFLTCC), with generic C fallbacks. CI runs on Linux, macOS and Windows. |
| **Thread safety** | Same model as zlib: separate streams can be used from separate threads if zalloc/zfree are thread-safe, but one stream must not be shared. The CPU-dispatch table is filled lazily with atomic pointer stores (__atomic on GCC/Clang, Interlocked on MSVC). |
| **Drop-in for the baseline** | partial — the ZLIB_COMPAT=ON build is API/ABI compatible with zlib (it advertises zlib 1.3.1, not 1.3.2) and can replace libz or be LD_PRELOADed. However, the compressed bytes differ from zlib's, it uses more memory, and the default native build needs zng_-prefixed calls and different types. |

## Gotchas

- The default CMake build is native mode (libz-ng, zlib-ng.h). You must pass ZLIB_COMPAT=ON to get a libz replacement. Linking a compat-mode zlib-ng into a process that also pulls in the system zlib through another library can crash or corrupt output (PORTING.md).
- Skip 2.3.1: its Chorba CRC32 returned wrong CRCs for some inputs over 256 KB, which the 2.3.2 hotfix fixed. The latest release is 2.3.3 (Feb 2026). Newer work, such as PR #2353's inflate bit-refill change (about 13% faster inflate on Apple Silicon), exists only on the develop branch. Releases have lagged fixes before: the CVE-2022-37434 fix took about 7 months to ship.
- MinGW-w64 GCC builds at -O0/-Og with AVX2/AVX-512 enabled crash in the chunkset code because of GCC PR54412 (misaligned vector spills); issue #1874 is still open. Workarounds are -O1 or higher, or -Wa,-muse-unaligned-vector-move.
- Maintainers say zlib-ng uses a 4-byte minimum match where gzip allows 3, which can cost ratio on some binary data (#1922). A 2021 report (#947) found it slower than zlib on many tiny PNGs via LD_PRELOAD on a Raspberry Pi 4. The maintainers replied that zlib-ng is tuned for larger inputs.

## Known shortcomings

- README's '\~4x faster than stock zlib' has no stated method and is not reproduced: independent lzbench shows \~2.2-2.5x compression and \~1.5x decompression. Hard fork of madler/zlib; zlib-compat mode needed for drop-in use. Found in wave 7 for its SIMD CRC32/Adler-32; filed under wave 9's general-lossless category.
- Level -1 ratio is \~22% worse (deflate_quick static Huffman); output bytes differ from zlib; deflate uses more memory (\~350 KB); zlib-compat targets zlib 1.3.1. 2.3.1 had a Chorba CRC bug (wrong CRCs above 256 KB); newer inflate speedups are develop-only. No published numbers for the CRC32/Adler-32 gains. libdeflate is faster for whole-buffer decompression; zstd/LZ4 are faster if DEFLATE is not required.

## Caveats and trade-offs

The README's "about 4x" claim gives no CPU, compiler or flags, and lzbench does not reproduce it. lzbench shows about 2.2-2.5x faster compression and about 1.5x faster decompression than zlib 1.3.1, and at level -1 zlib-ng gets a clearly worse ratio (44.41% vs 36.45%). lzbench does not measure CRC32/Adler32 on their own, so the checksum SIMD gains rest only on first-party code (the Google Benchmark suite in the repo) with no published numbers. The lzbench results table used zlib-ng 2.2.3, while the current lzbench bundles 2.3.3.

Drop-in ABI-compatible replacement for zlib; installing system-wide risks breaking other software if misconfigured. CRC32/Adler32 SIMD paths require runtime CPU feature detection.

## Maintenance

Actively developed (last commit 2026-09-25; latest release 2.3.3 on 2026-02-03) under the permissive Zlib license, OSS-Fuzz-tested, and accepted as Fedora 40's system-wide zlib replacement (zlib-ng-compat).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. The README quote is verbatim but has no methodology. However, the well-known independent lzbench suite (public code, inikep/lzbench, 1.1k stars) benchmarks zlib-ng 2.2.3 against zlib 1.3.1 on Silesia, using gcc 14.2.0 on an AMD EPYC 9554, and zlib-ng wins at every level. It is not A because the page gives the compiler but not the build flags (they are only implicit in the Makefile defaults).
- **Verifier notes:** Metadata checked via gh: license Zlib, not archived, GitHub fork=false, 2100 stars, last commit 2026-09-25, so it is active. The README quote is accurate, but the tier is raised to B on the strength of the independent lzbench table. The claimed speedup is rewritten to lzbench's numbers, and the README's 4x is kept only as a quoted first-party claim.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `is_fork_of`, `caveats`
- **Shortcomings recorded by:** lzbench (EPYC 9554, GCC 14.2): zlib-ng 2.2.3 vs zlib 1.3.1 \~2.2-2.5x compress, \~1.5x decompress.; zlib-ng discussion #871: zlib-rs (Rust port based on zlib-ng) matches zlib-ng byte-for-byte and in speed; both are about 4.3x stock zlib on level 9 compress and 3.7x on decompress (derived from page data, flags unstated)
- **Pages the verifier opened:**
  - <https://github.com/zlib-ng/zlib-ng>
  - <https://github.com/zlib-ng/zlib-ng#readme>
  - <https://github.com/zlib-ng/zlib-ng/commits>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/inikep/lzbench#benchmarks>
  - <https://github.com/inikep/lzbench/blob/master/Makefile>
- **Sources the enricher read:**
  - <https://github.com/zlib-ng/zlib-ng>
  - <https://github.com/zlib-ng/zlib-ng#readme>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/PORTING.md>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/test/benchmarks/README.md>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/CMakeLists.txt>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/deflate.c>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/deflate.h>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/deflate_quick.c>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/deflate_medium.c>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/functable.c>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/zlib-ng.h.in>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/crc32.c>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/insert_string_p.h>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/inffast_tpl.h>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/chunkset_tpl.h>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/arch/generic/crc32_chorba_c.c>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/arch/x86/crc32_pclmulqdq_tpl.h>
  - <https://github.com/zlib-ng/zlib-ng/blob/develop/arch/arm/crc32_armv8_pmull_eor3.c>
  - <https://github.com/zlib-ng/zlib-ng/releases>
  - <https://github.com/zlib-ng/zlib-ng/security/advisories>
  - <https://github.com/zlib-ng/zlib-ng/discussions/2022>
  - <https://github.com/zlib-ng/zlib-ng/issues>
  - <https://github.com/zlib-ng/zlib-ng/issues/1922>
  - <https://github.com/zlib-ng/zlib-ng/issues/1874>
  - <https://github.com/zlib-ng/zlib-ng/issues/2318>
  - <https://github.com/zlib-ng/zlib-ng/issues/947>
  - <https://github.com/zlib-ng/zlib-ng/issues/1998>
  - <https://github.com/zlib-ng/zlib-ng/issues/1446>
  - <https://github.com/zlib-ng/zlib-ng/pull/2353>
  - <https://github.com/zlib-ng/zlib-ng/wiki>
  - <https://github.com/inikep/lzbench#benchmarks>
  - <https://github.com/ebiggers/libdeflate#readme>
  - <https://fedoraproject.org/wiki/Changes/ZlibNGTransition>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/zlib-ng/zlib-ng`) · [data/wave7/enrich/raw/github_com_zlib_ng_zlib_ng.json](../../../data/wave7/enrich/raw/github_com_zlib_ng_zlib_ng.json) (enrichment confidence 0.82)

</details>
