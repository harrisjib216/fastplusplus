# nadavrot/memset_benchmark (AVX2 assembly memset and memcpy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Assembly (x86-64 AVX2, AT&T .S) with C/C++ harness` · `no license` · 🔴 abandoned

> Small-size-tuned AVX2 x86-64 assembly memset and memcpy that beat glibc, Folly and musl on 0-511 byte calls.

| | |
|---|---|
| **Beats** | glibc memset and memcpy (with and without PLT indirection, 'libc@plt' and 'libc'), also musl and folly (memcpy chart) |
| **Claimed result** | README text: 'These implementations outperform the folly and glibc implementations.' Random-size chart values (README image, time units not stated, lower is better): memset libc@plt 24344, libc 20172, asm_memset 14295 (about 1.41x faster than libc, derived from chart data); memcpy libc@plt 28285, libc 25263, folly 23969, asm_memcpy 21547 (about 1.17x faster than libc, derived from chart data). |
| **Workload** | README charts: (1) random-size batches, 10M calls x 20 samples (median), size and destination offset each drawn from a pre-computed random u8 sequence (0 to 255 bytes), nop-function call overhead subtracted; memset compares libc@plt, libc and asm_memset, memcpy compares libc@plt, libc, folly and asm_memcpy. (2) Hot-loop fixed-size sweeps for sizes 0 to 511 bytes (16-byte aligned buffer, 10M calls per size), memset against musl, libc@plt and libc-direct, memcpy against libc@plt, libc-direct and folly. memset always writes value 0. |
| **Metric** | latency |
| **Hardware** | Not stated (x86-64 with AVX2 required by impl.S; CPU model not given) |
| **Compiler and flags** | Harness built with CMake: add_compile_options(-Wall -g3 -O3 -march=native) (CMakeLists.txt); the assembly files are not compiler-dependent; glibc version not stated. |
| **Adoption** | 344 stars, 18 forks; the memset was upstreamed into Folly as folly/memset.S (commit 0ec02d4, 2022-01-05, 'asm memset implementation' by Ilya Albrecht, citing this repo and Nadav Rotem), with folly/test/MemsetBenchmark.cpp comparing std memset and __folly_memset (no published numbers) |
| **Last commit** | 2022-01-10 |
| **Links** | [repository](https://github.com/nadavrot/memset_benchmark) · [benchmark](https://github.com/nadavrot/memset_benchmark) |

## Verdict

On one unnamed AVX2 CPU with an unstated late-2021 glibc (issue #5 asking for both was never answered), the random-size benchmark (sizes and offsets 0-255, 10M calls, median of 20 samples, nop-call overhead subtracted) gives memset: glibc direct 20,172, via PLT 24,344, asm 14,295 (1.41x vs direct, derived from chart data); memcpy: glibc direct 25,263, Folly 23,969, asm 21,547 (1.17x, derived). The harness Stopwatch reports microseconds, so these read as about 2.0 vs 1.4 ns per memset call and 2.5 vs 2.2 ns per memcpy call (derived, assuming the charts plot the harness output); the only outside run (issue #6, 2023, Ivy Bridge i3-3210 without AVX2) timed the C huge_memset, not the assembly, and found musl faster.

## Use it when

- x86-64 code with AVX2 whose profile is dominated by short (0-512 byte), variable-length memset or memcpy calls you can route to a dedicated function, e.g. serialization, IPC message parsing, small-object zeroing.
- As a reference design when writing your own short-size memset/memcpy: the size-class tree and overlapping-store tricks are easy to read and the repo's exhaustive tester (sizes 0-1023, all small offsets, guard bytes) is reusable.
- If you already build Folly with AVX2 enabled: use __folly_memset (this memset plus a rep stosq path for fills of 4 KiB and up, licensed Apache-2.0) instead of the unlicensed original.
- To find out whether your own program's calls are short enough to benefit, via the repo's LD_PRELOAD length-histogram tool.

## Skip it when

- Buffers above 511 bytes were never measured, and the code has no rep stosb/rep movsb, non-temporal store or prefetch path; for multi-kilobyte and larger fills or copies glibc's ERMS/non-temporal paths (and Folly's rep stosq branch, added when it upstreamed this memset) are the safer choice.
- Overlapping buffers: asm_memcpy is plain memcpy and is not overlap-safe above 128 bytes, whereas glibc's x86-64 memcpy is its memmove entry (the README's own backtrace shows __memmove_avx_unaligned_erms) and Folly's memcpy detects overlap; swapping it in can expose latent overlap bugs.
- CPUs without AVX2 (asm_memset uses vpbroadcastb; asm_memcpy needs AVX) or the Windows x64 ABI: there is no CPUID dispatch and the code assumes System V argument registers (rdi, rsi, rdx); Linux and macOS symbol variants only.
- Anything that needs a license: the repository has no LICENSE file, so the code is all-rights-reserved reference material; only the memset has a licensed copy (Folly).
- memcpy sizes of roughly 155-195 bytes (Folly faster) and 190-255 bytes (glibc called directly faster), as read from the author's own fixed-size chart (docs/memcpy_bench.png).

## How it is fast

Both routines branch on size class and cover each class with two possibly overlapping unaligned stores (1-4, 4-8, 8-16, 16-32, 32-64 bytes, then three or four 32-byte stores up to 128), so a short call costs a couple of compares and two stores with no loop or tail handling. Memsets above 176 bytes store one unaligned head, then 32-byte-aligned vmovdqa stores unrolled five-wide, then one unaligned tail; larger memcpys run a 128-byte loop of four unaligned ymm loads/stores and finish with up to three 32-byte copies plus an overlapping last word. The design follows Joe Bialek's MSRC write-up on Windows memset and targets the short-length distribution the author measured in Chrome and other programs.

## Compared with alternatives

Pick it (or rather Folly's __folly_memset) over fancy-memset or Agner Fog's asmlib when the workload is short variable-length calls on AVX2 hardware and you want a tiny, readable size-class design; asmlib offers CPU dispatch and a full string-function set but its numbers are against glibc 2.7/2.8, and DPDK's rte_memcpy is the maintained, licensed choice for small cache-resident copies.

## Integration

| | |
|---|---|
| **Form** | source-drop (one .S file per function; harness built with CMake) |
| **Dependencies** | none for the functions; CMake 3.7+ and a C++14 compiler for the tester and benchmark |
| **Minimum toolchain** | GNU as or clang's integrated assembler (AT&T syntax, C preprocessor for .S); harness C++14 |
| **Platforms** | x86-64 Linux and macOS, System V ABI; AVX2 required for memset, AVX for memcpy |
| **Thread safety** | Reentrant: leaf functions with no global state (read from the source; not documented) |
| **Drop-in for the baseline** | partial — same signatures and return values as memset/memcpy but exported as asm_memset/asm_memcpy; no runtime dispatch, memcpy is not memmove-safe, and the repo's proxy shim forwards memset to the C local_memset, not the assembly |

## Gotchas

- Harness flaw in the headline 'random sizes' benchmark: offsets and sizes come from one fixed 320-byte table (include/utils.h DoomRNG) that is reset every sample; memset draws two bytes per call, so the same 160 (offset, size) pairs repeat 62,500 times in each 10M-call sample (memcpy draws three, a 320-call cycle). Branch predictors with long histories can learn much of a cycle that short, so the README's claim that this benchmark 'takes into account mispredicted branches' is optimistic; every implementation sees the same sequence, so the ranking is fair but the gap on genuinely random sizes is unmeasured. Hacker News commenters made the same priming criticism (search snippet of thread 29197161; the thread itself was not opened).
- The 'musl' curve in the fixed-size memset chart is musl's portable C memset copied into src/memset/impl.c and compiled by the harness with -O3 -march=native, not the x86_64 assembly memset.s that musl actually ships (rep stosq above 126 bytes), so it does not represent musl libc on x86-64. 'libc' is &memset called directly and 'libc@plt' adds a jmp trampoline through the PLT; the direct column is the fair glibc comparison.
- The README says the proxy tool swaps memset and memcpy, but src/memset/shims.c overrides only memset and forwards it to the C local_memset, not asm_memset; LD_PRELOAD experiments with it do not exercise the assembly.
- The impl.S files carry no .note.GNU-stack section (nor .type/.size/CFI), so GNU ld marks a binary linking them as needing an executable stack; Folly fixed this in its copy (commit 0b150f5, #1814, 2022-07-11). Fixed-size sweeps use only 16-byte-aligned buffers at offset 0 with identical source and destination alignment.

## Known shortcomings

- Chart values match (memset 1.41x, memcpy 1.17x over direct libc) but there is no LICENSE (the Folly memset.S is the Apache-2.0 route), no CPU, compiler or glibc version, and glibc direct matches or beats asm_memcpy around 165-250 bytes. Abandoned since 2022-01-10.
- Harness flaw: the 'random' sizes come from a fixed 320-byte DoomRNG table reset every sample; memset draws two bytes per call, so the same 160 (offset, size) pairs repeat 62,500 times per 10M-call sample and branch predictors can learn it, so the README's mispredict claim is optimistic (the ranking stays fair since every implementation sees the same sequence). The 'musl' row is musl's generic C memset compiled -O3 -march=native, not the shipped x86_64 memset.s (rep stosq above 126 B); the proxy shim overrides only memset and forwards to the C local_memset, not the asm; impl.S lacks .note.GNU-stack (Folly fixed its copy in #1814); asm_memcpy is not overlap-safe above 128 B while the glibc and Folly comparators are. Chart units are microseconds per 10M calls, about 2.0 vs 1.4 ns per memset call (derived). The only outside run (issue #6, Ivy Bridge) timed the C huge_memset, not the asm, and musl was fastest there.

## Caveats and trade-offs

Results exist only as README chart images from the author's own run (values read from the images; time units not stated). CPU model, compiler and glibc version are not stated (charts date from November 2021, so glibc of that era); CMakeLists.txt uses -O3 -march=native. The repository has no LICENSE file, so its code is reference only; the Folly copy of the memset (folly/memset.S, Apache-2.0 header, AVX2-gated with a std memset fallback in FollyMemset.cpp) is the licensed route, while the memcpy was not upstreamed by that commit. The fixed-size memcpy sweep is not a uniform win: glibc direct is at or below asm_memcpy around 165 to 250 bytes (read from docs/memcpy_bench.png), and musl beats the asm memset at size 0. The random-size benchmark uses one fixed pseudo-random sequence replayed every sample. The charts predate the final memset change (2021-11-29, removal of a second exit block). Last commit 2022-01-10.

x86-64 with AVX2 only (vmovdqu/ymm; Apple and Linux symbol variants); tuned for the short-buffer size distribution seen in Chrome, Python and server workloads rather than for large copies; includes exhaustive correctness tester, histogram LD_PRELOAD tool and a proxy tool that swaps builtin memset/memcpy with the local code.

## Maintenance

Abandoned since 2022-01-10 (110 commits, 344 stars, 3 open issues unanswered) and unlicensed, so treat it as reference; the memset lives on, licensed and maintained, as folly/memset.S, while the memcpy was never upstreamed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README charts (docs/memset_r.png, docs/memcpy_r.png, docs/memset_bench.png, docs/memcpy_bench.png) compare against glibc (via PLT and direct), musl and folly; the harness is public (src/memset/bench_memset.cc, src/memcpy/bench_memcpy.cc) and CMakeLists.txt gives -O3 -march=native -g3, but the compiler, glibc version and CPU model are never stated, so not A.
- **Verifier notes:** Chart values match the record exactly (memset 24344/20172/14295; memcpy 28285/25263/23969/21547), so the 1.41x and 1.17x derived ratios over direct libc hold. Tier C stays: public harness and flags, but no compiler, glibc version or CPU model. Shortcomings: no license (use Folly's Apache-2.0 memset.S), author-only measurements, memcpy loses to glibc in some size ranges, abandoned since 2022.
- **Fields the verifier corrected:** `workload`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-28 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/nadavrot/memset_benchmark>
  - <https://github.com/nadavrot/memset_benchmark/commits>
  - <https://github.com/nadavrot/memset_benchmark/tree/main/src/utils>
  - <https://github.com/nadavrot/memset_benchmark/tree/main/src/memset>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memset_r.png>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memcpy_r.png>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memset_bench.png>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memcpy_bench.png>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/bench_memset.cc>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/impl.S>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/impl.S>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/bench_memcpy.cc>
  - <https://raw.githubusercontent.com/facebook/folly/main/folly/memset.S>
  - <https://github.com/facebook/folly/commits/main/folly/memset.S>
  - <https://github.com/facebook/folly/commit/0ec02d4830c9d67987d7c71e52f8283217071c35>
- **Sources the enricher read:**
  - <https://github.com/nadavrot/memset_benchmark>
  - <https://github.com/nadavrot/memset_benchmark/commits/main>
  - <https://github.com/nadavrot/memset_benchmark/issues?q=is%3Aissue>
  - <https://github.com/nadavrot/memset_benchmark/issues/3>
  - <https://github.com/nadavrot/memset_benchmark/issues/4>
  - <https://github.com/nadavrot/memset_benchmark/issues/5>
  - <https://github.com/nadavrot/memset_benchmark/issues/6>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/include/utils.h>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/include/decl.h>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/include/types.h>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/impl.S>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/impl.c>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/shims.c>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/bench_memset.cc>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/test_memset.cc>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memset/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/impl.S>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/impl.c>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/folly.S>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/bench_memcpy.cc>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/test_memcpy.cc>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/src/memcpy/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memset_r.png>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memcpy_r.png>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memset_bench.png>
  - <https://raw.githubusercontent.com/nadavrot/memset_benchmark/HEAD/docs/memcpy_bench.png>
  - <https://raw.githubusercontent.com/facebook/folly/main/folly/memset.S>
  - <https://raw.githubusercontent.com/facebook/folly/main/folly/FollyMemset.cpp>
  - <https://github.com/facebook/folly/commits/main/folly/memset.S>
  - <https://raw.githubusercontent.com/kraj/musl/master/src/string/x86_64/memset.s>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/nadavrot/memset_benchmark`) · [data/wave13/enrich/raw/github_com_nadavrot_memset_benchmark.json](../../../data/wave13/enrich/raw/github_com_nadavrot_memset_benchmark.json) (enrichment confidence 0.72)

</details>
