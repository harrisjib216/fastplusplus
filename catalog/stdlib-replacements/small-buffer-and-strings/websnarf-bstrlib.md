# Bstrlib (The Better String Library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Paul Hsieh's original length-tracked C string library (plus CBString C++ wrapper) replacing string.h char\* handling.

| | |
|---|---|
| **Beats** | C standard library char\* string functions (string.h strcat/strcpy/strstr) for the C API; std::string for the CBString C++ wrapper |
| **Claimed result** | Ratios on the page are Bstrlib/baseline in percent (legend '(bstring / Clib)' and '(CBString / std::string)'; above 100% means Bstrlib faster). C API vs C library, gcc 3.3.3 SUSE Linux column: concatenation 3980% (about 40x, derived from page data), assignment 91%, character extraction 113%, scan 89%, replace 86%; concatenation is 21700% (WATCOM), 23700% (VC++ 6.0), 21200% (Intel 6.0), 9260% (gcc Cygwin). CBString vs std::string, g++ 3.3.3 SUSE Linux column: concatenation 200%, scan 192%, replace 135%, assignment 132%, character extraction 100%; VC++ 6.0 concatenation 21100%, Intel 6.0 19400%, g++ Cygwin 1330%. Page also says default construction is far slower than std::string. |
| **Workload** | Author's example benchmark programs (cbench.c for the C API against string.h, cppbench.cpp for CBString against std::string, mfcbench.cpp against MFC CString) timing char\* assignment, character extraction, scan, concatenation and replace, run with five compiler/platform combinations. |
| **Metric** | throughput |
| **Hardware** | Athlon XP 1.620Ghz (first four columns: WATCOM, VC++ 6.0, Intel 6.0, g++ Cygwin) and Power 4 1Ghz (g++ SUSE Linux column), per the page's table header |
| **Compiler and flags** | Per column: WATCOM C/C++ 11.0c with STLport, Visual C++ 6.0 (12.00.8168), Intel C++ 6.0 (4.0 99026), GNU gcc/g++ 3.3.3 (Cygwin), GNU gcc/g++ 3.3.3 (SUSE Linux). Flags used for the published numbers are not stated; the page only says Bstrlib must be built at a maximum optimisation setting such as -O2. The later SourceForge examples archive (examples-09282006.zip) ships makefiles with gcc -O3 -Wall -pedantic -ansi -s (Makefile.gccXnix), MSVC /O2 /Ob2 (Makefile.msvc), Intel /Ox /Ob2 (Makefile.intel) and WATCOM -oairten -6r (Makefile.watcom), but it is not known that these were used for the page's runs. |
| **Adoption** | 572 stars |
| **Last commit** | 2016-11-02 |
| **Links** | [repository](https://github.com/websnarf/bstrlib) · [benchmark](https://bstring.sourceforge.net/features.html) |

## Verdict

The author's features.html tables (single clock()-timed runs, flags not stated) put the Bstrlib C API at about 40x to 237x the speed of strcat-based concatenation and roughly 0.86x to 2.2x on assignment, character extraction, scan and replace, and CBString at 1.0x to 2.0x std::string on g++ 3.3.3 (Power 4) with up to 211x on Visual C++ 6.0's STL, which the page attributes to that STL's O(m+n) append. Runs used WATCOM 11.0c, VC++ 6.0, Intel C++ 6.0 and gcc 3.3.3 on an Athlon XP 1.62 GHz and a Power 4 1 GHz; the concatenation gaps reflect quadratic strcat and a 2004-era STL, and the C-API scan row compares different input strings.

## Use it when

- C code that builds strings by repeated appends (strcat/sprintf-into-buffer loops, log or report assembly), where the quadratic rescans are the cost
- C code that needs bounds-safe string handling with length-based compare and embedded NUL bytes, while still handing NUL-terminated char\* to other APIs
- Line-oriented parsing of cached files or sockets through bsreadln/bStream with your own read callback
- Legacy codebases already on Bstrlib that cannot take a new build system (two .c files, no dependencies beyond the C library)

## Skip it when

- New projects: upstream has had no commit since 2016-11-02; use the msteinert/bstring fork, which carries fixes (bsplitstr multi-character delimiter, bstraux memory-safety bugs) that upstream lacks
- Many short or default-constructed strings: every bstring is a malloced header plus a separately malloced buffer of at least 8 bytes, and CBString's default constructor mallocs, so there is no small-string optimisation
- Strings of 2 GiB or more: lengths are int, capped at INT_MAX (open issue #5)
- Inside modern C++: CBString has no move semantics (open issue #11) and its published wins over std::string were measured on 2004-era STLs; std::string is the safer default there
- Substring search on long texts: binstr is a scalar brute-force loop (binstrcaseless is documented as O(m\*n)), not a linear-time or SIMD algorithm

## How it is fast

The stored length makes length, append and equality checks O(1) instead of strlen-style rescans: bconcat copies only the appended bytes with memmove, while strcat in a loop rescans the growing destination each call (quadratic). Buffers grow to the next power of two (snapUpSize) so repeated appends rarely reallocate, and balloc picks realloc or malloc+copy depending on how full the buffer is. Searches use memchr for single characters, a 256-entry bit table (charField) for character-set scans, and a hand-unrolled brute-force loop for binstr.

## Compared with alternatives

Pick the upstream library only when you must match an existing Bstrlib vendor drop; otherwise msteinert/bstring is the same API with fixes, fuzzing and packaging. Against buffet (small-string optimised C strings) or the C++ siblings (FastString, MengRao/str), choose Bstrlib/bstring for a broad, mature C string API rather than for raw small-string speed.

## Integration

| | |
|---|---|
| **Form** | source-drop (bstrlib.c/bstrlib.h; optional bstraux.c, bstrwrap.cpp, bsafe.c, utf8util.c, buniutil.c) |
| **Dependencies** | C library only (memcpy, memmove, malloc, realloc, free, vsnprintf); CBString optionally uses STL and iostream |
| **Minimum toolchain** | ANSI/ISO C (C89) and ISO C++98; documented as tested with gcc/g++, MSVC, Intel C++, WATCOM, Borland C++ and Turbo C; no build files or build instructions in the repo (issue #3) |
| **Platforms** | any hosted C platform (Windows, Linux, Mac OS X; x86 and PPC64 named in porting.txt); not for freestanding/ROM targets |
| **Thread safety** | no static or global state and functions are re-entrant; a shared bstring needs external locking for writes or runtime write protection for read-only sharing |
| **Drop-in for the baseline** | partial: bdata()/-&gt;data give a NUL-terminated char\* for reading, but creating and modifying strings requires the bstring API; CBString is not source-compatible with std::string |

## Gotchas

- Harness defects in the published numbers (cbench.c in the 2006 SourceForge examples archive): the C-API scan row times strchr/strstr on the 60-character TESTSTRING1, which contains neither '.' nor "123" (full scans), against bstrchr/binstr on "Dot. 123. Some more data." with hits at offsets 3 and 5; the concatenation row is quadratic strcat against bconcat; and the char\* concat buffer is 15500 bytes while 250 appends write 15500 characters plus a NUL, a one-byte overrun. cppbench.cpp's CBString vs std::string tests use the same inputs and idioms on both sides.
- Upstream bstraux.c bNetStr2Bstr reads buff[i + 1 + x] for an attacker-supplied length x without checking the buffer, an out-of-bounds read on crafted netstrings; the fork fixed this in 2026, upstream did not. Open issues also report bsplitstr mis-splitting on multi-character delimiters (#27, "aXXXXb" on "XX") and intermittent access violations in CBString::format (#21), with no maintainer reply.
- Functions return BSTR_ERR or NULL instead of failing loudly; bsStatic/tagbstring literals are write-protected and mutating calls on them fail, so every return code must be checked. In CBString without BSTRLIB_THROWS_EXCEPTIONS, an out-of-range const character() read returns '\0' rather than throwing.
- Mutating functions may free() or realloc() any bstring passed to them, so hand-built bstrings must have malloced headers and data; buffers grow to powers of two and never shrink unless ballocmin is called.

## Known shortcomings

- 2004-era runs; the cbench.c/cppbench.cpp makefiles (-O3, /O2, /Ox) date from 2006, so flags are unconfirmed. The C-API concat test calls strcat 500x into a growing buffer, a quadratic baseline. Abandoned (last commit 2016-11-02).
- Enricher: cbench.c's C-API scan row searches different strings on each side (the char\* side scans a whole string with no hit) and its char\* concat baseline overruns a 15500-byte buffer by one byte (undefined behaviour); bstraux bNetStr2Bstr over-read unfixed upstream; no small-string optimisation.

## Caveats and trade-offs

First-party numbers from the author's project page, run on 2004-era compilers (gcc 3.3.3, VC++ 6.0, Intel C++ 6.0, WATCOM 11.0c) and CPUs (Athlon XP, Power 4), so they say little about current libstdc++, libc++ or glibc. Flags for the published runs are not stated. The page's benchmark links point to the dead SourceForge CVS viewer and the sources are not in the GitHub repo; cbench.c and cppbench.cpp (2006 versions) are in the SourceForge examples archive examples-09282006.zip (bstring/files/examples/ex10), which may differ from the code that produced the 2004-era numbers. The enormous C-API concatenation ratios come from cbench.c's testCSTR_concat, which calls strcat 500 times into one growing buffer (re-scanning the destination each call, quadratic) against Bstrlib's length-tracked bconcat, so they reflect the idiom, not general speed; the CBString vs std::string concatenation test uses the same += idiom on both sides, and its 21100%/19400% gaps on VC++ 6.0/Intel 6.0 reflect that era's Microsoft STL, as the author notes. On gcc (SUSE) the C API is slower than the C library for assignment (91%), scan (89%) and replace (86%), and on gcc Cygwin for assignment (89%); CBString is slower than STLport for character extraction (63% WATCOM) and assignment (93% WATCOM). Default construction is far slower than std::string per the page. Column for g++ SUSE ran on a different CPU (Power 4) than the other four (Athlon XP). Timing uses clock() over about 2 seconds per test, single run. bstrlib.txt also claims bsreadln can be 'several times faster' than fgets, with no numbers. Last commit 2016-11-02; the README calls the library stable and well tested but does not declare it complete. Repo also ships gpl.txt (dual BSD/GPL licensing). [retier] Enricher: harness defects in cbench.c (2006 SourceForge archive): the C-API scan row searches different strings on each side (strchr/strstr scan all of TESTSTRING1, which has no '.' and no "123", while bstrchr/binstr search "Dot. 123. Some more data." with hits at offsets 3 and 5), and the char\* concat buffer is 15500 bytes but the test writes 15501, a one-byte overrun, so the baseline is undefined behaviour. cppbench.cpp uses the same inputs on both sides. Gotchas: bstraux bNetStr2Bstr reads past the buffer on a crafted length (unfixed upstream, fixed in the msteinert fork); open issues #27 (bsplitstr wrong on multi-character delimiters), #21 (CBString::format crash), #5 (int lengths), #11 (no move semantics); CBString's default constructor mallocs 8 bytes, with no small-string optimisation.

Length-tracked bstring header plus separately malloced buffer: extra allocation and per-string overhead for small strings; buffer grows to powers of two (up to about 2x(n+1) bytes) and never shrinks. Not a drop-in for char\* or std::string (own API, bstring struct, CBString wrapper). Full bounds checking on CBString operator[] makes single-character extraction slower than unchecked STLs; CBString default constructor is non-trivial and slower than std::string's lazy one. Safety gain: avoids buffer overruns of the C string functions.

## Maintenance

Unmaintained upstream (last commit 2016-11-02, v1.0.0, 11 open issues and 6 open PRs) but BSD-3-Clause (with an optional GPL copy) and two source files, so easy to vendor; the actively maintained successor is msteinert/bstring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Author's own project page shows tables of Bstrlib vs C library string.h and CBString vs std::string with compilers and CPUs (Athlon XP 1.62 GHz, Power 4 1 GHz) named, but flags for those runs are not stated; benchmark sources (cbench.c, cppbench.cpp) exist only in a 2006 SourceForge examples archive that postdates the 2004-era runs. First-party with partial methodology, so C.
- **Verifier notes:** All claimed_speedup percentages match the features.html tables and column/CPU mapping (Athlon XP colspan 4, Power 4 for SUSE). maintenance_status corrected from finished to abandoned (last commit 2016-11-02, README says stable but not complete); BSD-3-Clause, 572 stars, not archived or a fork confirmed on github.com.
- **Fields the verifier corrected:** `maintenance_status`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-76 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://bstring.sourceforge.net/features.html>
  - <https://github.com/websnarf/bstrlib>
  - <https://github.com/websnarf/bstrlib/commits>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/README.md>
  - <https://sourceforge.net/projects/bstring/files/>
  - <https://sourceforge.net/projects/bstring/files/examples/>
  - <https://sourceforge.net/projects/bstring/files/examples/ex10/>
  - <https://sourceforge.net/projects/bstring/files/examples/ex10/examples-09282006.zip/download>
- **Sources the enricher read:**
  - <https://github.com/websnarf/bstrlib>
  - <https://github.com/websnarf/bstrlib/commits>
  - <https://github.com/websnarf/bstrlib/issues?q=is%3Aissue>
  - <https://github.com/websnarf/bstrlib/issues/27>
  - <https://github.com/websnarf/bstrlib/issues/21>
  - <https://github.com/websnarf/bstrlib/issues/7>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/README.md>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstrlib.h>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstrlib.c>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstrlib.txt>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/security.txt>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/porting.txt>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstrwrap.h>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstrwrap.cpp>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstraux.h>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bstraux.c>
  - <https://raw.githubusercontent.com/websnarf/bstrlib/HEAD/bsafe.c>
  - <https://bstring.sourceforge.net/features.html>
  - <https://sourceforge.net/projects/bstring/files/examples/ex10/examples-09282006.zip/download>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/websnarf/bstrlib`) · [data/wave1/enrich/raw/github_com_websnarf_bstrlib.json](../../../data/wave1/enrich/raw/github_com_websnarf_bstrlib.json) (enrichment confidence 0.8)

</details>
