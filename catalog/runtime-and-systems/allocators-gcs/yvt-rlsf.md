# rlsf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust no_std TLSF allocator with constant-time alloc/free; lower latency and far smaller code than dlmalloc on microcontrollers and wasm.

| | |
|---|---|
| **Beats** | dlmalloc (also buddy-alloc, umm_malloc, wee_alloc) |
| **Claimed result** | rlsf 260-320 cycles vs dlmalloc 450-750 cycles (buddy-alloc 340-440, umm_malloc 300-700); WebAssembly code size 1267 bytes vs dlmalloc 9613 bytes |
| **Workload** | Alloc/dealloc latency on an STM32F401 microcontroller and code size on WebAssembly, measured with FarCri.rs. |
| **Metric** | latency |
| **Hardware** | STM32F401 (Cortex-M4F) |
| **Adoption** | 127 stars |
| **Last commit** | 2026-07-26 |
| **Links** | [repository](https://github.com/yvt/rlsf) · [benchmark](https://github.com/yvt/rlsf) |

## Verdict

First-party FarCri.rs runs on an STM32F401 (Cortex-M4F) put rlsf's alloc/dealloc at 260-320 cycles vs 450-750 for the Rust dlmalloc crate (0.2.x, fed by a bump page source), 340-440 for buddy-alloc and 300-700 for umm_malloc (umm_malloc ignored alignment); a separate wasm build measured code size 1267 bytes vs 9613 for dlmalloc. Compiler version and flags are not given and the numbers appear only in chart alt text hosted on yvt.jp.

## Use it when

- Bare-metal or RTOS firmware (e.g. Cortex-M) that needs a heap with a bounded worst-case allocation time.
- Real-time code paths where malloc latency jitter matters more than peak throughput.
- wasm32 builds where allocator code size matters: SmallGlobalTlsf measured 1267 bytes vs 9613 for dlmalloc.
- Managing a fixed static arena or a carve-out region (DMA buffers, shared memory) with a general-purpose allocator.

## Skip it when

- Multi-threaded hosted applications: no concurrent access; GlobalTlsf wraps the whole pool in one mutex, so use jemalloc, mimalloc or TCMalloc there.
- Allocation-heavy desktop/server workloads: no small-object fast path or thread caches; the README itself says modern allocators such as glibc and jemalloc may win.
- Programs that need memory returned to the OS: GlobalTlsf never gives pages back.
- Targets other than unix or wasm32 without atomics if you want GlobalTlsf: elsewhere (e.g. ESP32, wasm with atomics, Windows) you must wire Tlsf/FlexTlsf into GlobalAlloc yourself (issues #4, #8 open).

## How it is fast

TLSF keeps segregated free lists indexed by a first level (power-of-two size class, found with leading_zeros) and a second level (SLLEN linear subdivisions, found by a rotate), with a bitmap per level so a fitting non-empty list is found with bit-scan instructions instead of a search. Every alloc and free is therefore O(1) with immediate coalescing of neighbours. rlsf caps each pool with a permanently occupied sentinel block instead of a last-block flag, which the README says simplifies the code and improves worst-case time and code size.

## Compared with alternatives

Pick rlsf over Talc when you want hard constant-time bounds rather than best wasm throughput (Talc's own wasm benchmarks rate it ahead of RLSF in size and speed); pick it over XenoAtom.Allocators (also TLSF) when you are in Rust/no_std rather than .NET. The other siblings target multi-threaded hosted malloc and are not alternatives on a microcontroller.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, const-default, rustversion; libc on unix |
| **Minimum toolchain** | Rust 1.61 (edition 2021) |
| **Platforms** | any for Tlsf/FlexTlsf (no_std); GlobalTlsf on unix and wasm32 without atomics |
| **Thread safety** | Tlsf is single-threaded (&mut self); GlobalTlsf is Sync via a single global mutex (FIFO lock gives O(contending threads) worst case) |
| **Drop-in for the baseline** | partial — GlobalTlsf is a drop-in #[global_allocator] replacing Rust's default (dlmalloc on wasm32); on embedded targets the Tlsf core API needs a small GlobalAlloc wrapper |

## Gotchas

- Maximum block size is (GRANULARITY &lt;&lt; FLLEN) - GRANULARITY; with the README's u16/12/16 config on 32-bit that is about 64 KiB, so pick FLLEN for your largest allocation.
- Internal fragmentation grows with free block size (README example: up to 4094 bytes worst case); SLLEN trades list count against fragmentation.
- deallocate requires the caller to pass the original alignment; allocate/deallocate are unsafe.
- Version 0.2.2 (2026-02-07) fixed invalid reference creation flagged by Miri and added a provenance workaround for GlobalAlloc dealloc/realloc; a Miri false-positive issue (#20) is still open.

## Known shortcomings

- Rust, not C++. The bench (stress.rs) compares against the Rust dlmalloc crate 0.2.1 behind a bump page source, not C dlmalloc; umm_malloc ignores alignment; no compiler version or flags.

## Caveats and trade-offs

Numbers appear only as image alt text in the README; the charts are hosted on yvt.jp. Baseline dlmalloc is not in the list, and there is no comparison to glibc malloc, jemalloc or mimalloc; the README itself says modern allocators may beat it in allocation-heavy apps and that it does not support concurrent access. wee_alloc could not be timed (out of memory), and the wasm wee_alloc build used a fork. Compiler version and flags not stated. Benchmark crate: crates/rlsf_benchmark_farcri.

Constant-time two-level segregated fit for no_std and real-time use; no thread scaling; embedded niche, not a hosted malloc replacement.

## Maintenance

Active (v0.2.2 in February 2026, commits through July 2026, v1 tracking issue open), MIT/Apache-2.0, small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers, given in the README image alt text, against dlmalloc, buddy-alloc and umm_malloc on an STM32F401. The benchmark code is public (crates/rlsf_benchmark_farcri, using FarCri.rs), but no compiler version or flags are stated, so it cannot be A.
- **Verifier notes:** README footnotes read: the latency figures were measured on an STM32F401 with FarCri.rs, and the latest version of each library was used. Metadata from github.com: MIT/Apache-2.0, 127 stars, not archived, last commit 2026-07-26.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party benchmark crate
- **Pages the verifier opened:**
  - <https://github.com/yvt/rlsf>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/README.md>
  - <https://github.com/yvt/rlsf/commits>
  - <https://github.com/yvt/rlsf/tree/main/crates>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/README.md>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/crates/rlsf/Cargo.toml>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/crates/rlsf/src/lib.rs>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/crates/rlsf/src/global.rs>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/crates/rlsf/src/tlsf.rs>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/crates/rlsf/src/flex.rs>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/crates/rlsf_benchmark_farcri/Cargo.toml>
  - <https://raw.githubusercontent.com/yvt/rlsf/HEAD/crates/rlsf_benchmark_farcri/benches/stress.rs>
  - <https://github.com/yvt/rlsf/tree/main/crates/rlsf/src>
  - <https://github.com/yvt/rlsf/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/yvt/rlsf`) · [data/wave11/enrich/raw/github_com_yvt_rlsf.json](../../../data/wave11/enrich/raw/github_com_yvt_rlsf.json) (enrichment confidence 0.8)

</details>
