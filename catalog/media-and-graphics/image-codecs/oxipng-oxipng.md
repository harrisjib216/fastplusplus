# oxipng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Multithreaded Rust lossless PNG/APNG optimizer; 2.2x (default) to 5x (-o4) faster than OptiPNG 0.7.7 wall-clock on one test image.

| | |
|---|---|
| **Beats** | OptiPNG |
| **Claimed result** | README benchmark (tags v9.0.0 through v10.0.0): Oxipng 9.0.0 versus OptiPNG 0.7.7 on one test image, hyperfine wall clock, Intel Core i7-12700: default level 59.6 ms versus 132.4 ms ('2.22 +/- 0.29 times faster'); -o4 88.7 ms versus 444.9 ms ('5.01 +/- 0.25 times faster'). CPU time is closer at -o4: user 270.3 ms versus 444.8 ms, about 1.65x (derived from page data). Older run in the same README (oxipng 5.0.0, AMD Ryzen 7 4800H, rustc 1.55.0-nightly): 1.97x at default and 5.16x at -o4. Independent op111.net blog, search snippet only: d3js.org.png default oxipng 0.764 s for 29.14% reduction versus optipng 2.638 s for 25.42% (about 3.5x, derived from snippet data); powertoys.png 0.266 s for 17.62% versus 0.960 s for 5.85% (about 3.6x, derived from snippet data). |
| **Workload** | hyperfine wall-clock time to optimize one repository test PNG (tests/files/rgb_16_should_be_grayscale_8.png) without writing output (oxipng -P versus optipng -simulate) at the default level and at -o4; the independent op111.net blog adds web images (d3js.org.png, powertoys.png) at default and maximum settings. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-12700 (8 performance cores, 4 efficiency cores, 20 threads), DDR5-5200 dual channel, Linux 6.5.0-2-amd64 (README run); op111 blog hardware unknown (page blocked). |
| **Compiler and flags** | Oxipng: rustc 1.74.0-nightly (7b4d9e155 2023-09-28), cargo release profile from Cargo.toml at commit c16519b (lto = "thin", strip = "symbols", default opt-level 3), default features including parallel (rayon). OptiPNG 0.7.7 as packaged by Debian unstable (distribution build flags). |
| **Adoption** | 4.3k stars |
| **Last commit** | 2026-09-02 |
| **Links** | [repository](https://github.com/oxipng/oxipng) · [benchmark](https://raw.githubusercontent.com/oxipng/oxipng/v10.0.0/README.md) |

## Verdict

The v9.0.0 to v10.0.0 README timed a pre-release oxipng 9.0.0 (commit c16519b, rustc 1.74.0-nightly 2023-09-28, release profile lto = "thin", default features with rayon) against Debian's OptiPNG 0.7.7 with hyperfine on an Intel Core i7-12700 (20 threads): 59.6 ms versus 132.4 ms at the default level (2.22x) and 88.7 ms versus 444.9 ms at -o4 (5.01x), both in dry-run mode. The input is one 500x400 16-bit RGB PNG (116 KB) that both tools can losslessly reduce to 8-bit grayscale; output sizes were not reported, and at that commit -o4 meant four filter strategies (None, Bigrams, BigEnt, Brute) fully compressed with libdeflate level 12 in parallel, a different trial set from OptiPNG's -o 4, so the 5x is time-at-named-preset, not the same work done faster.

## Use it when

- Build, CI or pre-commit steps that losslessly shrink PNG assets; the project ships a pre-commit hook and a ghcr.io Docker image for linux/amd64 and linux/arm64.
- Interactive or few-file runs on a multi-core machine where wall-clock time matters: one image's trials spread across cores, giving 2.22x at the default level and 5.01x at -o4 against single-threaded OptiPNG on a 20-thread i7-12700 in the README run.
- Replacing OptiPNG in image pipelines where the default level should also compress better: the op111.net comparison (search snippet only) reports 29.14% versus 25.42% size reduction on d3js.org.png at about 3.5x the speed.
- Rust programs that produce or post-process PNGs in memory: optimize_from_memory() or RawImage plus Options::from_preset(level), with --max-raw-size and timeout controls available.
- Web or WASM image tools: Squoosh and jSquash use it per the README, and a freestanding feature forwards to libdeflater for targets without a full libc.

## Skip it when

- Batch jobs that already run one OptiPNG process per core: then the parallel trials add little and the gain falls toward the CPU-time ratio, which was only 1.71x (default) and 1.65x (-o4) in the README run (derived from page data).
- Maximum compression at any cost: oxipng is not a brute-force optimizer, so a higher level can occasionally give a larger file and --zopfli is not guaranteed to help; op111 (snippet only) shows --opt max --zopfli taking 28.9 s for 30.25% versus 0.764 s for 29.14% at the default on the same image. ECT or other zopfli-based tools trade more time for bytes.
- Animated PNGs: APNG support is limited to alpha optimization, refiltering and recompression with all reductions disabled; the README recommends running apngopt first, and issue 'Feature-complete APNG optimization' is still open.
- C or C++ applications that want an in-process library: there is only a Rust API and no C ABI, so use the CLI as a subprocess or write your own FFI shim.
- Services processing untrusted or very large images under a hard deadline: --timeout is checked only between trials and does not stop a running compression, so set --max-raw-size; the libdeflater crate it depends on is looking for a new maintainer (issue #702, open, no decision).

## How it is fast

Three things, not one faster algorithm: (1) trials run in parallel on rayon, each reduction candidate and filter strategy in its own task, with a shared atomic best size (AtomicMin) passed to the deflater as an output cap so losing trials abort early; (2) compression uses libdeflate (levels 10-12 are its near-optimal parser) instead of zlib; (3) in the default fast-evaluation mode (levels 0-4) reductions and filter strategies are ranked with a cheap libdeflate level (5, 7 or 8 per optimize_raw) and only the winner is compressed once at the main level (11 at -o2, 12 at -o4). Filter strategies include the five PNG filters plus heuristic MinSum, Entropy, Bigrams, BigEnt and a Brute strategy that test-compresses a few lines per row choice.

## Compared with alternatives

Pick oxipng when you already have PNG files and want them smaller with identical pixels; fpng, fpnge and mtpng are fast encoders from raw pixels whose files are larger (fpnge's catalogued ratio is about 15% worse than libpng's), and libspng, image-png and zune-png are decoders. ECT (catalogued under general-lossless) squeezes harder with its zopfli-derived deflate at a much higher run time.

## Integration

| | |
|---|---|
| **Form** | crate (library) and CLI binary; also distro packages, Windows release binaries and a Docker image |
| **Dependencies** | libdeflater (Rust binding to the C libdeflate library; feature system-libdeflate links the system copy), indexmap, rgb, rustc-hash, log; optional rayon (parallel, default), zopfli (default), clap, env_logger, parse-size and glob (binary feature, default), image (sanity-checks) |
| **Minimum toolchain** | Rust 1.88.0 for 10.2.x (Cargo.toml rust-version, crates.io metadata; 1.85.1 for 10.0.0 to 10.1.1), edition 2024; the README still says 1.85.1 |
| **Platforms** | any target Rust and libdeflate support; Docker images for linux/amd64 and linux/arm64; WASM used downstream (Squoosh, jSquash) but WASM tests in CI are an open issue |
| **Thread safety** | optimize(), optimize_from_memory() and RawImage::create_optimized_png() are free functions taking an owned or borrowed Options with no shared mutable state beyond rayon's global pool; calling them from inside an existing rayon pool deadlocked before 9.0.0. Build without the parallel feature for single-threaded use, or cap threads with -t in the CLI. |
| **Drop-in for the baseline** | partial: produces standard PNG files like OptiPNG and keeps similar -o levels and strip options, but the CLI is different (README: not a drop-in replacement) and its levels run different trial sets |

## Gotchas

- Version 10.0.0 renamed flags: -P/--pretend became -d/--dry-run, -Z became -z and --interlace takes on/off, so the README benchmark commands (oxipng -P) do not run on 10.x as written; the library API also changed (optimize() now returns original and optimized sizes, Deflaters became Deflater).
- --alpha alters the color of fully transparent pixels (the README calls it technically lossy), and --scale16 forcibly scales 16-bit to 8-bit; both are off by default, but pipeline scripts copied from the web often include --alpha.
- Default output removes interlacing (since 9.0.0); use -i keep to retain it, and interlacing is only applied when smaller unless --force is given.
- The README's library snippet (version "10.0", features ["parallel", "zopfli", "filetime"], default-features = false) no longer builds: the filetime feature was dropped in 10.1.0 (crates.io feature lists for 10.1.0 to 10.2.1) without a changelog entry, and "10.0" resolves to 10.2.1; list only parallel and zopfli.

## Known shortcomings

- Rust (language-filter mismatch). Upgraded to A on the tagged v9.0.0 to v10.0.0 README hyperfine runs vs OptiPNG 0.7.7 (2.22x default, 5.01x at -o4; i7-12700, rustc 1.74.0-nightly, Cargo.toml lto thin at c16519b). The gain is mostly threads (user CPU about 1.65x at -o4), one test image, and a different trial set from OptiPNG's; the op111.net post is snippet-only.
- The measured file is one 500x400 16-bit RGB image that losslessly reduces to 8-bit grey, so both tools reduce it; no output sizes are given, and at c16519b -o4 runs 4 filters at libdeflate level 12 in parallel, different trials from OptiPNG's, so the CPU-time gain is only 1.71x/1.65x. README library snippet asks for the filetime feature removed in 10.1.0 (so '10.0' resolves to 10.2.1 and fails to build); the README MSRV says 1.85.1 but 10.2.x needs 1.88.0; benchmark commands use -P, renamed -d in 10.0.0; the libdeflater crate seeks a new maintainer (#702).

## Caveats and trade-offs

Rust, not C++ (the search's C++ language filter does not match); OptiPNG is not one of the category's listed baselines (libjpeg-turbo, libpng, libwebp, libavif). The README benchmark is first-party, uses a single small test image, does not report output sizes, and was removed from the README after v10.0.0 in favor of a link to the op111.net blog. Most of the wall-clock gain comes from multithreading on a 20-thread CPU against single-threaded OptiPNG (user CPU time at -o4 is only about 1.65x lower); oxipng also uses libdeflate and its own trial heuristics, so -o4 does not run the same trial set as optipng -o 4 (different work, not an identical algorithm made faster). The README names Oxipng 9.0.0 but Cargo.toml at the cited commit still says 8.0.0. The op111.net numbers are snippet only (page blocked); per the snippet oxipng also compresses better at default settings.

Rust command-line tool and library (not a C or C++ API); multithreaded by design, the README says it began as a Rust rewrite of OptiPNG to add multithreading. Optimizes existing PNG/APNG files, it is not a general encoder. Higher levels and --zopfli are slow.

## Maintenance

Actively developed (v10.2.1, last commit 2026-09-02, 4.3k stars), MIT and widely packaged; usable from C++ projects as a CLI build step rather than a linked library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the repo's own README (tags v9.0.0 through v10.0.0; removed at HEAD in favor of the op111 link) carries a hyperfine benchmark against OptiPNG 0.7.7 with the exact commands, a public test image (tests/files/rgb_16_should_be_grayscale_8.png), commit c16519b, rustc 1.74.0-nightly (7b4d9e155 2023-09-28), the release profile in Cargo.toml at that commit (lto = "thin") and an Intel Core i7-12700, so code, compiler, flags and CPU model are all public. The independent op111.net blog the record cited is blocked and was seen only as a search snippet.
- **Verifier notes:** Found a first-party reproducible benchmark in the repo's tagged README (v9.0.0 to v10.0.0), so the tier rises from C to A; benchmark_url now points at the v10.0.0 README. The op111 numbers in the record match a fresh search snippet but could not be opened, hence numbers_found_on_page null. Metadata confirmed: MIT, 4.3k stars, last commit 2026-09-02 (v10.2.1), not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/oxipng/oxipng>
  - <https://github.com/oxipng/oxipng/commits>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/README.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/v10.0.0/README.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/v9.1.5/README.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/v9.1.2/README.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/v8.0.0/README.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/c16519b38b0519988db625913be919d4f0e42f5d/Cargo.toml>
  - <https://raw.githubusercontent.com/oxipng/oxipng/c16519b38b0519988db625913be919d4f0e42f5d/tests/files/rgb_16_should_be_grayscale_8.png>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/Cargo.toml>
  - <https://github.com/oxipng/oxipng/issues/730>
- **Sources the enricher read:**
  - <https://github.com/oxipng/oxipng>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/README.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/v10.0.0/README.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/oxipng/oxipng/v10.0.0/Cargo.toml>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/MANUAL.txt>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/src/evaluate.rs>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/src/options.rs>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/src/deflate/mod.rs>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/src/rayon.rs>
  - <https://raw.githubusercontent.com/oxipng/oxipng/HEAD/src/atomicmin.rs>
  - <https://raw.githubusercontent.com/oxipng/oxipng/c16519b38b0519988db625913be919d4f0e42f5d/Cargo.toml>
  - <https://raw.githubusercontent.com/oxipng/oxipng/c16519b38b0519988db625913be919d4f0e42f5d/src/lib.rs>
  - <https://raw.githubusercontent.com/oxipng/oxipng/c16519b38b0519988db625913be919d4f0e42f5d/tests/files/rgb_16_should_be_grayscale_8.png>
  - <https://github.com/oxipng/oxipng/tree/master/src>
  - <https://github.com/oxipng/oxipng/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/oxipng/oxipng/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/oxipng/oxipng/issues/757>
  - <https://github.com/oxipng/oxipng/issues/730>
  - <https://github.com/oxipng/oxipng/issues/81>
  - <https://github.com/oxipng/oxipng/issues/702>
  - <https://github.com/oxipng/oxipng/releases>
  - WebSearch: "oxipng and friends" op111 (result snippets for op111.net; page blocked)
  - <https://crates.io/api/v1/crates/oxipng/versions>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/oxipng/oxipng`) · [data/wave10/enrich/raw/github_com_oxipng_oxipng.json](../../../data/wave10/enrich/raw/github_com_oxipng_oxipng.json) (enrichment confidence 0.8)

</details>
