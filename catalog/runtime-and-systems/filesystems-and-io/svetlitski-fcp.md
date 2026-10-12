# fcp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Parallel Rust replacement for the common cp -R cases; about 10x faster than GNU cp on a Linux kernel tree on SSD.

| | |
|---|---|
| **Beats** | GNU cp |
| **Claimed result** | Linux kernel tree: \~675ms vs cp \~6.02s (about 10x); 13x512MB: \~8s vs \~11.3s (1.4x); macOS kernel tree about 6x, large files 822x (copy-on-write) |
| **Workload** | Copy Linux kernel source tree and a directory of 13x512MB files, on AWS a1.metal XFS SSD and macOS APFS |
| **Metric** | latency |
| **Hardware** | AWS a1.metal (16 CPUs, 32 GiB, SSD, XFS); 2018 MacBook Pro i9 APFS |
| **Adoption** | 857 stars |
| **Last commit** | 2026-04-23 |
| **Links** | [repository](https://github.com/Svetlitski/fcp) · [benchmark](https://github.com/Svetlitski/fcp) |

## Verdict

A Criterion harness (benches/fcp_benchmark.rs: 60 s warm-up, 50 samples for the kernel tree, 100 for large files, destination removed outside the timed region) runs 'cp -R' against fcp. On an AWS a1.metal (Graviton, 16 vCPU, SSD, XFS) the Linux kernel tree took about 675 ms vs 6.02 s (about 9x) and 13x512 MB took about 8 s vs 11.3 s (1.4x). On a 2018 MacBook Pro (i9, APFS) the figures were 5.1 s vs 30 s (6x), and 4.5 ms vs 3.7 s for large files (822x, because of clones). Runs are warm-cache; compiler, run date and GNU cp version are not stated, which matters because newer coreutils cp also changed its copy path.

## Use it when

- Copying large trees of many small files (source checkouts, node_modules, build outputs) on NVMe/SATA SSD where cp is bound by one thread issuing syscalls.
- macOS on APFS, where large files become near-instant clones.
- Scripts and dev workflows that only need plain recursive copy semantics and can tolerate missing cp options.
- Linux or macOS hosts with many cores and an SSD-backed local filesystem.

## Skip it when

- HDDs: the README warns that parallel copying may perform poorly on spinning disks.
- When you need cp -p/-a semantics (timestamps, ownership, xattrs, ACLs): the code copies only mode bits via std::fs::copy and creates directories with the source mode.
- Large-file copies on Linux: the README's own number is only 1.4x (8 s vs 11.3 s), and issue #41 reports fcp slower than cp (9:39 vs 8:10) on a btrfs RAID1 NVMe workstation.
- FAT32 targets: issue #34 (open) reports a futex deadlock after 8-10 GB copied to a FAT32 USB drive.
- Windows: Unix only (issue #33 closed as wontfix).

## How it is fast

Each directory is read serially, then its entries are copied in parallel with a rayon work-stealing pool (into_par_iter), so directory walking and file copies spread over all cores and the SSD sees a higher queue depth. Regular files go through Rust's std::fs::copy, which uses copy_file_range on Linux and fcopyfile/fclonefileat on macOS; on APFS that becomes a copy-on-write clone, which is where the 822x large-file number comes from. There is no custom I/O engine (no io_uring, no buffer tuning).

## Compared with alternatives

Pick fcp over wcp or uring-sync when you want a packaged, widely distributed (Homebrew, AUR, NixOS) parallel cp with macOS clone support; wcp's io_uring engine reports a bigger large-file win on Linux (20x512 MiB in 3.97 s vs cp 8.44 s), and uring-sync targets many-file copies and network sync.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon 1.5, nix 0.25 (criterion and a local dev_utils crate for benches only) |
| **Minimum toolchain** | README says Rust 1.53.0, but Cargo.toml uses edition 2021, which needs Rust 1.56 or newer |
| **Platforms** | Unix-like only (Linux, macOS); CI and packages for Arch AUR, NixOS, Homebrew |
| **Thread safety** | Not applicable (CLI); internally runs a rayon pool sized to all cores, with no flag to limit parallelism (speed/IOPS limit request #18 closed) |
| **Drop-in for the baseline** | partial — covers 'cp -R SRC... DEST' only; rejects every cp option, and always recurses into directories |

## Gotchas

- Errors are printed as they happen and the copy continues; only the exit code reports that something failed.
- Mode bits, including setuid/setgid, are carried over; issue #48 (open) asks for a private security contact about preserving privileged mode bits.
- copy_single's self-overwrite check compares only inode numbers, not device plus inode (reject_self_copies does use both), so a cross-filesystem copy whose inode numbers happen to match is refused.
- Linux reflink (FICLONE) support is still an open request (#11); any Linux CoW benefit comes only from what copy_file_range does in the kernel.

## Known shortcomings

- Rust, not C++. The speedup is a rayon parallel copy per directory plus std::fs::copy (APFS clone gives the 822x). Open issues: 34 (deadlock on FAT32), 41 (fcp slower than cp on btrfs RAID1: 9:39 vs 8:10) and 48 (privileged mode bits kept). README says Rust 1.53 but edition 2021 needs 1.56. The copy_single self-overwrite check compares inode only, not device (not behind the numbers).

## Caveats and trade-offs

Results are shown as images, with averages taken from the alt text. Benchmark code is public (benches/fcp_benchmark.rs, Criterion, 60s warm-up, 50 samples, cp -R vs fcp), but the toolchain and flags are not stated, and the a1.metal CPU (AWS Graviton) is not named on the page. The runs are warm-cache with no cache drop. The macOS 822x large-file figure comes from APFS copy-on-write clones (fclonefileat/fcopyfile), not from copying data. The README warns of poor performance on HDDs. Rust CLI, not a C/C++ library.

Only common cp use cases; tuned for SSD, may be slow on HDD; Unix only.

## Maintenance

Small, BSD-3-Clause, 857 stars, last commit 2026-04-23, but several open issues (deadlock #34, btrfs slowdown #41, security #48) have no maintainer reply; fine to use as a dev tool, not a vetted cp replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's charts (numbers given in their alt text) compare fcp against cp -R, and the public Criterion harness benches/fcp_benchmark.rs runs both; compiler/flags are not stated and the Linux CPU is given only as AWS a1.metal, so not A; first-party, so C.
- **Verifier notes:** All numbers match the README. BSD-3-Clause, 857 stars, last commit 2026-04-23, not archived.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** public Criterion harness
- **Pages the verifier opened:**
  - <https://github.com/Svetlitski/fcp>
  - <https://github.com/Svetlitski/fcp/commits/master>
  - <https://github.com/Svetlitski/fcp/tree/master/benches>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/README.md>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/benches/fcp_benchmark.rs>
- **Sources the enricher read:**
  - <https://github.com/Svetlitski/fcp>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/README.md>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/benches/fcp_benchmark.rs>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/Svetlitski/fcp/HEAD/src/filesystem.rs>
  - <https://github.com/Svetlitski/fcp/issues?q=is%3Aissue>
  - <https://github.com/Svetlitski/fcp/issues/11>
  - <https://github.com/Svetlitski/fcp/issues/34>
  - <https://github.com/Svetlitski/fcp/issues/41>
  - <https://github.com/Svetlitski/fcp/issues/48>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/svetlitski/fcp`) · [data/wave11/enrich/raw/github_com_svetlitski_fcp.json](../../../data/wave11/enrich/raw/github_com_svetlitski_fcp.json) (enrichment confidence 0.8)

</details>
