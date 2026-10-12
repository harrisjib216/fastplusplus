# skani

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust ANI and aligned-fraction calculator for genomes and MAGs; 20-50x faster than FastANI (C++), slower than Mash at querying.

| | |
|---|---|
| **Beats** | FastANI 1.33 (C++) and Mash 2.3 (C++), bioconda builds pinned in skani-test/env.yml |
| **Claimed result** | README: sketching about 3x faster than Mash, querying about 25x faster than FastANI but slower than Mash; v0.4.0 (October 2026) claims about 2x faster than v0.3. Paper abstract (snippet only): &gt;20x faster than FastANI on fragmented, incomplete MAGs. Paper benchmark repo skani-test, /bin/time outputs at 50 threads (derived from page data): all-vs-all on 195 MAGs, skani triangle 3.30 s vs FastANI 2:58.96 (54x wall; 154.75 s vs 7142.43 s user, 46x); E. coli D3 database query, skani search 4.17 s (plus 3.55 s sketching) vs FastANI 2:44.50 (39x query-only, 21x including sketching); RefSeq all-vs-all, skani sketch 3.10 s plus triangle 11.38 s vs FastANI 3:02:24 (about 750x). Against Mash: skani sketching 3.55 s vs 18.19 s on D3 and 3.10 s vs 14.79 s on RefSeq (about 5x), but Mash dist on D3 takes 0.26 s vs skani search 4.17 s (skani 16x slower), and Mash triangle on the 195 MAGs takes 0.55 s vs 3.30 s. |
| **Workload** | Average nucleotide identity computation between prokaryotic genomes and against a database of more than 65,000 genomes. |
| **Metric** | throughput (query time) |
| **Hardware** | CPU model not stated; 50 threads (/bin/time reports 3500-4950% CPU) |
| **Compiler and flags** | skani: prebuilt binary checked into skani-test (cargo release build; flags not stated). FastANI 1.33 (fastani=1.33=h0fdf51a_1) and Mash 2.3 (mash=2.3=ha9a2dd8_3) from bioconda, build flags those of the bioconda recipes. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: approximate mapping with sparse chaining of seed matches instead of base-level alignment. |
| **Adoption** | 265 stars, 15 forks; Nature Methods 2023 paper (doi 10.1038/s41592-023-02018-3); bioconda package; pyskani Python bindings by a third party |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/bluenote-1577/skani) · [benchmark](https://github.com/bluenote-1577/skani-test) |

## Verdict

The paper's skani-test repo ran a paper-era skani binary, FastANI 1.33 and Mash 2.3 (Bioconda builds) under /bin/time -v at 50 threads on an unstated CPU. Wall times: 195 MAGs all-vs-all, skani 3.30 s vs FastANI 178.96 s (54x, user CPU 46x); E. coli K-12 against 4,351 D3 genomes, skani 4.17 s search plus 3.55 s sketch vs FastANI 164.5 s (21x in total, of which 53.7 s is FastANI building its index); RefSeq 4,233-genome all-vs-all, 14.5 s vs 3 h 2 min. Mash sketches 2.7-5x slower (GTDB, D3, RefSeq) but answers queries faster than skani.

## Use it when

- All-vs-all ANI over hundreds to thousands of bacterial or archaeal genomes or MAGs (dereplication, species or strain clustering) where FastANI takes minutes to hours: 195 MAGs in 3.30 s against 2 min 59 s at 50 threads.
- Searching a query genome against a large pre-sketched database (GTDB, 65,000+ genomes) in seconds with about 6 GB RAM.
- Incomplete or fragmented MAGs, where pure sketch distances such as Mash underestimate ANI and you also want aligned fraction.
- Memory-constrained runs (maximum RSS from /bin/time): 1.2 GiB for the 4,351-genome E. coli D3 search against 49 GiB for FastANI, and 10.2 GiB against 108 GiB for the RefSeq all-vs-all.

## Skip it when

- Pure speed screening where Mash-level approximation is enough: Mash dist took 0.26 s on D3 against 4.17 s for skani search, and Mash triangle 0.55 s against 3.30 s on the 195 MAGs.
- Distant genomes below about 82% ANI: pairs under 15% aligned fraction are not reported by default.
- When you need alignment-level ANI or exact parity with FastANI or ANIm outputs: skani is an approximation with a learned correction on top.
- Pipelines pinned to skani 0.3.x sketches: the v0.4.0 sketch format is incompatible with older binaries, and older sketches are converted on every load with a speed penalty.
- Eukaryotic or very repetitive genomes need the slower presets (--slow, c=30) per the changelog.

## How it is fast

Instead of FastANI's Mashmap-style mapping of every 3 kb query fragment, skani samples sparse k-mer seeds (FracMinHash, k=15, c=125 by default), chains seed matches between the two genomes with banded chaining, and estimates ANI from the k-mer identity inside the chained regions, with no base-level alignment. A marker k-mer screen (k=21, c=1000, inverted index) skips pairs below about 80% ANI before chaining, and triangle computes each unordered pair once because skani's ANI is symmetric. v0.4.0 adds AVX2 seed hashing, an i32 AVX2 chaining kernel, a sorted struct-of-arrays seed index with galloping search, and LSD radix sort of anchors, all with runtime AVX2 detection.

## Compared with alternatives

No sibling computes ANI; the closest catalogued tools (mosdepth for depth, rasusa for subsampling, sambamba for BAM processing) cover other pipeline steps. Pick skani whenever genome-to-genome ANI against FastANI is the job and approximate, alignment-free ANI is acceptable.

## Integration

| | |
|---|---|
| **Form** | CLI binary (cargo build, Bioconda at 0.3, prebuilt static x86-64 Linux binary) and crate (skani 0.4.0 on crates.io, API unstable) |
| **Dependencies** | Rust crates (bio, needletail, rayon, gbdt, bincode, memmap2 and others); a C compiler and make are required to build; tikv-jemallocator on musl targets |
| **Minimum toolchain** | Rust edition 2021 (no rust-version declared); release profile uses lto = true and panic = abort |
| **Platforms** | x86-64 with AVX2 fast paths and runtime detection; ARM64 and other non-x86 builds work, with -i commands fixed only in v0.3.2 (May 2026) |
| **Thread safety** | CLI parallelises with rayon via -t; library thread safety not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Default ANI values pass through a learned GBDT debiasing model (195 trees, depth 3), so output is piecewise constant. Issue #57 found about 0.2 percentage-point gaps with no reachable value near 92.5% ANI. Use --no-learned-ani for the raw estimate.
- Harness detail: the time_2328_results.sh in skani-test sets threads=1, but the checked-in times were run with -t 50, so the committed script does not reproduce them. FastANI --rl/--ql on 195 genomes runs both directions of every pair, while skani triangle computes each unordered pair once, so about 2x of the 54x is pair symmetry rather than speed per comparison.
- The roughly 750x RefSeq figure (4,233 genomes) uses triangle -E on pre-built sketches, where the marker screen discards most unrelated pairs (bacteria, archaea, viruses, fungi). The same all-vs-all through skani search took 174.8 s, about 61x faster than FastANI's 3 h 2 min including sketching. The run's glob also passed markers.bin to triangle as an input file.
- The v0.4.0 '\~2x faster' headline is first-party PR #58 data on a 100-genome all-vs-all with unstated hardware: cumulative 1.48-1.61x single-threaded and 1.41-1.42x at 30 threads with default c=125; 1.91x only with c=30. The CHANGELOG mentions an exception to 'results unchanged' that its Minor section does not list.

## Known shortcomings

- Tier B from the Nature Methods paper plus the public bluenote-1577/skani-test repo (/bin/time outputs, FastANI 1.33, Mash 2.3, 50 threads: 21-54x over FastANI) but no CPU model; the win is algorithmic, not the language; 16x slower than Mash dist; timings from the paper-era binary.
- The committed time_2328_results.sh sets threads=1 but the checked-in times ran at -t 50, so the script does not reproduce them; FastANI --rl/--ql runs both directions of each pair while skani triangle runs each once (about 2x of the 54x); the RefSeq 750x uses triangle -E with the marker screen, and skani search mode took 174.8 s (about 61x); the v0.4 '2x faster' is PR #58's self-measured 1.41-1.61x at the default c=125 (1.91x only at c=30) with hardware unstated; default ANI passes through a learned GBDT model whose output is piecewise constant (issue #57).

## Caveats and trade-offs

The speedup is algorithmic, not a language effect: skani does approximate mapping with sparse chaining of k-mer seeds and no base-level alignment, while FastANI uses Mashmap-style mapping of 3 kb fragments, so same_algorithm is false and the Rust-vs-C++ question is not answered. skani is slower than Mash at querying (16x on D3, 6x on the 195-MAG triangle) and only beats it at sketching. The timings come from the paper-era binary in skani-test, not the current v0.4.0. No CPU model is given, and the FastANI and Mash builds are bioconda defaults. The RefSeq row compares outputs filtered differently (skani -E edge list vs FastANI full output), so the \~750x figure is indicative only. The skani README says a C compiler is needed to build (C dependency). The README's 25x figure has no raw numbers on the README page itself. The wave-14 category is a poor fit, since the win comes from the method, not the language. [retier] The speedup is algorithmic, not a language effect: skani does approximate mapping with sparse chaining of k-mer seeds and no base-level alignment, while FastANI maps 3 kb fragments, so the Rust-vs-C++ question is not answered; skani is slower than Mash at querying (16x on D3, 6x on the 195-MAG triangle). The committed time_2328_results.sh sets threads=1 but the checked-in times ran at -t 50, so the script does not reproduce them; FastANI --rl/--ql runs both directions of each pair while skani triangle runs each once (about 2x of the 54x); the RefSeq 750x uses triangle -E with the marker screen, and skani search mode took 174.8 s (about 61x). The v0.4 '2x faster' is PR #58's self-measured 1.41-1.61x at the default c=125 (1.91x only at c=30) with hardware unstated. Default ANI passes through a learned GBDT model whose output is piecewise constant (issue #57); the timings come from the paper-era binary, not the current release.

Approximate ANI without base-level alignment; accuracy is 'almost as accurate' as BLAST-based methods per README.

## Maintenance

Actively maintained (v0.4.0 released 2026-10-11, MIT per the LICENSE file while Cargo.toml says MIT OR Apache-2.0), Nature Methods 2023 paper and Bioconda package. The benchmarks predate v0.4.0, and the Rust API is documented as unstable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. The peer-reviewed Nature Methods 2023 paper (abstract seen via snippet: &gt;20x faster than FastANI on fragmented MAGs) has a public benchmark repo, bluenote-1577/skani-test, whose time_results.sh and time_2328_results.sh run skani, FastANI 1.33 and Mash 2.3 (bioconda pins in env.yml) under /bin/time -v, with the outputs checked into times/. It is not A because no CPU model or compiler flags are given.
- **Verifier notes:** Upgraded to B with verdict confirm: the peer-reviewed paper's public benchmark repo (skani-test) holds scripts and /bin/time outputs showing skani 21x-54x faster than FastANI 1.33 at 50 threads, but no CPU model. Shortcomings: an algorithmic win, not a language one (different method from FastANI); slower than Mash for querying; paper-era binary; CPU model absent. baseline_in_list corrected to false, since FastANI and Mash are not in the verified lists.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-15 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/bluenote-1577/skani>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/README.md>
  - <https://github.com/bluenote-1577/skani/commits/main>
  - <https://github.com/bluenote-1577/skani/tree/main/test_results_versions>
  - <https://github.com/bluenote-1577?tab=repositories>
  - <https://github.com/bluenote-1577/skani-test>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/README.md>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/time_results.sh>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/time_2328_results.sh>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/env.yml>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_2328_triangle.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_2328_triangle.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_2328_triangle.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_D3.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_D3_query.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_D3_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_D3_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_D3_dist.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_refseq.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_refseq_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_refseq_query.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_refseq_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_refseq_dist.time>
- **Sources the enricher read:**
  - <https://github.com/bluenote-1577/skani>
  - <https://github.com/bluenote-1577/skani/commits/main>
  - <https://github.com/bluenote-1577/skani/issues?q=is%3Aissue>
  - <https://github.com/bluenote-1577/skani/issues/57>
  - <https://github.com/bluenote-1577/skani/pull/58>
  - <https://github.com/bluenote-1577/skani/tree/main/src>
  - <https://github.com/bluenote-1577/skani/tree/main/test_results_versions>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/README.md>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/src/params.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/src/cmd_line.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/src/avx2_seeding.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/src/chain.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/src/screen.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/src/radix_sort.rs>
  - <https://raw.githubusercontent.com/bluenote-1577/skani/HEAD/src/seeding.rs>
  - <https://crates.io/api/v1/crates/skani>
  - <https://pypi.org/pypi/pyskani/json>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/README.md>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/time_results.sh>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/time_2328_results.sh>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/env.yml>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_2328_triangle.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_2328_triangle.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_2328_triangle.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/sourmash_2328_triangle.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/sourmash_2328_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/anim_2328.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_D3.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_D3_log.txt>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_D3_query.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_D3_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_D3_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_D3_dist.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_refseq.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/fastani_refseq_log.txt>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_refseq_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_refseq_query.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_refseq_search.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_refseq_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_refseq_dist.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_gtdb_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/skani_gtdb_query.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_gtdb_sketch.time>
  - <https://raw.githubusercontent.com/bluenote-1577/skani-test/HEAD/times/mash_gtdb_dist.time>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/bluenote-1577/skani`) · [data/wave14/enrich/raw/github_com_bluenote_1577_skani.json](../../../data/wave14/enrich/raw/github_com_bluenote_1577_skani.json) (enrichment confidence 0.78)

</details>
