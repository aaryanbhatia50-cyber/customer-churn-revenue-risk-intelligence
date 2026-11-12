
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "logistic_regression_pipeline.pkl"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

CUSTOMER_DATA_PATH = (
    BASE_DIR / "data" / "processed" / "churn_selected_features.csv"
)

SHAP_REPORT_PATH = (
    BASE_DIR / "reports" / "shap_feature_importance.csv"
)

RISK_REPORT_PATH = (
    BASE_DIR / "reports" / "risk_intelligence_summary.csv"
)

MODEL_THRESHOLD = 0.50
