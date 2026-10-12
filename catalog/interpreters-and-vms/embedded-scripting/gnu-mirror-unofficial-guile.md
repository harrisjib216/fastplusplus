# GNU Guile

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `LGPL-3.0-or-later` · 🟢 active

> GNU's embeddable Scheme with a JIT; about 2x faster than PUC Lua 5.4.7 on a naive fib(47) shootout.

| | |
|---|---|
| **Beats** | Lua 5.4.7 (PUC-Rio). The same table also lists LuaJIT 2.1.1, Janet 1.36.0 and Tcl 9.0.0. |
| **Claimed result** | 102.887 s for Guile 3.0.10 versus 203.702 s for Lua 5.4.7, about 2.0x faster (derived from page data). LuaJIT at 37.837 s is faster than both; Janet (479.663 s) and Tcl (2230.883 s) are slower. |
| **Workload** | Naive recursive fibonacci fib(47) = 2,971,215,073, run as 'guile fib.scm' and 'lua fib.lua' and timed with bash 'time' (whole process, start-up included); run.sh runs :interpreted entries once despite the README's 'average of 5 runs' (unchanged since 2021-04-17); last run 2024-12-05. |
| **Metric** | throughput |
| **Hardware** | Hetzner CCX23, 4 vCPU, 'Intel Xeon 3.1Ghz' (exact model not stated), 16 GiB RAM, Ubuntu 24.04 |
| **Compiler and flags** | Guile installed from the apt package guile-3.0 and Lua 5.4.7 through asdf in an amd64/ubuntu:24.04 Docker image (versions table: guile 3.0.10, lua 5.4.7); the README states only common release flags for compiled languages and gives none for the interpreters |
| **Adoption** | Mirror has 0 stars; the benchmark repo drujensen/fib has 906 stars. Guile is the GNU project extension language. |
| **Last commit** | 2022-04-08 |
| **Links** | [repository](https://github.com/gnu-mirror-unofficial/guile) · [benchmark](https://github.com/drujensen/fib) |

## Verdict

One naive recursive fib(47) run per interpreter in drujensen/fib (whole-process bash time, 2024-12-05, ubuntu:24.04 container on a Hetzner CCX23 with 4 vCPU 'Intel Xeon 3.1Ghz'): Guile 3.0.10 from the Ubuntu package 102.887 s versus Lua 5.4.7 built by asdf 203.702 s, about 2.0x (derived from page data); LuaJIT 2.1.1 37.837 s.

## Use it when

- C or C++ applications on Linux or the BSDs that want a full Scheme (modules, hygienic macros, continuations, threads, FFI via (system foreign)) as their extension language, and can live with LGPL linking.
- Call-heavy, integer-heavy script code where a JIT pays off: drujensen/fib puts guile at 102.9 s vs lua at 203.7 s for naive fib(47).
- Projects choosing among Scheme engines: on ecraven/r7rs-benchmarks all.csv, Guile 3.0.11 is about 14x faster than Chibi-Scheme 0.11.0 (geomean over 44 shared benchmarks) and about 2.3x faster than s7 11.3 (51 shared), derived from page data.
- GNU-ecosystem tools (Guix-style workflows, GNU programs with Guile hooks) where Guile is already installed as a distro package (guile-3.0).

## Skip it when

- You need the fastest small dynamic language: LuaJIT 2.1.1 runs the same fib(47) in 37.8 s, 2.7x faster than Guile; Chez Scheme is about 2.6x faster than Guile 3.0.11 across r7rs-benchmarks (derived from page data).
- Tiny footprint or easy vendoring: libguile needs libgmp, libiconv, libintl, libltdl, libunistring, libgc (Boehm-Demers-Weiser, at least 7.2) and libffi, against Lua's single directory of ANSI C.
- Closed-source static linking: LGPL-3.0-or-later obliges you to allow relinking.
- Your scripts and bindings are already Lua: there is no compatibility layer, so the swap is a rewrite.
- Short-lived processes where start-up and first-run auto-compilation matter; the shootout times whole processes but says nothing about start-up cost separately.

## How it is fast

Source is compiled ahead of running to Guile 3's low-level bytecode (auto-compiled into \$XDG_CACHE_HOME/guile/ccache on first load), and hot code is then translated to native code by a JIT built on the lightening library, enabled by default on x86-64, i686, ARMv7 and AArch64; NEWS credits the JIT with up to 4x over Guile 2.2. The lower-level instruction set lets the compiler elide type checks and unbox integers, and 3.0.8 added cross-module inlining. PUC Lua, the baseline, is a pure bytecode interpreter, so the fib gap is largely JIT versus interpreter.

## Compared with alternatives

Pick Guile over Chibi-Scheme or s7 when you want a Scheme and speed matters more than size: on r7rs-benchmarks it is about 14x faster than Chibi and 2.3x faster than s7 (derived from page data), while Chibi and s7 are far smaller to embed. Pick LuaJIT or Luau instead when the language is open and you want the fastest small embeddable runtime.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libgmp, libiconv, libintl, libltdl, libunistring, libgc (bdw-gc 7.2+), libffi, pkg-config at build time; libreadline optional |
| **Minimum toolchain** | GNU autotools build (./configure); minimum compiler version not documented in the README read; prebuilt as the guile-3.0 package on Debian/Ubuntu |
| **Platforms** | JIT on x86-64, i686, ARMv7 and AArch64 (NEWS for 3.0.0), RISC-V added in 3.0.11 (search snippet); builds on GNU/Linux, FreeBSD (README notes), macOS and 64-bit Cygwin per NEWS; interpreter-only elsewhere |
| **Thread safety** | Threaded by default on a threaded libgc build (README shows --without-threads for single-threaded builds); host threads enter Scheme through scm_with_guile and leave with scm_without_guile |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: drujensen/fib's run.sh runs every :interpreted entry, Guile and Lua included, only once ('Running #{lang.name} 1 time', unchanged since the 2021-04-17 commit 'add compile times. average 5 runs'), although the README says all languages run 5 times; the 102.887 s and 203.702 s figures are single runs, not averages. With runs of 100 to 200 s the noise is small against a 2x gap, but nothing was repeated.
- The shootout files Guile under 'Interpreted, dynamically typed', but Guile 3 JIT-compiles by default on x86-64, so this is a JIT against the PUC interpreter, not interpreter against interpreter; the single timed run also includes the first-load auto-compilation of fib.scm (small for a five-line file).
- libgc is a conservative collector: C stacks and heap words that look like pointers keep objects alive, which eases embedding but can retain memory.
- The catalogued URL is a stale unofficial GitHub mirror (NEWS stops at 3.0.9, last commit 2022-04-08); the benchmark used Ubuntu's Guile 3.0.10 and 3.0.11 shipped on 2025-12-01 (search snippet; gnu.org, lists.gnu.org and codeberg.org are blocked here), so take sources from the official release tarballs, not this mirror.

## Known shortcomings

- Single fib(47) micro-benchmark from drujensen/fib (102.887 s vs Lua 5.4.7 at 203.702 s), Guile's JIT against the pure-interpreter Lua; the repo URL is a stale unofficial mirror (last commit 2022-04-08) while upstream lives at codeberg.org/guile/guile (3.0.11, December 2025, blocked here).
- Enricher: drujensen/fib's run.sh runs the :interpreted entries only once (unchanged since 2021-04-17) although the README says 5 runs, so the Guile 102.887 s and Lua 203.702 s are single runs; Guile's JIT is on by default, so the test is JIT against the PUC interpreter; the mirror's NEWS stops at 3.0.9.

## Caveats and trade-offs

Single naive-recursion micro-benchmark, so it says little about general scripting workloads; last run 2024-12-05. Guile 3 has a JIT (NEWS: 'Just-in-time code generation') and auto-compiles the script to bytecode, while PUC Lua is a pure interpreter; the page files Guile under 'Interpreted'. LuaJIT 2.1.1 (37.837 s) is far faster than both. Whole-process wall time with bash 'time'. The repo URL is a stale unofficial GitHub mirror (0 stars, last commit 2022-04-08); upstream moved to codeberg.org/guile/guile.git and released Guile 3.0.11 in December 2025 (search snippet only, codeberg and gnu.org not reachable here), so the project is active but its last commit date could not be checked. Benchmark code and Dockerfile are public but the CPU model is only 'Intel Xeon 3.1Ghz'. [retier] Single fib(47) micro-benchmark, a single run per entry (not 5), Guile's JIT (on by default) against the pure-interpreter Lua 5.4.7; LuaJIT (37.837 s) is faster than both. The repo URL is a stale unofficial mirror (last commit 2022-04-08, NEWS stops at 3.0.9) while upstream lives at codeberg.org/guile/guile (3.0.11, December 2025, blocked here).

Scheme, not Lua-like; garbage-collected library meant for embedding with a C API; LGPL linking terms; larger runtime and longer start-up than Lua.

## Maintenance

Guile itself is maintained (3.0.11 released 2025-12-01 per search snippet) and LGPL-3.0-or-later, but the catalogued GitHub mirror stopped in 2022, so build from GNU release tarballs or distro packages.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (drujensen/fib, 906 stars) with public code (fib.scm, fib.lua, run.sh, Dockerfile) lists 'guile fib.scm' at 102.887 s against 'lua fib.lua' at 203.702 s. Interpreter build flags are not stated and the CPU is only 'Intel Xeon 3.1Ghz', so not A.
- **Verifier notes:** Numbers verified on drujensen/fib README; licence LGPL-3.0-or-later confirmed from the mirror's LICENSE file. Main shortcoming: one fib micro-benchmark and a stale mirror URL (canonical repo codeberg.org/guile/guile per search snippet); maintenance_status set to active from the 3.0.11 release in December 2025 (snippet only), last_commit left as the mirror's date.
- **Fields the verifier corrected:** `maintenance_status`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/drujensen/fib>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/README.md>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/fib.scm>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/fib.lua>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/run.sh>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/Dockerfile>
  - <https://github.com/gnu-mirror-unofficial/guile>
  - <https://github.com/gnu-mirror-unofficial/guile/commits>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/NEWS>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/README.md>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/fib.scm>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/fib.lua>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/run.sh>
  - <https://raw.githubusercontent.com/drujensen/fib/HEAD/Dockerfile>
  - <https://github.com/drujensen/fib/commits/main/run.sh>
  - <https://github.com/drujensen/fib/blame/main/run.sh>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/README>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/libguile/init.h>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/libguile/threads.h>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/libguile/gsubr.h>
  - <https://raw.githubusercontent.com/gnu-mirror-unofficial/guile/HEAD/libguile/eval.h>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/all.csv>
  - <https://raw.githubusercontent.com/ecraven/r7rs-benchmarks/master/README.org>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/master/README.md>
  - https://www.gnu.org/software/guile/news/gnu-guile-3011-released.html (EGRESS_BLOCKED; search snippet only)
  - https://lists.gnu.org/archive/html/info-gnu/2025-12/msg00002.html (EGRESS_BLOCKED; search snippet only)
  - https://codeberg.org/guile/guile (blocked)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/gnu-mirror-unofficial/guile`) · [data/wave12/enrich/raw/github_com_gnu_mirror_unofficial_guile.json](../../../data/wave12/enrich/raw/github_com_gnu_mirror_unofficial_guile.json) (enrichment confidence 0.65)

</details>
