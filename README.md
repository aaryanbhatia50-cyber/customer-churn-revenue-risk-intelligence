# Customer Churn & Revenue Risk Intelligence

An end-to-end machine learning and business intelligence project focused on identifying customer churn risk, understanding customer behaviour, and supporting data-driven retention decisions.

The project combines Python, machine learning, SHAP explainability, PostgreSQL analytics, and an interactive Streamlit dashboard.

## Project Overview

Customer churn is an important business challenge because losing customers can affect long-term customer relationships and business performance.

This project analyses historical customer snapshots and transaction data to identify customers at risk of churning. It follows an end-to-end workflow covering data auditing, exploratory data analysis, feature engineering, machine learning, model evaluation, explainability, risk segmentation, SQL analysis, and dashboard development.

## Key Features

- **Data Analysis:** Customer and transaction data auditing and exploratory analysis.
- **Feature Engineering:** Behavioural and demographic feature preparation.
- **Churn Prediction:** Logistic Regression classification pipeline.
- **Model Evaluation:** Precision, recall, F1-score, ROC-AUC, PR-AUC, and confusion matrix.
- **Model Explainability:** Global feature importance analysis using SHAP.
- **Risk Intelligence:** Customer segmentation into Low, Medium, and High risk categories.
- **SQL Analytics:** PostgreSQL-based customer and transaction analysis.
- **Interactive Dashboard:** Five-page Streamlit application.

## Model Performance

The final selected model is a Logistic Regression pipeline evaluated on a temporally held-out test dataset.

| Metric | Test Result |
|---|---:|
| Accuracy | 53.31% |
| Precision | 27.61% |
| Recall | 87.33% |
| F1-score | 41.95% |
| ROC-AUC | 0.6942 |
| PR-AUC | 0.2861 |

The model achieves **87.33% recall**, indicating that it identifies a large proportion of actual churn cases.

However, precision is 27.61%, meaning many predicted churn cases are false positives. The model is therefore more suitable for prioritising customers for further investigation than making definitive churn decisions.

## Interactive Dashboard

The Streamlit dashboard includes five sections:

1. **Executive Overview** – Customer and transaction KPIs, churn distribution, and monthly customer trends.
2. **Customer Risk** – Customer-level churn risk exploration.
3. **Model Explainability** – Model performance and global SHAP feature importance.
4. **Risk Intelligence** – Risk-segment comparisons and transaction-value analysis.
5. **Transaction Analytics** – Transaction trends, transaction types, and customer-level activity.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Data Analysis | Pandas, NumPy |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Machine Learning | Scikit-learn |
| Explainability | SHAP |
| Database | PostgreSQL |
| Dashboard | Streamlit |
| Database Connectivity | SQLAlchemy, psycopg2 |

## Project Structure

```text
customer-churn-revenue-risk-intelligence/
│
├── app.py
├── config.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── models/
│   ├── logistic_regression_pipeline.pkl
│   └── model_metadata.json
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_model_training.ipynb
│   ├── 05_model_evaluation.ipynb
│   ├── 06_explainability.ipynb
│   └── 07_risk_intelligence.ipynb
│
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_Customer_Risk.py
│   ├── 3_Model_Explainability.py
│   ├── 4_Risk_Intelligence.py
│   └── 5_Transaction_Analytics.py
│
├── reports/
│   ├── risk_intelligence_summary.csv
│   └── shap_feature_importance.csv
│
├── SQL/
│   └── business queries.sql
│
└── utils/
    ├── __init__.py
    ├── database.py
    ├── model_utils.py
    └── styling.py
```

The raw and processed datasets and local Streamlit configuration are intentionally excluded from the repository.

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/aaryanbhatia50-cyber/customer-churn-revenue-risk-intelligence.git
cd customer-churn-revenue-risk-intelligence
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the local data

The raw and processed datasets are not included in this repository. Place the required datasets in their corresponding local `data/raw/` and `data/processed/` directories.

The application also uses the model, metadata, and aggregate report files included in the repository.

### 5. Configure PostgreSQL

Create and configure the PostgreSQL database and the tables and view required by the application.

Create a local `.streamlit/secrets.toml` file with your own database credentials:

```toml
[postgres]
user = "YOUR_USERNAME"
password = "YOUR_PASSWORD"
host = "YOUR_HOST"
port = 5432
database = "YOUR_DATABASE"
```

This file is local configuration and must never be committed to GitHub.

### 6. Run the dashboard

```bash
streamlit run app.py
```

## Important Notes

- Raw and processed datasets are excluded from the public repository.
- Database credentials and local Streamlit secrets must be configured separately.
- The model uses a classification threshold of 0.50.
- Model scores are not calibrated probabilities.
- Risk categories represent relative customer risk segments.
- Historical transaction value represents recorded transaction amounts and should not automatically be interpreted as company revenue or profit.
- Model predictions support risk identification and prioritisation, not guaranteed churn outcomes.

## Future Improvements

- Improve churn prediction precision while maintaining strong recall.
- Explore additional model optimisation and probability calibration.
- Extend customer-level risk monitoring and retention analysis.
- Develop additional business-focused insights and dashboard capabilities.

## Author

A data science project exploring machine learning, customer analytics, model explainability, and business intelligence.