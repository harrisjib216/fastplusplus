# toys strstr (SWAR SIMD-friendly Rabin-Karp substring search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> 2014-2016 prototype of Mula's first/last-byte SWAR substring filter, claimed 2-3x over std::string::find; buggy, superseded by sse4-strstr.

| | |
|---|---|
| **Beats** | std::string::find (strstr-stdstring.cpp) and libc strstr (strstr-libc.cpp), both included in the harness; library implementation not stated |
| **Claimed result** | README: 'SWAR algorithm, faster 2-3 times than C++ std::string::find.' (no table in the repo) |
| **Workload** | test64 times libc strstr, std::string::find and the 64-bit SWAR first/last-byte filter (10 iterations each, gettimeofday) for every unique word extracted from i386.txt by make_words.sh, so each search succeeds at the word's first occurrence in the same text; analyze.py then prints a histogram of per-word speed-ratio buckets (slower, same, 2-2.99x, 3-3.99x, ... faster) against std::string::find and against libc strstr. |
| **Metric** | throughput |
| **Compiler and flags** | g++ -Wall -pedantic -std=c++11 -O3 (from strstr/Makefile; compiler version not stated) |
| **Adoption** | 373 stars (toys repo) |
| **Last commit** | 2016-01-17 |
| **Links** | [repository](https://github.com/WojciechMula/toys) · [benchmark](https://github.com/WojciechMula/toys/blob/master/strstr/README.rst) |

## Verdict

The only claim is the README sentence 'faster 2-3 times than C++ std::string::find', with no stored output, CPU or compiler version, from a harness (g++ -O3, i386.txt word list, 10-call gettimeofday timing) whose histogram omits the 1-2x class. The author's later sse4-strstr results for the corrected SWAR code, on the same i386.txt word workload, show 1.70x (ARMv7, GCC 4.9.2) and 3.93x (ARMv8, clang 3.8.0) over std::string::find, but 2.1-3.0x slower than the libc strstr row on four x86 CPUs (derived from page data; libc version not stated).

## Use it when

- Reading or teaching the first/last-byte filter in its simplest scalar SWAR form (about 35 lines).
- As a starting point only after porting the fixes from sse4-strstr's swar64-strstr-v2.cpp: exact zero-byte test, a loop bound that covers the last position, and k=0, k=1 and n&lt;k handled.
- Non-x86 targets with a weak libc strstr: the fixed successor beat std::string::find 1.70x on ARMv7 (GCC 4.9.2) and 3.93x on ARMv8 (clang 3.8.0) in the sse4-strstr result files (derived from page data).

## Skip it when

- Any production use of this copy: by emulating its arithmetic, it returns wrong offsets (false positives), misses matches at the last start position, and runs off the end of the buffer when the needle is longer than the haystack.
- Modern x86-64 hosts: in the author's own later results the fixed SWAR successor was 2.12x slower than the std::strstr (libc) row on Skylake i7-6700, 3.04x slower on Haswell i7-4770, 3.0x on Westmere M540 and 2.53x on Cascade Lake Gold 5217 (derived from page data; libc version not stated); only the Bulldozer FX-8510 run with GCC 4.8.4 was faster (3.2x).
- Haystacks without at least 5 readable bytes after the NUL terminator (memory-mapped files ending at a page boundary, exact-size buffers under ASan).
- Empty needles, needles longer than the haystack, haystacks over 4 GiB (the loop counter is a 32-bit unsigned int), or strict-alignment CPUs (unaligned uint64_t loads through a type-punned pointer).
- When a maintained search is available: sse4-strstr's SIMD and SWAR v2 versions, sliceslice, or the libc/STL routine.

## How it is fast

It is a filter-then-verify search in the Karp-Rabin style where the hash is replaced by a test on the needle's first and last bytes: it XORs 8 haystack bytes at offset i and 8 bytes at offset i+k-1 against broadcast copies of those two needle bytes, ORs the results, and uses the classic SWAR has-zero-byte trick ((v - 0x01..) & \~v & 0x80..) to find candidate positions eight at a time. Only flagged candidates go to memcmp, so on natural text most positions are rejected with plain 64-bit integer operations and no SIMD instructions. This is the generic first/last-byte idea that the author's later sse4-strstr project and the Rust memchr crate's packed-pair prefilter build on.

## Compared with alternatives

Never for production: pick sse4-strstr (catalogued in string-search-and-hashing) for a fixed SWAR fallback or SIMD versions, sliceslice in Rust, or Ron Charlton's strstr.c for portable C; this entry is useful only as the historical first version of the first/last-byte filter.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond &lt;cstring&gt; and &lt;cstdint&gt;; the file has no includes and expects the caller to define NOT_FOUND |
| **Minimum toolchain** | C++11 (uses auto); Makefile builds with g++ -std=c++11 -O3; analyze.py needs Python 2 (print statements) |
| **Platforms** | little-endian with cheap unaligned 64-bit loads (x86-64, AArch64); the candidate-to-index mapping assumes little-endian byte order |
| **Thread safety** | not documented; the function is stateless and reentrant |
| **Drop-in for the baseline** | partial: different signature (pointer, length, NUL-terminated needle) and NOT_FOUND equals npos, but results differ from std::string::find in edge cases and it over-reads the haystack |

## Gotchas

- Correctness bugs confirmed by emulating strstr64's arithmetic in Python (the C++ was not built): the borrow in the has-zero test flags a byte equal to 0x01 directly above a real candidate, and memcmp checks only needle[1..k-1], so 'abb' in 'a`bb' returns 1 instead of not-found and 'all' in 'xx a`ll yy all' returns 4 instead of 11; the bound 'i &lt; n - k' with step 8 skips start position n-k when n-k is a multiple of 8 (needle equal to the haystack, or 'XYZ' at offset 16 of a 19-byte string, returns not-found); n &lt; k makes n - k wrap and the scan runs past the buffer; an empty needle indexes needle[-1].
- Reads up to 5 bytes past the haystack's NUL terminator (block loads and memcmp at offsets up to n+5); the test harness gets away with it only because std::string storage sits inside a larger malloc chunk.
- Harness flaw: analyze.py has no bucket for speedups between 1.0 and 2.0, so classify() returns None for them and print_summary never prints that class while still counting it in the total; the histogram that backs the '2-3x' claim hides every word where the gain was under 2x, and its percentages do not sum to 100.
- Harness flaw: each word is timed as 10 calls between gettimeofday readings (1 us resolution, no warm-up, one run) on words taken from the searched text, so most searches stop near the start; a 0 us custom time prints 'faster inf' and lands in the 6x-and-up bucket, and both at 0 us prints 'same speed'. The 'custom vs strlen' heading is really custom vs libc strstr.

## Known shortcomings

- The claim is one README sentence ('2-3x vs std::string::find') with no results, CPU or compiler version (10 gettimeofday iterations); reading strstr64 (not run) shows a borrow false positive with the first byte unchecked ('abb' in 'a`bb' returns 1), the last start position skipped and reads past the end. Lowered to D (unmeasured, buggy fast path).
- Correctness bugs confirmed by emulation: 'abb' in 'a`bb' returns 1 and 'all' in 'xx a`ll yy all' returns 4 instead of 11 (the borrow in the has-zero test flags a byte equal to 0x01 above a real candidate and memcmp checks only needle[1..k-1]); the last start is skipped when n-k is a multiple of 8; n&lt;k wraps past the buffer; an empty needle reads needle[-1]; reads run 5 bytes past the NUL; strstr32 shares the bugs. analyze.py has no 1.0-2.0 bucket (sub-2x gains are invisible), gettimeofday timing at 1 us granularity over 10 calls prints 'faster inf' at 0 us. Counter-evidence from the sse4-strstr results for swar64-strstr-v2: 1.70x (ARMv7) and 3.93x (ARMv8) over std::string::find, but 2.12-3.04x slower than libc strstr on i7-6700, i7-4770, M540 and Gold 5217.

## Caveats and trade-offs

The 2-3x figure is a single README sentence matching analyze.py's '2.00 - 2.99 faster' bucket; no stored output, CPU, compiler version or libstdc++/glibc version, so it cannot be checked without running (the Makefile wgets i386.txt from an MIT course URL). The harness also times libc strstr (analyze.py and the README mislabel it 'strlen'), but no margin over strstr is claimed; strstr must also scan for the terminator while the SWAR routine gets the length. Timing is 10 iterations with microsecond gettimeofday and no warm-up, and words are taken from the searched text, so many searches end early and are timer-resolution noise. By code reading (not run), strstr64.cpp has correctness bugs: the SWAR zero-byte test can flag the byte above a real candidate through borrow, and memcmp checks only needle[1..k-1], so needle 'abb' in text 'a`bb' returns 1 instead of not-found; the loop 'i < n - k' with step 8 skips the last start position when n-k is a multiple of 8; and the 8-byte loads read up to 5 bytes past the string terminator. verify.cpp checks only words from the same text, so these cases are not exercised. The linked article 0x80.pl/articles/simd-friendly-karp-rabin.html was unreachable (DNS ENOTFOUND). last_commit is the last commit touching strstr/ (2016-01-17); the toys repo itself was last pushed 2026-04-08. Shares its repo URL with the avx512-string entry, which needs separate ids at merge time. [retier] The 2-3x figure is a single README sentence matching analyze.py's '2.00 - 2.99 faster' bucket; no stored output, CPU, compiler or library versions. analyze.py has no 1.0-2.0 bucket (sub-2x gains are invisible), timing is gettimeofday at 1 us granularity over 10 calls and 0 us prints 'faster inf'. The harness also times libc strstr (mislabelled 'strlen'), with no margin claimed. Correctness bugs confirmed by emulating strstr64: 'abb' in 'a`bb' returns 1 and 'all' in 'xx a`ll yy all' returns 4 instead of 11 (the has-zero borrow flags a byte equal to 0x01 above a real candidate and memcmp checks only needle[1..k-1]); the last start is skipped when n-k is a multiple of 8; n&lt;k wraps past the buffer; an empty needle reads needle[-1]; reads run 5 bytes past the NUL; strstr32 shares the bugs. Counter-evidence from the author's sse4-strstr results for the fixed swar64-strstr-v2: 1.70x (ARMv7) and 3.93x (ARMv8) over std::string::find, but 2.12-3.04x slower than libc strstr on i7-6700, i7-4770, M540 and Gold 5217.

Portable SWAR (plain 32/64-bit integer arithmetic, no SIMD intrinsics), so it needs no special CPU; tuned for short needles taken from English text. The author's later SIMD versions are in the separate sse4-strstr project (already catalogued).

## Maintenance

Abandoned: the strstr directory's last commit is 2016-01-17 and the code was superseded by sse4-strstr in 2016; BSD-2-Clause and tiny, but it should not be vendored without the v2 fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party one-sentence claim ('faster 2-3 times than C++ std::string::find') in strstr/README.rst; the harness (strstr/test.cpp, analyze.py, Makefile with g++ -O3) is public but no results, CPU model or compiler version are stored, so it falls short of A and has no independent measurement for B.
- **Retiered** C to D: Enricher: D stands; the kernel has confirmed false positives and over-reads, and the author's later sse4-strstr results show swar64-strstr-v2 slower than libc strstr on four x86 CPUs; caveats corrected.
- **Verifier notes:** Claim and harness verified on github.com and raw files; tier C stands. Shortcomings for the orchestrator: single-sentence first-party claim with no stored results or CPU; noisy 10-iteration gettimeofday timing; code-reading correctness bugs in strstr64 (borrow false positive with unchecked first byte, skipped last position, over-read) that rarely trigger on the word-list workload.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-35 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/WojciechMula/toys>
  - <https://github.com/WojciechMula/toys/tree/master/strstr>
  - <https://github.com/WojciechMula/toys/commits/master/strstr>
  - <https://github.com/WojciechMula/toys/commits/master>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/test.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/analyze.py>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/strstr-libc.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/strstr-stdstring.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/strstr64.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/verify.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/make_words.sh>
- **Sources the enricher read:**
  - <https://github.com/WojciechMula/toys>
  - <https://github.com/WojciechMula/toys/tree/master/strstr>
  - <https://github.com/WojciechMula/toys/commits/master/strstr>
  - <https://github.com/WojciechMula/toys/issues?q=is%3Aissue+strstr>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/test.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/analyze.py>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/strstr-libc.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/strstr-stdstring.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/strstr64.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/strstr32.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/verify.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/make_words.sh>
  - <https://raw.githubusercontent.com/WojciechMula/toys/HEAD/strstr/.gitignore>
  - <https://github.com/WojciechMula/sse4-strstr>
  - <https://github.com/WojciechMula/sse4-strstr/tree/master/results>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/swar64-strstr-v2.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/swar32-strstr-v2.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/scalar.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/results/skylake-i7-6700-gcc5.4.1-avx2.txt>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/results/haswell-i7-4770-gcc5.4.1-avx2.txt>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/results/westmere-m540-gcc6.2.0-sse4.txt>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/results/bulldozer-fx-8510-gcc4.8.4-sse.txt>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/results/cascadelake-Gold-5217-gcc-7.4.0-avx512bw.txt>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/results/armv7-32bit-gcc4.9.2.txt>
  - <https://raw.githubusercontent.com/WojciechMula/sse4-strstr/HEAD/results/armv8-64bit-clang3.8.0.txt>
  - http://0x80.pl/notesen/2016-11-28-simd-strfind.html (unreachable: getaddrinfo ENOTFOUND 0x80.pl)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `paper:wojciechmula-toys-strstr-swar`) · [data/wave13/enrich/raw/paper_wojciechmula_toys_strstr_swar.json](../../../data/wave13/enrich/raw/paper_wojciechmula_toys_strstr_swar.json) (enrichment confidence 0.8)

</details>
