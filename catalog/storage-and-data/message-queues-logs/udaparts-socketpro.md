# SocketPro

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> C++ async RPC framework with a built-in persistent server queue; the vendor claims 3.6-54x RabbitMQ's enqueue/dequeue speed.

| | |
|---|---|
| **Beats** | RabbitMQ |
| **Claimed result** | Persistent-queue de-queue of 100,000 200-char messages cross-machine: RabbitMQ 44400 ms vs SocketPro 820 ms (\~54x, derived from page data; page says 'could be 50 times faster'); en-queue 6873 -&gt; 631 ms (\~11x, derived). Page says typically \~8x on de-queue and 8-10x on en-queue. Kafka: 'significantly faster' per README, no numbers. |
| **Workload** | Persistent message queue with auto-ack at the broker: en-queue and de-queue 100,000 messages of 200, 1024 and 10240 chars, same-machine and cross-machine. The RabbitMQ side uses modified rabbitmq-tutorials dotnet NewTask/Worker samples. Driver code is in-repo under samples/qperf (cperf, jperf, rabbitmq/Program.cs, server_queue, kafka_perf_test.txt); no Kafka results published |
| **Metric** | throughput |
| **Hardware** | Same-machine test: Acer AT3-605-UR22, Intel Core i7-4770 @3.40GHz, 16GB, Windows 8.1 Pro x64. Cross-machine: client Intel Core i7-3770 @3.40GHz 16GB (Windows 7 Pro x64); broker Intel Xeon E5-2630 v2 @2.60GHz, 4GB, Windows Server 2012R2 in VMware; 1 Gbps per figure (text says 100 Mbps) |
| **Adoption** | 28 stars |
| **Last commit** | 2023-02-16 |
| **Links** | [repository](https://github.com/udaparts/socketpro) · [benchmark](https://web.archive.org/web/20200210003353/http://www.udaparts.com/document/articles/fastsocketpro.htm) |

## Verdict

The vendor's 2016 study (PDF in the repo, HTML archived in 2020) enqueued and dequeued 100,000 persistent 200/1024/10240-char messages with the RabbitMQ .NET tutorial clients (RabbitMQ version, compiler and flags not stated). On one i7-4770 running Windows 8.1, SocketPro was 3.6-26x faster (200-char dequeue 14,129 -&gt; 544 ms). Across 1 Gbps to a 4 GB Xeon E5-2630 v2 Windows Server 2012R2 VMware broker it was 4.3-10.9x faster on enqueue and 9.8-54x on dequeue (200-char dequeue 44,400 -&gt; 820 ms), with RabbitMQ's consumer limited to prefetch 1 and per-message acks. A separate 2017 in-repo study against Kafka 0.10.1.1 (acks=1, Ubuntu 16.04, i7-4770, 7200-rpm HDD) reported SocketPro about 20-25% faster at writing medium and large messages, but Kafka about 20% faster on unbatched 4-32 B messages.

## Use it when

- You already build on SocketPro RPC (C++, .NET, Java, Python or Node.js) and want a work queue served from the same server process and port, without running a separate broker.
- Windows or x86-64 Linux hosts where producers stream many 200 B-1 KB messages and consumers drain in bulk, especially over higher-latency links where pipelining hides round trips. The vendor's largest gains are in this range.
- Producers must not lose messages during broker or network outages. An optional client-side queue file backs up every request and replays it after reconnect, and the tutorial shows this surviving repeated server kills.
- You are maintaining or re-measuring a legacy UDAParts deployment. The in-repo qperf drivers (C++, C#, Java, RabbitMQ C#) and the Kafka command lines let you rerun the comparisons.

## Skip it when

- You need AMQP, MQTT or the Kafka protocol, exchange or topic fan-out semantics, clustering or quorum queues, or ecosystem tooling such as a management UI. None of these exist, and the only way to interoperate is through SocketPro adapters.
- You need license-clear or auditable code. There is no LICENSE file, the client and server cores ship only as prebuilt .dll/.so files, and the changelog mentions an 'enterprise license'. Only the adapters and plugins such as the queue come as source.
- Tiny (4-32 B) messages without manual batching: the vendor's own 2017 Kafka study found Kafka about 20% faster at both writing and reading them. In that study, cross-machine dequeue of medium and large messages was roughly equal to Kafka.
- You need maintained software or other platforms. The last commit was in February 2023, issues #3 and #4 (2017, 2019) have no replies, there are no GitHub releases, and binaries exist only for x86-64 Linux, Windows x86/x64 and a Windows CE client. There are none for macOS or aarch64.
- You need per-message disk durability by default. Queues default to oMemoryCached, and a signal handler writes cached messages to the file on shutdown. Behavior on kill -9 or power loss is not documented.

## How it is fast

Requests are pipelined: a client keeps sending without waiting for replies, and both the client and server cores merge pending requests and results into full TCP packets. The vendor calls this 'inline batching', and Nagle's algorithm is disabled. Each Dequeue returns a batch of messages (16 KB by default, 32 KB in the benchmark server), and the benchmark keeps three Dequeue requests in flight so that disk reads, network transfer and client parsing overlap. On the server, enqueues under 4 KB run on the main thread to avoid a thread handoff, and EnqueueBatch commits many messages as one job. Two more factors matter. Queue writes default to oMemoryCached, which buffers them in process memory (revision 6.0.2.5), with FlushQueue pushing them to the OS cache or disk. The storage engine lives in the closed-source server core binary, so its file format and indexing cannot be inspected.

## Compared with alternatives

The siblings replace Kafka, NATS or ZeroMQ (Redpanda, Woodpecker, FluxMQ, Zenoh, Wisp, TCPSHM), and none targets RabbitMQ-style work queues. Pick SocketPro only if you are committed to its RPC framework and want the queue inside that server. For a maintained, durable, open log use Redpanda, and for crash-recoverable broker-less C++ point-to-point messaging use MIT-licensed TCPSHM.

## Integration

| | |
|---|---|
| **Form** | shared lib: prebuilt closed-source cores (usocket.dll/libusocket.so for the client, UServerCore.dll/libuservercore.so for the server) plus the uasyncqueue plugin .dll/.so. The plugin source is in include/queue/server_impl, and the C++ client adapter is compiled from include/aclientw.cpp and membuffer.cpp. |
| **Dependencies** | The prebuilt SocketPro core and plugin libraries, copied into /usr/lib or System32/SysWOW64. OpenSSL: the docs say 1.1.0+ and the 6.4 changelog says the cores link OpenSSL 3. libdl and pthread on Linux, and the Visual C++ 2015-2019 redistributable on Windows. |
| **Minimum toolchain** | C++11: the dev guide says so, and the qperf Makefile uses g++ -std=c++11 -O3. The co_await samples need C++20 coroutines. Tested compiler versions are not documented beyond Visual Studio 2015-2019 and g++ via NetBeans. |
| **Platforms** | Windows x86/x64 and Linux x86-64 (one binary set for Debian, Ubuntu, CentOS, RHEL and openSUSE), plus a Windows CE client (armv4i/x86). No macOS or aarch64 binaries. |
| **Thread safety** | The docs say the core libraries, socket pools and each pooled socket are thread-safe. The queue plugin guards each queue with a critical section and the key-to-queue map with a spin lock, and a queue may be shared by several producers and consumers at once. |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmark is not like-for-like. The RabbitMQ consumer in samples/qperf/rabbitmq/Program.cs sets BasicQos prefetch=1 and acks every message manually, so it pays one round trip per message. Cross-machine RabbitMQ dequeue took 44.4 s for 200-char and 45.4 s for 1024-char messages (about 444 us per message, flat with size), which fits that bottleneck. RabbitMQ enqueue timing stops when the BasicPublish loop returns (no publisher confirms), while SocketPro's waits for every server reply.
- The benchmark servers (cperf sq_server.cpp and the C# sq_server) never call FlushQueue or SetOptimistic, so the 'durable' SocketPro numbers ran at the oMemoryCached default. Call FlushQueue(key, cb, tagOptimistic::oDiskCommitted) when you need data committed to disk.
- Dequeue is batch-and-repeat: your DDequeue callback must re-issue Dequeue while messageCount &gt; 0, and throughput depends on keeping 2-3 requests in flight. The consumer must deserialize payloads with the same types and order the producer used (CUQueue), because there is no schema.
- The plugin opens every queue with a hard-coded ttl of 120 hours (StartQueue(key, 120\*3600)), and what expires is not documented. CloseQueue fails with QUEUE_DEQUEUING while messages are mid-dequeue, and the plugin drops all queue handles when its last client disconnects.

## Known shortcomings

- The live evidence page is gone (DNS dead); only a 2020 Wayback copy remains. No LICENSE file and the core ships as prebuilt binaries. Baseline is RabbitMQ, outside the category's list.
- The 54x is mostly a configuration artifact: the in-repo RabbitMQ consumer uses prefetch=1 with a manual ack per message (one round trip each, \~444 us/msg flat across sizes) and no publisher confirms. SocketPro's queue defaults to memory-cached and the bench server never flushes, so its 'durable' numbers aren't disk-committed. An in-repo 2017 Kafka comparison (0.10.1.1, percentages only) has Kafka \~20% faster on unbatched 4-32 B messages and SocketPro \~20-25% faster on medium/large. Closed binary core (.dll/.so), 'enterprise license', x86-64 Linux/Windows only; proprietary non-AMQP protocol; abandoned since 2023-02; vendor site dead.

## Caveats and trade-offs

First-party vendor page. The live evidence page (udaparts.com) no longer resolves; numbers are recovered from a 2020 Wayback snapshot (figures are images). Compiler/flags and RabbitMQ version are not stated. The broker ran in a 4GB VMware VM, and the network bandwidth is inconsistent (text 100 Mbps vs figure 1 Gbps). RabbitMQ is not a list baseline, and the Kafka claim has no numbers. There is no LICENSE file: the README calls the plugins 'free', and the core runtime ships as prebuilt binaries (bin/), with only adapters/plugins as source.

No license file (cannot legally reuse the code as-is); low adoption; the vendor's own detailed-results page (udaparts.com) is no longer reachable (DNS failure at time of research)

## Maintenance

Abandoned: the last commit is 2023-02-16 (v6.4), udaparts.com no longer resolves and old issues have no replies. With no license and a closed binary core, it is a reference design, not something you can legally vendor or patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README (benchmark_url) only says 'could be 50 times faster than RabbitMQ'. The detailed page it links (udaparts.com, domain no longer resolves) survives in the Wayback Machine with ms tables and CPU/OS for both machines, and the bench code is in-repo (samples/qperf). Compiler/flags are unstated, it is first-party, and the Kafka comparison has no numbers, so C.
- **Verifier notes:** The primary evidence page is dead, but the archived copy is traceable and contains the \~50x figure, so I kept the entry at C and pointed benchmark_url at the archive. The metadata matches: 28 stars, last commit 2023-02-16, abandoned, no license, reference.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/udaparts/socketpro>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/README.md>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/kafka_perf_test.txt>
  - <https://github.com/udaparts/socketpro/blob/master/README.md>
  - <http://www.udaparts.com/document/articles/fastsocketpro.htm>
  - <https://web.archive.org/web/20200210003353id_/http://www.udaparts.com:80/document/articles/fastsocketpro.htm>
  - <https://web.archive.org/web/20200210003353/http://www.udaparts.com/document/articles/fastsocketpro.htm>
  - <https://web.archive.org/web/2020id_/http://www.udaparts.com/document/articles/fastsocketpro_files/image003.png>
  - <https://web.archive.org/web/2020id_/http://www.udaparts.com/document/articles/fastsocketpro_files/image004.png>
- **Sources the enricher read:**
  - <https://github.com/udaparts/socketpro>
  - <https://github.com/udaparts/socketpro/blob/master/README.md>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/README.md>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/kafka_perf_test.txt>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/rabbitmq/Program.cs>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/cperf/sq_client/sq_client.cpp>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/cperf/sq_client/Makefile>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/cperf/sq_server/sq_server.cpp>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/server_queue/sq_client/Program.cs>
  - <https://github.com/udaparts/socketpro/blob/master/samples/qperf/server_queue/sq_server/Program.cs>
  - <https://github.com/udaparts/socketpro/blob/master/components/uasyncqueue/README.md>
  - <https://github.com/udaparts/socketpro/blob/master/include/queue/uasyncqueue.h>
  - <https://github.com/udaparts/socketpro/blob/master/include/queue/server_impl/asyncqueueimpl.h>
  - <https://github.com/udaparts/socketpro/blob/master/include/queue/server_impl/asyncqueueimpl.cpp>
  - <https://github.com/udaparts/socketpro/blob/master/include/aqhandler.h>
  - <https://github.com/udaparts/socketpro/blob/master/include/aserverw.h>
  - <https://github.com/udaparts/socketpro/blob/master/include/ucomm.h>
  - <https://github.com/udaparts/socketpro/blob/master/include/userver.h>
  - <https://github.com/udaparts/socketpro/blob/master/include/uclient.h>
  - <https://github.com/udaparts/socketpro/blob/master/lib/README.md>
  - <https://github.com/udaparts/socketpro/blob/master/bin/free_services/README.md>
  - <https://github.com/udaparts/socketpro/blob/master/doc/sp_arch.htm>
  - <https://github.com/udaparts/socketpro/blob/master/doc/cpp_serverqueue.htm>
  - <https://github.com/udaparts/socketpro/blob/master/doc/get_started.htm>
  - <https://github.com/udaparts/socketpro/blob/master/doc/dev_guide.htm>
  - <https://github.com/udaparts/socketpro/blob/master/doc/old_docs/sq_kafka_perf.pdf>
  - <https://github.com/udaparts/socketpro/blob/master/doc/old_docs/perf_comparison.pdf>
  - <https://github.com/udaparts/socketpro/blob/master/RevisionHistoryForLinux.txt>
  - <https://github.com/udaparts/socketpro/blob/master/RevisionHistoryForWin.txt>
  - <https://raw.githubusercontent.com/udaparts/socketpro/master/bin/linux/libuservercore.so>
  - <https://github.com/udaparts/socketpro/issues?q=is%3Aissue>
  - <https://github.com/udaparts/socketpro/issues/5>
  - <https://github.com/udaparts/socketpro/commits/master>
  - <https://web.archive.org/web/20200210003353id_/http://www.udaparts.com:80/document/articles/fastsocketpro.htm>
  - <https://web.archive.org/web/2020id_/http://www.udaparts.com/document/articles/fastsocketpro_files/image003.png>
  - <https://web.archive.org/web/2020id_/http://www.udaparts.com/document/articles/fastsocketpro_files/image004.png>
  - <https://hn.algolia.com/api/v1/search?query=SocketPro%20udaparts&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=udaparts>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/udaparts/socketpro`) · [data/wave6/enrich/raw/github_com_udaparts_socketpro.json](../../../data/wave6/enrich/raw/github_com_udaparts_socketpro.json) (enrichment confidence 0.7)

</details>
