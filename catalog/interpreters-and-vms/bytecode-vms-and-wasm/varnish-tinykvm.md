# TinyKVM (Varnish KVM sandbox; per-request numbers come from libriscv/kvmserver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> KVM-based userspace sandbox that resets a forked Linux program in tens of microseconds, versus milliseconds for process fork or V8 isolates.

| | |
|---|---|
| **Beats** | per-request sandboxing by process fork, a new V8 isolate or WebAssembly (Wasmtime serve); native Linux process as the speed reference. kvmserver's examples/bench.ts has benchmark groups for Wasmtime serve (instance reuse on/off and release), Bun process forking and Node isolated-vm isolate-per-request, but the README publishes no results for them |
| **Claimed result** | Page claim: 'We are able to run this benchmark 1.5-2 orders of magnitude faster than existing solutions' (previous React experiments: 'runtimes in the 10s of milliseconds with WebAssembly' and 'reset times of several milliseconds' for process fork or a new V8 isolate), against 55 us sandbox reset and 80 us total per-request overhead out of 690 us on the React benchmark. Against native it is slower: React page 646 us native vs 695 us ephemeral kvmserver (threads=1); Rust minimal server 13 us native vs 28 us; Deno hello world 17 us vs 50 us. |
| **Workload** | kvmserver (separate repo built on TinyKVM) runs unmodified Linux server executables with a TinyKVM VM reset after each request: Rust minimal HTTP server, Deno hello world and Deno React page rendering; 1000 warmup requests, load generator against native, kvmserver and kvmserver ephemeral. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 7950X (32) @ 5.881Ghz |
| **Compiler and flags** | Deno 2.3.6 run with --v8-flags=--predictable and built with deno compile; Rust server build flags not stated; TinyKVM build flags not stated |
| **Adoption** | 823 stars; used by Varnish (VMOD-TinyKVM) and libriscv/kvmserver |
| **Last commit** | 2026-08-21 |
| **Links** | [repository](https://github.com/varnish/tinykvm) · [benchmark](https://github.com/libriscv/kvmserver) |

## Verdict

libriscv/kvmserver, built on TinyKVM, measured with oha on an AMD Ryzen 9 7950X (Deno 2.3.6 with --v8-flags=--predictable, 1000 warm-up requests, build flags not stated): React page rendering 646 us native vs 695 us with a fresh VM per request (about 80 us overhead, 55 us of it reset), Rust minimal server 13 vs 28 us, Deno hello world 17 vs 50 us. The only baseline in the tables is native, which wins; the claimed win over process fork, V8 isolates and Wasmtime has no published numbers.

## Use it when

- Per-request isolation of a JIT runtime (Deno/V8, LuaJIT-style engines) or native server where Wasm would cost the JIT and fork or isolate creation costs milliseconds; kvmserver's React page renders in 695 us with a fresh VM per request against 646 us native.
- Multi-tenant edge or HTTP-cache workloads that must wipe all guest memory between requests and bound each call with a timeout and memory limit.
- Running prebuilt Linux x86-64 binaries in a sandbox without a cross toolchain or recompilation, on hosts that expose /dev/kvm.
- Large initialised programs (tens to hundreds of MB RSS) forked many times, since forks only allocate pages they write.

## Skip it when

- Tiny handlers where a few tens of microseconds matter: per request it is slower than native (Rust minimal server 13 us native vs 28 us ephemeral, Deno hello world 17 vs 50 us).
- Hosts without /dev/kvm or inside nested virtualization (kvmserver measured about 200 us extra per request nested under QEMU), or non-Linux hosts.
- Multithreaded guests: kvmserver says threads should be avoided and parallelism comes from forking VMs; aarch64 has no SMP, no remote VMs, no dynamic ELF loading tested and no published performance numbers.
- Projects that cannot accept GPL-3.0 (the alternative is a commercial licence from Varnish Software; contributions need a CLA).
- Hostile multi-tenant deployments that assume the isolation is mature: August 2026 fixes closed a host out-of-bounds read (#98), reset_to() leaking signal handlers, cwd, brk and pipe flags across requests (#103), and several syscall-policy bypasses (#94, #95).

## How it is fast

Guest code runs directly on the CPU under hardware virtualization, so compute (including JIT-compiled code such as V8 inside Deno) runs at native speed; only syscalls that need the host exit the VM (about 1 us each per kvmserver). Forks share the master's memory copy-on-write: write faults allocate pages from per-fork memory banks and record them in a sorted dirty-page list, and reset_to() restores just those pages and the registers instead of tearing down an address space, so reset cost scales with pages written (68 KB to 2.3 MB per request in kvmserver's examples). Page copies use AVX2 loads and stores on x86-64, and hugepage-backed loading is optional.

## Compared with alternatives

Pick TinyKVM over Wasm engines such as WAMR, or pre-initialisation with Wizer, when the guest is an existing native or JIT-compiled Linux binary that must keep its JIT and get a fresh state every request. Pick LFI when you can recompile and want in-process isolation at about 7% overhead without KVM, and a Wasm runtime when you need portability beyond Linux/KVM.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_library STATIC) |
| **Dependencies** | Linux KVM (/dev/kvm), pthread, rt; kvmserver adds CLI11 |
| **Minimum toolchain** | C++20 (cxx_std_20), CMake 3.10+; default flags -O2 -g |
| **Platforms** | Linux x86-64 hosts with AVX2 (page copies call avx2_page_duplicate with no runtime CPU check); Linux aarch64 backend partial (static ELF, 4 KiB pages, no SMP) |
| **Thread safety** | One Machine per thread; forks of one master can run in parallel on separate threads (the pooled benchmark keeps one fork per worker thread). Errors are reported with C++ exceptions (MachineException). |
| **Drop-in for the baseline** | no |

## Gotchas

- No benchmark in this repo is published: all per-request numbers are from libriscv/kvmserver (Ryzen 9 7950X, Deno 2.3.6, build flags not stated). Its README tables have fewer rows than the current examples/bench.ts produces, so they come from an earlier harness, and kvmserver pins a TinyKVM from 2026-03-06, before the August 2026 reset and sandbox fixes. The 1.5-2 orders-of-magnitude claim over fork, V8 isolates and Wasm rests on unpublished 'previous experiments'.
- Harness: in kvmserver's bench.ts the Wasmtime serve and Node isolated-vm groups use TCP to 127.0.0.1:8000 with keep-alive and 100 warm-up requests, while the kvmserver ephemeral rows use a Unix socket, a new connection per request and 1000 warm-ups, so a rerun of those groups is not like-for-like. The 'no-tail' row (2 VMs, 1 connection) hides the reset on the idle VM, so its 639 us React figure is latency with the reset off the critical path, not a win over native.
- Harness: TinyKVM's own src/bench.cpp times fork, vmcall and reset with CLOCK_THREAD_CPUTIME_ID, which leaves out time the thread is blocked; the repo's snapshot_bench.cpp says so and switches to CLOCK_MONOTONIC. bench.cpp's 'vmcall + destructor' line also includes the fork loop and warm-up calls, and benchmark_multiple_vms frees its placement-new Machines without destroying them, leaking VMs into later runs.
- Resetting a fork to a different master (allow_reset_to_new_master) comes 'at a steep cost', and alternating VMs on one thread carries a 'serious penalty on Linux' (bench.cpp comments); reset time also grows with open file descriptors and dirty pages.

## Known shortcomings

- All numbers come from the libriscv/kvmserver README (Ryzen 9 7950X, Deno 2.3.6; kvmserver commits are by lrowe, not the TinyKVM author): only native is compared and native is faster (646 us vs 695 us per request; 55 us reset, 80 us of 690 us per request in the sandbox). The '1.5-2 orders of magnitude' over fork, V8 and Wasm is prose with no table; kvmserver examples/bench.ts has Wasmtime serve, Bun fork and Node isolated-vm groups but no published results. Flags unstated.
- Enricher: kvmserver bench.ts gives the Wasmtime and isolated-vm groups TCP keep-alive with 100 warm-ups while the kvmserver rows use a Unix socket, a new connection per request and 1000 warm-ups; the 'no-tail' 639 us hides the reset; the README tables predate the current bench.ts. TinyKVM src/bench.cpp times with CLOCK_THREAD_CPUTIME_ID (the repo's own snapshot_bench.cpp says it hides blocked time), mislabels 'vmcall + destructor' and leaks placement-new Machines. Published numbers predate the August 2026 fixes #103 (reset_to() leaked signal handlers, cwd, brk and pipe flags), #98 (host out-of-bounds read) and #94/#95 (policy bypasses); kvmserver pins TinyKVM at 2026-03-06. x86-64 needs AVX2 (avx2_page_duplicate, no runtime check).

## Caveats and trade-offs

The varnish/tinykvm README and docs (docs/ holds only arm64-feature-matrix.md and seccomp.md) have no benchmark, only the qualitative claim that programs run 'at the same speed' in TinyKVM. The numbers come from libriscv/kvmserver, a separate project in the libriscv organization whose recent commits are by lrowe. They measure kvmserver plus TinyKVM, not TinyKVM alone. kvmserver's examples/bench.ts defines Wasmtime serve, Bun process-forking and Node isolated-vm per-request groups, but the README publishes only native and kvmserver tables. The 1.5-2 orders of magnitude claim over fork, V8 isolates and WebAssembly therefore rests on 'previous experiments' with no published table. Per request it is slower than native (Rust 13 vs 28 us, Deno hello world 17 vs 50 us, React 646 vs 695 us). Compiler flags are not stated. Snippets from search results (HN, Medium; snippet only) mention about 2.5 us snapshot restore and roughly 0.4 ms extra latency for React rendering in an earlier proof of concept; neither was used as evidence. The license is GPL-3.0 only, with a commercial dual licence from Varnish Software, and contributors must sign a CLA.

Needs /dev/kvm and Linux KVM (x86-64, with an arm64 feature matrix in docs); runs ordinary Linux programs at near-native speed with execution timeouts, memory limits and fork of an initialised program into many pre-initialised VMs. Syscalls needing the host cost about 1 us each; nested virtualization adds about 200 us; reset time grows with dirty pages and open file descriptors. Dual licence: GPL-3.0 or a commercial licence from Varnish Software.

## Maintenance

Active (last commit 2026-08-21, 823 stars, recent fuzzing and security hardening by Varnish maintainers) and used in VMOD-TinyKVM and kvmserver, but GPL-3.0 or commercial only and still fixing isolation bugs, so audit before trusting it with hostile tenants.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Every number in claimed_speedup appears in the libriscv/kvmserver README (Rust 13 vs 28 us, Deno hello 17 vs 50 us, React 646 vs 695 us, 55 us reset and 80 us of 690 us overhead) with the CPU model (Ryzen 9 7950X) and Deno 2.3.6 stated. The harness (examples/bench.ts) is public, but the published tables compare only against native. The win over fork, V8 isolates and WebAssembly is a prose claim from 'previous experiments' with no table, and compiler flags are not stated, so the tier is C.
- **Verifier notes:** Record is accurate. Kept at C: the measured baseline is native (and slower), and the claimed win over fork, V8 isolates and Wasm has no published numbers even though kvmserver's bench.ts can run those baselines. A rerun of that harness's Wasmtime, Bun fork and isolated-vm groups would be what could lift it. License GPL-3.0 confirmed from the LICENSE text, 823 stars, last commit 2026-08-21 (fwsGonzo).
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** published results of the existing Wasmtime, Bun and isolated-vm groups; same-transport comparison on current TinyKVM
- **Pages the verifier opened:**
  - <https://github.com/varnish/tinykvm>
  - <https://github.com/varnish/tinykvm/commits>
  - <https://github.com/varnish/tinykvm/tree/master/docs>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/README.md>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/LICENSE>
  - <https://github.com/libriscv/kvmserver>
  - <https://github.com/libriscv/kvmserver/commits>
  - <https://github.com/libriscv/kvmserver/commit/2753a77981094a6a041f6883a4e7edadd8bd99cb>
  - <https://github.com/libriscv/kvmserver/tree/main/examples>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/README.md>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/examples/bench.ts>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/examples/Makefile>
- **Sources the enricher read:**
  - <https://github.com/varnish/tinykvm>
  - <https://github.com/varnish/tinykvm/commits>
  - <https://github.com/varnish/tinykvm/issues?q=is%3Aissue>
  - <https://github.com/varnish/tinykvm/issues/103>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/README.md>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/docs/seccomp.md>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/docs/arm64-feature-matrix.md>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/src/bench.cpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/src/snapshot_bench.cpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/src/syscall_bench.cpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/tinykvm/machine.hpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/tinykvm/common.hpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/tinykvm/memory.cpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/tinykvm/page_streaming.cpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/tinykvm/page_streaming.hpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/tinykvm/amd64/paging.cpp>
  - <https://raw.githubusercontent.com/varnish/tinykvm/HEAD/lib/tinykvm/memory_bank.cpp>
  - <https://github.com/libriscv/kvmserver/commits>
  - <https://github.com/libriscv/kvmserver/commit/2753a77981094a6a041f6883a4e7edadd8bd99cb>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/README.md>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/examples/bench.ts>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/examples/Makefile>
  - <https://raw.githubusercontent.com/libriscv/kvmserver/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/varnish/tinykvm`) · [data/wave12/enrich/raw/github_com_varnish_tinykvm.json](../../../data/wave12/enrich/raw/github_com_varnish_tinykvm.json) (enrichment confidence 0.75)

</details>
