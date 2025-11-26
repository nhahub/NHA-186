import streamlit as st
import pandas as pd
import joblib
import datetime

st.set_page_config(page_title="Payment Prediction", layout="wide")
st.title("Payment Prediction — CSV Upload")

@st.cache_resource
def load_model(path="rf_model.pkl"):
    return joblib.load(path)

model = load_model("rf_model.pkl")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)
st.write("Input Preview")
st.dataframe(df.head(10))

if "contract_date" in df.columns:
    df["contract_date"] = pd.to_datetime(df["contract_date"], dayfirst=True, errors="coerce")
if "invoice_payment_date" in df.columns:
    df["invoice_payment_date"] = pd.to_datetime(df["invoice_payment_date"], dayfirst=True, errors="coerce")

today = pd.Timestamp.now().normalize()

df["contract_age_days"] = (today - df["contract_date"]).dt.days if "contract_date" in df.columns else -1
df["invoice_age_days"] = (today - df["invoice_payment_date"]).dt.days if "invoice_payment_date" in df.columns else -1

feature_cols_default = [
    "consumption",
    "installment_most_faw",
    "remaining_installments_faw",
    "bank_installment",
    "remaining_bank_installments",
    "customer_type",
    "total_financial_amount",
    "contract_age_days",
    "invoice_age_days"
]

missing = [c for c in feature_cols_default if c not in df.columns]
for c in missing:
    df[c] = 0

for c in feature_cols_default:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

X = df[feature_cols_default].copy()

id_col = df["C_ID"] if "C_ID" in df.columns else None

def get_expected_features(m):
    if hasattr(m, "named_steps"):
        steps = m.named_steps
        if hasattr(m, "feature_names_in_"):
            return list(m.feature_names_in_)
        for step in steps.values():
            if hasattr(step, "get_feature_names_out"):
                try:
                    return list(step.get_feature_names_out())
                except:
                    pass
    if hasattr(m, "feature_names_in_"):
        return list(m.feature_names_in_)
    return None

expected = get_expected_features(model)

if st.button("Predict"):
    if expected is not None:
        X_input = X.reindex(columns=expected, fill_value=0)
    else:
        X_input = X.copy()

    for col in X_input.columns:
        X_input[col] = pd.to_numeric(X_input[col], errors="coerce").fillna(0)

    preds = model.predict(X_input)

    df["prediction"] = preds.astype(int)
    df["label"] = df["prediction"].apply(lambda x: "Will Pay" if x == 1 else "Might Not Pay")

    if id_col is not None and "C_ID" not in df.columns:
        df.insert(0, "C_ID", id_col)

    st.write("Output")
    st.dataframe(df.head(20))

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="predictions.csv",
        mime="text/csv"
    )
