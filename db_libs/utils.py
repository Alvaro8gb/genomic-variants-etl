import re
from datetime import datetime


def none_for_unique(value): 
    return -1 if value is None else value

def clean_row_values(row_values:list[str]):
    """Replace empty strings or '-' with None."""
    null_values = {"", "-", "na", "n/a"}
    return [None if (v is None or str(v).strip().lower() in null_values) else v for v in row_values]


def is_header_line(line:str, required_columns=["VariationID", "ClinicalSignificance"]):
    """
    Detect if a line is the header by checking for required column names
    """
    # Remove leading '#' and whitespace, then split by tab
    columns = line.lstrip("#").strip().split("\t")
    return all(col in columns for col in required_columns)


def parse_header(line:str):
    """Parse the header line and return a mapping of column names to indices and VCF coordinate info."""
    line = line.lstrip("#").rstrip("\n")
    column_names = re.split(r"\t", line)
    header_mapping = {name: idx for idx, name in enumerate(column_names)}

    print("Header mapping loaded", header_mapping)

    return header_mapping

def text2date(date: str, format="%b %d, %Y"):
    if not date:
        return None
    return datetime.strptime(date.strip(), format).strftime("%Y-%m-%d")

