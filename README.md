# EPFO EEC-2026 Return File Generator

A Streamlit web application for generating EPFO EEC-2026 return files from employee wage data.

## Features

- **Data Input**: Upload Excel/CSV or use manual grid entry
- **Auto-calculation**: Computes all 11 EEC fields per EPFO rules
- **Two File Models**: Month-wise blocks or Employee-wise blocks
- **Live Review**: Editable grid with KPI summary cards
- **Preview & Download**: Text file preview + EEC text + Excel audit log

## Quick Start

```bash
cd epfo-eec-generator
pip install streamlit pandas openpyxl numpy
streamlit run app.py
```

Open http://localhost:8501

## Project Structure

```
epfo-eec-generator/
├── app.py          # Streamlit UI
├── eec_utils.py    # Pure business logic (no Streamlit deps)
├── README.md       # This file
```

## EPFO Calculation Rules (11 Fields)

| # | Field | Formula |
|---|-------|---------|
| 1 | UAN | From input (padded to 12 digits) |
| 2 | Member Name | From input (UPPERCASE) |
| 3 | Wage Month (YYYYMM) | Generated per period |
| 4 | Gross Wages | From input |
| 5 | EPF Wages | From input (default = Gross) |
| 6 | EPS Wages | min(EPF Wages, EPS_CAP) default ₹15,000 |
| 7 | EDLI Wages | min(EPF Wages, EDLI_CAP) default ₹15,000 |
| 8 | Employee PF Contribution | round(EPF Wages × PF_RATE) default 12% |
| 9 | Employer EPS Contribution | round(EPS Wages × EPS_RATE) default 8.33% |
| 10 | Employer PF Contribution | Employee PF − Employer EPS |
| 11 | NCP Days | From input (default 0) |

## Input Format (Excel/CSV)

| UAN | Member Name | Gross Wages | EPF Wages | Start Month (YYYYMM) | End Month (YYYYMM) | NCP Days |
|-----|-------------|-------------|-----------|----------------------|--------------------|----------|
| 100257274743 | NITESH | 15000 | 15000 | 202501 | 202603 | 0 |
| 100427601130 | RAMESH | 20000 | 15000 | | | 0 |

Start/End Month are optional — falls back to global sidebar selection.

## File Structure Models

- **Model 1 (Month-wise)**: All employees for 202501 → all for 202502 → etc.
- **Model 2 (Employee-wise)**: All months for Emp A → all months for Emp B → etc.

## Output

- **EEC Text File**: `#~#` delimited, CRLF line endings, ready for EPFO portal
- **Excel Audit Log**: Full expanded data for verification

## Unit Tests

Run validation:

```bash
python -m py_compile eec_utils.py
python -m py_compile app.py
```

Test core functions:

```python
from eec_utils import generate_month_list, calculate_eec_row, convert_df_to_eec_text
import pandas as pd

# Month list
assert generate_month_list("202501", "202504") == ["202501","202502","202503","202504"]
assert generate_month_list("202511", "202602") == ["202511","202512","202601","202602"]

# Calculation: 15000 wages
row = calculate_eec_row("100257274743", "TEST", "202501", 15000, 15000)
assert row["Employee PF Contribution"] == 1800   # 15000 * 0.12
assert row["Employer EPS Contribution"] == 1250  # 15000 * 0.0833
assert row["Employer PF Contribution"] == 550    # 1800 - 1250
```

## Bonus: Convert Existing ECR Format

If you have an existing ECR-format Excel (columns: UAN_NO, MEMBER_NAME, GROSS_WAGES, EPF_WAGES, EPS_WAGES, EDLI_WAGES, EPF_CONTRI_REMITTED, EPS_CONTRI_REMITTED, EPF_EPS_DIFF_REMITTED, NCP_DAYS):

```python
import pandas as pd
from eec_utils import expand_employee_data, sort_model_1, convert_df_to_eec_text, get_excel_audit_log

ecr_df = pd.read_excel("debasis.xlsx")

# Map ECR columns to EEC input format
eec_input = pd.DataFrame({
    "UAN": ecr_df["UAN_NO"],
    "Member Name": ecr_df["MEMBER_NAME"],
    "Gross Wages": ecr_df["GROSS_WAGES"],
    "EPF Wages": ecr_df["EPF_WAGES"],
    "Start Month (YYYYMM)": "",  # will use global
    "End Month (YYYYMM)": "",
    "NCP Days": ecr_df["NCP_DAYS"]
})

expanded = expand_employee_data(eec_input, "202501", "202603")
sorted_df = sort_model_1(expanded)

# Generate files
with open("EEC_Return.txt", "w") as f:
    f.write(convert_df_to_eec_text(sorted_df))

with open("EEC_Audit.xlsx", "wb") as f:
    f.write(get_excel_audit_log(sorted_df))
```

## Configuration

Sidebar allows adjusting:
- Global period (Start/End YYYYMM)
- EPS Wage Cap (default ₹15,000)
- EDLI Wage Cap (default ₹15,000)
- PF Rate (default 12%)
- EPS Rate (default 8.33%)

## Requirements

- Python 3.8+
- streamlit
- pandas
- openpyxl
- numpy

## License

Internal use — EPFO compliance tool.