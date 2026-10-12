# EOS VM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `EOS VM License v1.0 (MIT-derived text with an added clause requiring source release of any covered work used for non-EOSIO blockchain purposes; not OSI-approved)` · 🟡 stale

> Header-only C++ WebAssembly interpreter and x86-64 single-pass JIT for Antelope blockchains; vendor claims up to 16x over the Binaryen interpreter.

| | |
|---|---|
| **Beats** | Binaryen and WABT WebAssembly interpreters |
| **Claimed result** | Vendor claim (search snippet only): EOS VM runs the EOS Mechanics WASM CPU benchmarks up to 16x faster than Binaryen; WABT gave EOSIO 1.3 about 2x over Binaryen; EOS VM expected up to 6x more than that (up to 12x faster than EOSIO at launch). |
| **Workload** | EOS Mechanics WASM CPU benchmarks run under the EOSIO blockchain, comparing EOS VM with the Binaryen and WABT engines EOSIO previously shipped. |
| **Metric** | throughput |
| **Adoption** | 7 stars, 18 forks on AntelopeIO/eos-vm; the original EOSIO/eos-vm has 200 stars, 62 forks; runtime of Antelope (EOSIO) blockchains |
| **Last commit** | 2025-07-30 |
| **Links** | [repository](https://github.com/AntelopeIO/eos-vm) · [benchmark](https://medium.com/eosio/introducing-eosio-2-enhancing-performance-improving-security-and-new-developer-tools-38ca29c7ab4c) |

## Verdict

The only numbers are block.one's EOSIO 2 announcement, seen as search snippets: 'EOS VM runs the EOS Mechanics WASM CPU benchmarks up to 16x faster than Binaryen' (the EOSIO 1.0 interpreter), with no runtime, hardware, compiler or method given; the EOSIO v2.0.0 release notes on GitHub carry no numbers and recommend EOS VM JIT for block producers and the EOS VM Optimized Compiler, which is not in this repo, for other nodes. The repo's bench-interp tool prints a single parse time and execution time with no published results.

## Use it when

- Antelope/EOSIO-compatible chains, or any system that needs bit-identical Wasm results across machines (softfloat on by default) and consensus-matching limits such as call depth 250 and per-section caps in `options`.
- Embedding untrusted Wasm in a C++ host where predictable, linear load and validation time matters more than peak speed (the README contrasts this with WAVM's long, unpredictable LLVM compiles).
- Hard per-call CPU deadlines without instruction counting: the watchdog revokes execute permission on the code pages when time runs out.
- Many short calls into small contracts with cheap host-function transitions on x86-64 Linux (JIT) or other 64-bit Unix hosts (interpreter).

## Skip it when

- Peak throughput: the peer-reviewed 'VM Matters' study (snippet only) measured EOS VM at about 20 s on a matrix benchmark against about 70-170 ms for WAVM and Wasmtime, so it only beats the old Binaryen and WABT interpreters.
- Modern Wasm modules: the opcode table is MVP only (no sign-extension, saturating float-to-int, bulk memory, reference types or SIMD), so modules from toolchains that enable post-MVP features by default will not load unless built for the MVP target.
- Windows (CMake stops with an error on WIN32) or a JIT on anything but x86-64; AArch64 gets only the interpreter.
- Projects that cannot accept the EOS VM License v1.0: its share-alike clause covers any work adapted for other blockchain purposes and it is not OSI-approved.
- Hosts that install their own SIGSEGV/SIGFPE handlers or whose host functions need destructors to run when a trap unwinds.

## How it is fast

The interpreter's parser rewrites Wasm into an internal bitcode of fixed-size variant opcodes with branch and call targets pre-resolved (br_table_data, call_imm), dispatched through a statically derived visitor instead of virtual calls, and keeps module data in non-owning bump allocators that live as long as the module. Linear memory sits in an 8 GiB PROT_NONE reservation with guard pages, so loads and stores need no bounds checks and host functions need no pointer validation. The JIT is a single-pass x86-64 code writer driven directly by the parser (memory base kept in rsi, no IR or LLVM), which keeps compile time linear. Time limits cost nothing in the hot loop: on expiry the watchdog makes the code pages non-executable and the resulting SIGSEGV unwinds the run.

## Compared with alternatives

Pick EOS VM over wasm3, WAMR or Wasmi only when you need Antelope consensus compatibility, softfloat determinism and zero-overhead watchdog deadlines in a header-only C++ engine; for general embedding those interpreters have measured numbers, permissive licences and wider platform support, and WAVM or WasmEdge win on peak speed.

## Integration

| | |
|---|---|
| **Form** | header-only (plus a softfloat static library built by CMake when ENABLE_SOFTFLOAT is on, the default) |
| **Dependencies** | Berkeley SoftFloat (vendored under external/softfloat) unless softfloat is disabled; pthreads for the watchdog; Catch2 and the eos-vm-test-wasms repo only for tests |
| **Minimum toolchain** | C++20 with GNU extensions per CMakeLists.txt (docs/OVERVIEW.md still says C++17), CMake 3.12+, GCC or Clang |
| **Platforms** | Linux and macOS; JIT x86-64 only, interpreter on 64-bit Unix hosts that can reserve 8 GiB of virtual address space per wasm_allocator |
| **Thread safety** | One backend, wasm_allocator and watchdog per thread; a parsed module can be shared across threads since 2023 (issue #7 closed), and the signal-handling state is thread_local. |
| **Drop-in for the baseline** | no |

## Gotchas

- Each wasm_allocator reserves 8 GiB of virtual memory (max_memory = 4ull &lt;&lt; 31) plus guard pages; it had no destructor until April 2025 (commit 'Add destructor to wasm_allocator to release memory'), so older copies leaked the mapping.
- Static initialization installs process-wide SIGSEGV, SIGFPE (and SIGBUS outside Linux) handlers and traps unwind with siglongjmp; the README warns host functions must be able to 'fail hard' without destructors, and the watchdog starts a new std::thread for every timed run.
- A timeout disables code pages for the whole module: other threads running the same module take SEGVs and retry until the timed-out run re-enables them (signals.hpp comment), so one slow contract stalls its siblings briefly.
- Harness flaw in the cited benchmark: the EOS Mechanics CPU action (AlohaEOS/eos-mechanics contracts/eosmechanics.cpp) has is_prime assign `prime = BOOL(p)` inside its test, so it never returns FALSE for odd p, and the Lucas-Lehmer step overflows 64 bits for p &gt; 32 and shifts 1LLU by up to 375 (undefined behaviour); the work is about 35,000 iterations of a 64-bit multiply and remainder whose result is discarded (a code comment warns it could be optimized out), timed by self-reported on-chain cpu_usage_us that the repo's own disclaimer says producers can manipulate.

## Known shortcomings

- Vendor 16x claim is snippet only (medium.com blocked) and it is unclear which runtime produced it (the Optimized Compiler is not in this repo); the VM Matters paper puts it far behind wasmtime and WAVM. LICENSE is the custom non-OSI 'EOS VM License V1.0', not MIT, so usability is reference. Fork of EOSIO/eos-vm.
- Enricher: the cited EOS Mechanics CPU contract (AlohaEOS/eos-mechanics contracts/eosmechanics.cpp) has is_prime never returning false for odd p (prime = BOOL(p)), Lucas-Lehmer overflow for p over 32, '1LLU &lt;&lt; p' undefined up to 375, a discarded result and self-reported cpu_usage_us timing, so the 16x claim (snippet only, runtime unknown, no numbers in the v2.0.0 notes) rests on a broken harness. MVP-only opcodes, 8 GiB virtual reservation per allocator, process-wide signal handlers, JIT x86-64 only.

## Caveats and trade-offs

The repo README and docs have no numbers; the only bench tool (tools/bench-interp) prints parse and execution times without published results. The 16x/2x/6x claims come from block.one's EOSIO 2 announcement (Medium, blocked here; the eos.io copy no longer resolves) and the EOS VM Medium post, seen only as WebSearch snippets: 'EOS VM runs the EOS Mechanics WASM CPU benchmarks up to 16x faster than Binaryen'; WABT gave EOSIO 1.3 about 2x; EOSIO 2 up to 6x more (up to 12x faster than at launch). The snippet does not say which of EOSIO 2's three runtimes (EOS VM Interpreter, EOS VM JIT, EOS VM Optimized Compiler) produced the 16x; the Optimized Compiler (eos-vm-oc) lives in the EOSIO/Leap node repo, not here, so the figure may not apply to the code in this repo. The peer-reviewed 'VM Matters' paper (ACM TOSEM, arXiv 2012.01032; snippet only) measured EOS VM far slower than JIT/AOT engines on a matrix benchmark (one version: about 19,768 ms vs about 70 ms for WAVM and wasmtime; another: 21,855 ms vs about 170 ms WAVM and 156 ms wasmtime), so the win is only against the older Binaryen and WABT interpreters. Licence is the custom EOS VM License v1.0, not MIT: it adds a share-alike clause for use in non-EOSIO blockchain software, so it is not OSI-approved. AntelopeIO/eos-vm is the EOS Network Foundation continuation of EOSIO/eos-vm (its LICENSE says it is based upon EOSIO/eos-vm; GitHub does not mark it as a fork).

Header-only C++ backend (except the softfloat library) with an interpreter, a JIT, bounded memory and watchdog-timer execution limits; built for deterministic, time-bounded blockchain contracts rather than raw peak speed. README says WAVM executes extremely fast but has unpredictable compile times.

## Maintenance

Stale since 2025-07-30 (sync-call work for Antelope's node software), maintained by the EOS Network Foundation for its own chain with 5 open issues; the custom non-OSI licence and MVP-only Wasm make it a reference design rather than a general-purpose engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Only vendor (block.one) marketing numbers from the EOSIO 2 announcement, seen as WebSearch snippets (medium.com blocked, eos.io no longer resolves); repo README, docs/OVERVIEW.md and the EOSIO v2.0.0-rc1 release notes carry no numbers. Vendor-blog evidence without methodology is C at most.
- **Verifier notes:** Kept at C on snippet-only vendor numbers; shortcomings: no reachable numbers page, unclear which runtime (interpreter, JIT or optimized compiler) gave 16x, only beats old interpreters (Binaryen, WABT) and is far slower than wasmtime/WAVM per the VM Matters paper. License was wrong: the LICENSE file is the custom non-OSI 'EOS VM License V1.0', so usability moves to reference. Last commit 2025-07-30 (stale) confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `license`, `usability`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/README.md>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/docs/OVERVIEW.md>
  - <https://github.com/AntelopeIO/eos-vm>
  - <https://github.com/AntelopeIO/eos-vm/commits>
  - <https://github.com/EOSIO/eos-vm>
  - <https://github.com/EOSIO/eos/releases/tag/v2.0.0-rc1>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/README.md>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/docs/OVERVIEW.md>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/tools/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/tools/bench_interp.cpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/backend.hpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/x86_64.hpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/watchdog.hpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/allocator.hpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/signals.hpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/options.hpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/constants.hpp>
  - <https://raw.githubusercontent.com/AntelopeIO/eos-vm/HEAD/include/eosio/vm/opcodes_def.hpp>
  - <https://github.com/AntelopeIO/eos-vm/tree/main/include/eosio/vm>
  - <https://github.com/AntelopeIO/eos-vm/issues?q=is%3Aissue>
  - <https://github.com/AntelopeIO/eos-vm/commits/main>
  - <https://raw.githubusercontent.com/EOSIO/eos-vm/HEAD/README.md>
  - <https://github.com/EOSIO/eos/releases/tag/v2.0.0>
  - <https://github.com/AlohaEOS/eos-mechanics>
  - <https://raw.githubusercontent.com/AlohaEOS/eos-mechanics/HEAD/README.md>
  - <https://raw.githubusercontent.com/AlohaEOS/eos-mechanics/HEAD/contracts/eosmechanics.cpp>
  - https://eosioeos.wordpress.com/2021/10/03/introducing-eosio-2-enhancing-performance-improving-security-and-new-developer-tools/ (EGRESS_BLOCKED)
  - WebSearch: EOS VM 16x Binaryen EOS Mechanics; EOSIO 2 EOS VM Interpreter/JIT/Optimized Compiler (snippets only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/antelopeio/eos-vm`) · [data/wave12/enrich/raw/github_com_antelopeio_eos_vm.json](../../../data/wave12/enrich/raw/github_com_antelopeio_eos_vm.json) (enrichment confidence 0.55)

</details>
