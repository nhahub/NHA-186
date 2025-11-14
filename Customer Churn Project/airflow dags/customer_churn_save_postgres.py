import os
import zipfile
import pandas as pd
import joblib
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime

# Environment setup
os.environ['KAGGLE_USERNAME'] = '************'
os.environ['KAGGLE_KEY'] = '*********************'

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

def save_to_postgres():
    hook = PostgresHook(postgres_conn_id="postgres_churn")
    
    file_path = os.path.join(DATA_DIR, "churn_predicted.csv")
    df = pd.read_csv(file_path)

    with hook.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS churn_results (
                    age INT,
                    tenure INT,
                    usage_frequency INT,
                    support_calls INT,
                    payment_delay INT,
                    subscription_type TEXT,
                    contract_length TEXT,
                    total_spend FLOAT,
                    last_interaction INT,
                    prediction TEXT
                )
            """)

            records = df[[
                "age", "tenure", "usage_frequency", "support_calls", "payment_delay",
                "subscription_type", "contract_length", "total_spend", "last_interaction", "prediction"
            ]].values.tolist()

            from psycopg2.extras import execute_values
            execute_values(cur,
                "INSERT INTO churn_results VALUES %s",
                records
            )

            conn.commit()
    
    print("Data saved to PostgreSQL.")

default_args = {
    "owner": "airflow", 
    "start_date": datetime(2025, 10, 30)
}

with DAG(
    "customer_churn_save_postgres",
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    task_download = PythonOperator(
        task_id="download_test_data",
        python_callable=download_test_data
    )

    task_predict = PythonOperator(
        task_id="predict_data",
        python_callable=predict_data
    )

    task_save = PythonOperator(
        task_id="save_to_postgres",
        python_callable=save_to_postgres
    )

    task_download >> task_predict >> task_save
