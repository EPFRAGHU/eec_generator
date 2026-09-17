import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import eec_utils


st.set_page_config(
    page_title="EPFO EEC-2026 Return File Generator",
    page_icon="📋",
    layout="wide"
)

st.title("📋 EPFO EEC-2026 Return File Generator")

with st.sidebar:
    st.header("⚙️ Global Period & Rates")

    col_start, col_end = st.columns(2)
    with col_start:
        start_year = st.selectbox("Start Year", list(range(2020, 2028)), index=5)
        start_month = st.selectbox("Start Month", list(range(1, 13)), index=0)
    with col_end:
        end_year = st.selectbox("End Year", list(range(2020, 2028)), index=6)
        end_month = st.selectbox("End Month", list(range(1, 13)), index=2)

    global_start = f"{start_year}{start_month:02d}"
    global_end = f"{end_year}{end_month:02d}"

    st.divider()
    st.subheader("🔧 Configurable Caps & Rates")
    eps_cap = st.number_input("EPS Wage Cap (₹)", value=15000, step=1000, min_value=1)
    edli_cap = st.number_input("EDLI Wage Cap (₹)", value=15000, step=1000, min_value=1)
    pf_rate = st.number_input("PF Rate (%)", value=12.0, step=0.1, min_value=0.0, max_value=100.0) / 100
    eps_rate = st.number_input("EPS Rate (%)", value=8.33, step=0.01, min_value=0.0, max_value=100.0) / 100

    st.divider()
    st.subheader("📥 Download Templates")
    excel_bytes = eec_utils.get_excel_template()
    st.download_button(
        "📊 Excel Template",
        data=excel_bytes,
        file_name="eec_employee_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    csv_text = eec_utils.get_csv_template()
    st.download_button(
        "📄 CSV Template",
        data=csv_text,
        file_name="eec_employee_template.csv",
        mime="text/csv",
        use_container_width=True
    )


tab_upload, tab_manual = st.tabs(["📤 Upload Employees List", "✍️ Manual Quick Entry"])

employee_df = None

with tab_upload:
    st.subheader("Upload Employee Data (Excel/CSV)")
    uploaded = st.file_uploader("Choose file", type=["xlsx", "xls", "csv"])
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            df = eec_utils.auto_detect_columns(df)
            st.success(f"Loaded {len(df)} employee(s) with auto-detected columns.")
            st.dataframe(df.head(10), use_container_width=True)
            employee_df = df
        except Exception as e:
            st.error(f"Error reading file: {e}")

with tab_manual:
    st.subheader("Manual Entry Grid")
    st.caption("Add/edit rows directly. Pre-filled with 2 sample rows.")
    sample_df = pd.DataFrame({
        "UAN": ["100257274743", "100427601130"],
        "Member Name": ["NITESH", "RAMESH"],
        "Gross Wages": [15000.0, 20000.0],
        "EPF Wages": [15000.0, 15000.0],
        "Start Month (YYYYMM)": ["202501", ""],
        "End Month (YYYYMM)": ["202603", ""],
        "NCP Days": [0, 0]
    })
    edited_df = st.data_editor(
        sample_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "UAN": st.column_config.TextColumn("UAN", help="12-digit UAN"),
            "Member Name": st.column_config.TextColumn("Member Name"),
            "Gross Wages": st.column_config.NumberColumn("Gross Wages", format="%.2f"),
            "EPF Wages": st.column_config.NumberColumn("EPF Wages", format="%.2f"),
            "Start Month (YYYYMM)": st.column_config.TextColumn("Start Month (YYYYMM)", help="Optional"),
            "End Month (YYYYMM)": st.column_config.TextColumn("End Month (YYYYMM)", help="Optional"),
            "NCP Days": st.column_config.NumberColumn("NCP Days", format="%d", min_value=0),
        }
    )
    if st.button("Use Manual Data", type="primary"):
        employee_df = edited_df
        st.success(f"Using {len(employee_df)} employee(s) from manual entry.")


if employee_df is not None and not employee_df.empty:
    st.divider()
    st.header("🔄 Processing")

    try:
        expanded_df = eec_utils.expand_employee_data(
            employee_df,
            global_start=global_start,
            global_end=global_end
        )
    except Exception as e:
        st.error(f"Expansion error: {e}")
        st.stop()

    if expanded_df.empty:
        st.warning("No records generated. Check date ranges.")
        st.stop()

    model_choice = st.radio(
        "File Structure Model",
        ["Model 1: Month-wise Blocks", "Model 2: Employee-wise Blocks"],
        horizontal=True
    )

    if model_choice == "Model 1: Month-wise Blocks":
        final_df = eec_utils.sort_model_1(expanded_df)
    else:
        final_df = eec_utils.sort_model_2(expanded_df)

    kpis = eec_utils.compute_kpis(final_df)

    st.subheader("📊 KPI Summary")
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Records", f"{kpis['Total Records']:,}")
    kpi_cols[1].metric("Unique Employees", f"{kpis['Unique Employees']:,}")
    kpi_cols[2].metric("Total Gross Wages", f"₹{kpis['Total Gross Wages']:,.2f}")
    kpi_cols[3].metric("Total EPF Wages", f"₹{kpis['Total EPF Wages']:,.2f}")

    kpi_cols2 = st.columns(4)
    kpi_cols2[0].metric("Total EE PF", f"₹{kpis['Total EE PF']:,.2f}")
    kpi_cols2[1].metric("Total ER EPS", f"₹{kpis['Total ER EPS']:,.2f}")
    kpi_cols2[2].metric("Total ER PF", f"₹{kpis['Total ER PF']:,.2f}")
    kpi_cols2[3].metric("Total NCP Days", f"{kpis['Total NCP Days']:,}")

    st.subheader("📋 Review & Edit Grid")
    display_df = final_df.copy()
    display_df.insert(0, "Sr.", range(1, len(display_df) + 1))

    col_rename_map = {
        "UAN": "1. UAN",
        "Member Name": "2. Member Name",
        "Wage Month (YYYYMM)": "3. Wage Month (YYYYMM)",
        "Gross Wages": "4. Gross Wages",
        "EPF Wages": "5. EPF Wages",
        "EPS Wages": "6. EPS Wages",
        "EDLI Wages": "7. EDLI Wages",
        "Employee PF Contribution": "8. Employee PF Contribution",
        "Employer EPS Contribution": "9. Employer EPS Contribution",
        "Employer PF Contribution": "10. Employer PF Contribution",
        "NCP Days": "11. NCP Days"
    }
    display_df = display_df.rename(columns=col_rename_map)

    edited_review = st.data_editor(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Sr.": st.column_config.NumberColumn("Sr.", disabled=True),
            "1. UAN": st.column_config.TextColumn("1. UAN", disabled=True),
            "2. Member Name": st.column_config.TextColumn("2. Member Name", disabled=True),
            "3. Wage Month (YYYYMM)": st.column_config.TextColumn("3. Wage Month", disabled=True),
            "4. Gross Wages": st.column_config.NumberColumn("4. Gross Wages", format="%.2f"),
            "5. EPF Wages": st.column_config.NumberColumn("5. EPF Wages", format="%.2f"),
            "6. EPS Wages": st.column_config.NumberColumn("6. EPS Wages", format="%.2f"),
            "7. EDLI Wages": st.column_config.NumberColumn("7. EDLI Wages", format="%.2f"),
            "8. Employee PF Contribution": st.column_config.NumberColumn("8. EE PF", format="%d"),
            "9. Employer EPS Contribution": st.column_config.NumberColumn("9. ER EPS", format="%d"),
            "10. Employer PF Contribution": st.column_config.NumberColumn("10. ER PF", format="%d"),
            "11. NCP Days": st.column_config.NumberColumn("11. NCP Days", format="%d", min_value=0),
        }
    )

    if not edited_review.equals(display_df):
        reverse_map = {v: k for k, v in col_rename_map.items()}
        edited_review = edited_review.rename(columns=reverse_map)
        edited_review = edited_review.drop(columns=["Sr."], errors="ignore")
        final_df = edited_review
        kpis = eec_utils.compute_kpis(final_df)

    st.subheader("👁️ Text File Preview (#~# delimited)")
    preview_text = eec_utils.convert_df_to_eec_text(final_df)
    preview_lines = preview_text.strip().split("\r\n")
    preview_display = "\r\n".join(preview_lines[:15])
    if len(preview_lines) > 15:
        preview_display += f"\r\n... and {len(preview_lines) - 15} more lines"
    st.code(preview_display, language="text")

    st.divider()
    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        st.download_button(
            "📥 Download EEC Text File",
            data=preview_text,
            file_name=f"EEC_Return_{global_start}_{global_end}.txt",
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )

    with col_dl2:
        audit_bytes = eec_utils.get_excel_audit_log(final_df)
        st.download_button(
            "📊 Download Excel Audit Log",
            data=audit_bytes,
            file_name=f"EEC_Audit_{global_start}_{global_end}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.info("👆 Upload a file or use Manual Entry tab to load employee data.")