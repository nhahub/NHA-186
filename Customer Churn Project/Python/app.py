import streamlit as st
import joblib
import pandas as pd

model = joblib.load("rf_model_compressed.pkl")

st.title("Customer Retention Prediction App")
st.write("Enter customer details below to predict if they will stay or leave the company 👇")

age = st.number_input("Age", min_value=0, max_value=100, value=30)
tenure = st.number_input("Tenure (days with company)", min_value=0, value=365)
usage_frequency = st.number_input("Usage Frequency", min_value=0, value=10)
support_calls = st.number_input("Number of Support Calls", min_value=0, value=2)
payment_delay = st.number_input("Payment Delay (days)", min_value=0, value=3)

subscription_type = st.selectbox(
    "Subscription Type",
    ["Basic", "Standard", "Premium"]
)

contract_length = st.selectbox(
    "Contract Length",
    ["Annual", "Monthly", "Quarterly"]
)

total_spend = st.number_input("Total Spend ($)", min_value=0.0, value=500.0)
last_interaction = st.number_input("Days Since Last Interaction", min_value=0, value=10)

input_data = pd.DataFrame({
    "age": [age],
    "tenure": [tenure],
    "usage_frequency": [usage_frequency],
    "support_calls": [support_calls],
    "payment_delay": [payment_delay],
    "subscription_type": [subscription_type],
    "contract_length": [contract_length],
    "total_spend": [total_spend],
    "last_interaction": [last_interaction]
})

if st.button("🔍 Predict"):
    prediction = model.predict(input_data)[0]

    if prediction == 1:
        st.error("🚨 The customer WILL LEAVE the company.")
    else:
        st.success("✅ The customer WILL STAY with the company.")
