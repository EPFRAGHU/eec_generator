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
    ncp: int = 0,
    eps_wage: float = None,
    edli_wage: float = None,
    is_non_eps: bool = False
) -> Dict[str, Any]:
    uan_padded = str(uan).strip().zfill(12)
    name_upper = str(name).strip().upper()
    gross_val = _round_half_up(float(gross))
    epf_wage_val = _round_half_up(float(epf_wage))

    if is_non_eps:
        eps_wage_val = 0
    elif eps_wage is not None:
        eps_wage_val = _round_half_up(min(float(eps_wage), eps_cap))
    else:
        eps_wage_val = _round_half_up(min(epf_wage_val, eps_cap))

    if edli_wage is not None:
        edli_wage_val = _round_half_up(min(float(edli_wage), edli_cap))
    else:
        edli_wage_val = _round_half_up(min(epf_wage_val, edli_cap))

    ee_pf = _round_half_up(epf_wage_val * pf_rate)
    er_eps = _round_half_up(eps_wage_val * eps_rate) if not is_non_eps else 0
    er_pf = ee_pf - er_eps

    return {
        "UAN": uan_padded,
        "Member Name": name_upper,
        "Wage Month (YYYYMM)": wage_month,
        "Gross Wages": gross_val,
        "EPF Wages": epf_wage_val,
        "EPS Wages": eps_wage_val,
        "EDLI Wages": edli_wage_val,
        "Employee PF Contribution": ee_pf,
        "Employer EPS Contribution": er_eps,
        "Employer PF Contribution": er_pf,
        "NCP Days": int(ncp),
        "Is Non-EPS": is_non_eps
    }


def is_long_format(df: pd.DataFrame) -> bool:
    cols = [c.lower().replace(" ", "").replace("_", "") for c in df.columns]
    return any("wagemonth" in c or "wagemonth(yyyymm)" in c for c in cols)


def process_long_format(df: pd.DataFrame) -> pd.DataFrame:
    required = ["UAN", "Member Name", "Wage Month (YYYYMM)", "Gross Wages", "EPF Wages"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Long format missing required column: {col}")

    for col in ["NCP Days", "EPS Wages", "EDLI Wages", "Is Non-EPS"]:
        if col not in df.columns:
            df[col] = 0 if col == "NCP Days" else (False if col == "Is Non-EPS" else None)

    df["NCP Days"] = df["NCP Days"].fillna(0).astype(int)
    df["Wage Month (YYYYMM)"] = df["Wage Month (YYYYMM)"].astype(str)
    df["Is Non-EPS"] = df["Is Non-EPS"].fillna(False).astype(bool)

    rows = []
    for _, row in df.iterrows():
        rows.append(calculate_eec_row(
            uan=row["UAN"],
            name=row["Member Name"],
            wage_month=str(row["Wage Month (YYYYMM)"]),
            gross=row["Gross Wages"],
            epf_wage=row["EPF Wages"],
            ncp=row["NCP Days"],
            eps_wage=row["EPS Wages"] if pd.notna(row["EPS Wages"]) else None,
            edli_wage=row["EDLI Wages"] if pd.notna(row["EDLI Wages"]) else None,
            is_non_eps=row["Is Non-EPS"]
        ))

    return pd.DataFrame(rows)


def expand_employee_data(df: pd.DataFrame, global_start: str, global_end: str) -> pd.DataFrame:
    if is_long_format(df):
        return process_long_format(df)

    required_cols = ["UAN", "Member Name", "Gross Wages", "EPF Wages"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    for col in ["Start Month (YYYYMM)", "End Month (YYYYMM)", "NCP Days", "EPS Wages", "EDLI Wages", "Is Non-EPS"]:
        if col not in df.columns:
            if col in ["Start Month (YYYYMM)", "End Month (YYYYMM)"]:
                df[col] = global_start if col == "Start Month (YYYYMM)" else global_end
            elif col == "NCP Days":
                df[col] = 0
            elif col == "Is Non-EPS":
                df[col] = False
            else:
                df[col] = None

    df["Start Month (YYYYMM)"] = df["Start Month (YYYYMM)"].fillna(global_start).astype(str)
    df["End Month (YYYYMM)"] = df["End Month (YYYYMM)"].fillna(global_end).astype(str)
    df["NCP Days"] = df["NCP Days"].fillna(0).astype(int)
    df["Is Non-EPS"] = df["Is Non-EPS"].fillna(False).astype(bool)

    rows = []
    for _, row in df.iterrows():
        uan = row["UAN"]
        name = row["Member Name"]
        gross = row["Gross Wages"]
        epf_wage = row["EPF Wages"]
        start_month = str(row["Start Month (YYYYMM)"])
        end_month = str(row["End Month (YYYYMM)"])
        ncp = int(row["NCP Days"])
        is_non_eps = bool(row["Is Non-EPS"])
        eps_wage = row["EPS Wages"] if pd.notna(row["EPS Wages"]) else None
        edli_wage = row["EDLI Wages"] if pd.notna(row["EDLI Wages"]) else None

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
                ncp=ncp,
                eps_wage=eps_wage,
                edli_wage=edli_wage,
                is_non_eps=is_non_eps
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
        "EPS Wages": [15000, 15000],
        "EDLI Wages": [15000, 15000],
        "Start Month (YYYYMM)": ["202501", ""],
        "End Month (YYYYMM)": ["202603", ""],
        "NCP Days": [0, 0],
        "Is Non-EPS": [False, False]
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
        "EPS Wages": [15000, 15000, 15000],
        "EDLI Wages": [15000, 15000, 15000],
        "NCP Days": [0, 1, 0],
        "Is Non-EPS": [False, False, False]
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
        "EPS Wages": [15000, 15000],
        "EDLI Wages": [15000, 15000],
        "Start Month (YYYYMM)": ["202501", ""],
        "End Month (YYYYMM)": ["202603", ""],
        "NCP Days": [0, 0],
        "Is Non-EPS": [False, False]
    })
    return df.to_csv(index=False)


def get_csv_template_long() -> str:
    df = pd.DataFrame({
        "UAN": ["100257274743", "100257274743", "100427601130"],
        "Member Name": ["NITESH", "NITESH", "RAMESH"],
        "Wage Month (YYYYMM)": ["202501", "202502", "202501"],
        "Gross Wages": [15000, 16000, 20000],
        "EPF Wages": [15000, 15000, 15000],
        "EPS Wages": [15000, 15000, 15000],
        "EDLI Wages": [15000, 15000, 15000],
        "NCP Days": [0, 1, 0],
        "Is Non-EPS": [False, False, False]
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
        elif "eps" in cl and "wage" in cl:
            col_map[col] = "EPS Wages"
        elif "edli" in cl and "wage" in cl:
            col_map[col] = "EDLI Wages"
        elif "wage" in cl and "month" in cl:
            col_map[col] = "Wage Month (YYYYMM)"
        elif "start" in cl and "month" in cl:
            col_map[col] = "Start Month (YYYYMM)"
        elif "end" in cl and "month" in cl:
            col_map[col] = "End Month (YYYYMM)"
        elif "ncp" in cl and "day" in cl:
            col_map[col] = "NCP Days"
        elif "non" in cl and "eps" in cl:
            col_map[col] = "Is Non-EPS"
    df_renamed = df.rename(columns=col_map)
    return df_renamed