# Logging and tracing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md)</sub>

**What these beat:** spdlog, glog, OpenTelemetry SDK  
**23 entries:** 14 tier A · 0 tier B · 8 tier C · 1 tier D · 22 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Quill**](odygrd-quill.md) | Asynchronous C++17 logger whose LOG_INFO call site costs single-digit nanoseconds, about 45x below async spdlog at p50. | **A** | C++ | MIT | 🟢 active |
| 2 | [**loguru**](emilk-loguru.md) | Two-file synchronous C++ logger with printf-style LOG_F; 1.8x lower per-line cost than glog 0.6.0 single-threaded, mixed under contention. | **A** | C++ | Unlicense | 🟢 active |
| 3 | [**G3log**](kjellkod-g3log.md) | Public-domain asynchronous C++ logger with crash-safe flush; \~3x lower call-site latency than Boost.Log, 3-4x slower than spdlog. | **A** | C++ | Unlicense | 🟢 active |
| 4 | [**phuslu/log**](phuslu-log.md) | Zero-allocation structured JSON logger for Go, faster than zerolog, zap and log/slog in its own benchmarks. | **A** | Go | MIT | 🟢 active |
| 5 | [**BqLog**](tencent-bqlog.md) | Tencent's C++ async logger with a real-time compressed binary format; much higher end-to-end throughput than spdlog async and glog. | **A** | C++ | Apache-2.0 | 🟢 active |
| 6 | [**haclog**](mugglewei-haclog.md) | Plain C async printf-style logger; producer-side calls about 3.5x faster than spdlog when buffers are not full. | **A** | C | MIT | 🟢 active |
| 7 | [**XTR**](choll-xtr.md) | C++20 low-latency logger: per-thread SPSC ring buffer plus background {fmt} consumer; about 6-10 ns call-site latency vs spdlog async's 271-360 ns. | **A** | C++ | MIT | 🟢 active |
| 8 | [**slick-logger**](slickquant-slick-logger.md) | Header-only C++20 async logger: lock-free ring, formatting deferred to a writer thread; 2-5x spdlog async on producer-side throughput. | **A** | C++ | MIT | 🟢 active |
| 9 | [**NanoLog (PlatformLab)**](platformlab-nanolog.md) | Binary, printf-style C++ logger from Stanford PlatformLab with about 7-14 ns call-site latency, 20-40x below spdlog. | **A** | C++ | ISC | 🟡 stale |
| 10 | [**fmtlog**](mengrao-fmtlog.md) | Asynchronous fmt-syntax C++ logger with about 6 ns caller-side latency per call, versus 150-400 ns for synchronous spdlog. | **A** | C++ | MIT | 🟡 stale |
| 11 | [**glog**](google-glog.md) | Google's synchronous C++ stream logger (LOG, CHECK, VLOG); about 4x faster than Boost.Log 1.56 file logging in 2014 tests. | **A** | C++ | BSD-3-Clause | 🔴 abandoned |
| 12 | [**binlog**](morganstanley-binlog.md) | Asynchronous C++ logger writing structured binary logs; about 15x lower p50 call-site latency than async spdlog in Quill's harness. | **A** | C++ | Apache-2.0 | 🔴 abandoned |
| 13 | [**NanoLog (Iyengar111)**](iyengar111-nanolog.md) | Small asynchronous C++11 stream-style logger; lower median caller latency than spdlog async, far behind Quill/fmtlog/PlatformLab NanoLog. | **A** | C++ | MIT (full text in… | 🔴 abandoned |
| 14 | [**lockfreelog**](nluke17-lockfreelog.md) | Tiny header-only C++20 SPSC ring-buffer logger; about 5.3x spdlog async throughput to /dev/null on an Apple M3. | **A** | C++ | no license (study only) | 🟢 active |
| 15 | [**Coost co/log**](idealvin-coost.md) | Asynchronous double-buffered logger inside the coost C++17 base library; first-party numbers claim it beats glog and synchronous spdlog. | **C** | C++ | MIT | 🟢 active |
| 16 | [**zlog**](hardysimpson-zlog.md) | Pure-C, config-file-driven logging library (log4j-style categories and rules); claims about 1000x syslog(3) throughput, unmeasured in the repo. | **C** | C | Apache-2.0 | 🟢 active |
| 17 | [**fastrace**](fast-fastrace.md) | Rust timeline-tracing library (successor to minitrace) whose span creation costs 19-151x less than tokio-tracing in its own benchmark. | **C** | Rust | Apache-2.0 | 🟢 active |
| 18 | [**lwlog**](christianpanov-lwlog.md) | C++17 policy-based logger with allocation-free log calls and an SPSC/MPSC ring-buffer async mode; README claims 2.5-20x over spdlog. | **C** | C++ | MIT | 🟢 active |
| 19 | [**Boost.Log**](boostorg-log.md) | Boost's attribute-based logging framework; beats a flush-every-line std::fstream only under multithreaded or disk-stalled load. | **C** | C++ | BSL-1.0 | 🟢 active |
| 20 | [**low-latency-log**](wang-lp-low-latency-log.md) | Small async Rust file logger with deferred formatting; higher backend throughput than spdlog-rs, fast_log, ftlog in its own harness. | **C** | Rust | Apache-2.0 (some code from… | 🟡 stale |
| 21 | [**llcpp**](blapid-llcpp.md) | Header-only C++17 synchronous binary logger: writes format string plus raw argument bytes, about 4x lower median latency than spdlog. | **C** | C++ | MIT | 🔴 abandoned |
| 22 | [**Serenity Logger**](usafrenzy-serenity-logger.md) | Alpha C++20 synchronous logger (console, file, rotating targets) whose own crude benchmark beats spdlog's single-threaded sinks. | **C** | C++ | MIT | 🔴 abandoned |
| 23 | [**P7Baical (libP7)**](cmakeports-libp7-baical.md) | Binary trace/telemetry logger with deferred formatting; its call-site enqueue beats vsprintf-to-buffer and printf-to-console in its own test. | **D** | C++ | LGPL-3.0-or-later | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
