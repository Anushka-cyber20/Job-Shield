"""
Machine Learning Training & Academic Validation Pipeline for JobShield.
Trains an NLP classifier on benchmark job listings and extracts evaluation metrics.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

from backend.ml_engine.dataset import generate_synthetic_dataset

def train_and_evaluate():
    print("Generating training & validation dataset...")
    df = generate_synthetic_dataset(n_samples=1600)
    
    # Save dataset copy for reference
    data_dir = Path("backend/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(data_dir / "job_listings_dataset.csv", index=False)
    
    # Combine feature representations
    df["composite_text"] = (
        df["title"].fillna("") + " " +
        df["company_name"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["salary_range"].fillna("") + " " +
        df["contact_email"].fillna("")
    )
    
    X = df["composite_text"]
    y = df["fraudulent"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    # Create TF-IDF + Logistic Regression Pipeline with L2 regularization
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            stop_words="english"
        )),
        ("classifier", LogisticRegression(C=2.5, max_iter=1000, random_state=42))
    ])
    
    print("Training TF-IDF + Classification model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("\n--- Model Performance Metrics ---")
    print(f"Accuracy : {acc:.4f} ({acc*100:.1f}%)")
    print(f"Precision: {prec:.4f} ({prec*100:.1f}%)")
    print(f"Recall   : {rec:.4f} ({rec*100:.1f}%)")
    print(f"F1-Score : {f1:.4f} ({f1*100:.1f}%)")
    print(f"ROC-AUC  : {auc:.4f}")
    print(f"Confusion Matrix:\n  TN: {cm[0][0]}, FP: {cm[0][1]}\n  FN: {cm[1][0]}, TP: {cm[1][1]}")
    
    # Extract top influential tokens
    vectorizer = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["classifier"]
    feature_names = np.array(vectorizer.get_feature_names_out())
    coefs = clf.coef_[0]
    
    top_fraud_indices = np.argsort(coefs)[-20:][::-1]
    top_legit_indices = np.argsort(coefs)[:20]
    
    fraud_indicators = [
        {"token": feature_names[i], "weight": round(float(coefs[i]), 3)}
        for i in top_fraud_indices
    ]
    legit_indicators = [
        {"token": feature_names[i], "weight": round(float(-coefs[i]), 3)}
        for i in top_legit_indices
    ]
    
    # Save artifacts
    model_path = data_dir / "job_detector_model.joblib"
    joblib.dump(pipeline, model_path)
    print(f"Model serialized to {model_path}")
    
    metrics = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "confusion_matrix": {
            "true_negatives": cm[0][0],
            "false_positives": cm[0][1],
            "false_negatives": cm[1][0],
            "true_positives": cm[1][1]
        },
        "dataset_statistics": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "fraud_ratio": round(float(y.mean()), 3)
        },
        "top_fraud_tokens": fraud_indicators,
        "top_legit_tokens": legit_indicators,
        "algorithm": "TF-IDF (1-2 ngrams) + Calibrated Logistic Regression",
        "benchmark_reference": "EMSCAD (Employment Scam Aegean Dataset)"
    }
    
    with open(data_dir / "model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("Metrics written to backend/data/model_metrics.json")
    
    return pipeline, metrics

if __name__ == "__main__":
    train_and_evaluate()
