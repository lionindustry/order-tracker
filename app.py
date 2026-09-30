import os
import pandas as pd
import streamlit as st

DATA_FILE = "order_data.csv"

st.set_page_config(
    page_title="Order & Financial Management System",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Order & Financial Management System")
st.caption(
    "Automated tracking for Orders, Advance Payments, Balance Payments, Shipments, Invoicing, and Tax Refunds with built-in risk warnings."
)

# Status Dropdown Options
STATUS_ORDER = [
    "Pending Confirmation",
    "Confirmed",
    "In Production",
    "Completed",
    "Cancelled",
]
STATUS_ADVANCE = ["Unpaid", "Partially Paid", "Fully Paid"]
STATUS_BALANCE = ["Not Due", "Overdue / Follow-up", "Partially Paid", "Fully Paid"]
STATUS_SHIPMENT = [
    "Unshipped",
    "Partially Shipped",
    "Customs Cleared",
    "Delivered",
]
STATUS_PAYMENT = [
    "Unsettled",
    "Advance Received",
    "Balance Pending",
    "Fully Settled",
]
STATUS_INVOICE = [
    "Uninvoiced",
    "VAT Invoice Issued",
    "Invoice Sent",
    "Input Tax Received",
]
STATUS_TAX_REFUND = [
    "N/A",
    "Pending Filing",
    "Filing in Progress",
    "Refund Received",
]

# Default Initial Data
DEFAULT_DATA = [
    {
        "Order ID": "PO20260901",
        "Client/Supplier": "Client A",
        "Order Status": "In Production",
        "Advance Status": "Fully Paid",
        "Balance Status": "Not Due",
        "Shipment Status": "Unshipped",
        "Payment Status": "Advance Received",
        "Invoice Status": "Uninvoiced",
        "Tax Refund Status": "Pending Filing",
        "Total Amount ($)": 50000.0,
        "Received Amount ($)": 15000.0,
        "Notes": "Expected shipment next month",
    },
    {
        "Order ID": "PO20260815",
        "Client/Supplier": "Client B",
        "Order Status": "Completed",
        "Advance Status": "Fully Paid",
        "Balance Status": "Overdue / Follow-up",
        "Shipment Status": "Customs Cleared",
        "Payment Status": "Balance Pending",
        "Invoice Status": "Uninvoiced",  # Anomaly: Shipped but Uninvoiced
        "Tax Refund Status": "Pending Filing",  # Anomaly: Shipped but Pending Refund
        "Total Amount ($)": 120000.0,
        "Received Amount ($)": 36000.0,  # Anomaly: Shipped but Balance Unpaid
        "Notes": "Bill of Lading sent, urgent follow-up required",
    },
]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
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

# ================= Sidebar: Data Import & Single Entry =================
with st.sidebar:
    st.header("📂 Data Management & Entry")

    st.subheader("Batch Import")
    uploaded_file = st.file_uploader(
        "Upload Excel or CSV File", type=["csv", "xlsx"]
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                new_df = pd.read_csv(uploaded_file)
            else:
                new_df = pd.read_excel(uploaded_file)

            import_option = st.radio(
                "Import Mode", ["Overwrite Current Ledger", "Append to Ledger"]
            )
            if st.button("Confirm Import"):
                if import_option == "Overwrite Current Ledger":
                    st.session_state.order_df = new_df
                else:
                    st.session_state.order_df = pd.concat(
                        [st.session_state.order_df, new_df], ignore_index=True
                    )
                save_data(st.session_state.order_df)
                st.success("Data imported successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Error parsing file: {e}")

    st.markdown("---")

    st.subheader("➕ Add Single Order")
    with st.form("new_order_form", clear_on_submit=True):
        po_num = st.text_input("Order ID", value="PO2026001")
        client = st.text_input("Client / Supplier", value="")
        order_st = st.selectbox("Order Status", STATUS_ORDER)
        adv_st = st.selectbox("Advance Status", STATUS_ADVANCE)
        bal_st = st.selectbox("Balance Status", STATUS_BALANCE)
        ship_st = st.selectbox("Shipment Status", STATUS_SHIPMENT)
        pay_st = st.selectbox("Payment Status", STATUS_PAYMENT)
        inv_st = st.selectbox("Invoice Status", STATUS_INVOICE)
        tax_st = st.selectbox("Tax Refund Status", STATUS_TAX_REFUND)
        total_amt = st.number_input(
            "Total Amount ($)", min_value=0.0, value=0.0, step=1000.0
        )
        paid_amt = st.number_input(
            "Received Amount ($)", min_value=0.0, value=0.0, step=1000.0
        )
        notes = st.text_area("Notes", value="")

        submitted = st.form_submit_button("Save Order")
        if submitted:
            new_row = {
                "Order ID": po_num,
                "Client/Supplier": client,
                "Order Status": order_st,
                "Advance Status": adv_st,
                "Balance Status": bal_st,
                "Shipment Status": ship_st,
                "Payment Status": pay_st,
                "Invoice Status": inv_st,
                "Tax Refund Status": tax_st,
                "Total Amount ($)": total_amt,
                "Received Amount ($)": paid_amt,
                "Notes": notes,
            }
            st.session_state.order_df = pd.concat(
                [st.session_state.order_df, pd.DataFrame([new_row])],
                ignore_index=True,
            )
            save_data(st.session_state.order_df)
            st.success(f"Order {po_num} added successfully!")
            st.rerun()

# ================= Anomaly Detection Engine =================
df = st.session_state.order_df

# Anomaly 1: Shipped/Delivered but Balance not fully paid
anomaly_unpaid = df[
    df["Shipment Status"].isin(["Customs Cleared", "Delivered"])
    & (df["Balance Status"] != "Fully Paid")
]

# Anomaly 2: Shipped but Uninvoiced
anomaly_uninvoiced = df[
    df["Shipment Status"].isin(["Customs Cleared", "Delivered"])
    & (df["Invoice Status"] == "Uninvoiced")
]

# Anomaly 3: Shipped but Tax Refund Pending
anomaly_untaxed = df[
    df["Shipment Status"].isin(["Customs Cleared", "Delivered"])
    & df["Tax Refund Status"].isin(["Pending Filing"])
]

# Metrics Calculation
total_orders_val = df["Total Amount ($)"].sum()
total_received_val = df["Received Amount ($)"].sum()
total_pending_val = total_orders_val - total_received_val

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", f"{len(df)}")
col2.metric("Total Order Value", f"${total_orders_val:,.2f}")
col3.metric("Total Received", f"${total_received_val:,.2f}")
col4.metric(
    "Pending Balance / Gap",
    f"${total_pending_val:,.2f}",
    delta=f"-${total_pending_val:,.2f}" if total_pending_val > 0 else "Settled",
)

st.markdown("---")

# Risk Warning Dashboard
st.subheader("🚨 Automated Reconciliation Risk Dashboard")
num_anomalies = (
    len(anomaly_unpaid) + len(anomaly_uninvoiced) + len(anomaly_untaxed)
)

if num_anomalies == 0:
    st.success("✅ No status mismatches or financial delays detected.")
else:
    st.warning(f"⚠️ **{num_anomalies} process alignment risk(s)** detected:")
    a_tab1, a_tab2, a_tab3 = st.tabs([
        f"🔴 Shipped - Unpaid Balance ({len(anomaly_unpaid)})",
        f"🟡 Shipped - Uninvoiced ({len(anomaly_uninvoiced)})",
        f"🔵 Shipped - Tax Refund Pending ({len(anomaly_untaxed)})",
    ])

    with a_tab1:
        if not anomaly_unpaid.empty:
            st.error("Orders shipped/delivered but balance is NOT fully paid:")
            st.dataframe(
                anomaly_unpaid[
                    [
                        "Order ID",
                        "Client/Supplier",
                        "Shipment Status",
                        "Balance Status",
                        "Total Amount ($)",
                        "Received Amount ($)",
                        "Notes",
                    ]
                ],
                use_container_width=True,
            )
        else:
            st.info("No issues.")

    with a_tab2:
        if not anomaly_uninvoiced.empty:
            st.warning("Orders shipped but invoice has NOT been issued:")
            st.dataframe(
                anomaly_uninvoiced[
                    [
                        "Order ID",
                        "Client/Supplier",
                        "Shipment Status",
                        "Invoice Status",
                        "Notes",
                    ]
                ],
                use_container_width=True,
            )
        else:
            st.info("No issues.")

    with a_tab3:
        if not anomaly_untaxed.empty:
            st.info("Orders shipped requiring tax refund filing:")
            st.dataframe(
                anomaly_untaxed[
                    [
                        "Order ID",
                        "Client/Supplier",
                        "Shipment Status",
                        "Tax Refund Status",
                        "Notes",
                    ]
                ],
                use_container_width=True,
            )
        else:
            st.info("No issues.")

st.markdown("---")

# Interactive Data Table
st.subheader("🔍 Interactive Ledger (Double-click to Edit)")
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    filter_bal = st.multiselect("Filter Balance Status", options=STATUS_BALANCE)
with f_col2:
    filter_ship = st.multiselect(
        "Filter Shipment Status", options=STATUS_SHIPMENT
    )
with f_col3:
    filter_tax = st.multiselect(
        "Filter Tax Refund Status", options=STATUS_TAX_REFUND
    )

filtered_df = df.copy()
if filter_bal:
    filtered_df = filtered_df[filtered_df["Balance Status"].isin(filter_bal)]
if filter_ship:
    filtered_df = filtered_df[filtered_df["Shipment Status"].isin(filter_ship)]
if filter_tax:
    filtered_df = filtered_df[filtered_df["Tax Refund Status"].isin(filter_tax)]

edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    column_config={
        "Order Status": st.column_config.SelectboxColumn(
            options=STATUS_ORDER, required=True
        ),
        "Advance Status": st.column_config.SelectboxColumn(
            options=STATUS_ADVANCE, required=True
        ),
        "Balance Status": st.column_config.SelectboxColumn(
            options=STATUS_BALANCE, required=True
        ),
        "Shipment Status": st.column_config.SelectboxColumn(
            options=STATUS_SHIPMENT, required=True
        ),
        "Payment Status": st.column_config.SelectboxColumn(
            options=STATUS_PAYMENT, required=True
        ),
        "Invoice Status": st.column_config.SelectboxColumn(
            options=STATUS_INVOICE, required=True
        ),
        "Tax Refund Status": st.column_config.SelectboxColumn(
            options=STATUS_TAX_REFUND, required=True
        ),
        "Total Amount ($)": st.column_config.NumberColumn(format="$%.2f"),
        "Received Amount ($)": st.column_config.NumberColumn(format="$%.2f"),
    },
    use_container_width=True,
    key="editor",
)

if not edited_df.equals(filtered_df):
    st.session_state.order_df.update(edited_df)
    save_data(st.session_state.order_df)
    st.toast("💾 Changes auto-saved!")

st.markdown("---")
csv_data = st.session_state.order_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 Export Full Ledger (CSV / Excel)",
    data=csv_data,
    file_name="order_financial_ledger.csv",
    mime="text/csv",
)
