#!/usr/bin/env python3
"""
Test script for complete dataset analysis pipeline
Tests: Upload → Process → Store in Global State → Query → Results
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Configuration
API_BASE = "http://127.0.0.1:8000"
TEST_CSV = "test_dataset.csv"

def test_health_check():
    """Verify API is running"""
    print("\n[1] Health Check...")
    try:
        resp = requests.get(f"{API_BASE}/", timeout=5)
        if resp.status_code == 200:
            print(f"[OK] API is running: {resp.json()}")
            return True
        else:
            print(f"[FAIL] API returned {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Cannot connect to API: {e}")
        return False

def test_dataset_info_empty():
    """Check /dataset/info when no dataset loaded"""
    print("\n[2] Check Dataset Info (should be empty)...")
    try:
        resp = requests.get(f"{API_BASE}/dataset/info", timeout=10)
        data = resp.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        if "error" in data:
            print(f"[OK] Correctly reports no dataset loaded")
            return True
        else:
            print(f"[FAIL] Unexpected response format")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_upload_dataset():
    """Upload test CSV and verify analysis"""
    print(f"\n[3] Upload Test Dataset ({TEST_CSV})...")
    try:
        with open(TEST_CSV, "rb") as f:
            files = {"file": (TEST_CSV, f, "text/csv")}
            resp = requests.post(f"{API_BASE}/analizar-dataset", files=files, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            print(f"Status: {data.get('status')}")
            print(f"Total Cases: {data.get('resumen', {}).get('total_casos')}")
            print(f"Risk Levels - ROJO: {data.get('resumen', {}).get('rojos')}, "
                  f"AMARILLO: {data.get('resumen', {}).get('amarillos')}, "
                  f"VERDE: {data.get('resumen', {}).get('verdes')}")
            print(f"Available Columns: {data.get('columnas_disponibles', [])[:5]}...")

            if data.get("status") == "success" and data.get("resumen", {}).get("total_casos", 0) > 0:
                print("[OK] Dataset uploaded and analyzed successfully")
                return True, data
            else:
                print("[FAIL] Analysis failed")
                return False, data
        else:
            print(f"[FAIL] Upload failed with status {resp.status_code}: {resp.text}")
            return False, None
    except Exception as e:
        print(f"[FAIL] Error during upload: {e}")
        return False, None

def test_dataset_info_after_upload():
    """Check /dataset/info after upload"""
    print("\n[4] Check Dataset Info (after upload)...")
    try:
        resp = requests.get(f"{API_BASE}/dataset/info", timeout=10)
        data = resp.json()
        print(f"Rows: {data.get('filas')}")
        print(f"Total Columns: {data.get('total_columnas')}")
        print(f"Columns: {data.get('columnas', [])[:5]}...")

        if data.get("filas", 0) > 0:
            print("[OK] Global dataset state populated correctly")
            return True, data
        else:
            print("[FAIL] Dataset not in global state")
            return False, data
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False, None

def test_query_dataset():
    """Test /dataset/consulta endpoint"""
    print("\n[5] Execute Dataset Query...")
    try:
        payload = {"sql": "SELECT * FROM dataset", "limit": 5}
        resp = requests.post(f"{API_BASE}/dataset/consulta", json=payload, timeout=10)
        data = resp.json()

        print(f"Columns returned: {len(data.get('columnas', []))}")
        print(f"Rows returned: {data.get('total_filas')}")
        print(f"Total dataset size: {data.get('total_dataset')}")

        if data.get("total_filas", 0) > 0:
            print(f"Sample row: {json.dumps(data['filas'][0], indent=2)}")
            print("[OK] Query executed successfully")
            return True
        else:
            print("[FAIL] No rows returned")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_columns_detection():
    """Verify all columns were detected"""
    print("\n[6] Column Detection Test...")
    try:
        resp = requests.get(f"{API_BASE}/dataset/info", timeout=10)
        info = resp.json()

        expected_cols = ["id", "amount", "days_from_policy", "days_to_report",
                        "history", "documents_complete", "provider", "sum_insured",
                        "coverage", "city"]

        actual_cols = info.get("columnas", [])
        detected = sum(1 for col in expected_cols if col in actual_cols)

        print(f"Expected: {len(expected_cols)} columns")
        print(f"Detected: {detected} columns")
        print(f"Columns: {actual_cols}")

        if detected >= len(expected_cols):
            print("[OK] All columns detected correctly")
            return True
        else:
            print(f"[FAIL] Only {detected}/{len(expected_cols)} columns detected")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def run_all_tests():
    """Execute all tests in sequence"""
    print("=" * 70)
    print("DATASET ANALYSIS PIPELINE TEST SUITE")
    print("=" * 70)

    results = {}

    if not test_health_check():
        print("\n[FAIL] API is not running. Start it with: python src/app/main.py")
        return False

    results["info_empty"] = test_dataset_info_empty()
    results["upload"] = test_upload_dataset()
    results["info_after"] = test_dataset_info_after_upload()
    results["query"] = test_query_dataset()
    results["columns"] = test_columns_detection()

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if isinstance(v, tuple) and v[0])
    total = len([v for v in results.values() if isinstance(v, tuple)])

    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n[OK] ALL TESTS PASSED - Dataset pipeline is fully functional!")
        return True
    else:
        print("\n[FAIL] Some tests failed - check output above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
