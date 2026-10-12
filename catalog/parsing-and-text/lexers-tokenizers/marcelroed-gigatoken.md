# Gigatoken

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> SIMD/cache-optimized BPE tokenizer with a Python API, roughly 7x-1300x faster encoding than HF tokenizers.

| | |
|---|---|
| **Beats** | HuggingFace tokenizers (and OpenAI tiktoken) |
| **Claimed result** | GPT-2 on AMD EPYC 9565 dual-socket (144 cores): 24.53 GB/s vs HF tokenizers' 24.8 MB/s (989x) and tiktoken's 36.0 MB/s (681x); across the 23 tokenizer rows and three CPUs, speedup vs HF ranges from 7.3x (Gemma 1, EPYC) to 1,299x (OLMo 2/3, Apple M4 Max) and vs tiktoken from 50x to 681x; SentencePiece-based tokenizers (Gemma, Mistral, CodeLlama, TinyLlama/Phi-3) show the smallest gains, \~7-22x |
| **Workload** | Encoding the openwebtext corpus (owt_train.txt, 11.9GB) with BPE tokenizers for \~23 model families (GPT-2, Llama 3/3.1/3.2/3.3/4, Qwen 2/2.5/3/3.5/3.6, DeepSeek V3/R1/V4, GLM 4/5, Phi-4, Gemma, Mistral, etc.); Gigatoken tokenizes the whole file unsplit while HF tokenizers gets the first 100MB and tiktoken the first 1GB, both pre-split on the document separator |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9565 72-core x2 sockets (144 cores); Apple M4 Max (16 cores); AMD Ryzen 7 9800X3D (16 cores) |
| **Compiler and flags** | Rust nightly (rust-toolchain.toml channel = "nightly", version not pinned); Cargo release profile with lto = "fat" |
| **Adoption** | 4.1k stars |
| **Last commit** | 2026-08-06 |
| **Links** | [repository](https://github.com/marcelroed/gigatoken) · [benchmark](https://github.com/marcelroed/gigatoken#benchmarks) |

## Verdict

First-party benchmark (benchmarks/compare/measure.py + sweep.py, raw data in benchmarks/results.json) built with Rust nightly and a fat-LTO release profile: on a dual-socket AMD EPYC 9565 (144 cores) encoding the 11.9GB openwebtext corpus, Gigatoken reached 24.53 GB/s on GPT-2 BPE vs HF tokenizers' 24.8 MB/s (989x) and tiktoken's 36.0 MB/s (681x). Across 23 tokenizer families on three CPUs (EPYC 9565, Apple M4 Max, Ryzen 7 9800X3D), the margin vs HF ranged from 7.3x (Gemma 1, EPYC) to 1,299x (OLMo 2/3, M4 Max); Gigatoken tokenized the whole file unsplit while HF got the first 100MB and tiktoken the first 1GB, both pre-split on the document separator.

## Use it when

- Encoding large text corpora (GB-to-TB scale) with a supported BPE vocab (GPT-2/Llama/Qwen/DeepSeek/GLM/Phi-4 family, etc.) for LLM pretraining or bulk preprocessing
- Throughput-bound batch tokenization jobs where you control the pipeline and can adopt the native TextFileSource API instead of the HF/tiktoken object interface
- x86-64 or aarch64 Linux/macOS hosts, especially many-core servers (the EPYC/M4 Max/Ryzen numbers show gains scale with core count)
- Workloads dominated by common BPE (not SentencePiece) pretokenization, where the biggest speedups (hundreds to \~1000x vs HF) apply
- Cases where you can pin a Rust nightly toolchain to build the PyO3 wheel, or install a prebuilt wheel

## Skip it when

- You need byte-identical drop-in behavior with zero code change and top speed simultaneously — compatibility mode preserves output but is 'noticeably slower' than native mode per the README
- Your tokenizer is SentencePiece-based (Gemma, Mistral, CodeLlama, TinyLlama/Phi-3) — README states these paths 'are not well optimized' and gains drop to \~7-22x vs HF instead of hundreds of x
- WordPiece tokenizers — not supported yet
- CJK-heavy corpora — README says these are 'much slower to tokenize' due to caching challenges
- Windows deployment, or environments that can't tolerate an unpinned Rust nightly compiler dependency — README says Windows 'has not been tested much', recommends WSL

## How it is fast

Pretokenization (normally outsourced to a regex engine) is replaced with hand-written, per-tokenizer-family SIMD pretokenizers (src/pretokenize/fast/{cl100k,o200k,deepseek_v3,kimi,nemotron,olmo3,qwen2,qwen3_5,r50k}.rs) that avoid branching and generic regex overhead. A pretoken-cache hierarchy (src/bpe/pretoken_cache.rs) memoizes previously-seen word-to-token mappings using a concurrent hashmap (dashmap) so repeated words skip re-encoding. Work is parallelized across cores with rayon, input is read via memory-mapped files (memmap2) to avoid copies, and the Python/Rust boundary is minimized to cut interpreter overhead.

## Compared with alternatives

The catalogued siblings (Accelerated-Zig-Parser, StreamTok, CrossDB, lexer-exp, logos, LRSTAR, simd-lexing, Ragel) are all programming-language/DFA lexers beating flex-family tools, not LLM BPE tokenizers — none overlap with Gigatoken's workload. Pick Gigatoken specifically when the task is encoding natural-language text for an LLM with a supported BPE vocabulary at GB/s+ scale; it has no direct competitor among the siblings.

## Integration

| | |
|---|---|
| **Form** | crate (Rust, cdylib+lib) packaged as a PyO3 Python extension; pip install gigatoken |
| **Dependencies** | Rust: dashmap, rayon, pyo3 (abi3-py310), memmap2, icu, sonic-rs, memchr, aho-corasick, serde, flate2, zstd, spm_precompiled, simdutf, winnow, parquet/arrow-array/arrow-schema, ureq, libc (Linux only). Python: numpy&gt;=1.24.4, awkward&gt;=2.6.3, typer&gt;=0.12 |
| **Minimum toolchain** | Rust nightly (rust-toolchain.toml channel = "nightly", version unpinned), edition 2024; Python &gt;=3.10 (built against PyO3 abi3-py310) |
| **Platforms** | x86-64 and aarch64 (SIMD variants referenced for AVX512/AVX2/NEON in profiling assets); Windows 'not been tested much', README recommends WSL instead |
| **Thread safety** | not documented as an explicit guarantee; internal parallelism uses rayon for work distribution and dashmap (concurrent hashmap) for the shared pretoken cache |
| **Drop-in for the baseline** | partial — explain: a compatibility-mode wrapper (`gt.Tokenizer(hf_tokenizer).as_hf()` / `.as_tiktoken()`) matches HF/tiktoken output and call sites, but is slower than Gigatoken's own native `Tokenizer`/`TextFileSource` API, which requires adopting a different interface for full speed |

## Gotchas

- Compatibility mode (byte-identical to HF/tiktoken) is 'noticeably' slower than native mode — don't expect the headline \~1000x number when using it as a drop-in
- SentencePiece-family tokenizers (Gemma, Mistral, CodeLlama, TinyLlama/Phi-3) get far smaller speedups (\~7-22x vs HF) than the BPE families (up to \~1300x)
- README warns the first run on macOS triggers a security scan that slows the Rust binary, and recommends running benchmarks twice to get a representative timing
- WordPiece tokenizers and file sinks (in the native API) are not yet implemented

## Caveats and trade-offs

The benchmark gives Gigatoken the harder task (the whole 11.9GB file unsplit, finding its own split boundaries), while HF gets the first 100MB and tiktoken the first 1GB, both pre-split; the README argues this is fair but the setup is asymmetric; exact rustc nightly version not stated; first-party benchmark (benchmarks/compare/\*, results.json), not an independent suite; README says CJK-heavy data is much slower and SentencePiece paths are less optimized

Its own native API is fastest; a compatibility-mode wrapper that guarantees byte-identical output to HuggingFace/tiktoken is noticeably slower than native mode; SentencePiece-family tokenizers are not well optimized yet; ships as a Python package (PyO3) backed by a Rust core

## Maintenance

Actively maintained (last commit 2026-08-06 on main), MIT-licensed, 4.1k stars; small enough to vendor as a source drop but the build depends on an unpinned Rust nightly toolchain, so pin one yourself if reproducibility matters.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks tables show gigatoken vs HF tokenizers and tiktoken on owt_train.txt for three named CPUs, and the harness is public (benchmarks/compare/measure.py, sweep.py; raw data in benchmarks/results.json; `gigatoken bench` CLI). The Cargo.toml release profile (fat LTO) is given, but the compiler is an unpinned Rust nightly with no version stated, so this is not A; these are first-party numbers, so C.
- **Verifier notes:** All quoted numbers match the README tables. The last commit on the default branch (main) is 2026-08-06; the 2026-09-02 date is pushed_at from the side branch simplify-refactor. 4,111 stars, MIT, still active. I did not check the MarkTechPost amplification claim, so I left it out of the corrected caveats.
- **Fields the verifier corrected:** `last_commit`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/marcelroed/gigatoken#benchmarks>
  - <https://github.com/marcelroed/gigatoken>
  - <https://github.com/marcelroed/gigatoken/blob/main/rust-toolchain.toml>
  - <https://github.com/marcelroed/gigatoken/blob/main/.cargo/config.toml>
  - <https://github.com/marcelroed/gigatoken/blob/main/Cargo.toml>
  - <https://github.com/marcelroed/gigatoken/tree/main/benchmarks>
  - <https://github.com/marcelroed/gigatoken/blob/main/benchmarks/results.json>
- **Sources the enricher read:**
  - <https://github.com/marcelroed/gigatoken>
  - <https://github.com/marcelroed/gigatoken#benchmarks>
  - <https://github.com/marcelroed/gigatoken/blob/main/Cargo.toml>
  - <https://github.com/marcelroed/gigatoken/blob/main/pyproject.toml>
  - <https://github.com/marcelroed/gigatoken/blob/main/rust-toolchain.toml>
  - <https://github.com/marcelroed/gigatoken/blob/main/.cargo/config.toml>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/marcelroed/gigatoken`) · [data/wave3/enrich/raw/github_com_marcelroed_gigatoken.json](../../../data/wave3/enrich/raw/github_com_marcelroed_gigatoken.json) (enrichment confidence 0.65)

</details>
