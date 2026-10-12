# gocrack (wa7nt)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Go (hand-written AVX2 assembly kernels)` · `no license` · 🟢 active

> Go program with hand-written 8-way AVX2 multi-buffer MD5/SHA-1 compression kernels; beats single-stream crypto/md5 and crypto/sha1 on aggregate throughput.

| | |
|---|---|
| **Beats** | Go standard library crypto/md5 and crypto/sha1 (single-stream hashing) |
| **Claimed result** | md5x8 kernel alone 48 MH/s vs crypto/md5 5.7 MH/s (about 8.4x, derived from page data); sha1x8 compare path 22 MH/s vs crypto/sha1 4.1 MH/s (about 5.4x, derived); whole MD5 brute-force pipeline 38 MH/s on 1 core and 151 MH/s on 4 threads; kernels at 88-90% of a measured ALU-op ceiling |
| **Workload** | hashing short candidates (up to 55 bytes, one padded block) for brute-force and wordlist password recovery, 8 candidates per AVX2 register (multi-buffer), 1 core |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-7360U (Skylake, 2 physical cores, AVX2, no AVX-512, no SHA-NI) |
| **Compiler and flags** | Go 1.26 darwin/amd64; no flags stated |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/wa7nt/gocrack) · [benchmark](https://github.com/wa7nt/gocrack) |

## Verdict

First-party README table on an Intel Core i5-7360U (Skylake, AVX2, no AVX-512/SHA-NI), Go 1.26 darwin/amd64, no repeat statistics: md5x8 compression kernel 48 MH/s vs crypto/md5 5.7 MH/s (about 8.4x, derived; but compression-only vs full md5.Sum), whole MD5 brute-force pipeline 38 MH/s on 1 core (about 6.7x over stdlib) and 151 MH/s on 4 threads; sha1x8 22 MH/s vs a crypto/sha1 4.1 MH/s row that has no harness in the repo. Kernels reported at 88-90% of a measured per-machine ALU-op ceiling.

## Use it when

- You need to study a clean, heavily-commented example of an 8-lane AVX2 multi-buffer hash compression kernel written in Go's Plan 9 assembler, with an unusually detailed account of the assembler traps and A/B measurement methodology.
- Aggregate throughput over many independent short (&lt;=55 byte) one-block inputs matters more than per-message latency, on an AVX2 x86-64 CPU.
- You want the compare-in-kernel idea (return a lane bitmask, skip digest stores on a miss) as a reference for a filter or matching workload.
- Go 1.24+ and an AVX2 core (it falls back to nothing: there is no scalar path in the kernels, only the avx2Enabled guard).

## Skip it when

- You need a maintainable, importable dependency: it is a program with internal/ packages (not go-get-able), has no LICENSE file (all-rights-reserved by default, so not copyable), 1 star, and two commits all dated 2026-09-28.
- Messages longer than 55 bytes, multi-block inputs, or any keyed/iterated KDF (bcrypt, scrypt, PBKDF2): rejected or out of scope; only MD5 and SHA-1 single-block are implemented.
- Per-message latency: a multi-buffer kernel needs 8 inputs in flight and does not speed up a single hash.
- Non-x86-64 or AVX2-less hardware: no AVX-512, SHA-NI, or NEON path; no portable fallback kernel.
- You want a like-for-like replacement for crypto/md5 or crypto/sha1: the API is a program, not a Hash, and the baselines are single-stream scalar assembly while this is 8-lane aggregate.

## How it is fast

Standard SIMD multi-buffer hashing: 8 independent single-block messages are transposed so word w of every lane is one VMOVDQU, and the scalar MD5/SHA-1 round functions run on whole YMM registers as pure bitwise identities (e.g. F(b,c,d)=d^(b&(c^d))), avoiding byte shuffles. State registers are statically assigned across all 64/80 steps by rotating lane roles rather than moving data. The input buffer itself is the counter: internal/cand writes brute-force candidates directly into the transposed layout with a precomputed (carry, character) table, which the author reports cut generation from 28.3 to 4.97 ns per input. The author measured both kernels at 88-90% of a machine-specific ALU-op ceiling (md5x8 640 ops/block at 3.8 ops/ns; sha1x8 1404 at 3.9).

## Compared with alternatives

The closest catalogued sibling is minio/md5-simd, which is also an 8-lane AVX2/AVX-512 multi-buffer MD5 in Go assembly beating crypto/md5 (3.31x aggregate on 4 vCPUs) but is a maintained, importable, licensed package; prefer minio/md5-simd for production and gocrack only as a readable single-file-per-kernel reference that also covers SHA-1 and documents the Go-assembler pitfalls. Against the hashing siblings lukechampine/blake3, zeebo/blake3 and animetosho/md5-optimisation, gocrack is the one to read specifically for multi-buffer transposed-layout MD5/SHA-1 and compare-in-register matching.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standard library only; go.mod declares module gocrack, go 1.24) |
| **Minimum toolchain** | Go 1.24 per go.mod (README states it was built with Go 1.26 darwin/amd64) |
| **Platforms** | x86-64 with AVX2 only; kernels are guarded by an avx2Enabled check and have no fallback |
| **Thread safety** | not documented as an API; the program shards the brute-force space across goroutines (measured 1.87x on 2 physical cores, 76.6 MH/s on 4 with SMT) but exports no reusable concurrent hasher |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark-methodology flaw on the kernel row: internal/md5x8/bench_test.go TestBenchmarkReport times md5x8 doing compression only, on one pre-built constant transposed buffer reused every iteration (the same 8 'cand-000N' inputs), against md5.Sum([]byte("cand-0000")) which also pays digest init, padding and finalization each call. So the headline 48 vs 5.7 MH/s (about 8.4x) overstates the per-compression advantage; the whole-pipeline 1-core figure (38 MH/s, generator included) against 5.7 MH/s, about 6.7x, is the fairer comparison.
- The crypto/sha1 4.1 MH/s baseline row has no harness in the repository: internal/sha1x8/bench_test.go benchmarks only sha1x8 (digest) and sha1x8msg (match), never crypto/sha1, so that ratio is not reproducible from the repo. The README also never states which command produced its throughput table.
- The baselines (Go crypto/md5 and crypto/sha1 on amd64) are themselves hand-written scalar assembly running one stream; this is 8-lane multi-buffer vs single-stream, i.e. a throughput-vs-latency comparison, not instruction-for-instruction.
- Single machine (i5-7360U, 2 physical cores), single run, no repeat/variance statistics reported; the author notes the clock drifts enough between runs to invert a 12% result, and mitigates it only inside the same-process A/B step-form harness, not for the headline table.

## Known shortcomings

- The kernel row times compression of a constant prebuilt buffer against the full md5.Sum, so the 8.4x is overstated (pipeline about 6.7x, internal/md5x8/bench_test.go); no SHA-1 stdlib harness; no licence (reference); 1 star, 2 commits.
- Harness flaw: internal/md5x8 TestBenchmarkReport times compression only on one constant reused buffer against a full md5.Sum (init, pad, finalize), so 48 vs 5.7 MH/s (8.4x) overstates; the whole pipeline at 38 MH/s (about 6.7x) is the fairer figure. The crypto/sha1 4.1 MH/s row has no harness in the repo (sha1x8's bench times kernels only). 8-lane multi-buffer vs a single stream, one 2-core laptop, no repeat statistics, no LICENSE.

## Caveats and trade-offs

A stdlib comparison harness does exist for MD5: internal/md5x8/bench_test.go TestBenchmarkReport times md5x8 on a pre-built transposed buffer (the same 8 candidates every iteration, compression only) against md5.Sum([]byte("cand-0000")), which also pays digest init, padding and finalization, so the 48 vs 5.7 MH/s kernel ratio overstates the per-compression gain; the end-to-end brute-force pipeline (38 MH/s, generator included) is the fairer 1-core figure, about 6.7x (derived from page data). No harness for the crypto/sha1 4.1 MH/s row was found (internal/sha1x8/bench_test.go benchmarks only the sha1x8 digest and match kernels). The README does not say which command produced the table. Go's crypto/md5 and crypto/sha1 on amd64 are themselves scalar assembly, so this is 8-lane multi-buffer AVX2 against single-stream scalar code, not like-for-like latency. Single 2-core laptop, single run, no repeat statistics. No LICENSE file (usability reference). Two commits (both 2026-09-28), one star. Password-cracking tool; README says it is for authorised testing and recovery of credentials you own. Candidates limited to 55 bytes (one block).

AVX2-only, Skylake-tuned 8-lane kernels; only single-block messages (55 bytes or less); multi-buffer design raises throughput over many independent candidates but does not speed up one hash; x86-64 only.

## Maintenance

Active but brand-new and tiny (1 star, two commits 2026-09-28) with no LICENSE file, so it is reference-only, not copyable; treat the numbers as directional first-party measurements from a single 2-core laptop.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table on a named CPU (i5-7360U) and toolchain (Go 1.26 darwin/amd64), and the MD5 stdlib row has a public harness (internal/md5x8/bench_test.go TestBenchmarkReport times md5x8 against md5.Sum on a 9-byte message). The README never says which command produced the table, the crypto/sha1 4.1 MH/s row has no harness in the repo (internal/sha1x8/bench_test.go times only the 8-way kernels), and the kernel row times compression of a pre-built constant buffer against a full md5.Sum, so it stays C.
- **Verifier notes:** All numbers match the README table. The record's claim that no stdlib benchmark harness exists is wrong for MD5 (TestBenchmarkReport in internal/md5x8/bench_test.go) but right for SHA-1. Low notability (1 star, 2 commits, two weeks old); kept at C, reference only (no license).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-71 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/wa7nt/gocrack>
  - <https://github.com/wa7nt/gocrack/commits>
  - <https://github.com/wa7nt/gocrack/tree/main/cmd/gocrack>
  - <https://github.com/wa7nt/gocrack/tree/main/internal>
  - <https://github.com/wa7nt/gocrack/tree/main/internal/md5x8>
  - <https://github.com/wa7nt/gocrack/tree/main/internal/sha1x8>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/README.md>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/cmd/gocrack/main.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/md5x8/bench_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/md5x8/profile_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/md5x8/md5x8_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/sha1x8/bench_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/sha1x8/sha1x8_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/sha1x8/plain_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/wa7nt/gocrack>
  - <https://github.com/wa7nt/gocrack/tree/main/internal>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/README.md>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/go.mod>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/cmd/gocrack/main.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/md5x8/bench_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/md5x8/profile_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/md5x8/md5x8_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/sha1x8/bench_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/sha1x8/sha1x8_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/internal/sha1x8/plain_test.go>
  - <https://raw.githubusercontent.com/wa7nt/gocrack/HEAD/LICENSE>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wa7nt/gocrack`) · [data/wave13/enrich/raw/github_com_wa7nt_gocrack.json](../../../data/wave13/enrich/raw/github_com_wa7nt_gocrack.json) (enrichment confidence 0.6)

</details>
