import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File paths
OUTGOING_FILE = "lab_outgoing.csv"
INCOMING_FILE = "lab_incoming.csv"
TRANSACTIONS_FILE = "transactions.csv"

# ---------- Utility: Create CSVs if missing ----------
def init_files():
    if not os.path.exists(OUTGOING_FILE):
        pd.DataFrame(columns=["Roll No", "Name", "Product", "Date"]).to_csv(OUTGOING_FILE, index=False)
    if not os.path.exists(INCOMING_FILE):
        pd.DataFrame(columns=["Roll No", "Name", "Product", "Date"]).to_csv(INCOMING_FILE, index=False)
    if not os.path.exists(TRANSACTIONS_FILE):
        pd.DataFrame(columns=["Roll No", "Name", "Product", "Status", "Date"]).to_csv(TRANSACTIONS_FILE, index=False)

# Initialize
init_files()

# ---------- Load Data ----------
def load_data():
    outgoing = pd.read_csv(OUTGOING_FILE)
    incoming = pd.read_csv(INCOMING_FILE)
    transactions = pd.read_csv(TRANSACTIONS_FILE)
    return outgoing, incoming, transactions

def save_data(outgoing, incoming, transactions):
    outgoing.to_csv(OUTGOING_FILE, index=False)
    incoming.to_csv(INCOMING_FILE, index=False)
    transactions.to_csv(TRANSACTIONS_FILE, index=False)

# ---------- Streamlit UI ----------
st.title("🧪 Lab Register System")

menu = st.sidebar.radio("Navigation", ["Outgoing", "Incoming", "Reports"])

outgoing, incoming, transactions = load_data()

# ---------------- OUTGOING ----------------
if menu == "Outgoing":
    st.header("📤 Outgoing Products")
    with st.form("outgoing_form"):
        roll = st.text_input("Roll Number")
        name = st.text_input("Name")
        product = st.text_input("Product Name")
        submitted = st.form_submit_button("Submit Outgoing")
        if submitted:
            if roll and name and product:
                date = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_entry = pd.DataFrame([[roll, name, product, date]], columns=["Roll No", "Name", "Product", "Date"])
                outgoing = pd.concat([outgoing, new_entry], ignore_index=True)
                transactions = pd.concat([transactions, pd.DataFrame([[roll, name, product, "Outgoing", date]], 
                                                                     columns=["Roll No", "Name", "Product", "Status", "Date"])], ignore_index=True)
                save_data(outgoing, incoming, transactions)
                st.success(f"Product '{product}' issued to {name} ({roll})")

    st.subheader("Outgoing Records")
    st.dataframe(outgoing)

# ---------------- INCOMING ----------------
elif menu == "Incoming":
    st.header("📥 Incoming Products (Return)")
    roll = st.text_input("Enter Roll Number")
    if roll:
        # Find products not returned
        issued = outgoing[outgoing["Roll No"] == roll]
        returned = incoming[incoming["Roll No"] == roll]
        not_returned = issued[~issued["Product"].isin(returned["Product"])]

        if not_returned.empty:
            st.info("No pending products for this student.")
        else:
            st.write("Pending products:")
            product = st.selectbox("Select product to return", not_returned["Product"].unique())
            if st.button("Submit Return"):
                row = not_returned[not_returned["Product"] == product].iloc[0]
                date = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_entry = pd.DataFrame([[roll, row["Name"], product, date]], columns=["Roll No", "Name", "Product", "Date"])
                incoming = pd.concat([incoming, new_entry], ignore_index=True)
                transactions = pd.concat([transactions, pd.DataFrame([[roll, row["Name"], product, "Incoming", date]], 
                                                                     columns=["Roll No", "Name", "Product", "Status", "Date"])], ignore_index=True)
                save_data(outgoing, incoming, transactions)
                st.success(f"Product '{product}' returned by {row['Name']} ({roll})")

    st.subheader("Incoming Records")
    st.dataframe(incoming)

# ---------------- REPORTS ----------------
elif menu == "Reports":
    st.header("📊 Reports & Filters")

    # Not returned items
    issued_all = outgoing.copy()
    returned_all = incoming.copy()
    not_returned = issued_all.merge(returned_all, on=["Roll No", "Product"], how="left", suffixes=("_issued", "_returned"))
    not_returned = not_returned[not_returned["Date_returned"].isna()][["Roll No", "Name_issued", "Product", "Date_issued"]]
    not_returned.rename(columns={"Name_issued": "Name", "Date_issued": "Issued Date"}, inplace=True)

    st.subheader("❌ Not Returned Products")
    st.dataframe(not_returned)

    # Student-wise search
    st.subheader("🔎 Student History")
    search_roll = st.text_input("Enter Roll No to view history")
    if search_roll:
        student_history = transactions[transactions["Roll No"] == search_roll]
        if student_history.empty:
            st.info("No records found for this Roll Number.")
        else:
            st.dataframe(student_history)
