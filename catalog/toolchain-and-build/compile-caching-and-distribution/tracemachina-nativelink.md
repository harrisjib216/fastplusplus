# NativeLink

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compile caching and distribution](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `FSL-1.1-Apache-2.0` · 🟢 active

> REAPI remote build-cache and execution server for Bazel/Buck2/CMake; beats local-only, non-distributed builds.

| | |
|---|---|
| **Beats** | local, non-distributed single-machine build (no remote cache / no distributed compilation) |
| **Claimed result** | Independent blog (Reid Kleckner, 2026-03-30): a full LLVM + Clang build with CMake/Ninja took 1026.169s locally on the author's laptop (Ninja default -j, no remote execution, PCH disabled) vs 257.527s distributed through recc + NativeLink at -j96 over WiFi, about 4.0x (the intro says 'four times faster than my laptop, going from 1026s to 253s'). With PCH enabled, the local build took 682.778s, and the author writes that 'the distributed build is only 2.65x faster than the local build', calling the 4x an 'overstatement'. In the recc build directory, a clean rebuild with a full cache hit rate took 92.885s vs 266.600s for the preceding cold build (over VPN). NativeLink's homepage separately claims '4-15x faster builds' demonstrated on LLVM, with no methodology. |
| **Workload** | Full LLVM + Clang project build (\~4,468 build actions, culminating in llvm-readelf) via CMake+Ninja and the recc REAPI client, comparing a local laptop build to the same build distributed across a home Kubernetes/Talos cluster through NativeLink. |
| **Metric** | build-time |
| **Hardware** | Client: the author's laptop (model and CPU not stated), over WiFi (the cache test was over a VPN). Remote: a home Kubernetes cluster on Talos Linux made of small, low-power control nodes plus extra unpictured nodes; the author says his Framework desktop 'is doing most of the heavy lifting'. No CPU models are stated. |
| **Compiler and flags** | Toolchain from LLVM's ghcr.io/llvm/ci-ubuntu-24.04 container (LTO/BOLT-optimized clang); CMake + Ninja with recc as the compiler launcher; the linked demo repo's reconfig.sh uses CMAKE_BUILD_TYPE=Release, LLVM_TARGETS_TO_BUILD=X86, CMAKE_DISABLE_PRECOMPILE_HEADERS=ON; distributed run at -j96, local run at Ninja's default -j |
| **Adoption** | 1.6k stars; vendor claims 10B+ build requests/month in production, used by Samsung and others |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/TraceMachina/nativelink) · [benchmark](https://reidkleckner.dev/posts/llvm-recc-nativelink/) |

## Verdict

Independent blog (Reid Kleckner, 2026-03-30): a full LLVM+Clang build via CMake/Ninja/recc took 1026s locally (laptop, PCH disabled, Ninja default -j) versus 257s distributed at -j96 through NativeLink on a home Kubernetes/Talos cluster (\~4.0x); with PCH enabled the local build dropped to 683s, making the real distributed gain 2.65x, which the author calls the 4x headline an overstatement. No CPU models are given for the laptop or cluster nodes, and each configuration was run once (evidence tier C).

## Use it when

- Already building with Bazel, Buck2, Goma/Siso, or another REAPI client, where integration is closer to transparent
- CMake/Ninja C/C++ projects willing to add the recc compiler-launcher shim
- Large action graphs with many independent, cacheable steps (e.g. LLVM/Chromium-scale monorepos)
- Teams/CI where a cache and worker pool shared across many machines pays off more than single-machine speed
- You can operate a Docker/Kubernetes cluster to host the CAS, scheduler and workers

## Skip it when

- Solo local dev with no cluster to distribute to — the verified benchmark shows no win without remote workers
- Builds that depend on precompiled headers through recc: its input scanner doesn't recognize PCH files, so PCH had to be disabled, and re-enabling it locally cut the measured gain from \~4.0x to \~2.65x
- Teams that want a single dependency-free binary rather than standing up and operating a CAS/RE server
- Production use of the metrics/persistent-worker modules without a commercial license — those are Business Source Licensed separately from the FSL-1.1 core
- Windows Bazel builds: README claims Windows support but an open issue reports Bazel tests failing on Windows x64 (#485, unresolved since 2024)

## How it is fast

Content-addressed storage caches and reuses previously-built objects across machines and CI runs so unchanged actions are skipped entirely. A scheduler fans independent build actions from the action graph out to remote worker pods for parallel execution over the REAPI protocol (the same protocol Bazel, Buck2, and reclient use). In the verified benchmark this let a CMake/Ninja LLVM build run at -j96 across a home Kubernetes cluster instead of the client machine's default -j.

## Compared with alternatives

Pick NativeLink over FASTBuild/HOMCC/octobuild when you're already on, or willing to adopt, a Bazel Remote Execution API client (Bazel, Buck2, or CMake via recc) and want a shared cache plus a horizontally scalable Kubernetes-style execution cluster, rather than the single-protocol local caching (FASTBuild) or distcc-style compiler forwarding (HOMCC, octobuild) the siblings use.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | an REAPI-speaking build client (Bazel, Buck2, Goma/Siso, or CMake+Ninja plus recc); Docker or Kubernetes to host the CAS/scheduler/worker services |
| **Minimum toolchain** | Rust 1.97.1 (edition 2024) to build from source (Cargo.toml, v1.7.1); prebuilt Docker images available for consumers who don't build it |
| **Platforms** | Unix-based OSes and Windows per README; prebuilt container images are x86_64 only; Windows has at least one open, unresolved Bazel-test-failure issue (#485) |
| **Thread safety** | not documented (it is a server/service, not an in-process data-structure API) |
| **Drop-in for the baseline** | partial — explain: near-transparent for clients that already speak the Bazel Remote Execution API (Bazel, Buck2, reclient); CMake/Ninja needs the recc launcher shim, and in the verified benchmark PCH had to be disabled because recc's input scanner didn't see precompiled headers |

## Gotchas

- recc's input scanner doesn't recognize precompiled headers as build inputs; disabling PCH was required, and doing so alone accounts for most of the gap between the claimed 4.0x and the author's corrected 2.65x
- Core is FSL-1.1 (source-available, permits only non-competing use, converts to Apache-2.0 two years after each release, not OSI-approved); the metrics and persistent-worker modules are separately Business Source Licensed, needing a commercial license for shared production use
- Open issue reports Bazel tests failing on a Windows x64 machine (#485, open since 2024)
- The only third-party speedup evidence is a single-author, single-run personal blog post; the vendor's own '4-15x' homepage claim has no published methodology

## Caveats and trade-offs

Single-author personal experiment, one run per configuration, by an independent LLVM/Clang contributor. It compares a laptop against a laptop plus a remote cluster (mostly a Framework desktop), not against distcc, icecc or ccache. The author concedes the 4x headline is an overstatement: with PCH enabled locally the gain is 2.65x, because recc could not handle PCH. No CPU models are given. NativeLink's '4-15x' homepage figure has no published methodology. License is FSL-1.1-Apache-2.0 (not OSI; each release converts to Apache-2.0 after two years).

Requires standing up a CAS/remote-execution server (Docker/Kubernetes) rather than a single local binary; core cache is source-available FSL-1.1 (converts to Apache-2.0 two years after each release) and some modules (metrics, persistent-worker) are Business Source License requiring a commercial license for shared production use; integrates via the Bazel Remote Execution API (Bazel, Buck2, reclient/recc, etc.) rather than being a drop-in ccache/distcc substitute.

## Maintenance

Actively maintained (last commit 2026-09-24; 1.6k stars, 244 forks; vendor claims 10B+ build requests/month in production including Samsung); usability is 'reference' because it's infrastructure to deploy and operate, not a library to link.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification B, tier now C.
- **Tier reason:** The blog is a single-author personal experiment (one run each), not peer-reviewed and not an established third-party suite. Its scripts are public (rnk/llvm-nativelink-demo build-llvm-recc/reconfig.sh: CMAKE_BUILD_TYPE=Release, /opt/llvm clang, PCH disabled), but no CPU model is given for the laptop or the cluster nodes, so it is not A, and a one-off blog falls to C.
- **Verifier notes:** The record's hardware was wrong: the laptop was the client, the Framework desktop was a cluster worker, and 'OptiBlex' nodes do not appear on the page. The 'LLVM builds 4 times faster ... 17 minutes to 4' vendor quote was not found; the homepage says '4-15x faster builds'. GitHub reports license NOASSERTION; LICENSE is FSL-1.1-Apache-2.0, so 'reference' is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://reidkleckner.dev/posts/llvm-recc-nativelink/>
  - <https://github.com/rnk/llvm-nativelink-demo>
  - <https://github.com/TraceMachina/nativelink>
  - <https://www.nativelink.com/>
- **Sources the enricher read:**
  - <https://github.com/TraceMachina/nativelink>
  - <https://github.com/TraceMachina/nativelink/blob/main/README.md>
  - <https://github.com/TraceMachina/nativelink/blob/main/LICENSE>
  - <https://github.com/TraceMachina/nativelink/blob/main/Cargo.toml>
  - <https://reidkleckner.dev/posts/llvm-recc-nativelink/>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/tracemachina/nativelink`) · [data/wave2/enrich/raw/github_com_tracemachina_nativelink.json](../../../data/wave2/enrich/raw/github_com_tracemachina_nativelink.json) (enrichment confidence 0.55)

</details>
