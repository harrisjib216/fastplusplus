# magic-trace

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `OCaml` · `MIT` · 🟢 active

> Intel PT tracer recording every function call at about 40 ns resolution, with 2-10% overhead, below perf -g call-graph sampling.

| | |
|---|---|
| **Beats** | perf -g (and perf sampling flame graphs) |
| **Claimed result** | 2%-10% slowdown (most applications closer to 2%); a snapshot pauses the app for about 10 microseconds; overhead is lower than perf -g and higher than perf -glbr (qualitative, no perf numbers given); the README states about 40 ns resolution. |
| **Workload** | Intel Processor Trace based capture of every function call in a snapshot window (about 10 ms) around a chosen function, versus sampled stacks. |
| **Metric** | latency |
| **Hardware** | Requires Intel CPU with Processor Trace; specific model not stated on the page |
| **Adoption** | 6.3k stars; Jane Street |
| **Last commit** | 2026-05-29 |
| **Links** | [repository](https://github.com/janestreet/magic-trace) · [benchmark](https://github.com/janestreet/magic-trace/wiki/Overhead) |

## Verdict

The project wiki (first-party, no benchmark code, CPU model or workload named) says traced applications run 2-10% slower, mostly near 2%, with a \~10 us stall per snapshot, and that overhead is lower than perf -g and higher than perf -glbr. The perf comparison is qualitative only; the \~40 ns resolution comes from the README.

## Use it when

- Tail-latency hunting in production: put a stop-indicator call where a request or scheduler cycle runs long, and see every call that led up to it.
- Short functions (tens of ns to a few us) that a sampling profiler never catches, for example the 70 ns case in the README testimonials.
- Native C, C++, Rust or OCaml binaries on bare-metal Intel Skylake-or-newer Linux hosts (tested on Skylake, Ice Lake, Tiger Lake).
- Pre-crash history: snapshot at program exit to see the last milliseconds of control flow, not just the final stack.

## Skip it when

- AMD, ARM or non-Linux machines, and most VMs (KVM with kernel 5.0+ needed for guests): Intel PT only.
- Whole-run aggregate profiles or flame graphs over minutes: it only keeps a \~10 ms window per snapshot; use perf record or a sampling profiler.
- Memory-bandwidth-bound workloads: PT output competes for bandwidth, and saturation leads to paused tracing and decode errors.
- Code paths that rely on exceptions (unsupported per the platforms wiki), or Python beyond its C frames.

## How it is fast

Intel PT has the CPU write a compressed branch trace to memory in hardware, so there is no per-call instrumentation and no interrupt-driven stack walk like perf -g's frame-pointer or DWARF unwinding. magic-trace drives perf in snapshot mode and only decodes the ring buffer when a trigger fires, so the steady-state cost is mainly memory bandwidth (hundreds of Mbps) and each snapshot stalls the app for about 10 us. Timing resolution is configurable, trading detail for lower bandwidth.

## Compared with alternatives

Pick it over Tracy or funtrace when you cannot add instrumentation or recompile and need every call in a short window; pick Tracy or funtrace for full-run timelines with explicit zones, or Coz when the question is which code to optimize for end-to-end throughput.

## Integration

| | |
|---|---|
| **Form** | prebuilt binary or .deb (OCaml source, built with dune) |
| **Dependencies** | Linux perf with Intel PT support (perf 5.4+ for snapshot on exit, 5.5+ for better kernel tracing); kernel 3.10+; root for -trace-include-kernel |
| **Minimum toolchain** | none to use (release binary); building needs OCaml per the wiki build instructions |
| **Platforms** | Linux x86-64 on Intel Skylake or newer (Broadwell works with \~1 us resolution); no AMD or ARM |
| **Thread safety** | not documented; open issues report split traces without --per-thread (#236) and stop-indicator trouble in multi-threaded apps (#274) |
| **Drop-in for the baseline** | partial: same attach-to-a-pid workflow as perf and it drives perf underneath, but it produces snapshot timelines, not sampled call-graph profiles |

## Gotchas

- The tracee pauses about 10 us per snapshot, so trigger after the user-visible work finishes, as the wiki advises.
- Decode errors usually mean PT saturated memory bandwidth; lowering timing resolution reduces overhead.
- Fragile against perf output format changes: open issues include perf parsing exceptions (#324, #311, #257) and a perf-version cpu-clock incompatibility (#283).
- Kernel frames show as '[untraced]' unless run as root with -trace-include-kernel; Docker containers can break symbol lookup through /proc/pid/exe (#307).

## Known shortcomings

- Intel PT snapshot tracer, not embeddable C++ code. Linux only, Skylake or newer, no AMD or ARM, most VMs excluded, exceptions unsupported. 42 open issues, including perf parse breakage (324, 311, 283) and multi-thread trouble (236, 274). The perf -g comparison is qualitative only.

## Caveats and trade-offs

First-party wiki, no benchmark code or CPU model; it is a different kind of tool (high-resolution trace) than perf sampling, so the 'faster' claim is only about overhead versus perf -g. Jane Street blog post was not opened.

Intel PT only (no AMD, limited in VMs), snapshots only the last few milliseconds, uses memory bandwidth (hundreds of Mbps), decode errors if bandwidth saturates; needs perf and kernel support. Tool is OCaml but profiles C/C++ native binaries.

## Maintenance

Actively maintained by Jane Street (MIT, 6.3k stars, last commit 2026-05-29), shipped as release binaries; usable as a tool, not as code to embed in a C++ project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The wiki Overhead page states a 2%-10% slowdown (most apps closer to 2%), a pause of about 10 microseconds per snapshot, and overhead lower than perf -g but higher than perf -glbr. The perf comparison is qualitative only, with no benchmark code or CPU, so C.
- **Verifier notes:** MIT, 6.3k stars, last commit 2026-05-29, so active. The comparison with perf -g has no numbers; the 40 ns figure is from the README, not the wiki page.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/janestreet/magic-trace>
  - <https://github.com/janestreet/magic-trace/commits>
  - <https://github.com/janestreet/magic-trace/wiki/Overhead>
  - <https://raw.githubusercontent.com/janestreet/magic-trace/HEAD/README.md>
  - <https://raw.githubusercontent.com/janestreet/magic-trace/HEAD/LICENSE.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/janestreet/magic-trace/HEAD/README.md>
  - <https://github.com/janestreet/magic-trace/wiki/Overhead>
  - <https://github.com/janestreet/magic-trace/wiki/Supported-platforms,-programming-languages,-and-runtimes>
  - <https://github.com/janestreet/magic-trace/issues?q=is%3Aissue+is%3Aopen>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/janestreet/magic-trace`) · [data/wave11/enrich/raw/github_com_janestreet_magic_trace.json](../../../data/wave11/enrich/raw/github_com_janestreet_magic_trace.json) (enrichment confidence 0.75)

</details>
