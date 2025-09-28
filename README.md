# Agent-as-Coder — forked from apurv-korefi/ai-agent-challenge

## 5-step run instructions
1. Fork this repo on GitHub and clone your fork.
2. Create & activate a Python venv: `python -m venv .venv` then `source .venv/bin/activate` (or `.venv\Scripts\Activate.ps1` on Windows).
3. Install dependencies: `pip install -r requirements.txt`.
4. For fast pass: run `pytest -q` to run tests for the provided sample (ensure `data/icici/` has `icici_sample.pdf` and `icici_expected.csv`).
5. To run the agent (auto-generate parser): `python agent.py --target icici`. If using an LLM, set `OPENAI_API_KEY` in env first.

## Agent diagram (one paragraph)
The agent runs a short loop: it *plans* (reads sample CSV + PDF to infer schema), *generates code* (writes `custom_parsers/<target>_parser.py` using either a deterministic template or an LLM), *executes tests* (runs the bank-specific pytest that compares `parse(...)` output to expected CSV), and if tests fail it *observes* error output and iterates up to three self-fix cycles (optionally calling an LLM to propose code patches). This loop enables autonomous generation and validation of parsers for new banks.

