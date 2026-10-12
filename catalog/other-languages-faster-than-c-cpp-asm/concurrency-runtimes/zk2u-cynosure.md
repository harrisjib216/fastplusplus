# Cynosure RingBuf (async-native SPSC ring buffer, Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT (declared in Cargo.toml and the README; the repository has no LICENSE file)` · 🟢 active

> Rust lock-free SPSC ring with built-in async push/pop; 1.29 vs 2.46 ns push+pop against rigtorp::SPSCQueue on Apple M4 Max.

| | |
|---|---|
| **Beats** | rigtorp::SPSCQueue (C++ single-producer single-consumer ring buffer). The same table also holds a hand-rolled C11 cached-index ring, which is faster than Cynosure. |
| **Claimed result** | BENCHMARKS.md, 'How it compares to the absolute fastest (C / C++)', 1-thread push+pop latency: hand-rolled C11 ring 0.79 ns, Cynosure 1.29 ns, rigtorp::SPSCQueue 2.46 ns, ringbuffer-spsc (Rust) 2.03 ns. Cynosure is about 1.9x lower than rigtorp, and the C11 ring is about 1.6x lower than Cynosure (both derived from page data). The same file's criterion spsc_compare table gives 2.2 ns per push+pop for Cynosure and 2.5 ns for rtrb. |
| **Workload** | Single-thread push plus pop latency of an SPSC ring buffer, measured in a tight loop with LTO and DoNotOptimize against the C++ reference and a bare C11 ring; the same BENCHMARKS.md file also ranks the crate against Rust channels (rtrb, kanal, crossbeam, flume, tokio mpsc) on throughput and cross-thread latency. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max (aarch64, macOS) |
| **Compiler and flags** | Rust stable, cargo bench with release plus LTO (README). The C++ and C comparison is described only as a 'maximally-tuned tight loop (LTO, DoNotOptimize)'; C++ compiler, version and flags are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README and BENCHMARKS.md name the cached-index, cache-line-padded ring design (the same family as rtrb and rigtorp::SPSCQueue) and a waiter check that costs one atomic load and branch per call (free on AArch64 ldarb); neither says why 1.29 ns beats rigtorp's 2.46 ns. |
| **Adoption** | 3 stars; cynosure crate has about 59.6k crates.io downloads |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/zk2u/cynosure) · [benchmark](https://raw.githubusercontent.com/zk2u/cynosure/HEAD/BENCHMARKS.md) |

## Verdict

On an Apple M4 Max under macOS, one u32 push plus one pop on a single thread took 1.29 ns for Cynosure's RingBuf, 2.46 ns for rigtorp::SPSCQueue (C++), 2.03 ns for ringbuffer-spsc and 0.79 ns for a hand-rolled C11 ring, in an unpublished tight-loop harness (LTO, DoNotOptimize) whose C/C++ compiler and flags are not stated. The repository's own criterion suite (Rust only, capacity 1024, bench profile with LTO) puts the same operation at 2.2 ns against rtrb's 2.5 ns.

## Use it when

- A fixed 1:1 stream between two tasks or cores on a thread-per-core executor (monoio, glommio), where the consumer should park with pop().await instead of spinning.
- Small Copy payloads (u32-sized) at high rates on AArch64 (Apple silicon, Graviton-class servers), where the SeqCst publish costs the same as a release store.
- Byte streams between threads through std::io::Write/Read on Producer&lt;u8&gt;/Consumer&lt;u8&gt;, or bulk slice transfers with try_push_slice/try_pop_slice.
- Rust code that wants a single SPSC type with sync, blocking and async faces instead of combining a sync ring (rtrb, ringbuf-spsc) with a separate notification mechanism.

## Skip it when

- C or C++ code: the published lead over rigtorp::SPSCQueue (1.9x on one machine, single-thread push+pop) is not worth an FFI boundary, and the project's own hand-rolled C11 ring is 1.6x faster still.
- x86-64 targets where the margin matters: every push and every pop ends with a SeqCst store, which the source notes 'carries the barrier' on x86, while rigtorp publishes with release stores; the file itself says x86 numbers are very different, and none are published.
- Channels where either side may be dropped while the other waits: there is no closed flag or peer wake (open issue #2, 'close-on-drop semantics'), so pop().await or pop_blocking() on a ring whose producer is gone waits forever.
- Multiple producers or consumers, or a shared work-stealing runtime with many senders: use mpsc_light or another channel; RingBuf is strictly SPSC.
- Builds without LTO: the crate's Cargo.toml says its lean ops do not inline across the crate boundary without LTO and 'read artificially slow', so the published numbers assume release plus LTO.

## How it is fast

It is a Lamport ring with cached indices: each side keeps a private copy of the other side's index and reloads the shared atomic only when the ring looks full or empty, the two shared indices sit in separate 64-byte-aligned CachePadded cells, and power-of-two capacity turns wraparound into a mask (rigtorp::SPSCQueue wraps with a compare-and-reset over capacity+1 slots and splits a pop into front() plus pop()). Async support costs one SeqCst load of a waiter flag per operation (WaiterSlot::signal, inline(always), wake path cold-outlined), and the index publish is a SeqCst store; on AArch64 both compile to stlr/ldar with no dmb, per the source comments. Branch hints (likely/unlikely, taken from fereidani/branches) keep the full/empty checks off the hot path.

## Compared with alternatives

Pick Cynosure for in-process 1:1 handoff between cores on a thread-per-core Rust executor, where its async ring measured about 90 Melem/s cross-core against tokio mpsc's 15. Pick Myelon for cross-process shared-memory IPC, and Tokio's channels when you need multi-producer channels on a work-stealing runtime.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default; optional monoio 0.2 (feature monoio-0_2) |
| **Minimum toolchain** | Rust edition 2024 (Rust 1.85+); rust-toolchain.toml pins stable 1.89.0 |
| **Platforms** | any std target; tuned and measured only on AArch64 (Apple M4 Max, macOS); no x86 numbers published |
| **Thread safety** | Producer and Consumer are each Send (for T: Send) but not Sync: exactly one owner per side, usable from two different threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw beyond the verifier's notes (C/C++ harness unpublished, flags unknown): the headline 1.29 ns and the repo's own criterion figure of 2.2 ns are the same u32 push+pop on the same M4 Max, so harness choice alone moves Cynosure by about 1.7x, close to the 1.9x margin claimed over rigtorp. That margin holds only if rigtorp ran in the identical unpublished loop, and rigtorp's pop() carries an assert that performs an extra acquire load of writeIdx_ unless NDEBUG is defined, which nobody can check here.
- The C/C++ rows were added in the 0.6.0 commit 5f4601c (2026-07-27), after the 0.5.0 switch to SeqCst that fixed a cross-thread lost-wakeup deadlock; try_push and try_pop are unchanged between that commit and the 2026-09-21 hardening commit 2d44f34, so the numbers are not from stale or since-fixed hot-path code.
- CachePadded is repr(align(64)), while crossbeam documents 128-byte lines on aarch64 big cores and pads to 128 there; on the benchmark's own M4 Max the read and write indices may share a 128-byte line in the two-thread rows. The single-thread latency row is unaffected.
- Miri runs skip async tests (justfile: 'cargo +nightly miri test --lib -- --skip async'), so the async park and wake paths rely on loom and stress tests; push_slice/pop_slice futures are documented as not cancellation-safe (use the \*_counted variants); capacity must be a power of two and zero-sized T panics.

## Known shortcomings

- The rigtorp and C11 harness is not in the repo and the C++ flags are unstated; its own bare C11 ring beats it 1.6x, so no language win; no LICENSE file (MIT in Cargo.toml and README only).
- Harness flaw: the 1.29 ns comes from an unpublished loop while the crate's own criterion gives 2.2 ns for the same operation, a 1.7x harness swing near the claimed 1.9x over rigtorp; rigtorp's pop() assert adds an acquire load unless NDEBUG, and the flags are unknown. On x86 Cynosure does a SeqCst store per push and pop against rigtorp's release stores, so the win is unlikely to carry over (not measured). The C/C++ rows were added in the 0.6.0 commit 5f4601c (2026-07-27) after the SeqCst fix, and try_push/try_pop are unchanged through 2d44f34. No close-on-drop (open issue #2: pop().await hangs forever); CachePadded align(64) against 128-byte M4 lines; Miri skips async; needs LTO.

## Caveats and trade-offs

The C++ and C11 comparison code is not in the repository. benches/ holds only Rust criterion suites, and spsc_compare.rs and Cargo.toml mention neither rigtorp nor ringbuffer-spsc. The C/C++ rows therefore cannot be reproduced, and the C++ compiler, version and flags are unstated, which keeps the entry at tier C. The project's own table refutes a language-level win: a bare C11 cached-index ring beats Cynosure by about 1.6x on the same path. The win over rigtorp is single-thread push+pop latency only (producer and consumer on one thread, not two cores), and why rigtorp reads 2.46 ns in that harness is not explained. The 1.29 ns figure comes from a different harness than the 2.2 ns criterion figure for the same operation. Single representative run on one Apple M4 Max; the file warns that a back-to-back cargo bench run throttles later benches by about 15% and that x86 results differ (a SeqCst store is a barrier there). The repository has no LICENSE file; MIT is declared in Cargo.toml and the README. Young project: first commits July 2025, 3 stars, one author, 42 commits. Found through a README claim, not an independent measurement. [retier] The 1.29 ns comes from an unpublished loop while the crate's own criterion gives 2.2 ns for the same operation (a 1.7x harness swing near the claimed 1.9x); rigtorp's pop() assert adds an acquire load unless NDEBUG, flags unknown. On x86 Cynosure does a SeqCst store per push and pop against rigtorp's release stores (not measured). No close-on-drop (issue #2: pop().await hangs forever); CachePadded align(64) against 128-byte M4 lines; needs LTO.

Rust crate, so use from C++ needs FFI or a separate process. Tuned on AArch64: the benchmark file notes the SeqCst publish store is free on Apple silicon and a barrier on x86, and that numbers 'are very different on x86'. The async-native design pays about one atomic load and a branch per operation to check for a waiting task, which is why a bare synchronous C ring stays faster. Sibling primitives (LocalMutex, LocalSemaphore, triple_buffer, bip_buffer, oneshot, mpsc_light) are for thread-per-core executors such as monoio and glommio.

## Maintenance

Active single-author crate (0.7.0 published 2026-10-09, about 59.7k crates.io downloads, 3 stars, 42 commits) with a changelog that documents soundness fixes; MIT is declared in Cargo.toml and the README but the repo has no LICENSE file, and minor releases have broken APIs, so pin the version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARKS.md does give 1.29 ns for Cynosure against 2.46 ns for rigtorp::SPSCQueue and 0.79 ns for a hand-rolled C11 ring on an Apple M4 Max. The C/C++ harness is not in the repository (benches/ holds only Rust criterion suites, and spsc_compare.rs and Cargo.toml mention neither rigtorp nor ringbuffer-spsc), and the C/C++ compiler and flags are not stated, so these are first-party numbers without reproducible methodology: tier C.
- **Verifier notes:** Confirmed at C: the numbers match BENCHMARKS.md, but the rigtorp and C11 harness is unpublished and its flags are unknown. same_algorithm and same_opt_level cannot be checked without that code, so the fields were left as recorded. The project's own C11 ring beating Cynosure by about 1.6x means the rigtorp win is not a Rust-over-C++ language result. Metadata checked: MIT (no LICENSE file), 3 stars, last commit 2026-10-09, crate about 59.6k downloads.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/README.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/benches/spsc_compare.rs>
  - <https://github.com/zk2u/cynosure>
  - <https://github.com/zk2u/cynosure/commits/main>
  - <https://crates.io/api/v1/crates/cynosure>
- **Sources the enricher read:**
  - <https://github.com/zk2u/cynosure>
  - <https://github.com/zk2u/cynosure/commits/main/BENCHMARKS.md>
  - <https://github.com/zk2u/cynosure/commits/main/src/site_d/ringbuf.rs>
  - <https://github.com/zk2u/cynosure/tree/main/src/site_d>
  - <https://github.com/zk2u/cynosure/issues?q=is%3Aissue>
  - <https://github.com/zk2u/cynosure/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/README.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/MIRI.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/.miri.toml>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/justfile>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/benches/README.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/benches/spsc_compare.rs>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/src/hints.rs>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/src/site_d/ringbuf.rs>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/src/site_d/notify.rs>
  - <https://raw.githubusercontent.com/zk2u/cynosure/HEAD/src/site_d/padding.rs>
  - <https://raw.githubusercontent.com/zk2u/cynosure/5f4601cf651199e52aa5fa87b1ba86b4f665d2ea/src/site_d/ringbuf.rs>
  - <https://raw.githubusercontent.com/zk2u/cynosure/5f4601cf651199e52aa5fa87b1ba86b4f665d2ea/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/zk2u/cynosure/8557608/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/rigtorp/SPSCQueue/HEAD/include/rigtorp/SPSCQueue.h>
  - <https://raw.githubusercontent.com/crossbeam-rs/crossbeam/HEAD/crossbeam-utils/src/cache_padded.rs>
  - <https://crates.io/api/v1/crates/cynosure>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/zk2u/cynosure`) · [data/wave14/enrich/raw/github_com_zk2u_cynosure.json](../../../data/wave14/enrich/raw/github_com_zk2u_cynosure.json) (enrichment confidence 0.6)

</details>
