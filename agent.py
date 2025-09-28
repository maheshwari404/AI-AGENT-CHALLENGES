# agent.py
import subprocess
import sys
from pathlib import Path
import json
import os
from typing import Optional
import click

TEMPLATE = '''
# auto-generated parser for {target}
from typing import Any
import pandas as pd
import pdfplumber
from pathlib import Path

def parse(pdf_path: str) -> pd.DataFrame:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"{{pdf_path}} not found")
    rows = None
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table and len(table) >= 2:
                rows = table
                break
    if not rows:
        return pd.DataFrame()
    header = [h.strip() if h else "" for h in rows[0]]
    data = [[cell.strip() if cell else "" for cell in r] for r in rows[1:]]
    df = pd.DataFrame(data, columns=header)
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, df.columns.str.len() > 0]
    return df
'''

def run_pytest_for_target(target: str) -> int:
    test_file = f"tests/test_{target}.py"
    if not Path(test_file).exists():
        print(f"No test file {test_file} found.")
        return 1
    # run pytest, return exit code
    res = subprocess.run([sys.executable, "-m", "pytest", "-q", test_file], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("Pytest failed. stdout/stderr:")
        print(res.stderr)
    return res.returncode

def write_parser_from_template(target: str):
    out_dir = Path("custom_parsers")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{target}_parser.py"
    code = TEMPLATE.format(target=target)
    out_file.write_text(code, encoding="utf-8")
    print(f"Wrote parser to {out_file}")

@click.command()
@click.option("--target", required=True, help="target bank (e.g., icici)")
@click.option("--attempts", default=3, help="max self-fix attempts")
def main(target: str, attempts: int):
    """
    Simple agent: write a parser file from template, run tests, if failing optionally try LLM fixes.
    """
    # ensure tests/test_<target>.py and data/<target> exist
    data_dir = Path("data") / target
    if not data_dir.exists():
        print(f"Data for {target} not found at {data_dir} — ensure sample PDF and CSV are present.")
        sys.exit(2)

    for i in range(1, attempts + 1):
        print(f"=== Attempt {i} / {attempts} ===")
        write_parser_from_template(target)
        rc = run_pytest_for_target(target)
        if rc == 0:
            print("All tests passed! Agent succeeded.")
            sys.exit(0)
        else:
            print("Test failed.")
            # If an LLM key exists, you can collect the pytest output and ask LLM for a fix here.
            if os.getenv("OPENAI_API_KEY"):
                print("OPENAI_API_KEY detected — you can extend this agent to call the LLM to propose code fixes.")
                # placeholder: capture logs & call LLM to patch code (not implemented here)
                # implement LLM call for automatic code edits if you have API access.
                # For now, the agent will rewrite the template (possible area for improvement).
            else:
                print("No OPENAI_API_KEY; agent will try template tweaks (first try: nothing to change).")
    print("Agent failed after attempts.")
    sys.exit(1)

if __name__ == "__main__":
    main()
