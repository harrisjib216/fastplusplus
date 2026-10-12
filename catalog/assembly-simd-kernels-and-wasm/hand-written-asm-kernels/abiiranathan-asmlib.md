# asmlib (abiiranathan)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (NASM x86-64 AVX2/BMI2; GNU as AArch64 NEON) with a C header and a portable C/wasm backend` · `MIT` · 🟢 active

> Young MIT libc subset in NASM/AVX2 and AArch64 NEON assembly; its arena and malloc heap beat glibc on burst workloads, string routines mostly parity.

| | |
|---|---|
| **Beats** | glibc 2.44 memcpy/memset/memcmp/strlen/memchr/strstr/memmem, malloc/free, snprintf, sscanf and libm |
| **Claimed result** | docs/BENCHMARKS.md (glibc 2.44, i7-10510U, best of 7-9): arena 4.36 vs 37.46 ns/op (8.59x) and the 64 B asm_malloc row (4.79x) are the clean comparisons; the arena mixed 8..512B 19.80x, 2048 x 1 KiB 45.46x and 8.08x rows mostly time glibc page faults after each trial's bulk free (glibc about 494 ns per malloc+free pair there, derived, 13x its 64 B figure) |
| **Workload** | Nanoseconds per call from micro-benchmarks (bench/\*.c) of asm_\* routines against the glibc versions, best of 7 to 9 trials; function pointers are held volatile so the compiler cannot inline libc builtins. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-10510U (Comet Lake) laptop, AVX2+BMI1+BMI2+ERMS+FMA, glibc 2.44, Linux 7.2 |
| **Compiler and flags** | Harnesses built by the Makefile with \$(CC) and CFLAGS -O2 -Wall -Wextra (math_bench: -O2 -fno-builtin, math objects -O2 -ffreestanding -fno-builtin -ffp-contract=off); assembly via NASM. docs/BENCHMARKS.md lists GCC 16.2.1 and Clang 22.1.8 on the machine but does not say which compiler built the published runs. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/abiiranathan/asmlib) · [benchmark](https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/docs/BENCHMARKS.md) |

## Verdict

Author's best-of-7 to 9 laptop runs on an Intel i7-10510U with glibc 2.44 (harness -O2; whether GCC 16.2.1 or Clang 22.1.8 built it is unstated): arena 4.36 vs 37.46 ns per op against malloc/free for 1000 x 64 B (8.59x), asm_malloc 8.55 vs 40.94 ns (4.79x), asm_sscanf 2.2-3.1x and asm_u64toa 3.98x over glibc, libm mostly slower. The larger 19.8x, 8.08x and 45x allocator rows probably include glibc returning freed memory to the kernel between trials, and the memory/string results are reported only as ranges at or below parity except memchr.

## Use it when

- Per-request or per-frame scratch allocation on Linux x86-64 or AArch64 where a bump arena with mark/release and bulk reset fits (published 8.6x to 19.8x over glibc malloc/free for 64 B to 512 B bursts)
- Freestanding, -nostdlib or wasm32 builds that need a small libc subset plus libm with no imports
- Hot integer-to-decimal conversion where asm_u64toa's bounded buffer API can replace snprintf("%llu") (20.32 vs 80.79 ns/call published)
- Parsing simple integer or word fields with sscanf-like formats (2.2x to 3.1x published) when no floating point, scansets or %n are needed
- As readable, heavily commented AVX2/NEON reference code for memchr/memcmp/strcasecmp-style kernels

## Skip it when

- Expecting faster memcpy/memset/strlen/strstr than glibc: the author reports parity for mid/large memcpy, memset and memcmp, and glibc ahead on strlen (0.5-0.8x) and strstr (0.4-0.65x); no per-size table is published
- Allocations above 4080 bytes: each gets its own mmap/munmap under a global spinlock, a syscall per malloc and per free; the benchmark only covers 8-1024 byte blocks
- Long-running processes with phase changes: small-run memory is never returned to the kernel, and up to 1 MiB of thread-cached blocks is stranded per exiting thread unless asm_alloc_flush_tcache() is called from a thread-exit hook
- Pre-Haswell or FMA-less x86-64: the IFUNC fallback covers only the memory/string/search routines; the math objects in libasmlib.a/.so are compiled with -msse4.1 -mfma (use libasmlib_scalar.a there); macOS/BSD have no heap backend
- Production code that needs a track record: the repository is ten days old (2026-09-27 to 2026-10-06, 31 commits, 0 stars, no releases on the GitHub page), and the AArch64 port is tested only under QEMU with no published hardware numbers

## How it is fast

The string/memory routines use 32-byte AVX2 compares with vpmovmskb/tzcnt, an eight-vector vpand fold in memcmp, aligned-down page-safe loads, two-byte candidate filtering in strstr/memmem, and a size-tiered memcpy (AVX2 below 96 KiB, ERMS rep movsb to 256 KiB, non-temporal stores above). The large published wins come from allocation models, not SIMD: the arena is a pointer bump with an O(chunks) reset, and asm_malloc is a segregated size-class slab heap with a lock-free per-thread cache that never returns small-run memory to the kernel. asm_u64toa emits digit groups from a 200-byte table with reciprocal multiplies, and asm_sscanf is a small branch-driven scanner covering only integers, %s, %c and %p.

## Compared with alternatives

Pick it over FastMemcpy, memcpy_benchmark or ademakov/bzero when you want a tested, whole libc subset (strings, allocators, formatting, wasm build) rather than a single faster memcpy or memset; for raw memcpy/memset speed against a current glibc it shows only parity, so none of these is a clear win there.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time (Linux syscalls for the heap); build needs NASM 2.14+ and a C compiler (GNU as for AArch64, clang wasm32 target for wasm) |
| **Minimum toolchain** | NASM 2.14+ (3.02 tested), C11 GCC or Clang; Makefile or CMake; IFUNC dispatch needs hosted Linux x86-64 with GCC/Clang |
| **Platforms** | x86-64 Linux (AVX2/BMI hot paths with scalar IFUNC fallback; math requires FMA), AArch64 Linux (NEON), wasm32 and other freestanding targets via the portable C backend |
| **Thread safety** | string/memory routines reentrant; asm_malloc thread-safe via per-thread cache plus a global spinlock (not async-signal-safe); arena single-threaded by design. The asm_alloc doc block in asmlib.h still says the allocator is single-threaded, contradicting the README and alloc.asm. |
| **Drop-in for the baseline** | partial — asm_\* names by default; ASMLIB_ENABLE_LIBC_ALIASES macro-maps the string, ctype, printf, qsort and aligned-allocation names in one translation unit, but malloc/calloc/realloc/free stay libc and asm_malloc pointers must never reach libc free |

## Gotchas

- Harness flaw found this session (bench/arena_bench.c): the glibc side frees whole bursts of 1 KiB (2048 blocks, 2 MiB) and mixed 8-512 B blocks (4000, about 1 MB) each trial, which with glibc's default 128 KiB M_TRIM_THRESHOLD should hand the heap top back to the kernel and re-fault it next trial, while the arena reuses one pre-faulted 4 MiB mmap buffer and asm_malloc never returns small runs. The glibc 2048 x 1 KiB row costs 494 ns per malloc+free pair (derived from page data), 13x the 37.46 ns/op of the 64 B row, so the 45.46x, 19.80x and 8.08x rows largely measure page faults and brk trimming rather than allocator code; the 64 B rows (8.59x arena, 4.79x heap) are the cleaner comparison. Inferred from the harness and glibc defaults, not re-run here.
- ASMLIB_ENABLE_LIBC_ALIASES maps aligned_alloc, posix_memalign, reallocarray, malloc_usable_size and asprintf/vasprintf to the asm heap but leaves free, malloc and realloc on libc, so ordinary code such as aligned_alloc(...)/free(p) or asprintf(&s, ...)/free(s) in an aliased file hands an asm_malloc pointer to libc free, which asmlib.h itself says must never happen; asm_free does no pointer validation outside ASMLIB_ALLOC_DEBUG.
- Published numbers lag the code: the snprintf table (1.53-2.10x) measured the hand-written asm_snprintf that CHANGELOG [Unreleased] removed on 2026-10-06; the current asm_snprintf is the portable C printf engine and is unmeasured. The memchr harness always hits 'z' at offset 25, memcmp compares a buffer with itself (asm_memcmp has no pointer-equality shortcut, so this is an equal-input full scan, not an invalid row), strstr searches for an absent "zzz", and memmem has no benchmark despite the 'several times faster' claim.
- The math library is musl-derived portable C, not assembly; against glibc 2.44 only cbrt (2.18x), asinh (1.38x) and cosh (1.33x) are clearly faster and 13 of the 18 published functions are slower (sinh 0.52x).

## Known shortcomings

- Near A (public bench/\*.c, Makefile -O2, i7-10510U) but the README lists GCC 16.2.1 and Clang 22.1.8 without saying which built the runs; the memchr bench always hits 'z' at byte 25; memmem has no bench; the snprintf rows were measured on a hand-written asm_snprintf replaced by C printf.c on 2026-10-06; libm is musl-derived C, not asm; the big wins come from the allocator model.
- Enricher (inferred from code, not re-run): arena_bench frees whole 1-2 MiB glibc bursts each trial, which glibc's default 128 KiB trim threshold hands back to the kernel and re-faults next trial, while the arena reuses one pre-faulted buffer and asm_malloc never returns small runs, so the 45.46x, 19.80x and 8.08x rows mostly time page faults (glibc 494 ns per malloc+free pair, derived, 13x its 37.46 ns 64 B row); the 64 B rows (8.59x, 4.79x) are the cleaner comparison; ASMLIB_ENABLE_LIBC_ALIASES maps aligned_alloc/posix_memalign/reallocarray/asprintf to the asm heap but leaves free on libc; math objects are built with -mfma (use libasmlib_scalar.a on FMA-less x86-64); blocks above 4080 B cost an mmap and munmap each; asmlib.h still says the allocator is single-threaded.

## Caveats and trade-offs

Numbers are noisy laptop best-of-N results (author says so); the memory/string results are published only as approximate ranges and glibc wins on strlen and strstr. The memchr workload in bench/bench.c searches a repeating a-z string for 'z', so every size of 26 bytes or more measures a hit at offset 25, and the '1.1-1.2x from 128 B up' figure is really a 26-byte scan; memcmp compares a buffer with itself (equal-input case only). The 'memmem several times faster' claim has no benchmark. The snprintf table (docs/BENCHMARKS.md last changed 2026-09-28) was measured on the minimal hand-written asm_snprintf, which CHANGELOG [Unreleased] says was removed on 2026-10-06 in favour of the portable C printf engine (src/libc/printf.c); the current asm_snprintf is unmeasured C. asm_u64toa is a dedicated converter timed against general snprintf("%llu"). The arena and malloc-heap wins come from a different allocation model (bump arena with O(1) reset, thread-local cache), not from assembly alone. The libm routines are portable C adapted from musl (MIT), not assembly, so the cbrt/cosh/asinh wins are not asm-kernel results. Single machine; which of GCC 16.2.1 or Clang 22.1.8 built the harness is unstated. Young repo with 0 stars. [retier] Large-burst rows dominated by glibc trim-and-refault behaviour; ASMLIB_ENABLE_LIBC_ALIASES mixes allocators (free stays on libc); math objects built with -mfma; blocks above 4080 B cost an mmap and munmap each

Drop-in asm_\* API rather than libc symbols; x86-64 needs AVX2/BMI2; AArch64 port uses NEON; math is freestanding C.

## Maintenance

Active but brand-new (first commit 2026-09-27, last 2026-10-06, v1.0.0 in CHANGELOG, 0 stars); MIT with musl-derived math under MIT, thorough differential, guard-page, sanitizer and fuzz tests, but no external users or independent numbers yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party best-of-N tables in docs/BENCHMARKS.md from public harnesses (bench/arena_bench.c, format_bench.c, scan_bench.c, math_bench.c; Makefile CFLAGS -O2) on a named CPU (i7-10510U), which is close to A, but the page lists both GCC 16.2.1 and Clang 22.1.8 without saying which built the published runs, the memory/string results are qualitative only, and the snprintf table was measured on a hand-written asm_snprintf that has since been removed.
- **Verifier notes:** Arena, malloc, sscanf, u64toa and math numbers match docs/BENCHMARKS.md (u64toa libc figure is 80.79 ns, not 80.81). Shortcomings to record: the memchr benchmark always hits at byte 25, memmem is unbenchmarked, the snprintf rows describe asm code since replaced by C, the math library is musl-derived C, and the big wins are allocator-model wins. Last commit 2026-10-06, MIT, 0 stars, 31 commits all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-31 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/Makefile>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/format_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/scan_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/arena_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/math_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/format.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/memory.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/dprintf.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/LICENSE>
  - <https://github.com/abiiranathan/asmlib>
  - <https://github.com/abiiranathan/asmlib/commits>
  - <https://github.com/abiiranathan/asmlib/tree/main/src>
  - <https://github.com/abiiranathan/asmlib/commits/main/docs/BENCHMARKS.md>
- **Sources the enricher read:**
  - <https://github.com/abiiranathan/asmlib>
  - <https://github.com/abiiranathan/asmlib/commits>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/ROADMAP.md>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/Makefile>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/arena_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/format_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/scan_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/bench/math_bench.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/include/asmlib.h>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/memory.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/search.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/alloc.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/arena.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/format.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/scan.asm>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/dispatch_ifunc.c>
  - <https://raw.githubusercontent.com/abiiranathan/asmlib/HEAD/src/libc/printf.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/abiiranathan/asmlib`) · [data/wave13/enrich/raw/github_com_abiiranathan_asmlib.json](../../../data/wave13/enrich/raw/github_com_abiiranathan_asmlib.json) (enrichment confidence 0.7)

</details>
