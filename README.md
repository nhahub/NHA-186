Project 1 — Petrotrade Customer Payment Prediction
(Based on PetroTrade dataset — Power BI dashboard included)

1. Data Source
-Internal Petrotrade customer and payment records.
-Structured dataset containing: contracts, invoices, activity logs, payment history.

2. Data Loading (PostgreSQL)
-Imported raw Petrotrade dataset into PostgreSQL.
-Applied SQL cleaning + formatting + NULL handling.
-Created feature views used directly by Python.
-Ensured consistent schema for all pipeline stages.

3. Feature Engineering (SQL)
-Created training tables via SQL.
-Handled dates, missing values, and formatting.
-Extracted time-based features (contract_age_days, invoice_age_days).



4. Python Processing
-Connected to PostgreSQL using Python.
-Applied full cleaning pipeline:
-Fix date formats
-Drop invalid entries
-Remove duplicates
-Handle outliers
-Prepared data for model training.

5. Model Training
-Train–test split with SMOTE for balancing.
-GridSearchCV for hyperparameter tuning.
-Final model: Random Forest with high performance.

6. Streamlit Apps
-Single-customer prediction app.
-Batch CSV prediction app for bulk scoring.

7. Airflow Automation
-Pipeline performs:
-Fetches data from API.
-Converts to CSV.
-Performs cleaning + feature selection.
-Sends data to trained model.
-Stores predictions back into PostgreSQL (automated table refresh).

8. Reporting (Power BI)
-Connected live to PostgreSQL.
-Built interactive dashboard showing:
-Customer payment behavior
-Churn indicators
-Risk segmentation

Includes bookmarks & dynamic slicers.
Petrotrade Dashboard
https://app.powerbi.com/view?r=eyJrIjoiZTgyZjMxYWItN2UyNi00ZjBkLWFhMTMtYWZiZjg1YTY5OGY4IiwidCI6ImMyNzgwNjc3LTcyYTQtNGNmZC05ZGQ4LWJlZWE1ZjgwNTQyMyJ9

========================================================================================================================================================
========================================================================================================================================================
========================================================================================================================================================

Project 2 — Kaggle Customer Churn Prediction
(Based on Kaggle churn dataset — Power BI + Tableau dashboards)

1. Data Source
-Public Kaggle churn dataset.
-Downloaded dataset, extracted, and stored in PostgreSQL.

2. Data Loading (PostgreSQL)
-Loaded CSV into PostgreSQL.
-Cleaned columns & types.
-Standardized schema to match Petrotrade pipeline structure.

3. Feature Engineering (SQL)
-Selected essential features for churn modeling.
-Created SQL views for model-ready data.

4. Python Processing
-Cleaned inconsistent formats.
-Encoded categorical fields.
-Addressed missing values.
-Standard preprocessing pipeline ready for ML.

5. Model Training
-Random Forest tuned with GridSearchCV.
-Reached 93% accuracy.
-Used categorical preprocessing pipelines.

6. Streamlit Apps
-Single-customer app.
-Batch prediction CSV app.

7. Airflow Automation
-Same pipeline used in Petrotrade:
-Fetches new data via API.
-Cleans + prepares data.
-Predicts using trained model.
-Pushes predictions into PostgreSQL.

8. Reporting (Power BI & Tableau)

🔹 Kaggle Power BI Dashboard
https://app.powerbi.com/view?r=eyJrIjoiZGFiMmYxMjQtNzNhMC00YTQ4LTk1OTktNmI4ZGZmMTljYTljIiwidCI6ImMyNzgwNjc3LTcyYTQtNGNmZC05ZGQ4LWJlZWE1ZjgwNTQyMyJ9

🔹 Kaggle Tableau Dashboard
https://public.tableau.com/app/profile/marina.attala/viz/shared/YZBDTQ84R

Dashboard shows:
Usage patterns
Prediction comparison
Churn probability segmentation

========================================================================================================================================================
========================================================================================================================================================
========================================================================================================================================================

Common Workflow Between Both Projects
Both pipelines share the same tech stack:

Storage
PostgreSQL (raw → cleaned → model-ready → predictions)

Data Preparation
-SQL feature engineering
-Python cleaning
-Outlier handling
-Preprocessing pipelines

Model Training
-Random Forest
-GridSearchCV
-SMOTE balancing
-Evaluation with precision/recall/F1

Deployment & Apps
-Streamlit single + batch
-FastAPI/Flask prediction endpoints

Automation (Airflow)
-Fetch data
-Clean
-Feature select
-Predict
-Load to database

Reporting
-Power BI
-Tableau
-Live connection to PostgreSQL
