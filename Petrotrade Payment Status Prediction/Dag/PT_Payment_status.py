from datetime import datetime, timedelta
import pandas as pd
import joblib
import io

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

TEST_CSV_PATH = "/opt/airflow/data/test.csv"
MODEL_PATH = "/opt/airflow/data/pt_rf_model.pkl"
POSTGRES_CONN_ID = "postgres_PT"
TARGET_TABLE = "PT_payment_status"
SCHEMA = "public"


def get_expected_features(m):
    if hasattr(m, "feature_names_in_"):
        return list(m.feature_names_in_)
    return None


def task_read_and_preprocess(**context):
    df = pd.read_csv(TEST_CSV_PATH)

    if "contract_date" in df.columns:
        df["contract_date"] = pd.to_datetime(df["contract_date"], dayfirst=True, errors="coerce")
    if "invoice_payment_date" in df.columns:
        df["invoice_payment_date"] = pd.to_datetime(df["invoice_payment_date"], dayfirst=True, errors="coerce")

    today = pd.Timestamp.now().normalize()
    df["contract_age_days"] = (today - df["contract_date"]).dt.days if "contract_date" in df.columns else -1
    df["invoice_age_days"] = (today - df["invoice_payment_date"]).dt.days if "invoice_payment_date" in df.columns else -1

    feature_cols = [
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

    for c in feature_cols:
        if c not in df.columns:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    context["ti"].xcom_push(key="df_csv", value=df.to_csv(index=False))


def task_predict(**context):
    df_csv = context["ti"].xcom_pull(key="df_csv")
    df = pd.read_csv(io.StringIO(df_csv))

    model = joblib.load(MODEL_PATH)

    feature_cols = [
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

    X = df[feature_cols].copy()

    expected = get_expected_features(model)
    if expected is not None:
        X = X.reindex(columns=expected, fill_value=0)

    preds = model.predict(X)
    df["prediction"] = preds.astype(int)
    df["label"] = df["prediction"].apply(lambda x: "Will Pay" if x == 1 else "Might Not Pay")

    context["ti"].xcom_push(key="predicted_csv", value=df.to_csv(index=False))


def task_write_postgres(**context):
    df_csv = context["ti"].xcom_pull(key="predicted_csv")
    df = pd.read_csv(io.StringIO(df_csv))

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    engine = hook.get_sqlalchemy_engine()

    df.to_sql(TARGET_TABLE, engine, schema=SCHEMA, if_exists="append", index=False)


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

with DAG(
    dag_id="pt_payment_prediction",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
) as dag:

    t1 = PythonOperator(
        task_id="read_and_preprocess",
        python_callable=task_read_and_preprocess,
        provide_context=True
    )

    t2 = PythonOperator(
        task_id="predict",
        python_callable=task_predict,
        provide_context=True
    )

    t3 = PythonOperator(
        task_id="write_to_postgres",
        python_callable=task_write_postgres,
        provide_context=True
    )

    t1 >> t2 >> t3
