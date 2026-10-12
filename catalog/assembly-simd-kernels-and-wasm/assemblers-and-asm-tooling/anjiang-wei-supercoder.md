# SuperCoder

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Python` · `Apache-2.0` · 🟢 active

> RL-fine-tuned 7B LLM that rewrites gcc-compiled x86-64 assembly, claiming 1.46x over gcc -O3 on CodeNet programs.

| | |
|---|---|
| **Beats** | gcc -O3 compiled assembly (output quality) |
| **Claimed result** | Per WebSearch result text of arXiv 2505.11480 only (paper not opened): the RL-fine-tuned Qwen2.5-Coder-7B-Instruct model reaches a 95.0% test pass rate and a 1.46x average speedup over gcc -O3; the strongest baseline LLM (Claude-opus-4) reaches 51.5% pass rate and 1.43x average speedup. |
| **Workload** | Runtime speedup of LLM-rewritten x86 assembly versus the gcc -O3 assembly on a benchmark of 8,072 real-world programs averaging 130 lines (CodeNet-derived), with test-based correctness checks. |
| **Metric** | other |
| **Compiler and flags** | Per the paper (snippet only): baseline assembly from gcc -O3. Released scripts: src/create_data/convert_to_hf_raw.py emits gcc -O0 -S (stored as 'unoptimized_assembly', the prompt input and the timing baseline) and gcc -O3 -S (stored as the reference answer); all assembly is linked with plain 'gcc file.s -o bin -lm'; gcc version not stated. Timing: hyperfine --warmup 3 --runs 10, mean whole-process wall time per test input, up to 10 inputs per program. |
| **Adoption** | 2 stars, 0 forks; model weights published as LLM4Code/Superoptimizer_Qwen7B on HuggingFace |
| **Last commit** | 2025-10-23 |
| **Links** | [repository](https://github.com/Anjiang-Wei/SuperCoder) · [benchmark](https://arxiv.org/abs/2505.11480) |

## Verdict

Per search snippets of arXiv 2505.11480 (paper not opened): on a CodeNet-derived benchmark of 8,072 programs the RL-tuned Qwen2.5-Coder-7B reaches 95.0% test pass rate and a 1.46x average speedup over gcc -O3 (Claude-opus-4 51.5% and 1.43x; untuned base 61.4% and 1.10x), measured as hyperfine whole-process means on up to 10 inputs per program, hardware and gcc version not stated. The repo's print_results.py computes that 'average' as a geometric mean over problems with incorrect ones at 1.0 and per-input speedups floored at 1.0, and the released scripts time against gcc -O0 output rather than -O3.

## Use it when

- Research on learned code optimization where you need a reproducible baseline model, dataset recipe and reward function for assembly-level rewriting.
- Generating candidate rewrites of small, self-contained, stdin/stdout x86-64 programs (competitive-programming size) that you will re-verify and re-benchmark yourself.
- Comparing LLMs (OpenAI, Anthropic, Gemini, Together or local Hugging Face models) on assembly optimization with the same harness via src/evaluate.py.

## Skip it when

- Production builds: correctness is checked only on at most 10 stored test inputs per program, with no formal equivalence check, so a passing rewrite can still be wrong on other inputs.
- Large codebases, libraries or anything beyond single-file programs; prompts and answers are capped at 2,000 tokens each in the training script and the dataset filter drops pairs above 4,000 tokens.
- Non-x86-64 targets or non-gcc toolchains: the harness assembles with plain 'gcc file.s -o bin -lm' on the host.
- When you need a verified result for a hot kernel: STOKE or Minotaur in this category check equivalence instead of sampling tests.

## How it is fast

The speedup comes from LLM-proposed rewrites of whole small programs (about 130 lines of assembly on average), learned by reinforcement learning with a reward of 0 for wrong, non-compiling or input-identical answers and the measured mean speedup (only when above 1.0) for correct ones (verl/verl/utils/reward_score/speedup_assembly_design2.py). This is superoptimization in the STOKE sense, but driven by a learned policy and test execution instead of a stochastic search with an equivalence checker. Training programs were selected from CodeNet submissions that showed large -O0 to -O3 gains (create_top_speedup.py --threshold 3.0).

## Compared with alternatives

Pick SuperCoder over STOKE or Minotaur only when you want an LLM to propose rewrites of whole small programs and can afford independent verification; STOKE and Minotaur prove equivalence of the code they change and report measured gains on named hardware, which SuperCoder does not.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python 3.10.12 (conda), torch 2.6.0, transformers, datasets, sglang[all]&gt;=0.4.6.post5, flash-attn, ray, vLLM and the vendored verl (pip install -e) for training, anthropic/openai/together/google-genai clients, hyperfine, gcc; Hugging Face access for the model and dataset |
| **Minimum toolchain** | Python 3.10; GPUs for inference and RL (the training script sets 4 GPUs per node); gcc version not documented |
| **Platforms** | x86-64 Linux for the generated code and harness; CUDA GPUs for model inference and training |
| **Thread safety** | not documented (the evaluation harness runs test cases in a ThreadPoolExecutor) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in src/test_benchmark.py and src/metrics.py: a generated answer identical to the input 'unoptimized_assembly' is marked 'success' for every test case without being run, so echoing the prompt counts toward the reported pass rate (at speedup 1.0); the RL reward gives such an answer 0, but the evaluation does not, so the pass-rate metric is inflated by construction.
- Speedups are biased upward: each per-input ratio is floored at 1.0 ('If generated code is slower, set speedup to 1.0'), failed, non-compiling and benchmark-failing cases are scored 1.0, and print_results.py (which emits the LaTeX table rows) clamps the final geometric mean at 1.0, so whole-process timing noise on millisecond programs can only add to the score.
- Baseline mismatch: in the released scripts the timed baseline and the prompt's input are gcc -O0 output (convert_to_hf_raw.py stores 'gcc -O0 -S' as unoptimized_assembly; gcc -O3 is only the reference answer), while the paper reports speedups over gcc -O3; the published HF dataset could not be opened to see which variant the numbers used.
- Timings are mean whole-process wall time (hyperfine --warmup 3 --runs 10, startup included) on small CodeNet programs, measured while other test cases run concurrently in the thread pool; no CPU model or gcc version is given.

## Known shortcomings

- Preprint numbers (95.0% success, 1.46x over gcc -O3; arXiv 2505.11480 unopened) are snippet-only; the harness counts slower outputs and failures as 1.0x so the average can never drop below 1.0; the released scripts (convert_to_hf_raw.py) time against gcc -O0 assembly while the paper claims -O3 (unresolved, HF dataset unreachable); no CPU or gcc version.
- Enricher: the evaluation harness (src/test_benchmark.py, src/metrics.py) marks an answer identical to the input assembly as a pass for every test case without running it, so prompt echoes inflate the 95.0% pass rate; per-input speedups are floored at 1.0 with failed and non-compiling cases scored 1.0 and print_results.py clamps the geometric mean at 1.0; the released scripts time against gcc -O0 output while the paper says -O3 (HF dataset blocked, unresolved). Retiered to D.

## Caveats and trade-offs

Headline numbers come from WebSearch snippets of arXiv 2505.11480 (paper not opened; arXiv and alphaXiv blocked); the README has no results section and states no hardware or gcc version. The released harness (src/test_benchmark.py) floors every per-input speedup at 1.0 ('If generated code is slower, set speedup to 1.0'), gives failed, non-compiling or benchmark-failing cases a speedup of 1.0 (they are averaged in as 1.0, not excluded), and treats output identical to the baseline assembly as correct at 1.0 without running it, so the reported average can never fall below 1.0 and is biased upward. In the released dataset-building scripts (src/create_data/convert_to_hf_raw.py, create_top_speedup.py) the 'unoptimized_assembly' that test_benchmark.py times against is gcc -O0 output, while the paper says the baseline is gcc -O3; the published HuggingFace dataset (LLM4Code/llm_superoptimizer_ds) could not be opened to check which variant the reported numbers used, so the repo as released does not demonstrably reproduce the -O3 comparison. Correctness is checked on at most 10 CodeNet test inputs per program, and timings are whole-process (startup included) on small competitive-programming programs, run concurrently in a thread pool. The output is a fine-tuned model (HuggingFace LLM4Code/Superoptimizer_Qwen7B, licence not checked), not a library; the repo is a 2-commit code drop. Preprint status.

Probabilistic output: correctness is test-based (95.0% pass rate, not formal equivalence), so rewrites need independent verification. Needs a GPU-capable RL setup (verl) to retrain; model weights and dataset are listed on Hugging Face in the README.

## Maintenance

Two-commit code drop from 2025-10-23 (Apache-2.0, 2 stars, no issues) accompanying a preprint; usable as research code and a model checkpoint, but the evaluation harness counts prompt echoes as passes and floors slowdowns at 1.0, so re-measure any claimed gain yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party arXiv preprint (2505.11480, not peer-reviewed as far as seen) whose headline numbers (95.0% pass, 1.46x over gcc -O3; Claude-opus-4 51.5%, 1.43x; base Qwen2.5-Coder-7B 61.4%, 1.10x) were confirmed only through WebSearch snippets because arxiv.org and alphaxiv.org are blocked; the public harness (src/test_benchmark.py, hyperfine) exists but no CPU model or gcc version is stated in the repo, and the released dataset scripts do not match the paper's -O3 baseline, so not A or B.
- **Retiered** C to D: Enricher (2026-10-12): no valid measurement behind the reported numbers. src/test_benchmark.py and src/metrics.py count an answer identical to the input assembly as a pass without running it; each per-input speedup is floored at 1.0 with failed, non-compiling and benchmark-failing cases scored 1.0 and print_results.py clamps the geometric mean at 1.0; the released scripts time against gcc -O0 output although the paper states -O3. Crippled-baseline and floored-metric precedent.
- **Verifier notes:** Repo, Apache-2.0 licence, 2 stars and last commit 2025-10-23 (2 commits, both that day) confirmed on github.com; still 'active' until 2026-10-23. Shortcomings to record: speedup floored at 1.0 per input and failures averaged in as 1.0 (record's caveat said failures were excluded; corrected), released scripts time against gcc -O0 assembly while the paper claims gcc -O3 (unresolved, HF dataset unreachable), no CPU or gcc version, preprint numbers seen only in search snippets. Not invalid evidence, so kept at C.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-09 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Anjiang-Wei/SuperCoder>
  - <https://github.com/Anjiang-Wei/SuperCoder/commits>
  - <https://github.com/Anjiang-Wei/SuperCoder/tree/master/src>
  - <https://github.com/Anjiang-Wei/SuperCoder/tree/master/src/create_data>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/evaluate.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/metrics.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/test_benchmark.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/utils.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/print_results.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/scripts/eval.sh>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/scripts/create_ds.sh>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/convert_to_hf_raw.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/create_top_speedup.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/precompile.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/filter_wrong.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/generate_io.py>
- **Sources the enricher read:**
  - <https://github.com/Anjiang-Wei/SuperCoder>
  - <https://github.com/Anjiang-Wei/SuperCoder/issues?q=is%3Aissue>
  - <https://github.com/Anjiang-Wei/SuperCoder/tree/master/src>
  - <https://github.com/Anjiang-Wei/SuperCoder/tree/master/src/inference>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/print_results.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/download_parquet.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/scripts/eval.sh>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/scripts/create_ds.sh>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/scripts/install_dependencies.sh>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/evaluate.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/metrics.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/test_benchmark.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/utils.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/inference/__init__.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/inference/all_inference.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/inference/inference_clients.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/convert_to_hf_raw.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/create_top_speedup.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/precompile.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/filter_wrong.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/src/create_data/generate_io.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/verl/examples/ppo_trainer/run_qwen2.57_superopt.sh>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/verl/verl/utils/reward_score/__init__.py>
  - <https://raw.githubusercontent.com/Anjiang-Wei/SuperCoder/HEAD/verl/verl/utils/reward_score/speedup_assembly_design2.py>
  - WebSearch snippets for arXiv 2505.11480 (arxiv.org, alphaxiv.org, papers.cool results; pages not opened)
  - https://huggingface.co/datasets/LLM4Code/llm_superoptimizer_ds (blocked: DNS failure and proxy CONNECT 403)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/anjiang-wei/supercoder`) · [data/wave13/enrich/raw/github_com_anjiang_wei_supercoder.json](../../../data/wave13/enrich/raw/github_com_anjiang_wei_supercoder.json) (enrichment confidence 0.55)

</details>
