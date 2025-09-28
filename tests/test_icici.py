# tests/test_icici.py
import pandas as pd
from custom_parsers.icici_parser import parse
from pathlib import Path

def test_icici_matches_expected():
    data_dir = Path("data/icici")
    expected_csv = data_dir / "icici_expected.csv"
    pdf_file = data_dir / "icici_sample.pdf"
    expected = pd.read_csv(expected_csv)
    out = parse(str(pdf_file))
    # use DataFrame.equals as required by the challenge
    assert out.equals(expected), f"Parsed DataFrame does not equal expected. Output shape: {out.shape}, expected: {expected.shape}"
