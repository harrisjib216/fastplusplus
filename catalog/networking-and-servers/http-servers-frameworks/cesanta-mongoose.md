# Mongoose

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0-only` · 🟢 active

> Two-file C networking library with its own bare-metal TCP/IP stack; vendor reports about 3.8x lwIP raw's HTTP requests/s on an STM32F746.

| | |
|---|---|
| **Beats** | lwIP (raw API) TCP/IP stack with its HTTP server |
| **Claimed result** | Snippet only (mongoose.ws and eevblog.com EGRESS_BLOCKED). Search-result summaries of an EEVblog forum post (thread 'ch32v307, risc-v minicore with ethernet', msg5177385, headed 'How does it compare to lwIP?') report HTTP throughput on a Nucleo-F746ZG with an Ethernet dongle of 1080 requests/s for Mongoose's built-in stack vs 286 requests/s for lwIP raw API and 16 requests/s for lwIP sockets (about 3.8x and 67x, derived from snippet data), with firmware about 28k for Mongoose vs 114k-160k for the lwIP variants (the summaries disagree on which lwIP variant is 160k). The benchmark_url article itself, per its search summaries, reports footprint and integration size only, no requests/s: flash 50,140 vs 67,020 bytes, RAM 22,524 vs 31,504 bytes, 3 vs 279 files and 32k vs 105k lines added, Ethernet driver 250 vs 3,300 lines (Mongoose vs lwIP). |
| **Workload** | HTTP requests per second served by an STM32 Nucleo-F746ZG over Ethernet to a workstation, Mongoose (built-in TCP/IP stack) vs lwIP raw integration; the same article also compares flash and RAM footprint. |
| **Metric** | throughput |
| **Hardware** | STM32 Nucleo-F746ZG (Cortex-M7) board on Ethernet, benchmark run from a workstation |
| **Adoption** | 13.1k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/cesanta/mongoose) · [benchmark](https://mongoose.ws/articles/lwip-vs-mongoose-tcpip-stack-integration/) |

## Verdict

Snippet only (mongoose.ws and eevblog.com are EGRESS_BLOCKED): an EEVblog forum post reports siege fetching a 'hello world' page from a Nucleo-F746ZG (Cortex-M7) over an Ethernet dongle at 1080 req/s with Mongoose's built-in stack (about 28 KB firmware) against 286 req/s for lwIP raw API (about 114 KB) and much lower rates for socket-based lwIP or Zephyr, with the snippets disagreeing on the lower rows. The benchmark_url article measures footprint and integration effort on a NUCLEO-F756ZG (about 50 KB vs 67 KB flash, 22.5 KB vs 31.5 KB RAM), not speed; compiler, flags, lwIP options and keep-alive settings are not published.

## Use it when

- Bare-metal or small-RTOS MCU with on-chip Ethernet (STM32F7/H5/H7, i.MX RT, SAME54, RA) or a W5500 that needs a device web UI, REST API, WebSocket or MQTT with little flash and RAM.
- Replacing a CubeMX lwIP plus httpd integration when integration effort and footprint matter: the vendor's integration article reports 3 files vs 279 and about 50 KB vs 67 KB flash (snippet only).
- Local-network device dashboards where request latency and requests/s on a lossless LAN link matter more than WAN robustness.
- Projects wanting one networking API that also builds on Linux, macOS and Windows (epoll on Linux, poll elsewhere) for host-side testing.

## Skip it when

- Lossy, slow or high-latency links (cellular, Wi-Fi at range, WAN) with the default build: the built-in stack does not resend lost data unless the retransmission queue is enabled, and issue #3507 reports silent WebSocket data loss over GSM/LTE.
- Closed-source products that cannot buy Cesanta's commercial licence: the open licence is GPL-2.0 only.
- High-throughput Linux servers: it is a single-threaded event loop aimed at embedded devices; the catalogued Linux servers (Lwan, H2O, libuhttpd, Drogon) have published multi-core results and Mongoose has none.
- Bulk transfers where TCP window size and congestion control matter: the receive window is a fixed 6000 bytes (MG_TCPIP_WIN) and there is no cwnd or slow start.
- Code that must call the network API from several threads: all mg_\* calls must come from the task that runs mg_mgr_poll, with mg_wakeup() as the only cross-thread entry.

## How it is fast

The built-in stack has no sockets layer and no per-socket buffering: received frames are parsed in the polling loop and the TCP payload is copied once into the connection's receive buffer, then the HTTP parser hands the callback mg_str views into that buffer instead of copying headers. Everything runs in one cooperative event loop, with interrupt-driven drivers feeding a lock-free single-producer, single-consumer frame queue, so there are no task switches or mailbox handoffs between driver, stack and application. Part of the gap is also the stack doing less TCP work: it keeps no congestion-control state, drops out-of-order segments rather than queueing them, uses a fixed 6000-byte receive window and, by default, keeps no retransmission queue (see gotchas).

## Compared with alternatives

Pick Mongoose when the target is a microcontroller without an OS-level sockets stack; none of the catalogued siblings (Lwan, H2O, libuhttpd, Kore, Drogon) run bare metal. On Linux, pick libuhttpd for a small embedded-Linux server or Lwan or H2O for throughput, since those have published multi-core results and Mongoose has none.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (optional: lwIP, Zephyr, FreeRTOS-TCP or Keil RL-TCPnet instead of the built-in stack; mbedTLS, OpenSSL or wolfSSL instead of the built-in TLS) |
| **Minimum toolchain** | C99 or newer (mongoose.h errors on older C), or C++; test/ has GCC, Keil, TI CGT, MCUXpresso, CubeIDE, ESP-IDF, Zephyr, pico-sdk and Arduino builds |
| **Platforms** | Built-in stack: MCUs with listed Ethernet drivers (STM32F/H, NXP i.MX RT and RW612/MCXN, Microchip SAME54, Renesas RA, Infineon XMC, TI TM4C/TMS570), W5500/W5100, CYW43 Wi-Fi, cellular via PPP/AT; otherwise any OS with BSD sockets (Linux, macOS, Windows, ESP-IDF, Zephyr) |
| **Thread safety** | Not thread-safe: call every mg_\* function from the task that runs mg_mgr_poll; mg_wakeup() is the documented thread- and ISR-safe way in, and drivers push frames from ISRs through mg_tcpip_qwrite()'s lock-free queue. |
| **Drop-in for the baseline** | partial: replaces lwIP and its HTTP server as a whole stack with Mongoose's own event API; it can also run on top of lwIP (MG_ENABLE_LWIP=1), but then lwIP's performance applies and the claimed gain does not. |

## Gotchas

- No TCP data retransmission by default: mg_io_send advances the sequence number and write_conn deletes the bytes from c-&gt;send, so a lost outbound segment is never resent unless MG_ENABLE_TCPIP_TCPRTX=1 or ifp-&gt;enable_tcp_retransmit is set. The optional queue only arrived in PR #3682 (merged 2026-09-08); PR #2297 (2023) titled 'implemented tcp retransmission' only resent ACKs. The 1080 req/s figure therefore compares a stack without a retransmit queue, congestion control or out-of-order reassembly against lwIP raw, whose tcp_pcb keeps unacked, ooseq, cwnd and ssthresh state: a harness flaw in the comparison, not just a tuning difference.
- Out-of-order TCP segments are dropped and re-ACKed rather than queued, and the receive window is a fixed 6000 bytes (MG_TCPIP_WIN), so throughput collapses with reordering or high bandwidth-delay paths.
- Security history is heavy: GitHub lists ten advisories (two critical HTTP request-smuggling bugs, TLS CA-bundle chains accepted without signature checks, TCP-options and PPP out-of-bounds reads), plus CVE-2026-5246 (built-in TLS mTLS signature bypass, 7.0 to 7.20) and CVE-2026-73251 (forged-certificate acceptance, fixed in 7.23); stay on the latest release and prefer mbedTLS or wolfSSL if the built-in TLS worries you.
- Every throughput number is first-party and seen only through search snippets that disagree with each other (lwIP raw 286 req/s in one, 16 req/s with a 160k image in another, plus a 3 req/s Zephyr sockets row); no lwIP configuration, compiler, flags or benchmark code is published, and the repo has no benchmark directory.

## Known shortcomings

- Vendor first-party claim seen only as search snippets (mongoose.ws and the EEVblog post blocked): 1080 req/s Mongoose vs 286 lwIP raw vs 16 lwIP sockets on a Nucleo-F746ZG, with no public bench code, compiler, flags or lwIP tuning (16 req/s for lwIP sockets looks untuned); the linked page carries footprint only (flash 50,140 vs 67,020 B, RAM 22,524 vs 31,504 B), which is not speed. GPL-2.0 or commercial.
- Enricher: the default built-in TCP/IP stack kept no retransmission queue at the time of the claim (MG_ENABLE_TCPIP_TCPRTX 0; write_conn deletes sent bytes on send; the optional queue arrived with PR #3682 on 2026-09-08), has no congestion control, drops out-of-order segments and uses a fixed 6000-byte window, so the 1080 req/s run compared a lighter stack against lwIP raw, which keeps unacked/ooseq/cwnd state. Snippets disagree on the lwIP figures (286 vs 16 req/s). Issue #3507 (silent WebSocket data loss over GSM/LTE on 7.21); 10 GitHub advisories including 2 critical HTTP request smuggling, CVE-2026-5246, CVE-2026-73251.
- Re-found by the wave 5 seed backfill (w5-mine-n) with a vendor article (lwIP raw API 286 vs Mongoose 1080 requests per second, snippet only; mongoose.ws blocked); first-party, tier C either way.
- Name override keeps the verified identity after the w5-mine-n raw copy won the merge dedup.

## Caveats and trade-offs

First-party vendor measurement by Cesanta, which sells Mongoose's commercial licence. Every figure comes from machine-written WebSearch summaries: mongoose.ws (both lwIP-vs-Mongoose articles) and eevblog.com are EGRESS_BLOCKED here. The requests/s figures (1080 vs 286 vs 16) are not on the benchmark_url page according to its summaries; they come from an EEVblog forum post and possibly the 'lwIP vs Mongoose ... (Part 1)' article at mongoose.ws/articles/lwip-vs-mongoose, neither of which could be opened. The benchmark_url article measures footprint and integration effort, not speed, and one summary names its board as Nucleo-F756ZG rather than F746ZG. Compiler, flags, lwIP configuration (lwipopts.h buffer and window tuning), HTTP server used on top of lwIP, response size, keep-alive and client tool were not seen; 16 requests/s for lwIP sockets is far below typical lwIP results and suggests untuned defaults, so the gap may reflect configuration as much as stack design. The repo README links the integration article but has no numbers and no benchmark directory. Licence is GPL-2.0 (strong copyleft) or a paid commercial licence. [retier] Vendor first-party claim seen only as search snippets (mongoose.ws and the EEVblog post blocked): 1080 req/s Mongoose vs 286 lwIP raw vs 16 lwIP sockets on a Nucleo-F746ZG, with no public bench code, compiler, flags or lwIP tuning; snippets disagree on the lwIP figures (286 vs 16 req/s, Zephyr sockets 3 req/s). The built-in Mongoose TCP/IP stack measured there kept no TCP retransmission queue (MG_ENABLE_TCPIP_TCPRTX 0, sent bytes deleted on send; the optional queue arrived with PR #3682 on 2026-09-08), has no congestion control, drops out-of-order segments and uses a fixed 6000-byte window, so it did less work than lwIP raw. The linked page carries footprint only (flash 50,140 vs 67,020 B, RAM 22,524 vs 31,504 B). Issue #3507 (silent WebSocket data loss over GSM/LTE on 7.21); 10 GitHub advisories including 2 critical request-smuggling ones. GPL-2.0 or commercial.

Dual licensed: GPL-2.0-only or paid commercial licence from Cesanta; embedded targets (STM32, NXP, ESP32, RP2040 and others) plus POSIX and Windows. Two-file C library (mongoose.c, mongoose.h) with built-in TCP/IP, HTTP, WebSocket, MQTT, TLS 1.3.

## Maintenance

Very active (commits into October 2026, header at 7.23, release 7.22 in June 2026) and easy to vendor as two files, but GPL-2.0-only or paid commercial, and the speed claim rests on unreproducible vendor numbers against a stack that does more TCP work (retransmission, congestion control, reordering), which the default Mongoose build still omits.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party vendor numbers (Cesanta sells Mongoose's commercial licence) against lwIP, seen only through WebSearch result summaries because mongoose.ws and eevblog.com are EGRESS_BLOCKED; no benchmark code, compiler, flags or HTTP workload is published in the repo, so it cannot reach A or B.
- **Verifier notes:** Kept at C, snippet only: req/s claim (Mongoose 1080 vs lwIP raw 286 vs lwIP sockets 16 on Nucleo-F746ZG) traces to an EEVblog forum post and possibly mongoose.ws Part 1, not to the benchmark_url, which (per summaries) holds only flash/RAM/lines-of-code footprint numbers; all three pages are EGRESS_BLOCKED. Shortcomings to record: vendor first-party, no public benchmark code or methodology, lwIP tuning unstated (lwIP sockets 16 req/s looks untuned), footprint is not speed, GPL-2.0 or commercial. Metadata checked: GPLv2/commercial dual licence (LICENSE says version 2, no 'or later'), 13.1k stars, last commit 2026-10-06, not archived, not a fork; not a duplicate of a listed project.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** vendor snippets (verifier); enricher code reading; backfill w5-mine-n; orchestrator
- **Pages the verifier opened:**
  - <https://github.com/cesanta/mongoose>
  - <https://github.com/cesanta/mongoose/commits>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/README.md>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/cesanta/mongoose>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/README.md>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/mongoose.h>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/src/net_builtin.c>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/src/net_builtin.h>
  - <https://raw.githubusercontent.com/cesanta/mongoose/HEAD/src/config.h>
  - <https://github.com/cesanta/mongoose/tree/master/test>
  - <https://github.com/cesanta/mongoose/tree/master/tutorials/stm32>
  - <https://github.com/cesanta/mongoose/tree/master/tutorials/stm32/nucleo-f746zg>
  - <https://github.com/cesanta/mongoose/releases>
  - <https://github.com/cesanta/mongoose/commits/master/src/config.h>
  - <https://github.com/cesanta/mongoose/security/advisories>
  - <https://github.com/cesanta/mongoose/issues?q=is%3Aissue+retransmission>
  - <https://github.com/cesanta/mongoose/pulls?q=is%3Apr+retransmission>
  - <https://github.com/cesanta/mongoose/issues/3507>
  - <https://github.com/cesanta/mongoose/pull/3682>
  - <https://github.com/cesanta/mongoose/pull/2297>
  - <https://raw.githubusercontent.com/lwip-tcpip/lwip/master/src/include/lwip/tcp.h>
  - https://mongoose.ws/articles/lwip-vs-mongoose-tcpip-stack-integration/ (EGRESS_BLOCKED; WebSearch snippet only)
  - https://mongoose.ws/articles/lwip-vs-mongoose (not opened; WebSearch snippet only)
  - https://eevblog.com/forum/microcontrollers/ch32v307-risc-v-minicore-with-ethernet/msg5177385 (not opened; WebSearch snippet only)
  - https://mend.io/vulnerability-database/CVE-2026-73251/ (WebSearch snippet only)
  - https://www.wiz.io/vulnerability-database/cve/cve-2026-5246 (WebSearch snippet only)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cesanta/mongoose`) · [data/wave5/enrich/raw/github_com_cesanta_mongoose.json](../../../data/wave5/enrich/raw/github_com_cesanta_mongoose.json) (enrichment confidence 0.55)

</details>
