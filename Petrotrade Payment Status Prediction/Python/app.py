import streamlit as st
import pandas as pd
import joblib
import datetime

model = joblib.load("rf_model.pkl")

st.title("💳 Customer Payment Prediction App")
st.write("Predict whether a customer will pay or not based on contract data 👇")

contract_date = st.date_input("Contract Date")
invoice_payment_date = st.date_input("Invoice Payment Date")

consumption = st.number_input("Consumption", min_value=0.0, value=0.0)
installment_most_faw = st.number_input("Installment Most Faw", min_value=0, value=202407)
remaining_installments_faw = st.number_input("Remaining Installments Faw", min_value=0.0, value=0.0)
bank_installment = st.number_input("Bank Installment", min_value=0.0, value=0.0)
remaining_bank_installments = st.number_input("Remaining Bank Installments", min_value=0.0, value=0.0)
customer_type = st.number_input("Customer Type", min_value=0, value=0)
receipt = st.number_input("Receipt", min_value=0, value=0)

today = datetime.datetime.now()

contract_age_days = (today - datetime.datetime.combine(contract_date, datetime.datetime.min.time())).days
invoice_age_days = (today - datetime.datetime.combine(invoice_payment_date, datetime.datetime.min.time())).days

input_data = pd.DataFrame({
    'consumption': [consumption],
    'installment_most_faw': [installment_most_faw],
    'remaining_installments_faw': [remaining_installments_faw],
    'bank_installment': [bank_installment],
    'remaining_bank_installments': [remaining_bank_installments],
    'customer_type': [customer_type],
    'receipt': [receipt],
    'contract_age_days': [contract_age_days],
    'invoice_age_days': [invoice_age_days]
})

st.write("### 🧾 Input Data Preview")
st.dataframe(input_data)

if st.button("🔍 Predict Payment Status"):
    prediction = int(model.predict(input_data)[0])

    st.write(f"🔹 Model raw prediction value: {prediction}")

    if prediction == 1:
        st.success("✅ The customer **WILL PAY** successfully.")
    else:
        st.error("🚨 The customer **MIGHT NOT PAY**.")

