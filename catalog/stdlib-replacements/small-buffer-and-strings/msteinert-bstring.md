# bstring

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause OR GPL-2.0-only` · 🟢 active

> Maintained fork of Paul Hsieh's Bstrlib: length-prefixed, auto-growing C strings that avoid strcat-style rescans of char\* code.

| | |
|---|---|
| **Beats** | C standard library char\* string functions (strcpy, strcat, strchr, strstr, strcspn, memmove) |
| **Claimed result** | Bstrlib C API as percent of char\* Clib speed (100% is parity), columns WATCOM C 11.0c / Visual C++ 6.0 / Intel C++ 6.0 / gcc 3.3.3 Cygwin / gcc 3.3.3 Power 4 SUSE: concatenation 21700% / 23700% / 21200% / 9260% / 3980%; assignment 182% / 198% / 218% / 89% / 91%; scan 214% / 125% / 159% / 209% / 89%; char extraction 95% / 96% / 101% / 102% / 113%; replace 147% / 114% / 125% / 101% / 86%. Same page, CBString over std::string (WATCOM + STLport / Visual C++ 6.0 / Intel C++ 6.0 / g++ 3.3.3 Cygwin / g++ 3.3.3 Power 4): char \* assignment 93% / 248% / 264% / 537% / 132%; char extraction 63% / 118% / 123% / 132% / 100%; scan 155% / 143% / 178% / 274% / 192%; concatenation 187% / 21100% / 19400% / 1330% / 200%; replace 144% / 95% / 110% / 108% / 135%. |
| **Workload** | Upstream Bstrlib's cbench.c example (examples-09282006.zip): operations per second for assignment, char extraction, scan, concatenation (250 appends of a 60 character string plus '!!' into one growing buffer, buffer reset each iteration) and replace, bstring C API against plain char\* code (strcpy, strchr, strstr, strcspn, strcat, memmove/memcpy). The same page also benchmarks upstream's C++ wrapper CBString against std::string with cppbench.cpp. |
| **Metric** | throughput |
| **Hardware** | Athlon XP 1.620GHz (all Windows/Cygwin columns); Power 4 1GHz (SUSE Linux column) |
| **Compiler and flags** | WATCOM C/C++ 11.0c (with STLport for C++), Visual C++ 6.0 (12.00.8168), Intel C++ 6.0 (4.0 99026), gcc/g++ 3.3.3 on Cygwin and on SUSE Linux. The page says only that the compiler must be set to 'a reasonable maximum performance setting', for most compilers 'a flag such as -O2'; the makefiles shipped in examples-09282006.zip use gcc -O3 (Makefile.gccXnix), MSVC /O2 (plus /Ob2 for C++) and Intel /Ox /Ob2, but the page does not say these were the flags used. |
| **Adoption** | 175 stars (msteinert fork); upstream websnarf/bstrlib 570 stars; packaged in many distributions per the README's repology badge |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/msteinert/bstring) · [benchmark](https://bstring.sourceforge.net/features.html) |

## Verdict

Upstream Bstrlib's cbench.c (operations per second, results given as percentages of char\* speed) ran on a 1.62 GHz Athlon XP with WATCOM 11.0c, Visual C++ 6.0, Intel C++ 6.0 and Cygwin gcc 3.3.3, and on a 1 GHz Power 4 with gcc 3.3.3. Flags are not stated; the shipped makefiles use -O3. Concatenation was 40x to 237x faster than repeated strcat. Scan was 0.89x to 2.14x, but on unequal inputs. Assignment (0.89x to 2.18x), replace (0.86x to 1.47x) and char extraction (about 1x) were close to parity. None of this was re-measured on the msteinert fork.

## Use it when

- C code that builds strings incrementally (logs, protocol messages, templating) where char\* code would call strcat or strlen repeatedly on a growing buffer.
- C projects that want bounds-checked string handling with explicit error returns, plus split, find/replace and formatted append, in one BSD-3-Clause (or GPL-2.0) library.
- Mixed codebases that still pass strings to char\* APIs: the data stays NUL-terminated, and bsStatic/blk2tbstr wrap existing buffers without allocation.
- Linux and BSD distributions where a packaged, maintained shared library (libbstring, soversion 1) is preferred over vendoring.

## Skip it when

- C++ code: the fork has no CBString wrapper, and std::string today has amortized appends and small-string optimization, so the 2000s std::string results do not carry over.
- Short fixed strings where char\* code already tracks its end pointer: the measured assignment and replace rows ranged from 86% to 218% of char\* speed, a wash on gcc.
- Strings over INT_MAX bytes (lengths are int) or heap-less/freestanding targets (needs malloc, realloc, vsnprintf).
- Substring search on long or adversarial inputs: binstr is brute force with an O(n\*m) worst case, unlike glibc's strstr/memmem.
- Performance-critical choices that need current numbers: the only benchmarks are upstream's percentages from a 1.62 GHz Athlon XP and a 1 GHz Power 4.

## How it is fast

Length is stored, so appends copy only the new bytes at slen (memmove) instead of rescanning the destination as strcat does, and length queries are O(1). Capacity grows to the next power of two above the request (snapUpSize), using realloc when the string fills more than 7/8 of its buffer and malloc+copy otherwise, so repeated appends amortize to linear time. Character searches use memchr (bstrchr) or a 256-bit character bitmap (binchr, like strcspn); substring search (binstr, used by bfindreplace) is a 2x-unrolled brute-force scan, not Two-Way.

## Compared with alternatives

Pick bstring over buffet (the other C string library in the catalogue) when you want a mature, distro-packaged, fuzzed API with find/replace, split and formatting rather than small-string optimization; the C++ siblings (FastString, MengRao/str, jank persistent_string) target std::string and are the better choice inside C++.

## Integration

| | |
|---|---|
| **Form** | shared lib (Meson; bstrlib.c and bstraux.c can also be dropped into a tree) |
| **Dependencies** | C library only (memcpy, memmove, malloc, realloc, free, vsnprintf); Check for tests, Doxygen for docs, clang/libFuzzer for fuzzing |
| **Minimum toolchain** | C99 (meson c_std=c99); Meson + Ninja for the provided build |
| **Platforms** | any hosted C platform; CI includes FreeBSD, NetBSD, OpenBSD and OpenIndiana VMs (vmactions); MSVC warnings addressed (#103) |
| **Thread safety** | no global or static state; distinct bstrings are independent, and a shared bstring needs external locking for writes (or write protection for read-only use) |
| **Drop-in for the baseline** | partial: bdata() gives a NUL-terminated char\* for reading, but creating and modifying strings needs the bstring API |

## Gotchas

- Harness flaws behind the headline numbers (upstream cbench.c): the scan row times bstring on 'Dot. 123. Some more data.', where '.' sits at offset 3 and "123" at offset 5, against strchr/strstr over the 60-byte TESTSTRING1, which contains neither, so the char\* side scans the whole string twice. The 21700-23700% concatenation row times strcat rescanning a growing 15.5 KB buffer 500 times per pass (quadratic) against bconcat's append.
- Correctness bug in the char\* concatenation baseline: accum is ((sizeof TESTSTRING1) + 1) \* 250 = 15500 bytes, but 250 appends of 60 + 2 characters fill 15500 bytes and the final NUL lands at index 15500, a one-byte overrun of a static array (undefined behavior). It does not change the timing much, but the baseline code is not valid C.
- bstraux helpers had memory-safety bugs that this fork fixed only in March 2026: an out-of-bounds read in bNetStr2Bstr on a crafted netstring length (#149), and OOM plus a leak in bUuDecodeEx on malformed input (#148). Upstream websnarf/bstrlib (last commit 2016-11-02) has no such fixes, so use this fork rather than upstream.
- Lengths are int and negative mlen/slen act as invalid markers; bconcat and similar functions handle aliased arguments (e.g. appending a string to itself) by copying first; bsStatic strings are write-protected at runtime, so modifying or destroying them through the API fails with BSTR_ERR rather than trapping. Check every return code.

## Known shortcomings

- Numbers are upstream Bstrlib's 2000s features.html (Athlon XP, Power 4, '-O2' example), never re-benchmarked by the fork; cbench.c's scan row compares different strings (char\* scans a 60-char string with no match while bstring finds targets within 6 chars) and the concatenation win comes from quadratic strcat. Licence BSD-3-Clause OR GPL-2.0-only.
- Upstream cbench.c (examples-09282006.zip) confirms the scan flaw: the char\* side scans 60 bytes with no match while bstring finds its targets at offsets 3 and 5; the concat row times a quadratic strcat; the char\* concat baseline overruns its static accumulator by 1 byte (15500-byte buffer, needs 15501 for the final NUL; undefined behaviour). binstr/bfindreplace are brute-force O(n\*m) in the worst case. bstraux out-of-bounds read in bNetStr2Bstr (#149) and bUuDecodeEx OOM/leak (#148) were fixed in the fork in March 2026 but are absent upstream (dead since 2016). No re-benchmark of the fork.

## Caveats and trade-offs

The numbers are for upstream Bstrlib (websnarf/bstrlib, last commit 2016-11-02), measured with 2000s era compilers on a 1.62GHz Athlon XP and a 1GHz Power 4; the msteinert fork is described as binary compatible but was not re-benchmarked, and the CBString versus std::string rows apply only to upstream because the fork dropped the C++ wrapper. First-party project page with percentages only (no raw ops/s), no date, and flags not tied to the run, so tier C. The page's cbench.c/cppbench.cpp links point at the dead cvs.sourceforge.net; the code is in examples-09282006.zip on the SourceForge downloads page. The large concatenation ratios come from the baseline calling strcat repeatedly on a growing buffer (rescanning the whole string every call, quadratic) while bstring tracks length; a C program that keeps its own end pointer would not lose this much. The scan row is not like for like: in cbench.c the char\* test runs strchr '.', strstr "123" and strcspn "sm" over the 60-character TESTSTRING1, which contains neither '.' nor "123" (both calls scan the whole string), while the bstring test searches the 25-character 'Dot. 123. Some more data.', where '.' and "123" are found within the first six characters; the scan percentages therefore overstate bstring. The std::string comparison used old STLs (WATCOM with STLport, Visual C++ 6.0 and Intel C++ 6.0 sharing Microsoft's STL, g++ 3.3.3 libstdc++); the page itself attributes the 19400-21100% concatenation results to Microsoft's STL implementing concat as O(m+n), so they reflect a since-fixed library defect rather than a lasting advantage. std::string was faster or equal in some rows (char extraction 63% with STLport, replace 95% with Visual C++ 6.0, assignment 93% with STLport) and the C API loses on assignment and replace in some columns (89%, 91%, 86%). The fork's own README claims 'improved overall performance of common string operations' and doc/comparisons.md discusses performance qualitatively, with no numbers.

Length-prefixed string struct (slen, mlen, data) that stays NUL-terminated for interop with char\* code, so length is O(1) and appends amortize, at the cost of a header and a different API from &lt;string.h&gt;. Dual licensed BSD-3-Clause or GPL-2.0 (user's choice). This fork is pure C: it removed upstream's C++ wrapper (CBString, bstrwrap) and the const_bstring type, and adds Meson build, Check tests, fuzzing and CI.

## Maintenance

Actively maintained (v1.1.1 on 2026-09-04, last commit 2026-09-12; fuzzing, CodeQL and Scorecard in CI) and dual-licensed BSD-3-Clause or GPL-2.0. Upstream is unmaintained since 2016, and its benchmark numbers date from the gcc 3.3 era.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Upstream author's project page (bstring.sourceforge.net/features.html) gives percentage tables from cbench.c (bstring vs char\* Clib) and cppbench.cpp (CBString vs std::string) with compiler versions and CPUs, but the flags used for the run are not stated (only 'a flag such as -O2'), no raw numbers or date are given, and the numbers are for upstream Bstrlib, not this fork; first-party with partial methodology, so C.
- **Verifier notes:** All percentages on the page match the record; the CBString assignment and scan rows were added to claimed_speedup. Checked cbench.c from examples-09282006.zip: the scan row compares different input strings (char\* searches 60 chars with no match, bstring finds its targets within 6 chars), and the concatenation win comes from repeated strcat on a growing buffer; both are harness flaws to record as shortcomings, not grounds for rejection since concatenation and assignment wins are genuine algorithmic effects. License corrected to dual BSD-3-Clause or GPL-2.0 at the user's option (COPYING plus README); 175 stars and last commit 2026-09-12 confirmed; upstream websnarf/bstrlib has 570 stars, last commit 2016-11-02.
- **Fields the verifier corrected:** `license`, `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** upstream Bstrlib page and cbench.c (verifier); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://bstring.sourceforge.net/features.html>
  - <https://bstring.sourceforge.net/>
  - <https://prdownloads.sourceforge.net/bstring/examples-09282006.zip?download>
  - <https://github.com/msteinert/bstring>
  - <https://github.com/msteinert/bstring/commits>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/README.md>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/COPYING>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/doc/comparisons.md>
  - <https://github.com/websnarf/bstrlib>
  - <https://github.com/websnarf/bstrlib/commits>
- **Sources the enricher read:**
  - <https://github.com/msteinert/bstring/issues?q=is%3Aissue>
  - <https://github.com/msteinert/bstring/commits>
  - <https://github.com/msteinert/bstring/pulls?q=is%3Apr+fix>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/README.md>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/COPYING>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/meson.build>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/bstring/meson.build>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/bstring/bstrlib.h>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/bstring/bstrlib.c>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/bstring/bstraux.h>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/doc/comparisons.md>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/doc/introduction.md>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/doc/security.md>
  - <https://raw.githubusercontent.com/msteinert/bstring/HEAD/doc/porting.md>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstrlib.c>
  - <https://bstring.sourceforge.net/features.html>
  - <https://prdownloads.sourceforge.net/bstring/examples-09282006.zip?download>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/msteinert/bstring`) · [data/wave1/enrich/raw/github_com_msteinert_bstring.json](../../../data/wave1/enrich/raw/github_com_msteinert_bstring.json) (enrichment confidence 0.8)

</details>
