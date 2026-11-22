"""
JobShield Platform Launcher.
Starts the FastAPI application and opens the web portal.
"""

import sys
import webbrowser
import threading
import time
import uvicorn
from pathlib import Path

def open_browser():
    time.sleep(1.5)
    print("\n[JobShield] Launching browser interface at http://127.0.0.1:8000 ...")
    webbrowser.open("http://127.0.0.1:8000")

def main():
    print("=" * 65)
    print("  JobShield: Fake Internship & Job Listing Detection Platform")
    print("  AI/ML Academic Capstone Project | Version 2.0")
    print("=" * 65)
    
    # Verify model artifact exists or generate it
    model_path = Path("backend/data/job_detector_model.joblib")
    if not model_path.exists():
        print("[JobShield] Model artifact not found. Initializing training...")
        from backend.ml_engine.trainer import train_and_evaluate
        train_and_evaluate()

    # Start browser opener in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    print("[JobShield] Starting FastAPI server on http://127.0.0.1:8000")
    print("[JobShield] Interactive API Docs available at http://127.0.0.1:8000/docs")
    print("[JobShield] Press Ctrl+C to terminate.")
    print("=" * 65)
    
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")

if __name__ == "__main__":
    main()
