# netbsd-curses

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Utilities](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause AND BSD-3-Clause` · 🟡 stale

> Portable Linux build of NetBSD's widechar curses; builds 6.6x faster and installs far smaller than ncurses, with no runtime benchmark.

| | |
|---|---|
| **Beats** | ncurses (wide-char build) |
| **Claimed result** | README Table 1: build time (make -j2) 59 sec for ncurses vs 9 sec for netbsd curses (6.6x, derived from page data); installed size 15.9 MB vs 1.3 MB; size of libncursesw.so 346 KB vs 150 KB; extracted source 15.8 MB vs 3.3 MB; static-linked nano 334 KB vs 288 KB. |
| **Workload** | Build and install of the library, programs, shared and static libs and headers (make -j2 all install) on a dual-core x86_64 sabotage Linux system with built-in terminfo and widechar support. |
| **Metric** | build-time |
| **Hardware** | dual-core x86_64 sabotage Linux system (CPU model not stated) |
| **Compiler and flags** | CFLAGS '-g0 -fdata-sections -ffunction-sections -Os -fno-unwind-tables -fno-asynchronous-unwind-tables -Wa,--noexecstack', LDFLAGS '-s -Wl,--gc-sections -Wl,-z,relro,-z,now' (README Appendix A); compiler not named |
| **Adoption** | 171 stars |
| **Last commit** | 2024-01-16 |
| **Links** | [repository](https://github.com/sabotage-linux/netbsd-curses) · [benchmark](https://github.com/sabotage-linux/netbsd-curses) |

## Verdict

One first-party run from the 2016-era README (Table 1, Appendix A): on an unnamed dual-core x86_64 sabotage Linux system with -Os size-optimised CFLAGS and unstated compiler and library versions, make -j2 all install took 59 s for ncurses and 9 s for netbsd curses (6.6x, derived from page data), libncursesw.so was 346 KB vs 150 KB and a static nano 334 KB vs 288 KB (1.16x); there is no benchmark script and no runtime (rendering or input) measurement.

## Use it when

- Source-based or embedded Linux distributions (especially musl) where ncurses is an early bootstrap dependency and its 59 s configure-heavy build and 15.9 MB install matter.
- Static or size-constrained builds of curses applications: a static nano linked against it was 288 KB versus 334 KB with ncurses in the README test.
- Cross-compiling curses apps: no configure script or ncurses5-config tool to fight, HOSTCC selects cross mode, and pkg-config files are provided.
- Projects that want a small, readable BSD-licensed curses codebase to patch or vendor.

## Skip it when

- When you expect faster terminal rendering: no runtime comparison against ncurses exists in the repo or in public sources found.
- Applications that need mouse input (ncurses mouse calls are no-op macros), more than 510 color pairs, or rarely used functions such as vidputs() and wgetscrreg() (issue #60).
- Programs or bindings that touch ncurses struct members or expect libncursesw's ABI, such as Python's curses module, which needs a patch.
- Unicode-heavy UIs until open issue #53 is resolved: a reporter found wide characters printed after initscr() rendering as question marks, with no maintainer reply.
- Projects needing an actively maintained library: last release v0.3.2 (2021-05-20), last commit 2024-01-16, and several open issues have no response.

## How it is fast

The win is build time and footprint, not screen-update speed. There is no autoconf configure step (settings are plain make variables or config.mak) and the whole tree is one non-recursive GNUmakefile that parallelises fully, with only a few small sh/awk generator steps, versus ncurses' configure script and its layers of awk/sed/cpp preprocessing; the source is about 3.3 MB against 15.8 MB. Terminfo is compiled into a CDB constant database with perfect-hash tables generated at build time by the bundled nbperf tool, and a dozen common terminals are compiled into the library.

## Compared with alternatives

The only catalogued sibling, micron.cpp, replaces memcpy/memset/memmove and does not overlap; pick netbsd-curses when the goal is a smaller, faster-to-build curses implementation for a distro or static binary.

## Integration

| | |
|---|---|
| **Form** | static lib and shared lib (both built by 'make all') |
| **Dependencies** | none at runtime beyond libc; build needs GNU make, a POSIX sh, awk and a C compiler (a host compiler too when cross-compiling); no configure script |
| **Minimum toolchain** | GNU make and a C compiler; C standard version not documented; builds against musl and glibc |
| **Platforms** | Linux (musl, glibc) on any architecture; README says other POSIX systems should work with minor changes |
| **Thread safety** | not documented (the README says nothing about threads); treat as single-threaded like classic curses |
| **Drop-in for the baseline** | partial — source-compatible for most ncursesw programs after linking -lcurses -lterminfo (static and shared libs are both built), but not ABI-compatible, mouse calls are no-ops, some functions are missing, and code that reads ncurses internals needs patches |

## Gotchas

- Footprint rows are not like for like: the 15.9 MB vs 1.3 MB installed size excludes netbsd curses' manpages and terminfo database but counts ncurses' (1.1 MB and 6.4 MB), and the shared-library row compares libncursesw.so with a library that is split into libcurses and libterminfo without saying whether libterminfo.so is counted; the current install target also installs manpages, so a rerun would not reproduce 1.3 MB.
- Terminfo is a CDB file, not the ncurses directory tree: only about a dozen terminals are built in, others need 'make terminfo/terminfo.cdb' installed to \$PREFIX/share/terminfo.cdb or \~/.terminfo.cdb, and newer terminals can be missing (issue #54 asks for foot; a GNU screen lookup fix landed only in January 2024).
- Functions such as tgetent() and tputs() live in libterminfo, so autoconf checks that only try -lcurses or -lncurses can fail until LIBS='-lcurses -lterminfo' is passed.
- Open display bugs without maintainer response: #53 (wide characters after initscr() shown as '?'), #59 (garbled display after running vis in st) and #28 (sl hangs in the Linux console).

## Known shortcomings

- Tier C, build-time and footprint only (no runtime benchmark): build 59 s vs 9 s and installed size vs ncurses, but the installed-size row is not like for like (netbsd-curses excludes 1.1 MB of manpages and 6.4 MB of terminfo, so about 8.4 MB vs 1.3 MB, derived); table circa 2016 with no versions, CPU model or script. Stale (last commit 2024-01-16).
- Enricher: build-time and size claim only, no runtime benchmark anywhere; the size rows are not like for like (installed size excludes manpages and the terminfo database; the .so row compares libncursesw.so with a split libcurses, libterminfo.so inclusion unstated) and the current install target installs manpages, so the 1.3 MB figure is not reproducible. Open bugs with no maintainer reply: #53 wide characters after initscr() show as '?', #59 garbled display (vis in st), #28 sl hangs, #60 wgetscrreg missing. Last release v0.3.2 (2021-05-20).

## Caveats and trade-offs

The claim is build time and footprint, not runtime curses performance; no runtime benchmark against ncurses was found. Single run, no repeats or variance, ncurses and netbsd-curses versions not stated, and the table dates from the 2016-era README (README history from March 2016; no later commit touches the table), so it reflects ncurses of about ten years ago. The configure-heavy ncurses build is single-threaded for part of its time (the README says netbsd curses should scale better with more jobs, which is untested). The installed-size row is not like for like: Appendix A says netbsd curses was installed without manpages (ncurses: 1.1 MB) and without the terminfo database (ncurses: 6.4 MB), so excluding those the gap is about 8.4 MB vs 1.3 MB (derived from page data), not 15.9 MB vs 1.3 MB. Binary sizes are from a size-optimised (-Os, gc-sections, stripped) build. Not a 100% drop-in replacement: mouse handling is no-op macros, some functions (vidputs) are missing, only 510 color pairs, and programs touching ncurses struct members need patches. First-party numbers, no benchmark script in the repo.

Close to a drop-in ncurses replacement with widechar support, but no mouse handling (no-op macros), only 510 color pairs, missing rarely used functions such as vidputs(), different struct layout (some programs such as Python's curses module need patches), curses and terminfo are split into libcurses and libterminfo, and terminfo is a CDB database.

## Maintenance

Stale: last release v0.3.2 on 2021-05-20 and last commit 2024-01-16, with open bug reports unanswered, but it is BSD-2/3-Clause, has no runtime dependencies and is small enough to vendor; it remains sabotage Linux's curses.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README Table 1 with flags stated in Appendix A, but no benchmark script, no compiler named, no CPU model (only 'dual core x86_64'), and no package versions, so C.
- **Verifier notes:** All Table 1 numbers match the README (59 s vs 9 s make -j2, 6.6x derived; 15.9 MB vs 1.3 MB installed; 346 KB vs 150 KB shared lib; 334 KB vs 288 KB static nano). Installed-size row excludes manpages and terminfo db for netbsd curses only. Metadata checked: 171 stars, 18 forks, BSD-2-Clause and BSD-3-Clause (COPYING), not archived or a fork, last commit 2024-01-16 (stale).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sabotage-linux/netbsd-curses/HEAD/README.md>
  - <https://raw.githubusercontent.com/sabotage-linux/netbsd-curses/HEAD/COPYING>
  - <https://github.com/sabotage-linux/netbsd-curses>
  - <https://github.com/sabotage-linux/netbsd-curses/commits/master>
  - <https://github.com/sabotage-linux/netbsd-curses/commits/master/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sabotage-linux/netbsd-curses/HEAD/README.md>
  - <https://raw.githubusercontent.com/sabotage-linux/netbsd-curses/HEAD/COPYING>
  - <https://raw.githubusercontent.com/sabotage-linux/netbsd-curses/HEAD/GNUmakefile>
  - <https://github.com/sabotage-linux/netbsd-curses>
  - <https://github.com/sabotage-linux/netbsd-curses/commits/master>
  - <https://github.com/sabotage-linux/netbsd-curses/tags>
  - <https://github.com/sabotage-linux/netbsd-curses/issues?q=is%3Aissue>
  - <https://github.com/sabotage-linux/netbsd-curses/issues/53>
  - <https://github.com/sabotage-linux/netbsd-curses/issues/57>
  - <https://github.com/sabotage-linux/netbsd-curses/issues/59>
  - WebSearch: netbsd-curses vs ncurses runtime performance refresh benchmark (no runtime benchmark found; snippet from an Alpine devel list post on ncurses vs netbsd-curses sizes)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/sabotage-linux/netbsd-curses`) · [data/wave1/enrich/raw/github_com_sabotage_linux_netbsd_curses.json](../../../data/wave1/enrich/raw/github_com_sabotage_linux_netbsd_curses.json) (enrichment confidence 0.75)

</details>
