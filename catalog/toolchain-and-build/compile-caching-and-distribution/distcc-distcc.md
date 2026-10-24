# distcc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0-or-later` · 🟢 active

> Compiler front end that farms C/C++ compile jobs out to networked servers; beats a local single-machine make on big parallel builds.

| | |
|---|---|
| **Beats** | local single-machine compilation (make with every compile run locally); also plain distcc for the pump-mode rows |
| **Claimed result** | Linux 2.6.25: 818.3s local, 203.2s plain distcc (about 4.0x, derived from page data), 134.9s pump mode (about 6.1x, derived from page data). Samba 3.0.20: 314.0s local, 101.8s plain (about 3.1x, derived), 31.4s pump (about 10x, derived). glibc 2.6: 946.4s local, 534.0s plain, 357.8s pump. binutils 2.18: 125.8s local, 35.4s plain, 28.7s pump. httpd 2.0.43: 139.8s local, 85.1s plain, 80.1s pump. Page text: pump mode is sometimes more than 3x faster than plain distcc (Samba), and up to 2.5x faster than non-pump on 4-processor clients for large Google projects. hello-2.1.1 gets slower: 0.7s local, 0.9s plain, 1.1s pump. |
| **Workload** | Wall-clock make time (configure excluded) for binutils-2.18, glibc-2.6, httpd-2.0.43, linux-2.6.25, samba-3.0.20 and hello-2.1.1, built entirely locally versus distributed to 38 compile servers (152 CPUs) with make -j40, in plain mode and in pump mode (also -j80); each case run 5 times and averaged. |
| **Metric** | build-time |
| **Hardware** | Client: 2.8GHz Intel Pentium 4, 2G RAM, Linux 2.6.18.5 (modified Ubuntu 6.06). Servers: 38 machines described as 4 CPU 2GHz AMD Dual Core Processor 270 with 2G RAM (152 CPUs in total). |
| **Adoption** | 2.3k stars; README says it has compiled the Linux kernel, KDE, GNOME and Samba, and run with hundreds of servers |
| **Last commit** | 2026-07-08 |
| **Links** | [repository](https://github.com/distcc/distcc) · [benchmark](https://raw.githubusercontent.com/distcc/distcc/HEAD/doc/web/benchmark.html) |

## Verdict

Google's 2008 page timed make only (configure excluded), five runs averaged, for six open-source packages on a 2.8GHz Pentium 4 client: local make -j1 against make -j40 on 38 servers with 152 CPUs (2GHz AMD dual-core 270 machines). Linux 2.6.25 fell from 818s to 203s plain (about 4.0x) and 135s in pump mode (about 6.1x), Samba 3.0.20 from 314s to 31s with pump (about 10x), hello-2.1.1 got slower, and no compiler version or flags are given.

## Use it when

- Large C/C++ builds with flat, highly parallel Makefiles (Linux kernel, Samba) where a modest workstation can drive many idle Linux/BSD servers on a trusted LAN.
- Fleets where every machine has the same gcc or clang release (and, for pump mode, identical system headers, e.g. one distro image).
- Pump mode on clusters of dozens to hundreds of server CPUs; README.pump says below about ten CPUs local preprocessing keeps up and pump shows no major gain.
- Plain mode stacked under ccache (CC='ccache distcc gcc') so cache hits skip the network and misses are distributed.
- Cross-compiling: the client rewrites gcc to a fully qualified target name and adds -target for clang, so servers can run a matching cross compiler.

## Skip it when

- Small projects or Makefiles that recurse into subdirectories sequentially: hello-2.1.1 got slower (0.7s local, 0.9s plain, 1.1s pump) and the benchmark page says sequential sub-makes benefit little.
- Untrusted networks: in TCP mode anyone who can reach the port can run arbitrary commands as the distccd user and traffic is neither encrypted nor signed (CVE-2004-2687 covered unrestricted 2.x daemons); use SSH, which the docs call much slower, or the optional GSS-API auth.
- A strong many-core client with only a few remotes: open issue #325 reports a 40-core box building a kernel in about 16 minutes locally but about 40 minutes with distcc across two such boxes; host lists are static and there is no load-aware scheduler.
- MSVC or native Windows builds: only gcc-compatible compilers are wrapped, and Windows needs Cygwin (open issue #339 says the daemon will not run there).
- Pump mode together with ccache (the FAQ says ccache prevents pump mode), or builds that rewrite headers mid-build, which pump mode assumes do not change.

## How it is fast

It is plain job-level parallelism across machines: make -j issues many independent compiles, the client does only cheap work (preprocess, compress, send) and the expensive compiler passes run on remote CPUs. Pump mode attacks the client-side preprocessing bottleneck with an include server that statically analyses #include directives (computing a superset of possible include targets, memoised across the build) and LZO-compresses each file once, which the man page says cuts compile-preparation time by up to an order of magnitude. Nothing is cached: every compile runs every time.

## Compared with alternatives

Pick distcc over icecream when you want the simplest scheduler-free setup with a static host list and optional SSH transport, and over NativeLink when the build is plain make/CMake rather than Bazel-style remote execution; pick icecream when machines come and go or carry different compilers (its scheduler and shipped compiler environments), HOMCC for low-bandwidth links where its README shows it beating distcc, and ccache or sccache when repeat builds rather than cold builds dominate.

## Integration

| | |
|---|---|
| **Form** | standalone tool built from source (autotools) or distro packages: distcc client wrapper, distccd daemon, pump script with a Python include server |
| **Dependencies** | GNU Make, a C compiler and libpopt (no longer bundled as of the unreleased 3.z notes); Python &gt;= 3.1 with headers for pump mode, tests and the benchmark harness; optional GTK for the monitor and Avahi for zeroconf |
| **Minimum toolchain** | Any gcc or clang on client and servers, ideally the exact same release everywhere; pump mode needs distcc/distccd 3.0 or later on both ends |
| **Platforms** | Unix-like systems (Linux, BSDs, macOS, Solaris per the FAQ); Windows only through Cygwin; servers must emit the client's object format (same arch or a cross compiler) |
| **Thread safety** | Not a library; safe under make -jN. distccd forks per job and each host entry has a slot limit (host/N); the client coordinates slots with lock files in \~/.distcc/lock |
| **Drop-in for the baseline** | partial — the compiler command line, flags and outputs are unchanged and it hooks in via CC= or a masquerade PATH, but every server needs distccd plus a matching compiler, DISTCC_HOSTS must be configured, and the build must run with a high make -j |

## Gotchas

- Silent fallbacks: remote failures recompile locally, and pump mode drops to plain mode when the include server hits an error; the benchmark authors found pump runs that had fallen back without notice, and open issue #574 says DISTCC_FALLBACK=0 does not stop preprocessor fallbacks.
- distccd must be told which clients to accept (--allow, or --allow-private for private ranges; the man page says it exits with no --allow), and since 3.3 it runs only compilers masqueraded in /usr/lib/distcc, so versioned names such as x86_64-linux-gnu-gcc can be refused (issue #301); --enable-tcp-insecure lifts that at the cost of allowing arbitrary binaries.
- Stale lock files in \~/.distcc/lock can make remote hosts look busy and throttle the build (comments on issue #325, where removing the locking restored full utilisation).
- Harness caveats in the published benchmark: the local_01 baseline is make -j1 on the single Pentium 4 client (cpu% 60-84%, no local -j2 row), and pump rows use the ',cpp,lzo' host options (pump requires LZO) while plain rows ran uncompressed even though bench/compiler.py has an 'lzo' plain mode, so the pump-over-plain ratio mixes in compression.

## Known shortcomings

- First-party 2006-2008 numbers on old hardware with no compiler version or CFLAGS; one P4 client against 152 server CPUs, configure excluded from the timing.

## Caveats and trade-offs

First-party Google/distcc page dated 2008 (copyright line) on 2008-era hardware. The harness is in the repo (bench/benchmark.py, Build.py, compiler.py, ProjectDefs.py: exact project tarballs plus configure/build commands, compiler invoked as cc/gcc through a masquerade script farm), but no compiler version or CFLAGS are stated anywhere, so not tier A. The local baseline is one 2.8GHz Pentium 4 client against 152 server CPUs, which inflates the ratio; the page itself says a multi-processor client would show smaller gains. Only make time is counted, not configure. The page notes pump runs that silently fell back to plain mode while collecting results. The ratios above marked derived are computed from the page's wall-time column. README.md separately claims three machines are 2.6 times faster than one and README.pump says pump mode can distribute compilations up to 10X faster than plain distcc (compile step, not whole build); neither number is on the benchmark page. No comparison with ccache, icecream or a modern build system.

Needs the distccd daemon and a compatible compiler on every volunteer machine and a fast network (a slow network can cancel the gain). Plain mode ships preprocessed source and still preprocesses on the client; pump mode needs identical system headers on client and servers, assumes sources and headers do not change during the build, and falls back to plain distcc when it hits an error (the page says the Linux kernel needed special handling). Small projects get slower (hello-2.1.1). README.pump says pump mode will probably show no major gain with fewer than about ten CPUs. GPL licence.

## Maintenance

Last tagged release is 3.4 (2021-04-11); master still receives fixes (latest commit 2026-07-08, unreleased 3.z notes), but the original author's pinned 2023 'New maintainers needed' issue is still open with no release since, so treat it as community-maintained GPL v2 software that most distros package.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party (Google, 2008) benchmark page with walltime table against local_01 builds; harness code is public (bench/benchmark.py, bench/ProjectDefs.py) and CPU models are stated, but compiler version and flags are not, so it falls short of A.
- **Verifier notes:** All walltime numbers and derived ratios match doc/web/benchmark.html; README 2.6x and README.pump 10X quotes confirmed. gh CLI blocked in cloud session; metadata from github.com pages (2.3k stars, last commit 2026-07-08, GPL v2-or-later per source headers).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-12 (wave 2 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/doc/web/benchmark.html>
  - <https://github.com/distcc/distcc>
  - <https://github.com/distcc/distcc/commits>
  - <https://github.com/distcc/distcc/tree/master/bench>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/ProjectDefs.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/compiler.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/Build.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/README.pump>
- **Sources the enricher read:**
  - <https://github.com/distcc/distcc>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/README.md>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/README.pump>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/INSTALL>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/NEWS>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/doc/web/benchmark.html>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/doc/web/security.html>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/doc/web/faq.html>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/man/distcc.1>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/man/distccd.1>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/benchmark.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/Build.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/compiler.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/ProjectDefs.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/Summary.py>
  - <https://raw.githubusercontent.com/distcc/distcc/HEAD/bench/Project.py>
  - <https://github.com/distcc/distcc/commits/master>
  - <https://github.com/distcc/distcc/issues?q=is%3Aissue+is%3Aopen+pump>
  - <https://github.com/distcc/distcc/issues/488>
  - <https://github.com/distcc/distcc/issues/325>
  - https://nvd.nist.gov/vuln/detail/cve-2004-2687 (search result snippet only)
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/distcc/distcc`) · [data/wave2/enrich/raw/github_com_distcc_distcc.json](../../../data/wave2/enrich/raw/github_com_distcc_distcc.json) (enrichment confidence 0.8)

</details>
