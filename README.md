# Agent-Ranch-0 (AR0)

A locally-based agentic workflow system based around human-guided task completion.

## Usage

1. Create a project.
```bash
./init.sh projects/myawesomeproject
```
2. Edit specification (`projects/myawesomeproject/PROJECT_SPEC.md`).
3. Edit prompts (`project/prompts/builder_system.txt`, `project/prompts/planner_system.txt`, `project/prompts/tester_system.txt`).
4. Run the pipeline.
```bash
python3 run.py projects/myawesomeproject
```

> NOTE: Until I get this fleshed out, the steps above are mostly aspirational.

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Tools

- [Koboldcpp](https://github.com/LostRuins/koboldcpp)
- Gemma 4 (Unsloth QAT models)
    - [gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF)
    - [gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF)
