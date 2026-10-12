# EOS VM Optimized Compiler (eosvmoc in AntelopeIO/spring)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> LLVM-based tier-up compiler for Wasm smart contracts inside Antelope's nodeos; claimed faster than EOS VM JIT, no published numbers.

| | |
|---|---|
| **Beats** | EOS VM JIT and EOS VM interpreter (also WABT and Binaryen per the docs claim; WAVM is the origin of the code) |
| **Claimed result** | No numbers in spring. A search snippet of the EOS VM documentation (snippet only) says native code from the optimized compiler is 'often an order of magnitude faster' than the same code in WABT, Binaryen, the EOS VM interpreter and the EOS VM JIT. |
| **Workload** | Execution of WebAssembly smart contracts in an Antelope node: an LLVM-based tier that compiles a contract in the background while the baseline runtime (EOS VM JIT) serves it, then switches to the optimized native code. |
| **Metric** | throughput |
| **Adoption** | 30 stars; runs the Antelope/EOS blockchain node (Spring, formerly Leap) |
| **Last commit** | 2025-11-12 |
| **Links** | [repository](https://github.com/AntelopeIO/spring) |

## Verdict

Nothing was measured: spring, its chain_plugin docs and the EOSIO v2.0.0 and v2.0.0-rc1 release notes give no numbers (rc1 says only that OC 'exceeds the performance of WAVM'); the claim of being 'often an order of magnitude faster' than WABT, Binaryen, the EOS VM interpreter and EOS VM JIT comes from search snippets of the retired EOS VM docs, with no workload, hardware or compiler.

## Use it when

- You operate an Antelope (Vaulta/EOS, WAX, Telos and similar) node on x86-64 Linux and want hot system contracts (eosio.\*) and read-only transactions to run as native code.
- API or read-only nodes serving many repeated read-only queries against the same contracts, where background compile cost is amortized across many calls.
- Studying a production design for guard-page sandboxing plus GS-segment memory addressing and timer-driven code-unmapping preemption in a Wasm AOT tier.

## Skip it when

- As a general-purpose Wasm engine: it compiles only the Wasm Antelope hands it, and f32/f64 min, max, ceil, floor, trunc, nearest and float-to-int truncations are emitted as calls to an intrinsic named eosvmoc_internal.unreachable (a source comment says these should call out to C++ implementations); WAVM, Wasmtime or Wasmer are the standalone options.
- Any platform other than x86-64 Linux: it depends on the GS segment, arch_prctl, memfd, Linux SIGSEGV semantics and an x86 assembly stack switch (switch_stack_linux.s).
- Builds with a current LLVM: the Spring README says LLVM 7 to 11 only ('newer versions do not work') and LLVMJIT.cpp uses the legacy pass manager and ORC APIs of that era.
- When you need published, reproducible speedups: no benchmark of OC against EOS VM JIT or the interpreter exists in the repo, and the 'order of magnitude' claim is known only from search snippets of retired EOS VM docs (eos.io no longer resolves).
- Processes that cannot afford huge virtual address reservations or a process-wide SIGSEGV handler (Leap issue 645 counted 529 slices of about 8 GiB, roughly 4.2 TiB of virtual memory per execution thread, before Leap 5 added the mprotect threshold).

## How it is fast

The Wasm-to-LLVM-IR emitter is derived from WAVM; LLVMJIT.cpp runs a short legacy function pass pipeline (mem2reg, instcombine, simplifycfg, jump threading, constant propagation) and emits position-independent code for the generic host triple (no CPU-specific features). Linear memory is addressed through the GS segment (LLVM address space 256) with no explicit bounds checks: memory.cpp maps memfd-backed 'slices' surrounded by PROT_NONE regions, out-of-range accesses fault into a SIGSEGV handler, and memory.grow mostly just moves the GS base (wrgsbase via FSGSBASE when the kernel allows, arch_prctl otherwise), falling back to mprotect above a page threshold. Deadlines cost nothing in hot loops: the transaction timer's expiry callback mprotects the code mapping to PROT_NONE so the next instruction fetch faults; only a volatile call-depth counter is updated per call.

## Compared with alternatives

Only if you run an Antelope node: the catalogued EOS VM entry (AntelopeIO/eos-vm) is the baseline interpreter/JIT this tier sits on, and standalone Wasm needs are better served by WAVM (the code it was derived from, with published libsodium shootout numbers) or wasm2c, both of which have measured results.

## Integration

| | |
|---|---|
| **Form** | module (part of the nodeos binary in AntelopeIO/spring; not packaged separately) |
| **Dependencies** | LLVM 7-11 (Linux only), Boost (asio for the compile monitor), Spring's chain library, fc and chainbase |
| **Minimum toolchain** | C++20 compiler and standard library, CMake 3.16+ (README); reference builds use GCC 10 with LLVM 11 on Ubuntu 20.04/22.04 |
| **Platforms** | x86-64 Linux only (FSGSBASE used when the kernel enables it; disable with the SPRING_DISABLE_FSGSBASE environment variable) |
| **Thread safety** | One executor and one memory mapping per execution thread; compilation happens in separate forked oc-compile processes limited by RLIMIT_CPU and RLIMIT_AS; the SIGSEGV handler is installed once per process and chains to any earlier handler |
| **Drop-in for the baseline** | partial: a node flag switches it on, and the baseline runtime still serves each contract until its background compile finishes; it cannot be used outside an Antelope node |

## Gotchas

- The default 'auto' mode applies OC only to eosio.\* accounts, read-only transactions and whitelisted suffixes (default xsat,vaulta), and not when a producer applies blocks; every other contract stays on EOS VM JIT unless you set 'all'.
- Open spring issue #1880 (2025-12-10): full replays crash intermittently with eos-vm-oc-enable on (workaround: set it to none); PR #1881 'Do not oc interrupt during replay', which targets runs with disable-replay-opts, was still open when read.
- Out-of-bounds memory accesses and deadline expiry are both delivered as faults to a process-wide SIGSEGV handler that siglongjmps out of the contract when the fault address lies in the executor's code or memory range and otherwise chains to the previous handler; stack depth is bounded by a per-call depth counter plus a compile-time per-function stack-size cap (the compile child exits if exceeded), with a PROT_NONE guard at the bottom of the wasm stack. Spring's own checktime_unit_test_eos-vm-oc has an open test-failure issue (#1822).
- Compiled code lives in an on-disk code cache whose header id must match the nodeos version ('existing EOS VM OC code cache not compatible with this version'), so upgrades start cold and re-tier every contract.

## Known shortcomings

- No numbers for the EOS VM Optimized Compiler in spring, its chain_plugin docs or the EOSIO v2.0.0 release notes; the 'order of magnitude' claim exists only as a search snippet. The OC code carries a WAVM BSD-3 notice next to MIT and is embedded in the node, not standalone. Kept at D under the keep-and-document rule.
- Enricher: the default 'auto' mode applies the OC only to eosio.\* accounts, read-only transactions and whitelisted suffixes, never when a producer applies blocks; open issue #1880 (2025-12-10) has full replays crashing intermittently with eos-vm-oc-enable on, PR #1881 still open; out-of-bounds accesses and deadline expiry are delivered through a process-wide SIGSEGV handler that siglongjmps out of the contract; the checktime OC unit test has an open failure (#1822); the on-disk code cache is invalidated by every nodeos version change. Bound to Antelope host functions and LLVM 7-11, so reference material.

## Caveats and trade-offs

spring has no benchmark for the OC tier. libraries/chain/webassembly/runtimes/eos-vm-oc holds only source plus an 'About WAVM' note: OC is derived from WAVM, so that code also carries WAVM's BSD-3-Clause notice next to spring's MIT license. The chain_plugin docs list the --eos-vm-oc-enable (default auto), --eos-vm-oc-whitelist (default xsat,vaulta), cache-size and compile-threads options without performance numbers. The EOSIO v2.0.0 release notes call OC a 'high performance WASM tier-up runtime' and say the background compile takes 'a handful of seconds', with no numbers. The 'often an order of magnitude faster' than WABT, Binaryen, EOS VM interpreter and EOS VM JIT claim comes from search-result snippets of the EOS VM documentation (snippet only), with no workload, hardware or compiler. An everstake.one blog on CPU execution time could not be opened (EGRESS_BLOCKED). OC is embedded in the node and is not a standalone library. Tier D by the assignment rule; the eos-vm repo is catalogued separately. The last commit on main is 2025-11-12 (a LICENSE update); release dates on the releases page could not be pinned to a year with certainty.

x86_64 Linux only; needs LLVM; has compile_monitor, compile_trampoline and code_cache components and a tier-up design so the first calls run on the baseline runtime; a leap issue is titled 'Reduce EOS VM OC's memory slice count allowing for higher parallelization' (seen in search results only); code created in part from WAVM, and the eos-vm-oc files carry WAVM's BSD-3-Clause notice (spring's top-level LICENSE is MIT).

## Maintenance

Maintained inside Spring (last commit on main 2025-11-12, OC fixes such as PR #1881 still in review in December 2025); the code is MIT at the top level with WAVM's BSD-3-Clause notice in the OC directory, and it is reference material rather than something you can lift out, since it is bound to Antelope's host functions, timer and LLVM 7-11.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null, and no numbers for the OC tier exist in spring (README, chain_plugin docs and the eos-vm-oc source directory), in the EOSIO v2.0.0 release notes, or in the Leap issues opened. The 'often an order of magnitude faster' wording is known only from search snippets of the EOS VM docs, so the tier stays D.
- **Verifier notes:** Record is accurate; the only change is fuller caveats (WAVM BSD-3 notice in the OC directory, OC enabled by default only for whitelisted accounts, no numbers in the release notes or docs). Shortcomings: no benchmark or numbers anywhere reachable, claim known only from doc snippets, and it is embedded in a blockchain node rather than a standalone library. Not rejected: Spring runs the Antelope/EOS network despite 30 stars. MIT confirmed from LICENSE.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** any published eosvmoc vs eos-vm JIT numbers
- **Pages the verifier opened:**
  - <https://github.com/AntelopeIO/spring>
  - <https://github.com/AntelopeIO/spring/commits/main>
  - <https://github.com/AntelopeIO/spring/releases>
  - <https://github.com/AntelopeIO/spring/tree/main/libraries/chain/webassembly/runtimes/eos-vm-oc>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/README.md>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/docs/01_nodeos/03_plugins/chain_plugin/index.md>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/About%20WAVM>
  - <https://github.com/EOSIO/eos/releases/tag/v2.0.0>
  - <https://github.com/eosnetworkfoundation/product/issues/155>
  - <https://github.com/AntelopeIO/leap/issues/645>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/README.md>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/About%20WAVM>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/docs/01_nodeos/03_plugins/chain_plugin/index.md>
  - <https://github.com/AntelopeIO/spring/tree/main/libraries/chain/webassembly/runtimes/eos-vm-oc>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/LLVMJIT.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/LLVMEmitIR.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/memory.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/gs_seg_helpers.c>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/executor.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/code_cache.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/compile_monitor.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/compile_trampoline.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/spring/HEAD/libraries/chain/webassembly/runtimes/eos-vm-oc/stack.cpp>
  - <https://github.com/AntelopeIO/spring/commits/main>
  - <https://github.com/AntelopeIO/spring/issues?q=is%3Aissue+%22OC%22>
  - <https://github.com/AntelopeIO/spring/issues/1880>
  - <https://github.com/AntelopeIO/spring/pull/1881>
  - <https://github.com/AntelopeIO/leap/issues/645>
  - <https://github.com/EOSIO/eos/releases/tag/v2.0.0-rc1>
  - <https://github.com/atticlab/eos-bp-performance>
  - <https://raw.githubusercontent.com/atticlab/eos-bp-performance/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/atticlab/eos-bp-performance/HEAD/cpu_perf_presentation.pdf>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/antelopeio/spring`) · [data/wave12/enrich/raw/github_com_antelopeio_spring.json](../../../data/wave12/enrich/raw/github_com_antelopeio_spring.json) (enrichment confidence 0.6)

</details>
