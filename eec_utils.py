import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO


DEFAULT_EPS_CAP = 15000
DEFAULT_EDLI_CAP = 15000
DEFAULT_PF_RATE = 0.12
DEFAULT_EPS_RATE = 0.0833


def _round_half_up(x: float) -> int:
    return int(x + 0.5) if x >= 0 else int(x - 0.5)


def generate_month_list(start_str: str, end_str: str) -> List[str]:
    start_year = int(start_str[:4])
    start_month = int(start_str[4:])
    end_year = int(end_str[:4])
    end_month = int(end_str[4:])

    months = []
    current_year = start_year
    current_month = start_month

    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
        months.append(f"{current_year}{current_month:02d}")
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    return months


def calculate_eec_row(
    uan: str,
    name: str,
    wage_month: str,
    gross: float,
    epf_wage: float,
    eps_cap: float = DEFAULT_EPS_CAP,
    edli_cap: float = DEFAULT_EDLI_CAP,
    pf_rate: float = DEFAULT_PF_RATE,
    eps_rate: float = DEFAULT_EPS_RATE,
    ncp: int = 0
) -> Dict[str, Any]:
    uan_padded = str(uan).strip().zfill(12)
    name_upper = str(name).strip().upper()
    gross_val = _round_half_up(float(gross))
    epf_wage_val = _round_half_up(float(epf_wage))

    eps_wage = _round_half_up(min(epf_wage_val, eps_cap))
    edli_wage = _round_half_up(min(epf_wage_val, edli_cap))

    ee_pf = _round_half_up(epf_wage_val * pf_rate)
    er_eps = _round_half_up(eps_wage * eps_rate)
    er_pf = ee_pf - er_eps

    return {
        "UAN": uan_padded,
        "Member Name": name_upper,
        "Wage Month (YYYYMM)": wage_month,
        "Gross Wages": gross_val,
        "EPF Wages": epf_wage_val,
        "EPS Wages": eps_wage,
        "EDLI Wages": edli_wage,
        "Employee PF Contribution": ee_pf,
        "Employer EPS Contribution": er_eps,
        "Employer PF Contribution": er_pf,
        "NCP Days": int(ncp)
    }


def is_long_format(df: pd.DataFrame) -> bool:
    cols = [c.lower().replace(" ", "").replace("_", "") for c in df.columns]
    return any("wagemonth" in c or "wagemonth(yyyymm)" in c for c in cols)


def process_long_format(df: pd.DataFrame) -> pd.DataFrame:
    required = ["UAN", "Member Name", "Wage Month (YYYYMM)", "Gross Wages", "EPF Wages"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Long format missing required column: {col}")

    if "NCP Days" not in df.columns:
        df["NCP Days"] = 0

    df["NCP Days"] = df["NCP Days"].fillna(0).astype(int)
    df["Wage Month (YYYYMM)"] = df["Wage Month (YYYYMM)"].astype(str)

    rows = []
    for _, row in df.iterrows():
        rows.append(calculate_eec_row(
            uan=row["UAN"],
            name=row["Member Name"],
            wage_month=str(row["Wage Month (YYYYMM)"]),
            gross=row["Gross Wages"],
            epf_wage=row["EPF Wages"],
            ncp=row["NCP Days"]
        ))

    return pd.DataFrame(rows)


def expand_employee_data(df: pd.DataFrame, global_start: str, global_end: str) -> pd.DataFrame:
    if is_long_format(df):
        return process_long_format(df)

    required_cols = ["UAN", "Member Name", "Gross Wages", "EPF Wages"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    if "Start Month (YYYYMM)" not in df.columns:
        df["Start Month (YYYYMM)"] = global_start
    if "End Month (YYYYMM)" not in df.columns:
        df["End Month (YYYYMM)"] = global_end
    if "NCP Days" not in df.columns:
        df["NCP Days"] = 0

    df["Start Month (YYYYMM)"] = df["Start Month (YYYYMM)"].fillna(global_start).astype(str)
    df["End Month (YYYYMM)"] = df["End Month (YYYYMM)"].fillna(global_end).astype(str)
    df["NCP Days"] = df["NCP Days"].fillna(0).astype(int)

    rows = []
    for _, row in df.iterrows():
        uan = row["UAN"]
        name = row["Member Name"]
        gross = row["Gross Wages"]
        epf_wage = row["EPF Wages"]
        start_month = str(row["Start Month (YYYYMM)"])
        end_month = str(row["End Month (YYYYMM)"])
        ncp = int(row["NCP Days"])

        if len(start_month) != 6:
            start_month = global_start
        if len(end_month) != 6:
            end_month = global_end

        months = generate_month_list(start_month, end_month)
        for m in months:
            rows.append(calculate_eec_row(
                uan=uan,
                name=name,
                wage_month=m,
                gross=gross,
                epf_wage=epf_wage,
                ncp=ncp
            ))

    return pd.DataFrame(rows)


def sort_model_1(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(["Wage Month (YYYYMM)", "UAN"]).reset_index(drop=True)


def sort_model_2(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(["UAN", "Wage Month (YYYYMM)"]).reset_index(drop=True)


def convert_df_to_eec_text(df: pd.DataFrame) -> str:
    cols_order = [
        "UAN", "Member Name", "Wage Month (YYYYMM)", "Gross Wages",
        "EPF Wages", "EPS Wages", "EDLI Wages",
        "Employee PF Contribution", "Employer EPS Contribution",
        "Employer PF Contribution", "NCP Days"
    ]
    df_ordered = df[cols_order].copy()
    lines = df_ordered.astype(str).agg("#~#".join, axis=1)
    return "\r\n".join(lines) + "\r\n"


def get_excel_template() -> bytes:
    df = pd.DataFrame({
        "UAN": ["100257274743", "100427601130"],
        "Member Name": ["NITESH", "RAMESH"],
        "Gross Wages": [15000, 20000],
        "EPF Wages": [15000, 15000],
        "Start Month (YYYYMM)": ["202501", ""],
        "End Month (YYYYMM)": ["202603", ""],
        "NCP Days": [0, 0]
    })
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Employees")
    return buffer.getvalue()


def get_excel_template_long() -> bytes:
    df = pd.DataFrame({
        "UAN": ["100257274743", "100257274743", "100427601130"],
        "Member Name": ["NITESH", "NITESH", "RAMESH"],
        "Wage Month (YYYYMM)": ["202501", "202502", "202501"],
        "Gross Wages": [15000, 16000, 20000],
        "EPF Wages": [15000, 15000, 15000],
        "NCP Days": [0, 1, 0]
    })
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Employees_Long")
    return buffer.getvalue()


def get_csv_template() -> str:
    df = pd.DataFrame({
        "UAN": ["100257274743", "100427601130"],
        "Member Name": ["NITESH", "RAMESH"],
        "Gross Wages": [15000, 20000],
        "EPF Wages": [15000, 15000],
        "Start Month (YYYYMM)": ["202501", ""],
        "End Month (YYYYMM)": ["202603", ""],
        "NCP Days": [0, 0]
    })
    return df.to_csv(index=False)


def get_csv_template_long() -> str:
    df = pd.DataFrame({
        "UAN": ["100257274743", "100257274743", "100427601130"],
        "Member Name": ["NITESH", "NITESH", "RAMESH"],
        "Wage Month (YYYYMM)": ["202501", "202502", "202501"],
        "Gross Wages": [15000, 16000, 20000],
        "EPF Wages": [15000, 15000, 15000],
        "NCP Days": [0, 1, 0]
    })
    return df.to_csv(index=False)


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {
            "Total Records": 0,
            "Unique Employees": 0,
            "Total Gross Wages": 0,
            "Total EPF Wages": 0,
            "Total EE PF": 0,
            "Total ER EPS": 0,
            "Total ER PF": 0,
            "Total NCP Days": 0
        }
    return {
        "Total Records": len(df),
        "Unique Employees": df["UAN"].nunique(),
        "Total Gross Wages": df["Gross Wages"].sum(),
        "Total EPF Wages": df["EPF Wages"].sum(),
        "Total EE PF": df["Employee PF Contribution"].sum(),
        "Total ER EPS": df["Employer EPS Contribution"].sum(),
        "Total ER PF": df["Employer PF Contribution"].sum(),
        "Total NCP Days": df["NCP Days"].sum()
    }


def get_excel_audit_log(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="EEC_Audit")
    return buffer.getvalue()


def auto_detect_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    for col in df.columns:
        cl = col.lower().replace(" ", "").replace("_", "").replace("-", "")
        if "uan" in cl:
            col_map[col] = "UAN"
        elif "member" in cl and "name" in cl:
            col_map[col] = "Member Name"
        elif "gross" in cl and "wage" in cl:
            col_map[col] = "Gross Wages"
        elif "epf" in cl and "wage" in cl:
            col_map[col] = "EPF Wages"
        elif "wage" in cl and "month" in cl:
            col_map[col] = "Wage Month (YYYYMM)"
        elif "start" in cl and "month" in cl:
            col_map[col] = "Start Month (YYYYMM)"
        elif "end" in cl and "month" in cl:
            col_map[col] = "End Month (YYYYMM)"
        elif "ncp" in cl and "day" in cl:
            col_map[col] = "NCP Days"
    df_renamed = df.rename(columns=col_map)
    return df_renamed