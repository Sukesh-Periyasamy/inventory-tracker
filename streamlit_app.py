import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================
# File Paths
# =========================
OUTGOING_FILE = "lab_outgoing.csv"
RETURNED_FILE = "lab_returned.csv"

# =========================
# Sample Data (auto-create)
# =========================
if not os.path.exists(OUTGOING_FILE):
    sample_outgoing = pd.DataFrame([
        {"Date": "2025-08-20", "Roll No": "22BCS001", "Name": "Rahul", "Product": "Microscope", "Quantity": 1},
        {"Date": "2025-08-21", "Roll No": "22BCS002", "Name": "Priya", "Product": "Beaker", "Quantity": 2},
    ])
    sample_outgoing.to_csv(OUTGOING_FILE, index=False)

if not os.path.exists(RETURNED_FILE):
    sample_returned = pd.DataFrame([
        {"Date": "2025-08-22", "Roll No": "22BCS001", "Product": "Microscope", "Quantity": 1},
    ])
    sample_returned.to_csv(RETURNED_FILE, index=False)

# =========================
# Load CSVs
# =========================
def load_data():
    outgoing = pd.read_csv(OUTGOING_FILE)
    returned = pd.read_csv(RETURNED_FILE)
    return outgoing, returned

def save_data(df, file):
    df.to_csv(file, index=False)

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="🧪 Lab Register System", layout="wide")
st.title("🧪 Lab Register System")

tabs = st.tabs(["➕ Outgoing Entry", "✅ Returned Entry", "📊 Reports & Filters"])

# =========================
# Outgoing Entry
# =========================
with tabs[0]:
    st.header("➕ Add Outgoing Product")

    with st.form("outgoing_form", clear_on_submit=True):
        roll = st.text_input("Roll No")
        name = st.text_input("Student Name")
        product = st.text_input("Product")
        qty = st.number_input("Quantity", min_value=1, step=1)
        submitted = st.form_submit_button("Add Outgoing")

        if submitted:
            outgoing, returned = load_data()
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Roll No": roll,
                "Name": name,
                "Product": product,
                "Quantity": qty
            }
            outgoing = pd.concat([outgoing, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(outgoing, OUTGOING_FILE)
            st.success(f"✅ Outgoing entry added for {name} ({product})")

# =========================
# Returned Entry
# =========================
with tabs[1]:
    st.header("✅ Add Returned Product")

    with st.form("returned_form", clear_on_submit=True):
        roll = st.text_input("Roll No (Return)")
        product = st.text_input("Product (Return)")
        qty = st.number_input("Quantity Returned", min_value=1, step=1)
        submitted = st.form_submit_button("Add Returned")

        if submitted:
            outgoing, returned = load_data()
            new_entry = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Roll No": roll,
                "Product": product,
                "Quantity": qty
            }
            returned = pd.concat([returned, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(returned, RETURNED_FILE)
            st.success(f"✅ Return entry added for {roll} ({product})")

# =========================
# Reports & Filters
# =========================
with tabs[2]:
    st.header("📊 Reports & Filters")

    outgoing, returned = load_data()

    # --- Issued Report
    st.subheader("📦 All Issued Products")
    st.dataframe(outgoing, use_container_width=True)

    # --- Returned Report
    st.subheader("📥 All Returned Products")
    st.dataframe(returned, use_container_width=True)

    # --- Not Returned Report
    st.subheader("❌ Not Yet Returned")

    if not outgoing.empty:
        issued_summary = outgoing.groupby(["Roll No", "Name", "Product"], as_index=False)["Quantity"].sum()
        returned_summary = returned.groupby(["Roll No", "Product"], as_index=False)["Quantity"].sum()

        merged = issued_summary.merge(
            returned_summary,
            on=["Roll No", "Product"],
            how="left",
            suffixes=("_issued", "_returned")
        )

        merged["Quantity_returned"] = merged["Quantity_returned"].fillna(0)
        merged["Pending"] = merged["Quantity_issued"] - merged["Quantity_returned"]
        not_returned = merged[merged["Pending"] > 0]

        st.dataframe(not_returned, use_container_width=True)
    else:
        st.info("No outgoing records yet.")
