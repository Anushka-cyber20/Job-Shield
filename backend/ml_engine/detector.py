"""
Unified Hybrid Detection Engine for JobShield.
Combines NLP Machine Learning, Domain Security Heuristics, and Explainable AI.
"""

import os
import joblib
from pathlib import Path
from typing import Dict, Any, Optional

from backend.ml_engine.heuristics import HeuristicsEngine
from backend.ml_engine.explainability import ExplainabilityEngine

class JobFraudDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.heuristics = HeuristicsEngine()
        self.explainability = ExplainabilityEngine()
        
        if model_path is None:
            model_path = Path("backend/data/job_detector_model.joblib")
        
        self.model_path = Path(model_path)
        self.model = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                print(f"[JobShield Detector] Loaded trained model from {self.model_path}")
            except Exception as e:
                print(f"[JobShield Detector] Failed to load model ({e}), retraining...")
                self._train_fresh()
        else:
            print("[JobShield Detector] Model not found on disk, training fresh model...")
            self._train_fresh()

    def _train_fresh(self):
        from backend.ml_engine.trainer import train_and_evaluate
        self.model, _ = train_and_evaluate()

    def analyze(self, title: str = "", company: str = "", description: str = "",
                salary: str = "", contact_email: str = "", portal_url: str = "") -> Dict[str, Any]:
        """
        Execute full comprehensive fraud assessment on a job or internship listing.
        """
        # Composite text for NLP vectorizer
        composite_text = f"{title} {company} {description} {salary} {contact_email} {portal_url}".strip()
        if not composite_text:
            composite_text = "No content provided."

        # 1. Machine Learning Inference
        ml_prob = 0.5
        if self.model is not None:
            try:
                probs = self.model.predict_proba([composite_text])[0]
                ml_prob = float(probs[1]) # probability of class 1 (fraud)
            except Exception as e:
                print(f"[Detector Error] ML inference failed: {e}")
                ml_prob = 0.5
        
        ml_score = int(round(ml_prob * 100))

        # 2. Rule-Based Heuristic Evaluation
        heur_results = self.heuristics.evaluate(
            title=title,
            company=company,
            description=description,
            salary=salary,
            contact_email=contact_email,
            portal_url=portal_url
        )
        heur_score = heur_results["composite_score"]
        flags = heur_results["flags"]

        # 3. Hybrid Fusion Logic
        # If critical flags exist (e.g. security deposit, impersonation), heuristic takes strong precedence
        has_critical = any(f["severity"] == "CRITICAL" for f in flags)
        has_high = any(f["severity"] == "HIGH" for f in flags)

        if has_critical:
            final_score = max(85, int(0.3 * ml_score + 0.7 * heur_score))
        elif has_high:
            final_score = max(65, int(0.4 * ml_score + 0.6 * heur_score))
        else:
            # Balanced ensemble
            final_score = int(0.55 * ml_score + 0.45 * heur_score)
        
        final_score = max(2, min(99, final_score))

        # 4. Threat Categorization & Verdict
        if final_score < 25:
            verdict = "Legitimate"
            threat_level = "LOW RISK"
            status_color = "emerald"
            summary = "This listing matches standard corporate recruitment patterns with verified professional attributes."
        elif final_score < 50:
            verdict = "Low-to-Moderate Concern"
            threat_level = "CAUTION ADVISED"
            status_color = "amber"
            summary = "Minor inconsistencies detected. Verify recruiter credentials through official company channels before proceeding."
        elif final_score < 75:
            verdict = "Suspicious Listing"
            threat_level = "HIGH RISK"
            status_color = "orange"
            summary = "Multiple high-risk fraud indicators detected (e.g., payment requirements or off-platform channels). Strong likelihood of a deceptive offer."
        else:
            verdict = "Confirmed / Highly Probable Scam"
            threat_level = "CRITICAL DANGER"
            status_color = "rose"
            summary = "Severe employment scam characteristics detected. Demands fees, impersonates an organization, or uses prohibited advance-pay patterns. DO NOT PAY OR SHARE DOCUMENTS."

        # 5. Explainable AI Highlights
        explanation = self.explainability.explain_text(description or composite_text)

        # 6. Actionable Safety Recommendations
        recommendations = self._generate_recommendations(flags, final_score)

        return {
            "overall_fraud_score": final_score,
            "verdict": verdict,
            "threat_level": threat_level,
            "status_color": status_color,
            "summary": summary,
            "component_scores": {
                "ml_model_score": ml_score,
                "heuristic_score": heur_score,
                "financial_risk": heur_results["financial_risk"],
                "contact_risk": heur_results["contact_risk"],
                "linguistic_risk": heur_results["linguistic_risk"],
                "company_risk": heur_results["company_risk"],
                "salary_risk": heur_results["salary_risk"]
            },
            "red_flags": flags,
            "flag_count": len(flags),
            "annotated_text_html": explanation["annotated_html"],
            "explainable_spans": explanation["spans"],
            "safety_recommendations": recommendations,
            "metadata": {
                "model_algorithm": "TF-IDF + Calibrated Classifier",
                "analyzed_length": len(composite_text)
            }
        }

    def _generate_recommendations(self, flags: list, score: int) -> list:
        recs = [
            "Never pay money, security deposits, or purchase equipment kits for an internship or job offer. Legitimate companies never charge candidates.",
            "Verify the recruiter's official identity on LinkedIn and compare the email domain with the company's authentic website."
        ]
        
        has_telegram = any("Telegram" in f.get("rule", "") for f in flags)
        has_whatsapp = any("WhatsApp" in f.get("rule", "") for f in flags)
        has_impersonation = any("Impersonation" in f.get("rule", "") for f in flags)
        has_check = any("Cheque" in f.get("rule", "") for f in flags)

        if has_telegram or has_whatsapp:
            recs.append("Decline requests to move communications exclusively to Telegram or WhatsApp. Insist on corporate email correspondence and video interviews via official Google Meet/Teams/Zoom.")
        
        if has_impersonation:
            recs.append("Check the organization's official careers page (e.g. careers.google.com, tcs.com/careers). If this job ID or role is not listed there, it is an impersonation scam.")
        
        if has_check:
            recs.append("Beware of counterfeit cheque scams. If an employer asks you to deposit a cheque and wire back funds to an equipment vendor, immediately notify your bank's fraud department.")

        if score >= 50:
            recs.append("Do not submit scans of your National ID (Aadhaar/SSN), passport, or bank statements without verified corporate authentication.")
            recs.append("Report this listing to your College Placement Cell (TPO) and national cybercrime reporting portal (cybercrime.gov.in / IC3).")

        return recs
