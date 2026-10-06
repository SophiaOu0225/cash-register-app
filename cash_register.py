import os
from datetime import datetime, date

import streamlit as st


# The text file is stored in the same folder as this program.
PROGRAM_FOLDER = os.path.dirname(os.path.abspath(__file__))
TRANSACTION_FILE = os.path.join(PROGRAM_FOLDER, "transactions.txt")
FILE_HEADER = "date|time|sales|rendered|change|payment_type\n"


def create_transaction_file():
    """Create the text file and its heading when it does not exist."""
    if not os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, "w", encoding="utf-8") as file:
            file.write(FILE_HEADER)


def save_transaction(sales, rendered, change, payment_type):
    """Add one completed sale to the text file."""
    current_time = datetime.now()
    transaction_date = current_time.strftime("%Y-%m-%d")
    transaction_time = current_time.strftime("%H:%M:%S")

    line = transaction_date + "|" + transaction_time + "|"
    line += format(sales, ".2f") + "|" + format(rendered, ".2f") + "|"
    line += format(change, ".2f") + "|" + payment_type + "\n"

    with open(TRANSACTION_FILE, "a", encoding="utf-8") as file:
        file.write(line)


def load_transactions():
    """Read all valid transaction records from the text file."""
    transactions = []
    create_transaction_file()

    with open(TRANSACTION_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line_number in range(1, len(lines)):
        values = lines[line_number].strip().split("|")

        if len(values) == 6:
            try:
                transaction = {
                    "date": values[0],
                    "time": values[1],
                    "sales": float(values[2]),
                    "rendered": float(values[3]),
                    "change": float(values[4]),
                    "payment_type": values[5]
                }
                transactions.append(transaction)
            except ValueError:
                # Ignore an incomplete or damaged line and continue reading.
                pass

    return transactions


def get_daily_transactions(transactions, selected_date):
    """Return transactions recorded on one selected date."""
    daily_transactions = []

    for transaction in transactions:
        if transaction["date"] == selected_date:
            daily_transactions.append(transaction)

    return daily_transactions


def make_daily_table(daily_transactions):
    """Prepare readable rows for Streamlit's table."""
    table_rows = []

    for transaction in daily_transactions:
        row = {
            "Time": transaction["time"],
            "Sales (S$)": format(transaction["sales"], ".2f"),
            "Rendered (S$)": format(transaction["rendered"], ".2f"),
            "Change (S$)": format(transaction["change"], ".2f"),
            "Payment type": transaction["payment_type"]
        }
        table_rows.append(row)

    return table_rows


def get_monthly_summary(transactions, selected_year, selected_month):
    """Calculate the number of transactions and total sales for each day."""
    daily_totals = {}
    month_text = str(selected_year) + "-" + str(selected_month).zfill(2)

    for transaction in transactions:
        if transaction["date"].startswith(month_text):
            transaction_date = transaction["date"]

            if transaction_date not in daily_totals:
                daily_totals[transaction_date] = {
                    "count": 0,
                    "sales": 0.0
                }

            daily_totals[transaction_date]["count"] += 1
            daily_totals[transaction_date]["sales"] += transaction["sales"]

    summary_rows = []
    sorted_dates = sorted(daily_totals.keys())

    for transaction_date in sorted_dates:
        row = {
            "Date": transaction_date,
            "Transactions": daily_totals[transaction_date]["count"],
            "Total sales (S$)": format(
                daily_totals[transaction_date]["sales"], ".2f"
            )
        }
        summary_rows.append(row)

    return summary_rows


def get_payment_summary(transactions):
    """Calculate total sales for each payment type."""
    payment_totals = {}

    for transaction in transactions:
        payment_type = transaction["payment_type"]

        if payment_type not in payment_totals:
            payment_totals[payment_type] = 0.0

        payment_totals[payment_type] += transaction["sales"]

    summary_rows = []

    for payment_type in payment_totals:
        row = {
            "Payment type": payment_type,
            "Total sales (S$)": format(payment_totals[payment_type], ".2f")
        }
        summary_rows.append(row)

    return summary_rows


def make_csv_text(headers, rows):
    """Convert report rows into downloadable CSV text using strings."""
    csv_text = ",".join(headers) + "\n"

    for row in rows:
        values = []

        for header in headers:
            value = str(row[header]).replace('"', '""')
            values.append('"' + value + '"')

        csv_text += ",".join(values) + "\n"

    return csv_text


create_transaction_file()

st.set_page_config(
    page_title="Ah Beng Vegetarian Stall",
    page_icon="🥬",
    layout="wide"
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] .stButton > button {
        min-height: 68px;
        border-radius: 14px;
        padding: 10px 14px;
        font-size: 16px;
        font-weight: 600;
        text-align: left;
        justify-content: flex-start;
        margin-bottom: 5px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: #2e7d32;
        color: #2e7d32;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🥬 Ah Beng Vegetarian Stall")
st.caption("Simple cash register and sales reporting system")

if "page" not in st.session_state:
    st.session_state.page = "New transaction"

st.sidebar.title("Menu")

if st.sidebar.button(
    "🧾  New transaction",
    use_container_width=True,
    type="primary" if st.session_state.page == "New transaction" else "secondary"
):
    st.session_state.page = "New transaction"
    st.rerun()

if st.sidebar.button(
    "📅  Daily report",
    use_container_width=True,
    type="primary" if st.session_state.page == "Daily report" else "secondary"
):
    st.session_state.page = "Daily report"
    st.rerun()

if st.sidebar.button(
    "📊  Monthly report",
    use_container_width=True,
    type="primary" if st.session_state.page == "Monthly report" else "secondary"
):
    st.session_state.page = "Monthly report"
    st.rerun()

page = st.session_state.page


if page == "New transaction":
    st.header("New transaction")

    first_column, second_column = st.columns(2)

    with first_column:
        sales_input = st.text_input(
            "Sales amount (S$)",
            placeholder="0.00",
            key="sales_input"
        )

        payment_type = st.selectbox(
            "Payment type",
            ["Cash", "PayNow", "PayLah", "PayWave"]
        )

    with second_column:
        rendered_input = st.text_input(
            "Amount rendered (S$)",
            placeholder="0.00",
            key="rendered_input"
        )

    sales_amount = None
    amount_rendered = None
    input_error = ""

    try:
        if sales_input.strip() != "":
            sales_amount = float(sales_input)
        if rendered_input.strip() != "":
            amount_rendered = float(rendered_input)
    except ValueError:
        sales_amount = None
        amount_rendered = None
        input_error = "Please enter valid numbers only."

    if input_error == "":
        if sales_amount is not None and sales_amount < 0:
            input_error = "The sales amount must be greater than or equal to zero."
        elif amount_rendered is not None and amount_rendered < 0:
            input_error = "The amount rendered must be greater than or equal to zero."

    if input_error != "":
        st.error(input_error)

    if sales_amount is not None and amount_rendered is not None:
        if input_error == "":
            change_amount = amount_rendered - sales_amount

            if change_amount >= 0:
                st.metric("Change", "S$" + format(change_amount, ".2f"))
            else:
                shortage = 0 - change_amount
                st.metric("Amount short", "S$" + format(shortage, ".2f"))

    if st.button("Complete transaction"):
        if sales_input.strip() == "" or rendered_input.strip() == "":
            st.error("Please enter both the sales amount and amount rendered.")
        elif input_error != "":
            pass
        elif sales_amount == 0:
            st.error("Please enter a sales amount greater than zero.")
        elif amount_rendered < sales_amount:
            st.error("The amount rendered is not enough to complete the sale.")
        else:
            change_amount = round(amount_rendered - sales_amount, 2)
            save_transaction(
                sales_amount,
                amount_rendered,
                change_amount,
                payment_type
            )
            st.success(
                "Transaction saved. Change: S$" +
                format(change_amount, ".2f")
            )


elif page == "Daily report":
    st.header("Daily transaction report")

    report_date = st.date_input("Select a date", value=date.today())
    selected_date = report_date.strftime("%Y-%m-%d")

    all_transactions = load_transactions()
    daily_transactions = get_daily_transactions(
        all_transactions,
        selected_date
    )

    if len(daily_transactions) == 0:
        st.info("No transactions were recorded on this date.")
    else:
        total_sales = 0.0

        for transaction in daily_transactions:
            total_sales += transaction["sales"]

        first_metric, second_metric = st.columns(2)
        first_metric.metric("Transactions", len(daily_transactions))
        second_metric.metric("Total sales", "S$" + format(total_sales, ".2f"))

        st.table(make_daily_table(daily_transactions))

        daily_rows = make_daily_table(daily_transactions)
        daily_headers = [
            "Time",
            "Sales (S$)",
            "Rendered (S$)",
            "Change (S$)",
            "Payment type"
        ]
        daily_csv = make_csv_text(daily_headers, daily_rows)

        daily_payment_rows = get_payment_summary(daily_transactions)
        payment_headers = ["Payment type", "Total sales (S$)"]
        daily_payment_csv = make_csv_text(
            payment_headers,
            daily_payment_rows
        )

        st.subheader("Total sales amount by payment type by day")
        st.table(daily_payment_rows)

        first_download, second_download = st.columns(2)

        with first_download:
            st.download_button(
                "Download transaction listing",
                data=daily_csv,
                file_name="daily_transactions_" + selected_date + ".csv",
                mime="text/csv",
                use_container_width=True
            )

        with second_download:
            st.download_button(
                "Download payment summary",
                data=daily_payment_csv,
                file_name="daily_payment_summary_" + selected_date + ".csv",
                mime="text/csv",
                use_container_width=True
            )


elif page == "Monthly report":
    st.header("Monthly sales report")

    current_date = date.today()
    year_options = []

    for year in range(2020, 2101):
        year_options.append(year)

    month_options = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    first_column, second_column = st.columns(2)

    with first_column:
        selected_year = st.selectbox(
            "Year",
            year_options,
            index=year_options.index(current_date.year)
        )

    with second_column:
        selected_month_name = st.selectbox(
            "Month",
            month_options,
            index=current_date.month - 1
        )

    selected_month = month_options.index(selected_month_name) + 1
    st.caption(
        "Showing " + selected_month_name + " " + str(selected_year)
    )

    all_transactions = load_transactions()
    monthly_summary = get_monthly_summary(
        all_transactions,
        selected_year,
        selected_month
    )

    month_transactions = []
    selected_month_text = str(selected_year) + "-" + str(selected_month).zfill(2)

    for transaction in all_transactions:
        if transaction["date"].startswith(selected_month_text):
            month_transactions.append(transaction)

    if len(monthly_summary) == 0:
        st.info("No transactions were recorded in this month.")
    else:
        st.subheader("Sales summarised by day")
        st.table(monthly_summary)

        monthly_headers = ["Date", "Transactions", "Total sales (S$)"]
        monthly_csv = make_csv_text(monthly_headers, monthly_summary)
        month_file_text = str(selected_year) + "-" + str(selected_month).zfill(2)

        monthly_payment_rows = get_payment_summary(month_transactions)
        payment_headers = ["Payment type", "Total sales (S$)"]
        monthly_payment_csv = make_csv_text(
            payment_headers,
            monthly_payment_rows
        )

        st.subheader("Total sales amount by payment type by month")
        st.table(monthly_payment_rows)

        first_download, second_download = st.columns(2)

        with first_download:
            st.download_button(
                "Download daily sales summary",
                data=monthly_csv,
                file_name="monthly_daily_sales_" + month_file_text + ".csv",
                mime="text/csv",
                use_container_width=True
            )

        with second_download:
            st.download_button(
                "Download payment summary",
                data=monthly_payment_csv,
                file_name="monthly_payment_summary_" + month_file_text + ".csv",
                mime="text/csv",
                use_container_width=True
            )
