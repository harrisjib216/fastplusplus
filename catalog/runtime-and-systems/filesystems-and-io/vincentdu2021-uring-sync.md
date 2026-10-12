# uring-sync

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Linux io_uring directory copier and kTLS network sender for many-small-file trees; beats cp -r locally and rsync -az over SSH.

| | |
|---|---|
| **Beats** | cp -r (read/write syscalls); rsync over SSH for network |
| **Claimed result** | 4.2x faster than cp -r (5.4s vs 22.7s, 100K x 100KB); 1.5x on 100K x 4KB (5.14s vs 7.67s); 3.2x on GCP pd-standard (19s vs 60s); 58% faster than rsync over network (165s vs 390s, 9.7GB). |
| **Workload** | Local copy of 100K x 100KB and 100K x 4KB files on NVMe, cold cache; and 9.7GB laptop-to-GCP transfer with kTLS. |
| **Metric** | throughput |
| **Hardware** | Local NVMe on an unnamed Ubuntu laptop (CPU model not stated); GCP pd-standard VM |
| **Adoption** | 4 stars |
| **Last commit** | 2026-01-07 |
| **Links** | [repository](https://github.com/VincentDu2021/uring_sync) · [benchmark](https://github.com/VincentDu2021/uring_sync/blob/main/docs/BENCHMARKS.md) |

## Verdict

First-party, apparently single runs on an unnamed laptop NVMe (Ubuntu 24.04, kernel 6.14, compiler and CPU not stated, build flags -O3 -march=native from the Makefile), cold cache: cp -r 22.7 s vs 5.4 s for 100K files of about 100 KB (4.2x) and 7.67 s vs 5.14 s for 100K files of about 4 KB +/-75% (1.5x); 60 s vs 19 s on GCP pd-standard and about 2.15x on pd-balanced. Over the public internet to a GCP VM, the sender-side time for 9.7 GB / 100K files was 165 s with kTLS vs 390 s for rsync -az over SSH (2.36x, the README's "58% faster" is time saved) and 16.4 s vs 24.8 s for 589 MB, with plaintext over an SSH tunnel at 366 s.

## Use it when

- Copying trees of 10^4-10^6 small or medium files (ML datasets, 4-200 KB each) between local NVMe or cloud block volumes on Linux 5.7+.
- Cold-cache bulk copies where per-file syscall latency dominates and a single thread with a deep queue (-j 1 -q 64) can keep the device busy; on network block storage use -j 4 -q 128.
- One-shot bulk push of a dataset to a cloud VM you control, where you can run the receiver yourself and ssh/rsync CPU cost is the bottleneck.
- As a readable reference for an io_uring per-file state machine with buffer and pipe pools (about 1,400 lines of C++20).

## Skip it when

- Whenever confidentiality matters on the network path: the HELLO message carries the pre-shared secret in cleartext before kTLS is turned on, and both HKDF nonces also travel in cleartext, so a passive observer can derive the AES-128-GCM keys (docs/NETWORK_DESIGN.md nonetheless lists network sniffing as protected); treat --tls as obfuscation and tunnel over SSH or WireGuard instead.
- Incremental sync, resume, or preserving owners, timestamps, xattrs, hard links or symlinks: only regular files and mode bits are copied, every file is re-sent, and nothing is fsynced.
- Small network transfers: on 10K x 6 KB (60 MB) the kTLS mode was slower than rsync (2.98 s vs 2.63 s), and --splice with kTLS was 2.9x slower than read/send.
- Non-Linux platforms or kernels older than 5.7 (IORING_OP_SPLICE), or kernels without CONFIG_TLS.
- Production use without review: 10 commits, 4 stars, no releases, no issue tracker activity, a single author.

## How it is fast

Local mode scans the tree, sorts files by inode number, then runs a per-file state machine (openat, statx, openat, splice in/out or read/write, close, close) on one io_uring per worker with 64 files in flight by default, so opens, I/O and closes for many files overlap and are submitted in batches; data moves file to pipe to file with IORING_OP_SPLICE and the chunk size is auto-tuned from the file-size distribution. Network mode uses plain blocking read/send per file (the io_uring network path cannot be combined with --tls) with AES-128-GCM done in the kernel via kTLS, so user CPU stays near zero (0.3-0.4 s user vs rsync's 4 s on the same data).

## Compared with alternatives

Against fcp and wcp (both parallel cp replacements that beat cp -r), pick uring-sync only if you specifically want a single-thread io_uring design or the built-in network sender; fcp reports about 10x on a kernel tree and wcp has a broader benchmark table, both with more users. Against copy-fast it is the more complete tool, and liburing is the library it is built on if you want to write your own.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | liburing, fmt, OpenSSL libcrypto (HKDF for kTLS keys); gtest for unit tests |
| **Minimum toolchain** | C++20 (GCC 10+ or Clang 12+); Makefile builds with -O3 -march=native |
| **Platforms** | Linux only: io_uring 5.1+, IORING_OP_SPLICE 5.7+, kTLS TX 4.13+ / RX 4.17+; authors measured on Ubuntu 24.04, kernel 6.14 |
| **Thread safety** | not applicable (CLI tool); each worker thread owns its own io_uring, buffer pool and pipe pool and pulls from a shared mutex-protected work queue |
| **Drop-in for the baseline** | partial: local mode replaces `cp -r src/. dst/` for regular files (no symlinks, ownership or timestamps); network mode is not a drop-in for rsync (needs its own receiver, no delta transfer) |

## Gotchas

- The read/write fallback in src/main.cpp advances the file offset by the read size, not by the write completion's result, so a short write would silently leave a hole; a read returning 0 before the expected size (file shrank during copy) would loop forever. Neither path is hit in the normal splice mode on regular files, but there is no post-copy size check.
- The receiver prints the secret to stdout on start and compares it with a plain string compare; the secret is also passed on the command line, so it shows up in ps and shell history.
- The sender exits right after writing ALL_DONE without waiting for the receiver to acknowledge or flush, so `time` on the sender (how all network numbers were taken) excludes the receiver's tail of writes, while rsync's time includes remote completion.
- Benchmark data comes from /dev/urandom, so rsync -az spent CPU compressing incompressible data, which inflates the rsync baseline; tests/perf/lib/common.sh also times `rm -rf` of the previous destination inside each cp and uring-sync run and never syncs dirty pages, so writeback is outside the measured time for both tools.

## Known shortcomings

- Security bug: the HELLO message sends the PSK secret in cleartext before kTLS and the nonces are cleartext too, so a passive sniffer can derive the AES-128-GCM keys; NETWORK_DESIGN.md still claims sniffing is protected. Benchmarks: sender-side `time` skips receiver completion; rsync -az compressed /dev/urandom data, inflating the baseline; the bench timing includes rm -rf. The fallback read/write path ignores the short-write result (src/main.cpp).

## Caveats and trade-offs

First-party numbers, apparently single runs; CPU model and compiler flags not stated; baseline is cp -r, not a raw read/write or io_uring baseline; speedup depends on many-small-file workloads (only 1.5x on 100K x 4KB locally). Network rsync baseline was run as rsync -az (compression on, SSH encryption) against uring-sync plaintext-protocol with kTLS AES-128-GCM; on 10K x 6KB (60MB) uring-sync kTLS was slower than rsync (2.98s vs 2.63s), and 34% faster at 589MB. kTLS + splice mode measured 2.9x slower than read/send in its own docs. Pre-shared-secret protocol, not a drop-in rsync replacement (no delta transfer).

Linux-only (io_uring, splice, kTLS need recent kernels); copy-tool, not a general library; single worker with deep queue design.

## Maintenance

Ten commits from one author between late 2025 and 2026-01-07, MIT-licensed, no releases or issues; small enough to read and adapt for local copies, but its network encryption is not secure as written.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/BENCHMARKS.md shows every claimed number (cp -r 22.7s vs 5.4s and 7.67s vs 5.14s on local NVMe; 60s vs 19s on GCP pd-standard; rsync 390s vs 165s for 9.7GB) with bench scripts in tests/perf, but CPU model, compiler and flags are not stated, so first-party C.
- **Verifier notes:** All numbers check out; GCP 3.2x row is ml_large (100K x 4KB). Metadata matches (4 stars, MIT, last commit 2026-01-07).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/VincentDu2021/uring_sync>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/README.md>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/docs/BENCHMARKS.md>
  - <https://github.com/VincentDu2021/uring_sync/commits>
- **Sources the enricher read:**
  - <https://github.com/VincentDu2021/uring_sync>
  - <https://github.com/VincentDu2021/uring_sync/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/README.md>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/docs/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/Makefile>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/src/net.cpp>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/src/net_uring.cpp>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/include/ring.hpp>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/include/common.hpp>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/include/protocol.hpp>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/include/ktls.hpp>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/tests/perf/bench.sh>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/tests/perf/lib/common.sh>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/tests/perf/gen_data.sh>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/docs/DESIGN.md>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/docs/NETWORK_DESIGN.md>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/docs/blog/blog-io-uring-file-copier.md>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/docs/blog/blog-ktls-vs-rsync.md>
  - <https://raw.githubusercontent.com/VincentDu2021/uring_sync/HEAD/LICENSE>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/vincentdu2021/uring_sync`) · [data/wave11/enrich/raw/github_com_vincentdu2021_uring_sync.json](../../../data/wave11/enrich/raw/github_com_vincentdu2021_uring_sync.json) (enrichment confidence 0.8)

</details>
