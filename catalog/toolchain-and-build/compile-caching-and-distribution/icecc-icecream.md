# icecream (icecc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0-or-later` · 🟡 stale

> SUSE's distcc-derived distributed C/C++ compiler with a central scheduler; beats single-machine make when several networked machines are free.

| | |
|---|---|
| **Beats** | local single-machine compilation (make without icecream) |
| **Claimed result** | Linux 2.6.16: 315s local (make -j1) vs 230s with icecream over WLAN (make -j10, about 1.37x, derived from page data) and 203s over 100MBit LAN (make -j10/100, about 1.55x, derived from page data); the file says the maximum improvement is 27% (LAN: 36%) out of a theoretical 50%. Qt 3.3.6 src/: 368s local (make -j1) vs 269s over WLAN (make -j10, about 1.37x, derived) and 239s over LAN (make -j10/100, about 1.54x, derived). Stock icecream 0.7 on the same Qt test: 349s WLAN (the file calls it a 6% speedup over local) and 253s LAN. Later note in the file (test project not named): remote with -m 1 at 0.8.0 took 257s for make -j5, and 442s without compression. Overhead of the wrapper without a cluster is about 2%. |
| **Workload** | make builds of Linux 2.6.16 (defconfig, many small C files) and the src/ subdirectory of Qt 3.3.6 (medium and large C++ files) on a two-machine icecream cluster, over 54MBit WLAN and 100MBit LAN, versus make on one machine with no icecream; 5 runs, worst and best dropped, middle 3 averaged. |
| **Metric** | build-time |
| **Hardware** | Two single-CPU machines of about the same speed (1.7GHz Pentium M); otherwise idle 54MBit WLAN, repeated on 100MBit cabled LAN |
| **Adoption** | 1.8k stars; created by SUSE based on distcc (per README) |
| **Last commit** | 2026-03-04 |
| **Links** | [repository](https://github.com/icecc/icecream) · [benchmark](https://raw.githubusercontent.com/icecc/icecream/HEAD/BENCH) |

## Verdict

The only numbers are a first-party BENCH file from around 2006: two single-CPU 1.7GHz Pentium M machines, five runs with the best and worst dropped, no scripts, compiler version or flags. With a development patch, Linux 2.6.16 defconfig fell from 315s (best local setting, make -j1) to 230s over 54MBit WLAN and 203s over 100MBit LAN, and Qt 3.3.6 src/ from 363-368s locally to 269s and 239s (27% and 36% less time against a theoretical 50%), while stock 0.7 managed only 6% over WLAN.

## Use it when

- An office or lab of shared developer workstations whose load changes: the scheduler sends work to idle, fast machines and copes with nodes joining and leaving.
- Teams whose machines carry different or frequently changing GCC/Clang versions, or that cross-compile (Yocto and embedded targets), since the client's compiler environment travels with the job.
- Large parallel C/C++ builds on a low-latency LAN of 100 Mbit or better; the README budgets about 1 Mbit per concurrent job.
- Linux, FreeBSD, DragonFlyBSD or macOS clusters (Cygwin as a client only), optionally behind ccache with CCACHE_PREFIX=icecc.

## Skip it when

- A lone machine or a non-parallel make: the README's single-file test took 1.6s with g++ against 1.9s through icecream, and BENCH calls make -j1 with icecream 'a horrible mistake' (418s against 315s local on Linux 2.6.16).
- Untrusted networks: the README says never to use it there; daemons need root, or libcap-ng capabilities, to chroot into shipped environments, and no authentication or encryption is documented.
- High-latency or lossy links (between buildings, over VPN, in the cloud): the README calls icecream very sensitive to latency and packet loss, and stock 0.7 gained only 6% over WLAN in BENCH.
- Windows/MSVC builds, which are not supported.
- Builds that lean on precompiled headers, Clang modules or coverage: those flags force local work or are stripped for remote jobs, and open issue #618 reports Clang 13 PCH builds failing remotely and being silently recompiled locally.

## How it is fast

The gain is job-level parallelism across machines, steered by a scheduler that tracks each host's measured speed and load and gives every job to the host expected to finish it soonest (default 'fastest' algorithm; random, round_robin and least_busy are alternatives), preferring the local machine when it is free and at least 70% as fast as the best host. Daemons are pre-loaded with one extra job so a slot never idles waiting for a round trip, and transfers are compressed (LZO originally, zstd since 1.3). By default only #include expansion runs locally (-fdirectives-only for GCC, -frewrite-includes for Clang) and macro expansion runs remotely; shipping compiler environments lets mismatched or cross-compiling nodes contribute.

## Compared with alternatives

Pick icecream over distcc when machines are shared, come and go, or carry different compilers or targets, because distcc has a static host list and no scheduler; pick distcc on a fixed homogeneous farm where pump mode can move preprocessing off the client, and NativeLink or sccache when you want a shared cache or remote execution rather than plain job distribution.

## Integration

| | |
|---|---|
| **Form** | standalone tool built with autotools or taken from distro packages: icecc client stub plus compiler symlinks, iceccd daemon, icecc-scheduler; the icemon or icecream-sundae monitors are separate projects |
| **Dependencies** | lzo2, libzstd and libarchive (required by configure); libcap-ng (default on Linux); a C++11 compiler to build it |
| **Minimum toolchain** | Builds with -std=c++11; wraps GCC and Clang (C, C++, Objective-C/C++) |
| **Platforms** | Linux, FreeBSD, DragonFlyBSD and macOS as both client and server, with cross-compiling between them; Cygwin as client only |
| **Thread safety** | Not a library; safe under make -jN. Each daemon runs at most -m jobs at once and the scheduler assigns jobs centrally |
| **Drop-in for the baseline** | partial — compiler flags and outputs are unchanged and it hooks in via PATH stubs, but every node needs iceccd, the network needs a reachable scheduler and open ports (TCP 10245 and 8765, UDP 8765), and the build must use a high make -j |

## Gotchas

- Mixed icecream versions degrade the cluster: nodes running older versions may be excluded, and daemons older than 1.1 pick a random scheduler when several run on one network.
- Many cases fall back to local work without failing the build (PCH, -pedantic forcing local preprocessing per issue #630, preprocessing errors), so a build can quietly run mostly on the submitting machine; icemon shows where jobs actually ran.
- Open issue #657 reports a master-only regression (not in any release) where pick_server_fastest() computes a uint8_t weight_factor of 0, so host speed statistics are never refreshed and newly joined hosts can be skipped.
- Benchmark caveats in BENCH: the headline rows come from a development patch ('dirk's no-latency') on a two-node cluster, the author calls the identical 27%/36% gains for Linux and Qt 'astonishing' and in need of explanation, and the later rows (make-it-cool, 0.8.0 at 257s, 442s without compression) name no project and have no local baseline.

## Known shortcomings

- First-party 2006-2008 numbers on a 2-node cluster with no compiler version or flags; headline rows come from development patches, not a release (stock 0.7 was only 6% over local on WLAN); no measured comparison with distcc.
- Enricher: headline rows from a development patch on a two-node cluster with unexplained identical gains; later rows name no project and have no local baseline; no release since 1.4 (2022); unreleased scheduler regression #657.

## Caveats and trade-offs

First-party BENCH file with results only, not scripts: no compiler version or flags, no CPU beyond 1.7GHz Pentium M, circa 2006 (mentions a 2006-06-16 branch) on a two-node cluster, much older than current icecream. The cluster has only two nodes, so the 27-36% gains are bounded by a theoretical 50%. The headline rows are for development patches ('dirk's no-latency' patch, 'make-it-cool' branch), not a release; stock 0.7 gained only 6% over local on WLAN. The make -j1 local baseline is the fastest local setting for Linux (-j10 local was 334s); for Qt, local -j3 was 363s. No measured comparison against distcc anywhere in the repo; the distcc comparison in README is qualitative. Percentages are quoted from the file's own text. [retier] Enricher: the headline BENCH rows come from a development patch on a two-node cluster, and the author calls the identical 27%/36% gains for Linux and Qt 'astonishing', which needs explaining; the later rows (0.8.0: 257 s, 442 s without compression) name no project and have no local baseline. Unreleased master has a scheduler regression (#657: weight_factor is always 0, so host stats are never refreshed).

Needs iceccd on every node and a central scheduler (iceccd/icecc-scheduler); jobs ship preprocessed source and compiler environments across the network. README says the scheduler gives it advantages over distcc (idle-cycle scheduling, changing compiler versions, cross-compiling) but gives no numbers for that. A lone machine gains nothing: README's own test took 1.6s locally against 1.9s via icecream for one job, and BENCH calls running icecream without parallel make 'a horrible mistake' (make -j1 took 418s vs 315s local). GPL licence.

## Maintenance

Last release is 1.4 (2022-03-04) and only a handful of commits have landed since the end of 2022 (latest 2026-03-04), with about 72 open issues, so it is effectively in maintenance mode, though distros still package it and the GPL v2 code is usable as is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party BENCH file with results against make without icecream; no scripts, compiler version or flags, only a CPU model (1.7GHz Pentium M), so C.
- **Verifier notes:** All quoted numbers match BENCH. Added stock-0.7 rows and derived ratios. gh CLI blocked; metadata from github.com pages (1.8k stars, last commit 2026-03-04, GPL v2-or-later per daemon/main.cpp header).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-12 (wave 2 book seed pass, 2026-10-24); enrichment (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/BENCH>
  - <https://github.com/icecc/icecream>
  - <https://github.com/icecc/icecream/commits>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/daemon/main.cpp>
- **Sources the enricher read:**
  - <https://github.com/icecc/icecream>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/README.md>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/BENCH>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/NEWS>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/doc/icecream.adoc>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/doc/icecc.adoc>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/doc/iceccd.adoc>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/doc/icecc-scheduler.adoc>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/doc/icecc-create-env.adoc>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/client/main.cpp>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/client/cpp.cpp>
  - <https://raw.githubusercontent.com/icecc/icecream/HEAD/client/arg.cpp>
  - <https://github.com/icecc/icecream/commits/master>
  - <https://github.com/icecc/icecream/tags>
  - <https://github.com/icecc/icecream/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/icecc/icecream/issues/657>
  - <https://github.com/icecc/icecream/issues/645>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/icecc/icecream`) · [data/wave2/enrich/raw/github_com_icecc_icecream.json](../../../data/wave2/enrich/raw/github_com_icecc_icecream.json) (enrichment confidence 0.8)

</details>
