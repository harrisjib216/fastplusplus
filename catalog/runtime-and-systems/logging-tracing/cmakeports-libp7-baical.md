# P7Baical (libP7)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `LGPL-3.0-or-later` · 🔴 abandoned

> Binary trace/telemetry logger with deferred formatting; its call-site enqueue beats vsprintf-to-buffer and printf-to-console in its own test.

| | |
|---|---|
| **Beats** | printf() to console and vsprintf() to a memory buffer (stdio analog of std::cerr); not a logging library |
| **Claimed result** | Figure on page 11 of Documentation/P7.pdf (Intel i7-870, 16.03.2015, sink = file): 'Printing speed: P7 trace: 5 210 000 per sec; Buffer: 688 000 per sec; Console: 10 000 per sec' (about 7.6x the buffer print and 520x the console print, derived from page data). Text on page 10: i7-870 sends 50 000 traces per second at 0.5% CPU, max \~3.3 million per second to the network server. |
| **Workload** | Speed test in the P7 manual: messages per second for printing a simple formatted string to a memory buffer, to the console, and as a P7 trace message (saved to a file) on an Intel i7-870. |
| **Metric** | throughput |
| **Hardware** | Intel i7-870 (manual figure dated 16.03.2015); manual also lists Intel E8400 and ARM 926EJ numbers for P7 alone |
| **Adoption** | 26 stars (CMake port repo); upstream distribution at baical.net |
| **Last commit** | 2020-02-06 |
| **Links** | [repository](https://github.com/CMakePorts/libp7-baical) · [benchmark](https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Documentation/P7.pdf) |

## Verdict

The author's own speed test on an Intel i7-870 (2015, file sink, compiler and flags not stated) reports 5.21M P7 trace calls per second versus 688k vsprintf calls into a memory buffer and 10k printf calls to the console; the P7 number times only the enqueue into a 64 MB in-memory pool, not formatting or delivery, and no logging library was used as a baseline.

## Use it when

- High-volume diagnostic tracing (hundreds of thousands to millions of messages per second from C/C++) where you can read logs in a dedicated viewer instead of grep.
- You want trace plus numeric telemetry counters (CPU, queue depth, latencies) in one tool, with live streaming to a Baical server on another machine and remote verbosity control.
- Mixed-language processes (C, C++, C#, Python) that should log into one trace stream, or channels shared across modules by name via shared memory.
- Crash-time capture matters: P7_Set_Crash_Handler() installs a handler for segfaults, division by zero and similar faults that calls P7_Exceptional_Flush to save or send buffered records.

## Skip it when

- You need plain-text logs as the primary output: the manual's own sink ranking puts text file at about 0.9M/s, syslog 0.5M/s and console 0.1M/s, versus about 10M/s for the binary file sink, so most of the advantage disappears once P7 has to format text.
- Many threads log to the same channel: every call serializes on two mutexes, unlike the per-thread lock-free queues in Quill, fmtlog or NanoLog.
- You need a maintained dependency: this CMake port stopped at v5.2.0 in February 2020 (issue #4 points to an upstream 5.3.0 that was never merged), and issues about Clang builds (#1), 'unknown type name size_t' (#7) and timestamps jumping back two days on CentOS 7 (#2) are open with no replies.
- LGPL-3.0-or-later is a problem for static linking in closed-source products (the CMake default builds a static library).
- Lossless delivery is required: when the buffer pool is full or the sink is not connected, Trace() returns FALSE and the message is dropped (counted in reject counters), not blocked.

## How it is fast

Deferred formatting with binary records: each call site's format string, file, function, line and module are serialized once as a 'description' (looked up by a fixed trace ID in an array, or by an RB-tree keyed on function and format-string addresses), and every later call writes only a small header (level, CPU, thread ID, sequence, 100 ns timestamp) plus the raw va_arg values, whose types were parsed from the format string once. Records are copied into a preallocated buffer pool and written or sent by a background thread, so the caller never formats or does I/O. The hot path is not lock-free: it takes a per-channel recursive pthread mutex and then the sink's mutex.

## Compared with alternatives

Pick P7 over binlog or Quill when you want the Baical tooling: live network streaming, telemetry graphs next to traces, remote verbosity control and C#/Python clients in the same stream. For a maintained, permissively licensed, multi-thread-scalable logger with text output, Quill or fmtlog are the better choices, and binlog is the closest maintained equivalent of P7's binary deferred-format design.

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib via CMake (BUILD_SHARED_LIBS) |
| **Dependencies** | none beyond the OS: pthread and rt on Linux, ws2_32 on Windows |
| **Minimum toolchain** | CMake 3.10; C++ standard not documented (pre-C++11 style code); MSVC and GCC; Clang build reported failing in Visual Studio (issue #1) |
| **Platforms** | Linux x86/x64 and Windows x86/x64 per the manual; ARM atomics code and ARM 926EJ numbers exist but ARM is not in the supported list |
| **Thread safety** | Thread-safe per the manual; implemented with a recursive pthread mutex per channel plus a mutex in the sink, so concurrent writers to one channel serialize |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in Tests/Speed/Speed.cpp: the P7 loop ignores Trace()'s return value and the client's reject counters, and the test passes no sink, so the default sink is Baical over UDP; run without a reachable Baical server (or without /P7.Sink=File on the command line) every call returns FALSE right after the mutex because the channel is not 'connected', and the dropped calls are reported as P7 throughput.
- The same test sets /P7.Pool=65536 (64 MB, 16x the 4 MB default), so all 100,000 records fit in memory and the timed loop never meets back-pressure from the writer thread; the timer also stops before Release(), so file or network delivery is never timed.
- Speed.cpp measures whole milliseconds: at about 5M calls/s the 100,000-call P7 loop takes about 19-20 ms, so the printed rate moves in 5% steps (100,000/19 ms = 5.26M, /20 ms = 5.00M); the manual's 5,210,000/s figure matches neither, which fits the verifier's finding that the screenshot came from a different build of the test.
- The baselines are not like for like: the buffer case runs vsprintf with 6 arguments including two strings, the P7 case stores 1 integer and defers formatting, and the console case calls printf with the previous formatted line as its format string.

## Known shortcomings

- Manual figure (page 11, i7-870): asynchronous enqueue (5.21M/s) timed against synchronous vsprintf-to-buffer (688k/s, 6 arguments formatted vs 1 for P7) and console printf (10k/s); delivery to file is not timed; baselines are printf, not a logger; compiler and flags unstated; screenshot from a different test build. Upstream baical.net unreachable; the record points at the byte-identical CMakePorts copy. LGPL-3.0-or-later; abandoned since 2020-02-06.
- Harness flaw in Tests/Speed/Speed.cpp: the P7 loop ignores Trace()'s return value and the reject counters, passes no sink (default Baical UDP), so without a server every call returns FALSE after the mutex and dropped calls are counted as throughput; /P7.Pool=65536 (64 MB) holds all 100k records so no back-pressure; whole-ms timer gives 5% steps and the 5,210,000/s figure matches neither 19 nor 20 ms (different build). The manual's own sink ranking (text file \~0.9M/s, console \~0.1M/s vs binary file \~10M/s) shows the advantage is deferred formatting. Hot path is a recursive pthread mutex per channel plus a sink mutex, not lock-free. Port abandoned at v5.2.0 (upstream 5.3.0 never merged, issue #4); open issues #1 Clang, #2 timestamps jump back, #7 size_t.

## Caveats and trade-offs

No head-to-head against any logging library (the manual never names spdlog, glog or log4cplus); the only baselines are printf and vsprintf. The P7 side is a call-site enqueue into a ring buffer drained by a background thread: in Tests/Speed/Speed.cpp the timer stops before the client is released, so delivery to the file is not timed, and it is not comparable to a synchronous console print. The buffer case formats 6 arguments with vsprintf ('[%s][%s][%d][%d][%d] ... iteration is %d') while the P7 trace call passes 1 argument (P7 captures file, function, line, thread and processor as binary metadata and defers formatting); the console case calls printf with the already formatted buffer as the format string, so it prints the previous line unformatted and without a newline, i.e. it times raw terminal output. The shipped Speed.cpp prints its results as text, while the page-11 figure plots 'To P7trace/To Buffer/To Console' counters (Count 1000) in the Baical viewer and quotes its Max column, so the 2015 screenshot came from a different build of the test. The page-10 figures (50 000 traces/s at 0.5% CPU, \~3.3 million/s max on i7-870) were measured with /P7.Sink=Baical over loopback, not to file. Compiler and flags are unstated; numbers are first-party and from 2015. The manual and Speed.cpp in CMakePorts/libp7-baical are byte-identical to the Faramax/libp7-baical mirror (a 0-star fork of Mixaill/libp7-baical). The upstream site baical.net was not reachable; the CMakePorts port's last commit was 2020-02-06 (v5.2.0) while upstream may have newer releases. Claim words on the list ('high-speed', 'minimal CPU and memory') match the manual's speed chapter. [retier] First-party enqueue-only measurement with a flawed harness (ignores rejected calls, 64 MB pool, no delivery timed, whole-ms timer); baselines not like for like (vsprintf with 6 args vs one deferred integer). Abandoned port at v5.2.0; LGPL-3.0-or-later.

Binary trace format needs the Baical server/viewer (or P7 file reader) to read logs; asynchronous delivery through a client-side buffer pool; C, C++, C# and Python clients; LGPL-3.0-or-later; no dependencies.

## Maintenance

Abandoned port (last commit 2020-02-06, v5.2.0, upstream 5.3.0 never merged, six open issues without replies) but self-contained, dependency-free and copyable under LGPL-3.0-or-later; treat the speed figures as first-party and the benchmark as a best-case enqueue measurement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** Manual page 11 (rendered screenshot) shows 'Printing speed: P7 trace: 5 210 000 per sec; Buffer: 688 000 per sec; Console: 10 000 per sec' on an Intel i7-870 dated 16.03.2015, and page 10 gives the 50 000 traces/s at 0.5% CPU and \~3.3 million/s max figures; the harness Tests/Speed/Speed.cpp is public and the CPU is named, but compiler and flags are never stated and the numbers are first-party, so C.
- **Retiered** C to D: The only speed figures come from Tests/Speed/Speed.cpp, which ignores Trace()'s return value and the reject counters and passes no sink, so without a reachable Baical server every call fails after the mutex and dropped calls are reported as throughput; the pool is sized to hold every record, the timer stops before delivery, and the published 5,210,000/s figure matches no whole-millisecond reading of that loop (different build). Directional only.
- **Verifier notes:** Numbers verified on the rendered page-11 figure and page-10 text; benchmark_url moved to the identical copy in the entry's own repo (cmake branch). Main shortcomings: only printf/vsprintf baselines, async enqueue timed against synchronous formatting and console output, unequal argument counts, figure from a different test build, compiler/flags unstated, abandoned since 2020. License LGPL-3.0-or-later confirmed from LICENSE.md and the 'version 3.0 ... or any later version' source headers.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Shortcomings recorded by:** vendor manual figure (verifier); enricher (wave 11)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Faramax/libp7-baical/master/Documentation/P7.pdf>
  - <https://raw.githubusercontent.com/Faramax/libp7-baical/master/Tests/Speed/Speed.cpp>
  - <https://github.com/Faramax/libp7-baical>
  - <https://github.com/CMakePorts/libp7-baical>
  - <https://github.com/CMakePorts/libp7-baical/commits>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/HEAD/README.md>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/HEAD/Tests/Speed/Speed.cpp>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Documentation/P7.pdf>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Headers/P7_Client.h>
- **Sources the enricher read:**
  - <https://github.com/CMakePorts/libp7-baical>
  - <https://github.com/CMakePorts/libp7-baical/commits/cmake>
  - <https://github.com/CMakePorts/libp7-baical/issues>
  - <https://github.com/CMakePorts/libp7-baical/issues/1>
  - <https://github.com/CMakePorts/libp7-baical/issues/2>
  - <https://github.com/CMakePorts/libp7-baical/issues/4>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/README.md>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/LICENSE.md>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/CMakeLists.txt>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Documentation/P7.pdf>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Tests/Speed/Speed.cpp>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Headers/P7_Client.h>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Headers/P7_Trace.h>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Headers/GTypes.h>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Sources/Client.cpp>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Sources/Trace.cpp>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Sources/ClFile.cpp>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Sources/ClBaical.cpp>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Shared/Lock.h>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Shared/Platforms/Linux_x86/PLock.h>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Shared/Platforms/Linux_x86/PAtomic.h>
  - <https://raw.githubusercontent.com/CMakePorts/libp7-baical/cmake/Shared/Platforms/Linux_x86/PTime.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/cmakeports/libp7-baical`) · [data/wave11/enrich/raw/github_com_cmakeports_libp7_baical.json](../../../data/wave11/enrich/raw/github_com_cmakeports_libp7_baical.json) (enrichment confidence 0.7)

</details>
