# fast-strlen.c (bjourne gist): multi-threaded memchr-based strlen

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C` · `no license` · 🔴 abandoned

> Benchmark-stunt strlen: finds an upper bound by deliberately faulting, then runs memchr on every core; 2.6x over single-threaded libc strlen.

| | |
|---|---|
| **Beats** | libc strlen (labelled 'strlen' in the gist's printed output; libc implementation and version not stated, glibc presumed on Linux) |
| **Claimed result** | Xeon W-2245 @ 3.90GHz, gcc 13.1.1, 2.00GB buffer scanned 10 times: threaded_strlen 43.56 GB/s (0.46 s) vs libc strlen 16.84 GB/s (1.19 s), about 2.6x (derived from page data). Xeon E5-2650 v4 @ 2.20GHz, gcc 9.4.0, 4.00GB header: 34.09 GB/s (1.17 s) vs 8.76 GB/s (4.56 s), about 3.9x (derived from page data), measured on an unpublished variant of the code. threaded_strlen uses sysconf(_SC_NPROCESSORS_ONLN) threads, against single-threaded libc strlen. |
| **Workload** | strlen of one posix_memalign'd 2e9-byte buffer filled with 'A' and NUL-terminated at the last byte (length 1999999999), scanned 10 times per variant, with each call's result asserted equal to the first. The E5-2650 v4 block in the header reports a 4.00GB scan with length 4000007776, which does not match N_BUF in either gist revision. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2650 v4 @ 2.20GHz; Intel Xeon W-2245 @ 3.90GHz |
| **Compiler and flags** | gcc -O3 -march=native fast-strlen.c -lpthread -o fast-strlen (gcc 9.4.0 and gcc 13.1.1); gist says to use gcc because clang optimizes away parts of the benchmark |
| **Adoption** | 7 stars, 0 forks (gist) |
| **Last commit** | 2023-07-13 |
| **Links** | [repository](https://gist.github.com/bjourne/02df9abb0712584da3a74cb325e4fbe6) · [benchmark](https://gist.github.com/bjourne/02df9abb0712584da3a74cb325e4fbe6) |

## Verdict

On a Xeon W-2245 with gcc 13.1.1 -O3 -march=native, ten strlen calls on a 64-byte-aligned 2 GB buffer of 'A' with the NUL at the last byte took 0.46 s with threaded_strlen and 1.19 s with libc strlen (43.56 vs 16.84 GB/s, about 2.6x, derived from page data). Every returned length was asserted equal. The libc version is not named, and the gain comes from using all online CPUs against one.

## Use it when

- Benchmark games such as the '{n} times faster than C' challenge, where strlen over one huge DRAM-resident buffer dominates the run time.
- As a demonstration that a multi-gigabyte scan on one core tops out near the core's memory bandwidth (about 17 GB/s for every single-thread variant on the W-2245), and that splitting the scan across cores raises the total.
- As a template for a parallel memchr fan-out when the buffer length is already known: keep the chunked memchr threads and drop the SIGSEGV probe.
- Teaching material on SIGSEGV and si_addr probing tricks on Linux with glibc.

## Skip it when

- Any production code. The author says it 'heavily relies on undefined behavior and shouldn't be used for anything other than beating benchmarks'.
- Short or medium strings. Every call does two sigaction calls, creates one probe thread and nproc worker threads, and mallocs two arrays, and only a 2 GB string was measured.
- Multithreaded programs or libraries. It swaps the process-wide SIGSEGV handler, writes a global fault address and occupies every online CPU while it runs.
- Non-POSIX targets, or builds with -DNDEBUG (see gotchas).
- When you want a single-thread speedup. The gist's own AVX2 (15.36 GB/s) and AVX-512 (16.36 GB/s) loops do not beat libc strlen (16.84 GB/s) on the W-2245.

## How it is fast

A helper thread reads s[4 MB], s[8 MB] and so on in 4 MB steps until it hits unmapped memory. The SA_SIGINFO handler records si_addr and calls pthread_exit, which gives an upper bound on the length without scanning. That range is then cut into ceil(n/nproc) chunks, and sysconf(_SC_NPROCESSORS_ONLN) threads each run libc memchr for '\0' on one chunk. The answer comes from the first chunk that found a zero. The speedup is aggregate memory bandwidth from many cores, not a faster per-core scan.

## Compared with alternatives

Only when one string of several gigabytes must be measured as fast as possible and taking every core is acceptable, as in the Carandiru0 memcpy_threaded gist, the other many-core-versus-one-core entry. For a real single-thread strlen speedup, WojciechMula/toys avx512-string (4.96x vs libc on one core) or the ImGui ImStrlen AVX2 code (1.41x vs the MSVC CRT) are safe to call on ordinary strings.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | pthreads, POSIX sigaction with SA_SIGINFO, libc memchr; immintrin.h for the AVX2 and AVX-512 variants |
| **Minimum toolchain** | GCC (tested with gcc 9.4.0 and 13.1.1, -O3 -march=native -lpthread); the author says clang optimizes away parts of the benchmark |
| **Platforms** | Linux x86-64 as tested (Xeon E5-2650 v4, Xeon W-2245); threaded_strlen needs POSIX signals with si_addr; strlen_avx2 and strlen_avx512 need those ISAs and 32- or 64-byte aligned input |
| **Thread safety** | Not thread-safe: each call replaces the process-wide SIGSEGV handler and writes a global sigsegv_addr, so two concurrent calls, or a real crash in another thread during a call, interfere. |
| **Drop-in for the baseline** | no |

## Gotchas

- Side effects inside assert(). pthread_create and pthread_join in threaded_strlen, clock_gettime in nano_count, posix_memalign in main, and the nine repeated calls in benchmark() (assert(func(s) == cnt)) all sit inside assert(). A -DNDEBUG build, such as CMake's default Release flags, therefore drops the pthread_create, pthread_join, clock_gettime and posix_memalign calls themselves. It then spawns no threads, reads an uninitialised timer and buffer pointer, and times one call while dividing by 10 passes. The published numbers hold only for the stated command line without NDEBUG.
- The probe overshoots by up to 4 MB past the NUL, so worker threads scan mapped memory after the string. Workers whose chunk runs into unmapped memory are killed by the handler through pthread_exit, which is not async-signal-safe. While a call is running, a genuine segfault in any other thread is swallowed the same way.
- The comparison is all online CPUs against a single-threaded libc strlen, and no multithreaded baseline is timed. On the W-2245 the byte loop slow_strlen (16.87 GB/s) matches libc (16.84 GB/s) under gcc 13.1.1 but runs at 2.18 GB/s under gcc 9.4.0. That fits newer GCC rewriting the loop into a strlen call (inference).
- The E5-2650 v4 block (34.09 vs 8.76 GB/s, 3.9x) came from code not in the gist. It reports '4.00GB' and length 4000007776, which is 7,777 bytes more than 4e9, so in that run the terminator was not the buffer's last byte, while both revisions allocate 2e9 bytes and write the NUL at N_BUF-1.

## Known shortcomings

- Uses all online CPUs against a single-threaded libc strlen (W-2245 43.56 vs 16.84 GB/s, 2.6x derived) with undefined-behaviour SIGSEGV probing; the author says it is a benchmark stunt only; the E5-2650 v4 run comes from unpublished code (4.00 GB input). Last revision 2023-07-13, 7 stars.
- Enricher: pthread_create/join, clock_gettime, posix_memalign and the 9 timed repeat calls all sit inside assert(), so a -DNDEBUG build spawns no threads and times one call while dividing by 10 (numbers valid only with the stated command line); the E5 block length 4000007776 means the NUL was not inside the buffer (unpublished code); the slow_strlen jump from 2.18 GB/s (gcc 9.4) to 16.87 (gcc 13) suggests the loop was rewritten to a strlen call (inference). Lead: Const-me gist 3ade77faad47f0fbb0538965ae7f8e04 (AVX2 solution to the owen.cafe strlen benchmark).

## Caveats and trade-offs

Written for fun to beat the '{n} times faster' benchmark. The author says the technique 'heavily relies on undefined behavior' and 'shouldn't be used for anything other than beating benchmarks'. A helper thread probes past the string in 4 MB steps until it hits SIGSEGV, then memchr runs in parallel over chunks up to the faulting address, so on a real heap with mapped memory after a short string it can scan far beyond the string. The speedup comes from using every online CPU (sysconf(_SC_NPROCESSORS_ONLN)) against single-threaded libc strlen, not from a better single-thread algorithm. On the same pages the single-thread vector versions do not beat libc: strlen_avx2 7.86 vs 8.76 GB/s on the E5-2650 v4, and strlen_avx2 15.36 and strlen_avx512 16.36 vs 16.84 GB/s on the W-2245. On the W-2245 the byte-loop slow_strlen (while (s[i++] != '\0');) also prints 16.87 GB/s, level with libc, which fits GCC 12+ loop distribution turning the loop into a strlen call or a memory-bandwidth limit (inference, not confirmed). The E5-2650 v4 numbers came from a code version not in the gist (4.00GB, length 4000007776, while both revisions use N_BUF = 2e9). Both gist revisions are dated 2023-07-13; the 2025-12-27 'last active' date does not reflect a code change. The libc and glibc version are not named. No license.

Not a usable strlen replacement. The fast path deliberately triggers SIGSEGV to find the end of mapped memory, then fans memchr out over all online CPUs; the author says it 'heavily relies on undefined behavior' and exists to beat benchmarks. It only pays off for multi-gigabyte strings and occupies every core. No license.

## Maintenance

Abandoned single-file gist (both revisions dated 2023-07-13) with no licence, so it is legally not copyable; useful only as a reference for the parallel-memchr idea, and the author calls it a benchmark stunt built on undefined behavior.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The gist itself (fast-strlen.c) is the public benchmark, timing libc strlen next to threaded_strlen with the build command (gcc -O3 -march=native ... -lpthread), the compiler version (gcc 13.1.1) and the CPU (Xeon W-2245 @ 3.90GHz) all stated: 43.56 vs 16.84 GB/s, with every variant's returned length asserted equal and printed. The earlier E5-2650 v4 / gcc 9.4.0 block was produced by a version of the code that is not in the gist (it scanned 4.00GB and found length 4000007776, while both revisions set N_BUF to 2e9), so only the W-2245 run is reproducible from published code.
- **Verifier notes:** Numbers and the libc strlen baseline are as recorded and the code is public, so tier A holds on the W-2245 run (2.6x, derived from page data). Shortcomings to record: multi-threaded vs single-threaded baseline, UB-based SIGSEGV probing that the author says is for benchmarks only, E5-2650 v4 run from unpublished code, and single-thread AVX2/AVX-512 variants not faster than libc. last_commit corrected to 2023-07-13 (both revisions), which makes it abandoned under the 3-year rule.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-108 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://gist.github.com/bjourne/02df9abb0712584da3a74cb325e4fbe6>
  - <https://gist.github.com/bjourne/02df9abb0712584da3a74cb325e4fbe6/revisions>
- **Sources the enricher read:**
  - <https://gist.github.com/bjourne/02df9abb0712584da3a74cb325e4fbe6>
  - <https://gist.github.com/bjourne/02df9abb0712584da3a74cb325e4fbe6/revisions>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://gist.github.com/bjourne/02df9abb0712584da3a74cb325e4fbe6`) · [data/wave13/enrich/raw/gist_github_com_bjourne_02df9abb0712584da3a74cb325e4fbe6.json](../../../data/wave13/enrich/raw/gist_github_com_bjourne_02df9abb0712584da3a74cb325e4fbe6.json) (enrichment confidence 0.7)

</details>
