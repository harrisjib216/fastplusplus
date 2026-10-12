# XenoAtom.Allocators (TLSF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `BSD-2-Clause` · 🟢 active

> TLSF sub-allocator for .NET 8 over caller-supplied chunks; about 22% faster than CRT aligned malloc/free in its own micro-benchmark.

| | |
|---|---|
| **Beats** | C runtime malloc/free (MSVC CRT on Windows) |
| **Claimed result** | Tlsf 82.27 us vs Libc 105.34 us (ratio 0.78), '20%+ faster' |
| **Workload** | 2048 allocations and frees of random sizes 64-4096 bytes, BenchmarkDotNet, .NET 8.0.6. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X on Windows 11 |
| **Compiler and flags** | .NET SDK 8.0.300, RyuJIT, DefaultJob |
| **Adoption** | 55 stars |
| **Last commit** | 2026-02-23 |
| **Links** | [repository](https://github.com/XenoAtom/XenoAtom.Allocators) · [benchmark](https://github.com/XenoAtom/XenoAtom.Allocators) |

## Verdict

BenchmarkDotNet 0.13.12 on .NET 8.0.6 RyuJIT, AMD Ryzen 9 7950X, Windows 11: 2048 allocations of sizes drawn from {64, 96, 150, 200, 400, 1024, 4096} bytes followed by 2048 frees took 82.27 us with TLSF against 105.34 us with MSVC CRT aligned alloc/free (ratio 0.78). The TLSF side reuses its cached 64 KiB chunks, so it measures pure bookkeeping against CRT calls through interop; it is a single-threaded micro-benchmark from one run.

## Use it when

- .NET 8+ or NativeAOT code that needs deterministic O(1) allocation and free of unmanaged buffers, for example game engines, audio, or real-time loops.
- Sub-allocating a large device or mapped region (GPU heap, shared memory, file-backed buffer) where headers must not be written into the managed memory itself.
- Per-thread or per-subsystem arenas where one owner allocates and frees, so the missing locking costs nothing.
- Workloads with mixed sizes from 64 B to a few KB with heavy churn, where coalescing keeps fragmentation bounded.

## Skip it when

- C++ or C projects: this is a C# library; for native code pick a C or C++ TLSF or general allocator instead.
- Multi-threaded shared heaps: the class is documented as not thread safe and needs an external lock, which will likely erase the 22% margin.
- Many tiny allocations: the minimum allocation and alignment is 64 bytes plus 32 bytes of side metadata per block, so 8-32 byte objects waste most of their space.
- Code that expects malloc/free semantics (free by pointer, realloc, calloc): none of these exist; you must keep the token.
- Workloads that need memory returned to the OS: chunks are only released on Reset(), never when they become empty.

## How it is fast

Classic TLSF (Masmano et al., ECRTS 2004): a first-level bitmap over power-of-two size classes and second-level bitmaps over linear sub-bins, so finding a fitting free block is a couple of bit scans and allocation and free run in O(1) with immediate coalescing of physical neighbours. Block headers (32 bytes each) live in separate managed arrays grouped by 1024 rather than in-band, and the allocator takes no locks; in the benchmark the chunks stay cached after the first iteration, so the steady state never calls the CRT.

## Compared with alternatives

Pick it over rlsf or Talc (Rust TLSF-style allocators) only when you are in .NET and need a managed API over foreign memory; for native C++ arenas, fast-alloc or obstack are closer fits, and for a general-purpose malloc replacement use one of the mimalloc-class siblings.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | XenoAtom.Collections (NuGet) |
| **Minimum toolchain** | .NET 8 (net8.0 target), unsafe code allowed; NativeAOT compatible |
| **Platforms** | any .NET 8 platform (managed code); the published benchmark ran only on Windows x64 |
| **Thread safety** | Not thread safe; the source comments say to guard it with a lock or use one instance per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- The baseline in the benchmark is NativeMemory.AlignedAlloc(size, 64) and AlignedFree, which maps to _aligned_malloc on the MSVC CRT, not plain malloc; plain malloc may be faster than the reported baseline.
- Allocate throws OutOfMemoryException when the chunk allocator fails; use TryAllocate to avoid exceptions. Free throws ArgumentException on an out-of-range or already-free token.
- Maximum single allocation is 4 GB; alignment must be a power of two and is fixed per allocator instance.
- The backend chunk allocator is yours to write; the sample BasicChunkAllocator uses a Dictionary keyed by chunk count, which can reuse ids after a FreeChunk, so do not copy it unchanged for long-lived use.

## Known shortcomings

- C# library, not C++; the libc baseline is NativeMemory.AlignedAlloc (aligned_alloc), not plain malloc, and the TLSF side returns offset tokens rather than pointers.
- Additional harness caveats: the TLSF allocator reuses cached 64 KiB chunks, so steady state never calls the CRT; one run only. Not thread safe; 64 B minimum plus 32 B of side metadata per block; chunks are freed only on Reset().

## Caveats and trade-offs

C# library, not C++. Tiny benchmark: 2048 allocations from 7 fixed sizes (64, 96, 150, 200, 400, 1024, 4096) then frees. The 'Libc' baseline calls NativeMemory.AlignedAlloc(size, 64), which is _aligned_malloc on Windows MSVC CRT, not plain malloc. The TLSF side returns TlsfAllocationToken offsets into 64 KiB chunks from a managed chunk allocator (an offset/sub-allocator design), so the two sides do not do identical work. Windows only, single run.

Managed .NET allocator managing a caller-provided region (not a drop-in malloc); single-threaded; the libc call goes through interop.

## Maintenance

Small, BSD-2-Clause and published on NuGet, with 38 commits, one open feature request and a last commit on 2026-02-23 ('Fix benchmarks'); usable as is, but outside the catalog's C++ focus.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README shows a BenchmarkDotNet table (Tlsf 82.27 us vs Libc 105.34 us, ratio 0.78) with .NET SDK 8.0.300 / RyuJIT DefaultJob and AMD Ryzen 9 7950X stated; benchmark code is public at src/XenoAtom.Allocators.Bench/BenchAllocator.cs.
- **Verifier notes:** Opened BenchAllocator.cs: baseline is aligned CRT alloc, not malloc; that caveat is worth carrying. Metadata checked on github.com: 55 stars, BSD-2-Clause, last commit 2026-02-23 ('Fix benchmarks'). Language C# is outside the C++ focus.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/XenoAtom/XenoAtom.Allocators>
  - <https://github.com/XenoAtom/XenoAtom.Allocators/commits>
  - <https://raw.githubusercontent.com/XenoAtom/XenoAtom.Allocators/HEAD/readme.md>
  - <https://raw.githubusercontent.com/XenoAtom/XenoAtom.Allocators/HEAD/src/XenoAtom.Allocators.Bench/BenchAllocator.cs>
- **Sources the enricher read:**
  - <https://github.com/XenoAtom/XenoAtom.Allocators>
  - <https://github.com/XenoAtom/XenoAtom.Allocators/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/XenoAtom/XenoAtom.Allocators/HEAD/readme.md>
  - <https://raw.githubusercontent.com/XenoAtom/XenoAtom.Allocators/HEAD/doc/readme.md>
  - <https://raw.githubusercontent.com/XenoAtom/XenoAtom.Allocators/HEAD/src/XenoAtom.Allocators.Bench/BenchAllocator.cs>
  - <https://raw.githubusercontent.com/XenoAtom/XenoAtom.Allocators/HEAD/src/XenoAtom.Allocators/TlsfAllocator.cs>
  - <https://raw.githubusercontent.com/XenoAtom/XenoAtom.Allocators/HEAD/src/XenoAtom.Allocators/XenoAtom.Allocators.csproj>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/xenoatom/xenoatom.allocators`) · [data/wave11/enrich/raw/github_com_xenoatom_xenoatom_allocators.json](../../../data/wave11/enrich/raw/github_com_xenoatom_xenoatom_allocators.json) (enrichment confidence 0.8)

</details>
