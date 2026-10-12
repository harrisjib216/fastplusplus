# bzip3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `LGPL-3.0 (bundled libsais/LZP code Apache-2.0)` · 🟢 active

> BWT plus context-mixing compressor (bzip2 successor) that compresses text 3-4x faster than xz -9 at slightly smaller size.

| | |
|---|---|
| **Beats** | xz |
| **Claimed result** | lzbench 2.4 (EPYC 9555P, single thread, silesia.tar): bzip3 1.5.4 -5 compress 11.9 MB/s at 22.29% vs xz 5.8.4 -9 2.75 MB/s at 23.01% (4.3x faster compress with smaller output, derived from page data) and vs xz -5 3.84 MB/s at 23.70% (3.1x, derived from page data); decompress 12.4 vs 122 MB/s (about 10x slower). Versus bzip2 1.0.8 -9 (12.7 / 35.5 MB/s, 25.75%) bzip3 -5 compresses slightly slower but smaller. README (Perl5 tarballs, WD Blue HDD): wall-clock decompression bzip3 (parallel) 4min 06s vs bzip2 9min 22s, xz 4min 40s, zstd 3min 51s; compression bzip3 -b 256 -j 12 7:10 vs xz -T16 -9 12:09, bzip2 -9 17:16, zstd -T12 -16 6:35, with output 1.00 GB vs xz 2.06 GB, zstd 3.08 GB, bzip2 3.44 GB. |
| **Workload** | Compress silesia.tar single thread via lzbench; project README compares bzip2, xz, zstd on Perl5 release tarballs. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 1.5k stars |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/kspalaiologos/bzip3) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In the independent lzbench 2.4 run (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P at 3.20 GHz, silesia.tar), bzip3 1.5.4 -5 compressed at 11.9 MB/s to 22.29% versus xz 5.8.4 -9 at 2.75 MB/s to 23.01% (about 4.3x faster and slightly smaller), but decompressed at 12.4 MB/s versus xz's 122 MB/s. The README's Perl-tarball numbers are first-party, multi-threaded wall-clock runs on an HDD with no CPU model.

## Use it when

- Archiving large text, logs, source trees or tarballs of code, where ratio matters and xz -9 compression is too slow (lzbench silesia: 11.9 MB/s vs 2.75 MB/s, 22.29% vs 23.01%).
- Replacing bzip2 for cold storage: similar compression speed but 13% smaller output on silesia (22.29% vs 25.75%) and smaller on every file in the project's corpus.
- Multi-core batch compression with large blocks (-b up to 511 MiB, -j workers), where per-block parallelism gives the README's 7:10 vs xz -T16 12:09 and half the size on Perl tarballs.
- Write-once, read-rarely data where a decompression speed near compression speed (about 10-14 MB/s per thread) is acceptable.

## Skip it when

- Read-heavy data: single-thread decompression is about 10x slower than xz (12.4 vs 122 MB/s) and two orders of magnitude slower than zstd or LZ4.
- Binary, already-compressed or media data; the README says it excels at text or code, and BWT/CM gains shrink on other inputs.
- When interoperability matters: the .bz3 format is read only by bzip3, and both the format details (CRC change in 1.3.0/1.3.1) and the library ABI (1.5.0) have broken in recent releases.
- Memory-constrained hosts: each state allocates about 5x the block size (swap buffer, 4-byte suffix array, LZP table) and the README's -b 256 -j 12 run used 18.3 GB; parallel modes multiply that per thread.
- Streaming APIs: there is no incremental zlib-style stream interface; callers frame blocks themselves or buffer whole inputs (issue #171 asks for a memory-to-memory multi-threaded API).

## How it is fast

Each block passes through a run-length coder, then an LZP pass (hashed order-4 context, 2^18-entry table, minimum match 40 bytes) that removes long repeats before sorting, then a Burrows-Wheeler transform built with Ilya Grebnov's libsais (SA-IS suffix-array construction), then a bitwise arithmetic coder that mixes order-0/order-1/order-2 probability counters with a run-dependent secondary table (derived from Ilya Muravyov's BWT post-coder). Removing long matches before the BWT and coding with a small CM model instead of LZMA's optimal parsing gives xz-level ratio at roughly 4x xz -9's compression speed. Blocks are independent, so the CLI and the block API scale across threads.

## Compared with alternatives

Pick bzip3 over Fast LZMA2 or xz when compression time and ratio on text matter more than decompression speed; Kanzi -7 lands at almost the same point in lzbench (10.8 / 15.8 MB/s, 22.32%) under a permissive license and with more levels, so prefer Kanzi if LGPL-3.0 is a problem or you need to trade ratio for speed. For anything read often, zstd or LZ4 decompress far faster.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libbz3) plus CLI; autotools or CMake |
| **Dependencies** | none at runtime beyond libc; pthreads optional for the parallel block API (bundled libsais and LZP code) |
| **Minimum toolchain** | C99; CMake 3.13+ or autotools |
| **Platforms** | Portable C; tested on x86, x86_64, armv6, armv7, aarch64, ppc64le, mips, mips64, sparc, s390x; Windows builds exist but the README says Windows and 32-bit builds can be considerably slower |
| **Thread safety** | One bz3_state per thread; bz3_encode_blocks/bz3_decode_blocks take an array of states and spawn one pthread per block (2-16). Sharing a state across threads is not documented as safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- The repository moved to github.com/iczelia/bzip3 (NEWS v1.5.3; kspalaiologos/bzip3 redirects); 1.5.0 changed bz3_encode_block/bz3_decode_block signatures and the soname, so older callers must be updated.
- Archives written by 1.3.0 and 1.3.1 carry a wrong CRC and fail normal decompression in later versions; 'bzip3 -rd' (recovery mode, 1.3.2) restores them.
- Fuzzing found heap overflows in the 1.2.2 decoder (issue #94, CVE-2023-29421 per a search result; issue #97 in bz3_decompress); NEWS lists security fixes in 1.2.3 and libsais-related security fixes in 1.3.0 with 'updating is strongly encouraged'. Do not decode untrusted input with old versions.
- Speed depends heavily on the compiler (README: clang 13 x64 Linux reaches about 17 MiB/s compress and 23 MiB/s decompress per thread); release binaries are built without -march=native, and the CMake option BZIP3_ENABLE_ARCH_NATIVE is off by default. In lzbench the -9 setting gives a worse ratio than -5 (23.00% vs 22.29%).

## Known shortcomings

- Tier C: the win over bzip2 comes from multithreading; single-thread compression is slower than bzip2 (Calgary 265 vs 173 ms, Linux 77 vs 62 s). The real win is ratio-adjusted: Silesia in 17.5 s vs lzma -9 77 s and zstd -19 83 s at smaller output.
- Tier B on lzbench 2.4 (EPYC 9555P, gcc 15.2.0, flags unstated): 11.9 vs xz -9 2.75 MB/s at 22.29% vs 23.01%; the README decompress row is 'bzip3 (parallel)'. LGPL-3.0 plus Apache-2.0 libsais.
- Decompression is 12.4 vs xz 122 MB/s. Archives from 1.3.0/1.3.1 have a CRC break (need bzip3 -rd); ABI/soname break in 1.5.0; fuzzing found heap overflows in the 1.2.2 decoder (issue #94, CVE-2023-29421 per snippet), fixed in 1.2.3/1.3.0. Each state allocates about 5x the block size (the README run used 18.3 GB); lzbench -9 ratio is worse than -5 (23.00 vs 22.29%); Kanzi -7 lands at the same point in lzbench (10.8/15.8 MB/s, 22.32%). Repo moved to iczelia/bzip3.

## Caveats and trade-offs

Claim is compress-time and ratio versus xz and bzip2 (bzip2 is outside the list); decompression is about 10x slower than xz in lzbench. README Perl numbers are multi-threaded wall-clock on an HDD with no CPU model, and the README says speed is heavily compiler-dependent. lzbench compile flags are not stated on the page.

BWT plus context mixing; strongest on text and source; decompression is about 10x slower than xz in single-thread lzbench. Bundled libsais and LZP parts are Apache-2.0; core is LGPL.

## Maintenance

Actively maintained (1.5.4 released 2026-09-07, last commit 2026-09-09) under LGPL-3.0 with Apache-2.0 libsais/LZP parts; the format and ABI have changed in recent releases, so pin a version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent lzbench suite (public code, inikep/lzbench; gcc 15.2.0 release binary; single thread of an AMD EPYC 9555P) lists bzip3 1.5.4 -5 at 11.9 / 12.4 MB/s, 22.29% vs xz 5.8.4 -9 at 2.75 / 122 MB/s, 23.01%; compile flags are not on the page, so B, not A (consistent with kanzi-cpp and lzav in batch-08).
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** All lzbench numbers match the README rows; metadata confirmed (1.5k stars, last commit 2026-09-09, not a fork). Small correction: the README's 4m06s decompression row is labelled 'bzip3 (parallel)', not '-b 256'.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/kspalaiologos/bzip3>
  - <https://github.com/kspalaiologos/bzip3/commits>
  - <https://raw.githubusercontent.com/kspalaiologos/bzip3/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/kspalaiologos/bzip3>
  - <https://raw.githubusercontent.com/kspalaiologos/bzip3/HEAD/README.md>
  - <https://raw.githubusercontent.com/kspalaiologos/bzip3/HEAD/include/libbz3.h>
  - <https://raw.githubusercontent.com/iczelia/bzip3/HEAD/NEWS>
  - <https://raw.githubusercontent.com/iczelia/bzip3/HEAD/etc/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/iczelia/bzip3/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/iczelia/bzip3/HEAD/src/libbz3.c>
  - <https://github.com/iczelia/bzip3/issues>
  - <https://github.com/iczelia/bzip3/issues/94>
  - <https://github.com/iczelia/bzip3/releases>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/kspalaiologos/bzip3`) · [data/wave9/enrich/raw/github_com_kspalaiologos_bzip3.json](../../../data/wave9/enrich/raw/github_com_kspalaiologos_bzip3.json) (enrichment confidence 0.85)

</details>
