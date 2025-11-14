import os
import zipfile
import pandas as pd
import joblib
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

os.environ['KAGGLE_USERNAME'] = 'ahmed0elshafey0'
os.environ['KAGGLE_KEY'] = '3e662d52c4b9fcc84b873cb1efc46604'

DATA_DIR = "/opt/airflow/data"
os.makedirs(DATA_DIR, exist_ok=True)

def download_test_data():
    from kaggle.api.kaggle_api_extended import KaggleApi
    
    api = KaggleApi()
    api.authenticate()

    dataset_path = "muhammadshahidazeem/customer-churn-dataset"
    api.dataset_download_files(dataset_path, path=DATA_DIR, force=True, quiet=False)

    zip_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".zip")]
    if not zip_files:
        raise FileNotFoundError("No ZIP file found after Kaggle download!")

    zip_path = os.path.join(DATA_DIR, zip_files[0])
    print(f"Found ZIP file: {zip_path}")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    print("Dataset extracted successfully.")

    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError("No CSV file found after extraction!")
    
    print(f"Found CSV file: {csv_files[0]}")

def predict_data():
    csv_file = None
    for f in os.listdir(DATA_DIR):
        if f.endswith(".csv"):
            csv_file = os.path.join(DATA_DIR, f)
            break

    if not csv_file:
        raise FileNotFoundError("No CSV file found after extraction.")

    print(f"Reading data from {csv_file}")

    df = pd.read_csv(csv_file, encoding="latin1", on_bad_lines="skip")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    expected_cols = [
        "age", "tenure", "usage_frequency", "support_calls",
        "payment_delay", "subscription_type", "contract_length",
        "total_spend", "last_interaction"
    ]

    numeric_cols = ["age", "tenure", "usage_frequency", "support_calls",
                    "payment_delay", "total_spend"]

    for col in numeric_cols:
        if col not in df.columns:
            print(f"Column '{col}' missing in CSV. Filling with 0.")
            df[col] = 0

    model_file = os.path.join(DATA_DIR, "rf_model_compressed.pkl")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Model file not found at {model_file}")

    model = joblib.load(model_file)
    df["prediction"] = ["WILL LEAVE" if p == 1 else "WILL STAY" for p in model.predict(df[expected_cols])]
    
    output_path = os.path.join(DATA_DIR, "churn_predicted.csv")
    df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}")

def save_to_csv():
    input_file = os.path.join(DATA_DIR, "churn_predicted.csv")
    df = pd.read_csv(input_file)
    
    final_output_path = os.path.join(DATA_DIR, "final_churn_predictions.csv")
    df.to_csv(final_output_path, index=False)
    
    print(f"Final predictions saved to: {final_output_path}")
    print(f"Total records: {len(df)}")
    print(f"Predictions distribution:")
    print(df['prediction'].value_counts())
    
    print("\nSample of predictions:")
    print(df[['age', 'tenure', 'prediction']].head(10))

default_args = {
    "owner": "airflow", 
    "start_date": datetime(2025, 10, 30),
    "retries": 1,
}

dag = DAG(
    "customer_churn_save_csv", 
    default_args=default_args,
    description="Customer Churn Prediction Pipeline that saves to CSV",
    schedule_interval=None,
    catchup=False,
    tags=["churn", "prediction", "csv"]
)

task_download = PythonOperator(
    task_id="download_test_data",
    python_callable=download_test_data,
    dag=dag,
)

task_predict = PythonOperator(
    task_id="predict_data",
    python_callable=predict_data,
    dag=dag,
)

task_save = PythonOperator(
    task_id="save_to_csv",
    python_callable=save_to_csv,
    dag=dag,
)

# تعريف التبعيات
task_download >> task_predict >> task_save