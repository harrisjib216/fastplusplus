# zlog

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Logging and tracing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Pure-C, config-file-driven logging library (log4j-style categories and rules); claims about 1000x syslog(3) throughput, unmeasured in the repo.

| | |
|---|---|
| **Beats** | syslog(3) with rsyslogd |
| **Claimed result** | 'high-performance, 250'000 logs/second on my laptop, about 1000 times faster than syslog(3) with rsyslogd' (verbatim from the README feature list). |
| **Workload** | Log calls per second on the author's laptop, compared with syslog(3) delivering to rsyslogd (workload and message size not stated in the README). |
| **Metric** | throughput |
| **Hardware** | unnamed 'laptop' (no CPU model) |
| **Adoption** | 2.6k stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/HardySimpson/zlog) · [benchmark](https://github.com/HardySimpson/zlog) |

## Verdict

The only comparison with the baseline is an unmeasured README sentence: 250,000 logs/s 'on my laptop' and about 1000x syslog(3) through rsyslogd, with no CPU, compiler, flags, message size or rsyslogd setup; the repo's own timings (doc/performence.txt, -O2, 10 threads writing 1,000,000 lines to one file) compare zlog versions with each other and with raw write(2), never with syslog.

## Use it when

- C (or C-compatible C++) services on Linux, macOS or other POSIX systems that need text log files with per-module levels, several outputs and rotation, configured at deploy time rather than compiled in.
- Several processes writing to the same log file with rotation: zlog coordinates rotation across processes with a lock file and appends with O_APPEND.
- Replacing syslog(3) or printf in an application that logs at up to a few hundred thousand lines per second and can afford one or two syscalls per line.
- You want a mature, permissively licensed (Apache-2.0) C library that is still maintained, with CI on x86-64, arm64, 32-bit ARM, Alpine/musl and macOS including TSan and ASan builds.

## Skip it when

- Latency-sensitive hot paths: each synchronous call formats the whole line and does stat(2) plus write(2); doc/performence.txt implies about 1.8-4.5 us of user+sys CPU per line for v1.1.0-v1.1.1 (derived from page data), while the deferred-formatting C++ siblings enqueue in tens of nanoseconds.
- Durability per line: the User's Guide shows the 1,000,000-line press test going from 1.806 s to 41.995 s with 'fsync period = 1K', and O_SYNC files ('-' prefix) are described as 'painfully slow'.
- Real-time threads: every log call takes a pthread rwlock for reading, and issue #196 (priority inversion, open since 2021) reports that wrapping zlog in a priority-inheritance mutex cost significant performance.
- Windows: the main repo targets POSIX only; Windows support exists in a separate fork (lopsd07/WinZlog).
- Untrusted configuration files: issue #206 reports an ASan stack-buffer-overflow in zlog_conf_build_with_file and is still open.

## How it is fast

It stays in the calling process and writes directly: each thread has its own preallocated message buffer (pthread TLS), the format string is compiled at init into a list of specs, the formatted time string is cached per thread and per second (strftime was the profiled bottleneck in issue #3), and each line goes out with one write(2) on an O_APPEND descriptor, with no daemon round trip as syslog(3) to rsyslogd needs. Every call still takes a global pthread rwlock for reading and, for static files, calls stat(2) on the log path to detect external rotation. An optional writer thread (global option use_writer_thread = 1, queue size fifo_size) moves the write off the calling thread, but the message is still formatted with vsnprintf on the caller.

## Compared with alternatives

Pick zlog when the code base is C and you want configuration-file-driven routing, rotation and multi-process file sharing with a permissive licence; for raw call-site latency, Quill, fmtlog or NanoLog (C++) are one to two orders of magnitude faster, and P7 offers a C interface with deferred binary formatting if you can use its viewer.

## Integration

| | |
|---|---|
| **Form** | shared lib and static lib (CMake targets zlog::zlog and zlog::zlog_s, or plain Makefile), plus pkg-config file |
| **Dependencies** | none beyond POSIX (pthread) and a C99-conforming vsnprintf |
| **Minimum toolchain** | CMake 3.12 (or make); compiled with -std=c99 but includes &lt;stdatomic.h&gt;, so a GCC or Clang that ships C11 atomics; C header usable from C++ |
| **Platforms** | Linux (x86-64, arm64, 32-bit ARM, musl), macOS, AIX per the author; other POSIX systems untested; Windows only through the WinZlog fork |
| **Thread safety** | Thread-safe (global rwlock plus per-thread buffers); process-safe rotation via a lock file; fork() in a threaded process fixed in September 2026 |
| **Drop-in for the baseline** | no |

## Gotchas

- The '1000 times faster than syslog(3)' figure has no measurement anywhere in the repo: test/test_press_syslog.c exists but no timing for it is published, and the rsyslogd configuration (for example whether its file action syncs each line) is not documented, so the ratio cannot be reproduced or attributed.
- The two press harnesses are not symmetric: the zlog side runs N processes with M threads each and writes a full timestamped line (about 85 bytes, format '%d.%us %-6V %p:%T:%F:%L %m%n'), while the syslog side runs N single-threaded processes that send the bare string 'loglog' through /dev/log.
- The README's 250,000 logs/s does not match doc/performence.txt, whose 1 process x 10 threads x 100,000 lines runs imply about 430,000 lines/s for v1.1.1 (2.334 s) and about 900,000 for v1.1.0 (1.107 s) (derived from page data); all figures date from the 2012 1.x versions, with no CPU or compiler named.
- In writer-thread mode a full FIFO drops the message with an error (the producer's full counter is incremented) instead of blocking, and the default queue is 1024 \* 4 bytes; the default synchronous mode instead blocks in write(2).

## Known shortcomings

- The '250,000 logs/second, 1000 times faster than syslog(3) with rsyslogd' claim is a README sentence only: no syslog timing anywhere, unnamed laptop, and the syslog and zlog press harnesses are not symmetric (processes vs threads); the log4c claim has no numbers. Apache-2.0 (the list said LGPL-2.1).
- The '1000x faster than syslog' claim was never measured; the press harnesses are asymmetric (zlog writes an 84-byte full line across procs x threads, syslog logs a bare 'loglog' from single-thread procs) and the rsyslogd config is undocumented. README's 250k/s disagrees with doc/performence.txt (\~430k/s v1.1.1, \~900k/s v1.1.0, derived); all numbers date from 2012. Each synchronous call takes a global rwlock, a stat(2) and a write(2). The undocumented use_writer_thread mode drops records when its 4 KB FIFO fills. Open issues #196 priority inversion, #206 ASan overflow in the conf parser. Apache-2.0 since 1.2.17 (LGPL-2.1 before); active, v1.2.20 Sept 2026.

## Caveats and trade-offs

First-party sentence with no methodology: no CPU, compiler, flags, message size or rsyslogd configuration, and no published syslog timing anywhere in the repo (README, doc/UsersGuide-EN.md, doc/performence.txt). The repo ships load generators test/test_press_syslog.c and test/test_press_zlog.c; both log the 6-byte string 'loglog', but the syslog harness forks N processes that each call syslog(3) in a loop while the zlog harness forks processes that each run M threads, so the two sides are not symmetric. doc/performence.txt ('using makefile.linux for test, libzlog compile in O2') gives only zlog-vs-zlog and zlog-vs-direct-write timings (1 process x 10 threads x 100000 lines, 'time ./test_press_zlog 1 10 100000': v1.1.1 2.334s, v1.1.0 1.107s, v1.0.3 6.349s; direct write(2) test_press_write 1.872s), which suggests about 430k lines/s for v1.1.1 (derived from page data) and no syslog column; the User's Guide shows the same harness at 1.806s and slowing to 41.995s with an fsync period of 1K. The README's second claim, 'faster, safer and more powerful than log4c', has no numbers. The list entry tagged LGPL-2.1-only; the current repo is Apache-2.0 (LICENSE file and source headers such as src/zlog.h), so older releases may carry the older licence. [retier] '1000x faster than syslog' is unmeasured; press harnesses asymmetric (84-byte lines across procs x threads vs bare 'loglog' single-thread), rsyslogd config undocumented; README 250k/s vs doc/performence.txt \~430k/s (v1.1.1) and \~900k/s (v1.1.0), all 2012. Sync path takes a global rwlock, stat(2) and write(2) per call; use_writer_thread drops on a full 4 KB FIFO.

Pure C, config-file driven (rules, categories, formats), thread-safe and process-safe file rotation, MDC; calling it from C++ needs only the C header; heavier than printf because every call goes through category and rule lookup.

## Maintenance

Active again (version 1.2.20, a burst of fixes in September 2026 including fork safety, zlog_fsync and a non-hanging zlog_fini_try) and Apache-2.0 since 1.2.17 (LGPL-2.1 before), so it is safe to adopt; treat the speed claim as first-party and unreproduced.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README feature list says verbatim 'high-performance, 250'000 logs/second on my laptop, about 1000 times faster than syslog(3) with rsyslogd' (repeated in doc/UsersGuide-EN.md) with no CPU, compiler, flags or syslog timing published; first-party numbers without methodology, and a &gt;50x gain with unstated flags is capped at C anyway.
- **Verifier notes:** Claim and metadata check out (Apache-2.0, 2.6k stars, 774 forks, last commit 2026-09-29, active). Main shortcomings: 1000x-vs-syslog figure is an unmeasured README sentence on an unnamed laptop, asymmetric press harnesses, no log4c numbers.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher (wave 11)
- **Pages the verifier opened:**
  - <https://github.com/HardySimpson/zlog>
  - <https://github.com/HardySimpson/zlog/commits>
  - <https://github.com/HardySimpson/zlog/tree/master/doc>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/doc/performence.txt>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/doc/UsersGuide-EN.md>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/zlog.h>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_zlog.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_syslog.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_write.c>
- **Sources the enricher read:**
  - <https://github.com/HardySimpson/zlog>
  - <https://github.com/HardySimpson/zlog/commits/master>
  - <https://github.com/HardySimpson/zlog/tree/master/.github/workflows>
  - <https://github.com/HardySimpson/zlog/issues?q=is%3Aissue+performance+OR+slow+OR+deadlock+OR+crash>
  - <https://github.com/HardySimpson/zlog/issues/3>
  - <https://github.com/HardySimpson/zlog/issues/196>
  - <https://github.com/HardySimpson/zlog/issues/206>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/README.md>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/Changelog>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/.github/workflows/cmake-multi-platform.yml>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/doc/performence.txt>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/doc/UsersGuide-EN.md>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/zlog.h>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/zlog.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/conf.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/rule.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/rule.h>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/spec.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/buf.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/event.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/src/category.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_zlog.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_zlog.conf>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_zlog2.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_zlog2.conf>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_syslog.c>
  - <https://raw.githubusercontent.com/HardySimpson/zlog/HEAD/test/test_press_write.c>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/hardysimpson/zlog`) · [data/wave11/enrich/raw/github_com_hardysimpson_zlog.json](../../../data/wave11/enrich/raw/github_com_hardysimpson_zlog.json) (enrichment confidence 0.75)

</details>
