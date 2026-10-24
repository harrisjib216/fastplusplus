# Allocators and garbage collectors

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md)</sub>

**What these beat:** malloc, jemalloc, mimalloc, Boehm GC  
**32 entries:** 4 tier A · 4 tier B · 21 tier C · 3 tier D · 27 copyable, 5 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**SGCL**](pebal-sgcl.md) | Header-only C++20 concurrent garbage collector whose allocation path beats malloc-backed unique_ptr/shared_ptr for small objects on macOS. | **A** | C++ | Apache-2.0 | 🟢 active |
| 2 | [**XenoAtom.Allocators (TLSF)**](xenoatom-xenoatom-allocators.md) | TLSF sub-allocator for .NET 8 over caller-supplied chunks; about 22% faster than CRT aligned malloc/free in its own micro-benchmark. | **A** | C# | BSD-2-Clause | 🟢 active |
| 3 | [**fast-alloc**](notkeira-fast-alloc.md) | Small C++20 pool, stack and free-list arenas for game code; beats new/delete and malloc only on fixed-size or frame-scoped patterns. | **A** | C++ | MIT | 🟢 active |
| 4 | [**Kaname-Shiki (MemoryAllocator.KanameShiki)**](emuradaisuke-memoryallocator-kanameshiki.md) | Small (2600-line) thread-caching general-purpose allocator for 64-bit Windows/Linux that beats the MSVC CRT malloc on its own alloc/free stress tests. | **A** | C++ | MIT | 🔴 abandoned |
| 5 | [**Mesh**](plasma-umass-mesh.md) | Drop-in malloc that compacts fragmented C/C++ heaps by page remapping; 16% less memory than Firefox's jemalloc, 39% on Redis. | **B** | C++ | Apache-2.0 | 🟢 active |
| 6 | [**LLFree**](luhsra-llfree-c.md) | Lock- and log-free page-frame allocator in C; up to 88% (4 KiB) and 98% (2 MiB) lower concurrent allocation time than Linux's buddy allocator. | **B** | C | MIT | 🟢 active |
| 7 | [**Ralloc**](urcs-sync-ralloc.md) | Lock-free recoverable persistent-memory malloc (LRMalloc-based); about 10x faster than PMDK libpmemobj and Makalu on allocator microbenchmarks. | **B** | C++ | MIT | 🔴 abandoned |
| 8 | [**Exgen-Malloc**](paper-exgen-malloc.md) | Single-threaded malloc built by stripping mimalloc's thread machinery; paper reports 1.03-1.05x over mimalloc and 1.17-1.19x over dlmalloc on SPEC CPU2017. | **B** | C | no license (study only) | ⚪ unknown |
| 9 | [**Boehm-Demers-Weiser GC (bdwgc)**](bdwgc-bdwgc.md) | Conservative mark-sweep garbage collector for C and C++; first-party GCBench runs beat glibc malloc/free on small-object allocation. | **C** | C | Boehm-GC | 🟢 active |
| 10 | [**Talc**](sfbdragon-talc.md) | Rust no_std and WebAssembly heap allocator; about 2x DLmalloc's throughput on wasm at under a third of its code size. | **C** | Rust | MIT | 🟢 active |
| 11 | [**IsoAlloc**](struct-isoalloc.md) | Security-hardened C11 malloc replacement (size-isolated zones, guard pages, canaries) that runs near glibc ptmalloc speed. | **C** | C | Apache-2.0 | 🟢 active |
| 12 | [**rlsf**](yvt-rlsf.md) | Rust no_std TLSF allocator with constant-time alloc/free; lower latency and far smaller code than dlmalloc on microcontrollers and wasm. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 13 | [**ChunkSizedAllocator&lt;N,Sz...&gt; chunked fixed-size-class pool…**](paper-book-c-plus-plus-memory-management-chunksizedallocator.md) | Teaching-grade fixed size-class pool (one malloc'd chunk per power-of-two class) used through placement new; about 1.1x over new/delete in the book. | **C** | C++ | MIT | 🟢 active |
| 14 | [**SizeBasedArena&lt;T,N&gt; bump arena (Orc Tribe), Packt C++…**](paper-book-c-plus-plus-memory-management-sizebasedarena.md) | Per-class bump arena behind class-specific operator new/delete; book run shows about 1.3x faster construction than new/delete. | **C** | C++ | MIT | 🟢 active |
| 15 | [**Spaces**](xtellect-spaces.md) | Single-file C malloc replacement for Linux x86-64 with destroyable region heaps; README ranks it ahead of jemalloc on several mimalloc-bench workloads. | **C** | C | MIT | 🟢 active |
| 16 | [**FastAlloc**](komal-ai417-fastalloc.md) | Thread-caching slab allocator (C++17) that beats glibc malloc on small mixed-size alloc/free pairs and returns memory aggressively. | **C** | C++ | MIT | 🟢 active |
| 17 | [**rusty_alloc**](remade-with-rust-rusty-alloc.md) | Pure-Rust rebuild of mimalloc's design; slightly fewer instructions than mimalloc, jemalloc and glibc malloc under callgrind. | **C** | Rust | MIT | 🟢 active |
| 18 | [**ArenaAllocator (privateMwb)**](privatemwb-arenaallocator.md) | Header-only C++20 fixed-capacity bump arena with frame rollback; about 1.2-1.8x faster per allocate() than std::pmr::monotonic_buffer_resource. | **C** | C++ | MIT | 🟢 active |
| 19 | [**Bloodmoon001/memory-allocator**](bloodmoon001-memory-allocator.md) | Header-only C++17 fixed-capacity, single-type pool with intrusive free list; about 10x faster than MSVC malloc/free on alloc-free pairs. | **C** | C++ | MIT | 🟢 active |
| 20 | [**custom-memory-allocator (atul-singh-as)**](atul-singh-as-custom-memory-allocator.md) | Educational C++20 fixed-size pool and first-fit free-list allocators; the pool beats macOS malloc/free on bulk 16 B allocation. | **C** | C++ | MIT | 🟢 active |
| 21 | [**v8malloc**](iqbqioza-v8malloc.md) | Early-stage Linux malloc replacement (LD_PRELOAD) claiming parity or small wins over glibc, tcmalloc, jemalloc and mimalloc on microbenchmarks. | **C** | C | Apache-2.0 | 🟢 active |
| 22 | [**jdz_allocator**](joadnacer-jdz-allocator.md) | rpmalloc-style span allocator for Zig; claims parity with the rpmalloc Zig port and lower memory, no shown win over malloc. | **C** | Zig | MIT | 🟡 stale |
| 23 | [**micromalloc**](thermadiag-micromalloc.md) | Low-overhead general-purpose C/C++ malloc that usually beats glibc malloc on speed while using about as little memory. | **C** | C++ | MIT | 🟡 stale |
| 24 | [**elfmalloc (allocators-rs)**](ezrosent-allocators-rs.md) | Rust research malloc (elfmalloc) with a C API, faster than glibc ptmalloc2 and often 2017 jemalloc on multithreaded benchmarks. | **C** | Rust | Apache-2.0 OR MIT | 🔴 abandoned |
| 25 | [**halloc**](canonizer-halloc.md) | Kepler-era CUDA device-side slab allocator (hamalloc/hafree) for small blocks, built to beat in-kernel CUDA malloc on throughput. | **C** | C++ | GPL-2.0 or OpenIB BSD… | 🔴 abandoned |
| 26 | [**obstack (cleeus)**](cleeus-obstack.md) | Pointer-bump C++ object-stack arena with destructor tracking; about 100x faster than glibc malloc in its own 2012 benchmark. | **C** | C++ | BSL-1.0 | 🔴 abandoned |
| 27 | [**LWMalloc**](taehyeon-masu-lwmalloc.md) | 618-line single-file C malloc for embedded Linux, injected via LD_PRELOAD; paper claims up to 53% faster than glibc ptmalloc. | **C** | C | no license (study only) | 🟢 active |
| 28 | [**mem++ (memplusplus)**](m4drat-memplusplus.md) | Experimental single-threaded C++ arena allocator with GC smart pointers and heap compaction; beats jemalloc in its own charts, not glibc malloc. | **C** | C++ | no license (study only) | 🟡 stale |
| 29 | [**SpeedMalloc**](paper-speedmalloc.md) | Hardware proposal: a small in-order support core runs malloc/free for all cores; simulated 1.15x over mimalloc and 1.75x over jemalloc at 16 threads. | **C** | other | no license (study only) | ⚪ unknown |
| 30 | [**mtrebi/memory-allocators (free list allocator; linear…**](mtrebi-memory-allocators.md) | Teaching-grade C++ linear, stack, pool and first-fit free-list allocators; README claims the free list runs about 3x faster than malloc. | **D** | C++ | MIT | 🟢 active |
| 31 | [**libpas**](webkit-webkit.md) | Apple's libpas: isoheap-capable malloc toolkit behind WebKit's bmalloc, faster and leaner than the bmalloc it replaced. | **D** | C | BSD-2-Clause (per the Apple… | 🟢 active |
| 32 | [**fc_malloc**](bytemaster-fc-malloc.md) | 2013 proof-of-concept thread-caching allocator with a dedicated free-recycling thread; README claims about 2x faster than glibc and jemalloc. | **D** | C++ | no license (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
