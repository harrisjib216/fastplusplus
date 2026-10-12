# Mino

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-3.0` · 🟢 active

> C++20 shared-memory pub/sub framework passing slab handles over SPSC rings; beat Protobuf+ZeroMQ in author's six-process pipeline benchmark.

| | |
|---|---|
| **Beats** | ZeroMQ |
| **Claimed result** | (derived from page data) same-host 6-process network smoke: Mino TCP p50 0.855ms vs Protobuf+ZeroMQ p50 10.33ms (\~12x); pipeline small payload (256B): Mino SHM mean p50 1.815ms vs Protobuf+ZeroMQ mean p50 \~10.56ms (\~5.8x); pipeline large payload (1MiB): Mino SHM mean p50 13.72ms vs Protobuf+ZeroMQ mean p50 \~26.85ms (\~2x); medium payload (64KiB) latency also favored Mino SHM (mean p50 0.979ms vs ZeroMQ's \~1.97ms) though Fast DDS had slightly higher medium-payload throughput. |
| **Workload** | Six-stage automotive-style pipeline (Perception-&gt;Prediction-&gt;Planning-&gt;Control-&gt;Guardian-&gt;CANBus) exchanging 256B/64KiB/1MiB frames intra-host; Mino's zero-copy SHM/TCP transport was benchmarked head-to-head against a Protobuf+ZeroMQ pipeline (plus Fast DDS and Cyclone DDS) for one-way end-to-end latency and CANBus message rate, saturation mode, and separately a same-host 6-process 'mino_tcp' vs 'protobuf_zmq' network smoke test. |
| **Metric** | latency |
| **Hardware** | Debian 13 (trixie), 8 vCPU, 15.64 GiB RAM, x86_64 KVM guest (exact physical CPU model not disclosed) |
| **Compiler and flags** | bazel build --config=pipeline_comparison -c opt --jobs=4 (Bazel 7.4.1 via bazelisk 1.29.0; .bazelrc adds -std=c++20 -Wall -Wextra -Werror -fno-omit-frame-pointer globally). The host toolchain is not named for the pipeline build; the same report says Debian 13's g++-14 ran the host sanity tests. |
| **Adoption** | 2 stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/bkcarlos/Mino) · [benchmark](https://github.com/bkcarlos/Mino/blob/master/docs/benchmarks/kvm-2026-08-25/REPORT.md) |

## Verdict

The author ran a 2-round saturation test on an 8-vCPU Debian 13 KVM guest (CPU model undisclosed, bazel -c opt, C++20, compiler for this build not stated) with six processes and five hops, where every stage validates and copies the full payload. Mino SHM had mean p50 end-to-end latency of 1.8 ms vs 10.6 ms for Protobuf over ZeroMQ ipc:// PUSH/PULL at 256 B, 0.98 vs 1.97 ms at 64 KiB and 13.7 vs 26.9 ms at 1 MiB; a separate 50-message smoke run gave Mino loopback TCP 0.855 ms p50 vs 10.33 ms for ZeroMQ (which used ipc://, because all six roles shared one boot), and all percentiles include queueing delay.

## Use it when

- Linux x86-64, several processes on one host in a fixed pipeline (robotics or autonomous-driving stages, sensor fusion) where Protobuf+ZeroMQ encode/parse per hop dominates latency.
- Small, frequent messages (about 256 B): 5.8x lower saturated p50 than Protobuf+ZeroMQ on the KVM run. The author's earlier paced 100 Hz run on an i9-9900KS gave 19 us vs 586 us p50 end to end over five hops.
- Typed fixed-layout messages up to about 1 MiB where you want deterministic O(1) slab allocation and explicit crash recovery of leases, pins and allocation journals (SimpleNode::Recover(), a journal-backed Subscriber).
- Systems that need one C++ API and one IDL for same-host SHM and a cross-host TCP bridge, with optional TLS 1.3 mTLS or frame AEAD.
- Teams that already build with Bazel/Bzlmod and C++20 and control every process that attaches to the segment.

## Skip it when

- Anything other than Linux x86-64 in production. AArch64 is unqualified (cross-build/QEMU only), and macOS is only for compiling and non-persistent-SHM tests.
- When you need ZeroMQ's feature set: REQ/REP, ROUTER/DEALER, bindings for many languages, brokerless TCP across hosts as the primary path. Mino is C++-only pub/sub and work queues.
- Cross-host throughput. In the author's one-round two-host run, Mino TCP did 28.2k msg/s at 256 B vs Cyclone DDS's 51.5k. In the one-host six-process smoke, Mino TCP (0.855 ms p50) was only slightly ahead of Cyclone DDS (0.97 ms).
- Large payloads. The advantage shrinks to about 2x saturated (1.35x paced) at 1 MiB, and Fast DDS had higher 64 KiB throughput (3571 vs 2925 msg/s).
- Production-critical use today. The project is about 2 months old, has one author and no releases, every ADR is ACCEPTED but none VALIDATED or FROZEN, the hardware and clean-ref qualification gates are open, and September commits are still fixing CI race conditions.

## How it is fast

The control path and the data path are separate. A cache-line-aligned SPSC index ring keeps the producer and consumer cursors on separate cache lines and needs no CAS. It carries ShmHandle offsets into a central slab allocator that uses fixed-size classes and a sharded atomic bitmap, so allocate and free are O(1). Frames are generated with a fixed layout, so a same-host hop needs no Protobuf-style encode/parse and no socket syscall, and subscribers spin on the ring with yield instead of blocking in the kernel. In the benchmarked commit (c977bd1), each forwarding stage still copied the payload out and into a new slab, so the measured win comes from skipping serialization and socket I/O. True zero-copy forwarding (the 'exclusive hop', TakeExclusive -&gt; PublishLocal) landed later in a1b76c3, and docs/benchmarks has no end-to-end numbers for it.

## Compared with alternatives

Pick Mino over TCPSHM, the other ZeroMQ-beater here and a small point-to-point connection library with sub-microsecond SHM round trips, when you need topic-based multi-process pipelines with IDL-typed messages, MPSC or broadcast fan-out, crash recovery and one API that bridges to TCP across hosts. Pick Zenoh instead when you need a mature, multi-language, routed pub/sub rather than a young C++/Linux-only single-host pipeline.

## Integration

| | |
|---|---|
| **Form** | static lib (Bazel/Bzlmod targets built from source; no CMake, no releases) |
| **Dependencies** | OpenSSL 3.5.5 (source-built via BCR, production TLS), spdlog 1.15.3, toml++ 3.4.0; minoc codegen for IDL types; ZeroMQ, Protobuf, Fast DDS and Cyclone DDS are benchmark-only |
| **Minimum toolchain** | C++20, Bazel 7.4.1; CI uses GCC 12 and hermetic Clang/LLVM 18.1.8 |
| **Platforms** | Linux x86-64 only for production (ADR-0001); requires lock-free 64-bit atomics; AArch64 and macOS not qualified |
| **Thread safety** | SPSC channels require exactly one producer and one consumer (thread or process). MPSC and broadcast (up to 64 subscribers) topic modes exist. Per-object thread safety of Publisher/Subscriber is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Segments are sized as ring capacity x maximum payload. 1 MiB x 64 slots needs about 768 MiB, and the author's smoke run hit SIGBUS on a 64 MiB /dev/shm. Newer code fails closed via posix_fallocate, and the pipeline benchmark falls back to a file-backed mapping.
- Waiting burns CPU. Subscriber::Poll loops on std::this_thread::yield() and a kBlock publisher spins with a pause instruction. The design doc lists spin-then-park and futex wait strategies, but code search found no futex use in the source.
- Shared-memory layouts are still changing. SimpleNode manifest v3 and SharedHostDomain v3 (MINOSHD3) cannot open older segments, and writable secondary attach needs region layout v7, so upgrades mean recreating segments.
- No isolation among processes attached to the same RW region; the trust boundary is UID/GID/namespace. LGPL-3.0 plus Bazel static linking means you must ship relinkable objects if you distribute.

## Known shortcomings

- Serialization confound: the ZeroMQ baseline runs Protobuf over ipc:// at each hop while Mino SHM passes zero-copy handles with no codec. The 12x network figure is one 50-message smoke run; KVM with no CPU model and an unpinned compiler. Solo developer, 2 stars.
- The benchmark commit predates the zero-copy hop, so each stage still makes two payload copies; the win comes from skipping Protobuf and socket syscalls, not zero-copy. The 12x 'network' figure is loopback TCP vs ZeroMQ ipc:// at saturation (queue-dominated), where Cyclone DDS (0.97 ms) is close to Mino (0.855 ms). The gap shrinks with size (30x at 256 B to 1.35x at 1 MiB); Fast DDS wins 64 KiB throughput and Cyclone beats Mino TCP across two hosts for small messages.
- Polling busy-yields (burns a core); the futex/park wakeup in the design doc is not in the code. /dev/shm sizing can SIGBUS; the SHM layout ABI has changed incompatibly (v3 vs v7). Linux x86-64 only, Bazel-only, no releases, two months old; LGPL static linking carries a relink obligation.

## Caveats and trade-offs

The benchmark was designed, run and reported by the same solo author, so it is not independent. The physical CPU model is not disclosed, only a KVM guest with 8 vCPU and 15.64 GiB RAM, which falls short of full Tier A methodology. Saturation mode (publish-interval 0) means the percentiles include queuing delay, not idle one-hop latency. The baseline is Protobuf serialization over ZeroMQ ipc:// sockets at every hop, while Mino SHM transfers zero-copy handles to a generated typed frame and Mino TCP uses its own canonical wire codec. Part of the gap may therefore come from serialization and copying rather than transport alone. Only 2 rounds were run. The 12x network smoke figure comes from a single 50-message run, and buffering parameters (ZMQ HWM vs Mino SPSC capacity 64) are not semantically identical, as the README itself notes.

Solo-developer, \~2-month-old project (created 2026-07-26); README explicitly says 'not implemented yet' for parts of the typed Publisher&lt;T&gt; API; Linux-only for persistent SHM semantics (macOS is compile/non-persistent-SHM testing only); large-payload SHM run hit SIGBUS until /dev/shm was manually grown from 64MiB to 8GiB; LGPL-3.0 requires re-linkability for the Mino library itself.

## Maintenance

Actively developed by one author (152 commits since 2026-07-26, last on 2026-09-13), with no releases and 2 stars. It is LGPL-3.0 and builds only with Bazel, so treat it as a candidate to evaluate rather than a dependency to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** REPORT.md (in Chinese) runs the public benchmark code in benchmarks/pipeline_comparison/ (protobuf_zmq_pipeline.cc, mino_shm_pipeline.cc, mino_tcp_pipeline.cc, pipeline_comparison_runner.py, pipeline_network_runner.py) head-to-head against Protobuf+ZeroMQ, Fast DDS and Cyclone DDS. It gives only a KVM guest with 8 vCPU and no CPU model, and does not pin the compiler for the pipeline build, so it falls short of A. These are first-party numbers from 2 rounds, which makes them C.
- **Verifier notes:** All claimed figures check out against the page. Small p50 means: Mino 1814.5us vs ZMQ 10556us (5.8x). Medium: 979us vs 1973us (about 2x). Large: 13718us vs 26850.5us (about 1.96x). Network smoke: 855us vs 10.33ms (about 12x). Fast DDS medium throughput of 3571 msgs/s vs Mino's 2925 also matches. Metadata matches gh: LGPL-3.0, 2 stars, not a fork, not archived, last commit 2026-09-13, created 2026-07-26.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bkcarlos/Mino>
  - <https://github.com/bkcarlos/Mino/blob/master/docs/benchmarks/kvm-2026-08-25/REPORT.md>
  - <https://raw.githubusercontent.com/bkcarlos/Mino/master/docs/benchmarks/kvm-2026-08-25/REPORT.md>
  - <https://github.com/bkcarlos/Mino/tree/master/benchmarks/pipeline_comparison>
  - <https://github.com/bkcarlos/Mino/tree/master/docs/benchmarks>
  - <https://raw.githubusercontent.com/bkcarlos/Mino/master/.bazelrc>
  - <https://raw.githubusercontent.com/bkcarlos/Mino/master/benchmarks/pipeline_comparison/README.md>
  - <https://raw.githubusercontent.com/bkcarlos/Mino/master/benchmarks/pipeline_comparison/protobuf_zmq_pipeline.cc>
  - <https://raw.githubusercontent.com/bkcarlos/Mino/master/benchmarks/pipeline_comparison/mino_shm_pipeline.cc>
  - <https://raw.githubusercontent.com/bkcarlos/Mino/master/benchmarks/pipeline_comparison/mino_tcp_pipeline.cc>
- **Sources the enricher read:**
  - <https://github.com/bkcarlos/Mino>
  - <https://github.com/bkcarlos/Mino/blob/master/README.md>
  - <https://github.com/bkcarlos/Mino/blob/master/docs/benchmarks/kvm-2026-08-25/REPORT.md>
  - <https://github.com/bkcarlos/Mino/blob/master/docs/benchmarks/kvm-2026-08-25/UNIMPLEMENTED.md>
  - <https://github.com/bkcarlos/Mino/blob/master/docs/benchmarks/kvm-2026-08-25/REMAINING-TESTS.md>
  - <https://github.com/bkcarlos/Mino/blob/master/docs/optimization-status.md>
  - <https://github.com/bkcarlos/Mino/blob/master/docs/adr/0001-platform-baseline.md>
  - <https://github.com/bkcarlos/Mino/blob/master/examples/README.md>
  - <https://github.com/bkcarlos/Mino/blob/master/benchmarks/pipeline_comparison/README.md>
  - <https://github.com/bkcarlos/Mino/blob/master/benchmarks/pipeline_comparison/RESULTS_20260816.md>
  - <https://github.com/bkcarlos/Mino/blob/master/benchmarks/pipeline_comparison/RESULTS_TWO_HOST_20260816.md>
  - <https://github.com/bkcarlos/Mino/blob/master/benchmarks/pipeline_comparison/PERFORMANCE_FOLLOWUP.md>
  - <https://github.com/bkcarlos/Mino/blob/c977bd18ab67b17aa98406674ba482817e812beb/benchmarks/pipeline_comparison/protobuf_zmq_pipeline.cc>
  - <https://github.com/bkcarlos/Mino/blob/c977bd18ab67b17aa98406674ba482817e812beb/benchmarks/pipeline_comparison/mino_shm_pipeline.cc>
  - <https://github.com/bkcarlos/Mino/blob/master/benchmarks/pipeline_comparison/mino_shm_pipeline.cc>
  - <https://github.com/bkcarlos/Mino/blob/master/mino/shm/channel/spsc_channel.h>
  - <https://github.com/bkcarlos/Mino/blob/master/mino/shm/allocator/central_slab.h>
  - <https://github.com/bkcarlos/Mino/blob/master/mino/runtime/publisher.h>
  - <https://github.com/bkcarlos/Mino/blob/master/mino/runtime/subscriber.h>
  - <https://github.com/bkcarlos/Mino/blob/master/mino/runtime/simple_node.h>
  - <https://github.com/bkcarlos/Mino/blob/master/MODULE.bazel>
  - <https://github.com/bkcarlos/Mino/blob/master/.bazelrc>
  - <https://github.com/bkcarlos/Mino/blob/master/.bazelversion>
  - <https://github.com/bkcarlos/Mino/blob/master/.github/workflows/ci.yml>
  - <https://github.com/bkcarlos/Mino/commit/c977bd18ab67b17aa98406674ba482817e812beb>
  - <https://github.com/bkcarlos/Mino/commit/a1b76c38c7>
  - <https://github.com/bkcarlos/Mino/commit/1db52b15ee>
  - <https://github.com/bkcarlos/Mino/actions>
  - <https://github.com/search?q=repo%3Abkcarlos%2FMino+futex&type=code>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/bkcarlos/mino`) · [data/wave6/enrich/raw/github_com_bkcarlos_mino.json](../../../data/wave6/enrich/raw/github_com_bkcarlos_mino.json) (enrichment confidence 0.75)

</details>
