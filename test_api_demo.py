#!/usr/bin/env python3
"""
Script de verificación pre-demo para FraudIA API
Testea todos los endpoints antes de la presentación
"""

import requests
import json
import sys
from datetime import datetime

API_BASE = "https://gilled-founder-plot.ngrok-free.dev"
HEADERS = {"ngrok-skip-browser-warning": "true"}

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def test_endpoint(method, endpoint, data=None, name=""):
    """Testea un endpoint individual"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=HEADERS, timeout=10)
        else:
            resp = requests.post(url, json=data, headers=HEADERS, timeout=10)

        if resp.status_code in [200, 201]:
            print(f"{GREEN}PASS{RESET} {name}")
            return True, resp
        else:
            print(f"{RED}FAIL{RESET} {name} - Status {resp.status_code}")
            return False, resp
    except Exception as e:
        print(f"{RED}ERROR{RESET} {name} - {str(e)}")
        return False, None

def run_tests():
    """Ejecuta todos los tests"""
    print(f"\n{'='*60}")
    print(f"VERIFICACION PRE-DEMO FRAUDIA API")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    results = {}

    # Test 1: Root
    print("1. CONECTIVIDAD BASICA")
    success, resp = test_endpoint("GET", "/", name="GET /")
    results["root"] = success
    if success:
        data = resp.json()
        print(f"   Versión: {data.get('version')}, Estado: {data.get('estado')}\n")

    # Test 2: Métricas
    print("2. METRICAS GLOBALES")
    success, resp = test_endpoint("GET", "/resumen", name="GET /resumen")
    results["resumen"] = success
    if success:
        data = resp.json()
        print(f"   Total: {data.get('total_siniestros')}")
        print(f"   Rojos: {data.get('rojos')} | Amarillos: {data.get('amarillos')} | Verdes: {data.get('verdes')}")
        print(f"   Score promedio: {data.get('score_promedio')}\n")

    # Test 3: Casos
    print("3. LISTADO DE CASOS")
    success, resp = test_endpoint("GET", "/casos?limit=100", name="GET /casos")
    results["casos"] = success
    if success:
        data = resp.json()
        print(f"   Total de casos devueltos: {len(data)}")
        if len(data) > 0:
            print(f"   Primer caso: {data[0].get('id_siniestro')} (Nivel: {data[0].get('nivel')})\n")

    # Test 4: Caso individual
    print("4. DETALLE DE CASO")
    if results["casos"] and len(data) > 0:
        first_id = data[0].get('id_siniestro')
        success, resp = test_endpoint("GET", f"/caso/{first_id}", name=f"GET /caso/{first_id}")
        results["caso_detail"] = success
        if success:
            print(f"   Explicación generada: SI\n")
    else:
        print(f"{YELLOW}SKIP{RESET} Caso detail - no hay casos\n")
        results["caso_detail"] = None

    # Test 5: Proveedores
    print("5. RANKING DE PROVEEDORES")
    success, resp = test_endpoint("GET", "/proveedores", name="GET /proveedores")
    results["proveedores"] = success
    if success:
        data = resp.json()
        print(f"   Total de proveedores: {len(data)}")
        if len(data) > 0:
            print(f"   Top 1: {data[0].get('nombre')} ({data[0].get('alertas')} alertas)\n")

    # Test 6: Chat IA
    print("6. AGENTE IA - CHAT")
    success, resp = test_endpoint("POST", "/chat",
                                 data={"pregunta": "¿Cuántos casos ROJOS hay?"},
                                 name="POST /chat")
    results["chat"] = success
    if success:
        data = resp.json()
        respuesta = data.get('respuesta', '')[:80]
        print(f"   Respuesta (primeros 80 caracteres): {respuesta}...\n")

    # Test 7: Reporte
    print("7. REPORTE EJECUTIVO")
    success, resp = test_endpoint("GET", "/reporte", name="GET /reporte")
    results["reporte"] = success
    if success:
        print(f"   Reporte generado: SI\n")

    # Test 8: Descargas
    print("8. DESCARGAS")
    success, resp = test_endpoint("GET", "/descargar/casos", name="GET /descargar/casos")
    results["descargar_casos"] = success
    if success:
        print(f"   CSV descargable: SI\n")

    # Test 9: Análisis Dataset
    print("9. PANEL ANALIZAR DATASET")
    # Crear un CSV test simple
    csv_content = """id_siniestro,monto_reclamado,dias_desde_inicio_poliza,dias_entre_ocurrencia_reporte,historial_siniestros_asegurado,documentos_completos,id_proveedor,suma_asegurada,cobertura
SIN-001,50000,15,5,2,TRUE,P001,100000,Choque
SIN-002,75000,8,3,1,FALSE,P002,100000,Robo
SIN-003,30000,45,2,0,TRUE,P001,100000,Choque"""

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_csv = f.name

    try:
        with open(temp_csv, 'rb') as f:
            files = {'file': f}
            try:
                resp = requests.post(f"{API_BASE}/analizar-dataset",
                                    files=files,
                                    headers=HEADERS,
                                    timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('status') == 'success':
                        print(f"{GREEN}PASS{RESET} POST /analizar-dataset")
                        print(f"   Casos analizados: {data['resumen'].get('total_casos')}")
                        results["analizar_dataset"] = True
                    else:
                        print(f"{RED}FAIL{RESET} POST /analizar-dataset - {data.get('error')}")
                        results["analizar_dataset"] = False
                else:
                    print(f"{RED}FAIL{RESET} POST /analizar-dataset - Status {resp.status_code}")
                    results["analizar_dataset"] = False
            except Exception as e:
                print(f"{RED}ERROR{RESET} POST /analizar-dataset - {str(e)}")
                results["analizar_dataset"] = False
    finally:
        import os
        try:
            os.remove(temp_csv)
        except:
            pass

    # Resumen
    print(f"\n{'='*60}")
    print("RESUMEN DE VERIFICACION")
    print(f"{'='*60}")

    passed = sum(1 for v in results.values() if v is True)
    total = len(results)

    for endpoint, status in results.items():
        icon = GREEN + "OK" + RESET if status else (YELLOW + "SKIP" + RESET if status is None else RED + "FAIL" + RESET)
        print(f"  {icon} - {endpoint}")

    print(f"\nResultado: {GREEN}{passed}/{total}{RESET} endpoints operativos")

    if passed == total:
        print(f"\n{GREEN}API LISTA PARA DEMO{RESET}\n")
        return 0
    elif passed >= total * 0.8:
        print(f"\n{YELLOW}API CON ALGUNOS PROBLEMAS - REVISAR{RESET}\n")
        return 1
    else:
        print(f"\n{RED}API INESTABLE - NO DEMOSTRAR{RESET}\n")
        return 2

if __name__ == "__main__":
    sys.exit(run_tests())
