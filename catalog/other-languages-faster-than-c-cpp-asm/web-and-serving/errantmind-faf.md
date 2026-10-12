# faf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `AGPL-3.0` · 🟡 stale

> Minimal Linux epoll HTTP/1.1 server in unsafe Rust that tied lithium and cinatra (C++) on TechEmpower Round 22 plaintext.

| | |
|---|---|
| **Beats** | lithium (C++) and cinatra (C++) in the TechEmpower Round 22 plaintext leaderboard |
| **Claimed result** | TechEmpower Round 22 plaintext, as shown in a third-party screenshot: faf rank 2 of 486 at 7,010,014 responses/s vs cinatra (C++) 6,998,076 (rank 7, +0.17%, derived from page data), lithium (C++) 6,993,976 (rank 9, +0.23%, derived), libreactor (C) 6,971,119 (rank 11, +0.56%, derived), libsniper (C++) 6,883,107 (+1.8%, derived), cuehttp (C++) 6,224,825 (1.13x, derived) and userver[bare] (C++) 5,974,256 (1.17x, derived). Against the named baselines this is a tie at the network ceiling, measured with a canned-response handler. |
| **Workload** | TechEmpower Round 22 plaintext test (HTTP pipelining, 10 GbE) for faf, a Linux-only Rust web server stripped to the plaintext route. |
| **Metric** | throughput |
| **Hardware** | TechEmpower Round 22 physical environment: Dell R440 servers with an Intel Xeon Gold 5120 (28 HT cores), 32 GB RAM and a dedicated Cisco 10 GbE switch (leaderboard header 'Dell R440 Xeon Gold + 10 GbE' plus the hardware block in the gnet README that embeds the screenshot) |
| **Compiler and flags** | TechEmpower frameworks/Rust/faf/faf.dockerfile (HEAD): base image errantmind/debian-faf:v3 (nightly rustc, version not stated), clang-15 and ld.lld-15, RUSTFLAGS -Ctarget-cpu=native -Ztune-cpu=native -Zmutable-noalias=yes -Copt-level=3 -Clto=thin -Ccodegen-units=1 -Cpanic=abort -Coverflow-checks=no -Cdebug-assertions=no, cargo build --release -Zbuild-std; the faf crate is pulled from git HEAD (unpinned). C++ side: lithium compile.sh builds with clang++ -O3 -march=native -flto plus PGO; cinatra's dockerfile runs cmake .. with no CMAKE_BUILD_TYPE. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Single-purpose server tuned for the benchmark: unsafe Rust, no dependencies, optional no_std with about 400 lines of assembly text (README); no profiling analysis given. |
| **Adoption** | 186 stars |
| **Last commit** | 2024-04-14 |
| **Links** | [repository](https://github.com/errantmind/faf) · [benchmark](https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg) |

## Verdict

In the TechEmpower Round 22 plaintext test (pipelined HTTP/1.1 over 10 GbE, Dell R440 with Xeon Gold 5120), faf placed 2nd of 486 at 7,010,014 responses/s, against cinatra (C++) at 6,998,076 (+0.17%), lithium (C++, clang -O3 -march=native with PGO) at 6,993,976 (+0.23%) and libreactor (C) at 6,971,119 (+0.56%). This is a tie at the network ceiling, measured with a handler that writes a precomputed response; the figures were read from a third-party screenshot.

## Use it when

- Studying how far a syscall-level epoll design can go: at the TechEmpower Round 22 plaintext ceiling (Xeon Gold 5120, 10 GbE) it sits in the same 0.3% band as lithium, cinatra and libreactor.
- Serving one or a few fixed, small GET responses (health checks, canned pages) on dedicated Linux x86-64 boxes where you control every client and can audit about 1,000 lines of unsafe code.
- As reference code for SO_REUSEPORT plus CBPF CPU steering, per-core pinned workers and batched pipelined responses that you can port into your own server.

## Skip it when

- Anything that faces untrusted clients. See the response-buffer overflow under gotchas.
- Requests with bodies, headers you need to read, TLS, HTTP/2, chunked encoding or keep-alive control: the callback only gets method and path, and the parser jumps straight to the blank line, so a POST body is parsed as the next request.
- Responses larger than RES_BUFF_SIZE (4,096 bytes) or slow clients. A partial or EAGAIN sendto closes the connection with SO_LINGER 0 (a reset) instead of buffering the remainder.
- Non-Linux, non-x86-64, or stable-Rust builds. It needs nightly (core_intrinsics), x86-64 Linux syscall numbers and SSE4.2, and it has not been touched since 2024-04-14.
- As evidence that Rust beats C++: the plaintext top band is network-bound, and TechEmpower reclassified faf as Stripped in January 2026 (PR #10608) for hard-coding its headers, while lithium and cinatra run real frameworks.

## How it is fast

It runs one thread per logical CPU, each pinned with sched_setaffinity, with its own SO_REUSEPORT listener and epoll instance. A classic-BPF SO_ATTACH_REUSEPORT_CBPF program (added April 2024) steers each connection to the listener on the CPU that received it, and each thread calls unshare(CLONE_FILES) to keep fd numbers small. All syscalls are raw inline-asm `syscall` instructions on fixed per-fd request buffers, using recvfrom/sendto with TCP_NODELAY. An SSE4.2 `_mm_cmpestri` scan finds the end of each pipelined request, and all responses for one read go out in a single sendto. epoll_wait switches to a zero timeout while events keep arriving. The TechEmpower entry adds nightly -Zbuild-std, thin LTO, codegen-units=1, panic=abort and target-cpu=native, and its handler copies a precomputed status line and header block.

## Compared with alternatives

Pick faf only as a reference design. For a real server, ntex or actix-web (same plaintext band or the HttpArena C++-beating rows, full HTTP and safe APIs) or a raw tokio or libxev server from the HttpArena siblings do the same job without unbounded writes. firenio and wizzardo-http share faf's 0.2% tie with lithium and cinatra on the same Round 22 screenshot.

## Integration

| | |
|---|---|
| **Form** | crate via git dependency only (the `faf` name on crates.io is an unrelated MIT project, Wolfe-Jam/faf 0.3.0) |
| **Dependencies** | none (libc symbols memcmp, sysconf, sched_\*affinity and clock_gettime via extern "C"; std threads) |
| **Minimum toolchain** | nightly Rust (feature core_intrinsics; the TechEmpower entry also builds std with -Zbuild-std); rustc version not pinned, no rust-toolchain file |
| **Platforms** | Linux x86-64 only (raw syscall numbers, inline asm), SSE4.2 required by the request parser |
| **Thread safety** | One worker thread per logical CPU with no shared connection state. Shared globals are `static mut` with no synchronization: the main thread rewrites the Date buffer every second while workers copy it, and workers bump a startup counter non-atomically. |
| **Drop-in for the baseline** | no |

## Gotchas

- Remotely triggerable stack buffer overflow, found by reading src/epoll.rs. For each pipelined request in one recvfrom (up to 4,096 bytes), the callback receives `resbuf + response_buffer_filled_total` but no remaining-length argument, and nothing checks the running total against RES_BUFF_SIZE (4,096, a stack local). The TechEmpower callback writes 126 bytes per `GET /plaintext`, and the parser accepts a 19-byte request (`GET /plaintext \r\n\r\n`). One packet of about 215 such requests therefore writes about 27 KB into the 4 KB buffer, and any client pipelining 33 or more short requests overflows it. The README's advice that callbacks can simply avoid writing past RES_BUFF_SIZE cannot be followed under pipelining. TechEmpower's 16-deep pipelines of full-header requests stay under the limit, so the benchmark never hits it.
- Request-buffer handling: a partial request is kept in place and the next read is appended after it, with no compaction. If reads keep ending mid-request, the per-connection 4,096-byte slot fills, recvfrom is called with length 0, and the connection is closed. The method scan always reads 9 bytes, and `len -= i` can underflow on a fragment shorter than the method, so the parser reads past the received bytes. Commit history shows earlier fixes in this area ('Fix rare bug related to MTU + HTTP 1.1 pipelining', 'residual fix', October 2022).
- Data races by design: HTTP_DATE and NUM_WORKERS_INITED are `static mut` and shared across threads without atomics, so a Date header can be torn at a second boundary. The code comment admits that without a sleep the counter 'will never be rechecked', which is the compiler legally hoisting a racy load.
- The TechEmpower entry builds faf from git HEAD (unpinned), on a personal base image errantmind/debian-faf:v3 with an unstated nightly, so the measured code depends on the run date. The CBPF steering commit (2024-04-14) post-dates Round 22.

## Known shortcomings

- Ties lithium/cinatra (+0.17-0.23%) at the saturated 10 GbE TechEmpower plaintext ceiling; the handler sends a canned response (TechEmpower relabelled it Stripped in PR #10608, 2026-01-23); numbers only from a third-party screenshot. Stale since 2024-04-14.
- Security bug found by reading src/epoll.rs: a remotely triggerable stack buffer overflow. Pipelined responses are appended to a 4,096-byte stack resbuf with no bound check and the callback gets no remaining length; the TFB callback writes 126 bytes per 19-byte request, so 33 or more short pipelined requests in one packet overflow (about 27 KB per 4 KB packet); the TFB load never hits it. Also: no request-buffer compaction (the connection is closed when the slot fills), a len -= i underflow reads past the received bytes, racy static mut Date and counter, a partial sendto resets the connection, request bodies are not consumed. The crates.io name faf is an unrelated crate.

## Caveats and trade-offs

At Round 22 faf was listed as Realistic/Platform (IA column 'Rea' on the screenshot); TechEmpower PR #10608 (2026-01-23, under issue #9578 'No more fakes') reclassified it as Stripped because it hardcodes HTTP headers: the TFB src/main.rs copies a constant status line, Server, Content-Type and Content-Length block, then the cached date and the body, after checking only the method and path. lithium (Realistic, Micro) and cinatra (Realistic, Fullstack) run real frameworks, so faf does less work per request. Plaintext at the top of the table is saturated: the first nine rows are within 0.3% and the first 19 within 6%, network and pipelining bound, so the ordering among them is noise, not a language effect. Numbers are read from a screenshot hosted in the gnet author's illustrations repo (the header does not name the round; the gnet README links it to Round 22); techempower.com was unreachable from this environment. The faf README claims design choices were 'meticulously benchmarked' but names no competitors and gives no numbers; the no_std variant is said to be about 1% slower. Last commit 2024-04-14 (stale). Drogon does not appear in the top 50 screenshot. [retier] Security bug (code reading, src/epoll.rs): pipelined responses are appended to a 4,096-byte stack buffer with no bound check and the callback gets no remaining length, so 33 or more short pipelined requests in one packet overflow the stack (about 27 KB per 4 KB packet); the TFB load never hits it. No request-buffer compaction, a len -= i underflow reads past the received bytes, racy static mut Date and counter, partial sendto resets the connection, request bodies not consumed.

Linux x86_64 and nightly Rust only, extensive unsafe code (README ranks speed first and memory safety third), bounded response buffer for small and moderate payloads, AGPL-3.0, unsolicited PRs not reviewed.

## Maintenance

Stale since 2024-04-14 (37 commits, 186 stars, AGPL-3.0, unsolicited PRs not reviewed), and it has an unchecked response-buffer overflow, so it is copyable only as study material, not as a deployable server.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The screenshot of the TechEmpower Round 22 plaintext leaderboard does list faf at 7,010,014 next to lithium and cinatra, but the margin over the named C++ baselines is 0.17-0.23% at the 10 GbE ceiling (a tie), and the faf entry writes a precomputed response after checking only method and path, which TechEmpower reclassified as Stripped in January 2026 (PR #10608), so the comparison with the Realistic C++ frameworks is not like-for-like; capped at C under the asymmetric-harness precedent.
- **Verifier notes:** Numbers and metadata (AGPL-3.0, 186 stars, last commit 2024-04-14, stale, not a fork, not archived) confirmed; downgraded B to C. Record as shortcomings: tie with lithium and cinatra (+0.17-0.23%) at the network-bound plaintext ceiling; canned-response handler, reclassified Stripped by TechEmpower in January 2026 (PR #10608); numbers only from a third-party screenshot.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-17 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg>
  - <https://raw.githubusercontent.com/panjf2000/gnet/HEAD/README.md>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/faf.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/src/main.rs>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/Cargo.toml>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/lithium/lithium.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/lithium/compile.sh>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/lithium/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/cinatra/cinatra.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/cinatra/benchmark_config.json>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/commits/master/frameworks/Rust/faf/benchmark_config.json>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/pull/10608>
  - <https://github.com/errantmind/faf>
  - <https://github.com/errantmind/faf/commits>
- **Sources the enricher read:**
  - <https://github.com/errantmind/faf>
  - <https://github.com/errantmind/faf/commits/master>
  - <https://github.com/errantmind/faf/issues?q=is%3Aissue>
  - <https://github.com/errantmind/faf/issues/1>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/README.md>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/REF.md>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/epoll.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/net.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/http_request_path.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/const_config.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/const_http.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/util.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/syscall.rs>
  - <https://raw.githubusercontent.com/errantmind/faf/HEAD/src/http_date.rs>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/src/main.rs>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/faf.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/Cargo.toml>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/faf/README.md>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/pull/10608>
  - <https://crates.io/api/v1/crates/faf>
  - <https://crates.io/api/v1/crates/faf-syscall>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/errantmind/faf`) · [data/wave14/enrich/raw/github_com_errantmind_faf.json](../../../data/wave14/enrich/raw/github_com_errantmind_faf.json) (enrichment confidence 0.76)

</details>
