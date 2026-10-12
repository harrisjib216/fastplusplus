# Mesh

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Drop-in malloc that compacts fragmented C/C++ heaps by page remapping; 16% less memory than Firefox's jemalloc, 39% on Redis.

| | |
|---|---|
| **Beats** | jemalloc (Firefox, Redis) and glibc malloc (SPEC CPU2006, Ruby) |
| **Claimed result** | Reduces Firefox mean heap by 16% vs jemalloc and Redis by 39%; 400.perlbench peak RSS 564 MB vs 664 MB glibc, 614 MB jemalloc, 732 MB Hoard (15% below glibc); SPECint geomean memory -2.4% and runtime +0.7% vs glibc; 3.9% runtime overhead on perlbench |
| **Workload** | Heap size over time for Firefox 57 Speedometer, Redis 4.0.2 insertion/defrag test, SPECint 2006, Ruby microbenchmark. |
| **Metric** | memory |
| **Hardware** | MacBook Pro, Intel i7-5600U, 16 GiB RAM, Linux 4.18 Ubuntu Bionic |
| **Compiler and flags** | SPEC built with clang 4.0 -O2; Mesh built with gcc 8 -O3 -flto |
| **Adoption** | 1.9k stars; PLDI 2019 paper |
| **Last commit** | 2026-03-25 |
| **Links** | [repository](https://github.com/plasma-umass/Mesh) · [benchmark](https://github.com/plasma-umass/Mesh/blob/master/mesh-pldi19-powers.pdf) |

## Verdict

The PLDI 2019 paper ran on an Intel i7-5600U with 16 GiB under Linux 4.18 (SPEC built with clang 4.0 -O2, Mesh with gcc 8 -O3 -flto): mean RSS on Firefox 57 Speedometer was 530 MB vs 632 MB with bundled jemalloc (16%, under 1% score loss); Redis 4.0.2 got the same 39% heap reduction as jemalloc 3.6.0 active defrag with 0.23 s of meshing vs 1.49 s of defrag; 400.perlbench peak RSS was 564 MB vs 664 MB glibc 2.26 (+3.9% runtime); SPECint geomean -2.4% memory, +0.7% time.

## Use it when

- Long-running, allocation-heavy servers or browsers whose RSS grows from fragmentation (many small objects of mixed lifetimes), e.g. Redis-style caches where you would otherwise rely on jemalloc's active defragmentation.
- You cannot change the application (no custom arenas, no defrag API) but can LD_PRELOAD an allocator on Linux or macOS.
- Memory-constrained deployments where a few percent runtime overhead is acceptable for 15-40% lower heap size on fragmenting workloads.
- Workloads with regular allocate/free patterns (the paper's Ruby microbenchmark), where randomized placement gives meshing room that non-randomized allocators lack.

## Skip it when

- You want speed: Mesh does not beat glibc or jemalloc on runtime; the paper shows +0.7% SPECint geomean, +3.9% on perlbench and +10.7% on the Ruby microbenchmark, and Redis insertion took 1.76 s vs 1.72 s with jemalloc.
- Workloads without fragmentation or dominated by objects over 16 KiB: large objects bypass meshing, and SPECint memory only dropped 2.4% geomean.
- Programs that install their own SIGSEGV handlers or rely on fault handling (JVMs, sanitizers, some runtimes): Mesh interposes sigaction for its write barrier, and open issues report segfaults under OpenJDK 16 (#87) and when preloaded (#72, #99).
- Applications that depend on transparent huge pages: meshing works at 4 KiB (16 KiB on Apple Silicon) granularity and the paper notes poor interaction with THP; huge-page support is an open issue (#89).
- Some users report higher memory than jemalloc 5.1, Chrome or Firefox (#116, #45, #67), and there are no tagged releases (#114).

## How it is fast

Meshing: when two spans of the same size class have non-overlapping live objects, Mesh copies one span's objects into the other's physical page and remaps both virtual spans onto that one physical span (the arena is a memfd_create-backed shared mapping, so mmap can alias offsets), so object addresses never change. Candidate pairs come from SplitMesher, a randomized matching algorithm with a probabilistic guarantee, and shuffle vectors randomize object placement within spans at bump-pointer cost so pages stay meshable. Meshing runs concurrently, using mprotect plus a SIGSEGV handler as a write barrier, and is rate-limited (default at most every 100 ms).

## Compared with alternatives

Pick Mesh over speed-oriented siblings such as v8malloc, FastAlloc or Spaces when fragmentation-driven RSS is the problem and you accept equal-or-slightly-slower runtime; IsoAlloc targets hardening, and libpas returns pages sooner but only inside WebKit, while Mesh is the only catalogued allocator that compacts an unmodified C/C++ heap.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none at runtime beyond libc; build uses Bazel wrapped in a Makefile (CMakeLists.txt also present, fetching Heap Layers and googletest) |
| **Minimum toolchain** | C++17 (bumped in November 2025) |
| **Platforms** | Linux and macOS on x86-64; aarch64 build flags and Apple Silicon 16 KiB pages handled in recent code; Windows work in progress; 32-bit unsupported |
| **Thread safety** | Thread-safe: per-thread heaps with shuffle vectors, atomic bitmaps for remote frees, global heap lock held during meshing; fork/spawn races fixed in January 2026 |
| **Drop-in for the baseline** | yes |

## Gotchas

- Reserves a 64 GB virtual arena on Linux (32 GB on macOS) backed by a memfd temporary file, so strict overcommit or address-space limits can break it.
- Meshing adds page-table entries and brief pauses (paper: max 7.5 ms on Firefox, 22 ms on Redis); tune with MESH_PERIOD_MS, MESH_BACKGROUND_THREAD or mallctl.
- The CMake RANDOMIZATION option (0, 1 or 2) and DISABLE_MESHING change behavior; with randomization off the Ruby benchmark saved only 3%.
- Memory must be measured as RSS including page tables (the paper used its mstat cgroup tool); allocator-reported heap sizes do not show meshing savings.

## Known shortcomings

- Wins memory only; runtime costs +0.7% to +10.7%. 29 open issues: crashes 72, 87 and 99 (OpenJDK 16 segfault), more memory than jemalloc 5.1, Chrome and Firefox (116, 45, 67), distro build failures, no releases (114). Reserves a 64 GB virtual arena and interposes sigaction for its write barrier.

## Caveats and trade-offs

Benefit is memory footprint, not speed; runtime is equal or slightly slower. Paper numbers from 2019 on old software versions (jemalloc 3.6.0, glibc 2.26). Paper PDF read from the repo; benchmark scripts not in a dedicated directory, so reproducibility is partial.

Drop-in malloc replacement for Linux and macOS (Windows in development); trades small runtime overhead (up to 10.7% on the Ruby microbenchmark with randomization) for memory savings; relies on virtual-memory page remapping.

## Maintenance

Active again (commits through 2026-03-25 fixing fork races, signal handling, aarch64 atomics), Apache-2.0, 1.9k stars, but 29 open issues including crashes and build failures on several distros and no releases.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** PLDI 2019 paper checked into the repo states every claimed number (Firefox -16% vs bundled jemalloc, Redis -39%, perlbench peak RSS 564 MB vs 664/614/732 MB, SPECint geomean memory -2.4% and runtime +0.7%, perlbench +3.9%) plus clang 4.0 -O2 / gcc 8 -O3 -flto on an i7-5600U. Peer-reviewed but no dedicated benchmark harness in the repo, so B not A.
- **Verifier notes:** Win is memory footprint, not speed (runtime equal or slightly worse); metric 'memory' is correctly set. Apache-2.0, 1.9k stars, last commit 2026-03-25 verified.
- **Shortcomings recorded by:** peer-reviewed paper, read from a repo copy
- **Pages the verifier opened:**
  - <https://github.com/plasma-umass/Mesh>
  - <https://github.com/plasma-umass/Mesh/commits>
  - <https://github.com/plasma-umass/Mesh/blob/master/mesh-pldi19-powers.pdf>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/README.md>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/plasma-umass/Mesh>
  - <https://github.com/plasma-umass/Mesh/issues>
  - <https://github.com/plasma-umass/Mesh/commits/master>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/README.md>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/mesh-pldi19-powers.pdf>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/src/libmesh.cc>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/src/meshing.h>
  - <https://raw.githubusercontent.com/plasma-umass/Mesh/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/plasma-umass/mesh`) · [data/wave11/enrich/raw/github_com_plasma_umass_mesh.json](../../../data/wave11/enrich/raw/github_com_plasma_umass_mesh.json) (enrichment confidence 0.8)

</details>
