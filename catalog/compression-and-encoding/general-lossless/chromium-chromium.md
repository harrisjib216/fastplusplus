# Chromium zlib (third_party/zlib fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Zlib` · 🟢 active

> Chromium's zlib fork with SIMD CRC-32, Adler-32, chunk-copy inflate and a faster deflate hash; API-compatible, faster than madler/zlib.

| | |
|---|---|
| **Beats** | zlib (upstream madler/zlib) |
| **Claimed result** | CRC-32 5x-25x faster than zlib's default BYFOUR crc32; gzip- and zlib-wrapped inflate 69% and 50% faster on the snappy corpus; PNG 140 corpus decoding rate 4% faster on average from crc32 alone, 40% total combined with adler32 SIMD and inflate chunk copy. Later commits report gains over the previous Chromium zlib, not upstream: the ANZAC++ hash gives 30-40% faster compression (M1 31.3%, SPR 41.9%; 0.1% ratio loss on snappy) and overlapped bitstream refill gives an 8.09% average inflate gain across 7 CPUs (EPYC 9B45 7.86%, EPYC 9B14 11.21%, Xeon 8481C 6.16%, Axion 8.89%, Ryzen 9 9900X 8.77%, Cortex-X3 5.53%, Cortex-X4 10.13%). |
| **Workload** | Inflate of gzip and zlib-wrapped streams (snappy corpus), raw CRC-32, and PNG decoding with SSE4.2/PCLMUL crc32, adler32 SIMD and chunk-copy inflate. |
| **Metric** | throughput |
| **Compiler and flags** | SSE4.2 and PCLMUL for the SIMD crc32 code (selected at run time); since Aug 2026 the SIMD ISA is set per function via __target__. Benchmark compiler and flags not stated in the commits. |
| **Adoption** | Ships in Chrome; github.com/chromium/chromium mirror 24.9k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/chromium/chromium/tree/main/third_party/zlib) · [benchmark](https://github.com/chromium/chromium/commit/65e2abcb74b1c07fa14f46abaa1fb1717892eec3) |

## Verdict

Chromium's 2018 commit 65e2abcb reports SSE4.2+PCLMUL CRC-32 at 5x-25x zlib's BYFOUR crc32, with gzip- and zlib-wrapped inflate 69% and 50% faster on the snappy corpus and PNG decoding 40% faster combined with SIMD Adler-32 and chunk copy; it gives no CPU, compiler or flags (details on blocked crbug.com/796178). The 2026 commits (refill overlap 8.09% average inflate gain across 11 CPUs; SWAR compare256 9.6% average deflate gain at levels 1/6/9 across 10 CPUs) name CPUs but compare against the previous Chromium zlib, not upstream. Independently, Volker Simonis's zlib-chromium README reports more than 50% faster inflate than madler/zlib on Silesia and Calgary (i7-8650U fixed at 1900 MHz, zbench.c, LD_PRELOAD, Chromium rev 3fc79233, Feb 2022), shown as graphs only.

## Use it when

- Inflate-heavy workloads (PNG, HTTP gzip/deflate, zip extraction) on x86-64 or arm64 where you must keep the zlib API
- gzip streams where CRC-32 cost matters: the SIMD CRC is 5x-25x faster than zlib's BYFOUR table code per the 2018 commit
- Projects that already build with GN/Chromium tooling or AOSP, or that can vendor the CMake build with ENABLE_SIMD_OPTIMIZATIONS=ON
- When you want a zlib that is fuzzed (OSS-Fuzz, inflate_fuzzer.cc) and ships to billions of Chrome and Android installs

## Skip it when

- You need byte-identical deflate output to canonical zlib (reproducible archives, delta updates): the default ANZAC++ hash changes the output unless built with USE_ZLIB_RABIN_KARP_HASH / CHROMIUM_ZLIB_NO_CASTAGNOLI
- Your code assumes inflate writes nothing past the produced bytes: chunk copies may scribble on next_out beyond the decoded data, up to avail_out (this broke OpenJDK tests and Spring/ASM when Java ran on it)
- You want a turnkey, versioned library: there are no releases, the code lives in a monorepo mirror, and zconf.h says building outside Chromium is not guaranteed to keep working; zlib-ng or libdeflate are easier to package
- Maximum speed regardless of API: libdeflate (whole-buffer) and ISA-L igzip are faster for one-shot (de)compression, and zlib-ng is the more widely packaged drop-in
- Big-endian or exotic targets: the hash is 'validated for little endian archs', and the SIMD paths cover only x86, Arm and RISC-V (CMake)

## How it is fast

On inflate, contrib/optimizations/inffast_chunk.c replaces byte-wise match copies with 16-byte SSE2/NEON chunk copies (chunkcopy.h), reads input 64 bits at a time (INFLATE_CHUNK_READ_64LE), and since 2026-09 issues the bit-buffer refill after the Huffman table lookup so the two loads overlap. Checksums use carry-less-multiply folding (SSE4.2+PCLMUL, optional AVX-512 VPCLMULQDQ, Armv8 CRC32/PMULL) for CRC-32 and SSSE3/NEON/RVV for Adler-32, chosen once at run time by cpu_features.c. On deflate, the ANZAC++ multiplicative 4-byte hash (insert_string.h) replaces the Rabin-Karp rolling hash, with SIMD slide_hash and a 64-bit SWAR compare256 in longest_match.

## Compared with alternatives

Pick it over zlib-ng or Cloudflare zlib when you already build Chromium/AOSP code or want the exact zlib Chrome ships, with its fuzzing and per-CPU tuning. Pick zlib-ng for a packaged, versioned zlib-compatible library, and libdeflate when you can drop the streaming API for whole-buffer speed.

## Integration

| | |
|---|---|
| **Form** | static lib (GN component 'zlib' / CMake static or shared library) |
| **Dependencies** | none outside libc; pthread for run-time CPU detection on POSIX; Android builds need the NDK cpu_features |
| **Minimum toolchain** | C (K&R-compatible zlib sources) built with GN/clang in Chromium; CMake 3.12+ for the standalone build; per-function __target__ attributes need GCC or clang for the SIMD paths (MSVC Windows-on-Arm optimizations disabled) |
| **Platforms** | x86/x86-64 (SSE2, SSSE3, SSE4.2+PCLMUL detected at run time; AVX-512 CRC opt-in), arm/arm64 (NEON, CRC32, PMULL), riscv64 (RVV, CMake only); portable C fallback elsewhere; iOS x86 simulator builds without SIMD |
| **Thread safety** | Same as zlib: one z_stream per thread; CPU feature detection runs once through pthread_once / InitOnceExecuteOnce |
| **Drop-in for the baseline** | partial — same zlib.h API and valid DEFLATE streams, but symbols are renamed to Cr_z_\* by default, deflate output bytes differ from madler/zlib, and inflate may overwrite unused output-buffer space |

## Gotchas

- contrib/optimizations/inflate.c is a hand-maintained copy of inflate.c: the zlib 1.3.2 update (2026-02/03) missed upstream fix madler/zlib@f7d01aa, which left state-&gt;distcode stale after inflateCopy() (the regression test shows SIGILL when a fixed Huffman block switches to a dynamic one). It was fixed 2026-04-17 in commit 296866e, so fixes to upstream inflate.c can lag here.
- AVX-512 CRC (CMake ENABLE_SIMD_AVX512, off by default) is enabled from XCR0 bit 6 alone (`_xgetbv(0) & 0x40`), with no CPUID check for AVX512F or VPCLMULQDQ and no OSXSAVE check. Read from the source, not tested: on AVX-512 CPUs without VPCLMULQDQ (Skylake-SP/Cascade Lake) this likely faults with SIGILL. The same path failed to build with GCC until commit 53a2b53 (2026-08-31) added pclmul to the target attribute.
- The x86 SIMD CRC is used only after cpu_check_features() has run, which happens in deflateInit/inflateInit or on the zlib-convention call crc32(0, NULL, 0); a program that calls crc32(crc, buf, len) cold gets the portable path.
- With the Chromium hash, hash_bits is forced to at least 15, so a low memLevel no longer shrinks the hash table, and deflateBound() always returns the conservative stored/fixed bound.

## Known shortcomings

- Evidence is Chromium's own commit 65e2abcb numbers (crc32 5x-25x, inflate 69%/50%, PNG 4%/40%); later commits name CPUs but measure against older Chromium zlib, not upstream. Distinct fork (own SIMD, chunk-copy and ANZAC++ code), not folded into zlib-ng or Cloudflare zlib. The code lives under third_party/zlib inside the Chromium tree, so extraction is manual.
- The hand-copied contrib/optimizations/inflate.c missed the upstream fix madler/zlib@f7d01aa in the 1.3.2 update (stale distcode after inflateCopy), fixed 2026-04-17 in commit 296866e. The opt-in AVX-512 CRC is enabled on XCR0 bit 6 alone with no CPUID AVX512F/VPCLMULQDQ or OSXSAVE check, so likely SIGILL on Skylake-SP/Cascade Lake (read from source, not tested). Not bit-identical to canonical zlib (ANZAC++ hash); symbols renamed Cr_z_\* by default; chunk copy may write past produced bytes within avail_out; hash_bits forced to at least 15. The 2026 commit gains are measured against prior Chromium zlib, not upstream. An independent run exists in simonis/zlib-chromium (i7-8650U at 1900 MHz, zbench.c, Silesia/Calgary, Feb 2022, over 50%, graphs only).

## Caveats and trade-offs

Headline numbers come from a first-party commit message (the 2018 SSE4.2 crc32 change) with no CPU model, compiler or flags; its details are on crbug.com/796178, which was blocked here. Newer commits (ANZAC++ hash 2023, bitstream-refill overlap 2026-09-22) name CPUs but measure against the previous Chromium zlib, not upstream madler/zlib, and do not state the tool or flags. A public harness exists at third_party/zlib/contrib/bench/zlib_bench.cc. This is a distinct fork from Cloudflare zlib (an independent fork) and zlib-ng (a separate project that adopted some Chromium ideas such as chunk copy), with its own code (\*simd\* files, contrib/optimizations) and its own evidence, so it is not a duplicate. The repo URL is the whole Chromium mirror; the code is in third_party/zlib (canonical: chromium.googlesource.com/chromium/src/third_party/zlib). Synced to zlib 1.3.2.

Tied to Chromium's build (BUILD.gn, runtime CPU detection, symbol renaming via names.h); x86, Arm and RISC-V SIMD paths; heavily patched inflate (inffast_chunk) means it does not track upstream zlib cleanly.

## Maintenance

Actively maintained by Chromium (last zlib commit 2026-09-22, synced to zlib 1.3.2) under the Zlib licence (Chromium-original files carry BSD-style Chromium headers); there are no tagged releases, so you vendor a snapshot of third_party/zlib or the CMake build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Commit 65e2abcb (Noel Gordon) states raw crc32 is 5x-25x faster than zlib's default BYFOUR crc32, gzip- and zlib-wrapped inflate are 69% and 50% faster on the snappy corpus, and PNG 140 corpus decoding is 4% faster (40% combined with adler32 SIMD and chunk copy). It gives no CPU model or flags, and its details sit on crbug.com/796178, which is blocked. The public harness third_party/zlib/contrib/bench/zlib_bench.cc exists, but the commit does not tie it to a stated CPU and flags, so first-party C.
- **Verifier notes:** Kept as a distinct fork: it has its own SIMD crc32/adler32, chunk-copy inflate and ANZAC++ hash, its own commit evidence, and still ships in Chrome. License Zlib per README.chromium; last commit 2026-09-22 verified. The 24.9k-star figure for the mirror was not rechecked. Consider pointing repo_url at https://github.com/chromium/chromium/tree/main/third_party/zlib.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party commit messages
- **Pages the verifier opened:**
  - <https://github.com/chromium/chromium/commit/65e2abcb74b1c07fa14f46abaa1fb1717892eec3>
  - <https://github.com/chromium/chromium/commits/main/third_party/zlib>
  - <https://github.com/chromium/chromium/commits/main/third_party/zlib/contrib/optimizations>
  - <https://github.com/chromium/chromium/commit/ea7f42038188e90cbb8884160c980f9c679c7440>
  - <https://github.com/chromium/chromium/commit/e1a960f284b6f81eddb6b04eccd4f81dd07d6c95>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/README.chromium>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/contrib/bench/zlib_bench.cc>
- **Sources the enricher read:**
  - <https://github.com/chromium/chromium/commits/main/third_party/zlib>
  - <https://github.com/chromium/chromium/commit/65e2abcb74b1c07fa14f46abaa1fb1717892eec3>
  - <https://github.com/chromium/chromium/commit/ea7f42038188e90cbb8884160c980f9c679c7440>
  - <https://github.com/chromium/chromium/commit/dc2f437>
  - <https://github.com/chromium/chromium/commit/296866e>
  - <https://github.com/chromium/chromium/commit/53a2b53>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/README.chromium>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/BUILD.gn>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/zconf.h>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/chromeconf.h>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/cpu_features.c>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/crc32.c>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/crc32_simd.c>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/crc32_simd.h>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/deflate.c>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/contrib/optimizations/insert_string.h>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/contrib/optimizations/inffast_chunk.c>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/contrib/optimizations/inflate.c>
  - <https://raw.githubusercontent.com/chromium/chromium/HEAD/third_party/zlib/contrib/bench/zlib_bench.cc>
  - <https://github.com/simonis/zlib-chromium>
  - <https://raw.githubusercontent.com/simonis/zlib-chromium/HEAD/README.md>
  - <https://raw.githubusercontent.com/simonis/zlib-bench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/chromium/chromium`) · [data/wave9/enrich/raw/github_com_chromium_chromium.json](../../../data/wave9/enrich/raw/github_com_chromium_chromium.json) (enrichment confidence 0.8)

</details>
