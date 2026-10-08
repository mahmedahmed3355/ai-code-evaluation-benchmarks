from pathlib import Path
s=Path("/app/ml_eval/pipeline.py").read_text()
for x in ["train_end","validation_end","future_rows_ignored","duplicated","prepare_features","predict_proba"]: assert x in s
assert "events.csv" not in s and "pd.read_csv" not in s
print("PASS independent static verifier")
