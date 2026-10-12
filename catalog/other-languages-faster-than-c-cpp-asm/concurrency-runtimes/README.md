# Concurrency runtimes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md)</sub>

**What these beat:** the same task written in C or C++ at -O3, or hand-written assembly where the source compares against it  
**21 entries:** 1 tier A · 1 tier B · 12 tier C · 7 tier D · 19 copyable, 2 study only

**Languages swept:** Go, Erlang/BEAM, Pony, Rust (tokio), Kotlin coroutines  
**Where they tend to win:** scheduler design, message passing, cheap green threads

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Go goroutines vs Intel TBB on a task-graph dynamic program…**](luncliff-comparison-go-cpptbb.md) | 2017 study: Go goroutines vs Intel TBB tasks on tiled optimal-BST dynamic programming; Go won only at N=4096, by 1.003-1.15x. | **A** | Go | CC-BY-4.0 (study only) | 🔴 abandoned |
| 2 | [**Pony actor mailbox performance (100,000,000 messages) vs…**](lang-pony-ponylang-ponylang-website-mailbox-performance.md) | Pony's actor runtime on a 100-sender, one-receiver mailbox stress test, about 6-8x CAF 0.13 throughput in 2015 charts. | **B** | Pony | BSD-2-Clause | 🟢 active |
| 3 | [**Rust std futex-based Mutex (rust-lang/rust PR 95035) vs the…**](paper-rust-lang-rust-pr95035-futex-mutex.md) | Rust's std::sync::Mutex on Linux since 1.62: an inline three-state futex word with a short spin, replacing a boxed glibc pthread_mutex_t. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 4 | [**Tokio (1M concurrent tasks, peak memory)**](tokio-rs-tokio.md) | Rust's work-stealing async runtime; 1M sleeping tasks used 2.8x less peak memory than concurrencpp and 4x less than Asio. | **C** | Rust | MIT | 🟢 active |
| 5 | [**GHC Haskell lightweight threads (skynet 1M-spawn benchmark…**](lang-haskell-atemerev-skynet-skynet.md) | GHC sparks and green threads: skynet spawn cost 0.05-0.06 us per unit versus 52-73 us per C++ OS thread. | **C** | Haskell | BSD-3-Clause | 🟢 active |
| 6 | [**Redcon (Go Redis-compatible server framework; clone vs real…**](tidwall-redcon.md) | Go framework for writing Redis-protocol servers; its 136-line map clone out-ran redis-server about 2x on a 2016 laptop pipeline test. | **C** | Go | MIT | 🟢 active |
| 7 | [**ScyllaDB Rust driver (async Tokio CQL driver vs C++ driver)**](scylladb-scylla-rust-driver.md) | Pure-Rust async Tokio CQL driver for ScyllaDB and Cassandra; the vendor's insert benchmark shows it level with the multi-threaded DataStax C++ driver. | **C** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 8 | [**Stylo (Rust parallel CSS style engine in Firefox Quantum)…**](servo-stylo.md) | Firefox's and Servo's Rust CSS style engine; its parallel cascade replaced Gecko's sequential C++ style system in Firefox 57. | **C** | Rust | MPL-2.0 | 🟢 active |
| 9 | [**NPB-Rust (NAS Parallel Benchmarks in Rust, sequential and…**](lang-rust-gmap-npb-rust-npb-sequential.md) | Rust port of the NAS Parallel Benchmarks; its paper reports the sequential suite 5.59% faster than C++ NPB-CPP. | **C** | Rust | MIT | 🟢 active |
| 10 | [**Myelon / disruptor-mp (shared-memory ring-buffer IPC…**](venkat2811-myelon.md) | Rust LMAX-Disruptor-style shared-memory IPC ring for Linux and macOS; first-party 1 KB ping-pong chart beats Boost.Interprocess and Open MPI. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 11 | [**Cynosure RingBuf (async-native SPSC ring buffer, Rust)**](zk2u-cynosure.md) | Rust lock-free SPSC ring with built-in async push/pop; 1.29 vs 2.46 ns push+pop against rigtorp::SPSCQueue on Apple M4 Max. | **C** | Rust | MIT (declared in Cargo.toml… | 🟢 active |
| 12 | [**Kairos / rusty_rtos_kernel (FreeRTOS kernel remade in Rust)**](remade-with-rust-rusty-rtos-kernel.md) | FreeRTOS V11.3.1 scheduler rewritten in safe no_std Rust; fewer instructions per rv32 tick and cooperative switch, less RAM per task, more flash. | **C** | Rust | MIT OR Apache-2.0 | 🟢 active |
| 13 | [**evio (Go epoll/kqueue event loop; Redis clone vs real Redis)**](tidwall-evio.md) | Go event-loop framework using raw epoll/kqueue; its toy Redis clone out-served Redis 4.0.2 on pipelined PING. | **C** | Go | MIT | 🔴 abandoned |
| 14 | [**Rayon vs OpenMP (CMU 15-618 project)**](trsupradeep-15618-project.md) | 2019 CMU course study timing Rust+Rayon against C++/OpenMP on four kernels; Rayon wins only large parallel stable sorts. | **C** | Rust | no license (study only) | 🔴 abandoned |
| 15 | [**Go goroutines on thread-ring (SCOOP/Qs paper, arXiv…**](lang-go-arxiv-1405-7153-thread-ring.md) | Go goroutines passing a token round a 503-member ring, 2.4x faster than a C++ Boost.Asio program on 503 OS threads. | **D** | Go | BSD-3-Clause | 🟢 active |
| 16 | [**Go net TCP echo server (Boost.Redis echo benchmark, vs…**](lang-go-boostorg-redis-tcp-echo-direct.md) | Go's net package with one goroutine per connection, as a TCP echo server; about 1.22x less wall time than the libuv docs example. | **D** | Go | BSD-3-Clause | 🟢 active |
| 17 | [**Tokio TCP echo server (Boost.Redis echo benchmark, vs libuv)**](lang-rust-boostorg-redis-tcp-echo-direct.md) | Tokio's docs-example TCP echo server on the single-threaded runtime; one 2022 run took 30.7 s against 43.6 s for the libuv docs example. | **D** | Rust | MIT | 🟢 active |
| 18 | [**Erlang/OTP processes on thread-ring (SCOOP/Qs paper, arXiv…**](lang-erlang-arxiv-1405-7153-thread-ring.md) | Erlang/BEAM processes pass a token round a 503-member ring about 10x faster than a Boost.Asio C++ program using 503 OS threads. | **D** | Erlang | Apache-2.0 | 🟢 active |
| 19 | [**Embassy (async Rust executor) vs FreeRTOS**](embassy-rs-embassy.md) | Async Rust embedded framework whose cooperative executor replaces an RTOS; claimed smaller than FreeRTOS, latency win unproven. | **D** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 20 | [**Pony actor message ring plus factorisation vs CAF and…**](lang-pony-ponylang-ponylang-website-message-ring-factorisation.md) | Pony actor rings plus trial-division workers vs CAF 0.13 (2015 charts, 2-4x); Pony's program skips most repetitions. | **D** | Pony | BSD-2-Clause | 🟢 active |
| 21 | [**Lingua Franca (reactor language, C++ runtime) on the Savina…**](lang-lingua-franca-lf-lang-benchmarks-lingua-franca-savina.md) | Deterministic reactor language whose generated C++ (reactor-cpp runtime) ran the ported Savina suite faster than CAF and Akka. | **D** | Lingua Franca | BSD-2-Clause | 🟡 mixed |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
