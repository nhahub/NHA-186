import streamlit as st
import joblib
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

# Load the trained pipeline model
model = joblib.load("rf_model_compressed.pkl")

st.title("Batch Customer Churn Prediction App")
st.write("Upload a CSV file with customer data to predict if they will stay or leave the company.")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV
    df = pd.read_csv(uploaded_file)
    st.write("File uploaded successfully. Here’s a preview:")
    st.dataframe(df.head())

    # Normalize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Required columns
    required_columns = [
        "age", "tenure", "usage_frequency", "support_calls",
        "payment_delay", "subscription_type", "contract_length",
        "total_spend", "last_interaction"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
    else:
        if st.button("🔍 Predict for all customers"):
            # Make predictions
            preds = model.predict(df)
            df["prediction"] = ["WILL LEAVE" if p == 1 else "WILL STAY" for p in preds]

            st.success("Predictions completed successfully!")
            st.dataframe(df.head())

            st.subheader("Prediction Summary")
            summary = df["prediction"].value_counts()

            fig, ax = plt.subplots()
            ax.pie(
                summary,
                labels=summary.index,
                autopct="%1.1f%%",
                startangle=90,
                colors=["#4CAF50","#FF6B6B"]
            )
            ax.axis("equal")  
            st.pyplot(fig)

            # Download predicted CSV
            output = BytesIO()
            df.to_csv(output, index=False)
            processed_data = output.getvalue()

            st.download_button(
                label="Download Predicted CSV",
                data=processed_data,
                file_name="predicted_customers.csv",
                mime="text/csv"
            )
