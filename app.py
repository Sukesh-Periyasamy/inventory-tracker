import streamlit as st
import pandas as pd
import os

# File paths
OUT_FILE = "lab_outgoing.csv"
INVENTORY_FILE = "inventory.csv"

# Initialize inventory (if not exists)
if not os.path.exists(INVENTORY_FILE):
    inventory_df = pd.DataFrame({
        "Product": ["Microscope", "Beaker", "Test Tube", "Pipette", "Slide"],
        "Quantity": [10, 50, 100, 40, 200]
    })
    inventory_df.to_csv(INVENTORY_FILE, index=False)
else:
    inventory_df = pd.read_csv(INVENTORY_FILE)

# Initialize outgoing log
if not os.path.exists(OUT_FILE):
    outgoing_df = pd.DataFrame(columns=["Roll No", "Name", "Product", "Date", "Status"])
    outgoing_df.to_csv(OUT_FILE, index=False)

# Load data
outgoing_df = pd.read_csv(OUT_FILE)

st.title("🔬 Lab Inventory Management System")

# Tabs for Outgoing and Incoming
tab1, tab2, tab3 = st.tabs(["📤 Outgoing", "📥 Incoming", "📊 Admin Dashboard"])

# ---------------- OUTGOING ----------------
with tab1:
    st.header("📤 Outgoing Register (Student Taking Item)")
    with st.form("outgoing_form"):
        roll = st.text_input("Roll Number")
        name = st.text_input("Student Name")
        product = st.selectbox("Select Product", inventory_df["Product"].tolist())
        date = st.date_input("Date")
        submitted = st.form_submit_button("Submit Outgoing")

        if submitted:
            # Check balance
            if inventory_df.loc[inventory_df["Product"] == product, "Quantity"].values[0] > 0:
                new_entry = pd.DataFrame([[roll, name, product, date, "Not Returned"]],
                                         columns=["Roll No", "Name", "Product", "Date", "Status"])
                outgoing_df = pd.concat([outgoing_df, new_entry], ignore_index=True)
                outgoing_df.to_csv(OUT_FILE, index=False)

                # Decrease balance
                inventory_df.loc[inventory_df["Product"] == product, "Quantity"] -= 1
                inventory_df.to_csv(INVENTORY_FILE, index=False)

                st.success(f"{product} issued to {name} ({roll}) ✅")
            else:
                st.error("❌ Not enough stock available!")

# ---------------- INCOMING ----------------
with tab2:
    st.header("📥 Incoming Register (Student Returning Item)")
    roll_in = st.text_input("Enter Roll Number")

    if roll_in:
        student_items = outgoing_df[(outgoing_df["Roll No"] == roll_in) &
                                    (outgoing_df["Status"] == "Not Returned")]

        if not student_items.empty:
            product_to_return = st.selectbox("Select Product to Return",
                                             student_items["Product"].tolist())

            if st.button("Submit Incoming"):
                # Update outgoing record
                idx = outgoing_df[(outgoing_df["Roll No"] == roll_in) &
                                  (outgoing_df["Product"] == product_to_return) &
                                  (outgoing_df["Status"] == "Not Returned")].index[0]
                outgoing_df.at[idx, "Status"] = "Returned"
                outgoing_df.to_csv(OUT_FILE, index=False)

                # Increase balance
                inventory_df.loc[inventory_df["Product"] == product_to_return, "Quantity"] += 1
                inventory_df.to_csv(INVENTORY_FILE, index=False)

                st.success(f"{product_to_return} returned successfully ✅")
        else:
            st.info("No pending items found for this Roll Number.")

# ---------------- ADMIN DASHBOARD ----------------
with tab3:
    st.header("📊 Admin Dashboard")

    # Inventory balance
    st.subheader("📦 Inventory Balance")
    st.dataframe(inventory_df, use_container_width=True)

    # Students with unreturned items
    st.subheader("❌ Students with Pending Returns")
    pending = outgoing_df[outgoing_df["Status"] == "Not Returned"]
    if not pending.empty:
        st.dataframe(pending, use_container_width=True)
    else:
        st.success("✅ No pending returns!")

    # Filter by roll number
    st.subheader("🔎 Search Student Records")
    search_roll = st.text_input("Enter Roll Number to Search")
    if search_roll:
        student_history = outgoing_df[outgoing_df["Roll No"] == search_roll]
        if not student_history.empty:
            st.dataframe(student_history, use_container_width=True)
        else:
            st.info("No records found for this student.")

    # Download logs
    st.download_button("📥 Download Outgoing Log",
                       outgoing_df.to_csv(index=False), "outgoing_log.csv")
    st.download_button("📥 Download Inventory Balance",
                       inventory_df.to_csv(index=False), "inventory_balance.csv")
