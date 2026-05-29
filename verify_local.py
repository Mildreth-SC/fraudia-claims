#!/usr/bin/env python3
"""
Script de verificación LOCAL completa - FraudIA
Verifica que TODO funcione antes de demostrar
"""

import subprocess
import sys
import time
import json
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_section(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{RESET}")

def check_pass(item):
    print(f"{GREEN}[PASS]{RESET} {item}")

def check_fail(item):
    print(f"{RED}[FAIL]{RESET} {item}")

def check_warn(item):
    print(f"{YELLOW}[WARN]{RESET} {item}")

def run_command(cmd):
    """Ejecuta comando y devuelve output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def main():
    print(f"\n{BLUE}VERIFICACION LOCAL COMPLETA - FRAUDIA{RESET}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "python": False,
        "venv": False,
        "requirements": False,
        "r": False,
        "supabase_url": False,
        "supabase_key": False,
        "groq_key": False,
        "node": False,
        "npm": False,
        "env_file": False
    }

    # ========== PYTHON ==========
    print_section("1. PYTHON ENVIRONMENT")

    success, stdout, _ = run_command("python --version")
    if success:
        check_pass(f"Python {stdout.strip()}")
        results["python"] = True
    else:
        check_fail("Python no encontrado. Instala Python 3.12+")
        return 1

    # ========== VENV ==========
    success, _, _ = run_command("python -m venv --help")
    if success:
        check_pass("Virtual environment disponible")
        results["venv"] = True
    else:
        check_fail("Virtual environment no disponible")

    # ========== REQUIREMENTS ==========
    print_section("2. DEPENDENCIAS PYTHON")

    req_path = Path("requirements.txt")
    if req_path.exists():
        check_pass("requirements.txt existe")

        # Verificar si FastAPI está instalado
        success, _, _ = run_command("python -c \"import fastapi; print(fastapi.__version__)\"")
        if success:
            check_pass("FastAPI instalado")
            results["requirements"] = True
        else:
            check_warn("FastAPI no está instalado. Ejecuta: pip install -r requirements.txt")
    else:
        check_fail("requirements.txt no encontrado")

    # ========== R ==========
    print_section("3. R ENVIRONMENT")

    success, stdout, _ = run_command("R --version")
    if success:
        version_line = stdout.split('\n')[0]
        check_pass(f"R {version_line}")
        results["r"] = True
    else:
        check_warn("R no encontrado. El panel de análisis no funcionará sin R")

    # ========== ENV VARIABLES ==========
    print_section("4. VARIABLES DE AMBIENTE (.env)")

    env_path = Path(".env")
    if env_path.exists():
        check_pass(".env encontrado")
        results["env_file"] = True

        with open(env_path) as f:
            env_content = f.read()

            if "SUPABASE_URL" in env_content:
                check_pass("SUPABASE_URL configurada")
                results["supabase_url"] = True
            else:
                check_fail("SUPABASE_URL no configurada")

            if "SUPABASE_KEY" in env_content:
                check_pass("SUPABASE_KEY configurada")
                results["supabase_key"] = True
            else:
                check_fail("SUPABASE_KEY no configurada")

            if "GROQ_API_KEY" in env_content:
                check_pass("GROQ_API_KEY configurada")
                results["groq_key"] = True
            else:
                check_fail("GROQ_API_KEY no configurada")
    else:
        check_fail(".env no encontrado. Copia .env.example a .env")

    # ========== NODE.JS ==========
    print_section("5. NODEJS ENVIRONMENT")

    success, stdout, _ = run_command("node --version")
    if success:
        check_pass(f"Node.js {stdout.strip()}")
        results["node"] = True
    else:
        check_warn("Node.js no encontrado. El frontend no funcionará")

    success, stdout, _ = run_command("npm --version")
    if success:
        check_pass(f"npm {stdout.strip()}")
        results["npm"] = True
    else:
        check_warn("npm no encontrado")

    # ========== ARCHIVOS CRITICOS ==========
    print_section("6. ARCHIVOS CRITICOS")

    critical_files = [
        "src/app/main.py",
        "src/rules/fraud_rules.py",
        "src/models/fraud_model.py",
        "src/analysis/data_cleaner.R",
        "frontend/package.json",
        "frontend/src/routes/index.tsx",
        "data/",
    ]

    for file in critical_files:
        if Path(file).exists():
            check_pass(f"{file}")
        else:
            check_fail(f"{file} no encontrado")

    # ========== RESUMEN ==========
    print_section("RESUMEN DE VERIFICACION")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nEstado de dependencias: {passed}/{total}")

    if results["python"] and results["requirements"]:
        print(f"{GREEN}Backend: LISTO{RESET}")
    else:
        print(f"{RED}Backend: PROBLEMAS{RESET}")

    if results["node"] and results["npm"]:
        print(f"{GREEN}Frontend: LISTO{RESET}")
    else:
        print(f"{RED}Frontend: PROBLEMAS{RESET}")

    if results["supabase_url"] and results["supabase_key"] and results["groq_key"]:
        print(f"{GREEN}APIs: CONFIGURADAS{RESET}")
    else:
        print(f"{RED}APIs: FALTAN CONFIGURAR{RESET}")

    # ========== INSTRUCCIONES SIGUIENTES ==========
    print_section("PROXIMOS PASOS")

    if passed == total:
        print(f"{GREEN}TODO LISTO PARA INICIAR DESARROLLO LOCAL{RESET}\n")
        print("Ejecuta en 3 terminales diferentes:")
        print("  Terminal 1: python src/app/main.py")
        print("  Terminal 2: cd frontend && npm run dev")
        print("  Terminal 3: ngrok http 8000")
        print("\nLuego abre: http://localhost:5173")
        return 0
    else:
        print(f"{YELLOW}FALTAN ALGUNOS PASOS:{RESET}\n")
        if not results["python"]:
            print("  - Instala Python 3.12+")
        if not results["requirements"]:
            print("  - Ejecuta: pip install -r requirements.txt")
        if not results["node"]:
            print("  - Instala Node.js 18+")
        if not results["npm"]:
            print("  - npm debería venir con Node.js")
        if not results["supabase_url"]:
            print("  - Configura SUPABASE_URL en .env")
        if not results["supabase_key"]:
            print("  - Configura SUPABASE_KEY en .env")
        if not results["groq_key"]:
            print("  - Configura GROQ_API_KEY en .env")

        return 1

if __name__ == "__main__":
    sys.exit(main())
