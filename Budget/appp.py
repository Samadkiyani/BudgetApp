import streamlit as st
import pandas as pd
import hashlib
import os
import uuid

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

# Load Users
users = load_users()

# App Title
st.title("💰 Budget Dashboard")

# Authentication Handling
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.customer_id = ""

# Show only Login/Signup initially
if not st.session_state.authenticated:
    option = st.radio("Login or Signup", ["Login", "Signup"])

    if option == "Signup":
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        
        if st.button("Sign Up"):
            if new_username in users["Username"].values:
                st.error("Username already exists! Choose another.")
            else:
                customer_id = str(uuid.uuid4())[:8]
                new_user = pd.DataFrame([[new_username, hash_password(new_password), customer_id]], 
                                        columns=["Username", "Password", "Customer ID"])
                users = pd.concat([users, new_user], ignore_index=True)
                save_users(users)
                st.success("Signup successful! Please log in.")

    if option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user = users[(users["Username"] == username) & (users["Password"] == hash_password(password))]
            if not user.empty:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.customer_id = user.iloc[0]["Customer ID"]
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

# Show Dashboard **only after login**
if st.session_state.authenticated:
    st.image(
        "https://media.istockphoto.com/id/1488294044/photo/businessman-works-on-laptop-showing-business-analytics-dashboard-with-charts-metrics-and-kpi.jpg?s=612x612&w=0&k=20&c=AcxzQAe1LY4lGp0C6EQ6reI7ZkFC2ftS09yw_3BVkpk=",
        use_container_width=True
    )
    st.subheader(f"Welcome, {st.session_state.username}!")

    # Sample Budget Input Form
    st.write("### Enter Your Monthly Budget")
    income = st.number_input("Income", min_value=0, value=5000, step=100)
    expenses = st.number_input("Expenses", min_value=0, value=2000, step=100)
    savings = st.number_input("Savings", min_value=0, value=1000, step=100)
    
    if st.button("Save Budget"):
        if not os.path.exists(data_file):
            df = pd.DataFrame(columns=["Customer ID", "Income", "Expenses", "Savings"])
        else:
            df = pd.read_csv(data_file)
        
        new_data = pd.DataFrame([[st.session_state.customer_id, income, expenses, savings]], 
                                columns=["Customer ID", "Income", "Expenses", "Savings"])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(data_file, index=False)
        st.success("Budget saved successfully!")

    # Logout Button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.customer_id = ""
        st.experimental_rerun()
