import os
import pandas as pd
import streamlit as st

DATA_FILE = "lion_orders_data.csv"

st.set_page_config(
    page_title="LION INDUSTRY - Underwear OEM Order Management System",
    page_icon="👙",
    layout="wide",
)

st.title("👙 LION INDUSTRY Order & Operations Tracker")
st.caption(
    "End-to-End Workflow & Tax Refund Management (Brand Owner ↔ LION INDUSTRY ↔ Manufacturer)"
)

# Define the exact workflow stages
WORKFLOW_STAGES = [
    "1. Sample Received",
    "2. Price Quoted",
    "3. Price Agreed by Buyer",
    "4. PO Issued & Advance Payment",
    "5. Prototype Sample (Making/Shipped/Approved)",
    "6. Fitting Sample (Making/Shipped/Approved)",
    "7. Pre-Production Sample (Making/Shipped/Approved)",
    "8. Bulk Production in Progress",
    "9. Goods Ready",
    "10. Inspection Completed & Approved",
    "11. Balance Payment Received",
    "12. Shipping Booked & Goods Shipped",
    "13. Forwarder Paid",
    "14. B/L & Customs Declaration Received",
    "15. Factory VAT Receipts Received",
    "16. Tax Return Applied & Completed",
]

# Standard default columns structure
DEFAULT_COLUMNS = [
    "Order PO #",
    "Brand Owner / Buyer",
    "Manufacturer / Factory",
    "Item Description",
    "Current Stage",
    "PPS Approval",
    "Inspection Status",
    "Advance Payment",
    "Balance Payment",
    "Customs Declaration",
    "Factory VAT Receipt",
    "Tax Refund Status",
    "Total PO Amount ($)",
    "Deposit Received ($)",
    "Notes",
]

DEFAULT_DATA = [
    {
        "Order PO #": "PO-2026-UW01",
        "Brand Owner / Buyer": "Alpha Apparel (US)",
        "Manufacturer / Factory": "Yiwu Textile Factory A",
        "Item Description": "Men's Seamless Boxer Briefs (10,000 pcs)",
        "Current Stage": "7. Pre-Production Sample (Making/Shipped/Approved)",
        "PPS Approval": "Approved",
        "Inspection Status": "Pending",
        "Advance Payment": "Received",
        "Balance Payment": "Pending",
        "Customs Declaration": "Missing",
        "Factory VAT Receipt": "Pending",
        "Tax Refund Status": "Not Applied",
        "Total PO Amount ($)": 45000.0,
        "Deposit Received ($)": 13500.0,
        "Notes": "PPS approved on Sept 20. Preparing bulk raw materials.",
    },
    {
        "Order PO #": "PO-2026-UW02",
        "Brand Owner / Buyer": "Luxe Intimates (EU)",
        "Manufacturer / Factory": "Shantou Bra Mfg Co.",
        "Item Description": "Lace Bralette Set (5,000 pcs)",
        "Current Stage": "13. Forwarder Paid",
        "PPS Approval": "Approved",
        "Inspection Status": "Passed",
        "Advance Payment": "Received",
        "Balance Payment": "Received",
        "Customs Declaration": "Received",
        "Factory VAT Receipt": "Missing",
        "Tax Refund Status": "Pending Filing",
        "Total PO Amount ($)": 32000.0,
        "Deposit Received ($)": 32000.0,
        "Notes": "Goods shipped. Urgent follow-up needed with factory for VAT invoice.",
    },
]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Ensure all required columns exist in the DataFrame
            for col in DEFAULT_COLUMNS:
                if col not in df.columns:
                    df[col] = "Pending" if "Status" in col or "Payment" in col else ""
            return df[DEFAULT_COLUMNS]
        except Exception:
            return pd.DataFrame(DEFAULT_DATA)
    else:
        df = pd.DataFrame(DEFAULT_DATA)
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        return df


def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


if "order_df" not in st.session_state:
    st.session_state.order_df = load_data()

df = st.session_state.order_df

# ================= SIDEBAR =================
with st.sidebar:
    st.header("⚙️ Order Management")

    st.subheader("➕ Create New Order")
    with st.form("add_order_form", clear_on_submit=True):
        po_num = st.text_input("PO / Sample Tracking #", value="PO-2026-UW03")
        buyer = st.text_input("Brand Owner / Buyer", value="")
        factory = st.text_input("Manufacturer / Factory", value="")
        item_desc = st.text_input("Item / Style Description", value="")
        stage = st.selectbox("Initial Workflow Stage", WORKFLOW_STAGES)
        po_amt = st.number_input(
            "Total PO Amount ($)", min_value=0.0, value=0.0, step=1000.0
        )
        dep_amt = st.number_input(
            "Deposit Received ($)", min_value=0.0, value=0.0, step=500.0
        )
        notes = st.text_area("Notes / Specifications", value="")

        submitted = st.form_submit_button("Save New Order")
        if submitted:
            new_row = {
                "Order PO #": po_num,
                "Brand Owner / Buyer": buyer,
                "Manufacturer / Factory": factory,
                "Item Description": item_desc,
                "Current Stage": stage,
                "PPS Approval": "Pending",
                "Inspection Status": "Pending",
                "Advance Payment": "Received" if dep_amt > 0 else "Pending",
                "Balance Payment": "Pending",
                "Customs Declaration": "Missing",
                "Factory VAT Receipt": "Missing",
                "Tax Refund Status": "Not Applied",
                "Total PO Amount ($)": po_amt,
                "Deposit Received ($)": dep_amt,
                "Notes": notes,
            }
            st.session_state.order_df = pd.concat(
                [st.session_state.order_df, pd.DataFrame([new_row])],
                ignore_index=True,
            )
            save_data(st.session_state.order_df)
            st.success(f"Order {po_num} created successfully!")
            st.rerun()

    st.markdown("---")
    st.subheader("📂 Reset Data")
    if st.button("Reset to Sample OEM Ledger"):
        st.session_state.order_df = pd.DataFrame(DEFAULT_DATA)
        save_data(st.session_state.order_df)
        st.success("Ledger reset successfully!")
        st.rerun()

# ================= TOP METRICS & RISKS =================
total_orders = len(df)
shipped_orders = df[
    df["Current Stage"].isin([
        "12. Shipping Booked & Goods Shipped",
        "13. Forwarder Paid",
        "14. B/L & Customs Declaration Received",
        "15. Factory VAT Receipts Received",
        "16. Tax Return Applied & Completed",
    ])
]

missing_vat = df[
    df["Current Stage"].isin([
        "12. Shipping Booked & Goods Shipped",
        "13. Forwarder Paid",
        "14. B/L & Customs Declaration Received",
    ])
    & (df["Factory VAT Receipt"] == "Missing")
]

pending_tax_refund = df[
    (df["Customs Declaration"] == "Received")
    & (df["Factory VAT Receipt"] == "Received")
    & (df["Tax Refund Status"] != "Completed")
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Active Orders", f"{total_orders}")
col2.metric("Shipped Orders", f"{len(shipped_orders)}")
col3.metric("Missing Factory VAT Invoices", f"{len(missing_vat)}")
col4.metric("Pending Tax Refunds", f"{len(pending_tax_refund)}")

st.markdown("---")

# ================= DASHBOARD TABS =================
st.subheader("🚨 Key Bottlenecks & Critical Action Items")

tab_vat, tab_tax, tab_samples = st.tabs([
    f"🧾 Missing Factory VAT Receipts ({len(missing_vat)})",
    f"💰 Pending Tax Refunds ({len(pending_tax_refund)})",
    "🔍 Active Sampling / Pre-PO Orders",
])

with tab_vat:
    if not missing_vat.empty:
        st.error("Goods are shipped, but factory VAT invoices are missing:")
        st.dataframe(
            missing_vat[
                [
                    "Order PO #",
                    "Brand Owner / Buyer",
                    "Manufacturer / Factory",
                    "Current Stage",
                    "Factory VAT Receipt",
                    "Notes",
                ]
            ],
            use_container_width=True,
        )
    else:
        st.info("No missing VAT receipts for shipped orders.")

with tab_tax:
    if not pending_tax_refund.empty:
        st.warning("Customs Declaration & Factory VAT Receipts ready for Tax Refund:")
        st.dataframe(
            pending_tax_refund[
                [
                    "Order PO #",
                    "Brand Owner / Buyer",
                    "Manufacturer / Factory",
                    "Customs Declaration",
                    "Factory VAT Receipt",
                    "Tax Refund Status",
                    "Notes",
                ]
            ],
            use_container_width=True,
        )
    else:
        st.info("No orders currently waiting for tax refund filing.")

with tab_samples:
    sampling_orders = df[
        df["Current Stage"].str.contains("Sample|Price|PO Issued", regex=True)
    ]
    if not sampling_orders.empty:
        st.dataframe(
            sampling_orders[
                [
                    "Order PO #",
                    "Brand Owner / Buyer",
                    "Item Description",
                    "Current Stage",
                    "PPS Approval",
                    "Notes",
                ]
            ],
            use_container_width=True,
        )
    else:
        st.info("No active pre-PO or sampling orders.")

st.markdown("---")

# ================= MASTER TABLE =================
st.subheader("📊 Master Workflow Table (Double-click any cell to edit)")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    column_config={
        "Current Stage": st.column_config.SelectboxColumn(
            options=WORKFLOW_STAGES, required=True
        ),
        "PPS Approval": st.column_config.SelectboxColumn(
            options=["Pending", "Shipped", "Approved", "Rejected/Revision"],
            required=True,
        ),
        "Inspection Status": st.column_config.SelectboxColumn(
            options=["Pending", "Scheduled", "Passed", "Failed"], required=True
        ),
        "Advance Payment": st.column_config.SelectboxColumn(
            options=["Pending", "Partial", "Received"], required=True
        ),
        "Balance Payment": st.column_config.SelectboxColumn(
            options=["Pending", "Received"], required=True
        ),
        "Customs Declaration": st.column_config.SelectboxColumn(
            options=["Missing", "Received"], required=True
        ),
        "Factory VAT Receipt": st.column_config.SelectboxColumn(
            options=["Missing", "Pending", "Received"], required=True
        ),
        "Tax Refund Status": st.column_config.SelectboxColumn(
            options=["Not Applied", "Pending Filing", "Filed", "Completed"],
            required=True,
        ),
        "Total PO Amount ($)": st.column_config.NumberColumn(format="$%.2f"),
        "Deposit Received ($)": st.column_config.NumberColumn(format="$%.2f"),
    },
    use_container_width=True,
    key="master_editor",
)

if not edited_df.equals(df):
    st.session_state.order_df.update(edited_df)
    save_data(st.session_state.order_df)
    st.toast("💾 Changes auto-saved!")

st.markdown("---")

csv_data = st.session_state.order_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 Download Master Order Ledger (CSV / Excel)",
    data=csv_data,
    file_name="LION_INDUSTRY_Underwear_Orders.csv",
    mime="text/csv",
)
