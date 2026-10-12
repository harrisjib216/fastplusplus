# Cornflakes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `Rust` · `no license` · 🔴 abandoned

> Rust research serialization library and kernel-bypass UDP stack that sends large fields zero-copy via NIC scatter-gather, beating Protobuf/FlatBuffers/Cap'n Proto.

| | |
|---|---|
| **Beats** | Protobuf, FlatBuffers and Cap'n Proto via the pure-Rust crates protobuf 3.0.3 (rust-protobuf), flatbuffers 2.1.2 and capnp 0.13.6 (cf-kv/Cargo.toml); Redis handwritten serialization for Table 3 |
| **Claimed result** | CDN image trace (Table 2), in thousands of objects/s: Cornflakes 366.5 vs Cap'n Proto 161.0, FlatBuffers 181.2 and Protobuf 186.1; the paper says 97-128% higher. Twitter cache trace (Fig. 7): 15.4-45.9% higher throughput than the three baselines, at a p99 of 52 us for Cornflakes vs 53 us (FlatBuffers, Protobuf) and 61 us (Cap'n Proto). Google bytes-size trace (Table 1), in thousands of req/s: no win for small values. Cornflakes has 844.7 vs Protobuf 852.5 (1 value) and 727.2 vs 741.9 (1-4 values). It leads only at 1-8 values (584.5 vs 583.8) and 1-16 values (441.2 vs 412.0). Redis (Table 3) is measured against Redis's own handwritten serialization, not Protobuf, FlatBuffers or Cap'n Proto: 15-40.1% higher throughput (get 23.37 vs 18.49 Gbps, mget-2 14.12 vs 12.27, lrange-2 15.07 vs 10.75). |
| **Workload** | Custom Rust key-value store and echo server serving a CDN image-object trace (1M objects, 1KB-116MB, mean \~20KB), a Twitter cache trace, and Redis GET/MGET/LRANGE commands, over kernel-bypass 100Gb NICs |
| **Metric** | throughput |
| **Hardware** | 2x 24-core AMD EPYC 7402P 2.80GHz servers (CloudLab c6525-100g), Dual-port Mellanox ConnectX-5Ex 100Gb NICs, jumbo frames MTU 9000, Ubuntu 20.04 / Linux 5.04 |
| **Compiler and flags** | rustc version not pinned: install/install-rust.sh installs 1.70.0 and then runs `rustup default stable`. Cargo.toml [profile.release] sets opt-level=3, lto="fat", codegen-units=1, panic="abort"; the Makefile builds with --release unless DEBUG=y. The paper states no compiler. |
| **Adoption** | 51 stars; peer-reviewed at SOSP 2023 (ACM DOI 10.1145/3600006.3613137) |
| **Last commit** | 2023-07-27 |
| **Links** | [repository](https://github.com/deeptir18/cornflakes) · [benchmark](https://people.eecs.berkeley.edu/~matei/papers/2023/sosp_cornflakes.pdf) |

## Verdict

The SOSP 2023 paper runs a single-core Rust KV server on CloudLab c6525-100g machines (2x EPYC 7402P, ConnectX-5Ex 100 Gb, MTU 9000), with every system on the Cornflakes UDP stack and the pure-Rust protobuf 3.0.3, flatbuffers 2.1.2 and capnp 0.13.6 crates as baselines; the rustc version is not stated. Cornflakes served 366.5k vs 161.0-186.1k objects/s on the CDN image trace, delivered 15.4-45.9% more throughput on the Twitter trace (p99 about 52-61 us) and roughly tied on Google's small-field trace; in Redis, get/mget/lrange gained 15-40.1% over Redis's own handwritten serialization.

## Use it when

- Microsecond-scale datacenter services such as caches and KV stores that already run on kernel bypass with Mellanox ConnectX-5/6 or Intel E810 NICs, where serialization copies are a large share of CPU time per request.
- Responses built from values of 512 B or more that already sit in pinned memory, e.g. a store that returns stored blobs. On the paper's CDN image trace (objects of 1 KB and up) it served 97-128% more objects/s than the three baselines.
- Workloads that mix small and large values, like the Twitter cache trace (about 32% of requests are 512 B or more), where the hybrid copy/zero-copy path beat pure scatter-gather by 2.3-3.9% and beat the copy-based libraries by 15.4-45.9%.
- Applications that never modify data in place while it is being sent, such as Redis-style stores, versioned stores, or code that updates by allocating and swapping pointers.
- As a reference design and threshold-calibration method (paper Section 5) when adding zero-copy serialization to your own kernel-bypass stack.

## Skip it when

- Small-field workloads. On Google's field-size distribution (94.9% of fields are 512 B or less) it ties or slightly trails Protobuf (844.7 vs 852.5 k req/s at 1 value) and wins only at 1-8 and 1-16 values per list.
- Standard Linux sockets. The linux-datapath returns usize::MAX as its copy threshold (always copies), and many of its functions are unimplemented!().
- Messages larger than one jumbo frame. The prototype has no segmentation: the CDN benchmark split objects into sub-objects that fit a jumbo frame, and the copy path carries a 'doesn't work if buffer is &gt; than an MTU' TODO.
- Production or multicore use, or any need for Protobuf wire compatibility, proto2 required fields, or recursive pointer-based types (the author confirms in issue #7 that trees with pointers are not supported). The paper evaluates a single-core server and leaves multicore to future work.
- Any project that needs a license: the repo has no LICENSE file.

## How it is fast

Protobuf, FlatBuffers and Cap'n Proto copy each bytes/string field into a contiguous buffer and then again into DMA memory; Cornflakes instead posts each pinned-memory field of 512 B or more as its own NIC scatter-gather entry (zero-copy transmit), and a per-buffer reference count keeps that memory alive until the DMA completes. A per-field size threshold, checked when the field's smart pointer (CFBytes/CFPtr) is constructed, chooses copy or zero-copy: smaller fields go into an arena-backed copy buffer, because below about 512 B the reference-count cache miss costs more than the memcpy. Serialize-and-send writes the packet header, the object header and the copied data into one entry and posts the zero-copy entries directly onto the NIC ring, with no intermediate scatter-gather array (a 7.7-17.4% throughput gain in the paper). All framing (a field bitmap plus u32 size/offset forward pointers) is at the front of the object, so each zero-copy field needs only one extra scatter-gather entry.

## Compared with alternatives

Pick it over rkyv, or over FlatBuffers-family formats such as Karmem and Lite³, only when your bottleneck is the transmit-path memcpy on a kernel-bypass NIC and your fields are 512 B or larger. Those siblings speed up CPU encode/decode over any transport, but Cornflakes's gain comes from NIC scatter-gather and disappears for small fields or on normal sockets.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Cargo workspace crates (cornflakes-codegen, cornflakes-libos, cornflakes-utils, a datapath crate) used as path dependencies with build.rs code generation; git forks of bumpalo (and optionally demikernel); protobuf-parser, rdma-core and DPDK git submodules; Mellanox OFED 5.6-2.0.9.0 or Intel ice drivers (Intel also needs igb_uio binding); hugepages. protoc/flatc/capnp are needed only to build the baselines. |
| **Minimum toolchain** | Rust 2021 edition. install-rust.sh installs 1.70.0 and then switches the default to stable, so the rustc version is not pinned. Only Ubuntu 20.04 is tested. |
| **Platforms** | x86-64 Linux (Ubuntu 20.04) with Mellanox ConnectX-5/ConnectX-6 (mlx5) or Intel E810 (ice) NICs; DPDK support is partial; the paper's runs use jumbo frames (MTU 9000) |
| **Thread safety** | Not documented. The datapath creates one connection per thread from per-thread contexts. The paper's servers run on a single core, and multicore is left to future work. Nothing prevents the application from modifying a buffer that the NIC is still sending. |
| **Drop-in for the baseline** | partial — it reuses Protobuf's proto3 schema language and a Protobuf-like getter/setter API, but it has its own wire format, networking stack and pinned-buffer allocator, so neither application code nor wire data carry over unchanged |

## Gotchas

- The kv app's --copy_threshold CLI default and the mlx5 datapath default are both 256 B, not the paper's 512 B. The experiment configs pass 512 explicitly (cornflakes-dynamic-512). The paper recommends re-measuring the threshold on your own NIC and CPU.
- Zero-copy applies only to data inside the stack's registered pinned memory. For any other pointer, recover_metadata returns None and the field is copied without any warning.
- Copied entries come before zero-copy entries on the wire. As a result, peers configured with different thresholds can serialize repeated elements in different orders.
- Issue #1, open since 2021: the code generator emits code with lifetime errors for messages that contain only int32 fields.

## Known shortcomings

- Research prototype, abandoned since 2023-07. No win on small objects (paper Table 1). Baselines are the pure-Rust protobuf/flatbuffers/capnp crates, not the C++ libraries, and the Redis gains are against Redis's own handwritten serialization.
- Needs a kernel-bypass NIC datapath (mlx5); the Linux-socket datapath always copies. Single-core, single-jumbo-frame prototype with no segmentation or write protection for buffers in flight. Code defaults use a 256 B zero-copy threshold, while the paper's numbers use 512 B. C bindings exist but use from C++ is undocumented, and generated code fails for int32-only messages (issue #1, open since 2021).

## Caveats and trade-offs

The baselines are pure-Rust implementations (rust-protobuf 3.0.3, the flatbuffers 2.1.2 Rust runtime, capnproto-rust 0.13.6), not wrappers around the canonical C++ libraries. The C++ installs in install/install-libraries.sh are used only for the protoc/flatc/capnp code generators. All systems run over Cornflakes's own kernel-bypass UDP stack, with a per-library network API. There is no gain on small-object workloads (Table 1: within 98% of Protobuf at 1 and 1-4 values). The Redis gains are against Redis's handwritten serialization. The rustc version is not pinned. The repo has no LICENSE file. The default branch's last commit is 2023-07-27; a non-default 'timetrace' branch has a commit from 2024-01-19.

Rust-primary implementation; README states C-bindings to the serialization code exist but this was not independently verified for C++ usability; requires DPDK or Mellanox/Intel ICE NIC drivers and hugepages (kernel-bypass networking), so it is not a drop-in library without specialized datacenter NIC hardware; zero-copy only helps once field/object sizes exceed the measured \~512-byte threshold — for small objects Cornflakes only ties the baselines, it does not beat them

## Maintenance

Abandoned research prototype: the main branch was last committed on 2023-07-27 (the timetrace branch on 2024-01-19), and there is no LICENSE file, so use it as a reference design to study, not as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed SOSP 2023 paper (DOI 10.1145/3600006.3613137). Tables 1-3 and Figure 7 compare Cornflakes with Protobuf, FlatBuffers and Cap'n Proto on stated hardware (EPYC 7402P, CloudLab c6525-100g, ConnectX-5Ex), and the code is public (cf-kv/, ds-echo/). The Cargo.toml release profile gives the flags, but the rustc version is not pinned: install/install-rust.sh installs 1.70.0 and then runs `rustup default stable`. The paper states no compiler, so it is not A, and B stands.
- **Verifier notes:** The paper's numbers are quoted correctly. The record's caveat that the Rust crates 'wrap each C/C++ library' was wrong: all three are pure-Rust runtimes, per cf-kv/Cargo.toml. The last commit on the default branch (main) is 2023-07-27, more than 3 years ago, so the status is abandoned; the 2024-01-19 date is from the timetrace branch. The license is null with no LICENSE file, so 'reference' is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://people.eecs.berkeley.edu/~matei/papers/2023/sosp_cornflakes.pdf>
  - <https://github.com/deeptir18/cornflakes>
  - <https://github.com/deeptir18/cornflakes/blob/main/README.md>
  - <https://github.com/deeptir18/cornflakes/blob/main/Cargo.toml>
  - <https://github.com/deeptir18/cornflakes/blob/main/Makefile>
  - <https://github.com/deeptir18/cornflakes/blob/main/install/install-rust.sh>
  - <https://github.com/deeptir18/cornflakes/blob/main/install/install-libraries.sh>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/Cargo.toml>
  - <https://github.com/deeptir18/cornflakes-scripts>
- **Sources the enricher read:**
  - <https://github.com/deeptir18/cornflakes>
  - <https://github.com/deeptir18/cornflakes/blob/main/README.md>
  - <https://github.com/deeptir18/cornflakes/blob/main/Cargo.toml>
  - <https://github.com/deeptir18/cornflakes/blob/main/.gitmodules>
  - <https://github.com/deeptir18/cornflakes/blob/main/install/install-rust.sh>
  - <https://github.com/deeptir18/cornflakes/blob/main/cornflakes-codegen/API.md>
  - <https://github.com/deeptir18/cornflakes/blob/main/cornflakes-codegen/Cargo.toml>
  - <https://github.com/deeptir18/cornflakes/blob/main/cornflakes-libos/Cargo.toml>
  - <https://github.com/deeptir18/cornflakes/blob/main/cornflakes-libos/src/dynamic_rcsga_hybrid_hdr.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cornflakes-libos/src/datapath.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cornflakes-libos/src/lib.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cornflakes-utils/src/lib.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/mlx5-datapath/src/datapath/connection.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/mlx5-datapath/mlx5-wrapper/inc/base/mempool.h>
  - <https://github.com/deeptir18/cornflakes/blob/main/linux-datapath/src/datapath/connection.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/echo-dynamic-sga-c/echo_dynamic_sga.h>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/Cargo.toml>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/build.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/src/lib.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/src/cdn.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/src/run_cdn.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/src/bin/cdn_mlx5.rs>
  - <https://github.com/deeptir18/cornflakes/blob/main/cf-kv/cdn.yaml>
  - <https://github.com/deeptir18/cornflakes/blob/main/experiments/yamls/loopingparams/cf-kv-cdn.yaml>
  - <https://github.com/deeptir18/cornflakes/blob/main/experiments/yamls/loopingparams/cf-kv-twitter.yaml>
  - <https://github.com/deeptir18/cornflakes/issues/1>
  - <https://github.com/deeptir18/cornflakes/issues/7>
  - <https://github.com/deeptir18/cornflakes/pulls?q=is%3Apr>
  - <https://github.com/deeptir18/cornflakes/commits/main>
  - <https://github.com/deeptir18/cornflakes-scripts>
  - <https://people.eecs.berkeley.edu/~matei/papers/2023/sosp_cornflakes.pdf>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/deeptir18/cornflakes`) · [data/wave4/enrich/raw/github_com_deeptir18_cornflakes.json](../../../data/wave4/enrich/raw/github_com_deeptir18_cornflakes.json) (enrichment confidence 0.82)

</details>
