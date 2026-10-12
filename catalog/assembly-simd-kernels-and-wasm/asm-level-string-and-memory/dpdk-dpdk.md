# rte_memcpy (DPDK): SSE/AVX2/AVX-512 memcpy for small, cache-resident copies

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> DPDK's header-inlined x86 SSE/AVX2/AVX-512 memcpy for small, cache-hot, non-overlapping packet-sized copies, pitched against glibc memcpy.

| | |
|---|---|
| **Beats** | glibc memcpy() |
| **Claimed result** | No rte_memcpy-versus-glibc results are checked into the repo (the test prints a tick pair and a percent difference per size). Intel's article 'Performance Optimization of memcpy in DPDK' (search-result snippet only, page could not be opened): replacing glibc memcpy with rte_memcpy in the DPDK vhost Rx/Tx path gave 22 percent more total bandwidth in a physical-VM-physical OvS-DPDK setup. The 2026 commit d0ab5a7 'eal/x86: optimize memcpy of small sizes' reports only rte_memcpy before/after cycle counts (8 bytes: 4 vs 7 cycles; 16 bytes: 2 vs 4; 64 bytes: 4 vs 7). |
| **Workload** | DPDK's app/test/test_memcpy_perf.c (memcpy_perf_autotest) times rte_memcpy and then libc memcpy on the same random source/destination offsets, in TSC ticks per copy averaged over 1,000,000 iterations, printing both tick counts and the percent difference. Variable sizes run from 1 to 8192 bytes (63 sizes, including 1518/1522/1536 packet sizes) and compile-time-constant sizes are 6, 64, 128, 192, 256, 512, 768, 1024 and 1536 bytes, each aligned (16/32/64-byte unit depending on SSE/AVX2/AVX-512 build) and unaligned, cache-to-cache, cache-to-memory, memory-to-cache and memory-to-memory (100 MB buffer). For the constant-size rows the 'memcpy' baseline is normally expanded inline by the compiler, so it is a GCC/Clang builtin rather than glibc. The system-level claim (snippet only) is a vhost Rx/Tx copy path in OvS-DPDK. |
| **Metric** | throughput |
| **Adoption** | 4.5k stars (GitHub mirror of dpdk.org); core of the DPDK data plane |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/DPDK/dpdk) · [benchmark](https://github.com/DPDK/dpdk/blob/main/app/test/test_memcpy_perf.c) |

## Verdict

No rte_memcpy-versus-glibc microbenchmark result is published: the in-repo memcpy_perf_autotest prints rte_memcpy and memcpy TSC ticks side by side for 1 to 8192 bytes, but no output, CPU, compiler or glibc version is recorded. The only glibc comparison is Intel's vendor figure (search snippet only) of 22% more vhost Rx/Tx bandwidth in a physical-VM-physical OvS-DPDK setup with no methodology, and the 2026 commit d0ab5a7 compares rte_memcpy only with its own previous version (for example 8 bytes 7 to 4 cycles, 64 bytes 7 to 4, cache to cache, CPU not named).

## Use it when

- Code already built against DPDK on x86-64 that copies packet headers, descriptors or small payloads (roughly 1 B to 1.5 KB) between buffers that are already in cache.
- Hot loops where variable small sizes would otherwise be an out-of-line libc call, and where inlining the copy is the gain you are after.
- Builds with an old toolchain or glibc whose small-size memcpy is weak; that was the original motivation, and the arm64 header still says its opt-in variant only helps with glibc 2.17/2.19-era libraries.
- Images built with a fixed -march (DPDK's default platform is 'native'), so the AVX2 or AVX-512 path is chosen once at build time.

## Skip it when

- Overlapping buffers: it is restrict-qualified and has no memmove semantics.
- Large streaming copies (tens of KB to MB): the header has no non-temporal stores, prefetch or REP MOVSB path, and nobody publishes rte_memcpy numbers for that range.
- Generic distribution binaries that must run on many x86 CPUs: there is no runtime dispatch, so a portable build gets the SSE path even on AVX-512 hardware.
- Non-x86 targets: on arm64 and LoongArch it is literally memcpy, so there is nothing to gain.
- Code checked by sanitizers or fortify tooling: DPDK reviewers note that bounds tooling understands memcpy but not rte_memcpy, and upstream is moving drivers back to plain memcpy.

## How it is fast

The whole copy is inlined at the call site, so there is no call, PLT or ifunc dispatch; sizes below 16 bytes use 8/4/2/1-byte moves selected by the bits of n, and 16 to 64 bytes use two overlapping unaligned vector moves (head and tail) with no loop. Larger copies align the store side and run unrolled 128-byte (AVX2) or 512-byte (AVX-512) blocks of unaligned loads, and the SSE-only build uses PALIGNR (_mm_alignr_epi8) with one switch case per source misalignment. The ISA is fixed at compile time from -march macros, and there is no non-temporal store, prefetch or REP MOVSB path.

## Compared with alternatives

Pick it when you are already inside DPDK on x86 and want inlined small copies with the ISA fixed at build time; for a drop-in libc replacement with runtime dispatch, AOCL-LibMem (AMD Zen) or Agner Fog's asmlib fit better, and nadavrot/memset_benchmark at least publishes charts against glibc, which rte_memcpy does not.

## Integration

| | |
|---|---|
| **Form** | header-only (part of DPDK's EAL headers; vendoring it needs the rte_common.h/rte_vect.h macros) |
| **Dependencies** | DPDK EAL headers (rte_common.h, rte_vect.h, rte_config.h) for macros such as __rte_always_inline, __rte_restrict, __rte_constant and __rte_may_alias |
| **Minimum toolchain** | C11 compiler as used by DPDK's meson build; x86 builds force at least SSE4.2 (-msse4), the SSE path needs SSSE3 for PALIGNR, and the plain-AVX (non-AVX2) path is used only on GCC 11+ or Clang |
| **Platforms** | x86-64 (SSE, AVX, AVX2, opt-in AVX-512) is the real implementation; POWER has a VSX version; arm64, LoongArch and default RISC-V map to memcpy (opt-in RTE_ARCH_ARM64_MEMCPY and RTE_ARCH_RISCV_MEMCPY variants exist) |
| **Thread safety** | Stateless copy function; safe to call concurrently on disjoint buffers (no shared state in the header) |
| **Drop-in for the baseline** | partial: same (dst, src, n) signature and return value, but it is an inline header function rather than a libc symbol, it requires non-overlapping buffers, and the documented contract is a macro whose address should not be taken and whose arguments may be evaluated more than once |

## Gotchas

- AVX-512 is opt-in: even with __AVX512F__ defined, the 64-byte zmm path is used only if RTE_MEMCPY_AVX512 is defined before including the header; otherwise an AVX-512 build runs the AVX2 path. A DPDK list report (search snippet only) found the AVX-512 path slower than AVX2 in an OvS-DPDK test.
- Harness asymmetry in app/test/test_memcpy_perf.c: rte_memcpy is force-inlined into the timed loop, while variable-size libc memcpy is an out-of-line call through the PLT, so small-size tick gaps partly measure call overhead. Constant-size rows let the compiler expand memcpy inline, so they compare against the GCC/Clang builtin rather than glibc. rte_memcpy always runs first, per-copy times are printed rounded to whole TSC ticks (a 4-vs-7-tick row has about ±0.5 tick of rounding error), and no results are checked in.
- In the SSE-only build (no -mavx), copies over 512 bytes with a 16-byte-aligned destination and an unaligned source enter the PALIGNR loop without the 17-31-byte head copy, so the first load reads the aligned 16-byte block containing src, up to 15 bytes before it (code reading, untested). It cannot fault because the read never crosses a page, but it touches memory outside the source object; the functional test only uses offsets inside a larger array, so it would not catch this.
- Small-size loads and stores were undefined behaviour (misaligned, strict-aliasing) from the first public release until commit 00901e4 in 2022 moved them to packed may_alias structs; the 2026 rewrite d0ab5a7 also dropped the header's stringop-overflow warning suppression after drivers that tripped it were switched to memcpy.

## Known shortcomings

- The only glibc number is Intel's 22% vhost figure (vendor, snippet only); the in-repo test_memcpy_perf.c has no published results and its constant-size rows compare against compiler-inlined memcpy; DPDK developers report shrinking gains with newer compilers (2022 Hemminger, 2024 Ronnblom, 2026 "reduce use of rte_memcpy" series); workload sizes fixed up to 8192 B.
- Enricher: still no published rte_memcpy-vs-glibc numbers; in test_memcpy_perf.c rte_memcpy is force-inlined in the timed loop while libc memcpy goes out-of-line through the PLT, constant-size rows hit the compiler builtin, rte_memcpy always runs first and ticks are rounded to integers; the AVX-512 path needs -DRTE_MEMCPY_AVX512 (otherwise AVX2 runs); on arm64 and LoongArch rte_memcpy is just memcpy; in the SSE-only build with n&gt;512, aligned dst and unaligned src the PALIGNR loop reads up to 15 bytes before src (code reading, cannot fault).

## Caveats and trade-offs

The only glibc comparison number (22 percent) is a system-level bandwidth figure from a search snippet of Intel's article 'Performance Optimization of memcpy in DPDK' (intel.com fails with getaddrinfo ENOTFOUND here); Intel originated DPDK, so it is first-party vendor evidence with no stated CPU, glibc, compiler or OvS/DPDK versions, and not a memcpy microbenchmark. The in-repo harness compares against libc memcpy but no results are checked in. Commit d0ab5a7 (2026, 'eal/x86: optimize memcpy of small sizes') reports only rte_memcpy before/after cycles (8 bytes 4 vs 7, 16 bytes 2 vs 4, 64 bytes 4 vs 7, up to 15 bytes about 4.5 vs 6.5), with no CPU or compiler named. Counter-evidence from the DPDK list (search snippets only, mails.dpdk.org unreachable): Stephen Hemminger wrote in 2022 that rte_memcpy was added because gcc/glibc then used poor x86 instructions and that for small copies plain moves are as fast or faster; Mattias Ronnblom's 2024 series 'Optionally have rte_memcpy delegate to compiler memcpy' argued the benefit 'has been diminishing with every compiler release' (its use_cc_memcpy option is not in meson_options.txt on main, so it was not merged); a 61-patch series 'reduce use of rte_memcpy' was under review in August 2026, with reviewers asking for data-path performance tests and noting sanitizer/bounds tooling understands memcpy but not rte_memcpy. A DPDK mailing-list report (snippet only) found the AVX-512 path slower than AVX2 in an OvS-DPDK test. The 2015 RFC that motivated the AVX path said results depend on the glibc version. last_commit is the repository head; rte_memcpy.h (lib/eal/x86/include) was last touched 2026-09-23 (commit 4f795dd).

Not a libc drop-in: callers use the rte_memcpy() header function. ISA is chosen at compile time from -march macros (SSE, AVX, AVX2, AVX-512); the header forces SSE instead of AVX on GCC older than 11. Tuned for small copies whose source and destination are in cache; large streaming copies are not its target. x86 header plus separate arm/ppc variants.

## Maintenance

Actively maintained (rte_memcpy.h last changed 2026-09-23, repository head 2026-10-10) and BSD-3-Clause, so it is easy to lift, but DPDK maintainers themselves question its advantage over modern compiler and glibc memcpy and a 2026 series is replacing many call sites with plain memcpy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** app/test/test_memcpy_perf.c does time rte_memcpy and libc memcpy side by side in TSC ticks, but no results, CPU, compiler or flags are published anywhere in the repo; the only rte_memcpy-versus-glibc number (22 percent more vhost bandwidth in OvS-DPDK) comes from an Intel article, seen as a search snippet only (intel.com unreachable here), which is first-party vendor evidence without methodology. The 2026 commit d0ab5a7 compares rte_memcpy only with its own previous version.
- **Verifier notes:** Real, widely used x86 memcpy (BSD-3-Clause header in lib/eal/x86/include/rte_memcpy.h), but the only win over glibc is a snippet-only vendor figure at system level; the harness exists yet nobody publishes its rte_memcpy-vs-memcpy output, and DPDK maintainers themselves are moving code back to plain memcpy. Shortcomings to record: no published microbenchmark results, vendor snippet-only evidence, constant-size baseline is compiler-inlined, upstream doubts about the benefit on current compilers. Record's workload said sizes up to about 1.5 KB; variable sizes actually go to 8192 bytes.
- **Fields the verifier corrected:** `workload`, `last_commit`, `caveats`
- **Shortcomings recorded by:** verifier batch-93 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/DPDK/dpdk>
  - <https://github.com/DPDK/dpdk/commits/main>
  - <https://github.com/DPDK/dpdk/commits/main/lib/eal/x86/include/rte_memcpy.h>
  - <https://github.com/DPDK/dpdk/commit/d0ab5a7>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/app/test/test_memcpy_perf.c>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/meson_options.txt>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/x86/include/rte_memcpy.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/include/generic/rte_memcpy.h>
- **Sources the enricher read:**
  - <https://github.com/DPDK/dpdk>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/README>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/x86/include/rte_memcpy.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/include/generic/rte_memcpy.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/arm/include/rte_memcpy.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/arm/include/rte_memcpy_64.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/ppc/include/rte_memcpy.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/riscv/include/rte_memcpy.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/lib/eal/loongarch/include/rte_memcpy.h>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/app/test/test_memcpy_perf.c>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/app/test/test_memcpy.c>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/meson_options.txt>
  - <https://raw.githubusercontent.com/DPDK/dpdk/main/config/x86/meson.build>
  - <https://github.com/DPDK/dpdk/commits/main/lib/eal/x86/include/rte_memcpy.h>
  - <https://github.com/DPDK/dpdk/commit/d0ab5a7>
  - <https://github.com/DPDK/dpdk/commit/2ef17be>
  - <https://github.com/DPDK/dpdk/commit/00901e4>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/dpdk/dpdk`) · [data/wave13/enrich/raw/github_com_dpdk_dpdk.json](../../../data/wave13/enrich/raw/github_com_dpdk_dpdk.json) (enrichment confidence 0.7)

</details>
