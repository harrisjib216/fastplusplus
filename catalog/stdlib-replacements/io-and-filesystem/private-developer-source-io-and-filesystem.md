# fastcpp::io::buffered_writer (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [I/O and filesystem](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ output buffer that coalesces small writes into 64 KiB flushes instead of issuing write(2) per call.

| | |
|---|---|
| **Beats** | unbuffered write(2) per call (about two write(2) calls per line) |
| **Claimed result** | 67.17x faster per line than an unbuffered writer that makes about two write(2) calls per line (2.93ns vs 196.803ns per line, results/fastest.json row 'buffered_output'). The row labels the baseline 'one write(2) per line', but it makes 40,010 calls for 20,000 lines, i.e. \~98.4ns per write(2) call (derived from page data). The buffered writer cuts the syscall count from 40,010 to 4. |
| **Workload** | bench/bench_doing_less.cpp bench_output writes 20,000 short lines ('line N\n') to /dev/null through io::fd_sink. The winner is fastcpp::io::buffered_writer with a 64 KiB buffer (4 write(2) calls in total). The baseline is the same buffered_writer with a 1-byte buffer: each 'line ' fragment goes straight to write(2), and each number plus newline goes out in the next flush. That is 40,010 write(2) calls in total, about two per line. |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz (AVX2, SSE4.2, BMI2), 4 cores, Ubuntu 24.04 / Linux 6.18, shared cloud VM (bench/bench_syscall.cpp additionally reports this host as 'Not affected' by Meltdown and retbleed, i.e. no KPTI/retpoline tax) |
| **Compiler and flags** | gcc 13.3.0, -O2 -g -DNDEBUG -std=c++20 -march=native (RelWithDebInfo), commit dfa74f2 (run id '2026-09-02-core') |
| **Adoption** | 0 stars (private repository) |
| **Last commit** | 2026-09-04 |
| **Links** | private repository, not published yet |

## Verdict

Writing 20,000 short 'line N' lines to /dev/null took 2.93 ns per line with a 64 KiB buffered_writer and 196.8 ns per line with the same writer at a 1-byte buffer, which makes about two write(2) calls per line (40,010 in total against 4), a 67x ratio. This was one first-party run (gcc 13.3.0, -O2 -march=native, commit dfa74f2) on a shared 4-core Xeon @ 2.10GHz VM running Linux 6.18 without KPTI or retpoline, and no stdio, iostreams or other real-world writer was measured.

## Use it when

- Code that calls write(2) on a raw descriptor once per record (log lines, CSV/TSV rows, protocol or text dumps) and can accept deferred output. This is the case the 67x was measured on.
- Text-output loops dominated by integer fields: write(std::uint64_t) formats directly into the buffer instead of going through snprintf or a std::to_string temporary.
- Batch or offline tools that produce a lot of output and can call flush() at natural boundaries (end of batch, end of run) instead of per line.
- Hosts with KPTI/retpoline mitigations. The repo's bench_syscall notes that these add several hundred nanoseconds to each kernel entry, so each avoided write(2) saves more there than on the benchmark host.
- Projects that already use {fmt}: io::format_line_to formats into a 512-byte stack buffer and appends it to the writer, so fmt-formatted lines need no std::string and no per-line syscall.

## Skip it when

- You already write through stdio (fwrite/printf) or std::ofstream. Those buffer by default, and the benchmark never compared against them, so the 67x does not carry over and any remaining gain is unmeasured.
- Output that must appear or survive promptly (interactive prompts, progress lines, crash-critical logs). Nothing reaches the descriptor until the buffer fills or flush() runs; there is no line-buffered mode and no fsync.
- Code that needs to know a write failed. fd_sink retries short writes but stops silently on the first write(2) that returns 0 or -1 (EINTR, EAGAIN, EPIPE, ENOSPC). file_sink ignores fwrite's return value, and flush() returns void, so data can be lost with no error reported.
- Several threads sharing one writer: the class has no locking, and the repo does not document thread safety.
- Windows, or production code that needs a tested descriptor path. fd_sink compiles only under __unix__ or __APPLE__, and all three buffered_writer unit tests use memory_sink, so fd_sink and file_sink are exercised only by the benchmarks.

## How it is fast

This is ordinary userspace output buffering (write coalescing). Each write is an always-inlined bounds check plus a memcpy into the buffer, and the sink runs once per full buffer, so the benchmark's 20,000 lines take 4 write(2) calls instead of 40,010. Integers are formatted in place with a divide-by-100 two-digit lookup table and a bit_width\*1233&gt;&gt;12 digit-count estimate, so no temporary string is built, and writes at least as large as the buffer skip the copy and go straight to the sink. The gain comes from making fewer kernel entries (about 100-112 ns each on the test host, per bench_syscall), not from faster byte handling.

## Compared with alternatives

No siblings catalogued yet. Within its own repo, pair it with io/format.hpp when you want {fmt} formatting without a per-line std::string, and pick file_sink over fd_sink only when output must interleave with existing stdio writes.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none outside the repo for io/buffered_writer.hpp, which includes fastcpp/core/macros.hpp and fastcpp/string/itoa.hpp; io/format.hpp adds {fmt}. The CMake target fastcpp::fastcpp links all ten vendored libraries (simdjson, yyjson, CRoaring, xsimd, etc.), so copying the three headers is lighter. |
| **Minimum toolchain** | C++20 for this header chain (std::bit_width in string/itoa.hpp); the repo sets C++23 and lists gcc 13+, clang 17+ or MSVC 19.35+ and CMake 3.20+ |
| **Platforms** | any for memory_sink and file_sink; fd_sink needs POSIX (__unix__ or __APPLE__). CI builds on Linux (gcc, clang) and macOS (clang); benchmarked only on x86-64 Linux. |
| **Thread safety** | not documented; no internal synchronization, so use one writer per thread or lock externally |
| **Drop-in for the baseline** | partial — replacing each write(fd, p, n) with writer.write(p, n) on an fd_sink is mechanical, but output is deferred until flush() or destruction and write errors are no longer reported. It does not replace the FILE\* or std::ostream interface. |

## Gotchas

- A capacity below 21 bytes is undefined behaviour. write(std::uint64_t) and write(std::int64_t) flush and then write up to 20 or 21 characters without checking again, and write(char) does the same with a 0-byte buffer. Nothing asserts a minimum, and the repo's own 1-byte-buffer baseline overruns its heap buffer this way.
- The only integer overloads are std::uint64_t and std::int64_t (plus char), so write(42) or write(an unsigned) fails to compile as an ambiguous call. Cast the value as the benchmark does (static_cast&lt;std::uint64_t&gt;(i)). std::size_t is ambiguous too where it is a different type from std::uint64_t, as on macOS.
- The writer stores a raw sink pointer and flushes in its destructor, so the sink must outlive the writer. It can be neither copied nor moved (copy is deleted and no move is declared). If the sink throws during that final flush (memory_sink can throw std::bad_alloc), the program terminates.
- The constructor calls std::make_unique&lt;char[]&gt;(capacity), which allocates and zero-fills the whole buffer. A 64 KiB writer created per short task therefore pays for an allocation and a 64 KiB memset each time, so keep one long-lived writer.

## Caveats and trade-offs

PRIVATE repo, readable only via the authenticated gh CLI (private:developer-source), not publicly browsable -- capped at tier C rather than A despite full compiler/flags/CPU/commit metadata being stated in results/fastest.json, per instruction not to claim tier A for private code. The header's own comment history (include/fastcpp/io/buffered_writer.hpp) originally claimed 'a write(2) costs 1-3us'; bench/bench_syscall.cpp later measured a real write(64B) to /dev/null at \~112ns and a bare kernel entry (getppid) at \~100ns on this unmitigated host -- roughly an order of magnitude below the original claim, because syscall entry cost is dominated by speculative-execution mitigations (KPTI/retpoline), which this host lacks. The repository's own text is explicit that this correction does not weaken the buffered_writer result: the count reduction (40,010 -&gt; 4 syscalls) holds regardless of the per-syscall cost, but the previously advertised per-call nanosecond saving was overstated. The baseline is labelled 'one write(2) per line', but it is buffered_writer with a 1-byte buffer and makes about two write(2) calls per line, so the 67x is measured against a baseline about twice as syscall-heavy as its label. That baseline also writes up to 5 digits plus a newline into its 1-byte heap buffer. This is a heap overrun of up to 5 bytes, which is undefined behaviour. The asan preset builds no benchmarks (FASTCPP_BUILD_BENCHMARKS OFF), so ASan never runs this code. glibc's minimum allocation probably absorbs the overrun, so the timing is likely unaffected. Since commit 6c81a90 the benchmarks are forced to -O3, so a rebuild at HEAD does not reproduce these -O2 flags. Shared cloud VM: results/fastest.json's own caveat states absolute nanoseconds are not stable across runs or CPU-clock changes -- only ratios within one row are meaningful.

Requires an explicit flush() or destructor call to guarantee bytes reach the sink (no per-write durability); the buffer is a heap allocation (std::unique_ptr&lt;char[]&gt;, default 64 KiB) sized once at construction; a write larger than the remaining buffer bypasses buffering and goes straight to the sink. In the same bench file, buffered_writer also beats std::ostringstream heavily for in-memory formatting, but that comparison is not the row captured in results/fastest.json.

## Maintenance

Private repo (private:developer-source, readable only with access; 0 stars, 13 commits, last push 2026-09-04) whose MIT-licensed writer is three small headers and easy to copy, although all 21 CI runs have failed, at HEAD from unrelated code (the xsimd benchmark build, and a parse_i64 UBSan error that halts test_strings before its buffered_writer tests).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** results/fastest.json row buffered_output (run 2026-09-02-core, commit dfa74f2) gives 2.93 vs 196.803 ns per line against unbuffered write(2) to /dev/null, and states gcc 13.3.0, -O2 flags and the Xeon CPU. The code (bench/bench_doing_less.cpp bench_output) is in a PRIVATE repo, so it is not public and cannot be A, and there is no paper or independent suite for B. First-party numbers: C, unchanged. This is a downgrade because the claim mislabels the baseline.
- **Verifier notes:** The numbers (2.93 vs 196.803ns, 67.17x, 40,010 -&gt; 4 calls, \~112ns write and \~100ns getppid) all match results/fastest.json and the README. Tracing buffered_writer with capacity 1 accounts for exactly 40,010 calls: 20,000 'line ' writes, 19,999 per-line flushes, 10 extra flushes for single-digit lines and 1 final flush. So the baseline is \~2 syscalls per line, not one, and I corrected baseline, workload and claimed_speedup. It also overruns a 1-byte heap buffer (UB). Tier C is unchanged; MIT, last commit 2026-09-04 and 0 stars are confirmed.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - private:developer-source
  - private:developer-source/commits/main
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/bench/bench_doing_less.cpp
  - private:developer-source/blob/main/include/fastcpp/io/buffered_writer.hpp
  - private:developer-source/blob/main/include/fastcpp/string/itoa.hpp
  - private:developer-source/blob/main/bench/bench_syscall.cpp
  - private:developer-source/blob/main/bench/bench_harness.hpp
  - private:developer-source/commit/ab9259f
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/LICENSE
  - private:developer-source/blob/main/CMakeLists.txt
  - private:developer-source/blob/main/CMakePresets.json
  - private:developer-source/commits/main/include/fastcpp/io/buffered_writer.hpp
  - private:developer-source/commits/main/bench/bench_doing_less.cpp
- **Sources the enricher read:**
  - private:developer-source
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/LICENSE
  - private:developer-source/blob/main/include/fastcpp/io/buffered_writer.hpp
  - private:developer-source/blob/main/include/fastcpp/io/format.hpp
  - private:developer-source/blob/main/include/fastcpp/string/itoa.hpp
  - private:developer-source/blob/main/include/fastcpp/core/macros.hpp
  - private:developer-source/blob/main/bench/bench_doing_less.cpp
  - private:developer-source/blob/main/bench/bench_syscall.cpp
  - private:developer-source/blob/main/bench/bench_harness.hpp
  - private:developer-source/blob/main/bench/CMakeLists.txt
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/tests/test_strings.cpp
  - private:developer-source/blob/main/tests/test_core.cpp
  - private:developer-source/blob/main/tests/test_containers.cpp
  - private:developer-source/blob/main/tests/test_phf.cpp
  - private:developer-source/blob/main/tests/test_sort.cpp
  - private:developer-source/blob/main/tests/test_simdjson_dispatch.cpp
  - private:developer-source/blob/main/tests/CMakeLists.txt
  - private:developer-source/blob/main/CMakeLists.txt
  - private:developer-source/blob/main/CMakePresets.json
  - private:developer-source/blob/main/.github/workflows/ci.yml
  - private:developer-source/commits/main
  - private:developer-source/commits/main/include/fastcpp/io/buffered_writer.hpp
  - private:developer-source/commits/main/bench/bench_doing_less.cpp
  - private:developer-source/commit/ab9259f
  - private:developer-source/commit/dfa74f2
  - private:developer-source/issues
  - private:developer-source/pull/1
  - private:developer-source/actions
  - private:developer-source/actions/runs/33828450197
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source#io-and-filesystem`) · [data/wave1-phf/enrich/raw/private_developer_source_io_and_filesystem.json](../../../data/wave1-phf/enrich/raw/private_developer_source_io_and_filesystem.json) (enrichment confidence 0.85)

</details>
