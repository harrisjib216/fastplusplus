# Vectorscan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Portable BSD fork of Intel Hyperscan multi-regex matcher for ARM, Power and x86; 1.4-3.6x faster Snort 3 on ARM routers.

| | |
|---|---|
| **Beats** | Snort 3 built without Vectorscan (the OpenWrt snort3 package sets -DENABLE_HYPERSCAN only when the vectorscan package is selected, so Snort falls back to its built-in non-Hyperscan fast-pattern search methods and PCRE; the commit message does not name the search_method used) |
| **Claimed result** | Snort 3.1.84.0 download throughput through the router, with vs without Vectorscan 5.4.11, n=3: GL.iNet GL-MT6000 (flogic, kernel 6.6.26) IDS mode 331.0 +/-27.34 vs 91.2 +/-0.21 Mbit/s (3.6x), IPS mode 52.9 +/-0.78 vs 30.0 +/-0.06 Mbit/s (1.8x); Raspberry Pi 5B (bcm2712, kernel 6.1.86) IPS mode 232.8 +/-0.26 vs 164.3 +/-0.64 Mbit/s (1.4x). The commit notes single-core CPU saturation in all runs. Snippet only, not opened: Arm's blog reports a 20-40% uplift over Snort's default regex implementations on a Neoverse N1 (Ampere Altra); Wordfence's CLI 4.0.1 post reports 6x to 30x faster malware scans with Vectorscan or Hyperscan instead of PCRE. |
| **Workload** | End-to-end network throughput of Snort 3.1.84.0 running on OpenWrt routers with a roughly 22 MB community ruleset, measured with and without the Vectorscan 5.4.11 package (download speed through the router in IDS and IPS mode, n=3). |
| **Metric** | throughput |
| **Hardware** | GL.iNet GL-MT6000 router SoC (flogic/glinet_gl-mt6000, kernel 6.6.26) and Raspberry Pi 5B (bcm2712, kernel 6.1.86); exact CPU model strings not given |
| **Adoption** | 766 stars, 93 forks; packaged in OpenWrt (with Snort 3) and in Debian-family and other distributions as libvectorscan |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/VectorCamp/vectorscan) · [benchmark](https://github.com/openwrt/packages/commit/d62471c093bfec5c5203ade9e5175a8ef7ae80b1) |

## Verdict

An OpenWrt packager's commit measured download throughput through routers running Snort 3.1.84.0 with a roughly 22 MB community ruleset, built with and without the Vectorscan 5.4.11 package (n=3, one core saturated): GL.iNet GL-MT6000 IDS 91.2 to 331.0 Mbit/s (3.6x) and IPS 30.0 to 52.9 Mbit/s (1.8x), Raspberry Pi 5 IPS 164.3 to 232.8 Mbit/s (1.4x). It is a whole-application number against an unnamed fallback matcher, with the OpenWrt toolchain's unstated compiler and flags, and it mostly reflects the Hyperscan design Vectorscan inherits.

## Use it when

- IDS/IPS, DPI, log or malware scanning where hundreds to tens of thousands of signatures must be matched in one pass, including matching across packet or chunk boundaries in streaming mode.
- aarch64 servers and boards (Graviton, Ampere Altra, Apple Silicon, Raspberry Pi 5, router SoCs) or ppc64le, where Intel Hyperscan does not build; Snort 3 on OpenWrt and Arm's Snort learning path both use it there.
- You need a maintained BSD-3-Clause Hyperscan: the open Intel line stopped at 5.4 and 5.5+ ships under Intel's proprietary licence, while Vectorscan 5.4.13 (August 2026) is packaged by Debian/Ubuntu (libvectorscan-dev), Fedora, Arch AUR and OpenWrt.
- x86 deployments that already use Hyperscan 5.4 and want current compiler fixes (clang 21, GCC 15/16) and bug fixes without an API change; a fat runtime picks SSE4.2, AVX2, AVX-512 or AVX-512VBMI code at load time.

## Skip it when

- You need capture groups, back-references, lookaround or PCRE/RE2 leftmost-first semantics: those constructs fail to compile (prefilter mode only approximates them as a superset that another engine must confirm), and start offsets need HS_FLAG_SOM_LEFTMOST, which rebar's notes say slows scanning and limits pattern size.
- One pattern, patterns that change per request, or tiny inputs: the database must be compiled up front and large or complex patterns can hit 'Pattern too large' or 'Unable to generate bytecode' errors.
- Windows/MSVC, RISC-V or LoongArch targets: the 5.4.12 platform list is Linux (x86, Arm, Power), FreeBSD 14 and macOS 14+; 5.4.13 dropped macOS x86 and FreeBSD from CI, excludes new architectures without a support contract, and an MSYS2 UCRT64 port still fails two rebar-derived match-count tests (issue #417, 4 matches short).
- Logical-combination patterns whose operands use singlematch or max_offset: they return incomplete results (open issue #357, inherited from Hyperscan #430).

## How it is fast

It keeps Hyperscan's hybrid-automata design: the Rose engine splits patterns into literal factors found by SIMD literal matchers (FDR, Teddy, noodle), then confirms them with bit-parallel LimEx NFAs, McClellan and shuffle-based Sheng/McSheng DFAs, and repeat engines (LBR, Castle), and skips input with SIMD acceleration scanners (shufti, truffle, vermicelli). Vectorscan's own work is the SIMD layer: since 5.4.6 the engines use a SuperVector C++ template library with NEON/ASIMD, SVE/SVE2, VSX and SIMDe backends, plus Arm-specific tweaks such as the shrn-based movemask (5.4.8) and 256-bit TBL truffle (5.4.12).

## Compared with alternatives

Pick it over Hyperscan whenever you are on ARM or Power, or want a maintained open-source build; on x86 the two share algorithms and API. Pick it over RE2, rejit, BLARE or regexr when many patterns must be matched in one pass or across streamed chunks and you do not need captures or leftmost-first semantics.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libhs via CMake; distro packages libvectorscan5 / libvectorscan-dev) |
| **Dependencies** | Build only: CMake 3.18.4+, Ragel, Boost headers (1.57+, 1.61+ in some configurations), pkg-config; optional PCRE 8.41+ for the Chimera library, SQLite and libpcap for tools and benchmarks. Runtime: none beyond libc (C API). |
| **Minimum toolchain** | C17 and C++17 (cflags-generic.cmake sets -std=c17 / -std=c++17); GCC or Clang, with fixes for clang 21 and GCC 15/16 in 5.4.13 |
| **Platforms** | Linux x86-64 (SSE4.2 minimum; AVX2/AVX-512/AVX-512VBMI paths, fat runtime on by default), aarch64 NEON/ASIMD plus SVE/SVE2 (fat runtime on Linux), ppc64le VSX, macOS 14+ arm64; SIMDe backend for other CPUs; Windows not officially supported |
| **Thread safety** | Compiled databases are read-only and can be shared; every concurrent caller needs its own hs_scratch_t (hs_alloc_scratch, or hs_clone_scratch per thread), per hs_runtime.h. |
| **Drop-in for the baseline** | partial — ABI/API replacement for Intel Hyperscan 5.4 (Snort 3 picks it up via -DENABLE_HYPERSCAN and search_method 'hyperscan'), but not a drop-in for Snort's Aho-Corasick search methods' semantics, PCRE or std::regex |

## Gotchas

- The measured 5.4.11 predates a run of ARM and SIMD correctness fixes released in 5.4.13: arm64 HS_FLAG_DOTALL false negatives (#382, tests in #391), SVE shufti/truffle/noodle bugs (#377), a NEON rshift fallback bug (#396), double-shufti missing matches across stream chunk boundaries (#402) and a stack buffer overflow in rvermicelliDoubleExecReal (#392); use 5.4.13 or later.
- Match semantics differ from backtracking engines: every match end is reported, including overlapping ones ([a-z]+ on 'abc' reports three matches per rebar's Hyperscan notes), so counts differ from PCRE unless HS_FLAG_SINGLEMATCH or SOM flags are used.
- Compiling in UTF-8 mode and scanning invalid UTF-8 is undefined behaviour (rebar's Hyperscan runner refuses such haystacks); validate input first.
- In Snort 3 the gain depends on the configured fast-pattern search method: Arm's learning path sets search_engine.search_method='hyperscan' explicitly, OpenWrt's snort.uc sets no method, and the OpenWrt commit does not say which matcher ran in either column.

## Known shortcomings

- Only numbers are OpenWrt commit d62471c (Snort 3.1.84.0 with vs without Vectorscan 5.4.11: 3.6x IDS and 1.8x IPS on GL-MT6000, 1.4x IPS on RPi5B): whole-Snort throughput against an unnamed fallback matcher, no code, flags or CPU details, n=3. The Arm blog (20-40%) and Wordfence (6-30x) figures are snippets only. Arm64 correctness fixes (#382 DOTALL false negatives, #377, #392, #396) came after 5.4.11. Kept as a separate entry from intel/hyperscan (rewritten NEON/SVE/VSX SIMD layer, own ARM evidence, maintained BSD line after Hyperscan 5.5 went closed), but the gain is mostly inherited Hyperscan design.
- Enricher: OpenWrt's snort.uc sets no search_method, so it is unclear which matcher ran in either column of the only measurement; 5.4.11 predates the 5.4.13 ARM/SIMD correctness fixes (#382 DOTALL, #377, #396, #402, #392); open bugs #357 (combo-pattern results incomplete) and #417 (MSYS2 UCRT64 build matches short on two rebar-derived tests); the Arm learning path snort.md has no baseline.

## Caveats and trade-offs

The only numeric comparison reachable is a packager's commit message in the OpenWrt packages repository (third party, not the project's own repo). It measures Snort 3 as a whole through a router with a speedtest script against a roughly 22 MB community ruleset, not the regex engine in isolation, and the baseline is 'Snort without Vectorscan' with the fallback matcher unnamed, so the speedups are whole-application gains and mostly reflect the Hyperscan design that Vectorscan inherits rather than Vectorscan-specific work. Compiler, flags and exact CPU models are not stated, no benchmark code is public, n=3 per cell. The README links a wiki 'Vectorscan Benchmarks' page that does not exist (the wiki index lists only Home and two installation pages). benchmarks/benchmarks.cpp is an internal microbenchmark of its own primitives (shufti, truffle, noodle and so on) with no baseline. The Arm Neoverse blog (20-40% Snort uplift on Ampere Altra) and Wordfence CLI post (6x-30x vs PCRE, Vectorscan or Hyperscan) were blocked by the egress policy and are snippet only; Arm co-develops Vectorscan, so its figure is first-party. Later correctness fixes postdate the measured 5.4.11: an arm64 HS_FLAG_DOTALL false-negative bug (issue #382, reported on 5.4.12, regression tests in #391), SVE accelerator bugs in shufti/truffle/noodle (#377), a NEON rshift fallback bug (#396) and a stack buffer overflow in rvermicelliDoubleExecReal (#392) were fixed for 5.4.13; whether 5.4.11 on these ARM boards was affected is not established. The patch's author date reads May 2023 while the message cites Snort 3.1.84.0 and Vectorscan 5.4.11, so the numbers were evidently added when the long-running PR was revised. No comparison against std::regex, RE2, PCRE2 or Hyperscan itself was found.

Multi-pattern (set) matching library with a libpcre-like syntax subset: no backreferences or arbitrary lookaround, and it reports match end offsets, so it is not a drop-in replacement for a backtracking engine such as std::regex or PCRE. It exists mainly to bring Hyperscan to non-x86 CPUs (ARM NEON/ASIMD, ARM SVE2, Power VSX, plus a SIMDe backend); on x86 it keeps the upstream Hyperscan code paths. Large compiled databases and long compile times are the usual cost of the hybrid-automata approach. Fork of Intel Hyperscan; per the project README, Hyperscan versions after 5.4 are going closed-source, so Vectorscan is the open-source line (the README says its ARM port was rejected upstream).

## Maintenance

Actively maintained (5.4.13 released 2026-08-21 after a funding gap the changelog says is solved, last commit 2026-09-04), BSD-3-Clause and packaged by major distributions, so link the distro library rather than vendoring the Ragel/Boost build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers reachable are an OpenWrt packager's commit message (Snort 3.1.84.0 through a router with and without Vectorscan 5.4.11, n=3 per cell, speedtest download rate): third-party but with no benchmark code, compiler, flags or CPU model, and no well-known suite or paper, so C. The Arm blog claim of a 20-40% Snort uplift on Ampere Altra (snippet only) comes from a co-developer of Vectorscan and is also C.
- **Verifier notes:** Numbers in the record match the OpenWrt commit (d62471c, libs/vectorscan/Makefile, PKG_VERSION 5.4.11); tier C stands; metadata verified on github.com (BSD-3-Clause, 766 stars, GitHub-marked fork of intel/hyperscan, default branch develop, last commit 2026-09-04, release 5.4.13 on 2026-08-21). Fork judgement: keep as a separate entry, not a duplicate of the listed Hyperscan, because it changes performance-relevant code (SIMD layer rewritten as SuperVector templates with NEON/ASIMD, SVE/SVE2 and VSX backends), its own evidence is on ARM boards where Hyperscan cannot run, and it is the maintained BSD line now that Hyperscan 5.5+ is closed source; record as a shortcoming that the measured gain is whole-Snort vs an unnamed fallback matcher and mostly reflects inherited Hyperscan algorithms. Wiki Benchmarks link is dead; later arm64 correctness fixes postdate the measured 5.4.11.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** OpenWrt commit (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/openwrt/packages/commit/d62471c093bfec5c5203ade9e5175a8ef7ae80b1>
  - <https://github.com/openwrt/packages/commit/d62471c093bfec5c5203ade9e5175a8ef7ae80b1.patch>
  - <https://github.com/VectorCamp/vectorscan>
  - <https://github.com/VectorCamp/vectorscan/commits/develop>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/README.md>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/LICENSE>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/CHANGELOG-vectorscan.md>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/benchmarks/benchmarks.cpp>
  - <https://github.com/VectorCamp/vectorscan/wiki>
  - <https://github.com/VectorCamp/vectorscan/wiki/_pages>
  - <https://github.com/VectorCamp/vectorscan/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/wiki/VectorCamp/vectorscan/Home.md>
  - <https://github.com/VectorCamp/vectorscan/pull/391>
  - <https://github.com/VectorCamp/vectorscan/issues/382>
  - <https://raw.githubusercontent.com/openwrt/packages/master/net/snort3/Makefile>
  - <https://raw.githubusercontent.com/openwrt/packages/master/net/snort3/files/snort.uc>
  - <https://raw.githubusercontent.com/openwrt/packages/master/libs/vectorscan/Makefile>
  - <https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/servers-and-cloud-computing/vectorscan/_index.md>
  - <https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/servers-and-cloud-computing/vectorscan/snort.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/README.md>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/CHANGELOG-vectorscan.md>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/cmake/compiler.cmake>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/cmake/cflags-generic.cmake>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/cmake/boost.cmake>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/cmake/osdetection.cmake>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/cmake/archdetect.cmake>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/src/hs.h>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/src/hs_common.h>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/src/hs_compile.h>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/src/hs_runtime.h>
  - <https://raw.githubusercontent.com/VectorCamp/vectorscan/develop/benchmarks/benchmarks.cpp>
  - <https://github.com/VectorCamp/vectorscan/tree/develop/src/nfa>
  - <https://github.com/VectorCamp/vectorscan/issues>
  - <https://github.com/VectorCamp/vectorscan/issues/417>
  - <https://github.com/VectorCamp/vectorscan/issues/382>
  - <https://github.com/VectorCamp/vectorscan/issues/357>
  - <https://github.com/VectorCamp/vectorscan/commits/develop>
  - <https://github.com/openwrt/packages/commit/d62471c093bfec5c5203ade9e5175a8ef7ae80b1>
  - <https://raw.githubusercontent.com/openwrt/packages/master/net/snort3/Makefile>
  - <https://raw.githubusercontent.com/openwrt/packages/master/net/snort3/files/snort.uc>
  - <https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/servers-and-cloud-computing/vectorscan/_index.md>
  - <https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/servers-and-cloud-computing/vectorscan/snort.md>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/master/engines/hyperscan/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/master/engines/hyperscan/Cargo.toml>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/vectorcamp/vectorscan`) · [data/wave3/enrich/raw/github_com_vectorcamp_vectorscan.json](../../../data/wave3/enrich/raw/github_com_vectorcamp_vectorscan.json) (enrichment confidence 0.75)

</details>
