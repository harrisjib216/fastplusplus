# HOMCC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `MIT` · 🟢 active

> Distributed C/C++ compiler wrapper replacing distcc with server-side dependency caching and compression for thin uplinks.

| | |
|---|---|
| **Beats** | distcc |
| **Claimed result** | README chart 'compilation_times.png' (read visually, approximate): at 5/25 Mbps homcc \~9.2min vs distcc \~57.5min (\~6.3x); at 10/50 Mbps \~7.7min vs \~28.8min (\~3.7x); at 20/100 Mbps \~6.4min vs \~14.8min (\~2.3x); at 40/200 Mbps \~5.8min vs \~7.9min (\~1.4x); at 1000/1000 Mbps (gigabit, effectively unconstrained) \~5.8min vs \~4.9min — distcc is slightly faster once bandwidth is no longer the bottleneck (derived from page data / chart, values estimated from bar heights, not printed as text) |
| **Workload** | Distributed remote compilation of a Celonis-internal C++ codebase with clang++-14 (total server job limit 112, 60 compilation threads), measuring total remote compilation time at up/download bandwidths from 5/25 Mbps to 1000/1000 Mbps, comparing homcc vs. distcc. |
| **Metric** | compile-time |
| **Compiler and flags** | clang++-14; server job limit 112, 60 compilation threads |
| **Adoption** | 24 stars |
| **Last commit** | 2026-08-18 |
| **Links** | [repository](https://github.com/celonis/homcc) · [benchmark](https://github.com/celonis/homcc#readme) |

## Verdict

On an internal, non-public Celonis C++ codebase built with clang++-14 (server job limit 112, 60 compilation threads), the README's bar chart shows homcc beating distcc by about 6.3x at 5/25 Mbps (\~9.2 vs \~57.5 min), narrowing to \~1.4x at 40/200 Mbps, and homcc being slightly slower than distcc at gigabit (\~5.8 vs \~4.9 min). No CPU/hardware spec, raw data, or runnable benchmark script is published; the numbers are estimated from bar heights in an image, and the README's prose claim of gains 'by some orders of magnitude' overstates what its own chart shows.

## Use it when

- Remote/distributed C or C++ builds (gcc or clang) over thin or variable-bandwidth links (roughly 5-40 Mbps in the README's own numbers), e.g. work-from-home developers hitting an office build farm
- Teams already using a distcc-style CCACHE_PREFIX or conan-profile hook and willing to swap in a different client/server pair
- Need sandboxed remote compilation per client via schroot profiles or docker containers rather than running arbitrary code directly on the build host
- Debian/Ubuntu-based build infrastructure (packaged and tested as .deb on Ubuntu 22.04)
- Want to tunnel remote compiles over SSH (multiplexed ControlMaster) instead of exposing a plaintext TCP service

## Skip it when

- Gigabit or otherwise unconstrained links to the build farm — the project's own chart shows distcc is not slower (slightly faster) once bandwidth stops being the bottleneck
- Untrusted/public networks without a VPN or SSH tunnel — there is no built-in TLS; homcc transmits source over plain TCP by default and the README explicitly warns not to expose homccd publicly
- Environments needing per-client connection limits on the server — homccd does not cap simultaneous connections from one client, so a single client can exhaust the job pool
- Non-Debian/Ubuntu targets or languages other than C/C++ — schroot sandboxing and the packaging are Debian-specific, and gcc/clang are the only supported compilers
- Projects wary of small-team tooling — 24 stars, single corporate maintainer (Celonis), no independent adopters visible; internal benchmark numbers cannot be reproduced by outsiders

## How it is fast

On a cache miss homcc still sends preprocessed sources like distcc, but homccd keeps a persistent, size-bounded (LRU, `HOMCC_MAX_DEPENDENCY_CACHE_SIZE`) cache of dependency files keyed by content hash, so once warm only genuinely new headers/sources cross the network instead of the full preprocessed unit every time. Transferred sources and resulting object files are additionally compressed with lzo or lzma. Both mechanisms specifically target bandwidth, not CPU parallelism, which is why the reported gains shrink to nothing as link speed rises.

## Compared with alternatives

Pick homcc over NativeLink, FASTBuild, or octobuild specifically when your bottleneck is a thin/variable uplink to an existing distcc-style distributed build farm and you want server-side dependency caching plus compression to shrink that — NativeLink targets single-machine local build acceleration (no distribution), FASTBuild is a from-scratch build system with its own distribution/unity-build model, and octobuild is scoped to Unreal Engine's UBT/UAT toolchain; none of them are distcc drop-in replacements for bandwidth-constrained remote C/C++ compilation.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | python-lzo (&gt;=1.12, needs liblzo2-dev/apt python3-lzo) for compression; sysv_ipc for the client's semaphore-based concurrency control; optional schroot or docker for sandboxed remote execution; ssh for tunneled hosts |
| **Minimum toolchain** | Python 3.9+ (debian/control declares X-Python3-Version &gt;= 3.9; CI runs on 3.9); gcc or clang on both client and server |
| **Platforms** | Linux, packaged and CI-tested for Debian/Ubuntu (ubuntu-22.04); schroot sandboxing is Debian/Ubuntu-specific, docker sandboxing is more portable but the server itself targets Linux |
| **Thread safety** | not documented as a formal guarantee; the client uses SysV semaphores (sysv_ipc, inspectable via `ipcs -s`) to bound concurrent local/remote compilation slots, and the issue history shows multiple fixed semaphore-race and AttributeError-on-exit bugs in that mechanism |
| **Drop-in for the baseline** | partial — explain: same general workflow as distcc (CCACHE_PREFIX hook, HOST/LIMIT-style hosts file), but it is a separate protocol and daemon: you run homccd instead of distccd, configure via HOMCC_\*/HOMCCD_\* env vars or homcc.conf instead of distcc's variables, and there is no wire-protocol compatibility with distcc |

## Gotchas

- No built-in transport encryption: plain TCP hosts send source unencrypted; use an SSH-tunneled `@HOST`/`user@HOST` entry or a VPN, and never expose homccd on an untrusted network
- homccd does not limit simultaneous connections per client, so one misbehaving client can consume the entire server job pool
- docker sandboxing requires the container to bind-mount the host's /tmp to /tmp so the server-side dependency cache is reachable inside the container; schroot sandboxing has the same /tmp-mount requirement
- Client relies on SysV semaphores for concurrency bookkeeping — historically a source of race-condition bugs (see issues 'Fix SysV semaphore race', 'AttributeError on HostSemaphore __exit__'), now fixed but worth knowing if debugging odd hangs

## Caveats and trade-offs

The benchmark uses an internal, non-public Celonis C++ codebase, so it cannot be reproduced independently. The only numbers are in a chart image, with no CPU model, raw data or benchmark script. Values were read off the bar chart and are approximate. The README text claims compilation times 'smaller by some orders of magnitudes' on small uplinks, but its own chart shows at most about 6x, and distcc is slightly faster at 1000/1000 Mbps.

Gains are specific to bandwidth-constrained (work-from-home style) links via server-side dependency caching and compression; on a fast/unconstrained link (gigabit in the chart) homcc is not faster than distcc and can be marginally slower; requires running a homccd server and schroot/docker sandboxing for remote execution.

## Maintenance

Actively maintained by Celonis (last commit 2026-08-18, v1.0.4 tagged the same day, zero open issues) under the MIT license; small adoption (24 stars) but the codebase is compact and copyable/vendorable if you accept the Debian/Ubuntu-oriented packaging.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The README chart (assets/compilation_times.png) is first-party and compares homcc against distcc directly on an internal Celonis codebase with clang++-14. It gives no hardware, no benchmark script and no raw data, so it is C.
- **Verifier notes:** I opened the chart image; the bar readings in claimed_speedup match (about 9.2 vs 57.6 min at 5/25 Mbps, about 5.8 vs 5.0 min at 1000/1000). The README does not say the bandwidths were simulated, so that word was removed from workload. Metadata (MIT, 24 stars, last commit 2026-08-18) is correct.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/celonis/homcc#readme>
  - <https://github.com/celonis/homcc>
  - <https://raw.githubusercontent.com/celonis/homcc/main/assets/compilation_times.png>
- **Sources the enricher read:**
  - <https://github.com/celonis/homcc>
  - <https://github.com/celonis/homcc#readme>
  - <https://github.com/celonis/homcc/blob/main/pyproject.toml>
  - <https://github.com/celonis/homcc/blob/main/requirements.txt>
  - <https://github.com/celonis/homcc/blob/main/setup.py>
  - <https://github.com/celonis/homcc/blob/main/debian/control>
  - <https://github.com/celonis/homcc/blob/main/.github/workflows/build-main.yml>
  - <https://github.com/celonis/homcc/blob/main/homcc/__init__.py>
  - <https://github.com/celonis/homcc/blob/main/homcc/client/__init__.py>
  - <https://github.com/celonis/homcc/blob/main/LICENSE>
  - <https://github.com/celonis/homcc/issues>
  - <https://github.com/celonis/homcc/releases>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/celonis/homcc`) · [data/wave2/enrich/raw/github_com_celonis_homcc.json](../../../data/wave2/enrich/raw/github_com_celonis_homcc.json) (enrichment confidence 0.6)

</details>
