# glibc (libc string functions, qsort, regexec, strtod, malloc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [String search and hashing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-or-later` · 🟢 active

> GNU C library; its CPU-dispatched string routines, malloc, qsort, regexec and strtod beat zig-bundled static musl in most micro-benchmarks.

| | |
|---|---|
| **Beats** | musl libc as shipped by zig 0.15.2 (string functions replaced by Zig code), single run |
| **Claimed result** | glibc fastest in 17 of 32 rows (musl 2, musl+jemalloc 11, 2 ties); README summary: 'glibc wins most benchmarks'. ns/op, glibc vs musl: strncmp 9.91 vs 366.91; strcpy 22.05 vs 129.35; strncpy 25.20 vs 136.77; strstr_search 36.28 vs 104.23; strtod_parse 52.40 vs 226.72 (4.3x, derived from page data); regex_match 117.54 vs 694.23 (5.9x, derived from page data); qsort_int 214387.15 vs 591408.11 (2.8x, derived from page data); malloc_free_small 10.78 vs 122.61; malloc_free_medium 828.38 vs 3343.75. musl is faster on atoi_parse 3.96 vs 9.28, bsearch_int 10.52 vs 16.02, sprintf_float 136.34 vs 160.56, strtok_parse 5.71 vs 15.23, strtok_r_parse 4.94 vs 14.76, strrchr 157.31 vs 354.19 and memcpy 154.19 vs 4043.27; musl+jemalloc beats glibc on malloc_free_medium 80.59 vs 828.38 and malloc_free_small 10.15 vs 10.78. |
| **Workload** | 32 libc micro-benchmarks (benchmark.c), each calibrated to a target run time and reported as ns per call: strncmp, strcpy, strncpy, strstr, strchr, qsort of 4096 ints, regexec of an e-mail pattern over 128 lines, strtod over 256 numbers, malloc/free small and medium, printf family, file I/O, and others. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 PRO 5850U with Radeon Graphics; Linux 6.8.0-87-generic (Ubuntu 22.04 kernel); run 2025-11-18 |
| **Compiler and flags** | zig 0.15.2 (zig cc, clang 20.1.2); -std=c11 -O3 -march=native -mtune=native -flto=full -fomit-frame-pointer -funroll-loops -DNDEBUG -fno-math-errno -fno-trapping-math -g0 -s; targets x86_64-linux-gnu and x86_64-linux-musl (run.sh) |
| **Adoption** | 1.9k stars (unofficial bminor/glibc mirror); the default libc of most Linux distributions |
| **Last commit** | 2026-01-20 |
| **Links** | [repository](https://github.com/bminor/glibc) · [benchmark](https://github.com/fereidani/musl-vs-glibc) |

## Verdict

fereidani/musl-vs-glibc built one C benchmark with zig 0.15.2 (clang 20.1.2, -O3 -march=native -flto=full) against the host's dynamic glibc (Ubuntu 22.04 kernel string, so probably 2.35) and against zig's static musl, then ran each binary once (250 ms calibrated target per row) on an AMD Ryzen 7 PRO 5850U. glibc was fastest in 17 of 32 rows (strncmp 37x, strcpy 5.9x, strncpy 5.4x, regexec 5.9x, strtod 4.3x, qsort 2.8x, 32-byte malloc/free 11.4x, derived from page data) and lost memcpy (26x), strrchr, strtok, strtok_r, atoi, bsearch and sprintf_float.

## Use it when

- You ship dynamically linked binaries for mainstream Linux distributions: glibc is already the libc and costs nothing to adopt.
- Deciding between a glibc and a musl target for code heavy in strcpy/strncpy/strncmp, regexec, strtod, qsort or small malloc/free: glibc measured 2.8x (qsort of 4096 ints) to 37x (strncmp) faster in this run, 11x on 32-byte malloc/free.
- Long string copies and compares on x86-64, where the per-CPU AVX2/EVEX variants pay off (strcpy of 2047 bytes: 22 ns vs 129 ns).
- Parsing-heavy code (strtod 4.3x, regexec 5.9x, getline 3.5x faster than the musl build) where you cannot swap in a specialised parser.

## Skip it when

- Fully static, portable binaries: static glibc carries LGPL obligations and breaks NSS and iconv module loading; musl is the usual static choice.
- Large memcpy on AMD Zen 3/Zen 4 with a glibc that predates the BZ 30994 fix (2.35 as on Ubuntu 22.04): the 16 KB copy ran 26x slower (4043 vs 154 ns) because rep movsb hits page aliasing; upgrade, or raise glibc.cpu.x86_rep_movsb_threshold through GLIBC_TUNABLES.
- Workloads dominated by strtok/strtok_r (2.7x and 3.0x slower than the musl build), atoi (2.3x slower), bsearch (1.5x slower) or strrchr over long strings with many matches (2.25x slower on glibc 2.35).
- Medium (4 KB) allocation churn: ptmalloc2 took 828 ns per malloc/free against 81 ns for jemalloc linked into the musl build; link jemalloc or mimalloc instead of relying on the default allocator.
- Footprint-constrained containers or embedded images where musl's much smaller runtime matters more than these speedups.

## How it is fast

On x86-64 the string and memory functions are hand-written assembly variants (SSE2, AVX2, EVEX/AVX-512) picked once at load time through IFUNC from CPU feature bits: in 2.35, strstr resolves to __strstr_sse2_unaligned, which scans 64 bytes per loop iteration for the needle's first two bytes, and memmove/memcpy switch to rep movsb above 2112 bytes on FSRM CPUs (dl-cacheinfo.h). malloc puts a per-thread cache (tcache: 64 size bins, 7 chunks each) in front of the ptmalloc2 arenas; qsort is a merge sort with a temporary buffer (alloca under 1 KB, malloc above, quicksort fallback); regexec runs a DFA-state matcher; strtod converts exactly with multi-precision (mpn) arithmetic. The musl side loses on plain C loops by comparison: word-at-a-time stpcpy for strcpy, smoothsort for qsort, a two-way matcher for strstr.

## Compared with alternatives

glibc is the libc you already link, so it is the baseline those siblings beat. Reach for StringZilla or sse4-strstr when substring search dominates: glibc 2.35's x86-64 strstr only chooses between two SSE2 versions. Reach for the Boost.Algorithm Boyer-Moore searchers when one long pattern is searched in many haystacks.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Linux kernel 3.2 or later (glibc 2.35 README); otherwise none, it is the system libc |
| **Minimum toolchain** | any C/C++ toolchain targeting \*-linux-gnu (the benchmark used zig cc -target x86_64-linux-gnu); building glibc itself not covered here |
| **Platforms** | Linux on x86-64, aarch64, arm, ppc, riscv, s390 and others (README configuration list), plus GNU/Hurd; SIMD string variants are per architecture and chosen at load time by IFUNC on x86-64 |
| **Thread safety** | malloc is thread-safe with per-thread tcache and arenas; strtok keeps hidden static state (use strtok_r); other functions follow POSIX thread-safety rules |
| **Drop-in for the baseline** | partial: same ISO C/POSIX API as musl, so switching is a target/link change, but static linking, locale/NSS behaviour and GNU extensions differ |

## Gotchas

- The baseline is not pure musl: zig 0.15.2 replaces musl's memcpy, memmove, strlen, strcmp and strncmp with Zig code (lib/c/string.zig, compiler_rt memcpy.zig). The 37x strncmp win is against Zig's byte-at-a-time loop, the memcpy loss is against Zig's compiler_rt memcpy, and musl's strrchr win (musl calls memrchr(s, c, strlen(s)+1)) rides on Zig's SIMD strlen (std.mem.indexOfSentinel).
- memcpy speed depends on the glibc version and the CPU: 2.35 uses rep movsb from 2112 bytes up to the L2 size on AMD (dl-cacheinfo.h). On Zen 3/4 that hits BZ 30994 page aliasing when (dst-src) mod 4096 is small, as with two adjacent 16 KB heap blocks. The fix 'x86: Fix Zen3/Zen4 ERMS selection' landed on the 2.39 branch (search snippets only; sourceware.org not opened).
- glibc qsort through 2.38 can corrupt memory when the comparator is non-transitive (for example a - b on ints) and its temporary-buffer malloc fails, which sends it to the _quicksort fallback (Qualys advisory 2024-01-30; glibc treats the comparator as the bug). qsort also mallocs a temporary buffer of 1 KB or more, so it allocates on every large call.
- Harness flaws behind several rows: strlen, strcmp and memcmp are hoisted no-ops (about 0.1 ns). vprintf_mix never calls vprintf; it calls vsnprintf with another format. file_io_rw times tmpfile() disk I/O. The strstr_search averages are implausible for the source: 10 of 16 needles scan the about 16 KB haystack that strcpy's NUL leaves, so glibc's 36.28 ns average implies about 282 bytes/ns, beyond what the SSE2 loop in strstr-sse2-unaligned.S (eight 16-byte loads per 64 bytes) can deliver. The cause was not found and was not reproduced (derived from benchmark.c and page data).

## Known shortcomings

- Tier A on fereidani/musl-vs-glibc (benchmark.c, run.sh, zig 0.15.2/clang 20.1.2, flags, Ryzen 7 PRO 5850U), but the glibc version is unstated (Ubuntu 22.04, probably 2.35), it is one run, the strlen/strcmp/memcmp rows are hoisted no-ops, the strstr haystack is cut to about 16 KB (averages look low, not reproduced), and the memcpy row matches glibc BZ 30994 (rep movsb page-aliasing on AMD Zen) rather than a harness artefact; musl wins on sprintf_float and strtok_r_parse were omitted from the record's headline. The bminor mirror was archived 2026-02-15; upstream glibc is live.
- Enricher: the fereidani/musl-vs-glibc 'musl' column is not pure musl: zig 0.15.2 swaps musl's memcpy, memmove, strlen, strcmp and strncmp for Zig code (lib/c/string.zig, compiler_rt/memcpy.zig), so the 37x strncmp win is against a Zig byte loop, the memcpy loss is against Zig's memcpy and the musl strrchr win rides on Zig's SIMD strlen. The strstr_search row is physically implausible (10 of 16 needles scan about 16 KB; glibc's 36.28 ns average implies about 282 bytes/ns, beyond the SSE2 loop in strstr-sse2-unaligned.S; cause unknown, not reproduced); vprintf_mix never calls vprintf (uses vsnprintf); file_io_rw times tmpfile disk I/O; single run. The memcpy row is glibc BZ 30994 (Zen 3 rep movsb from 2112 bytes in 2.35; fixed on the 2.39 branch; tunable glibc.cpu.x86_rep_movsb_threshold). qsort through 2.38 had memory corruption with a non-transitive comparator (Qualys 2024-01-30). bminor mirror archived 2026-02-15.

## Caveats and trade-offs

Third-party hobby repo (7 stars, 7 commits, no licence file), one machine, one calibrated run per benchmark (250 ms target) with no repeats or variance; results dated 2025-11-18. The glibc version is not stated: the binary is built with zig cc -target x86_64-linux-gnu and runs against the host's dynamic glibc (kernel string 6.8.0-87-generic #88\~22.04.1-Ubuntu, so Ubuntu 22.04 and probably glibc 2.35, an inference). The musl side is zig's bundled musl compiled by zig (its optimisation level not stated) and linked statically, so the two sides are built differently and glibc calls go through the PLT. Several rows are not meaningful: strlen, strcmp and memcmp show about 0.1 ns/op because the loop-invariant pure calls are hoisted out of the loop (ties); the strstr haystack is cut to about 16 KB because the strcpy that plants the first marker writes a NUL (benchmark.c), and the strstr averages look low for the 10 of 16 needles that scan that whole haystack (verifier's estimate, not reproduced). The memcpy row (glibc 4043.27 vs musl 154.19 ns for 16 KB, about 4 GB/s vs 106 GB/s) is not a harness artifact but matches glibc bug BZ 30994, 'REP MOVSB performance suffers from page aliasing' on AMD Zen 3/Zen 4 when (dst-src) mod 4096 is small (reported 4.2 GB/s vs 111 GB/s), addressed upstream by 'x86: Fix Zen3/Zen4 ERMS selection (BZ 30994)' (WebSearch snippets only; sourceware.org is blocked here), so results on this CPU depend on the glibc version. A vendor blog (BellSoft Alpaquita, which sells a musl build with tuned routines) reports glibc ahead of musl on memcpy and memcmp; the page was EGRESS_BLOCKED and its numbers are not used. repo_url is the read-only unofficial mirror (archived 2026-02-15, last commit 2026-01-20); upstream development is at sourceware.org, which was not opened. Baseline is a C library, not a C++ standard library. [retier] fereidani/musl-vs-glibc (zig 0.15.2/clang 20.1.2, Ryzen 7 PRO 5850U, Ubuntu 22.04 glibc probably 2.35, one run): the 'musl' column uses Zig's own memcpy/memmove/strlen/strcmp/strncmp, so the strncmp 37x and strrchr wins and the memcpy loss are against Zig code; strlen/strcmp/memcmp rows are hoisted no-ops; strstr row implausible (about 282 bytes/ns); vprintf_mix uses vsnprintf; file_io_rw times disk I/O; memcpy loss is BZ 30994 (fixed on 2.39). musl wins sprintf_float and strtok_r_parse. Static vs dynamic linking asymmetric.

LGPL: the normal route is dynamic linking, static linking brings LGPL obligations and breaks NSS and iconv loading. Much larger runtime than musl. The comparison is for x86-64 on one CPU; glibc's speed on str\*/mem\* routines depends on per-CPU variant selection (general knowledge, not shown on the benchmark page). malloc is the default ptmalloc2 and loses to jemalloc on the medium-size row.

## Maintenance

glibc is actively developed upstream at sourceware.org; the bminor GitHub mirror used as repo_url was archived on 2026-02-15 and is read-only, and the library is LGPL-2.1-or-later and used as the system shared library rather than vendored. The evidence is one unrepeated hobby run whose musl column partly measures Zig's own memcpy/strlen/strcmp/strncmp, whose memcpy row reflects a Zen 3 glibc bug fixed in later versions, and whose strstr row is implausibly fast for the code it times.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** fereidani/musl-vs-glibc publishes the harness (benchmark.c, run.sh), the compiler (zig 0.15.2 using clang 20.1.2), the full flag set in run.sh and the CPU (AMD Ryzen 7 PRO 5850U), and its README table is the source of every claimed number, which meets A for a third-party run. The glibc version is not printed, but the kernel string (6.8.0-87-generic #88\~22.04.1-Ubuntu) pins the host to Ubuntu 22.04 (glibc 2.35, an inference) and zig 0.15.2 pins the bundled musl.
- **Retiered** A to C: The harness is public with flags and CPU, but its 'musl' baseline is zig 0.15.2's patched musl (Zig replaces memcpy, memmove, strlen, strcmp and strncmp), several rows are hoisted no-ops or physically implausible, and it is a single run; a mislabelled baseline caps the evidence at C (crippled-baseline precedent).
- **Verifier notes:** Every claimed number matches the README table; claimed_speedup now also lists the musl wins it omitted (sprintf_float, strtok_r_parse) and the musl+jemalloc malloc_free_small win. The memcpy row is explained by the known glibc rep movsb page-aliasing bug on AMD Zen (BZ 30994, snippet only), so the caveat no longer calls it a harness artifact; strlen/strcmp/memcmp rows are hoisted no-ops. maintenance_status left 'active': the bminor mirror was archived 2026-02-15 (strict rule would say abandoned), but glibc itself is the actively developed default libc and the mirror's last commit (2026-01-20) is within 12 months; metadata checked on github.com (1.9k stars, 487 forks, LGPL-2.1).
- **Fields the verifier corrected:** `claimed_speedup`, `compared_against_cpp_std_directly`, `caveats`, `baseline`
- **Shortcomings recorded by:** verifier batch-63 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/bminor/glibc>
  - <https://github.com/bminor/glibc/commits>
  - <https://github.com/fereidani/musl-vs-glibc>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/README.md>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/run.sh>
- **Sources the enricher read:**
  - <https://github.com/bminor/glibc>
  - <https://github.com/fereidani/musl-vs-glibc/commits>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/README.md>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/fereidani/musl-vs-glibc/HEAD/run.sh>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/README>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/NEWS>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/sysdeps/x86_64/multiarch/strstr.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/sysdeps/x86_64/multiarch/strstr-sse2-unaligned.S>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/sysdeps/x86_64/multiarch/ifunc-impl-list.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/sysdeps/x86_64/multiarch/ifunc-memmove.h>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/sysdeps/x86_64/multiarch/strrchr-avx2.S>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/sysdeps/x86/dl-cacheinfo.h>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/stdlib/msort.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/malloc/malloc.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/stdlib/strtod_l.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.35/posix/regexec.c>
  - <https://github.com/ziglang/zig/tree/0.15.2/lib/libc/musl/src/string>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c/string.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/c/strings.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/compiler_rt.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/compiler_rt/memcpy.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/compiler_rt/memmove.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/std/mem.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/musl/src/stdlib/qsort.c>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/musl/src/string/strrchr.c>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/musl/src/string/strstr.c>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/musl/src/string/strcpy.c>
  - <https://raw.githubusercontent.com/ziglang/zig/0.15.2/lib/libc/musl/src/string/stpcpy.c>
  - https://www.qualys.com/2024/01/30/qsort (WebSearch snippet only)
  - https://sourceware.org/bugzilla/show_bug.cgi?id=30994 (WebSearch snippet only)
  - https://patchwork.sourceware.org/comment/166019/ (WebSearch snippet only)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/bminor/glibc`) · [data/wave1/enrich/raw/github_com_bminor_glibc.json](../../../data/wave1/enrich/raw/github_com_bminor_glibc.json) (enrichment confidence 0.6)

</details>
