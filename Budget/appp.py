import streamlit as st
import pandas as pd
import os
import hashlib
import uuid
import matplotlib.pyplot as plt
import seaborn as sns

# Image Upload Function
def save_uploaded_file(uploaded_file):
    with open(os.path.join("images", uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return os.path.join("images", uploaded_file.name)

data_file = "users.csv"
budget_file = "budget_data.csv"

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to load user data
def load_users():
    if os.path.exists(data_file) and os.stat(data_file).st_size > 0:
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["Username", "Password"])

# Function to save user data
def save_users(df):
    df.to_csv(data_file, index=False)

# Load users
data = load_users()

st.title("🔐 Welcome to Samad Kiani Budget Dashboard")

# Check authentication status
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""

if not st.session_state["authenticated"]:
    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])
    
    if menu == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up"):
            if new_password == confirm_password:
                if new_username in data["Username"].values:
                    st.error("Username already exists. Please choose a different one.")
                else:
                    hashed_pw = hash_password(new_password)
                    new_user = pd.DataFrame([[new_username, hashed_pw]], columns=["Username", "Password"])
                    data = pd.concat([data, new_user], ignore_index=True)
                    save_users(data)
                    st.success("Account created successfully! You can now log in.")
            else:
                st.error("Passwords do not match. Please try again.")
    
    if menu == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            hashed_pw = hash_password(password)
            user = data[(data["Username"] == username) & (data["Password"] == hashed_pw)]
            if not user.empty:
                st.success(f"Welcome, {username}!")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password. Please try again.")
else:
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.experimental_rerun()
    
    st.title("💰 Budget Dashboard")
    
    def load_budget_data():
        if os.path.exists(budget_file) and os.stat(budget_file).st_size > 0:
            return pd.read_csv(budget_file)
        else:
            return pd.DataFrame(columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])

    def save_budget_data(df):
        df.to_csv(budget_file, index=False)

    data = load_budget_data()

    st.sidebar.header("Add a New Transaction")
    date = st.sidebar.date_input("Date")
    customer = st.session_state["username"]
    category = st.sidebar.selectbox("Category", ["Salary", "Groceries", "Bills", "Entertainment", "Transport", "Other"])
    amount = st.sidebar.slider("Amount", min_value=0, max_value=10000, step=10)
    transaction_type = st.sidebar.radio("Type", ("Income", "Expense"))
    
    uploaded_file = st.sidebar.file_uploader("Upload Image (Optional)", type=["png", "jpg", "jpeg"])
    image_path = ""
    if uploaded_file:
        image_path = save_uploaded_file(uploaded_file)
    
    if st.sidebar.button("Add Transaction"):
        customer_id = str(uuid.uuid4())[:8]  # Generate a unique ID for each transaction
        new_data = pd.DataFrame([[customer_id, date, customer, category, amount, transaction_type]], columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])
        data = pd.concat([data, new_data], ignore_index=True)
        save_budget_data(data)
        st.sidebar.success("Transaction added successfully!")
    
    st.subheader("Transaction History")
    st.dataframe(data)
    
    st.sidebar.subheader("Delete Transaction")
    delete_id = st.sidebar.text_input("Enter Transaction ID to Delete")
    if st.sidebar.button("Delete Transaction"):
        data = data[data["ID"] != delete_id]
        save_budget_data(data)
        st.sidebar.success("Transaction deleted successfully!")
        st.experimental_rerun()

    total_income = data[data["Type"] == "Income"]["Amount"].sum()
    total_expense = data[data["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.subheader("Summary")
    st.write(f"**Total Income:** ${total_income:.2f}")
    st.write(f"**Total Expense:** ${total_expense:.2f}")
    st.write(f"**Balance:** ${balance:.2f}")

    st.subheader("Expense Breakdown by Category")
    expense_data = data[data["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
    if not expense_data.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=expense_data, x="Category", y="Amount", palette="pastel", ax=ax)
        ax.set_ylabel("Amount ($)")
        ax.set_title("Expense Breakdown by Category")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.sidebar.subheader("Download Data")
    st.sidebar.download_button(
        label="Download CSV",
        data=data.to_csv(index=False),
        file_name="budget_data.csv",
        mime="text/csv"
    )
