# msgq (comma.ai)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> comma.ai's shared-memory ring-buffer pub/sub for one machine, callable from Python and C++; about 3.2x pyzmq IPC on Python-driven ping-pong.

| | |
|---|---|
| **Beats** | ZeroMQ |
| **Claimed result** | 362.13k msgs/sec (msgq) vs 113.97k msgs/sec (pyzmq ZeroMQ IPC), 1 KiB cross-process ping-pong on x86 Linux - about 3.2x higher (derived from page data; the figures are read from the bar chart embedded in the README) |
| **Workload** | 1 KiB cross-process ping-pong on x86 Linux. Messages/sec counts both requests and replies and is the median of 5 randomized repeats, each at least 2 s and 1000 round trips. The comparison covers msgq, pyzmq IPC (XPUB/SUB over ipc://), multiprocessing.Pipe, Eclipse Zenoh (unix socket) and LCM UDP, all driven from Python by the repo's msgq/examples/benchmark.py. |
| **Metric** | throughput |
| **Hardware** | x86 Linux (exact CPU model not stated) |
| **Adoption** | 256 stars; used in production in comma.ai's openpilot |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/commaai/msgq) · [benchmark](https://github.com/commaai/msgq/blob/master/README.md) |

## Verdict

The README's chart comes from msgq/examples/benchmark.py: two Python processes play 1 KiB ping-pong on an unspecified x86 Linux machine, taking the median of 5 randomized repeats. msgq reached 362.13k msgs/s against 113.97k for pyzmq XPUB/SUB over ipc:// (about 3.2x), with multiprocessing.Pipe at 231.66k, LCM UDP at 173.68k and Zenoh over a Unix socket at 86.03k. Counting both directions, that is about 181k round trips/s, or roughly 5.5 us per round trip including Python overhead. This is not native libzmq, no CPU, kernel or compiler is given (the SCons build uses -O2), and the 64 B and 64 KiB runs are not published.

## Use it when

- Same-host sensor or telemetry pipelines where Python and C/C++ processes publish and subscribe to the same topics (openpilot's use case).
- Latest-value streams where dropping stale messages is acceptable or wanted; conflate=True returns only the newest message.
- Small to medium messages (64 B to 64 KiB are exercised by the benchmark) at high rates, where per-message syscalls and kernel copies (Unix sockets, pipes) cost too much CPU.
- Linux on x86-64 or aarch64 with /dev/shm, using CPython 3.11 to 3.14 (prebuilt manylinux, musllinux and macOS wheels on PyPI as msgq-ipc).
- Tests that need to step a pub/sub system deterministically, via the bundled fake backend (CEREAL_FAKE).

## Skip it when

- Any cross-host messaging: there is no network transport, and the subscriber address must be 127.0.0.1 (enforced by assert).
- Workloads that need reliable delivery, backpressure, acknowledgements or persistence: a slow subscriber is silently reset to the write head and loses messages.
- Topics with several producers, or request/reply and fan-in patterns: a new publisher takes over the endpoint and the old one's send fails with MultiplePublishersError.
- More than 25 subscribers on one topic, or messages larger than a third of the segment (about 349 KB with the default 1 MiB segment) unless segment_size is raised.
- Latency-sensitive work on macOS, which has no tkill and polls every 10 ms instead; processes that already use SIGUSR2; containers without a shared /dev/shm.

## How it is fast

Each endpoint is a file in /dev/shm that every process mmaps. It holds a header of 64-bit atomics, each packing a 32-bit wrap-cycle counter with a 32-bit offset, one for the writer and one per reader, followed by a single-producer, multi-consumer byte ring of 8-byte-size-prefixed records. A send is a memcpy into the ring plus an atomic write-pointer update, then a tkill(SIGUSR2) to each reader thread to interrupt its nanosleep-based poll. A receive is a memcpy out, bracketed by checks of a per-reader validity flag in the style of a seqlock optimistic read, so there are no locks and no kernel socket copies. The writer never waits for readers: readers it laps are invalidated and reset, so there is no backpressure work on the hot path.

## Compared with alternatives

Pick msgq over Monocoque (ZeroMQ-style REQ/REP over IPC and TCP) or TCPSHM (point-to-point TCP/SHM round trips) when you need one-to-many same-host pub/sub that Python and C++ can both use, and lossy latest-value delivery is fine. Choose those siblings or Zenoh when you need request/reply, reliable delivery or a network hop.

## Integration

| | |
|---|---|
| **Form** | module (pip wheel msgq-ipc with Cython bindings); static libs libmsgq.a / libvisionipc.a via SCons for C++ |
| **Dependencies** | none at runtime (librt on Linux); build needs SCons, Cython&gt;=3.1 and setuptools&gt;=77 |
| **Minimum toolchain** | C++17 (-std=c++1z), C gnu11; Python &gt;= 3.11 |
| **Platforms** | Linux x86-64 and aarch64 (CI and wheels); macOS x86-64/arm64 wheels, where wake-ups fall back to 10 ms polling |
| **Thread safety** | Not documented. The code has no locks. A random per-publisher UID enforces a single writer and reader slots are claimed by CAS, but each socket object holds unsynchronized state, so sharing one socket across threads is at your own risk. |
| **Drop-in for the baseline** | no |

## Gotchas

- Despite folklore calling it zero-copy, the README says it copies on both send and receive. Large frames go through VisionIPC instead.
- Hard limits are enforced with assert(), and the SCons build does not define NDEBUG. A message over segment/3 aborts the publisher, and an empty message trips the receiver's size&gt;0 assert. A 26th subscriber evicts every reader on the endpoint, which then re-registers (open issue #702 calls the fixed cap a footgun).
- Creating a queue installs a SIGUSR2 handler, and every send signals each subscriber's thread. The signal targets the thread that created the subscriber, so receiving on another thread waits out the poll timeout (100 ms slices when blocking). A rare lost wake-up in poll is acknowledged in closed issue #208.
- Creating a publisher resets the endpoint's reader table, so create publishers before subscribers (the benchmark barriers on this). Queue files in /dev/shm are never unlinked. OPENPILOT_PREFIX namespaces them.

## Known shortcomings

- The \~3.2x vs pyzmq is a Python ping-pong test (latency-bound, not streaming), shared-memory IPC on one host.
- Same host only (no network); lossy: a slow subscriber is silently reset and there is no backpressure; one publisher per topic and the 26th subscriber evicts all readers (#702). Live assert()s abort the process on messages over segment/3 (\~349 KB default) or empty messages. SIGUSR2 is sent per message to the subscriber's creator thread, so a recv on another thread waits out the poll timeout; lost-wakeup race (#208). macOS polls every 10 ms; /dev/shm files are never unlinked; copies on send and recv (not zero-copy). CPU not given; 64 B/64 KiB runs unpublished.

## Caveats and trade-offs

The README states only 'x86 Linux': no CPU model, kernel, compiler or flags. Both sides are driven through Python bindings (msgq's own binding vs pyzmq), not native C++ ZeroMQ. The test is synchronous ping-pong, so the rate is set by round-trip latency rather than streaming throughput. msgq uses a shared-memory ring buffer, while pyzmq goes over ipc:// Unix-domain sockets. The script also measures 64 B and 64 KiB messages, but only the 1 KiB results are plotted and published.

Single-host IPC only (no network transport like real ZeroMQ/Kafka); ring-buffer based pub/sub, not a durable/distributed log; C/C++ core with Python bindings, so Python overhead is included in the benchmark on both sides.

## Maintenance

Actively maintained: v1.0 went to PyPI as msgq-ipc in September 2026, the last commit was 2026-09-09, and it runs in production in openpilot as a git submodule. It is MIT-licensed, and its roughly 500-line C++ core is easy to vendor, but the packaging depends on SCons and Cython.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's embedded chart (1 KiB cross-process ping-pong on x86 Linux) shows msgq at 362.13k and pyzmq at 113.97k messages/sec, alongside zenoh 86.03k, LCM 173.68k and multiprocessing.Pipe 231.66k. The benchmark code (msgq/examples/benchmark.py) is public, but no CPU model, compiler or flags are given, so it is first-party C.
- **Verifier notes:** The numbers match the README chart exactly. The record's benchmark path 'benchmarks/examples/benchmark.py' was wrong and is corrected to msgq/examples/benchmark.py. last_commit uses the committer date 2026-09-09 (author date 2026-09-07). The openpilot usage is confirmed: its .gitmodules includes commaai/msgq. Metadata: MIT, 256 stars, active, not a fork or archived.
- **Fields the verifier corrected:** `last_commit`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/commaai/msgq>
  - <https://github.com/commaai/msgq/blob/master/README.md>
  - <https://github.com/user-attachments/assets/79bb91cf-c9ad-4fb4-97d9-33359a083f0f>
  - <https://github.com/commaai/msgq/blob/master/msgq/examples/benchmark.py>
  - <https://github.com/commaai/openpilot/blob/master/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/commaai/msgq>
  - <https://github.com/commaai/msgq/blob/master/README.md>
  - <https://github.com/user-attachments/assets/79bb91cf-c9ad-4fb4-97d9-33359a083f0f>
  - <https://github.com/commaai/msgq/blob/master/msgq/examples/benchmark.py>
  - <https://github.com/commaai/msgq/blob/master/msgq/msgq.h>
  - <https://github.com/commaai/msgq/blob/master/msgq/msgq.cc>
  - <https://github.com/commaai/msgq/blob/master/msgq/ipc.h>
  - <https://github.com/commaai/msgq/blob/master/msgq/ipc.cc>
  - <https://github.com/commaai/msgq/blob/master/msgq/impl_msgq.h>
  - <https://github.com/commaai/msgq/blob/master/msgq/impl_msgq.cc>
  - <https://github.com/commaai/msgq/blob/master/msgq/event.h>
  - <https://github.com/commaai/msgq/blob/master/msgq/event.cc>
  - <https://github.com/commaai/msgq/blob/master/msgq/ipc_pyx.pyx>
  - <https://github.com/commaai/msgq/blob/master/msgq/__init__.py>
  - <https://github.com/commaai/msgq/blob/master/msgq/tests/test_messaging.py>
  - <https://github.com/commaai/msgq/blob/master/msgq/msgq_tests.cc>
  - <https://github.com/commaai/msgq/blob/master/SConstruct>
  - <https://github.com/commaai/msgq/blob/master/SConscript>
  - <https://github.com/commaai/msgq/blob/master/pyproject.toml>
  - <https://github.com/commaai/msgq/blob/master/setup.py>
  - <https://github.com/commaai/msgq/blob/master/setup.sh>
  - <https://github.com/commaai/msgq/blob/master/.github/workflows/tests.yml>
  - <https://github.com/commaai/msgq/blob/master/.github/workflows/wheels.yml>
  - <https://github.com/commaai/msgq/issues/702>
  - <https://github.com/commaai/msgq/issues/640>
  - <https://github.com/commaai/msgq/issues/365>
  - <https://github.com/commaai/msgq/issues/208>
  - <https://github.com/commaai/msgq/issues/186>
  - <https://github.com/commaai/msgq/pull/681>
  - <https://github.com/commaai/msgq/commits/master>
  - <https://github.com/commaai/msgq/releases>
  - <https://github.com/commaai/openpilot/blob/master/.gitmodules>
  - <https://pypi.org/pypi/msgq-ipc/json>
  - <https://hn.algolia.com/api/v1/search?query=commaai%20msgq&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=msgq%20openpilot&tags=comment>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/commaai/msgq`) · [data/wave6/enrich/raw/github_com_commaai_msgq.json](../../../data/wave6/enrich/raw/github_com_commaai_msgq.json) (enrichment confidence 0.8)

</details>
