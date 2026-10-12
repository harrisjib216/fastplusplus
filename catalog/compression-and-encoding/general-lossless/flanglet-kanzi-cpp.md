# Kanzi (kanzi-cpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Multithreaded BWT/context-mixing/LZ compressor with nine presets; beats xz -9 on compress speed at similar or better ratio.

| | |
|---|---|
| **Beats** | xz |
| **Claimed result** | README (Ryzen 9 9950X, multithreaded): kanzi -l 7 compress 1150 ms / decompress 885 ms at 47,330,431 B vs xz 5.8.1 -9 43611 ms / 931 ms at 48,802,580 B (38x faster compress, derived from page data). lzbench 2.4 single thread (EPYC 9555P): kanzi 2.5.3 -7 10.8 MB/s compress at ratio 22.32% vs xz 5.8.4 -9 2.75 MB/s at 23.01% (3.9x, derived from page data); decompress 15.8 vs 122 MB/s (slower). |
| **Workload** | Compress and decompress silesia.tar vs xz, zstd, brotli, bzip2, gzip at matched ratios. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; README: AMD Ryzen 9 9950X 16-core, Ubuntu 26.04.1 |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 229 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/flanglet/kanzi-cpp) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

Independent lzbench 2.4 (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P, silesia.tar) measured kanzi 2.5.3 -7 compressing at 10.8 MB/s to 22.32% vs xz 5.8.4 -9 at 2.75 MB/s to 23.01% (about 3.9x faster), while decompressing at 15.8 vs 122 MB/s. The README's 38x figure (1150 ms vs 43611 ms on a Ryzen 9 9950X) pits multithreaded kanzi 2.6.0 against single-threaded xz, so most of that gap is parallelism.

## Use it when

- Backups, archives and one-off transfers where you control both ends and want xz -9 class ratio or better at a fraction of the compress time on a multicore box (README, Ryzen 9 9950X, silesia.tar: level 7 1150 ms vs xz -9 43611 ms, 47.3 MB vs 48.8 MB).
- Single-thread high-ratio compression faster than xz -9: lzbench 2.4 on EPYC 9555P has kanzi -7 at 10.8 MB/s vs xz -9 at 2.75 MB/s with a slightly smaller output.
- Text, UTF-8, x86 executables or DNA/FASTA data, where the built-in TEXT, UTF, EXE and DNA transforms help (wiki lzbench DNA table: kanzi -7 ratio 8.15% vs xz -5 7.64%, kanzi -9 7.02%).
- Data that needs block-level random access: the bitstream is seekable and --from/--to decode a range of blocks.
- Research or niche formats where you want to plug in a custom Transform&lt;T&gt; or entropy codec via the factory classes.

## Skip it when

- Read-heavy data (compress once, decompress many times): at levels 5-7 decompression is roughly symmetric with compression and far slower than xz or zstd per core (lzbench single thread: kanzi -7 15.8 MB/s vs xz -9 122 MB/s; zstd -19 decompresses silesia in 23 ms vs 885 ms for kanzi -7 in the README).
- Anything that must interoperate with standard tools or formats (gzip, xz, zstd, 7z): the output is only readable by Kanzi (Java/Go ports exist, but issue #39 found TPAQX and CM bitstreams differed between the Java and C++ 2.5.0 implementations).
- Low levels as a zstd replacement: on silesia.tar with 16 threads kanzi -2 (59/41 ms) is about the same ratio as zstd -T16 -2 (57/25 ms) and decodes slower; the wiki lzbench tables show zstd -1/-3 compressing faster.
- Levels 8-9 under latency or memory constraints: TPAQ/TPAQX run at 2-60 MB/s even with 16 threads and use 16-32 MiB blocks per thread.
- Untrusted or adversarial input without your own fuzzing: memory-safety bugs in decoders were found and fixed as recently as 2026 (issue #37 ROLZ out-of-bounds read, #36 TPAQ double free on 64 MiB+ blocks).

## How it is fast

Blocks (4 MiB default, 8-32 MiB at levels 6-9) are compressed and decompressed in parallel on worker threads, which is where most of the wall-clock win over single-threaded xz comes from. The mid and high levels use Burrows-Wheeler Transform pipelines (BWT+RANK/SRT+ZRLT with ANS0/FPAQ at levels 5-6; LZP+TEXT+UTF+BWT+LZP with a CM coder at level 7) instead of LZ77+LZMA's optimal parsing, and content-specific preprocessors (text dictionary, UTF, x86 EXE, DNA) raise ratio before entropy coding. Levels 8-9 use TPAQ/TPAQX context mixing and are symmetric and slow.

## Compared with alternatives

Pick Kanzi over xz, Fast LZMA2 or lrzip when you want LZMA-class or better ratio with much faster compression of a single stream and can live with slow, non-standard decompression; prefer LZHAM or zstd -19 when decompression speed matters more than compress time. Against bzip3 it is about equal single-threaded (lzbench: kanzi -7 10.8 MB/s at 22.32% vs bzip3 -5 11.9 MB/s at 22.29%) but offers a wider preset range and faster multithreaded runs (README: 1150 ms vs bzip3 -j16 2348 ms at similar size).

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (Makefile 'lib' target or CMake), plus CLI |
| **Dependencies** | none (pthreads/std::thread for multithreading) |
| **Minimum toolchain** | Builds as C++98 through C++20 per README (CMake defaults to C++17); multithreading needs C++11 and g++ 5+; MSVC 2008/2022/2026 solutions provided |
| **Platforms** | Linux, macOS, Windows, BSD; portable C++ with optional intrinsics (KANZI_USE_INTRINSICS off by default); armhf and i386 builds tested in issue #34 |
| **Thread safety** | Library parallelizes internally across blocks (job count parameter); per-stream objects are not documented as shareable across threads; custom transforms must be multi-thread safe per the wiki. |
| **Drop-in for the baseline** | no |

## Gotchas

- Both the Makefile and CMake (KANZI_ENABLE_NATIVE_OPTIMIZATIONS ON) build with -march=native by default, so a binary built on one machine may crash with illegal instructions on an older CPU; turn it off for distributable builds. Builds use -fno-rtti.
- The CLI uses half the available cores by default (max 64 jobs); -j 0 uses all cores, -j 1 forces single-threaded. Large default block sizes at levels 7-9 cap parallelism on small files.
- Bitstream compatibility is kept for releases (old versions decode), but development snapshots may break it; pin a release tag for stored data.
- It is a compressor, not an archiver: no file metadata, permissions or timestamps are kept, and checksums are optional (block-level 32/64-bit).

## Known shortcomings

- Tier B on the independent lzbench table (EPYC 9555P, gcc 15.2.0); compile flags are not on the page.
- Default builds use -march=native (Makefile and CMake KANZI_ENABLE_NATIVE_OPTIMIZATIONS ON), so binaries do not carry to older CPUs; the format is non-standard. Decoder memory-safety bugs were fixed only recently (#37 ROLZ out-of-bounds read, #36 TPAQ double free on 64 MiB+ blocks); #39: Java and C++ TPAQX/CM bitstreams incompatible in 2.5.0; #41 (odd lzbench 2.3 result) closed without explanation. lzbench figures are from 2.5.3 while the README shows 2.6.0.

## Caveats and trade-offs

The README comparison uses kanzi with threads versus single-thread xz, so the large README speedup is partly parallelism; the single-thread lzbench figures are the fair ones. At low levels kanzi is roughly on par with zstd, not clearly faster.

Context-modelling / BWT pipeline: much slower decompression than xz in single-thread lzbench (kanzi -7 15.8 vs xz 122 MB/s); multithreaded in its own CLI; high memory use at top levels.

## Maintenance

Actively maintained (commits in late September 2026, all 36 visible issues closed; issue #37 came from integrating Kanzi into 7-Zip-zstd) and Apache-2.0 with no dependencies, so it is easy to vendor as a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The well-known independent lzbench suite (public code, inikep/lzbench) lists kanzi 2.5.3 -7 at 10.8 MB/s compress, 15.8 MB/s decompress, 22.32% vs xz 5.8.4 -9 at 2.75 / 122 MB/s, 23.01%, using gcc 15.2.0 on a single thread of an EPYC 9555P. The page does not list compile flags (they are only implicit in the public Makefile, -O3 by default), so B as in earlier lzbench-based verdicts, not A.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** All README (Ryzen 9 9950X) and lzbench numbers in the record match the pages exactly. In the README table kanzi -l 7 (1150 ms, 47,330,431 B) also beats zstd 1.6.0 -T16 -19 (11090 ms, 52,830,213 B) on both speed and size; the decompression of kanzi at high levels is slower than xz in lzbench, as the record already says.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/flanglet/kanzi-cpp/HEAD/README.md>
  - <https://github.com/flanglet/kanzi-cpp>
  - <https://github.com/flanglet/kanzi-cpp/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/flanglet/kanzi-cpp/HEAD/README.md>
  - <https://github.com/flanglet/kanzi-cpp/wiki/Using-and-extending-the-code>
  - <https://github.com/flanglet/kanzi-cpp/wiki/q&a>
  - <https://github.com/flanglet/kanzi-cpp/wiki/Performance>
  - <https://github.com/flanglet/kanzi-cpp/issues?q=is%3Aissue>
  - <https://github.com/flanglet/kanzi-cpp/issues/41>
  - <https://github.com/flanglet/kanzi-cpp/issues/37>
  - <https://raw.githubusercontent.com/flanglet/kanzi-cpp/HEAD/src/app/BlockCompressor.cpp>
  - <https://raw.githubusercontent.com/flanglet/kanzi-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/flanglet/kanzi-cpp/HEAD/src/Makefile>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/flanglet/kanzi-cpp`) · [data/wave9/enrich/raw/github_com_flanglet_kanzi_cpp.json](../../../data/wave9/enrich/raw/github_com_flanglet_kanzi_cpp.json) (enrichment confidence 0.8)

</details>
