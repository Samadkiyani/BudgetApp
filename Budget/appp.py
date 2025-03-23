import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore
import streamlit as st
import os
import uuid
import hashlib

# Display Banner Image
st.image(
    "https://media.istockphoto.com/id/1488294044/photo/businessman-works-on-laptop-showing-business-analytics-dashboard-with-charts-metrics-and-kpi.jpg?s=612x612&w=0&k=20&c=AcxzQAe1LY4lGp0C6EQ6reI7ZkFC2ftS09yw_3BVkpk=",
    use_column_width=True
)

# File Paths
user_data_file = "users.csv"
data_file = "budget_data.csv"

# Function to Hash Passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to Load Users
def load_users():
    if os.path.exists(user_data_file) and os.stat(user_data_file).st_size > 0:
        return pd.read_csv(user_data_file)
    else:
        return pd.DataFrame(columns=["Username", "Password", "Customer ID"])

# Function to Save Users
def save_users(df):
    df.to_csv(user_data_file, index=False)

# Function to Load Transaction Data
def load_data():
    if os.path.exists(data_file) and os.stat(data_file).st_size > 0:
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])

# Function to Save Transaction Data
def save_data(df):
    df.to_csv(data_file, index=False)

# Load Users & Transactions
data = load_data()
users = load_users()

# App Title
st.title("💰 Welcome to Samad Kiani Budget Dashboard")

# Authentication Handling
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.customer_id = ""

# Login / Signup Page
if not st.session_state.authenticated:
    option = st.sidebar.selectbox("Login / Signup", ["Login", "Signup"])

    if option == "Signup":
        new_username = st.sidebar.text_input("Choose a Username")
        new_password = st.sidebar.text_input("Choose a Password", type="password")
        
        if st.sidebar.button("Sign Up"):
            if new_username in users["Username"].values:
                st.sidebar.error("Username already exists! Choose another.")
            else:
                customer_id = str(uuid.uuid4())[:8]
                new_user = pd.DataFrame([[new_username, hash_password(new_password), customer_id]], 
                                        columns=["Username", "Password", "Customer ID"])
                users = pd.concat([users, new_user], ignore_index=True)
                save_users(users)
                st.sidebar.success("Signup successful! Please log in.")

    if option == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            user = users[(users["Username"] == username) & (users["Password"] == hash_password(password))]
            if not user.empty:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.customer_id = user.iloc[0]["Customer ID"]
                st.sidebar.success("Login successful!")
                st.experimental_rerun()
            else:
                st.sidebar.error("Invalid username or password.")

# If Logged In, Show Dashboard
if st.session_state.authenticated:
    st.sidebar.write(f"Logged in as: {st.session_state.username}")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.customer_id = ""
        st.experimental_rerun()

    # Add a New Transaction
    st.sidebar.header("Add a New Transaction")
    date = st.sidebar.date_input("Date")
    category = st.sidebar.selectbox("Category", ["Salary", "Groceries", "Bills", "Entertainment", "Transport", "Other"])
    amount = st.sidebar.slider("Amount", min_value=0, max_value=10000, step=10)
    transaction_type = st.sidebar.radio("Type", ("Income", "Expense"))

    if st.sidebar.button("Add Transaction"):
        new_data = pd.DataFrame([[st.session_state.customer_id, date, st.session_state.username, category, amount, transaction_type]],
                                columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)
        st.sidebar.success("Transaction added successfully!")

    # Delete Transactions
    st.sidebar.header("Delete Transactions")
    if st.sidebar.button("Delete My Transactions"):
        data = data[data["ID"] != st.session_state.customer_id]
        save_data(data)
        st.sidebar.success("All your transactions deleted successfully!")

    # Display Transaction History
    st.subheader("Transaction History")
    user_data = data[data["ID"] == st.session_state.customer_id]
    st.dataframe(user_data)

    # Financial Summary
    total_income = user_data[user_data["Type"] == "Income"]["Amount"].sum()
    total_expense = user_data[user_data["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.subheader("Summary")
    st.write(f"**Total Income:** ${total_income:.2f}")
    st.write(f"**Total Expense:** ${total_expense:.2f}")
    st.write(f"**Balance:** ${balance:.2f}")

    # Expense Breakdown by Category
    st.subheader("Expense Breakdown by Category")
    expense_data = user_data[user_data["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()

    if not expense_data.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=expense_data, x="Category", y="Amount", palette="pastel", ax=ax)
        ax.set_ylabel("Amount ($)")
        ax.set_title("Expense Breakdown by Category")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Income vs. Expense Trend
    st.subheader("Income vs. Expense Trend")
    user_data["Date"] = pd.to_datetime(user_data["Date"], errors='coerce')
    user_data = user_data.dropna(subset=["Date"])
    user_data["Month"] = user_data["Date"].dt.strftime('%Y-%m')
    customer_groups = user_data.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)

    if not customer_groups.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        customer_groups.plot(kind='bar', stacked=True, ax=ax, color=["#1f77b4", "#ff7f0e"])
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount ($)")
        ax.set_title("Income vs. Expense Trend")
        st.pyplot(fig)

    # Download Transactions
    st.sidebar.subheader("Download Data")
    st.sidebar.download_button(
        label="Download CSV",
        data=user_data.to_csv(index=False),
        file_name="budget_data.csv",
        mime="text/csv"
    )
