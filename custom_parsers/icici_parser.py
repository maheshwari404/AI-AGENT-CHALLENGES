# custom_parsers/icici_parser.py
from typing import Any
import pandas as pd
import pdfplumber
from pathlib import Path

def parse(pdf_path: str) -> pd.DataFrame:
    """
    Basic parser: open pdf with pdfplumber, find the first table-like extraction
    and return it as a pandas.DataFrame formatted to the expected schema.
    If no table found, returns empty DataFrame.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"{pdf_path} not found")

    rows = None
    with pdfplumber.open(str(pdf_path)) as pdf:
        # iterate pages, try extract_table (works when pdfplumber detects table grid)
        for page in pdf.pages:
            table = page.extract_table()
            if table and len(table) >= 2:
                rows = table
                break
        # fallback: try extract_tables (multiple)
        if rows is None:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for t in tables:
                        if t and len(t) >= 2:
                            rows = t
                            break
                    if rows:
                        break

    if not rows:
        # no table found → try text fallback (very naive)
        return pd.DataFrame()

    # rows: list of lists; assume first row is header
    header = [h.strip() if h else "" for h in rows[0]]
    data = [[cell.strip() if cell else "" for cell in r] for r in rows[1:]]
    df = pd.DataFrame(data, columns=header)
    # optional: drop empty columns & strip column names
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, df.columns.str.len() > 0]
    return df
