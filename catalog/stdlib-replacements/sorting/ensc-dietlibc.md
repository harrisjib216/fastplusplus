# dietlibc (qsort and bsearch)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `GPL-2.0-or-later` · 🔴 abandoned

> dietlibc's in-place 3-way quicksort and binary search; a 2001 changelog claimed 2.3x and 6.1x fewer cycles than glibc.

| | |
|---|---|
| **Beats** | glibc qsort and bsearch |
| **Claimed result** | qsort 300010 cycles vs glibc 679414 cycles (about 2.3x fewer cycles, derived from page data); bsearch 553 cycles vs glibc 3352 cycles (about 6.1x fewer cycles, derived from page data). Changelog author: 'I have no idea why glibc is so slow.' |
| **Workload** | qsort and bsearch on 1000 random ints, measured in CPU cycles, as recorded in the dietlibc 0.8 changelog entry (2001 or earlier; lib/qsort.c history in the mirror starts 2001-02-11). The qsort that was measured has since been replaced twice (new qsort 2003-11-02, 'faster qsort' 2006-08-16, random pivot via rand_i 2019-01-29). |
| **Metric** | latency |
| **Adoption** | 130 stars on the unofficial ensc git-cvs mirror (archived 2023-09-05); packaged by Debian, Fedora, Gentoo, openSUSE per search results |
| **Last commit** | 2019-03-18 |
| **Links** | [repository](https://github.com/ensc/dietlibc) · [benchmark](https://raw.githubusercontent.com/ensc/dietlibc/HEAD/CHANGES) |

## Verdict

The only numbers are one changelog line from 2001 (section 0.7.3, later 0.8): on 1000 random ints, glibc's qsort took 679,414 cycles against dietlibc's 300,010, and one bsearch took 3,352 against 553 cycles. No compiler, flags, CPU or glibc version is given, the probable harness times a single call of each, and both measured routines were later rewritten after correctness and robustness fixes.

## Use it when

- You already build a static Linux binary against dietlibc for size (initramfs tools, rescue or embedded utilities) and need a working qsort/bsearch at no extra cost.
- Sorting must not touch the heap: dietlibc's qsort is in place and only uses the recursion stack, while glibc's current qsort mallocs a merge buffer once the array exceeds 1024 bytes.
- Inputs with many equal keys: 3-way partitioning sorts 1000 identical ints in 2,000 comparisons in the Python port (6 recursion levels or fewer for 4 distinct values).
- You want a short, readable 3-way quicksort to study or adapt (lib/qsort.c is 73 lines), and GPL-2.0-or-later is acceptable.

## Skip it when

- Speed-critical sorting with a function-pointer comparator: about 1.8x more comparator calls than a merge sort on random distinct keys (Python port), byte-by-byte swaps, and the x86_64 build uses -Os; nothing shows it beating a current glibc.
- You need a stable sort: it is an unstable quicksort.
- Untrusted or adversarial input with tight stack limits: there is no recursion-depth bound and it recurses into both partitions, so worst-case stack depth is O(n).
- You link prebuilt libraries compiled against glibc headers, need shared libraries, or target anything but Linux: the FAQ says glibc-compiled libraries fail to link (missing __ctype_b), shared libraries are experimental, and FreeBSD/Solaris/Windows ports are refused.
- Proprietary binaries: the libc is GPL-2.0-or-later and statically linked, so distributed binaries carry GPL obligations (the FAQ only promises not to sue over BSD programs with public source).

## How it is fast

The current qsort is the Sedgewick/Bentley 3-way partitioning quicksort from 'Quicksort is Optimal', with a random pivot drawn from a per-process Park-Miller generator (rand_i, seeded from the ELF AT_RANDOM bytes); keys equal to the pivot are gathered at the ends and swapped to the middle, so duplicate-heavy input finishes in near-linear time. It makes no malloc, syscall or first-call setup, which is the likeliest source of its 2001 win over glibc's merge sort (glibc 2.2's first large qsort call read /etc/mtab and /proc/meminfo to size its buffer, then malloc'd it). There is no insertion-sort cutoff, median-of-three or word-sized swap, so on random distinct keys it is not algorithmically faster: a Python port of lib/qsort.c made 15,814 comparator calls on 1000 random distinct keys (1.59 n log2 n), against 8,735 for a glibc-style top-down merge sort on the same data.

## Compared with alternatives

Only when the program is already built against dietlibc for binary size. For speed, swenson/sort (typed C macros, about 2.2x libc qsort on 10,000 int64 in its README) or pdqsort and crumsort are measured alternatives; dietlibc's qsort has no current evidence of beating anything.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (Linux syscalls only); qsort.c also needs rand_i.c, which uses getauxval(AT_RANDOM) and rand_r |
| **Minimum toolchain** | GCC (FAQ: compiling dietlibc with another compiler is not supported; CHANGES 0.34 adds clang support with larger code and no cross-compiling); bsearch.c uses GNU void-pointer arithmetic |
| **Platforms** | Linux only: i386, x86_64, arm, aarch64, mips, ppc/ppc64, sparc/sparc64, s390, alpha, parisc, ia64 per the Makefile |
| **Thread safety** | bsearch is stateless; qsort is reentrant except that rand_i keeps an unsynchronized static seed, a data race under concurrent qsort calls that only perturbs pivot choice |
| **Drop-in for the baseline** | partial — same qsort/bsearch signatures, but you get them only by linking the whole program statically against dietlibc; copying lib/qsort.c alone needs rand_i and puts the file under GPL-2.0-or-later |

## Gotchas

- Harness flaw behind the numbers: CHANGES gives no method, and the closest harness is the scratch t.c in the same 2001 commit (344deb2), which times one rdtsc-bracketed qsort and one bsearch per run (SIZE is 100000 there, not the 1000 quoted). Its warm-up qsort(array,2,...) is 8 bytes, which glibc 2.2's msort.c sorts on an alloca buffer, so the timed glibc call is the first to take the 1024-byte-or-larger path: sysconf(_SC_PHYS_PAGES), which in glibc 2.2 parses /etc/mtab and /proc/meminfo through stdio, then malloc/free of the merge buffer. bsearch gets no warm-up, so glibc's 3,352 cycles for one lookup probably include first-call costs (cold cache, and lazy PLT binding if glibc was linked dynamically, which is not stated). The repo's later timing test, test/qsort.c, is no better: its string comparator loops while (l=(\*A-\*B)), an inverted condition, so it always returns 0 (every key compares equal, which a 3-way quicksort finishes in one pass) and its 'not sorted' check can never fire.
- The measured 2001 qsort never advances its left scan past a key equal to the pivot, so it goes quadratic with O(n) recursion depth on all-equal or few-distinct input (Python port: 1,001,948 comparisons and depth 993 for 1000 equal ints; 4,029,021 comparisons for 4000 ints with 4 distinct values). It was replaced on 2003-11-02 ('write new qsort that does not fail so').
- The measured 2001 bsearch shrinks the window by num instead of num+1 when it moves right, so probes can land past the end of the array: it reads out of bounds and can miss keys that are present, not only the last one (Python port: sizes 1 to 199 read past the end for 137 sizes; with n=13 it misses index 11 when the word past the end is smaller than the key), and with nmemb 0 it still reads base[0]. CHANGES records bsearch fixes in 0.10, 0.11, 0.13 ('didn't find the very last element') and 0.15.
- From 'faster qsort' (2006-08-16, the 0.31 changelog line) until commit 635fb76 (2012-08-27, 'two fixes by Enrico Scholz') the pivot was the rightmost element, quadratic with recursion depth n on sorted or reversed input (Python port: 501,498 comparisons for 1000 sorted ints), so 0.31/0.32-era packages carry it. From 2012 to 2019-01-29 the random pivot called rand(), which advanced the program's own rand() sequence, until rand_i replaced it (CHANGES 0.35).

## Known shortcomings

- Tier C: CHANGES 0.8 numbers (qsort 300010 vs 679414 cycles, bsearch 553 vs 3352) date from 2001 or earlier with no benchmark code, compiler, flags, CPU or glibc version. The measured qsort was since replaced (2003-11-02 rewrite, 2006-08-16 'faster qsort', 2019 rand_i pivot); a 2016 nullprogram animation (snippet only) shows glibc at 307 frames vs dietlibc 0.32 at 503, so probably not faster today; the 6x bsearch gap is likely a first-call/PLT artefact; the current qsort uses a byte-swap loop with no recursion bound. Abandoned (mirror archived 2023-09-05, last commit 2019-03-18); GPL-2.0-or-later; fefe.de blocked.
- Enricher: the closest harness is t.c in the 2001 commit 344deb2; it times one rdtsc call each with SIZE 100000 (not the 1000 the changelog quotes); the warm-up qsort(array,2) sorts 8 bytes so glibc 2.2's msort uses an alloca buffer, and the timed glibc call is its first over 1024 bytes and pays sysconf(_SC_PHYS_PAGES) (stdio parse of /etc/mtab and /proc/meminfo) plus malloc/free; bsearch gets no warm-up; the in-repo test/qsort.c comparator has an inverted loop that always returns 0, so its sort check never fires. Bugs in the measured code: the 2001 qsort never moves the left scan past pivot-equal keys, so equal or few-distinct input goes quadratic (Python port: 1,001,948 comparisons, depth 993 on 1000 equal ints); the 2001 bsearch shrinks the window by num, not num+1, reads past the array end, misses present keys and reads base[0] when nmemb is 0 (fixed across 0.10/0.11/0.13/0.15). Pivot history: rightmost pivot 2006-08-16 to 2012-08-27 (635fb76, quadratic on sorted input), random pivot via rand() in 2012, rand_i swapped in 2019. HEAD qsort makes about 1.8x more comparator calls than merge sort on random keys (15,814 vs 8,735); byte swaps; -Os on x86_64; no recursion depth bound; rand_i static seed races across threads.

## Caveats and trade-offs

First-party, one changelog line from the 0.8 release (2001 or earlier) with no benchmark program, compiler, flags, CPU model or glibc version stated; the author adds 'I have no idea why glibc is so slow.' The measured qsort no longer exists: lib/qsort.c was rewritten on 2003-11-02 ('write new qsort that does not fail so'), again on 2006-08-16 ('faster qsort', the 0.31 'faster qsort' changelog line) and given a random pivot on 2019-01-29, so the 2.3x figure describes code that is gone. The current qsort is a recursive Sedgewick 3-way quicksort with a byte-by-byte swap loop, no insertion-sort cutoff and no recursion-depth bound; glibc's qsort has also changed many times since 2001. Independent counter-evidence (snippet only, nullprogram.com 2016 'Inspecting C's qsort Through Animation', page EGRESS_BLOCKED): glibc's qsort finished the animated sort in 307 frames versus 503 for dietlibc 0.32, and the author calls dietlibc 'optimized for size, which shows through its slower performance'. The bsearch gap (3352 vs 553 cycles for a single lookup in 1000 ints, about 10 comparisons) is far larger than two plain binary searches can differ algorithmically; it probably reflects first-call costs such as lazy PLT binding of a dynamically linked glibc or cold caches, which the changelog does not control for. Size is dietlibc's real selling point and is not benchmarked in the repo. The FAQ says dietlibc can 'improve performance by an order of magnitude for certain programming models' and points to fefe.de/fnord/SPEED; fefe.de was EGRESS_BLOCKED here. The same changelog notes an i386 strlen that is '31% faster, 14% smaller', but its baseline is the older dietlibc C version, not glibc. repo_url is the unofficial ensc git-cvs mirror, archived 2023-09-05 with its last commit on 2019-03-18; upstream lives in CVS at cvs.fefe.de and may be newer (the mirror's CHANGES already has an unreleased 0.35 section). License is GPL-2.0 'or later' per README, so linking it into distributed binaries carries GPL obligations. [retier] 2001 changelog cycle counts (qsort 300010 vs 679414, bsearch 553 vs 3352) from harness t.c (commit 344deb2): one rdtsc call each, glibc's timed call pays sysconf(_SC_PHYS_PAGES) and malloc on first use, bsearch unwarmed. Measured qsort went quadratic on equal keys and measured bsearch read past the array end (fixed 0.10-0.15); qsort rewritten 2003, 2006, 2012 (rand pivot) and 2019. HEAD qsort makes about 1.8x more comparisons than glibc's merge sort on random keys. Mirror archived; upstream last commit 2019-03-18; GPL-2.0-or-later.

A libc built for the smallest static Linux binaries (the dietlibc README says to use it for programs that do not need the bloat of glibc). Static linking only, GCC-only, no FreeBSD/Solaris/Windows support (FAQ), GPL-2.0-or-later licence, so statically linked programs carry the GPL. The qsort/bsearch comparison is a data point for the libc's small routines; the project's headline claim is size, not speed.

## Maintenance

The ensc git-cvs mirror is archived (2023-09-05, last commit 2019-03-18; upstream is CVS at cvs.fefe.de) and the code is usable as part of dietlibc under GPL-2.0-or-later, but the benchmarked qsort and bsearch are gone and the 2.3x/6.1x figures are historical and probably not reproducible against current glibc, whose qsort is now a merge sort with a heapsort fallback.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The CHANGES file's 0.8 entry (lines 1083-1086) states 'Benchmark on 1000 random ints: glibc: 679414 cycles qsort and 3352 cycles bsearch / diet libc: 300010 cycles qsort, 553 cycles bsearch', matching the record; it is a first-party changelog line with no benchmark code in the repo, no compiler, flags, CPU model or glibc version, so C.
- **Retiered** C to D: The 2001 cycle counts come from a harness whose glibc call pays first-call sysconf and malloc costs while dietlibc gets the warm path, and the measured dietlibc qsort and bsearch had correctness bugs (quadratic on equal keys; bsearch reads past the array end and misses present keys) that were fixed later, so the numbers describe neither the current code nor a fair comparison (bug-in-measured-path precedent). Directional only.
- **Verifier notes:** Numbers are on the page exactly as recorded and the baseline (glibc qsort/bsearch) is named, so the entry stands at tier C, but the claim is a 25-year-old one-liner about a qsort implementation that has since been replaced twice, and a 2016 independent animation (snippet only) shows dietlibc 0.32's qsort doing more work than glibc's; record it as 'probably not faster today, measured code gone, no methodology'. maintenance_status corrected to abandoned (mirror archived 2023-09-05, last commit 2019-03-18). Not a duplicate of any listed project.
- **Fields the verifier corrected:** `maintenance_status`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/CHANGES>
  - <https://github.com/ensc/dietlibc>
  - <https://github.com/ensc/dietlibc/commits>
  - <https://github.com/ensc/dietlibc/commits/master/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/COPYING>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/README>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/FAQ>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/lib/bsearch.c>
- **Sources the enricher read:**
  - <https://github.com/ensc/dietlibc>
  - <https://github.com/ensc/dietlibc/commits/master/lib/qsort.c>
  - <https://github.com/ensc/dietlibc/issues?q=is%3Aissue>
  - <https://github.com/ensc/dietlibc/tree/344deb240aed7bc32597a1941e292ca17ed58bee>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/README>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/FAQ>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/BUGS>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/COPYING>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/Makefile>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/x86_64/Makefile.add>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/i386/Makefile.add>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/dietfeatures.h>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/include/stdlib.h>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/lib/bsearch.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/lib/rand_i.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/lib/rand_r.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/test/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/test/bsearch.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/HEAD/test/stdlib/testsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/344deb240aed7bc32597a1941e292ca17ed58bee/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/344deb240aed7bc32597a1941e292ca17ed58bee/lib/bsearch.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/344deb240aed7bc32597a1941e292ca17ed58bee/lib/rand.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/344deb240aed7bc32597a1941e292ca17ed58bee/CHANGES>
  - <https://raw.githubusercontent.com/ensc/dietlibc/344deb240aed7bc32597a1941e292ca17ed58bee/t.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/45efc35bb6bd49520baa99ca7707ce4d6ba0cce4/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/4403ff30651cc2d7c97f7a27815a2199740453a8/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/0fb87e6fe9d672070f3d9bda67b07bd217515af2/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/29c21485753418dc9440ea6d32c1da785eccdd00/lib/qsort.c>
  - <https://raw.githubusercontent.com/ensc/dietlibc/635fb7644a5cfe4be050662bfe63fba19e85e8c6/lib/qsort.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.2/stdlib/msort.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.2.2/stdlib/msort.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.2/sysdeps/unix/sysv/linux/getsysstats.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.2/sysdeps/posix/sysconf.c>
  - <https://raw.githubusercontent.com/bminor/glibc/glibc-2.39/stdlib/qsort.c>
  - <https://raw.githubusercontent.com/bminor/glibc/master/stdlib/qsort.c>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ensc/dietlibc`) · [data/wave1/enrich/raw/github_com_ensc_dietlibc.json](../../../data/wave1/enrich/raw/github_com_ensc_dietlibc.json) (enrichment confidence 0.75)

</details>
