# Ninja

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Build systems](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Minimal C++ build executor fed by generated build.ninja files; much faster no-op and incremental builds than CMake-generated Makefiles.

| | |
|---|---|
| **Beats** | GNU Make (CMake Unix Makefiles generator backend) |
| **Claimed result** | Page text: switching the CMake backend from Make to Ninja shaves 3.5 seconds (over 20%) off the total build time of the 1000-file project with no CMake file changes. Chart values (bar-chart PNGs, read off approximately): full build CMake/Make about 16 s vs CMake/Ninja about 12.5 s; empty (no-op) build CMake/Make about 0.55 s vs CMake/Ninja about 0.04 s (about 13x, derived from page data). Page text also says Meson (Ninja backend) takes 0.03 s for the empty build and Autotools, the fastest Make-based system, is almost an order of magnitude slower. Anecdote on the same page: no-op build times of 30 seconds for Make versus less than one second for Ninja when compiling the Clang compiler. |
| **Workload** | Meson author's experiment: 1000 generated trivial C files (each defining one function and including a header) built into one executable with CMake, once with its Make backend and once with its Ninja backend, four parallel processes, fastest of several runs; plus an anecdote about no-op builds of the Clang compiler. |
| **Metric** | build-time |
| **Hardware** | 2011-era MacBook Pro running Ubuntu 13.04 (CPU model not stated) |
| **Compiler and flags** | Linked measure.py: cmake -DCMAKE_BUILD_TYPE=debug (default Unix Makefiles generator) then make -j 4, versus cmake -DCMAKE_BUILD_TYPE=debug -G Ninja then ninja -j 4; system C compiler picked by CMake (the Meson row sets CC=gcc); compiler, CMake, Make and Ninja versions are not stated. |
| **Adoption** | 13.3k stars |
| **Last commit** | 2026-10-18 |
| **Links** | [repository](https://github.com/ninja-build/ninja) · [benchmark](https://github.com/mesonbuild/meson/blob/master/docs/markdown/Simple-comparison.md) |

## Verdict

The Meson author's 1,000-trivial-C-file experiment (CMake debug build, -j 4, 2011-era MacBook Pro on Ubuntu 13.04, compiler and tool versions unstated, fastest of several manual runs) shows CMake's Ninja backend about 3.5 s (over 20%) faster than its Unix Makefiles backend on a full build (about 12.5 s vs 16 s, read off a chart) and about 13x faster on an empty rebuild (about 0.04 s vs 0.55 s). The same page anecdotally reports Clang no-op builds of 30 s with Make versus under 1 s with Ninja.

## Use it when

- Any CMake or Meson C/C++ project where edit-compile-run latency matters: switching the generator to Ninja cuts no-op builds from about 0.55 s to about 0.04 s on 1,000 files in the Meson experiment, and the gap grows with tree size.
- Large trees (tens of thousands of sources, such as Chromium, or the Clang compiler) where build-system startup dominates a one-file rebuild: the manual cites under 1 s versus 10 s for Chromium's custom Makefiles.
- Generated build graphs from your own tooling: the format is small, documented and easy to emit from any language.
- Windows builds with MSVC, using deps = msvc to capture /showIncludes header dependencies.

## Skip it when

- Hand-maintained build logic: build.ninja has no conditionals or built-in rules, so without a generator you would be writing every command yourself.
- When your Makefiles are already lean: in a separate third-party synthetic benchmark (thutt/build-tool-comparator), GNU Make 4.3 with --no-builtin-rules --no-builtin-variables matched Ninja 1.11.1 on incremental and null builds and beat it on full builds from 50,000 modules (100,000 modules on x86_64: full 103.8 s vs 407.1 s), so the large wins are over default-rules or CMake-generated Makefiles.
- Clean full builds of real code: they are compiler-bound, and the Meson charts put Make-based Premake (about 12.7 s) level with CMake's Ninja backend (about 12.5 s).
- Memory-tight machines with heavy link or LTO steps: default parallelism is processor count plus 2 with no memory limit (open issue #2187 reports OOM kills building LLVM and KiCad), so cap it with -j, -l or a pool.
- Builds that need content-hash rebuild decisions, remote caching or sandboxing: Ninja uses mtimes and command hashes only (content-based checking is an open request, #1459).

## How it is fast

It avoids decision-making at build time: there is no implicit or suffix rule search (Make's built-in rules even look for RCS files), and the whole dependency graph is loaded once in a single process. The manifest lexer is generated with re2c, command lines are stored as rapidhash hashes in .ninja_log so flag changes trigger rebuilds cheaply, and compiler header dependencies (deps = gcc or msvc) are folded into a compact binary .ninja_deps database instead of thousands of .d files parsed at startup. On Windows it caches directory listings to cut stat calls.

## Compared with alternatives

Pick Ninja as the default local backend for CMake or Meson C++ projects; choose Bazel or Buck2 only when you need hermetic builds with remote caching (in the build-tool-comparator tables Ninja beat Bazel in every incremental and null row), tup when you need near-instant no-op checks on very large trees, and add ccache on top of Ninja rather than instead of it.

## Integration

| | |
|---|---|
| **Form** | standalone executable (single binary, no install step needed) |
| **Dependencies** | none at runtime; building from source needs Python (configure.py --bootstrap) or CMake 3.15+, with re2c optional to regenerate the lexers |
| **Minimum toolchain** | C++17 compiler to build Ninja itself |
| **Platforms** | Linux, macOS and Windows release binaries; configure.py also supports FreeBSD, OpenBSD, NetBSD, Solaris, AIX and MinGW |
| **Thread safety** | One process whose scheduler spawns parallel subprocesses; running two ninja processes on one build directory at once is not documented |
| **Drop-in for the baseline** | partial: for CMake or Meson projects it is a generator switch (-G Ninja) with no build-file changes; hand-written Makefiles must be rewritten or generated |

## Gotchas

- Builds always run in parallel (default processors + 2), so under-specified dependencies that happened to work with serial make produce wrong or flaky builds.
- Header dependencies only work if the rule sets depfile or deps = gcc/msvc; depfiles that mix absolute and relative paths fail to match other rules' paths, so the manual recommends relative include paths.
- Command output is buffered per job; tasks that need the terminal (tests with progress output) must use the console pool, which runs one at a time.
- Jobserver client support exists only since 1.13 and only for GNU Make 4.4+ FIFO jobservers; an older pipe-based jobserver is ignored with a warning and Ninja then uses its own job count.

## Known shortcomings

- Figures read off bar charts (Make about 16 s vs Ninja 12.5 s full build; 0.55 s vs 0.04 s empty build); CMake Debug build at -j 4, tool versions not stated. Meson uses Ninja as its backend rather than competing with it.
- Enricher: fastest-of-several runs taken by hand (measure.py does one pass, never cleans); most of the 20% full-build gain is CMake Makefile-generator overhead; Make -rR ties Ninja on incremental and null builds and beats it on full builds from 50k modules in build-tool-comparator.

## Caveats and trade-offs

The only quantified third-party comparison reachable is written by the author of Meson, a meta-build system that itself generates Ninja files (an interested party for Ninja, competing with CMake rather than with Ninja), and is old (2011-era MacBook Pro, Ubuntu 13.04). CPU model, compiler and tool versions are not stated. The generator and measurement scripts are linked from the page (raw.githubusercontent.com/wiki/jpakkane/meson/gen_src.py and measure.py); measure.py times a single build and a single empty build per tool, while the page says the fastest of several runs was taken. The per-tool values are in bar-chart PNGs, so the figures other than the 3.5 s / over 20% text are read off the charts and approximate. The baseline is CMake-generated Makefiles, not a hand-written Makefile, so the gap partly reflects CMake's Makefile generator. The 30 s versus under 1 s Clang figure is explicitly anecdotal. First-party claim on the Ninja manual page (https://github.com/ninja-build/ninja/blob/master/doc/manual.asciidoc, introduction): Chromium, with over 30,000 source files, had other build systems, including one built from custom non-recursive Makefiles, that took ten seconds to start building after changing one file, while Ninja takes under a second; no hardware, date or method is given there, so it is tier C on its own. Ninja's advantage is mostly incremental and no-op startup time; clean full builds are compiler-bound, and the 20 percent gain is on a synthetic project of trivial files, so real projects will see less on clean builds. [retier] Enricher: measure.py does one pass and never cleans the build directories, so the fastest-of-several-runs figures were taken by hand; on the full-build chart Premake's Make backend (about 12.7 s) nearly matches CMake/Ninja (about 12.5 s), so most of the 20% gain over CMake's Makefile generator is generator overhead. In thutt/build-tool-comparator, Make with -rR ties Ninja 1.11.1 on incremental and null builds and beats it on full builds from 50k modules (x86 100k: 103.8 s vs 407.1 s).

Deliberately has no build-file features (no conditionals, no built-in rules, no globbing); build.ninja files are meant to be emitted by a generator such as CMake or Meson, so Ninja alone is not a replacement for a hand-written Makefile. It needs a generator step. Uses all hardware threads by default; the manual says the design trades convenience for speed.

## Maintenance

Actively maintained (v1.13.2 is the latest release, master already documents 1.14 features, 13.3k stars), Apache-2.0, and shipped as one dependency-free binary, so adoption cost is low for CMake and Meson users.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now B.
- **Tier reason:** Measurement by the Meson author (not a Ninja author) in mesonbuild/meson docs/markdown/Simple-comparison.md, comparing CMake's Make backend with its Ninja backend; generator and measurement scripts are public (linked gen_src.py, measure.py) and the build type and -j 4 are stated, but compiler version and CPU model are not, so not A.
- **Verifier notes:** Page text figures confirmed; the record wrongly said the generator script is absent and that the charts were unreadable (both PNGs fetched and read). Meson is not a competitor of Ninja (it uses Ninja as its backend), so caveats reworded. Tier B kept as independent-of-Ninja measurement with public scripts; it is old and modest evidence.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-09 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/mesonbuild/meson/blob/master/docs/markdown/Simple-comparison.md>
  - <https://raw.githubusercontent.com/mesonbuild/meson/HEAD/docs/markdown/Simple-comparison.md>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/buildtime.png>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/emptytime.png>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/gen_src.py>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/measure.py>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/doc/manual.asciidoc>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/COPYING>
  - <https://github.com/ninja-build/ninja>
  - <https://github.com/ninja-build/ninja/commits>
- **Sources the enricher read:**
  - <https://github.com/ninja-build/ninja>
  - <https://github.com/ninja-build/ninja/releases>
  - <https://github.com/ninja-build/ninja/issues?q=is%3Aissue%20state%3Aopen%20performance>
  - <https://github.com/ninja-build/ninja/issues/2187>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/README.md>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/doc/manual.asciidoc>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/src/build_log.cc>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/src/deps_log.cc>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/src/disk_interface.cc>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/src/lexer.in.cc>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/src/ninja.cc>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ninja-build/ninja/HEAD/configure.py>
  - <https://raw.githubusercontent.com/mesonbuild/meson/HEAD/docs/markdown/Simple-comparison.md>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/measure.py>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/gen_src.py>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/buildtime.png>
  - <https://raw.githubusercontent.com/wiki/jpakkane/meson/emptytime.png>
  - <https://raw.githubusercontent.com/thutt/build-tool-comparator/HEAD/README.md>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/ninja-build/ninja`) · [data/wave2/enrich/raw/github_com_ninja_build_ninja.json](../../../data/wave2/enrich/raw/github_com_ninja_build_ninja.json) (enrichment confidence 0.75)

</details>
