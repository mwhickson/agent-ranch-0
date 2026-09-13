# Agent-Ranch-0 (AR0)

A locally-based agentic workflow system based around human-guided task completion.

## Warning

This project is interesting, but still very much at "toy" level.

I suspect it could provide the basis for something more impressive, both with respect to code generation -- AND non-code related tasks.

Consider yourself warned.

> WARN: Python seems reasonably reliable.
> The stress test with Go indicates a number of issues related to repeated syntax errors, flaky tests, and issues testing I/O for game playability.
> I strongly recommend Python for any experimentation at this point.

## Usage

1. Create a project.
```bash
./init.sh projects/myawesomeproject
```
2. Edit specification (`projects/myawesomeproject/PROJECT_SPEC.md`).
3. Edit prompts (`project/prompts/builder_system.txt`, `project/prompts/planner_system.txt`, `project/prompts/tester_system.txt`).
4. For a Go project:
```bash
cd projects/myawesomeproject
go mod init myawesomeproject
cd ../..
```
5. Run the pipeline.
```bash
python3 run.py projects/myawesomeproject
```

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Tools

- [Koboldcpp](https://github.com/LostRuins/koboldcpp)
- Gemma 4 (Unsloth QAT models)
    - [gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF) **PREFERRED**
    - [gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF)
