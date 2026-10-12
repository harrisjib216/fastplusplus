# see (see::sync)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Runtime-agnostic watch (latest-value broadcast) channel with sync and single-threaded variants; beats tokio::sync::watch at 1, 4 and 64 subscribers.

| | |
|---|---|
| **Beats** | tokio::sync::watch |
| **Claimed result** | Up to 2.3x faster than tokio::sync::watch at 1 subscriber (84.9us vs 213.8us) and 11-23% faster at 4 and 64 subscribers; tokio is faster at 16 subscribers (1.14ms vs 1.52ms) |
| **Workload** | Criterion benches/comparison.rs 'SPSC/MPSC Throughput' group, which appears to be the source of the README table (same 1/4/16/64 receiver counts): time to deliver 1,000 sends of a 1 KB payload to N receiver tasks on a tokio multi-thread Runtime, see::sync vs tokio::sync::watch |
| **Metric** | latency |
| **Hardware** | Intel Core i5-11300H |
| **Compiler and flags** | Rust nightly (flake.nix, version unpinned); cargo bench profile defaults; Criterion 0.7 |
| **Adoption** | 15 stars |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/compio-rs/see) · [benchmark](https://github.com/compio-rs/see#performance-advantages-sync-version) |

## Verdict

In the author's Criterion benchmark (benches/comparison.rs, 'SPSC/MPSC Throughput') on an Intel Core i5-11300H with a tokio 1.48 multi-thread Runtime and an unpinned nightly rustc, one task sends 1,000 1 KB arrays to N receiver tasks: see::sync 84.9 us vs tokio::sync::watch 213.8 us at N=1 (the README says 2.3x, but its numbers give about 2.5x), 350.6 vs 388.6 us at N=4, 1.52 vs 1.14 ms at N=16 (tokio wins) and 2.17 vs 2.67 ms at N=64. Watch channels coalesce updates, and the receivers' marker byte ((999 as u8) = 231) also appears at i=231, 487 and 743, so the benchmark mostly measures send cost plus task spawn and wakeup, not per-message delivery.

## Use it when

- Code that runs on smol, compio or another non-tokio executor and needs tokio-style watch semantics (latest value, coalesced updates) without a tokio dependency.
- Single-threaded or thread-per-core runtimes such as compio: use see::unsync. The README measures about 4.8 us vs 38.6 us per 1,000 SPSC messages against see::sync, and a 3.5 ns vs 14.3 ns borrow.
- Send-heavy config or state broadcast with 1-4 subscribers, where the per-send cost dominates. The author measured 84.9 us vs 213.8 us per 1,000 sends of a 1 KB value to 1 subscriber.
- Replacing tokio's watch in a library that must stay runtime-agnostic, where you control every changed() loop and can audit it.

## Skip it when

- About 16 subscribers: in the author's own table tokio is faster (1.14 ms vs 1.52 ms). Scaling is not monotone, and there are no numbers above 64 subscribers or on a second CPU.
- As a transparent drop-in inside existing tokio code. changed() has different semantics (see gotchas), there is no Receiver::is_closed, and the error and guard types differ.
- Multi-threaded use where missing the final update is unacceptable. see::sync::Receiver::changed() has a check-then-listen window that can lose a wakeup (see gotchas). The tests use only single-threaded executors (compio::test, smol::block_on), with no loom or multi-thread stress tests.
- When you need a mature dependency: version 0.1.2, 13 commits, 15 stars, about 12.9k crates.io downloads, and 2 reverse dependencies (openraft-rt-compio, and synchrony as an optional dependency).
- When every message must arrive. Like any watch channel, see keeps only the latest value, so use an mpsc or broadcast channel instead.

## How it is fast

The README does not say why see::sync beats tokio; the source copies tokio's own watch layout (an atomic version counter stepping by 2, the least significant bit as the closed flag, the value behind an RwLock). The visible difference is notification: each send makes one event-listener notify(usize::MAX), which takes one mutex, while tokio's BigNotify calls notify_waiters on 8 sharded Notify objects and locks each shard's waiter mutex on every send. see also skips tokio's cooperative-scheduling budget, and the lock is not the difference: the benchmark's tokio `full` feature turns on parking_lot, so both sides use parking_lot's RwLock. see::unsync gets its further 4-8x by replacing atomics and locks with Rc, RefCell and Cell.

## Compared with alternatives

No sibling is a synchronization primitive: monoio, ringline, exec-rs and zokio replace the whole tokio runtime, while see replaces only the watch channel and runs on tokio, smol or compio. Pick it when the event loop is fine and the bottleneck, or the tokio dependency, is the watch channel.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | event-listener 5.4, parking_lot 0.12, local-event 0.1, futures-util 0.3 (alloc only), scopeguard 1.2, thiserror 2 |
| **Minimum toolchain** | Rust edition 2024 (so Rust 1.85+). No rust-version is declared, and CI tests nightly only (ubuntu-22.04). |
| **Platforms** | any (pure Rust, no platform-specific code); CI runs only on Linux x86-64 |
| **Thread safety** | see::sync: Sender and Receiver are Send + Sync when T is Send + Sync (Arc plus parking_lot::RwLock). see::unsync: Rc and RefCell, so !Send and !Sync, for one thread only. |
| **Drop-in for the baseline** | partial — the method names match tokio::sync::watch, but changed(&self) does not mark the value seen (you must call borrow_and_update), changed() returns Err as soon as the sender drops even if an unseen value is pending (tokio returns Ok first), there is no Receiver::is_closed, and SendError, RecvError and Guard are different types |

## Gotchas

- A tokio-style `while rx.changed().await.is_ok() { let v = rx.borrow(); ... }` loop becomes a busy spin. In see, only borrow_and_update, mark_unchanged and wait_for advance the receiver's version; changed() does not.
- In see::sync, changed() loads the version, then calls Event::listen(), then awaits, without re-checking in between. event-listener's docs say a notification sent while no listener is registered 'simply gets lost', and tell you to re-check after listen(). tokio registers first and then checks. So a send that lands in that window can go unnoticed until the next send or until the sender drops. see's own Sender::closed() does use the double-check.
- In see::unsync, Guard holds a RefCell Ref. If any task keeps a Guard alive (for example across an .await), send() on the same thread hits RefCell::borrow_mut and panics. In see::sync, the same pattern deadlocks on the non-reentrant parking_lot RwLock.
- The `stream` feature uses unsafe code: it reuses the boxed future's allocation by comparing layouts and casting pointers (future_store.rs), and BoxedFutureStore has an unconditional `unsafe impl Sync`.

## Known shortcomings

- Likely lost-wakeup race in see::sync::Receiver::changed(): it checks the version, then listens and awaits with no re-check, which event-listener's docs warn loses notifications (tokio registers first); a receiver can miss the final update. changed() takes &self, doesn't mark the value seen, and errors as soon as the sender drops even with an unread value, so a tokio-style changed()+borrow() loop spins; no is_closed; only a partial drop-in. README's 2.3x at 1 subscriber is \~2.5x by its own numbers. The benchmark mostly measures send cost plus spawn/wakeup (watch keeps only the latest value; the u8 marker 231 recurs, so receivers can stop early); both sides use parking_lot. Tests only on single-threaded executors, no loom; nightly CI on one OS; no rust-version. see::unsync panics if a Guard is held while the thread sends (RefCell); the stream feature has unsafe box reuse and an unconditional unsafe impl Sync. v0.1.2, 13 commits.

## Caveats and trade-offs

Not a uniform win: tokio is faster at 16 subscribers, and the README says so. The README does not name the bench group behind the table. The comparison runs on a tokio multi-threaded runtime, not single-threaded as first recorded (only the sync vs unsync numbers are single-threaded). The rustc version is unpinned. It measures a watch-channel sync primitive, not a reactor or event loop.

Runtime-agnostic (works with tokio, smol, compio) but the unsync variant sacrifices thread-safety (Rc/RefCell/Cell) for speed; sync variant uses parking_lot::RwLock and is \~4-8x slower than unsync in single-threaded use.

## Maintenance

Active (v0.1.2 published 2026-08-20 under the compio-rs org, MIT OR Apache-2.0) and small enough to add or vendor, but young (0.1.x, 13 commits, 4 merged PRs, no issues filed) and not stress-tested across threads.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table compares see::sync with tokio::sync::watch at 1/4/16/64 subscribers (84.9us vs 213.8us, 350.6 vs 388.6us, 1.52 vs 1.14ms, 2.17 vs 2.67ms) on an Intel Core i5-11300H. The Criterion code is public (benches/comparison.rs), but the rustc version is not stated beyond an unpinned nightly in flake.nix, so this is first-party partial methodology: tier C.
- **Verifier notes:** Numbers match the README exactly. Repo metadata checks out: Apache-2.0 on GitHub plus LICENSE-MIT, Cargo.toml 'MIT OR Apache-2.0', 15 stars, last commit 2026-08-20, not a fork. The workload field was wrong to say single-threaded, so I fixed it.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/compio-rs/see>
  - <https://github.com/compio-rs/see#performance-advantages-sync-version>
  - <https://github.com/compio-rs/see/blob/master/benches/comparison.rs>
  - <https://github.com/compio-rs/see/blob/master/Cargo.toml>
  - <https://github.com/compio-rs/see/blob/master/flake.nix>
- **Sources the enricher read:**
  - <https://github.com/compio-rs/see>
  - <https://github.com/compio-rs/see#performance-advantages-sync-version>
  - <https://raw.githubusercontent.com/compio-rs/see/master/README.md>
  - <https://raw.githubusercontent.com/compio-rs/see/master/Cargo.toml>
  - <https://raw.githubusercontent.com/compio-rs/see/master/Cargo.lock>
  - <https://raw.githubusercontent.com/compio-rs/see/master/flake.nix>
  - <https://raw.githubusercontent.com/compio-rs/see/master/src/lib.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/src/sync.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/src/unsync.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/src/state.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/src/stream.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/src/future_store.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/benches/comparison.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/benches/single_thread.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/tests/compio_sync.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/tests/smol.rs>
  - <https://raw.githubusercontent.com/compio-rs/see/master/.github/workflows/test.yml>
  - <https://raw.githubusercontent.com/compio-rs/see/master/LICENSE-MIT>
  - <https://github.com/compio-rs/see/tree/master/tests>
  - <https://github.com/compio-rs/see/tree/master/.github/workflows>
  - https://github.com/compio-rs/see/pulls (via gh search issues --repo compio-rs/see --include-prs)
  - <https://crates.io/api/v1/crates/see>
  - <https://crates.io/api/v1/crates/see/reverse_dependencies>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/master/tokio/src/sync/watch.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/master/tokio/src/sync/notify.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/master/tokio/Cargo.toml>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/master/tokio/src/loom/std/mod.rs>
  - <https://raw.githubusercontent.com/smol-rs/event-listener/master/src/lib.rs>
  - <https://raw.githubusercontent.com/smol-rs/event-listener/master/src/intrusive.rs>
  - <https://github.com/smol-rs/event-listener/tree/master/src>
  - <https://hn.algolia.com/api/v1/search?query=%22compio-rs%2Fsee%22>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/compio-rs/see`) · [data/wave5/enrich/raw/github_com_compio_rs_see.json](../../../data/wave5/enrich/raw/github_com_compio_rs_see.json) (enrichment confidence 0.7)

</details>
