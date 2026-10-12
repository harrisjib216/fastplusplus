# libriscv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Embeddable RISC-V sandbox for game scripting; 2 ns host-to-guest calls versus about 150 ns into LuaJIT, mixed on compute.

| | |
|---|---|
| **Beats** | LuaJIT (JIT mode); README also compares against wasmtime, wasm3 and Luau |
| **Claimed result** | Gist, libriscv with libtcc binary translation vs LuaJIT, medians over 200x1200 samples with call overhead subtracted for both: call overhead 2 vs 156 ns; call args=8 7 vs 197 ns; syscall args=0 10 vs 174 ns; syscall string 13 vs 186 ns; complex syscall 50 vs 873 ns; integer math 6 vs 52 ns; array append 5 vs table append 18 ns; memcpy 18 vs 87 ns; memset 15 vs 67 ns; micro threads 102 vs coroutines 166 ns; sieve(10M) 80 vs 123 ms; fib(40) 66 vs 66 ns (equal); taylor(1K) 2234 vs 858 ns (LuaJIT about 2.6x faster, derived from page data). README: VM function call 3 ns vs \~50-150 ns for other solutions; libriscv can call a 3x-sinf function 5.25-7.25 times before wasmtime has called it once. |
| **Workload** | Embedded scripting micro-benchmarks run in the sandbox as RISC-V guest code with binary translation, versus the same tasks as LuaJIT scripts: host-to-guest call overhead, syscall cost, integer math loops, sieve of 10M. |
| **Metric** | latency |
| **Hardware** | Gist does not state the CPU; the README names a Ryzen 7950X for its other charts (CoreMark 38223 vs 41382 native, about 92%). |
| **Adoption** | 1.1k stars; same organisation maintains godot-sandbox (487 stars) |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/libriscv/libriscv) · [benchmark](https://gist.github.com/fwsGonzo/9132f0ef7d3f009baa5b222eedf392da) |

## Verdict

In the author's gist (October 2025, medians of 200x1200 samples, call overhead subtracted on both sides, CPU, compiler and LuaJIT version not stated), libriscv with libtcc binary translation calls a guest function in 2 ns versus 156 ns for LuaJIT and handles a zero-argument syscall in 10 versus 174 ns, but compute rows are mixed: sieve(10M) 80 versus 123 ms (about 1.5x), fib(40) tied at 66 ns, taylor(1K) 2,234 versus 858 ns (LuaJIT 2.6x faster). The README's 92%-of-native CoreMark (38,224 vs 41,382 on a Ryzen 7950X) is from ahead-of-time embedded binary translation, not from the libtcc mode used for the LuaJIT comparison.

## Use it when

- Game or engine scripting where the host makes many short calls into scripts per frame and per-call latency (tens of ns versus hundreds) matters more than peak compute.
- Sandboxing untrusted, precompiled code from compiled languages with hard instruction and memory limits, pause/resume, preemption and serialisable VM state.
- Platforms that forbid executable memory (consoles, iOS-style mobile): ship the interpreter plus an embedded ahead-of-time translation compiled into the binary.
- Many short-lived instances: execute segments are shared between machines and copy-on-write forking supports ephemeral per-request VMs.

## Skip it when

- Compute-heavy scripts in production: SECURITY.md says not to use binary translation in production yet, and the interpreter runs CoreMark at about 3,559 iterations/s versus 41,382 native on a Ryzen 7950X (under 10%, derived from page data); LuaJIT also wins taylor(1K) by 2.6x even against libtcc translation.
- You want a dynamic, hot-reloadable scripting language for designers: scripts need a RISC-V cross-compiler (GCC 10-14 riscv64-linux-gnu, or GCC 16+ for -march=rva23u64) and a rebuild of the ELF.
- Running general Linux programs that need filesystem or socket access in a hostile setting: those Linux system call emulations are flagged not for production, and Linux syscall coverage is an explicit non-goal.
- Bulk memory work done in guest code: the same gist shows guest-side naive memcpy at 586 ns versus 87 ns for LuaJIT; only the host-accelerated syscall variants win.
- Go guests or Zig-built C++ guests: open issues report high memory footprint with Go (#264) and C++ exceptions failing on Zig toolchains (#267).

## How it is fast

Call latency is low because a vmcall only writes argument registers and jumps into an already-decoded execute segment, returning through a dedicated fast-exit address, with no stack marshalling through a dynamic-language C API. Common host operations (memcpy, memset, string handling) are 'accelerated system calls' that run natively on the host. Throughput comes from a computed-goto threaded interpreter over pre-decoded instructions, a flat read-write memory arena that avoids page-table lookups, and binary translation of RISC-V basic blocks into C that libtcc (JIT-like, 2-5x over the interpreter) or a full optimising compiler (ahead of time) turns into native code.

## Compared with alternatives

Pick libriscv over rv32emu, rv8 or RVVM when you embed a sandbox in your own application and care about host-to-guest call latency, instruction limits and pause/resume rather than raw emulation throughput of whole programs; pick rv32emu (tiered JIT) or RVVM when you want to run complete RV32 programs or full systems as fast as possible, or Blink/Box64 when the guest ISA is x86-64 rather than RISC-V.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the interpreter; libtcc (fetched by CMake FetchContent from the fwsGonzo/tinycc 'mob' branch when RISCV_LIBTCC=ON, the default with binary translation) and libdl for translation; optional asmjit backend (experimental); a RISC-V cross-compiler for guest programs |
| **Minimum toolchain** | CMake 3.5+; C++20 (lib/CMakeLists.txt sets cxx_std_20 PUBLIC although the README says C++17 or later); GCC or Clang for the computed-goto threaded dispatch (other compilers fall back to switch dispatch); Clang-cl on Windows |
| **Platforms** | any host for the interpreter (Linux, FreeBSD, macOS, Windows via Clang-cl or MinGW, Android, WebAssembly via Emscripten); libtcc translation on x86-64 and arm64 hosts; guests RV32GCVB, RV64GCVB (RVA23U64), experimental RV128G |
| **Thread safety** | A Machine is not documented as safe for concurrent use (use one per thread or fork per request); sharing execute segments between machines and live-patching background translations are documented as thread-safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- The LuaJIT comparison numbers come from libtcc binary translation and the README's CoreMark 38,224 vs 41,382 native (92%) from an embedded full translation of GCC 13.2 -O3 guest code, yet SECURITY.md says 'Do not use binary translation in production at this time'. In the same CoreMark gist, libtcc mode reaches 18,294 (44% of native), the sandboxed mode with instruction counting 34,473 (83%) and the interpreter 3,559.
- The LuaJIT gist mostly measures call and syscall latency of tiny functions, with call overhead subtracted on both sides and LuaJIT driven through the Lua C API. Its memcpy and memset wins (18 vs 87 ns, 15 vs 67 ns) are host-native accelerated syscalls; guest-code naive memcpy (586 ns) and memset (188 ns) lose to LuaJIT by 6.7x and 2.8x. No CPU, compiler, flags or LuaJIT version is given, and no harness source is linked (not found in rvscript's engine, scripts or programs directories at HEAD).
- The two gists disagree: the interpreted gist (June 2025) reports integer math 3 ns and syscall 3 ns, faster than the binary-translated gist (October 2025: 6 ns and 10 ns), so they were not run on the same build or machine. The interpreted run also loses fib(40) to LuaJIT (156 vs 60 ns) and ties sieve(10M) (133 vs 131 ms).
- The headline 2-3 ns call latency needs a custom fast-exit function: open issue #311 reports the default exit address is created and destroyed on every call, giving much higher call latency unless the host sets memory.set_exit_address() to a guest function. Embedded translations are keyed by a hash of the program and libriscv configuration, and any mismatch silently falls back to the interpreter.

## Known shortcomings

- The LuaJIT comparison is a first-party gist without CPU model, flags or LuaJIT version; the record left out the taylor(1K) loss where LuaJIT is about 2.6x faster, and the wins are mostly host-to-script call latency rather than compute.
- Enricher: SECURITY.md says 'Do not use binary translation in production', yet the LuaJIT numbers come from libtcc translation and the CoreMark 92% from embedded AOT translation (libtcc 44%, interpreter 3,559 vs 41,382 native); the gist memcpy and memset wins are host-accelerated syscalls (guest naive memcpy 586 ns vs LuaJIT 87 ns), the interpreted and binary-translated gists disagree (3 vs 6-10 ns) so they are not the same setup, and the harness source was not found in rvscript. Open issue #311: the default exit address raises call latency.

## Caveats and trade-offs

Gist does not state CPU, compiler flags, LuaJIT version or date (gist last active Oct 2025) and links no harness, so first-party tier C. The wins are mostly host-to-script call and syscall latency, which the author's rvscript README describes as the overhead of calling into Lua/LuaJIT from a game engine; it compares native-compiled RISC-V guest code against Lua scripts, not the same program. LuaJIT is about 2.6x faster on taylor(1K) (858 vs 2234 ns) and equal on fib(40); only sieve(10M) is a classic compute benchmark won (80 vs 123 ms). Benchmarks are hand-picked for game scripting; call overhead is subtracted from every result for both sides. Binary translation needs libtcc or an ahead-of-time translated build; the interpreted libriscv vs LuaJIT comparison is a separate gist. A sandbox/emulator with a JIT-like translator, not a drop-in replacement for LuaJIT as a language implementation. [retier] First-party gist without CPU model, flags or LuaJIT version; the record left out the taylor(1K) row where LuaJIT is about 2.6x faster (1038 vs 7875 ns). The LuaJIT comparison runs libtcc binary translation and the CoreMark 92%-of-native figure embedded AOT translation (libtcc 44%, interpreter 3,559 vs 41,382 native), while SECURITY.md says 'Do not use binary translation in production'. memcpy and memset wins are host-accelerated syscalls (guest naive memcpy 586 ns vs LuaJIT 87 ns). The interpreted and binary-translated gists disagree (3 vs 6-10 ns call latency), so they are not the same setup; harness source not found in rvscript. Open issue #311: default exit address raises call latency. Wins are mostly host-to-script call latency.

Emulator and sandbox for precompiled RISC-V programs rather than a general JIT for a dynamic language; full binary translation needs a C compiler (GCC or TCC) at run time, or the generated C99 can be embedded ahead of time for platforms that forbid executable memory. Needs a RISC-V toolchain to build guest code.

## Maintenance

Actively developed (last commit 2026-09-30, about 3,200 commits, 1.1k stars, BSD-3-Clause; the same organisation maintains godot-sandbox) by essentially one author; the interpreter is the production-safe path, while the binary translation modes behind most of the speed claims are still marked not for production in SECURITY.md.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party gist (libriscv_bintr_vs_luajit.txt) with median/lowest/highest numbers against LuaJIT but no CPU, compiler, flags, LuaJIT version or linked harness code; the related rvscript repo has a BENCHMARK=1 build but the gist does not tie its numbers to it.
- **Verifier notes:** Numbers verified on the gist; the record omitted the taylor(1K) loss (LuaJIT 2.6x faster), now in claimed_speedup and caveats. Metadata checked: BSD-3-Clause, 1.1k stars, not archived or a fork, last commit 2026-09-30.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://gist.github.com/fwsGonzo/9132f0ef7d3f009baa5b222eedf392da>
  - <https://raw.githubusercontent.com/libriscv/libriscv/HEAD/README.md>
  - <https://github.com/libriscv/libriscv>
  - <https://github.com/libriscv/libriscv/commits>
  - <https://github.com/libriscv/libriscv/tree/master/examples>
  - <https://raw.githubusercontent.com/fwsGonzo/rvscript/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/libriscv/libriscv>
  - <https://raw.githubusercontent.com/libriscv/libriscv/HEAD/README.md>
  - <https://raw.githubusercontent.com/libriscv/libriscv/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/libriscv/libriscv/HEAD/docs/INTEGRATION.md>
  - <https://raw.githubusercontent.com/libriscv/libriscv/HEAD/docs/VMCALL.md>
  - <https://raw.githubusercontent.com/libriscv/libriscv/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libriscv/libriscv/HEAD/lib/CMakeLists.txt>
  - <https://github.com/libriscv/libriscv/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/libriscv/libriscv/issues/311>
  - <https://gist.github.com/fwsGonzo/9132f0ef7d3f009baa5b222eedf392da>
  - <https://gist.github.com/fwsGonzo/1af5b2a9b4f38c1f3d3074d78acdf609>
  - <https://gist.github.com/fwsGonzo/7ef100ba4fe7116e97ddb20cf26e6879>
  - <https://github.com/fwsGonzo/rvscript>
  - <https://raw.githubusercontent.com/fwsGonzo/rvscript/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/fwsGonzo/rvscript/HEAD/engine/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fwsGonzo/rvscript/HEAD/engine/build.sh>
  - <https://github.com/fwsGonzo/rvscript/tree/master/engine>
  - <https://github.com/fwsGonzo/rvscript/tree/master/engine/src>
  - <https://github.com/fwsGonzo/rvscript/tree/master/engine/scripts>
  - <https://github.com/fwsGonzo/rvscript/tree/master/engine/scripts/src>
  - <https://github.com/fwsGonzo/rvscript/tree/master/programs>
  - <https://github.com/fwsGonzo/rvscript/tree/master/programs/micro>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/libriscv/libriscv`) · [data/wave12/enrich/raw/github_com_libriscv_libriscv.json](../../../data/wave12/enrich/raw/github_com_libriscv_libriscv.json) (enrichment confidence 0.75)

</details>
